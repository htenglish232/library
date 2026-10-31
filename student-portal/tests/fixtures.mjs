import {data} from '../functions/src/grading.js';
const orders={q36:[3,5,1,0,2,4,6],q37:[1,5,2,0,3,6,7,4,8],q38:[1,6,2,0,3,7,4,5,8,9]};
export const correctAnswers=()=>Object.fromEntries(data.questions.map(q=>[q.id,{
  value:q.kind==='rearrange'?'':q.accepted?.[0]||'',
  fields:q.kind==='multi-text'?q.acceptedTuples[0]:[''],
  tokens:orders[q.id]||[]
}]));
