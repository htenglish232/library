/* Shared presentation layer. Existing engines retain grading, storage and audio ownership. */
import {minimalContexts} from './minimal-contexts.js';
export function setupMinimalUI({data=window.HT_PRACTICE_DATA||window.HT_GAME_SOURCE,exam=data.exam}={}) {
  if(document.documentElement.dataset.minimalReady==='true')return;
  const viewportMeta=document.querySelector('meta[name=viewport]');
  for(const option of ['viewport-fit=cover','interactive-widget=resizes-content'])if(!viewportMeta.content.includes(option))viewportMeta.content+=','+option;
  const $=id=>document.getElementById(id);
  const metadata=minimalContexts[exam.id];
  const shortTitle=`${exam.school} · Đề ${exam.number||1}`;
  const nav=document.querySelector('.question-navigation');
  const card=$('question-card'),feedback=$('feedback'),passage=$('passage-content');
  const heading=document.createElement('div');heading.className='minimal-heading';
  const title=document.createElement('h1');title.textContent=shortTitle;
  const count=document.createElement('span');count.id='minimal-question-count';
  heading.append(title,count);$('play').prepend(heading);

  // Move existing controls rather than creating a second set of navigation/actions.
  const tools=document.createElement('details');tools.id='minimal-tools';tools.hidden=true;
  const toolsLabel=document.createElement('summary');toolsLabel.textContent='Tùy chọn';tools.append(toolsLabel);
  const actions=document.createElement('div');actions.className='minimal-tool-actions';
  for(const id of ['home-button','results-button','restart-button','change-student'])if($(id))actions.append($(id));
  if($('sound-toggle'))$('sound-toggle').setAttribute('aria-label','Âm thanh hiệu ứng');
  tools.append(actions);document.querySelector('.header-actions').append(tools);
  tools.addEventListener('click',event=>{if(event.target.closest('button'))tools.open=false;});
  const list=document.createElement('details');list.id='minimal-question-list';
  const listLabel=document.createElement('summary');listLabel.textContent='☷ Danh sách câu';listLabel.setAttribute('aria-controls','question-dots');list.append(listLabel);
  let jump=$('jump-question');
  const legacyJump=!jump;
  let jumpControl=document.querySelector('.jump-control');
  if(legacyJump){jumpControl=document.createElement('label');jumpControl.className='jump-control';jumpControl.textContent='Đến câu ';jump=document.createElement('select');jump.id='jump-question';jumpControl.append(jump);jump.onchange=()=>{[...$('question-dots').querySelectorAll('button')].find(b=>b.dataset.questionId===jump.value)?.click();};}
  list.append(jumpControl,$('question-dots'));
  document.querySelector('.play-progress').after(list);
  const navCount=document.createElement('span');navCount.id='minimal-nav-count';navCount.setAttribute('aria-live','polite');
  nav.insertBefore(navCount,$('next-question'));
  nav.setAttribute('aria-label','Chuyển câu hỏi');nav.setAttribute('role','navigation');
  const missingAudio=document.createElement('p');missingAudio.id='minimal-audio-notice';missingAudio.textContent='Đề gốc chưa có tệp nghe. Em hãy nhờ giáo viên cung cấp.';
  // Place the existing player next to the prompt, so essential audio controls
  // never push the question itself below the first phone screen.
  $('prompt').after($('audio-panel'),missingAudio);
  document.querySelector('.welcome h1').textContent=shortTitle;

  function highlightBlank(number){
    if(!number)return;
    const walker=document.createTreeWalker(passage,NodeFilter.SHOW_TEXT);
    const re=new RegExp('\\(\\s*'+number+'\\s*\\)');
    while(walker.nextNode()){
      const node=walker.currentNode,match=node.textContent.match(re);if(!match)continue;
      const range=document.createRange();range.setStart(node,match.index);range.setEnd(node,match.index+match[0].length);
      const mark=document.createElement('mark');mark.className='minimal-blank';mark.setAttribute('aria-label',`Chỗ trống ${number} đang làm`);range.surroundContents(mark);break;
    }
  }
  let renderedId=null,readingKey=null,savedReadingScroll=0;
  const question=()=>data.questions.find(q=>q.id===card.dataset.questionId);
  function sync(){
    tools.hidden=$('session-tools')?$('session-tools').hidden:!$('student-label').textContent;
    const q=question();if(!q)return;
    const position=$('question-position').textContent.replace(/\s*\/\s*/,'/');
    count.textContent=navCount.textContent=position;
    $('previous-question').textContent='‹ Câu trước';
    $('next-question').textContent=$('next-question').textContent.toLocaleLowerCase('vi').includes('tổng kết')?'Tổng kết ›':'Câu tiếp ›';
    const passageIndex=metadata?.byQuestion[q.id];
    const html=passageIndex!==undefined?metadata.passages[passageIndex]:metadata?'':(q.contextHtml||(q.context!==undefined?data.contexts?.[q.context]:'')||data.passages?.[q.passage]||'');
    $('passage-panel').hidden=!html;
    $('question-layout').classList.toggle('with-passage',!!html);
    if(html){
      if(passage.innerHTML!==html)passage.innerHTML=html;
      highlightBlank(metadata.clozeMarkers[q.id]);
      if(readingKey===html)passage.scrollTop=savedReadingScroll;
      else passage.scrollTop=0;
    }
    readingKey=html||null;
    missingAudio.hidden=!!q.track||!/listen|nghe/i.test(data.sections?.find(s=>s.id===q.section)?.title||q.section);
    if(legacyJump){
      const dots=[...$('question-dots').querySelectorAll('button')];
      for(const button of dots)if(!button.dataset.questionId){const item=data.questions.find(item=>Number(item.number??item.id.replace(/^q/,''))===Number(button.textContent));if(item)button.dataset.questionId=item.id;}
      jump.replaceChildren(...dots.map(button=>{const option=document.createElement('option');option.value=button.dataset.questionId;option.textContent=`Câu ${button.textContent}`;option.selected=option.value===q.id;return option;}));
      jump.disabled=$('next-question').disabled;
    }
    const explanations=$('explanation-content').querySelectorAll('.explanation-item');
    if(explanations[0])explanations[0].querySelector('h3').textContent=q.autoGrade===false?'Đáp án tham khảo · cần giáo viên duyệt':'Đáp án';
    if(explanations[1]){
      explanations[1].querySelector('h3').textContent='Giải thích';
      if(!(q.explainHtml??q.source?.explain))explanations[1].lastElementChild.textContent='Chưa có lời giải chi tiết.';
    }
    let unverified=false;for(const child of $('explanation-content').children){if(child.classList.contains('support-notice'))unverified=true;if(unverified)child.hidden=true;}
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
  if($('session-tools'))observer.observe($('session-tools'),{attributes:true,attributeFilter:['hidden']});
  observer.observe($('student-label'),{childList:true});
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
  document.documentElement.dataset.minimalReady='true';
}
