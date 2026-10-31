"""Deterministic PDF text adapter; no generated academic content.

Run pdftotext -layout against the supplied PDFs first. Only PDF line wrapping,
page furniture and list/table layout are normalized. --verify never writes.
"""
from pathlib import Path
import hashlib, json, re, sys

UNIT = Path(__file__).resolve().parents[1] / 'unit-2-individuals-and-families'
def compact(text): return re.sub(r'\s+', ' ', text).strip()
def clean(name):
    text = (UNIT/'sources'/name).read_text()
    return '\n'.join(line for line in text.replace('\f', '\n').splitlines()
        if not re.match(r'^\s*(?:\d+\s+Prepared by|Trang \d+\s*$)', line))
source, key = clean('worksheet.txt'), clean('answer-key.txt')
review, rest = source.split('📚 Vocabulary Summary', 1)
passages = []
for block in re.split(r'🔹 Passage ', review)[1:]:
    heading, body = block.split('\n', 1)
    number, title = heading.split(': ', 1)
    text, vocabulary = body.split('Vocabulary:', 1)
    entries = []
    for raw in re.split(r'\s*', vocabulary)[1:]:
        raw = compact(raw)
        term, meaning = raw.split(' – ', 1)
        match = re.search(r' \(synonym: (.*)\)$', meaning)
        entries.append({'term': term, 'meaning': meaning[:match.start()] if match else meaning,
            **({'synonyms': match.group(1)} if match else {}), 'sourceText': raw})
    passages.append({'number': int(number), 'title': title, 'text': compact(text), 'vocabulary': entries})
vocab, reading = rest.split('READING PRACTICE', 1)
reading, multiple = reading.split('MULTIPLE CHOICE (10 QUESTIONS)', 1)
multiple, summary = multiple.split('SUMMARY COMPLETION (10 BLANKS)', 1)
summary, translation = summary.split('TRANSLATION (VIET → ENG)', 1)
questions = []
for block in re.split(r'(?m)^\s*(?=\d+\. )', multiple):
    if not block.strip(): continue
    parts = re.split(r'(?m)^([ABCD])\.\s*', block.strip())
    number, prompt = parts[0].strip().split('. ', 1)
    questions.append({'number': int(number), 'question': compact(prompt),
        'options': [{'value': parts[i], 'text': compact(parts[i+1])} for i in range(1, len(parts), 2)]})
instructions, summary = summary.split('SUMMARY', 1)
summary, bank = summary.split('WORD BANK', 1)
def paragraphs(text, starts):
    return [compact(p) for p in re.split(r'(?m)^(?='+'|'.join(map(re.escape, starts))+')', text) if p.strip()]
unit = {
    'id': 'unit-2-individuals-and-families', 'version': 1, 'number': 2,
    'title': 'Individuals and Families', 'heading': 'IELTS Vocabulary & Reading Practice',
    'passages': passages,
    'vocabularySummary': [compact(v) for v in re.split(r'\s*', vocab)[1:]],
    'reading': paragraphs(reading, ['Families play', 'In addition', 'Modern lifestyles', 'Despite these', 'Finally,']),
    'multipleChoice': questions,
    'summary': {'instructions': compact(instructions.split('Instructions:', 1)[1]),
        'paragraphs': paragraphs(summary, ['Families play', 'However,', 'Families also']),
        'wordBankText': compact(bank), 'wordBank': [v.strip() for v in compact(bank).split(' – ')]},
    'translation': {'instruction': 'Translate into English', 'text': compact(translation.split('Translate into English:', 1)[1])},
    'source': {'worksheet': 'sources/worksheet.pdf', 'answers': 'sources/answer-key.pdf',
        'credit': 'Prepared by Phạm Bá Đạt', 'printedPages': [12, 13, 14, 15, 16]}
}
mc, remaining = key.split('PHẦN 2. SUMMARY COMPLETION', 1)
answers = [{'number': int(n), 'answer': a, 'explanation': compact(e)}
    for n, a, e in re.findall(r'(?m)^\s*(\d+)\s+([ABCD])\s+([^\n]+)', mc)]
answer_table, remaining = remaining.split('Đoạn văn hoàn chỉnh:', 1)
summary_answers = [a for n, a in re.findall(r'(?m)^\s*(\d+)\s+([a-z]+)\s*$', answer_table)]
completed, remaining = remaining.split('Lưu ý về đề gốc:', 1)
note, remaining = remaining.split('PHẦN 3. TRANSLATION (VIETNAMESE → ENGLISH)', 1)
reference, glossary = remaining.split('Bài dịch tham khảo:', 1)[1].split('Cụm từ quan trọng:', 1)
terms = []
for line in glossary.splitlines():
    columns = re.split(r'\s{2,}', line.strip())
    if len(columns) == 2 and columns[0] != 'Tiếng Việt': terms.append({'vi': columns[0], 'en': columns[1]})
answer_key = {'multipleChoice': answers, 'summary': summary_answers,
    'completedSummary': paragraphs(completed, ['Families play', 'However,', 'Families also']),
    'sourceNote': 'Lưu ý về đề gốc: '+compact(note),
    'referenceTranslation': compact(reference), 'translationGlossary': terms}
assert len(passages) == 10 and sum(len(p['vocabulary']) for p in passages) == 33
assert len(unit['vocabularySummary']) == 33 and len(unit['reading']) == 5
assert len(questions) == 10 and all([o['value'] for o in q['options']] == list('ABCD') for q in questions)
assert [q['number'] for q in questions] == list(range(1, 11))
assert re.findall(r'__________\((\d+)\)', ' '.join(unit['summary']['paragraphs'])) == list(map(str, range(1, 11)))
assert [a['answer'] for a in answers] == list('BBCCBCBDCC')
assert summary_answers == ['behavior','support','support','relationships','distance','balance','traditions','wisdom','energy','conflicts']
assert len(unit['summary']['wordBank']) == 10 and unit['summary']['wordBank'].count('support') == 1
assert len(terms) == 10
manifest = {file.name: {'sha256': hashlib.sha256(file.read_bytes()).hexdigest(), 'bytes': file.stat().st_size}
    for file in sorted((UNIT/'sources').iterdir()) if file.suffix in ['.pdf', '.txt']}
for name, data in [('unit.json', unit), ('answers.json', answer_key), ('sources/integrity.json', manifest)]:
    text = json.dumps(data, ensure_ascii=False, indent=2)+'\n'
    if '--verify' in sys.argv:
        assert (UNIT/name).read_text() == text, f'{name} differs from extracted PDF text'
    else: (UNIT/name).write_text(text)
print('PASS: 10 passages / 33 vocabulary entries / 33 summary terms / 5 reading paragraphs / 10×4 MCQ / 10 blanks / 10 bank terms / translation and all key content matched')
