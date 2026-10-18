# Tử Vi — Luận giải chuyên sâu: roadmap, kiến trúc engine, ma trận mâu thuẫn, độ phủ 10 chương

Trạng thái: **P0/P1 đã triển khai sau cờ `TVBT_DEEP_INTERPRETATION` (mặc định OFF)**. Không merge, không deploy. Các API hiện có không đổi (có test so sánh từng byte).

## 0. Hiện trạng (baseline)

- `/api/reasoning` chạy engine suy diễn (`reasoning/engine.py`) rồi `nlg/generate.py` xuất **mỗi finding một câu** ("Có thể nhận thấy một dấu hiệu…"). Mâu thuẫn chỉ được gắn nhãn per-claim (`conflict.resolve`), không được tổng hợp.
- `/api/analysis` (analysis.py) là văn bản dựng từ vị trí sao, tách khỏi các finding.
- Hai luồng này không biết nhau ⇒ cùng một ý xuất hiện ở nhiều chỗ, nhận định trái chiều nằm cạnh nhau không lời giải thích.
- Lưu ý: bản luận đính kèm (81 nhận định) **không có trong repo**; baseline "trước" trong mẫu là đầu ra `/api/reasoning` hiện hành của một lá số kiểm thử. Engine không hardcode lá số nào.

## 1. Kiến trúc engine mới (`engine/tvbt/synthesis/`)

```
 rule engine hiện có (không đổi)          lớp mới (chỉ đọc)
 facts → engine.run → findings ─┐
                                ├─► evidence.build   (Evidence: trang sách, trường phái, điều kiện lá, sao neo, aspect, polarity)
 data/claims_vi.json ───────────┘        │
                                         ├─► evidence.cluster (cụm: cung × aspect × sao neo; trùng lặp gộp, đếm SÁCH chứ không đếm quy tắc)
                                         ├─► conflicts.find_tensions (5 loại, không điểm số)
 tuvi chart (palaces, tu_hoa) ──────────► structures.detect_all (6 cấu trúc đặc biệt, tiền đề/phá/cứu/biến thể/nguồn/mức xác minh)
 data/deep/conflict_matrix.json ────────► conflicts.matrix_hits (điểm nguồn mâu thuẫn Phase 7 chạm vào lá số)
 temporal.tuvi_year ────────────────────► compose (đại hạn/lưu niên)
                                         └─► compose.build_deep_reading → 10 chương
```

| Module | Vai trò |
|---|---|
| `taxonomy.py` | chương chính của từng cung; aspect (tài/danh/trí/hôn nhân/…); valence từ slug theo **token** (không phải chuỗi con). Là heuristic hiển thị, không là điểm. |
| `evidence.py` | Finding → Evidence → Cluster. Một (cung, claim, quy tắc) chỉ một lần. Cụm cùng chủ đề gập thành một dòng + "còn N quy tắc". |
| `conflicts.py` | Phân loại cặp nhận định ngược chiều (xem §3). |
| `structures.py` | Bộ dò cấu trúc đặc biệt, độc lập với lá số cụ thể (test trên cung dựng tay). |
| `compose.py` | Ghép chương: kết luận trước, nâng đỡ/hạn chế, chuỗi lập luận, điều kiện đọc, nguồn, mức xác minh, phần mở rộng trong `details`. |

Nguyên tắc cứng đã được test:

1. Một finding chỉ được kể ở **một** chương; các chương khác chỉ trỏ (`pointers`).
2. Không cộng điểm. Kết luận là câu điều kiện nêu mỗi phía cần gì để đúng.
3. Mục hôn nhân / sức khỏe / tuổi thọ / tiền của luôn mở bằng "theo truyền thống ghi nhận … (không phải dự báo)".
4. `basis` lấy nguyên từ quy tắc; engine **không** tự đánh dấu verified; mức xác minh cấu trúc chỉ có `da_doi_chieu | mot_phan | chua_du_nguon`.
5. Không chọn trường phái; không chọn bảng Nhâm-Khoa (`tuvi.TU_HOA[Nhâm]` vẫn là Tả Phụ, test khóa lại); không có logic Khôi Việt giáp Mệnh; không suy diễn Tuần/Triệt ngoài câu sách.

Cờ: `engine/tvbt/synthesis/__init__.py::enabled()` đọc `TVBT_DEEP_INTERPRETATION` (`1/true/on/yes`). Endpoint mới `POST /api/deep-reading` (cùng body `BirthReq`, `to_year` chọn năm lưu niên, mặc định sinh+30; `experimental=true` mới thêm cách cục nháp). Cờ tắt ⇒ HTTP 404, không import thêm gì ở các endpoint khác.

## 2. Phương pháp luận → nơi thực hiện

| Yêu cầu | Trạng thái | Nơi |
|---|---|---|
| Mệnh/Thân/Cục, âm dương thuận nghịch, Mệnh–Cục | **Có** (nêu ở Tổng quan) | `compose.py` |
| Chính/phụ tinh, độ sáng, đồng cung, xung chiếu, tam hợp, giáp | **Có** (vị trí → quan hệ cung, mỗi chương) | `structures.Geo`, `_palace_position` |
| Tam phương tứ chính, cách cục, phá/cứu | **Một phần**: 6 cấu trúc + cách cục nháp khi `experimental` | `structures.py` |
| Tứ Hóa, Lộc Tồn, bộ sao | **Một phần**: Tứ Hóa trong cấu trúc và đại hạn; Lộc Tồn chỉ qua quy tắc sẵn có | |
| Tuần/Triệt | **Một phần**: nêu hai chiều (R07), không chọn | `conflict_matrix.json` |
| Vô chính diệu, mượn đối cung | **Một phần**: Thân cư Quan Lộc VCD ghi rõ *chưa đủ nguồn* | `structures.than_cu_quan_loc_vcd` |
| Đại hạn, tiểu hạn, lưu niên, lưu Tứ Hóa × nguyên cục | **Một phần**: vị trí + lời sách theo sao hóa + Tứ Hóa đại hạn đáp cung nào; chưa có luật giao thoa có nguồn | `compose.py` |

## 3. Ma trận mâu thuẫn

### 3a. Phân loại cặp nhận định (tự động)

Chỉ so sánh cặp cùng chương+aspect (cùng sao neo nếu aspect "tổng hợp"), một thuận một nghịch. Mọi cặp khác chỉ *cùng tồn tại*.

| Loại | Điều kiện | Cách trình bày |
|---|---|---|
| `refinement` | điều kiện quy tắc A ⊂ B | A là nền, B điều chỉnh; cả hai đều thỏa |
| `both_hold` | điều kiện kích hoạt khác nhau, **cả hai đều đã thỏa** (hai quy tắc đều fire) | hai lực cùng tồn tại; nêu từng điều kiện kích hoạt; sách không xếp thứ tự |
| `school_divergence` | cùng điều kiện, khác sách | nêu cả hai, không ưu tiên |
| `unresolved` | cùng điều kiện, cùng sách | mâu thuẫn thật |
| *(không phải mâu thuẫn)* | khác aspect / khác sao neo | cùng tồn tại, không so |

Phát hiện khi quét 600 lá số: 8.737 `both_hold`, 482 `refinement`, 30 `unresolved` (0 `school_divergence`). Mẫu `unresolved` đều là cặp Toàn Thư cung Phúc Đức viết hai câu ngược nhau theo góc nhìn từng sao đồng cung (ví dụ Cự Môn "hưởng phúc" vs Thiên Đồng "nhiều buồn hơn vui") — đây là **mâu thuẫn thật trong cùng một sách**, được giữ nguyên.

### 3b. Điểm nguồn mâu thuẫn đã biết (`data/deep/conflict_matrix.json`, từ Phase 7)

R01 phạm vi "hội/gặp" · R03 ngưỡng sát tinh phá cách · R05 Nhâm-Khoa (Tả Phụ KL ↔ Thiên Phủ TH) · R07 Tuần/Triệt hại ↔ cứu · R08 Thạch trung ẩn ngọc / Kình ở Ngọ · R09 Tử Phủ đồng cung neo Mệnh/Thân. Engine chỉ báo điểm nào **chạm** lá số hiện tại và chính sách hiển thị; R02, R04, R06, R10, R11 chưa mã hóa (xem §6).

## 4. Cấu trúc đặc biệt đã làm sâu

| Cấu trúc | Tiền đề kiểm tra | Phá / cứu / biến thể | Mức xác minh | Ghi chú nguồn |
|---|---|---|---|---|
| Cự Môn hãm + Hóa Lộc | Cự Môn có Hóa Lộc **và** hãm (nếu không hãm, báo rõ "không áp dụng") | Tứ Mộ giảm Lộc (KL tr.66, TH tr.52); sát tinh; Kỵ; Tuần/Triệt (R07); Cự Tý/Ngọ (R08) | `mot_phan` | Không có câu sách nói thẳng tổ hợp; cấm đọc thành "hãm biến tốt" |
| Tam Hóa hội Mệnh | Lộc–Quyền–Khoa trong tam phương | báo theo 3 phạm vi (đồng cung / +đối cung / tam phương) — R01; Kỵ & sát tinh là limiter | `da_doi_chieu` (TH tr.87, tr.30–33) | độ nhạy phạm vi hiển thị |
| Thân cư Quan Lộc vô chính diệu | Thân ở Quan Lộc, Quan Lộc không chính tinh | mượn đối cung chỉ là phép đọc phụ | `chua_du_nguon` | KL tr.222/218 chỉ cho Mệnh/Thiên Di; không suy diễn |
| Cơ/Nguyệt tại Phu Thê | Cơ hoặc Nguyệt ở Phu Thê | Tuần/Triệt, Kỵ, Đà (đồng cung hoặc tam phương) | `mot_phan` (TT tr.82–83, KL tr.80) | phần "gặp Tuần/Kỵ/Đà" chỉ có câu chung (R07); không kết luận hôn nhân |
| Kình Dương ở Tứ Mộ | Kình ở Thìn/Tuất/Sửu/Mùi | Hỏa Tinh (TT tr.50, chỉ cho Mệnh); Khoa/Quyền/Lộc (KL tr.64); Sát/Hình, Không Kiếp | `mot_phan` ở Mệnh, `chua_du_nguon` cung khác | TT tr.142 nói về Kình ở Ngọ, không áp sang Tứ Mộ |
| Sát–Phá–Tham | 3 sao trong tam phương Mệnh | 3 ngưỡng phá cách song song (≥1 / ≥2 / ≥3+Kỵ) | `mot_phan` | R03: ngưỡng chưa đủ nguồn; có thể cho 3 kết luận khác nhau |

## 5. Độ phủ 10 chương

| # | Chương | Nội dung chính | Nguồn nội dung | Còn thiếu |
|---|---|---|---|---|
| 1 | Tổng quan | Mệnh/Thân/Cục, âm dương, số cụm/mâu thuẫn/cấu trúc, trục chính Bản Mệnh; **không lặp chương khác** | tính toán + cụm verified | chưa có "luận điểm trung tâm" liên-hệ (cần quy tắc ưu tiên có nguồn) |
| 2 | Bản Mệnh | cung Mệnh + Tam Hóa hội Mệnh | finding cung Mệnh | |
| 3 | Tính cách | Phúc Đức + finding Mệnh aspect tính/trí | | aspect từ slug còn thô |
| 4 | Công danh | Quan Lộc + finding Mệnh aspect danh + Thân cư Quan VCD | | |
| 5 | Tài Bạch | Tài Bạch, Điền Trạch, Mệnh aspect tài | | |
| 6 | Quan hệ | Phu Thê, Nô Bộc, Tử Tức, Huynh Đệ, Phụ Mẫu + Cơ/Nguyệt Phu Thê | | |
| 7 | Đại hạn & lưu niên | đại hạn hiện tại, Tứ Hóa đại hạn đáp cung, lưu Tứ Hóa, tiểu hạn | `temporal.tuvi_year` | luật giao thoa đại hạn × nguyên cục chưa có nguồn |
| 8 | Cách cục | 6 cấu trúc + cách cục nháp (khi `experimental`) | `structures.py` | |
| 9 | 12 cung | bảng vị trí 12 cung; chỉ Thiên Di + Tật Ách luận ở đây | | |
| 10 | Luận giải chuyên sâu | mâu thuẫn, điểm nguồn mâu thuẫn chạm lá số, chính sách "chưa đủ nguồn", cấu trúc vắng | `conflict_matrix.json` | |

Mỗi chương trả: `conclusion` (đứng đầu), `supports`, `limits`, `neutral`, `reasoning_chain` (vị trí sao → quan hệ cung → cách cục → điều kiện → kết luận), `reading_conditions`, `sources` (trang + trường phái), `verification`, `details` (toàn bộ cụm, mâu thuẫn, cấu trúc).

## 6. Việc chưa làm và lý do

| Mục | Ưu tiên | Lý do chưa làm |
|---|---|---|
| UI (tab "Luận giải sâu") đọc `/api/deep-reading` | P1 (UI) | `engine/web/*` đang có thay đổi chưa commit của người dùng; không đụng. API đã đủ để nối |
| Mã hóa R02, R04, R06, R10, R11 vào ma trận | P2 | R04/R06 cần quyết định chuyên gia; R10 đã xác nhận nguồn (không còn mâu thuẫn); R11 là quy ước hiển thị |
| Luật giao thoa đại hạn/lưu niên × nguyên cục | P2 | không có câu sách trong bộ quy tắc; sẽ phải tự suy diễn |
| Valence theo slug → nhãn thủ công cho ~1.274 claim | P2 | heuristic hiện đủ cho nhóm/hiển thị, nhưng sai-lệch gây bỏ sót/nhầm mâu thuẫn; nên review thủ công |
| Khôi Việt giáp Mệnh, Tuần/Triệt ngoài câu sách, Nhâm-Khoa | — | **cố ý không làm** theo yêu cầu: nguồn chưa đủ |
| Văn phong: câu kết luận hiện là mẫu điều kiện (đã bỏ văn mẫu cũ) | P2 | cần biên tập viên để đa dạng hóa mà vẫn bám provenance |

## 7. QA

- `tests/test_deep_interpretation.py` (15 test): cờ OFF → 404; cờ ON → 10 chương; `/api/reasoning`, `/api/analysis`, `/api/chart` giống từng byte trước/sau; 6 bộ dò trên cung dựng tay (có ca đối lập: Cự Môn miếu vs hãm, Kình Tứ Mộ ở Mệnh vs cung khác, Thân cư Quan có/không chính tinh, 3 phạm vi Tam Hóa); 5 loại mâu thuẫn + tính tất định; quét 240 lá số: không câu cấm, mỗi finding đúng một chương, mục nhạy cảm luôn có "không phải dự báo", mức xác minh trong tập cho phép, không hàm Khôi Việt, Nhâm-Khoa giữ Tả Phụ.
- Quét 600 lá số (1940–2039): 0 lỗi; ~69 finding/lá (44–121), ~38 cụm; tần suất cấu trúc: Kình Tứ Mộ 290, Sát–Phá–Tham 184, Cự Môn hóa Lộc 70, Cơ/Nguyệt Phu Thê 86, Tam Hóa hội Mệnh 40.
- **Chưa có** đối chiếu độc lập với bản sách gốc cho các câu văn do engine sinh (chỉ trang trích dẫn lấy từ quy tắc đã có). Mọi câu kết luận cấu trúc là diễn đạt của engine, cần chuyên gia duyệt trước khi bật cờ cho người dùng.

## 8. Cách bật thử

```bash
TVBT_DEEP_INTERPRETATION=1 uvicorn tvbt.api:app   # trong engine/
curl -XPOST localhost:8000/api/deep-reading -H 'content-type: application/json' \
  -d '{"year":1990,"month":5,"day":15,"hour":10,"minute":30,"gender":"male"}'
```

Bản mẫu trước/sau: `docs/TUVI-DEEP-SAMPLE-BEFORE-AFTER.md`.
