"""Catalog rendering fixture; no Firebase auth claims, account or production writes."""
from pathlib import Path
from urllib.parse import quote,urlsplit
import functools,http.server,json,re,subprocess,threading
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];OUT=Path('/tmp/ht-grade7-catalog');OUT.mkdir(exist_ok=True)
rows=json.loads((ROOT/'docs/grade7-dual-mode/inventory.json').read_text())['games']
before=json.loads(subprocess.check_output(['git','show','d1f7ebf:catalog/current-library-catalog.json'],cwd=ROOT))['data']
fixture=re.sub(r'<script type="module"[^>]*></script>','',(ROOT/'index.html').read_text())
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def translate_path(self,path):return super().translate_path(path[len('/library'):] if path.startswith('/library/') else path)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}/'
checks=[];errors=[];bad=[];external=[]
def passed(s):checks.append(s);print('PASS '+s,flush=True)
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);c=b.new_context(viewport={'width':1280,'height':900})
  def route(r):
   if not r.request.url.startswith(BASE):external.append(r.request.url);r.abort()
   elif urlsplit(r.request.url).path.endswith('/catalog-fixture.html'):r.fulfill(content_type='text/html',body=fixture)
   else:r.continue_()
  c.route('**/*',route);page=c.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);page.on('response',lambda r:bad.append((r.status,r.url)) if r.status>=400 else None)
  page.goto(BASE+'library/catalog-fixture.html');expect(page.locator('#library')).to_be_hidden();expect(page.locator('#content')).to_be_empty();expect(page.locator('a[href^="grade-"]')).to_have_count(0)
  passed('initial index fixture keeps all material hidden and empty before catalog access')
  page.evaluate('''async d=>{window.view=await import('./assets/catalog-view.js');const release=await import('./assets/catalog-release.js');window.upgraded=release.addReleaseLessons(d).data;window.before=d;window.view.setCatalog(upgraded,2);for(const id of ['library','library-hero','library-search'])document.getElementById(id).hidden=false;document.getElementById('auth-panel').hidden=true;}''',before)
  for grade in ['Grade 4','Grade 5','Grade 6','Grade 8']:
   page.get_by_role('button',name=grade,exact=True).click();now=page.locator('#content').inner_html();page.evaluate('view.setCatalog(before,2)');page.get_by_role('button',name=grade,exact=True).click();assert page.locator('#content').inner_html()==now,grade;page.evaluate('view.setCatalog(upgraded,2)')
  passed('Grade 4/5/6/8 rendering unchanged by the Grade 7 release')
  page.get_by_role('button',name='Grade 7',exact=True).click();folder=page.locator('.grade-section.active .exam-school-folder');folder.locator('.folder-head').click();expect(folder.locator('.school-folder')).to_have_count(14);expect(folder.locator('a.exam-resource')).to_have_count(14);expect(folder.locator('a.game-resource')).to_have_count(14)
  for row in rows:
   school=folder.locator('.school-folder').filter(has=page.locator('.school-name',has_text=re.compile('^'+re.escape(row['school'])+'$')));pair=school.locator(f'.exam-pair[data-exam-number="{row["number"]}"]');expect(pair.locator('a')).to_have_count(2);assert pair.locator('a').evaluate_all('(els)=>els.map(a=>a.getAttribute("href"))')==[row['source'],row['game']]
   expect(pair.locator('a.game-resource strong')).to_have_text(f'Game đề số {row["number"]} – {row["school"]}');assert page.request.get(BASE+'library/'+quote(row['game'])).status==200
  passed('14 source/game pairs across 14 schools; all schools preserve exam 1 and exact launch paths')
  for width in [360,390,768,1280]:
   page.set_viewport_size({'width':width,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(OUT/f'grade7-{width}.png'),full_page=True)
  page.locator('#search').fill('Game đề số');expect(page.locator('.grade-section.active a.game-resource')).to_have_count(14);expect(page.locator('.grade-section.active a.exam-resource')).to_have_count(0)
  page.locator('#search').fill('Liêm Hải');expect(page.locator('.grade-section.active a.lesson')).to_have_count(2)
  changed=page.evaluate('structuredClone(upgraded)');g=next(g for g in changed if g['grade']=='Grade 7');u=next(u for u in g['units'] if u['name']=='Đề thi GHK1');u['lessons'][1]['hidden']=True;u['lessons'][1]['title']='Tên game Admin đổi';page.evaluate('d=>view.setCatalog(d,2)',changed);page.locator('#search').fill('Trực Thái');expect(page.locator('.grade-section.active a.game-resource')).to_have_count(0)
  u['hidden']=True;page.evaluate('d=>view.setCatalog(d,2)',changed);expect(page.locator('.grade-section.active a[href^="grade-7/De_thi_GHK_1/"]')).to_have_count(0)
  page.evaluate('view.clearCatalog()');expect(page.locator('#content')).to_be_empty();expect(page.locator('#tabs')).to_be_empty();assert not errors and not bad and not external,(errors,bad,external)
  passed('mobile widths, search, Admin hide/title metadata, hidden folders and catalog clearing; no Console/HTTP/external errors')
  (OUT/'report.json').write_text(json.dumps(dict(checks=checks,errors=errors,bad=bad),ensure_ascii=False,indent=2)+'\n');b.close()
finally:server.shutdown()
