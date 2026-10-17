# CLASSICAL-SOURCE-AUDIT — Kiểm toán nguồn cổ thư của `tu-vi-bat-tu`

Ngày: 2026-10-17. Phạm vi: toàn bộ thư viện quy tắc (1.622 quy tắc, 1.806 câu diễn giải), dữ liệu bảng, nội dung học và hệ thống bằng chứng.
Số liệu trong tài liệu này sinh từ công cụ trong `tools/` (cách chạy lại ở §8); không số nào gõ tay mà không có công cụ đứng sau.

> **Đọc trước.** Người đọc nguồn trong đợt này là **mô hình AI** (Claude, nhiều tác tử chạy song song), không phải chuyên gia Tử Vi/Hán Nôm và không có người thứ hai kiểm lại. Mọi trích dẫn từ sách in được **máy kiểm lại** là nằm đúng trên trang; việc *hiểu đúng ý sách* vẫn cần con người. Không quy tắc nào được nâng lên "chuyên gia xác nhận".

---

## 0. Tóm tắt

1. **Thư viện có nguồn thật, nhưng nhãn `verified` cũ yếu hơn vẻ ngoài.** Trong 115 quy tắc `verified` lấy ngẫu nhiên (phân tầng theo gói), **81%** (khoảng tin cậy 95%: 73–87%) khớp cả lời khẳng định lẫn điều kiện với trang sách; **17%** lõi đúng nhưng điều kiện hẹp hơn/rộng hơn/mạnh hơn trang; **2%** sai trang hoặc đọc sai câu phú. Nghĩa là `verified` = "tìm thấy trang và diễn đạt lại", chưa phải "điều kiện khít với sách".
2. **Tìm được lỗi thật và đã xử lý phần an toàn:** 3 quy tắc gán nhầm/đọc sai câu phú bị hạ xuống `draft` (sao Tử bị gán cho sao Mộ ở hai cung; "Tứ Sát" bị đọc thành "Tử, Sát"), 2 số trang sai đã sửa, 1 lỗi chính tả hiển thị ("khuynh hướng khuynh hướng") đã sửa, bảng `sources.json` ghi sai phạm vi trang đã cập nhật. 45 chỗ lệch điều kiện: phần an toàn đã áp (lời của 3 claim nháp không dùng chung được sửa theo trang; cả 45 quy tắc được gắn ghi chú "khớp một phần" vào mô tả); **42 chỗ còn lại chưa sửa vì sẽ đổi kết quả của engine** — mỗi dòng trong `docs/source_audit_findings.csv` có lớp thay đổi và tỉ lệ lá số ngẫu nhiên bị ảnh hưởng.
3. **Định nghĩa cách cục viết theo trí nhớ về Tử Bình Chân Thuyên (11 cách, 13 cấu trúc) không có chỗ nào bịa hoàn toàn, nhưng chỉ 4/24 khớp nguyên văn**; 20/24 lệch điều kiện, và một mục con (Kiêu đoạt Thực làm bại cách Thiên Ấn) **ngược** với văn bản. Giữ `draft`.
4. **Một lá số "khớp" không chứng minh gì:** trên 400 lá số ngẫu nhiên, trung vị 67 nhận định mỗi lá số, 99% có ít nhất một nhận định giàu/sang/công danh ở cung Mệnh và 100% có ít nhất một nhận định hạn chế. Lá số Hán Cao Tổ trong Khảo Luận (74 nhận định) nằm hơi trên trung vị, không phải ngoại lệ.
5. **Nội dung mới:** trang `/reference` (tra cứu theo sao, theo cung, Bát Tự; mức tin cậy 5 bậc; trích nguyên văn máy-kiểm), 12 bài học mới (cấp 4 "Đọc có nguồn" và cấp 5 "Nghiên cứu"), tệp bằng chứng `engine/data/source_evidence.json` (204 quy tắc) và `source_evidence_web.json` (24 định nghĩa), 3 bộ kiểm thử mới (19 test).
6. **Không đổi engine tính toán.** Hồi quy: 1.212 test đạt, 0 lỗi (trước đợt này: 1.132 đạt). Hai thay đổi đụng đầu ra: ba quy tắc hạ xuống `draft` (chúng không còn hiện ở chế độ "Dễ hiểu") và một câu diễn giải được sửa chính tả.

---

## 1. Phương pháp và giới hạn

| Bước | Cách làm | Công cụ | Giới hạn |
|---|---|---|---|
| Kiểm kê | Đọc mọi gói quy tắc, đếm theo gói/nguồn/trạng thái/khoảng trang, tìm claim mồ côi | `tools/audit_knowledge_base.py` → `docs/knowledge_audit.json` | Ma trận chủ đề dùng từ khóa: chỉ là ước lượng |
| Neo trang (1) | Sao mà quy tắc nhắc có nằm trên trang được cite không | `tools/audit_source_anchors.py` | Độ đặc hiệu thấp (xem §3.1) |
| Neo trang (2) | Xếp hạng trang được cite trong *toàn bộ* sách theo TF-IDF | `tools/audit_citation_retrieval.py` | Không dự báo được lệch điều kiện (xem §3.1) |
| Đọc nguyên văn | 204 quy tắc: người đọc mở trang, chép nguyên văn ≤30 từ, xếp loại; máy kiểm trích dẫn có nằm trên trang | `tools/build_source_evidence.py`, `tools/show_page.py` | Người đọc là AI; một người đọc/quy tắc; chọn mẫu 9%/gói |
| Điều chỉnh | Chủ trì đọc lại ảnh trang cho các trường hợp "đọc sai", gỡ báo động giả | `tools/data/evidence_overrides.json`, `evidence_corrections.json` | — |
| Tử Bình Chân Thuyên | Đọc bản chữ Hán trên mạng (không phải sách in), hai máy chủ | `engine/data/source_evidence_web.json` | Trích dẫn không kiểm tự động bằng test (cần mạng); chủ trì tái kiểm 4/24 |
| Cơ sở lặp | Chạy thư viện trên 400 lá số ngẫu nhiên | `tools/measure_reading_base_rate.py` → `docs/reading_base_rate.json` | Phép đếm bằng từ khóa tiếng Việt |

**Sách có trong tay** (`~/Downloads`, không nằm trong repo): Tử Vi Khảo Luận (KL, 290 tr.), Tử Vi Thực Hành (TH, 163 tr.), Tử Vi Đẩu Số Toàn Thư (TT, 170 tr.), 八字真宗 (ZZ, 96 tr.), Trích Thiên Tủy (TTT, 235 tr.), Dự Đoán Theo Tứ Trụ – Thiệu Vĩ Hoa (TVH, bản scan 681 tr., chỉ đọc qua ảnh), Đổi Vận Cho Người Mệnh Khuyết (không dùng làm nguồn), Phương thuật kỷ dị (chưa đọc). **Không có:** Tử Bình Chân Thuyên, Uyên Hải Tử Bình, Tam Mệnh Thông Hội, Cùng Thông Bảo Giám bản in.

**Không làm trong đợt này:** đọc lại 120 ô điều hậu và các quy tắc `SRC_TVH_*` (đã có kiểm toán riêng: `docs/BAZI_DEEP_TVH_AUDIT.md`, `docs/BAZI_DEEP_TVH_CELLS_CHECK.md`), kiểm toán 93 điều kiện cách cục Tử Vi (đã làm ở Phase 2/5/6 trước: `docs/PHASE4_KIEM_TOAN_NGUON.md`), kiểm chứng lịch pháp.

---

## 2. Phase 1 — Kiểm kê tri thức

### 2.1 Quy mô

| | Tử Vi | Bát Tự | Ghi chú |
|---|---|---|---|
| Quy tắc | 1.386 | 236 | Tử Vi gấp ~6 lần Bát Tự |
| Gói | 22 gói `pack_*` | 5 gói (+ `bazi_deep`) | |
| Câu diễn giải (`claims_vi`) | 1.806 chung | | 3 claim mồ côi, 25 claim của gói thử nghiệm chưa có chữ |
| Bài học | 7 (cấp 1-3) → **11** | 4 → **7** | cộng 1 bài giới thiệu (có từ trước) và 5 bài cấp 5 chung: tổng 12 → **24** |

Theo trạng thái (sau đợt này): **1.315 `verified`, 279 `draft`, 28 chưa gắn nhãn** (toàn bộ `van_han_rules.json`).

Theo nguồn (số quy tắc): Toàn Thư 517 (475 v / 42 d), Thực Hành 462 (365 / 97), Khảo Luận 352 (309 / 43), 八字真宗 104 (83 / 21), TVH 55, Trích Thiên Tủy 28, **Tử Bình Chân Thuyên 41 (đều `draft`)**, quy ước hệ thống 10, thử nghiệm 26, không nguồn 28.

Trang sách thực sự được trích trong mô tả quy tắc: KL 56/290 trang, TH 66/163, TT 54/170, ZZ 14/96. **Phần lớn mỗi cuốn chưa được khai thác** (§ Roadmap).

Dữ liệu ngoài quy tắc: bảng độ sáng 14 chính tinh × 2 trường phái + 8 phụ tinh, bảng Tứ Hóa theo Can, bảng thần sát (ZZ), bảng điều hậu 12×10 (TVH), 51 dòng dụng thần theo cách (TVH), 39 câu thành/bại (TVH), bảng tư lệnh (viết từ trí nhớ, `draft`), 11 cách + 13 cấu trúc từ trí nhớ (`draft`), từ điển thuật ngữ (14 chính tinh, 51 phụ tinh, 12 cung, 10 Can, 12 Chi, 10 Thập Thần, 26 khái niệm — viết tay, **không có trích dẫn nguồn**).

### 2.2 Độ phủ theo chủ đề

Số quy tắc **gắn sao** theo cung (Tử Vi, 14 chính tinh; từ `engine/web/js/reference.json`):

| Cung | Số nhận định | | Cung | Số nhận định |
|---|---|---|---|---|
| Mệnh | 664 | | Phụ Mẫu | 70 |
| Tài Bạch | 122 | | Phúc Đức / Điền Trạch | 88 / 88 |
| Thiên Di | 115 | | **Tử Tức** | **15** |
| Quan Lộc | 112 | | **Tật Ách** | **4** (cố ý: loại bệnh tật) |
| Nô Bộc | 103 | | **Huynh Đệ** | **1** |
| Phu Thê | 99 | | | |

Mệnh chiếm hơn một nửa; ba cung gần như trống (tính cả quy tắc không gắn sao: Tử Tức 14, Huynh Đệ 9, Tật Ách 1). Tật Ách trống do chính sách (không mã hóa bệnh tật); Tử Tức một phần do chính sách bỏ các câu về số con sống chết; Toàn Thư phần cung (tr.77-165) không mã hóa Huynh Đệ, Tử Tức, Tật Ách. Phần còn lại là **khoảng trống nội dung có thật**, không phải chủ ý.

| Chủ đề | Tình trạng | Bằng chứng |
|---|---|---|
| Thiên Can | Bảng "nhật can lâm thập thần" và "ngũ hành trực đoán" (ZZ tr.25-26, 20 quy tắc, `verified`); hình ảnh mỗi Can trong từ điển **không có nguồn** | Trích Thiên Tủy chương Thiên Can chưa đọc |
| Địa Chi | Bảng quan hệ, tàng can (ZZ tr.7-17) `verified`; diễn giải riêng từng Chi gần như không có | |
| Ngũ hành, âm dương | Cơ bản có trong từ điển; quy tắc: 5 quy tắc "thiếu hành" (`draft`) | |
| Thập Thần | Định nghĩa tính toán đúng; diễn giải: 10+ quy tắc ZZ, phần Lục thân của TTT/TVH chưa đọc | |
| Tàng can | Bảng `verified`; không có quy tắc diễn giải | |
| Vượng suy | **Mạnh nhất của Bát Tự**: cách điểm TVH tr.331-355, ví dụ tính tay đối chiếu, khớp 45/48 nhãn của TTT | `docs/BAZI_DEEP_BOOKS.md` |
| Dụng thần | TVH: bảng điều hậu 120 ô (tác giả nói bảng do độc giả tặng, không rõ gốc), 51 dòng dụng thần theo cách; phần phù ức/thông quan của hệ thống là quy ước | 9/120 ô bảng ≠ chú thích |
| Cách cục Bát Tự | TVH tr.356-376 `verified` (29/31 lá số mẫu); 11 cách + 13 cấu trúc từ trí nhớ `draft` | §3.4 |
| Đại vận / lưu niên | Tuế vận TTT 8 quy tắc `verified`, 15 `draft`; 28 quy tắc vận Tử Vi (`van_han_rules.json`) **không có `sourceIds`** (chỉ có ghi chú "KL tr.233-236, TH tr.115-117") | |
| Chính tinh Tử Vi | 14 sao, 76–168 nhận định/sao | |
| Phụ tinh | Cát tinh/sát tinh: 46–89 nhận định/sao; **Thiên Hỷ 3, Hóa Lộc/Khoa gần 0 theo mô hình "đồng cung"** (Tứ Hóa có mô-đun riêng); các sao Long Phượng, Hoa Cái, Thiên Hình, Thiên Riêu, Khốc Hư, Quan Phúc, Quốc Ấn, Cô Quả… **chưa mã hóa** vì cách an chưa được kiểm | README |
| Tam phương tứ chính | Hình học: đối chiếu độc lập 116.928 lá số, 0 sai khác; ngữ nghĩa "hội" là quy ước vận hành | `docs/PHASE6_INDEPENDENT_VALIDATION.md` |
| Tứ Hóa | KL tr.195-197 + TH; bảng KL tr.36 in sai (prose đúng); **Nhâm-Khoa: TH ghi Thiên Phủ, KL ghi Tả Phụ** — hệ thống theo KL | |
| Trường phái | Độ sáng: 2 bảng, **45 ô khác nhau**; cách cục: 17 biến thể nháp; Phi Hóa: thử nghiệm | |

### 2.3 Bảng chấm (0–3)

Tiêu chí: **Nguồn** (truy được tới trang/câu), **Chính xác** (đo được so với trang), **Chiều sâu** (điều kiện, ngoại lệ, ví dụ), **Rõ** (người mới đọc hiểu), **Nhất quán** (với engine và giữa các sách), **Sư phạm**. 0 = không có, 1 = yếu, 2 = đủ dùng, 3 = tốt. "Trước → sau" khi đợt này thay đổi điểm.

| Mảng | Nguồn | Chính xác | Sâu | Rõ | Nhất quán | Sư phạm | Căn cứ chấm |
|---|---|---|---|---|---|---|---|
| Tử Vi: chính tinh ở Mệnh | 3 | 2 | 3 | 2 | 2 | 1 → 2 | 81% khớp hoàn toàn; 664 nhận định; trước đó không có điều kiện/ngoại lệ hiển thị |
| Tử Vi: các cung khác | 3 | 2 | 2 | 2 | 2 | 1 → 2 | 70–122/cung; Tử Tức/Huynh Đệ gần trống |
| Tử Vi: phụ tinh | 3 | 2 | 2 | 2 | 2 | 1 | nhiều sao chưa kiểm cách an |
| Độ sáng | 3 | 2 | 2 | 2 → 3 | 3 | 1 → 3 | 2 bảng tách bạch, 45 ô bất đồng; bài tv-9 |
| Tam phương tứ chính | 2 | 3 (hình học) / 1 (ngữ nghĩa) | 1 | 2 | 3 | 2 | |
| Tứ Hóa | 3 | 2 | 2 | 3 | 2 | 2 | tranh chấp Nhâm-Khoa ghi rõ |
| Cách cục Tử Vi | 2 | 1 | 2 | 2 | 3 | 1 | toàn `draft`, đã kiểm toán riêng |
| Vận hạn Tử Vi | 1 | 1 | 1 | 2 | 2 | 1 | 28 quy tắc không `sourceIds` |
| Bát Tự: Can Chi / Ngũ hành / Thập Thần (tính) | 3 | 3 | 2 | 3 | 3 | 2 | bảng ZZ + test vàng |
| Bát Tự: diễn giải Can/Chi/Thập Thần | 1 | 1 | 1 | 2 | 2 | 1 | từ điển không trích nguồn; TTT chương Can/Chi chưa đọc |
| Bát Tự: vượng suy (TVH 40%) | 3 | 2 | 3 | 2 → 3 | 3 | 1 → 3 | 45/48; bài bt-5 |
| Bát Tự: dụng thần/điều hậu | 2 | 2 | 2 | 2 | 2 | 1 → 3 | bảng không rõ gốc, 9 ô mâu thuẫn nội bộ; bài bt-6 |
| Bát Tự: cách cục | 2 (TVH) / 1 (TBCT) | 2 / 1 | 2 | 2 | 2 | 1 → 3 | 4/24 khớp nguyên văn TBCT; bài bt-7 |
| Nội dung học | 0 → 3 | – | 1 → 3 | 3 | 3 | 2 → 3 | 12 → 24 bài; mọi trích dẫn có test |

---

## 3. Phase 2 — Đối chiếu nguồn

### 3.1 Phép kiểm tự động và bài học về giới hạn của chúng

* **Neo sao–trang (ngây thơ):** tỉ lệ "mọi sao quy tắc nhắc đều nằm trên trang cite" là 97% (KL), 90% (TH), 97% (TT), nhưng **trang giả (lệch 15–60 trang) cũng đạt 44%, 57%, 73%**. Dùng tên đầy đủ thay tên tắt: trang thật 70/46/83%, trang giả 23/17/33%. Kết luận: phép đo này chỉ bắt được lỗi trích dẫn thô; **không được coi là bằng chứng quy tắc đúng**.
* **Xếp hạng trang bằng TF-IDF toàn sách:** trang được cite đứng **hạng 1** ở 78% (KL), 80% (TH), 58% (TT) lượt trích, nằm trong **top 10** ở 96% / 94% / 99%; so với ngẫu nhiên là 1/290, 1/163, 1/170. Đây là bằng chứng mạnh rằng số trang trong dữ liệu *nhìn chung* đúng. Hàng đợi 90 lượt trích có hạng >10 được đọc tay: phần lớn là báo động giả (trang phú ngắn, từ vựng khác văn diễn giải), và **tỉ lệ quy tắc có chênh lệch trong hàng đợi (21%, 8/39) không cao hơn mẫu ngẫu nhiên (24%, 31/127; riêng từng sách 19–33%)**. Tức phép tìm trang **không** dự báo được quy tắc lệch điều kiện.
* **Hệ quả:** muốn biết một quy tắc có đúng với sách hay không chỉ có cách mở trang và so từng điều kiện (§3.2).

### 3.2 Đọc nguyên văn: 204 quy tắc

Mẫu: ngẫu nhiên ≈9%/gói (tối thiểu 3), cộng 39 quy tắc do phép tìm trang nghi ngờ, cộng toàn bộ 28 quy tắc dựa trên Trích Thiên Tủy. Kết quả (chưa điều chỉnh số liệu theo kích thước gói):

| Phân tầng | Khớp | Một phần | Sai trang | Đọc sai | n |
|---|---|---|---|---|---|
| KL ngẫu nhiên | 27 | 7 | 0 | 0 | 34 |
| TH ngẫu nhiên | 30 | 13 | 1 | 1 | 45 |
| TT ngẫu nhiên | 39 | 9 | 0 | 0 | 48 |
| ZZ ngẫu nhiên | 8 | 2 | 0 | 0 | 10 |
| Bị phép tìm trang nghi (KL/TH/TT) | 31 | 6 | 1 | 1 | 39 |
| Trích Thiên Tủy (toàn bộ) | 20 | 8 | 0 | 0 | 28 |
| **Tổng** | **155** | **45** | **2** | **2** | **204** |

Chỉ riêng quy tắc `verified` trong mẫu ngẫu nhiên: **81% khớp** (KL 83%, TH 74%, TT 84%, ZZ 78%); quy tắc `draft` trong mẫu ngẫu nhiên: 11/22 khớp (nhãn `draft` hợp lý). 200/204 trích dẫn được máy xác nhận nằm trên trang; 4 trích dẫn đọc từ ảnh trang không kiểm được bằng máy.

Mỗi mục bằng chứng có: sách, trang, **nguyên văn** (≤30 từ), cách đọc (lớp chữ hay ảnh), bản dịch tiếng Việt (bắt buộc với chữ Hán), **bối cảnh** (giọng của ai, mục nào, có rào đón không), **điều kiện sách nêu mà quy tắc thiếu**, chỗ lệch và cách sửa tối thiểu, và ghi chú trường phái khi chính trang đó cho thấy bất đồng. Xem trên `/reference` hoặc `GET /api/evidence`.

### 3.3 Những phát hiện đáng chú ý

**A. Lỗi thật, đã xử lý (hạ `draft` hoặc sửa số trang)**

| Quy tắc | Phát hiện | Xử lý |
|---|---|---|
| `TV_TH_AUX2_TAI_BACH_MO`, `TV_TH_AUX2_DIEN_TRACH_MO` | TH tr.59: câu "tần tiện, chịu dành của chô dấu" nói về sao **Tử** (mục 8), không phải sao **Mộ** (mục 9, chỉ "đần độn, ngu si"). Lớp chữ PDF đảo thứ tự dòng nên dễ nhầm; chỉ ảnh trang mới rõ. Quy tắc anh em ở Điền Trạch cùng lỗi (truy từ mẫu) | hạ `draft`, ghi chú trong mô tả |
| `TV_TH_MV_MENH_TU_SAT_VUONG` | TH tr.86 in "**Tứ** Sát vượng địa đã đành minh huy" (bốn sát tinh); quy tắc đọc thành "Tử, Sát" (Tử Vi + Thất Sát). Không có câu nào về Tử Vi + Thất Sát ở tr.80-89 | hạ `draft` |
| `TV_KL_STAR_PHU_MAU_TV_SANG` | đoạn ở cuối tr.75, không phải tr.76 | sửa số trang |
| `TV_TH_CACH_MENH_NHAT_MAO` | mục 23 ở tr.72, không phải tr.73 | sửa số trang |
| `quyen_quy_cong_khanh` (claim) | lỗi chính tả "khuynh hướng khuynh hướng" hiện trên giao diện thật | sửa claim + trình sinh |
| `engine/data/sources.json` | ghi KL "p.36", TT "PDF pp.21-40", ZZ "chỉ bảng" trong khi quy tắc cite tới tr.246/163/74 | cập nhật phạm vi trang thật |

**B. Báo động giả quan trọng (bài học phương pháp):** hai quy tắc (`TV_KL_PHU_TU_PHU_TUAN_TRIET`, `TV_TH_AUX_MENH_HL_TU_MO`) bị người đọc báo "đảo cực" vì họ chỉ thấy câu trung tính của claim, trong khi quy tắc có `effect: limit` và giao diện dùng câu `limit:<id>` ("phúc lộc kém đi"). Chủ trì đối chiếu lại: cấu hình **đúng**. Lỗi này cũng bị phát hiện ở chính công cụ của đợt kiểm: `build_reference.py` ban đầu bỏ qua `limit:`. Test `test_limit_findings_use_the_limit_phrasing_the_ui_shows` giữ điều này.

**C. 45 chỗ "khớp một phần" (chưa sửa)** — nhóm lỗi lặp lại:
* Điều kiện **rộng hơn trang**: bắt "một trong hai sao" khi sách nêu cặp (Tả *và* Hữu, Quyền *và* Lộc, Không *và* Kiếp), bắt miếu/vượng/đắc khi sách chỉ nói "nhập miếu".
* Điều kiện **thiếu rào đón của trang**: "có sát tinh" khi sách đòi nhiều sát tinh; thiếu ngoại lệ Tham/Vũ (TH tr.52); thiếu điều kiện nam/nữ khi mục phú nằm dưới "A. Nam mệnh".
* **Từ ca thành luật:** `TV_KL_CASE_TAI_BACH_THAI_TUE` biến lời bình một lá số cụ thể (KL tr.246) thành quy tắc cho mọi lá số.
* **Mạnh/yếu hơn trang:** "sung túc, nhiều người giúp" khi TT tr.45 chỉ nói "cao sang".
Toàn bộ trong `docs/source_audit_findings.csv` (69 dòng gồm cả 24 mục TBCT), mỗi dòng có "sửa tối thiểu", **lớp thay đổi** (`fix_class`) và **tỉ lệ trong 300 lá số ngẫu nhiên mà quy tắc đang chạy** (`pct_random_charts_firing_now`, `tools/measure_fix_impact.py`). Đã áp: (1) lời claim của 3 quy tắc nháp mà claim không dùng chung (`TV_TH_P2_TAI_BACH_TT`, `TV_TH_MV_MENH_KHOI_XUONG_LANH`, `TV_TH_P2_TU_TUC_NHAT_DUONG`) và (2) ghi chú vào mô tả của cả 45 quy tắc. Hai quy tắc có claim dùng chung với quy tắc khác (`TV_KL_CUNG_MENH_GIAP_TA_HUU`, `TV_TT_MENH_TA_HUU_DONG_CUNG`) không sửa lời vì sẽ đổi câu của quy tắc kia hoặc tách thẻ gộp nguồn. **Chưa áp 40 quy tắc còn lại** (siết, nới hoặc viết lại điều kiện, hoặc cần sự kiện mới): mỗi sửa đổi đầu ra của engine và cần chủ dữ liệu quyết (§ Roadmap R1).

**D. Giọng và lớp của nguồn.**
* *Trích Thiên Tủy*: trong 28 quy tắc đối chiếu, mọi đoạn đỡ nằm ở **lời bình của Nhậm Thiết Tiều**, không có đoạn nào ở dòng nguyên chú của Lưu Bá Ôn. Nhãn "Lưu Bá Ôn / Nhậm Thiết Tiều" trong registry che mất điều này.
* *Toàn Thư*: có lớp phú cổ và lớp lời giải của dịch giả; bằng chứng ghi rõ quy tắc đỡ ở lớp nào (ví dụ `TV_TT_PHU_MENH_VU_TU_MO` đỡ bởi lời giải).
* *Khảo Luận*: tác giả tự dặn ở tr.49 rằng có câu phú "ngày nay không còn dùng được" và cần "áp dụng hợp tình hợp lý"; một số mục là bình một lá số mẫu chứ không phải luật.
* *Tự mâu thuẫn trong một cuốn*: TT tr.27 ("buôn bán lớn") vs tr.77 ("cần tĩnh thủ") cho Vũ Khúc ở Thiên Di; TT tr.40 viết "Canh, Quí" trong văn xuôi nhưng "Giáp và Quí" trong lời giải phú.

### 3.4 Tử Bình Chân Thuyên: 24 định nghĩa viết theo trí nhớ

Đọc bản chữ Hán `東里書齋` (có ghi dị bản 秘本/中州本), đối chiếu máy chủ thứ hai (Sina; 20/24 trích dẫn khớp ≥0,8). ctext.org trả thử thách bot, không vượt. Kết quả: **khớp 4, một phần 20, không có mục nào hoàn toàn bịa**.

Những chỗ đáng chú ý:
* **Thiên Ấn · `kieu_doat_thuc` đi ngược văn bản**: 論用神 bác cách hiểu "thiên ấn thấu thực là kiêu đoạt thực" (coi là 洩身之秀); Kiêu đoạt Thực là bại của cách **Thực Thần**.
* **Âm Nhận** (ánh xạ dùng lại định nghĩa Dương Nhận) **không có trong văn bản**: 論陽刃 chỉ nói "惟五陽有之".
* **Chính Quan**: hệ thống cho cả Tài lẫn Ấn cứu Thương-kiến-Quan; văn bản chỉ cứu bằng Ấn và dặn kỵ gặp Tài khi dùng Ấn.
* "Tài Quan song mỹ" **không phải tên có trong văn bản** (văn bản mô tả "財旺生官…不透傷官，不混七煞").
* Văn bản coi nhiều điều kiện theo khí hậu mùa (冬金傷官生財不貴…) mà các vị ngữ của engine không mô hình hóa.
Chi tiết và URL từng chương: `engine/data/source_evidence_web.json`, hiển thị ở `/reference#bt`.

### 3.5 Phân loại khẳng định (đã đưa vào giao diện)

| Loại | Ví dụ | Nhãn hiển thị |
|---|---|---|
| Tính toán lịch pháp/thiên văn | Can Chi giờ ngày, tiết khí, vị trí sao | (không gắn nhãn tin cậy: kiểm bằng oracle) |
| Quy tắc truyền thống có nguồn | "Tử Phủ đồng cung ở Dần/Thân: đời sống thuận lợi" (KL tr.49) | Đã đối chiếu / Khớp một phần / Có nguồn |
| Vận hành hóa của hệ thống | ngưỡng 40%, nghĩa của "hội", chỉ số nhiệt hàn–noãn | trong bài học và trang nguồn; quy tắc mang `draft` |
| Giả thuyết thử nghiệm | cách cục nháp, Phi Hóa, TBCT từ trí nhớ | Nháp / Giả thuyết |

Số quy tắc theo nhãn hiện nay (đếm theo quy tắc, gồm cả Bát Tự): **Đã đối chiếu 125, Khớp một phần 29, Có nguồn 1.030, Nháp 179, Giả thuyết 72**.

---

## 4. Phase 4 — Kiểm tra học thuật và nhất quán

* **Nguồn độc lập, không tự tạo nguyên văn.** Quy trình bắt buộc: người đọc chép từ kết quả công cụ; `validate` đọc lại PDF và từ chối trích dẫn không nằm trên trang (200/204 đạt, 4 đọc từ ảnh bị đánh dấu "không kiểm máy"). Test `test_quotes_sit_on_their_pages` chạy lại việc này khi có sách; bài học (`lessons_deep.json`) có 14 trích dẫn sách in được kiểm lại bằng test, và các trích dẫn Hán văn TBCT phải trùng tệp bằng chứng web.
* **Nhất quán diễn giải ↔ engine.** `test_reference.py`: dữ liệu `/reference` được sinh từ gói quy tắc và phải trùng bản đã commit; bảng độ sáng và số ô bất đồng trùng `dignity.compare`; quy tắc `limit` dùng đúng câu của giao diện; quy tắc đã hạ `draft` không còn xuất hiện ở mức "có nguồn". `test_lessons_deep.py`: mọi số liệu trong bài học (`stat`) phải trùng nguồn đo (`docs/reading_base_rate.json`, `reference.json`, hoặc có trong `docs/BAZI_DEEP_BOOKS.md`); số nhận định của lá số Hán Cao Tổ được tính lại từ engine; ví dụ Tham Lang ở Ngọ trùng bảng; không có câu tiên đoán số phận trong bài học.
* **Nhãn giả thuyết.** Không quy tắc nào được nâng nhãn. Ba quy tắc bị hạ. Định nghĩa TBCT giữ `draft` (test khẳng định).
* **Không trình bày dự đoán như sự thật.** Bài rs-4 và tab "Nguồn và giới hạn" nói thẳng: chưa có phép thử nào, lá số nào cũng "khớp", và những loại câu bị loại khỏi hệ thống.
* **Hồi quy.** `pytest` toàn bộ: 1.212 đạt, 1 bỏ qua, 3 xfail (khoảng trống đã ghi nhận từ trước, không liên quan), 0 lỗi. Trình duyệt: các bài học và `/reference` được mở và kiểm tra ở cỡ máy tính và 375 px (không tràn ngang, bảng cuộn trong khung), không có lỗi console.

---

## 5. Những gì đợt này thay đổi

**Dữ liệu tri thức:** 45 mô tả quy tắc gắn ghi chú "khớp một phần"; 3 claim nháp sửa lời; `docs/source_audit_fix_impact.json` + `tools/data/fix_classes.json` (lớp thay đổi và tần suất); `engine/data/source_evidence.json` (mới), `source_evidence_web.json` (mới), `reference_editorial_vi.json` (mới), `sources.json` (cập nhật locator), `claims_vi.json` (sửa 1 câu), `pack_thuc_hanh_aux2.json`, `pack_thuc_hanh_menh_verse.json` (3 quy tắc → `draft`, ghi chú), `pack_khao_luan_stars.json`, `pack_thuc_hanh_cach.json` (số trang).

**Nội dung/UI:** `engine/web/reference.html` (mới), `js/reference.json` (sinh), `js/lessons_deep.json` + phần hiển thị trong `js/learn.js` (12 bài), `css/learn_deep.css`, liên kết "Tra cứu có nguồn" trong cửa sổ giải thích thuật ngữ. API: thêm `GET /reference`, `GET /api/evidence` (chỉ thêm, không đổi hợp đồng cũ).

**Không đổi:** mã tính toán lịch pháp, an sao, Bát Tự; lược đồ API hiện có; nhãn và id trường phái; các biến thể cách cục.

---

## 6. Rủi ro còn lại

1. **Chưa có người kiểm thứ hai.** Mọi "Đã đối chiếu" là một lần đọc của một mô hình AI + kiểm máy.
2. **Mẫu 204/1.622.** 1.030 quy tắc "Có nguồn" chưa được đọc riêng từng câu; ước lượng 17% có lệch điều kiện áp dụng cho cả nhóm này với khoảng tin cậy rộng.
3. **45 chỗ lệch điều kiện còn nguyên** trong engine; chúng vẫn hiện ở chế độ "Chuyên sâu" kèm nhãn "Khớp một phần" trong trang tra cứu, nhưng **chưa** kèm nhãn đó trên thẻ kết quả của lá số.
4. **TBCT chỉ đọc qua bản web**, không phải sách in.
5. **Từ điển thuật ngữ vẫn viết tay không nguồn** (hình ảnh Can, Chi, tính chất sao).
6. Phần "Cơ sở lặp" dùng từ khóa; con số chính xác phụ thuộc tập từ khóa (99% / 100% thay đổi nhẹ khi đổi từ khóa, kết luận không đổi).

---

## 7. Danh sách tệp công cụ

| Tệp | Việc |
|---|---|
| `tools/audit_knowledge_base.py` | kiểm kê → `docs/knowledge_audit.json` |
| `tools/audit_source_anchors.py` | neo sao–trang, kèm kiểm đối chứng trang giả |
| `tools/audit_citation_retrieval.py` | xếp hạng trang được cite |
| `tools/show_page.py` | xem chữ/ảnh một trang sách (KL, TH, TT, ZZ, TTT, TVH) |
| `tools/build_source_evidence.py` | `batches` (tạo mẫu) / `validate` (kiểm máy trích dẫn) |
| `tools/apply_evidence_corrections.py` | áp sửa lỗi có căn cứ (chạy sau các trình sinh gói) |
| `tools/export_audit_findings.py` | `docs/source_audit_findings.csv` |
| `tools/measure_reading_base_rate.py` | `docs/reading_base_rate.json` |
| `tools/build_reference.py` | `engine/web/js/reference.json` |

## 8. Chạy lại

```bash
.venv/bin/python tools/audit_knowledge_base.py --out docs/knowledge_audit.json
.venv/bin/python tools/audit_source_anchors.py            # cần sách trong ~/Downloads hoặc $TVBT_BOOKS_DIR
.venv/bin/python tools/audit_citation_retrieval.py
.venv/bin/python tools/measure_reading_base_rate.py 400 --out docs/reading_base_rate.json
.venv/bin/python tools/apply_evidence_corrections.py      # sau khi chạy bất kỳ trình sinh gói nào
.venv/bin/python tools/build_reference.py
.venv/bin/python tools/export_audit_findings.py
cd engine && ../.venv/bin/python -m pytest -q
```
