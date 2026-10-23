# Phân tích đề gốc — THCS Trực Tuấn lớp 8

Nguồn: hai HTML và hai MP3 cùng thư mục. Hai HTML có nội dung byte giống nhau. Không ghép hai bản thành 84 câu. Bộ dữ liệu gồm 42 ID duy nhất q1–q42.

| Phần | Câu | Dạng bài |
| --- | --- | --- |
| Listening Challenge | q1–q6 | 6 câu A/B/C/D, bài nghe 1 |
| Listening Challenge | q7–q12 | 6 câu True/False, bài nghe 2 |
| Grammar Battle | q13–q22 | 10 câu A/B/C/D, gồm phát âm, trọng âm, từ vựng, giao tiếp, ngữ pháp |
| Grammar Battle | q23–q25 | 3 câu chia động từ |
| Reading Quest | q26–q30 | 5 chỗ trống trong đoạn leo núi |
| Reading Quest | q31–q33 | 3 câu trả lời mở về MY VILLAGE |
| Reading Quest | q34–q35 | 2 câu A/B/C/D về MY VILLAGE |
| Sentence Builder | q36–q38 | 3 câu ghép thẻ từ |
| Sentence Builder | q39–q42 | 4 câu viết lại, nhập phần còn lại sau mũi tên |

Tổng: 29 câu chọn (23 A/B/C/D, 6 True/False), 10 câu nhập, 3 câu ghép. Có đầy đủ 42 đáp án, 42 lời giải, 42 ghi chú, 2 đoạn đọc, 2 transcript có đánh dấu từ khóa, 3 bộ thẻ gốc. Các ID không trùng số thứ tự nội bộ của từng phần; game dùng ID q1–q42 để không nhầm câu.

Audio giữ nguyên tên, kể cả dấu cách trước `.mp3` của bài 2:

- `GHK1 K8 - part 1.mp3`
- `GHK1 K8 - part 2 .mp3`

## Các điểm cần giáo viên xác nhận

1. **q12:** HTML chấm F, ghi chú nói đáp án Word là T. Transcript trong HTML có “strong”, nhận định là “light”. Giữ F theo HTML; chưa có Word và chưa xác minh thủ công nội dung MP3 để khẳng định đáp án Word đúng/sai.
2. **q13:** Giữ B, phần gạch chân và giải thích phiên âm của HTML. Nguyên âm không nhấn trong “activity” có biến thể theo giọng/từ điển. Giáo viên chọn chuẩn phát âm dùng để chấm.
3. **q19:** Nguồn viết “lunch tonight”; nghĩa bữa trưa/tối chưa nhất quán. Đáp án B được giữ, nhưng C “That’s great. Thanks” cũng có thể đáp lời mời trong ngữ cảnh. Không sửa câu hỏi hay loại phương án C.
4. **q29:** Nguồn chọn D “keep”. A “stay” cũng tạo “stay fit” đúng nghĩa trong đoạn văn. Game đánh dấu để giáo viên xem lại, không tự đổi đáp án.
5. **q40:** HTML dùng yours / your bike và ghi chú Word dùng his. Chưa có Word; giữ các cách viết được nêu trong HTML, không chấp nhận tự động his.
6. **Tự luận q31–q33, q39–q42:** nguồn chấm bằng từ khóa con, có thể nhận sai câu thiếu ý hoặc đảo nghĩa (ví dụ q31 chỉ có một hoạt động, q33 “not yes”). Game giữ nguyên toàn bộ trường nguồn để đối chiếu, nhưng chỉ tự nhận đáp án mẫu/cách viết được nêu rõ, không suy diễn đáp án mới. Câu khác mẫu hiện “chưa khớp”, cần giáo viên xem lại, không tuyên bố mọi cách diễn đạt khác đều sai. Không tạo điểm kiểm tra chính thức.

## Bảo toàn dữ liệu

`source-data.js` được tái tạo bằng `tools/extract-truc-tuan-game.py`: DOMParser chỉ phân tích HTML, không chạy ứng dụng gốc; hai object literal được đọc riêng bằng Node VM có timeout. Thẻ gạch chân ngữ âm và đánh dấu transcript được giữ; bỏ class giao diện/các nút phát âm để phù hợp giao diện mới. Không đổi nội dung chữ.

`learning-notes.js` chứa bản dịch tiếng Việt, lỗi thường gặp và lưu ý giáo viên bổ sung, tách khỏi dữ liệu nguồn. Không thêm tình tiết bài nghe. Công thức/ghi chú và lời giải gốc luôn có trong màn hình phản hồi.

`sourceFiles` ghi SHA-256 của cả bốn file gốc. Kiểm thử so lại hash và trích xuất lại toàn bộ để phát hiện mất câu, đổi đáp án, phương án, thẻ từ, transcript hoặc đoạn đọc.

## Thứ tự triển khai

1. Trích xuất/đối chiếu dữ liệu và lập báo cáo này.
2. Bản 5 câu thật: q1 (nghe), q16 (ngữ pháp), q23 (nhập), q26 (đọc), q36 (ghép).
3. Chỉ sau khi kiểm thử trình duyệt bản 5 câu đạt mới bật đủ 42 câu. Giữ `?pilot=1` để tái kiểm tra bản nhỏ.

Các kết quả kiểm thử và hướng dẫn triển khai được ghi trong `README.md` khi hoàn tất.
