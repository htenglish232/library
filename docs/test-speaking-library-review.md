# Review Test Speaking trong HT English Library

Nhánh: `feature/test-speaking-library`; base PR: `main`. Không merge hoặc chạy workflow deploy production trước khi chủ dự án xác nhận.

## Giao diện và đường dẫn

1. Library chính vẫn giữ đăng nhập, các Grade và danh mục hiện tại. Sau đăng nhập, mục **Test Speaking** nằm phía trên các tab Grade.
2. Mở **Test Speaking → Grade 3 → Global Success → Unit 5 → Speaking Cards**.
3. Chọn **Practice**, **Sequential Test** hoặc **Random Test**. Khi kiểm tra, chọn 14 thẻ hoặc 5 thẻ Unit 5 Core.
4. Trong phiên, Previous/Next giữ thứ tự và thanh chuyển câu cố định. Có nút fullscreen, về danh sách Unit, về danh sách Grade và Library chính.
5. Tìm kiếm/lọc mở nhanh các bộ. Grade/giáo trình/Unit không có nội dung không xuất hiện. Bộ demo Speaking Practice cũ vẫn được giữ ở Grade 3, tách khỏi Unit 5.

Đường dẫn mới: `test-speaking/index.html`; hỗ trợ prefix `/library/test-speaking/`. `speaking-cards/index.html` chuyển tiếp tương đối tới trang mới. Không tạo repository hoặc website riêng.

## Preview không deploy production

Repository hiện chỉ có workflow deploy GitHub Pages thủ công từ main với chuỗi xác nhận. Workflow đó không được sửa hoặc chạy trong thay đổi này. Chưa có cấu hình deploy URL riêng cho từng PR trong repository.

Workflow mới **Test Speaking checks and downloadable preview** chạy khi push nhánh feature hoặc mở PR, kiểm thử rồi tạo hai artifact:

- `test-speaking-library-preview`: bản website đóng gói `.site`, có main Library, ứng dụng, JSON và đủ 14 ảnh; loại bỏ test scripts và tài liệu nội bộ của ứng dụng.
- `test-speaking-browser-reports`: screenshot và báo cáo kiểm thử.

Sau khi workflow thành công trên GitHub Actions:

1. Tải artifact `test-speaking-library-preview`, giải nén.
2. Trong thư mục giải nén, chạy `python3 -m http.server 8000`.
3. Trên chính máy đó, mở `http://localhost:8000/test-speaking/index.html` để xem Speaking mà không cần đăng nhập; hoặc `http://localhost:8000/index.html` để dùng luồng Library với đăng nhập hiện có.
4. Không mở trực tiếp file HTML bằng `file://`: fetch JSON cần HTTP(S).

Artifact là bản xem thử tải về, **không phải URL preview đã được host**. Không dùng workflow GitHub Pages production để tạo preview. Một URL thử nghiệm được host riêng cần có dịch vụ preview hoặc cấu hình GitHub Pages phù hợp đã được kiểm tra; không tự ghi đè site đang chạy. Kết quả CI trên GitHub và URL remote chỉ được coi là xác nhận sau khi đọc được trạng thái từ GitHub.

## Kiểm thử cục bộ

```sh
npm ci
node --test test-speaking/tests/*.test.mjs
npm run check:catalog
npm run test:prepare
python3 test-speaking/tests/browser.py
python3 test-speaking/tests/unit5-browser.py
python3 test-speaking/tests/library-navigation.py
node tools/prepare-site.mjs
HT_LIBRARY_SERVE_ROOT="$PWD/.site" python3 test-speaking/tests/library-navigation.py
```

Python browser tests cần Playwright 1.58 và Chromium; có thể đặt `CHROMIUM_PATH` tới binary tương ứng. Cloud hiện tại dùng `/workspace/library-venv/bin/python`. Nếu `.site` đã tồn tại, kiểm tra artifact cũ trước khi tạo lại; công cụ đóng gói không ghi đè.

Các kiểm thử đã xác nhận: 16 unit tests; 41 test chuẩn bị Library; 261 đường dẫn catalog; 8 nhóm browser regression; 8 nhóm Unit 5; 7 nhóm điều hướng trên mã nguồn và artifact. Đủ 14 PNG và câu hỏi/đáp án gốc khớp SHA-256. Browser test điều hướng Library dùng fixture truy cập cục bộ, không gọi Firebase production. Nghe giọng thật và thử tivi/máy chiếu vẫn cần thiết bị thực.

## Phạm vi file

- Sửa `index.html`: một link danh mục mới và một stylesheet, giữ nguyên các danh mục cũ.
- Thêm `assets/test-speaking-entry.css`.
- Thêm `test-speaking/index.html`, `styles.css`, `app.js`, `core.js`, `media.js`, `README.md`.
- Thêm dữ liệu demo được giữ nguyên `test-speaking/data/sets.json` và `import-template.csv`.
- Thêm `test-speaking/data/global3-unit5/`: JSON, CSV, README nguồn, 14 ảnh `Speaking_Card_01.png`–`Speaking_Card_14.png`, manifest SHA-256 và hướng dẫn.
- Thêm các unit/browser/navigation tests và báo cáo nghiệm thu trong `test-speaking/tests/`.
- Thêm `speaking-cards/index.html` để tương thích đường dẫn demo cũ.
- Sửa `tools/prepare-site.mjs` để đóng gói ứng dụng và loại test/tài liệu khỏi artifact.
- Thêm `.github/workflows/test-speaking.yml` để kiểm thử và tạo artifact; thêm tài liệu review này.
- Thêm `.gitattributes` chỉ cho các tệp nguồn Unit 5 để giữ nguyên byte, kể cả CRLF của CSV gốc.

Không sửa TTS, thêm Unit mới, đổi ảnh/câu hỏi/đáp án Unit 5, chỉnh Firebase, đổi catalog hoặc sửa game cũ.

Khi yêu cầu điều chỉnh, ghi rõ màn hình (Library/Grade/Unit/Phiên), thiết bị hoặc kích thước, thao tác và kết quả mong muốn. Có thể đính kèm screenshot từ bản preview hoặc artifact báo cáo.
