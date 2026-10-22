# Đề xuất tương thích index và quản lý thư viện — chưa triển khai

Index hiện tại chỉ hiện tài liệu sau khi tài khoản được Firebase xác minh quyền; mục đề GHK1 nhóm theo trường. Catalog Firestore hỗ trợ bản gốc v1 và catalog v2 do Admin quản lý, có lịch sử và metadata tiếp nhận từng đợt liên kết mới. **Giữ nguyên toàn bộ thiết kế này trong giai đoạn A/B.**

## Hiển thị học sinh về lâu dài

- Dựng một lớp trình bày: `Đề số 1`, `Đề số 2`, … theo số đầu thư mục gốc, không theo vị trí mảng hoặc thứ tự trường. Giữ khoảng trống số 15; không tự đánh lại số đề 16–20. Hai bản Trực Tuấn trùng byte không trở thành hai đề khác nhau.
- Mở từng đề thành hai lựa chọn **Làm đề kiểm tra** và **Chơi game luyện đề**. Có thể dùng details/summary hoặc một trang chọn riêng trong thư mục đề. Mỗi lựa chọn vẫn trỏ tới URL HTML gốc/game riêng.
- Tên trường, năm và tiêu đề giữ trong HTML đề/game. Các trường trùng tên nhưng khác thư mục/số đề vẫn có mã đề riêng; không gom nhầm hai đề Phương Định hoặc Đào Sư Tích.
- Nếu game chưa được tạo/duyệt, chỉ hiện lựa chọn đề kiểm tra; không tạo liên kết chết hoặc giả định mọi trường đã có game.
- Duy trì màn hình đăng nhập không có tài liệu/preview. Không tự mở quyền đọc Firestore hay tạo vai trò/tài khoản học sinh; mọi thay đổi quyền là nhiệm vụ riêng cần yêu cầu cụ thể.

## Catalog và triển khai sau khi duyệt

1. Giữ nguyên toàn bộ href, tiêu đề lưu trữ, trạng thái ẩn, thứ tự tùy chỉnh, các khối lớp khác và lịch sử của Admin. Đổi nhãn trình bày sang “Đề số…” không được thay nguồn catalog hàng loạt.
2. Dùng manifest tương thích `examId → sourceHtml, gameHtml, teacherReviewStatus, sourceHash`. Nguồn gốc quan hệ là thư mục đề, không chỉ tên trường; validate đủ file trước khi bổ sung liên kết.
3. Nếu thêm game vào danh mục, dùng cùng cơ chế bổ sung theo đợt đang có, có ID riêng và tôn trọng releaseApplied. Không tự tạo lại bài Admin đã xóa/ẩn, không reset tài liệu `libraryCatalog/current`.
4. Không đổi hash/count của export v1 201 bài hoặc Rules v1; chỉ dùng cơ chế v2/lớp trình bày tương thích đã kiểm thử. Bổ sung ba mẫu này sẽ cần kế hoạch duyệt danh mục riêng; hiện tại **0 liên kết mới được ghi vào index/Firebase**.
5. Kiểm thử trên bản sao/Emulator: đầy đủ URL cũ, ẩn/hiện, đổi tên, đề trùng trường, lịch sử/concurrent save, quyền truy cập trước/sau đăng nhập và `/library/`.
6. Tạo PR riêng cho index và catalog, để giáo viên xem nhãn và lựa chọn. Chỉ merge/deploy khi người dùng yêu cầu; giữ quy trình triển khai thủ công hiện tại.

## Điểm duyệt trước giai đoạn C

Theo yêu cầu nhiệm vụ: **“Dừng sau khi hoàn thành bản thử nghiệm. Không tự động tạo game hàng loạt, cập nhật Index, merge hoặc deploy cho đến khi tôi xác nhận.”**

Ba game mới, báo cáo từng đề và bộ máy dùng chung là kết quả bàn giao để duyệt. Các câu chờ giáo viên, mức chấp nhận các đáp án nguồn có nhiều biến thể và phạm vi bổ sung bản dịch AI cần được xem trước khi nhân rộng. Chưa thực hiện bất kỳ bước cập nhật index/catalog hoặc xuất bản nào.
