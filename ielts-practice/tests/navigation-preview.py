"""Check Library link, built artifact links and downloadable file:// preview."""
from pathlib import Path
from urllib.parse import urlparse
import argparse, functools, http.server, json, os, shutil, threading
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser();parser.add_argument('--root',default=str(ROOT));parser.add_argument('--preview',default='/tmp/ielts-unit2-preview.html');args=parser.parse_args()
OUT=Path('/tmp/ht-ielts-preview');OUT.mkdir(exist_ok=True)
PREVIEW=Path(args.preview)
key=json.loads((ROOT/'ielts-practice/unit-2-individuals-and-families/answers.json').read_text())
class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
    def translate_path(self,path):
        if path.startswith('/library/'):path=path[len('/library'):]
        return super().translate_path(path)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=args.root))
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}'
errors=[]
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'),args=['--no-sandbox'])
        context=browser.new_context(viewport={'width':1440,'height':1000})
        # A local auth fixture avoids production Firebase while checking the entry.
        context.route('**/assets/library.js*',lambda r:r.fulfill(body="document.getElementById('library').hidden=false;document.getElementById('auth-panel').hidden=true;",content_type='text/javascript'))
        context.route('**/*',lambda r:r.fallback() if r.request.url.startswith(BASE+'/') or r.request.url.startswith('file:') else r.abort())
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE+'/library/index.html')
        page.get_by_role('link',name='IELTS Practice Vocabulary · Reading · Translation →').click()
        page.get_by_role('link',name='Mở phiếu Unit 2 →').click()
        expect(page.locator('#welcome')).to_be_visible()
        assert '/library/ielts-practice/unit-2-individuals-and-families/index.html' in page.url
        page.locator('.library-link').click();assert page.url==BASE+'/library/index.html'
        print('PASS Library → IELTS Practice → Unit 2 and back under /library/; Firebase fixture only')
        for path in ['unit.json','answers.json','support.json','sources/worksheet.pdf','sources/answer-key.pdf']:
            response=context.request.get(BASE+'/library/ielts-practice/unit-2-individuals-and-families/'+path)
            assert response.status==200,(response.status,path)
        print('PASS worksheet/key JSON and original PDF paths')
        context.close()
        assert PREVIEW.exists(), 'Build the downloadable preview first'
        if PREVIEW.exists():
            context=browser.new_context(viewport={'width':390,'height':844});requests=[]
            context.route('http**/*',lambda r:(requests.append(r.request.url),r.abort())[-1])
            page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(PREVIEW.as_uri())
            expect(page.locator('#welcome')).to_be_visible()
            page.locator('#student-name').fill('Xem thử HTML');page.locator('#start-form button').click()
            expect(page.locator('.passage-section')).to_have_count(10)
            page.locator('#vocabulary-reading-top').click()
            page.locator('#step-picker').evaluate('e=>e.open=true')
            page.get_by_role('button',name='C · Câu 1',exact=True).click()
            page.locator('input[value=B]').check();page.locator('#check-answer').click()
            expect(page.locator('#feedback .keyword-list')).to_be_visible()
            page.reload();expect(page.locator('input[value=B]')).to_be_disabled()
            page.locator('#step-picker').evaluate('e=>e.open=true')
            page.get_by_role('button',name='E · Translation',exact=True).click()
            page.locator('#translation-input').fill('This is a preview draft.');page.reload()
            expect(page.locator('#translation-input')).to_have_value('This is a preview draft.')
            page.locator('#submit-open').click();page.locator('#submit-confirm').click()
            expect(page.locator('#results')).to_be_visible()
            assert page.locator('#result-stats strong').all_text_contents()==['20','1','0','19']
            page.locator('#reference-details summary').click()
            expect(page.locator('.reference-translation')).to_have_text(key['referenceTranslation'])
            assert not requests,requests
            page.screenshot(path=str(OUT/'downloadable-preview-mobile.png'),full_page=True)
            print('PASS downloaded standalone HTML opens on file://; inputs persist, submits/grades, reference displays; no external assets or requests')
            context.close()
        assert not errors,errors
        browser.close()
finally:server.shutdown()
