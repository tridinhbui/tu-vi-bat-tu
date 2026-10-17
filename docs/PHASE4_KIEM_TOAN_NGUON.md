# Phase 2 — Kiểm toán nguồn học thuật cho 10 cách cục Tử Vi (bản nháp)

Tài liệu sinh bởi `tools/build_formation_audit.py` từ `engine/data/experimental/formation_audit.json`. Mọi dòng được viết sau khi **đọc trực tiếp trang sách** (Khảo Luận = KL, Thực Hành = TH, Toàn Thư = TT; số trang in = chỉ số PDF + 1). Câu trích được so với văn bản trang khi sách có trên máy (`van_ban`); các trang lỗi lớp chữ phải đọc từ ảnh (`anh`). **Không điều kiện nào được đánh dấu verified; toàn bộ cách cục vẫn là `draft`, chỉ hiện ở `?thu-nghiem`.**

## 1. Tổng kết

- Tổng số điều kiện: **93**
- Khớp nguồn (nguồn nói đúng vai trò này): **21**
- Có nguồn một phần nhưng định nghĩa nháp lỏng hơn / chặt hơn: **13 / 11**
- Khác hoặc ngược nguồn: **4**
- Chỉ liên quan (nguồn nói về sao đó nhưng không đúng vai trò): **25**
- Chưa tìm được nguồn: **19**
- Bị loại khỏi định nghĩa 'có nguồn' (giữ như giả thuyết riêng hoặc không thể xảy ra): **43**
- Đề xuất sửa định nghĩa (chuyển cho chủ định nghĩa, chưa áp dụng): **23**
- Quy ước thiết kế được gắn nhãn: **12**; bất đồng giữa trường phái được nêu: **19**

## 2. Bảng kiểm toán 93 điều kiện


### Tử Phủ Vũ Tướng (`CACH_X_TU_PHU_VU_TUONG`)

| Vai trò | Điều kiện | Mức khớp | Nguồn · trang · trích | Lý do | Xử lý |
|---|---|---|---|---|---|
| lõi | `core` — Điều kiện lõi | Khớp | TH p.72 (van_ban): “Tử, Phủ, Vũ, Tướng cách”<br>KL p.132 (van_ban): “cách Tử Phủ Vũ Tướng mà thiếu Tả Hữu” | tên cách có trong danh sách quý cách (TH p.72 mục 7); sách không nêu vị trí chính xác, việc đòi cả bốn sao trong tam phương Mệnh là cách mô hình hóa chuẩn | giữ (có nguồn) |
| tăng thế | `ta_huu_hoi` — Tả Phụ, Hữu Bật cùng hội trong tam phương | Khớp | KL p.132 (van_ban): “cách Tử Phủ Vũ Tướng mà thiếu Tả Hữu” | KL p.132: cách Tử Phủ Vũ Tướng mà thiếu Tả Hữu thì 'đầu Ngô mình Sở' | giữ (có nguồn) |
| tăng thế | `xuong_khuc_hoi` — Văn Xương hoặc Văn Khúc hội trong tam phương | Lỏng hơn nguồn | KL p.193 (van_ban): “Xương Khúc, Tử Phủ Vũ Tướng là người văn võ toàn tài” | sách nói Xương Khúc đi với Tử Phủ Vũ Tướng thì văn võ toàn tài; bản nháp chấp nhận một trong hai sao | giữ (có nguồn) |
| tăng thế | `loc_hoi` — Lộc Tồn hoặc Hóa Lộc hội trong tam phương | Khớp | TH p.115 (van_ban): “Tử, Phủ, Vũ, Tướng có sao Lộc, Long Phượng, Tả Hữu nhất định phát giàu có lớn” | TH p.115 (đại tiểu hạn): Tử Phủ Vũ Tướng gặp sao Lộc thì phát giàu; lưu ý sách nói về hạn, không về bản cách | giữ (có nguồn) |
| phá | `sat_dong_cung` — sát tinh (Kình, Đà, Hỏa, Linh, Không, Kiếp) đồng cung với Mệnh | Chặt hơn nguồn | TH p.116 (van_ban): “Tử Phủ Vũ Tướng găp phải Tam Không, Kiếp Kỵ Hình Đà hay gặp Linh Hỏa Tang Diêu thì bị giáng chức, phá tài”<br>KL p.96 (van_ban): “Nhưng nếu gặp Không Kiếp, Tuần Triệt, Kình Đà, Hỏa Linh thì tài lộc bị giảm đáng kể” | sách nói 'gặp' (Tam Không, Kiếp, Hình, Đà, Linh Hỏa) không giới hạn đồng cung; bản nháp chỉ tính đồng cung Mệnh | đề xuất sửa |
| phá | `ky_dong_cung` — Hóa Kỵ đồng cung với Mệnh | Chặt hơn nguồn | TH p.116 (van_ban): “Tử Phủ Vũ Tướng găp phải Tam Không, Kiếp Kỵ Hình Đà hay gặp Linh Hỏa Tang Diêu thì bị giáng chức, phá tài” | TH p.116 liệt kê Kỵ trong nhóm gặp phải thì giáng chức phá tài; không giới hạn đồng cung | đề xuất sửa |
| cứu | `khoa_dong_cung` — Hóa Khoa đồng cung với Mệnh (giải Kỵ) | Chỉ liên quan | KL p.132 (van_ban): “Hóa khoa, một sao Đại cứu giải” | sách chỉ nói Hóa Khoa là sao giải nói chung (KL p.132), không nói Khoa có quyền cứu riêng cách cục này; không suy ra quyền cứu cách cục từ một đoạn khen sao tốt | giữ như giả thuyết |
| cứu | `tam_hoa_hoi_cuu` — Hóa Lộc, Quyền, Khoa cùng hội trong tam phương (Tam Hóa cứu giải) | Lỏng hơn nguồn | TH p.74 (van_ban): “cần được cứu giải băng Tam hóa hội” | TH p.74 chỉ nói Tam Hóa cứu Mệnh ở bại địa/tuyệt địa (Tuyệt xứ phùng sinh); bản nháp khái quát thành cứu mọi yếu tố phá cách; **quy ước:** 'phá được cứu' là quy ước thiết kế, không phải kết luận cổ thư | đề xuất sửa |
| phản chứng | `tuan_triet_an_ngu` — Tuần hoặc Triệt đóng ở cung Mệnh | Khớp | KL p.222 (van_ban): “Mệnh có Vũ Tướng mà không bị Tuần Triệt án ngữ thì cuộc đời suôn”<br>TH p.94 (van_ban): “Nhưng nếu Phủ gặp Tuần Triệt hay Thiên, Địa Không”<br>TH p.95 (van_ban): “Nhưng nếu Tướng miếu vượng đắc địa mà gặp Tuần Triệt án ngữ, chẳng khác nào như Tướng hãm địa” | Vũ Tướng/Thiên Phủ/Thiên Tướng đều bị Tuần Triệt làm hại; việc 'hạ một bậc' là quy ước thiết kế; **trường phái:** Tuần/Triệt có hai vai trò trái nhau trong sách: giải hung tinh/hãm tinh (KL p.199-201, p.85) và làm hại quý tinh (KL p.55, TH p.94-95); kết luận theo từng cách phải nêu trường phái; **quy ước:** hạ một bậc là quy ước thiết kế | giữ (có nguồn) |
| phản chứng | `Thiên_Tướng_ham` — Thiên Tướng ở vị trí hãm (độ sáng thấp nhất trong bảng) | Chỉ liên quan | TH p.95 (van_ban): “Nhưng nếu Tướng miếu vượng đắc địa mà gặp Tuần Triệt án ngữ, chẳng khác nào như Tướng hãm địa” | TH p.95 nói Tướng gặp Tuần Triệt 'như hãm', không nói Tướng hãm hạ cả cách; điều kiện không thể xảy ra vì Thiên Tướng hãm chỉ ở Mão/Dậu, nơi không hình thành đủ bốn sao | không thể xảy ra |

### Tử Phủ đồng cung (`CACH_X_TU_PHU_DONG_CUNG`)

| Vai trò | Điều kiện | Mức khớp | Nguồn · trang · trích | Lý do | Xử lý |
|---|---|---|---|---|---|
| lõi | `core` — Điều kiện lõi | Chặt hơn nguồn | TH p.72 (van_ban): “Tử, Phủ đồng cung cáh (đóng ở Mệnh hay Thân)”<br>TT p.22 (van_ban): “Tử Phủ đồng cung vô sát tấu” | TH p.72 mục 1: đóng ở Mệnh HAY Thân; bản nháp chỉ neo ở Mệnh. TT p.22 còn nhắc cả Tỵ/Hợi nơi mô hình không có Tử Phủ đồng cung (bất đồng nguồn); **trường phái:** TT p.22 nói Tử Phủ đồng cung ở Tỵ/Hợi; mô hình (và KL p.49) chỉ có ở Dần/Thân | đề xuất sửa |
| tăng thế | `ta_huu_hoi` — Tả Phụ, Hữu Bật cùng hội trong tam phương | Khớp | TT p.22 (van_ban): “Tử Vi Thiên Phủ toàn y phụ bật chi công” | TT p.22: 'Tử Vi Thiên Phủ toàn y Phụ Bật chi công' (Tử Vi và Thiên Phủ cần dựa vào Tả Phụ Hữu Bật mới dễ bề phú quí); phạm vi 'dựa vào' không nêu. Nguồn cùng cấu trúc (Phase 8: thay cho câu KL p.49 nói riêng về Tử Vi) | giữ (có nguồn) |
| tăng thế | `xuong_khuc_hoi` — Văn Xương hoặc Văn Khúc hội trong tam phương | Lỏng hơn nguồn | KL p.96 (van_ban): “Nếu Thiên phủ đi với Tử vi, Xương Khúc, Hóa khoa, Thiên việt, Thiên khôi thì rất mạnh” | KL p.96: Thiên Phủ đi với Tử Vi, Xương Khúc, Hóa Khoa, Thiên Việt, Thiên Khôi thì rất mạnh; bản nháp chấp nhận một trong hai sao, phạm vi 'đi với' không nêu | giữ (có nguồn) |
| tăng thế | `khoi_viet_hoi` — Thiên Khôi hoặc Thiên Việt hội trong tam phương | Lỏng hơn nguồn | KL p.96 (van_ban): “Nếu Thiên phủ đi với Tử vi, Xương Khúc, Hóa khoa, Thiên việt, Thiên khôi thì rất mạnh” | KL p.96 (như trên): Thiên Việt, Thiên Khôi; bản nháp chấp nhận một trong hai | giữ (có nguồn) |
| phá | `sat_dong_cung` — sát tinh (Kình, Đà, Hỏa, Linh, Không, Kiếp) đồng cung với Mệnh | Khác/ngược nguồn | TT p.22 (van_ban): “Tử Phủ đồng cung vô sát tấu”<br>KL p.50 (van_ban): “Tử vi, Thiên phủ đồng cung với Kình dương, lực sĩ thì buôn bán giàu có” | TT p.22: Tử Phủ đồng cung 'vô sát tấu' mới hưởng phúc (ủng hộ); nhưng KL p.50 nói Tử Phủ đồng cung với Kình Dương thì buôn bán giàu có (ngược lại); **trường phái:** TT p.22 (sát tinh làm hỏng) trái KL p.50 (Kình Dương đồng cung vẫn giàu) | đề xuất sửa |
| phá | `ky_dong_cung` — Hóa Kỵ đồng cung với Mệnh | Khác/ngược nguồn | KL p.50 (van_ban): “Mệnh ở Dần có Hoá kỵ, Hóa quyền đồng cung với Tử Phủ là người mưu cơ tài trí” | KL p.50: Tử Phủ cùng Hóa Kỵ, Hóa Quyền ở Dần là người mưu cơ tài trí; không coi Kỵ là yếu tố phá | đề xuất sửa |
| cứu | `khoa_dong_cung` — Hóa Khoa đồng cung với Mệnh (giải Kỵ) | Chỉ liên quan | KL p.132 (van_ban): “Hóa khoa, một sao Đại cứu giải” | sách chỉ nói Hóa Khoa là sao giải nói chung (KL p.132), không nói Khoa có quyền cứu riêng cách cục này; không suy ra quyền cứu cách cục từ một đoạn khen sao tốt | giữ như giả thuyết |
| cứu | `tam_hoa_hoi_cuu` — Hóa Lộc, Quyền, Khoa cùng hội trong tam phương (Tam Hóa cứu giải) | Lỏng hơn nguồn | TH p.74 (van_ban): “cần được cứu giải băng Tam hóa hội” | như mọi cách: Tam Hóa chỉ được sách nói là cứu bại/tuyệt địa. Ngoài ra điều kiện này KHÔNG BAO GIỜ đúng ở Dần/Thân (Tam Hóa không bao giờ hội đủ trong tam phương của Dần/Thân khi có Tử Vi+Thiên Phủ): ràng buộc hình học của mô hình; **quy ước:** 'phá được cứu' là quy ước thiết kế | không thể xảy ra |
| phản chứng | `tuan_triet_an_ngu` — Tuần hoặc Triệt đóng ở cung Mệnh | Khớp | KL p.55 (van_ban): “chỉ sợ Triệt Tuần án ngữ thì kém đi thôi”<br>TH p.94 (van_ban): “Nhưng nếu Phủ gặp Tuần Triệt hay Thiên, Địa Không” | KL p.55: Tử Phủ đồng cung chỉ sợ Triệt Tuần án ngữ; TH p.94: Thiên Phủ kỵ Tuần Triệt; **trường phái:** Tuần/Triệt có hai vai trò trái nhau trong sách: giải hung tinh/hãm tinh (KL p.199-201, p.85) và làm hại quý tinh (KL p.55, TH p.94-95); kết luận theo từng cách phải nêu trường phái; **quy ước:** hạ một bậc là quy ước thiết kế | giữ (có nguồn) |

### Cơ Nguyệt Đồng Lương (`CACH_X_CO_NGUYET_DONG_LUONG`)

| Vai trò | Điều kiện | Mức khớp | Nguồn · trang · trích | Lý do | Xử lý |
|---|---|---|---|---|---|
| lõi | `core` — Điều kiện lõi | Khớp | TT p.24 (van_ban): “Mệnh thân và các cung tam hợp xang chiếu có đủ bốn sao trên đây”<br>KL p.51 (van_ban): “Mệnh có Cơ Nguyệt Đồng Lương hội chiếu thường là công chức” | TT p.24 đòi đủ bốn sao ở Mệnh/Thân và tam hợp xung chiếu: trùng định nghĩa; KL p.51 chỉ nói 'hội chiếu' | giữ (có nguồn) |
| tăng thế | `cat_tinh_hoi` — một cát tinh (Tả, Hữu, Xương, Khúc, Khôi, Việt) hội trong tam phương | Khớp | TT p.24 (van_ban): “Mệnh thân và các cung tam hợp xang chiếu có đủ bốn sao trên đây”<br>TH p.77 (van_ban): “Nguyệt Đồng Lương hội Tả Hữu, Thai Cáo, Xương Khúc tất là hàng công chức” | TT p.24: thiếu cát tinh trợ lực chỉ là công chức quèn; TH p.77 kể Tả Hữu, Thai Cáo, Xương Khúc (vẫn là công chức); danh sách 6 cát tinh là chọn lọc của bản nháp; **trường phái:** TT p.24 / TH p.77 coi hội cát tinh vẫn chỉ ở mức công chức; KL p.221 (ảnh) nói hội Khoa Quyền Lộc, Khôi Việt, Xương Khúc thì giáo sư danh tiếng: mức 'tốt' khác nhau giữa các sách | giữ (có nguồn) |
| tăng thế | `khoa_quyen_loc_hoi` — Hóa Khoa, Quyền hoặc Lộc hội trong tam phương | Khớp | KL p.221 (van_ban): “Quyền Lộc, Khôi Việt, Xương khúc thì làm giáo sư danh tiếng” | KL p.221: CNDL hội (Khoa) Quyền Lộc, Khôi Việt, Xương Khúc thì làm giáo sư danh tiếng; chữ 'Khoa' bị mất ở lớp chữ của trang, đọc bổ sung từ ảnh; **trường phái:** xem cat_tinh_hoi | giữ (có nguồn) |
| phá | `khong_kiep_dong_cung` — Địa Không hoặc Địa Kiếp đồng cung với Mệnh | Chặt hơn nguồn | TT p.24 (van_ban): “Gặp Kiếp Không Hoá Kị xuống hạ cách”<br>TH p.116 (van_ban): “Cơ Nguyệt Đồng Lương hay Cự Nhật mà gặp Kình Đà, Không Kiếp hay Phá toái, Kiếp sát” | TT p.24 và TH p.116: 'gặp' Kiếp, Không (không giới hạn đồng cung Mệnh) | đề xuất sửa |
| phá | `ky_dong_cung` — Hóa Kỵ đồng cung với Mệnh | Chặt hơn nguồn | TT p.24 (van_ban): “Gặp Kiếp Không Hoá Kị xuống hạ cách” | TT p.24: gặp Hóa Kị thì xuống hạ cách (áp dụng cho cả cấu trúc, không chỉ đồng cung Mệnh) | đề xuất sửa |
| cứu | `khoa_dong_cung` — Hóa Khoa đồng cung với Mệnh (giải Kỵ) | Chỉ liên quan | KL p.132 (van_ban): “Hóa khoa, một sao Đại cứu giải” | sách chỉ nói Hóa Khoa là sao giải nói chung (KL p.132), không nói Khoa có quyền cứu riêng cách cục này; không suy ra quyền cứu cách cục từ một đoạn khen sao tốt | giữ như giả thuyết |
| cứu | `tam_hoa_hoi_cuu` — Hóa Lộc, Quyền, Khoa cùng hội trong tam phương (Tam Hóa cứu giải) | Lỏng hơn nguồn | TH p.74 (van_ban): “cần được cứu giải băng Tam hóa hội” | TH p.74 chỉ nói Tam Hóa cứu Mệnh ở bại địa/tuyệt địa (Tuyệt xứ phùng sinh); bản nháp khái quát thành cứu mọi yếu tố phá cách; **quy ước:** 'phá được cứu' là quy ước thiết kế, không phải kết luận cổ thư | đề xuất sửa |
| phản chứng | `tuan_triet_an_ngu` — Tuần hoặc Triệt đóng ở cung Mệnh | Chỉ liên quan | TH p.94 (van_ban): “Nhưng nếu Phủ gặp Tuần Triệt hay Thiên, Địa Không” | TH p.94-95 chỉ nói Thái Âm, Thiên Lương gặp Tuần Triệt là bất lợi; không nói cả cách CNDL; **trường phái:** Tuần/Triệt có hai vai trò trái nhau trong sách: giải hung tinh/hãm tinh (KL p.199-201, p.85) và làm hại quý tinh (KL p.55, TH p.94-95); kết luận theo từng cách phải nêu trường phái | giữ như giả thuyết |

### Sát Phá Liêm Tham (`CACH_X_SAT_PHA_LIEM_THAM`)

| Vai trò | Điều kiện | Mức khớp | Nguồn · trang · trích | Lý do | Xử lý |
|---|---|---|---|---|---|
| lõi | `core` — Điều kiện lõi | Chỉ liên quan | TH p.72 (anh_doc_ro): “Sát, Phá, Liêm, Tham cách” | tên cách có trong TH p.72 mục 4 (đọc từ ảnh), nhưng sách không nêu số sao cần có; ngưỡng '3 trong 4 sao' là quy ước thiết kế; **quy ước:** ngưỡng 3 trong 4 sao là quy ước thiết kế, sách không nêu | quy ước thiết kế |
| tăng thế | `khoa_quyen_hoi` — Hóa Khoa hoặc Hóa Quyền hội trong tam phương | Khớp | TH p.76 (van_ban): “Hồng Đào, Khoa Quyền. Lộc, Kình, Không” | TH p.76: Sát Phá Liêm Tham miếu vượng hội cát tinh gồm Khoa Quyền Lộc (nhóm phi thường cách); **trường phái:** TH p.76 cũng đếm Kình, Không trong nhóm cát hội; KL p.221 không coi sát tinh là yếu tố phá | giữ (có nguồn) |
| tăng thế | `ta_huu_hoi` — Tả Phụ, Hữu Bật cùng hội trong tam phương | Chỉ liên quan | TH p.76 (van_ban): “hội Tả, Hữu, Xương Khúc, Khôi Việt, Long Phượng, Hồng Đào, Tam Hóa” | danh sách cát tinh của TH p.76 là cho nhóm Thượng cách (Tử Phủ Vũ Tướng, Cơ Nguyệt, Cự Nhật...), không riêng cho SPLT | giữ như giả thuyết |
| tăng thế | `xuong_khuc_hoi` — Văn Xương hoặc Văn Khúc hội trong tam phương | Chỉ liên quan | TH p.76 (van_ban): “hội Tả, Hữu, Xương Khúc, Khôi Việt, Long Phượng, Hồng Đào, Tam Hóa” | như trên | giữ như giả thuyết |
| tăng thế | `khoi_viet_hoi` — Thiên Khôi hoặc Thiên Việt hội trong tam phương | Chỉ liên quan | TH p.76 (van_ban): “hội Tả, Hữu, Xương Khúc, Khôi Việt, Long Phượng, Hồng Đào, Tam Hóa” | như trên | giữ như giả thuyết |
| phá | `ba_sat_va_ky_trong_tam_phuong` — từ ba sát tinh trở lên và Hóa Kỵ cùng trong tam phương | Chặt hơn nguồn | TH p.77 (van_ban): “Sát Phá Liêm Tham hội Vũ, Kình Đà”<br>TH p.116 (van_ban): “Sát phá Liêm Tham mà gặp Nhị tam Không, Linh Hỏa Kình Kỵ” | TH p.77: hạ cách khi hội Vũ, Kình Đà, Thiên Địa Không... 'nhiều' hung sát ở hãm địa; bản nháp đòi từ 3 sát tinh VÀ Hóa Kỵ. Con số 3 và điều kiện kèm Kỵ là quy ước thiết kế; **trường phái:** TH p.76 xếp Kình, Không vào nhóm cát hội của SPLT, trái TH p.77; **quy ước:** ngưỡng '3 sát tinh + Kỵ' là quy ước thiết kế | quy ước thiết kế |
| phá | `ky_dong_cung` — Hóa Kỵ đồng cung với Mệnh | Chặt hơn nguồn | TH p.116 (van_ban): “Sát phá Liêm Tham mà gặp Nhị tam Không, Linh Hỏa Kình Kỵ” | TH p.116: gặp Linh Hỏa Kình Kỵ thì tù ngục vong gia; không giới hạn đồng cung | đề xuất sửa |
| cứu | `khoa_dong_cung` — Hóa Khoa đồng cung với Mệnh (giải Kỵ) | Chỉ liên quan | KL p.132 (van_ban): “Hóa khoa, một sao Đại cứu giải” | sách chỉ nói Hóa Khoa là sao giải nói chung (KL p.132), không nói Khoa có quyền cứu riêng cách cục này; không suy ra quyền cứu cách cục từ một đoạn khen sao tốt | giữ như giả thuyết |
| cứu | `tam_hoa_hoi_cuu` — Hóa Lộc, Quyền, Khoa cùng hội trong tam phương (Tam Hóa cứu giải) | Lỏng hơn nguồn | TH p.74 (van_ban): “cần được cứu giải băng Tam hóa hội” | TH p.74 chỉ nói Tam Hóa cứu Mệnh ở bại địa/tuyệt địa (Tuyệt xứ phùng sinh); bản nháp khái quát thành cứu mọi yếu tố phá cách; **quy ước:** 'phá được cứu' là quy ước thiết kế, không phải kết luận cổ thư | đề xuất sửa |
| phản chứng | `tuan_triet_an_ngu` — Tuần hoặc Triệt đóng ở cung Mệnh | Chưa có nguồn | — | không có trang nói Tuần/Triệt làm hại cách này; sách chỉ nói về từng sao; **trường phái:** Tuần/Triệt có hai vai trò trái nhau trong sách: giải hung tinh/hãm tinh (KL p.199-201, p.85) và làm hại quý tinh (KL p.55, TH p.94-95); kết luận theo từng cách phải nêu trường phái | giữ như giả thuyết |
| phản chứng | `Thất_Sát_ham` — Thất Sát ở vị trí hãm (độ sáng thấp nhất trong bảng) | Chưa có nguồn | — | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế | giữ như giả thuyết |

### Nhật Nguyệt tịnh minh (`CACH_X_NHAT_NGUYET_TINH_MINH`)

| Vai trò | Điều kiện | Mức khớp | Nguồn · trang · trích | Lý do | Xử lý |
|---|---|---|---|---|---|
| lõi | `core` — Điều kiện lõi | Lỏng hơn nguồn | TH p.72 (van_ban): “Nhật, Nguyệt tinh minh cách (Nhật ở Thìn, Tỵ, Nguyệt ở Dậu, Tuất, mà Mệnh đóng ở Nguyệt hay Nhật đều tốt)”<br>KL p.53 (van_ban): “Nhật nguyệt thủ Mệnh bất như hợp chiếu tịnh minh” | TH p.72: Nhật ở Thìn/Tỵ, Nguyệt ở Dậu/Tuất và Mệnh đóng ở Nhật hay Nguyệt; KL p.53 chỉ cần Nhật Nguyệt hợp chiếu Mệnh (ví dụ Mệnh Sửu). Bản nháp theo KL (rộng hơn TH); **trường phái:** TH p.72 (vị trí cố định) khác KL p.53 (hợp chiếu tịnh minh) | đề xuất sửa |
| tăng thế | `nhat_nguyet_deu_sang` — Thái Dương và Thái Âm đều sáng (độ sáng từ đắc trở lên) | Khớp | TT p.142 (van_ban): “Thái Dương đều đứng ở miếu vượng địa chiếu sáng”<br>KL p.53 (van_ban): “Nhật nguyệt thủ Mệnh bất như hợp chiếu tịnh minh” | TT p.142: cả hai sao ở miếu vượng; KL p.53: đắc địa; ngưỡng bản nháp 'đắc trở lên' theo KL; **trường phái:** TT nói miếu vượng, KL nói đắc địa | giữ (có nguồn) |
| tăng thế | `ta_huu_hoi` — Tả Phụ, Hữu Bật cùng hội trong tam phương | Chỉ liên quan | KL p.56 (van_ban): “Mệnh có Thái âm đắc địa, hoặc Vũ khúc đắc địa được Lộc tồn, Tả Hữu hợp chiếu thì giàu lớn” | KL p.56 nói Tả Hữu giúp Thái Âm/Vũ Khúc, không nói riêng Nhật Nguyệt tịnh minh | giữ như giả thuyết |
| tăng thế | `khoa_quyen_hoi` — Hóa Khoa hoặc Hóa Quyền hội trong tam phương | Chỉ liên quan | KL p.53 (van_ban): “lại không có Đào Hồng Hỉ hay Khoa Quyền Lộc hợp chiếu” | KL p.53 mục 8 nói Khoa Quyền Lộc hợp chiếu giúp Nhật Nguyệt Sửu Mùi; chưa phải cách tịnh minh | giữ như giả thuyết |
| phá | `nhat_nguyet_ham_gap_sat` — Thái Dương hoặc Thái Âm hãm, lại có sát tinh trong tam phương | Khớp | TH p.74 (van_ban): “Nhật Nguyệt hãm tại Mệnh mà không có cứu tinh”<br>KL p.56 (van_ban): “Mệnh có Nhật hay Nguyệt hãm địa gặp Kình, Đà, Không Kiếp thì bôn ba khốn khổ” | TH p.74 (bần tiện cách số 7, từ ảnh) và KL p.56: Nhật/Nguyệt hãm gặp sát tinh thì khốn khổ | giữ (có nguồn) |
| phá | `ky_dong_cung` — Hóa Kỵ đồng cung với Mệnh | Chỉ liên quan | KL p.85 (van_ban): “Thái dương ghét lũ Riêu, Đà, Kỵ” | KL p.85 nói Thái Dương ghét Kỵ nhưng không nêu cho cách tịnh minh | giữ như giả thuyết |
| phá | `khong_kiep_dong_cung` — Địa Không hoặc Địa Kiếp đồng cung với Mệnh | Chỉ liên quan | KL p.56 (van_ban): “Mệnh có Nhật hay Nguyệt hãm địa gặp Kình, Đà, Không Kiếp thì bôn ba khốn khổ” | KL p.56 nói Nhật/Nguyệt HÃM gặp Không Kiếp; bản nháp áp dụng cho cả khi sáng | giữ như giả thuyết |
| cứu | `khoa_dong_cung` — Hóa Khoa đồng cung với Mệnh (giải Kỵ) | Chỉ liên quan | KL p.132 (van_ban): “Hóa khoa, một sao Đại cứu giải” | sách chỉ nói Hóa Khoa là sao giải nói chung (KL p.132), không nói Khoa có quyền cứu riêng cách cục này; không suy ra quyền cứu cách cục từ một đoạn khen sao tốt | giữ như giả thuyết |
| cứu | `tam_hoa_hoi_cuu` — Hóa Lộc, Quyền, Khoa cùng hội trong tam phương (Tam Hóa cứu giải) | Lỏng hơn nguồn | TH p.74 (van_ban): “cần được cứu giải băng Tam hóa hội” | TH p.74 chỉ nói Tam Hóa cứu Mệnh ở bại địa/tuyệt địa (Tuyệt xứ phùng sinh); bản nháp khái quát thành cứu mọi yếu tố phá cách; **quy ước:** 'phá được cứu' là quy ước thiết kế, không phải kết luận cổ thư | đề xuất sửa |
| phản chứng | `Thái_Dương_ham` — Thái Dương ở vị trí hãm (độ sáng thấp nhất trong bảng) | Chặt hơn nguồn | TH p.74 (van_ban): “Nhật Nguyệt hãm tại Mệnh mà không có cứu tinh”<br>KL p.68 (van_ban): “chỉ mong được Khôi Việt chiếu mới là tốt đẹp” | TH p.74: hãm tại Mệnh KHÔNG có cứu tinh mới là tàn hung; KL p.68 cho Khôi Việt chiếu là cứu. Bản nháp hạ mọi trường hợp hãm; **trường phái:** Tuần/Triệt vừa cứu Nhật hãm (KL p.85) vừa hại Thái Âm (TH p.94) | đề xuất sửa |
| phản chứng | `Thái_Âm_ham` — Thái Âm ở vị trí hãm (độ sáng thấp nhất trong bảng) | Chặt hơn nguồn | TH p.74 (van_ban): “Nhật Nguyệt hãm tại Mệnh mà không có cứu tinh”<br>KL p.68 (van_ban): “chỉ mong được Khôi Việt chiếu mới là tốt đẹp” | như Thái Dương hãm | đề xuất sửa |
| phản chứng | `tuan_triet_an_ngu` — Tuần hoặc Triệt đóng ở cung Mệnh | Khác/ngược nguồn | KL p.53 (van_ban): “rất cần Tuần không án ngữ ở Mệnh”<br>KL p.85 (van_ban): “Thái dương hãm địa, cần gặp Tuần, Triệt, cũng cần gặp Đào, Hồng, Hỉ giúp sức” | KL p.53 mục 11 nói Nhật Nguyệt Sửu Mùi RẤT CẦN Tuần án ngữ; KL p.85 Tuần Triệt giải Thái Dương hãm: ngược với việc coi Tuần/Triệt là phản chứng; **trường phái:** Tuần/Triệt có hai vai trò trái nhau trong sách: giải hung tinh/hãm tinh (KL p.199-201, p.85) và làm hại quý tinh (KL p.55, TH p.94-95); kết luận theo từng cách phải nêu trường phái | đề xuất sửa |

### Nhật lệ trung thiên (`CACH_X_NHAT_LE_TRUNG_THIEN`)

| Vai trò | Điều kiện | Mức khớp | Nguồn · trang · trích | Lý do | Xử lý |
|---|---|---|---|---|---|
| lõi | `core` — Điều kiện lõi | Khớp | TH p.72 (van_ban): “Nhật lệ trung thiên cách ( Nhật cư Ngọ có Mệnh)”<br>KL p.52 (van_ban): “Mệnh có Thái dương ở Ngọ, vi như mặt trời chiếu sáng giữa trưa” | TH p.72 mục 22 và KL p.52: Thái Dương cư Ngọ ở Mệnh | giữ (có nguồn) |
| tăng thế | `ta_huu_hoi` — Tả Phụ, Hữu Bật cùng hội trong tam phương | Chưa có nguồn | — | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế | giữ như giả thuyết |
| tăng thế | `khoa_quyen_hoi` — Hóa Khoa hoặc Hóa Quyền hội trong tam phương | Khớp | KL p.85 (van_ban): “Thái dương thích Xương, Khúc, Khoa, Quyền, Lộc” | KL p.85: Thái Dương thích Xương Khúc, Khoa Quyền Lộc | giữ (có nguồn) |
| tăng thế | `xuong_khuc_hoi` — Văn Xương hoặc Văn Khúc hội trong tam phương | Khớp | KL p.85 (van_ban): “Thái dương thích Xương, Khúc, Khoa, Quyền, Lộc” | KL p.85: Thái Dương thích Xương Khúc, Khoa Quyền Lộc | giữ (có nguồn) |
| phá | `sat_dong_cung` — sát tinh (Kình, Đà, Hỏa, Linh, Không, Kiếp) đồng cung với Mệnh | Chỉ liên quan | KL p.85 (van_ban): “Thái dương sợ: Kình, Đà, Không, Kiếp, gặp đám sát tinh này thì công danh trắc trở” | KL p.85 (nói về sao Thái Dương ở mọi cung, không riêng Ngọ): Thái Dương sợ Kình, Đà, Không, Kiếp 'gặp' thì công danh trắc trở, và 'cần Tuần Triệt cứu giải' — KL nói Tuần/Triệt cứu cho Thái Dương, không cho cách Nhật lệ trung thiên; phạm vi 'gặp' không nêu | giữ như giả thuyết |
| phá | `ky_dong_cung` — Hóa Kỵ đồng cung với Mệnh | Chặt hơn nguồn | KL p.85 (van_ban): “Thái dương ghét lũ Riêu, Đà, Kỵ” | KL p.85: Thái Dương ghét Kỵ (không giới hạn đồng cung) | đề xuất sửa |
| cứu | `khoa_dong_cung` — Hóa Khoa đồng cung với Mệnh (giải Kỵ) | Chỉ liên quan | KL p.132 (van_ban): “Hóa khoa, một sao Đại cứu giải” | sách chỉ nói Hóa Khoa là sao giải nói chung (KL p.132), không nói Khoa có quyền cứu riêng cách cục này; không suy ra quyền cứu cách cục từ một đoạn khen sao tốt | giữ như giả thuyết |
| cứu | `tam_hoa_hoi_cuu` — Hóa Lộc, Quyền, Khoa cùng hội trong tam phương (Tam Hóa cứu giải) | Lỏng hơn nguồn | TH p.74 (van_ban): “cần được cứu giải băng Tam hóa hội” | TH p.74 chỉ nói Tam Hóa cứu Mệnh ở bại địa/tuyệt địa (Tuyệt xứ phùng sinh); bản nháp khái quát thành cứu mọi yếu tố phá cách; **quy ước:** 'phá được cứu' là quy ước thiết kế, không phải kết luận cổ thư | đề xuất sửa |
| phản chứng | `tuan_triet_an_ngu` — Tuần hoặc Triệt đóng ở cung Mệnh | Chưa có nguồn | KL p.85 (van_ban): “Thái dương hãm địa, cần gặp Tuần, Triệt, cũng cần gặp Đào, Hồng, Hỉ giúp sức” | Tuần/Triệt trong sách giúp Thái Dương HÃM; với Thái Dương vượng ở Ngọ không có trang nói Tuần/Triệt gây hại; **trường phái:** Tuần/Triệt có hai vai trò trái nhau trong sách: giải hung tinh/hãm tinh (KL p.199-201, p.85) và làm hại quý tinh (KL p.55, TH p.94-95); kết luận theo từng cách phải nêu trường phái | giữ như giả thuyết |
| phản chứng | `Thái_Dương_ham` — Thái Dương ở vị trí hãm (độ sáng thấp nhất trong bảng) | Chưa có nguồn | — | Không thể xảy ra: Thái Dương ở Ngọ luôn vượng theo bảng miếu vượng, nên điều kiện (bảng độ sáng) không bao giờ đúng; đây không phải lỗi logic mà là hệ quả của bảng | không thể xảy ra |

### Thạch trung ẩn ngọc (`CACH_X_THACH_TRUNG_AN_NGOC`)

| Vai trò | Điều kiện | Mức khớp | Nguồn · trang · trích | Lý do | Xử lý |
|---|---|---|---|---|---|
| lõi | `core` — Điều kiện lõi | Khớp | KL p.58 (van_ban): “Mệnh ở Tí Ngọ có Cự môn được Khoa Quyền Lộc tam hợp chiếu là cách ngọc ở trong đá”<br>KL p.44 (van_ban): “Thạch trung ẩn ngọc -Ngọc quí ở trong đá -Mệnh có Cự môn, Di có Thiên cơ ở Tí Ngọ” | KL p.58: Mệnh ở Tí/Ngọ có Cự Môn; KL p.44 lại định nghĩa Mệnh Cự Môn + Di Thiên Cơ ở Tí Ngọ (ba định nghĩa khác nhau giữa KL p.44, KL p.58 và TH p.43); **trường phái:** KL p.44 (Mệnh Cự, Di Cơ) / KL p.58 (cần Khoa Quyền Lộc) / KL p.106 và TH p.43 (cần Tuần Triệt hoặc Hóa Lộc) là ba điều kiện khác nhau | giữ (có nguồn) |
| tăng thế | `tam_hoa_hoi_du` — Hóa Khoa, Quyền và Lộc cùng hội đủ trong tam phương | Khớp | KL p.58 (van_ban): “Mệnh ở Tí Ngọ có Cự môn được Khoa Quyền Lộc tam hợp chiếu là cách ngọc ở trong đá”<br>TT p.142 (van_ban): “Khoa, Quyền lộc củng (Chiếu thủ có cả ba Khoa, Quyền, Lộc)” | KL p.58: Khoa Quyền Lộc tam hợp chiếu là cách ngọc ở trong đá | giữ (có nguồn) |
| tăng thế | `ta_huu_hoi` — Tả Phụ, Hữu Bật cùng hội trong tam phương | Chưa có nguồn | — | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế | giữ như giả thuyết |
| phá | `ky_hoac_kinh_dong_cung` — Hóa Kỵ hoặc Kình Dương đồng cung với Mệnh | Chưa có nguồn | — | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế | giữ như giả thuyết |
| cứu | `khoa_dong_cung` — Hóa Khoa đồng cung với Mệnh (giải Kỵ) | Chỉ liên quan | KL p.132 (van_ban): “Hóa khoa, một sao Đại cứu giải” | sách chỉ nói Hóa Khoa là sao giải nói chung (KL p.132), không nói Khoa có quyền cứu riêng cách cục này; không suy ra quyền cứu cách cục từ một đoạn khen sao tốt | giữ như giả thuyết |
| phản chứng | `tuan_triet_an_ngu` — Tuần hoặc Triệt đóng ở cung Mệnh | Khác/ngược nguồn | KL p.106 (van_ban): “Cự môn ở Tí Ngọ gặp Tuần Triệt là kỳ cách”<br>TH p.43 (van_ban): “cần gặp được Tuần, Triệt hay Hóa Lộc thì ngọc mới lộ ra được” | KL p.106: Cự Môn Tí Ngọ gặp Tuần Triệt là kỳ cách; TH p.43: cần Tuần, Triệt hay Hóa Lộc: ngược với việc dùng Tuần/Triệt làm phản chứng; **trường phái:** Tuần/Triệt có hai vai trò trái nhau trong sách: giải hung tinh/hãm tinh (KL p.199-201, p.85) và làm hại quý tinh (KL p.55, TH p.94-95); kết luận theo từng cách phải nêu trường phái | đề xuất sửa |
| phản chứng | `Cự_Môn_ham` — Cự Môn ở vị trí hãm (độ sáng thấp nhất trong bảng) | Chưa có nguồn | — | Không thể xảy ra: Cự Môn ở Tí/Ngọ luôn vượng theo bảng miếu vượng; không phải lỗi logic mà là hệ quả của bảng | không thể xảy ra |

### Mã đầu đới kiếm (`CACH_X_MA_DAU_DOI_KIEM`)

| Vai trò | Điều kiện | Mức khớp | Nguồn · trang · trích | Lý do | Xử lý |
|---|---|---|---|---|---|
| lõi | `core` — Điều kiện lõi | Khớp | KL p.64 (van_ban): “Mệnh ở Ngọ, có Kình dương, gặp Thất sát, Thiên hình đồng cung là cách kiếm kể cổ ngựa”<br>KL p.64 (van_ban): “có Kình dương đồng cung, nhưng xa lánh được Thất sát, Thiên hình mà lại gặp được Khoa Quyền Lộc”<br>TT p.142 (van_ban): “phải ở tứ mộ địa mới hay, ở Ngọ cung xấu” | KL p.64 mục 5-6: Mệnh ở Ngọ có Kình Dương; TT p.142 nói Kình ở Ngọ là xấu (khác KL mục 6); **trường phái:** KL p.64 mục 5 xấu / mục 6 tốt cùng một vị trí; TT p.142 cho rằng Kình ở Ngọ xấu | giữ (có nguồn) |
| tăng thế | `khoa_quyen_loc_hoi` — Hóa Khoa, Quyền hoặc Lộc hội trong tam phương | Khớp | KL p.64 (van_ban): “có Kình dương đồng cung, nhưng xa lánh được Thất sát, Thiên hình mà lại gặp được Khoa Quyền Lộc” | KL p.64 mục 6: gặp Khoa Quyền Lộc thì sự nghiệp lớn về võ nghiệp (điều kiện kèm xa lánh Thất Sát, Thiên Hình) | giữ (có nguồn) |
| tăng thế | `ta_huu_hoi` — Tả Phụ, Hữu Bật cùng hội trong tam phương | Chưa có nguồn | — | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế | giữ như giả thuyết |
| phá | `that_sat_trong_tam_phuong` — Thất Sát hội trong tam phương | Lỏng hơn nguồn | KL p.64 (van_ban): “Mệnh ở Ngọ, có Kình dương, gặp Thất sát, Thiên hình đồng cung là cách kiếm kể cổ ngựa”<br>KL p.60 (van_ban): “có Thất sát Kình dương toạ thủ, lại thêm nhiều sát tinh hội chiếu” | KL p.64 mục 5: Thất Sát, Thiên Hình ĐỒNG CUNG với Kình; KL p.60: Thất Sát Kình tọa thủ + nhiều sát tinh hội chiếu. Bản nháp tính cả tam phương | đề xuất sửa |
| phá | `sat_khac_dong_cung` — Hỏa, Linh, Không hoặc Kiếp đồng cung với Mệnh | Chỉ liên quan | KL p.60 (van_ban): “có Thất sát Kình dương toạ thủ, lại thêm nhiều sát tinh hội chiếu” | KL p.60 nói 'nhiều sát tinh hội chiếu', không phải đồng cung | giữ như giả thuyết |
| phá | `ky_dong_cung` — Hóa Kỵ đồng cung với Mệnh | Chưa có nguồn | — | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế | giữ như giả thuyết |
| cứu | `khoa_dong_cung` — Hóa Khoa đồng cung với Mệnh (giải Kỵ) | Chỉ liên quan | KL p.132 (van_ban): “Hóa khoa, một sao Đại cứu giải” | sách chỉ nói Hóa Khoa là sao giải nói chung (KL p.132), không nói Khoa có quyền cứu riêng cách cục này; không suy ra quyền cứu cách cục từ một đoạn khen sao tốt | giữ như giả thuyết |
| cứu | `tam_hoa_hoi_cuu` — Hóa Lộc, Quyền, Khoa cùng hội trong tam phương (Tam Hóa cứu giải) | Lỏng hơn nguồn | TH p.74 (van_ban): “cần được cứu giải băng Tam hóa hội” | TH p.74 chỉ nói Tam Hóa cứu Mệnh ở bại địa/tuyệt địa (Tuyệt xứ phùng sinh); bản nháp khái quát thành cứu mọi yếu tố phá cách; **quy ước:** 'phá được cứu' là quy ước thiết kế, không phải kết luận cổ thư | đề xuất sửa |
| phản chứng | `tuan_triet_an_ngu` — Tuần hoặc Triệt đóng ở cung Mệnh | Chưa có nguồn | — | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế | giữ như giả thuyết |

### Tam kỳ gia hội (`CACH_X_TAM_KY_GIA_HOI`)

| Vai trò | Điều kiện | Mức khớp | Nguồn · trang · trích | Lý do | Xử lý |
|---|---|---|---|---|---|
| lõi | `core` — Điều kiện lõi | Khớp | KL p.66 (van_ban): “Cung mệnh có Khoa, Quyền, Lộc hội họp mà lại bị Hóa kỵ, Kình dương đồng cung hoặc chiếu vào”<br>TT p.142 (van_ban): “Khoa, Quyền lộc củng (Chiếu thủ có cả ba Khoa, Quyền, Lộc)” | KL p.66 mục 10: Khoa, Quyền, Lộc hội họp ở Mệnh; TT p.142 Khoa Quyền Lộc củng. TH p.72 mục 12 'Tam Hóa liên châu' (ba cung liền) là điều kiện chặt hơn, khác tên; **trường phái:** TH p.72 mục 12 (ba cung liền) khác KL/TT (hội trong tam phương) | giữ (có nguồn) |
| tăng thế | `hoa_o_ban_cung` — có ít nhất một trong ba hóa ngay ở bản cung Mệnh | Chỉ liên quan | TH p.72 (anh_doc_ro): “Tam Hoá hên châu cách (tức Khao, Quyền, Lộc đi liền 3 cung đến cung Mệnh có 1 hóa)” | TH p.72 mục 12 là cách 'Tam Hóa liên châu' (Khoa, Quyền, Lộc đi liền 3 cung, Mệnh có một hóa): cấu trúc khác Tam kỳ gia hội (cả ba Hóa hội trong tam phương) | giữ như giả thuyết |
| tăng thế | `ta_huu_hoi` — Tả Phụ, Hữu Bật cùng hội trong tam phương | Chưa có nguồn | — | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế | giữ như giả thuyết |
| tăng thế | `xuong_khuc_hoi` — Văn Xương hoặc Văn Khúc hội trong tam phương | Chưa có nguồn | — | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế | giữ như giả thuyết |
| phá | `ky_hoac_kinh_dong_cung` — Hóa Kỵ hoặc Kình Dương đồng cung với Mệnh | Chặt hơn nguồn | KL p.66 (van_ban): “Cung mệnh có Khoa, Quyền, Lộc hội họp mà lại bị Hóa kỵ, Kình dương đồng cung hoặc chiếu vào” | KL p.66: Hóa Kỵ, Kình Dương 'đồng cung HOẶC CHIẾU' làm công danh mờ mịt; bản nháp chỉ tính đồng cung | đề xuất sửa |
| cứu | `ta_huu_giai_ky` — Tả Phụ, Hữu Bật cùng hội trong tam phương (giải Kỵ) | Chưa có nguồn | — | không tìm thấy trang nói Tả Hữu giải Kỵ/Kình cho cách này | giữ như giả thuyết |
| phản chứng | `tuan_triet_an_ngu` — Tuần hoặc Triệt đóng ở cung Mệnh | Chưa có nguồn | — | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế | giữ như giả thuyết |

### Khôi Việt giáp Mệnh (`CACH_X_KHOI_VIET_GIAP_MENH`)

| Vai trò | Điều kiện | Mức khớp | Nguồn · trang · trích | Lý do | Xử lý |
|---|---|---|---|---|---|
| lõi | `core` — Điều kiện lõi | Khớp | KL p.44 (van_ban): “Mệnh ở giữa, Khôi một bên, Việt một bên”<br>TT p.46 (van_ban): “Đóng ở Mệnh cung sang quí nhiều phúc lộc” | KL p.44 mục 9: Mệnh ở giữa, Khôi một bên, Việt một bên (tuổi Bính Đinh Nhâm Quý, Mệnh Thìn/Tuất) | giữ (có nguồn) |
| tăng thế | `co_chinh_tinh` — cung Mệnh có chính tinh | Chưa có nguồn | — | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế | giữ như giả thuyết |
| tăng thế | `ta_huu_hoi` — Tả Phụ, Hữu Bật cùng hội trong tam phương | Chưa có nguồn | — | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế | giữ như giả thuyết |
| tăng thế | `xuong_khuc_hoi` — Văn Xương hoặc Văn Khúc hội trong tam phương | Chỉ liên quan | KL p.62 (van_ban): “Mệnh có Khôi Việt, Xương, Khúc và Lộc tồn đồng cung hay hội chiếu” | KL p.62 mục 2 nói Khôi Việt, Xương, Khúc, Lộc Tồn ĐỒNG CUNG hay HỘI CHIẾU Mệnh; không phải Khôi Việt GIÁP Mệnh (KL p.62 mục 3 nói riêng về 'giáp mệnh' chỉ khen 'được kính nể, yêu quí') | giữ như giả thuyết |
| phá | `sat_dong_cung` — sát tinh (Kình, Đà, Hỏa, Linh, Không, Kiếp) đồng cung với Mệnh | Chỉ liên quan | KL p.62 (van_ban): “Cung mệnh có Khôi Việt lại bị sát tinh hội chiếu thì mang bệnh tật khó chữa khỏi” | KL p.62 mục 4: 'Cung mệnh CÓ Khôi Việt lại bị sát tinh hội chiếu' — Khôi Việt ở Mệnh, không phải giáp Mệnh; cấu trúc khác, nên không dùng làm nguồn cho phá cách Khôi Việt giáp Mệnh | giữ như giả thuyết |
| phá | `ky_dong_cung` — Hóa Kỵ đồng cung với Mệnh | Chỉ liên quan | KL p.62 (van_ban): “lại không bị Hóa kỵ Thiên hình cản phá thì giàu sang lớn” | KL p.62 mục 2: Khôi Việt, Xương, Khúc, Lộc Tồn đồng cung/hội chiếu mà không bị Kỵ, Hình cản phá — cấu trúc Khôi Việt ở/hội chiếu Mệnh, không phải giáp Mệnh | giữ như giả thuyết |
| cứu | `khoa_dong_cung` — Hóa Khoa đồng cung với Mệnh (giải Kỵ) | Chỉ liên quan | KL p.132 (van_ban): “Hóa khoa, một sao Đại cứu giải” | sách chỉ nói Hóa Khoa là sao giải nói chung (KL p.132), không nói Khoa có quyền cứu riêng cách cục này; không suy ra quyền cứu cách cục từ một đoạn khen sao tốt | giữ như giả thuyết |
| cứu | `tam_hoa_hoi_cuu` — Hóa Lộc, Quyền, Khoa cùng hội trong tam phương (Tam Hóa cứu giải) | Lỏng hơn nguồn | TH p.74 (van_ban): “cần được cứu giải băng Tam hóa hội” | TH p.74 chỉ nói Tam Hóa cứu Mệnh ở bại địa/tuyệt địa (Tuyệt xứ phùng sinh); bản nháp khái quát thành cứu mọi yếu tố phá cách; **quy ước:** 'phá được cứu' là quy ước thiết kế, không phải kết luận cổ thư | đề xuất sửa |
| phản chứng | `vo_chinh_dieu` — Mệnh vô chính diệu (phải mượn sao đối cung) | Chưa có nguồn | — | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế | giữ như giả thuyết |
| phản chứng | `tuan_triet_an_ngu` — Tuần hoặc Triệt đóng ở cung Mệnh | Chưa có nguồn | — | không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế | giữ như giả thuyết |

## 3. Ngưỡng và quy ước thiết kế (không phải kết luận cổ thư)

- **'3 trong 4 sao' của Sát Phá Liêm Tham**: sách có tên cách (TH p.72 mục 4) nhưng không nêu số sao cần có. Đây là quy ước thiết kế.
- **'2 yếu tố tăng thế' → *thành thượng***: không trang nào định nghĩa mức này; ngưỡng `thuong_at = 2` là quy ước. Thang bậc không cộng điểm: thêm sao tăng thế không vượt quá *thành thượng*.
- **'3 sát tinh + Hóa Kỵ' (SPLT hạ cách)**: TH p.77 chỉ nói 'nhiều' hung sát ở hãm địa; con số 3 và việc kèm Kỵ là quy ước.
- **'Phá được cứu'**: TH p.74 chỉ nói Tam Hóa cứu Mệnh ở bại/tuyệt địa; KL p.132 chỉ gọi Hóa Khoa là sao giải nói chung. Việc một sao cứu một yếu tố phá của một cách cụ thể là quy ước thiết kế; không dùng đoạn khen sao tốt để suy ra quyền cứu.
- **Phản chứng hạ một bậc**: quy ước (sách chỉ nói sao bị Tuần/Triệt/hãm thì kém đi).

## 4. Bốn điều kiện không bao giờ kích hoạt

| Điều kiện | Phân loại | Giải thích |
|---|---|---|
| Thiên Tướng hãm (TPVT) | **hạn chế vị trí sao** | Thiên Tướng chỉ hãm ở Mão/Dậu, nơi bốn sao Tử Phủ Vũ Tướng không thể cùng tam phương Mệnh. Không phải mâu thuẫn logic của luật. |
| Thái Dương hãm (NLTT) | **bảng miếu vượng** | cách đòi Thái Dương ở Ngọ, mà bảng cho Ngọ là vượng. Điều kiện đúng về logic nhưng bị bảng loại trừ. |
| Cự Môn hãm (TTAN) | **bảng miếu vượng** | cách đòi Cự Môn ở Tý/Ngọ, bảng cho là vượng. |
| Tam Hóa hội cứu (TPDC) | **hạn chế hình học của mô hình** | xem mục 5. |

Không điều kiện nào bị sửa để tăng tỷ lệ kích hoạt; chúng giữ nguyên và bị gắn nhãn `không thể xảy ra`.

## 5. Tử Phủ đồng cung × *phá được cứu* — bất khả thi trong mô hình

Tử Vi và Thiên Phủ cùng cung chỉ khi Tử Vi ở Dần/Thân (Thiên Phủ đối xứng qua trục Dần–Thân). Khi đó cả 14 chính tinh có vị trí cố định; chỉ Tả/Hữu (theo tháng) và Xương/Khúc (theo giờ) thay đổi. Để *phá được cứu* cần (A) Hóa Khoa và Hóa Kỵ cùng ở cung Mệnh, hoặc (B) Hóa Lộc, Quyền, Khoa cùng hội trong tam phương.

(A) Hóa Kỵ chỉ có thể nằm trong cung Mệnh nếu sao mang Kỵ là phụ tinh: chỉ có Kỷ (Kỵ = Văn Khúc) và Tân (Kỵ = Văn Xương); ở tám can còn lại Kỵ rơi vào một chính tinh có vị trí cố định khác cung Tử Phủ. Với Kỷ, Hóa Khoa là Thiên Lương (chính tinh, Thiên Phủ + 5 cung) nên không ở cung Mệnh. Với Tân, Khoa = Văn Khúc và Kỵ = Văn Xương, mà hai sao này chỉ trùng cung ở Sửu/Mùi, không bao giờ ở Dần/Thân. (B) kiểm bằng liệt kê 10 can × 2 vị trí × 12 tháng × 12 giờ. Cả hai được test trong `engine/tests/test_formation_geometry.py` và xác nhận lại trên mọi lá số thật có Tử Phủ đồng cung.

## 6. Bất đồng giữa các trường phái (giữ riêng, không gộp)

- **Tuần/Triệt**: vừa là sao giải hung/hãm tinh mạnh (KL p.199-201, p.85, p.289) vừa làm hại quý tinh (KL p.55, p.222; TH p.94-95). Cách kết luận phụ thuộc cách cục. Thạch trung ẩn ngọc và Nhật Nguyệt Sửu Mùi thì Tuần/Triệt là điều kiện *cần* (KL p.106, TH p.43, KL p.53).
- **Thạch trung ẩn ngọc**: ba định nghĩa — Mệnh Cự Môn + Di Thiên Cơ (KL p.44), Cự Môn Tý/Ngọ + Khoa Quyền Lộc tam hợp (KL p.58, TT p.34), Cự Môn Tý/Ngọ gặp Tuần/Triệt hoặc Hóa Lộc (KL p.106, TH p.43).
- **Mã đầu đới kiếm**: xấu khi Kình + Thất Sát/Thiên Hình đồng cung (KL p.64 mục 5), tốt khi xa lánh Thất Sát/Thiên Hình mà gặp Khoa Quyền Lộc (mục 6); TT p.142 cho Kình ở Ngọ là xấu.
- **Tử Phủ đồng cung**: 'vô sát tấu' (TT p.22) trái KL p.50 (Kình Dương, Hóa Kỵ đồng cung vẫn giàu/mưu trí); TT p.22 còn nhắc Tỵ/Hợi trong khi mô hình chỉ có Dần/Thân; TH p.72 cho phép đóng ở Mệnh hay Thân.
- **Nhật Nguyệt tịnh minh**: TH p.72 vị trí cố định (Nhật Thìn/Tỵ, Nguyệt Dậu/Tuất); KL p.53 chỉ cần hợp chiếu; TT p.142 'miếu vượng', KL p.53 'đắc địa'.
- **Sát Phá Liêm Tham**: TH p.76 xếp Kình, Không vào nhóm cát hội của Thân Sát Phá Liêm Tham, trái TH p.77 coi hội sát tinh nhiều là hạ cách.
- **Cơ Nguyệt Đồng Lương**: TT p.24 / TH p.77 coi hội cát tinh vẫn chỉ ở mức công chức; KL p.221 nói hội Khoa Quyền Lộc, Khôi Việt, Xương Khúc thì giáo sư danh tiếng.

## 7. Bộ lá số đối chứng (KL pp.237-246)

| Lá số | Cách cục | Engine | Nhận xét của sách | Kết quả |
|---|---|---|---|---|
| Hán Cao Tổ | Tử Phủ Vũ Tướng | thành thượng | thế rất mạnh | đồng ý |
| Hạng Võ | Cơ Nguyệt Đồng Lương | thành | thất bại (Triệt + Địa Kiếp ở Tài; Tuần ở Quan) | **không khớp** |
| Hạng Võ | Tam kỳ gia hội | thành | số xấu tổng thể (Cự + Kỵ ở Di) | **không khớp** |
| Khổng Minh | Nhật Nguyệt tịnh minh | thành thượng | thông minh tuyệt vời | đồng ý |
| Nữ Quý Mão | Cơ Nguyệt Đồng Lương, Khôi Việt giáp Mệnh | thành | sách không gọi tên | không xét |
| Mậu Tý phá sản | Nhật Nguyệt tịnh minh | bị phá | âm dương lạc hãm, phá sản | đồng ý |
| Mậu Tý phá sản | Cơ Nguyệt Đồng Lương | thành thượng | Cơ + Kỵ + Hỏa Linh phá sản | **không khớp** |

Cả ba trường hợp không khớp cùng nguyên nhân: sách tính Triệt/Tuần/Kỵ/sát tinh trên cả tam phương hoặc cung chiếu; bản nháp chỉ tính khi đồng cung Mệnh. Engine **không được chỉnh** để khớp; ghi nhận là phát hiện (đề xuất sửa ở mục 8). Số mẫu rất nhỏ (7 cặp có nhận xét) nên không thể suy ra độ chính xác.

## 8. Đề xuất sửa định nghĩa (chủ định nghĩa quyết định; chưa áp dụng)

1. Mở rộng phạm vi phá từ 'đồng cung Mệnh' sang 'đồng cung hoặc chiếu' cho Tam kỳ gia hội (KL p.66), và sang tam phương cho Cơ Nguyệt Đồng Lương (TT p.24).
2. Mã đầu đới kiếm: phá khi Thất Sát/Thiên Hình ĐỒNG CUNG (KL p.64), không phải mọi Thất Sát trong tam phương.
3. Bỏ 'Tuần/Triệt' làm phản chứng cho Thạch trung ẩn ngọc và Nhật Nguyệt tịnh minh (sách coi là điều kiện thuận), hoặc tách theo trường phái.
4. Tử Phủ đồng cung: neo ở Mệnh hoặc Thân (TH p.72); tách nhánh 'vô sát' (TT p.22) khỏi nhánh Kình/Kỵ (KL p.50).
5. Nhật/Nguyệt hãm: chỉ hạ khi không có cứu tinh (TH p.74), thêm Khôi Việt chiếu làm cứu (KL p.68).
6. Khôi Việt giáp Mệnh: sát tinh và Kỵ/Hình tính cả hội chiếu (KL p.62).

