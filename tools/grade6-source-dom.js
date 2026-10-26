// Parse source markup without executing any exam application or remote script.
({source,specs,stripSelectors=''})=>{
 const doc=new DOMParser().parseFromString(source,'text/html'),all=[...doc.querySelectorAll('*')];
 const clean=(node,{prompt=false,context=false}={})=>{
  const copy=node.cloneNode(true);
  if(stripSelectors)copy.querySelectorAll(stripSelectors).forEach(n=>n.remove());
  copy.querySelectorAll('script,style,iframe,object,embed,link,svg,audio,[data-listening-player],.ht-audio-player,[id^="ht-listening"],.explanation-box,.explain-box,.feedback-box,[id^="exp_"],[id^="explain"],[id^="feedback"],.placeholder,.placeholder-text').forEach(n=>n.remove());
  // Preserve explicit underline markup/styles; never infer phonetic substrings.
  copy.querySelectorAll('[class*="underline"],[style*="underline"]').forEach(n=>{if(n.tagName!=='U'){const u=doc.createElement('u');u.innerHTML=n.innerHTML;n.replaceWith(u);}});
  if(prompt)copy.querySelectorAll('label:has(input[type=radio]),.option-btn,.word-bank,.word-pool,.words-pool,.target-zone,.answer-zone,.answer-slot,.available-chips-box,[id^="slot_"],[id^="selected_"],[id$="-answer"],[id^="drop-"]').forEach(n=>n.remove());
  copy.querySelectorAll('button').forEach(n=>n.remove());
  copy.querySelectorAll('input,select,textarea').forEach(n=>prompt?n.replaceWith(doc.createTextNode(' ______ ')):n.remove());
  for(const n of [copy,...copy.querySelectorAll('*')])for(const a of [...n.attributes])if(!['colspan','rowspan'].includes(a.name))n.removeAttribute(a.name);
  return copy.innerHTML.trim();
 };
 const names=id=>[id,'q_'+id,'q-'+id,'card_'+id,'qBox_'+id,'qBox-'+id,'q_box_'+id,'box_'+id,'puzzle_'+id,'puzzle-'+id,'write_'+id,'writing-'+id,'block_'+id];
 const nodes=specs.map(s=>{
  let node=all.find(e=>['data-qid','data-wid','data-id','data-puzzle-id'].some(a=>e.getAttribute(a)===s.id))||names(s.id).map(id=>doc.getElementById(id)).find(Boolean);
  const inputs=[...doc.querySelectorAll('input,select,textarea')].filter(e=>names(s.id).includes(e.name)||names(s.id).includes(e.id)||e.name==='ans_'+s.id);
  if(!node&&inputs.length){
   node=inputs[0];
   while(node.parentElement&&!['SECTION','BODY','MAIN','HTML'].includes(node.parentElement.tagName)){
    const parent=node.parentElement,groups=[...parent.querySelectorAll('input:not([type=range]),select,textarea')];
    if(groups.some(e=>!inputs.includes(e)))break;
    node=parent;
    if(node.matches('.q-item,.q-card,.q-block,.question-block,.question-card,.question-item,.question-box,[data-qid]'))break;
   }
  }
  if(!node){
   const anchor=all.find(e=>['pool-'+s.id,'chips_'+s.id,'bank_'+s.id,s.id+'-pool'].includes(e.id));
   node=anchor?.closest('.writing-card,.puzzle-container,.puzzle-block,.word-puzzle-block,.word-puzzle,.question-card,.question-item,[data-puzzle]');
   if(!node&&anchor){node=anchor;while(node.parentElement&&!node.querySelector('p,strong')&&!['SECTION','BODY','MAIN'].includes(node.parentElement.tagName))node=node.parentElement;}
  }
  if(!node)throw Error('No source question anchor: '+s.id);
  const radios=[...node.querySelectorAll('input[type=radio]')];
  let options=radios.map(e=>({value:e.value,html:clean(e.closest('label')||e.parentElement)}));
  const select=node.querySelector('select');if(select)options=[...select.options].filter(o=>o.value).map(o=>({value:o.value,html:o.innerHTML}));
  if(!options.length)options=[...node.querySelectorAll('button[data-val]')].map(e=>({value:e.dataset.val,html:clean(e)}));
  const headings=[...doc.querySelectorAll('h2,h3,h4')].filter(h=>h.compareDocumentPosition(node)&Node.DOCUMENT_POSITION_FOLLOWING);
  const heading=[...headings].reverse().find(h=>/LISTENING|LANGUAGE|VOCABULARY|GRAMMAR|READING|WRITING|PRONUNCIATION/i.test(h.textContent));
  let tokens=[...node.querySelectorAll('.word-bank .chip,.words-pool .word-chip')].map(e=>e.getAttribute('data-word')||e.textContent.trim());
  const pool=node.querySelector('[data-words]');if(pool)tokens=JSON.parse(pool.getAttribute('data-words'));
  const attrs=Object.fromEntries([...node.attributes].filter(a=>a.name.startsWith('data-')).map(a=>[a.name,a.value]));
  return {node,inputs,id:s.id,options,tokens,attrs,heading:heading?.textContent.trim()||'',subheading:headings.at(-1)?.textContent.trim()||'',promptHtml:clean(node,{prompt:true}),sourcePosition:all.indexOf(node)};
 });
 if(new Set(nodes.map(r=>r.node)).size!==nodes.length)throw Error('Two questions share source container: '+JSON.stringify(nodes.filter((r,i)=>nodes.some((x,j)=>i!==j&&x.node===r.node)).map(r=>({id:r.id,html:r.node.outerHTML.slice(0,250)}))));
 const covered=new Set(nodes.flatMap(r=>[...r.node.querySelectorAll('input,select,textarea')]));
 const uncovered=[...doc.querySelectorAll('input:not([type=range]),select,textarea')].filter(e=>!covered.has(e)&&!e.closest('.ht-audio-player')&&!/name|student|class|school|file|audio|speed|voice|volume|date/i.test(e.name+' '+e.id+' '+e.type));
 if(uncovered.length)throw Error('Unmapped source controls: '+uncovered.map(e=>e.name||e.id));
 const contexts=[];
 const sectionContext=node=>{
  const section=node.closest('section')||node.parentElement;
  if(contexts.some(r=>r.node===section))return contexts.find(r=>r.node===section).html;
  const copy=section.cloneNode(true);
  // Mark source containers before deleting, retaining paths even when siblings move.
  for(const q of nodes)if(section.contains(q.node)&&section!==q.node){
   const path=[];let cur=q.node;while(cur!==section){path.unshift([...cur.parentElement.children].indexOf(cur));cur=cur.parentElement;}
   let other=copy;for(const i of path)other=other?.children[i];other?.setAttribute('data-question-remove','');
  }
  copy.querySelectorAll('[data-question-remove],[id*="transcript" i],[id*="result" i],[id*="submit" i],header,footer').forEach(n=>n.remove());
  const value=clean(copy,{context:true});contexts.push({node:section,html:value});return value;
 };
 return nodes.map(r=>({id:r.id,options:r.options,tokens:r.tokens,attrs:r.attrs,heading:r.heading,subheading:r.subheading,promptHtml:r.promptHtml,sourcePosition:r.sourcePosition,contextHtml:sectionContext(r.node)}));
}
