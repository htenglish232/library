import { auth, db } from './firebase-client.js';
import { ADMIN_UID } from './firebase-config.js';
import { onAuthStateChanged, onSnapshot, doc, setPersistence, browserSessionPersistence,
  signInWithEmailAndPassword, signOut, sendPasswordResetEmail } from './firebase-sdk.js';

export function explainAuthError(error) {
  const code = error.code || '';
  if (['auth/invalid-credential','auth/wrong-password','auth/user-not-found','auth/invalid-login-credentials'].includes(code)) return 'Email hoặc mật khẩu không đúng.';
  if (code === 'auth/user-disabled') return 'Tài khoản đăng nhập đã bị vô hiệu hóa. Vui lòng liên hệ Admin.';
  if (code === 'auth/too-many-requests') return 'Có quá nhiều lần thử. Vui lòng chờ rồi thử lại.';
  if (code === 'auth/network-request-failed' || code === 'unavailable') return 'Không kết nối được Firebase. Kiểm tra kết nối và thử lại.';
  if (code === 'permission-denied') return 'Không có quyền truy cập. Vui lòng liên hệ Admin.';
  return 'Không thực hiện được thao tác. Vui lòng thử lại hoặc liên hệ Admin.';
}

// Observe authorization, not just authentication. Epochs reject stale async responses.
export function observeAccess(callback) {
  let stopMember = () => {}, epoch = 0;
  const stopAuth = onAuthStateChanged(auth, user => {
    const current = ++epoch;
    stopMember(); stopMember = () => {};
    callback({ user, allowed: false, admin: false, status: user ? 'checking' : 'signed-out' });
    if (!user) return;
    if (user.uid === ADMIN_UID) {
      callback({ user, allowed: true, admin: true, status: 'active' });
      return;
    }
    stopMember = onSnapshot(doc(db, 'libraryMembers', user.uid), { includeMetadataChanges: true }, snap => {
      if (current !== epoch) return;
      // Never grant access based solely on cached permissions.
      if (snap.metadata.fromCache) {
        callback({ user, allowed: false, admin: false, status: 'checking' }); return;
      }
      const status = snap.exists() ? snap.data().status : 'unapproved';
      callback({ user, allowed: status === 'active', admin: false, status });
    }, error => {
      if (current === epoch) callback({ user, allowed: false, admin: false, status: 'error', error });
    });
  }, error => callback({ allowed: false, status: 'error', error }));
  return () => { epoch++; stopMember(); stopAuth(); };
}

export function setupLogin() {
  const form = document.getElementById('login-form');
  const message = document.getElementById('auth-message');
  const login = document.getElementById('login-submit');
  const reset = document.getElementById('reset-password');
  let pending = false;
  const persistence = setPersistence(auth, browserSessionPersistence);
  form.addEventListener('submit', async event => {
    event.preventDefault(); if (pending) return;
    pending = true; login.disabled = true; reset.disabled = true;
    message.textContent = 'Đang đăng nhập…';
    try {
      await persistence;
      await signInWithEmailAndPassword(auth, form.elements.email.value.trim(), form.elements.password.value);
    } catch (error) { message.textContent = explainAuthError(error); }
    finally { form.elements.password.value = ''; pending = false; login.disabled = false; reset.disabled = false; }
  });
  document.getElementById('logout').addEventListener('click', async () => {
    try { await signOut(auth); } catch (error) { message.textContent = explainAuthError(error); }
  });
  reset.addEventListener('click', async () => {
    const email = form.elements.email.value.trim();
    if (!email || !form.elements.email.checkValidity()) { message.textContent = 'Nhập email hợp lệ trước khi đặt lại mật khẩu.'; return; }
    reset.disabled = true;
    try {
      await sendPasswordResetEmail(auth, email);
      message.textContent = 'Nếu email đủ điều kiện, Firebase sẽ gửi hướng dẫn đặt lại mật khẩu. Kiểm tra hộp thư và thư rác.';
    } catch (error) { message.textContent = explainAuthError(error); }
    finally { reset.disabled = false; }
  });
  persistence.catch(error => { message.textContent = explainAuthError(error); });
}

export function showSession(state) {
  const signedIn = !!state.user;
  document.getElementById('account-email').textContent = state.user?.email || '';
  document.getElementById('logout').hidden = !signedIn;
  document.getElementById('login-form').hidden = signedIn;
  document.getElementById('reset-password').hidden = signedIn;
  const descriptions = {
    'signed-out': 'Đăng nhập bằng tài khoản giáo viên đã được Admin cấp quyền.',
    checking: 'Đang kiểm tra quyền truy cập…', active: '',
    unapproved: 'Tài khoản chưa được cấp quyền xem thư viện. Vui lòng liên hệ Admin.',
    locked: 'Quyền truy cập thư viện đang bị khóa. Vui lòng liên hệ Admin.',
    revoked: 'Quyền truy cập thư viện đã bị thu hồi. Vui lòng liên hệ Admin.',
    error: state.error ? explainAuthError(state.error) : 'Không xác minh được quyền truy cập.'
  };
  document.getElementById('auth-message').textContent = descriptions[state.status] ?? descriptions.unapproved;
}
