import { auth, db } from './firebase-client.js';
import { ADMIN_UID, firebaseConfig, useEmulators } from './firebase-config.js';
import { collection, onSnapshot, doc, setDoc, serverTimestamp, getDocFromServer, runTransaction } from './firebase-sdk.js';
import { setupLogin, observeAccess, showSession, explainAuthError } from './session.js';
import { validateCatalog, decodeCatalog } from './catalog-data.js';

setupLogin();
let stopMembers = () => {}, candidate = null, catalogBeforeImport = null, epoch = 0, busy = false;
const panel = document.getElementById('admin-panel');
const message = document.getElementById('admin-message');
const members = document.getElementById('members');
const importer = document.getElementById('import-catalog');
const preview = document.getElementById('catalog-preview');
const project = useEmulators ? 'demo-ht-english-library (máy cục bộ)' : firebaseConfig.projectId;
function requireAdmin() { if (auth.currentUser?.uid !== ADMIN_UID) throw new Error('Chỉ Admin được thực hiện thao tác này.'); }
function node(tag, text) { const el = document.createElement(tag); el.textContent = text; return el; }
async function writeMember(uid, fields) {
  requireAdmin();
  await setDoc(doc(db, 'libraryMembers', uid), { ...fields, updatedAt: serverTimestamp() });
}
observeAccess(state => {
  epoch++; stopMembers(); stopMembers = () => {};
  candidate = null; catalogBeforeImport = null; importer.disabled = true; preview.textContent = '';
  document.getElementById('catalog-file').value = '';
  members.replaceChildren(); message.textContent = '';
  showSession(state); panel.hidden = !state.admin;
  document.getElementById('auth-panel').hidden = !!state.admin;
  if (state.user && !state.admin) document.getElementById('auth-message').textContent = 'Chỉ tài khoản Admin được mở trang quản lý.';
  if (!state.admin) return;
  const current = epoch;
  stopMembers = onSnapshot(collection(db, 'libraryMembers'), { includeMetadataChanges: true }, snap => {
    if (current !== epoch) return;
    if (snap.metadata.fromCache) { members.replaceChildren(node('p', 'Đang xác minh danh sách trên Firebase…')); return; }
    members.replaceChildren();
    if (snap.empty) members.append(node('p', 'Chưa có giáo viên được cấp quyền.'));
    for (const item of snap.docs) {
      const data = item.data(), row = node('section', ''); row.className = 'member';
      row.append(node('strong', data.name || data.email), node('p', `${data.email} · UID: ${item.id}`), node('p', `Trạng thái: ${{active:'Đang hoạt động',locked:'Đang khóa',revoked:'Đã thu hồi'}[data.status] || 'Không hợp lệ'}`));
      for (const [status, label] of [['locked','Khóa'],['active','Mở khóa / cấp lại'],['revoked','Thu hồi']]) {
        const button = node('button', label); button.type = 'button'; button.disabled = data.status === status;
        button.addEventListener('click', async () => {
          if (busy || !confirm(`${label} quyền thư viện của ${data.email}?\nTài khoản đăng nhập Firebase không bị xóa.`)) return;
          busy = true; button.disabled = true;
          try { await writeMember(item.id, { email: data.email, name: data.name, status }); message.textContent = `Đã ${label.toLowerCase()} quyền của ${data.email}.`; }
          catch (error) { message.textContent = explainAuthError(error); button.disabled = false; }
          finally { busy = false; }
        });
        row.append(button);
      }
      members.append(row);
    }
  }, error => { if (current === epoch) { members.replaceChildren(); message.textContent = explainAuthError(error); } });
});

document.getElementById('member-form').addEventListener('submit', async event => {
  event.preventDefault(); if (busy) return;
  const form = event.currentTarget, uid = form.elements.uid.value.trim();
  if (uid === ADMIN_UID) { message.textContent = 'Không thay đổi tài khoản Admin bằng danh sách giáo viên.'; return; }
  busy = true;
  try {
    requireAdmin();
    const previous = await getDocFromServer(doc(db, 'libraryMembers', uid));
    if (previous.exists() && !confirm('UID này đã được quản lý. Ghi đè thông tin và cấp lại quyền?')) return;
    await writeMember(uid, { email: form.elements.email.value.trim(), name: form.elements.name.value.trim(), status: 'active' });
    message.textContent = 'Đã cấp quyền thư viện. Hãy đối chiếu UID với Firebase Console.'; form.reset();
  } catch (error) { message.textContent = error.code ? explainAuthError(error) : error.message; }
  finally { busy = false; }
});

document.getElementById('catalog-file').addEventListener('change', async event => {
  const current = epoch; candidate = null; catalogBeforeImport = null; importer.disabled = true; preview.textContent = '';
  try {
    requireAdmin(); const file = event.target.files[0]; if (!file) return;
    if (file.size > 200000) throw new Error('File quá lớn.');
    const payload = JSON.parse(await file.text()); await validateCatalog(payload);
    const before = await getDocFromServer(doc(db, 'libraryCatalog', 'current'));
    if (current !== epoch) return;
    if (before.exists()) throw new Error('libraryCatalog/current đã tồn tại. Dừng nhập: lần triển khai này chỉ được tạo mới, không ghi đè.');
    candidate = payload; catalogBeforeImport = before; importer.disabled = false;
    preview.textContent = `Đã kiểm tra: 201 đường dẫn, đúng nội dung và thứ tự bản gốc. Đích: ${project}. Tài liệu hiện chưa tồn tại; chỉ tạo mới. Chưa ghi dữ liệu.`;
  } catch (error) { if (current === epoch) preview.textContent = error.message; }
});

importer.addEventListener('click', async () => {
  if (busy || !candidate) return;
  if (!confirm(`Xác nhận tạo mới danh mục 201 đường dẫn trong ${project}?\nĐích: libraryCatalog/current. Nếu tài liệu đã tồn tại, thao tác phải dừng.`)) return;
  if (!useEmulators && prompt(`Để xác nhận ghi dữ liệu thật, nhập chính xác: ${firebaseConfig.projectId}`) !== firebaseConfig.projectId) return;
  busy = true; importer.disabled = true;
  try {
    requireAdmin(); const payload = candidate; await validateCatalog(payload);
    const before = catalogBeforeImport;
    await runTransaction(db, async transaction => {
      const target = doc(db, 'libraryCatalog', 'current');
      const latest = await transaction.get(target);
      if (!before || before.exists() || latest.exists()) throw new Error('libraryCatalog/current đã tồn tại hoặc chưa được kiểm tra. Dừng nhập; không ghi đè.');
      transaction.set(target, {
        schemaVersion: 1, count: 201, sha256: payload.sha256, dataJson: JSON.stringify(payload.data), updatedAt: serverTimestamp()
      });
    });
    const saved = await getDocFromServer(doc(db, 'libraryCatalog', 'current'));
    await decodeCatalog(saved.data());
    message.textContent = `Đã nhập và đọc lại xác minh đủ 201 đường dẫn, đúng nội dung và thứ tự (${project}).`;
    candidate = null; catalogBeforeImport = null;
  } catch (error) { message.textContent = error.code ? explainAuthError(error) : error.message; }
  finally { busy = false; importer.disabled = !candidate; }
});
