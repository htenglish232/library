"""Regression: a missing name must not make the next submission unusable.

Run with Python Playwright and Chromium installed:
  python3 grade-7/De_thi_GHK_1/tests/submission_name_checks.py
No production requests; all interactions use the visible exam controls.
"""
import argparse
import functools
import http.server
import json
import os
from pathlib import Path
import re
import threading
from urllib.parse import quote

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[3]
EXAMS = ROOT / 'grade-7' / 'De_thi_GHK_1'


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def copyfile(self, source, output):
        try:
            super().copyfile(source, output)
        except (BrokenPipeError, ConnectionResetError):
            pass  # A browser may stop an audio download when closing a page.


def check_exam(browser, path, base):
    context = browser.new_context(viewport={'width': 390, 'height': 844})
    context.route('**/*', lambda route: route.continue_()
                  if route.request.url.startswith(base) else route.abort())
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    try:
        page.goto(base + quote(str(path.relative_to(ROOT))), wait_until='load')
        data = json.loads(page.locator('#examData').text_content())
        choice = next(q for q in data['questions'] if q['kind'] == 'choice')
        answer = page.locator('#question-' + choice['id'] +
                              ' input[value="' + choice['accepted'][0] + '"]')
        answer.check()
        writing = page.locator('.question-card input:not([type=radio])[data-answer-field], .question-card textarea[data-answer-field]').first
        writing.fill('Bài viết đang làm thử')
        chip_card = page.locator('.question-card').filter(has=page.locator('.bank-chip')).first
        chip_card.locator('.bank-chip').nth(0).click()
        selected_words = chip_card.locator('.selected-chip').all_text_contents()
        name = page.locator('#studentName')
        modal = page.locator('#confirmModal')

        def assert_answers_preserved():
            expect(answer).to_be_checked()
            expect(writing).to_have_value('Bài viết đang làm thử')
            assert chip_card.locator('.selected-chip').all_text_contents() == selected_words

        def reject_missing_name(value):
            name.fill(value)
            page.locator('#submitBtn').click()
            expect(page.locator('#htIdentityMessage')).to_have_text(
                'Em vui lòng nhập đầy đủ họ và tên trước khi nộp bài nhé!')
            expect(name).to_be_focused()
            expect(name).to_be_enabled()
            expect(page.locator('#submitBtn')).to_be_enabled()
            assert not modal.evaluate('(dialog) => dialog.open')
            assert page.locator('.feedback-box:visible').count() == 0
            assert page.evaluate('HTSubmission.attempt') is None
            assert_answers_preserved()

        def open_valid_confirmation():
            name.fill('  Nguyễn   Minh Anh  ')
            page.locator('#studentClass').fill(' 7A ')
            page.locator('#submitBtn').click()
            expect(modal).to_be_visible(timeout=1500)
            expect(page.locator('#confirmSubmit')).to_be_visible()
            expect(page.locator('#confirmMessage')).to_contain_text('chưa hoàn thành')
            assert_answers_preserved()

        # This sequence failed before the fix: the closed native dialog gained .hidden.
        reject_missing_name('')
        open_valid_confirmation()
        page.locator('#continueExam').click()
        expect(modal).not_to_be_visible()
        assert_answers_preserved()
        reject_missing_name(' \t\u00a0 ')
        open_valid_confirmation()

        # Revalidate at the final click if the field is cleared while confirming.
        name.evaluate('(input) => input.value = "   "')
        page.locator('#confirmSubmit').click()
        expect(name).to_be_focused()
        expect(name).to_be_enabled()
        expect(modal).not_to_be_visible()
        assert page.evaluate('HTSubmission.attempt') is None
        assert_answers_preserved()
        open_valid_confirmation()
        page.locator('#confirmSubmit').click()

        expect(page.locator('#examResults')).to_be_visible()
        expect(page.locator('#htIdentitySummary')).to_be_visible()
        expect(page.locator('#submissionBanner')).to_be_visible()
        expect(page.locator('#htIdentityReview')).to_be_visible()
        expect(name).to_have_value('Nguyễn Minh Anh')
        expect(name).to_be_disabled()
        expect(page.locator('#submitBtn')).to_be_disabled()
        expect(writing).to_be_disabled()
        assert_answers_preserved()
        assert page.locator('.feedback-box:visible').count() == len(data['questions'])
        assert page.locator('.status-indicator:visible').count() == len(data['questions'])
        record = page.evaluate('HTSubmission.attempt')
        assert float(record['score']) == choice['points'], (record, choice)
        assert record['name'] == 'Nguyễn Minh Anh' and record['studentClass'] == '7A'
        assert record['id'].startswith('HT7-')
        expect(page.locator('#examResults h2')).to_contain_text(record['score'].rstrip('0'))
        assert page.locator('[data-transcript]:visible').count() == page.locator('[data-transcript]').count()
        for width in (360, 390, 768):
            page.set_viewport_size({'width': width, 'height': 844})
            assert page.locator('#htIdentitySummary').evaluate(
                '(panel) => panel.scrollWidth <= panel.clientWidth + 1')
        page.evaluate('HTSubmission.render()')
        assert page.evaluate('HTSubmission.attempt') == record
        assert not errors, errors
        print('PASS', path.name, ': name retry, preserved answers, score and all explanations', flush=True)
    finally:
        context.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', help='Run a single filename instead of all Grade 7 exams.')
    args = parser.parse_args()
    paths = sorted(EXAMS.glob('*/*.html'))
    if args.file:
        paths = [path for path in paths if path.name == args.file]
    assert paths, 'No selected exams'
    server = http.server.ThreadingHTTPServer(
        ('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}/'
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'),
                args=['--no-sandbox'])
            try:
                for path in paths:
                    check_exam(browser, path, base)
            finally:
                browser.close()
        print(f'PASS {len(paths)} Grade 7 exams')
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    main()
