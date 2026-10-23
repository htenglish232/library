# HT ENGLISH — English Quest 8, THCS Trực Tuấn

Trang chính: [`../truc-tuan-game-test.html`](../truc-tuan-game-test.html).

Nhánh thử nghiệm: `experiment/truc-tuan-grade8-game`. Bản đầy đủ 42 câu, độc lập với giao diện/chấm điểm của đề gốc. Không đổi hoặc ghi đè hai HTML hay hai MP3 gốc. Không yêu cầu tài khoản, Firebase, backend, CDN hay bước build.

## Sử dụng

1. Mở trang chính, nhập họ tên rồi bấm **Bắt đầu hành trình**.
2. Chọn một trong bốn thử thách; có thể đổi thử thách, đi câu trước/tiếp hoặc bấm số câu. Câu đang làm và đáp án đã kiểm tra được giữ trong trang đang mở.
3. Chọn đáp án hoặc nhập phần trả lời. Các câu viết lại chỉ nhập phần sau mũi tên. Với câu ghép, bấm thẻ theo thứ tự; bấm thẻ đã chọn để gỡ, hoặc dùng Hoàn tác/Làm lại.
4. Bấm **Kiểm tra đáp án** để xem đáp án nguồn, lời giải, kiến thức, dịch nghĩa, lỗi thường gặp, dẫn chứng và từ khóa bài đọc. Transcript chỉ xuất hiện sau khi kiểm tra câu nghe đang làm; không tự mở transcript của câu chưa làm khi chuyển câu.
5. Bài nghe có phát/tạm dừng, tua ±5 giây, thanh tua và tốc độ 0.75×/1×/1.25×. Có thể tiếp tục nghe sau khi kiểm tra đáp án; đổi phần sẽ tạm dừng audio.
6. Mỗi câu đúng **lần đầu** nhận 10 XP, tối đa 420 XP. Câu đã kiểm tra khóa đáp án của lần đầu. Bấm nhiều lần hoặc quay lại câu không cộng thêm XP.
7. Mở **Kết quả** bất cứ lúc nào để xem đúng lần đầu, cần ôn và chưa trả lời. **Ôn lại câu cần luyện** cho phép làm lại các câu chưa khớp đáp án nguồn. Lượt ôn không thay đổi XP/kết quả lần đầu. Rời chế độ ôn sẽ khôi phục đáp án của lần đầu.

Tiến độ và tên chỉ nằm trong bộ nhớ trang. Tải lại/đóng trang sẽ mất phiên; không gửi tên, câu trả lời hoặc kết quả lên máy chủ. Cần giữ tab mở để tiếp tục cùng phiên.

## Dữ liệu cần giáo viên xác nhận

Đọc [PHAN_TICH_NGUON.md](PHAN_TICH_NGUON.md) trước khi dùng để đánh giá chính thức:

- q12: HTML F, ghi chú nói Word T; nhận định “light” so với transcript “strong”.
- q13: biến thể phát âm nguyên âm không nhấn trong activity; giữ B của nguồn.
- q19: “lunch tonight” và lời đáp C có thể chấp nhận tùy ngữ cảnh; giữ B của nguồn.
- q29: keep fit và stay fit đều phù hợp; giữ D của nguồn, nhắc đối chiếu nếu chọn A.
- q40: yours / your bike trong HTML so với his được ghi trong ghi chú Word.
- Tự luận: chỉ tự nhận đáp án mẫu và biến thể được nguồn nêu rõ; cách diễn đạt khác hiển thị “chưa khớp”, cần giáo viên xem lại. Không dùng từ khóa con để nhận nhầm câu phủ định/câu thiếu ý.

Các lưu ý này hiện ngay trong lời giải liên quan. XP là kết quả luyện tập theo đáp án HTML, không phải điểm kiểm tra chính thức. Không tự thay đáp án để giải quyết các câu còn mơ hồ; chưa có file Word và chưa xác minh thủ công từng nội dung MP3.

## Cấu trúc và triển khai

- `../truc-tuan-game-test.html`: trang vào.
- `game.css`, `game.js`: giao diện và trạng thái trò chơi.
- `source-data.js`: 42 câu, phương án, đáp án, lời giải, ghi chú, đoạn đọc, transcript và thẻ từ trích từ nguồn.
- `learning-notes.js`: bản dịch, lỗi thường gặp, từ khóa và lưu ý giáo viên bổ sung, tách khỏi dữ liệu gốc.
- Hai MP3 dùng đường dẫn tương đối ngay cạnh HTML chính. Giữ nguyên dấu cách trong tên file bài 2.
- Noto Sans được tải từ các file có sẵn tại `grade-7/De_thi_GHK_1/fonts/` qua CSS tương đối. Nếu sao chép ra nơi khác, giữ cây thư mục hoặc sao chép font và sửa URL trong CSS bản sao.

Mở HTML trực tiếp cùng các file phụ trên máy, hoặc phục vụ kho mã bằng `python3 -m http.server 8000`. Để kiểm tra tua audio trên máy chủ thử nghiệm, dùng máy chủ hỗ trợ HTTP byte ranges (bộ kiểm thử bên dưới có sẵn); GitHub Pages hỗ trợ tính năng này.

Không thêm game vào danh mục Firebase/index trong nhánh thử nghiệm. Dùng liên kết trực tiếp để giáo viên xem trước.

Đưa lên GitHub Pages sau khi giáo viên xem PR:

1. Merge PR khi sẵn sàng; nhánh thử nghiệm không tự merge hay tự triển khai.
2. Chạy workflow **Publish reviewed library to GitHub Pages (manual only)** trên `main`; nhập xác nhận `DEPLOY HT ENGLISH LIBRARY`.
3. Đợi job publish thành công. Đường dẫn dự kiến lúc đó:
   `https://htenglish232.github.io/library/grade-8/De_thi_GHK1/1_THCS%20Truc%20Tuan/truc-tuan-game-test.html`
4. Không coi đường dẫn trên là preview đã triển khai trước khi job publish thành công. Nếu cần bản kiểm thử 5 câu, thêm `?pilot=1`.

Đã kiểm tra công cụ đóng gói `.site`: có HTML game, dữ liệu/JS/CSS, cả hai MP3 nguyên bản và các font cục bộ. `tools/check-catalog.mjs` được điều chỉnh để cho thêm bài độc lập mới; vẫn chặn sửa/xóa/đổi tên file gốc đã duyệt. Không thay đổi Rules, cấu hình Firebase, SDK hay danh mục.

## Kiểm thử thực tế ngày 20/10/2026

Quy trình: phân tích nguồn → bản 5 câu q1/q16/q23/q26/q36 chạy Chromium đạt → bật đủ 42 câu → kiểm thử đầy đủ. Commit đầu lưu riêng bản thử nghiệm 5 câu để kiểm tra trình tự.

| Kiểm tra | Kết quả |
| --- | --- |
| SHA-256 hai HTML và hai MP3 so với main `395f33e` | Giữ nguyên cả 4 file |
| Trích xuất lại và đối chiếu toàn bộ dữ liệu | 42/42 câu, phương án, đáp án, lời giải, ghi chú, thẻ, 2 đoạn đọc, 2 transcript khớp |
| Bản 5 câu, Chromium thật | 11 nhóm đạt, 0 lỗi |
| Bản đầy đủ, Chromium thật | 13 nhóm đạt, 0 lỗi |
| Từng câu của đề đầy đủ | Đã thao tác kiểm tra 42/42 câu, gồm cả 10 câu nhập và 3 câu ghép |
| XP/tổng kết | Ca chủ ý 40 đúng + 2 cần ôn + 0 chưa làm = 400 XP; ôn đúng cả 2 vẫn 400 XP |
| Nghe | Hai MP3 tải/phát được; tạm dừng, tua, ba tốc độ; transcript ẩn trước/hiện sau kiểm tra |
| Điện thoại, máy tính bảng, máy tính | 360/390/768/820/1280 px; không tràn ngang; khung đọc giữ trên màn hình khi trả lời |
| Cảm ứng thật qua Playwright | Chọn đáp án, kiểm tra, chuyển phần, ghép thẻ, nhận XP |
| Đường dẫn GitHub Pages `/library/` | HTML/JS/CSS/font/MP3 phân giải đúng |
| Console/JavaScript | 0 lỗi |
| Yêu cầu mạng ngoài/backend/Firebase | 0 |
| Kiểm tra chuẩn bị hiện có của thư viện | 18/18 đạt; 208 liên kết danh mục hiện có giữ nguyên |

Không dùng kết quả này để khẳng định website công khai đã triển khai hoặc xác thực lại nội dung nghe bằng người thật. Bộ kiểm thử nghe xác nhận MP3 phát và điều khiển được; dữ liệu lời thoại lấy nguyên từ HTML.

Chạy lại (Python 3.12, Node 24):

```sh
python3 -m pip install playwright==1.58.0
python3 -m playwright install --with-deps chromium
python3 tests/truc-tuan-game-browser.py --pilot
python3 tests/truc-tuan-game-browser.py
npm run check:catalog
npm run test:prepare
```

Đặt `CHROMIUM_PATH` nếu cần chọn Chromium hệ thống. Kết quả JSON/ảnh chụp mặc định ở `/tmp/ht-truc-tuan-game-tests`; đổi bằng `GAME_TEST_OUTPUT`. CI `.github/workflows/truc-tuan-game-checks.yml` chạy hai lượt và lưu artifact báo cáo/ảnh, không deploy.

Muốn tái tạo dữ liệu nguồn (không đổi file gốc):

```sh
python3 tools/extract-truc-tuan-game.py
```

Sau đó luôn chạy lại bộ kiểm thử, vì thay đáp án nguồn có thể cần giáo viên rà soát phần ghi chú bổ sung.
