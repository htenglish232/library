"""Every existing Reading question: exact source fragment, labelled blank and scroll."""
from pathlib import Path
from urllib.parse import quote,unquote
import functools,http.server,json,re,threading
from playwright.sync_api import sync_playwright,expect
from practice_browser_controls import control,assert_context
ROOT=Path(__file__).resolve().parents[1];OUT=Path('/tmp/all-minimal');rows=json.loads((ROOT/'docs/minimal-exam-ui/inventory.json').read_text())['inventory']
handler=(ROOT/'tests/dual-mode-browser.py').read_text().split('class Handler',1)[1].split('server=http.server',1)[0];exec('class Handler'+handler)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}/'
errors=[];bad=[];cases=[];highlights=0
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce');ctx.route('**/*',lambda r:r.continue_() if r.request.url.startswith(BASE) else r.abort());page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:bad.append(r.url) if r.status>=400 else None)
  for row in rows:
   page.goto(BASE+'library/'+quote(row['game']));page.wait_for_selector('html[data-minimal-ready="true"]',state='attached');page.locator('#student-name').fill('Kiểm tra Reading');page.locator('#start-form button').click();data=page.evaluate('window.HT_PRACTICE_DATA||window.HT_GAME_SOURCE');previous=None;scroll=0
   for id in row['readingEvidence']:
    q=next(q for q in data['questions'] if q['id']==id)
    if page.locator('#question-card').get_attribute('data-question-id')!=id:control(page,'#jump-question').select_option(id)
    page.wait_for_timeout(25);assert_context(page,q,data)
    text=page.locator('#passage-content').text_content()
    if text==previous:assert abs(page.locator('#passage-content').evaluate('e=>e.scrollTop')-scroll)<2,(row['game'],id,'reading position lost')
    highlights+=page.locator('#passage-content mark.minimal-blank').count()
    page.locator('#passage-content').evaluate('e=>e.scrollTop=80');page.wait_for_timeout(25);scroll=page.locator('#passage-content').evaluate('e=>e.scrollTop');previous=text
    expect(page.locator('#xp-total')).to_have_text('✦ 0 XP');cases.append({'game':row['game'],'question':id,'result':'PASS'});page.locator('#next-question').click()
   print('PASS Reading',row['game'],row['readingQuestions'],'source questions',flush=True)
  assert not errors,errors;assert not bad,bad
  assert len(cases)==sum(row['readingQuestions'] for row in rows)
  (OUT/'reading.json').write_text(json.dumps({'cases':cases,'exactBlankHighlights':highlights,'errors':errors,'bad':bad},ensure_ascii=False,indent=2)+'\n');print('PASS',len(cases),'Reading questions;',highlights,'exact numbered blanks; text, markup, reading scroll and XP retained',flush=True);browser.close()
finally:server.shutdown()
