// Read-only Google IAM inspection. No Rules publication or Firestore writes.
import { GoogleAuth } from 'google-auth-library';
import { mkdir, writeFile, realpath } from 'node:fs/promises';
import { resolve, relative, dirname, isAbsolute, sep } from 'node:path';
import { createHash } from 'node:crypto';
import { pathToFileURL, fileURLToPath } from 'node:url';

export const PROJECT = 'ht-english-library';
export const documentName = `projects/${PROJECT}/databases/(default)/documents/libraryCatalog/current`;
export const sha256 = text => createHash('sha256').update(text).digest('hex');

export function assertReadOnly(url, method = 'GET') {
  const parsed = new URL(url);
  if (parsed.protocol !== 'https:' || parsed.username || parsed.password) throw new Error('Unsupported API URL.');
  const hosts = ['firebaserules.googleapis.com', 'firestore.googleapis.com', 'firebase.googleapis.com'];
  if (!hosts.includes(parsed.hostname) || !parsed.pathname.startsWith(`/v1${parsed.hostname === 'firebase.googleapis.com' ? 'beta1' : ''}/projects/${PROJECT}/`)) throw new Error('Unexpected API/project.');
  if (method !== 'GET' && !(method === 'POST' && parsed.hostname === 'firestore.googleapis.com' && parsed.pathname.endsWith('/documents:listCollectionIds'))) throw new Error('Only read operations are permitted.');
}

export async function collectPreflight(request) {
  const result = { projectId: PROJECT, databaseId: '(default)', startedAt: new Date().toISOString(), complete: false, otherApplicationUsage: 'unconfirmed', rules: null, databases: null, rootCollections: null, apps: {}, catalog: null, warnings: [], errors: [] };
  async function capture(label, operation) {
    try { await operation(); }
    catch (error) { result.errors.push({ operation: label, code: error.status || 'request-failed' }); }
  }
  async function pages(url, property, method = 'GET') {
    const values = []; let token; const seen = new Set();
    do {
      if (token && seen.has(token)) throw new Error('Repeated page token; inventory incomplete.');
      if (token) seen.add(token);
      const target = new URL(url);
      if (method === 'GET') { target.searchParams.set('pageSize', '100'); if (token) target.searchParams.set('pageToken', token); }
      const page = await request(target.href, method, method === 'POST' ? { pageSize: 100, ...(token ? { pageToken: token } : {}) } : undefined);
      values.push(...(page[property] || [])); token = page.nextPageToken;
    } while (token);
    return values;
  }
  await capture('active Rules backup', async () => {
    const releases = await pages(`https://firebaserules.googleapis.com/v1/projects/${PROJECT}/releases`, 'releases');
    const active = releases.filter(item => item.name.split('/releases/')[1] === 'cloud.firestore' || item.name.split('/releases/')[1]?.startsWith('cloud.firestore/'));
    if (!active.some(item => item.name === `projects/${PROJECT}/releases/cloud.firestore`)) throw new Error('Default Firestore release not found.');
    const backups = [];
    for (const release of active) {
      if (!release.rulesetName?.startsWith(`projects/${PROJECT}/rulesets/`)) throw new Error('Unexpected Ruleset project.');
      const ruleset = await request(`https://firebaserules.googleapis.com/v1/${release.rulesetName}`);
      if (!ruleset.source?.files?.length) throw new Error('Ruleset source missing.');
      backups.push({ release, ruleset });
    }
    result.rules = backups;
  });
  await capture('database inventory', async () => {
    const data = await request(`https://firestore.googleapis.com/v1/projects/${PROJECT}/databases`);
    result.databases = data.databases || [];
    if (data.nextPageToken) throw new Error('Database inventory pagination unsupported; stop for review.');
  });
  await capture('default database root collections', async () => {
    result.rootCollections = await pages(`https://firestore.googleapis.com/v1/projects/${PROJECT}/databases/(default)/documents:listCollectionIds`, 'collectionIds', 'POST');
    const other = result.rootCollections.filter(name => !['libraryCatalog', 'libraryMembers'].includes(name));
    if (other.length) result.warnings.push('Other root collections exist; proposed default-deny Rules need review.');
    if ((result.databases || []).some(db => db.name !== `projects/${PROJECT}/databases/(default)`)) result.warnings.push('Other databases exist; inspect their Rules and integrations separately.');
  });
  for (const platform of ['webApps', 'androidApps', 'iosApps']) await capture(`${platform} inventory`, async () => {
    result.apps[platform] = await pages(`https://firebase.googleapis.com/v1beta1/projects/${PROJECT}/${platform}`, 'apps');
  });
  await capture('libraryCatalog/current backup', async () => {
    try {
      const document = await request(`https://firestore.googleapis.com/v1/${documentName}`);
      if (document.name !== documentName || !document.updateTime) throw new Error('Invalid document response.');
      result.catalog = { exists: true, document }; // Raw Firestore typed values retained verbatim.
    } catch (error) {
      if (error.status !== 404) throw error;
      // A document 404 alone does not prove that the database exists.
      if (!(result.databases || []).some(db => db.name === `projects/${PROJECT}/databases/(default)`)) throw new Error('Missing database; document absence unconfirmed.');
      result.catalog = { exists: false, document: null };
    }
  });
  await capture('Rules unchanged during inspection', async () => {
    if (!result.rules) throw new Error('Rules backup missing.');
    for (const entry of result.rules) {
      const latest = await request(`https://firebaserules.googleapis.com/v1/${entry.release.name}`);
      if (latest.rulesetName !== entry.release.rulesetName) throw new Error('Rules changed during backup; re-inspect.');
    }
  });
  result.completedAt = new Date().toISOString();
  result.complete = result.errors.length === 0;
  result.warnings.push('App/collection inventory cannot prove that no external application uses this project. Owner confirmation and Console usage review are required.');
  return result;
}

export async function savePreflight(result, directory) {
  const output = resolve(directory), checkout = await realpath(resolve(dirname(fileURLToPath(import.meta.url)), '..'));
  await mkdir(output, { recursive: true, mode: 0o700 });
  const actual = await realpath(output);
  const distance = relative(checkout, actual);
  if (!(distance === '..' || distance.startsWith('..' + sep) || isAbsolute(distance))) throw new Error('Backups must be outside the repository.');
  const bytes = JSON.stringify(result, null, 2) + '\n';
  await writeFile(resolve(actual, 'preflight.json'), bytes, { flag: 'wx', mode: 0o600 });
  await writeFile(resolve(actual, 'preflight.sha256'), sha256(bytes) + '\n', { flag: 'wx', mode: 0o600 });
  return actual;
}

async function main() {
  const output = process.argv[2];
  if (!output) throw new Error('Provide a new private backup directory outside the checkout.');
  if (process.env.FIRESTORE_EMULATOR_HOST || process.env.FIREBASE_AUTH_EMULATOR_HOST) throw new Error('Clear emulator variables; this tool is a read-only production inspector.');
  const auth = new GoogleAuth({ scopes: ['https://www.googleapis.com/auth/cloud-platform.read-only', 'https://www.googleapis.com/auth/firebase'] });
  const client = await auth.getClient();
  const token = await client.getAccessToken();
  if (!token.token) throw new Error('Google operator authentication is required.');
  const request = async (url, method = 'GET', body) => {
    assertReadOnly(url, method);
    const response = await fetch(url, { method, headers: { Authorization: `Bearer ${token.token}`, 'Content-Type': 'application/json' }, ...(body ? { body: JSON.stringify(body) } : {}), signal: AbortSignal.timeout(30000) });
    if (!response.ok) { const error = new Error('Read-only API request failed.'); error.status = response.status; throw error; }
    return response.json();
  };
  const result = await collectPreflight(request);
  const directory = await savePreflight(result, output);
  console.log(`Inspection ${result.complete ? 'collected' : 'INCOMPLETE'}. Private backup: ${directory}. No Rules published and no database writes.`);
  if (!result.complete) process.exitCode = 1;
}
if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) main().catch(() => {
  console.error('Inspection could not finish. Check Google operator authentication, project read permissions and API network access. Do not send tokens/keys in chat. No Firebase writes performed.');
  process.exitCode = 1;
});
