// Frozen pre-upgrade model, not the implementation under test, creates these saves.
import {readFileSync,globSync} from 'node:fs';
import vm from 'node:vm';
import {pathToFileURL} from 'node:url';
const shared='grade-8/De_thi_GHK1/shared-practice/';
export function runtime(legacy=false){
 const ctx=vm.createContext({});
 vm.runInContext(readFileSync(shared+'model.js','utf8'),ctx);
 vm.runInContext(readFileSync(legacy?'tests/fixtures/legacy-dual-progress.js':shared+'dual-progress.js','utf8'),ctx);
 vm.runInContext(readFileSync(shared+'dual-store.js','utf8'),ctx);
 return ctx;
}
export const student={name:'Học sinh trước nâng cấp',code:'saved-01'};
export function sourceGames(){
 return [...globSync('grade-{6,7,8}/**/*dual-data.js')].sort().map(path=>({path,data:JSON.parse(readFileSync(path,'utf8').split('window.HT_PRACTICE_DATA = ')[1].trim().slice(0,-1))}));
}
export function answer(P,M,q,wrong=false){
 const draft=P.blank(q);
 if(q.kind==='choice')draft.value=(wrong?q.options.find(o=>!q.accepted.includes(o.value))?.value:q.accepted[0])||q.options[0].value;
 else if(q.kind==='multi-text')draft.fields=wrong?draft.fields.map(()=> 'incorrect fixture'):q.acceptedTuples[0];
 else if(q.kind==='text')draft.value=wrong?'incorrect fixture':q.accepted[0]||'teacher review';
 else{
  function solve(indices,left){
   if(indices.length===q.tokens.length)return left.length?null:indices;
   for(let i=0;i<q.tokens.length;i++){
    const part=M.normalize(q.tokens[i]).split(' ').filter(Boolean);
    if(!indices.includes(i)&&part.every((v,j)=>left[j]===v)){
     const result=solve([...indices,i],left.slice(part.length));if(result)return result;
    }
   }return null;
  }
  draft.tokens=solve([],M.normalize(q.accepted[0]||'').split(' ').filter(Boolean))||q.tokens.map((_,i)=>i);
  if(wrong)draft.tokens.reverse();
 }
 return draft;
}
export function legacyRecords(data){
 const old=runtime(true),P=old.HTDualProgress,M=old.HTPracticeModel;
 const state=P.create(data,student);
 const auto=data.questions.filter(q=>q.autoGrade),good=auto[0],bad=auto[1];
 P.update(data,state,good.id,answer(P,M,good));P.check(data,state,good.id);
 P.update(data,state,bad.id,answer(P,M,bad,true));P.check(data,state,bad.id);
 const pending=data.questions.find(q=>!q.autoGrade);
 if(pending){P.update(data,state,pending.id,answer(P,M,pending));P.check(data,state,pending.id);}
 for(const q of data.questions.filter(q=>!state.answers[q.id].first)){
  const draft=P.blank(q);
  if(q.kind==='choice')draft.value=q.options[0].value;
  else if(q.kind==='rearrange')draft.tokens=[0];
  else if(q.kind==='multi-text')draft.fields[0]='bản nháp nhiều ô';
  else draft.value='bản nháp cũ chưa kiểm tra';
  P.update(data,state,q.id,draft);
 }
 P.go(data,state,data.questions.find(q=>!state.answers[q.id].first).id);
 state.view='challenges';
 const copy=s=>JSON.parse(JSON.stringify(s));
 const challenge=copy(state);
 P.setMode(data,state,'ordered');state.view='results';const ordered=copy(state);
 P.setMode(data,state,'challenge');P.beginReview(data,state);
 P.update(data,state,bad.id,answer(P,M,bad));
 const review=copy(state);
 P.check(data,state,bad.id);const checkedReview=copy(state);
 return {challenge,ordered,review,checkedReview};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 console.log(JSON.stringify(sourceGames().map(({path,data})=>({path,examId:data.exam.id,records:legacyRecords(data)}))));
}
