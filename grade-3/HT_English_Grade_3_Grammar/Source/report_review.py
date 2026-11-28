from pathlib import Path


REVIEW = Path(__file__).with_name('report-review.html')
GENERATED_DETAILS = r"""text('h3','Giải thích từng câu');for(const q of QUESTIONS){let a=STATE.answers[q.id];text('p',q.id+' – '+(!a?'Chưa trả lời':correct(q,a)?'Đúng':'Sai')+(a?' ('+a+')':'')+'\n'+q.explanation)}"""
SAMPLE_DETAILS = """text('h3','Giải thích các phần cần sửa');for(const q of QUESTIONS){let a=STATE.answers[q.id];if(!correct(q,a))text('p',q.id+' – '+(a||'Chưa trả lời')+'. Đáp án: '+(Array.isArray(q.ans)?q.ans.join(' / '):q.ans)+'. '+EXPLANATIONS[q.id])}"""


def with_report_review(html, sample=False):
    old_details = SAMPLE_DETAILS if sample else GENERATED_DETAILS
    explanation = 'EXPLANATIONS[q.id]' if sample else 'q.explanation'
    details = (
        "if(STATE.mode==='test'){"
        "const wrong=QUESTIONS.filter(q=>STATE.answers[q.id]&&!correct(q,STATE.answers[q.id]));"
        "appendWrongAnswerReview(body,wrong.map(q=>q.id+' – '+STATE.answers[q.id]"
        r"+'\nĐáp án: '+(Array.isArray(q.ans)?q.ans.join(' / '):q.ans)+'\n'+"
        f"{explanation}));"
        "}"
    )
    for old, new in [
        (old_details, details),
        ("$('report').showModal();$('report').scrollTop=0", "openWorksheetReport(STATE.mode)"),
        ('</script></html>', '</script>\n' + REVIEW.read_text(encoding='utf-8') + '</html>'),
    ]:
        if html.count(old) != 1:
            raise ValueError('Expected exactly one worksheet report marker')
        html = html.replace(old, new)
    return html
