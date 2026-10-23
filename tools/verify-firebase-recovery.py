"""Read-only verification of the October 23 recovery against immutable Git objects."""
from pathlib import Path
import hashlib, json, subprocess

ROOT = Path(__file__).resolve().parents[1]
CURRENT_MAIN = 'ff64f80'
# Pinned SHA-256 of the trusted integration from 7cfca10; no orphaned-branch dependency.

def blob(commit, name):
    return subprocess.check_output(['git', 'show', commit + ':' + name], cwd=ROOT)

files = subprocess.check_output(['git', 'ls-tree', '-rz', '--name-only', CURRENT_MAIN], cwd=ROOT).decode().strip('\0').split('\0')
for name in files:
    if name != 'index.html':
        assert (ROOT / name).read_bytes() == blob(CURRENT_MAIN, name), 'Current main file changed: ' + name

trusted = {
    '.firebaserc': '4b52cfb9848639b070817710bc881bf7740a9999634f9c7f1681b6c2fccbff50',
    'firebase.json': '9a0fcb722e4cd60659be541aac80165ee58f3cabcd0b9acf475061533b5c841f',
    'firestore.rules': 'f55771af3838fcb78553ad1b4dbf6fe5e3e09148aee78387f3bd3e42e85e6ff7',
    'firestore.indexes.json': 'eed5043202a2d6a6c498b00feb7c57d844516429ec5eb2ee3de6c9c9ab322794',
    'assets/firebase-config.js': 'c8e1f1ab874a1fb9c487063a3601b2c5669e3382ef908b07469d49674cd9cf68',
    'assets/session.js': 'f7990759c6a13c03cd1132606259f9b5805e69b0470fc5d24745dbf03009f334',
    'assets/firebase-client.js': '6a4b75c5174dce06c51babbbe5ab78a098b196905baf18b83392e74a69003be0',
    'catalog/library-catalog.json': '0dae225f8839468ee138744343599707ecbcc5c99919f5ca901432c1981cbefd',
    'assets/catalog-integrity.js': '0510bcfa6a20ce046450a56fc9fee0b24b5c36ec98223f73ffae13cb3bd1d7e7',
}
for name, digest in trusted.items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, "Trusted Firebase integration changed: " + name

index = (ROOT / 'index.html').read_text()
assert 'const DATA =' not in index and 'id="login-form"' in index
assert 'id="library" hidden' in index and 'assets/library.js?v=' in index

game_dir = ROOT / 'grade-8/De_thi_GHK1/12_THCS_Truc_Hung'
game = json.loads((game_dir / 'practice-game-data.js').read_text().split('window.HT_PRACTICE_DATA = ', 1)[1].strip()[:-1])
assert [track['src'] for track in game['tracks']] == ['Part 1.mp3', 'Part 2.mp3']
assert hashlib.sha256((game_dir / game['exam']['sourceHtml']).read_bytes()).hexdigest() == game['exam']['sourceSha256']
print(f'PASS {len(files)-1} current-main files byte-identical, including all exams, audio and the restored Truc Hung game; only index reconnected. Firebase project/config/Rules/Admin logic and legacy catalog preserved; production not contacted.')
