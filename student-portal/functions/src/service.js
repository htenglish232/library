import {createHash} from 'node:crypto';
import {FieldValue, Timestamp} from 'firebase-admin/firestore';
import {data, gameId, evaluate} from './grading.js';

export class ApiError extends Error {
  constructor(status, code) { super(code); this.status = status; }
}
const fail = (status, code) => { throw new ApiError(status, code); };
const exact = (body, keys) => {
  if (!body || typeof body !== 'object' || Array.isArray(body) ||
      Object.keys(body).sort().join(',') !== [...keys].sort().join(',')) fail(400, 'invalid-request');
};
export const assignmentIdValid = value => typeof value === 'string' && /^[a-zA-Z0-9_-]{1,64}$/.test(value);
const attemptIdValid = value => typeof value === 'string' && /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/.test(value);
const stamp = () => FieldValue.serverTimestamp();
const serialize = value => JSON.parse(JSON.stringify(value, (_, item) => item));
export function createService(db, {enabled = () => process.env.PORTAL_ENABLED === 'true', now = () => Date.now()} = {}) {
  const studentRef = uid => db.doc('students/' + uid);
  async function access(tx, uid) {
    const principal = await tx.get(db.doc('portalPrincipals/' + uid));
    const student = await tx.get(studentRef(uid));
    if (!principal.exists || principal.data().role !== 'student' || principal.data().status !== 'active' ||
        !student.exists || student.data().status !== 'active') fail(403, 'student-access-denied');
    return student.data();
  }
  async function assignment(tx, uid, student, id) {
    const a = await tx.get(db.doc('assignments/' + id));
    const membership = await tx.get(studentRef(uid).collection('assignments').doc(id));
    if (!a.exists || !membership.exists || membership.data().status !== 'active') fail(403, 'assignment-unavailable');
    const record = a.data();
    if (record.classId !== student.classId || record.status !== 'open' || record.mode !== 'practice' ||
        record.gameId !== gameId || record.contentVersion !== data.contentVersion ||
        !(record.opensAt instanceof Timestamp) || !(record.dueAt instanceof Timestamp) ||
        now() < record.opensAt.toMillis() || now() > record.dueAt.toMillis()) fail(403, 'assignment-unavailable');
    return record;
  }
  return {
    async dashboard(uid) {
      return db.runTransaction(async tx => {
        const student = await access(tx, uid);
        const refs = await tx.get(studentRef(uid).collection('assignments').limit(30));
        const assignments = [];
        for (const ref of refs.docs) {
          try { const a = await assignment(tx, uid, student, ref.id); assignments.push({id:ref.id, title:a.title, mode:a.mode}); }
          catch (error) { if (!(error instanceof ApiError) || error.status !== 403) throw error; }
        }
        const history = await tx.get(studentRef(uid).collection('attempts').orderBy('startedAt', 'desc').limit(30));
        return serialize({student:{studentId:student.studentId, displayName:student.displayName,
          className:student.className, avatarId:'default', stars:student.stars || 0,
          level:1 + Math.floor((student.stars || 0) / 50)}, assignments,
          history:history.docs.map(d => {
            const a=d.data();return {id:d.id,assignmentId:a.assignmentId,status:a.status,
              startedAt:a.startedAt,submittedAt:a.submittedAt||null,elapsedSeconds:a.elapsedSeconds??null,result:a.result||null};
          })});
      });
    },
    async start(uid, body) {
      if (!enabled()) fail(503, 'portal-paused');
      exact(body, ['assignmentId', 'attemptId']);
      if (!assignmentIdValid(body.assignmentId) || !attemptIdValid(body.attemptId)) fail(400, 'invalid-request');
      const ref = studentRef(uid).collection('attempts').doc(body.attemptId);
      return db.runTransaction(async tx => {
        const student = await access(tx, uid);
        await assignment(tx, uid, student, body.assignmentId);
        const existing = await tx.get(ref);
        const rewardRef = studentRef(uid).collection('studentRewards').doc(body.assignmentId);
        const reward = await tx.get(rewardRef);
        if (existing.exists) {
          if (existing.data().assignmentId !== body.assignmentId) fail(409, 'attempt-conflict');
          return {attemptId:ref.id, status:existing.data().status, contentVersion:data.contentVersion};
        }
        if ((reward.data()?.startedCount || 0) >= 20) fail(429, 'attempt-limit');
        tx.set(ref, {assignmentId:body.assignmentId, gameId, contentVersion:data.contentVersion,
          status:'in_progress', startedAt:stamp()});
        tx.set(rewardRef, {startedCount:(reward.data()?.startedCount || 0)+1}, {merge:true});
        return {attemptId:ref.id, status:'in_progress', contentVersion:data.contentVersion};
      });
    },
    async submit(uid, body) {
      if (!enabled()) fail(503, 'portal-paused');
      exact(body, ['attemptId', 'answers', 'contentVersion']);
      if (!attemptIdValid(body.attemptId) || body.contentVersion !== data.contentVersion) fail(400, 'invalid-request');
      let result;
      try { result = evaluate(body.answers); } catch { fail(400, 'invalid-answers'); }
      // Hash normalized key ordering; retrying identical answers is idempotent.
      const answers = Object.fromEntries(data.questions.map(q => [q.id, {
        value:body.answers[q.id].value, fields:body.answers[q.id].fields, tokens:body.answers[q.id].tokens
      }]));
      const digest = createHash('sha256').update(JSON.stringify(answers)).digest('hex');
      const attemptRef = studentRef(uid).collection('attempts').doc(body.attemptId);
      return db.runTransaction(async tx => {
        const student = await access(tx, uid);
        const snapshot = await tx.get(attemptRef);
        if (!snapshot.exists) fail(404, 'attempt-not-found');
        const attempt = snapshot.data();
        // Retry still requires current student access, but a previously committed
        // receipt remains retrievable after the assignment deadline.
        if (attempt.status === 'submitted') {
          if (attempt.submissionDigest !== digest) fail(409, 'submission-conflict');
          return attempt.receipt;
        }
        await assignment(tx, uid, student, attempt.assignmentId);
        if (attempt.status !== 'in_progress' || attempt.contentVersion !== data.contentVersion) fail(409, 'attempt-conflict');
        const rewardRef = studentRef(uid).collection('studentRewards').doc(attempt.assignmentId);
        const reward = await tx.get(rewardRef);
        const ledgerRef = studentRef(uid).collection('starTransactions').doc(attempt.assignmentId + '-completion');
        const ledger = await tx.get(ledgerRef);
        const starsAwarded = !ledger.exists && !reward.data()?.rewardGranted && result.checked === result.total ? 5 : 0;
        const receipt = {attemptId:body.attemptId, result, starsAwarded,
          verification:'server_evaluated_practice', official:false};
        const elapsedSeconds = Math.max(0, Math.floor((now()-attempt.startedAt.toMillis())/1000));
        tx.update(attemptRef, {answers, result, receipt, submissionDigest:digest,
          status:'submitted', submittedAt:stamp(), elapsedSeconds});
        if (starsAwarded) {
          tx.create(ledgerRef, {delta:starsAwarded, reason:'practice-completion', assignmentId:attempt.assignmentId,
            attemptId:body.attemptId, policyVersion:'staging-v1', createdAt:stamp()});
          tx.set(rewardRef, {rewardGranted:true, rewardedAttemptId:body.attemptId, awardedAt:stamp()}, {merge:true});
          tx.update(studentRef(uid), {stars:(student.stars||0)+starsAwarded, updatedAt:stamp()});
        }
        return receipt;
      });
    },
    async teacherReport(uid, classId) {
      if (!assignmentIdValid(classId)) fail(400, 'invalid-request');
      return db.runTransaction(async tx => {
        const role = await tx.get(db.doc('portalPrincipals/' + uid));
        const scope = await tx.get(db.doc('portalTeachers/' + uid + '/classes/' + classId));
        if (!role.exists || role.data().status !== 'active' || !['teacher','admin'].includes(role.data().role) ||
            (role.data().role !== 'admin' && (!scope.exists || scope.data().status !== 'active'))) fail(403, 'teacher-access-denied');
        const students = await tx.get(db.collection('students').where('classId','==',classId).limit(30));
        return {students:students.docs.map(d=>({studentId:d.data().studentId, displayName:d.data().displayName, stars:d.data().stars}))};
      });
    }
  };
}
