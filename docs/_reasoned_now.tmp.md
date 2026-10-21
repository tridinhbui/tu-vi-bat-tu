# Đặc trưng nội dung chương Mệnh — engine `reasoned`

Sinh bởi `tools/interpret/eval_distinct.ts --engine reasoned` (knowledge `f579e7a886c88283`). Đo **nội dung** được nói ra (khái niệm, luật), không đo câu chữ. Tất cả là kiểm tra tự động; chưa có chuyên gia chấm.

## Đặc trưng trên corpus và bộ chuẩn

| Chỉ số | corpus (1000 lá) | benchmark20 |
|---|---|---|
| Barnum: tần suất nền TB của khái niệm được nói (thấp = đặc trưng) | 47.5% | 47.6% |
| Tỉ lệ khái niệm được nói mà ≥ 50% lá số đều có | 40.5% | 37.7% |
| Căn cứ: tần suất bắn TB của luật hiếm nhất mỗi câu | 7.0% | 7.1% |
| Jaccard tập khái niệm, cùng chính tinh Mệnh (trung vị) | 0.214 | 0.176 |
| Strip test: trigram sau khi bỏ tên sao/cung, khác chính tinh (trung vị) | 0.078 | 0.068 |
| Chương rỗng | 0.0% | 0.0% |

Khái niệm được nói nhiều nhất (corpus): life.degree 39.1%, career.status 30.7%, disc.diligent 27.6%, fin.abundance 26.6%, fin.scarcity 25.2%, career.success 24.8%, career.obstacle 23.6%, career.fame 22.2%, career.authority 21.4%, life.hardship 18.8%

## Phản thực một yếu tố (counterfactual)

| Nhóm | Số biến thể | Khái niệm đổi | Đổi đúng chỗ (luật nhắc yếu tố) | Độ giống văn với lá gốc (trigram) |
|---|---|---|---|---|
| critical (phải đổi) | 74 | 95.9% | 95.9% | 0.545 |
| inert (không được đổi) | 20 | 0.0% | — | 1 |

| Loại biến thể | n | đổi | đúng chỗ | giống văn |
|---|---|---|---|---|
| remove_sat | 11 | 11 | 11 | 0.492 |
| flip_dignity | 17 | 16 | 16 | 0.365 |
| remove_hoa | 9 | 9 | 9 | 0.643 |
| toggle_tuan | 20 | 18 | 18 | 0.699 |
| remove_unmentioned | 19 | 0 | 0 | 1 |
| add_hoa_ky | 8 | 8 | 8 | 0.419 |
| add_sat | 9 | 9 | 9 | 0.624 |
| remove_tat_ach_minor | 1 | 0 | 0 | 1 |

## Bộ chuẩn 20 lá: khái niệm được nói (tần suất nền)

| Lá | Khái niệm | Barnum |
|---|---|---|
| ref_cu_tuat | life.mitigated (12.0%), comm.friction (40.0%), fin.abundance (82.9%), fin.scarcity (39.6%), life.pleasure (49.9%), temper.assertive (37.8%), temper.proud (59.1%), career.status (67.8%), emo.melancholy (49.8%), life.mobility (31.4%), life.degree (90.2%) | 51.0% |
| triet_menh | comm.friction (40.0%), career.success (53.2%), career.obstacle (42.1%), cog.sharp (89.4%), career.authority (37.8%), temper.cunning (20.6%), values.selfish (25.1%), emo.melancholy (49.8%), life.mobility (31.4%), life.degree (90.2%) | 48.0% |
| menh_vcd | life.indulgent (32.1%), life.pleasure (49.9%), comm.friction (40.0%), career.obstacle (42.1%), career.success (53.2%), cog.sharp (89.4%), life.degree (90.2%) | 56.7% |
| co_nguyet_dong_luong | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh (0.0%), cog.analytic (24.6%), spirit.unworldly (33.0%), cog.sharp (89.4%), career.authority (37.8%), career.status (67.8%), fin.scarcity (39.6%), life.transient (52.1%) | 43.0% |
| nhat_nguyet_ham | cach:CACH_X_NHAT_NGUYET_TINH_MINH:bi_pha (0.0%), life.mitigated (12.0%), emo.melancholy (49.8%), life.pleasure (49.9%), disc.diligent (32.8%), life.early_hardship (69.0%), life.degree (90.2%) | 43.4% |
| sat_pha_tham | life.hardship (69.7%), temper.assertive (37.8%), cog.analytic (24.6%), comm.reserved (24.7%), career.obstacle (42.1%), life.transient (52.1%) | 41.8% |
| tuan_menh | life.hardship (69.7%), disc.diligent (32.8%), career.obstacle (42.1%), amb.material_focus (33.5%), fin.scarcity (39.6%), temper.headstrong (52.0%), life.degree (90.2%) | 51.4% |
| hoa_ky_menh | life.legal (9.5%), inner.unrest (6.2%), cog.sharp (89.4%), career.authority (37.8%), career.success (53.2%), life.mitigated (12.0%), emo.melancholy (49.8%), life.mobility (31.4%), life.degree (90.2%) | 42.2% |
| loc_ton_menh | career.status (67.8%), comm.friction (40.0%), amb.material_focus (33.5%), amb.drive (60.9%), cog.sharp (89.4%), career.authority (37.8%), life.pleasure (49.9%), disc.diligent (32.8%), values.integrity (66.6%), life.late_bloom (41.1%) | 52.0% |
| khoi_viet_giap | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh (0.0%), cach:CACH_X_KHOI_VIET_GIAP_MENH:thanh (0.0%), cog.analytic (24.6%), spirit.unworldly (33.0%), career.success (53.2%), career.authority (37.8%), career.status (67.8%) | 30.9% |
| than_menh | temper.assertive (37.8%), temper.headstrong (52.0%), presence.charm (69.4%), comm.reserved (24.7%), fin.scarcity (39.6%), values.integrity (66.6%), life.mobility (31.4%), life.degree (90.2%) | 51.5% |
| khong_kiep_menh | cach:CACH_X_TU_PHU_VU_TUONG:bi_pha (0.0%), career.status (67.8%), values.integrity (66.6%), career.obstacle (42.1%), career.authority (37.8%), life.hardship (69.7%), cog.analytic (24.6%), life.mitigated (12.0%) | 40.1% |
| cat_tu_hoi | life.pleasure (49.9%), disc.diligent (32.8%), life.mobility (31.4%), life.degree (90.2%) | 51.1% |
| tu_vi_menh | temper.reckless (20.2%), career.fame (33.0%), career.obstacle (42.1%), career.success (53.2%), emo.melancholy (49.8%), life.degree (90.2%) | 48.1% |
| tu_phu_vu_tuong | cach:CACH_X_TU_PHU_VU_TUONG:bi_pha (0.0%), spirit.unworldly (33.0%), fin.abundance (82.9%), fin.scarcity (39.6%), comm.reserved (24.7%), values.selfish (25.1%), values.integrity (66.6%), emo.melancholy (49.8%), life.early_hardship (69.0%) | 43.4% |
| kinh_ngo | cach:CACH_X_MA_DAU_DOI_KIEM:thanh (0.0%), cach:CACH_X_THACH_TRUNG_AN_NGOC:bi_pha (0.0%), comm.persuasive (14.8%), fin.abundance (82.9%), disc.diligent (32.8%), temper.proud (59.1%), life.degree (90.2%) | 40.0% |
| sat_nang_ham | cach:CACH_X_CO_NGUYET_DONG_LUONG:bi_pha (0.0%), cach:CACH_X_NHAT_NGUYET_TINH_MINH:bi_pha (0.0%), life.mitigated (12.0%), career.success (53.2%), career.obstacle (42.1%), temper.assertive (37.8%), disc.diligent (32.8%), career.fame (33.0%), career.authority (37.8%), life.degree (90.2%) | 33.9% |
| cu_ty_ngo | comm.persuasive (14.8%), fin.abundance (82.9%), fin.scarcity (39.6%), career.obstacle (42.1%), emo.melancholy (49.8%) | 45.8% |
| tam_hoa_hoi | cach:CACH_X_CO_NGUYET_DONG_LUONG:pha_duoc_cuu (0.0%), cach:CACH_X_NHAT_NGUYET_TINH_MINH:pha_duoc_cuu (0.0%), cog.sharp (89.4%), cog.analytic (24.6%), comm.reserved (24.7%), career.success (53.2%), life.transient (52.1%) | 34.9% |
| nhat_nguyet_sang | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh_thuong (0.0%), inner.peace (7.7%), fin.abundance (82.9%), inner.unrest (6.2%), emo.cheerful (16.6%) | 22.7% |

## Chi tiết biến thể

| Lá gốc | Biến thể | Kỳ vọng | Đổi | Đúng chỗ | Giống văn | Thêm | Bớt |
|---|---|---|---|---|---|---|---|
| ref_cu_tuat | bỏ Kình Dương khỏi Mệnh | critical | có | có | 0.521 |  | temper.assertive, temper.proud |
| ref_cu_tuat | Cự Môn: hãm → miếu | critical | có | có | 0.492 | disc.diligent | fin.abundance, emo.melancholy |
| ref_cu_tuat | bỏ Hóa Lộc (Cự Môn) khỏi Mệnh | critical | có | có | 0.217 | cog.suspicious | life.mitigated, fin.abundance, life.pleasure, emo.melancholy |
| ref_cu_tuat | bỏ Tuần ở Mệnh | critical | có | có | 0.826 |  | emo.melancholy |
| ref_cu_tuat | bỏ Thai Phụ (không luật nào nhắc) khỏi Mệnh | inert | không | — | 1 |  |  |
| triet_menh | bỏ Địa Không khỏi Mệnh | critical | có | có | 0.539 |  | temper.cunning, values.selfish |
| triet_menh | Thiên Cơ: vượng → hãm | critical | có | có | 0.25 | life.mitigated, life.hardship | cog.sharp, career.authority, life.mobility |
| triet_menh | đặt Hóa Kỵ lên Thiên Cơ ở Mệnh | critical | có | có | 0.227 | life.mitigated | values.selfish |
| triet_menh | thêm Tuần ở Mệnh | critical | không | — | 0.912 |  |  |
| triet_menh | bỏ Thiên Đức (không luật nào nhắc) khỏi Mệnh | inert | không | — | 1 |  |  |
| menh_vcd | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.312 | temper.proud, temper.headstrong | cog.sharp |
| menh_vcd | thêm Tuần ở Mệnh | critical | có | có | 0.29 | fin.scarcity, emo.melancholy, fin.abundance | cog.sharp |
| menh_vcd | bỏ Thiên Khốc (không luật nào nhắc) khỏi Mệnh | inert | không | — | 1 |  |  |
| co_nguyet_dong_luong | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.904 | temper.headstrong |  |
| co_nguyet_dong_luong | Thiên Cơ: None → hãm | critical | có | có | 0.116 | life.mitigated, fin.abundance, emo.melancholy, life.mobility | spirit.unworldly, cog.sharp, life.transient |
| co_nguyet_dong_luong | bỏ Hóa Khoa (Thiên Lương) khỏi Mệnh | critical | có | có | 0.71 |  | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh |
| co_nguyet_dong_luong | bỏ Tuần ở Mệnh | critical | có | có | 0.843 | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh_thuong | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh, fin.scarcity |
| co_nguyet_dong_luong | bỏ Thai Phụ (không luật nào nhắc) khỏi Mệnh | inert | không | — | 1 |  |  |
| nhat_nguyet_ham | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.624 | temper.cunning, temper.proud, values.integrity | life.pleasure |
| nhat_nguyet_ham | Thái Dương: hãm → miếu | critical | có | có | 0.36 | life.blessed, temper.assertive, life.transient | life.mitigated, emo.melancholy, life.early_hardship |
| nhat_nguyet_ham | bỏ Hóa Lộc (Thái Dương) khỏi Mệnh | critical | có | có | 0.43 |  | life.pleasure |
| nhat_nguyet_ham | thêm Tuần ở Mệnh | critical | có | có | 0.784 | fin.scarcity |  |
| nhat_nguyet_ham | bỏ Long Đức (không luật nào nhắc) khỏi Mệnh | inert | không | — | 1 |  |  |
| sat_pha_tham | bỏ Địa Kiếp khỏi Mệnh | critical | có | có | 0.247 | career.success, emo.melancholy | life.hardship, cog.analytic, comm.reserved, life.transient |
| sat_pha_tham | Thất Sát: miếu → hãm | critical | có | có | 0.478 | comm.friction, life.mobility | temper.assertive, life.transient |
| sat_pha_tham | đặt Hóa Kỵ lên Thất Sát ở Mệnh | critical | có | có | 0.742 | cach:CACH_X_SAT_PHA_LIEM_THAM:bi_pha, life.mitigated |  |
| sat_pha_tham | thêm Tuần ở Mệnh | critical | có | có | 0.883 | fin.scarcity |  |
| sat_pha_tham | bỏ Quốc Ấn (không luật nào nhắc) khỏi Mệnh | inert | không | — | 1 |  |  |
| tuan_menh | bỏ Đà La khỏi Mệnh | critical | có | có | 0.226 | adapt.flexible | life.hardship, temper.headstrong |
| tuan_menh | bỏ Tuần ở Mệnh | critical | có | có | 0.682 |  | fin.scarcity |
| tuan_menh | bỏ Thai Phụ (không luật nào nhắc) khỏi Mệnh | inert | không | — | 1 |  |  |
| hoa_ky_menh | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.945 | temper.headstrong |  |
| hoa_ky_menh | Thiên Cơ: vượng → hãm | critical | có | có | 0.374 | life.hardship | cog.sharp, career.authority, life.mobility |
| hoa_ky_menh | bỏ Hóa Khoa (Thiên Cơ) khỏi Mệnh | critical | có | có | 0.753 |  | career.success |
| hoa_ky_menh | thêm Tuần ở Mệnh | critical | có | có | 0.86 | fin.scarcity |  |
| hoa_ky_menh | bỏ Long Trì (không luật nào nhắc) khỏi Mệnh | inert | không | — | 1 |  |  |
| loc_ton_menh | bỏ Hỏa Tinh khỏi Mệnh | critical | có | có | 0.945 |  | values.integrity |
| loc_ton_menh | Thiên Cơ: vượng → hãm | critical | có | có | 0.426 | life.hardship, career.fame, comm.reserved | cog.sharp, career.authority, life.pleasure, life.late_bloom |
| loc_ton_menh | bỏ Hóa Lộc (Thiên Cơ) khỏi Mệnh | critical | có | có | 0.245 |  | amb.material_focus, amb.drive |
| loc_ton_menh | thêm Tuần ở Mệnh | critical | có | có | 0.835 | fin.scarcity, life.mobility | life.late_bloom |
| loc_ton_menh | bỏ Long Trì (không luật nào nhắc) khỏi Mệnh | inert | không | — | 1 |  |  |
| khoi_viet_giap | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.773 | cach:CACH_X_KHOI_VIET_GIAP_MENH:bi_pha, temper.assertive | cach:CACH_X_KHOI_VIET_GIAP_MENH:thanh |
| khoi_viet_giap | Thiên Cơ: None → hãm | critical | có | có | 0.36 | temper.cunning, fin.abundance, fin.scarcity | spirit.unworldly, career.authority |
| khoi_viet_giap | bỏ Hóa Quyền (Thiên Cơ) khỏi Mệnh | critical | có | có | 0.833 |  | career.status |
| khoi_viet_giap | thêm Tuần ở Mệnh | critical | có | có | 0.375 | life.hardship, career.obstacle, fin.scarcity | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh, cach:CACH_X_KHOI_VIET_GIAP_MENH:thanh, career.authority |
| khoi_viet_giap | bỏ Phượng Các (không luật nào nhắc) khỏi Mệnh | inert | không | — | 1 |  |  |
| than_menh | bỏ Hỏa Tinh khỏi Mệnh | critical | có | có | 0.926 |  | values.integrity |
| than_menh | Vũ Khúc: None → hãm | critical | có | có | 0.525 | life.hardship, career.fame |  |
| than_menh | đặt Hóa Kỵ lên Vũ Khúc ở Mệnh | critical | có | có | 0.542 | cach:CACH_X_SAT_PHA_LIEM_THAM:bi_pha, life.mitigated |  |
| than_menh | bỏ Tuần ở Mệnh | critical | có | có | 0.889 |  | fin.scarcity |
| than_menh | bỏ Thiên Sứ khỏi Tật Ách | inert | không | — | 1 |  |  |
| khong_kiep_menh | bỏ Địa Không khỏi Mệnh | critical | có | có | 0.197 |  | life.hardship, cog.analytic |
| khong_kiep_menh | Liêm Trinh: miếu → hãm | critical | có | có | 0.238 | inner.unrest, fin.scarcity, fin.abundance, life.transient | values.integrity, life.hardship |
| khong_kiep_menh | bỏ Hóa Kỵ (Liêm Trinh) khỏi Mệnh | critical | có | có | 0.88 |  | life.mitigated |
| khong_kiep_menh | thêm Tuần ở Mệnh | critical | có | có | 0.626 | emo.melancholy |  |
| khong_kiep_menh | bỏ Thiên Hư (không luật nào nhắc) khỏi Mệnh | inert | không | — | 1 |  |  |
| cat_tu_hoi | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.225 | temper.headstrong, temper.proud |  |
| cat_tu_hoi | Thiên Tướng: hãm → miếu | critical | có | có | 0.162 | life.blessed, life.hardship, fin.abundance, fin.scarcity | life.pleasure |
| cat_tu_hoi | đặt Hóa Kỵ lên Thiên Tướng ở Mệnh | critical | có | có | 0.203 | life.mitigated |  |
| cat_tu_hoi | thêm Tuần ở Mệnh | critical | có | có | 0.222 | career.obstacle, fin.scarcity |  |
| cat_tu_hoi | bỏ Long Đức (không luật nào nhắc) khỏi Mệnh | inert | không | — | 1 |  |  |
| tu_vi_menh | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.871 | temper.assertive |  |
| tu_vi_menh | Tử Vi: đắc → hãm | critical | không | — | 0.92 |  |  |
| tu_vi_menh | đặt Hóa Kỵ lên Tử Vi ở Mệnh | critical | có | có | 0.848 | cach:CACH_X_SAT_PHA_LIEM_THAM:bi_pha |  |
| tu_vi_menh | thêm Tuần ở Mệnh | critical | có | có | 0.88 | fin.scarcity |  |
| tu_vi_menh | bỏ Quốc Ấn (không luật nào nhắc) khỏi Mệnh | inert | không | — | 1 |  |  |
| tu_phu_vu_tuong | bỏ Linh Tinh khỏi Mệnh | critical | có | có | 0.756 | cach:CACH_X_TU_PHU_VU_TUONG:thanh | cach:CACH_X_TU_PHU_VU_TUONG:bi_pha, values.integrity |
| tu_phu_vu_tuong | Vũ Khúc: None → hãm | critical | có | có | 0.211 | temper.proud, life.hardship, life.blessed, career.fame, values.kind | fin.abundance, comm.reserved, values.selfish |
| tu_phu_vu_tuong | đặt Hóa Kỵ lên Vũ Khúc ở Mệnh | critical | có | có | 0.428 | life.mitigated, values.kind | comm.reserved, values.selfish |
| tu_phu_vu_tuong | bỏ Tuần ở Mệnh | critical | không | — | 0.892 |  |  |
| tu_phu_vu_tuong | bỏ Tam Thai (không luật nào nhắc) khỏi Mệnh | inert | không | — | 1 |  |  |
| kinh_ngo | bỏ Kình Dương khỏi Mệnh | critical | có | có | 0.377 | comm.friction | cach:CACH_X_MA_DAU_DOI_KIEM:thanh, cach:CACH_X_THACH_TRUNG_AN_NGOC:bi_pha, disc.diligent, temper.proud |
| kinh_ngo | Cự Môn: vượng → hãm | critical | có | có | 0.364 | cog.suspicious, cog.dull, cog.sharp | comm.persuasive, fin.abundance |
| kinh_ngo | đặt Hóa Kỵ lên Cự Môn ở Mệnh | critical | có | có | 0.308 | cach:CACH_X_MA_DAU_DOI_KIEM:bi_pha, inner.unrest, cog.fanciful | cach:CACH_X_MA_DAU_DOI_KIEM:thanh, comm.persuasive, fin.abundance |
| kinh_ngo | thêm Tuần ở Mệnh | critical | có | có | 0.739 | fin.scarcity, values.kind | cach:CACH_X_MA_DAU_DOI_KIEM:thanh |
| kinh_ngo | bỏ Thiên Khốc (không luật nào nhắc) khỏi Mệnh | inert | không | — | 1 |  |  |
| sat_nang_ham | bỏ Kình Dương khỏi Mệnh | critical | có | có | 0.269 | spirit.unworldly, temper.reckless, temper.cunning | career.success, career.obstacle, temper.assertive, disc.diligent, career.fame, career.authority |
| sat_nang_ham | Thái Âm: hãm → miếu | critical | có | có | 0.555 | life.blessed, life.hardship | life.mitigated |
| sat_nang_ham | bỏ Hóa Kỵ (Thái Âm) khỏi Mệnh | critical | có | có | 0.882 | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh_thuong | cach:CACH_X_CO_NGUYET_DONG_LUONG:bi_pha |
| sat_nang_ham | thêm Tuần ở Mệnh | critical | có | có | 0.939 | fin.scarcity |  |
| sat_nang_ham | bỏ Thiên Quan (không luật nào nhắc) khỏi Mệnh | inert | không | — | 1 |  |  |
| cu_ty_ngo | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.809 | cach:CACH_X_THACH_TRUNG_AN_NGOC:bi_pha, temper.headstrong |  |
| cu_ty_ngo | Cự Môn: vượng → hãm | critical | có | có | 0.176 | cog.suspicious, cog.dull, cog.sharp | comm.persuasive, fin.abundance, fin.scarcity |
| cu_ty_ngo | đặt Hóa Kỵ lên Cự Môn ở Mệnh | critical | có | có | 0.056 | cach:CACH_X_THACH_TRUNG_AN_NGOC:bi_pha, inner.unrest, cog.fanciful, life.mitigated | comm.persuasive, fin.abundance, fin.scarcity, emo.melancholy |
| cu_ty_ngo | bỏ Tuần ở Mệnh | critical | có | có | 0.401 | temper.assertive | fin.scarcity, career.obstacle, emo.melancholy |
| cu_ty_ngo | bỏ Long Trì (không luật nào nhắc) khỏi Mệnh | inert | không | — | 1 |  |  |
| tam_hoa_hoi | bỏ Địa Kiếp khỏi Mệnh | critical | có | có | 0.411 | cach:CACH_X_NHAT_NGUYET_TINH_MINH:thanh_thuong, cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh, career.fame, fin.abundance | cach:CACH_X_CO_NGUYET_DONG_LUONG:pha_duoc_cuu, cach:CACH_X_NHAT_NGUYET_TINH_MINH:pha_duoc_cuu, cog.analytic, comm.reserved, life.transient |
| tam_hoa_hoi | thêm Tuần ở Mệnh | critical | có | có | 0.956 | fin.scarcity |  |
| tam_hoa_hoi | bỏ Kiếp Sát (không luật nào nhắc) khỏi Mệnh | inert | không | — | 1 |  |  |
| nhat_nguyet_sang | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.153 | temper.assertive, temper.proud | emo.cheerful |
| nhat_nguyet_sang | Thái Âm: vượng → hãm | critical | có | có | 0.197 | life.mitigated | fin.abundance |
| nhat_nguyet_sang | bỏ Hóa Quyền (Thái Âm) khỏi Mệnh | critical | có | có | 0.835 | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh_thuong |
| nhat_nguyet_sang | thêm Tuần ở Mệnh | critical | có | có | 0.14 | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh, career.success, career.obstacle, emo.melancholy, life.mobility | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh_thuong, fin.abundance, emo.cheerful |
| nhat_nguyet_sang | bỏ Đường Phù (không luật nào nhắc) khỏi Mệnh | inert | không | — | 1 |  |  |
