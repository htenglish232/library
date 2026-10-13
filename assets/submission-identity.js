/* Local-only identity for a completed HT English exam. No storage or network requests. */
(() => {
  'use strict';
  let config, draft, attempt;
  const byId = id => id ? document.getElementById(id) : null;
  const normalize = value => String(value || '').replace(/\s+/gu, ' ').trim();
  const make = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  };
  function closeConfirmation() {
    const modals = (config.modals || []).map(byId).filter(Boolean);
    modals.filter(modal => !modals.some(parent => parent !== modal && parent.contains(modal))).forEach(modal => {
      if (modal.tagName === 'DIALOG' && modal.open) modal.close();
      else modal.classList.add('hidden');
    });
  }
  function check() {
    if (attempt) return false;
    const input = byId(config.name);
    const name = normalize(input?.value);
    const message = byId('htIdentityMessage');
    if (!name) {
      closeConfirmation();
      message.textContent = 'Em vui lòng nhập đầy đủ họ và tên trước khi nộp bài nhé!';
      message.hidden = false;
      input.setAttribute('aria-invalid', 'true');
      input.focus();
      return false;
    }
    message.hidden = true;
    message.textContent = '';
    input.removeAttribute('aria-invalid');
    return true;
  }
  function begin() {
    if (!check()) return false;
    const name = byId(config.name), studentClass = byId(config.class);
    name.value = normalize(name.value);
    if (studentClass) studentClass.value = normalize(studentClass.value);
    draft = {name: name.value, studentClass: studentClass?.value || ''};
    return true;
  }
  function submissionId() {
    const prefix = 'HT' + config.grade + '-';
    if (typeof crypto?.randomUUID === 'function') return prefix + crypto.randomUUID().replace(/-/g, '').toUpperCase();
    if (typeof crypto?.getRandomValues === 'function') {
      const values = crypto.getRandomValues(new Uint32Array(4));
      return prefix + Array.from(values, value => value.toString(16).padStart(8, '0')).join('').toUpperCase();
    }
    return prefix + Date.now().toString(36).toUpperCase() + '-' + Math.random().toString(36).slice(2).toUpperCase();
  }
  function render() {
    if (!attempt) return;
    const studentClass = attempt.studentClass || 'Chưa nhập lớp';
    byId(config.name).value = attempt.name;
    byId(config.name).disabled = true;
    if (byId(config.class)) { byId(config.class).value = attempt.studentClass; byId(config.class).disabled = true; }
    const summary = byId('htIdentitySummary');
    summary.replaceChildren();
    summary.append(make('h3', '', 'HT ENGLISH – KẾT QUẢ BÀI KIỂM TRA'));
    summary.append(make('p', 'ht-identity-greeting', 'Chúc mừng ' + attempt.name + '!'));
    summary.append(make('p', '', 'Em đã hoàn thành bài kiểm tra Tiếng Anh lớp ' + config.grade + '.'));
    const completed = new Date(attempt.completedAt);
    const time = completed.toLocaleTimeString('vi-VN', {hour:'2-digit', minute:'2-digit'}) + ' – ' + completed.toLocaleDateString('vi-VN');
    const details = make('dl', 'ht-identity-details');
    [['Học sinh', attempt.name], ['Lớp', studentClass], ['Điểm số', attempt.score + '/10'], ['Thời gian hoàn thành (giờ địa phương)', time], ['Mã bài nộp', attempt.id]].forEach(([label, value]) => {
      const item = make('div'); item.append(make('dt', '', label), make('dd', '', value)); details.append(item);
    });
    summary.append(details, make('p', 'ht-identity-completed', 'ĐÃ HOÀN THÀNH BÀI TEST'));
    summary.hidden = false;
    const review = byId('htIdentityReview');
    review.replaceChildren(make('strong', '', 'BÀI LÀM CỦA: ' + attempt.name + ' | LỚP: ' + studentClass + ' | ĐIỂM: ' + attempt.score + '/10'), make('small', '', 'HT English | Mã bài nộp: ' + attempt.id));
    review.hidden = false;
    const status = byId('htIdentityStatus');
    status.textContent = 'Đã hoàn thành: ' + attempt.name + ' | ' + attempt.id;
    status.hidden = false;
    // Preserve controls used to replay Listening during review.
    document.querySelectorAll('.listening-player,.ht-listening-player,.ht-audio-player,[data-listening-player]').forEach(player => {
      player.querySelectorAll('input,select,button').forEach(control => {
        control.disabled = false;
        control.style.pointerEvents = 'auto';
        control.classList.remove('opacity-75', 'opacity-85', 'cursor-not-allowed', 'field-disabled', 'locked-input');
      });
    });
  }
  function complete(score) {
    if (attempt) return render();
    if (!draft) return;
    const scoreText = String(score ?? document.querySelector(config.score)?.textContent ?? '').replace(',', '.');
    const match = scoreText.match(/\d+(?:\.\d+)?/);
    if (!match) throw new Error('Không đọc được điểm từ bộ chấm hiện tại.');
    attempt = Object.freeze({...draft, score: match[0], completedAt: new Date().toISOString(), id: submissionId()});
    render();
  }
  function configure(options) {
    if (config) throw new Error('Submission identity already configured.');
    config = options;
    const name = byId(config.name);
    if (!name) throw new Error('Missing configured student name field.');
    const message = make('p', 'ht-identity-message'); message.id = 'htIdentityMessage'; message.hidden = true; message.setAttribute('role', 'alert');
    name.insertAdjacentElement('afterend', message);
    name.setAttribute('aria-describedby', [name.getAttribute('aria-describedby'), message.id].filter(Boolean).join(' '));
    const summary = make('section', 'ht-identity-summary'); summary.id = 'htIdentitySummary'; summary.hidden = true;
    const result = byId(config.result);
    if (!result) throw new Error('Missing configured results container.');
    const modalPanel = result.classList.contains('fixed') ? result.firstElementChild : null;
    if (modalPanel) {
      result.classList.add('ht-identity-result-modal');
      modalPanel.classList.add('ht-identity-modal-panel');
      modalPanel.prepend(summary);
    } else {
      result.classList.add('ht-identity-result-container');
      result.prepend(summary);
    }
    const review = make('div', 'ht-identity-review'); review.id = 'htIdentityReview'; review.hidden = true;
    const root = document.querySelector('main,#examForm,#test-form,.exam-shell') || name.closest('form') || document.body;
    root.prepend(review);
    const status = make('p', 'ht-identity-status'); status.id = 'htIdentityStatus'; status.hidden = true;
    (byId(config.banner) || name.parentElement).append(status);
  }
  window.HTSubmission = Object.freeze({configure, check, begin, complete, render, get attempt() { return attempt || null; }});
})();
