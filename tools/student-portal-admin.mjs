import {readFile,realpath} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {randomBytes,createCipheriv,publicEncrypt,constants} from 'node:crypto';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
const require=createRequire(new URL('../student-portal/functions/package.json',import.meta.url));
const {initializeApp,applicationDefault}=require('firebase-admin/app');
const {getAuth}=require('firebase-admin/auth');
const {getFirestore}=require('firebase-admin/firestore');
const {provisionStudents,assignDemo,demoStudents,validateRows}=await import('../student-portal/functions/src/provision.js');
const arg=name=>{const i=process.argv.indexOf(name);return i<0?null:process.argv[i+1];};
const project=arg('--project');
if(project!=='ht-english-student-staging')throw Error('Only explicit ht-english-student-staging is allowed; production is forbidden');
if(process.env.FIRESTORE_EMULATOR_HOST||process.env.FIREBASE_AUTH_EMULATOR_HOST)throw Error('Use the Emulator test runner for local demo accounts');
// CSV exported from Excel, with strict header and support for quoted newlines/commas.
function csv(text){
  const rows=[];let row=[],field='',quoted=false;
  text=text.replace(/^\uFEFF/,'');
  for(let i=0;i<text.length;i++){
    const c=text[i];
    if(c==='"'){if(quoted&&text[i+1]==='"'){field+='"';i++;}else if(!quoted&&field)throw Error('Invalid CSV quoting');else quoted=!quoted;}
    else if(!quoted&&(c===','||c==='\n')){row.push(field.replace(/\r$/,''));field='';if(c==='\n'){rows.push(row);row=[];}}
    else field+=c;
  }
  if(quoted)throw Error('Unclosed CSV field');
  if(field||row.length){row.push(field.replace(/\r$/,''));rows.push(row);}
  const header=rows.shift();if(header?.join(',')!=='studentId,displayName,classId')throw Error('CSV header must be studentId,displayName,classId');
  return rows.filter(r=>r.some(Boolean)).map(r=>{if(r.length!==3)throw Error('Invalid CSV columns');return Object.fromEntries(header.map((key,i)=>[key,r[i].trim()]));});
}
const rows=arg('--csv')?csv(await readFile(arg('--csv'),'utf8')):demoStudents;
validateRows(rows);
if(!process.argv.includes('--apply')){
  console.log('Dry-run validated '+rows.length+' rows. No Firebase connection or account creation performed.');
}else{
  if(!process.argv.includes('--confirmed-staging')||!arg('--recipient-public-key')||!arg('--out'))throw Error('Apply requires --confirmed-staging, --recipient-public-key and --out for encrypted delivery');
  const out=resolve(arg('--out'));
  const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
  const actual=resolve(await realpath(dirname(out)),out.split('/').pop());
  if(actual===root||actual.startsWith(root+'/'))throw Error('Credential delivery must be outside the checkout');
  const publicKey=await readFile(arg('--recipient-public-key'),'utf8');
  // Verify the recipient key and exclusive destination before any Auth mutation.
  const key=randomBytes(32);
  const wrappedKey=publicEncrypt({key:publicKey,oaepHash:'sha256',padding:constants.RSA_PKCS1_OAEP_PADDING},key).toString('base64');
  const handle=await import('node:fs/promises').then(fs=>fs.open(out,'wx',0o600));
  try{
    async function deliver(credentials){
      const iv=randomBytes(12),cipher=createCipheriv('aes-256-gcm',key,iv);
      const encrypted=Buffer.concat([cipher.update(JSON.stringify(credentials),'utf8'),cipher.final()]);
      const envelope=Buffer.from(JSON.stringify({algorithm:'RSA-OAEP-SHA256+AES-256-GCM',wrappedKey,iv:iv.toString('base64'),tag:cipher.getAuthTag().toString('base64'),ciphertext:encrypted.toString('base64')}));
      await handle.write(envelope,0,envelope.length,0);await handle.truncate(envelope.length);await handle.sync();
    }
    await deliver([]);
    initializeApp({credential:applicationDefault(),projectId:project});
    const credentials=await provisionStudents(getAuth(),getFirestore(),rows,{onCreated:deliver});
    if(!arg('--csv'))await assignDemo(getFirestore());
    await deliver(credentials);
    console.log('Provisioning complete. Encrypted credential delivery written; existing passwords were not reset.');
  }finally{key.fill(0);await handle.close();}
}
