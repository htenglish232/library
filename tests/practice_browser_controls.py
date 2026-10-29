"""Use the pilot's real disclosure controls when a shared browser suite needs them."""
def control(page, selector):
    if page.locator('html[data-minimal-ui]').count():
        page.wait_for_function('document.documentElement.dataset.minimalReady === "true" || !document.documentElement.dataset.minimalUi')
    target=page.locator(selector)
    if target.count() and not target.first.is_visible():
        details=target.first.locator('xpath=ancestor::details[1]')
        if details.count() and details.is_visible() and details.get_attribute('open') is None:
            details.locator(':scope > summary').click()
    return target

_contexts=None
def assert_context(page, question, data):
    """Compare display text/markup to the independently source-built passage map."""
    global _contexts
    if _contexts is None:
        from pathlib import Path
        import subprocess,json
        root=Path(__file__).resolve().parents[1]
        _contexts=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import {minimalContexts} from './grade-8/De_thi_GHK1/shared-practice/minimal-contexts.js'; console.log(JSON.stringify(minimalContexts));"],cwd=root,text=True))
    metadata=_contexts[data.get('exam',{}).get('id','legacy-truc-tuan')]
    index=metadata['byQuestion'].get(question['id'])
    panel=page.locator('#passage-panel')
    if index is None:
        assert panel.is_hidden(),question['id']
        return
    expected=metadata['passages'][index]
    normalized=page.evaluate('html=>{const e=document.createElement("div");e.innerHTML=html;return e.innerHTML;}',expected)
    actual=page.locator('#passage-content').evaluate('el=>{const e=el.cloneNode(true);e.querySelectorAll("mark.minimal-blank").forEach(m=>m.replaceWith(...m.childNodes));return e.innerHTML;}')
    assert actual==normalized,(data.get('exam',{}).get('id'),question['id'],'source passage differs')
    assert panel.is_visible()
    marker=metadata['clozeMarkers'].get(question['id'])
    marks=page.locator('#passage-content mark.minimal-blank')
    if marker:
        assert marks.count()==1,(data.get('exam',{}).get('id'),question['id'],'missing exact blank highlight')
        assert marks.text_content().replace(' ','')==f'({marker})'
    else:assert marks.count()==0
