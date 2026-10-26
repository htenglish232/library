"""Source-only Grade 6 adapters, sharing the unchanged Grade 8 runtime.

No original app executes. Raw JS literals are parsed by the existing Acorn tool;
static HTML is read by DOMParser. Generation fails for unmapped source controls.
"""
from pathlib import Path
from urllib.parse import quote,unquote
import argparse,copy,hashlib,html,importlib.util,json,re,subprocess
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'grade-6/De_thi_GHK_1';DOC=ROOT/'docs/grade6-dual-mode'
spec=importlib.util.spec_from_file_location('g8',ROOT/'tools/build-grade8-dual-games.py');g8=importlib.util.module_from_spec(spec);spec.loader.exec_module(g8)
sha=lambda b:hashlib.sha256(b).hexdigest()
DYNAMIC={
5:['listeningPart1Data','listeningPart2Data','languagePart1Data','languagePart2Data','languagePart3Data','readingPart1Data','readingPart2AData','readingPart2BData','writingPart1Data','writingPart2Data'],
14:['listeningPart1','listeningPart2','langPart1','langPart2','langPart3','readingPart1','readingPart2','writingPart1','writingPart2'],
15:['task1Data','task2Data','languageMcqData','verbFormData','clozeData','robertMcqData','robertTfData','writingRearrangeData','writingTransformData'],
16:['taskA1Data','taskA2Data','taskB1Data','taskB2Data','taskC1Data','taskC2AData','taskC2BData','taskD1Data','taskD2Data']}
CONTAINERS={5:['listListeningPart1','listListeningPart2','listLanguagePart1','listLanguagePart2','listLanguagePart3','listReadingPart1','listReadingPart2A','listReadingPart2B','listWritingPart1','listWritingPart2'],14:[k+'Container' for k in DYNAMIC[14]],15:['task1QuestionsContainer','task2QuestionsContainer','languageMcqContainer','verbFormContainer','clozeQuestionsContainer','robertQuestionsContainer','robertTfContainer','writingRearrangeContainer','writingTransformContainer'],16:['taskA1-questions','taskA2-questions','taskB1-questions','taskB2-questions','taskC1-questions','taskC2A-questions','taskC2B-questions','taskD1-questions','taskD2-questions']}
KEYS={1:'explanations',2:'ANSWER_KEY',3:'examAnswerKey',4:'questionBank',6:'EXAM_KEY',7:'answerKeys',8:'answerKeys',9:'EXAM_DATA',10:'questionsDB',11:'explanations',12:'explanations',13:'EXAM_ANSWERS'}
WRITING={1:'writingData',3:'wordBankData',4:'puzzleData',6:'WRITING_DATA',7:'writingData',8:'writingData',9:'WORD_CHIP_DATA',10:'wordChipData',13:'WRITING_POOLS'}
def literals(path):return g8.literals(path)['variables']
def rows():
 snapshot=json.loads((DOC/'source-inventory.json').read_text())['rows'];actual={p.relative_to(ROOT).as_posix() for p in BASE.rglob('*.html') if 'dual-mode' not in p.name}
 assert actual=={r['source'] for r in snapshot},'Source inventory changed; review inventory before generating'
 return snapshot

def answer_values(raw):
 for k in ['accepted','validAnswers','validOptions']:
  if isinstance(raw.get(k),list):return raw[k]
 out=[]
 for k in ['correct','ans','answer','key','correctAnswer','correctSentence','target','altTarget','alt','altSentence','targetAlt','alternateTarget']:
  value=raw.get(k)
  if isinstance(value,str):out.append(value)
 return list(dict.fromkeys(out))
def tokens(raw):
 if isinstance(raw,list):return raw
 for key in ['tokens','pool','chips','initialBank','scrambled','shuffledWords']:
  if isinstance(raw.get(key),list):return raw[key]
 return []
def question(raw,r,section,number,word_data=None):
 accepted=answer_values(raw);flags=[];evidence=[{'kind':'literal','value':copy.deepcopy(raw)}]
 for k in ['data-correct','data-answer','data-key','data-target']:
  if r.get('attrs',{}).get(k):
   value=r['attrs'][k];evidence.append({'kind':'html-attribute','name':k,'value':value})
   if accepted and value not in accepted:flags.append('Đáp án thuộc tính HTML không khớp đáp án JavaScript nguồn; cần giáo viên duyệt.')
   if not accepted:accepted=[value]
 if 'data-valid' in r.get('attrs',{}):
  try:accepted=json.loads(r['attrs']['data-valid'])
  except ValueError:flags.append('Thuộc tính data-valid của nguồn bị lỗi dấu nháy; không tự phục hồi/suy đoán đáp án, cần giáo viên kiểm tra.')
  evidence.append({'kind':'html-attribute','name':'data-valid','value':r['attrs']['data-valid']})
 opts=r['options'];ts=tokens(word_data) if word_data is not None else r.get('tokens',[])
 kind='choice' if opts else 'rearrange' if ts else 'text'
 if kind=='choice':accepted=[x for x in accepted if x in [o['value'] for o in opts]]
 if not accepted:flags.append('Chưa có đáp án đầy đủ hợp lệ trong nguồn; cần giáo viên kiểm tra.')
 if kind=='rearrange' and not g8.realizable(ts,accepted):
  # Preserve both tiles and complete source answers; do not invent prefix tiles.
  flags.append('Thẻ từ nguồn không tạo được toàn bộ câu đáp án (có thể có tiền tố cố định); giữ nguyên dữ liệu và chuyển giáo viên kiểm tra.')
 if any(raw.get(k) for k in ['keywords','keyword']):flags.append('Nguồn chấm theo từ khóa, chưa có quy tắc đáp án đầy đủ được xác minh; cần giáo viên kiểm tra.')
 item=dict(id=r['id'],number=number,sourceNumber=r['id'],section=section,kind=kind,promptHtml=r['promptHtml'],options=opts,accepted=accepted,autoGrade=bool(accepted) and not flags,sourceRaw=raw,answerEvidence=evidence,answerLabel=raw.get('correctText') if kind!='choice' else None,explainHtml=raw.get('explain') or raw.get('explanation') or raw.get('exp') or raw.get('why') or raw.get('reason') or raw.get('rule') or '',knowledge=raw.get('grammar') or raw.get('vocab') or '',teacherFlags=flags)
 item['answerLabel']=item['answerLabel'] or ' / '.join(accepted) or 'Cần giáo viên kiểm tra — xem đề gốc.'
 if ts:item['tokens']=ts
 return item

def build(row,page):
 path=ROOT/row['source'];source=path.read_text();assert sha(path.read_bytes())==row['sourceSha256'];v=literals(path);n=row['folder'];questions=[];sections=[];contexts=[]
 def section(title,description=''):
  sid='part-'+str(len(sections)+1);sections.append(dict(id=sid,title=title,description=description or title,icon='🎧' if 'Listen' in title else '📖' if 'Reading' in title else '🧩' if 'Writing' in title else '⚡'));return sid
 if n in DYNAMIC:
  # Literal arrays follow the exact calls/sections of the source renderers.
  static=page.evaluate('''({source,containers})=>{const d=new DOMParser().parseFromString(source,'text/html');return containers.map(id=>{const container=d.getElementById(id);if(!container)throw Error('Missing dynamic source container '+id);let e=container.closest('section');if(!e){e=container.parentElement;while(e.parentElement&&!e.querySelector('h2,h3,h4')&&!['MAIN','BODY'].includes(e.parentElement.tagName))e=e.parentElement;}const copy=e.cloneNode(true);copy.querySelectorAll('script,style,button,svg,audio,.ht-audio-player,[id*=transcript i],input').forEach(n=>n.remove());copy.querySelectorAll('[class*=underline]').forEach(n=>{const u=d.createElement('u');u.innerHTML=n.innerHTML;n.replaceWith(u);});for(const n of [copy,...copy.querySelectorAll('*')])for(const a of [...n.attributes])n.removeAttribute(a.name);return copy.innerHTML;});}''',dict(source=source,containers=CONTAINERS[n]))
  for i,key in enumerate(DYNAMIC[n]):
   values=v[key];is_writing=any(s in key.lower() for s in ['writing','taskd']);is_reading=any(s in key.lower() for s in ['reading','cloze','robert','taskc'])
   title=('Listening Challenge · Phần '+str(i+1) if i<2 else 'Writing Challenge · '+('Viết lại câu' if i==len(DYNAMIC[n])-1 else 'Sắp xếp câu') if is_writing else 'Reading Quest · '+str(i-4) if is_reading else 'Pronunciation Challenge' if n in [5,14] and i==2 else 'Vocabulary & Grammar Battle' if i==2 or n in [5,14] and i==3 else 'Verb Forms')
   sid=section(title);context=static[i]
   for raw in values:
    opts=[dict(value=o.get('val',o.get('key')),html=o.get('text','')) for o in raw.get('options',[])]
    if not opts and not is_writing:opts=[dict(value='T',html='True (T)'),dict(value='F',html='False (F)')]
    # Original templates interpolate these fields as HTML; preserve u/b markup.
    prompt=raw.get('q') or raw.get('qText') or raw.get('question') or raw.get('text') or raw.get('prompt') or raw.get('original') or raw.get('root') or ''
    if raw.get('displayWord'):prompt+='<p>'+raw['displayWord']+'</p>'
    if raw.get('prefix'):prompt+='<p>'+html.escape(raw['prefix'])+' ______</p>'
    if not prompt and is_writing:prompt='Sắp xếp các thẻ từ theo đề gốc.'
    r=dict(id=raw['id'],promptHtml='<div>'+prompt+'</div>',options=opts)
    wd=copy.deepcopy(raw) if is_writing else None
    # Prefix pieces are SOURCE data, not invented answers: represent as text
    # input rather than silently adding missing tiles to the original word bank.
    fixed_prefix=re.sub(r'^[→➜\s]+','',raw.get('prefix',''))
    if is_writing and fixed_prefix and g8.realizable([fixed_prefix]+tokens(raw),answer_values(raw)):
     # The runtime has no fixed-prefix tile UI. Keep the original source words
     # as hints and use its supported full-sentence input with verified answers.
     r['promptHtml']+='<p>Từ gợi ý: '+html.escape(' / '.join(tokens(raw)))+'</p><p>Viết cả câu hoàn chỉnh, gồm phần đầu đã cho.</p>'
     wd=None
    item=question(raw,r,sid,len(questions)+1,wd)
    if is_writing:item['sourceTokens']=tokens(raw)
    if context:item['contextHtml']=context
    if i<2:item['listeningPart']=i+1
    questions.append(item)
 else:
  answers=copy.deepcopy(v[KEYS[n]]);word_data=v.get(WRITING.get(n,''),{})
  for k,raw in word_data.items():
   if k not in answers:answers[k]=copy.deepcopy(raw) if isinstance(raw,dict) else {}
   elif isinstance(raw,dict):answers[k]={**answers[k],**{k2:raw[k2] for k2 in ['target','altTarget','alt'] if k2 in raw}}
  if n==10:
   for k,variants in v['writingValidOptions'].items():answers[k]['validAnswers']=variants;answers[k]['exp']=v['writingExplanations'][k]
  extracted=page.evaluate((ROOT/'tools/grade6-source-dom.js').read_text(),dict(source=source,specs=[dict(id=k) for k in answers]))
  extracted.sort(key=lambda x:x['sourcePosition']);assert len({x['sourcePosition'] for x in extracted})==len(answers)
  last_title=None;listening_count=0
  for r in extracted:
   heading=r['heading'];sub=r['subheading'];title=heading+' · '+sub
   if title!=last_title:sid=section(sub or heading or 'Theo đề gốc',heading);last_title=title
   raw=answers[r['id']];wd=word_data.get(r['id']);prefix=raw.get('targetPrefix','')
   source_tiles=tokens(wd) if wd is not None else r.get('tokens',[])
   if prefix and source_tiles and g8.realizable([prefix]+source_tiles,answer_values(raw)):
    r['promptHtml']+='<p>Từ gợi ý: '+html.escape(' / '.join(source_tiles))+'</p><p>Viết cả câu hoàn chỉnh, gồm phần đầu đã cho.</p>'
    r['tokens']=[];wd=None
   item=question(raw,r,sid,len(questions)+1,wd)
   if source_tiles:item['sourceTokens']=source_tiles
   item['sourcePosition']=r['sourcePosition']
   if r['contextHtml']:item['contextHtml']=r['contextHtml']
   if re.search(r'LISTENING',heading,re.I):listening_count+=1;item['listeningPart']=1 if listening_count<=6 else 2
   questions.append(item)
 assert len(questions)==row['questions'],(n,len(questions),row['questions'])
 # Never reconstruct absent pronunciation underline formatting from the key.
 for q in questions:
  if re.search(r'underlined|gạch chân',q['promptHtml'],re.I) and not re.search(r'<u[ >]',q['promptHtml']+''.join(o['html'] for o in q['options']),re.I):
   q['teacherFlags'].append('Nguồn không đánh dấu rõ phần gạch chân trong câu/phương án; không tự suy đoán, cần giáo viên kiểm tra.')
   q['autoGrade']=False
 # Use actual source part boundaries (some exams have 4+5 or 5+4 Listening
 # questions). Only a single combined source section uses the 6+6 fallback.
 if n not in DYNAMIC:
  listening_sections=list(dict.fromkeys(q['section'] for q in questions if 'listeningPart' in q))
  if len(listening_sections)==2:
   for q in questions:
    if 'listeningPart' in q:q['listeningPart']=listening_sections.index(q['section'])+1
 # Only use audio links already approved in the original HTML. AUDIO_REPORT.md
 # identifies the unused/mismatched files; never attach them just by filename.
 audio=page.evaluate('''s=>{const d=new DOMParser().parseFromString(s,'text/html');return [...d.querySelectorAll('audio[src]')].filter(e=>e.getAttribute('src')).map(e=>({id:e.id,src:e.getAttribute('src')}));}''',source)
 tracks=[]
 for a in audio:
  src=html.unescape(a['src']);file=path.parent/unquote(src);assert file.is_file();part=2 if a['id'].endswith('-2') else 1;whole=a['id'].endswith('-0');tid='listen-'+str(part)
  tracks.append(dict(id=tid,title='Listening · '+('Toàn bộ bài nghe' if whole else 'Phần '+str(part)),src=src,wholeFile=whole,sha256=sha(file.read_bytes())))
 for q in questions:
  if 'listeningPart' not in q:continue
  part=q['listeningPart'];track=next((t for t in tracks if t['wholeFile'] or t['id']=='listen-'+str(part)),None)
  if track:q['track']=track['id']
  else:q['contextHtml']='<p><strong>Nguồn nghe phần này chưa có file được xác nhận. Mở đề gốc để dùng cách nghe hiện có; cần giáo viên kiểm tra audio.</strong></p>'+q.get('contextHtml','')
 # Keep original transcript markup only; never synthesize a transcript from keys.
 transcripts=page.evaluate('''s=>{const d=new DOMParser().parseFromString(s,'text/html');return [...d.querySelectorAll('[id*=transcript i]')].filter(e=>e.textContent.length>100&&!e.querySelector('[id*=transcript i]')).map(e=>{const c=e.cloneNode(true);c.querySelectorAll('script,button,svg').forEach(n=>n.remove());for(const n of [c,...c.querySelectorAll('*')])for(const a of [...n.attributes])n.removeAttribute(a.name);return c.innerHTML;});}''',source)
 if n==1:
  # This source builds transcripts at runtime from literal sentences. Preserve
  # those exact sentences too; no original application needs to execute.
  transcripts=[''.join('<p>'+html.escape(line)+'</p>' for line in v['listeningTracks'][key]['sentences']) for key in ['task1','task2']]
 for q in questions:
  if 'listeningPart' in q and len(transcripts)>=q['listeningPart']:q['transcriptHtml']=transcripts[q['listeningPart']-1]
 data=dict(schemaVersion=1,exam=dict(id='grade6-ghk1-source-'+str(n),grade=6,school=row['school'],number=row['number'],title=f'Đề số {row["number"]} · Giữa học kỳ I · Tiếng Anh 6',sourceHtml=path.name,sourceBaseline='7407b43',sourceSha256=row['sourceSha256']),questions=questions,sections=sections,contexts=contexts,tracks=tracks)
 return g8.finish(data)
def main():
 p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');args=p.parse_args();inventory=[]
 template=(ROOT/'grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-dual-mode.html').read_text()
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page()
  for row in rows():
   data=build(row,page);folder=(ROOT/row['source']).parent
   g8.emit(folder/'practice-dual-data.js','// Generated from original HTML by tools/build-grade6-dual-games.py.\nwindow.HT_PRACTICE_DATA = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n',args.verify)
   launcher=template.replace('../shared-practice/','../../../grade-8/De_thi_GHK1/shared-practice/').replace('THCS Trực Tuấn',html.escape(row['school'])).replace('English Quest 8','English Quest 6').replace('GRADE 8','GRADE 6').replace('dual-mode-engine.js?v=20261026-sound-fix','dual-mode-engine.js?v=20261026-grade6').replace('TIẾNG ANH LỚP 8','TIẾNG ANH LỚP 6').replace('Quest <b>8</b>','Quest <b>6</b>').replace('truc-tuan-dual-data.js','practice-dual-data.js').replace('  <script defer src="truc-tuan-dual-support.js"></script>\n','').replace('1.%20THCS%20Truc%20Tuan.html',quote(Path(row['source']).name)).replace('42',str(len(data['questions'])))
   g8.emit(folder/'practice-dual-mode.html',launcher,args.verify)
   entry={**row,'game':(folder/'practice-dual-mode.html').relative_to(ROOT).as_posix(),'autoGrade':sum(q['autoGrade'] for q in data['questions']),'maxXP':data['maxXP'],'tracks':data['tracks'],'missingAudioParts':sorted(set(q['listeningPart'] for q in data['questions'] if 'listeningPart' in q and not q.get('track'))),'issues':data['issues']};inventory.append(entry)
   print('PASS',row['folder'],row['school'],len(data['questions']),'questions',data['maxXP'],'XP',len(data['tracks']),'approved tracks',flush=True)
  b.close()
 g8.emit(DOC/'inventory.json',json.dumps(dict(baseline='7407b43',games=inventory),ensure_ascii=False,indent=2)+'\n',args.verify)
if __name__=='__main__':main()
