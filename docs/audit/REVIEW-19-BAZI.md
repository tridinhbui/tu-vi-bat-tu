# REVIEW-19 W6 — Bát Tự: bớt tính toán, tổ hợp Thập thần, luận thực tế, phân xử tiền bạc (2026-10-23)

Điểm 6 của bản soát của chủ (origin/main ef62dc5): phần Bát Tự quá nặng tính toán (khoảng 2/3 câu là `tinh_toan`), thiếu luận thực tế và tổ hợp
Thập thần. Kế hoạch: `pasted-content-id-de4b-p0-soft-shore` bước W6. Quy tắc giữ nguyên: mỗi câu là dữ kiện lá số + một lời sách đã kiểm trang,
hoặc một quy ước có nhãn của hệ thống; không câu phổ thông; câu tổng hợp (basis `tong_hop`, quyết định của chủ 2026-10-23) chỉ ghép những điều
đã nói cho chính lá số. Văn trước / sau từng chương: [../examples/review-19-bazi-2002.md](../examples/review-19-bazi-2002.md),
[../examples/review-19-bazi-1971.md](../examples/review-19-bazi-1971.md).

## 1. Số đo (trước → sau)

Công cụ: `node tools/interpret/bazi_main_share.ts [corpus]` (mới; "phần chính" = các đoạn ngoài fold Đọc sâu / Số liệu). "Trước" = mã ef62dc5 trên
corpus1000 của commit ấy; "sau" = nhánh này, corpus đã làm tươi facts Bát Tự (`refresh_bazi_deep.py --corpus`).

| corpus1000 | Trước | Sau |
|---|---|---|
| Câu phần chính / lá | 87,0 | 73,6 |
| **Tỉ lệ `tinh_toan` ở phần chính** | **56,8 %** | **34,5 %** (trung vị 34,6 %, p90 38,0 %) |
| Lá có ít nhất một tổ hợp Thập thần được nói | 0 | 795 |
| Câu mở tổ hợp (mỗi câu kèm ≥ 1 lời sách có trang) | 0 | 1.329 |
| Câu cân hai mặt tiền bạc (`tong_hop`, nêu lý do) | 0 | 852 |
| Câu theo nhóm Thập thần mạnh / yếu (`BT_TVHK_G*`) | 0 | 2.723 |
| Câu "không lời nào xếp bên nào nặng hơn" và tương tự | 1.439 | **0** |
| Câu nhắc "nếu cách … đứng được" ở phần chính đại vận + lưu niên | 9.622 | 1.782 (một lần mỗi chương) |
| Số độ / % trong phần chính | có (sức nhật chủ, ngũ hành, Tài, Quan Sát) | **0** |

Theo chương (câu phần chính / lá, tỉ lệ `tinh_toan`):

| Chương | Trước | Sau |
|---|---|---|
| Nhật chủ | 8,0 · 26,1 % | 7,0 · 15,5 % |
| Ngũ hành | 2,0 · 50,0 % | 2,0 · 48,8 % |
| Sự nghiệp & tài lộc | 3,9 · 33,3 % | 8,9 · 15,1 % |
| Quan hệ | 9,6 · 42,7 % | 6,8 · 19,0 % |
| Đại vận | 30,8 · 71,5 % | 22,1 · 60,6 % |
| Cách cục | 8,4 · 54,7 % | 6,9 · 32,2 % |
| Lưu niên | 17,6 · 81,7 % | 10,8 · 46,5 % |
| Tổng kết | 6,7 · 0 % | 8,9 · 0 % |

Hai lá ví dụ (facts tính lại bằng engine của từng phía): 09/01/2002 04:30 nam 94 câu / 55,3 % → 79 câu / 31,6 %; 24/05/1971 10:30 nam 87 câu /
54,0 % → 69 câu / 33,3 %.

## 2. Đã làm

### 2.1 Tổ hợp Thập thần (task 1)

Tổ hợp tìm ở `engine/tvbt/bazi_deep/kin.py` `_patterns` (facts `bazi.k.pt`, `pt_pha`, `pt_cuu`; chi tiết `deep.kin.detail.patterns`), cùng quy ước
"đứng sát" với mọi luật kin (cùng một trụ, hoặc cùng hàng ở hai trụ liền nhau — quy ước của hệ thống, ghi ở note từng câu). Lời đọc là luật
`BT_TVHK_PT_*` (`tools/build_bazi_tvh_kin_pack.py`), câu in nguyên văn trong `quotes_tvh_kin.json`, đối chiếu với trang chép bởi
`test_pack_is_valid_and_every_rule_has_its_words`; vài luật đã có được gắn nhãn tổ hợp (`pt`) để nói cùng chỗ.

| Tổ hợp | Thành / bại / cứu | Lời sách (trang) | Vào việc |
|---|---|---|---|
| Thực Thần chế Sát | phá khi Thiên Ấn đứng sát Thực Thần | "Thực thần chế ngự sát là anh hùng áp đảo hàng vạn người" (TVH tr.535, trước là `Q03`); "… thì vợ vinh hiển, con hiển đạt" (tr.533, lá nam); "trong trụ không có kiêu thần là bậc quan quản việc giáo dục trong triều" (tr.533); "Sát có chế ngự mà không gặp kiêu …" (tr.535) | chức vụ, gia đạo, nghề |
| Sát Ấn tương sinh | Ấn đứng sát nhật chủ; phá khi Tài đứng sát Ấn | "Sát ấn tương sinh cho nhau thì có lợi cho công danh" (tr.551); "Sát ấn đều có là văn, võ song toàn" (tr.547) | danh, chức |
| Thương Quan sinh Tài | — | "Thương quan sinh tài thì sẽ tự nhiên giàu có" (tr.521); "… thương quan sinh ra tài thì nguồn của dồi dào" (tr.522); "Thương quan gặp tài là chức cao mà của nhiều" (tr.535, khi không có Chính Quan) | tiền, chức |
| **Thực Thần sinh Tài** (mới) | phá khi Thiên Ấn đứng sát Thực Thần | "Thương quan thực thần mừng được sinh tài, thì phú quý do trời sắp sặt" (tr.525); Tài nhiều thì "… không sang mà chỉ là trọc phú" (tr.521) | tiền |
| Tài Quan song mỹ | nhật chủ vượng; phá khi Thương Quan đứng sát Quan | "Thân vượng, tài quan tương sinh là phú quý song toàn" (TVH tr.165) | tiền, chức |
| Hợp Sát lưu Quan / Hợp Quan lưu Sát | Sát (Quan) hợp với can khác, chữ kia ở lại | "Quan tinh xen kẽ với thất sát, nếu hợp với thất sát là quý" / "nếu hợp mất quan tinh thì không tốt" (tr.533) | chức |
| Tài phá Ấn | cứu khi Quan Sát đứng sát Ấn (TTT tr.138 "Tài tinh phá Ấn, Quan có thể sinh Ấn") | "Tài là kị thần vượng, dụng thần là ấn. Tài phá ấn nên nghèo" (TVH tr.166); TTT tr.139, 142 (đã có) | tiền |
| Thương Quan kiến Quan | — | "Trong trụ thương quan gặp quan là vừa không có quan vừa không có của" (tr.541) | chức, tiền |
| Kiêu Thần đoạt Thực | — | "Thực thần gặp kiêu là tài vật hao tán" (tr.527, đã có) | tiền |
| Tỉ Kiếp đoạt Tài | nhật chủ vượng, Tài yếu; cứu khi có Quan Sát | "… huynh đệ tỉ kiếp chia nhau cướp đoạt nên mất tài" (tr.166); "Kiếp nặng tài nhẹ, quan có thể khắc kiếp … sang nhiều hơn giàu" (tr.167); TTT tr.138-139 (đã có) | tiền |

Văn (`src/interpret/prose/bazi_kin.ts`): đoạn "Về các tổ hợp Thập thần" trong Sự nghiệp & tài lộc — mỗi tổ hợp một câu tính toán (chữ nào, đứng ở
đâu, thành / bị phá / được đỡ bởi chữ nào), rồi từng lời sách theo việc (tiền bạc, danh và chức vụ, nghề, gia đạo). Lời đã có lên đây thì không nói
lại ở đoạn chủ đề của nó.

**Khác bản giao việc:** bản giao việc ghi Tài Quan song mỹ và hợp lưu "không có trang". Trang đã chép có lời phán cho cả hai (TVH tr.165, tr.533), nên
đã đưa vào văn với đúng câu ấy; tr.533 còn cho thấy Hợp Quan lưu Sát là thế *xấu* ("hợp mất quan tinh thì không tốt"), nên lời của nó mang dấu
nghịch (luật `BT_PT_HOP_QUAN_LUU_SAT` đổi effect sang `limit`). **Giữ ngoài văn:** Thương Quan phối Ấn (chưa có trang phán trong bộ đã chép; tr.551
"Thương quan gặp ấn và tài, dùng ấn, bỏ tài" cần cả Tài và việc chọn dụng), Chế Sát quá mức (TTT tr.91-92 chưa chép, ngưỡng 4 chữ là của hệ
thống), Quan Sát hỗn tạp (đã nói ở chương Cách cục qua luật TTT tr.84-91).

Lớp cấu trúc nháp (`patterns_defs.json`, `BT_PT_*` trong `pack_structure.json`): thêm `thuc_sinh_tai` (+ luật `BT_PT_THUC_SINH_TAI`), ghi trang cho
từng mục, lời `claims_vi.json` thay bằng câu có trang, nguồn `SRC_TVH_TOHOP`. Các mục này vẫn `draft` (vị trí "kề" của chúng chỉ xét thiên can và
có vị ngữ khí thế nháp); văn không đọc chúng.

### 2.2 Bớt tính toán ở phần chính (task 2)

- **Nhật chủ:** câu mở là mùa sinh + can điều hậu; bốn trụ và nạp âm vào fold *Số liệu · tứ trụ*. Sức vượng nhược nói bằng chữ ("giữ khoảng một phần
  tư sức của tám chữ, chưa tới mức bốn phần mười cần để tự đứng vững"), câu độ đầy đủ mở fold *Số liệu · sức vượng nhược*.
- **Ngũ hành:** phần chính là nhóm mạnh / yếu bằng chữ và các lời tính cách theo nhóm (2.3); đếm chữ, độ theo hành, độ theo nhóm vào *Số liệu ·
  ngũ hành theo độ*.
- **Sự nghiệp:** "Tài chiếm 29 % số độ" thành "khoảng một phần tư số độ"; câu O05 (Quan Sát vượng) bỏ số %; chỗ đứng từng nhóm vào *Số liệu · chỗ
  đứng của các nhóm*; ba lớp Tài (sức nhật chủ, cách, điều quyết định) vào Đọc sâu, đoạn chính kết bằng câu cân (2.4).
- **Quan hệ:** cung phối ngẫu tàng can gì và quan hệ hợp xung giữa các trụ vào *Số liệu*; sao anh chị em ở đâu vào *Số liệu* khi có lời sách về anh em.
- **Đại vận:** mở chương bằng một câu "nhóm nào ứng với việc gì" (Bát Tự Chân Tông tr.50-63) thay câu lặp "năm 2026 thuộc đại vận …". Mỗi chặng: tên
  chặng + hai thập thần + lời xếp vận tốt / xấu của cách trong **một** câu; trường sinh và tên thập thần từng chữ vào Đọc sâu của chặng; chỗ hai phía
  vênh nhau vào Đọc sâu, câu kết nói "hai phía vênh nhau, nên …"; câu kết nói chặng chạm việc gì ("chặng này chạm nhiều nhất tới tiền bạc (Tài) và
  công việc (Quan Sát)", `tong_hop`).
- **Cách cục:** câu "cách mới xác lập một phần" là trạng thái của hệ thống, basis `he_thong`; sao hung và sao không có lời chú vào *Số liệu · thần
  sát theo vị trí*.
- Trang báo cáo (`engine/web/js/report.js`): fold có tiêu đề "Số liệu · …" mang nhãn **Số liệu** (không phải "Đọc sâu"); basis `tong_hop` có nhãn
  "Tổng hợp của hệ thống" ở mục Phạm vi kiểm chứng.

### 2.3 Luận thực tế theo nhóm Thập thần (task 3)

19 luật `BT_TVHK_G01-G19` từ các trang đã chép, điều kiện là nhóm mạnh / yếu / không có (25 % / 12 % số độ — quy ước có nhãn) và sức nhật chủ:
tính cách (tr.520 "Tài lộ rõ là người hào phóng khảng khái", tr.548 "Ấn thụ nhiều là người thông minh", tr.547, tr.554), nghề và chức vụ (tr.530, 541,
542), tiền (tr.520-522, 166). Lời tính cách vào chương Ngũ hành sau câu nhóm mạnh / yếu; lời tiền và chức vào Sự nghiệp. Những cặp sách tự vênh được
giữ tách bằng điều kiện và ghi ở note (vd. tr.521 "thân suy không thắng tài là người vất vả" chỉ khi không có Tỉ Kiếp, vì tr.522 "Tài nhiều gặp tỉ
kiếp trợ giúp là nhà giàu thịnh vượng"); test `test_book_internal_conflicts_are_kept_apart` thêm 9 cặp.

### 2.4 Phân xử tiền bạc, bỏ lặp, Tổng kết xếp ưu tiên (task 4)

- **Thang cân (basis `tong_hop`, note ghi rõ):** khi lời về tiền đi hai chiều, xét trước sức nhật chủ (quy tắc 40 %) so với phần Tài: nhật chủ nhược mà
  Tài vượng → mặt nghịch nặng hơn; vượng mà Tài vượng → mặt thuận; vượng mà Tài mỏng → mặt nghịch; nếu hai thứ không kéo về phía nào thì xét vai của Tài
  trong bảng dụng thần theo cách (có điều kiện "nếu cách … đứng được"); còn lại "hai mặt cân nhau" kèm lý do. Thang dựa trên chính các lời TVH tr.166,
  520-521 ("thân nhược trong mệnh không nên gặp tài vượng", "Tài nhiều, thân nhược cần có ấn thụ" …). Chức vụ cân tương tự theo sức nhật chủ và Quan
  Sát (tr.533, 542). Câu nêu tối đa hai hiệu ứng mỗi mặt, không lặp chữ.
- **Bỏ lặp:** "Xét theo cách … (nếu cách này đứng được)" chỉ nói ở chặng đầu và năm đầu (mọi câu vẫn mang `trace.conditional = cach_partial`); lưu niên
  không nhắc lại lý do nhóm tốt / xấu mà đại vận đã nói; câu "việc, tiền và người" của năm gộp vào câu kết của năm; quan hệ năm × đại vận (chỉ vị trí)
  vào Đọc sâu; một lời lưu niên của 八字真宗 tr.64-65 lên phần chính của năm.
- **Tổng kết theo ưu tiên:** chẩn đoán → chặng đang đi và năm đang hỏi → tiền bạc (kết quả cân) → công việc → mốc chuyển → các chặng theo tuổi →
  điều kiện cách → chỗ nên dựa.

## 3. Test

- `src/interpret/test/bazi_w6.test.ts` (mới): trên lá 2002 và 1.000 lá — phần chính dưới 35 % `tinh_toan`, không số độ / % ở phần chính, mỗi câu tổ hợp
  có lời sách verified theo sau, không tổ hợp không trang, không câu "không lời nào xếp…", câu cân có lý do và nhãn, điều kiện cách một lần mỗi chương,
  thứ tự Tổng kết.
- `bazi_reconcile.test.ts`: kiểm "nếu cách đứng được" chuyển sang "một lần mỗi chương + trace mọi câu"; năm 2027 × Mậu Tuất tìm ở cả Đọc sâu của năm;
  basis `tong_hop` hợp lệ.
- `tools/interpret/bazi_depth.ts` (Track C "≥ 2 câu có nguồn mỗi đại vận"): đếm theo chặng (đoạn chính + Đọc sâu của nó).
- Python: `test_bazi_deep_kin.py` (chủ đề `character`, 9 cặp vênh mới), các test cấu trúc giữ nguyên.

## 4. Còn mở

- Đại vận vẫn 60 % `tinh_toan` ở phần chính: nội dung chính của một chặng là bảng dụng thần theo cách và bảng điều hậu (TVH tr.378-396), mà cách
  mới "xác lập một phần" nên câu ấy không thể là câu sách. Các lời "hành đến vận …" của TVH tr.519-556 (khoảng 170 dòng TIMING) chưa mã hóa — đó là chỗ
  có thể thêm luận thực tế cho từng chặng.
- Biên của mục tiêu mỏng (34,5 %): thêm câu tính toán ở phần chính sẽ đẩy lên trên 35 %; test corpus chặn việc ấy.
- Lớp cấu trúc nháp `patterns.py` dùng "kề" chỉ trên thiên can, khác quy ước kin; hai lớp không mâu thuẫn trên văn vì văn chỉ đọc lớp kin, nhưng
  trang `/api/bazi-structure` vẫn báo tổ hợp theo lớp nháp.
- Thang cân tiền bạc / chức vụ là quy ước của hệ thống (nhãn `tong_hop`), chưa được người đọc chuyên môn duyệt.
