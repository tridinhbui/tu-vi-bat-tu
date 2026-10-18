# Đề xuất nâng cấp chiều sâu luận giải Tử Vi (symbolic rule engine, không LLM)

Phạm vi: chỉ phần Tử Vi Đẩu Số; Bát Tự giữ nguyên. Tài liệu này dựa trên việc đọc `engine/tvbt/{tuvi,analysis,van_han,temporal}.py`, `knowledge/{schema,dsl}.py`, `reasoning/{engine,facts,conflict}.py` và toàn bộ `engine/data/pack_*.json`.

**Quy ước trung thực.** Tử Vi là hệ thống biểu tượng truyền thống, chưa được kiểm chứng như dự báo khoa học. Phần mềm chỉ được nói “theo sách X, cấu trúc này được đọc là Y”, không nói “sẽ xảy ra”. Mọi quy tắc dưới đây tôi nêu từ kiến thức chung về Tử Vi; **chưa quy tắc nào được đối chiếu với trang sách cụ thể**, nên tất cả vào kho ở trạng thái `draft` cho tới khi có `locator` thật (đúng cơ chế `validate_pack` hiện có: `verified` đòi nguồn đã `verified`). Cột “nguồn cần xác minh” chỉ là gợi ý nơi tìm, không phải trích dẫn.

---

## 1. Chẩn đoán hiện trạng (số liệu thật)

| Hạng mục | Hiện có | Hệ quả |
|---|---|---|
| Luật | 418 luật, 12 gói; ~414 luật chỉ phát `finding`, **4** luật `assert` | Suy luận nhiều bước gần như không dùng: engine có forward-chaining nhưng kho luật hầu như phẳng |
| Hiệu ứng | 338 `support`, 73 `neutral`, **3** `limit` | Gần như không có luật phản chứng/chế hóa; phần “phản biện” chủ yếu là câu chung trong `analysis.py` |
| Ngoại lệ | **0** luật có `exceptions`, **0** có `conflictsWith` | Mọi cách cục đều “thành” khi đủ sao, không bao giờ “phá” |
| Phạm vi luật | gần như toàn bộ `subject: palace`, hầu hết khóa vào cung Mệnh | Quan Lộc, Tài, Phúc, Di, Thân, liên cung chỉ có rải rác |
| Trường phái | 1 trường phái dùng thật (`vn_dlhc_draft`); `vn_tan_bien_draft`, `tu_binh_draft` chỉ là khung | Chưa có cơ chế chọn/tách trường phái ở tầng luận |
| Độ sáng | bảng cho 14 chính tinh + 24 phụ tinh (`dignity_aux.json`, xem `docs/AUX-DIGNITY.md`) | Khôi Việt, Đào Hồng Hỷ, Quang Quý, Thai Tọa… không sách nào xếp miếu/hãm: để trống |
| Sao tính được | 14 chính tinh, Tả Hữu, Xương Khúc, Lộc Tồn, Kình Đà, Khôi Việt, Mã, Hỏa Linh, Kiếp Không, Đào Hồng Hỷ, Thiên Không, vòng Thái Tuế, vòng Bác Sĩ, vòng Trường Sinh, Tuần/Triệt | Thiếu cả một lớp trung tinh (xem 2.1) |
| Vận hạn | đại hạn (cung + can cung), tiểu hạn (cung), 5 bước Khảo Luận pp.230–233, `van_han.read` (khoảng 15 câu if-else) | Không có lưu niên Tử Vi thật sự, không lưu Tứ Hóa, không lưu tinh, không Tứ Hóa theo can cung đại hạn dù `dai_han[].stem` đã có |
| Tổng hợp | `analysis.py` là bản mẫu viết tay theo chương (tính cách, công danh…), **tách khỏi** rule engine | Hai đường song song: câu trong `analysis.py` không có provenance/exception/conflict của engine |

**Gốc vấn đề (bốn thiếu hụt cấu trúc):**

1. **Fact quá phẳng.** `palace.tam_phuong_stars` gộp bản cung + tam hợp + xung chiếu. Không thể viết “sao A đồng cung, sao B xung chiếu, sao C tam hợp” thành ba điều kiện khác nhau, trong khi toàn bộ khái niệm “đồng cung / hội chiếu / xung chiếu / giáp” phụ thuộc điều đó. Câu luật hiện ghi: “‘Hội/gặp’ = trong tam phương (our reading)”.
2. **DSL chỉ nói về một cung.** Không có phép tham chiếu cung khác (Mệnh–Quan–Tài–Di, Phúc–Phối–Di, Mệnh–Thân), không đếm, không so sánh thứ bậc độ sáng.
3. **Cách cục không phải thực thể.** Hiện “cách” chỉ là một finding bình thường. Không có trạng thái thành / bán thành / phá / được cứu / biến.
4. **Chưa có tầng dụng–biến thống nhất.** Tứ Hóa chỉ tra bảng can–năm; vận hạn là if-else rời; không có “khí” (cát/hung/độ sáng tổng hợp theo cung) làm lớp trung gian cho các luật cấp cao.

---

## 2. Các tầng tri thức còn thiếu

Sắp theo thứ tự phụ thuộc. Mỗi tầng ghi: **Dữ liệu / Thuật toán / Quan hệ / Logic** cần bổ sung.

### 2.1 Tầng L0 — Sao và bảng tra còn thiếu (Tượng)

- **Dữ liệu cần thêm (sao an theo công thức, cần xác minh từng công thức):** Thiên Hình, Thiên Riêu, Thiên Y; Thiên Thương, Thiên Sứ (cố định theo cung Tật Ách/Nô); Thai Phụ, Phong Cáo; Tam Thai, Bát Tọa; Ân Quang, Thiên Quý; Long Trì, Phượng Các; Giải Thần, Thiên Giải, Địa Giải; Thiên Quan, Thiên Phúc; Quốc Ấn, Đường Phù; Thiên Tài, Thiên Thọ; Cô Thần, Quả Tú; Phá Toái; Thiên Đức, Nguyệt Đức; Lưu Hà; Thiên La, Địa Võng (theo vị trí Thìn/Tuất); Hoa Cái; Kiếp Sát; Đẩu Quân.
- **Độ sáng bổ sung:** Linh Tinh, Địa Không, Địa Kiếp, Lộc Tồn, Tả Hữu, Khôi Việt, Thiên Mã, Đào Hồng, Thiên Hình, Thiên Riêu… (nhiều sao “chỉ có vị trí, không có miếu hãm” thì ghi rõ `n/a`, đừng điền bừa).
- **Hồ sơ sao (`star_profiles.json`) chỉ có 14 chính tinh.** Cần hồ sơ có cấu trúc cho phụ tinh: hành, âm dương, tính cát/hung/biến, “đầu”/nhóm (Nam Đẩu / Bắc Đẩu / Trung Thiên), chủ đề (quyền, tài, danh, tình, bệnh), cung có ý nghĩa đặc biệt.
- **Phân loại sao thành thuộc tính tính toán được** (đây là nền cho mọi luật cấp cao): `nature ∈ {cát, hung, trung, sát, bại, đào hoa, quý nhân, văn tinh…}`, `element`, `polarity`, `dau`, `family` (Tử Phủ Vũ Tướng, Sát Phá Liêm Tham, Cơ Nguyệt Đồng Lương, Cự Nhật…). Một bảng `star_attrs.json` thay cho các danh sách `CAT`, `SAT`, `GROUPS` đang nằm rải rác trong code.

### 2.2 Tầng L1 — Quan hệ vị trí có kiểu (Thế)

Thay vì một tập `tam_phuong_stars`, sinh các fact **theo vai** cho mỗi cung `P`:

| Fact | Định nghĩa |
|---|---|
| `rel.self.stars` | sao đồng cung |
| `rel.opp.stars` | cung xung chiếu (đối, +6) |
| `rel.trine1.stars`, `rel.trine2.stars` | hai cung tam hợp (+4, +8), giữ riêng từng cung |
| `rel.flank_prev.stars`, `rel.flank_next.stars` | hai cung giáp (−1, +1), **tách trái/phải** (giáp cung cần “một sao mỗi bên”) |
| `rel.nhi_hop.stars` | cung nhị hợp / lục hợp (Khảo Luận p.230–233 đã dùng cho đại hạn) |
| `rel.cross`, `rel.tam_phuong_tu_chinh` | gộp có nhãn vai, vẫn giữ để tương thích luật cũ |

- **Vô chính diệu mượn sao đối cung (an tinh nhập cung):** thuật toán “mượn” có hệ số (sao xung chiếu vào bản cung bị giảm lực) và có ghi chú `borrowed=true` trong provenance. Hiện chỉ có câu văn trong `analysis.py`, không có fact.
- **Fact độ sáng có thứ bậc:** `dignity_rank` 0–4 (hãm→miếu) để so sánh “≥ đắc”, đếm “hai sao cùng đắc”, tránh liệt kê thủ công như `["miếu","vượng","đắc"]` trong từng luật.
- **Fact Tuần/Triệt có vị trí tương đối:** Tuần/Triệt *ở bản cung* khác với *ở xung chiếu*; một số luật phản ứng khác nhau (xem R-B).

### 2.3 Tầng L2 — Khí: trạng thái tổng hợp từng cung (Khí)

Lớp trung gian chưa tồn tại. Tính một **hồ sơ khí** (ordinal, không cộng điểm) cho mỗi cung, từ L1:

`cat_count / sat_count` (trọng số theo vai: đồng cung > xung chiếu > tam hợp > giáp), `best_major_dignity`, `has_tuan`, `has_triet`, `hoa_set` (Lộc/Quyền/Khoa/Kỵ rơi vào cung và vai nào), `van_tinh_dac_biet` (Lộc Tồn, Mã, Hình, Riêu…), `emptiness` (vô chính diệu, Không Kiếp đóng), `support_level ∈ {yếu, trung, mạnh}`.

Mỗi giá trị được **derive** bằng luật (kiểu `assert`), nên mọi câu luận cấp trên truy ngược được qua `why()`. Chuyển `reach_note()` (hiện chỉ in câu) thành các fact này.

### 2.4 Tầng L3 — Cách cục là thực thể có vòng đời (Cách)

Thêm schema riêng, không nhét vào `KnowledgeRule` phẳng:

```json
{
  "id": "CACH_...", "school": "...", "kind": "cat|hung|bien",
  "anchor": {"palace": "Mệnh", "alt_palaces": ["Thân"]},
  "core":      { /* điều kiện cần để cách hiện hình */ },
  "boosters":  [ /* tăng thế: tên sao + vai */ ],
  "breakers":  [ /* phá cách: sao/hóa/Tuần Triệt + vai */ ],
  "rescuers":  [ /* giải cứu phá cách: ví dụ Triệt gặp sát tinh, Tuần ... */ ],
  "transforms":[ /* biến cách: khi X thì cách đổi thành cách Y */ ],
  "refutations":[ /* phản chứng: dấu hiệu cho thấy cách chỉ còn hình thức */ ],
  "sources": [...], "reviewStatus": "draft"
}
```

Trạng thái đầu ra (chuỗi có thứ bậc, không phải điểm): `không_hiện` → `hình_thức` (chỉ có core) → `thành` (core + ≥1 booster, không breaker) → `thành_thượng` → `bị_phá` → `phá_được_cứu` → `biến_thành:<cách khác>`. Ở UI luôn in kèm nguyên nhân (booster nào, breaker nào, ai cứu).

### 2.5 Tầng L4 — Tứ Hóa tĩnh và tương tác (Biến, bản mệnh)

- **Biến thể bảng Tứ Hóa theo trường phái** (hiện chỉ một bảng `TU_HOA`; bản thân code đã gặp lỗi in ở bảng Khảo Luận). Cần `tu_hoa_tables.json` có `schoolId`, từng can có thể có ≥2 biến thể được ghi nhận (các can thường bị tranh luận: Canh, Mậu, Nhâm, Quý… — **phải đối chiếu từng sách**, không tự điền).
- **Fact vị trí hóa theo vai** (hóa ở đồng cung/tam hợp/xung chiếu/giáp của cung X), nền cho “Lộc Quyền Khoa hội”, “Kỵ xung Mệnh”, “Lộc Kỵ giao nhau”.
- **Quan hệ giữa hai hóa:** Lộc–Kỵ đồng cung/xung nhau; Quyền–Kỵ; Khoa giải Kỵ; “Tam Hóa liên châu” (ba hóa ở ba cung liền kề); “Song Lộc” (Hóa Lộc + Lộc Tồn).
- **Hóa × độ sáng của chính sao hóa:** Hóa Lộc cho sao hãm khác Hóa Lộc cho sao miếu (đây là lõi của “cùng sao, khác cấu trúc → khác cách luận”).

### 2.6 Tầng L5 — Phi Hóa (trường phái riêng, không trộn)

Phi Hóa dùng **can của cung** để bay Tứ Hóa tới cung khác (trường phái Phi Tinh/Tứ Hóa; không thuộc truyền thống Tam Hợp VN trong kho hiện tại). `dai_han[].stem` và `palaces[].stem` đã có, nên dữ liệu gốc sẵn sàng.

- **Dữ liệu:** bảng Tứ Hóa theo can (cùng bảng L4 nhưng gắn `schoolId = phi_tinh_*`), danh sách “chủ đề” từng cung.
- **Thuật toán:** `fly(from_palace, hoa) → (star, to_palace)`; tập cạnh có hướng `from → to` với nhãn Lộc/Quyền/Khoa/Kỵ; phát hiện **tự hóa** (sao của cung tự hóa bằng can của chính cung), **xung phi** (hóa bay sang cung đối), **hóa ngược** (A phi Lộc vào B, B phi Kỵ vào A).
- **Cách ly trường phái:** mọi fact `phi.*` sống trong namespace riêng; luật `tam_hop.*` không đọc được `phi.*` (kiểm ở `validate_pack`). Giao diện phải gắn nhãn trường phái từng đoạn.

### 2.7 Tầng L6 — Liên cung và chủ đề (Thế → Dụng)

Hiện mỗi chương lấy 1–2 cung. Cần **công thức chủ đề** (topic recipe) khai báo bằng dữ liệu, không viết tay trong Python:

- Tính cách: Mệnh + Thân + Phúc Đức + (Phụ Mẫu cho ảnh hưởng thuở nhỏ).
- Công danh: Quan Lộc + Mệnh + Tài + Thiên Di (tam phương Mệnh) + Phúc.
- Tài: Tài Bạch + Điền Trạch + Phúc + Mệnh; vị trí Lộc Tồn/Hóa Lộc.
- Hôn nhân: Phu Thê + Thiên Di (xung) + Phúc + Mệnh/Thân.
- Phúc đức–gia đạo: Phúc, Phụ Mẫu, Huynh Đệ, Điền Trạch, Tử Tức.
- Mệnh–Thân: so sánh hai cung (cùng cung / khác cung; Thân cư Quan, Tài, Phu, Di, Phúc, Mệnh), luận “tiên thiên vs hậu thiên”.

Thuật toán: với mỗi chủ đề, gom `finding` của các cung trong công thức, nhóm theo **chủ đề–vai cung** (chủ/hỗ trợ/đối chiếu), rồi xuất cấu trúc: *luận đề chính, chứng cứ ủng hộ, yếu tố hạn chế, phản chứng, lưu ý trường phái* — không cộng điểm, mà theo **thứ tự thống trị có giải thích** (xem 3.4).

### 2.8 Tầng L7 — Vận hạn đa tầng (Biến, động)

Thiếu so với `temporal.py`/`van_han.py` hiện tại:

- **Lưu niên Tử Vi:** lưu Mệnh = cung của địa chi năm xem (Thái Tuế); xây lại 12 cung “lưu” chồng lên 12 cung bản mệnh.
- **Lưu Tứ Hóa** theo can năm xem; chồng lên sao bản mệnh và Tứ Hóa bản mệnh (Lộc lưu gặp Kỵ bản, Kỵ lưu xung Mệnh…).
- **Lưu tinh:** lưu Lộc Tồn/Kình/Đà, lưu Khôi Việt, lưu Xương Khúc, lưu Mã (theo can/chi năm) — cần quy tắc xác minh.
- **Tứ Hóa đại hạn theo can cung đại hạn** (đã có `stem`), chồng lên bản mệnh.
- **Ma trận tương tác bốn tầng:** bản mệnh – đại hạn – lưu niên – (tiểu hạn/nguyệt hạn). Khái niệm “trùng điệp”: Đại hạn Mệnh trùng Lưu Mệnh; hai Kỵ gặp nhau; Lộc đại hạn gặp Lộc lưu niên; Kình/Đà chồng lên nhau (“Song Kình/Song Đà”).
- **Hạn–thế–cách:** đại hạn đi vào cung làm *kích hoạt* hay *phá* một cách cục bản mệnh (cách cục có `activation_palaces`).
- **Chỗ sai/yếu cần sửa:** `van_han.read` mã hóa cứng ~15 điều kiện, có nhánh `pass` vô tác dụng và biểu thức chết (`h in {x["star"] for x in []}`). Nên chuyển toàn bộ thành luật dữ liệu có `exceptions`.

### 2.9 Tầng L8 — Phản biện có cấu trúc (Phản)

Mỗi luật mang thêm: `supports` (sao/hóa làm tăng), `limiters` (chế hóa), `counter_evidence` (dấu hiệu trái ngược nên trình bày cùng), `exceptions` (vô hiệu hóa khi…), `non_activation` (điều kiện khiến cách không phát: ví dụ Tuần/Triệt đúng chỗ, độ sáng hãm, Kình Đà đồng cung Mệnh, Tứ Hóa phá, vận hạn không kích hoạt). Hiện chỉ ba luật có `limit`.

### 2.10 Tầng L9 — Trường phái và nguồn

- Mỗi luật có `schoolId` thật sự dùng được: `tam_hop_vn` (Thực Hành/Khảo Luận/Toàn Thư đang dùng), `phi_tinh`, `trung_chau`, khác. Engine chạy theo *một* trường phái được chọn (hoặc chạy song song, in hai cột), không bao giờ trộn.
- `Source` cần thêm: `edition`, `trường phái`, `độ cổ` (cổ thư / thế kỷ XX), `ý kiến khác` (liên kết `disputedBy`). Hiện `disputed` trong `REVIEW` chưa luật nào dùng.
- Quy tắc trung thực: luật chỉ nêu trong một sách → in “theo sách X”; có ≥2 sách đồng ý → `corroborated`; có sách bác → `disputed` và in cả hai (cơ chế `_merge_corroborated` đã có ở `api.py`, mở rộng cho mâu thuẫn).

---

## 3. Nâng cấp engine (làm trước khi nạp luật mới)

### 3.1 Fact và DSL

1. Thêm fact theo vai L1 và `dignity_rank`; giữ fact cũ để 418 luật hiện có chạy không đổi (test `test_book_golden`, `test_khao_luan_rules` bảo vệ hồi quy).
2. Toán tử mới: `count_gte/lte`, `subset`, `intersects`, `between`, `rank_gte`.
3. **Tham chiếu cung:** `{"palace": "Quan Lộc", "relation": "opp", "fact": "stars", "operator": "contains", "value": "Hóa Kỵ"}`; `relation ∈ self|opp|trine|flank_prev|flank_next|nhi_hop`. Validate ở `dsl.validate`; evaluate trong ngữ cảnh toàn lá số, không chỉ cung hiện tại.
4. **Biến lượng hóa:** `{"exists": {"palace": {"in": ["Mệnh","Quan Lộc","Tài Bạch"]}, ...}}`.
5. Facts thời gian: `time.year`, `time.age`, `time.dai_han.palace`, `time.luu_nien.palace`, `time.luu_hoa.*` → cho luật vận hạn cùng DSL với luật tĩnh (hiện hai thế giới).

### 3.2 Schema luật

- Thêm `layer ∈ Tượng|Khí|Thế|Cách|Dụng|Biến|Phản|Tổng`, `topic`, `formation` (3.3), `strength ∈ {1..4}` thứ bậc (không cộng), `counter_evidence_id[]`, `activation` (tĩnh / cần hạn kích hoạt).
- Consequence mới: `modulate` (tăng/giảm một claim cụ thể, bắt buộc nêu lý do), `cancel` (phá cách, ghi `breaker`), `transform` (biến cách), `rescue` (giải phá).

### 3.3 Cách cục là thực thể (xem 2.4)

Bộ đánh giá `formation.evaluate()` trả `status`, `evidence[]`, `breakers_found[]`, `rescuers_found[]`, `missing_for_next_level[]` (cho phép UI nói “thiếu gì để thành”).

### 3.4 Tổng hợp không cộng điểm

Thay `resolve()` (chỉ dựa độ đặc thù + verified) bằng ba bước:

1. **Thứ tự thống trị có giải thích:** phá cách / Kỵ xung / sát tinh miếu ở tam phương *giới hạn* (không xóa) cách cát; Tuần/Triệt đúng vị trí *giải* sát tinh.
2. **Chế hóa có chỉ định** (`modulate` có nguồn), không suy diễn.
3. **Mâu thuẫn còn lại** được đưa ra thành mục “điểm tranh chấp” kèm cả hai nguồn, không chọn thay người đọc.

### 3.5 Hợp nhất `analysis.py` với engine

Chuyển từng đoạn viết tay sang luật `layer=Tổng/Tượng` hoặc “topic recipe”, để câu nào cũng có `why()` và có thể bị `exceptions` làm im. Không bỏ nội dung câu văn; chỉ đổi nơi nó được sinh ra.

### 3.6 Kiểm thử bắt buộc

Golden tests theo lá số có lời giải trong sách (đã có kiểu `test_book_golden`); thêm: mỗi cách cục ≥1 lá số “thành”, ≥1 “phá”, ≥1 “được cứu” (lá số tự tạo bằng cách chỉnh giờ/ngày sinh để kích hoạt, ghi rõ là *thử nghiệm cấu trúc*, không phải ví dụ sách); test “trường phái không rò rỉ”; test “luật `verified` không có `locator`” (đã có).

---

## 4. Khung Tượng → Khí → Thế → Cách → Dụng → Biến

Pipeline suy luận mới (mỗi mức chỉ đọc mức dưới):

| Mức | Câu hỏi | Đầu ra | Ví dụ |
|---|---|---|---|
| **Tượng** | Sao này tượng trưng gì? | `star_attrs` + hồ sơ | Thái Dương: quang minh, ban phát, quý khí; ngược lại hãm: mờ tối, hao mình vì người |
| **Khí** | Sao ở trạng thái nào? | `dignity_rank`, Tuần/Triệt, sao đồng cung theo `nature`, `cat/sat_count` | Thái Dương miếu ở Ngọ, không sát tinh → khí mạnh, sáng |
| **Thế** | Thế đứng trong tam phương tứ chính + giáp? | các fact `rel.*`, hồ sơ khí từng cung | Nhật ở Mệnh, Nguyệt ở Tài, Cự ở Quan… |
| **Cách** | Có tạo thành cấu trúc cổ điển không, thành hay phá? | `formation.status` | “Nhật Nguyệt tịnh minh” thành / hình thức |
| **Dụng** | Theo cách này, hướng dụng/đường ứng xử nào được sách nêu? | luận đề theo chủ đề | thiên về danh, hay thiên về tài, hay thiên về học |
| **Biến** | Vận hạn kích hoạt hay phá? | tương tác bản–đại–lưu | đại hạn Kỵ xung, lưu Lộc hội… |

**Vì sao cùng một sao khác cách luận** — cơ chế phải hiện ra trong output (không chỉ ghi trong tài liệu): ví dụ “Thái Dương ở Mệnh” sẽ đổi luận theo (a) độ sáng (Ngọ/Mão sáng, Tuất hãm), (b) sao đồng cung (Cự Môn đồng cung Sửu/Mùi là thế khác), (c) có Hóa Kỵ không, (d) tam phương có Nguyệt sáng không, (e) Tuần/Triệt đúng vị trí không, (f) đại hạn có kích hoạt hay không. Mỗi (a)–(f) là một nhánh luật có điều kiện và ngoại lệ ghi rõ; đầu ra in “vì sao đọc như vậy”.

---

## 5. Danh mục quy tắc đề xuất (88 nhóm, theo ưu tiên)

Ký hiệu: **P0** làm ngay (nền tảng, nhiều luật hưởng lợi); **P1** giá trị cao; **P2** tiếp theo; **P3** hiếm/nâng cao hoặc cần thêm nguồn. Mọi dòng mặc định `draft`; “Ngoại lệ/chế hóa” là điều kiện **cần kiểm tra trong sách**, không khẳng định đã đúng. “Ví dụ” là mô tả cấu trúc để tạo test, không phải lá số trong sách.

Viết tắt vai: **Đ**=đồng cung, **X**=xung chiếu, **T**=tam hợp, **G**=giáp, **Tp**=tam phương tứ chính (Đ+X+T).

### 5.A — Cách cục chính tinh (đối tượng Mệnh; mở rộng sang Thân và cung đối)

| ID | Cách (điều kiện lõi) | Ngoại lệ / chế hóa cần xác minh | Ví dụ cấu trúc | Nguồn cần xác minh |
|---|---|---|---|---|
| A01 P0 | Tử Phủ Vũ Tướng triều viên: Tử Phủ Vũ Tướng đủ trong Tp Mệnh | Phá bởi Kình/Đà/Không/Kiếp đồng cung các sao chính; Tuần/Triệt đồng cung | Mệnh Tý + Tp có 4 sao | Toàn Thư, Thực Hành, Khảo Luận |
| A02 P0 | Tử Phủ đồng cung (Dần/Thân) | Kình/Hỏa/Linh/Không Kiếp đồng cung → hạ cách | Mệnh Dần Tử Phủ | cổ phú về Tử Vi |
| A03 P0 | Phủ Tướng triều viên (Phủ + Tướng trong Tp) | Tướng hãm hoặc Tướng gặp Kình/Triệt | Mệnh Thiên Phủ, Tướng ở tam hợp | Toàn Thư |
| A04 P0 | Cơ Nguyệt Đồng Lương (≥3 sao trong Tp, Mệnh dùng Tp) | Thiếu Xương Khúc/Khoa/Quyền → chỉ “hình thức”; Không Kiếp, Kình Đà phá | Mệnh Dần, Cơ Nguyệt Đồng Lương đủ | Khảo Luận pp.230+ (đã dùng một phần ở `van_han`) |
| A05 P0 | Sát Phá Liêm Tham (≥3 sao Tp) | Cần cát tinh hội (Khoa Quyền Lộc, Xương Khúc, Tả Hữu) mới “thành”; có Hóa Kỵ/Tuần Triệt sai chỗ → bại | Mệnh Thân Thất Sát | Toàn Thư, Khảo Luận (nhóm này đã có phát hiện sơ khởi) |
| A06 P0 | Cự Nhật (Cự Môn + Thái Dương Tp) | Cự Môn gặp Hóa Kỵ, Kình Đà → thị phi; Thái Dương hãm → lực kém | Mệnh Dần/Thân Cự Nhật | Toàn Thư |
| A07 P1 | Nhật Nguyệt tịnh minh (Nhật, Nguyệt đều sáng ở hai bên Mệnh/Tp) | Một trong hai hãm → “phản bối”; Tuần/Triệt bản cung | Nhật Mão, Nguyệt Hợi, Mệnh Mùi | Toàn Thư |
| A08 P1 | Nhật Nguyệt phản bối (Nhật hãm, Nguyệt hãm hoặc đặt ngược) | Có Khoa Quyền Lộc, Xương Khúc, Tả Hữu giải; vận sáng kích hoạt | Mệnh Tuất | Toàn Thư |
| A09 P1 | Nhật Lệ Trung Thiên (Thái Dương Ngọ, đồng Mệnh) | Hóa Kỵ, Hỏa/Linh/Kình đồng cung; Tuần/Triệt | Mệnh Ngọ Thái Dương | Toàn Thư |
| A10 P1 | Nhật Xuất Lôi Môn (Thái Dương Mão) | tương tự A09; cần Thân/Tp | Mệnh Mão | Toàn Thư |
| A11 P1 | Nguyệt Lãng Thiên Môn (Thái Âm Hợi, Mệnh) | Thái Âm Hóa Kỵ; Tuần Triệt | Mệnh Hợi | Toàn Thư |
| A12 P1 | Nguyệt Sinh Thương Hải (Thái Âm Tý, Mệnh) | tương tự A11 | Mệnh Tý | Toàn Thư |
| A13 P1 | Thạch Trung Ẩn Ngọc (Cự Môn Tý/Ngọ, Mệnh) | Cần Khoa Quyền Lộc/Hóa Lộc; Tuần/Triệt phá; Kỵ phá | Mệnh Tý Cự Môn | Toàn Thư |
| A14 P1 | Thiên Lương Ngọ (Thiên Lương miếu Ngọ) / Cơ Lương Thìn Tuất | Thiên Lương hãm hoặc gặp Kình Đà thì chuyển nghĩa | Mệnh Ngọ | Toàn Thư |
| A15 P2 | Thiên Đồng Thái Âm Tý/Ngọ (đồng cung) | Kình Dương Ngọ → “Mã đầu đới kiếm” (xem B01) | Mệnh Tý | Toàn Thư |
| A16 P2 | Tham Vũ đồng hành (Tham + Vũ Sửu/Mùi), “đại khí vãn thành” | Phải tuổi muộn; gặp Hóa Kỵ/Không Kiếp thì khác | Mệnh Sửu | Toàn Thư |
| A17 P2 | Liêm Tham Tỵ/Hợi, Liêm Trinh Thanh Bạch (Liêm Phủ?) | điều kiện cách tùy sách: cần so | Mệnh Tỵ | Toàn Thư; so Khảo Luận |
| A18 P3 | Minh Châu xuất hải / các cách cung Mệnh vô chính diệu mượn sao đối cung | Nhật Nguyệt ở cung chiếu phải đúng chỗ; Tuần Triệt đặc biệt | Mệnh Mùi vô chính diệu | Toàn Thư |

### 5.B — Phá cách, biến cách, phản cách, cách hung

| ID | Quy tắc | Điều kiện / chế hóa cần xác minh | Nguồn |
|---|---|---|---|
| B01 P0 | “Mã đầu đới kiếm” (Kình Dương Ngọ ở Mệnh) | Có/không có cát tinh Tp; độ sáng Kình; được xem là cách đặc biệt (có sách khen) | Toàn Thư |
| B02 P0 | Phá cách do Hóa Kỵ đồng cung chính tinh cát | Khoa/Quyền cùng cung giảm; Kỵ rơi hãm địa thì nặng hơn | Khảo Luận/Toàn Thư |
| B03 P0 | Tuần/Triệt án ngữ Mệnh hoặc Tp | Phân biệt Tuần vs Triệt; sao nào được “giải” (sát tinh bị giải là lợi, cát tinh bị cắt là hại); tuổi ảnh hưởng (Triệt khi trẻ, Tuần khi già nhiều sách nói) | Toàn Thư |
| B04 P1 | Kình–Đà giáp Mệnh / Không–Kiếp giáp Mệnh / Hỏa–Linh giáp Mệnh | Nếu cung Mệnh có chính tinh sáng và cát tinh đồng cung thì giảm | Toàn Thư |
| B05 P1 | Lộc Kỵ giao nhau (Hóa Lộc xung hoặc đồng cung Hóa Kỵ) | Trường phái tam hợp vs phi tinh đọc khác nhau (cần tách) | Cả hai trường phái |
| B06 P1 | Sát tinh miếu đắc địa thành cách (Kình/Hỏa/Linh miếu) | điều kiện địa chi; đi cùng chính tinh nào | Toàn Thư |
| B07 P1 | Hỏa/Linh đồng Tham Lang (Hỏa Tham, Linh Tham) | Tham ở Sửu/Mùi/Thìn/Tuất mới thành; nơi khác thành hung | Toàn Thư |
| B08 P1 | Mệnh vô chính diệu gặp Không Kiếp (“nhị Không”) | Có chính tinh sáng ở đối cung giải; Triệt trùng | Toàn Thư |
| B09 P2 | Thất Sát/Phá Quân hãm gặp Kình–Đà hay Không Kiếp | Chế hóa bởi Khoa Quyền, Tử Vi, Thiên Phủ | Toàn Thư |
| B10 P2 | Biến cách: cách tốt gặp hạn “phản” → đổi cách | Cần bảng sách ghi rõ (chưa có) | cần tìm |
| B11 P2 | Phản cách: cách hung gặp chế hóa → trở thành thượng cách | Dạng “Hung tinh miếu địa” | Toàn Thư |
| B12 P3 | Cách hiếm trong cổ phú (nhiều chục tên) cần danh sách chuẩn hóa | Phải gom từ “Thái Vi phú”, “Đẩu số phú” rồi xác minh, không tự tạo | cổ phú |

### 5.C — Phụ tinh, sát tinh, giáp cung

| ID | Quy tắc | Điều kiện / chế hóa | Nguồn |
|---|---|---|---|
| C01 P0 | Tả Hữu giáp Mệnh / Tả Hữu Đồng cung chính tinh | cần cặp trái-phải đúng | Toàn Thư |
| C02 P0 | Xương Khúc giáp Mệnh; Xương Khúc đồng cung chính tinh | cùng cung Mệnh khác với giáp | Toàn Thư |
| C03 P0 | Khôi Việt giáp Mệnh (“Tọa Quý hướng Quý”) | điều kiện chi của Mệnh | Toàn Thư |
| C04 P1 | Quân Thần Khánh Hội (Tử Vi + Tả Hữu + Xương Khúc) | thiếu một sao → “bán thành” | Toàn Thư |
| C05 P1 | Lộc Tồn đồng cung / Lộc Mã giao trì / Song Lộc | Mã bị Tuần/Triệt, Kình Đà cùng cung Lộc | Toàn Thư |
| C06 P1 | Đào Hồng Hỷ với chính tinh (đào hoa cách) | phân biệt theo cung (Phu Thê, Mệnh) và chính tinh đi kèm | Khảo Luận (đã có 12 luật Đào–Hồng–Thiên Không theo năm) |
| C07 P1 | Thiên Hình, Thiên Riêu, Thiên Y — cung vị và đồng cung | cần thêm dữ liệu an sao | Toàn Thư |
| C08 P2 | Hóa tinh trung tinh (Quốc Ấn, Đường Phù, Thiên Quan, Thiên Phúc) | điều kiện cung | Toàn Thư |
| C09 P2 | Sát tinh nhập Mệnh theo độ sáng (Linh, Hỏa, Kình, Đà, Không, Kiếp) | cần mở rộng bảng độ sáng | Thực Hành/Toàn Thư |
| C10 P2 | Cô Thần/Quả Tú đồng cung Phu Thê hoặc Mệnh | Hóa Khoa/Tả Hữu giảm | Toàn Thư |
| C11 P2 | Thiên La Địa Võng ở Thìn Tuất | Mệnh cung đó + sao gì | Toàn Thư |
| C12 P3 | Long Trì/Phượng Các/Thai Phụ/Phong Cáo/Tam Thai/Bát Tọa | sao phụ, lực yếu: chỉ làm *booster* | Toàn Thư |

### 5.D — Tứ Hóa tĩnh (bản mệnh)

| ID | Quy tắc | Điều kiện / chế hóa | Nguồn |
|---|---|---|---|
| D01 P0 | Tam Hóa liên châu (Lộc Quyền Khoa ba cung liền) | Kỵ nằm ở Tp hoặc xung → giảm | Toàn Thư |
| D02 P0 | Tam Kỳ Gia Hội (Lộc Quyền Khoa hội Tp Mệnh) | điều kiện sao sáng và không bị phá | Toàn Thư |
| D03 P0 | Hóa Kỵ nhập/xung Mệnh, Phúc, Quan, Tài, Di (từng cung ý nghĩa khác) | độ sáng sao hóa Kỵ; Khoa/Lộc giải; Tuần Triệt | Khảo Luận/Toàn Thư |
| D04 P0 | Hóa Lộc vào các cung (Tài, Quan, Phúc, Điền, Phu) | sao hóa hãm → Lộc hạn chế | Khảo Luận p.197 (đã có) |
| D05 P1 | Hóa Quyền đi với sao quyền (Tử Vi, Vũ Khúc, Thiên Tướng…) và Hóa Khoa với văn tinh | cát tinh đi cùng | Toàn Thư |
| D06 P1 | Khoa giải Kỵ (Khoa-Kỵ cùng hội hoặc đồng cung) | “giải” có điều kiện (độ sáng) | Khảo Luận |
| D07 P1 | Hóa theo can của năm sinh × chính tinh đồng cung: ma trận 14 sao × 4 hóa | cần bảng từng ô, không điền chung | Khảo Luận/Toàn Thư |
| D08 P2 | Lộc Tồn × Hóa Lộc (Song Lộc), Hóa Lộc × Lộc Tồn xung | tách tam hợp / phi tinh | cả hai |
| D09 P2 | Tứ Hóa × Tuần Triệt (Triệt Hóa Lộc, Tuần Hóa Kỵ…) | phần lớn sách nêu rời rạc; cần chuẩn hóa | cần tìm |
| D10 P3 | Biến thể bảng Tứ Hóa theo trường phái (Canh, Mậu, Nhâm, Quý…) | chạy song song hai bảng, nhãn trường phái | đối chiếu mọi sách |

### 5.E — Phi Hóa (trường phái Phi Tinh, tách biệt)

| ID | Quy tắc | Điều kiện | Nguồn |
|---|---|---|---|
| E01 P1 | Mô hình đồ thị phi hóa: cung A bay Lộc/Quyền/Khoa/Kỵ vào cung B theo can cung A | chỉ chạy khi chọn trường phái phi tinh | Huệ Tâm Trai Chủ / Phi Tinh tài liệu (xác minh tác giả, sách) |
| E02 P1 | Tự hóa (can cung hóa sao nằm trong chính cung) | tự hóa Lộc khác tự hóa Kỵ; ngoại lệ theo trường phái | Phi Tinh |
| E03 P1 | Mệnh phi Kỵ vào cung nào (nơi “vướng”), phi Lộc vào cung nào (nơi “thuận”) | tách Mệnh và Thân | Phi Tinh |
| E04 P2 | Quan–Tài, Phu–Phúc lộ trình hóa | cần lý thuyết cung “chủ thể–đối tượng” | Phi Tinh |
| E05 P2 | Kỵ nhập, Kỵ xung (xung phá cung đối) | trong phi tinh Kỵ xung nặng hơn Kỵ nhập | Phi Tinh |
| E06 P2 | Lộc Kỵ qua lại giữa hai cung (hóa ngược) | điều kiện đối xứng | Phi Tinh |
| E07 P3 | Phi hóa theo đại hạn và lưu niên (đại hạn phi, lưu niên phi) | tầng 3–4 | Phi Tinh |
| E08 P3 | Phi hóa cung Thân | quan điểm khác nhau giữa trường phái | cần xác minh |

### 5.F — Tam phương tứ chính, liên cung, Mệnh–Thân

| ID | Quy tắc | Điều kiện / chế hóa | Nguồn |
|---|---|---|---|
| F01 P0 | Tam phương Mệnh–Tài–Quan–Di: hồ sơ khí tổng hợp (bộ tứ) | chia vai Đ/X/T; sao hãm giảm | Khảo Luận/Toàn Thư |
| F02 P0 | Mệnh vô chính diệu: mượn đối cung, trọng số giảm | Tuần/Triệt đối cung; Nhật Nguyệt đối cung | Toàn Thư |
| F03 P0 | Mệnh–Thân cùng cung / khác cung; Thân cư Quan, Tài, Phu, Di, Phúc | mỗi vị trí Thân có ý nghĩa riêng | Toàn Thư (đã có tên cung Thân trong `analysis`) |
| F04 P0 | Phúc–Phối–Di: Phúc Đức (nội), Phu Thê (đối tượng quan hệ), Thiên Di (ngoại cảnh) liên đới | đọc Kỵ ở Phúc/Di | Toàn Thư |
| F05 P1 | Quan Lộc–Tài Bạch: “Quan Tài” cùng Tp, Lộc ở cung nào | Tài hãm, Quan sáng → khác | Toàn Thư |
| F06 P1 | Điền Trạch–Tài Bạch–Phúc Đức: nền tảng tài sản | Phúc có Triệt | Toàn Thư |
| F07 P1 | Thiên Di xung Mệnh: tương quan nội–ngoại (Di sáng Mệnh hãm…) | “xuất ngoại phát” có điều kiện | Toàn Thư |
| F08 P1 | Phụ Mẫu–Mệnh: sao Phụ Mẫu hãm vs Mệnh sáng | cũng đọc cung Phụ Mẫu ở vai “giáp” | Toàn Thư |
| F09 P2 | Huynh Đệ–Nô Bộc–Điền Trạch: quan hệ ngang | thưa thớt trong sách; cần tìm | cần tìm |
| F10 P2 | Phu Thê × Tử Tức × Huynh Đệ (tam hợp) | hôn nhân và con cái liên đới | Toàn Thư |
| F11 P2 | Cung đối chiếu hãm/cung sáng (chủ khách) → “thế phản” | cần định nghĩa chủ khách | cần tìm |
| F12 P3 | Cung Thân đối chiếu Cung Phúc (hậu thiên–tiên thiên) | ý kiến khác nhau | cần tìm |

### 5.G — Vận hạn đa tầng

| ID | Quy tắc | Điều kiện / chế hóa | Nguồn |
|---|---|---|---|
| G01 P0 | Chuyển `van_han.read` thành luật dữ liệu (15 điều kiện hiện có) | giữ nguyên nội dung, thêm `exceptions` | Khảo Luận pp.233–236 |
| G02 P0 | Tứ Hóa đại hạn theo can cung đại hạn × sao bản mệnh (Lộc/Quyền/Khoa/Kỵ vào cung nào) | chạy cả tam hợp (đọc vị trí) và phi tinh (đọc cạnh) | cả hai |
| G03 P0 | Lưu niên: lưu Mệnh = cung chi năm; 12 cung lưu chồng lên bản | cần quy ước | Toàn Thư |
| G04 P0 | Lưu Tứ Hóa theo can năm xem | thêm bảng; tách bảng hóa | cả hai |
| G05 P1 | Đại hạn Mệnh trùng Lưu Mệnh (“trùng điệp”) | cần định nghĩa chính xác theo sách | Toàn Thư |
| G06 P1 | Hai Kỵ gặp nhau (Kỵ bản mệnh + Kỵ đại hạn/lưu) | độ sáng, Khoa giải | cả hai |
| G07 P1 | Lưu Lộc Tồn, Kình, Đà, Khôi Việt, Xương Khúc, Mã | công thức theo can/chi năm | Toàn Thư |
| G08 P1 | Hạn kích hoạt cách cục (cách có `activation_palaces`) | bảng sách chưa gom; phải tự lập từ phú | cổ phú |
| G09 P1 | Đại hạn gặp Tuần/Triệt (tuổi vận) | “Triệt gặp hạn” vs “Tuần gặp hạn” | Toàn Thư |
| G10 P2 | Tiểu hạn × đại hạn × cung bản mệnh (3 tầng đồng ngôi) | “thế Tam trùng/Nhị trùng” cần tên chuẩn hóa | cần tìm |
| G11 P2 | Cung Thái Tuế / Quan Phù / Bạch Hổ (đã có `van_han`) mở rộng cho Tang Môn, Điếu Khách, Thiên Khốc, Thiên Hư | đã có một phần; cần bảng | Toàn Thư |
| G12 P2 | Nguyệt hạn (Đẩu Quân) | quy ước nhiều dị bản | cần tìm |
| G13 P3 | Độ tuổi Mệnh–Thân chuyển pha đời | bảng giai đoạn đời hiện có (STAGE_THUAN/NGHICH) cần mở rộng theo sách | Khảo Luận |
| G14 P3 | Khác biệt nam–nữ trong vận (thuận–nghịch đã có ở đại hạn) mở rộng vào lưu niên | cần xác minh | cần tìm |

### 5.H — Tổng hợp và phản biện (siêu luật)

| ID | Quy tắc | Mô tả |
|---|---|---|
| H01 P0 | Mọi luật cách cục xuất đủ bộ: `thành/hình thức/phá/cứu`, kèm booster/breaker | thay `finding` đơn |
| H02 P0 | Mục “Điều khiến luận đề không đứng” sinh tự động từ `refutations` + `exceptions` + `non_activation` | thay các câu cố định |
| H03 P0 | Luận đề theo chủ đề (tính cách, công danh, tài, hôn nhân, phúc đức) bằng topic recipe | dùng L6 |
| H04 P1 | Điểm tranh chấp: luật cùng chủ đề trái chiều → hai cột, nêu nguồn | thay `unresolved` chung chung |
| H05 P1 | Mức độ bảo chứng: mỗi luận đề ghi “1 nguồn / ≥2 nguồn đồng ý / bị bác” | từ `Source` + `disputedBy` |
| H06 P2 | Giải thích “vì sao cùng sao khác luận” tự động từ nhánh luật đã/chưa kích hoạt | dựa `why()` |
| H07 P2 | Đối chiếu hai trường phái song song trên cùng lá số, nêu chỗ khác nhau | chạy engine hai lần |
| H08 P3 | Cảnh báo giới hạn: câu mở/đóng cố định về tính biểu tượng, không dự báo | đã có thiên hướng này, giữ |

**Tổng cộng:** 18 (A) + 12 (B) + 12 (C) + 10 (D) + 8 (E) + 12 (F) + 14 (G) + 8 (H) = **94 nhóm**, mỗi nhóm khai triển thành vài luật con theo cung/độ sáng/cung vị (ước lượng 400–700 luật dữ liệu thực tế, vì nhiều nhóm là họ luật theo bảng).

---

## 6. Ví dụ định dạng luật cách cục (minh họa, đang `draft`, chưa có nguồn)

```json
{
  "id": "CACH_NHAT_NGUYET_TINH_MINH",
  "school": "tam_hop_vn", "kind": "cat",
  "anchor": {"palace": "Mệnh"},
  "core": {"all": [
    {"ref": {"star": "Thái Dương", "in": ["self","opp","trine"]}, "dignity_rank_gte": 3},
    {"ref": {"star": "Thái Âm",   "in": ["self","opp","trine"]}, "dignity_rank_gte": 3}
  ]},
  "boosters": ["Tả Phụ|Hữu Bật in Tp", "Hóa Khoa|Hóa Quyền|Hóa Lộc in Tp"],
  "breakers": ["Hóa Kỵ đồng cung Thái Dương|Thái Âm", "Kình Dương|Đà La|Địa Không|Địa Kiếp đồng cung Mệnh"],
  "rescuers": ["Hóa Khoa đồng cung Hóa Kỵ", "Triệt tại cung chứa sát tinh phá"],
  "refutations": ["một trong hai sao rơi cung hãm", "Tuần hoặc Triệt trùng bản cung Mệnh"],
  "sources": ["<phải điền khi đã tra trang>"], "reviewStatus": "draft"
}
```

Đầu ra mong muốn cho người đọc (không phải dự báo):

> “Cấu trúc *Nhật Nguyệt tịnh minh* ở trạng thái **thành** (Thái Dương sáng ở X, Thái Âm sáng ở Y, có Tả Phụ trong tam phương). Theo [nguồn] cấu trúc này được đọc là … Điều có thể làm giảm: nếu Hóa Kỵ nhập cung … thì sách đọc khác (ở lá số này: *không có*). Đây là cách đọc truyền thống, không phải khẳng định về sự kiện.”

---

## 7. Lộ trình đề xuất

| Giai đoạn | Nội dung | Kết quả kiểm chứng được |
|---|---|---|
| 1. Nền | Fact theo vai (L1), `dignity_rank`, `star_attrs`, toán tử DSL mới, tham chiếu cung; bảo toàn 418 luật hiện có | test cũ vẫn xanh; thêm test fact theo vai |
| 2. Khí + Cách | Hồ sơ khí (L2), schema `formation`, trạng thái thành/phá/cứu; nạp A01–A06, B01–B04, D01–D03 | mỗi cách có lá số thành/hình thức/phá |
| 3. Liên cung | Topic recipe, F01–F05, H01–H04, hợp nhất `analysis.py` dần vào engine | câu nào cũng có `why()` |
| 4. Vận hạn | G01–G06, lưu niên, lưu Tứ Hóa, tương tác bốn tầng | test tương tác theo trường hợp dựng sẵn |
| 5. Trường phái | Tứ Hóa biến thể, Phi Hóa (E), chạy song song 2 trường phái | test không rò rỉ giữa trường phái |
| 6. Mở rộng sao | Dữ liệu L0 (trung tinh), C07–C12, các cách hiếm | từng sao có công thức đã xác minh |

**Việc phải làm ngoài code (không thể bỏ qua):** thu thập sách và đối chiếu từng công thức an sao, từng bảng Tứ Hóa, từng cách cục; ghi `locator` thật vào `sources.json`; chỉ khi đó mới chuyển `reviewStatus` sang `verified`. Không có bước này, các luật ở trên vẫn chỉ là kiến thức tôi nhớ, và phần mềm phải ghi trung thực như vậy.

## 8. Rủi ro và giới hạn

- **Bùng nổ luật mâu thuẫn:** càng nhiều cách cục càng nhiều xung đột giữa các sách. Lý do chính để cần `disputed` + hai cột (3.4), không nên “chọn bản hay”.
- **Ảo giác chính xác:** nhiều tầng chồng nhau dễ tạo cảm giác như đang tính được vận mệnh. Mọi đầu ra giữ nhãn “theo sách…”, và UI nên đưa mục phản biện lên cùng cấp với luận đề.
- **Dữ liệu từ trí nhớ:** các tên cách, điều kiện và biến thể bảng trong tài liệu này phải coi là *danh sách cần tra*, không phải nguồn.
- **Không xác nhận khoa học:** không có bằng chứng thực nghiệm cho khả năng dự báo của Tử Vi; sản phẩm là công cụ đọc biểu tượng truyền thống một cách nhất quán, có thể truy vết.
