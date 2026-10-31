import {initializeApp} from 'firebase-admin/app';
import {getAuth} from 'firebase-admin/auth';
import {getFirestore} from 'firebase-admin/firestore';
import {onRequest} from 'firebase-functions/v2/https';
import {createService} from './service.js';
import {createHandler} from './handler.js';
const projectId = process.env.GCLOUD_PROJECT || process.env.GOOGLE_CLOUD_PROJECT || '';
if (!/^demo-ht-student-portal$|^[a-z][a-z0-9-]*-staging[a-z0-9-]*$/.test(projectId) || projectId === 'ht-english-library') {
  throw Error('Student Portal backend requires a separate staging project');
}
initializeApp({projectId});
export const studentApi = onRequest({region:'asia-southeast1', maxInstances:2, minInstances:0,
  memory:'256MiB', timeoutSeconds:30, cors:false, invoker:'public'},
  createHandler({auth:getAuth(), service:createService(getFirestore())}));
