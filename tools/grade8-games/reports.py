"""Publish source inventory and per-exam reports; never create additional games."""
from pathlib import Path
from collections import Counter
import hashlib,json,os,re
ROOT=Path(__file__).resolve().parents[2]
DOCS=ROOT/'docs/grade8-games'
records=json.loads((DOCS/'inventory.json').read_text())
OUT=Path(os.environ.get('GRADE8_GAME_TEST_OUTPUT','/tmp/ht-grade8-pilot-tests'))
PILOTS={11:'truc-khang',12:'truc-hung',19:'truc-chinh'}
report_dir=DOCS/'reports';report_dir.mkdir(exist_ok=True)
table=['# Danh sách đề đã quét — Giai đoạn A/B','','Số đếm của các đề chưa chuyển là bằng chứng từ cấu trúc nguồn, chưa phải kết quả đối chiếu game. Chỉ ba đề thử nghiệm được kiểm chứng toàn bộ bằng Chromium.','','| Thư mục | HTML nguồn | Số câu phát hiện | Audio vật lý | Trạng thái |','| --- | --- | ---: | ---: | --- |']
suffixes=Counter()
for record in records:
 source=Path(record['source']);number=int(source.parent.name.split('_')[0]);suffixes[number]+=1
 report={**record,'convertedQuestions':0,'gamePath':None,'validationStatus':'scan-only; waiting for Phase C approval','teacherReview':[]}
 if number==1:
  report['validationStatus']='existing Truc Tuan reference preserved, not regenerated'
 elif number in PILOTS:
  game_file=ROOT/source.parent/'practice-game-data.js'
  data=json.loads(game_file.read_text().split('window.HT_PRACTICE_DATA = ',1)[1].strip()[:-1])
  browser=json.loads((OUT/(PILOTS[number]+'.json')).read_text())
  assert browser['failed']==0 and browser['dataSha256']==hashlib.sha256(game_file.read_bytes()).hexdigest(),'Stale or failed browser report'
  report.update({'convertedQuestions':len(data['questions']),'gamePath':str(source.parent/'practice-game-pilot.html'),
   'validationStatus':'pilot verified; awaiting teacher approval before bulk conversion','autoGradeableQuestions':sum(q['autoGrade'] for q in data['questions']),
   'manualReviewQuestions':[q['id'] for q in data['questions'] if not q['autoGrade']],
   'gameForms':dict(Counter(q['form'] for q in data['questions'])),'sections':data['sections'],
   'teacherReview':data['issues'],'browser':browser,
   'pedagogyCoverage':{'sourceExplanations':sum(bool(q['explainHtml']) for q in data['questions']),
    'dedicatedAITranslations':1,'aiStatus':'AI-generated, unverified; separate support file, never used for grading',
    'remainingTranslations':'No additional translations invented. Original Vietnamese explanations preserved; separate full translations need teacher review.'}})
 if not record['audioReferences'] and record['physicalAudioFiles']:
  report['teacherReview'].append({'question':None,'message':'Audio exists in the source folder but is assigned dynamically; its mapping needs an adapter before conversion.'})
 if number==6:report['teacherReview'].append({'question':None,'message':'37 source questions, no sentence rewriting section. Several grading keys are functions, not static JSON. Do not pad to 42.'})
 if number==9:report['teacherReview'].append({'question':None,'message':'41 source questions; one standalone pronunciation question plus 9 other data groups. Do not pad to 42.'})
 if number==10:report['teacherReview'].append({'question':None,'message':'Procedural grading distributed through functions; requires explicit answer adapter and validation, not guessed extraction.'})
 if record.get('duplicateOf'):report['teacherReview'].append({'question':None,'message':'Byte-identical duplicate of '+record['duplicateOf']+'; not an additional independent exam.'})
 name=f'{number:02d}-{suffixes[number]}.json';(report_dir/name).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 state='Thử nghiệm đạt' if number in PILOTS else 'Mẫu có sẵn, giữ nguyên' if number==1 else 'Đã quét, chưa tạo game'
 table.append(f'| {source.parent.name} | {source.name} | {record["detectedQuestionCount"]} | {record["physicalAudioFiles"]} | [{state}](reports/{name}) |')
table+=['','20 HTML trong 19 thư mục, 19 nội dung duy nhất. Hai HTML Trực Tuấn giống nhau. Không có thư mục số 15 trong nguồn hiện tại; không đánh lại số hay tự tạo đề thiếu.','','**Chỉ tạo 3 game thử nghiệm mới. Chưa sửa index/danh mục Firebase, chưa làm hàng loạt, chưa merge/deploy.**']
(DOCS/'INVENTORY.md').write_text('\n'.join(table)+'\n')
print('Published 20 per-source reports and inventory table; only 3 pilot games exist in this task.')
