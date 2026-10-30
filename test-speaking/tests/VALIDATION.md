# Kết quả kiểm thử demo

Đã kiểm tra trong cloud với Node 24, Python 3.12, Playwright 1.58 và Chromium hệ thống. Chưa triển khai production.

- `node --test test-speaking/tests/core.test.mjs test-speaking/tests/unit5.test.mjs`: **16 đạt**, 0 thất bại, 0 bỏ qua. Bao gồm đối chiếu SHA-256 đủ 14 ảnh với ZIP và xác nhận bộ demo cũ giữ nguyên byte.
- `python3 test-speaking/tests/browser.py`: **8 nhóm kiểm thử trình duyệt đạt**, 0 lỗi JavaScript, 0 yêu cầu ngoài máy chủ kiểm thử, không truy cập micro.
- `python3 test-speaking/tests/unit5-browser.py`: **8 nhóm Unit 5 đạt**: đủ 14 ảnh đúng byte/đường dẫn, đúng ảnh/câu hỏi/đáp án, Practice, Sequential/Random trên toàn bộ 14 thẻ hoặc 5 thẻ Core, giữ scope khi restart, phân loại khi sửa/xuất và tương thích thư viện cục bộ cũ.
- `npm run check:catalog`: **261 đường dẫn đạt**, tài nguyên bài thi/audio cũ được giữ nguyên.
- `npm run test:prepare`: **41 đạt**, 0 thất bại, 0 bỏ qua.
- Tích hợp Library chỉ sửa `index.html`, bổ sung CSS lối vào và cập nhật đóng gói. Catalog, Firebase và game cũ không đổi; bộ demo 15 câu và nguồn Unit 5 vẫn khớp SHA-256 đã kiểm tra.

| Yêu cầu nghiệm thu | Bằng chứng tự động |
| --- | --- |
| Practice Next/Previous | Kiểm tra câu 1/2 và chặn vượt giới hạn |
| Ẩn đáp án khi chuyển câu | Kiểm tra đáp án và từ khóa ẩn sau Next và reload |
| Sequential đúng thứ tự | So sánh đủ 15 ID theo thứ tự nguồn; browser kiểm tra câu 1/2 |
| Random không lặp | Đi hết 15 câu duy nhất; unit test lặp 30 lượt |
| Previous giữ thứ tự Random | So sánh câu trước/sau, giữ số thẻ đã xem |
| Restart & Reshuffle | Kiểm tra đủ 14 lần chọn ngẫu nhiên Fisher–Yates cho 15 thẻ và đặt lại tiến độ |
| Âm thanh không chồng | Mock speech/MP3 kiểm tra cancel/pause, tốc độ, ưu tiên MP3, fallback và callback cũ |
| Timer | Giả lập thời gian kiểm tra pause/resume/expiry/reset; câu và đáp án không tự đổi |
| Responsive | Chromium ở 360, 390, 768, 1920 px; không tràn ngang, thanh điều hướng ở đáy |
| Không ảnh hưởng thư viện cũ | Catalog và 41 test hiện có đạt; index/catalog/game cũ không thay đổi |

Kiểm tra thêm: xuất tệp JSON thực và nhập phục hồi, CSV, xác nhận thay thế/xóa, thêm/sửa thẻ, lọc/tìm kiếm, lưu Practice và thư viện sau reload, hình minh họa tùy chọn, phím tắt không tác động vào điều khiển/hộp thoại, fullscreen F/Escape, localStorage/giọng đọc không khả dụng, cả đường dẫn `/test-speaking/` và `/library/test-speaking/`.

Ảnh chụp và báo cáo máy: `/tmp/ht-test-speaking/`. Đây là kiểm thử mô phỏng trình duyệt, không phải kiểm tra thiết bị vật lý. **Cần nghe thử TTS/MP3 và âm báo trên thiết bị lớp học, đồng thời thử fullscreen trên tivi/máy chiếu thực tế trước khi sử dụng chính thức.** Không khẳng định hoạt động offline của giọng đọc hệ điều hành.

Ảnh/báo cáo Unit 5 tại `/tmp/ht-speaking-unit5/`. Bộ gốc 15 câu vẫn ở `data/sets.json`, không thay đổi; bộ Unit 5 dùng JSON/ảnh riêng trong `data/global3-unit5/`. Ảnh Unit 5 được giữ nguyên tệp và hiển thị contain, không crop hoặc vẽ lại.

Đã được chủ dự án cho phép tích hợp lối vào Library và tạo PR trên nhánh `feature/test-speaking-library`. Chưa được phép merge main hoặc deploy production. Thêm 7 nhóm kiểm tra Library → Test Speaking → Grade → giáo trình → Unit và đường dẫn quay lại; chạy cả trên mã nguồn và artifact đóng gói. Kiểm thử đăng nhập/thư viện dùng fixture cục bộ để không gọi production Firebase; không khẳng định kiểm thử end-to-end Firebase production.
