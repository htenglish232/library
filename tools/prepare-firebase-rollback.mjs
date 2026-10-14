// OFFLINE ONLY: verify a preflight backup and prepare a restoration request template.
import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { PROJECT, documentName, sha256 } from './firebase-preflight.mjs';

const directory = process.argv[2];
if (!directory) throw new Error('Provide the private backup directory.');
const text = await readFile(resolve(directory, 'preflight.json'), 'utf8');
const expected = (await readFile(resolve(directory, 'preflight.sha256'), 'utf8')).trim();
if (sha256(text) !== expected) throw new Error('Backup checksum mismatch; refusing to prepare rollback.');
const backup = JSON.parse(text);
if (backup.projectId !== PROJECT || backup.databaseId !== '(default)' || !backup.complete || !backup.rules?.length || !backup.catalog) throw new Error('Incomplete/wrong-project backup; rollback unavailable.');
const old = backup.catalog.document;
if (backup.catalog.exists && old?.name !== documentName) throw new Error('Unexpected document path.');
const write = backup.catalog.exists
  ? { update: { name: documentName, fields: old.fields || {} }, currentDocument: { updateTime: 'REPLACE_WITH_VERIFIED_POST_IMPORT_UPDATE_TIME' } }
  : { delete: documentName, currentDocument: { updateTime: 'REPLACE_WITH_VERIFIED_POST_IMPORT_UPDATE_TIME' } };
const plan = {
  projectId: PROJECT, sourceBackupSha256: expected, execute: false,
  approvalRequired: true, currentRulesMustStillMatchAppliedVersion: true,
  catalogWasPresent: backup.catalog.exists,
  rulesRestore: backup.rules.map(entry => ({ releaseName: entry.release.name, previousRulesetName: entry.release.rulesetName, sourceFiles: entry.ruleset.source.files })),
  firestoreCommitTemplate: { writes: [write] },
  notes: ['This file does not execute a request.', 'Stop if current document changed since the intended import; do not overwrite newer work.', 'Use Google project operator IAM access for restoration; client Rules may reject the old schema or a delete.', 'Restore old document fields and value types; server createTime/updateTime cannot be restored.', 'If previously absent, delete only the newly created current document, never the collection or its subcollections.', 'Rules rollback restores the full prior source, including unrelated application rules.']
};
await writeFile(resolve(directory, 'rollback-plan.json'), JSON.stringify(plan, null, 2) + '\n', { flag: 'wx', mode: 0o600 });
console.log('Offline rollback template prepared. No API requests, no Firebase writes.');
