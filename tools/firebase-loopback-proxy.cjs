// Firebase CLI 15.33's explicit ProxyAgent ignores NO_PROXY. Keep the inherited
// proxy for all remote destinations, but dispatch loopback emulator traffic locally.
// This preload changes no dependency files, proxy variables, CA trust, or TLS checks.
const undici = require('../node_modules/undici');
const Original = undici.ProxyAgent;
const local = new undici.Agent();
class EmulatorAwareProxyAgent extends Original {
  dispatch(options, handler) {
    const hostname = new URL(options.origin).hostname;
    if (['127.0.0.1', 'localhost', '[::1]'].includes(hostname)) return local.dispatch(options, handler);
    return super.dispatch(options, handler);
  }
}
undici.ProxyAgent = EmulatorAwareProxyAgent;
