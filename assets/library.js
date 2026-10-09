import { db } from './firebase-client.js';
import { doc, getDocFromServer } from './firebase-sdk.js';
import { setupLogin, observeAccess, showSession, explainAuthError } from './session.js';
import { decodeCatalog } from './catalog-data.js';
import { setCatalog, clearCatalog } from './catalog-view.js';

setupLogin();
let generation = 0, loadedFor = null;
const message = document.getElementById('auth-message');
function hideCatalog() {
  ['library', 'library-hero', 'library-search'].forEach(id => { document.getElementById(id).hidden = true; });
  document.getElementById('auth-panel').hidden = false;
  clearCatalog(); loadedFor = null;
}
observeAccess(async state => {
  const current = ++generation;
  showSession(state);
  document.getElementById('admin-link').hidden = !state.admin;
  if (!state.allowed) { hideCatalog(); return; }
  if (loadedFor === state.user.uid) return;
  hideCatalog(); message.textContent = 'Đang tải danh mục…';
  try {
    const snap = await getDocFromServer(doc(db, 'libraryCatalog', 'current'));
    if (!snap.exists()) throw new Error('Danh mục chưa được Admin nhập.');
    const data = await decodeCatalog(snap.data());
    if (current !== generation) return;
    setCatalog(data); loadedFor = state.user.uid;
    ['library', 'library-hero', 'library-search'].forEach(id => { document.getElementById(id).hidden = false; });
    document.getElementById('auth-panel').hidden = true;
  } catch (error) {
    if (current !== generation) return;
    hideCatalog();
    message.textContent = error.code ? explainAuthError(error) : error.message;
  }
});
// A background tab does not retain a visible catalog until server permissions are rechecked.
document.addEventListener('visibilitychange', () => {
  if (document.hidden) { generation++; hideCatalog(); }
  else location.reload();
});
