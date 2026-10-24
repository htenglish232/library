// Run in an empty browser page via DOMParser; never executes the original app.
({source, specs}) => {
 const doc=new DOMParser().parseFromString(source,'text/html');
 const clean=(node,removeOptions=false)=>{
  if(!node)return '';
  const copy=node.cloneNode(true);
  copy.querySelectorAll('script,style,button,audio,svg,[id^="expl"],[id^="exp_"],[id^="feedback"],.feedback-box,.explanation-box,.status-indicator').forEach(n=>n.remove());
  if(removeOptions)copy.querySelectorAll('label').forEach(n=>{if(n.querySelector('input[type=radio]'))n.remove();});
  copy.querySelectorAll('[class*=underline]').forEach(n=>{if(n.tagName!=='U'){const u=doc.createElement('u');u.innerHTML=n.innerHTML;n.replaceWith(u);}});
  copy.querySelectorAll('input,select,textarea').forEach(n=>n.replaceWith(doc.createTextNode(' ______ ')));
  for(const el of [copy,...copy.querySelectorAll('*')])for(const a of [...el.attributes])if(!['colspan','rowspan'].includes(a.name))el.removeAttribute(a.name);
  return copy.innerHTML.trim();
 };
 const norm=s=>s.toLowerCase().replace(/^(?:input|inp|ans|q)[_-]/,'').replace(/[-_]/g,'');
 const controls=[...doc.querySelectorAll('input:not([type=range]),select,textarea')].filter(e=>!e.closest('[data-listening-player],.ht-listening-player,.modern-listening-player'));
 const findControl=names=>controls.filter(e=>names.includes(e.name)||names.includes(e.id)||names.some(n=>norm(n)===norm(e.name||e.id)));
 const nodes=specs.map(s=>{
  const inputs=findControl(s.aliases||[s.id]);
  let anchor=(s.anchors||[]).map(id=>doc.getElementById(id)).find(Boolean)||inputs[0];
  if(!anchor)return {spec:s,error:'No source DOM anchor: '+s.id};
  let node=anchor;
  if(s.anchors?.length)node=anchor.closest('.question-item,.question-block,.q-card,[id^=card_],[id^=qbox],[id^=q-block],[id^=q-container],[id^=rearrange-container]')||anchor;
  if(!s.anchors?.some(id=>doc.getElementById(id)===anchor)){
   const labels=inputs.filter(e=>e.type==='radio').map(e=>e.closest('label')||e);
   let candidate=anchor.parentElement;
   // Prefer a complete question container, not an option bank or input wrapper.
   while(candidate&& !['MAIN','BODY','HTML','SECTION'].includes(candidate.tagName)){
    const groups=new Set([...candidate.querySelectorAll('input:not([type=range]),select,textarea')].map(e=>e.name||e.id));
    const own=new Set(inputs.map(e=>e.name||e.id));
    if([...groups].some(g=>!own.has(g)))break;
    node=candidate;
    if(candidate.matches('tr,.question-card,.question-item,.q-card,.question-container,[id^="q-block"],[id^="qbox"],[id^="card_"],[id^="q-container"]'))break;
    candidate=candidate.parentElement;
   }
  }
  const radios=inputs.filter(e=>e.type==='radio');
  let options=radios.map(e=>({value:e.value,html:clean(e.closest('label'))||e.value}));
  const select=inputs.find(e=>e.tagName==='SELECT');
  if(select)options=[...select.options].filter(o=>o.value).map(o=>({value:o.value,html:o.textContent}));
  const before=[...doc.querySelectorAll('h2,h3,h4')].filter(h=>h.compareDocumentPosition(node)&Node.DOCUMENT_POSITION_FOLLOWING);
  const heading=[...before].reverse().find(h=>/LISTENING|LANGUAGE|VOCABULARY|GRAMMAR|READING|WRITING|PRONUNCIATION/i.test(h.textContent));
  return {spec:s,node,inputs,options,promptHtml:clean(node,true),heading:heading?.textContent.trim()||'',subheading:before.at(-1)?.textContent.trim()||''};
 });
 // Context contains the original instructions, passages, tables and word boxes.
 // Remove answer cards from a cloned source section, keeping every source word.
 const covered=new Set(nodes.flatMap(r=>r.inputs||[]));
 const ignored=e=>/student|class|school|date|speed|volume|name/i.test(e.name+' '+e.id)||e.type==='hidden'||e.type==='checkbox';
 const uncovered=controls.filter(e=>!covered.has(e)&&!ignored(e)).map(e=>e.name||e.id);
 if(uncovered.length)throw Error('Unmapped source answer controls: '+uncovered.join(', '));
 const allNodes=nodes.map(r=>r.node).filter(Boolean);
 return nodes.map(r=>{
  if(r.error)return r;
  let section=r.node.closest('section');
  if(!section){section=r.node.parentElement;while(section.parentElement&&!section.querySelector('h3,h2'))section=section.parentElement;}
  const clone=section.cloneNode(true);
  for(const n of allNodes){if(section.contains(n)&&n!==section){
   const indices=[];let cur=n;while(cur!==section){indices.unshift([...cur.parentElement.children].indexOf(cur));cur=cur.parentElement;}
   let other=clone;for(const i of indices)other=other?.children[i];if(other)other.setAttribute('data-extracted-question','');
  }}
  clone.querySelectorAll('[data-extracted-question]').forEach(n=>n.remove());
  clone.querySelectorAll('[id*="transcript" i],[id*="result" i],[id*="score" i],[id*="confirm" i],header,footer,form').forEach(n=>n.remove());
  const audio=[...doc.querySelectorAll('audio')].filter(a=>a.getAttribute('src')||a.querySelector('source[src]'));
  const sourceAudioIndex=audio.filter(a=>a.compareDocumentPosition(r.node)&Node.DOCUMENT_POSITION_FOLLOWING).length-1;
  return {sourceAudioIndex,id:r.spec.id,promptHtml:r.promptHtml,options:r.options,heading:r.heading,subheading:r.subheading,contextHtml:clean(clone),sourcePosition:[...doc.querySelectorAll('*')].indexOf(r.node),inputCount:r.inputs.filter(e=>!['radio','select-one'].includes(e.type)).length};
 });
}
