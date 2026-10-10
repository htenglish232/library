# Gói Admin thử nghiệm Windows

Gói được tạo từ mã nguồn commit `19e08455e635e16403184a322d9604b2737c1b82` trên nhánh `firebase-auth-trial`; giao diện hỗ trợ quản lý danh mục linh hoạt, sao lưu/khôi phục và lưu có kiểm tra phiên bản. Cấu hình dự án Firebase thật được giữ; mở trang không tự ghi dữ liệu.

Tải `HT-English-Admin-thu-nghiem-Windows.zip`, chọn **Extract All**, rồi chạy `MO_ADMIN_WINDOWS.cmd`. Máy cần Python 3; không cần Node.js/Firebase CLI. Đọc `HUONG_DAN_WINDOWS.txt` và [hướng dẫn nâng cấp](../QUAN_LY_DANH_MUC_VA_TRIEN_KHAI.md).

Chưa Publish Rules hoặc triển khai Pages trong lần chuẩn bị này. Không nhấn Lưu hoặc thay đổi quyền trên Firebase thật trước khi được phê duyệt. Nếu Rules cũ chỉ CREATE đang hoạt động, thao tác chỉnh sửa sẽ bị từ chối. Công cụ nhập gốc vẫn chỉ tạo mới 201 mục và dừng nếu tài liệu đã tồn tại.

Gói nhỏ không chứa bài tập/audio. Chỉ dùng giao diện để thử Admin; bài tập hiện tại trên GitHub Pages giữ nguyên. Không chứa mật khẩu hoặc khóa Admin SDK.

SHA-256 ZIP: `8259530d9707307c8d3046250e39d7d7a60b1b1d269ea908fbf80a26ccef26a0`.

Tạo lại gói bằng `python3 tools/build-admin-package.py` sau khi commit mã nguồn đã kiểm thử; không thực hiện thao tác mạng hoặc Firebase.
