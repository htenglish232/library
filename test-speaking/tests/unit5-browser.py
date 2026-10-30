"""Exercise the real Unit 5 image pack in Practice and both Test scopes/orders."""
from pathlib import Path
from urllib.parse import urlsplit
import functools, hashlib, http.server, json, os, shutil, threading
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT/'test-speaking/data/global3-unit5'
SOURCE = json.loads((PACK/'unit5_speaking_cards.json').read_text())
BY_ID = {card['id']:card for card in SOURCE['cards']}
DECK_ID = SOURCE['id']
OUT = Path('/tmp/ht-speaking-unit5'); OUT.mkdir(exist_ok=True)
checks, errors, external, bad_responses = [], [], [], []

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
    def translate_path(self, path):
        if path.startswith('/library/'): path = path[len('/library'):]
        return super().translate_path(path)

server = http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE = f'http://127.0.0.1:{server.server_port}'
def passed(message):
    checks.append(message); print('PASS',message,flush=True)

def deck(page):
    page.locator('#search').fill('Unit 5')
    return page.locator(f'[data-set-id="{DECK_ID}"]')
def card_id(page): return page.locator('#speaking-card').get_attribute('data-card-id')
def check_card(page, practice=False):
    id = card_id(page); source = BY_ID[id]
    expect(page.locator('#question')).to_have_text(source['question'])
    expect(page.locator('#sample-answer')).to_have_text(source['sampleAnswer'] if practice else '')
    if practice:expect(page.locator('#answer-panel')).to_be_visible()
    else:expect(page.locator('#answer-panel')).to_be_hidden()
    expect(page.locator('#card-group')).to_have_text({'review':'Review','extension':'Extension','unit5':'Unit 5 Core'}[source['category']])
    expect(page.locator('#question-image')).to_have_attribute('src','./data/global3-unit5/'+source['image'])
    page.wait_for_function('document.getElementById("question-image").complete && document.getElementById("question-image").naturalWidth > 0')
    return id

def start_test(page, order, scope):
    deck(page).get_by_role('button',name='Random Test' if order=='random' else 'Sequential Test',exact=True).click()
    expect(page.locator('#setup-scope option')).to_have_text(['Toàn bộ 14 thẻ','Unit 5 Core · 5 thẻ'])
    page.locator('#setup-scope').select_option(scope)
    page.locator(f'input[name=test-order][value={order}]').check()
    page.locator('#setup-images').check();page.locator('#setup-timer').uncheck()
    page.get_by_role('button',name='Bắt đầu Test →').click()

try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'),args=['--no-sandbox'])
        context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce',accept_downloads=True)
        context.add_init_script("""window.speechCalls=[];window.micRequests=0;
Object.defineProperty(window,'speechSynthesis',{value:{cancel(){},getVoices(){return [{lang:'en-US'}]},speak(u){speechCalls.push({text:u.text,lang:u.lang})}}});
window.SpeechSynthesisUtterance=class{constructor(text){this.text=text}};
navigator.mediaDevices.getUserMedia=()=>{micRequests++;throw Error('No microphone permitted')};""")
        context.route('**/*',lambda route:route.continue_() if route.request.url.startswith(BASE+'/') else (external.append(route.request.url),route.abort())[-1])
        page=context.new_page();page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('response',lambda response:bad_responses.append([response.status,response.url]) if response.status>=400 else None)
        page.goto(BASE+'/library/test-speaking/')
        page.locator('#search').fill('Grade')
        expect(page.locator('.set-tile')).to_have_count(2)
        for label in ['Review · 8','Extension · 1','Unit 5 Core · 5']:expect(deck(page).get_by_text(label,exact=True)).to_be_visible()
        page.locator('#unit-filter').select_option('Unit 5');expect(page.locator('.set-tile')).to_have_count(1)
        page.locator('#unit-filter').select_option('')
        for card in SOURCE['cards']:
            response=context.request.get(BASE+'/library/test-speaking/data/global3-unit5/'+card['image'])
            assert response.status==200
            assert hashlib.sha256(response.body()).digest()==hashlib.sha256((PACK/card['image']).read_bytes()).digest()
        passed('All 14 original image paths return exact PNG bytes under GitHub project Pages; categories and Unit 5 filter are correct')

        deck(page).get_by_role('button',name='Practice →',exact=True).click()
        for i,source in enumerate(SOURCE['cards']):
            assert check_card(page,practice=True)==source['id']
            expect(page.locator('#sample-answer')).to_be_visible()
            expect(page.locator('#toggle-answer')).to_have_count(0)
            page.locator('#play-audio').click()
            assert page.evaluate('speechCalls.at(-1)')=={'text':source['question'],'lang':'en-US'}
            if i<13:page.locator('#next-card').click()
        expect(page.locator('#next-card')).to_be_disabled()
        page.locator('#first-card').click()
        for _ in range(9):page.locator('#next-card').click()
        for width,height in [(360,800),(390,844),(1440,1000),(1920,1080)]:
            page.set_viewport_size({'width':width,'height':height})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            image_box=page.locator('#question-image').bounding_box()
            assert image_box['height']>=200,(width,image_box)
            if width<=800:
                question_box=page.locator('#question').bounding_box()
                assert image_box['y']<question_box['y']
            for position in ['0','document.body.scrollHeight']:
                page.evaluate(f'scrollTo(0,{position})')
                nav=page.locator('.player-nav').bounding_box();assert abs(nav['y']+nav['height']-height)<2
            page.evaluate('scrollTo(0,0)')
            page.screenshot(path=str(OUT/f'unit5-practice-{width}.png'),full_page=True)
        page.set_viewport_size({'width':1440,'height':1000})
        page.locator('#exit-session').click()
        passed('Practice checks all 14 image/question/answer associations, always-visible answers, English speech calls and large responsive images with fixed navigation')

        for scope in ['all','unit5']:
            expected=[c['id'] for c in SOURCE['cards'] if scope=='all' or c['category']=='unit5']
            for order in ['sequential','random']:
                start_test(page,order,scope)
                actual=[]
                for i in range(len(expected)):
                    actual.append(check_card(page))
                    expect(page.locator('#toggle-answer')).to_have_count(0)
                    expect(page.locator('#sample-answer')).to_be_empty()
                    if i<len(expected)-1:page.locator('#next-card').click()
                assert len(set(actual))==len(expected)
                assert set(actual)==set(expected)
                if order=='sequential':assert actual==expected
                expect(page.locator('#test-progress')).to_have_text(f'Đã xem {len(expected)} · Còn 0')
                page.locator('#previous-card').click();assert card_id(page)==actual[-2]
                page.locator('#next-card').click();assert card_id(page)==actual[-1]
                page.locator('#restart-test').click();page.locator('#confirm-accept').click()
                expect(page.locator('#card-position')).to_have_text(f'Câu 1 / {len(expected)}')
                expect(page.locator('#test-progress')).to_have_text(f'Đã xem 1 · Còn {len(expected)-1}')
                if scope=='unit5':expect(page.locator('#card-group')).to_have_text('Unit 5 Core')
                page.locator('#exit-session').click()
                passed(f'{order} Test / {scope}: {len(expected)} exact cards; default hidden answers, no repeats, stable Previous/Next, restart retains scope')

        # Editing/export must not erase category metadata, breaking future scope filtering.
        deck(page).get_by_role('button',name='Chỉnh sửa bộ thẻ',exact=True).click()
        page.locator('#editor-cards button').nth(9).click()
        expect(page.locator('#edit-category')).to_have_value('unit5')
        page.locator('#card-form button[type=submit]').click()
        with page.expect_download() as download:page.locator('#export-set').click()
        exported=json.loads(Path(download.value.path()).read_text())['sets'][0]
        assert [c['category'] for c in exported['cards']]==[c['category'] for c in SOURCE['cards']]
        assert [c['question'] for c in exported['cards']]==[c['question'] for c in SOURCE['cards']]
        assert [c['sampleAnswer'] for c in exported['cards']]==[c['sampleAnswer'] for c in SOURCE['cards']]
        page.locator('#editor-dialog [data-close]').click()
        assert page.evaluate('micRequests')==0
        passed('Editing and real JSON export retain all categories and supplied his/her question/answer text; no microphone requests')

        old=browser.new_context()
        original=json.loads((ROOT/'test-speaking/data/sets.json').read_text())
        original[0]['title']='Teacher legacy library'
        old.add_init_script('''if(!sessionStorage.getItem('seeded')){localStorage.setItem('ht-speaking:v1:sets',JSON.stringify(%s));sessionStorage.setItem('seeded','true')}'''%json.dumps(original))
        legacy=old.new_page();legacy.on('pageerror',lambda error:errors.append(str(error)))
        legacy.goto(BASE+'/test-speaking/')
        legacy.locator('#search').fill('Grade')
        expect(legacy.locator('.set-tile')).to_have_count(2)
        expect(legacy.get_by_role('heading',name='Teacher legacy library',exact=True)).to_be_visible()
        assert legacy.evaluate("JSON.parse(localStorage.getItem('ht-speaking:v1:sets'))")==original
        deck(legacy).get_by_role('button',name='Chỉnh sửa bộ thẻ',exact=True).click()
        legacy.locator('#delete-set').click();legacy.locator('#confirm-accept').click()
        legacy.reload();legacy.locator('#search').fill('Grade');expect(legacy.locator('.set-tile')).to_have_count(1)
        expect(legacy.get_by_role('heading',name='Teacher legacy library',exact=True)).to_be_visible()
        passed('Existing local teacher decks are unchanged; new pack appears automatically and confirmed deletion is respected after reload')
        assert not errors,errors
        assert not external,external
        assert not bad_responses,bad_responses
        (OUT/'report.json').write_text(json.dumps({'checks':checks,'errors':errors,'external':external,'badResponses':bad_responses,'realDeviceSpeechVerified':False},ensure_ascii=False,indent=2))
        browser.close()
finally:server.shutdown()
print(f'PASS {len(checks)} Unit 5 browser groups')
