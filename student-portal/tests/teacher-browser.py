"""Successful teacher login, membership revocation and logout on unchanged Pages UI."""
import functools,http.server,json,os,subprocess,threading
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[2]
# The fixture uses Admin SDK only against loopback demo emulators. No password logs.
seed="""
import {createRequire} from 'node:module';import {randomBytes} from 'node:crypto';
const require=createRequire(new URL('./student-portal/functions/package.json',import.meta.url));
const {initializeApp}=require('firebase-admin/app'),{getAuth}=require('firebase-admin/auth'),{getFirestore}=require('firebase-admin/firestore');
initializeApp({projectId:'demo-ht-english-library'});
const auth=getAuth(),db=getFirestore(),uid='portal-regression-teacher',password=randomBytes(18).toString('base64url');
await auth.createUser({uid,email:'portal-teacher@example.test',password});
await db.doc('libraryMembers/'+uid).set({email:'portal-teacher@example.test',name:'Teacher Regression',status:'active',updatedAt:new Date()});
const fs=await import('node:fs/promises');const catalog=JSON.parse(await fs.readFile('catalog/library-catalog.json','utf8'));
await db.doc('libraryCatalog/current').set({schemaVersion:1,count:catalog.count,sha256:catalog.sha256,dataJson:JSON.stringify(catalog.data),updatedAt:new Date()});
await fs.writeFile(process.env.PORTAL_TEACHER_CREDENTIALS,JSON.stringify({password}),{mode:0o600,flag:'wx'});
"""
private=Path(os.environ['PORTAL_TEST_CREDENTIALS']).parent/'teacher.json'
env=os.environ.copy();env['PORTAL_TEACHER_CREDENTIALS']=str(private)
subprocess.run(['node','--input-type=module','-e',seed],cwd=ROOT,env=env,check=True,stdout=subprocess.DEVNULL)
password=json.loads(private.read_text())['password']
class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}'
config='export const firebaseConfig={projectId:"demo-ht-english-library"};export const ADMIN_UID="4Y82k6RBaRUPflZriPsUvQv1qKj2";export const useEmulators=true;'
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['CHROMIUM_PATH'],args=['--no-sandbox'])
        context=browser.new_context()
        def route(r):
            if r.request.url.endswith('/assets/firebase-config.js'):r.fulfill(content_type='text/javascript',body=config)
            elif r.request.url.startswith(('http://127.0.0.1:','http://localhost:')):r.continue_()
            elif 'www.google.com/images/cleardot.gif' in r.request.url:r.fulfill(content_type='image/gif',body=b'')
            else:r.abort()
        context.route('**/*',route)
        page=context.new_page();page.goto(BASE)
        expect(page.locator('#library')).to_be_hidden()
        page.locator('#email').fill('portal-teacher@example.test');page.locator('#password').fill('incorrect-regression-password')
        with page.expect_response(lambda r:'accounts:signInWithPassword' in r.url) as wrong:
            page.locator('#login-submit').click()
        assert wrong.value.status==400
        expect(page.locator('#auth-message')).to_contain_text('Email hoặc mật khẩu không đúng')
        page.locator('#password').fill(password)
        with page.expect_response(lambda r:'accounts:signInWithPassword' in r.url) as response:
            page.locator('#login-submit').click()
        assert response.value.status==200,{'status':response.value.status,'error':response.value.json().get('error',{}).get('message')}
        expect(page.locator('#library')).to_be_visible(timeout=15000)
        expected=json.loads((ROOT/'catalog/current-library-catalog.json').read_text())['count']
        expect(page.locator('#stats')).to_have_text(str(expected)+' bài học')
        assert page.locator('a.lesson').count()>0
        page.get_by_role('button',name='Grade 8',exact=True).click()
        expect(page.locator('a.lesson[href="grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-dual-mode.html"]')).to_have_count(1)
        expect(page.locator('#admin-link')).to_be_hidden()
        def status(value):
            source="""import {createRequire} from 'node:module';const require=createRequire(new URL('./student-portal/functions/package.json',import.meta.url));require('firebase-admin/app').initializeApp({projectId:'demo-ht-english-library'});await require('firebase-admin/firestore').getFirestore().doc('libraryMembers/portal-regression-teacher').update({status:process.argv[1]});"""
            subprocess.run(['node','--input-type=module','-e',source,value],cwd=ROOT,env=env,check=True,stdout=subprocess.DEVNULL)
        status('locked');expect(page.locator('#library')).to_be_hidden()
        expect(page.locator('#auth-message')).to_contain_text('đang bị khóa')
        status('active');expect(page.locator('#library')).to_be_visible()
        page.locator('#logout').click();expect(page.locator('#library')).to_be_hidden()
        expect(page.locator('#login-form')).to_be_visible()
        browser.close()
    print('PASS unchanged teacher UI: active teacher login, catalog, no Admin access, live lock/unlock, and logout',flush=True)
finally:
    server.shutdown();server.server_close();private.unlink(missing_ok=True)
