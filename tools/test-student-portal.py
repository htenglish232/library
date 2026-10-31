"""Auth/Functions/Hosting emulators + checksum-verified official Firestore JAR.

Only demo projects and loopback sockets. All processes started here are stopped.
Screenshots/reports are retained in /tmp; random demo credentials are deleted.
"""
import ast, hashlib, json, os, pathlib, shutil, socket, subprocess, tempfile, time, tarfile, urllib.request

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=pathlib.Path('/tmp/ht-student-portal')
OUT.mkdir(exist_ok=True)
SOURCE=ROOT/'tools/test-emulators-official.py'
# Read only literal pinned artifact metadata; never disable checksum verification.
metadata={}
for node in ast.parse(SOURCE.read_text()).body:
    if isinstance(node,ast.Assign):
        for target in node.targets:
            if isinstance(target,ast.Name) and target.id in ['JAR_SHA','ARCHIVE_SHA','ARCHIVE_SIZE','URL']:
                metadata[target.id]=ast.literal_eval(node.value)
cache=pathlib.Path(os.environ.get('FIREBASE_EMULATORS_PATH','/workspace/.cache/firebase' if pathlib.Path('/workspace/.cache/firebase').exists() else tempfile.gettempdir()+'/library-firebase-emulators'))
cache.mkdir(parents=True,exist_ok=True)
jar=cache/'cloud-sdk-firestore-emulator-1.22.0.jar'
if not jar.exists():
    archive=cache/'cloud-sdk-firestore-1.22.0.tar.gz'
    if not archive.exists():
        partial=archive.with_suffix('.partial')
        try:
            with urllib.request.urlopen(metadata['URL'],timeout=60) as response,partial.open('wb') as output:shutil.copyfileobj(response,output)
            with partial.open('rb') as file:
                if partial.stat().st_size!=metadata['ARCHIVE_SIZE'] or hashlib.file_digest(file,'sha256').hexdigest()!=metadata['ARCHIVE_SHA']:raise RuntimeError('Official emulator archive checksum/size mismatch')
            partial.replace(archive)
        finally:partial.unlink(missing_ok=True)
    with archive.open('rb') as file:
        if archive.stat().st_size!=metadata['ARCHIVE_SIZE'] or hashlib.file_digest(file,'sha256').hexdigest()!=metadata['ARCHIVE_SHA']:raise RuntimeError('Cached emulator archive checksum mismatch')
    with tarfile.open(archive) as tar:
        with tar.extractfile('platform/cloud-firestore-emulator/cloud-firestore-emulator.jar') as source,jar.open('wb') as output:shutil.copyfileobj(source,output)
with jar.open('rb') as file:
    if hashlib.file_digest(file,'sha256').hexdigest()!=metadata['JAR_SHA']:raise RuntimeError('Firestore JAR checksum mismatch.')
for port in [8080,9099,5000,5001]:
    with socket.socket() as probe:
        if probe.connect_ex(('127.0.0.1',port))==0:raise RuntimeError(f'Port {port} in use; do not stop unrelated services.')
env=os.environ.copy()
node22=pathlib.Path('/workspace/.tools/portal-node/node_modules/node/bin')
env['PATH']=str(node22)+':/workspace/library-venv/bin:'+env['PATH']
env['NODE_OPTIONS']=(env.get('NODE_OPTIONS','')+' --require='+str(ROOT/'tools/firebase-loopback-proxy.cjs')).strip()
env.update(FIRESTORE_EMULATOR_HOST='127.0.0.1:8080',
           FIREBASE_AUTH_EMULATOR_HOST='127.0.0.1:9099',
           XDG_CONFIG_HOME=env.get('XDG_CONFIG_HOME',tempfile.gettempdir()+'/ht-student-config'),
           CHROMIUM_PATH=env.get('CHROMIUM_PATH','/usr/bin/chromium'))
subprocess.run(['node','tools/build-student-portal.mjs','--emulator'],cwd=ROOT,env=env,check=True)
subprocess.run(['node','--test','student-portal/tests/unit.test.mjs','student-portal/tests/delivery.test.mjs'],cwd=ROOT,env=env,check=True)
runtime=ROOT/'student-portal/.runtime'
runtime.mkdir(exist_ok=True)
config=json.loads((ROOT/'firebase.student-portal.json').read_text())
config['functions'][0]['source']='../functions'
config['hosting'].pop('target',None)
config['hosting']['site']='demo-ht-student-portal'
config['hosting']['public']='../dist'
config['firestore']['rules']='../firestore.rules'
config['firestore']['indexes']='../firestore.indexes.json'
for entry in config['hosting'].get('headers',[]):
    for header in entry['headers']:
        if header['key']=='Content-Security-Policy':
            header['value']=header['value'].replace("connect-src 'self'","connect-src 'self' http://127.0.0.1:9099")
(runtime/'firebase.json').write_text(json.dumps(config))
credentials=pathlib.Path(tempfile.mkdtemp(prefix='ht-portal-private-'))/'credentials.json'
env['PORTAL_TEST_CREDENTIALS']=str(credentials)
functionenv=ROOT/'student-portal/functions/.env.local'
if functionenv.exists():raise RuntimeError('Preserve existing Functions .env.local; move it explicitly before this runner.')
functionenv.write_text('PORTAL_ENABLED=true\n');functionenv.chmod(0o600)
log=(OUT/'firestore.log').open('w')
process=subprocess.Popen(['java','-cp',str(jar),'com.google.cloud.datastore.emulator.firestore.CloudFirestore',
    '--host','127.0.0.1','--port','8080','--rules',str(ROOT/'student-portal/firestore.rules'),
    '--project_id','demo-ht-student-portal','--single_project_mode','false'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
try:
    deadline=time.monotonic()+40
    while True:
        if process.poll() is not None:raise RuntimeError('Firestore failed: see /tmp/ht-student-portal/firestore.log')
        with socket.socket() as probe:
            if probe.connect_ex(('127.0.0.1',8080))==0:break
        if time.monotonic()>deadline:raise RuntimeError('Firestore startup timed out')
        time.sleep(.2)
    command='node --test student-portal/tests/emulators.test.mjs && python3 student-portal/tests/browser.py && npm run test:rules'
    if os.environ.get('PORTAL_TEST_COMMAND'):command=os.environ['PORTAL_TEST_COMMAND']
    result=subprocess.run([str(ROOT/'node_modules/.bin/firebase'),'emulators:exec',
        '--config',str(runtime/'firebase.json'),'--project','demo-ht-student-portal',
        '--only','auth,functions,hosting',command],cwd=ROOT,env=env)
    if result.returncode==0 and not os.environ.get('PORTAL_TEST_COMMAND'):
        # Auth Emulator's Web API always uses its default project. Restart Auth
        # with the teacher demo project, so both applications run unchanged.
        result=subprocess.run([str(ROOT/'node_modules/.bin/firebase'),'emulators:exec',
            '--config',str(ROOT/'firebase.json'),'--project','demo-ht-english-library',
            '--only','auth','python3 tests/auth-login-browser.py && python3 student-portal/tests/teacher-browser.py'],
            cwd=ROOT,env=env)
finally:
    process.terminate()
    try:process.wait(timeout=15)
    except subprocess.TimeoutExpired:process.kill();process.wait()
    log.close();functionenv.unlink(missing_ok=True);shutil.rmtree(credentials.parent)
raise SystemExit(result.returncode)
