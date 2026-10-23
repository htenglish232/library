# Trực Hùng — Grade 8, GHK1: hai bài nghe riêng

Nguồn mới nhất: `75096f7`. Đã thay trình phát chung trỏ tới `FILE NGHE.mp3` không còn tồn tại bằng hai trình phát ở đúng phần I/II:

| Phần | Tệp đã tải lên | Thời lượng xấp xỉ |
| --- | --- | --- |
| Listening Part 1 | `Part 1.mp3` | 3:05 |
| Listening Part 2 | `Part 2.mp3` | 3:30 |

Hai MP3 giữ nguyên từng byte. Toàn bộ HTML đề ngoài các khối trình phát giữ nguyên so với nguồn mới nhất; không sửa câu hỏi, đáp án, transcript hoặc cách chấm.

Lịch sử `main` hiện tại không còn game đã làm ở nhánh thử nghiệm. Thay đổi này khôi phục riêng game Trực Hùng và bốn tài nguyên dùng chung từ `7f466cf`, cập nhật dữ liệu hai track và hash HTML nguồn. Không khôi phục hàng loạt các thay đổi trước đây hay hệ thống Firebase. `wholeFile` được đặt false để bỏ thông báo cũ “tệp nghe dùng chung cho hai phần”.

Index có lại liên kết game cạnh đề Trực Hùng. Game: `grade-8/De_thi_GHK1/12_THCS_Truc_Hung/practice-game-pilot.html`. Đề: `grade-8/De_thi_GHK1/12_THCS_Truc_Hung/12 THCS Truc Hung.html`. Chưa merge/deploy.

Kiểm chứng bằng Chromium và Playwright 1.58:

- Đề phát đúng hai file độc lập; phát phần sau tạm dừng phần trước; tua ±5 giây, thanh tiến độ, ba tốc độ và dừng/đặt lại hoạt động. Nút nghe vẫn dùng được sau nộp bài. Kiểm tra cả gốc website và `/library/`.
- Đối chiếu cả 43 bản ghi đáp án game với `answersData` trong đề hiện tại. Giữ hai câu chờ giáo viên C_II_B3 và D_II_1.
- Thao tác cả 43 câu qua game: đúng/sai/chờ duyệt, XP một lần, ôn lại, thẻ từ, audio thật và transcript. Giao diện game kiểm tra 360/390/768/820/1280px và cảm ứng. Không lỗi JavaScript hoặc yêu cầu Firebase.
- Tất cả URL trong index tồn tại; liên kết game Trực Hùng xuất hiện đúng một lần.

Chạy lại: cài `playwright==1.58.0` và Chromium, rồi chạy `python3 tests/truc-hung-listening.py`. Có thể đặt `CHROMIUM_PATH` nếu Chromium ở vị trí khác. Kết quả JSON/ảnh mặc định trong `/tmp/truc-hung-listening-tests`; bản báo cáo lần này được lưu ở [truc-hung-listening-test-report.json](truc-hung-listening-test-report.json).

Kiểm thử đề cô lập các dịch vụ CSS/font bên ngoài để kiểm tra media và chấm bài; không đánh giá giao diện Tailwind tải từ CDN. Việc nghe và xác nhận nội dung học thuật của MP3 vẫn cần giáo viên đối chiếu với câu hỏi/transcript.
