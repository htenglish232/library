// Emulator-only fixture initialization. Never accepts a production project.
import { initializeTestEnvironment } from '@firebase/rules-unit-testing';
import { readFileSync } from 'node:fs';
import { doc, setDoc, serverTimestamp } from 'firebase/firestore';
if (process.env.FIRESTORE_EMULATOR_HOST !== '127.0.0.1:8080') throw new Error('Local emulator is required.');
let input=''; for await (const chunk of process.stdin) input += chunk;
const users=JSON.parse(input);
const env=await initializeTestEnvironment({projectId:'demo-ht-english-library',firestore:{host:'127.0.0.1',port:8080}});
await env.clearFirestore();
const payload=JSON.parse(readFileSync('catalog/library-catalog.json','utf8'));
await env.withSecurityRulesDisabled(async context=>{
  const db=context.firestore();
  await setDoc(doc(db,'libraryCatalog','current'),{schemaVersion:1,count:201,sha256:payload.sha256,dataJson:JSON.stringify(payload.data),updatedAt:serverTimestamp()});
  for(const user of users) if(user.status) await setDoc(doc(db,'libraryMembers',user.uid),{email:user.email,name:user.label,status:user.status,updatedAt:serverTimestamp()});
});
await env.cleanup();
