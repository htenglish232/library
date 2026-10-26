"""Inventory real dual launchers; optional read-only GitHub Pages comparisons.

Connection/proxy failures are not interpreted as an origin HTTP response or as
proof that Pages is stale. Never changes Firebase, GitHub or the website.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote,quote,urljoin
from urllib.request import urlopen,Request
from urllib.error import HTTPError,URLError
from concurrent.futures import ThreadPoolExecutor
import argparse,datetime,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1];BASE='https://htenglish232.github.io/library/'
SHARED=ROOT/'grade-8/De_thi_GHK1/shared-practice'
class Page(HTMLParser):
 def __init__(self):super().__init__();self.scripts=[];self.styles=[];self.soundButtons=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='script' and 'src' in a:self.scripts.append(a)
  if tag=='link' and a.get('rel')=='stylesheet':self.styles.append(a)
  if tag=='button' and a.get('id')=='sound-toggle':self.soundButtons.append(a)
def inventory():
 games=[]
 for html in sorted((ROOT/'grade-8/De_thi_GHK1').rglob('*.html')):
  page=Page();page.feed(html.read_text())
  engines=[s for s in page.scripts if Path(unquote(urlsplit(s['src']).path)).name=='dual-mode-engine.js']
  is_dual='data-practice="dual-mode"' in html.read_text() or bool(engines)
  if not is_dual:continue
  assert len(engines)==1,('Missing/duplicate shared engine',html)
  engine=(html.parent/unquote(urlsplit(engines[0]['src']).path)).resolve();assert engine==SHARED/'dual-mode-engine.js'
  dataScript=next(s['src'] for s in page.scripts if unquote(urlsplit(s['src']).path).endswith('-data.js'))
  data=json.loads((html.parent/unquote(urlsplit(dataScript).path)).read_text().split('window.HT_PRACTICE_DATA = ',1)[1].strip()[:-1])
  resources=[]
  for entry,key in [(s,'src') for s in page.scripts]+[(s,'href') for s in page.styles]:
   target=(html.parent/unquote(urlsplit(entry[key]).path)).resolve();assert target.is_file(),target
   resources.append({'url':entry[key],'path':target.relative_to(ROOT).as_posix()})
  games.append({'school':data['exam']['school'],'examNumber':data['exam'].get('number',1),'questions':len(data['questions']),'html':html.relative_to(ROOT).as_posix(),'engine':engines[0],'staticSoundButtons':len(page.soundButtons),'resources':resources})
 assert games,'No existing dual-mode launchers detected'
 return games

def probe(item):
 relative=item['path'];url=BASE+quote(relative);checkout=(ROOT/relative).read_bytes();main=subprocess.check_output(['git','show','origin/main:'+relative],cwd=ROOT);result={'path':relative,'url':url,'checkoutSha256':hashlib.sha256(checkout).hexdigest(),'mainSha256':hashlib.sha256(main).hexdigest()}
 try:
  with urlopen(Request(url,headers={'User-Agent':'HT-English-read-only-release-audit/1.0'}),timeout=20) as response:
   body=response.read();result.update(status=response.status,state='fetched',sha256=hashlib.sha256(body).hexdigest(),matchesCheckout=body==checkout,matchesMain=body==main,headers={k:response.headers.get(k) for k in ['Cache-Control','Age','ETag','Last-Modified','Content-Type']})
 except HTTPError as error:result.update(status=error.code,state='http-error',error=str(error))
 except (URLError,OSError) as error:result.update(status=None,state='unreachable-from-environment',error=str(error))
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--public',action='store_true');p.add_argument('--output',default='/tmp/grade8-sound-inventory.json');a=p.parse_args()
 games=inventory();report={'checkedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'count':len(games),'games':games}
 if a.public:
  # Trực Tuấn is the first public test case, then all other real launchers.
  ordered=sorted(games,key=lambda r:'truc-tuan' not in r['html'])
  targets=[{'path':r['html']} for r in ordered]+[{'path':f'grade-8/De_thi_GHK1/shared-practice/{name}'} for name in ['dual-mode-engine.js','dual-sound.js','dual-mode.css']]
  results=[probe(targets[0])]
  with ThreadPoolExecutor(max_workers=4) as pool:results+=list(pool.map(probe,targets[1:]))
  report['public']=results
  report['publicVerified']=all(r['state']=='fetched' for r in results)
  report['publicConclusion']='Fetched resources can be compared by SHA256; this does not replace public browser interaction tests.' if report['publicVerified'] else 'Cannot verify the live release from this environment. Connection errors do not prove that Pages returned 403/404 or that deployment is stale.'
 Path(a.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('PASS disk inventory:',len(games),'real dual-mode launchers; all share one engine and local resources exist.')
 if a.public:print('PUBLIC:',sum(r['state']=='fetched' for r in report['public']),'/',len(report['public']),'resources fetched; see',a.output)
if __name__=='__main__':main()
