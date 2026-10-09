# Đăng nhập giáo viên — bản thử nghiệm

Nhánh: `trial/teacher-login`. Chưa đưa lên `main`, chưa thay đổi GitHub Pages đang chạy.

## Phương án

GitHub Pages chỉ phục vụ tệp tĩnh, không có máy chủ kiểm tra mật khẩu. Phương án đơn giản nhất là JavaScript ẩn danh mục ở `index.html` cho đến khi đăng nhập. Không cần dịch vụ trả phí hoặc cơ sở dữ liệu.

**Đây chỉ là lớp hạn chế truy cập, không phải bảo mật thực sự.** Người có kỹ thuật có thể đọc danh mục trong mã nguồn, sửa JavaScript hoặc trạng thái đăng nhập để vượt qua. Các bài tập và audio vẫn công khai. Băm mật khẩu giúp tránh lưu mật khẩu rõ nhưng giá trị băm công khai vẫn có thể bị dò ngoại tuyến. Nếu cần bảo mật thực sự, cần một máy chủ hoặc dịch vụ xác thực kết hợp kiểm soát truy cập nội dung; chỉ thêm Firebase/Auth0 vào giao diện cũng không bảo vệ các tệp công khai trên Pages.

Tài khoản được so sánh bằng PBKDF2-SHA-256, 600.000 vòng, salt ngẫu nhiên 16 byte. Mật khẩu không gửi qua mạng, không ghi vào localStorage và không có mật khẩu mặc định. Dùng mật khẩu riêng, dài, không dùng lại mật khẩu quan trọng.

## Các thao tác bạn cần làm

1. Khi nhánh thử nghiệm đã có trên GitHub, chọn nhánh `trial/teacher-login`, bấm **Code → Download ZIP**, giải nén. Mở `teacher-access/create-account.html` bằng Chrome, Edge, Firefox hoặc Safari mới. Giữ các tệp đi kèm trong ZIP để công cụ hoạt động.
2. Nhập tên tài khoản và mật khẩu riêng (ít nhất 12 ký tự), nhập lại mật khẩu. Bấm **Tạo tệp tài khoản**, rồi **Tải teacher-accounts.json**. Không gửi mật khẩu qua chat.
3. Trên GitHub, vẫn chọn nhánh thử nghiệm. Mở thư mục `teacher-access`, chọn **Add file → Upload files**, tải tệp `teacher-accounts.json` mới để thay tệp cùng tên. Chọn commit vào nhánh thử nghiệm; không chọn `main`. Bạn cũng có thể gửi lại tệp JSON cho tôi cập nhật nhánh thử nghiệm; tệp không chứa mật khẩu rõ nhưng vẫn nên coi là thông tin cấu hình nhạy cảm với mật khẩu yếu.
4. Thử đăng nhập đúng/sai, đóng rồi mở lại trang, đăng xuất và mở một link bài tập trực tiếp. Xác nhận khi muốn đưa lên `main`; lúc đó mới hợp nhất nhánh và để GitHub Pages xuất bản.

GitHub Pages hiện tại không tự có một website xem trước riêng cho nhánh thử nghiệm. Không đổi nguồn Pages sang nhánh thử nghiệm vì việc đó sẽ thay website đang dùng. Có thể thử bản ZIP bằng máy chủ cục bộ như dưới đây, hoặc yêu cầu tôi hỗ trợ kiểm tra bản thử nghiệm trong môi trường cloud. Không mở trực tiếp `index.html` bằng `file://`: trình duyệt có thể chặn tải cấu hình JSON.

Để thêm giáo viên, chọn tệp `teacher-accounts.json` hiện có trong công cụ trước khi tạo; tệp tải xuống sẽ giữ các tài khoản khác. Tạo lại cùng tên để đổi mật khẩu; ID tài khoản mới làm phiên cũ không còn hợp lệ khi tải lại trang. Xóa tài khoản bằng cách bỏ mục tương ứng trong tệp JSON. Nếu không chọn tệp cũ, tệp mới chỉ chứa tài khoản vừa tạo.

## Hoạt động

- Chỉ trang danh mục có màn hình đăng nhập. Toàn bộ thư mục Grade 4–8, nội dung đề, audio, đường dẫn, bộ chấm điểm và `home-button.js` giữ nguyên.
- Ghi nhớ trên cùng trình duyệt trong đúng 30 ngày kể từ lần đăng nhập, không kéo dài thời hạn mỗi lần truy cập. Trình duyệt xóa dữ liệu, chế độ riêng tư hoặc cấm lưu trữ có thể làm mất phiên sớm hơn. Nếu cấm localStorage, hiển thị thông báo chỉ dùng phiên tạm thời.
- Hết hạn được kiểm tra khi tải trang, quay lại tab, lấy lại focus và định kỳ. Đăng xuất xóa phiên, ẩn thư viện ngay và đồng bộ các tab cùng website. Phiên này không phải token bảo mật.
- Giao diện thư viện cũ được giữ, thêm nút đăng xuất. Chỉ màn hình đăng nhập và công cụ tạo tài khoản dùng Noto Sans từ các tệp phông đã có trong repository (giấy phép OFL đi kèm).
- Cấu hình rỗng hoặc hỏng không mở danh mục. Bản thử nghiệm để `accounts: []` cho đến khi người quản lý tự tạo tài khoản.

## Chạy và kiểm tra kỹ thuật

Website tĩnh, không cần build hay cài dependency để chạy. Từ thư mục repository:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Kiểm tra đăng nhập bằng Python Playwright và Chromium đã có trong môi trường cloud:

```sh
python3 tests/teacher_login_checks.py
```

Bộ kiểm tra dùng tài khoản tạm thời do test tạo và chèn vào phản hồi HTTP trong trình duyệt; không ghi mật khẩu hoặc tài khoản thử vào cấu hình thật. Kiểm tra đường dẫn project Pages `/library/`, đăng nhập đúng/sai, nhớ phiên, hết hạn 30 ngày, phiên hỏng, đăng xuất nhiều tab, thiếu cấu hình, trình duyệt cấm lưu trữ, công cụ tạo tài khoản, giao diện máy tính và các kích thước màn hình điện thoại. Đây là kiểm tra trình duyệt giả lập, chưa phải kiểm tra trên điện thoại vật lý.

Cloud task đã được cách ly: sử dụng checkout hiện có, không tạo Git worktree trừ khi người dùng yêu cầu. Không sửa đề hoặc cài package vào checkout để thử đăng nhập.

## Kết quả kiểm tra bản thử nghiệm

- 20 nhóm kiểm tra trình duyệt đăng nhập đã đạt, gồm giao diện desktop và 5 kích thước mobile/tablet, thời hạn đúng 30 ngày, phiên hỏng, đăng xuất nhiều tab, trường hợp chặn lưu trữ và tài khoản tạo bằng công cụ.
- Toàn bộ 201 đường dẫn trong danh mục trả HTTP 200. Script tạo danh mục giữ nguyên từng ký tự. Đề Grade 7 đại diện mở trực tiếp, nộp và hiển thị phản hồi mà không cần đăng nhập.
- Công cụ tạo tài khoản đã chạy qua HTTP, tạo tệp tải xuống và đăng nhập thành công bằng cấu hình được tạo. Kiểm tra mở bằng `file://` từ ZIP bị bỏ qua vì chính sách quản trị của Chromium trong cloud chặn URL tệp; chưa xác minh thao tác này trên máy cá nhân. Nếu trình duyệt của bạn chặn mở tệp cục bộ, cần thử qua máy chủ HTTP/HTTPS hoặc nhờ hỗ trợ, không tắt cơ chế bảo vệ của trình duyệt.
- Chưa thử trên điện thoại vật lý hoặc GitHub Pages đang chạy.
- Bộ kiểm tra chấm toàn bộ Grade 7 có sẵn (`browser_checks.py --grading-only`) dừng tại `d2_1`: test tìm Word Chips, nhưng giao diện đề hiện tại dùng ô nhập cho câu `rewrite-card`, dù dữ liệu câu vẫn ghi `kind: chips`. Đây là sự không khớp có sẵn giữa test và UI; không sửa đề, mã chấm hoặc bộ test đó trong thay đổi đăng nhập. Không tuyên bố toàn bộ bộ chấm đã đạt; chỉ kiểm tra nộp/phản hồi đại diện đã đạt.

Môi trường phát triển hiện tại đã chạy được website và bộ test đăng nhập. Hướng dẫn khởi động đã lưu vào `start_skill` của cấu hình cloud; không cần `install_script`. Lưu cấu hình cloud không xuất bản website hoặc hợp nhất nhánh GitHub. Muốn lưu môi trường cho tác vụ sau: xem và lưu thay đổi trong cài đặt môi trường, rồi Publish môi trường cloud.
