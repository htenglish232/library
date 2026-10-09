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
  return validateCatalog({ ...fields, data: JSON.parse(fields.dataJson) });
}
