"""Real shared WAV decoding/playback: all Grade 6/7/8 games, fallback and Listening.
Phone testing uses Chromium touch emulation, not physical devices/Safari.
"""
from pathlib import Path
from urllib.parse import quote
import ast,functools,http.server,json,os,re,threading,importlib.util
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/tmp/ht-shared-wav-tests');OUT.mkdir(exist_ok=True)
old=(ROOT/'tests/dual-mode-sound-browser.py').read_text();tree=ast.parse(old)
exec('class Handler'+(ROOT/'tests/dual-mode-browser.py').read_text().split('class Handler',1)[1].split('server=http.server',1)[0])
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}/'
spec=importlib.util.spec_from_file_location('audit',ROOT/'tools/audit-grade8-sound-loading.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit);rows=[{**r,'game':r['html']} for r in audit.inventory()];rows += [{**r,'html':r['game']} for r in json.loads((ROOT/'docs/grade6-dual-mode/inventory.json').read_text())['games']];rows += [{**r,'html':r['game']} for r in json.loads((ROOT/'docs/grade7-dual-mode/inventory.json').read_text())['games']];TT=next(r for r in rows if 'truc-tuan' in r['html'])
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ['click','start','answer_choice','seed_completion']:exec(ast.get_source_segment(old,node))
choice_answer=answer_choice
def answer_choice(page,q,wrong=False,touch=False):
 if q['kind']=='choice':return choice_answer(page,q,wrong,touch)
 if q['kind']=='text':page.locator('#written-answer').fill('Incorrect answer for feedback' if wrong else q['accepted'][0])
 elif q['kind']=='multi-text':
  for i,value in enumerate(q['acceptedTuples'][0]):page.locator(f'#written-answer-{i}').fill('Incorrect' if wrong else value)
 else:raise AssertionError('WAV feedback fixture needs a verified source answer for '+q['id'])
 click(page,'#check-answer',touch)
SPY='''(()=>{
 const Native=window.AudioContext||window.webkitAudioContext;
 window.wavLog={contexts:0,wavs:[],notes:[],gains:[],media:[],stops:0};
 function Tracked(...args){const c=new Native(...args);wavLog.contexts++;
 const make=c.createBufferSource.bind(c);c.createBufferSource=()=>{const s=make(),start=s.start.bind(s),stop=s.stop.bind(s);s.start=t=>{wavLog.wavs.push({duration:s.buffer.duration,start:t});return start(t);};s.stop=t=>{wavLog.stops++;return stop(t);};return s;};
 const osc=c.createOscillator.bind(c);c.createOscillator=()=>{const s=osc(),start=s.start.bind(s);s.start=t=>{wavLog.notes.push(s.frequency.value);return start(t);};return s;};
 const gain=c.createGain.bind(c);c.createGain=()=>{const g=gain(),connect=g.connect.bind(g);g.connect=(...args)=>{wavLog.gains.push(g.gain.value);return connect(...args);};return g;};return c;}
 Tracked.prototype=Native.prototype;window.AudioContext=Tracked;
 for(const method of ['play','pause','load']){const original=HTMLMediaElement.prototype[method];HTMLMediaElement.prototype[method]=function(...args){wavLog.media.push(method);return original.apply(this,args);};}
})();'''
checks=[];errors=[];bad=[];responses=[]
def passed(s):checks.append(s);print('PASS '+s,flush=True)
def ready(page):expect(page.locator('#sound-toggle')).to_have_attribute('data-sound-state','ready');page.wait_for_timeout(100)
def count(page):return page.evaluate('wavLog.wavs.length')
def expect_wavs(page,kinds):
 page.wait_for_function('(n)=>wavLog.wavs.length===n',arg=len(kinds));log=page.evaluate('wavLog');durations={'correct':1.06093,'wrong':1.73887,'complete':3.54224}
 assert not log['notes'],log
 for event,kind in zip(log['wavs'],kinds):assert abs(event['duration']-durations[kind])<.002,(kind,event)
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for mobile in [False,True]:
   c=b.new_context(viewport={'width':390 if mobile else 1280,'height':844},is_mobile=mobile,has_touch=mobile,reduced_motion='reduce');c.add_init_script(SPY);page=c.new_page();page.set_default_timeout(12000)
   page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);page.on('response',lambda r:bad.append((r.status,r.url)) if r.status>=400 else responses.append(r.url))
   for row in rows:
    page.goto(BASE+'library/'+quote(row['html']));ready(page);assert page.evaluate('wavLog.contexts')==0
    data=page.evaluate('HT_PRACTICE_DATA');start(page,mobile);assert count(page)==0
    answer_choice(page,data['questions'][0],False,mobile);expect_wavs(page,['correct']);assert abs(page.evaluate('wavLog.gains[0]')-.7)<1e-6
    page.locator('#jump-question').select_option(data['questions'][1]['id']);answer_choice(page,data['questions'][1],True,mobile);expect_wavs(page,['correct','wrong']);expect(page.locator('#xp-total')).to_have_text('✦ 10 XP')
    page.locator('#play-mode').select_option('challenge');page.locator('#play-mode').select_option('ordered');page.evaluate('document.querySelector("#check-answer").click()');assert count(page)==2
    page.locator('#sound-toggle').click();expect(page.locator('#sound-toggle')).to_have_text('🔇 Âm thanh: Tắt');page.reload();ready(page);expect(page.locator('#sound-toggle')).to_have_text('🔇 Âm thanh: Tắt');start(page,mobile);assert count(page)==0;expect(page.locator('#xp-total')).to_have_text('✦ 10 XP')
    page.locator('#jump-question').select_option(data['questions'][2]['id']);answer_choice(page,data['questions'][2],False,mobile);assert count(page)==0;expect(page.locator('#xp-total')).to_have_text('✦ 20 XP');page.locator('#sound-toggle').click()
    last=seed_completion(page);page.reload();ready(page);start(page,mobile);assert count(page)==0;answer_choice(page,last,False,mobile);expect_wavs(page,['correct','complete']);log=page.evaluate('wavLog');assert log['wavs'][1]['start']>=log['wavs'][0]['start']+log['wavs'][0]['duration']+.079
    xp=page.locator('#xp-total').text_content();page.locator('#results-button').click();assert count(page)==2;page.reload();ready(page);start(page,mobile);assert count(page)==0;expect(page.locator('#xp-total')).to_have_text(xp)
   c.close();passed(f'{len(rows)}/{len(rows)} {"mobile touch emulation" if mobile else "desktop"}: native WAV correct/wrong/completion, 70% volume, quiet restore/review/mode, saved mute, unchanged XP, /library/ URLs')
  # Independent real listening + adjustable volume API without adding UI.
  c=b.new_context();c.add_init_script(SPY);page=c.new_page();page.goto(BASE+'library/'+quote(TT['game']));ready(page);data=page.evaluate('HT_PRACTICE_DATA');start(page);page.wait_for_function('document.querySelector("audio").readyState>=1');page.locator('#audio-toggle').click();page.wait_for_function('!document.querySelector("audio").paused');before=page.locator('audio').evaluate('e=>[e.currentSrc,e.volume,e.playbackRate,e.currentTime]');methods=page.evaluate('wavLog.media.slice()')
  answer_choice(page,data['questions'][0]);expect_wavs(page,['correct']);page.wait_for_timeout(250);after=page.locator('audio').evaluate('e=>[e.currentSrc,e.volume,e.playbackRate,e.currentTime]');assert before[:3]==after[:3] and after[3]>before[3] and page.evaluate('wavLog.media')==methods;assert abs(page.evaluate('wavLog.gains[0]')-.28)<1e-6
  page.evaluate('''async()=>{const m=await import('../shared-practice/dual-sound.js?v=20261026-sound-fix');window.testSound=m.createGameSound();testSound.setVolume(.35);window.reloadedSound=m.createGameSound();}''');assert page.evaluate('reloadedSound.volume')==.35
  # A real trusted button gesture invokes exported controller.
  page.evaluate('''()=>{const button=document.createElement('button');button.id='test-wav';button.textContent='Test volume';button.onclick=e=>testSound.playFeedback('wrong',{event:e});document.body.append(button);}''');page.locator('#test-wav').click();page.wait_for_function('wavLog.wavs.length===2');assert abs(page.evaluate('wavLog.gains.at(-1)')-.35)<1e-6
  page.locator('#sound-toggle').click();assert not page.locator('audio').evaluate('e=>e.paused');c.close();passed('Listening remains playing with unchanged media properties/method calls; ducked WAV gain; volume API persists separately')
  # Actual network/decode failures fallback; no delayed replay and mute cancels waits.
  for failure in ['404','corrupt','slow','decode-reject']:
   c=b.new_context();c.add_init_script(SPY);held=[]
   if failure=='decode-reject':c.add_init_script('const Native=AudioContext;window.AudioContext=function(...args){const c=new Native(...args);c.decodeAudioData=(bytes,ok,fail)=>fail(new Error("injected decode failure"));return c;};')
   def route(r):
    if failure=='404':r.fulfill(status=404,body='Missing test WAV')
    elif failure=='corrupt':r.fulfill(status=200,content_type='audio/wav',body='invalid WAV bytes')
    elif failure=='slow':held.append(r)
    else:r.continue_()
   c.route('**/sounds/*.wav',route);page=c.new_page();page.goto(BASE+'library/'+quote(TT['game']),wait_until='domcontentloaded');ready(page);data=page.evaluate('HT_PRACTICE_DATA');start(page);answer_choice(page,data['questions'][0]);page.wait_for_function('wavLog.notes.length===2');assert count(page)==0;expect(page.locator('#xp-total')).to_have_text('✦ 10 XP')
   if failure=='slow':
    for r in held:r.fulfill(status=200,content_type='audio/wav',body=(ROOT/'grade-8/De_thi_GHK1/shared-practice/sounds'/r.request.url.rsplit('/',1)[-1]).read_bytes())
    page.wait_for_timeout(400);assert count(page)==0 and page.evaluate('wavLog.notes.length')==2
   c.close();passed(f'{failure}: original Web Audio fallback, grading/XP continue, no late WAV replay')
  # A pending decode cannot replay after mute or navigation/cancellation.
  for cancel in ['mute','stop']:
   c=b.new_context();c.add_init_script(SPY);c.add_init_script('const N=AudioContext;window.AudioContext=function(...a){const c=new N(...a),d=c.decodeAudioData.bind(c);c.decodeAudioData=(bytes,ok,fail)=>setTimeout(()=>d(bytes,ok,fail),80);return c;};');page=c.new_page();page.goto(BASE+'library/'+quote(TT['game']));ready(page)
   page.evaluate('''async()=>{const m=await import('../shared-practice/dual-sound.js?v=20261026-sound-fix');window.s=m.createGameSound();const b=document.createElement('button');b.id='cancel-test';b.textContent='Cancel';b.onclick=e=>{s.playFeedback('correct',{event:e});setTimeout(()=>CANCEL,10);};document.body.append(b);}'''.replace('CANCEL','s.setEnabled(false)' if cancel=='mute' else 's.stop()'));page.locator('#cancel-test').click();page.wait_for_timeout(250);assert count(page)==0 and page.evaluate('wavLog.notes.length')==0;c.close();passed(cancel+' cancels pending WAV decoding without replay')
  assert not errors,errors;assert not bad,bad
  wav_urls=sorted(set(u.split('/library/',1)[1] for u in responses if '/sounds/' in u));assert len(wav_urls)==3,wav_urls
  passed('normal 49-game desktop/mobile run: no console/JS errors or HTTP failures; all 3 WAV URLs served under /library/')
  (OUT/'report.json').write_text(json.dumps({'checks':checks,'games':rows,'errors':errors,'bad':bad,'wavURLs':wav_urls,'physicalDevices':False},ensure_ascii=False,indent=2)+'\n');b.close()
finally:server.shutdown()
