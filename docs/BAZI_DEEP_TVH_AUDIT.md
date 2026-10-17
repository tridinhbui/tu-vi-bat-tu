# Kiểm toán Điều Hậu và Dụng Thần theo Thiệu Vĩ Hoa (tr.386–399)

Báo cáo do `tools/bazi_deep_tvh_audit.py` sinh ra; mọi con số được tính lại từ oracle độc lập và từ engine hiện hành. Trạng thái dưới đây chỉ nói rằng *bản cài khớp với những gì sách in*, không nói rằng học thuyết đó đã được kiểm chứng. Chính tác giả viết ở tr.388 rằng bảng điều hậu là do một độc giả tặng và ông không biết nó lấy từ sách nào.

## 1. Oracle độc lập và lỗi đã bắt được

- `engine/tests/golden/tvh_dieuhau_blind.json`: bảng tr.389–390 và chú thích tr.391–396 do một lượt chép **mù** khác thực hiện từ ảnh trang (không xem dữ liệu của engine), rồi so với engine.
- Bảng 120 ô: **120/120 khớp**. Chú thích: lượt chép mù và engine khớp 117/120; 3 ô lệch được đối chiếu lại với ảnh trang:
  - Thìn/Ất (tr.391): engine data had a transcription error (sách in 'quý, bính, mậu'); engine fixed.
  - Mùi/Tân (tr.395): blind pass misordered; sách in 'nhâm, canh, giáp'; engine data correct.
  - Sửu/Quý (tr.397): blind pass was given pp.391-396 only; entry is the first line of p.397 ('bính, đinh').
- Kết quả thực: oracle độc lập **bắt được một lỗi chép của chính engine** (Ất tháng Thìn: sách in `quý, bính, mậu`, engine cũ có `bính, quý, mậu`). Đã sửa và có test ghim.
- Giới hạn: cả hai lượt chép đều do mô hình thực hiện, chưa có người đọc kiểm. Hai lượt độc lập cùng khớp làm giảm rủi ro chép sai, không loại bỏ nó.

## 2. Chín ô bảng và chú thích không khớp

Phân loại 120 ô: **6 ô giống hệt** (cùng tập và cùng thứ tự), **105 ô cùng tập can nhưng khác thứ tự in**, **9 ô khác tập can** (5 thay thế, 3 chú thích thêm, 1 bảng thêm).

- **Sai tập can** (9 ô, bảng dưới) là mâu thuẫn thật của sách: hai nơi nêu hai tập can khác nhau.
- **Khác thứ tự** (105 ô) không phải lỗi dữ liệu: bảng tr.389–390 là 'bảng dụng thần dự bị' liệt kê tập can, thứ tự in trong ô không mang nghĩa ưu tiên; ưu tiên chỉ có ở chú thích tr.391–396. Vì vậy thứ tự ưu tiên của engine lấy hoàn toàn từ chú thích, và test khẳng định thứ tự in của bảng không phải thứ tự ưu tiên.
- Can đứng đầu chú thích luôn nằm trong bảng ở cả 120 ô: True, nên can chủ không bao giờ nằm trong vùng xung đột.

| Can ngày | Tháng | Bảng (tr.389–390) | Chú thích (tr.391–396) | Engine (thứ tự) | Loại lệch | Nguyên nhân | Hướng xử lý |
|---|---|---|---|---|---|---|---|
| Đinh | Thìn | Canh Giáp | Giáp Canh Mậu | Giáp Canh (chủ: Giáp) | sai **tập can** (note_adds) | chú thích thêm một can mà bảng không có | giữ tập can của bảng; can chỉ có trong chú thích không được thăng cấp; báo `book_internal_conflict` |
| Nhâm | Thìn | Canh Giáp | Giáp Canh Bính | Giáp Canh (chủ: Giáp) | sai **tập can** (note_adds) | chú thích thêm một can mà bảng không có | giữ tập can của bảng; can chỉ có trong chú thích không được thăng cấp; báo `book_internal_conflict` |
| Bính | Ngọ | Quý Nhâm | Nhâm Canh | Nhâm Quý (chủ: Nhâm) | sai **tập can** (swap) | sách tự mâu thuẫn: bảng và chú thích thay một can bằng can khác | giữ tập can của bảng; can chỉ có trong chú thích không được đưa lên; can chỉ có trong bảng xếp sau các can có trong chú thích; báo `book_internal_conflict` |
| Mậu | Ngọ | Canh Nhâm Bính | Nhâm Giáp Bính | Nhâm Bính Canh (chủ: Nhâm) | sai **tập can** (swap) | sách tự mâu thuẫn: bảng và chú thích thay một can bằng can khác | giữ tập can của bảng; can chỉ có trong chú thích không được đưa lên; can chỉ có trong bảng xếp sau các can có trong chú thích; báo `book_internal_conflict` |
| Quý | Ngọ | Nhâm Canh Quý | Canh Tân Quý | Canh Quý Nhâm (chủ: Canh) | sai **tập can** (swap) | sách tự mâu thuẫn: bảng và chú thích thay một can bằng can khác | giữ tập can của bảng; can chỉ có trong chú thích không được đưa lên; can chỉ có trong bảng xếp sau các can có trong chú thích; báo `book_internal_conflict` |
| Quý | Mùi | Tân Canh Nhâm Quý | Canh Tân Quý | Canh Tân Quý Nhâm (chủ: Canh) | sai **tập can** (table_adds) | bảng có một can mà chú thích bỏ qua | giữ tập can của bảng; can chỉ có trong bảng xếp cuối; báo `book_internal_conflict` |
| Bính | Thân | Quý Nhâm | Nhâm Mậu | Nhâm Quý (chủ: Nhâm) | sai **tập can** (swap) | sách tự mâu thuẫn: bảng và chú thích thay một can bằng can khác | giữ tập can của bảng; can chỉ có trong chú thích không được đưa lên; can chỉ có trong bảng xếp sau các can có trong chú thích; báo `book_internal_conflict` |
| Tân | Thân | Giáp Nhâm Canh | Nhâm Giáp Mậu | Nhâm Giáp Canh (chủ: Nhâm) | sai **tập can** (swap) | sách tự mâu thuẫn: bảng và chú thích thay một can bằng can khác | giữ tập can của bảng; can chỉ có trong chú thích không được đưa lên; can chỉ có trong bảng xếp sau các can có trong chú thích; báo `book_internal_conflict` |
| Tân | Dậu | Giáp Nhâm | Nhâm Giáp Đinh | Nhâm Giáp (chủ: Nhâm) | sai **tập can** (note_adds) | chú thích thêm một can mà bảng không có | giữ tập can của bảng; can chỉ có trong chú thích không được thăng cấp; báo `book_internal_conflict` |

Kết luận: 9 ô này là mâu thuẫn **trong nội bộ sách**, không phải lỗi chép (đã đối chiếu hai lượt chép). Engine không chọn bên nào làm đúng; nó giữ bảng làm tập can, không đưa can chỉ có ở chú thích lên, và gắn cờ cho người dùng. Can chủ không bị ảnh hưởng ở cả 9 ô.

## 3. Ba ví dụ chọn dụng thần (tr.397–399) và năm ví dụ điều hậu (tr.387–388)

### p397_vd1 (tr.397): Nhâm Thìn / Tân Hợi / Mậu Tuất / Bính Thìn

- Dữ kiện đầu vào: lá số trên; sách in thập thần và tàng can, test đối chiếu cả hai với engine (khớp).
- Bước 1, vượng/nhược: sách đọc **vượng** (định tính: 3 chi thổ + Bính hỏa trên giờ sinh ngày; sách nói 'thân cũng thiên vượng'). Quy tắc 40% trên điểm TVH: phe mình = **0.5523** → vượng.
- Bước 2, các bước của sách: Mậu sinh tháng Hợi (tử địa) nhưng 3 chi là thổ và Bính hỏa trên giờ sinh ngày → kỵ thần là Thổ; Thổ nhiều mong gặp Mộc làm tơi xốp → lấy Mộc làm dụng thần; Tài tinh ở vượng địa, thân thiên vượng.
- Bước 3, engine `cach_cuc_tvh`: nhóm nhiều nhất **Ti** → dụng QuanSat (bảng cho thêm QuanSat ThucThuong).
- Engine `dieu_hau`: dụng QuanSat, hỷ An. `khuyet_hanh`: khong_ap_dung —.
- **Sách chọn:** Mộc (nhóm QuanSat).

### p398_vd2 (tr.398): Ất Mão / Bính Tuất / Quý Tỵ / Nhâm Tý

- Dữ kiện đầu vào: lá số trên; sách in thập thần và tàng can, test đối chiếu cả hai với engine (khớp).
- Bước 1, vượng/nhược: sách đọc **nhược** (định tính: 'thất lệnh, không có gốc, Mậu thổ nắm quyền'. Lưu ý: giờ Tý và tàng can Tân/Canh có mặt nên lời sách không tái lập được bằng quy tắc 40%). Quy tắc 40% trên điểm TVH: phe mình = **0.4185** → vượng.
- Bước 2, các bước của sách: Quý sinh tháng Tuất thất lệnh, Mậu thổ nắm quyền → thân nhược; phải dùng Tân kim cấp nguồn cho thủy; Tứ trụ thiếu kim nên lấy kim làm dụng thần; kỵ thần là Thổ; tỉ kiếp Nhâm Quý thủy trợ thân là có lợi.
- Bước 3, engine `cach_cuc_tvh`: **hai cách đọc** (trong biên heuristic ±0.03); vượng: nhóm nhiều nhất Ti, dụng QuanSat ThucThuong; nhược: nhóm nhiều nhất ThucThuong, dụng An.
- Engine `dieu_hau`: dụng An, hỷ ThucThuong Ti. `khuyet_hanh`: khong_ap_dung —.
- **Sách chọn:** Kim (nhóm An).

### p399_vd3 (tr.399): Canh Tuất / Bính Tuất / Tân Tỵ / Đinh Dậu

- Dữ kiện đầu vào: lá số trên; sách in thập thần và tàng can, test đối chiếu cả hai với engine (khớp).
- Bước 1, vượng/nhược: sách đọc **vượng** (định tính: Chính Ấn nắm lệnh, Chính Ấn năm trợ thân, giờ Dậu ngang vai; sách nói 'thân vượng, ấn vượng'). Quy tắc 40% trên điểm TVH: phe mình = **0.7373** → vượng.
- Bước 2, các bước của sách: Tân sinh tháng Tuất, Chính Ấn nắm lệnh, thân vượng, ấn vượng; Ngũ hành không đầy đủ, thiếu Mộc và Thủy; để cân bằng ngũ hành, chọn Thủy và Mộc làm dụng thần (không dùng bảng cách cục).
- Bước 3, engine `cach_cuc_tvh`: nhóm nhiều nhất **Ti** → dụng QuanSat (bảng cho thêm QuanSat Tai).
- Engine `dieu_hau`: dụng ThucThuong, hỷ Tai. `khuyet_hanh`: ap_dung Tai ThucThuong.
- **Sách chọn:** Thủy Mộc (nhóm ThucThuong Tai).

Kết quả đối chiếu:

| Ví dụ | Vượng/nhược | cach_cuc_tvh | dieu_hau | khuyet_hanh | Đánh giá |
|---|---|---|---|---|---|
| tr.397 vd1 | khớp (55,2% → vượng) | **khớp** (Quan Sát) | **khớp** | không áp dụng | 2 phương pháp tái lập kết luận của sách |
| tr.398 vd2 | **lệch**: 41,85% → vượng theo quy tắc 40%, sách nói nhược | hai cách đọc; cách đọc nhược cho Ấn **khớp** | **khớp** (Ấn dụng, Tỉ hỷ) | không áp dụng | sách không tái lập được bằng chính quy tắc 40%; engine không che điều này |
| tr.399 vd3 | khớp (73,7% → vượng) | **một phần**: bảng cho Quan Sát (+Tài), sách chọn Thủy+Mộc | **khớp** (Thủy rồi Mộc, đúng thứ tự) | **khớp** (thiếu Mộc, Thủy) | sách chọn theo cân bằng ngũ hành chứ không theo bảng cách cục của chính nó |

Năm ví dụ điều hậu của tr.387–388 (Dụng thần theo chú thích điều hậu):

| Ví dụ | Lá số | Sách lấy | Engine (can chủ → …) | Kết quả |
|---|---|---|---|---|
| p387_intro | Bính Thân / Canh Tý / Quý Sửu / Ất Mão | Bính (Tai) | Bính=Tai Tân=An | khớp can chủ |
| p387_vd1 | Đinh Mão / Canh Tuất / Kỷ Tỵ / Canh Ngọ | Đinh (An) | Giáp=QuanSat Bính=An Quý=Tai | một phần: nhóm của sách có trong ô nhưng không đứng đầu |
| p388_vd2 | Mậu Thìn / Giáp Dần / Đinh Mão / Kỷ Dậu | Tân (Tai) | Giáp=An Canh=Tai | một phần: nhóm của sách có trong ô nhưng không đứng đầu |
| p388_vd3 | Đinh Mão / Quý Sửu / Bính Thân / Mậu Tý | Ất (An) | Nhâm=QuanSat Giáp=An | một phần: nhóm của sách có trong ô nhưng không đứng đầu |
| p388_vd4 | Canh Dần / Mậu Dần / Giáp Tý / Bính Dần | Bính (ThucThuong) | Bính=ThucThuong Quý=An | khớp can chủ |

## 4. Ngưỡng 40%

**Nguồn gốc.** Quy tắc nằm ở `tvh_score.py` (`THRESHOLD`, `decide`) và đi vào `yongshen.cach_cuc_tvh` qua cờ `dm_strong`; bản thân `yongshen.py` không có hằng 0,40. Sách tr.355 nêu 40% tổng độ làm ngưỡng, kèm hai phép thử số học: 78 < 78,8 (40% của 197) → nhược; 115 > 87,2 (40% của 218) → vượng. Cả hai được test tái lập bằng `decide`.

**Phần của sách:** con số 40% và phép so sánh lớn hơn/nhỏ hơn. **Phần của hệ thống (heuristic, đã gắn nhãn trong output `threshold`):**
- Đúng 40% tính là vượng (sách không nói); nhãn `equality_choice`.
- Biên ±0.03 quanh 40% cho hai cách đọc (`tvh_margin`); nhãn `margin_src: he_thong (không phải của sách)`. Ví dụ 6 của sách (39,6%) nằm trong biên này nhưng sách đọc dứt khoát là nhược, nên output luôn ghi thêm `book_rule_reading` và cờ `follows_book_rule` cho từng cách đọc.

**Độ nhạy của ngưỡng** trên 55 lá số có nhãn (48 nhãn Nhật Chủ của Trích Thiên Tủy, 4 ví dụ tính điểm của Thiệu Vĩ Hoa, 3 ví dụ đang kiểm; một nhãn trong đó là vd2 mà quy tắc 40% không tái lập được):

| Ngưỡng | 0.30 | 0.34 | 0.36 | 0.38 | 0.39 | 0.40 | 0.41 | 0.42 | 0.44 | 0.46 | 0.50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Số lá số khớp nhãn | 46 | 47 | 49 | 49 | 51 | 51 | 51 | 52 | 51 | 50 | 51 |

Tại 40%: 51/55 (92.7%). Vùng 0,39–0,44 gần như phẳng (±1); dưới 0,36 xấu đi rõ. Vậy 40% nằm trên một cao nguyên, **không bị tinh chỉnh cho khớp dữ liệu**, và dữ liệu này cũng không đủ để bảo vệ riêng con số 40% so với 42%.

Số lá số trong 81 mệnh lệ rơi vào biên hai cách đọc theo độ rộng biên: ±0.0: 0, ±0.01: 0, ±0.02: 1, ±0.03: 2, ±0.05: 7. Ở mức mặc định chỉ 2/81 lá số bị tách đôi.

Kiểm thử ngay dưới/bằng/trên ngưỡng nằm ở `test_cach_cuc_tvh_just_below_at_and_above_the_threshold` (0,3999 / 0,40 / 0,4001 với biên 0,03 và 0) và `test_40_percent_decision_on_the_books_own_numbers_and_at_the_edge`.

## 5. Các phương pháp tách biệt

Mỗi phương pháp trong `yongshen.run` mang `meta` (nguồn, mức xác minh, điều kiện áp dụng, cơ sở khí thế, đã áp dụng hay chưa) và `trace` (các bước). `comparison` chỉ liệt kê đồng thuận và bất đồng kèm điều kiện áp dụng; `no_final_answer: true`, không có khóa điểm số hay thắng-thua và không có phép cộng điểm giữa các phương pháp (test kiểm tra tập khóa).

| Phương pháp | Mức xác minh | Nguồn | Điều kiện áp dụng |
|---|---|---|---|
| `phu_uc` | draft | he_thong (nguyên lý phù ức phổ thông; ngưỡng cấp độ khí thế là của hệ thống) | không có ngoại cách chân và khí thế không ở mức trung hòa |
| `dieu_hau` | partial | SRC_TVH_DIEUHAU tr.389-390 (tập can); SRC_TVH_DIEUHAU tr.391-396 (thứ tự); SRC_TTT_HANTHU tr.113-114 (hàn/noãn) | luôn tra được: mỗi (can ngày, tháng) có một ô. Việc gán can chính = Dụng, các can còn lại = Hỷ là quy ước của hệ thống; ngưỡng hàn/nhiệt là chỉ số thô của hệ thống |
| `cach_cuc` | draft | he_thong (bảng cách cục nháp); SRC_TTT_THUONGQUAN tr.93-94 (Thương Quan) | nội cách đứng đầu; Thương Quan dùng năm mẫu của Trích Thiên Tủy |
| `cach_cuc_tvh` | partial | SRC_TVH_DUNGTHAN tr.378-386 (bảng cách × vượng/nhược × nhóm nhiều nhất); SRC_TVH_DIEM tr.355 (ngưỡng 40%) | nội cách đứng đầu và có dòng trong bảng; 'nhóm nhiều nhất' lấy theo tổng điểm TVH; biên ±tvh_margin quanh 40% là ngưỡng hiển thị của hệ thống nên cho hai cách đọc |
| `thong_quan` | draft | he_thong (nguyên lý thông quan; ngưỡng war_share/bridge_min là của hệ thống) | có hai hành khắc nhau cùng ≥ war_share |
| `thuan_the` | partial | SRC_TTT_TONG tr.171-179 (vai trò các loại tòng); SRC_TTT_HOA tr.175-176 (hóa thần) | chỉ khi hệ thống/Trích Thiên Tủy nhận ngoại cách chân (tòng/hóa); ngưỡng hóa thần dư/thiếu là của hệ thống; không dùng cách đặc biệt của Thiệu Vĩ Hoa |
| `thuan_the_tvh` | partial | SRC_TVH_DUNGTHAN tr.381-386 | chỉ khi có cách đặc biệt chân theo Thiệu Vĩ Hoa (tòng tài/sát/nhi, chuyên vượng, hóa khí); các ngưỡng nhận diện là của hệ thống |
| `khuyet_hanh` | draft | SRC_TVH_DUNGTHAN tr.399 (ví dụ 3: ngũ hành thiếu mộc, thủy thì dụng mộc, thủy) | lá số thiếu hẳn một hành (kể cả tàng can). Sách chỉ có MỘT ví dụ, không phát biểu thành quy tắc chung |

Phương pháp mới trong đợt này: `khuyet_hanh` (căn cứ duy nhất là một ví dụ tr.399, nên draft) và `thuan_the_tvh` (tách khỏi `thuan_the`, xem mục 6).

## 6. Cách ly trường phái: phát hiện và sửa

**Phát hiện (đo trên 81 mệnh lệ, profile mặc định `hệ thống` so với `tvh_40`):** tên nội cách giống nhau 81/81, nhưng điểm TVH và ngoại cách TVH làm đổi kết quả của trường phái khác: trạng thái thành/bại của cách đổi ở 6 lá số, ngoại cách không-TVH đổi ở 7, dụng thần của `cach_cuc` đổi ở 19. Cơ chế chính: các ngoại cách do `tvh_cach.special` sinh ra được trộn vào cùng danh sách `geju.outer`, nên khi TVH nhận một 'Tòng … chân' thì `cach_cuc` thành *không xác định nội cách* và `phu_uc` bị loại, dù hệ thống không nhận ngoại cách đó (ví dụ `Quý Mão / Mậu Ngọ / Nhâm Dần / Bính Ngọ`). Cùng cách, `thuan_the` đọc cả hai trường phái tùy thứ tự.

**Sửa:** khi profile là `tvh_40`, `yongshen.run` tính lại phần của hệ thống từ khí thế và cách cục của chính hệ thống (`+he_thong_view`), và chỉ dùng điểm TVH, ngoại cách TVH cho `cach_cuc_tvh` và `thuan_the_tvh`. `phu_uc` vẫn dùng quyết định vượng/nhược của profile (đó là lựa chọn có chủ ý, được ghi ở `meta.strength_basis`) nhưng chỉ xét ngoại cách của hệ thống.

**Kiểm chứng:** trên 96 lá số (81 mệnh lệ + EX1–EX15), `cach_cuc` và `thuan_the` giống hệt nhau giữa hai profile (0 khác biệt); `phu_uc` giống hệt trên các lá số cùng mức khí thế (28/96). Hệ quả hiển thị: có thêm bất đồng được liệt kê (EX5 nay có `BT_ST_DISAGREE`, vì phù ức hệ thống không còn bị TVH loại).

## 7. Danh sách heuristic của hệ thống (không gán cho tác giả)

| Tham số | Giá trị | Dùng ở | Ghi chú |
|---|---|---|---|
| `tvh_margin` | 0.03 | cach_cuc_tvh, phu_uc (biên hai cách đọc) | hiển thị; không phải của sách |
| đúng 40% = vượng | ≥ | tvh_score.decide | sách chỉ nói lớn hơn/nhỏ hơn |
| `level_cuts` | (0.22, 0.36, 0.46, 0.54, 0.64, 0.78) | phu_uc, các mức khí thế | hệ thống; sách chỉ có phép 40% |
| `presence_share` | 0.05 | Thương Quan (5 cách) | 'có/không có' Tài, Quan, Ấn là ngưỡng hệ thống |
| `thuong_vuong` | 0.3 | Thương Quan (5 cách) | hệ thống |
| `war_share`, `bridge_min` | 0.2, 0.1 | thong_quan | cả phương pháp là draft |
| `hua_du_share` | 0.5 | thuan_the (hóa) | hệ thống |
| `tvh_no_help`, `tvh_tong_main` | 0.15, 0.35 | nhận diện tòng TVH | sách dùng lời 'không có/nhiều', số là của hệ thống |
| `chuyen_vuong_chars`, `chuyen_vuong_share` | 5, 0.6 | nhận diện chuyên vượng/hóa khí | hệ thống |
| nhóm 'nhiều nhất' | lớn nhất theo tổng điểm TVH | cach_cuc_tvh | cách đọc của sách; cắt đồng hạng là của hệ thống |
| vai trò Dụng/Hỷ trong điều hậu | can chủ = Dụng, còn lại = Hỷ | dieu_hau | quy ước hệ thống; sách chỉ xếp thứ tự can |
| chỉ số hàn/nhiệt | heat ≤ −1, ≥ 1,5 | dieu_hau.han_noan | hệ thống (nguyên tắc hàn/noãn theo Trích Thiên Tủy tr.113–114) |
| `khuyet_hanh` cả phương pháp | — | khuyet_hanh | một ví dụ tr.399, không phải quy tắc chung của sách |

## 8. Kết luận về trạng thái draft → verified

| Hạng mục | Trạng thái đề xuất | Lý do |
|---|---|---|
| Bảng điều hậu 120 ô (tập can) | `verified` (bản chép) | 120/120 khớp lượt chép mù; 9 ô mâu thuẫn nội bộ sách được gắn cờ, vẫn thuộc diện bản chép đúng |
| Thứ tự ưu tiên trong chú thích | `verified` (bản chép) cho can chủ ở 120 ô; thứ tự các can sau chủ `verified` ở 111 ô cùng tập | 117/120 khớp ngay, 3 ô đã đối chiếu ảnh; 9 ô lệch tập can có cờ |
| Học thuyết điều hậu | **không** nâng | tác giả nói không biết nguồn của bảng; 3/5 ví dụ minh họa của chính ông chỉ khớp một phần với thứ tự chú thích |
| Quy tắc 40% (tr.355) | `verified` cho con số và phép so sánh | tái lập hai phép thử số của sách; 51/55 lá số có nhãn |
| Đúng 40%, biên ±0,03, các ngưỡng ở mục 7 | `draft` | do hệ thống đặt |
| Bảng cách × vượng/nhược × nhóm nhiều (tr.378–386) | `partial` | bản chép đã đối chiếu; 1/3 ví dụ khớp hoàn toàn, 1 khớp theo cách đọc nhược, 1 khớp một phần: chưa đủ để nói 'đã xác minh đúng' |
| `phu_uc`, `cach_cuc` (hệ thống), `thong_quan`, `khuyet_hanh` | `draft` | không có nguồn đối chiếu hoặc nguồn chỉ là một ví dụ |
| `thuan_the`, `thuan_the_tvh` | `partial` | bảng vai trò đã đối chiếu, ngưỡng nhận diện là của hệ thống |

## 9. Những gì chưa thể xác minh

- Ví dụ 4 tr.399 (nữ) tiếp tục sang tr.400, ngoài phạm vi trang đã dựng ảnh; chưa dùng.
- Mệnh lệ trong sách có chỗ tự mâu thuẫn (vd2 tr.398: nói 'không có gốc' trong khi giờ Tý và tàng can Tân/Canh có mặt); không thể dùng làm oracle cho vượng/nhược.
- Thứ tự các can sau can chủ trong 9 ô lệch: sách mâu thuẫn, không có căn cứ để chọn.
- Cả hai lượt chép bảng đều do mô hình; chưa có người đọc kiểm ảnh trang.
- Giá trị dự báo của dụng thần/điều hậu: không được kiểm chứng ở đâu trong repo; mọi nhãn ở trên là về độ trung thực với văn bản.
- Phu tòng thê hóa, thê tòng phu hóa, uyên ương hợp hóa chưa hỗ trợ trong tính điểm; điểm TVH chưa áp cho các trụ lưu (đại vận, lưu niên).

## Phụ lục: đối chiếu cả 120 ô

Cột *Bảng* theo thứ tự in; *Chú thích* theo thứ tự ưu tiên (can đầu là chủ); *Engine* là thứ tự engine trả về. `≠` đánh dấu ô khác tập can.

| Tháng | Can ngày | Bảng | Chú thích | Engine | Khớp tập |
|---|---|---|---|---|---|
| Dần | Giáp | Quý Bính | Bính Quý | Bính Quý | có |
| Dần | Ất | Quý Bính | Bính Quý | Bính Quý | có |
| Dần | Bính | Canh Nhâm | Nhâm Canh | Nhâm Canh | có |
| Dần | Đinh | Canh Giáp | Giáp Canh | Giáp Canh | có |
| Dần | Mậu | Giáp Bính Quý | Bính Giáp Quý | Bính Giáp Quý | có |
| Dần | Kỷ | Canh Bính Giáp | Bính Canh Giáp | Bính Canh Giáp | có |
| Dần | Canh | Giáp Nhâm Mậu Bính Đinh | Mậu Giáp Bính Nhâm Đinh | Mậu Giáp Bính Nhâm Đinh | có |
| Dần | Tân | Nhâm Kỷ Canh | Kỷ Nhâm Canh | Kỷ Nhâm Canh | có |
| Dần | Nhâm | Bính Canh Mậu | Canh Bính Mậu | Canh Bính Mậu | có |
| Dần | Quý | Bính Tân | Tân Bính | Tân Bính | có |
| Mão | Giáp | Bính Đinh Canh Mậu Kỷ | Canh Bính Đinh Mậu Kỷ | Canh Bính Đinh Mậu Kỷ | có |
| Mão | Ất | Quý Bính | Bính Quý | Bính Quý | có |
| Mão | Bính | Kỷ Nhâm | Nhâm Kỷ | Nhâm Kỷ | có |
| Mão | Đinh | Giáp Canh | Canh Giáp | Canh Giáp | có |
| Mão | Mậu | Giáp Bính Quý | Bính Giáp Quý | Bính Giáp Quý | có |
| Mão | Kỷ | Quý Giáp Bính | Giáp Quý Bính | Giáp Quý Bính | có |
| Mão | Canh | Giáp Canh Đinh Bính | Đinh Giáp Bính Canh | Đinh Giáp Bính Canh | có |
| Mão | Tân | Giáp Nhâm | Nhâm Giáp | Nhâm Giáp | có |
| Mão | Nhâm | Tân Mậu Canh | Mậu Tân Canh | Mậu Tân Canh | có |
| Mão | Quý | Tân Canh | Canh Tân | Canh Tân | có |
| Thìn | Giáp | Đinh Canh Nhâm | Canh Đinh Nhâm | Canh Đinh Nhâm | có |
| Thìn | Ất | Bính Quý Mậu | Quý Bính Mậu | Quý Bính Mậu | có |
| Thìn | Bính | Giáp Nhâm | Nhâm Giáp | Nhâm Giáp | có |
| Thìn | Đinh | Canh Giáp | Giáp Canh Mậu | Giáp Canh | ≠ (note_adds) |
| Thìn | Mậu | Bính Giáp Quý | Giáp Bính Quý | Giáp Bính Quý | có |
| Thìn | Kỷ | Quý Bính Giáp | Bính Quý Giáp | Bính Quý Giáp | có |
| Thìn | Canh | Đinh Giáp Nhâm Quý | Giáp Đinh Nhâm Quý | Giáp Đinh Nhâm Quý | có |
| Thìn | Tân | Giáp Nhâm | Nhâm Giáp | Nhâm Giáp | có |
| Thìn | Nhâm | Canh Giáp | Giáp Canh Bính | Giáp Canh | ≠ (note_adds) |
| Thìn | Quý | Tân Bính Giáp | Bính Tân Giáp | Bính Tân Giáp | có |
| Tỵ | Giáp | Đinh Quý Canh | Quý Đinh Canh | Quý Đinh Canh | có |
| Tỵ | Ất | Quý | Quý | Quý | có |
| Tỵ | Bính | Canh Nhâm Quý | Nhâm Canh Quý | Nhâm Canh Quý | có |
| Tỵ | Đinh | Canh Giáp | Giáp Canh | Giáp Canh | có |
| Tỵ | Mậu | Bính Giáp Quý | Giáp Bính Quý | Giáp Bính Quý | có |
| Tỵ | Kỷ | Bính Quý | Quý Bính | Quý Bính | có |
| Tỵ | Canh | Mậu Nhâm Bính Đinh | Nhâm Bính Đinh Mậu | Nhâm Bính Đinh Mậu | có |
| Tỵ | Tân | Giáp Nhâm Quý | Nhâm Giáp Quý | Nhâm Giáp Quý | có |
| Tỵ | Nhâm | Tân Nhâm Canh Quý | Nhâm Tân Canh Quý | Nhâm Tân Canh Quý | có |
| Tỵ | Quý | Tân | Tân | Tân | có |
| Ngọ | Giáp | Đinh Quý Canh | Quý Đinh Canh | Quý Đinh Canh | có |
| Ngọ | Ất | Bính Quý | Quý Bính | Quý Bính | có |
| Ngọ | Bính | Quý Nhâm | Nhâm Canh | Nhâm Quý | ≠ (swap) |
| Ngọ | Đinh | Canh Nhâm Quý | Nhâm Canh Quý | Nhâm Canh Quý | có |
| Ngọ | Mậu | Canh Nhâm Bính | Nhâm Giáp Bính | Nhâm Bính Canh | ≠ (swap) |
| Ngọ | Kỷ | Bính Quý | Quý Bính | Quý Bính | có |
| Ngọ | Canh | Nhâm Quý | Nhâm Quý | Nhâm Quý | có |
| Ngọ | Tân | Kỷ Nhâm Quý | Nhâm Kỷ Quý | Nhâm Kỷ Quý | có |
| Ngọ | Nhâm | Canh Quý Tân | Quý Canh Tân | Quý Canh Tân | có |
| Ngọ | Quý | Nhâm Canh Quý | Canh Tân Quý | Canh Quý Nhâm | ≠ (swap) |
| Mùi | Giáp | Đinh Quý Canh | Quý Canh Đinh | Quý Canh Đinh | có |
| Mùi | Ất | Bính Quý | Quý Bính | Quý Bính | có |
| Mùi | Bính | Canh Nhâm | Nhâm Canh | Nhâm Canh | có |
| Mùi | Đinh | Nhâm Giáp Canh | Giáp Nhâm Canh | Giáp Nhâm Canh | có |
| Mùi | Mậu | Bính Quý Giáp | Quý Bính Giáp | Quý Bính Giáp | có |
| Mùi | Kỷ | Bính Quý | Quý Bính | Quý Bính | có |
| Mùi | Canh | Giáp Đinh | Đinh Giáp | Đinh Giáp | có |
| Mùi | Tân | Canh Nhâm Giáp | Nhâm Canh Giáp | Nhâm Canh Giáp | có |
| Mùi | Nhâm | Giáp Tân | Tân Giáp | Tân Giáp | có |
| Mùi | Quý | Tân Canh Nhâm Quý | Canh Tân Quý | Canh Tân Quý Nhâm | ≠ (table_adds) |
| Thân | Giáp | Đinh Canh Nhâm | Canh Đinh Nhâm | Canh Đinh Nhâm | có |
| Thân | Ất | Quý Bính Kỷ | Bính Quý Kỷ | Bính Quý Kỷ | có |
| Thân | Bính | Quý Nhâm | Nhâm Mậu | Nhâm Quý | ≠ (swap) |
| Thân | Đinh | Canh Giáp Bính Mậu | Giáp Canh Bính Mậu | Giáp Canh Bính Mậu | có |
| Thân | Mậu | Quý Bính Giáp | Bính Quý Giáp | Bính Quý Giáp | có |
| Thân | Kỷ | Quý Bính | Bính Quý | Bính Quý | có |
| Thân | Canh | Giáp Đinh | Đinh Giáp | Đinh Giáp | có |
| Thân | Tân | Giáp Nhâm Canh | Nhâm Giáp Mậu | Nhâm Giáp Canh | ≠ (swap) |
| Thân | Nhâm | Đinh Mậu | Mậu Đinh | Mậu Đinh | có |
| Thân | Quý | Đinh | Đinh | Đinh | có |
| Dậu | Giáp | Đinh Canh Bính | Canh Đinh Bính | Canh Đinh Bính | có |
| Dậu | Ất | Bính Quý Đinh | Quý Bính Đinh | Quý Bính Đinh | có |
| Dậu | Bính | Quý Nhâm | Nhâm Quý | Nhâm Quý | có |
| Dậu | Đinh | Canh Giáp Bính Mậu | Giáp Canh Bính Mậu | Giáp Canh Bính Mậu | có |
| Dậu | Mậu | Quý Bính | Bính Quý | Bính Quý | có |
| Dậu | Kỷ | Quý Bính | Bính Quý | Bính Quý | có |
| Dậu | Canh | Giáp Đinh Bính | Đinh Giáp Bính | Đinh Giáp Bính | có |
| Dậu | Tân | Giáp Nhâm | Nhâm Giáp Đinh | Nhâm Giáp | ≠ (note_adds) |
| Dậu | Nhâm | Canh Giáp | Giáp Canh | Giáp Canh | có |
| Dậu | Quý | Bính Tân | Tân Bính | Tân Bính | có |
| Tuất | Giáp | Giáp Đinh Canh Nhâm Quý | Canh Giáp Đinh Nhâm Quý | Canh Giáp Đinh Nhâm Quý | có |
| Tuất | Ất | Tân Quý | Quý Tân | Quý Tân | có |
| Tuất | Bính | Nhâm Giáp | Giáp Nhâm | Giáp Nhâm | có |
| Tuất | Đinh | Canh Giáp Mậu | Giáp Canh Mậu | Giáp Canh Mậu | có |
| Tuất | Mậu | Bính Giáp Quý | Giáp Bính Quý | Giáp Bính Quý | có |
| Tuất | Kỷ | Bính Giáp Quý | Giáp Bính Quý | Giáp Bính Quý | có |
| Tuất | Canh | Nhâm Giáp | Giáp Nhâm | Giáp Nhâm | có |
| Tuất | Tân | Giáp Nhâm | Nhâm Giáp | Nhâm Giáp | có |
| Tuất | Nhâm | Bính Giáp | Giáp Bính | Giáp Bính | có |
| Tuất | Quý | Giáp Tân Nhâm Quý | Tân Giáp Quý Nhâm | Tân Giáp Quý Nhâm | có |
| Hợi | Giáp | Đinh Bính Canh Mậu | Canh Đinh Bính Mậu | Canh Đinh Bính Mậu | có |
| Hợi | Ất | Mậu Bính | Bính Mậu | Bính Mậu | có |
| Hợi | Bính | Mậu Giáp Canh Nhâm | Giáp Mậu Canh Nhâm | Giáp Mậu Canh Nhâm | có |
| Hợi | Đinh | Canh Giáp | Giáp Canh | Giáp Canh | có |
| Hợi | Mậu | Bính Giáp | Giáp Bính | Giáp Bính | có |
| Hợi | Kỷ | Giáp Bính Mậu | Bính Giáp Mậu | Bính Giáp Mậu | có |
| Hợi | Canh | Bính Đinh | Đinh Bính | Đinh Bính | có |
| Hợi | Tân | Bính Nhâm | Nhâm Bính | Nhâm Bính | có |
| Hợi | Nhâm | Bính Mậu Canh | Mậu Bính Canh | Mậu Bính Canh | có |
| Hợi | Quý | Tân Canh Mậu Đinh | Canh Tân Mậu Đinh | Canh Tân Mậu Đinh | có |
| Tý | Giáp | Canh Đinh Bính | Đinh Canh Bính | Đinh Canh Bính | có |
| Tý | Ất | Bính | Bính | Bính | có |
| Tý | Bính | Mậu Nhâm Kỷ | Nhâm Mậu Kỷ | Nhâm Mậu Kỷ | có |
| Tý | Đinh | Canh Giáp | Giáp Canh | Giáp Canh | có |
| Tý | Mậu | Giáp Bính | Bính Giáp | Bính Giáp | có |
| Tý | Kỷ | Giáp Bính Mậu | Bính Giáp Mậu | Bính Giáp Mậu | có |
| Tý | Canh | Giáp Đinh Bính | Đinh Giáp Bính | Đinh Giáp Bính | có |
| Tý | Tân | Mậu Bính Nhâm Giáp | Bính Mậu Nhâm Giáp | Bính Mậu Nhâm Giáp | có |
| Tý | Nhâm | Bính Mậu | Mậu Bính | Mậu Bính | có |
| Tý | Quý | Tân Bính | Bính Tân | Bính Tân | có |
| Sửu | Giáp | Canh Đinh Bính | Đinh Canh Bính | Đinh Canh Bính | có |
| Sửu | Ất | Bính | Bính | Bính | có |
| Sửu | Bính | Giáp Nhâm | Nhâm Giáp | Nhâm Giáp | có |
| Sửu | Đinh | Canh Giáp | Giáp Canh | Giáp Canh | có |
| Sửu | Mậu | Giáp Bính | Bính Giáp | Bính Giáp | có |
| Sửu | Kỷ | Giáp Bính Mậu | Bính Giáp Mậu | Bính Giáp Mậu | có |
| Sửu | Canh | Đinh Bính Giáp | Bính Đinh Giáp | Bính Đinh Giáp | có |
| Sửu | Tân | Nhâm Bính Mậu Kỷ | Bính Mậu Nhâm Kỷ | Bính Mậu Nhâm Kỷ | có |
| Sửu | Nhâm | Đinh Bính Giáp | Bính Giáp Đinh | Bính Giáp Đinh | có |
| Sửu | Quý | Đinh Bính | Bính Đinh | Bính Đinh | có |
