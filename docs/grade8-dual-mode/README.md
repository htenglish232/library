# Giai đoạn 1 — Game Trực Tuấn hai chế độ

Nhánh `feature/grade8-dual-mode-games`, từ main `544777a`. **Đã viết mã và kiểm thử cục bộ. Chưa merge, chưa triển khai website, chưa thêm liên kết vào catalog. Dừng để người dùng duyệt trước khi mở rộng.**

## Đã hoàn thành

- Trang mới `grade-8/De_thi_GHK1/1_THCS Truc Tuan/truc-tuan-dual-mode.html`, đủ **42 câu**, dùng hai MP3 gốc. Game cũ `truc-tuan-game-test.html` và toàn bộ `truc-tuan-game/` giữ nguyên.
- Hai chế độ: **Theo thử thách** (12 nghe, 13 ngôn ngữ/ngữ pháp, 10 đọc, 7 viết) và **Toàn đề theo thứ tự** (câu 1–42). Cùng dữ liệu và kết quả lần đầu; đổi chế độ giữ câu hiện tại, bản nháp và XP.
- Chọn chặng, câu trước/tiếp, chọn nhanh bất kỳ câu nào, tiến độ, tổng kết 42 câu và danh sách cần ôn. Bài đọc có nút thu gọn/mở lại để thuận tiện khi nhập trên điện thoại.
- Mỗi câu đúng lần đầu nhận 10 XP, tối đa 420 theo đáp án HTML. Kiểm tra lại, đổi chế độ, tải lại hoặc ôn lại không cộng thêm. Đáp án lần đầu được lưu riêng và khóa; ôn lại dùng bản nháp/kết quả riêng.
- Lưu bản nháp, thẻ từ, chế độ, câu đang làm, kết quả lần đầu và lượt ôn trên thiết bị bằng localStorage. Nhập họ tên rồi bấm bắt đầu; nếu có bài lưu, phải bấm **Tiếp tục bài đang làm** hoặc **Bắt đầu lại**. Bắt đầu lại luôn yêu cầu xác nhận và chỉ tác động đúng học sinh/đề đó.
- Hồ sơ riêng theo họ tên chuẩn hóa và mã riêng tùy chọn. Hai bạn trùng họ tên cần nhập mã riêng khác nhau. Không liệt kê bài lưu của người khác, không gửi tên/mã/kết quả lên dịch vụ bên ngoài. Đây là tách tiến độ trên thiết bị, không phải hệ thống xác thực học sinh hoặc mã hóa localStorage.
- Audio phát/tạm dừng, tua ±5 giây, thanh tua, tốc độ 0.75×/1×/1.25×; transcript chỉ đưa ra giao diện sau khi kiểm tra câu đang làm. Giữ nguyên khoảng trắng trong tên `GHK1 K8 - part 2 .mp3`.

## Xem thử mà không sửa code hoặc chạy lệnh

1. Mở [các lượt kiểm tra của nhánh](https://github.com/htenglish232/library/actions?query=branch%3Afeature%2Fgrade8-dual-mode-games), chọn lượt **Grade 8 dual-mode Stage 1 (no deploy)** đã chạy thành công.
2. Trong **Artifacts**, tải **truc-tuan-dual-mode-preview**. Giải nén toàn bộ, rồi mở **MO_GAME.html** bằng Chrome/Edge. Không chuyển riêng một HTML ra ngoài thư mục. Gói nhỏ có sẵn dữ liệu, CSS/JS, font và hai MP3; không chứa tài khoản hay tiến độ học sinh. Giao diện có thể xem trước qua [ảnh chào mừng](welcome.png) và [ảnh điện thoại](reading-mobile.png).
3. Nhập tên, chọn một chế độ và bắt đầu. Tải lại, nhập đúng họ tên/mã để tiếp tục. Dữ liệu bản tải về không tự chuyển sang website vì là môi trường trình duyệt khác.

Artifact chỉ xuất hiện sau khi workflow hoàn tất; đây không phải đường dẫn website đã triển khai. Gói xem thử đã chạy thành công qua HTTP với chính các file trong gói. **Mở trực tiếp `file://` bị Chromium trong môi trường kiểm thử chặn bằng `ERR_BLOCKED_BY_ADMINISTRATOR`, nên chưa được xác nhận ở môi trường này.** Không đổi chính sách trình duyệt để vượt chặn. Nếu máy người xem cũng chặn HTML cục bộ, chưa có bản web preview thay thế vì chưa được duyệt triển khai.

Ảnh và gói preview được workflow tạo để duyệt, không phát hành Pages và không sửa dữ liệu Firebase. Có thể [tải ZIP mã nguồn của nhánh](https://github.com/htenglish232/library/archive/refs/heads/feature/grade8-dual-mode-games.zip) nếu cần xem đầy đủ mã/tài nguyên.

## Những đề đã có game và phần chưa mở rộng

Đã quét lại: **19 đề, 17 trường**, hiện có 4 game cũ ở Trực Tuấn, Trực Khang, Trực Hùng, Trực Chính. Bản hai chế độ chỉ được tạo thêm cho **Trực Tuấn — Đề số 1**. Ba pilot và 15 đề chưa có game vẫn giữ nguyên, chưa tạo hàng loạt hay chuyển dữ liệu. Các trường có hai đề (Đào Sư Tích, Phương Định) được liệt kê riêng theo số trong trường, không theo số thư mục.

Danh sách trường/đề/game/URL và hash baseline: [inventory.json](inventory.json). Phân tích tái sử dụng và dữ liệu: [ANALYSIS.md](ANALYSIS.md).

## Kiến trúc và file thêm mới

- `shared-practice/dual-progress.js`: mô hình trạng thái dùng chung, thứ tự câu, chuyển chế độ, bản nháp/đáp án lần đầu/ôn lại, tính XP từ kết quả lần đầu và xác thực bản lưu. Không có bộ đếm XP có thể cộng trùng.
- `shared-practice/dual-store.js`: khóa lưu theo đề/họ tên/mã, kiểm tra phiên bản nội dung, bản lưu hỏng, lỗi quyền/quota và tab khác. Không quét hoặc xóa các hồ sơ khác. Phiên bản đề thay đổi không tự ghi đè bài cũ; cần xác nhận bắt đầu lại.
- `shared-practice/dual-mode-engine.js`, `dual-mode.css`: controller/giao diện dùng chung cho giai đoạn mới; tái sử dụng `model.js`, `game.css`, icon và font hiện có. CSS mới chỉ trang mới tải. Controller cũ chưa bị thay hoặc xóa trước khi duyệt.
- `truc-tuan-dual-mode.html`, `truc-tuan-dual-data.js`, `truc-tuan-dual-support.js`: launcher và dữ liệu riêng của Trực Tuấn. Giữ toàn bộ bản ghi đáp án nguồn; bản dịch/mẹo kế thừa từ game cũ nằm riêng, có nhãn AI/chưa được giáo viên xác nhận và không tham gia chấm điểm.
- `tools/build-truc-tuan-dual-data.mjs`, `verify-truc-tuan-dual-source.py`: dựng/đối chiếu dữ liệu với HTML hiện tại. DOMParser không chạy ứng dụng đề gốc; hai literal đáp án/thẻ được đọc riêng trong VM có timeout. Chế độ verify không ghi file.
- `tools/verify-dual-mode-preservation.py`: so từng byte toàn bộ 394 file main ban đầu, bao gồm index/catalog, Firebase/Rules/Admin, game cũ, ba pilot và các khối khác.
- `tools/build-dual-mode-preview.py`: đóng gói thư mục xem thử mới, nhúng font vào **bản CSS trong gói** để giảm rào cản font cục bộ; không sửa CSS/font nguồn, không lấy localStorage hoặc dữ liệu học sinh.
- `tests/dual-mode-progress.test.mjs`, `tests/dual-mode-browser.py`, workflow `grade8-dual-mode-checks.yml` và báo cáo trong thư mục này. Workflow chỉ kiểm thử/tạo artifact, không deploy.

Các commit được chia thành kiểm kê/dữ liệu → bộ máy/trạng thái → kiểm thử/đóng gói/báo cáo. Không sửa bất kỳ file nào đã có trên main ban đầu.

## Câu cần giáo viên duyệt

| Câu | Vấn đề giữ nguyên từ nguồn |
| --- | --- |
| q12 | HTML chấm F, ghi chú nói Word T; “light” so với transcript “strong”. Giữ F theo HTML. |
| q13 | Chuẩn phát âm nguyên âm trong “activity” có biến thể; giữ B. |
| q19 | “lunch tonight” và lời đáp C có thể hợp lý tùy ngữ cảnh; giữ B. |
| q29 | “keep fit” và “stay fit” đều có nghĩa phù hợp; giữ D của HTML, không tự nhận A. |
| q40 | HTML nêu yours/your bike; ghi chú nhắc Word dùng his. Chưa có Word; không tự nhận his. |
| q31–q33, q39–q42 | Chỉ tự chấm câu mẫu/biến thể được nguồn nêu rõ. Không dùng từ khóa con; cách diễn đạt khác cần giáo viên đối chiếu. |

Giữ nguyên 42 đáp án, giải thích và ghi chú HTML. Không tự sửa học thuật, không thêm câu. XP là điểm luyện tập theo nguồn, không phải điểm thi chính thức hay cơ chế chống gian lận. Chưa có đối chiếu Word và chưa được giáo viên nghe xác minh học thuật từng MP3.

## Kiểm thử đã chạy

| Kiểm tra | Kết quả cục bộ |
| --- | --- |
| Đối chiếu HTML/reference/game mới | 42/42 ID, thứ tự, prompt, phương án, bản ghi đáp án/ghi chú/thẻ, 2 bài đọc, 2 transcript và hash MP3 khớp |
| Bảo toàn repository | 394/394 file baseline nguyên byte, không đổi index/catalog/Firebase hoặc game cũ |
| Model/lưu tiến độ | 12 nhóm kiểm thử đạt: mọi đáp án nguồn, XP một lần, chế độ, ôn lại, hồ sơ/đề riêng, dữ liệu hỏng, tab cũ, lỗi quyền/quota và xác nhận reset |
| Chromium thực tế | Thao tác đủ 42/42 câu; 12 nhóm kiểm thử đạt; xem [browser-report.json](browser-report.json) |
| Ca đúng/sai/tổng kết | Cố ý làm sai q1/q31/q36: 39 đúng + 3 sai + 0 chưa làm = 390 XP; ôn đúng cả 3, đổi chế độ/tải lại vẫn 390 XP và giữ đáp án lần đầu |
| Bản nháp | Câu nhập và thẻ ghép giữ qua đổi chế độ/tải lại; lượt ôn giữ vị trí và bản nháp riêng |
| Nghe | Hai MP3 phát/tạm dừng, tua ±5s, thanh tua, ba tốc độ; transcript ẩn trước/hiện sau kiểm tra |
| Thiết bị | 360/390/768/820/1280px, không tràn ngang; thao tác cảm ứng thật; thu gọn/mở bài đọc; đường dẫn `/library/` |
| Lỗi/mạng | 0 JavaScript/console errors trong các kiểm tra HTTP; 0 yêu cầu ngoài/backend/Firebase của game |
| Gói xem thử | Chạy qua HTTP bằng các file đóng gói, tiếp tục tiến độ và phát MP3 đạt; kiểm tra file:// bị chặn và được ghi là skipped, không báo đạt |
| Thư viện hiện có | 212 URL, 36 kiểm thử chuẩn bị đạt; Firebase Emulator có 18 Rules + 23 kịch bản đăng nhập/Admin/catalog đạt |

Tất cả được thực hiện với Node 24, Python 3.12, Playwright 1.58, Chromium và Java 21 cho Firebase Emulator. Các script được Codex/CI chạy tự động; người dùng không cần chạy lệnh.

## Giới hạn và việc chưa làm

- Chưa xác nhận kết quả CI trên GitHub, chưa merge và chưa deploy; báo cáo trên là kiểm thử cục bộ đã thực hiện.
- Không dùng Firebase cho tiến độ game, không đọc/ghi production; việc kiểm thử thư viện/Firebase dùng Emulator.
- localStorage chỉ bền khi trình duyệt cho phép và chưa xóa dữ liệu trang. Nếu bị từ chối hoặc hết quota, game báo không lưu được và giữ phiên trong bộ nhớ; tải lại có thể mất phần chưa lưu. Các hồ sơ trùng cả họ tên lẫn mã được coi là cùng một người; muốn tách phải dùng mã riêng.
- Nếu hai tab cùng hồ sơ thay đổi tiến độ, tab cũ dừng ghi và yêu cầu tải lại, tránh ghi đè bản mới. Không có lưu tập trung, đồng bộ thiết bị hay xuất kết quả cho giáo viên.
- Chưa chuẩn hóa ba pilot, chưa làm game cho 15 đề còn lại, chưa đổi liên kết thư viện. Sau khi người dùng duyệt bản chuẩn, mới tiếp tục các giai đoạn đó, đối chiếu/test riêng từng đề.

**Dừng ở Giai đoạn 1 để duyệt. Không tự mở rộng, merge hoặc triển khai.**
