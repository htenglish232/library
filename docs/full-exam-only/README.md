# Chỉ giữ “Làm toàn bộ đề”

Phạm vi: **53 URL game**: 16 lớp 6, 14 lớp 7, 19 game có lưu tiến độ lớp 8 và 4 game lớp 8 đời cũ. Tổng cộng **2.212 câu** trên các URL đó (2.043 câu trong 49 game dùng bộ lưu tiến độ chung, 169 câu trong 4 game cũ).

Sau khi nhập tên hoặc xác nhận tiếp tục bài đã lưu, học sinh vào thẳng đề tại vị trí đang làm. Bộ chọn chế độ, menu và tab thử thách được gỡ khỏi DOM bởi engine chung; CSS che markup cũ trước khi engine khởi tạo. Không cần sửa từng launcher hoặc thay URL. Thanh tiến độ, danh sách/chuyển câu, tổng kết và ôn câu sai vẫn hoạt động. Các thẻ tổng kết theo phần chỉ trình bày số liệu, không mở lại luồng thử thách. Reading luôn hiện nội dung liên quan, giữ bố cục sticky/mobile và bỏ nút thu gọn.

## Dữ liệu và tương thích

- Không đổi câu hỏi, số lượng/thứ tự, dữ liệu đáp án, file audio/WAV, quy tắc chấm hoặc XP.
- Giữ nguyên `htenglish:practice:v1:`, khóa hồ sơ, `schemaVersion`, `examId` và `contentVersion`.
- Model nhận bản lưu cũ `mode: challenge` và `view: challenges`, chuẩn hóa thành `ordered`/`play`. Giữ toàn bộ `answers` (lần đầu, nháp, token, trường nhập, lượt ôn), cursor, danh sách ôn, tên/mã học sinh. Khi vào từ bản lưu tổng kết, engine mở câu đang làm; nút Kết quả vẫn mở tổng kết.
- XP vẫn suy ra từ kết quả lần đầu. Ôn lại, chuyển câu, mở tổng kết và tải lại không cộng thêm XP.
- Không liệt kê/xóa dữ liệu học sinh khác. Cơ chế phát hiện tab cũ, bản lưu hỏng, thiếu dung lượng và xác nhận reset được giữ.
- Bốn game đời cũ vẫn giữ mô hình tiến độ trong bộ nhớ như trước; không chuyển hay ghi đè localStorage của 49 game mới.
- Không đổi index, catalog, URL game, đăng nhập, Admin hoặc cấu hình/Rules Firebase. Giữ nguyên dữ liệu tên trong catalog/Firebase; khi index hiển thị, bỏ hậu tố “(2 chế độ)” khỏi tên game, kể cả bản lưu danh mục cũ.

## File ứng dụng

Trong `grade-8/De_thi_GHK1/shared-practice/`:

- `dual-mode-engine.js`: một luồng làm đề; bỏ điều khiển thử thách/thu gọn Reading; tiếp tục bản lưu cũ vào đúng câu.
- `dual-progress.js`: mặc định toàn đề, danh sách theo thứ tự gốc, nhận dữ liệu thử thách cũ.
- `dual-mode.css`: ẩn sớm markup cũ, bỏ CSS lựa chọn chế độ, định dạng tổng kết không tương tác.
- `engine.js`, `game.css`: áp dụng luồng toàn đề cho ba game pilot cũ.

Trong `grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-game/`:

- `game.js`, `game.css`: áp dụng cùng luồng cho game Trực Tuấn đời đầu, giữ dữ liệu/chấm điểm riêng của URL này.

`assets/school-folders.js` bỏ hậu tố chế độ ở tên hiển thị trên index, không sửa tên lưu trữ, URL, thứ tự hoặc trạng thái ẩn.

Các file còn lại là kiểm thử, CI, tài liệu và kiểm tra bảo toàn nguồn. Danh sách đầy đủ nằm trong [changed-files.txt](changed-files.txt). Các kiểm tra hash lịch sử chỉ miễn trừ chính xác controller/CSS/model được chủ đích sửa; đề, dữ liệu đáp án, audio, Firebase và index vẫn được bảo vệ.

## Chạy lại kiểm thử

Dùng Node 24, Java 21, Python 3.12, Playwright 1.58 và Chromium. Trong môi trường cloud đã chuẩn bị:

```bash
cd /workspace/library
export PATH=/workspace/.venvs/library/bin:$PATH
export XDG_CONFIG_HOME=/workspace/.config/library
export FIREBASE_EMULATORS_PATH=/workspace/.cache/firebase/emulators
npm run check:catalog
npm run test:prepare
node --test tests/dual-mode-progress.test.mjs tests/full-exam-migration.test.mjs tests/dual-mode-sound.test.mjs tests/grade6-dual.test.mjs tests/grade7-dual.test.mjs tests/grade8-all-dual.test.mjs
python3 tests/grade6-all-dual-browser.py
python3 tests/grade7-all-dual-browser.py
python3 tests/grade8-all-dual-browser.py
python3 tests/full-exam-legacy-browser.py
python3 tests/full-exam-migration-browser.py
python3 tests/dual-mode-browser.py
python3 tests/dual-mode-wav-browser.py
python3 tests/dual-mode-sound-loading-browser.py
python3 tests/dual-mode-sound-browser.py
python3 tests/grade6-cross-grade-browser.py
python3 tests/grade7-cross-grade-browser.py
python3 tools/test-emulators-official.py
```

Fixture `tests/fixtures/legacy-dual-progress.js` là model trước nâng cấp, cố định từ commit `26623fb`; không dùng model mới để giả tạo bản lưu cũ. Kiểm thử Node đối chiếu 49 × 4 trạng thái cũ; kiểm thử browser đối chiếu lại trên desktop và cảm ứng (392 lượt nâng cấp), gồm bài đang thử thách, trang tổng kết, nháp ôn và lượt ôn đã kiểm tra. Đọc bản lưu không tự reset; lưu lại hai lần không thay đáp án hoặc XP.

Kết quả chạy thực tế và giới hạn được ghi ở [verification.json](verification.json). Cảm ứng là mô phỏng Chromium, chưa phải thiết bị vật lý/Safari. Mở trực tiếp `file://` bị chính sách quản trị Chromium chặn; gói độc lập được kiểm thử qua HTTP. Không merge hoặc deploy.
