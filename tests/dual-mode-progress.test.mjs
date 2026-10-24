import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const folder='grade-8/De_thi_GHK1/';
const data=JSON.parse(readFileSync(folder+'1_THCS Truc Tuan/truc-tuan-dual-data.js','utf8').split('window.HT_PRACTICE_DATA = ')[1].trim().slice(0,-1));
const context=vm.createContext({});
for(const file of ['model.js','dual-progress.js','dual-store.js'])vm.runInContext(readFileSync(folder+'shared-practice/'+file,'utf8'),context);
const P=context.HTDualProgress,S=context.HTDualStore,M=context.HTPracticeModel;
const learner={name:'Học sinh A',code:'8A-01'};
const plain=o=>JSON.parse(JSON.stringify(o));
function tokenOrder(q){
 const words=M.normalize(q.accepted[0]).split(' ').filter(Boolean);
 function solve(indices,left){if(indices.length===q.tokens.length)return !left.length?indices:null;
  for(let i=0;i<q.tokens.length;i++){const part=M.normalize(q.tokens[i]).split(' ').filter(Boolean);
   if(!indices.includes(i)&&part.every((w,k)=>w===left[k])){const found=solve([...indices,i],left.slice(part.length));if(found)return found;}
  }return null;
 }return solve([],words);
}
function fill(state,q,wrong=false){const draft=P.blank(q);
 if(q.kind==='rearrange'){draft.tokens=tokenOrder(q);if(wrong)[draft.tokens[0],draft.tokens[1]]=[draft.tokens[1],draft.tokens[0]];}
 else draft.value=wrong?(q.kind==='choice'?q.options.find(o=>!q.accepted.includes(o.value)).value:'not '+q.accepted[0]):q.accepted[0];
 P.update(data,state,q.id,draft);
}
class MemoryStorage{map=new Map();getItem(k){return this.map.get(k)??null;}setItem(k,v){this.map.set(k,v);}removeItem(k){this.map.delete(k);}}

test('42 real questions, four source sections and source-only accepted variants validate',()=>{
 assert.equal(M.validate(data),true);assert.equal(data.questions.length,42);assert.equal(data.sections.length,4);
 assert.deepEqual(data.questions.map(q=>q.id),Array.from({length:42},(_,i)=>'q'+(i+1)));
 const state=P.create(data,learner);
 for(const q of data.questions){fill(state,q);P.check(data,state,q.id);}
 assert.equal(P.summary(data,state).xp,420);assert.equal(P.summary(data,state).correct,42);
});
test('mode changes and repeated checks share immutable first attempts and never duplicate XP',()=>{
 const state=P.create(data,learner),q=data.questions[0];fill(state,q);P.check(data,state,q.id);
 const first=JSON.stringify(state.answers.q1.first);
 for(let i=0;i<10;i++){P.setMode(data,state,i%2?'ordered':'challenge');assert.equal(P.check(data,state,q.id),false);}
 assert.equal(P.summary(data,state).xp,10);assert.equal(JSON.stringify(state.answers.q1.first),first);
 assert.equal(P.update(data,state,q.id,P.blank(q)),false);assert.equal(Object.isFrozen(state.answers.q1.first.draft),true);
});
test('ordered mode uses original global order while challenge navigation filters real sections',()=>{
 const state=P.create(data,learner);P.setMode(data,state,'ordered');P.go(data,state,'q31');
 assert.equal(P.list(data,state).length,42);assert.equal(state.cursorId,'q31');
 P.setMode(data,state,'challenge');assert.equal(state.cursorId,'q31');assert.equal(state.section,'reading');
 assert.equal(P.list(data,state).length,10);
});
test('wrong choice/text/builder review and reload preserve first-score 390 XP',()=>{
 const state=P.create(data,learner),wrong=new Set(['q1','q31','q36']);
 for(const q of data.questions){fill(state,q,wrong.has(q.id));P.check(data,state,q.id);}
 assert.equal(P.summary(data,state).xp,390);const first=JSON.stringify(Object.values(state.answers).map(a=>a.first));
 P.beginReview(data,state);for(const id of state.reviewIds){const q=data.questions.find(q=>q.id===id);fill(state,q);P.check(data,state,id);}
 const restored=P.restore(data,learner,plain(state));assert.equal(P.summary(data,restored).xp,390);
 assert.equal(JSON.stringify(Object.values(restored.answers).map(a=>a.first)),first);
});
test('partial drafts, token indices and review drafts survive round-trip independently',()=>{
 const state=P.create(data,learner),q=data.questions.find(q=>q.id==='q36');
 const draft=P.blank(q);draft.tokens=[0,3];P.update(data,state,q.id,draft);P.go(data,state,q.id);
 const restored=P.restore(data,learner,plain(state));assert.deepEqual(plain(P.draft(data,restored,q.id).tokens),[0,3]);
 assert.throws(()=>P.check(data,restored,q.id),/ghép đủ/);
 const duplicate={...plain(draft),tokens:[1,1]};assert.throws(()=>P.update(data,restored,q.id,duplicate),/Thẻ từ/);
});
test('full text matching rejects missing meaning and negation, accepts only explicit Yes variant',()=>{
 const state=P.create(data,learner);
 for(const [id,answer] of [['q31','collect water'],['q33','not yes'],['q40','more slowly than']]){
  const q=data.questions.find(q=>q.id===id);P.update(data,state,id,{...P.blank(q),value:answer});P.check(data,state,id);
  assert.equal(state.answers[id].first.result,'wrong');
 }assert.equal(P.summary(data,state).xp,0);
 assert.equal(M.evaluate(data.questions.find(q=>q.id==='q33'),'Yes.'),true);
});
test('corrupt/tampered snapshots, different learner/exam and stale source are rejected',()=>{
 const state=P.create(data,learner);fill(state,data.questions[0]);P.check(data,state,'q1');
 const altered=plain(state);altered.answers.q1.first.result='wrong';assert.throws(()=>P.restore(data,learner,altered));
 assert.throws(()=>P.restore(data,{name:'Học sinh B'},state));
 assert.throws(()=>P.restore({...data,exam:{...data.exam,id:'other-exam'}},learner,state));
 assert.throws(()=>P.restore({...data,contentVersion:'new-source'},learner,state));
 const missing=plain(state);delete missing.answers.q42;assert.throws(()=>P.restore(data,learner,missing));
});
test('each exam and learner/code gets a distinct key; normalized same identity resumes',()=>{
 const storage=new MemoryStorage(),a=P.create(data,learner);fill(a,data.questions[0]);P.check(data,a,'q1');
 const first=S.open(data,learner,storage);assert.equal(first.save(a),'saved');
 assert.equal(S.open(data,{name:'  HỌC SINH A ',code:'8a-01'},storage).status,'found');
 for(const student of [{name:'Học sinh B',code:'8A-01'},{name:learner.name,code:'8A-02'}])assert.equal(S.open(data,student,storage).status,'empty');
 assert.equal(S.open({...data,exam:{...data.exam,id:'exam-2'}},learner,storage).status,'empty');
});
test('reset only removes the selected learner/exam and invalid records require explicit reset',()=>{
 const storage=new MemoryStorage(),other={name:'Học sinh B'};
 S.open(data,other,storage).save(P.create(data,other));
 const key=S.keyFor(data,learner);storage.setItem(key,'{invalid');
 const handle=S.open(data,learner,storage);assert.equal(handle.status,'corrupt');assert.equal(handle.save(P.create(data,learner)),'conflict');
 assert.equal(storage.getItem(key),'{invalid');assert.equal(handle.reset(),'reset');assert.equal(handle.save(P.create(data,learner)),'saved');
 assert.equal(S.open(data,other,storage).status,'found');
});
test('stale tab cannot overwrite or reset a newer persisted session',()=>{
 const storage=new MemoryStorage(),one=S.open(data,learner,storage),two=S.open(data,learner,storage);
 const state=P.create(data,learner);fill(state,data.questions[0]);P.check(data,state,'q1');assert.equal(one.save(state),'saved');
 assert.equal(two.save(P.create(data,learner)),'conflict');assert.equal(two.reset(),'conflict');
 assert.equal(P.summary(data,S.open(data,learner,storage).state).xp,10);
});
test('blocked and quota-exceeded storage return a recoverable status without altering in-memory progress',()=>{
 const blocked={getItem(){throw Error('denied');},setItem(){throw Error('quota');},removeItem(){throw Error('denied');}};
 const handle=S.open(data,learner,blocked),state=P.create(data,learner);fill(state,data.questions[0]);P.check(data,state,'q1');
 assert.equal(handle.status,'blocked');assert.equal(handle.save(state),'blocked');assert.equal(P.summary(data,state).xp,10);
});
test('a confirmed reset can recover a corrupt record after a temporary storage denial ends',()=>{
 const storage=new MemoryStorage(),key=S.keyFor(data,learner);storage.setItem(key,'{broken');
 const handle=S.open(data,learner,storage),remove=storage.removeItem;
 storage.removeItem=()=>{throw Error('temporary denial');};assert.equal(handle.reset(),'blocked');
 storage.removeItem=remove;
 assert.equal(handle.save(P.create(data,learner)),'saved');assert.equal(S.open(data,learner,storage).status,'found');
});

test('grade 8 remembers the complete identity/code without enumerating or changing progress',()=>{
 const storage=new MemoryStorage();const a=P.identity('  Cùng tên  ','8A-01'),b=P.identity('Cùng tên','8A-02');
 const state=P.create(data,a);fill(state,data.questions[0]);P.check(data,state,data.questions[0].id);const store=S.open(data,a,storage);store.save(state);const before=storage.getItem(store.key);
 assert.equal(S.profile(storage),null);assert.equal(S.remember(a,storage),true);assert.deepEqual(plain(S.profile(storage)),plain(a));
 S.remember(b,storage);assert.equal(S.profile(storage).key,b.key);assert.notEqual(a.key,b.key);assert.equal(storage.getItem(store.key),before);
 S.forget(storage);assert.equal(S.profile(storage),null);assert.equal(storage.getItem(store.key),before);
 storage.setItem(S.profileKey,'{broken');assert.equal(S.profile(storage),null);
 assert.equal(S.remember(a,{setItem(){throw Error('quota');}}),false);
 assert.equal(S.profile({getItem(){throw Error('blocked');}}),null);
});

test('pending choice answers need no invented key or transcript and never award XP',()=>{
 const pending=plain(data);pending.questions=pending.questions.slice(0,1);pending.questions[0].autoGrade=false;pending.questions[0].accepted=[];pending.tracks[0].transcriptHtml='';
 assert.equal(M.validate(pending),true);const state=P.create(pending,learner),q=pending.questions[0];
 P.update(pending,state,q.id,{...P.blank(q),value:q.options[0].value});P.check(pending,state,q.id);
 assert.equal(P.summary(pending,state).pending,1);assert.equal(P.summary(pending,state).xp,0);assert.equal(P.check(pending,state,q.id),false);
 P.setMode(pending,state,'ordered');const restored=P.restore(pending,learner,plain(state));assert.equal(P.summary(pending,restored).xp,0);
 P.beginReview(pending,restored);P.update(pending,restored,q.id,{...P.blank(q),value:q.options[0].value});P.check(pending,restored,q.id);assert.equal(P.summary(pending,restored).xp,0);
});
