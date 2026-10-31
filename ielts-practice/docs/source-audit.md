# Đối chiếu nguồn — IELTS Unit 2: Individuals and Families

Trạng thái học thuật: **giáo viên đã xác nhận giữ nguyên nguồn và giữ cả hai lưu ý Summary trong phiên giao việc này**. Không hiệu đính câu hỏi, không tự thêm lời giải. Các tài liệu PDF chỉ là nguồn nội dung; yêu cầu triển khai lấy từ văn bản nhiệm vụ của giáo viên.

## Tài liệu đã đọc đầy đủ

| Tài liệu được cung cấp | Bản giữ nguyên trong repository | Số trang |
| --- | --- | ---: |
| UNIT 1-6 VOCAB Unit 2.pdf | `../unit-2-individuals-and-families/sources/worksheet.pdf` | 5, in số 12–16 |
| Dap_an_Unit_2_Individuals_and_Families.pdf | `../unit-2-individuals-and-families/sources/answer-key.pdf` | 2 |

Tên tệp tải lên không có hậu tố `(1)` như tên trong bản giao việc. Đã dùng chính hai PDF được đính kèm. Nguồn đề có ghi tác giả “Prepared by Phạm Bá Đạt”. Bản PDF giữ nguyên cả phần đầu/cuối trang; nội dung bài học không chèn số trang, footer liên hệ của bản in.

SHA-256 PDF đề: `a5ff100f8de3b8fe7bb4da3c623404952447576c63fdbdf9567a599255c3b417`.

SHA-256 PDF đáp án: `31bf0a766032a340607f9de09cae761e47ef4365cf9ddec36bd7347fcf7874b7`.

`sources/integrity.json` ghi hash/kích thước cho cả hai PDF và văn bản trích xuất đầy đủ. `tests/source-pdf.py` đọc lại đủ 7 trang bằng Poppler, so sánh văn bản và kiểm tra từng trường dữ liệu qua `extract-source.py --verify`.

## Quy tắc trích xuất

File đề quyết định toàn bộ câu chữ học sinh đọc. File đáp án chỉ cung cấp đáp án, giải thích, đoạn Summary đã điền, bản dịch tham khảo, bảng cụm từ và lưu ý học thuật. Chỉ bỏ xuống dòng do dàn trang, bullet trang trí và header/footer; nối bằng khoảng trắng. Giữ dấu câu, apostrophe, cách viết `behavior`, synonym, tiếng Việt và thứ tự. Không dùng đoạn Summary hoàn chỉnh trong file đáp án để thay cho đoạn Summary có chỗ trống trong đề.

## Ma trận nội dung

| Nội dung | Nguồn PDF đề | Dữ liệu ứng dụng | Kết quả |
| --- | --- | --- | --- |
| Passage 1 — The Role of Parents in a Child’s Development | Trang 1 / số in 12 | `unit.json → passages[0]`, 4 mục Vocabulary | Đủ, nguyên văn |
| Passage 2 — Family as a Support System | Trang 1 / 12 | `passages[1]`, 3 mục | Đủ, nguyên văn |
| Passage 3 — Shared Responsibilities at Home | Trang 1 / 12 | `passages[2]`, 4 mục | Đủ, nguyên văn |
| Passage 4 — Individual Responsibility in Society | Trang 1 / 12 | `passages[3]`, 3 mục | Đủ, nguyên văn |
| Passage 5 — Intergenerational Relationships | Trang 1 / 12 | `passages[4]`, 4 mục | Đủ, nguyên văn |
| Passage 6 — Work-Life Balance for Families | Tiêu đề trang 1; nội dung trang 2 / 13 | `passages[5]`, 3 mục | Ghép đúng qua ngắt trang |
| Passage 7 — Education Begins at Home | Trang 2 / 13 | `passages[6]`, 3 mục | Đủ, nguyên văn |
| Passage 8 — Family Traditions and Culture | Trang 2 / 13 | `passages[7]`, 3 mục | Đủ, nguyên văn |
| Passage 9 — Supporting Elderly Family Members | Trang 2 / 13 | `passages[8]`, 2 mục | Đủ, nguyên văn |
| Passage 10 — Family Conflicts and Resolution | Trang 2 / 13 | `passages[9]`, 4 mục | Đủ, nguyên văn |
| Vocabulary Summary | Trang 2–3 / 13–14 | `vocabularySummary`, 33 mục | Đủ; hiển thị sau Passage 10 |
| Reading Practice | Trang 3 / 14 | `reading`, đúng 5 đoạn | Đủ, đúng thứ tự |
| Multiple Choice câu 1 | Trang 3 / 14 | `multipleChoice[0]`, A–D | Đủ |
| Multiple Choice câu 2–9 | Trang 4 / 15 | `multipleChoice[1…8]`, A–D | Đủ |
| Multiple Choice câu 10 | Trang 4–5 / 15–16 | `multipleChoice[9]`, A–D | Ghép đúng hai lựa chọn cuối ở trang 5 |
| Summary Completion | Trang 5 / 16 | `summary.paragraphs`, 3 đoạn, 10 ô | Nguyên văn, không hiệu đính |
| Word Bank | Trang 5 / 16 | `summary.wordBankText` và `wordBank`, 10 từ | Đúng thứ tự, không thêm từ |
| Translation tiếng Việt | Trang 5 / 16 | `translation.text` | Đầy đủ; không dùng bản dịch để viết lại đề |

Tổng cộng **33 mục Vocabulary** với nghĩa tiếng Việt và toàn bộ synonym có trong nguồn. Phần A/B không chấm điểm và không tạo câu trắc nghiệm mới từ Vocabulary.

## Đáp án và giải thích

Toàn bộ 10 giải thích tiếng Việt MCQ lấy nguyên văn từ trang 1 của PDF đáp án. Không thêm lời giải mới cho Summary, vì tài liệu chỉ có bảng đáp án, đoạn hoàn chỉnh và lưu ý. Sau kiểm tra từng ô hoặc sau nộp, Summary đối chiếu chính câu trong đáp án nguồn; đoạn hoàn chỉnh đầy đủ và lưu ý gốc vẫn mở sau nộp. Trang 2 của PDF đáp án cung cấp bản dịch tham khảo và đủ 10 cặp cụm từ Việt–Anh, chỉ mở sau khi nộp.

| Câu / Ô | MCQ | Summary |
| ---: | :---: | --- |
| 1 | B | behavior |
| 2 | B | support |
| 3 | C | support |
| 4 | C | relationships |
| 5 | B | distance |
| 6 | C | balance |
| 7 | B | traditions |
| 8 | D | wisdom |
| 9 | C | energy |
| 10 | C | conflicts |

Word Bank giữ đúng: **support – behavior – traditions – wisdom – balance – distance – energy – conflicts – relationships – assistance**.

## Hai điểm giáo viên đã xác nhận giữ nguyên

1. **Ô 2 và 3 đều là `support`**, nhưng Word Bank chỉ liệt kê từ này một lần. Giữ nguyên Word Bank, cho nhập lại cùng từ tại nhiều ô, không áp dụng cơ chế dùng một lần. Giáo viên đã xác nhận tiếp tục giữ nguyên đề/đáp án và giữ lưu ý này.
2. **Ô 4 tạo cụm `reduced family relationships`**. File đáp án ghi chú cụm này chưa tự nhiên và gợi ý hai cách hiệu đính; ứng dụng không áp dụng các gợi ý vào đề. Giữ `relationships` làm đáp án theo tài liệu. Giáo viên đã xác nhận giữ nguyên nội dung nguồn và giữ lưu ý này; chưa áp dụng bản hiệu đính.

Ghi chú khác từ nguồn: ô 7 dùng `cultural traditions`, phù hợp Word Bank; cách diễn đạt trong Reading không giống hoàn toàn. Giữ nguyên, không suy diễn thành đáp án khác. Từ `assistance` trong Word Bank không được dùng trong đáp án; không loại bỏ.

Không còn khác biệt giữa dữ liệu JSON và hai PDF ngoài việc bỏ ngắt dòng dàn trang. Không tự chấp nhận synonym, không chấm Translation bằng so khớp, không quy đổi band. Nộp bài được chấm theo **20 câu xác định**; bài dịch được trình bày riêng để giáo viên đọc và đánh giá.

## Bổ sung kiểm tra ngay khi làm và Keywords

Theo yêu cầu tiếp theo của giáo viên, bổ sung nút kiểm tra giống game đề trường; yêu cầu này thay cho cách chỉ hiện đáp án sau nộp trước đây. Không sửa `unit.json`, `answers.json` hoặc PDF nguồn.

`support.json` lưu 20 mục Keywords/dẫn chứng (10 MCQ + 10 Summary). Đây là **phần chọn lọc bổ sung để trình bày**, không nhận là danh sách Keywords có sẵn trong PDF. Tất cả từ khóa đều là chuỗi nguyên văn trong dẫn chứng; mỗi dẫn chứng là câu/nhóm câu liền nhau từ `reading` hoặc `completedSummary`, có số đoạn và nguồn rõ ràng. `build-support.py --verify` kiểm tra việc trích chọn; model test đối chiếu từng từ/câu với dữ liệu nguồn đã xác minh.

MCQ giữ nguyên giải thích tiếng Việt, bổ sung trích dẫn Reading có tô sáng Keywords. Summary không sáng tác thêm lời giải tiếng Việt; dùng đúng câu Summary đã điền từ file đáp án để đối chiếu và hiển thị Keywords trong đó. Những ô Summary chưa kiểm tra vẫn được che trong câu dẫn chứng; bản hoàn chỉnh đầy đủ chỉ mở sau nộp. Hai lưu ý `support` và `relationships` đã được giáo viên xác nhận tiếp tục giữ nguyên. Translation vẫn là tự luận, không thêm chấm tự động.

## Cập nhật cách trình bày phần A thành tài liệu

Đã đọc lại trực tiếp toàn bộ `sources/worksheet.pdf` theo yêu cầu mới. Phần A hiện trình bày liên tục đúng thứ tự Passage 1–10, với đoạn văn đầy đủ và danh sách Vocabulary ngay bên dưới; 33 mục nghĩa/synonym và 33 dòng Vocabulary Summary hiện sẵn, không cần mở thu gọn. Không có câu hỏi/chấm điểm hoặc hiệu ứng game trong tài liệu.

Chỉ thay đổi DOM/CSS và điều hướng; `unit.json`, `answers.json`, `support.json` cùng các PDF/văn bản nguồn không đổi byte. Browser test đối chiếu toàn bộ văn bản từng passage và `sourceText` của mỗi mục Vocabulary, kể cả dấu câu và synonym, với dữ liệu đã xác minh từ PDF.
