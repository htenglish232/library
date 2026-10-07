/* Listening media only: independent of exam data, grading and speech synthesis. */
'use strict';
const Grade7Listening = (() => {
  function formatAudioTime(seconds) {
    if (!Number.isFinite(seconds) || seconds < 0) return '00:00';
    return `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;
  }
  function pauseOtherAudios(current) {
    document.querySelectorAll('audio').forEach(audio => {
      if (audio !== current) audio.pause();
    });
  }
  function init() {
    document.querySelectorAll('[data-audio-player]').forEach(player => {
      if (player.dataset.ready) return;
      player.dataset.ready = 'true';
      const audio = player.querySelector('audio');
      const source = audio.querySelector('source');
      audio.controls = false;
      audio.autoplay = false;
      function node(tag, className, text) {
        const item = document.createElement(tag);
        item.className = className;
        if (text !== undefined) item.textContent = text;
        return item;
      }
      player.append(node('p', 'widget-label', player.dataset.label));
      const status = node('p', 'audio-status');
      status.setAttribute('role', 'status');
      status.hidden = true;
      player.append(status);
      const controls = node('div', 'mp3-controls');
      function button(parent, text, label, action) {
        const item = node('button', '', text);
        item.type = 'button';
        item.setAttribute('aria-label', label);
        item.addEventListener('click', action);
        parent.append(item);
        return item;
      }
      function seek(seconds) {
        const end = Number.isFinite(audio.duration) ? audio.duration : Math.max(0, seconds);
        try { audio.currentTime = Math.max(0, Math.min(end, seconds)); }
        catch { /* Metadata may not be available yet; keep controls usable. */ }
        update();
      }
      function fail() {
        status.hidden = false;
        const unsupported = (audio.error && audio.error.code === 4)
          || (source && source.type && !audio.canPlayType(source.type));
        status.textContent = unsupported
          ? 'Trình duyệt hiện tại không hỗ trợ định dạng file nghe này.'
          : 'Không phát được file nghe. Vui lòng kiểm tra kết nối và thử lại.';
        update();
      }
      function play() {
        pauseOtherAudios(audio);
        // Called directly by a user gesture; no AudioContext or autoplay.
        try {
          const pending = audio.play();
          if (pending) pending.then(() => { status.hidden = true; }).catch(fail);
        } catch { fail(); }
      }
      button(controls, '↶ 5s', 'Lùi 5 giây', () => seek(audio.currentTime - 5));
      const toggle = button(controls, '▶', 'Phát', () => audio.paused ? play() : audio.pause());
      toggle.className = 'mp3-play';
      button(controls, '5s ↷', 'Tiến 5 giây', () => seek(audio.currentTime + 5));
      button(controls, '↺', 'Phát lại từ đầu', () => { seek(0); play(); });
      player.append(controls);
      function range(label, max, step, value) {
        const item = node('input', '');
        Object.assign(item, {type: 'range', min: 0, max, step, value});
        item.setAttribute('aria-label', label);
        return item;
      }
      const timeline = node('div', 'mp3-timeline');
      const current = node('span', '', '00:00');
      const duration = node('span', '', '00:00');
      const progress = range('Tiến trình audio', 100, 0.1, 0);
      progress.addEventListener('input', () => {
        if (Number.isFinite(audio.duration)) seek(Number(progress.value) * audio.duration / 100);
      });
      timeline.append(current, progress, duration);
      player.append(timeline);
      const settings = node('div', 'mp3-settings');
      const mute = button(settings, '🔊', 'Tắt tiếng', () => { audio.muted = !audio.muted; });
      const volume = range('Âm lượng audio', 1, 0.05, audio.volume);
      volume.addEventListener('input', () => { audio.volume = Number(volume.value); });
      settings.append(volume);
      const rates = node('div', 'mp3-speeds');
      rates.setAttribute('role', 'group');
      rates.setAttribute('aria-label', 'Tốc độ phát');
      const rateButtons = [0.75, 1, 1.25].map(rate => {
        const item = button(rates, `${rate}x`, `Tốc độ ${rate}x`, () => { audio.playbackRate = rate; });
        item.dataset.rate = rate;
        return item;
      });
      settings.append(rates);
      player.append(settings);
      function update() {
        current.textContent = formatAudioTime(audio.currentTime);
        duration.textContent = formatAudioTime(audio.duration);
        progress.disabled = !Number.isFinite(audio.duration) || audio.duration <= 0;
        progress.value = !progress.disabled ? audio.currentTime / audio.duration * 100 : 0;
        toggle.textContent = audio.paused ? '▶' : '⏸';
        toggle.setAttribute('aria-label', audio.paused ? 'Phát' : 'Tạm dừng');
        toggle.setAttribute('aria-pressed', String(!audio.paused));
        const silent = audio.muted || audio.volume === 0;
        mute.textContent = silent ? '🔇' : '🔊';
        mute.setAttribute('aria-label', audio.muted ? 'Bật tiếng' : 'Tắt tiếng');
        mute.setAttribute('aria-pressed', String(audio.muted));
        volume.value = audio.volume;
        rateButtons.forEach(item => item.setAttribute('aria-pressed', String(Number(item.dataset.rate) === audio.playbackRate)));
      }
      ['loadedmetadata', 'durationchange', 'timeupdate', 'pause', 'ended', 'volumechange', 'ratechange', 'emptied'].forEach(name => audio.addEventListener(name, update));
      audio.addEventListener('play', () => { pauseOtherAudios(audio); update(); });
      audio.addEventListener('error', fail);
      // A rejected <source> may emit its own error without setting audio.error.
      if (source) source.addEventListener('error', fail);
      update();
      if (audio.error || (source && source.type && !audio.canPlayType(source.type))) fail();
    });
  }
  return {init};
})();
