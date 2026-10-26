# Game hai chế độ lớp 7

Nhánh `feature/grade7-all-dual-mode`, từ main `d1f7ebf` đã có lớp 6/8 và ba WAV. Chưa merge hoặc deploy. File yêu cầu kết thúc giữa mục 8; thực hiện những nội dung đầy đủ đã nhận.

**14 đề / 14 trường / 589 câu** được chuyển đầy đủ, gồm **572 câu tự chấm**, **17 câu cần giáo viên kiểm tra**. Trực Hùng có 43 câu, các đề khác có 42; không ép tất cả về cùng số câu.

## Kiểm kê và đường dẫn

Kiểm kê trước khi tạo game: [source-inventory.md](source-inventory.md), [source-inventory.json](source-inventory.json). Thư mục thực tế là `grade-7/De_thi_GHK_1/`. Không coi 26 bài Semester 1, 12 game ngữ pháp HTBT, font, CSS/JS hoặc test là đề GHK1. Đáp án/lời giải nằm trong `script#examData` của từng HTML, không có file đáp án độc lập. Không chạy ứng dụng gốc để trích xuất.

| STT nguồn | Trường | Đề số | Câu | Tự chấm | XP tối đa | Track | Game |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | THCS Trực Thái | 1 | 42 | 42 | 420 | 2 | [Mở game](../../grade-7/De_thi_GHK_1/1_THCS_Truc_Thai/practice-dual-mode.html) |
| 2 | THCS Trực Nội | 1 | 42 | 39 | 390 | 2 | [Mở game](../../grade-7/De_thi_GHK_1/2_THCS_Truc_Noi/practice-dual-mode.html) |
| 3 | THCS Trực Cường | 1 | 42 | 42 | 420 | 0 | [Mở game](../../grade-7/De_thi_GHK_1/3_THCS_Truc_Cuong/practice-dual-mode.html) |
| 4 | THCS Trực Đại | 1 | 42 | 41 | 410 | 2 | [Mở game](../../grade-7/De_thi_GHK_1/4_THCS_Truc_Dai/practice-dual-mode.html) |
| 5 | THCS Trung Đông | 1 | 42 | 42 | 420 | 0 | [Mở game](../../grade-7/De_thi_GHK_1/5_THCS_Trung_Dong/practice-dual-mode.html) |
| 6 | THCS Liêm Hải | 1 | 42 | 40 | 400 | 2 | [Mở game](../../grade-7/De_thi_GHK_1/6_THCS_Liem_Hai/practice-dual-mode.html) |
| 7 | THCS Trực Thuận | 1 | 42 | 42 | 420 | 2 | [Mở game](../../grade-7/De_thi_GHK_1/7_THCS_Truc_Thuan/practice-dual-mode.html) |
| 8 | THCS Cổ Lễ | 1 | 42 | 42 | 420 | 2 | [Mở game](../../grade-7/De_thi_GHK_1/8_THCS_Co_Le/practice-dual-mode.html) |
| 9 | THCS Cát Thành | 1 | 42 | 39 | 390 | 2 | [Mở game](../../grade-7/De_thi_GHK_1/9_THCS_Cat_Thanh/practice-dual-mode.html) |
| 10 | THCS Phương Định | 1 | 42 | 42 | 420 | 2 | [Mở game](../../grade-7/De_thi_GHK_1/10_THCS_Phuong_Dinh/practice-dual-mode.html) |
| 11 | THCS Trực Khang | 1 | 42 | 42 | 420 | 1 | [Mở game](../../grade-7/De_thi_GHK_1/11_THCS_Truc_Khang/practice-dual-mode.html) |
| 12 | THCS Trực Hùng | 1 | 43 | 39 | 390 | 2 | [Mở game](../../grade-7/De_thi_GHK_1/12_THCS_Truc_Hung/practice-dual-mode.html) |
| 13 | THCS Đào Sư Tích | 1 | 42 | 41 | 410 | 1 | [Mở game](../../grade-7/De_thi_GHK_1/13_Dao_Su_Tich/practice-dual-mode.html) |
| 14 | THCS Việt Hùng | 1 | 42 | 39 | 390 | 1 | [Mở game](../../grade-7/De_thi_GHK_1/14_THCS_Viet_Hung/practice-dual-mode.html) |

## Tái sử dụng và bảo toàn

- Mỗi trường chỉ thêm một launcher và một JS dữ liệu. Tất cả dùng trực tiếp `../../../grade-8/De_thi_GHK1/shared-practice/` cho engine, CSS, model, XP, tiến độ, hồ sơ và WAV. Không sao chép engine hoặc WAV, không tạo hệ thống lớp 7 độc lập.
- Controller chỉ mở rộng đúng một dòng chọn nhãn khối: hỗ trợ metadata grade 6/7, vẫn mặc định Grade 8. Không đổi chấm bài, XP, sound, Listening, localStorage hoặc nội dung game lớp 6/8. Launcher lớp 7 có phiên bản URL engine riêng để tránh cache nhãn cũ.
- Giữ nguyên byte tất cả tài liệu, HTML, audio gốc, dữ liệu/game cũ của lớp 6/8, index, Admin, Firebase, Auth/session, Rules và các lớp khác. Có kiểm thử đối chiếu với main. Một MP3 mới cho Việt Hùng là bản tương thích, không thay WMA gốc.
- Dùng lại parser DOM của lớp 6 với tham số tùy chọn loại các widget riêng của HTML lớp 7; mặc định của lớp 6 không đổi, kiểm tra builder --verify vẫn khớp toàn bộ lớp 6.
- Thứ tự câu lấy từ card HTML gốc, không từ thứ tự mảng JSON: một số đề, như Trực Nội, đặt dữ liệu viết lại trước sắp xếp trong JSON nhưng giao diện nguồn hiển thị ngược lại. Đề gốc HTML là thứ tự cần giữ. Năm câu cloze Trực Hùng có nhãn Blank ở ngoài card; trích nguyên nhãn đó làm prompt, không bịa câu.
- Giữ câu hỏi/phương án/gạch chân, Reading, transcript và đáp án nguồn. Rewrite dùng ô nhập phần còn lại sau tiền tố như HTML gốc. `parts` trong Đào Sư Tích được ánh xạ thành hai ô, dùng đúng tuple đáp án nguồn.
- Không sử dụng lại bộ chấm substring/overlap/nhóm từ khóa quá rộng: chỉ đối chiếu tập đáp án đầy đủ đã có. Tiền tố tùy chọn được hỗ trợ đúng quy tắc rõ ràng của nguồn. Một câu Trực Thái có key `didnt` nhưng câu mẫu nguồn ghi `didn’t`: chỉ bổ sung nguyên câu mẫu có thật sau khi đối chiếu key và các thẻ từ, không tự tạo đáp án. Có lưu `answerEvidence` và toàn bộ `sourceRaw`.
- Đúng lần đầu +10 XP; câu pending/sai/làm lại/đổi chế độ/xem lại/reload không thêm XP. Khóa exam `grade7-ghk1-source-N` tách lớp 6/8; giữ nguyên khóa hồ sơ chung để tự điền tên/mã giữa ba khối.

## Các câu cần giáo viên kiểm tra

Không tự biến từ khóa thành câu trả lời chính thức, không tách chuỗi đáp án mơ hồ hoặc đoán chữ gạch chân. Các câu dưới đây dùng trạng thái chờ giáo viên của engine chung và không nhận XP.

| Trường | Câu | Lý do |
|---|---|---|
| THCS Trực Nội | `C_RC1` | Chưa có đáp án đầy đủ hợp lệ trong nguồn; cần giáo viên kiểm tra. |
| THCS Trực Nội | `C_RC1` | Nguồn chỉ có nhóm từ khóa, chưa có tập đáp án đầy đủ; cần giáo viên kiểm tra. |
| THCS Trực Nội | `C_RC2` | Chưa có đáp án đầy đủ hợp lệ trong nguồn; cần giáo viên kiểm tra. |
| THCS Trực Nội | `C_RC2` | Nguồn chỉ có nhóm từ khóa, chưa có tập đáp án đầy đủ; cần giáo viên kiểm tra. |
| THCS Trực Nội | `C_RC3` | Chưa có đáp án đầy đủ hợp lệ trong nguồn; cần giáo viên kiểm tra. |
| THCS Trực Nội | `C_RC3` | Nguồn chỉ có nhóm từ khóa, chưa có tập đáp án đầy đủ; cần giáo viên kiểm tra. |
| THCS Trực Đại | `b1_1` | Nguồn không đánh dấu phần gạch chân; không tự suy đoán, cần giáo viên kiểm tra. |
| THCS Liêm Hải | `LF1_1` | Nguồn không đánh dấu phần gạch chân; không tự suy đoán, cần giáo viên kiểm tra. |
| THCS Liêm Hải | `LF1_2` | Nguồn không đánh dấu phần gạch chân; không tự suy đoán, cần giáo viên kiểm tra. |
| THCS Cát Thành | `QA1` | Chưa có đáp án đầy đủ hợp lệ trong nguồn; cần giáo viên kiểm tra. |
| THCS Cát Thành | `QA1` | Nguồn chỉ có nhóm từ khóa, chưa có tập đáp án đầy đủ; cần giáo viên kiểm tra. |
| THCS Cát Thành | `QA2` | Chưa có đáp án đầy đủ hợp lệ trong nguồn; cần giáo viên kiểm tra. |
| THCS Cát Thành | `QA2` | Nguồn chỉ có nhóm từ khóa, chưa có tập đáp án đầy đủ; cần giáo viên kiểm tra. |
| THCS Cát Thành | `QA3` | Chưa có đáp án đầy đủ hợp lệ trong nguồn; cần giáo viên kiểm tra. |
| THCS Cát Thành | `QA3` | Nguồn chỉ có nhóm từ khóa, chưa có tập đáp án đầy đủ; cần giáo viên kiểm tra. |
| THCS Trực Hùng | `rc1` | Chưa có đáp án đầy đủ hợp lệ trong nguồn; cần giáo viên kiểm tra. |
| THCS Trực Hùng | `rc1` | Nguồn chỉ có nhóm từ khóa, chưa có tập đáp án đầy đủ; cần giáo viên kiểm tra. |
| THCS Trực Hùng | `rc2` | Chưa có đáp án đầy đủ hợp lệ trong nguồn; cần giáo viên kiểm tra. |
| THCS Trực Hùng | `rc2` | Nguồn chỉ có nhóm từ khóa, chưa có tập đáp án đầy đủ; cần giáo viên kiểm tra. |
| THCS Trực Hùng | `rc3` | Chưa có đáp án đầy đủ hợp lệ trong nguồn; cần giáo viên kiểm tra. |
| THCS Trực Hùng | `rc3` | Nguồn chỉ có nhóm từ khóa, chưa có tập đáp án đầy đủ; cần giáo viên kiểm tra. |
| THCS Trực Hùng | `rc4` | Chưa có đáp án đầy đủ hợp lệ trong nguồn; cần giáo viên kiểm tra. |
| THCS Trực Hùng | `rc4` | Nguồn chỉ có nhóm từ khóa, chưa có tập đáp án đầy đủ; cần giáo viên kiểm tra. |
| THCS Đào Sư Tích | `c2_1` | Đáp án nguồn ghép nhiều cách viết trong một chuỗi; không tự tách/suy đoán biến thể, cần giáo viên kiểm tra. |
| THCS Việt Hùng | `rc1` | Chưa có đáp án đầy đủ hợp lệ trong nguồn; cần giáo viên kiểm tra. |
| THCS Việt Hùng | `rc1` | Nguồn chỉ có nhóm từ khóa, chưa có tập đáp án đầy đủ; cần giáo viên kiểm tra. |
| THCS Việt Hùng | `rc2` | Chưa có đáp án đầy đủ hợp lệ trong nguồn; cần giáo viên kiểm tra. |
| THCS Việt Hùng | `rc2` | Nguồn chỉ có nhóm từ khóa, chưa có tập đáp án đầy đủ; cần giáo viên kiểm tra. |
| THCS Việt Hùng | `rc3` | Chưa có đáp án đầy đủ hợp lệ trong nguồn; cần giáo viên kiểm tra. |
| THCS Việt Hùng | `rc3` | Nguồn chỉ có nhóm từ khóa, chưa có tập đáp án đầy đủ; cần giáo viên kiểm tra. |

## Listening, WMA và file còn thiếu

21 tham chiếu audio gốc được giữ theo đúng đường dẫn từng đề, không đoán theo tên file hoặc mượn audio trường khác. Bản nghe duy nhất dùng cho toàn đề giữ nguyên nhãn toàn bộ, không tự cắt/gán mốc thời gian. Transcript có container tổng hợp được giữ toàn bộ thay vì suy đoán nội dung từng phần.

- **Trực Cường, Trung Đông:** HTML nguồn không liên kết file nghe và thư mục không có MP3/WAV. Game giữ đủ câu Listening, cảnh báo thiếu file và có link đề gốc; cần giáo viên bổ sung nguồn đúng. Không tạo track rỗng, không thay bài nghe bằng TTS hoặc nội dung khác.
- **Việt Hùng:** WMA gốc dùng codec `wmav2`; Chromium trả `canPlayType=""`, `MediaError 4`. Thêm duy nhất `listening-2024-browser.mp3`, chuyển từ chính WMA với `ffmpeg -map 0:a:0 -c:a libmp3lame -q:a 4`, giữ nguyên WMA/HTML. Không cắt, ghép hoặc thay nội dung bài nghe.
- Thời lượng WMA 570,068 giây, MP3 570,096 giây (chênh 0,028 giây). Giải mã toàn bộ hai bản; so sánh PCM ở giây 5/285/560 đạt tương quan >0,9996, không lệch mẫu ở 8 kHz. Browser phát/tua ở đầu/giữa/cuối trên desktop/touch đạt. Encoder có cảnh báo timestamp DTS không tăng đơn điệu từ nguồn nhưng thoát 0; các kiểm tra giải mã/thời lượng/PCM/trình duyệt đều đạt. Chi tiết: [audio-compatibility.json](audio-compatibility.json).
- Kết quả này xác nhận tương thích kỹ thuật và giữ nguồn, không thay cho nghe thủ công toàn bộ bản ghi để thẩm định nội dung.

## Thư viện, catalog và Admin

Thêm release batch trong `assets/grade7-dual-links.js` và `assets/catalog-release.js`; snapshot `catalog/current-library-catalog.json` tăng 247 → 261 liên kết. Chỉ thêm 14 game vào Grade 7 → Đề thi GHK1 → từng trường, đúng cặp đề số 1. Bỏ đúng 14 link mới thì catalog khớp hoàn toàn main cũ. Tên hiển thị theo catalog; Đào Sư Tích thêm tiền tố THCS đã được HTML xác nhận, Cát Thành giữ nhãn catalog trong khi JSON nguồn ghi THCS TT Cát Thành. Không đổi tên hay nội dung HTML nguồn.

Không sửa index hoặc logic đăng nhập. `library.js` vẫn chỉ hiển thị overlay sau khi xác thực quyền và nhận catalog Firebase hợp lệ từ server. Chống trùng URL tương đối/mã hóa/Pages, giữ title/hidden Admin đã đặt và tôn trọng xóa sau khi ghi nhận release. Không ghi production.

Sau phát hành code, overlay có thể hiện game khi học sinh đăng nhập. Để lưu batch vào Firebase và quản lý lâu dài, Admin có thể sao lưu, bấm **Bổ sung bài mới từ GitHub vào bản nháp**, kiểm tra rồi **Lưu danh mục**. Không cần tạo lại Firebase/tài khoản.

## Kiểm thử đã chạy

- Builder Grade 7 --verify: 14 launcher/data khớp JSON và DOM nguồn; source controls được kiểm kê/ánh xạ đầy đủ. Builder Grade 6/8 --verify cũng đạt.
- Node model/source/progress/sound/catalog delta: **41 đạt**. Catalog/release/preflight/school-folders: **41 đạt**. Check catalog: **261 URL duy nhất có thật**, giữ hash v1 gốc và cơ chế v2.
- Grade 7 browser: **14 game / 589 câu**, cả hai chế độ, nội dung/đoạn đọc, lựa chọn/text/multi-field/chips/rewrite, pending, XP, repeat check, resume, học sinh/mã riêng/reset, mọi track nghe phát/tạm dừng/tua ±5s/tốc độ. Không lỗi JS/Console/HTTP trong lượt bình thường.
- Hồi quy Grade 6: **16 game / 661 câu**; Grade 8: **19 game / 793 câu**, đều đạt.
- Native WAV: **49/49 desktop và 49/49 touch emulation**, 10 nhóm đạt: đúng/sai/hoàn thành, gain 70%, mute/restore/XP, không phát lại, Listening không bị ngắt, WAV 404/hỏng/chậm/decode lỗi và hủy lượt phát. Bộ test được mở rộng cho câu text ở đầu đề Trực Hùng, không giả định câu đầu luôn là trắc nghiệm.
- Shared sound loading/cache/import/retry/timeout: **9 nhóm đạt**; Web Audio fallback: **9 nhóm đạt**.
- Grade 7 catalog browser: **4 nhóm đạt**, 14 cặp đề/game trong 14 trường; tìm kiếm/ẩn/tên Admin/ẩn folder/clear; 360/390/768/1280px; DOM Grade 4/5/6/8 không đổi; catalog rỗng trước bước hiển thị fixture.
- Cross-grade desktop/touch: dùng chung tên/mã/mute giữa **7 → 6 → 8**, nhãn đúng khối, tiến độ và XP từng đề/học sinh độc lập, reset không xóa dữ liệu cũ.
- Media browser: tái hiện WMA lỗi codec 4 trong fixture riêng; MP3 phát và seek đầu/giữa/cuối trên desktop/touch, thời lượng khớp.
- Kiểm thử numbering trước đây Grade 6/7 và Grade 8 đạt. Fixture lịch sử Grade 6/7 giữ tập đề cũ; các game mới được kiểm trong bộ riêng.
- YAML workflow, `git diff --check`, đóng gói `.site` đạt. Không upload artifact. Đã xem ảnh game mobile có nhãn Grade 7 và câu hai ô nhập.

Bằng chứng: [verification.json](verification.json). Danh sách file: [changed-files.txt](changed-files.txt). Chromium thực tế với desktop và mô phỏng mobile/touch; chưa kiểm tra điện thoại vật lý, Safari hoặc binary Edge riêng. Không chạy Firebase Auth production; các file Auth/session/Admin/Rules không đổi. Kiểm tra fixture hiển thị không được coi là kiểm thử Authentication thật. Truy cập Pages bị proxy CONNECT 403 (cả lần thử quyền mở rộng), nên chưa xác nhận phiên bản công khai.

## Đưa lên website

1. Duyệt Pull Request và merge khi đã kiểm tra. Tác vụ này không tự merge hoặc deploy.
2. Chạy workflow **Publish reviewed library to GitHub Pages (manual only)** trên `main`, nhập xác nhận theo quy trình hiện có.
3. Đăng nhập thư viện → Grade 7 → Đề thi GHK1 → trường → Game đề số 1 (2 chế độ). Nếu còn cache danh mục cũ, hard reload/xóa cache rồi kiểm tra lại.
4. Admin có thể nhận batch vào bản nháp và Lưu như mô tả trên; không khởi tạo lại Firebase.
5. Bổ sung file nghe Trực Cường/Trung Đông và duyệt 17 câu pending khi có nguồn xác nhận trước khi bật tự chấm cho chúng.
