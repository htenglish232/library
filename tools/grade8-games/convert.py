"""Explicit source adapters for THREE reviewed pilots; no mass conversion switch.

Uses inventory cache, serves original exams on loopback, blocks external requests.
Outputs additive game HTML/data only. Unknown schemas raise errors.
"""
from pathlib import Path
import functools,hashlib,http.server,json,os,re,shutil,subprocess,threading
from urllib.parse import quote
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
BASELINE='33f05fa'  # Reviewed source; originals remain byte-identical.
PILOTS={
 'truc-khang':('11_THCS_Truc_Khang','11 THCS Truc Khang.html','THCS Trực Khang'),
 'truc-hung':('12_THCS_Truc_Hung','12 THCS Truc Hung.html','THCS Trực Hùng'),
 'truc-chinh':('19_THCS_Truc_Chinh','19 THCS Truc Chinh.html','THCS Trực Chính'),
}
SECTION_NAMES={
 'listen-1':'Listening · Phần I','listen-2':'Listening · Phần II',
 'language':'Vocabulary, Pronunciation & Grammar','verbs':'Verb Forms',
 'cloze':'Reading · Điền từ','reading':'Reading · Đọc hiểu',
 'arrange':'Sentence Builder','rewrite':'Sentence Rewriting',
}

DOM_EXTRACT=r'''({specs,starts,transcriptIds})=>{
 const clean=(node)=>{
  if(!node)throw Error('Source element missing');
  const copy=node.cloneNode(true);
  copy.querySelectorAll('button,script,style,.explanation-box,.feedback-box,.status-indicator,[hidden],.hidden').forEach(n=>n.remove());
  copy.querySelectorAll('input,textarea,select').forEach(n=>n.replaceWith(document.createTextNode(' ______ ')));
  for(const el of [copy,...copy.querySelectorAll('*')])for(const a of [...el.attributes])if(!['src','alt','colspan','rowspan'].includes(a.name))el.removeAttribute(a.name);
  return copy.tagName==='TABLE'?'<table>'+copy.innerHTML.trim()+'</table>':copy.innerHTML.trim();
 };
 const questions={};
 for(const spec of specs){
  let card=document.querySelector(spec.selector);
  if(!card)throw Error('Missing question '+spec.id+' '+spec.selector);
  const radio=[...card.querySelectorAll('input[type=radio]')];
  const opts=radio.map(input=>{const label=input.closest('label').cloneNode(true);label.querySelectorAll('input,button').forEach(n=>n.remove());return {value:input.value,html:clean(label)||input.value};});
  let prompt;
  if(spec.arrange)prompt=clean(card.firstElementChild);
  else if(radio.length){
   const copy=card.cloneNode(true);
   copy.querySelectorAll('label:has(input[type=radio])').forEach(n=>n.remove());
   prompt=clean(copy);
  }else prompt=clean(card);
  const heading=card.closest('section')?.querySelector('h3')?.textContent.trim()||'';
  questions[spec.id]={promptHtml:prompt,options:opts,sourceHeading:heading};
 }
 const contexts=starts.map(start=>{
  const node=[...document.querySelectorAll('p,div')].find(n=>n.textContent.trim().startsWith(start)&&!n.querySelector('input')&&n.textContent.trim().length<12000);
  if(!node)throw Error('Missing reading passage '+start);
  return clean(node.tagName==='P'?node.parentElement:node);
 });
 const transcripts=transcriptIds.map(id=>clean(document.getElementById(id)));
 const table=document.getElementById('blank1')?.closest('table');
 return {questions,contexts,transcripts,images:[...document.querySelectorAll('img')].map(n=>({src:n.getAttribute('src'),alt:n.alt})),table:table?clean(table):null,examHeadings:[...document.querySelectorAll('h1,h2')].map(n=>n.textContent.trim()),headings:[...document.querySelectorAll('h4')].map(n=>n.textContent.trim())};
}'''

def norm(value):return re.sub(r'\s+',' ',re.sub(r'[.,!?;:]','',value.lower().replace('’',"'"))).strip()
def html(value):
 import html as h
 return h.escape(str(value))

def source_specs(key,objects):
 specs=[]
 if key=='truc-khang':
  for qid in objects['EXAM_ANSWERS']:
   selector=f'[data-qid="{qid}"]'
   if qid.startswith('blank'):selector=f'#{qid}'
   if qid.startswith('RW'):selector=f'#rw_block_{qid[2:]}'
   specs.append({'id':qid,'selector':selector})
  # The six listening gaps use cells, not question cards.
  for spec in specs:
   if spec['id'].startswith('blank'):spec['selector']=f'td:has(#{spec["id"]})'
  for n in objects['rearrangeData']:specs.append({'id':'arrange'+n,'selector':'#rearrange_block_'+n,'arrange':True})
 elif key=='truc-hung':
  specs=[{'id':qid,'selector':f'[data-q="{qid}"]','arrange':qid.startswith('D_I_')} for qid in objects['answersData']]
 elif key=='truc-chinh':
  for part,items in objects['testData'].items():
   if not isinstance(items,list):continue
   for item in items:
    selector=f'#card_{item["id"]}'
    if part in ['partA1','partC2A']:selector=f'#row_{item["id"]}'
    specs.append({'id':item['id'],'selector':selector,'arrange':part=='partD1'})
 return specs

def answer(q,raw,choices,issues):
 q['sourceRaw']=raw
 q['explainHtml']=raw.get('explain',raw.get('expl',raw.get('explanation','')))
 q['knowledge']=raw.get('note',raw.get('category',''))
 q['teacherFlags']=[]
 if q.get('tokens'):
  candidates=raw.get('targetOrders')
  if candidates:
   accepted=[' '.join(order) for order in candidates]
  else:accepted=[raw.get('correctSentence',raw.get('correctString',raw.get('correctText','')))]
  # Only use source-provided orders that can actually be built from source cards.
  from collections import Counter
  q['accepted']=[text for text in accepted if Counter(norm(text).split())==Counter(norm(' '.join(q['tokens'])).split())]
  if len(q['accepted'])>1:q['teacherFlags'].append('Nguồn có nhiều thứ tự ghép được; cần giáo viên duyệt các biến thể.')
  if len(q['accepted'])<len(accepted):q['teacherFlags'].append('Một số đáp án/thứ tự nguồn không thể dựng từ bộ thẻ đã cho; chỉ đối chiếu các biến thể giữ đủ thẻ, cần giáo viên xác nhận.')
  if not q['accepted']:q['teacherFlags'].append('Đáp án nguồn không ghép được từ đúng bộ thẻ. Không tự thêm/bớt từ.')
  q['answerLabel']=raw.get('displaySentence',accepted[0])
 elif choices:
  correct=raw.get('correct')
  if not isinstance(correct,str) or correct not in [o['value'] for o in choices]:raise ValueError('Missing/invalid source choice '+q['id'])
  q['accepted']=[correct];q['answerLabel']=raw.get('text',raw.get('displayCorrect',next(o['html'] for o in choices if o['value']==correct)))
 else:
  if q['kind']=='multi-text':q['acceptedTuples']=[raw['correct']];q['accepted']=[]
  else:
   value=raw.get('correctVariants',raw.get('correctPhrases',raw.get('correct')))
   if isinstance(value,str):q['accepted']=[value]
   elif isinstance(value,list):q['accepted']=value
   else:q['accepted']=[]
  q['answerLabel']=raw.get('suggested',raw.get('displayCorrect',raw.get('text',raw.get('display',raw.get('correctText','')))))
  if not q['answerLabel']:q['answerLabel']=' / '.join(raw.get('correct',[])) if isinstance(raw.get('correct'),list) else str(raw.get('correct',''))
  if not q['accepted'] and q['kind']!='multi-text':
   # A free-text model may be usable, but never treat a keyword as an answer.
   model=q['answerLabel']
   if model and not re.search(r'\(|/|hoặc|\bOr:',model,re.I):q['accepted']=[model]
   else:q['teacherFlags'].append('Nguồn chỉ có từ khóa hoặc mẫu có nhiều cách diễn đạt; cần giáo viên xác nhận câu trả lời đầy đủ.')
  if len(q['accepted'])>1:q['teacherFlags'].append('Nguồn cho nhiều đáp án; giữ nguyên các biến thể, cần giáo viên duyệt trước khi dùng đánh giá chính thức.')
 q['autoGrade']=bool(q.get('accepted') or q.get('acceptedTuples'))
 if re.search(r'lưu ý giáo viên|ghi nhầm|đề gốc.*(?:sai|nhầm)',q['explainHtml'],re.I):q['teacherFlags'].append('Lời giải nguồn có lưu ý/hiệu chỉnh cần giáo viên đối chiếu.')
 issues.extend({'question':q['id'],'message':m} for m in q['teacherFlags'])

def convert(key,objects,dom,file,school):
 result={'schemaVersion':1,'exam':{'id':key,'school':school,'title':school+' · Giữa học kỳ I · Tiếng Anh 8','sourceHtml':file.name,'sourceSha256':hashlib.sha256(file.read_bytes()).hexdigest(),'sourceBaseline':BASELINE,'sourceHeadings':dom['examHeadings'],'sectionHeadings':dom['headings']},'sections':[],'questions':[],'contexts':dom['contexts'],'tracks':[],'issues':[]}
 def append(qid,section,raw,kind=None,tokens=None):
  snapshot=dom['questions'][qid]
  q={'id':qid,'section':section,'kind':kind or ('choice' if snapshot['options'] else 'text'),'promptHtml':snapshot['promptHtml'],'options':snapshot['options'],'sourceHeading':snapshot['sourceHeading']}
  if tokens:q['tokens']=tokens
  prompt_text=re.sub('<[^>]+>',' ',q['promptHtml']).lower()
  q['form']='sentence-rearrangement' if tokens else 'sentence-rewriting' if section=='rewrite' else 'verb-forms' if section=='verbs' else 'true-false' if q['options'] and all(o['value'] in ['T','F'] for o in q['options']) else 'pronunciation' if 'pronounced' in prompt_text or 'pronunciation' in prompt_text else 'stress' if 'stress pattern' in prompt_text or 'stressed syllable' in prompt_text else 'multiple-choice' if q['options'] else q['kind']
  if section=='cloze':q['context']=0
  if section=='reading':q['context']=1
  if section.startswith('listen-'):q['track']=section
  answer(q,raw,q['options'],result['issues']);result['questions'].append(q)
 if key=='truc-khang':
  for qid,raw in objects['EXAM_ANSWERS'].items():
   section='listen-1' if qid.startswith('L') else 'listen-2' if qid.startswith('blank') else 'language' if re.match(r'B\d',qid) else 'verbs' if qid.startswith('VF') else 'cloze' if re.match(r'C\d',qid) else 'reading' if qid.startswith(('RC','RQ')) else 'rewrite'
   append(qid,section,raw)
   if qid.startswith('blank'):result['questions'][-1]['contextHtml']=dom['table']
  for n,raw in objects['rearrangeData'].items():append('arrange'+n,'arrange',raw,'rearrange',raw['pool'])
 elif key=='truc-hung':
  for qid,raw in objects['answersData'].items():
   section=next((section for prefix,section in [('A_I_','listen-1'),('A_II_','listen-2'),('B_I_','language'),('B_II_','verbs'),('C_I_','cloze'),('C_II_','reading'),('D_I_','arrange'),('D_II_','rewrite')] if qid.startswith(prefix)))
   tokens=[x['text'] for x in objects['rearrangeData'][qid]['poolChunks']] if section=='arrange' else None
   append(qid,section,raw,'rearrange' if tokens else None,tokens)
   if tokens:result['questions'][-1]['rearrangeSource']=objects['rearrangeData'][qid]
 elif key=='truc-chinh':
  mapping={'partA1':'listen-1','partA2':'listen-2','partB1':'language','partB2':'verbs','partC1':'cloze','partC2A':'reading','partC2B':'reading','partD1':'arrange','partD2':'rewrite'}
  for part,section in mapping.items():
   for raw in objects['testData'][part]:
    tokens=raw.get('rawTokens');kind='rearrange' if tokens else 'multi-text' if raw.get('dual') else None
    append(raw['id'],section,raw,kind,tokens)
    if raw.get('dual'):
     result['questions'][-1]['inputCount']=len(raw['correct'])
     result['questions'][-1]['contextHtml']='<p>'+html(raw['prompt'])+'</p>'
     result['questions'][-1]['teacherFlags'].append('Giữ cả prompt nguyên văn có gợi ý (do), dù giao diện HTML gốc bỏ gợi ý này ở mẫu hai ô. Giáo viên cần đối chiếu.')
     result['issues'].append({'question':raw['id'],'message':result['questions'][-1]['teacherFlags'][-1]})
    if raw['id']=='D1_1':
     q=result['questions'][-1];q['autoGrade']=False;q['teacherFlags'].append('Bộ thẻ dùng fluent/speaks, đáp án mẫu lại có speak/fluently; giữ nguyên nguồn, không tự chấm đúng.')
     result['issues'].append({'question':q['id'],'message':q['teacherFlags'][-1]})
    if raw['id']=='D2_3':
     result['questions'][-1]['teacherFlags'].append('Câu gốc ở hiện tại (spend), câu viết lại dùng took. Giữ nguyên, cần giáo viên duyệt sự nhất quán về thì.')
     result['issues'].append({'question':raw['id'],'message':result['questions'][-1]['teacherFlags'][-1]})
 for section,title in SECTION_NAMES.items():
  members=[q for q in result['questions'] if q['section']==section]
  if members:result['sections'].append({'id':section,'title':title,'description':members[0]['sourceHeading'],'icon':'🎧' if section.startswith('listen') else '🧩' if section=='arrange' else '🧭' if section in ['reading','cloze'] else '⚡'})
 # Follow source section order, retaining all stable source IDs.
 result['questions'].sort(key=lambda q:list(SECTION_NAMES).index(q['section']))
 for i,q in enumerate(result['questions'],1):q['number']=i
 audio=list(dict.fromkeys(re.findall(r'<audio[^>]+src="([^"]+)"',file.read_text())))
 for i,section in enumerate(['listen-1','listen-2']):
  src=audio[min(i,len(audio)-1)]
  if not (file.parent/src).exists():raise ValueError('Missing audio '+src)
  result['tracks'].append({'id':section,'src':src,'transcriptHtml':dom['transcripts'][i],'wholeFile':len(audio)==1})
 if dom['images']:
  educational_html=' '.join(q['promptHtml']+' '+q.get('contextHtml','')+' '+' '.join(o['html'] for o in q['options']) for q in result['questions'])+' '.join(result['contexts'])
  for image in dom['images']:
   if image['src'] not in educational_html:raise ValueError('Image needs explicit mapping: '+str(image['src']))
 result['sourceSnapshot']=dom
 return result

class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def copyfile(self,source,output):
  try:super().copyfile(source,output)
  except (BrokenPipeError,ConnectionResetError):pass

def generate(verify=False):
 raw=json.loads(Path('/tmp/ht-grade8-source-scan.json').read_text())
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
 threading.Thread(target=server.serve_forever,daemon=True).start();results=[]
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'),args=['--no-sandbox'])
   context=browser.new_context();base=f'http://127.0.0.1:{server.server_port}/'
   context.route('**/*',lambda r:r.continue_() if r.request.url.startswith(base) else r.abort())
   page=context.new_page()
   for key,(folder,name,school) in PILOTS.items():
    file=ROOT/'grade-8/De_thi_GHK1'/folder/name;objects=raw[str(file.relative_to(ROOT))]['objects'];specs=source_specs(key,objects)
    page.goto(base+quote(str(file.relative_to(ROOT))));page.wait_for_selector(specs[0]['selector'])
    # The card IDs of Truc Chinh are rendered by its own unchanged source script.
    starts={'truc-khang':['Many people who are close','Teenagers today live'], 'truc-hung':['I live in a village in the north','Last week, Nick'], 'truc-chinh':['Children in my hometown','Many teenagers love']}[key]
    transcriptIds={'truc-khang':['transcript1','transcript2'],'truc-hung':['transcriptSec1','transcriptSec2'],'truc-chinh':['trans1','trans2']}[key]
    dom=page.evaluate(DOM_EXTRACT,{'specs':specs,'starts':starts,'transcriptIds':transcriptIds})
    data=convert(key,objects,dom,file,school)
    target=file.parent/'practice-game-data.js'
    encoded='// Generated from unchanged exam source. Do not hand-edit.\nwindow.HT_PRACTICE_DATA = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n'
    if verify:
     if target.read_text()!=encoded:raise ValueError('Generated data differs from current source: '+str(target))
    else:target.write_text(encoded)
    shell=(ROOT/'tools/grade8-games/shell.html').read_text().replace('SOURCE_HTML',quote(file.name))
    shell=shell.replace('Luyện đề thử nghiệm · English Quest 8',school+' · English Quest 8')
    shell=shell.replace('HT ENGLISH</span></div>',school+'</span></div>')
    if verify:
     if (file.parent/'practice-game-pilot.html').read_text()!=shell:raise ValueError('Launcher differs from shared shell')
    else:(file.parent/'practice-game-pilot.html').write_text(shell)
    support={
      'truc-khang':{'B3':{'translation':'Chị/em gái tôi say mê lập trình máy tính. Cô ấy muốn học công nghệ thông tin trong tương lai.','tip':'Be keen on + danh từ / V-ing diễn tả sự yêu thích.'}},
      'truc-hung':{'D_I_2':{'translation':'Mạng xã hội quan trọng đối với cuộc sống của một thiếu niên.','tip':'Be important to + người/sự vật: quan trọng đối với ai/cái gì.'}},
      'truc-chinh':{'B1_3':{'translation':'Anh/em trai tôi thích làm mô hình máy bay trong thời gian rảnh.','tip':'Be fond of + V-ing; sau giới từ of dùng danh động từ.'}}
    }
    supplemental=file.parent/'practice-game-support.js'
    if not verify and not supplemental.exists():supplemental.write_text('// Supplemental AI content; teacher review required. Never used for grading.\nwindow.HT_PRACTICE_SUPPORT = '+json.dumps({'schemaVersion':1,'provenance':'AI-generated','teacherVerified':False,'items':support[key]},ensure_ascii=False,indent=2)+';\n')
    results.append(data);print(key,len(data['questions']),'questions,',len(data['sections']),'sections,',len(data['issues']),'review flags',flush=True)
   context.close();browser.close()
 finally:server.shutdown();server.server_close()
 return results
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');args=parser.parse_args();generate(args.verify)
