"""Real browser and Firebase Auth/Firestore emulators; no production requests."""
import functools, http.server, json, os, secrets, shutil, subprocess, threading, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
assert os.environ.get('FIRESTORE_EMULATOR_HOST') == '127.0.0.1:8080'
assert os.environ.get('FIREBASE_AUTH_EMULATOR_HOST') == '127.0.0.1:9099'
ADMIN = '4Y82k6RBaRUPflZriPsUvQv1qKj2'
password = secrets.token_urlsafe(24)  # Ephemeral test-only password, never printed.

def auth_request(method, data):
    req = urllib.request.Request('http://127.0.0.1:9099/identitytoolkit.googleapis.com/v1/accounts:'+method+'?key=demo-api-key', data=json.dumps(data).encode(), headers={'Content-Type':'application/json','Authorization':'Bearer owner'})
    with urllib.request.urlopen(req) as response: return json.load(response)

users=[]
for uid,label,status in [(ADMIN,'admin',None),('active-teacher','active','active'),('locked-teacher','locked','locked'),('revoked-teacher','revoked','revoked'),('unapproved-teacher','unapproved',None),('disabled-teacher','disabled','active')]:
    email=label+'@example.test'
    result=auth_request('signUp',{'localId':uid,'email':email,'password':password,'returnSecureToken':True})
    assert result['localId']==uid, result
    if label=='disabled': auth_request('update',{'localId':uid,'disableUser':True})
    users.append({'uid':uid,'email':email,'label':label,'status':status})
subprocess.run(['node','tests/seed-emulator.mjs'],cwd=ROOT,input=json.dumps(users),text=True,check=True)

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
    def copyfile(self,source,output):
        try: super().copyfile(source,output)
        except (BrokenPipeError,ConnectionResetError): pass # Browser closes an audio stream on navigation.
server=http.server.ThreadingHTTPServer(('127.0.0.1',8765),functools.partial(QuietHandler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE='http://127.0.0.1:8765/'
config=f'export const firebaseConfig = {{projectId:"demo-ht-english-library"}}; export const ADMIN_UID="{ADMIN}"; export const useEmulators=true;'
baseline=json.loads((ROOT/'catalog/baseline.json').read_text())['commit']
original_html=subprocess.check_output(['git','show',baseline+':index.html'],cwd=ROOT,text=True)
blocked=[]

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'),args=['--no-sandbox'])
    def new_page():
        context=browser.new_context()
        def route(request):
            if request.request.url.endswith('/baseline-index.html'):
                request.fulfill(status=200,content_type='text/html',body=original_html)
            elif request.request.url.endswith('/assets/firebase-config.js'):
                request.fulfill(status=200,content_type='text/javascript',body=config)
            elif request.request.url.startswith(('http://127.0.0.1:','http://localhost:')):
                request.continue_()
            else:
                blocked.append(request.request.url); request.abort()
        context.route('**/*',route)
        page=context.new_page(); page.set_default_timeout(15000)
        return context,page
    def login(page,email,secret=password,path='index.html'):
        page.goto(BASE+path)
        page.locator('#email').fill(email); page.locator('#password').fill(secret); page.locator('#login-submit').click()
    count=0
    context,page=new_page(); page.goto(BASE)
    expect(page.locator('#login-form')).to_be_visible(); expect(page.locator('#library')).to_be_hidden()
    assert page.locator('a.lesson').count()==0
    for width in [360,375,390,430]:
        page.set_viewport_size({'width':width,'height':850})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),('login overflow',width)
    count+=1; print('PASS anonymous catalog hidden',flush=True); context.close()

    context,page=new_page(); login(page,'active@example.test','wrong-password')
    expect(page.locator('#auth-message')).to_contain_text('Email hoặc mật khẩu không đúng')
    expect(page.locator('#library')).to_be_hidden()
    count+=1; print('PASS wrong-password login rejected',flush=True); context.close()

    for label,text in [('unapproved','chưa được cấp quyền'),('locked','đang bị khóa'),('revoked','đã bị thu hồi'),('disabled','đã bị vô hiệu hóa')]:
        context,page=new_page(); login(page,label+'@example.test')
        expect(page.locator('#auth-message')).to_contain_text(text)
        expect(page.locator('#library')).to_be_hidden(); assert page.locator('a.lesson').count()==0
        count+=1; print('PASS '+label+' account denied',flush=True); context.close()

    teacher_context,teacher=new_page(); login(teacher,'active@example.test')
    expect(teacher.locator('#library')).to_be_visible()
    expect(teacher.locator('#stats')).to_have_text('201 bài học')
    data=json.loads((ROOT/'catalog/library-catalog.json').read_text())['data']
    baseline_context,baseline_page=new_page(); baseline_page.goto(BASE+'baseline-index.html')
    for grade in data:
        teacher.get_by_role('button',name=grade['grade'],exact=True).click()
        baseline_page.get_by_role('button',name=grade['grade'],exact=True).click()
        expected=baseline_page.locator('a.lesson').evaluate_all('(els)=>els.map(e=>e.getAttribute("href"))')
        actual=teacher.locator('a.lesson').evaluate_all('(els)=>els.map(e=>e.getAttribute("href"))')
        assert actual==expected,(grade['grade'],'catalog order')
    baseline_context.close()
    count+=1; print('PASS active teacher sees exactly 201 links in original order',flush=True)
    restricted_context,restricted=new_page(); login(restricted,'active@example.test',path='admin.html')
    expect(restricted.locator('#auth-message')).to_contain_text('Chỉ tài khoản Admin')
    expect(restricted.locator('#admin-panel')).to_be_hidden()
    count+=1; print('PASS teacher denied admin UI',flush=True); restricted_context.close()

    admin_context,admin=new_page(); login(admin,'admin@example.test',path='admin.html')
    expect(admin.locator('#admin-panel')).to_be_visible()
    for width in [360,375,390,430]:
        admin.set_viewport_size({'width':width,'height':850})
        assert admin.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),('admin overflow',width)
    admin.set_viewport_size({'width':960,'height':800})
    admin.locator('#teacher-uid').fill('unapproved-teacher'); admin.locator('#teacher-email').fill('unapproved@example.test'); admin.locator('#teacher-name').fill('New Teacher'); admin.locator('#grant-access').click()
    expect(admin.locator('#admin-message')).to_contain_text('Đã cấp quyền')
    row=admin.locator('.member').filter(has_text='UID: active-teacher')
    admin.on('dialog',lambda dialog:dialog.accept())
    row.get_by_role('button',name='Khóa',exact=True).click()
    expect(teacher.locator('#library')).to_be_hidden(); expect(teacher.locator('#auth-message')).to_contain_text('đang bị khóa')
    row.get_by_role('button',name='Mở khóa / cấp lại',exact=True).click()
    expect(teacher.locator('#library')).to_be_visible()
    row.get_by_role('button',name='Thu hồi',exact=True).click()
    expect(teacher.locator('#library')).to_be_hidden(); expect(teacher.locator('#auth-message')).to_contain_text('đã bị thu hồi')
    count+=1; print('PASS admin grant, lock, unlock, revoke; open teacher session updates immediately',flush=True)

    payload=json.loads((ROOT/'catalog/library-catalog.json').read_text())
    altered=json.loads(json.dumps(payload)); altered['data'][0]['units'][0]['lessons'].reverse()
    admin.locator('#catalog-file').set_input_files({'name':'altered.json','mimeType':'application/json','buffer':json.dumps(altered).encode()})
    expect(admin.locator('#catalog-preview')).to_contain_text('không khớp bản gốc')
    expect(admin.locator('#import-catalog')).to_be_disabled()
    admin.locator('#catalog-file').set_input_files(str(ROOT/'catalog/library-catalog.json'))
    expect(admin.locator('#catalog-preview')).to_contain_text('Chưa ghi dữ liệu')
    expect(admin.locator('#import-catalog')).to_be_enabled()
    admin.locator('#import-catalog').click()
    expect(admin.locator('#admin-message')).to_contain_text('Đã nhập và đọc lại xác minh đủ 201')
    count+=1; print('PASS importer rejects changed order; imports and reads back exact catalog in emulator',flush=True)
    admin.locator('#catalog-file').set_input_files(str(ROOT/'catalog/library-catalog.json'))
    expect(admin.locator('#catalog-preview')).to_contain_text('Chưa ghi dữ liệu')
    before=admin.evaluate("""async()=>{const {db}=await import('./assets/firebase-client.js');const {doc,setDoc,serverTimestamp,getDocFromServer}=await import('./assets/firebase-sdk.js');const ref=doc(db,'libraryCatalog','current');await setDoc(ref,{updatedAt:serverTimestamp()},{merge:true});return (await getDocFromServer(ref)).data().updatedAt.toMillis()}""")
    admin.locator('#import-catalog').click()
    expect(admin.locator('#admin-message')).to_contain_text('Danh mục đã thay đổi')
    after=admin.evaluate("""async()=>{const {db}=await import('./assets/firebase-client.js');const {doc,getDocFromServer}=await import('./assets/firebase-sdk.js');return (await getDocFromServer(doc(db,'libraryCatalog','current'))).data().updatedAt.toMillis()}""")
    assert before==after
    count+=1; print('PASS stale catalog import rejected without overwriting newer changes',flush=True)
    admin.locator('#logout').click(); expect(admin.locator('#admin-panel')).to_be_hidden()
    count+=1; print('PASS logout clears admin data',flush=True)

    context,exercise=new_page()
    url='grade-7/De_thi_GHK_1/1_THCS_Truc_Thai/1%20THCS%20Truc%20Thai.html'
    assert exercise.goto(BASE+url).status==200
    assert exercise.locator('.question-card').count()>0
    exercise.locator('#submitBtn').click(); exercise.locator('#confirmSubmit').click()
    expect(exercise.locator('#submissionBanner')).to_be_visible()
    expect(exercise.locator('#submitBtn')).to_be_disabled()
    audio=exercise.request.get(BASE+'grade-7/De_thi_GHK_1/1_THCS_Truc_Thai/Task%201.mp3')
    assert audio.status==200 and len(audio.body())>1000
    count+=1; print('PASS anonymous direct exercise, scoring submission and audio request',flush=True)
    teacher_context.close(); admin_context.close(); context.close(); browser.close()
    assert not blocked, 'Unexpected external network requests: '+str(blocked)
    print(f'PASS {count} browser scenarios; production network never contacted.')
server.shutdown(); server.server_close()
