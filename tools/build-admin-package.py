"""Build the small Windows preview package from reviewed local sources; no network."""
import hashlib, json, pathlib, subprocess, zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
NAME = 'HT-English-Admin-thu-nghiem-Windows'
files = {}
for relative in ['admin.html', 'index.html', 'catalog/library-catalog.json']:
    files[relative] = (ROOT / relative).read_bytes()
for path in sorted((ROOT / 'assets').glob('*')):
    if path.is_file(): files[str(path.relative_to(ROOT))] = path.read_bytes()
for name in ['MO_ADMIN.py', 'MO_ADMIN_WINDOWS.cmd']:
    files[name] = (ROOT / 'tools/windows' / name).read_bytes()
files['HUONG_DAN_WINDOWS.txt'] = (ROOT / 'tools/windows/HUONG_DAN_WINDOWS.txt').read_bytes()
manifest = {
    'branch': subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip(),
    'sourceCommit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'projectId': 'ht-english-library',
    'scope': 'Local Admin preview; no automatic Firebase writes; proposed upgrade requires approval.',
    'files': {name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())}
}
files['MANIFEST.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()
output = ROOT / 'downloads' / (NAME + '.zip')
output.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
    for name, data in sorted(files.items()):
        entry = zipfile.ZipInfo(NAME + '/' + name, date_time=(2026, 10, 10, 0, 0, 0))
        entry.compress_type = zipfile.ZIP_DEFLATED
        entry.external_attr = 0o644 << 16
        archive.writestr(entry, data)
with zipfile.ZipFile(output) as archive:
    assert archive.testzip() is None
    for name, data in files.items(): assert archive.read(NAME + '/' + name) == data
checksum = hashlib.sha256(output.read_bytes()).hexdigest()
readme = f'''# Gói Admin thử nghiệm Windows

Gói được tạo từ mã nguồn commit `{manifest['sourceCommit']}` trên nhánh `{manifest['branch']}`; giao diện hỗ trợ quản lý danh mục linh hoạt, sao lưu/khôi phục và lưu có kiểm tra phiên bản. Cấu hình dự án Firebase thật được giữ; mở trang không tự ghi dữ liệu.

Tải `{NAME}.zip`, chọn **Extract All**, rồi chạy `MO_ADMIN_WINDOWS.cmd`. Máy cần Python 3; không cần Node.js/Firebase CLI. Đọc `HUONG_DAN_WINDOWS.txt` và [hướng dẫn nâng cấp](../QUAN_LY_DANH_MUC_VA_TRIEN_KHAI.md).

Chưa Publish Rules hoặc triển khai Pages trong lần chuẩn bị này. Không nhấn Lưu hoặc thay đổi quyền trên Firebase thật trước khi được phê duyệt. Nếu Rules cũ chỉ CREATE đang hoạt động, thao tác chỉnh sửa sẽ bị từ chối. Công cụ nhập gốc vẫn chỉ tạo mới 201 mục và dừng nếu tài liệu đã tồn tại.

Gói nhỏ không chứa bài tập/audio. Chỉ dùng giao diện để thử Admin; bài tập hiện tại trên GitHub Pages giữ nguyên. Không chứa mật khẩu hoặc khóa Admin SDK.

SHA-256 ZIP: `{checksum}`.

Tạo lại gói bằng `python3 tools/build-admin-package.py` sau khi commit mã nguồn đã kiểm thử; không thực hiện thao tác mạng hoặc Firebase.
'''
(output.parent / 'README.md').write_text(readme, encoding='utf-8')
print(f'Package verified: {output.name} ({output.stat().st_size} bytes); SHA-256 {checksum}')
