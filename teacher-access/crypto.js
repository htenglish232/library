/* Static-site access restriction only. All account verifiers are public. */
(() => {
  'use strict';
  const ITERATIONS = 600000;
  const hex = bytes => Array.from(bytes, b => b.toString(16).padStart(2, '0')).join('');
  const bytes = value => new Uint8Array(value.match(/../g).map(pair => parseInt(pair, 16)));
  async function verifier(password, salt) {
    const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(password), 'PBKDF2', false, ['deriveBits']);
    const result = await crypto.subtle.deriveBits({name: 'PBKDF2', hash: 'SHA-256', salt: bytes(salt), iterations: ITERATIONS}, key, 256);
    return hex(new Uint8Array(result));
  }
  function validate(config) {
    if (!config || config.schemaVersion !== 1 || !Array.isArray(config.accounts) || config.accounts.length > 100) throw new Error('Invalid account configuration');
    const names = new Set(), ids = new Set();
    for (const a of config.accounts) {
      if (!a || typeof a.username !== 'string' || !/^[a-zA-Z0-9._-]{3,80}$/.test(a.username) || names.has(a.username) ||
          typeof a.id !== 'string' || !/^[a-f0-9]{32}$/.test(a.id) || ids.has(a.id) ||
          a.iterations !== ITERATIONS || a.algorithm !== 'PBKDF2-SHA-256' ||
          typeof a.salt !== 'string' || !/^[a-f0-9]{32}$/.test(a.salt) ||
          typeof a.verifier !== 'string' || !/^[a-f0-9]{64}$/.test(a.verifier)) throw new Error('Invalid account configuration');
      names.add(a.username); ids.add(a.id);
    }
    return config;
  }
  async function create(username, password) {
    const salt = hex(crypto.getRandomValues(new Uint8Array(16)));
    return {username, id: hex(crypto.getRandomValues(new Uint8Array(16))), algorithm: 'PBKDF2-SHA-256', iterations: ITERATIONS, salt, verifier: await verifier(password, salt)};
  }
  window.HTTeacherCrypto = Object.freeze({verifier, validate, create});
})();
