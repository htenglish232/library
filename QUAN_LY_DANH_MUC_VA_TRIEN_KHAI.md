# Quản lý danh mục và triển khai HT English Library

Tài liệu này thay thế phần «chỉ tạo danh mục một lần / luôn đúng 201 mục» trong các hướng dẫn thử nghiệm cũ khi nâng cấp được phê duyệt. Chưa áp dụng Rules hoặc sửa dữ liệu Firebase thật, chưa merge `main`, chưa chạy workflow Pages. Bản gốc 201 mục và toàn bộ file HTML/audio được giữ nguyên trong repository.

## Bạn có thể quản lý những gì?

Trong `admin.html`, sau khi đăng nhập Admin, phần **Quản lý tài liệu và danh mục** tự tải danh mục hiện tại từ Firebase. Chỉ UID Admin `4Y82k6RBaRUPflZriPsUvQv1qKj2` được chỉnh sửa.

- Thêm, đổi tên, xóa, ẩn/hiện khối lớp và thư mục.
- Sắp xếp khối, thư mục và bài bằng nút Lên/Xuống; sắp xếp khối theo tên/số.
- Thêm/sửa/xóa/ẩn/hiện liên kết bài tập. Khi Sửa bài, chọn **Khối lớp đích / Thư mục đích** để chuyển bài mà giữ nguyên đường dẫn HTML.
- Tự tính tổng bài và bài đang hiển thị, không cố định ở 201.
- Tải bản sao JSON, khôi phục từ file hoặc từ phiên bản đã sao lưu.

Mọi thay đổi nằm trong **bản nháp** đến khi bạn nhấn **Lưu danh mục** và xác nhận tên dự án. Xóa thư mục/khối sẽ bỏ các liên kết bên trong khỏi bản nháp, không xóa HTML/audio. Có cảnh báo khi rời trang với bản nháp chưa lưu. Đăng xuất sẽ xóa bản nháp khỏi giao diện.

Trang Admin quản lý liên kết, không sửa nội dung đề, không tải file lên GitHub. Với bài mới, trước hết cần đặt file HTML/audio tại đường dẫn `grade-N/...` trong repository qua một thay đổi được duyệt và triển khai, hoặc dùng URL HTTPS tới một bài HTML đã hoạt động. Sau đó thêm đường dẫn ở Admin. Đường dẫn tương đối có khoảng trắng như bản gốc được hỗ trợ; đường dẫn nguy hiểm, trùng lặp, `javascript:`, `data:`, HTTP, đường dẫn đi ngược `../` bị từ chối. Việc kiểm tra định dạng không chứng minh bài mới đã tồn tại: hãy mở thử URL thực tế trước khi Lưu.

Ẩn/hiện dùng để tổ chức giao diện. Đây không phải cách bảo mật file hoặc giữ bí mật nội dung ẩn: giáo viên có quyền đọc tài liệu danh mục vẫn có thể thấy dữ liệu ẩn qua API, và bài tập tĩnh vẫn mở trực tiếp cho học sinh.

## Dữ liệu và kiểm tra phiên bản

Không tự động chuyển đổi dữ liệu khi mở trang. Bản Firestore cũ `schemaVersion: 1` vẫn được đọc và xác minh đúng 201 mục/SHA-256 gốc. Nếu danh mục chưa tồn tại, công cụ nhập gốc vẫn chỉ CREATE, không ghi đè.

Lần đầu Admin chủ động Lưu một chỉnh sửa sẽ chuyển danh mục hiện tại sang phiên bản có thể quản lý, sau khi đã đọc và kiểm tra bản gốc:

| Vị trí | Nội dung |
| --- | --- |
| `libraryCatalog/current` | `schemaVersion: 2`, `revision` tăng từng lần, `parentSha256`, `count`, `sha256`, `dataJson`, `updatedAt`, `updatedBy` |
| `libraryCatalogHistory/0` | Bản sao đầy đủ tài liệu v1 trước lần sửa đầu tiên, gồm cả thời gian gốc; `revision: 0`, `snapshot`, `archivedAt`, `archivedBy` |
| `libraryCatalogHistory/N` | Bản sao đầy đủ phiên bản N trước khi lưu N+1; lịch sử chỉ được tạo, không sửa/xóa |
| `libraryMembers/{uid}` | Giữ nguyên `email`, `name`, `status`, `updatedAt`; `active` được đọc, `locked`/`revoked` không được đọc danh mục |

Trong `dataJson`, cấu trúc khối → thư mục → bài của bản gốc được giữ: `{grade, units: [{name, type?, lessons: [{title, href, hidden?}], hidden?}], hidden?}`. Không thêm `hidden` hoặc sắp xếp dữ liệu gốc khi chỉ đọc. Tổng bài bao gồm bài ẩn; số hiển thị loại trừ khối/thư mục/bài ẩn. Giáo viên nhận cập nhật danh mục qua Firebase, giữ khối đang xem và từ khóa tìm kiếm nếu khối vẫn còn.

Mỗi lần lưu là **một giao dịch nguyên tử gồm 2 tài liệu**: sao lưu nguyên trạng bản trước và lưu bản mới. Nếu một thao tác bị từ chối thì cả hai không được lưu. Công cụ so sánh số phiên bản, SHA-256 và thời gian đọc trước đó với bản Firebase mới nhất. Khi khác nhau, dừng và giữ bản nháp; bạn có thể tải bản nháp JSON trước khi tải lại để đối chiếu.

Rules bắt buộc số phiên bản kế tiếp, đúng SHA-256 cha, đúng Admin/thời gian máy chủ và một bản sao nguyên trạng chưa tồn tại. Admin không được xóa `current` hoặc sửa/xóa lịch sử. Giáo viên không được đọc lịch sử, ghi danh mục hoặc tự thay đổi quyền. Bộ sưu tập khác vẫn bị đóng.

Firestore Rules không phân tích JSON hoặc tự tính SHA-256. Kiểm tra cấu trúc, số bài, đường dẫn và băm nội dung được thực hiện ở công cụ Admin và khi đọc lại trên giao diện; Rules kiểm tra metadata, quyền, liên kết phiên bản và bản sao nguyên trạng. Thiết kế tin cậy tài khoản Admin, không tuyên bố chống Admin cố ý tự gửi nội dung sai qua API.

## Sao lưu và khôi phục

1. Chọn **Tải sao lưu JSON**. Nếu còn bản nháp chưa lưu, tên file có `ban-nhap` và nội dung ghi `includesUnsavedDraft: true`; đây là bản nháp, không phải ảnh chụp Firebase mới nhất. File chỉ chứa danh mục, không chứa email hoặc quyền giáo viên.
2. Để khôi phục từ file: tải danh mục hiện tại, chọn JSON ở **Khôi phục danh mục**. Công cụ kiểm tra SHA-256, số bài, cấu trúc và đường dẫn rồi hỏi xác nhận. Bản được đưa vào nháp; chưa ghi Firebase.
3. Để khôi phục từ Firebase: chọn **Tải danh sách lịch sử**, chọn phiên bản và **Khôi phục lịch sử vào bản nháp**.
4. Kiểm tra bản nháp và nhấn **Lưu danh mục**. Khôi phục luôn tạo phiên bản mới, sao lưu bản hiện tại và không xóa lịch sử hoặc giảm số phiên bản.

Danh sách lịch sử hiện tải toàn bộ các bản sao. Khi có nhiều bản, việc này tăng dung lượng tải và lượt đọc; chỉ Admin bấm tải khi cần. Không tự động xóa lịch sử hoặc thông tin giáo viên.

## Spark miễn phí và giới hạn thực tế

Dùng Firebase Authentication Email/Password và Cloud Firestore trên Spark, không dùng Functions, Admin SDK, dịch vụ trả phí hoặc yêu cầu Blaze. Không lưu mật khẩu/khóa quản trị; cấu hình Web App trong mã là thông tin công khai.

Theo hạn mức Spark của Firestore: khoảng 50.000 lượt đọc/ngày, 20.000 lượt ghi/ngày và 1 GiB lưu trữ; cần đối chiếu trang Usage và hạn mức hiện tại trong Console. Mỗi lần Lưu ghi 2 tài liệu, kèm lượt đọc giao dịch, kiểm tra Rules, đọc lại và cập nhật cho giáo viên đang mở trang. Lịch sử chiếm thêm dung lượng. Nếu hết hạn mức miễn phí, thao tác có thể bị từ chối; hệ thống không tự nâng cấp Blaze.

Không giới hạn số mục ở 201, nhưng Firestore giới hạn một tài liệu ở 1 MiB. Công cụ giới hạn nội dung JSON ở 700.000 byte để chừa chỗ metadata. Nếu vượt, công cụ dừng; cần thiết kế chia tài liệu riêng trong một lần nâng cấp sau, không cắt dữ liệu. `firestore.indexes.json` đề xuất bỏ chỉ mục cho `dataJson` và `snapshot.dataJson`, vì không truy vấn theo các trường này; hiện chưa áp dụng.

## Thứ tự triển khai sau khi bạn phê duyệt

Không thực hiện các bước thay đổi thật chỉ vì tài liệu này tồn tại.

1. **Sao lưu hiện trạng thật:** Firebase Console → dự án `ht-english-library` → Firestore Database → Rules, sao chép toàn bộ Rules đang Publish và lưu riêng trên máy. Kiểm tra Data, các bộ sưu tập và `libraryCatalog/current`; không giả định vẫn trống dựa trên kiểm tra cũ. Tải JSON danh mục bằng phiên bản Admin đã kiểm thử nếu tài liệu tồn tại. Công cụ `npm run preflight:firebase -- <thư-mục-riêng-ngoài-repo>` chỉ đọc và cần phiên Google IAM hợp lệ; không gửi khóa/mật khẩu cho Codex. Công cụ đó sao lưu tài liệu hiện tại, không xuất toàn bộ giáo viên/lịch sử; nếu có dữ liệu khác, phải kiểm kê và sao lưu riêng trước khi thay đổi.
2. **Publish Rules được duyệt:** Console → Firestore Database → Rules → thay bằng toàn bộ `firestore.rules` trong PR được duyệt → Publish → kiểm tra lịch sử phiên bản. Không mở tạm quyền công khai. Trong Database → Indexes → Single field, có thể cấu hình miễn lập chỉ mục các trường dài theo `firestore.indexes.json`; không chạy deploy toàn bộ Firebase.
3. **Xác minh trên bản thử nghiệm mới:** đăng nhập Admin bằng trình duyệt của bạn, tải danh mục, đối chiếu số bài và SHA-256. Chưa nhấn Lưu nếu bạn mới chỉ đồng ý Publish Rules. Nếu danh mục chưa tồn tại, chỉ nhập gốc 201 mục khi được phép; công cụ vẫn từ chối tài liệu đã tồn tại.
4. **Phê duyệt PR và merge vào `main`:** kiểm tra các kiểm thử đã đạt; không sửa file đề thi/audio. Trước merge, kiểm tra GitHub Settings → Pages. Nếu Pages đang tự xuất bản từ `main`, việc merge cũng có thể xuất bản; cần phê duyệt triển khai trước hoặc chuyển sang GitHub Actions theo bước sau trước merge. PR này không tự thay cấu hình Pages.
5. **Cấu hình Pages cho chạy thủ công:** GitHub repository → Settings → Pages → Build and deployment → Source: GitHub Actions. Trong Settings → Environments → `github-pages`, thêm người duyệt nếu gói GitHub cho phép. Không chạy deployment trong bước chuẩn bị.
6. **Triển khai sau xác nhận:** Actions → **Publish reviewed library to GitHub Pages (manual only)** → Run workflow → chọn `main` → nhập `DEPLOY HT ENGLISH LIBRARY` → Run workflow. Workflow chỉ nhận `main`, chạy kiểm thử, đóng gói `.site` rồi mới xuất bản. Không có trigger deploy khi push hoặc mở PR. Workflow không Publish Firebase Rules và không ghi dữ liệu Firebase thật.
7. **Kiểm tra sau triển khai:** mở URL Pages hiện tại (với repository này thường là `https://htenglish232.github.io/library/`; phải đối chiếu URL ở Settings → Pages), đăng nhập sai/đúng, giáo viên không quyền/khóa/thu hồi, Admin đọc và sửa thử một liên kết đã được phép rồi khôi phục, học sinh mở trực tiếp một link bài/audio cũ. Chỉ sửa danh mục thật khi bạn đã đồng ý. Không sửa 201 file đề trong thử nghiệm.

Nếu đăng nhập báo miền chưa được cho phép, kiểm tra Firebase Console → Authentication → Settings → Authorized domains. Giữ `htenglish232.github.io`; chỉ thêm `localhost` nếu cần chạy gói Windows và Console chưa có tên miền này. Không dùng `file://` để mở Admin.

## Khôi phục khi gặp lỗi triển khai

- Khi Lưu bị lỗi quyền hoặc xung đột: không nhập lại/xóa tài liệu. Tải bản nháp JSON, kiểm tra Rules và bản hiện tại. Giao dịch lỗi không tạo bản sao một phần.
- Khi danh mục mới sai: dùng lịch sử hoặc JSON đúng, khôi phục vào nháp và Lưu thành phiên bản mới. Bản sai cũng được giữ trong lịch sử để đối chiếu.
- Khi cần khóa chỉnh sửa tạm thời: sau phê duyệt, dùng Rules cũ chỉ cho tạo mới và không cập nhật/xóa. Quyền đọc danh mục/giáo viên vẫn giữ. Giữ giao diện mới có thể đọc schema v2; giao diện thử nghiệm cũ chỉ hiểu v1 sẽ không đọc được v2.
- Không quay về frontend thư viện công khai cũ để sửa một lỗi đăng nhập. Với lỗi frontend, sửa/khôi phục bản có đăng nhập và có khả năng đọc cả v1/v2, rồi chạy lại workflow thủ công sau phê duyệt. Không tự động chạy lại deploy, xóa dữ liệu hoặc hạ schema.
- Công cụ rollback offline cũ chỉ tạo phương án. Không thực thi đề xuất xóa hoặc ghi đè từ công cụ đó trong giai đoạn này; khôi phục danh mục bằng phiên bản mới là phương án ưu tiên.
