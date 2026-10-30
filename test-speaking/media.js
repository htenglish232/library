export class QuestionAudio {
  constructor({speech = globalThis.speechSynthesis, Utterance = globalThis.SpeechSynthesisUtterance, AudioClass = globalThis.Audio, status = () => {}} = {}) {
    Object.assign(this, {speech, Utterance, AudioClass, status}); this.token = 0; this.audio = null;
  }
  stop() {
    this.token++;
    if (this.audio) { this.audio.pause(); this.audio.removeAttribute('src'); this.audio.load(); this.audio = null; }
    this.speech?.cancel();
  }
  async play(card, rate) {
    this.stop(); const token = this.token;
    const speak = () => {
      if (token !== this.token) return;
      if (!this.speech || !this.Utterance) { this.status('Thiết bị không hỗ trợ giọng đọc. Bạn vẫn có thể dùng thẻ bình thường.'); return; }
      const voices = this.speech.getVoices();
      const voice = voices.find(v => /^en-US$/i.test(v.lang)) || voices.find(v => /^en-GB$/i.test(v.lang)) || voices.find(v => /^en[-_]/i.test(v.lang));
      if (voices.length && !voice) { this.status('Thiết bị chưa có giọng tiếng Anh. Hãy cài giọng English; thẻ vẫn dùng bình thường.'); return; }
      const utterance = new this.Utterance(card.question);
      this.utterance = utterance; utterance.lang = voice?.lang || 'en-US'; if (voice) utterance.voice = voice;
      utterance.rate = rate;
      utterance.onend = () => { if (token === this.token) this.status(''); };
      utterance.onerror = () => { if (token === this.token) this.status('Không phát được giọng đọc. Kiểm tra giọng English hoặc âm lượng thiết bị.'); };
      this.status('Đang đọc câu hỏi…');
      try { this.speech.speak(utterance); } catch { this.status('Không phát được giọng đọc trên trình duyệt này.'); }
    };
    if (!card.audio) { speak(); return; }
    const audio = new this.AudioClass(card.audio); this.audio = audio; audio.playbackRate = rate;
    let failed = false;
    const fallback = () => { if (failed || token !== this.token) return; failed = true; audio.pause(); this.status('Không tải được MP3, chuyển sang giọng đọc thiết bị.'); speak(); };
    audio.onerror = fallback;
    audio.onended = () => { if (token === this.token) this.status(''); };
    this.status('Đang phát âm thanh câu hỏi…');
    try { await audio.play(); } catch { fallback(); }
  }
}

// Use an absolute deadline so background throttling cannot extend a question.
export class QuestionTimer {
  constructor(onUpdate, onExpire, now = () => performance.now()) { Object.assign(this, {onUpdate, onExpire, now}); this.interval = null; this.remaining = 0; this.running = false; }
  reset(seconds, enabled) {
    this.stop(); this.remaining = seconds * 1000; this.expired = false;
    if (enabled) { this.running = true; this.deadline = this.now() + this.remaining; this.interval = setInterval(() => this.tick(), 100); }
    this.onUpdate(Math.ceil(this.remaining / 1000), this.running);
  }
  tick() {
    if (!this.running) return;
    this.remaining = Math.max(0, this.deadline - this.now());
    this.onUpdate(Math.ceil(this.remaining / 1000), true);
    if (this.remaining === 0 && !this.expired) { this.expired = true; this.stop(); this.onUpdate(0, false); this.onExpire(); }
  }
  pause() { if (!this.running) return; this.tick(); this.stop(); this.onUpdate(Math.ceil(this.remaining / 1000), false); }
  resume() { if (this.running || this.expired || !this.remaining) return; this.running = true; this.deadline = this.now() + this.remaining; this.interval = setInterval(() => this.tick(), 100); this.onUpdate(Math.ceil(this.remaining / 1000), true); }
  stop() { clearInterval(this.interval); this.interval = null; this.running = false; }
}
