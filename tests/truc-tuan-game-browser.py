"""Real Chromium checks. Run first with --pilot while HTML data-stage=pilot.

python tests/truc-tuan-game-browser.py [--pilot]
Needs Playwright Python and Chromium; no Firebase, internet, or npm build.
"""
import argparse
import functools
import hashlib
import http.server
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import threading
from urllib.parse import quote
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
RELATIVE = 'grade-8/De_thi_GHK1/1_THCS Truc Tuan/'
BASELINE = '395f33ea7adb44723812197e7d67d92cc84a2e94'
parser = argparse.ArgumentParser()
parser.add_argument('--pilot', action='store_true')
args = parser.parse_args()
ARTIFACTS = Path(os.environ.get('GAME_TEST_OUTPUT', '/tmp/ht-truc-tuan-game-tests'))
ARTIFACTS.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location('extract_game', ROOT / 'tools/extract-truc-tuan-game.py')
extractor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extractor)
expected_source = extractor.extract()
for filename, digest in expected_source['sourceFiles'].items():
    original = subprocess.check_output(['git', 'show', BASELINE + ':' + RELATIVE + filename], cwd=ROOT)
    assert hashlib.sha256(original).hexdigest() == digest, ('original changed', filename)


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *unused):
        pass

    def translate_path(self, path):
        if path.startswith('/library/'):
            path = path[len('/library'):]
        return super().translate_path(path)

    def copyfile(self, source, output):
        try:
            remaining=getattr(self, '_range_remaining', None)
            if remaining is None:
                super().copyfile(source, output)
            else:
                while remaining > 0:
                    chunk=source.read(min(65536,remaining))
                    if not chunk: break
                    output.write(chunk)
                    remaining-=len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def send_head(self):
        # Match GitHub Pages byte-range support so Chromium can seek real MP3s.
        target=Path(self.translate_path(self.path))
        self._range_remaining=None
        if target.suffix.lower()!='.mp3' or not target.is_file():
            return super().send_head()
        size=target.stat().st_size
        requested=self.headers.get('Range')
        match=re.fullmatch(r'bytes=(\d+)-(\d*)',requested or '')
        start=int(match[1]) if match else 0
        end=min(int(match[2]) if match and match[2] else size-1,size-1)
        if start>=size or end<start:
            self.send_error(416)
            return None
        self.send_response(206 if match else 200)
        self.send_header('Content-Type','audio/mpeg')
        self.send_header('Accept-Ranges','bytes')
        self.send_header('Content-Length',str(end-start+1))
        if match:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.end_headers()
        stream=target.open('rb');stream.seek(start)
        self._range_remaining=end-start+1
        return stream


server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(ROOT)))
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{server.server_port}/'
path = quote(RELATIVE + 'truc-tuan-game-test.html')
checks = []
errors = []
external = []


def passed(message):
    checks.append(message)
    print('PASS ' + message, flush=True)


try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'), args=['--no-sandbox', '--autoplay-policy=no-user-gesture-required'])
        context = browser.new_context(viewport={'width':1280, 'height':900}, reduced_motion='reduce')

        def route(request):
            if request.request.url.startswith(base):
                request.continue_()
            else:
                external.append(request.request.url)
                request.abort()

        context.route('**/*', route)
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('console', lambda message: errors.append(message.text) if message.type == 'error' else None)
        assert page.goto(base + path).status == 200
        expect(page.locator('#welcome')).to_be_visible()
        actual_source = page.evaluate('window.HT_GAME_SOURCE')
        assert actual_source == expected_source, 'Generated source must match ALL original content, not just count.'
        assert page.evaluate('Object.keys(window.HT_GAME_NOTES).length') == 42
        assert page.locator('#transcript-content').inner_text() == ''
        passed('page opens; all 42 source questions/answers/options/explanations/notes/passages/transcripts/tokens and original file hashes match')
        page.locator('#start-form button').click()
        expect(page.locator('#name-error')).to_contain_text('nhập tên')
        expect(page.locator('#welcome')).to_be_visible()
        page.locator('#student-name').fill('   Học sinh   Trực Tuấn  ')
        page.locator('#start-form button').click()
        expect(page.locator('#student-label')).to_have_text('Học sinh Trực Tuấn')
        total = 5 if args.pilot else 42
        expect(page.locator('#journey-count')).to_have_text(f'0/{total} câu đã luyện')
        passed('empty name rejected; normalized student name starts a fresh session; correct pilot/full question count')

        def go(qid):
            q = next(q for q in actual_source['questions'] if q['id'] == qid)
            if page.locator('#play').is_visible():
                page.locator(f'#section-tabs button[data-section="{q["section"]}"]').click()
            else:
                if not page.locator('#challenges').is_visible():
                    page.locator('#home-button').click()
                page.locator(f'#challenge-grid button[data-section="{q["section"]}"]').click()
            page.get_by_role('button', name=re.compile('^Đến câu ' + qid[1:] + r'(?: –|$)')).click()
            expect(page.locator('#question-card')).to_have_attribute('data-question-id', qid)
            assert re.sub(r'\s+', ' ', page.locator('#prompt').inner_html()).strip() == re.sub(r'\s+', ' ', q['promptHtml']).strip()
            return q

        def check():
            page.locator('#check-answer').click()
            expect(page.locator('#feedback')).to_be_visible()

        def xp(value):
            expect(page.locator('#xp-total')).to_have_text(f'✦ {value} XP')

        go('q1')
        expect(page.locator('#feedback')).to_be_hidden()
        expect(page.locator('#transcript-panel')).to_be_hidden()
        assert page.locator('#transcript-content').inner_text() == ''
        page.locator('#check-answer').click()
        expect(page.locator('#answer-error')).to_contain_text('chọn hoặc nhập')
        xp(0)
        page.wait_for_function('document.querySelector("audio").readyState >= 1')
        assert page.locator('audio').evaluate('(a)=>a.duration') > 30
        for speed in ['0.75','1','1.25']:
            page.locator('#audio-speed').select_option(speed)
            assert page.locator('audio').evaluate('(a)=>a.playbackRate') == float(speed)
        page.locator('#audio-toggle').click()
        page.wait_for_function('!document.querySelector("audio").paused')
        page.locator('#audio-toggle').click()
        assert page.locator('audio').evaluate('(a)=>a.paused')
        page.locator('#audio-forward').click()
        page.wait_for_function('document.querySelector("audio").currentTime>=5')
        page.locator('#audio-back').click()
        page.wait_for_function('document.querySelector("audio").currentTime<2')
        page.locator('#audio-seek').fill('50')
        page.wait_for_function('Math.abs(document.querySelector("audio").currentTime/document.querySelector("audio").duration-.5)<.02')
        ratio = page.locator('audio').evaluate('(a)=>a.currentTime/a.duration')
        assert abs(ratio - .5) < .02
        page.locator('input[name=q1][value=C]').check()
        check();xp(10)
        expect(page.locator('#transcript-panel')).to_be_visible()
        assert page.locator('#transcript-content mark').count() > 0
        expect(page.locator('#explanation-content')).to_contain_text('Giải thích')
        expect(page.locator('#explanation-content')).to_contain_text('Dịch nghĩa')
        page.evaluate('document.querySelector("#check-answer").dispatchEvent(new MouseEvent("click"))')
        xp(10)
        page.locator('#audio-toggle').click()
        page.wait_for_function('!document.querySelector("audio").paused')
        passed('audio plays/pauses/replays after answer; ±5 seconds, seeking and all speeds work; transcript gated; correct answer +10 XP once')

        go('q16')
        assert page.locator('audio').evaluate('(a)=>a.paused')
        page.locator('input[name=q16][value=B]').check();check();xp(10)
        expect(page.locator('#feedback')).to_have_class(re.compile('is-wrong'))
        expect(page.locator('#explanation-content')).to_contain_text('interested in')
        expect(page.locator('#explanation-content')).to_contain_text('Lỗi thường gặp')
        page.locator('#next-question').click()
        if args.pilot:
            expect(page.locator('#question-card')).to_have_attribute('data-question-id','q23')
            page.locator('#previous-question').click()
        else:
            expect(page.locator('#question-card')).to_have_attribute('data-question-id','q17')
            page.locator('#previous-question').click()
        expect(page.locator('input[name=q16][value=B]')).to_be_checked()
        expect(page.locator('#feedback')).to_be_visible()
        passed('wrong answer explains grammar with no XP; next/previous and selected-answer/feedback retention work')

        go('q23');page.locator('#written-answer').fill('Cycling')
        go('q1');go('q23')
        expect(page.locator('#written-answer')).to_have_value('Cycling')
        check();xp(20)
        passed('typed draft persists across sections and accepts original answer case-insensitively')
        go('q26');expect(page.locator('#passage-panel')).to_be_visible()
        expect(page.locator('#passage-content')).to_contain_text('There are a lot of leisure activities')
        page.locator('input[name=q26][value=B]').check();check();xp(30)
        expect(page.locator('#passage-panel')).to_be_visible()
        passed('reading passage remains visible before and after answer; context-based explanation shown')

        go('q36')
        page.locator('#check-answer').click()
        expect(page.locator('#answer-error')).to_contain_text('đủ tất cả')
        page.locator('#word-bank button[data-token-index="3"]').click()
        page.locator('#word-bank button[data-token-index="5"]').click()
        page.locator('#undo-word').click()
        assert page.locator('#word-target button').count() == 1
        page.locator('#reset-words').click()
        assert page.locator('#word-target button').count() == 0
        page.locator('#word-bank button[data-token-index="3"]').click()
        go('q1');go('q36')
        assert page.locator('#word-target button').count() == 1
        page.locator('#word-target button').click()
        assert page.locator('#word-target button').count() == 0
        for i in [3,5,1,0,2,4,6]:
            page.locator(f'#word-bank button[data-token-index="{i}"]').click()
        check();xp(40)
        expect(page.locator('#explanation-content')).to_contain_text('The local people are kind and hospitable to visitors.')
        passed('sentence tokens selectable/removable, undo/reset, cross-section draft retention, complete-sentence grading and explanation work')

        # Pilot must pass ALL interaction checks before the full data is enabled.
        page.locator('#results-button').click()
        expect(page.locator('#result-correct')).to_have_text('4')
        expect(page.locator('#result-wrong')).to_have_text('1')
        expect(page.locator('#result-unanswered')).to_have_text(str(total-5))
        page.locator('#review-wrong').click()
        expect(page.locator('#feedback')).to_be_hidden()
        page.locator('input[name=q16][value=A]').check();check();xp(40)
        page.locator('#next-question').click()
        expect(page.locator('#review-summary')).to_contain_text('1 câu đã làm đúng')
        expect(page.locator('#result-correct')).to_have_text('4')
        go('q16')
        expect(page.locator('input[name=q16][value=B]')).to_be_checked()
        page.locator('#results-button').click()
        page.locator('#review-wrong').click()
        page.locator('input[name=q16][value=A]').check();check();xp(40)
        page.locator('#next-question').click()
        passed('summary counts correct/wrong/unanswered; repeat wrong-answer reviews award no XP and preserve original attempt')

        if not args.pilot:
            # Complete every remaining original question through real UI controls.
            already = {'q1','q16','q23','q26','q36'}
            for q in actual_source['questions']:
                if q['id'] in already:
                    continue
                go(q['id'])
                expect(page.locator('#feedback')).to_be_hidden()
                if q['section'] == 'listening':
                    expect(page.locator('#transcript-panel')).to_be_hidden()
                    page.wait_for_function('document.querySelector("audio").readyState >= 1')
                    assert page.locator('audio').evaluate('(a)=>a.duration') > 30
                if q['section'] == 'reading':
                    expect(page.locator('#passage-panel')).to_be_visible()
                if q['id'] == 'q13':
                    assert page.locator('.option u').count() == 4
                if q['kind'] == 'choice':
                    answer = 'A' if q['id']=='q29' else q['source']['correct']
                    page.locator(f'input[name={q["id"]}][value={answer}]').check()
                elif q['kind'] == 'text':
                    variants = page.evaluate('window.HT_GAME_TEXT_VARIANTS')
                    value = variants.get(q['id'], [q['source']['correct']])[0]
                    page.locator('#written-answer').fill(value)
                else:
                    indices = {'q37':[1,5,2,0,3,6,7,4,8], 'q38':[1,6,2,0,3,7,4,5,8,9]}[q['id']]
                    for i in indices:
                        page.locator(f'#word-bank button[data-token-index="{i}"]').click()
                check()
                expect(page.locator('#feedback')).to_have_class(re.compile('is-wrong') if q['id']=='q29' else re.compile(r'^feedback(?: celebrate)?$'))
                if q['id'] in ['q12','q13','q19','q29','q40']:
                    expect(page.locator('#explanation-content')).to_contain_text('Giáo viên cần xác nhận')
            xp(400)
            page.locator('#results-button').click()
            expect(page.locator('#result-correct')).to_have_text('40')
            expect(page.locator('#result-wrong')).to_have_text('2')
            expect(page.locator('#result-unanswered')).to_have_text('0')
            expect(page.locator('#result-xp')).to_have_text('400')
            page.locator('#review-wrong').click()
            page.locator('input[name=q16][value=A]').check();check();page.locator('#next-question').click()
            expect(page.locator('#question-card')).to_have_attribute('data-question-id','q29')
            page.locator('input[name=q29][value=D]').check();check();page.locator('#next-question').click()
            expect(page.locator('#review-summary')).to_contain_text('2 câu đã làm đúng')
            xp(400)
            passed('ALL 42 questions exercised: MCQ, true/false, 10 typed answers, 3 builders, both tracks, both readings, teacher flags; 40 correct + 2 wrong = 400 XP; mixed-section review works')
            # Reject broad substring false positives present in the old grader.
            page2=context.new_page();page2.on('pageerror',lambda error:errors.append(str(error)))
            page2.goto(base+path);page2.locator('#student-name').fill('Đối chiếu tự luận');page2.locator('#start-form button').click()
            page2.locator('#challenge-grid button[data-section="reading"]').click()
            page2.get_by_role('button',name='Đến câu 31',exact=True).click()
            page2.locator('#written-answer').fill('He does not collect water.');page2.locator('#check-answer').click()
            expect(page2.locator('#feedback-title')).to_contain_text('Chưa khớp đáp án mẫu')
            expect(page2.locator('#xp-total')).to_have_text('✦ 0 XP')
            page2.get_by_role('button',name='Đến câu 33',exact=True).click()
            page2.locator('#written-answer').fill('not yes');page2.locator('#check-answer').click()
            expect(page2.locator('#xp-total')).to_have_text('✦ 0 XP')
            page2.close()
            passed('free-text substring/negation false positives rejected without inventing answer variants')

        for width in [360,390,768,820,1280]:
            page.set_viewport_size({'width':width,'height':900})
            for screen in ['menu','listening','grammar','reading','writing','results']:
                if screen=='menu':
                    page.locator('#home-button').click()
                elif screen=='results':
                    page.locator('#results-button').click()
                else:
                    go({'listening':'q1','grammar':'q23','reading':'q26','writing':'q36'}[screen])
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), (width,screen,'horizontal overflow')
                if screen=='reading':
                    expect(page.locator('#passage-panel')).to_be_visible()
                if width in [390,1280] and screen in ['menu','reading','results']:
                    page.screenshot(path=str(ARTIFACTS/f'{"pilot" if args.pilot else "full"}-{screen}-{width}.png'),full_page=True)
        passed('all main screens responsive at 360, 390, 768, 820 and 1280px; reading remains visible; screenshots saved')

        mobile = browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
        mobile.route('**/*', route)
        touch=mobile.new_page();touch.on('pageerror',lambda error:errors.append(str(error)))
        assert touch.goto(base+'library/'+path).status==200
        touch.locator('#student-name').fill('Học sinh điện thoại');touch.locator('#start-form button').tap()
        touch.locator('#challenge-grid button[data-section="listening"]').tap()
        touch.locator('input[name=q1][value=C]').tap();touch.locator('#check-answer').tap()
        expect(touch.locator('#xp-total')).to_have_text('✦ 10 XP')
        touch.locator('#section-tabs button[data-section="writing"]').tap()
        for i in [3,5,1,0,2,4,6]:
            touch.locator(f'#word-bank button[data-token-index="{i}"]').tap()
        touch.locator('#check-answer').tap()
        expect(touch.locator('#xp-total')).to_have_text('✦ 20 XP')
        for filename in ['GHK1 K8 - part 1.mp3','GHK1 K8 - part 2 .mp3']:
            response=touch.request.get(base+'library/'+quote(RELATIVE+filename))
            assert response.status==200 and len(response.body())>1000000
        mobile.close()
        passed('real touch interactions work; GitHub Pages /library/ prefix resolves scripts, fonts and both original MP3 files')
        assert not errors, errors
        assert not external, external
        passed('no JavaScript/console errors; zero external/backend/Firebase requests')
        context.close();browser.close()
    report={'stage':'pilot' if args.pilot else 'full','passed':len(checks),'failed':0,'checks':checks,'consoleErrors':errors,'externalRequests':external,'browser':'Chromium','sourceBaseline':BASELINE}
    (ARTIFACTS/f'{report["stage"]}-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f'PASS {len(checks)} groups; artifacts: {ARTIFACTS}',flush=True)
finally:
    server.shutdown()
    server.server_close()
