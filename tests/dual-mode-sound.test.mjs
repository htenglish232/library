import {beforeSoundBootstrap,isDualLauncher} from './sound-bootstrap-contract.mjs';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createGameSound,SOUND_CUES,SOUND_PREFERENCE_KEY} from '../grade-8/De_thi_GHK1/shared-practice/dual-sound.js';
const click={isTrusted:true};
function rig({state='running',resume,storage,clock=()=>0,visible=()=>true}={}){
 const contexts=[],events=[];
 class Context{
  constructor(){this.state=state;this.currentTime=10;this.destination={};this.nodes=[];contexts.push(this);}
  resume(){events.push('resume');if(resume)return resume(this);this.state='running';return Promise.resolve();}
  createOscillator(){const node={type:'',frequency:{setValueAtTime(v,t){node.frequencyValue=v;node.at=t;}},connect(){},disconnect(){},start(t){node.startedAt=t;},stop(t){node.stoppedAt=t;},onended:null};this.nodes.push(node);return node;}
  createGain(){const values=[],gain={values,connect(){},disconnect(){}};gain.gain=Object.fromEntries(['setValueAtTime','linearRampToValueAtTime','setTargetAtTime','cancelScheduledValues'].map(k=>[k,(...args)=>values.push([k,...args])]));this.gains??=[];this.gains.push(gain);return gain;}
 }
 const sound=createGameSound({audioContextClass:()=>Context,storage:()=>storage||{getItem:()=>null,setItem(){}},now:clock,visible});
 return {sound,contexts,events};
}
test('loading/toggling, untrusted events and teacher-pending answers never unlock audio',async()=>{
 const {sound,contexts}=rig();assert.equal(contexts.length,0);
 sound.setEnabled(false);sound.setEnabled(true);assert.equal(contexts.length,0);
 for(const event of [undefined,{isTrusted:false}])assert.equal(await sound.playFeedback('correct',{event}),false);
 assert.equal(await sound.playFeedback('pending',{event:click}),false);assert.equal(contexts.length,0);
});
test('two ascending/descending sine notes have bounded gain and 0.5/0.4 second envelopes',async()=>{
 for(const [type,length,ascending] of [['correct',.5,true],['wrong',.4,false]]){
  const {sound,contexts}=rig();assert(await sound.playFeedback(type,{event:click}));const ctx=contexts[0];assert.equal(ctx.nodes.length,2);
  assert.equal(ctx.nodes[1].frequencyValue>ctx.nodes[0].frequencyValue,ascending);assert(ctx.nodes.every(n=>n.type==='sine'));
  assert(Math.abs(Math.max(...ctx.nodes.map(n=>n.stoppedAt))-ctx.nodes[0].startedAt-length-.01)<1e-9);
  for(const g of ctx.gains){assert(g.values.some(v=>v[0]==='linearRampToValueAtTime'&&v[1]===0));assert(g.values.every(v=>v[0]==='cancelScheduledValues'||v[1]<=.06));}
 }
});
test('completion is a separate 1.5-second phrase, after the answer or on a final pending question',async()=>{
 for(const result of ['correct','wrong','pending']){
  const {sound,contexts}=rig();assert(await sound.playFeedback(result,{event:click,completed:true}));const nodes=contexts[0].nodes;const last=nodes.slice(-5);
  assert.equal(nodes.length,result==='pending'?5:7);assert(Math.abs(Math.max(...last.map(n=>n.stoppedAt))-last[0].startedAt-1.51)<1e-9);
  if(result!=='pending')assert(last[0].startedAt>nodes[1].stoppedAt);
 }
 assert.equal(SOUND_CUES.complete.length,5);
});
test('resume is requested within the gesture, context is reused, and a later cue stops old nodes',async()=>{
 const {sound,contexts,events}=rig({state:'suspended'});const promise=sound.playFeedback('correct',{event:click});assert.deepEqual(events,['resume']);assert(await promise);
 const previous=contexts[0].nodes.slice();assert(await sound.playFeedback('wrong',{event:click}));assert.equal(contexts.length,1);assert(previous.every(n=>n.stoppedAt===10.02));
});
test('mute persists only its own key and a reloaded instance respects it; blocked storage stays playable',async()=>{
 const records=new Map([['htenglish:practice:v1:existing','unchanged']]);const storage={getItem:k=>records.get(k)??null,setItem:(k,v)=>records.set(k,v)};
 const a=rig({storage});a.sound.setEnabled(false);assert.equal(records.get(SOUND_PREFERENCE_KEY),'off');assert.equal(await a.sound.playFeedback('correct',{event:click}),false);assert.equal(a.contexts.length,0);
 const b=rig({storage});assert.equal(b.sound.enabled,false);b.sound.setEnabled(true);assert.equal(records.get(SOUND_PREFERENCE_KEY),'on');assert.equal(records.get('htenglish:practice:v1:existing'),'unchanged');
 const blocked=rig({storage:{getItem(){throw Error('denied');},setItem(){throw Error('quota');}}});blocked.sound.setEnabled(false);blocked.sound.setEnabled(true);assert(await blocked.sound.playFeedback('correct',{event:click}));
});
test('muting/background/slow resume cancel pending audio without a late surprise',async()=>{
 for(const reason of ['mute','background','slow','newer']){
  let resolve,t=0,visible=true;const {sound,contexts}=rig({state:'interrupted',clock:()=>t,visible:()=>visible,resume:ctx=>new Promise(r=>{resolve=()=>{ctx.state='running';r();};})});
  const play=sound.playFeedback('correct',{event:click});assert.equal(contexts[0].nodes.length,0);
  if(reason==='mute')sound.setEnabled(false);
  if(reason==='background')visible=false;
  if(reason==='slow')t=501;
  if(reason==='newer')sound.stop();
  resolve();assert.equal(await play,false);assert.equal(contexts[0].nodes.length,0,reason);
 }
});
test('unavailable context, construction/resume failure and background calls never reject grading',async()=>{
 const unsupported=createGameSound({audioContextClass:()=>null});assert.equal(unsupported.supported,false);assert.equal(await unsupported.playFeedback('correct',{event:click}),false);
 const broken=createGameSound({audioContextClass:()=>class {constructor(){throw Error('device');}}});assert.equal(await broken.playFeedback('correct',{event:click}),false);
 const denied=rig({state:'suspended',resume:()=>Promise.reject(Error('autoplay denied'))});assert.equal(await denied.sound.playFeedback('correct',{event:click}),false);
 const hidden=rig({visible:()=>false});assert.equal(await hidden.sound.playFeedback('correct',{event:click}),false);assert.equal(hidden.contexts.length,0);
});
test('Listening uses lower effect gain; muting does not create or close audio devices',async()=>{
 const {sound,contexts}=rig();assert(await sound.playFeedback('correct',{event:click,listeningActive:true}));const ctx=contexts[0];assert(ctx.gains.every(g=>g.values.some(v=>v[0]==='linearRampToValueAtTime'&&v[1]===.025)));
 sound.setEnabled(false);assert(ctx.nodes.every(n=>n.stoppedAt===10.02));assert.equal(contexts.length,1);
});

test('index, legacy catalog, all source/data/answers/XP/storage/Firebase files match merged main; game HTML permits only the sound button and asset versions',async()=>{
 const {execFileSync}=await import('node:child_process');
 const paths=execFileSync('git',['ls-tree','-rz','--name-only','b38d578']).toString().split('\0').filter(Boolean);
 const mutable=new Set(['dual-mode-engine.js','dual-mode.css'].map(f=>'grade-8/De_thi_GHK1/shared-practice/'+f));
 // Grade 6 adds a release batch; its exact catalog delta is checked in grade6-dual.test.mjs.
 mutable.add('assets/catalog-release.js');
 const games=paths.filter(isDualLauncher);
 const {readFileSync}=await import('node:fs');
 for(const file of games)assert.equal(beforeSoundBootstrap(readFileSync(file,'utf8')),execFileSync('git',['show','b38d578:'+file],{encoding:'utf8'}),file);
 const protectedPaths=paths.filter(p=>!mutable.has(p)&&!games.includes(p)&&(p.startsWith('grade-')||p.startsWith('assets/')||(p.startsWith('catalog/')&&p!=='catalog/current-library-catalog.json')||['index.html','admin.html','firestore.rules','firestore.indexes.json','firebase.json','.firebaserc'].includes(p)));
 assert(protectedPaths.length>=379);
 assert.equal(execFileSync('git',['diff','b38d578','--name-only','--',...protectedPaths],{maxBuffer:1000000}).toString(),'');
});

test('legacy webkitAudioContext fallback remains lazy and works from a trusted check',async()=>{
 const rigged=rig();await rigged.sound.playFeedback('correct',{event:click});
 const Native=rigged.contexts[0].constructor,keys=['AudioContext','webkitAudioContext'];
 const descriptors=keys.map(k=>Object.getOwnPropertyDescriptor(globalThis,k));
 try {
  globalThis.AudioContext=undefined;globalThis.webkitAudioContext=Native;
  const sound=createGameSound();assert(sound.supported);assert.equal(rigged.contexts.length,1);
  assert(await sound.playFeedback('correct',{event:click}));assert.equal(rigged.contexts.length,2);
 } finally {keys.forEach((k,i)=>descriptors[i]?Object.defineProperty(globalThis,k,descriptors[i]):delete globalThis[k]);}
});
