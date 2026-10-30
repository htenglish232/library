import {MAX_IMPORT_BYTES, CATEGORY_LABELS, LocalRepository, validateSets, importText, createSession, currentCard, move, shuffle, cardsForScope, loadPack, addNewPacks} from './core.js';
import {QuestionAudio, QuestionTimer} from './media.js';

const $ = id => document.getElementById(id);
const storageWarning = () => {
  $('storage-warning').hidden = false;
  $('storage-warning').textContent = 'Không thể đọc/lưu đầy đủ dữ liệu cục bộ. Nội dung hiện tại vẫn dùng được trong phiên này. Hãy xuất JSON trước khi đóng trang.';
};
let storage;
try { storage = window.localStorage; } catch { storageWarning(); storage = {getItem: () => null, setItem: () => { throw new Error('Storage unavailable'); }}; }
const repository = new LocalRepository(storage, storageWarning);
const storedSettings = repository.read('settings', {});
let settings = {rate: 1, images: true, timer: false, duration: 30};
if (storedSettings && typeof storedSettings === 'object') {
  if ([0.75, 1, 1.25].includes(storedSettings.rate)) settings.rate = storedSettings.rate;
  if (typeof storedSettings.images === 'boolean') settings.images = storedSettings.images;
  if (typeof storedSettings.timer === 'boolean') settings.timer = storedSettings.timer;
  if ([15, 30, 45, 60].includes(storedSettings.duration)) settings.duration = storedSettings.duration;
}
let progress = repository.read('progress', {});
if (!progress || typeof progress !== 'object' || Array.isArray(progress)) progress = {};
let sets = [], session = null, pendingSet = null, editingSetId = null, editingCardId = null;
let loadedPackIds = [];
let browse = readBrowse();
function readBrowse() {
  const params = new URLSearchParams(location.hash.slice(1));
  return {grade: params.get('grade'), textbook: params.get('textbook'), unit: params.get('unit')};
}
function setBrowse(next) {
  browse = next;
  const params = new URLSearchParams();
  for (const key of ['grade', 'textbook', 'unit']) if (browse[key]) params.set(key, browse[key]);
  history.replaceState(null, '', location.pathname + location.search + (params.size ? '#' + params : ''));
  renderLibrary();
}
function resetFilters() {
  $('search').value = '';
  for (const key of ['grade', 'textbook', 'unit']) $(key + '-filter').value = '';
}
function allGrades() { resetFilters(); setBrowse({grade: null, textbook: null, unit: null}); }
window.addEventListener('hashchange', () => { browse = readBrowse(); renderLibrary(); });
let toastTimeout, confirmAction = null, beepContext;
let turning = false, turnVersion = 0, turnAnimation = null;
const audio = new QuestionAudio({status: message => { $('audio-status').textContent = message; }});
const timer = new QuestionTimer((seconds, running) => {
  $('timer-readout').textContent = `${seconds}s`;
  $('timer-pause').textContent = running ? 'Tạm dừng' : 'Tiếp tục';
  $('timer-pause').disabled = seconds === 0;
  $('presentation-timer').textContent = seconds ? ` · ${seconds}s` : ' · Hết giờ';
}, () => {
  $('timer-panel').classList.add('expired');
  $('timer-message').textContent = 'Hết giờ! Giáo viên chọn thời điểm chuyển câu.';
  try {
    if (beepContext?.state === 'running') {
      const oscillator = beepContext.createOscillator(), gain = beepContext.createGain();
      oscillator.connect(gain); gain.connect(beepContext.destination); oscillator.frequency.value = 660;
      gain.gain.setValueAtTime(0.12, beepContext.currentTime); gain.gain.exponentialRampToValueAtTime(0.001, beepContext.currentTime + 0.35);
      oscillator.start(); oscillator.stop(beepContext.currentTime + 0.35);
    }
  } catch { /* Visible notification remains available without audio output. */ }
});
function unlockBeep() {
  try {
    const Context = window.AudioContext || window.webkitAudioContext;
    if (Context && !beepContext) beepContext = new Context();
    beepContext?.resume().catch(() => {});
  } catch { /* Optional notification sound. */ }
}
function toast(message) { clearTimeout(toastTimeout); $('toast').textContent = message; $('toast').hidden = false; toastTimeout = setTimeout(() => { $('toast').hidden = true; }, 5000); }
function element(tag, className, text) { const node = document.createElement(tag); if (className) node.className = className; if (text !== undefined) node.textContent = text; return node; }
function action(label, onClick, className = '') { const button = element('button', className, label); button.type = 'button'; button.onclick = onClick; return button; }
function saveSets(next) {
  sets = validateSets(next);
  const saved = repository.write('sets', sets);
  if (saved) repository.write('known-packs', loadedPackIds);
  renderLibrary();
  toast(saved ? 'Đã lưu trên thiết bị. Hãy xuất JSON để có bản sao lưu.' : 'Chỉ lưu được trong phiên này. Hãy xuất JSON ngay để giữ nội dung.');
}
function saveSettings() { repository.write('settings', settings); }
function saveProgress() {
  if (session?.mode !== 'practice') return;
  // Own properties only; imported IDs can never alter an object's prototype.
  Object.defineProperty(progress, session.set.id, {value: {sequence: session.sequence, cursor: session.cursor}, enumerable: true, configurable: true, writable: true});
  repository.write('progress', progress);
}
function refreshFilters() {
  for (const [id, field, label] of [['grade-filter', 'grade', 'Tất cả lớp'], ['textbook-filter', 'textbook', 'Tất cả giáo trình'], ['unit-filter', 'unit', 'Tất cả Unit']]) {
    const select = $(id), selected = select.value;
    select.replaceChildren(new Option(label, ''));
    [...new Set(sets.map(s => s[field]))].sort((a, b) => a.localeCompare(b, 'vi', {numeric: true})).forEach(value => select.add(new Option(value, value)));
    if ([...select.options].some(o => o.value === selected)) select.value = selected;
  }
}
function renderLibrary() {
  refreshFilters();
  const query = $('search').value.trim().toLocaleLowerCase('vi');
  const shown = sets.filter(set => ['grade', 'textbook', 'unit'].every(field => !$(field + '-filter').value || set[field] === $(field + '-filter').value) && `${set.title} ${set.grade} ${set.textbook} ${set.unit}`.toLocaleLowerCase('vi').includes(query));
  const filtering = !!query || ['grade', 'textbook', 'unit'].some(key => $(key + '-filter').value);
  const branch = shown.filter(set => filtering || (set.cards.length > 0 && ['grade', 'textbook', 'unit'].every(key => !browse[key] || browse[key] === set[key])));
  const showDecks = filtering || !!browse.unit;
  $('set-list').hidden = !showDecks;
  $('browse-folders').hidden = showDecks;
  $('browse-folders').replaceChildren();
  const gradeHome = action('Danh sách Grade', allGrades); gradeHome.id = 'all-grades';
  $('browse-trail').replaceChildren(gradeHome);
  if (!filtering) {
    if (browse.grade) $('browse-trail').append(element('span', '', '›'), action(browse.grade, () => setBrowse({grade: browse.grade, textbook: null, unit: null})));
    if (browse.textbook) $('browse-trail').append(element('span', '', '›'), action(browse.textbook, () => setBrowse({...browse, unit: null})));
    if (browse.unit) $('browse-trail').append(element('span', '', '›'), element('strong', '', browse.unit));
  } else $('browse-trail').append(element('span', '', '› Kết quả tìm kiếm / lọc'));
  if (!showDecks) {
    const level = !browse.grade ? 'grade' : !browse.textbook ? 'textbook' : 'unit';
    const groups = [...new Set(branch.map(set => set[level]))].sort((a,b) => a.localeCompare(b,'vi',{numeric:true}));
    for (const name of groups) {
      const children = branch.filter(set => set[level] === name);
      const button = action('', () => setBrowse({...browse, [level]: name}), 'browse-folder');
      button.dataset[level] = name;
      button.setAttribute('aria-label', `Mở ${name}`);
      const count = children.reduce((sum,set) => sum + set.cards.length, 0);
      button.append(element('span','folder-symbol','▰'),element('h3','',name),element('p','muted',`${new Set(children.map(set => set.unit)).size} Unit · ${count} Speaking Cards`),element('span','folder-open','Mở thư mục →'));
      $('browse-folders').append(button);
    }
  }
  $('set-list').replaceChildren();
  for (const set of showDecks ? branch : []) {
    const tile = element('article', 'set-tile');
    tile.dataset.setId = set.id;
    const top = element('div', 'tile-top'); top.append(element('span', 'tile-icon', '☏'), element('span', 'tile-badge', set.id === 'demo-grade3-global-success' ? 'DEMO · A1' : 'SPEAKING CARDS'));
    const buttons = element('div', 'tile-actions');
    const practice = action('Practice →', () => startSession(set, 'practice'), 'primary');
    const sequential = action('Sequential Test', () => openTest(set, 'sequential'));
    const random = action('Random Test', () => openTest(set, 'random'));
    practice.disabled = sequential.disabled = random.disabled = set.cards.length === 0;
    buttons.append(practice, sequential, random);
    tile.append(top, element('h3', '', set.title), element('div', 'tile-path', `${set.grade} › ${set.textbook} › ${set.unit}`), element('p', 'tile-count', `${set.cards.length} câu hỏi · ${set.cards.length ? 'Sẵn sàng trò chuyện' : 'Thêm câu hỏi để bắt đầu'}`), buttons, action('Chỉnh sửa bộ thẻ', () => openEditor(set.id), 'tile-manage'));
    const categories = element('div', 'category-list');
    for (const [category, label] of Object.entries(CATEGORY_LABELS)) {
      const count = set.cards.filter(card => card.category === category).length;
      if (count) categories.append(element('span', `category-badge ${category}`, `${label} · ${count}`));
    }
    if (categories.childElementCount) tile.insertBefore(categories, buttons);
    $('set-list').append(tile);
  }
  $('library-count').textContent = `${branch.length} / ${sets.length} bộ thẻ · ${branch.reduce((sum, s) => sum + s.cards.length, 0)} câu hỏi`;
  $('empty-library').hidden = branch.length !== 0;
}
function openTest(set, order = 'sequential') {
  pendingSet = set;
  $('test-form').querySelector(`input[name="test-order"][value="${order}"]`).checked = true;
  $('setup-images').checked = settings.images; $('setup-timer').checked = settings.timer; $('setup-duration').value = settings.duration;
  $('setup-scope-label').hidden = !set.cards.some(card => card.category === 'unit5');
  $('setup-scope').replaceChildren(new Option(`Toàn bộ ${set.cards.length} thẻ`, 'all'));
  const coreCount = cardsForScope(set, 'unit5').length;
  if (coreCount) $('setup-scope').add(new Option(`Unit 5 Core · ${coreCount} thẻ`, 'unit5'));
  $('test-dialog').showModal();
}
function syncSettingsUI() {
  $('speech-rate').value = settings.rate; $('show-images').checked = settings.images;
  $('timer-enabled').checked = settings.timer; $('timer-duration').value = settings.duration;
  $('timer-duration').disabled = !settings.timer;
}
function startSession(set, mode, order = 'sequential', scope = 'all') {
  cancelTurn();
  try { session = createSession(set, mode, order, Object.hasOwn(progress, set.id) ? progress[set.id] : null, scope); }
  catch (error) { toast(error.message); return; }
  $('library-view').hidden = true; $('player-view').hidden = false; document.body.classList.add('playing');
  $('session-title').textContent = set.title;
  $('session-mode').textContent = mode === 'practice' ? 'PRACTICE · LITTLE STEPS, BIG CONFIDENCE' : order === 'random' ? 'RANDOM TEST · KIỂM TRA NGẪU NHIÊN' : 'SEQUENTIAL TEST · KIỂM TRA THEO THỨ TỰ';
  $('session-meta').textContent = `${set.grade} · ${set.textbook} · ${set.unit}${scope === 'unit5' ? ' · Chỉ Unit 5 Core' : ''}`;
  $('presentation-label').textContent = `${mode === 'practice' ? 'Practice' : order === 'random' ? 'Random Test' : 'Sequential Test'} · ${set.unit}`;
  $('practice-options').hidden = mode !== 'practice'; $('test-options').hidden = mode !== 'test';
  $('restart-test').textContent = order === 'random' ? 'Restart & Reshuffle' : 'Bắt đầu lại lượt';
  syncSettingsUI(); window.scrollTo(0, 0); renderCard();
}
function renderCard() {
  audio.stop(); $('audio-status').textContent = ''; $('session-notice').textContent = '';
  const card = currentCard(session), isTest = session.mode === 'test';
  $('speaking-card').dataset.cardId = card.id;
  $('question').textContent = card.question;
  $('card-category').textContent = `${session.set.grade} / ${session.set.unit}`;
  $('card-group').textContent = CATEGORY_LABELS[card.category] || '';
  $('card-group').className = `category-badge ${card.category || ''}`;
  $('card-group').hidden = !card.category;
  $('sample-answer').textContent = card.sampleAnswer;
  $('keywords').textContent = card.keywords.length ? `Useful words: ${card.keywords.join(' · ')}` : '';
  $('keywords').hidden = card.keywords.length === 0;
  $('answer-panel').hidden = isTest;
  $('toggle-answer').hidden = !isTest;
  $('toggle-answer').setAttribute('aria-expanded', String(!isTest));
  $('toggle-answer').textContent = 'Reveal Answer';
  renderImage();
  $('card-position').textContent = `Câu ${session.cursor + 1} / ${session.sequence.length}`;
  syncNavigation();
  $('test-progress').textContent = isTest ? `Đã xem ${session.seen.size} · Còn ${session.sequence.length - session.seen.size}` : 'Một câu hỏi, một chút tự tin.';
  $('session-progress').max = session.sequence.length; $('session-progress').value = isTest ? session.seen.size : session.cursor + 1;
  if (session.cursor === session.sequence.length - 1) $('session-notice').textContent = isTest ? 'Đây là câu cuối của lượt kiểm tra. Có thể quay lại hoặc bắt đầu lượt mới.' : 'Bạn đã đến câu cuối. Thật tuyệt!';
  resetTimer(); if (turning) timer.stop(); saveProgress();
  if (!card.audio && !window.speechSynthesis) $('audio-status').textContent = 'Thiết bị không hỗ trợ giọng đọc. Bạn vẫn có thể dùng thẻ bình thường.';
  if (!turning) $('question').focus({preventScroll: true});
  fitPresentation();
}
function renderImage() {
  const card = currentCard(session), img = $('question-image');
  $('speaking-card').classList.toggle('has-image', !!card.image && settings.images);
  $('question-figure').hidden = !card.image || !settings.images;
  img.removeAttribute('src');
  if (card.image && settings.images) { img.referrerPolicy = 'no-referrer'; img.alt = `Minh họa: ${card.question}`; img.src = card.image; }
}
$('question-image').onerror = () => { $('question-figure').hidden = true; $('session-notice').textContent = 'Không tải được hình minh họa. Bạn vẫn có thể trả lời câu hỏi.'; };
function toggleAnswer() {
  if (session?.mode !== 'test' || turning) return;
  const reveal = $('answer-panel').hidden;
  $('answer-panel').hidden = !reveal; $('toggle-answer').setAttribute('aria-expanded', String(reveal));
  $('toggle-answer').textContent = reveal ? 'Hide Answer' : session.mode === 'test' ? 'Reveal Answer' : 'Show Answer';
  fitPresentation();
}
function resetTimer() {
  const enabled = session?.mode === 'test' && settings.timer;
  $('timer-panel').hidden = !enabled; $('timer-message').textContent = ''; $('timer-panel').classList.remove('expired');
  $('presentation-timer').hidden = !enabled;
  timer.reset(settings.duration, enabled);
}
async function fullscreen() {
  try {
    if (document.fullscreenElement) await document.exitFullscreen();
    else if ($('presentation').requestFullscreen) await $('presentation').requestFullscreen();
    else toast('Trình duyệt chưa hỗ trợ toàn màn hình. Có thể dùng chế độ trình chiếu của thiết bị.');
  } catch { toast('Không mở được toàn màn hình. Hãy thử nút toàn màn hình của trình duyệt.'); }
}
function syncNavigation() {
  $('previous-card').disabled = turning || !session || session.cursor === 0;
  $('next-card').disabled = turning || !session || session.cursor === session.sequence.length - 1;
  for (const id of ['first-card', 'shuffle-practice', 'restart-test']) $(id).disabled = turning;
}
function cancelTurn() {
  turnVersion++; turnAnimation?.cancel(); turnAnimation = null; turning = false;
  $('card-stage').inert = false; $('card-stage').setAttribute('aria-busy', 'false');
}
async function navigate(delta) {
  if (!session || turning || session.cursor + delta < 0 || session.cursor + delta >= session.sequence.length) return;
  const version = ++turnVersion, activeSession = session;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches || !$('speaking-card').animate;
  turning = true; syncNavigation(); audio.stop(); $('audio-status').textContent = ''; timer.stop();
  $('card-stage').inert = true; $('card-stage').setAttribute('aria-busy', 'true');
  // Warm the next image without changing the visible card or playing audio.
  const next = session.set.cards.find(card => card.id === session.sequence[session.cursor + delta]);
  if (next.image && settings.images) { const preload = new Image(); preload.src = next.image; }
  const animate = async (from, to) => {
    turnAnimation = $('speaking-card').animate([{transform:`rotateY(${from}deg)`},{transform:`rotateY(${to}deg)`}],
      {duration:260,easing:'cubic-bezier(.45, 0, .55, 1)',fill:'both'});
    await turnAnimation.finished;
  };
  try {
    if (!reduced) await animate(0, delta > 0 ? -90 : 90);
    if (version !== turnVersion || session !== activeSession) return;
    move(session, delta); renderCard();
    if (!reduced) {
      const outgoing = turnAnimation;
      // Start the incoming face at the opposite edge before dropping the old
      // animation, so the content swap is never painted facing the audience.
      const incoming = animate(delta > 0 ? 90 : -90, 0);
      outgoing.cancel();
      await incoming;
    }
  } catch (error) {
    if (version === turnVersion && error.name !== 'AbortError') toast('Không chạy được hiệu ứng trên thiết bị này. Bạn vẫn có thể chuyển câu.');
  } finally {
    if (version === turnVersion) {
      turnAnimation?.cancel(); turnAnimation = null; turning = false;
      $('card-stage').inert = false; $('card-stage').setAttribute('aria-busy', 'false'); syncNavigation();
      resetTimer(); $('question').focus({preventScroll:true}); fitPresentation();
    }
  }
}
function fitPresentation() {
  const question = $('question'), answer = $('sample-answer');
  question.style.removeProperty('font-size'); answer.style.removeProperty('font-size');
  if (document.fullscreenElement !== $('presentation')) return;
  const body = $('question').closest('.question-body');
  // Preserve readable large type for normal cards; shrink unusually long
  // teacher text to fit, with a scrollable text area as the final fallback.
  let q = parseFloat(getComputedStyle(question).fontSize), a = parseFloat(getComputedStyle(answer).fontSize);
  for (let i=0; i<18 && body.scrollHeight > body.clientHeight + 2 && q>22; i++) {
    q = Math.max(22,q*.93); a = Math.max(20,a*.93);
    question.style.fontSize = `${q}px`; answer.style.fontSize = `${a}px`;
  }
}
new ResizeObserver(() => { if (session) fitPresentation(); }).observe($('presentation'));
document.fonts.ready.then(() => { if (session) fitPresentation(); });
window.addEventListener('resize', () => { if (session) fitPresentation(); });
function confirmChange(message, callback) { confirmAction = callback; $('confirm-message').textContent = message; $('confirm-dialog').showModal(); }
$('confirm-accept').onclick = () => { const callback = confirmAction; confirmAction = null; $('confirm-dialog').close(); callback?.(); };
$('confirm-cancel').onclick = () => { confirmAction = null; $('confirm-dialog').close(); };
$('confirm-dialog').addEventListener('cancel', () => { confirmAction = null; });

const editingSet = () => sets.find(set => set.id === editingSetId);
function openEditor(id = null) {
  editingSetId = id; $('editor-error').textContent = '';
  const set = editingSet();
  for (const field of ['title', 'grade', 'textbook', 'unit']) $('set-' + field).value = set?.[field] || '';
  $('editor-title').textContent = set ? 'Quản lý bộ thẻ' : 'Tạo bộ thẻ mới';
  renderEditorCards(); selectCard(null); $('editor-dialog').showModal();
}
function renderEditorCards() {
  const set = editingSet(); $('editor-cards').replaceChildren();
  for (const card of set?.cards || []) {
    const item = element('li'); const button = action(card.question, () => selectCard(card.id));
    button.setAttribute('aria-current', String(card.id === editingCardId)); item.append(button); $('editor-cards').append(item);
  }
  $('add-card').disabled = $('export-set').disabled = $('delete-set').disabled = !set;
  $('card-form').querySelectorAll('input,textarea,select,button').forEach(control => { control.disabled = !set; });
  if (!set) $('editor-error').textContent = 'Lưu thông tin bộ thẻ trước, sau đó thêm câu hỏi.';
}
function selectCard(id) {
  editingCardId = id; const card = editingSet()?.cards.find(c => c.id === id);
  $('card-form-title').textContent = card ? 'Chỉnh sửa thẻ' : 'Thêm thẻ';
  $('edit-question').value = card?.question || ''; $('edit-answer').value = card?.sampleAnswer || '';
  $('edit-keywords').value = card?.keywords.join(' | ') || ''; $('edit-image').value = card?.image || ''; $('edit-audio').value = card?.audio || '';
  $('edit-category').value = card?.category || '';
  $('delete-card').hidden = !card;
  if (editingSet()) $('editor-error').textContent = '';
  renderEditorCards();
}
function exportJSON(selected, name) {
  const blob = new Blob([JSON.stringify({schemaVersion: 1, exportedAt: new Date().toISOString(), sets: selected}, null, 2) + '\n'], {type: 'application/json;charset=utf-8'});
  const url = URL.createObjectURL(blob), link = element('a'); link.href = url; link.download = name; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  toast('Đã tạo tệp JSON. Hãy lưu tệp ở nơi an toàn.');
}
const newId = prefix => `${prefix}-${crypto.randomUUID?.() || Date.now() + '-' + Math.random().toString(36).slice(2)}`;
$('set-form').onsubmit = event => {
  event.preventDefault();
  try {
    const set = {...editingSet(), id: editingSetId || newId('set'), cards: editingSet()?.cards || []};
    for (const field of ['title', 'grade', 'textbook', 'unit']) set[field] = $('set-' + field).value;
    saveSets([...sets.filter(s => s.id !== set.id), set]); editingSetId = set.id;
    $('editor-title').textContent = 'Quản lý bộ thẻ'; $('editor-error').textContent = ''; renderEditorCards();
  } catch (error) { $('editor-error').textContent = error.message; }
};
$('card-form').onsubmit = event => {
  event.preventDefault(); const set = editingSet(); if (!set) return;
  try {
    const card = {id: editingCardId || newId('card'), question: $('edit-question').value, sampleAnswer: $('edit-answer').value, ...($('edit-category').value ? {category: $('edit-category').value} : {}), keywords: $('edit-keywords').value.split('|').map(k => k.trim()).filter(Boolean), image: $('edit-image').value.trim(), audio: $('edit-audio').value.trim()};
    const cards = [...set.cards]; const index = cards.findIndex(c => c.id === card.id);
    if (index < 0) cards.push(card); else cards[index] = card;
    saveSets(sets.map(s => s.id === set.id ? {...s, cards} : s)); selectCard(card.id);
  } catch (error) { $('editor-error').textContent = error.message; }
};
$('add-card').onclick = () => { selectCard(null); $('edit-question').focus(); };
$('delete-card').onclick = () => {
  const set = editingSet(), id = editingCardId;
  confirmChange('Xóa thẻ này khỏi bộ? Thao tác chỉ áp dụng trên thiết bị hiện tại. Hãy xuất JSON nếu cần giữ bản sao.', () => {
    saveSets(sets.map(s => s.id === set.id ? {...s, cards: s.cards.filter(c => c.id !== id)} : s)); selectCard(null);
  });
};
$('delete-set').onclick = () => {
  const id = editingSetId;
  confirmChange('Xóa toàn bộ bộ thẻ này trên thiết bị? Hãy xuất JSON trước nếu cần giữ bản sao.', () => { saveSets(sets.filter(s => s.id !== id)); $('editor-dialog').close(); });
};
$('import-submit').onclick = async () => {
  $('import-error').textContent = '';
  try {
    const file = $('import-file').files[0];
    if (!file) throw new Error('Hãy chọn tệp JSON hoặc CSV.');
    if (!/\.(json|csv)$/i.test(file.name)) throw new Error('Chỉ nhận tệp .json hoặc .csv.');
    if (file.size > MAX_IMPORT_BYTES) throw new Error('Tệp vượt quá 2 MB.');
    const incoming = importText(await file.text(), file.name);
    if (!incoming.length) throw new Error('Tệp không chứa bộ thẻ nào.');
    const collisions = incoming.filter(s => sets.some(existing => existing.id === s.id));
    const apply = () => { try { const ids = new Set(incoming.map(s => s.id)); saveSets([...sets.filter(s => !ids.has(s.id)), ...incoming]); $('import-dialog').close(); } catch (error) { $('import-error').textContent = error.message; } };
    if (collisions.length) confirmChange(`${collisions.length} bộ thẻ trùng ID sẽ được thay thế. Các bộ khác được giữ nguyên. Bạn đã sao lưu JSON chưa?`, apply);
    else apply();
  } catch (error) { $('import-error').textContent = `Không nhập dữ liệu: ${error.message}`; }
};
$('new-set').onclick = () => openEditor();
$('export-all').onclick = () => exportJSON(sets, 'ht-speaking-cards-backup.json');
$('export-set').onclick = () => exportJSON([editingSet()], 'ht-speaking-cards-set.json');
$('import-open').onclick = () => { $('import-error').textContent = ''; $('import-file').value = ''; $('import-dialog').showModal(); };
document.querySelectorAll('[data-close]').forEach(button => { button.onclick = () => button.closest('dialog').close(); });
$('search').oninput = renderLibrary;
for (const id of ['grade-filter', 'textbook-filter', 'unit-filter']) $(id).onchange = renderLibrary;
$('test-form').onsubmit = event => {
  event.preventDefault(); settings.images = $('setup-images').checked; settings.timer = $('setup-timer').checked; settings.duration = Number($('setup-duration').value); saveSettings();
  if (settings.timer) unlockBeep();
  $('test-dialog').close(); startSession(pendingSet, 'test', new FormData($('test-form')).get('test-order'), $('setup-scope').value);
};
function leaveSession(toGrades = false) {
  cancelTurn();
  const set = session.set;
  saveProgress(); audio.stop(); timer.stop(); session = null;
  $('player-view').hidden = true; $('library-view').hidden = false; document.body.classList.remove('playing');
  if (document.fullscreenElement) document.exitFullscreen().catch(() => {});
  resetFilters();
  setBrowse(toGrades ? {grade:null,textbook:null,unit:null} : {grade:set.grade,textbook:set.textbook,unit:null});
  window.scrollTo(0, 0); $('library-title').setAttribute('tabindex', '-1'); $('library-title').focus({preventScroll: true});
}
$('exit-session').onclick = () => leaveSession();
$('session-grades').onclick = () => leaveSession(true);
$('previous-card').onclick = () => navigate(-1); $('next-card').onclick = () => navigate(1);
$('toggle-answer').onclick = toggleAnswer;
$('play-audio').onclick = () => audio.play(currentCard(session), settings.rate);
$('fullscreen').onclick = fullscreen;
$('exit-fullscreen').onclick = () => { if (document.fullscreenElement) document.exitFullscreen().catch(() => {}); };
document.addEventListener('fullscreenchange', () => {
  $('fullscreen').setAttribute('aria-pressed', String(document.fullscreenElement === $('presentation')));
  fitPresentation();
});
$('speech-rate').onchange = () => { settings.rate = Number($('speech-rate').value); saveSettings(); audio.stop(); $('audio-status').textContent = ''; };
$('show-images').onchange = () => { settings.images = $('show-images').checked; saveSettings(); renderImage(); };
$('timer-enabled').onchange = () => { settings.timer = $('timer-enabled').checked; if (settings.timer) unlockBeep(); saveSettings(); syncSettingsUI(); resetTimer(); };
$('timer-duration').onchange = () => { settings.duration = Number($('timer-duration').value); saveSettings(); resetTimer(); };
$('timer-pause').onclick = () => { if (timer.running) timer.pause(); else timer.resume(); };
$('timer-reset').onclick = () => { unlockBeep(); resetTimer(); };
$('first-card').onclick = () => { session.cursor = 0; renderCard(); };
$('shuffle-practice').onclick = () => { session.sequence = shuffle(session.sequence); session.cursor = 0; renderCard(); toast('Đã trộn câu hỏi và quay về câu đầu.'); };
$('restart-test').onclick = () => confirmChange('Bắt đầu một lượt kiểm tra mới? Lượt hiện tại sẽ kết thúc.', () => { const {set, mode, order, scope} = session; startSession(set, mode, order, scope); if (settings.timer) unlockBeep(); });
document.addEventListener('keydown', event => {
  if (!session || event.repeat || event.altKey || event.ctrlKey || event.metaKey || document.querySelector('dialog[open]')) return;
  if (event.target.closest('input,textarea,select,[contenteditable="true"]')) return;
  const key = event.key.toLowerCase();
  if (key === ' ' && event.target.closest('button,a')) return;
  const shortcuts = {'arrowright': () => navigate(1), 'arrowleft': () => navigate(-1), ' ': () => { if (!turning) audio.play(currentCard(session), settings.rate); }, a: toggleAnswer, f: fullscreen,
    escape: () => { if (document.fullscreenElement) document.exitFullscreen().catch(() => {}); }};
  if (shortcuts[key]) { event.preventDefault(); shortcuts[key](); }
});
window.addEventListener('pagehide', () => { cancelTurn(); saveProgress(); audio.stop(); timer.stop(); });
window.addEventListener('pageshow', event => { if (event.persisted && session) renderCard(); });
document.addEventListener('visibilitychange', () => { if (document.hidden) audio.stop(); else if (session) timer.tick(); });

async function init() {
  try {
    const paths = ['./data/sets.json', './data/global3-unit5/unit5_speaking_cards.json'];
    const [baseData, unit5Data] = await Promise.all(paths.map(async path => {
      const response = await fetch(path); if (!response.ok) throw new Error(`Không tải được ${path}.`); return response.json();
    }));
    const packs = [loadPack(unit5Data, './data/global3-unit5/')];
    loadedPackIds = packs.map(pack => pack.id);
    const baseline = validateSets([...validateSets(baseData), ...packs]);
    const saved = repository.read('sets', null);
    try {
      const known = repository.read('known-packs', []);
      sets = saved === null ? baseline : addNewPacks(validateSets(saved), packs, Array.isArray(known) ? known : []);
    }
    catch { sets = baseline; storageWarning(); }
    renderLibrary();
  } catch (error) {
    $('library-count').textContent = `Không tải được bộ demo: ${error.message} Hãy mở ứng dụng qua máy chủ HTTP. Bạn vẫn có thể tạo hoặc nhập bộ thẻ.`;
  }
}
init();
