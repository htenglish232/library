"""Real browser identity sharing and progress separation across Grades 7, 6, 8."""
from pathlib import Path
from urllib.parse import quote
import functools,http.server,json,threading
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def copyfile(self,source,output):
  try:super().copyfile(source,output)
  except (BrokenPipeError,ConnectionResetError):pass
 def translate_path(self,path):return super().translate_path(path[len('/library'):] if path.startswith('/library/') else path)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}/library/'
paths=[('grade-7/De_thi_GHK_1/1_THCS_Truc_Thai/practice-dual-mode.html',7),('grade-6/De_thi_GHK_1/3_THCS_Truc_Tuan/practice-dual-mode.html',6),('grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-dual-mode.html',8)];checks=[];errors=[]
def ready(page):expect(page.locator('#sound-toggle')).to_have_attribute('data-sound-state','ready')
def start(page):
 page.locator('#start-form button').click()
 if page.locator('#resume-panel').is_visible():page.locator('#resume-button').click()
def fill_identity(page,name,code):
 page.locator('#student-name').fill(name)
 if not page.locator('#student-code').is_visible():page.locator('.identity-options summary').click()
 page.locator('#student-code').fill(code)
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for touch in [False,True]:
   c=b.new_context(viewport={'width':390 if touch else 1280,'height':844},has_touch=touch,is_mobile=touch);page=c.new_page();page.on('pageerror',lambda e:errors.append(str(e)));saved={}
   for i,(path,grade) in enumerate(paths):
    page.goto(BASE+quote(path));ready(page)
    if i==0:fill_identity(page,'Học sinh liên khối','HT-01')
    else:expect(page.locator('#student-name')).to_have_value('Học sinh liên khối');expect(page.locator('#student-code')).to_have_value('HT-01');expect(page.locator('#sound-toggle')).to_have_text('🔇 Âm thanh: Tắt')
    start(page);expect(page.locator('#section-kicker')).to_contain_text('GRADE '+str(grade));expect(page.locator('#xp-total')).to_have_text('✦ 0 XP');q=page.evaluate('HT_PRACTICE_DATA.questions[0]');page.locator(f'#answer-area input[value="{q["accepted"][0]}"]').check();page.locator('#check-answer').click();expect(page.locator('#xp-total')).to_have_text('✦ 10 XP')
    if i==0:page.locator('#sound-toggle').click()
    key=page.evaluate('HTDualStore.keyFor(HT_PRACTICE_DATA,{name:"Học sinh liên khối",code:"HT-01"})');saved[key]=page.evaluate('k=>localStorage.getItem(k)',key)
   assert len(saved)==3
   for path,grade in paths:
    page.goto(BASE+quote(path));ready(page);start(page);expect(page.locator('#xp-total')).to_have_text('✦ 10 XP');page.locator('#results-button').click();page.locator('#continue-playing').click();expect(page.locator('#xp-total')).to_have_text('✦ 10 XP')
   page.goto(BASE+quote(paths[0][0]));ready(page);start(page);page.locator('#change-student').click();fill_identity(page,'Học sinh khác','HT-02');start(page);expect(page.locator('#xp-total')).to_have_text('✦ 0 XP');page.locator('#restart-button').click();page.locator('#confirm-restart').click()
   for key,value in saved.items():assert json.loads(page.evaluate('k=>localStorage.getItem(k)',key))['state']['answers']==json.loads(value)['state']['answers']
   page.goto(BASE+quote(paths[1][0]));ready(page);expect(page.locator('#student-name')).to_have_value('Học sinh khác');expect(page.locator('#student-code')).to_have_value('HT-02');start(page);expect(page.locator('#xp-total')).to_have_text('✦ 0 XP');c.close();msg=('touch emulation' if touch else 'desktop')+': Grade 7→6→8 remembers identity/mute; grade labels correct; each exam/student has separate XP/progress; restore/navigation/reset preserve old records';checks.append(msg);print('PASS '+msg,flush=True)
  assert not errors,errors;Path('/tmp/grade7-cross-grade-browser.json').write_text(json.dumps(dict(checks=checks,errors=errors),ensure_ascii=False,indent=2)+'\n');b.close()
finally:server.shutdown()
