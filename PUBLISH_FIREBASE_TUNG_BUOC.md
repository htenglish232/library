> Nâng cấp quản lý danh mục: xem [QUAN_LY_DANH_MUC_VA_TRIEN_KHAI.md](QUAN_LY_DANH_MUC_VA_TRIEN_KHAI.md). Nội dung «chỉ tạo một lần / 201 mục» bên dưới mô tả giai đoạn thử nghiệm trước; công cụ nhập gốc vẫn chỉ CREATE, nhưng Rules đề xuất mới cho phép Admin lưu phiên bản mới kèm bản sao bắt buộc. Chưa áp dụng lên Firebase thật.

# Firebase: bước Publish Rules — danh mục chỉ tạo mới

Chủ dự án đã cho phép áp dụng thật theo từng bước. Hiện mới hoàn tất sửa mã và kiểm tra Emulator; chưa Publish Rules hoặc ghi dữ liệu Firebase thật. Nhánh `firebase-auth-trial`; không đổi main hoặc triển khai GitHub Pages. Không cần Blaze.

## Kết quả kiểm tra bản cuối

- 9/9 kiểm tra danh mục, preflight và khôi phục ngoại tuyến đạt.
- 13/13 kiểm tra Security Rules đạt trên Emulator.
- 14/14 tình huống trình duyệt đạt, gồm từ chối catalog đã tồn tại và trường hợp tài liệu được tạo bởi thao tác khác sau kiểm tra; tạo lần đầu và đọc lại xác minh đủ 201 mục.
- Các file đề, audio, chức năng chấm điểm và home-button không thay đổi.

Rules chỉ cho Admin tạo `libraryCatalog/current`; chặn mọi update/delete tài liệu đó, kể cả Admin. Giáo viên không thể tự cấp quyền. Quản lý trạng thái giáo viên vẫn được Admin tạo/cập nhật đúng schema. Importer dừng ở bước chọn file nếu catalog đã tồn tại và kiểm tra lần nữa trong giao dịch trước khi tạo. Nút nhập bị vô hiệu hóa sau khi tạo thành công.

Các thao tác xóa fixture trong bộ kiểm tra chỉ xảy ra trong dự án Emulator `demo-ht-english-library` trên máy cục bộ; không có thao tác xóa Firebase thật.

## Publish trong Firebase Console

1. Mở https://console.firebase.google.com/ bằng tài khoản Google quản lý dự án, chọn **ht-english-library**.
2. Menu bên trái **Build → Firestore Database**. Chọn database **(default)** nếu có bộ chọn database.
3. Tab **Data**: chỉ quan sát. Phải vẫn trống và chưa có `libraryCatalog/current`. Nếu khác, dừng và báo lại; không bấm Start collection.
4. Tab **Rules**: lưu lại bản đang Publish. Phải khớp bản sao lưu cũ có `allow read, write: if false`. Nếu khác, dừng để kiểm tra.
5. Thay toàn bộ nội dung trong trình soạn thảo bằng bộ Rules bên dưới. Không nối thêm vào Rules cũ.
6. Kiểm tra UID Admin, `allow create` trong `libraryCatalog/current`, và `allow update, delete: if false`.
7. Nhấn **Publish** phía trên trình soạn thảo; chờ thông báo thành công. Nếu lỗi cú pháp hoặc quyền dự án, gửi nguyên thông báo lỗi, không đổi sang Rules công khai và không nâng gói.
8. Tải lại trang Console, mở lại tab Rules và kiểm tra nguồn đang Publish vẫn đúng bộ vừa dán. Xác nhận Data vẫn trống.
9. Báo lại kết quả Publish và nội dung hai dòng quyền catalog. Chưa đăng nhập Admin thử nghiệm hoặc nhập dữ liệu trước khi bước Publish được xác minh.

Nếu có **Rules playground**, có thể kiểm tra GET `/libraryCatalog/current`: Authentication tắt phải bị từ chối; Authentication bật với UID Admin phải được phép. Đây là mô phỏng quyền, không tạo tài liệu và không thay thế việc kiểm tra nhập thật ở bước tiếp theo.

## Bộ Rules cần dán

```text
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    function admin() {
      return request.auth != null && request.auth.uid == '4Y82k6RBaRUPflZriPsUvQv1qKj2';
    }
    function activeTeacher() {
      return request.auth != null
        && exists(/databases/$(database)/documents/libraryMembers/$(request.auth.uid))
        && get(/databases/$(database)/documents/libraryMembers/$(request.auth.uid)).data.status == 'active';
    }
    match /libraryMembers/{uid} {
      allow get: if admin() || (request.auth != null && request.auth.uid == uid);
      allow list: if admin();
      allow create, update: if admin()
        && uid != '4Y82k6RBaRUPflZriPsUvQv1qKj2'
        && uid.matches('^[A-Za-z0-9_-]{1,128}$')
        && request.resource.data.keys().hasAll(['email', 'name', 'status', 'updatedAt'])
        && request.resource.data.keys().hasOnly(['email', 'name', 'status', 'updatedAt'])
        && request.resource.data.email is string && request.resource.data.email.size() <= 254
        && request.resource.data.name is string && request.resource.data.name.size() <= 120
        && request.resource.data.status in ['active', 'locked', 'revoked']
        && request.resource.data.updatedAt == request.time;
      allow delete: if false;
    }
    match /libraryCatalog/current {
      allow get: if admin() || activeTeacher();
      allow list: if false;
      allow create: if admin()
        && request.resource.data.keys().hasAll(['schemaVersion', 'count', 'sha256', 'dataJson', 'updatedAt'])
        && request.resource.data.keys().hasOnly(['schemaVersion', 'count', 'sha256', 'dataJson', 'updatedAt'])
        && request.resource.data.schemaVersion == 1
        && request.resource.data.count == 201
        && request.resource.data.sha256 is string && request.resource.data.sha256.matches('^[0-9a-f]{64}$')
        && request.resource.data.dataJson is string && request.resource.data.dataJson.size() < 200000
        && request.resource.data.updatedAt == request.time;
      allow update, delete: if false;
    }
    match /{document=**} { allow read, write: if false; }
  }
}
```

SHA-256 của file Rules: `5e29ba61952059a72c5752321bef290fae6248dd2f22fa74f7f8c98d1770d136`.

Bản Rules trước thay đổi đã lưu tại `/workspace/library-files/firebase-preflight-2026-10-09/firestore-rules-before.rules`. Chưa thực hiện khôi phục; khôi phục là thao tác riêng chỉ làm khi có sự cố và được chủ dự án cho phép. Không xóa tài liệu/tài khoản trong giai đoạn hiện tại.

Sau khi Publish đã được xác minh mới hướng dẫn mở Admin cục bộ và nhập danh mục. Tạo mới tài liệu mục tiêu không đồng nghĩa xuất bản website; GitHub Pages vẫn giữ phiên bản hiện hành.
