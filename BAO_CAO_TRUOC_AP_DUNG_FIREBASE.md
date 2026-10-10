# Báo cáo chuẩn bị áp dụng Firebase thật — chờ phê duyệt

Ngày lập: 09/10/2026. Nhánh: `firebase-auth-trial`. Dự án: `ht-english-library`. Database được kiểm tra qua Console: `(default)`.

**Chưa Publish Rules, chưa ghi/nhập/xóa dữ liệu Firebase thật, chưa triển khai GitHub Pages, chưa thay đổi main.**

Cập nhật giai đoạn đã được phê duyệt: Rules và importer đã được siết thành **chỉ tạo mới catalog**; không cho ghi đè/cập nhật/xóa. Báo cáo này ghi nhận đợt kiểm tra chuẩn bị trước đó; kết quả và hướng dẫn Publish mới nhất ở `PUBLISH_FIREBASE_TUNG_BUOC.md`. Không thực hiện lại yêu cầu phê duyệt cũ; các bước thật sẽ tiến hành tuần tự và kiểm tra kết quả giữa các bước.

## 1. Bằng chứng hiện trạng và bản sao lưu

Môi trường không có phiên Firebase CLI được đăng nhập. Biến Google credentials có mặt nhưng nội dung chỉ là cấu hình rỗng; không có quyền Google IAM dùng được để tự đọc Rules và dữ liệu. Vì vậy, bằng chứng Firebase thật được thu thập từ nội dung và quan sát mà chủ dự án cung cấp qua Firebase Console. Không mô tả các quan sát này là kết quả gọi API độc lập.

| Nội dung | Kết quả và nguồn |
| --- | --- |
| Rules đang Publish | Chủ dự án sao chép toàn bộ nguồn từ Console; `allow read, write: if false` |
| Firestore `(default)` | Chủ dự án thấy “Start collection”; không có bộ sưu tập |
| `libraryCatalog/current` | Chủ dự án xác nhận chưa tồn tại |
| Ứng dụng | Chủ dự án xác nhận chỉ có HT English Library Web |
| Mục đích dự án | Chủ dự án xác nhận chưa dùng cho website/phần mềm khác |
| Release ID, lịch sử Rules, API inventory mọi database | Chưa đọc độc lập; không nằm trong bản sao lưu nguồn Rules đã nhận |

Bản sao lưu nguồn Rules nằm **ngoài checkout**, không đưa vào Git hoặc website:

`/workspace/library-files/firebase-preflight-2026-10-09/firestore-rules-before.rules`

SHA-256: `ecf30f940747dcc3c5ba4993093e9a11ac9fc5df7e14b2a1512d2446923d84eb`.

File được lưu nguyên văn nội dung gửi từ Console và đọc lại đối chiếu SHA-256. Thư mục riêng tư dùng quyền 700; các file sao lưu dùng quyền 600. Metadata nguồn, thời điểm lưu và xác nhận hiện trạng được lưu cùng thư mục. Nên tải bản Rules về máy của chủ dự án trước khi áp dụng thật; không chỉ phụ thuộc bản trong máy cloud.

Không tạo file “sao lưu tài liệu cũ” giả: tài liệu chưa tồn tại nên chỉ lưu bằng chứng trạng thái vắng mặt. Nếu kiểm tra lại trước khi áp dụng thấy tài liệu hoặc dữ liệu mới, kết luận trống này hết hiệu lực: dừng và sao lưu bản mới đầy đủ trước.

## 2. Rà soát Security Rules mới

`firestore.rules` không thay đổi trong giai đoạn chuẩn bị này; chỉ tăng kiểm tra.

- Admin được xác định bằng UID `4Y82k6RBaRUPflZriPsUvQv1qKj2` từ danh tính do Firebase xác thực. Email, thông tin `role` trong Firestore hoặc claim do người dùng tự đặt không thể nâng quyền.
- Giáo viên chỉ đọc `libraryCatalog/current` khi bản ghi quyền của chính UID có trạng thái `active`.
- Giáo viên chỉ đọc bản ghi quyền của mình, không xem danh sách giáo viên hoặc quyền người khác.
- Chỉ Admin tạo/cập nhật bản ghi quyền, và không được dùng bản ghi giáo viên để sửa tài khoản Admin chính.
- Quyền `locked`, `revoked` và tài khoản chưa được cấp quyền không đọc được danh mục. Các tài khoản đó không thể tự tạo bản ghi hoặc tự mở khóa.
- Không mở truy cập các bộ sưu tập, tài liệu hoặc subcollection ngoài phạm vi được phép.
- Schema chặn trường `role`, `admin`, mật khẩu và timestamp giả trong bản ghi quyền.
- Danh mục chỉ Admin ghi; giao diện kiểm tra SHA-256 của bản gốc trước nhập và sau đọc lại. Rules kiểm tra schema/số lượng, nhưng không tự tính SHA-256 của chuỗi JSON; Admin là người được tin cậy để nhập bản đã kiểm tra.

Rules có tính chất OR: nếu một `allow` khác cũng khớp đường dẫn và cho phép truy cập, quy tắc hạn chế không thể phủ nhận nó. Rules cũ được cung cấp chỉ có `allow ... false`, nên không thấy nhánh cấp quyền rộng gây xung đột. Không tự hợp nhất một quy tắc công khai trong tương lai vào bộ Rules này.

Không dựa vào việc ẩn nút Admin làm lớp bảo vệ. Kiểm tra chống nâng quyền được chạy trực tiếp trên Firestore Emulator.

## 3. Danh mục và công cụ nhập

`catalog/library-catalog.json` giữ nguyên dữ liệu gốc gồm 201 đường dẫn riêng biệt, tiêu đề, cấu trúc và thứ tự. SHA-256:

`456425b97fca668d9bd81c7cde123dd6a041350bc7ed7f1343deb7da841e0289`.

`npm run check:catalog` đối chiếu trực tiếp dữ liệu từ commit gốc và kiểm tra file bài tập còn tồn tại. Thứ tự hiển thị cũng được so với trang web gốc; việc sắp xếp Unit có sẵn được giữ nguyên.

Importer đọc trạng thái tài liệu khi kiểm tra file. Lúc nhập, giao dịch Firestore đọc lại tài liệu và so với phiên bản vừa kiểm tra. Nếu có thay đổi, công cụ dừng thay vì ghi đè. Sau nhập phải đọc lại từ server và xác minh đủ 201 mục, đúng SHA-256. Đăng nhập Admin và chọn file không tự ghi danh mục.

Với trạng thái hiện tại, lần nhập được phê duyệt sẽ **tạo một tài liệu** `libraryCatalog/current`, không ghi đè tài liệu cũ. Không cần tạo bản ghi quyền cho Admin; không tạo tài khoản giáo viên hoặc thay đổi Authentication trong bước áp dụng này.

## 4. Công cụ kiểm tra/sao lưu bổ sung

`tools/firebase-preflight.mjs` chỉ gọi API đọc Rules, database, tên bộ sưu tập gốc, danh sách app và tài liệu mục tiêu bằng tài khoản Google có quyền dự án. POST duy nhất được cho phép là thao tác đọc `listCollectionIds`. Công cụ chặn Publish/PATCH/commit/DELETE, sai dự án và hostname ngoài danh sách API.

Đây là công cụ tùy chọn cho người hỗ trợ đã có Google OAuth/ADC trên máy của mình, **không yêu cầu gửi token, mật khẩu hoặc service account vào chat**. Công cụ chưa được chạy với dự án thật trong phiên này. Quan sát Console của chủ dự án là nguồn bằng chứng hiện tại.

Khi đọc được tài liệu đã có, công cụ giữ nguyên biểu diễn Firestore REST có kiểu dữ liệu, gồm số nguyên lớn, timestamp, bytes, map, array và reference; không làm mất kiểu bằng cách chuyển tùy tiện sang JSON thường. 403/lỗi mạng không được coi là “không tồn tại”. Kết quả thiếu quyền hoặc Rules đổi trong lúc đọc được đánh dấu không hoàn tất và không dùng để tạo kế hoạch khôi phục.

`tools/prepare-firebase-rollback.mjs` chỉ đọc bản sao lưu trên đĩa và tạo mẫu khôi phục; không gọi API, không thực hiện khôi phục. Mẫu dùng điều kiện updateTime để tránh ghi đè/xóa dữ liệu mới hơn. Xem `PHUONG_AN_KHOI_PHUC_FIREBASE.md`.

## 5. Kiểm tra đã hoàn thành

| Bộ kiểm tra | Kết quả |
| --- | --- |
| Catalog + preflight/rollback offline | 9/9 đạt |
| Firestore Security Rules | 12/12 đạt trên Emulator |
| Trình duyệt Auth + Firestore | 13/13 tình huống đạt trên Emulator |
| Danh mục và file bài tập | Đúng 201 đường dẫn; đề/audio/chấm điểm và home-button không thay đổi |

Bổ sung kiểm tra tài khoản chưa có quyền/bị khóa/thu hồi không tự cấp quyền; subcollections không bị mở; 403 không bị hiểu nhầm là database trống; bản sao lưu giữ nguyên kiểu; và importer từ chối ghi đè khi tài liệu bị thay đổi sau khi kiểm tra.

Lệnh đã chạy:

```sh
npm run build
node --test tests/preflight.test.mjs tests/catalog.test.mjs
npm run check:catalog
python3 tools/test-emulators-official.py
```

Kiểm tra trình duyệt dùng cấu hình demo và chặn các yêu cầu mạng ngoài máy cục bộ. Kiểm tra công cụ preflight sử dụng phản hồi giả lập trên máy; không gọi API Firebase thật. Google Storage bị proxy chặn ở lần trước; Emulator chính thức từ Cloud SDK được xác minh checksum và dùng lại, không bỏ qua TLS/checksum.

## 6. Phạm vi cần phê duyệt cuối cùng

Chỉ sau khi chủ dự án xác nhận cuối cùng mới:

1. Kiểm tra lại dự án, UID Admin, Rules và trạng thái Firestore vẫn giống bằng chứng đã lưu. Có thay đổi thì dừng để đánh giá và sao lưu lại.
2. Publish bộ `firestore.rules` đã duyệt **cho database `(default)`** bằng Firebase Console.
3. Đăng nhập Admin trên giao diện cục bộ; chọn bản danh mục đúng; xác nhận tạo `libraryCatalog/current` trong `ht-english-library`.
4. Đọc lại từ server, kiểm tra 201 mục và lưu thời gian cập nhật của tài liệu mới để phục vụ khôi phục có điều kiện.
5. Báo cáo kết quả; không triển khai GitHub Pages, không sửa main và không tạo tài khoản giáo viên trong phạm vi này.

Các bước này chưa thực hiện. Quy trình thao tác Console chi tiết và cách quay về trạng thái ban đầu nằm trong tài liệu khôi phục. Những gì đã chạy cục bộ không chứng minh vận hành Firebase thật đã thành công.
