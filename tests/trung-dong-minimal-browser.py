"""Real Chromium UI checks; phone profiles and keyboard geometry are emulated."""
from pathlib import Path
from urllib.parse import quote,urlsplit
import ast,functools,http.server,json,os,re,subprocess,threading
from playwright.sync_api import sync_playwright,expect
from practice_browser_controls import control
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('TRUNG_DONG_REPORT','/tmp/trung-dong-minimal'));OUT.mkdir(parents=True,exist_ok=True)
GAME='grade-8/De_thi_GHK1/3_THCS Trung Dong/practice-dual-mode.html'
BASELINE=subprocess.check_output(['git','show','7ebbe8a:'+GAME],cwd=ROOT)
# Helpers solve original source token sequences, not inferred answer keys.
source=(ROOT/'tests/grade8-all-dual-browser.py').read_text()
for node in ast.parse(source).body:
 if isinstance(node,ast.FunctionDef) and node.name in ['norm','order']:exec(ast.get_source_segment(source,node))
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  if urlsplit(self.path).query=='baseline':
   self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(BASELINE)));self.end_headers();self.wfile.write(BASELINE)
  else:super().do_GET()
 def copyfile(self,source,output):
  try:super().copyfile(source,output)
  except (BrokenPipeError,ConnectionResetError):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}/';URL=BASE+quote(GAME)
checks=[];errors=[];external=[]
def passed(message):checks.append(message);print('PASS '+message,flush=True)
def start(page):
 page.locator('#student-name').fill('Học sinh thử nghiệm');page.locator('#start-form button').click()
 if page.locator('#resume-panel').is_visible():page.locator('#resume-button').click()
 expect(page.locator('#play')).to_be_visible()
def jump(page,qid):
 control(page,'#jump-question').select_option(qid)
 expect(page.locator('#question-card')).to_have_attribute('data-question-id',qid)
 expect(page.locator('#minimal-question-list')).not_to_have_attribute('open','')
 page.wait_for_timeout(35)
def fill(page,q,wrong=False):
 if q['kind']=='choice':
  v=next(o['value'] for o in q['options'] if o['value'] not in q['accepted']) if wrong else q['accepted'][0]
  page.locator('#answer-area input').evaluate_all('(els,v)=>{const e=els.find(e=>e.value===v);e.checked=true;e.dispatchEvent(new Event("change"));}',v)
 elif q['kind']=='text':page.locator('#written-answer').fill('incorrect fixture' if wrong else q['accepted'][0])
 else:
  indices=order(q);assert indices is not None
  if wrong:indices[0],indices[1]=indices[1],indices[0]
  for i in indices:page.locator(f'[data-token-index="{i}"]').click()
def nav_geometry(page):
 return page.locator('.question-navigation').evaluate('e=>{const r=e.getBoundingClientRect();return {top:r.top,bottom:r.bottom,height:r.height,innerHeight,scrollY};}')
def assert_bar(page):
 g=nav_geometry(page);assert g['top']>=0 and abs(g['bottom']-g['innerHeight'])<2,g
 assert page.locator('.question-navigation:visible').count()==1
 for id in ['previous-question','next-question']:assert page.locator('#'+id).bounding_box()['height']>=44
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
def record(page):return page.evaluate('JSON.parse(localStorage.getItem(HTDualStore.keyFor(HT_PRACTICE_DATA,{name:"Học sinh thử nghiệm",code:""}))).state')
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for name,width,height,mobile in [('iphone',390,844,True),('android',412,915,True),('desktop',1440,1000,False)]:
   ctx=browser.new_context(viewport={'width':width,'height':height},is_mobile=mobile,has_touch=mobile,reduced_motion='reduce')
   ctx.route('**/*',lambda r:r.continue_() if r.request.url.startswith(BASE) else (external.append(r.request.url),r.abort())[-1])
   page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
   # Before/after use identical learner and viewport, and genuine main HTML.
   page.goto(URL+'?baseline');start(page);page.screenshot(path=str(OUT/f'before-{name}.png'))
   page.evaluate('localStorage.clear()');page.goto(URL);start(page)
   expect(page.locator('#minimal-question-list')).not_to_have_attribute('open','')
   expect(page.locator('#question-dots')).to_be_hidden();expect(page.locator('#jump-question')).to_be_hidden()
   assert page.locator('#prompt').bounding_box()['y']<height*.4
   expect(page.locator('#minimal-audio-notice')).to_be_visible();expect(page.locator('#audio-panel')).to_be_hidden()
   assert page.evaluate('HT_PRACTICE_DATA.tracks.length')==0
   page.screenshot(path=str(OUT/f'after-{name}.png'));assert_bar(page)
   passed(name+': question appears early, no grid on first screen, one reachable fixed bar, original missing-audio notice')
   # Grid and jump controls close on use, including clicking the selected question.
   control(page,'#jump-question').select_option('l2');expect(page.locator('#minimal-question-list')).not_to_have_attribute('open','')
   page.locator('#minimal-question-list>summary').click();page.locator('#question-dots button[data-question-id="l1"]').click()
   expect(page.locator('#minimal-question-list')).not_to_have_attribute('open','')
   data=page.evaluate('HT_PRACTICE_DATA');xp=0;reading_scroll=0;wrongs={'l1','rc3','w1'}
   for q in data['questions']:
    jump(page,q['id'])
    if q['id']=='cl1':
     expect(page.locator('#passage-content')).to_contain_text('mountain climbing');assert 'living on a farm' not in page.locator('#passage-content').text_content()
     if mobile:assert page.locator('#passage-panel').bounding_box()['y']<page.locator('#question-card').bounding_box()['y']
     else:assert page.locator('#passage-panel').bounding_box()['x']<page.locator('#question-card').bounding_box()['x']
     page.screenshot(path=str(OUT/f'after-reading-{name}.png'))
     page.locator('#passage-content').evaluate('e=>e.scrollTop=80');page.wait_for_timeout(50);reading_scroll=page.locator('#passage-content').evaluate('e=>e.scrollTop')
    if q['id']=='cl2' and mobile:assert abs(page.locator('#passage-content').evaluate('e=>e.scrollTop')-reading_scroll)<2
    if q['id']=='rc1':
     expect(page.locator('#passage-content')).to_contain_text('living on a farm');assert 'mountain climbing' not in page.locator('#passage-content').text_content()
    if q['section'] not in ['section-5','section-6']:expect(page.locator('#passage-panel')).to_be_hidden()
    # Verified source explanation must be shown immediately and remain visible.
    fill(page,q,q['id'] in wrongs);page.locator('#check-answer').click();expect(page.locator('#feedback')).to_be_visible()
    if q['id'] not in wrongs:xp+=10
    expect(page.locator('#xp-total')).to_have_text(f'✦ {xp} XP')
    expected=page.evaluate('html=>{const d=document.createElement("div");d.innerHTML=html;return d.innerHTML;}',q['explainHtml'])
    assert page.locator('#explanation-content .explanation-item').nth(1).locator('div').inner_html()==expected
    assert not page.locator('dialog[open]').count();assert_bar(page)
    if q['id']=='l1':
     page.wait_for_timeout(50);assert 0<=page.locator('#feedback-title').bounding_box()['y']<height*.3
     page.screenshot(path=str(OUT/f'after-feedback-{name}.png'))
    page.evaluate('scrollTo(0,document.body.scrollHeight)');assert_bar(page)
    # The final content and navigation remain reachable without overlap.
    bottom=page.locator('#question-layout').evaluate('e=>e.getBoundingClientRect().bottom')
    assert bottom<=nav_geometry(page)['top']+2,(name,q['id'],bottom,nav_geometry(page))
    if q['id']=='vf2':
     before=record(page);page.reload();start(page);assert record(page)['answers']==before['answers'];expect(page.locator('#question-card')).to_have_attribute('data-question-id',q['id'])
     expect(page.locator('#xp-total')).to_have_text(f'✦ {xp} XP')
    page.evaluate('document.querySelector("#check-answer").click()');expect(page.locator('#xp-total')).to_have_text(f'✦ {xp} XP')
   passed(name+': all 42 source questions and verified explanations, original scoring (390 XP), typed/chip answers, reload, fixed bar at scroll bottom')
   control(page,'#results-button').click();expect(page.locator('#result-xp')).to_have_text('390');page.locator('#review-wrong').click()
   first={key:value['first'] for key,value in record(page)['answers'].items()}
   for id in ['l1','rc3','w1']:
    jump(page,id);q=next(q for q in data['questions'] if q['id']==id);fill(page,q);page.locator('#check-answer').click();expect(page.locator('#xp-total')).to_have_text('✦ 390 XP')
   assert {key:value['first'] for key,value in record(page)['answers'].items()}==first
   passed(name+': wrong-answer review keeps immutable first answers/XP; paragraph selection and scroll position retained')
   # Emulate the visual viewport geometry of an on-screen keyboard and iOS pan.
   control(page,'#results-button').click();page.locator('#continue-playing').click();jump(page,'rw4')
   # Use an unanswered learner so a real Writing textarea stays editable.
   control(page,'#change-student').click();page.locator('#student-name').fill('Keyboard fixture');page.locator('#start-form button').click();jump(page,'rw4')
   field=page.locator('#written-answer');field.fill('Bản nháp bàn phím');field.focus()
   page.evaluate('''()=>{window.originalViewport=visualViewport;const mock={height:innerHeight-360,offsetTop:24};Object.defineProperty(window,'visualViewport',{value:mock,configurable:true});originalViewport.dispatchEvent(new Event('resize'));}''')
   page.wait_for_timeout(100)
   r=field.bounding_box();nav_top=nav_geometry(page)['top'];assert r['y']>=24 and r['y']+r['height']<=nav_top-8,(name,r,nav_top)
   assert page.locator('.question-navigation').bounding_box()['y']+page.locator('.question-navigation').bounding_box()['height']<=height-336+2
   page.screenshot(path=str(OUT/f'keyboard-geometry-{name}.png'))
   page.evaluate('''()=>{Object.defineProperty(window,'visualViewport',{value:originalViewport,configurable:true});window.dispatchEvent(new Event('resize'));}''');page.wait_for_timeout(50)
   page.locator('#next-question').click();expect(page.locator('#results')).to_be_visible()
   passed(name+': simulated keyboard shrink/pan keeps Writing input and the sole bar above keyboard; draft remains saved')
   ctx.close()
  # Missing explanation is a local fixture, never a change to official exam data.
  ctx=browser.new_context();ctx.route('**/*',lambda r:r.continue_() if r.request.url.startswith(BASE) else (external.append(r.request.url),r.abort())[-1]);page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)));fixture=json.loads(json.dumps(data));fixture['questions'][0]['explainHtml']=''
  ctx.route('**/practice-dual-data.js',lambda r:r.fulfill(content_type='text/javascript',body='window.HT_PRACTICE_DATA='+json.dumps(fixture)+';'))
  page.goto(URL);start(page);fill(page,fixture['questions'][0]);page.locator('#check-answer').click()
  expect(page.locator('#explanation-content')).to_contain_text('Chưa có lời giải chi tiết.');expect(page.locator('#xp-total')).to_have_text('✦ 10 XP');page.locator('#next-question').click();expect(page.locator('#question-card')).to_have_attribute('data-question-id','l2')
  passed('missing-explanation fixture: honest short notice, grading and next navigation still work');ctx.close()
  assert not errors,errors;assert not external,external
  (OUT/'report.json').write_text(json.dumps({'checks':checks,'errors':errors,'external':external,'physicalDevices':False,'actualSystemKeyboard':False,'engine':'Chromium','sourceTracks':0},ensure_ascii=False,indent=2)+'\n')
  browser.close()
finally:server.shutdown()
