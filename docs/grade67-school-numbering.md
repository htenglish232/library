# Phân loại GHK1 lớp 6 và lớp 7

Nhánh `feature/grade67-school-exam-numbering`, bắt đầu từ main `808d2a6` đã áp dụng cách nhóm lớp 8. Chỉ nâng cấp lớp trình bày; chưa merge hoặc deploy.

## Kiểm kê trước thay đổi

| Khối | Thư mục nguồn | HTML đề trong catalog | Trường | Game GHK1 | Chưa xác định trường |
| --- | --- | ---: | ---: | ---: | ---: |
| Grade 6 | `grade-6/De_thi_GHK_1/` | 16 | 14 | 0 | 0 sau xác nhận của người dùng |
| Grade 7 | `grade-7/De_thi_GHK_1/` | 14 | 14 | 0 | 0 |

Quét các thư mục lớp 6/7, đối chiếu HTML GHK1 với catalog: đúng 30 HTML đề đã có, không có HTML hỗ trợ/game GHK1 bị tính thành đề. Không đưa các bài game ngữ pháp trong HTBT vào đây. Đủ 42 tham chiếu audio tồn tại (40 MP3, 1 WAV, 1 WMA), giữ nguyên đường dẫn và byte.

Kiểm kê gồm tên trường, tên file, loại tài liệu, số đề, URL, SHA-256, tiêu đề HTML, nguồn xác nhận trường và audio: [grade67-exam-inventory.json](grade67-exam-inventory.json). Mỗi liên kết dưới đây là một mục đã có trong catalog, không tạo thêm đề/game.

### Xác nhận và trường hợp cần lưu ý

- `grade-6/De_thi_GHK_1/7_THCS_Liem_Hai/7 THCS Liem Hai.html`: catalog ghi THCS Liêm Hải, HTML ghi THCS Trực Thắng.
- `grade-6/De_thi_GHK_1/12_THCS_Truc_Hung/12 THCS Truc Hung.html`: catalog ghi THCS Trực Hùng, HTML ghi Trực Hưng.
- Đã hỏi người dùng; chỉ đạo được xác nhận: **“Giữ tên trường theo catalog hiện tại”**. Vì vậy hai mục vẫn thuộc Liêm Hải và Trực Hùng, không sửa trường trong HTML gốc. Mỗi trường này có số 1/2 theo thứ tự catalog đã có.
- Lớp 7 Đào Sư Tích thiếu “THCS” trong nhãn catalog, nhưng `<h2>` và metadata HTML ghi rõ **THCS Đào Sư Tích**. Chỉ bổ sung tiền tố cho tên hiển thị, không thay dữ liệu nguồn.
- Không có file trùng toàn bộ SHA-256. Tuy nhiên văn bản hiển thị của `7_THCS_Liem_Hai` và `8_THCS_Truc_Thang` giống nhau sau khi loại nhãn của trình phát Listening Part 1/2. Báo cáo ghi nhận cặp này để quản trị rà soát. Không kết luận hai file có cùng toàn bộ đáp án/JavaScript/audio; không xóa, gộp, nhân bản hoặc thêm liên kết. Giữ hai mục đang có và tên trường theo xác nhận của người dùng.

## Danh sách lớp 6

| Trường | Đề hiện có | Game |
| --- | --- | --- |
| THCS Trực Cường | [Đề số 1](../grade-6/De_thi_GHK_1/1_THCS_Truc_Cuong/1%20THCS%20Truc%20Cuong.html) | Chưa có |
| THCS Cổ Lễ | [Đề số 1](../grade-6/De_thi_GHK_1/2_THCS_Co_Le/2%20THCS%20Co%20Le.html) | Chưa có |
| THCS Trực Tuấn | [Đề số 1](../grade-6/De_thi_GHK_1/3_THCS_Truc_Tuan/3%20THCS%20Truc%20Tuan.html) | Chưa có |
| THCS Trực Hùng | [Đề số 1](../grade-6/De_thi_GHK_1/4_THCS_Truc_Hung_%281%29/4%20THCS%20Truc%20Hung%20%281%29.html); [Đề số 2](../grade-6/De_thi_GHK_1/12_THCS_Truc_Hung/12%20THCS%20Truc%20Hung.html) | Chưa có |
| THCS Trung Đông | [Đề số 1](../grade-6/De_thi_GHK_1/5_THCS_Trung_Dong/5%20THCS%20Trung%20Dong.html) | Chưa có |
| THCS Liêm Hải | [Đề số 1](../grade-6/De_thi_GHK_1/6_THCS_Liem_Hai/6%20THCS%20Liem%20Hai.html); [Đề số 2](../grade-6/De_thi_GHK_1/7_THCS_Liem_Hai/7%20THCS%20Liem%20Hai.html) | Chưa có |
| THCS Trực Thắng | [Đề số 1](../grade-6/De_thi_GHK_1/8_THCS_Truc_Thang/8%20THCS%20Truc%20Thang.html) | Chưa có |
| THCS Trực Thuận | [Đề số 1](../grade-6/De_thi_GHK_1/9_THCS_Truc_Thuan/9%20THCS%20Truc%20Thuan.html) | Chưa có |
| THCS Phương Định | [Đề số 1](../grade-6/De_thi_GHK_1/10_THCS_Phuong_Dinh/10%20THCS%20Phuong%20Dinh.html) | Chưa có |
| THCS Trực Đạo | [Đề số 1](../grade-6/De_thi_GHK_1/11_THCS_Truc_Dao/11%20THCS%20Truc%20Dao.html) | Chưa có |
| THCS Đào Sư Tích | [Đề số 1](../grade-6/De_thi_GHK_1/13_THCS_Dao_Su_Tich/13%20THCS%20Dao%20Su%20Tich.html) | Chưa có |
| THCS Việt Hùng | [Đề số 1](../grade-6/De_thi_GHK_1/14_THCS_Viet_Hung/14%20THCS%20Viet%20Hung.html) | Chưa có |
| THCS Trực Thái | [Đề số 1](../grade-6/De_thi_GHK_1/15_THCS_Truc_Thai/15%20THCS%20Truc%20Thai.html) | Chưa có |
| THCS Trực Nội | [Đề số 1](../grade-6/De_thi_GHK_1/16_THCS_Truc_Noi/16%20THCS%20Truc%20Noi.html) | Chưa có |

## Danh sách lớp 7

| Trường | Đề hiện có | Game |
| --- | --- | --- |
| THCS Trực Thái | [Đề số 1](../grade-7/De_thi_GHK_1/1_THCS_Truc_Thai/1%20THCS%20Truc%20Thai.html) | Chưa có |
| THCS Trực Nội | [Đề số 1](../grade-7/De_thi_GHK_1/2_THCS_Truc_Noi/2%20THCS%20Truc%20Noi.html) | Chưa có |
| THCS Trực Cường | [Đề số 1](../grade-7/De_thi_GHK_1/3_THCS_Truc_Cuong/3%20THCS%20Truc%20Cuong.html) | Chưa có |
| THCS Trực Đại | [Đề số 1](../grade-7/De_thi_GHK_1/4_THCS_Truc_Dai/4%20THCS%20Truc%20Dai.html) | Chưa có |
| THCS Trung Đông | [Đề số 1](../grade-7/De_thi_GHK_1/5_THCS_Trung_Dong/5%20THCS%20Trung%20Dong.html) | Chưa có |
| THCS Liêm Hải | [Đề số 1](../grade-7/De_thi_GHK_1/6_THCS_Liem_Hai/6%20THCS%20Liem%20Hai.html) | Chưa có |
| THCS Trực Thuận | [Đề số 1](../grade-7/De_thi_GHK_1/7_THCS_Truc_Thuan/7%20THCS%20Truc%20Thuan.html) | Chưa có |
| THCS Cổ Lễ | [Đề số 1](../grade-7/De_thi_GHK_1/8_THCS_Co_Le/8%20THCS%20Co%20Le.html) | Chưa có |
| THCS Cát Thành | [Đề số 1](../grade-7/De_thi_GHK_1/9_THCS_Cat_Thanh/9%20THCS%20Cat%20Thanh.html) | Chưa có |
| THCS Phương Định | [Đề số 1](../grade-7/De_thi_GHK_1/10_THCS_Phuong_Dinh/10%20THCS%20Phuong%20Dinh.html) | Chưa có |
| THCS Trực Khang | [Đề số 1](../grade-7/De_thi_GHK_1/11_THCS_Truc_Khang/11%20THCS%20Truc%20Khang.html) | Chưa có |
| THCS Trực Hùng | [Đề số 1](../grade-7/De_thi_GHK_1/12_THCS_Truc_Hung/12%20THCS%20Truc%20Hung.html) | Chưa có |
| THCS Đào Sư Tích | [Đề số 1](../grade-7/De_thi_GHK_1/13_Dao_Su_Tich/13%20Dao%20Su%20Tich.html) | Chưa có |
| THCS Việt Hùng | [Đề số 1](../grade-7/De_thi_GHK_1/14_THCS_Viet_Hung/14%20THCS%20Viet%20Hung.html) | Chưa có |

Hiện không có game GHK1 cho hai lớp này. Không hiển thị nút game chờ hoặc tạo tài liệu giả.

## Cách triển khai và các file thay đổi

- `assets/catalog-view.js`: dùng lại `numberSchoolLessons` của lớp 8 cho các thư mục `exam-folder` có href lớp 6/7. Thêm duy nhất nhãn trường đã kiểm chứng từ HTML Đào Sư Tích lớp 7. Số được tính từ catalog đầy đủ trước khi lọc ẩn/tìm kiếm, riêng theo từng trường/khối/bộ đề.
- `assets/school-folders.js`: nhận nhãn trường đã xác minh, hỗ trợ nhóm **Đề thi chưa phân loại** khi nguồn thực sự chưa rõ trường. Không suy tên trường từ URL. Tên nguồn của đề chưa phân loại vẫn hiện dưới `Đề số N – Chưa phân loại`. Nhóm này không được đếm như một trường THCS. Mặc định của lớp 8 giữ nguyên.
- `assets/school-folders.css`: chỉ thêm kiểu chữ cho tên nguồn trong nhóm chưa phân loại; dùng lại toàn bộ bố cục thư mục và cặp đề/game lớp 8.
- `index.html`, `assets/library.js`: đổi phiên bản tải CSS/module giao diện, không đổi logic đăng nhập/đăng xuất hay kiểm tra quyền.
- `tests/school-folders.test.mjs`, `tests/grade67-numbering-browser.py`: kiểm tra dữ liệu thật, các trường có nhiều đề, nhãn Đào Sư Tích, trường chưa rõ, ẩn/tìm kiếm và tương thích tương lai.
- `tests/grade8-numbering-browser.py`: cập nhật phạm vi so sánh cũ, vì lớp 6/7 giờ có cách đánh số riêng; tiếp tục chạy toàn bộ kiểm tra lớp 8. Workflow Firebase chạy cả hai bộ kiểm thử và lưu ảnh/JSON; không deploy.
- Ba tài liệu kiểm kê/báo cáo trong `docs/` lưu kết quả và bằng chứng.

**Giữ nguyên byte** toàn bộ `grade-*`, catalog JSON, Firebase config/SDK/client, session, Admin/editor, catalog release/store, Rules, indexes, Hosting và `.firebaserc`. Đối chiếu với main xác nhận 350 file tài liệu/catalog/Firebase/quản trị được bảo toàn. Catalog vẫn đúng **212 liên kết**; không thay schema/hash/export v1/v2 hay cơ chế phát hành `releaseApplied`. Không ghi dữ liệu production.

## Khả năng mở rộng

Qua Admin, thêm HTML thật vào đúng thư mục `exam-folder`, nhập tên `Đề số 2 – THCS …` hoặc `Game đề số 2 – THCS …` và href thật. Thêm bộ GHK2/HK1/HK2 bằng thư mục catalog riêng; số đề bắt đầu lại trong từng trường/bộ đề. Không cần viết lại index.

Game được ghép theo thư mục nguồn và số đã ghi rõ. Nếu nhiều đề cùng thư mục, phải ghi rõ số trong tên để tránh mơ hồ; nếu chưa ghép được, giữ tên nguồn và không tự gán số. Khi muốn giữ số sau xóa/đổi thứ tự, đặt rõ “Đề số N” qua Admin. Các tên cũ dùng thứ tự hiện có trong catalog. Ẩn đề 1 hoặc tìm kiếm không làm đề 2 đổi thành đề 1.

## Kiểm thử

- `npm run check:catalog`: 212 URL tồn tại, không trùng.
- `npm run test:prepare`: **36 kiểm thử đạt**.
- Firebase Auth/Firestore Emulator: **18 kiểm thử Rules và 23 kịch bản trình duyệt đạt**, gồm đăng nhập/đăng xuất, cổng phân quyền, Admin cấp/khóa/thu hồi quyền, lưu/xuất bản catalog, lịch sử, lưu đồng thời và các game lớp 8.
- `python3 tests/grade67-numbering-browser.py`: **8 nhóm kiểm tra đạt**; đúng 30 đề/28 nhóm trường theo từng khối, 0 game giả, mở/đóng bằng chuột/bàn phím, tìm tên cũ/mới, ẩn đề vẫn giữ số, thư mục tương lai và nhóm chưa phân loại. Toàn bộ 30 HTML và 42 audio trả đúng byte dưới `/library/`; phát MP3 thật đại diện mỗi lớp thành công.
- Giao diện Grade 4/5/8 được so DOM chính xác với main trước thay đổi; không đổi. Các mục ngoài đề thi của lớp 6/7 cũng khớp DOM cũ. Kiểm tra 360/390/768/1280px không tràn ngang, không lỗi JavaScript/console ở giao diện catalog.
- `python3 tests/grade8-numbering-browser.py`: **7 nhóm hồi quy lớp 8 đạt**, gồm 19 đề/4 game/17 trường, cặp đề-game, số khi ẩn/tìm kiếm và mở liên kết.
- `python3 tools/verify-firebase-recovery.py`: nguồn cũ và bản nghe Trực Hùng mới vẫn nguyên byte, Firebase/Rules/Admin và catalog gốc khớp hash tin cậy.
- Báo cáo: [grade67-numbering-browser-report.json](grade67-numbering-browser-report.json). CI lưu thêm ảnh chụp và JSON.

Chạy với Node 24, Python 3.12, Java 21, Playwright 1.58 và Chromium. Bộ Firebase dùng `npm run test:emulators`; phương án Google Cloud SDK chính thức khi tải emulator bị chặn là `tools/test-emulators-official.py`.

## Giới hạn xác minh

Firebase được kiểm thử trên Emulator, không đăng nhập/đọc/ghi Firebase production trong lần này. Không chạy lại toàn bộ câu hỏi/chấm điểm của 30 đề; thay vào đó xác minh nội dung, script và audio gốc không đổi byte. Kiểm tra phát thực tế dùng MP3 đại diện; WAV/WMA đã xác minh HTTP/hash, chưa khẳng định khả năng giải mã/phát trên mọi trình duyệt. Phân loại/tên trường không sửa các khác biệt hoặc nội dung trùng trong đề gốc.

Chưa tự động merge, deploy website hoặc publish Rules. Cần duyệt PR và triển khai để bản web nhận thay đổi.
