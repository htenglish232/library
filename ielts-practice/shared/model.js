// IELTS worksheet state is separate from every GHK1/Speaking storage key.
export const cleanAnswer = value => String(value ?? '').trim().toLowerCase();
export const wordCount = text => (String(text).trim().match(/\S+/gu) || []).length;
export const storageKey = unit => `ht-ielts:worksheet:v1:${unit.id}`;
export function stepsFor(unit) {
  return [{kind:'vocabulary', section:'A'},
    {kind:'reading', section:'B'},
    ...unit.multipleChoice.map((_, index) => ({kind:'mcq', index, section:'C'})),
    {kind:'summary', section:'D'}, {kind:'translation', section:'E'}];
}
export function newState(unit) {
  return {schema:1, navigationVersion:2, unit:unit.id, version:unit.version, name:'', started:false, view:'welcome', step:0,
    readingMark:-1, submittedAt:null, checked:{mcq:Array(unit.multipleChoice.length).fill(false),summary:Array(10).fill(false)},
    answers:{mcq:Array(unit.multipleChoice.length).fill(''), summary:Array(10).fill(''), translation:''}};
}
export function restore(unit, raw) {
  const state = newState(unit);
  if (!raw || raw.schema !== 1 || raw.unit !== unit.id || raw.version !== unit.version) return state;
  const safe = (text, max) => typeof text === 'string' ? text.slice(0,max) : '';
  state.name = safe(raw.name,120); state.started = !!raw.started && !!state.name.trim();
  if (Number.isInteger(raw.step)) {
    // Legacy navigation used ten separate Passage screens (23 steps). Keep
    // every saved exercise cursor on the same question after merging Part A.
    const legacy = raw.navigationVersion !== 2;
    const position = Math.max(0,Math.min(legacy?22:stepsFor(unit).length-1,raw.step));
    state.step = legacy ? (position<10?0:position-9) : position;
  }
  state.readingMark = Number.isInteger(raw.readingMark) && raw.readingMark >= 0 && raw.readingMark < unit.reading.length ? raw.readingMark : -1;
  state.submittedAt = typeof raw.submittedAt === 'string' && Number.isFinite(Date.parse(raw.submittedAt)) ? raw.submittedAt : null;
  state.view = raw.view==='vocabulary' && state.step===0 ? 'vocabulary' :
    !state.started ? 'welcome' : state.submittedAt && raw.view !== 'work' ? 'results' : 'work';
  state.answers.mcq = state.answers.mcq.map((_,i) => /^[ABCD]$/.test(raw.answers?.mcq?.[i]) ? raw.answers.mcq[i] : '');
  state.answers.summary = state.answers.summary.map((_,i) => safe(raw.answers?.summary?.[i],100));
  state.answers.translation = safe(raw.answers?.translation,20000);
  for (const kind of ['mcq','summary']) state.checked[kind] = state.checked[kind].map((_,i)=>raw.checked?.[kind]?.[i]===true && !!cleanAnswer(state.answers[kind][i]));
  return state;
}
export const hasChecks = state => [...state.checked.mcq,...state.checked.summary].some(Boolean);
export function markChecked(state, kind, indexes) {
  if (state.submittedAt) return;
  for (const index of indexes) if (Number.isInteger(index) && index >= 0 && index < state.checked[kind].length && cleanAnswer(state.answers[kind][index])) state.checked[kind][index]=true;
}
export function completed(state) {
  return [...state.answers.mcq,...state.answers.summary].filter(value=>String(value).trim()).length;
}
export function grade(state, key) {
  const items = [
    ...key.multipleChoice.map((q,index)=>({kind:'mcq',index,expected:q.answer,value:state.answers.mcq[index]})),
    ...key.summary.map((answer,index)=>({kind:'summary',index,expected:answer,value:state.answers.summary[index]}))
  ].map(q=>({...q,status:!cleanAnswer(q.value)?'blank':cleanAnswer(q.value)===cleanAnswer(q.expected)?'correct':'wrong'}));
  const count = status => items.filter(q=>q.status===status).length;
  return {items,total:items.length,correct:count('correct'),wrong:count('wrong'),blank:count('blank'),
    completion:Math.round(completed(state)/items.length*100),needsReview:items.filter(q=>q.status!=='correct')};
}
