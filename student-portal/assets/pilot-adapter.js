/* Portal-only adapter. The original launcher/controller remain byte-identical. */
(() => {
  const nativeOpen=HTDualStore.open;
  let state=null, identity=null, attemptId=null;
  HTDualStore.open=(data,student)=>{
    const store=nativeOpen(data,student,sessionStorage), save=store.save;
    state=store.state;
    store.save=session=>{state=session;return save(session);};
    return store;
  };
  HTDualStore.profile=()=>null;HTDualStore.remember=()=>true;HTDualStore.forget=()=>{};
  const send=message=>parent.postMessage(message,location.origin);
  window.addEventListener('message',event=>{
    if(event.origin!==location.origin||event.source!==parent)return;
    const m=event.data;
    if(m?.type==='portal-init'&&!identity&&/^[0-9a-f-]{36}$/.test(m.attemptId)&&typeof m.studentName==='string'){
      identity={name:m.studentName,code:m.attemptId};attemptId=m.attemptId;
      document.getElementById('student-name').value=identity.name;
      document.getElementById('student-code').value=identity.code;
      document.getElementById('start-form').requestSubmit();
      if(!document.getElementById('resume-panel').hidden)document.getElementById('resume-button').click();
      send({type:'portal-started',attemptId});
    }
    if(m?.type==='portal-export'&&m.attemptId===attemptId&&state){
      const answers=Object.fromEntries(HT_PRACTICE_DATA.questions.map(q=>{
        const a=state.answers[q.id];return [q.id,a.first?.draft||a.draft];
      }));
      send({type:'portal-answers',attemptId,answers});
    }
  });
  document.addEventListener('click',event=>{if(event.target.closest('a[href]'))event.preventDefault();});
  document.addEventListener('DOMContentLoaded',()=>send({type:'portal-ready'}));
})();
