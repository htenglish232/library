/* Shared Grade 7 exam interaction. Each HTML supplies its own unchanged rubric. */
'use strict';
const Grade7Exam = (() => {
  // Speech receives only the literal public text attached to a neutral button.
  // It has no reference to exam data, grading, explanations or model answers.
  function speakNeutralWord(text) {
    if (!('speechSynthesis' in window) || typeof text !== 'string') return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-GB';
    utterance.rate = 0.9;
    utterance.pitch = 1;
    const voice = window.speechSynthesis.getVoices().find(v => v.lang === 'en-GB');
    if (voice) utterance.voice = voice;
    window.speechSynthesis.speak(utterance);
  }
  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function initExistingPlayers() {
    Grade7Listening.init();
  }
  function init(normalize) {
    initExistingPlayers();
    const data = JSON.parse(document.getElementById('examData').textContent);
    let isSubmitted = false;
    const rearrangeState = Object.create(null);
    const cards = new Map(data.questions.map(q => [q.id, document.getElementById('question-' + q.id)]));
    const modal = document.getElementById('confirmModal');
    const submit = document.getElementById('submitBtn');
    const confirm = document.getElementById('confirmSubmit');
    const continueButton = document.getElementById('continueExam');
    const today = new Date();
    document.getElementById('examDate').value = [today.getFullYear(), String(today.getMonth() + 1).padStart(2, '0'), String(today.getDate()).padStart(2, '0')].join('-');
    function fields(q) {
      return [...cards.get(q.id).querySelectorAll('[data-answer-field]')];
    }
    function sentence(q) {
      const selected = rearrangeState[q.id];
      return selected.length ? selected.map(index => q.tokens[index]).join(' ') + q.punctuation : '';
    }
    function readResponse(q) {
      if (q.kind === 'chips') return sentence(q);
      const inputs = fields(q);
      if (q.kind === 'choice') return inputs.find(input => input.checked)?.value || '';
      if (q.parts) return inputs.map(input => input.value.trim()).join(' | ');
      return inputs[0]?.value.trim() || '';
    }
    function completed(q) {
      if (q.kind === 'chips') return rearrangeState[q.id].length === q.tokens.length;
      return fields(q).length > 0 && (q.kind === 'choice' ? !!readResponse(q) : fields(q).every(f => f.value.trim()));
    }
    function renderChips(q) {
      const card = cards.get(q.id);
      const assembled = card.querySelector('.assembled-sentence');
      const bank = card.querySelector('.word-bank');
      assembled.replaceChildren();
      bank.replaceChildren();
      if (!rearrangeState[q.id].length) {
        assembled.append(element('span', 'chip-placeholder', 'Bấm chọn các từ bên dưới theo thứ tự để ghép câu...'));
      }
      rearrangeState[q.id].forEach((index, position) => {
        const chip = element('button', 'word-chip selected-chip', q.tokens[index] + ' ✕');
        chip.type = 'button';
        chip.disabled = isSubmitted;
        chip.setAttribute('aria-label', 'Bỏ từ ' + q.tokens[index]);
        chip.addEventListener('click', () => {
          if (isSubmitted) return;
          rearrangeState[q.id].splice(position, 1);
          renderChips(q);
        });
        assembled.append(chip);
      });
      q.tokens.forEach((text, index) => {
        const chip = element('button', 'word-chip bank-chip', text);
        chip.type = 'button';
        chip.dataset.tokenIndex = String(index);
        chip.disabled = isSubmitted || rearrangeState[q.id].includes(index);
        chip.addEventListener('click', () => {
          if (isSubmitted || rearrangeState[q.id].includes(index)) return;
          rearrangeState[q.id].push(index);
          renderChips(q);
        });
        bank.append(chip);
      });
      card.querySelectorAll('.chip-actions button').forEach(button => { button.disabled = isSubmitted; });
    }
    data.questions.forEach(q => {
      const card = cards.get(q.id);
      if (!card) throw new Error('Missing question card: ' + q.id);
      if (q.kind === 'chips') {
        rearrangeState[q.id] = [];
        card.querySelector('[data-action="undo"]').addEventListener('click', () => {
          if (isSubmitted) return;
          rearrangeState[q.id].pop();
          renderChips(q);
        });
        card.querySelector('[data-action="reset"]').addEventListener('click', () => {
          if (isSubmitted) return;
          rearrangeState[q.id] = [];
          renderChips(q);
        });
        renderChips(q);
      }
      // Neutral speakers are built from visible option labels, without consulting the rubric.
      // Exclude Listening, Reading, true/false and any sentence or long phrase.
      if (q.kind === 'choice' && q.section === 1) {
        const labels = [...card.querySelectorAll('.option-box')];
        const texts = labels.map(label => label.textContent.trim().replace(/^[A-D][.)]\s*/, ''));
        const safe = texts.length >= 2 && texts.every(text => /^[A-Za-z][A-Za-z'’ -]*$/.test(text) && text.split(/\s+/).length === 1 && text.length <= 32);
        if (safe) labels.forEach((label, index) => {
          const button = element('button', 'neutral-speaker', '🔊');
          button.type = 'button';
          button.dataset.speechText = texts[index];
          button.setAttribute('aria-label', 'Phát âm: ' + texts[index]);
          button.addEventListener('click', event => {
            event.preventDefault();
            event.stopPropagation();
            speakNeutralWord(button.dataset.speechText);
          });
          label.append(button);
        });
      }
    });
    function matches(q, raw) {
      if (!raw) return false;
      if (q.kind === 'choice') return q.accepted.includes(raw);
      if (q.parts) return fields(q).every((f, i) => q.parts[i].includes(f.value.trim().toLowerCase()));
      let value = normalize(raw);
      if (q.prefix && value.startsWith(normalize(q.prefix))) value = value.slice(normalize(q.prefix).length).trim();
      if (q.match === 'startsYes') return value.startsWith('yes');
      if (q.groups) return q.groups.every(group => group.some(word => value.includes(normalize(word))));
      return q.accepted.some(answer => {
        const expected = normalize(String(answer));
        if (q.match === 'contains') return value.includes(expected.replace(/\./g, ''));
        if (q.match === 'overlap') return value === expected || (value.length > 5 && expected.includes(value)) || (expected.length > 5 && value.includes(expected));
        return value === expected;
      });
    }
    function showFeedback(q, raw, right) {
      const card = cards.get(q.id);
      card.classList.add(right ? 'answer-correct' : 'answer-wrong');
      const status = card.querySelector('.status-indicator');
      status.hidden = false;
      status.textContent = right ? 'Đúng' : 'Sai';
      const box = card.querySelector('.feedback-box');
      box.hidden = false;
      const ownLabel = q.kind === 'chips' ? 'Câu em đã sắp xếp: ' : 'Đáp án học sinh: ';
      box.append(element('p', '', ownLabel + (raw || 'Chưa trả lời')));
      let display = q.display;
      if (q.kind === 'choice') {
        const texts = q.accepted.map(answer => {
          const input = fields(q).find(f => f.value === answer);
          const label = input?.closest('label');
          return label ? label.textContent.trim().replace(/🔊/g, '').trim() : answer;
        });
        display = texts.join(' / ');
      }
      box.append(element('p', 'correct-response', 'Đáp án đúng: ' + display));
      const explanation = element('div', 'explanation');
      // Only trusted, repository-provided explanation markup is rendered as HTML.
      explanation.innerHTML = '<strong>Giải thích: </strong>' + q.explanation;
      box.append(explanation);
    }
    function closeModal() { modal.close(); submit.focus(); }
    function openModal() {
      if (isSubmitted) return;
      const unanswered = data.questions.filter(q => !completed(q)).length;
      document.getElementById('confirmMessage').textContent = unanswered
        ? `Bạn vẫn còn ${unanswered} câu hỏi chưa hoàn thành. Bạn có muốn nộp bài không?`
        : 'Bạn có chắc chắn muốn nộp bài không? Sau khi nộp bài, bạn sẽ không thể thay đổi đáp án.';
      modal.showModal();
      continueButton.focus();
    }
    function grade() {
      if (isSubmitted || !modal.open) return;
      const responses = data.questions.map(q => readResponse(q));
      isSubmitted = true;
      modal.close();
      let points = 0;
      let rightCount = 0;
      data.questions.forEach((q, index) => {
        const right = matches(q, responses[index]);
        if (right) { points += q.points; rightCount++; }
        showFeedback(q, responses[index], right);
        if (q.kind === 'chips') renderChips(q);
      });
      document.querySelectorAll('.exam-shell input,.exam-shell textarea,.exam-shell select,.chip-actions button').forEach(control => { if (!control.closest('.listening-player')) control.disabled = true; });
      submit.disabled = true;
      document.getElementById('submissionBanner').hidden = false;
      const results = document.getElementById('examResults');
      results.hidden = false;
      results.append(element('h2', '', `Điểm: ${points.toFixed(2).replace(/0$/, '')} / ${data.maxScore}`));
      results.append(element('p', '', `Số câu đúng: ${rightCount} • Số câu sai: ${data.questions.length - rightCount} • Tổng: ${data.questions.length} câu`));
      document.querySelectorAll('[data-transcript]').forEach((transcript, index) => {
        transcript.classList.remove('hidden');
        transcript.hidden = false;
        const toggle = element('button', 'transcript-toggle', 'Ẩn / Hiện transcript');
        toggle.type = 'button';
        const transcriptId = 'review-transcript-' + index;
        transcript.id = transcriptId;
        toggle.setAttribute('aria-controls', transcriptId);
        toggle.setAttribute('aria-expanded', 'true');
        toggle.addEventListener('click', () => {
          if (!isSubmitted) return;
          transcript.hidden = !transcript.hidden;
          toggle.setAttribute('aria-expanded', String(!transcript.hidden));
        });
        transcript.before(toggle);
        // Old nested transcript bodies were hidden with utility classes.
        transcript.querySelectorAll('.hidden').forEach(node => node.classList.remove('hidden'));
      });
      results.scrollIntoView({behavior: 'smooth', block: 'start'});
    }
    submit.addEventListener('click', openModal);
    continueButton.addEventListener('click', closeModal);
    confirm.addEventListener('click', grade);
    // There is no timer-triggered grading and no alternative submission path.
  }
  return {init, speakNeutralWord};
})();
