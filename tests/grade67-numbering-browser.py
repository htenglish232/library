"""Grade 6/7 presentation and unchanged Grade 8/non-exam layout; Firebase is tested separately."""
from pathlib import Path
from urllib.parse import urlsplit, unquote, quote
import functools, http.server, json, os, re, shutil, subprocess, threading
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('GRADE67_NUMBERING_OUTPUT', '/tmp/ht-grade67-numbering'))
OUT.mkdir(parents=True, exist_ok=True)
data = json.loads((ROOT / 'catalog/current-library-catalog.json').read_text())['data']
old_view = subprocess.check_output(['git','show','808d2a6:assets/catalog-view.js'], cwd=ROOT, text=True).replace("'./school-folders.js?v=20261023-exam-numbering'", "'./school-folders-before-numbering.js'")
old_folders = subprocess.check_output(['git','show','808d2a6:assets/school-folders.js'], cwd=ROOT, text=True)
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
        browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'), args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
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
        page = page_for('catalog-view.js?v=20261023-grade67-numbering')
        inventory=json.loads((ROOT/'docs/grade67-exam-inventory.json').read_text())
        legacy=json.loads(json.dumps(data))
        for grade in legacy:
            for unit in grade['units']:unit['lessons']=[l for l in unit['lessons'] if not l['href'].endswith('/truc-tuan-dual-mode.html')]
        for target in [before,page]:target.evaluate('d=>window.view.setCatalog(d,2)',legacy)
        for grade in ['Grade 4','Grade 5','Grade 8']:
            snapshots=[]
            for target in [before,page]:
                target.get_by_role('button',name=grade,exact=True).click()
                snapshots.append(target.locator('#content').inner_html())
            assert snapshots[0]==snapshots[1],grade
        passed('all previous Grade 4/5/8 entries render exactly as before; the single new dual-mode entry is tested separately')
        for target in [before,page]:target.evaluate('d=>window.view.setCatalog(d,2)',data)
        for grade,total,school_count in [('Grade 6',16,14),('Grade 7',14,14)]:
            snapshots=[]
            for target in [before,page]:
                target.get_by_role('button',name=grade,exact=True).click()
                snapshots.append(target.locator('.grade-section.active > :not(.exam-school-folder)').evaluate_all('(els)=>els.map(e=>e.outerHTML)'))
            assert snapshots[0]==snapshots[1],grade
            folder=page.locator('.grade-section.active .exam-school-folder')
            expect(folder).to_have_count(1);folder.locator('.folder-head').click()
            expect(folder.locator('.school-folder')).to_have_count(school_count)
            expect(folder.locator('a.exam-resource')).to_have_count(total)
            expect(folder.locator('a.game-resource')).to_have_count(0)
            records=[r for r in inventory['rows'] if r['grade']==grade]
            for school in folder.locator('.school-folder').all():
                name=school.locator('.school-name').inner_text();summary=school.locator('summary')
                expected=[r for r in records if r['school']==name]
                assert expected,name
                expect(school.locator('a.lesson strong')).to_have_text([f'Đề số {r["examNumber"]} – {name}' for r in expected])
                assert school.locator('a.lesson').evaluate_all('(els)=>els.map(a=>a.getAttribute("href"))')==[r['href'] for r in expected]
                summary.click();expect(school.locator('a.lesson').first).to_be_visible()
                summary.focus();summary.press('Enter');expect(school.locator('a.lesson').first).to_be_hidden();summary.press('Enter')
            for record in records:
                response=page.request.get(base+'library/'+quote(record['href']))
                assert response.status==200 and response.body()==(ROOT/record['href']).read_bytes()
                for audio in record['audio']:
                    response=page.request.get(base+'library/'+quote(audio['path']))
                    assert response.status==200 and response.body()==(ROOT/audio['path']).read_bytes()
            passed(f'{grade}: {total} actual exams in {school_count} schools; no invented games; exact school labels/numbers, HTML/audio bytes and keyboard folder controls; vocabulary/grammar DOM unchanged')
            for width in [360,390,768,1280]:
                page.set_viewport_size({'width':width,'height':900})
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(grade,width)
                if width in [390,1280]:page.screenshot(path=str(OUT/f'{grade.replace(" ","-")}-{width}.png'),full_page=True)
            page.locator('#search').fill('Đề số 2')
            expect(page.locator('.grade-section.active a.lesson')).to_have_count(2 if grade=='Grade 6' else 0)
            page.locator('#search').fill('Đề 13')
            expect(page.locator('.grade-section.active a.lesson strong')).to_have_text('Đề số 1 – THCS Đào Sư Tích')
            page.locator('#search').fill('')
        passed('Grade 6/7 responsive at 360/390/768/1280px; new and original catalog titles remain searchable')
        changed=json.loads(json.dumps(data));grade=next(g for g in changed if g['grade']=='Grade 6');grade['grade']='Khối 6'
        unit=next(u for u in grade['units'] if u.get('type')=='exam-folder');unit['name']='Giữa kỳ'
        next(l for l in unit['lessons'] if '/4_THCS_Truc_Hung_(1)/' in l['href'])['hidden']=True
        page.evaluate('d=>window.view.setCatalog(d,2)',changed);page.get_by_role('button',name='Khối 6',exact=True).click()
        page.locator('#search').fill('Trực Hùng')
        expect(page.locator('.grade-section.active a.lesson strong')).to_have_text('Đề số 2 – THCS Trực Hùng')
        unit['hidden']=True;page.evaluate('d=>window.view.setCatalog(d,2)',changed)
        expect(page.locator('a[href^="grade-6/De_thi_GHK_1/"]')).to_have_count(0)
        passed('hidden first exam retains number 2 for the second; renamed grade/unit and hidden unit stay respected')
        future=json.loads(json.dumps(data));grade=next(g for g in future if g['grade']=='Grade 7')
        grade['units'].append({'name':'Đề thi HK2','type':'exam-folder','lessons':[
          {'title':f'{kind} số {number} – THCS Mới','href':f'grade-7/De_thi_HK2/new/{filename}-{number}.html'}
          for number in [2,1] for kind,filename in [('Game đề','game'),('Đề','exam')]
        ]})
        grade['units'][-1]['lessons'].append({'title':'Đề chưa rõ trường','href':'grade-7/De_thi_HK2/unknown/exam.html'})
        # Fixture-only future examples are not saved to the real catalog or repository.
        page.evaluate('d=>window.view.setCatalog(d,2)',future);page.get_by_role('button',name='Grade 7',exact=True).click()
        page.locator('#search').fill('THCS Mới')
        expect(page.locator('.grade-section.active a.lesson strong')).to_have_text([
          'Đề số 1 – THCS Mới','Game đề số 1 – THCS Mới','Đề số 2 – THCS Mới','Game đề số 2 – THCS Mới'])
        page.locator('#search').fill('Chưa phân loại')
        expect(page.locator('.school-name')).to_have_text('Đề thi chưa phân loại')
        expect(page.locator('.grade-section.active a.lesson strong')).to_have_text('Đề số 1 – Chưa phân loại')
        expect(page.locator('.unclassified-title')).to_have_text('Đề chưa rõ trường')
        expect(page.locator('.exam-school-folder > .folder-head .badge')).to_have_text('1 nhóm chưa phân loại')
        page.evaluate('window.view.clearCatalog()');expect(page.locator('#content')).to_be_empty()
        passed('future Grade 7 exam/game pairs and another exam set work through the catalog; unknown school retains its original title in an unclassified folder; clear removes all links')
        # Exercise a real MP3 from each grade using the native browser media stack.
        for grade in ['Grade 6','Grade 7']:
            audio=next(a for r in inventory['rows'] if r['grade']==grade for a in r['audio'] if a['src'].lower().endswith('.mp3'))
            page.evaluate('(url)=>{window.checkAudio?.pause();window.checkAudio=new Audio(url);checkAudio.load();}',base+'library/'+quote(audio['path']))
            page.wait_for_function('checkAudio.readyState>=1 && Number.isFinite(checkAudio.duration) && checkAudio.duration>0')
            page.evaluate('checkAudio.play()');page.wait_for_function('!checkAudio.paused');page.evaluate('checkAudio.pause()')
        passed('real MP3 playback from both Grade 6 and Grade 7 under /library/; all 42 original audio references return exact bytes')
        assert not errors,errors;assert not external,external
        passed('zero JavaScript/console errors and zero production/Firebase requests in presentation tests')
        browser.close()
    (OUT/'report.json').write_text(json.dumps({'passed':len(checks),'failed':0,'checks':checks,'consoleErrors':errors},ensure_ascii=False,indent=2)+'\n')
finally:
    server.shutdown();server.server_close()
