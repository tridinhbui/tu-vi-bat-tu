# Phase 7 — Kiểm chứng nguồn có phê phán (source-critical) cho 17 biến thể cách cục Tử Vi (bản nháp)

Sinh bởi `tools/build_phase7_report.py` từ các file đã ghim. **Không quy tắc nào được đóng dấu `verified`, không cách đọc nào được chọn, không giả làm ý kiến chuyên gia.** Oracle khớp sản xuất chỉ chứng minh hai bản hiện thực nhất quán; mục tiêu của Phase 7 là tìm những chỗ mà cả hai (hoặc audit) đã âm thầm giả định.

## 0. Kết quả chính

1. **Tứ Hóa Nhâm-Khoa** (R05): khác biệt giữa hai dòng văn bản, không phải lỗi in một chỗ và không phải lỗi diễn giải: TH tr.20 *và* tr.21 in Thiên Phủ; KL tr.36, tr.197 in Tả Phụ; một văn bản 紫微斗數全書 số hóa độc lập cũng ghi 府. Production giữ bảng KL; ba bảng theo nguồn được lưu riêng; ghi chú sai 'agree on all ten stems' trong `tuvi.py` đã sửa (chỉ chữ, không đổi logic).
2. **Hai breaker tỷ lệ phá cao** (R03): 82,1% và 91,7% đều đến từ ngưỡng 'một sát tinh/một trong ba' ở phạm vi tam phương. Thu hẹp phạm vi hay siết cách đọc kéo xuống 0–69%; không cách nào được chọn. Với Khôi Việt giáp Mệnh còn phát hiện thêm: các câu KL tr.62 nói về Khôi Việt Ở Mệnh, không phải giáp Mệnh (cấu trúc khác) nên ba quy tắc bị hạ xuống `chua_du_nguon`.
3. **Đọc lại toàn đoạn** 59 câu trích khác nhau của audit (không chỉ từ khoá): 10 dòng audit có nguồn thuộc cấu trúc lân cận (chuyển về `lien_quan`), 3 dòng nói về đại tiểu hạn, bỏ sót nhiều đoạn có ích (mục 4). Số quy tắc của 17 biến thể nay là **10 đối chiếu trực tiếp / 33 có nguồn còn giả định / 4 chưa đủ nguồn** (tổng 47).
4. **Lịch pháp**: lịch Trung Quốc của sản xuất khớp bảng Hong Kong Observatory trên 47,789 ngày (0 sai khác). Lịch Việt Nam khớp oracle amlich độc lập, trừ 4 đoạn: 3 ngày sát nửa đêm (new moon trong 40 phút sau 0h) và **một lỗi thật của sản xuất**: 2033-12-22..31 (tháng nhuận 11) bị đánh số là tháng 12. Lỗi ghi lại bằng test `xfail`, chưa sửa (ngoài phạm vi).
5. **Oracle mở rộng**: mọi công thức an sao của oracle (Địa Kiếp/Không, Hỏa/Linh, Kình/Đà, Thiên Hình, Lực Sĩ, Thiên Mã, Lộc Tồn, Tuần, Triệt, Khôi Việt) có câu in trong Thực Hành và ví dụ minh họa của chính sách được chạy lại; thêm kiểm biên: giờ Tý, giao ngày/Tết, tháng nhuận (3 quy tắc), Lập Xuân so với Tết, múi giờ.

## 1. Ma trận 11 quy tắc cần chuyên gia

| # | Quy tắc | Phân loại | Nguồn chính | Cách đọc có căn cứ (✓ = đang dùng) | Tác động đo được | Cần quyết định |
|---|---|---|---|---|---|---|
| R01 | Phạm vi của 'hội / gặp / thích' khi câu sách không nêu phạm vi | **nguồn chưa đủ** | KL tr.132; KL tr.193; KL tr.85; KL tr.62; TT tr.24; TT tr.142; KL tr.53 | ✓ tam phương tứ chính (đồng cung + đối cung + hai tam hợp) — cách đọc đang dùng cho điều kiện không nêu phạm vi<br>mọi cung chiếu vào Mệnh, không tính chính cung Mệnh<br>chỉ đối cung (xung chiếu)<br>chỉ đồng cung<br>chỉ hai cung tam hợp | tỷ lệ lá số (lõi đúng) đổi trạng thái khi đọc phạm vi khác tam phương (số liệu ở mục dưới / JSON) | chọn phạm vi cho từng câu 'hội/thích' hoặc giữ nhiều bản đọc song song |
| R02 | Liệt kê 'Kiếp, Không, Kị' (TT tr.24): một trong ba hay đủ ba | **nguồn chưa đủ** | TT tr.24; TT tr.24; TH tr.116 | ✓ một trong ba sao, trong tam phương (đang dùng; ngữ cảnh câu: 'Mệnh thân và các cung tam hợp xung chiếu')<br>cả cặp Không-Kiếp, hoặc Kỵ<br>ít nhất hai trong ba<br>đủ cả ba<br>một trong ba nhưng chỉ ở Mệnh/Thân (đọc 'gặp' hẹp nhất) | tỷ lệ phá của Cơ Nguyệt Đồng Lương trên 14,688 lá số có lõi (số liệu ở mục dưới / JSON) | đọc câu liệt kê và 'gặp' theo cách nào |
| R03 | Ngưỡng sát tinh phá cách (≥1 sát tinh; ≥3 sát tinh + Kỵ) và hai breaker phân biệt kém | **nguồn chưa đủ** | TH tr.77; TH tr.116; KL tr.62; KL tr.199; KL tr.85; KL tr.85 | ✓ ≥1 trong sáu sát tinh ở tam phương (đang dùng cho Khôi Việt giáp Mệnh)<br>≥2 sát tinh<br>≥2 trong Tứ sát<br>✓ ≥3 sát tinh VÀ Kỵ (đang dùng cho Sát Phá Liêm Tham — quy ước thiết kế) | KVGM (2.784 lá số có lõi) và SPLT (29.328) (số liệu ở mục dưới / JSON) | ngưỡng và tập sát tinh; có nên để Khoa/Tuần/Triệt làm giảm nhẹ |
| R04 | 'Chiếu' (KL tr.66) = đối cung hay cả tam phương; 'Khôi Việt chiếu' (KL tr.68) | **nguồn chưa đủ** | KL tr.66; KL tr.67; KL tr.68; TT tr.142 | ✓ đồng cung hoặc xung chiếu (đối cung) — đang dùng<br>đồng cung hoặc chiếu từ mọi cung trong tam phương<br>chỉ đồng cung | Tam kỳ gia hội: tỷ lệ bị phá theo cách đọc 'chiếu' (4.048 lá số có lõi) (số liệu ở mục dưới / JSON) | 'chiếu' hẹp hay rộng; cùng câu hỏi cho 'Khôi Việt chiếu' |
| R05 | Nhâm-Khoa: Thiên Phủ (TH) hay Tả Phụ (KL); Canh trong văn bản 全書 số hóa | **nguồn mâu thuẫn** | KL tr.36 | ✓ Nhâm-Khoa = Tả Phụ (production; Khảo Luận tr.36, tr.197)<br>Nhâm-Khoa = Thiên Phủ (Thực Hành tr.20-21; trùng với 全書 số hóa)<br>Thêm: Canh-Khoa Thái Âm, Kỵ Thiên Đồng (全書 số hóa; KL và TH đều ghi Khoa Thiên Đồng, Kỵ Thái Âm) | trạng thái của 17 biến thể trong 16.704 lá số của hai năm Canh và hai năm Nhâm (số liệu ở mục dưới / JSON) | chọn bảng mặc định và có cho người dùng chọn không |
| R06 | Độ sáng Thái Dương ở Thân/Mùi | **nguồn chưa đủ** | TH tr.31; TH tr.32 | gán Thân/Mùi mức hãm<br>gán Thân/Mùi mức bình<br>gán Thân/Mùi mức đắc<br>gán Thân/Mùi mức vượng<br>gán Thân/Mùi mức miếu | Nhật Nguyệt tịnh minh (KL tr.53/68): lá số có lõi mà Thái Dương nằm ở Thân/Mùi (số liệu ở mục dưới / JSON) | tra bảng độ sáng đầy đủ ở nguồn khác hoặc giữ trống |
| R07 | Tuần/Triệt hai chiều (cứu hung tinh vs làm hại quý tinh vs điều kiện thuận) | **nguồn mâu thuẫn** | KL tr.55; TH tr.94; TH tr.95; KL tr.222; KL tr.85; KL tr.85; KL tr.199 | ✓ làm hại: Tử Phủ, Phủ, Tướng, Vũ Tướng (KL tr.55, 222; TH tr.94-95)<br>cứu: Thái Dương hãm, sát tinh gặp Thái Dương, 'hung tinh chịu lép vế' (KL tr.85, 199-200)<br>✓ điều kiện thuận: Nhật Nguyệt Sửu Mùi cần Tuần (KL tr.53); Cự Môn Tý Ngọ gặp Tuần/Triệt là kỳ cách (KL tr.106, TH tr.43) | Tuần/Triệt đóng ở Mệnh khi lõi đúng (số liệu ở mục dưới / JSON) | Tuần/Triệt có thể đồng thời hại và cứu trong một lá số: cần quy tắc ưu tiên của chuyên gia |
| R08 | Ba định nghĩa Thạch trung ẩn ngọc; hai kết cục Mã đầu đới kiếm; TT tr.142 coi Kình ở Ngọ là xấu | **nguồn mâu thuẫn** | KL tr.44; KL tr.58; KL tr.106; TH tr.43; KL tr.64; KL tr.64; TT tr.142 | ✓ Cự Môn ở Mệnh, Thiên Cơ ở Di, Tý/Ngọ<br>✓ Cự Môn Tý/Ngọ có Khoa Quyền Lộc tam hợp chiếu<br>✓ Cự Môn Tý/Ngọ gặp Tuần/Triệt (hoặc Hóa Lộc)<br>✓ Kình ở Ngọ + Thất Sát + Thiên Hình đồng cung: xấu<br>✓ Kình đồng cung, xa Thất Sát/Thiên Hình, gặp Khoa Quyền Lộc: tốt | quy mô từng định nghĩa (lá số) (số liệu ở mục dưới / JSON) | định nghĩa nào là 'cách' của trường phái nào |
| R09 | Tử Phủ đồng cung: TH tr.72 'Mệnh hay Thân' và TT tr.22 'Tỵ Hợi'; mệnh đề 'Giáp nhân' | **nguồn mâu thuẫn** | TH tr.72; TT tr.22; TT tr.22; TT tr.22; TT tr.22; KL tr.50; KL tr.68 | ✓ chỉ neo ở Mệnh (đang dùng)<br>Mệnh hoặc Thân (TH tr.72)<br>TT tr.22 'Tử Phủ đồng cung lâm Tị Hợi' đọc là chép nhầm của 'Tử Sát đồng lâm Tỵ Hợi' (KL tr.50 mục 13, cùng vế sau 'nhất triều phú quí song toàn')<br>'vô sát tấu' chỉ cho tuổi Giáp (TT tr.22) | lá số (số liệu ở mục dưới / JSON) | có thêm neo Thân; có tách mệnh đề tuổi Giáp |
| R10 | Trang TH tr.72 và tr.74 (lớp chữ vỡ) | **nguồn xác nhận** | TH tr.72; TH tr.72; TH tr.72; TH tr.72; TH tr.72; TH tr.72; TH tr.74 | — | cả hai trang đã được đọc trực tiếp từ ảnh ở độ phân giải 1.6x; mọi câu hiện được dùng đều đọc rõ (số liệu ở mục dưới / JSON) | không còn |
| R11 | Cơ chế: 2 yếu tố tăng thế = thành thượng; phản chứng hạ một bậc; không cộng điểm | **nguồn chưa đủ** | — | thành thượng từ 1 yếu tố; phản chứng hạ 0 bậc<br>thành thượng từ 1 yếu tố; phản chứng hạ 1 bậc<br>thành thượng từ 1 yếu tố; phản chứng hạ 2 bậc<br>thành thượng từ 2 yếu tố; phản chứng hạ 0 bậc<br>✓ thành thượng từ 2 yếu tố; phản chứng hạ 1 bậc | tỷ lệ lá số (lõi đúng) đổi trạng thái khi đổi cơ chế (số liệu ở mục dưới / JSON) | giữ như quy ước hiển thị hay thay bằng phân hạng theo TH tr.76-77 |

### 1.1 Hồ sơ từng quy tắc

Mỗi mục: nguyên văn · trang · ngữ cảnh trước/sau (tự trích từ trang; câu in trong ảnh được ghi 'đọc từ ảnh') · kết luận. Toàn bộ trong `formation_rule_dossier.json`.

#### R01 — Phạm vi của 'hội / gặp / thích' khi câu sách không nêu phạm vi

*Câu hỏi:* Khi sách nói 'hội Tả Hữu', 'thiếu Tả Hữu', 'thích Xương Khúc...', phạm vi là đồng cung, đối cung, tam hợp hay cả tam phương tứ chính?
*Phân loại:* **nguồn chưa đủ** · *Trạng thái:* mo (cần chuyên gia)

- KL tr.132 (van_ban): “cách Tử Phủ Vũ Tướng mà thiếu Tả Hữu” _…anh hùng áo vải lại thích Thai Tọa là ghế gỗ, xe thồ, miễn sao được việc. Cho nên người xưa vẫn quan niệm rằng_ **[câu]** _thì đi tìm Tham Tọa thay thế, e rằng bị trật đường rầy, hóa ra đầu Ngô mình Sở, không những không được việc……_
- KL tr.193 (van_ban): “Xương Khúc, Tử Phủ Vũ Tướng là người văn võ toàn tài” _…TỬ VI KHẢO LUẬN – Hòang Thường – Hàm Chương www.tuviglobal.com 193_ **[câu]** _. Xương Khúc, Cơ Nguyệt Đồng Lương là lúc đắc thời gặp được minh chủ ý hợp tâm đầu. 19. Đẩu quân Thiếu dương……_
- KL tr.85 (van_ban): “Thái dương thích Xương, Khúc, Khoa, Quyền, Lộc” _…- Thái dương hãm địa, cần gặp Tuần, Triệt, cũng cần gặp Đào, Hồng, Hỉ giúp sức gỡ thế bí, để có đường thoát. -_ **[câu]** _, có nhóm văn tinh này giúp sức thì được hưởng phúc lộc. - Thái dương ghét lũ Riêu, Đà, Kỵ gặp đám tang ám……_
- KL tr.62 (van_ban): “Mệnh có Khôi Việt, Xương, Khúc và Lộc tồn đồng cung hay hội chiếu” _…ược cành quế tượng trưng danh vọng. 2 . Khôi, Việt, Xương, Khúc, Lộc tồn phùng, Hình Sát vô hung, đại phú quí:_ **[câu]** _lại không bị Hóa kỵ Thiên hình cản phá thì giàu sang lớn. 3 . Khôi tinh lâm Mệnh vị chí tam công, Khôi tinh……_
- TT tr.24 (van_ban): “Mệnh thân và các cung tam hợp xang chiếu có đủ bốn sao trên đây” _…các sao tốt, phú quí. Nếu gặp Thiên Hình, Hóa Kị dễ chán mùi thế luỵ). - Cơ Nguyệt đông lương tác lại nhân. (_ **[câu]** _nếu không có những cát tinh khác trợ lực chỉ làm công chức quèn. Gặp Kiếp Không Hoá Kị xuống hạ cách). -……_
- TT tr.142 (van_ban): “Khoa, Quyền lộc củng (Chiếu thủ có cả ba Khoa, Quyền, Lộc)” _…cung xấu). - Hình tù hiệp ấn (Thiên Tướng thủ Mệnh Thân, có Thiên Hình Liêm Trinh hội hiệp quí về võ cách). -_ **[câu]** _- Tham Hỏa tương phùng (Tham Lang cư miếu địa, thủ Mệnh tại cung Mão) - Kình Dương nhập miếu (Đơn thủ Mệnh……_
- KL tr.53 (van_ban): “lại không có Đào Hồng Hỉ hay Khoa Quyền Lộc hợp chiếu” _…8 . Nhật Nguyệt đồng cung Sửu Mùi, tam phương vô cát, phản vi hung Mệnh có Nhật Nguyệt ở đồng cung ở Sửu Mùi,_ **[câu]** _thì chỉ đủ cơm no áo ấm không thể vinh hiển được. 9 . Nhật Nguyệt tịnh tranh quang, Quyền lộc phi tàn Nhật……_

Chính các trang phân biệt đồng cung với chiếu khi cần: KL tr.62 'đồng cung hay hội chiếu', KL tr.66 'đồng cung hoặc chiếu', KL tr.67 'đồng cung hay xung chiếu', TT tr.142 'Chiếu thủ có cả ba Khoa, Quyền, Lộc', TT tr.24 'các cung tam hợp xung chiếu'. Vì vậy một câu chỉ nói 'hội' không tự động là đồng cung; nhưng cũng không có trang nào nói 'hội' = đủ cả tam phương tứ chính.

*Đang triển khai:* tam phương (đánh dấu `co_nguon_con_gia_dinh` ở từng quy tắc).

#### R02 — Liệt kê 'Kiếp, Không, Kị' (TT tr.24): một trong ba hay đủ ba

*Câu hỏi:* 'Gặp Kiếp Không Hoá Kị xuống hạ cách': chỉ cần gặp một sao, một cặp, hay đủ cả ba? Và 'gặp' ở đâu: Mệnh/Thân hay cả tam hợp xung chiếu?
*Phân loại:* **nguồn chưa đủ** · *Trạng thái:* mo (cần chuyên gia)

- TT tr.24 (van_ban): “Mệnh thân và các cung tam hợp xang chiếu có đủ bốn sao trên đây” _…các sao tốt, phú quí. Nếu gặp Thiên Hình, Hóa Kị dễ chán mùi thế luỵ). - Cơ Nguyệt đông lương tác lại nhân. (_ **[câu]** _nếu không có những cát tinh khác trợ lực chỉ làm công chức quèn. Gặp Kiếp Không Hoá Kị xuống hạ cách). -……_
- TT tr.24 (van_ban): “Gặp Kiếp Không Hoá Kị xuống hạ cách” _…ung tam hợp xang chiếu có đủ bốn sao trên đây nếu không có những cát tinh khác trợ lực chỉ làm công chức quèn._ **[câu]** _). - Thiên Lương Tham Nguyệt đồng cơ hội, mộ dạ kinh thương vô miên thuỵ. (Các sao Thiên Lương, Thái Aâm,……_
- TH tr.116 (van_ban): “Cơ Nguyệt Đồng Lương hay Cự Nhật mà gặp Kình Đà, Không Kiếp hay Phá toái, Kiếp sát” _…n Cự môn, ngộ Linh Hỏa ại Tiểu hạn thất lọ: Khi găp các cách cuộc sau đây thì thất lợi cho Đại hạn hay Tiều a._ **[câu]** _thì dễ tàn tật, mất cướp b. Sát phá Liêm Tham mà gặp Nhị tam Không, Linh Hỏa Kình Kỵ hay Đại tiểu Hao Hình,……_

*Đang triển khai:* một trong ba, tam phương: 82,1% bị phá.

#### R03 — Ngưỡng sát tinh phá cách (≥1 sát tinh; ≥3 sát tinh + Kỵ) và hai breaker phân biệt kém

*Câu hỏi:* Sách nói 'nhiều sát tinh' (TH tr.77) và 'bị sát tinh hội chiếu' (KL tr.62) mà không nêu số lượng. Bao nhiêu sát tinh, ở đâu, thì phá cách?
*Phân loại:* **nguồn chưa đủ** · *Trạng thái:* mo (cần chuyên gia)

- TH tr.77 (van_ban): “Sát Phá Liêm Tham hội Vũ, Kình Đà” _…: Có những cách chính tinh như trên, nhưng không gặp được cát tinh hội đủ b ëp Hung tinh và sát tinh đóng. dụ:_ **[câu]** _, Thiên địa Kho tinh cùng hung tinh sát tinh nhiều ở vào nơi hãm địa p phải cách ấy thì thật suốt đời lao……_
- TH tr.116 (van_ban): “Sát phá Liêm Tham mà gặp Nhị tam Không, Linh Hỏa Kình Kỵ” _…Cơ Nguyệt Đồng Lương hay Cự Nhật mà gặp Kình Đà, Không Kiếp hay Phá toái, Kiếp sát thì dễ tàn tật, mất cướp b._ **[câu]** _hay Đại tiểu Hao Hình, Sát Phục binh, Tang Hổ thì tù ngục vong gia c. Tử Phủ Vũ Tướng găp phải Tam Không,……_
- KL tr.62 (van_ban): “Cung mệnh có Khôi Việt lại bị sát tinh hội chiếu thì mang bệnh tật khó chữa khỏi” _…ợc Khôi Việt giáp mệnh thì được mọi người kính nể, yêu quí. 4 . Khôi Việt trùng phùng sát thấu, cố tật vưu đa:_ **[câu]** _. PHÚ VỀ SAO LỘC TỒN 1 . Lộc tồn thủ ư Tài, Trạch, tích ngọc mai kim: Lộc tồn đóng ở cung Tài, hay cung Điền……_
- KL tr.199 (van_ban): “Hung tinh chịu lép vế khi gặp Khoa, Tuần Triệt, Tài Thọ, Quan Phúc” _…còn tiềm ẩn cái xấu. Hung tinh hãm địa gieo nhiều tai họa, nhất là hung tinh khắc Mệnh hay khắc Can năm sinh._ **[câu]** _. Hung tinh được chia ra như sau: Lục sát tinh: Không Kiếp, Kình Đà, Hỏa Linh, ngoài ra các sao Kiếp sát, Lưu……_
- KL tr.85 (van_ban): “Thái dương sợ: Kình, Đà, Không, Kiếp, gặp đám sát tinh này thì công danh trắc trở” _…Riêu, Đà, Kỵ gặp đám tang ám này, thì bị miệng tiếng, bôi nhọ danh dự và chính bản thân cũng có điều mờ ám! -_ **[câu]** _, đổ vỡ, lúc đó cần Tuần Triệt cứu giải để giảm bớt đau thương! - Thái dương gặp Tuần, Triệt, có 2 cách:……_
- KL tr.85 (van_ban): “lúc đó cần Tuần Triệt cứu giải để giảm bớt đau thương” _…ũng có điều mờ ám! - Thái dương sợ: Kình, Đà, Không, Kiếp, gặp đám sát tinh này thì công danh trắc trở, đổ vỡ,_ **[câu]** _! - Thái dương gặp Tuần, Triệt, có 2 cách: +Thái dương đắc địa ở cung ban ngày gặp Tuần Triệt thì bế tắc vì……_

*Ghi chú:* Điều kiện của KL tr.62 mục 4 mô tả 'Cung mệnh CÓ Khôi Việt', không phải Khôi Việt GIÁP Mệnh; cả trên cấu trúc đúng như sách mô tả, 'ít nhất một sát tinh hội chiếu' vẫn đúng ở 83,1% lá số. Vậy tần suất cao không do việc lấy nhầm cấu trúc mà do ngưỡng 'một'. KL tr.199/85 còn nói Khoa, Tuần Triệt 'làm hung tinh lép vế / cứu giải' cho Thái Dương: sát tinh không luôn phá.

*Đang triển khai:* KVGM: ≥1 sát tinh (91,7% bị phá, cờ `chua_du_nguon`); SPLT: ≥3 sát tinh + Kỵ (quy ước).

#### R04 — 'Chiếu' (KL tr.66) = đối cung hay cả tam phương; 'Khôi Việt chiếu' (KL tr.68)

*Câu hỏi:* KL tr.66: Kỵ, Kình 'đồng cung hoặc chiếu vào'; KL tr.67 dùng riêng 'xung chiếu'. 'Chiếu' có rộng hơn 'xung chiếu' không?
*Phân loại:* **nguồn chưa đủ** · *Trạng thái:* mo (cần chuyên gia)

- KL tr.66 (van_ban): “Cung mệnh có Khoa, Quyền, Lộc hội họp mà lại bị Hóa kỵ, Kình dương đồng cung hoặc chiếu vào” _…với khốc đồng cung thì giàu sang quyền thế rõ ràng. 10. Tam kỳ giao hội, mặc ngộ Kỵ, Kình giáng lộ thanh vân :_ **[câu]** _thì đường công danh mờ mịt như sương tụ đầy đường đi. 11. Hoá kỵ văn nhân bất nại : Cung mệnh có Hóa kỵ gặp……_
- KL tr.67 (van_ban): “gặp Hoá khoa đồng cung hay xung chiếu” _…rở không thành. 12. Kỵ ngộ Khoa tinh cư Hợi, Tí, ngôn hành danh thuận. Cung mệnh tại Hợi, Tí có Hóa kỵ tọa thủ_ **[câu]** _là người cẩn thận lời ăn tiếng nói, nên được mọi người kính nể. PHÚ ĐOÁN VỀ BỘ SAO LỤC BẠI 1. Nam nhân Tang,……_
- KL tr.68 (van_ban): “chỉ mong được Khôi Việt chiếu mới là tốt đẹp” _…phản bối hà vọng thanh quang, tối hỷ ngoại chiều Khôi Việt. Mệnh có Nhật Nguyệt hãm địa thì làm sao sáng được,_ **[câu]** _. 3. Khốc Hư Tí Ngọ đồng cung, Tiền bần hậu phú : Mệnh ở Tí Ngọ có Khốc Hư đồng cung thì tuổi trẻ nghèo, tuổi……_
- TT tr.142 (van_ban): “Khoa, Quyền lộc củng (Chiếu thủ có cả ba Khoa, Quyền, Lộc)” _…cung xấu). - Hình tù hiệp ấn (Thiên Tướng thủ Mệnh Thân, có Thiên Hình Liêm Trinh hội hiệp quí về võ cách). -_ **[câu]** _- Tham Hỏa tương phùng (Tham Lang cư miếu địa, thủ Mệnh tại cung Mão) - Kình Dương nhập miếu (Đơn thủ Mệnh……_

*Đang triển khai:* đối cung (28,5% bị phá).

#### R05 — Nhâm-Khoa: Thiên Phủ (TH) hay Tả Phụ (KL); Canh trong văn bản 全書 số hóa

*Câu hỏi:* Đây là khác biệt trường phái, lỗi in hay lỗi diễn giải?
*Phân loại:* **nguồn mâu thuẫn** · *Trạng thái:* mo (cần chuyên gia)

- KL tr.36 (van_ban): “Nhâm Lương Vi Phụ Vũ” _…nh Nguyệt Đồng Cơ Cự Mậu Tham Nguyệt Bật Cơ Kỷ Vũ Tham Lương Khúc Canh Nhật Vũ Đồng Âm Tân Cơ Dương Khúc Xương_ **[câu]** _Quí Phá Cự Âm Tham Bảng giải thích các tên chính tinh và trung tinh dùng trong Tứ hóa Liêm = Liêm Trinh Tham……_
- TH tr.20: “Nhâm : Lương, Tử, Phủ, Vũ tú thị” — đọc trực tiếp từ ảnh trang TH tr.20: chữ 'Phủ' rõ ràng trong câu thơ
- TH tr.21: “Người sinh năm NHÂM: Lộc an với Thiên Lương, Quyền an với Tử vi, Khoa an với Thiên Phủ, Ky an với Vũ Khúc” — đọc trực tiếp từ ảnh trang TH tr.21: văn xuôi gọi đích danh 'Thiên Phủ'
- KL tr.197: “Tuổi Nhâm: Lương Vi Phụ Vũ ... Tả phụ, phải khéo léo, chăm chỉ mới có danh” — đọc trực tiếp từ ảnh trang KL tr.197: bình riêng từng sao, 'Tả phụ' đứng ở vị trí Khoa (danh)
- zh.wikisource.org (紫微斗數全書, 卷二, 安祿權科忌四星變化訣): “壬梁紫府武宿是; 庚日武陰同為首” — văn bản số hóa của một ấn bản, truy cập 2026-10-17 (nguồn NGOÀI ba sách của dự án)
- zh.wikipedia.org (紫微斗數, 安四化星): “bảng hai cột 紫微斗數全集 / 紫微斗數全書 khác nhau đúng hai hàng: 庚 và 壬 (左 / 府)” — nguồn thứ cấp, chỉ dùng để xác nhận rằng hai hàng này vốn có hai biến thể truyền thống

**Kết luận:** Không phải lỗi in của một chỗ (TH in Thiên Phủ ở cả câu thơ lẫn văn xuôi; trang có các lỗi in khác như 'Khao', 'Vự Môn', nên không thể loại trừ hoàn toàn một lỗi lặp, nhưng lặp ở hai chỗ khác dạng là dấu hiệu của chủ ý) và không phải lỗi diễn giải của dự án: một văn bản 全書 số hóa độc lập cũng ghi 府, trong khi KL (và 全集 theo zh.wikipedia) ghi 左輔. Đây là khác biệt giữa hai dòng văn bản truyền thống; chưa có bằng chứng chọn bên nào.

*Đang triển khai:* Khảo Luận (Tả Phụ) làm mặc định; bảng của từng nguồn lưu riêng ở data/experimental/tu_hoa_tables.json; đề xuất tham số `tu_hoa_table` (KL mặc định, TH, TT_WS) hiển thị nhãn nguồn, không đổi âm thầm.

#### R06 — Độ sáng Thái Dương ở Thân/Mùi

*Câu hỏi:* TH tr.31 liệt kê Thái Dương miếu ở Mão; vượng Ngọ, Tỵ, Thìn, Dần; bình Dậu; hãm Tuất, Hợi, Tí, Sửu — thiếu Thân và Mùi. Có được suy ra không?
*Phân loại:* **nguồn chưa đủ** · *Trạng thái:* mo (cần chuyên gia)

- TH tr.31 (van_ban): “Bình thì ở Dậu khá tường” _…ệt đỡ được đôi phần. Nếu nữ mệnh ga SAO THÁI DƯƠNG Thái dương miếu ở Mão cung, Vương ở Ngọ, Tỵ, Thìn, Dần, một_ **[câu]** _, Hãm : Tuất, Hợi, Tí, Sửu cu…_
- TH tr.32 (van_ban): “Từ Mùi đến Sửu bần cùng khốn” _…tươm tất, thảo ngay, h Canh nhân: Ngọ mệnh khá Nhâm nhân: Ngọ mệnhquí quyền tinh thô Giảp nhân: Hợi mệnh vô du_ **[câu]** _th Dương Đà, Không Kiếp a Đa phiền tâm sự tính ngày lo đêm Da đen sắc hãm tính hen Kyk, Đà: tật mục chẳng yên……_

*Ghi chú:* TH tr.32 có dòng 'Từ Mùi đến Sửu bần cùng khốn' nằm giữa các câu về Thái Dương, nhưng không nêu mức sáng của Thân/Mùi; không đủ để suy ra.

*Đang triển khai:* để trống (kết quả 'chưa biết', điều kiện không được tính là sai).

#### R07 — Tuần/Triệt hai chiều (cứu hung tinh vs làm hại quý tinh vs điều kiện thuận)

*Câu hỏi:* Tuần/Triệt là phản chứng, sao cứu, hay điều kiện thuận — tùy cách?
*Phân loại:* **nguồn mâu thuẫn** · *Trạng thái:* mo (cần chuyên gia)

- KL tr.55 (van_ban): “chỉ sợ Triệt Tuần án ngữ thì kém đi thôi” _…đồng cung tối vi phúc hậu, thiết hiềm nội trở Triệt Tuần Mệnh có Tử Phủ thì được hưởng phúc lộc tốt rất nhiều,_ **[câu]** _. 2 . Thiên phủ lâm giải ách nhi vô bệnh, Địa kiếp lâm Phúc đức nhi hữu tai Thiên phủ ở cung Ách thì không……_
- TH tr.94 (van_ban): “Nhưng nếu Phủ gặp Tuần Triệt hay Thiên, Địa Không” _…tu ha Ở NỮ MỆNH : Thiên phủ là người mặt tươi đẹp như hoa; hội cát tinh tất giàu sang sống lâu, lợi chồng con._ **[câu]** _thì suốt đời lao tâm, đau khổ vì chồng co THÁI ÂM Ở NAM MỆNH : Thái âm miếu vượng hay đắc địa hôi cát tinh……_
- TH tr.95 (van_ban): “Nhưng nếu Tướng miếu vượng đắc địa mà gặp Tuần Triệt án ngữ, chẳng khác nào như Tướng hãm địa” _…: Tướng miếu vượng hay đắc địa là người thông minh dáng cách uy nghi phúc hậu, tất có uy quyền và danh tiếng._ **[câu]** _mà gặp sát tinh, cuộc đời sẽ lao đao, chỉ có tu hành mới tránh được Ở NỮ MỆNH : Tướng miếu vượng đắc địa là……_
- KL tr.222 (van_ban): “Mệnh có Vũ Tướng mà không bị Tuần Triệt án ngữ thì cuộc đời suôn” _…. Vũ Sát ở Mão Dậu thì chặt chém chẳng nể tình. Vũ Tham ở Sửu Mùi thì cố thủ tham tiềm miễn có tiền là được. V_ **[câu]** _Liêm Tham ở Tỵ Hợi thì giang hồ liều mạng, chẳng sợ tù đầy. L Liêm Sát ở Sửu 9. Thiên phủ: Thiên phủ cũng là……_
- KL tr.85 (van_ban): “Thái dương hãm địa, cần gặp Tuần, Triệt, cũng cần gặp Đào, Hồng, Hỉ giúp sức” _…rắng tay. *Thái dương đắc địa vẫn cần Đào Hồng Hỉ, có nhóm Tam minh này thì công danh đến mau chóng dễ dàng. -_ **[câu]** _gỡ thế bí, để có đường thoát. - Thái dương thích Xương, Khúc, Khoa, Quyền, Lộc, có nhóm văn tinh này giúp sức……_
- KL tr.85 (van_ban): “lúc đó cần Tuần Triệt cứu giải để giảm bớt đau thương” _…ũng có điều mờ ám! - Thái dương sợ: Kình, Đà, Không, Kiếp, gặp đám sát tinh này thì công danh trắc trở, đổ vỡ,_ **[câu]** _! - Thái dương gặp Tuần, Triệt, có 2 cách: +Thái dương đắc địa ở cung ban ngày gặp Tuần Triệt thì bế tắc vì……_
- KL tr.199 (van_ban): “Hung tinh chịu lép vế khi gặp Khoa, Tuần Triệt, Tài Thọ, Quan Phúc” _…còn tiềm ẩn cái xấu. Hung tinh hãm địa gieo nhiều tai họa, nhất là hung tinh khắc Mệnh hay khắc Can năm sinh._ **[câu]** _. Hung tinh được chia ra như sau: Lục sát tinh: Không Kiếp, Kình Đà, Hỏa Linh, ngoài ra các sao Kiếp sát, Lưu……_
- KL tr.200 (van_ban): “Những sao giải mạnh gồm Tuần Triệt, Thiên tài, Hóa khoa, Quan Phúc” _…a kỵ, Kiếp sát, Lưu hà như là lũ sát tinh. tức chế biến, cải trang lại, không nguy hiểm mà có khi còn tốt nữa._ **[câu]** _.…_
- KL tr.53 (van_ban): “rất cần Tuần không án ngữ ở Mệnh” _…Không, Quí Ân Xương Khúc, văn tất thượng cách, đường quan xuất chính Mệnh ở Sửu Mùi có Nhật nguyệt đồng cung,_ **[câu]** _để trở nên sáng đẹp thì nổi tiếng văn chương, ắt sẽ làm lớn. 12 . Nhật Nguyệt sát hại, nam đa gian, nữ đa dâm……_
- KL tr.106 (van_ban): “Cự môn ở Tí Ngọ gặp Tuần Triệt là kỳ cách” _…ỉ thì tránh được họa lớn.  Người có Cự môn thủ Mệnh, dù ở bất cứ cung nào cũng ôm cao vọng nhưng hay bất mãn._ **[câu]** _, người xưa gọi là “Thạch trung ẩn ngọc” ví như ngọc nằm trong đá, có thợ đẽo đá cắt gọt thành viên ngọc quí,……_
- TH tr.43 (van_ban): “cần gặp được Tuần, Triệt hay Hóa Lộc thì ngọc mới lộ ra được” _…áp, lý luận, thường làm nghề Thầy kiện, Quan Toà. Cự ở cung Tí, Ngọ là ngọc trong đá (Thạch trung ẩn ngọc) nên_ **[câu]** _, thì mới đẹp rực rỡ. Nếu không ặp được cách này hay lại gặp Lộc tồn th hưng không gặp đươc thời vận hiển……_

*Đang triển khai:* hại ở Tử Phủ Vũ Tướng / Tử Phủ đồng cung; thuận trong lõi Thạch trung ẩn ngọc (KL106); không dùng ở Nhật Nguyệt; sao cứu chưa mô hình hóa.

#### R08 — Ba định nghĩa Thạch trung ẩn ngọc; hai kết cục Mã đầu đới kiếm; TT tr.142 coi Kình ở Ngọ là xấu

*Câu hỏi:* Các định nghĩa có thật sự mâu thuẫn hay chỉ mô tả các tập khác nhau?
*Phân loại:* **nguồn mâu thuẫn** · *Trạng thái:* mo (cần chuyên gia)

- KL tr.44 (van_ban): “Thạch trung ẩn ngọc -Ngọc quí ở trong đá -Mệnh có Cự môn, Di có Thiên cơ ở Tí Ngọ” _…TỬ VI KHẢO LUẬN – Hòang Thường – Hàm Chương www.tuviglobal.com 44 6._ **[câu]** _7. Tam hoá liên châu -3 viên ngọc quí - Mệnh có Cự môn, Di có Thiên cơ ở Tí Ngọ 8. Toạ quí hướng hướng quí……_
- KL tr.58 (van_ban): “Mệnh ở Tí Ngọ có Cự môn được Khoa Quyền Lộc tam hợp chiếu là cách ngọc ở trong đá” _…TỬ VI KHẢO LUẬN – Hòang Thường – Hàm Chương www.tuviglobal.com 58_ **[câu]** _, phú quí giàu sang. 2.Cự Nhật Dần Thân, quan phong tam đại : Mệnh ở Dần, Thân có cự môn đồng cung với Thái……_
- KL tr.106 (van_ban): “Cự môn ở Tí Ngọ gặp Tuần Triệt là kỳ cách” _…ỉ thì tránh được họa lớn.  Người có Cự môn thủ Mệnh, dù ở bất cứ cung nào cũng ôm cao vọng nhưng hay bất mãn._ **[câu]** _, người xưa gọi là “Thạch trung ẩn ngọc” ví như ngọc nằm trong đá, có thợ đẽo đá cắt gọt thành viên ngọc quí,……_
- TH tr.43 (van_ban): “cần gặp được Tuần, Triệt hay Hóa Lộc thì ngọc mới lộ ra được” _…áp, lý luận, thường làm nghề Thầy kiện, Quan Toà. Cự ở cung Tí, Ngọ là ngọc trong đá (Thạch trung ẩn ngọc) nên_ **[câu]** _, thì mới đẹp rực rỡ. Nếu không ặp được cách này hay lại gặp Lộc tồn th hưng không gặp đươc thời vận hiển……_
- KL tr.64 (van_ban): “Mệnh ở Ngọ, có Kình dương, gặp Thất sát, Thiên hình đồng cung là cách kiếm kể cổ ngựa” _…, Linh tinh, gặp tiểu hạn có Bạch hổ thì dễ gặp thương tổn. 5 . Mã đầu đới kiếm, phi yểu chiết nhi hình thương_ **[câu]** _, thì không chết yểu cũng mang tàn tật khổ sở. 6 . Mã đầu đới kiếm, trấn ngự biên cương: Mệnh ở Ngọ, có Kình……_
- KL tr.64 (van_ban): “có Kình dương đồng cung, nhưng xa lánh được Thất sát, Thiên hình mà lại gặp được Khoa Quyền Lộc” _…kể cổ ngựa, thì không chết yểu cũng mang tàn tật khổ sở. 6 . Mã đầu đới kiếm, trấn ngự biên cương: Mệnh ở Ngọ,_ **[câu]** _thì tại có sự nghiệp lớn, hiển đạt về võ nghiệp. 7 . Kình dương, Đồng Âm nhi phùng Phượng, Giải nhất thế uy……_
- TT tr.142 (van_ban): “phải ở tứ mộ địa mới hay, ở Ngọ cung xấu” _…hái Dương đều đứng ở miếu vượng địa chiếu sáng). - Mã đầu đới nhẫn (Nhẫn là sao Kình Dương gặp Thiên Mã, nhưng_ **[câu]** _). - Hình tù hiệp ấn (Thiên Tướng thủ Mệnh Thân, có Thiên Hình Liêm Trinh hội hiệp quí về võ cách). - Khoa,……_

**Kết luận:** Thạch trung ẩn ngọc: ba định nghĩa chọn ba tập lá số khác nhau (1.728 / 696 / 32 lá số) và sách không gắn kết luận tốt/xấu khác nhau cho chúng, nên chúng khác nhau về TÊN CÁCH chứ chưa mâu thuẫn về hệ quả. Trong mô hình này Cự Môn ở Tý/Ngọ luôn có Thiên Cơ ở đối cung nên vế sau của KL tr.44 tự động đúng. Mã đầu đới kiếm: KL gắn tên cách với Kình ở Ngọ; TT tr.142 gắn với Kình gặp Thiên Mã. Trong mô hình, Kình (Mão Thìn Ngọ Mùi Dậu Tuất Tý Sửu) và Thiên Mã (Dần Thân Tỵ Hợi) không bao giờ đồng cung, nên bản TT chỉ có nghĩa nếu 'gặp' rộng hơn đồng cung.

*Đang triển khai:* ba biến thể Thạch trung, hai biến thể Mã đầu; TT tr.142 chưa mô hình hóa.

#### R09 — Tử Phủ đồng cung: TH tr.72 'Mệnh hay Thân' và TT tr.22 'Tỵ Hợi'; mệnh đề 'Giáp nhân'

*Câu hỏi:* Neo ở Mệnh hay Thân? 'Tỵ Hợi' có phải Tử Phủ không? Câu 'vô sát tấu' chỉ áp cho tuổi Giáp?
*Phân loại:* **nguồn mâu thuẫn** · *Trạng thái:* mo (cần chuyên gia)

- TH tr.72 (van_ban): “Tử, Phủ đồng cung cáh (đóng ở Mệnh hay Thân)” _…tốt, ở các cung Cách tìm giờ Dạ đề như sau: Mùa Hạ || Dậu Mùa Thu || Tí M II> CÁCH CUỘC LẬP THÀNH Ở 12 C A 1._ **[câu]** _2. Phủ, Tướng triều v 3 4. Sát, 5. Cơ, Liêm, Tham c ng ồng, Lương các . 8. Nh 9. Cư àn cung ần tốt hơ ) 12.……_
- TT tr.22 (van_ban): “Tử Phủ đồng cung vô sát tấu” _…hiên Phủ toàn y phụ bật chi công. (Tử Vi và Thiên Phủ cần dựa vào hai sao Tả Phụ Hữu Bật mới dễ bề phú quí). -_ **[câu]** _, Giáp nhân hưởng phúc chung thân. (Hai sao Tử Vi, Thiên Phủ đồng cung ở Dần và Thân thủ mệnh, những người……_
- TT tr.22 (van_ban): “Tử Phủ đồng cung lâm Tị Hợi nhất triều phú quí song toàn” _…hiên Phủ toàn y phụ bật chi công. (Tử Vi và Thiên Phủ cần dựa vào hai sao Tả Phụ Hữu Bật mới dễ bề phú quí). -_ **[câu]** _thân. (Hai sao Tử Vi, Thiên Phủ đồng cung ở Dần và Thân thủ mệnh, những người tuổi Giáp hưởng phúc suốt đời……_
- TT tr.22 (van_ban): “Giáp nhân hưởng phúc chung thân” _…ông. (Tử Vi và Thiên Phủ cần dựa vào hai sao Tả Phụ Hữu Bật mới dễ bề phú quí). - Tử Phủ đồng cung vô sát tấu,_ **[câu]** _. (Hai sao Tử Vi, Thiên Phủ đồng cung ở Dần và Thân thủ mệnh, những người tuổi Giáp hưởng phúc suốt đời nếu……_
- TT tr.22 (van_ban): “Tử Vi Thiên Phủ toàn y phụ bật chi công” _…u bị Tứ SaÙt) là Kinh, Đà, Hoả, Linh vây hãm cùng với Kiếp Không chỉ nên đi tu cho thoát tục là tốt hơn cả). -_ **[câu]** _. (Tử Vi và Thiên Phủ cần dựa vào hai sao Tả Phụ Hữu Bật mới dễ bề phú quí). - Tử Phủ đồng cung vô sát tấu,……_
- KL tr.50 (van_ban): “Tử Sát đồng lâm Tỵ Hợi, nhất triều phú quí song toàn” _…có Tử Tướng đồng cung, Thân có phá quân đồng cung với Đế vượng, là người mưu cơ nhưng không lương thiện. 13 ._ **[câu]** _Cung an Mệnh ở Tỵ Hợi có Tử Sát đồng cung thì vừa giàu vừa sang. 14 . Tử vi, Vũ khúc, Phá quân hội Dương Đà,……_
- KL tr.68 (van_ban): “chỉ mong được Khôi Việt chiếu mới là tốt đẹp” _…phản bối hà vọng thanh quang, tối hỷ ngoại chiều Khôi Việt. Mệnh có Nhật Nguyệt hãm địa thì làm sao sáng được,_ **[câu]** _. 3. Khốc Hư Tí Ngọ đồng cung, Tiền bần hậu phú : Mệnh ở Tí Ngọ có Khốc Hư đồng cung thì tuổi trẻ nghèo, tuổi……_

**Kết luận:** Trong mô hình Tử Vi và Thiên Phủ không bao giờ cùng cung ở Tỵ/Hợi (0 lá số) nhưng Tử Vi và Thất Sát cùng cung ở Tỵ/Hợi (1.584 lá số có Mệnh ở đó); câu của TT trùng gần như nguyên văn với KL tr.50 mục 13 về Tử Sát. Đây là bằng chứng văn bản gián tiếp cho nghi ngờ chép nhầm, KHÔNG phải kết luận.

*Đang triển khai:* chỉ Mệnh; câu 'Giáp nhân' và 'toàn y phụ bật' chưa mô hình hóa.

#### R10 — Trang TH tr.72 và tr.74 (lớp chữ vỡ)

*Câu hỏi:* Các câu trích phụ thuộc vào ảnh trang có đọc rõ không?
*Phân loại:* **nguồn xác nhận** · *Trạng thái:* dong (đã đọc ảnh)

- TH tr.72 (van_ban): “Tử, Phủ đồng cung cáh (đóng ở Mệnh hay Thân)” _…tốt, ở các cung Cách tìm giờ Dạ đề như sau: Mùa Hạ || Dậu Mùa Thu || Tí M II> CÁCH CUỘC LẬP THÀNH Ở 12 C A 1._ **[câu]** _2. Phủ, Tướng triều v 3 4. Sát, 5. Cơ, Liêm, Tham c ng ồng, Lương các . 8. Nh 9. Cư àn cung ần tốt hơ ) 12.……_
- TH tr.72 (van_ban): “Tử, Phủ, Vũ, Tướng cách” _…ở Mệnh) . Tham, Vũ đồng hành cách (đóng ở Sửu, Mùi có Mệnh) Phá, ách Nguyệt, Đồ , Lương cách 6. Cơ, Cự, Đ h 7._ **[câu]** _. ật, Nguyệt đo g cung cách ï, Nhật đồng cách (ở D n ở Thân 10. Cự, Cơ đồng cung cách (ở Mão, Dậu) 11. Tả,……_
- TH tr.72 (van_ban): “Nhật, Nguyệt tinh minh cách (Nhật ở Thìn, Tỵ, Nguyệt ở Dậu, Tuất, mà Mệnh đóng ở Nguyệt hay Nhật đều tốt)” _…a Hữu úc, Kho hôi v 1 . khác thì không lợi) 20. Lộc, Mã giao tri cách (ở Mệnh, Tài, Quan, Thiên di đề tốt) 21._ **[câu]** _22. Nhật lệ trung thiên cách ( Nhật cư Ngọ có Mệnh) 23. Nhật chiếu lôi môn cách (Nhật ở Mão có Mệnh) 24.……_
- TH tr.72 (van_ban): “Nhật lệ trung thiên cách ( Nhật cư Ngọ có Mệnh)” _…Nhật, Nguyệt tinh minh cách (Nhật ở Thìn, Tỵ, Nguyệt ở Dậu, Tuất, mà Mệnh đóng ở Nguyệt hay Nhật đều tốt) 22._ **[câu]** _23. Nhật chiếu lôi môn cách (Nhật ở Mão có Mệnh) 24. Nguyệt lãng thiên môn cách (Nguyệt ở Hợi có Mệnh) 25.……_
- TH tr.72 (anh_doc_ro): “Sát, Phá, Liêm, Tham cách” _…M II> CÁCH CUỘC LẬP THÀNH Ở 12 C A 1. Tử, Phủ đồng cung cáh (đóng ở Mệnh hay Thân) 2. Phủ, Tướng triều v 3 4._ **[câu]** _ng ồng, Lương các . 8. Nh 9. Cư àn cung ần tốt hơ ) 12. Tam châu c hao, Qu i liền án cung M 15. Vu võ cách……_
- TH tr.72 (anh_doc_ro): “Tam Hoá hên châu cách (tức Khao, Quyền, Lộc đi liền 3 cung đến cung Mệnh có 1 hóa)” _…n) 2. Phủ, Tướng triều v 3 4. Sát, 5. Cơ, Liêm, Tham c ng ồng, Lương các . 8. Nh 9. Cư àn cung ần tốt hơ ) 12._ **[câu]** _guyệt, Đồng, Cơ, Cự cách. g nào ma ng cách a Hữu úc, Kho hôi v 1 . khác thì không lợi) 20. Lộc, Mã giao tri……_
- TH tr.74 (van_ban): “Nhật Nguyệt hãm tại Mệnh mà không có cứu tinh” _…ào xem bản thì sẽ rõ: H M Mệnh an ở : Mệnh an ở : Mệnh an ở : g (Mã tại Mệnh gặp Tuần, Triệt án ngữ) àn hung (_ **[câu]** _, 8. Lưỡng trùng Hoa cái (Y như cách L 9. Không, Kiếp sát hội (Mệnh gặp Kh III. SINH, VƯỢNG BẠI, TUYỆT ĐỊA V……_
- TH tr.74 (van_ban): “cần được cứu giải băng Tam hóa hội” _…KIM TỴ DẬU NGỌ D M ỘC HỢI MÃO TÍ THÂN H MÃO HỢI ÓA DẦN NGỌ THỦY – THÂN TÍ T DẬU TỴ HỔ Gặp Bại địa và Tuyệt địa_ **[câu]** _hay c được bản mệnh theo Ngũ hành, thì gọi là Tuyệt xứ Phùng sinh. Nếu k ần có Chính Diệu ở đó sanh ïi nếu……_

**Kết luận:** Đã xác nhận bằng ảnh: TH tr.72 mục 1, 4, 7, 12, 21, 22 và TH tr.74 mục 7 ('Nhật, Nguyệt tàn hung ... hãm tại Mệnh mà không có cứu tinh, hoặc hãm mà gặp sát tinh') cùng đoạn 'cứu giải bằng Tam hóa hội' (chỉ cho Mệnh ở Bại/Tuyệt địa). TH tr.72 mục 12 là 'Tam Hoá liên châu' (ba cung liền), khác Tam kỳ gia hội. Câu trích của ảnh được ghi nguyên văn kể cả lỗi in ('hên châu', 'Khao'). Quy tắc dựa vào câu chỉ có trong ảnh không bao giờ được xếp `doi_chieu_truc_tiep`.

*Đang triển khai:* TH tr.72/tr.74: `anh_doc_ro` hoặc `van_ban`; không còn trang `chua_du_nguon` vì chữ.

#### R11 — Cơ chế: 2 yếu tố tăng thế = thành thượng; phản chứng hạ một bậc; không cộng điểm

*Câu hỏi:* Có trang nào định nghĩa ngưỡng hay mức hạ?
*Phân loại:* **nguồn chưa đủ** · *Trạng thái:* mo (cần chuyên gia)


**Kết luận:** Không trang nào của ba sách nêu số yếu tố hay số bậc; TH tr.76-77 chỉ phân hạng (phi thường / thượng / trung / hạ) bằng 'hội cát tinh đủ bậc'. Đây là quy ước thiết kế và được hiển thị như vậy.

*Đang triển khai:* 2 yếu tố, hạ một bậc, không cộng điểm.

## 2. Tứ Hóa: Nhâm-Khoa (và Canh)

| Nguồn | Nhâm: Lộc · Quyền · Khoa · Kỵ | Canh: Lộc · Quyền · Khoa · Kỵ | Ghi chú |
|---|---|---|---|
| Tử Vi Khảo Luận (Hoàng Thường – Hàm Chương) | Thiên Lương · Tử Vi · Tả Phụ · Vũ Khúc | Thái Dương · Vũ Khúc · Thiên Đồng · Thái Âm | bảng tr.36 in nhầm Tân-Lộc là Thiên Cơ; phần diễn giải tr.196 ghi Cự Môn (dùng Cự Môn) |
| Tử Vi Thực Hành (Dịch Lý Huyền Cơ) | Thiên Lương · Tử Vi · Thiên Phủ · Vũ Khúc | Thái Dương · Vũ Khúc · Thiên Đồng · Thái Âm | TH in Thiên Phủ ở CẢ câu thơ lẫn văn xuôi: không thể coi là lỗi chính tả một chỗ |
| 紫微斗數全書 bản số hóa (zh.wikisource.org/wiki/紫微斗數全書/卷二) — NGUỒN NGOÀI, không thuộc ba sách của dự án | Thiên Lương · Tử Vi · Thiên Phủ · Vũ Khúc | Thái Dương · Vũ Khúc · Thái Âm · Thiên Đồng | khác KL ở Canh (Khoa Thái Âm, Kỵ Thiên Đồng) và Nhâm (Khoa Thiên Phủ). zh.wikipedia/紫微斗數 cũng ghi hai biến thể ở đúng hai hàng này, nên đây là khác biệt giữa các văn bản truyền thống, không phải lỗi một cuốn |

Độ nhạy (oracle, 16.704 lá số của hai năm Canh và hai năm Nhâm): đổi bảng Canh **không** đổi trạng thái biến thể nào; đổi Nhâm-Khoa sang Thiên Phủ đổi NHAT_LE_TRUNG_THIEN@kl_52_85: 32, SAT_PHA_LIEM_THAM@th_76_77: 408 lá số. Bảng riêng từng nguồn: `engine/data/experimental/tu_hoa_tables.json`. **Cơ chế lựa chọn đề xuất (chưa nối):** tham số `tu_hoa_table` = `KL` (mặc định hiện tại) | `TH` | `TT_WS`; kết quả luôn kèm nhãn nguồn và cảnh báo khi hai bảng cho kết quả khác nhau; không bao giờ đổi âm thầm.

## 3. Độ nhạy của hai breaker có tỷ lệ phá cao

### 3.1 Cơ Nguyệt Đồng Lương — TT tr.24 (lõi đúng ở 14,688 lá số). Tỷ lệ bị phá theo phạm vi và cách đọc liệt kê

| Phạm vi | một trong ba (Không, Kiếp, Kỵ) — đang dùng | cặp Không-Kiếp hoặc Kỵ | ít nhất hai trong ba | đủ cả ba |
|---|---|---|---|---|
| đồng cung | 32.2% | 18.5% | 2.9% | 0.0% |
| đối cung | 21.6% | 5.7% | 0.8% | 0.0% |
| hai tam hợp | 57.7% | 35.5% | 11.1% | 0.0% |
| hội chiếu (đối + tam hợp) | 65.6% | 47.9% | 21.3% | 4.3% |
| tam phương tứ chính | 82.1% | 67.1% | 35.0% | 9.2% |

Câu của TT: 'Mệnh thân và các cung tam hợp xung chiếu có đủ bốn sao ... Gặp Kiếp Không Hoá Kị xuống hạ cách'. Phạm vi tam phương có căn cứ vì chính câu đã nêu 'tam hợp xung chiếu'; nhưng 'gặp' có thể chỉ Mệnh/Thân, và liệt kê ba sao có thể đòi đủ ba. Mọi ô trong bảng đều có chỗ dựa trong câu; ô nào cũng không được chọn.

### 3.2 Khôi Việt giáp Mệnh — KL tr.62 mục 4 (lõi đúng ở 2,784 lá số). Tỷ lệ phá theo phạm vi / tập sát tinh / ngưỡng

| Phạm vi · tập sát tinh | ≥1 | ≥2 | ≥3 |
|---|---|---|---|
| đồng cung · sáu sát tinh | 31.2% | 2.1% | 0.0% |
| đối cung · sáu sát tinh | 64.6% | 18.8% | 0.0% |
| hội chiếu (đối + tam hợp) · sáu sát tinh | 83.3% | 62.5% | 35.4% |
| tam phương tứ chính · sáu sát tinh | 91.7% | 68.8% | 41.7% |
| đồng cung · Tứ sát (Kình Đà Hỏa Linh) | 16.7% | 0.0% | 0.0% |
| đối cung · Tứ sát (Kình Đà Hỏa Linh) | 58.3% | 8.3% | 0.0% |
| hội chiếu (đối + tam hợp) · Tứ sát (Kình Đà Hỏa Linh) | 75.0% | 50.0% | 20.8% |
| tam phương tứ chính · Tứ sát (Kình Đà Hỏa Linh) | 83.3% | 50.0% | 20.8% |
| đồng cung · Không Kiếp | 16.7% | 0.0% | 0.0% |
| đối cung · Không Kiếp | 16.7% | 0.0% | 0.0% |
| hội chiếu (đối + tam hợp) · Không Kiếp | 33.3% | 16.7% | 0.0% |
| tam phương tứ chính · Không Kiếp | 50.0% | 16.7% | 0.0% |

Điều quan trọng: câu KL tr.62 mục 4 mô tả 'Cung mệnh CÓ Khôi Việt lại bị sát tinh hội chiếu', không phải Khôi Việt *giáp* Mệnh. Trên cấu trúc đúng như sách mô tả (Khôi Việt cùng trong tam phương, 22,272 lá số) 'ít nhất một sát tinh hội chiếu' vẫn đúng ở 83.1% lá số. Nghĩa là tần suất cao do **ngưỡng một sát tinh**, không do việc áp sang cấu trúc giáp. Nhưng việc áp sang cấu trúc giáp là một suy diễn riêng nên quy tắc bị đánh `chua_du_nguon`.

### 3.3 Sát Phá Liêm Tham — TH tr.77 'nhiều sát tinh' (lõi đúng ở 29,328 lá số)

| Ngưỡng | không Kỵ | kèm Kỵ |
|---|---|---|
| ≥1 sát tinh | 86.1% | 17.6% |
| ≥2 sát tinh | 61.8% | 11.6% |
| ≥3 sát tinh | 33.8% | 5.3% |
| ≥4 sát tinh | 13.8% | 1.6% |

Các tỷ lệ này là tần suất toán học của điều kiện trong mô hình, không phải độ đúng của sách. Việc điều kiện phá hầu như luôn đúng nghĩa là nó không phân biệt được lá số tốt/xấu; KL tr.199-200 còn cho Khoa, Tuần Triệt làm 'hung tinh lép vế', tức sát tinh không phá tuyệt đối.

## 4. Đọc lại toàn đoạn: phát hiện và hiệu chỉnh audit

Phase 6 chỉ kiểm câu trích có chứa từ khoá. Phase 7 đọc cả đoạn quanh mỗi câu (ngữ cảnh lưu trong dossier). Kết quả:

**Sai/yếu của audit (đã sửa trong dữ liệu):**

- Mười dòng audit có trang nói về **cấu trúc lân cận** (`structure_fit = khac_cau_truc`), nay chỉ được xếp `lien_quan`: Khôi Việt giáp Mệnh (3 dòng; KL tr.62 nói Khôi Việt *ở* Mệnh), Tam kỳ gia hội Hóa ở bản cung (TH tr.72 mục 12 là *Tam Hóa liên châu*, ba cung liền), Tả Hữu của Tử Phủ đồng cung (KL tr.49 nói Tử Vi), cát tinh của Sát Phá Liêm Tham (danh sách TH tr.76 là của Thượng cách), Tả Hữu và Khoa Quyền Lộc của Nhật Nguyệt tịnh minh.
- Ba dòng Tử Phủ Vũ Tướng dựa vào TH tr.115-116 là **đại tiểu hạn**, không phải bản cách (`khac_ngu_canh`).
- Hai dòng Kỵ/Thái Dương dẫn câu 'Tuần Triệt' thay vì câu 'ghét Kỵ'; một dòng Cơ Nguyệt Đồng Lương dẫn nhầm câu về Sát Phá Tham — đã thay (Phase 6).
- Trang TH tr.72, tr.74: đã đọc ảnh; câu ghi nguyên văn kể cả lỗi in của sách; TH tr.74 mục 7 máy kiểm được.

**Đoạn có ích mà audit trước bỏ sót (chưa đưa vào biến thể; đề xuất Phase 8):**

- TT tr.22: 'Tử Vi Thiên Phủ toàn y Phụ Bật chi công' — nguồn đúng cấu trúc cho yếu tố tăng thế Tả Hữu của Tử Phủ đồng cung.
- KL tr.96: 'Nếu Thiên phủ đi với Tử vi, Xương Khúc, Hóa khoa, Thiên việt, Thiên khôi thì rất mạnh' — nguồn cho tăng thế Xương Khúc/Khôi Việt của Tử Phủ.
- TT tr.22: 'Tử Phủ đồng cung vô sát tấu, **Giáp nhân** hưởng phúc chung thân': mệnh đề chỉ cho tuổi Giáp; biến thể `tt_22` bỏ điều kiện này.
- KL tr.85: 'Thái dương sợ: Kình, Đà, Không, Kiếp ... **cần Tuần Triệt cứu giải**' và KL tr.106: 'Cự môn hãm địa cần có Hóa khoa cứu giải' — hai chỗ sách nói trực tiếp sao cứu cho MỘT SAO; chưa phải cứu cho cả cách, nên vẫn không có sao cứu trong biến thể.
- TT tr.142: 'Khoa, Quyền lộc củng (**Chiếu thủ** có cả ba)' — củng cố cách đọc 'hội' = Mệnh cùng các cung chiếu cho Tam Hóa.
- KL tr.44 có mục 7 'Tam hoá liên châu' lặp nguyên định nghĩa của mục 6 Thạch trung ẩn ngọc (nghi lỗi in của sách).

**Hai lá số KL tr.221 không khớp (Hạng Võ, Mậu Tý) — kiểm lại:** KL tr.221 (ảnh đã đọc) là phần *loại hình*: 'may thì làm quan, xui thì làm công chức ba cọc ba đồng', 'hội Tả Hữu Quang Quí, Thiên quan, Thiên phúc → bác sĩ danh tiếng', 'hội Khoa Quyền Lộc, Khôi Việt, Xương Khúc → giáo sư danh tiếng'; **không nêu yếu tố phá**. Việc sách coi hai lá số là thất bại nằm ở phần luận cung (tr.238, tr.246): Hạng Võ — Tài có Đồng Lương ngộ Triệt và Địa Kiếp, Quan có Thái Âm ngộ Tuần, Di có Cự Kỵ; Mậu Tý — Cơ Hóa Kỵ gặp Hỏa Linh ở Tài. Oracle xác nhận từng chi tiết đó trên lá số dựng lại (Triệt và Địa Kiếp cùng cung Đồng Lương; Tuần cùng cung Thái Âm; Hỏa, Linh, Cơ Kỵ cùng cung Tý). Biến thể TT tr.24 chỉ bắt được qua Kiếp/Kỵ, **không** qua Tuần/Triệt (TT không liệt kê). Đây là khác biệt thể loại bên trong một cuốn, không phải mâu thuẫn quy tắc; và không có cơ sở để thêm Tuần/Triệt làm breaker chỉ để khớp hai lá số.

## 5. Kiểm lịch pháp độc lập

Tham chiếu: bảng *Gregorian-Lunar Calendar Conversion Table* của Hong Kong Observatory 1901–2100 (UTC+8; `calendar_reference_hko.json`) và thuật toán amlich (Hồ Ngọc Đức) viết lại độc lập (`oracle_calendar_independent.py`; không import `tvbt`, không dùng `sxtwl`), được xác nhận với HKO trước khi dùng cho UTC+7. Quét 47,789 ngày 1930-03-01 → 2060-12-31:

| So sánh | Số ngày khác nhau | Phân loại |
|---|---|---|
| sản xuất `cn` (sxtwl) ↔ HKO | 0 | **khớp hoàn toàn** |
| oracle amlich UTC+8 ↔ HKO | 4 | 4 ngày có trăng mới trong 40 phút sau nửa đêm (1939-04-19, 1947-03-22, 2009-03-26, 2054-05-07): giới hạn độ chính xác của oracle, sản xuất đúng |
| sản xuất `vn` ↔ oracle (UTC+8 trước 1968, UTC+7 từ 1968) | 13 | 3 ngày trên (cùng ngày borderline) + **2033-12-22..31: lỗi của sản xuất** |
| sản xuất `vn_south` ↔ oracle (UTC+8 đến 1975) | 13 | như trên |

**Lỗi lịch pháp thật (chỉ đường `vn`/`vn_south`):** 2033-12-22..31 thuộc tháng nhuận 11 (sxtwl, HKO, amlich và PyEphem đều đồng ý: tháng bắt đầu 12-22 không chứa trung khí; Đại Hàn rơi 2034-01-20), nhưng `lunar_vn.solar_to_lunar` cắt cấu trúc theo năm dương nên gán 12-22 là tháng 12 ngày 1 và 2034-01-20 lại là tháng 12 ngày 1 (hai tháng 12), cờ nhuận chỉ xuất hiện ở bên 2034. Tác động: Mệnh/Thân của người sinh trong 10 ngày này (đường lịch Việt) lệch một cung. Bằng chứng: test `xfail(strict)` + `test_the_2033_bug_is_confined_to_the_vietnamese_path_and_has_a_precise_signature`. Chưa sửa vì ngoài phạm vi và thuộc module của phiên khác; hướng sửa: tính cấu trúc theo cặp trung khí Đông chí liên tiếp thay vì `date.year`.

**Kiểm biên** (`test_calendar_independent.py`): giờ Tý (22:59, 23:00, 23:59, 00:00, 00:59, 01:00, 02:59, 03:00 × hai quy tắc Tý sớm/muộn); giao ngày; Tết 2024 với Tý 23:30 (hai quy tắc cho hai năm khác nhau: Giáp Thìn vs Quý Mão — lựa chọn trường phái, không phải lỗi); Tử Vi dùng năm âm lịch chứ không phải Lập Xuân (2024-02-05); mọi tháng nhuận 1950–2050 (≥35) ở hai phía ranh giới; ba quy tắc tháng nhuận `same_month/next_month/split_15` so với oracle; múi giờ không đổi ngày âm đọc từ lịch treo tường nhưng đổi UTC; khoảng không tồn tại do DST bị từ chối; Tết 1968 (Việt Nam 29-1 vs Trung Quốc 30-1, trăng mới 16:29 UTC) tái hiện quy tắc UTC+7 từ 1968.

**Phân tách ba tầng lỗi:**

| Tầng | Kiểm bằng | Kết quả |
|---|---|---|
| Lịch pháp (dương → âm → can chi) | HKO, amlich, PyEphem, quét 47.789 ngày, kiểm biên | 1 lỗi thật (2033-12-22..31, đường VN); phần còn lại khớp |
| An sao | oracle không import `tvbt` trên 116.928 lá số + công thức tra trang TH + ví dụ in trong sách + 6 lá số KL | 0 sai khác; hai chỗ sách khác nhau (Nhâm-Khoa, độ sáng Thân/Mùi) |
| Luận cách | 17 biến thể, audit từng quy tắc, độ nhạy cách đọc | không phải đúng/sai; xem ma trận mục 1 |

Giới hạn: không có bảng lịch Việt Nam xuất bản độc lập để tải về; phần Việt Nam dựa vào amlich + PyEphem và quy tắc UTC+8 trước 1968 (nguồn quy tắc: tài liệu mô-đun; VASTI 1/2019 theo chú thích của `calendar_core.py`, Wikipedia ghi 8/1967 — nguồn khác nhau); `vn_south` đến 1975 vẫn ghi là chưa xác minh.

## 6. Hồ sơ học thuật từng biến thể

Mỗi biến thể hiển thị được: trường phái và sách; điều kiện trích trực tiếp; điều kiện còn giả định; mức xác minh từng quy tắc; trường phái đưa kết luận khác (`formation_variant_dossier.json`).

| Biến thể | Trường phái · sách | trực tiếp | giả định | chưa đủ nguồn | Kích hoạt | Trường phái khác (mức khác biệt) |
|---|---|---|---|---|---|---|
| `TU_PHU_VU_TUONG@kl_132_193` | Tử Vi Khảo Luận · KL tr.132, KL tr.193, KL tr.222, TH tr.72 | 0 | 4 | 0 | 12.6% | th_115 (5,652/14,736) |
| `TU_PHU_VU_TUONG@th_115` | Tử Vi Thực Hành · TH tr.115, TH tr.72, TH tr.94, TH tr.95 | 0 | 4 | 0 | 12.6% | kl_132_193 (5,652/14,736) |
| `TU_PHU_DONG_CUNG@tt_22` | Tử Vi Đẩu Số Toàn Thư · KL tr.55, TH tr.72, TT tr.22 | 0 | 3 | 0 | 1.64% | kl_50 (658/1,920) |
| `TU_PHU_DONG_CUNG@kl_50` | Tử Vi Khảo Luận · KL tr.50, KL tr.55, TH tr.72 | 3 | 1 | 0 | 1.64% | tt_22 (658/1,920) |
| `CO_NGUYET_DONG_LUONG@tt_24` | Tử Vi Đẩu Số Toàn Thư · TH tr.77, TT tr.24 | 0 | 4 | 0 | 12.56% | kl_221 (14,352/14,688) |
| `CO_NGUYET_DONG_LUONG@kl_221` | Tử Vi Khảo Luận · KL tr.221, KL tr.51 | 0 | 3 | 0 | 12.56% | tt_24 (14,352/14,688) |
| `SAT_PHA_LIEM_THAM@th_76_77` | Tử Vi Thực Hành · TH tr.116, TH tr.72, TH tr.76, TH tr.77 | 0 | 1 | 2 | 25.08% | — |
| `NHAT_NGUYET_TINH_MINH@th_72` | Tử Vi Thực Hành · TH tr.72, TH tr.74, TT tr.142 | 1 | 2 | 0 | 2.63% | kl_53_68 (0/3,072) |
| `NHAT_NGUYET_TINH_MINH@kl_53_68` | Tử Vi Khảo Luận · KL tr.53, KL tr.56, KL tr.68 | 0 | 4 | 0 | 22.0% | th_72 (0/3,072) |
| `NHAT_LE_TRUNG_THIEN@kl_52_85` | Tử Vi Khảo Luận · KL tr.52, KL tr.85, TH tr.72 | 1 | 2 | 0 | 0.57% | — |
| `THACH_TRUNG_AN_NGOC@kl_44` | Tử Vi Khảo Luận · KL tr.44 | 1 | 0 | 0 | 1.48% | kl_58 (0/32); kl_106 (0/696) |
| `THACH_TRUNG_AN_NGOC@kl_58` | Tử Vi Khảo Luận · KL tr.58, TT tr.142 | 0 | 1 | 0 | 0.03% | kl_44 (0/32); kl_106 (0/32) |
| `THACH_TRUNG_AN_NGOC@kl_106` | Tử Vi Khảo Luận · KL tr.106, TH tr.43 | 0 | 1 | 0 | 0.6% | kl_44 (0/696); kl_58 (0/32) |
| `MA_DAU_DOI_KIEM@kl_64_xau` | Tử Vi Khảo Luận · KL tr.64 | 2 | 0 | 0 | 3.57% | kl_64_tot (94/4,176) |
| `MA_DAU_DOI_KIEM@kl_64_tot` | Tử Vi Khảo Luận · KL tr.64 | 1 | 1 | 0 | 3.57% | kl_64_xau (94/4,176) |
| `TAM_KY_GIA_HOI@kl_66` | Tử Vi Khảo Luận · KL tr.66, TT tr.142 | 0 | 2 | 0 | 3.46% | — |
| `KHOI_VIET_GIAP_MENH@kl_44_62` | Tử Vi Khảo Luận · KL tr.44, KL tr.62 | 1 | 0 | 2 | 2.38% | — |

## 7. Regression


## 8. Đề xuất ưu tiên cho Phase 8

1. **Quyết định của chuyên gia** cho R01–R05 (phạm vi 'hội/gặp/chiếu', liệt kê Kiếp-Không-Kị, ngưỡng sát tinh, Nhâm-Khoa). Cung cấp cho họ ma trận mục 1 và hai bảng mục 3; không triển khai gì trước đó.
2. **Sửa lỗi lịch 2033** trong `lunar_vn.solar_to_lunar` (module của phiên khác) rồi bỏ `xfail`; thêm quét độc lập hằng năm cho `vn` so với oracle.
3. **Thêm quy tắc có nguồn đúng cấu trúc** đã tìm thấy: TT tr.22 (Tả Hữu và mệnh đề tuổi Giáp), KL tr.96 (Xương Khúc, Khoa, Khôi Việt) cho Tử Phủ đồng cung — kèm quét lại 116.928 lá số.
4. **Quyết định số phận quy tắc `chua_du_nguon` của Khôi Việt giáp Mệnh** (loại khỏi bản có nguồn hay giữ như giả thuyết); không dựa vào tỷ lệ phá.
5. **Tham số `tu_hoa_table`** hiển thị trong kết quả (chỉ sau khi chuyên gia chọn mặc định).
6. **Tra bảng độ sáng đầy đủ** của Thái Dương ở Thân/Mùi từ nguồn thứ hai; hiện để trống.
7. **Tuần/Triệt**: viết quy tắc ưu tiên khi Tuần/Triệt vừa hại quý tinh vừa cứu hung tinh trong cùng lá số.
8. **Nhãn `verified` của `tu_hoa` trong `SCHOOL_PACK`** (tuvi.py) không còn đúng khi hai nguồn của chính dự án bất đồng ở Nhâm-Khoa; Phase 7 chỉ sửa ghi chú, chưa đổi nhãn (đổi nhãn đổi đầu ra API). Đề xuất `verified_with_variants` như `leap_month`, khi chủ module đồng ý.
9. **Đối chiếu sách giấy** cho những câu chỉ đọc được từ ảnh (`anh_doc_ro`), đặc biệt TH tr.72.
