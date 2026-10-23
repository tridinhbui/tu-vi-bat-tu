# Cách cục: nguồn trang sách cho mười cách (W4, phần dữ liệu)

Ngày 2026-10-23. Owner review item 13. Dữ liệu: `engine/data/formations_verified.json`, sinh bởi `tools/build_formations_verified.py`;
kiểm tra: `engine/tests/test_formations_verified.py`. Không sửa file prose nào; chương Cách cục do phiên chính dựng.

## Kết quả

- **9 verified, 1 disputed (Mã đầu đới kiếm), 0 rejected.** Cả mười cách đều có trang sách cho lõi.
- **154 trích dẫn**, tất cả nằm trên trang của nó (`book_text.quote_on_page`). Trang TH xáo dòng, nên trích dẫn TH là đoạn liền trong lớp chữ;
  câu đầy đủ đọc từ ảnh trang nằm ở trường `image`. Đã xem ảnh các trang TH 43, 72–74, 76–77, 116, 157, 159 và KL 96; trích dẫn TH p.75 là một dòng liền.
- **75 điều kiện của bản nháp bị bỏ**, mỗi điều có lý do trong `dropped` (kèm trang khi có trang cho thấy lý do).
- **Không trang nào nêu điều cứu giải (rescuer) cho cách nào trong mười cách.** Tất cả `rescuers` để trống. `tam_hoa_hoi_cuu` của bản nháp
  không có căn cứ: TH p.74 chỉ nói Tam Hóa cứu Mệnh ở bại địa, tuyệt địa. Vì vậy trạng thái `pha_duoc_cuu` không bao giờ xảy ra.

Nguồn chính về thành cách và phá cách là **TH pp.76–77 "Luận các cách ở Mệnh Thân"**: thượng cách (Tử Phủ Vũ Tướng, Cơ Nguyệt Đồng Lương,
Sát Phá Liêm Tham, Cự Nhật, Nhật Nguyệt đồng cung cần nhập miếu, vượng, đắc địa, hội Tả Hữu, Xương Khúc, Khôi Việt, Long Phượng, Hồng Đào,
Tam Hóa thì "phát đến Tam công") và hạ cách ("không gặp được cát tinh hội đủ bộ, mà lại gặp Hung tinh và sát tinh đóng", "suốt đời lao khổ").
KL pp.166–167 chỉ gọi tên bốn nhóm chính tinh, không nói phá hay cứu.

## Việc phiên chính cần làm khi dùng file

1. `formation.validate_formations` từ chối mọi `reviewStatus: verified` ("none supported yet"). Cần nới quy tắc này cho file này, vì mỗi điều
   kiện giờ đã có trang trong `evidence`. Test chỉ chấp nhận lỗi đó và lỗi "needs at least one booster" ở các cách có `core_alone: thanh`.
2. **`evidence[id].core_alone`**: `thanh` nghĩa là sách kể chính cái lõi là một quý cách (Tử Phủ đồng cung, Nhật Nguyệt tịnh minh,
   Nhật lệ trung thiên, Tam kỳ gia hội, Khôi Việt giáp Mệnh). Bộ đánh giá hiện tại cho lõi không kèm điều tăng thế là `hinh_thuc`, nên
   bốn cách hiện ra là "chỉ có hình thức" dù sách gọi là cách đẹp. Cần ánh xạ `hinh_thuc → thanh` khi `core_alone == "thanh"`, ở cả
   `formation_eval.py` lẫn `structures.ts`. Chưa thêm kiểm tra song song TS: `structures.ts` chưa đọc file này.
3. Chỉ đưa ra người đọc các cách `verified`. Mã đầu đới kiếm là `disputed`, xem bên dưới.
4. Mỗi điều kiện có `scope` (`cach`: sách nói cho chính cách này; `cach_ghep`: một cách có tên trong sách, gồm cách này cộng điều kiện thêm)
   và `reading` (cách hệ thống đọc câu sách thành điều kiện máy). Các quy ước của hệ thống đều ghi trong `reading`: "gặp" đọc là hội trong
   tam phương tứ chính; một nhóm sao kể liền nhau cần từ hai sao; "nhiều" hung sát = từ hai; thượng cách = hai bộ cát tinh.
5. Tần suất trên 3.000 lá số thật (Mệnh): Tử Phủ đồng cung bị phá 1,2% trên 1,5% có lõi, và Thạch trung ẩn ngọc bị phá 1,2% trên 1,6%,
   vì sát tinh hoặc Lộc Tồn, Kỵ, Hình gần như luôn có trong tam phương. Đó là hệ quả của cách đọc "gặp = trong tam phương". Đọc chặt hơn
   (đồng cung) là một lựa chọn mà phiên chính có thể cân nhắc.

## Từng cách

Tên viết tắt: KL Khảo Luận, TH Thực Hành, TT Toàn Thư. Mọi cách đều neo ở Mệnh (TH p.76 nói "đóng Mệnh Thân"; Thân chưa xét).

### Tử Phủ Vũ Tướng: verified, lõi chỉ là hình thức
- Lõi: TH p.72 mục 7; TH p.76 (thượng cách); KL p.166; hiệu lực KL p.96. Sách không định nghĩa hình học. Hệ thống đọc là đủ bốn sao trong
  tam phương, như TT p.24 định nghĩa nhóm song song Cơ Nguyệt Đồng Lương.
- Giữ: tăng thế = sáu bộ cát tinh đủ bộ của TH p.76 (Tả Hữu có thêm KL p.132). Phá = hạ cách TH p.77. Phản chứng = chính tinh bình hoặc hãm (TH p.76).
- Bỏ: `loc_hoi` (KL p.96 nói về sao Thiên Phủ); `sat_dong_cung` và `ky_dong_cung` (gộp vào hạ cách); `khoa_dong_cung`, `tam_hoa_hoi_cuu`;
  `tuan_triet_an_ngu` (TH p.94 nói về sao Thiên Phủ); `Thiên_Tướng_ham` (thay bằng phản chứng độ sáng). Xương Khúc đổi từ một sao lẻ thành đủ bộ.

### Tử Phủ đồng cung: verified, lõi là cách
- Lõi: TH p.72 mục 1; KL p.49 mục 4 (Mệnh Dần Thân, cả đời sung sướng); hiệu lực KL p.55.
- Giữ: tăng thế = Lộc Tồn hội (TT p.22, `thuong_at` 1). Phá = sát tinh hội trong tam phương (TT p.22 "vô sát tấu", hiểu theo lời giảng KL p.49).
  Phản chứng = Tuần hoặc Triệt ở Mệnh (KL p.55 và TT p.160: "kém đi", không phá hẳn).
- Bỏ: Tả Hữu, Xương Khúc, Khôi Việt (các câu ở KL p.49, 55 nói về từng sao); `sat_dong_cung` (thay bằng hội); Kỵ; hai điều cứu.
- Ghi chú: câu "Tử Phủ đồng cung lâm Tị Hợi" ở TT p.22 không thể xảy ra trên lá số, nên không dùng.

### Cơ Nguyệt Đồng Lương: verified, lõi chỉ là hình thức
- Lõi: TT p.24 (đủ bốn sao trong Mệnh và các cung tam hợp xung chiếu); KL p.51 mục 4 (thường là công chức).
- Giữ: sáu bộ cát tinh của TH p.76; phá = hạ cách TH p.77, cộng **Không Kiếp Kỵ** (TT p.24 "xuống hạ cách"), cộng **Hỏa Linh** (TH p.159
  "tối kỵ Hỏa Linh xâm phá"); phản chứng độ sáng.
- Bỏ: `cat_tinh_hoi` và `khoa_quyen_loc_hoi` (sao lẻ, thay bằng đủ bộ); `khong_kiep_dong_cung` và `ky_dong_cung` (thay bằng điều của TT p.24);
  hai điều cứu; `tuan_triet_an_ngu` (TH p.75 nói ngược lại: Mệnh Tuần, Thân Triệt rất cần Cơ Nguyệt Đồng Lương sáng sủa).

### Sát Phá Liêm Tham: verified, lõi chỉ là hình thức
- Lõi: KL p.167; TH pp.76–77. Đọc là đủ Sát, Phá, Tham trong tam phương. Ba sao này luôn tạo một bộ tam hợp, nên tương đương ngưỡng
  "ba trong bốn" của bản nháp.
- Giữ: sáu bộ cát tinh; phá = hạ cách TH p.77 (ví dụ của sách chính là Sát Phá Liêm Tham); phản chứng độ sáng.
- Bỏ: `khoa_quyen_hoi`; `ba_sat_va_ky_trong_tam_phuong` (thay bằng hạ cách); Kỵ; hai điều cứu; `tuan_triet_an_ngu`; `Thất_Sát_ham`.
- Ghi chú: TH p.76 (phi thường cách, nói cho Thân) coi Kình, Không, Kiếp, Hình Hổ là tốt khi Sát Phá Liêm Tham nhập miếu. Không mã hóa.

### Nhật Nguyệt tịnh minh: verified, lõi là cách, đã định nghĩa lại
- Lõi theo TH p.72 mục 21: Nhật ở Thìn, Tỵ, Nguyệt ở Dậu, Tuất, Mệnh đóng ở Nhật hay Nguyệt. Hiệu lực KL p.53 mục 9. Bản nháp chỉ đòi
  "Nhật và Nguyệt trong tam phương", rộng hơn nhiều.
- Không có điều tăng thế, phá hay cứu nào trên trang. Biến thể: KL p.53 mục 6 (hợp chiếu ở Sửu, Mùi, chưa mã hóa); TT p.142 (cả hai miếu vượng, khớp).
- Bỏ: toàn bộ chín điều của bản nháp. "Nhật Nguyệt tàn hung" (TH p.74) là một bần cách riêng. KL p.53 mục 12 nói về tính cách, không nói phá cách.

### Nhật lệ trung thiên: verified, lõi là cách
- Lõi: TH p.72 mục 22, KL p.52 mục 2, TT p.158. Tăng thế: tuổi Canh, Tân, Đinh, Kỷ (KL p.52 mục 3, `thuong_at` 1).
- Bỏ: toàn bộ chín điều của bản nháp (không trang nào nói Tả Hữu, Xương Khúc, sát, Kỵ, Tuần Triệt với cách này).

### Thạch trung ẩn ngọc: verified, lõi chỉ là hình thức
- Lõi: KL p.44 mục 6, TH p.43, TT p.123; hiệu lực KL p.106, TT p.34.
- Giữ: tăng thế = **Tuần hoặc Triệt ở Mệnh** (TH p.43, KL p.106), Hóa Lộc hội (TH p.43), đủ Khoa Quyền Lộc (KL p.57, TT p.34), Song Hao (KL p.203,
  p.106). Phá = Lộc Tồn hội ("ngọc chìm", TH p.43), Hóa Kỵ hoặc Thiên Hình hội (TH p.43).
- **Bản nháp làm ngược sách:** Tuần Triệt là phản chứng trong bản nháp, nhưng sách nói cách này cần nó. Đã chuyển thành điều tăng thế.
- Bỏ: chữ "Sát" trong "Kỵ, Hình, Sát" (cùng trang nói Cự đắc địa gặp sát tinh thì phú quý); `ky_hoac_kinh_dong_cung` (KL p.66 nói về Tam kỳ);
  `ta_huu_hoi`; `khoa_dong_cung`; `Cự_Môn_ham` (Cự ở Tý Ngọ không bao giờ hãm).

### Mã đầu đới kiếm: disputed, không đưa ra người đọc
- KL p.64: Mệnh ở Ngọ có Kình đồng cung. Xa Thất Sát, Thiên Hình mà gặp Khoa Quyền Lộc thì hiển đạt võ nghiệp; gặp Thất Sát, Thiên Hình
  đồng cung thì yểu hoặc tàn tật. TT p.50 đồng ý.
- Trái lại: TT p.142 nói Kình gặp Thiên Mã, phải ở tứ mộ, ở Ngọ thì xấu. KL p.200 đòi thêm Thiên Mã và Tham Lang ("không bền").
  Điều kiện đã mã hóa theo KL p.64 để dùng khi có quyết định.

### Tam kỳ gia hội: verified, lõi là cách
- Lõi: KL p.66 mục 10, TH p.73 mục 26, TT p.142. Phá = Hóa Kỵ hoặc Kình Dương "đồng cung hoặc chiếu" (KL p.66; mở rộng từ chỉ đồng cung).
  Tăng thế = Văn chức cách (TH p.77: Tam Hóa triều cộng Xương Khúc, Khôi Việt, Tả Hữu; rất hiếm).
- Bỏ: `hoa_o_ban_cung`; Tả Hữu, Xương Khúc lẻ; `ta_huu_giai_ky`; `tuan_triet_an_ngu`.

### Khôi Việt giáp Mệnh: verified, lõi là cách
- Lõi: KL p.44 mục 9, KL p.62 mục 3, TT p.46. Không trang nào nêu điều tăng thế hay phá. KL p.62 mục 4 và TT p.46 nói về Khôi Việt ở Mệnh
  gặp sát, không phải giáp Mệnh.
- Bỏ: toàn bộ chín điều của bản nháp.

## Ngoài phạm vi, nhưng tìm thấy

- TH p.116 "Đại tiểu hạn thất lộ": các nhóm chính tinh gặp sát tinh trong vận hạn (CNĐL hay Cự Nhật gặp Kình Đà, Không Kiếp...;
  Tử Phủ Vũ Tướng gặp Tam Không, Kiếp Kỵ Hình Đà...). Đây là điều kiện vận hạn, không phải phá cách gốc.
- TT pp.143–155 có hai đoạn "Thập nhị cung chư tinh đắc địa hợp cách quyết" và "thất hãm phá cách quyết", hợp cách và phá cách theo
  từng cung. Đây là nguồn cho cách theo vị trí nếu sau này mở rộng.
