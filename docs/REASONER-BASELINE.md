# Đặc trưng nội dung chương Mệnh — engine `old`

Sinh bởi `tools/interpret/eval_distinct.ts --engine old` (knowledge `4db446cf1b5653fc`). Đo **nội dung** được nói ra (khái niệm, luật), không đo câu chữ. Tất cả là kiểm tra tự động; chưa có chuyên gia chấm.

## Đặc trưng trên corpus và bộ chuẩn

| Chỉ số | corpus (1000 lá) | benchmark20 |
|---|---|---|
| Barnum: tần suất nền TB của khái niệm được nói (thấp = đặc trưng) | 56.6% | 56.3% |
| Tỉ lệ khái niệm được nói mà ≥ 50% lá số đều có | 60.1% | 59.5% |
| Căn cứ: tần suất bắn TB của luật hiếm nhất mỗi câu | 8.2% | 7.6% |
| Jaccard tập khái niệm, cùng chính tinh Mệnh (trung vị) | 0.444 | 0.364 |
| Strip test: trigram sau khi bỏ tên sao/cung, khác chính tinh (trung vị) | 0.054 | 0.054 |
| Chương rỗng | 0.0% | 0.0% |

Khái niệm được nói nhiều nhất (corpus): life.degree 100.0%, cog.sharp 72.2%, values.kind 58.5%, adapt.unsteady 44.1%, temper.headstrong 39.3%, career.early 37.1%, temper.proud 32.9%, life.mobility 31.4%, amb.drive 30.0%, values.integrity 29.4%

## Phản thực một yếu tố (counterfactual)

| Nhóm | Số biến thể | Khái niệm đổi | Đổi đúng chỗ (luật nhắc yếu tố) | Độ giống văn với lá gốc (trigram) |
|---|---|---|---|---|
| critical (phải đổi) | 74 | 73.0% | 73.0% | 0.59 |
| inert (không được đổi) | 20 | 30.0% | — | 0.199 |

| Loại biến thể | n | đổi | đúng chỗ | giống văn |
|---|---|---|---|---|
| remove_sat | 11 | 11 | 11 | 0.098 |
| flip_dignity | 17 | 14 | 14 | 0.651 |
| remove_hoa | 9 | 2 | 2 | 0.912 |
| toggle_tuan | 20 | 16 | 16 | 0.754 |
| remove_unmentioned | 19 | 6 | 0 | 0.202 |
| add_hoa_ky | 8 | 3 | 3 | 0.903 |
| add_sat | 9 | 8 | 8 | 0.108 |
| remove_tat_ach_minor | 1 | 0 | 0 | 0.15 |

## Bộ chuẩn 20 lá: khái niệm được nói (tần suất nền)

| Lá | Khái niệm | Barnum |
|---|---|---|
| ref_cu_tuat | cog.suspicious (9.6%), comm.friction (40.0%), cog.sharp (89.4%), life.hardship (69.7%), life.mitigated (12.0%), life.early_hardship (69.0%), temper.assertive (37.8%), temper.proud (59.1%), life.pleasure (49.9%), values.kind (76.7%), temper.headstrong (52.0%), life.degree (90.2%), life.mobility (31.4%) | 52.8% |
| triet_menh | cog.sharp (89.4%), temper.cunning (20.6%), comm.friction (40.0%), career.early (59.3%), comm.persuasive (14.8%), values.kind (76.7%), temper.headstrong (52.0%), life.degree (90.2%), life.mobility (31.4%), life.transient (52.1%) | 52.6% |
| menh_vcd | cog.sharp (89.4%), life.indulgent (32.1%), adapt.unsteady (57.5%), life.late_bloom (41.1%), cog.analytic (24.6%), comm.reserved (24.7%), comm.friction (40.0%), life.degree (90.2%) | 50.0% |
| co_nguyet_dong_luong | values.kind (76.7%), life.early_hardship (69.0%), emo.melancholy (49.8%), cog.sharp (89.4%), values.integrity (66.6%), life.degree (90.2%), life.mobility (31.4%), life.transient (52.1%) | 65.6% |
| nhat_nguyet_ham | values.kind (76.7%), adapt.unsteady (57.5%), emo.melancholy (49.8%), life.early_hardship (69.0%), cog.sharp (89.4%), values.integrity (66.6%), cog.dull (14.9%), life.degree (90.2%), life.late_bloom (41.1%), life.mobility (31.4%) | 58.7% |
| sat_pha_tham | temper.assertive (37.8%), life.early_hardship (69.0%), temper.headstrong (52.0%), comm.friction (40.0%), cog.sharp (89.4%), amb.drive (60.9%), cog.analytic (24.6%), adapt.unsteady (57.5%), life.degree (90.2%), life.transient (52.1%) | 57.4% |
| tuan_menh | adapt.flexible (48.5%), temper.proud (59.1%), temper.headstrong (52.0%), life.early_hardship (69.0%), amb.drive (60.9%), cog.sharp (89.4%), comm.friction (40.0%), life.degree (90.2%) | 63.6% |
| hoa_ky_menh | cog.sharp (89.4%), comm.friction (40.0%), inner.unrest (6.2%), life.early_hardship (69.0%), comm.persuasive (14.8%), values.kind (76.7%), cog.fanciful (9.6%), life.degree (90.2%), life.mobility (31.4%), life.late_bloom (41.1%) | 46.8% |
| loc_ton_menh | cog.sharp (89.4%), life.late_bloom (41.1%), temper.headstrong (52.0%), values.kind (76.7%), comm.persuasive (14.8%), values.integrity (66.6%), temper.hot (29.2%), life.pleasure (49.9%), comm.friction (40.0%), life.degree (90.2%), life.mobility (31.4%) | 52.8% |
| khoi_viet_giap | values.kind (76.7%), career.late (27.8%), adapt.unsteady (57.5%), cog.sharp (89.4%), values.integrity (66.6%), presence.charm (69.4%), comm.friction (40.0%), life.degree (90.2%) | 64.7% |
| than_menh | temper.assertive (37.8%), temper.headstrong (52.0%), comm.friction (40.0%), values.integrity (66.6%), temper.hot (29.2%), life.early_hardship (69.0%), amb.drive (60.9%), cog.sharp (89.4%), adapt.unsteady (57.5%), life.degree (90.2%), life.mobility (31.4%), life.late_bloom (41.1%) | 55.4% |
| khong_kiep_menh | values.integrity (66.6%), career.early (59.3%), temper.hot (29.2%), cog.analytic (24.6%), comm.reserved (24.7%), cog.sharp (89.4%), temper.assertive (37.8%), adapt.unsteady (57.5%), life.degree (90.2%), life.transient (52.1%) | 53.1% |
| cat_tu_hoi | values.kind (76.7%), life.pleasure (49.9%), values.integrity (66.6%), career.late (27.8%), cog.sharp (89.4%), life.degree (90.2%), life.mobility (31.4%) | 61.7% |
| tu_vi_menh | amb.drive (60.9%), life.early_hardship (69.0%), temper.proud (59.1%), temper.reckless (20.2%), temper.assertive (37.8%), cog.sharp (89.4%), temper.headstrong (52.0%), life.degree (90.2%), life.transient (52.1%), life.mobility (31.4%) | 56.2% |
| tu_phu_vu_tuong | spirit.unworldly (33.0%), temper.proud (59.1%), values.integrity (66.6%), temper.hot (29.2%), life.early_hardship (69.0%), values.kind (76.7%), cog.sharp (89.4%), emo.melancholy (49.8%), life.degree (90.2%), life.late_bloom (41.1%), life.transient (52.1%) | 59.7% |
| kinh_ngo | comm.persuasive (14.8%), career.late (27.8%), comm.friction (40.0%), temper.headstrong (52.0%), cog.sharp (89.4%), disc.diligent (32.8%), adapt.unsteady (57.5%), life.degree (90.2%) | 50.6% |
| sat_nang_ham | cog.sharp (89.4%), temper.headstrong (52.0%), temper.proud (59.1%), temper.assertive (37.8%), career.early (59.3%), amb.material_focus (33.5%), spirit.unworldly (33.0%), life.indulgent (32.1%), life.degree (90.2%) | 54.0% |
| cu_ty_ngo | cog.sharp (89.4%), life.early_hardship (69.0%), temper.headstrong (52.0%), comm.persuasive (14.8%), amb.drive (60.9%), temper.proud (59.1%), life.degree (90.2%) | 62.2% |
| tam_hoa_hoi | adapt.unsteady (57.5%), cog.analytic (24.6%), comm.reserved (24.7%), career.early (59.3%), cog.sharp (89.4%), temper.assertive (37.8%), emo.melancholy (49.8%), life.degree (90.2%), life.transient (52.1%) | 53.9% |
| nhat_nguyet_sang | cog.sharp (89.4%), inner.peace (7.7%), amb.material_focus (33.5%), career.early (59.3%), life.pleasure (49.9%), life.degree (90.2%) | 55.0% |

## Chi tiết biến thể

| Lá gốc | Biến thể | Kỳ vọng | Đổi | Đúng chỗ | Giống văn | Thêm | Bớt |
|---|---|---|---|---|---|---|---|
| ref_cu_tuat | bỏ Kình Dương khỏi Mệnh | critical | có | có | 0.085 | cog.dull | temper.assertive, temper.proud, temper.headstrong |
| ref_cu_tuat | Cự Môn: hãm → miếu | critical | có | có | 0.425 | comm.persuasive | cog.suspicious, life.hardship, life.mitigated, values.kind |
| ref_cu_tuat | bỏ Hóa Lộc (Cự Môn) khỏi Mệnh | critical | có | có | 0.476 | adapt.flexible | life.hardship, life.mitigated, life.pleasure |
| ref_cu_tuat | bỏ Tuần ở Mệnh | critical | có | có | 0.853 | career.early | life.early_hardship |
| ref_cu_tuat | bỏ Địa Võng (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.225 |  |  |
| triet_menh | bỏ Địa Không khỏi Mệnh | critical | có | có | 0.156 |  | temper.cunning |
| triet_menh | Thiên Cơ: vượng → hãm | critical | có | có | 0.716 | cog.dull, amb.drive | values.kind, temper.headstrong |
| triet_menh | đặt Hóa Kỵ lên Thiên Cơ ở Mệnh | critical | có | có | 0.925 | cog.fanciful | temper.headstrong |
| triet_menh | thêm Tuần ở Mệnh | critical | có | có | 0.916 | fin.scarcity | temper.cunning |
| triet_menh | bỏ Thiên Đức (không luật nào nhắc) khỏi Mệnh | inert | có | — | 0.165 | amb.drive |  |
| menh_vcd | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.152 | temper.headstrong, life.pleasure, temper.proud | comm.friction |
| menh_vcd | thêm Tuần ở Mệnh | critical | có | có | 0.724 | life.early_hardship |  |
| menh_vcd | bỏ Thiên Khốc (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.228 |  |  |
| co_nguyet_dong_luong | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.034 | temper.assertive, temper.proud, temper.headstrong |  |
| co_nguyet_dong_luong | Thiên Cơ: None → hãm | critical | có | có | 0.743 | cog.dull |  |
| co_nguyet_dong_luong | bỏ Hóa Khoa (Thiên Lương) khỏi Mệnh | critical | không | — | 1 |  |  |
| co_nguyet_dong_luong | bỏ Tuần ở Mệnh | critical | có | có | 0.783 | career.early | life.early_hardship |
| co_nguyet_dong_luong | bỏ Địa Võng (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.305 |  |  |
| nhat_nguyet_ham | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.13 | temper.headstrong, temper.reckless | emo.melancholy |
| nhat_nguyet_ham | Thái Dương: hãm → miếu | critical | có | có | 0.452 | career.late, presence.charm, temper.cunning, life.transient | adapt.unsteady, emo.melancholy, life.early_hardship, values.integrity, life.late_bloom |
| nhat_nguyet_ham | bỏ Hóa Lộc (Thái Dương) khỏi Mệnh | critical | không | — | 1 |  |  |
| nhat_nguyet_ham | thêm Tuần ở Mệnh | critical | có | có | 0.599 | temper.headstrong, life.mitigated |  |
| nhat_nguyet_ham | bỏ Long Đức (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.33 |  |  |
| sat_pha_tham | bỏ Địa Kiếp khỏi Mệnh | critical | có | có | 0.081 |  | cog.analytic, life.transient |
| sat_pha_tham | Thất Sát: miếu → hãm | critical | có | có | 0.788 | life.mobility |  |
| sat_pha_tham | đặt Hóa Kỵ lên Thất Sát ở Mệnh | critical | không | — | 1 |  |  |
| sat_pha_tham | thêm Tuần ở Mệnh | critical | không | — | 0.973 |  |  |
| sat_pha_tham | bỏ Thiên Quan (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.344 |  |  |
| tuan_menh | bỏ Đà La khỏi Mệnh | critical | có | có | 0.027 | disc.diligent, emo.melancholy | temper.proud, temper.headstrong |
| tuan_menh | bỏ Tuần ở Mệnh | critical | có | có | 0.751 |  | life.early_hardship |
| tuan_menh | bỏ Cô Thần (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.22 |  |  |
| hoa_ky_menh | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.153 | temper.headstrong | inner.unrest |
| hoa_ky_menh | Thiên Cơ: vượng → hãm | critical | có | có | 0.647 | cog.dull, amb.status_focus | inner.unrest, values.kind |
| hoa_ky_menh | bỏ Hóa Khoa (Thiên Cơ) khỏi Mệnh | critical | không | — | 1 |  |  |
| hoa_ky_menh | thêm Tuần ở Mệnh | critical | không | — | 0.976 |  |  |
| hoa_ky_menh | bỏ Long Trì (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.244 |  |  |
| loc_ton_menh | bỏ Hỏa Tinh khỏi Mệnh | critical | có | có | 0.116 |  | values.integrity, temper.hot, life.pleasure |
| loc_ton_menh | Thiên Cơ: vượng → hãm | critical | có | có | 0.626 | cog.dull | comm.friction |
| loc_ton_menh | bỏ Hóa Lộc (Thiên Cơ) khỏi Mệnh | critical | có | có | 0.73 | cog.analytic | life.pleasure |
| loc_ton_menh | thêm Tuần ở Mệnh | critical | có | có | 0.823 | life.early_hardship |  |
| loc_ton_menh | bỏ Long Trì (không luật nào nhắc) khỏi Mệnh | inert | có | — | 0.15 |  | life.pleasure |
| khoi_viet_giap | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.082 | temper.proud, temper.headstrong, temper.assertive | presence.charm, comm.friction |
| khoi_viet_giap | Thiên Cơ: None → hãm | critical | có | có | 0.699 | cog.dull, temper.cunning | comm.friction |
| khoi_viet_giap | bỏ Hóa Quyền (Thiên Cơ) khỏi Mệnh | critical | không | — | 1 |  |  |
| khoi_viet_giap | thêm Tuần ở Mệnh | critical | có | có | 0.76 | life.early_hardship | career.late |
| khoi_viet_giap | bỏ Phượng Các (không luật nào nhắc) khỏi Mệnh | inert | có | — | 0.184 |  | presence.charm |
| than_menh | bỏ Hỏa Tinh khỏi Mệnh | critical | có | có | 0.128 | presence.charm | values.integrity, temper.hot |
| than_menh | Vũ Khúc: None → hãm | critical | không | — | 0.878 |  |  |
| than_menh | đặt Hóa Kỵ lên Vũ Khúc ở Mệnh | critical | không | — | 1 |  |  |
| than_menh | bỏ Tuần ở Mệnh | critical | có | có | 0.855 |  | life.early_hardship |
| than_menh | bỏ Thiên Sứ khỏi Tật Ách | inert | không | — | 0.15 |  |  |
| khong_kiep_menh | bỏ Địa Không khỏi Mệnh | critical | có | có | 0.078 | career.late, adapt.flexible | career.early, cog.analytic, comm.reserved, temper.assertive, life.transient |
| khong_kiep_menh | Liêm Trinh: miếu → hãm | critical | có | có | 0.447 | inner.unrest, temper.headstrong, adapt.flexible | values.integrity, temper.hot |
| khong_kiep_menh | bỏ Hóa Kỵ (Liêm Trinh) khỏi Mệnh | critical | không | — | 1 |  |  |
| khong_kiep_menh | thêm Tuần ở Mệnh | critical | có | có | 0.335 | life.early_hardship, fin.scarcity | career.early, temper.assertive |
| khong_kiep_menh | bỏ Thiên Hư (không luật nào nhắc) khỏi Mệnh | inert | có | — | 0.129 |  | temper.assertive |
| cat_tu_hoi | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.156 | temper.headstrong, temper.proud | cog.sharp |
| cat_tu_hoi | Thiên Tướng: hãm → miếu | critical | có | có | 0.76 | temper.assertive | values.integrity |
| cat_tu_hoi | đặt Hóa Kỵ lên Thiên Tướng ở Mệnh | critical | không | — | 1 |  |  |
| cat_tu_hoi | thêm Tuần ở Mệnh | critical | có | có | 0.572 | life.early_hardship, emo.melancholy | career.late |
| cat_tu_hoi | bỏ Long Đức (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.151 |  |  |
| tu_vi_menh | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | không | — | 0.106 |  |  |
| tu_vi_menh | Tử Vi: đắc → hãm | critical | không | — | 1 |  |  |
| tu_vi_menh | đặt Hóa Kỵ lên Tử Vi ở Mệnh | critical | không | — | 1 |  |  |
| tu_vi_menh | thêm Tuần ở Mệnh | critical | không | — | 0.933 |  |  |
| tu_vi_menh | bỏ Quả Tú (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.084 |  |  |
| tu_phu_vu_tuong | bỏ Linh Tinh khỏi Mệnh | critical | có | có | 0.202 |  | values.integrity, temper.hot |
| tu_phu_vu_tuong | Vũ Khúc: None → hãm | critical | không | — | 1 |  |  |
| tu_phu_vu_tuong | đặt Hóa Kỵ lên Vũ Khúc ở Mệnh | critical | không | — | 1 |  |  |
| tu_phu_vu_tuong | bỏ Tuần ở Mệnh | critical | không | — | 0.974 |  |  |
| tu_phu_vu_tuong | bỏ Tam Thai (không luật nào nhắc) khỏi Mệnh | inert | có | — | 0.12 | comm.reserved |  |
| kinh_ngo | bỏ Kình Dương khỏi Mệnh | critical | có | có | 0.082 | life.pleasure | disc.diligent, adapt.unsteady |
| kinh_ngo | Cự Môn: vượng → hãm | critical | có | có | 0.428 | cog.suspicious, life.pleasure, cog.dull | comm.persuasive, adapt.unsteady |
| kinh_ngo | đặt Hóa Kỵ lên Cự Môn ở Mệnh | critical | có | có | 0.886 | cog.fanciful | adapt.unsteady |
| kinh_ngo | thêm Tuần ở Mệnh | critical | có | có | 0.779 | life.early_hardship | career.late |
| kinh_ngo | bỏ Thiên Khốc (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.226 |  |  |
| sat_nang_ham | bỏ Kình Dương khỏi Mệnh | critical | có | có | 0.073 | temper.cunning | temper.proud, temper.assertive |
| sat_nang_ham | Thái Âm: hãm → miếu | critical | có | có | 0.616 | life.pleasure | spirit.unworldly |
| sat_nang_ham | bỏ Hóa Kỵ (Thái Âm) khỏi Mệnh | critical | không | — | 1 |  |  |
| sat_nang_ham | thêm Tuần ở Mệnh | critical | có | có | 0.813 | life.early_hardship | career.early |
| sat_nang_ham | bỏ Thiên Quan (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.287 |  |  |
| cu_ty_ngo | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.103 | cog.analytic, emo.melancholy |  |
| cu_ty_ngo | Cự Môn: vượng → hãm | critical | có | có | 0.46 | cog.suspicious, cog.dull, cog.analytic, comm.friction | temper.headstrong, comm.persuasive, temper.proud |
| cu_ty_ngo | đặt Hóa Kỵ lên Cự Môn ở Mệnh | critical | có | có | 0.417 | cog.fanciful, inner.unrest, comm.friction, cog.analytic | temper.proud |
| cu_ty_ngo | bỏ Tuần ở Mệnh | critical | có | có | 0.768 | career.late | life.early_hardship |
| cu_ty_ngo | bỏ Long Trì (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.174 |  |  |
| tam_hoa_hoi | bỏ Địa Kiếp khỏi Mệnh | critical | có | có | 0.055 | values.kind | adapt.unsteady, cog.analytic, comm.reserved, career.early, temper.assertive, life.transient |
| tam_hoa_hoi | thêm Tuần ở Mệnh | critical | có | có | 0.572 | life.early_hardship | career.early |
| tam_hoa_hoi | bỏ Kiếp Sát (không luật nào nhắc) khỏi Mệnh | inert | có | — | 0.045 |  | temper.assertive |
| nhat_nguyet_sang | thêm Kình Dương vào Mệnh (độ sáng không rõ) | critical | có | có | 0.058 | temper.assertive, temper.proud, temper.headstrong | life.pleasure |
| nhat_nguyet_sang | Thái Âm: vượng → hãm | critical | có | có | 0.385 | temper.headstrong | life.pleasure |
| nhat_nguyet_sang | bỏ Hóa Quyền (Thái Âm) khỏi Mệnh | critical | không | — | 1 |  |  |
| nhat_nguyet_sang | thêm Tuần ở Mệnh | critical | có | có | 0.317 | life.early_hardship, emo.melancholy, life.mobility | career.early, life.pleasure |
| nhat_nguyet_sang | bỏ Địa Võng (không luật nào nhắc) khỏi Mệnh | inert | không | — | 0.226 |  |  |
