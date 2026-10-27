/* Shared dual-mode session model. No DOM, storage, network or score counters. */
(() => {
  'use strict';
  const copy = value => JSON.parse(JSON.stringify(value));
  const identity = (name,code='') => {
    if(typeof name!=='string'||typeof code!=='string')throw Error('Thông tin học sinh không hợp lệ.');
    name=name.normalize('NFC').replace(/\s+/gu,' ').trim();code=code.normalize('NFC').trim();
    if(!name||name.length>80||code.length>40)throw Error('Em hãy nhập họ tên hợp lệ.');
    return {name,code,key:JSON.stringify([name.toLocaleLowerCase('vi'),code.toLocaleLowerCase('vi')])};
  };
  const blank = q => ({value:'',fields:Array(q.inputCount||1).fill(''),tokens:[]});
  const question = (data,id) => {const q=data.questions.find(q=>q.id===id);if(!q)throw Error('Không tìm thấy câu hỏi.');return q;};
  function validDraft(q,draft) {
    if(!draft||typeof draft.value!=='string'||draft.value.length>1500||!Array.isArray(draft.fields)||draft.fields.length!==(q.inputCount||1)||draft.fields.some(v=>typeof v!=='string'||v.length>1500)||!Array.isArray(draft.tokens))throw Error('Bản nháp không hợp lệ.');
    if(new Set(draft.tokens).size!==draft.tokens.length||draft.tokens.some(i=>!Number.isInteger(i)||i<0||i>=(q.tokens?.length||0)))throw Error('Thẻ từ không hợp lệ.');
    if(q.kind==='choice' && draft.value && !q.options.some(o=>o.value===draft.value))throw Error('Lựa chọn không hợp lệ.');
    return copy(draft);
  }
  function complete(q,draft) {
    if(q.kind==='rearrange')return draft.tokens.length===q.tokens.length;
    if(q.kind==='multi-text')return draft.fields.every(v=>v.trim());
    return !!draft.value.trim();
  }
  const value = (q,draft) => q.kind==='rearrange'?draft.tokens.map(i=>q.tokens[i]).join(' '):draft.value;
  function result(q,draft) {
    const correct=HTPracticeModel.evaluate(q,value(q,draft),draft.fields);
    return correct===null?'pending':correct?'correct':'wrong';
  }
  function lock(first) {
    Object.freeze(first.draft.fields);Object.freeze(first.draft.tokens);Object.freeze(first.draft);return Object.freeze(first);
  }
  function create(data,student) {
    HTPracticeModel.validate(data);student=identity(student.name,student.code);
    return {schemaVersion:1,examId:data.exam.id,contentVersion:data.contentVersion,student,
      mode:'challenge',section:data.questions[0].section,cursorId:data.questions[0].id,view:'challenges',review:false,reviewIds:[],
      answers:Object.fromEntries(data.questions.map(q=>[q.id,{draft:blank(q),first:null,review:{draft:blank(q),checked:false,result:null}}]))};
  }
  function draft(data,state,id) {
    question(data,id);const a=state.answers[id];
    return state.review?a.review.draft:a.first?.draft||a.draft;
  }
  const locked = (state,id) => state.review?state.answers[id].review.checked:!!state.answers[id].first;
  function update(data,state,id,next) {
    if(locked(state,id))return false;
    const q=question(data,id),a=state.answers[id],normalized=validDraft(q,next);
    if(state.review)a.review.draft=normalized;else a.draft=normalized;
    return true;
  }
  function check(data,state,id) {
    if(locked(state,id))return false;
    const q=question(data,id),a=state.answers[id],given=validDraft(q,draft(data,state,id));
    if(!complete(q,given))throw Error(q.kind==='rearrange'?'Em hãy ghép đủ các thẻ trước khi kiểm tra.':'Em hãy trả lời đầy đủ trước khi kiểm tra.');
    const outcome=result(q,given);
    if(state.review){
      if(!a.first||a.first.result==='correct')throw Error('Chỉ ôn lại câu đã kiểm tra cần luyện thêm.');
      a.review.checked=true;a.review.result=outcome;
    } else a.first=lock({draft:given,result:outcome});
    return true;
  }
  function summary(data,state) {
    const first=data.questions.map(q=>state.answers[q.id].first);
    const correct=first.filter(a=>a?.result==='correct').length;
    return {total:data.questions.length,checked:first.filter(Boolean).length,correct,wrong:first.filter(a=>a?.result==='wrong').length,
      pending:first.filter(a=>a?.result==='pending').length,unanswered:first.filter(a=>!a).length,xp:correct*10,
      reviewIds:data.questions.filter(q=>state.answers[q.id].first&&state.answers[q.id].first.result!=='correct').map(q=>q.id)};
  }
  function list(data,state) {
    return state.review?data.questions.filter(q=>state.reviewIds.includes(q.id)):state.mode==='ordered'?data.questions:data.questions.filter(q=>q.section===state.section);
  }
  function go(data,state,id) {
    const q=question(data,id);if(state.review&&!state.reviewIds.includes(id))state.review=false;
    state.cursorId=id;state.section=q.section;state.view='play';
  }
  function setMode(data,state,mode) {
    if(!['challenge','ordered'].includes(mode))throw Error('Chế độ chưa hợp lệ.');
    state.review=false;state.mode=mode;state.section=question(data,state.cursorId).section;
  }
  function beginReview(data,state) {
    state.reviewIds=summary(data,state).reviewIds;if(!state.reviewIds.length)return false;
    for(const id of state.reviewIds)state.answers[id].review={draft:blank(question(data,id)),checked:false,result:null};
    state.review=true;state.cursorId=state.reviewIds[0];state.section=question(data,state.cursorId).section;state.view='play';return true;
  }
  function restore(data,student,raw) {
    const state=create(data,student);
    if(!raw||raw.schemaVersion!==1||raw.examId!==data.exam.id||raw.contentVersion!==data.contentVersion||raw.student?.key!==state.student.key)throw Error('Bản lưu thuộc đề hoặc học sinh khác, hay phiên bản đề đã thay đổi.');
    if(!['challenge','ordered'].includes(raw.mode)||!['challenges','play','results'].includes(raw.view)||typeof raw.review!=='boolean'||!Array.isArray(raw.reviewIds)||!raw.answers||Object.keys(raw.answers).length!==data.questions.length)throw Error('Bản lưu thiếu dữ liệu.');
    for(const q of data.questions){
      const a=raw.answers[q.id];if(!a||!a.review||typeof a.review.checked!=='boolean')throw Error('Thiếu câu trong bản lưu.');
      state.answers[q.id].draft=validDraft(q,a.draft);
      if(a.first!==null){
        const given=validDraft(q,a.first?.draft);
        if(!complete(q,given)||a.first.result!==result(q,given))throw Error('Kết quả lần đầu không khớp đáp án đã lưu.');
        state.answers[q.id].first=lock({draft:given,result:a.first.result});
      }
      const review={draft:validDraft(q,a.review.draft),checked:a.review.checked,result:a.review.result};
      if(review.checked && (!state.answers[q.id].first||state.answers[q.id].first.result==='correct'||!complete(q,review.draft)||review.result!==result(q,review.draft)))throw Error('Kết quả ôn lại không hợp lệ.');
      if(!review.checked&&review.result!==null)throw Error('Trạng thái ôn lại không hợp lệ.');
      state.answers[q.id].review=review;
    }
    const candidates=summary(data,state).reviewIds;
    if(new Set(raw.reviewIds).size!==raw.reviewIds.length||raw.reviewIds.some(id=>!candidates.includes(id)))throw Error('Danh sách ôn chưa hợp lệ.');
    question(data,raw.cursorId);
    if(raw.review&&!raw.reviewIds.includes(raw.cursorId))throw Error('Vị trí ôn chưa hợp lệ.');
    if(!data.sections.some(s=>s.id===raw.section))throw Error('Phần đang học không hợp lệ.');
    return {...state,mode:raw.mode,section:question(data,raw.cursorId).section,cursorId:raw.cursorId,view:raw.view,review:raw.review,reviewIds:[...raw.reviewIds]};
  }
  globalThis.HTDualProgress={identity,blank,create,draft,locked,update,check,summary,list,go,setMode,beginReview,restore,value};
})();
