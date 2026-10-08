from pathlib import Path
from playwright.sync_api import sync_playwright
import json,re,sys
ROOT=Path(__file__).resolve().parents[3]; reports=[]
if '--grading-only' not in sys.argv:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for path in sorted(ROOT.glob('grade-7/De_thi_GHK_1/*/*.html'),key=lambda p:int(p.parent.name.split('_')[0])):
   page=browser.new_page(viewport={'width':960,'height':800}); errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto('http://127.0.0.1:8000/'+str(path.relative_to(ROOT)),wait_until='networkidle')
   d=page.locator('#examData').text_content();data=json.loads(d);qs=data['questions'];result={'page':path.parent.name,'questions':len(qs),'errors':errors,'chips':sum(q['kind']=='chips' for q in qs)}
   assert len(qs)==page.locator('.question-card').count(),(path,'cards')
   duplicate=page.evaluate("""() => {const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);return ids.filter((id,i)=>ids.indexOf(id)!==i)}""");assert not duplicate,(path,duplicate)
   assert page.locator('.feedback-box:visible,.status-indicator:visible,[data-transcript]:visible').count()==0,(path,'pre-submit leak')
   missing=page.evaluate("""() => [...document.querySelectorAll('[data-answer-field]')].filter(e=>!e.closest('.question-card')).map(e=>e.outerHTML)""");assert not missing,(path,missing)
   assert all(q['kind']=='chips' or page.locator('#question-'+q['id']+' [data-answer-field]').count() for q in qs),(path,'no fields')
   overflows=[]
   for width in [360,375,390,430]:
    page.set_viewport_size({'width':width,'height':850});page.wait_for_timeout(50)
    detail=page.evaluate("""() => {const w=document.documentElement.clientWidth;return [...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>w+1 && getComputedStyle(e).display!=='none' && !e.closest('[hidden],dialog:not([open])')).slice(0,5).map(e=>({tag:e.tagName,cls:e.className,right:e.getBoundingClientRect().right}));}""")
    if detail:overflows.append([width,detail])
   assert not overflows,(path,overflows)
   result['overflow']=overflows
   # Each chip supports removal, undo and reset. Duplicate tokens remain independent.
   for q in qs:
    if q['kind']!='chips':continue
    card=page.locator('#question-'+q['id']);bank=card.locator('.bank-chip')
    bank.nth(0).click();assert card.locator('.selected-chip').count()==1
    bank.nth(1).click();assert card.locator('.selected-chip').count()==2
    card.locator('.selected-chip').nth(0).click();assert card.locator('.selected-chip').count()==1
    card.locator('[data-action=undo]').click();assert card.locator('.selected-chip').count()==0
    bank.nth(0).click();card.locator('[data-action=reset]').click();assert card.locator('.selected-chip').count()==0
    assert bank.evaluate_all('(chips)=>chips.every(chip=>!chip.disabled)')
    duplicate_tokens=[t for t in q['tokens'] if q['tokens'].count(t)>1]
    if duplicate_tokens:
     indexes=[i for i,t in enumerate(q['tokens']) if t==duplicate_tokens[0]]
     bank.nth(indexes[0]).click();assert bank.nth(indexes[1]).is_enabled();card.locator('[data-action=reset]').click()
   choice=next(q for q in qs if q['kind']=='choice');page.locator('#question-'+choice['id']+' input').first.check()
   text=next((q for q in qs if q['kind']=='text'),None)
   if text:page.locator('#question-'+text['id']+' [data-answer-field]').first.fill('test')
   page.locator('#submitBtn').click();assert page.locator('#confirmModal').is_visible();assert page.locator('.feedback-box:visible').count()==0
   for width in [360,375,390,430]:
    page.set_viewport_size({'width':width,'height':850});assert page.locator('#confirmModal').evaluate('(e)=>{const r=e.getBoundingClientRect();return r.left>=0 && r.right<=innerWidth && r.top>=0 && r.bottom<=innerHeight}'),(path,'modal overflow')
   page.locator('#continueExam').click();assert not page.locator('#confirmModal').is_visible();assert page.locator('#submitBtn').is_enabled()
   # Submit mostly blank: verify wrong/unanswered feedback and full lock, including chips.
   page.locator('#submitBtn').click();page.locator('#confirmSubmit').click()
   assert page.locator('.feedback-box:visible').count()==len(qs),(path,'feedback')
   assert page.locator('.status-indicator:visible').count()==len(qs),(path,'status')
   assert page.locator('.student-info input:enabled,[data-answer-field]:enabled,.word-chip:enabled,.chip-actions button:enabled').count()==0,(path,'lock')
   assert page.locator('#submissionBanner').is_visible();assert page.locator('#submitBtn').is_disabled()
   if page.locator('.transcript-toggle').count():
    page.locator('.transcript-toggle').first.click();assert not page.locator('[data-transcript]').first.is_visible();page.locator('.transcript-toggle').first.click();assert page.locator('[data-transcript]').first.is_visible()
   for width in [360,375,390,430]:
    page.set_viewport_size({'width':width,'height':850})
    if page.evaluate('document.documentElement.scrollWidth > innerWidth + 1'):result['overflow'].append([width,'post-submit'])
   assert not result['overflow'],(path,result['overflow'])
   assert not errors,(path,errors)
   result['blankScore']=page.locator('#examResults').inner_text();reports.append(result);print(json.dumps(result,ensure_ascii=False),flush=True);page.close()
  browser.close()
 print('UI, chip controls, submission, feedback, transcript and mobile checks passed for all 14 exams.')
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,re
ROOT=Path(__file__).resolve().parents[3]
def norm(t):return re.sub(r"[.,?!'’]", '',t.lower()).strip()
def order(tokens,target):
 target=norm(target)
 def dfs(prefix,left):
  if not left:return prefix if target==norm(' '.join(tokens[i] for i in prefix)) else None
  for i in left:
   test=norm(' '.join(tokens[j] for j in prefix+[i]))
   if target==test or target.startswith(test+' '):
    result=dfs(prefix+[i],[j for j in left if j!=i])
    if result is not None:return result
  return None
 return dfs([],list(range(len(tokens))))
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 reports=[]
 for path in sorted(ROOT.glob('grade-7/De_thi_GHK_1/*/*.html'),key=lambda p:int(p.parent.name.split('_')[0])):
  page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8000/'+str(path.relative_to(ROOT)),wait_until='networkidle');data=json.loads(page.locator('#examData').text_content());unbuildable=[]
  for q in data['questions']:
   card=page.locator('#question-'+q['id'])
   if q['kind']=='choice':
    card.locator(f'input[value="{q["accepted"][0]}"]').check()
   elif q['kind']=='text':
    if q.get('parts'):
     for i,answers in enumerate(q['parts']):card.locator('[data-answer-field]').nth(i).fill(answers[0])
    else:card.locator('[data-answer-field]').first.fill(q['accepted'][0] if q['accepted'] else q['display'])
   else:
    found=None
    for target in q['accepted']:
     found=order(q['tokens'],target)
     if found is not None:break
    if found is None:unbuildable.append([q['id'],q['tokens'],q['accepted']]);continue
    for i in found:card.locator(f'.bank-chip[data-token-index="{i}"]').click()
  page.locator('#submitBtn').click();modaltext=page.locator('#confirmMessage').inner_text();page.locator('#confirmSubmit').click()
  wrong=page.locator('.answer-wrong').evaluate_all('(els)=>els.map(e=>({id:e.id,feedback:e.querySelector(".feedback-box").textContent}))')
  assert not unbuildable,(path,unbuildable)
  assert not wrong,(path,wrong)
  assert not errors,(path,errors)
  assert '10.0 / 10' in page.locator('#examResults').inner_text(),path
  assert 'chưa hoàn thành' not in modaltext,(path,modaltext)
  result={'page':path.parent.name,'score':page.locator('#examResults').inner_text(),'wrong':wrong,'unbuildable':unbuildable,'modal':modaltext,'errors':errors};reports.append(result);print(json.dumps(result,ensure_ascii=False),flush=True);page.close()
 browser.close();print('Full-score grading passed for all 14 exams.')

# Speech must read only the literal displayed option, and never select a radio.
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for path in ROOT.glob('grade-7/De_thi_GHK_1/*/*.html'):
  page=browser.new_page()
  page.add_init_script("window.__spoken=[];speechSynthesis.speak=u=>window.__spoken.push(u.text);speechSynthesis.cancel=()=>{};")
  page.goto('http://127.0.0.1:8000/'+str(path.relative_to(ROOT)),wait_until='networkidle')
  buttons=page.locator('.neutral-speaker')
  expected=buttons.evaluate_all('(buttons)=>buttons.map(button=>button.dataset.speechText)')
  for button in buttons.all():button.click()
  assert page.evaluate('window.__spoken')==expected,path
  assert page.locator('input[type=radio]:checked').count()==0,path
  assert page.locator('[data-transcript]:visible,.feedback-box:visible').count()==0,path
  assert page.locator('.listening-player:visible').count()==page.locator('audio').count(),path
  page.locator('#submitBtn').click();page.locator('#confirmSubmit').click()
  if buttons.count():
   assert buttons.first.is_enabled(),path
   buttons.first.click();assert page.evaluate('window.__spoken.at(-1)')==expected[0],path
  page.close()
 browser.close()
print('Neutral TTS text, radio isolation and post-submission review controls passed for all 14 exams.')
