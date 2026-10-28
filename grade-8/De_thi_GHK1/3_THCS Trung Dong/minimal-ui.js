/* Presentation-only pilot for this exam. The shared engine owns grading/storage/audio. */
(() => {
  'use strict';
  if(document.documentElement.dataset.minimalUi!=='trung-dong-1' || window.HT_PRACTICE_DATA?.exam.id!=='grade8-ghk1-source-3')return;
  const $=id=>document.getElementById(id),data=window.HT_PRACTICE_DATA;
  const nav=document.querySelector('.question-navigation');
  const card=$('question-card'),feedback=$('feedback'),passage=$('passage-content');
  const heading=document.createElement('div');heading.className='minimal-heading';
  const title=document.createElement('h1');title.textContent='Trung Đông · Đề 1';
  const count=document.createElement('span');count.id='minimal-question-count';
  heading.append(title,count);$('play').prepend(heading);

  // Move existing controls rather than creating a second set of navigation/actions.
  const tools=document.createElement('details');tools.id='minimal-tools';tools.hidden=true;
  const toolsLabel=document.createElement('summary');toolsLabel.textContent='Tùy chọn';tools.append(toolsLabel);
  const actions=document.createElement('div');actions.className='minimal-tool-actions';
  for(const id of ['results-button','sound-toggle','restart-button','change-student'])actions.append($(id));
  tools.append(actions);document.querySelector('.header-actions').append(tools);
  tools.addEventListener('click',event=>{if(event.target.closest('button'))tools.open=false;});
  const list=document.createElement('details');list.id='minimal-question-list';
  const listLabel=document.createElement('summary');listLabel.textContent='Danh sách câu';list.append(listLabel);
  list.append(document.querySelector('.jump-control'),$('question-dots'));
  document.querySelector('.play-progress').after(list);
  const navCount=document.createElement('span');navCount.id='minimal-nav-count';navCount.setAttribute('aria-live','polite');
  nav.insertBefore(navCount,$('next-question'));
  nav.setAttribute('aria-label','Chuyển câu hỏi');
  const missingAudio=document.createElement('p');missingAudio.id='minimal-audio-notice';missingAudio.textContent='Đề gốc chưa có tệp nghe. Em hãy nhờ giáo viên cung cấp.';
  $('audio-panel').after(missingAudio);
  document.querySelector('.welcome h1').textContent='Trung Đông · Đề 1';

  // The verified source groups both readings into context 2. Show only the
  // passage box belonging to this question's original section, without editing data.
  const readingDocument=document.createElement('div');readingDocument.innerHTML=data.contexts[2];
  const readings=new Map();
  for(const [section,index] of [['section-5',1],['section-6',2]]){
    const box=readingDocument.children[index]?.querySelector(':scope > div');
    if(box?.querySelector('p'))readings.set(section,box.innerHTML);
  }
  let renderedId=null,readingKey=null,savedReadingScroll=0;
  const question=()=>data.questions.find(q=>q.id===card.dataset.questionId);
  function sync(){
    tools.hidden=$('session-tools').hidden;
    const q=question();if(!q)return;
    const position=$('question-position').textContent.replace(/\s*\/\s*/,'/');
    count.textContent=navCount.textContent=position;
    $('previous-question').textContent='‹ Câu trước';
    $('next-question').textContent=$('next-question').textContent.toLocaleLowerCase('vi').includes('tổng kết')?'Tổng kết ›':'Câu tiếp ›';
    const html=readings.get(q.section);
    $('passage-panel').hidden=!html;
    $('question-layout').classList.toggle('with-passage',!!html);
    if(html){
      if(passage.innerHTML!==html)passage.innerHTML=html;
      if(readingKey===q.section)passage.scrollTop=savedReadingScroll;
      else passage.scrollTop=0;
    }
    readingKey=html?q.section:null;
    missingAudio.hidden=!!q.track||!['section-1','section-2'].includes(q.section);
    const explanations=$('explanation-content').querySelectorAll('.explanation-item');
    if(explanations[0])explanations[0].querySelector('h3').textContent='Đáp án';
    if(explanations[1]){
      explanations[1].querySelector('h3').textContent='Giải thích';
      if(!q.explainHtml)explanations[1].lastElementChild.textContent='Chưa có lời giải chi tiết.';
    }
    if(renderedId!==q.id){list.open=false;renderedId=q.id;}
    updateViewport();
  }
  passage.addEventListener('scroll',()=>{savedReadingScroll=passage.scrollTop;},{passive:true});
  function navigate(event){
    const check=event.target.closest('#check-answer');
    if(check && !check.disabled){
      requestAnimationFrame(()=>{sync();if(!feedback.hidden)feedback.scrollIntoView({block:'start',behavior:'instant'});});
      return;
    }
    const control=event.target.closest('#previous-question,#next-question,#question-dots button,#jump-question');
    if(!control || control.disabled || event.type==='click'&&control.id==='jump-question')return;
    savedReadingScroll=passage.scrollTop;
    if(document.activeElement?.matches('textarea,input'))document.activeElement.blur();
    requestAnimationFrame(()=>{
      sync();list.open=false;
      if($('play').hidden)return;
      const anchor=readingKey?$('question-layout'):card;
      $('question-title').focus({preventScroll:true});
      anchor.scrollIntoView({block:'start',behavior:'instant'});
    });
  }
  document.addEventListener('click',navigate,true);
  $('jump-question').addEventListener('change',navigate,true);
  const observer=new MutationObserver(sync);
  observer.observe(card,{attributes:true,attributeFilter:['data-question-id']});
  observer.observe(feedback,{attributes:true,attributeFilter:['hidden']});
  observer.observe($('session-tools'),{attributes:true,attributeFilter:['hidden']});
  observer.observe($('play'),{attributes:true,attributeFilter:['hidden']});

  // iOS can shrink/pan only the visual viewport when its keyboard opens.
  // Keep the single fixed bar above it and reserve matching scroll space.
  function updateViewport(){
    const viewport=window.visualViewport;
    const inset=viewport?Math.max(0,window.innerHeight-viewport.height-viewport.offsetTop):0;
    document.documentElement.style.setProperty('--minimal-keyboard-inset',`${inset}px`);
    const height=nav.getBoundingClientRect().height;
    if(height)document.documentElement.style.setProperty('--minimal-nav-height',`${height}px`);
  }
  const resizeObserver=new ResizeObserver(updateViewport);resizeObserver.observe(nav);
  function keepAnswerVisible(){
    const field=document.activeElement;
    if(!field?.matches('#answer-area textarea,#answer-area input'))return;
    const top=(window.visualViewport?.offsetTop||0)+12;
    const bottom=nav.getBoundingClientRect().top-12;
    const rect=field.getBoundingClientRect();
    if(rect.bottom>bottom || rect.top<top){
      window.scrollBy({top:rect.top-(top+Math.max(0,(bottom-top-rect.height)/2)),behavior:'instant'});
    }
  }
  function viewportChanged(){updateViewport();requestAnimationFrame(keepAnswerVisible);}
  window.visualViewport?.addEventListener('resize',viewportChanged);
  window.visualViewport?.addEventListener('scroll',updateViewport,{passive:true});
  window.addEventListener('resize',viewportChanged,{passive:true});
  document.addEventListener('focusin',()=>requestAnimationFrame(keepAnswerVisible));
  sync();updateViewport();
})();
