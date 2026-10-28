import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
const baseline='7ebbe8a',folder='grade-8/De_thi_GHK1/3_THCS Trung Dong/';
test('only one of 53 game launchers opts in; all 52 others and shared engine/data remain byte-identical to main',()=>{
 const paths=execFileSync('git',['ls-tree','-rz','--name-only',baseline],{maxBuffer:2000000}).toString().split('\0').filter(Boolean);
 const launchers=paths.filter(p=>p.endsWith('-dual-mode.html')||p.endsWith('/practice-game-pilot.html')||p.endsWith('/truc-tuan-game-test.html'));
 assert.equal(launchers.length,53);
 const protectedPaths=paths.filter(p=>p.startsWith('grade-')&&p!==folder+'practice-dual-mode.html'||p.startsWith('assets/')||p.startsWith('catalog/')||['index.html','admin.html','firebase.json','firestore.rules','firestore.indexes.json','.firebaserc'].includes(p));
 for(const p of protectedPaths)assert.equal(fs.readFileSync(p).equals(execFileSync('git',['show',baseline+':'+p],{maxBuffer:20000000})),true,p);
 for(const p of launchers)assert.equal(fs.readFileSync(p,'utf8').includes('data-minimal-ui="trung-dong-1"'),p===folder+'practice-dual-mode.html',p);
 const script=fs.readFileSync(folder+'minimal-ui.js','utf8');
 assert(!/localStorage|\.setItem\(|\.removeItem\(|HTDualProgress|HTDualStore/.test(script),'presentation adapter must not own progress/scoring');
 assert(script.includes('window.visualViewport'));assert(fs.readFileSync(folder+'minimal-ui.css','utf8').includes('env(safe-area-inset-bottom'));
});
