"""Scan all original Grade 8 exams without executing source JavaScript or creating games."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
EXAMS=ROOT/'grade-8/De_thi_GHK1'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def count_evidence(file,objects):
 number=int(file.parent.name.split('_')[0])
 stores={1:'masterData',2:'EXAM_KEY',3:'testDatabase',4:'masterExplanations',5:'EXAM_KEYS',8:'questionsConfig',11:'EXAM_ANSWERS',12:'answersData',14:'pedagogicalExplanations',16:'masterKeys',17:'answerKey',18:'answerKey',20:'EXAM_DATA'}
 if number in stores:
  name=stores[number];count=len(objects[name]);evidence=name
  if number in [11,18]:count+=len(objects['rearrangeData']);evidence+=' + rearrangeData'
  return count,evidence
 if number==7:
  names=['listeningData1','listeningData2','langFocusData','verbFormData','clozeData','readingCompDataA','readingCompDataB','rearrangeData','rewriteData']
  return sum(len(objects[n]) for n in names),'sum of 9 distinct source part arrays'
 if number==9:return sum(len(v) for v in objects['EXAM_DATA'].values()),'sum of 10 EXAM_DATA parts (including one pronunciation question)'
 if number==19:return sum(len(v) for v in objects['testData'].values() if isinstance(v,list)),'sum of 9 testData arrays; one question has two fields'
 if number==6:return 37,'countAnswered() explicitly totals 6+5+10+3+5+2+3+3=37; no rewriting section'
 if number==10:return 42,'29 radio groups + 10 text questions + 3 rearrangeData records; grading code is procedural'
 if number==13:return 42,'18 radio groups + 21 text questions + 3 rearrangeQuestions records'
 return None,'requires an explicit source adapter'
def originals():
 return sorted((p for d in EXAMS.iterdir() if d.is_dir() and d.name.split('_')[0].isdigit() for p in d.glob('*.html') if 'game' not in p.name.lower()),key=lambda p:(int(p.parent.name.split('_')[0]),p.name))
def scan():
 records=[];raw={}
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'),args=['--no-sandbox'])
  page=browser.new_page()
  for file in originals():
   source=file.read_text()
   dom=page.evaluate('''source=>{
    const doc=new DOMParser().parseFromString(source,'text/html');
    return {title:doc.title,headings:[...doc.querySelectorAll('h1,h2,h3,h4')].map(n=>n.textContent.trim()),
     scripts:[...doc.querySelectorAll('script:not([src])')].map(n=>n.textContent),
     controls:[...doc.querySelectorAll('input:not([type=range]):not([type=checkbox]),textarea,select')].filter(n=>n.name||n.id).map(n=>({id:n.id,name:n.name,type:n.type,value:n.value})),
     cards:[...doc.querySelectorAll('.question-card,[data-q],[data-qid]')].map(n=>({id:n.id,key:n.getAttribute('data-q')||n.getAttribute('data-qid')})),
     images:[...doc.querySelectorAll('img')].map(n=>({src:n.getAttribute('src'),alt:n.alt})),
     audio:[...doc.querySelectorAll('audio[src],audio source[src]')].map(n=>n.getAttribute('src'))};
   }''',source)
   objects=json.loads(subprocess.check_output(['node',str(Path(__file__).with_name('literals.mjs'))],input=json.dumps(dom.pop('scripts')),text=True))
   key=str(file.relative_to(ROOT));raw[key]={'dom':dom,'objects':objects}
   def answer_records(obj,prefix=''):
    found=[]
    if isinstance(obj,dict):
     if any(k in obj for k in ['correct','correctKeywords','correctPhrases','suggested','correctString','answer','targetOrders']):found.append(prefix)
     else:
      for k,v in obj.items():found+=answer_records(v,prefix+'.'+str(k))
    elif isinstance(obj,list):
     for i,v in enumerate(obj):found+=answer_records(v,prefix+'.'+str(i))
    return found
   stores={name:answer_records(value) for name,value in objects.items() if answer_records(value)}
   resources=[{'path':str(x.relative_to(ROOT)),'sha256':digest(x),'bytes':x.stat().st_size} for x in sorted(file.parent.iterdir()) if x.suffix.lower() in ['.mp3','.wav','.wma','.png','.jpg','.jpeg','.svg','.webp']]
   count,evidence=count_evidence(file,objects)
   content=(source+' '+' '.join(dom['headings'])).lower()
   types=[name for name,pattern in [('listening',r'listen'),('pronunciation',r'pronounc|underlined'),('stress',r'stress pattern|stressed syllable'),('grammar',r'grammar|language focus'),('reading',r'read(?:ing| the| and)'),('true-false',r'true.{0,20}false'),('verb-forms',r'verb.{0,25}form|form.{0,25}verb'),('rearrangement',r'rearrang|correct order|arrange these'),('rewriting',r'rewrite|second sentence')] if re.search(pattern,content)]
   records.append({'source':key,'sha256':digest(file),'title':dom['title'],'headings':dom['headings'],
    'detectedQuestionCount':count,'countEvidence':evidence,'countValidation':'source analysis only; browser parity verified only for selected pilots',
    'detectedForms':types,'physicalAudioFiles':len([r for r in resources if Path(r['path']).suffix.lower() in ['.mp3','.wav','.wma']]),
    'questionCards':len(dom['cards']),'answerStores':{k:len(v) for k,v in stores.items()},'answerRecordIds':stores,
    'audioReferences':dom['audio'],'images':dom['images'],'resources':resources,
    'staticObjectNames':list(objects),'status':'scanned-only; not converted'})
  browser.close()
 hashes={}
 for rec in records:
  if rec['sha256'] in hashes:rec['duplicateOf']=hashes[rec['sha256']]
  else:hashes[rec['sha256']]=rec['source']
 return records,raw
if __name__=='__main__':
 records,raw=scan()
 output=ROOT/'docs/grade8-games/inventory.json';output.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
 cache=Path(os.environ.get('GRADE8_SCAN_CACHE','/tmp/ht-grade8-source-scan.json'));cache.write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n')
 print(f'Scanned {len(records)} original HTML files; {len({r["sha256"] for r in records})} distinct contents. No games generated. Raw scan: {cache}')
