# Kết quả kiểm tra nhánh Firebase thử nghiệm

Ngày kiểm tra: 09/10/2026. Nhánh: `firebase-auth-trial`.

Mã nguồn gốc để đối chiếu: `8c6361c8cd85831097f28419bcbdaa5b31601bfc`.

## Kết quả đã thực hiện

| Kiểm tra | Kết quả |
| --- | --- |
| Xây dựng Firebase SDK cục bộ | Đạt |
| Danh mục so với bản gốc | Đúng 201 đường dẫn riêng biệt; toàn bộ tiêu đề, cấu trúc và thứ tự dữ liệu khớp |
| File bài tập, audio, chấm điểm, home-button | Không thay đổi so với bản gốc |
| Kiểm tra tính toàn vẹn danh mục | 3 bài kiểm tra đạt; từ chối dữ liệu bị sửa, thiếu, trùng, đảo thứ tự hoặc sai mã kiểm tra |
| Firestore Security Rules | 10 bài kiểm tra đạt, không bỏ qua bài nào |
| Kiểm tra trình duyệt với Auth và Firestore Emulator | 12 tình huống đạt |
| Kiểm tra Authentication độc lập | 4 tình huống đạt |
| Giao diện đăng nhập và Admin trên mobile | Không tràn ngang ở 360/375/390/430 px |
| Website đóng gói `.site/` | Các file bài tập/audio giống bản gốc từng byte; không chứa file xuất danh mục hoặc công cụ quản trị cục bộ |

12 tình huống trình duyệt: chưa đăng nhập; sai mật khẩu; chưa được cấp quyền; quyền bị khóa; quyền bị thu hồi; tài khoản Authentication bị vô hiệu hóa; giáo viên hoạt động xem đúng 201 link theo thứ tự hiển thị gốc; giáo viên bị chặn khỏi trang Admin; Admin cấp/khóa/mở khóa/thu hồi và phiên giáo viên cập nhật; công cụ nhập từ chối bản bị đổi thứ tự và đọc lại xác minh bản đúng; đăng xuất xóa dữ liệu Admin; học sinh mở trực tiếp bài tập, nộp/chấm bài và tải audio.

Thứ tự dữ liệu lưu và thứ tự hiển thị được kiểm tra riêng. Trang gốc đã sắp xếp Unit theo số khi hiển thị; nhánh thử nghiệm giữ nguyên hành vi đó. Không chỉnh dữ liệu gốc để chạy theo một kỳ vọng kiểm thử mới.

## Công cụ và cách chạy

Firebase JS SDK 13.0.0, Firebase CLI 15.33.0, Rules Unit Testing 6.0.0, Firestore Emulator 1.22.0, Node.js 24, Java 21, Python Playwright và Chromium.

```sh
npm run build
npm run check:catalog
node --test tests/catalog.test.mjs
python3 tools/test-emulators-official.py
```

Lệnh Firebase CLI tải trực tiếp từ Google Storage ban đầu vẫn gặp proxy HTTP 403, kể cả sau khi người dùng cho biết đã thêm tên miền. Không xác nhận được chính sách mới đã có hiệu lực trên máy đang chạy. Vì vậy đã dùng bản Firestore Emulator cùng phiên bản trong Cloud SDK chính thức từ `dl.google.com`, kiểm tra SHA-256 của archive và JAR trước khi thực thi. Công cụ thay thế đã được chạy lại thành công, tự khởi động và dừng dịch vụ cục bộ. Không sửa checksum của Firebase CLI và không tắt xác minh TLS.

Thông báo `PERMISSION_DENIED` trong các bài kiểm tra quyền là kết quả mong đợi của thao tác bị chặn, không phải bài kiểm tra thất bại. Cảnh báo Emulator hub không liệt kê Firestore là dự kiến khi Firestore được chạy riêng bằng Cloud SDK.

## Những việc chưa thực hiện

- Chưa áp dụng `firestore.rules` lên `ht-english-library`.
- Chưa nhập danh mục hoặc sửa tài khoản/quyền trên Firebase thật. Danh mục chỉ được nhập vào Emulator.
- Chưa kiểm tra Rules, bộ sưu tập hoặc danh mục hiện có của dự án thật.
- Chưa kiểm tra tài khoản Admin thật; không yêu cầu hoặc sử dụng mật khẩu thật.
- Chưa triển khai, đổi nhánh GitHub Pages, merge vào main hoặc đẩy nhánh lên GitHub.
- Workflow GitHub Actions chỉ kiểm tra, không triển khai; chưa chạy trên GitHub.
- Chưa kiểm tra Safari/Firefox hoặc thiết bị điện thoại thật.

Hướng dẫn sử dụng, kiểm tra và quy trình cần xác nhận trước khi áp dụng thật nằm trong `HUONG_DAN_FIREBASE.md`. Trước khi thay Rules, phải kiểm tra/sao lưu Rules hiện tại và bảo đảm không ảnh hưởng ứng dụng khác. Trước khi nhập, kiểm tra/sao lưu `libraryCatalog/current` nếu đã tồn tại. Việc xuất bản GitHub Pages là một bước riêng, cần được cho phép riêng.
