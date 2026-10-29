"""All games × required viewports; phone input and keyboard geometry are emulated."""
from pathlib import Path
from urllib.parse import quote,unquote
import argparse,functools,http.server,json,os,re,threading
from playwright.sync_api import sync_playwright,expect
from practice_browser_controls import control,assert_context
ROOT=Path(__file__).resolve().parents[1];OUT=Path('/tmp/all-minimal');OUT.mkdir(exist_ok=True)
parser=argparse.ArgumentParser();parser.add_argument('--widths',default='375,390,360,412,768,1280,1440');args=parser.parse_args();widths=[int(n) for n in args.widths.split(',')]
rows=json.loads((ROOT/'docs/minimal-exam-ui/inventory.json').read_text())['inventory'];assert len(rows)==53
handler=(ROOT/'tests/dual-mode-browser.py').read_text().split('class Handler',1)[1].split('server=http.server',1)[0];exec('class Handler'+handler)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}/';URL=BASE+'library/'
errors=[];bad=[];external=[];report=[]
samples={6:'grade-6/De_thi_GHK_1/3_THCS_Truc_Tuan/practice-dual-mode.html',7:'grade-7/De_thi_GHK_1/1_THCS_Truc_Thai/practice-dual-mode.html',8:'grade-8/De_thi_GHK1/6_THCS Cat Thanh/practice-dual-mode.html'}
def start(page):
 page.locator('#student-name').fill('Học sinh thử nghiệm');page.locator('#start-form button').click()
 if page.locator('#resume-panel').count() and page.locator('#resume-panel').is_visible():page.locator('#resume-button').click()
 expect(page.locator('#play')).to_be_visible();page.wait_for_timeout(20)
def jump(page,id):
 control(page,'#jump-question').select_option(id);expect(page.locator('#question-card')).to_have_attribute('data-question-id',id);page.wait_for_timeout(25)
 expect(page.locator('#minimal-question-list')).not_to_have_attribute('open','')
def bar(page):
 assert page.locator('.question-navigation:visible').count()==1
 g=page.locator('.question-navigation').evaluate('e=>{const r=e.getBoundingClientRect();return {top:r.top,bottom:r.bottom,h:r.height,innerHeight};}')
 assert abs(g['bottom']-g['innerHeight'])<2 and g['top']>=0,g
 assert page.locator('#previous-question').bounding_box()['height']>=44 and page.locator('#next-question').bounding_box()['height']>=44
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 return g
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width in widths:
   height={375:812,390:844,360:800,412:915,768:1024,1280:900,1440:1000}[width];mobile=width<1000
   ctx=browser.new_context(viewport={'width':width,'height':height},is_mobile=mobile,has_touch=mobile,reduced_motion='reduce')
   ctx.route('**/*',lambda r:r.continue_() if r.request.url.startswith(BASE) else (external.append(r.request.url),r.abort())[-1])
   page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:bad.append((r.status,r.url)) if r.status>=400 else None)
   for row in rows:
    page.goto(URL+quote(row['game']));page.wait_for_selector('html[data-minimal-ready="true"]',state='attached');start(page)
    data=page.evaluate('window.HT_PRACTICE_DATA||window.HT_GAME_SOURCE');qs=data['questions']
    expect(page.locator('#question-card')).to_have_attribute('data-question-id',qs[0]['id']);expect(page.locator('#previous-question')).to_be_disabled();expect(page.locator('#xp-total')).to_have_text('✦ 0 XP')
    expect(page.locator('#question-dots')).to_be_hidden();expect(page.locator('#jump-question')).to_be_hidden();assert page.locator('#prompt').bounding_box()['y']<height*.45,(row['game'],width,page.locator('#prompt').bounding_box())
    assert page.evaluate('scrollY')==0,'Compact layout must not rely on scrolling to hide its header'
    assert page.locator('audio').evaluate('e=>e.paused'),row['game'];bar(page)
    if row['game']==samples[row['grade']] and width in [390,1440]:page.screenshot(path=str(OUT/(f'after-grade{row["grade"]}-'+('mobile' if width==390 else 'desktop')+'.png')))
    # Native details supports keyboard open/close; no state/XP changes.
    summary=page.locator('#minimal-question-list>summary');summary.focus();summary.press('Enter');expect(page.locator('#question-dots')).to_be_visible();summary.press('Enter');expect(page.locator('#question-dots')).to_be_hidden()
    jump(page,qs[-1]['id']);expect(page.locator('#next-question')).to_contain_text('Tổng kết');page.locator('#next-question').click();expect(page.locator('#results')).to_be_visible();expect(page.locator('#result-xp')).to_have_text('0')
    page.locator('#continue-playing').click();expect(page.locator('#question-card')).to_have_attribute('data-question-id',qs[-1]['id'])
    page.locator('#previous-question').click();expect(page.locator('#question-card')).to_have_attribute('data-question-id',qs[-2]['id']);page.locator('#next-question').click();expect(page.locator('#question-card')).to_have_attribute('data-question-id',qs[-1]['id'])
    reading_id=next(iter(row['readingEvidence']));q=next(q for q in qs if q['id']==reading_id);jump(page,reading_id);assert_context(page,q,data)
    if width>800:assert page.locator('#passage-panel').bounding_box()['x']<page.locator('#question-card').bounding_box()['x']
    else:assert page.locator('#passage-panel').bounding_box()['y']<page.locator('#question-card').bounding_box()['y']
    page.evaluate('scrollTo(0,document.body.scrollHeight)');g=bar(page);assert page.locator('#question-layout').evaluate('e=>e.getBoundingClientRect().bottom')<=g['top']+2,(row['game'],width,'end content hidden')
    if row['game']==samples[row['grade']] and width in [390,1440]:
     jump(page,reading_id);page.screenshot(path=str(OUT/(f'after-reading-grade{row["grade"]}-'+('mobile' if width==390 else 'desktop')+'.png')))
    writing=next((q for q in reversed(qs) if q['kind'] in ['text','multi-text']),None)
    keyboard='source has no editable text question';persistent=page.evaluate('typeof HTDualStore!=="undefined"')
    if writing:
     jump(page,writing['id']);field=page.locator('#answer-area textarea').first;field.fill('Bản nháp Writing được giữ');field.focus()
     if width<1000:
      page.evaluate('''()=>{window.realViewport=visualViewport;Object.defineProperty(window,'visualViewport',{value:{height:innerHeight-320,offsetTop:20},configurable:true});realViewport.dispatchEvent(new Event('resize'));}''');page.wait_for_timeout(50)
      r=field.bounding_box();top=page.locator('.question-navigation').bounding_box()['y'];assert r['y']>=20 and r['y']+r['height']<=top-8,(row['game'],width,r,top)
      page.evaluate('''()=>{Object.defineProperty(window,'visualViewport',{value:realViewport,configurable:true});window.dispatchEvent(new Event('resize'));}''');page.wait_for_timeout(20);keyboard='visual viewport shrink/pan PASS'
     if persistent and width==390:
      answers=page.evaluate('JSON.parse(localStorage.getItem(HTDualStore.keyFor(HT_PRACTICE_DATA,{name:"Học sinh thử nghiệm",code:""}))).state.answers')
      page.reload();page.wait_for_selector('html[data-minimal-ready="true"]',state='attached');start(page);expect(page.locator('#question-card')).to_have_attribute('data-question-id',writing['id']);expect(page.locator('#answer-area textarea').first).to_have_value('Bản nháp Writing được giữ')
      assert page.evaluate('JSON.parse(localStorage.getItem(HTDualStore.keyFor(HT_PRACTICE_DATA,{name:"Học sinh thử nghiệm",code:""}))).state.answers')==answers
    expect(page.locator('#xp-total')).to_have_text('✦ 0 XP')
    report.append({'game':row['game'],'width':width,'result':'PASS','keyboard':keyboard,'persistentStorage':persistent});print('PASS',width,row['game'],flush=True)
   ctx.close()
  assert not errors,errors;assert not bad,bad;assert not external,external
  (OUT/('smoke-'+args.widths.replace(',','-')+'.json')).write_text(json.dumps({'cases':report,'errors':errors,'bad':bad,'external':external,'physicalDevices':False},ensure_ascii=False,indent=2)+'\n');print(f'PASS {len(report)} game/viewport cases; all grids closed, one fixed bar, first questions early without initial auto-scroll, source Reading/keyboard/progress preserved',flush=True);browser.close()
finally:server.shutdown()
