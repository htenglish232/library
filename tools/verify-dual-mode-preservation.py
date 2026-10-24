"""The Stage 1 branch is additive: no baseline file may change, including index/Firebase."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
BASELINE='544777a'
paths=subprocess.check_output(['git','ls-tree','-rz','--name-only',BASELINE],cwd=ROOT).decode().strip('\0').split('\0')
for name in paths:
    original=subprocess.check_output(['git','show',BASELINE+':'+name],cwd=ROOT)
    assert (ROOT/name).read_bytes()==original,'Existing file changed: '+name
print('PASS',len(paths),'baseline files byte-identical, including all exams/MP3s/old games, pilots, index/catalog/Firebase/Admin and other grades. Stage 1 adds files only.')
