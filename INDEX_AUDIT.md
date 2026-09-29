# Báo cáo kiểm tra liên kết thư viện

Ngày kiểm tra: 2026-09-29

## Phạm vi thử nghiệm

- Trang được kiểm tra: `index.html`.
- Thư mục đề thử nghiệm: `grade-8/De_thi_GHK1`.
- Mục tiêu kiểm tra: liên kết nội bộ phải là đường dẫn tương đối và trỏ tới tệp có thật trong repository để tương thích với GitHub Pages.

## Kết quả

- `index.html` hiện có **152 liên kết nội bộ**.
- Cả 152 liên kết đều là đường dẫn tương đối và đều trỏ tới tệp đang tồn tại trong repository.
- Không phát hiện đường dẫn tuyệt đối dạng `/...`, `file://...`, đường dẫn ổ đĩa Windows, hoặc đường dẫn bắt đầu bằng `Documents/...`.
- Không có liên kết nào trong `index.html` trỏ tới `grade-8/De_thi_GHK1`.
- Đề thử nghiệm đã tồn tại tại `grade-8/De_thi_GHK1/1_THCS Truc Tuan/1. THCS Truc Tuan.html` nhưng **chưa có trong index**.

Theo yêu cầu của giai đoạn thử nghiệm đầu tiên, liên kết cho đề còn thiếu **chưa được tự ý thêm vào** và `index.html` không bị thay đổi. Không có section/category, tên hiển thị, thiết kế, bố cục hoặc liên kết bài học hiện hữu nào bị sửa hay xóa.

## Liên kết đề xuất cho lần cập nhật tiếp theo

Nếu được xác nhận bổ sung đề này vào index, `href` tương đối (đã mã hóa dấu cách) nên là:

```text
./grade-8/De_thi_GHK1/1_THCS%20Truc%20Tuan/1.%20THCS%20Truc%20Tuan.html
```

Đường dẫn trên phản ánh đúng cấu trúc thư mục thực tế, bao gồm thư mục con `1_THCS Truc Tuan`.
