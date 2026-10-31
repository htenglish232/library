"""Continuous document entry and legacy progress preservation in a real browser."""
from pathlib import Path
import argparse, functools, http.server, json, os, shutil, threading
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[2];UNIT=ROOT/'ielts-practice/unit-2-individuals-and-families'
unit=json.loads((UNIT/'unit.json').read_text());key=json.loads((UNIT/'answers.json').read_text())
parser=argparse.ArgumentParser();parser.add_argument('--browser-path',default=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'));parser.add_argument('--name',default='chromium');args=parser.parse_args()
OUT=Path('/tmp/ht-ielts-unit2')/args.name/'vocabulary';OUT.mkdir(parents=True,exist_ok=True)
checks,errors,bad,external=[],[],[],[]
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def translate_path(self,path):
  if path.startswith('/library/'):path=path[len('/library'):]
  return super().translate_path(path)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}'
URL=BASE+'/library/ielts-practice/unit-2-individuals-and-families/index.html'
STORE='ht-ielts:worksheet:v1:'+unit['id']
def passed(text):checks.append(text);print('PASS',args.name,text,flush=True)
def jump(page,label):
 if page.locator('#vocabulary-reading-top').is_visible():page.locator('#vocabulary-reading-top').click()
 page.locator('#step-picker').evaluate('e=>e.open=true');page.get_by_role('button',name=label,exact=True).click()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=args.browser_path,args=['--no-sandbox'])
  for width,height in [(1440,1000),(768,1024),(390,844),(375,812)]:
   context=browser.new_context(viewport={'width':width,'height':height})
   context.route('**/*',lambda r:r.continue_() if r.request.url.startswith(BASE+'/') else (external.append(r.request.url),r.abort())[-1])
   page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
   page.on('response',lambda r:bad.append([r.status,r.url]) if r.status>=400 else None)
   page.goto(URL);page.locator('#open-vocabulary').click()
   expect(page.locator('.passage-section')).to_have_count(10)
   expect(page.locator('#navigation')).to_be_hidden();expect(page.locator('.progress-line')).to_be_hidden();expect(page.locator('#step-picker')).to_be_hidden()
   assert page.locator('#vocabulary-document details,#vocabulary-document input,#vocabulary-document button').count()==0
   assert page.evaluate("getComputedStyle(document.body).backgroundColor")=='rgb(255, 255, 255)'
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
   assert page.locator('.passage-copy').all_text_contents()==[source['text'] for source in unit['passages']]
   for index,source in enumerate(unit['passages']):
    block=page.locator('.passage-section').nth(index)
    expect(block.locator('h3')).to_have_text(f"Passage {index+1}: {source['title']}")
    assert block.locator('li').all_text_contents()==[word['sourceText'] for word in source['vocabulary']]
   assert page.locator('#vocabulary-summary li').all_text_contents()==unit['vocabularySummary']
   page.locator('#vocabulary-summary li').last.scroll_into_view_if_needed();expect(page.locator('#vocabulary-summary li').last).to_be_in_viewport()
   stored=page.evaluate('(k)=>JSON.parse(localStorage.getItem(k))',STORE)
   assert stored['started'] is False and stored['name']=='' and all(not a for a in stored['answers']['mcq']+stored['answers']['summary'])
   page.evaluate('scrollTo(0,0)')
   if width in [1440,390]:page.screenshot(path=str(OUT/f'document-{width}.png'),full_page=True)
   page.reload();expect(page.locator('.passage-section')).to_have_count(10)
   page.locator('#vocabulary-reading').click();expect(page.locator('#welcome')).to_be_visible()
   page.locator('#student-name').fill('Người đọc tài liệu');page.locator('#start-form button').click()
   expect(page.locator('#reading-panel')).to_be_visible();expect(page.locator('#reading-text p')).to_have_count(5)
   page.locator('#previous').click();expect(page.locator('.passage-section')).to_have_count(10)
   page.locator('#vocabulary-overview').click();expect(page.locator('#welcome')).to_be_visible()
   context.close();passed(f'{width}px: open without name; all 10 passages/33 vocabulary entries/synonyms/33 Summary terms visible in one white document; no accordion, quiz, score or fixed game navigation; Reading handoff and reload work')
  context=browser.new_context(viewport={'width':390,'height':844});page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  old={'schema':1,'unit':unit['id'],'version':unit['version'],'name':'Bài lưu trước đây','started':True,'view':'work','step':14,'readingMark':2,'submittedAt':None,
       'checked':{'mcq':[False]*10,'summary':[False]*10},'answers':{'mcq':['']*10,'summary':['']*10,'translation':'My original saved translation.'}}
  old['answers']['mcq'][3]='C';old['checked']['mcq'][3]=True;old['answers']['summary'][3]='relationships'
  # Seed on the new document: pagehide autosave intentionally protects the
  # currently open page, so writing an external fixture before reload is stale.
  seed=json.dumps({'key':STORE,'value':old},ensure_ascii=False)
  page.add_init_script("(()=>{const s="+seed+";if(!sessionStorage.getItem('legacy-seeded')){localStorage.setItem(s.key,JSON.stringify(s.value));sessionStorage.setItem('legacy-seeded','1')}})()")
  page.goto(URL)
  expect(page.locator('#task-title')).to_have_text(unit['multipleChoice'][3]['question'])
  expect(page.locator('input[value=C]')).to_be_checked();expect(page.locator('input[value=C]')).to_be_disabled()
  jump(page,'E · Translation');expect(page.locator('#translation-input')).to_have_value(old['answers']['translation'])
  jump(page,'A · Vocabulary & Passages');page.reload();expect(page.locator('.passage-section')).to_have_count(10)
  jump(page,'C · Câu 4');expect(page.locator('input[value=C]')).to_be_checked();expect(page.locator('input[value=C]')).to_be_disabled()
  jump(page,'D · Summary');expect(page.locator('#blank-4')).to_have_value('relationships')
  old['view']='results';old['step']=22;old['submittedAt']='2026-10-31T00:00:00Z'
  old['answers']['mcq']=[q['answer'] for q in key['multipleChoice']];old['answers']['summary']=key['summary']
  seed=json.dumps({'key':STORE,'value':old},ensure_ascii=False)
  page.add_init_script("(()=>{const s="+seed+";if(!sessionStorage.getItem('submitted-seeded')){localStorage.setItem(s.key,JSON.stringify(s.value));sessionStorage.setItem('submitted-seeded','1')}})()")
  page.reload()
  expect(page.locator('#results')).to_be_visible();assert page.locator('#result-stats strong').all_text_contents()==['20','20','0','0']
  expect(page.locator('#result-translation')).to_have_text(old['answers']['translation'])
  context.close();passed('Existing 23-step saves keep the same MCQ, checked first answer, Summary draft, translation and submitted score after document navigation migration')
  assert not errors,errors;assert not bad,bad;assert not external,external
  (OUT/'report.json').write_text(json.dumps({'browser':args.name,'version':browser.version,'checks':checks,'errors':errors,'httpErrors':bad,'externalRequests':external},ensure_ascii=False,indent=2));browser.close()
finally:server.shutdown()
