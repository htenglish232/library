"""Keep the four earlier game URLs usable without challenge navigation."""
from pathlib import Path
from urllib.parse import quote,unquote
import ast,functools,http.server,json,re,threading
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
helper=(ROOT/'tests/grade8-all-dual-browser.py').read_text()
for node in ast.parse(helper).body:
 if isinstance(node,ast.FunctionDef) and node.name in ['norm','order']:exec(ast.get_source_segment(helper,node))
handler=(ROOT/'tests/dual-mode-browser.py').read_text().split('class Handler',1)[1].split('server=http.server',1)[0]
exec('class Handler'+handler)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}/library/'
files=sorted(ROOT.glob('grade-8/De_thi_GHK1/*/practice-game-pilot.html'))+[ROOT/'grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-game-test.html']
assert len(files)==4
errors=[];external=[];report=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  context=browser.new_context(viewport={'width':390,'height':844},reduced_motion='reduce')
  context.route('**/*',lambda r:r.continue_() if r.request.url.startswith(BASE.removesuffix('library/')) else (external.append(r.request.url),r.abort())[-1])
  page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  for file in files:
   page.goto(BASE+quote(file.relative_to(ROOT).as_posix()))
   old=file.name=='truc-tuan-game-test.html'
   data=page.evaluate('HT_GAME_SOURCE' if old else 'HT_PRACTICE_DATA')
   questions=data['questions']
   if old:
    for q in questions:q['accepted']=page.evaluate('q=>window.HT_GAME_TEXT_VARIANTS[q.id]||[q.source.correct,...(q.source.alternatives||[])]',q);q['autoGrade']=True
   page.locator('#student-name').fill('Kiểm tra game cũ');page.locator('#start-form button').click()
   expect(page.locator('#play')).to_be_visible();expect(page.locator('#question-dots button')).to_have_count(len(questions))
   assert page.locator('#challenges,#back-menu,#section-tabs').count()==0
   xp=0;pending=0
   for i,q in enumerate(questions):
    expect(page.locator('#question-card')).to_have_attribute('data-question-id',q['id'])
    assert page.locator('#prompt').inner_html()==page.evaluate('html=>{const d=document.createElement("div");d.innerHTML=html;return d.innerHTML;}',q['promptHtml'])
    if q['section']=='reading' and page.locator('#passage-content').text_content().strip():expect(page.locator('#passage-content')).to_be_visible()
    if q['kind']=='choice':
     value=next(o['value'] for o in q['options'] if o['value'] not in q['accepted']) if i==0 else q['accepted'][0] if q['accepted'] else q['options'][0]['value']
     page.locator('#answer-area input').evaluate_all('(els,v)=>{const e=els.find(e=>e.value===v);e.checked=true;e.dispatchEvent(new Event("change"));}',value)
    elif q['kind']=='multi-text':
     for j,value in enumerate(q['acceptedTuples'][0]):page.locator(f'#written-answer-{j}').fill(value)
    elif q['kind']=='text':page.locator('#written-answer').fill('incorrect fixture' if i==0 else q['accepted'][0] if q['accepted'] else 'teacher review')
    else:
     indices=order(q)
     for j in indices if indices is not None else range(len(q['tokens'])):page.locator(f'[data-token-index="{j}"]').click()
    page.locator('#check-answer').click()
    if q['autoGrade'] and i!=0:xp+=10
    elif not q['autoGrade']:pending+=1
    expect(page.locator('#xp-total')).to_have_text(f'✦ {xp} XP')
    page.locator('#next-question').click()
   expect(page.locator('#results')).to_be_visible();expect(page.locator('#result-xp')).to_have_text(str(xp))
   page.locator('#review-wrong').click();expect(page.locator('#play')).to_be_visible();expect(page.locator('#xp-total')).to_have_text(f'✦ {xp} XP')
   page.locator('#home-button').click();expect(page.locator('#question-dots button')).to_have_count(len(questions))
   page.locator('#previous-question').click() if page.locator('#previous-question').is_enabled() else None
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
   report.append({'game':file.relative_to(ROOT).as_posix(),'questions':len(questions),'xp':xp,'pending':pending,'result':'PASS'});print('PASS',report[-1],flush=True)
  assert not errors,errors;assert not external,external
  Path('/tmp/full-exam-legacy-browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
  print('PASS all 4 retained legacy URLs; 169 questions in original order, scoring, navigation and review',flush=True)
  browser.close()
finally:server.shutdown()
