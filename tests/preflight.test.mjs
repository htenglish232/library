import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, stat } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';
import { assertReadOnly, collectPreflight, savePreflight, PROJECT, documentName } from '../tools/firebase-preflight.mjs';

const release = { name: `projects/${PROJECT}/releases/cloud.firestore`, rulesetName: `projects/${PROJECT}/rulesets/original` };
const ruleset = { source: { files: [{ name: 'firestore.rules', content: "rules_version = '2'; service cloud.firestore { match /databases/{database}/documents { match /{document=**} { allow read, write: if false; } } }" }] } };
const originalDoc = { name: documentName, createTime: '2026-01-01T00:00:00Z', updateTime: '2026-01-02T00:00:00.123456789Z', fields: { large: { integerValue: '9223372036854775807' }, time: { timestampValue: '2026-01-01T00:00:00.123456789Z' }, map: { mapValue: { fields: { bytes: { bytesValue: 'AAEC' } } } }, list: { arrayValue: { values: [{ nullValue: null }, { referenceValue: 'projects/ht-english-library/databases/(default)/documents/old/path' }] } } } };

function fixture({ status = 404, rootError = false, changedRules = false, databaseExists = true } = {}) {
  const calls = [];
  return { calls, async request(url, method = 'GET', body) {
    assertReadOnly(url, method); calls.push({ url, method, body });
    const path = new URL(url).pathname;
    if (path.endsWith('/releases')) return { releases: [release] };
    if (path.endsWith('/rulesets/original')) return ruleset;
    if (path.endsWith('/releases/cloud.firestore')) return { ...release, ...(changedRules ? { rulesetName: `projects/${PROJECT}/rulesets/changed` } : {}) };
    if (path.endsWith('/databases')) return { databases: databaseExists ? [{ name: `projects/${PROJECT}/databases/(default)` }] : [] };
    if (path.endsWith('/documents:listCollectionIds')) {
      if (rootError) { const error = new Error('Forbidden'); error.status = 403; throw error; }
      if (!body.pageToken) return { collectionIds: ['libraryCatalog'], nextPageToken: 'page2' };
      return { collectionIds: ['otherApplication'] };
    }
    if (/\/(webApps|androidApps|iosApps)$/.test(path)) return { apps: path.endsWith('/webApps') ? [{ displayName: 'HT English Library Web' }] : [] };
    if (path.endsWith('/documents/libraryCatalog/current')) {
      if (status === 200) return structuredClone(originalDoc);
      const error = new Error('API refused'); error.status = status; throw error;
    }
    throw new Error('Unexpected fixture endpoint');
  } };
}

test('preflight permits only expected project HTTPS reads and collection-ID enumeration', () => {
  assertReadOnly(`https://firestore.googleapis.com/v1/projects/${PROJECT}/databases`);
  assertReadOnly(`https://firestore.googleapis.com/v1/projects/${PROJECT}/databases/(default)/documents:listCollectionIds`, 'POST');
  for (const [url, method] of [
    [`https://firebaserules.googleapis.com/v1/projects/${PROJECT}/releases/cloud.firestore`, 'PATCH'],
    [`https://firestore.googleapis.com/v1/projects/${PROJECT}/databases/(default)/documents:commit`, 'POST'],
    [`https://firestore.googleapis.com/v1/${documentName}`, 'DELETE'],
    ['https://firestore.googleapis.com/v1/projects/other-project/databases', 'GET'],
    [`http://firestore.googleapis.com/v1/projects/${PROJECT}/databases`, 'GET'],
    [`https://firestore.googleapis.com.attacker.example/v1/projects/${PROJECT}/databases`, 'GET']
  ]) assert.throws(() => assertReadOnly(url, method));
});
test('confirmed database and document 404 record absence; collections paginate; external use stays unconfirmed', async () => {
  const api = fixture(); const result = await collectPreflight(api.request);
  assert.equal(result.complete, true); assert.equal(result.catalog.exists, false);
  assert.deepEqual(result.rootCollections, ['libraryCatalog', 'otherApplication']);
  assert.equal(result.otherApplicationUsage, 'unconfirmed');
  assert.equal(api.calls.filter(c => c.method === 'POST').length, 2);
});
test('403 and missing database never mean the document is absent', async () => {
  for (const options of [{ status: 403 }, { databaseExists: false }, { rootError: true }]) {
    const result = await collectPreflight(fixture(options).request); assert.equal(result.complete, false);
    if (!options.rootError) assert.equal(result.catalog, null);
  }
});
test('Rules changed during collection prevent a complete backup', async () => {
  const result = await collectPreflight(fixture({ changedRules: true }).request);
  assert.equal(result.complete, false); assert.ok(result.errors.some(e => e.operation.includes('Rules unchanged')));
});
test('typed document backup preserves large integers, nanoseconds, bytes, maps, arrays and references; rollback is offline', async () => {
  const folder = await mkdtemp(join(tmpdir(), 'library-preflight-fixture-'));
  try {
    const result = await collectPreflight(fixture({ status: 200 }).request);
    await savePreflight(result, folder);
    assert.deepEqual(JSON.parse(await readFile(join(folder, 'preflight.json'), 'utf8')).catalog.document, originalDoc);
    assert.equal((await stat(join(folder, 'preflight.json'))).mode & 0o777, 0o600);
    execFileSync(process.execPath, ['tools/prepare-firebase-rollback.mjs', folder]);
    const plan = JSON.parse(await readFile(join(folder, 'rollback-plan.json'), 'utf8'));
    assert.equal(plan.execute, false); assert.deepEqual(plan.firestoreCommitTemplate.writes[0].update.fields, originalDoc.fields);
    await assert.rejects(savePreflight(result, folder), /EEXIST/);
  } finally { await rm(folder, { recursive: true, force: true }); }
});
test('originally absent catalog prepares only a conditional single-document deletion', async () => {
  const folder = await mkdtemp(join(tmpdir(), 'library-preflight-absent-'));
  try {
    await savePreflight(await collectPreflight(fixture().request), folder);
    execFileSync(process.execPath, ['tools/prepare-firebase-rollback.mjs', folder]);
    const plan = JSON.parse(await readFile(join(folder, 'rollback-plan.json'), 'utf8'));
    assert.equal(plan.firestoreCommitTemplate.writes.length, 1);
    assert.equal(plan.firestoreCommitTemplate.writes[0].delete, documentName);
    assert.ok(plan.firestoreCommitTemplate.writes[0].currentDocument.updateTime.includes('REPLACE'));
  } finally { await rm(folder, { recursive: true, force: true }); }
});
