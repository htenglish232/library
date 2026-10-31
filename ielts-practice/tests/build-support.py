"""Extract selected keywords/evidence; never rewrite source questions or keys."""
from pathlib import Path
import json, re, sys
UNIT=Path(__file__).resolve().parents[1]/'unit-2-individuals-and-families'
unit=json.loads((UNIT/'unit.json').read_text());key=json.loads((UNIT/'answers.json').read_text())
sentences=lambda text:re.split(r'(?<=\.)\s+',text)
# Zero-based paragraph/sentence indexes select only literal source excerpts.
mcq=[
 ([(0,[1])],['Parents','emotional support','discipline']),
 ([(1,[2])],['support','economic instability','social change']),
 ([(2,[1])],['work demands','urban migration','reduce the time']),
 ([(2,[3])],['work-life balance','preserving','healthy family relationships']),
 ([(3,[1])],['Traditions','preserve identity','intergenerational bonds']),
 ([(3,[2])],['Elderly members','wisdom','life experience']),
 ([(3,[2])],['younger generations','innovation','energy']),
 ([(4,[0,1])],['conflicts','inevitable','resolved effectively']),
 ([(4,[1])],['empathy','communication','compromise']),
 ([(3,[0]),(4,[2])],['Despite these challenges','essential role','Strong family relationships'])
]
summary=[
 (0,0,['individual','behavior']),
 (0,1,['emotional','support']),
 (0,2,['family','support','system']),
 (1,0,['modern lifestyles','relationships']),
 (1,0,['emotional','distance']),
 (1,1,['work-life','balance']),
 (2,0,['cultural','traditions']),
 (2,1,['Elderly members','wisdom']),
 (2,1,['younger generations','innovation','energy']),
 (2,2,['family','conflicts','empathy','communication'])
]
data={'provenance':'Keywords là phần chọn lọc bổ sung từ nguồn, không phải danh sách từ khóa do PDF cung cấp. Dẫn chứng trích nguyên văn, không sửa đề hoặc lời giải.',
 'mcq':[], 'summary':[]}
for index,(refs,keywords) in enumerate(mcq):
 quotes=[{'source':'reading','paragraph':p+1,'text':' '.join(sentences(unit['reading'][p])[s] for s in indices)} for p,indices in refs]
 data['mcq'].append({'number':index+1,'keywords':keywords,'quotes':quotes})
for index,(p,s,keywords) in enumerate(summary):
 data['summary'].append({'number':index+1,'keywords':keywords,'quotes':[{'source':'completedSummary','paragraph':p+1,'text':sentences(key['completedSummary'][p])[s]}]})
for kind in ['mcq','summary']:
 for item in data[kind]:
  assert all(any(word.lower() in quote['text'].lower() for quote in item['quotes']) for word in item['keywords']),item
text=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
if '--verify' in sys.argv:assert (UNIT/'support.json').read_text()==text,'Source excerpt selections differ'
else:(UNIT/'support.json').write_text(text)
print('PASS 20 keyword/evidence entries selected literally from source Reading/completed Summary')
