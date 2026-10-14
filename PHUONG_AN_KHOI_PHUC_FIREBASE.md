# Phương án khôi phục — chỉ thực hiện nếu được cho phép

Phương án được chuẩn bị ngày 09/10/2026; chưa thực hiện bất kỳ thao tác Firebase thật nào.

Hiện trạng theo xác nhận của chủ dự án: database `(default)` trống, `libraryCatalog/current` chưa tồn tại, Rules chặn toàn bộ đọc/ghi, chỉ một Web App HT English Library và dự án không dùng cho phần mềm khác.

## Trước khi áp dụng thật

1. Mở https://console.firebase.google.com/ và chọn **ht-english-library**. Không chọn dự án khác.
2. Vào **Firestore Database → Rules** của `(default)`. So sánh Rules đang Publish với bản sao lưu cũ. Không bấm Publish khi chưa được phê duyệt cuối cùng.
3. Vào **Firestore Database → Data**. Màn hình phải vẫn chỉ có **Start collection**, không có tài liệu. Nếu đã có dữ liệu, dừng và báo lại; không dùng kết luận trống cũ để ghi đè.
4. Vào **Authentication → Users**, kiểm tra UID của tài khoản Admin đúng `4Y82k6RBaRUPflZriPsUvQv1qKj2`. Chỉ xem, không đổi mật khẩu hoặc tài khoản.
5. Tải/lưu bản Rules trước thay đổi về máy riêng. Bản trong cloud: `/workspace/library-files/firebase-preflight-2026-10-09/firestore-rules-before.rules`. Không đưa các bản sao lưu dữ liệu hoặc thông tin tài khoản vào GitHub.

Sau khi được duyệt, người hỗ trợ hướng dẫn Publish Rules và nhập bản catalog. Lưu bản Rules mới được áp dụng và updateTime của tài liệu nhập thành công. Những thông tin đó xác định đúng thay đổi cần khôi phục.

## Nếu cần quay lại sau khi đã áp dụng

Các thao tác dưới đây là thay đổi thật, chỉ thực hiện khi được chủ dự án cho phép khôi phục:

1. Dừng thao tác nhập/cấp quyền để tránh có thay đổi đồng thời. Giữ bản dữ liệu vừa nhập và thông báo lỗi để kiểm tra nguyên nhân.
2. Kiểm tra Rules đang Publish vẫn là bản do đợt áp dụng này tạo. Nếu người khác đã sửa Rules, không thay thế tự động.
3. Trong **Firestore Database → Rules**, dán nguyên văn file Rules cũ đã lưu, so sánh lại và chỉ sau khi được cho phép mới chọn **Publish**. Không khôi phục bằng cách mở `allow read, write: if true`.
4. Kiểm tra `libraryCatalog/current` vẫn là tài liệu do đợt nhập này tạo, chưa có sửa đổi mới. Nếu có thay đổi khác, dừng và sao lưu/đánh giá thay đổi đó.
5. Vì tài liệu **không tồn tại trước triển khai**, khôi phục dữ liệu nghĩa là xóa **chính tài liệu `libraryCatalog/current` vừa tạo**. Không xóa database hoặc cả bộ sưu tập. Chỉ xóa sau khi được phép.
6. Chủ dự án có thể dùng **Firestore Database → Data → libraryCatalog → current → Delete document** bằng tài khoản Google quản lý dự án. Console dùng quyền quản trị dự án; đăng nhập Firebase bằng UID Admin trong website không đồng nghĩa có quyền Console. Phương án kỹ thuật chặt hơn dùng yêu cầu xóa có điều kiện `updateTime` và quyền Google IAM; nếu phiên bản thay đổi, API phải từ chối. Mẫu này chỉ là file chuẩn bị, chưa được gửi.
7. Kiểm tra lại dữ liệu và Rules trong Console. Nếu không có thay đổi ngoài phạm vi, trạng thái dữ liệu trở lại trống và Rules lại chặn toàn bộ. Không đụng đến tài khoản Authentication hoặc Web App có sẵn.

Nếu đã phát sinh tài liệu giáo viên hoặc dữ liệu khác sau lần nhập, không tự xóa chúng để làm database “trống”. Cần lập danh sách thay đổi và phương án khôi phục riêng được chủ dự án duyệt.

## Nếu trước lần áp dụng sau này tài liệu đã tồn tại

Không dùng cách xóa ở trên. Phải sao lưu toàn bộ fields bằng biểu diễn Firestore có kiểu dữ liệu, ghi nhận đường dẫn và updateTime, rồi mới xin duyệt ghi đè. Khi khôi phục, thay lại toàn bộ fields cũ, bao gồm loại bỏ fields mới không có trong bản gốc, với điều kiện phiên bản hiện tại vẫn là bản muốn hoàn tác. Subcollections không bị đụng tới.

Firestore không cho đặt lại server `createTime`/`updateTime` về thời gian cũ; khôi phục fields không đồng nghĩa phục hồi hai mốc hệ thống này. Bản sao lưu giữ hai mốc cũ để đối chiếu lịch sử.

## Công cụ dành cho người hỗ trợ kỹ thuật

Đọc và sao lưu bằng tài khoản Google đã có quyền trên máy riêng, không dùng khóa Admin SDK trong repository:

```sh
npm run preflight:firebase -- /duong-dan-rieng/ban-sao-luu-moi
```

Đường dẫn phải là thư mục mới ở ngoài checkout. Công cụ chỉ đọc; kết quả thiếu quyền hoặc API bị chặn được ghi là chưa hoàn tất. Không tạo bản sao lưu giả khi không đọc được dữ liệu. Không nhập token vào chat.

Chuẩn bị mẫu khôi phục **ngoại tuyến**, không thực thi:

```sh
npm run prepare:rollback -- /duong-dan-rieng/ban-sao-luu-moi
```

Lệnh kiểm tra checksum và chỉ chấp nhận bản đọc API hoàn tất đúng dự án. Mẫu có `execute: false`, yêu cầu phê duyệt và chỗ trống cho updateTime đã kiểm chứng sau nhập. Không tự động Publish Rules hoặc gửi yêu cầu ghi/xóa.

Bằng chứng hiện tại được lấy qua Console của chủ dự án; không có phiên Google OAuth dùng được trong máy Codex này. Không cần thiết lập khóa mới chỉ để thực hiện phương án Console hiện tại. Nguồn Rules cũ, bản xác nhận database trống và mẫu dành cho trường hợp hiện tại đã lưu riêng ở thư mục sao lưu ngoài repository.
