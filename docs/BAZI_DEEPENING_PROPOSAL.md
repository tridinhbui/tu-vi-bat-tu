# Đề xuất nâng chiều sâu luận giải Bát Tự

Phạm vi: chỉ tầng tri thức và suy luận của Bát Tự. Không bàn UI hay lỗi kỹ thuật, trừ chỗ lỗi kỹ thuật làm sai nền dữ kiện.
Tài liệu này không sửa code. Các tên chương sách chỉ để định hướng đối chiếu. Số trang và câu chữ phải qua quy trình `verified` của dự án (như `八字真宗`) trước khi quy tắc được đánh dấu là có nguồn.

---

## 0. Chẩn đoán hiện trạng (đọc từ code)

| Lớp | Hiện có | Khoảng trống |
|---|---|---|
| Lịch/trụ | Tiết khí chính xác, 4 trụ, tàng can, thập thần, trường sinh (âm nghịch), đại vận, thai nguyên, mệnh/thân cung, không vong, thần sát tra bảng ([bazi.py](../engine/tvbt/bazi.py)) | Tàng can chỉ là danh sách, không có phân lực. Không biết "đã vào tiết bao nhiêu ngày" cho tư lệnh. Tuổi đại vận lấy `năm − năm sinh` nguyên, còn `start_age` là số thập phân. |
| Quan hệ | Quan hệ **từng cặp**: can hợp/xung, lục hợp/xung/hại/phá, tam hợp/tam hội **đủ ba chữ**, hình ([bazi.py:130](../engine/tvbt/bazi.py)) | Không có bán hợp, củng hợp, ám hợp. Không phân biệt kề sát với cách vị. Không xét tranh hợp hay hợp bị phá. `transforms` luôn là `None`, tức không có logic hợp hóa. Không có thứ tự giải quyết khi nhiều tương tác chồng nhau. |
| Fact cho rule engine | Chỉ 8 fact: can ngày, nạp âm, hành vắng mặt, hành Nhật Chủ, `dm_has_root` (boolean, **đếm cả dư khí và cả trụ ngày**), chi tháng, trường sinh theo tháng ([facts.py:38](../engine/tvbt/reasoning/facts.py)) | Không có fact về thập thần, vị trí, cách cục, khí thế, tương tác, dụng thần. Vì vậy 55 rule Bát Tự trong pack (`day_master_character`, `element_balance`, `day_pillar_nap_am`) đều chỉ tra một fact. Bộ suy luận đa bước, ngoại lệ và mâu thuẫn ([engine.py](../engine/tvbt/reasoning/engine.py)) gần như chưa được dùng cho Bát Tự. |
| Văn bản phân tích | [analysis.py](../engine/tvbt/analysis.py) mô tả đắc lệnh/căn/trợ lực rồi **cố ý không kết luận** ("chưa có quy tắc cách cục", "không gộp thành nhãn thân vượng/nhược"). | Thái độ thận trọng là đúng. Nhưng "đắc lệnh" hiện = hành của chi tháng cùng hành hoặc sinh Nhật Chủ (`tiet`), bỏ qua Tứ Quý Thổ, tư lệnh và 12 trạng thái. Chưa có đường đi từ dữ kiện đến luận giải. |
| Đại vận/lưu niên | Thập thần của can vận/niên/nguyệt, quan hệ từng cặp với nguyên cục ([temporal.py](../engine/tvbt/temporal.py)) | Không tính lại cách cục/khí thế khi thêm vận. Không có cái-đầu-tiệt-cước, phục/phản ngâm, tuế vận tịnh lâm, xung khai khố, hay vai trò dụng thần qua từng thời kỳ. |
| Xử lý mâu thuẫn | Độ đặc hiệu = số điều kiện lá; chỉ rule `verified` mới thắng ([conflict.py](../engine/tvbt/reasoning/conflict.py)) | Chưa có thứ bậc theo **tầng** (cách cục thắng thập thần lẻ; dụng thần thắng quy tắc đơn). Chưa có khái niệm "nhiều cách đọc cùng hợp lệ". |
| Chủ thể suy luận | `chart` và `palace` ([engine.py:114](../engine/tvbt/reasoning/engine.py)) | Bát Tự cần chủ thể `pillar`, `char`, `interaction`, `cach`, `luck`, `year`, `topic`. |

**Kết luận.** Hệ thống đang ở mức "tra Can Chi và giải nghĩa". Phần còn thiếu không phải là thêm câu chữ. Phần thiếu là ba tầng **tính toán** nằm giữa dữ kiện và lời luận:

1. Khí thế định lượng có thứ bậc (tư lệnh, căn, thấu, vị trí, dòng khí).
2. Bộ giải tương tác (hợp, xung, hình có điều kiện và có thứ tự).
3. Bộ nhận diện cách cục và dụng thần theo từng phương pháp.

---

## 1. Kiến trúc suy luận đề xuất

### 1.1 Nguyên tắc: Analyzer tính, Rule diễn giải

- **Analyzer** (Python thuần, tất định, nhận `school_profile`) tính các fact có cấu trúc kèm trace. Ví dụ: sức căn, danh sách tương tác đã giải, ứng viên cách cục.
- **Rule** (JSON như hiện nay, qua DSL) biến fact thành finding có nguồn, mức xác minh và ngoại lệ.
- Logic số học và đồ thị không nhét vào JSON rule. JSON chỉ chứa tri thức dạng "nếu fact X thì nhận định Y theo sách Z".

### 1.2 Đường ống sáu bước, đúng thứ tự Tượng → Khí → Thế → Cách → Dụng → Biến

```
S0 Lịch (có sẵn)
S1 TƯỢNG/KHÍ   bz_season.py    vượng-tướng-hưu-tù-tử, tư lệnh, hàn-nhiệt-táo-thấp, tượng can/chi
S2 THẾ         bz_position.py  đồ thị vị trí (kề/cách/xa), căn, thấu, khố
               bz_interact.py  bộ giải tương tác (hợp-xung-hình theo thứ tự) -> "cục sau tương tác"
               bz_strength.py  khí thế từng chữ, từng hành, từng nhóm thập thần, Nhật Chủ (có biên)
               bz_flow.py      dòng khí sinh–khắc trên đồ thị, điểm tắc
S3 CÁCH        bz_geju.py      ứng viên cách (nội/ngoại), thành–bại–cứu, thanh–trọc, thuần–tạp
S4 DỤNG        bz_yongshen.py  mỗi phương pháp một bảng Dụng/Hỷ/Kỵ/Cừu/Nhàn, rồi bảng đối chiếu
S5 BIẾN        bz_luck.py      chạy lại S2–S4 trên cục mở rộng (nguyên cục + vận + niên + nguyệt), lấy delta
S6 TỔNG        bz_synth.py     bộ lập kế hoạch luận giải theo chủ đề, bộ tìm phản chứng
S7 RULE        engine hiện có  nhận fact từ S1–S6, phát finding có nguồn
```

Mỗi bước ghi `Trace` (có sẵn) theo dạng `{input, rule_id/analyzer, output, school}` để mọi kết luận truy ngược được.

### 1.3 Knowledge graph

- **Nút:** Can (10), Chi (12), Hành (5), Thập thần (10), Trụ (4 + vận/niên/nguyệt), Tương tác, Cách, Dụng thần, Quy tắc, Nguồn, Trường phái.
- **Cạnh có kiểu:** `sinh`, `khắc`, `tàng`, `thấu`, `căn`, `hợp`, `xung`, `hình`, `phá`, `kề`, `cách_vị`, `tư_lệnh`, `thành_cách`, `phá_cách`, `cứu`, `là_dụng_của`.
- Dùng lại `Node/Edge` của [engine.py](../engine/tvbt/reasoning/engine.py), mở rộng thuộc tính `weight_class` và `school`.
- Đồ thị cho phép truy vấn cấu trúc. Ví dụ "tìm đường Sát → Nhật Chủ có Ấn nối không?" (Sát Ấn tương sinh), "Tài có bị Tỉ Kiếp chắn giữa không?" (Quần Kiếp tranh Tài).

### 1.4 Khí thế có thứ bậc, không đếm ngũ hành

- Mỗi chữ có **sức** tính từ: lệnh (BZ-01/02), vị trí (BZ-05), căn (BZ-03), thấu (BZ-04), tương tác đã giải (BZ-53).
- Kết quả là **thang thứ bậc kèm bằng chứng** (ví dụ `thiên vượng, biên độ 0.12, 2 cách đọc`), không phải một điểm duy nhất.
- Trọng số là lựa chọn của hệ thống (`basis: he_thong`). Chúng nằm trong `school_profile` có tên và có version, công khai trên giao diện, để người dùng tự đổi và thấy kết luận đổi theo.
- Gần ngưỡng thì xuất **hai cách đọc** (BZ-85), không ép về một.

### 1.5 Ưu tiên và mâu thuẫn

Thứ bậc giữa các tầng khi hai finding đối nghịch (có nguồn kinh điển cho tinh thần này, nhưng thứ bậc cụ thể là lựa chọn thiết kế, cần ghi rõ):

```
Ngoại cách/Tòng/Hóa đã xác lập > Cách cục nội > Dụng thần theo phương pháp > Tương tác cục bộ > Thập thần lẻ > Thần sát
```

- Mở rộng [conflict.py](../engine/tvbt/reasoning/conflict.py): mỗi rule có `layer` và `school`. Khi hai finding đối nghịch thuộc **cùng trường phái**, tầng cao thắng. Khác trường phái thì **không phân xử**, hiển thị cả hai.
- Kiểu mâu thuẫn có tên: `cach_vs_yongshen`, `method_vs_method`, `interaction_vs_interaction`, `season_vs_structure`. Mỗi kiểu có mẫu giải thích riêng.

### 1.6 Nhãn mức độ chắc chắn

Mỗi câu luận mang đúng một nhãn:

| Nhãn | Ý nghĩa |
|---|---|
| `tinh_toan` | Tính được và kiểm chứng được (thiên văn, lịch, bảng tra). |
| `kinh_dien` | Một sách cụ thể nói vậy (kèm chương/trang đã verified). |
| `he_thong` | Định nghĩa hay ngưỡng do hệ thống chọn. |
| `suy_dien` | Kết hợp nhiều tầng, truy vết được nhưng không có sách nào nói nguyên văn. |

### 1.7 Luận giải truyền thống và dự báo khoa học

- Bát Tự là hệ thống biểu tượng truyền thống. Theo hiểu biết của tôi, không có nghiên cứu đối chứng độc lập nào xác nhận Tứ Trụ dự đoán được sự kiện đời sống tốt hơn ngẫu nhiên. Phần mềm không được diễn đạt như vậy.
- Giao diện và NLG phải **chặn** các câu dạng dự báo chắc chắn ("sẽ", "năm X chắc chắn"). Câu mẫu: "Theo sách A, cấu trúc này được đọc là…; đây là luận giải truyền thống, chưa được kiểm chứng thực nghiệm."
- "Kiểm thử" ở đây nghĩa là **trung thành với kinh điển** (hệ thống ra đúng kết luận mà mệnh lệ trong sách ra) và **nhất quán nội tại**. Nó không có nghĩa là xác minh tính đúng của tiên đoán. Hai điều này tách bạch trong báo cáo kiểm thử (BZ-88).

---

## 2. Bộ ví dụ Tứ Trụ dùng chung

Ký hiệu `Năm / Tháng / Ngày / Giờ`. Các lá số dựng để minh họa cấu trúc, không phải người thật. EX1–EX15 đã kiểm khớp quy tắc ngũ hổ độn, ngũ thử độn và quy luật âm dương của Can Chi (xem phụ lục, mục 6).

| Mã | Tứ Trụ | Đặc điểm dùng để minh họa |
|---|---|---|
| **EX1** | Giáp Tý / Bính Dần / Giáp Tuất / Canh Ngọ | Giáp sinh tháng Dần = Kiến Lộc. Bính (Thực Thần) thấu tháng, Canh (Thất Sát) thấu giờ. Dần–Ngọ–Tuất tam hợp Hỏa đủ ba chữ. |
| **EX2** | Quý Dậu / Ất Mão / Mậu Tý / Đinh Tỵ | Mậu sinh tháng Mão, Ất (Chính Quan) thấu tháng. Quý (Chính Tài) ở năm. Đinh (Chính Ấn) ở giờ. Dậu–Mão xung (năm–tháng). Mão–Tý hình (tháng–ngày). Quý–Mậu hợp nhưng cách Ất. |
| **EX3** | Tân Mão / Đinh Dậu / Giáp Thìn / Giáp Tý | Giáp sinh tháng Dậu, Tân (Chính Quan) thấu năm, Đinh (Thương Quan) thấu tháng, Đinh khắc Tân. Mão–Dậu xung ngay nguyệt lệnh. Thìn–Dậu hợp. Tý–Thìn bán hợp Thủy (Ấn). |
| **EX4** | Canh Thân / Ất Dậu / Ất Dậu / Tân Tỵ | Ất sinh tháng Dậu giữa Kim dày. Ất–Canh hợp (năm–tháng). Tỵ–Dậu bán hợp Kim. Mộc không căn: ứng viên Tòng Sát, nhưng Ất tháng còn bị Canh "trói". |
| **EX5** | Mậu Tuất / Kỷ Mùi / Giáp Tuất / Mậu Thìn | Giáp–Kỷ hợp (tháng–ngày) giữa tháng Thổ, Thổ dày. Tuất–Mùi hình. Thìn–Tuất xung (ngày–giờ). Ứng viên Hóa Thổ nhưng bị xung phá. |
| **EX6** | Nhâm Tý / Mậu Thân / Canh Thìn / Nhâm Ngọ | Canh sinh tháng Thân = Kiến Lộc. Nhâm (Thực Thần) bị Mậu (Thiên Ấn) kề khắc = Kiêu Thần đoạt Thực. Thân–Tý–Thìn tam hợp Thủy. Tý–Ngọ xung. |
| **EX7** | Canh Tý / Nhâm Ngọ / Đinh Dậu / Quý Mão | Đinh có Nhâm (Chính Quan) và Quý (Thất Sát) cùng thấu = Quan Sát hỗn tạp. Nhâm–Đinh hợp (tháng–ngày). Tý–Ngọ và Dậu–Mão hai xung. |
| **EX8** | Giáp Thân / Bính Tý / Bính Dần / Giáp Ngọ | Bính sinh tháng Tý (mùa lạnh): nhu cầu điều hậu. Quý ẩn trong Tý là Chính Quan. Tý–Ngọ xung (tháng–giờ). Giáp ×2 là Thiên Ấn thấu. |
| **EX9** | Nhâm Dần / Bính Ngọ / Bính Tuất / Mậu Tý | Bính sinh tháng Ngọ = Dương Nhận. Nhâm (Thất Sát) thấu năm, Mậu (Thực Thần) thấu giờ. Dần–Ngọ–Tuất hợp Hỏa đủ ba chữ làm Nhận quá vượng. Tý–Ngọ xung (tháng–giờ). |
| **EX10** | Canh Thân / Mậu Dần / Giáp Thân / Canh Ngọ | Giáp sinh tháng Dần. Canh ×2 (Thất Sát) và Thân ×2 đối đầu Mộc: Kim–Mộc giao chiến. Dần–Thân xung hai bên ngay nguyệt lệnh. Không có Thủy để thông quan; chỉ có Hỏa (Ngọ). |
| **EX11** | Tân Sửu / Nhâm Thìn / Ất Mão / Đinh Hợi | Ất: Tân (Thất Sát, năm) → Nhâm (Chính Ấn, tháng) → Ất (ngày), mỗi bậc kề nhau. Hợi–Mão bán hợp Mộc. Đinh–Nhâm hợp nhưng cách vị. |
| **EX12** | Quý Hợi / Kỷ Mùi / Canh Tý / Kỷ Mão | Canh có Quý (Thương Quan) và Kỷ ×2 (Chính Ấn). Hợi–Mão–Mùi tam hợp Mộc đủ ba chữ biến thành cục Tài khắc Ấn. Thương Quan sinh Tài qua Thủy → Mộc. |
| **EX13** | Giáp Thìn / Đinh Mão / Bính Dần / Quý Tỵ | Dần–Mão–Thìn tam hội Mộc đủ ba chữ, Giáp thấu năm, Ấn rất nặng với Bính. Quý (Chính Quan) ở giờ. Dần–Tỵ hình. |
| **EX14** | Giáp Tý / Bính Dần / Kỷ Sửu / Canh Ngọ | Tý–Sửu lục hợp (năm–ngày cách vị nhưng tháng giữa). Dần–Sửu ám hợp qua tàng Giáp–Kỷ. Giáp–Kỷ hợp lộ (năm–ngày, cách vị). |
| **EX15** | Nhâm Dần / Quý Mão / Ất Mão / Bính Tý | Ất ngày giờ Tý, không có Kim: điều kiện hình thức của Lục Ất Thử Quý (ngoại cách cổ, ít đồng thuận). |

---

## 3. Danh mục quy tắc

Mỗi mục có đủ sáu trường: **(a)** nguyên lý và nguồn cần đối chiếu, **(b)** điều kiện kích hoạt / ngoại lệ, **(c)** ví dụ, **(d)** tương tác nhiều tầng, **(e)** triển khai tất định, **(f)** giá trị so với hiện tại.

Viết tắt nguồn: **TBCT** `子平真詮`, **TTT** `滴天髓`, **CTBG** `窮通寶鑑`, **UHTB** `淵海子平`, **TMTH** `三命通會`. Một chỗ ghi "đối chiếu" nghĩa là tôi chưa kiểm chương/trang trong văn bản gốc.

Tổng cộng **89 nhóm quy tắc** (BZ-01 đến BZ-89): P0 = 59, P1 = 29, P2 = 3 (BZ-17 và BZ-18 tính ở cả hai mức). Số quy tắc đơn lẻ thực tế khi triển khai sẽ lớn hơn nhiều (ví dụ BZ-09 là ma trận 10×5).

### Tầng I — Tượng, Khí, Thế (nền tảng)

#### BZ-01 · Vượng–Tướng–Hưu–Tù–Tử theo nguyệt lệnh · **P0**
- **(a)** Nguyệt lệnh quyết định trạng thái năm hành: hành đương lệnh vượng, hành do nó sinh ra tướng, hành sinh ra nó hưu, hành khắc nó tù, hành nó khắc tử. TTT chương 月令 (đối chiếu), TBCT luận cách theo nguyệt lệnh.
- **(b)** Luôn chạy. Ngoại lệ: tháng Thìn/Tuất/Sửu/Mùi, Thổ vượng, hành mùa trước còn dư khí; một số sách chia 18 ngày cuối quý cho Thổ. Ngưỡng này nằm trong `school_profile`.
- **(c)** EX1, tháng Dần: Mộc vượng, Hỏa tướng, Thủy hưu, Kim tù, Thổ tử. Giáp Mộc đắc lệnh.
- **(d)** Trạng thái này là đầu vào của BZ-06, BZ-07, BZ-38. Tam hợp cục (BZ-46) có thể đổi hành đang mạnh nhất mà không đổi lệnh.
- **(e)** Bảng `season_state[12][5]` trong JSON. Analyzer xuất `bz.season.state.<hành>` ∈ {vượng, tướng, hưu, tù, tử}.
- **(f)** Thay `tiet` (boolean thô) bằng thang 5 bậc cho **cả năm hành**, không chỉ Nhật Chủ.

#### BZ-02 · Nhân nguyên tư lệnh · **P0**
- **(a)** Trong một tháng, can nào "nắm lệnh" thay đổi theo số ngày sau tiết. UHTB, TMTH, CTBG đều có bảng tư lệnh, các bảng **khác nhau** giữa các sách.
- **(b)** Cần số ngày từ tiết gần nhất (đã có `jie_used.prev_jie_utc`, chưa quy ra ngày). Ngoại lệ: trường phái không dùng tư lệnh thì tắt cờ.
- **(c)** EX1 sinh 3 ngày sau Lập Xuân: theo bảng phổ biến, giai đoạn đầu tháng Dần do dư khí (Mậu) nắm lệnh, rồi Bính, rồi Giáp. Số ngày phải lấy từ bảng của sách được chọn.
- **(d)** Đổi can nắm lệnh có thể đổi cách (BZ-14), đổi hỷ kỵ điều hậu (BZ-36).
- **(e)** `tu_menh_table[school][branch] = [(stem, days)...]`. Analyzer xuất `bz.siling.stem`, `bz.siling.day_in_month`. Đồng thời xuất cờ `near_boundary` nếu cách chuyển tiết < 1 ngày (dữ kiện giờ sinh không chắc).
- **(f)** Giải quyết trường hợp biên: hai người cùng tháng Dần nhưng khác ngày vào tiết có thể khác cách.

#### BZ-03 · Thông căn phân cấp · **P0**
- **(a)** Căn không chỉ có/không. Bản khí mạnh hơn trung khí hơn dư khí. Căn ở Lâm Quan/Đế Vượng/Trường Sinh mạnh hơn căn ở Mộ khố. Vị trí nguyệt chi > nhật chi > thời chi > niên chi (thứ tự cụ thể tùy trường phái). TTT, TBCT (đối chiếu).
- **(b)** Ngoại lệ: căn bị xung hoặc bị hợp trói giảm hoặc mất (đẩy sang BZ-53).
- **(c)** EX1: Giáp có căn **bản khí** ở Dần (tháng, Lâm Quan). Tuất ngày không có Giáp. Nhật Chủ Giáp có một căn mạnh ở nguyệt lệnh. EX4: Ất có căn bản khí ở Mão? Không có chữ Mão. Chỉ có Ất thấu (tháng, ngày), căn rỗng, nên là ứng viên Tòng.
- **(d)** Căn + thấu (BZ-04) + vị trí (BZ-05) + tương tác (BZ-53).
- **(e)** Với mỗi can thấu và mỗi Nhật Chủ, duyệt tàng can các chi: cùng chữ (căn thật), cùng hành (căn hành). Gán `class ∈ {ban_khi, trung_khi, du_khi}`, `stage ∈ 12 trạng thái`, `pillar`. Fact: `bz.root.<char>` = danh sách (pillar, class, stage).
- **(f)** Thay `dm_has_root` (đếm cả dư khí và cả trụ ngày, không phân cấp).

#### BZ-04 · Thấu can – Tàng – Lộ · **P0**
- **(a)** Tàng can "thấu" khi cùng chữ xuất hiện ở thiên can: ra mặt và có lực dụng. TBCT dùng "thấu" để chọn dụng của nguyệt lệnh. TTT bàn "隱顯" (ẩn hiện).
- **(b)** Thấu cùng chữ mạnh hơn thấu cùng hành. Ngoại lệ: thấu nhưng bị hợp, bị khắc (BZ-46, BZ-50).
- **(c)** EX2: nguyệt lệnh Mão chỉ tàng Ất, Ất thấu tháng: Chính Quan thấu. EX3: Dậu tàng Tân, Tân thấu năm (xa, qua Đinh), không kề tháng.
- **(d)** Xác định cách (BZ-14), thanh–trọc (BZ-26).
- **(e)** Phép chiếu `hidden → visible`. Fact `bz.tou.<tên_cách>` = {stem, pillar, adjacency_to_month}.
- **(f)** Phần "thấu" hiện chỉ là bảng thống kê trong UI; chưa dẫn tới cách.

#### BZ-05 · Cung vị và kề sát · **P0**
- **(a)** Hợp, khắc, sinh có lực khi **kề**, giảm khi **cách vị**, nhiều khi bị ngăn bởi chữ ở giữa. TBCT 論刑沖會合解法, TTT (đối chiếu). Các thành ngữ "tham sinh vong khắc", "tham hợp vong khắc" là quy tắc ưu tiên cục bộ.
- **(b)** Hai chữ ở trụ liền nhau (năm–tháng, tháng–ngày, ngày–giờ) là kề. Thiên can với địa chi cùng trụ là "tọa". Ngoại lệ: một số tương tác (xung chi) vẫn có hiệu lực qua một trụ nhưng yếu.
- **(c)** EX2: Quý (năm) hợp Mậu (ngày) bị Ất (tháng) ngăn. Quý lại sinh Ất kề bên, nên có thể đọc Quý "tham sinh Ất" mà "quên hợp". Cách đọc này là một nhánh hợp lệ, không phải chân lý.
- **(d)** Mọi tương tác ở BZ-45 đến BZ-56 đều kèm `adjacency`.
- **(e)** Đồ thị 8 chữ + 4 nút trụ, cạnh `kề` (khoảng cách 1), `cách_1` (2), `xa` (3). Fact `bz.pos.dist.<a>.<b>`.
- **(f)** Hiện `relations` coi mọi cặp ngang nhau. Đây là nguyên nhân chính khiến văn bản phải thêm câu "chưa xét điều kiện".

#### BZ-06 · Đắc lệnh – Đắc địa – Đắc thế – Đắc sinh (bốn trục) · **P0**
- **(a)** TTT chương 衰旺 và `八字真宗` p.26 (hệ thống đã có ba tiêu chí). Nâng thành bốn trục độc lập: lệnh (BZ-01/02), địa (căn ở chi, BZ-03), thế (đồng đảng thấu và kề), sinh (Ấn sinh nhập).
- **(b)** Ngoại lệ: Thổ ở Tứ Quý; Dương Nhận (BZ-22).
- **(c)** EX1: lệnh đắc, địa đắc (Dần), thế khá (Giáp một mình nhưng Tuất không sinh), sinh không (không Ấn). Khoảng trống: Dần–Ngọ–Tuất hợp Hỏa tiết khí (BZ-47).
- **(d)** Bốn trục tách biệt để người đọc thấy "mạnh vì đâu, yếu vì đâu".
- **(e)** Vector 4 chiều với bằng chứng từng chiều. Không cộng thành một điểm ở bước này.
- **(f)** Thay danh sách mô tả bằng đối tượng có cấu trúc, đầu vào cho BZ-07.

#### BZ-07 · Thang bậc vượng–nhược có biên · **P0**
- **(a)** Thang cổ điển: cực nhược, nhược, thiên nhược, trung hòa, thiên vượng, vượng, cực vượng. Nhận xét "không nên mặc định thân nhược phải phù, thân vượng phải khắc" thuộc TTT 中和, 順逆 và TBCT (dụng thần theo cách trước, phù ức sau).
- **(b)** Chạy sau BZ-06 và BZ-54 (cục sau tương tác). Biên < ngưỡng (`school_profile.margin`) → xuất hai mức liền kề và `ambiguous=true`.
- **(c)** EX1 thô: "thân vượng". Sau tam hợp Hỏa (BZ-47): Giáp bị tiết mạnh, "thiên vượng, hoặc trung hòa nếu tính hợp Hỏa". Hai cách đọc.
- **(d)** Lệ thuộc BZ-54 (hợp cục đổi khí thế). Đầu ra đi vào BZ-35, BZ-28.
- **(e)** Lexicographic: so theo thứ tự (lệnh, căn, thế) trước, bằng nhau mới xét chiều sau, kèm biên. Ngưỡng và trọng số trong `school_profile` có tên (`weights: "tbct_leaning_v1"`).
- **(f)** Thực hiện đúng ý "không đếm Ngũ Hành" mà vẫn có nhãn dùng được.

#### BZ-08 · Hàn – Nhiệt – Táo – Thấp · **P0**
- **(a)** TTT chương 寒暖, 燥濕. Mùa quyết định nhiệt độ và độ ẩm nền; cấu trúc cục điều chỉnh.
- **(b)** Chỉ số nền từ chi tháng (Tý Sửu Hợi: hàn; Tỵ Ngọ Mùi: nhiệt; Sửu Thìn Mùi Tuất: thấp/táo…) điều chỉnh bởi số hành Hỏa/Thủy **có sức** trong cục. Ngoại lệ: Hỏa/Thủy cục (BZ-47) có thể đảo chỉ số.
- **(c)** EX8: Bính (Hỏa) sinh tháng Tý: nền hàn, cần Hỏa/Mộc ấm cục. Giáp ×2 và Dần giúp, nhưng Thân–Tý bán hợp Thủy làm hàn thêm.
- **(d)** Đầu vào của điều hậu (BZ-36).
- **(e)** Hai chỉ số rời `heat ∈ [-2,2]`, `moist ∈ [-2,2]`, thứ bậc.
- **(f)** Dữ kiện thiếu hoàn toàn hiện nay, nhưng là điều kiện để điều hậu (một trong các phương pháp) chạy được.

#### BZ-09 · Thiên Can tượng × trạng thái mùa · **P1**
- **(a)** TTT chương 天干 mô tả bản chất từng can ("Giáp như cây lớn, Ất như dây leo…"). CTBG đặc tả thêm theo từng tháng. Đây là lớp **Tượng**.
- **(b)** Ma trận 10 can × 5 trạng thái (vượng/tướng/hưu/tù/tử) = 50 ô văn bản có nguồn; ô nào chưa verified thì gắn `draft`.
- **(c)** Cùng Nhật Chủ Giáp: EX1 (Giáp vượng giữa xuân) khác EX3 (Giáp tù tháng Dậu, Kim sát lệnh).
- **(d)** Kết hợp BZ-08 cho tượng dạng "Giáp Mộc mùa đông thiếu Hỏa".
- **(e)** Rule JSON với `conditions: {bz.day_master_stem, bz.season.state.<hành Nhật Chủ>}`.
- **(f)** Mở rộng 20 rule `day_master_character` (chỉ theo can) thành 50+ rule theo can × mùa.

#### BZ-10 · Địa Chi tượng và Tứ Quý khố · **P1**
- **(a)** TTT chương 地支. Mỗi chi có tính (Tý cực hàn, Ngọ cực nhiệt, Thìn Tuất Sửu Mùi là Thổ chứa khố…). TMTH có phần luận chi.
- **(b)** Tượng chi gắn với vị trí trụ (BZ-05).
- **(c)** EX5: bốn chi Tuất, Mùi, Tuất, Thìn đều là Thổ khố: đối tượng của BZ-11.
- **(d)** BZ-11, BZ-31 (chuyên vượng Thổ).
- **(e)** Bảng 12 mục `branch_image`.
- **(f)** Lớp Tượng hiện chỉ có 10 can và nạp âm.

#### BZ-11 · Mộ khố và mở khố · **P1**
- **(a)** Thìn (Thủy khố), Tuất (Hỏa khố), Sửu (Kim khố), Mùi (Mộc khố). Trường phái chia: khố cần xung/hình mới phát; hay khố tự có căn dù yếu. TBCT bàn tàng khố của Tài, TMTH (đối chiếu).
- **(b)** Cờ `khố_policy ∈ {can_mo, tu_co_can}` trong `school_profile`. Mở khố bởi xung hoặc hình.
- **(c)** EX5: Thìn–Tuất xung (ngày–giờ) vừa mở khố vừa phá Thổ (BZ-30). EX6: Thìn là khố Thủy trong tam hợp Thủy.
- **(d)** Với đại vận/lưu niên có xung (BZ-73).
- **(e)** Cạnh `mở_khố(from=xung_or_hình, to=chi_khố)`; cập nhật `root.class` khi mở.
- **(f)** Căn ở khố hiện bị coi như căn thường hoặc không tính.

#### BZ-12 · Trường sinh: chọn trường phái âm dương · **P1**
- **(a)** Hiện hệ thống dùng "âm nghịch" (`yin_reverse`). Có trường phái "âm dương đồng sinh đồng tử" (Giáp–Ất cùng sinh ở Hợi…). Tranh luận kéo dài, không phải chân lý.
- **(b)** Cờ trong `school_profile`. Kết quả BZ-03 phải ghi trường phái đang dùng.
- **(c)** Ất tại Ngọ: âm nghịch cho Trường Sinh; trường phái đồng sinh cho kết quả khác.
- **(d)** Mọi chỗ dùng trạng thái 12 giai đoạn.
- **(e)** Hai bảng `growth_start`; test hai bảng khớp ở các ô không tranh cãi.
- **(f)** Hiện chỉ có một cách; muốn so sánh trường phái thì cần cả hai.

#### BZ-13 · Dòng khí (源流) và điểm tắc · **P0**
- **(a)** TTT chương 源流: khí lưu thông theo chuỗi sinh. Chuỗi liền (ví dụ Thủy → Mộc → Hỏa → Thổ) là tốt về khí; bị cắt giữa chừng là "tắc", nên cần thông quan (BZ-37).
- **(b)** Xây đồ thị có hướng trên các nút hành, trọng số = sức hành (BZ-06). Nút bị khắc cắt chuỗi là điểm tắc.
- **(c)** EX3: Thủy (Tý) → Mộc (Giáp) → Hỏa (Đinh) bị Thủy yếu (Tý đơn lẻ) và Kim (Tân, Dậu) khắc Mộc… Chuỗi: Kim khắc Mộc, Hỏa khắc Kim: Đinh kiềm Tân.
- **(d)** Tầng Thế → Cách: nhiều cách nhận diện (Thực Thần sinh Tài, Sát Ấn tương sinh) thực chất là chuỗi trên đồ thị này.
- **(e)** Đồ thị trọng số + hàm `longest_flow()`, `break_points()`. Fact `bz.flow.chain`, `bz.flow.breaks`.
- **(f)** Là cơ sở chung cho BZ-58 đến BZ-67, thay vì hard-code từng cấu trúc.

### Tầng II — Cách cục nội cách

#### BZ-14 · Quy trình định cách từ nguyệt lệnh · **P0**
- **(a)** TBCT: lấy nguyệt lệnh làm gốc; nếu chi tháng có nhiều tàng can thì xét can nào **thấu**; không thấu thì lấy bản khí; Tứ Quý xét riêng (BZ-24). Có trường phái lấy tư lệnh (BZ-02).
- **(b)** Trình tự: (1) Kiến Lộc/Dương Nhận nếu chi tháng là lộc/nhận của Nhật Chủ (BZ-21, BZ-22); (2) can tàng thấu theo thứ tự bản/trung/dư; (3) không thấu → bản khí; (4) không thành → ngoại cách (BZ-28 đến BZ-33). Ngoại lệ: nhiều can thấu cùng lúc → nhiều ứng viên.
- **(c)** EX1: chi Dần là Lộc của Giáp → **Kiến Lộc**; Bính thấu và Canh thấu bổ sung dụng (Thực chế Sát). EX2: Mão tàng Ất, thấu → **Chính Quan cách**.
- **(d)** Kết quả `cach_candidates` thay vì `cach`: danh sách có thứ hạng + lý do.
- **(e)** Hàm `detect_geju(chart, school)` trả `[Candidate{name, basis, steps}]`. Mỗi bước ghi trace.
- **(f)** Là phần hệ thống hiện thừa nhận thiếu ("chưa có quy tắc cách cục"). Đây là khối giá trị lớn nhất của đề xuất.

#### BZ-15 · Chính Quan cách · **P0**
- **(a)** TBCT 論官: Quan cần Tài hoặc Ấn hộ vệ, kỵ Thương Quan khắc, kỵ hình xung, kỵ Quan Sát hỗn tạp.
- **(b)** Kích hoạt khi BZ-14 chọn Chính Quan. Thành: Tài sinh Quan hoặc Ấn hộ Quan mà Quan không bị phá. Bại: Thương Quan thấu mà không có Ấn chế, hình xung nguyệt lệnh, Quan Sát cùng thấu. Cứu: Ấn chế Thương hoặc Hợp Thương.
- **(c)** EX2: Quan thấu (Ất), có Tài (Quý), có Ấn (Đinh). Thuận, nhưng Dậu–Mão xung và Mão–Tý hình **chạm thẳng nguyệt lệnh** nên phá lực: kết luận là "cách thành nhưng bị phá", cần xét cứu.
- **(d)** Cùng lúc với BZ-25 (thành bại), BZ-50 (xung), BZ-51 (hình).
- **(e)** Bảng `geju_def[Chính Quan] = {thanh:[...], bai:[...], cuu:[...]}` dạng DSL; Analyzer đánh giá từng điều kiện bằng fact S2.
- **(f)** Chuyển một cách thành chuỗi điều kiện kiểm tra được thay vì một câu mô tả chung.

#### BZ-16 · Thất Sát cách · **P0**
- **(a)** TBCT 論偏官: Sát cần chế (Thực Thần chế Sát), hóa (Ấn hóa Sát), hoặc hợp (hợp Sát), hoặc Dương Nhận giá Sát; Sát không chế thì là "bại".
- **(b)** Thân yếu mà Sát nặng cần Ấn hóa. Thân vượng, Sát có Tài sinh, Thực chế thì quý. Ngoại lệ: Sát thành Tòng Sát (BZ-28).
- **(c)** EX1 nếu xét Canh là Sát: Bính (Thực Thần) khắc Canh; vị trí không kề (Bính tháng, Canh giờ, cách ngày) nên lực chế giảm (BZ-05).
- **(d)** BZ-59 (Sát Ấn), BZ-60 (Thực chế Sát), BZ-22 (Nhận giá Sát).
- **(e)** Như BZ-15; có thêm điều kiện `margin` thân (BZ-07).
- **(f)** Phân biệt "Sát có chế" và "Sát không chế", hai kết quả rất khác.

#### BZ-17 · Ấn cách (Chính Ấn, Thiên Ấn) · **P0** (Chính Ấn) / **P1** (Thiên Ấn)
- **(a)** TBCT 論印綬, 論偏印. Ấn kỵ Tài phá; Thiên Ấn (Kiêu) kỵ đoạt Thực.
- **(b)** Thành: Quan Sát sinh Ấn, hoặc thân vượng có Thực Thương tiết. Bại: Tài phá Ấn không có Tỉ Kiếp cứu. Kiêu Thần gặp Thực Thần (BZ-65).
- **(c)** EX8: Giáp ×2 là Thiên Ấn thấu, sinh Bính vốn ở mùa lạnh: Ấn có giá trị điều hậu cộng thêm.
- **(d)** BZ-08, BZ-64.
- **(e)** `geju_def[Chính Ấn]`, `geju_def[Thiên Ấn]`.
- **(f)** Hiện Ấn chỉ được liệt kê vị trí.

#### BZ-18 · Tài cách (Chính Tài, Thiên Tài) · **P0** (Chính) / **P1** (Thiên)
- **(a)** TBCT 論財: Tài cần có Quan hoặc Thực Thương sinh, kỵ Tỉ Kiếp cướp, cần thân đủ sức gánh.
- **(b)** Thành: Tài có nguồn (Thực Thương) và thân vượng; Tài có Quan; Tài có kho (BZ-11). Bại: Tỉ Kiếp nặng không có Quan chế, Tài nhiều thân nhược không Ấn.
- **(c)** EX7: Canh (Chính Tài) thấu năm xa, bị Quý (Sát) và Nhâm (Quan) ở giữa; Hỏa Đinh yếu nên "Tài nhiều thân yếu" nếu Đinh không đủ căn.
- **(d)** BZ-64 (Tỉ Kiếp tranh Tài).
- **(e)** `geju_def[Chính Tài]`, `geju_def[Thiên Tài]`.
- **(f)** Nền cho phần tài vận (BZ-80).

#### BZ-19 · Thực Thần cách · **P0**
- **(a)** TBCT 論食神: Thực Thần sinh Tài là tốt; cần chế Sát; kỵ Kiêu đoạt.
- **(b)** Thành: Thực Thần có sức, có Tài làm đường ra, hoặc chế Sát. Bại: Thiên Ấn kề khắc mà không có Tài giải.
- **(c)** EX1: Bính thấu nguyệt can; Tuất ngày; hợp Hỏa cục làm Thực Thương **quá vượng**.
- **(d)** BZ-60, BZ-65, BZ-66.
- **(e)** `geju_def[Thực Thần]`.
- **(f)** Hiện Thực Thần chỉ là nhãn ở vị trí thiên can.

#### BZ-20 · Thương Quan cách · **P0**
- **(a)** TBCT 論傷官: các hình thái cổ điển: Thương Quan sinh Tài, Thương Quan phối Ấn, Thương Quan dụng Sát Ấn, Thương Quan kiến Quan, Thương Quan tận (傷官傷盡).
- **(b)** Mỗi hình thái là một điều kiện cấu trúc (xem BZ-61, BZ-62). Ngoại lệ: Thương Quan kiến Quan tùy việc có Tài hoặc Ấn thông quan.
- **(c)** EX3: Đinh (Thương Quan) thấu nguyệt can, kề Tân (Quan, năm): **Thương Quan kiến Quan**; Ấn chỉ có Quý ẩn trong Tý.
- **(d)** BZ-61.
- **(e)** `geju_def[Thương Quan]` với danh sách hình thái.
- **(f)** Cho phép nói "Thương Quan là gì" thay vì chỉ "có Thương Quan".

#### BZ-21 · Kiến Lộc và Nguyệt Kiếp · **P0**
- **(a)** TBCT 論建祿月劫: Kiến Lộc / Nguyệt Kiếp không tự thành cách, phải xem thêm Quan, Tài, Thực Thương làm dụng.
- **(b)** Kích hoạt khi chi tháng là Lộc (Giáp–Dần, Ất–Mão, Bính Mậu–Tỵ, Đinh Kỷ–Ngọ, Canh–Thân, Tân–Dậu, Nhâm–Hợi, Quý–Tý) hoặc Kiếp Tài.
- **(c)** EX1 (Giáp Dần): chọn dụng từ Thực Thần (Bính) + Sát (Canh). EX6 (Canh Thân): dụng từ Thực Thần (Nhâm), nhưng bị Kiêu (Mậu).
- **(d)** BZ-14 (bước 1), BZ-23.
- **(e)** Bảng `lu_nhan[stem] = {lu, nhan}`. Trả `geju=Kiến Lộc` kèm `yong_candidates`.
- **(f)** Tránh đọc "thân vượng nên phải khắc tiết" một cách máy móc.

#### BZ-22 · Dương Nhận cách · **P1**
- **(a)** TBCT 論陽刃: Dương Nhận phải có Quan Sát chế; Nhận Sát tương hợp. Chỉ áp cho dương can (Giáp–Mão, Bính Mậu–Ngọ, Canh–Dậu, Nhâm–Tý); âm can: có trường phái không lập.
- **(b)** Cờ trường phái cho âm nhận. Nhận mà không Quan Sát chế là hung theo nguyên lý "thái quá".
- **(c)** EX9: Bính sinh Ngọ, Nhâm (Sát) thấu năm. Nhận nên phải có Sát chế, nhưng Dần–Ngọ–Tuất hợp Hỏa làm Nhận quá thịnh, còn Tý (Sát ẩn Quý) xung Nhận ngay nguyệt lệnh. Hai cách đọc: Nhận bị xung nên giảm, hoặc Nhận gặp hợp cục nên bội thịnh.
- **(d)** BZ-16 (Nhận giá Sát), BZ-50 (xung Nhận).
- **(e)** Bảng `lu_nhan`.
- **(f)** Một dạng thân vượng đặc biệt mà quy tắc phù ức chung xử lý sai.

#### BZ-23 · Dụng thần từ cách: bảng "dụng theo cách" · **P0**
- **(a)** TBCT 論用神: mỗi cách có họ dụng kỳ vọng (Quan dụng Tài Ấn; Sát dụng Thực/Ấn; Ấn dụng Quan Sát; Thực dụng Tài; Thương dụng Tài hoặc Ấn…).
- **(b)** Chỉ là bảng khởi điểm; sau đó kiểm tra BZ-42 xem dụng có thật sự hiện diện, có lực, không bị phá.
- **(c)** EX2: Quan cách → xem Tài (Quý) và Ấn (Đinh).
- **(d)** BZ-42, BZ-26.
- **(e)** JSON `geju_yong[geju] = [ten_god...]`.
- **(f)** Cầu nối cách → dụng thần.

#### BZ-24 · Tứ Quý (Thìn Tuất Sửu Mùi) chọn cách · **P1**
- **(a)** TBCT 論雜格 (đối chiếu): tháng Tứ Quý tàng 3 can; chọn can thấu; nếu nhiều can thấu, ưu tiên theo trường phái; một số tình huống "tạp khí tài quan" cần xung hình khai khố.
- **(b)** Tháng chi ∈ {Thìn, Tuất, Sửu, Mùi}. Quy tắc phụ thuộc BZ-02, BZ-11.
- **(c)** EX5 (tháng Mùi tàng Kỷ Đinh Ất); Kỷ thấu nguyệt can → Chính Tài cách; nhưng Kỷ hợp Giáp.
- **(d)** BZ-30 (hợp hóa) chồng với cách.
- **(e)** Mở rộng bước (2) của BZ-14.
- **(f)** Trường hợp khó nhất và hay bị bỏ qua.

#### BZ-25 · Thành – Bại – Cứu ứng (bảng điều kiện) · **P0**
- **(a)** TBCT 論用神成敗救應: cách thành nhờ gì, bại vì sao, và nếu bại thì có thứ gì cứu.
- **(b)** Mỗi cách có ba danh sách điều kiện. Cứu = điều kiện triệt tiêu điều kiện bại (thí dụ Ấn chế Thương Quan cứu Quan cách). Cách thành rồi bại, bại rồi cứu: ba trạng thái `thanh | bai | bai_co_cuu | thanh_nhung_bi_pha`.
- **(c)** EX3: Quan cách bại vì Thương Quan kề; cứu cần Ấn (Quý ẩn trong Tý, Giáp?). Kết luận "bại, cứu yếu".
- **(d)** Nhờ đồ thị dòng khí (BZ-13) để tìm đường Ấn tới Thương Quan.
- **(e)** Trong DSL: `bai` có thể có `exceptions` (đã hỗ trợ). `cuu` là rule thứ cấp với `suppresses`.
- **(f)** Là cách dùng sẵn cơ chế ngoại lệ trong [engine.py](../engine/tvbt/reasoning/engine.py), vốn chưa được dùng cho Bát Tự.

#### BZ-26 · Thanh – Trọc, Thuần – Tạp · **P0**
- **(a)** TTT chương 清濁; TBCT 論用神格局高低: cách tốt hay xấu ở chỗ thanh (một ý rõ ràng, không lẫn) hay trọc (lẫn Quan Sát, Tài Ấn xung khắc, hỷ kỵ lẫn lộn).
- **(b)** Chỉ số: số nhóm thập thần có sức xung khắc nhau thấy rõ; Quan Sát hỗn tạp; dụng thần bị phá. Ngoại lệ: "trọc mà có chế" vẫn có thể dùng được.
- **(c)** EX7 (Quan Sát hỗn tạp): trọc. EX2 chưa hỗn tạp nhưng bị hình xung: "thanh nhưng bị phá".
- **(d)** BZ-25, BZ-61.
- **(e)** Hai trục `clarity ∈ {thanh, tạm thanh, trọc}`, `purity ∈ {thuần, hơi tạp, tạp}` kèm danh sách nguyên nhân.
- **(f)** Có "độ cao thấp của cách" nhưng không dùng điểm số tổng.

#### BZ-27 · Cách biến (đổi cách theo cấu trúc) · **P1**
- **(a)** TBCT 論用神變化: dụng thần có thể đổi khi tương tác đổi (ví dụ Quan bị Thương hợp mất, chuyển sang Tài).
- **(b)** Chạy sau BZ-54: nếu cục sau tương tác khác hẳn, ghi cách mới.
- **(c)** EX5: trước hợp hóa → Chính Tài cách (Kỷ); nếu Giáp Kỷ hóa Thổ thành → chuyển sang Hóa Thổ cách.
- **(d)** BZ-30.
- **(e)** Chạy `detect_geju` hai lần (nguyên cục, cục sau tương tác), báo khác biệt.
- **(f)** Biến động cấu trúc bên trong nguyên cục (khác "biến" do đại vận).

### Tầng III — Ngoại cách

#### BZ-28 · Tòng cách (Tòng Tài, Tòng Sát, Tòng Nhi, Tòng Cường, Tòng Vượng) · **P0**
- **(a)** TTT chương 從象; TBCT 論外格 (đối chiếu). Nhật Chủ cực nhược, không căn, không Ấn Tỉ cứu → bỏ mình theo thế.
- **(b)** Điều kiện: Nhật Chủ không căn ở bất cứ chi nào (BZ-03), không có Ấn/Tỉ Kiếp có lực (kể cả sau tương tác), thế một hành áp đảo (Tài/Sát/Thực Thương). Ngoại lệ: có căn yếu → xét "giả tòng" (BZ-29).
- **(c)** EX4: Ất không căn thật, Kim áp đảo (Canh, Tân, Thân, Dậu ×2, Tỵ). Ứng viên **Tòng Sát**. Nhưng Ất tháng còn là Tỉ Kiên bị Canh hợp.
- **(d)** BZ-29, BZ-46 (hợp trói).
- **(e)** Tiền điều kiện: `bz.dm.level ∈ {cực nhược}` và `bz.root.dm = []` và `bz.dominant_group` đạt ngưỡng.
- **(f)** Ngoại cách không bị loại bỏ vì mặc định thân nhược phải phù.

#### BZ-29 · Chân Tòng và Giả Tòng · **P0**
- **(a)** TTT chương 真假; Chân tòng: hoàn toàn không cứu. Giả tòng: còn tia gốc/trợ nên khi vận gặp trợ thì đổi.
- **(b)** Phân loại theo số và chất của "tia cứu": căn dư khí, Ấn ẩn, Tỉ thấu bị hợp trói.
- **(c)** EX4: Ất ngày còn Ất tháng (Tỉ), nhưng bị Canh hợp → giả tòng nhiều khả năng; hai cách đọc: Tòng Sát, hoặc thân nhược cần Thủy Ấn.
- **(d)** BZ-46 (hợp trói).
- **(e)** Phân loại `chan_tong | gia_tong | khong_tong`, kèm `cuu_tia = [...]`.
- **(f)** Ví dụ điển hình cho nhu cầu hiển thị nhiều cách luận hợp lệ (BZ-85).

#### BZ-30 · Hóa khí cách · **P0**
- **(a)** TTT chương 化象; TBCT 論十干合而不合. Năm cặp hợp: Giáp–Kỷ → Thổ, Ất–Canh → Kim, Bính–Tân → Thủy, Đinh–Nhâm → Mộc, Mậu–Quý → Hỏa.
- **(b)** Điều kiện cần: (1) hợp là của Nhật Chủ với can kề sát (thường tháng hoặc giờ); (2) chi tháng thuộc hành hóa (đắc thời); (3) hóa thần có căn hoặc thấu; (4) không có can/chi khắc chế hóa thần; (5) không tranh hợp, không đố hợp; (6) Nhật Chủ không có căn mạnh của hành gốc. Ngoại lệ: thiếu điều kiện → "hợp mà không hóa" (BZ-46).
- **(c)** EX5: Giáp–Kỷ kề, tháng Mùi (Thổ), Thổ dày: sơ bộ đủ (1)(2)(3). Nhưng Thìn–Tuất xung và Tuất–Mùi hình phá Thổ; Ất ẩn trong Thìn, Mùi cho Mộc căn yếu → kết luận "hóa không trọn / giả hóa".
- **(d)** Chồng với BZ-11 (xung phá khố), BZ-50, BZ-51.
- **(e)** Hàm `check_hua(pair)` trả `{met, unmet, state ∈ chan_hoa | gia_hoa | hop_khong_hoa}`; mỗi điều kiện trả bằng chứng.
- **(f)** `relations` hiện luôn `transforms: None`. Đây là chỗ chuyển từ "có hợp" sang "hợp ra sao".

#### BZ-31 · Chuyên vượng ngũ cách · **P1**
- **(a)** Khúc Trực (Mộc), Viêm Thượng (Hỏa), Giá Sắc (Thổ), Tòng Cách (Kim), Nhuận Hạ (Thủy). TMTH, UHTB (đối chiếu).
- **(b)** Một hành áp đảo, đúng mùa, Nhật Chủ thuộc hành đó, không bị khắc phá.
- **(c)** EX5 (Giá Sắc?): Thổ dày nhưng Nhật Chủ là Giáp: không đạt điều kiện Nhật Chủ cùng hành.
- **(d)** BZ-43.
- **(e)** Cờ cho từng hành.
- **(f)** Tránh nhầm "hành mạnh" với "Chuyên vượng".

#### BZ-32 · Lưỡng thần thành tượng và hội cục thành cách · **P1**
- **(a)** TTT chương 方局, 合局; cục hội (Tam Hội) hoặc tam hợp đủ lực đổi cách đoán.
- **(b)** Tam hội/tam hợp **đủ ba chữ**, thêm can thấu cùng hành, không bị xung phá.
- **(c)** EX1 (Dần–Ngọ–Tuất): Hỏa cục đủ ba chữ, Bính thấu; Nhật Chủ Giáp bị tiết hoàn toàn.
- **(d)** BZ-47, BZ-48.
- **(e)** `bz.cuc.complete` + điều kiện thấu + không phá.
- **(f)** Nền cho dụng thần "thuận khí thế".

#### BZ-33 · Ngoại cách cổ điển và thần sát cách · **P2**
- **(a)** Lục Ất Thử Quý, Phi Thiên Lộc Mã, Tỉnh Lan Xoa, Thiên Nguyên Nhất Khí, Kim Thần, Khôi Cang, Lộc Mã… TMTH. Độ đồng thuận giữa các trường phái thấp; nhiều nhà Tử Bình hiện đại bác bỏ.
- **(b)** Mặc định tắt; bật theo `school_profile`. Luôn gắn nhãn "ít đồng thuận".
- **(c)** EX15: Ất ngày giờ Tý, không thấy Kim. Thỏa điều kiện hình thức của Lục Ất Thử Quý nhưng nội cách (Ất sinh Mão, Kiến Lộc) hoàn toàn lập được, nên ngoại cách chỉ hiển thị dạng "tham khảo".
- **(d)** Không cho phép đè lên nội cách.
- **(e)** Bảng điều kiện thuần vị trí.
- **(f)** Đầy đủ cho người nghiên cứu, mà không làm nhiễu người dùng thường.

#### BZ-34 · Phân xử nội cách – ngoại cách · **P0**
- **(a)** TBCT: nội cách trước, ngoại cách khi nội cách không lập được hoặc bị tòng/hóa đủ điều kiện. TTT nhấn mạnh Tòng/Hóa phải "chân".
- **(b)** Quy trình: chạy nội cách (BZ-14) và ngoại cách (BZ-28–BZ-32); nếu ngoại cách đạt chuẩn chân, nó **thay** nội cách; nếu chỉ "giả", giữ cả hai như hai cách đọc.
- **(c)** EX4: Tòng Sát (giả) vs Nội cách (Dậu → Thất Sát/Kiến Lộc?). Hiển thị cả hai.
- **(d)** BZ-85.
- **(e)** Bộ phân xử trong `bz_geju.py`.
- **(f)** Chống việc ngoại cách bị gán tùy tiện hoặc bị bỏ qua.

### Tầng IV — Dụng thần và Hỷ Kỵ

#### BZ-35 · Phù ức (扶抑) · **P0**
- **(a)** Phương pháp "vượng thì khắc/tiết, nhược thì sinh/trợ". Là **một** phương pháp trong nhiều, không phải mặc định (TBCT ưu tiên cách trước, TTT dùng quân bình khí).
- **(b)** Chỉ chạy khi BZ-07 cho kết quả rõ ràng và không có Tòng/Hóa. Gần biên thì xuất cả hai chiều.
- **(c)** EX6: Canh sinh Thân + Thổ Ấn + Thủy cục vượng: phù ức nghiêng về "vượng tiết", nhưng cách (Thực Thần bị Kiêu đoạt) đòi Tài chế Kiêu.
- **(d)** BZ-39 (bệnh dược), BZ-41.
- **(e)** Bảng `fuyi[level]` → danh sách thập thần Dụng/Hỷ/Kỵ. Gắn `method="phu_uc"`.
- **(f)** Tách riêng để so sánh với phương pháp khác (BZ-41).

#### BZ-36 · Điều hậu (調候) · **P0**
- **(a)** CTBG: bảng dụng thần theo can ngày × tháng sinh (120 ô). TTT 寒暖燥濕.
- **(b)** Chạy khi BZ-08 cho thấy cực hàn/nhiệt/táo/thấp, hoặc theo yêu cầu phương pháp. Ngoại lệ: cục Tòng/Hóa không áp điều hậu như cũ.
- **(c)** EX8 (Bính sinh Tý): tra bảng CTBG; Mộc/Hỏa ấm cục được chú ý, xem trực tiếp bảng sách.
- **(d)** BZ-08, BZ-42.
- **(e)** JSON 10×12 do người nhập từ sách, `verified` từng ô. Fact `bz.diaohou.yong = [can...]` + vai trò chính/phụ.
- **(f)** Lớp "Điều hậu" thiếu hoàn toàn.

#### BZ-37 · Thông quan (通關) · **P0**
- **(a)** TTT chương 通關: hai hành giao chiến thì dùng hành giữa làm cầu (Kim Mộc tranh → Thủy; Thủy Hỏa tranh → Mộc; Thủy Thổ tranh → Kim…).
- **(b)** Phát hiện "giao chiến": hai nhóm hành lực tương đương, đối khắc, kề nhau (BZ-05, BZ-13). Thông quan là hành sinh từ nhóm này và sinh ra nhóm kia.
- **(c)** EX10: Canh/Thân (Kim) đối đầu Giáp/Dần (Mộc) và Dần–Thân xung hai phía. Thủy vắng mặt nên thông quan không có sẵn; Ngọ (Hỏa) chỉ chế Kim chứ không làm cầu. Kết luận: "giao chiến, thiếu thông quan", chuyển sang bệnh dược (BZ-39).
- **(d)** BZ-13 (điểm tắc).
- **(e)** `bz.war.pairs` từ đồ thị; `bz.tongguan.candidate`.
- **(f)** Phương pháp độc lập, không quy về sinh trợ/khắc tiết.

#### BZ-38 · Dụng thần theo cách cục · **P0**
- **(a)** TBCT: dụng thần của cách theo bảng ở BZ-23, nhưng đây là phương pháp cấp cục: dụng phải có sức thật trong cục.
- **(b)** Lấy `geju_yong`, lọc bằng BZ-42.
- **(c)** EX2: Chính Quan → Tài (Quý), Ấn (Đinh); kiểm tra Quý có bị hợp (Mậu–Quý) mất lực không.
- **(d)** BZ-42.
- **(e)** `method="geju"`.
- **(f)** Là phương pháp mặc định của Tử Bình cách cục.

#### BZ-39 · Bệnh dược (病藥) · **P0**
- **(a)** Cục có "bệnh" (mất quân bình, cấu trúc phá cách) và "dược" (thứ chữa bệnh). Bệnh gồm: Kiêu đoạt Thực, Tài phá Ấn, Thương kiến Quan, Quan Sát hỗn tạp, Tỉ Kiếp đoạt Tài, thái quá/bất cập. TTT, TBCT 用神成敗救應.
- **(b)** Các "bệnh" lấy từ BZ-25/26/58–66. "Dược" là thập thần cứu theo bảng cứu.
- **(c)** EX6: bệnh = Kiêu đoạt Thực; dược = Tài (Giáp/Ất Mộc khắc Mậu) hoặc hợp, nhưng cục ít Mộc; ghi thẳng "không có dược sẵn".
- **(d)** BZ-25.
- **(e)** Danh sách `disease` đánh số, mỗi cái có `cure_gods`.
- **(f)** Hướng tới "cách dùng" mà người dùng quen: bệnh gì, thuốc gì, có thuốc hay không.

#### BZ-40 · Vai trò Dụng–Hỷ–Kỵ–Cừu–Nhàn theo từng phương pháp · **P0**
- **(a)** Truyền thống chia năm vai (用神, 喜神, 忌神, 仇神, 閑神). Hỷ là hành sinh Dụng; Kỵ là hành phá Dụng; Cừu sinh Kỵ; Nhàn không tác dụng đáng kể.
- **(b)** Với mỗi phương pháp (phù ức, điều hậu, thông quan, cách cục, tòng/hóa, bệnh dược) sinh **một bảng riêng**. Cấm hợp nhất thành một bảng duy nhất.
- **(c)** EX6: phù ức có thể cho Thủy làm Kỵ; điều hậu (mùa thu) ít cần ấm; bệnh dược cho Mộc làm dược. Ba bảng khác nhau.
- **(d)** BZ-41.
- **(e)** Dữ liệu `yongshen[method] = {yong:[], xi:[], ji:[], chou:[], xian:[]}`.
- **(f)** Hiện hoàn toàn thiếu.

#### BZ-41 · Bảng đối chiếu phương pháp và phát hiện bất đồng · **P0**
- **(a)** Các trường phái thường cho kết quả khác nhau. Phần mềm không được ngầm chọn.
- **(b)** Với từng thập thần/hành, đếm phương pháp xếp vào Dụng/Kỵ. Đồng thuận (≥ 2 phương pháp, không phương pháp nào đối nghịch) hoặc **bất đồng** (một phương pháp Dụng, một Kỵ).
- **(c)** EX6: bất đồng giữa phù ức và bệnh dược về Mộc/Thủy → hiển thị.
- **(d)** BZ-40, BZ-85.
- **(e)** Ma trận `method × god` và hàm `disagreement()`. Mỗi bất đồng có mẫu giải thích: "phương pháp A xét … nên …; phương pháp B xét … nên …".
- **(f)** Đây là cơ chế "nhận diện mâu thuẫn" và "giải thích vì sao" mà bạn đề ra.

#### BZ-42 · Kiểm tra dụng thần hữu lực · **P0**
- **(a)** TBCT: dụng thần phải có lực và không bị phá. Dụng bị hợp đi, bị xung, bị khắc, không căn thì là "dụng vô lực".
- **(b)** Với mỗi Dụng của mọi phương pháp: có hiện diện không (thấu/tàng/căn), có bị hợp trói (BZ-46), bị xung (BZ-50), bị khắc kề, bị cách vị không.
- **(c)** EX2: Dụng Quý bị Mậu hợp nhưng cách vị (nhẹ). Dụng Đinh (Ấn) bị Tý xung? Tỵ–Tý không xung; Đinh–Quý khắc nhưng cách. Kết luận chi tiết.
- **(d)** Toàn bộ tầng tương tác.
- **(e)** Hàm `yong_health(yong)` trả `{present, rooted, bound, clashed, countered}`.
- **(f)** Sự phân biệt "có Dụng" và "Dụng dùng được".

#### BZ-43 · Dụng thần trong Tòng, Hóa, Chuyên vượng (thuận thế) · **P1**
- **(a)** Với Tòng/Hóa/Chuyên vượng, dụng là **thuận** khí thế (ví dụ Tòng Sát dụng Sát, Tài; kỵ Ấn Tỉ). Hoàn toàn ngược phù ức.
- **(b)** Chạy khi BZ-34 chọn ngoại cách; chỉ khi chân. Giả thì ghi hai chiều.
- **(c)** EX4: nếu Tòng Sát, dụng Kim/Thủy, kỵ Mộc Hỏa.
- **(d)** BZ-29.
- **(e)** Bảng `waige_yong[type]`.
- **(f)** Tránh áp phù ức cho cục tòng, lỗi phổ biến.

#### BZ-44 · Dụng thần theo thời kỳ · **P1**
- **(a)** TBCT 論行運, 論喜忌: dụng thần cố định ở nguyên cục, nhưng việc hỷ hay kỵ **ở một thời kỳ** thay đổi tùy cục mở rộng (BZ-71).
- **(b)** Tính lại BZ-35–BZ-42 trên cục có can chi vận.
- **(c)** EX1 + vận Thân (xung Dần): Dụng vẫn là Thực/Sát nhưng căn Giáp ở Dần bị xung; "dụng thần động".
- **(d)** BZ-71–BZ-78.
- **(e)** `yongshen_by_luck[i]`.
- **(f)** Đây là nền cho "vai trò dụng thần qua từng thời kỳ".

### Tầng V — Can Chi tương tác

#### BZ-45 · Thiên Can ngũ hợp: các tình huống · **P0**
- **(a)** TBCT 論十干合而不合; TTT 化象. Phân loại: hóa thật, hóa giả, hợp mà không hóa, hợp bị phá, hợp trói (合絆), tranh hợp, đố hợp.
- **(b)** Hợp chỉ xét khi kề sát (BZ-05). Mỗi loại có điều kiện và hậu quả riêng: *hợp trói* = hai can giữ nhau, mất tác dụng ban đầu; *tranh hợp/đố hợp* = hai can cùng hợp một can.
- **(c)** EX4: Ất (tháng) bị Canh (năm) hợp; Ất ngày cũng muốn hợp Canh nhưng cách vị: **tranh hợp** có thể xảy ra. EX7: Nhâm hợp Đinh, nhưng Quý cũng gần: Quý–Đinh khắc.
- **(d)** BZ-30, BZ-46, BZ-53.
- **(e)** Hàm `classify_stem_combine(pair)` trả loại và lý do. Bắt buộc ghi `transforms` theo kết quả (hiện luôn `None`).
- **(f)** Thay thế dòng "tiềm năng hóa…, chưa xét hóa".

#### BZ-46 · Hợp mà không hóa / hợp trói · **P0**
- **(a)** Khi thiếu điều kiện hóa (BZ-30) thì chỉ có hiệu ứng "hợp": hai can **mất bản tính, ràng nhau**. Hiệu ứng là: cản khắc/sinh vốn có (tham hợp vong khắc).
- **(b)** Kích hoạt khi cặp hợp kề sát nhưng không đủ điều kiện hóa. Ngoại lệ: một bên bị tranh hợp.
- **(c)** EX2: Quý (Tài) hợp Mậu (Nhật Chủ) cách vị: hợp rất nhẹ. EX4: Ất tháng bị Canh hợp trói → Ất mất tư cách làm "Tỉ cứu", củng cố Tòng.
- **(d)** BZ-29 (giả tòng).
- **(e)** Cạnh `hop_troi(a,b)` làm giảm sức a và b trong BZ-54.
- **(f)** Hiệu ứng cụ thể thay cho câu chung chung.

#### BZ-47 · Tam hợp, bán hợp, củng hợp · **P0**
- **(a)** Tam hợp: Thân–Tý–Thìn (Thủy), Hợi–Mão–Mùi (Mộc), Dần–Ngọ–Tuất (Hỏa), Tỵ–Dậu–Sửu (Kim). **Bán hợp** (hai chữ) mạnh khi có chi Vượng (Tý/Mão/Ngọ/Dậu). Củng hợp (hai chữ cách một chi giữa) là dạng yếu.
- **(b)** Hiện chỉ nhận đủ ba chữ ([bazi.py:155](../engine/tvbt/bazi.py)). Thêm bán hợp (sinh–vượng hoặc vượng–mộ) kèm điều kiện thấu hành đó; cách vị giảm lực; bị xung phá hợp.
- **(c)** EX3: Tý–Thìn bán hợp Thủy (vượng–mộ, không có Thân). EX4: Tỵ–Dậu bán hợp Kim (sinh–vượng).
- **(d)** BZ-50 (xung vào chi hợp), BZ-32.
- **(e)** Bảng `semi_triad` với `strength ∈ {manh, vua, yeu}`.
- **(f)** Bắt được các cục thủy/kim thường bị bỏ sót.

#### BZ-48 · Tam hội · **P0**
- **(a)** Tam hội cùng phương: Dần–Mão–Thìn (Mộc), Tỵ–Ngọ–Mùi (Hỏa), Thân–Dậu–Tuất (Kim), Hợi–Tý–Sửu (Thủy). Lực lớn hơn tam hợp, theo TTT 方局.
- **(b)** Đủ ba chữ; hội cục thành khi có thấu và đúng mùa. Hội hai chữ (bán hội) chỉ là xu hướng.
- **(c)** EX13: Dần–Mão–Thìn tam hội Mộc, Giáp thấu năm. Với Bính, Mộc là Ấn: hội cục khiến Ấn cực nặng (BZ-66), trong khi Dần–Tỵ hình làm xao động chi Tỵ ở giờ.
- **(d)** BZ-32.
- **(e)** Kiểm tra `meeting_complete` đã có; thêm điều kiện thấu, nguyệt lệnh.
- **(f)** Nâng từ phát hiện lên đánh giá hiệu lực.

#### BZ-49 · Lục hợp và hợp hóa chi · **P1**
- **(a)** Tý–Sửu, Dần–Hợi, Mão–Tuất, Thìn–Dậu, Tỵ–Thân, Ngọ–Mùi. Hóa tương ứng (Thổ, Mộc, Hỏa, Kim, Thủy, Hỏa/Thổ tùy trường phái). Hiệu lực thấp hơn tam hợp. Nhiều trường phái nói hợp chi hiếm khi hóa.
- **(b)** Hóa chi cần can thấu cùng hành và nguyệt lệnh hỗ trợ; mặc định "hợp mà không hóa".
- **(c)** EX3: Thìn–Dậu hợp (ngày–tháng). Dậu là nguyệt lệnh Kim; Thìn bị kéo về Kim, nhưng Dậu–Mão xung kề.
- **(d)** BZ-50.
- **(e)** Bảng `liuhe` và cờ trường phái cho hóa.
- **(f)** Hiện chỉ liệt kê.

#### BZ-50 · Lục xung và hiệu lực · **P0**
- **(a)** TBCT 論刑沖會合解法: vượng xung suy thì suy bị nhổ (拔), suy xung vượng thì vượng được phát (動); xung khai khố; xung có thể bị hợp giải; kề xung nặng, cách vị nhẹ.
- **(b)** Với mỗi xung: (1) sức hai bên (BZ-03); (2) kề/cách (BZ-05); (3) có hợp giải không (BZ-52); (4) có là khố không (BZ-11); (5) có chạm nguyệt lệnh (nguyệt lệnh bị xung là điều đại sự theo nhiều sách).
- **(c)** EX3: Mão xung Dậu kề năm–tháng: nguyệt lệnh bị xung nên khí Kim (Quan) bị lung lay. EX7: Tý–Ngọ xung (năm–tháng) và Dậu–Mão xung (ngày–giờ) hai xung đồng thời.
- **(d)** Chạm cả BZ-14 (cách), BZ-42 (dụng).
- **(e)** `classify_clash(pair)` → `{effect ∈ [nhổ, động, khai_khố, giảm], notes}`.
- **(f)** Mỗi xung hiện có cùng mô tả "xung giữa trụ A và B".

#### BZ-51 · Hình, Hại, Phá (có điều kiện) · **P1**
- **(a)** Hình: Dần–Tỵ–Thân (vô ân), Sửu–Tuất–Mùi (trì thế), Tý–Mão (vô lễ), tự hình (Thìn, Ngọ, Dậu, Hợi). Hại, Phá ít quan trọng hơn trong Tử Bình; nhiều người chỉ xét khi chạm dụng thần.
- **(b)** Hình xét đủ ba chữ cho nhóm ba, hai chữ cho bán hình; hiệu lực giảm khi cách vị. Hại, Phá: mặc định "mức nhẹ", chỉ nêu khi chạm dụng/nguyệt lệnh.
- **(c)** EX2: Mão–Tý hình tháng–ngày (vô lễ), chạm nguyệt lệnh. EX5: Tuất–Mùi hình (Sửu–Tuất–Mùi thiếu Sửu, nên chỉ bán hình).
- **(d)** BZ-50.
- **(e)** Hiện có phát hiện, cần thêm trọng số và điều kiện `chạm_dụng`.
- **(f)** Tránh việc mọi hình/hại/phá được liệt kê ngang nhau.

#### BZ-52 · Hợp giải xung, xung phá hợp, tham hợp vong xung · **P0**
- **(a)** TBCT 論刑沖會合解法: một chi vừa hợp vừa bị xung thì hợp có thể giải xung (hợp thì không xung), hoặc xung phá hợp. Thành ngữ "tham hợp vong xung" cần điều kiện sức bên hợp.
- **(b)** So sánh: nếu hợp kề, xung cách → hợp thắng. Nếu xung kề, hợp cách → xung thắng. Ngang nhau → trạng thái giằng co.
- **(c)** EX3: Dậu vừa hợp Thìn (kề ngày) vừa bị Mão xung (kề năm): hợp Thìn–Dậu với xung Mão–Dậu cùng chạm nguyệt lệnh Dậu; hai bên kề ngang nhau → giằng co.
- **(d)** BZ-50, BZ-53.
- **(e)** Bộ giải trong `bz_interact.py` (xem BZ-53).
- **(f)** Là khối logic ưu tiên mà hiện chưa có.

#### BZ-53 · Bộ giải tương tác: thứ tự, kết cấu, trạng thái ròng · **P0**
- **(a)** Nhiều tương tác chồng nhau không thể xét độc lập. TBCT 論刑沖會合解法 cho các nguyên tắc ưu tiên, nhưng thứ tự cụ thể có tranh luận.
- **(b)** Thứ tự đề xuất, đặt trong `school_profile.interact_order`: (1) hội/tam hợp đủ; (2) lục hợp, can hợp; (3) xung; (4) hình; (5) hại, phá. Mỗi bước thay đổi sức chữ và có thể vô hiệu hóa tương tác sau (ví dụ chi đã vào hợp cục thì xung vào nó yếu đi). Vòng lặp đến điểm cố định (≤ 4 vòng) để tránh vô hạn.
- **(c)** EX1: Dần–Ngọ–Tuất hợp Hỏa; Dần Tuất Ngọ không xung nhau; EX6: Thân–Tý–Thìn hợp Thủy, rồi Tý–Ngọ xung: xung vào chi đã nằm trong hợp cục.
- **(d)** Đầu vào của BZ-07, BZ-35 đến BZ-42.
- **(e)** `resolve_interactions(chart) → {net_strengths, applied, overridden, ties}`, tất định, trace từng bước.
- **(f)** Đây là lõi "sinh khắc chế hóa" cấp cục.

#### BZ-54 · Tái tính khí thế sau tương tác · **P0**
- **(a)** Hợp hóa, hợp trói, hội cục, xung nhổ đều đổi sức hành. Đọc khí thế trên nguyên cục thô là sai khi có tương tác mạnh (TTT chương 戰局, 合局).
- **(b)** Sau BZ-53 tính lại BZ-06/07. Báo `delta` trước/sau.
- **(c)** EX1: Giáp thô "vượng" → sau hợp Hỏa "thiên vượng bị tiết".
- **(d)** BZ-07, BZ-85.
- **(e)** Hai lần chạy `strength`, xuất `before/after`.
- **(f)** Cho người dùng thấy **vì sao** kết luận đổi.

#### BZ-55 · Ám hợp, ám củng, củng lộc · **P2**
- **(a)** Ám hợp giữa tàng can của hai chi (ví dụ Dần–Sửu qua Giáp/Kỷ ẩn). Dùng nhiều trong Manh phái, ít trong Tử Bình chính thống.
- **(b)** Mặc định tắt, bật theo `school_profile`.
- **(c)** EX14: Dần (tàng Giáp, Bính, Mậu) và Sửu (tàng Kỷ, Quý, Tân) có ám hợp Giáp–Kỷ qua tàng can, cộng thêm Tý–Sửu lục hợp. Cần ghi rõ cặp nào là lộ (Giáp–Kỷ thiên can), cặp nào chỉ ám.
- **(d)** Không đè lên nội cách.
- **(e)** Đồ thị tàng can; cạnh `an_he`.
- **(f)** Dành cho người nghiên cứu.

#### BZ-56 · Thiên Can xung/khắc kề · **P1**
- **(a)** Giáp–Canh, Ất–Tân, Bính–Nhâm, Đinh–Quý xung. Khắc kề có lực lớn.
- **(b)** Chỉ tính kề, trừ khi có chi tọa cùng xung.
- **(c)** EX3: Đinh khắc Tân kề năm–tháng (Thương kiến Quan).
- **(d)** BZ-61.
- **(e)** Dùng `STEM_CLASH` đã có, thêm khoảng cách.
- **(f)** Khớp với BZ-05.

### Tầng VI — Thập Thần đa tầng

#### BZ-57 · Thập thần theo cung vị · **P1**
- **(a)** TBCT 論宮分用神配六親. Vị trí trụ gợi lĩnh vực: năm — tổ nghiệp, nguyệt — cha mẹ/sự nghiệp (cung quan trọng nhất), ngày — bản thân/phối ngẫu, giờ — con cái/hậu vận.
- **(b)** Khớp thập thần × cung. Chỉ là bản đồ gợi ý chủ đề, không là phán đoán.
- **(c)** EX2: Tài ở năm, Quan ở tháng, Ấn ở giờ.
- **(d)** BZ-79–BZ-82.
- **(e)** Bảng `pillar_domain`.
- **(f)** Cơ sở cho luận chủ đề.

#### BZ-58 · Quan Sát hỗn tạp và cách xử lý · **P0**
- **(a)** TBCT: Quan Sát cùng thấu là "hỗn". Cách xử lý: khử Quan lưu Sát, khử Sát lưu Quan, hợp Sát lưu Quan, hoặc Ấn hóa.
- **(b)** Kích hoạt khi Chính Quan và Thất Sát cùng thấu hoặc cùng thấu/tàng có lực. Cứu: Thực Thương chế Sát, Đinh–Nhâm hợp giữ Quan, Ấn hóa. Hợp Quan Sát với Nhật Chủ nữ có cách đọc riêng (có trường phái dùng cho lục thân).
- **(c)** EX7: Nhâm (Quan) hợp Đinh (Nhật Chủ) → "hợp Quan lưu Sát" kiểu tự nhiên; Quý (Sát) còn lại.
- **(d)** BZ-26, BZ-45.
- **(e)** Cấu trúc `hunza`, `cuu: [...]`.
- **(f)** Cấu trúc kinh điển quan trọng.

#### BZ-59 · Sát Ấn tương sinh · **P0**
- **(a)** TBCT 論偏官: Sát sinh Ấn, Ấn sinh thân.
- **(b)** Điều kiện: chuỗi Sát → Ấn → Nhật Chủ liền mạch (BZ-13), Ấn không bị Tài phá, Sát có sức. Thân quá nhược mà Ấn lại bị hợp đi thì đứt.
- **(c)** EX11: Tân (Sát, năm) → Nhâm (Ấn, tháng) → Ất (ngày), ba bậc kề nhau. Ấn không bị Tài phá (Mậu ẩn Thìn nhưng không thấu). Hợi–Mão bán hợp Mộc củng cố Nhật Chủ. Cấu trúc thành, khuyết điểm: Đinh (giờ) có thể khắc Tân nhưng cách vị.
- **(d)** BZ-64 (Tài phá Ấn).
- **(e)** Mẫu chuỗi trên đồ thị dòng khí.
- **(f)** Chuyển "cấu trúc có tên" thành truy vấn đồ thị.

#### BZ-60 · Thực Thần chế Sát · **P0**
- **(a)** TBCT: Thực Thần khắc Sát, Sát được tiết chế.
- **(b)** Điều kiện: cả hai hiện diện có lực, Thực Thần không bị Kiêu đoạt, không bị hợp đi, vị trí đủ gần để tác dụng (BZ-05). Cân sức: Thực nhẹ Sát nặng thì chế không nổi.
- **(c)** EX1: Bính (Thực) khắc Canh (Sát), cách ngày (không kề). Tam hợp Hỏa cục làm Thực quá mạnh: thành "chế thái quá".
- **(d)** BZ-65.
- **(e)** Mẫu cạnh `khắc` từ Thực tới Sát + kiểm tra `adjacency`, `strength_ratio`.
- **(f)** Cho phép nói "chế có hiệu lực hay chỉ có tên".

#### BZ-61 · Thương Quan kiến Quan · **P0**
- **(a)** TBCT 論傷官: "vi họa bách đoan" khi Thương Quan khắc Chính Quan mà không có Tài thông quan hoặc Ấn chế.
- **(b)** Điều kiện: Thương Quan và Chính Quan cùng có lực, Thương khắc được Quan (kề). Giải: Ấn chế Thương, Tài thông quan (Thương → Tài → Quan), Thương bị hợp đi. Nếu "Thương Quan tận" (không còn Quan) thì đọc theo mẫu khác.
- **(c)** EX3: Đinh kề Tân → bại; cứu bằng Ấn Quý (Tý ẩn) yếu; Tài (Mậu ẩn Thìn) cách. Kết luận "bại, cứu yếu".
- **(d)** BZ-25.
- **(e)** Mẫu bắt buộc kiểm 3 đường cứu.
- **(f)** Một trong những cấu trúc hay gặp nhất, hiện chưa nhận diện.

#### BZ-62 · Thương Quan phối Ấn và Thương Quan sinh Tài · **P0**
- **(a)** TBCT 論傷官: Thương Quan thân vượng dùng Tài; Thương Quan thân nhược dùng Ấn; Thương Quan Sát Ấn.
- **(b)** Điều kiện chọn đường theo BZ-07 và có chất Tài/Ấn tương ứng. Ngoại lệ: thân gần biên → hai đường.
- **(c)** EX12: Canh nhược sinh tháng Mùi, Quý (Thương Quan) thấu năm, Kỷ ×2 (Ấn) thấu tháng và giờ chế Thương: dạng Thương Quan phối Ấn. Nhưng Hợi–Mão–Mùi hợp Mộc cục (Tài) khắc Ấn; Thương Quan còn sinh Tài (Thủy → Mộc). Hai hình thái chồng lên nhau.
- **(d)** BZ-35.
- **(e)** Mẫu hai nhánh.
- **(f)** Phân biệt hai hình thái cho cùng "Thương Quan cách".

#### BZ-63 · Tài Quan song mỹ / Tài sinh Quan · **P1**
- **(a)** TBCT 論官, 論財: Tài sinh Quan, Quan sinh Ấn… thân đủ sức đỡ.
- **(b)** Điều kiện: chuỗi Tài → Quan liền mạch, thân vượng đủ gánh, Tỉ Kiếp không cướp Tài, Thương Quan không phá Quan.
- **(c)** EX2: Quý (Tài, năm) → Ất (Quan, tháng) kề, nhưng Quý hợp Mậu cách vị và Dậu–Mão xung phá.
- **(d)** BZ-64.
- **(e)** Mẫu chuỗi.
- **(f)** Hình thái "tốt" mà phần mềm hiện không thể nêu.

#### BZ-64 · Tài phá Ấn và Tỉ Kiếp tranh Tài · **P0**
- **(a)** TBCT: Tài khắc Ấn là bệnh của Ấn cách; Tỉ Kiếp cướp Tài là bệnh của Tài cách; "Quần Kiếp tranh Tài".
- **(b)** Điều kiện: Tài và Ấn kề khắc, hoặc Tài bị nhiều Tỉ Kiếp vây. Giải: Quan chế Tỉ Kiếp; Tỉ Kiếp cứu Ấn.
- **(c)** EX12: Mộc (Tài) cục từ Hợi–Mão–Mùi khắc Kỷ (Ấn) ở tháng và giờ: Tài phá Ấn. Cứu cần Tỉ Kiếp (Kim) hay Quan Sát chế Tài: cục chỉ có Canh (Nhật Chủ), nên cứu yếu. EX7 minh họa chiều ngược: Tỉ Kiếp vắng, Tài Canh xa.
- **(d)** BZ-17, BZ-18.
- **(e)** Mẫu cạnh + đếm Tỉ Kiếp có sức.
- **(f)** Hai "bệnh" phổ biến.

#### BZ-65 · Kiêu Thần đoạt Thực · **P1**
- **(a)** TBCT 論偏印: Thiên Ấn khắc Thực Thần.
- **(b)** Điều kiện: Thiên Ấn kề Thực Thần và khắc được; không có Tài phá Kiêu. Cứu: Tài khắc Kiêu hoặc Kiêu bị hợp.
- **(c)** EX6: Mậu (Kiêu, tháng) kề khắc Nhâm (Thực, năm); Nhâm giờ cách vị. Thủy cục (Thân–Tý–Thìn) làm Thực rất vượng nên "đoạt" không trọn.
- **(d)** BZ-47, BZ-54.
- **(e)** Mẫu cạnh.
- **(f)** Ví dụ tương tác nhiều tầng: Kiêu đoạt, tam hợp, xung.

#### BZ-66 · Thái quá – Bất cập của nhóm thập thần · **P1**
- **(a)** TTT chương 衰旺, 中和: nhóm thập thần quá vượng lại thành bệnh (Ấn nhiều che, Tài nhiều thân nhược, Thực Thương quá nhiều tiết khí).
- **(b)** Dựa vào sức nhóm sau BZ-54, so với Nhật Chủ.
- **(c)** EX1: Thực Thương nặng sau hợp Hỏa.
- **(d)** BZ-07.
- **(e)** Ngưỡng `excess` trong `school_profile`.
- **(f)** Bổ sung góc nhìn "hành nào đang thừa" thay vì "thiếu".

#### BZ-67 · Cấu trúc thập thần: danh mục thu gọn · **P1**
- **(a)** Danh mục: Sát Ấn, Thực chế Sát, Thương phối Ấn, Tài Quan, Quan Ấn tương sinh, Tỉ Kiếp phân Tài, Thân Tài đều thắng, Nhận Sát…
- **(b)** Mỗi cấu trúc là một mẫu đồ thị có điều kiện thành/bại. Việc đăng ký mẫu mới chỉ là thêm dữ liệu.
- **(c)** Như các mục BZ-58–BZ-66.
- **(d)** Chung.
- **(e)** `pattern_registry` dạng JSON: `nodes`, `edges`, `constraints`, `bai`, `cuu`.
- **(f)** Mở rộng tri thức không cần sửa code.

### Tầng VII — Tượng pháp và triết lý

#### BZ-68 · Mạch luận Tượng → Khí → Thế → Cách → Dụng → Biến · **P0**
- **(a)** Khung luận do bạn đề ra, tương ứng cách TTT đi từ thiên can, địa chi (Tượng), đến quân bình khí (Khí/Thế), cách cục, dụng thần, vận.
- **(b)** Mỗi báo cáo bắt buộc đi đủ sáu bước; bước nào thiếu dữ kiện ghi rõ "chưa đủ điều kiện để luận".
- **(c)** Mọi EX.
- **(d)** Toàn pipeline.
- **(e)** Mở rộng `B(text, layer, basis, src)` trong [analysis.py](../engine/tvbt/analysis.py) (đã có layer); thêm `depends_on` (finding ids). Báo cáo dựng theo thứ tự lớp; câu nào không truy ngược được về fact thì bị loại.
- **(f)** Biến cách trình bày hiện tại thành đường suy luận kiểm chứng được.

#### BZ-69 · Giải thích đối chứng: vì sao cùng Nhật Chủ, cấu trúc khác thì luận khác · **P1**
- **(a)** Yêu cầu giải thích của bạn (mục 6). TTT nhấn mạnh cùng can ngày nhưng cục khác nhau thì dụng khác nhau.
- **(b)** Cho hai lá số cùng Nhật Chủ, tìm các **khác biệt tối thiểu** làm đổi kết luận (tháng, tương tác, căn).
- **(c)** EX1 và EX3 cùng Nhật Chủ Giáp: EX1 Kiến Lộc, hợp Hỏa; EX3 tháng Dậu, Quan bị Thương, xung nguyệt lệnh.
- **(d)** Nhiều tầng.
- **(e)** So sánh `finding` hai lần chạy, trích các fact khác nhau dẫn tới khác biệt (đã có `compare_charts` làm khung).
- **(f)** Giải thích mang tính phản thực (counterfactual).

#### BZ-70 · Nạp âm làm lớp tượng phụ · **P2**
- **(a)** Nạp âm là hệ biểu tượng riêng (`八字真宗` pp.31-32 đã có 30 rule). Không trộn với ngũ hành chính.
- **(b)** Chỉ hiển thị ở lớp Tượng, không dùng để quyết khí thế.
- **(c)** Mọi EX.
- **(d)** Không tham gia suy luận.
- **(e)** Gắn `school=napam`.
- **(f)** Giữ nguyên ranh giới trường phái.

### Tầng VIII — Đại vận, Lưu niên, Lưu nguyệt

#### BZ-71 · Cục mở rộng: nguyên cục + vận + niên + nguyệt · **P0**
- **(a)** TBCT 論行運: vận là một trụ bổ sung; xét sinh khắc hợp xung của nó với nguyên cục như một chữ mới.
- **(b)** Tạo `chart_ext(natal, luck, year, month)` và chạy lại BZ-01…BZ-67; so với nguyên cục để lấy `delta` (cách đổi, dụng đổi, tương tác mới).
- **(c)** EX1 + vận Thân: Thân xung Dần (nguyệt lệnh) → delta lớn.
- **(d)** Toàn bộ.
- **(e)** Hàm thuần `extend(chart, pillar_list)`; bộ nhớ đệm theo `(chart_id, luck, year)`.
- **(f)** [temporal.py](../engine/tvbt/temporal.py) hiện chỉ xét cặp.

#### BZ-72 · Vận trợ cách / phá cách · **P0**
- **(a)** TBCT: vận hay cách khi hỗ trợ dụng, phá khi cản. Thí dụ Chính Quan cách gặp vận Thương Quan là phá.
- **(b)** Sau BZ-71: so sánh thành/bại/cứu trước/sau.
- **(c)** EX2 + vận Tân (Thất Sát): thành Quan Sát hỗn tạp (phá cách Chính Quan).
- **(d)** BZ-25, BZ-58.
- **(e)** `luck_effect ∈ {tro, pha, trung_tinh, doi_cach}` + lý do.
- **(f)** Đúng ý "vận trợ cách, phá cách".

#### BZ-73 · Hợp xung kích hoạt (引動) · **P0**
- **(a)** Vận/niên có thể "dẫn động" quan hệ ngủ trong nguyên cục: xung với một chữ chỉ có hợp, hợp với chữ đang bị xung, v.v. TMTH (đối chiếu).
- **(b)** Với mỗi tương tác nguyên cục, kiểm tra vận/niên có thể kích hoạt (hoàn thành tam hợp, mở khố, giải xung).
- **(c)** EX1 thiếu chỉ Hợi/Dần… (hợp Hỏa đã đủ). EX3: vận Thân (Tý–Thìn thành đủ tam hợp Thủy, Thân xung Dần? trong cục không có Dần; Thân hại?). Để test.
- **(d)** BZ-47, BZ-11.
- **(e)** Bộ phát hiện `completions(natal, ext)`.
- **(f)** Là phần "thay đổi khí thế" theo thời gian.

#### BZ-74 · Cái đầu – tiệt cước, phục ngâm, phản ngâm, thiên khắc địa xung, tuế vận tịnh lâm · **P1**
- **(a)** Truyền thống: can vận khắc chi vận (cái đầu), chi vận khắc can vận (tiệt cước); phục ngâm: vận/niên trùng trụ nguyên cục; phản ngâm: xung trụ nguyên cục; tuế vận tịnh lâm: niên trùng vận.
- **(b)** Các cờ thuần cấu trúc. Hiệu quả cụ thể tùy trường phái (có người chia vận 5/5 năm).
- **(c)** EX1 + vận Giáp Tuất là phục ngâm trụ ngày.
- **(d)** BZ-71.
- **(e)** So khớp trụ; bảng cờ.
- **(f)** Nhóm khái niệm phổ biến chưa có.

#### BZ-75 · Giao vận và thời kỳ chuyển tiếp · **P1**
- **(a)** Giao thoát (交脫): giai đoạn chuyển vận có khí của hai vận trộn.
- **(b)** Cờ chỉ ra ±1–2 năm quanh ngày khởi vận chính xác (cần tuổi thập phân).
- **(c)** Mọi EX.
- **(d)** BZ-76.
- **(e)** Dùng `start_age` thập phân đã có.
- **(f)** Tránh việc mốc vận bị cắt cứng theo năm dương lịch.

#### BZ-76 · Chuẩn hóa tuổi và niên đại vận (điều kiện tiên quyết) · **P0**
- **(a)** [temporal.py:44](../engine/tvbt/temporal.py) dùng `age = year − birth_year` nguyên rồi so `start_age` thập phân; `start_year_approx` được dùng làm mốc. Sai lệch ±1 năm làm sai vận nhưng không phải lỗi thiên văn.
- **(b)** Mọi mốc vận phải theo ngày chính xác: `luck_start_date = birth + start_age` quy đổi theo tiết.
- **(c)** Sinh gần cuối năm dương lịch.
- **(d)** Chặn mọi BZ-71 đến BZ-80 trước khi chạy đúng.
- **(e)** Hàm `luck_at(date)`.
- **(f)** Nền tảng; rẻ nhưng ảnh hưởng toàn bộ phần Biến.

#### BZ-77 · Vai trò dụng thần qua từng đại vận (dòng thời gian) · **P0**
- **(a)** TBCT 論行運, 論喜忌.
- **(b)** Với mỗi đại vận: Dụng/Hỷ/Kỵ theo từng phương pháp (BZ-40), vận hợp hay phạm.
- **(c)** EX8 + vận Mộc/Hỏa (điều hậu): thuận; vận Thủy: ngược.
- **(d)** BZ-44.
- **(e)** Bảng `timeline[luck_i][method]`.
- **(f)** Thay danh sách "thập thần của can vận" hiện nay.

#### BZ-78 · Lưu niên/lưu nguyệt theo tầng · **P1**
- **(a)** Lưu niên chạy trên nền (nguyên cục + vận). Lưu nguyệt chạy trên nền (nguyên cục + vận + niên).
- **(b)** Mỗi tầng thêm một trụ rồi gọi BZ-71. Giới hạn: không đưa ra nhận định sự kiện cụ thể.
- **(c)** EX1, năm Ngọ trên vận Thân.
- **(d)** BZ-71.
- **(e)** Đệ quy `extend`.
- **(f)** Sửa cách hiện tại chỉ xét năm/tháng so với nguyên cục.

### Tầng IX — Luận giải tổng hợp

#### BZ-79 · Bộ lập kế hoạch luận theo chủ đề · **P0**
- **(a)** Chủ đề: tính cách, năng lực, công danh, tài vận, quan hệ, gia đạo, giai đoạn đời.
- **(b)** Mỗi chủ đề là truy vấn trên đồ thị: các nút liên quan (thập thần + cung vị + dụng thần + vận), thứ tự ưu tiên theo cách. **Không** luận từng trụ hay thập thần độc lập.
- **(c)** Chủ đề công danh của EX2: Quan cách (thành nhưng bị phá) + Ấn + vị trí nguyệt trụ.
- **(d)** Gom mọi tầng.
- **(e)** `topic_plan[topic] = [pattern_ids...]`; NLG chỉ in finding nằm trong kế hoạch.
- **(f)** Thay `ch["cong-danh"]`, `ch["tai-bach"]` (hiện dựa vào vị trí Tử Vi) bằng luận Bát Tự thực.

#### BZ-80 · Công danh và Tài vận từ cấu trúc · **P1**
- **(a)** TBCT: công danh nhìn Quan Sát, Ấn, Thực Thương theo cách; tài vận nhìn Tài tinh có nguồn, có kho, có Tỉ Kiếp vây hay không.
- **(b)** Lấy từ BZ-15–BZ-20, BZ-63, BZ-64, BZ-77.
- **(c)** EX7: Tài (Canh) xa, bị Quan Sát che.
- **(d)** BZ-79.
- **(e)** Rule chủ đề có `requires: [pattern]`.
- **(f)** Luận có điều kiện.

#### BZ-81 · Quan hệ và gia đạo: lục thân · **P1**
- **(a)** TBCT 論妻子, 論宮分用神配六親. Nam: Tài là vợ; nữ: Quan Sát là chồng; Ấn là mẹ; Thực Thương là con (nữ) hoặc Quan Sát là con (nam)… Nhật chi là cung phối ngẫu.
- **(b)** Chỉ gợi ý biểu tượng; gắn nhãn "luận truyền thống". Hiệu quả biến đổi theo giới tính khai báo; có trường phái không dùng phân biệt giới.
- **(c)** EX7 (nữ giả định): Nhâm hợp Đinh ngày; Dậu cung phối ngẫu (Tân: Thiên Tài…).
- **(d)** BZ-57.
- **(e)** Tham số `gender` đã có.
- **(f)** Hiện chỉ in tàng can của nhật chi.

#### BZ-82 · Giai đoạn đời từ vận và trụ · **P1**
- **(a)** Truyền thống: năm → thời niên thiếu; tháng → thanh niên; ngày → trung niên; giờ → hậu vận; đồng thời đại vận chạy theo thứ tự.
- **(b)** Kết hợp trạng thái trụ (BZ-57) với vận (BZ-77).
- **(c)** Mọi EX.
- **(d)** Nhiều tầng.
- **(e)** `life_phase` từ `age` và `luck`.
- **(f)** Một biểu tượng thời gian phổ biến.

### Tầng X — Phản biện và so sánh trường phái

#### BZ-83 · Bộ tìm phản chứng · **P0**
- **(a)** Mỗi nhận định mang theo "điều gì có thể làm sai nó".
- **(b)** Với mỗi finding, tìm: tương tác cản, yếu tố đối nghịch (BZ-25 bại), tia cứu, ngoại lệ hợp lệ.
- **(c)** EX2: "Quan cách thành" kèm phản chứng "xung hình nguyệt lệnh".
- **(d)** Mọi tầng.
- **(e)** `counter_evidence(finding)` quét đồ thị theo cạnh `opposes`/`suppresses` (đã có trong [engine.py](../engine/tvbt/reasoning/engine.py)).
- **(f)** Tự động hóa tinh thần "phản chứng".

#### BZ-84 · Danh bạ ngoại lệ · **P0**
- **(a)** Mỗi cách và mỗi tương tác có ngoại lệ kinh điển (ví dụ ngoại lệ hóa; hợp giải xung).
- **(b)** Ngoại lệ là `exceptions` của rule (đã hỗ trợ), kèm ghi chú nguồn.
- **(c)** Như BZ-30.
- **(d)** Chung.
- **(e)** Mở rộng schema thêm `exception_note`.
- **(f)** Giữ các ngoại lệ ở dạng dữ liệu có nguồn.

#### BZ-85 · Nhiều cách luận cùng hợp lệ · **P0**
- **(a)** TTT nhận có thể thấy "chân" hay "giả". Phần mềm phải nói rõ khi hai đường đọc đều có cơ sở.
- **(b)** Khi biên BZ-07 nhỏ, hoặc BZ-34 giữ hai cách, hoặc BZ-41 có bất đồng: xuất `readings = [R1, R2]` kèm điều kiện nào làm R1 thắng R2.
- **(c)** EX4: Tòng Sát (R1) và thân nhược dụng Ấn (R2).
- **(d)** BZ-29, BZ-34, BZ-41.
- **(e)** Tập `Reading` với `prerequisites`, `consequences`, `would_be_chosen_if`.
- **(f)** Trung thực về giới hạn thay vì ép một đáp án.

#### BZ-86 · Cô lập trường phái · **P0**
- **(a)** Không trộn quy tắc giữa Tử Bình cách cục, điều hậu, phù ức, tượng pháp, Manh phái.
- **(b)** Mỗi rule có `schoolId`. Engine chỉ phân xử trong cùng trường phái. Báo cáo phân nhóm theo trường phái và có "bảng so sánh".
- **(c)** EX6: Cách cục nói Kỵ Thiên Ấn; điều hậu không nhấn.
- **(d)** BZ-41.
- **(e)** Mở rộng `resolve()` để khóa theo `schoolId`.
- **(f)** Đáp ứng "không trộn quy tắc giữa các trường phái".

#### BZ-87 · Nhãn mức chắc chắn và chặn dự báo · **P0**
- **(a)** Phần 1.6–1.7.
- **(b)** Bộ lọc NLG: cấm cụm dự báo ("sẽ", "chắc chắn", "năm X xảy ra…"); mỗi câu mang một nhãn; phần về vận luôn kèm chú thích "luận truyền thống".
- **(c)** Mọi báo cáo.
- **(d)** Hậu xử lý toàn bộ.
- **(e)** Lint tĩnh trên đầu ra NLG (regex + từ điển) và test.
- **(f)** Ngăn việc nâng độ chắc chắn ngoài khả năng.

#### BZ-88 · Bộ mệnh lệ kiểm thử theo kinh điển · **P0**
- **(a)** TBCT, TTT, UHTB, TMTH đều kèm mệnh lệ (ví dụ lá số và kết luận của tác giả).
- **(b)** Mỗi mệnh lệ là test: `chart → expected cách, dụng, thành/bại` theo sách. Đo **độ trung thành với sách**, không phải độ chính xác tiên đoán.
- **(c)** Chọn từ sách, đối chiếu thủ công.
- **(d)** Chạy cho từng `school_profile`.
- **(e)** Mở rộng `test_bazi_book_golden.py` (đã có khung golden).
- **(f)** Cách duy nhất để nâng chất lượng mà không tự thuyết phục mình.

#### BZ-89 · Kiểm thử bất biến và biến đổi · **P1**
- **(a)** Tính chất phải đúng bất kể chart: tất định; đổi `school_profile` thì kết quả đổi đúng chỗ; hoán đổi âm dương đối xứng cho kết quả đối xứng; thêm tương tác chỉ làm đổi các fact phụ thuộc.
- **(b)** Property-based test, ví dụ 10k lá số ngẫu nhiên (đã có `test_fuzz_pipeline.py`).
- **(c)** Ngẫu nhiên.
- **(d)** Tầng 1–6.
- **(e)** Bổ sung bất biến cho analyzer mới.
- **(f)** Chống hồi quy khi thêm quy tắc.

---

## 4. Tổng kết ưu tiên

**P0 (59 mục, làm trước, quyết định chất lượng luận):** BZ-01–08, 13–21, 23, 25–26, 28–30, 34–42, 45–48, 50, 52–54, 58–62, 64, 68, 71–73, 76–77, 79, 83–88.

**P1 (29 mục, mở rộng và tinh chỉnh):** BZ-09–12, 17–18, 22, 24, 27, 31–32, 43–44, 49, 51, 56–57, 63, 65–67, 69, 74–75, 78, 80–82, 89.

**P2 (3 mục, cho người nghiên cứu, mặc định tắt):** BZ-33, 55, 70.

(BZ-17 và BZ-18 xuất hiện ở cả P0 và P1 vì nửa Chính và nửa Thiên khác mức ưu tiên.)

### Lộ trình triển khai gợi ý

1. **Giai đoạn A, nền (P0, không đổi giao diện):** BZ-76, BZ-01–05, BZ-13. Xuất fact mới và trace, viết test golden bảng.
2. **Giai đoạn B, thế và tương tác:** BZ-45–54, BZ-06–08. Có cục sau tương tác và thang vượng nhược có biên.
3. **Giai đoạn C, cách và dụng:** BZ-14–26, BZ-28–30, BZ-34–42. Lúc này mới thay các dòng "chưa có quy tắc cách cục".
4. **Giai đoạn D, biến:** BZ-71–77.
5. **Giai đoạn E, tổng hợp và phản biện:** BZ-79–89.

Nên nhập liệu có nguồn (bảng điều hậu 10×12, bảng tư lệnh, bảng thành–bại–cứu) trước khi viết rule, và đánh dấu từng ô `draft` cho đến khi có người đối chiếu văn bản gốc, đúng quy trình của các pack hiện có.

---

## 5. Giới hạn của đề xuất này

- **Chưa kiểm văn bản gốc.** Tên chương lấy từ hiểu biết chung về các sách, không phải từ bản scan trong repo. Mọi "đối chiếu" cần người xác minh trước khi gán `verified`.
- **Một số thứ tự ưu tiên (mục 1.5, BZ-53) là lựa chọn thiết kế.** Chúng được đặt trong `school_profile` và hiển thị, không giả vờ là quy luật kinh điển.
- **Ví dụ EX1–EX8 là cấu trúc minh họa**; nhận xét về từng ví dụ minh họa cách quy tắc kích hoạt, không phải kết luận về mệnh.
- **Mục tiêu "chuyên gia" nghĩa là trung thành và nhất quán với kinh điển.** Nó không nghĩa là tiên đoán chính xác.

---

## 6. Phụ lục: kiểm tra tính hợp lệ của EX1–EX8

Mỗi lá số được kiểm bằng script (đã chạy lại sau khi thêm EX9–EX15, tất cả đạt): (1) Can Chi mỗi trụ cùng âm dương; (2) Can tháng khớp ngũ hổ độn theo Can năm; (3) Can giờ khớp ngũ thử độn theo Can ngày. Đã chạy khi soạn tài liệu.
