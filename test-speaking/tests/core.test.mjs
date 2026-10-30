import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validateSets, parseCSV, importText, shuffle, createSession, move, currentCard, LocalRepository, mediaPath, loadPack} from '../core.js';
import {QuestionAudio, QuestionTimer} from '../media.js';
const demo = JSON.parse(readFileSync(new URL('../data/sets.json', import.meta.url)));

test('demo is a portable 15-card A1 set and validates after JSON backup round-trip', () => {
  const sets = validateSets(demo);
  assert.equal(sets[0].cards.length, 15);
  assert.deepEqual(importText(JSON.stringify({schemaVersion: 1, sets}), 'backup.json'), sets);
});
test('sequential test covers each card in order, boundaries stay fixed, backtracking does not recount', () => {
  const session = createSession(demo[0], 'test');
  assert.equal(move(session, -1), false);
  const actual = [currentCard(session).id];
  while (move(session, 1)) actual.push(currentCard(session).id);
  assert.deepEqual(actual, demo[0].cards.map(c => c.id));
  assert.equal(session.seen.size, 15); assert.equal(move(session, 1), false);
  move(session, -1); move(session, 1); assert.equal(session.seen.size, 15);
});
test('Fisher–Yates makes exactly n-1 bounded swaps, never mutates input', () => {
  const input = ['a', 'b', 'c', 'd']; let calls = 0;
  assert.deepEqual(shuffle(input, () => { calls++; return 0; }), ['b', 'c', 'd', 'a']);
  assert.equal(calls, 3); assert.deepEqual(input, ['a', 'b', 'c', 'd']);
});
test('random tests use one permutation, never repeat a new question, preserve order on backtracking', () => {
  for (let run = 0; run < 30; run++) {
    const session = createSession(demo[0], 'test', 'random'), order = [...session.sequence];
    assert.equal(new Set(order).size, 15);
    move(session, 1); const card = currentCard(session).id;
    move(session, -1); move(session, 1); assert.equal(currentCard(session).id, card);
    while (move(session, 1)) { /* Finish the fixed permutation. */ }
    assert.deepEqual(session.sequence, order); assert.equal(session.seen.size, 15);
  }
});
test('practice restores shuffled order and position, discards stale/duplicate orders safely', () => {
  const sequence = demo[0].cards.map(c => c.id).reverse();
  const session = createSession(demo[0], 'practice', 'sequential', {sequence, cursor: 7});
  assert.equal(currentCard(session).id, sequence[7]);
  assert.equal(createSession(demo[0], 'practice', 'sequential', {sequence: [...sequence.slice(1), sequence[1]], cursor: 7}).cursor, 0);
  assert.equal(createSession(demo[0], 'practice', 'sequential', {sequence, cursor: -100}).cursor, 0);
  assert.throws(() => createSession({...demo[0], cards: []}, 'test'));
});
test('CSV accepts BOM, Unicode, commas, multiline answers and escaped quotes', () => {
  const csv = '\uFEFFsetId,title,grade,textbook,unit,id,question,sampleAnswer,keywords,image,audio\r\nx,Bộ thẻ,Grade 3,Global Success,Unit 1,q1,"Hello, what is your name?","My name is ""Anna"".\nHello!",name|hello,,\r\n';
  const [set] = parseCSV(csv);
  assert.equal(set.title, 'Bộ thẻ'); assert.equal(set.cards[0].sampleAnswer, 'My name is "Anna".\nHello!');
  assert.deepEqual(set.cards[0].keywords, ['name', 'hello']);
});
test('imports reject broken rows, duplicate identifiers, incomplete data and unsafe media atomically', () => {
  assert.throws(() => parseCSV('id,question\n1,hello'));
  assert.throws(() => parseCSV('setId,title,grade,textbook,unit,id,question,sampleAnswer\na,t,g,b,u,1,q,"unclosed'));
  assert.throws(() => validateSets([...demo, demo[0]]));
  assert.throws(() => validateSets([{...demo[0], cards: [demo[0].cards[0], demo[0].cards[0]]}]));
  assert.throws(() => validateSets([{...demo[0], cards: [{...demo[0].cards[0], sampleAnswer: ''}]}]));
  for (const path of ['javascript:alert(1)', 'data:text/html,hello', '//evil.test/a', 'https://user:password@host.test/a', 'a\\b']) assert.throws(() => mediaPath(path));
  assert.equal(mediaPath('./audio/hello.mp3'), './audio/hello.mp3');
  assert.throws(() => importText('x'.repeat(2 * 1024 * 1024 + 1), 'large.json'));
});
test('storage failure does not crash or claim persistence; corrupt JSON is reported', () => {
  let failures = 0;
  const repository = new LocalRepository({getItem: () => '{bad', setItem: () => { throw Error('QuotaExceeded'); }}, () => failures++);
  assert.equal(repository.read('sets', null), null); assert.equal(repository.write('sets', demo), false); assert.equal(failures, 2);
});
test('timer uses elapsed time, pauses/resumes, expires only once without changing questions', () => {
  let now = 0, expired = 0, last;
  const timer = new QuestionTimer((seconds, running) => { last = {seconds, running}; }, () => expired++, () => now);
  timer.reset(15, true); now = 5500; timer.pause(); assert.equal(last.seconds, 10);
  now = 20000; timer.tick(); assert.equal(last.seconds, 10);
  timer.resume(); now = 29499; timer.tick(); assert.equal(expired, 0);
  now = 29500; timer.tick(); timer.tick(); assert.equal(expired, 1); assert.deepEqual(last, {seconds: 0, running: false});
  timer.reset(30, false); now = 999999; timer.tick(); assert.equal(expired, 1); assert.equal(last.seconds, 30); timer.stop();
});
test('rapid speech replay cancels previous playback, selects English US and stops on navigation', async () => {
  let cancels = 0; const spoken = [];
  const speech = {cancel: () => cancels++, getVoices: () => [{lang: 'vi-VN'}, {lang: 'en-GB'}, {lang: 'en-US'}], speak: u => spoken.push(u)};
  const audio = new QuestionAudio({speech, Utterance: class {constructor(text) {this.text = text;}}, status: () => {}});
  await audio.play(demo[0].cards[0], 0.75); await audio.play(demo[0].cards[1], 1.25);
  assert.equal(cancels, 2); assert.equal(spoken[0].voice.lang, 'en-US'); assert.equal(spoken[1].rate, 1.25);
  audio.stop(); assert.equal(cancels, 3);
});
test('MP3 takes precedence, failing media falls back once, stale callbacks cannot restart speech', async () => {
  const clips = [], spoken = [];
  class Clip {
    constructor(src) {this.src = src; clips.push(this);}
    async play() { if (this.src === 'broken.mp3') throw Error('missing'); }
    pause() {this.paused = true;} removeAttribute() {} load() {}
  }
  const audio = new QuestionAudio({speech: {cancel() {}, getVoices: () => [], speak: u => spoken.push(u)}, Utterance: class {}, AudioClass: Clip});
  await audio.play({...demo[0].cards[0], audio: 'working.mp3'}, 1); assert.equal(spoken.length, 0);
  audio.stop(); clips[0].onerror(); assert.equal(spoken.length, 0);
  await audio.play({...demo[0].cards[0], audio: 'broken.mp3'}, 1); clips[1].onerror(); assert.equal(spoken.length, 1);
});
test('unsupported or non-English voices leave the card usable with an explicit message', async () => {
  let message = '';
  const audio = new QuestionAudio({speech: null, Utterance: null, status: text => {message = text;}});
  await audio.play(demo[0].cards[0], 1); assert.match(message, /không hỗ trợ/);
  const other = new QuestionAudio({speech: {cancel() {}, getVoices: () => [{lang: 'vi-VN'}]}, Utterance: class {}, status: text => {message = text;}});
  await other.play(demo[0].cards[0], 1); assert.match(message, /chưa có giọng tiếng Anh/);
});

test('answerAudio survives JSON/CSV and pack resolution with safe media validation', () => {
  const set = structuredClone(demo[0]);
  set.cards[0].answerAudio = 'audio/answer.mp3';
  assert.equal(importText(JSON.stringify(set), 'set.json')[0].cards[0].answerAudio, 'audio/answer.mp3');
  assert.equal(loadPack(set, './pack/').cards[0].answerAudio, './pack/audio/answer.mp3');
  set.cards[0].audio = 'https://example.test/question.mp3';
  assert.equal(loadPack(set, './pack/').cards[0].audio, set.cards[0].audio);
  const csv = 'setId,title,grade,textbook,unit,id,question,sampleAnswer,answerAudio\ns,Set,Grade 3,Book,Unit 5,c,Question?,Answer.,answer.mp3';
  assert.equal(parseCSV(csv)[0].cards[0].answerAudio, 'answer.mp3');
  set.cards[0].answerAudio = 'javascript:alert(1)';
  assert.throws(() => loadPack(set, './pack/'));
});
test('answer playback uses its own MP3/text and stale answer failures never restart speech', async () => {
  const spoken = [], clips = [];
  class Clip {
    constructor(src) {this.src=src; clips.push(this);}
    async play() {} pause() {this.paused=true;} removeAttribute() {} load() {}
  }
  const player = new QuestionAudio({speech:{cancel(){},getVoices:()=>[],speak:u=>spoken.push(u.text)}, Utterance:class {constructor(text){this.text=text;}},AudioClass:Clip});
  const card = {...demo[0].cards[0],audio:'question.mp3',answerAudio:'answer.mp3'};
  await player.play(card,1,'answer');assert.equal(clips[0].src,'answer.mp3');
  await player.play(card,1);assert.equal(clips[1].src,'question.mp3');assert.ok(clips[0].paused);
  clips[0].onerror();assert.deepEqual(spoken,[]);
  await player.play({...card,answerAudio:''},1,'answer');assert.deepEqual(spoken,[card.sampleAnswer]);
  assert.ok(clips[1].paused);
});
