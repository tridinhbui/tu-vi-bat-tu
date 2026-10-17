# Phase 6 — Kiểm chứng độc lập và chuẩn hoá 17 biến thể cách cục Tử Vi (bản nháp)

Sinh bởi `tools/build_formation_report6.py` từ dữ liệu đã ghim (audit, biến thể, đề xuất, quét 116.928 lá số, bộ lá số đối chứng). Mọi cách cục và biến thể vẫn `draft`, chỉ hiện ở `?thu-nghiem`; **không dùng `verified`** vì chưa có thẩm định độc lập của chuyên gia. Định nghĩa gốc `formations_experimental.json` (của phiên khác) không bị sửa.

## 1. Chốt provenance (đếm lại sau khi thêm cờ giả định từng quy tắc)

Tổng **51** quy tắc trong 17 biến thể: **10** `doi_chieu_truc_tiep`, **37** `co_nguon_con_gia_dinh`, **4** `chua_du_nguon`. Con số 15 xuất hiện trong tin nhắn bàn giao Phase 5 (đếm trước khi thêm cờ giả định) không khớp file đã commit, vốn ghi 8 `doi_chieu_truc_tiep`; cả hai **đã bị thay thế** bởi số trên, tính theo từng quy tắc sau khi cờ giả định được gắn cho từng quy tắc và một trích dẫn sai chủ đề của audit (KL tr.221, Cơ Nguyệt Đồng Lương) được sửa.

- `doi_chieu_truc_tiep`: mọi trích dẫn của quy tắc được máy so với văn bản trang, câu sách đã xác định phạm vi, không có giả định của mô hình.
- `co_nguon_con_gia_dinh`: có trang sách nói đúng chủ đề nhưng còn giả định (phạm vi, ngưỡng, tập sao, một-trong-các-sao).
- `chua_du_nguon`: trang chỉ đọc được từ ảnh, hoặc là quy ước thiết kế (3 trong 4 sao; 3 sát tinh + Kỵ), hoặc quy tắc gốc chỉ 'liên quan'.

| Biến thể | Sách · trang | đối chiếu trực tiếp | có nguồn còn giả định | chưa đủ nguồn |
|---|---|---|---|---|
| `TU_PHU_VU_TUONG@kl_132_193` | KL tr.132, KL tr.193, KL tr.222, TH tr.72 | 0 | 4 | 0 |
| `TU_PHU_VU_TUONG@th_115` | TH tr.115, TH tr.72, TH tr.94, TH tr.95 | 0 | 4 | 0 |
| `TU_PHU_DONG_CUNG@tt_22` | KL tr.55, TH tr.72, TT tr.22 | 0 | 4 | 0 |
| `TU_PHU_DONG_CUNG@kl_50` | KL tr.50, KL tr.55, KL tr.96, TH tr.72 | 3 | 4 | 0 |
| `CO_NGUYET_DONG_LUONG@tt_24` | TH tr.77, TT tr.24 | 0 | 4 | 0 |
| `CO_NGUYET_DONG_LUONG@kl_221` | KL tr.221, KL tr.51 | 0 | 3 | 0 |
| `SAT_PHA_LIEM_THAM@th_76_77` | TH tr.116, TH tr.72, TH tr.76, TH tr.77 | 0 | 1 | 2 |
| `NHAT_NGUYET_TINH_MINH@th_72` | TH tr.72, TH tr.74, TT tr.142 | 1 | 2 | 0 |
| `NHAT_NGUYET_TINH_MINH@kl_53_68` | KL tr.53, KL tr.56, KL tr.68 | 0 | 4 | 0 |
| `NHAT_LE_TRUNG_THIEN@kl_52_85` | KL tr.52, KL tr.85, TH tr.72 | 1 | 2 | 0 |
| `THACH_TRUNG_AN_NGOC@kl_44` | KL tr.44 | 1 | 0 | 0 |
| `THACH_TRUNG_AN_NGOC@kl_58` | KL tr.58, TT tr.142 | 0 | 1 | 0 |
| `THACH_TRUNG_AN_NGOC@kl_106` | KL tr.106, TH tr.43 | 0 | 1 | 0 |
| `MA_DAU_DOI_KIEM@kl_64_xau` | KL tr.64 | 2 | 0 | 0 |
| `MA_DAU_DOI_KIEM@kl_64_tot` | KL tr.64 | 1 | 1 | 0 |
| `TAM_KY_GIA_HOI@kl_66` | KL tr.66, TT tr.142 | 0 | 2 | 0 |
| `KHOI_VIET_GIAP_MENH@kl_44_62` | KL tr.44, KL tr.62 | 1 | 0 | 2 |

Ghi chú về cơ chế (áp cho mọi biến thể, không phải kết luận cổ thư): thang `hình thức → thành → thành thượng` (thành thượng = từ 2 yếu tố tăng thế), mỗi phản chứng hạ một bậc, không cộng điểm, breaker không được cứu thì `bị phá`. Biến thể không có sao cứu.

### Sửa audit trong Phase 6

Một test mới (`test_every_cited_quote_speaks_about_the_condition_it_supports`) kiểm từng câu trích có nói đến chủ thể của điều kiện. Nó phát hiện: (1) audit gắn câu về Sát Phá Tham (KL tr.221) cho điều kiện của Cơ Nguyệt Đồng Lương — đã thay bằng hai câu đúng chủ đề; (2) hai điều kiện Kỵ của Nhật Nguyệt/Nhật lệ trung thiên trích câu về Tuần/Triệt thay vì câu 'Thái dương ghét ... Kỵ' (KL tr.85); (3) ba điều kiện cát tinh của Sát Phá Liêm Tham trích sai câu (TH tr.76). Các số trang của lá số đối chứng cũng được sửa (Hạng Võ tr.238, Khổng Minh tr.240, Nữ Quý Mão tr.244, Mậu Tý tr.245–246; trước đó ghi tr.239/241/243). Phép kiểm này chỉ là kiểm từ khoá, KHÔNG chứng minh ý nghĩa câu trích.

## 2. Hai mươi lăm đề xuất sửa, từng đề xuất

Quan hệ: *mở rộng* = điều kiện mới đúng ở mọi nơi điều kiện gốc đúng; *thu hẹp* = ngược lại; *thay bằng* = không chứa nhau. Số liệu trước/sau tính trên mẫu 11,520 lá số, chỉ ở những lá số mà lõi baseline đúng.

| # | Cách · điều kiện gốc | Nguồn · trang · trích | Cách hiểu mới | Giả định | Biến thể | Xử lý | Trước → sau (gốc đúng / mới đúng / chỉ gốc / chỉ mới) | Regression |
|---|---|---|---|---|---|---|---|---|
| P01 | Tử Phủ Vũ Tướng · `sat_dong_cung` | TH tr.116: “Tử Phủ Vũ Tướng găp phải Tam Không, Kiếp Kỵ Hình Đà hay gặp Linh Hỏa Tang Diêu thì bị giáng chức, phá tài”<br>KL tr.96: “Nhưng nếu gặp Không Kiếp, Tuần Triệt, Kình Đà, Hỏa Linh thì tài lộc bị giảm đáng kể” | giữ đồng cung ở baseline | cách đọc 'gặp' trong ngữ cảnh đại tiểu hạn, không xác định phạm vi trong bản cách → không mở rộng | — | không triển khai (chưa đủ căn cứ) — cách đọc 'gặp' trong ngữ cảnh đại tiểu hạn, không xác định phạm vi trong bản cách → không mở rộng | — | `test_formation_proposals.py::test_unimplemented_and_dropped_stay_out_of_variants` |
| P02 | Tử Phủ Vũ Tướng · `ky_dong_cung` | TH tr.116: “Tử Phủ Vũ Tướng găp phải Tam Không, Kiếp Kỵ Hình Đà hay gặp Linh Hỏa Tang Diêu thì bị giáng chức, phá tài” | giữ đồng cung ở baseline | cách đọc 'gặp' trong ngữ cảnh đại tiểu hạn, không xác định phạm vi trong bản cách → không mở rộng | — | không triển khai (chưa đủ căn cứ) — cách đọc 'gặp' trong ngữ cảnh đại tiểu hạn, không xác định phạm vi trong bản cách → không mở rộng | — | `test_formation_proposals.py::test_unimplemented_and_dropped_stay_out_of_variants` |
| P03 | Tử Phủ Vũ Tướng · `tam_hoa_hoi_cuu` | TH tr.74: “cần được cứu giải băng Tam hóa hội” | bỏ khỏi mọi biến thể | — | kl_132_193, th_115 | bỏ khỏi biến thể — Không biến thể nào có sao cứu: TH tr.74 chỉ nói Tam Hóa cứu Mệnh ở bại/tuyệt địa, KL tr.132 chỉ gọi Hóa Khoa là sao giải nói chung; không trang nào nói sao đó cứu cách này. | — | `test_formation_proposals.py::test_unimplemented_and_dropped_stay_out_of_variants` |
| P04 | Tử Phủ đồng cung · `core` | TH tr.72: “Tử, Phủ đồng cung cáh (đóng ở Mệnh hay Thân)”<br>TT tr.22: “Tử Phủ đồng cung vô sát tấu” | neo ở Mệnh hoặc Thân (TH tr.72) | mô hình chỉ neo một cung; Thân không biểu diễn được ở dạng dữ liệu hiện tại | — | không triển khai (chưa đủ căn cứ) — anchor của cách cục là một tên cung duy nhất; cần thay đổi schema của phiên khác | — | `test_formation_proposals.py::test_unimplemented_and_dropped_stay_out_of_variants` |
| P05 | Tử Phủ đồng cung · `sat_dong_cung` | TT tr.22: “Tử Phủ đồng cung vô sát tấu”<br>KL tr.50: “Tử vi, Thiên phủ đồng cung với Kình dương, lực sĩ thì buôn bán giàu có” | TT tr.22: sát tinh làm hỗn là phá; KL tr.50 là bản ngược (Kình Dương đồng cung là tăng thế) | 'gặp sát tinh' đọc là đồng cung | tt_22 | giữ, khai báo cách đọc | 56 / 56 / 0 / 0 (trên 192) | `test_formation_proposals.py::test_relation_holds_on_the_sample` |
| P06 | Tử Phủ đồng cung · `ky_dong_cung` | KL tr.50: “Mệnh ở Dần có Hoá kỵ, Hóa quyền đồng cung với Tử Phủ là người mưu cơ tài trí” | bỏ khỏi cả hai biến thể; KL tr.50 thêm 'Kỵ + Quyền ở Dần' như tăng thế | — | tt_22, kl_50 | bỏ khỏi biến thể — TT tr.22 không nói Kỵ; KL tr.50 nói Kỵ+Quyền đồng cung là tốt | — | `test_formation_proposals.py::test_unimplemented_and_dropped_stay_out_of_variants` |
| P07 | Cơ Nguyệt Đồng Lương · `khong_kiep_dong_cung` | TT tr.24: “Gặp Kiếp Không Hoá Kị xuống hạ cách”<br>TH tr.116: “Cơ Nguyệt Đồng Lương hay Cự Nhật mà gặp Kình Đà, Không Kiếp hay Phá toái, Kiếp sát” | Địa Không/Địa Kiếp trong tam phương (TT tr.24 'các cung tam hợp xung chiếu') | câu liệt kê Kiếp, Không, Kị: một trong số đó là đủ | tt_24 | mở rộng phạm vi | 216 / 648 / 0 / 432 (trên 1296) | `test_formation_proposals.py::test_relation_holds_on_the_sample` |
| P08 | Cơ Nguyệt Đồng Lương · `ky_dong_cung` | TT tr.24: “Gặp Kiếp Không Hoá Kị xuống hạ cách” | Hóa Kỵ trong tam phương (TT tr.24) | câu liệt kê Kiếp, Không, Kị: một trong số đó là đủ | tt_24 | mở rộng phạm vi | 92 / 536 / 0 / 444 (trên 1296) | `test_formation_proposals.py::test_relation_holds_on_the_sample` |
| P09 | Cơ Nguyệt Đồng Lương · `tam_hoa_hoi_cuu` | TH tr.74: “cần được cứu giải băng Tam hóa hội” | bỏ khỏi mọi biến thể | — | tt_24, kl_221 | bỏ khỏi biến thể — Không biến thể nào có sao cứu: TH tr.74 chỉ nói Tam Hóa cứu Mệnh ở bại/tuyệt địa, KL tr.132 chỉ gọi Hóa Khoa là sao giải nói chung; không trang nào nói sao đó cứu cách này. | — | `test_formation_proposals.py::test_unimplemented_and_dropped_stay_out_of_variants` |
| P10 | Sát Phá Liêm Tham · `ky_dong_cung` | TH tr.116: “Sát phá Liêm Tham mà gặp Nhị tam Không, Linh Hỏa Kình Kỵ” | giữ đồng cung ở baseline | cách đọc 'gặp' trong ngữ cảnh đại tiểu hạn, không xác định phạm vi trong bản cách → không mở rộng | — | không triển khai (chưa đủ căn cứ) — cách đọc 'gặp' trong ngữ cảnh đại tiểu hạn, không xác định phạm vi trong bản cách → không mở rộng | — | `test_formation_proposals.py::test_unimplemented_and_dropped_stay_out_of_variants` |
| P11 | Sát Phá Liêm Tham · `tam_hoa_hoi_cuu` | TH tr.74: “cần được cứu giải băng Tam hóa hội” | bỏ khỏi mọi biến thể | — | th_76_77 | bỏ khỏi biến thể — Không biến thể nào có sao cứu: TH tr.74 chỉ nói Tam Hóa cứu Mệnh ở bại/tuyệt địa, KL tr.132 chỉ gọi Hóa Khoa là sao giải nói chung; không trang nào nói sao đó cứu cách này. | — | `test_formation_proposals.py::test_unimplemented_and_dropped_stay_out_of_variants` |
| P12 | Nhật Nguyệt tịnh minh · `core` | TH tr.72: “Nhật, Nguyệt tinh minh cách (Nhật ở Thìn, Tỵ, Nguyệt ở Dậu, Tuất, mà Mệnh đóng ở Nguyệt hay Nhật đều tốt)”<br>KL tr.53: “Nhật nguyệt thủ Mệnh bất như hợp chiếu tịnh minh” | TH tr.72: Nhật Thìn/Tỵ, Nguyệt Dậu/Tuất, Mệnh ở Nhật hay Nguyệt; bản KL tr.53 giữ lõi hợp chiếu của baseline | bản KL: 'hợp chiếu' mô hình là cả hai sao trong tam phương | th_72 | thu hẹp | 2640 / 384 / 2256 / 0 (trên 2640) | `test_formation_proposals.py::test_relation_holds_on_the_sample` |
| P13 | Nhật Nguyệt tịnh minh · `tam_hoa_hoi_cuu` | TH tr.74: “cần được cứu giải băng Tam hóa hội” | bỏ khỏi mọi biến thể | — | th_72, kl_53_68 | bỏ khỏi biến thể — Không biến thể nào có sao cứu: TH tr.74 chỉ nói Tam Hóa cứu Mệnh ở bại/tuyệt địa, KL tr.132 chỉ gọi Hóa Khoa là sao giải nói chung; không trang nào nói sao đó cứu cách này. | — | `test_formation_proposals.py::test_unimplemented_and_dropped_stay_out_of_variants` |
| P14 | Nhật Nguyệt tịnh minh · `Thái_Dương_ham` | TH tr.74: “Nhật Nguyệt hãm tại Mệnh mà không có cứu tinh”<br>KL tr.68: “chỉ mong được Khôi Việt chiếu mới là tốt đẹp” | KL tr.68: Nhật/Nguyệt hãm mà KHÔNG có Khôi/Việt chiếu mới là phản chứng | 'Khôi Việt chiếu' đọc là hội chiếu tam phương | kl_53_68 | thay bằng điều kiện của sách | 1344 / 672 / 696 / 24 (trên 2640) | `test_formation_proposals.py::test_relation_holds_on_the_sample` |
| P15 | Nhật Nguyệt tịnh minh · `Thái_Âm_ham` | TH tr.74: “Nhật Nguyệt hãm tại Mệnh mà không có cứu tinh”<br>KL tr.68: “chỉ mong được Khôi Việt chiếu mới là tốt đẹp” | như Thái Dương hãm (gộp một điều kiện cho cả hai sao) | như trên | kl_53_68 | thay bằng điều kiện của sách | 912 / 672 / 456 / 216 (trên 2640) | `test_formation_proposals.py::test_relation_holds_on_the_sample` |
| P16 | Nhật Nguyệt tịnh minh · `tuan_triet_an_ngu` | KL tr.53: “rất cần Tuần không án ngữ ở Mệnh”<br>KL tr.85: “Thái dương hãm địa, cần gặp Tuần, Triệt, cũng cần gặp Đào, Hồng, Hỉ giúp sức” | bỏ khỏi cả hai biến thể | — | th_72, kl_53_68 | bỏ khỏi biến thể — KL tr.53 mục 11 và tr.85 coi Tuần/Triệt là điều kiện thuận cho Nhật Nguyệt/Thái Dương hãm | — | `test_formation_proposals.py::test_unimplemented_and_dropped_stay_out_of_variants` |
| P17 | Nhật lệ trung thiên · `ky_dong_cung` | KL tr.85: “Thái dương ghét lũ Riêu, Đà, Kỵ” | giữ nguyên ở baseline | KL tr.85 'ghét Kỵ' không nêu phạm vi | — | không triển khai (chưa đủ căn cứ) — KL tr.85 'ghét Kỵ' không nêu phạm vi → không suy ra đồng cung | — | `test_formation_proposals.py::test_unimplemented_and_dropped_stay_out_of_variants` |
| P18 | Nhật lệ trung thiên · `tam_hoa_hoi_cuu` | TH tr.74: “cần được cứu giải băng Tam hóa hội” | bỏ khỏi mọi biến thể | — | kl_52_85 | bỏ khỏi biến thể — Không biến thể nào có sao cứu: TH tr.74 chỉ nói Tam Hóa cứu Mệnh ở bại/tuyệt địa, KL tr.132 chỉ gọi Hóa Khoa là sao giải nói chung; không trang nào nói sao đó cứu cách này. | — | `test_formation_proposals.py::test_unimplemented_and_dropped_stay_out_of_variants` |
| P19 | Thạch trung ẩn ngọc · `tuan_triet_an_ngu` | KL tr.106: “Cự môn ở Tí Ngọ gặp Tuần Triệt là kỳ cách”<br>TH tr.43: “cần gặp được Tuần, Triệt hay Hóa Lộc thì ngọc mới lộ ra được” | bỏ phản chứng; ở bản KL tr.106/TH tr.43 Tuần/Triệt là điều kiện thuận nằm trong lõi | 'gặp' Tuần/Triệt đọc là cùng cung Mệnh | kl_44, kl_58, kl_106 | bỏ khỏi biến thể — KL tr.106 và TH tr.43 coi Tuần/Triệt (hoặc Hóa Lộc) là điều kiện để ngọc lộ ra | — | `test_formation_proposals.py::test_unimplemented_and_dropped_stay_out_of_variants` |
| P20 | Mã đầu đới kiếm · `that_sat_trong_tam_phuong` | KL tr.64: “Mệnh ở Ngọ, có Kình dương, gặp Thất sát, Thiên hình đồng cung là cách kiếm kể cổ ngựa”<br>KL tr.60: “có Thất sát Kình dương toạ thủ, lại thêm nhiều sát tinh hội chiếu” | KL tr.64 mục 5: Thất Sát VÀ Thiên Hình ĐỒNG CUNG với Kình Dương | — | kl_64_xau | thu hẹp | 72 / 4 / 68 / 0 (trên 192) | `test_formation_proposals.py::test_relation_holds_on_the_sample` |
| P21 | Mã đầu đới kiếm · `tam_hoa_hoi_cuu` | TH tr.74: “cần được cứu giải băng Tam hóa hội” | bỏ khỏi mọi biến thể | — | kl_64_xau, kl_64_tot | bỏ khỏi biến thể — Không biến thể nào có sao cứu: TH tr.74 chỉ nói Tam Hóa cứu Mệnh ở bại/tuyệt địa, KL tr.132 chỉ gọi Hóa Khoa là sao giải nói chung; không trang nào nói sao đó cứu cách này. | — | `test_formation_proposals.py::test_unimplemented_and_dropped_stay_out_of_variants` |
| P22 | Tam kỳ gia hội · `ky_hoac_kinh_dong_cung` | KL tr.66: “Cung mệnh có Khoa, Quyền, Lộc hội họp mà lại bị Hóa kỵ, Kình dương đồng cung hoặc chiếu vào” | KL tr.66: đồng cung HOẶC chiếu → đồng cung hoặc đối cung | 'chiếu' đọc hẹp là xung chiếu (đối cung); chưa mở ra tam phương vì câu sách không nói | kl_66 | mở rộng phạm vi | 24 / 92 / 0 / 68 (trên 472) | `test_formation_proposals.py::test_relation_holds_on_the_sample` |
| P23 | Khôi Việt giáp Mệnh · `sat_dong_cung` | KL tr.62: “Cung mệnh có Khôi Việt lại bị sát tinh hội chiếu thì mang bệnh tật khó chữa khỏi” | KL tr.62 mục 4: sát tinh HỘI CHIẾU → tam phương | 'hội chiếu' = tam phương (từ ngữ đã xác định phạm vi) | kl_44_62 | mở rộng phạm vi | 120 / 352 / 0 / 232 (trên 384) | `test_formation_proposals.py::test_relation_holds_on_the_sample` |
| P24 | Khôi Việt giáp Mệnh · `ky_dong_cung` | KL tr.62: “lại không bị Hóa kỵ Thiên hình cản phá thì giàu sang lớn” | giữ đồng cung ở baseline | KL tr.62 'cản phá' không nêu phạm vi | — | không triển khai (chưa đủ căn cứ) — KL tr.62 'Hóa kỵ Thiên hình cản phá' không nêu phạm vi | — | `test_formation_proposals.py::test_unimplemented_and_dropped_stay_out_of_variants` |
| P25 | Khôi Việt giáp Mệnh · `tam_hoa_hoi_cuu` | TH tr.74: “cần được cứu giải băng Tam hóa hội” | bỏ khỏi mọi biến thể | — | kl_44_62 | bỏ khỏi biến thể — Không biến thể nào có sao cứu: TH tr.74 chỉ nói Tam Hóa cứu Mệnh ở bại/tuyệt địa, KL tr.132 chỉ gọi Hóa Khoa là sao giải nói chung; không trang nào nói sao đó cứu cách này. | — | `test_formation_proposals.py::test_unimplemented_and_dropped_stay_out_of_variants` |

Tổng: 4 mở rộng, 2 thu hẹp, 2 thay bằng, 1 giữ, **10 bỏ** (chủ yếu sao cứu), **6 không triển khai** vì sách dùng 'gặp' trong ngữ cảnh chưa xác định phạm vi.

## 3. Oracle độc lập

`engine/tests/oracle_tuvi_independent.py` **không import `tvbt`**. Nó tự an: Mệnh/Thân, cục (Ngũ Hổ Độn + nạp âm), Tử Vi, Thiên Phủ và hai hệ chính tinh, Tả/Hữu, Xương/Khúc, Khôi/Việt (TH tr.19), Lộc Tồn/Kình/Đà (TH tr.21), Địa Không/Địa Kiếp, Hỏa/Linh, Thiên Hình, Lực Sĩ, Tứ Hóa (TH tr.20–21, KL tr.36, tr.196–197), Triệt (TH tr.20), Tuần (giáp tuần), độ sáng Thái Dương (TH tr.31) và Thái Âm (TH tr.39); rồi tự hiện thực 17 biến thể từ nhãn tiếng Việt của từng điều kiện (không từ DSL) với logic ba giá trị.

- **So sánh toàn bộ 116,928 lá số** (mười năm liên tiếp × mọi ngày âm × 12 giờ × 2 giới + 4 năm Mậu): số sai khác = **0** trên Mệnh/Thân/cục, vị trí mọi sao, Tứ Hóa, Tuần/Triệt và trạng thái của cả 17 biến thể.
- **Oracle tự tái hiện các lá số in trong sách** (5 lá số của phiên khác + Hàn Tín) về chính tinh từng cung, phụ tinh đọc được và Tứ Hóa — mà không dùng bất cứ hàm sản xuất nào.
- **Kiểm đột biến**: 4 đột biến có chủ đích trong sản xuất (đổi phạm vi tam phương → đồng cung, đối cung → giáp cung, Tuần sai cung, hội chiếu → giáp) đều bị oracle phát hiện; so sánh không rỗng.
- Test không phải xác nhận vòng tròn: oracle không đọc `tuvi.py`, `positions.py`, bảng độ sáng JSON hay DSL.

**Giới hạn của oracle (không che giấu):**

1. Ngày dương lịch ↔ âm lịch vẫn do `lunar_input` sản xuất cung cấp; oracle nhận ngày âm. Lịch pháp không được kiểm chứng ở đây.
2. Công thức Địa Không/Kiếp, Hỏa/Linh (điểm khởi + chiều), Thiên Hình, Lực Sĩ được gõ theo quy tắc chuẩn, **không** theo một trang sách tôi đã đọc; chỉ được xác nhận gián tiếp qua các lá số in trong sách (Địa Không/Kiếp, Hỏa/Linh, Thiên Hình, Lộc Tồn).
3. Độ sáng Thái Dương tại Thân/Mùi không in trong dòng TH tr.31 mà lớp chữ còn đọc được → để trống (kết quả 'chưa biết'), không đoán; nếu sách đầy đủ có giá trị thì kết quả Nhật Nguyệt tịnh minh có thể đổi.
4. Hai bảng độ sáng cùng trang với bảng của sản xuất (TH tr.31, tr.39); sự độc lập nằm ở việc gõ lại từ văn bản trang, không ở chọn nguồn khác.
5. **Bất đồng trường phái ảnh hưởng đến cả hai phía**: TH tr.21 in Nhâm-Khoa = Thiên Phủ, KL tr.197 in Tả Phụ; sản xuất và oracle đều theo KL. Dưới cách đọc của TH mọi lá số năm Nhâm có sao Khoa khác, nên Tam Hóa/Tam kỳ gia hội của các năm đó cũng khác. Ghi chú 'agree on all ten stems' trong `tuvi.py` không đúng cho Nhâm. Cần chuyên gia quyết định, tôi không chọn.

## 4. Xung đột trường phái (giữ nguyên, không hợp nhất)

| Cách | Các biến thể giữ riêng | Mức bất đồng đo được trên các lá số mà cả hai cùng hiện |
|---|---|---|
| CO_NGUYET_DONG_LUONG | `tt_24` vs `kl_221` | 14,352/14,688 (97.7%) |
| MA_DAU_DOI_KIEM | `kl_64_xau` vs `kl_64_tot` | 94/4,176 (2.3%) |
| NHAT_NGUYET_TINH_MINH | `th_72` vs `kl_53_68` | 0/3,072 (0.0%) |
| THACH_TRUNG_AN_NGOC | `kl_44` vs `kl_106` | 0/696 (0.0%) |
| THACH_TRUNG_AN_NGOC | `kl_44` vs `kl_58` | 0/32 (0.0%) |
| THACH_TRUNG_AN_NGOC | `kl_58` vs `kl_106` | 0/32 (0.0%) |
| TU_PHU_DONG_CUNG | `tt_22` vs `kl_50` | 1,439/1,920 (74.9%) |
| TU_PHU_VU_TUONG | `kl_132_193` vs `th_115` | 5,652/14,736 (38.4%) |

- **Cơ Nguyệt Đồng Lương**: TT tr.24 (Kiếp, Không, Kị trong tam hợp xung chiếu thì hạ cách) và KL tr.221 (không nêu yếu tố phá) khác nhau ở 97,7% lá số cả hai cùng nhận. Đây là bất đồng thật giữa hai sách, không phải lỗi mô hình.
- **Tử Phủ đồng cung**: TT tr.22 coi sát tinh làm hỏng; KL tr.50 coi Kình Dương, Kỵ + Quyền đồng cung là tốt. Khác nhau đúng ở 658 lá số có sát tinh đồng cung.
- **Thạch trung ẩn ngọc**: ba định nghĩa mô tả ba tập lá số khác nhau (KL tr.44: 1.728; KL tr.106/TH tr.43: 696; KL tr.58: chỉ 32). Chúng không mâu thuẫn trên phần giao vì không có yếu tố tăng thế/phá để so.
- **Mã đầu đới kiếm**: hai kết cục trái nhau của cùng KL tr.64; chỉ khác ở 94 lá số vì điều kiện Thất Sát + Thiên Hình đồng cung hiếm.
- **Tuần/Triệt hai chiều** được giữ hai hướng ở các biến thể khác nhau (hại ở Tử Phủ Vũ Tướng, Tử Phủ đồng cung; thuận ở Thạch trung ẩn ngọc; không là phản chứng ở Nhật Nguyệt).
- Không có tổng kết 'trường phái nào đúng hơn'; không biến thể nào được ưu tiên.

## 5. Lá số đối chứng mở rộng (KL tr.237–247)

Sáu lá số có đủ ngày giờ sinh in trong sách (thêm Hàn Tín so với Phase 5), mười hàng cách. Ba loại nhận xét của sách được tách: *xác nhận*, *phủ định*, *không kết luận*; và tách theo mức bằng chứng: **ten** = nhận xét nêu đích danh các sao của cách; **tong_the** = sách chỉ nhận xét chung về lá số. Hàng 'không quyết định' là trạng thái trung tính (hình thức).

| Lá số · trang | Cách | Sách | Căn cứ | Trích | Gốc | Biến thể → trạng thái (kết quả) |
|---|---|---|---|---|---|---|
| Hán Cao Tổ (Giáp Ngọ) tr.237 | TU_PHU_VU_TUONG | sách xác nhận | tong_the | KL tr.237: “Phải công nhận đây là một lá số có nhiều ưu điểm về công danh sự nghiệp lâu bền” | thanh_thuong (khớp) | `kl_132_193` → thanh_thuong (khớp); `th_115` → thanh_thuong (khớp) |
| Hạng Võ (Đinh Mão) tr.238 | CO_NGUYET_DONG_LUONG | sách phủ định | ten | KL tr.238: “Cung Tài có Đồng Lương ngọ Triệt lại gặp Địa kiếp thì dù Tướng Ấn cũng chẳng giữ được sự nghiệp lâu dài” | thanh (KHÔNG khớp) | `tt_24` → bi_pha (khớp); `kl_221` → thanh (KHÔNG khớp) |
| Hạng Võ (Đinh Mão) tr.238 | TAM_KY_GIA_HOI | sách phủ định | tong_the | KL tr.238: “Cung Di, có Cự Kỵ là cách tử nạn về sông nước” | thanh (KHÔNG khớp) | `kl_66` → bi_pha (khớp) |
| Khổng Minh (Tân Dậu) tr.240 | NHAT_NGUYET_TINH_MINH | sách xác nhận | ten | KL tr.240: “là người thông minh tuyệt vời, tài ba xuất chúng được kính nể cầu cạnh” | thanh_thuong (khớp) | `kl_53_68` → thanh (khớp) |
| Hàn Tín (Giáp Tuất) tr.242 | TU_PHU_VU_TUONG | sách xác nhận | tong_the | KL tr.242: “Hơn nữa lại còn giữ Song Lộc, Hóa Lộc ở Mệnh, có Lộc tồn ở Tài chiếu lên giàu sang phú quí một thời” | thanh_thuong (khớp) | `kl_132_193` → thanh_thuong (khớp); `th_115` → thanh_thuong (khớp) |
| Hàn Tín (Giáp Tuất) tr.242 | TAM_KY_GIA_HOI | sách không kết luận | tong_the | KL tr.242: “Đây là một lá số đẹp nhưng không có hậu” | thanh_thuong (sách không xét) | `kl_66` → hinh_thuc (sách không xét) |
| Nữ Quý Mão tr.244 | CO_NGUYET_DONG_LUONG | sách không kết luận | tong_the | KL tr.244: “Người tuổi Quí Mão, Can Quí (Thủy) sinh Chi Mão (Mộc), tương sinh” | thanh (sách không xét) | `tt_24` → thanh (sách không xét); `kl_221` → thanh_thuong (sách không xét) |
| Nữ Quý Mão tr.244 | KHOI_VIET_GIAP_MENH | sách không kết luận | tong_the | KL tr.244: “Người tuổi Quí Mão, Can Quí (Thủy) sinh Chi Mão (Mộc), tương sinh” | thanh (sách không xét) | `kl_44_62` → bi_pha (sách không xét) |
| Mậu Tý phá sản tr.246 | NHAT_NGUYET_TINH_MINH | sách phủ định | ten | KL tr.245: “Lá số phá sản Âm dương lạc hãm cung Mệnh” | bi_pha (khớp) | `kl_53_68` → bi_pha (khớp) |
| Mậu Tý phá sản tr.246 | CO_NGUYET_DONG_LUONG | sách phủ định | ten | KL tr.246: “bởi cách Thiên cơ Hóa kỵ gặp Hỏa Linh đốt cháy ra tro” | thanh_thuong (KHÔNG khớp) | `tt_24` → bi_pha (khớp); `kl_221` → thanh_thuong (KHÔNG khớp) |

Tóm tắt (đếm theo hàng gốc / theo từng biến thể):

| Căn cứ | Phiên bản | khớp | KHÔNG khớp | sách không xét |
|---|---|---|---|---|
| ten | gốc | 2 | 2 | 0 |
| ten | biến thể | 4 | 2 | 0 |
| tong_the | gốc | 2 | 1 | 3 |
| tong_the | biến thể | 5 | 0 | 4 |

Hai điểm không khớp còn lại trong nhóm 'ten' đều là bản KL tr.221 của Cơ Nguyệt Đồng Lương, bản không có breaker (Hạng Võ: thành; Mậu Tý: thành thượng) — đúng là bất đồng giữa KL và TT. Các biến thể được viết từ trang sách trước khi so với các lá số này; không điều kiện nào được chỉnh để ép khớp. Mẫu rất nhỏ (6 lá số), nên không dùng để suy ra độ chính xác. Hàng 'tong_the' là bằng chứng yếu hơn vì sách không nêu đích danh cách.

## 6. Độ nhạy trên 116,928 lá số

Tỷ lệ kích hoạt = lõi đúng / tổng. Tỷ lệ bị phá = `bị phá` / lõi đúng. Cột cuối: so với baseline.

| Biến thể | Kích hoạt | Bị phá | Trạng thái hiện (lá số) | Chỉ baseline hiện | Khác baseline (cả hai hiện) |
|---|---|---|---|---|---|
| `CO_NGUYET_DONG_LUONG@kl_221` | 12.56% | 0.0% (0 do thiết kế: không breaker) | thanh 5,888, hinh_thuc 540, thanh_thuong 8,260 | 0 | 7,616/14,688 |
| `CO_NGUYET_DONG_LUONG@tt_24` | 12.56% | 82.1% ⚠ phân biệt kém | thanh 2,628, bi_pha 12,060 | 0 | 9,508/14,688 |
| `KHOI_VIET_GIAP_MENH@kl_44_62` | 2.38% | 91.7% ⚠ phân biệt kém | bi_pha 2,552, thanh 232 | 0 | 1,756/2,784 |
| `MA_DAU_DOI_KIEM@kl_64_tot` | 3.57% | 0.0% (0 do thiết kế: không breaker) | thanh 56, hinh_thuc 4,120 | 0 | 3,485/4,176 |
| `MA_DAU_DOI_KIEM@kl_64_xau` | 3.57% | 0.9% | hinh_thuc 4,138, bi_pha 38 | 0 | 3,482/4,176 |
| `NHAT_LE_TRUNG_THIEN@kl_52_85` | 0.57% | 0.0% (0 do thiết kế: không breaker) | thanh 232, hinh_thuc 240, thanh_thuong 200 | 0 | 502/672 |
| `NHAT_NGUYET_TINH_MINH@kl_53_68` | 22.00% | 44.3% | thanh 9,792, bi_pha 11,386, hinh_thuc 4,550 | 0 | 9,940/25,728 |
| `NHAT_NGUYET_TINH_MINH@th_72` | 2.63% | 0.0% | thanh 3,072 | 22,656 | 2,332/3,072 |
| `SAT_PHA_LIEM_THAM@th_76_77` | 25.08% | 5.3% | thanh 12,901, hinh_thuc 14,877, bi_pha 1,550 | 0 | 14,313/29,328 |
| `TAM_KY_GIA_HOI@kl_66` | 3.46% | 28.5% | hinh_thuc 2,894, bi_pha 1,154 | 0 | 3,204/4,048 |
| `THACH_TRUNG_AN_NGOC@kl_106` | 0.60% | 0.0% (0 do thiết kế: không breaker) | hinh_thuc 696 | 1,032 | 116/696 |
| `THACH_TRUNG_AN_NGOC@kl_44` | 1.48% | 0.0% (0 do thiết kế: không breaker) | hinh_thuc 1,728 | 0 | 756/1,728 |
| `THACH_TRUNG_AN_NGOC@kl_58` | 0.03% | 0.0% (0 do thiết kế: không breaker) | hinh_thuc 32 | 1,696 | 32/32 |
| `TU_PHU_DONG_CUNG@kl_50` | 1.64% | 0.0% (0 do thiết kế: không breaker) | thanh_thuong 604, thanh 536, hinh_thuc 780 | 0 | 924/1,920 |
| `TU_PHU_DONG_CUNG@tt_22` | 1.64% | 34.3% | hinh_thuc 1,053, bi_pha 658, thanh 209 | 0 | 763/1,920 |
| `TU_PHU_VU_TUONG@kl_132_193` | 12.60% | 0.0% (0 do thiết kế: không breaker) | thanh 4,200, thanh_thuong 1,744, hinh_thuc 8,792 | 0 | 9,466/14,736 |
| `TU_PHU_VU_TUONG@th_115` | 12.60% | 0.0% (0 do thiết kế: không breaker) | thanh 4,788, thanh_thuong 688, hinh_thuc 9,260 | 0 | 10,389/14,736 |

Phát hiện:

- Chín biến thể không có breaker nên tỷ lệ bị phá 0% là hệ quả thiết kế (sách không nêu phạm vi phá đủ rõ), **không phải** bằng chứng cách đó bền.
- Hai breaker **phân biệt kém**: Cơ Nguyệt Đồng Lương theo TT tr.24 (82,1% bị phá) và Khôi Việt giáp Mệnh theo KL tr.62 (91,7%), vì 'có ít nhất một sát tinh/Không-Kiếp/Kỵ trong tam phương' hầu như luôn đúng. Ngưỡng 'một' là cách đọc của tôi; sách nói 'bị sát tinh hội chiếu' mà không nêu số lượng. Cần chuyên gia quyết định.
- Không biến thể nào đạt `bị phá nhưng được cứu` (không có sao cứu). Không biến thể nào hiện khi lõi baseline vắng.
- Điều kiện không thể xảy ra trong mô hình (giữ nguyên, đã có test): Thiên Tướng hãm (TPVT), Thái Dương hãm ở Ngọ (NLTT), Cự Môn hãm ở Tý/Ngọ (TTAN), Tam Hóa hội cứu của Tử Phủ đồng cung; và Tử Phủ đồng cung × phá được cứu bất khả thi theo hình học của mô hình (`test_formation_geometry.py`) — đó là giới hạn của cách an sao và bảng Tứ Hóa đang dùng, không phải kết luận theo mọi trường phái.

## 7. Kiểm tra tích hợp

- `formations_experimental.json` giữ 10 cách, `definition_version` 2, không id chứa `@`. API `/api/formations` mặc định trả đúng 10 id baseline; `analyse()` chỉ chạy biến thể khi được truyền rõ ràng.
- Không file giao diện hay module sản xuất nào tham chiếu `formations_school_variants`; luận giải chính không chứa id cách cục thử nghiệm. Không thay đổi UI hay API.

## 8. Regression

- Worktree sạch của HEAD `f402574`: **1119 passed, 1 skipped, 2 xfailed, 0 failed (git archive của HEAD, chạy pytest trong engine/)**.
- Ghi chú: Hai test fail ở working tree hiện tại (`test_bazi_deep_tvh_audit`) thuộc thay đổi chưa commit của phiên Bát Tự, không có trong HEAD sạch và không được sửa ở đây. Trong bản xuất sạch, các test đọc PDF dùng sách trong ~/Downloads nên trích dẫn được so với trang thật; khi thiếu PDF chúng tự bỏ qua và KHÔNG được tính là bằng chứng — bằng chứng nằm ở các file JSON đã ghim (`quote_check`) và bản quét/oracle đã commit.

## 9. Quy tắc cần chuyên gia xác nhận

1. Phạm vi của 'hội/gặp' khi câu sách không nêu (Tả Hữu, Xương Khúc, Lộc, Khoa Quyền Lộc, sát tinh): baseline đọc là tam phương.
2. Liệt kê 'Kiếp, Không, Kị' (TT tr.24): một trong số đó là đủ hay phải đủ cả ba.
3. Ngưỡng của sát tinh phá (≥1 sát tinh, '≥3 sát tinh + Kỵ'), và hai breaker phân biệt kém ở mục 6.
4. 'Chiếu' (KL tr.66) = đối cung hay cả tam phương; 'Khôi Việt chiếu' (KL tr.68).
5. Nhâm-Khoa là Tả Phụ (KL) hay Thiên Phủ (TH); Canh-Tân Khôi Việt (Ngọ, Dần) theo TH tr.19 nhưng lớp chữ trang đó bị vỡ, nguồn ghi trong `tuvi.py`.
6. Độ sáng Thái Dương ở Thân/Mùi (dòng TH tr.31 bị cắt).
7. Tuần/Triệt vừa cứu hung tinh vừa hại quý tinh: chọn theo cách cụ thể nào.
8. Ba định nghĩa Thạch trung ẩn ngọc; hai kết cục của Mã đầu đới kiếm; TT tr.142 coi Kình ở Ngọ là xấu và chỉ tốt ở tứ mộ.
9. TT tr.22 nhắc Tử Phủ đồng cung ở Tỵ/Hợi (mô hình chỉ có Dần/Thân) và TH tr.72 cho phép đóng ở Mệnh hay Thân.
10. TH tr.72 (mục 4, 12) chỉ máy-không-kiểm-được; đã đọc từ ảnh, cần người đối chiếu sách giấy (Phase 7 đã xác nhận bằng ảnh, cả TH tr.74).
11. Ngưỡng cơ chế: 2 yếu tố tăng thế → thành thượng; phản chứng hạ một bậc; không cộng điểm.
