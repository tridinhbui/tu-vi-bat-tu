# Gộp Tử Vi Hàm Số cho 11 cung (2026-10-25)

Nhánh `worktree-ham-so-book` (d69001a) gộp vào main: **569 luật Hàm Số (HS) cho 11 cung ngoài Mệnh**; gói Mệnh (766 luật,
`engine/data/experimental/pack_ham_so_menh.json`) vẫn **chưa nạp**, như yêu cầu. Dữ liệu sinh lại từ đầu trên main hiện tại
(refire fixtures → build → kg_draft → build → base_rates → build → index_norms). Test và golden của nhánh **không lấy**: dùng bản của
main, để mọi thay đổi hiện ra thành lỗi thật rồi xét từng cái (§3).

## 1. Trùng và mâu thuẫn với luật sẵn có

So điều kiện (các điều kiện lá) và khái niệm của từng luật HS với mọi luật verified khác:

| | Số luật HS | Cách xử lý |
|---|---|---|
| Cùng điều kiện với một luật đã có | 259 | |
| — trong đó **cùng ý** (trùng) | 130 | không kể lại: chương Đọc sâu gắn chúng làm **đồng chứng** (`trace.also`), câu không viết hai lần |
| — trong đó **ngược chiều trên cùng mặt** (mâu thuẫn) | 16 | xem dưới |

16 cặp mâu thuẫn, phần lớn là HS với Toàn Thư trên cùng một bộ sao, ví dụ:

- Vũ Khúc – Thất Sát ở Quan Lộc: HS tr.143 "thăng giáng thất thường" ↔ TT tr.78-80 "có chức vị".
- Liêm Trinh – Thất Sát ở Quan Lộc: HS tr.92 "chậm thăng tiến, may rủi liền nhau" ↔ TT "công danh hiển đạt".
- Tử Vi – Thiên Tướng ở Phu Thê: HS tr.139 "vợ chồng có thể xích mích" ↔ TT tr.82-83 "vợ chồng giai lão".
- Cự Môn – Thiên Cơ ở Phúc Đức: HS tr.87 "hưởng phúc thọ, phú quý" ↔ TT tr.83-84 "lao tâm".

10 cặp đã có quan hệ "chưa phân xử" do `kg_draft.ts` sinh: cả hai câu được nói, sổ cân của lĩnh vực ghi hai mặt, không gộp. 6 cặp không có
quan hệ, vì hai khái niệm khác mặt (vd. "thăng trầm" và "có chức vị" có thể cùng đúng) hoặc vì điều kiện thật ra khác nhau (KL tr.113 nói
Thất Sát ở Tử Tức **trừ** Dần Thân, HS tr.115 nói **ở** Dần Thân; phép so điều kiện bỏ qua chữ "trừ"). Không cặp nào bị xóa hay sửa chữ
sách.

## 2. Độ sâu trên 150 lá (trung vị mỗi chương), main hôm nay (đã có DEEP-3) → sau khi gộp

| Chương | Câu sách | Phần chính | Luật khác nhau được nói | Chữ |
|---|---|---|---|---|
| Quan Lộc | 8 → **11** | 2 → 4 | 4 → 8 | 422 → 531 |
| Phúc Đức | 5 → **8** | 2 → 3 | 3 → 6 | 207 → 259 |
| Điền Trạch | 6 → **8** | 2 → 3 | 3 → 5 | 320 → 387 |
| Thiên Di | 8 → **10** | 3 → 4 | 5 → 7 | 301 → 329 |
| Tài Bạch | 8 → 9 | 2 → 3 | 4 → 7 | 474 → 561 |
| Phu Thê | 6 → 7 | 2 → 3 | 3 → 5 | 344 → 375 |
| Nô Bộc | 8 → 9 | 3 → 3 | 6 → 7 | 283 → 282 |
| Tử Tức | 6 → 7 | 2 → 2 | 3 → 4 | 221 → 242 |
| Huynh Đệ | 4 → 5 | 2 → 2 | 3 → 4 | 174 → 190 |
| Phụ Mẫu | 7 → 7 | 3 → 3 | 5 → 6 | 233 → 241 |
| Tật Ách | 5 → 5 | 2 → 2 | 2 → 3 | 270 → 251 |
| Mệnh | 24 → 24 | 10 → 10 | 23 → 24 | 1038 → 1081 |

Số luật khác nhau được nói tăng nhiều hơn số câu: các luật trùng ý đi vào làm đồng chứng chứ không thành câu mới. Ví dụ nội dung mới có trên
lá mẫu: Điền Trạch "chậm có nhà đất, vất vả lúc đầu, về già mới có nhà cửa"; Phu Thê "lấy nhau vì tình" (Ân Quang); Quan Lộc "công danh
lừng lẫy, thịnh và bền" (Thiên Việt, HS tr.210).

## 3. Cổng chất lượng (eval_synthesis 300 lá, eval_repeat 100 lá), main → sau khi gộp

| Đo | main hôm nay | sau |
|---|---|---|
| giới hạn chưa đối diện / kết luận một sao / verdict vênh | 0 / 0 / 0 | 0 / 0 / 0 |
| mâu thuẫn giữa chương chưa giải thích | 0 | 0 (trước khi sửa: 3, xem dưới) |
| câu trùng nguyên văn / báo cáo | 3,57 | 3,57 |
| cụm 6 chữ lặp / 100 câu | 136,9 | 136,0 |
| câu "chưa phân xử" / báo cáo | 4,50 | 4,99 |
| độ giống khung câu chương Mệnh (strip, cổng ≤ 0,065) | — | 0,067 → **0,063** |

Đã sửa trong lúc gộp (không nới cổng nào):

- **Mâu thuẫn sức khỏe (3 lá):** câu "phúc thọ" của HS ở Phúc Đức đối với câu bệnh ở Tật Ách, không có câu kết luận nào nêu cả hai.
  Phúc Đức được thêm vào lĩnh vực sức khỏe (vai phụ, `domains.json`, có ghi chú); lĩnh vực này vẫn không bao giờ kết luận tốt xấu, chỉ
  nêu cả hai mặt.
- **Độ giống khung câu Mệnh 0,067 > 0,065:** nhánh gốc nới cổng lên 0,068; ở đây **không nới**. Thêm biến thể cho các khung câu đồng chứng /
  phản chứng giữa các cung và câu "hai mặt chưa phân xử" → 0,063 (Barnum 40,1 %, tốt hơn mốc 40,5 %).
- **"Bù lại," đứng trước một câu hạn chế** (lộ ra khi thứ tự chọn từ nối dịch đi): câu bổ sung mang ý hạn chế nay luôn dùng từ nối hạn chế.

Câu "chưa phân xử" tăng (4,50 → 4,99 mỗi báo cáo) vì HS thêm bằng chứng ở **cả hai phía** của nhiều lĩnh vực. Không ép phân xử: thang cân có
nhãn vẫn quyết khi chênh rõ.

## 4. Test thay đổi và lý do (không sửa golden cho xanh)

| Test | Thay đổi | Lý do |
|---|---|---|
| 13 golden văn (12 chương lá mẫu + 20 lá benchmark) | sinh lại sau khi đọc diff | nội dung mới có trang HS; diff đã đọc: không câu nào mất trang, một lỗi từ nối ("Bù lại") tìm ra và sửa trong mã |
| `synthesis.test` 2002 Phu Thê | `nghieng_ve` → chấp nhận cả `chua_phan_xu` | HS thêm hai câu trắc trở ngay ở Phu Thê (Hóa Kỵ: hay cãi vã, tr.169; Tuần: trắc trở, tr.227) và hai câu hòa hợp (Quang Quý tr.147, Cơ Nguyệt Dần Thân tr.119); hai phía nay ngang nhau |
| `synthesis.test` 2002 Quan Lộc (một sao) | chấp nhận đồng chứng từ cung khác trên sao khác | đúng thiết kế `luan.ts caveats()`: câu về Tả Phụ ở Quan Lộc có Quang Quý ở Tài Bạch cùng ý, nên không còn là kết luận một sao |
| `correctness.test` #5 | mặt thuận công danh có thể được gọi "danh tiếng" | câu dẫn đầu mặt thuận nay là Thiên Việt ở Quan Lộc (HS tr.210) |

**Thay đổi kết luận trên lá 2002 của chủ dự án:** hôn nhân từ "nghiêng về thuận" thành "chưa phân xử" (lý do ở trên); các lĩnh vực khác giữ
nguyên.

## 5. Còn lại

- Hai câu "gốc" về cùng một sao đứng liền nhau ở Đọc sâu Quan Lộc của lá mẫu ("Gốc của danh tiếng là Thiên Việt…" rồi "Sự thuận lợi …
  đứng trên Thiên Việt…"): HS đổi tên mặt thuận, lớp Đọc sâu vẫn gọi lại tên cũ.
- Từ nối hạn chế ("Chỉ có điều") đôi khi đứng giữa hai câu cùng xấu; nên chọn từ nối theo câu đứng trước, không chỉ theo câu đang viết.
- Gói Mệnh của HS (766 luật) vẫn để riêng.
- Gộp lần hai trên main có DEEP-3: xung đột mã (loader, generator, semantic, book_text, show_page) gộp cả hai phía; dữ liệu tay
  (`claims_vi.json`, `rule_concepts.manual.json`) lấy hợp hai bên; tệp sinh, trang tĩnh, fixture sinh lại.
