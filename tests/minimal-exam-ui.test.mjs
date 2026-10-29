import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {execFileSync} from 'node:child_process';
import {minimalContexts} from '../grade-8/De_thi_GHK1/shared-practice/minimal-contexts.js';
const baseline='3691356',shared='grade-8/De_thi_GHK1/shared-practice/';
const inventory=JSON.parse(fs.readFileSync('docs/minimal-exam-ui/inventory.json','utf8'));
const ui=new Set([shared+'dual-mode-engine.js',shared+'engine.js',shared+'game.css',
 'grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-game/game.js',
 'grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-game/game.css',
 ...['minimal-ui.js','minimal-ui.css','practice-dual-mode.html'].map(f=>'grade-8/De_thi_GHK1/3_THCS Trung Dong/'+f)]);
const original=p=>execFileSync('git',['show',baseline+':'+p],{maxBuffer:20000000});
test('fresh inventory finds 53 existing game URLs and 2212 questions across all three runtime families',()=>{
 assert.equal(inventory.games,53);assert.equal(inventory.questions,2212);
 assert.deepEqual(inventory.engines,{'dual-mode-engine.js':49,'engine.js':3,'truc-tuan-game/game.js':1});
 for(const [grade,count] of [[6,16],[7,14],[8,23]])assert.equal(inventory.inventory.filter(g=>g.grade===grade).length,count);
 const launchers=execFileSync('git',['ls-tree','-rz','--name-only',baseline],{maxBuffer:2000000}).toString().split('\0').filter(p=>p.endsWith('-dual-mode.html')||p.endsWith('/practice-game-pilot.html')||p.endsWith('/truc-tuan-game-test.html'));
 assert.deepEqual(inventory.inventory.map(g=>g.game).sort(),launchers.sort());
});
test('all academic payloads/source HTML/audio/WAV, XP/storage models, index/catalog/Firebase stay byte-identical',()=>{
 const paths=execFileSync('git',['ls-tree','-rz','--name-only',baseline],{maxBuffer:2000000}).toString().split('\0').filter(Boolean);
 const protectedPaths=paths.filter(p=>!ui.has(p)&&(p.startsWith('grade-')||p.startsWith('assets/')||p.startsWith('catalog/')||['index.html','admin.html','firebase.json','firestore.rules','firestore.indexes.json','.firebaserc','package.json','package-lock.json'].includes(p)));
 for(const critical of ['index.html',shared+'dual-progress.js',shared+'dual-store.js',shared+'model.js',...inventory.inventory.map(g=>g.source)])assert(protectedPaths.includes(critical),critical);
 for(const path of protectedPaths)assert(fs.readFileSync(path).equals(original(path)),path);
});
test('the three controllers only add presentation loading; existing scoring/navigation/storage bodies are preserved',()=>{
 for(const path of [shared+'dual-mode-engine.js',shared+'engine.js','grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-game/game.js']){
  const now=fs.readFileSync(path,'utf8').replace('  const presentationScriptURL=document.currentScript.src;\n','').replace(/  \/\/ Presentation only; existing answer\/progress\/audio handlers remain owners\.[\s\S]*?\n\}\)\(\);\s*$/,'})();\n');
  assert.equal(now,original(path).toString(),path);
 }
 const adapter=fs.readFileSync(shared+'minimal-ui.js','utf8');
 assert(!/localStorage|\.setItem\(|\.removeItem\(|HTDualProgress|HTDualStore|\.play\(/.test(adapter));
 assert(fs.readFileSync(shared+'minimal-ui.css','utf8').includes('env(safe-area-inset-bottom'));
});
test('every source Reading question maps to one of two intact source passages; only exact labelled blanks are highlighted',()=>{
 assert.equal(Object.keys(minimalContexts).length,50);
 for(const row of inventory.inventory){
  const meta=minimalContexts[row.examId];assert(meta,row.game);assert.equal(meta.passages.length,2);assert.equal(Object.keys(meta.byQuestion).length,row.readingQuestions);
  for(const [id,index] of Object.entries(meta.byQuestion)){assert(Number.isInteger(index)&&index>=0&&index<2);assert(meta.passages[index].length>100);assert(row.readingEvidence[id]);}
  for(const [id,number] of Object.entries(meta.clozeMarkers)){assert(Number.isInteger(number)&&number>0);assert(id in meta.byQuestion);}
 }
 const state=vm.createContext({});vm.runInContext('globalThis.window={};'+fs.readFileSync('grade-6/De_thi_GHK_1/1_THCS_Truc_Cuong/practice-dual-data.js','utf8'),state);
 const meta=minimalContexts[state.window.HT_PRACTICE_DATA.exam.id];assert(meta.passages[meta.byQuestion.c1].includes('Volunteer Work'));assert(meta.passages[meta.byQuestion.rc1].includes('MIKE'));
});
