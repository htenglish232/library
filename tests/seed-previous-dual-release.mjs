// Isolated, old-release fixture; never accepts a production project or endpoint.
import {initializeTestEnvironment} from '@firebase/rules-unit-testing';
import {doc,setDoc,serverTimestamp} from 'firebase/firestore';
import {readFileSync} from 'node:fs';
import {managedPayload,encodeCatalogData} from '../assets/catalog-data.js';
import {RELEASE_IDS,DUAL_GAME_RELEASE_ID,DUAL_GAME_ADDITION} from '../assets/catalog-release.js';
if(process.env.FIRESTORE_EMULATOR_HOST!=='127.0.0.1:8080')throw Error('Local emulator required.');
const data=JSON.parse(readFileSync('catalog/current-library-catalog.json','utf8')).data;
const grade=data.find(g=>g.grade==='Grade 8');grade.grade='Khối 8';
const unit=grade.units.find(u=>u.name==='Đề thi GHK1');unit.name='Giữa kỳ';
const alreadyLinked=process.argv.includes('--already-linked');
unit.lessons=unit.lessons.filter(l=>(alreadyLinked||l.href!==DUAL_GAME_ADDITION.lesson.href)&&!l.href.endsWith('/truc-tuan-game-test.html'));
unit.lessons.find(l=>l.href.endsWith('/1. THCS Truc Tuan.html')).hidden=true;
const payload=await managedPayload(data);
const env=await initializeTestEnvironment({projectId:'demo-ht-english-library',firestore:{host:'127.0.0.1',port:8080}});
await env.withSecurityRulesDisabled(async context=>setDoc(doc(context.firestore(),'libraryCatalog','current'),{
 schemaVersion:2,revision:alreadyLinked?2000:1000,parentSha256:payload.sha256,count:payload.count,sha256:payload.sha256,
 dataJson:encodeCatalogData(data,RELEASE_IDS.filter(id=>id!==DUAL_GAME_RELEASE_ID)),updatedAt:serverTimestamp(),updatedBy:'4Y82k6RBaRUPflZriPsUvQv1qKj2'
}));
await env.cleanup();
console.log(JSON.stringify({count:payload.count}));
