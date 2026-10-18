# Bản luận mẫu: trước / sau (lá số kiểm thử 15/5/1990 10:30 nam)

> Lá số này chỉ là ví dụ kiểm thử; engine không hardcode lá số nào. Bản đính kèm trong yêu cầu không có trong repo nên baseline “trước” là đầu ra `/api/reasoning` (level 3) hiện hành.

## TRƯỚC (rút gọn 40 dòng đầu của luồng liệt kê)

```text
Về toàn lá số:
Có thể nhận thấy một dấu hiệu liên quan đến thế đứng Đào – Hồng – Thiên Không của người tuổi Ngọ: Đào Hồng đối mặt: công danh sớm, yêu sớm, về sau nhiều ngậm ngùi; nhận định này được các quy tắc đã khớp hỗ trợ.
Vì vậy, nhận định dựa trên các dữ kiện: chart.year_branch='Ngọ' @chart.
Ngoài ra chưa có quy tắc đối lập nào trong bộ quy tắc hiện hành khớp với dữ kiện này.
Về cung Huynh Đệ:
Chưa thể khẳng định một dấu hiệu thuộc điều kiện hạn chế: hạn chế: anh em ít, mỗi người một ngả (Tuần hoặc Triệt ở Huynh Đệ); nhận định này bị giới hạn bởi quy tắc đối lập.
Trong điều kiện này, nhận định dựa trên các dữ kiện: cung Huynh Đệ; cung có Tuần; cung không có Triệt.
Chỉ có quy tắc hạn chế (TV_TH_P2_HUYNH_DE_TT), không có quy tắc hỗ trợ đi kèm.
Về cung Mệnh:
Chưa thể khẳng định một dấu hiệu thuộc điều kiện hạn chế: khuynh hướng Phá Quân ở Tý, Ngọ: hoạnh phát nhưng cũng hoạnh phá; nhận định này bị giới hạn bởi quy tắc đối lập.
Do đó, nhận định dựa trên các dữ kiện: cung Mệnh; các sao trong cung: Phá Quân, Tướng Quân, Tuế Phá, Thai, Thiên Khốc, Thiên Hư, Thiên Hình, Ân Quang; tọa tại Tý.
Chỉ có quy tắc hạn chế (TV_TH_CACH_MENH_PHA_TY_NGO), không có quy tắc hỗ trợ đi kèm.
Có thể nhận thấy một dấu hiệu gắn với khuynh hướng Phá Quân ở Tý, Ngọ: hoạnh phát nhưng cũng hoạnh phá; nhận định này được các quy tắc đã khớp hỗ trợ.
Vì vậy, nhận định dựa trên các dữ kiện: cung Mệnh; các sao trong cung: Phá Quân, Tướng Quân, Tuế Phá, Thai, Thiên Khốc, Thiên Hư, Thiên Hình, Ân Quang; tọa tại Tý.
Ngoài ra chưa có quy tắc đối lập nào trong bộ quy tắc hiện hành khớp với dữ kiện này.
Có thể nhận thấy một dấu hiệu liên quan đến cấu trúc Sát – Phá – Tham trong tam phương; nhận định này được các quy tắc đã khớp hỗ trợ.
Trong điều kiện này, nhận định dựa trên các dữ kiện: Thất Sát, Phá Quân, Tham Lang cùng nằm trong tam phương.
Điểm đáng chú ý là chưa có quy tắc đối lập nào trong bộ quy tắc hiện hành khớp với dữ kiện này.
Có thể nhận thấy một dấu hiệu gắn với khuynh hướng học nhiều nhưng khó đạt thành tựu tương xứng (sao Thai tại Mệnh); nhận định này được các quy tắc đã khớp hỗ trợ.
Do đó, nhận định dựa trên các dữ kiện: cung Mệnh; các sao trong cung: Phá Quân, Tướng Quân, Tuế Phá, Thai, Thiên Khốc, Thiên Hư, Thiên Hình, Ân Quang.
Khi xét cùng chưa có quy tắc đối lập nào trong bộ quy tắc hiện hành khớp với dữ kiện này.
Có thể nhận thấy một dấu hiệu gắn với khuynh hướng đúng chỗ của mình (Mệnh dương đóng cung dương: đắc chính); nhận định này được các quy tắc đã khớp hỗ trợ.
Vì vậy, nhận định dựa trên các dữ kiện: chart.menh_dac_chinh=True @palace:Mệnh; chart.year_polarity='dương' @palace:Mệnh; cung Mệnh.
Ngoài ra chưa có quy tắc đối lập nào trong bộ quy tắc hiện hành khớp với dữ kiện này.
Có thể nhận thấy một dấu hiệu gắn với khuynh hướng tinh thần trách nhiệm cao, luôn lo giữ uy tín (tuổi Tý, Ngọ, Mão, Dậu nằm trong tứ chính); nhận định này được các quy tắc đã khớp hỗ trợ.
Trong điều kiện này, nhận định dựa trên các dữ kiện: chart.year_branch='Ngọ' @palace:Mệnh; cung Mệnh.
Điểm đáng chú ý là chưa có quy tắc đối lập nào trong bộ quy tắc hiện hành khớp với dữ kiện này.
Chưa thể khẳng định một dấu hiệu thuộc điều kiện hạn chế: khuynh hướng giờ sinh nghịch lý (giờ dương mà Mệnh ở cung âm hoặc ngược lại): độ số bị kém bớt; nhận định này bị giới hạn bởi quy tắc đối lập.
Do đó, nhận định dựa trên các dữ kiện: chart.hour_menh_polarity='nghich_ly' @palace:Mệnh; cung Mệnh.
Chỉ có quy tắc hạn chế (TV_TH_CACH_MENH_NGHICH_LY), không có quy tắc hỗ trợ đi kèm.
Có thể nhận thấy một dấu hiệu liên quan đến nhóm “hành động mạnh mẽ” (Sát – Phá – Liêm – Tham); nhận định này được các quy tắc đã khớp hỗ trợ.
Vì vậy, nhận định dựa trên các dữ kiện: chính tinh trong cung: Phá Quân; cung Mệnh; thuộc nhóm sao Sát – Phá – Liêm – Tham.
Ngoài ra chưa có quy tắc đối lập nào trong bộ quy tắc hiện hành khớp với dữ kiện này.
Có thể nhận thấy một dấu hiệu gắn với khuynh hướng Mệnh an ở sinh địa hoặc vượng địa của hành bản mệnh (nền thuận); sách nêu bảng nhưng chỉ nói rõ phần bại, tuyệt; nhận định này được các quy tắc đã khớp hỗ trợ.
Trong điều kiện này, nhận định dựa trên các dữ kiện: chart.menh_stage_th='vuong' @palace:Mệnh; cung Mệnh.
Điểm đáng chú ý là chưa có quy tắc đối lập nào trong bộ quy tắc hiện hành khớp với dữ kiện này.
Có thể nhận thấy một dấu hiệu gắn với khuynh hướng thuận mùa sinh (Mệnh Vượng hoặc Mệnh Tướng theo mùa): độ số được tăng; mùa lấy theo tháng âm 1-3 xuân, 4-6 hạ, 7-9 thu, 10-12 đông; nhận định này được các quy tắc đã khớp hỗ trợ.
Do đó, nhận định dựa trên các dữ kiện: chart.season_relation='tuong' @palace:Mệnh; cung Mệnh.
Khi xét cùng chưa có quy tắc đối lập nào trong bộ quy tắc hiện hành khớp với dữ kiện này.
Có thể nhận thấy một dấu hiệu gắn với khuynh hướng hiển đạt về võ nghiệp, uy quyền hiển hách (Phá Quân miếu vượng đắc địa); nhận định này được các quy tắc đã khớp hỗ trợ.
```

## SAU (`/api/deep-reading`, cờ TVBT_DEEP_INTERPRETATION=1)

### Tổng quan

Mệnh tại Tý với Phá Quân (miếu), Thân cư Phu Thê; Hỏa lục cục, bản mệnh Lộ Bàng Thổ (Cục sinh Mệnh); dương nam, đại hạn thuận. Từ 61 nhận định được kích hoạt, hệ thống rút ra 34 cụm chủ đề, 8 chỗ trái chiều (trong đó 0 chưa thể phân xử) và 1 cấu trúc đặc biệt: Sát – Phá – Tham trong tam phương Mệnh. Trục chính của Bản Mệnh: ‘khuynh hướng đúng chỗ của mình’; ‘khuynh hướng thông minh, cương nghị, can đảm, thích hoạt động; đời thăng trầm, tiền bạc tụ tán bất thường’. Chi tiết nằm ở từng chương; chương này không lặp lại.

**Chuỗi lập luận**

1. `vi_tri_sao` — Cung Mệnh an tại Mậu Tý: Phá Quân (miếu). Đối cung Thiên Di (Liêm Trinh (miếu), Thiên Tướng (vượng)). Tam hợp Quan Lộc (Tham Lang (miếu)) và Tài Bạch (Thất Sát (miếu)).
2. `ket_luan` — Mệnh tại Tý với Phá Quân (miếu), Thân cư Phu Thê; Hỏa lục cục, bản mệnh Lộ Bàng Thổ (Cục sinh Mệnh); dương nam, đại hạn thuận. Từ 61 nhận định được kích hoạt, hệ thống rút ra 34 cụm chủ đề, 8 chỗ trái chiều (trong đó 0 chưa thể phân xử) và 1 cấu trúc đặc biệt: Sát – Phá – Tham trong tam phương Mệnh. Trục chính của Bản Mệnh: ‘khuynh hướng đúng chỗ của mình’; ‘khuynh hướng thông minh, cương nghị, can đảm, thích hoạt động; đời thăng trầm, tiền bạc tụ tán bất thường’. Chi tiết nằm ở từng chương; chương này không lặp lại.

**Xác minh:** tóm tắt cấu trúc; số liệu lấy từ các chương sau

### Bản Mệnh

Bản Mệnh: Mệnh — Phá Quân (miếu). Nâng đỡ nổi bật là ‘khuynh hướng đúng chỗ của mình’; đối trọng là ‘khuynh hướng giờ sinh nghịch lý’. Hai phía thuộc những mặt khác nhau của cung nên không mâu thuẫn; chúng đọc song song.

**Nâng đỡ**

- khuynh hướng đúng chỗ của mình (Mệnh dương đóng cung dương: đắc chính) [KL p.238; TH p.75] — cùng chủ đề còn 1 quy tắc khác
- khuynh hướng thông minh, cương nghị, can đảm, thích hoạt động; đời thăng trầm, tiền bạc tụ tán bất thường (theo Phá Quân ở vị trí miếu/vượng/đắc tại cung Mệnh) [KL p.223; TH p.48] — cùng chủ đề còn 1 quy tắc khác

**Hạn chế**

- khuynh hướng giờ sinh nghịch lý (giờ dương mà Mệnh ở cung âm hoặc ngược lại): độ số bị kém bớt [TH p.76]

**Chuỗi lập luận**

1. `vi_tri_sao` — Cung Mệnh an tại Mậu Tý: Phá Quân (miếu). Đối cung Thiên Di (Liêm Trinh (miếu), Thiên Tướng (vượng)). Tam hợp Quan Lộc (Tham Lang (miếu)) và Tài Bạch (Thất Sát (miếu)).
2. `ket_luan` — Bản Mệnh: Mệnh — Phá Quân (miếu). Nâng đỡ nổi bật là ‘khuynh hướng đúng chỗ của mình’; đối trọng là ‘khuynh hướng giờ sinh nghịch lý’. Hai phía thuộc những mặt khác nhau của cung nên không mâu thuẫn; chúng đọc song song.

**Xác minh:** 4/4 nhận định có quy tắc đã đối chiếu sách (trạng thái lấy nguyên từ bộ quy tắc, hệ thống này không tự nâng cấp)

**Nguồn:** KL p.223; KL p.238; KL p.244; TH p.48; TH p.74; TH p.75; TH p.76

### Tính cách

Tính cách: Phúc Đức — Tử Vi (miếu), Thiên Phủ (đắc). Nâng đỡ nổi bật là ‘khuynh hướng hiển đạt về võ nghiệp, uy quyền hiển hách’; đối trọng là ‘hạn chế: tính tình ngang ngược, cương’. Hai phía cùng tồn tại vì điều kiện kích hoạt của cả hai đều thỏa (xem ‘điều kiện đọc’); sách không xếp thứ tự giữa chúng, nên bản luận là thành tựu có kèm trở ngại, không cái nào triệt tiêu cái nào.

**Nâng đỡ**

- khuynh hướng hiển đạt về võ nghiệp, uy quyền hiển hách (Phá Quân miếu vượng đắc địa) [TH p.96]
- theo truyền thống ghi nhận về tiền của, phúc lộc (không phải dự báo): khuynh hướng phúc lộc lâu dài (Tử Vi ở Phúc Đức tại Tý/Ngọ hoặc đồng cung Phủ, Tướng) [KL p.76]
- khuynh hướng họ hàng đông đúc, thịnh vượng (Trường Sinh hoặc Đế Vượng ở Phúc Đức) [KL p.217; TH p.112; TT pp.83-84] — cùng chủ đề còn 2 quy tắc khác
- khuynh hướng an dật (Thiên Phủ ở Phúc Đức, đồng cung Tử Vi) [TT pp.83-84] — cùng chủ đề còn 1 quy tắc khác
- … và 2 nhận định khác trong phần mở rộng

**Hạn chế**

- hạn chế: tính tình ngang ngược, cương (Cự, Phá hoặc Kình Dương thủ Mệnh) [TT p.151]
- khuynh hướng hay tranh cãi (Tuế Phá ở Mệnh) [KL p.229]
- hạn chế: phúc phận kém (Tử Vi ở Phúc Đức, gặp sát tinh) [TT pp.83-84]

**Điều kiện đọc**

- Đồng thời đúng (TV_KL_AUX_TUE_PHA ↔ TV_TH_STAR_PHA_QUAN_NAM_MV): Cả hai cùng đúng trong lá số vì hai điều kiện kích hoạt khác nhau đều thỏa: (1) Tuế Phá cùng cung → thiên về hạn chế; (2) chart.gender eq nam; chính tinh Phá Quân cùng cung; độ sáng của Phá Quân = miếu, vượng, đắc → thiên về nâng đỡ. Sách trong bộ quy tắc không xếp thứ tự giữa hai lực này, nên đọc là hai mặt đồng thời (có thuận có nghịch), không phải một bên triệt tiêu bên kia.
- Đồng thời đúng (TV_TH_STAR_PHA_QUAN_NAM_MV ↔ TV_TT_PHU_MENH_CO_PHA_KINH): Cả hai cùng đúng trong lá số vì hai điều kiện kích hoạt khác nhau đều thỏa: (1) chart.gender eq nam; chính tinh Phá Quân cùng cung; độ sáng của Phá Quân = miếu, vượng, đắc → thiên về nâng đỡ; (2) Cự Môn cùng cung; Kình Dương cùng cung; Phá Quân cùng cung → thiên về hạn chế. Sách trong bộ quy tắc không xếp thứ tự giữa hai lực này, nên đọc là hai mặt đồng thời (có thuận có nghịch), không phải một bên triệt tiêu bên kia.
- Đồng thời đúng (TV_TT_PAL_PHUC_DUC_THIEN_PHU_WITH_TU_VI_P ↔ TV_TT_PAL_PHUC_DUC_TU_VI_SAT_M): Cả hai cùng đúng trong lá số vì hai điều kiện kích hoạt khác nhau đều thỏa: (1) chính tinh Thiên Phủ cùng cung → thiên về nâng đỡ; (2) palace.khi.sat_tp gte 1 → thiên về hạn chế. Sách trong bộ quy tắc không xếp thứ tự giữa hai lực này, nên đọc là hai mặt đồng thời (có thuận có nghịch), không phải một bên triệt tiêu bên kia.
- Điều chỉnh (TV_TT_PAL_PHUC_DUC_TU_VI_BASE_P ↔ TV_TT_PAL_PHUC_DUC_TU_VI_SAT_M): TV_TT_PAL_PHUC_DUC_TU_VI_BASE_P là nhận định nền; TV_TT_PAL_PHUC_DUC_TU_VI_SAT_M chỉ thêm điều kiện (palace.khi.sat_tp gte 1) nên điều chỉnh nó khi điều kiện ấy có mặt. Hai điều kiện cùng thỏa trong lá số này, vì vậy nhận định nền được đọc kèm điều chỉnh.
- Đồng thời đúng (TV_TT_PAL_PHUC_DUC_TU_VI_SAT_M ↔ TV_TT_PAL_PHUC_DUC_TU_VI_WITH_THIEN_PHU_P): Cả hai cùng đúng trong lá số vì hai điều kiện kích hoạt khác nhau đều thỏa: (1) palace.khi.sat_tp gte 1 → thiên về hạn chế; (2) chính tinh Thiên Phủ cùng cung → thiên về nâng đỡ. Sách trong bộ quy tắc không xếp thứ tự giữa hai lực này, nên đọc là hai mặt đồng thời (có thuận có nghịch), không phải một bên triệt tiêu bên kia.

**Chuỗi lập luận**

1. `vi_tri_sao` — Cung Phúc Đức an tại Mậu Dần: Tử Vi (miếu), Thiên Phủ (đắc). Đối cung Tài Bạch (Thất Sát (miếu)). Tam hợp Thiên Di (Liêm Trinh (miếu), Thiên Tướng (vượng)) và Phu Thê (Vũ Khúc (miếu)).
2. `dieu_kien` — Đồng thời đúng (TV_KL_AUX_TUE_PHA ↔ TV_TH_STAR_PHA_QUAN_NAM_MV): Cả hai cùng đúng trong lá số vì hai điều kiện kích hoạt khác nhau đều thỏa: (1) Tuế Phá cùng cung → thiên về hạn chế; (2) chart.gender eq nam; chính tinh Phá Quân cùng cung; độ sáng của Phá Quân = miếu, vượng, đắc → thiên về nâng đỡ. Sách trong bộ quy tắc không xếp thứ tự giữa hai lực này, nên đọc là hai mặt đồng thời (có thuận có nghịch), không phải một bên triệt tiêu bên kia. | Đồng thời đúng (TV_TH_STAR_PHA_QUAN_NAM_MV ↔ TV_TT_PHU_MENH_CO_PHA_KINH): Cả hai cùng đúng trong lá số vì hai điều kiện kích hoạt khác nhau đều thỏa: (1) chart.gender eq nam; chính tinh Phá Quân cùng cung; độ sáng của Phá Quân = miếu, vượng, đắc → thiên về nâng đỡ; (2) Cự Môn cùng cung; Kình Dương cùng cung; Phá Quân cùng cung → thiên về hạn chế. Sách trong bộ quy tắc không xếp thứ tự giữa hai lực này, nên đọc là hai mặt đồng thời (có thuận có nghịch), không phải một bên triệt tiêu bên kia. | Đồng thời đúng (TV_TT_PAL_PHUC_DUC_THIEN_PHU_WITH_TU_VI_P ↔ TV_TT_PAL_PHUC_DUC_TU_VI_SAT_M): Cả hai cùng đúng trong lá số vì hai điều kiện kích hoạt khác nhau đều thỏa: (1) chính tinh Thiên Phủ cùng cung → thiên về nâng đỡ; (2) palace.khi.sat_tp gte 1 → thiên về hạn chế. Sách trong bộ quy tắc không xếp thứ tự giữa hai lực này, nên đọc là hai mặt đồng thời (có thuận có nghịch), không phải một bên triệt tiêu bên kia.
3. `ket_luan` — Tính cách: Phúc Đức — Tử Vi (miếu), Thiên Phủ (đắc). Nâng đỡ nổi bật là ‘khuynh hướng hiển đạt về võ nghiệp, uy quyền hiển hách’; đối trọng là ‘hạn chế: tính tình ngang ngược, cương’. Hai phía cùng tồn tại vì điều kiện kích hoạt của cả hai đều thỏa (xem ‘điều kiện đọc’); sách không xếp thứ tự giữa chúng, nên bản luận là thành tựu có kèm trở ngại, không cái nào triệt tiêu cái nào.

**Xác minh:** 9/10 nhận định có quy tắc đã đối chiếu sách (trạng thái lấy nguyên từ bộ quy tắc, hệ thống này không tự nâng cấp)

**Nguồn:** KL p.217; KL p.229; KL p.76; TH p.112; TH p.85; TH p.96; TT p.151; TT pp.83-84

### Công danh

Công danh: Quan Lộc — Tham Lang (miếu). Nâng đỡ nổi bật là ‘khuynh hướng công danh thẳng bước, uy quyền hiển hách’; đối trọng là ‘khuynh hướng khó đạt công danh’. Hai phía cùng tồn tại vì điều kiện kích hoạt của cả hai đều thỏa (xem ‘điều kiện đọc’); sách không xếp thứ tự giữa chúng, nên bản luận là thành tựu có kèm trở ngại, không cái nào triệt tiêu cái nào.

**Nâng đỡ**

- khuynh hướng công danh thẳng bước, uy quyền hiển hách (Phá Quân đắc địa gặp Tam Hóa, Tả Hữu, Xương Khúc, Tướng Ấn) [TH p.49]
- khuynh hướng sống tích cực: không thành công thì cũng thành nhân (Sát Phá Tham ở Mệnh) [KL p.221]

**Hạn chế**

- khuynh hướng khó đạt công danh (Kiếp/Không hãm đóng cung Quan) [TH p.68]

**Điều kiện đọc**

- Đồng thời đúng (TV_KL_CT_SAT_PHA_THAM ↔ TV_TH_AUX2_QUAN_LOC_KK_HAM): Cả hai cùng đúng trong lá số vì hai điều kiện kích hoạt khác nhau đều thỏa: (1) chính tinh Phá Quân cùng cung; chính tinh Tham Lang cùng cung; chính tinh Thất Sát cùng cung → thiên về nâng đỡ; (2) cung tại Tỵ, Hợi, Dần, Thân; Địa Không cùng cung; Địa Kiếp cùng cung → thiên về hạn chế. Sách trong bộ quy tắc không xếp thứ tự giữa hai lực này, nên đọc là hai mặt đồng thời (có thuận có nghịch), không phải một bên triệt tiêu bên kia.
- Đồng thời đúng (TV_TH_AUX2_QUAN_LOC_KK_HAM ↔ TV_TH_COMBO_PHÁ_QUAN_CAT): Cả hai cùng đúng trong lá số vì hai điều kiện kích hoạt khác nhau đều thỏa: (1) cung tại Tỵ, Hợi, Dần, Thân; Địa Không cùng cung; Địa Kiếp cùng cung → thiên về hạn chế; (2) Hóa Khoa trong tam phương; Hóa Lộc trong tam phương; Hóa Quyền trong tam phương; Hữu Bật trong tam phương; Thiên Tướng trong tam phương; Tả Phụ trong tam phương; Văn Khúc trong tam phương; Văn Xương trong tam phương; chính tinh Phá Quân cùng cung; độ sáng của Phá Quân = miếu, vượng, đắc → thiên về nâng đỡ. Sách trong bộ quy tắc không xếp thứ tự giữa hai lực này, nên đọc là hai mặt đồng thời (có thuận có nghịch), không phải một bên triệt tiêu bên kia.

**Chuỗi lập luận**

1. `vi_tri_sao` — Cung Quan Lộc an tại Canh Thìn: Tham Lang (miếu). Đối cung Phu Thê (Vũ Khúc (miếu)). Tam hợp Tài Bạch (Thất Sát (miếu)) và Mệnh (Phá Quân (miếu)).
2. `dieu_kien` — Đồng thời đúng (TV_KL_CT_SAT_PHA_THAM ↔ TV_TH_AUX2_QUAN_LOC_KK_HAM): Cả hai cùng đúng trong lá số vì hai điều kiện kích hoạt khác nhau đều thỏa: (1) chính tinh Phá Quân cùng cung; chính tinh Tham Lang cùng cung; chính tinh Thất Sát cùng cung → thiên về nâng đỡ; (2) cung tại Tỵ, Hợi, Dần, Thân; Địa Không cùng cung; Địa Kiếp cùng cung → thiên về hạn chế. Sách trong bộ quy tắc không xếp thứ tự giữa hai lực này, nên đọc là hai mặt đồng thời (có thuận có nghịch), không phải một bên triệt tiêu bên kia. | Đồng thời đúng (TV_TH_AUX2_QUAN_LOC_KK_HAM ↔ TV_TH_COMBO_PHÁ_QUAN_CAT): Cả hai cùng đúng trong lá số vì hai điều kiện kích hoạt khác nhau đều thỏa: (1) cung tại Tỵ, Hợi, Dần, Thân; Địa Không cùng cung; Địa Kiếp cùng cung → thiên về hạn chế; (2) Hóa Khoa trong tam phương; Hóa Lộc trong tam phương; Hóa Quyền trong tam phương; Hữu Bật trong tam phương; Thiên Tướng trong tam phương; Tả Phụ trong tam phương; Văn Khúc trong tam phương; Văn Xương trong tam phương; chính tinh Phá Quân cùng cung; độ sáng của Phá Quân = miếu, vượng, đắc → thiên về nâng đỡ. Sách trong bộ quy tắc không xếp thứ tự giữa hai lực này, nên đọc là hai mặt đồng thời (có thuận có nghịch), không phải một bên triệt tiêu bên kia.
3. `ket_luan` — Công danh: Quan Lộc — Tham Lang (miếu). Nâng đỡ nổi bật là ‘khuynh hướng công danh thẳng bước, uy quyền hiển hách’; đối trọng là ‘khuynh hướng khó đạt công danh’. Hai phía cùng tồn tại vì điều kiện kích hoạt của cả hai đều thỏa (xem ‘điều kiện đọc’); sách không xếp thứ tự giữa chúng, nên bản luận là thành tựu có kèm trở ngại, không cái nào triệt tiêu cái nào.

**Xác minh:** 4/5 nhận định có quy tắc đã đối chiếu sách (trạng thái lấy nguyên từ bộ quy tắc, hệ thống này không tự nâng cấp)

**Nguồn:** KL p.216; KL p.221; KL p.229; TH p.49; TH p.59; TH p.68

### Tài Bạch

Tài Bạch: Tài Bạch — Thất Sát (miếu); Điền Trạch — Thái Âm (hãm). Chỉ có nhận định hạn chế được kích hoạt, nổi bật là ‘khuynh hướng khó tích lũy, tài lộc hao hụt’; bộ quy tắc không có nhận định nâng đỡ tương ứng nên đây là điểm cần tự điều chỉnh.

**Hạn chế**

- theo truyền thống ghi nhận về tiền của, phúc lộc (không phải dự báo): khuynh hướng khó tích lũy, tài lộc hao hụt (Không, Kiếp hoặc Liêm Tham ghé vào Tài Bạch); 'ghé vào' đọc là hội trong tam phương [KL p.216]

**Chuỗi lập luận**

1. `vi_tri_sao` — Cung Tài Bạch an tại Giáp Thân: Thất Sát (miếu). Đối cung Phúc Đức (Tử Vi (miếu), Thiên Phủ (đắc)). Tam hợp Mệnh (Phá Quân (miếu)) và Quan Lộc (Tham Lang (miếu)). Cung Điền Trạch an tại Kỷ Mão: Thái Âm (hãm). Đối cung Tử Tức (Thiên Đồng (bình)). Tam hợp Tật Ách (Thiên Lương (đắc)) và Huynh Đệ (Thái Dương (hãm)). Sao hóa tại cung: Hóa Kỵ.
2. `ket_luan` — Tài Bạch: Tài Bạch — Thất Sát (miếu); Điền Trạch — Thái Âm (hãm). Chỉ có nhận định hạn chế được kích hoạt, nổi bật là ‘khuynh hướng khó tích lũy, tài lộc hao hụt’; bộ quy tắc không có nhận định nâng đỡ tương ứng nên đây là điểm cần tự điều chỉnh.

**Xác minh:** 2/4 nhận định có quy tắc đã đối chiếu sách (trạng thái lấy nguyên từ bộ quy tắc, hệ thống này không tự nâng cấp)

**Nguồn:** KL p.216; KL p.219; TH p.106; TH p.111; TT p.159; TT p.47; TT pp.80-81

### Quan hệ

Quan hệ: Phu Thê — Vũ Khúc (miếu); Nô Bộc — Cự Môn (hãm). Nâng đỡ nổi bật là ‘khuynh hướng cha mẹ khá giả, con cái hòa thuận’; đối trọng là ‘hạn chế: anh em ít, mỗi người một ngả’. Hai phía cùng tồn tại vì điều kiện kích hoạt của cả hai đều thỏa (xem ‘điều kiện đọc’); sách không xếp thứ tự giữa chúng, nên bản luận là thành tựu có kèm trở ngại, không cái nào triệt tiêu cái nào.

**Nâng đỡ**

- khuynh hướng cha mẹ khá giả, con cái hòa thuận (Phụ Mẫu có Thiên Đồng, Thiên Cơ, Thái Âm, Thiên Phủ, Thiên Tướng hoặc Thiên Lương) [KL p.220]

**Hạn chế**

- hạn chế: anh em ít, mỗi người một ngả (Tuần hoặc Triệt ở Huynh Đệ) [TH p.99]
- theo truyền thống ghi nhận về chuyện hôn nhân (không phải dự báo): hạn chế: dễ bất hòa nên thành hôn muộn, lấy người bằng tuổi; lấy rồi làm ăn có tiền vào (Vũ Khúc ở Phu Thê) [TT pp.82-83]
- hạn chế: cha mẹ và con dễ xung khắc (Thiên Cơ ở Phụ Mẫu tại Hợi, Tý, Sửu) [TH p.113]
- theo truyền thống ghi nhận về tiền của, phúc lộc (không phải dự báo): hạn chế: người phối ngẫu hà tiện (Linh Tinh ở Phu Thê) [TH p.102]

**Điều kiện đọc**

- Đồng thời đúng (TV_KL_CUNG_PHU_MAU_SAO_TOT ↔ TV_TH_P2_PHU_MAU_CO_HOI_TY_SUU): Cả hai cùng đúng trong lá số vì hai điều kiện kích hoạt khác nhau đều thỏa: (1) chính tinh Thiên Lương cùng cung; chính tinh Thiên Phủ cùng cung; chính tinh Thiên Tướng cùng cung; chính tinh Thiên Đồng cùng cung; chính tinh Thái Âm cùng cung → thiên về nâng đỡ; (2) cung tại Hợi, Tý, Sửu → thiên về hạn chế. Sách trong bộ quy tắc không xếp thứ tự giữa hai lực này, nên đọc là hai mặt đồng thời (có thuận có nghịch), không phải một bên triệt tiêu bên kia.

**Chuỗi lập luận**

1. `vi_tri_sao` — Cung Phu Thê an tại Bính Tuất: Vũ Khúc (miếu). Đối cung Quan Lộc (Tham Lang (miếu)). Tam hợp Phúc Đức (Tử Vi (miếu), Thiên Phủ (đắc)) và Thiên Di (Liêm Trinh (miếu), Thiên Tướng (vượng)). Cung có Tuần. Sao hóa tại cung: Hóa Quyền. Cung Nô Bộc an tại Tân Tỵ: Cự Môn (hãm). Đối cung Huynh Đệ (Thái Dương (hãm)). Tam hợp Tử Tức (Thiên Đồng (bình)) và Phụ Mẫu (Thiên Cơ (hãm)).
2. `dieu_kien` — Đồng thời đúng (TV_KL_CUNG_PHU_MAU_SAO_TOT ↔ TV_TH_P2_PHU_MAU_CO_HOI_TY_SUU): Cả hai cùng đúng trong lá số vì hai điều kiện kích hoạt khác nhau đều thỏa: (1) chính tinh Thiên Lương cùng cung; chính tinh Thiên Phủ cùng cung; chính tinh Thiên Tướng cùng cung; chính tinh Thiên Đồng cùng cung; chính tinh Thái Âm cùng cung → thiên về nâng đỡ; (2) cung tại Hợi, Tý, Sửu → thiên về hạn chế. Sách trong bộ quy tắc không xếp thứ tự giữa hai lực này, nên đọc là hai mặt đồng thời (có thuận có nghịch), không phải một bên triệt tiêu bên kia.
3. `ket_luan` — Quan hệ: Phu Thê — Vũ Khúc (miếu); Nô Bộc — Cự Môn (hãm). Nâng đỡ nổi bật là ‘khuynh hướng cha mẹ khá giả, con cái hòa thuận’; đối trọng là ‘hạn chế: anh em ít, mỗi người một ngả’. Hai phía cùng tồn tại vì điều kiện kích hoạt của cả hai đều thỏa (xem ‘điều kiện đọc’); sách không xếp thứ tự giữa chúng, nên bản luận là thành tựu có kèm trở ngại, không cái nào triệt tiêu cái nào.

**Xác minh:** 6/8 nhận định có quy tắc đã đối chiếu sách (trạng thái lấy nguyên từ bộ quy tắc, hệ thống này không tự nâng cấp)

**Nguồn:** KL p.217; KL p.218; KL p.220; TH p.102; TH p.113; TH p.99; TT pp.82-83; TT pp.87-88

### Đại hạn & lưu niên

Năm 2020 (tuổi mụ 31) nằm trong đại hạn 26–35 tại cung Phúc Đức (Mậu Dần). Đại hạn không tạo ra nhận định mới: nó chọn cung nguyên cục nào được ‘bật sáng’ trong giai đoạn này — ở đây là Phúc Đức, cùng với việc bốn hóa theo can Mậu đáp xuống Hóa Lộc → Quan Lộc, Hóa Quyền → Điền Trạch, Hóa Khoa → Tật Ách, Hóa Kỵ → Phụ Mẫu. Cung này mang 5 nhận định nâng đỡ và 1 nhận định hạn chế nguyên cục, đọc xem ở chương tương ứng. Lưu niên chỉ ghi vị trí và lời sách theo từng sao hóa; không dự báo sự kiện.

**Nâng đỡ**

- Hóa Lộc: sáng suốt, biết phô trương thì có lộc (Khảo Luận pp.195-197)
- Hóa Quyền: lo buôn bán, giỏi tài chính thì có quyền (Khảo Luận pp.195-197)
- Hóa Khoa: uyển chuyển, khéo léo thì có danh (Khảo Luận pp.195-197)

**Hạn chế**

- Hóa Kỵ: ham tiền quá sẽ bị chê cười (Khảo Luận pp.195-197)

**Chuỗi lập luận**

1. `vi_tri_sao` — Đại hạn tại Phúc Đức (can Mậu), tiểu hạn tại Phu Thê, lưu Thái Tuế tại Mệnh.
2. `quan_he_cung` — Tứ Hóa đại hạn đáp: Hóa Lộc→Quan Lộc, Hóa Quyền→Điền Trạch, Hóa Khoa→Tật Ách, Hóa Kỵ→Phụ Mẫu
3. `dieu_kien` — Hóa Kỵ đại hạn tại cung Phụ Mẫu trong khi Hóa Lộc nguyên cục ở Huynh Đệ
4. `ket_luan` — Năm 2020 (tuổi mụ 31) nằm trong đại hạn 26–35 tại cung Phúc Đức (Mậu Dần). Đại hạn không tạo ra nhận định mới: nó chọn cung nguyên cục nào được ‘bật sáng’ trong giai đoạn này — ở đây là Phúc Đức, cùng với việc bốn hóa theo can Mậu đáp xuống Hóa Lộc → Quan Lộc, Hóa Quyền → Điền Trạch, Hóa Khoa → Tật Ách, Hóa Kỵ → Phụ Mẫu. Cung này mang 5 nhận định nâng đỡ và 1 nhận định hạn chế nguyên cục, đọc xem ở chương tương ứng. Lưu niên chỉ ghi vị trí và lời sách theo từng sao hóa; không dự báo sự kiện.

**Xác minh:** phần tính vị trí đã đối chiếu (Thực Hành p.27); phần lời sách theo sao hóa lấy từ Khảo Luận, chưa có quy tắc đại hạn giao thoa nguyên cục nên chỉ nêu vị trí

**Nguồn:** Khảo Luận pp.195-197; Khảo Luận pp.233-236; Thực Hành p.27

### Cách cục

Cách cục được đọc như các luận điểm có điều kiện: Sát – Phá – Tham trong tam phương Mệnh. Mỗi cấu trúc nêu rõ điều kiện tiên quyết, yếu tố nâng, yếu tố phá và mức nguồn; hệ thống không cộng điểm để quyết ‘thành’ hay ‘phá’ cách.

**Nâng đỡ**

- Cát tinh trong tam phương: Thiên Khôi

**Hạn chế**

- Sát tinh trong tam phương: Hỏa Tinh, Địa Không, Địa Kiếp

**Điều kiện đọc**

- Ngưỡng phá cách chưa đủ nguồn (R03).

**Chuỗi lập luận**

1. `vi_tri_sao` — Nhận diện cách cục từ vị trí chính tinh và sát/cát tinh trong tam phương tứ chính của từng cung có liên quan.
2. `cach_cuc` — Sát – Phá – Tham trong tam phương Mệnh: ✓ Thất Sát trong tam phương tứ chính của Mệnh; ✓ Phá Quân trong tam phương tứ chính của Mệnh; ✓ Tham Lang trong tam phương tứ chính của Mệnh
3. `ket_luan` — Cách cục được đọc như các luận điểm có điều kiện: Sát – Phá – Tham trong tam phương Mệnh. Mỗi cấu trúc nêu rõ điều kiện tiên quyết, yếu tố nâng, yếu tố phá và mức nguồn; hệ thống không cộng điểm để quyết ‘thành’ hay ‘phá’ cách.

**Xác minh:** Sát – Phá – Tham trong tam phương Mệnh: mới đối chiếu từng thành phần, tổ hợp chưa có câu sách

**Nguồn:** TH tr.116; TH tr.77

### 12 cung

Mười hai cung được liệt kê dưới dạng bảng vị trí; chỉ Thiên Di và Tật Ách được luận ở đây, mười cung còn lại luận ở chương chứa chúng để không lặp. Thiên Di và Tật Ách: Thiên Di — Liêm Trinh (miếu), Thiên Tướng (vượng); Tật Ách — Thiên Lương (đắc). Nâng đỡ nổi bật là ‘khuynh hướng hay gặp người sang giúp’; đối trọng là ‘hạn chế: ngoài giao thiệp lắm trắc trở’. Hai phía thuộc những mặt khác nhau của cung nên không mâu thuẫn; chúng đọc song song.

**Nâng đỡ**

- khuynh hướng hay gặp người sang giúp (Thiên Khôi ở Thiên Di) [TH p.108]

**Hạn chế**

- hạn chế: ngoài giao thiệp lắm trắc trở (Không, Kiếp ở Thiên Di) [TH p.109]
- hạn chế: độc thủ ra ngoài bất an; được cát tinh phù trì thì hay hoạnh tài (Hỏa Tinh ở Thiên Di) [TT pp.77-78]

**Chuỗi lập luận**

1. `vi_tri_sao` — Cung Thiên Di an tại Nhâm Ngọ: Liêm Trinh (miếu), Thiên Tướng (vượng). Đối cung Mệnh (Phá Quân (miếu)). Tam hợp Phu Thê (Vũ Khúc (miếu)) và Phúc Đức (Tử Vi (miếu), Thiên Phủ (đắc)). Cung có Triệt. Cung Tật Ách an tại Quý Mùi: Thiên Lương (đắc). Đối cung Phụ Mẫu (Thiên Cơ (hãm)). Tam hợp Huynh Đệ (Thái Dương (hãm)) và Điền Trạch (Thái Âm (hãm)). Cung có Triệt.
2. `ket_luan` — Thiên Di và Tật Ách: Thiên Di — Liêm Trinh (miếu), Thiên Tướng (vượng); Tật Ách — Thiên Lương (đắc). Nâng đỡ nổi bật là ‘khuynh hướng hay gặp người sang giúp’; đối trọng là ‘hạn chế: ngoài giao thiệp lắm trắc trở’. Hai phía thuộc những mặt khác nhau của cung nên không mâu thuẫn; chúng đọc song song.

**Xác minh:** 7/8 nhận định có quy tắc đã đối chiếu sách (trạng thái lấy nguyên từ bộ quy tắc, hệ thống này không tự nâng cấp)

**Nguồn:** KL p.218; KL p.219; TH p.108; TH p.109; TH p.86; TT pp.77-78

### Luận giải chuyên sâu

Phần này là hồ sơ kiểm chứng: mọi chỗ trái chiều, mọi điểm nguồn mâu thuẫn từ Phase 7 chạm vào lá số này, và các quy tắc chưa đủ nguồn mà hệ thống cố ý không suy diễn.

**Điều kiện đọc**

- Nêu cả hai chiều, nói rõ chiều nào áp dụng cho sao nào; không cộng trừ.
- Không rút ra kết luận 'phá cách' chắc chắn; hiển thị số sát tinh và để người đọc thấy ngưỡng.
- Không tự chọn; nêu hai neo.

**Chuỗi lập luận**

1. `dieu_kien` — R07 Tuần/Triệt vừa hại quý tinh vừa cứu hung tinh (nguon_mau_thuan); R03 Ngưỡng sát tinh phá cách (nguon_chua_du); R09 Tử Phủ đồng cung: neo Mệnh/Thân; 'Tỵ Hợi' (nguon_mau_thuan)
2. `ket_luan` — Mọi mục trên được giữ ở trạng thái ‘chưa phân xử’: hệ thống không chọn trường phái và không đánh dấu verified.

**Xác minh:** không có mục nào được tự đánh dấu verified; policy chưa đủ nguồn xem bên dưới

**Nguồn:** KL tr.55; KL tr.222; TH tr.94; TH tr.95; KL tr.85; KL tr.199; KL tr.53; KL tr.106; TH tr.43; TH tr.77; TH tr.116; KL tr.62; KL tr.199; KL tr.85; TH tr.72; TT tr.22; KL tr.50; KL tr.68

