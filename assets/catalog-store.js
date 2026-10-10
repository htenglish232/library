import { db, auth } from './firebase-client.js';
import { ADMIN_UID } from './firebase-config.js';
import { doc, getDocFromServer, runTransaction, serverTimestamp } from './firebase-sdk.js';
import { decodeCatalog, managedPayload } from './catalog-data.js';

export function catalogRevision(fields) {
  if (fields.schemaVersion === 1) return 0;
  if (fields.schemaVersion !== 2 || !Number.isSafeInteger(fields.revision) || fields.revision < 1
    || !/^[0-9a-f]{64}$/.test(fields.parentSha256) || fields.updatedBy !== ADMIN_UID) throw new Error('Thông tin phiên bản danh mục không hợp lệ.');
  return fields.revision;
}
export function catalogToken(fields) {
  return JSON.stringify([catalogRevision(fields), fields.sha256, fields.updatedAt?.seconds, fields.updatedAt?.nanoseconds]);
}
export async function loadCatalog() {
  const snap = await getDocFromServer(doc(db, 'libraryCatalog', 'current'));
  if (!snap.exists()) throw new Error('Danh mục chưa được nhập. Hãy dùng công cụ tạo mới bản gốc trước.');
  const fields = snap.data();
  const data = await decodeCatalog(fields);
  catalogRevision(fields);
  return { fields, data, token: catalogToken(fields) };
}
export async function saveCatalog(data, base) {
  if (auth.currentUser?.uid !== ADMIN_UID) throw new Error('Chỉ Admin được lưu danh mục.');
  if (!base?.token) throw new Error('Phải tải danh mục từ Firebase trước khi sửa.');
  const payload = await managedPayload(data);
  const target = doc(db, 'libraryCatalog', 'current');
  await runTransaction(db, async tx => {
    const latest = await tx.get(target);
    if (!latest.exists()) throw new Error('Danh mục không còn tồn tại. Dừng lưu.');
    const previous = latest.data();
    if (catalogToken(previous) !== base.token) throw new Error('Danh mục đã được thay đổi ở cửa sổ khác. Bản nháp được giữ lại; tải bản mới và đối chiếu trước khi lưu.');
    const revision = catalogRevision(previous);
    const history = doc(db, 'libraryCatalogHistory', String(revision));
    if ((await tx.get(history)).exists()) throw new Error('Bản sao phiên bản đã tồn tại. Dừng lưu để tránh ghi đè.');
    tx.set(history, { revision, snapshot: previous, archivedAt: serverTimestamp(), archivedBy: ADMIN_UID });
    tx.set(target, { schemaVersion: 2, revision: revision + 1, parentSha256: previous.sha256,
      count: payload.count, sha256: payload.sha256, dataJson: JSON.stringify(payload.data),
      updatedAt: serverTimestamp(), updatedBy: ADMIN_UID });
  });
  const saved = await loadCatalog();
  // Another Admin tab may save immediately after our transaction succeeds.
  if (saved.fields.sha256 !== payload.sha256 || saved.fields.dataJson !== JSON.stringify(payload.data)) throw new Error('Lưu đã hoàn tất nhưng bản hiện tại thay đổi trước khi đọc lại. Tải lại để kiểm tra; không tự lưu lần nữa.');
  return saved;
}
