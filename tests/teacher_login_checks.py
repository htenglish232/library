"""Browser checks for the static catalog gate. No real credentials are used."""
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from datetime import datetime, timezone
import hashlib
import json
import secrets
import subprocess
from urllib.parse import quote
from urllib.request import urlopen, Request

from playwright.sync_api import sync_playwright, expect, Error

ROOT = Path(__file__).resolve().parents[1]
KEY = 'ht-english:teacher-session:v1'
DURATION = 30 * 24 * 60 * 60 * 1000
PASSWORD = secrets.token_urlsafe(24)  # Never persisted or printed.
SALT = secrets.token_hex(16)
ACCOUNT = dict(username='test.teacher', id=secrets.token_hex(16),
               algorithm='PBKDF2-SHA-256', iterations=600000, salt=SALT,
               verifier=hashlib.pbkdf2_hmac('sha256', PASSWORD.encode(), bytes.fromhex(SALT), 600000).hex())
CONFIG = dict(schemaVersion=1, accounts=[ACCOUNT])


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def login(page, base):
    page.goto(base)
    expect(page.locator('#teacher-username')).to_be_enabled()
    page.locator('#teacher-username').fill(ACCOUNT['username'])
    page.locator('#teacher-password').fill(PASSWORD)
    page.locator('#login-submit').click()
    expect(page.locator('#teacher-library')).to_be_visible()


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT.parent)))
    Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}/library/'
    checks = []
    skipped = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])

        @contextmanager
        def context(config=CONFIG, **options):
            ctx = browser.new_context(**options)
            errors = []
            ctx.on('page', lambda p: p.on('pageerror', lambda e: errors.append(str(e))))
            if config is not None:
                ctx.route('**/teacher-access/teacher-accounts.json', lambda route: route.fulfill(json=config))
            try:
                yield ctx
                assert not errors, errors
            finally:
                ctx.close()

        with context(viewport={'width': 1440, 'height': 1000}) as ctx:
            page = ctx.new_page(); page.goto(base)
            expect(page.locator('#teacher-username')).to_be_enabled()
            expect(page.locator('#teacher-library')).to_be_hidden()
            assert page.locator('.lesson:visible').count() == 0
            page.locator('#teacher-username').fill('unknown')
            page.locator('#teacher-password').fill('incorrect-password')
            page.locator('#login-submit').click()
            expect(page.locator('#login-message')).to_contain_text('chưa đúng')
            expect(page.locator('#teacher-library')).to_be_hidden()
            page.locator('#teacher-username').fill(ACCOUNT['username'])
            page.locator('#teacher-password').fill('incorrect-password')
            page.locator('#show-password').click()
            assert page.locator('#teacher-password').get_attribute('type') == 'text'
            page.locator('#show-password').click()
            page.locator('#login-submit').click()
            expect(page.locator('#login-message')).to_contain_text('chưa đúng')
            login(page, base)
            session = page.evaluate('(key) => JSON.parse(localStorage.getItem(key))', KEY)
            assert session['expiresAt'] - session['issuedAt'] == DURATION
            assert PASSWORD not in json.dumps(session)
            assert 'password' not in session and 'verifier' not in session
            page.locator('#search').fill('Unit 1')
            assert page.locator('.lesson:visible').count() > 0
            page.screenshot(path='/tmp/ht-library-desktop.png', full_page=True)
            page.close(); page = ctx.new_page(); page.goto(base)
            expect(page.locator('#teacher-library')).to_be_visible()
            # Same origin storage is also restored in a new browser context.
            state = ctx.storage_state()
            restored = browser.new_context(storage_state=state)
            restored.route('**/teacher-access/teacher-accounts.json', lambda r: r.fulfill(json=CONFIG))
            rp = restored.new_page(); rp.goto(base)
            expect(rp.locator('#teacher-library')).to_be_visible(); restored.close()
            other = ctx.new_page(); other.goto(base)
            expect(other.locator('#teacher-library')).to_be_visible()
            page.locator('#teacher-logout').click()
            expect(page.locator('#teacher-login')).to_be_visible()
            expect(other.locator('#teacher-login')).to_be_visible()
            assert page.evaluate('(key) => localStorage.getItem(key)', KEY) is None
            page.go_back(); page.goto(base)
            expect(page.locator('#teacher-library')).to_be_hidden()
            checks.append('desktop: wrong/right password, search, 30-day persistence, new context, logout across tabs')

        for width in [360, 375, 390, 430, 768]:
            with context(viewport={'width': width, 'height': 844}, is_mobile=True, has_touch=True) as ctx:
                page = ctx.new_page(); page.goto(base)
                expect(page.locator('#teacher-username')).to_be_enabled()
                page.evaluate('document.fonts.ready'); assert page.evaluate("document.fonts.check('400 16px \"Noto Sans\"', 'Thầy cô')")
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
                assert page.locator('#login-submit').bounding_box()['height'] >= 44
                if width == 390:
                    page.screenshot(path='/tmp/ht-login-mobile.png', full_page=True)
                login(page, base)
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
                for tab in page.locator('.tab').all():
                    tab.click()
                    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'), width
                if width == 390:
                    page.screenshot(path='/tmp/ht-library-mobile.png', full_page=True)
                page.locator('#teacher-logout').click()
                expect(page.locator('#teacher-login')).to_be_visible()
            checks.append(f'mobile/tablet {width}px: Noto Sans, no overflow, login, grade tabs, logout')

        with context() as ctx:
            page = ctx.new_page(); login(page, base)
            # Test just before and exactly at 30 days using browser's controllable clock.
            session = page.evaluate('(key) => JSON.parse(localStorage.getItem(key))', KEY)
            page.clock.set_fixed_time(datetime.fromtimestamp((session['expiresAt'] - 1) / 1000, timezone.utc))
            page.evaluate("window.dispatchEvent(new Event('focus'))")
            expect(page.locator('#teacher-library')).to_be_visible()
            page.clock.set_fixed_time(datetime.fromtimestamp(session['expiresAt'] / 1000, timezone.utc))
            page.evaluate("window.dispatchEvent(new Event('focus'))")
            expect(page.locator('#teacher-library')).to_be_hidden()
            expect(page.locator('#login-message')).to_contain_text('hết hạn')
            checks.append('30-day expiry boundary while page remains open')

        for mutation in ['broken', 'expired', 'future', 'extended', 'revoked']:
            with context() as ctx:
                page = ctx.new_page(); login(page, base)
                page.evaluate('''([key, mutation]) => {
                  const session = JSON.parse(localStorage.getItem(key)), now = Date.now();
                  if (mutation === 'expired') {session.issuedAt = now - 2592000001; session.expiresAt = now - 1;}
                  if (mutation === 'future') {session.issuedAt = now + 10000; session.expiresAt = session.issuedAt + 2592000000;}
                  if (mutation === 'extended') session.expiresAt += 1000;
                  if (mutation === 'revoked') session.accountId = 'old-account';
                  localStorage.setItem(key, mutation === 'broken' ? 'invalid json' : JSON.stringify(session));
                }''', [KEY, mutation])
                page.reload(); expect(page.locator('#teacher-library')).to_be_hidden()
                assert page.evaluate('(key) => localStorage.getItem(key)', KEY) is None
            checks.append(f'invalid session rejected: {mutation}')

        for config in [None, {'schemaVersion': 1, 'accounts': []}, {'schemaVersion': 1, 'accounts': [{'username': 'bad'}]}]:
            with context(config=config) as ctx:
                page = ctx.new_page(); page.goto(base)
                expect(page.locator('#login-message')).not_to_contain_text('Đang kiểm tra')
                expect(page.locator('#teacher-library')).to_be_hidden()
                expect(page.locator('#login-submit')).to_be_disabled()
            checks.append('empty/malformed real or intercepted configuration stays locked')
        with context() as ctx:
            ctx.unroute('**/teacher-access/teacher-accounts.json')
            ctx.route('**/teacher-access/teacher-accounts.json', lambda r: r.fulfill(status=503, body='Unavailable'))
            page = ctx.new_page(); page.goto(base)
            expect(page.locator('#login-message')).to_contain_text('Không tải được')
            expect(page.locator('#teacher-library')).to_be_hidden()
            checks.append('configuration HTTP failure stays locked')

        for blocked in ['localStorage', 'both']:
            with context() as ctx:
                ctx.add_init_script("""Object.defineProperty(window, 'localStorage', {get() {throw new Error('Blocked');}});""")
                if blocked == 'both':
                    ctx.add_init_script("""Object.defineProperty(window, 'sessionStorage', {get() {throw new Error('Blocked');}});""")
                page = ctx.new_page(); login(page, base)
                expect(page.locator('#session-notice')).to_contain_text('tạm thời')
                page.reload()
                expect(page.locator('#teacher-library')).to_be_visible() if blocked == 'localStorage' else expect(page.locator('#teacher-library')).to_be_hidden()
                if blocked == 'both':
                    login(page, base)
                page.locator('#teacher-logout').click()
                expect(page.locator('#teacher-library')).to_be_hidden()
            checks.append(f'blocked storage fallback: {blocked}')

        with context(viewport={'width': 390, 'height': 844}, accept_downloads=True) as ctx:
            page = ctx.new_page(); page.goto(base + 'teacher-access/create-account.html')
            assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
            page.locator('#new-username').fill('new.teacher')
            page.locator('#new-password').fill(PASSWORD)
            page.locator('#confirm-password').fill('different-password')
            page.locator('#create-submit').click()
            expect(page.locator('#account-message')).to_contain_text('chưa giống')
            page.locator('#confirm-password').fill(PASSWORD)
            page.locator('#existing-accounts').set_input_files({'name': 'teacher-accounts.json', 'mimeType': 'application/json', 'buffer': json.dumps(CONFIG).encode()})
            page.locator('#create-submit').click()
            expect(page.locator('#account-download')).to_be_visible()
            with page.expect_download() as download_event:
                page.locator('#account-download').click()
            generated = json.loads(Path(download_event.value.path()).read_text())
            assert PASSWORD not in json.dumps(generated)
            assert len(generated['accounts']) == 2 and generated['accounts'][0] == ACCOUNT
            a = generated['accounts'][1]
            assert a['verifier'] == hashlib.pbkdf2_hmac('sha256', PASSWORD.encode(), bytes.fromhex(a['salt']), 600000).hex()
            assert page.locator('#new-password').input_value() == ''
            ctx.unroute('**/teacher-access/teacher-accounts.json')
            ctx.route('**/teacher-access/teacher-accounts.json', lambda r: r.fulfill(json=generated))
            page.goto(base); expect(page.locator('#teacher-username')).to_be_enabled()
            page.locator('#teacher-username').fill('new.teacher'); page.locator('#teacher-password').fill(PASSWORD)
            page.locator('#login-submit').click(); expect(page.locator('#teacher-library')).to_be_visible()
            checks.append('account generator: mismatch, retain existing account, downloaded PBKDF2 hash, generated login')
        # Offline ZIP workflow for the generator must work without HTTP.
        with context() as ctx:
            page = ctx.new_page()
            try:
                page.goto((ROOT / 'teacher-access/create-account.html').as_uri())
            except Error as error:
                if 'ERR_BLOCKED_BY_ADMINISTRATOR' not in str(error):
                    raise
                skipped.append('offline ZIP/file URL: cloud Chromium administrative policy blocks file URLs; HTTP generator verified')
            else:
                page.locator('#new-username').fill('offline.teacher')
                page.locator('#new-password').fill(PASSWORD); page.locator('#confirm-password').fill(PASSWORD)
                page.locator('#create-submit').click(); expect(page.locator('#account-download')).to_be_visible()
                checks.append('account generator works from local ZIP/file URL')

        with context(config=None) as ctx:
            page = ctx.new_page(); page.goto(base)
            catalog = page.evaluate('DATA')
            original = subprocess.check_output(['git', 'show', '8c6361c:index.html'], cwd=ROOT, text=True)
            # The complete original catalog rendering script is unchanged.
            assert original.split('<script>')[1].split('</script>')[0] == (ROOT / 'index.html').read_text().split('<script>')[1].split('</script>')[0]
            paths = [lesson['href'] for grade in catalog for unit in grade['units'] for lesson in unit['lessons']]
            for path in paths:
                assert (ROOT / path).is_file(), path
                with urlopen(Request(base + quote(path), method='HEAD')) as response:
                    assert response.status == 200, path
            # A representative exam opens and grades without any teacher session.
            exam = next(ROOT.glob('grade-7/De_thi_GHK_1/*/*.html'))
            page.goto(base + quote(str(exam.relative_to(ROOT))))
            assert page.locator('#teacher-login').count() == 0
            expect(page.locator('#submitBtn')).to_be_visible()
            page.locator('#submitBtn').click(); page.locator('#confirmSubmit').click()
            expect(page.locator('#submissionBanner')).to_be_visible()
            assert page.locator('.feedback-box:visible').count() > 0
            checks.append(f'original rendering script unchanged; all {len(paths)} catalog links resolve; direct exam grading without login')
        browser.close()
    server.shutdown(); server.server_close()
    for check in checks:
        print('PASS:', check)
    for check in skipped:
        print('SKIP:', check)
    print(f'{len(checks)} check groups passed. Browser: Chromium; mobile viewports simulated, not physical devices.')


if __name__ == '__main__':
    main()
