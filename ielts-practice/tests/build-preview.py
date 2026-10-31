"""Build one downloadable review HTML that opens without a server.

No hosting/deployment. Canonical app continues to load separate JSON/modules.
"""
from pathlib import Path
import base64, json, re, sys
ROOT=Path(__file__).resolve().parents[2]
APP=ROOT/'ielts-practice'
UNIT=APP/'unit-2-individuals-and-families'
target=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/ielts-unit2-preview.html')
html=(UNIT/'index.html').read_text()
css=(APP/'shared/worksheet.css').read_text()
def font(match):
    path=(APP/'shared'/match.group(1)).resolve()
    return 'url(data:font/woff2;base64,'+base64.b64encode(path.read_bytes()).decode()+')'
css=re.sub(r'url\(([^)]+\.woff2)\)',font,css)
model=(APP/'shared/model.js').read_text().replace('export ','')
engine=(APP/'shared/worksheet.js').read_text()
engine=re.sub(r'^import .*?;\n','',engine,count=1)
payload=json.dumps({'unit':json.loads((UNIT/'unit.json').read_text()),'answers':json.loads((UNIT/'answers.json').read_text()),'support':json.loads((UNIT/'support.json').read_text())},ensure_ascii=False).replace('<','\\u003c')
script='window.HT_IELTS_PREVIEW='+payload+';\n'+model+'\n'+engine
assert '</script' not in script.lower()
html=html.replace('<link rel="stylesheet" href="../shared/worksheet.css">','<style>'+css+'</style>')
html=html.replace('<script type="module" src="../shared/worksheet.js"></script>','<script type="module">'+script+'</script>')
icon='data:image/svg+xml;base64,'+base64.b64encode((APP/'shared/icon.svg').read_bytes()).decode()
html=html.replace('../shared/icon.svg',icon)
base='https://github.com/htenglish232/library/blob/feature/ielts-unit2-worksheet/ielts-practice/'
html=html.replace('href="../index.html"','href="https://htenglish232.github.io/library/index.html"')
html=html.replace('href="../../index.html"','href="https://htenglish232.github.io/library/index.html"')
for old,new in [('sources/worksheet.pdf','unit-2-individuals-and-families/sources/worksheet.pdf'),('sources/answer-key.pdf','unit-2-individuals-and-families/sources/answer-key.pdf'),('../docs/source-audit.md','docs/source-audit.md')]:
    html=html.replace('href="'+old+'"','href="'+base+new+'"')
html=html.replace('Đang mở Unit 2…','Đang mở bản xem thử Unit 2…')
target.parent.mkdir(parents=True,exist_ok=True);target.write_text(html)
print(f'Review HTML: {target} ({target.stat().st_size} bytes). No deployment.')
