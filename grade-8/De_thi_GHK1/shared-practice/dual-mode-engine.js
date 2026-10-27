/* Shared full-exam controller. Legacy storage keys and source data stay compatible. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  // Capture the script URL now. currentScript is null in later callbacks/modules.
  const engineScriptURL=document.currentScript?.src || [...document.scripts].find(script=>{
    try{return new URL(script.src,document.baseURI).pathname.endsWith('/shared-practice/dual-mode-engine.js');}catch{return false;}
  })?.src;
  let soundModuleURL=null;
  try{
    if(engineScriptURL){soundModuleURL=new URL('./dual-sound.js',engineScriptURL);soundModuleURL.searchParams.set('v',new URL(engineScriptURL).searchParams.get('v')||'20261026-sound-fix');}
  }catch{ /* Show the loader error below; grading still initializes. */ }
  let sound=null,soundState='loading',soundAttempt=0;
  const soundToggle=$('sound-toggle')||document.createElement('button');
  soundToggle.id='sound-toggle';soundToggle.type='button';soundToggle.className='quiet';
  if(!soundToggle.isConnected)document.querySelector('.header-actions').append(soundToggle);
  const updateSoundToggle=()=>{
    const loading=soundState==='loading',failed=soundState==='error',ready=soundState==='ready';
    soundToggle.dataset.soundState=soundState;
    soundToggle.disabled=loading||soundState==='unsupported';
    soundToggle.textContent=failed?'⚠ Âm thanh: Lỗi tải':ready?(sound.enabled?'🔊 Âm thanh: Bật':'🔇 Âm thanh: Tắt'):loading?'🔊 Âm thanh: Bật':'Âm thanh không khả dụng';
    soundToggle.setAttribute('aria-busy',String(loading));
    soundToggle.setAttribute('aria-pressed',String(ready?sound.enabled:loading));
    soundToggle.title=failed?'Chưa tải được hiệu ứng âm thanh. Nhấn để thử lại.':loading?'Đang tải hiệu ứng âm thanh…':ready?'Bật/tắt hiệu ứng; không thay đổi âm thanh bài nghe.':'Trình duyệt chưa hỗ trợ Web Audio.';
  };
  function loadSound(){
    const attempt=++soundAttempt;soundState='loading';soundToggle.onclick=null;updateSoundToggle();
    const fail=()=>{if(attempt!==soundAttempt||soundState!=='loading')return;sound=null;soundState='error';soundToggle.onclick=loadSound;updateSoundToggle();};
    if(!soundModuleURL){fail();return;}
    const url=new URL(soundModuleURL);
    if(attempt>1)url.searchParams.set('retry',String(attempt));
    const timer=setTimeout(fail,10000);
    import(url.href).then(({createGameSound,SOUND_PREFERENCE_KEY})=>{
      if(attempt!==soundAttempt||soundState!=='loading')return;
      clearTimeout(timer);sound=createGameSound();soundState=sound.supported?'ready':'unsupported';updateSoundToggle();
      soundToggle.onclick=()=>{sound.setEnabled(!sound.enabled);updateSoundToggle();};
      window.addEventListener('storage',event=>{
        if(event.key===SOUND_PREFERENCE_KEY||event.key===null){
          let value=event.newValue;
          if(event.key===null)try{value=localStorage.getItem(SOUND_PREFERENCE_KEY);}catch{return;}
          sound.setEnabled(value!=='off',false);updateSoundToggle();
        }
      });
    }).catch(()=>{clearTimeout(timer);fail();});
  }
  loadSound();
  const source = window.HT_PRACTICE_DATA;
  try {HTPracticeModel.validate(source);} catch(error) {
    $('name-error').textContent='Dữ liệu đề chưa thể mở. Hãy báo giáo viên: '+error.message;
    $('start-form').querySelector('button').disabled=true;
    return;
  }
  const support = window.HT_PRACTICE_SUPPORT || {items:{}};
  const questions = source.questions;
  const sections = source.sections.map((s,i)=>({...s,short:s.title,color:['#e5f3fc','#e8f5ee','#f1edfb','#fff4d9'][i%4]}));
  const P=HTDualProgress;
  let state=null,store=null,pendingStudent=null,conflict=false;
  // Launchers share this controller; remove obsolete UI once for every game.
  document.querySelectorAll('.mode-options,#play-mode,#challenges,#back-menu,#section-tabs,#toggle-passage').forEach(el=>{
    if(el.id==='play-mode')el.closest('label').remove();else el.remove();
  });
  $('home-button').textContent='Làm toàn bộ đề';
  $('continue-playing').textContent='Tiếp tục làm đề';
  $('section-progress').setAttribute('aria-label','Tiến độ toàn đề');
  document.querySelector('#welcome .privacy-note').textContent='Tiến độ chỉ lưu trên thiết bị này. Không gửi tên, mã riêng hoặc kết quả đến dịch vụ bên ngoài.';
  const audio=$('audio-player');let currentTrack=0;
  const bySection=id=>questions.filter(q=>q.section===id);
  const activeQuestions=()=>P.list(source,state);
  const currentQuestion=()=>questions.find(q=>q.id===state.cursorId);
  const currentIndex=()=>activeQuestions().findIndex(q=>q.id===state.cursorId);
  const totalChecked=()=>P.summary(source,state).checked;
  const totalCorrect=()=>P.summary(source,state).correct;
  const isLocked=a=>state.review?a.review.checked:!!a.first;
  const correctNow=a=>state.review?a.review.result==='correct':a.first?.result==='correct';
  const firstCorrect=a=>a.first?.result==='correct';
  const text = (tag,value,className) => {const el=document.createElement(tag);el.textContent=value;if(className)el.className=className;return el;};
  function pauseAudio() {audio.pause();}
  function showPage(id) {
    for(const page of ['welcome','play','results']) $(page).hidden=page!==id;
    if(id!=='play') pauseAudio();
    $('home-button').hidden=!state.student.name;
    $('results-button').hidden=!state.student.name;
    $('student-label').textContent=state.student.name;
    $('xp-total').textContent=`✦ ${totalCorrect()*10} XP`;
    $('session-tools').hidden=false;
    state.view=id;persist();
    $('main').focus({preventScroll:true});
    window.scrollTo({top:0,behavior:'instant'});
  }
  function showExam() {showPage('play');renderQuestion();}
  function move(index){const q=activeQuestions()[index];if(q){P.go(source,state,q.id);renderQuestion();$('question-title').focus({preventScroll:true});}}
  function writeDraft(q,next){if(conflict)return;if(P.update(source,state,q.id,next))persist();}
  function renderQuestion() {
    const list=activeQuestions(),q=currentQuestion();
    if(!q) {showResults();return;}
    const section=sections.find(s=>s.id===q.section),a=state.answers[q.id];
    state.view='play';persist();
    $('question-card').dataset.questionId=q.id;
    $('section-title').textContent=state.review?'Ôn lại câu cần luyện':'Làm toàn bộ đề';
    $('section-description').textContent=state.review?'Thử lại sau khi đọc lời giải. Lượt ôn không thay đổi XP và kết quả lần đầu.':section.description;
    const gradeLabel=[6,7].includes(source.exam.grade)?`GRADE ${source.exam.grade}`:'GRADE 8';
    $('section-kicker').textContent=state.review?'PRACTICE MAKES PROGRESS':`THEO THỨ TỰ ĐỀ GỐC · ${gradeLabel}`;
    const done=list.filter(item=>state.review?state.answers[item.id].review.checked:!!state.answers[item.id].first).length;
    $('question-position').textContent=`Câu ${currentIndex()+1} / ${list.length}`;
    $('section-progress').max=list.length;$('section-progress').value=done;
    $('section-score').textContent=`${done} đã luyện`;
    $('question-dots').replaceChildren();
    list.forEach((item,i)=>{
      const answer=state.answers[item.id];const checked=state.review?answer.review.checked:!!answer.first;
      const button=text('button',String(item.number));
      button.dataset.questionId=item.id;button.setAttribute('aria-label',`Đến câu ${item.number}${checked?(correctNow(answer)?' – đúng':' – cần ôn'):''}`);
      button.disabled=conflict;
      button.setAttribute('aria-current',String(i===currentIndex()));
      if(checked)button.className=correctNow(answer)?'correct':'wrong';
      button.onclick=()=>move(i);$('question-dots').append(button);
    });
    $('jump-question').replaceChildren();
    (state.review?list:questions).forEach(item=>{const option=text('option',`Câu ${item.number} · ${sections.find(s=>s.id===item.section).title}`);option.value=item.id;option.selected=item.id===q.id;$('jump-question').append(option);});
    $('question-type').textContent=q.kind==='rearrange'?'GHÉP TỪ THÀNH CÂU':['text','multi-text'].includes(q.kind)?'VIẾT ĐÁP ÁN':q.options?.every(o=>['T','F'].includes(o.value))?'ĐÚNG / SAI':'CHỌN ĐÁP ÁN';
    document.querySelector('.reward-tag').textContent=q.autoGrade?'✦ 10 XP lần đầu':'Cần giáo viên duyệt';
    $('question-title').textContent=`Câu ${q.number}`;
    $('prompt').innerHTML=q.promptHtml;
    $('answer-error').textContent='';
    renderAnswer(q,a);
    $('check-answer').disabled=isLocked(a)||conflict;
    $('check-answer').textContent=isLocked(a)?'Đã kiểm tra ✓':'Kiểm tra đáp án ✓';
    const contextHtml=q.contextHtml || (q.context!==undefined?source.contexts[q.context]:'');
    $('passage-panel').hidden=!contextHtml;
    $('question-layout').classList.toggle('with-passage',!!contextHtml);
    if(contextHtml)$('passage-content').innerHTML=contextHtml;
    $('passage-content').hidden=false;
    $('audio-panel').hidden=!q.track;
    if(q.track)loadTrack(q.track);else pauseAudio();
    $('previous-question').disabled=conflict||currentIndex()===0;$('next-question').disabled=conflict;$('jump-question').disabled=conflict;
    $('next-question').textContent=currentIndex()===list.length-1?'Xem tổng kết →':'Câu tiếp →';
    $('review-label').textContent=state.review?'Lượt ôn · Không cộng XP':'';
    renderFeedback(q,a);
  }
  function renderAnswer(q,a) {
    const area=$('answer-area');area.replaceChildren();
    const locked=isLocked(a)||conflict,draft=P.draft(source,state,q.id);
    if(q.kind==='choice') {
      const options=document.createElement('fieldset');options.className='options';options.style.cssText='border:0;padding:0;margin:0;min-width:0';
      const legend=text('legend','Chọn một đáp án','input-hint');options.append(legend);
      q.options.forEach(option=>{
        const label=document.createElement('label');label.className='option';
        const input=document.createElement('input');input.type='radio';input.name=q.id;input.value=option.value;input.checked=draft.value===option.value;input.disabled=locked;
        input.onchange=()=>{writeDraft(q,{...draft,value:input.value});$('answer-error').textContent='';};
        const content=document.createElement('span');content.lang='en';content.innerHTML=option.html;
        label.append(input,content);
        if(locked && q.autoGrade && q.accepted.includes(option.value))label.classList.add('correct-option');
        if(locked && q.autoGrade && draft.value===option.value && !q.accepted.includes(option.value))label.classList.add('wrong-option');
        options.append(label);
      });area.append(options);
    } else if(['text','multi-text'].includes(q.kind)) {
      const count=q.inputCount||1;
      for(let i=0;i<count;i++){
        const wrapper=document.createElement('div');wrapper.className='answer-field';
        const label=text('label',count>1?`Ô trả lời ${i+1}`:q.section==='rewrite'||q.promptHtml.includes('→')?'Nhập phần còn lại sau mũi tên':'Đáp án của em');
        const input=document.createElement('textarea');input.id=count>1?`written-answer-${i}`:'written-answer';label.htmlFor=input.id;
        input.className='answer-input';input.lang='en';input.value=count>1?draft.fields[i]:draft.value;input.disabled=locked;input.maxLength=1500;input.spellcheck=false;
        input.oninput=()=>{const next=JSON.parse(JSON.stringify(P.draft(source,state,q.id)));if(count>1)next.fields[i]=input.value;else next.value=input.value;writeDraft(q,next);$('answer-error').textContent='';};
        wrapper.append(label,input);area.append(wrapper);
      }
      area.append(text('p','Đối chiếu cả câu với đáp án nguồn; không tự chấm bằng từ khóa. Cách diễn đạt khác cần giáo viên xem lại.','input-hint'));
    } else {
      area.append(text('p','Bấm các thẻ theo thứ tự. Bấm thẻ đã ghép để đưa về kho từ.','input-hint'));
      const target=document.createElement('div');target.className='word-target';target.id='word-target';target.setAttribute('aria-label','Câu đang ghép');target.setAttribute('aria-live','polite');
      if(!draft.tokens.length)target.append(text('span','Câu của em sẽ xuất hiện ở đây…','word-placeholder'));
      draft.tokens.forEach((tokenIndex,position)=>{
        const chip=text('button',q.tokens[tokenIndex],'word-chip');chip.disabled=locked;chip.setAttribute('aria-label',`Bỏ thẻ ${q.tokens[tokenIndex]}`);
        chip.onclick=()=>{writeDraft(q,{...draft,tokens:draft.tokens.filter((_,i)=>i!==position)});renderAnswer(q,a);};target.append(chip);
      });
      const bank=document.createElement('div');bank.className='word-bank';bank.id='word-bank';
      q.tokens.forEach((token,i)=>{
        const chip=text('button',token,'word-chip');chip.disabled=locked || draft.tokens.includes(i);chip.dataset.tokenIndex=i;
        chip.onclick=()=>{writeDraft(q,{...draft,tokens:[...draft.tokens,i]});$('answer-error').textContent='';renderAnswer(q,a);};bank.append(chip);
      });
      const tools=document.createElement('div');tools.className='builder-tools';
      const undo=text('button','↶ Hoàn tác','secondary');undo.id='undo-word';undo.disabled=locked || !draft.tokens.length;undo.onclick=()=>{writeDraft(q,{...draft,tokens:draft.tokens.slice(0,-1)});renderAnswer(q,a);};
      const reset=text('button','↻ Làm lại','secondary');reset.id='reset-words';reset.disabled=locked || !draft.tokens.length;reset.onclick=()=>{writeDraft(q,{...draft,tokens:[]});renderAnswer(q,a);};
      tools.append(undo,reset);area.append(target,bank,tools);
    }
  }
  function addExplanation(title,content,html=false) {
    const item=document.createElement('div');item.className='explanation-item';item.append(text('h3',title));
    const body=document.createElement('div');if(html)body.innerHTML=content;else body.textContent=content;
    item.append(body);$('explanation-content').append(item);
  }
  function renderFeedback(q,a) {
    $('feedback').hidden=!isLocked(a);
    $('explanation-content').replaceChildren();$('transcript-panel').hidden=true;$('transcript-content').replaceChildren();
    if(!isLocked(a))return;
    const correct=correctNow(a),pending=(state.review?a.review.result:a.first?.result)==='pending',draft=P.draft(source,state,q.id);
    $('feedback').classList.toggle('is-wrong',!correct&&!pending);$('feedback').classList.toggle('pending-feedback',!!pending);
    $('feedback-title').textContent=pending?'Chờ giáo viên đối chiếu':correct?(state.review?'✓ Chính xác! Không cộng thêm XP.':'✓ Khớp đáp án nguồn! +10 XP'):'↻ Chưa khớp đáp án nguồn';
    const userAnswer=q.kind==='rearrange'?draft.tokens.map(i=>q.tokens[i]).join(' '):q.kind==='multi-text'?draft.fields.join(' / '):draft.value;
    $('your-answer').textContent=`Em đã trả lời: ${userAnswer}`;
    addExplanation('Đáp án / câu mẫu · nguyên văn nguồn',q.answerLabel,true);
    addExplanation('Giải thích & kiến thức · nguyên văn nguồn',q.explainHtml || 'Nguồn chưa cung cấp lời giải riêng cho câu này.',true);
    if(q.knowledge)addExplanation('Ghi chú nguồn',q.knowledge,true);
    if(['text','multi-text'].includes(q.kind))$('explanation-content').append(text('p','Chấm máy chỉ nhận câu mẫu/biến thể được nêu rõ trong nguồn. Cách diễn đạt khác không đồng nghĩa với sai; hãy nhờ giáo viên đối chiếu. Không dùng từ khóa đơn lẻ để kết luận đúng.','teacher-note'));
    for(const flag of q.teacherFlags)$('explanation-content').append(text('p',`Giáo viên cần duyệt: ${flag}`,'teacher-note'));
    const added=support.items?.[q.id];
    if(added){
      $('explanation-content').append(text('p','Nội dung hỗ trợ tạo thêm bằng AI · Chưa được giáo viên xác nhận.','support-notice'));
      if(added.translation)addExplanation('Dịch nghĩa · hỗ trợ AI chưa duyệt',added.translation);
      if(added.tip)addExplanation('Mẹo học · hỗ trợ AI chưa duyệt',added.tip);
      if(added.readingWords)addExplanation('Từ khóa bài đọc · hỗ trợ chưa duyệt',added.readingWords);
    }
    const transcript=q.transcriptHtml || (q.track && source.tracks.find(t=>t.id===q.track)?.transcriptHtml);
    if(transcript){$('transcript-panel').hidden=false;$('transcript-content').innerHTML=transcript;}
  }
  function checkAnswer(event) {
    if(conflict)return;const q=currentQuestion(),checkedBefore=totalChecked();
    try {if(!P.check(source,state,q.id))return;}catch(error){$('answer-error').textContent=error.message;return;}
    renderQuestion();$('xp-total').textContent=`✦ ${totalCorrect()*10} XP`;
    const a=state.answers[q.id];$('feedback').classList.remove('celebrate');
    void sound?.playFeedback(state.review?a.review.result:a.first?.result,{
      event,completed:checkedBefore<questions.length&&totalChecked()===questions.length,
      listeningActive:!audio.paused
    });
    if(correctNow(a)){void $('feedback').offsetWidth;$('feedback').classList.add('celebrate');}
    $('feedback-title').focus({preventScroll:true});$('feedback').scrollIntoView({block:'nearest',behavior:'instant'});
  }
  function showResults() {
    showPage('results');
    const {checked,correct,pending,wrong}=P.summary(source,state);
    $('result-total').textContent=questions.length;
    $('results-title').textContent=`${state.student.name}, em đang làm rất tốt!`;
    $('result-description').textContent=checked===questions.length?'Em đã hoàn thành hành trình. Hãy ôn lại các câu cần luyện để hiểu bài hơn nhé.':`Em đã khám phá ${checked}/${questions.length} câu. Em có thể tiếp tục làm đề.`;
    $('result-pending').textContent=pending;$('result-xp').textContent=correct*10;$('result-correct').textContent=correct;$('result-wrong').textContent=wrong;$('result-unanswered').textContent=questions.length-checked;
    $('result-breakdown').replaceChildren();
    sections.forEach(s=>{
      const group=bySection(s.id),done=group.filter(q=>!!state.answers[q.id].first).length,good=group.filter(q=>firstCorrect(state.answers[q.id])).length;
      const button=document.createElement('div');button.append(text('strong',`${s.icon} ${s.title}`),text('span',`${done}/${group.length} đã luyện · ${good} đúng lần đầu · ${good*10} XP`));$('result-breakdown').append(button);
    });
    const improved=questions.filter(q=>!!state.answers[q.id].first && !firstCorrect(state.answers[q.id]) && state.answers[q.id].review.result==='correct').length;
    $('review-summary').textContent=`${improved} câu đã làm đúng khi ôn lại. Kết quả lần đầu và XP được giữ nguyên.`;
    $('review-wrong').disabled=!(wrong+pending);
    $('review-list').replaceChildren();
    P.summary(source,state).reviewIds.forEach(id=>{const q=questions.find(q=>q.id===id),button=text('button',`Câu ${q.number} · ${sections.find(s=>s.id===q.section).title}`,'secondary');button.onclick=()=>{state.review=false;P.go(source,state,id);showPage('play');renderQuestion();};$('review-list').append(button);});
  }
  function beginReview(){if(conflict||!P.beginReview(source,state))return;showPage('play');renderQuestion();}
  function leaveReview(){state.review=false;}
  function routeSession(){showExam();}
  function persist(){
    if(!state||!store||conflict)return;
    const status=store.save(state);
    $('save-message').textContent=status==='saved'?'Đã lưu tiến độ trên thiết bị này.':status==='blocked'?'Thiết bị chưa lưu được tiến độ. Hãy giữ trang mở để tiếp tục.':'Tiến độ đã thay đổi ở tab khác. Tải lại trang để dùng bản mới nhất.';
    $('reload-progress').hidden=status!=='conflict';
    if(status==='conflict')freezeSession();
  }
  function freezeSession(){sound?.stop();conflict=true;pauseAudio();$('reload-progress').hidden=false;document.querySelectorAll('#play button,#play input,#play textarea,#play select').forEach(el=>el.disabled=true);}
  function freshSession(){sound?.stop();state=P.create(source,pendingStudent);$('resume-panel').hidden=true;$('start-form').hidden=false;conflict=false;routeSession();}
  function welcome(){
    sound?.stop();persist();pauseAudio();state=null;store=null;pendingStudent=null;conflict=false;
    for(const id of ['welcome','play','results'])$(id).hidden=id!=='welcome';
    $('session-tools').hidden=true;$('resume-panel').hidden=true;$('start-form').hidden=false;
    $('home-button').hidden=true;$('results-button').hidden=true;$('student-label').textContent='';$('xp-total').textContent='✦ 0 XP';
    $('answer-area').replaceChildren();$('explanation-content').replaceChildren();$('transcript-content').replaceChildren();$('save-message').textContent='';$('reload-progress').hidden=true;
    HTDualStore.forget();$('student-name').value='';$('student-code').value='';$('name-error').textContent='';$('student-name').focus();
  }
  $('start-form').onsubmit=event=>{
    event.preventDefault();try{pendingStudent=P.identity($('student-name').value,$('student-code').value);}catch(error){$('name-error').textContent=error.message;$('student-name').focus();return;}
    HTDualStore.remember(pendingStudent);
    store=HTDualStore.open(source,pendingStudent);
    if(store.status==='empty'||store.status==='blocked'){freshSession();return;}
    $('start-form').hidden=true;$('resume-panel').hidden=false;
    $('resume-button').disabled=store.status!=='found';
    $('resume-description').textContent=store.status==='found'?`${pendingStudent.name}: đã kiểm tra ${P.summary(source,store.state).checked}/${questions.length} câu · ${P.summary(source,store.state).xp} XP. Tiếp tục làm toàn bộ đề tại vị trí đã lưu.`:store.status==='incompatible'?'Đề đã được cập nhật. Bản lưu cũ vẫn được giữ; hãy xác nhận nếu em muốn bắt đầu lại.':'Bản lưu chưa đọc được. Hãy xác nhận nếu em muốn bắt đầu lại; các bài và học sinh khác được giữ nguyên.';
  };
  $('resume-button').onclick=()=>{if(!store.state)return;state=store.state;conflict=false;$('resume-panel').hidden=true;routeSession();};
  const restart=()=>{$('restart-name').textContent=state?.student.name||pendingStudent?.name||'';$('restart-dialog').showModal();};
  $('restart-button').onclick=$('restart-saved').onclick=restart;
  $('confirm-restart').onclick=()=>{
    if(store.reset()==='conflict'){$('restart-dialog').close();$('save-message').textContent='Tiến độ đã thay đổi ở tab khác. Tải lại trang để dùng bản mới nhất.';if(state)freezeSession();else{$('resume-button').disabled=true;$('reload-progress').hidden=false;}return;}
    if(state){pendingStudent=state.student;}freshSession();$('restart-dialog').close();
  };
  $('cancel-restart').onclick=()=>$('restart-dialog').close();
  $('change-student').onclick=$('resume-other-student').onclick=welcome;
  $('reload-progress').onclick=()=>location.reload();
  $('jump-question').onchange=()=>{P.go(source,state,$('jump-question').value);renderQuestion();};
  $('home-button').onclick=()=>{if(!state)return;leaveReview();showExam();};
  $('results-button').onclick=showResults;
  $('continue-playing').onclick=()=>{leaveReview();showExam();};
  $('review-wrong').onclick=beginReview;$('check-answer').onclick=checkAnswer;
  $('previous-question').onclick=()=>move(currentIndex()-1);$('next-question').onclick=()=>{if(currentIndex()<activeQuestions().length-1)move(currentIndex()+1);else showResults();};
  window.addEventListener('storage',event=>{if(state&&store&&event.key===store.key&&event.newValue!==store.lastRaw){$('save-message').textContent='Tiến độ đã thay đổi ở tab khác. Tải lại trang để dùng bản mới nhất.';freezeSession();}});
  window.addEventListener('pagehide',()=>{sound?.stop();persist();});

  function timeLabel(value){if(!Number.isFinite(value))return '0:00';return `${Math.floor(value/60)}:${String(Math.floor(value%60)).padStart(2,'0')}`;}
  function updateAudio(){
    $('audio-time').textContent=`${timeLabel(audio.currentTime)} / ${timeLabel(audio.duration)}`;
    $('audio-seek').value=audio.duration?audio.currentTime/audio.duration*100:0;
    $('audio-toggle').textContent=audio.paused?'▶ Phát':'Ⅱ Tạm dừng';
  }
  function loadTrack(id) {
    if(currentTrack===id)return;
    const track=source.tracks.find(t=>t.id===id);if(!track)throw Error('Audio mapping missing');
    pauseAudio();currentTrack=id;audio.src=track.src;audio.playbackRate=Number($('audio-speed').value);audio.load();
    $('audio-title').textContent=`🎧 Audio gốc · ${track.title || sections.find(s=>s.id===currentQuestion().section)?.title || track.id}`;
    $('audio-message').textContent=track.wholeFile?'Tệp nghe gốc dùng chung cho hai phần. Dùng thanh tua để tìm đoạn cần nghe.':'Transcript chỉ mở sau khi em kiểm tra câu đang làm.';updateAudio();
  }
  $('audio-toggle').onclick=async()=>{
    if(audio.paused){try{await audio.play();$('audio-message').textContent='Đang phát bài nghe.';}catch{$('audio-message').textContent='Chưa phát được audio. Em hãy thử lại và kiểm tra kết nối.';}}
    else{pauseAudio();$('audio-message').textContent='Đã tạm dừng. Có thể nghe lại bất cứ lúc nào.';}
  };
  function seek(delta){if(Number.isFinite(audio.duration))audio.currentTime=Math.max(0,Math.min(audio.duration,audio.currentTime+delta));updateAudio();}
  $('audio-back').onclick=()=>seek(-5);$('audio-forward').onclick=()=>seek(5);
  $('audio-speed').onchange=()=>{audio.playbackRate=Number($('audio-speed').value);};
  $('audio-seek').oninput=()=>{if(Number.isFinite(audio.duration))audio.currentTime=audio.duration*Number($('audio-seek').value)/100;};
  for(const event of ['timeupdate','loadedmetadata','play','pause','ended'])audio.addEventListener(event,updateAudio);
  audio.addEventListener('error',()=>{$('audio-message').textContent='Không tải được MP3. Em hãy kiểm tra kết nối hoặc báo giáo viên.';});
  $('source-info').textContent=[source.exam.school,source.exam.title].join(' · ')+(source.tracks.length?'':' · Đề gốc chưa có tệp MP3. Em hãy nhờ giáo viên cung cấp bài nghe.');
  const remembered=HTDualStore.profile();if(remembered){$('student-name').value=remembered.name;$('student-code').value=remembered.code;}
  document.title=`${source.exam.school} · English Quest ${source.exam.grade||8} | HT ENGLISH`;
  document.addEventListener('visibilitychange',()=>{if(document.hidden){sound?.stop();pauseAudio();persist();}});
})();
