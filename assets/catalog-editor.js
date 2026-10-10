import { db, auth } from './firebase-client.js';
import { ADMIN_UID, firebaseConfig, useEmulators } from './firebase-config.js';
import { collection, doc, getDocsFromServer, getDocFromServer } from './firebase-sdk.js';
import { inspectCatalog, managedPayload, validateBackup, decodeCatalog, MAX_CATALOG_BYTES } from './catalog-data.js';
import { loadCatalog, saveCatalog, catalogRevision } from './catalog-store.js';
import { explainAuthError } from './session.js';

const $ = id => document.getElementById(id);
let allowed = false, epoch = 0, draft = null, base = null, dirty = false, busy = false;
let gradeIndex = 0, unitIndex = 0, lessonIndex = -1;
const status = $('editor-message');
function requireAdmin() { if (!allowed || auth.currentUser?.uid !== ADMIN_UID) throw new Error('Chỉ Admin được quản lý danh mục.'); }
function fail(error) { status.textContent = error.code ? explainAuthError(error) : error.message; }
function element(tag, text) { const node = document.createElement(tag); node.textContent = text; return node; }
function grade() { return draft?.[gradeIndex]; }
function unit() { return grade()?.units[unitIndex]; }
function resetLesson() { lessonIndex = -1; $('lesson-form').reset(); $('lesson-destination').hidden = true; $('lesson-submit').textContent = 'Thêm bài tập vào bản nháp'; }
function destinationOptions(targetGrade = gradeIndex, targetUnit = unitIndex) {
  options($('lesson-target-grade'), draft.map(g => g.grade), targetGrade);
  options($('lesson-target-unit'), (draft[targetGrade]?.units || []).map(u => u.name), targetUnit);
}
function options(select, values, selected) {
  select.replaceChildren();
  values.forEach((name, index) => { const option = element('option', name); option.value = index; select.append(option); });
  select.value = String(selected);
}
function render() {
  $('catalog-editor-fields').disabled = !draft || busy;
  $('save-catalog').disabled = !draft || !dirty || busy;
  $('backup-catalog').disabled = !draft || busy;
  $('reload-catalog').disabled = busy;
  $('restore-file').disabled = !draft || busy;
  $('refresh-history').disabled = !base || busy;
  $('restore-history').disabled = !base || busy || !$('history-version').value;
  if (!draft) { $('editor-summary').textContent = 'Tải danh mục hiện tại để bắt đầu. Chưa sửa dữ liệu Firebase.'; $('lesson-list').replaceChildren(); return; }
  const summary = inspectCatalog(draft);
  gradeIndex = Math.min(gradeIndex, Math.max(0, draft.length - 1));
  unitIndex = Math.min(unitIndex, Math.max(0, (grade()?.units.length || 0) - 1));
  $('editor-summary').textContent = `${summary.count} bài tập tổng cộng · ${summary.visible} đang hiển thị · Phiên bản ${catalogRevision(base.fields)}${dirty ? ' · Có bản nháp chưa lưu' : ' · Đã đọc từ Firebase'}`;
  options($('grade-select'), draft.map(g => g.grade + (g.hidden ? ' (ẩn)' : '')), gradeIndex);
  options($('unit-select'), (grade()?.units || []).map(u => u.name + (u.hidden ? ' (ẩn)' : '')), unitIndex);
  $('grade-name').value = grade()?.grade || '';
  $('unit-name').value = unit()?.name || '';
  $('unit-type').value = unit()?.type || '';
  $('lesson-list').replaceChildren();
  (unit()?.lessons || []).forEach((lesson, index) => {
    const row = element('section', ''); row.className = 'catalog-item';
    row.append(element('strong', `${index + 1}. ${lesson.title}${lesson.hidden ? ' (ẩn)' : ''}`), element('p', lesson.href));
    const actions = [
      ['Sửa', () => { lessonIndex = index; $('lesson-title').value = lesson.title; $('lesson-href').value = lesson.href; $('lesson-hidden').checked = !!lesson.hidden; $('lesson-destination').hidden = false; destinationOptions(); $('lesson-submit').textContent = 'Cập nhật bài tập trong bản nháp'; $('lesson-title').focus(); }],
      [lesson.hidden ? 'Hiện bài' : 'Ẩn bài', () => change(() => { lesson.hidden = !lesson.hidden; })],
      ['Lên', () => reorder(unit().lessons, index, -1)],
      ['Xuống', () => reorder(unit().lessons, index, 1)],
      ['Xóa bài', () => { if (confirm('Xóa liên kết khỏi bản nháp? File HTML/audio và dữ liệu Firebase chưa thay đổi.')) change(() => unit().lessons.splice(index, 1)); }]
    ];
    for (const [label, action] of actions) {
      const button = element('button', label); button.type = 'button'; button.disabled = busy;
      if ((label === 'Lên' && index === 0) || (label === 'Xuống' && index === unit().lessons.length - 1)) button.disabled = true;
      button.addEventListener('click', action); row.append(button);
    }
    $('lesson-list').append(row);
  });
}
function change(action) {
  try {
    requireAdmin(); if (!draft || busy) return;
    const previous = structuredClone(draft);
    try { action(); inspectCatalog(draft); } catch (error) { draft = previous; throw error; }
    dirty = true; resetLesson(); render(); status.textContent = 'Đã sửa bản nháp trên máy. Nhấn Lưu danh mục để áp dụng lên Firebase.';
  } catch (error) { fail(error); }
}
function reorder(items, index, offset) {
  const next = index + offset;
  if (next < 0 || next >= items.length) return;
  change(() => { [items[index], items[next]] = [items[next], items[index]]; });
}
async function task(action) {
  if (busy) return;
  const current = epoch;
  try {
    requireAdmin(); busy = true; render(); await action(current);
  } catch (error) { if (current === epoch) fail(error); }
  finally { if (current === epoch) { busy = false; render(); } }
}
export function setEditorSession(admin) {
  allowed = admin; epoch++; draft = null; base = null; dirty = false; busy = false;
  gradeIndex = 0; unitIndex = 0; resetLesson();
  $('history-version').replaceChildren(); $('restore-file').value = ''; status.textContent = ''; render();
  if (admin) reload();
}
async function reload() {
  if (dirty && !confirm('Bỏ bản nháp chưa lưu và tải danh mục hiện tại? Bạn có thể hủy để tải bản sao lưu trước.')) return;
  await task(async current => {
    const loaded = await loadCatalog(); if (current !== epoch) return;
    draft = structuredClone(loaded.data); base = loaded; dirty = false; resetLesson();
    status.textContent = 'Đã tải và xác minh danh mục hiện tại. Chưa thay đổi Firebase.';
  });
}
$('reload-catalog').addEventListener('click', reload);
$('grade-select').addEventListener('change', event => { gradeIndex = Number(event.target.value); unitIndex = 0; resetLesson(); render(); });
$('unit-select').addEventListener('change', event => { unitIndex = Number(event.target.value); resetLesson(); render(); });
$('add-grade').addEventListener('click', () => change(() => { draft.push({ grade: $('grade-name').value.trim(), units: [] }); gradeIndex = draft.length - 1; unitIndex = 0; }));
$('rename-grade').addEventListener('click', () => change(() => { if (!grade()) throw new Error('Chọn khối lớp trước.'); grade().grade = $('grade-name').value.trim(); }));
$('toggle-grade').addEventListener('click', () => change(() => { if (!grade()) throw new Error('Chọn khối lớp trước.'); grade().hidden = !grade().hidden; }));
$('delete-grade').addEventListener('click', () => { if (grade() && confirm(`Xóa khối ${grade().grade} và toàn bộ liên kết trong khối khỏi bản nháp? Không xóa file bài tập.`)) change(() => draft.splice(gradeIndex, 1)); });
$('grade-up').addEventListener('click', () => { const index = gradeIndex; if (index > 0) { reorder(draft, index, -1); gradeIndex = index - 1; render(); } });
$('grade-down').addEventListener('click', () => { const index = gradeIndex; if (index < draft.length - 1) { reorder(draft, index, 1); gradeIndex = index + 1; render(); } });
$('sort-grades').addEventListener('click', () => change(() => { draft.sort((a,b) => a.grade.localeCompare(b.grade, 'vi', { numeric: true })); gradeIndex = 0; unitIndex = 0; }));
$('add-unit').addEventListener('click', () => change(() => {
  if (!grade()) throw new Error('Tạo hoặc chọn khối lớp trước.');
  const value = { name: $('unit-name').value.trim(), lessons: [] }; if ($('unit-type').value) value.type = $('unit-type').value;
  grade().units.push(value); unitIndex = grade().units.length - 1;
}));
$('rename-unit').addEventListener('click', () => change(() => { if (!unit()) throw new Error('Chọn thư mục trước.'); unit().name = $('unit-name').value.trim(); if ($('unit-type').value) unit().type = $('unit-type').value; else delete unit().type; }));
$('toggle-unit').addEventListener('click', () => change(() => { if (!unit()) throw new Error('Chọn thư mục trước.'); unit().hidden = !unit().hidden; }));
$('delete-unit').addEventListener('click', () => { if (unit() && confirm(`Xóa thư mục ${unit().name} và các liên kết bên trong khỏi bản nháp? Không xóa file bài tập.`)) change(() => grade().units.splice(unitIndex, 1)); });
$('unit-up').addEventListener('click', () => { const index = unitIndex; if (index > 0) { reorder(grade().units, index, -1); unitIndex = index - 1; render(); } });
$('unit-down').addEventListener('click', () => { const index = unitIndex; if (index < (grade()?.units.length || 0) - 1) { reorder(grade().units, index, 1); unitIndex = index + 1; render(); } });
$('lesson-form').addEventListener('submit', event => {
  event.preventDefault();
  change(() => {
    if (!unit()) throw new Error('Chọn thư mục trước.');
    const value = { title: $('lesson-title').value.trim(), href: $('lesson-href').value.trim() };
    if ($('lesson-hidden').checked) value.hidden = true;
    if (lessonIndex < 0) unit().lessons.push(value);
    else {
      const destination = draft[Number($('lesson-target-grade').value)]?.units[Number($('lesson-target-unit').value)];
      if (!destination) throw new Error('Chọn khối lớp và thư mục đích hợp lệ.');
      if (destination === unit()) unit().lessons[lessonIndex] = value;
      else { unit().lessons.splice(lessonIndex, 1); destination.lessons.push(value); }
    }
  });
});
$('lesson-target-grade').addEventListener('change', event => destinationOptions(Number(event.target.value), 0));
$('cancel-lesson-edit').addEventListener('click', resetLesson);
$('save-catalog').addEventListener('click', () => {
  if (!dirty || busy) return;
  const { count, visible } = inspectCatalog(draft);
  if (!confirm(`Lưu bản nháp lên ${useEmulators ? 'Emulator' : firebaseConfig.projectId}?\n${base.fields.count} → ${count} bài (${visible} hiển thị). Bản trước sẽ được sao lưu và phiên bản tăng thêm 1.`)) return;
  if (!useEmulators && prompt(`Nhập chính xác tên dự án để xác nhận: ${firebaseConfig.projectId}`) !== firebaseConfig.projectId) return;
  task(async current => {
    const saved = await saveCatalog(structuredClone(draft), base); if (current !== epoch) return;
    draft = structuredClone(saved.data); base = saved; dirty = false; resetLesson();
    status.textContent = `Đã lưu và đọc lại xác minh ${saved.fields.count} bài, phiên bản ${saved.fields.revision}; bản trước đã được sao lưu. SHA-256: ${saved.fields.sha256}`;
  });
});
$('backup-catalog').addEventListener('click', () => task(async current => {
  const payload = await managedPayload(draft); if (current !== epoch) return;
  const json = JSON.stringify({ ...payload, sourceRevision: catalogRevision(base.fields), includesUnsavedDraft: dirty, exportedAt: new Date().toISOString() }, null, 2);
  const url = URL.createObjectURL(new Blob([json], { type: 'application/json' }));
  const link = document.createElement('a'); link.href = url; link.download = `ht-library-v${catalogRevision(base.fields)}${dirty ? '-ban-nhap' : ''}.json`; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  status.textContent = 'Đã tải bản sao JSON kèm số lượng và SHA-256. Bản nháp chưa lưu được ghi rõ trong tên file; không chứa quyền hoặc thông tin giáo viên.';
}));
$('restore-file').addEventListener('change', event => {
  const file = event.target.files[0]; if (!file) return;
  task(async current => {
    if (!base) throw new Error('Tải danh mục hiện tại trước khi khôi phục.');
    if (file.size > MAX_CATALOG_BYTES * 3) throw new Error('File sao lưu quá lớn.');
    const payload = JSON.parse(await file.text()); const data = await validateBackup(payload);
    if (current !== epoch || !confirm(`Khôi phục ${payload.count} bài vào bản nháp? Chưa ghi Firebase; bản hiện tại vẫn được giữ nguyên đến khi bạn nhấn Lưu.`)) return;
    draft = structuredClone(data); dirty = true; gradeIndex = 0; unitIndex = 0; resetLesson();
    status.textContent = 'Đã kiểm tra số lượng, đường dẫn và SHA-256; khôi phục vào bản nháp. Nhấn Lưu để tạo phiên bản mới, không ghi đè lịch sử.';
  });
  event.target.value = '';
});
$('refresh-history').addEventListener('click', () => task(async current => {
  const snapshots = await getDocsFromServer(collection(db, 'libraryCatalogHistory')); if (current !== epoch) return;
  const list = snapshots.docs.sort((a,b) => b.data().revision - a.data().revision);
  $('history-version').replaceChildren();
  for (const snap of list) { const data = snap.data(); const option = element('option', `Phiên bản ${data.revision} · ${data.snapshot.count} bài`); option.value = snap.id; $('history-version').append(option); }
  status.textContent = list.length ? 'Chọn phiên bản để khôi phục vào bản nháp.' : 'Chưa có lịch sử. Bản trước được tự sao lưu từ lần chỉnh sửa đầu tiên.';
}));
$('history-version').addEventListener('change', render);
$('restore-history').addEventListener('click', () => task(async current => {
  const snap = await getDocFromServer(doc(db, 'libraryCatalogHistory', $('history-version').value));
  if (!snap.exists()) throw new Error('Không tìm thấy phiên bản đã chọn.');
  const history = snap.data(); const data = await decodeCatalog(history.snapshot); catalogRevision(history.snapshot);
  if (current !== epoch || !confirm(`Khôi phục phiên bản ${history.revision} vào bản nháp? Sau khi lưu, đây sẽ là phiên bản mới; lịch sử không bị xóa.`)) return;
  draft = structuredClone(data); dirty = true; gradeIndex = 0; unitIndex = 0; resetLesson();
  status.textContent = 'Đã kiểm tra và khôi phục lịch sử vào bản nháp. Nhấn Lưu để áp dụng.';
}));
window.addEventListener('beforeunload', event => { if (dirty && allowed) { event.preventDefault(); event.returnValue = ''; } });
render();
