const tabs=document.getElementById('tabs'), content=document.getElementById('content'), search=document.getElementById('search'), empty=document.getElementById('empty'), stats=document.getElementById('stats');
let current=0;
let DATA = [];
function updateStats() { const total=DATA.reduce((n,g)=>n+g.units.reduce((m,u)=>m+u.lessons.length,0),0); stats.textContent=`${total} bài học`; }
function toggle(el){ el.classList.toggle('open'); }
function unitNumber(u){ const m=u.name.match(/Unit\s+(\d+)/i); return m?Number(m[1]):999; }
export function render(q=''){
 tabs.innerHTML=''; content.innerHTML=''; let found=false;
 DATA.forEach((g,gi)=>{
   const b=document.createElement('button'); b.className='tab'+(gi===current?' active':''); b.textContent=g.grade;
   b.onclick=()=>{current=gi;render(search.value)}; tabs.appendChild(b);
   const sec=document.createElement('section'); sec.className='grade-section'+(gi===current?' active':'');
   if(gi!==current){ content.appendChild(sec); return; }
   const needle=q.toLowerCase();

   if(g.grade==='Grade 4' || g.grade==='Grade 5'){
     const all=g.units.flatMap(u=>u.lessons).filter(l=>!q || (g.grade+' Bổ trợ ngữ pháp '+l.title).toLowerCase().includes(needle));
     if(all.length){
       found=true;
       all.sort((a,b)=>{const na=Number((a.title.match(/Unit\s+(\d+)/i)||[])[1]||999), nb=Number((b.title.match(/Unit\s+(\d+)/i)||[])[1]||999); return na-nb;});
       const folder=document.createElement('div'); folder.className='folder'+(q?' open':'');
       folder.innerHTML=`<div class="folder-head"><div class="folder-title"><span class="folder-icon">📁</span><h3>Bổ trợ ngữ pháp</h3></div><div><span class="badge">${all.length} bài</span> <span class="chev">›</span></div></div><div class="folder-body"><div class="grammar-list"></div></div>`;
       folder.querySelector('.folder-head').onclick=()=>toggle(folder);
       const list=folder.querySelector('.grammar-list');
       all.forEach(l=>{ const a=document.createElement('a'); a.className='lesson'; a.href=l.href; a.innerHTML=`<strong>${l.title}</strong>`; list.appendChild(a); });
       sec.appendChild(folder);
     }
   } else {
     const categories=[...new Set(g.units.filter(u=>u.type!=='exam-folder').map(u=>u.name.split(' · ')[0]))];
     categories.forEach(category=>{
       const matchingUnits=g.units.filter(u=>u.name.startsWith(category+' · ')).map(u=>({u,lessons:u.lessons.filter((l,li)=>!q || (g.grade+' '+category+' '+u.name+' '+l.title+' '+(li+1)).toLowerCase().includes(needle))})).filter(x=>x.lessons.length);
       if(!matchingUnits.length) return;
       found=true;
       matchingUnits.sort((a,b)=>unitNumber(a.u)-unitNumber(b.u));
       const folder=document.createElement('div'); folder.className='folder'+(q?' open':'');
       folder.innerHTML=`<div class="folder-head"><div class="folder-title"><span class="folder-icon">📁</span><h3>${category}</h3></div><div><span class="badge">${matchingUnits.length} Unit</span> <span class="chev">›</span></div></div><div class="folder-body"></div>`;
       folder.querySelector('.folder-head').onclick=()=>toggle(folder);
       const body=folder.querySelector('.folder-body');
       matchingUnits.forEach(({u,lessons})=>{
         const num=(u.name.match(/Unit\s+(\d+)/i)||[])[1]||'';
         const box=document.createElement('div'); box.className='unit nested-unit'+(q?' open':'');
         box.innerHTML=`<div class="unit-head"><h3>Unit ${num}</h3><div><span class="badge">${lessons.length} bài</span> <span class="chev">›</span></div></div>`;
         box.querySelector('.unit-head').onclick=()=>toggle(box);
         const grid=document.createElement('div'); grid.className='lessons';
         lessons.forEach(l=>{ const originalIndex=u.lessons.indexOf(l); const a=document.createElement('a'); a.className='lesson'; a.href=l.href; a.innerHTML=`<strong>${originalIndex+1}. ${l.title}</strong>`; grid.appendChild(a); });
         box.appendChild(grid); body.appendChild(box);
       });
       sec.appendChild(folder);
     });
     g.units.filter(u=>u.type==='exam-folder').forEach(examFolder=>{
       const lessons=examFolder.lessons.filter(l=>!q || (g.grade+' '+examFolder.name+' '+l.title).toLowerCase().includes(needle));
       if(!lessons.length) return;
       found=true;
       const folder=document.createElement('div'); folder.className='folder'+(q?' open':'');
       folder.innerHTML=`<div class="folder-head"><div class="folder-title"><span class="folder-icon">📁</span><h3>${examFolder.name}</h3></div><div><span class="badge">${lessons.length} đề</span> <span class="chev">›</span></div></div><div class="folder-body"><div class="grammar-list"></div></div>`;
       folder.querySelector('.folder-head').onclick=()=>toggle(folder);
       const list=folder.querySelector('.grammar-list');
       lessons.forEach(l=>{ const a=document.createElement('a'); a.className='lesson'; a.href=l.href; a.innerHTML=`<strong>${l.title}</strong>`; list.appendChild(a); });
       sec.appendChild(folder);
     });
   }
   content.appendChild(sec);
 });
 empty.style.display=found?'none':'block';
}
search.addEventListener('input',()=>render(search.value.trim()));
export function setCatalog(data) { DATA = data; current = 0; search.value = ''; updateStats(); render(); }
export function clearCatalog() { DATA = []; content.replaceChildren(); tabs.replaceChildren(); stats.textContent = ''; search.value = ''; empty.style.display = 'none'; }
