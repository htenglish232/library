"""Browser identity and progress isolation across the unchanged shared runtime."""
from pathlib import Path
from urllib.parse import quote
import functools,http.server,json,threading
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def translate_path(self,path):return super().translate_path(path[len('/library'):] if path.startswith('/library/') else path)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}/library/'
paths=['grade-6/De_thi_GHK_1/3_THCS_Truc_Tuan/practice-dual-mode.html','grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-dual-mode.html'];checks=[];errors=[]
def ready(page):expect(page.locator('#sound-toggle')).to_have_attribute('data-sound-state','ready')
def start(page):
 page.locator('input[name=start-mode][value=ordered]').check();page.locator('#start-form button').click()
 if page.locator('#resume-panel').is_visible():page.locator('#resume-button').click()
def check(page):
 q=page.evaluate('HT_PRACTICE_DATA.questions[0]');page.locator(f'#answer-area input[value="{q["accepted"][0]}"]').check();page.locator('#check-answer').click();expect(page.locator('#xp-total')).to_have_text('✦ 10 XP')
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for touch in [False,True]:
   c=b.new_context(viewport={'width':390 if touch else 1280,'height':844},has_touch=touch,is_mobile=touch);page=c.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(BASE+quote(paths[0]));ready(page);page.locator('#student-name').fill('Học sinh liên khối');page.locator('.identity-options summary').click();page.locator('#student-code').fill('HT-01');start(page);expect(page.locator('#section-kicker')).to_contain_text('GRADE 6');check(page)
   key6=page.evaluate('HTDualStore.keyFor(HT_PRACTICE_DATA,{name:"Học sinh liên khối",code:"HT-01"})');record6=page.evaluate('k=>localStorage.getItem(k)',key6);page.locator('#sound-toggle').click()
   page.goto(BASE+quote(paths[1]));ready(page);expect(page.locator('#student-name')).to_have_value('Học sinh liên khối');expect(page.locator('#student-code')).to_have_value('HT-01');expect(page.locator('#sound-toggle')).to_have_text('🔇 Âm thanh: Tắt');start(page);expect(page.locator('#section-kicker')).to_contain_text('GRADE 8');expect(page.locator('#xp-total')).to_have_text('✦ 0 XP');check(page)
   key8=page.evaluate('HTDualStore.keyFor(HT_PRACTICE_DATA,{name:"Học sinh liên khối",code:"HT-01"})');record8=page.evaluate('k=>localStorage.getItem(k)',key8);assert key6!=key8;assert page.evaluate('k=>localStorage.getItem(k)',key6)==record6
   page.goto(BASE+quote(paths[0]));ready(page);start(page);expect(page.locator('#xp-total')).to_have_text('✦ 10 XP');page.locator('#change-student').click();expect(page.locator('#student-name')).to_have_value('');page.locator('#student-name').fill('Học sinh khác');page.locator('.identity-options summary').click();page.locator('#student-code').fill('HT-02');start(page);expect(page.locator('#xp-total')).to_have_text('✦ 0 XP');page.locator('#restart-button').click();page.locator('#confirm-restart').click();expect(page.locator('#xp-total')).to_have_text('✦ 0 XP');assert page.evaluate('k=>localStorage.getItem(k)',key8)==record8;assert json.loads(page.evaluate('k=>localStorage.getItem(k)',key6))['state']['answers']==json.loads(record6)['state']['answers']
   page.goto(BASE+quote(paths[1]));ready(page);expect(page.locator('#student-name')).to_have_value('Học sinh khác');expect(page.locator('#student-code')).to_have_value('HT-02');start(page);expect(page.locator('#xp-total')).to_have_text('✦ 0 XP');assert page.evaluate('k=>localStorage.getItem(k)',key8)==record8;c.close();msg=('touch emulation' if touch else 'desktop')+': one shared remembered identity/mute, separate Grade 6/8 exam and student progress, resume and confirmed reset preserve old Grade 8 records';checks.append(msg);print('PASS '+msg,flush=True)
  # A complete alternative explicitly present in the source must be accepted.
  c=b.new_context();page=c.new_page();page.goto(BASE+'grade-6/De_thi_GHK_1/5_THCS_Trung_Dong/practice-dual-mode.html');ready(page);page.locator('#student-name').fill('Biến thể nguồn');start(page);page.locator('#jump-question').select_option('W1_3')
  for i in [0,1,2,5,4,3,6]:page.locator(f'#word-bank [data-token-index="{i}"]').click()
  page.locator('#check-answer').click();expect(page.locator('#xp-total')).to_have_text('✦ 10 XP');assert not page.locator('#feedback').evaluate('e=>e.classList.contains("is-wrong")');c.close();checks.append('source-verified alternate arrangement is accepted with +10 XP, without adding or changing original tiles');print('PASS '+checks[-1],flush=True)
  assert not errors,errors;Path('/tmp/grade6-cross-grade-browser.json').write_text(json.dumps(dict(checks=checks,errors=errors),ensure_ascii=False,indent=2)+'\n');b.close()
finally:server.shutdown()
