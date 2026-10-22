import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const context=vm.createContext({});
vm.runInContext(fs.readFileSync('grade-8/De_thi_GHK1/shared-practice/model.js','utf8'),context);
const model=context.HTPracticeModel;
const files=['11_THCS_Truc_Khang','12_THCS_Truc_Hung','19_THCS_Truc_Chinh'];
const data=files.map(folder=>JSON.parse(fs.readFileSync(`grade-8/De_thi_GHK1/${folder}/practice-game-data.js`,'utf8').split('window.HT_PRACTICE_DATA = ')[1].trim().slice(0,-1)));
test('three distinct source counts validate with their own sections and stable IDs',()=>{
 assert.deepEqual(data.map(d=>d.questions.length),[42,43,42]);
 for(const d of data){assert.equal(model.validate(d),true);assert.equal(new Set(d.questions.map(q=>q.id)).size,d.questions.length);}
});
test('schema accepts a different number of sections and rejects missing/duplicate data',()=>{
 const d=structuredClone(data[0]);d.questions=[d.questions[0]];d.sections=d.sections.filter(s=>s.id===d.questions[0].section);
 assert.equal(model.validate(d),true);
 d.questions.push(structuredClone(d.questions[0]));assert.throws(()=>model.validate(d));
 const missing=structuredClone(data[0]);missing.questions[0].options=[];assert.throws(()=>model.validate(missing));
 const contextMissing=structuredClone(data[0]);contextMissing.contexts=[];assert.throws(()=>model.validate(contextMissing));
});
test('all source options, exact text variants and tuples are graded without side effects',()=>{
 for(const d of data)for(const q of d.questions){
  const before=JSON.stringify(q);
  if(!q.autoGrade)assert.equal(model.evaluate(q,'any answer'),null);
  else if(q.kind==='multi-text'){
   assert.equal(model.evaluate(q,'',q.acceptedTuples[0]),true);
   assert.equal(model.evaluate(q,'',['wrong',...q.acceptedTuples[0].slice(1)]),false);
  }else for(const answer of q.accepted)assert.equal(model.evaluate(q,answer),true);
  assert.equal(JSON.stringify(q),before);
 }
});
test('negations, missing ideas and answer substrings do not earn a correct result',()=>{
 for(const d of data)for(const q of d.questions.filter(q=>q.autoGrade&&q.kind==='text')){
  assert.equal(model.evaluate(q,'not '+q.accepted[0]),false,q.id);
  const words=q.accepted[0].split(' ');if(words.length>2&&!q.accepted.some(a=>model.normalize(a)===model.normalize(words[0])))assert.equal(model.evaluate(q,words[0]),false,q.id);
 }
});
test('inconsistent Truc Chinh word cards are preserved and require teacher review',()=>{
 const q=data[2].questions.find(q=>q.id==='D1_1');
 assert.equal(q.autoGrade,false);assert.ok(q.tokens.includes('fluent'));assert.ok(q.tokens.includes('speaks'));
 assert.equal(model.evaluate(q,q.answerLabel),null);assert.ok(q.teacherFlags.length);
});
test('AI supplements are separate, explicitly unverified, and cannot provide grading keys',()=>{
 for(const folder of files){
  const notes=JSON.parse(fs.readFileSync(`grade-8/De_thi_GHK1/${folder}/practice-game-support.js`,'utf8').split('window.HT_PRACTICE_SUPPORT = ')[1].trim().slice(0,-1));
  assert.equal(notes.provenance,'AI-generated');assert.equal(notes.teacherVerified,false);
  for(const item of Object.values(notes.items))assert.ok(!('accepted' in item)&&!('correct' in item));
 }
});
