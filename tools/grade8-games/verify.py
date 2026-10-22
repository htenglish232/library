"""Verify originals, raw answer parity and deterministic pilot generation. No game writes."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess
ROOT=Path(__file__).resolve().parents[2]
BASELINE='33f05fa'
def load(folder):
 p=ROOT/'grade-8/De_thi_GHK1'/folder/'practice-game-data.js'
 return json.loads(p.read_text().split('window.HT_PRACTICE_DATA = ',1)[1].strip()[:-1])
records=json.loads((ROOT/'docs/grade8-games/inventory.json').read_text())
protected={r['source']:r['sha256'] for r in records}
for r in records:
 for asset in r['resources']:protected[asset['path']]=asset['sha256']
for path,digest in protected.items():
 assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,('changed original',path)
 blob=subprocess.check_output(['git','show',BASELINE+':'+path],cwd=ROOT)
 assert hashlib.sha256(blob).hexdigest()==digest,('not original baseline bytes',path)
for path in ['assets/catalog-data.js','firestore.rules','assets/firebase-config.js','grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-game-test.html','grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-game/game.js','grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-game/game.css']:
 assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show',BASELINE+':'+path],cwd=ROOT),('protected application file changed',path)
raw=json.loads(Path('/tmp/ht-grade8-source-scan.json').read_text())
folders=['11_THCS_Truc_Khang','12_THCS_Truc_Hung','19_THCS_Truc_Chinh']
for folder in folders:
 data=load(folder);entry=next(v for k,v in raw.items() if k.split('/')[2]==folder);objects=entry['objects']
 if folder.startswith('11_'):
  expected={**objects['EXAM_ANSWERS'],**{'arrange'+k:v for k,v in objects['rearrangeData'].items()}}
 elif folder.startswith('12_'):expected=objects['answersData']
 else:expected={item['id']:item for items in objects['testData'].values() if isinstance(items,list) for item in items}
 assert set(expected)=={q['id'] for q in data['questions']},('missing or duplicate source IDs',folder)
 assert len(data['questions'])==len(expected)
 for q in data['questions']:
  assert q['sourceRaw']==expected[q['id']],('source answer/explanation changed',q['id'])
  assert q['promptHtml']==data['sourceSnapshot']['questions'][q['id']]['promptHtml']
  assert q['options']==data['sourceSnapshot']['questions'][q['id']]['options']
  if q['kind']=='choice':assert q['sourceRaw']['correct'] in {o['value'] for o in q['options']}
  if q['kind']=='multi-text':assert q['acceptedTuples'][0]==q['sourceRaw']['correct'] and q['inputCount']==len(q['sourceRaw']['correct'])
  if q.get('track'):assert any(t['id']==q['track'] and t['transcriptHtml'] for t in data['tracks'])
  if 'context' in q:assert data['contexts'][q['context']]
 if folder.startswith('12_'):
  for q in data['questions']:
   if q['kind']=='rearrange':assert q['tokens']==[c['text'] for c in objects['rearrangeData'][q['id']]['poolChunks']]
 assert len(data['sourceSnapshot']['images'])==len(entry['dom']['images'])
 print('PASS',folder,'all',len(expected),'source IDs, original answers, explanations, options, contexts, transcript/image mappings',flush=True)
subprocess.run([__import__('sys').executable,str(Path(__file__).with_name('convert.py')),'--verify'],cwd=ROOT,check=True)
print('PASS',len(protected),'original HTML/audio/image files byte-identical; Firebase config/Rules/reference game unchanged; exactly 3 pilots regenerated identically without writes. Index/catalog release additions are checked by tools/check-catalog.mjs.')
