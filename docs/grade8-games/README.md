# HT ENGLISH — Bộ máy game lớp 8, giai đoạn A/B

Nhánh: `experiment/grade8-shared-game-pilot`.

Đã quét 20 HTML nguồn trong 19 thư mục của `grade-8/De_thi_GHK1/`: 19 nội dung duy nhất, hai HTML Trực Tuấn giống nhau. Danh sách, cách đếm và báo cáo riêng từng nguồn nằm tại [INVENTORY.md](INVENTORY.md) và [inventory.json](inventory.json).

**Chỉ tạo ba game thử nghiệm mới. Dừng ở giai đoạn C theo yêu cầu: chưa tạo hàng loạt, chưa đổi index/danh mục Firebase, chưa merge/deploy.** Game Trực Tuấn tham chiếu và mọi file đã có trước nhiệm vụ này được giữ nguyên.

## Ba game thử nghiệm

| Đề | Game HTML | Câu | Phần | Audio vật lý | Đặc điểm |
| --- | --- | ---: | ---: | ---: | --- |
| THCS Trực Khang | [Mở file game](../../grade-8/De_thi_GHK1/11_THCS_Truc_Khang/practice-game-pilot.html) | 42 | 8 | 1 | A/B/C, A/B/C/D, nghe điền tối đa hai từ trong bảng, chia động từ, đọc, ghép và viết lại |
| THCS Trực Hùng | [Mở file game](../../grade-8/De_thi_GHK1/12_THCS_Truc_Hung/practice-game-pilot.html) | 43 | 8 | 1 | Nghe chọn/True–False, ba câu ngữ âm/trọng âm, nguồn có hai ID B_I_4a/B_I_4b riêng, thẻ từ dạng cụm |
| THCS Trực Chính | [Mở file game](../../grade-8/De_thi_GHK1/19_THCS_Truc_Chinh/practice-game-pilot.html) | 42 | 8 | 2 | HTML dựng động từ dữ liệu, một câu gồm hai ô bắt buộc, nhiều biến thể và một bộ thẻ mâu thuẫn |

Các liên kết trên trỏ tới mã nguồn trên nhánh, không phải website đã triển khai. Để chơi, tải checkout/ZIP của nhánh và phục vụ thư mục repository bằng máy chủ tĩnh. Các game không cần Firebase, tài khoản hay backend. Có thể dùng `python3 -m http.server 8000`; mở đường dẫn tương đối của từng game trong trình duyệt trên máy của bạn. Máy chủ có HTTP byte-range cho MP3 giúp tua audio ổn định; máy chủ trong bộ kiểm thử có sẵn tính năng này.

Mỗi game có `practice-game-data.js`, `practice-game-support.js` riêng cùng thư mục. Logic/CSS/model/icon dùng chung ở `grade-8/De_thi_GHK1/shared-practice/`. Noto Sans dùng bốn font Latin/Vietnamese 400/700 có sẵn tại `grade-7/De_thi_GHK_1/fonts/`; giữ cây thư mục khi sao chép.

## Kiến trúc

1. **Quét nguồn:** `tools/grade8-games/inventory.py` đọc HTML bằng DOMParser, ghi cấu trúc, bộ đáp án tĩnh, audio/hình ảnh và SHA-256. Bộ đọc literal Node chỉ đánh giá object/array riêng lẻ trong context có timeout; không chạy cả script đề để đoán đáp án. Các phần chứa hàm, biểu thức động hoặc regex không được tự suy diễn.
2. **Adapter có tên:** `convert.py` chỉ cho phép ba mẫu trong `PILOTS`. Adapter hiểu selector, ID, bộ đáp án, bài đọc, transcript và thẻ của đúng nguồn đó. Trực Chính cần chạy script của chính HTML nguyên bản trên loopback để lấy giao diện dựng động; mọi request ngoài loopback bị chặn. Không sửa HTML nguồn.
3. **Dữ liệu từng đề:** `schemaVersion`, thông tin nguồn/hash, `sections`, `questions`, `contexts`, `tracks`, `sourceSnapshot`, `issues`. `sourceRaw` giữ nguyên bản ghi đáp án/lời giải; `rearrangeSource` giữ bộ thẻ riêng nếu cần. Mã câu nguồn được giữ, số thứ tự hiển thị chỉ giúp điều hướng.
4. **Model dùng chung:** `model.js` kiểm tra cấu trúc và đối chiếu toàn bộ đáp án/biến thể nguồn. Các dạng hỗ trợ: `choice`, `text`, `multi-text`, `rearrange`. True/False là lựa chọn T/F, phát âm giữ gạch chân, ngữ pháp/đọc/viết được mô tả bằng dữ liệu. Không cố định 42 câu, bốn phần, bốn lựa chọn hay hai audio riêng biệt.
5. **Giao diện dùng chung:** `engine.js` và `game.css` kế thừa phong cách Trực Tuấn: nhập tên, chọn thử thách, giữ nháp khi đổi câu/phần, lời giải, XP, tổng kết, ôn lại, nghe/tua/tốc độ. Mỗi launcher HTML được dựng từ `tools/grade8-games/shell.html`; không nhân bản logic JavaScript theo trường.
6. **Hỗ trợ bổ sung:** ba bản dịch/mẹo AI thí điểm nằm riêng trong ba `practice-game-support.js`, có `provenance: AI-generated`, `teacherVerified: false`. Giao diện ghi rõ **AI tạo, chưa được giáo viên xác nhận**. Các tệp này không được dùng để chấm điểm. Không tự tạo bản dịch cho toàn bộ 127 câu: lời giải tiếng Việt nguồn được giữ nguyên; bản dịch riêng cho các câu còn lại cần được biên soạn/duyệt ở bước sau.

Ngữ cảnh đọc và bảng nghe giữ bên cạnh câu hỏi; trên màn hình hẹp khung ngữ cảnh có thể cuộn và vẫn hiện khi trả lời. Transcript chỉ được đưa vào khung hiển thị sau khi kiểm tra câu hiện tại. Với một MP3 chung cho hai phần nghe, giữ nguyên cả file và cho học sinh tua; không tự tạo mốc cắt audio.

## Quy tắc chấm và điểm cần giáo viên duyệt

- Đúng lần đầu theo đáp án nguồn: 10 XP. Kiểm tra lại/navigating/review không cộng thêm. Đáp án lần đầu và XP được giữ trong phiên; tải lại trang bắt đầu phiên mới, không lưu tên/kết quả lên backend.
- Câu gồm hai ô chỉ đúng khi cả hai khớp tuple nguồn. Mỗi câu nhận tối đa 10 XP, không nhân đôi vì có hai ô.
- Tự luận đối chiếu cả câu, không dùng `includes(keyword)` hoặc từ khóa để đoán đúng. Các câu Yes/No ngắn chỉ được chấp nhận nếu nguồn nêu rõ chúng là biến thể hợp lệ. Bỏ qua khác biệt hoa/thường, khoảng trắng và dấu câu theo quy ước luyện tập; không tuyên bố đây là bộ chấm ngữ nghĩa/NLP.
- Câu chỉ có mẫu không rõ ràng hoặc bộ thẻ không thể sử dụng an toàn được chuyển sang **chờ giáo viên**: vẫn cho nhập/ghép, kiểm tra và xem nguồn; không tự đánh đúng/sai hoặc cộng XP. Số câu chờ giáo viên được thống kê riêng khỏi câu sai/chưa làm.
- Nhiều biến thể nguồn, đáp án không dựng được từ thẻ, ghi chú hiệu chỉnh và bất nhất về thì đều có cờ duyệt. Bộ máy không tự sửa từ/đáp án gốc.

Các trường hợp cần xem kỹ:

- **Trực Hùng C_II_B3, D_II_1:** mẫu có phần tùy chọn/biến thể và checker gốc dựa vào từ khóa. Hai câu giữ mẫu nguồn và chờ giáo viên, không tự kết luận câu trả lời khác là sai.
- **Trực Chính C2B_4, C2B_5:** đáp án gợi ý có nhiều cách diễn đạt dạng “Or”; cần xác nhận câu trả lời đầy đủ.
- **Trực Chính D1_1:** pool có `fluent`, `speaks`, `does`, trong khi mẫu có `speak/fluently`; một số targetOrders không dựng được từ pool, một số giữ lỗi ngữ pháp. Giữ toàn bộ nguồn và pool, tắt chấm tự động câu này.
- **Trực Chính B2_3:** một câu có hai ô; giữ cả prompt gốc có `(do)` trong ngữ cảnh vì renderer HTML gốc lại bỏ gợi ý đó. **B2_4** có hai đáp án gave/gives; **D2_3** câu gốc dùng spend nhưng câu viết lại có took. Không tự đổi nguồn; cần giáo viên xác nhận.
- **Trực Khang:** có nhiều biến thể văn bản trong đáp án nguồn; giữ đúng những biến thể được nêu, đánh dấu để duyệt trước khi dùng làm đánh giá chính thức.

Danh sách đầy đủ kèm ID câu nằm trong từng báo cáo JSON ở [INVENTORY.md](INVENTORY.md). XP chỉ là kết quả luyện tập theo nguồn, không phải điểm kiểm tra chính thức.

## Bằng chứng kiểm thử

- 49 HTML/audio/ảnh nguồn được so SHA-256 với baseline main `33f05fa`; không đổi byte nào. Index, catalog, Firebase config/Rules và game mẫu Trực Tuấn cũng được so với baseline.
- `verify.py` đối chiếu toàn bộ ID, nguyên văn bản ghi đáp án/lời giải, phương án, thẻ, đoạn đọc, transcript và ánh xạ tài nguyên; chạy tái tạo với `--verify` để kiểm tra dữ liệu/launcher đã commit khớp nguồn mà không ghi file.
- 6 nhóm kiểm thử model: cấu trúc động, ID trùng, thiếu dữ liệu, biến thể/tuple, câu phủ định/thiếu ý/từ khóa, dữ liệu mâu thuẫn và tách AI khỏi chấm điểm.
- Chromium thao tác tất cả **127/127 câu** trên ba game; mỗi game có 6 nhóm kiểm thử. Bao gồm đúng/sai/chờ duyệt, XP đúng một lần, ôn câu sai, ghép thẻ/hoàn tác/làm lại, nhập hai ô, nguồn chưa duyệt, audio thật, pause/tua/ba tốc độ/transcript, cảm ứng và đường dẫn `/library/`.
- Mọi phần và màn hình chào kiểm tra ở 360/390/768/820/1280px; không tràn ngang; ngữ cảnh vẫn hiển thị. Không có lỗi JavaScript/console và không có request ngoài/backend/Firebase trong các game.
- Kiểm tra bổ sung: ID audio không cần trùng ID phần; dữ liệu hỏng phải hiện thông báo cho giáo viên và vô hiệu nút bắt đầu, không để màn hình im lặng hoặc crash.
- Mỗi pilot report có `questionsExercised`, các cờ duyệt, số câu cần chấm tay, số audio/hình và hash dữ liệu đã kiểm thử. CI lưu JSON/ảnh chụp thành artifact; không deploy.

Đây là kiểm thử nội dung khớp HTML và khả năng chạy. Không thay cho việc giáo viên nghe/đối chiếu thủ công MP3, Word, chuẩn phát âm hoặc chấp thuận đáp án; không khẳng định các file đáp án nguồn đều đúng về học thuật.

Chạy lại với Node 24, Python 3.12 và Playwright 1.58.0:

```sh
python3 -m pip install playwright==1.58.0
python3 -m playwright install --with-deps chromium
python3 tools/grade8-games/inventory.py
python3 tools/grade8-games/verify.py
node --test tests/grade8-shared-model.test.mjs
python3 tests/grade8-shared-game-browser.py
python3 tools/grade8-games/reports.py
```

Nếu Chromium hệ thống ở vị trí khác, đặt `CHROMIUM_PATH`. `GRADE8_GAME_TEST_OUTPUT` chọn thư mục JSON/ảnh, mặc định `/tmp/ht-grade8-pilot-tests`. Cache nguồn `/tmp/ht-grade8-source-scan.json` được tái tạo bởi inventory. Đổi nội dung nguồn phải quét lại và duyệt lại baseline; không sửa hash để che thay đổi.

## Tạo game cho đề mới — sau khi được duyệt giai đoạn C

1. Giữ nguyên thư mục/số thứ tự/HTML/audio mới. Chạy inventory và kiểm tra dạng câu, nguồn đáp án, đoạn đọc, transcript, ảnh và ánh xạ audio. Không copy adapter chỉ vì giao diện trông giống nhau.
2. Thêm một adapter có tên cho cấu trúc mới hoặc tái dùng adapter đã đối chiếu; chỉ chuẩn hóa trường dữ liệu, không tự đổi đáp án. CLI hiện chỉ cho phép ba mẫu đã chọn, **không có tùy chọn tạo hàng loạt**.
3. Nếu thiếu dữ liệu hoặc chưa hiểu dạng câu, trả lỗi rõ ràng và bổ sung báo cáo. Không lấy ví dụ của đề khác để lấp chỗ trống. Mẫu có đáp án mơ hồ đi vào danh sách duyệt, không chấm bằng từ khóa.
4. Dựng dữ liệu/launcher từ shell và shared engine; giữ AI hỗ trợ trong tệp riêng, không ghi đè phần giáo viên đã sửa. `convert.py` không ghi đè tệp hỗ trợ đã tồn tại.
5. Đối chiếu với nguồn, kiểm thử đủ từng câu, hai loại thao tác đúng/sai/chờ duyệt, tài nguyên và giao diện. Chỉ coi chuyển đổi đạt khi report ghi toàn bộ ID đã được thao tác và các lỗi đã được xử lý hoặc đánh dấu chấm tay.
6. Giáo viên duyệt báo cáo/đáp án trước khi đưa vào danh mục. Lưu việc hiệu chỉnh có nguồn gốc rõ ràng ở tệp riêng; không xóa hay thay đề gốc.

Kế hoạch tương thích index/Firebase nằm tại [INDEX_COMPATIBILITY.md](INDEX_COMPATIBILITY.md). Nhiệm vụ hiện tại chưa thực hiện kế hoạch đó.
