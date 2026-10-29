"""Grade 3 catalog and the supplied 20-question Unit 8 lesson, without Firebase writes."""
from pathlib import Path
from urllib.parse import quote, urlsplit
import functools, http.server, json, re, threading
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = Path('/tmp/ht-grade3-unit8'); OUT.mkdir(exist_ok=True)
lesson = 'grade-3/Bo_Tro_Ngu_Phap/unit_08_these_those.html'
server_catalog = json.loads((ROOT/'catalog/library-catalog.json').read_text())['data']
fixture = re.sub(r'<script type="module"[^>]*></script>', '', (ROOT/'index.html').read_text())

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
    def translate_path(self, path):
        return super().translate_path(path[len('/library'):] if path.startswith('/library/') else path)

server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(ROOT)))
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{server.server_port}/'
errors, bad = [], []

try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        context = browser.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True)
        context.add_init_script("""
          window.__spoken=[];
          window.SpeechSynthesisUtterance=class { constructor(text){this.text=text;} };
          Object.defineProperty(window,'speechSynthesis',{value:{cancel(){},speak(u){window.__spoken.push({text:u.text,lang:u.lang,rate:u.rate});}},configurable:true});
        """)
        def route(request):
            if urlsplit(request.request.url).path.endswith('/catalog-fixture.html'):
                request.fulfill(content_type='text/html', body=fixture)
            elif request.request.url.startswith('https://fonts.googleapis.com') or request.request.url.startswith('https://fonts.gstatic.com'):
                request.abort()
            else:
                request.continue_()
        context.route('**/*', route)
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('console', lambda message: errors.append(message.text) if message.type == 'error' and 'ERR_FAILED' not in message.text else None)
        page.on('response', lambda response: bad.append((response.status, response.url)) if response.status >= 400 else None)

        page.goto(base + 'library/' + quote(lesson))
        expect(page).to_have_title(re.compile(r'Unit 08: These / Those'))
        expect(page.locator('.q-item')).to_have_count(20)
        assert page.locator('.q-illustration svg, .overview-scene-card svg').count() >= 10
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')

        data = page.evaluate("Object.fromEntries(Object.entries(questionsData).map(([id,q])=>[id,{...q}]))")
        for qid, question in data.items():
            if question['type'] == 'choice':
                page.locator(f'button[data-qid="{qid}"][data-val="{question["correct"]}"]').click()
            elif question['type'] == 'single-select':
                page.locator(f'#sel-{qid}').select_option(question['correct'])
            else:
                page.locator(f'#sel-{qid}-d').select_option(question['correctPronoun'])
                page.locator(f'#sel-{qid}-n').select_option(question['correctNoun'])
            expect(page.locator(f'#exp-{qid}')).to_have_class(re.compile(r'is-correct'))
        expect(page.locator('#total-score')).to_have_text('20 / 20')
        page.locator('#btn-submit').click()
        expect(page.locator('#btn-submit')).to_be_disabled()
        expect(page.locator('.choice-btn').first).to_be_disabled()
        expect(page.locator('.select-input').first).to_be_disabled()
        page.locator('#btn-reset').click()
        expect(page.locator('#total-score')).to_have_text('0 / 20')
        expect(page.locator('.choice-btn').first).to_be_enabled()
        expect(page.locator('.select-input').first).to_be_enabled()
        page.locator('button[data-qid="a1"][data-val="These"]').click()
        expect(page.locator('#exp-a1')).to_have_class(re.compile(r'is-wrong'))
        expect(page.locator('#exp-a1')).to_contain_text('Those')
        expect(page.locator('#exp-a1')).to_contain_text('Lý do')
        page.locator('#item-a1 button[title*="Those"]').click()
        assert page.evaluate('window.__spoken') == [{'text': 'Those', 'lang': 'en-US', 'rate': 0.9}]
        page.screenshot(path=str(OUT/'unit8-mobile.png'), full_page=True)

        page.goto(base + 'library/catalog-fixture.html')
        page.evaluate("""async data=>{
          const release=await import('./assets/catalog-release.js');
          window.view=await import('./assets/catalog-view.js');
          window.view.setCatalog(release.addReleaseLessons(data).data,2);
          for(const id of ['library','library-hero','library-search'])document.getElementById(id).hidden=false;
          document.getElementById('auth-panel').hidden=true;
        }""", server_catalog)
        tabs = page.locator('#tabs .tab')
        expect(tabs.first).to_have_text('Grade 3')
        expect(tabs.nth(1)).to_have_text('Grade 4')
        folder = page.locator('.grade-section.active .folder')
        expect(folder).to_have_count(1)
        expect(folder.locator('h3')).to_have_text('Bổ trợ ngữ pháp')
        expect(folder.locator('.folder-body')).to_be_hidden()
        folder.locator('.folder-head').click()
        expect(folder.locator('.folder-body')).to_be_visible()
        link = folder.locator(f'a[href="{lesson}"]')
        expect(link).to_have_text('Unit 08 – These / Those')
        for query in ['Grade 3', 'Unit 8', 'These / Those']:
            page.locator('#search').fill(query)
            expect(page.locator(f'.grade-section.active a[href="{lesson}"]')).to_have_count(1)
        page.locator('#search').fill('')
        page.locator('.grade-section.active .folder-head').click()
        with page.expect_navigation(): page.locator(f'a[href="{lesson}"]').click()
        assert urlsplit(page.url).path.endswith('/library/' + lesson)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
        assert not errors and not bad, (errors, bad)
        (OUT/'report.json').write_text(json.dumps({'questions': 20, 'score': '20 / 20', 'catalogSearches': 3, 'errors': errors, 'bad': bad}, ensure_ascii=False, indent=2) + '\n')
        browser.close()
finally:
    server.shutdown()

print('PASS Grade 3 catalog folder/search/link and Unit 08: 20 questions, scoring, explanations, submit/reset, speech and mobile layout')
