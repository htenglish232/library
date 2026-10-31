# Student Portal — tạo staging và cấp quyền an toàn

## Trạng thái bàn giao

Mã nguồn ở nhánh feature/student-portal-phase1. Cấu hình mới độc lập với Firebase production ht-english-library và GitHub Pages. Theo chỉ dẫn bổ sung của chủ dự án, chỉ triển khai/test Emulator trong phiên này; chưa bật Blaze hoặc dịch vụ trả phí.

Tên dự kiến: project ht-english-student-staging; Hosting site ht-english-student-staging; Firestore và Functions asia-southeast1 (Singapore). Chưa xác nhận tên còn khả dụng hoặc project đã tồn tại: Firebase CLI hiện báo chưa xác thực, môi trường không có Google Cloud connection sẵn sàng. Nếu Console báo tên không dùng được, dừng và thống nhất tên mới để cập nhật các guard/config; không dùng production thay thế.

Đây là runbook cho quản trị viên. Các lệnh thay đổi cloud bên dưới chưa được thực thi. Không gửi mật khẩu, access token hoặc service-account key trong chat.

## 1. Tạo project riêng trên Firebase Console

1. Đăng nhập https://console.firebase.google.com/ bằng tài khoản quản trị của bạn. Chọn tạo project mới, không chọn ht-english-library.
2. Đặt tên hiển thị “HT English Student Staging”; kiểm tra Project ID chính xác ht-english-student-staging. Kiểm tra tính khả dụng khi tạo. Có thể tắt Analytics cho bản demo.
3. Bắt đầu với Spark. Không liên kết billing hoặc nâng Blaze trong giai đoạn này.
4. Mở Authentication → Sign-in method → bật Email/Password. Chưa cần email link, SMS hoặc đăng ký qua UI. Tài khoản Portal chỉ được cấp quyền khi có principal/profile server tương ứng.
5. Mở Firestore Database → Create database, chọn Standard/default database và location asia-southeast1 nếu Console hỗ trợ. Chọn chế độ khóa mặc định/production mode; không mở test mode public. Location không đổi được tùy ý sau khi tạo, hãy đối chiếu trước khi xác nhận.
6. Project settings → Your apps → đăng ký Web App “HT English Student Portal Staging”. Lấy Firebase Web configuration công khai. Không tạo/download service-account JSON.
7. Trong Hosting, tạo site riêng ht-english-student-staging khi tên còn khả dụng. Việc có project ID không tự chứng minh site ID còn trống. Không chọn site bất kỳ của project production.
8. Kiểm tra Authentication authorized domains có hostname Hosting staging thực tế; chỉ thêm hostname đã xác nhận. Không đổi domains/password policy của production.

Bạn có thể thực hiện các bước Console trên trước. Chưa có backend public trên Spark của kiến trúc này. Muốn có link chạy trọn vẹn đăng nhập → nộp bài → tính lại điểm → thưởng sao, cần phê duyệt billing cho backend trước bước 3 dưới đây.

## 2. Cấp quyền triển khai

Ưu tiên kết nối Google Cloud của môi trường bằng cơ chế OAuth/Workload Identity, hoặc quản trị viên tự đăng nhập Firebase CLI trên máy riêng:

```sh
firebase login
firebase projects:list
```

Nếu CLI yêu cầu đăng nhập/đồng ý OAuth, quản trị viên hoàn tất trong trình duyệt của mình. Không dán kết quả token vào chat, không dùng firebase login:ci để bàn giao token lâu dài. Trong môi trường cloud, dùng phần Connections/identities để cấp một danh tính có quyền đúng project staging nếu sản phẩm hỗ trợ.

Tách ba vai trò:

- Deployer: quyền Hosting deploy, Functions deploy và sử dụng runtime service account trong staging. Có thể bắt đầu từ Firebase Hosting Admin + Cloud Functions Developer + Service Account User giới hạn đúng runtime account; việc đặt public HTTP invoker cho Functions gen2 cần quyền Cloud Run IAM tương ứng. Người quản trị xét quyền bổ sung mà CLI thực sự yêu cầu; không cấp Owner cho tiện.
- Runtime backend: quyền đọc/ghi Firestore staging và đọc trạng thái Firebase Auth users để verify token/revocation. Không cần quyền tạo/xóa project, sửa billing hoặc quản trị Hosting. Nên dùng service account riêng, chọn qua cấu hình Functions sau khi tên account được xác nhận.
- Người tạo tài khoản demo: Firebase Authentication Admin và quyền Firestore cần thiết, dùng ADC/Workload Identity trên máy tin cậy. Không đưa credential của vai trò này vào browser hay runtime nếu không cần.

Quản trị viên bật các API cần thiết cho Functions gen2/Cloud Run/Cloud Build/Artifact Registry trong staging chỉ sau khi phê duyệt billing. Ghi lại IAM và service account được dùng. Không tự cấp quyền trên ht-english-library.

## 3. Quyết định billing riêng trước backend

Cloud Functions deploy của phương án này cần billing phù hợp, thông thường là Blaze. Hiện CHƯA có phê duyệt nâng gói; dừng trước bước này cho đến khi bạn đồng ý rõ ràng. Không tự liên kết phương thức thanh toán.

Trước khi duyệt: đối chiếu bảng giá Firebase/Google Cloud tại ngày triển khai; cấu hình budget alerts; kiểm tra region. maxInstances=2 và minInstances=0 đã đặt trong backend, nhưng không phải hard cap chi phí. Log, build images, mạng và lưu trữ vẫn có thể tính phí. Không thay backend tin cậy bằng ghi điểm/sao từ client để tránh Blaze.

Ước lượng pilot: 3 tài khoản × 20 lượt tối đa cho mỗi assignment; mỗi lượt vài document reads/writes, không ghi từng click. Artifact khoảng 5 MiB ở lần build kiểm tra, thư mục game/audio pilot khoảng 2,6 MiB; băng thông tải lại và bộ nhớ cache quyết định chi phí mạng. Free quota không đồng nghĩa mọi dịch vụ đều miễn phí. Chưa có region billing/traffic thật nên không đưa cam kết tiền cố định.

## 4. Chuẩn bị build staging sau khi đủ quyền

Node 22 cho backend; Java 21; Python 3.12 và Playwright 1.58 cho kiểm thử.

```sh
git switch feature/student-portal-phase1
npm ci
npm ci --prefix student-portal/functions
```

Sao chép student-portal/staging-config.example.json ra một vị trí riêng ngoài checkout, điền Web App configuration công khai của đúng staging. Giữ emulator=false. Các trường API key/appId Web là cấu hình công khai, không phải Admin key.

```sh
node tools/build-student-portal.mjs --config /DUONG_DAN_RIENG/staging-web.json
```

Build từ chối project production và yêu cầu ID staging đã chốt. Artifact ở student-portal/dist; server grader được copy vào functions/generated từ đúng source gốc, có kiểm tra hash. Không dùng artifact --emulator cho deploy.

Backend mặc định khóa nhận bài trừ khi PORTAL_ENABLED=true. Sau khi sẵn sàng pilot, tạo tệp riêng không commit:

```text
student-portal/functions/.env.ht-english-student-staging
PORTAL_ENABLED=true
```

Để tạm dừng nhận bài về sau, đặt false và deploy riêng Functions staging. Dashboard/lịch sử vẫn đọc được nếu backend đang hoạt động. Không dùng .env.local để cấu hình deployment; runner chỉ tạo/xóa tệp đó cho Emulator.

## 5. Kiểm tra và deploy khi đã có phê duyệt billing/quyền

Chạy lại Emulator theo docs/student-portal-implementation.md. Đối chiếu test report với commit sẽ deploy, project và site trong firebase.student-portal.json. Sao lưu Rules/indexes và dữ liệu staging hiện có trước khi cập nhật.

Các lệnh sau chỉ dành cho người đã được cấp quyền:

```sh
firebase projects:list
firebase hosting:sites:list --project ht-english-student-staging
firebase deploy --config firebase.student-portal.json --project ht-english-student-staging --only firestore:rules,firestore:indexes,functions:student-portal,hosting
```

Config này có Hosting site cố định, Functions codebase riêng và Rules riêng. .firebaserc gốc không cần đổi. Không chạy firebase deploy thiếu --config/--project; không deploy root firebase.json; không gọi workflow Pages; không merge main.

Nếu CLI thiếu OAuth, IAM, API hoặc billing: dừng ngay ở bước lỗi, lưu thông báo không chứa bí mật và nhờ quản trị viên hoàn tất. Không tự bật Blaze, thêm quyền rộng hoặc dùng production để thử.

Sau deploy, lấy URL từ CLI/Console và kiểm tra HTTP thật: trang chủ 200, /api/health trả đúng service, đăng nhập demo, nộp bài, đổi tài khoản và thử sửa stars bị chặn. Chỉ công bố URL sau khi các bước này đạt. Báo cáo hiện tại không chứa URL public đã xác minh.

## 6. Tạo đúng ba tài khoản demo và bàn giao mật khẩu

Chỉ thực hiện sau khi staging được xác nhận. ID: HT0001, HT0002, HT0003; tên Demo A/B/C; Grade 8. Mỗi tài khoản có mật khẩu CSPRNG 18 byte, không gửi ra log.

Quản trị viên tạo khóa bàn giao trên máy riêng, giữ private key tại máy mình:

```sh
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:3072 -out /DUONG_DAN_RIENG/portal-private.pem
chmod 600 /DUONG_DAN_RIENG/portal-private.pem
openssl pkey -in /DUONG_DAN_RIENG/portal-private.pem -pubout -out /DUONG_DAN_RIENG/portal-public.pem
```

Chỉ chuyển public key cho người chạy provisioning bằng kênh phù hợp. Dùng ADC/Workload Identity cho Admin SDK; nếu cần ADC local, quản trị viên chạy gcloud auth application-default login trên máy riêng. Không đọc/copy file ADC vào repository hoặc chat.

Dry-run không kết nối Firebase:

```sh
node tools/student-portal-admin.mjs --project ht-english-student-staging
```

Apply thực sự (chưa chạy trong bàn giao này):

```sh
node tools/student-portal-admin.mjs --project ht-english-student-staging --apply --confirmed-staging --recipient-public-key /DUONG_DAN_RIENG/portal-public.pem --out /DUONG_DAN_RIENG/demo-credentials.encrypted.json
```

Tệp output phải ở ngoài checkout, tạo mới với quyền 0600; mã hóa RSA-OAEP-SHA256 + AES-256-GCM. Công cụ lưu envelope sau mỗi tài khoản mới, để bảo toàn thông tin đã tạo nếu một bước tiếp theo thất bại. Retry không tự reset mật khẩu hoặc xóa tài khoản có sẵn. Nếu nguồn bị ngắt giữa Auth create và ghi envelope, cần quy trình reset có kiểm soát; không thể lấy lại plaintext từ Firebase.

Trên máy quản trị, giải mã ra tệp riêng bằng:

```sh
node tools/student-portal-decrypt.mjs --in /DUONG_DAN_RIENG/demo-credentials.encrypted.json --private-key /DUONG_DAN_RIENG/portal-private.pem --out /DUONG_DAN_RIENG/demo-credentials.json
```

Bàn giao qua kênh riêng được trung tâm chấp thuận, xóa tệp plaintext sau khi sử dụng; không gửi vào chat, commit hoặc CI artifact. Nếu import lại không có tài khoản mới, output là danh sách rỗng vì mật khẩu cũ không bị reset.

CSV/Excel: --csv student-portal/demo-students.csv hỗ trợ CSV UTF-8/quoted fields, dry-run trước apply, tối đa 100 dòng mỗi batch. Không có cột mật khẩu/quyền. Excel xuất CSV thay vì XLSX/macro. Import CSV tổng quát chỉ tạo hồ sơ; chỉ lệnh demo mặc định tự giao bài pilot. Chưa có màn hình quản trị giao bài hàng loạt.

## 7. Cách trải nghiệm khi URL đã được xác minh

- Mở hostname Hosting staging thực tế, nhập một Student ID và mật khẩu từ bàn giao riêng.
- Link giáo viên: thêm /?assignment=truc-tuan-grade8-demo vào hostname đã xác minh.
- Nhấn “Bắt đầu làm bài”, hoàn thành và “Nộp bài”. Backend tính lại điểm từ đáp án, lưu thời gian server và lịch sử.
- Hoàn thành đủ 42 câu nhận +5 sao đúng một lần cho assignment. Làm lại vẫn có lịch sử và điểm nhưng không thêm sao. Đây là chính sách completion của demo, không phải thưởng theo điểm thi.
- ID bài không cấp quyền; tài khoản khác lớp/không được giao không mở được qua API. Đăng xuất khi dùng thiết bị chung.

Không có mật khẩu demo hoặc URL staging đang chạy trong tài liệu này: hiện chỉ tài khoản Emulator tạm thời được tạo và đã xóa khi kiểm thử kết thúc.

## 8. Rollback và giữ nguyên hệ thống chính

1. Tạm dừng nhận bài/thưởng qua PORTAL_ENABLED=false trong Functions staging, deploy riêng codebase student-portal nếu đang có sự cố ghi.
2. Rollback đúng Hosting site staging bằng release cũ đã ghi nhận; redeploy Functions từ commit tương thích schema. Không rollback Pages hoặc Firebase production.
3. Giữ attempts/starTransactions đã chốt; không phục hồi stars từ snapshot cũ một cách mù quáng. Nếu cần điều chỉnh, công việc riêng phải có giao dịch bù/audit/idempotency.
4. Trước deploy ghi lại Rules/indexes source, commit, artifact hashes, Functions config/revision và Hosting release ID. Nếu staging đã có dữ liệu, dùng phương án backup được plan hỗ trợ và thử restore trên đích riêng.
5. Khóa đúng các UID portal của batch lỗi; không xóa hoặc reset tài khoản ngoài batch. Không có tài khoản thật trong scope.

Sau khi quản trị viên hoàn tất Console/quyền và quyết định billing, có thể tiếp tục deploy và kiểm chứng URL từ trạng thái mã đã bàn giao, không cần thay đổi project production.
