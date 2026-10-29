/* Compatibility for previously cached pilot launchers; no duplicate UI engine. */
document.documentElement.dataset.minimalUi='all-grades';
import('../shared-practice/minimal-ui.js?v=20261028-all').then(({setupMinimalUI})=>setupMinimalUI()).catch(()=>{delete document.documentElement.dataset.minimalUi;});
