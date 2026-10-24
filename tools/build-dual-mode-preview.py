"""Package a fresh, offline review folder. No deployment and no learner records."""
from pathlib import Path
from urllib.parse import quote
import base64, hashlib, json, shutil, sys
ROOT=Path(__file__).resolve().parents[1]
target=Path(sys.argv[1]).resolve()
if target.exists():raise SystemExit('Choose a fresh preview directory; existing files are never deleted.')
target.mkdir(parents=True)
school='grade-8/De_thi_GHK1/1_THCS Truc Tuan/'
shared='grade-8/De_thi_GHK1/shared-practice/'
files=[school+name for name in ['truc-tuan-dual-mode.html','truc-tuan-dual-data.js','truc-tuan-dual-support.js','1. THCS Truc Tuan.html','GHK1 K8 - part 1.mp3','GHK1 K8 - part 2 .mp3']]
files += [shared+name for name in ['model.js','game.css','icon.svg','dual-progress.js','dual-store.js','dual-mode-engine.js','dual-mode.css']]
files += ['grade-7/De_thi_GHK_1/fonts/'+name for name in ['noto-sans-latin-400-normal.woff2','noto-sans-vietnamese-400-normal.woff2','noto-sans-latin-700-normal.woff2','noto-sans-vietnamese-700-normal.woff2','OFL.txt']]
for file in files:
    dest=target/file;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/file,dest)
# Embed fonts only in the preview copy, avoiding file-origin font restrictions.
css=target/shared/'game.css';text=css.read_text()
for file in files:
    if file.endswith('.woff2'):
        text=text.replace('../../../'+file,'data:font/woff2;base64,'+base64.b64encode((ROOT/file).read_bytes()).decode())
css.write_text(text)
url=quote(school+'truc-tuan-dual-mode.html')
(target/'MO_GAME.html').write_text(f'<!doctype html><html lang="vi"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={url}"><title>Mở game Trực Tuấn</title><a href="{url}">Mở game Trực Tuấn hai chế độ</a></html>')
(target/'index.html').write_text(f'''<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HT English · Bản xem thử</title><style>body{{font:18px Arial,sans-serif;max-width:650px;margin:50px auto;padding:20px;color:#123750;background:#f3f9ff}}a{{display:inline-block;background:#087eae;color:white;padding:16px;border-radius:12px;text-decoration:none}}</style><h1>HT English · Game Trực Tuấn</h1><p>Bản xem thử Giai đoạn 1: 42 câu, hai chế độ và lưu tiến độ trên thiết bị.</p><p>Giải nén toàn bộ thư mục rồi mở MO_GAME.html bằng Chrome hoặc Edge. Không cần cài thêm phần mềm hay chạy lệnh.</p><a href="{url}">Mở game →</a><p>Bản xem thử độc lập với website. Tiến độ ở bản này không tự chuyển lên website. Các bạn trùng họ tên nên thêm mã riêng.</p></html>''')
manifest={file:hashlib.sha256((target/file).read_bytes()).hexdigest() for file in files}
(target/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Offline preview prepared:',target)
