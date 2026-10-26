/* Device-only feedback. No media files, network, grading or progress writes. */
export const SOUND_PREFERENCE_KEY = 'htenglish:grade8:sound:v1';
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
  let enabled=true,context=null,generation=0;
  const active=new Set();
  try {enabled=storage().getItem(SOUND_PREFERENCE_KEY)!=='off';} catch { /* Keep the in-memory preference usable. */ }
  const supported=!!audioContextClass();
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
    if(!enabled||!supported||!visible()||event?.isTrusted!==true)return false;
    const cue=['correct','wrong'].includes(result)?SOUND_CUES[result]:null,finish=completed?SOUND_CUES.complete:null;
    if(!cue&&!finish)return false; // Teacher-pending is neither right nor wrong.
    stop();const ticket=generation,requestedAt=now();
    try {
      if(!context||context.state==='closed')context=new (audioContextClass())();
      if(context.state!=='running')await context.resume();
      // A blocked/slow resume must not replay an old answer later or after mute/background.
      if(ticket!==generation||!enabled||!visible()||context.state!=='running'||now()-requestedAt>500)return false;
      const start=context.currentTime+.008,level=listeningActive ? .025 : .06;
      if(cue)schedule(cue,start,level);
      if(finish){
        const delay=cue?Math.max(...cue.map(([offset,,duration])=>offset+duration))+.08:0;
        schedule(finish,start+delay,level);
      }
      return true;
    } catch {
      stop();return false; // Audio never blocks checking, XP or saving progress.
    }
  }
  return {get enabled(){return enabled;},supported,setEnabled,playFeedback,stop};
}
