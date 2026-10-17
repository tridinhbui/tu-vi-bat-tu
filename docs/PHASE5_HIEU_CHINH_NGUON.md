# Phase 5 — Hiệu chỉnh định nghĩa cách cục theo nguồn (bản nháp)

Sinh bởi `tools/build_formation_report5.py` từ `formation_audit.json`, `formations_school_variants.json` và `formation_variants_reach.json`. **Định nghĩa gốc (`formations_experimental.json`, của phiên khác) không bị sửa.** Các hiệu chỉnh nằm ở lớp biến thể riêng theo từng sách; các định nghĩa mâu thuẫn được giữ thành biến thể khác nhau, không gộp, không chọn bên đúng hơn. Mọi thứ vẫn `draft`, chỉ hiện ở `?thu-nghiem`.

## 1. Chốt audit

- Tổng điều kiện: **93**; khớp nguồn **21** (trong đó 21 có câu trích được máy so với văn bản trang, còn lại dựa vào trang TH tr.72 đọc trực tiếp từ ảnh); bị loại khỏi tập có nguồn **43**; đề xuất sửa **23**.
- Các trích dẫn (`van_ban` = máy so với văn bản trang; `anh_doc_ro` = ảnh trang đọc trực tiếp, chữ rõ) được lưu kèm kết quả kiểm trong JSON đã commit, nên việc kiểm lại không phụ thuộc test có chạy hay bị bỏ qua khi thiếu PDF; test đọc PDF tự bỏ qua khi thiếu sách và KHÔNG được tính là bằng chứng.

## 2. Lớp biến thể theo nguồn

17 biến thể cho 10 cách (mỗi biến thể = một sách, một cách đọc). Quy tắc xây dựng: chỉ giữ điều kiện có nguồn ĐÚNG vai trò trong sách đó; thay phạm vi khi câu sách nêu rõ (đồng cung / đối cung / tam phương / hội chiếu); không mở rộng chữ "gặp" khi câu không xác định phạm vi; **không biến thể nào có sao cứu giải**.

| Biến thể | Sách · trang | Điều kiện (giữ từ gốc hoặc thêm theo sách) | Lõi | Giả định cách đọc |
|---|---|---|---|---|
| `TU_PHU_VU_TUONG@kl_132_193` | TH tr.72, KL tr.132, KL tr.193, KL tr.222 | boos:ta_huu_hoi, boos:xuong_khuc_hoi, refu:tuan_triet_an_ngu | như gốc | 4 sao trong tam phương của Mệnh là cách mô hình hóa; sách chỉ nêu tên cách, không nêu vị trí; phạm vi hội của sao không được câu sách nêu; đọc là tam phương; phạm vi hội của sao không được câu sách nêu; đọc là tam phương; sách nói Xương Khúc, baseline chấp nhận một trong hai; KL tr.222 nói về Vũ Tướng; áp cho cả cách là mở rộng |
| `TU_PHU_VU_TUONG@th_115` | TH tr.72, TH tr.115, TH tr.94, TH tr.95 | boos:ta_huu_hoi, boos:loc_hoi, refu:tuan_triet_an_ngu | như gốc | 4 sao trong tam phương của Mệnh là cách mô hình hóa; sách chỉ nêu tên cách, không nêu vị trí; TH tr.115 nói về đại tiểu hạn, không về bản cách; phạm vi hội của sao không được câu sách nêu; đọc là tam phương; TH tr.94-95 nói về từng sao Phủ/Tướng, không về cả cách |
| `TU_PHU_DONG_CUNG@tt_22` | TH tr.72, TT tr.22, TT tr.22, KL tr.55 | boos:ta_huu_hoi, brea:sat_dong_cung, refu:tuan_triet_an_ngu | như gốc | TH tr.72 cho phép đóng ở Mệnh hay Thân; mô hình chỉ neo ở Mệnh; TT tr.22 còn nhắc Tỵ/Hợi mà mô hình không có Tử Phủ đồng cung ở đó; phạm vi hội của sao không được câu sách nêu; đọc là tam phương; câu TT là 'dựa vào', bản dịch ghi 'cần dựa vào hai sao'; 'gặp sát tinh' đọc là đồng cung (cách hẹp nhất); tập sáu sát tinh là của baseline; nguồn là KL, không phải TT; TT tr.22/tr.160 cùng ý 'hiềm Triệt Tuần' nhưng chưa trích |
| `TU_PHU_DONG_CUNG@kl_50` | TH tr.72, KL tr.55, KL tr.50, KL tr.96, KL tr.50 | boos:xuong_khuc_hoi, boos:khoi_viet_hoi, boos:hoa_khoa_hoi, boos:kinh_luc_si_dong_cung, boos:ky_quyen_dong_cung, refu:tuan_triet_an_ngu | như gốc | TH tr.72 cho phép đóng ở Mệnh hay Thân; mô hình chỉ neo ở Mệnh; phạm vi hội của sao không được câu sách nêu; đọc là tam phương; sách nói 'Xương Khúc', baseline chấp nhận một trong hai; phạm vi hội của sao không được câu sách nêu; đọc là tam phương; sách nói 'Thiên Việt, Thiên Khôi', baseline chấp nhận một trong hai; phạm vi hội của sao không được câu sách nêu; đọc là tam phương; 'đi với Hóa Khoa' được đọc là Hóa Khoa trong tam phương |
| `CO_NGUYET_DONG_LUONG@tt_24` | TT tr.24, TH tr.77, TT tr.24 | boos:cat_tinh_hoi, brea:khong_kiep_trong_tam_phuong, brea:ky_trong_tam_phuong | như gốc | TT tr.24 cho Mệnh hoặc Thân; mô hình chỉ neo ở Mệnh; tập sáu cát tinh và phạm vi hội là của baseline; sách chỉ nói 'cát tinh trợ lực'; câu liệt kê Kiếp, Không, Kị; hiểu là một trong số đó là đủ |
| `CO_NGUYET_DONG_LUONG@kl_221` | KL tr.51, KL tr.221, KL tr.221 | boos:cat_tinh_hoi, boos:khoa_quyen_loc_hoi | như gốc | KL tr.51 chỉ nói 'hội chiếu'; mô hình neo ở Mệnh, tam phương; tập sáu cát tinh của baseline khác danh sách của KL (Tả Hữu Quang Quý Thiên quan); phạm vi hội không nêu; chữ 'Khoa' mất ở lớp chữ của trang (đọc bổ sung từ ảnh); phạm vi hội không nêu |
| `SAT_PHA_LIEM_THAM@th_76_77` | TH tr.72, TH tr.76, TH tr.77, TH tr.116 | boos:khoa_quyen_hoi, brea:ba_sat_va_ky_trong_tam_phuong | như gốc | tên cách ở TH tr.72 đọc từ ảnh; ngưỡng 3 trong 4 sao là quy ước thiết kế; sách đòi Khoa Quyền Lộc, baseline chấp nhận Khoa hoặc Quyền; phạm vi hội không nêu; 'nhiều' sát tinh → ngưỡng 3 sát tinh + Hóa Kỵ là quy ước thiết kế |
| `NHAT_NGUYET_TINH_MINH@th_72` | TH tr.72, TT tr.142, TH tr.74 | boos:nhat_nguyet_deu_sang, brea:nhat_nguyet_ham_gap_sat | lõi theo sách | nguồn là TT ('miếu vượng'); baseline dùng ngưỡng từ đắc trở lên; TH tr.74 nói Nhật/Nguyệt hãm TẠI MỆNH (không cứu tinh, hoặc hãm gặp sát tinh); baseline tính hãm + sát tinh trong tam phương; tập sáu sát tinh là của baseline |
| `NHAT_NGUYET_TINH_MINH@kl_53_68` | KL tr.53, KL tr.56, KL tr.68 | boos:nhat_nguyet_deu_sang, brea:nhat_nguyet_ham_gap_sat, refu:nhat_nguyet_ham_khong_khoi_viet | như gốc | 'hợp chiếu' mô hình là cả hai sao trong tam phương; KL nói 'đắc địa'; baseline ngưỡng từ đắc trở lên; KL liệt kê Kình Đà Không Kiếp; baseline dùng sáu sát tinh; 'gặp' không nêu phạm vi; 'Khôi Việt chiếu' đọc là hội chiếu tam phương |
| `NHAT_LE_TRUNG_THIEN@kl_52_85` | TH tr.72, KL tr.52, KL tr.85 | boos:khoa_quyen_hoi, boos:xuong_khuc_hoi | như gốc | 'thích' không nêu phạm vi; sách kể Khoa Quyền Lộc, baseline chấp nhận Khoa hoặc Quyền; 'thích' không nêu phạm vi; đọc là tam phương |
| `THACH_TRUNG_AN_NGOC@kl_44` | KL tr.44 | — | lõi theo sách | — |
| `THACH_TRUNG_AN_NGOC@kl_58` | KL tr.58, TT tr.142 | — | lõi theo sách | 'tam hợp chiếu' được mô hình là tam phương tứ chính (gồm cả đồng cung và đối cung) |
| `THACH_TRUNG_AN_NGOC@kl_106` | KL tr.106, TH tr.43 | — | lõi theo sách | 'gặp' Tuần/Triệt/Hóa Lộc được hiểu hẹp nhất là cùng cung Mệnh; sách không nêu phạm vi |
| `MA_DAU_DOI_KIEM@kl_64_xau` | KL tr.64 | brea:that_sat_thien_hinh_dong_cung | như gốc | — |
| `MA_DAU_DOI_KIEM@kl_64_tot` | KL tr.64 | boos:khoa_quyen_loc_xa_sat_hinh | như gốc | 'xa lánh' = không đồng cung; 'gặp Khoa Quyền Lộc' = hội chiếu cả ba; sách không nêu phạm vi rõ hơn |
| `TAM_KY_GIA_HOI@kl_66` | KL tr.66, TT tr.142 | brea:ky_kinh_dong_cung_hoac_doi_cung | như gốc | 'hội họp' mô hình là cả ba Hóa trong tam phương; 'chiếu' được hiểu là xung chiếu (đối cung) — cách hẹp nhất cho chữ 'chiếu'; chưa mở ra toàn tam phương vì sách không nói |
| `KHOI_VIET_GIAP_MENH@kl_44_62` | KL tr.44, KL tr.62, KL tr.62 | boos:xuong_khuc_hoi, brea:sat_tinh_hoi_chieu | như gốc | KL nói 'đồng cung hay hội chiếu' cùng Lộc Tồn; baseline tam phương, không đòi Lộc Tồn; KL tr.62 mục 4 nói Khôi Việt Ở Mệnh bị sát tinh hội chiếu, không phải Khôi Việt GIÁP Mệnh (cấu trúc khác); 'hội chiếu' = tam phương; tập sáu sát tinh là của baseline |

Mức xác minh theo TỪNG QUY TẮC (không nâng cả cách): **10** quy tắc `doi_chieu_truc_tiep` (câu trích đã được máy so với trang, không cần giả định), **37** quy tắc `co_nguon_con_gia_dinh` (có nguồn nhưng còn giả định về phạm vi/ngưỡng), **4** quy tắc `chua_du_nguon` (trang đọc từ ảnh hoặc quy ước thiết kế). Đây là đối chiếu của phiên AI, chưa có thẩm định của chuyên gia Tử Vi nên không mức nào là `verified` ở cấp cách cục.

## 3. Bảng 93 điều kiện sau hiệu chỉnh

| Cách | Vai trò | Điều kiện | Mức khớp (audit) | Số phận sau hiệu chỉnh |
|---|---|---|---|---|
| Tử Phủ Vũ Tướng | lõi | `core` | Khớp | lõi giữ nguyên ở mọi biến thể |
| Tử Phủ Vũ Tướng | tăng thế | `ta_huu_hoi` | Khớp | giữ ở: kl_132_193, th_115 |
| Tử Phủ Vũ Tướng | tăng thế | `xuong_khuc_hoi` | Lỏng hơn nguồn | giữ ở: kl_132_193 |
| Tử Phủ Vũ Tướng | tăng thế | `loc_hoi` | Khớp | giữ ở: th_115 |
| Tử Phủ Vũ Tướng | phá | `sat_dong_cung` | Chặt hơn nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Tử Phủ Vũ Tướng | phá | `ky_dong_cung` | Chặt hơn nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Tử Phủ Vũ Tướng | cứu | `khoa_dong_cung` | Chỉ liên quan | không vào biến thể nào (không nguồn nói sao nào cứu cách nào); chỉ còn ở giả thuyết gốc |
| Tử Phủ Vũ Tướng | cứu | `tam_hoa_hoi_cuu` | Lỏng hơn nguồn | không vào biến thể nào (không nguồn nói sao nào cứu cách nào); chỉ còn ở giả thuyết gốc |
| Tử Phủ Vũ Tướng | phản chứng | `tuan_triet_an_ngu` | Khớp | giữ ở: kl_132_193, th_115 |
| Tử Phủ Vũ Tướng | phản chứng | `Thiên_Tướng_ham` | Chỉ liên quan | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Tử Phủ đồng cung | lõi | `core` | Chặt hơn nguồn | lõi giữ nguyên ở mọi biến thể |
| Tử Phủ đồng cung | tăng thế | `ta_huu_hoi` | Khớp | giữ ở: tt_22 |
| Tử Phủ đồng cung | tăng thế | `xuong_khuc_hoi` | Lỏng hơn nguồn | giữ ở: kl_50 |
| Tử Phủ đồng cung | tăng thế | `khoi_viet_hoi` | Lỏng hơn nguồn | giữ ở: kl_50 |
| Tử Phủ đồng cung | phá | `sat_dong_cung` | Khác/ngược nguồn | giữ ở: tt_22 |
| Tử Phủ đồng cung | phá | `ky_dong_cung` | Khác/ngược nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Tử Phủ đồng cung | cứu | `khoa_dong_cung` | Chỉ liên quan | không vào biến thể nào (không nguồn nói sao nào cứu cách nào); chỉ còn ở giả thuyết gốc |
| Tử Phủ đồng cung | cứu | `tam_hoa_hoi_cuu` | Lỏng hơn nguồn | không vào biến thể nào (không nguồn nói sao nào cứu cách nào); chỉ còn ở giả thuyết gốc |
| Tử Phủ đồng cung | phản chứng | `tuan_triet_an_ngu` | Khớp | giữ ở: tt_22, kl_50 |
| Cơ Nguyệt Đồng Lương | lõi | `core` | Khớp | lõi giữ nguyên ở mọi biến thể |
| Cơ Nguyệt Đồng Lương | tăng thế | `cat_tinh_hoi` | Khớp | giữ ở: tt_24, kl_221 |
| Cơ Nguyệt Đồng Lương | tăng thế | `khoa_quyen_loc_hoi` | Khớp | giữ ở: kl_221 |
| Cơ Nguyệt Đồng Lương | phá | `khong_kiep_dong_cung` | Chặt hơn nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Cơ Nguyệt Đồng Lương | phá | `ky_dong_cung` | Chặt hơn nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Cơ Nguyệt Đồng Lương | cứu | `khoa_dong_cung` | Chỉ liên quan | không vào biến thể nào (không nguồn nói sao nào cứu cách nào); chỉ còn ở giả thuyết gốc |
| Cơ Nguyệt Đồng Lương | cứu | `tam_hoa_hoi_cuu` | Lỏng hơn nguồn | không vào biến thể nào (không nguồn nói sao nào cứu cách nào); chỉ còn ở giả thuyết gốc |
| Cơ Nguyệt Đồng Lương | phản chứng | `tuan_triet_an_ngu` | Chỉ liên quan | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Sát Phá Liêm Tham | lõi | `core` | Chỉ liên quan | lõi giữ nguyên ở mọi biến thể |
| Sát Phá Liêm Tham | tăng thế | `khoa_quyen_hoi` | Khớp | giữ ở: th_76_77 |
| Sát Phá Liêm Tham | tăng thế | `ta_huu_hoi` | Chỉ liên quan | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Sát Phá Liêm Tham | tăng thế | `xuong_khuc_hoi` | Chỉ liên quan | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Sát Phá Liêm Tham | tăng thế | `khoi_viet_hoi` | Chỉ liên quan | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Sát Phá Liêm Tham | phá | `ba_sat_va_ky_trong_tam_phuong` | Chặt hơn nguồn | giữ ở: th_76_77 |
| Sát Phá Liêm Tham | phá | `ky_dong_cung` | Chặt hơn nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Sát Phá Liêm Tham | cứu | `khoa_dong_cung` | Chỉ liên quan | không vào biến thể nào (không nguồn nói sao nào cứu cách nào); chỉ còn ở giả thuyết gốc |
| Sát Phá Liêm Tham | cứu | `tam_hoa_hoi_cuu` | Lỏng hơn nguồn | không vào biến thể nào (không nguồn nói sao nào cứu cách nào); chỉ còn ở giả thuyết gốc |
| Sát Phá Liêm Tham | phản chứng | `tuan_triet_an_ngu` | Chưa có nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Sát Phá Liêm Tham | phản chứng | `Thất_Sát_ham` | Chưa có nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Nhật Nguyệt tịnh minh | lõi | `core` | Lỏng hơn nguồn | lõi thay bằng định nghĩa nguồn ở: th_72;  |
| Nhật Nguyệt tịnh minh | tăng thế | `nhat_nguyet_deu_sang` | Khớp | giữ ở: th_72, kl_53_68 |
| Nhật Nguyệt tịnh minh | tăng thế | `ta_huu_hoi` | Chỉ liên quan | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Nhật Nguyệt tịnh minh | tăng thế | `khoa_quyen_hoi` | Chỉ liên quan | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Nhật Nguyệt tịnh minh | phá | `nhat_nguyet_ham_gap_sat` | Khớp | giữ ở: th_72, kl_53_68 |
| Nhật Nguyệt tịnh minh | phá | `ky_dong_cung` | Chỉ liên quan | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Nhật Nguyệt tịnh minh | phá | `khong_kiep_dong_cung` | Chỉ liên quan | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Nhật Nguyệt tịnh minh | cứu | `khoa_dong_cung` | Chỉ liên quan | không vào biến thể nào (không nguồn nói sao nào cứu cách nào); chỉ còn ở giả thuyết gốc |
| Nhật Nguyệt tịnh minh | cứu | `tam_hoa_hoi_cuu` | Lỏng hơn nguồn | không vào biến thể nào (không nguồn nói sao nào cứu cách nào); chỉ còn ở giả thuyết gốc |
| Nhật Nguyệt tịnh minh | phản chứng | `Thái_Dương_ham` | Chặt hơn nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Nhật Nguyệt tịnh minh | phản chứng | `Thái_Âm_ham` | Chặt hơn nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Nhật Nguyệt tịnh minh | phản chứng | `tuan_triet_an_ngu` | Khác/ngược nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Nhật lệ trung thiên | lõi | `core` | Khớp | lõi giữ nguyên ở mọi biến thể |
| Nhật lệ trung thiên | tăng thế | `ta_huu_hoi` | Chưa có nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Nhật lệ trung thiên | tăng thế | `khoa_quyen_hoi` | Khớp | giữ ở: kl_52_85 |
| Nhật lệ trung thiên | tăng thế | `xuong_khuc_hoi` | Khớp | giữ ở: kl_52_85 |
| Nhật lệ trung thiên | phá | `sat_dong_cung` | Chỉ liên quan | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Nhật lệ trung thiên | phá | `ky_dong_cung` | Chặt hơn nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Nhật lệ trung thiên | cứu | `khoa_dong_cung` | Chỉ liên quan | không vào biến thể nào (không nguồn nói sao nào cứu cách nào); chỉ còn ở giả thuyết gốc |
| Nhật lệ trung thiên | cứu | `tam_hoa_hoi_cuu` | Lỏng hơn nguồn | không vào biến thể nào (không nguồn nói sao nào cứu cách nào); chỉ còn ở giả thuyết gốc |
| Nhật lệ trung thiên | phản chứng | `tuan_triet_an_ngu` | Chưa có nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Nhật lệ trung thiên | phản chứng | `Thái_Dương_ham` | Chưa có nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Thạch trung ẩn ngọc | lõi | `core` | Khớp | lõi thay bằng định nghĩa nguồn ở: kl_44, kl_58, kl_106;  |
| Thạch trung ẩn ngọc | tăng thế | `tam_hoa_hoi_du` | Khớp | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Thạch trung ẩn ngọc | tăng thế | `ta_huu_hoi` | Chưa có nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Thạch trung ẩn ngọc | phá | `ky_hoac_kinh_dong_cung` | Chưa có nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Thạch trung ẩn ngọc | cứu | `khoa_dong_cung` | Chỉ liên quan | không vào biến thể nào (không nguồn nói sao nào cứu cách nào); chỉ còn ở giả thuyết gốc |
| Thạch trung ẩn ngọc | phản chứng | `tuan_triet_an_ngu` | Khác/ngược nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Thạch trung ẩn ngọc | phản chứng | `Cự_Môn_ham` | Chưa có nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Mã đầu đới kiếm | lõi | `core` | Khớp | lõi giữ nguyên ở mọi biến thể |
| Mã đầu đới kiếm | tăng thế | `khoa_quyen_loc_hoi` | Khớp | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Mã đầu đới kiếm | tăng thế | `ta_huu_hoi` | Chưa có nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Mã đầu đới kiếm | phá | `that_sat_trong_tam_phuong` | Lỏng hơn nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Mã đầu đới kiếm | phá | `sat_khac_dong_cung` | Chỉ liên quan | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Mã đầu đới kiếm | phá | `ky_dong_cung` | Chưa có nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Mã đầu đới kiếm | cứu | `khoa_dong_cung` | Chỉ liên quan | không vào biến thể nào (không nguồn nói sao nào cứu cách nào); chỉ còn ở giả thuyết gốc |
| Mã đầu đới kiếm | cứu | `tam_hoa_hoi_cuu` | Lỏng hơn nguồn | không vào biến thể nào (không nguồn nói sao nào cứu cách nào); chỉ còn ở giả thuyết gốc |
| Mã đầu đới kiếm | phản chứng | `tuan_triet_an_ngu` | Chưa có nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Tam kỳ gia hội | lõi | `core` | Khớp | lõi giữ nguyên ở mọi biến thể |
| Tam kỳ gia hội | tăng thế | `hoa_o_ban_cung` | Chỉ liên quan | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Tam kỳ gia hội | tăng thế | `ta_huu_hoi` | Chưa có nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Tam kỳ gia hội | tăng thế | `xuong_khuc_hoi` | Chưa có nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Tam kỳ gia hội | phá | `ky_hoac_kinh_dong_cung` | Chặt hơn nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Tam kỳ gia hội | cứu | `ta_huu_giai_ky` | Chưa có nguồn | không vào biến thể nào (không nguồn nói sao nào cứu cách nào); chỉ còn ở giả thuyết gốc |
| Tam kỳ gia hội | phản chứng | `tuan_triet_an_ngu` | Chưa có nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Khôi Việt giáp Mệnh | lõi | `core` | Khớp | lõi giữ nguyên ở mọi biến thể |
| Khôi Việt giáp Mệnh | tăng thế | `co_chinh_tinh` | Chưa có nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Khôi Việt giáp Mệnh | tăng thế | `ta_huu_hoi` | Chưa có nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Khôi Việt giáp Mệnh | tăng thế | `xuong_khuc_hoi` | Chỉ liên quan | giữ ở: kl_44_62 |
| Khôi Việt giáp Mệnh | phá | `sat_dong_cung` | Chỉ liên quan | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Khôi Việt giáp Mệnh | phá | `ky_dong_cung` | Chỉ liên quan | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Khôi Việt giáp Mệnh | cứu | `khoa_dong_cung` | Chỉ liên quan | không vào biến thể nào (không nguồn nói sao nào cứu cách nào); chỉ còn ở giả thuyết gốc |
| Khôi Việt giáp Mệnh | cứu | `tam_hoa_hoi_cuu` | Lỏng hơn nguồn | không vào biến thể nào (không nguồn nói sao nào cứu cách nào); chỉ còn ở giả thuyết gốc |
| Khôi Việt giáp Mệnh | phản chứng | `vo_chinh_dieu` | Chưa có nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |
| Khôi Việt giáp Mệnh | phản chứng | `tuan_triet_an_ngu` | Chưa có nguồn | không vào biến thể nào; chỉ còn ở giả thuyết gốc |

## 4. Ma trận bất đồng trường phái

Mỗi dòng là một điều kiện có bất đồng; cột cuối là các biến thể giữ riêng từng bên.

| Cách | Điều kiện | Bất đồng | Biến thể giữ riêng |
|---|---|---|---|
| Tử Phủ Vũ Tướng | `tuan_triet_an_ngu` | Tuần/Triệt có hai vai trò trái nhau trong sách: giải hung tinh/hãm tinh (KL p.199-201, p.85) và làm hại quý tinh (KL p.55, TH p.94-95); kết luận theo từng cách phải nêu trường phái | kl_132_193, th_115 |
| Tử Phủ đồng cung | `core` | TT p.22 nói Tử Phủ đồng cung ở Tỵ/Hợi; mô hình (và KL p.49) chỉ có ở Dần/Thân | tt_22, kl_50 |
| Tử Phủ đồng cung | `sat_dong_cung` | TT p.22 (sát tinh làm hỏng) trái KL p.50 (Kình Dương đồng cung vẫn giàu) | tt_22, kl_50 |
| Tử Phủ đồng cung | `tuan_triet_an_ngu` | Tuần/Triệt có hai vai trò trái nhau trong sách: giải hung tinh/hãm tinh (KL p.199-201, p.85) và làm hại quý tinh (KL p.55, TH p.94-95); kết luận theo từng cách phải nêu trường phái | tt_22, kl_50 |
| Cơ Nguyệt Đồng Lương | `cat_tinh_hoi` | TT p.24 / TH p.77 coi hội cát tinh vẫn chỉ ở mức công chức; KL p.221 (ảnh) nói hội Khoa Quyền Lộc, Khôi Việt, Xương Khúc thì giáo sư danh tiếng: mức 'tốt' khác nhau giữa các sách | tt_24, kl_221 |
| Cơ Nguyệt Đồng Lương | `khoa_quyen_loc_hoi` | xem cat_tinh_hoi | tt_24, kl_221 |
| Cơ Nguyệt Đồng Lương | `tuan_triet_an_ngu` | Tuần/Triệt có hai vai trò trái nhau trong sách: giải hung tinh/hãm tinh (KL p.199-201, p.85) và làm hại quý tinh (KL p.55, TH p.94-95); kết luận theo từng cách phải nêu trường phái | tt_24, kl_221 |
| Sát Phá Liêm Tham | `khoa_quyen_hoi` | TH p.76 cũng đếm Kình, Không trong nhóm cát hội; KL p.221 không coi sát tinh là yếu tố phá | th_76_77 |
| Sát Phá Liêm Tham | `ba_sat_va_ky_trong_tam_phuong` | TH p.76 xếp Kình, Không vào nhóm cát hội của SPLT, trái TH p.77 | th_76_77 |
| Sát Phá Liêm Tham | `tuan_triet_an_ngu` | Tuần/Triệt có hai vai trò trái nhau trong sách: giải hung tinh/hãm tinh (KL p.199-201, p.85) và làm hại quý tinh (KL p.55, TH p.94-95); kết luận theo từng cách phải nêu trường phái | th_76_77 |
| Nhật Nguyệt tịnh minh | `core` | TH p.72 (vị trí cố định) khác KL p.53 (hợp chiếu tịnh minh) | th_72, kl_53_68 |
| Nhật Nguyệt tịnh minh | `nhat_nguyet_deu_sang` | TT nói miếu vượng, KL nói đắc địa | th_72, kl_53_68 |
| Nhật Nguyệt tịnh minh | `Thái_Dương_ham` | Tuần/Triệt vừa cứu Nhật hãm (KL p.85) vừa hại Thái Âm (TH p.94) | th_72, kl_53_68 |
| Nhật Nguyệt tịnh minh | `tuan_triet_an_ngu` | Tuần/Triệt có hai vai trò trái nhau trong sách: giải hung tinh/hãm tinh (KL p.199-201, p.85) và làm hại quý tinh (KL p.55, TH p.94-95); kết luận theo từng cách phải nêu trường phái | th_72, kl_53_68 |
| Nhật lệ trung thiên | `tuan_triet_an_ngu` | Tuần/Triệt có hai vai trò trái nhau trong sách: giải hung tinh/hãm tinh (KL p.199-201, p.85) và làm hại quý tinh (KL p.55, TH p.94-95); kết luận theo từng cách phải nêu trường phái | kl_52_85 |
| Thạch trung ẩn ngọc | `core` | KL p.44 (Mệnh Cự, Di Cơ) / KL p.58 (cần Khoa Quyền Lộc) / KL p.106 và TH p.43 (cần Tuần Triệt hoặc Hóa Lộc) là ba điều kiện khác nhau | kl_44, kl_58, kl_106 |
| Thạch trung ẩn ngọc | `tuan_triet_an_ngu` | Tuần/Triệt có hai vai trò trái nhau trong sách: giải hung tinh/hãm tinh (KL p.199-201, p.85) và làm hại quý tinh (KL p.55, TH p.94-95); kết luận theo từng cách phải nêu trường phái | kl_44, kl_58, kl_106 |
| Mã đầu đới kiếm | `core` | KL p.64 mục 5 xấu / mục 6 tốt cùng một vị trí; TT p.142 cho rằng Kình ở Ngọ xấu | kl_64_xau, kl_64_tot |
| Tam kỳ gia hội | `core` | TH p.72 mục 12 (ba cung liền) khác KL/TT (hội trong tam phương) | kl_66 |

## 5. Tám lá số đối chứng (KL tr.237–246), trước và sau

Biến thể được viết từ trang sách, không chỉnh theo lá số. Cột sau là kết quả của biến thể; nơi hai sách cho hai kết luận thì ghi cả hai.

| Lá số | Cách | Gốc | Sách nói | Kết quả gốc | Biến thể → trạng thái |
|---|---|---|---|---|---|
| Hán Cao Tổ | TU_PHU_VU_TUONG | thanh_thuong | KL p.237: Tử Vi cư Ngọ 'đế cư đế vị', Tài Vũ Tướng, Quan Liêm Phủ: thế rất mạnh | đồng ý | kl_132_193 → thanh_thuong, th_115 → thanh_thuong |
| Hạng Võ | CO_NGUYET_DONG_LUONG | thanh | KL p.238: Tài Đồng Lương ngộ Triệt + Địa Kiếp, Quan Thái Âm ngộ Tuần: thất bại ở Ô Giang; engine chỉ tính phá đồng cung Mệnh (TT p.24 tính cả tam phương) | không khớp | tt_24 → bi_pha, kl_221 → thanh |
| Hạng Võ | TAM_KY_GIA_HOI | thanh | KL p.238: Cung Di Cự + Kỵ; cách tổng thể xấu; engine chỉ tính Kỵ/Kình đồng cung (KL p.66 tính cả chiếu) | không khớp | kl_66 → bi_pha |
| Khổng Minh | NHAT_NGUYET_TINH_MINH | thanh_thuong | KL p.240: 'Nhật Nguyệt chiếu hư không', thông minh tuyệt vời | đồng ý | kl_53_68 → thanh |
| Nữ Quý Mão | CO_NGUYET_DONG_LUONG | thanh | KL p.244: sách không gọi tên cách này | sách không xét | tt_24 → thanh, kl_221 → thanh_thuong |
| Nữ Quý Mão | KHOI_VIET_GIAP_MENH | thanh | KL p.244: sách không gọi tên cách này | sách không xét | kl_44_62 → bi_pha |
| Mậu Tý phá sản | NHAT_NGUYET_TINH_MINH | bi_pha | KL p.245: 'Âm dương lạc hãm' phá sản | đồng ý | kl_53_68 → bi_pha |
| Mậu Tý phá sản | CO_NGUYET_DONG_LUONG | thanh_thuong | KL p.246: Cơ + Hóa Kỵ + Hỏa Linh phá sản; engine không tính Kỵ/Hỏa Linh ngoài đồng cung Mệnh | không khớp | tt_24 → bi_pha, kl_221 → thanh_thuong |

Nguyên nhân thay đổi: phạm vi. Cơ Nguyệt Đồng Lương theo TT tr.24 tính Kiếp/Không/Kỵ trên cả tam phương → Hạng Võ và Mậu Tý đổi sang `bi_pha` (khớp sách); Tam kỳ gia hội theo KL tr.66 tính Kỵ/Kình ở đối cung → Hạng Võ `bi_pha` (khớp). Bản KL tr.221 của Cơ Nguyệt Đồng Lương không nêu yếu tố phá nên vẫn `thành`: bất đồng giữa các sách được giữ, không ép khớp. Khôi Việt giáp Mệnh của Nữ Quý Mão chuyển `bi_pha` do KL tr.62 (sát tinh hội chiếu), sách không đánh giá lá số này nên không phán đúng/sai.

## 6. Phạm vi kết luận hình học

- **Giả định của mô hình:** vị trí Tử Vi/Thiên Phủ (đối xứng Dần–Thân), bảng Tứ Hóa theo can năm (Thực Hành tr.21, Khảo Luận tr.196–197), công thức Tả/Hữu theo tháng và Xương/Khúc theo giờ.
- **Bất khả thi trong mô hình:** Tử Phủ đồng cung × *phá được cứu*, được test tái lập trong `test_formation_geometry.py`. Đây KHÔNG phải kết luận cổ thư: một trường phái an sao khác hoặc bảng Tứ Hóa khác (vd. Nhâm-Khoa là Tả Phụ hay Phủ, đã ghi trong tuvi.py) có thể cho kết quả khác. Trong các biến thể theo nguồn *phá được cứu* không tồn tại vì không sách nào cho phép.
- **Bốn điều kiện không thể kích hoạt** giữ nguyên, không sửa để tăng độ phủ: Thiên Tướng hãm (giới hạn vị trí sao), Thái Dương hãm ở Ngọ và Cự Môn hãm ở Tý/Ngọ (bảng miếu vượng), Tam Hóa hội cứu của Tử Phủ đồng cung (hình học).

## 7. Khả năng kích hoạt của các biến thể (quét 116,928 lá số)

| Biến thể | Các trạng thái xuất hiện |
|---|---|
| `CO_NGUYET_DONG_LUONG@kl_221` | thanh 5888, hinh_thuc 540, thanh_thuong 8260 |
| `CO_NGUYET_DONG_LUONG@tt_24` | thanh 2628, bi_pha 12060 |
| `KHOI_VIET_GIAP_MENH@kl_44_62` | bi_pha 2552, thanh 232 |
| `MA_DAU_DOI_KIEM@kl_64_tot` | thanh 56, hinh_thuc 4120 |
| `MA_DAU_DOI_KIEM@kl_64_xau` | hinh_thuc 4138, bi_pha 38 |
| `NHAT_LE_TRUNG_THIEN@kl_52_85` | thanh 232, hinh_thuc 240, thanh_thuong 200 |
| `NHAT_NGUYET_TINH_MINH@kl_53_68` | thanh 9792, bi_pha 11386, hinh_thuc 4550 |
| `NHAT_NGUYET_TINH_MINH@th_72` | thanh 3072 |
| `SAT_PHA_LIEM_THAM@th_76_77` | thanh 12901, hinh_thuc 14877, bi_pha 1550 |
| `TAM_KY_GIA_HOI@kl_66` | hinh_thuc 2894, bi_pha 1154 |
| `THACH_TRUNG_AN_NGOC@kl_106` | hinh_thuc 696 |
| `THACH_TRUNG_AN_NGOC@kl_44` | hinh_thuc 1728 |
| `THACH_TRUNG_AN_NGOC@kl_58` | hinh_thuc 32 |
| `TU_PHU_DONG_CUNG@kl_50` | thanh_thuong 604, thanh 536, hinh_thuc 780 |
| `TU_PHU_DONG_CUNG@tt_22` | hinh_thuc 1053, bi_pha 658, thanh 209 |
| `TU_PHU_VU_TUONG@kl_132_193` | thanh 4200, thanh_thuong 1744, hinh_thuc 8792 |
| `TU_PHU_VU_TUONG@th_115` | thanh 4788, thanh_thuong 688, hinh_thuc 9260 |

## 8. Điều kiện còn thiếu nguồn

| Cách | Vai trò | Điều kiện | Ghi chú |
|---|---|---|---|
| Tử Phủ Vũ Tướng | cứu | `khoa_dong_cung` | sách chỉ nói Hóa Khoa là sao giải nói chung (KL p.132), không nói Khoa có quyền cứu riêng cách cục này; không suy ra quyền cứu cách cục từ một đoạn khen sao tốt |
| Tử Phủ đồng cung | cứu | `khoa_dong_cung` | sách chỉ nói Hóa Khoa là sao giải nói chung (KL p.132), không nói Khoa có quyền cứu riêng cách cục này; không suy ra quyền cứu cách cục từ một đoạn khen sao tốt |
| Cơ Nguyệt Đồng Lương | cứu | `khoa_dong_cung` | sách chỉ nói Hóa Khoa là sao giải nói chung (KL p.132), không nói Khoa có quyền cứu riêng cách cục này; không suy ra quyền cứu cách cục từ một đoạn khen sao tốt |
| Cơ Nguyệt Đồng Lương | phản chứng | `tuan_triet_an_ngu` | TH p.94-95 chỉ nói Thái Âm, Thiên Lương gặp Tuần Triệt là bất lợi; không nói cả cách CNDL |
| Sát Phá Liêm Tham | tăng thế | `ta_huu_hoi` | danh sách cát tinh của TH p.76 là cho nhóm Thượng cách (Tử Phủ Vũ Tướng, Cơ Nguyệt, Cự Nhật...), không riêng cho SPLT |
| Sát Phá Liêm Tham | tăng thế | `xuong_khuc_hoi` | như trên |
| Sát Phá Liêm Tham | tăng thế | `khoi_viet_hoi` | như trên |
| Sát Phá Liêm Tham | cứu | `khoa_dong_cung` | sách chỉ nói Hóa Khoa là sao giải nói chung (KL p.132), không nói Khoa có quyền cứu riêng cách cục này; không suy ra quyền cứu cách cục từ một đoạn khen sao tốt |
| Sát Phá Liêm Tham | phản chứng | `tuan_triet_an_ngu` | không có trang nói Tuần/Triệt làm hại cách này; sách chỉ nói về từng sao |
| Sát Phá Liêm Tham | phản chứng | `Thất_Sát_ham` | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế |
| Nhật Nguyệt tịnh minh | tăng thế | `ta_huu_hoi` | KL p.56 nói Tả Hữu giúp Thái Âm/Vũ Khúc, không nói riêng Nhật Nguyệt tịnh minh |
| Nhật Nguyệt tịnh minh | tăng thế | `khoa_quyen_hoi` | KL p.53 mục 8 nói Khoa Quyền Lộc hợp chiếu giúp Nhật Nguyệt Sửu Mùi; chưa phải cách tịnh minh |
| Nhật Nguyệt tịnh minh | phá | `ky_dong_cung` | KL p.85 nói Thái Dương ghét Kỵ nhưng không nêu cho cách tịnh minh |
| Nhật Nguyệt tịnh minh | phá | `khong_kiep_dong_cung` | KL p.56 nói Nhật/Nguyệt HÃM gặp Không Kiếp; bản nháp áp dụng cho cả khi sáng |
| Nhật Nguyệt tịnh minh | cứu | `khoa_dong_cung` | sách chỉ nói Hóa Khoa là sao giải nói chung (KL p.132), không nói Khoa có quyền cứu riêng cách cục này; không suy ra quyền cứu cách cục từ một đoạn khen sao tốt |
| Nhật lệ trung thiên | tăng thế | `ta_huu_hoi` | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế |
| Nhật lệ trung thiên | phá | `sat_dong_cung` | KL p.85 (nói về sao Thái Dương ở mọi cung, không riêng Ngọ): Thái Dương sợ Kình, Đà, Không, Kiếp 'gặp' thì công danh trắc trở, và 'cần Tuần Triệt cứu giải' — KL nói Tuần/Triệt cứu cho Thái Dương, không cho cách Nhật lệ trung thiên; phạm vi 'gặp' không nêu |
| Nhật lệ trung thiên | cứu | `khoa_dong_cung` | sách chỉ nói Hóa Khoa là sao giải nói chung (KL p.132), không nói Khoa có quyền cứu riêng cách cục này; không suy ra quyền cứu cách cục từ một đoạn khen sao tốt |
| Nhật lệ trung thiên | phản chứng | `tuan_triet_an_ngu` | Tuần/Triệt trong sách giúp Thái Dương HÃM; với Thái Dương vượng ở Ngọ không có trang nói Tuần/Triệt gây hại |
| Nhật lệ trung thiên | phản chứng | `Thái_Dương_ham` | Không thể xảy ra: Thái Dương ở Ngọ luôn vượng theo bảng miếu vượng, nên điều kiện (bảng độ sáng) không bao giờ đúng; đây không phải lỗi logic mà là hệ quả của bảng |
| Thạch trung ẩn ngọc | tăng thế | `ta_huu_hoi` | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế |
| Thạch trung ẩn ngọc | phá | `ky_hoac_kinh_dong_cung` | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế |
| Thạch trung ẩn ngọc | cứu | `khoa_dong_cung` | sách chỉ nói Hóa Khoa là sao giải nói chung (KL p.132), không nói Khoa có quyền cứu riêng cách cục này; không suy ra quyền cứu cách cục từ một đoạn khen sao tốt |
| Thạch trung ẩn ngọc | phản chứng | `Cự_Môn_ham` | Không thể xảy ra: Cự Môn ở Tí/Ngọ luôn vượng theo bảng miếu vượng; không phải lỗi logic mà là hệ quả của bảng |
| Mã đầu đới kiếm | tăng thế | `ta_huu_hoi` | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế |
| Mã đầu đới kiếm | phá | `sat_khac_dong_cung` | KL p.60 nói 'nhiều sát tinh hội chiếu', không phải đồng cung |
| Mã đầu đới kiếm | phá | `ky_dong_cung` | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế |
| Mã đầu đới kiếm | cứu | `khoa_dong_cung` | sách chỉ nói Hóa Khoa là sao giải nói chung (KL p.132), không nói Khoa có quyền cứu riêng cách cục này; không suy ra quyền cứu cách cục từ một đoạn khen sao tốt |
| Mã đầu đới kiếm | phản chứng | `tuan_triet_an_ngu` | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế |
| Tam kỳ gia hội | tăng thế | `hoa_o_ban_cung` | TH p.72 mục 12 là cách 'Tam Hóa liên châu' (Khoa, Quyền, Lộc đi liền 3 cung, Mệnh có một hóa): cấu trúc khác Tam kỳ gia hội (cả ba Hóa hội trong tam phương) |
| Tam kỳ gia hội | tăng thế | `ta_huu_hoi` | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế |
| Tam kỳ gia hội | tăng thế | `xuong_khuc_hoi` | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế |
| Tam kỳ gia hội | cứu | `ta_huu_giai_ky` | không tìm thấy trang nói Tả Hữu giải Kỵ/Kình cho cách này |
| Tam kỳ gia hội | phản chứng | `tuan_triet_an_ngu` | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế |
| Khôi Việt giáp Mệnh | tăng thế | `co_chinh_tinh` | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế |
| Khôi Việt giáp Mệnh | tăng thế | `ta_huu_hoi` | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế |
| Khôi Việt giáp Mệnh | tăng thế | `xuong_khuc_hoi` | KL p.62 mục 2 nói Khôi Việt, Xương, Khúc, Lộc Tồn ĐỒNG CUNG hay HỘI CHIẾU Mệnh; không phải Khôi Việt GIÁP Mệnh (KL p.62 mục 3 nói riêng về 'giáp mệnh' chỉ khen 'được kính nể, yêu quí') |
| Khôi Việt giáp Mệnh | phá | `sat_dong_cung` | KL p.62 mục 4: 'Cung mệnh CÓ Khôi Việt lại bị sát tinh hội chiếu' — Khôi Việt ở Mệnh, không phải giáp Mệnh; cấu trúc khác, nên không dùng làm nguồn cho phá cách Khôi Việt giáp Mệnh |
| Khôi Việt giáp Mệnh | phá | `ky_dong_cung` | KL p.62 mục 2: Khôi Việt, Xương, Khúc, Lộc Tồn đồng cung/hội chiếu mà không bị Kỵ, Hình cản phá — cấu trúc Khôi Việt ở/hội chiếu Mệnh, không phải giáp Mệnh |
| Khôi Việt giáp Mệnh | cứu | `khoa_dong_cung` | sách chỉ nói Hóa Khoa là sao giải nói chung (KL p.132), không nói Khoa có quyền cứu riêng cách cục này; không suy ra quyền cứu cách cục từ một đoạn khen sao tốt |
| Khôi Việt giáp Mệnh | phản chứng | `vo_chinh_dieu` | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế |
| Khôi Việt giáp Mệnh | phản chứng | `tuan_triet_an_ngu` | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế |
