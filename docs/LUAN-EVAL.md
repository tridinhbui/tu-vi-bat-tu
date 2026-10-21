# Đặc trưng nội dung chương Mệnh — engine `luan`

Sinh bởi `tools/interpret/eval_distinct.ts --engine luan` (knowledge `f579e7a886c88283`). Đo **nội dung** được nói ra (khái niệm, luật), không đo câu chữ. Tất cả là kiểm tra tự động; chưa có chuyên gia chấm.

## Đặc trưng trên corpus và bộ chuẩn

| Chỉ số | corpus (1000 lá) | benchmark20 |
|---|---|---|
| Barnum: tần suất nền TB của khái niệm được nói (thấp = đặc trưng) | 42.7% | 40.5% |
| Tỉ lệ khái niệm được nói mà ≥ 50% lá số đều có | 34.1% | 30.1% |
| Căn cứ: tần suất bắn TB của luật hiếm nhất mỗi câu | 5.3% | 5.2% |
| Jaccard tập khái niệm, cùng chính tinh Mệnh (trung vị) | 0.2 | 0.176 |
| Strip test: trigram sau khi bỏ tên sao/cung, khác chính tinh (trung vị) | 0.072 | 0.068 |
| Chương rỗng | 0.0% | 0.0% |

Khái niệm được nói nhiều nhất (corpus): fin.abundance 37.2%, fin.scarcity 36.5%, career.status 33.6%, disc.diligent 27.7%, career.success 27.1%, career.obstacle 26.4%, life.hardship 26.1%, career.fame 22.4%, life.blessed 21.9%, career.authority 21.6%

## Phản thực một yếu tố (counterfactual)

| Nhóm | Số biến thể | Khái niệm đổi | Đổi đúng chỗ (luật nhắc yếu tố) | Độ giống văn với lá gốc (trigram) |
|---|---|---|---|---|
| critical (phải đổi) | 74 | 95.9% | 95.9% | 0.597 |
| inert (không được đổi) | 20 | 0.0% | — | 0.37 |

| Loại biến thể | n | đổi | đúng chỗ | giống văn |
|---|---|---|---|---|
| remove_sat | 11 | 11 | 11 | 0.235 |
| flip_dignity | 17 | 16 | 16 | 0.631 |
| remove_hoa | 9 | 9 | 9 | 0.796 |
| toggle_tuan | 20 | 18 | 18 | 0.806 |
| remove_unmentioned | 19 | 0 | 0 | 0.377 |
| add_hoa_ky | 8 | 8 | 8 | 0.695 |
| add_sat | 9 | 9 | 9 | 0.223 |
| remove_tat_ach_minor | 1 | 0 | 0 | 0.254 |

## Bộ chuẩn 20 lá: khái niệm được nói (tần suất nền)

| Lá | Khái niệm | Barnum |
|---|---|---|
| ref_cu_tuat | life.mitigated (12.0%), comm.friction (40.0%), temper.assertive (37.8%), temper.proud (59.1%), emo.melancholy (49.8%), fin.abundance (82.9%), fin.scarcity (39.6%), life.pleasure (49.9%), career.status (67.8%), life.mobility (31.4%), fin.volatile (13.9%) | 44.0% |
| triet_menh | comm.friction (40.0%), career.success (53.2%), career.obstacle (42.1%), cog.sharp (89.4%), career.authority (37.8%), temper.cunning (20.6%), values.selfish (25.1%), emo.melancholy (49.8%), life.mobility (31.4%), exp.martial (14.7%) | 40.4% |
| menh_vcd | life.indulgent (32.1%), life.pleasure (49.9%), comm.friction (40.0%), career.obstacle (42.1%), career.success (53.2%), cog.sharp (89.4%), outside.adverse (0.0%), temper.reckless (20.2%) | 40.9% |
| co_nguyet_dong_luong | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh (0.0%), cog.analytic (24.6%), spirit.unworldly (33.0%), cog.sharp (89.4%), career.authority (37.8%), career.status (67.8%), fin.scarcity (39.6%), life.transient (52.1%), fin.abundance (82.9%), fin.self_made (22.8%) | 45.0% |
| nhat_nguyet_ham | cach:CACH_X_NHAT_NGUYET_TINH_MINH:bi_pha (0.0%), life.mitigated (12.0%), emo.melancholy (49.8%), life.pleasure (49.9%), disc.diligent (32.8%), life.early_hardship (69.0%) | 35.6% |
| sat_pha_tham | life.hardship (69.7%), temper.assertive (37.8%), cog.analytic (24.6%), comm.reserved (24.7%), career.obstacle (42.1%), life.transient (52.1%), outside.favorable (0.0%), outside.adverse (0.0%) | 31.4% |
| tuan_menh | life.hardship (69.7%), disc.diligent (32.8%), temper.headstrong (52.0%), career.obstacle (42.1%), amb.material_focus (33.5%), fin.scarcity (39.6%), rel.strain (37.3%) | 43.9% |
| hoa_ky_menh | life.legal (9.5%), inner.unrest (6.2%), cog.sharp (89.4%), career.authority (37.8%), emo.melancholy (49.8%), career.success (53.2%), life.mitigated (12.0%), life.mobility (31.4%), fam.positive (0.0%) | 32.1% |
| loc_ton_menh | amb.material_focus (33.5%), amb.drive (60.9%), cog.sharp (89.4%), career.authority (37.8%), life.pleasure (49.9%), disc.diligent (32.8%), values.integrity (66.6%), career.status (67.8%), comm.friction (40.0%), life.late_bloom (41.1%) | 52.0% |
| khoi_viet_giap | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh (0.0%), cach:CACH_X_KHOI_VIET_GIAP_MENH:thanh (0.0%), cog.analytic (24.6%), spirit.unworldly (33.0%), career.success (53.2%), career.authority (37.8%), career.status (67.8%), fam.positive (0.0%) | 27.1% |
| than_menh | temper.assertive (37.8%), temper.headstrong (52.0%), presence.charm (69.4%), comm.reserved (24.7%), values.integrity (66.6%), fin.scarcity (39.6%), life.mobility (31.4%) | 45.9% |
| khong_kiep_menh | cach:CACH_X_TU_PHU_VU_TUONG:bi_pha (0.0%), life.hardship (69.7%), cog.analytic (24.6%), career.status (67.8%), values.integrity (66.6%), career.obstacle (42.1%), career.authority (37.8%), life.mitigated (12.0%), temper.reckless (20.2%), fin.windfall (2.3%) | 34.3% |
| cat_tu_hoi | life.pleasure (49.9%), disc.diligent (32.8%), life.mobility (31.4%), fin.scarcity (39.6%) | 38.4% |
| tu_vi_menh | temper.reckless (20.2%), career.fame (33.0%), emo.melancholy (49.8%), career.obstacle (42.1%), career.success (53.2%), career.status (67.8%) | 44.4% |
| tu_phu_vu_tuong | cach:CACH_X_TU_PHU_VU_TUONG:bi_pha (0.0%), comm.reserved (24.7%), values.selfish (25.1%), values.integrity (66.6%), emo.melancholy (49.8%), spirit.unworldly (33.0%), fin.abundance (82.9%), fin.scarcity (39.6%), life.early_hardship (69.0%), career.status (67.8%), exp.versatile (2.6%) | 41.9% |
| kinh_ngo | cach:CACH_X_MA_DAU_DOI_KIEM:thanh (0.0%), cach:CACH_X_THACH_TRUNG_AN_NGOC:bi_pha (0.0%), comm.persuasive (14.8%), fin.abundance (82.9%), disc.diligent (32.8%), temper.proud (59.1%), exp.martial (14.7%), life.mitigated (12.0%) | 27.0% |
| sat_nang_ham | cach:CACH_X_CO_NGUYET_DONG_LUONG:bi_pha (0.0%), cach:CACH_X_NHAT_NGUYET_TINH_MINH:bi_pha (0.0%), temper.assertive (37.8%), disc.diligent (32.8%), life.mitigated (12.0%), career.success (53.2%), career.obstacle (42.1%), career.fame (33.0%), career.authority (37.8%), inner.unrest (6.2%) | 25.5% |
| cu_ty_ngo | comm.persuasive (14.8%), fin.abundance (82.9%), fin.scarcity (39.6%), career.obstacle (42.1%), emo.melancholy (49.8%), values.kind (76.7%), rel.harmony (28.1%) | 47.7% |
| tam_hoa_hoi | cach:CACH_X_CO_NGUYET_DONG_LUONG:pha_duoc_cuu (0.0%), cach:CACH_X_NHAT_NGUYET_TINH_MINH:pha_duoc_cuu (0.0%), cog.sharp (89.4%), cog.analytic (24.6%), comm.reserved (24.7%), career.success (53.2%), life.transient (52.1%), inner.unrest (6.2%), outside.adverse (0.0%), outside.favorable (0.0%) | 25.0% |
| nhat_nguyet_sang | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh_thuong (0.0%), inner.peace (7.7%), fin.abundance (82.9%), inner.unrest (6.2%), emo.cheerful (16.6%), career.status (67.8%) | 30.2% |

## Chi tiết biến thể

| Lá gốc | Biến thể | Kỳ vọng | Đổi | Đúng chỗ | Giống văn | Thêm | Bớt |
|---|---|---|---|---|---|---|---|
| ref_cu_tuat | bỏ Kình Dương khỏi Mệnh | critical | có | có | 0.235 |  | temper.assertive, temper.proud |
| ref_cu_tuat | Cự Môn: hãm → miếu | critical | có | có | 0.612 | disc.diligent | emo.melancholy, fin.volatile |
| ref_cu_tuat | bỏ Hóa Lộc (Cự Môn) khỏi Mệnh | critical | có | có | 0.431 | cog.suspicious | life.mitigated, emo.melancholy, life.pleasure, fin.volatile |
| ref_cu_tuat | bỏ Tuần ở Mệnh | critical | có | có | 0.869 |  | emo.melancholy |
| ref_cu_tuat | bỏ Thai Phụ (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.295 |  |  |
| triet_menh | bỏ Địa Không khỏi Mệnh | critical | có | có | 0.324 |  | temper.cunning, values.selfish |
| triet_menh | Thiên Cơ: vượng → hãm | critical | có | có | 0.666 | life.mitigated, life.hardship | cog.sharp, career.authority, life.mobility |
| triet_menh | đặt Hóa Kỵ lên Thiên Cơ ở Mệnh | critical | có | có | 0.745 | life.mitigated | values.selfish |
| triet_menh | thêm Tuần ở Mệnh | critical | không | — | 0.956 |  |  |
| triet_menh | bỏ Thiên Đức (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.244 |  |  |
| menh_vcd | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.231 | temper.proud, temper.headstrong | cog.sharp |
| menh_vcd | thêm Tuần ở Mệnh | critical | có | có | 0.74 | fin.scarcity, emo.melancholy, fin.abundance | cog.sharp |
| menh_vcd | bỏ Thiên Khốc (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.465 |  |  |
| co_nguyet_dong_luong | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.258 | temper.headstrong |  |
| co_nguyet_dong_luong | Thiên Cơ: None → hãm | critical | có | có | 0.405 | life.mitigated, emo.melancholy, life.mobility, fin.volatile | spirit.unworldly, cog.sharp, life.transient, fin.self_made |
| co_nguyet_dong_luong | bỏ Hóa Khoa (Thiên Lương) khỏi Mệnh | critical | có | có | 0.823 |  | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh |
| co_nguyet_dong_luong | bỏ Tuần ở Mệnh | critical | có | có | 0.826 | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh_thuong | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh |
| co_nguyet_dong_luong | bỏ Thai Phụ (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.254 |  |  |
| nhat_nguyet_ham | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.223 | temper.cunning, temper.proud, values.integrity | life.pleasure |
| nhat_nguyet_ham | Thái Dương: hãm → miếu | critical | có | có | 0.431 | life.blessed, temper.assertive, life.transient, exp.versatile | emo.melancholy, life.early_hardship |
| nhat_nguyet_ham | bỏ Hóa Lộc (Thái Dương) khỏi Mệnh | critical | có | có | 0.8 |  | life.pleasure |
| nhat_nguyet_ham | thêm Tuần ở Mệnh | critical | có | có | 0.848 | fin.scarcity |  |
| nhat_nguyet_ham | bỏ Long Đức (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.492 |  |  |
| sat_pha_tham | bỏ Địa Kiếp khỏi Mệnh | critical | có | có | 0.187 | career.success, emo.melancholy | life.hardship, cog.analytic, comm.reserved, life.transient |
| sat_pha_tham | Thất Sát: miếu → hãm | critical | có | có | 0.706 | comm.friction, life.mobility | temper.assertive, life.transient |
| sat_pha_tham | đặt Hóa Kỵ lên Thất Sát ở Mệnh | critical | có | có | 0.807 | cach:CACH_X_SAT_PHA_LIEM_THAM:bi_pha, life.mitigated |  |
| sat_pha_tham | thêm Tuần ở Mệnh | critical | có | có | 0.919 | fin.scarcity |  |
| sat_pha_tham | bỏ Quốc Ấn (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.582 |  |  |
| tuan_menh | bỏ Đà La khỏi Mệnh | critical | có | có | 0.205 | adapt.flexible | life.hardship, temper.headstrong |
| tuan_menh | bỏ Tuần ở Mệnh | critical | có | có | 0.808 |  | fin.scarcity |
| tuan_menh | bỏ Thai Phụ (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.192 |  |  |
| hoa_ky_menh | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.249 | temper.headstrong |  |
| hoa_ky_menh | Thiên Cơ: vượng → hãm | critical | có | có | 0.625 | life.hardship | cog.sharp, career.authority, life.mobility |
| hoa_ky_menh | bỏ Hóa Khoa (Thiên Cơ) khỏi Mệnh | critical | có | có | 0.828 |  | career.success |
| hoa_ky_menh | thêm Tuần ở Mệnh | critical | có | có | 0.841 | fin.scarcity |  |
| hoa_ky_menh | bỏ Long Trì (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.426 |  |  |
| loc_ton_menh | bỏ Hỏa Tinh khỏi Mệnh | critical | có | có | 0.212 |  | values.integrity |
| loc_ton_menh | Thiên Cơ: vượng → hãm | critical | có | có | 0.595 | comm.reserved, life.hardship, career.fame | cog.sharp, career.authority, life.pleasure, life.late_bloom |
| loc_ton_menh | bỏ Hóa Lộc (Thiên Cơ) khỏi Mệnh | critical | có | có | 0.605 |  | amb.material_focus, amb.drive |
| loc_ton_menh | thêm Tuần ở Mệnh | critical | có | có | 0.888 | fin.scarcity, life.mobility | life.late_bloom |
| loc_ton_menh | bỏ Long Trì (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.463 |  |  |
| khoi_viet_giap | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.255 | cach:CACH_X_KHOI_VIET_GIAP_MENH:bi_pha, temper.assertive | cach:CACH_X_KHOI_VIET_GIAP_MENH:thanh |
| khoi_viet_giap | Thiên Cơ: None → hãm | critical | có | có | 0.555 | temper.cunning, fin.abundance, fin.scarcity | spirit.unworldly, career.authority |
| khoi_viet_giap | bỏ Hóa Quyền (Thiên Cơ) khỏi Mệnh | critical | có | có | 0.904 |  | career.status |
| khoi_viet_giap | thêm Tuần ở Mệnh | critical | có | có | 0.619 | life.hardship, career.obstacle, fin.scarcity | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh, cach:CACH_X_KHOI_VIET_GIAP_MENH:thanh, career.authority |
| khoi_viet_giap | bỏ Phượng Các (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.288 |  |  |
| than_menh | bỏ Hỏa Tinh khỏi Mệnh | critical | có | có | 0.223 |  | values.integrity |
| than_menh | Vũ Khúc: None → hãm | critical | có | có | 0.711 | life.hardship, career.fame |  |
| than_menh | đặt Hóa Kỵ lên Vũ Khúc ở Mệnh | critical | có | có | 0.804 | cach:CACH_X_SAT_PHA_LIEM_THAM:bi_pha, life.mitigated |  |
| than_menh | bỏ Tuần ở Mệnh | critical | có | có | 0.879 |  | fin.scarcity |
| than_menh | bỏ Thiên Sứ khỏi Tật Ách | inert | không | — | 0.254 |  |  |
| khong_kiep_menh | bỏ Địa Không khỏi Mệnh | critical | có | có | 0.244 |  | life.hardship, cog.analytic |
| khong_kiep_menh | Liêm Trinh: miếu → hãm | critical | có | có | 0.692 | inner.unrest, fin.scarcity, fin.abundance, life.transient | life.hardship, values.integrity |
| khong_kiep_menh | bỏ Hóa Kỵ (Liêm Trinh) khỏi Mệnh | critical | có | có | 0.919 |  | life.mitigated |
| khong_kiep_menh | thêm Tuần ở Mệnh | critical | có | có | 0.644 | emo.melancholy |  |
| khong_kiep_menh | bỏ Thiên Hư (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.278 |  |  |
| cat_tu_hoi | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.171 | temper.headstrong, temper.proud |  |
| cat_tu_hoi | Thiên Tướng: hãm → miếu | critical | có | có | 0.499 | life.blessed, life.hardship, fin.abundance | life.pleasure |
| cat_tu_hoi | đặt Hóa Kỵ lên Thiên Tướng ở Mệnh | critical | có | có | 0.71 | life.mitigated |  |
| cat_tu_hoi | thêm Tuần ở Mệnh | critical | có | có | 0.636 | career.obstacle |  |
| cat_tu_hoi | bỏ Long Đức (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.341 |  |  |
| tu_vi_menh | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.239 | temper.assertive |  |
| tu_vi_menh | Tử Vi: đắc → hãm | critical | không | — | 0.98 |  |  |
| tu_vi_menh | đặt Hóa Kỵ lên Tử Vi ở Mệnh | critical | có | có | 0.899 | cach:CACH_X_SAT_PHA_LIEM_THAM:bi_pha |  |
| tu_vi_menh | thêm Tuần ở Mệnh | critical | có | có | 0.887 | fin.scarcity |  |
| tu_vi_menh | bỏ Quốc Ấn (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.56 |  |  |
| tu_phu_vu_tuong | bỏ Linh Tinh khỏi Mệnh | critical | có | có | 0.367 | cach:CACH_X_TU_PHU_VU_TUONG:thanh | cach:CACH_X_TU_PHU_VU_TUONG:bi_pha, values.integrity |
| tu_phu_vu_tuong | Vũ Khúc: None → hãm | critical | có | có | 0.577 | temper.proud, values.kind, life.hardship, life.blessed, career.fame | comm.reserved, values.selfish, fin.abundance |
| tu_phu_vu_tuong | đặt Hóa Kỵ lên Vũ Khúc ở Mệnh | critical | có | có | 0.614 | values.kind, life.mitigated | comm.reserved, values.selfish |
| tu_phu_vu_tuong | bỏ Tuần ở Mệnh | critical | không | — | 0.948 |  |  |
| tu_phu_vu_tuong | bỏ Tam Thai (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.362 |  |  |
| kinh_ngo | bỏ Kình Dương khỏi Mệnh | critical | có | có | 0.158 | comm.friction | cach:CACH_X_MA_DAU_DOI_KIEM:thanh, cach:CACH_X_THACH_TRUNG_AN_NGOC:bi_pha, disc.diligent, temper.proud |
| kinh_ngo | Cự Môn: vượng → hãm | critical | có | có | 0.584 | cog.suspicious, cog.dull, cog.sharp | comm.persuasive, fin.abundance |
| kinh_ngo | đặt Hóa Kỵ lên Cự Môn ở Mệnh | critical | có | có | 0.582 | cach:CACH_X_MA_DAU_DOI_KIEM:bi_pha, inner.unrest, cog.fanciful | cach:CACH_X_MA_DAU_DOI_KIEM:thanh, comm.persuasive, fin.abundance |
| kinh_ngo | thêm Tuần ở Mệnh | critical | có | có | 0.77 | fin.scarcity, values.kind | cach:CACH_X_MA_DAU_DOI_KIEM:thanh |
| kinh_ngo | bỏ Thiên Khốc (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.465 |  |  |
| sat_nang_ham | bỏ Kình Dương khỏi Mệnh | critical | có | có | 0.211 | temper.reckless, temper.cunning, spirit.unworldly | temper.assertive, disc.diligent, career.success, career.obstacle, career.fame, career.authority |
| sat_nang_ham | Thái Âm: hãm → miếu | critical | có | có | 0.778 | life.blessed, life.hardship | life.mitigated |
| sat_nang_ham | bỏ Hóa Kỵ (Thái Âm) khỏi Mệnh | critical | có | có | 0.932 | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh_thuong | cach:CACH_X_CO_NGUYET_DONG_LUONG:bi_pha |
| sat_nang_ham | thêm Tuần ở Mệnh | critical | có | có | 0.938 | fin.scarcity |  |
| sat_nang_ham | bỏ Thiên Quan (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.442 |  |  |
| cu_ty_ngo | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.204 | cach:CACH_X_THACH_TRUNG_AN_NGOC:bi_pha, temper.headstrong |  |
| cu_ty_ngo | Cự Môn: vượng → hãm | critical | có | có | 0.489 | cog.suspicious, cog.dull, cog.sharp | comm.persuasive, fin.abundance, fin.scarcity |
| cu_ty_ngo | đặt Hóa Kỵ lên Cự Môn ở Mệnh | critical | có | có | 0.397 | cach:CACH_X_THACH_TRUNG_AN_NGOC:bi_pha, inner.unrest, cog.fanciful, life.mitigated | comm.persuasive, fin.abundance, fin.scarcity, emo.melancholy |
| cu_ty_ngo | bỏ Tuần ở Mệnh | critical | có | có | 0.603 | temper.assertive | fin.scarcity, career.obstacle, emo.melancholy |
| cu_ty_ngo | bỏ Long Trì (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.488 |  |  |
| tam_hoa_hoi | bỏ Địa Kiếp khỏi Mệnh | critical | có | có | 0.224 | cach:CACH_X_NHAT_NGUYET_TINH_MINH:thanh_thuong, cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh, career.fame, fin.abundance | cach:CACH_X_CO_NGUYET_DONG_LUONG:pha_duoc_cuu, cach:CACH_X_NHAT_NGUYET_TINH_MINH:pha_duoc_cuu, cog.analytic, comm.reserved, life.transient |
| tam_hoa_hoi | thêm Tuần ở Mệnh | critical | có | có | 0.891 | fin.scarcity |  |
| tam_hoa_hoi | bỏ Kiếp Sát (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.342 |  |  |
| nhat_nguyet_sang | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.178 | temper.assertive, temper.proud | emo.cheerful |
| nhat_nguyet_sang | Thái Âm: vượng → hãm | critical | có | có | 0.829 | life.mitigated | fin.abundance |
| nhat_nguyet_sang | bỏ Hóa Quyền (Thái Âm) khỏi Mệnh | critical | có | có | 0.92 | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh_thuong |
| nhat_nguyet_sang | thêm Tuần ở Mệnh | critical | có | có | 0.615 | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh, career.success, career.obstacle, emo.melancholy, life.mobility | cach:CACH_X_CO_NGUYET_DONG_LUONG:thanh_thuong, fin.abundance, emo.cheerful |
| nhat_nguyet_sang | bỏ Đường Phù (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.177 |  |  |
