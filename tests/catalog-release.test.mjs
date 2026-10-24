import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {addReleaseLessons, RELEASE_ADDITIONS, RELEASE_ID, RELEASE_IDS, IELTS_RELEASE_ID, GAME_RELEASE_ID, PILOT_GAME_RELEASE_ID, PILOT_GAME_ADDITIONS, DUAL_GAME_RELEASE_ID, DUAL_GAME_ADDITION, releaseCatalogView} from '../assets/catalog-release.js';
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
 assert.deepEqual(result.data.find(g=>g.grade==='Grade 9'),data.at(-1));
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

test('IELTS release preserves deletions from a previously adopted Grade 5 release',async()=>{
 const data=structuredClone(current);
 const lessons=data.find(g=>g.grade==='Grade 5').units[0].lessons;
 const removed=lessons.shift().href;
 lessons.splice(lessons.findIndex(l=>l.href===RELEASE_ADDITIONS[0].lesson.href),1);
 data.pop();
 const fields={...await managedPayload(data),dataJson:encodeCatalogData(data,[RELEASE_ID])};
 const result=releaseCatalogView(fields,data);
 assert.equal(result.at(-1).grade,'Apps for IELTS');
 assert.ok(!result.flatMap(g=>g.units.flatMap(u=>u.lessons)).some(l=>[removed,RELEASE_ADDITIONS[0].lesson.href].includes(l.href)));
 const adopted=result.filter(g=>g.grade!=='Apps for IELTS');
 assert.deepEqual(releaseCatalogView({...fields,dataJson:encodeCatalogData(adopted,RELEASE_IDS)},adopted),adopted);
 assert.ok(RELEASE_IDS.includes(IELTS_RELEASE_ID));
});

test('game link is inserted beside the original and respects prior release deletions',async()=>{
 const game=RELEASE_ADDITIONS.find(p=>p.lesson.href.endsWith('/truc-tuan-game-test.html')),data=structuredClone(current);
 const grade=data.find(g=>g.grade==='Grade 8');
 const folder=grade.units.find(u=>u.name==='Đề thi GHK1');
 const original=folder.lessons.findIndex(l=>l.title==='Đề 01 · THCS Trực Tuấn');
 assert.equal(folder.lessons[original+1].href,game.lesson.href);
 folder.hidden=true;
 folder.lessons=folder.lessons.filter(l=>l.href!==game.lesson.href);
 data.find(g=>g.grade==='Grade 5').units[0].lessons.shift();
 data.splice(data.findIndex(g=>g.grade==='Apps for IELTS'),1);
 const previous=structuredClone(data);
 const fields={...await managedPayload(data),dataJson:encodeCatalogData(data,[RELEASE_ID,IELTS_RELEASE_ID])};
 const view=releaseCatalogView(fields,data);
 assert.deepEqual(data,previous);
 assert.equal(view.find(g=>g.grade==='Grade 8').units.find(u=>u.name==='Đề thi GHK1').hidden,true);
 assert.ok(!view.some(g=>g.grade==='Apps for IELTS'));
 assert.equal(addReleaseLessons(data,[RELEASE_ID,IELTS_RELEASE_ID]).added,1);
 const adopted={...fields,dataJson:encodeCatalogData(data,[...RELEASE_IDS])};
 assert.deepEqual(releaseCatalogView(adopted,data),data);
 assert.ok(RELEASE_IDS.includes(GAME_RELEASE_ID));
});

test('all three pilot links upgrade the previous release once and preserve Admin visibility and deletions',async()=>{
 const previousIds=RELEASE_IDS.filter(id=>id!==PILOT_GAME_RELEASE_ID);
 const paths=new Set(PILOT_GAME_ADDITIONS.map(p=>p.lesson.href));
 const data=structuredClone(current),grade=data.find(g=>g.grade==='Grade 8');
 grade.grade='Khối 8';grade.hidden=true;
 const unit=grade.units.find(u=>u.name==='Đề thi GHK1');unit.name='Đề giữa kỳ';unit.hidden=true;
 unit.lessons=unit.lessons.filter(l=>!paths.has(l.href));
 const deleted=unit.lessons.shift().href;
 const original=structuredClone(data);
 const result=addReleaseLessons(data,previousIds);
 assert.equal(result.added,3);assert.deepEqual(data,original);
 const updated=result.data.find(g=>g.grade==='Khối 8');assert.equal(updated.hidden,true);
 const folder=updated.units.find(u=>u.name==='Đề giữa kỳ');assert.equal(folder.hidden,true);
 for(const patch of PILOT_GAME_ADDITIONS){
  const idx=folder.lessons.findIndex(l=>l.href===patch.lesson.href);
  assert.ok(idx>0);assert.equal(folder.lessons[idx-1].href.slice(0,folder.lessons[idx-1].href.lastIndexOf('/')),patch.lesson.href.slice(0,patch.lesson.href.lastIndexOf('/')));
 }
 assert.ok(!folder.lessons.some(l=>l.href===deleted));
 assert.equal(addReleaseLessons(result.data,previousIds).added,0);
 const hidden=folder.lessons.find(l=>paths.has(l.href));hidden.hidden=true;hidden.title='Tên game đã sửa';
 assert.deepEqual(addReleaseLessons(result.data,previousIds).data,result.data);
 folder.lessons=folder.lessons.filter(l=>l.href!==PILOT_GAME_ADDITIONS[1].lesson.href);
 const fields={...await managedPayload(result.data),dataJson:encodeCatalogData(result.data,RELEASE_IDS)};
 assert.deepEqual(releaseCatalogView(fields,result.data),result.data);
});

test('dual game adds exactly one href to an already adopted catalog and keeps the old exam/game',async()=>{
 const href=DUAL_GAME_ADDITION.lesson.href,previous=RELEASE_IDS.filter(id=>id!==DUAL_GAME_RELEASE_ID);
 const old=structuredClone(current);
 const unit=old.find(g=>g.grade==='Grade 8').units.find(u=>u.name==='Đề thi GHK1');
 unit.lessons=unit.lessons.filter(l=>l.href!==href);
 const before=structuredClone(old),fields={...await managedPayload(old),dataJson:encodeCatalogData(old,previous)};
 const view=releaseCatalogView(fields,old),folder=view.find(g=>g.grade==='Grade 8').units.find(u=>u.name==='Đề thi GHK1');
 assert.deepEqual(old,before);assert.equal(addReleaseLessons(old,previous).added,1);
 const trio=folder.lessons.filter(l=>l.href.startsWith('grade-8/De_thi_GHK1/1_THCS Truc Tuan/'));
 assert.equal(trio.length,3);assert.equal(trio[0].title,'Đề 01 · THCS Trực Tuấn');
 assert.ok(trio[1].href.endsWith('/truc-tuan-game-test.html'));assert.equal(trio[2].href,href);
 assert.equal(trio[2].title,'Game đề số 1 – THCS Trực Tuấn (2 chế độ)');
 for(const grade of old.filter(g=>g.grade!=='Grade 8'))assert.deepEqual(view.find(g=>g.grade===grade.grade),grade);
 assert.deepEqual(folder.lessons.filter(l=>l.href!==href),unit.lessons);
 assert.equal(addReleaseLessons(view,previous).added,0);
});

test('dual release preserves custom hidden titles and respects deletion after adoption',async()=>{
 const href=DUAL_GAME_ADDITION.lesson.href,old=structuredClone(current),previous=RELEASE_IDS.filter(id=>id!==DUAL_GAME_RELEASE_ID);
 const grade=old.find(g=>g.grade==='Grade 8');grade.grade='Khối 8';
 const unit=grade.units.find(u=>u.name==='Đề thi GHK1');unit.name='Giữa kỳ';unit.hidden=true;
 const game=unit.lessons.find(l=>l.href===href);game.title='Tên Admin đã đặt';game.hidden=true;
 assert.equal(addReleaseLessons(old,previous).added,0);assert.deepEqual(addReleaseLessons(old,previous).data,old);
 unit.lessons=unit.lessons.filter(l=>l.href!==href);
 assert.deepEqual(releaseCatalogView({...await managedPayload(old),dataJson:encodeCatalogData(old,RELEASE_IDS)},old),old);
});
test('encoded relative and owned Pages URLs already in Firebase do not duplicate the dual game',()=>{
 const href=DUAL_GAME_ADDITION.lesson.href,previous=RELEASE_IDS.filter(id=>id!==DUAL_GAME_RELEASE_ID);
 for(const stored of [href.replaceAll(' ','%20'),'https://htenglish232.github.io/library/'+href.replaceAll(' ','%20')]){
  const data=structuredClone(current),unit=data.find(g=>g.grade==='Grade 8').units.find(u=>u.name==='Đề thi GHK1');
  const lesson=unit.lessons.find(l=>l.href===href);lesson.href=stored;lesson.hidden=true;
  const before=structuredClone(data),result=addReleaseLessons(data,previous);
  assert.equal(result.added,0);assert.deepEqual(result.data,before);assert.deepEqual(data,before);
 }
});
