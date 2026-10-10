import { CATALOG_SHA256, CATALOG_COUNT } from './catalog-integrity.js';
export async function validateCatalog(payload) {
  if (payload.schemaVersion !== 1 || payload.count !== CATALOG_COUNT || !Array.isArray(payload.data)) throw new Error('Sai cấu trúc danh mục.');
  const json = JSON.stringify(payload.data);
  const digest = [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(json)))].map(b => b.toString(16).padStart(2, '0')).join('');
  if (digest !== CATALOG_SHA256 || payload.sha256 !== digest) throw new Error('Danh mục không khớp bản gốc: đường dẫn, nội dung hoặc thứ tự đã thay đổi.');
  const links = payload.data.flatMap(g => g.units.flatMap(u => u.lessons.map(l => l.href)));
  if (links.length !== CATALOG_COUNT || new Set(links).size !== CATALOG_COUNT) throw new Error('Danh mục phải có đúng 201 đường dẫn riêng biệt.');
  if (links.some(h => !h.startsWith('grade-') || h.includes('..') || /^[a-z]+:/i.test(h))) throw new Error('Đường dẫn không hợp lệ.');
  return payload.data;
}
export async function decodeCatalog(fields) {
  const payload = { ...fields, data: JSON.parse(fields.dataJson) };
  if (fields.schemaVersion === 1) return validateCatalog(payload);
  await validateManagedCatalog(payload);
  return payload.data;
}

// Reserve space below Firestore's 1 MiB document limit, including metadata.
export const MAX_CATALOG_BYTES = 700000;
export async function catalogHash(data) {
  return [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(JSON.stringify(data))))].map(b => b.toString(16).padStart(2, '0')).join('');
}
function keys(value, required, optional = []) {
  if (!value || typeof value !== 'object' || Array.isArray(value)
    || required.some(key => !(key in value))
    || Object.keys(value).some(key => ![...required, ...optional].includes(key))) throw new Error('Sai cấu trúc danh mục.');
  if ('hidden' in value && typeof value.hidden !== 'boolean') throw new Error('Trạng thái ẩn/hiện không hợp lệ.');
}
function text(value, max = 200) {
  if (typeof value !== 'string' || !value.trim() || value.length > max || /[\u0000-\u001f\u007f]/.test(value)) throw new Error('Tên hoặc đường dẫn không hợp lệ.');
}
export function validateHtmlLink(value) {
  text(value, 2000);
  if (value !== value.trim() || /[\\\s<>"'`]/.test(value.replace(/ /g, ''))) throw new Error('Đường dẫn HTML không hợp lệ.');
  if (/^https:\/\//i.test(value)) {
    const url = new URL(value);
    if (url.username || url.password || !/\.html?$/i.test(url.pathname)) throw new Error('Chỉ chấp nhận đường dẫn HTTPS tới tệp HTML.');
    return;
  }
  if (/^[a-z][a-z0-9+.-]*:/i.test(value) || value.startsWith('/') || value.includes('?') || value.includes('#')) throw new Error('Dùng đường dẫn tương đối trong thư viện hoặc HTTPS tới tệp HTML.');
  let decoded;
  try { decoded = decodeURIComponent(value); } catch { throw new Error('Đường dẫn có mã hóa không hợp lệ.'); }
  if (decoded.split('/').some(part => !part || part === '.' || part === '..') || /[\\\u0000-\u001f\u007f]/.test(decoded) || !/\.html?$/i.test(decoded)) throw new Error('Đường dẫn HTML không an toàn.');
}
export function inspectCatalog(data) {
  if (!Array.isArray(data)) throw new Error('Danh mục phải là danh sách khối lớp.');
  const grades = new Set(), links = new Set();
  let count = 0, visible = 0;
  for (const grade of data) {
    keys(grade, ['grade', 'units'], ['hidden']); text(grade.grade);
    if (grades.has(grade.grade) || !Array.isArray(grade.units)) throw new Error('Khối lớp bị trùng hoặc sai cấu trúc.');
    grades.add(grade.grade);
    for (const unit of grade.units) {
      keys(unit, ['name', 'lessons'], ['type', 'hidden']); text(unit.name);
      if ('type' in unit && unit.type !== 'exam-folder') throw new Error('Loại thư mục không hợp lệ.');
      if (!Array.isArray(unit.lessons)) throw new Error('Danh sách bài tập không hợp lệ.');
      for (const lesson of unit.lessons) {
        keys(lesson, ['title', 'href'], ['hidden']); text(lesson.title); validateHtmlLink(lesson.href);
        if (links.has(lesson.href)) throw new Error('Đường dẫn bài tập bị trùng.');
        links.add(lesson.href); count++;
        if (!grade.hidden && !unit.hidden && !lesson.hidden) visible++;
      }
    }
  }
  if (new TextEncoder().encode(JSON.stringify(data)).length > MAX_CATALOG_BYTES) throw new Error('Danh mục vượt giới hạn kích thước an toàn của Firestore (700 KB). Hãy chia nhỏ bằng một thiết kế mới trước khi tiếp tục.');
  return { count, visible };
}
export async function managedPayload(data) {
  const { count } = inspectCatalog(data);
  return { schemaVersion: 2, count, sha256: await catalogHash(data), data: structuredClone(data) };
}
export async function validateManagedCatalog(payload) {
  if (payload.schemaVersion !== 2) throw new Error('Phiên bản danh mục không hỗ trợ.');
  const { count } = inspectCatalog(payload.data);
  if (payload.count !== count || payload.sha256 !== await catalogHash(payload.data)) throw new Error('Số lượng hoặc SHA-256 không khớp nội dung danh mục.');
  return payload.data;
}
export async function validateBackup(payload) {
  if (payload.schemaVersion === 1) return validateCatalog(payload);
  return validateManagedCatalog(payload);
}
export function visibleCatalog(data) {
  return data.filter(g => !g.hidden).map(g => ({ ...g, units: g.units.filter(u => !u.hidden).map(u => ({ ...u, lessons: u.lessons.filter(l => !l.hidden) })) }));
}
