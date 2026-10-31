// Run only on the administrator's private machine. Never prints credentials.
import {readFile,writeFile,realpath} from 'node:fs/promises';
import {privateDecrypt,createDecipheriv,constants} from 'node:crypto';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
const arg=name=>{const i=process.argv.indexOf(name);return i<0?null:process.argv[i+1];};
if(!arg('--in')||!arg('--private-key')||!arg('--out'))throw Error('Required: --in envelope --private-key private.pem --out private/credentials.json');
const out=resolve(arg('--out'));
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const actual=resolve(await realpath(dirname(out)),out.split('/').pop());
if(actual===root||actual.startsWith(root+'/'))throw Error('Plaintext output must be outside the checkout');
const e=JSON.parse(await readFile(arg('--in'),'utf8'));
if(e.algorithm!=='RSA-OAEP-SHA256+AES-256-GCM')throw Error('Unsupported envelope');
const key=privateDecrypt({key:await readFile(arg('--private-key'),'utf8'),oaepHash:'sha256',padding:constants.RSA_PKCS1_OAEP_PADDING},Buffer.from(e.wrappedKey,'base64'));
try{
  const decipher=createDecipheriv('aes-256-gcm',key,Buffer.from(e.iv,'base64'));
  decipher.setAuthTag(Buffer.from(e.tag,'base64'));
  const content=Buffer.concat([decipher.update(Buffer.from(e.ciphertext,'base64')),decipher.final()]);
  JSON.parse(content.toString('utf8'));
  await writeFile(out,content,{flag:'wx',mode:0o600});content.fill(0);
  console.log('Private credential file created. Deliver privately and delete after use.');
}finally{key.fill(0);}
