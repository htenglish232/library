"""Real Library markup/catalog with a local access fixture, no production Firebase."""
from pathlib import Path
import functools, http.server, json, os, shutil, threading
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[2]
SERVE=Path(os.environ.get('HT_LIBRARY_SERVE_ROOT',str(ROOT)))
OUT=Path('/tmp/ht-test-speaking-library');OUT.mkdir(exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
    def translate_path(self,path):
        if path.startswith('/library/'):path=path[len('/library'):]
        return super().translate_path(path)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(SERVE)))
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}'
data=json.loads((ROOT/'catalog/current-library-catalog.json').read_text())['data']
fixture="import {setCatalog} from './catalog-view.js';setCatalog("+json.dumps(data)+",2);for(const id of ['library','library-hero','library-search'])document.getElementById(id).hidden=false;document.getElementById('auth-panel').hidden=true;"
errors=[];external=[]
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'),args=['--no-sandbox'])
        context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce')
        context.route('**/*',lambda r:r.continue_() if r.request.url.startswith(BASE+'/') else (external.append(r.request.url),r.abort())[-1])
        context.route('**/assets/library.js*',lambda r:r.fulfill(content_type='text/javascript',body=fixture))
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE+'/library/index.html')
        expect(page.locator('#tabs button')).to_have_text([grade['grade'] for grade in data])
        assert page.locator('a.lesson').evaluate_all('(els)=>els.map(a=>a.getAttribute("href"))')==[lesson['href'] for unit in data[0]['units'] for lesson in unit['lessons']]
        entry=page.get_by_role('link',name='Test Speaking Speaking Cards · Practice & Test →')
        expect(entry).to_have_attribute('href','test-speaking/index.html')
        page.screenshot(path=str(OUT/'main-library-entry.png'),full_page=True)
        entry.click();expect(page).to_have_url(BASE+'/library/test-speaking/index.html')
        expect(page.locator('#browse-folders>button')).to_have_count(1)
        expect(page.get_by_role('button',name='Mở Grade 3',exact=True)).to_be_visible()
        page.screenshot(path=str(OUT/'speaking-grades.png'),full_page=True)
        page.get_by_role('button',name='Mở Grade 3',exact=True).click()
        page.get_by_role('button',name='Mở Global Success',exact=True).click()
        expect(page.get_by_role('button',name='Mở Unit 5',exact=True)).to_contain_text('14 Speaking Cards')
        page.screenshot(path=str(OUT/'speaking-units.png'),full_page=True)
        page.get_by_role('button',name='Mở Unit 5',exact=True).click()
        expect(page.locator('.set-tile')).to_have_count(1)
        for label in ['Review · 8','Extension · 1','Unit 5 Core · 5']:expect(page.get_by_text(label,exact=True)).to_be_visible()
        for label in ['Practice →','Sequential Test','Random Test']:expect(page.get_by_role('button',name=label,exact=True)).to_be_visible()
        page.screenshot(path=str(OUT/'speaking-unit5.png'),full_page=True)
        page.get_by_role('button',name='Random Test',exact=True).click()
        expect(page.locator('input[value=random]')).to_be_checked()
        page.locator('#setup-scope').select_option('unit5');page.get_by_role('button',name='Bắt đầu Test →').click()
        ids=[page.locator('#speaking-card').get_attribute('data-card-id')]
        page.locator('#next-card').click();second=page.locator('#speaking-card').get_attribute('data-card-id')
        page.locator('#previous-card').click();assert page.locator('#speaking-card').get_attribute('data-card-id')==ids[0]
        page.locator('#next-card').click();assert page.locator('#speaking-card').get_attribute('data-card-id')==second
        page.locator('#exit-session').click()
        expect(page.get_by_role('button',name='Mở Unit 5',exact=True)).to_be_visible()
        page.locator('#all-grades').click();expect(page.get_by_role('button',name='Mở Grade 3',exact=True)).to_be_visible()
        page.locator('.main-library-link').click();expect(page).to_have_url(BASE+'/library/index.html')
        expect(page.locator('#tabs button')).to_have_text([grade['grade'] for grade in data])
        page.goto(BASE+'/library/speaking-cards/')
        page.wait_for_url('**/library/test-speaking/index.html')
        page.locator('#search').fill('Unit 5');expect(page.locator('.set-tile')).to_have_count(1)
        page.set_viewport_size({'width':390,'height':844})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        page.screenshot(path=str(OUT/'speaking-mobile.png'),full_page=True)
        page.locator('#new-set').click()
        for key,value in [('title','Empty teacher draft'),('grade','Grade 99'),('textbook','Draft'),('unit','Unit 99')]:page.locator('#set-'+key).fill(value)
        page.locator('#set-form button[type=submit]').click();page.locator('#editor-dialog [data-close]').click()
        page.locator('#all-grades').click()
        expect(page.locator('[data-grade="Grade 99"]')).to_have_count(0)
        expect(page.locator('[data-grade="Grade 3"]')).to_be_visible()
        page.locator('#search').fill('Empty teacher draft')
        expect(page.locator('.set-tile')).to_have_count(1)
        expect(page.get_by_role('button',name='Chỉnh sửa bộ thẻ',exact=True)).to_be_visible()
        assert not errors,errors;assert not external,external
        (OUT/'report.json').write_text(json.dumps({'serverRoot':str(SERVE),'checks':['Library categories and entry','Grade → textbook → Unit → cards','three mode buttons','Core random navigation state','back to Units/Grades/Library','legacy redirect','mobile and project Pages paths'],'errors':errors,'externalRequests':external,'firebaseAccess':'local fixture; production not contacted'},ensure_ascii=False,indent=2))
        browser.close()
finally:server.shutdown()
print('PASS Library → Test Speaking → Grade 3 → Global Success → Unit 5; 7 navigation groups; no production calls')
