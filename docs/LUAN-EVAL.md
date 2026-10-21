# Đặc trưng nội dung chương Mệnh — engine `luan`

Sinh bởi `tools/interpret/eval_distinct.ts --engine luan` (knowledge `16248b904e42c13a`). Đo **nội dung** được nói ra (khái niệm, luật), không đo câu chữ. Tất cả là kiểm tra tự động; chưa có chuyên gia chấm.

## Đặc trưng trên corpus và bộ chuẩn

| Chỉ số | corpus (1000 lá) | benchmark20 |
|---|---|---|
| Barnum: tần suất nền TB của khái niệm được nói (thấp = đặc trưng) | 42.7% | 40.5% |
| Tỉ lệ khái niệm được nói mà ≥ 50% lá số đều có | 34.1% | 30.1% |
| Căn cứ: tần suất bắn TB của luật hiếm nhất mỗi câu | 5.3% | 5.2% |
| Jaccard tập khái niệm, cùng chính tinh Mệnh (trung vị) | 0.214 | 0.182 |
| Strip test: trigram sau khi bỏ tên sao/cung, khác chính tinh (trung vị) | 0.074 | 0.071 |
| Chương rỗng | 0.0% | 0.0% |

Khái niệm được nói nhiều nhất (corpus): fin.abundance 37.2%, fin.scarcity 36.5%, career.status 33.6%, disc.diligent 27.7%, career.success 27.1%, career.obstacle 26.4%, life.hardship 26.1%, career.fame 22.4%, life.blessed 21.9%, career.authority 21.6%

## Phản thực một yếu tố (counterfactual)

| Nhóm | Số biến thể | Khái niệm đổi | Đổi đúng chỗ (luật nhắc yếu tố) | Độ giống văn với lá gốc (trigram) |
|---|---|---|---|---|
| critical (phải đổi) | 74 | 89.2% | 89.2% | 0.596 |
| inert (không được đổi) | 20 | 0.0% | — | 0.378 |

| Loại biến thể | n | đổi | đúng chỗ | giống văn |
|---|---|---|---|---|
| remove_sat | 11 | 11 | 11 | 0.233 |
| flip_dignity | 17 | 16 | 16 | 0.609 |
| remove_hoa | 9 | 6 | 6 | 0.814 |
| toggle_tuan | 20 | 17 | 17 | 0.802 |
| remove_unmentioned | 19 | 0 | 0 | 0.385 |
| add_hoa_ky | 8 | 7 | 7 | 0.713 |
| add_sat | 9 | 9 | 9 | 0.231 |
| remove_tat_ach_minor | 1 | 0 | 0 | 0.243 |

## Bộ chuẩn 20 lá: khái niệm được nói (tần suất nền)

| Lá | Khái niệm | Barnum |
|---|---|---|
| ref_cu_tuat | life.mitigated (12.0%), comm.friction (40.0%), temper.assertive (37.8%), temper.proud (59.1%), emo.melancholy (49.8%), fin.abundance (82.9%), fin.scarcity (39.6%), life.pleasure (49.9%), career.status (67.8%), life.mobility (31.4%), fin.volatile (13.9%) | 44.0% |
| triet_menh | comm.friction (40.0%), career.success (53.2%), career.obstacle (42.1%), cog.sharp (89.4%), career.authority (37.8%), temper.cunning (20.6%), values.selfish (25.1%), emo.melancholy (49.8%), life.mobility (31.4%), exp.martial (14.7%) | 40.4% |
| menh_vcd | life.indulgent (32.1%), life.pleasure (49.9%), comm.friction (40.0%), career.obstacle (42.1%), career.success (53.2%), cog.sharp (89.4%), outside.adverse (0.0%), temper.reckless (20.2%) | 40.9% |
| co_nguyet_dong_luong | cog.analytic (24.6%), spirit.unworldly (33.0%), cog.sharp (89.4%), career.authority (37.8%), career.status (67.8%), fin.scarcity (39.6%), life.transient (52.1%), fin.abundance (82.9%), fin.self_made (22.8%) | 50.0% |
| nhat_nguyet_ham | life.mitigated (12.0%), emo.melancholy (49.8%), life.pleasure (49.9%), disc.diligent (32.8%), life.early_hardship (69.0%) | 42.7% |
| sat_pha_tham | life.hardship (69.7%), temper.assertive (37.8%), cog.analytic (24.6%), comm.reserved (24.7%), career.obstacle (42.1%), life.transient (52.1%), outside.favorable (0.0%), outside.adverse (0.0%) | 31.4% |
| tuan_menh | life.hardship (69.7%), disc.diligent (32.8%), temper.headstrong (52.0%), career.obstacle (42.1%), amb.material_focus (33.5%), fin.scarcity (39.6%), rel.strain (37.3%) | 43.9% |
| hoa_ky_menh | life.legal (9.5%), inner.unrest (6.2%), cog.sharp (89.4%), career.authority (37.8%), emo.melancholy (49.8%), career.success (53.2%), life.mitigated (12.0%), life.mobility (31.4%), fam.positive (0.0%) | 32.1% |
| loc_ton_menh | amb.material_focus (33.5%), amb.drive (60.9%), cog.sharp (89.4%), career.authority (37.8%), life.pleasure (49.9%), disc.diligent (32.8%), values.integrity (66.6%), career.status (67.8%), comm.friction (40.0%), life.late_bloom (41.1%) | 52.0% |
| khoi_viet_giap | cog.analytic (24.6%), spirit.unworldly (33.0%), career.success (53.2%), career.authority (37.8%), career.status (67.8%), fam.positive (0.0%) | 36.1% |
| than_menh | temper.assertive (37.8%), temper.headstrong (52.0%), presence.charm (69.4%), comm.reserved (24.7%), values.integrity (66.6%), fin.scarcity (39.6%), life.mobility (31.4%) | 45.9% |
| khong_kiep_menh | life.hardship (69.7%), cog.analytic (24.6%), career.status (67.8%), values.integrity (66.6%), career.obstacle (42.1%), career.authority (37.8%), life.mitigated (12.0%), temper.reckless (20.2%), fin.windfall (2.3%) | 38.1% |
| cat_tu_hoi | life.pleasure (49.9%), disc.diligent (32.8%), life.mobility (31.4%), fin.scarcity (39.6%) | 38.4% |
| tu_vi_menh | temper.reckless (20.2%), career.fame (33.0%), emo.melancholy (49.8%), career.obstacle (42.1%), career.success (53.2%), career.status (67.8%) | 44.4% |
| tu_phu_vu_tuong | comm.reserved (24.7%), values.selfish (25.1%), values.integrity (66.6%), emo.melancholy (49.8%), spirit.unworldly (33.0%), fin.abundance (82.9%), fin.scarcity (39.6%), life.early_hardship (69.0%), career.status (67.8%), exp.versatile (2.6%) | 46.1% |
| kinh_ngo | comm.persuasive (14.8%), fin.abundance (82.9%), disc.diligent (32.8%), temper.proud (59.1%), exp.martial (14.7%), life.mitigated (12.0%) | 36.0% |
| sat_nang_ham | temper.assertive (37.8%), disc.diligent (32.8%), life.mitigated (12.0%), career.success (53.2%), career.obstacle (42.1%), career.fame (33.0%), career.authority (37.8%), inner.unrest (6.2%) | 31.9% |
| cu_ty_ngo | comm.persuasive (14.8%), fin.abundance (82.9%), fin.scarcity (39.6%), career.obstacle (42.1%), emo.melancholy (49.8%), values.kind (76.7%), rel.harmony (28.1%) | 47.7% |
| tam_hoa_hoi | cog.sharp (89.4%), cog.analytic (24.6%), comm.reserved (24.7%), career.success (53.2%), life.transient (52.1%), inner.unrest (6.2%), outside.adverse (0.0%), outside.favorable (0.0%) | 31.3% |
| nhat_nguyet_sang | inner.peace (7.7%), fin.abundance (82.9%), inner.unrest (6.2%), emo.cheerful (16.6%), career.status (67.8%) | 36.2% |

## Chi tiết biến thể

| Lá gốc | Biến thể | Kỳ vọng | Đổi | Đúng chỗ | Giống văn | Thêm | Bớt |
|---|---|---|---|---|---|---|---|
| ref_cu_tuat | bỏ Kình Dương khỏi Mệnh | critical | có | có | 0.228 |  | temper.assertive, temper.proud |
| ref_cu_tuat | Cự Môn: hãm → miếu | critical | có | có | 0.605 | disc.diligent | emo.melancholy, fin.volatile |
| ref_cu_tuat | bỏ Hóa Lộc (Cự Môn) khỏi Mệnh | critical | có | có | 0.429 | cog.suspicious | life.mitigated, emo.melancholy, life.pleasure, fin.volatile |
| ref_cu_tuat | bỏ Tuần ở Mệnh | critical | có | có | 0.87 |  | emo.melancholy |
| ref_cu_tuat | bỏ Thai Phụ (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.304 |  |  |
| triet_menh | bỏ Địa Không khỏi Mệnh | critical | có | có | 0.337 |  | temper.cunning, values.selfish |
| triet_menh | Thiên Cơ: vượng → hãm | critical | có | có | 0.657 | life.mitigated, life.hardship | cog.sharp, career.authority, life.mobility |
| triet_menh | đặt Hóa Kỵ lên Thiên Cơ ở Mệnh | critical | có | có | 0.742 | life.mitigated | values.selfish |
| triet_menh | thêm Tuần ở Mệnh | critical | không | — | 0.954 |  |  |
| triet_menh | bỏ Thiên Đức (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.253 |  |  |
| menh_vcd | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.24 | temper.proud, temper.headstrong | cog.sharp |
| menh_vcd | thêm Tuần ở Mệnh | critical | có | có | 0.736 | fin.scarcity, emo.melancholy, fin.abundance | cog.sharp |
| menh_vcd | bỏ Thiên Khốc (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.501 |  |  |
| co_nguyet_dong_luong | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.275 | temper.headstrong |  |
| co_nguyet_dong_luong | Thiên Cơ: None → hãm | critical | có | có | 0.365 | life.mitigated, emo.melancholy, life.mobility, fin.volatile | spirit.unworldly, cog.sharp, life.transient, fin.self_made |
| co_nguyet_dong_luong | bỏ Hóa Khoa (Thiên Lương) khỏi Mệnh | critical | không | — | 0.924 |  |  |
| co_nguyet_dong_luong | bỏ Tuần ở Mệnh | critical | không | — | 0.852 |  |  |
| co_nguyet_dong_luong | bỏ Thai Phụ (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.275 |  |  |
| nhat_nguyet_ham | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.204 | temper.cunning, temper.proud, values.integrity | life.pleasure |
| nhat_nguyet_ham | Thái Dương: hãm → miếu | critical | có | có | 0.384 | life.blessed, temper.assertive, life.transient, exp.versatile | emo.melancholy, life.early_hardship |
| nhat_nguyet_ham | bỏ Hóa Lộc (Thái Dương) khỏi Mệnh | critical | có | có | 0.777 |  | life.pleasure |
| nhat_nguyet_ham | thêm Tuần ở Mệnh | critical | có | có | 0.807 | fin.scarcity |  |
| nhat_nguyet_ham | bỏ Long Đức (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.5 |  |  |
| sat_pha_tham | bỏ Địa Kiếp khỏi Mệnh | critical | có | có | 0.198 | career.success, emo.melancholy | life.hardship, cog.analytic, comm.reserved, life.transient |
| sat_pha_tham | Thất Sát: miếu → hãm | critical | có | có | 0.682 | comm.friction, life.mobility | temper.assertive, life.transient |
| sat_pha_tham | đặt Hóa Kỵ lên Thất Sát ở Mệnh | critical | có | có | 0.869 | life.mitigated |  |
| sat_pha_tham | thêm Tuần ở Mệnh | critical | có | có | 0.911 | fin.scarcity |  |
| sat_pha_tham | bỏ Quốc Ấn (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.615 |  |  |
| tuan_menh | bỏ Đà La khỏi Mệnh | critical | có | có | 0.189 | adapt.flexible | life.hardship, temper.headstrong |
| tuan_menh | bỏ Tuần ở Mệnh | critical | có | có | 0.796 |  | fin.scarcity |
| tuan_menh | bỏ Thai Phụ (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.208 |  |  |
| hoa_ky_menh | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.265 | temper.headstrong |  |
| hoa_ky_menh | Thiên Cơ: vượng → hãm | critical | có | có | 0.59 | life.hardship | cog.sharp, career.authority, life.mobility |
| hoa_ky_menh | bỏ Hóa Khoa (Thiên Cơ) khỏi Mệnh | critical | có | có | 0.82 |  | career.success |
| hoa_ky_menh | thêm Tuần ở Mệnh | critical | có | có | 0.83 | fin.scarcity |  |
| hoa_ky_menh | bỏ Long Trì (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.457 |  |  |
| loc_ton_menh | bỏ Hỏa Tinh khỏi Mệnh | critical | có | có | 0.19 |  | values.integrity |
| loc_ton_menh | Thiên Cơ: vượng → hãm | critical | có | có | 0.583 | comm.reserved, life.hardship, career.fame | cog.sharp, career.authority, life.pleasure, life.late_bloom |
| loc_ton_menh | bỏ Hóa Lộc (Thiên Cơ) khỏi Mệnh | critical | có | có | 0.593 |  | amb.material_focus, amb.drive |
| loc_ton_menh | thêm Tuần ở Mệnh | critical | có | có | 0.883 | fin.scarcity, life.mobility | life.late_bloom |
| loc_ton_menh | bỏ Long Trì (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.464 |  |  |
| khoi_viet_giap | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.269 | temper.assertive |  |
| khoi_viet_giap | Thiên Cơ: None → hãm | critical | có | có | 0.51 | temper.cunning, fin.abundance, fin.scarcity | spirit.unworldly, career.authority |
| khoi_viet_giap | bỏ Hóa Quyền (Thiên Cơ) khỏi Mệnh | critical | có | có | 0.893 |  | career.status |
| khoi_viet_giap | thêm Tuần ở Mệnh | critical | có | có | 0.648 | life.hardship, career.obstacle, fin.scarcity | career.authority |
| khoi_viet_giap | bỏ Phượng Các (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.296 |  |  |
| than_menh | bỏ Hỏa Tinh khỏi Mệnh | critical | có | có | 0.218 |  | values.integrity |
| than_menh | Vũ Khúc: None → hãm | critical | có | có | 0.703 | life.hardship, career.fame |  |
| than_menh | đặt Hóa Kỵ lên Vũ Khúc ở Mệnh | critical | có | có | 0.85 | life.mitigated |  |
| than_menh | bỏ Tuần ở Mệnh | critical | có | có | 0.875 |  | fin.scarcity |
| than_menh | bỏ Thiên Sứ khỏi Tật Ách | inert | không | — | 0.243 |  |  |
| khong_kiep_menh | bỏ Địa Không khỏi Mệnh | critical | có | có | 0.255 |  | life.hardship, cog.analytic |
| khong_kiep_menh | Liêm Trinh: miếu → hãm | critical | có | có | 0.676 | inner.unrest, fin.scarcity, fin.abundance, life.transient | life.hardship, values.integrity |
| khong_kiep_menh | bỏ Hóa Kỵ (Liêm Trinh) khỏi Mệnh | critical | có | có | 0.917 |  | life.mitigated |
| khong_kiep_menh | thêm Tuần ở Mệnh | critical | có | có | 0.635 | emo.melancholy |  |
| khong_kiep_menh | bỏ Thiên Hư (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.264 |  |  |
| cat_tu_hoi | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.176 | temper.headstrong, temper.proud |  |
| cat_tu_hoi | Thiên Tướng: hãm → miếu | critical | có | có | 0.468 | life.blessed, life.hardship, fin.abundance | life.pleasure |
| cat_tu_hoi | đặt Hóa Kỵ lên Thiên Tướng ở Mệnh | critical | có | có | 0.698 | life.mitigated |  |
| cat_tu_hoi | thêm Tuần ở Mệnh | critical | có | có | 0.618 | career.obstacle |  |
| cat_tu_hoi | bỏ Long Đức (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.356 |  |  |
| tu_vi_menh | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.251 | temper.assertive |  |
| tu_vi_menh | Tử Vi: đắc → hãm | critical | không | — | 0.979 |  |  |
| tu_vi_menh | đặt Hóa Kỵ lên Tử Vi ở Mệnh | critical | không | — | 0.932 |  |  |
| tu_vi_menh | thêm Tuần ở Mệnh | critical | có | có | 0.882 | fin.scarcity |  |
| tu_vi_menh | bỏ Quốc Ấn (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.59 |  |  |
| tu_phu_vu_tuong | bỏ Linh Tinh khỏi Mệnh | critical | có | có | 0.366 |  | values.integrity |
| tu_phu_vu_tuong | Vũ Khúc: None → hãm | critical | có | có | 0.556 | temper.proud, values.kind, life.hardship, life.blessed, career.fame | comm.reserved, values.selfish, fin.abundance |
| tu_phu_vu_tuong | đặt Hóa Kỵ lên Vũ Khúc ở Mệnh | critical | có | có | 0.593 | values.kind, life.mitigated | comm.reserved, values.selfish |
| tu_phu_vu_tuong | bỏ Tuần ở Mệnh | critical | không | — | 0.946 |  |  |
| tu_phu_vu_tuong | bỏ Tam Thai (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.366 |  |  |
| kinh_ngo | bỏ Kình Dương khỏi Mệnh | critical | có | có | 0.172 | comm.friction | disc.diligent, temper.proud |
| kinh_ngo | Cự Môn: vượng → hãm | critical | có | có | 0.537 | cog.suspicious, cog.dull, cog.sharp | comm.persuasive, fin.abundance |
| kinh_ngo | đặt Hóa Kỵ lên Cự Môn ở Mệnh | critical | có | có | 0.614 | inner.unrest, cog.fanciful | comm.persuasive, fin.abundance |
| kinh_ngo | thêm Tuần ở Mệnh | critical | có | có | 0.789 | fin.scarcity, values.kind |  |
| kinh_ngo | bỏ Thiên Khốc (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.436 |  |  |
| sat_nang_ham | bỏ Kình Dương khỏi Mệnh | critical | có | có | 0.171 | temper.reckless, temper.cunning, spirit.unworldly | temper.assertive, disc.diligent, career.success, career.obstacle, career.fame, career.authority |
| sat_nang_ham | Thái Âm: hãm → miếu | critical | có | có | 0.743 | life.blessed, life.hardship | life.mitigated |
| sat_nang_ham | bỏ Hóa Kỵ (Thái Âm) khỏi Mệnh | critical | không | — | 0.99 |  |  |
| sat_nang_ham | thêm Tuần ở Mệnh | critical | có | có | 0.93 | fin.scarcity |  |
| sat_nang_ham | bỏ Thiên Quan (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.436 |  |  |
| cu_ty_ngo | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.224 | temper.headstrong |  |
| cu_ty_ngo | Cự Môn: vượng → hãm | critical | có | có | 0.484 | cog.suspicious, cog.dull, cog.sharp | comm.persuasive, fin.abundance, fin.scarcity |
| cu_ty_ngo | đặt Hóa Kỵ lên Cự Môn ở Mệnh | critical | có | có | 0.406 | inner.unrest, cog.fanciful, life.mitigated | comm.persuasive, fin.abundance, fin.scarcity, emo.melancholy |
| cu_ty_ngo | bỏ Tuần ở Mệnh | critical | có | có | 0.592 | temper.assertive | fin.scarcity, career.obstacle, emo.melancholy |
| cu_ty_ngo | bỏ Long Trì (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.532 |  |  |
| tam_hoa_hoi | bỏ Địa Kiếp khỏi Mệnh | critical | có | có | 0.242 | career.fame, fin.abundance | cog.analytic, comm.reserved, life.transient |
| tam_hoa_hoi | thêm Tuần ở Mệnh | critical | có | có | 0.866 | fin.scarcity |  |
| tam_hoa_hoi | bỏ Kiếp Sát (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.306 |  |  |
| nhat_nguyet_sang | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.171 | temper.assertive, temper.proud | emo.cheerful |
| nhat_nguyet_sang | Thái Âm: vượng → hãm | critical | có | có | 0.832 | life.mitigated | fin.abundance |
| nhat_nguyet_sang | bỏ Hóa Quyền (Thái Âm) khỏi Mệnh | critical | không | — | 0.984 |  |  |
| nhat_nguyet_sang | thêm Tuần ở Mệnh | critical | có | có | 0.624 | career.success, career.obstacle, emo.melancholy, life.mobility | fin.abundance, emo.cheerful |
| nhat_nguyet_sang | bỏ Đường Phù (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.16 |  |  |
