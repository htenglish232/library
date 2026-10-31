"""Re-extract both complete PDFs, then compare every academic field to JSON."""
from pathlib import Path
import re, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'unit-2-individuals-and-families/sources'
compact=lambda text:re.sub(r'\s+',' ',text).strip()
for name,pages in [('worksheet',5),('answer-key',2)]:
    pdf=SOURCE/(name+'.pdf')
    info=subprocess.check_output(['pdfinfo',str(pdf)],text=True)
    assert int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1))==pages
    extracted=subprocess.check_output(['pdftotext','-layout',str(pdf),'-'],text=True)
    assert compact(extracted)==compact((SOURCE/(name+'.txt')).read_text()),name+' PDF extraction differs'
    print('PASS complete PDF:',name,pages,'pages')
subprocess.run([sys.executable,str(ROOT/'tests/extract-source.py'),'--verify'],check=True)
