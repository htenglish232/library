from pathlib import Path
from html import escape
import argparse
import base64
import json
import re
import subprocess
import tempfile
import zipfile
from hashlib import sha256
from lessons import lessons

ROOT=Path(__file__).resolve().parent
TEMPLATE=ROOT/'worksheet.template.html'
OUT=ROOT.parent/'HTML_Output'
DATA=ROOT/'lessons.json'

def catalog():
    for unit in range(1,25):
        yield f'Unit {unit:02}'
        if unit%4==0:
            yield f'Review {unit//4:02}'

def image_uri(path):
    return 'data:image/jpeg;base64,'+base64.b64encode(path.read_bytes()).decode('ascii')

def safely_embed(value):
    return json.dumps(value,ensure_ascii=False,separators=(',',':')).replace('<',r'\u003c')

def prepare(source, files):
    if source.is_dir():
        for path in source.rglob('*'):
            if path.is_file():
                files[path.name]=path.read_bytes()
    else:
        with zipfile.ZipFile(source) as archive:
            for name in archive.namelist():
                if not name.endswith('/'):
                    files[Path(name).name]=archive.read(name)

def render(pdf, folder):
    source=folder/'source.pdf'
    source.write_bytes(pdf)
    subprocess.run(['pdftoppm','-scale-to','1350','-jpeg','-jpegopt','quality=90',str(source),str(folder/'page')],check=True)
    from PIL import Image
    for path in sorted(folder.glob('page-*.jpg')):
        with Image.open(path) as image:
            width,height=image.size
        yield {'width':width,'height':height,'src':image_uri(path)}

def html_file(prefix,label,source):
    stem=Path(source).stem.replace(' - ','_').replace('-','_').replace(' ','_')
    if label=='Unit 03':
        stem='Unit_03_The_Noun'
    return f'{prefix:02}_{stem}.html'

def write_index(records, logo, out):
    cards=[]
    for i in range(6):
        items=[]
        for r in records[i*5:i*5+5]:
            name=escape(r['label']+(' – '+r['topic'] if r['topic'] else ''))
            if r['status']=='Completed':
                items.append(f"<li><a href=\"{r['file']}\">{name}</a></li>")
            elif r['file'] and r.get('generated'):
                items.append(f"<li><a href=\"{r['file']}\">{name}</a> <small>{'Mẫu gốc · cần đối chiếu' if r['label']=='Unit 01' else 'Cần kiểm tra'}</small></li>")
            else:
                items.append(f'<li>{name} <small>Đang chuẩn bị</small></li>')
        cards.append(f'<section><h2>Units {i*4+1:02}–{i*4+4:02}</h2><ul>{"".join(items)}</ul></section>')
    out.write_text(f"""<!doctype html>
<html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HT English Center – Grade 3 Grammar Practice</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#eaf2fa;color:#163653;font:16px system-ui}}
header{{text-align:center;padding:24px 12px 8px}}img{{width:150px}}h1{{font-size:clamp(19px,4vw,28px)}}
p{{margin:4px}}main{{max-width:970px;margin:auto;display:grid;gap:12px;padding:16px;grid-template-columns:repeat(auto-fit,minmax(min(100%,275px),1fr))}}
section{{background:white;border:1px solid #d5e3f0;border-radius:12px;padding:16px}}h2{{margin:0 0 10px;font-size:16px}}ul{{padding:0;list-style:none;margin:0}}li{{padding:8px 0;border-top:1px solid #eaf2fa}}a{{color:#1767b5}}small{{display:inline-block;color:#526784}}
</style><header><img alt="HT English Center" src="{logo}"><p><strong>HT English Center</strong></p><p>SĐT 0962240866</p><h1>GRADE 3 – GRAMMAR PRACTICE</h1></header>
<main>{"".join(cards)}</main></html>""",encoding='utf-8')

TOPICS={
    'Unit 01':'Person / Place / Thing / Animal','Unit 04':'Noun + -s / -es',
    'Unit 05':'I / You / He / She / It','Unit 06':'We / You / They','Unit 07':'This / That','Unit 08':'These / Those',
    'Unit 09':'Pronoun + Be','Unit 10':'Pronoun + Be + Not','Unit 11':'Am / Are / Is','Unit 12':'Who / What + Be',
    'Unit 13':'Adjective + Noun','Unit 14':'Be + Adjective','Unit 15':'Adjective + Noun / Be + Adjective','Unit 16':'Numbers',
    'Unit 17':'Like / Likes','Unit 18':'Have / Has','Unit 19':"Don't / Doesn't Like",'Unit 20':'Do / Does ... Like?',
    'Unit 21':'What Do / Does ... Like?','Unit 22':"Can / Can't",'Unit 23':'Can Questions','Unit 24':'Time / Weather / Season'
}
SAMPLE_NOTE='Trang in 4, A5. Answer Key ghi “left picture (school)”. HTML mẫu chấm “hospital” và khai báo hình trái là “hospital”. Cần xác nhận tên của hình trái trước khi đổi từ hiển thị. Bản HTML gốc được giữ nguyên.'


def interaction_for(source, label):
    q=source.copy()
    if label=='Unit 02':
        return q
    if q['kind']=='word' and not q.get('group'):
        q['kind']='direct'
        q.pop('choices',None)
    if q['kind']=='entry' and not q.get('cells'):
        official=q['ans'][0] if isinstance(q['ans'],list) else q['ans']
        tokens=official.split()
        if len(tokens)>=3 and official.endswith(('.', '?', '!')):
            from random import Random
            mixed=tokens.copy()
            Random(label+q['id']).shuffle(mixed)
            if mixed==tokens:
                mixed=tokens[1:]+tokens[:1]
            q['kind']='order'
            q['choices']=mixed
        else:
            q['kind']='direct'
    return q


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('source',type=Path,help='G3_Grammar_Units ZIP or extracted directory')
    parser.add_argument('--output',type=Path,default=OUT)
    parser.add_argument('--force',action='store_true')
    parser.add_argument('--only',action='append',help='Build only the specified worksheet label. May be repeated.')
    args=parser.parse_args()
    out=args.output
    out.mkdir(parents=True,exist_ok=True)
    files={}
    prepare(args.source,files)
    manifest=out/'manifest.json'
    previous={r['label']:r for r in json.loads(manifest.read_text(encoding='utf-8'))} if manifest.exists() else {}
    records=[]
    for i,label in enumerate(catalog(),1):
        filename=next(n for n in files if n.startswith(label) and n.endswith('.pdf'))
        exists=label in lessons or label=='Unit 01'
        topic=lessons[label].title if label in lessons else TOPICS.get(label,'')
        if label.startswith('Review') and label not in lessons:
            end=int(label[-2:])*4
            topic=f'Units {end-3:02}–{end:02}'
        records.append(dict(order=i,label=label,topic=topic,source=filename,pages=2 if label.startswith('Review') else 3,
                            file=html_file(i,label,filename),components=32 if label=='Unit 01' else len(lessons[label].questions) if exists else None,
                            status='Pending',generated=False,notes=[]))
    def save():
        temp=manifest.with_suffix('.tmp')
        temp.write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
        temp.replace(manifest)
    for r in records:
        prior=previous.get(r['label'])
        if prior and ((args.only and r['label'] not in args.only) or (not args.force and prior['status']=='Completed' and (out/r['file']).is_file())):
            r.update(prior)
    save()
    template=TEMPLATE.read_text(encoding='utf-8')
    sample=next(b for n,b in files.items() if n.endswith('.html'))
    logo=re.search(r'id="brandLogo"[^>]+src="([^"]+)"',sample.decode('utf-8-sig')).group(1)
    for r in records:
        label=r['label']
        if (args.only and label not in args.only) or r['status']=='Completed' or (label!='Unit 01' and label not in lessons):
            continue
        r['status']='In progress'
        save()
        try:
            path=out/r['file']
            if label=='Unit 01':
                path.write_bytes(sample)
                r['sha256']=sha256(sample).hexdigest()
                r['notes']=[SAMPLE_NOTE]
            else:
                lesson=lessons[label]
                with tempfile.TemporaryDirectory() as folder:
                    pages=list(render(files[r['source']],Path(folder)))
                r['pages']=len(pages)
                questions=[interaction_for(q,label) for q in lesson.questions]
                ids=[q['id'] for q in questions]
                assert len(ids)==len(set(ids)), f'Duplicate question IDs in {label}'
                title=f"{label} – {r['topic']}"
                substitutions={
                    'TITLE':escape(title), 'UPPER_TITLE':escape(title.upper()), 'TOTAL':str(len(questions)),
                    'NAV':''.join(f'<button type="button" data-page="{i}">{i+1}</button>' for i in range(len(pages))),
                    'DATA':safely_embed(dict(title=title,key='HT_ENGLISH_GRAMMAR_'+label.upper().replace(' ','_')+'_V1',
                                          pages=pages,questions=questions,targets=lesson.targets,reviewSlots=lesson.review_slots))
                }
                path.write_text(re.sub(r'%%([A-Z_]+)%%',lambda m:substitutions[m[1]],template),encoding='utf-8')
                r['notes']=lesson.notes[:]
                r['teacherGradedSlots']=[slot['id'] for slot in lesson.review_slots]
            r['generated']=True
            r['status']='Needs review'
        except Exception as error:
            r['status']='Failed'
            r['notes']=[str(error)]
        save()
    write_index(records,logo,out/'index.html')

if __name__=='__main__':
    main()
