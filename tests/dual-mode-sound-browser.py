from practice_browser_controls import control
"""Real Chromium sine FALLBACK, desktop/touch, default autoplay policy and OfflineAudioContext.

Intentionally serve corrupt WAV bytes to test the original fallback contract.
Native WAV playback for all grades is covered in dual-mode-wav-browser.py.

Phone profiles emulate input/viewport; this is not a claim about physical speakers,
Microsoft Edge binaries or Safari/iOS hardware.
"""
from pathlib import Path
from urllib.parse import quote,unquote
import functools,http.server,json,math,os,re,shutil,threading,importlib.util
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('DUAL_SOUND_OUTPUT','/tmp/ht-dual-sound-tests'));OUT.mkdir(parents=True,exist_ok=True)
# Use the existing MP3-range handler without executing its test suite.
exec('class Handler'+(ROOT/'tests/dual-mode-browser.py').read_text().split('class Handler',1)[1].split('server=http.server',1)[0])
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}/'
spec=importlib.util.spec_from_file_location('sound_audit',ROOT/'tools/audit-grade8-sound-loading.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
rows=[{**r,'game':r['html']} for r in audit.inventory()]
TT=next(r for r in rows if 'truc-tuan-dual-mode.html' in r['game'])
MODULE=BASE+'library/grade-8/De_thi_GHK1/shared-practice/dual-sound.js'
SPY='''(() => {
 const Native=window.AudioContext||window.webkitAudioContext;
 window.soundLog={contexts:0,resumes:0,notes:[],gains:[],media:[]};
 function Tracked(...args){
  const ctx=new Native(...args);soundLog.contexts++;
  const resume=ctx.resume.bind(ctx);ctx.resume=()=>{soundLog.resumes++;return resume();};
  const osc=ctx.createOscillator.bind(ctx);ctx.createOscillator=()=>{
   const o=osc(),note={frequency:0,start:0,stop:0};
   const frequency=o.frequency.setValueAtTime.bind(o.frequency);o.frequency.setValueAtTime=(v,t)=>{note.frequency=v;return frequency(v,t);};
   const start=o.start.bind(o);o.start=t=>{note.start=t;soundLog.notes.push(note);return start(t);};
   const stop=o.stop.bind(o);o.stop=t=>{note.stop=t;return stop(t);};return o;
  };
  const gain=ctx.createGain.bind(ctx);ctx.createGain=()=>{const g=gain(),ramp=g.gain.linearRampToValueAtTime.bind(g.gain);g.gain.linearRampToValueAtTime=(v,t)=>{soundLog.gains.push(v);return ramp(v,t);};return g;};
  return ctx;
 }
 Tracked.prototype=Native.prototype;window.AudioContext=Tracked;
 for(const method of ['play','pause','load']){
  const original=HTMLMediaElement.prototype[method];HTMLMediaElement.prototype[method]=function(...a){soundLog.media.push(method);return original.apply(this,a);};
 }
})();'''
errors=[];external=[];bad=[];checks=[]
def passed(msg):checks.append(msg);print('PASS '+msg,flush=True)
def click(page,selector,touch=False):
 target=control(page,selector)
 if touch:target.tap()
 else:target.click()
def start(page,touch=False):
 page.locator('#student-name').fill('Sound Check')
 if not page.locator('#student-code').is_visible():click(page,'.identity-options summary',touch)
 page.locator('#student-code').fill('8A');click(page,'#start-form button',touch)
 if page.locator('#resume-panel').is_visible():click(page,'#resume-button',touch)
def log(page):return page.evaluate('structuredClone(soundLog)')
def answer_choice(page,q,wrong=False,touch=False):
 value=next(o['value'] for o in q['options'] if o['value'] not in q['accepted']) if wrong else q['accepted'][0] if q['accepted'] else q['options'][0]['value']
 target=page.locator(f'#answer-area input[value="{value}"]')
 if touch:target.tap()
 else:target.check()
 click(page,'#check-answer',touch)
def open_game(page,row):
 page.goto(BASE+'library/'+quote(row['game']));expect(control(page,'#sound-toggle')).to_have_count(1);expect(control(page,'#sound-toggle')).to_have_attribute('data-sound-state','ready');expect(control(page,'#sound-toggle')).to_be_enabled();return page.evaluate('HT_PRACTICE_DATA')
def seed_completion(page,target_id=None):
 return page.evaluate('''targetId=>{
  const d=HT_PRACTICE_DATA,P=HTDualProgress,state=P.create(d,{name:'Sound Check',code:'8A'}),target=d.questions.find(q=>q.id===targetId)||d.questions[1];
  for(const q of d.questions){if(q.id===target.id)continue;const draft=P.blank(q);
   if(q.kind==='choice')draft.value=q.id===d.questions[0].id?q.options.find(o=>!q.accepted.includes(o.value)).value:(q.accepted[0]||q.options[0].value);
   else if(q.kind==='multi-text')draft.fields=q.acceptedTuples?.[0]||draft.fields.map(()=> 'teacher review');
   else if(q.kind==='rearrange')draft.tokens=q.tokens.map((_,i)=>i);
   else draft.value=q.accepted[0]||'teacher review';
   P.update(d,state,q.id,draft);P.check(d,state,q.id);
  }
  P.setMode(d,state,'ordered');P.go(d,state,target.id);const store=HTDualStore.open(d,state.student);if(store.status!=='empty')store.reset();store.save(state);
  return target;
 }''',target_id)
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'),args=['--no-sandbox']) # No autoplay bypass.
  def context(**kwargs):
   c=b.new_context(reduced_motion='reduce',**kwargs);c.add_init_script(SPY)
   c.route('**/*',lambda r:r.continue_() if r.request.url.startswith(BASE) else (external.append(r.request.url),r.abort())[-1]);c.route('**/sounds/*.wav',lambda r:r.fulfill(status=200,content_type='audio/wav',body='Invalid WAV: deliberate fallback fixture'));return c
  def page_for(c):
   page=c.new_page();page.set_default_timeout(12000);page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);page.on('response',lambda r:bad.append((r.status,r.url)) if r.status>=400 else None);return page
  # Every real launcher loads the same module and displays an accessible toggle.
  c=context(viewport={'width':1280,'height':900});page=page_for(c)
  for row in rows:
   data=open_game(page,row);assert log(page)['contexts']==0
   start(page);assert log(page)['contexts']==0
   answer_choice(page,data['questions'][0]);page.wait_for_function('soundLog.notes.length===2')
   assert log(page)['notes'][0]['frequency']<log(page)['notes'][1]['frequency']
   assert log(page)['contexts']==1
   # Each actual exam length (37/41/42/43) must trigger completion once.
   last=seed_completion(page);page.reload();expect(control(page,'#sound-toggle')).to_have_attribute('data-sound-state','ready');start(page);assert log(page)['contexts']==0
   answer_choice(page,last);page.wait_for_function('soundLog.notes.length===7');completion=log(page)['notes'][-5:];assert abs(completion[-1]['stop']-completion[0]['start']-1.51)<.001
   click(page,'#results-button');assert len(log(page)['notes'])==7
   page.reload();expect(control(page,'#sound-toggle')).to_have_attribute('data-sound-state','ready');start(page);assert log(page)['notes']==[]
  passed(f'{len(rows)}/{len(rows)} launchers load one shared module under /library/; no AudioContext before checking; each correct answer starts two ascending notes; every exam length completes once with the fanfare and stays quiet on restore')
  c.close()
  for label,options,touch in [
   ('desktop',{'viewport':{'width':1280,'height':900}},False),
   ('Android touch',{'viewport':{'width':390,'height':844},'is_mobile':True,'has_touch':True,'device_scale_factor':3},True),
   ('iPhone viewport/touch (Chromium)',{'viewport':{'width':375,'height':812},'is_mobile':True,'has_touch':True,'device_scale_factor':3,'user_agent':p.devices['iPhone 13']['user_agent']},True)
  ]:
   c=context(**options);page=page_for(c);data=open_game(page,TT)
   for width in [360,390,768,1280]:
    page.set_viewport_size({'width':width,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(label,width)
   page.set_viewport_size(options['viewport']);start(page,touch)
   click(page,'#check-answer',touch);assert log(page)['contexts']==0;expect(page.locator('#answer-error')).to_contain_text('đầy đủ')
   # Listen while checking; no sound service touches HTMLMediaElement.
   page.wait_for_function('document.querySelector("audio").readyState>=1');click(page,'#audio-toggle',touch);page.wait_for_function('!document.querySelector("audio").paused')
   media_before=log(page)['media'];media_settings=page.locator('audio').evaluate('e=>[e.currentSrc,e.volume,e.playbackRate]');time_before=page.locator('audio').evaluate('e=>e.currentTime')
   answer_choice(page,data['questions'][0],True,touch);page.wait_for_function('soundLog.notes.length===2')
   effect=log(page);assert effect['notes'][0]['frequency']>effect['notes'][1]['frequency'];assert max(effect['gains'])<=.025
   page.wait_for_timeout(450);assert not page.locator('audio').evaluate('e=>e.paused');assert page.locator('audio').evaluate('e=>e.currentTime')>time_before;assert log(page)['media']==media_before;assert page.locator('audio').evaluate('e=>[e.currentSrc,e.volume,e.playbackRate]')==media_settings
   n=len(log(page)['notes']);control(page,'#jump-question').select_option(page.locator('#question-card').get_attribute('data-question-id'));assert len(log(page)['notes'])==n
   # Old checked answers and disabled duplicate checks remain quiet.
   page.evaluate('document.querySelector("#check-answer").click()');assert len(log(page)['notes'])==n
   control(page,'#jump-question').select_option(data['questions'][1]['id']);answer_choice(page,data['questions'][1],False,touch)
   page.wait_for_function('(n)=>soundLog.notes.length===n+2',arg=n);n+=2
   assert log(page)['notes'][-2]['frequency']<log(page)['notes'][-1]['frequency'];expect(page.locator('#xp-total')).to_have_text('✦ 10 XP')
   key=page.evaluate('HTDualStore.keyFor(HT_PRACTICE_DATA,{name:"Sound Check",code:"8A"})');saved=page.evaluate('(k)=>localStorage.getItem(k)',key)
   click(page,'#sound-toggle',touch);expect(control(page,'#sound-toggle')).to_have_attribute('aria-pressed','false');assert page.evaluate('(k)=>localStorage.getItem(k)',key)==saved
   assert not page.locator('audio').evaluate('e=>e.paused')
   page.reload();expect(control(page,'#sound-toggle')).to_have_attribute('aria-pressed','false');start(page,touch);assert log(page)['contexts']==0
   control(page,'#jump-question').select_option(data['questions'][2]['id']);answer_choice(page,data['questions'][2],False,touch);assert log(page)['notes']==[];expect(page.locator('#xp-total')).to_have_text('✦ 20 XP')
   click(page,'#sound-toggle',touch);assert log(page)['contexts']==0
   control(page,'#jump-question').select_option(data['questions'][0]['id']);assert log(page)['notes']==[]
   click(page,'#results-button',touch);assert log(page)['notes']==[]
   # Complete exactly once after the last unanswered question, across reload/resume.
   page.close();page=page_for(c);open_game(page,TT);q=seed_completion(page);page.reload();expect(control(page,'#sound-toggle')).to_be_enabled();start(page,touch);assert log(page)['contexts']==0
   answer_choice(page,q,False,touch);page.wait_for_function('soundLog.notes.length===7');notes=log(page)['notes'];assert abs(notes[-1]['stop']-notes[-5]['start']-1.51)<.001
   click(page,'#results-button',touch);assert len(log(page)['notes'])==7
   page.reload();expect(control(page,'#sound-toggle')).to_be_enabled();start(page,touch);assert log(page)['notes']==[]
   click(page,'#home-button',touch);control(page,'#jump-question').select_option(page.locator('#question-card').get_attribute('data-question-id'));assert log(page)['notes']==[]
   # A new review attempt may get feedback, but never another completion fanfare/XP.
   click(page,'#results-button',touch);click(page,'#review-wrong',touch);q1=data['questions'][0];expect(page.locator('#question-card')).to_have_attribute('data-question-id',q1['id']);before_xp=page.locator('#xp-total').text_content()
   answer_choice(page,q1,False,touch);page.wait_for_function('soundLog.notes.length===2');expect(page.locator('#xp-total')).to_have_text(before_xp)
   page.screenshot(path=str(OUT/(re.sub('[^a-zA-Z]+','-',label)+'.png')),full_page=True)
   passed(label+': default autoplay policy, trusted clicks/taps, quiet restore/mode/old answer, mute remembered, Listening uninterrupted, once-only completion and review; XP unchanged')
   c.close()
  # Render actual PCM through production envelopes, then measure pitch/RMS/tail.
  c=context();page=page_for(c);open_game(page,TT)
  waveforms=page.evaluate('''async moduleURL=>{
   const {createGameSound,SOUND_CUES}=await import(moduleURL),out=[];
   for(const kind of ['correct','wrong','complete']){
    const duration=Math.max(...SOUND_CUES[kind].map(([o,,d])=>o+d)),rate=48000;
    const offline=new OfflineAudioContext(1,Math.ceil((duration+.05)*rate),rate);
    const sound=createGameSound({storage:()=>({getItem:()=>null}),audioContextClass:()=>function(){return {state:'running',currentTime:0,destination:offline.destination,createOscillator:()=>offline.createOscillator(),createGain:()=>offline.createGain()};}});
    await sound.playFeedback(kind==='complete'?'pending':kind,{event:{isTrusted:true},completed:kind==='complete'});
    const buffer=(await offline.startRendering()).getChannelData(0);
    const measured=SOUND_CUES[kind].map(([offset,hz,length])=>{
     const from=Math.ceil((offset+.035)*rate),to=Math.floor((offset+length-.065)*rate);let crossings=0,sum=0;
     for(let i=from;i<to;i++){sum+=buffer[i]*buffer[i];if(buffer[i]<=0&&buffer[i+1]>0)crossings++;}
     return {expectedHz:hz,measuredHz:crossings/((to-from)/rate),rms:Math.sqrt(sum/(to-from))};
    });
    const tail=buffer.slice(Math.ceil((duration+.025)*rate));out.push({kind,duration,peak:Math.max(...buffer.map(Math.abs)),measured,tailPeak:Math.max(...tail.map(Math.abs))});
   }return out;
  }''',MODULE)
  for wave in waveforms:
   assert wave['peak']<=.061 and wave['tailPeak']<.00001,wave
   for note in wave['measured']:assert abs(note['measuredHz']-note['expectedHz'])<20 and .025<note['rms']<.045,(wave,note)
  (OUT/'waveforms.json').write_text(json.dumps(waveforms,indent=2)+'\n')
  passed('OfflineAudioContext PCM: measured ascending/descending/fanfare pitches, 0.5/0.4/1.5s envelopes, peak below 0.061 and silent tails')
  c.close()
  # Preference synchronizes across games/tabs without changing student progress.
  c=context();a=page_for(c);open_game(a,TT);start(a);bpage=page_for(c);open_game(bpage,rows[1]);assert log(bpage)['contexts']==0
  click(a,'#sound-toggle');expect(control(bpage,'#sound-toggle')).to_have_attribute('aria-pressed','false')
  bpage.reload();expect(control(bpage,'#sound-toggle')).to_have_attribute('aria-pressed','false')
  click(bpage,'#sound-toggle');expect(a.locator('#sound-toggle')).to_have_attribute('aria-pressed','true');assert log(bpage)['contexts']==0
  c.close();passed('one preference is shared across games and live tabs; enabling never auto-plays')
  # Pending answers are silent; the final pending check gets only congratulations.
  c=context();page=page_for(c);hung=next(r for r in rows if r['school']=='THCS Trực Hùng');hung_data=open_game(page,hung)
  pending=next(q for q in hung_data['questions'] if not q['autoGrade'] and q['kind']=='text');start(page);control(page,'#jump-question').select_option(pending['id']);page.locator('#written-answer').fill('Giáo viên đối chiếu');click(page,'#check-answer');assert log(page)['contexts']==0;expect(page.locator('#xp-total')).to_have_text('✦ 0 XP')
  seed_completion(page,pending['id']);page.reload();expect(control(page,'#sound-toggle')).to_be_enabled();start(page);xp=page.locator('#xp-total').text_content();page.locator('#written-answer').fill('Giáo viên đối chiếu');click(page,'#check-answer');page.wait_for_function('soundLog.notes.length===5');expect(page.locator('#xp-total')).to_have_text(xp)
  c.close();passed('teacher-pending answers have no right/wrong cue or XP; a final pending answer triggers only the 1.5s fanfare')
  # No Web Audio support still leaves grading and progress fully functional.
  c=context();c.add_init_script('window.AudioContext=undefined;window.webkitAudioContext=undefined;');page=page_for(c);page.goto(BASE+'library/'+quote(TT['game']));expect(control(page,'#sound-toggle')).to_be_disabled();start(page);answer_choice(page,data['questions'][0]);expect(page.locator('#xp-total')).to_have_text('✦ 10 XP');c.close()
  passed('missing Web Audio support degrades to a disabled toggle while checking and XP still work')
  assert not errors,errors;assert not bad,bad;assert not external,external
  passed('zero JS/console errors, broken resources or external requests')
  (OUT/'report.json').write_text(json.dumps({'engine':'Chromium','physicalDevicesTested':False,'webkit':'not run by this Chromium suite','checks':checks,'waveforms':waveforms},ensure_ascii=False,indent=2)+'\n')
  b.close()
finally:server.shutdown()
