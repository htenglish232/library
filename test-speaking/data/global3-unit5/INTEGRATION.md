# Grade 3 – Global Success – Unit 5

Nguồn: `HT_English_Global_3_Unit_5_Speaking_Cards_His_Her.zip` do giáo viên cung cấp. Đã tích hợp vào Test Speaking tại `test-speaking/index.html`, với lối vào từ Library chính trên nhánh review. Catalog/game/Firebase cũ giữ nguyên. Chưa merge main hoặc triển khai production.

Giữ nguyên 14 ảnh PNG, JSON, CSV và README từ ZIP; SHA-256 và kích thước từng tệp được lưu trong `integrity.json`. Không tạo thêm câu hỏi, ảnh hoặc đáp án. Ảnh minh họa không chứa đáp án mẫu. Tệp `unit5_speaking_cards.json` giữ nguyên byte; adapter chỉ chuẩn hóa nhãn Grade/Unit, đường dẫn media và audio null trong bộ nhớ.

| Thẻ | Ảnh gốc | Nhóm |
| --- | --- | --- |
| 01–08 | `images/Speaking_Card_01.png` … `Speaking_Card_08.png` | Review |
| 09 | `images/Speaking_Card_09.png` | Extension |
| 10–14 | `images/Speaking_Card_10.png` … `Speaking_Card_14.png` | Unit 5 Core |

Câu hỏi/đáp án thẻ 09–14 giữ nguyên “What's his/her hobby?” và “He/She likes…” theo JSON. Không gán ảnh guitar của thẻ Extension cho nhóm Core hoặc tự bổ sung singing/walking/cooking. Các đáp án câu hỏi cá nhân là câu mẫu.

Trong Library chọn Test Speaking → Grade 3 → Global Success → Unit 5:

- **Practice**: đủ 14 thẻ; câu trả lời mẫu luôn hiện ngay dưới câu hỏi, kể cả khi chuyển câu; không có nút Reveal Answer. Ghi nhớ vị trí luyện tập trên thiết bị.
- **Sequential Test / Random Test**: chọn “Toàn bộ 14 thẻ” hoặc “Unit 5 Core · 5 thẻ”, rồi chọn Sequential hoặc Random. Không ghi âm, không tự chấm điểm và không tự hiện đáp án.
- **Random**: Fisher–Yates trên đúng phạm vi đã chọn. Không lặp thẻ mới trong lượt. Previous giữ nguyên thứ tự; Restart & Reshuffle giữ nguyên phạm vi 14/5 thẻ và tạo lượt mới.
- **Âm thanh**: bấm Listen to the question để đọc câu hỏi bằng SpeechSynthesis, ưu tiên English US/UK; không có MP3 trong gói nguồn. Không tự phát và không yêu cầu micro.
- **Ảnh**: giữ tỷ lệ, không crop; hình lớn và câu hỏi ở cạnh nhau trên desktop, câu hỏi ở trên ảnh trên điện thoại. Previous/Next cố định khi cuộn.

Các URL ảnh hoạt động cả ở `/test-speaking/` và dưới GitHub project Pages `/library/test-speaking/`. Đường dẫn gốc `images/...` được giải quyết thành `./data/global3-unit5/images/...` khi tải gói. Không cần nhập lại JSON thủ công; nếu xuất sao lưu từ ứng dụng thì đường dẫn đã được giải quyết sẵn.

Đã đạt 8 nhóm browser test riêng cho Unit 5: kiểm tra HTTP và byte của đủ 14 ảnh, đúng cặp ảnh/câu hỏi/đáp án, Practice, Sequential/Random trên cả hai phạm vi, giữ scope sau restart, sửa/xuất không mất category, bổ sung gói vào thư viện cục bộ cũ mà không đổi các bộ cũ, không yêu cầu micro. Đã kiểm tra bố cục 360/390/1440/1920 px. Ảnh và báo cáo ở `/tmp/ht-speaking-unit5/`.

SpeechSynthesis được kiểm tra lời gọi/ngôn ngữ bằng mock; cần nghe thử giọng thật và kiểm tra trình chiếu trên thiết bị lớp học. Chưa xác nhận chất lượng âm thanh trên thiết bị vật lý.
