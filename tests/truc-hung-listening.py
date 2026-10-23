"""Check the two uploaded listening files in the exam and all 43 restored game questions."""
from pathlib import Path
import functools,hashlib,http.server,json,os,re,shutil,subprocess,threading
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('GRADE8_GAME_TEST_OUTPUT','/tmp/truc-hung-listening-tests'));OUT.mkdir(parents=True,exist_ok=True)
FOLDERS=['12_THCS_Truc_Hung']
def load(folder):return json.loads((ROOT/'grade-8/De_thi_GHK1'/folder/'practice-game-data.js').read_text().split('window.HT_PRACTICE_DATA = ',1)[1].strip()[:-1])
def norm(value):return re.sub(r'\s+',' ',re.sub(r'[.,!?;:]','',value.lower().replace('’',"'").replace('‘',"'"))).strip()
def order(tokens,target):
 words=norm(target).split()
 def solve(indices,left):
  if not left:return indices if len(indices)==len(tokens) else None
  for i,token in enumerate(tokens):
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
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}/'
reports=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'),args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
  folder='12_THCS_Truc_Hung';data=load(folder)
  assert [t['src'] for t in data['tracks']]==['Part 1.mp3','Part 2.mp3']
  assert all(not t['wholeFile'] for t in data['tracks'])
  exam_file=ROOT/'grade-8/De_thi_GHK1'/folder/data['exam']['sourceHtml']
  assert hashlib.sha256(exam_file.read_bytes()).hexdigest()==data['exam']['sourceSha256']
  errors=[];unexpected=[]
  exam_context=browser.new_context(viewport={'width':390,'height':844})
  def exam_route(r):
   if r.request.url.startswith(BASE):r.continue_()
   elif r.request.url=='https://cdn.tailwindcss.com/':r.fulfill(content_type='text/javascript',body='window.tailwind={};document.head.insertAdjacentHTML("beforeend","<style>.hidden{display:none!important}</style>");' )
   elif r.request.url=='https://cdn.tailwindcss.com':r.fulfill(content_type='text/javascript',body='window.tailwind={};document.head.insertAdjacentHTML("beforeend","<style>.hidden{display:none!important}</style>");' )
   elif r.request.url.startswith('https://fonts.googleapis.com/') or r.request.url.startswith('https://fonts.gstatic.com/'):r.abort()
   else:unexpected.append(r.request.url);r.abort()
  # Do not contact third-party styling services while testing media and grading.
  exam_context.route('**/*',exam_route);exam=exam_context.new_page()
  exam.on('pageerror',lambda e:errors.append(str(e)))
  for prefix in ['', 'library/']:
   exam.goto(BASE+prefix+quote(str(exam_file.relative_to(ROOT))))
   source_answers=exam.evaluate('answersData')
   assert set(source_answers)=={q['id'] for q in data['questions']}
   for q in data['questions']:assert q['sourceRaw']==source_answers[q['id']],q['id']
   expect(exam.locator('[data-listening-player]')).to_have_count(2)
   for number in [1,2]:
    player=exam.locator(f'[data-listening-part="{number}"]');audio=player.locator('audio')
    assert audio.get_attribute('src')==f'Part {number}.mp3'
    expect(player.locator('strong')).to_have_text(f'🎧 LISTENING – PART {number}')
    audio.evaluate('(a)=>a.load()');exam.wait_for_function('(n)=>document.querySelector(`[data-listening-part="${n}"] audio`).readyState>=1',arg=number)
    assert audio.evaluate('(a)=>Number.isFinite(a.duration)&&a.duration>30')
    player.locator('.ht-play').click();exam.wait_for_function('(n)=>!document.querySelector(`[data-listening-part="${n}"] audio`).paused',arg=number)
    assert exam.locator('audio').evaluate_all('(els)=>els.filter(a=>!a.paused).length')==1
    player.locator('.ht-play').click();assert audio.evaluate('(a)=>a.paused')
    audio.evaluate('(a)=>a.currentTime=10');player.locator('.ht-forward').click();assert abs(audio.evaluate('(a)=>a.currentTime')-15)<1
    player.locator('.ht-back').click();assert abs(audio.evaluate('(a)=>a.currentTime')-10)<1
    for speed in ['0.75','1.25','1']:
     player.locator('.ht-speed').select_option(speed);assert audio.evaluate('(a)=>a.playbackRate')==float(speed)
    player.locator('.ht-seek').evaluate('(e)=>{e.value=20;e.dispatchEvent(new Event("input",{bubbles:true}));}')
    assert abs(audio.evaluate('(a)=>a.currentTime')-20)<1
    player.locator('.ht-stop').click();assert audio.evaluate('(a)=>a.paused&&a.currentTime===0')
   first=exam.locator('[data-listening-part="1"]');second=exam.locator('[data-listening-part="2"]')
   first.locator('.ht-play').click();exam.wait_for_function('!document.querySelectorAll("audio")[0].paused')
   second.locator('.ht-play').click();exam.wait_for_function('!document.querySelectorAll("audio")[1].paused')
   assert first.locator('audio').evaluate('(a)=>a.paused');second.locator('.ht-stop').click()
   # Both players remain available after the original submission flow locks answers.
   exam.locator('#btnSubmitTest').click();exam.locator('button[onclick="finalizeSubmission()"]').click()
   for number in [1,2]:
    player=exam.locator(f'[data-listening-part="{number}"]')
    expect(player.locator('.ht-play')).to_be_enabled();expect(player.locator('.ht-speed')).to_be_enabled()
  assert not errors,errors;assert not unexpected,unexpected
  exam_context.close()
  print('PASS exercise Part 1/2: distinct MP3s, real playback, mutual pause, seek, speed, stop, controls after submission, original 43 answer records, root and /library/',flush=True)
  for folder in FOLDERS:
   data=load(folder);errors=[];external=[];checks=[]
   def passed(message):checks.append(message);print('PASS '+data['exam']['id']+' '+message,flush=True)
   context=browser.new_context(viewport={'width':1280,'height':900},reduced_motion='reduce')
   def route(r):
    if r.request.url.startswith(BASE):r.continue_()
    else:external.append(r.request.url);r.abort()
   context.route('**/*',route);page=context.new_page();page.set_default_timeout(12000)
   page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
   prefix='library/'+quote('grade-8/De_thi_GHK1/'+folder+'/');url=BASE+prefix+'practice-game-pilot.html'
   assert page.goto(url).status==200
   expect(page.locator('#welcome')).to_be_visible();assert page.evaluate('window.HT_PRACTICE_DATA')==data
   for width in [360,390,768,820,1280]:
    page.set_viewport_size({'width':width,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(folder,width,'welcome overflow')
   page.screenshot(path=str(OUT/(data['exam']['id']+'-welcome.png')),full_page=True)
   page.locator('#start-form button').click();expect(page.locator('#name-error')).to_contain_text('nhập tên')
   page.locator('#student-name').fill('  Học sinh  thử nghiệm  ');page.locator('#start-form button').click()
   expect(page.locator('#student-label')).to_have_text('Học sinh thử nghiệm')
   expect(page.locator('#journey-count')).to_have_text(f'0/{len(data["questions"])} câu đã luyện')
   assert page.locator('#challenge-grid button').count()==len(data['sections'])
   passed('launcher, source metadata, normalized name, dynamic question/section counts, welcome responsive')
   def go(q):
    if page.locator('#play').is_visible():page.locator(f'#section-tabs button[data-section="{q["section"]}"]').click()
    else:
     if not page.locator('#challenges').is_visible():page.locator('#home-button').click()
     page.locator(f'#challenge-grid button[data-section="{q["section"]}"]').click()
    page.locator(f'#question-dots button[data-question-id="{q["id"]}"]').click()
    expect(page.locator('#question-card')).to_have_attribute('data-question-id',q['id'])
   wrongs={next(q['id'] for q in data['questions'] if q['kind']=='choice')}
   wrongs.add(next(q['id'] for q in data['questions'] if q['kind']=='rearrange' and q['autoGrade']))
   wrongs.update(q['id'] for q in data['questions'] if q['kind']=='multi-text')
   xp=0;audio_seen=set();first_answers={}
   def fill(q,wrong=False):
    if q['kind']=='choice':
     answer=next(o['value'] for o in q['options'] if o['value'] not in q['accepted']) if wrong else q['accepted'][0]
     page.locator(f'#answer-area input[value="{answer}"]').check();return answer
    if q['kind']=='multi-text':
     for i,answer in enumerate(q['acceptedTuples'][0]):page.locator(f'#written-answer-{i}').fill('incorrect' if wrong and i==0 else answer)
     return None
    if q['kind']=='text':
     answer=q['accepted'][0] if q['autoGrade'] else 'Please ask the teacher to review this answer.'
     page.locator('#written-answer').fill(answer);return answer
    sequence=order(q['tokens'],q['accepted'][0]) if q['autoGrade'] else list(range(len(q['tokens'])))
    assert sequence is not None,(q['id'],'cannot build source answer')
    if wrong:sequence=list(reversed(sequence))
    for i in sequence:page.locator(f'#word-bank button[data-token-index="{i}"]').click()
    return sequence
   for q in data['questions']:
    go(q);expect(page.locator('#feedback')).to_be_hidden()
    # All English source prompt/option content survives browser HTML parsing.
    expected=page.evaluate("s=>new DOMParser().parseFromString(s,'text/html').body.textContent",q['promptHtml'])
    assert norm(page.locator('#prompt').inner_text())==norm(expected),(q['id'],'prompt differs')
    if q['kind']=='choice':assert page.locator('#answer-area input[type=radio]').count()==len(q['options'])
    if q.get('contextHtml') or 'context' in q:expect(page.locator('#passage-panel')).to_be_visible()
    if q.get('track'):
     expect(page.locator('#transcript-panel')).to_be_hidden();assert page.locator('#transcript-content').inner_text()==''
     if q['track'] not in audio_seen:
      audio_seen.add(q['track']);page.wait_for_function('document.querySelector("audio").readyState>=1')
      assert page.locator('audio').evaluate('(a)=>a.duration')>10
      for rate in ['0.75','1','1.25']:
       page.locator('#audio-speed').select_option(rate);assert page.locator('audio').evaluate('(a)=>a.playbackRate')==float(rate)
      page.locator('#audio-toggle').click();page.wait_for_function('!document.querySelector("audio").paused');page.locator('#audio-toggle').click()
      page.locator('#audio-forward').click();page.wait_for_function('document.querySelector("audio").currentTime>=5')
      page.locator('#audio-back').click();page.wait_for_function('document.querySelector("audio").currentTime<2')
      page.locator('#audio-seek').fill('50');page.wait_for_function('Math.abs(document.querySelector("audio").currentTime/document.querySelector("audio").duration-.5)<.02')
    if q['kind']=='multi-text':
     page.locator('#written-answer-0').fill(q['acceptedTuples'][0][0]);page.locator('#check-answer').click()
     expect(page.locator('#answer-error')).to_contain_text('chọn hoặc nhập')
    first_answers[q['id']]=fill(q,q['id'] in wrongs)
    if q['kind']=='rearrange':
     last=page.locator('#word-target button').last.inner_text();page.locator('#undo-word').click();assert page.locator('#word-target button').count()==len(q['tokens'])-1
     used=first_answers[q['id']][-1];page.locator(f'#word-bank button[data-token-index="{used}"]').click()
    if q['autoGrade'] and q['id'] not in wrongs:xp+=10
    page.locator('#check-answer').click();expect(page.locator('#feedback')).to_be_visible();expect(page.locator('#xp-total')).to_have_text(f'✦ {xp} XP')
    if not q['autoGrade']:expect(page.locator('#feedback-title')).to_have_text('Chờ giáo viên đối chiếu')
    if q.get('track'):expect(page.locator('#transcript-panel')).to_be_visible()
    if q['teacherFlags']:expect(page.locator('#explanation-content')).to_contain_text('Giáo viên cần duyệt')
    if q['id'] in page.evaluate('Object.keys(window.HT_PRACTICE_SUPPORT.items)'):expect(page.locator('#explanation-content')).to_contain_text('Chưa được giáo viên xác nhận')
    page.evaluate('document.querySelector("#check-answer").dispatchEvent(new MouseEvent("click"))');expect(page.locator('#xp-total')).to_have_text(f'✦ {xp} XP')
   pending=sum(not q['autoGrade'] for q in data['questions'])
   page.locator('#results-button').click();expect(page.locator('#result-unanswered')).to_have_text('0')
   expect(page.locator('#result-pending')).to_have_text(str(pending));expect(page.locator('#result-wrong')).to_have_text(str(len(wrongs)))
   expect(page.locator('#result-correct')).to_have_text(str(xp//10));expect(page.locator('#result-xp')).to_have_text(str(xp))
   passed(f'ALL {len(data["questions"])} source questions played; correct/wrong/manual review, all options/fields/tokens, audio controls/transcript gating, XP once, exact summary ({xp} XP)')
   page.locator('#review-wrong').click()
   for q in data['questions']:
    if q['id'] not in wrongs and q['autoGrade']:continue
    expect(page.locator('#question-card')).to_have_attribute('data-question-id',q['id'])
    fill(q);page.locator('#check-answer').click();expect(page.locator('#xp-total')).to_have_text(f'✦ {xp} XP');page.locator('#next-question').click()
   expect(page.locator('#results')).to_be_visible();expect(page.locator('#review-summary')).to_contain_text(f'{len(wrongs)} câu đã làm đúng')
   expect(page.locator('#result-xp')).to_have_text(str(xp));passed('mixed-type wrong/pending review preserves first-attempt score and awards zero extra XP')
   for width in [360,390,768,820,1280]:
    page.set_viewport_size({'width':width,'height':900})
    for section in data['sections']:
     q=next(q for q in data['questions'] if q['section']==section['id']);go(q)
     assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(folder,width,section['id'],'overflow')
     if q.get('contextHtml') or 'context' in q:
      page.locator('#check-answer').scroll_into_view_if_needed()
      assert page.locator('#passage-panel').evaluate('(e)=>{const r=e.getBoundingClientRect();return r.top<innerHeight&&r.bottom>0;}')
     if width in [390,1280] and section['id']=='reading':page.screenshot(path=str(OUT/f'{data["exam"]["id"]}-reading-{width}.png'),full_page=True)
   passed('all sections responsive at 360/390/768/820/1280px; original reading/table context remains on screen')
   mobile=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce');mobile.route('**/*',route)
   touch=mobile.new_page();touch.on('pageerror',lambda e:errors.append(str(e)));touch.goto(url)
   touch.locator('#student-name').fill('Học sinh cảm ứng');touch.locator('#start-form button').tap()
   first=data['questions'][0];touch.locator(f'#challenge-grid button[data-section="{first["section"]}"]').tap()
   touch.locator(f'#answer-area input[value="{first["accepted"][0]}"]').tap();touch.locator('#check-answer').tap();expect(touch.locator('#xp-total')).to_have_text('✦ 10 XP')
   build=next(q for q in data['questions'] if q['kind']=='rearrange' and q['autoGrade']);touch.locator(f'#section-tabs button[data-section="{build["section"]}"]').tap();touch.locator(f'#question-dots button[data-question-id="{build["id"]}"]').tap()
   for i in order(build['tokens'],build['accepted'][0]):touch.locator(f'#word-bank button[data-token-index="{i}"]').tap()
   touch.locator('#reset-words').tap();assert touch.locator('#word-target button').count()==0
   for i in order(build['tokens'],build['accepted'][0]):touch.locator(f'#word-bank button[data-token-index="{i}"]').tap()
   touch.locator('#check-answer').tap();expect(touch.locator('#xp-total')).to_have_text('✦ 20 XP')
   for track in data['tracks']:assert touch.request.get(BASE+prefix+quote(track['src'])).status==200
   mobile.close();passed('touch selection, sentence building/reset, and /library/ relative HTML/CSS/JS/fonts/audio work')
   assert not errors,errors;assert not external,external;passed('zero JavaScript/console errors and zero external/backend/Firebase requests')
   report={'exam':data['exam'],'dataSha256':hashlib.sha256((ROOT/'grade-8/De_thi_GHK1'/folder/'practice-game-data.js').read_bytes()).hexdigest(),'questions':len(data['questions']),'sections':len(data['sections']),'physicalAudioFiles':len({t['src'] for t in data['tracks']}),'images':len(data['sourceSnapshot']['images']),'passedGroups':len(checks),'failed':0,'checks':checks,'questionsExercised':[q['id'] for q in data['questions']],'manualReviewQuestions':[q['id'] for q in data['questions'] if not q['autoGrade']],'teacherFlags':data['issues'],'consoleErrors':errors,'externalRequests':external}
   (OUT/(data['exam']['id']+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');reports.append(report);context.close()
  # Audio identities are independent of section identities in the shared schema.
  remapped=json.loads(json.dumps(data));mapping={t['id']:'clip-'+str(i) for i,t in enumerate(remapped['tracks'])}
  for t in remapped['tracks']:t['id']=mapping[t['id']]
  for q in remapped['questions']:
   if q.get('track'):q['track']=mapping[q['track']]
  clip=browser.new_context();clip.route('**/*',lambda r:r.fulfill(status=200,content_type='text/javascript',body='window.HT_PRACTICE_DATA='+json.dumps(remapped)+';') if r.request.url.split('?')[0].endswith('/practice-game-data.js') else r.continue_() if r.request.url.startswith(BASE) else r.abort())
  clip_page=clip.new_page();clip_errors=[];clip_page.on('pageerror',lambda e:clip_errors.append(str(e)));clip_page.goto(url)
  clip_page.locator('#student-name').fill('Thử audio độc lập');clip_page.locator('#start-form button').click()
  clip_page.locator('#challenge-grid button').first.click();clip_page.wait_for_function('document.querySelector("audio").readyState>=1')
  assert not clip_errors;clip.close();print('PASS audio IDs can differ from section IDs',flush=True)
  invalid=browser.new_context();invalid.route('**/*',lambda r:r.fulfill(status=200,content_type='text/javascript',body='window.HT_PRACTICE_DATA={schemaVersion:99};') if r.request.url.split('?')[0].endswith('/practice-game-data.js') else r.continue_() if r.request.url.startswith(BASE) else r.abort())
  bad=invalid.new_page();invalid_errors=[];bad.on('pageerror',lambda e:invalid_errors.append(str(e)));bad.goto(url)
  expect(bad.locator('#name-error')).to_contain_text('Dữ liệu đề chưa thể mở')
  expect(bad.locator('#start-form button')).to_be_disabled();assert not invalid_errors
  invalid.close();print('PASS invalid/missing source data shows a teacher-facing error and disables start without JavaScript crashes',flush=True)
  browser.close()
 (OUT/'summary.json').write_text(json.dumps({'pilots':len(reports),'questions':sum(r['questions'] for r in reports),'failed':0},indent=2)+'\n')
 print('PASS Truc Hung game; '+str(sum(r['questions'] for r in reports))+' questions exercised. Reports: '+str(OUT),flush=True)
finally:server.shutdown();server.server_close()
