"""Isolated catalog presentation checks; Firebase access is tested by auth-browser.py."""
from pathlib import Path
from urllib.parse import urlsplit, unquote, quote
import functools, http.server, json, os, re, shutil, subprocess, threading
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('GRADE8_NUMBERING_OUTPUT', '/tmp/ht-grade8-numbering'))
OUT.mkdir(parents=True, exist_ok=True)
data = json.loads((ROOT / 'catalog/current-library-catalog.json').read_text())['data']
old_view = subprocess.check_output(['git','show','a8a38ed:assets/catalog-view.js'], cwd=ROOT, text=True).replace("'./school-folders.js'", "'./school-folders-before-numbering.js'")
old_folders = subprocess.check_output(['git','show','a8a38ed:assets/school-folders.js'], cwd=ROOT, text=True)
fixture = re.sub(r'<script type="module"[^>]*></script>', '', (ROOT / 'index.html').read_text())

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
    def translate_path(self, path):
        if path.startswith('/library/'): path = path[len('/library'):]
        return super().translate_path(path)

server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(ROOT)))
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{server.server_port}/'
errors, external, checks = [], [], []
def passed(message):
    checks.append(message)
    print('PASS ' + message, flush=True)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'), args=['--no-sandbox'])
        context = browser.new_context(viewport={'width':1280,'height':900}, reduced_motion='reduce')
        def route(r):
            path = urlsplit(r.request.url).path
            if not r.request.url.startswith(base): external.append(r.request.url); r.abort()
            elif path.endswith('/catalog-fixture.html'): r.fulfill(content_type='text/html', body=fixture)
            elif path.endswith('/assets/catalog-view-before-numbering.js'): r.fulfill(content_type='text/javascript', body=old_view)
            elif path.endswith('/assets/school-folders-before-numbering.js'): r.fulfill(content_type='text/javascript', body=old_folders)
            else: r.continue_()
        context.route('**/*', route)
        def page_for(module):
            page = context.new_page(); page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('console', lambda m: errors.append(m.text) if m.type=='error' else None)
            page.goto(base + 'library/catalog-fixture.html')
            page.evaluate('''async module => {
              window.view = await import('./assets/' + module);
              for(const id of ['library','library-hero','library-search'])document.getElementById(id).hidden=false;
              document.getElementById('auth-panel').hidden=true;
            }''', module)
            page.evaluate('(data)=>window.view.setCatalog(data,2)', data)
            return page
        before = page_for('catalog-view-before-numbering.js')
        page = page_for('catalog-view.js?v=20261023-exam-numbering')
        for grade in ['Grade 4','Grade 5']:
            snapshots=[]
            for target in [before,page]:
                target.get_by_role('button', name=grade, exact=True).click()
                snapshots.append(target.locator('#content').inner_html())
            assert snapshots[0]==snapshots[1], grade
        passed('Grade 4/5 rendered DOM exactly matches the previous implementation; Grade 6/7 have their own numbering checks')
        page.get_by_role('button', name='Grade 8', exact=True).click()
        folder = page.locator('.exam-school-folder')
        expect(folder).to_have_count(1); folder.locator('.folder-head').click()
        schools=folder.locator('.school-folder'); expect(schools).to_have_count(17)
        expect(folder.locator('a.exam-resource')).to_have_count(19)
        expect(folder.locator('a.game-resource')).to_have_count(23)
        hrefs=folder.locator('a.lesson').evaluate_all('(els)=>els.map(a=>a.getAttribute("href"))')
        assert len(set(hrefs))==42
        for href in hrefs:
            response=page.request.get(base+'library/'+quote(href))
            assert response.status==200 and response.body()==(ROOT/unquote(href)).read_bytes(),href
        for name in ['Trực Tuấn','Trực Khang','Trực Hùng','Trực Chính']:
            school=schools.filter(has=page.locator('.school-name',has_text='THCS '+name))
            summary=school.locator('summary');summary.click()
            expect(school.locator('a.lesson strong')).to_have_text([f'Đề số 1 – THCS {name}',f'Game đề số 1 – THCS {name}']+[f'Game đề số 1 – THCS {name} (2 chế độ)'])
            expect(school.locator('.exam-pair')).to_have_count(1)
            expect(school.locator('a.lesson').first).to_be_visible()
            summary.focus();summary.press('Enter');expect(school.locator('a.lesson').first).to_be_hidden();summary.press('Enter')
        for name in ['Đào Sư Tích','Phương Định']:
            school=schools.filter(has=page.locator('.school-name',has_text='THCS '+name))
            expect(school.locator('a.lesson strong')).to_have_text([label for n in [1,2] for label in [f'Đề số {n} – THCS {name}',f'Game đề số {n} – THCS {name} (2 chế độ)']])
            expect(school.locator('a.game-resource')).to_have_count(2)
        passed('17 school folders, 19 numbered exams, 23 paired games; all 42 exact HTML files resolve under /library/; keyboard open/close works')
        for width in [360,390,768,1280]:
            page.set_viewport_size({'width':width,'height':900})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),width
            pair=schools.filter(has=page.locator('.school-name',has_text='THCS Trực Hùng')).locator('.exam-pair')
            columns=pair.evaluate('e=>getComputedStyle(e).gridTemplateColumns.split(" ").length')
            assert columns==(1 if width<=600 else 2),width
            if width in [390,1280]:page.screenshot(path=str(OUT/f'schools-{width}.png'),full_page=True)
        passed('numbered exam/game pairs share a row on desktop and stack on mobile; 360/390/768/1280px without horizontal overflow')
        page.locator('#search').fill('Đề số 2')
        expect(page.locator('.grade-section.active a.lesson')).to_have_count(4)
        page.locator('#search').fill('Game đề số 1')
        expect(page.locator('.grade-section.active a.game-resource')).to_have_count(21)
        page.locator('#search').fill('Đề 19')
        expect(page.locator('.grade-section.active a.lesson strong')).to_have_text('Đề số 1 – THCS Trực Chính')
        passed('new numbered names and original catalog names remain searchable without renumbering or duplicates')
        changed=json.loads(json.dumps(data));grade=next(g for g in changed if g['grade']=='Grade 8');grade['grade']='Khối 8'
        unit=next(u for u in grade['units'] if u.get('type')=='exam-folder');unit['name']='Đề giữa kỳ'
        for lesson in unit['lessons']:
            if '/8_THCS Phuong Dinh/' in lesson['href'] or lesson['href'].endswith('/1. THCS Truc Tuan.html'):lesson['hidden']=True
        page.evaluate('d=>window.view.setCatalog(d,2)',changed);page.get_by_role('button',name='Khối 8',exact=True).click()
        page.locator('#search').fill('Phương Định')
        expect(page.locator('.grade-section.active a.lesson strong')).to_have_text(['Đề số 2 – THCS Phương Định','Game đề số 2 – THCS Phương Định (2 chế độ)'])
        page.locator('#search').fill('Trực Tuấn')
        expect(page.locator('.grade-section.active a.lesson strong')).to_have_text(['Game đề số 1 – THCS Trực Tuấn','Game đề số 1 – THCS Trực Tuấn (2 chế độ)'])
        unit['hidden']=True;page.evaluate('d=>window.view.setCatalog(d,2)',changed)
        expect(page.locator('a[href^="grade-8/De_thi_GHK1/"]')).to_have_count(0)
        passed('hidden exam 1 never relabels exam 2; a visible game keeps its hidden-source pairing; renamed grades/units and hidden units are respected')
        future=json.loads(json.dumps(data));grade=next(g for g in future if g['grade']=='Grade 8')
        grade['units'].append({'name':'Đề thi HK2','type':'exam-folder','lessons':[
          {'title':f'{kind} số {number} – THCS Mới','href':f'grade-8/De_thi_HK2/new/{filename}-{number}.html'}
          for number in [2,1] for kind,filename in [('Game đề','game'),('Đề','exam')]
        ]})
        # Synthetic future data exercises rendering only; it is never saved or published.
        page.evaluate('d=>window.view.setCatalog(d,2)',future);page.get_by_role('button',name='Grade 8',exact=True).click()
        page.locator('#search').fill('THCS Mới')
        expect(page.locator('.grade-section.active a.lesson strong')).to_have_text([
          'Đề số 1 – THCS Mới','Game đề số 1 – THCS Mới','Đề số 2 – THCS Mới','Game đề số 2 – THCS Mới'])
        page.evaluate('window.view.clearCatalog()');expect(page.locator('#content')).to_be_empty();expect(page.locator('#tabs')).to_be_empty()
        passed('future explicit catalog names and another Grade 8 exam set render in numeric pair order; clearing the catalog removes all material DOM')
        assert not errors,errors;assert not external,external
        passed('zero JavaScript/console errors and zero external/Firebase requests in the isolated rendering checks')
        browser.close()
    (OUT/'report.json').write_text(json.dumps({'passed':len(checks),'failed':0,'checks':checks,'consoleErrors':errors},ensure_ascii=False,indent=2)+'\n')
finally:
    server.shutdown();server.server_close()
