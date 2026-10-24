# Giai đoạn 1 — THCS Trực Tuấn

Baseline `544777a`. Catalog thực có 19 đề GHK1 lớp 8 của 17 trường và 4 game đã có. Hai trường Đào Sư Tích và Phương Định có hai đề riêng; không suy số đề từ số đầu thư mục. Danh sách/hash nguồn: [inventory.json](inventory.json).

Chỉ triển khai bản chuẩn Trực Tuấn trước khi duyệt mở rộng. Không sửa index/catalog, Firebase, game Trực Tuấn cũ, ba pilot, HTML đề hoặc MP3. Bộ mới đặt trong `shared-practice/`, dùng lại model chấm theo nguồn và CSS hiện có; launcher/data Trực Tuấn riêng. Controller cũ tiếp tục phục vụ các game cũ cho đến khi giai đoạn sau được duyệt.

Nguồn Trực Tuấn có 42 câu: 12 nghe, 13 ngôn ngữ/ngữ pháp, 10 đọc, 7 viết; 29 lựa chọn (gồm 6 True/False), 10 nhập và 3 ghép thẻ. Hai bài đọc, hai transcript và hai MP3, giữ cả dấu cách trong `GHK1 K8 - part 2 .mp3`. HTML bản sao `(2)` ghi trong tài liệu cũ hiện không tồn tại trên main; không tạo lại hoặc đếm thành đề mới.

Game cũ có thử thách, XP một lần, điều hướng, audio/đọc, giải thích và ôn lại nhưng chưa có chế độ toàn đề hoặc lưu bền. Bản mới bổ sung hai chế độ trên cùng kết quả lần đầu, lưu bản nháp/tiến độ riêng mỗi đề và học sinh, tiếp tục/bắt đầu lại có xác nhận.

Giữ các điểm cần giáo viên duyệt: q12 (F theo HTML, ghi chú Word T), q13 (phát âm), q19 (“lunch tonight”/lời đáp), q29 (keep/stay fit), q40 (yours/your bike so với his). Tự luận chỉ chấp nhận câu mẫu/biến thể được nguồn nêu rõ; các cách viết khác cần giáo viên đối chiếu. Không dùng từ khóa để nhận đúng. Bản dịch/mẹo cũ được sao chép riêng, đánh dấu AI/chưa xác nhận, không dùng làm đáp án.

`tools/verify-truc-tuan-dual-source.py` trích lại trực tiếp DOM và hai object đáp án/thẻ từ trong HTML hiện tại; không chạy ứng dụng đề, không ghi file nguồn. Đã đối chiếu đủ 42 ID, thứ tự, nội dung, phương án, đáp án/ghi chú, thẻ từ, đoạn đọc, transcript và hash MP3. `tools/build-truc-tuan-dual-data.mjs` tạo dữ liệu riêng và có chế độ `--verify` không ghi file.
