import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {groupSchoolLessons,numberSchoolLessons} from '../assets/school-folders.js';
import {visibleCatalog} from '../assets/catalog-data.js';
const data=JSON.parse(readFileSync('catalog/current-library-catalog.json','utf8')).data;
const examFolder=grade=>data.find(g=>g.grade===grade).units.find(u=>u.type==='exam-folder');
test('all original exam and game URLs occur once, with unchanged titles, across school folders',()=>{
 for(const g of data)for(const u of g.units.filter(u=>u.type==='exam-folder')){
  const original=structuredClone(u.lessons),grouped=groupSchoolLessons(u.lessons);
  const actual=grouped.flatMap(s=>s.lessons.map(({kind,...lesson})=>lesson));
  assert.deepEqual(actual.toSorted((a,b)=>a.href.localeCompare(b.href)),original.toSorted((a,b)=>a.href.localeCompare(b.href)));
  assert.deepEqual(u.lessons,original);
 }
});
test('Truc Tuan exam and game share one school and retain distinct resource types',()=>{
 const group=groupSchoolLessons(examFolder('Grade 8').lessons).find(s=>s.name==='THCS Trực Tuấn');
 assert.deepEqual(group.lessons.map(l=>l.kind),['exam','game']);
 assert.ok(group.lessons[1].href.endsWith('/truc-tuan-game-test.html'));
});
test('multiple exams from the same school merge without conflating different schools or grades',()=>{
 const groups=groupSchoolLessons(examFolder('Grade 8').lessons);
 assert.equal(groups.find(s=>s.name==='THCS Phương Định').lessons.length,2);
 assert.equal(groups.find(s=>s.name==='THCS Đào Sư Tích').lessons.length,2);
 assert.equal(groups.find(s=>s.name==='THCS Trực Tuấn').lessons.length,2);
 const grade6=groupSchoolLessons(examFolder('Grade 6').lessons);
 assert.equal(grade6.find(s=>s.name==='THCS Trực Hùng').lessons.length,2);
 assert.equal(grade6.find(s=>s.name==='THCS Trực Tuấn').lessons.length,1);
});
test('game placed before exam uses exact school directory, including nested game paths',()=>{
 const source=examFolder('Grade 8').lessons.slice(0,2);
 const game={...source[1],title:'Game phiên bản mới',href:source[1].href.replace('truc-tuan-game-test.html','games/new-game.html')};
 const result=groupSchoolLessons([game,source[0]]);
 assert.equal(result.length,1);assert.equal(result[0].name,'THCS Trực Tuấn');
 assert.deepEqual(result[0].lessons.map(l=>l.href),[game.href,source[0].href]);
});
test('hidden lessons and folders stay absent when rendering the visible server catalog',()=>{
 const raw=structuredClone(data),grade=raw.find(g=>g.grade==='Grade 8'),unit=grade.units.find(u=>u.type==='exam-folder');
 const game=unit.lessons.find(l=>l.href.includes('truc-tuan-game-test'));game.hidden=true;
 let visible=visibleCatalog(raw).find(g=>g.grade==='Grade 8').units.find(u=>u.type==='exam-folder');
 assert.ok(!groupSchoolLessons(visible.lessons).flatMap(s=>s.lessons).some(l=>l.href===game.href));
 unit.hidden=true;
 assert.ok(!visibleCatalog(raw).find(g=>g.grade==='Grade 8').units.some(u=>u.type==='exam-folder'));
});
test('unknown custom resources remain visible without inventing a school or game',()=>{
 const original=[{title:'Bài Admin mới',href:'https://example.com/custom.html'},{title:'Bài khác',href:'https://example.net/custom.html'}];
 const groups=groupSchoolLessons(original);
 assert.equal(groups.length,2);assert.deepEqual(groups.map(s=>s.name),original.map(l=>l.title));
 assert.ok(groups.every(s=>s.lessons.every(l=>l.kind==='exam')));
});

test('Grade 8 real inventory has 17 schools, 19 numbered exams and exactly four paired games',()=>{
 const original=structuredClone(examFolder('Grade 8').lessons),groups=numberSchoolLessons(original);
 assert.equal(groups.length,17);
 const rows=groups.flatMap(g=>g.lessons);
 assert.equal(rows.filter(l=>l.kind==='exam').length,19);
 assert.equal(rows.filter(l=>l.kind==='game').length,4);
 assert.deepEqual(rows.map(l=>l.href).toSorted(),original.map(l=>l.href).toSorted());
 for(const g of groups){
  const exams=g.lessons.filter(l=>l.kind==='exam');
  assert.deepEqual(exams.map(l=>l.examNumber),exams.map((_,i)=>i+1));
  for(const l of g.lessons){
   assert.equal(l.displayTitle,`${l.kind==='game'?'Game đề':'Đề'} số ${l.examNumber} – ${g.name}`);
   assert.ok(g.lessons.some(e=>e.href===l.examHref&&e.kind==='exam'));
  }
 }
 assert.deepEqual(original,examFolder('Grade 8').lessons);
 for(const name of ['THCS Đào Sư Tích','THCS Phương Định'])assert.deepEqual(groups.find(g=>g.name===name).lessons.map(l=>l.examNumber),[1,2]);
});

test('future explicit catalog titles pair multiple exams and games even in the same directory',()=>{
 const base='grade-8/De_thi_GHK2/THCS_New/';
 const input=[
  {title:'Game đề số 2 – THCS Mới',href:base+'game-2.html'},
  {title:'Đề số 2 – THCS Mới',href:base+'exam-2.html'},
  {title:'Game đề số 1 – THCS Mới',href:base+'game-1.html'},
  {title:'Đề số 1 – THCS Mới',href:base+'exam-1.html'},
 ];
 const before=structuredClone(input),groups=numberSchoolLessons(input);
 assert.equal(groups.length,1);assert.equal(groups[0].name,'THCS Mới');
 assert.deepEqual(groups[0].lessons.map(l=>[l.kind,l.examNumber]),[['exam',1],['game',1],['exam',2],['game',2]]);
 assert.deepEqual(groups[0].lessons.filter(l=>l.kind==='game').map(l=>l.examHref),[base+'exam-1.html',base+'exam-2.html']);
 assert.deepEqual(input,before);
});

test('games in nested directories pair by the nearest actual exam, independent of catalog order',()=>{
 const input=[{title:'Game mới',href:'grade-8/new/2/games/play.html'},
  {title:'Đề số 1 – THCS Mới',href:'grade-8/new/exam.html'},
  {title:'Đề số 2 – THCS Mới',href:'grade-8/new/2/exam.html'}];
 const groups=numberSchoolLessons(input);assert.equal(groups.length,1);
 const game=groups[0].lessons.find(l=>l.kind==='game');assert.equal(game.examNumber,2);
 assert.equal(game.displayTitle,'Game đề số 2 – THCS Mới');
});

test('hidden first exam retains its reserved number and does not relabel the second',()=>{
 const input=[{title:'Đề 01 · THCS Mới',href:'grade-8/new/1/exam.html',hidden:true},
  {title:'Đề 02 · THCS Mới',href:'grade-8/new/2/exam.html'},
  {title:'Game · THCS Mới',href:'grade-8/new/2/game.html'}];
 const rows=numberSchoolLessons(input)[0].lessons.filter(l=>!l.hidden);
 assert.deepEqual(rows.map(l=>l.examNumber),[2,2]);
});

test('ambiguous same-directory games and orphan resources never receive guessed exam numbers',()=>{
 const input=[{title:'Đề 01 · THCS Mới',href:'grade-8/new/a.html'},
  {title:'Đề 02 · THCS Mới',href:'grade-8/new/b.html'},
  {title:'Game · THCS Mới',href:'grade-8/new/game.html'},
  {title:'Game đề số 3 – THCS Mới',href:'grade-8/new/unknown/game.html'}];
 for(const row of numberSchoolLessons(input)[0].lessons.filter(l=>l.kind==='game')){
  assert.equal(row.examNumber,null);assert.equal(row.displayTitle,row.title);
 }
 const custom={title:'Bài riêng của Admin',href:'https://example.com/custom.html'};
 assert.equal(numberSchoolLessons([custom])[0].lessons[0].displayTitle,custom.title);
});

test('duplicate explicit exam numbers stay unpaired instead of silently inventing numbering',()=>{
 const input=[{title:'Đề số 1 – THCS Mới',href:'grade-8/new/a.html'},
  {title:'Đề số 1 – THCS Mới',href:'grade-8/new/b.html'},
  {title:'Game đề số 1 – THCS Mới',href:'grade-8/new/game.html'}];
 assert.ok(numberSchoolLessons(input)[0].lessons.every(l=>l.examNumber===null));
});

test('Grade 6 has 16 actual exams in 14 schools, with separate Hung and Liem Hai exams and no games',()=>{
 const original=structuredClone(examFolder('Grade 6').lessons),groups=numberSchoolLessons(original,{unclassified:true});
 assert.equal(groups.length,14);assert.equal(groups.flatMap(g=>g.lessons).length,16);
 for(const g of groups){
  assert.ok(g.name.startsWith('THCS '));assert.ok(g.lessons.every(l=>l.kind==='exam'));
  assert.deepEqual(g.lessons.map(l=>l.examNumber),g.lessons.map((_,i)=>i+1));
 }
 for(const name of ['THCS Trực Hùng','THCS Liêm Hải'])assert.deepEqual(groups.find(g=>g.name===name).lessons.map(l=>l.examNumber),[1,2]);
 assert.deepEqual(original,examFolder('Grade 6').lessons);
});

test('Grade 7 Dao Su Tich has a verified THCS label without changing its stored title or href',()=>{
 const href='grade-7/De_thi_GHK_1/13_Dao_Su_Tich/13 Dao Su Tich.html';
 assert.match(readFileSync(href,'utf8'),/<h2>THCS Đào Sư Tích<\/h2>/u);
 const groups=numberSchoolLessons(examFolder('Grade 7').lessons,{schoolNames:{[href]:'THCS Đào Sư Tích'},unclassified:true});
 assert.equal(groups.length,14);assert.equal(groups.flatMap(g=>g.lessons).length,14);
 const lesson=groups.find(g=>g.name==='THCS Đào Sư Tích').lessons[0];
 assert.equal(lesson.displayTitle,'Đề số 1 – THCS Đào Sư Tích');
 assert.equal(lesson.title,'Đề 13 · Đào Sư Tích');assert.equal(lesson.href,href);
 assert.ok(groups.every(g=>g.lessons.length===1&&g.lessons[0].kind==='exam'&&g.lessons[0].examNumber===1));
});

test('unidentified Grade 6/7 schools form one unclassified folder, keep original titles and never infer a school from the URL',()=>{
 const input=[{title:'Đề thử A',href:'grade-6/De_thi_GHK_1/THCS_Guess/a.html'},
  {title:'Đề thử B',href:'grade-6/De_thi_GHK_1/other/b.html'}];
 const before=structuredClone(input),groups=numberSchoolLessons(input,{unclassified:true});
 assert.equal(groups.length,1);assert.equal(groups[0].name,'Đề thi chưa phân loại');
 assert.deepEqual(groups[0].lessons.map(l=>l.displayTitle),['Đề số 1 – Chưa phân loại','Đề số 2 – Chưa phân loại']);
 assert.deepEqual(groups[0].lessons.map(l=>l.title),input.map(l=>l.title));assert.deepEqual(input,before);
 // Grade 8's default behavior is unchanged.
 assert.equal(numberSchoolLessons(input)[0].name,'Đề thử A');
});

test('future Grade 6/7 games and exam sets use the same pairing rules with numbering isolated per grade',()=>{
 for(const grade of [6,7]){
  const dir=`grade-${grade}/De_thi_HK2/THCS_New/`;
  const input=[{title:'Game đề số 2 – THCS Mới',href:dir+'game2.html'},
   {title:'Đề số 2 – THCS Mới',href:dir+'exam2.html'},
   {title:'Đề số 1 – THCS Mới',href:dir+'exam1.html',hidden:true}];
  const rows=numberSchoolLessons(input,{unclassified:true})[0].lessons;
  assert.deepEqual(rows.map(l=>[l.kind,l.examNumber]),[['exam',1],['exam',2],['game',2]]);
  assert.equal(rows[2].examHref,dir+'exam2.html');assert.equal(rows[2].displayTitle,'Game đề số 2 – THCS Mới');
 }
});
