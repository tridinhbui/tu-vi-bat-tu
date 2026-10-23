# Bát Tự: đọc sâu hơn, chặt hơn (2026-10-22/23)

Mục tiêu: bài luận Bát Tự sâu hơn về nội dung (cơ chế, điều kiện, chỗ vênh và cách cân), không phải dài hơn. Không có câu LLM lúc chạy; mọi câu
mới là dữ kiện tính được, một cơ chế có trang sách, một lời sách có mã quy tắc, một lời kết của hệ thống nhắc lại điều đã nói, hoặc một câu
minh họa gắn vào đúng một câu có nguồn.

## 1. Đo trước khi sửa (corpus1000)

Công cụ: `tools/interpret/bazi_deep_audit.ts <corpus.json.gz>`. Corpus = 1.000 ngày sinh của `src/interpret/test/fixtures/corpus1000.json.gz`,
facts Bát Tự **tính lại** bằng engine của từng bên (fixture trong repo còn facts trước Track C, không phản ánh bản đang chạy). "Trước" =
code và engine của main 8a47abc; "sau" = nhánh này. Văn = `checkedOnly(proseBazi(...))`, đúng như người đọc nhận.

Định nghĩa (tự động, không phải đánh giá của thầy):
- **đơn vị phân tích** = câu mang lời sách hoặc dữ kiện tính được (basis `sach` / `tinh_toan`); minh họa và lời kết của hệ thống không tính.
- **kết luận** = câu `he_thong` hoặc bước verdict / conclusion / closing; **kết luận trơ** = kết luận mà đoạn của nó không có câu nào nói *vì sao*
  (câu có nguồn mang từ nối nhân quả, hoặc `trace.mech`).
- **độ phủ cơ chế** = tỉ lệ đoạn có kết luận mà cũng có câu cơ chế.
- **strip sim** = trung vị Jaccard bộ ba từ giữa bài của hai lá số khác nhật chủ, đã bỏ tên can, chi, hành, thập thần và con số (thấp = ít khuôn sáo).

| Chỉ số (trung bình / lá số) | Trước | Sau |
|---|---|---|
| Số từ | 2.370 | 3.407 |
| Đơn vị phân tích | 68,6 | 99,4 |
| Từ trên một đơn vị phân tích | 34,6 | **34,3** (không tệ hơn) |
| Kết luận / kết luận trơ | 19,8 / 15,1 | 21,7 / **11,8** |
| Độ phủ cơ chế | 0,32 | **0,66** |
| Strip sim | 0,350 | **0,331** (không tệ hơn) |
| Câu minh họa | 0 | 2,5 |

Đơn vị phân tích theo chương (trước → sau): nhật chủ 8,6 → 15,1; ngũ hành 1,0 → 4,4; sự nghiệp 1,8 → 2,3; quan hệ 4,3 → 4,3; đại vận 30,8 →
38,3; cách cục 10,3 → 15,2; lưu niên 11,7 → 19,8; tổng kết 0 → 0 (chỉ lời kết).

### Cấu trúc đã tính mà văn không nói (trước → sau, tỉ lệ lá số có cấu trúc ấy mà văn có nói)

| Cấu trúc (đã có trong engine) | Có ở | Trước | Sau |
|---|---|---|---|
| Khoảng cách tới mốc 40% tính bằng độ | 100% | 0% | 100% |
| Phần cộng / trừ của hành nắm lệnh, và lệnh có quyết định kết luận không | 100% | 4% | 99% |
| Chỗ dựa (gốc) của nhật chủ, tên từng can tàng | 100% | 0% | 74% |
| Can hợp: hóa hay không, vì sao (TVH tr.336), bên nào yếu đi | 46% | 8% | 77% |
| Thập thần sinh khắc nhau trên thiên can (Tài sinh Quan Sát, Ấn sinh thân…) | 100% | 7% | 44% |
| Vì sao dụng thần là nhóm ấy | 89% | 13% | 70% |
| Dụng thần trong tứ trụ: bị khắc / hợp / xung, được sinh | 89% | 0% | 67% |
| Lời chú của ô điều hậu (tr.391-397) | 100% | 0% | 97% |
| Can quản năm năm đầu, chi năm năm sau (tr.382) | 100% | 0% | 97% |
| Đại vận chạm vào dụng thần của nguyên cục | 100% | 2% | 88% |
| Chiều đi giữa các vận (mốc chuyển) | 100% | 0% | 87% |

### Lặp lại giữa các lá số khác nhau (trước)

Những khung câu xuất hiện ở gần mọi lá số: câu mở mỗi năm (96%), "về khí hậu, can … là một can điều hậu" (90%), "nhìn chung vận … khá thuận"
(78%), và câu về mức tin cậy của hai bảng "…chính Thiệu Vĩ Hoa ghi là do một độc giả gửi…" (73%, lời về phương pháp nằm ngay trong văn).
Sau: câu tin cậy về phương pháp chuyển vào ghi chú của câu; khung mới có 2–3 biến thể; strip sim giảm.

### Kết luận không kèm lý do (trước), ví dụ trên lá 09/01/2002

- "Can Mậu và chi Tuất cùng thuộc nhóm Thực Thương, nhóm vận xấu." — không nói vì sao Thực Thương xấu với lá này.
- "phe trợ nhật chủ chiếm khoảng 26%, dưới ngưỡng 40%" — không nói 26% đến từ đâu, thiếu bao nhiêu, lệnh tháng góp gì.
- "Bảng dụng thần … dụng thần là Tỉ Kiếp" — không nói vì sao Tỉ Kiếp.
- "Đinh Dậu … tốt xấu đan xen" — không nói nửa nào tốt, nửa nào xấu.

## 2. Đã làm

**Facts mới** (`engine/tvbt/bazi_deep/depth.py`, nối vào `pipeline.prose_summary` → `facts.bazi.deep.depth`, và mỗi đại vận / năm):
- `score`: điểm Thiệu Vĩ Hoa tháo rời như sách tự trình bày ví dụ (tr.355): phe mình bao nhiêu độ / tổng bao nhiêu, 40% là bao nhiêu, thiếu
  hay dư bao nhiêu (quy ra số can có chỗ dựa, 36 độ, tr.332), thiên can / địa chi, hành nắm lệnh +1/5 và hành bị nó khắc −1/5, bỏ lệnh thì
  kết luận có đổi không.
- `stems`: độ từng can và vì sao đổi (chỗ dựa / hư phù tr.333, ngũ hợp hóa hay không theo điều kiện 1 tr.336, khắc gần / cách ngôi / kẹp tr.332,
  can–chi cùng trụ); chỗ dựa của nhật chủ theo tên can. `tvh_score.score` thêm `detail` (không đổi con số; đã chạy lại toàn bộ test TVH).
- `units` (tam hội / tam hợp / bán hợp / lục hợp: hóa hay không), `flow` (nhóm theo độ, mạch sinh trên thiên can).
- `yong`: dụng thần với lý do của sách (tr.378-383, `data/bazi_deep/tvh_mechanism.json`), thứ tự thay thế "không có X thì lấy Y" (có dữ
  kiện X trong tứ trụ hay không), chỗ dụng thần đứng, cái khắc / hợp / xung / sinh nó trong tứ trụ, hỉ thần và kị thần theo định nghĩa tr.382,
  và chỗ định nghĩa ấy vênh với danh sách vận của cách.
- mỗi đại vận / năm: `halves` (tr.382), `touch` (điều nó làm với dụng thần, tr.382), `why` (lý do bảng xếp nhóm ấy là vận tốt / xấu, tr.377-382),
  `luck_half` (năm nằm ở nửa nào của vận), `vs_luck` (năm đặt cạnh chính đại vận).
- `dh_note`: lời chú của ô điều hậu, chép từ tr.391-397 cho đủ 120 ô (`tvh_dieuhau.json` `notes_text`), lần theo "như tháng X".

**Văn** (`src/interpret/prose/bazi_deep.ts`, `bazi.ts`, khung trong `content/prose/bat_tu.json`):
- mỗi chương: đoạn đọc ngắn trước, phần cơ chế đánh dấu `depth: 'sau'`, báo cáo gập dưới "Đọc sâu" (`report.js` `btProseHtml`).
- không còn tên sách, trang, "bảng", "phép chấm điểm" trong văn; nguồn ở ghi chú từng câu và mục Căn cứ.
- mỗi lời xếp vận tốt / xấu đi liền lý do trong cùng câu; vận "đan xen" nói rõ nửa đầu (can, năm a–b) và nửa sau (chi, năm c–d).
- chỗ hai phép vênh nhau (bảng theo cách / điều hậu; danh sách vận / định nghĩa hỉ kị) được nói và cân rõ; đặc biệt cách tòng (khớp nhiều cách
  đặc biệt: nói cách nào được theo), hóa khí (nhật chủ đã hóa: tính theo hành hóa), sát ngưỡng ("hơi vượng/nhược", ghi chú dải ±3% là của hệ thống),
  nhóm nhiều nhất không có dòng trong bảng (nói thẳng là xét theo nhóm kế tiếp).
- tổng kết: chẩn đoán một câu (chỗ lệch → thuốc), các chặng, mốc chuyển, lời khuyên chung.
- **minh họa** (chính sách 2026-10-22): `trace.basis = 'minh_hoa'`, `trace.attach` = bước của câu có nguồn; `checked.ts` bỏ câu minh họa nếu
  câu được gắn không còn hoặc không phải câu sách / tính toán; báo cáo dán nhãn "minh họa" ở từng câu và liệt kê ở mục Căn cứ.

## 3. §Correctness (rà soát của chủ dự án, 2026-10-22)

Mỗi điểm sửa tận gốc, có test hồi quy trên lá 09/01/2002 04:30 nam: `src/interpret/test/bazi_reconcile.test.ts` ("owner review 2026-10-22…")
và `engine/tests/test_bazi_deep_depth.py` (`test_owner_review_*`).

1. **Cách cục có hai trạng thái trái nhau.** `analysis.py` nói "không xác định cách cục", bài luận lại dùng cách Thiên Tài để lấy dụng thần.
   Quyết định một trạng thái: **xác lập một phần** (`yongshen.METHOD_META.cach_cuc_tvh.verification = partial`: bảng chép khớp trang in, phép
   định cách mới đối chiếu một phần với tr.356-366). Facts mang `cach_tvh.verification`; `analysis.py` (dòng Bát Tự) nói cùng trạng thái; bài
   luận nói một lần ở chương cách cục, mọi câu xếp vận tốt / xấu của đại vận và năm mang điều kiện "nếu cách Thiên Tài đứng được", câu kết luận
   mang `trace.conditional = 'cach_partial'`, tổng kết nhắc điều kiện; khung phạm vi (`scope.js`) ghi rõ. Lời dẫn của chủ dự án đề nghị nêu tên
   Thiệu Vĩ Hoa trong câu; theo luật đọc dễ (không tên sách trong văn) tên ở ghi chú câu, còn điều kiện nằm trong câu.
2. **Tài vận vênh nhau.** 八字真宗 tr.50 "Thiên Tài thấu can, có gốc: tài vận tốt" xét vị trí; Thiệu Vĩ Hoa xét sức nhật chủ (nhược) và cách
   (vận Tài xấu; "nhật chủ nhược, Tài vượng, có Ấn hoặc Tỉ Kiếp hộ thân: mệnh tốt"). Chương sự nghiệp nay có đoạn ba lớp: vị trí → sức nhật chủ →
   kết luận theo phép (có điều kiện cách), và câu nói điều quyết định là sức nhật chủ và chỗ hộ thân; ghi rõ không trang nào cân hai lời này nên
   chỗ vênh còn mở (thứ tự "lời có điều kiện cụ thể hơn đứng trên" là quy ước của hệ thống, ghi trong note).
3. **Năm × đại vận.** 2027 được kể vào "nên tiến" của Mậu Tuất mà đoạn của chính nó nói "tốt xấu đan xen" (Mùi hình, phá Tuất của vận). Nay:
   bước năm × đại vận tường minh (`vs_luck`: hợp, xung, khắc, lục hợp, hình, hại, phá, bán hợp, phục / phản ngâm theo bảng tr.19-20), nói trong đoạn
   ngắn của năm; danh sách "nên tiến" lấy từ **kết luận cuối của từng năm** (thuận / khá thuận, không thiên khắc địa xung với vận), không còn theo
   nhóm của can năm. Mậu Tuất: 2025, 2026 (trước: 2024, 2026, 2027). Bản TS dự phòng `goodYearsTs` theo cùng quy tắc (test đối chiếu).
4. **Phạm vi kiểm chứng.** Bảng "Điểm nổi bật" chỉ đếm các phát hiện của engine suy luận (3 câu tính cách). Nay chương Tổng quan có mục
   "Phạm vi kiểm chứng của phần Bát Tự" liệt kê **mọi câu** của bài theo chương, mỗi câu kèm nhãn căn cứ (theo sách / tính từ lá số / kết luận của
   hệ thống / minh họa), mã quy tắc và điều kiện; dòng tóm tắt đếm theo căn cứ đặt dưới "Điểm nổi bật". Test: mọi câu có basis hợp lệ, mọi câu
   minh họa gắn được.
5. **Quy ước tuổi.** Mặt Bát Tự dùng một quy ước: **tuổi thực** (số năm từ lúc sinh), ghi ở mọi chỗ có tuổi: văn (đại vận, tổng kết), bảng và
   dải đại vận (`bazi.js`), ô năm trong phần Bát Tự (`ui.js` khi `side === 'bazi'`: "tuổi thực N (tròn tuổi trong năm)"). Tử Vi giữ tuổi mụ, có
   nhãn. Test: không câu Bát Tự nào có "N tuổi" mà thiếu "thực".

## 4. Mở rộng tri thức, có trang

- `tvh_dieuhau.json` `notes_text`: lời chú 120 ô, tr.391-397 (bản scan, đọc 2026-10-22). Phần đưa vào văn bỏ lời phán về người ("tầm thường",
  "quý cách") và 5 câu in lỗi / tối nghĩa (ghi trong `_notes_text`).
- `tvh_mechanism.json`: lý do chọn dụng thần (14 dòng, tr.378-383), bệnh / thuốc (tr.376-377), hỉ / kị thần (tr.382), can năm năm đầu, chi năm năm
  sau (tr.382), bổ cứu bằng vận (tr.377), cách đặc biệt lấy theo thế (tr.381). Test: mỗi dòng lý do khớp một ô của bảng dụng thần.
- Đọc lại tr.331-337 (điều kiện hóa tr.336 dùng để giải thích "hợp mà không hóa"), tr.355 (cách sách tự trình bày độ).

## 5. Còn thiếu (gaps)

- Thiệu Vĩ Hoa không chấm độ cho đại vận, lưu niên: văn không nói vận làm phe nhật chủ lên bao nhiêu phần trăm.
- Ý nghĩa của hình, hại, phá giữa năm, vận và tứ trụ: 八字真宗 tr.19-20 chỉ in bảng; văn chỉ nêu vị trí. Riêng "hợp, xung dụng thần" có nghĩa
  theo tr.382.
- Lời chú điều hậu có điều kiện "thủy nhiều", "mộc vượng"… chưa được vận hành thành ngưỡng (chỉ "X cục" được kiểm bằng tổ hợp chi của điểm TVH).
- Dòng hỉ / kị của vận theo từng cách (tr.382-386) còn có lời điều kiện (ví dụ "vận gặp Ấn thì Tài và Ấn không làm trở ngại nhau mới tốt", tr.383)
  chưa nhập thành dữ liệu.
- Phép định cách tr.356-366 chưa đối chiếu từng dòng với `geju.py` (lý do trạng thái "một phần").
- Lục thân của cả hai sách chưa đọc; Trích Thiên Tủy các chương Thiên Can, Địa Chi, Thể Dụng chưa đọc.
- Phép phù ức vẫn là nháp, không vào văn.
- Thứ tự "lời cụ thể hơn đứng trên" khi 八字真宗 và Thiệu Vĩ Hoa vênh (Tài vận) là quy ước hệ thống, chưa có trang.

## 6. Cổng (gate) — sáu lá số

Văn đầy đủ trước / sau: `docs/examples/bazi-deep-{2002,1911,1971,tong_1981,near_1998,hoa_1982}.md`.

| Lá số | Đơn vị phân tích | Từ / đơn vị | Kết luận trơ | Độ phủ cơ chế |
|---|---|---|---|---|
| 09/01/2002 04:30 nam | 71 → 108 | 35,0 → 36,4 | 12 → 11 | 0,53 → 0,75 |
| 01/01/1911 12:30 nam | 76 → 102 | 36,4 → 36,2 | 13 → 12 | 0,47 → 0,67 |
| 24/05/1971 10:30 nam | 68 → 102 | 34,1 → 35,0 | 16 → 11 | 0,27 → 0,75 |
| 06/01/1981 09:00 nữ (Tòng Tài) | 67 → 100 | 33,7 → 32,1 | 15 → 10 | 0,33 → 0,75 |
| 17/03/1998 15:00 nam (40,3%) | 67 → 96 | 37,3 → 34,1 | 15 → 11 | 0,33 → 0,67 |
| 23/02/1982 07:45 nam (Hóa Mộc) | 65 → 91 | 31,6 → 31,4 | 16 → 10 | 0,27 → 0,73 |

(Số đo trên từng lá trước đợt sửa §3; corpus1000 ở §1 là số sau cùng.)
