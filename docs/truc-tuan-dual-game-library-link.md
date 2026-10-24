# Liên kết game Trực Tuấn hai chế độ vào thư viện

Nhánh `feature/add-truc-tuan-dual-game-to-library`, từ main `96cbe54` (đã merge game hai chế độ ở PR #34). Chưa merge hoặc triển khai nhánh liên kết này. Không đọc/ghi Firebase production và không publish Rules.

## Kết quả hiển thị

**Grade 8 → Đề thi GHK1 → THCS Trực Tuấn**:

1. **Đề số 1 – THCS Trực Tuấn** → `grade-8/De_thi_GHK1/1_THCS Truc Tuan/1. THCS Truc Tuan.html`.
2. **Game đề số 1 – THCS Trực Tuấn** → `grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-game-test.html`.
3. **Game đề số 1 – THCS Trực Tuấn (2 chế độ)** → `grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-dual-mode.html`.

Chỉ thêm một liên kết; export danh mục v2 tăng từ 212 lên **213**. Giữ nguyên 212 mục cũ, tên nguồn, thứ tự tương đối, URL đề/game cũ và các trường khác. Không sửa file game, dữ liệu 42 câu, MP3, khóa localStorage hoặc logic chấm/lưu tiến độ.

## Vì sao không chỉ sửa index

Index tải `assets/library.js`; sau khi Firebase xác minh quyền, thư viện đọc `libraryCatalog/current`, kiểm tra dữ liệu và gọi `releaseCatalogView`. Hàm này ghép các đợt liên kết chưa tiếp nhận vào **bản sao để hiển thị**, rồi renderer phân nhóm trường và đánh số. Admin lưu catalog v2 cùng metadata `releaseApplied`, có lịch sử/kiểm tra phiên bản. Trước đăng nhập, khi bị khóa/thu hồi hoặc sau đăng xuất không dựng các liên kết tài liệu.

Đợt mới dùng ID `53127f09114b784cf86528e5df88fbf89443b5d8`, thêm mục đúng nhóm lớp 8. Nếu Firebase đã có href này, không thêm bản trùng; cũng nhận diện URL tương đương có `%20` hoặc URL đầy đủ của Pages, nhưng không ghi đè href đã lưu. Tên, trạng thái ẩn và dữ liệu riêng của Admin được giữ nguyên. Các mục xóa sau khi tiếp nhận đợt cũ không bị khôi phục khi thêm đợt mới.

Renderer giữ hậu tố **(2 chế độ)**, vẫn ghép cùng đề số 1. Nhận diện `dual-mode.html` là game cả khi Admin sửa tên, tránh biến nó thành đề số 2. Tìm theo “2 chế độ”, tên trường hoặc tên đầy đủ đều tìm được.

## Các file đã chỉnh sửa

- `assets/catalog-release.js`: đợt bổ sung một link, khử trùng theo href tương đương, giữ các batch/metadata cũ.
- `catalog/current-library-catalog.json`: export v2 213 mục và hash mới; không thay export v1 hay Rules.
- `assets/school-folders.js`: giữ nhãn hai chế độ/nhóm trường/số đề, nhận diện loại game khi đổi tên.
- `assets/catalog-editor.js`: chỉ ghép các đợt chưa tiếp nhận; giữ metadata đã có. Cho tiếp nhận metadata khi link đã có sẵn để thao tác xóa sau đó vẫn có hiệu lực. Bấm bổ sung chỉ đổi bản nháp, chưa ghi Firebase trước khi bấm Lưu.
- `index.html`, `admin.html`, `assets/library.js`, `assets/admin.js`, `assets/catalog-view.js`: đổi phiên bản URL module để tải đồng bộ renderer và release mới, không thay luồng Authentication/phân quyền. Cache của các trang game và dữ liệu tiến độ không đổi.
- `tests/catalog-release.test.mjs`, `tests/school-folders.test.mjs`, `tests/auth-browser.py`, `tests/grade8-numbering-browser.py`, `tests/grade67-numbering-browser.py`: cập nhật kỳ vọng số liên kết, thêm kiểm thử game mới, trường/lớp khác và tiếp nhận/ẩn/hiện/xóa.
- `tests/seed-previous-dual-release.mjs`: fixture **chỉ Emulator**, mô phỏng catalog đã tiếp nhận các đợt cũ và trường hợp link đã có; không nhận endpoint/project production.
- Workflow Firebase hiện có thêm nhánh này vào danh sách kiểm thử khi push; không thêm bước deploy.

Đối chiếu main xác nhận **351 file đề/game/audio/Firebase/Security/legacy catalog** giữ nguyên byte. Đặc biệt Firebase project ID/config, client/SDK/session, Firestore Rules/indexes, Hosting và `.firebaserc` không thay đổi. Không thay Admin UID hoặc cấp quyền/tạo tài khoản production.

## Admin có cần thao tác không?

**Để học sinh thấy link:** sau khi nhánh được merge và website được triển khai, cơ chế release sẽ ghép liên kết mới vào giao diện từ catalog đang đọc trên Firebase. Không cần chạy script hay nhập lại dữ liệu production để link xuất hiện, miễn tài khoản/thư mục được phép hiển thị.

**Để ghi nhận đợt này chính thức và quản lý xóa bền vững:** Admin thực hiện qua trang quản lý hiện có:

1. Bấm **Bổ sung bài mới từ GitHub vào bản nháp**.
2. Kiểm tra nhóm Trực Tuấn, ba mục ở trên và trạng thái ẩn/hiện mong muốn. Nếu link đã có thì không thêm lần hai; chỉ tiếp nhận thông tin đợt phát hành.
3. Bấm **Lưu danh mục**. Chỉ bước này mới ghi Firebase, có lưu phiên bản trước theo cơ chế hiện có.

Sau khi tiếp nhận, Admin có thể sửa/ẩn/hiện/xóa game mới như các mục khác; tải lại không tự khôi phục mục đã xóa. Không nhập lại danh mục gốc 201 mục, không reset database, không deploy Rules chỉ để thêm liên kết.

## Kiểm thử đã chạy

- `npm run check:catalog`: **213 URL tồn tại, không trùng**; đủ đề/game cũ.
- `npm run test:prepare`: **41 kiểm thử đạt**, gồm catalog cũ/v2, đợt bổ sung một href, không trùng với href encoded/Pages đã có, ẩn/xóa sau tiếp nhận và đúng số/loại tài liệu.
- `node --test tests/dual-mode-progress.test.mjs`: **12 kiểm thử đạt**; không đổi dữ liệu hay namespace tiến độ.
- `tests/dual-mode-browser.py`: thao tác đủ **42 câu**, **12 nhóm HTTP đạt**, hai chế độ, XP một lần, profile/đề riêng, tải lại, ôn, hai MP3/tua/tốc độ/transcript, cảm ứng và `/library/`. Kiểm tra mở file:// vẫn bị Chromium administrator policy chặn và ghi skipped, không báo đạt; đây không phải đường dẫn Pages cần phát hành.
- Firebase Auth/Firestore Emulator: **18 kiểm thử Rules và 25 kịch bản trình duyệt đạt**. Mở game mới từ thư viện đã đăng nhập ở cả root và `/library/`, nạp 42 câu, hai mode/MP3 và reload giữ 10 XP; logout/thay đổi catalog không xóa bài lưu game. Xác minh trước đăng nhập không lộ danh mục, giáo viên bị chặn Admin, quản lý cấp/khóa/thu hồi/lưu/lịch sử vẫn hoạt động.
- Trên Emulator, catalog đã xóa game cũ/ẩn đề gốc vẫn được giữ như Admin đã đặt; tiếp nhận đợt mới chỉ thêm đúng một link. Ẩn/hiện/xóa game mới và reload đều đúng. Trường hợp Firebase đã có link: hiển thị một lần, tiếp nhận metadata không tăng count, xóa sau tiếp nhận không bị khôi phục.
- `tests/grade8-numbering-browser.py`: **7 nhóm đạt**; 17 trường/19 đề/5 game, 24 href lớp 8 trả đúng HTML; nhãn/tìm kiếm/mobile đều đúng.
- `tests/grade67-numbering-browser.py`: **8 nhóm đạt**, xác nhận các mục cũ Grade 4/5/8 (bỏ riêng link mới khi so snapshot) và toàn bộ Grade 6/7/vocabulary/grammar giữ nguyên, 30 đề và 42 audio vẫn mở đúng.
- `tools/verify-firebase-recovery.py`: kiểm tra nguồn cũ/Firebase/Rules/catalog gốc đạt. `tools/prepare-site.mjs` tạo artifact `.site` cục bộ, có game/JS/CSS/MP3, **không deploy**.

Các kiểm tra chạy cục bộ bằng Node 24, Python 3.12, Java 21, Playwright 1.58 và Chromium. Một ảnh thăm dò kết nối của SDK WebChannel được fixture trả GIF cục bộ, không chuyển yêu cầu ra Google; mọi endpoint ngoài khác vẫn bị chặn và kiểm tra. Chưa xác minh trạng thái CI từ GitHub hoặc danh mục/tài khoản production; kiểm thử Firebase dùng dự án demo và Emulator. Không báo URL công khai đã hoạt động khi chưa kiểm tra triển khai.

## URL dự kiến và bước còn lại

[Game Trực Tuấn hai chế độ sau khi phát hành](https://htenglish232.github.io/library/grade-8/De_thi_GHK1/1_THCS%20Truc%20Tuan/truc-tuan-dual-mode.html)

Đã kiểm tra phân giải URL bằng URL API và chạy thật dưới `/library/` cục bộ. Đây là **URL đích dự kiến**, chưa xác nhận trạng thái website đang phục vụ nó.

1. Duyệt và merge Pull Request của nhánh này.
2. Chạy workflow thủ công **Publish reviewed library to GitHub Pages (manual only)** trên main theo quy trình đang có. Nhánh này không tự chạy deploy.
3. Sau triển khai, đăng nhập thư viện → Grade 8 → Đề thi GHK1 → THCS Trực Tuấn → chọn **Game đề số 1 – THCS Trực Tuấn (2 chế độ)**.
4. Admin tiếp nhận/lưu đợt bổ sung nếu muốn ghi chính thức vào catalog server và quản lý xóa theo đợt. Nếu không thấy link, kiểm tra trạng thái ẩn của khối/thư mục/mục và quyền tài khoản, không khôi phục/reset toàn bộ dữ liệu.
