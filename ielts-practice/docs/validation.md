# Kiểm thử IELTS Unit 2

## Đã chạy trên bản triển khai

| Kiểm tra | Kết quả |
| --- | --- |
| `source-pdf.py` | Đọc lại đủ 5 + 2 trang PDF; khớp bản trích xuất và dữ liệu có cấu trúc |
| `extract-source.py --verify` | 10 passage, 33 Vocabulary kèm nghĩa/synonym, 33 từ tổng hợp, 5 đoạn Reading, 10×4 lựa chọn, 10 ô Summary, 10 từ Word Bank, đoạn dịch và toàn bộ nội dung đáp án |
| `node --test ielts-practice/tests/model.test.mjs` | 6 đạt: thứ tự, chấm điểm, hai ô support, trim/case, từ đồng nghĩa bị từ chối, lưu/phục hồi, Translation tách riêng, không thay điểm khi ôn |
| Chrome Linux 156.0.8078.79 | 5 nhóm nghiệm thu đạt; đủ 1440×1000, 768×1024, 390×844, 375×812 |
| Edge Linux 142.0.3595.94 | 5 nhóm nghiệm thu đạt, cùng 4 viewport |
| `navigation-preview.py` trên source và `.site` | Library → IELTS Practice → Unit 2 và quay lại; JSON/PDF; bản HTML tự chứa mở `file://` và làm/nộp được |
| `npm run test:prepare` | 41 đạt |
| `npm run check:catalog` | 261 đường dẫn hiện có đạt; không đổi catalog cũ |
| So sánh với `origin/main` tại `caaae56` | `grade-6/`, `grade-7/`, `grade-8/`, `test-speaking/`, `Apps for IELTS/`, `assets/`, Firebase và package files không đổi |

Mỗi viewport kiểm tra nguyên văn cả 10 passage/Vocabulary, 5 đoạn Reading, 10 câu và đủ lựa chọn, Word Bank và nội dung Summary có số ô, đoạn Việt và bản dịch tham khảo. Lựa chọn/điền từ/bài dịch được lưu rồi tải lại, chuyển phần, nộp/hủy nộp, xem giải thích, ôn đúng 4 câu cần luyện và kiểm tra kết quả lần nộp không đổi. Kịch bản chấm gồm **16 đúng, 2 sai, 2 bỏ trống, hoàn thành 90%**; mô hình kiểm tra thêm trường hợp 20/20 và 0/20.

Không tải `answers.json` trong luồng chính trước khi nộp, không có feedback trước nộp. Sau nộp bài bị khóa, mới mở lời giải/bản dịch. Bản HTML review nhúng dữ liệu để chạy không cần server, vẫn chỉ trình bày đáp án sau nộp. Đây là phiếu luyện tập client, không tuyên bố bảo mật đáp án khỏi người đọc mã nguồn.

Không lỗi JavaScript, không HTTP lỗi hoặc yêu cầu dịch vụ ngoài trong luồng bình thường. Kiểm tra chủ động lỗi storage/quota và HTTP 503 của file đáp án: giữ bài đang nhập, cảnh báo đúng, nộp lại thành công. Không gọi Firebase production. Điều hướng có khoảng đệm đáy; nội dung cuối trang cuộn tới được, nút tối thiểu 44px, không tràn ngang. Mobile/tablet đưa câu hỏi trước bài đọc, desktop Reading bên trái/câu hỏi bên phải. Đánh dấu đoạn đọc không làm đổi nội dung nguồn.

## Bộ kiểm tra lịch sử GHK1

Chạy thêm 4 tệp `full-exam-migration`, `minimal-exam-ui`, `dual-mode-progress`, `dual-mode-sound`: **27/29 đạt, 2 không đạt**. Hai bài thất bại đều là assertion yêu cầu `index.html` giữ nguyên so với các commit lịch sử `3691356` hoặc `b38d578`. Trang chủ đã có lối vào Speaking từ trước nhiệm vụ IELTS.

Đã tạo checkout tách rời của chính `origin/main` (`caaae56`) và chạy lại cùng lệnh: **cũng 27/29, cùng đúng 2 bài thất bại ở `index.html`**. Không sửa hoặc vô hiệu hóa các bài kiểm tra này. Log main và nhánh hiện tại lưu ở `tests/reports/ghk1-baseline.log`, `ghk1-current.log`. Không coi đây là bộ kiểm tra đạt toàn bộ. Kiểm tra byte trực tiếp với main xác nhận tất cả file game, model, nguồn học thuật, audio, catalog, tài nguyên Speaking và Firebase hiện tại vẫn giữ nguyên; trang chủ chỉ thêm link IELTS đã được kiểm tra điều hướng.

## Ảnh chụp và giới hạn

Ảnh thực từ Chrome headless:

- [Màn hình bắt đầu desktop](screenshots/welcome-1440.png)
- [Reading + Multiple Choice desktop](screenshots/multiple-choice-1440.png)
- [Multiple Choice mobile](screenshots/multiple-choice-390.png)
- [Summary mobile](screenshots/summary-390.png)
- [Translation mobile](screenshots/translation-390.png)
- [Kết quả desktop](screenshots/results-1440.png)

Báo cáo Chrome/Edge ở `tests/reports/`. Ảnh full-page có thể vẽ thanh điều hướng cố định tại vị trí viewport đầu tiên; các câu ở dưới vẫn cuộn lên được và bài kiểm tra xác minh phần tử cuối không bị thanh điều hướng chặn vĩnh viễn.

Đây là Chrome/Edge thật chạy headless với viewport mô phỏng, không phải kiểm tra điện thoại/tablet vật lý hoặc bàn phím Safari/iOS. Không chạy emulator Firebase trong nhiệm vụ này vì không thay Firebase; kiểm tra đường dẫn Library dùng auth fixture cục bộ. Bản HTML mở trực tiếp đã thử trên Chrome; chưa khẳng định hành vi `localStorage` của mọi trình duyệt với `file://`.

Chưa có URL preview công khai tự động cho nhánh. File HTML xem thử tải xuống và GitHub Actions artifact là các bản review, không triển khai website chính. Không merge `main`, không kích hoạt workflow Pages production. Giáo viên đã xác nhận giữ nguyên nguồn và giữ hai lưu ý học thuật Summary theo [báo cáo nguồn](source-audit.md).
