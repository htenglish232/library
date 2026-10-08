# Báo cáo audio — Đề thi GHK 1 lớp 6

## Phạm vi và kết quả

Thư mục thực tế duy nhất: `grade-6/De_thi_GHK_1`.

- Đã kiểm tra **16 folder đề thi, 16 file HTML, 26 file âm thanh** (25 MP3 và 1 WAV).
- Đã chỉnh sửa **12 file HTML**, thêm **21 player HTML5** sử dụng file nghe trong chính folder đề thi.
- Không đổi cấu trúc folder, tên file hoặc dữ liệu âm thanh. Không sửa HTML ngoài thư mục này.
- Hai đề dùng **một player chung**: `5_THCS_Trung_Dong`, `11_THCS_Truc_Dao`.
- Chín đề dùng **hai player riêng**: Cổ Lễ, Trực Tuấn, Trực Hùng (1), Trực Thắng, Trực Thuận, Phương Định, Trực Hùng (12), Trực Thái, Trực Nội.
- Đào Sư Tích: nâng cấp **Part 2**; giữ nguyên cách nghe Part 1 vì nguồn còn cần xác nhận.
- Giữ nguyên toàn bộ HTML của Trực Cường, hai đề Liêm Hải và Việt Hùng.

## Nguồn nghe theo từng đề

Việc liên kết dùng tên Task/Part, vị trí file trong folder và mô tả Listening/transcript của HTML. Không coi file trùng dữ liệu trong các đề có transcript khác nhau là căn cứ để tự chọn một đề. Chưa có thẩm định nội dung bằng cách nghe thủ công toàn bộ 26 file.

| Folder | File nghe được liên kết | Player HTML5 mới | Ghi chú |
| --- | --- | ---: | --- |
| `1_THCS_Truc_Cuong` | — | 0 | Giữ nguyên. Nội dung HTML còn ghi Tiếng Anh 7; file Task 1/2 trùng dữ liệu với Đào Sư Tích nhưng transcript khác. Không tự gán. |
| `2_THCS_Co_Le` | `Mid-term test 1- Task 1.mp3`; `Mid-term test 1 - Task 2.mp3` | 2 | Một file riêng cho mỗi phần Listening. |
| `3_THCS_Truc_Tuan` | `GHK1 K6 - part 1 .mp3`; `GHK1 K6 - part 2 .mp3` | 2 | Một file riêng cho mỗi phần Listening. |
| `4_THCS_Truc_Hung_(1)` | `TASK 1.mp3`; `TASK 2.mp3` | 2 | Một file riêng cho mỗi phần Listening. |
| `5_THCS_Trung_Dong` | `LISTENING GK 1 E6.mp3` | 1 | Một file dùng chung cho cả hai phần. |
| `6_THCS_Liem_Hai` | — | 0 | Giữ nguyên giọng tổng hợp. MP3 trùng hệt đề số 7 nhưng Listening khác; cần xác nhận. |
| `7_THCS_Liem_Hai` | — | 0 | Giữ nguyên giọng tổng hợp. MP3 trùng hệt đề số 6 nhưng Listening khác; cần xác nhận. |
| `8_THCS_Truc_Thang` | `Anh 6- listening- task- 1.mp3`; `Anh_6- listening-_task_2.mp3` | 2 | Một file riêng cho mỗi phần Listening. |
| `9_THCS_Truc_Thuan` | `MIDTERM TEST 6 - PART I.mp3`; `MIDTERM TEST 6 - PART II.mp3` | 2 | Một file riêng cho mỗi phần Listening. |
| `10_THCS_Phuong_Dinh` | `1.mp3`; `2.wav` | 2 | Một file riêng cho mỗi phần Listening. |
| `11_THCS_Truc_Dao` | `Nghe  GIỮA KÌ I ANH 6.mp3` | 1 | Một file dùng chung cho cả hai phần. |
| `12_THCS_Truc_Hung` | `GHK1 K6 - part 1.mp3`; `GHK1 K6 - part 2.mp3` | 2 | Một file riêng cho mỗi phần Listening. |
| `13_THCS_Dao_Su_Tich` | `Task 2.mp3` | 1 | Part 2 dùng file riêng; Part 1 giữ nguyên giọng tổng hợp và cần xác nhận Task 1.mp3. |
| `14_THCS_Viet_Hung` | — | 0 | Không có file nghe trong folder; giữ nguyên hai nút đọc giọng tổng hợp, không tạo nguồn giả. |
| `15_THCS_Truc_Thai` | `TASK 1 .mp3`; `TASK 2 .mp3` | 2 | Một file riêng cho mỗi phần Listening. |
| `16_THCS_Truc_Noi` | `bài nghe 1.mp3`; `bai nghe 2.mp3` | 2 | Một file riêng cho mỗi phần Listening. |

## Bảo toàn nguồn cũ và nội dung đề

Không phát hiện nguồn Base64, URL audio trực tuyến hoặc nguồn file audio mặc định trong 16 HTML gốc. Trực Cường có hai phần tử `<audio>` chưa có nguồn mặc định và chức năng nạp file cục bộ tạo Blob URL; HTML này được giữ nguyên. Những đề còn lại dùng SpeechSynthesis cho bài nghe.

Các đề giữ nguyên cách nghe gốc: Trực Cường, Liêm Hải số 6, Liêm Hải số 7, Việt Hùng và Part 1 của Đào Sư Tích. Không xóa các hàm/đoạn transcript gốc. Ở những phần được nâng cấp, nút nghe tổng hợp cũ được ẩn để tránh hai bộ điều khiển; ID vẫn được giữ để không làm hỏng mã tham chiếu gốc.

Tất cả script gốc, đáp án, mã chấm điểm, câu hỏi và các trường nhập gốc được bảo toàn. Kiểm tra tái dựng: sau khi bỏ đúng các thành phần audio được thêm và các thuộc tính ẩn của nút nghe cũ, toàn bộ 16 HTML khớp bản gốc, ngoại trừ khoảng trắng cuối dòng ở hai nút audio của Trung Đông.

## Chức năng và giao diện

Mỗi player có Phát, Tạm dừng, Phát lại từ đầu, lùi/tiến 5 giây, thanh tiến trình, thời gian hiện tại/tổng thời lượng, âm lượng, trạng thái tải và thông báo lỗi. Chỉ bật tua khi có thời lượng hữu hạn và vùng seekable có độ dài dương; vị trí tua được giới hạn trong vùng cho phép. Không autoplay, không loop. Khi một audio phát, các audio khác cùng trang được tạm dừng.

Dùng JavaScript thuần và HTML5 Audio API; CSS chỉ áp dụng trong `.ht-audio-player`. Màu chủ đạo lấy từ class của nút nghe gốc từng phần, ví dụ indigo ở Phương Định/Trực Hùng, emerald ở Part 2 Trực Thắng và sky ở Part 2 Trực Thuận; không áp một màu cố định cho toàn bộ đề. Font được kế thừa. Nội dung CSS/JS nằm trong từng HTML để không cần thư viện hoặc file dùng chung mới.

Đường dẫn audio tương đối, mã hóa khoảng trắng và ký tự Unicode. Tất cả 21 đường dẫn đã được trình duyệt tải từ file hiện có; không đổi tên hoặc sao chép file nghe.

## Kiểm thử đã thực hiện

- **Chromium thực tế:** cả 12 HTML/21 player đều hoàn thành kiểm tra Phát/Tạm dừng/Phát lại, tua ±5 giây, kéo thanh tiến trình bằng sự kiện input và bàn phím, giới hạn tua, âm lượng, thời lượng, tạm dừng player khác và không autoplay/loop.
- **Lỗi tải:** thử nguồn không tồn tại trong bộ nhớ trang; cả 12 trang hiển thị thông báo lỗi. Không ghi đường dẫn thử nghiệm vào repository.
- **Bố cục:** kiểm tra các player ở màn hình desktop 1280 px và kích thước mobile 375/390 px; không tràn ngang trong player, nút có chiều cao tối thiểu 44 px. Đã xem ảnh chụp đại diện của player indigo và emerald.
- **Phục vụ audio:** kiểm tra qua HTTP cục bộ có hỗ trợ byte ranges/206 để trình duyệt thực hiện tua. Không triển khai lên GitHub Pages; tính tương thích đường dẫn được kiểm tra tại chỗ.
- **Chấm bài:** chạy cùng thao tác nhập thông tin/chọn đáp án/nộp bài trên bản gốc và bản sửa của 16 HTML, đối chiếu kết quả và lỗi. Lỗi Trực Đạo nêu bên dưới xuất hiện ở cả hai bản.
- **Bảo toàn:** script gốc và các trường câu hỏi khớp; không sửa file nghe; `git diff --check` không báo lỗi.
- **FFmpeg:** giải mã 26 file. Có cảnh báo khung MP3 ở ba file nêu bên dưới, dù lệnh kết thúc với mã 0 và Chromium phát/tua được các nguồn này trong kiểm tra.

Chưa kiểm thử trên thiết bị Android/iPhone thực, Safari hoặc Firefox; chưa nghe thủ công toàn bộ nội dung và chưa phát từ bản đã triển khai GitHub Pages. Chromium không tải được CDN Tailwind gốc trong môi trường này: kiểm tra bố cục dùng CSS Tailwind 3.4.17 biên dịch tạm từ các class hiện có, chỉ đưa vào trang kiểm thử, không thay đổi phụ thuộc hoặc CSS tổng thể của đề. Font/icon ngoài cũng chưa được xác nhận tải đầy đủ.

## Những mục cần kiểm tra tiếp

1. **Trực Cường:** xác nhận đúng lớp và đúng file nghe. HTML ở folder lớp 6 nhưng còn ghi Tiếng Anh 7. `Task 1.mp3` và `Task 2.mp3` trùng SHA-256 với hai file tương ứng của Đào Sư Tích, trong khi transcript Trực Cường là Tom/Jack và hoạt động câu lạc bộ, còn Đào Sư Tích là Nam/Mrs Nhi và Mai. Giữ nguyên HTML Trực Cường; không thay nội dung đề để khớp audio.
2. **Liêm Hải số 6 và số 7:** cùng file `Nghe giua ki 1 Anh 6.mp3` trùng SHA-256; đề số 6 nói Janet/trường học và Mi/Minh, đề số 7 nói Maya và Linda/Tom. Cần xác nhận nội dung file trước khi nhúng cho một hoặc cả hai đề.
3. **Đào Sư Tích Part 1:** `Task 1.mp3` thuộc nhóm trùng dữ liệu với Trực Cường nêu trên; giữ nguyên nút nghe tổng hợp chờ xác nhận. Part 2 đã liên kết `Task 2.mp3` theo tên phần và transcript Mai, cũng trùng file bài nghe 1 của Trực Nội có transcript Mai.
4. **Việt Hùng:** thiếu file nghe thực. SpeechSynthesis hiện tại không cung cấp thời lượng/seekable như HTML5 Audio; giữ nguyên, không tạo player rỗng hoặc đường dẫn giả.
5. **Khung MP3:** FFmpeg báo `Header missing`/`Invalid data found when processing input` cho `4_THCS_Truc_Hung_(1)/TASK 1.mp3`, `8_THCS_Truc_Thang/Anh 6- listening- task- 1.mp3` và `10_THCS_Phuong_Dinh/1.mp3`. Hai file Task 1 đầu tiên trùng dữ liệu. Chưa sửa hoặc mã hóa lại file nghe; cần bản gốc sạch nếu muốn loại bỏ cảnh báo. Một số MP3 có thời lượng được Chromium cập nhật khi đọc tới cuối; player cập nhật theo `durationchange`.
6. **Lỗi chấm bài có sẵn ở Trực Đạo:** `data-valid='["lan is nam\'s sister."]'` dùng dấu nháy đơn có dấu gạch chéo để escape trong thuộc tính HTML. HTML không hỗ trợ cách escape này nên thuộc tính bị cắt, dẫn tới `JSON.parse` lỗi `Unexpected end of JSON input`. Lỗi được tái hiện ở bản gốc và bản sửa; không thay mã chấm điểm trong nhiệm vụ audio.
7. **CDN có sẵn:** một số trang báo `tailwind is not defined` do CDN không tải được trong môi trường kiểm thử. Đây là phụ thuộc giao diện gốc; không thay cấu hình hoặc thêm thư viện cho đề trong nhiệm vụ này.

Các nguồn chưa rõ không được gán tự động. Không có lỗi đường dẫn hoặc lỗi tải tồn đọng trong 21 nguồn đã liên kết ở máy chủ kiểm thử; cảnh báo khung MP3 và các mục cần xác nhận trên vẫn còn.
