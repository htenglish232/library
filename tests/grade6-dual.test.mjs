import {test} from 'node:test';import assert from 'node:assert/strict';
import fs from 'node:fs';import path from 'node:path';import vm from 'node:vm';import {execFileSync} from 'node:child_process';import {createHash} from 'node:crypto';
import {GRADE6_DUAL_ID,GRADE6_DUAL_LINKS} from '../assets/grade6-dual-links.js';
import {addReleaseLessons,releaseCatalogView,RELEASE_IDS} from '../assets/catalog-release.js';
import {managedPayload,encodeCatalogData} from '../assets/catalog-data.js';
import {numberSchoolLessons} from '../assets/school-folders.js';
const baseline='7407b43',rows=JSON.parse(fs.readFileSync('docs/grade6-dual-mode/inventory.json')).games;
const source=JSON.parse(fs.readFileSync('docs/grade6-dual-mode/source-inventory.json'));
const current=JSON.parse(fs.readFileSync('catalog/current-library-catalog.json')).data;
const before=JSON.parse(execFileSync('git',['show',baseline+':catalog/current-library-catalog.json'])).data;
const grade6=d=>d.find(g=>g.grade==='Grade 6'),unit=d=>grade6(d).units.find(u=>u.name==='Đề thi GHK1');
const sha=b=>createHash('sha256').update(b).digest('hex'),context=vm.createContext({});
for(const f of ['model.js','dual-progress.js','dual-store.js'])vm.runInContext(fs.readFileSync('grade-8/De_thi_GHK1/shared-practice/'+f,'utf8'),context);
const data=row=>{const c={window:{}};vm.runInNewContext(fs.readFileSync(path.join(path.dirname(row.game),'practice-dual-data.js'),'utf8'),c);return c.window.HT_PRACTICE_DATA;};
test('16 real source exams / 14 catalog schools / 661 source questions; 16 complete games, no extra engine',()=>{
 assert.equal(rows.length,16);assert.equal(new Set(rows.map(r=>r.school)).size,14);assert.equal(rows.reduce((n,r)=>n+r.questions,0),661);assert.equal(GRADE6_DUAL_LINKS.length,16);
 assert.equal(fs.existsSync('grade-6/De_thi_GHK_1/shared-practice'),false);
 const groups=numberSchoolLessons(unit(current).lessons);
 for(const row of rows){
  const d=data(row);assert(context.HTPracticeModel.validate(d));assert.equal(d.questions.length,row.questions);assert.equal(d.exam.id,'grade6-ghk1-source-'+row.folder);assert.equal(d.exam.grade,6);
  assert.equal(sha(fs.readFileSync(row.source)),row.sourceSha256);assert.equal(d.maxXP,d.questions.filter(q=>q.autoGrade).length*10);
  assert.deepEqual(Array.from(d.questions,q=>q.number),Array.from({length:row.questions},(_,i)=>i+1));
  for(const q of d.questions){assert(q.answerEvidence.length);assert(q.sourceRaw);if(!q.autoGrade)assert(q.teacherFlags.length);if(q.autoGrade)assert(q.accepted.length);assert(!/<script|\son\w+=|javascript:/i.test(q.promptHtml+q.options.map(o=>o.html).join('')));}
  const launcher=fs.readFileSync(row.game,'utf8');assert(launcher.includes('../../../grade-8/De_thi_GHK1/shared-practice/dual-mode-engine.js'));assert(launcher.includes('English Quest 6'));assert(!launcher.includes('English Quest 8'));assert(!launcher.includes('GRADE 8'));assert(launcher.includes('GRADE 6'));assert(launcher.includes('id="sound-toggle"'));
  const pair=groups.flatMap(g=>g.lessons).find(l=>l.href===row.game);assert.equal(pair.examHref,row.source);assert.equal(pair.examNumber,row.number);assert.equal(pair.displayTitle,`Game đề số ${row.number} – ${row.school} (2 chế độ)`);
 }
 assert.deepEqual(source.rows.map(r=>r.questions),rows.map(r=>r.questions));
});
test('source-only answers: malformed JSON and absent phonetic underlines stay pending; source prefixes use full text without invented tiles',()=>{
 const cuong=data(rows.find(r=>r.folder===1));assert(cuong.questions[0].transcriptHtml.includes("Tom: Hi Jack."));
 const dao=data(rows.find(r=>r.folder===11));const broken=dao.questions.find(q=>q.id==='rewrite4');assert(!broken.autoGrade);assert(broken.teacherFlags.some(s=>s.includes('data-valid')));
 const viet=data(rows.find(r=>r.folder===14));const q=viet.questions.find(q=>q.id==='w4');assert.equal(q.kind,'text');assert(q.autoGrade);assert.equal(q.sourceTokens.length,6);const trung=data(rows.find(r=>r.folder===5)).questions.find(q=>q.id==='W1_3');assert(trung.accepted.includes('Is the bag small or big?'));assert.equal(context.HTPracticeModel.evaluate(trung,'is THE bag small or BIG ?'),true);assert(q.accepted.includes('My school is in front of some tall trees.'));
 const phonetic=viet.questions.find(q=>q.id==='lang1');assert(phonetic.options.every(o=>o.html.includes('<u>')));assert(phonetic.autoGrade);
 const thai=data(rows.find(r=>r.folder===15));assert(!thai.questions.find(q=>q.id==='LF1').autoGrade);
});
test('only original approved Listening URLs are linked; 4+5 and 5+4 part boundaries are preserved',()=>{
 assert.equal(rows.reduce((n,r)=>n+r.tracks.length,0),21);
 for(const row of rows){const d=data(row);for(const t of d.tracks){assert.equal(t.sha256,sha(fs.readFileSync(path.join(path.dirname(row.game),decodeURIComponent(t.src)))));assert(fs.readFileSync(row.source,'utf8').includes(t.src));}}
 for(const folder of [1,6,7,14]){const d=data(rows.find(r=>r.folder===folder));assert.equal(d.tracks.length,0);assert(d.questions.filter(q=>q.listeningPart).every(q=>!q.track&&q.contextHtml.includes('chưa có file được xác nhận')));}
 const phuong=data(rows.find(r=>r.folder===10));assert.equal(phuong.questions.find(q=>q.id==='L5').track,'listen-2');
 const dao=data(rows.find(r=>r.folder===13));assert(!dao.questions.find(q=>q.id==='L5').track);assert.equal(dao.questions.find(q=>q.id==='L6').track,'listen-2');
});
test('exactly 16 catalog additions; all old links, other grades, exam numbers and Admin edits preserved',()=>{
 assert.deepEqual(addReleaseLessons(before).data,current);assert.equal(addReleaseLessons(before).added,16);assert.equal(addReleaseLessons(current).added,0);
 const hrefs=new Set(GRADE6_DUAL_LINKS.map(p=>p.lesson.href)),stripped=structuredClone(current);for(const g of stripped)for(const u of g.units)u.lessons=u.lessons.filter(l=>!hrefs.has(l.href));assert.deepEqual(stripped,before);
 assert.equal(unit(current).lessons.length,32);assert.equal(numberSchoolLessons(unit(current).lessons).length,14);
 for(const row of rows)for(const storedHref of [encodeURI(row.game),'https://htenglish232.github.io/library/'+encodeURI(row.game)]){
  const server=structuredClone(before),u=unit(server);u.lessons.push({href:storedHref,title:'Tên Admin',hidden:true});
  const merged=addReleaseLessons(server);assert.equal(merged.added,15);assert.deepEqual(unit(merged.data).lessons.find(l=>l.href===storedHref),u.lessons.at(-1));
 }
});
test('Admin release adoption and later deletion remain respected without production writes',async()=>{
 const server=structuredClone(current),g=grade6(server);g.hidden=true;g.grade='Khối 6';const u=g.units.find(u=>u.type==='exam-folder');u.name='Giữa kỳ';u.hidden=true;
 u.lessons=u.lessons.filter(l=>l.href!==rows[0].game);const fields={...await managedPayload(server),dataJson:encodeCatalogData(server,RELEASE_IDS)};assert.deepEqual(releaseCatalogView(fields,server),server);assert(RELEASE_IDS.includes(GRADE6_DUAL_ID));
});
test('same browser identity, separate Grade 6/8 exam and student keys; shared WAV files unchanged',()=>{
 const d=data(rows[0]),g8={window:{}};vm.runInNewContext(fs.readFileSync('grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-dual-data.js','utf8'),g8);const store=context.HTDualStore,P=context.HTDualProgress;
 const person=P.identity('Học sinh','A');assert.notEqual(store.keyFor(d,person),store.keyFor(g8.window.HT_PRACTICE_DATA,person));assert.notEqual(store.keyFor(d,person),store.keyFor(d,P.identity('Học sinh','B')));
 const map=new Map(),storage={getItem:k=>map.get(k),setItem:(k,v)=>map.set(k,v)};assert(store.remember(person,storage));assert.equal(store.profile(storage).key,person.key);
 for(const name of ['correct','wrong','complete']){const file='grade-8/De_thi_GHK1/shared-practice/sounds/'+name+'.wav';assert.equal(sha(fs.readFileSync(file)),sha(execFileSync('git',['show',baseline+':'+file],{maxBuffer:2000000})));}
});
test('every pre-existing source, audio, Grade 8 game, index, Firebase and other class file remains identical; controller permits only a grade caption',()=>{
 for(const file of source.files)assert.equal(sha(fs.readFileSync(file.path)),file.sha256,file.path);
 const tracked=execFileSync('git',['ls-tree','-rz','--name-only',baseline],{maxBuffer:2000000}).toString().split('\0').filter(Boolean);
 const engine='grade-8/De_thi_GHK1/shared-practice/dual-mode-engine.js';
 const oldEngine=execFileSync('git',['show',baseline+':'+engine],{encoding:'utf8'});
 const oldLine=oldEngine.split('\n').find(line=>line.includes("$('section-kicker').textContent"));
 const lines=fs.readFileSync(engine,'utf8').split('\n');
 const restored=lines.filter(line=>!line.includes("const gradeLabel=source.exam.grade===6")).map(line=>line.includes("$('section-kicker').textContent")?oldLine:line).join('\n');assert.equal(restored,oldEngine,'Only the grade caption may change in the shared controller');
 const exact=tracked.filter(p=>p!==engine).filter(p=>p.startsWith('grade-')||['index.html','admin.html','firebase.json','firestore.rules','firestore.indexes.json','.firebaserc'].includes(p)||['assets/firebase','assets/session','assets/catalog-editor','assets/catalog-store','assets/catalog-data','assets/catalog-view','assets/school-folders'].some(prefix=>p.startsWith(prefix)));
 assert.equal(execFileSync('git',['diff',baseline,'--name-only','--',...exact],{maxBuffer:2000000}).toString(),'');
});
