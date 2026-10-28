from practice_browser_controls import control
"""Play every source question through the shared dual controller under /library/."""
from pathlib import Path
import argparse,functools,http.server,json,os,re,threading
from urllib.parse import quote,unquote
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--pilots',action='store_true');parser.add_argument('--folders',help='Comma separated original folder numbers for targeted checks');args=parser.parse_args()
# Reuse only the tested range-serving handler, without running the reference suite.
handler_source=(ROOT/'tests/dual-mode-browser.py').read_text().split('class Handler',1)[1].split('server=http.server',1)[0]
exec('class Handler'+handler_source)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}/'
def norm(s):return re.sub(r'\s+',' ',re.sub(r'[.,!?;:]','',s.lower().replace('’',"'").replace('‘',"'"))).strip()
def order(q):
 for accepted in q['accepted']:
  def solve(indices,left):
   if len(indices)==len(q['tokens']):return indices if not left else None
   for i,t in enumerate(q['tokens']):
    part=norm(t).split()
    if i not in indices and left[:len(part)]==part:
     found=solve(indices+[i],left[len(part):])
     if found is not None:return found
  found=solve([],norm(accepted).split())
  if found is not None:return found
 return None
errors=[];external=[];bad=[];report=[]
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
  ctx=b.new_context(viewport={'width':390,'height':844},reduced_motion='reduce')
  ctx.route('**/*',lambda r:r.continue_() if r.request.url.startswith(BASE) else (external.append(r.request.url),r.abort())[-1])
  page=ctx.new_page();page.set_default_timeout(12000)
  page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
  page.on('response',lambda r:bad.append((r.status,r.url)) if r.status>=400 else None)
  files=list(ROOT.glob('grade-8/De_thi_GHK1/*/practice-dual-mode.html'))
  if args.pilots:files=[f for f in files if f.parent.name.startswith(('11_','12_','19_'))]
  else:files.insert(0,ROOT/'grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-dual-mode.html')
  if args.folders:files=[f for f in files if f.parent.name.split('_')[0] in args.folders.split(',')]
  expected=len(args.folders.split(',')) if args.folders else 3 if args.pilots else 19;assert len(files)==expected,(len(files),expected)
  saved={};total=0
  for idx,file in enumerate(files):
   url=BASE+'library/'+quote(file.relative_to(ROOT).as_posix());page.goto(url)
   minimal=page.locator('html[data-minimal-ui]').count()>0
   data=page.evaluate('HT_PRACTICE_DATA');qs=data['questions'];assert page.evaluate('HTPracticeModel.validate(HT_PRACTICE_DATA)')
   if idx==0:
    page.locator('#student-name').fill('Học sinh cùng tên');page.locator('.identity-options summary').click();page.locator('#student-code').fill('8A-01')
   else:
    expect(page.locator('#student-name')).to_have_value('Học sinh cùng tên');expect(page.locator('#student-code')).to_have_value('8A-01')
   page.locator('#start-form button').click();expect(page.locator('#play')).to_be_visible()
   expect(page.locator('#question-dots button')).to_have_count(len(qs));assert page.locator('.mode-options,#play-mode,#challenges,#section-tabs,#toggle-passage').count()==0;xp=0;pending=0;played_tracks=set()
   for q in qs:
    control(page,'#jump-question').select_option(q['id']);expect(page.locator('#question-card')).to_have_attribute('data-question-id',q['id'])
    assert page.locator('#prompt').inner_html()==page.evaluate('(html)=>{const d=document.createElement("div");d.innerHTML=html;return d.innerHTML;}',q['promptHtml']),(file,q['id'])
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(file,q['id'],'mobile overflow')
    if not minimal and q.get('context') is not None:assert page.locator('#passage-content').inner_html()==data['contexts'][q['context']]
    if not minimal and q.get('contextHtml'):assert page.locator('#passage-content').inner_html()==q['contextHtml']
    if not minimal and page.locator('#passage-content').text_content().strip() and (q.get('contextHtml') or (data['contexts'][q['context']] if q.get('context') is not None else '')):expect(page.locator('#passage-content')).to_be_visible()
    if q.get('track') and q['track'] not in played_tracks:
     page.wait_for_function('document.querySelector("audio").readyState>=1')
     track=next(t for t in data['tracks'] if t['id']==q['track']);assert unquote(page.locator('audio').evaluate('e=>new URL(e.currentSrc).pathname')).endswith(track['src'])
     page.locator('#audio-toggle').click();page.wait_for_function('!document.querySelector("audio").paused');page.locator('#audio-toggle').click()
     page.locator('audio').evaluate('e=>e.currentTime=10');page.locator('#audio-forward').click();assert abs(page.locator('audio').evaluate('e=>e.currentTime')-15)<1
     page.locator('#audio-back').click();assert abs(page.locator('audio').evaluate('e=>e.currentTime')-10)<1
     page.locator('#audio-speed').select_option('1.25');assert page.locator('audio').evaluate('e=>e.playbackRate')==1.25
     played_tracks.add(q['track'])
    elif not q.get('track'):expect(page.locator('#audio-panel')).to_be_hidden()
    if q['kind']=='choice':
     assert page.locator('#answer-area input').evaluate_all('(els)=>els.map(e=>e.value)')==[o['value'] for o in q['options']]
     value=q['accepted'][0] if q['accepted'] else q['options'][0]['value'];None
     page.locator('#answer-area input').evaluate_all('(els,v)=>{const e=els.find(e=>e.value===v);e.checked=true;e.dispatchEvent(new Event("change"));}',value)
    elif q['kind']=='multi-text':
     for i,value in enumerate(q['acceptedTuples'][0]):page.locator(f'#written-answer-{i}').fill(value)
    elif q['kind']=='text':page.locator('#written-answer').fill(q['accepted'][0] if q['accepted'] else 'Đáp án chờ giáo viên')
    else:
     indices=order(q)
     if q['autoGrade']:assert indices is not None,('Unreachable source answer',file,q['id'])
     for i in indices if indices is not None else range(len(q['tokens'])):page.locator(f'[data-token-index="{i}"]').click()
    # Draft and cursor survive results/continue navigation.
    control(page,'#results-button').click();page.locator('#continue-playing').click()
    page.locator('#check-answer').click();expect(page.locator('#feedback')).to_be_visible()
    if q['autoGrade']:xp+=10
    else:pending+=1
    expect(page.locator('#xp-total')).to_have_text(f'✦ {xp} XP')
    page.evaluate('document.querySelector("#check-answer").click()');expect(page.locator('#xp-total')).to_have_text(f'✦ {xp} XP')
    if q.get('transcriptHtml'):expect(page.locator('#transcript-panel')).to_be_visible()
    if q.get('track'):
     track=next(t for t in data['tracks'] if t['id']==q['track'])
     if track.get('transcriptHtml'):expect(page.locator('#transcript-panel')).to_be_visible()
    total+=1
   control(page,'#results-button').click();expect(page.locator('#result-total')).to_have_text(str(len(qs)));expect(page.locator('#result-xp')).to_have_text(str(xp));expect(page.locator('#result-pending')).to_have_text(str(pending))
   key=page.evaluate('HTDualStore.keyFor(HT_PRACTICE_DATA,{name:"Học sinh cùng tên",code:"8A-01"})');raw=page.evaluate('(key)=>localStorage.getItem(key)',key);saved[key]=raw
   page.reload();expect(page.locator('#student-code')).to_have_value('8A-01');page.locator('#start-form button').click();page.locator('#resume-button').click();expect(page.locator('#xp-total')).to_have_text(f'✦ {xp} XP')
   expect(page.locator('#question-card')).to_have_attribute('data-question-id',qs[-1]['id'])
   # Same name, different code is an independent student, then return to A.
   control(page,'#change-student').click();expect(page.locator('#student-name')).to_have_value('');page.locator('#student-name').fill('Học sinh cùng tên')
   if not page.locator('#student-code').is_visible():page.locator('.identity-options summary').click()
   page.locator('#student-code').fill('8A-02');page.locator('#start-form button').click();expect(page.locator('#xp-total')).to_have_text('✦ 0 XP')
   control(page,'#restart-button').click();page.locator('#cancel-restart').click();control(page,'#restart-button').click();page.locator('#confirm-restart').click();expect(page.locator('#xp-total')).to_have_text('✦ 0 XP')
   assert page.evaluate('(key)=>JSON.parse(localStorage.getItem(key)).state.answers',key)==json.loads(raw)['state']['answers']
   control(page,'#change-student').click();page.locator('#student-name').fill('Học sinh cùng tên');page.locator('#student-code').fill('8A-01');page.locator('#start-form button').click();page.locator('#resume-button').click()
   for prior,record in saved.items():assert page.evaluate('(key)=>JSON.parse(localStorage.getItem(key)).state.answers',prior)==json.loads(record)['state']['answers']
   report.append({'school':data['exam']['school'],'exam':data['exam'].get('number',1),'questions':len(qs),'xp':xp,'pending':pending,'audio':len(played_tracks),'result':'PASS'})
   print('PASS',report[-1],flush=True)
  assert not errors,errors;assert not external,external;assert not bad,bad
  print(f'PASS {expected} games / {total} questions; mobile, full-exam navigation, source content, audio, XP, resume, remembered identity/code, student isolation, reset; no JS/network/resource errors.',flush=True)
  out=Path(os.environ.get('GRADE8_DUAL_REPORT','/tmp/grade8-all-dual-browser.json'));out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
  ctx.close();b.close()
finally:server.shutdown()
