from practice_browser_controls import control,assert_context
"""Real Chromium: 42 Truc Tuan questions, modes, persistence, profiles and local media."""
from pathlib import Path
import functools,hashlib,http.server,json,os,re,shutil,threading,subprocess,sys,tempfile
from urllib.parse import quote,unquote
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('DUAL_MODE_TEST_OUTPUT','/tmp/ht-dual-mode-tests'));OUT.mkdir(parents=True,exist_ok=True)
FOLDER=ROOT/'grade-8/De_thi_GHK1/1_THCS Truc Tuan'
data=json.loads((FOLDER/'truc-tuan-dual-data.js').read_text().split('window.HT_PRACTICE_DATA = ',1)[1].strip()[:-1])
def norm(s):return re.sub(r'\s+',' ',re.sub(r'[.,!?;:]','',s.lower().replace('’',"'").replace('‘',"'"))).strip()
def order(q):
 words=norm(q['accepted'][0]).split()
 def solve(indices,left):
  if len(indices)==len(q['tokens']):return indices if not left else None
  for i,token in enumerate(q['tokens']):
   part=norm(token).split()
   if i not in indices and left[:len(part)]==part:
    found=solve(indices+[i],left[len(part):])
    if found is not None:return found
  return None
 return solve([],words)
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def translate_path(self,path):
  if path.startswith('/library/'):path=path[len('/library'):]
  return super().translate_path(path)
 def copyfile(self,source,output):
  try:
   remaining=getattr(self,'remaining',None)
   if remaining is None:super().copyfile(source,output)
   else:
    while remaining>0:
     chunk=source.read(min(remaining,65536))
     if not chunk:break
     output.write(chunk);remaining-=len(chunk)
  except (BrokenPipeError,ConnectionResetError):pass
 def send_head(self):
  self.remaining=None;target=Path(self.translate_path(self.path))
  if target.suffix.lower()!='.mp3' or not target.is_file():return super().send_head()
  size=target.stat().st_size;m=re.fullmatch(r'bytes=(\d+)-(\d*)',self.headers.get('Range',''))
  start=int(m[1]) if m else 0;end=min(int(m[2]) if m and m[2] else size-1,size-1)
  if start>=size or end<start:self.send_error(416);return None
  self.send_response(206 if m else 200);self.send_header('Content-Type','audio/mpeg');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1))
  if m:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  self.end_headers();stream=target.open('rb');stream.seek(start);self.remaining=end-start+1;return stream
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}/'
URL=BASE+'library/'+quote(str(FOLDER.relative_to(ROOT)))+'/truc-tuan-dual-mode.html'
errors=[];external=[];checks=[];skipped=[]
def passed(message):checks.append(message);print('PASS '+message,flush=True)
def start(page,name='Học sinh A',code='8A-01',mode='ordered',resume=True):
 page.locator('#student-name').fill(name)
 if not page.locator('#student-code').is_visible():page.locator('.identity-options summary').click()
 page.locator('#student-code').fill(code)
 page.locator('#start-form button').click()
 if resume and page.locator('#resume-panel').is_visible():page.locator('#resume-button').click()
def go(page,qid):control(page,'#jump-question').select_option(qid)
def fill(page,q,wrong=False):
 if q['kind']=='choice':
  value=next(o['value'] for o in q['options'] if o['value'] not in q['accepted']) if wrong else q['accepted'][0]
  page.locator(f'#answer-area input[value="{value}"]').check()
 elif q['kind']=='text':page.locator('#written-answer').fill('not '+q['accepted'][0] if wrong else q['accepted'][0])
 else:
  tokens=order(q);assert tokens is not None,q['id']
  if wrong:tokens[0],tokens[1]=tokens[1],tokens[0]
  for i in tokens:page.locator(f'#word-bank button[data-token-index="{i}"]').click()
def records(page):return page.evaluate('Object.fromEntries(Object.entries(localStorage).filter(([k])=>k.startsWith("htenglish:practice:v1:")))')
def current_record(page,name='Học sinh A',code='8A-01'):
 return page.evaluate('''([name,code])=>JSON.parse(localStorage.getItem(HTDualStore.keyFor(HT_PRACTICE_DATA,{name,code})))''',[name,code])
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'),args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
  def route(r):
   if r.request.url.startswith(BASE):r.continue_()
   else:external.append(r.request.url);r.abort()
  def page_for(context):
   page=context.new_page();page.set_default_timeout(12000)
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
   page.goto(URL);return page
  context=browser.new_context(viewport={'width':1280,'height':900},reduced_motion='reduce');context.route('**/*',route)
  page=page_for(context);expect(page.locator('#welcome')).to_be_visible()
  assert len(records(page))==0
  page.locator('#start-form button').click();expect(page.locator('#name-error')).to_contain_text('họ tên')
  for width in [360,390,768,820,1280]:
   page.set_viewport_size({'width':width,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),width
  page.screenshot(path=str(OUT/'welcome.png'),full_page=True)
  start(page);expect(page.locator('#play')).to_be_visible();expect(page.locator('#question-position')).to_have_text('Câu 1 / 42')
  expect(page.locator('#question-dots button')).to_have_count(42)
  page.locator('#check-answer').click();expect(page.locator('#answer-error')).to_contain_text('đầy đủ')
  assert current_record(page)['state']['answers']['q1']['first'] is None
  passed('welcome/name confirmation, no writes before starting, 42-question ordered mode and responsive welcome')
  xp=0;wrongs={'q1','q31','q36'}
  for q in data['questions']:
   expect(page.locator('#question-card')).to_have_attribute('data-question-id',q['id'])
   expect(page.locator('#question-position')).to_have_text(f'Câu {q["number"]} / 42')
   if q['kind']=='choice':assert page.locator('#answer-area input').evaluate_all('(els)=>els.map(e=>e.value)')==[o['value'] for o in q['options']]
   assert_context(page,q,data)
   expect(page.locator('#transcript-panel')).to_be_hidden()
   assert page.locator('#transcript-content').inner_html()==''
   if q['id'] in ['q1','q7']:
    track=data['tracks'][0 if q['id']=='q1' else 1]
    page.wait_for_function('document.querySelector("audio").readyState>=1')
    assert unquote(page.locator('audio').evaluate('e=>new URL(e.currentSrc).pathname')).endswith(track['src'])
    page.locator('#audio-toggle').click();page.wait_for_function('!document.querySelector("audio").paused')
    page.locator('#audio-toggle').click();assert page.locator('audio').evaluate('e=>e.paused')
    page.locator('audio').evaluate('e=>e.currentTime=10');page.locator('#audio-forward').click();assert abs(page.locator('audio').evaluate('e=>e.currentTime')-15)<1
    page.locator('#audio-back').click();assert abs(page.locator('audio').evaluate('e=>e.currentTime')-10)<1
    for speed in ['0.75','1.25','1']:
     page.locator('#audio-speed').select_option(speed);assert page.locator('audio').evaluate('e=>e.playbackRate')==float(speed)
    page.locator('#audio-seek').evaluate('e=>{e.value=25;e.dispatchEvent(new Event("input",{bubbles:true}));}')
    assert abs(page.locator('audio').evaluate('e=>e.currentTime/e.duration')-.25)<.02
   if q['id']=='q23':
    page.locator('#written-answer').fill('bản nháp trước khi tải lại')
    control(page,'#results-button').click();page.locator('#continue-playing').click()
    expect(page.locator('#written-answer')).to_have_value('bản nháp trước khi tải lại')
    page.reload();start(page)
    expect(page.locator('#written-answer')).to_have_value('bản nháp trước khi tải lại')
    expect(page.locator('#question-position')).to_have_text('Câu 23 / 42')
   if q['id']=='q36':
    for i in [0,3]:page.locator(f'#word-bank button[data-token-index="{i}"]').click()
    control(page,'#results-button').click();page.locator('#continue-playing').click()
    expect(page.locator('#word-target button')).to_have_count(2)
    page.reload();start(page);expect(page.locator('#word-target button')).to_have_count(2)
    page.locator('#undo-word').click();expect(page.locator('#word-target button')).to_have_count(1)
    page.locator('#reset-words').click();expect(page.locator('#word-target button')).to_have_count(0)
   fill(page,q,q['id'] in wrongs);page.locator('#check-answer').click()
   if q['id'] not in wrongs:xp+=10
   expect(page.locator('#xp-total')).to_have_text(f'✦ {xp} XP')
   page.evaluate('document.querySelector("#check-answer").dispatchEvent(new MouseEvent("click"))')
   expect(page.locator('#xp-total')).to_have_text(f'✦ {xp} XP')
   if q.get('track'):expect(page.locator('#transcript-panel')).to_be_visible()
   if q['id'] in ['q1','q13','q31','q36']:
    before=records(page);first=current_record(page)['state']['answers'][q['id']]['first']
    control(page,'#results-button').click()
    page.locator('#continue-playing').click()
    expect(page.locator('#question-card')).to_have_attribute('data-question-id',q['id'])
    expect(page.locator('#xp-total')).to_have_text(f'✦ {xp} XP')
    assert current_record(page)['state']['answers'][q['id']]['first']==first
   page.locator('#next-question').click()
  expect(page.locator('#results')).to_be_visible()
  for key,value in [('total',42),('xp',390),('correct',39),('wrong',3),('unanswered',0),('pending',0)]:expect(page.locator('#result-'+key)).to_have_text(str(value))
  expect(page.locator('#review-list button')).to_have_count(3)
  passed('ALL 42 questions played in original order, all four source sections/types, exact contexts/options, real two-track audio/seek/speeds/transcript gating, navigation and XP exactly once (390 XP)')
  firsts={k:v['first'] for k,v in current_record(page)['state']['answers'].items()}
  page.locator('#review-wrong').click()
  for q in [q for q in data['questions'] if q['id'] in wrongs]:
   expect(page.locator('#question-card')).to_have_attribute('data-question-id',q['id'])
   if q['id']=='q31':
    page.locator('#written-answer').fill('nháp ôn lại');page.reload();start(page)
    expect(page.locator('#written-answer')).to_have_value('nháp ôn lại')
   fill(page,q);page.locator('#check-answer').click();expect(page.locator('#xp-total')).to_have_text('✦ 390 XP');page.locator('#next-question').click()
  expect(page.locator('#review-summary')).to_contain_text('3 câu đã làm đúng')
  assert {k:v['first'] for k,v in current_record(page)['state']['answers'].items()}==firsts
  page.reload();start(page);expect(page.locator('#xp-total')).to_have_text('✦ 390 XP')
  passed('typed and builder drafts persist; reload restores ordered and review positions; wrong choice/text/builder review never changes first attempts or XP')
  control(page,'#change-student').click();expect(page.locator('#student-name')).to_have_value('')
  start(page,'Học sinh B','8A-02','challenge');expect(page.locator('#play')).to_be_visible()
  expect(page.locator('#question-position')).to_have_text('Câu 1 / 42')
  fill(page,data['questions'][0]);page.locator('#check-answer').click()
  expect(page.locator('#xp-total')).to_have_text('✦ 10 XP')
  control(page,'#change-student').click();start(page,'Học sinh A','8A-99','challenge');expect(page.locator('#question-position')).to_have_text('Câu 1 / 42')
  control(page,'#change-student').click();start(page);expect(page.locator('#xp-total')).to_have_text('✦ 390 XP')
  passed('different learners and same-name learners with distinct codes keep independent progress without listing other profiles')
  control(page,'#change-student').click();start(page,'Học sinh B','8A-02',resume=False)
  page.locator('#restart-saved').click();expect(page.locator('#restart-dialog')).to_be_visible();page.locator('#cancel-restart').click()
  assert current_record(page,'Học sinh B','8A-02')['state']['answers']['q1']['first']['result']=='correct'
  page.locator('#resume-button').click();control(page,'#restart-button').click();page.locator('#confirm-restart').click()
  expect(page.locator('#xp-total')).to_have_text('✦ 0 XP');assert current_record(page)['state']['answers']['q1']['first'] is not None
  passed('cancel preserves progress; confirmed restart resets only the current learner/exam, leaving A and other profiles intact')
  # A second exam identity is an isolated fixture, never a published extra game.
  different=json.loads(json.dumps(data));different['exam']['id']='fixture-other-exam'
  def other_exam(r):r.fulfill(content_type='text/javascript',body='window.HT_PRACTICE_DATA='+json.dumps(different)+';')
  context.route('**/truc-tuan-dual-data.js',other_exam)
  other=page_for(context);start(other);expect(other.locator('#xp-total')).to_have_text('✦ 0 XP')
  assert current_record(other)['examId']=='fixture-other-exam';other.close();context.unroute('**/truc-tuan-dual-data.js',other_exam)
  passed('a separate exam identity cannot read or overwrite the original exam progress')
  control(page,'#change-student').click();start(page)
  control(page,'#home-button').click()
  tab=page_for(context);start(tab);go(tab,'q2')
  expect(page.locator('#reload-progress')).to_be_visible();expect(control(page,'#jump-question')).to_be_disabled()
  assert current_record(tab)['state']['answers']['q1']['first']==firsts['q1']
  with page.expect_navigation(wait_until='load'):
   page.locator('#reload-progress').click()
  start(page);expect(page.locator('#xp-total')).to_have_text('✦ 390 XP');tab.close()
  passed('a changed same-profile tab is detected; stale UI cannot overwrite newer stored first results')
  for width in [360,390,768,820,1280]:
   page.set_viewport_size({'width':width,'height':900})
   for qid in ['q1','q13','q31','q36']:
    go(page,qid);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(width,qid)
    if qid=='q31':
     page.locator('#check-answer').scroll_into_view_if_needed()
     assert page.locator('#passage-panel').evaluate('e=>{const r=e.getBoundingClientRect();return r.top<innerHeight&&r.bottom>0}')
     if width in [390,1280]:page.screenshot(path=str(OUT/f'reading-{width}.png'),full_page=True)
  passed('all sections responsive at 360/390/768/820/1280px; reading remains available while answering')
  mobile=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce');mobile.route('**/*',route)
  touch=page_for(mobile);start(touch,'Học sinh cảm ứng','touch','challenge');go(touch,'q36')
  q=data['questions'][35]
  for i in order(q):touch.locator(f'#word-bank button[data-token-index="{i}"]').tap()
  touch.locator('#check-answer').tap();expect(touch.locator('#xp-total')).to_have_text('✦ 10 XP')
  go(touch,'q31');expect(touch.locator('#toggle-passage')).to_have_count(0);expect(touch.locator('#passage-content')).to_be_visible()
  touch.locator('#written-answer').fill('nháp đọc hiểu');touch.reload();start(touch,'Học sinh cảm ứng','touch','challenge')
  expect(touch.locator('#written-answer')).to_have_value('nháp đọc hiểu')
  expect(touch.locator('#passage-content')).to_be_visible();mobile.close()
  passed('real touch controls open a writing question, arrange all source tokens and check the answer')
  # Corrupt/old-schema records stay intact until the learner confirms a reset.
  page.evaluate('localStorage.setItem(HTDualStore.keyFor(HT_PRACTICE_DATA,{name:"Hỏng dữ liệu",code:""}),"{broken")')
  page.reload();start(page,'Hỏng dữ liệu','',resume=False);expect(page.locator('#resume-button')).to_be_disabled()
  assert page.evaluate('localStorage.getItem(HTDualStore.keyFor(HT_PRACTICE_DATA,{name:"Hỏng dữ liệu",code:""}))')=='{broken'
  page.locator('#restart-saved').click();page.locator('#confirm-restart').click();expect(page.locator('#xp-total')).to_have_text('✦ 0 XP')
  old_name='Phiên bản cũ'
  page.evaluate('''name=>{const student=HTDualProgress.identity(name,'');localStorage.setItem(HTDualStore.keyFor(HT_PRACTICE_DATA,student),JSON.stringify({schemaVersion:1,examId:HT_PRACTICE_DATA.exam.id,contentVersion:'old-source',state:HTDualProgress.create(HT_PRACTICE_DATA,student)}));}''',old_name)
  page.reload();start(page,old_name,'',resume=False)
  expect(page.locator('#resume-description')).to_contain_text('Đề đã được cập nhật')
  expect(page.locator('#resume-button')).to_be_disabled()
  assert current_record(page,old_name,'')['contentVersion']=='old-source'
  for failure in ['denied','quota']:
   blocked=browser.new_context();blocked.route('**/*',route)
   blocked.add_init_script('Object.defineProperty(window,"localStorage",{get(){throw new DOMException("Denied","SecurityError")}})' if failure=='denied' else 'Storage.prototype.setItem=function(){throw new DOMException("Full","QuotaExceededError")}')
   broken=page_for(blocked);start(broken,'Học sinh lưu lỗi','',resume=False)
   fill(broken,data['questions'][0]);broken.locator('#check-answer').click();expect(broken.locator('#xp-total')).to_have_text('✦ 10 XP')
   expect(broken.locator('#save-message')).to_contain_text('chưa lưu');blocked.close()
  passed('corrupt progress is not silently overwritten; blocked/quota storage warns and remains playable in memory')
  with tempfile.TemporaryDirectory(prefix='ht-dual-preview-test-') as temp:
   preview=Path(temp)/'preview'
   subprocess.run([sys.executable,str(ROOT/'tools/build-dual-mode-preview.py'),str(preview)],check=True,capture_output=True)
   offline=browser.new_context();file_errors=[]
   offline.route('**/*',lambda r:r.continue_() if r.request.url.startswith('file:') else (external.append(r.request.url),r.abort())[1])
   filepage=offline.new_page();filepage.on('pageerror',lambda e:file_errors.append(str(e)))
   filepage.on('console',lambda m:file_errors.append(m.text) if m.type=='error' else None)
   try:
    filepage.goto((preview/'MO_GAME.html').as_uri());filepage.wait_for_url('**/truc-tuan-dual-mode.html')
    start(filepage,'Xem thử offline','preview');fill(filepage,data['questions'][0]);filepage.locator('#check-answer').click()
    expect(filepage.locator('#xp-total')).to_have_text('✦ 10 XP')
    filepage.reload();start(filepage,'Xem thử offline','preview');expect(filepage.locator('#xp-total')).to_have_text('✦ 10 XP')
    filepage.locator('#audio-toggle').click();filepage.wait_for_function('!document.querySelector("audio").paused')
    errors.extend(file_errors)
    passed('offline package opens MO_GAME.html, saves/resumes progress and plays the local MP3')
   except Exception as error:
    if 'ERR_BLOCKED_BY_ADMINISTRATOR' not in str(error):raise
    skipped.append('Direct file:// preview blocked by this Chromium administrator policy (ERR_BLOCKED_BY_ADMINISTRATOR); not claimed as verified.')
    print('SKIP '+skipped[-1],flush=True)
    errors.extend(e for e in file_errors if 'ERR_BLOCKED_BY_ADMINISTRATOR' not in e)
   finally:offline.close()
   preview_server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(preview)))
   threading.Thread(target=preview_server.serve_forever,daemon=True).start();preview_base=f'http://127.0.0.1:{preview_server.server_port}/'
   bundle=browser.new_context()
   bundle.route('**/*',lambda r:r.continue_() if r.request.url.startswith(preview_base) else (external.append(r.request.url),r.abort())[1])
   try:
    preview_page=bundle.new_page();preview_page.on('pageerror',lambda e:errors.append(str(e)))
    preview_page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
    preview_page.goto(preview_base+'MO_GAME.html');preview_page.wait_for_url('**/truc-tuan-dual-mode.html')
    start(preview_page,'Xem thử gói game','preview');fill(preview_page,data['questions'][0]);preview_page.locator('#check-answer').click()
    preview_page.reload();start(preview_page,'Xem thử gói game','preview');expect(preview_page.locator('#xp-total')).to_have_text('✦ 10 XP')
    preview_page.locator('#audio-toggle').click();preview_page.wait_for_function('!document.querySelector("audio").paused')
   finally:bundle.close();preview_server.shutdown();preview_server.server_close()
  passed('self-contained review package works over HTTP with only its bundled files, resumes progress and plays MP3 without external dependencies')
  assert not errors,errors;assert not external,external
  passed('zero JavaScript/console errors, zero external/backend/Firebase requests; no automatic network transmission of learner details')
  context.close();browser.close()
 (OUT/'report.json').write_text(json.dumps({'questionsPlayed':42,'passedGroups':len(checks),'skippedChecks':skipped,'failed':0,'checks':checks,'consoleErrors':errors,'externalRequests':external},ensure_ascii=False,indent=2)+'\n')
finally:server.shutdown();server.server_close()
