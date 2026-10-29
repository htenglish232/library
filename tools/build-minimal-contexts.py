"""Build read-only presentation metadata from source HTML; never execute exam apps.

Does not modify question payloads, answers, progress versions or original exams.
Requires the same Python Playwright/Chromium toolchain as the existing builders.
"""
from pathlib import Path
from urllib.parse import unquote
import argparse,hashlib,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
SHARED=ROOT/'grade-8/De_thi_GHK1/shared-practice'
def read_data(path,key='window.HT_PRACTICE_DATA = '):
    return json.JSONDecoder().raw_decode(path.read_text().split(key,1)[1])[0]
def inventory():
    rows=[]
    for path in sorted(ROOT.glob('grade-[678]/**/*-dual-data.js')):
        data=read_data(path)
        rows.append((path.with_name(path.name.replace('-data.js','-mode.html')),data,'dual-mode-engine.js'))
    for path in sorted(ROOT.glob('grade-8/**/practice-game-data.js')):
        rows.append((path.with_name('practice-game-pilot.html'),read_data(path),'engine.js'))
    folder=ROOT/'grade-8/De_thi_GHK1/1_THCS Truc Tuan'
    old=read_data(folder/'truc-tuan-game/source-data.js','window.HT_GAME_SOURCE = ')
    old['exam']={'id':'legacy-truc-tuan','school':'THCS Trực Tuấn','number':1,'grade':8,'sourceHtml':'1. THCS Truc Tuan.html'}
    rows.append((folder/'truc-tuan-game-test.html',old,'truc-tuan-game/game.js'))
    return rows

def emit(path,text,verify):
    if verify:
        assert path.read_text()==text, f'Presentation metadata differs: {path.relative_to(ROOT)}'
    else:
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    manifest={};games=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page()
        for launcher,data,engine in inventory():
            assert launcher.exists(),launcher
            source=launcher.parent/unquote(data['exam']['sourceHtml'])
            source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
            # Legacy pilot payloads retain historical whole-file hashes; current source
            # is recorded separately while payload bytes stay unchanged.
            if engine=='dual-mode-engine.js' and data['exam'].get('sourceSha256'):assert data['exam']['sourceSha256'] in [source_sha,hashlib.sha256(source.read_text().encode()).hexdigest()],str(source)
            if data['exam']['id']=='legacy-truc-tuan':
                extracted=[{'id':q['id'],'html':data['passages'][q['passage']] if q['section']=='reading' else '',
                            'reading':q['section']=='reading','evidence':'verified-original-passages'} for q in data['questions']]
            else:
                extracted=page.evaluate((ROOT/'tools/minimal-context-source.js').read_text(),{'source':source.read_text(),'data':data})['questions']
            passages=[];by_question={};evidence={};markers={}
            for item in extracted:
                if not item['reading']:continue
                assert item['html'],f'Missing reading {launcher}: {item["id"]}'
                if item['html'] not in passages:passages.append(item['html'])
                by_question[item['id']]=passages.index(item['html']);evidence[item['id']]=item['evidence']
                q=next(q for q in data['questions'] if q['id']==item['id'])
                # Highlight only an explicit prompt/blank label that also occurs
                # exactly once as a numbered blank in the original passage.
                marker=page.evaluate('''({q,html})=>{const p=document.createElement('div');p.innerHTML=q.promptHtml;const text=p.textContent;const match=text.match(/\\((\\d{1,2})\\)|(?:blank|gap|vị trí)\\s*[:#]?\\s*(\\d{1,2})/i);const n=match?Number(match[1]||match[2]):/^\\d{1,2}$/.test(String(q.sourceNumber))?Number(q.sourceNumber):null;if(!n)return null;const d=document.createElement('div');d.innerHTML=html;const re=new RegExp('\\\\(\\\\s*'+n+'\\\\s*\\\\)\\\\s*[_….[\\\\] ]{2,}','g');return [...d.textContent.matchAll(re)].length===1?n:null;}''',{'q':q,'html':item['html']})
                if marker:markers[q['id']]=marker
            assert len(passages)==2,f'Inspect source reading groups: {launcher}, {len(passages)}'
            entry={'passages':passages,'byQuestion':by_question,'clozeMarkers':markers}
            id=data['exam']['id']
            if id in manifest:assert manifest[id]==entry,f'Duplicate exam views disagree: {id}'
            else:manifest[id]=entry
            game={'game':launcher.relative_to(ROOT).as_posix(),'grade':int(launcher.relative_to(ROOT).parts[0].split('-')[1]),'school':data['exam']['school'],'number':data['exam'].get('number',1),'examId':id,'engine':engine,'questions':len(data['questions']),'readingQuestions':len(by_question),'passages':len(passages),'highlightableBlanks':len(markers),'source':source.relative_to(ROOT).as_posix(),'sourceSha256':source_sha,'payloadSourceSha256':data['exam'].get('sourceSha256'),'readingEvidence':evidence}
            games.append(game);print('PASS',game['game'],game['questions'],'questions',len(by_question),'reading',len(markers),'exact blank markers',flush=True)
        browser.close()
    content='// Generated presentation-only passages. Rebuild with tools/build-minimal-contexts.py.\nexport const minimalContexts = '+json.dumps(manifest,ensure_ascii=False,indent=2)+';\n'
    emit(SHARED/'minimal-contexts.js',content,args.verify)
    summary={'games':len(games),'questions':sum(g['questions'] for g in games),'engines':{e:sum(g['engine']==e for g in games) for e in sorted({g['engine'] for g in games})},'inventory':games}
    emit(ROOT/'docs/minimal-exam-ui/inventory.json',json.dumps(summary,ensure_ascii=False,indent=2)+'\n',args.verify)
    print('PASS inventory:',summary['games'],'games /',summary['questions'],'questions; source/payloads unchanged')
if __name__=='__main__':main()
