import { before, after, beforeEach, test } from 'node:test';
import { readFileSync } from 'node:fs';
import { initializeTestEnvironment, assertSucceeds, assertFails } from '@firebase/rules-unit-testing';
import { doc, collection, getDoc, getDocs, setDoc, deleteDoc, serverTimestamp } from 'firebase/firestore';
const adminUid='4Y82k6RBaRUPflZriPsUvQv1qKj2';
let env;
const database = uid => uid ? env.authenticatedContext(uid).firestore() : env.unauthenticatedContext().firestore();
const member = status => ({ email:'teacher@example.test', name:'Teacher', status, updatedAt:serverTimestamp() });
const catalog = () => ({schemaVersion:1,count:201,sha256:'a'.repeat(64),dataJson:'[]',updatedAt:serverTimestamp()});
before(async()=>{ env=await initializeTestEnvironment({ projectId:'demo-ht-english-library', firestore:{host:'127.0.0.1',port:8080,rules:readFileSync('firestore.rules','utf8')} }); });
beforeEach(async()=>{
  await env.clearFirestore();
  await env.withSecurityRulesDisabled(async context=>{
    const db=context.firestore();
    await setDoc(doc(db,'libraryMembers','teacher'),member('active'));
    await setDoc(doc(db,'libraryCatalog','current'),catalog());
  });
});
after(async()=>{ await env.cleanup(); });
test('anonymous users cannot read catalog or memberships',async()=>{
  const db=database(); await assertFails(getDoc(doc(db,'libraryCatalog','current'))); await assertFails(getDoc(doc(db,'libraryMembers','teacher')));
});
test('unapproved teacher cannot read catalog',async()=>{await assertFails(getDoc(doc(database('unapproved'),'libraryCatalog','current')));});
test('active teacher reads catalog and own permission only',async()=>{
  const db=database('teacher'); await assertSucceeds(getDoc(doc(db,'libraryCatalog','current'))); await assertSucceeds(getDoc(doc(db,'libraryMembers','teacher')));
  await assertFails(getDoc(doc(db,'libraryMembers','other'))); await assertFails(getDocs(collection(db,'libraryMembers'))); await assertFails(getDocs(collection(db,'libraryCatalog')));
});
test('locked and revoked teachers cannot read catalog, even with existing identity',async()=>{
  const teacher=database('teacher');
  await assertSucceeds(getDoc(doc(teacher,'libraryCatalog','current')));
  for(const status of ['locked','revoked']) {
    await setDoc(doc(database(adminUid),'libraryMembers','teacher'),member(status));
    await assertFails(getDoc(doc(teacher,'libraryCatalog','current')));
  }
});
test('teacher cannot self-grant, unlock, revoke others or change catalog',async()=>{
  const db=database('teacher');
  await assertFails(setDoc(doc(db,'libraryMembers','teacher'),member('active')));
  await assertFails(setDoc(doc(db,'libraryMembers','other'),member('active')));
  await assertFails(setDoc(doc(db,'libraryCatalog','current'),catalog()));
  await assertFails(deleteDoc(doc(db,'libraryMembers','teacher')));
});
test('email or fake admin role cannot elevate a teacher',async()=>{
  const db=env.authenticatedContext('teacher',{email:'admin@example.test',admin:true}).firestore();
  await assertFails(setDoc(doc(db,'libraryMembers','other'),member('active')));
  await assertFails(setDoc(doc(database('unapproved'),'libraryMembers','unapproved'),{...member('active'),role:'admin'}));
});
test('fixed admin can grant, lock, unlock, revoke and import',async()=>{
  const db=database(adminUid); await assertSucceeds(getDoc(doc(db,'libraryCatalog','current'))); await assertSucceeds(getDocs(collection(db,'libraryMembers')));
  for(const status of ['active','locked','active','revoked']) await assertSucceeds(setDoc(doc(db,'libraryMembers','other'),member(status)));
  await assertSucceeds(setDoc(doc(db,'libraryCatalog','current'),catalog()));
});
test('admin cannot create a second admin via membership or edit primary admin',async()=>{
  const db=database(adminUid);
  await assertFails(setDoc(doc(db,'libraryMembers','other'),{...member('active'),role:'admin'}));
  await assertFails(setDoc(doc(db,'libraryMembers',adminUid),member('locked')));
});
test('member schema rejects invalid status, extra fields and forged timestamp',async()=>{
  const target=doc(database(adminUid),'libraryMembers','other');
  await assertFails(setDoc(target,member('pending')));
  await assertFails(setDoc(target,{...member('active'),password:'never-store-passwords'}));
  await assertFails(setDoc(target,{...member('active'),updatedAt:new Date(0)}));
});
test('catalog schema rejects wrong count, extra fields and unknown collections',async()=>{
  const db=database(adminUid); const target=doc(db,'libraryCatalog','current');
  await assertFails(setDoc(target,{...catalog(),count:200}));
  await assertFails(setDoc(target,{...catalog(),unexpected:true}));
  await assertFails(setDoc(doc(db,'libraryCatalog','other'),catalog()));
  await assertFails(setDoc(doc(db,'unrelated','data'),{value:true}));
});
test('unapproved, locked and revoked teachers cannot self-grant or write an admin role',async()=>{
  await assertFails(setDoc(doc(database('unapproved'),'libraryMembers','unapproved'),member('active')));
  for(const status of ['locked','revoked']) {
    await setDoc(doc(database(adminUid),'libraryMembers','teacher'),member(status));
    await assertFails(setDoc(doc(database('teacher'),'libraryMembers','teacher'),member('active')));
    await assertFails(setDoc(doc(database('teacher'),'libraryMembers','teacher'),{...member('active'),role:'admin'}));
  }
});
test('catalog and membership subcollections stay denied; no unrelated collection is opened',async()=>{
  for(const uid of [adminUid,'teacher','unapproved']) {
    await assertFails(getDoc(doc(database(uid),'libraryCatalog','current','private','data')));
    await assertFails(setDoc(doc(database(uid),'libraryMembers','teacher','roles','admin'),{admin:true}));
  }
});
