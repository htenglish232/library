# Hiệu ứng âm thanh game hai chế độ lớp 8

Nhánh `feature/grade8-dual-game-sounds`, từ main `b38d578` (PR #36). Dùng chung cho cả 19 game. Chưa merge/deploy, không đọc/ghi Firebase production.

## Hành vi

- Khi kiểm tra một đáp án mới, đúng phát hai nốt sine tăng dần (523 → 784 Hz), khoảng **0,5 giây**; sai phát hai nốt trầm giảm dần (262 → 196 Hz), khoảng **0,4 giây**. Một lần kiểm tra mới khi ôn sai cũng có phản hồi, nhưng không đổi XP/kết quả lần đầu.
- Khi lần kiểm tra đó đưa số câu đã kiểm tra từ chưa đủ lên đủ toàn đề, phát thêm giai điệu **1,5 giây** sau phản hồi đúng/sai. Câu chờ giáo viên không phát đúng/sai; nếu là câu cuối thì chỉ có giai điệu hoàn thành. Điều kiện lấy từ progress hiện hành, không cần thêm cờ hay schema mới.
- Không phát khi mở trang, khôi phục bài, đổi chế độ, mở kết quả, xem câu cũ hoặc bấm lặp nút đã khóa. Không phát chúc mừng lại lúc ôn hoặc tải lại bài đã hoàn thành. Reset xác nhận bắt đầu bài mới có thể nhận giai điệu sau khi hoàn thành bài mới đó.
- Nút **Âm thanh: Bật/Tắt** nằm ở đầu game, dùng được từ trang chào; hỗ trợ bàn phím và touch, có `aria-pressed`, vùng nhấn tối thiểu 44px. Ghi nhớ chung cho game lớp 8 tại `htenglish:grade8:sound:v1`, chỉ giá trị `on/off`. Đồng bộ giữa các tab. Không sửa hoặc xóa khóa tiến độ/tên/mã học sinh. Nếu localStorage bị chặn, nút vẫn dùng trong phiên đang mở.
- Mặc định bật, nhưng không tạo AudioContext/phát tiếng cho đến một thao tác **Kiểm tra đáp án** thật (`event.isTrusted`). Tạo context và gọi `resume()` ngay trong thao tác đó; hỗ trợ `AudioContext`/`webkitAudioContext` và trạng thái suspended/interrupted. Không tự resume khi tải trang/đổi tab. Lỗi quyền âm thanh/thiết bị không chặn chấm hay lưu bài.
- Dùng sóng sine và đường tăng/giảm âm lượng mềm, peak gain **0,06**, giảm còn **0,025** khi Listening đang phát. Context hiệu ứng độc lập, không lấy quyền điều khiển, đổi src/time/volume/rate, pause hay đóng audio Listening. Không thêm MP3, CDN, thư viện hoặc request ngoài cho hiệu ứng.
- Mỗi phản hồi mới thay thế hiệu ứng trước để không chồng nhiều tiếng. Tắt tiếng, đổi học sinh, reset, đổi chế độ, xung đột tab hoặc ẩn/đóng trang hủy các nốt đang chờ. Một lần resume bị chặn/quá chậm (>500ms) không phát lại đáp án cũ sau đó. Chuyển trang và chế độ không tạo hiệu ứng mới.

## Các file thay đổi

| File | Nội dung |
|---|---|
| `grade-8/De_thi_GHK1/shared-practice/dual-sound.js` | Module ES dùng chung: oscillator/gain, nốt nhạc, resume theo thao tác, mute/persistence, hủy lịch, xử lý lỗi. |
| `grade-8/De_thi_GHK1/shared-practice/dual-mode-engine.js` | Nạp module tương đối từ URL script, thêm nút chung, chỉ gọi sound sau khi `P.check` thực sự thành công; phát hoàn thành trên chuyển tiếp số câu đã làm. |
| `grade-8/De_thi_GHK1/shared-practice/dual-mode.css` | Nút âm thanh 44px; không đổi giao diện index. |
| `tools/build-dual-mode-preview.py` | Đóng gói thêm module trong bản xem thử tự chứa. |
| `tests/dual-mode-sound.test.mjs` | 10 kiểm thử module, quyền âm thanh, resume/cancel, mute/storage, gain và bảo toàn các file. |
| `tests/dual-mode-sound-browser.py` | Kiểm thử Web Audio thực, PCM offline, 19 launcher, desktop/touch, Listening, completion, pending và nhiều tab. |
| `tests/dual-mode-browser.py` | Đợi điều hướng reload hoàn tất trước khi nhập tên/tiếp tục trong tình huống xung đột tab; giữ nguyên kiểm tra 390 XP. Lượt đầu phát hiện race này, lượt chạy lại sau khi đồng bộ điều hướng đã đạt đầy đủ. |
| `.github/workflows/grade8-dual-mode-checks.yml` | Chạy kiểm thử âm thanh và lưu artifact; thêm nhánh kiểm thử. Không thêm/sửa workflow triển khai. |
| `docs/grade8-dual-sounds.md` | Báo cáo này. |
| `docs/grade8-dual-sounds-report.json` | Kết quả đo/kiểm thử và giới hạn xác minh. |

Module nạp từ `document.currentScript.src`, nên cả 19 launcher hiện có dùng ngay mà không cần sao chép code/thay HTML riêng. Bộ kiểm tra byte so với main `b38d578` giữ nguyên **index, admin, catalog, Firebase, các lớp khác, toàn bộ HTML đề/game, dữ liệu/câu hỏi/đáp án, MP3, model chấm, dual-progress và dual-store**. Chỉ engine/CSS hai chế độ được chỉnh trong các tài nguyên đang có. Không thay namespace, contentVersion hoặc tính XP.

## Kiểm thử đã thực sự chạy

- `node --test tests/dual-mode-sound.test.mjs`: **10 đạt**. Bao gồm chưa có thao tác thì không tạo context, lời gọi không trusted/pending im lặng, hai giai điệu và gain, fanfare, resume đồng bộ trong gesture, hủy âm thanh sau mute/background/timeout, quyền bị từ chối, storage bị chặn, context không hỗ trợ và fallback webkit.
- `tests/dual-mode-sound-browser.py`: **9 nhóm đạt**. Cả 19 trang tải cùng module dưới `/library/`; click đúng/sai thực tạo oscillator qua AudioContext của Chromium với **chính sách autoplay mặc định, không bật cờ bỏ qua chính sách**. Kiểm tra desktop 1280px, touch Android 390px và viewport/user-agent/touch iPhone 375px trong Chromium. Nút không tràn ngang ở 360/390/768/1280px. Kiểm tra bật/tắt qua reload/game/tab, kết quả cũ không phát, completion chỉ một lần, ôn không tăng XP, pending không bị gán đúng/sai và thiếu Web Audio không làm hỏng game.
- Listening được phát thật trong khi kiểm tra đúng/sai/tắt hiệu ứng. Xác nhận currentTime vẫn tăng, không bị pause hoặc gọi lại play/load bởi hiệu ứng; gain hiệu ứng giảm khi đang nghe. Không chỉnh audio volume/rate/src.
- **OfflineAudioContext** chạy qua chính module sản xuất để kết xuất PCM và đo cao độ/RMS: đúng **0,5s**, sai **0,4s**, hoàn thành **1,5s**, peak đo được **0,06**, đuôi im lặng. Đây là đo tín hiệu số, không phải đánh giá âm lượng trên loa thực.
- `node --test tests/dual-mode-progress.test.mjs tests/dual-mode-sound.test.mjs tests/grade8-all-dual.test.mjs`: **28 đạt**. `npm run test:prepare`: **41 đạt**. `npm run check:catalog`: **231 đường dẫn** không trùng/tồn tại.
- `tests/grade8-all-dual-browser.py`: **19 game / 793 câu đạt**; cả hai chế độ, nội dung/đáp án nguồn, XP, tiến độ/học sinh, audio/mobile; không lỗi JS/console, request ngoài hoặc tài nguyên thiếu.
- `tests/dual-mode-browser.py`: hồi quy Trực Tuấn đủ **42 câu / 12 nhóm HTTP đạt**, kể cả storage bị chặn, tab xung đột, reset, touch và gói preview chứa module mới. `file://` vẫn bị chính sách Chromium chặn, ghi **skipped**, không báo đạt.
- `tools/build-grade8-dual-games.py --verify`: tái lập đủ 18 bộ dữ liệu/launcher mới, không thay đáp án/nội dung. `tools/verify-firebase-recovery.py`, chuẩn bị artifact bằng `tools/prepare-site.mjs` và phân tích YAML workflow đạt. Artifact chỉ tạo cục bộ, không deploy.

Xem [số đo và kết quả JSON](grade8-dual-sounds-report.json). Ảnh desktop/touch và số đo waveform được lưu trong artifact kiểm thử âm thanh của CI.

## Giới hạn và phát hành

**Chưa kiểm tra trên loa/thiết bị điện thoại thật, binary Chrome/Edge, Safari hay iOS thật.** Các profile điện thoại là mô phỏng touch/viewport trong Chromium, không phải Safari. Đã thử cài WebKit, kể cả chạy với quyền mở rộng; các máy chủ tải trả **403 Domain forbidden**, nên không tuyên bố WebKit/Safari đã đạt. Mã xử lý chuẩn Web Audio, trusted gesture, suspended/interrupted và webkit fallback có kiểm thử, nhưng chính sách/âm lượng trên thiết bị thật vẫn cần xác nhận sau khi có môi trường phù hợp. Chưa xác minh CI GitHub hoặc bản website production.

Sau khi duyệt/merge và chạy quy trình Pages thủ công hiện có, nút âm thanh sẽ có trên 19 game. Không cần cập nhật Firebase, xuất bản lại catalog hoặc nhập thêm liên kết để bật tính năng này. Không tự merge/deploy trong tác vụ này.
