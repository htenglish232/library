"""Upgrade actual pre-change model saves for every game; never contact Firebase."""
from pathlib import Path
from urllib.parse import quote
import functools,http.server,json,re,subprocess,threading
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
handler=(ROOT/'tests/dual-mode-browser.py').read_text().split('class Handler',1)[1].split('server=http.server',1)[0]
exec('class Handler'+handler)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}/library/'
fixtures=json.loads(subprocess.check_output(['node','tests/legacy-progress-fixtures.mjs'],cwd=ROOT,text=True))
assert len(fixtures)==49
errors=[];external=[];results=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for mobile in [False,True]:
   context=browser.new_context(viewport={'width':390 if mobile else 1280,'height':844},is_mobile=mobile,has_touch=mobile,reduced_motion='reduce')
   context.route('**/*',lambda r:r.continue_() if r.request.url.startswith(BASE.removesuffix('library/')) else (external.append(r.request.url),r.abort())[-1])
   page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('requestfailed',lambda req:errors.append(req.url+':'+str(req.failure)) if not req.url.endswith('.mp3') else None)
   for fixture in fixtures:
    path=fixture['path'].replace('practice-dual-data.js','practice-dual-mode.html').replace('truc-tuan-dual-data.js','truc-tuan-dual-mode.html')
    page.goto(BASE+quote(path))
    data=page.evaluate('HT_PRACTICE_DATA')
    for scenario in ['challenge','review','ordered','checkedReview']:
     raw=fixture['records'][scenario]
     key=page.evaluate('student=>HTDualStore.keyFor(HT_PRACTICE_DATA,student)',raw['student'])
     record={'schemaVersion':1,'examId':data['exam']['id'],'contentVersion':data['contentVersion'],'state':raw}
     # Write bytes produced by the frozen model before loading the new controller.
     page.evaluate('([key,record])=>localStorage.setItem(key,JSON.stringify(record))',[key,record])
     page.reload();page.locator('#student-name').fill(raw['student']['name'])
     if not page.locator('#student-code').is_visible():page.locator('.identity-options summary').click()
     page.locator('#student-code').fill(raw['student']['code']);page.locator('#start-form button').click()
     expect(page.locator('#resume-panel')).to_be_visible();page.locator('#resume-button').click()
     expect(page.locator('#play')).to_be_visible()
     expect(page.locator('#question-card')).to_have_attribute('data-question-id',raw['cursorId'])
     expect(page.locator('#xp-total')).to_have_text('✦ 10 XP')
     assert page.locator('.mode-options,#play-mode,#challenges,#back-menu,#section-tabs,#toggle-passage').count()==0
     saved=page.evaluate('key=>JSON.parse(localStorage.getItem(key)).state',key)
     assert saved['answers']==raw['answers'],(path,scenario,'answers changed')
     assert saved['reviewIds']==raw['reviewIds'] and saved['review']==raw['review']
     assert saved['mode']=='ordered'
     expected=[q for q in data['questions'] if not raw['review'] or q['id'] in raw['reviewIds']]
     assert page.locator('#question-dots button').evaluate_all('(els)=>els.map(e=>e.dataset.questionId)')==[q['id'] for q in expected]
     q=next(q for q in data['questions'] if q['id']==raw['cursorId'])
     a=raw['answers'][q['id']];draft=a['review']['draft'] if raw['review'] else a['first']['draft'] if a['first'] else a['draft']
     if q['kind']=='choice':expect(page.locator('#answer-area input:checked')).to_have_value(draft['value'])
     elif q['kind']=='text':expect(page.locator('#written-answer')).to_have_value(draft['value'])
     elif q['kind']=='multi-text':
      for i,value in enumerate(draft['fields']):expect(page.locator(f'#written-answer-{i}')).to_have_value(value)
     else:expect(page.locator('#word-target button')).to_have_count(len(draft['tokens']))
     # Confirm rereading and persisting the migrated record is stable.
     page.reload();page.locator('#start-form button').click();page.locator('#resume-button').click()
     assert page.evaluate('key=>JSON.parse(localStorage.getItem(key)).state.answers',key)==raw['answers']
    results.append({'game':path,'touch':mobile,'legacyScenarios':4,'result':'PASS'})
    print('PASS legacy saves',path,'touch' if mobile else 'desktop',flush=True)
   context.close()
  assert not errors,errors;assert not external,external
  Path('/tmp/full-exam-migration-browser.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
  print('PASS 49 games × 4 old-save scenarios × desktop/touch; no lost answers, drafts, cursor, review or XP; no external requests',flush=True)
  browser.close()
finally:server.shutdown()
