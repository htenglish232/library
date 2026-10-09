(() => {
  'use strict';
  const KEY = 'ht-english:teacher-session:v1';
  const DAYS_30 = 30 * 24 * 60 * 60 * 1000;
  const login = document.getElementById('teacher-login');
  const library = document.getElementById('teacher-library');
  const form = document.getElementById('login-form');
  const username = document.getElementById('teacher-username');
  const password = document.getElementById('teacher-password');
  const submit = document.getElementById('login-submit');
  const show = document.getElementById('show-password');
  const message = document.getElementById('login-message');
  let accounts = [], ready = false, timer, memorySession = null;
  // Fall back to this tab when persistent browser storage is unavailable.
  function storage(name) {
    try {
      const store = window[name], probe = KEY + ':probe';
      store.setItem(probe, '1'); store.removeItem(probe); return store;
    } catch { return null; }
  }
  let persistent = storage('localStorage');
  const temporary = storage('sessionStorage');
  function removeSessions() {
    for (const store of [persistent, temporary]) {
      try { store?.removeItem(KEY); } catch { /* Storage can be disabled during use. */ }
    }
    memorySession = null;
  }
  function readSession() {
    try { return JSON.parse(persistent?.getItem(KEY) || temporary?.getItem(KEY) || 'null') || memorySession; }
    catch { return null; }
  }
  function valid(session) {
    const now = Date.now();
    return session && session.version === 1 && Number.isFinite(session.issuedAt) && Number.isFinite(session.expiresAt) &&
      session.issuedAt <= now && session.expiresAt > now && session.expiresAt - session.issuedAt === DAYS_30 &&
      accounts.some(a => a.username === session.username && a.id === session.accountId);
  }
  function lock(text = '', focus = false) {
    clearTimeout(timer); removeSessions(); library.hidden = true; login.hidden = false;
    form.reset(); password.type = 'password'; show.textContent = 'Hiện'; show.setAttribute('aria-pressed', 'false');
    message.textContent = text;
    if (focus && ready) username.focus();
  }
  function unlock(session, focus = false) {
    login.hidden = true; library.hidden = false; password.value = '';
    document.getElementById('session-notice').textContent = persistent ? '' : '· Trình duyệt không cho phép ghi nhớ 30 ngày; phiên này chỉ dùng tạm thời.';
    clearTimeout(timer);
    // setTimeout has a 32-bit maximum; recheck periodically and on resume.
    timer = setTimeout(checkSession, Math.min(session.expiresAt - Date.now(), 60 * 60 * 1000));
    if (focus) document.getElementById('search').focus();
  }
  function checkSession() {
    if (!ready) return;
    const session = readSession();
    if (valid(session)) unlock(session);
    else if (library.hidden) removeSessions();
    else lock('Phiên đăng nhập đã hết hạn hoặc đã đăng xuất. Vui lòng đăng nhập lại.');
  }
  show.addEventListener('click', () => {
    const visible = password.type === 'password'; password.type = visible ? 'text' : 'password';
    show.textContent = visible ? 'Ẩn' : 'Hiện'; show.setAttribute('aria-pressed', String(visible));
  });
  document.getElementById('teacher-logout').addEventListener('click', () => lock('Bạn đã đăng xuất.', true));
  window.addEventListener('storage', event => { if (event.key === KEY || event.key === null) checkSession(); });
  window.addEventListener('pageshow', checkSession);
  window.addEventListener('focus', checkSession);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) checkSession(); });
  form.addEventListener('submit', async event => {
    event.preventDefault(); if (!ready || submit.disabled) return;
    submit.disabled = true; message.textContent = 'Đang kiểm tra tài khoản…';
    try {
      const account = accounts.find(a => a.username === username.value.trim());
      // Perform derivation for unknown users too. This is not server-side rate limiting.
      const result = await HTTeacherCrypto.verifier(password.value, account?.salt || '00000000000000000000000000000000');
      if (!account || result !== account.verifier) {
        message.textContent = 'Tài khoản hoặc mật khẩu chưa đúng. Vui lòng thử lại.';
        password.value = ''; password.focus(); return;
      }
      const now = Date.now();
      const session = {version: 1, username: account.username, accountId: account.id, issuedAt: now, expiresAt: now + DAYS_30};
      removeSessions();
      try { if (!persistent) throw new Error('No persistent storage'); persistent.setItem(KEY, JSON.stringify(session)); }
      catch {
        persistent = null;
        try { if (!temporary) throw new Error('No session storage'); temporary.setItem(KEY, JSON.stringify(session)); }
        catch { memorySession = session; }
      }
      unlock(session, true);
    } catch { message.textContent = 'Không thể kiểm tra đăng nhập. Hãy dùng trình duyệt mới và mở trang qua HTTPS.'; }
    finally { submit.disabled = false; }
  });
  async function init() {
    try {
      if (!window.crypto?.subtle || !window.HTTeacherCrypto) throw new Error('Unsupported browser');
      const response = await fetch(new URL('teacher-accounts.json', document.querySelector('script[src="teacher-access/login.js"]').src), {cache: 'no-store'});
      if (!response.ok) throw new Error('Account configuration unavailable');
      accounts = HTTeacherCrypto.validate(await response.json()).accounts;
      if (!accounts.length) {
        lock('Thư viện chưa được cấu hình tài khoản giáo viên. Vui lòng liên hệ người quản lý.'); return;
      }
      ready = true; username.disabled = password.disabled = show.disabled = submit.disabled = false;
      message.textContent = ''; checkSession();
    } catch { lock('Không tải được cấu hình đăng nhập. Vui lòng tải lại trang hoặc liên hệ người quản lý.'); }
  }
  init();
})();
