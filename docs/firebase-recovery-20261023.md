# Khôi phục tích hợp Firebase — 23/10/2026

## Xác định nguyên nhân

Main `ff64f80` không có `assets/firebase-config.js`, mã đăng nhập/phiên, `admin.html`, catalog exports, `firestore.rules`, `.firebaserc`, cấu hình, công cụ và workflow Firebase. `index.html` lại chứa DATA trực tiếp thay vì cổng đăng nhập. Lần fetch trước đó ghi nhận main bị force-update từ lịch sử có Firebase về `75096f7`, thuộc lịch sử trước lần tích hợp Firebase. Việc này đã xảy ra trước PR #30 sửa audio Trực Hùng; PR #30 không xóa các file Firebase.

Đây là bằng chứng mất **tích hợp trong mã nguồn**. Chưa có bằng chứng dự án `ht-english-library`, tài khoản Authentication hay dữ liệu Firestore bị xóa. Chạy lại công cụ kiểm tra chỉ đọc `firebase-preflight.mjs` không lấy được quyền xác thực Google; không thu được bản sao hay kết luận nào về dữ liệu production. Không in, sao chép hoặc thay khóa/mật khẩu.

## Bản khôi phục

Nhánh `restore/firebase-integration-20261023`, bắt đầu từ main `ff64f80`, khôi phục chọn lọc các file thiếu từ `7cfca10`. Giữ nguyên Project ID, cấu hình ứng dụng, Admin UID, logic phân quyền, Rules và export v1 201 mục. Không tạo dự án/tài khoản mới, không import/reset database hoặc publish Rules.

- Nối lại index với đăng nhập, xác minh quyền và trang Admin. Trước đăng nhập, tài khoản bị khóa/thu hồi/chưa cấp quyền và sau đăng xuất đều không hiện tài liệu.
- 321/321 file đang có trên main ngoài index giữ nguyên byte. Bao gồm mọi đề, audio, game Trực Hùng vừa khôi phục và hai file `Part 1.mp3`/`Part 2.mp3`. Không rollback hay force-push main.
- Danh mục main trước khôi phục có 202 liên kết. Khôi phục 10 liên kết đã mất trong lịch sử để đủ 212: sáu bài ngữ pháp lớp 5 Unit 13–18, IELTS Writing, ba game Trực Tuấn/Trực Khang/Trực Chính. Sáu file ngữ pháp vẫn tồn tại; bốn HTML IELTS/game cùng tài nguyên thiếu được khôi phục. Không ghi đè file hiện có.
- Catalog tiếp tục nhận dữ liệu từ Firebase và ghép các đợt bổ sung đã có. Giữ trạng thái ẩn, tiêu đề/thứ tự sửa bởi Admin, lịch sử và `releaseApplied`; không tự tạo lại mục đã xóa sau khi tiếp nhận đợt bổ sung. Không nhập lại danh mục 201 mục vào tài liệu đang tồn tại.

## Kiểm chứng

- `npm run build`: dựng SDK cục bộ thành công.
- `npm run check:catalog`: đủ 212 URL, không trùng, tồn tại trên đĩa; giữ các đường dẫn hiện có.
- `npm run test:prepare`: 26 kiểm thử đạt.
- `tools/verify-firebase-recovery.py`: 321 file main giữ nguyên; cấu hình/Rules/Admin/legacy catalog khớp SHA-256 tin cậy; bản nghe mới còn nguyên.
- Firebase Auth/Firestore Emulator: 18 kiểm thử Rules và 23 kịch bản Chromium đạt. Bao gồm đăng nhập, chặn tài khoản không có quyền, quyền Admin/giáo viên, cấp/khóa/thu hồi quyền, quản lý danh mục, sao lưu/lịch sử/lưu đồng thời, xóa sau tiếp nhận release, mở cả ba game từ index và đường dẫn `/library/`. Không gọi production.
- `node tools/prepare-site.mjs`: tạo `.site` cục bộ, không xuất bản. Artifact không chứa công cụ, dữ liệu sao lưu hoặc Rules.

Chạy lại với Node 24, Java 21, Python 3.12, Playwright 1.58 và Chromium. Cài dependencies bằng `npm ci`. Dùng `npm run test:emulators`; nếu tải Firestore Emulator bị chặn, công cụ `tools/test-emulators-official.py` dùng bản Google Cloud SDK chính thức đã kiểm tra checksum.

## Bước đưa trở lại web

1. Duyệt và merge nhánh khôi phục vào main. Không reset main về commit cũ.
2. Kiểm tra dự án [ht-english-library trong Firebase Console](https://console.firebase.google.com/project/ht-english-library/overview): Authentication và Firestore. Chưa xác minh dữ liệu thật từ môi trường này; không cần tạo dự án mới hay nhập lại dữ liệu chỉ vì mã nguồn mất cấu hình.
3. Triển khai website bằng workflow thủ công hiện có sau khi merge. Không chạy deploy Rules chỉ để khôi phục giao diện; cấu hình/Rules trong PR giữ nguyên bản tin cậy. Nếu Rules thực tế khác, cần đọc và đối chiếu trước mọi thay đổi.
4. Nên bật Ruleset bảo vệ main trong GitHub, chặn force-push/xóa nhánh và yêu cầu Pull Request. Thay đổi hiện tại chưa tự sửa cài đặt repository.

Nhánh này chưa merge, chưa deploy, chưa thay đổi production. Khôi phục giao diện không thay thế việc xác minh dữ liệu thật trong Console.
