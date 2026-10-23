# Bát Tự: Sự nghiệp & tài lộc, Quan hệ, Lưu niên theo sách (DEEP-BAZI-2, 2026-10-23)

Kế hoạch: `quirky-tinkering-rabin` P2 — Bát Tự. Audit trước đó: mọi luật verified đã bắn đều đã được nói; hai chương mỏng vì **sách chưa
được mã hóa**. Đợt này mã hóa các trang lục thân / tài / nghề / lưu niên, nói thêm các dữ kiện đã tính mà văn chưa nói, và nối từng năm với
tiền bạc, công việc, quan hệ. Không đổi engine tính lá số, không đổi giao diện.

## 1. Số đo trên corpus1000 (trước → sau)

Công cụ: `tools/interpret/bazi_deep_audit.ts <corpus>` (định nghĩa ở đầu file). "Trước" = main 6ba6a68, facts Bát Tự tính lại bằng engine
của commit ấy; "sau" = nhánh này, `corpus1000.json.gz` đã làm tươi facts Bát Tự (`tools/interpret/refresh_bazi_deep.py --corpus`).

| Chỉ số (trung bình / lá số) | Trước | Sau |
|---|---|---|
| Số từ | 3.410 | 3.989 |
| Đơn vị phân tích (câu sách / tính toán) | 99,4 | 122,4 |
| Từ trên một đơn vị | 34,3 | **32,6** (không tăng) |
| Kết luận / kết luận trơ | 21,7 / 11,8 | 20,3 / **9,9** |
| Tỉ lệ kết luận có câu nguồn đi kèm (1 − trơ / kết luận) | 45,6 % | **51,4 %** |
| Độ phủ cơ chế | 0,659 | **0,716** |
| Strip sim (khuôn sáo giữa các lá) | 0,331 | **0,313** |

Đơn vị theo chương (từ / đơn vị):

| Chương | Trước | Sau |
|---|---|---|
| Sự nghiệp & tài lộc | 2,3 (43,1) | **8,4** (34,4) |
| Quan hệ | 4,3 (27,0) | **12,8** (23,6) |
| Lưu niên (3 năm) | 19,8 (29,1) | **28,1** (27,7) |
| Nhật chủ, ngũ hành, đại vận, cách cục | không đổi | không đổi |

Lá số thiếu câu theo chủ đề (câu có nguồn — sách hoặc tính toán — mang từ khóa của chủ đề, trong chương tương ứng; tiền: "Tài / tiền / tài
vận / của cải / tài lộc", nghề: "nghề / công việc / chức vụ / sự nghiệp…", anh em: "anh em / anh chị em / huynh đệ"):

| Trên 1.000 lá | Trước | Sau |
|---|---|---|
| không có câu anh em (Quan hệ) | 317 | **2** |
| có ≤ 1 câu Tài (Sự nghiệp) | 536 | **9** |
| có ≤ 1 câu nghề (Sự nghiệp) | 939 | **25** |
| có ≤ 1 câu anh em (Quan hệ) | 784 | 227 |

Cổng: `bazi_reconcile` (không mâu thuẫn chưa giải thích, không "tài vận tốt" trơ — nay trên 1.000 lá với facts tươi: 0 vấn đề), `bazi_prose`,
`readable`, `engine` (parity), `test_bazi_reference_charts.py`, `test_bazi_deep_kin.py` đều xanh.

## 2. Đã làm

**Nguồn thô đã commit trước khi mã hóa** (`engine/data/bazi_deep/mined/`): 八字真宗 tr.50-60, 63-65, 73; Trích Thiên Tủy tr.128-148, 219-228
(lớp chữ của PDF, không sửa). Test `test_mined_pages_are_the_pdf_text_layer` so lại với PDF khi máy có file.

**Facts** (`engine/tvbt/bazi_deep/kin.py`, nối vào `facts.bazi.deep.kin` và `deep.years[].kin`): tính đúng các chữ sách tự định nghĩa, theo
cách ví dụ của chính sách dùng:
- *流入日主* (tr.50 điều kiện 1): Tài kề Quan, Quan kề Ấn, Ấn đứng ở chi ngày, can tháng hoặc can giờ; "kề" = cùng trụ hoặc cùng hàng hai trụ
  liền nhau (ví dụ 2 tr.58: can không sinh chi của trụ khác). Khớp ví dụ tr.50 (Mậu Thân…: chảy), tr.51 (Quý Hợi…: Tài vượng, không chảy),
  tr.53 ví dụ 3 (Sát chảy qua Ấn can tháng), tr.58 ví dụ 2 (không chảy).
- *有根*: chính / trung khí cùng hành ở chi của chính trụ hoặc trụ liền bên (ví dụ tr.51 gọi Mậu chỉ có dư khí trong Thân là "không gốc").
- *截脚 / 盖头, 墓 / 库* (tr.63: mộ ở trụ tháng, ngày; khố ở trụ năm, giờ), *胎身命* (tr.35-38), không vong theo trụ ngày.
- "vượng / nhược" của một nhóm: phần độ Thiệu Vĩ Hoa từ 25 % / dưới 12 % (Tỉ Kiếp không tính độ của chính nhật chủ) — **ngưỡng của hệ thống**,
  ghi ở note từng câu dựa vào nó.

**Luật** (`pack_zz_kin.json` 96 luật, `pack_ttt_kin.json` 51 luật; câu in nguyên văn trong `quotes_*_kin.json`, test đối chiếu từng câu với
trang đã chép; builder `tools/build_bazi_kin_pack.py`, `tools/build_bazi_ttt_kin_pack.py`):
- 八字真宗: tr.50 tài vận (21 mục + điều kiện cuối trang), tr.51-52 công việc (流入日主, trụ bên trái trụ Quan: lớn / nhỏ, nhóm nghề theo thập
  thần, nghề theo hành của can), tr.52-53 quan chức (7), tr.55 cha mẹ (3, bỏ mọi mục về thọ yểu), tr.57-58 hôn nhân (9), tr.64 anh em (7),
  tr.64-65 lưu niên (22).
- Trích Thiên Tủy Phần II: Hà Tri — giàu (tr.137, 6 thế "Tài khí thông môn hộ"), nghèo (tr.139, 7 thế "Tài bất chân"), quý (tr.138, 6 thế
  "Quan tinh hữu lý hội"), tiện (tr.142, 5); Phụ Mẫu (tr.133, 9); Huynh Đệ (tr.135, 10); Phu Thê lá số nam (tr.128-129, 7, không có lời khắc vợ);
  Địa Vị "Sát Nhận thần thanh" (tr.224). Các luật đọc "nhật chủ hỉ / kỵ X" lấy hỉ / kỵ từ bảng dụng thần và vận tốt xấu theo cách của Thiệu Vĩ Hoa
  (tr.378-386), nên câu mang điều kiện "nếu cách … đứng được" (trace.conditional `cach_partial`).

**Sửa tận gốc: nghề đọc ở trụ bên trái trụ Quan, không phải trụ giờ.** Tr.52 mục 6-7 "以官星左柱论 … 年柱的左柱为时柱"; ví dụ 1 tr.53 (Quan ở
chi tháng → đọc trụ năm, "劫财为自由业") và ví dụ 2 (Quan ở chi năm → đọc trụ giờ, "丙火印弱"). Luật cũ `BT_ZZ_DIRECT_HOUR_GROUP_*` đọc can giờ cho
mọi lá số: đã bỏ khỏi `pack_bazi_zz_direct.json`, thay bằng `BT_ZZK_OG_*` / `OS_*` / `O06*`; test `test_book_examples_left_pillar`. Quan ở nhiều
trụ: lấy trụ có Quan thấu can nếu chỉ một, còn lại không có lời; không có Quan thì lấy Tài (tr.51 mục 3). Mục 8 ghi "(tức hành của can trụ giờ)":
hệ thống đọc cùng trụ bên trái như mục 6-7 và hai ví dụ (ghi trong note). Các luật tài vận tr.50 cũ (`W_*`) và `O_QUAN_SAT_ROOT` (bỏ qua điều kiện
"chảy vào nhật chủ") cũng chuyển sang gói mới.

**Lá 2002: chỗ vênh tài vận được giải bằng chính điều kiện của sách.** Tài (Tân, Tân) chiếm 29 % số độ — vượng — nhưng ba chỗ sát nhật chủ (can
tháng Tân, chi ngày Sửu, can giờ Nhâm) không có Ấn, nên "Tài vượng mà chưa chảy vào nhật chủ: tài vận bình thường" (tr.50 điều kiện 2). Các
điểm cộng theo vị trí (Thiên Tài thấu có gốc, Tài ở mệnh cung) được nói là chưa đổi được mức chung; lớp sức nhật chủ (Thiệu Vĩ Hoa) nay *gặp*
lớp này thay vì "để ngỏ". Câu đã sửa ở `bazi_reconcile.test.ts` (owner review).

**Văn** (`src/interpret/prose/bazi_kin.ts`, khung `content/prose/bat_tu.json` → `kin`):
- Sự nghiệp & tài lộc: chỗ đứng của Tài / Quan Sát / Ấn / Thực Thương / Tỉ Kiếp theo trụ (dữ kiện đã tính, trước chưa nói), kết luận tài vận
  theo điều kiện của sách, công việc theo 流入日主, nghề theo trụ bên trái trụ Quan, một lời về chức vụ; Đọc sâu: vì sao (chảy) hay không chảy,
  từng chữ Tài (điểm cộng gom một câu, chịu điều kiện chung), giàu / nghèo theo Trích Thiên Tủy, nơi làm việc lớn / nhỏ, các lời quý / tiện.
- Quan hệ: sao phối ngẫu theo giới tính (nam Tài, nữ Quan — tr.57), sao phối ngẫu hợp nhật can, các lời hôn nhân; sao anh chị em (Tỉ Kiếp,
  không có thì Ấn — tr.63) và các lời anh em; Đọc sâu: sao cha / mẹ (tr.54-55), gốc gác theo năm tháng (Trích Thiên Tủy tr.133), sao con cái
  (tr.60, không đoán trai gái), thai nguyên / mệnh / thân cung nêu trong chính các câu dùng chúng.
- Lưu niên: mỗi năm một câu "việc, tiền và người" — hai thập thần của năm ứng với gì theo sách (Tài: tiền, và là sao vợ với nam; Quan: công việc,
  chức vụ, và là sao chồng với nữ; Ấn: học hành; Tỉ Kiếp: anh chị em; sao con cái theo tr.60); Đọc sâu: các lời tr.64-65 bắn trong năm, mỗi lời
  với điều kiện có tên chữ cụ thể; lời trùng điều kiện ở nhiều năm nói một lần, kèm các năm ("Trong năm 2026, 2027 và 2028, …"); lời xấu
  trong năm được kết là thuận thì nói là một mặt ("Dù nhìn chung năm … thuận, vẫn có một mặt cần giữ").
- Mâu thuẫn trong sách được giữ bằng điều kiện (`build_*` ghi từng cặp, test `test_book_internal_conflicts_are_kept_apart`), còn lại nói thẳng
  là hai mặt (Tài thuận / nghịch khi Tài không vượng; giàu / nghèo theo Trích Thiên Tủy; quý / tiện; đường chảy của Tài vs thế cân bằng).
- Không tên sách, trang, "ngưỡng" trong văn: ở note của từng câu và mục Căn cứ.

## 3. Bỏ có chủ đích

- 八字真宗: ngoại tình, tái hôn, tam giác, nhân tình (tr.57 #9, 13-17, 22, 26, 31-32, 35-38 và vế sau #29-30), quan tai / lao ngục (tr.53-54), thọ yểu
  và tống chung cha mẹ (tr.54-55), anh em yểu, con nuôi, con riêng (tr.63-64 #1-19), số và giới tính con, sinh nở (tr.60-61), bệnh tật, thương tích
  (tr.61-63), các năm tang cha mẹ, bệnh, hỏa hoạn (tr.64-65 #4-7, 17, 39-41, 43), "cung giáp trụ" / đếm anh em (tr.63).
- Không tính được nếu không đoán: nạp âm Tài / Quan tinh (tr.50 #3, tr.53 #13), "女命财优官地" (tr.50 #15), tiểu vận (tr.64 #9-12), "命前五辰 / 命后三辰"
  (tr.64 #2-3: 命 nào), đại hạn (#18-19), "三合三会相战" (#15), "身弱入弱乡" (#16, trùng phép xếp vận đã có).
- Trích Thiên Tủy: mọi lời khắc vợ / khắc con / không con / số con / trai gái (Phu Thê, Tử Nữ tr.128-132), thọ yểu (tr.145-148), "bại tổ nhục tông"
  (tr.133), các lời cần đọc thanh / trọc, chân / giả thần, hóa thần, các điển (Tư Mã, ngũ chung), Xuất Thân tr.219-223 (định tính).

## 4. BLOCKED / còn mở

- **ZZ tr.73 #8 "日刃藏杀，妻烈好斗，夫妻不和": không bao giờ bắn.** Với bảng dương nhẫn của tr.72 và bảng tàng can của sách, không chi ngày nào là
  nhẫn của nhật can mà tàng Thất Sát (Bính Ngọ, Mậu Ngọ, Nhâm Tý, Đinh Tỵ, Kỷ Tỵ, Quý Hợi đều không). Tr.73 #9 lại ghi "戊刃在未，己刃在辰", trái
  bảng tr.72 (Mậu Ngọ, Kỷ Tỵ) — vênh trong sách; hệ thống giữ bảng tr.72. Không mã hóa, cần người đọc lại ý tác giả.
- Ngưỡng "vượng / nhược" của nhóm thập thần (25 % / 12 %) là của hệ thống; sách không có thước đo. Luật hay bắn nhất: tr.65 #21 (chi năm hình /
  xung / hại thai, mệnh, thân cung) ở ~58 % số năm — đúng chữ sách nhưng dày; nói một lần cho các năm cùng điều kiện.
- 11/147 luật chưa bắn trên 300 lá thử (`BT_ZZK_W25` Tài vượng chảy vào nhật chủ, `R01`, `Y13`, `Y37`, `OG_QUANSAT`, `BT_TTTK_PHU3/5`, `TIEN5`,
  `DV1`, `HD1`, `HD9`): điều kiện hẹp, không phải lỗi; `OG_QUANSAT` gần như không thể (trụ bên trái trụ Quan có Quan thì Quan đã ở hai trụ).
- Thiệu Vĩ Hoa (bản quét) tr.148-173, 462-499, 519-556: đã chép lại toàn văn và lập danh sách điều kiện → nhận định (xem §5); chưa mã hóa ở commit này.
- Trang giới thiệu (`/gioi-thieu/`) chỉ đếm gói luật cấp cao (`engine/data/pack_*.json`): con số 八字真宗 giảm 83 → 73 vì 20 luật chuyển sang gói
  `bazi_deep/`; các gói `bazi_deep` (TTT, TVH, kin) chưa được đếm ở trang này (của luồng khác).

## 5. Thiệu Vĩ Hoa — tình trạng

(cập nhật ở commit sau)
