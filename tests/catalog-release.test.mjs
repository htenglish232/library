import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {addReleaseLessons, RELEASE_ADDITIONS, RELEASE_ID, releaseCatalogView} from '../assets/catalog-release.js';
import {decodeCatalog, managedPayload, encodeCatalogData} from '../assets/catalog-data.js';
const legacy=JSON.parse(readFileSync('catalog/library-catalog.json','utf8')).data;
const current=JSON.parse(readFileSync('catalog/current-library-catalog.json','utf8')).data;
test('legacy catalog gains exactly the main release additions without mutation',()=>{
 const original=structuredClone(legacy),result=addReleaseLessons(legacy);
 assert.deepEqual(result.data,current);assert.deepEqual(legacy,original);
 assert.equal(result.added,RELEASE_ADDITIONS.length);
 assert.deepEqual(addReleaseLessons(result.data),{data:current,added:0});
});
test('server edits, hidden grades/folders/lessons and renamed folders remain intact',()=>{
 const data=structuredClone(legacy),grade=data.find(g=>g.grade==='Grade 5');
 grade.grade='Khối 5';grade.hidden=true;grade.units[0].name='Ngữ pháp lớp 5';grade.units[0].hidden=true;
 const patch=RELEASE_ADDITIONS[0];grade.units[0].lessons.push({...patch.lesson,title:'Tên Admin đã sửa',hidden:true});
 data.push({grade:'Grade 9',units:[{name:'Thư mục Admin',lessons:[{title:'Bài riêng',href:'grade-9/new.html'}]}]});
 const result=addReleaseLessons(data);
 const preserved=result.data.find(g=>g.grade==='Khối 5');
 assert.equal(preserved.hidden,true);assert.equal(preserved.units[0].hidden,true);
 assert.deepEqual(preserved.units[0].lessons.find(l=>l.href===patch.lesson.href),grade.units[0].lessons.at(-1));
 assert.deepEqual(result.data.at(-1),data.at(-1));
 assert.equal(result.added,RELEASE_ADDITIONS.length-1);
});
test('adding new main links does not resurrect deleted legacy links',()=>{
 const data=structuredClone(legacy),grade=data.find(g=>g.grade==='Grade 5');
 const deleted=grade.units[0].lessons.shift().href;
 const result=addReleaseLessons(data);
 assert.ok(!result.data.some(g=>g.units.some(u=>u.lessons.some(l=>l.href===deleted))));
 assert.equal(result.added,RELEASE_ADDITIONS.length);
});

test('explicit release adoption round-trips and respects later Admin deletions',async()=>{
 const data=structuredClone(current);const group=data.find(g=>g.grade==='Grade 5');
 group.units[0].lessons=group.units[0].lessons.filter(l=>l.href!==RELEASE_ADDITIONS[0].lesson.href);
 const payload=await managedPayload(data);
 const fields={...payload,dataJson:encodeCatalogData(data,[RELEASE_ID])};
 assert.deepEqual(await decodeCatalog(fields),data);
 assert.deepEqual(releaseCatalogView(fields,data),data);
 const oldFields={...payload,dataJson:JSON.stringify(data)};
 assert.equal(releaseCatalogView(oldFields,data).find(g=>g.grade==='Grade 5').units[0].lessons.length,group.units[0].lessons.length+1);
});
test('malformed release metadata is rejected without weakening legacy hashes',async()=>{
 const payload=await managedPayload(current);
 await assert.rejects(decodeCatalog({...payload,dataJson:JSON.stringify({data:current,releaseApplied:['invalid']})}));
 await assert.rejects(decodeCatalog({...payload,dataJson:JSON.stringify({data:current,releaseApplied:[],extra:true})}));
});
