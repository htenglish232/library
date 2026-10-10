import { before, after, beforeEach, test } from 'node:test';
import { readFileSync } from 'node:fs';
import { initializeTestEnvironment, assertSucceeds, assertFails } from '@firebase/rules-unit-testing';
import { doc, collection, getDoc, getDocs, setDoc, deleteDoc, serverTimestamp, writeBatch } from 'firebase/firestore';
const adminUid='4Y82k6RBaRUPflZriPsUvQv1qKj2';
let env;
const database = uid => uid ? env.authenticatedContext(uid).firestore() : env.unauthenticatedContext().firestore();
const member = status => ({ email:'teacher@example.test', name:'Teacher', status, updatedAt:serverTimestamp() });
const original = JSON.parse(readFileSync('catalog/library-catalog.json','utf8'));
const catalog = () => ({schemaVersion:1,count:201,sha256:original.sha256,dataJson:JSON.stringify(original.data),updatedAt:serverTimestamp()});
async function updateCatalog(db, options = {}) {
  const target = doc(db,'libraryCatalog','current');
  const previous = (await getDoc(target)).data();
  const revision = previous.schemaVersion === 1 ? 0 : previous.revision;
  const fields = {schemaVersion:2,revision:revision+1,parentSha256:previous.sha256,count:202,sha256:'b'.repeat(64),dataJson:'[]',updatedAt:serverTimestamp(),updatedBy:adminUid,...options.fields};
  const batch = writeBatch(db); batch.set(target, fields);
  if (!options.noArchive) batch.set(doc(db,'libraryCatalogHistory',options.archiveId ?? String(revision)), {
    revision,snapshot:previous,archivedAt:serverTimestamp(),archivedBy:adminUid,...options.archive
  });
  return batch.commit();
}
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
test('fixed admin can grant, lock, unlock, revoke and create the first catalog',async()=>{
  const db=database(adminUid); await assertSucceeds(getDoc(doc(db,'libraryCatalog','current'))); await assertSucceeds(getDocs(collection(db,'libraryMembers')));
  for(const status of ['active','locked','active','revoked']) await assertSucceeds(setDoc(doc(db,'libraryMembers','other'),member(status)));
  await env.withSecurityRulesDisabled(context=>deleteDoc(doc(context.firestore(),'libraryCatalog','current')));
  await assertSucceeds(setDoc(doc(db,'libraryCatalog','current'),catalog()));
});
test('admin cannot overwrite without archive, merge-update or delete existing catalog',async()=>{
  const target=doc(database(adminUid),'libraryCatalog','current');
  await assertFails(setDoc(target,catalog()));
  await assertFails(setDoc(target,{count:201},{merge:true}));
  await assertFails(deleteDoc(target));
});
test('admin migrates v1 atomically, preserves exact snapshot and saves more than 201 items',async()=>{
  const db=database(adminUid), previous=(await getDoc(doc(db,'libraryCatalog','current'))).data();
  await assertSucceeds(updateCatalog(db));
  const saved=(await getDoc(doc(db,'libraryCatalog','current'))).data();
  const archive=(await getDoc(doc(db,'libraryCatalogHistory','0'))).data();
  if(saved.schemaVersion!==2 || saved.revision!==1 || saved.count!==202 || !archive.snapshot.updatedAt.isEqual(previous.updatedAt) || archive.snapshot.dataJson!==previous.dataJson) throw new Error('Migration changed original snapshot.');
  await assertSucceeds(updateCatalog(db,{fields:{count:0,sha256:'c'.repeat(64)}}));
  await assertSucceeds(getDocs(collection(db,'libraryCatalogHistory')));
});
test('rules require mandatory exact archive and correct next revision and parent hash',async()=>{
  const db=database(adminUid);
  for(const options of [
    {noArchive:true}, {archiveId:'wrong'}, {archive:{snapshot:{}}},
    {fields:{revision:2}}, {fields:{parentSha256:'f'.repeat(64)}},
    {fields:{count:-1}}, {fields:{count:1.5}}, {fields:{schemaVersion:1}},
    {fields:{updatedBy:'teacher'}}, {fields:{unexpected:true}},
    {fields:{updatedAt:new Date(0)}}, {archive:{archivedBy:'teacher'}},
    {archive:{archivedAt:new Date(0)}}, {archive:{unexpected:true}},
    {fields:{dataJson:'a'.repeat(700001)}}
  ]) await assertFails(updateCatalog(db,options));
});
test('stale batch revision cannot overwrite a newer save and immutable archive cannot be changed',async()=>{
  const db=database(adminUid), target=doc(db,'libraryCatalog','current');
  const previous=(await getDoc(target)).data();
  await assertSucceeds(updateCatalog(db));
  const batch=writeBatch(db);
  batch.set(target,{schemaVersion:2,revision:1,parentSha256:previous.sha256,count:0,sha256:'c'.repeat(64),dataJson:'[]',updatedAt:serverTimestamp(),updatedBy:adminUid});
  batch.set(doc(db,'libraryCatalogHistory','0'),{revision:0,snapshot:previous,archivedAt:serverTimestamp(),archivedBy:adminUid});
  await assertFails(batch.commit());
  await assertFails(setDoc(doc(db,'libraryCatalogHistory','0'),{revision:0,snapshot:previous,archivedAt:serverTimestamp(),archivedBy:adminUid}));
  await assertFails(deleteDoc(doc(db,'libraryCatalogHistory','0')));
  const saved=(await getDoc(target)).data(); if(saved.count!==202) throw new Error('Stale save altered catalog.');
});
test('standalone or fake future archive cannot be created',async()=>{
  const db=database(adminUid), previous=(await getDoc(doc(db,'libraryCatalog','current'))).data();
  for(const id of ['0','1','999']) await assertFails(setDoc(doc(db,'libraryCatalogHistory',id),{revision:0,snapshot:previous,archivedAt:serverTimestamp(),archivedBy:adminUid}));
});
test('teachers cannot read archives or update a managed catalog with forged archive',async()=>{
  await assertSucceeds(updateCatalog(database(adminUid)));
  for(const uid of [undefined,'teacher','unapproved','locked-teacher']) {
    const db=database(uid);
    await assertFails(getDoc(doc(db,'libraryCatalogHistory','0')));
    await assertFails(getDocs(collection(db,'libraryCatalogHistory')));
    await assertFails(setDoc(doc(db,'libraryCatalogHistory','1'),{revision:1}));
  }
  await assertFails(updateCatalog(database('teacher')));
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
  await env.withSecurityRulesDisabled(context=>deleteDoc(doc(context.firestore(),'libraryCatalog','current')));
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
