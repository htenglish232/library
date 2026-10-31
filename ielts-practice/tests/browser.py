"""Real browser acceptance/source checks at desktop, tablet and phone sizes."""
from pathlib import Path
from urllib.parse import urlparse
import argparse, functools, http.server, json, os, shutil, threading
from playwright.sync_api import sync_playwright, expect

parser=argparse.ArgumentParser()
parser.add_argument('--browser-path',default=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'))
parser.add_argument('--name',default='chromium')
parser.add_argument('--root',default=str(Path(__file__).resolve().parents[2]))
args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[2];APP=ROOT/'ielts-practice'
UNIT=APP/'unit-2-individuals-and-families'
unit=json.loads((UNIT/'unit.json').read_text());key=json.loads((UNIT/'answers.json').read_text())
OUT=Path('/tmp/ht-ielts-unit2')/args.name;OUT.mkdir(parents=True,exist_ok=True)
errors,bad,external,checks=[],[],[],[]
class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
    def translate_path(self,path):
        if path.startswith('/library/'):path=path[len('/library'):]
        return super().translate_path(path)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=args.root))
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}'
URL=BASE+'/library/ielts-practice/unit-2-individuals-and-families/index.html'
def passed(text):checks.append(text);print('PASS',args.name,text,flush=True)
def jump(page,name):
    page.locator('#step-picker').evaluate('(e)=>e.open=true')
    page.locator('#step-list').get_by_role('button',name=name,exact=True).click()
def layout(page):
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
    if page.locator('#navigation').is_visible():
        g=page.evaluate('''()=>{
          const n=document.getElementById('navigation'),r=n.getBoundingClientRect();
          return {bottom:r.bottom,h:innerHeight,height:r.height,buttons:[...n.querySelectorAll('button')].map(b=>b.getBoundingClientRect().toJSON())};
        }''')
        assert abs(g['bottom']-g['h'])<2,g
        for button in g['buttons']:assert button['height']>=44 and button['bottom']<=g['bottom'],g
        # The last input/text remains reachable above the navigation after scroll.
        page.evaluate('scrollTo(0,document.documentElement.scrollHeight)')
        content=page.locator('#task-content').bounding_box()
        if content and page.locator('#task').is_visible():
            nav=page.locator('#navigation').bounding_box()
            assert content['y']+content['height']<=nav['y']+1,(content,nav)
        page.evaluate('scrollTo(0,0)')
def stat_values(page):return page.locator('#result-stats strong').all_text_contents()

try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=args.browser_path,args=['--no-sandbox'])
        version=browser.version
        for width,height in [(1440,1000),(768,1024),(390,844),(375,812)]:
            context=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce')
            requests=[]
            context.route('**/*',lambda r:r.continue_() if r.request.url.startswith(BASE+'/') else (external.append(r.request.url),r.abort())[-1])
            page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('request',lambda r:requests.append(r.url))
            page.on('response',lambda r:bad.append([r.status,r.url]) if r.status>=400 else None)
            page.goto(URL)
            expect(page.locator('#welcome')).to_be_visible();expect(page.locator('#welcome-sections li')).to_have_count(5)
            page.evaluate("localStorage.setItem('ht-ghk1-test-sentinel','unchanged')")
            if width in [1440,390]:page.screenshot(path=str(OUT/f'welcome-{width}.png'),full_page=True)
            page.locator('#student-name').fill('Nguyễn An')
            page.get_by_role('button',name='Bắt đầu làm bài →',exact=True).click()
            expect(page.locator('#task-title')).to_have_text(unit['passages'][0]['title'])
            for index,passage in enumerate(unit['passages']):
                expect(page.locator('#task-title')).to_have_text(passage['title'])
                expect(page.locator('.passage-copy')).to_have_text(passage['text'])
                page.locator('.vocabulary').first.locator('summary').click()
                assert page.locator('.vocabulary dt').all_text_contents()==[v['term'] for v in passage['vocabulary']]
                assert [t.split('synonym:')[0].strip() for t in page.locator('.vocabulary dd').all_text_contents()]==[v['meaning'] for v in passage['vocabulary']]
                if index==9:
                    page.locator('.vocabulary').last.locator('summary').click()
                    assert page.locator('.vocabulary-summary li').all_text_contents()==unit['vocabularySummary']
                page.locator('#next').click()
            assert page.locator('#reading-text p').count()==5
            assert page.locator('#reading-text p').evaluate_all("ps=>ps.map(p=>p.lastChild.textContent)")==unit['reading']
            page.get_by_role('button',name='Đánh dấu đoạn 3',exact=True).click()
            expect(page.locator('.paragraph-mark').nth(2)).to_have_attribute('aria-pressed','true')
            page.locator('#next').click()
            for index,q in enumerate(unit['multipleChoice']):
                expect(page.locator('#task-title')).to_have_text(q['question'])
                assert page.locator('.option span').all_text_contents()==[o['value']+'.'+o['text'] for o in q['options']]
                expect(page.locator('#feedback')).to_be_hidden()
                if index<9:page.locator(f'input[value={"A" if index==0 else key["multipleChoice"][index]["answer"]}]').check()
                if index==2:
                    page.reload();expect(page.locator('#task-title')).to_have_text(q['question'])
                    expect(page.locator(f'input[value={key["multipleChoice"][index]["answer"]}]')).to_be_checked()
                layout(page)
                if index==3:
                    if width>900:
                        assert page.locator('#reading-panel').bounding_box()['x']<page.locator('#task').bounding_box()['x']
                    if width in [1440,390]:page.screenshot(path=str(OUT/f'multiple-choice-{width}.png'),full_page=True)
                page.locator('#next').click()
            expect(page.locator('.word-bank p').first).to_have_text(unit['summary']['wordBankText'])
            expect(page.locator('.summary-blank input')).to_have_count(10)
            # Verify original Summary text/markers independent of form controls.
            assert page.locator('.summary-copy').evaluate_all("ps=>ps.map(p=>[...p.childNodes].map(n=>n.nodeType===3?n.textContent:'__________'+n.querySelector('span').textContent).join(''))")==unit['summary']['paragraphs']
            for index,answer in enumerate(key['summary']):
                if index<9:page.locator(f'#blank-{index+1}').fill('behaviour' if index==0 else ' '+answer.upper()+' ')
            page.reload();expect(page.locator('#blank-3')).to_have_value(' SUPPORT ')
            assert not any(url.endswith('/answers.json') for url in requests),requests
            layout(page)
            if width in [1440,390]:page.screenshot(path=str(OUT/f'summary-{width}.png'),full_page=True)
            page.locator('#next').click()
            expect(page.locator('.translation-prompt')).to_have_text(unit['translation']['text'])
            draft='Families support each other.\nWe learn at home.'
            page.locator('#translation-input').fill(draft);expect(page.locator('#word-count')).to_have_text('8 từ')
            jump(page,'D · Summary');expect(page.locator('#blank-2')).to_have_value(' SUPPORT ')
            jump(page,'E · Translation');expect(page.locator('#translation-input')).to_have_value(draft)
            page.reload();expect(page.locator('#translation-input')).to_have_value(draft)
            layout(page)
            if width in [1440,390]:page.screenshot(path=str(OUT/f'translation-{width}.png'),full_page=True)
            page.locator('#next').click();expect(page.locator('#submit-dialog')).to_be_visible()
            expect(page.locator('#submit-description')).to_contain_text('18/20')
            page.locator('#submit-cancel').click();expect(page.locator('#translation-input')).to_have_value(draft)
            page.locator('#submit-open').click();page.locator('#submit-confirm').click()
            expect(page.locator('#results')).to_be_visible()
            assert stat_values(page)==['20','16','2','2'],stat_values(page)
            expect(page.locator('#result-completion')).to_contain_text('90%')
            expect(page.locator('#result-translation')).to_have_text(draft)
            assert page.locator('#reference-details').get_attribute('open') is None
            page.locator('#reference-details summary').click()
            expect(page.locator('#reference-content .reference-translation')).to_have_text(key['referenceTranslation'])
            expect(page.locator('#reference-content dt')).to_have_count(10)
            if width in [1440,390]:page.screenshot(path=str(OUT/f'results-{width}.png'),full_page=True)
            page.reload();expect(page.locator('#results')).to_be_visible();assert stat_values(page)==['20','16','2','2']
            expect(page.locator('#result-translation')).to_have_text(draft)
            page.locator('#review-wrong').click();expect(page.locator('#review-banner')).to_be_visible()
            expect(page.locator('#step-list button')).to_have_count(4)
            page.locator('input[value=B]').check();page.locator('#review-check').click()
            expect(page.locator('#review-result')).to_contain_text('Đúng rồi.')
            page.locator('#next').click();page.locator('input[value=C]').check();page.locator('#review-check').click()
            page.locator('#next').click();expect(page.locator('#blank-1')).to_be_enabled();expect(page.locator('#blank-2')).to_be_disabled()
            page.locator('#blank-1').fill('behavior');page.locator('#review-check').click();expect(page.locator('#review-result')).to_have_text('Đúng rồi.')
            page.locator('#results-open').click();assert stat_values(page)==['20','16','2','2']
            page.locator('#view-solutions').click();expect(page.locator('#feedback')).to_contain_text(key['multipleChoice'][0]['explanation'])
            expect(page.locator('input[value=A]')).to_be_checked();expect(page.locator('input[value=A]')).to_be_disabled()
            jump(page,'D · Summary');expect(page.locator('#feedback')).to_contain_text(key['sourceNote'])
            expect(page.locator('#blank-1')).to_have_value('behaviour')
            assert page.evaluate("localStorage.getItem('ht-ghk1-test-sentinel')")=='unchanged'
            if width in [1440,390]:page.screenshot(path=str(OUT/f'summary-feedback-{width}.png'),full_page=True)
            page.locator('#results-open').click();page.locator('#restart').click();page.locator('#restart-cancel').click()
            expect(page.locator('#result-translation')).to_have_text(draft)
            page.locator('#restart').click();page.locator('#restart-confirm').click();expect(page.locator('#welcome')).to_be_visible()
            page.locator('#student-name').fill('Lượt mới');page.locator('#start-form button').click();jump(page,'C · Câu 1')
            assert page.locator('input[type=radio]:checked').count()==0
            expect(page.locator('#feedback')).to_be_hidden()
            context.close()
            passed(f'{width}px: all source passages/vocab/reading/questions/summary/translation; autosave/reload; 16 correct/2 wrong/2 blank; explanations, reference and isolated wrong-answer review; reachable navigation, reset and no answer leak')

        # Fault cases: storage denial and answer-file errors must not lose work.
        context=browser.new_context(viewport={'width':390,'height':844})
        context.add_init_script("Storage.prototype.setItem=function(){throw Error('quota')}")
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(URL);page.locator('#student-name').fill('Không lưu');page.locator('#start-form button').click()
        expect(page.locator('#storage-message')).to_be_visible();jump(page,'E · Translation')
        page.locator('#translation-input').fill('Keep this draft.')
        page.route('**/answers.json',lambda r:r.fulfill(status=503,body='temporarily unavailable'))
        page.locator('#submit-open').click();page.locator('#submit-confirm').click()
        expect(page.locator('#submit-error')).to_contain_text('Bài làm vẫn được giữ nguyên')
        page.locator('#submit-cancel').click();expect(page.locator('#translation-input')).to_have_value('Keep this draft.')
        page.unroute('**/answers.json');page.locator('#submit-open').click();page.locator('#submit-confirm').click()
        expect(page.locator('#results')).to_be_visible();context.close()
        passed('Storage quota warning and failed key fetch preserve entered work; retry submission succeeds')
        assert not errors,errors;assert not bad,bad;assert not external,external
        (OUT/'report.json').write_text(json.dumps({'browser':args.name,'version':version,'checks':checks,'errors':errors,'httpErrorsInNormalFlow':bad,'externalRequests':external},ensure_ascii=False,indent=2))
        browser.close()
finally:server.shutdown()
print('PASS',args.name,len(checks),'acceptance groups')
