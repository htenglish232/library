import {test} from 'node:test';
import assert from 'node:assert/strict';
import {runtime,sourceGames,legacyRecords,student} from './legacy-progress-fixtures.mjs';
const games=sourceGames();
const {HTDualProgress:P,HTDualStore:S}=runtime();
const plain=value=>JSON.parse(JSON.stringify(value));
test('all 49 games read genuine pre-upgrade challenge/ordered/review records losslessly',()=>{
 assert.equal(games.length,49);
 for(const {path,data} of games){
  for(const [scenario,raw] of Object.entries(legacyRecords(data))){
   const before=JSON.stringify(raw),state=P.restore(data,student,raw);
   assert.equal(state.mode,'ordered',path+scenario);
   assert.equal(state.view,raw.view==='challenges'?'play':raw.view);
   for(const field of ['answers','cursorId','review','reviewIds','student','examId','contentVersion'])assert.deepEqual(plain(state[field]),raw[field],path+':'+scenario+':'+field);
   assert.equal(JSON.stringify(raw),before,'migration must not mutate the old record');
   assert.equal(P.summary(data,state).xp,10);
   assert.deepEqual(plain(P.list(data,state)).map(q=>q.id),data.questions.filter(q=>!state.review||state.reviewIds.includes(q.id)).map(q=>q.id));
   const key=S.keyFor(data,student),record=JSON.stringify({schemaVersion:1,examId:data.exam.id,contentVersion:data.contentVersion,state:raw});
   const memory=new Map([[key,record],['unrelated-student','preserved']]);
   const storage={getItem:k=>memory.get(k)??null,setItem:(k,v)=>memory.set(k,v)};
   const handle=S.open(data,student,storage);
   assert.equal(handle.status,'found');assert.equal(memory.get(key),record,'opening must not write');
   assert.equal(handle.save(handle.state),'saved');
   assert.deepEqual(JSON.parse(memory.get(key)).state.answers,raw.answers);
   assert.equal(memory.get('unrelated-student'),'preserved');
   const stable=memory.get(key);assert.equal(handle.save(handle.state),'saved');assert.equal(memory.get(key),stable,'repeat save is idempotent');
  }
 }
});
