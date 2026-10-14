"""Serve the reviewed Admin package locally; no Firebase operation is performed here."""
import argparse, functools, http.server, pathlib, webbrowser
parser=argparse.ArgumentParser()
parser.add_argument('--no-browser',action='store_true')
parser.add_argument('--port',type=int,default=8123)
args=parser.parse_args()
root=pathlib.Path(__file__).resolve().parent
if not (root/'admin.html').is_file() or not (root/'assets/firebase-sdk.js').is_file():
    raise SystemExit('Please extract the complete ZIP before starting.')
class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
    def copyfile(self,source,output):
        try:super().copyfile(source,output)
        except (BrokenPipeError,ConnectionResetError):pass
try:
    server=http.server.ThreadingHTTPServer(('127.0.0.1',args.port),functools.partial(Handler,directory=str(root)))
except OSError:
    raise SystemExit('Cannot start: port is already in use. Close the previous Admin launcher, then try again.')
url=f'http://localhost:{args.port}/admin.html'
print('HT English Library: local Admin connected to Firebase ht-english-library.',flush=True)
print(url,flush=True)
print('Keep this window open. Ctrl+C stops only this local server.',flush=True)
if not args.no_browser:webbrowser.open(url)
try:server.serve_forever()
except KeyboardInterrupt:pass
finally:server.server_close()
