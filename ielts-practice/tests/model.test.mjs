import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {newState,restore,stepsFor,storageKey,wordCount,grade} from '../shared/model.js';
const unit=JSON.parse(readFileSync(new URL('../unit-2-individuals-and-families/unit.json',import.meta.url)));
const key=JSON.parse(readFileSync(new URL('../unit-2-individuals-and-families/answers.json',import.meta.url)));
test('single course sequence has ten review passages, original reading and ten MCQs followed by summary and translation',()=>{
  assert.equal(stepsFor(unit).length,23);
  assert.deepEqual(stepsFor(unit).map(s=>s.kind),[...Array(10).fill('passage'),'reading',...Array(10).fill('mcq'),'summary','translation']);
  assert.match(storageKey(unit),/^ht-ielts:/);
});
test('all source answers score 20/20; support can be repeated and case/edge whitespace are ignored',()=>{
  const state=newState(unit);
  state.answers.mcq=key.multipleChoice.map(q=>q.answer);
  state.answers.summary=key.summary.map(s=>'  '+s.toUpperCase()+'  ');
  const result=grade(state,key);
  assert.deepEqual([result.correct,result.wrong,result.blank,result.completion],[20,0,0,100]);
  assert.equal(state.answers.summary[1],state.answers.summary[2]);
});
test('blank/wrong counts are exclusive; synonyms and interior whitespace are not accepted',()=>{
  const state=newState(unit);state.answers.mcq[0]='A';state.answers.mcq[1]='B';
  state.answers.summary[0]='behaviour';state.answers.summary[1]='   ';state.answers.summary[3]='relation ships';
  const result=grade(state,key);
  assert.deepEqual([result.correct,result.wrong,result.blank,result.completion],[1,3,16,20]);
  assert.equal(result.needsReview.length,19);
});
test('translation never changes automatic score or completion and is not assigned a band',()=>{
  const state=newState(unit);const before=grade(state,key);
  state.answers.translation=key.referenceTranslation;
  assert.deepEqual(grade(state,key),before);
  assert.equal(wordCount('  one\n two\tthree  '),3);assert.equal(wordCount(' '),0);
  assert.ok(!('band' in before));
});
test('round-trip preserves all answers, translation and cursor without touching GHK1 or another unit',()=>{
  const state=newState(unit);state.started=true;state.name='Nguyễn An';state.step=22;state.view='work';
  state.answers.translation='My draft.\nAnother line.';state.answers.summary[3]='relationships';
  assert.deepEqual(restore(unit,JSON.parse(JSON.stringify(state))),state);
  assert.deepEqual(restore(unit,{...state,unit:'unit-3'}),newState(unit));
  const bounded=restore(unit,{...state,step:900,readingMark:100,answers:{mcq:['Z'],summary:[{},42],translation:{bad:true}}});
  assert.equal(bounded.step,22);assert.equal(bounded.readingMark,-1);assert.equal(bounded.answers.translation,'');
  assert.equal(bounded.answers.mcq[0],'');assert.equal(bounded.answers.summary[0],'');
});
test('submission grading is pure, so wrong-answer review cannot rewrite the submitted result',()=>{
  const state=newState(unit);state.submittedAt=new Date().toISOString();const original=JSON.stringify(state);
  grade(state,key);assert.equal(JSON.stringify(state),original);
  assert.equal(restore(unit,{...state,started:true,name:'An',view:'results'}).view,'results');
});
