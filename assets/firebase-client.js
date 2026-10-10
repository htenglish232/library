import { firebaseConfig, useEmulators } from './firebase-config.js';
import { initializeApp, getAuth, getFirestore, connectAuthEmulator, connectFirestoreEmulator } from './firebase-sdk.js';
const local = ['127.0.0.1', 'localhost', '[::1]'].includes(location.hostname);
if (useEmulators && !local) throw new Error('Emulator chỉ được dùng trên máy cục bộ.');
const app = initializeApp(useEmulators ? { apiKey: 'demo-api-key', projectId: 'demo-ht-english-library', authDomain: 'localhost' } : firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app); // Memory-only cache; no persistent offline catalog.
if (useEmulators) {
  connectAuthEmulator(auth, 'http://127.0.0.1:9099', { disableWarnings: true });
  connectFirestoreEmulator(db, '127.0.0.1', 8080);
}
