# Tạo lại phiếu bài tập HT English Grade 3

Thư mục HTML_Output chứa 30 bài HTML độc lập và index.html. Có thể mở trực tiếp bằng trình duyệt hoặc dùng thư mục này làm nội dung của GitHub Pages.

## Thành phần mã nguồn

- worksheet.template.html chứa bố cục từ Unit 01, logo, phông điểm viết tay và logic tương tác dùng chung.
- lessons.py chứa dữ liệu từng bài, tọa độ theo ảnh rộng khoảng 1.000 px, đáp án và giải thích. Trình duyệt quy đổi kích thước vùng bấm sang phần trăm từ kích thước trang thực tế.
- answer-key.json ghi đáp án dùng để chấm theo bài, trang và câu. Mục Unit 01 phản ánh bản HTML mẫu và có ghi chênh lệch với đáp án in.
- build.py tạo lại các file HTML và cập nhật manifest.
- report_review.py và report-review.html thêm hộp kết quả dùng chung cho chế độ Kiểm tra, gồm cả Unit 01.
- verify.cjs kiểm tra các thao tác trong Chromium ở hai kích thước khung nhìn.

## Tạo hoặc cập nhật

Cần Python 3.12 trở lên, Pillow và Poppler với pdftoppm trên PATH. Chạy ở thư mục gốc của bộ bàn giao.

    python -B Source/build.py "D:/Downloads/G3_Grammar_Units (2).zip"

Có thể truyền thư mục đã giải nén thay cho ZIP. Manifest theo dõi tiến độ từng bài. Script giữ file đã Completed và kiểm tra các mục còn lại. Khi chỉnh một bài đã hoàn tất, dùng lệnh sau.

    python -B Source/build.py "D:/Downloads/G3_Grammar_Units (2).zip" --force --only "Unit 03"

Cờ --only có thể lặp lại. File vừa tạo có trạng thái Needs review cho đến khi kiểm tra giao diện, đáp án và thao tác. Unit 01 dùng HTML mẫu trong ZIP làm nguồn và bổ sung hộp kết quả chung.

## Chạy kiểm thử

Cài Playwright cho Node.js và Chromium, rồi chạy từ thư mục gốc của bộ bàn giao.

    node Source/verify.cjs

Có thể truyền số thứ tự đầu và cuối để kiểm tra một nhóm. Đặt biến CHROME_EXECUTABLE nếu dùng bản Chrome đã cài trên máy. Ảnh kiểm tra được ghi vào work/qa.
