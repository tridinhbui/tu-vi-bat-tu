# Phase 4 — bảng nguồn cho 10 cách cục (định nghĩa v2)

Sinh bởi `tools/build_formation_source_audit.py`. **Không điều kiện nào đạt T0 (đọc trực tiếp trang sách)**, nên toàn bộ vẫn `draft`.

| Tầng | Ý nghĩa |
|---|---|
| T0 | đọc trực tiếp trang sách trong lần audit này |
| T1 | luật trong registry, đã verified (diễn giải, không độc lập) |
| T2 | luật trong registry, còn draft |
| T3 | câu phú gốc từ một bản web, chưa đối chiếu bản in |
| T4 | giả thuyết thiết kế |

Registry **không phải bằng chứng độc lập**: nó là cách các phiên trước đã đọc sách, lưu dưới dạng diễn giải tiếng Việt, không có nguyên văn.
Chỉ nguồn có mức tương ứng `khop` mới tính là *ủng hộ*; `lien_quan`/`long_hon`/`chat_hon`/`khac` chỉ liệt kê là liên quan.

## Xung đột giữa các nguồn

- **X_MDDK_NGO** (CACH_X_MA_DAU_DOI_KIEM): KL p.64 (registry, draft): Kình Dương ở Ngọ ↔ chú giải 定貴局 (T3): 'Mã có nhận', không phải cách ở cung Ngọ. Hệ quả: điều kiện lõi của cách chưa thể coi là đã xác định; giữ draft, cần đọc lại cả hai trang sách.
- **X_TTAN_HOA** (CACH_X_THACH_TRUNG_AN_NGOC): KL p.58 và TT p.34 (registry, verified): Khoa+Quyền+Lộc đủ ↔ phú gốc (T3): tam phương có Khoa, Lộc chiếu (không nêu Quyền). Hệ quả: booster 'tam_hoa_hoi_du' chặt hơn câu phú; cần xem bản chú Việt có thêm Quyền hay không.
- **X_TRIET_GIAI** (*): mọi bản nháp v1: Triệt giải sát tinh (đã bỏ ở v2) ↔ TH pp.94-95 (registry, verified): Tuần/Triệt bất lợi cho Phủ, Tướng, Âm, Lương. Hệ quả: đã loại khỏi v2; ghi lại để không tái xuất hiện.

## Câu phú gốc đã truy xuất (T3)

Nguồn: https://zh.wikisource.org/wiki/紫微斗數全書/卷一. Qua công cụ tóm tắt, một bản web; bản dịch là dịch sát nghĩa của người audit.

| id | mục | nguyên văn | dịch sát nghĩa |
|---|---|---|---|
| C_TP_DONG | 斗數骨髓賦 | 紫府同宮終身福厚 | Tử Phủ đồng cung, suốt đời phúc dày. |
| C_TP_TRIEU | 斗數骨髓賦 | 紫府朝垣食祿萬鍾 | Tử Phủ chầu viên (triều viên), hưởng lộc muôn chung. |
| C_CNDL | 斗數骨髓賦 | 七殺破軍宜出外，機月同梁作吏人 | Thất Sát, Phá Quân nên ra ngoài; Cơ Nguyệt Đồng Lương làm hạng lại viên (viên chức). |
| C_NN_MINH | 斗數骨髓賦 | 日月並明佐九重於堯殿 | Nhật Nguyệt cùng sáng, giúp chín tầng cung điện vua Nghiêu. |
| C_NN_BOI | 太微賦 | 日月最嫌反背 | Nhật Nguyệt rất ngại bị phản bối (đảo ngược). |
| C_NLTT | 太微賦 | 太陽居午，謂之日麗中天，有專權之貴，敵國之富 | Thái Dương ở Ngọ gọi là Nhật lệ trung thiên: có cái quý chuyên quyền, cái giàu địch quốc. |
| C_TTAN | 斗數骨髓賦 | 子午巨門石中隱玉，明祿暗祿錦上添花 | Cự Môn ở Tý Ngọ là ngọc ẩn trong đá; minh lộc, ám lộc thêm hoa trên gấm. |
| C_TTAN_PHU | 論石中隱玉格（以檢索工具轉述） | 巨門子午二宮逢，身命逢之必貴榮，更得三方科祿照，石中隱玉是豐隆 | Cự Môn gặp ở hai cung Tý Ngọ, thân hoặc mệnh gặp ắt vinh quý; lại được tam phương Khoa, Lộc chiếu thì ngọc ẩn trong đá là thịnh vượng. |
| C_MDDK | 太微賦 | 馬頭帶劍，鎮衛邊疆 | Đầu ngựa đeo gươm, trấn giữ biên cương. |
| C_MDDK_CHU | 定貴局（chú） | 馬頭帶劍 謂馬有刃是也不是居午格 | Mã đầu đới kiếm: nghĩa là (Thiên) Mã có 'nhận' (lưỡi), chứ không phải cách ở cung Ngọ. |
| C_KV | 定貴局（chú） | 坐貴向貴 謂魁鉞在命迭相坐拱是也 | Tọa quý hướng quý: Khôi Việt ở Mệnh, thay nhau tọa và củng chiếu. |

## Tử Phủ Vũ Tướng (`CACH_X_TU_PHU_VU_TUONG`)

Tóm tắt tầng hiệu lực: T4=10.

| vai trò | điều kiện máy hóa | tầng | nguồn (sách, trang, review) | mức tương ứng | ghi chú |
|---|---|---|---|---|---|
| core:core | `palace.rel.tp_majors contains_all ["Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"]` | T4 | KHAO_LUAN KL p.217 [draft] `TV_KL_CUNG_PHUC_DUC_TU_PHU_VU_TUONG`; 斗數骨髓賦「紫府朝垣食祿萬鍾」 | lien_quan | nguồn có nhóm Tử Phủ Vũ Tướng ở các cung khác (Phúc Đức, Tử Tức, Nô Bộc); không có luật nói bốn sao hội ở tam phương Mệnh thành một cách |
| boosters:ta_huu_hoi | `palace.rel.tp_stars contains_all ["Tả Phụ", "Hữu Bật"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| boosters:xuong_khuc_hoi | `palace.rel.tp_stars contains_any ["Văn Xương", "Văn Khúc"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| boosters:loc_hoi | `HOẶC(palace.rel.tp_stars contains "Lộc Tồn"; palace.rel.tp_hoa contains "Hóa Lộc")` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| breakers:sat_dong_cung | `palace.rel.self_stars contains_any ["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| breakers:ky_dong_cung | `palace.rel.self_hoa contains "Hóa Kỵ"` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| rescuers:khoa_dong_cung | `palace.rel.self_hoa contains "Hóa Khoa"` | T4 | KHAO_LUAN KL p.67 [verified] `TV_KL_STAR_MENH_KY_KHOA`; THUC_HANH TH p.53 [verified] `TV_TH_AUX_MENH_HKY_KHOA` | lien_quan | nguồn chỉ nói Hóa Kỵ gặp Hóa Khoa ở Hợi/Tý (kết quả tốt); bản nháp khái quát cho mọi vị trí |
| rescuers:tam_hoa_hoi_cuu | `palace.rel.tp_hoa contains_all ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa"]` | T4 | THUC_HANH TH p.74 [verified] `TV_TH_CACH_MENH_SV_CUU_GIAI` | long_hon | nguồn nói Mệnh ở bại địa hoặc tuyệt địa mà được Tam Hóa hội thì được cứu giải; bản nháp khái quát cho mọi yếu tố phá cách |
| refutations:tuan_triet_an_ngu | `HOẶC(palace.tuan eq true; palace.triet eq true)` | T4 | THUC_HANH TH p.94 [verified] `TV_TH_STAR_THIEN_PHU_NAM_TUAN_TRIET`; KHAO_LUAN KL p.228 [verified] `TV_KL_AUX_TUAN_TRIET` | lien_quan | nguồn: Thiên Phủ gặp Tuần/Triệt là điều kỵ nhất (TH p.94); chưa có nguồn cho cả nhóm bốn sao |
| refutations:Thiên_Tướng_ham | `palace.tp_rank.Thiên Tướng lte 0` | T4 | THUC_HANH TH p.95 [verified] `TV_TH_STAR_THIEN_TUONG_NAM_TUAN_TRIET` | lien_quan | nguồn nói Thiên Tướng gặp Tuần/Triệt như hãm; không nói Tướng hãm hạ cả cách |

## Tử Phủ đồng cung (`CACH_X_TU_PHU_DONG_CUNG`)

Tóm tắt tầng hiệu lực: T1=1, T3=1, T4=7.

| vai trò | điều kiện máy hóa | tầng | nguồn (sách, trang, review) | mức tương ứng | ghi chú |
|---|---|---|---|---|---|
| core:core | `palace.rel.self_majors contains_all ["Tử Vi", "Thiên Phủ"]` | T3 | KHAO_LUAN KL p.55 [verified] `TV_KL_PHU_TU_PHU_TUAN_TRIET`; 斗數骨髓賦「紫府同宮終身福厚」 | khop, lien_quan | KL p.55 lấy Tử Vi và Thiên Phủ đồng cung ở Mệnh làm khung nhưng không gọi là một cách |
| boosters:ta_huu_hoi | `palace.rel.tp_stars contains_all ["Tả Phụ", "Hữu Bật"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| boosters:xuong_khuc_hoi | `palace.rel.tp_stars contains_any ["Văn Xương", "Văn Khúc"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| boosters:khoi_viet_hoi | `palace.rel.tp_stars contains_any ["Thiên Khôi", "Thiên Việt"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| breakers:sat_dong_cung | `palace.rel.self_stars contains_any ["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| breakers:ky_dong_cung | `palace.rel.self_hoa contains "Hóa Kỵ"` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| rescuers:khoa_dong_cung | `palace.rel.self_hoa contains "Hóa Khoa"` | T4 | KHAO_LUAN KL p.67 [verified] `TV_KL_STAR_MENH_KY_KHOA`; THUC_HANH TH p.53 [verified] `TV_TH_AUX_MENH_HKY_KHOA` | lien_quan | nguồn chỉ nói Hóa Kỵ gặp Hóa Khoa ở Hợi/Tý (kết quả tốt); bản nháp khái quát cho mọi vị trí |
| rescuers:tam_hoa_hoi_cuu | `palace.rel.tp_hoa contains_all ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa"]` | T4 | THUC_HANH TH p.74 [verified] `TV_TH_CACH_MENH_SV_CUU_GIAI` | long_hon | nguồn nói Mệnh ở bại địa hoặc tuyệt địa mà được Tam Hóa hội thì được cứu giải; bản nháp khái quát cho mọi yếu tố phá cách |
| refutations:tuan_triet_an_ngu | `HOẶC(palace.tuan eq true; palace.triet eq true)` | T1 | KHAO_LUAN KL p.55 [verified] `TV_KL_PHU_TU_PHU_TUAN_TRIET`; THUC_HANH TH p.94 [verified] `TV_TH_STAR_THIEN_PHU_NAM_TUAN_TRIET` | khop | KL p.55: Tử Phủ bị Tuần hoặc Triệt án ngữ thì phúc lộc kém đi; TH p.94: Thiên Phủ kỵ Tuần, Triệt |

## Cơ Nguyệt Đồng Lương (`CACH_X_CO_NGUYET_DONG_LUONG`)

Tóm tắt tầng hiệu lực: T1=1, T4=7.

| vai trò | điều kiện máy hóa | tầng | nguồn (sách, trang, review) | mức tương ứng | ghi chú |
|---|---|---|---|---|---|
| core:core | `palace.rel.tp_majors contains_all ["Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"]` | T1 | TOAN_THU TT p.24 [verified] `TV_TT_MENH_CNDL_CONG_CHUC`; KHAO_LUAN KL p.221 [verified] `TV_KL_CT_CNDL`; 斗數骨髓賦「七殺破軍宜出外，機月同梁作吏人」 | khop, lien_quan | Toàn Thư p.24: Mệnh đủ bốn sao Cơ Nguyệt Đồng Lương trong tam phương |
| boosters:cat_tinh_hoi | `palace.rel.tp_stars contains_any ["Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"]` | T4 | TOAN_THU TT p.24 [verified] `TV_TT_MENH_CNDL_CONG_CHUC`; KHAO_LUAN KL p.221 [draft] `TV_KL_CT_CNDL_KQL_KV_XK` | lien_quan | TT p.24: thiếu cát tinh trợ lực thì chỉ ở mức công chức bình thường; KL p.221 (nháp): hội Khôi Việt, Xương Khúc thì hợp đường học thuật |
| boosters:khoa_quyen_loc_hoi | `palace.rel.tp_hoa contains_any ["Hóa Khoa", "Hóa Quyền", "Hóa Lộc"]` | T4 | KHAO_LUAN KL p.221 [draft] `TV_KL_CT_CNDL_KQL_KV_XK` | lien_quan | luật nháp có trang (KL p.221): hội Khoa Quyền Lộc thì hợp đường học thuật |
| breakers:khong_kiep_dong_cung | `palace.rel.self_stars contains_any ["Địa Không", "Địa Kiếp"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| breakers:ky_dong_cung | `palace.rel.self_hoa contains "Hóa Kỵ"` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| rescuers:khoa_dong_cung | `palace.rel.self_hoa contains "Hóa Khoa"` | T4 | KHAO_LUAN KL p.67 [verified] `TV_KL_STAR_MENH_KY_KHOA`; THUC_HANH TH p.53 [verified] `TV_TH_AUX_MENH_HKY_KHOA` | lien_quan | nguồn chỉ nói Hóa Kỵ gặp Hóa Khoa ở Hợi/Tý (kết quả tốt); bản nháp khái quát cho mọi vị trí |
| rescuers:tam_hoa_hoi_cuu | `palace.rel.tp_hoa contains_all ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa"]` | T4 | THUC_HANH TH p.74 [verified] `TV_TH_CACH_MENH_SV_CUU_GIAI` | long_hon | nguồn nói Mệnh ở bại địa hoặc tuyệt địa mà được Tam Hóa hội thì được cứu giải; bản nháp khái quát cho mọi yếu tố phá cách |
| refutations:tuan_triet_an_ngu | `HOẶC(palace.tuan eq true; palace.triet eq true)` | T4 | KHAO_LUAN KL p.228 [verified] `TV_KL_AUX_TUAN_TRIET` | lien_quan | nguồn: Tuần hoặc Triệt đóng ở Mệnh thì vui ít buồn nhiều (điểm kém); việc coi đó là phản chứng hạ một bậc là suy diễn của bản nháp |

## Sát Phá Liêm Tham (`CACH_X_SAT_PHA_LIEM_THAM`)

Tóm tắt tầng hiệu lực: T2=1, T4=10.

| vai trò | điều kiện máy hóa | tầng | nguồn (sách, trang, review) | mức tương ứng | ghi chú |
|---|---|---|---|---|---|
| core:core | `đếm(palace.rel.tp_majors contains "Thất Sát"; palace.rel.tp_majors contains "Phá Quân"; palace.rel.tp_majors contains "Liêm Trinh"; palace.rel.tp_majo` | T4 | THUC_HANH TH p.77 [draft] `TV_TH_CACH_MENH_HA_CACH`; THUC_HANH TH p.76 [draft] `TV_TH_CACH_THIEN_DI_THAN_SPLT`; 斗數骨髓賦「七殺破軍宜出外，機月同梁作吏人」 | lien_quan | ngưỡng ba trong bốn sao là quy ước của bản nháp; nguồn nói về chính tinh Sát Phá Liêm Tham ở Mệnh/Thân |
| boosters:khoa_quyen_hoi | `palace.rel.tp_hoa contains_any ["Hóa Khoa", "Hóa Quyền"]` | T4 | THUC_HANH TH p.76 [draft] `TV_TH_CACH_THIEN_DI_THAN_SPLT` | lien_quan | nguồn (nháp): miếu vượng, hội nhiều cát tinh thì có thể phát mạnh, nói cho Thân cư Thiên Di |
| boosters:ta_huu_hoi | `palace.rel.tp_stars contains_all ["Tả Phụ", "Hữu Bật"]` | T4 | THUC_HANH TH p.76 [draft] `TV_TH_CACH_THIEN_DI_THAN_SPLT` | lien_quan |  |
| boosters:xuong_khuc_hoi | `palace.rel.tp_stars contains_any ["Văn Xương", "Văn Khúc"]` | T4 | THUC_HANH TH p.76 [draft] `TV_TH_CACH_THIEN_DI_THAN_SPLT` | lien_quan |  |
| boosters:khoi_viet_hoi | `palace.rel.tp_stars contains_any ["Thiên Khôi", "Thiên Việt"]` | T4 | THUC_HANH TH p.76 [draft] `TV_TH_CACH_THIEN_DI_THAN_SPLT` | lien_quan |  |
| breakers:ba_sat_va_ky_trong_tam_phuong | `VÀ(palace.khi.sat_tp gte 3; palace.rel.tp_hoa contains "Hóa Kỵ")` | T2 | THUC_HANH TH p.77 [draft] `TV_TH_CACH_MENH_HA_CACH` | khop | TH p.77 (luật nguồn còn ở mức nháp): hạ cách khi từ ba sát tinh hội kèm Hóa Kỵ |
| breakers:ky_dong_cung | `palace.rel.self_hoa contains "Hóa Kỵ"` | T4 | THUC_HANH TH p.77 [draft] `TV_TH_CACH_MENH_HA_CACH` | lien_quan |  |
| rescuers:khoa_dong_cung | `palace.rel.self_hoa contains "Hóa Khoa"` | T4 | KHAO_LUAN KL p.67 [verified] `TV_KL_STAR_MENH_KY_KHOA`; THUC_HANH TH p.53 [verified] `TV_TH_AUX_MENH_HKY_KHOA` | lien_quan | nguồn chỉ nói Hóa Kỵ gặp Hóa Khoa ở Hợi/Tý (kết quả tốt); bản nháp khái quát cho mọi vị trí |
| rescuers:tam_hoa_hoi_cuu | `palace.rel.tp_hoa contains_all ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa"]` | T4 | THUC_HANH TH p.74 [verified] `TV_TH_CACH_MENH_SV_CUU_GIAI` | long_hon | nguồn nói Mệnh ở bại địa hoặc tuyệt địa mà được Tam Hóa hội thì được cứu giải; bản nháp khái quát cho mọi yếu tố phá cách |
| refutations:tuan_triet_an_ngu | `HOẶC(palace.tuan eq true; palace.triet eq true)` | T4 | KHAO_LUAN KL p.228 [verified] `TV_KL_AUX_TUAN_TRIET` | lien_quan | nguồn: Tuần hoặc Triệt đóng ở Mệnh thì vui ít buồn nhiều (điểm kém); việc coi đó là phản chứng hạ một bậc là suy diễn của bản nháp |
| refutations:Thất_Sát_ham | `palace.tp_rank.Thất Sát lte 0` | T4 | THUC_HANH TH p.76 [draft] `TV_TH_CACH_THIEN_DI_THAN_SPLT` | lien_quan | nguồn đòi chính tinh nhập miếu vượng mới phát mạnh |

## Nhật Nguyệt tịnh minh (`CACH_X_NHAT_NGUYET_TINH_MINH`)

Tóm tắt tầng hiệu lực: T1=1, T3=1, T4=10.

| vai trò | điều kiện máy hóa | tầng | nguồn (sách, trang, review) | mức tương ứng | ghi chú |
|---|---|---|---|---|---|
| core:core | `palace.rel.tp_majors contains_all ["Thái Dương", "Thái Âm"]` | T1 | KHAO_LUAN KL p.224 [verified] `TV_KL_CT_NHAT_NGUYET_DONG_CUNG`; KHAO_LUAN KL p.224 [verified] `TV_KL_CT_NHAT_NGUYET_CHIEU` | khop | hai luật có trang: Nhật Nguyệt đồng cung hoặc chiếu Mệnh |
| boosters:nhat_nguyet_deu_sang | `VÀ(palace.tp_rank.Thái Dương gte 2; palace.tp_rank.Thái Âm gte 2)` | T3 | THUC_HANH TH p.74 [draft] `TV_TH_CACH_MENH_BT_NN_TAN_HUNG`; 斗數骨髓賦「日月並明佐九重於堯殿」 | khop, lien_quan | nguồn (nháp) nói Nhật hoặc Nguyệt hãm gặp sát tinh là tàn hung, nên độ sáng có liên quan |
| boosters:ta_huu_hoi | `palace.rel.tp_stars contains_all ["Tả Phụ", "Hữu Bật"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| boosters:khoa_quyen_hoi | `palace.rel.tp_hoa contains_any ["Hóa Khoa", "Hóa Quyền"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| breakers:nhat_nguyet_ham_gap_sat | `VÀ(HOẶC(palace.tp_rank.Thái Dương lte 0; palace.tp_rank.Thái Âm lte 0); palace.khi.sat_tp gte 1)` | T4 | THUC_HANH TH p.74 [draft] `TV_TH_CACH_MENH_BT_NN_TAN_HUNG` | long_hon | TH p.74 (nháp): Nhật hoặc Nguyệt hãm Ở MỆNH gặp sát tinh; bản nháp xét sát tinh trong cả tam phương |
| breakers:ky_dong_cung | `palace.rel.self_hoa contains "Hóa Kỵ"` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| breakers:khong_kiep_dong_cung | `palace.rel.self_stars contains_any ["Địa Không", "Địa Kiếp"]` | T4 | THUC_HANH TH p.74 [draft] `TV_TH_CACH_MENH_BT_NN_TAN_HUNG` | lien_quan | nguồn nói sát tinh gặp Nhật/Nguyệt hãm; không nói riêng Không Kiếp |
| rescuers:khoa_dong_cung | `palace.rel.self_hoa contains "Hóa Khoa"` | T4 | KHAO_LUAN KL p.67 [verified] `TV_KL_STAR_MENH_KY_KHOA`; THUC_HANH TH p.53 [verified] `TV_TH_AUX_MENH_HKY_KHOA` | lien_quan | nguồn chỉ nói Hóa Kỵ gặp Hóa Khoa ở Hợi/Tý (kết quả tốt); bản nháp khái quát cho mọi vị trí |
| rescuers:tam_hoa_hoi_cuu | `palace.rel.tp_hoa contains_all ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa"]` | T4 | THUC_HANH TH p.74 [verified] `TV_TH_CACH_MENH_SV_CUU_GIAI` | long_hon | nguồn nói Mệnh ở bại địa hoặc tuyệt địa mà được Tam Hóa hội thì được cứu giải; bản nháp khái quát cho mọi yếu tố phá cách |
| refutations:Thái_Dương_ham | `palace.tp_rank.Thái Dương lte 0` | T4 | THUC_HANH TH p.74 [draft] `TV_TH_CACH_MENH_BT_NN_TAN_HUNG`; 太微賦「日月最嫌反背」 | lien_quan, long_hon | nguồn đòi hãm VÀ gặp sát tinh mới là tàn hung; bản nháp chỉ cần hãm |
| refutations:Thái_Âm_ham | `palace.tp_rank.Thái Âm lte 0` | T4 | THUC_HANH TH p.74 [draft] `TV_TH_CACH_MENH_BT_NN_TAN_HUNG`; 太微賦「日月最嫌反背」 | lien_quan, long_hon | như trên |
| refutations:tuan_triet_an_ngu | `HOẶC(palace.tuan eq true; palace.triet eq true)` | T4 | KHAO_LUAN KL p.228 [verified] `TV_KL_AUX_TUAN_TRIET` | lien_quan | nguồn: Tuần hoặc Triệt đóng ở Mệnh thì vui ít buồn nhiều (điểm kém); việc coi đó là phản chứng hạ một bậc là suy diễn của bản nháp |

## Nhật lệ trung thiên (`CACH_X_NHAT_LE_TRUNG_THIEN`)

Tóm tắt tầng hiệu lực: T1=1, T4=9.

| vai trò | điều kiện máy hóa | tầng | nguồn (sách, trang, review) | mức tương ứng | ghi chú |
|---|---|---|---|---|---|
| core:core | `VÀ(palace.branch eq "Ngọ"; palace.rel.self_majors contains "Thái Dương")` | T1 | THUC_HANH TH p.72 [verified] `TV_TH_CACH_MENH_NHAT_NGO`; KHAO_LUAN KL p.52 [verified] `TV_KL_PHU_DUONG_NGO`; 太微賦「太陽居午，謂之日麗中天，有專權之貴，敵國之富」 | khop | Thực Hành p.72: Thái Dương cư Ngọ có Mệnh là cách Nhật lệ trung thiên |
| boosters:ta_huu_hoi | `palace.rel.tp_stars contains_all ["Tả Phụ", "Hữu Bật"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| boosters:khoa_quyen_hoi | `palace.rel.tp_hoa contains_any ["Hóa Khoa", "Hóa Quyền"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| boosters:xuong_khuc_hoi | `palace.rel.tp_stars contains_any ["Văn Xương", "Văn Khúc"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| breakers:sat_dong_cung | `palace.rel.self_stars contains_any ["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| breakers:ky_dong_cung | `palace.rel.self_hoa contains "Hóa Kỵ"` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| rescuers:khoa_dong_cung | `palace.rel.self_hoa contains "Hóa Khoa"` | T4 | KHAO_LUAN KL p.67 [verified] `TV_KL_STAR_MENH_KY_KHOA`; THUC_HANH TH p.53 [verified] `TV_TH_AUX_MENH_HKY_KHOA` | lien_quan | nguồn chỉ nói Hóa Kỵ gặp Hóa Khoa ở Hợi/Tý (kết quả tốt); bản nháp khái quát cho mọi vị trí |
| rescuers:tam_hoa_hoi_cuu | `palace.rel.tp_hoa contains_all ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa"]` | T4 | THUC_HANH TH p.74 [verified] `TV_TH_CACH_MENH_SV_CUU_GIAI` | long_hon | nguồn nói Mệnh ở bại địa hoặc tuyệt địa mà được Tam Hóa hội thì được cứu giải; bản nháp khái quát cho mọi yếu tố phá cách |
| refutations:tuan_triet_an_ngu | `HOẶC(palace.tuan eq true; palace.triet eq true)` | T4 | KHAO_LUAN KL p.228 [verified] `TV_KL_AUX_TUAN_TRIET` | lien_quan | nguồn: Tuần hoặc Triệt đóng ở Mệnh thì vui ít buồn nhiều (điểm kém); việc coi đó là phản chứng hạ một bậc là suy diễn của bản nháp |
| refutations:Thái_Dương_ham | `palace.tp_rank.Thái Dương lte 0` | T4 | THUC_HANH TH p.74 [draft] `TV_TH_CACH_MENH_BT_NN_TAN_HUNG` | lien_quan | nguồn nói Thái Dương hãm gặp sát tinh là tàn hung |

## Thạch trung ẩn ngọc (`CACH_X_THACH_TRUNG_AN_NGOC`)

Tóm tắt tầng hiệu lực: T1=3, T4=4.

| vai trò | điều kiện máy hóa | tầng | nguồn (sách, trang, review) | mức tương ứng | ghi chú |
|---|---|---|---|---|---|
| core:core | `VÀ(palace.branch in ["Tý", "Ngọ"]; palace.rel.self_majors contains "Cự Môn")` | T1 | KHAO_LUAN KL p.58 [verified] `TV_KL_PHU_CU_TY_NGO_TAM_HOA`; TOAN_THU TT p.34 [verified] `TV_TT_MENH_CU_TY_NGO_TAM_HOA`; 斗數骨髓賦「子午巨門石中隱玉，明祿暗祿錦上添花」; 論石中隱玉格（以檢索工具轉述）「巨門子午二宮逢，身命逢之必貴榮，更得三方科祿照，石中隱玉是豐隆」 | khop | cả hai luật nguồn lấy Cự Môn ở Tý/Ngọ làm nền |
| boosters:tam_hoa_hoi_du | `palace.rel.tp_hoa contains_all ["Hóa Khoa", "Hóa Quyền", "Hóa Lộc"]` | T1 | KHAO_LUAN KL p.58 [verified] `TV_KL_PHU_CU_TY_NGO_TAM_HOA`; TOAN_THU TT p.34 [verified] `TV_TT_MENH_CU_TY_NGO_TAM_HOA`; 論石中隱玉格（以檢索工具轉述）「巨門子午二宮逢，身命逢之必貴榮，更得三方科祿照，石中隱玉是豐隆」 | khac, khop | hai luật nguồn: Cự Môn ở Tý/Ngọ hội đủ Khoa, Quyền, Lộc thì như ngọc ẩn trong đá |
| boosters:ta_huu_hoi | `palace.rel.tp_stars contains_all ["Tả Phụ", "Hữu Bật"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| breakers:ky_hoac_kinh_dong_cung | `HOẶC(palace.rel.self_hoa contains "Hóa Kỵ"; palace.rel.self_stars contains "Kình Dương")` | T1 | KHAO_LUAN KL p.66 [verified] `TV_KL_STAR_MENH_TAM_KY_KY_KINH` | khop | KL p.66: khi Khoa Quyền Lộc hội mà Hóa Kỵ hoặc Kình đồng cung thì mờ mịt; áp cho cấu trúc Tam Hóa hội của cách này |
| rescuers:khoa_dong_cung | `palace.rel.self_hoa contains "Hóa Khoa"` | T4 | KHAO_LUAN KL p.67 [verified] `TV_KL_STAR_MENH_KY_KHOA`; THUC_HANH TH p.53 [verified] `TV_TH_AUX_MENH_HKY_KHOA` | lien_quan | nguồn chỉ nói Hóa Kỵ gặp Hóa Khoa ở Hợi/Tý (kết quả tốt); bản nháp khái quát cho mọi vị trí |
| refutations:tuan_triet_an_ngu | `HOẶC(palace.tuan eq true; palace.triet eq true)` | T4 | KHAO_LUAN KL p.228 [verified] `TV_KL_AUX_TUAN_TRIET` | lien_quan | nguồn: Tuần hoặc Triệt đóng ở Mệnh thì vui ít buồn nhiều (điểm kém); việc coi đó là phản chứng hạ một bậc là suy diễn của bản nháp |
| refutations:Cự_Môn_ham | `palace.tp_rank.Cự Môn lte 0` | T4 | THUC_HANH TH p.95 [verified] `TV_TH_STAR_CU_MON_NAM_HAM_SAT` | lien_quan | nguồn: Cự Môn hãm hội sát tinh thì suốt đời cùng khổ |

## Mã đầu đới kiếm (`CACH_X_MA_DAU_DOI_KIEM`)

Tóm tắt tầng hiệu lực: T2=3, T4=6.

| vai trò | điều kiện máy hóa | tầng | nguồn (sách, trang, review) | mức tương ứng | ghi chú |
|---|---|---|---|---|---|
| core:core | `VÀ(palace.branch eq "Ngọ"; palace.rel.self_stars contains "Kình Dương")` | T2 | KHAO_LUAN KL p.64 [draft] `TV_KL_STAR_MENH_KINH_PHUC_LOC`; 太微賦「馬頭帶劍，鎮衛邊疆」; 定貴局（chú）「馬頭帶劍 謂馬有刃是也不是居午格」 | khac, khop, lien_quan | KL p.64 (luật còn ở mức nháp): Kình Dương ở Ngọ |
| boosters:khoa_quyen_loc_hoi | `palace.rel.tp_hoa contains_any ["Hóa Khoa", "Hóa Quyền", "Hóa Lộc"]` | T2 | KHAO_LUAN KL p.64 [draft] `TV_KL_STAR_MENH_KINH_PHUC_LOC` | khop | KL p.64: gặp Khoa, Quyền, Lộc (luật nguồn còn ở mức nháp) |
| boosters:ta_huu_hoi | `palace.rel.tp_stars contains_all ["Tả Phụ", "Hữu Bật"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| breakers:that_sat_trong_tam_phuong | `palace.rel.tp_stars contains "Thất Sát"` | T2 | KHAO_LUAN KL p.64 [draft] `TV_KL_STAR_MENH_KINH_PHUC_LOC` | khop | KL p.64 (luật nguồn còn ở mức nháp): tránh Thất Sát; sao Hình chưa được kiểm nên chưa đưa vào |
| breakers:sat_khac_dong_cung | `palace.rel.self_stars contains_any ["Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| breakers:ky_dong_cung | `palace.rel.self_hoa contains "Hóa Kỵ"` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| rescuers:khoa_dong_cung | `palace.rel.self_hoa contains "Hóa Khoa"` | T4 | KHAO_LUAN KL p.67 [verified] `TV_KL_STAR_MENH_KY_KHOA`; THUC_HANH TH p.53 [verified] `TV_TH_AUX_MENH_HKY_KHOA` | lien_quan | nguồn chỉ nói Hóa Kỵ gặp Hóa Khoa ở Hợi/Tý (kết quả tốt); bản nháp khái quát cho mọi vị trí |
| rescuers:tam_hoa_hoi_cuu | `palace.rel.tp_hoa contains_all ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa"]` | T4 | THUC_HANH TH p.74 [verified] `TV_TH_CACH_MENH_SV_CUU_GIAI` | long_hon | nguồn nói Mệnh ở bại địa hoặc tuyệt địa mà được Tam Hóa hội thì được cứu giải; bản nháp khái quát cho mọi yếu tố phá cách |
| refutations:tuan_triet_an_ngu | `HOẶC(palace.tuan eq true; palace.triet eq true)` | T4 | KHAO_LUAN KL p.228 [verified] `TV_KL_AUX_TUAN_TRIET` | lien_quan | nguồn: Tuần hoặc Triệt đóng ở Mệnh thì vui ít buồn nhiều (điểm kém); việc coi đó là phản chứng hạ một bậc là suy diễn của bản nháp |

## Tam kỳ gia hội (`CACH_X_TAM_KY_GIA_HOI`)

Tóm tắt tầng hiệu lực: T1=2, T4=5.

| vai trò | điều kiện máy hóa | tầng | nguồn (sách, trang, review) | mức tương ứng | ghi chú |
|---|---|---|---|---|---|
| core:core | `palace.rel.tp_hoa contains_all ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa"]` | T1 | KHAO_LUAN KL p.66 [verified] `TV_KL_STAR_MENH_TAM_KY_KY_KINH` | khop | Khoa, Quyền, Lộc cùng hội ở tam phương Mệnh |
| boosters:hoa_o_ban_cung | `palace.rel.self_hoa contains_any ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| boosters:ta_huu_hoi | `palace.rel.tp_stars contains_all ["Tả Phụ", "Hữu Bật"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| boosters:xuong_khuc_hoi | `palace.rel.tp_stars contains_any ["Văn Xương", "Văn Khúc"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| breakers:ky_hoac_kinh_dong_cung | `HOẶC(palace.rel.self_hoa contains "Hóa Kỵ"; palace.rel.self_stars contains "Kình Dương")` | T1 | KHAO_LUAN KL p.66 [verified] `TV_KL_STAR_MENH_TAM_KY_KY_KINH` | khop | KL p.66: Hóa Kỵ hoặc Kình Dương đồng cung thì công danh mờ mịt |
| rescuers:ta_huu_giai_ky | `palace.rel.tp_stars contains_all ["Tả Phụ", "Hữu Bật"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| refutations:tuan_triet_an_ngu | `HOẶC(palace.tuan eq true; palace.triet eq true)` | T4 | KHAO_LUAN KL p.228 [verified] `TV_KL_AUX_TUAN_TRIET` | lien_quan | nguồn: Tuần hoặc Triệt đóng ở Mệnh thì vui ít buồn nhiều (điểm kém); việc coi đó là phản chứng hạ một bậc là suy diễn của bản nháp |

## Khôi Việt giáp Mệnh (`CACH_X_KHOI_VIET_GIAP_MENH`)

Tóm tắt tầng hiệu lực: T1=1, T4=9.

| vai trò | điều kiện máy hóa | tầng | nguồn (sách, trang, review) | mức tương ứng | ghi chú |
|---|---|---|---|---|---|
| core:core | `HOẶC(VÀ(palace.rel.flank_prev_stars contains "Thiên Khôi"; palace.rel.flank_next_stars contains "Thiên Việt"); VÀ(palace.rel.flank_prev_stars contains` | T1 | KHAO_LUAN KL p.215 [verified] `TV_KL_CUNG_MENH_GIAP_KHOI_VIET`; 定貴局（chú）「坐貴向貴 謂魁鉞在命迭相坐拱是也」 | khop, lien_quan | Khôi, Việt giáp hai bên Mệnh |
| boosters:co_chinh_tinh | `palace.has_no_major eq false` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| boosters:ta_huu_hoi | `palace.rel.tp_stars contains_all ["Tả Phụ", "Hữu Bật"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| boosters:xuong_khuc_hoi | `palace.rel.tp_stars contains_any ["Văn Xương", "Văn Khúc"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| breakers:sat_dong_cung | `palace.rel.self_stars contains_any ["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"]` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| breakers:ky_dong_cung | `palace.rel.self_hoa contains "Hóa Kỵ"` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| rescuers:khoa_dong_cung | `palace.rel.self_hoa contains "Hóa Khoa"` | T4 | KHAO_LUAN KL p.67 [verified] `TV_KL_STAR_MENH_KY_KHOA`; THUC_HANH TH p.53 [verified] `TV_TH_AUX_MENH_HKY_KHOA` | lien_quan | nguồn chỉ nói Hóa Kỵ gặp Hóa Khoa ở Hợi/Tý (kết quả tốt); bản nháp khái quát cho mọi vị trí |
| rescuers:tam_hoa_hoi_cuu | `palace.rel.tp_hoa contains_all ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa"]` | T4 | THUC_HANH TH p.74 [verified] `TV_TH_CACH_MENH_SV_CUU_GIAI` | long_hon | nguồn nói Mệnh ở bại địa hoặc tuyệt địa mà được Tam Hóa hội thì được cứu giải; bản nháp khái quát cho mọi yếu tố phá cách |
| refutations:vo_chinh_dieu | `palace.has_no_major eq true` | T4 | — | khong_co_nguon | giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho |
| refutations:tuan_triet_an_ngu | `HOẶC(palace.tuan eq true; palace.triet eq true)` | T4 | KHAO_LUAN KL p.228 [verified] `TV_KL_AUX_TUAN_TRIET` | lien_quan | nguồn: Tuần hoặc Triệt đóng ở Mệnh thì vui ít buồn nhiều (điểm kém); việc coi đó là phản chứng hạ một bậc là suy diễn của bản nháp |
