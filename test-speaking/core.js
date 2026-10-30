export const MAX_IMPORT_BYTES = 2 * 1024 * 1024;
export const CATEGORY_LABELS = {review: 'Review', extension: 'Extension', unit5: 'Unit 5 Core'};
const text = (value, field, max, optional = false) => {
  if (optional && (value === undefined || value === null || value === '')) return '';
  if (typeof value !== 'string' || !value.trim() || value.length > max) throw new Error(`${field}: cần văn bản từ 1 đến ${max} ký tự.`);
  return value.trim();
};
export function mediaPath(value) {
  const path = text(value, 'Hình/âm thanh', 2000, true);
  if (!path) return '';
  if (/[\u0000-\u0020\\]/.test(path) || path.startsWith('//')) throw new Error('Đường dẫn media không hợp lệ. Hãy dùng đường dẫn tương đối hoặc HTTPS.');
  const url = new URL(path, 'https://example.test/test-speaking/');
  if (!['https:', 'http:'].includes(url.protocol) || url.username || url.password) throw new Error('Chỉ chấp nhận media HTTP(S) hoặc đường dẫn tương đối, không kèm mật khẩu.');
  return path;
}
export function validateSets(input) {
  const raw = Array.isArray(input) ? input : input?.sets ?? [input];
  if (!Array.isArray(raw) || raw.length > 1000) throw new Error('Dữ liệu phải là danh sách tối đa 1.000 bộ thẻ.');
  const ids = new Set();
  return raw.map((set, index) => {
    if (!set || typeof set !== 'object') throw new Error(`Bộ thẻ ${index + 1} không hợp lệ.`);
    const id = text(set.id, 'ID bộ thẻ', 120);
    if (ids.has(id)) throw new Error(`Trùng ID bộ thẻ: ${id}`);
    ids.add(id);
    if (!Array.isArray(set.cards) || set.cards.length > 2000) throw new Error(`${id}: cards phải là danh sách tối đa 2.000 thẻ.`);
    const cardIds = new Set();
    const grade = Number.isInteger(set.grade) && set.grade > 0 ? `Grade ${set.grade}` : set.grade;
    const unit = Number.isInteger(set.unit) && set.unit > 0 ? `Unit ${set.unit}` : set.unit;
    return {
      id, title: text(set.title, 'Tên bộ thẻ', 200), grade: text(grade, 'Lớp', 80),
      textbook: text(set.textbook, 'Giáo trình', 120), unit: text(unit, 'Unit', 120),
      ...(set.language ? {language: text(set.language, 'Ngôn ngữ', 40)} : {}),
      ...(set.notes ? {notes: text(set.notes, 'Ghi chú bộ thẻ', 4000)} : {}),
      cards: set.cards.map(card => {
        if (!card || typeof card !== 'object') throw new Error(`${id}: thẻ không hợp lệ.`);
        const cardId = text(card.id, 'ID thẻ', 120);
        if (cardIds.has(cardId)) throw new Error(`${id}: trùng ID thẻ ${cardId}`);
        cardIds.add(cardId);
        const keywords = card.keywords ?? [];
        if (!Array.isArray(keywords) || keywords.length > 50) throw new Error(`${cardId}: keywords phải là danh sách tối đa 50 từ khóa.`);
        if (card.category && !Object.hasOwn(CATEGORY_LABELS, card.category)) throw new Error(`${cardId}: nhóm thẻ không hợp lệ.`);
        return {id: cardId, question: text(card.question, 'Câu hỏi', 2000), sampleAnswer: text(card.sampleAnswer, 'Câu trả lời mẫu', 4000),
          ...(card.category ? {category: card.category} : {}),
          keywords: keywords.map(k => text(k, 'Từ khóa', 200)), image: mediaPath(card.image), audio: mediaPath(card.audio), ...(card.answerAudio ? {answerAudio: mediaPath(card.answerAudio)} : {})};
      })
    };
  });
}
// RFC 4180-style quoted fields, escaped quotes, CRLF and multiline cells.
export function parseCSV(source) {
  source = source.replace(/^\uFEFF/, '');
  const rows = []; let row = [], cell = '', quoted = false, closed = false;
  for (let i = 0; i < source.length; i++) {
    const c = source[i];
    if (quoted) {
      if (c === '"' && source[i + 1] === '"') { cell += '"'; i++; }
      else if (c === '"') { quoted = false; closed = true; }
      else cell += c;
    } else if (c === '"') {
      if (cell || closed) throw new Error('CSV: dấu ngoặc kép không đúng vị trí.');
      quoted = true;
    } else if (c === ',' || c === '\n' || c === '\r') {
      row.push(cell); cell = ''; closed = false;
      if (c !== ',') { if (row.some(v => v.trim())) rows.push(row); row = []; if (c === '\r' && source[i + 1] === '\n') i++; }
    } else {
      if (closed) throw new Error('CSV: ký tự sau dấu ngoặc kép đóng.');
      cell += c;
    }
  }
  if (quoted) throw new Error('CSV: thiếu dấu ngoặc kép đóng.');
  row.push(cell); if (row.some(v => v.trim())) rows.push(row);
  if (rows.length < 2) throw new Error('CSV cần tiêu đề cột và ít nhất một dòng thẻ.');
  const headers = rows.shift().map(h => h.trim());
  for (const key of ['setId', 'title', 'grade', 'textbook', 'unit', 'id', 'question', 'sampleAnswer']) {
    if (!headers.includes(key)) throw new Error(`CSV thiếu cột ${key}.`);
  }
  if (new Set(headers).size !== headers.length) throw new Error('CSV có cột trùng tên.');
  const sets = new Map();
  rows.forEach((values, i) => {
    if (values.length !== headers.length) throw new Error(`CSV dòng ${i + 2}: số cột không khớp.`);
    const r = Object.fromEntries(headers.map((key, j) => [key, values[j]]));
    let set = sets.get(r.setId);
    if (!set) { set = {id: r.setId, title: r.title, grade: r.grade, textbook: r.textbook, unit: r.unit, cards: []}; sets.set(r.setId, set); }
    for (const key of ['title', 'grade', 'textbook', 'unit']) if (set[key] !== r[key]) throw new Error(`CSV dòng ${i + 2}: thông tin bộ ${r.setId} không thống nhất.`);
    set.cards.push({id: r.id, question: r.question, sampleAnswer: r.sampleAnswer, ...(r.category ? {category: r.category} : {}), keywords: (r.keywords || '').split('|').map(k => k.trim()).filter(Boolean), image: r.image || '', audio: r.audio || '', ...(r.answerAudio ? {answerAudio: r.answerAudio} : {})});
  });
  return validateSets([...sets.values()]);
}
export function importText(source, filename) {
  if (new TextEncoder().encode(source).length > MAX_IMPORT_BYTES) throw new Error('Tệp vượt quá 2 MB.');
  return filename.toLowerCase().endsWith('.csv') ? parseCSV(source) : validateSets(JSON.parse(source.replace(/^\uFEFF/, '')));
}
// Fisher–Yates: never mutate the source list or re-roll while navigating.
export function shuffle(items, random = Math.random) {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}
export function cardsForScope(set, scope = 'all') {
  if (!['all', 'unit5'].includes(scope)) throw new Error('Phạm vi kiểm tra không hợp lệ.');
  return scope === 'unit5' ? set.cards.filter(card => card.category === 'unit5') : set.cards;
}
export function createSession(set, mode, order = 'sequential', saved = null, scope = 'all') {
  const ids = cardsForScope(set, scope).map(c => c.id);
  if (!ids.length) throw new Error('Phạm vi đã chọn chưa có câu hỏi. Hãy thêm thẻ trước.');
  let sequence = mode === 'test' && order === 'random' ? shuffle(ids) : ids;
  let cursor = 0;
  if (mode === 'practice' && saved && Array.isArray(saved.sequence) && saved.sequence.length === ids.length && new Set(saved.sequence).size === ids.length && saved.sequence.every(id => ids.includes(id))) {
    sequence = [...saved.sequence]; cursor = Number.isInteger(saved.cursor) ? Math.min(Math.max(saved.cursor, 0), ids.length - 1) : 0;
  }
  return {set, mode, order, scope, sequence, cursor, seen: new Set([sequence[cursor]])};
}
export function move(session, delta) {
  const next = Math.max(0, Math.min(session.sequence.length - 1, session.cursor + delta));
  if (next === session.cursor) return false;
  session.cursor = next; session.seen.add(session.sequence[next]); return true;
}
export function currentCard(session) { return session.set.cards.find(c => c.id === session.sequence[session.cursor]); }

// Source packs retain their original JSON and media names. Only the in-memory
// media URLs are resolved relative to the pack rather than the app document.
export function loadPack(raw, directory) {
  const resolve = value => {
    const path = mediaPath(value);
    return path && !/^(?:https?:|\/)/i.test(path) ? directory + path : path;
  };
  return validateSets({...raw, cards: raw.cards.map(card => ({...card,
    image: resolve(card.image), audio: resolve(card.audio),
    ...(card.answerAudio ? {answerAudio: resolve(card.answerAudio)} : {})
  }))})[0];
}
export function addNewPacks(existing, packs, knownIds) {
  return [...existing, ...packs.filter(pack => !knownIds.includes(pack.id) && !existing.some(set => set.id === pack.id))];
}

// Storage is an adapter boundary for a future remote repository. JSON files and
// exports remain portable; no Firebase dependency or authentication is needed.
export class LocalRepository {
  constructor(storage, onFailure = () => {}) { this.storage = storage; this.onFailure = onFailure; }
  read(key, fallback) {
    try { const raw = this.storage.getItem(`ht-speaking:v1:${key}`); return raw === null ? fallback : JSON.parse(raw); }
    catch { this.onFailure(); return fallback; }
  }
  write(key, value) {
    try { this.storage.setItem(`ht-speaking:v1:${key}`, JSON.stringify(value)); return true; }
    catch { this.onFailure(); return false; }
  }
}
