import {test} from 'node:test';
import assert from 'node:assert/strict';
import {generateKeyPairSync,randomBytes,createCipheriv,publicEncrypt,constants} from 'node:crypto';
import {mkdtemp,writeFile,readFile,rm,access} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawnSync} from 'node:child_process';
test('encrypted administrator handover decrypts privately and rejects tampering/overwrite',async()=>{
  const dir=await mkdtemp(join(tmpdir(),'ht-delivery-test-'));
  try{
    const {privateKey,publicKey}=generateKeyPairSync('rsa',{modulusLength:2048});
    await writeFile(join(dir,'private.pem'),privateKey.export({type:'pkcs8',format:'pem'}),{mode:0o600});
    const credentials=[{studentId:'HT0001',password:randomBytes(18).toString('base64url')}];
    const key=randomBytes(32),iv=randomBytes(12),cipher=createCipheriv('aes-256-gcm',key,iv);
    const encrypted=Buffer.concat([cipher.update(JSON.stringify(credentials),'utf8'),cipher.final()]);
    const envelope={algorithm:'RSA-OAEP-SHA256+AES-256-GCM',
      wrappedKey:publicEncrypt({key:publicKey,oaepHash:'sha256',padding:constants.RSA_PKCS1_OAEP_PADDING},key).toString('base64'),
      iv:iv.toString('base64'),tag:cipher.getAuthTag().toString('base64'),ciphertext:encrypted.toString('base64')};
    await writeFile(join(dir,'envelope.json'),JSON.stringify(envelope));
    const args=['tools/student-portal-decrypt.mjs','--in',join(dir,'envelope.json'),'--private-key',join(dir,'private.pem'),'--out',join(dir,'credentials.json')];
    const result=spawnSync(process.execPath,args,{encoding:'utf8'});assert.equal(result.status,0,result.stderr);
    assert.deepEqual(JSON.parse(await readFile(join(dir,'credentials.json'),'utf8')),credentials);
    assert(!result.stdout.includes(credentials[0].password));
    assert.notEqual(spawnSync(process.execPath,args).status,0,'must not overwrite an existing delivery');
    envelope.tag=randomBytes(16).toString('base64');await writeFile(join(dir,'envelope.json'),JSON.stringify(envelope));
    args[args.length-1]=join(dir,'tampered.json');
    assert.notEqual(spawnSync(process.execPath,args).status,0);
    await assert.rejects(access(join(dir,'tampered.json')));
    key.fill(0);
  }finally{await rm(dir,{recursive:true,force:true});}
});
