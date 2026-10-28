"""Smoke all 52 unchanged games; exact source equality is checked by the Node suite."""
from pathlib import Path
from urllib.parse import quote
import functools,http.server,json,threading
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];SKIP='grade-8/De_thi_GHK1/3_THCS Trung Dong/practice-dual-mode.html'
files=sorted([*ROOT.glob('grade-[678]/**/*-dual-mode.html'),*ROOT.glob('grade-8/**/practice-game-pilot.html'),*ROOT.glob('grade-8/**/truc-tuan-game-test.html')]);files=[f for f in files if f.relative_to(ROOT).as_posix()!=SKIP];assert len(files)==52
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def copyfile(self,source,output):
  try:super().copyfile(source,output)
  except (BrokenPipeError,ConnectionResetError):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}/'
errors=[];external=[];report=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
  ctx.route('**/*',lambda r:r.continue_() if r.request.url.startswith(BASE) else (external.append(r.request.url),r.abort())[-1])
  page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  for f in files:
   path=f.relative_to(ROOT).as_posix();page.goto(BASE+quote(path));assert not page.locator('html[data-minimal-ui]').count()
   page.locator('#student-name').fill('Hồi quy game khác');page.locator('#start-form button').click();expect(page.locator('#play')).to_be_visible()
   data=page.evaluate('window.HT_PRACTICE_DATA||window.HT_GAME_SOURCE');assert data['questions']
   expect(page.locator('#question-dots')).to_be_visible();expect(page.locator('#question-dots button')).to_have_count(len(data['questions']))
   assert page.locator('.question-navigation').evaluate('e=>getComputedStyle(e).position')!='fixed'
   expect(page.locator('#section-title')).to_have_text('Làm toàn bộ đề');assert not page.locator('#minimal-tools,#minimal-question-list').count()
   page.locator('#next-question').click();expect(page.locator('#question-card')).to_have_attribute('data-question-id',data['questions'][1]['id'])
   page.locator('#previous-question').click();expect(page.locator('#question-card')).to_have_attribute('data-question-id',data['questions'][0]['id'])
   report.append({'game':path,'questions':len(data['questions']),'result':'PASS'});print('PASS unchanged',path,flush=True)
  assert not errors,errors;assert not external,external
  Path('/tmp/trung-dong-minimal/unaffected.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('PASS all 52 other games keep existing UI/navigation, no external requests or JS errors',flush=True);browser.close()
finally:server.shutdown()
