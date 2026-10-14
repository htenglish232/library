import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validateCatalog, decodeCatalog, managedPayload, validateManagedCatalog, validateBackup, inspectCatalog, visibleCatalog, validateHtmlLink, MAX_CATALOG_BYTES } from '../assets/catalog-data.js';
const original=JSON.parse(readFileSync('catalog/library-catalog.json','utf8'));
test('original export and Firestore representation both validate',async()=>{
  assert.deepEqual(await validateCatalog(original),original.data);
  assert.deepEqual(await decodeCatalog({...original,dataJson:JSON.stringify(original.data)}),original.data);
});
test('managed catalog is dynamic, preserves original content and validates backups',async()=>{
  const data=structuredClone(original.data);
  data.push({grade:'Grade 9',units:[{name:'New folder',lessons:[{title:'New lesson',href:'grade-9/new.html'}]}]});
  const payload=await managedPayload(data);
  assert.equal(payload.count,202);
  assert.deepEqual(await validateManagedCatalog(payload),data);
  assert.deepEqual(await validateBackup({...payload,sourceRevision:1}),data);
  assert.deepEqual(await decodeCatalog({...payload,dataJson:JSON.stringify(data)}),data);
  assert.equal((await managedPayload([])).count,0);
  await assert.rejects(validateManagedCatalog({...payload,count:201}));
  await assert.rejects(validateManagedCatalog({...payload,sha256:'f'.repeat(64)}));
  await assert.rejects(validateBackup({...payload,schemaVersion:3}));
});
test('hidden items and folders affect visible count without deleting stored paths',async()=>{
  const data=structuredClone(original.data);
  data[0].hidden=true; data[1].units[0].hidden=true; data[2].units[0].lessons[0].hidden=true;
  const summary=inspectCatalog(data);
  assert.equal(summary.count,201);
  assert.equal(summary.visible,201-24-12-1);
  const visible=visibleCatalog(data);
  assert.equal(visible.flatMap(g=>g.units.flatMap(u=>u.lessons)).length,summary.visible);
  assert.equal(data[0].units[0].lessons.length,24);
});
test('unsafe links, duplicate links, malformed structure and excess byte size are rejected',async()=>{
  for(const href of ['javascript:alert(1)','data:text/html,test','http://example.org/a.html','//example.org/a.html','/a.html','../a.html','grade-9/%2e%2e/a.html','grade-9/%5cfoo.html','grade-9/a.txt','grade-9/a.html?x=1','grade-9/a.html#x']) assert.throws(()=>validateHtmlLink(href),href);
  for(const href of ['grade-9/a.html','grade-9/My lesson.html','grade-9/B%C3%A0i.html','https://example.org/a.html?q=1']) assert.doesNotThrow(()=>validateHtmlLink(href));
  const data=structuredClone(original.data);
  data[0].units[0].lessons.push(data[0].units[0].lessons[0]); assert.throws(()=>inspectCatalog(data));
  for(const data of [[{grade:'Grade 9',units:[],role:'admin'}],[{grade:'Grade 9',units:[],hidden:'true'}],[{grade:'Grade 9',units:[{name:'x',type:'other',lessons:[]}]}]]) assert.throws(()=>inspectCatalog(data));
  const many=[{grade:'Grade 9',units:[{name:'x',lessons:Array.from({length:5000},(_,i)=>({title:'x'.repeat(200),href:`grade-9/${i}.html`}))}]}];
  assert(new TextEncoder().encode(JSON.stringify(many)).length>MAX_CATALOG_BYTES); assert.throws(()=>inspectCatalog(many));
});
test('changed path, title, lesson order, category order or grade order is rejected',async()=>{
  const mutate=[
    data=>{data[0].units[0].lessons[0].href='grade-4/elsewhere.html';},
    data=>{data[0].units[0].lessons[0].title='Changed';},
    data=>data[0].units[0].lessons.reverse(),
    data=>data[2].units.reverse(),
    data=>data.reverse()
  ];
  for(const change of mutate) {const payload=structuredClone(original);change(payload.data);await assert.rejects(validateCatalog(payload));}
});
test('wrong count, hash, schema, duplicate, omitted item and invalid JSON are rejected',async()=>{
  for(const fields of [{count:200},{sha256:'0'.repeat(64)},{schemaVersion:2},{data:null}]) await assert.rejects(validateCatalog({...original,...fields}));
  const duplicate=structuredClone(original); duplicate.data[0].units[0].lessons[1]=duplicate.data[0].units[0].lessons[0]; await assert.rejects(validateCatalog(duplicate));
  const omitted=structuredClone(original); omitted.data[0].units[0].lessons.pop(); await assert.rejects(validateCatalog(omitted));
  await assert.rejects(decodeCatalog({...original,dataJson:'not-json'}));
});
