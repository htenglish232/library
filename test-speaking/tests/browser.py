"""Standalone and GitHub Pages paths; local-only browser regression checks."""
from pathlib import Path
from urllib.parse import urlsplit
import functools, http.server, json, os, shutil, threading
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[2]
OUT = Path('/tmp/ht-speaking-cards')
OUT.mkdir(exist_ok=True)

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
    def translate_path(self, path):
        if path.startswith('/library/'): path = path[len('/library'):]
        return super().translate_path(path)

server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(ROOT)))
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f'http://127.0.0.1:{server.server_port}'
checks, errors, external = [], [], []
def passed(message):
    checks.append(message)
    print('PASS', message, flush=True)

SPEECH = """(() => {
 window.mediaCalls=[]; window.micRequests=0;
 Object.defineProperty(window,'speechSynthesis',{value:{cancel(){mediaCalls.push(['cancel'])},getVoices(){return [{lang:'vi-VN'},{lang:'en-GB'},{lang:'en-US'}]},speak(u){mediaCalls.push(['speak',u.text,u.rate,u.voice?.lang])}}});
 window.SpeechSynthesisUtterance=class{constructor(text){this.text=text}};
 window.Audio=class{constructor(src){this.src=src;mediaCalls.push(['mp3',src])} play(){mediaCalls.push(['play']);return Promise.resolve()}pause(){mediaCalls.push(['pause'])}removeAttribute(){}load(){}};
 navigator.mediaDevices.getUserMedia=()=>{window.micRequests++;throw Error('Microphone must never be used')};
})()"""

def no_overflow(page):
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')

def start_test(page, random=False, timed=False):
    page.locator('#search').fill('Speaking Practice')
    page.get_by_role('button', name='Random Test' if random else 'Sequential Test', exact=True).first.click()
    page.locator(f'input[name="test-order"][value="{"random" if random else "sequential"}"]').check()
    page.locator('#setup-timer').set_checked(timed)
    page.locator('#setup-duration').select_option('15')
    page.get_by_role('button', name='Bắt đầu Test →').click()

def import_file(page, name, content):
    page.locator('#import-open').click()
    page.locator('#import-file').set_input_files({'name':name,'mimeType':'text/plain','buffer':content.encode()})
    page.locator('#import-submit').click()

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'), args=['--no-sandbox'])
        context = browser.new_context(viewport={'width':1440,'height':1000}, accept_downloads=True, reduced_motion='reduce')
        context.add_init_script(SPEECH)
        context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(BASE + '/') else (external.append(route.request.url), route.abort())[-1])
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(BASE + '/library/test-speaking/')
        expect(page.locator('[data-grade="Grade 3"]')).to_be_visible()
        page.locator('#grade-filter').select_option('Grade 3')
        expect(page.locator('.set-tile')).to_have_count(2)
        expect(page.locator('#library-count')).to_contain_text('29 câu hỏi')
        page.screenshot(path=str(OUT/'library-desktop.png'), full_page=True)
        page.locator('#search').fill('not an existing deck')
        expect(page.locator('#empty-library')).to_be_visible()
        page.locator('#search').fill('global success')
        expect(page.locator('.set-tile')).to_have_count(2)
        page.locator('#search').fill('')
        for key, value in [('grade','Grade 3'),('textbook','Global Success'),('unit','Speaking Practice')]:
            page.locator(f'#{key}-filter').select_option(value)
            expect(page.locator('.set-tile')).to_have_count(1 if key == 'unit' else 2)
        passed('Library loads under /library/, search and all Grade/textbook/Unit filters work')

        page.get_by_role('button', name='Practice →', exact=True).first.click()
        expect(page.locator('#question')).to_have_text('What is your name?')
        expect(page.locator('#answer-panel')).to_be_visible()
        page.locator('#question').focus(); page.keyboard.press('a')
        expect(page.locator('#sample-answer')).to_be_visible()
        page.keyboard.press('ArrowRight')
        expect(page.locator('#question')).to_have_text('How old are you?')
        expect(page.locator('#answer-panel')).to_be_visible()
        page.locator('#speech-rate').focus(); page.keyboard.press('a')
        expect(page.locator('#answer-panel')).to_be_visible()
        page.locator('#question').focus()
        page.keyboard.press('ArrowLeft')
        expect(page.locator('#card-position')).to_have_text('Câu 1 / 15')
        page.keyboard.press('Space'); page.keyboard.press('Space')
        assert page.evaluate("mediaCalls.filter(c=>c[0]==='speak').length") == 2
        assert page.evaluate("mediaCalls.filter(c=>c[0]==='speak').every(c=>c[3]==='en-US')")
        page.locator('#speech-rate').select_option('0.75')
        page.locator('#play-audio').click()
        assert page.evaluate("mediaCalls.filter(c=>c[0]==='speak').at(-1)[2]") == .75
        before = page.evaluate("mediaCalls.filter(c=>c[0]==='cancel').length")
        page.locator('#next-card').click()
        assert page.evaluate("mediaCalls.filter(c=>c[0]==='cancel').length") > before
        page.locator('#shuffle-practice').click()
        questions = [page.locator('#question').inner_text()]
        for _ in range(14):
            page.locator('#next-card').click(); questions.append(page.locator('#question').inner_text())
        assert len(set(questions)) == 15
        expect(page.locator('#next-card')).to_be_disabled()
        page.locator('#first-card').click()
        expect(page.locator('#question')).to_have_text(questions[0])
        page.locator('#next-card').click(); remembered = page.locator('#question').inner_text()
        page.reload(); page.locator('#search').fill('Speaking Practice'); page.get_by_role('button', name='Practice →', exact=True).first.click()
        expect(page.locator('#question')).to_have_text(remembered)
        expect(page.locator('#card-position')).to_have_text('Câu 2 / 15')
        expect(page.locator('#answer-panel')).to_be_visible()
        passed('Practice navigation, always-visible answers, keyboard, shuffled coverage, resume after reload and speech cancellation/rate')

        page.locator('#fullscreen').click()
        assert page.evaluate('document.fullscreenElement?.id') == 'presentation'
        page.locator('#question').focus(); page.keyboard.press('Escape')
        page.wait_for_function('!document.fullscreenElement')
        page.locator('#question').focus(); page.keyboard.press('f')
        page.wait_for_function('!!document.fullscreenElement')
        page.keyboard.press('f'); page.wait_for_function('!document.fullscreenElement')
        passed('Fullscreen button, F and Escape')
        page.locator('#exit-session').click()
        start_test(page)
        expect(page.locator('#question')).to_have_text('What is your name?')
        expect(page.locator('#timer-panel')).to_be_hidden()
        expect(page.locator('#toggle-answer')).to_have_count(0)
        page.keyboard.press('a'); expect(page.locator('#answer-panel')).to_be_hidden()
        page.locator('#next-card').click()
        expect(page.locator('#question')).to_have_text('How old are you?')
        expect(page.locator('#answer-panel')).to_be_hidden()
        page.locator('#exit-session').click()
        start_test(page, random=True)
        random_questions = [page.locator('#question').inner_text()]
        for _ in range(14):
            page.locator('#next-card').click(); random_questions.append(page.locator('#question').inner_text())
        assert len(set(random_questions)) == 15
        expect(page.locator('#test-progress')).to_have_text('Đã xem 15 · Còn 0')
        page.locator('#previous-card').click(); expect(page.locator('#question')).to_have_text(random_questions[-2])
        expect(page.locator('#test-progress')).to_have_text('Đã xem 15 · Còn 0')
        page.locator('#next-card').click(); expect(page.locator('#question')).to_have_text(random_questions[-1])
        page.evaluate("window.shuffleCalls=0;window.originalRandom=Math.random;Math.random=()=>{if(new Error().stack.includes('/test-speaking/core.js'))shuffleCalls++;return originalRandom()}")
        page.locator('#restart-test').click()
        page.keyboard.press('a'); expect(page.locator('#answer-panel')).to_be_hidden()
        page.locator('#confirm-accept').click()
        assert page.evaluate('shuffleCalls') == 14, page.evaluate('shuffleCalls')
        page.evaluate('Math.random=originalRandom')
        expect(page.locator('#card-position')).to_have_text('Câu 1 / 15')
        expect(page.locator('#test-progress')).to_have_text('Đã xem 1 · Còn 14')
        page.clock.install()
        page.locator('#timer-enabled').check()
        page.locator('#timer-duration').select_option('15')
        current = page.locator('#question').inner_text()
        page.clock.fast_forward(5000)
        expect(page.locator('#timer-readout')).to_have_text('10s')
        page.locator('#timer-pause').click(); page.clock.fast_forward(20000)
        expect(page.locator('#timer-readout')).to_have_text('10s')
        page.locator('#timer-pause').click(); page.clock.fast_forward(10000)
        expect(page.locator('#timer-message')).to_contain_text('Hết giờ!')
        expect(page.locator('#question')).to_have_text(current)
        expect(page.locator('#answer-panel')).to_be_hidden()
        page.locator('#next-card').click(); expect(page.locator('#timer-readout')).to_have_text('15s')
        page.locator('#timer-enabled').uncheck(); expect(page.locator('#timer-panel')).to_be_hidden()
        passed('Sequential and non-repeating Random Test, stable backtracking, restart, optional timer pause/expiry with no auto-advance')

        for width,height in [(360,800),(390,844),(768,1024),(1920,1080)]:
            page.set_viewport_size({'width':width,'height':height})
            no_overflow(page)
            nav = page.locator('.player-nav').bounding_box()
            assert abs(nav['y'] + nav['height'] - height) <= 1
            assert page.locator('#next-card').bounding_box()['height'] >= 44
            page.screenshot(path=str(OUT/f'player-{width}.png'), full_page=True)
        page.locator('#exit-session').click()
        page.set_viewport_size({'width':390,'height':844}); no_overflow(page)
        page.screenshot(path=str(OUT/'library-mobile.png'), full_page=True)
        page.set_viewport_size({'width':1440,'height':1000})
        passed('Mobile/tablet/projector layout without overflow; fixed accessible navigation')

        page.locator('#new-set').click()
        for field,value in [('title','Teacher cards'),('grade','Grade 4'),('textbook','Teacher content'),('unit','Unit 2')]:
            page.locator('#set-'+field).fill(value)
        page.locator('#set-title').press('End')
        page.locator('#set-title').press('a')
        expect(page.locator('#set-title')).to_have_value('Teacher cardsa')
        page.locator('#set-title').fill('Teacher cards')
        page.locator('#set-form button[type=submit]').click()
        page.locator('#edit-question').fill('What do you like?')
        page.locator('#edit-answer').fill('I like books.')
        page.locator('#edit-keywords').fill('books | reading')
        page.locator('#card-form button[type=submit]').click()
        expect(page.locator('#editor-cards li')).to_have_count(1)
        page.locator('#edit-answer').fill('I like reading books.')
        page.locator('#card-form button[type=submit]').click()
        page.locator('#delete-card').click(); page.locator('#confirm-cancel').click()
        expect(page.locator('#editor-cards li')).to_have_count(1)
        with page.expect_download() as download:
            page.locator('#export-set').click()
        backup = json.loads(Path(download.value.path()).read_text())
        assert backup['sets'][0]['cards'][0]['sampleAnswer'] == 'I like reading books.'
        page.locator('#delete-card').click(); page.locator('#confirm-accept').click()
        expect(page.locator('#editor-cards li')).to_have_count(0)
        page.locator('#editor-dialog [data-close]').click()
        for key in ['grade','textbook','unit']: page.locator(f'#{key}-filter').select_option('')
        page.locator('#search').fill('Grade')
        import_file(page, 'restore.json', json.dumps(backup))
        expect(page.locator('#confirm-dialog')).to_be_visible()
        page.locator('#confirm-accept').click()
        expect(page.locator('#import-dialog')).not_to_be_visible()
        expect(page.locator('.set-tile')).to_have_count(3)
        passed('Teacher set/card creation and edits, delete confirmation/cancel, real JSON download and restore with replacement confirmation')

        import_file(page, 'bad.json', '{"id":"bad","cards":[]}')
        expect(page.locator('#import-error')).to_contain_text('Không nhập dữ liệu')
        page.locator('#import-dialog [data-close]').click()
        expect(page.locator('.set-tile')).to_have_count(3)
        csv = 'setId,title,grade,textbook,unit,id,question,sampleAnswer,keywords,image,audio\nmedia,Media cards,Grade 3,Global Success,Unit 5,media1,Hello?,Hello!,hello,./test-image.svg,./hello.mp3\n'
        import_file(page, 'cards.csv', csv)
        expect(page.locator('.set-tile')).to_have_count(4)
        page.route('**/test-image.svg', lambda route: route.fulfill(content_type='image/svg+xml', body='<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60"><circle cx="30" cy="30" r="20" fill="blue"/></svg>'))
        tile = page.locator('.set-tile').filter(has=page.get_by_role('heading', name='Media cards', exact=True))
        tile.get_by_role('button', name='Sequential Test', exact=True).click()
        page.locator('#setup-images').check(); page.locator('#setup-timer').uncheck()
        page.get_by_role('button', name='Bắt đầu Test →').click()
        expect(page.locator('#question-image')).to_be_visible()
        page.locator('#show-images').uncheck(); expect(page.locator('#question-figure')).to_be_hidden()
        spoken = page.evaluate("mediaCalls.filter(c=>c[0]==='speak').length")
        page.locator('#play-audio').click()
        assert page.evaluate("mediaCalls.filter(c=>c[0]==='mp3').at(-1)[1]") == './hello.mp3'
        assert page.evaluate("mediaCalls.filter(c=>c[0]==='speak').length") == spoken
        page.locator('#exit-session').click()
        assert page.evaluate("mediaCalls.filter(c=>c[0]==='pause').length") >= 1
        assert page.evaluate('micRequests') == 0
        page.reload(); page.locator('#search').fill('Grade'); expect(page.locator('.set-tile')).to_have_count(4)
        tile = page.locator('.set-tile').filter(has=page.get_by_role('heading', name='Media cards', exact=True))
        tile.get_by_role('button', name='Chỉnh sửa bộ thẻ').click()
        page.locator('#delete-set').click(); page.locator('#confirm-accept').click()
        expect(page.locator('.set-tile')).to_have_count(3)
        passed('Invalid imports are atomic; CSV import, optional image toggle, MP3 priority/stop, persisted library and confirmed set deletion')

        # A distinct browser with storage disabled still supports the baseline and export.
        fallback = browser.new_context()
        fallback.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new DOMException('denied','SecurityError')}});Object.defineProperty(window,'speechSynthesis',{value:undefined});")
        fallback.route('**/*', lambda route: route.continue_() if route.request.url.startswith(BASE + '/') else route.abort())
        safe = fallback.new_page(); safe.on('pageerror', lambda error: errors.append(str(error)))
        safe.goto(BASE + '/test-speaking/')
        safe.locator('#search').fill('Grade')
        expect(safe.locator('.set-tile')).to_have_count(2)
        expect(safe.locator('#storage-warning')).to_be_visible()
        safe.get_by_role('button', name='Practice →', exact=True).first.click()
        safe.locator('#play-audio').click()
        expect(safe.locator('#audio-status')).to_contain_text('không hỗ trợ')
        safe.locator('#next-card').click(); expect(safe.locator('#card-position')).to_have_text('Câu 2 / 15')
        passed('Standalone path and unavailable storage/speech degrade safely without blocking cards')
        assert not errors, errors
        assert not external, external
        (OUT/'report.json').write_text(json.dumps({'checks':checks,'errors':errors,'externalRequests':external,'realDeviceAudioVerified':False},ensure_ascii=False,indent=2))
        browser.close()
finally:
    server.shutdown()
print(f'PASS {len(checks)} browser groups; no production requests or microphone access.')
