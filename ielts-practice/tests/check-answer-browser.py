"""First-response checks, source explanations/keywords and save migration."""
from pathlib import Path
import argparse, functools, http.server, json, os, shutil, threading
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[2];UNIT=ROOT/'ielts-practice/unit-2-individuals-and-families'
key=json.loads((UNIT/'answers.json').read_text())
parser=argparse.ArgumentParser();parser.add_argument('--browser-path',default=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'));parser.add_argument('--name',default='chromium');args=parser.parse_args()
OUT=Path('/tmp/ht-ielts-unit2')/args.name/'checks';OUT.mkdir(parents=True,exist_ok=True)
checks,errors,bad,external=[],[],[],[]
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def translate_path(self,path):
  if path.startswith('/library/'):path=path[len('/library'):]
  return super().translate_path(path)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}'
URL=BASE+'/library/ielts-practice/unit-2-individuals-and-families/index.html'
def jump(page,label):
 if page.locator('#vocabulary-reading-top').is_visible():page.locator('#vocabulary-reading-top').click()
 page.locator('#step-picker').evaluate('e=>e.open=true');page.get_by_role('button',name=label,exact=True).click()
def passed(text):checks.append(text);print('PASS',args.name,text,flush=True)
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=args.browser_path,args=['--no-sandbox'])
  for width,height in [(1440,1000),(390,844)]:
   context=browser.new_context(viewport={'width':width,'height':height});requests=[]
   context.route('**/*',lambda r:r.continue_() if r.request.url.startswith(BASE+'/') else (external.append(r.request.url),r.abort())[-1])
   page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
   page.on('response',lambda r:bad.append([r.status,r.url]) if r.status>=400 else None)
   page.on('request',lambda r:requests.append(r.url))
   page.goto(URL);page.locator('#student-name').fill('Nguyễn An');page.locator('#start-form button').click();jump(page,'C · Câu 1')
   expect(page.locator('#feedback')).to_be_hidden();page.locator('#check-answer').click()
   expect(page.locator('#check-error')).to_contain_text('chọn một đáp án')
   assert not any(url.endswith(('/answers.json','/support.json')) for url in requests)
   page.locator('input[value=A]').check();page.locator('#check-answer').click()
   expect(page.locator('#feedback')).to_contain_text('Sai · Đáp án: B')
   expect(page.locator('#feedback')).to_contain_text(key['multipleChoice'][0]['explanation'])
   expect(page.locator('#feedback .keyword-list span')).to_have_count(3)
   expect(page.locator('#feedback blockquote mark')).to_have_count(3)
   expect(page.locator('input[value=A]')).to_be_disabled()
   expect(page.locator('#check-answer')).to_have_text('Đã kiểm tra ✓')
   page.screenshot(path=str(OUT/f'mcq-feedback-{width}.png'),full_page=True)
   page.locator('#next').click();expect(page.locator('#feedback')).to_be_hidden();expect(page.locator('#check-answer')).to_be_enabled()
   page.locator('input[value=B]').check();page.locator('#check-answer').click();expect(page.locator('#feedback')).to_contain_text('Đúng · Đáp án: B')
   page.reload();expect(page.locator('input[value=B]')).to_be_checked();expect(page.locator('input[value=B]')).to_be_disabled()
   jump(page,'C · Câu 1');expect(page.locator('input[value=A]')).to_be_checked();expect(page.locator('#feedback')).to_contain_text('Sai · Đáp án: B')
   jump(page,'D · Summary');page.locator('#check-answer').click();expect(page.locator('#check-error')).to_contain_text('ít nhất một ô')
   expect(page.locator('#feedback')).to_be_hidden()
   page.locator('#blank-4').fill('relationships');page.locator('#check-answer').click()
   expect(page.locator('#blank-4')).to_be_disabled();expect(page.locator('#blank-5')).to_be_enabled()
   expect(page.locator('#feedback')).to_contain_text('__________(5)')
   assert 'emotional distance' not in page.locator('#feedback').inner_text()
   expect(page.locator('#feedback .summary-feedback')).to_have_count(1)
   page.locator('#blank-1').fill('behaviour');page.locator('#blank-2').fill(' SUPPORT ');page.locator('#blank-3').fill('support')
   page.locator('#check-answer').click();expect(page.locator('#feedback .summary-feedback')).to_have_count(4)
   expect(page.locator('#blank-1')).to_have_class('wrong');expect(page.locator('#blank-2')).to_have_class('correct')
   expect(page.locator('#blank-3')).to_be_disabled();expect(page.locator('#blank-10')).to_be_enabled()
   page.reload();expect(page.locator('#blank-1')).to_have_value('behaviour');expect(page.locator('#blank-1')).to_be_disabled()
   page.locator('.summary-feedback').nth(1).locator('summary').click()
   expect(page.locator('.summary-feedback').nth(1)).to_contain_text('support')
   page.screenshot(path=str(OUT/f'summary-feedback-{width}.png'),full_page=True)
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
   jump(page,'E · Translation');page.locator('#translation-input').fill('Families help one another.')
   expect(page.locator('#check-answer')).to_have_count(0)
   page.locator('#submit-open').click();page.locator('#submit-confirm').click()
   expect(page.locator('#results')).to_be_visible()
   assert page.locator('#result-stats strong').all_text_contents()==['20','4','2','14']
   page.locator('#review-wrong').click();page.locator('input[value=B]').check();page.locator('#review-check').click()
   expect(page.locator('#review-support .keyword-list')).to_be_visible()
   page.locator('#results-open').click();assert page.locator('#result-stats strong').all_text_contents()==['20','4','2','14']
   expect(page.locator('#result-translation')).to_have_text('Families help one another.')
   context.close();passed(f'{width}px: check each MCQ/filled Summary cells; first response locked and saved; source explanation, keywords/highlighted evidence; unchecked answers concealed; review keeps original score; Translation remains manual')
  # Exercise network failure without locking the answer prematurely.
  context=browser.new_context(viewport={'width':390,'height':844});page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(URL);page.locator('#student-name').fill('Thử kết nối');page.locator('#start-form button').click();jump(page,'C · Câu 1')
  page.locator('input[value=B]').check();page.route('**/support.json',lambda r:r.fulfill(status=503,body='unavailable'))
  page.locator('#check-answer').click();expect(page.locator('#check-error')).to_contain_text('Bài làm vẫn được giữ nguyên')
  expect(page.locator('input[value=B]')).to_be_enabled();expect(page.locator('#feedback')).to_be_hidden()
  page.unroute('**/support.json');page.locator('#check-answer').click();expect(page.locator('#feedback')).to_contain_text('Đúng · Đáp án: B')
  context.close();passed('Failed evidence fetch does not lock answers or lose draft; retry works')
  context=browser.new_context(viewport={'width':390,'height':844});page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  held=[];support=json.loads((UNIT/'support.json').read_text())
  page.route('**/support.json',lambda r:held.append(r))
  page.goto(URL);page.locator('#student-name').fill('Chuyển câu nhanh');page.locator('#start-form button').click();jump(page,'C · Câu 1')
  page.locator('input[value=B]').check()
  with page.expect_request('**/support.json'):page.locator('#check-answer').click()
  page.locator('#next').click();page.locator('input[value=C]').check()
  assert len(held)==1;held[0].fulfill(json=support)
  expect(page.locator('#check-answer')).to_be_enabled();expect(page.locator('#feedback')).to_be_hidden()
  expect(page.locator('input[value=C]')).to_be_checked();expect(page.locator('input[value=C]')).to_be_enabled()
  page.locator('#previous').click();expect(page.locator('input[value=B]')).to_be_disabled();expect(page.locator('#feedback')).to_contain_text('Đúng · Đáp án: B')
  page.locator('#next').click();expect(page.locator('input[value=C]')).to_be_checked();expect(page.locator('#feedback')).to_be_hidden()
  context.close();passed('Navigation during delayed evidence loading checks only the original question and preserves the new question draft')
  assert not errors,errors;assert not bad,bad;assert not external,external
  (OUT/'report.json').write_text(json.dumps({'browser':args.name,'version':browser.version,'checks':checks,'errors':errors,'httpErrorsInNormalFlow':bad,'externalRequests':external},ensure_ascii=False,indent=2))
  browser.close()
finally:server.shutdown()
