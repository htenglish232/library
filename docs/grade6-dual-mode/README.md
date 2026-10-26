# Game hai chế độ lớp 6

Nhánh `feature/grade6-all-dual-mode`, từ main `7407b43` (đã có WAV). Chưa merge hoặc deploy. File yêu cầu được gửi kết thúc giữa mục 10; không tự suy diễn phần chưa nhận.

Đã tạo **16 game / 14 trường / 661 câu**, gồm **654 câu tự chấm** và **7 câu cần giáo viên kiểm tra**. Không mặc định mỗi đề có 42 câu: Trực Tuấn và Trung Đông có 43, Phương Định 35, Đào Sư Tích 36. Tất cả đều giữ thứ tự và số câu thực tế của nguồn.

## Danh sách đầy đủ

Kiểm kê trước khi tạo game: [source-inventory.md](source-inventory.md), cùng SHA256/phân loại HTML/audio/bài học/game ngữ pháp trong [source-inventory.json](source-inventory.json). Không có file đáp án độc lập: dùng literal và thuộc tính đáp án có sẵn, có lưu `answerEvidence` trong dữ liệu game.

| Nguồn | Trường | Đề số | Câu | Tự chấm | XP tối đa | Track đã liên kết | Game |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | THCS Trực Cường | 1 | 42 | 42 | 420 | 0 | [Mở game](../../grade-6/De_thi_GHK_1/1_THCS_Truc_Cuong/practice-dual-mode.html) |
| 2 | THCS Cổ Lễ | 1 | 42 | 42 | 420 | 2 | [Mở game](../../grade-6/De_thi_GHK_1/2_THCS_Co_Le/practice-dual-mode.html) |
| 3 | THCS Trực Tuấn | 1 | 43 | 43 | 430 | 2 | [Mở game](../../grade-6/De_thi_GHK_1/3_THCS_Truc_Tuan/practice-dual-mode.html) |
| 4 | THCS Trực Hùng | 1 | 42 | 42 | 420 | 2 | [Mở game](../../grade-6/De_thi_GHK_1/4_THCS_Truc_Hung_%281%29/practice-dual-mode.html) |
| 5 | THCS Trung Đông | 1 | 43 | 41 | 410 | 1 | [Mở game](../../grade-6/De_thi_GHK_1/5_THCS_Trung_Dong/practice-dual-mode.html) |
| 6 | THCS Liêm Hải | 1 | 42 | 42 | 420 | 0 | [Mở game](../../grade-6/De_thi_GHK_1/6_THCS_Liem_Hai/practice-dual-mode.html) |
| 7 | THCS Liêm Hải | 2 | 42 | 42 | 420 | 0 | [Mở game](../../grade-6/De_thi_GHK_1/7_THCS_Liem_Hai/practice-dual-mode.html) |
| 8 | THCS Trực Thắng | 1 | 42 | 42 | 420 | 2 | [Mở game](../../grade-6/De_thi_GHK_1/8_THCS_Truc_Thang/practice-dual-mode.html) |
| 9 | THCS Trực Thuận | 1 | 42 | 42 | 420 | 2 | [Mở game](../../grade-6/De_thi_GHK_1/9_THCS_Truc_Thuan/practice-dual-mode.html) |
| 10 | THCS Phương Định | 1 | 35 | 35 | 350 | 2 | [Mở game](../../grade-6/De_thi_GHK_1/10_THCS_Phuong_Dinh/practice-dual-mode.html) |
| 11 | THCS Trực Đạo | 1 | 42 | 41 | 410 | 1 | [Mở game](../../grade-6/De_thi_GHK_1/11_THCS_Truc_Dao/practice-dual-mode.html) |
| 12 | THCS Trực Hùng | 2 | 42 | 42 | 420 | 2 | [Mở game](../../grade-6/De_thi_GHK_1/12_THCS_Truc_Hung/practice-dual-mode.html) |
| 13 | THCS Đào Sư Tích | 1 | 36 | 36 | 360 | 1 | [Mở game](../../grade-6/De_thi_GHK_1/13_THCS_Dao_Su_Tich/practice-dual-mode.html) |
| 14 | THCS Việt Hùng | 1 | 42 | 42 | 420 | 0 | [Mở game](../../grade-6/De_thi_GHK_1/14_THCS_Viet_Hung/practice-dual-mode.html) |
| 15 | THCS Trực Thái | 1 | 42 | 40 | 400 | 2 | [Mở game](../../grade-6/De_thi_GHK_1/15_THCS_Truc_Thai/practice-dual-mode.html) |
| 16 | THCS Trực Nội | 1 | 42 | 40 | 400 | 2 | [Mở game](../../grade-6/De_thi_GHK_1/16_THCS_Truc_Noi/practice-dual-mode.html) |

## Tái sử dụng và bảo toàn

- Mỗi trường chỉ có launcher HTML và dữ liệu JS. Tất cả dùng trực tiếp `../../../grade-8/De_thi_GHK1/shared-practice/` (engine, CSS, model, dual-progress, dual-store, dual-sound). Không tạo engine lớp 6, không sao chép WAV.
- Giữ nguyên byte toàn bộ đề/audio/game cũ, index, Admin, Firebase, auth/session, model, CSS và WAV. Engine chung chỉ sửa đúng nhãn khối: đọc `exam.grade === 6`, mặc định giữ Grade 8 như trước; không thay logic. Kiểm thử bảo toàn so sánh engine sau khi loại đúng thay đổi nhãn với main `7407b43`. Launcher mới có phiên bản URL riêng để tránh dùng engine cũ từ cache.
- Hai chế độ dùng cùng snapshot/XP hiện có: đúng lần đầu +10, sai/chờ giáo viên/làm lại/xem đáp án/chuyển chế độ không cộng thêm. Khóa exam mới `grade6-ghk1-source-N` tách dữ liệu lớp 8; giữ nguyên khóa hồ sơ cũ để tên/mã học sinh dùng chung giữa hai khối.
- Giữ markup gạch chân có thật, đoạn đọc, thứ tự phương án và thẻ từ nguồn. Không suy đoán chữ gạch chân từ lời giải. Dạng viết lại có tiền tố cố định được chuyển sang ô viết cả câu khi đáp án đầy đủ và tiền tố được ghi rõ trong nguồn; thẻ nguồn vẫn giữ dưới dạng gợi ý và `sourceTokens`, không tự thêm thẻ từ.
- WAV và nút/tùy chọn âm thanh dùng chung trực tiếp với lớp 8. Âm lượng 70% và API điều chỉnh hiện có được giữ nguyên, không thêm hệ thống riêng.
- `7_THCS_Liem_Hai` và `8_THCS_Truc_Thang` có nội dung tương tự, đã được ghi nhận từ kiểm kê trước. Giữ hai mục nguồn riêng theo catalog và xác nhận trước của người dùng; mỗi mục chỉ thêm một game. Không xóa/gộp nguồn. Tên Trực Hùng ở nguồn 12 cũng giữ theo catalog.
- Trực Cường nằm trong lớp 6 nhưng HTML có ghi Tiếng Anh 7/nội dung sở thích–sức khỏe–tình nguyện. Giữ nguyên nội dung, ghi nhận để giáo viên xác nhận.

## Câu cần giáo viên kiểm tra

Không chấm sai, không tự cho đúng và không cộng XP cho các câu dưới đây. Dữ liệu/đáp án nguồn vẫn được giữ để đối chiếu.

| Trường / nguồn | Câu | Lý do |
|---|---|---|
| THCS Trung Đông / 5 | `LAN1_1` | Nguồn không đánh dấu rõ phần gạch chân trong câu/phương án; không tự suy đoán, cần giáo viên kiểm tra. |
| THCS Trung Đông / 5 | `LAN1_2` | Nguồn không đánh dấu rõ phần gạch chân trong câu/phương án; không tự suy đoán, cần giáo viên kiểm tra. |
| THCS Trực Đạo / 11 | `rewrite4` | Thuộc tính data-valid của nguồn bị lỗi dấu nháy; không tự phục hồi/suy đoán đáp án, cần giáo viên kiểm tra. |
| THCS Trực Thái / 15 | `LF1` | Nguồn không đánh dấu rõ phần gạch chân trong câu/phương án; không tự suy đoán, cần giáo viên kiểm tra. |
| THCS Trực Thái / 15 | `LF2` | Nguồn không đánh dấu rõ phần gạch chân trong câu/phương án; không tự suy đoán, cần giáo viên kiểm tra. |
| THCS Trực Nội / 16 | `B1_1` | Nguồn không đánh dấu rõ phần gạch chân trong câu/phương án; không tự suy đoán, cần giáo viên kiểm tra. |
| THCS Trực Nội / 16 | `B1_2` | Nguồn không đánh dấu rõ phần gạch chân trong câu/phương án; không tự suy đoán, cần giáo viên kiểm tra. |

## Listening và nguồn chưa xác nhận

26 file nghe nằm trong các thư mục nguồn; game chỉ dùng **21 liên kết đã được HTML nguồn xác nhận** (20 MP3, 1 WAV), giữ nguyên byte/đường dẫn. Các file dùng chung cho hai phần vẫn là một track có nhãn toàn bộ bài nghe. Ranh giới Listening 4+5 của Phương Định và 5+4 của Đào Sư Tích được lấy từ cấu trúc nguồn, không chia cứng thành 6+6.

Các phần chưa có nguồn file được xác nhận:
- THCS Trực Cường, đề 1 (nguồn 1): phần 1, 2.
- THCS Liêm Hải, đề 1 (nguồn 6): phần 1, 2.
- THCS Liêm Hải, đề 2 (nguồn 7): phần 1, 2.
- THCS Đào Sư Tích, đề 1 (nguồn 13): phần 1.
- THCS Việt Hùng, đề 1 (nguồn 14): phần 1, 2.

Không tự gán 5 file còn nghi vấn chỉ theo tên; không tạo track rỗng cho Việt Hùng. Game hiển thị cảnh báo và có nút mở đề gốc để sử dụng cách nghe cũ. Transcript gốc được giữ để đối chiếu sau khi kiểm tra đáp án; riêng Trực Cường trích nguyên văn từ `listeningTracks.sentences`. Các trường hợp trên chưa có phát/tua file nghe trong game cho đến khi giáo viên xác nhận/bổ sung file đúng. Chi tiết nguồn: [AUDIO_REPORT.md](../../grade-6/De_thi_GHK_1/AUDIO_REPORT.md). Chưa nghe thủ công toàn bộ bản ghi âm để thẩm định nội dung.

## Catalog, Firebase và index

- Thêm `assets/grade6-dual-links.js` và một batch trong `assets/catalog-release.js`; snapshot `catalog/current-library-catalog.json` tăng 231 → 247 liên kết. Bỏ đúng 16 liên kết mới thì danh mục khớp hoàn toàn main cũ, kể cả thứ tự/tên các trường và mọi lớp khác.
- Không sửa `index.html` hoặc logic đăng nhập. `assets/library.js` vẫn chỉ gọi release overlay sau khi xác thực quyền và đọc snapshot Firebase hợp lệ từ server; trước đăng nhập catalog không có DOM tài liệu.
- Overlay chỉ đọc, chống trùng URL tương đối/mã hóa/Pages và giữ trạng thái ẩn/tên Admin đã sửa. Admin có thể bấm **Bổ sung bài mới từ GitHub vào bản nháp**, kiểm tra rồi **Lưu danh mục** để ghi nhận batch; sau đó xóa/ẩn/sửa tài liệu theo quy trình hiện có. Không tự ghi production, không thay Rules hoặc tài khoản.
- Sau phát hành code, overlay có thể hiển thị các game mới khi học sinh đăng nhập và server cho quyền truy cập; thao tác Admin trên là cần khi muốn lưu batch vào Firebase/quản lý lâu dài, không cần tạo Firebase mới.

## Kiểm thử đã chạy

- `python tools/build-grade6-dual-games.py --verify`: đủ 16 launcher/data khớp nguồn, không còn control nguồn chưa ánh xạ.
- `node --test tests/grade6-dual.test.mjs tests/grade8-all-dual.test.mjs tests/dual-mode-progress.test.mjs tests/dual-mode-sound.test.mjs`: 35 đạt.
- Catalog/release/preflight/school-folders: 41 đạt. `node tools/check-catalog.mjs`: 247 đường dẫn duy nhất, có thật.
- `tests/grade6-all-dual-browser.py`: đủ 16 game / 661 câu trên viewport mobile, cả hai chế độ, đúng nội dung/đoạn đọc, chấm/XP, tiến độ, hồ sơ/mã học sinh, reset và 21 track nghe phát/tạm dừng/tua/tốc độ. Sau các cải tiến về tiền tố Đào Sư Tích, transcript Trực Cường và nhãn khối trong controller, chạy lại đầy đủ 16 game / 661 câu.
- `tests/grade8-all-dual-browser.py`: hồi quy 19 game / 793 câu đạt.
- `tests/dual-mode-wav-browser.py`: 35/35 game trên desktop và 35/35 touch emulation, WAV đúng/sai/hoàn thành, mute/restore, 70% gain, Listening không gián đoạn; 10 nhóm đạt gồm WAV 404/hỏng/chậm/decode lỗi và hủy lượt phát đang chờ.
- `tests/dual-mode-sound-loading-browser.py`: 9 nhóm tải module/cache/retry/timeout đạt. `tests/dual-mode-sound-browser.py`: 9 nhóm Web Audio dự phòng đạt. Hai bộ sine cũ được cập nhật fixture cố ý gây WAV decode lỗi để kiểm tra fallback, và có bộ kiểm thử native WAV riêng; không bỏ qua kiểm thử âm thanh mới.
- `tests/grade6-catalog-browser.py`: 4 nhóm đạt, 16 cặp đề/game đúng trường, tìm kiếm, ẩn Admin, 360/390/768/1280px, giữ DOM các lớp khác và trạng thái catalog rỗng ban đầu. Đây là fixture hiển thị, không giả lập thành kết quả kiểm thử Firebase Authentication thật.
- `tests/grade6-cross-grade-browser.py`: desktop và touch đạt, thêm ca sắp xếp câu theo biến thể nguồn được chấp nhận; dùng chung tên/mã/mute, tiến độ và XP lớp 6/8/học sinh khác độc lập.
- Kiểm thử trình bày cũ Grade 6/7 và Grade 8 đều đạt; fixture cũ Grade 6/7 chủ động giữ tập đề gốc, còn các game mới được kiểm ở bộ riêng.
- Gói xem thử lớp 8 trước đó chưa mang theo WAV sau bản nâng cấp âm thanh. Công cụ `build-dual-mode-preview.py` chỉ bổ sung ba WAV vào manifest/gói; chạy lại hồi quy Trực Tuấn 42 câu và preview HTTP đạt, hết 404. Direct `file://` bị chính sách Chromium chặn nên bỏ qua kiểm tra đó, không báo đạt.
- Builder/nguồn lớp 8, YAML workflow, `git diff --check` và chuẩn bị artifact `.site` đạt. Không upload artifact lên hosting.

Kết quả chi tiết: [verification.json](verification.json). Danh sách file: [changed-files.txt](changed-files.txt). Chromium thực tế với desktop và mô phỏng touch; chưa thử điện thoại vật lý/Safari/Edge riêng. Không chạy Firebase production hoặc tuyên bố kiểm thử Auth production. Truy cập Pages công khai bị proxy CONNECT 403, kể cả quyền thực thi mở rộng; đây không phải bằng chứng Pages trả 403/404 hoặc bản đã phát hành.

## Đưa lên website

1. Duyệt Pull Request, xử lý các lưu ý giáo viên nếu muốn; chỉ merge khi đã duyệt.
2. Chạy workflow **Publish reviewed library to GitHub Pages (manual only)** trên `main`, nhập xác nhận theo workflow. Tác vụ này không tự merge/deploy.
3. Sau triển khai, đăng nhập thư viện → Grade 6 → Đề thi GHK1 → trường → Game đề số N (2 chế độ). Nếu trình duyệt còn cache cũ, hard reload/xóa cache rồi kiểm tra lại.
4. Admin có thể sao lưu danh mục, đưa batch GitHub vào bản nháp rồi Lưu như mô tả trên. Không cần khởi tạo lại Firebase.
5. Xác nhận/bổ sung nguồn nghe còn thiếu và duyệt 7 câu đang chờ giáo viên trước khi bật tự chấm cho chúng.
