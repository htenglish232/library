import {randomBytes} from 'node:crypto';
import {Timestamp} from 'firebase-admin/firestore';
import {data, gameId} from './grading.js';
export const DEMO_ASSIGNMENT = 'truc-tuan-grade8-demo';
export const demoStudents = [
  {studentId:'HT0001',displayName:'Học sinh Demo A',classId:'grade8-demo'},
  {studentId:'HT0002',displayName:'Học sinh Demo B',classId:'grade8-demo'},
  {studentId:'HT0003',displayName:'Học sinh Demo C',classId:'grade8-demo'}
];
export function validateRows(rows) {
  if(!Array.isArray(rows)||!rows.length||rows.length>100)throw Error('Expected 1–100 student rows');
  const ids=new Set();
  for(const row of rows){
    if(Object.keys(row).sort().join(',')!=='classId,displayName,studentId' ||
       !/^HT[A-Z0-9-]{4,30}$/.test(row.studentId)||ids.has(row.studentId)||
       typeof row.displayName!=='string'||!row.displayName.trim()||row.displayName.length>80||
       !/^[a-zA-Z0-9_-]{1,64}$/.test(row.classId))throw Error('Invalid/duplicate student row');
    ids.add(row.studentId);
  }
}
// An interrupted run can resume without resetting credentials or overwriting stars.
export async function provisionStudents(auth, db, rows, {onCreated=async()=>{}}={}) {
  validateRows(rows);
  const credentials=[];
  for(const row of rows){
    const uid='portal-'+row.studentId.toLowerCase(),email=row.studentId.toLowerCase()+'@students.htenglish.invalid';
    const reservation=db.doc('portalStudentIds/'+row.studentId);
    await db.runTransaction(async tx=>{
      const prior=await tx.get(reservation);
      if(prior.exists&&prior.data().uid!==uid)throw Error('Student ID reservation conflict');
      if(!prior.exists)tx.create(reservation,{uid,status:'pending'});
    });
    let user;
    try{user=await auth.getUser(uid);}catch(error){if(error.code!=='auth/user-not-found')throw error;}
    if(user&&user.email!==email)throw Error('Auth identity conflict; stop without resetting');
    if(!user){
      const password=randomBytes(18).toString('base64url');
      user=await auth.createUser({uid,email,password,displayName:row.displayName});
      credentials.push({studentId:row.studentId,password});
      await onCreated([...credentials]);
    }
    await db.runTransaction(async tx=>{
      const profile=db.doc('students/'+uid),principal=db.doc('portalPrincipals/'+uid);
      const [existing,role]=await Promise.all([tx.get(profile),tx.get(principal)]);
      if(existing.exists&&(existing.data().studentId!==row.studentId||existing.data().classId!==row.classId))throw Error('Existing profile conflict');
      if(role.exists&&role.data().role!=='student')throw Error('Existing role conflict');
      if(!existing.exists)tx.create(profile,{...row,className:'Grade 8',avatarId:'default',stars:0,status:'active',createdAt:Timestamp.now()});
      if(!role.exists)tx.create(principal,{role:'student',status:'active',createdAt:Timestamp.now()});
      tx.set(reservation,{uid,status:'provisioned'});
    });
  }
  return credentials;
}
export async function assignDemo(db, rows=demoStudents) {
  const ref=db.doc('assignments/'+DEMO_ASSIGNMENT);
  await db.runTransaction(async tx=>{
    const existing=await tx.get(ref);
    if(existing.exists){
      if(existing.data().contentVersion!==data.contentVersion||existing.data().mode!=='practice')throw Error('Existing assignment conflict');
    }else tx.create(ref,{title:'Trực Tuấn · Nhiệm vụ tiếng Anh 8',classId:'grade8-demo',
      gameId,contentVersion:data.contentVersion,mode:'practice',status:'open',
      opensAt:Timestamp.fromMillis(Date.now()-60000),dueAt:Timestamp.fromMillis(Date.now()+30*86400000)});
    for(const row of rows)tx.set(db.doc('students/portal-'+row.studentId.toLowerCase()+'/assignments/'+DEMO_ASSIGNMENT),{status:'active'});
  });
}
