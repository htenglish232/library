"""Reproduce game data without executing or changing either original exam.

Requires Playwright Python and Chromium. Run from any directory.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'grade-8/De_thi_GHK1/1_THCS Truc Tuan'
FILES = ['1. THCS Truc Tuan.html', '1. THCS Truc Tuan(2).html',
         'GHK1 K8 - part 1.mp3', 'GHK1 K8 - part 2 .mp3']


def extract():
    source = (FOLDER / FILES[0]).read_text()
    assert (FOLDER / FILES[0]).read_bytes() == (FOLDER / FILES[1]).read_bytes()
    literals = {}
    for key in ['masterData', 'rearrangeConfig']:
        match = re.search(r'const ' + key + r' = (\{.*?\n    \});', source, re.S)
        assert match, key
        # Only the isolated, checked-in object literal is evaluated, in a fresh VM.
        script = "const vm=require('node:vm');process.stdout.write(JSON.stringify(vm.runInNewContext('('+" + json.dumps(match[1]) + "+')',{}, {timeout:1000})));"
        literals[key] = json.loads(subprocess.check_output(['node', '-e', script], text=True))
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'), args=['--no-sandbox'])
        page = browser.new_page()
        data = page.evaluate('''source => {
          const doc=new DOMParser().parseFromString(source,'text/html');
          const clean=node=>{
            const copy=node.cloneNode(true);
            copy.querySelectorAll('input').forEach(n=>n.replaceWith(doc.createTextNode(' ______ ')));
            copy.querySelectorAll('button,.status-indicator,.feedback-box').forEach(n=>n.remove());
            for(const el of [copy,...copy.querySelectorAll('*')]){
              for(const a of [...el.attributes])el.removeAttribute(a.name);
            }
            return copy.innerHTML.trim();
          };
          const questions=[...doc.querySelectorAll('.question-card')].map(card=>{
            const id=card.dataset.qid;
            const heading=card.firstElementChild.firstElementChild;
            return {id, promptHtml:clean(heading), options:[...card.querySelectorAll('input[type="radio"]')].map(input=>{
              const label=input.closest('label').cloneNode(true);
              label.querySelectorAll('input,button').forEach(n=>n.remove());
              return {value:input.value,html:clean(label)};
            })};
          });
          const sections=[...doc.querySelectorAll('section')];
          const reading=sections.find(s=>s.querySelector('[data-qid="q26"]'));
          const passages=[...reading.querySelectorAll('div.bg-gradient-to-br')].map(clean);
          return {questions,passages,transcripts:[1,2].map(n=>clean(doc.getElementById('transcriptContent'+n)))};
        }''', source)
        browser.close()
    assert len(data['questions']) == 42 and len(data['passages']) == 2
    for q in data['questions']:
        n = int(q['id'][1:])
        q['section'] = 'listening' if n <= 12 else 'grammar' if n <= 25 else 'reading' if n <= 35 else 'writing'
        q['source'] = literals['masterData'][q['id']]
        q['kind'] = q['source'].get('type', 'choice')
        if n <= 12:
            q['track'] = 1 if n <= 6 else 2
        if 26 <= n <= 35:
            q['passage'] = 0 if n <= 30 else 1
        if q['kind'] == 'rearrange':
            q['tokens'] = literals['rearrangeConfig'][q['id']]['tokens']
    data['sourceFiles'] = {name: hashlib.sha256((FOLDER / name).read_bytes()).hexdigest() for name in FILES}
    return data


if __name__ == '__main__':
    data = extract()
    target = FOLDER / 'truc-tuan-game/source-data.js'
    target.write_text('// Generated from the original exam by tools/extract-truc-tuan-game.py.\nwindow.HT_GAME_SOURCE = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';\n')
    print('Extracted 42 questions, original answers/explanations, 2 passages, 2 transcripts, 3 word banks; originals unchanged.')
