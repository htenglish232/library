# Đề thi GHK1 Grade 7

14 đề dùng chung `exam-ui.js` và `exam-ui.css`. Mỗi HTML giữ câu hỏi, phương án, bài đọc, transcript, đáp án, lời giải và trọng số riêng trong `#examData`. Không dùng nội dung đề Trực Tuấn.

## Chạy và kiểm tra

Repository là website tĩnh, không cần cài dependency để chạy. Từ thư mục gốc:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Kiểm tra trên Chromium với Python Playwright (đã có trong môi trường cloud):

```sh
python3 grade-7/De_thi_GHK_1/tests/browser_checks.py
```

Bộ kiểm tra mở cả 14 đề, kiểm tra ID, radio/input, Word Chips và token trùng, bỏ chip, hoàn tác, reset từng câu, modal xác nhận/hủy, feedback, khóa bài, transcript và responsive ở 360/375/390/430px; sau đó làm toàn bộ câu bằng đáp án của từng đề để kiểm tra điểm tối đa và kiểm tra loa chỉ đọc đúng chuỗi phương án, không chọn radio, vẫn hoạt động sau nộp. Không kiểm tra hoặc thay thế nội dung file nghe.

## Quy tắc tương tác

- Chỉ nút xác nhận trong modal mới chấm và khóa bài. Không có tự nộp theo timer hoặc reset toàn bài sau nộp.
- State Word Chips lưu index; token trùng độc lập; cụm từ giữ nguyên; dấu câu cuối được lưu riêng.
- Loa trung tính lấy chuỗi trực tiếp từ nhãn phương án hiển thị. Chỉ các nhóm phương án từ đơn trong Language/Vocabulary được thêm loa trước nộp; không có loa trong Listening, Reading, Rearrangement hoặc transcript. Hàm speech không đọc dữ liệu đáp án/lời giải.
- Transcript được ẩn bằng thuộc tính `hidden` và chỉ mở sau xác nhận nộp. Nút ẩn/hiện transcript và loa trung tính vẫn hoạt động khi bài bị khóa.
- Thẻ `<audio>` và `<source>` cũ giữ nguyên. Chỉ các audio đã có mới được gắn điều khiển giao diện; không tạo `src`, không ghép media, không dùng TTS thay bài nghe. Các đường dẫn audio có sẵn bị thiếu file vẫn được giữ nguyên cho phiên xử lý audio sau.
- Giữ thông tin đề gốc, gồm Cổ Lễ 45 phút và Trực Hùng 43 câu. Trực Đại không ghi thời gian làm bài trong HTML gốc; Trực Nội không ghi năm học, nên không suy đoán các giá trị này.
- Liêm Hải có lỗi cũ: radio chia động từ gửi text (`reused`, ...) nhưng key dùng mã phương án (`A`, ...). Giá trị radio được đồng bộ theo mã phương án, giữ nguyên nội dung và đáp án đúng. Reading Cloze câu 2 Trực Đại tiếp tục chấp nhận B hoặc D như bộ chấm gốc.

## Font và CSS

Noto Sans được phục vụ cục bộ, gồm Latin, Latin Extended và tiếng Việt, trọng lượng 400–800. Nguồn: `@fontsource/noto-sans@5.2.8`; giấy phép SIL Open Font License trong `fonts/OFL.txt`. Không phụ thuộc Google Fonts hoặc Tailwind CDN khi mở đề.

`exam-ui.source.css` là nguồn của CSS đã biên dịch. Khi sửa layout, biên dịch lại bằng Tailwind 3.4.17 từ thư mục gốc:

```sh
npm install --prefix /tmp/grade7-css-tools --cache /tmp/grade7-npm-cache --no-audit --no-fund tailwindcss@3.4.17
/tmp/grade7-css-tools/node_modules/.bin/tailwindcss \
  -i grade-7/De_thi_GHK_1/exam-ui.source.css \
  -o grade-7/De_thi_GHK_1/exam-ui.css \
  --content 'grade-7/De_thi_GHK_1/**/*.html' --minify
```

Cài tool ngoài checkout để không tạo/sửa package manifest hoặc lockfile của repository. Dùng checkout hiện có; cloud task đã được cách ly, không tạo Git worktree trừ khi người dùng yêu cầu.
