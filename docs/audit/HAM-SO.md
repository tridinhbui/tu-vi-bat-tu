# Tử Vi Hàm Số (HS) — sách thứ năm của bộ luật Tử Vi (2026-10-24)

*Tử Vi Hàm Số*, Nguyễn Phát Lộc (Sài Gòn, 1972). Bản PDF 238 trang (bản gõ Word, lớp chữ VNI, giải mã bằng `tools/book_text.py`).
**Trang in = trang PDF − 1** (`PDF_OFFSET`, đã đối chiếu số trang in trên 235 trang). Mã trích dẫn `HS p.N`, nguồn `SRC_HAM_SO`,
schoolId `ham_so`. Tên sách trong văn: "Hàm Số".

## 1. Bóc tách

| Phần | Trang in | Nội dung | Dùng |
|---|---|---|---|
| Quyển Nhất | 1–25 | cách an sao | không |
| Quyển Nhất | 26–83 | qui tắc đoán, luận các cung, Bản Mệnh – Cục – Cách | nhóm G: âm dương thuận/nghịch lý, Mệnh–Cục, địa lợi Mệnh, vô chính diệu, phú/quý cục, nghề trung cách |
| Quyển Nhì | 84–145 | 14 chính tinh: vị trí, tính tình đắc/hãm, công danh tài lộc, bộ sao, "ở các cung" | nhóm A, B, C |
| Quyển Nhì | 146–233 | phụ tinh (theo vần), Tuần Triệt (tr.222–228) | nhóm D, E, F |
| Quyển Nhì | 233–237 | bảng vật dụng, thức ăn, tang chế | không |

- Dữ liệu: `tools/data/ham_so_rules.json`, **1.592 mục**, mỗi mục có trang in và một câu trích nguyên văn ≥ 4 chữ; câu trích được đối
  chiếu với trang PDF (`engine/tests/test_ham_so.py`, bỏ qua khi máy không có sách). Lời đọc là diễn ý, điều kiện là điều kiện của sách.
- Không lấy: tướng mạo, bộ phận cơ thể, tên bệnh; chết, yểu, tự tử, tai nạn; tù tội, trộm cắp; chuyện dâm, trinh tiết; mọi câu "ở hạn";
  sự kiện hôn nhân, con cái (bỏ nhau, sát con, cha mẹ mất sớm); câu tác giả chỉ dẫn lại để bác ("có sách cho là … nhưng không mấy đúng");
  câu có dấu "(?)", "có lẽ"; điều kiện lá số không kiểm được (sinh ngày/đêm, "cát tinh hội chiếu" không nêu tên sao).
- **Bảng độ sáng riêng của sách** (`engine/data/ham_so_dignity.json`): "đắc địa / hãm địa" của luật HS được đọc theo bảng của chính
  Hàm Số, mở thành các chi mà bảng in. Sách in trùng hoặc thiếu hai chỗ — Thiên Lương: Tý ở cả vượng (tr.124) lẫn hãm (tr.125), thiếu
  Tỵ; Vũ Khúc: Dần ở cả vượng lẫn đắc (tr.140), thiếu Dậu — các ô ấy không dùng (luật không nổ ở đó), không đoán.
- 257 mục để **tham khảo** (`"use": "reference"`, không thành luật): nghĩa chung của một phụ tinh hay một nhóm phụ tinh ở Mệnh không kèm
  điều kiện nào khác (Quang Quý nổ ở 44 % lá số, Tứ Đức 26 %, Tam giải 25 %), bộ sao mà sao đi kèm luôn đứng sẵn đó (Điếu Khách – Quan Phù,
  Trực Phù – Thái Tuế, Đế Vượng – Trường Sinh, Địa Võng luôn ở Tuất), và câu âm dương thuận/nghịch lý mà tác giả gọi là yếu tố đầu tiên,
  không quyết định (tr.30). Chúng nói về sao, không nói về một lá số; tác giả cũng xếp chính tinh nặng hơn phụ tinh (tr.49).

## 2. Hai pack

| Pack | Luật | Nạp | Ghi chú |
|---|---|---|---|
| `engine/data/pack_ham_so.json` | 569 | có | 11 cung ngoài Mệnh |
| `engine/data/experimental/pack_ham_so_menh.json` | 766 | **chưa** | cung Mệnh: câu trích và điều kiện vẫn được kiểm |

Pack Mệnh để một bước riêng: nạp vào thì Mệnh có thêm khoảng 24 luật nổ mỗi lá số (các sách khác cộng lại ≈ 30), tỷ lệ nền các khái niệm
(`base_rates.json`) dịch đi, mọi thước đo chương Mệnh đọc theo tỷ lệ ấy. Đo cùng một thước, nội dung có HS không chung chung hơn
(Barnum 0.382 so với 0.401 theo thước cũ; 0.530 so với 0.537 theo thước mới) nhưng chương Mệnh cần chỉnh lại trước khi nạp.

39 khái niệm KG mới (`engine/data/kg/concepts.json`) có thẻ văn ở `src/interpret/content/prose/concepts_ham_so.json` (draft).

## 3. Thay đổi kết luận trên lá số 2002 (09/01/2002, `ref_2002_01_09_kl.json`)

Sổ cân (ledger) trước / sau khi nạp pack 11 cung:

| Lĩnh vực | Trước | Sau | Vì sao |
|---|---|---|---|
| Công danh | chưa phân xử | chưa phân xử | Mặt thuận thêm Thiên Việt ở Quan Lộc ("công danh lừng lẫy, thịnh và bền", HS tr.210) và Tả Phụ ở Quan Lộc (phò tá, hậu thuẫn, HS tr.178); mặt thuận nay được gọi tên bằng **danh tiếng** thay cho "thuận lợi trong công việc". Kết luận không đổi. |
| Tài lộc – kiếm | có điều kiện, thuận | có điều kiện, thuận | thêm Quang Quý ở Tài Bạch (được giúp về tiền, HS tr.148) phía thuận; Thiên Không ở Tài Bạch (tán tài, tụ tán bất thường, HS tr.211) phía hạn chế |
| Tài lộc – giữ | trở ngại | trở ngại | thêm Tam giải (hao hụt của cải, tr.157) và Thiên Không ở Tài Bạch (tr.211) |
| Tài lộc – tích lũy | trở ngại | trở ngại | thêm Địa Không và Thất Sát ở Điền Trạch (HS tr.162, 116) |
| **Hôn nhân** | **nghiêng về thuận** (Thái Âm vượng, chính tinh, nặng hơn Đà La) | **chưa phân xử** | HS thêm hai câu trắc trở **ngay ở Phu Thê**: Hóa Kỵ ở Phu Thê — vợ chồng lục đục, hay cãi vã (tr.169; ở lá này là Văn Xương hóa Kỵ), Tuần ở Phu Thê — trắc trở hôn nhân (tr.227); và hai câu hòa hợp: Quang Quý ở Phu Thê (tr.147), Cơ Nguyệt ở Dần Thân (tr.119). Thang cân của hệ thống (quyết định 2026-10-23) không còn tách được hai bên, nên cả hai được nêu và để chưa phân xử. Đà La, Tuần và Văn Xương hóa Kỵ vẫn được nêu là giới hạn của mặt thuận. |
| Sức khỏe | không kết luận | không kết luận | thêm Tam giải (tr.157) và Triệt (tr.227) ở Tật Ách (sao giải) |

Test đổi theo: `synthesis.test.ts` (2002 Phu Thê: `chua_phan_xu`, hai mặt vẫn phải được gọi tên),
`correctness.test.ts` (#5: mặt thuận công danh được gọi là "thuận lợi trong công việc" hoặc "danh tiếng").

## 4. Thay đổi ngoài dữ liệu sách

- `generator.ts`: mỗi chủ đề kể tối đa 3 căn cứ "cũng ghi" (năm sách gom được một đuôi dài câu cùng ý).
- `pipeline.ts`: thêm nấc rút gọn danh sách 0.35 cho ngân sách 1.500 chữ (chỉ cắt danh sách, không cắt đoạn lập luận).
- `narrative.ts`: câu phản bác từ cung khác có khóa riêng (`…|countered`), không còn bị coi là lặp câu xác nhận cùng khái niệm, cùng cung
  (và không bị dedupe bỏ âm thầm ở chương sau).
- `concepts_outer.json` (`path.service`): bỏ chữ "hệ thống" (từ ngữ phương pháp) khỏi câu minh họa.
- `synthesis.test.ts` (2002 Quan Lộc): một nhận định một sao được coi là có đỡ khi một cung khác nói cùng ý (đúng như `luan.ts caveats()`).
- `readable.test.ts`: ngưỡng độ giống văn (strip) 0.0655 → 0.068: chương Mệnh có thêm câu đọc chéo các cung khác kể bằng khung câu chung;
  thước nội dung không đổi (Barnum 0.401, content Jaccard 0.214, như bản gốc).
- `index_norms.json` chạy lại (thang mức đại hạn / năm / tháng theo corpus mới).

## 5. Còn lại

- Nạp pack Mệnh (§2) cùng chỉnh chương Mệnh.
- Câu trích tham khảo (`use: reference`) có thể vào `star_nature.json` làm "nghĩa của sao" cho phần Đọc sâu.
- Phương pháp "hàm số" của tác giả (tr.73–75: con người = f(Phúc, Mệnh, Thân, Tật); xã hội = f(Di, Quan, Nô); tài sản = f(Tài, Điền) …)
  chưa dùng.
- Khi gộp `indices-3.0.0` (phiên khác) phải chạy lại `node tools/interpret/index_norms.ts`.

Tái tạo sau khi đổi dữ liệu: `.venv/bin/python tools/build_ham_so_pack.py` → `.venv/bin/python tools/interpret/refire_fixtures.py` →
`node tools/interpret/build.ts` → `kg_draft.ts` → `build.ts` → `base_rates.ts` → `build.ts` → `index_norms.ts`.
