"""Reproducible source adapters. Run --group pilots, then remaining, then --verify.

Parses all original HTML and isolated JS literals, never runs original applications.
No source exam, legacy game, MP3, Firebase or progress record is overwritten.
Requires Node/acorn and Python Playwright/Chromium.
"""
from pathlib import Path
import argparse, copy, hashlib, html, json, re, subprocess
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'grade-8/De_thi_GHK1'
sha=lambda b:hashlib.sha256(b).hexdigest()
load_js=lambda p:json.loads(p.read_text().split('window.HT_PRACTICE_DATA = ',1)[1].strip()[:-1])
PILOTS={11,12,19}

def literals(path):
 return json.loads(subprocess.check_output(['node','tools/grade8-source-literals.mjs',str(path)],cwd=ROOT))

def flat_objects(v):
 if isinstance(v,dict):
  yield v
  for item in v.values():yield from flat_objects(item)
 elif isinstance(v,list):
  for item in v:yield from flat_objects(item)

def rows():
 catalog=json.loads((ROOT/'catalog/current-library-catalog.json').read_text())['data']
 lessons=next(u['lessons'] for g in catalog if g['grade']=='Grade 8' for u in g['units'] if u['name']=='Đề thi GHK1')
 counts={};out=[]
 for l in lessons:
  if not l['href'].startswith('grade-8/De_thi_GHK1/') or any(s in l['href'] for s in ['game','dual-mode']):continue
  school=l['title'].split(' · ')[-1];counts[school]=counts.get(school,0)+1
  out.append(dict(school=school,number=counts[school],href=l['href'],folder=int(Path(l['href']).parent.name.split('_')[0])))
 assert len(out)==19 and len(counts)==17
 disk={p.relative_to(ROOT).as_posix() for p in BASE.glob('*/*.html') if not any(s in p.name for s in ['game','dual'])}
 assert disk=={r['href'] for r in out},'Catalog/disk exam inventory mismatch'
 return out

def pilot(row,source,v):
 folder=(ROOT/row['href']).parent
 data=copy.deepcopy(load_js(folder/'practice-game-data.js'))
 objects=list(flat_objects(v))
 for q in data['questions']:
  assert q['sourceRaw'] in objects,('Pilot raw answer no longer matches source',row['school'],q['id'])
  assert q['promptHtml'] and q['id'] in data['sourceSnapshot']['questions']
  # A documented contradictory/ungradable source must never mint arbitrary XP.
  if not q['autoGrade'] or any(re.search(r'mâu thuẫn|không khớp|không thể|không có đáp án|thiếu.*(?:từ|dữ liệu)',f,re.I) for f in q['teacherFlags']):q['autoGrade']=False
 data['exam'].update(number=row['number'],school=row['school'],sourceSha256=sha(source.encode()),sourceBaseline='bcf44e9')
 for t in data['tracks']:t['sha256']=sha((folder/t['src']).read_bytes())
 return data

def specs_for(row,v,source,calls):
 n=row['folder'];a={};arr={};aliases={};anchors={}
 if n in {2,3,4,5,14,16,17,18,20}:
  key={2:'EXAM_KEY',3:'testDatabase',4:'masterExplanations',5:'EXAM_KEYS',14:'pedagogicalExplanations',16:'masterKeys',17:'answerKey',18:'answerKey',20:'EXAM_DATA'}[n]
  a=copy.deepcopy(v[key])
 elif n==8:
  for q in v['questionsConfig']:
   a[q['id']]=q;aliases[q['id']]=[q.get('name',''),q.get('inputId',''),q['id']]
 elif n==9:
  for part,items in v['EXAM_DATA'].items():
   for k,q in items.items():a['arrange'+k if part=='rearrange' else k]=q
 elif n==6:
  for key,prefix in [('tfKey','listening_tf_'),('lisMCKey','lis_mc_'),('vocabKey','b_mc_'),('verbKey','verb_'),('clozeKey','cloze_'),('readMCKey','read_mc_'),('readSAKey','read_sa_')]:
   for k,q in v[key].items():a[prefix+k]=q
  for k,q in v['rearrangeQuestions'].items():a['rearrange'+k]=q;arr['rearrange'+k]=q
 elif n==7:
  for key in ['listeningData1','listeningData2','langFocusData','verbFormData','clozeData','readingCompDataA','readingCompDataB','rearrangeData','rewriteData']:
   for q in v[key]:a[q['id']]=q
 elif n==13:
  for key,prefix in [('keyL1','q'),('keyL2','q'),('keyB1','b1_'),('keyB2','b2_'),('keyC1','c1_')]:
   for k,q in v[key].items():a[prefix+k]=q
  # The source grades C2 inline by keyword. Preserve complete source feedback,
  # but require teacher review rather than reusing permissive substring checks.
  for i in range(1,6):
   block=re.search(r'const c2_'+str(i)+r'_val[\s\S]*?(?=// Q|// 7\.)',source)
   labels=re.findall(r'<strong[^>]*>(.*?)</strong>',block[0] if block else '',re.S)
   a['c2_'+str(i)]={'sourceInline':block[0] if block else '', 'sample':' / '.join(labels)}
   if i in [4,5]:a['c2_'+str(i)]['ans']='F' # Explicit === "F" in both source blocks, asserted below.
   if i in [4,5]:assert f'c2_{i}_val === "F"' in source
  for q in v['keyRe']:a['rearrange'+str(q['id'])]=q
  for q in v['keyST']:a['st_'+str(q['id'])]=q
 elif n==10:
  for call in calls:
   args=call['args']
   if not args or not isinstance(args[0],str) or not args[0].startswith('card_'):continue
   k=args[0][5:];label=args[3];q={'display':label,'explain':args[4] if len(args)>4 and isinstance(args[4],str) else '', 'sourceInline':call['raw']}
   match=re.search(r"===\s*['\"]([^'\"]+)['\"]",call['raw'])
   if match:q['correct']=match[1]
   a[k]=q
  for k,q in v['rearrangeData'].items():a['D1_'+k]=q;arr['D1_'+k]=q
 else:raise ValueError(n)
 # Map native rearrangement tokens to the exact source question, never synthesize words.
 config=v.get('rearrangeData') or v.get('REARRANGE_DATA') or v.get('rearrangeConfig') or v.get('rearrangeQuestions') or v.get('arrangementState') or {}
 for k,q in a.items():
  if n==2 and k.startswith('q_rearrange_'):arr[k]=config[k.rsplit('_',1)[1]];anchors[k]=['rearrange-container-'+k.rsplit('_',1)[1]]
  if n==3 and k in config:arr[k]=config[k];anchors[k]=['card_'+k]
  if n==4 and k.startswith('d1_'):
   arr[k]={'tokens':next(c['args'][1] for c in calls if c['name']=='buildWordPool' and c['args'][0]==k)};anchors[k]=['card_'+k.upper()]
  if n==5 and k.startswith('D_I_'):arr[k]=config[k.rsplit('_',1)[1]];anchors[k]=['card_'+k,'rearrange_'+k,'q_'+k]
  if n==6 and k.startswith('rearrange'):anchors[k]=['q_rearr_'+k[-1]+'_box']
  if n==8 and q.get('type')=='rearrange':arr[k]=config[str(q['qNum'])];anchors[k]=['dropzone_'+str(q['qNum'])]
  if n==9 and k.startswith('arrange'):arr[k]=v['CHIP_POOLS'][k[-1]];anchors[k]=['q-block-rearrange-'+k[-1]]
  if n==10 and k.startswith('D1_'):anchors[k]=['card_'+k]
  if n==13 and k.startswith('rearrange'):
   arr[k]=next(x for x in config if str(x['id'])==k[-1]);anchors[k]=['rearrange-box-'+k[-1],'rearrange-container-'+k[-1],'qbox-re-'+k[-1]]
  if n==14 and k.startswith('W1_'):arr[k]=config[k];anchors[k]=['q_'+k,'container_'+k,'answerZone_'+k]
  if n==16 and q.get('type')=='rearrange':arr[k]=config[str(q['id'])];anchors[k]=['q-block-re'+str(q['id'])]
  if n==17 and re.fullmatch(r'W\d',k):arr[k]=config[k[-1]];anchors[k]=['q-container-'+k]
  if n==18:
   if k.startswith('WR2_'):pass
  if n==20 and q.get('type')=='rearrange':arr[k]=config[k];anchors[k]=['dropArea_'+k]
 # Trực Cường keeps arrangement answers outside answerKey.
 if n==18:
  for k,q in config.items():a['WR1_'+k]=q;arr['WR1_'+k]=q;anchors['WR1_'+k]=['q_WR1_'+k,'target_'+k,'arrange_'+k]
 specs=[]
 for k,q in a.items():
  al=aliases.get(k,[k,'q_'+k,'input_'+k,'inp_'+k])
  if n==17:al += [re.sub(r'([A-Z]+)(\d)',lambda m:m[1].lower()+'-'+m[2],k)]
  specs.append({'id':k,'aliases':[x for x in al if x], 'anchors':anchors.get(k,[])})
 return a,arr,specs

def values(q):
 if not isinstance(q,dict):return []
 # Only explicit whole answers/variants. Never treat keyword fragments as answers.
 keys=['accepted','acceptedPatterns','acceptedAnswers','correctAnswers','correctVariants','validAnswers','validEndings','acceptablePatterns','expectedVariants','answers','variants','validSequences']
 for key in keys:
  if isinstance(q.get(key),list) and all(isinstance(s,str) for s in q[key]):return q[key]
 for key in ['correct','ans','answer','key','correctText','expectedStr','expected','expectedString','correctString','correctSentence','targetSentence','rawExpected','expectedStr','target']:
  val=q.get(key)
  if isinstance(val,list) and all(isinstance(s,str) for s in val):return val
  if isinstance(val,str):return [val]
 if isinstance(q.get('validOrders'),list):return [' '.join(order) for order in q['validOrders']]
 for key in ['correctSequence','correctWords','correctOrder','correctSeq','answer','correctSeq1']:
  if isinstance(q.get(key),list):return [' '.join(q[key])]
 return []

def realizable(ts,accepted):
 def norm(s):return re.sub(r'\s+',' ',re.sub(r'[.,!?;:]','',s.lower().replace('’',"'").replace('‘',"'"))).strip()
 for target in accepted:
  failed=set()
  def solve(mask,left):
   if mask==(1<<len(ts))-1:return not left
   cache=(mask,tuple(left))
   if cache in failed:return False
   for i,t in enumerate(ts):
    part=norm(t).split()
    if not mask&(1<<i) and left[:len(part)]==part and solve(mask|(1<<i),left[len(part):]):return True
   failed.add(cache);return False
  if solve(0,norm(target).split()):return True
 return False

def tokens(q):
 if isinstance(q,list):return [s.get('text',s) if isinstance(s,dict) else s for s in q]
 for k in ['tokens','words','raw','rawPieces','pool','poolChunks','allWords','chunks','chips']:
  if isinstance(q.get(k),list):return [s.get('text',s) if isinstance(s,dict) else s for s in q[k]]
 return []

def build(row,page,dom):
 path=ROOT/row['href'];source=path.read_text();parsed=literals(path);v=parsed['variables'];n=row['folder']
 if n in PILOTS:return pilot(row,source,v)
 answers,arr,specs=specs_for(row,v,source,parsed['calls'])
 if n==7:return dynamic_my(row,source,v,page)
 extracted=page.evaluate(dom,{'source':source,'specs':specs})
 errors=[r for r in extracted if 'error' in r]
 if errors:raise AssertionError((path.parent.name,errors))
 # Source DOM order determines global numbering; original local numbers/IDs stay in prompt.
 extracted.sort(key=lambda q:q['sourcePosition'])
 assert len({q['sourcePosition'] for q in extracted})==len(extracted),('Shared source question container',n)
 questions=[];sections=[];contexts=[]
 for i,r in enumerate(extracted):
  q=answers[r['id']];opts=r['options'];kind='rearrange' if r['id'] in arr else 'choice' if opts else 'text'
  accepted=values(q);flags=[]
  if kind=='rearrange':
   ts=tokens(arr[r['id']]);assert ts,('No source word tiles',n,r['id'])
   if not accepted:accepted=values(arr[r['id']])
  if kind=='choice':
   accepted=[s if s in [o['value'] for o in opts] else (re.match(r'^([A-DTF])\b',s).group(1) if re.match(r'^([A-DTF])\b',s) else s) for s in accepted]
   accepted=[s for s in accepted if s in [o['value'] for o in opts]]
  if 'keywords' in q:
   flags.append('Nguồn chấm bằng từ khóa; cần giáo viên duyệt đáp án đầy đủ. Không tự chấm hoặc cộng XP từ từ khóa.')
  if not accepted:flags.append('Nguồn chưa cung cấp đáp án đầy đủ có thể đối chiếu tự động; cần giáo viên duyệt.')
  # Variants written as slash/parenthetical alternatives are preserved verbatim,
  # never expanded into invented accepted strings.
  if any(re.search(r'\bhoặc\b| / |\([^)]*\)',s) for s in accepted) and kind!='choice':flags.append('Đáp án nguồn có ghi chú/biến thể chưa tách rõ; cần giáo viên duyệt.')
  sectionId='section-'+str(len(sections)+1)
  title=r['subheading'] or r['heading'] or 'Luyện theo đề gốc'
  if sections and sections[-1]['sourceTitle']==title:sectionId=sections[-1]['id']
  else:
   heading=r['heading'];icon='🎧' if 'LISTEN' in heading.upper() else '🧭' if 'READ' in heading.upper() else '🧩' if 'WRIT' in heading.upper() else '⚡'
   sections.append({'id':sectionId,'title':title,'sourceTitle':title,'description':heading,'icon':icon})
  item={'id':r['id'],'number':i+1,'sourceNumber':re.sub('<[^>]+>',' ',r['promptHtml']).strip().split('.')[0][:35], 'section':sectionId,'kind':kind,'promptHtml':r['promptHtml'],'options':opts,'sourceRaw':q,'accepted':accepted,'autoGrade':bool(accepted) and not flags,'answerLabel':q.get('display') or q.get('sample') or q.get('standardAnswer') or q.get('standard') or q.get('target') or q.get('ans') or ' / '.join(accepted) or 'Cần giáo viên duyệt — xem đề gốc.','explainHtml':q.get('explain') or q.get('explanation') or q.get('expl') or q.get('exp') or q.get('detail') or q.get('rule') or '', 'knowledge':q.get('note',''),'teacherFlags':flags,'sourcePosition':r['sourcePosition'],'sourceAudioIndex':r['sourceAudioIndex']}
  if not isinstance(item['answerLabel'],str):item['answerLabel']=' / '.join(item['answerLabel'])
  if kind=='rearrange':
   item['tokens']=ts
   if not realizable(ts,accepted):item['autoGrade']=False;item['teacherFlags'].append('Các thẻ từ không khớp đáp án đầy đủ trong nguồn; cần giáo viên duyệt, không tự sửa từ hoặc đáp án.')
  if r['inputCount']>1:raise AssertionError(('Unmapped multi-input source',n,r['id'],r['inputCount']))
  if r['contextHtml']:
   if r['contextHtml'] not in contexts:contexts.append(r['contextHtml'])
   item['context']=contexts.index(r['contextHtml'])
  questions.append(item)
 data={'schemaVersion':1,'exam':{'id':'grade8-ghk1-source-'+str(n),'school':row['school'],'number':row['number'],'title':f'Đề số {row["number"]} · Giữa học kỳ I · Tiếng Anh 8','sourceHtml':path.name,'sourceSha256':sha(path.read_bytes()),'sourceBaseline':'bcf44e9'},'questions':questions,'sections':sections,'contexts':contexts,'tracks':[]}
 # Read exact MP3 references in source order; no fabricated audio for speech-only exams.
 mp3s=list(dict.fromkeys(re.findall(r'(?:src|data-src)=["\']([^"\']+\.mp3)["\']',source,re.I)))
 mp3s=[html.unescape(s) for s in mp3s]
 listening=[q for q in questions if 'LISTEN' in next(s['description'] for s in sections if s['id']==q['section']).upper()]
 for i,src in enumerate(mp3s):
  assert (path.parent/src).is_file(),src
  trackId='listen-'+str(i+1)
  transcriptHtml=transcript(source,v,page,i)
  if len(mp3s)==1:transcriptHtml+='\n'+transcript(source,v,page,1)
  data['tracks'].append({'id':trackId,'title':'Listening · Phần '+str(i+1),'src':src,'wholeFile':len(mp3s)==1,'transcriptHtml':transcriptHtml,'sha256':sha((path.parent/src).read_bytes())})
 for q in listening:
  if not mp3s:
   part=1 if (n==2 and q['id'].startswith('q_listen_mc_')) or (n==3 and q['id'].startswith('tf')) else 0
   q['transcriptHtml']=transcript(source,v,page,part)
  if mp3s:q['track']='listen-'+str(max(0,min(q['sourceAudioIndex'],len(mp3s)-1))+1)
 return data

def transcript(source,v,page,index):
 # Prefer literal transcript data. No transcript is fabricated when absent.
 candidates=[]
 for key in ['listeningScripts','LISTENING_DATA','AUDIO_CONTENT','audioScripts']:
  x=v.get(key)
  if isinstance(x,dict):candidates=list(x.values());break
 if not candidates:
  for pair in [('track1Script','track2Script'),('track1AudioDialogue','track2AudioDialogue')]:
   if pair[0] in v:candidates=[v[k] for k in pair];break
 if index<len(candidates):
  value=candidates[index]
  if isinstance(value,list):return ''.join('<p>'+html.escape((r.get('speaker','')+': ' if r.get('speaker') else '')+r.get('text',''))+'</p>' for r in value)
  if isinstance(value,str):return '<p>'+html.escape(value)+'</p>'
 return page.evaluate('''({source,index})=>{const d=new DOMParser().parseFromString(source,'text/html');let nodes=[...d.querySelectorAll('[id*="transcript" i]')].filter(n=>n.textContent.length>100&&!n.querySelector('[id*="transcript" i]'));return nodes[index]?.innerHTML||'';}''',{'source':source,'index':index})

def dynamic_my(row,source,v,page):
 # The original Trực Mỹ app constructs questions from these literal arrays.
 # Keep question/option markup directly from those arrays, preserving array order.
 parts=['listeningData1','listeningData2','langFocusData','verbFormData','clozeData','readingCompDataA','readingCompDataB','rearrangeData','rewriteData']
 sections=[];questions=[]
 for i,key in enumerate(parts):
  icon='🎧' if i<2 else '🧭' if 4<=i<=6 else '🧩' if i>=7 else '⚡'
  title=['Listening · Phần I','Listening · Phần II','Phonics & Grammar Battle','Verb Forms','Reading · Điền từ','Reading · Phần A','Reading · Phần B','Sentence Builder','Writing Challenge'][i]
  sections.append({'id':key,'title':title,'description':title,'icon':icon})
  for raw in v[key]:
   options=[{'value':o['key'],'html':o.get('displayText',o['text'])} for o in raw.get('options',[])]
   if i==0:options=[{'value':'T','html':'T (True)'},{'value':'F','html':'F (False)'}]
   kind='rearrange' if key=='rearrangeData' else 'choice' if options else 'text'
   accepted=values(raw);flags=[]
   if raw.get('keywords') or not accepted:flags=['Nguồn chấm bằng từ khóa hoặc chưa có đáp án đầy đủ; cần giáo viên duyệt, không cộng XP.']
   prompt='<p>'+html.escape(raw.get('statement') or raw.get('textPrompt') or raw.get('sentence') or raw.get('question') or raw.get('givenPrompt') or raw.get('given') or raw.get('prompt') or raw.get('gap') or '')+'</p>'
   if raw.get('title'):prompt='<p>'+html.escape(raw['title'])+'</p>'+prompt
   if raw.get('promptPrefix'):prompt+='<p>'+html.escape(raw['promptPrefix'])+' ______</p>'
   assert re.sub('<[^>]+>','',prompt).strip(),(row['school'],raw)
   q={'id':raw['id'],'number':len(questions)+1,'sourceNumber':raw['num'],'section':key,'kind':kind,'promptHtml':prompt,'options':options,'accepted':accepted,'autoGrade':bool(accepted) and not flags,'sourceRaw':raw,'answerLabel':raw.get('sample') or raw.get('standardFull') or ' / '.join(accepted) or 'Cần giáo viên duyệt — xem đề gốc.','explainHtml':raw.get('explain',''),'knowledge':'','teacherFlags':flags}
   if kind=='rearrange':
    q['tokens']=raw['tokens']
    if not realizable(q['tokens'],accepted):q['autoGrade']=False;q['teacherFlags'].append('Thẻ từ không khớp đáp án nguồn; cần giáo viên duyệt, không tự sửa từ.')
   questions.append(q)
 # Original paragraphs are static outside the dynamic question containers.
 reading=page.evaluate('''source=>{const d=new DOMParser().parseFromString(source,'text/html');const h=[...d.querySelectorAll('h3')].find(h=>h.textContent.includes('PART C: READING'));const section=h.closest('section').cloneNode(true);section.querySelectorAll('script,button,svg').forEach(n=>n.remove());for(const el of [section,...section.querySelectorAll('*')])for(const a of [...el.attributes])el.removeAttribute(a.name);return section.innerHTML;}''',source)
 assert 'school' in reading.lower(), 'Missing original reading passages'
 for q in questions:
  if q['section'] in parts[4:7]:q['contextHtml']=reading
 path=ROOT/row['href'];mp3s=list(dict.fromkeys(re.findall(r'(?:src|data-src)=["\']([^"\']+\.mp3)["\']',source,re.I)));tracks=[]
 for i,src in enumerate(mp3s):
  tracks.append({'id':'listen-'+str(i+1),'src':html.unescape(src),'wholeFile':False,'transcriptHtml':transcript(source,v,None,i),'sha256':sha((path.parent/html.unescape(src)).read_bytes())})
  for q in questions:
   if q['section']==parts[i]:q['track']=tracks[-1]['id']
 return {'schemaVersion':1,'exam':{'id':'grade8-ghk1-source-7','school':row['school'],'number':row['number'],'title':'Đề số 1 · Giữa học kỳ I · Tiếng Anh 8','sourceHtml':path.name,'sourceBaseline':'bcf44e9','sourceSha256':sha(path.read_bytes())},'sections':sections,'questions':questions,'contexts':[],'tracks':tracks}

def finish(data):
 core={k:data[k] for k in ['questions','sections','contexts','tracks']}
 data['contentVersion']=sha(json.dumps(core,ensure_ascii=False,separators=(',',':')).encode())
 data['issues']=[{'question':q['id'],'message':m} for q in data['questions'] for m in q['teacherFlags']]
 data['maxXP']=sum(q['autoGrade'] for q in data['questions'])*10
 return data

def emit(path,content,verify):
 if verify:assert path.read_text()==content,('Generated output differs from source',path)
 else:path.write_text(content)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--group',choices=['pilots','remaining','all'],default='all');parser.add_argument('--verify',action='store_true');args=parser.parse_args()
 dom=(ROOT/'tools/grade8-source-dom.js').read_text();template=(BASE/'1_THCS Truc Tuan/truc-tuan-dual-mode.html').read_text()
 inventory=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page()
  for row in rows():
   if row['folder']==1:continue
   if args.group=='pilots' and row['folder'] not in PILOTS:continue
   if args.group=='remaining' and row['folder'] in PILOTS:continue
   data=finish(build(row,page,dom));folder=(ROOT/row['href']).parent
   emit(folder/'practice-dual-data.js','// Generated from original exam by tools/build-grade8-dual-games.py.\nwindow.HT_PRACTICE_DATA = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n',args.verify)
   launcher=template.replace('THCS Trực Tuấn',row['school']).replace('truc-tuan-dual-data.js','practice-dual-data.js').replace('  <script defer src="truc-tuan-dual-support.js"></script>\n','').replace('1.%20THCS%20Truc%20Tuan.html',html.escape(Path(row['href']).name,quote=True)).replace('42',str(len(data['questions'])))
   if row['folder']==3:
    launcher=launcher.replace('content="width=device-width,initial-scale=1"','content="width=device-width,initial-scale=1,viewport-fit=cover,interactive-widget=resizes-content"').replace('<html lang="vi" data-practice="dual-mode">','<html lang="vi" data-practice="dual-mode" data-minimal-ui="trung-dong-1">').replace('</head>','  <link rel="stylesheet" href="minimal-ui.css?v=20261028">\n  <script defer src="minimal-ui.js?v=20261028"></script>\n</head>')
   emit(folder/'practice-dual-mode.html',launcher,args.verify)
   inventory.append({'school':row['school'],'examNumber':row['number'],'source':row['href'],'game':(folder/'practice-dual-mode.html').relative_to(ROOT).as_posix(),'questions':len(data['questions']),'autoGrade':sum(q['autoGrade'] for q in data['questions']),'maxXP':data['maxXP'],'tracks':[t['src'] for t in data['tracks']],'issues':data['issues'],'sourceSha256':data['exam']['sourceSha256']})
   print('PASS',row['school'],row['number'],len(data['questions']),'questions;',data['maxXP'],'XP;',len(data['tracks']),'audio')
  browser.close()
 if args.group=='all':
  tt=load_js(BASE/'1_THCS Truc Tuan/truc-tuan-dual-data.js');r=rows()[0]
  inventory.insert(0,{'school':r['school'],'examNumber':1,'source':r['href'],'game':'grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-dual-mode.html','questions':len(tt['questions']),'autoGrade':sum(q['autoGrade'] for q in tt['questions']),'maxXP':sum(q['autoGrade'] for q in tt['questions'])*10,'tracks':[t['src'] for t in tt['tracks']],'issues':tt['issues'],'sourceSha256':tt['exam']['sourceSha256']})
  path=ROOT/'docs/grade8-all-dual-mode';path.mkdir(exist_ok=True)
  emit(path/'inventory.json',json.dumps({'baseline':'bcf44e9','exams':19,'schools':17,'games':inventory},ensure_ascii=False,indent=2)+'\n',args.verify)
if __name__=='__main__':main()
