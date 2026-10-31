import {before,after,test} from 'node:test';
import assert from 'node:assert/strict';
import {randomUUID} from 'node:crypto';
import {createRequire} from 'node:module';
import {readFile,writeFile} from 'node:fs/promises';
import {initializeTestEnvironment,assertFails,assertSucceeds} from '@firebase/rules-unit-testing';
import {doc,getDoc,getDocs,collection,setDoc,writeBatch} from 'firebase/firestore';
import {createService} from '../functions/src/service.js';
import {provisionStudents,assignDemo,demoStudents,DEMO_ASSIGNMENT} from '../functions/src/provision.js';
import {data} from '../functions/src/grading.js';
import {correctAnswers} from './fixtures.mjs';
const require=createRequire(new URL('../functions/package.json',import.meta.url));
const {initializeApp,deleteApp}=require('firebase-admin/app');
const {getAuth}=require('firebase-admin/auth');
const {getFirestore,Timestamp}=require('firebase-admin/firestore');
const projectId='demo-ht-student-portal', uid='portal-ht0001', uidB='portal-ht0002';
let admin,db,auth,env,tokens,credentials;
const service=()=>createService(db,{enabled:()=>true});
const url='http://127.0.0.1:5000/api/';
async function call(path,token,body){
  const r=await fetch(url+path,{method:body?'POST':'GET',headers:{...(token?{Authorization:'Bearer '+token}:{}),...(body?{'Content-Type':'application/json'}:{})},body:body?JSON.stringify(body):undefined});
  return {status:r.status,data:await r.json()};
}
async function login(studentId,password){
  const r=await fetch('http://127.0.0.1:9099/identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=demo-api-key',{
    method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:studentId.toLowerCase()+'@students.htenglish.invalid',password,returnSecureToken:true})});
  return {status:r.status,data:await r.json()};
}
async function start(id=uid){return service().start(id,{assignmentId:DEMO_ASSIGNMENT,attemptId:randomUUID()});}
before(async()=>{
  assert.equal(process.env.FIRESTORE_EMULATOR_HOST,'127.0.0.1:8080');
  assert.equal(process.env.FIREBASE_AUTH_EMULATOR_HOST,'127.0.0.1:9099');
  admin=initializeApp({projectId});auth=getAuth(admin);db=getFirestore(admin);
  env=await initializeTestEnvironment({projectId,firestore:{host:'127.0.0.1',port:8080,rules:await readFile('student-portal/firestore.rules','utf8')}});
  await env.clearFirestore();
  credentials=await provisionStudents(auth,db,demoStudents);await assignDemo(db);
  tokens={};for(const c of credentials){const r=await login(c.studentId,c.password);assert.equal(r.status,200);tokens[c.studentId]=r.data.idToken;}
  await writeFile(process.env.PORTAL_TEST_CREDENTIALS,JSON.stringify(credentials),{mode:0o600,flag:'wx'});
});
after(async()=>{await env?.cleanup();await deleteApp(admin);});
test('Auth Emulator and deployed Functions handler reject anonymous, invalid password and forged tokens',async()=>{
  assert.equal((await call('dashboard')).status,401);
  assert.equal((await call('dashboard','forged')).status,401);
  assert.equal((await login('HT0001','incorrect-password')).status,400);
  const dashboard=await call('dashboard',tokens.HT0001);assert.equal(dashboard.status,200);
  assert.equal(dashboard.data.student.studentId,'HT0001');assert.equal(dashboard.data.assignments[0].id,DEMO_ASSIGNMENT);
  assert.equal((await call('teacher/report?classId=grade8-demo',tokens.HT0001)).status,403);
});
test('Firestore ownership, queries, status and immutable score/stars survive malicious batch/merge writes',async()=>{
  const a=env.authenticatedContext(uid).firestore(),b=env.authenticatedContext(uidB).firestore();
  const anon=env.unauthenticatedContext().firestore();
  await assertSucceeds(getDoc(doc(a,'students',uid)));
  await assertSucceeds(getDocs(collection(a,'students',uid,'attempts')));
  await assertFails(getDoc(doc(a,'students',uidB)));
  await assertFails(getDocs(collection(a,'students')));
  await assertFails(getDoc(doc(anon,'students',uid)));
  await assertFails(getDoc(doc(env.authenticatedContext('unprovisioned').firestore(),'students',uid)));
  for(const payload of [{stars:99999},{role:'admin'},{classId:'other'},{status:'active'}])await assertFails(setDoc(doc(a,'students',uid),payload,{merge:true}));
  for(const sub of ['attempts','starTransactions','studentRewards','assignments'])await assertFails(setDoc(doc(a,'students',uid,sub,'fake'),{score:10,delta:999}));
  const batch=writeBatch(b);batch.set(doc(b,'students',uidB),{stars:999},{merge:true});batch.set(doc(b,'students',uid,'attempts','fake'),{score:10});await assertFails(batch.commit());
  await db.doc('portalPrincipals/'+uid).update({status:'locked'});
  await assertFails(getDoc(doc(a,'students',uid)));assert.equal((await call('dashboard',tokens.HT0001)).status,403);
  await db.doc('portalPrincipals/'+uid).update({status:'active'});
});
test('backend refuses cross-account attempts, arbitrary assignments, forged scores and expired/exam tasks',async()=>{
  const attempt=await start();
  assert.equal((await call('attempts/submit',tokens.HT0002,{attemptId:attempt.attemptId,contentVersion:data.contentVersion,answers:correctAnswers()})).status,404);
  assert.equal((await call('attempts/submit',tokens.HT0001,{attemptId:attempt.attemptId,contentVersion:data.contentVersion,answers:correctAnswers(),score:10})).status,400);
  assert.equal((await call('attempts/start',tokens.HT0001,{attemptId:randomUUID(),assignmentId:'https://evil.test'})).status,400);
  const ref=db.doc('assignments/'+DEMO_ASSIGNMENT);
  await ref.update({mode:'exam'});await assert.rejects(start(),/assignment-unavailable/);
  await ref.update({mode:'practice',dueAt:Timestamp.fromMillis(Date.now()-1000)});await assert.rejects(start(),/assignment-unavailable/);
  await ref.update({dueAt:Timestamp.fromMillis(Date.now()+86400000)});
  await db.doc('students/'+uid+'/assignments/'+DEMO_ASSIGNMENT).update({status:'revoked'});
  await assert.rejects(start(),/assignment-unavailable/);
  await db.doc('students/'+uid+'/assignments/'+DEMO_ASSIGNMENT).update({status:'active'});
  await assert.rejects(createService(db,{enabled:()=>false}).start(uid,{assignmentId:DEMO_ASSIGNMENT,attemptId:randomUUID()}),/portal-paused/);
});
test('parallel duplicate submits and retry after lost response grant exactly one ledger reward',async()=>{
  const attempt=await start();
  const body={attemptId:attempt.attemptId,contentVersion:data.contentVersion,answers:correctAnswers()};
  const results=await Promise.all(Array.from({length:5},()=>call('attempts/submit',tokens.HT0001,body)));
  results.forEach(r=>{assert.equal(r.status,200);assert.equal(r.data.result.correct,42);assert.equal(r.data.official,false);});
  assert(results.every(r=>JSON.stringify(r.data)===JSON.stringify(results[0].data)));
  assert.equal((await db.doc('students/'+uid).get()).data().stars,5);
  assert.equal((await db.collection('students/'+uid+'/starTransactions').get()).size,1);
  // Treat the first response as lost: retrying the same committed request is safe.
  const retry=await call('attempts/submit',tokens.HT0001,body);assert.deepEqual(retry.data,results[0].data);
  const record=(await db.doc('students/'+uid+'/attempts/'+attempt.attemptId).get()).data();
  assert(record.startedAt instanceof Timestamp);assert(record.submittedAt instanceof Timestamp);assert(record.elapsedSeconds>=0);
  const modified=correctAnswers();modified.q1.value='A';
  assert.equal((await call('attempts/submit',tokens.HT0001,{...body,answers:modified})).status,409);
  assert.equal((await db.doc('students/'+uid).get()).data().stars,5);
});
test('retakes keep separate history but do not farm stars; incomplete submissions do not earn rewards',async()=>{
  const retake=await start();
  const receipt=await service().submit(uid,{attemptId:retake.attemptId,contentVersion:data.contentVersion,answers:correctAnswers()});
  assert.equal(receipt.starsAwarded,0);
  const incomplete=correctAnswers();incomplete.q1.value='';
  const b=await start(uidB);
  const partial=await service().submit(uidB,{attemptId:b.attemptId,contentVersion:data.contentVersion,answers:incomplete});
  assert.equal(partial.result.unanswered,1);assert.equal(partial.starsAwarded,0);
  const history=await call('dashboard',tokens.HT0001);assert(history.data.history.filter(a=>a.status==='submitted').length>=2);
});
test('provision retry never resets passwords or erases rewards; teacher scopes enforced by backend',async()=>{
  const repeat=await provisionStudents(auth,db,demoStudents);assert.equal(repeat.length,0);
  assert.equal((await login('HT0001',credentials[0].password)).status,200);
  assert.equal((await db.doc('students/'+uid).get()).data().stars,5);
  await db.doc('portalPrincipals/teacher-demo').set({role:'teacher',status:'active'});
  await db.doc('portalTeachers/teacher-demo/classes/grade8-demo').set({status:'active'});
  assert.equal((await service().teacherReport('teacher-demo','grade8-demo')).students.length,3);
  await assert.rejects(service().teacherReport('teacher-demo','another-class'),/teacher-access-denied/);
  await assert.rejects(service().teacherReport(uid,'grade8-demo'),/teacher-access-denied/);
});
test('concurrent attempts cannot exceed the limit or double-award across different attempts',async()=>{
  const row={studentId:'HT0099',displayName:'Emulator Race Test',classId:'grade8-demo'};
  await provisionStudents(auth,db,[row]);await assignDemo(db,[row]);
  const id='portal-ht0099',attempts=[];
  for(let i=0;i<19;i++)attempts.push(await start(id));
  const race=await Promise.allSettled([start(id),start(id)]);
  assert.equal(race.filter(r=>r.status==='fulfilled').length,1);
  assert.match(race.find(r=>r.status==='rejected').reason.message,/attempt-limit/);
  const receipts=await Promise.all(attempts.slice(0,2).map(a=>service().submit(id,{
    attemptId:a.attemptId,contentVersion:data.contentVersion,answers:correctAnswers()})));
  assert.equal(receipts.reduce((n,r)=>n+r.starsAwarded,0),5);
  assert.equal((await db.collection('students/'+id+'/starTransactions').get()).size,1);
  assert.equal((await db.doc('students/'+id).get()).data().stars,5);
});
test('a disabled Auth account is rejected even with a previously issued token',async()=>{
  await auth.updateUser(uidB,{disabled:true});
  try{assert.equal((await call('dashboard',tokens.HT0002)).status,401);}
  finally{await auth.updateUser(uidB,{disabled:false});}
});
