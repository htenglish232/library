"""Verified official Google Cloud SDK fallback if Google Storage is blocked.

Starts local Firestore directly using its supported Java entry point, then runs
Firebase Auth Emulator and the same Rules/browser checks. Never deploys anything.
"""
import hashlib, os, pathlib, shutil, socket, subprocess, tarfile, tempfile, time, urllib.request

ROOT=pathlib.Path(__file__).resolve().parents[1]
CACHE=pathlib.Path(os.environ.get('FIREBASE_EMULATORS_PATH',str(pathlib.Path(tempfile.gettempdir())/'library-firebase-emulators')))
# Pinned to the official Cloud SDK component manifest checked during implementation.
VERSION='1.22.0'
URL='https://dl.google.com/dl/cloudsdk/channels/rapid/components/google-cloud-sdk-cloud-firestore-emulator-20260717053915.tar.gz'
ARCHIVE_SHA='e962450b637827664094959571fd92c3680de863936bd481bd0a050f76ca91ba'
JAR_SHA='6262939c48d3d6b08495931706b8920399e57d5f5918e6af133a3d30cb3ae369'
ARCHIVE_SIZE=70115087

def digest(path):
    with path.open('rb') as file:return hashlib.file_digest(file,'sha256').hexdigest()

CACHE.mkdir(parents=True,exist_ok=True)
archive=CACHE/'cloud-sdk-firestore-1.22.0.tar.gz'
if not archive.exists():
    partial=archive.with_suffix('.partial')
    try:
        with urllib.request.urlopen(URL,timeout=60) as response,partial.open('wb') as output:shutil.copyfileobj(response,output)
        if partial.stat().st_size!=ARCHIVE_SIZE or digest(partial)!=ARCHIVE_SHA:raise RuntimeError('Official archive checksum/size mismatch; refusing to execute.')
        partial.replace(archive)
    finally:
        if partial.exists():partial.unlink()
if archive.stat().st_size!=ARCHIVE_SIZE or digest(archive)!=ARCHIVE_SHA:raise RuntimeError('Cached archive checksum mismatch.')
jar=CACHE/'cloud-sdk-firestore-emulator-1.22.0.jar'
with tarfile.open(archive) as tar:
    member=tar.getmember('platform/cloud-firestore-emulator/cloud-firestore-emulator.jar')
    with tar.extractfile(member) as source,jar.open('wb') as output:shutil.copyfileobj(source,output)
if digest(jar)!=JAR_SHA:raise RuntimeError('JAR checksum mismatch; refusing to execute.')
print(f'Official Google Cloud SDK Firestore Emulator {VERSION}; archive and JAR SHA-256 verified.',flush=True)
with socket.socket() as probe:
    if probe.connect_ex(('127.0.0.1',8080))==0:raise RuntimeError('Port 8080 is already in use; do not stop unrelated processes.')
env=os.environ.copy();env['FIRESTORE_EMULATOR_HOST']='127.0.0.1:8080'
env.setdefault('XDG_CONFIG_HOME',str(CACHE/'config'))
env['FIREBASE_EMULATORS_PATH']=str(CACHE)
log=(CACHE/'firestore-standalone.log').open('w')
process=subprocess.Popen(['java','-cp',str(jar),'com.google.cloud.datastore.emulator.firestore.CloudFirestore','--host','127.0.0.1','--port','8080','--rules',str(ROOT/'firestore.rules'),'--project_id','demo-ht-english-library','--single_project_mode','true'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
try:
    deadline=time.monotonic()+30
    while True:
        if process.poll() is not None:raise RuntimeError('Firestore failed to start; inspect '+str(CACHE/'firestore-standalone.log'))
        with socket.socket() as probe:
            if probe.connect_ex(('127.0.0.1',8080))==0:break
        if time.monotonic()>deadline:raise RuntimeError('Firestore startup timed out.')
        time.sleep(.2)
    command='npm run test:rules && python3 tests/auth-browser.py'
    result=subprocess.run([str(ROOT/'node_modules/.bin/firebase'),'emulators:exec','--project','demo-ht-english-library','--only','auth',command],cwd=ROOT,env=env)
finally:
    process.terminate()
    try:process.wait(timeout=15)
    except subprocess.TimeoutExpired:process.kill();process.wait()
    log.close()
raise SystemExit(result.returncode)
