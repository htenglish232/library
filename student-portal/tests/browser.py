"""Real UI -> Auth Emulator -> Functions -> Firestore; no production traffic."""
import json, os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
BASE='http://127.0.0.1:5000'
OUT=Path('/tmp/ht-student-portal');OUT.mkdir(exist_ok=True)
credentials={r['studentId']:r['password'] for r in json.loads(Path(os.environ['PORTAL_TEST_CREDENTIALS']).read_text())}
checks=[];errors=[];external=[]
def passed(label):
    checks.append(label);print('PASS '+label,flush=True)
def login(page,id):
    page.locator('#student-id').fill(id);page.locator('#password').fill(credentials[id]);page.locator('#login-button').click()
    expect(page.locator('#display-name')).to_contain_text('Học sinh Demo')
    expect(page.locator('#dashboard-message')).to_be_empty()
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ['CHROMIUM_PATH'],args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce')
    def route(r):
        if r.request.url.startswith(('http://127.0.0.1:5000/','http://127.0.0.1:9099/')):r.continue_()
        else:external.append(r.request.url);r.abort()
    context.route('**/*',route)
    page=context.new_page();page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto(BASE+'/?assignment=truc-tuan-grade8-demo')
    expect(page.locator('#login-view')).to_be_visible();expect(page.locator('#dashboard-view')).to_be_hidden()
    page.screenshot(path=str(OUT/'login-desktop.png'),full_page=True)
    page.locator('#student-id').fill('HT0003');page.locator('#password').fill('wrong-password')
    with page.expect_response(lambda r: 'accounts:signInWithPassword' in r.url) as wrong_response:
        page.locator('#login-button').click()
    assert wrong_response.value.status==400
    expect(page.locator('#login-message')).to_contain_text('chưa đúng')
    passed('Anonymous users see login; wrong password rejected by Auth Emulator')
    page.reload();login(page,'HT0003')
    expect(page.locator('.assignment-card.highlight')).to_have_count(1)
    page.screenshot(path=str(OUT/'dashboard-desktop.png'),full_page=True)
    for width in [360,390,768]:
        page.set_viewport_size({'width':width,'height':850})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    page.set_viewport_size({'width':390,'height':850})
    page.screenshot(path=str(OUT/'dashboard-mobile.png'),full_page=True)
    passed('Teacher assignment survives reload/login; profile/avatar/level render without mobile overflow')
    page.locator('.assignment-card button').click()
    expect(page.locator('#game-message')).to_contain_text('Điểm luyện tập')
    game=page.frame_locator('#game-frame')
    expect(game.locator('#question-position')).to_have_text('Câu 1 / 42')
    # Answer every question via original controls, using the source grader's accepted
    # fixtures only for test input. No server state or receipt is mocked.
    data=page.frames[1].evaluate('HT_PRACTICE_DATA')
    orders={'q36':[3,5,1,0,2,4,6],'q37':[1,5,2,0,3,6,7,4,8],'q38':[1,6,2,0,3,7,4,5,8,9]}
    for index,q in enumerate(data['questions']):
        expect(game.locator('#question-card')).to_have_attribute('data-question-id',q['id'])
        if q['kind']=='choice':game.locator('#answer-area input[value="'+q['accepted'][0]+'"]').check()
        elif q['kind']=='text':game.locator('#written-answer').fill(q['accepted'][0])
        elif q['kind']=='multi-text':
            for i,value in enumerate(q['acceptedTuples'][0]):game.locator('#written-answer-'+str(i)).fill(value)
        else:
            for token in orders[q['id']]:game.locator('#word-bank button[data-token-index="'+str(token)+'"]').click()
        game.locator('#check-answer').click()
        if index<41:game.locator('#next-question').click()
    page.screenshot(path=str(OUT/'game-mobile.png'),full_page=True)
    passed('All 42 original questions answered using the original game controls and grader')
    # Drop a successful submit response to model loss of the network after commit.
    lost={'value':False}
    def lose_response(r):
        if not lost['value']:
            response=r.fetch();assert response.status==200;lost['value']=True;r.abort('failed')
        else:r.continue_()
    page.route('**/api/attempts/submit',lose_response)
    page.locator('#submit-attempt').click()
    expect(page.locator('#game-message')).to_contain_text('Bài chưa được xác nhận')
    page.locator('#submit-attempt').click()
    expect(page.locator('#receipt-view')).to_be_visible()
    expect(page.locator('#receipt-score')).to_contain_text('10/10')
    expect(page.locator('#receipt-stars')).to_contain_text('+5 sao')
    page.screenshot(path=str(OUT/'receipt-mobile.png'),full_page=True)
    page.locator('#receipt-home').click();expect(page.locator('#stars')).to_have_text('5')
    expect(page.locator('.history-row')).to_have_count(1)
    passed('Lost response retry preserves the same attempt/receipt and awards exactly five stars')
    page.unroute('**/api/attempts/submit',lose_response)
    page.locator('.assignment-card button').click();expect(page.locator('#game-message')).to_contain_text('Điểm luyện tập')
    game=page.frame_locator('#game-frame');expect(game.locator('#question-position')).to_have_text('Câu 1 / 42')
    page.locator('#submit-attempt').click();expect(page.locator('#receipt-view')).to_be_visible()
    expect(page.locator('#receipt-stars')).to_contain_text('không cộng thêm')
    page.locator('#receipt-home').click();expect(page.locator('.history-row')).to_have_count(2)
    expect(page.locator('#stars')).to_have_text('5')
    passed('Practice retake creates a separate history row and does not duplicate stars')
    page.locator('#logout').click();expect(page.locator('#login-view')).to_be_visible()
    login(page,'HT0002');expect(page.locator('#display-name')).to_have_text('Học sinh Demo B')
    expect(page.locator('#stars')).to_have_text('0')
    expect(page.locator('.history-row')).to_have_count(1)
    passed('Logout/login with another account clears the previous profile, rewards and game state')
    page.locator('#logout').click();expect(page.locator('#login-view')).to_be_visible()
    page.goto(BASE+'/?assignment=https%3A%2F%2Fevil.test')
    expect(page.locator('#login-message')).to_contain_text('không hợp lệ')
    assert page.url.startswith(BASE)
    page.set_viewport_size({'width':390,'height':850})
    page.screenshot(path=str(OUT/'login-mobile.png'),full_page=True)
    assert not errors,errors;assert not external,external
    (OUT/'browser-report.json').write_text(json.dumps({'checks':checks,'pageErrors':errors,'externalRequests':external},ensure_ascii=False,indent=2))
    browser.close()
print('PASS '+str(len(checks))+' browser groups; screenshots saved without credentials',flush=True)
