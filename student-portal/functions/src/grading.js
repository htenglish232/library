import {readFileSync} from 'node:fs';
import vm from 'node:vm';
// Build copies these exact reviewed source files; no second grading implementation.
const context = vm.createContext({window: {}});
vm.runInContext(readFileSync(new URL('../generated/data.js', import.meta.url), 'utf8'), context, {timeout: 1000});
vm.runInContext(readFileSync(new URL('../generated/model.js', import.meta.url), 'utf8'), context, {timeout: 1000});
vm.runInContext(readFileSync(new URL('../generated/progress.js', import.meta.url), 'utf8'), context, {timeout: 1000});
export const data = context.window.HT_PRACTICE_DATA;
export const gameId = 'grade8-truc-tuan';
export function evaluate(answers) {
  if (!answers || typeof answers !== 'object' || Array.isArray(answers) ||
      Object.keys(answers).length !== data.questions.length) throw Error('invalid-answers');
  const state = context.HTDualProgress.create(data, {name: 'Server', code: 'server'});
  for (const q of data.questions) {
    const draft = answers[q.id];
    if (!draft || Object.keys(draft).sort().join(',') !== 'fields,tokens,value') throw Error('invalid-answers');
    context.HTDualProgress.update(data, state, q.id, draft);
    const filled = q.kind === 'rearrange' ? draft.tokens.length === q.tokens.length :
      q.kind === 'multi-text' ? draft.fields.every(v => v.trim()) : draft.value.trim();
    if (filled) context.HTDualProgress.check(data, state, q.id);
  }
  const summary = context.HTDualProgress.summary(data, state);
  return {...JSON.parse(JSON.stringify(summary)), score: Math.round(summary.correct / summary.total * 1000) / 100};
}
