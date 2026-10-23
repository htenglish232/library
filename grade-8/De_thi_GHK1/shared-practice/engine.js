/* Standalone, in-memory learning game. No account, backend, analytics or storage. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const source = window.HT_PRACTICE_DATA;
  try {HTPracticeModel.validate(source);} catch(error) {
    $('name-error').textContent='Dữ liệu đề chưa thể mở. Hãy báo giáo viên: '+error.message;
    $('start-form').querySelector('button').disabled=true;
    return;
  }
  const support = window.HT_PRACTICE_SUPPORT || {items:{}};
  const questions = source.questions;
  const sections = source.sections.map((s,i)=>({...s,short:s.title,color:['#e5f3fc','#e8f5ee','#f1edfb','#fff4d9'][i%4]}));
  const state = {name:'',section:sections[0].id,index:0,review:false,reviewIds:[],answers:{}};
  questions.forEach(q => state.answers[q.id] = {draft:'',drafts:Array(q.inputCount||1).fill(''),tokens:[],checked:false,firstCorrect:false,reviewed:false,reviewCorrect:false});
  const audio = $('audio-player');
  let currentTrack = 0;
  const bySection = id => questions.filter(q => q.section === id);
  const activeQuestions = () => state.review ? questions.filter(q => state.reviewIds.includes(q.id)) : bySection(state.section);
  const currentQuestion = () => activeQuestions()[state.index];
  const totalChecked = () => questions.filter(q => state.answers[q.id].checked).length;
  const totalCorrect = () => questions.filter(q => state.answers[q.id].firstCorrect).length;
  const isLocked = a => state.review ? a.reviewed : a.checked;
  const correctNow = a => state.review ? a.reviewCorrect : a.firstCorrect;
  const text = (tag,value,className) => {const el=document.createElement(tag);el.textContent=value;if(className)el.className=className;return el;};
  function accepted(q,value,a){return HTPracticeModel.evaluate(q,value,a.drafts);}
  function pauseAudio() {audio.pause();}
  function showPage(id) {
    for(const page of ['welcome','challenges','play','results']) $(page).hidden=page!==id;
    if(id!=='play') pauseAudio();
    $('home-button').hidden=!state.name;
    $('results-button').hidden=!state.name;
    $('student-label').textContent=state.name;
    $('xp-total').textContent=`✦ ${totalCorrect()*10} XP`;
    $('main').focus({preventScroll:true});
    window.scrollTo({top:0,behavior:'instant'});
  }
  function showMenu() {
    showPage('challenges');
    $('challenge-greeting').textContent=`Chào ${state.name}! Hôm nay em muốn khám phá điều gì?`;
    $('journey-count').textContent=`${totalChecked()}/${questions.length} câu đã luyện`;
    $('journey-progress').max=questions.length;
    $('journey-progress').value=totalChecked();
    $('challenge-grid').replaceChildren();
    sections.forEach((section,i) => {
      const group=bySection(section.id),done=group.filter(q=>state.answers[q.id].checked).length;
      const card=document.createElement('article');card.className='challenge-card';card.style.setProperty('--tint',section.color);
      card.append(text('div',section.icon,'challenge-icon'),text('span',`0${i+1} / CHALLENGE`,'number'),text('h2',section.title),text('p',section.description));
      const progress=document.createElement('progress');progress.max=group.length;progress.value=done;progress.setAttribute('aria-label',`Tiến độ ${section.short}`);card.append(progress);
      const bottom=document.createElement('div');bottom.className='card-bottom';bottom.append(text('span',`${done}/${group.length} câu · ${group.filter(q=>state.answers[q.id].firstCorrect).length*10} XP`));
      const button=text('button',done?'Tiếp tục →':'Khám phá →');button.dataset.section=section.id;button.setAttribute('aria-label',`Mở ${section.title}`);button.onclick=()=>openSection(section.id);bottom.append(button);card.append(bottom);$('challenge-grid').append(card);
    });
  }
  function openSection(id) {
    leaveReview();
    state.review=false;state.section=id;
    const group=bySection(id);state.index=Math.max(0,group.findIndex(q=>!state.answers[q.id].checked));
    showPage('play');renderQuestion();
  }
  function renderTabs() {
    $('section-tabs').replaceChildren();
    sections.forEach(section=>{
      const button=text('button',`${section.icon} ${section.short}`);button.dataset.section=section.id;
      button.setAttribute('aria-current',String(!state.review && state.section===section.id));button.onclick=()=>openSection(section.id);$('section-tabs').append(button);
    });
  }
  function renderQuestion() {
    const list=activeQuestions(),q=list[state.index];
    if(!q) {showResults();return;}
    const section=sections.find(s=>s.id===q.section),a=state.answers[q.id];
    $('question-card').dataset.questionId=q.id;
    $('section-title').textContent=state.review?'Ôn lại câu cần luyện':section.title;
    $('section-description').textContent=state.review?'Thử lại sau khi đọc lời giải. Lượt ôn không thay đổi XP và kết quả lần đầu.':section.description;
    $('section-kicker').textContent=state.review?'PRACTICE MAKES PROGRESS':`CHALLENGE 0${sections.indexOf(section)+1} · GRADE 8`;
    renderTabs();
    const done=list.filter(item=>state.review?state.answers[item.id].reviewed:state.answers[item.id].checked).length;
    $('question-position').textContent=`Câu ${state.index+1} / ${list.length}`;
    $('section-progress').max=list.length;$('section-progress').value=done;
    $('section-score').textContent=`${done} đã luyện`;
    $('question-dots').replaceChildren();
    list.forEach((item,i)=>{
      const answer=state.answers[item.id];const checked=state.review?answer.reviewed:answer.checked;
      const button=text('button',String(item.number));
      button.dataset.questionId=item.id;button.setAttribute('aria-label',`Đến câu ${item.number}${checked?(correctNow(answer)?' – đúng':' – cần ôn'):''}`);
      button.setAttribute('aria-current',String(i===state.index));
      if(checked)button.className=correctNow(answer)?'correct':'wrong';
      button.onclick=()=>{state.index=i;renderQuestion();$('question-title').focus({preventScroll:true});};$('question-dots').append(button);
    });
    $('question-type').textContent=q.kind==='rearrange'?'GHÉP TỪ THÀNH CÂU':['text','multi-text'].includes(q.kind)?'VIẾT ĐÁP ÁN':q.options?.every(o=>['T','F'].includes(o.value))?'ĐÚNG / SAI':'CHỌN ĐÁP ÁN';
    document.querySelector('.reward-tag').textContent=q.autoGrade?'✦ 10 XP lần đầu':'Chờ giáo viên đối chiếu';
    $('question-title').textContent=`Câu ${q.number} · Mã nguồn ${q.id}`;
    $('prompt').innerHTML=q.promptHtml;
    $('answer-error').textContent='';
    renderAnswer(q,a);
    $('check-answer').disabled=isLocked(a);
    $('check-answer').textContent=isLocked(a)?'Đã kiểm tra ✓':'Kiểm tra đáp án ✓';
    const contextHtml=q.contextHtml || (q.context!==undefined?source.contexts[q.context]:'');
    $('passage-panel').hidden=!contextHtml;
    $('question-layout').classList.toggle('with-passage',!!contextHtml);
    if(contextHtml)$('passage-content').innerHTML=contextHtml;
    $('audio-panel').hidden=!q.track;
    if(q.track)loadTrack(q.track);else pauseAudio();
    $('previous-question').disabled=state.index===0;
    $('next-question').textContent=state.index===list.length-1?'Xem tổng kết →':'Câu tiếp →';
    $('review-label').textContent=state.review?'Lượt ôn · Không cộng XP':'';
    renderFeedback(q,a);
  }
  function renderAnswer(q,a) {
    const area=$('answer-area');area.replaceChildren();
    const locked=isLocked(a);
    if(q.kind==='choice') {
      const options=document.createElement('fieldset');options.className='options';options.style.cssText='border:0;padding:0;margin:0;min-width:0';
      const legend=text('legend','Chọn một đáp án','input-hint');options.append(legend);
      q.options.forEach(option=>{
        const label=document.createElement('label');label.className='option';
        const input=document.createElement('input');input.type='radio';input.name=q.id;input.value=option.value;input.checked=a.draft===option.value;input.disabled=locked;
        input.onchange=()=>{a.draft=input.value;$('answer-error').textContent='';};
        const content=document.createElement('span');content.lang='en';content.innerHTML=option.html;
        label.append(input,content);
        if(locked && option.value===q.accepted[0])label.classList.add('correct-option');
        if(locked && a.draft===option.value && option.value!==q.accepted[0])label.classList.add('wrong-option');
        options.append(label);
      });area.append(options);
    } else if(['text','multi-text'].includes(q.kind)) {
      const count=q.inputCount||1;
      for(let i=0;i<count;i++){
        const wrapper=document.createElement('div');wrapper.className='answer-field';
        const label=text('label',count>1?`Ô trả lời ${i+1}`:q.section==='rewrite'?'Nhập phần còn lại sau mũi tên':'Đáp án của em');
        const input=document.createElement('textarea');input.id=count>1?`written-answer-${i}`:'written-answer';label.htmlFor=input.id;
        input.className='answer-input';input.lang='en';input.value=count>1?a.drafts[i]:a.draft;input.disabled=locked;input.maxLength=1500;input.spellcheck=false;
        input.oninput=()=>{if(count>1)a.drafts[i]=input.value;else a.draft=input.value;$('answer-error').textContent='';};
        wrapper.append(label,input);area.append(wrapper);
      }
      area.append(text('p','Đối chiếu cả câu với đáp án nguồn; không tự chấm bằng từ khóa. Cách diễn đạt khác cần giáo viên xem lại.','input-hint'));
    } else {
      area.append(text('p','Bấm các thẻ theo thứ tự. Bấm thẻ đã ghép để đưa về kho từ.','input-hint'));
      const target=document.createElement('div');target.className='word-target';target.id='word-target';target.setAttribute('aria-label','Câu đang ghép');target.setAttribute('aria-live','polite');
      if(!a.tokens.length)target.append(text('span','Câu của em sẽ xuất hiện ở đây…','word-placeholder'));
      a.tokens.forEach((tokenIndex,position)=>{
        const chip=text('button',q.tokens[tokenIndex],'word-chip');chip.disabled=locked;chip.setAttribute('aria-label',`Bỏ thẻ ${q.tokens[tokenIndex]}`);
        chip.onclick=()=>{a.tokens.splice(position,1);renderAnswer(q,a);};target.append(chip);
      });
      const bank=document.createElement('div');bank.className='word-bank';bank.id='word-bank';
      q.tokens.forEach((token,i)=>{
        const chip=text('button',token,'word-chip');chip.disabled=locked || a.tokens.includes(i);chip.dataset.tokenIndex=i;
        chip.onclick=()=>{a.tokens.push(i);$('answer-error').textContent='';renderAnswer(q,a);};bank.append(chip);
      });
      const tools=document.createElement('div');tools.className='builder-tools';
      const undo=text('button','↶ Hoàn tác','secondary');undo.id='undo-word';undo.disabled=locked || !a.tokens.length;undo.onclick=()=>{a.tokens.pop();renderAnswer(q,a);};
      const reset=text('button','↻ Làm lại','secondary');reset.id='reset-words';reset.disabled=locked || !a.tokens.length;reset.onclick=()=>{a.tokens=[];renderAnswer(q,a);};
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
    const correct=correctNow(a),pending=state.review?a.reviewPending:a.pending;
    $('feedback').classList.toggle('is-wrong',!correct&&!pending);$('feedback').classList.toggle('pending-feedback',!!pending);
    $('feedback-title').textContent=pending?'Chờ giáo viên đối chiếu':correct?(state.review?'✓ Chính xác! Không cộng thêm XP.':'✓ Khớp đáp án nguồn! +10 XP'):'↻ Chưa khớp đáp án nguồn';
    const userAnswer=q.kind==='rearrange'?a.tokens.map(i=>q.tokens[i]).join(' '):q.kind==='multi-text'?a.drafts.join(' / '):a.draft;
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
    }
    if(q.track){const track=source.tracks.find(t=>t.id===q.track);if(track?.transcriptHtml){$('transcript-panel').hidden=false;$('transcript-content').innerHTML=track.transcriptHtml;}}
  }
  function checkAnswer() {
    const q=currentQuestion(),a=state.answers[q.id];if(isLocked(a))return;
    const value=q.kind==='rearrange'?a.tokens.map(i=>q.tokens[i]).join(' '):q.kind==='multi-text'?a.drafts.map(v=>v.trim()).join(' / '):a.draft.trim();
    if(!value || (q.kind==='multi-text' && a.drafts.some(v=>!v.trim())) || (q.kind==='rearrange' && a.tokens.length!==q.tokens.length)) {
      $('answer-error').textContent=q.kind==='rearrange'?'Em hãy ghép đủ tất cả các thẻ trước khi kiểm tra.':'Em hãy chọn hoặc nhập đáp án trước khi kiểm tra.';return;
    }
    const correct=accepted(q,value,a);
    if(state.review){a.reviewed=true;a.reviewCorrect=correct===true;a.reviewPending=correct===null;}else{a.checked=true;a.firstCorrect=correct===true;a.pending=correct===null;}
    renderQuestion();$('xp-total').textContent=`✦ ${totalCorrect()*10} XP`;
    $('feedback').classList.remove('celebrate');
    if(correct){void $('feedback').offsetWidth;$('feedback').classList.add('celebrate');}
    $('feedback-title').focus({preventScroll:true});
    $('feedback').scrollIntoView({block:'nearest',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
  }
  function showResults() {
    showPage('results');
    const checked=totalChecked(),correct=totalCorrect(),pending=questions.filter(q=>state.answers[q.id].checked&&state.answers[q.id].pending).length,wrong=checked-correct-pending;
    $('results-title').textContent=`${state.name}, em đang làm rất tốt!`;
    $('result-description').textContent=checked===questions.length?'Em đã hoàn thành hành trình. Hãy ôn lại các câu cần luyện để hiểu bài hơn nhé.':`Em đã khám phá ${checked}/${questions.length} câu. Có thể tiếp tục bất cứ thử thách nào.`;
    $('result-pending').textContent=pending;$('result-xp').textContent=correct*10;$('result-correct').textContent=correct;$('result-wrong').textContent=wrong;$('result-unanswered').textContent=questions.length-checked;
    $('result-breakdown').replaceChildren();
    sections.forEach(s=>{
      const group=bySection(s.id),done=group.filter(q=>state.answers[q.id].checked).length,good=group.filter(q=>state.answers[q.id].firstCorrect).length;
      const button=document.createElement('button');button.append(text('strong',`${s.icon} ${s.title}`),text('span',`${done}/${group.length} đã luyện · ${good} đúng lần đầu · ${good*10} XP`));button.onclick=()=>openSection(s.id);$('result-breakdown').append(button);
    });
    const improved=questions.filter(q=>state.answers[q.id].checked && !state.answers[q.id].firstCorrect && state.answers[q.id].reviewCorrect).length;
    $('review-summary').textContent=`${improved} câu đã làm đúng khi ôn lại. Kết quả lần đầu và XP được giữ nguyên.`;
    $('review-wrong').disabled=!(wrong+pending);
  }
  function beginReview() {
    state.reviewIds=questions.filter(q=>state.answers[q.id].checked&&!state.answers[q.id].firstCorrect).map(q=>q.id);
    if(!state.reviewIds.length)return;
    state.review=true;state.index=0;
    state.reviewIds.forEach(id=>{const a=state.answers[id];a.reviewed=false;a.reviewCorrect=false;});
    // Preserve the first-attempt draft separately so leaving review cannot overwrite it.
    state.reviewIds.forEach(id=>{const a=state.answers[id];if(!a.firstDraft)a.firstDraft={draft:a.draft,drafts:[...a.drafts],tokens:[...a.tokens]};a.draft='';a.drafts=a.drafts.map(()=>'');a.tokens=[];});
    showPage('play');renderQuestion();
  }
  function leaveReview() {
    if(!state.review)return;
    state.reviewIds.forEach(id=>{const a=state.answers[id];if(a.firstDraft){a.draft=a.firstDraft.draft;a.drafts=[...a.firstDraft.drafts];a.tokens=[...a.firstDraft.tokens];}});
    state.review=false;
  }
  $('start-form').onsubmit=event=>{
    event.preventDefault();const value=$('student-name').value.replace(/\s+/gu,' ').trim();
    if(!value){$('name-error').textContent='Em hãy nhập tên trước khi bắt đầu nhé.';$('student-name').setAttribute('aria-invalid','true');$('student-name').focus();return;}
    $('student-name').removeAttribute('aria-invalid');state.name=value;showMenu();
  };
  $('home-button').onclick=$('back-menu').onclick=()=>{leaveReview();showMenu();};
  $('results-button').onclick=$('menu-summary').onclick=showResults;
  $('continue-playing').onclick=()=>{leaveReview();showMenu();};
  $('review-wrong').onclick=beginReview;
  $('check-answer').onclick=checkAnswer;
  $('previous-question').onclick=()=>{if(state.index>0){state.index--;renderQuestion();$('question-title').focus({preventScroll:true});}};
  $('next-question').onclick=()=>{if(state.index<activeQuestions().length-1){state.index++;renderQuestion();$('question-title').focus({preventScroll:true});}else showResults();};

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
  $('source-info').textContent=[source.exam.school,...source.exam.sourceHeadings].join(' · ');
  document.title=`${source.exam.school} · English Quest 8 | HT ENGLISH`;
  document.addEventListener('visibilitychange',()=>{if(document.hidden)pauseAudio();});
})();
