import {fullExamRuntime} from './full-exam-contract.mjs';
import {GRADE7_DUAL_ID,GRADE7_DUAL_LINKS} from '../assets/grade7-dual-links.js';
import {GRADE6_DUAL_ID,GRADE6_DUAL_LINKS} from '../assets/grade6-dual-links.js';
import {beforeSoundBootstrap,isDualLauncher} from './sound-bootstrap-contract.mjs';
import {test} from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import vm from 'node:vm';import {createHash} from 'node:crypto';import {execFileSync} from 'node:child_process';
import {addReleaseLessons,RELEASE_IDS,releaseCatalogView} from '../assets/catalog-release.js';
import {GRADE8_PILOT_DUAL_ID,GRADE8_PILOT_DUAL_LINKS,GRADE8_REMAINING_DUAL_ID,GRADE8_REMAINING_DUAL_LINKS} from '../assets/grade8-dual-links.js';
import {numberSchoolLessons} from '../assets/school-folders.js';import {encodeCatalogData,managedPayload} from '../assets/catalog-data.js';
const inventory=JSON.parse(fs.readFileSync('docs/grade8-all-dual-mode/inventory.json')).games;
const current=JSON.parse(fs.readFileSync('catalog/current-library-catalog.json')).data;
const before=JSON.parse(execFileSync('git',['show','bcf44e9:catalog/current-library-catalog.json'])).data;
const additions=[...GRADE8_PILOT_DUAL_LINKS,...GRADE8_REMAINING_DUAL_LINKS];
const unit=data=>data.find(g=>g.grade==='Grade 8').units.find(u=>u.name==='Đề thi GHK1');
const model=vm.createContext({});for(const file of ['model.js','dual-progress.js','dual-store.js'])vm.runInContext(fs.readFileSync('grade-8/De_thi_GHK1/shared-practice/'+file,'utf8'),model);
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
test('disk/catalog inventory: exactly 19 source exams, 17 schools, 19 distinct complete dual games',()=>{
 assert.equal(inventory.length,19);assert.equal(new Set(inventory.map(r=>r.school)).size,17);assert.equal(new Set(inventory.map(r=>r.game)).size,19);
 assert.equal(additions.length,18);assert.equal(unit(current).lessons.length,42);const groups=numberSchoolLessons(unit(current).lessons);
 assert.equal(groups.length,17);assert.equal(groups.flatMap(g=>g.lessons).filter(l=>l.kind==='exam').length,19);
 for(const row of inventory){
  const folder=path.dirname(row.game),file=path.join(folder,row.game.includes('truc-tuan')?'truc-tuan-dual-data.js':'practice-dual-data.js');const c={window:{}};vm.runInNewContext(fs.readFileSync(file,'utf8'),c);const data=c.window.HT_PRACTICE_DATA;
  assert.equal(model.HTPracticeModel.validate(data),true);assert.equal(data.questions.length,row.questions);assert.equal(data.exam.sourceSha256,sha(fs.readFileSync(row.source)));
  assert.deepEqual(Array.from(data.questions,q=>q.number),Array.from({length:row.questions},(_,i)=>i+1));assert.equal(new Set(data.questions.map(q=>q.id)).size,row.questions);
  assert.equal(row.maxXP,data.questions.filter(q=>q.autoGrade).length*10);
  for(const t of data.tracks){assert(fs.existsSync(path.join(folder,t.src)));if(t.sha256)assert.equal(t.sha256,sha(fs.readFileSync(path.join(folder,t.src))));}
  for(const q of data.questions){assert(q.sourceRaw);assert(q.promptHtml);assert(Array.isArray(q.teacherFlags));if(!q.autoGrade)assert(q.teacherFlags.length,'Pending questions must explain why');}
  const lesson=groups.flatMap(g=>g.lessons).find(l=>l.href===row.game);assert.equal(lesson.examHref,row.source);assert.equal(lesson.examNumber,row.examNumber);assert.equal(lesson.displayTitle,`Game đề số ${row.examNumber} – ${row.school} (2 chế độ)`);
 }
 assert.equal(inventory.reduce((n,r)=>n+r.questions,0),793);
});
test('all earlier links, titles, visibility and order remain intact after removing the explicit Grade 6/8 additions',()=>{
 const newHrefs=new Set([...additions,...GRADE6_DUAL_LINKS,...GRADE7_DUAL_LINKS].map(a=>a.lesson.href));const stripped=structuredClone(current);for(const g of stripped)for(const u of g.units)u.lessons=u.lessons.filter(l=>!newHrefs.has(l.href));assert.deepEqual(stripped,before);
 assert.equal(new Set(unit(current).lessons.map(l=>l.href)).size,42);
});
test('new batches deduplicate encoded/Pages URLs and preserve hidden renamed lessons and deletion after adoption',async()=>{
 for(const patch of additions){
  const server=structuredClone(before),u=unit(server);u.lessons.push({...patch.lesson,title:'Admin đổi tên',hidden:true,href:'https://htenglish232.github.io/library/'+encodeURI(patch.lesson.href)});
  const merged=addReleaseLessons(server,[GRADE6_DUAL_ID,GRADE7_DUAL_ID]);assert.equal(merged.added,17);assert(u.lessons.at(-1).hidden);assert(!unit(merged.data).lessons.some(l=>l.href===patch.lesson.href));
 }
 const server=structuredClone(current);const removed=additions[0].lesson.href;unit(server).lessons=unit(server).lessons.filter(l=>l.href!==removed);
 const fields={...await managedPayload(server),dataJson:encodeCatalogData(server,RELEASE_IDS)};assert.deepEqual(releaseCatalogView(fields,server),server);
 assert(RELEASE_IDS.includes(GRADE8_PILOT_DUAL_ID));assert(RELEASE_IDS.includes(GRADE8_REMAINING_DUAL_ID));
});
test('original sources and payloads stay identical; launcher HTML only adds the reviewed sound bootstrap',()=>{
 const paths=execFileSync('git',['ls-tree','-rz','--name-only','bcf44e9'],{maxBuffer:2000000}).toString().split('\0').filter(Boolean);
 const shared=new Set(['dual-mode-engine.js','dual-store.js','model.js','dual-mode.css'].map(f=>'grade-8/De_thi_GHK1/shared-practice/'+f));
 const exact=['assets/firebase-config.js','assets/firebase-client.js','assets/firebase-sdk.js','assets/session.js','assets/catalog-store.js','assets/catalog-data.js','assets/catalog-integrity.js','catalog/library-catalog.json','firestore.rules','firestore.indexes.json','firebase.json','.firebaserc'];
 const protectedPaths=paths.filter(p=>(p.startsWith('grade-')&&!shared.has(p)&&!fullExamRuntime.has(p))||exact.includes(p));
 for(const file of protectedPaths){const current=fs.readFileSync(file),original=execFileSync('git',['show','bcf44e9:'+file],{maxBuffer:20000000});assert.equal(sha(isDualLauncher(file)?beforeSoundBootstrap(current.toString()):current),sha(original),file);}
 assert(protectedPaths.length>340);
});
