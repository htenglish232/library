# Toàn bộ game hai chế độ lớp 8

Baseline `main:bcf44e9` (đã merge PR #35). Nhánh `feature/grade8-all-dual-mode-games`. Không merge, không triển khai website, không đọc/ghi Firebase production.

## Kết quả và giới hạn

Kiểm kê trực tiếp: **19 HTML đề, 17 trường, 19 game hai chế độ**, gồm một Trực Tuấn hiện có và 18 bản mới. **793 câu: 732 câu tự chấm theo nguồn, 61 câu chờ giáo viên duyệt, XP tối đa cộng dồn 7.320**. Hai đề không có MP3 thật (Đào Sư Tích đề 1, Trung Đông): không hiển thị trình phát giả, có thông báo nhờ giáo viên cung cấp file; transcript gốc hiện sau khi kiểm tra.

Đây là kết quả hoàn thành vận hành và liên kết của 19 game, **không phải xác nhận toàn bộ đáp án đã được giáo viên duyệt**. 61 câu chờ không chấm đúng/sai và không cộng XP; đáp án/ghi chú nguồn vẫn được giữ. Trực Tuấn giữ nguyên bộ dữ liệu hiện hành, gồm các cảnh báo giáo viên từ giai đoạn trước. Tổng cộng có **87 câu được ghi chú** (kể cả câu vẫn chấm theo nguồn có cảnh báo), xem [teacher-review.json](teacher-review.json) với trường, số đề, số câu toàn đề, ID gốc, đáp án nguyên văn, trạng thái tự chấm và lý do.

Số câu lấy từ nguồn thực tế: Cát Thành **37**, Phương Định đề 2 **41**, Trực Hùng **43**, những đề khác **42**. Không tạo câu để bù lên 42, không lấy số đầu thư mục làm số đề trong trường. Cát Thành thực có 6 câu T/F + 5 câu nghe lựa chọn + 10 ngôn ngữ + 3 chia động từ + 10 đọc + 3 ghép từ; HTML không có phần viết lại câu.

## Bảng từng đề

Tất cả liên kết dưới đây là **URL dự kiến sau phát hành**, chưa xác nhận đang được website công khai phục vụ. “Đạt” là kiểm thử kỹ thuật theo dữ liệu nguồn; số câu chờ giáo viên ghi riêng.

| Trường | Số đề | Số câu | Game hai chế độ | Audio | Kiểm thử | Link |
|---|---:|---:|---|---|---|---|
| THCS Trực Tuấn | 1 | 42 | Có · tối đa 420 XP | 2 MP3 | Đạt | [Mở game](https://htenglish232.github.io/library/grade-8/De_thi_GHK1/1_THCS%20Truc%20Tuan/truc-tuan-dual-mode.html) |
| THCS Đào Sư Tích | 1 | 42 | Có · tối đa 420 XP | Không có MP3 | Đạt | [Mở game](https://htenglish232.github.io/library/grade-8/De_thi_GHK1/2_THCS%20Dao%20Su%20Tich/practice-dual-mode.html) |
| THCS Trung Đông | 1 | 42 | Có · tối đa 420 XP | Không có MP3 | Đạt | [Mở game](https://htenglish232.github.io/library/grade-8/De_thi_GHK1/3_THCS%20Trung%20Dong/practice-dual-mode.html) |
| THCS Trực Đại | 1 | 42 | Có · tối đa 420 XP | 2 MP3 | Đạt | [Mở game](https://htenglish232.github.io/library/grade-8/De_thi_GHK1/4_THCS%20Truc%20Dai/practice-dual-mode.html) |
| THCS Trực Thuận | 1 | 42 | Có · tối đa 320 XP | 2 MP3 | Đạt; 10 câu chờ | [Mở game](https://htenglish232.github.io/library/grade-8/De_thi_GHK1/5_THCS%20Truc%20Thuan/practice-dual-mode.html) |
| THCS Cát Thành | 1 | 37 | Có · tối đa 340 XP | 2 MP3 | Đạt; 3 câu chờ | [Mở game](https://htenglish232.github.io/library/grade-8/De_thi_GHK1/6_THCS%20Cat%20Thanh/practice-dual-mode.html) |
| THCS Trực Mỹ | 1 | 42 | Có · tối đa 390 XP | 2 MP3 | Đạt; 3 câu chờ | [Mở game](https://htenglish232.github.io/library/grade-8/De_thi_GHK1/7_THCS%20Truc%20My/practice-dual-mode.html) |
| THCS Phương Định | 1 | 42 | Có · tối đa 420 XP | 2 MP3 | Đạt | [Mở game](https://htenglish232.github.io/library/grade-8/De_thi_GHK1/8_THCS%20Phuong%20Dinh/practice-dual-mode.html) |
| THCS Phương Định | 2 | 41 | Có · tối đa 340 XP | 2 MP3 | Đạt; 7 câu chờ | [Mở game](https://htenglish232.github.io/library/grade-8/De_thi_GHK1/9_THCS_Phuong_Dinh/practice-dual-mode.html) |
| THCS Trực Đạo | 1 | 42 | Có · tối đa 340 XP | 2 MP3 | Đạt; 8 câu chờ | [Mở game](https://htenglish232.github.io/library/grade-8/De_thi_GHK1/10_THCS_Truc_Dao/practice-dual-mode.html) |
| THCS Trực Khang | 1 | 42 | Có · tối đa 420 XP | 1 MP3 dùng chung | Đạt | [Mở game](https://htenglish232.github.io/library/grade-8/De_thi_GHK1/11_THCS_Truc_Khang/practice-dual-mode.html) |
| THCS Trực Hùng | 1 | 43 | Có · tối đa 410 XP | 2 MP3 | Đạt; 2 câu chờ | [Mở game](https://htenglish232.github.io/library/grade-8/De_thi_GHK1/12_THCS_Truc_Hung/practice-dual-mode.html) |
| THCS Đào Sư Tích | 2 | 42 | Có · tối đa 390 XP | 1 MP3 dùng chung | Đạt; 3 câu chờ | [Mở game](https://htenglish232.github.io/library/grade-8/De_thi_GHK1/13_THCS_Dao_Su_Tich/practice-dual-mode.html) |
| THCS Việt Hùng | 1 | 42 | Có · tối đa 350 XP | 1 MP3 dùng chung | Đạt; 7 câu chờ | [Mở game](https://htenglish232.github.io/library/grade-8/De_thi_GHK1/14_THCS_Viet_Hung/practice-dual-mode.html) |
| THCS Trực Thái | 1 | 42 | Có · tối đa 390 XP | 2 MP3 | Đạt; 3 câu chờ | [Mở game](https://htenglish232.github.io/library/grade-8/De_thi_GHK1/16_THCS_Truc_Thai/practice-dual-mode.html) |
| THCS Trực Nội | 1 | 42 | Có · tối đa 350 XP | 1 MP3 dùng chung | Đạt; 7 câu chờ | [Mở game](https://htenglish232.github.io/library/grade-8/De_thi_GHK1/17_THCS_Truc_Noi/practice-dual-mode.html) |
| THCS Trực Cường | 1 | 42 | Có · tối đa 390 XP | 2 MP3 | Đạt; 3 câu chờ | [Mở game](https://htenglish232.github.io/library/grade-8/De_thi_GHK1/18_THCS_Truc_Cuong/practice-dual-mode.html) |
| THCS Trực Chính | 1 | 42 | Có · tối đa 370 XP | 2 MP3 | Đạt; 5 câu chờ | [Mở game](https://htenglish232.github.io/library/grade-8/De_thi_GHK1/19_THCS_Truc_Chinh/practice-dual-mode.html) |
| THCS Cổ Lễ | 1 | 42 | Có · tối đa 420 XP | 2 MP3 | Đạt | [Mở game](https://htenglish232.github.io/library/grade-8/De_thi_GHK1/20_THCS_Co_Le/practice-dual-mode.html) |

## Cách trích xuất và bảo toàn nguồn

- `tools/grade8-source-literals.mjs` dùng Acorn để phân tích các script inline và chỉ đọc các object/array, lời gọi chấm có tham số nguyên văn. Không chạy ứng dụng đề hoặc tải script ngoài. `acorn@8.15.0` là công cụ phát triển, không tải vào game.
- `tools/grade8-source-dom.js` dùng DOMParser trên HTML gốc để lấy câu hỏi/phương án, vị trí trong nguồn, chỉ dẫn/bảng/đoạn văn; giữ phần gạch chân phát âm. Kiểm tra không sót ô trả lời, không gán hai câu vào cùng card. Không tự sửa đáp án nghi vấn.
- `tools/build-grade8-dual-games.py` tạo dữ liệu và launcher theo từng đề. Ba pilot tái sử dụng dữ liệu đã có, đối chiếu toàn bộ object đáp án với HTML hiện tại. Trực Mỹ lấy nguyên các array nguồn tạo giao diện động. Các đề tĩnh lấy thứ tự theo DOM và ánh xạ thẻ từ từ cấu hình gốc. `sourceRaw`, SHA256 HTML/MP3 và vị trí/ID nguồn được lưu để đối chiếu. Trực Tuấn không tạo lại hoặc ghi đè.
- Dùng `python tools/build-grade8-dual-games.py --verify` để trích lại và đối chiếu mọi file sinh ra; báo lỗi khi số câu, thứ tự, nội dung, phương án, đáp án, ngữ cảnh, transcript hoặc tài nguyên thay đổi. Đợt pilot chạy/kiểm thử trước khi tạo các đề còn lại.
- Chỉ chấp nhận đáp án đầy đủ/biến thể ghi rõ trong nguồn. Không dùng phép `includes(keyword)` của các grader cũ để tự nhận đúng. Đáp án không thể ghép từ thẻ gốc, dữ liệu không rõ hoặc đáp án có diễn giải/biến thể chưa tách được đánh dấu để giáo viên duyệt, không sửa từ/đáp án để đạt đủ số.
- Dữ liệu đọc giữ nguyên HTML nội dung; bỏ CSS lớp nguồn và hành vi phát âm/nhập liệu của đề. Bài đọc luôn có nút thu gọn/mở rộng, không mất khi đổi câu. MP3 dùng đúng tên file, kể cả khoảng trắng; đề có một file chung vẫn nghe nguyên file và xem transcript gốc sau kiểm tra.

## Thay đổi giao diện và lưu tiến độ

Mỗi đề mới có `practice-dual-mode.html` và `practice-dual-data.js` trong thư mục nguồn của mình, dùng chung `dual-mode-engine.js`, `dual-mode.css`, `dual-progress.js`, `dual-store.js`, `model.js`. Không nhân bản engine. Launcher giữ bố cục Trực Tuấn, thay metadata, dữ liệu, số câu và link đề gốc. Giữ toàn bộ 19 HTML đề, 4 game cũ, tất cả MP3 và tài nguyên hiện có và các lớp khác nguyên byte.

`dual-store.js` thêm duy nhất hồ sơ đang dùng `htenglish:grade8:active-student:v1`, lưu cả tên lẫn mã. Khi mở game khác trên cùng website, trình duyệt và thiết bị, tên/mã được điền sẵn; vẫn để học sinh chọn bắt đầu/tiếp tục. **Đổi học sinh** chỉ bỏ hồ sơ đang dùng, không xóa bài lưu. Các khóa `htenglish:practice:v1:<examId>:<identity>` và schema tiến độ cũ giữ nguyên, không di chuyển/gộp/xóa dữ liệu. Đề, tên trùng nhưng mã khác, draft, mode, vị trí, đáp án lần đầu, XP và lượt ôn tách riêng. Reset có xác nhận, chỉ ảnh hưởng bài của hồ sơ đang chọn. Không thêm Firebase hoặc tài khoản riêng vào game.

Controller thêm tự điền hồ sơ, thông báo/hiện transcript cho đề thiếu MP3, và giữ lựa chọn chờ giáo viên không bị tô đúng/sai tùy tiện. Model cho phép câu pending không có đáp án máy và MP3 không có transcript. CSS dual thêm xuống dòng chuỗi dài, cuộn bảng trong vùng đọc trên điện thoại. Trực Tuấn giữ HTML, dữ liệu, hỗ trợ và tiến độ cũ; có kiểm thử hồi quy đầy đủ.

## Liên kết thư viện và Firebase

`assets/grade8-dual-links.js` định nghĩa 18 liên kết mới trong hai đợt (3 pilot + 15 còn lại), ID SHA1 ổn định từ danh sách đã duyệt. `assets/catalog-release.js` dùng cơ chế bổ sung hiện có; JSON v2 tăng **213 → 231**, không sửa catalog v1. Cả 213 mục cũ, tên, thứ tự tương đối, trạng thái ẩn và chức năng Admin được giữ nguyên. Mỗi game ghi đúng số đề trong trường; renderer có sẵn ghép vào đúng cặp đề/game, kể cả hai đề Đào Sư Tích/Phương Định. Href tương đương encoded/URL Pages đã có không được thêm trùng. Các đợt đã tiếp nhận giữ quyền xóa của Admin, không khôi phục lại bài đã xóa.

`index.html`, `admin.html`, các import ở `assets/library.js`, `assets/catalog-view.js`, `assets/admin.js`, `assets/catalog-editor.js` chỉ đổi phiên bản URL module để tải catalog mới; không đổi màu, bố cục, Authentication, quyền Admin hay cách mở tài liệu. Chỉ sau xác minh đăng nhập/quyền mới dựng các liên kết. Không có thao tác ghi Firebase production trong lần này.

Sau merge + deploy, cơ chế release ghép link mới vào giao diện đã đăng nhập, không cần reset database hoặc nhập lại catalog. Để tiếp nhận chính thức và quản lý xóa bền vững, Admin dùng **Bổ sung bài mới từ GitHub vào bản nháp → kiểm tra → Lưu danh mục**. Trước khi bấm Lưu chỉ là draft. Trường hợp đã có href thì tiếp nhận metadata mà không tạo bản trùng. Không cần cập nhật Rules, project ID, Auth hay quyền Admin để thêm game.

## Kiểm thử thực tế

- Ba pilot: **3 game/127 câu**, hai mode, XP, audio, mobile, lưu/khôi phục, tách học sinh/mã đều đạt trước khi mở rộng.
- `tests/grade8-all-dual-browser.py`: **19 game/793 câu** chạy qua giao diện Chromium dưới `/library/`, đối chiếu mọi prompt/options/ngữ cảnh với dữ liệu đã trích; kiểm tra đúng/pending, XP một lần, chuyển mode, question navigation, reload/resume, mã học sinh, tách tiến độ, reset, audio thật/tua/tốc độ/transcript và mobile 390px. Không lỗi JS/console, request ngoài hay tài nguyên thiếu. [Kết quả từng game](browser-report.json).
- Kiểm tra bổ sung sau khi thêm transcript không kèm MP3: **2 game/84 câu**, xác nhận vẫn không có player giả và transcript gốc mở sau khi kiểm tra.
- `npm run test:prepare`: **41 kiểm thử đạt**. `node --test tests/dual-mode-progress.test.mjs tests/grade8-all-dual.test.mjs`: **18 kiểm thử đạt** (14 model/storage + 4 kiểm tra toàn bộ danh mục, nguồn và bảo toàn file).
- `npm run check:catalog`: **231 href duy nhất tồn tại**. Kiểm tra byte với `bcf44e9` giữ nguyên toàn bộ file tài liệu/audio/game cũ và Firebase/Rules/session/catalog store; chỉ bốn thành phần dual dùng chung được phép nâng cấp. Không sửa `dual-progress.js` hoặc khóa bài lưu Trực Tuấn.
- `tests/grade8-numbering-browser.py`: **7 nhóm đạt**, 17 trường/19 đề/23 game (19 dual + 4 cũ), đủ 42 URL HTML, tìm kiếm và 360/390/768/1280px. `tests/grade67-numbering-browser.py`: **8 nhóm đạt**, các mục cũ Grade 4/5/8, 30 đề và 42 audio Grade 6/7 và phần từ vựng/ngữ pháp giữ nguyên.
- Firebase Auth/Firestore Emulator: **18 kiểm thử Rules + 27 tình huống trình duyệt đạt**, gồm trước đăng nhập không lộ tài liệu, tài khoản bị khóa/thu hồi, quyền Admin, catalog CRUD/lịch sử, mở cả 19 game từ index sau đăng nhập, tiếp nhận hai đợt đúng 18 href, không ghi trước Save, giữ mục ẩn/xóa cũ và xóa bền vững sau tiếp nhận. Một ảnh thăm dò kết nối SDK được trả cục bộ; không request nào được chuyển đến production.
- Hồi quy Trực Tuấn: `tools/verify-truc-tuan-dual-source.py` khớp đủ **42 câu, 2 đoạn đọc, 2 transcript và SHA256 hai MP3**; `tests/dual-mode-browser.py` đạt **12 nhóm HTTP**, gồm toàn bộ câu, ôn/reset/touch/storage bị chặn/xung đột tab. Kiểm tra `file://` bị chính sách Chromium chặn, ghi **skipped**, không báo đạt. Đường HTTP/GitHub Pages mới là mục tiêu phát hành.
- `tools/verify-firebase-recovery.py`, `npm run build`, `tools/prepare-site.mjs` đạt; artifact `.site` chỉ tạo cục bộ. Các dependency Firebase và bundle JS không đổi; file license được build lại theo thứ tự khác đã trả về nguyên bản.

Workflow kiểm thử dual được mở rộng để kiểm tra tất cả đề, dùng Acorn, kiểm tra bảo toàn mới theo baseline `bcf44e9` và chạy cả bộ hồi quy Trực Tuấn. Guard giai đoạn 1 vẫn giữ cho snapshot cũ; bản mở rộng được kiểm tra bằng guard phạm vi mới thay cho điều kiện “chỉ thêm file Trực Tuấn” của nhiệm vụ trước. **Không thay workflow triển khai website** và không bổ sung deploy.

Các kiểm tra trên chạy cục bộ bằng Node 24, Python 3.12, Chromium/Playwright 1.58 và Firebase Emulator. Chưa xác minh trạng thái CI trên GitHub hoặc URL/tài khoản production.

## Xuất bản

1. Duyệt Pull Request, đặc biệt [danh sách câu cần duyệt](teacher-review.json); giáo viên có thể bổ sung bộ đáp án được xác nhận trong một thay đổi riêng.
2. Merge vào `main` khi đồng ý, sau đó chạy workflow **Publish reviewed library to GitHub Pages (manual only)** theo quy trình hiện tại.
3. Admin tiếp nhận/lưu hai đợt catalog nếu muốn ghi nhận chính thức; không reset hoặc khôi phục toàn bộ Firebase.
4. Kiểm tra website thật: đăng nhập → Grade 8 → Đề thi GHK1 → trường → Game đề số tương ứng (2 chế độ). Các folder/item bị Admin ẩn tiếp tục ẩn.
5. Hai đề thiếu MP3 cần giáo viên cung cấp file nếu muốn nghe audio thật. Những câu pending vẫn luyện được và xem đáp án tham khảo, nhưng chưa được cộng XP/chấm đúng sai cho tới khi được xác nhận.
