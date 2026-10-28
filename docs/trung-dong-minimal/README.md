# Thử giao diện tối giản — Trung Đông, lớp 8, đề 1

Chỉ áp dụng tại `grade-8/De_thi_GHK1/3_THCS Trung Dong/practice-dual-mode.html` (42 câu). Nhánh được tạo từ `main:7ebbe8a`, sau khi PR #43 đã được merge từ trước tác vụ này. Không merge hoặc deploy trong tác vụ.

## Giao diện

- Tên ngắn, bộ đếm câu, thanh tiến độ 4px; bỏ phần trang trí/giới thiệu dài khỏi màn hình làm bài.
- Lưới câu và bộ chọn câu nằm trong “Danh sách câu”, mặc định đóng và tự đóng sau khi chọn. Tên học sinh/XP được giữ; thao tác phụ ở “Tùy chọn”.
- Tái sử dụng chính thanh Câu trước/Câu tiếp hiện có, không tạo bộ nút thứ hai. Thanh cố định trong vùng hiển thị, có đệm nội dung, vùng bấm ≥44px và `safe-area-inset-bottom`. Viewport bổ sung `viewport-fit=cover` và `interactive-widget=resizes-content`.
- `visualViewport` xử lý trường hợp bàn phím thu nhỏ/pan vùng hiển thị: nâng thanh điều hướng lên trên bàn phím và giữ textarea đang nhập trong vùng còn trống. Chuyển câu đưa về vùng câu hỏi/đoạn đọc, không cuộn lên đầu toàn trang.
- Lời giải nguồn xuất hiện ngay sau Kiểm tra, giữ nguyên HTML nội dung đã có. Chỉ rút gọn nhãn trình bày. Nếu nguồn không có lời giải, hiện thông báo ngắn; không tạo thêm giải thích/dịch nghĩa.
- Dữ liệu nguồn gộp hai bài Reading trong một context. Adapter lấy nguyên khối đoạn văn của đúng phần `section-5` hoặc `section-6`, không hiển thị phần còn lại. Desktop chia cột, điện thoại đặt đoạn đọc trên câu hỏi; giữ scrollTop của đoạn đọc khi chuyển câu cùng đoạn.
- **Đề này chưa có tệp nghe gốc.** Giữ thông báo thiếu audio; không mượn file trường khác, tạo track giả hay thay nguồn. Markup và controller phát/tạm dừng, tua ±5s và tốc độ vẫn nguyên vẹn, CSS riêng chỉ thu gọn bố cục nếu có track hợp lệ. Hiệu ứng WAV được giữ.

## Cách cô lập

Chỉ launcher của đề được thêm `data-minimal-ui="trung-dong-1"`, CSS và JS riêng. JS còn kiểm tra chính xác `exam.id === grade8-ghk1-source-3`. Adapter chỉ thay DOM/bố cục, không gọi bộ chấm, bộ lưu, `localStorage` hoặc API Firebase; không sao chép engine.

Engine/CSS chung, dữ liệu đề/đáp án, XP, WAV, khóa/phiên bản lưu tiến độ, index và Firebase không đổi byte so với main. Bộ kiểm tra phạm vi đối chiếu toàn bộ file nguồn và 53 launcher: chỉ 1 bật thử nghiệm, 52 còn lại giữ nguyên. Builder Grade 8 tái tạo được launcher có cấu hình riêng. CI thêm kiểm thử pilot và hồi quy 52 game.

Các bộ browser dùng chung được bổ sung helper mở đúng disclosure của pilot khi cần thao tác, không thay hành vi kiểm thử của game khác. Kiểm tra context của pilot nằm trong suite riêng vì yêu cầu mới cố ý chỉ hiển thị một đoạn đọc thay cho cả phần Reading.

## Kiểm thử và giới hạn

Bằng chứng chi tiết: [verification.json](verification.json). Danh sách file: [changed-files.txt](changed-files.txt).

- Chromium desktop 1440×1000; mô phỏng viewport/cảm ứng iPhone 390×844 và Android 412×915. Mỗi profile làm đủ 42 câu, đối chiếu lời giải HTML nguồn, tổng điểm 390 XP với ba câu sai chủ đích; ôn lại không đổi điểm lần đầu. Có kiểm tra bản nháp/tải lại, thanh cố định khi cuộn, khoảng đệm cuối trang, Reading và lời giải trống.
- Kiểm thử thu nhỏ/pan visual viewport mô phỏng bàn phím, đo textarea và thanh điều hướng không giao nhau; đây **không phải kiểm tra bàn phím hệ điều hành trên điện thoại thật**.
- Chưa xác nhận Safari/iPhone thật. Tải WebKit bị proxy chặn 403 tại `cdn.playwright.dev` và `playwright.download.prss.microsoft.com`. Không tắt TLS/kiểm tra tải xuống để vượt qua lỗi.
- Đề không có track nghe, vì vậy không tuyên bố đã nghe thử Listening của đề Trung Đông. Bộ WAV chung kiểm tra âm đúng/sai/hoàn thành và chức năng Listening có sẵn ở game khác.
- Không gọi Firebase production, không đổi index hoặc các game khác.

Ảnh trước dùng HTML thật của main, cùng tên học sinh và kích thước màn hình; ảnh sau dùng pilot. Đây là ảnh từ trình duyệt mô phỏng, không phải ảnh chụp thiết bị vật lý.

| | Trước | Sau |
|---|---|---|
| iPhone — câu đầu | [Ảnh trước](before-iphone.png) | [Ảnh sau](after-iphone.png) |
| Android — câu đầu | [Ảnh trước](before-android.png) | [Ảnh sau](after-android.png) |
| Reading trên iPhone | | [Đúng đoạn văn](after-reading-iphone.png) |
| Giải thích trên iPhone | | [Lời giải nguồn](after-feedback-iphone.png) |

## Chạy lại

Từ thư mục gốc repository, dùng Node 24, Python 3.12, Playwright 1.58, Chromium và dependencies đã cài:

```bash
node --test tests/trung-dong-minimal.test.mjs
python3 tools/build-grade8-dual-games.py --verify
python3 tests/trung-dong-minimal-browser.py
python3 tests/trung-dong-unaffected-browser.py
python3 tests/grade8-all-dual-browser.py --folders 3
python3 tests/dual-mode-wav-browser.py
```

Kết quả/ảnh mới được tạo dưới `/tmp/trung-dong-minimal`; bộ kiểm thử không ghi lại tiến độ của học sinh thật.
