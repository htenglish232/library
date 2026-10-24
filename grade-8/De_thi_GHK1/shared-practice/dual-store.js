/* Device-only, per-exam/per-learner storage. Never enumerates other learners. */
(() => {
  'use strict';
  const keyFor=(data,student)=>'htenglish:practice:v1:'+encodeURIComponent(data.exam.id)+':'+encodeURIComponent(HTDualProgress.identity(student.name,student.code).key);
  function open(data,student,providedStorage) {
    const key=keyFor(data,student);let storage=providedStorage,lastRaw=null,status='empty',state=null;
    try {storage=storage||globalThis.localStorage;lastRaw=storage.getItem(key);} catch {status='blocked';}
    if(lastRaw!==null){
      try {
        if(lastRaw.length>500000)throw Error('Oversized record');
        const record=JSON.parse(lastRaw);
        if(record.schemaVersion!==1||record.examId!==data.exam.id||record.contentVersion!==data.contentVersion)status='incompatible';
        else {state=HTDualProgress.restore(data,student,record.state);status='found';}
      } catch {status='corrupt';}
    }
    return {key,get status(){return status;},get state(){return state;},get lastRaw(){return lastRaw;},
      save(session){
        if(['corrupt','incompatible'].includes(status))return 'conflict';
        // Validate the snapshot, derive XP from first answers, never trust counters.
        const validated=HTDualProgress.restore(data,student,session);
        const bytes=JSON.stringify({schemaVersion:1,examId:data.exam.id,contentVersion:data.contentVersion,updatedAt:new Date().toISOString(),state:validated});
        try {
          if(!storage)storage=globalThis.localStorage;
          if(storage.getItem(key)!==lastRaw)return 'conflict';
          if(status==='found' && lastRaw && JSON.stringify(JSON.parse(lastRaw).state)===JSON.stringify(validated)){state=validated;return 'saved';}
          storage.setItem(key,bytes);lastRaw=bytes;state=validated;status='found';return 'saved';
        } catch {return 'blocked';}
      },
      reset(){
        try {
          if(!storage)storage=globalThis.localStorage;
          if(storage.getItem(key)!==lastRaw)return 'conflict';
          storage.removeItem(key);lastRaw=null;state=null;status='empty';return 'reset';
        } catch {status='blocked';return 'blocked';}
      }
    };
  }
  const profileKey='htenglish:grade8:active-student:v1';
  function profile(storage) {
    try {storage=storage||globalThis.localStorage;const raw=JSON.parse(storage.getItem(profileKey));return HTDualProgress.identity(raw.name,raw.code);} catch {return null;}
  }
  function remember(student,storage) {
    try {(storage||globalThis.localStorage).setItem(profileKey,JSON.stringify(HTDualProgress.identity(student.name,student.code)));return true;} catch {return false;}
  }
  function forget(storage) {
    try {(storage||globalThis.localStorage).removeItem(profileKey);} catch { /* Progress records remain untouched. */ }
  }
  globalThis.HTDualStore={keyFor,open,profile,remember,forget,profileKey};
})();
