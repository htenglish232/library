// Permit only the reviewed sound bootstrap changes; all other HTML stays exact.
export const SOUND_RELEASE='20261026-sound-fix';
export const STATIC_SOUND_BUTTON='<button type="button" id="sound-toggle" class="quiet" aria-pressed="true" aria-busy="true" data-sound-state="loading" title="Đang tải hiệu ứng âm thanh…" disabled>🔊 Âm thanh: Bật</button>';
export const isDualLauncher=file=>/\/(?:practice|truc-tuan)-dual-mode\.html$/u.test(file);
export function beforeSoundBootstrap(html){
 return html.replace(STATIC_SOUND_BUTTON,'')
  .replaceAll('dual-mode-engine.js?v='+SOUND_RELEASE,'dual-mode-engine.js')
  .replaceAll('dual-mode.css?v='+SOUND_RELEASE,'dual-mode.css');
}
