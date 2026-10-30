"""Real Fullscreen API + full-motion/reduced-motion checks in a chosen browser."""
from pathlib import Path
import argparse, functools, http.server, json, os, shutil, threading, time
from playwright.sync_api import sync_playwright, expect

parser=argparse.ArgumentParser()
parser.add_argument('--browser-path',default=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'))
parser.add_argument('--name',default='chromium')
args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[2]
OUT=Path('/tmp/ht-speaking-presentation')/args.name;OUT.mkdir(parents=True,exist_ok=True)
SOURCE=json.loads((ROOT/'test-speaking/data/global3-unit5/unit5_speaking_cards.json').read_text())
CARDS={card['id']:card for card in SOURCE['cards']}
checks,errors,external=[],[],[]
class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
    def translate_path(self,path):
        if path.startswith('/library/'):path=path[len('/library'):]
        return super().translate_path(path)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}'
def passed(text):checks.append(text);print('PASS',args.name,text,flush=True)
def id(page):return page.locator('#speaking-card').get_attribute('data-card-id')
def settled(page):expect(page.locator('#card-stage')).to_have_attribute('aria-busy','false')
def next_card(page):page.locator('#next-card').click();settled(page)
def enter(page):
    page.locator('#fullscreen').click()
    page.wait_for_function('document.fullscreenElement?.id === "presentation"')
    expect(page.locator('#exit-fullscreen')).to_be_visible()
def exit(page):
    page.locator('#exit-fullscreen').click();page.wait_for_function('!document.fullscreenElement')
def geometry(page):
    g=page.evaluate('''()=>{
      const rect=id=>{const r=document.getElementById(id).getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,bottom:r.bottom}};
      const p=document.getElementById('presentation'),b=document.querySelector('.question-body');
      return {frame:rect('presentation'),card:rect('speaking-card'),image:rect('question-image'),question:rect('question'),nav:document.querySelector('.player-nav').getBoundingClientRect().toJSON(),sw:p.scrollWidth,cw:p.clientWidth,sh:p.scrollHeight,ch:p.clientHeight,textScroll:b.scrollHeight,textHeight:b.clientHeight,fit:getComputedStyle(document.getElementById('question-image')).objectFit,w:innerWidth,h:innerHeight};
    }''')
    assert g['frame']['x']==0 and g['frame']['y']==0,g
    assert abs(g['frame']['h']-g['h'])<2 and abs(g['frame']['w']-g['w'])<2,g
    assert g['card']['bottom']<=g['nav']['y']+1,g
    assert g['image']['bottom']<=g['nav']['y']+1,g
    assert g['question']['bottom']<=g['nav']['y']+1,g
    assert abs(g['nav']['bottom']-g['h'])<2,g
    assert g['sw']<=g['cw']+1 and g['sh']<=g['ch']+1,g
    assert g['fit']=='contain',g
    assert page.locator('#presentation .site-header,#presentation .session-options,#presentation footer').count()==0
    return g

try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=args.browser_path,args=['--no-sandbox'])
        version=browser.version
        context=browser.new_context(viewport={'width':1920,'height':1080},reduced_motion='no-preference')
        context.add_init_script("""window.speechCalls=[];window.cancels=0;window.micRequests=0;
Object.defineProperty(window,'speechSynthesis',{value:{cancel(){cancels++},getVoices(){return [{lang:'en-US'}]},speak(u){speechCalls.push(u.text)}}});
window.SpeechSynthesisUtterance=class{constructor(text){this.text=text}};
navigator.mediaDevices.getUserMedia=()=>{micRequests++;throw Error('No microphone')};""")
        context.route('**/*',lambda r:r.continue_() if r.request.url.startswith(BASE+'/') else (external.append(r.request.url),r.abort())[-1])
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE+'/library/test-speaking/index.html#grade=Grade+3&textbook=Global+Success&unit=Unit+5')
        page.get_by_role('button',name='Practice →',exact=True).click()
        page.evaluate('document.fonts.ready')
        assert page.evaluate('document.fonts.check(\'700 32px "Noto Sans"\',"Tiếng Việt")')
        assert page.evaluate('[...document.fonts].some(font=>font.family.includes("Noto Sans") && font.status === "loaded")')
        expect(page.locator('#answer-panel')).to_be_visible();expect(page.locator('#toggle-answer')).to_be_hidden()
        page.locator('#play-audio').click()
        before=page.evaluate('cancels');started=time.monotonic()
        state=page.evaluate("""()=>{
          for(let i=0;i<12;i++)document.getElementById('next-card').click();
          const card=document.getElementById('speaking-card'),animation=card.getAnimations()[0];
          return {id:card.dataset.cardId,busy:document.getElementById('card-stage').getAttribute('aria-busy'),disabled:document.getElementById('next-card').disabled,duration:animation.effect.getTiming().duration,frames:animation.effect.getKeyframes().map(frame=>frame.transform)};
        }""")
        assert state=={'id':'unit5-card-01','busy':'true','disabled':True,'duration':260,'frames':['rotateY(0deg)','rotateY(-90deg)']},state
        settled(page)
        assert time.monotonic()-started>=.45
        assert id(page)=='unit5-card-02'
        assert page.evaluate('speechCalls')==[SOURCE['cards'][0]['question']]
        assert page.evaluate('cancels')>before
        expect(page.locator('#answer-panel')).to_be_visible()
        page.locator('#question').focus();page.keyboard.press('a');expect(page.locator('#answer-panel')).to_be_visible()
        for _ in range(8):next_card(page)
        expect(page.locator('#sample-answer')).to_have_text('She likes swimming.')
        page.screenshot(path=str(OUT/'practice.png'),full_page=True)
        passed('Noto Sans local font; Practice always shows supplied answer; 520ms turn blocks repeated Next and stops speech without autoplay')

        for width,height in [(1920,1080),(1366,768),(390,844)]:
            page.set_viewport_size({'width':width,'height':height});enter(page)
            g=geometry(page)
            assert g['textScroll']<=g['textHeight']+2,g
            if width>height:assert g['image']['x']<g['question']['x']
            else:assert g['image']['y']<g['question']['y']
            page.screenshot(path=str(OUT/f'fullscreen-practice-{width}.png'))
            old=id(page)
            page.locator('#next-card').focus();page.keyboard.press('ArrowRight');settled(page)
            assert id(page)!=old
            page.keyboard.press('ArrowLeft');settled(page);assert id(page)==old
            expect(page.locator('#answer-panel')).to_be_visible();geometry(page)
            exit(page)
        passed('Real container fullscreen at 1920×1080, 1366×768 and portrait; large contain images, readable answers, visible non-overlapping navigation and keyboard arrows')

        page.set_viewport_size({'width':1920,'height':1080})
        page.locator('#exit-session').click();page.locator('#search').fill('Unit 5')
        page.get_by_role('button',name='Sequential Test',exact=True).click()
        page.locator('#setup-scope').select_option('all');page.get_by_role('button',name='Bắt đầu Test →').click()
        expect(page.locator('#answer-panel')).to_be_hidden();expect(page.locator('#toggle-answer')).to_be_visible()
        page.screenshot(path=str(OUT/'test.png'),full_page=True)
        enter(page);geometry(page)
        page.locator('#question').focus();page.keyboard.press('a');expect(page.locator('#answer-panel')).to_be_visible()
        next_card(page);expect(page.locator('#answer-panel')).to_be_hidden();assert id(page)=='unit5-card-02'
        page.screenshot(path=str(OUT/'fullscreen-test.png'))
        page.locator('#question').focus();page.keyboard.press('Escape');page.wait_for_function('!document.fullscreenElement')
        passed('Sequential Test hides answers, teacher reveal works in fullscreen, next turn hides answer again and Escape exits')

        page.locator('#exit-session').click();page.locator('#search').fill('Unit 5')
        page.get_by_role('button',name='Random Test',exact=True).click()
        page.locator('#setup-scope').select_option('unit5');page.get_by_role('button',name='Bắt đầu Test →').click()
        enter(page);order=[id(page)]
        for _ in range(4):next_card(page);order.append(id(page));expect(page.locator('#answer-panel')).to_be_hidden()
        assert set(order)==set(c['id'] for c in SOURCE['cards'][9:])
        page.locator('#previous-card').click();settled(page);assert id(page)==order[-2]
        next_card(page);assert id(page)==order[-1]
        page.emulate_media(reduced_motion='reduce')
        page.locator('#previous-card').click();expect(page.locator('#card-stage')).to_have_attribute('aria-busy','false')
        assert id(page)==order[-2]
        assert page.locator('#speaking-card').evaluate('e=>e.getAnimations().length')==0
        # Long display text exercises wrapping/fit without mutating lesson data.
        page.evaluate("document.getElementById('question').textContent='Tell your teacher about the things you enjoy doing with your friends at school. '.repeat(4);dispatchEvent(new Event('resize'))")
        g=geometry(page);assert g['textScroll']<=g['textHeight']+2,g
        assert page.evaluate('micRequests')==0
        assert len(page.evaluate('speechCalls'))==1
        passed('Random Core order stays fixed through 3D Previous/Next; reduced motion disables turns; long text fits and no microphone/audio autoplay')
        assert not errors,errors;assert not external,external
        (OUT/'report.json').write_text(json.dumps({'browser':args.name,'version':version,'checks':checks,'errors':errors,'externalRequests':external,'nativeFullscreen':True,'actualSpeechOutputVerified':False},ensure_ascii=False,indent=2))
        browser.close()
finally:server.shutdown()
print('PASS',args.name,len(checks),'presentation groups')
