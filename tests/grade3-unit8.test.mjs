import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {execFileSync} from 'node:child_process';
import {
  addReleaseLessons,
  GRADE3_GRAMMAR_ADDITION,
  GRADE3_GRAMMAR_RELEASE_ID,
  RELEASE_IDS,
} from '../assets/catalog-release.js';

const path = 'grade-3/Bo_Tro_Ngu_Phap/unit_08_these_those.html';
const html = readFileSync(path, 'utf8');
const current = JSON.parse(readFileSync('catalog/current-library-catalog.json', 'utf8')).data;
const before = JSON.parse(execFileSync('git', ['show', 'd047dbe:catalog/current-library-catalog.json'])).data;
const questionsMatch = html.match(/const questionsData = (\{[\s\S]*?\n    \});\n\n    \/\/ Quản lý trạng thái bài làm/);

function questionData() {
  assert.ok(questionsMatch, 'questionsData must remain readable');
  return vm.runInNewContext(`(${questionsMatch[1]})`);
}

test('the supplied Unit 8 academic data stays exact while A4 and answer locking are repaired', () => {
  assert.equal(createHash('sha256').update(questionsMatch[1]).digest('hex'), '41ebaf1a83079725057c34905282cb457a7224f6b470722fba51c32d50841d86');
  assert.match(html, /UNIT8_REPAIR_START/);
  assert.match(html, /function lockQuestion\(qid\)/);
  const data = questionData();
  assert.deepEqual(Object.keys(data), [
    'a1','a2','a3','a4','b1','b2','b3','b4','b5','b6',
    'c1','c2','c3','c4','d1','d2','d3','d4','d5','d6'
  ]);
  const itemIds = [...html.matchAll(/class="q-item" id="item-([a-d]\d+)"/g)].map(match => match[1]);
  assert.deepEqual(itemIds, Object.keys(data));
  for (const [id, question] of Object.entries(data)) {
    assert.ok(question.explanation && question.translation, id);
    if (question.type === 'pair') {
      assert.ok(question.correctPronoun && question.correctNoun, id);
      assert.match(html, new RegExp(`id="sel-${id}-d"`));
      assert.match(html, new RegExp(`id="sel-${id}-n"`));
    } else {
      assert.ok(question.correct, id);
    }
  }
  assert.match(html, /speechSynthesis\.speak\(utterance\)/);
  assert.match(html, /function submitWorksheet\(\)/);
  assert.match(html, /function resetWorksheet\(\)/);
  assert.ok((html.match(/<svg\b/g) || []).length >= 10, 'illustrations stay inline and self-contained');
});

test('the Grade 3 release is additive, ordered before Grade 4 and can be adopted once', () => {
  const result = addReleaseLessons(before);
  assert.deepEqual(result.data, current);
  assert.deepEqual(current.slice(1), before);
  const grade = current[0];
  assert.equal(grade.grade, 'Grade 3');
  assert.deepEqual(grade.units, [{name: 'Bổ trợ ngữ pháp', lessons: [GRADE3_GRAMMAR_ADDITION.lesson]}]);
  assert.equal(GRADE3_GRAMMAR_ADDITION.lesson.href, path);
  assert.ok(RELEASE_IDS.includes(GRADE3_GRAMMAR_RELEASE_ID));
  assert.deepEqual(addReleaseLessons(result.data), {data: current, added: 0});
  const adopted = structuredClone(before);
  assert.deepEqual(addReleaseLessons(adopted, [GRADE3_GRAMMAR_RELEASE_ID]).data, addReleaseLessons(before).data.slice(1));
});

test('existing catalog grades, Firebase integration and access rules stay untouched', () => {
  assert.equal(execFileSync('git', ['diff', 'd047dbe', '--name-only', '--',
    'assets/firebase-config.js','assets/firebase-client.js','assets/firebase-sdk.js','assets/session.js',
    'assets/catalog-store.js','assets/catalog-data.js','assets/catalog-editor.js',
    'firestore.rules','firestore.indexes.json','firebase.json','.firebaserc','admin.html'
  ], {encoding: 'utf8'}), '');
});
