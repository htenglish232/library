/* Shared source-only grading. Supplemental AI notes can never alter answers. */
(() => {
  'use strict';
  const normalize = value => value.toLowerCase().normalize('NFC').replace(/[’‘]/g,"'").replace(/[.,!?;:]/g,'').replace(/\s+/gu,' ').trim();
  function evaluate(question,value,fields=[]) {
    if(!question.autoGrade)return null;
    if(question.kind==='multi-text')return question.acceptedTuples.some(tuple=>tuple.length===fields.length && tuple.every((answer,i)=>normalize(answer)===normalize(fields[i])));
    if(question.kind==='choice')return question.accepted.includes(value);
    return question.accepted.some(answer=>normalize(answer)===normalize(value));
  }
  function validate(data) {
    if(data?.schemaVersion!==1 || !data.exam?.id || !Array.isArray(data.sections) || !Array.isArray(data.questions) || !data.questions.length)throw Error('Dữ liệu đề chưa hợp lệ.');
    const sections=new Set(data.sections.map(s=>s.id)),ids=new Set();
    if(sections.size!==data.sections.length)throw Error('Mã phần bị trùng.');
    for(const q of data.questions){
      if(ids.has(q.id)||!sections.has(q.section)||!q.promptHtml||!['choice','text','multi-text','rearrange'].includes(q.kind))throw Error(`Câu ${q.id} thiếu dữ liệu hoặc sai cấu trúc.`);
      ids.add(q.id);
      if(q.kind==='choice'&&(!q.options.length||!q.options.some(o=>q.accepted.includes(o.value))))throw Error(`Câu ${q.id} thiếu phương án/đáp án.`);
      if(q.kind==='rearrange'&&(!Array.isArray(q.tokens)||!q.tokens.length))throw Error(`Câu ${q.id} thiếu thẻ từ.`);
      if(q.kind==='multi-text'&&(!q.inputCount||!q.acceptedTuples?.every(t=>t.length===q.inputCount)))throw Error(`Câu ${q.id} thiếu ô trả lời.`);
      if(q.autoGrade && !q.accepted.length && !q.acceptedTuples?.length)throw Error(`Câu ${q.id} thiếu đáp án để tự chấm.`);
      if(q.track&&!data.tracks.some(t=>t.id===q.track&&t.src&&t.transcriptHtml))throw Error(`Câu ${q.id} thiếu audio/transcript.`);
      if(q.context!==undefined&&!data.contexts[q.context])throw Error(`Câu ${q.id} thiếu đoạn đọc.`);
    }
    return true;
  }
  globalThis.HTPracticeModel={normalize,evaluate,validate};
})();
