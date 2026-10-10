import { db } from './firebase-client.js';
import { doc, onSnapshot } from './firebase-sdk.js';
import { setupLogin, observeAccess, showSession, explainAuthError } from './session.js';
import { decodeCatalog } from './catalog-data.js';
import { setCatalog, clearCatalog } from './catalog-view.js';

setupLogin();
let generation = 0, loadedFor = null, stopCatalog = () => {};
const message = document.getElementById('auth-message');
function hideCatalog() {
  ['library', 'library-hero', 'library-search'].forEach(id => { document.getElementById(id).hidden = true; });
  document.getElementById('auth-panel').hidden = false;
  clearCatalog(); loadedFor = null; stopCatalog(); stopCatalog = () => {};
}
observeAccess(async state => {
  showSession(state);
  document.getElementById('admin-link').hidden = !state.admin;
  if (!state.allowed) { generation++; hideCatalog(); return; }
  if (loadedFor === state.user.uid) return;
  const current = ++generation;
  hideCatalog(); message.textContent = 'Đang tải danh mục…';
  let delivery = 0;
  stopCatalog = onSnapshot(doc(db, 'libraryCatalog', 'current'), { includeMetadataChanges: true }, async snap => {
    const received = ++delivery;
    try {
      if (current !== generation) return;
      if (snap.metadata.fromCache) {
        clearCatalog();
        ['library', 'library-hero', 'library-search'].forEach(id => { document.getElementById(id).hidden = true; });
        document.getElementById('auth-panel').hidden = false;
        message.textContent = 'Đang xác minh danh mục trên Firebase…'; return;
      }
      if (!snap.exists()) throw new Error('Danh mục chưa được Admin nhập.');
      const data = await decodeCatalog(snap.data());
      if (current !== generation || received !== delivery) return;
      setCatalog(data, snap.data().schemaVersion); loadedFor = state.user.uid;
      ['library', 'library-hero', 'library-search'].forEach(id => { document.getElementById(id).hidden = false; });
      document.getElementById('auth-panel').hidden = true;
    } catch (error) {
      if (current !== generation || received !== delivery) return;
      hideCatalog();
      message.textContent = error.code ? explainAuthError(error) : error.message;
    }
  }, error => {
    if (current !== generation) return;
    hideCatalog(); message.textContent = explainAuthError(error);
  });
});
// A background tab does not retain a visible catalog until server permissions are rechecked.
document.addEventListener('visibilitychange', () => {
  if (document.hidden) { generation++; hideCatalog(); }
  else location.reload();
});
