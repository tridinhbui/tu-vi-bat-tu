# Đánh giá trải nghiệm người mới — Thiên Bàn

Cách làm: chạy site cục bộ, đóng vai người chưa biết gì về Tử Vi/Bát Tự, đi 3 hành trình (desktop + mobile 375px) trên lá số mẫu 17/05/1990 10:30. Không soi lỗi kỹ thuật.

## Kết luận một dòng
Site là **một công cụ tra cứu minh bạch dành cho người đã biết nghề**, chưa phải **người dẫn đường cho người mới**. Phần "tính" rất mạnh; phần "dịch ra đời thường" và "dạy" gần như vắng.

## Ba hành trình

**A. Người chỉ tò mò (muốn biết "tôi là người thế nào")**
- Trang chủ đẹp, gọn, nhưng hero chỉ nói "Can Chi, Ngũ Hành, hệ thống luận giải có thể truy vết" — 3 từ lạ trong câu đầu, không nói "bạn sẽ nhận được gì".
- Bấm lá số mẫu → vào thẳng tab **Bát Tự** (không phải Tử Vi), chip "Nhâm Thủy NHẬT CHỦ · Hỏa lục cục · Mệnh Lộ Bàng Thổ" không giải thích. Cuộn xuống là 8 chương, ~30.000 ký tự. Không có câu trả lời "tóm lại tôi là ai" trong 10 giây.
- Kết quả đọc được lại mâu thuẫn mà không tổng hợp: "tự cao", "hay tranh cãi", "phóng đãng", "thiếu tình nghĩa", cùng "giàu sang lớn". Người mới chỉ nhớ những chữ xấu.

**B. Người muốn hiểu lá số của mình**
- Nhấp cung Nô Bộc → ngăn bên hiện "Thiên Lương HÃM", "Cát tinh: Văn Xương…", rồi **"Chưa có quy tắc nào được kích hoạt cho cung này"**. Ngõ cụt: không nói Nô Bộc là gì (bạn bè, cấp dưới), Thiên Lương là sao gì, HÃM là yếu hay mạnh.
- Phần luận giải trộn nhãn THẾ/KHÍ/TƯỢNG/BIẾN/TỔNG/DỤNG/CÁCH, trích nguồn "八字真宗 PDF pp.24-25", "TH p.33", "Khảo Luận pp.195-197" — vô nghĩa với người mới, và chiếm chỗ của lời giải thích.
- Nhiều chỗ kết thúc bằng "hệ thống không kết luận" (thân vượng/nhược, Dụng thần, cách cục, sự nghiệp, hôn nhân: "chưa có quy tắc nào"). Trung thực là điểm cộng, nhưng người dùng ra về tay trắng. Sao Thiên Lương/Vũ Khúc có sẵn `star_profiles.json` nhưng chưa thành giải thích tại chỗ.

**C. Người muốn học**
- Thư viện chỉ có **5 đoạn ngắn** trong hộp thoại (Can Chi, Ngũ Hành, Tam phương, Tuần Triệt, Giờ Tý, Tiết khí). Không có: Tử Vi là gì, Bát Tự là gì, hai hệ khác nhau thế nào, 12 cung nghĩa là gì, 14 chính tinh, Thập Thần, Tứ Hóa, Miếu/Hãm.
- "Thư viện" ở thanh điều hướng, nếu bấm, đưa tới `/library` — trang dành cho người soạn quy tắc (JSON, verified/draft). Lạc đề với người học.
- Không có thuật ngữ nào gạch chân/tooltip trong lá số (không `title`, không glossary).

## 10 câu hỏi

| # | Điểm | Nhận xét |
|---|---|---|
| 1. 5 giây đầu | 5/10 | Đẹp, rõ nút bấm. Nhưng không nói Tử Vi vs Bát Tự khác gì, không gợi ý bắt đầu từ đâu; "Không dùng AI" là điểm nhấn của dev, không phải của người mới. |
| 2. Hành trình | 5/10 | Form tốt (chọn giờ Địa chi, "không rõ giờ sinh"). Đáng ngại: form đã điền sẵn 17/05/1990 nên dễ bấm nhầm ra lá số mẫu; sau kết quả là tường chữ. |
| 3. Đọc lá số | 3/10 | Không có "nhìn đây trước": 12 cung × hàng chục sao cùng độ nổi bật. Nên đánh dấu Mệnh/Thân và 3 sao đáng chú ý. |
| 4. Luận giải | 3/10 | Có chữ Việt nhưng là văn giải thuật ("Có thể nhận thấy một dấu hiệu liên quan đến khuynh hướng…"), không ví dụ đời sống, không tổng hợp. |
| 5. Hướng dẫn học | 2/10 | Gần như không có (xem hành trình C). |
| 6. Tương tác | 5/10 | Chạm cung → sáng tam phương, ngăn chi tiết: hướng đúng. Nhưng chạm **sao** không ra giải thích, Can Chi/Thập Thần không click được. |
| 7. Cảm xúc | 4/10 | Tò mò ban đầu (la bàn, ngũ hành tương tác), rồi choáng ngợp. Văn bản "bản nháp chưa xác minh" lặp nhiều làm mất niềm tin cả những phần tốt. |
| 8. Giá trị 10–15 phút | 4/10 | Người mới nhớ được "Nhật Chủ", "Mệnh", ngũ hành sinh khắc; không rút ra được cách luận. |
| 9. Mobile | 7/10 | Form dùng được, không tràn ngang, có chế độ **Tổng quan dạng danh sách** (rất tốt). Trừ điểm: thanh tab chương bị cắt, "Trường phái: vn_dlhc_draft" lộ mã nội bộ. |
| 10. Giữ chân | 3/10 | Không có tài khoản/đánh dấu, không "bài học tiếp theo", không "lá số của người thân", không so sánh, không nhắc năm nay. Lập xong là hết lý do quay lại. |

## Điều làm tốt (nên giữ)
Giao diện tinh tế; tách "dữ kiện tính" và "diễn giải truyền thống"; nhãn độ tin cậy; nút "Vì sao quy tắc này khớp?" (độc nhất so với web tử vi khác); danh sách mobile; form chọn giờ Địa chi.

## Đề xuất, xếp theo hiệu quả

**P0 — làm trước (trả lời "tôi là ai" và "đây là gì")**
1. **Thẻ "Tóm tắt cho người mới" ở đầu kết quả**: 3–5 câu tiếng đời thường, kèm đúng 3 điểm nổi bật + 1 điểm cần lưu ý, và một câu nói mâu thuẫn là bình thường ("lá số là bản đồ xu hướng, không phải một người duy nhất"). Sinh từ chính các luật đã kích hoạt, gom theo chủ đề.
2. **Hero + "Bắt đầu từ đâu"**: một câu cho mỗi hệ ("Tử Vi: bản đồ 12 lĩnh vực đời sống. Bát Tự: 8 chữ cho biết bạn là kiểu năng lượng nào") và 3 cổng: "Tôi tò mò → lá số mẫu", "Hiểu lá số của tôi", "Học từ đầu".
3. **Chạm là giải thích**: mọi sao, cung, Can/Chi, Thập Thần, HÃM/MIẾU có tooltip/ngăn chi tiết một dòng ("Nô Bộc: bạn bè, cấp dưới, người giúp việc"). Dữ liệu sao đã có trong `star_profiles.json`.
4. **Ngõ cụt thành lời mời**: thay "Chưa có quy tắc nào…" bằng ý nghĩa của cung đó + gợi ý "đọc cung này liên quan tới…".

**P1 — dẫn dắt**
5. Chế độ **"Đọc theo 5 bước"**: Mệnh → Thân → cung Tài/Quan → Tứ Hóa → đại hạn hiện tại; mỗi bước làm sáng đúng phần cần nhìn, làm mờ phần còn lại.
6. **Hai tầng nội dung**: "Dễ hiểu" mặc định; "Chuyên sâu/kiểm chứng" (THẾ/KHÍ/…, trang sách, trace) gập sẵn. Đổi nhãn THẾ/KHÍ/TƯỢNG thành chữ thường hoặc ẩn.
7. Mở kết quả ở tab **Tử Vi** hoặc cho chọn; chip đầu trang thêm "?" giải thích Nhật Chủ, Cục, Mệnh Lộ Bàng Thổ.
8. Bỏ mã nội bộ khỏi giao diện (`vn_dlhc_draft`); gom thông báo "nháp" thành một lần, đặt ở đầu thay vì lặp ở từng thẻ.

**P2 — học và quay lại**
9. **Lộ trình học 3 cấp** (Mới nhập môn → Đọc được lá số → Hiểu cách luận): Tử Vi là gì / Bát Tự là gì / 12 cung / 14 chính tinh / Thập Thần / Tứ Hóa / Miếu-Hãm, mỗi bài 2 phút, có "xem trên lá số của bạn" làm ví dụ.
10. Tách **Thư viện học** (cho người đọc) khỏi **Thư viện quy tắc** (cho dev, `/library`), đổi tên menu.
11. Giữ chân: "Năm nay của bạn" (lưu niên, có sẵn), lưu lá số trên trình duyệt (localStorage, vẫn không gửi server), lá số người thân/so sánh, đố vui "đoán sao Mệnh".
12. Mobile: cho tab chương cuộn ngang có chỉ báo, thêm "Tóm tắt" làm tab đầu.

## Lưu ý
Đây là đánh giá bằng một lá số mẫu và vai người mới mô phỏng, chưa phải thử nghiệm với người thật; nên chạy 5 người dùng thật với thử thách "sau 5 phút, kể lại tôi là người thế nào".
