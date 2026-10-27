"""Real browser and Firebase Auth/Firestore emulators; no production requests."""
import re, base64, functools, http.server, json, os, secrets, shutil, subprocess, threading, urllib.request
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
baseline=json.loads((ROOT/'catalog/current-baseline.json').read_text())['commit']
release=json.loads((ROOT/'catalog/current-library-catalog.json').read_text())
legacy_count=json.loads((ROOT/'catalog/library-catalog.json').read_text())['count']
release_additions=release['count']-legacy_count
release_ids=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import {RELEASE_IDS} from './assets/catalog-release.js'; console.log(JSON.stringify(RELEASE_IDS));"],cwd=ROOT,text=True))
original_html=subprocess.check_output(['git','show',baseline+':index.html'],cwd=ROOT,text=True)
blocked=[]
sdk_probes=[]

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
            elif request.request.method=='GET' and request.request.resource_type=='image' and request.request.url.startswith('https://www.google.com/images/cleardot.gif?zx='):
                # Existing WebChannel SDK reachability probe: satisfy locally,
                # never forward a third-party request from emulator tests.
                sdk_probes.append('WebChannel reachability image fulfilled locally')
                request.fulfill(content_type='image/gif',body=base64.b64decode('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'))
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
    assert page.locator('a[href^="grade-"], a[href^="Apps for IELTS/"]').count()==0
    assert page.locator('.school-folder').count()==0
    assert page.locator('#school-preview, #truc-tuan-game-link').count()==0
    for width in [360,375,390,430]:
        page.set_viewport_size({'width':width,'height':850})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),('login overflow',width)
    count+=1; print('PASS anonymous login screen contains no material, exam, school or game links',flush=True); context.close()

    context,page=new_page(); login(page,'active@example.test','wrong-password')
    expect(page.locator('#auth-message')).to_contain_text('Email hoặc mật khẩu không đúng')
    expect(page.locator('#library')).to_be_hidden()
    count+=1; print('PASS wrong-password login rejected',flush=True); context.close()

    for label,text in [('unapproved','chưa được cấp quyền'),('locked','đang bị khóa'),('revoked','đã bị thu hồi'),('disabled','đã bị vô hiệu hóa')]:
        context,page=new_page(); login(page,label+'@example.test')
        expect(page.locator('#auth-message')).to_contain_text(text)
        expect(page.locator('#library')).to_be_hidden(); assert page.locator('a.lesson').count()==0
        assert page.locator('a[href^="grade-"], a[href^="Apps for IELTS/"]').count()==0
        count+=1; print('PASS '+label+' account denied',flush=True); context.close()

    teacher_context,teacher=new_page(); login(teacher,'active@example.test')
    expect(teacher.locator('#library')).to_be_visible()
    assert teacher.locator('#school-preview').count()==0
    expect(teacher.locator('#stats')).to_have_text(f'{201+release_additions} bài học')
    data=release['data']
    baseline_context,baseline_page=new_page(); baseline_page.goto(BASE+'baseline-index.html')
    for grade in data:
        if grade['grade']=='Apps for IELTS': continue
        teacher.get_by_role('button',name=grade['grade'],exact=True).click()
        baseline_page.get_by_role('button',name=grade['grade'],exact=True).click()
        expected=baseline_page.locator('a.lesson').evaluate_all('(els)=>els.map(e=>e.getAttribute("href"))')
        actual=teacher.locator('a.lesson').evaluate_all('(els)=>els.map(e=>e.getAttribute("href"))')
        game_href='grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-game-test.html'
        without_game=[href for href in actual if href!=game_href and not href.endswith('/practice-game-pilot.html')]
        assert sorted(href for href in actual if href in expected)==sorted(expected),(grade['grade'],'all current-main links retained exactly once')
        approved={l['href'] for g in data if g['grade']==grade['grade'] for u in g['units'] for l in u['lessons']}
        assert set(actual)==approved,(grade['grade'],'only approved recovered links added')
        exam_hrefs={l['href'] for u in grade['units'] if u.get('type')=='exam-folder' for l in u['lessons']}
        assert [h for h in without_game if h in expected and h not in exam_hrefs]==[h for h in expected if h not in exam_hrefs],(grade['grade'],'current non-exam order')
        if grade['grade']=='Grade 8':
            schools=teacher.locator('.exam-school-folder .school-folder')
            assert schools.count()==17
            phuong=schools.filter(has=teacher.locator('.school-name',has_text='THCS Phương Định'))
            assert phuong.count()==1 and phuong.locator('a.lesson').count()==4
    teacher.get_by_role('button',name='Grade 8',exact=True).click()
    teacher.locator('.folder').filter(has=teacher.get_by_role('heading',name='Đề thi GHK1',exact=True)).locator('.folder-head').click()
    school=teacher.locator('.exam-school-folder .school-folder').filter(has=teacher.locator('.school-name',has_text='THCS Trực Tuấn'))
    expect(school.locator('a.lesson')).to_have_count(3)
    expect(school.locator('a.lesson').first).to_be_hidden()
    school.locator('.school-summary').click()
    expect(school.locator('.exam-resource')).to_be_visible()
    school.locator('.school-summary').focus()
    school.locator('.school-summary').press('Enter')
    expect(school.locator('.exam-resource')).to_be_hidden()
    school.locator('.school-summary').press('Enter')
    screenshots=Path(os.environ.get('SCHOOL_TEST_OUTPUT','/tmp/ht-school-folders'))
    screenshots.mkdir(parents=True,exist_ok=True)
    for width in [360,390,768,1280]:
        teacher.set_viewport_size({'width':width,'height':900})
        assert teacher.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),('school folder overflow',width)
        if width in [390,1280]:
            teacher.screenshot(path=str(screenshots/f'schools-{width}.png'),full_page=True)
    teacher.set_viewport_size({'width':1280,'height':900})
    game=school.locator('a.lesson[href="grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-game-test.html"]')
    expect(game).to_be_visible()
    game.click()
    expect(teacher.locator('#welcome')).to_be_visible()
    teacher.locator('#student-name').fill('Học sinh mở từ thư viện')
    teacher.locator('#start-form button').click()
    expect(teacher.locator('#question-position')).to_have_text('Câu 1 / 42')
    teacher.go_back()
    expect(teacher.locator('#library')).to_be_visible()
    teacher.get_by_role('button',name='Grade 8',exact=True).click()
    teacher.locator('#search').fill('Game luyện đề')
    expect(teacher.locator('a.lesson[href="grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-game-test.html"]')).to_be_visible()
    teacher.locator('#search').fill('2 chế độ')
    dual_href='grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-dual-mode.html'
    dual=teacher.locator('a.lesson').filter(has_text='Game đề số 1 – THCS Trực Tuấn')
    expect(dual).to_have_count(1);assert dual.get_attribute('href')==dual_href
    dual_errors=[];teacher.on('pageerror',lambda e:dual_errors.append(str(e)))
    dual.click();expect(teacher.locator('#welcome')).to_be_visible()
    assert teacher.evaluate('HT_PRACTICE_DATA.questions.length')==42
    teacher.locator('#student-name').fill('Mở từ thư viện')
    teacher.locator('#start-form button').click()
    expect(teacher.locator('#question-position')).to_have_text('Câu 1 / 42')
    teacher.locator('#answer-area input[value="C"]').check();teacher.locator('#check-answer').click()
    expect(teacher.locator('#xp-total')).to_have_text('✦ 10 XP')
    teacher.locator('#results-button').click();teacher.locator('#continue-playing').click()
    expect(teacher.locator('#xp-total')).to_have_text('✦ 10 XP')
    for qid in ['q1','q7']:
        teacher.locator('#jump-question').select_option(qid)
        teacher.wait_for_function('document.querySelector("audio").readyState>=1')
        teacher.locator('#audio-toggle').click();teacher.wait_for_function('!document.querySelector("audio").paused')
        teacher.locator('#audio-toggle').click()
    teacher.reload();teacher.locator('#student-name').fill('Mở từ thư viện');teacher.locator('#start-form button').click()
    expect(teacher.locator('#resume-panel')).to_be_visible();teacher.locator('#resume-button').click()
    expect(teacher.locator('#xp-total')).to_have_text('✦ 10 XP')
    assert not dual_errors,dual_errors
    teacher.goto(BASE+'index.html');expect(teacher.locator('#library')).to_be_visible()
    teacher.get_by_role('button',name='Grade 8',exact=True).click()
    print('PASS exact dual-mode label opens 42 questions from the authenticated library; whole-exam navigation, MP3s and persisted progress work',flush=True)
    for name,total in [('Trực Khang',42),('Trực Hùng',43),('Trực Chính',42)]:
        teacher.locator('#search').fill(name)
        link=teacher.locator('a.game-resource[href$="/practice-game-pilot.html"]').filter(has=teacher.locator('strong',has_text=re.compile('^'+re.escape(f'Game đề số 1 – THCS {name}')+'$')))
        expect(link).to_be_visible()
        group=link.locator('xpath=ancestor::details')
        expect(group.locator('a.exam-resource')).to_have_count(1)
        link.click();expect(teacher.locator('#welcome')).to_be_visible()
        teacher.locator('#student-name').fill('Học sinh từ index')
        teacher.locator('#start-form button').click()
        expect(teacher.locator('#question-position')).to_have_text(f'Câu 1 / {total}')
        teacher.go_back();expect(teacher.locator('#library')).to_be_visible()
        teacher.get_by_role('button',name='Grade 8',exact=True).click()
        teacher.locator('#search').fill('Game luyện đề')
    print('PASS all three new game links open from the authenticated index beside their original exams',flush=True)
    all_games=json.loads((ROOT/'docs/grade8-all-dual-mode/inventory.json').read_text())['games']
    for entry in all_games:
        teacher.locator('#search').fill(entry['school'])
        link=teacher.locator(f'a.lesson[href="{entry["game"]}"]')
        expect(link).to_have_count(1);assert link.get_attribute('href')==entry['game']
        link.click();expect(teacher.locator('#welcome')).to_be_visible()
        teacher.wait_for_function('typeof HT_PRACTICE_DATA !== "undefined"')
        assert teacher.evaluate('HT_PRACTICE_DATA.questions.length')==entry['questions']
        teacher.go_back();expect(teacher.locator('#library')).to_be_visible();teacher.get_by_role('button',name='Grade 8',exact=True).click()
    count+=1;print('PASS all 19 exact dual-mode links open their own source data from the authenticated library, including both exams of Dao Su Tich and Phuong Dinh',flush=True)

    teacher.locator('#search').fill('Phương Định')
    matched=teacher.locator('.exam-school-folder .school-folder')
    expect(matched).to_have_count(1)
    expect(matched.locator('a.lesson')).to_have_count(4)
    expect(matched.locator('a.lesson').first).to_be_visible()
    teacher.locator('#search').fill('')
    teacher.get_by_role('button',name='Apps for IELTS',exact=True).click()
    teacher.locator('.folder-head').click()
    ielts=teacher.locator('a.lesson').filter(has_text='Luyện viết IELTS')
    expect(ielts).to_be_visible()
    assert ielts.get_attribute('href')=='Apps for IELTS/Luyện viết IELTS.html'
    app_response=teacher.request.get(BASE+ielts.get_attribute('href'))
    assert app_response.status==200 and 'IELTS Writing Practice' in app_response.text()
    teacher.locator('#search').fill('Luyện viết')
    expect(teacher.locator('a.lesson').filter(has_text='Luyện viết IELTS')).to_be_visible()
    teacher.locator('#search').fill('')
    baseline_context.close()
    count+=1; print('PASS active teacher sees all current-main links, school folders, grouped exam/game, keyboard controls, mobile layout and search; non-exam order preserved',flush=True)
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
    expect(teacher.locator('#stats')).to_have_text(f'{201+release_additions} bài học')
    admin.locator('#save-catalog').click()
    expect(admin.locator('#editor-message')).to_contain_text('phiên bản 1')
    expect(teacher.locator('#stats')).to_have_text(f'{202+release_additions} bài học')
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
    expect(teacher.locator('#stats')).to_have_text(f'{201+release_additions} bài học')
    assert teacher.locator('a.lesson').count()==0
    admin.locator('#toggle-unit').click()
    admin.locator('.catalog-item').get_by_role('button',name='Ẩn bài',exact=True).click()
    admin.locator('#save-catalog').click(); expect(admin.locator('#editor-message')).to_contain_text('phiên bản 3')
    expect(teacher.locator('#stats')).to_have_text(f'{201+release_additions} bài học')
    admin.locator('.catalog-item').get_by_role('button',name='Hiện bài',exact=True).click()
    admin.locator('.catalog-item').get_by_role('button',name='Sửa',exact=True).click()
    admin.locator('#lesson-title').fill('Bài mới đã sửa'); admin.locator('#lesson-submit').click()
    admin.locator('#save-catalog').click(); expect(admin.locator('#editor-message')).to_contain_text('phiên bản 4')
    expect(teacher.locator('#stats')).to_have_text(f'{202+release_additions} bài học')
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
    expect(teacher.locator('#stats')).to_have_text(f'{203+release_additions} bài học')
    teacher.get_by_role('button',name='Grade 10',exact=True).click()
    assert teacher.locator('a.lesson strong').all_text_contents()==['Bài thứ hai','Bài mới đã sửa']
    count+=1; print('PASS lesson and folder add/delete/reorder, grade rename/reorder/sort and dynamic count above 201',flush=True)

    admin.locator('#toggle-grade').click(); admin.locator('#save-catalog').click()
    expect(admin.locator('#editor-message')).to_contain_text('phiên bản 6')
    expect(teacher.locator('#stats')).to_have_text(f'{201+release_additions} bài học')
    expect(teacher.get_by_role('button',name='Grade 10',exact=True)).to_have_count(0)
    admin.locator('#toggle-grade').click(); admin.locator('#save-catalog').click()
    expect(admin.locator('#editor-message')).to_contain_text('phiên bản 7')
    expect(teacher.locator('#stats')).to_have_text(f'{203+release_additions} bài học')
    with admin.expect_download() as download_info: admin.locator('#backup-catalog').click()
    backup=json.loads(Path(download_info.value.path()).read_text())
    assert backup['count']==203 and backup['schemaVersion']==2 and not backup['includesUnsavedDraft']
    admin.locator('.catalog-item').filter(has_text='Bài thứ hai').get_by_role('button',name='Xóa bài',exact=True).click()
    admin.locator('#save-catalog').click(); expect(admin.locator('#editor-message')).to_contain_text('phiên bản 8')
    expect(teacher.locator('#stats')).to_have_text(f'{202+release_additions} bài học')
    bad_backup=json.loads(json.dumps(backup)); bad_backup['data'][0]['grade']='Changed without checksum'
    admin.locator('#restore-file').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':json.dumps(bad_backup).encode()})
    expect(admin.locator('#editor-message')).to_contain_text('SHA-256 không khớp')
    expect(admin.locator('#save-catalog')).to_be_disabled()
    admin.locator('#restore-file').set_input_files({'name':'good.json','mimeType':'application/json','buffer':json.dumps(backup).encode()})
    expect(admin.locator('#editor-message')).to_contain_text('khôi phục vào bản nháp')
    expect(teacher.locator('#stats')).to_have_text(f'{202+release_additions} bài học')
    admin.locator('#save-catalog').click(); expect(admin.locator('#editor-message')).to_contain_text('phiên bản 9')
    expect(teacher.locator('#stats')).to_have_text(f'{203+release_additions} bài học')
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
    expect(teacher.locator('#stats')).to_have_text(f'{203+release_additions} bài học')
    admin.locator('#save-catalog').click(); expect(admin.locator('#editor-message')).to_contain_text('phiên bản 11')
    expect(teacher.locator('#stats')).to_have_text(f'{201+release_additions} bài học')
    restored=admin.evaluate("""async()=>{const {loadCatalog}=await import('./assets/catalog-store.js');return (await loadCatalog()).fields.dataJson}""")
    assert restored==original_fields['dataJson']
    for width in [360,375,390,430]:
        admin.set_viewport_size({'width':width,'height':850})
        assert admin.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),('editor overflow',width)
    count+=1; print('PASS history restore preserves original 201 links exactly, keeps all newer versions and editor fits mobile widths',flush=True)
    pages_context,pages=new_page(); login(pages,'active@example.test',path='library/index.html')
    expect(pages.locator('#stats')).to_have_text(f'{201+release_additions} bài học')
    pages.locator('.folder-head').first.click()
    href=pages.locator('a.lesson').first.get_attribute('href')
    assert pages.locator('a.lesson').first.evaluate('(a)=>a.href')==BASE+'library/'+href
    assert pages.request.get(BASE+'library/'+href).status==200
    pages.get_by_role('button',name='Grade 8',exact=True).click();pages.locator('#search').fill('2 chế độ')
    link=pages.locator('a.lesson').filter(has_text='Game đề số 1 – THCS Trực Tuấn')
    expect(link).to_have_count(1)
    expected='https://htenglish232.github.io/library/grade-8/De_thi_GHK1/1_THCS%20Truc%20Tuan/truc-tuan-dual-mode.html'
    assert link.evaluate('(a)=>new URL(a.getAttribute("href"),"https://htenglish232.github.io/library/index.html").href')==expected
    link.click();expect(pages.locator('#welcome')).to_be_visible()
    pages.locator('#student-name').fill('Kiểm thử Pages');pages.locator('#start-form button').click()
    expect(pages.locator('#question-position')).to_have_text('Câu 1 / 42')
    assert '/library/grade-8/' in pages.url
    pages.goto(BASE+'library/admin.html')
    expect(pages.locator('#auth-message')).to_contain_text('Chỉ tài khoản Admin')
    count+=1; print('PASS GitHub Pages /library/ prefix: Firebase sign-in, catalog and exercise links resolve correctly',flush=True)
    pages_context.close()
    # Release additions only stage a draft. The existing document remains unchanged until Save.
    before_release=admin.evaluate("""async()=>{const {loadCatalog}=await import('./assets/catalog-store.js');return (await loadCatalog()).fields}""")
    admin.locator('#add-release-lessons').click()
    expect(admin.locator('#editor-summary')).to_contain_text(str(release['count'])+' bài tập tổng cộng')
    still_unchanged=admin.evaluate("""async()=>{const {loadCatalog}=await import('./assets/catalog-store.js');return (await loadCatalog()).fields}""")
    assert before_release==still_unchanged
    admin.locator('#save-catalog').click()
    expect(admin.locator('#editor-message')).to_contain_text('phiên bản 12')
    expect(teacher.locator('#stats')).to_have_text(str(release['count'])+' bài học')
    adopted=admin.evaluate("""async()=>{const {loadCatalog}=await import('./assets/catalog-store.js');return (await loadCatalog()).fields}""")
    assert adopted['count']==release['count'] and json.loads(adopted['dataJson'])['releaseApplied']==release_ids
    original_archive=admin.evaluate("""async()=>{const {db}=await import('./assets/firebase-client.js');const {doc,getDocFromServer}=await import('./assets/firebase-sdk.js');return (await getDocFromServer(doc(db,'libraryCatalogHistory','11'))).data().snapshot}""")
    assert original_archive==before_release
    admin.locator('#grade-select').select_option('1');admin.locator('#unit-select').select_option('0')
    removed=admin.locator('.catalog-item').filter(has_text='Unit 13 Future')
    removed.get_by_role('button',name='Xóa bài',exact=True).click();admin.locator('#save-catalog').click()
    expect(admin.locator('#editor-message')).to_contain_text('phiên bản 13')
    expect(teacher.locator('#stats')).to_have_text(str(release['count']-1)+' bài học')
    teacher.get_by_role('button',name='Grade 5',exact=True).click()
    assert teacher.locator('a.lesson[href="grade-5/Bo_Tro_Ngu_Phap/unit_13_future_will.html"]').count()==0
    count+=1; print('PASS manual release adoption: no writes before Save, exact previous document archived, later Admin deletion respected',flush=True)
    teacher.reload()
    expect(teacher.locator('#library')).to_be_visible()
    expect(teacher.locator('#stats')).to_have_text(str(release['count']-1)+' bài học')
    count+=1; print('PASS reload restores Firebase session and verifies server permission/catalog again',flush=True)
    teacher.locator('#logout').click()
    expect(teacher.locator('#login-form')).to_be_visible()
    expect(teacher.locator('#library')).to_be_hidden()
    assert teacher.locator('a[href^="grade-"], a[href^="Apps for IELTS/"]').count()==0
    admin.locator('#logout').click(); expect(admin.locator('#admin-panel')).to_be_hidden()
    expect(admin.locator('#lesson-list')).to_be_empty()
    count+=1; print('PASS logout clears teacher material links and admin data',flush=True)

    context,exercise=new_page()
    url='grade-7/De_thi_GHK_1/1_THCS_Truc_Thai/1%20THCS%20Truc%20Thai.html'
    assert exercise.goto(BASE+url).status==200
    assert exercise.locator('.question-card').count()>0
    exercise.locator('#studentName').fill('Học sinh kiểm thử')
    exercise.locator('#submitBtn').click(); exercise.locator('#confirmSubmit').click()
    expect(exercise.locator('#submissionBanner')).to_be_visible()
    expect(exercise.locator('#submitBtn')).to_be_disabled()
    audio=exercise.request.get(BASE+'grade-7/De_thi_GHK_1/1_THCS_Truc_Thai/Task%201.mp3')
    assert audio.status==200 and len(audio.body())>1000
    count+=1; print('PASS anonymous direct exercise, scoring submission and audio request',flush=True)
    # Emulate a production catalog that adopted previous releases, then deleted
    # the old game and hid the exam. Stage only the new release, never resurrect.
    upgrade_context,upgrade=new_page();login(upgrade,'admin@example.test',path='admin.html')
    expect(upgrade.locator('#admin-panel')).to_be_visible()
    upgrade.on('dialog',lambda dialog:dialog.accept())
    prepared=json.loads(subprocess.check_output(['node','tests/seed-previous-dual-release.mjs'],cwd=ROOT,text=True))
    upgrade.reload();expect(upgrade.locator('#editor-summary')).to_contain_text(str(prepared['count'])+' bài tập tổng cộng')
    pre=upgrade.evaluate("async()=>{const {loadCatalog}=await import('./assets/catalog-store.js');return (await loadCatalog()).fields;}")
    upgrade.locator('#add-release-lessons').click()
    expect(upgrade.locator('#editor-summary')).to_contain_text(str(prepared['count']+1)+' bài tập tổng cộng')
    assert upgrade.evaluate("async()=>{const {loadCatalog}=await import('./assets/catalog-store.js');return (await loadCatalog()).fields;}")==pre
    upgrade.locator('#save-catalog').click();expect(upgrade.locator('#editor-message')).to_contain_text('Đã lưu và đọc lại xác minh')
    saved=upgrade.evaluate("async()=>{const {loadCatalog}=await import('./assets/catalog-store.js');return (await loadCatalog()).data;}")
    folder=next(u for g in saved if g['grade']=='Khối 8' for u in g['units'] if u['name']=='Giữa kỳ')
    assert not any(l['href'].endswith('/truc-tuan-game-test.html') for l in folder['lessons'])
    assert next(l for l in folder['lessons'] if l['href'].endswith('/1. THCS Truc Tuan.html'))['hidden']
    assert sum(l['href'].endswith('/truc-tuan-dual-mode.html') for l in folder['lessons'])==1
    # After adoption, Admin hide/show/delete keeps control over the new item.
    viewer_context,viewer=new_page();login(viewer,'active@example.test');expect(viewer.locator('#library')).to_be_visible()
    viewer.get_by_role('button',name='Khối 8',exact=True).click();viewer.locator('#search').fill('Trực Tuấn')
    expect(viewer.locator('a.lesson strong')).to_have_text('Game đề số 1 – THCS Trực Tuấn')
    upgrade.locator('#grade-select').select_option(label='Khối 8');upgrade.locator('#unit-select').select_option(label='Giữa kỳ')
    row=upgrade.locator('.catalog-item').filter(has_text='Game đề số 1 – THCS Trực Tuấn')
    row.get_by_role('button',name='Ẩn bài',exact=True).click();upgrade.locator('#save-catalog').click()
    expect(viewer.locator('a.lesson')).to_have_count(0)
    row=upgrade.locator('.catalog-item').filter(has_text='Game đề số 1 – THCS Trực Tuấn')
    row.get_by_role('button',name='Hiện bài',exact=True).click();upgrade.locator('#save-catalog').click()
    expect(viewer.locator('a.lesson strong')).to_have_text('Game đề số 1 – THCS Trực Tuấn')
    row=upgrade.locator('.catalog-item').filter(has_text='Game đề số 1 – THCS Trực Tuấn')
    row.get_by_role('button',name='Xóa bài',exact=True).click();upgrade.locator('#save-catalog').click()
    expect(viewer.locator('a.lesson')).to_have_count(0);expect(upgrade.locator('#add-release-lessons')).to_be_disabled()
    upgrade.reload();expect(upgrade.locator('#add-release-lessons')).to_be_disabled()
    count+=1;print('PASS previous release deletions stay deleted; new batch stages exactly one link without writes until Save; Admin hide/show/delete survives reload and does not resurrect either game',flush=True)
    # An already-linked game still needs adoption metadata to make later deletion durable.
    existing=json.loads(subprocess.check_output(['node','tests/seed-previous-dual-release.mjs','--already-linked'],cwd=ROOT,text=True))
    upgrade.reload();expect(upgrade.locator('#editor-summary')).to_contain_text(str(existing['count'])+' bài tập tổng cộng')
    expect(upgrade.locator('#add-release-lessons')).to_be_enabled()
    expect(viewer.locator('a.lesson strong')).to_have_text('Game đề số 1 – THCS Trực Tuấn')
    upgrade.locator('#add-release-lessons').click();expect(upgrade.locator('#editor-summary')).to_contain_text(str(existing['count'])+' bài tập tổng cộng')
    upgrade.locator('#save-catalog').click();expect(upgrade.locator('#editor-message')).to_contain_text('Đã lưu và đọc lại xác minh')
    adopted=upgrade.evaluate("async()=>{const {loadCatalog}=await import('./assets/catalog-store.js');return (await loadCatalog()).fields;}")
    assert set(json.loads(adopted['dataJson'])['releaseApplied'])==set(release_ids)
    upgrade.locator('#grade-select').select_option(label='Khối 8');upgrade.locator('#unit-select').select_option(label='Giữa kỳ')
    upgrade.locator('.catalog-item').filter(has_text='Game đề số 1 – THCS Trực Tuấn').get_by_role('button',name='Xóa bài',exact=True).click()
    upgrade.locator('#save-catalog').click();expect(viewer.locator('a.lesson')).to_have_count(0)
    upgrade.reload();expect(upgrade.locator('#add-release-lessons')).to_be_disabled()
    count+=1;print('PASS game already present in Firebase appears once; metadata-only adoption preserves count and makes subsequent Admin deletion durable',flush=True)

    # Both new batches adopt 18 additions; earlier deleted TT games stay deleted.
    all_prepared=json.loads(subprocess.check_output(['node','tests/seed-previous-dual-release.mjs','--previous-all'],cwd=ROOT,text=True))
    upgrade.reload();expect(upgrade.locator('#editor-summary')).to_contain_text(str(all_prepared['count'])+' bài tập tổng cộng')
    before_all=upgrade.evaluate("async()=>{const {loadCatalog}=await import('./assets/catalog-store.js');return (await loadCatalog()).fields;}")
    upgrade.locator('#add-release-lessons').click();expect(upgrade.locator('#editor-summary')).to_contain_text(str(all_prepared['count']+18)+' bài tập tổng cộng')
    assert upgrade.evaluate("async()=>{const {loadCatalog}=await import('./assets/catalog-store.js');return (await loadCatalog()).fields;}")==before_all
    upgrade.locator('#save-catalog').click();expect(upgrade.locator('#editor-message')).to_contain_text('Đã lưu và đọc lại xác minh')
    all_saved=upgrade.evaluate("async()=>{const {loadCatalog}=await import('./assets/catalog-store.js');return await loadCatalog();}")
    assert set(json.loads(all_saved['fields']['dataJson'])['releaseApplied'])==set(release_ids)
    all_folder=next(u for g in all_saved['data'] if g['grade']=='Khối 8' for u in g['units'] if u['name']=='Giữa kỳ')
    assert not any(l['href'].endswith(('/truc-tuan-game-test.html','/truc-tuan-dual-mode.html')) for l in all_folder['lessons'])
    assert next(l for l in all_folder['lessons'] if l['href'].endswith('/1. THCS Truc Tuan.html'))['hidden']
    assert sum(l['href'].endswith('/practice-dual-mode.html') for l in all_folder['lessons'])==18
    upgrade.locator('#grade-select').select_option(label='Khối 8');upgrade.locator('#unit-select').select_option(label='Giữa kỳ')
    viewer.locator('#search').fill('Cát Thành');expect(viewer.locator('a.lesson')).to_have_count(2)
    def cat_row():return upgrade.locator('.catalog-item').filter(has_text='Game đề số 1 – THCS Cát Thành')
    cat_row().get_by_role('button',name='Ẩn bài',exact=True).click();upgrade.locator('#save-catalog').click();expect(viewer.locator('a.lesson')).to_have_count(1)
    cat_row().get_by_role('button',name='Hiện bài',exact=True).click();upgrade.locator('#save-catalog').click();expect(viewer.locator('a.lesson')).to_have_count(2)
    cat_row().get_by_role('button',name='Xóa bài',exact=True).click();upgrade.locator('#save-catalog').click();expect(viewer.locator('a.lesson')).to_have_count(1)
    upgrade.reload();expect(upgrade.locator('#add-release-lessons')).to_be_disabled();viewer.reload();viewer.get_by_role('button',name='Khối 8',exact=True).click();viewer.locator('#search').fill('Cát Thành');expect(viewer.locator('a.lesson')).to_have_count(1)
    count+=1;print('PASS 18 new links stage only in draft, adopt once, preserve prior hidden/deleted entries, and support durable Admin hide/show/delete',flush=True)
    assert teacher.evaluate('''()=>Object.entries(localStorage).filter(([k])=>k.startsWith('htenglish:practice:v1:')).map(([,v])=>JSON.parse(v)).some(r=>r.state.student.name==='Mở từ thư viện'&&r.state.answers.q1.first.result==='correct')''')
    print('PASS catalog changes and Firebase logout leave the game localStorage progress intact',flush=True)
    viewer_context.close();upgrade_context.close()
    teacher_context.close(); admin_context.close(); context.close(); browser.close()
    assert not blocked, 'Unexpected external network requests: '+str(blocked)
    print(f'INFO {len(sdk_probes)} SDK reachability probes handled locally; none forwarded.',flush=True)
    print(f'PASS {count} browser scenarios; production network never contacted.')
server.shutdown(); server.server_close()
