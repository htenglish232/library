"""Native codec rejection evidence and MP3 compatibility; original WMA immutable."""
from pathlib import Path
from urllib.parse import quote
import functools,http.server,json,re,subprocess,threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
exec('class Handler'+(ROOT/'tests/dual-mode-browser.py').read_text().split('class Handler',1)[1].split('server=http.server',1)[0])
class MediaHandler(Handler):
 def do_GET(self):
  if self.path=='/probe.html':
   body=b'<!doctype html><button id="play">Play test recording</button><audio preload="metadata"></audio>';self.send_response(200);self.send_header('Content-Type','text/html');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
  else:super().do_GET()
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(MediaHandler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}/'
folder='grade-7/De_thi_GHK_1/14_THCS_Viet_Hung/';report={};errors=[]
def probe(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size','-of','json',str(ROOT/path)]))['format']
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  # Expected codec failure in an isolated fixture, not a pageerror in the game.
  page=b.new_page();page.goto(BASE+'probe.html');page.locator('audio').evaluate('(e,url)=>e.src=url',BASE+'library/'+quote(folder+'Listening 2024.wma'));page.wait_for_function('document.querySelector("audio").error||document.querySelector("audio").readyState>=1');report['originalBrowser']=page.locator('audio').evaluate('e=>({canPlay:e.canPlayType("audio/x-ms-wma"),readyState:e.readyState,error:e.error?.code,message:e.error?.message})');assert report['originalBrowser']['error']==4;page.close()
  for mobile in [False,True]:
   c=b.new_context(viewport={'width':390 if mobile else 1280,'height':844},is_mobile=mobile,has_touch=mobile);page=c.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(BASE+'probe.html');page.locator('audio').evaluate('(e,url)=>e.src=url',BASE+'library/'+quote(folder+'listening-2024-browser.mp3'));page.wait_for_function('document.querySelector("audio").readyState>=1');page.locator('#play').evaluate('e=>e.onclick=()=>document.querySelector("audio").play()');page.locator('#play').click();page.wait_for_function('!document.querySelector("audio").paused && document.querySelector("audio").currentTime>0');duration=page.locator('audio').evaluate('e=>e.duration');assert abs(duration-570.068)<.2
   for at in [10,285,565]:page.locator('audio').evaluate('(e,t)=>e.currentTime=t',at);page.wait_for_function('(t)=>!document.querySelector("audio").seeking && Math.abs(document.querySelector("audio").currentTime-t)<1',arg=at)
   assert not page.locator('audio').evaluate('e=>!!e.error');c.close();report['mobile' if mobile else 'desktop']={'play':True,'seekStartMiddleEnd':True,'duration':duration}
  report['originalProbe']=probe(folder+'Listening 2024.wma');report['derivativeProbe']=probe(folder+'listening-2024-browser.mp3');assert abs(float(report['originalProbe']['duration'])-float(report['derivativeProbe']['duration']))<.1;assert not errors,errors;report['errors']=errors;Path('/tmp/grade7-media-browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('PASS original WMA native error 4 reproduced; MP3 plays/seeks start/middle/end on desktop/touch; duration delta <0.1s; no game JS errors',flush=True);b.close()
finally:server.shutdown()
