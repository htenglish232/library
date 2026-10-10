"""Independent Auth Emulator checks when Firestore download is unavailable."""
import functools, http.server, json, os, secrets, shutil, threading, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
assert os.environ.get('FIREBASE_AUTH_EMULATOR_HOST')=='127.0.0.1:9099'
password=secrets.token_urlsafe(24)
def auth_request(method,data):
    request=urllib.request.Request('http://127.0.0.1:9099/identitytoolkit.googleapis.com/v1/accounts:'+method+'?key=demo-api-key',data=json.dumps(data).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer owner'})
    with urllib.request.urlopen(request) as response:return json.load(response)
auth_request('signUp',{'localId':'auth-check-active','email':'auth-check-active@example.test','password':password})
auth_request('signUp',{'localId':'auth-check-disabled','email':'auth-check-disabled@example.test','password':password})
auth_request('update',{'localId':'auth-check-disabled','disableUser':True})
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
    def copyfile(self,source,output):
        try:super().copyfile(source,output)
        except (BrokenPipeError,ConnectionResetError):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',8765),functools.partial(QuietHandler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:8765/'
config='export const firebaseConfig={projectId:"demo-ht-english-library"};export const ADMIN_UID="4Y82k6RBaRUPflZriPsUvQv1qKj2";export const useEmulators=true;'
external=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'),args=['--no-sandbox'])
    for label in ['anonymous','wrong-password','disabled','direct-exercise']:
        context=browser.new_context();page=context.new_page();page.set_default_timeout(15000);errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        def route(request):
            if request.request.url.endswith('/assets/firebase-config.js'):request.fulfill(content_type='text/javascript',body=config)
            elif request.request.url.startswith('http://127.0.0.1:'):request.continue_()
            else:external.append(request.request.url);request.abort()
        context.route('**/*',route)
        if label=='direct-exercise':
            assert page.goto(base+'grade-7/De_thi_GHK_1/1_THCS_Truc_Thai/1%20THCS%20Truc%20Thai.html').status==200
            assert page.locator('.question-card').count()==42
            page.locator('#submitBtn').click();page.locator('#confirmSubmit').click()
            expect(page.locator('#submissionBanner')).to_be_visible();expect(page.locator('#submitBtn')).to_be_disabled()
            audio=page.request.get(base+'grade-7/De_thi_GHK_1/1_THCS_Truc_Thai/Task%201.mp3')
            assert audio.status==200 and len(audio.body())>1000
        else:
            page.goto(base)
            expect(page.locator('#auth-message')).to_contain_text('Đăng nhập bằng tài khoản')
            if label!='anonymous':
                page.locator('#email').fill('auth-check-'+('disabled' if label=='disabled' else 'active')+'@example.test')
                page.locator('#password').fill(password if label=='disabled' else 'wrong-password')
                page.locator('#login-submit').click()
                expect(page.locator('#auth-message')).to_contain_text('đã bị vô hiệu hóa' if label=='disabled' else 'Email hoặc mật khẩu không đúng')
                expect(page.locator('#password')).to_have_value('')
            expect(page.locator('#library')).to_be_hidden();assert page.locator('a.lesson').count()==0
        assert not errors,errors
        print('PASS '+label,flush=True);context.close()
    assert not external,external
    browser.close()
server.shutdown();server.server_close()
print('PASS 4 Auth/anonymous browser checks; Firestore permissions not tested by this suite; no production requests.')
