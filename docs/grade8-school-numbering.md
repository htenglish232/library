# Grade 8 — phân loại đề và game theo trường

Nhánh `feature/grade8-school-exam-numbering`, dựa trên main `a8a38ed` đã khôi phục Firebase. Chỉ đổi cách trình bày, không sửa dữ liệu catalog hoặc tài liệu. Chưa merge/deploy.

## Quét và đối chiếu nguồn

Đã đối chiếu thư mục `grade-8/De_thi_GHK1/` với `catalog/current-library-catalog.json`: **19 HTML đề, 4 HTML game, 17 trường**. Không có game nào khác để đưa thêm vào danh mục. Trực Tuấn giữ bản game đầy đủ 42 câu (`c59aa3f`, khôi phục từ lịch sử PR #23); ba game thử nghiệm giữ bản từ `7f466cf` (PR #28), riêng Trực Hùng dùng bản nghe riêng mới đã merge PR #30. Không chỉnh sửa các file này.

Nhãn “số 1, 2…” được tính **trong từng trường** theo thứ tự đề thực có trong catalog, không lấy số đầu thư mục làm số đề của trường. Vì vậy Đào Sư Tích và Phương Định có hai đề, những trường còn lại có một đề. Không đánh lại số hay đổi tên thư mục vật lý.

| Trường | Đề thi hiện có | Game hiện có |
| --- | --- | --- |
| THCS Trực Tuấn | [Đề số 1](../grade-8/De_thi_GHK1/1_THCS%20Truc%20Tuan/1.%20THCS%20Truc%20Tuan.html) | [Game đề số 1](../grade-8/De_thi_GHK1/1_THCS%20Truc%20Tuan/truc-tuan-game-test.html) |
| THCS Đào Sư Tích | [Đề số 1](../grade-8/De_thi_GHK1/2_THCS%20Dao%20Su%20Tich/2.%20THCS%20Dao%20Su%20Tich.html); [Đề số 2](../grade-8/De_thi_GHK1/13_THCS_Dao_Su_Tich/13%20THCS%20Dao%20Su%20Tich.html) | Chưa có |
| THCS Trung Đông | [Đề số 1](../grade-8/De_thi_GHK1/3_THCS%20Trung%20Dong/3%20THCS%20Trung%20Dong.html) | Chưa có |
| THCS Trực Đại | [Đề số 1](../grade-8/De_thi_GHK1/4_THCS%20Truc%20Dai/4%20THCS%20Truc%20Dai.html) | Chưa có |
| THCS Trực Thuận | [Đề số 1](../grade-8/De_thi_GHK1/5_THCS%20Truc%20Thuan/5%20THCS%20Truc%20Thuan.html) | Chưa có |
| THCS Cát Thành | [Đề số 1](../grade-8/De_thi_GHK1/6_THCS%20Cat%20Thanh/6%20THCS%20Cat%20Thanh.html) | Chưa có |
| THCS Trực Mỹ | [Đề số 1](../grade-8/De_thi_GHK1/7_THCS%20Truc%20My/7%20THCS%20Truc%20My.html) | Chưa có |
| THCS Phương Định | [Đề số 1](../grade-8/De_thi_GHK1/8_THCS%20Phuong%20Dinh/8%20THCS%20Phuong%20Dinh.html); [Đề số 2](../grade-8/De_thi_GHK1/9_THCS_Phuong_Dinh/9%20THCS%20Phuong%20Dinh.html) | Chưa có |
| THCS Trực Đạo | [Đề số 1](../grade-8/De_thi_GHK1/10_THCS_Truc_Dao/10%20THCS%20Truc%20Dao.html) | Chưa có |
| THCS Trực Khang | [Đề số 1](../grade-8/De_thi_GHK1/11_THCS_Truc_Khang/11%20THCS%20Truc%20Khang.html) | [Game đề số 1](../grade-8/De_thi_GHK1/11_THCS_Truc_Khang/practice-game-pilot.html) |
| THCS Trực Hùng | [Đề số 1](../grade-8/De_thi_GHK1/12_THCS_Truc_Hung/12%20THCS%20Truc%20Hung.html) | [Game đề số 1](../grade-8/De_thi_GHK1/12_THCS_Truc_Hung/practice-game-pilot.html) |
| THCS Việt Hùng | [Đề số 1](../grade-8/De_thi_GHK1/14_THCS_Viet_Hung/14%20THCS%20Viet%20Hung.html) | Chưa có |
| THCS Trực Thái | [Đề số 1](../grade-8/De_thi_GHK1/16_THCS_Truc_Thai/16%20THCS%20Truc%20Thai.html) | Chưa có |
| THCS Trực Nội | [Đề số 1](../grade-8/De_thi_GHK1/17_THCS_Truc_Noi/17%20THCS%20Truc%20Noi.html) | Chưa có |
| THCS Trực Cường | [Đề số 1](../grade-8/De_thi_GHK1/18_THCS_Truc_Cuong/18%20THCS%20Truc%20Cuong.html) | Chưa có |
| THCS Trực Chính | [Đề số 1](../grade-8/De_thi_GHK1/19_THCS_Truc_Chinh/19%20THCS%20Truc%20Chinh.html) | [Game đề số 1](../grade-8/De_thi_GHK1/19_THCS_Truc_Chinh/practice-game-pilot.html) |
| THCS Cổ Lễ | [Đề số 1](../grade-8/De_thi_GHK1/20_THCS_Co_Le/20%20THCS%20Co%20Le.html) | Chưa có |

## Thay đổi và tương thích

- `assets/school-folders.js`: mở rộng bộ nhóm đang có bằng metadata trình bày, ghép theo thư mục chứa đề, sắp đề/game cùng số gần nhau. Nhãn mới là `Đề số N – THCS …` và `Game đề số N – THCS …`. Giữ nguyên `title`/`href` nguồn. Nhận diện thêm nhãn mới do Admin nhập, kể cả khi nhiều đề cùng thư mục. Nếu quan hệ mơ hồ thì giữ tên nguồn thay vì đoán số hoặc tạo đề/game giả.
- `assets/catalog-view.js`: chuẩn bị số từ catalog đầy đủ trước khi lọc ẩn/tìm kiếm, chỉ áp dụng cho thư mục `exam-folder` có tài liệu `grade-8/`. Grade 4–7 giữ cách hiển thị cũ. Grade 8 có thể thêm bộ HK1/HK2/GHK2 qua catalog hiện tại mà không viết lại index.
- `assets/school-folders.css`: cặp đề/game nằm cùng hàng trên máy tính, xếp dọc trên điện thoại. Trường chỉ có đề không sinh ô game chờ.
- `index.html`, `assets/library.js`: cập nhật phiên bản tải CSS/module giao diện để nhận bản mới; luồng xác minh quyền và đăng nhập không đổi.
- `tests/school-folders.test.mjs`, `tests/grade8-numbering-browser.py`, `tests/auth-browser.py`: bổ sung kiểm tra cặp đề/game và đổi kỳ vọng nhãn hiển thị. Workflow Firebase hiện có chạy kiểm thử và lưu ảnh/JSON, không deploy.
- `tools/verify-firebase-recovery.py`: cho phép đổi phiên bản URL module index; vẫn xác minh các file nguồn cũ, cấu hình Firebase, Rules, Admin và catalog v1 bằng hash tin cậy.

**Không sửa** `assets/catalog-editor.js`, `assets/catalog-release.js`, `assets/catalog-store.js`, JSON catalog, cấu hình Firebase/Hosting, Authentication, Rules hoặc các file đề/game/audio. Export vẫn đúng 212 liên kết; schema, hash và cơ chế `releaseApplied` giữ nguyên. Admin tiếp tục thêm/sửa/ẩn/xóa, xuất bản danh mục và phục hồi lịch sử như trước. Không ghi vào Firebase production.

## Bổ sung tài liệu sau này

1. Tải HTML/tài nguyên thật lên repository, giữ các URL đang dùng. Không thêm liên kết tới file chưa tồn tại.
2. Qua Admin, thêm vào thư mục `exam-folder` của Grade 8 với tên rõ ràng: `Đề số 2 – THCS Trực Tuấn`, `Game đề số 2 – THCS Trực Tuấn`. Điền đúng href HTML riêng. Có thể dùng cùng thư mục trường hoặc thư mục con riêng của đề.
3. Game dùng cùng số với đề. Với nhiều đề cùng thư mục, phải nhập rõ số để tránh ghép nhầm. Không có game thì chỉ nhập đề. Số ghi rõ trong tên được ưu tiên; với tên cũ không có “Đề số N”, số theo thứ tự catalog. Khi muốn giữ số cố định qua việc xóa/đổi thứ tự, đặt tên nguồn rõ số qua Admin.
4. Các trường mới dùng cùng quy ước, không cần danh sách tên trường viết cứng. Các bộ đề mới là thư mục `exam-folder` riêng; số đề bắt đầu lại trong mỗi trường/bộ đề.
5. Trạng thái ẩn được giữ. Tìm kiếm nhận cả tên cũ lẫn tên hiển thị mới. Ẩn đề 1 không khiến đề 2 đổi thành đề 1; game còn hiển thị vẫn giữ số ghép từ nguồn đầy đủ. Không có dữ liệu tài liệu nào được dựng ra DOM trước đăng nhập hoặc sau đăng xuất.

## Kết quả kiểm thử

- `npm run check:catalog`: đủ 212 URL tồn tại, không trùng; không sửa đề/audio/game.
- `npm run test:prepare`: **32 kiểm thử đạt**, gồm cấu trúc thật, đề/game nhiều số, thư mục lồng nhau, lọc ẩn, game mơ hồ và số trùng.
- `python3 tests/grade8-numbering-browser.py`: **7 nhóm kiểm tra đạt**; DOM Grade 4–7 khớp nguyên bản trước thay đổi; 23 HTML lớp 8 trả đúng file dưới `/library/`; mở/đóng bằng chuột/bàn phím; tìm tên mới/cũ; kiểm tra 360/390/768/1280px không tràn ngang. Kiểm tra riêng dữ liệu tương lai chỉ chạy trong fixture cục bộ, không lưu hay phát hành đề/game giả. Không lỗi JavaScript/console. Xem [báo cáo JSON](grade8-numbering-browser-report.json); ảnh được lưu trong artifact CI.
- Firebase Auth/Firestore Emulator: **18 kiểm thử Rules và 23 kịch bản trình duyệt đạt**. Đăng nhập/đăng xuất, phân quyền Admin/giáo viên, cấp/khóa/thu hồi quyền, sửa/xuất bản catalog, lưu đồng thời, lịch sử, tiếp nhận release và xóa sau phát hành đều hoạt động. Mở game Trực Tuấn và ba mẫu từ index đều thành công. Không lộ tài liệu trước đăng nhập/sau đăng xuất.
- `python3 tools/verify-firebase-recovery.py`: các file hiện có trước khi khôi phục Firebase, gồm bản nghe mới Trực Hùng, vẫn nguyên byte; cấu hình, Rules và catalog gốc giữ nguyên. Đối chiếu thêm diff với main `a8a38ed` xác nhận toàn bộ thư mục tài liệu, catalog JSON, cấu hình và mã quản trị không đổi.

Chạy bằng Node 24, Python 3.12, Java 21, Playwright 1.58 và Chromium. `npm run test:emulators` chạy bộ Firebase; nếu tải emulator bị chặn, `tools/test-emulators-official.py` là phương án Google Cloud SDK đã có kiểm tra checksum.

**Giới hạn xác minh:** kiểm thử Firebase thực hiện trên Emulator, không đăng nhập hay đọc/ghi Firebase production trong lần này. Chưa xác nhận trạng thái website/danh mục thật sau triển khai. Cần duyệt PR, merge và triển khai trước khi bản web nhận giao diện mới; không tự động merge hoặc deploy.
