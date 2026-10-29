// Read presentation passages from verified source/context markup; never run exam JS.
({source,data})=>{
 const doc=new DOMParser().parseFromString(source,'text/html'),all=[...doc.querySelectorAll('*')];
 const norm=s=>s.normalize('NFC').replace(/\s+/g,' ').trim();
 const instruction=s=>/^(?:(?:[IVX]+|[A-D]|\d+)[.)]\s*)?(?:read\b|choose\b|circle\b|task\b|part\b|answer\b|listen\b|complete\b|decide\b|đọc\b)/i.test(s.trim());
 const long=el=>norm(el.textContent).split(' ').length>=24&&!instruction(el.textContent);
 const aliases=id=>[id,'q_'+id,'q-'+id,'card_'+id,'qBox_'+id,'qBox-'+id,'box_'+id,'puzzle_'+id,'puzzle-'+id];
 function locate(q){
  if(Number.isInteger(q.sourcePosition))return all[q.sourcePosition];
  let node=all.find(n=>['data-qid','data-wid','data-id','data-puzzle-id'].some(a=>n.getAttribute(a)===q.id));
  if(node)return node;
  const control=[...doc.querySelectorAll('input,textarea,select')].find(n=>aliases(q.id).includes(n.name)||aliases(q.id).includes(n.id));
  return control?.closest('[data-qid],.question-card,.question-item,.q-card,.question-block,.q-block')||control;
 }
 function clean(node,inner=false){
  const copy=node.cloneNode(true);
  copy.querySelectorAll('script,style,iframe,object,embed,button,audio,input,textarea,select,[id*="transcript" i],[id*="result" i],[id*="score" i],[id^="explain"],[id^="exp_"],[id^="feedback"],.feedback-box,.explanation-box').forEach(n=>n.remove());
  copy.querySelectorAll('[class*="underline"],[style*="underline"]').forEach(n=>{if(n.tagName!=='U'){const u=doc.createElement('u');u.innerHTML=n.innerHTML;n.replaceWith(u);}});
  for(const n of [copy,...copy.querySelectorAll('*')])for(const a of [...n.attributes])if(!['colspan','rowspan','src','alt','width','height'].includes(a.name))n.removeAttribute(a.name);
  return inner?copy.innerHTML:copy.outerHTML;
 }
 const allContexts=[...new Set(data.questions.map(q=>q.contextHtml||(q.context!==undefined?data.contexts?.[q.context]:'')).filter(Boolean))];
 const candidates=[];
 function add(node){
  const text=norm(node.textContent);if(!text||candidates.some(c=>c.text===text))return;
  const matches=all.filter(n=>['P','DIV','BLOCKQUOTE','ARTICLE'].includes(n.tagName)&&norm(n.textContent)===text&&!n.closest('[id*="transcript" i],[id*="explain" i],.explanation-box'));
  candidates.push({text,html:clean(node,node.dataset.contextRoot==='true'),matches});
 }
 for(const html of allContexts){
  const root=doc.createElement('div');root.innerHTML=html;root.dataset.contextRoot='true';
  if(!/READING|Reading|reading|đọc|cloze/.test(root.querySelector('h2,h3')?.textContent||'') && !data.questions.some(q=>(q.contextHtml===html||data.contexts?.[q.context]===html)&&/reading|cloze|đọc/i.test(data.sections?.find(s=>s.id===q.section)?.title||q.section)))continue;
  const paragraphs=[...root.querySelectorAll('p')].filter(long);
  for(const p of paragraphs){
   let box=p.parentElement;
   const headings=[...box.querySelectorAll('h2,h3,h4,h5')];
   if(box===root || headings.some(h=>instruction(h.textContent)||/^(?:part [a-d].*)?(?:reading|listening|writing|language)/i.test(norm(h.textContent)))){
    box=doc.createElement('div');
    // Adjacent source paragraphs share a passage; a heading/div boundary separates tasks.
    let first=p;while(first.previousElementSibling?.matches('p')&&!instruction(first.previousElementSibling.textContent))first=first.previousElementSibling;
    const heading=first.previousElementSibling;
    if(heading?.matches('h1,h2,h3,h4,h5')&&!instruction(heading.textContent)&&!/reading|listening|writing|language/i.test(heading.textContent))box.append(heading.cloneNode(true));
    for(let cur=first;cur?.matches('p')&&!instruction(cur.textContent);cur=cur.nextElementSibling)box.append(cur.cloneNode(true));
   }
   add(box);
  }
  {
   const leaves=[...root.querySelectorAll('div,blockquote,article')].filter(n=>!n.querySelector('p,table,article,blockquote')&&long(n)&&[...n.childNodes].filter(c=>c.nodeType===Node.TEXT_NODE).map(c=>c.textContent).join(' ').trim().split(/\s+/).length>=24);
   if(leaves.length)leaves.forEach(add);else if(!paragraphs.length&&long(root))add(root);
  }
 }
 // Source-only passages missing from an old presentation payload are retained
 // using their original paragraph blocks, not rewritten text.
 const sourceReading=[...doc.querySelectorAll('p,div,li,blockquote')].filter(p=>!p.querySelector('p,div,li,blockquote')&&long(p)&&!p.closest('script,[id*="transcript" i],[id*="explain" i],.explanation-box')).filter(p=>{
  const head=[...doc.querySelectorAll('h2,h3,h4')].reverse().find(h=>(h.compareDocumentPosition(p)&Node.DOCUMENT_POSITION_FOLLOWING)&&/READING|WRITING|LISTENING|LANGUAGE|VOCABULARY|GRAMMAR/i.test(h.textContent));
  return /reading/i.test(head?.textContent||'');
 });
 for(const p of sourceReading){
  if(candidates.some(c=>c.text.includes(norm(p.textContent))))continue;
  const box=p.closest('ul,ol')||p.parentElement;
  if(!box.querySelector('input,select,textarea,button')&&![...box.querySelectorAll('h2,h3,h4,h5')].some(h=>instruction(h.textContent)))add(box);
 }
 const results=[];
 const readingSections=[];
 for(const q of data.questions){
  const section=data.sections?.find(s=>s.id===q.section),raw=q.contextHtml||(q.context!==undefined?data.contexts?.[q.context]:'')||'';
  const root=doc.createElement('div');root.innerHTML=raw;
  const node=locate(q),heading=node?[...doc.querySelectorAll('h2,h3,h4')].reverse().find(h=>(h.compareDocumentPosition(node)&Node.DOCUMENT_POSITION_FOLLOWING)&&/READING|WRITING|LISTENING|LANGUAGE|VOCABULARY|GRAMMAR/i.test(h.textContent)):null;
  const reading=!q.track&&(/reading|cloze|đọc/i.test(section?.title||q.section)||/reading|cloze|đọc/i.test(root.querySelector('h2,h3')?.textContent||'')||/reading/i.test(heading?.textContent||''));
  if(!reading){results.push({id:q.id,html:'',reading:false});continue;}
  if(!readingSections.includes(q.section))readingSections.push(q.section);
  let chosen=null,evidence='';
  const contained=candidates.filter(c=>norm(root.textContent).includes(c.text));
  if(contained.length===1){chosen=contained[0];evidence='single-source-passage';}
  if(!chosen&&node){
   const allowed=contained.length?contained:candidates;
   const before=allowed.flatMap(c=>c.matches.filter(m=>m.compareDocumentPosition(node)&Node.DOCUMENT_POSITION_FOLLOWING).map(m=>({c,index:all.indexOf(m)}))).sort((a,b)=>b.index-a.index);
   if(before.length){chosen=before[0].c;evidence='source-position';}
  }
  if(!chosen&&contained.length===2){
   chosen=contained[readingSections.indexOf(q.section)===0?0:1];evidence='ordered-source-groups';
  }
  results.push({id:q.id,reading:true,html:chosen?.html||'',evidence,section:q.section,title:section?.title||q.section});
 }
 return {questions:results,candidates:candidates.map(c=>({text:c.text.slice(0,100),html:c.html,positions:c.matches.map(m=>all.indexOf(m))}))};
}
