# Biểu đồ vận "Tổng quan lá số" — đánh giá (indices-2.0.0, 2026-10-21)

Track A của kế hoạch 2026-10-21: biểu đồ đại vận / năm / tháng đo **mức kích hoạt của thời vận trên cả lá số**, không dùng lại luận giải bẩm sinh của cung vận. Số liệu sinh bởi `node tools/interpret/index_norms.ts` trên `corpus1000.json.gz` (1.000 lá, bộ mẫu phân tầng, không phải dân số thật). Tất cả là kiểm tra tự động; chưa có chuyên gia chấm.

## Mô hình

| Giai đoạn | Lớp (mỗi lớp quy về điểm chuẩn z so với bộ mẫu) | Trọng số | Nguồn |
|---|---|---|---|
| Đại vận | Tứ Hóa theo can đại vận rơi vào cung vận, tam phương, Mệnh | 0,45 | thông lệ (phi hóa), ba sách không có câu luận |
| | Câu sách về cung vận | 0,45 | KL tr.230-236, TH tr.115-117; Toàn Thư tr.97-105 diễn ý × 0,5 |
| | Nền bẩm sinh của cung vận | 0,10 | radar, chỉ là nền, không bao giờ được liệt kê là lý do |
| | Độ vững cả lá số (Mệnh + tam phương; cách cục thử nghiệm × 0,5) | hệ số ± 0,15 × z (giới hạn 1,5) | quy ước hệ thống |
| Năm | Đại vận đang đi | 0,40 | |
| | Câu sách về cung tiểu hạn (năm xem: `year.tieu_han_tt/kl`) | 0,25 | như trên |
| | Nền bẩm sinh cung tiểu hạn | 0,10 | |
| | Cung lưu Thái Tuế (chất lượng bẩm sinh) | 0,05 | vị trí KL tr.41-42, dùng chất lượng là quy ước |
| | Chín sao lưu chạm tiểu hạn / tam phương / Mệnh | 0,10 | vị trí KL tr.41-42; Khốc Hư tại tiểu hạn "là xấu", thêm hung tinh "năm đầy tai ương" TH tr.114 (đã xem ảnh trang); Kình Đà Lộc Tồn theo loại sao: thông lệ; KL tr.41 "không nặng ký" → trọng số thấp |
| | Lưu Tứ Hóa | 0,10 | thông lệ, không có trong ba sách |
| Tháng | Mức của năm + 0,25 × z (nền bẩm sinh cung nguyệt hạn) | | vị trí TH tr.115 |

Năm mức (Rất thử thách · Nhiều thử thách · Trung bình · Thuận · Rất thuận) = ngưỡng 10 / 30 / 70 / 90 % của chính loại giai đoạn trên bộ mẫu. Dải Bát Tự dưới biểu đồ đại vận: vận nào mang thần điều hậu của bảng Thiệu Vĩ Hoa (tr.389-396; dụng / hỷ / không mang — bảng không định nghĩa kỵ), không cộng vào mức Tử Vi.

Sửa kèm: `rarity()` đọc theo cung của nhận định (`kg.baseRates.palaces`); trước đây mọi luật ngoài Mệnh cùng "trọng số 0,63".

## Kiểm tra

| Chỉ số | Trước (indices-1.0.0) | Sau (indices-2.0.0) |
|---|---|---|
| Tương quan điểm đại vận với chất lượng bẩm sinh của cung đại vận (10.000 chặng) | 0,424 (bên thuận 0,432, bên thử thách 0,530) | **0,243** |
| Tương quan với lớp Tứ Hóa / câu sách / nền | — | 0,687 / 0,686 / 0,243 |
| Tương quan riêng của lớp Tứ Hóa, lớp câu sách với chất lượng bẩm sinh (300 lá) | — | 0,04 / 0,07 |
| Tương quan điểm năm với đại vận của nó | — | 0,796 |
| Phân bố năm mức, đại vận | (hai số thập phân, không có mức) | 10 / 20 / 40 / 20 / 10 % |
| Phân bố năm mức, chỉ các đại vận hiện hành | — | 8,6 / 20,2 / 40,3 / 22,0 / 8,9 % |
| Phân bố năm mức, năm / tháng | — | 10 / 20 / 40 / 20 / 10 % |

Phản thực (`src/interpret/test/indices.test.ts`, lá tham chiếu Cự Môn Tuất): đổi Tứ Hóa của chặng Phu Thê sang Tứ Hóa can Giáp → điểm chặng đổi > 0,3, các chặng khác giữ nguyên; bỏ một luật bẩm sinh ở cung ngoài tam phương của chặng và của Mệnh → điểm chặng không đổi; bỏ một luật trong tam phương của chặng → đổi < 0,15 (chỉ qua lớp nền). Chín sao lưu khớp Python (`year.luu_stars`) trên cả 1.000 lá; tiểu hạn và lưu Thái Tuế khớp Python trên benchmark20.

Văn: mỗi chặng / năm 2–4 câu, không mã luật, không "trọng số", không số thập phân; mã luật, trang, trọng số, điểm chuẩn và công thức chỉ ở phần "Căn cứ".
