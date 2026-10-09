export { initializeApp } from 'firebase/app';
export { getAuth, connectAuthEmulator, onAuthStateChanged, signInWithEmailAndPassword,
  signOut, sendPasswordResetEmail, setPersistence, browserSessionPersistence } from 'firebase/auth';
export { getFirestore, connectFirestoreEmulator, doc, collection, onSnapshot,
  getDocFromServer, setDoc, serverTimestamp } from 'firebase/firestore';
