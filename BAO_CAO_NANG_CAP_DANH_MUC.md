# Kết quả nâng cấp đăng nhập và quản lý danh mục

Nhánh: `firebase-auth-trial`. Hoàn thiện mã và phương án triển khai để duyệt, chưa áp dụng Rules/indexes, chưa thay đổi dữ liệu Firebase thật, chưa merge `main` và chưa triển khai GitHub Pages.

## Kết quả

- Admin có thể thêm/sửa/xóa/ẩn/hiện khối, thư mục và bài; sắp xếp, chuyển bài giữa khối/thư mục, thêm đường dẫn HTML; số bài tính tự động.
- Bản nháp tách khỏi dữ liệu Firebase. Mỗi lần Lưu phải xác nhận, kiểm tra bản đọc trước đó còn mới và đọc lại dữ liệu để xác minh.
- Lưu lịch sử nguyên trạng và bản mới trong cùng giao dịch; Rules yêu cầu tăng phiên bản đúng một bước và sao lưu bắt buộc. Không cho xóa `current`, sửa/xóa lịch sử hoặc tự nâng quyền giáo viên.
- Khôi phục từ JSON hoặc lịch sử vào bản nháp; chỉ khi Lưu mới tạo phiên bản mới. Bản gốc v1 vẫn đọc được, không tự chuyển đổi khi mở trang.
- Workflow Pages thủ công, chỉ chạy trên `main` với chuỗi xác nhận. Không deploy khi push hoặc mở PR; không thay Firebase Rules.
- Gói Admin Windows được tạo lại từ mã đã kiểm thử để tải qua GitHub.

## Kiểm thử đã thực hiện

| Bộ kiểm tra | Kết quả |
| --- | --- |
| Unit / công cụ sao lưu và khôi phục offline | 12/12 đạt |
| Firestore Security Rules trên Emulator | 18/18 đạt |
| Trình duyệt Chromium + Auth/Firestore Emulator | 21/21 tình huống đạt |
| Danh mục gốc | 201 URL tồn tại, dữ liệu/nội dung/thứ tự khớp tuyệt đối bản gốc |
| File đề thi, audio, chấm điểm và home-button | Không thay đổi so với commit gốc `8c6361c8cd85831097f28419bcbdaa5b31601bfc` |
| Đóng gói Pages | Đủ HTML/audio gốc, kiểm tra SHA-256 từng file; không chứa export danh mục, tools, Rules hoặc ZIP Admin |
| Workflow YAML | Hợp lệ; deploy chỉ `workflow_dispatch` trên `main` |

Trình duyệt kiểm tra: đăng nhập sai, tài khoản vô hiệu hóa/khóa/thu hồi/chưa có quyền, giáo viên không mở Admin, quyền cập nhật ngay trong phiên đang mở, nhập CREATE khi tài liệu vắng mặt và dừng khi tồn tại/tạo đồng thời, 202/203 mục, sửa/sắp xếp/chuyển bài, ẩn/hiện bài/thư mục/khối, chống chèn HTML qua tiêu đề, sao lưu JSON, từ chối checksum sai, khôi phục lịch sử, hai Admin lưu đồng thời, giữ bản nháp khi xung đột, URL tương đối dưới `/library/`, màn hình nhỏ và bài tập/audio/chấm điểm mở trực tiếp không đăng nhập.

Tất cả phép thử ghi dữ liệu dùng dự án `demo-ht-english-library` trên máy cục bộ. Bộ kiểm tra trình duyệt chặn mạng bên ngoài và xác nhận không có yêu cầu sản xuất. Dùng Firestore Emulator chính thức, kiểm tra SHA-256 trước khi chạy, do đường tải Google Storage bị hạn chế trong môi trường cloud.

## Giới hạn và bước cần phê duyệt

Đây là kết quả Emulator và đóng gói cục bộ; chưa xác minh đăng nhập/dữ liệu Firebase thật hoặc bản Pages mới. Không có phiên Firebase Admin hợp lệ trong Codex và không yêu cầu mật khẩu hoặc service account. Trước khi áp dụng, phải sao lưu Rules/dữ liệu hiện tại và kiểm tra trạng thái thực tế.

Spark được hỗ trợ trong hạn mức miễn phí; không cần Blaze. Không cố định 201 mục nhưng nội dung một tài liệu được giới hạn 700.000 byte để tránh trần 1 MiB của Firestore. Lịch sử chiếm dung lượng và mỗi lần lưu dùng 2 lượt ghi, kèm lượt đọc. Rules không tự tính SHA-256 bên trong JSON; công cụ Admin và giao diện đọc kiểm tra nội dung, Rules kiểm tra quyền, metadata và chuỗi phiên bản/bản sao.

Trang Admin quản lý danh mục liên kết, không tải/sửa file HTML/audio. Ẩn là loại khỏi giao diện, không giữ bí mật dữ liệu khỏi giáo viên có quyền đọc API hoặc khóa link bài tập trực tiếp.

Trình tự và khôi phục: [QUAN_LY_DANH_MUC_VA_TRIEN_KHAI.md](QUAN_LY_DANH_MUC_VA_TRIEN_KHAI.md). Sau phê duyệt mới Publish Rules, kiểm tra thật, merge và chạy workflow Pages. Nếu Pages đang xuất bản từ `main`, cần xử lý cấu hình Source trước khi merge để không xuất bản ngoài ý muốn.
