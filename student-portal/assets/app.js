import {initializeApp} from 'firebase/app';
import {getAuth, connectAuthEmulator, setPersistence, browserSessionPersistence, signInWithEmailAndPassword, signOut, onAuthStateChanged} from 'firebase/auth';
import {parseAssignment, studentEmail} from './routing.js';
const $ = id => document.getElementById(id);
const views = ['login','dashboard','game','receipt'];
function show(view) { for (const v of views) $(v+'-view').hidden = v !== view; }
let config, auth, student, currentAttempt, currentAssignment, submission, generation = 0, ready = false, busy = false;
const storage = {get:k=>{try{return sessionStorage.getItem(k);}catch{return null;}},set:(k,v)=>{try{sessionStorage.setItem(k,v);}catch{}},remove:k=>{try{sessionStorage.removeItem(k);}catch{}}};
let pending = null;
try {
  pending = parseAssignment(location.search);
  if (pending) storage.set('portal-assignment', pending);
  else if (!location.search) pending = parseAssignment('?assignment='+encodeURIComponent(storage.get('portal-assignment')||''));
} catch { $('login-message').textContent = 'Link bài tập không hợp lệ. Em vẫn có thể đăng nhập để xem bài được giao.'; storage.remove('portal-assignment'); }
async function api(path, body) {
  const user = auth.currentUser;
  if (!user) throw Error('Em cần đăng nhập lại.');
  const token = await user.getIdToken();
  const response = await fetch('/api/'+path, {method:body?'POST':'GET',
    headers:{Authorization:'Bearer '+token, ...(body?{'Content-Type':'application/json'}:{})},
    body:body?JSON.stringify(body):undefined, cache:'no-store'});
  const data = await response.json();
  if (auth.currentUser?.uid !== user.uid) throw Error('Tài khoản đã thay đổi. Em hãy đăng nhập lại.');
  if (!response.ok) throw Error(({
    'sign-in-required':'Phiên đăng nhập đã hết. Em hãy đăng xuất rồi đăng nhập lại.',
    'student-access-denied':'Tài khoản chưa được cấp quyền hoặc đã bị khóa. Em hãy nhờ giáo viên hỗ trợ.',
    'assignment-unavailable':'Bài tập chưa được giao hoặc đã hết hạn.',
    'portal-paused':'Hệ thống đang tạm dừng nhận bài. Em hãy thử lại sau.',
    'attempt-limit':'Em đã đạt giới hạn 20 lượt luyện tập của bài này.',
    'submission-conflict':'Bài này đã nộp với nội dung khác. Em hãy xem lịch sử.'
  })[data.error] || 'Chưa thực hiện được. Em hãy kiểm tra kết nối và thử lại.');
  return data;
}
function node(tag, text, className) {const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(className)el.className=className;return el;}
async function dashboard() {
  const epoch = generation;
  show('dashboard'); $('dashboard-message').textContent = 'Đang tải góc học tập…';
  $('assignments').replaceChildren(); $('history').replaceChildren();
  try {
    const d = await api('dashboard'); if (epoch !== generation) return;
    student = d.student;
    $('greeting').textContent = 'Chào '+student.displayName+'! 👋';
    $('display-name').textContent=student.displayName;
    $('student-details').textContent=student.studentId+' · '+student.className;
    $('stars').textContent=student.stars; $('level').textContent='Nhà khám phá · Cấp '+student.level;
    $('dashboard-message').textContent=pending && !d.assignments.some(a=>a.id===pending)?'Bài trong link không khả dụng cho tài khoản này. Em hãy chọn bài được giao bên dưới.':'';
    d.assignments.sort((a,b)=>(b.id===pending)-(a.id===pending));
    for (const a of d.assignments) {
      const card=node('article',undefined,'assignment-card'+(a.id===pending?' highlight':''));
      card.dataset.assignmentId=a.id;
      card.append(node('span',a.id===pending?'BÀI TỪ GIÁO VIÊN':'LUYỆN TẬP','badge'),node('h3',a.title),
        node('p','Lớp 8 · 42 câu · Nghe, đọc và viết'),node('p','Hoàn thành đủ câu: +5 sao một lần cho bài được giao.'));
      const button=node('button','Bắt đầu làm bài →','primary'); button.onclick=()=>start(a.id,button); card.append(button); $('assignments').append(card);
    }
    if (!d.assignments.length) $('assignments').append(node('p','Em chưa có bài tập đang mở. Hãy nhờ giáo viên giao bài nhé.','empty-card'));
    for (const attempt of d.history) {
      const row=node('article',undefined,'history-row'), info=node('div');
      const time = attempt.submittedAt?new Date((attempt.submittedAt._seconds??attempt.submittedAt.seconds)*1000).toLocaleString('vi-VN'):'Chưa nộp';
      info.append(node('span','Trực Tuấn · Lớp 8'),node('small',time+(typeof attempt.elapsedSeconds==='number'?' · '+attempt.elapsedSeconds+' giây':'')));
      row.append(info,node('strong',attempt.result?attempt.result.score+'/10 · '+attempt.result.correct+'/42 đúng':'Đang luyện tập')); $('history').append(row);
    }
    if (!d.history.length) $('history').append(node('p','Chưa có lượt làm. Bắt đầu nhiệm vụ đầu tiên nào!','empty-card'));
  } catch (error) { if(epoch===generation)$('dashboard-message').textContent=error.message; }
}
async function start(id, button) {
  if (busy) return; busy=true;button.disabled=true;
  const epoch=generation, key='portal-attempt:'+auth.currentUser.uid+':'+id;
  try {
    let attemptId=storage.get(key);
    if(!attemptId){attemptId=crypto.randomUUID();storage.set(key,attemptId);}
    let result=await api('attempts/start',{assignmentId:id,attemptId});
    if(result.status==='submitted'){attemptId=crypto.randomUUID();storage.set(key,attemptId);result=await api('attempts/start',{assignmentId:id,attemptId});}
    if(epoch!==generation)return;
    currentAttempt=result;currentAssignment=id;submission=null;ready=false;
    $('submit-attempt').disabled=true;$('game-message').textContent='Đang mở bài luyện tập…';show('game');
    $('game-frame').src=config.gamePath;
  }catch(error){if(epoch===generation)$('dashboard-message').textContent=error.message;}
  finally{busy=false;button.disabled=false;}
}
async function submit(answers) {
  if(busy || !currentAttempt)return;
  busy=true;$('submit-attempt').disabled=true;
  const epoch=generation;
  submission={attemptId:currentAttempt.attemptId,contentVersion:currentAttempt.contentVersion,answers};
  $('game-message').textContent='Đang gửi bài. Em hãy giữ trang mở nhé…';
  try{
    const receipt=await api('attempts/submit',submission);
    if(epoch!==generation)return;
    storage.remove('portal-attempt:'+auth.currentUser.uid+':'+currentAssignment);
    $('game-frame').removeAttribute('src');submission=null;
    $('receipt-score').textContent=receipt.result.score+'/10 · '+receipt.result.correct+'/42 câu đúng';
    $('receipt-stars').textContent=receipt.starsAwarded?'⭐ +'+receipt.starsAwarded+' sao đã được ghi nhận!':'Sao không cộng thêm. Mỗi bài được giao chỉ thưởng một lần khi hoàn thành đủ 42 câu.';
    $('receipt-detail').textContent='Chưa trả lời: '+receipt.result.unanswered+' · Chờ giáo viên: '+receipt.result.pending;show('receipt');
  }catch(error){if(epoch===generation)$('game-message').textContent=error.message+' Bài chưa được xác nhận. Nhấn “Nộp bài” để gửi lại cùng lượt.';}
  finally{busy=false;$('submit-attempt').disabled=!ready;}
}
window.addEventListener('message',event=>{
  if(event.origin!==location.origin||event.source!==$('game-frame').contentWindow||!currentAttempt||!auth.currentUser)return;
  const m=event.data;
  if(m?.type==='portal-ready')$('game-frame').contentWindow.postMessage({type:'portal-init',attemptId:currentAttempt.attemptId,studentName:student.displayName},location.origin);
  if(m?.type==='portal-started'&&m.attemptId===currentAttempt.attemptId){ready=true;$('submit-attempt').disabled=false;$('game-message').textContent='Điểm luyện tập chưa phải điểm thi. Em có thể nộp bài hoặc làm lại sau.';}
  if(m?.type==='portal-answers'&&m.attemptId===currentAttempt.attemptId)submit(m.answers);
});
$('submit-attempt').onclick=()=>{if(submission)submit(submission.answers);else if(ready)$('game-frame').contentWindow.postMessage({type:'portal-export',attemptId:currentAttempt.attemptId},location.origin);};
$('back-dashboard').onclick=()=>{if(busy)return;$('game-frame').removeAttribute('src');currentAttempt=null;dashboard();};
$('receipt-home').onclick=dashboard;$('refresh-dashboard').onclick=dashboard;
$('show-password').onclick=()=>{const visible=$('password').type==='password';$('password').type=visible?'text':'password';$('show-password').textContent=visible?'Ẩn':'Hiện';$('show-password').setAttribute('aria-label',visible?'Ẩn mật khẩu':'Hiện mật khẩu');$('show-password').setAttribute('aria-pressed',String(visible));};
$('login-form').onsubmit=async event=>{
  event.preventDefault();if(!auth||busy)return;busy=true;$('login-button').disabled=true;
  $('login-message').textContent='Đang đăng nhập…';
  try{await signInWithEmailAndPassword(auth,studentEmail($('student-id').value),$('password').value);$('login-message').textContent='';}
  catch{$('login-message').textContent='ID hoặc mật khẩu chưa đúng, hoặc chưa kết nối được. Em hãy kiểm tra và thử lại.';}
  finally{$('password').value='';$('password').type='password';busy=false;$('login-button').disabled=false;}
};
$('logout').onclick=async()=>{if(busy)return;await signOut(auth);};
try {
  config=await (await fetch('/portal-config.json',{cache:'no-store'})).json();
  const local=['127.0.0.1','localhost'].includes(location.hostname);
  if(config.firebase?.projectId==='ht-english-library'||!/^ht-english-student-staging$|^demo-ht-student-portal$/.test(config.firebase?.projectId) ||
    (config.emulator && !local) || !config.gamePath?.startsWith('/games/grade-8/'))throw Error();
  const app=initializeApp(config.firebase);auth=getAuth(app);
  if(config.emulator)connectAuthEmulator(auth,'http://127.0.0.1:9099',{disableWarnings:true});
  await setPersistence(auth,browserSessionPersistence);
  onAuthStateChanged(auth,user=>{
    generation++;student=null;currentAttempt=null;submission=null;ready=false;
    $('game-frame').removeAttribute('src');$('display-name').textContent='';$('student-details').textContent='';$('stars').textContent='0';$('assignments').replaceChildren();$('history').replaceChildren();
    if(user)dashboard();else{show('login');for(let i=sessionStorage.length-1;i>=0;i--){const key=sessionStorage.key(i);if(key.startsWith('portal-attempt:')||key.startsWith('htenglish:practice:'))storage.remove(key);}}
  });
  $('login-button').disabled=false;
} catch { $('login-message').textContent='Cấu hình thử nghiệm chưa sẵn sàng. Em hãy liên hệ giáo viên.';$('login-button').disabled=true; }
