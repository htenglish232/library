import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {validateSets, loadPack, cardsForScope, addNewPacks, createSession, currentCard, move} from '../core.js';
const root = new URL('../data/global3-unit5/', import.meta.url);
const raw = JSON.parse(readFileSync(new URL('unit5_speaking_cards.json', root)));
const pack = loadPack(raw, './data/global3-unit5/');
const sha = bytes => createHash('sha256').update(bytes).digest('hex');

test('all 14 original images, JSON, CSV and README match the ZIP integrity manifest byte for byte', () => {
  const manifest = JSON.parse(readFileSync(new URL('integrity.json', root)));
  assert.equal(Object.keys(manifest.files).filter(name => name.endsWith('.png')).length, 14);
  for (const [name, expected] of Object.entries(manifest.files)) {
    const bytes = readFileSync(new URL(name, root));
    assert.equal(bytes.length, expected.bytes, name); assert.equal(sha(bytes), expected.sha256, name);
  }
  assert.equal(sha(readFileSync(new URL('../data/sets.json', import.meta.url))), 'e7afa10d5fb11eda71176b95fa5b99ccd64439fedc059049e0b827ceced33781');
});
test('pack adapter preserves question/answer/category/image associations and his/her phrasing', () => {
  assert.equal(pack.grade, 'Grade 3'); assert.equal(pack.unit, 'Unit 5'); assert.equal(pack.cards.length, 14);
  raw.cards.forEach((source, i) => {
    assert.equal(pack.cards[i].id, source.id);
    assert.equal(pack.cards[i].question, source.question);
    assert.equal(pack.cards[i].sampleAnswer, source.sampleAnswer);
    assert.equal(pack.cards[i].category, source.category);
    assert.equal(pack.cards[i].image, './data/global3-unit5/' + source.image);
    assert.deepEqual(pack.cards[i].keywords, source.keywords);
  });
  assert.equal(pack.cards.filter(c => c.category === 'review').length, 8);
  assert.equal(pack.cards.filter(c => c.category === 'extension').length, 1);
  assert.deepEqual(cardsForScope(pack, 'unit5').map(c => c.id), raw.cards.slice(9).map(c => c.id));
  assert.deepEqual(validateSets(JSON.parse(JSON.stringify({sets:[pack]}))), [pack]);
});
test('Sequential and Random Test operate only on the selected 14/5 cards and keep backtracking stable', () => {
  for (const scope of ['all', 'unit5']) {
    const expected = cardsForScope(pack, scope).map(c => c.id);
    for (const order of ['sequential', 'random']) {
      const session = createSession(pack, 'test', order, null, scope);
      const seen = [currentCard(session).id];
      while (move(session, 1)) seen.push(currentCard(session).id);
      assert.equal(new Set(seen).size, expected.length);
      assert.deepEqual([...seen].sort(), [...expected].sort());
      if (order === 'sequential') assert.deepEqual(seen, expected);
      const last = currentCard(session).id;
      move(session, -1); move(session, 1); assert.equal(currentCard(session).id, last);
      assert.equal(session.seen.size, expected.length);
      const restart = createSession(pack, 'test', order, null, session.scope);
      assert.equal(restart.sequence.length, expected.length);
      assert.equal(restart.cursor, 0);
    }
  }
  assert.throws(() => cardsForScope(pack, 'unknown'));
});
test('new bundled pack is added to old saved libraries without changing existing cards or resurrecting intentional deletions', () => {
  const demo = JSON.parse(readFileSync(new URL('../data/sets.json', import.meta.url)));
  const snapshot = JSON.stringify(demo);
  const merged = addNewPacks(demo, [pack], []);
  assert.equal(merged.length, 2); assert.equal(JSON.stringify(demo), snapshot); assert.equal(merged[0], demo[0]);
  assert.equal(addNewPacks(merged, [pack], []).length, 2);
  assert.deepEqual(addNewPacks(demo, [pack], [pack.id]), demo);
  const custom = {...pack, title: 'Teacher edited title'};
  assert.equal(addNewPacks([custom], [pack], [pack.id])[0], custom);
});
