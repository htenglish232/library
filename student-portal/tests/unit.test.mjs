import {test} from 'node:test';
import assert from 'node:assert/strict';
import {parseAssignment,studentEmail} from '../assets/routing.js';
import {evaluate,data} from '../functions/src/grading.js';
import {validateRows,demoStudents} from '../functions/src/provision.js';
import {correctAnswers} from './fixtures.mjs';
import {buildPortal} from '../../tools/build-student-portal.mjs';
test('build guard refuses production, placeholder app configuration and private credential fields before writing artifacts',async()=>{
  await assert.rejects(buildPortal({emulator:false,firebase:{projectId:'ht-english-library'}}));
  await assert.rejects(buildPortal({emulator:false,firebase:{projectId:'ht-english-student-staging',apiKey:'COPY_PUBLIC_WEB_API_KEY',appId:'COPY_WEB_APP_ID',authDomain:'ht-english-student-staging.firebaseapp.com'}}));
  await assert.rejects(buildPortal({emulator:true,firebase:{projectId:'demo-ht-student-portal',private_key:'must-never-be-written'}}));
});
test('assignment resolver accepts IDs and rejects arbitrary redirects, duplicate/encoded paths',()=>{
  assert.equal(parseAssignment('?assignment=truc-tuan-grade8-demo'),'truc-tuan-grade8-demo');
  assert.equal(parseAssignment(''),null);
  for(const input of ['?assignment=https://evil.test','?assignment=//evil.test','?assignment=..%2Fa',
    '?assignment=a&assignment=b','?redirect=https://evil.test','?assignment=%2561','?assignment=<svg>']){
    assert.throws(()=>parseAssignment(input),input);
  }
});
test('student ID uses a single deterministic password-login identity; rejects malformed IDs',()=>{
  assert.equal(studentEmail(' ht0001 '),'ht0001@students.htenglish.invalid');
  for(const id of ['HT','a@b.test','HT0001/../x','ＨＴ0001','HT0001\nHT0002'])assert.throws(()=>studentEmail(id));
});
test('the unchanged source grader evaluates all 42 answers including token arrangement',()=>{
  assert.equal(data.questions.length,42);
  const result=evaluate(correctAnswers());
  assert.equal(result.correct,42);assert.equal(result.score,10);assert.equal(result.xp,420);
  const wrong=correctAnswers();wrong.q1.value='A';wrong.q31.value='wrong';
  const r=evaluate(wrong);assert.equal(r.correct,40);assert.equal(r.wrong,2);
  wrong.q31.value='';assert.equal(evaluate(wrong).unanswered,1);
});
test('answer validation rejects unknown/missing questions, invalid choices/tokens and oversized strings',()=>{
  for(const mutate of [a=>delete a.q1,a=>{a.extra=a.q1;},a=>{a.q1.value='E';},
    a=>{a.q36.tokens=[1,1];},a=>{a.q31.value='x'.repeat(1501);},a=>{a.q1.score=10;}]){
    const answers=correctAnswers();mutate(answers);assert.throws(()=>evaluate(answers));
  }
});
test('bulk provisioning validates the entire identity set before writes',()=>{
  validateRows(demoStudents);
  assert.throws(()=>validateRows([...demoStudents,demoStudents[0]]));
  assert.throws(()=>validateRows([{...demoStudents[0],role:'admin'}]));
  assert.throws(()=>validateRows([{...demoStudents[0],displayName:'x'.repeat(81)}]));
});
