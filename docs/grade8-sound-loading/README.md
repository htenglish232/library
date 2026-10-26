# Sửa tải âm thanh toàn bộ game hai chế độ lớp 8

Nhánh `fix/grade8-shared-sound-loading`, từ `main:7f4be94` đã merge PR #37. Không merge, deploy, thay workflow triển khai hoặc ghi Firebase production.

## 1. Kết quả điều tra có bằng chứng

Quét **tất cả HTML** trong `grade-8/De_thi_GHK1/` bằng `tools/audit-grade8-sound-loading.py`, nhận diện theo `data-practice="dual-mode"` hoặc script engine. Phát hiện **19 game của 17 trường**; cả 19 dùng đúng một `shared-practice/dual-mode-engine.js`. Không lấy số lượng từ danh sách cũ để mặc định kết quả. Đọc lại dữ liệu của từng file để lấy trường/số đề/số câu và đối chiếu mọi CSS/script với tệp thật.

Đã kiểm tra lại bản main trước sửa qua HTTP cục bộ: **19/19 tải mới có nút hoạt động, không lỗi JavaScript**. Vì vậy chưa có bằng chứng engine main bị lỗi trên mọi lần tải hoặc thiếu 18 game.

Hai tình huống tái hiện được:

1. **Cache engine cũ làm mất nút:** phục vụ engine trước tính năng sound (`b38d578`) với cache hợp lệ, sau đó chuyển server sang HTML/main mới (`7f4be94`) trên cùng origin. Trình duyệt thật vẫn dùng engine cũ: **0 nút**, **0 request tải lại engine**. Các HTML cũ chưa có phiên bản URL engine/CSS và chỉ chờ JS tạo nút, nên có thể gặp đúng biểu hiện này. Fixture dùng `max-age=3600` để kiểm chứng hành vi; đây không phải số đo Cache-Control của website thật.
2. **currentScript null:** khi controller chạy trong ngữ cảnh module, bản cũ phát lỗi **Cannot read properties of null (reading 'src')** và nút nằm ở trạng thái “Âm thanh đang tải…”. Đối số `import(new URL(...document.currentScript.src))` được đánh giá đồng bộ, trước `.catch()`, nên lỗi đối số không được nhánh catch đó xử lý. Các launcher đang có dùng classic `defer`, vì vậy không khẳng định đây là nguyên nhân thực tế trên website. Bản sửa lưu URL ngay khi khởi tạo và có fallback qua script element.

### Website công khai: chưa thể xác minh

Đã thử đọc Trực Tuấn trước, sau đó **18 HTML khác và engine/sound/CSS: 22 URL**. Proxy của môi trường trả lỗi **CONNECT tunnel 403**, kể cả khi chạy lại với quyền mở rộng. Kết quả **0/22 nội dung lấy được**. Không thu được JS/HTML/HTTP header/Console công khai để so hash, không coi lỗi kết nối này là status 403/404 của website.

Công cụ lưu SHA256 của checkout và `origin/main`; khi có kết nối, nó ghi thêm hash nội dung Pages, `matchesMain`, `matchesCheckout`, Cache-Control/Age/ETag/Last-Modified để đối chiếu. Lần này chưa có hash nội dung public. **Chưa kết luận website đang chạy bản cũ, đã deploy PR #37 hay đang gặp lỗi mã cụ thể nào.** Hai tình huống trên là bằng chứng tái hiện cục bộ, không thay cho kiểm tra website thật.

Đã đọc `.github/workflows/pages-manual.yml`: phát hành chỉ qua `workflow_dispatch` trên main với xác nhận, không tự chạy khi merge. Không thể suy ra một lần deploy đã/ chưa chạy chỉ từ cấu hình workflow; chưa đọc được trạng thái Actions qua API.

## 2. Danh sách toàn bộ game đã kiểm tra

Các đường dẫn dưới đây là file thật trong repository. Cả 19 đã kiểm tra trình duyệt trên desktop và mô phỏng touch 390px: một nút ready, đúng/sai, ghi nhớ mute, khôi phục XP; cả 19 kiểm tra completion đúng độ dài đề, không lặp khi tải lại. Không tuyên bố URL công khai đã được kiểm thử.

| Trường | Đề trong trường | Câu | Game đã sửa bootstrap | Kiểm thử |
|---|---:|---:|---|---|
| THCS Trực Tuấn | 1 | 42 | [1_THCS Truc Tuan](../../grade-8/De_thi_GHK1/1_THCS%20Truc%20Tuan/truc-tuan-dual-mode.html) | Desktop/touch/đúng/sai/hoàn thành đạt |
| THCS Đào Sư Tích | 1 | 42 | [2_THCS Dao Su Tich](../../grade-8/De_thi_GHK1/2_THCS%20Dao%20Su%20Tich/practice-dual-mode.html) | Desktop/touch/đúng/sai/hoàn thành đạt |
| THCS Trung Đông | 1 | 42 | [3_THCS Trung Dong](../../grade-8/De_thi_GHK1/3_THCS%20Trung%20Dong/practice-dual-mode.html) | Desktop/touch/đúng/sai/hoàn thành đạt |
| THCS Trực Đại | 1 | 42 | [4_THCS Truc Dai](../../grade-8/De_thi_GHK1/4_THCS%20Truc%20Dai/practice-dual-mode.html) | Desktop/touch/đúng/sai/hoàn thành đạt |
| THCS Trực Thuận | 1 | 42 | [5_THCS Truc Thuan](../../grade-8/De_thi_GHK1/5_THCS%20Truc%20Thuan/practice-dual-mode.html) | Desktop/touch/đúng/sai/hoàn thành đạt |
| THCS Cát Thành | 1 | 37 | [6_THCS Cat Thanh](../../grade-8/De_thi_GHK1/6_THCS%20Cat%20Thanh/practice-dual-mode.html) | Desktop/touch/đúng/sai/hoàn thành đạt |
| THCS Trực Mỹ | 1 | 42 | [7_THCS Truc My](../../grade-8/De_thi_GHK1/7_THCS%20Truc%20My/practice-dual-mode.html) | Desktop/touch/đúng/sai/hoàn thành đạt |
| THCS Phương Định | 1 | 42 | [8_THCS Phuong Dinh](../../grade-8/De_thi_GHK1/8_THCS%20Phuong%20Dinh/practice-dual-mode.html) | Desktop/touch/đúng/sai/hoàn thành đạt |
| THCS Phương Định | 2 | 41 | [9_THCS_Phuong_Dinh](../../grade-8/De_thi_GHK1/9_THCS_Phuong_Dinh/practice-dual-mode.html) | Desktop/touch/đúng/sai/hoàn thành đạt |
| THCS Trực Đạo | 1 | 42 | [10_THCS_Truc_Dao](../../grade-8/De_thi_GHK1/10_THCS_Truc_Dao/practice-dual-mode.html) | Desktop/touch/đúng/sai/hoàn thành đạt |
| THCS Trực Khang | 1 | 42 | [11_THCS_Truc_Khang](../../grade-8/De_thi_GHK1/11_THCS_Truc_Khang/practice-dual-mode.html) | Desktop/touch/đúng/sai/hoàn thành đạt |
| THCS Trực Hùng | 1 | 43 | [12_THCS_Truc_Hung](../../grade-8/De_thi_GHK1/12_THCS_Truc_Hung/practice-dual-mode.html) | Desktop/touch/đúng/sai/hoàn thành đạt |
| THCS Đào Sư Tích | 2 | 42 | [13_THCS_Dao_Su_Tich](../../grade-8/De_thi_GHK1/13_THCS_Dao_Su_Tich/practice-dual-mode.html) | Desktop/touch/đúng/sai/hoàn thành đạt |
| THCS Việt Hùng | 1 | 42 | [14_THCS_Viet_Hung](../../grade-8/De_thi_GHK1/14_THCS_Viet_Hung/practice-dual-mode.html) | Desktop/touch/đúng/sai/hoàn thành đạt |
| THCS Trực Thái | 1 | 42 | [16_THCS_Truc_Thai](../../grade-8/De_thi_GHK1/16_THCS_Truc_Thai/practice-dual-mode.html) | Desktop/touch/đúng/sai/hoàn thành đạt |
| THCS Trực Nội | 1 | 42 | [17_THCS_Truc_Noi](../../grade-8/De_thi_GHK1/17_THCS_Truc_Noi/practice-dual-mode.html) | Desktop/touch/đúng/sai/hoàn thành đạt |
| THCS Trực Cường | 1 | 42 | [18_THCS_Truc_Cuong](../../grade-8/De_thi_GHK1/18_THCS_Truc_Cuong/practice-dual-mode.html) | Desktop/touch/đúng/sai/hoàn thành đạt |
| THCS Trực Chính | 1 | 42 | [19_THCS_Truc_Chinh](../../grade-8/De_thi_GHK1/19_THCS_Truc_Chinh/practice-dual-mode.html) | Desktop/touch/đúng/sai/hoàn thành đạt |
| THCS Cổ Lễ | 1 | 42 | [20_THCS_Co_Le](../../grade-8/De_thi_GHK1/20_THCS_Co_Le/practice-dual-mode.html) | Desktop/touch/đúng/sai/hoàn thành đạt |

## 3. Sửa 19/19 game qua bootstrap và một loader chung

- Đặt sẵn **một** nút `🔊 Âm thanh: Bật` trong HTML, trạng thái loading/aria-busy. Nút hiện ngay cả trước khi engine tải xong. Controller tái sử dụng nút, không tạo bản trùng. Khi module đọc lựa chọn đã lưu sẽ chuyển thành Bật/Tắt đúng trạng thái.
- Thêm `?v=20261026-sound-fix` vào URL engine và dual CSS trong cả 19 launcher; import sound dùng cùng phiên bản. Trình duyệt đã cache engine chưa có sound sẽ yêu cầu URL engine mới. Giữ nguyên tên/đường dẫn mở game, không đổi catalog hoặc index.
- Lưu URL script đồng bộ ngay ở đầu controller. Khi `document.currentScript` không khả dụng, tìm đúng script engine trong DOM. Việc khởi tạo module, timeout và thử lại chỉ dùng URL đã lưu; không đọc currentScript trong callback. URL không phân giải được cũng chuyển trạng thái lỗi và để game tiếp tục khởi tạo.
- Loading → ready / unsupported / **⚠ Âm thanh: Lỗi tải**. Lỗi/timeout 10 giây giữ nút hiển thị và cho nhấn thử lại. Retry dùng query riêng để tránh giữ lỗi import trong module map; kết quả trễ của lần tải đã timeout không ghi đè trạng thái. Không phát lại đáp án đã kiểm tra trong thời gian chờ tải.
- Dùng nguyên `shared-practice/dual-sound.js`, không nhân bản hoặc thay bộ tạo tiếng. Vẫn đúng hai nốt tăng 0,5s, sai hai nốt trầm giảm 0,4s, hoàn thành 1,5s; xử lý trusted gesture và mute/localStorage như trước. Không tạo context trước thao tác học sinh. Không thêm MP3/dependency runtime.
- Không đổi vị trí/màu/bố cục game sau khi tải xong: nút tĩnh nằm đúng vị trí nút từng được JS append. Chỉ bổ sung trạng thái loading/error cho điều khiển âm thanh.

Không sửa dữ liệu, đáp án, âm thanh Listening, hàm chấm, `dual-progress.js`, `dual-store.js`, contentVersion hoặc khóa tiến độ. Không đổi index/admin/catalog/Firebase/quyền/các lớp khác. Mỗi HTML launcher chỉ có **ba thay đổi cho phép**: query engine, query CSS, nút tĩnh. Guard kiểm thử xóa đúng các đoạn này rồi so byte với Git baseline để chặn thay đổi ngoài phạm vi. Toàn bộ 18 data sinh lại đều khớp nguồn cũ.

## 4. File thay đổi

- **19 HTML launcher** liệt kê trong bảng: query phiên bản engine/CSS và nút dự phòng tĩnh, không sửa nội dung đề/câu hỏi.
- `grade-8/De_thi_GHK1/shared-practice/dual-mode-engine.js`: URL chụp lúc khởi tạo, nạp module có trạng thái/timeout/retry và tái sử dụng nút HTML.
- `tools/audit-grade8-sound-loading.py`: kiểm kê từ đĩa, kiểm tra engine/tài nguyên/metadata và đối chiếu public bằng GET khi được mạng cho phép.
- `tests/dual-mode-sound-loading-browser.py`: tái hiện cache thật và kiểm thử đủ game, script/module chậm, 404, retry, timeout, currentScript null và URL lỗi.
- `tests/dual-mode-sound-browser.py`: lấy danh sách game từ quét đĩa, yêu cầu trạng thái ready và kiểm tra hoàn thành một lần trên cả 19 đề, không chỉ Trực Tuấn.
- `tests/sound-bootstrap-contract.mjs`: định nghĩa chính xác các thay đổi bootstrap được phép; không bỏ qua toàn bộ HTML.
- `tests/dual-mode-sound.test.mjs`, `tests/grade8-all-dual.test.mjs`: kiểm tra toàn bộ dữ liệu và HTML còn nguyên sau khi chuẩn hóa đúng ba thay đổi bootstrap nói trên.
- `.github/workflows/grade8-dual-mode-checks.yml`: chạy thêm kiểm kê/loading/browser tests và lưu artifact; không sửa workflow deploy.
- `docs/grade8-sound-loading/README.md`, `verification.json`, `changed-files.txt`: báo cáo, bằng chứng và danh sách file đầy đủ.

## 5. Kiểm thử đã chạy

- `tests/dual-mode-sound-loading-browser.py`: **9 nhóm đạt**. Cache trước/sau được thử bằng HTTP cache Chromium thật (không dùng route/mock tắt cache ở tình huống đó). Đủ **19/19 desktop và 19/19 touch**, đúng/sai, nút duy nhất, mute/reload, tiến độ/XP. Nút hiện trước engine, module chậm không chặn game, tiêm 404 có error/retry, timeout/kết quả trễ, currentScript null và URL lỗi đều được xử lý.
- `tests/dual-mode-sound-browser.py`: **9 nhóm đạt**. Đủ 19 launcher: đúng hai nốt tăng, hoàn thành 1,5s một lần trên từng đề 37/41/42/43 câu, restore im lặng. Desktop/touch Android và viewport/touch iPhone trong Chromium; Listening vẫn phát và không đổi src/time/volume/rate, muted giữ qua game/tab, pending không bị gán tiếng đúng/sai. OfflineAudioContext đo cao độ/envelope/gain, không chỉ đếm file. Chính sách autoplay mặc định, không dùng cờ bỏ qua chính sách.
- `tests/grade8-all-dual-browser.py`: **19 game / 793 câu đạt**, hai chế độ, nội dung, phương án, chấm/XP, audio, lưu/khôi phục/học sinh/mobile. Không lỗi JS/console, request ngoài hoặc tài nguyên hỏng.
- `node --test tests/dual-mode-progress.test.mjs tests/dual-mode-sound.test.mjs tests/grade8-all-dual.test.mjs`: **28 đạt**. `npm run test:prepare`: **41 đạt**. `npm run check:catalog`: **231 URL hợp lệ**, không trùng/thay đường dẫn.
- `tools/build-grade8-dual-games.py --verify`: dữ liệu và launcher được tái lập chính xác; HTML chỉ thêm bootstrap, không thay data. `tools/verify-truc-tuan-dual-source.py`: đủ 42 câu/2 đoạn đọc/2 transcript/hai MP3 khớp nguồn. `tests/dual-mode-browser.py`: **12 nhóm HTTP hồi quy đạt**, gồm preview chứa sound module, reset, tab conflict và storage bị chặn. `file://` bị Chromium policy chặn, ghi skipped.
- `tools/verify-firebase-recovery.py`, chuẩn bị `.site` cục bộ, kiểm tra YAML workflow và `git diff --check` đạt. Không deploy.

Không có lỗi Console/404 ở luồng thành công. Có **một 404 cố tình tiêm** trong fixture riêng để xác nhận error/retry; không bỏ qua lỗi mạng ngoài tình huống đó. Lượt đầu của fixture loading có lỗi import `re` trong HTTP range handler của bài kiểm thử; đã sửa import và chạy lại đạt, không phải lỗi MP3/ứng dụng.

Kiểm thử trên Chromium desktop và mô phỏng viewport/touch di động; chưa chạy binary Chrome/Edge hoặc điện thoại thật. Không tuyên bố kiểm thử public/Safari/loa thiết bị thật. Xem [verification.json](verification.json) và [danh sách file](changed-files.txt).

## 6. Pull Request và xuất bản

1. Duyệt PR nhánh `fix/grade8-shared-sound-loading`, kiểm tra CI; chưa có xác minh CI từ GitHub trong môi trường này.
2. Merge khi đồng ý, sau đó chạy Actions **Publish reviewed library to GitHub Pages (manual only)** trên `main`, nhập **DEPLOY HT ENGLISH LIBRARY** theo workflow hiện có. Merge riêng lẻ không tự kích hoạt workflow này.
3. Sau khi deploy thành công, mở Trực Tuấn trước rồi các game trong bảng. Kiểm tra HTML có `?v=20261026-sound-fix`, một nút âm thanh; Network engine/module/CSS 200, trạng thái ready; kiểm tra đúng/sai/hoàn thành và Listening. Chạy lại audit `--public` ở môi trường truy cập được Pages để đối chiếu SHA256 với main và header cache.
4. Nếu Pages vẫn phục vụ HTML/JS cũ, kiểm tra commit của lần deploy và cache thực tế trước khi sửa mã tiếp. Không reset Firebase, nhập lại catalog hoặc đổi Rules cho bản sửa này.

Tác vụ này chưa merge/deploy và chưa xác nhận sửa đã xuất hiện trên website công khai. Không cần thao tác Admin xuất bản danh mục vì tất cả href được giữ nguyên.
