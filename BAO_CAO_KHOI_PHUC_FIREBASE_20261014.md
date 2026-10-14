# Báo cáo khôi phục Firebase – HT English

## Phạm vi và sao lưu

- Repository: `htenglish232/library`; dự án Firebase giữ nguyên `ht-english-library`.
- Nhánh thực hiện: `restore-firebase-auth`, bắt đầu từ main `946b05b6d128cd88ac8ba09431cb645ae80a453d`.
- Nhánh sao lưu trên GitHub: [`backup-main-before-firebase-restore-20261014`](https://github.com/htenglish232/library/tree/backup-main-before-firebase-restore-20261014), đã đối chiếu đúng SHA trước khi sửa.
- Main ban đầu: 315 file tracked, 209 HTML, 74 MP3, 1 WAV, 1 WMA, 15 WOFF2; danh mục thực tế 207 liên kết.
- Working tree tracked ban đầu sạch. `node_modules` là phụ thuộc cục bộ từ lần thiết lập môi trường, được giữ nguyên và nay được `.gitignore` khôi phục bỏ qua.
- Không reset, force push, thay toàn bộ repository, merge vào main hoặc triển khai website/Rules.

## 1. File Firebase đã khôi phục

Khôi phục chọn lọc 52 file còn thiếu từ `firebase-auth-trial` (37722c1118a5041dc8531946fef1f81b8522292a), không ghi đè file có sẵn:

- `.firebaserc`
- `.github/workflows/firebase-trial-checks.yml`
- `.github/workflows/pages-manual.yml`
- `.gitignore`
- `BAO_CAO_NANG_CAP_DANH_MUC.md`
- `BAO_CAO_TRUOC_AP_DUNG_FIREBASE.md`
- `HUONG_DAN_FIREBASE.md`
- `KET_QUA_KIEM_TRA_FIREBASE.md`
- `PHUONG_AN_KHOI_PHUC_FIREBASE.md`
- `PUBLISH_FIREBASE_TUNG_BUOC.md`
- `QUAN_LY_DANH_MUC_VA_TRIEN_KHAI.md`
- `admin.html`
- `assets/admin.js`
- `assets/auth.css`
- `assets/catalog-data.js`
- `assets/catalog-editor.js`
- `assets/catalog-integrity.js`
- `assets/catalog-store.js`
- `assets/catalog-view.js`
- `assets/firebase-client.js`
- `assets/firebase-config.js`
- `assets/firebase-sdk.js`
- `assets/firebase-sdk.js.LEGAL.txt`
- `assets/library.js`
- `assets/session.js`
- `catalog/baseline.json`
- `catalog/library-catalog.json`
- `downloads/HT-English-Admin-thu-nghiem-Windows.zip`
- `downloads/README.md`
- `firebase.json`
- `firestore.indexes.json`
- `firestore.rules`
- `package-lock.json`
- `package.json`
- `tests/auth-browser.py`
- `tests/auth-login-browser.py`
- `tests/catalog.test.mjs`
- `tests/firestore-rules.test.mjs`
- `tests/preflight.test.mjs`
- `tests/reset-emulator-catalog.mjs`
- `tests/seed-emulator.mjs`
- `tools/build-admin-package.py`
- `tools/build.mjs`
- `tools/check-catalog.mjs`
- `tools/firebase-preflight.mjs`
- `tools/prepare-firebase-rollback.mjs`
- `tools/prepare-site.mjs`
- `tools/sdk-entry.js`
- `tools/test-emulators-official.py`
- `tools/windows/HUONG_DAN_WINDOWS.txt`
- `tools/windows/MO_ADMIN.py`
- `tools/windows/MO_ADMIN_WINDOWS.cmd`

Trong số đó, các file quản lý danh mục và kiểm thử được tích hợp thêm để tương thích bản main mới. File cấu hình production, Project ID, Admin UID, `firestore.rules` và `firestore.indexes.json` giữ nguyên byte theo nhánh Firebase cũ.

## 2. File đang có trên main được chỉnh sửa

Chỉ `index.html`: giữ HTML/CSS và cấu trúc thư viện hiện tại, thêm ô đăng nhập/thông tin phiên, cổng phân quyền, đăng xuất và liên kết Admin. Dữ liệu DATA hiện tại được lưu đầy đủ trong `catalog/current-library-catalog.json` và kiểm tra bằng `catalog/current-baseline.json`; renderer được nối qua `assets/catalog-view.js` và `assets/library.js` thay cho script inline.

Các bổ sung khác đều là file mới hoặc file Firebase vốn đã mất trên main. Không sửa file đề thi.

## 3. Các cập nhật mới được bảo toàn

- Unit 13–18 Grade 5 và đúng tên file có khoảng trắng của Unit 18.
- Mọi bản sửa Grade 6/7/8, Trực Tuấn lớp 8 và file thử nghiệm (2).
- `assets/submission-identity.js`, `.css`, kiểm tra tên trước nộp, điểm cá nhân hóa, mã lượt nộp và bản sửa hộp xác nhận lớp 7.
- Tất cả file HTML/audio/hình ảnh/font/tài liệu tracked hiện có, trừ index đã tích hợp theo yêu cầu.
- Đối chiếu SHA Git blob: 314/314 file main ngoài index không đổi byte nào; không xóa hoặc di chuyển file.

## 4. Danh mục và tài nguyên

- `npm run check:catalog` qua: 207 liên kết riêng biệt, đúng dữ liệu và thứ tự main; tất cả đích HTML tồn tại.
- Artifact `.site` được tạo cục bộ, chưa upload/publish: 207/207 URL HTML trả HTTP 200, cùng các asset Firebase và cá nhân hóa.
- JavaScript/JSON và mọi import tương đối đã kiểm tra; danh mục và cấu trúc folder được so với index gốc trong trình duyệt.
- Catalog export, Tools và Security Rules không được đưa vào artifact Pages.

### Tương thích danh mục Firebase cũ

Không sửa hash/count 201 của schema v1 vì dữ liệu đã có và Rules cũ phụ thuộc nó. Bản main 207 bài được bảo toàn riêng; client bổ sung sáu bài mới khi danh mục server chưa tiếp nhận bản phát hành này. Không tự ghi danh mục, tài khoản hoặc quyền lên Firebase.

Admin có nút **Bổ sung bài mới từ GitHub vào bản nháp**. Chỉ bấm nút này vẫn chưa ghi dữ liệu. Khi Admin chủ động Lưu, giao dịch cũ sao lưu nguyên tài liệu trước đó vào lịch sử, kiểm tra phiên bản và lưu bản nháp. Thông tin đã tiếp nhận bản phát hành nằm bên trong `dataJson`, không thêm field Firestore và không thay Rules. Sau bước tiếp nhận, việc Admin ẩn/xóa/sắp xếp bài được tôn trọng, không tự thêm lại bài đã xóa. Catalog v1/v2 dạng mảng cũ vẫn đọc được.

Nếu tài liệu danh mục chưa tồn tại, ứng dụng báo cần Admin nhập; không tự tạo hoặc ghi đè. Công cụ nhập nguyên bản vẫn CREATE ONLY và dừng khi tài liệu đã tồn tại. Không tự reset danh mục server thành 207 bài: giữ nguyên mọi mục tùy chỉnh của Admin.

## 5. Kết quả Firebase cục bộ

- SDK build thành công bằng npm lockfile đã khôi phục.
- 17/17 test chuẩn bị: legacy hash, catalog động, bổ sung release, tôn trọng ẩn/xóa sau tiếp nhận, chống payload lỗi, preflight và rollback chỉ đọc/offline.
- 18/18 test Firestore Rules trên emulator: anonymous/unapproved/locked/revoked bị từ chối; giáo viên chỉ đọc quyền mình/danh mục; không tự cấp quyền; Admin cố định; schema, transaction, history và stale revision được kiểm tra.
- 23/23 tình huống Chromium: đăng nhập đúng/sai, teacher denied Admin, cấp/khóa/mở/thu hồi quyền, catalog/import create-only, editing/hidden/backup/history/concurrency, manual release staging không ghi trước Save, lưu giữ nguyên snapshot cũ, xóa bài sau tiếp nhận, tải lại giữ phiên và xác minh quyền lại, logout.
- GitHub Pages prefix `/library/` được mô phỏng và kiểm tra. Giao diện desktop/mobile đạt các assertion responsive; học sinh mở bài trực tiếp, nộp bài có tên, xem điểm và tải MP3 được.
- 14/14 đề GHK1 Grade 7 qua regression quên tên → nhập lại → nộp: giữ bài viết/chọn đáp án/sắp xếp từ và hiện đầy đủ lời giải.
- Emulators dùng `demo-ht-english-library` cục bộ; trình duyệt chặn mọi request ngoài loopback. Firestore emulator chính thức được kiểm tra SHA-256. Không có thao tác Firebase production.

## 6. Giới hạn và việc chưa xác minh

- Preflight production không khởi tạo được phiên Google operator. Chưa xác minh trạng thái thực tế của Auth users, Firestore data, active Rules, Authorized Domains, IAM hoặc hoạt động dịch vụ `ht-english-library`.
- Test Rules dùng bản Rules khôi phục trên emulator; không chứng minh Rules đang Publish trên production giống bản này. Không triển khai Rules.
- Chưa kiểm tra Safari/iOS/Firefox trực tiếp. Chưa công bố hoặc kiểm chứng website thật.
- Bảo vệ bằng Firebase áp dụng cho danh mục/quyền giáo viên và Admin. Các bài HTML/audio trên GitHub Pages vẫn là file công khai có thể mở trực tiếp theo thiết kế hiện tại; không tuyên bố khóa file bằng Auth. GitHub repository/public asset nguồn cũng không phải kho bí mật.
- Phiên bản Admin cũ không đọc được metadata release dạng mới sau khi Admin chủ động tiếp nhận; cần sử dụng bộ mã đã khôi phục đồng bộ, tải lại các tab/gói Admin cũ. Mọi snapshot lịch sử vẫn được giữ nguyên.
- Đã push nhánh thử nghiệm và thử POST tạo draft PR vào `main`; GitHub API trả `Forbidden`. Chưa có PR được tạo. Nhánh đã đẩy là bản review, cần tạo PR qua giao diện GitHub. Không coi link compare/create là PR đã tạo.

## 7. Bàn giao

Main không thay đổi và vẫn ở `946b05b6d128cd88ac8ba09431cb645ae80a453d`. Chỉ commit/push `restore-firebase-auth`. Không merge hoặc triển khai. Nhánh backup đã được xác nhận trên GitHub. Gói Windows Admin đã được tạo lại từ bộ mã vừa kiểm thử và xác minh nội dung/checksum.

Review và tạo PR tại [compare với main](https://github.com/htenglish232/library/compare/main...restore-firebase-auth?expand=1), chọn **Create pull request**. Đây là trang tạo PR, không phải PR đã tồn tại; phần tạo PR tự động đang bị chặn bởi API.

Trước khi merge/publish, cần xác minh trạng thái Firebase thật bằng Console/phiên Google hợp lệ, đối chiếu Rules và dữ liệu hiện có. Mọi cập nhật Rules production cần phê duyệt riêng. Nhánh có workflow kiểm tra không deploy; workflow Pages khôi phục chỉ chạy thủ công trên main với câu xác nhận.
