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
    def translate_path(self,path):
        # Model GitHub project Pages under /library/, without changing source links.
        if path.startswith('/library/'): path=path[len('/library'):]
        return super().translate_path(path)
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
    expect(admin.locator('#catalog-preview')).to_contain_text('đã tồn tại')
    expect(admin.locator('#import-catalog')).to_be_disabled()
    count+=1; print('PASS importer rejects changed order and refuses an already-existing catalog',flush=True)
    subprocess.run(['node','tests/reset-emulator-catalog.mjs'],cwd=ROOT,check=True)
    admin.locator('#catalog-file').set_input_files([])
    admin.locator('#catalog-file').set_input_files(str(ROOT/'catalog/library-catalog.json'))
    expect(admin.locator('#catalog-preview')).to_contain_text('Chưa ghi dữ liệu')
    before=admin.evaluate("""async(payload)=>{const {db}=await import('./assets/firebase-client.js');const {doc,setDoc,serverTimestamp,getDocFromServer}=await import('./assets/firebase-sdk.js');const ref=doc(db,'libraryCatalog','current');await setDoc(ref,{schemaVersion:1,count:201,sha256:payload.sha256,dataJson:JSON.stringify(payload.data),updatedAt:serverTimestamp()});return (await getDocFromServer(ref)).data().updatedAt.toMillis()}""",payload)
    admin.locator('#import-catalog').click()
    expect(admin.locator('#admin-message')).to_contain_text('đã tồn tại')
    after=admin.evaluate("""async()=>{const {db}=await import('./assets/firebase-client.js');const {doc,getDocFromServer}=await import('./assets/firebase-sdk.js');return (await getDocFromServer(doc(db,'libraryCatalog','current'))).data().updatedAt.toMillis()}""")
    assert before==after
    count+=1; print('PASS concurrent catalog creation causes import to stop without overwriting',flush=True)
    subprocess.run(['node','tests/reset-emulator-catalog.mjs'],cwd=ROOT,check=True)
    admin.locator('#catalog-file').set_input_files([])
    admin.locator('#catalog-file').set_input_files(str(ROOT/'catalog/library-catalog.json'))
    expect(admin.locator('#catalog-preview')).to_contain_text('Chưa ghi dữ liệu')
    expect(admin.locator('#import-catalog')).to_be_enabled()
    admin.locator('#import-catalog').click()
    expect(admin.locator('#admin-message')).to_contain_text('Đã nhập và đọc lại xác minh đủ 201')
    expect(admin.locator('#import-catalog')).to_be_disabled()
    count+=1; print('PASS first catalog created and read-back verified exactly; repeat import disabled',flush=True)

    row.get_by_role('button',name='Mở khóa / cấp lại',exact=True).click()
    expect(teacher.locator('#library')).to_be_visible()
    admin.locator('#reload-catalog').click()
    expect(admin.locator('#editor-summary')).to_contain_text('201 bài tập tổng cộng')
    original_fields=admin.evaluate("""async()=>{const {db}=await import('./assets/firebase-client.js');const {doc,getDocFromServer}=await import('./assets/firebase-sdk.js');return (await getDocFromServer(doc(db,'libraryCatalog','current'))).data()}""")
    admin.locator('#grade-name').fill('Grade 9'); admin.locator('#add-grade').click()
    admin.locator('#unit-name').fill('Thư mục mới'); admin.locator('#add-unit').click()
    malicious='<img src=x onerror="window.catalogInjected=true">'
    admin.locator('#lesson-title').fill(malicious); admin.locator('#lesson-href').fill('grade-9/new.html'); admin.locator('#lesson-submit').click()
    expect(admin.locator('#editor-summary')).to_contain_text('202 bài tập tổng cộng')
    expect(admin.locator('#editor-summary')).to_contain_text('bản nháp chưa lưu')
    expect(teacher.locator('#stats')).to_have_text('201 bài học')
    admin.locator('#save-catalog').click()
    expect(admin.locator('#editor-message')).to_contain_text('phiên bản 1')
    expect(teacher.locator('#stats')).to_have_text('202 bài học')
    teacher.get_by_role('button',name='Grade 9',exact=True).click()
    expect(teacher.locator('a.lesson')).to_have_count(1)
    assert teacher.locator('a.lesson strong').inner_text()==malicious
    assert teacher.locator('a.lesson img').count()==0
    assert not teacher.evaluate('!!window.catalogInjected')
    archive=admin.evaluate("""async()=>{const {db}=await import('./assets/firebase-client.js');const {doc,getDocFromServer}=await import('./assets/firebase-sdk.js');return (await getDocFromServer(doc(db,'libraryCatalogHistory','0'))).data()}""")
    assert archive['snapshot']==original_fields
    count+=1; print('PASS dynamic 202-item catalog, migration preserves exact original snapshot, teacher live update and safe title rendering',flush=True)

    admin.locator('#lesson-title').fill('Không hợp lệ'); admin.locator('#lesson-href').fill('javascript:alert(1)'); admin.locator('#lesson-submit').click()
    expect(admin.locator('#editor-message')).to_contain_text('đường dẫn')
    expect(admin.locator('#editor-summary')).to_contain_text('202 bài tập tổng cộng')
    admin.locator('#cancel-lesson-edit').click()
    admin.locator('#toggle-unit').click(); admin.locator('#save-catalog').click()
    expect(admin.locator('#editor-message')).to_contain_text('phiên bản 2')
    expect(teacher.locator('#stats')).to_have_text('201 bài học')
    assert teacher.locator('a.lesson').count()==0
    admin.locator('#toggle-unit').click()
    admin.locator('.catalog-item').get_by_role('button',name='Ẩn bài',exact=True).click()
    admin.locator('#save-catalog').click(); expect(admin.locator('#editor-message')).to_contain_text('phiên bản 3')
    expect(teacher.locator('#stats')).to_have_text('201 bài học')
    admin.locator('.catalog-item').get_by_role('button',name='Hiện bài',exact=True).click()
    admin.locator('.catalog-item').get_by_role('button',name='Sửa',exact=True).click()
    admin.locator('#lesson-title').fill('Bài mới đã sửa'); admin.locator('#lesson-submit').click()
    admin.locator('#save-catalog').click(); expect(admin.locator('#editor-message')).to_contain_text('phiên bản 4')
    expect(teacher.locator('#stats')).to_have_text('202 bài học')
    expect(teacher.locator('a.lesson strong')).to_have_text('Bài mới đã sửa')
    count+=1; print('PASS invalid links rejected; folder and lesson hide/show and lesson editing; count updates without deleting files',flush=True)

    admin.locator('#lesson-title').fill('Bài thứ hai'); admin.locator('#lesson-href').fill('https://example.test/lesson.html'); admin.locator('#lesson-submit').click()
    admin.locator('.catalog-item').filter(has_text='Bài thứ hai').get_by_role('button',name='Lên',exact=True).click()
    admin.locator('#grade-name').fill('Grade 10'); admin.locator('#rename-grade').click()
    admin.locator('#grade-up').click(); admin.locator('#grade-down').click(); admin.locator('#sort-grades').click()
    admin.locator('#grade-select').select_option(label='Grade 10')
    admin.locator('#unit-name').fill('Thư mục phụ'); admin.locator('#add-unit').click()
    admin.locator('#unit-up').click(); admin.locator('#unit-down').click()
    admin.locator('#unit-name').fill('Thư mục phụ đổi tên'); admin.locator('#rename-unit').click()
    admin.locator('#unit-select').select_option('0')
    admin.locator('.catalog-item').filter(has_text='Bài thứ hai').get_by_role('button',name='Sửa',exact=True).click()
    admin.locator('#lesson-target-unit').select_option('1'); admin.locator('#lesson-submit').click()
    expect(admin.locator('.catalog-item')).to_have_count(1)
    admin.locator('#unit-select').select_option('1')
    admin.locator('.catalog-item').get_by_role('button',name='Sửa',exact=True).click()
    admin.locator('#lesson-target-unit').select_option('0'); admin.locator('#lesson-submit').click()
    expect(admin.locator('.catalog-item')).to_have_count(0)
    admin.locator('#delete-unit').click()
    admin.locator('.catalog-item').filter(has_text='Bài thứ hai').get_by_role('button',name='Lên',exact=True).click()
    admin.locator('#save-catalog').click(); expect(admin.locator('#editor-message')).to_contain_text('phiên bản 5')
    expect(teacher.locator('#stats')).to_have_text('203 bài học')
    teacher.get_by_role('button',name='Grade 10',exact=True).click()
    assert teacher.locator('a.lesson strong').all_text_contents()==['Bài thứ hai','Bài mới đã sửa']
    count+=1; print('PASS lesson and folder add/delete/reorder, grade rename/reorder/sort and dynamic count above 201',flush=True)

    admin.locator('#toggle-grade').click(); admin.locator('#save-catalog').click()
    expect(admin.locator('#editor-message')).to_contain_text('phiên bản 6')
    expect(teacher.locator('#stats')).to_have_text('201 bài học')
    expect(teacher.get_by_role('button',name='Grade 10',exact=True)).to_have_count(0)
    admin.locator('#toggle-grade').click(); admin.locator('#save-catalog').click()
    expect(admin.locator('#editor-message')).to_contain_text('phiên bản 7')
    expect(teacher.locator('#stats')).to_have_text('203 bài học')
    with admin.expect_download() as download_info: admin.locator('#backup-catalog').click()
    backup=json.loads(Path(download_info.value.path()).read_text())
    assert backup['count']==203 and backup['schemaVersion']==2 and not backup['includesUnsavedDraft']
    admin.locator('.catalog-item').filter(has_text='Bài thứ hai').get_by_role('button',name='Xóa bài',exact=True).click()
    admin.locator('#save-catalog').click(); expect(admin.locator('#editor-message')).to_contain_text('phiên bản 8')
    expect(teacher.locator('#stats')).to_have_text('202 bài học')
    bad_backup=json.loads(json.dumps(backup)); bad_backup['data'][0]['grade']='Changed without checksum'
    admin.locator('#restore-file').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':json.dumps(bad_backup).encode()})
    expect(admin.locator('#editor-message')).to_contain_text('SHA-256 không khớp')
    expect(admin.locator('#save-catalog')).to_be_disabled()
    admin.locator('#restore-file').set_input_files({'name':'good.json','mimeType':'application/json','buffer':json.dumps(backup).encode()})
    expect(admin.locator('#editor-message')).to_contain_text('khôi phục vào bản nháp')
    expect(teacher.locator('#stats')).to_have_text('202 bài học')
    admin.locator('#save-catalog').click(); expect(admin.locator('#editor-message')).to_contain_text('phiên bản 9')
    expect(teacher.locator('#stats')).to_have_text('203 bài học')
    count+=1; print('PASS grade hide/show, local JSON backup, corrupt restore rejected and verified restore creates new version',flush=True)

    second_context,second=new_page(); login(second,'admin@example.test',path='admin.html')
    expect(second.locator('#editor-summary')).to_contain_text('Phiên bản 9')
    second.on('dialog',lambda dialog:dialog.accept())
    second.locator('#grade-name').fill('Grade 11'); second.locator('#add-grade').click()
    admin.locator('#grade-name').fill('Grade 12'); admin.locator('#add-grade').click()
    admin.locator('#save-catalog').click(); expect(admin.locator('#editor-message')).to_contain_text('phiên bản 10')
    second.locator('#save-catalog').click()
    expect(second.locator('#editor-message')).to_contain_text('đã được thay đổi ở cửa sổ khác')
    expect(second.locator('#editor-summary')).to_contain_text('bản nháp chưa lưu')
    assert 'Grade 11' in second.locator('#grade-select option').all_text_contents()
    server_grades=admin.evaluate("""async()=>{const {loadCatalog}=await import('./assets/catalog-store.js');return (await loadCatalog()).data.map(g=>g.grade)}""")
    assert 'Grade 12' in server_grades and 'Grade 11' not in server_grades
    second_context.close()
    count+=1; print('PASS two Admin windows: stale draft save blocked, draft kept and newer server data preserved',flush=True)

    admin.locator('#refresh-history').click()
    expect(admin.locator('#history-version option')).to_have_count(10)
    admin.locator('#history-version').select_option('0'); admin.locator('#restore-history').click()
    expect(admin.locator('#editor-summary')).to_contain_text('201 bài tập tổng cộng')
    expect(teacher.locator('#stats')).to_have_text('203 bài học')
    admin.locator('#save-catalog').click(); expect(admin.locator('#editor-message')).to_contain_text('phiên bản 11')
    expect(teacher.locator('#stats')).to_have_text('201 bài học')
    restored=admin.evaluate("""async()=>{const {loadCatalog}=await import('./assets/catalog-store.js');return (await loadCatalog()).fields.dataJson}""")
    assert restored==original_fields['dataJson']
    for width in [360,375,390,430]:
        admin.set_viewport_size({'width':width,'height':850})
        assert admin.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),('editor overflow',width)
    count+=1; print('PASS history restore preserves original 201 links exactly, keeps all newer versions and editor fits mobile widths',flush=True)
    pages_context,pages=new_page(); login(pages,'active@example.test',path='library/index.html')
    expect(pages.locator('#stats')).to_have_text('201 bài học')
    pages.locator('.folder-head').first.click()
    href=pages.locator('a.lesson').first.get_attribute('href')
    assert pages.locator('a.lesson').first.evaluate('(a)=>a.href')==BASE+'library/'+href
    assert pages.request.get(BASE+'library/'+href).status==200
    pages.goto(BASE+'library/admin.html')
    expect(pages.locator('#auth-message')).to_contain_text('Chỉ tài khoản Admin')
    count+=1; print('PASS GitHub Pages /library/ prefix: Firebase sign-in, catalog and exercise links resolve correctly',flush=True)
    pages_context.close()
    admin.locator('#logout').click(); expect(admin.locator('#admin-panel')).to_be_hidden()
    expect(admin.locator('#lesson-list')).to_be_empty()
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
