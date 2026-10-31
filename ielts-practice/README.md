# IELTS Vocabulary & Reading Practice

Nhánh review: `feature/ielts-unit2-worksheet`. URL dự kiến trong cùng Library: `/library/ielts-practice/unit-2-individuals-and-families/`. Chưa merge hoặc triển khai production.

## Xem thử

Chạy từ gốc repository:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Mở `http://localhost:8000/ielts-practice/`, chọn Unit 2. Bản chính cần HTTP(S) để tải JSON/module. Không dùng `file://` cho `index.html` gốc.

Để xem bằng một tệp HTML có thể tải xuống và mở trực tiếp trong Chrome/Edge:

```sh
python3 ielts-practice/tests/build-preview.py
```

Mở `/tmp/ielts-unit2-preview.html`. Tệp review nhúng dữ liệu, CSS, font và mã để không cần server. Đáp án chỉ xuất hiện trong giao diện sau nộp; đây là phiếu luyện tập phía client, không phải cơ chế bảo mật đáp án của kỳ thi. Các đường dẫn nguồn/Library trong bản review dẫn về GitHub/trang Library. Bản HTML preview được sinh từ đúng mã và dữ liệu chính, không sửa thủ công.

Workflow **IELTS Unit 2 checks and downloadable preview** chạy trên nhánh/PR, tải artifact `ielts-unit2-preview-open-in-browser` và ảnh/báo cáo trình duyệt. Tải artifact, giải nén, mở HTML. Workflow chỉ có quyền đọc và không có bước deploy. Repository chưa có dịch vụ preview hosting riêng cho nhánh; không coi URL GitHub Pages production là bản xem thử.

## Sử dụng

Nhập tên, bắt đầu với phần A; chọn từng phần/câu qua danh sách đóng mặc định hoặc dùng Previous/Next. Đáp án và bản dịch tham khảo chỉ mở sau nộp. Summary cho nhập lại từ; chấm sau khi trim và chuyển chữ thường, không chấp nhận synonym. Kết quả tách đúng/sai/bỏ trống trên 20 câu; tỷ lệ hoàn thành tính số câu MCQ/Summary đã trả lời. Translation có đếm từ, lưu nháp, giữ nguyên khi chuyển phần và không tự chấm.

Ôn câu cần luyện tạo bản nháp riêng trong phiên, gồm cả câu bỏ trống, không ghi đè bài nộp hay điểm lần đầu. Có thể xem lại toàn bộ bài làm đã khóa, lời giải MCQ, đoạn Summary hoàn chỉnh, lưu ý nguồn và bản dịch tham khảo. Lượt mới yêu cầu xác nhận vì thay thế bản lưu hiện tại.

Lưu tự động dùng duy nhất namespace `ht-ielts:worksheet:v1:unit-2-individuals-and-families`. Không dùng Firebase hoặc khóa GHK1/Speaking; không gửi tên, bài làm hay kết quả đến dịch vụ ngoài. Nếu bộ nhớ không khả dụng, có cảnh báo; không hứa lưu thành công. Tiến độ gắn với trình duyệt/origin, không tự đồng bộ sang thiết bị khác. Phiên ôn sai không lưu qua tải lại; bài nộp gốc vẫn được bảo toàn.

## Cấu trúc và mở rộng

- `index.html`: danh sách các Unit đã có nội dung.
- `shared/worksheet.js`, `model.js`, `worksheet.css`: controller, mô hình chấm/lưu và giao diện dùng chung.
- `unit-2-individuals-and-families/unit.json`: chỉ nội dung đề; `answers.json`: đáp án và nội dung sau nộp.
- `sources/`: hai PDF nguyên bản, văn bản trích xuất và hash.
- `docs/source-audit.md`: đối chiếu từng phần và hai lưu ý giáo viên đã xác nhận giữ nguyên.
- `tests/`: kiểm thử nguồn, mô hình, trình duyệt và công cụ tạo preview; không đóng gói lên site.

Unit sau có thể thêm thư mục với cùng hợp đồng dữ liệu và HTML trỏ tới `shared/`, thêm thẻ ở `ielts-practice/index.html`; không hiển thị Unit trống. Engine hiện triển khai đúng cấu trúc 10 MCQ + 10 ô Summary của Unit 2; nếu số lượng hoặc loại câu khác cần mở rộng schema/kiểm thử tương ứng, không đoán nội dung.

Đã tham khảo GHK1 `dual-mode-engine.js`, `dual-mode.css`, `minimal-ui.js`, `minimal-ui.css` và `docs/minimal-exam-ui/README.md`. Kế thừa cách trình bày gọn, danh sách câu đóng, hai cột Reading desktop, thanh điều hướng có khoảng đệm và xử lý `visualViewport`. Không nhập nguyên bộ chấm/XP GHK1 vì phiếu này chỉ chấm sau nộp và có quy tắc Summary/Translation riêng. Font Noto Sans đã có và có giấy phép trong `test-speaking/fonts/OFL`; chỉ tham chiếu, không sửa tài nguyên Speaking.

## Kiểm tra lại

```sh
python3 ielts-practice/tests/source-pdf.py
node --test ielts-practice/tests/model.test.mjs
python3 ielts-practice/tests/browser.py
python3 ielts-practice/tests/build-preview.py
python3 ielts-practice/tests/navigation-preview.py
npm run test:prepare
npm run check:catalog
```

Cần Poppler (`pdfinfo`, `pdftotext`), Node, Python Playwright 1.58.0 và Chromium; `CHROMIUM_PATH` hoặc `browser.py --browser-path` chọn binary đã cài. Không cần quyền Firebase hay token API.

Bằng chứng nghiệm thu, ảnh chụp và giới hạn: [docs/validation.md](docs/validation.md).
