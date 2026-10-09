import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validateCatalog, decodeCatalog } from '../assets/catalog-data.js';
const original=JSON.parse(readFileSync('catalog/library-catalog.json','utf8'));
test('original export and Firestore representation both validate',async()=>{
  assert.deepEqual(await validateCatalog(original),original.data);
  assert.deepEqual(await decodeCatalog({...original,dataJson:JSON.stringify(original.data)}),original.data);
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
