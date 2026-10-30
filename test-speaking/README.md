# HT English Speaking Cards

Ứng dụng tích hợp tại `test-speaking/index.html` trong cùng repository HT English Library. Trang Library thêm một lối vào Test Speaking; các danh mục, catalog, Firebase và game cũ giữ nguyên. Nhánh review: `feature/test-speaking-library`. Chưa merge main hoặc triển khai production. Đường dẫn demo cũ `speaking-cards/` chuyển tiếp tới trang mới.

Chạy từ gốc repository:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Mở đường dẫn `/test-speaking/` trên máy chạy server. Cần HTTP(S), không mở trực tiếp bằng `file://` vì ứng dụng tải JSON qua fetch. Tất cả đường dẫn tài nguyên đều tương đối, hỗ trợ GitHub project Pages `/library/test-speaking/`. Không cần npm build, đăng nhập hay API key.

## Sử dụng

Từ Library chọn **Test Speaking → Grade 3 → Global Success → Unit 5**. Chỉ hiện Grade/giáo trình/Unit có bộ thẻ. Mỗi Unit ghi số Speaking Cards. Breadcrumb và nút Danh sách Grade/Danh sách Unit cho phép quay lại; nút Library chính dùng đường dẫn tương đối `../index.html`. Tìm kiếm/lọc cho phép mở nhanh bộ thẻ; hash URL giữ cấp thư mục khi tải lại hoặc chia sẻ.

- Thư viện lọc theo Grade → giáo trình → Unit và tìm kiếm tên bộ.
- Practice lưu vị trí và thứ tự đã trộn theo từng bộ trên thiết bị. Đổi nội dung bộ làm thứ tự lưu cũ không còn hợp lệ thì quay về câu đầu.
- Test chọn Sequential hoặc Random. Random dùng Fisher–Yates đúng một lần lúc bắt đầu lượt, giữ nguyên thứ tự khi Previous/Next, không lặp câu mới. “Đã xem / Còn” đếm các thẻ đã mở, không suy đoán học sinh đã hoàn thành hay chấm điểm. Lượt Test không lưu sau khi đóng trang.
- Đáp án và từ khóa ẩn ở mỗi câu mới; giáo viên chủ động Reveal Answer. Không tự chuyển câu, kể cả hết giờ.
- Bộ đếm tùy chọn 15/30/45/60 giây, đặt lại khi đổi câu, có tạm dừng/tiếp tục. Hết giờ báo bằng chữ và âm báo ngắn nếu trình duyệt cho phép. Không dùng giọng đọc câu hỏi làm âm báo.
- Phím ←/→, Space, A, F và Escape để thoát toàn màn hình. Không bắt phím khi nhập liệu, chọn tùy chọn, tương tác nút hoặc đang mở hộp thoại.
- MP3 được ưu tiên; lỗi MP3 thử SpeechSynthesis. Giọng ưu tiên en-US, rồi en-GB, rồi English khác. Không tự phát. Chuyển câu, thay tốc độ và rời trang sẽ dừng âm thanh. Giọng, chất lượng và chế độ toàn màn hình phụ thuộc hệ điều hành/trình duyệt; có thông báo nếu không hỗ trợ. Ứng dụng không yêu cầu quyền micro, không có ghi âm hoặc SpeechRecognition. Dịch vụ TTS của thiết bị có thể cần mạng.

## Nội dung và sao lưu

`data/sets.json` chứa bộ demo 15 câu A1 theo yêu cầu: Grade 3 – Global Success – Speaking Practice. Đây là nội dung minh họa, không khẳng định khớp một Unit chính thức. Câu “What is this?” dùng với đồ vật do giáo viên chỉ trên lớp. Bộ demo không bắt buộc ảnh/MP3. Ứng dụng không tự tạo thêm nội dung cho các bộ do giáo viên nhập.

Đã bổ sung bộ **Grade 3 – Global Success – Unit 5 – My Hobbies** từ ZIP giáo viên cung cấp, tách riêng tại `data/global3-unit5/`. Giữ nguyên 14 PNG và JSON nguồn. Thư viện hiển thị Review (8 thẻ), Extension (1 thẻ), Unit 5 Core (5 thẻ). Khi bấm Sequential Test hoặc Random Test, chọn **Toàn bộ 14 thẻ** hoặc **Unit 5 Core · 5 thẻ**, sau đó chọn Sequential/Random. Practice luôn dùng đủ 14 thẻ. Trên điện thoại, câu hỏi nằm trên hình lớn; trên màn hình lớn, hình và câu hỏi đặt cạnh nhau. Thanh Previous/Next luôn cố định. Chi tiết và kiểm chứng tại [hướng dẫn Unit 5](data/global3-unit5/INTEGRATION.md).

Thêm bộ lâu dài bằng cách bổ sung JSON vào `data/sets.json` qua một thay đổi repository đã duyệt. Trình quản lý cho phép tạo bộ, sửa thông tin, thêm/sửa/xóa thẻ và xóa bộ có xác nhận. Thay đổi trong trình quản lý chỉ nằm trên trình duyệt hiện tại. **Xuất JSON sau khi chỉnh sửa**, giữ tệp sao lưu bên ngoài thiết bị hoặc đưa vào kho nội dung được quản lý. Không coi localStorage là bản gốc duy nhất. Nếu bộ nhớ bị chặn/đầy/lỗi, ứng dụng cảnh báo và vẫn cho xuất phiên hiện tại.

Sau lần chỉnh sửa đầu tiên, thư viện cục bộ được ưu tiên hơn tệp JSON mặc định để giữ nguyên nội dung và thao tác xóa của giáo viên. Để nhận các bộ mới vào trình duyệt đã chỉnh sửa, nhập tệp JSON cập nhật; ứng dụng giữ các ID khác và hỏi xác nhận với ID trùng. Không tự đồng bộ giữa thiết bị.

Riêng các gói nội dung mới được đăng ký trong ứng dụng (như Unit 5), ứng dụng bổ sung gói có ID chưa xuất hiện vào thư viện cục bộ cũ, không thay thế các bộ giáo viên đã chỉnh sửa. Một gói đã bị giáo viên xóa có xác nhận sẽ không tự xuất hiện lại. Nội dung các bộ có cùng ID vẫn ưu tiên bản cục bộ.

```json
{
  "id": "teacher-defined-set-id",
  "title": "Tên bộ thẻ của giáo viên",
  "grade": "Grade 3",
  "textbook": "Global Success",
  "unit": "Unit 5",
  "cards": [{
    "id": "teacher-defined-card-id",
    "question": "Câu hỏi do giáo viên cung cấp",
    "sampleAnswer": "Câu trả lời mẫu do giáo viên cung cấp",
    "keywords": [],
    "image": "",
    "audio": ""
  }]
}
```

Nhập JSON nhận một bộ, mảng bộ hoặc bản sao lưu `{ "schemaVersion": 1, "sets": [...] }`. CSV UTF-8 xem `data/import-template.csv`: mỗi dòng một thẻ, các dòng cùng `setId` phải có cùng thông tin bộ; từ khóa phân cách `|`; hỗ trợ ô có dấu phẩy, xuống dòng và dấu `"` theo RFC 4180. Mẫu CSV chỉ minh họa một dòng từ bộ demo; nhập với ID demo sẽ yêu cầu xác nhận thay thế cả bộ, nên sao lưu trước.

Thẻ có thể bổ sung `category`: `review`, `extension` hoặc `unit5`. Trình chỉnh sửa, xuất/nhập JSON và cột CSV tùy chọn `category` giữ nguyên phân loại này. Bộ không có category vẫn hoạt động như trước. Trường grade/unit dạng số trong JSON được chuẩn hóa thành nhãn “Grade N”/“Unit N” khi tải; tệp JSON nguồn không bị viết lại.

Tệp nhập tối đa 2 MB; tối đa 1.000 bộ, 2.000 thẻ/bộ. Kiểm tra toàn bộ trước khi cập nhật; ID trùng trong tệp bị từ chối; ID trùng bộ đã có yêu cầu xác nhận thay thế. Không diễn giải nội dung như HTML. Hình/âm thanh chấp nhận đường dẫn tương đối hoặc HTTP(S); từ chối script/data URL. Đường dẫn tương đối tính từ `test-speaking/`; mã hóa khoảng trắng bằng `%20`. Không nhúng URL kèm thông tin xác thực. Chỉ dùng ảnh/âm thanh có quyền sử dụng.

Kiến trúc: `core.js` quản lý schema/nhập/xáo trộn/phiên và adapter localStorage; `media.js` quản lý âm thanh/timer; `app.js` điều khiển DOM. Có thể thay adapter bằng Firebase sau này, chưa tích hợp Firebase ở bản demo.

## Kiểm thử

```sh
node --test test-speaking/tests/core.test.mjs test-speaking/tests/unit5.test.mjs
python3 test-speaking/tests/browser.py
python3 test-speaking/tests/unit5-browser.py
python3 test-speaking/tests/library-navigation.py
npm run check:catalog
npm run test:prepare
```

Browser test cần Python Playwright và Chromium. Trong cloud hiện tại: `PATH=/workspace/library-venv/bin:$PATH python3 test-speaking/tests/browser.py`. Test tự chạy HTTP server, chặn yêu cầu bên ngoài, kiểm tra cả đường dẫn `/library/`, xuất báo cáo/screenshot vào `/tmp/ht-speaking-cards`. Test SpeechSynthesis bằng mock xác định được lời gọi; nghe giọng thật và thử trên tivi/máy chiếu thật cần kiểm tra trên thiết bị đó. Không dùng micro hay production Firebase.

## Review và preview

Xem [hướng dẫn review](../docs/test-speaking-library-review.md). Workflow `.github/workflows/test-speaking.yml` chỉ chạy kiểm thử và tạo artifact preview, không deploy. Workflow production hiện có không thay đổi. Khi artifact có sẵn trên GitHub Actions, tải về và chạy máy chủ HTTP từ thư mục giải nén. Không mở HTML bằng file:// vì cần fetch JSON.
