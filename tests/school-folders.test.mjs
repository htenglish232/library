import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {groupSchoolLessons} from '../assets/school-folders.js';
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
