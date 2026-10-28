from practice_browser_controls import control
"""Browser regression: real cached old JS, visible bootstrap, delayed/404 import,
retry with currentScript=null, and every on-disk Grade 8 dual launcher. No production IO.
Deliberately corrupt WAV bytes so the existing oscillator spy checks FALLBACK;
dual-mode-wav-browser.py checks native WAV playback for both grades.
"""
from pathlib import Path
from urllib.parse import quote,unquote,urlsplit
import ast,functools,http.server,io,json,os,re,shutil,subprocess,threading
from playwright.sync_api import sync_playwright,expect
import importlib.util
ROOT=Path(__file__).resolve().parents[1];OUT=Path(os.environ.get('SOUND_LOADING_OUTPUT','/tmp/ht-sound-loading-tests'));OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('audit',ROOT/'tools/audit-grade8-sound-loading.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit);rows=audit.inventory();TT=next(r for r in rows if 'truc-tuan' in r['html'])
shared='grade-8/De_thi_GHK1/shared-practice/dual-mode-engine.js'
old_engine=subprocess.check_output(['git','show','b38d578:'+shared],cwd=ROOT)
main_engine=subprocess.check_output(['git','show','7f4be94:'+shared],cwd=ROOT)
main_html=subprocess.check_output(['git','show','7f4be94:'+TT['html']],cwd=ROOT)
phase={'value':'fixed'};engine_requests=[]
# Share tested media range behavior, not another copy of game code.
exec('class Handler'+(ROOT/'tests/dual-mode-browser.py').read_text().split('class Handler',1)[1].split('server=http.server',1)[0])
class LoadingHandler(Handler):
 def send_head(self):
  self.remaining=None;url=urlsplit(self.path);resource=unquote(url.path).removeprefix('/library/');body=None
  if '/shared-practice/sounds/' in resource and resource.endswith('.wav'):
   body=b'Invalid WAV: deliberate bootstrap/fallback fixture';content_type='audio/wav';cache='no-store'
  elif resource==shared:
   engine_requests.append({'phase':phase['value'],'url':self.path})
   body=old_engine if phase['value']=='old' else main_engine if phase['value']=='main' else (ROOT/shared).read_bytes()
   content_type='text/javascript';cache='public, max-age=3600'
  elif resource==TT['html']:
   body=main_html if phase['value'] in ['old','main'] else (ROOT/TT['html']).read_bytes();content_type='text/html';cache='no-store'
  if body is None:return super().send_head()
  self.send_response(200);self.send_header('Content-Type',content_type);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control',cache);self.end_headers();return io.BytesIO(body)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(LoadingHandler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}/library/'
# Only extract the monitoring fixture; never execute the other suite on import.
spy=next(ast.literal_eval(n.value) for n in ast.parse((ROOT/'tests/dual-mode-sound-browser.py').read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SPY' for t in n.targets))
checks=[];observations={}
def passed(msg):checks.append(msg);print('PASS '+msg,flush=True)
def page_for(context):
 page=context.new_page();page.set_default_timeout(12000);record={'pageErrors':[],'consoleErrors':[],'bad':[],'external':[]}
 page.on('pageerror',lambda e:record['pageErrors'].append(str(e)));page.on('console',lambda m:record['consoleErrors'].append({'text':m.text,'url':m.location.get('url','')}) if m.type=='error' else None)
 page.on('response',lambda r:record['bad'].append({'status':r.status,'url':r.url}) if r.status>=400 else None)
 page.on('request',lambda r:record['external'].append(r.url) if not r.url.startswith(BASE.removesuffix('library/')) else None)
 return page,record

def clean(record,expected404=False):
 assert not record['pageErrors'],record;assert not record['external'],record
 if expected404:
  assert len(record['bad'])==1 and record['bad'][0]['status']==404 and '/dual-sound.js' in record['bad'][0]['url'],record
  assert all('/dual-sound.js' in r['url'] and '404' in r['text'] for r in record['consoleErrors']),record
 else:assert not record['bad'] and not record['consoleErrors'],record

def start(page,touch=False):
 page.locator('#student-name').fill('Kiểm tra tải âm thanh');
 if touch:page.locator('#start-form button').tap()
 else:page.locator('#start-form button').click()
 if page.locator('#resume-panel').is_visible():page.locator('#resume-button').click()
def check(page,q,wrong=False,touch=False):
 control(page,'#jump-question').select_option(q['id'])
 value=next(o['value'] for o in q['options'] if o['value'] not in q['accepted']) if wrong else q['accepted'][0]
 if touch:page.locator(f'#answer-area input[value="{value}"]').tap();page.locator('#check-answer').tap()
 else:page.locator(f'#answer-area input[value="{value}"]').check();page.locator('#check-answer').click()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'),args=['--no-sandbox'])
  # Real HTTP cache: DO NOT register Playwright routes (routes disable caching).
  context=browser.new_context();page,record=page_for(context);url=BASE+quote(TT['html'])
  phase['value']='old';page.goto(url+'?html=old');assert control(page,'#sound-toggle').count()==0;count=len(engine_requests)
  phase['value']='main';page.goto(url+'?html=fresh-main');assert control(page,'#sound-toggle').count()==0;assert len(engine_requests)==count
  observations['staleEngine']={'oldButtonCount':0,'freshMainHtmlButtonCount':0,'newEngineRequests':0}
  phase['value']='fixed';page.goto(url+'?html=fixed');expect(control(page,'#sound-toggle')).to_have_attribute('data-sound-state','ready');expect(control(page,'#sound-toggle')).to_have_count(1)
  assert len(engine_requests)==count+1 and '?v=20261026-sound-fix' in engine_requests[-1]['url'];clean(record);context.close()
  passed('reproduced missing toggle with a genuinely cached pre-sound engine; fixed HTML fetches the versioned engine and restores one ready toggle')
  # Every real file was discovered on disk, not assumed from an old inventory.
  for touch in [False,True]:
   context=browser.new_context(viewport={'width':390 if touch else 1280,'height':844},has_touch=touch,is_mobile=touch,reduced_motion='reduce');context.add_init_script(spy);page,record=page_for(context)
   for row in rows:
    assert row['staticSoundButtons']==1,row;page.goto(BASE+quote(row['html']));expect(control(page,'#sound-toggle')).to_have_attribute('data-sound-state','ready');expect(control(page,'#sound-toggle')).to_have_count(1)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),row
    data=page.evaluate('HT_PRACTICE_DATA');start(page,touch);check(page,data['questions'][0],touch=touch);page.wait_for_function('soundLog.notes.length===2')
    check(page,data['questions'][1],wrong=True,touch=touch);page.wait_for_function('soundLog.notes.length===4')
    notes=page.evaluate('soundLog.notes');assert notes[0]['frequency']<notes[1]['frequency'] and notes[2]['frequency']>notes[3]['frequency'];expect(page.locator('#xp-total')).to_have_text('✦ 10 XP')
    control(page,'#jump-question').select_option(page.locator('#question-card').get_attribute('data-question-id'));assert len(page.evaluate('soundLog.notes'))==4
    control(page,'#sound-toggle').click();expect(control(page,'#sound-toggle')).to_have_text('🔇 Âm thanh: Tắt')
    page.reload();expect(control(page,'#sound-toggle')).to_have_attribute('data-sound-state','ready');expect(control(page,'#sound-toggle')).to_have_text('🔇 Âm thanh: Tắt');assert page.evaluate('soundLog.notes.length')==0
    start(page,touch);expect(page.locator('#xp-total')).to_have_text('✦ 10 XP');control(page,'#sound-toggle').click();expect(control(page,'#sound-toggle')).to_have_text('🔊 Âm thanh: Bật')
   clean(record);context.close();passed(f'{len(rows)}/{len(rows)} real games on '+('mobile touch' if touch else 'desktop')+': one ready toggle, correct/wrong sounds, navigation stays quiet, mute persists, resume keeps XP, no Console/404')
  # Static button is already visible even if the controller has not arrived.
  context=browser.new_context();held=[];context.route('**/dual-mode-engine.js*',lambda r:held.append(r));page,record=page_for(context)
  page.goto(url,wait_until='commit');expect(control(page,'#sound-toggle')).to_be_visible();expect(control(page,'#sound-toggle')).to_have_attribute('data-sound-state','loading');page.wait_for_function('!!window.HTDualStore');assert held
  held.pop().fulfill(content_type='text/javascript',body=(ROOT/shared).read_text());expect(control(page,'#sound-toggle')).to_have_attribute('data-sound-state','ready');expect(control(page,'#sound-toggle')).to_have_count(1);clean(record);context.close()
  passed('static toggle is visible before the shared controller downloads; controller reuses it without a duplicate')
  # Slow sound module does not hide the button or hold up the exam/XP.
  context=browser.new_context();context.add_init_script(spy);held=[];context.route('**/dual-sound.js*',lambda r:held.append(r));page,record=page_for(context)
  page.goto(url,wait_until='domcontentloaded');expect(control(page,'#sound-toggle')).to_be_visible();expect(control(page,'#sound-toggle')).to_have_attribute('data-sound-state','loading');start(page);data=page.evaluate('HT_PRACTICE_DATA');check(page,data['questions'][0]);expect(page.locator('#xp-total')).to_have_text('✦ 10 XP');assert page.evaluate('soundLog.notes.length')==0
  assert held;held.pop().fulfill(content_type='text/javascript',body=(ROOT/'grade-8/De_thi_GHK1/shared-practice/dual-sound.js').read_text());expect(control(page,'#sound-toggle')).to_have_attribute('data-sound-state','ready');assert page.evaluate('soundLog.notes.length')==0
  check(page,data['questions'][1]);page.wait_for_function('soundLog.notes.length===2');clean(record);context.close()
  passed('delayed import leaves a visible busy toggle and working XP; readiness never replays the earlier answer')
  # A real failed module request has an explicit state and can be retried later,
  # when document.currentScript is null; it never aborts the game controller.
  context=browser.new_context();context.add_init_script(spy)
  def fail_once(route):
   if 'retry=' in route.request.url:route.continue_()
   else:route.fulfill(status=404,content_type='text/javascript',body='Module unavailable in fault-injection fixture')
  context.route('**/dual-sound.js*',fail_once);page,record=page_for(context);page.goto(url);expect(control(page,'#sound-toggle')).to_have_attribute('data-sound-state','error');expect(control(page,'#sound-toggle')).to_be_visible();expect(control(page,'#sound-toggle')).to_have_text('⚠ Âm thanh: Lỗi tải')
  start(page);data=page.evaluate('HT_PRACTICE_DATA');check(page,data['questions'][0]);expect(page.locator('#xp-total')).to_have_text('✦ 10 XP');assert page.evaluate('document.currentScript===null');control(page,'#sound-toggle').click();expect(control(page,'#sound-toggle')).to_have_attribute('data-sound-state','ready');assert page.evaluate('soundLog.notes.length')==0
  check(page,data['questions'][1]);page.wait_for_function('soundLog.notes.length===2');clean(record,expected404=True);context.close()
  passed('injected 404 shows an error/retry toggle, grading remains usable, retry captures the right URL with currentScript null and emits no late answer')
  # A late response after the timeout cannot silently replace the error state.
  context=browser.new_context();held=[]
  def slow_first(route):
   if 'retry=' in route.request.url:route.continue_()
   else:held.append(route)
  context.route('**/dual-sound.js*',slow_first);page,record=page_for(context);page.clock.install();page.goto(url,wait_until='domcontentloaded');expect(control(page,'#sound-toggle')).to_have_attribute('data-sound-state','loading')
  page.clock.fast_forward(10001);expect(control(page,'#sound-toggle')).to_have_attribute('data-sound-state','error');assert held
  held.pop().fulfill(content_type='text/javascript',body=(ROOT/'grade-8/De_thi_GHK1/shared-practice/dual-sound.js').read_text());page.wait_for_load_state('networkidle');expect(control(page,'#sound-toggle')).to_have_attribute('data-sound-state','error')
  control(page,'#sound-toggle').click();expect(control(page,'#sound-toggle')).to_have_attribute('data-sound-state','ready');clean(record);context.close()
  passed('timeout leaves a visible retry state; a late import cannot overwrite it; explicit retry succeeds')
  # Also support a null currentScript at initialization (module-style execution).
  context=browser.new_context();context.add_init_script(spy)
  def as_module(route):
   body=(ROOT/TT['html']).read_text().replace('<script defer src="../shared-practice/dual-mode-engine.js','<script type="module" src="../shared-practice/dual-mode-engine.js');route.fulfill(content_type='text/html',body=body)
  context.route('**/truc-tuan-dual-mode.html',as_module);page,record=page_for(context);page.goto(url);expect(control(page,'#sound-toggle')).to_have_attribute('data-sound-state','ready');start(page);check(page,page.evaluate('HT_PRACTICE_DATA.questions[0]'));page.wait_for_function('soundLog.notes.length===2');clean(record);context.close()
  passed('module-style initialization with currentScript=null resolves the existing script URL and plays sound without JavaScript errors')
  context=browser.new_context();context.add_init_script(spy);context.add_init_script("Object.defineProperty(document,'currentScript',{get:()=>({src:'data:text/javascript,invalid-base'})});");page,record=page_for(context);page.goto(url);expect(control(page,'#sound-toggle')).to_have_attribute('data-sound-state','error')
  start(page);check(page,page.evaluate('HT_PRACTICE_DATA.questions[0]'));expect(page.locator('#xp-total')).to_have_text('✦ 10 XP');assert page.evaluate('soundLog.notes.length')==0;clean(record);context.close()
  passed('unresolvable script URL reports a visible loader error and leaves grading/XP usable')
  report={'gamesFound':len(rows),'games':rows,'checks':checks,'observations':observations,'physicalPhoneTested':False,'browser':'Chromium desktop and mobile touch emulation','publicWebsiteTested':False}
  (OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');browser.close()
finally:server.shutdown();server.server_close()
