# HT English Library — hướng dẫn thử nghiệm Firebase

Bản này nằm trên nhánh `firebase-auth-trial`. Chưa đưa lên GitHub Pages chính thức, chưa áp dụng Security Rules và chưa nhập dữ liệu vào dự án Firebase thật. Không cần nâng gói Spark để dùng chức năng hiện tại.

Báo cáo chuẩn bị áp dụng mới nhất: `BAO_CAO_TRUOC_AP_DUNG_FIREBASE.md`. Phương án khôi phục: `PHUONG_AN_KHOI_PHUC_FIREBASE.md`. Hiện trạng đã được chủ dự án xác nhận trong Console: `(default)` trống, chỉ có HT English Library Web và Rules chặn toàn bộ. Chỉ thay đổi Firebase thật sau xác nhận cuối cùng.

## 1. Hiểu cách hoạt động

- Giáo viên đăng nhập bằng email và mật khẩu của tài khoản Firebase riêng.
- Đăng nhập thành công chưa đủ: giáo viên phải có quyền thư viện ở trạng thái **Đang hoạt động**.
- Danh mục được tải từ Firestore sau khi Firebase kiểm tra quyền. Không còn 201 đường dẫn nằm trong `index.html` hoặc gói JavaScript của giao diện.
- Học sinh vẫn mở link bài tập trực tiếp. Đề, audio, chấm điểm và nút về trang chủ không thay đổi.
- Admin chính là UID `4Y82k6RBaRUPflZriPsUvQv1qKj2`, được xác định trong Security Rules. Không có nút tự cấp quyền Admin. Email hoặc một trường `role` không thể thay thế UID này.
- Không lưu mật khẩu, khóa Admin SDK hoặc file service account. `assets/firebase-config.js` chứa cấu hình Web App công khai, bao gồm API key dùng cho ứng dụng web. Không bật Analytics hoặc Storage.

## 2. Tạo và quản lý giáo viên

Tạo tài khoản đăng nhập tại Firebase Console → dự án **ht-english-library** → Authentication → Users → Add user. Đây là thao tác thật: chỉ thực hiện sau khi bạn quyết định bắt đầu sử dụng. Giáo viên nên tự đặt mật khẩu riêng bằng liên kết đặt lại mật khẩu; không gửi mật khẩu vào mã nguồn hoặc chat.

Sau khi có tài khoản, sao chép UID trong Console. Đăng nhập `admin.html` bằng tài khoản Admin, điền đúng UID, email và tên giáo viên, rồi chọn **Cấp quyền**. Giao diện không có quyền tra cứu danh sách tài khoản Authentication; Admin phải đối chiếu UID với Console. Email và tên trong danh sách chỉ để nhận biết; quyền được gắn với UID.

| Nút trên trang Admin | Kết quả |
| --- | --- |
| Cấp quyền | UID được đọc danh mục |
| Khóa | UID bị ngừng đọc danh mục, nhưng tài khoản đăng nhập vẫn tồn tại |
| Mở khóa / cấp lại | Khôi phục quyền đọc |
| Thu hồi | Giữ bản ghi ở trạng thái đã thu hồi và ngừng quyền đọc |

Để vô hiệu hóa hoặc xóa **tài khoản đăng nhập**, dùng Authentication → Users trong Firebase Console. Nếu muốn chặn ngay phiên đang đăng nhập, **khóa/thu hồi quyền thư viện trước**, rồi vô hiệu hóa tài khoản. Việc vô hiệu hóa Authentication riêng lẻ có thể chưa làm token đã phát hành hết hiệu lực ngay.

Admin không quản lý chính tài khoản Admin qua danh sách giáo viên. Thay Admin cần quy trình riêng: xác minh UID mới, cập nhật Rules và cấu hình giao diện, kiểm tra rồi áp dụng có chủ ý.

## 3. Kiểm tra cục bộ trước khi áp dụng thật

Phần này dành cho người hỗ trợ kỹ thuật. Mở terminal ở thư mục repository; dùng checkout hiện có, không cần tạo worktree.

Cần Node.js 24, Java 21, Python 3, Python Playwright và Chromium tại `/usr/bin/chromium`. SDK Firebase được đóng gói tại chỗ để giao diện không phụ thuộc CDN.

```sh
npm ci
npm run build
npm run check:catalog
node --test tests/catalog.test.mjs
npm run test:emulators
```

Firebase Emulator cần tải công cụ chính thức từ `storage.googleapis.com`. Nếu môi trường chặn tên miền này, phải cho phép tải trước khi chạy các kiểm tra Rules. Không tắt kiểm tra chứng chỉ hoặc checksum.

Nếu đã cho phép Google Storage mà máy vẫn báo HTTP 403, có phương án thay thế đã chuẩn bị:

```sh
python3 tools/test-emulators-official.py
```

Công cụ dùng Firestore Emulator 1.22.0 từ gói Cloud SDK **chính thức của Google** trên `dl.google.com`, xác minh SHA-256 của cả gói tải và file JAR, rồi chạy cùng bộ kiểm tra Rules và trình duyệt. Không sửa checksum của Firebase CLI, không thay file công cụ bằng bản chưa xác minh. Firestore chạy trực tiếp qua điểm khởi động Java được Google cung cấp; Authentication vẫn chạy bằng Firebase CLI. Cảnh báo Emulator hub không liệt kê Firestore là dự kiến vì Firestore được khởi động riêng. Lệnh tự dừng các dịch vụ do nó tạo khi kiểm tra xong.

Danh mục được bảo toàn theo hai cách: dữ liệu xuất phải khớp chính xác bản `DATA` gốc, còn thứ tự hiển thị phải khớp trang web gốc. Trang gốc đã sắp xếp Unit theo số khi hiển thị; việc này được giữ nguyên, kể cả khi thứ tự Unit lưu trong dữ liệu khác thứ tự hiển thị.

Trong cloud có thư mục nhà chỉ đọc, dùng:

```sh
npm ci --cache /tmp/library-npm-cache
FIREBASE_EMULATORS_PATH=/tmp/library-firebase-emulators XDG_CONFIG_HOME=/tmp/library-firebase-config npm run test:emulators
```

Emulator dùng dự án giả `demo-ht-english-library`, tài khoản thử và mật khẩu ngẫu nhiên. Bài kiểm tra trình duyệt chặn mọi yêu cầu mạng ngoài máy cục bộ, và thay cấu hình emulator trong phản hồi kiểm thử; không sửa cấu hình thật trên đĩa.

Kiểm tra Rules bao gồm người chưa đăng nhập, giáo viên không có quyền, giáo viên bị khóa/thu hồi, đọc quyền người khác, tự cấp quyền, giả Admin, cấu trúc dữ liệu sai và quyền quản trị hợp lệ. Kiểm tra trình duyệt bao gồm sai mật khẩu, tài khoản Authentication bị vô hiệu hóa, toàn bộ 201 đường dẫn đúng thứ tự, quyền thay đổi khi giáo viên đang mở trang, công cụ nhập, đăng xuất và bài tập/audio mở trực tiếp.

`npm run check:catalog` so sánh với bản gốc tại commit `8c6361c8cd85831097f28419bcbdaa5b31601bfc`, đối chiếu SHA-256, kiểm tra file đích tồn tại và bảo đảm các file đề/audio/chấm điểm không đổi.

Bộ kiểm tra Grade 7 cũ ở `grade-7/De_thi_GHK_1/tests/browser_checks.py` có giả định word-chip đã lỗi thời; lỗi này đã có trước thay đổi Firebase. Không sửa bài tập hoặc bộ kiểm tra cũ trong nhánh này.

## 4. Những thay đổi Firebase thật cần bạn duyệt trước

Chưa thực hiện các bước dưới đây. Cần bạn xác nhận trước khi áp dụng Rules hoặc nhập dữ liệu thật.

Security Rules dự kiến thay toàn bộ bộ quy tắc Firestore hiện tại bằng `firestore.rules`. Quy tắc chỉ mở `libraryMembers/{UID}` và `libraryCatalog/current`; các đường dẫn khác bị từ chối. **Trước khi thay, phải sao lưu Rules đang dùng và kiểm tra dự án có ứng dụng/bộ sưu tập nào khác cần truy cập hay không.** Nếu có, cần hợp nhất quy tắc thay vì thay toàn bộ. Mã đang đặt mặc định CLI là dự án demo để tránh thao tác nhầm.

Sau khi bạn xác nhận, vào Firebase Console → Firestore Database → Rules, lưu lại bản Rules cũ, dán nội dung đã duyệt và chọn Publish. Không cần đăng nhập Firebase CLI hoặc tải service account để làm bước này.

Dữ liệu dự kiến gồm:

| Đường dẫn Firestore | Dữ liệu |
| --- | --- |
| `libraryCatalog/current` | Một bản danh mục gốc đủ 201 đường dẫn, thứ tự nguyên vẹn, số lượng, mã SHA-256 và thời gian cập nhật |
| `libraryMembers/{UID giáo viên}` | Tên, email, trạng thái quyền và thời gian cập nhật; không có mật khẩu |

Danh mục lưu trong trường chuỗi `dataJson` để giữ thứ tự và tránh hạn chế mảng lồng nhau của Firestore. Mỗi lần tải danh mục cần đọc một tài liệu; việc kiểm tra quyền giáo viên có thể phát sinh lượt đọc thêm. Kích thước được công cụ kiểm tra và giới hạn dưới 200 KB.

Trước khi nhập, kiểm tra `libraryCatalog/current` đã tồn tại chưa. Nếu tồn tại, xuất/sao lưu nội dung trước. Công cụ nhập sẽ ghi thay thế tài liệu này; không đụng đến các bộ sưu tập khác.

## 5. Nhập danh mục sau khi đã được chấp thuận

Người hỗ trợ chạy website cục bộ từ gốc repository:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Sau khi được bạn duyệt và Rules đã áp dụng, mở `admin.html` trên máy đó bằng trình duyệt, đăng nhập Admin. Cấu hình mặc định trỏ tới **ht-english-library**; không nhầm với Emulator. Nếu đăng nhập cục bộ bị từ chối vì tên miền, kiểm tra Authorized domains và thêm `localhost` cho thử nghiệm; không cần thêm đường dẫn `/library/` vào tên miền.

Ở **Nhập danh mục đã kiểm tra**, chọn file `catalog/library-catalog.json`. Chọn file chỉ kiểm tra, chưa ghi dữ liệu. Công cụ kiểm tra đủ 201 đường dẫn riêng biệt và SHA-256 khớp bản gốc, bao gồm toàn bộ tiêu đề, đường dẫn và thứ tự.

Chỉ khi bạn cho phép nhập thật mới nhấn **Nhập danh mục vào Firestore**, xác nhận hộp thoại và gõ `ht-english-library`. Sau khi ghi, công cụ đọc lại từ máy chủ và kiểm tra tính chính xác. Nếu thao tác ghi hoặc đọc lại thất bại, không coi việc nhập là thành công; kiểm tra thông báo và trạng thái trong Console trước khi thử lại.

Công cụ đọc lại phiên bản tài liệu trong giao dịch trước khi ghi. Nếu tài liệu đổi sau lúc kiểm tra file, công cụ dừng và yêu cầu kiểm tra/sao lưu lại, không ghi đè phiên bản mới.

## 6. Chuẩn bị GitHub Pages — chưa triển khai

Không đổi nhánh Pages, không merge vào main, không chạy triển khai tự động trong giai đoạn thử nghiệm. Website chính thức hiện vẫn phục vụ phiên bản cũ.

Người hỗ trợ tạo thư mục website để bạn xem xét:

```sh
npm run build
node tools/prepare-site.mjs
```

Kết quả ở `.site/` gồm các bài tập/audio nguyên vẹn, `index.html`, `admin.html`, `home-button.js` và `assets/`. Không đưa `catalog/`, `tests/`, `tools/`, `node_modules/`, Rules hoặc tài liệu vào website. Lệnh chỉ chuẩn bị thư mục, không tải lên GitHub hay Firebase.

Khi bạn duyệt triển khai ở giai đoạn sau, GitHub Actions nên tải **nội dung `.site/`** làm Pages artifact. Không bật kiểu xuất bản toàn bộ gốc nhánh thử nghiệm, vì sẽ phục vụ cả file xuất danh mục. Nếu site hiện ở `https://htenglish232.github.io/library/`, phải giữ nguyên vị trí `/library/`; chuyển sang gốc tên miền sẽ đổi URL bài tập. Liên kết mới vẫn dùng đường dẫn tương đối nên tương thích vị trí hiện có.

Sau khi triển khai đã được cho phép, kiểm tra Admin, giáo viên hoạt động, giáo viên chưa cấp quyền, khóa/mở khóa/thu hồi, đăng xuất, sai mật khẩu và một link bài tập mở trong cửa sổ riêng tư. Chỉ xác nhận vận hành thật khi kiểm tra này hoàn thành.

## 7. Giới hạn cần biết

Đây là kiểm soát quyền đọc **danh mục đang phục vụ**. Bài tập và audio vẫn công khai theo yêu cầu. Nếu repository công khai, file xuất trong mã nguồn hoặc danh mục cũ trong lịch sử Git vẫn có thể được đọc; đăng nhập không xóa dữ liệu đã công bố.

Không thể thu hồi đường dẫn người dùng đã xem hoặc sao chép. Giao diện xóa danh mục khi mất quyền, đăng xuất hoặc chuyển tab; không dùng bộ nhớ Firestore ngoại tuyến bền vững. Firebase Rules vẫn là lớp quyết định quyền, dù ai đó sửa JavaScript trong trình duyệt.

Ưu tiên Spark: không Functions, không Admin SDK, không Storage. Hạn mức miễn phí có giới hạn; nếu vượt, dịch vụ có thể bị hạn chế. Theo dõi Usage trong Firebase Console. Không tự nâng gói thanh toán.

Không gửi mật khẩu hoặc khóa service account cho người hỗ trợ. Admin đăng nhập trực tiếp bằng biểu mẫu Firebase. Lưu bản Rules cũ để khôi phục khi cần; không khôi phục bằng cách mở quyền công khai cho Firestore.
