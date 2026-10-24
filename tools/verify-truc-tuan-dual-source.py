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
FILES = ['1. THCS Truc Tuan.html', 'GHK1 K8 - part 1.mp3', 'GHK1 K8 - part 2 .mp3']


def extract():
    source = (FOLDER / FILES[0]).read_text()
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
    raw = extract()
    reference = json.loads((FOLDER/'truc-tuan-game/source-data.js').read_text().split('window.HT_GAME_SOURCE = ',1)[1].strip()[:-1])
    for key in ['questions','passages','transcripts']: assert raw[key] == reference[key], ('Reference/current HTML mismatch',key)
    data = json.loads((FOLDER/'truc-tuan-dual-data.js').read_text().split('window.HT_PRACTICE_DATA = ',1)[1].strip()[:-1])
    assert [q['id'] for q in data['questions']] == [q['id'] for q in raw['questions']]
    for a,b in zip(data['questions'],raw['questions']):
        assert a['sourceRaw']==b['source'] and a['promptHtml']==b['promptHtml'] and a['options']==b['options'],a['id']
        assert a.get('tokens')==b.get('tokens'),a['id']
        assert a.get('context')==b.get('passage'),a['id']
        if 'track' in b: assert a['track']=='listen-'+str(b['track'])
    assert data['contexts']==raw['passages'] and [t['transcriptHtml'] for t in data['tracks']]==raw['transcripts']
    assert data['exam']['sourceSha256']==raw['sourceFiles'][FILES[0]]
    for track in data['tracks']: assert track['sha256']==raw['sourceFiles'][track['src']]
    subprocess.run(['node','tools/build-truc-tuan-dual-data.mjs','--verify'],cwd=ROOT,check=True)
    print('PASS all 42 IDs/prompts/options/raw answers/notes/tokens, original order, 2 readings, 2 transcripts and MP3 hashes match current HTML; originals unchanged.')
