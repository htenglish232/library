// Test fixture reset only. No production credentials or projects are accepted.
import { initializeTestEnvironment } from '@firebase/rules-unit-testing';
import { doc, deleteDoc, getDocFromServer } from 'firebase/firestore';
if (process.env.FIRESTORE_EMULATOR_HOST !== '127.0.0.1:8080') throw new Error('Local emulator required.');
const env=await initializeTestEnvironment({projectId:'demo-ht-english-library',firestore:{host:'127.0.0.1',port:8080}});
await env.withSecurityRulesDisabled(async context=>{
  const target=doc(context.firestore(),'libraryCatalog','current');
  await deleteDoc(target);
  if ((await getDocFromServer(target)).exists()) throw new Error('Emulator fixture reset failed.');
});
await env.cleanup();
