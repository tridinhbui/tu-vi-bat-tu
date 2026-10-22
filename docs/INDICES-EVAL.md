# Biểu đồ vận "Tổng quan lá số" — đánh giá (indices-2.1.0, 2026-10-21)

Track A của kế hoạch 2026-10-21: biểu đồ đại vận / năm / tháng đo **mức kích hoạt của thời vận trên cả lá số**, không dùng lại luận giải bẩm sinh của cung vận. Số liệu sinh bởi `node tools/interpret/index_norms.ts` trên `corpus1000.json.gz` (1.000 lá, bộ mẫu phân tầng, không phải dân số thật). Tất cả là kiểm tra tự động; chưa có chuyên gia chấm.

## Mô hình

**Sách trước, thông lệ sau** (quy tắc của chủ, 2026-10-21): các lớp có sách quyết định chiều; các lớp thông lệ cộng lại chỉ được thêm tối đa 0,5 × |phần có sách| (+ 0,15 khi cùng chiều hoặc sách không nói), nên chỉ nhấn thêm hoặc làm dịu, không lật được lời sách (`conventionCap`, phần `thong_le_cap` trong "Căn cứ").

| Giai đoạn | Lớp (mỗi lớp quy về điểm chuẩn z so với bộ mẫu) | Trọng số | Nguồn |
|---|---|---|---|
| Đại vận | Câu sách về cung vận | 0,65 | KL tr.230-236, TH tr.115-117; Toàn Thư tr.97-105 diễn ý × 0,5 |
| | Nền bẩm sinh của cung vận | 0,10 | nhận định đã đối chiếu sách (radar); chỉ là nền, không bao giờ được liệt kê là lý do |
| | Tứ Hóa theo can đại vận rơi vào cung vận, tam phương, Mệnh | 0,25, có trần | thông lệ (phi hóa), ba sách không có câu luận |
| | Độ vững: Mệnh + tam phương (nhận định đã đối chiếu, gồm cách cục sách) | hệ số ± 0,15 × z (giới hạn 1,5) | cách cục thử nghiệm (nháp) không còn dùng |
| Năm | Đại vận đang đi | 0,40 | |
| | Câu sách về cung tiểu hạn (năm xem: `year.tieu_han_tt/kl`) | 0,27 | như trên |
| | Nền bẩm sinh cung tiểu hạn | 0,08 | |
| | Lưu Khốc, Hư ở cung tiểu hạn (+ hung tinh) | 0,10 | TH tr.114 (đã xem ảnh trang), vị trí KL tr.41-42 |
| | Thông lệ: cung lưu Thái Tuế 0,04, sao lưu khác theo loại sao 0,04, lưu Tứ Hóa 0,07 | 0,15, có trần | KL tr.41 "không nặng ký" |
| Tháng | Mức của năm + 0,25 × z (nền bẩm sinh cung nguyệt hạn) | | vị trí TH tr.115 |

Năm mức (Rất thử thách · Nhiều thử thách · Trung bình · Thuận · Rất thuận) = ngưỡng 12 / 33 / 67 / 88 % của chính loại giai đoạn trên bộ mẫu. Dải Bát Tự dưới biểu đồ đại vận: vận nào mang thần điều hậu của bảng Thiệu Vĩ Hoa (tr.389-396; dụng / hỷ / không mang — bảng không định nghĩa kỵ), không cộng vào mức Tử Vi.

Sửa kèm: `rarity()` đọc theo cung của nhận định (`kg.baseRates.palaces`); trước đây mọi luật ngoài Mệnh cùng "trọng số 0,63".

## Kiểm tra

| Chỉ số | indices-1.0.0 | 2.0.0 | **2.1.0** |
|---|---|---|---|
| Tương quan điểm đại vận với chất lượng bẩm sinh của cung đại vận (10.000 chặng) | 0,424 | 0,243 | **0,231** |
| Tương quan với lớp câu sách / Tứ Hóa (thông lệ) / nền | — | 0,686 / 0,687 / 0,243 | **0,933 / 0,261 / 0,231** |
| Tương quan điểm năm với đại vận của nó | — | 0,796 | 0,804 |
| Năm mức, đại vận (corpus) | — | 10 / 20 / 40 / 20 / 10 % | **12 / 21 / 34 / 21 / 12 %** |
| Năm mức, chỉ đại vận hiện hành | — | 8,6 / 20,2 / 40,3 / 22,0 / 8,9 % | 11,3 / 20,5 / 34,5 / 22,9 / 10,8 % |
| Năm mức, năm / tháng | — | 10 / 20 / 40 / 20 / 10 % | 12 / 21 / 34 / 21 / 12 % |
| Lá có ≥ 3 chặng "Rất thử thách" / ≥ 3 "Rất thuận" (trên 1.000) | — | 85 / 86 | 146 / 116 |

2.0.0 → 2.1.0: 40,7 % chặng và 35,2 % năm trên corpus đổi mức (2,4 % chặng, 0,9 % năm đổi từ hai mức trở lên). Lá 09/01/2002 04:30 nam: 3/10 chặng đổi (23–32 Phu Thê "Thuận" → "Trung bình": sách −0,67 thắng Tứ Hóa thông lệ +0,68 bị giới hạn còn +0,23), 11/21 năm đổi (2026 "Rất thuận" → "Trung bình"); số chặng "Rất thử thách" 4 → 3. Lá 1911-01-01 12:30 nam: 4/10 chặng, 2/21 năm đổi.

Giới hạn còn lại: khi sách quyết định, các chặng cùng một tam hợp nhận cùng một câu Khảo Luận tr.230-233 (hành tam hợp của vận so với tuổi), nên trên một lá số các mức dễ dồn theo tam hợp hơn trước (146 lá có ≥ 3 chặng "Rất thử thách"). Đó là đúng lời sách, không phải lỗi thang.

Phản thực (`src/interpret/test/indices.test.ts`, lá tham chiếu Cự Môn Tuất): kiểm thêm rằng phần thông lệ luôn nằm trong trần và không lật chiều của sách trên cả benchmark20; đổi Tứ Hóa của chặng Phu Thê sang Tứ Hóa can Giáp → điểm chặng đổi > 0,3, các chặng khác giữ nguyên; bỏ một luật bẩm sinh ở cung ngoài tam phương của chặng và của Mệnh → điểm chặng không đổi; bỏ một luật trong tam phương của chặng → đổi < 0,15 (chỉ qua lớp nền). Chín sao lưu khớp Python (`year.luu_stars`) trên cả 1.000 lá; tiểu hạn và lưu Thái Tuế khớp Python trên benchmark20.

Văn: mỗi chặng / năm 2–4 câu, không mã luật, không "trọng số", không số thập phân; mã luật, trang, trọng số, điểm chuẩn và công thức chỉ ở phần "Căn cứ".
