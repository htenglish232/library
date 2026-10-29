# Giao diện tối giản cho toàn bộ game lớp 6, 7, 8

Nhánh `feature/minimal-exam-ui-all-grades`, xuất phát từ `main` tại `3691356b835db21d787824510491c261b6505e99` (đã kiểm tra lại remote trước khi commit). Không merge hoặc deploy.

## Kiểm kê và phạm vi

| Khối | Game được tìm thấy và cập nhật | Câu hỏi |
| --- | ---: | ---: |
| 6 | 16 | 661 |
| 7 | 14 | 589 |
| 8 | 23 | 962 |
| Tổng | **53** | **2.212** |

[Kiểm kê từng URL, engine, nguồn và bằng chứng Reading](inventory.json). 49 game dùng `dual-mode-engine.js`; ba pilot Trực Khang, Trực Hùng, Trực Chính lớp 8 dùng `engine.js`; bản Trực Tuấn cũ dùng `truc-tuan-game/game.js`. Cả bốn URL đời cũ vẫn hoạt động và dùng chung lớp trình bày mới. Ba pilot trùng mã đề với bản mới nên bản đồ đoạn đọc có 50 mã đề cho 53 URL.

## Thay đổi

- Thêm `shared-practice/minimal-ui.js` và `minimal-ui.css`: đầu trang gọn, số câu, tiến độ mỏng, âm thanh; danh sách câu đóng mặc định bằng `details/summary`, hỗ trợ bàn phím, đóng sau khi chọn. Công cụ tên học sinh, kết quả, ôn sai và làm lại vẫn truy cập được.
- Tái sử dụng thanh chuyển câu hiện có thành một thanh cố định duy nhất, nút ít nhất 44px, có khoảng đệm theo chiều cao thực tế và safe area. Theo dõi `visualViewport` để xử lý bàn phím; chuyển câu cuộn tới nội dung, không tự cuộn khi mở bài.
- Kết quả và lời giải nguồn hiện ngay trong luồng câu hỏi. Không tạo lời giải hoặc bản dịch. Câu chờ giáo viên duyệt có nhãn rõ ràng; phần hỗ trợ chưa xác minh không được trình bày như lời giải chính thức. Câu thiếu lời giải có thông báo ngắn, không ảnh hưởng chấm điểm.
- `minimal-contexts.js` được sinh từ HTML nguồn bằng `tools/build-minimal-contexts.py` và `minimal-context-source.js`. Chỉ đưa đúng đoạn liên quan, giữ tiêu đề, nội dung và thứ tự, bảo toàn cấu trúc hình/bảng nếu có. Khôi phục đoạn đọc có trong HTML gốc nhưng bị thiếu ở context trình bày cũ của Trực Cường lớp 6; không sửa payload đề. Desktop hai cột; mobile đoạn đọc trước câu hỏi; giữ vị trí cuộn cùng đoạn. Chỉ 236 vị trí có nhãn chỗ trống xác định chính xác được tô sáng, không đoán vị trí còn lại.
- Trình nghe được đặt gần câu hỏi, giữ handler phát/dừng, ±5 giây và tốc độ. Không tự phát, không đổi file nghe/WAV. Những đề vốn thiếu audio giữ thông báo gốc.
- Ba controller chỉ thêm bootstrap trình bày; CSS riêng Trực Tuấn và asset pilot Trung Đông trở thành shim dùng chung, không sao chép engine. Bỏ ngoại lệ pilot khỏi builder lớp 8; gói preview HTTP chứa đủ asset mới.

## Bảo toàn dữ liệu

Kiểm thử so sánh byte với main xác nhận câu hỏi, đáp án, nguồn đề, audio, WAV, model XP/localStorage, index/catalog, Firebase và các khối khác không đổi. Controller sau khi bỏ bootstrap mới giống nguyên bản. Không đổi schema hoặc phiên bản nội dung, không ghi lại localStorage từ module trình bày.

49 game có lưu localStorage giữ nguyên cơ chế cũ; bốn game đời cũ vốn chỉ lưu trong phiên vẫn giữ cơ chế đó, không được tuyên bố có thêm lưu lâu dài. 392 trường hợp được tạo bằng model cũ đóng băng gồm dữ liệu cả chế độ thử thách trước đây; sau nâng cấp giữ đáp án đầu, bản nháp, XP, câu hiện tại và ôn sai. Không khôi phục giao diện thử thách.

Hai payload pilot cũ có `sourceSha256` lịch sử khác nguồn hiện tại ngay từ main. Giữ nguyên cả payload và nguồn; inventory ghi riêng SHA nguồn hiện tại và SHA payload để truy nguyên, không sửa siêu dữ liệu học thuật cũ.

## Kết quả kiểm thử

| Nhóm | Kết quả |
| --- | --- |
| Toàn bộ câu hỏi | 53 game / 2.212 câu; thứ tự, chấm điểm, điều hướng, kết quả, ôn sai: PASS |
| Responsive | 53 × 7 = 371 trường hợp tại 375, 390, 360, 412, 768, 1280, 1440px: PASS |
| Reading | 534 câu, 236 chỗ trống xác định được; đúng đoạn, không thu gọn, giữ vị trí: PASS |
| Bản lưu cũ | 49 × 4 kịch bản × desktop/touch = 392: PASS |
| Node | 46 kiểm thử model, migration, âm thanh và bảo toàn dữ liệu: PASS |
| Prepare/catalog | 41 kiểm thử; catalog 261 mục: PASS |
| Builder | Lớp 6/7/8 và context `--verify`: PASS |
| WAV | 49 game trên desktop và touch; 10 nhóm kiểm tra âm thanh/lỗi/hủy: PASS |
| Nạp âm thanh và sine fallback | 9 nhóm mỗi bộ: PASS |
| Hồi quy khác | Golden 42 câu, tab xung đột, store lỗi/quota, gói preview HTTP; đổi chéo khối; Trung Đông 42 câu × 3 viewport: PASS |

Ma trận responsive kiểm tra câu hỏi xuất hiện sớm với scrollY ban đầu bằng 0, danh sách đóng, một thanh cố định, nút đủ lớn, không tràn ngang/che nội dung, không autoplay, điều hướng, Reading, Writing và mô phỏng hình học bàn phím. Không phát hiện lỗi JS hoặc tài nguyên HTTP trong luồng bình thường. Các tình huống tiêm lỗi tài nguyên có kiểm tra fallback riêng.

**Giới hạn:** Đây là Chromium mô phỏng viewport/touch, không phải iPhone/Android thật. Bàn phím dùng mô phỏng thay đổi `visualViewport`; chưa xác nhận thanh địa chỉ/bàn phím trên Safari thiết bị thật. Không tải được WebKit do proxy mạng. Kiểm tra mở gói bằng `file://` bị chính sách Chromium chặn và được bỏ qua rõ ràng; gói offline qua HTTP đã chạy. Không chạy lại emulator Firebase trong nhiệm vụ này; Firebase không đổi. Không có game bình thường nào còn lưới câu mở sẵn hoặc thanh điều hướng che nội dung trong ma trận đã chạy.

[Chi tiết số liệu máy đọc](verification.json) · [Danh sách đầy đủ file thay đổi](changed-files.txt).

## Ảnh trước/sau

Ảnh trước chụp trên main gốc; ảnh sau cùng tên học sinh thử nghiệm, cùng URL/kích thước. Mobile 390×844, desktop 1440×1000. Các trường mẫu: Trực Tuấn lớp 6, Trực Thái lớp 7, Cát Thành lớp 8.

| Khối | Mobile trước → sau | Desktop trước → sau | Reading mobile / desktop | Kết quả và lời giải mobile / desktop |
| --- | --- | --- | --- | --- |
| 6 | [Trước](before-grade6-mobile.png) → [Sau](after-grade6-mobile.png) | [Trước](before-grade6-desktop.png) → [Sau](after-grade6-desktop.png) | [Mobile](after-reading-grade6-mobile.png) / [Desktop](after-reading-grade6-desktop.png) | [Mobile](after-feedback-grade6-mobile.png) / [Desktop](after-feedback-grade6-desktop.png) |
| 7 | [Trước](before-grade7-mobile.png) → [Sau](after-grade7-mobile.png) | [Trước](before-grade7-desktop.png) → [Sau](after-grade7-desktop.png) | [Mobile](after-reading-grade7-mobile.png) / [Desktop](after-reading-grade7-desktop.png) | [Mobile](after-feedback-grade7-mobile.png) / [Desktop](after-feedback-grade7-desktop.png) |
| 8 | [Trước](before-grade8-mobile.png) → [Sau](after-grade8-mobile.png) | [Trước](before-grade8-desktop.png) → [Sau](after-grade8-desktop.png) | [Mobile](after-reading-grade8-mobile.png) / [Desktop](after-reading-grade8-desktop.png) | [Mobile](after-feedback-grade8-mobile.png) / [Desktop](after-feedback-grade8-desktop.png) |

Ảnh Writing: [lớp 6 mobile](after-writing-grade6-mobile.png) / [desktop](after-writing-grade6-desktop.png), [lớp 7 mobile](after-writing-grade7-mobile.png) / [desktop](after-writing-grade7-desktop.png), [lớp 8 mobile](after-writing-grade8-mobile.png) / [desktop](after-writing-grade8-desktop.png).

[Báo cáo gốc responsive](reports/smoke-375-390-360-412.json), [tablet/desktop](reports/smoke-768-1280-1440.json), [Reading](reports/reading.json), [bản lưu cũ](reports/old-save-migration.json), [46 kiểm thử Node](reports/final-complete-node.log).

## Chạy lại

Cài `npm ci`, Python Playwright và Chromium (CI dùng Playwright 1.58.0). Các bài browser tự mở HTTP server nội bộ. Không cần Firebase production.

```sh
python3 tools/build-grade6-dual-games.py --verify
python3 tools/build-grade7-dual-games.py --verify
python3 tools/build-grade8-dual-games.py --verify
python3 tools/build-minimal-contexts.py --verify
node --test tests/full-exam-migration.test.mjs tests/minimal-exam-ui.test.mjs tests/dual-mode-progress.test.mjs tests/dual-mode-sound.test.mjs
npm run test:prepare
npm run check:catalog
python3 tests/grade6-all-dual-browser.py
python3 tests/grade7-all-dual-browser.py
python3 tests/grade8-all-dual-browser.py
python3 tests/full-exam-legacy-browser.py
python3 tests/minimal-exam-smoke-browser.py
python3 tests/minimal-reading-browser.py
python3 tests/full-exam-migration-browser.py
python3 tests/dual-mode-wav-browser.py
python3 tests/dual-mode-sound-loading-browser.py
python3 tests/dual-mode-sound-browser.py
python3 tests/dual-mode-browser.py
python3 tests/grade6-cross-grade-browser.py
python3 tests/grade7-cross-grade-browser.py
python3 tests/trung-dong-minimal-browser.py
```

Workflow `grade8-dual-mode-checks.yml` thêm verify metadata, bảo toàn dữ liệu, responsive toàn bộ và Reading; giữ các kiểm thử hiện có, tải báo cáo artifact. Workflow này không deploy.
