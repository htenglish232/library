/* Shared feedback only. Never changes Listening media, grading or progress. */
export const SOUND_PREFERENCE_KEY = 'htenglish:grade8:sound:v1';
export const SOUND_VOLUME_KEY = 'htenglish:grade8:sound-volume:v1';
const wavFiles = Object.fromEntries(['correct','wrong','complete'].map(kind=>[
  kind,new URL(`./sounds/${kind}.wav`,import.meta.url).href
]));
// Fetch ahead without opening an audio device or playing anything. Resolve failures
// to null so offline/404/corrupt files can always use the original sine cues.
let wavBytes;
function preloadWavs() {
  return wavBytes ||= Object.fromEntries(Object.entries(wavFiles).map(([kind,url])=>[
    kind,(async()=>{
      const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),8000);
      try {
        const response=await fetch(url,{signal:controller.signal});
        if(!response.ok)return null;
        return await response.arrayBuffer();
      } catch {return null;} finally {clearTimeout(timer);}
    })()
  ]));
}
const notes = values => Object.freeze(values.map(note => Object.freeze(note)));
// [offset in seconds, frequency in Hz, duration in seconds]. Sine waves only.
export const SOUND_CUES = Object.freeze({
  correct: notes([[0,523.25,.23],[.25,783.99,.25]]),
  wrong: notes([[0,261.63,.18],[.2,196,.2]]),
  complete: notes([[0,523.25,.18],[.2,659.25,.18],[.4,783.99,.18],[.6,1046.5,.3],[1,1318.51,.5]])
});

export function createGameSound({
  storage = () => globalThis.localStorage,
  audioContextClass = () => globalThis.AudioContext || globalThis.webkitAudioContext,
  visible = () => !globalThis.document?.hidden,
  now = () => globalThis.performance.now()
} = {}) {
  let enabled=true,volume=.7,context=null,generation=0;
  const active=new Set();
  try {enabled=storage().getItem(SOUND_PREFERENCE_KEY)!=='off';} catch { /* Keep the in-memory preference usable. */ }
  try {
    const saved=storage().getItem(SOUND_VOLUME_KEY),value=Number(saved);
    if(saved!==null&&Number.isFinite(value)&&value>=0&&value<=1)volume=value;
  } catch { /* Keep the default volume when storage is unavailable. */ }
  const supported=!!audioContextClass();
  const files=supported?preloadWavs():null,decoded=new Map();
  function bufferFor(kind) {
    if(!context.decodeAudioData||!context.createBufferSource)return Promise.resolve(null);
    if(!decoded.has(kind))decoded.set(kind,files[kind].then(bytes=>{
      if(!bytes)return null;
      // Callback form also works in Safari; clone because decoding detaches bytes.
      return new Promise((resolve,reject)=>{
        const decoding=context.decodeAudioData(bytes.slice(0),resolve,reject);
        // Modern browsers also return a Promise even with callbacks. Handle its
        // rejection too, avoiding an unhandled error for a corrupt WAV.
        decoding?.catch?.(reject);
      });
    }).catch(()=>null));
    return decoded.get(kind);
  }
  function stop() {
    generation++;
    if(!context)return;
    for(const node of active){
      try {
        node.gain.gain.cancelScheduledValues(context.currentTime);
        node.gain.gain.setTargetAtTime(0,context.currentTime,.004);
        node.oscillator.stop(context.currentTime+.02);
        if(context.state!=='running'){node.oscillator.disconnect();node.gain.disconnect();}
      } catch { /* Already ended or device unavailable. */ }
    }
    active.clear();
  }
  function setEnabled(value,persist=true) {
    enabled=!!value;
    if(!enabled)stop();
    if(persist)try {storage().setItem(SOUND_PREFERENCE_KEY,enabled?'on':'off');} catch { /* Never touch progress records. */ }
    return enabled;
  }
  function setVolume(value,persist=true) {
    if(!Number.isFinite(value))return volume;
    volume=Math.max(0,Math.min(1,value));
    if(volume===0)stop();
    if(persist)try {storage().setItem(SOUND_VOLUME_KEY,String(volume));} catch { /* Device preference only. */ }
    return volume;
  }
  function scheduleWav(buffer,start,level) {
    const oscillator=context.createBufferSource(),gain=context.createGain();
    const node={oscillator,gain};active.add(node);
    oscillator.buffer=buffer;gain.gain.value=level;
    oscillator.connect(gain);gain.connect(context.destination);
    oscillator.onended=()=>{active.delete(node);oscillator.disconnect();gain.disconnect();};
    oscillator.start(start);
  }
  function schedule(cue,start,level) {
    for(const [offset,frequency,duration] of cue){
      const oscillator=context.createOscillator(),gain=context.createGain();
      const node={oscillator,gain};active.add(node);
      const at=start+offset,end=at+duration;
      gain.gain.value=0; // Even a future note cancelled before its start must remain silent.
      oscillator.type='sine';oscillator.frequency.setValueAtTime(frequency,at);
      gain.gain.setValueAtTime(0,at);
      gain.gain.linearRampToValueAtTime(level,at+.015);
      gain.gain.setValueAtTime(level,end-.06);
      gain.gain.linearRampToValueAtTime(0,end);
      oscillator.connect(gain);gain.connect(context.destination);
      oscillator.onended=()=>{active.delete(node);oscillator.disconnect();gain.disconnect();};
      oscillator.start(at);oscillator.stop(end+.01);
    }
  }
  // Called synchronously from the student's trusted answer click, never render/restore.
  // resume() runs inside that gesture for Chrome/Edge and Safari's suspended/interrupted state.
  async function playFeedback(result,{completed=false,listeningActive=false,event}={}) {
    if(!enabled||volume===0||!supported||!visible()||event?.isTrusted!==true)return false;
    const cue=['correct','wrong'].includes(result)?SOUND_CUES[result]:null,finish=completed?SOUND_CUES.complete:null;
    if(!cue&&!finish)return false; // Teacher-pending is neither right nor wrong.
    stop();const ticket=generation,requestedAt=now();
    try {
      if(!context||context.state==='closed')context=new (audioContextClass())();
      if(context.state!=='running')await context.resume();
      let buffers=[];
      if(context.decodeAudioData&&context.createBufferSource){
        // Bound waiting: a late download/decode never replays an old answer.
        // Completed decoding may be reused by the NEXT trusted answer click.
        const kinds=[...(cue?[result]:[]),...(finish?['complete']:[])];
        let timer;
        try {buffers=await Promise.race([
          Promise.all(kinds.map(bufferFor)),
          new Promise(resolve=>{timer=setTimeout(()=>resolve([]),120);})
        ]);} finally {clearTimeout(timer);}
      }
      // A blocked/slow resume must not replay an old answer later or after mute/background.
      if(ticket!==generation||!enabled||!visible()||context.state!=='running'||now()-requestedAt>500)return false;
      const start=context.currentTime+.008,level=(listeningActive ? .025 : .06)*(volume/.7);
      const cueBuffer=cue?buffers[0]:null,finishBuffer=finish?buffers[cue?1:0]:null;
      const wavLevel=volume*(listeningActive ? .4 : 1);
      if(cue){if(cueBuffer)scheduleWav(cueBuffer,start,wavLevel);else schedule(cue,start,level);}
      if(finish){
        const delay=cue?(cueBuffer?cueBuffer.duration:Math.max(...cue.map(([offset,,duration])=>offset+duration)))+.08:0;
        if(finishBuffer)scheduleWav(finishBuffer,start+delay,wavLevel);else schedule(finish,start+delay,level);
      }
      return true;
    } catch {
      stop();return false; // Audio never blocks checking, XP or saving progress.
    }
  }
  return {get enabled(){return enabled;},get volume(){return volume;},supported,setEnabled,setVolume,playFeedback,stop};
}
