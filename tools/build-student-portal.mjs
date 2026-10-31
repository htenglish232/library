import {readFile, writeFile, mkdir, cp, rm, readdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve, dirname, join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {build} from 'esbuild';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const dest=join(root,'student-portal/dist');
const school='grade-8/De_thi_GHK1/1_THCS Truc Tuan';
const shared='grade-8/De_thi_GHK1/shared-practice';
const launcher='truc-tuan-dual-mode.html';
export const pilotPath='/games/'+school+'/'+launcher;
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
export async function buildPortal(config) {
  const publicFields=['apiKey','projectId','authDomain','appId','storageBucket','messagingSenderId','measurementId'];
  if(!config || Object.keys(config).some(k=>!['emulator','firebase'].includes(k)) ||
      !config.firebase || Object.keys(config.firebase).some(k=>!publicFields.includes(k)))throw Error('Only public Firebase Web configuration is accepted');
  if(!config || !['ht-english-student-staging','demo-ht-student-portal'].includes(config.firebase?.projectId) ||
      (config.firebase.projectId.startsWith('demo-')&&!config.emulator) ||
      (config.firebase.projectId==='ht-english-student-staging'&&config.emulator))throw Error('Explicit staging config or --emulator required; production forbidden');
  if(!config.emulator && (!/^AIza[A-Za-z0-9_-]{30,}$/.test(config.firebase.apiKey) || !/^1:[0-9]+:web:[a-zA-Z0-9]+$/.test(config.firebase.appId) || config.firebase.authDomain!=='ht-english-student-staging.firebaseapp.com'))throw Error('Copy staging Web App configuration from its Console');
  await rm(dest,{recursive:true,force:true});
  await mkdir(dest,{recursive:true});
  await cp(join(root,'student-portal/index.html'),join(dest,'index.html'));
  await cp(join(root,'student-portal/assets'),join(dest,'assets'),{recursive:true});
  await cp(join(root,shared),join(dest,'games',shared),{recursive:true});
  await cp(join(root,'grade-7/De_thi_GHK_1/fonts'),join(dest,'games/grade-7/De_thi_GHK_1/fonts'),{recursive:true});
  await cp(join(root,'grade-7/De_thi_GHK_1/fonts'),join(dest,'fonts'),{recursive:true});
  const generated=join(root,'student-portal/functions/generated');
  await mkdir(generated,{recursive:true});
  for(const [from,to] of [[school+'/truc-tuan-dual-data.js','data.js'],[shared+'/model.js','model.js'],[shared+'/dual-progress.js','progress.js']]){
    await cp(join(root,from),join(generated,to));
  }
  const text=await readFile(join(root,school,'truc-tuan-dual-data.js'),'utf8');
  const data=JSON.parse(text.slice(text.indexOf('{')).trim().replace(/;\s*$/,''));
  await mkdir(join(dest,'games',school),{recursive:true});
  const files=['truc-tuan-dual-data.js','truc-tuan-dual-support.js',...data.tracks.map(t=>t.src)];
  for(const file of files)await cp(join(root,school,file),join(dest,'games',school,file));
  let html=await readFile(join(root,school,launcher),'utf8');
  html=html.replace('</head>','<link rel="stylesheet" href="/assets/pilot.css">\n</head>')
    .replace(/(<script defer src="[^"]*dual-store.js"[^>]*><\/script>)/,'$1\n<script defer src="/assets/pilot-adapter.js"></script>');
  if(!html.includes('/assets/pilot-adapter.js'))throw Error('Pilot adapter injection failed');
  await writeFile(join(dest,'games',school,launcher),html);
  await build({entryPoints:[join(root,'student-portal/assets/app.js')],outfile:join(dest,'assets/app.js'),bundle:true,format:'esm',target:['es2022'],minify:true,legalComments:'linked'});
  await writeFile(join(dest,'portal-config.json'),JSON.stringify({...config,gamePath:pilotPath})+'\n');
  const integrity={gameId:'grade8-truc-tuan',contentVersion:data.contentVersion,questions:data.questions.length,files:{}};
  for(const file of [...files.map(f=>school+'/'+f),shared+'/model.js',shared+'/dual-progress.js',shared+'/dual-mode-engine.js']){
    const original=await readFile(join(root,file)),packaged=await readFile(join(dest,'games',file));
    if(!original.equals(packaged))throw Error('Pilot source changed: '+file);
    integrity.files[file]=sha(original);
  }
  await writeFile(join(dest,'pilot-integrity.json'),JSON.stringify(integrity,null,2)+'\n');
  console.log('Portal artifact built: '+data.questions.length+' questions; original game, model and audio hashes preserved.');
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
  const flag=process.argv.indexOf('--config');
  const config=process.argv.includes('--emulator')?{emulator:true,firebase:{apiKey:'demo-api-key',projectId:'demo-ht-student-portal',authDomain:'localhost'}}:
    flag>=0?JSON.parse(await readFile(process.argv[flag+1],'utf8')):null;
  await buildPortal(config);
}
