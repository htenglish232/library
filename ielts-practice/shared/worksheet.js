import {newState, restore, stepsFor, storageKey, completed, grade, cleanAnswer, wordCount, hasChecks, markChecked} from './model.js';

const $ = id => document.getElementById(id);
const el = (tag, text, className) => {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
};
const sections = [
  'Vocabulary & Passages', 'Reading Practice', 'Multiple Choice', 'Summary Completion', 'Translation'
];
let unit, key, support, keyPromise, state, steps, review = null, submitting = false, checking = false;
const statusLabels = {correct:'Đúng', wrong:'Sai', blank:'Bỏ trống'};
function storageWarning(message) { $('storage-message').hidden = false; $('storage-message').textContent = message; }
function save() {
  try { localStorage.setItem(storageKey(unit),JSON.stringify(state)); }
  catch { storageWarning('Trình duyệt không lưu được tiến độ. Hãy giữ trang mở và sao chép bài dịch trước khi rời trang.'); }
}
async function json(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Không tải được ${url} (${response.status}).`);
  return response.json();
}
async function loadKey() {
  if (key && support) return key;
  if (!keyPromise) keyPromise = Promise.all([
    window.HT_IELTS_PREVIEW?.answers || json('./answers.json'),
    window.HT_IELTS_PREVIEW?.support || json('./support.json')
  ]).then(([answers, notes])=>{key=answers;support=notes;return key;}).finally(()=>{keyPromise=null;});
  return keyPromise;
}
function activeStep() { return review ? review.items[review.cursor] : steps[state.step]; }
function activeAnswers() { return review ? review.drafts : state.answers; }
function updateProgress() {
  const done = completed(state);
  const checked=[...state.checked.mcq,...state.checked.summary].filter(Boolean).length;
  $('completion-label').textContent = `${done}/20 câu đã trả lời${checked?` · ${checked} đã kiểm tra`:''}`;
  $('completion-progress').value = done;
}
function view(name) {
  state.view = name;
  for (const id of ['welcome','work','results']) $(id).hidden = id==='work'?!['work','vocabulary'].includes(name):id!==name;
  document.documentElement.classList.toggle('vocabulary-document-open',name==='vocabulary');
  $('navigation').hidden = name !== 'work';
  $('student-label').textContent = state.name;
  save();
}
function stepLabel(step) {
  if (step.kind === 'vocabulary') return 'A · Vocabulary & Passages';
  if (step.kind === 'reading') return 'B · Reading';
  if (step.kind === 'mcq') return `C · Câu ${step.index+1}`;
  if (step.kind === 'summary') return review ? `D · Ô ${step.index+1}` : 'D · Summary';
  return 'E · Translation';
}
function go(index, focus = true) {
  window.speechSynthesis?.cancel();
  if (review) review.cursor = Math.max(0,Math.min(review.items.length-1,index));
  else state.step = Math.max(0,Math.min(steps.length-1,index));
  $('step-picker').open = false;
  if(!state.started && activeStep().kind!=='vocabulary') {
    view('welcome');window.scrollTo(0,0);$('student-name').focus();return;
  }
  renderWork();
  if (focus) { window.scrollTo(0,0); $('task-title').focus({preventScroll:true}); }
}
function renderSteps() {
  $('step-list').replaceChildren();
  (review ? review.items : steps).forEach((step,index) => {
    const button = el('button',stepLabel(step));
    button.setAttribute('aria-current',String(index === (review ? review.cursor : state.step)));
    button.onclick = () => go(index);
    $('step-list').append(button);
  });
}
function reading() {
  if (!$('reading-text').childElementCount) {
    unit.reading.forEach((text,index) => {
      const p = el('p'); const mark = el('button',String(index+1),'paragraph-mark');
      mark.setAttribute('aria-label',`Đánh dấu đoạn ${index+1}`);
      mark.onclick = () => { state.readingMark = state.readingMark === index ? -1 : index; save(); reading(); };
      p.append(mark,document.createTextNode(text)); $('reading-text').append(p);
    });
  }
  [...$('reading-text').children].forEach((p,index) => {
    p.classList.toggle('marked',state.readingMark===index);
    p.querySelector('button').setAttribute('aria-pressed',String(state.readingMark===index));
  });
}
function vocabularyDocument() {
  $('task-title').textContent='Vocabulary & Passages';
  const actions=el('nav',undefined,'document-actions');actions.setAttribute('aria-label','Điều hướng tài liệu');
  const overview=el('button','← Tổng quan Unit 2','quiet');overview.id='vocabulary-overview';
  overview.onclick=()=>{view('welcome');window.scrollTo(0,0);};
  const reading=el('button','Reading Practice →','primary');reading.id='vocabulary-reading-top';reading.onclick=()=>go(1);
  actions.append(overview,reading);$('task-content').append(actions);
  const content=el('div',undefined,'vocabulary-document');content.id='vocabulary-document';
  unit.passages.forEach(source=>{
    const section=el('section',undefined,'passage-section');section.id=`passage-${source.number}`;
    const title=el('h3',`Passage ${source.number}: ${source.title}`);title.lang='en';
    const p=el('p',source.text,'passage-copy');p.lang='en';
    const heading=el('h4','Vocabulary:');heading.lang='en';
    const words=el('ul',undefined,'vocabulary-list');
    source.vocabulary.forEach(word=>{
      const item=el('li'),term=el('strong',word.term);term.lang='en';
      item.append(term,document.createTextNode(` – ${word.meaning}${word.synonyms?` (synonym: ${word.synonyms})`:''}`));
      words.append(item);
    });
    section.append(title,p,heading,words);content.append(section);
  });
  const summary=el('section',undefined,'vocabulary-summary-section');summary.id='vocabulary-summary';
  const heading=el('h3','Vocabulary Summary');heading.lang='en';
  const list=el('ul');list.lang='en';unit.vocabularySummary.forEach(word=>list.append(el('li',word)));
  summary.append(heading,list);content.append(summary);$('task-content').append(content);
  const next=el('button','Chuyển sang Reading Practice →','primary');next.id='vocabulary-reading';next.onclick=()=>go(1);
  $('task-content').append(next);
}
function answerChanged(kind,index,value) {
  if (state.submittedAt && !review) return;
  if (!review && state.checked[kind][index]) return;
  activeAnswers()[kind][index] = value;
  if (review) {
    delete review.checked[`${kind}-${index}`];
    $('review-result')?.remove();
    $('review-support')?.remove();
  } else { save(); updateProgress(); }
}
function resultFor(kind,index) { return grade(state,key).items.find(item=>item.kind===kind && item.index===index); }
function feedbackFor(kind,index) {
  const box = $('feedback'); box.hidden=false;
  const result = resultFor(kind,index);
  box.append(el('h3',`${statusLabels[result.status]} · Đáp án: ${result.expected}`,result.status==='correct'?'correct-label':'wrong-label'));
  box.append(el('p',`${state.submittedAt?'Bài làm đã nộp':'Đáp án lần kiểm tra đầu'}: ${result.value.trim() || 'Chưa trả lời'}`,'muted'));
  if (kind==='mcq') {
    const correctOption=unit.multipleChoice[index].options.find(option=>option.value===result.expected);
    const answer=el('p',`${result.expected}. ${correctOption.text}`);answer.lang='en';box.append(answer);
    box.append(el('h4','Giải thích từ file đáp án'),el('p',key.multipleChoice[index].explanation));
  }
  appendSupport(box,kind,index);
}
function highlighted(text, words) {
  const fragment=document.createDocumentFragment();let offset=0;
  while(offset<text.length) {
    const next=words.map(word=>({word,index:text.toLowerCase().indexOf(word.toLowerCase(),offset)}))
      .filter(match=>match.index>=0).sort((a,b)=>a.index-b.index || b.word.length-a.word.length)[0];
    if(!next){fragment.append(document.createTextNode(text.slice(offset)));break;}
    fragment.append(document.createTextNode(text.slice(offset,next.index)),el('mark',text.slice(next.index,next.index+next.word.length)));
    offset=next.index+next.word.length;
  }
  return fragment;
}
function appendSupport(target,kind,index) {
  const item=support[kind][index],section=el('section',undefined,'answer-support');
  section.append(el('h4','Keywords · Từ khóa trong nguồn'));
  const words=el('div',undefined,'keyword-list');words.lang='en';
  item.keywords.forEach(word=>words.append(el('span',word)));section.append(words);
  section.append(el('h4',kind==='mcq'?'Dẫn chứng trong Reading':'Đối chiếu câu Summary theo file đáp án'));
  item.quotes.forEach(quote=>{
    let text=quote.text;
    // Keep unrelated, unchecked Summary answers concealed in shared sentences.
    if(kind==='summary' && !state.submittedAt) key.summary.forEach((answer,n)=>{
      if(!state.checked.summary[n])text=text.split(`${answer} (${n+1})`).join(`__________(${n+1})`);
    });
    const block=el('blockquote'),p=el('p');p.lang='en';p.append(highlighted(text,item.keywords));
    block.append(p,el('cite',`${quote.source==='reading'?'Reading Practice':'Summary — file đáp án'} · Đoạn ${quote.paragraph}`));section.append(block);
  });
  if(kind==='summary' && [1,2,3].includes(index)) {
    const note=index===3?'Lưu ý giáo viên: giữ nguyên “reduced family relationships” và đáp án “relationships” theo nguồn đã xác nhận.':
      state.submittedAt || state.checked.summary[1] && state.checked.summary[2] ? 'Lưu ý giáo viên: từ “support” được dùng cho cả ô 2 và 3 theo đáp án nguồn.' :
      'Lưu ý giáo viên: Word Bank cho phép dùng lại một từ theo nguồn đã xác nhận.';
    section.append(el('p',note,'notice'));
  }
  target.append(section);
}
function renderCheck(kind,index) {
  const indexes=kind==='mcq'?[index]:state.checked.summary.map((_,i)=>i);
  const allChecked=indexes.every(i=>state.checked[kind][i]);
  const button=el('button',allChecked?'Đã kiểm tra ✓':checking?'Đang kiểm tra…':'Kiểm tra đáp án ✓','primary check-answer');
  button.id='check-answer';button.disabled=checking || allChecked;
  const error=el('p',undefined,'check-error');error.id='check-error';error.setAttribute('role','alert');
  const hint=el('p',kind==='summary'?'Kiểm tra các ô đã nhập; ô trống có thể điền tiếp. Ô đã kiểm tra giữ đáp án lần đầu.':'Sau khi kiểm tra, câu này giữ đáp án lần đầu. Em có thể ôn lại sau khi nộp bài.','muted small');
  button.onclick=async()=>{
    const target=state,pending=indexes.filter(i=>!target.checked[kind][i] && cleanAnswer(target.answers[kind][i]));
    if(!pending.length){error.textContent=kind==='mcq'?'Em hãy chọn một đáp án trước khi kiểm tra.':'Em hãy nhập ít nhất một ô chưa kiểm tra.';return;}
    const snapshot=pending.map(i=>target.answers[kind][i]);
    checking=true;button.disabled=true;button.textContent='Đang kiểm tra…';
    try {
      await loadKey();
      if(state===target && !state.submittedAt) {
        markChecked(state,kind,pending.filter((i,n)=>state.answers[kind][i]===snapshot[n]));save();
      }
    } catch {error.textContent='Chưa tải được đáp án hoặc dẫn chứng. Bài làm vẫn được giữ nguyên; em hãy thử lại.';}
    finally {
      checking=false;
      if(state===target && state.view==='work' && key && support) {
        renderWork();if(activeStep().kind===kind)$('feedback').scrollIntoView({block:'nearest'});
      } else {button.disabled=false;button.textContent='Kiểm tra đáp án ✓';}
    }
  };
  $('task-content').append(button,hint,error);
}
function multipleChoice(step) {
  const q=unit.multipleChoice[step.index]; $('task-title').textContent=q.question;
  $('task-title').lang='en';
  const options=el('fieldset',undefined,'options'); options.append(el('legend','Chọn một đáp án'));
  q.options.forEach(option => {
    const label=el('label',undefined,'option');
    const input=el('input');input.type='radio';input.name=`mcq-${step.index}`;input.value=option.value;
    input.checked=activeAnswers().mcq[step.index]===option.value;input.disabled=!review && (!!state.submittedAt || state.checked.mcq[step.index]);
    input.onchange=()=>answerChanged('mcq',step.index,input.value);
    const text=el('span');text.lang='en';text.append(el('b',option.value+'.'),document.createTextNode(option.text));
    if (!review && (state.submittedAt || state.checked.mcq[step.index])) {
      label.classList.toggle('correct',option.value===key.multipleChoice[step.index].answer);
      label.classList.toggle('wrong',input.checked && option.value!==key.multipleChoice[step.index].answer);
    }
    label.append(input,text);options.append(label);
  });
  $('task-content').append(options);
  if (review) reviewCheck('mcq',step.index);
  else {
    if(!state.submittedAt)renderCheck('mcq',step.index);
    if(state.submittedAt || state.checked.mcq[step.index])feedbackFor('mcq',step.index);
  }
}
function summaryCompletion(step) {
  $('task-title').textContent='Summary Completion';
  const instructions=el('p',unit.summary.instructions);instructions.lang='en';
  const bank=el('section',undefined,'word-bank');bank.setAttribute('aria-label','Word Bank');bank.append(el('h3','WORD BANK'));
  const words=el('p',unit.summary.wordBankText);words.lang='en';bank.append(words,el('p','Có thể dùng lại một từ trong nhiều chỗ trống.','muted'));
  $('task-content').append(instructions,bank);
  unit.summary.paragraphs.forEach(text => {
    const p=el('p',undefined,'summary-copy');p.lang='en';
    const chunks=text.split(/__________\((\d+)\)/g);
    chunks.forEach((chunk,index)=>{
      if(index%2===0) {p.append(document.createTextNode(chunk));return;}
      const n=Number(chunk)-1, wrapper=el('label',undefined,'summary-blank'), input=el('input');
      input.type='text';input.id=`blank-${n+1}`;input.maxLength=100;input.autocomplete='off';input.spellcheck=false;
      input.setAttribute('aria-label',`Summary ô ${n+1}`);input.value=activeAnswers().summary[n];
      input.disabled=review?n!==step.index:!!state.submittedAt || state.checked.summary[n];
      input.oninput=()=>answerChanged('summary',n,input.value);
      if (!review && (state.submittedAt || state.checked.summary[n])) input.classList.add(resultFor('summary',n).status);
      wrapper.append(input,el('span',`(${n+1})`));p.append(wrapper);
    });
    $('task-content').append(p);
  });
  if(review) reviewCheck('summary',step.index);
  else {
    if(!state.submittedAt)renderCheck('summary');
    if(!state.submittedAt && !state.checked.summary.some(Boolean))return;
    const box=$('feedback');box.hidden=false;box.append(el('h3','Đối chiếu theo đáp án nguồn'));
    key.summary.forEach((answer,index)=>{
      if(!state.submittedAt && !state.checked.summary[index])return;
      const q=resultFor('summary',index);
      const detail=el('details',undefined,'summary-feedback');
      detail.open=index===(state.submittedAt?0:state.checked.summary.findIndex(Boolean));
      detail.append(el('summary',`Ô ${index+1} · ${statusLabels[q.status]} · ${q.value.trim() || 'Chưa trả lời'} → ${answer}`));
      appendSupport(detail,'summary',index);box.append(detail);
    });
    if(!state.submittedAt)return;
    const original=el('details');original.append(el('summary','Đoạn văn hoàn chỉnh theo file đáp án'));
    key.completedSummary.forEach(text=>{const p=el('p',text);p.lang='en';original.append(p);});box.append(original);
    box.append(el('p',key.sourceNote,'notice'));
  }
}
function reviewCheck(kind,index) {
  const button=el('button','Kiểm tra lại','primary');button.id='review-check';
  button.onclick=()=>{
    const expected=kind==='mcq'?key.multipleChoice[index].answer:key.summary[index];
    const correct=cleanAnswer(review.drafts[kind][index])===cleanAnswer(expected);
    review.checked[`${kind}-${index}`]=correct;
    $('review-result')?.remove();const text=el('p',correct?'Đúng rồi.':`Đáp án nguồn: ${expected}`,correct?'correct-label':'wrong-label');
    text.id='review-result';text.setAttribute('role','status');button.after(text);
    if(kind==='mcq')text.append(el('span',' '+key.multipleChoice[index].explanation));
    $('review-support')?.remove();const evidence=el('div');evidence.id='review-support';appendSupport(evidence,kind,index);text.after(evidence);
  };
  $('task-content').append(button);
}
function translation() {
  $('task-title').textContent=unit.translation.instruction;
  const prompt=el('p',unit.translation.text,'translation-prompt');prompt.lang='vi';
  const label=el('label','Bài dịch của em');label.htmlFor='translation-input';
  const area=el('textarea');area.id='translation-input';area.lang='en';area.maxLength=20000;area.value=state.answers.translation;
  area.disabled=!!state.submittedAt;area.setAttribute('aria-describedby','translation-note');
  const count=el('span',`${wordCount(area.value)} từ`);count.id='word-count';count.setAttribute('role','status');
  area.oninput=()=>{state.answers.translation=area.value;save();count.textContent=`${wordCount(area.value)} từ`;};
  const note=el('p','Bài tự luận do giáo viên đánh giá; không chấm bằng so khớp văn bản, không gán IELTS Band Score.','muted small');note.id='translation-note';
  $('task-content').append(prompt,label,area,count,note);
  if(state.submittedAt)appendReference($('task-content'));
}
function renderWork() {
  const step=activeStep(),isDocument=step.kind==='vocabulary';view(isDocument?'vocabulary':'work');updateProgress();renderSteps();
  $('task-content').replaceChildren();$('feedback').replaceChildren();$('feedback').hidden=true;
  $('task-title').lang='vi';$('task-kicker').textContent=review?`ÔN LẠI · ${stepLabel(step)}`:`${step.section} · ${sections['ABCDE'.indexOf(step.section)]}`;
  if(isDocument)$('task-kicker').textContent=`UNIT ${unit.number} · ${unit.title}`;
  $('task').classList.toggle('document-paper',isDocument);
  $('step-picker').hidden=isDocument;document.querySelector('.progress-line').hidden=isDocument;
  $('reading-panel').hidden=!['mcq','reading'].includes(step.kind);
  $('task').hidden=step.kind==='reading';
  $('workspace').classList.toggle('with-reading',step.kind==='mcq');
  $('workspace').classList.toggle('reading-only',step.kind==='reading');
  $('review-banner').hidden=!review;
  $('submit-open').hidden=isDocument || !!state.submittedAt;$('results-open').hidden=isDocument || !state.submittedAt;
  if(['mcq','reading'].includes(step.kind))reading();
  if(isDocument)vocabularyDocument();
  if(step.kind==='mcq')multipleChoice(step);
  if(step.kind==='summary')summaryCompletion(step);
  if(step.kind==='translation')translation();
  const position=review?review.cursor:state.step, length=review?review.items.length:steps.length;
  $('previous').disabled=position===0;
  $('position').textContent=review?`Ôn ${position+1}/${length}`:stepLabel(step);
  $('next').textContent=position===length-1?(state.submittedAt?'Kết quả →':'Nộp bài →'):'Next →';
  save();
}
function appendReference(target) {
  const p=el('p',key.referenceTranslation,'reference-translation');p.lang='en';
  const heading=el('h3','Reference Translation – Bài dịch tham khảo');
  const note=el('p','Một cách dịch tham khảo, không phải đáp án duy nhất.','muted small');
  const terms=el('dl');
  key.translationGlossary.forEach(term=>{const en=el('dd',term.en);en.lang='en';terms.append(el('dt',term.vi),en);});
  target.append(heading,note,p,terms);
}
function renderResults() {
  review=null;window.speechSynthesis?.cancel();view('results');
  const result=grade(state,key);
  $('result-student').textContent=`${state.name} · Unit ${unit.number} – ${unit.title}`;
  $('result-stats').replaceChildren();
  for(const [value,label] of [[result.total,'Câu tự chấm'],[result.correct,'Đúng'],[result.wrong,'Sai'],[result.blank,'Bỏ trống']]) {
    const stat=el('div',undefined,'stat');stat.append(el('strong',String(value)),el('span',label));$('result-stats').append(stat);
  }
  $('result-completion').textContent=`Đã trả lời ${completed(state)}/${result.total} câu · Hoàn thành ${result.completion}%. Điểm tự động: ${result.correct}/${result.total}.`;
  $('review-wrong').disabled=result.needsReview.length===0;
  $('review-wrong').textContent=result.needsReview.length?`Ôn ${result.needsReview.length} câu cần luyện`:'Tất cả 20 câu đều đúng ✓';
  $('result-list').replaceChildren();
  result.items.forEach(q=>{
    const button=el('button',`${q.kind==='mcq'?'C · Câu':'D · Ô'} ${q.index+1} · ${statusLabels[q.status]}`,q.status);
    button.onclick=()=>{
      review=null;state.step=q.kind==='mcq'?steps.findIndex(s=>s.kind==='mcq'&&s.index===q.index):steps.findIndex(s=>s.kind==='summary');
      renderWork();window.scrollTo(0,0);
      if(q.kind==='summary')$(`blank-${q.index+1}`).scrollIntoView({block:'center'});
      else $('task-title').focus({preventScroll:true});
    };
    $('result-list').append(button);
  });
  $('result-translation').textContent=state.answers.translation || 'Chưa có bài dịch.';
  $('translation-status').textContent=`${wordCount(state.answers.translation)} từ · ${state.answers.translation.trim()?'Chờ giáo viên đánh giá':'Bỏ trống phần tự luận'}`;
  $('reference-content').replaceChildren();appendReference($('reference-content'));
  $('source-notes').replaceChildren(el('p','Theo xác nhận của giáo viên: giữ nguyên đề và đáp án nguồn, đồng thời giữ hai lưu ý Summary dưới đây.','notice'),el('p',key.sourceNote),el('p',unit.source.credit));
  window.scrollTo(0,0);$('results-title').focus({preventScroll:true});
}
function openSubmit() {
  $('submit-description').textContent=`Em đã trả lời ${completed(state)}/20 câu; còn ${20-completed(state)} câu bỏ trống. Bài dịch: ${wordCount(state.answers.translation)} từ.`;
  $('submit-error').textContent='';$('submit-dialog').showModal();
}
$('start-form').onsubmit=event=>{
  event.preventDefault();const name=$('student-name').value.trim();
  if(!name){$('student-name').setCustomValidity('Vui lòng nhập họ và tên.');$('student-name').reportValidity();return;}
  state.name=name;state.started=true;renderWork();window.scrollTo(0,0);
};
$('student-name').oninput=()=>{$('student-name').setCustomValidity('');state.name=$('student-name').value;save();};
$('previous').onclick=()=>go((review?review.cursor:state.step)-1);
$('next').onclick=()=>{
  const position=review?review.cursor:state.step,length=review?review.items.length:steps.length;
  if(position===length-1){if(state.submittedAt)renderResults();else openSubmit();}
  else go(position+1);
};
$('submit-open').onclick=openSubmit;
$('submit-cancel').onclick=()=>$('submit-dialog').close();
$('submit-confirm').onclick=async()=>{
  if(submitting)return;
  submitting=true;$('submit-confirm').disabled=true;
  try { await loadKey();state.submittedAt=new Date().toISOString();save();$('submit-dialog').close();renderResults(); }
  catch { $('submit-error').textContent='Chưa tải được đáp án. Bài làm vẫn được giữ nguyên; em hãy thử nộp lại khi kết nối ổn định.'; }
  finally{submitting=false;$('submit-confirm').disabled=false;}
};
$('results-open').onclick=renderResults;
$('view-solutions').onclick=()=>{review=null;go(steps.findIndex(s=>s.kind==='mcq'));};
$('review-wrong').onclick=()=>{
  review={items:grade(state,key).needsReview.map(q=>({...q,section:q.kind==='mcq'?'C':'D'})),cursor:0,drafts:structuredClone(state.answers),checked:{}};
  if(review.items.length)go(0);
};
$('restart').onclick=()=>$('restart-dialog').showModal();
$('restart-cancel').onclick=()=>$('restart-dialog').close();
$('restart-confirm').onclick=()=>{
  $('restart-dialog').close();state=newState(unit);review=null;save();
  $('student-name').value='';$('reference-details').open=false;view('welcome');window.scrollTo(0,0);$('student-name').focus();
};
// Match the useful GHK1 navigation behavior without importing its grading/XP model.
new ResizeObserver(()=>document.documentElement.style.setProperty('--nav-height',`${$('navigation').getBoundingClientRect().height || 80}px`)).observe($('navigation'));
function keyboardInset(){
  const viewport=window.visualViewport;
  const inset=viewport && viewport.scale===1?Math.max(0,innerHeight-viewport.height-viewport.offsetTop):0;
  document.documentElement.style.setProperty('--keyboard-inset',`${inset}px`);
}
window.visualViewport?.addEventListener('resize',keyboardInset);
window.visualViewport?.addEventListener('scroll',keyboardInset);
window.addEventListener('resize',keyboardInset);
window.addEventListener('pagehide',()=>{if(state)save();});
async function init(){
  try {
    unit=window.HT_IELTS_PREVIEW?.unit || await json('./unit.json');steps=stepsFor(unit);
    let raw=null;
    try {const text=localStorage.getItem(storageKey(unit));if(text)raw=JSON.parse(text);}
    catch{storageWarning('Không đọc được bản lưu cũ. Phiếu vẫn dùng được; tiến độ chỉ được giữ khi trình duyệt cho phép lưu.');}
    state=restore(unit,raw);
    $('student-name').value=state.name;
    sections.forEach((section,index)=>{
      const item=el('li');
      if(index===0){const button=el('button',section,'welcome-document-link');button.id='open-vocabulary';button.onclick=()=>go(0);item.append(button);}
      else item.textContent=section;
      $('welcome-sections').append(item);
    });
    $('load-message').hidden=true;
    if(state.submittedAt || hasChecks(state)){await loadKey();if(state.submittedAt && !['work','vocabulary'].includes(state.view))renderResults();else renderWork();}
    else if(state.started || state.view==='vocabulary')renderWork();else view('welcome');
    keyboardInset();
  } catch(error){$('load-message').hidden=false;$('load-message').textContent=`Không mở được phiếu. ${error.message} Hãy tải lại trang để thử lại.`;}
}
init();
