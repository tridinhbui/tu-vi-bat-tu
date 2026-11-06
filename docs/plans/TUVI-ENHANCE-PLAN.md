# Kế hoạch nâng cấp toàn bộ luận giải Tử Vi

Lập ngày 06/11/2026 trên `main` 302a3385. Áp dụng cho phần luận giải miễn phí đối chiếu sách (không dùng mô hình ngôn ngữ). Luận riêng ba mức được nhắc ở giai đoạn 9.

## 1. Giữ nguyên các nguyên tắc

- Mỗi câu người đọc thấy đều dựa vào dữ kiện lá số cộng với một câu sách có ghi trang, hoặc một quy ước của hệ thống có gắn nhãn.
  - Không đưa văn phổ thông ra người đọc.
  - Phần miễn phí không dùng mô hình ngôn ngữ.
- Không ghi tên sách, số trang hay chữ "hệ thống" vào lời văn. Những thứ đó nằm trong phần "căn cứ" mở ra khi bấm vào câu.
- Không đoán sự kiện (năm cưới, ly hôn, bệnh). Cung Tật Ách chỉ cân sao cứu giải và sao gây sức ép, không phán tốt hay xấu.
- Bảng sáng tối mặc định theo Khảo Luận. Tiểu hạn mặc định theo Khảo Luận trang 39–40.
- Kiểm thử gọn:
  1. `npm run check:prose` trước.
  2. Sau đó chỉ chạy test của các phần đã sửa.
  3. Chạy toàn bộ test đúng một lần trước khi đẩy lên `main`, và chạy tách nền (`nohup`).

## 2. Hiện trạng đo được hôm nay

### Độ dài từng chương trên hai lá số mẫu

Hai lá số mẫu là 09/01/2002 (nam, Khảo Luận) và 02/03/1991 (Cự Môn ở Tuất). Số liệu theo dạng "lá 2002 / lá 1991".

| Chương | Số chữ | Ghi chú |
|---|---|---|
| Tổng quan lá số | 131 / 181 | chỉ nói độ số và Mệnh–Cục, chưa có chân dung |
| Mệnh | 1.082 / 1.192 | dày nhất |
| Quan Lộc, Tài Bạch, Phu Thê | 436–682 | |
| Thiên Di, Phúc Đức, Nô Bộc, Tử Tức | 233–337 | |
| Huynh Đệ, Phụ Mẫu | 163–246 | mỏng nhất |
| Vận hạn | 3.114 / 2.573 | khoảng một nửa số câu là câu hệ thống |
| Cách cục | 132 / 59 | |
| Tổng luận | 228 / 252 | gần như toàn câu hệ thống |

### Chất lượng câu chữ

Đo bằng `eval_deep3`, 300 lá số, và `check:prose`, 23 lá số.

| Chỉ số | Hiện tại | Ngưỡng / ghi chú |
|---|---|---|
| Câu dài quá 35 chữ (`check:prose`, cả Bát Tự) | 10,1 % | test chỉ cho phép ≤ 5 % |
| Tỉ lệ câu khung và câu hệ thống: Tài Bạch | 40,3 % | |
| Tỉ lệ câu khung và câu hệ thống: Cách cục | 43,4 % | |
| Cách cục: câu lặp nguyên văn giữa các lá số | 29,4 % | |
| Cách cục: khung câu lặp | 44,3 % | |

Ví dụ câu lặp ở Cách cục:
- "Thêm nữa, chính tinh của cách không nhập miếu…" xuất hiện trên 58/300 lá số.
- "Mệnh thành cách Sát Phá Liêm Tham." xuất hiện trên 53/300 lá số.

Vận hạn còn lặp cùng một khung câu qua mười đại hạn: theo đo trước, 3,57 câu lặp nguyên văn mỗi bản luận.

### Lỗi hiển thị

Cụm "(KL p.47)" lọt vào lời văn của chương Cách cục, gặp trên cả hai lá số mẫu.

### Thiếu dữ liệu sách

Số liệu trên 1.000 lá số, lấy từ các tài liệu audit:

| Mục | Số liệu |
|---|---|
| Chương Huynh Đệ không có gì để luận | 39 lá số |
| Chương Tử Tức không có gì để luận | 9 lá số |
| Chương Điền Trạch không có gì để luận | 15 lá số |
| Câu sách đã kiểm mà không bao giờ được nói: Tài Bạch / Phu Thê | 256 / 525 |
| Tứ Hóa ở trong cung mà không được nhắc: Phu Thê / Điền Trạch | 74 / 127 |
| Cặp chính tinh đồng cung không được luận chung: Quan / Tài / Phu / Điền | 29 / 30 / 43 / 99 |
| Gói Hàm Số phần Mệnh (766 câu) | còn để riêng, chưa nạp |
| 257 câu "tham khảo" của Hàm Số | chưa vào bảng tính chất sao |

### Suy luận

- Biểu đồ vận hạn và bảng kết luận ngược chiều nhau ở 13,2 % số cặp (đo trên 1.124 cặp).
- Câu "chưa phân xử" tăng từ 4,50 lên 4,99 mỗi bản luận sau khi nạp Hàm Số.
- 16 chỗ Hàm Số nói ngược Toàn Thư. Trong đó 6 chỗ chưa có quan hệ vì điều kiện "trừ" chưa được đọc.

### Vận hạn còn thiếu

- Nhật vận.
- So sao hạn với cung Thân (Khảo Luận trang 234).
- Lưu Tuần, lưu Triệt.
- Tuổi kỵ năm (Thực Hành trang 119).
- Câu văn cho các luật mới ở Thực Hành trang 115–117.
- Khung câu Hóa Quyền, Hóa Khoa của hạn đã có nhưng chưa dùng.

### Chưa có người thẩm định

Mọi số đo đều tự động. Chưa có bộ đoạn mẫu do người viết, chưa có điểm chấm của chuyên gia.

## 3. Đích đến

Mỗi giai đoạn có cổng kiểm tra riêng. Sau giai đoạn 6, toàn bộ bản luận phải đạt các mức sau.

| Chỉ số | Hiện tại | Đích |
|---|---|---|
| Tổng quan lá số | 130–180 chữ | 450–700 chữ, có trục lá số, chân dung, ba điểm mạnh và ba điểm phải giữ |
| Trung vị câu sách mỗi chương: Huynh Đệ, Tử Tức, Phụ Mẫu, Nô Bộc, Thiên Di | 4–7 | ≥ 8 |
| Chương không có gì để luận (1.000 lá số) | tới 39 | < 10 mỗi cung |
| Câu quá 35 chữ | 10,1 % | ≤ 5 % |
| Câu lặp nguyên văn mỗi bản luận | 3,57 | ≤ 1,5 |
| Câu khung và câu hệ thống: Tài Bạch, Cách cục | 40–43 % | ≤ 30 % |
| Vận hạn | 2.500–3.100 chữ | 1.600–2.000 chữ, mỗi đại hạn có điểm chính riêng |
| Biểu đồ và kết luận ngược chiều | 13,2 % | ≤ 5 %, chỗ còn lại có câu giải thích |
| Cặp sao đồng cung, Tứ Hóa trong cung bị bỏ sót | 29–127 | 0 |
| Tên sách, số trang trong lời văn | có | 0 (thêm test) |
| Điểm chuyên gia, thang 5, trên 20 lá số | chưa có | ≥ 4,0 cho Mệnh, Tổng quan, Tổng luận |

## 4. Các giai đoạn

### Giai đoạn 0. Dọn lỗi và lấy số liệu gốc (1 ngày)

**Việc làm**
- Bỏ "(KL p.47)" khỏi lời văn chương Cách cục. Thêm test chặn mẫu `\b(KL|TH|TT|HS|TL|NL) p\.\d` trong mọi câu người đọc thấy.
- Sửa từ nối "Chỉ có điều" để không đặt giữa hai câu cùng chiều xấu.
- Đổi tên "Gốc của…" trong phần Đọc sâu Quan Lộc theo tên mới của mặt thuận.
- Giảm câu Phụ Mẫu "cha mẹ xa cách nhau" lặp trên nhiều lá số: một luật chỉ được nói một lần và phải có điều kiện riêng của lá số.
- Chạy lại `eval_deep3 --n 1000`, `eval_repeat` và `eval_indices` trên `main`. Ghi kết quả vào `docs/audit/TUVI-BASELINE-2026-11.md` làm số gốc cho các giai đoạn sau.

**Cổng kiểm tra:** `check:prose` sạch; test mới về tên sách, số trang đạt.

### Giai đoạn 1. Mở đầu và kết luận (3–4 ngày)

Đây là hai chương người đọc nhớ nhất, nên làm trước.

**Việc làm, chương Tổng quan lá số**
- Viết lại `prose/tong_quan`.
- Trục lá số: một đến hai câu về điều xuyên suốt. Lấy từ:
  - sao trung tâm do `reasonMenh` chọn;
  - cách mạnh nhất ở chương Cách cục;
  - lĩnh vực đứng đầu trong bảng kết luận.
  - Mỗi ý nêu rõ sao, cung.
- Chân dung: mở rộng `portrait()` của chương Mệnh thành 4–6 câu. Gồm tính khí, cách làm việc, cách quan hệ, và chỗ giằng co lớn nhất cùng bên nặng hơn.
- Ba chỗ dựa và ba chỗ phải giữ, xếp theo bảng kết luận, mỗi chỗ một câu lý do.
- Nhịp đời một câu: chặng thuận nhất, chặng khó nhất, bước chuyển lớn nhất (lấy từ chỉ số vận).
- Giữ đoạn độ số đang có, nhưng đưa xuống cuối chương.

**Việc làm, chương Tổng luận**
- Bỏ các câu nói về cách làm, ví dụ "Đặt các lĩnh vực cạnh nhau…" hay "Biểu đồ mười hai cung cho…".
- Thay bằng: thứ tự ưu tiên có lý do, việc nên dựa vào, việc nên lo sớm, mỗi ý kèm cung và sao.
- Lời khuyên vẫn gắn nhãn lời khuyên chung.

**Việc làm, cho biểu đồ khớp với kết luận**
- Khi biểu đồ vận và bảng kết luận ngược chiều, thêm một câu giải thích. Ví dụ: "điểm cao vì vận đẹp, còn bản cung yếu nên kết quả không trọn".
- Hoặc sửa trọng số nếu bên sai là bên tính.
- Tài liệu đo: `docs/INDICES-EVAL.md`.

**Tệp sửa**
- `src/interpret/prose/tong_luan.ts`
- `src/interpret/prose/chapter.ts` (chương Tổng quan)
- `src/interpret/prose/luan.ts` (`portrait`)
- `src/interpret/reason/ledger.ts`
- `src/interpret/indices.ts`
- `content/prose/luan.json`

**Cổng kiểm tra**
- Tổng quan ≥ 450 chữ trên 95 % lá số.
- Không câu nào trong Tổng luận là câu nói về phương pháp.
- Biểu đồ và kết luận ngược chiều ≤ 5 %.
- Golden của lá 2002 được cập nhật, kèm bảng so trước/sau để chủ site duyệt.

### Giai đoạn 2. Làm dày các cung mỏng (5–7 ngày; tách được thành hai phiên chạy song song)

Áp dụng cho Huynh Đệ, Tử Tức, Phụ Mẫu, Nô Bộc, Thiên Di, Tật Ách và Điền Trạch.

**Việc làm**
- Khai thác thêm câu sách cho từng cung. Mỗi câu chép nguyên văn và kiểm trang bằng `tools/book_text.py`.
  - Khảo Luận "X ở các cung" (trang 84–142): các phần còn bỏ qua và các mục "hoặc" có nhiều địa chi.
  - Toàn Thư và Thực Hành: phần luận từng cung.
  - Hàm Số: 257 câu "tham khảo". Phần đúng loại đưa vào `kg/star_nature.json` để giải thích, không thành kết luận mới.
- Mở lớp Đọc sâu (`reason/depth.ts`, `prose/luan_deep.ts`) cho mọi cung còn thiếu. Gồm chế hóa, sao giáp cung, sao chiếu từ tam phương.
- Đọc chung các cặp chính tinh đồng cung (29–99 chỗ bị sót) và Tứ Hóa trong cung (74–127 chỗ bị sót).
  - Quy tắc: nếu cung có cặp sao hay có Hóa thì chương phải nhắc tới, kể cả khi chỉ có câu sách cho từng sao riêng.
- Câu sách đã kiểm mà chưa bao giờ được nói (Tài Bạch 256, Phu Thê 525): xét lại luật chọn câu trong `prose/select.ts`.
  - Câu bị loại vì trùng ý thì ghi lý do.
  - Câu bị loại vì thiếu thẻ khái niệm thì thêm thẻ.

**Tệp sửa**
- `tools/data/*_rules.json` và các tệp pack tương ứng
- `engine/data/kg/star_nature.json`
- `src/interpret/reason/depth.ts`, `src/interpret/prose/luan_deep.ts`, `src/interpret/prose/select.ts`
- `content/prose/concepts_*.json`

**Cổng kiểm tra**
- Trung vị câu sách ≥ 8 cho các cung trên.
- Chương không có gì để luận dưới 10 trên 1.000 lá số mỗi cung.
- Chỉ số Barnum và strip không xấu hơn số gốc. Các ngưỡng nằm trong `readable.test.ts`.

### Giai đoạn 3. Nạp gói Hàm Số phần Mệnh (3 ngày)

**Việc làm**
- Chỉnh chương Mệnh để nhận 766 câu Hàm Số mà không loãng:
  - câu trùng điều kiện với sách khác được nói như lời xác nhận (chứng thêm), không nói lại lần nữa;
  - mỗi khái niệm có trần số câu;
  - tính lại tỉ lệ nền khái niệm theo chuỗi tạo lại dữ liệu ghi trong `docs/audit/HAM-SO.md`.
- Đọc điều kiện "trừ" để xử lý 6 chỗ Hàm Số nói ngược Toàn Thư chưa có quan hệ.

**Cổng kiểm tra**
- Barnum ≤ 0,4055 và strip ≤ 0,0655, cả hai đo trên benchmark20.
- Mọi thay đổi kết luận trên lá 2002 được liệt kê để chủ site duyệt trước khi đẩy.

### Giai đoạn 4. Phối hợp sao và cách cục (4–5 ngày)

**Việc làm**
- Bộ sao có ghi trang:
  - Sát Phá Tham, Tử Phủ Vũ Tướng, Cơ Nguyệt Đồng Lương, Cự Nhật, cùng bố cục Khảo Luận trang 180–186 trong `kg/combos.json`.
  - Mỗi bộ có câu riêng theo vị trí (`per_palace`) thay cho câu chung lặp lại.
- Chương Cách cục:
  - viết lại khung câu để hết lặp nguyên văn (đang 29,4 %);
  - mỗi cách nói được cách đó làm gì cho chính lá số này, qua sao, cung và đại hạn kích hoạt;
  - bỏ câu chép điều kiện của luật.
- Python `formation_eval.py` dùng `formations_verified.json`, và xét cả cung Thân khi định cách.

**Cổng kiểm tra:** Cách cục có tỉ lệ câu khung và câu hệ thống ≤ 30 %, câu lặp nguyên văn ≤ 10 %.

### Giai đoạn 5. Vận hạn gọn và sâu hơn (5–6 ngày)

**Việc làm**
- Mỗi đại hạn chỉ giữ:
  - một câu mức chung, có lý do;
  - hai đến ba việc chính;
  - Tứ Hóa của can hạn;
  - một câu nên làm, có nhãn lời khuyên.
- Câu luật chung ("Chính tinh của cung hạn hãm địa thì xấu…") chỉ nói một lần ở đầu chương, không lặp ở từng hạn.
- Thêm câu văn cho các luật Thực Hành trang 115–117 đã có trong chỉ số.
- Thêm so sao hạn với cung Thân (Khảo Luận trang 234).
- Thêm lưu Tuần, lưu Triệt, tuổi kỵ năm (Thực Hành trang 119), và Hóa Quyền, Hóa Khoa của hạn.
- Lưu niên:
  - năm hiện tại và hai năm tới, mỗi năm có tiểu hạn, lưu Tứ Hóa và các tháng nổi bật;
  - tháng nào không có căn cứ thì ghi "chưa xác định", không bịa ra khác biệt.
- Nhật vận (Khảo Luận trang 41, Thực Hành trang 115): làm sau cùng, chỉ khi đủ căn cứ.

**Tệp sửa**
- `src/interpret/prose/vanhan.ts`, `src/interpret/prose/course.ts`, `src/interpret/indices.ts`
- `engine/data/van_han*.json`
- `tools/interpret/refresh_van_readings.py`

**Cổng kiểm tra**
- Vận hạn 1.600–2.000 chữ.
- Câu lặp nguyên văn trong chương ≤ 1.
- Chỉ số vận được tính lại bằng `index_norms`.

### Giai đoạn 6. Văn phong toàn bản (2–3 ngày, chạy song song với giai đoạn 2–5)

**Việc làm**
- Tách câu quá 35 chữ ở các khung tạo ra câu dài: đưa từ 10,1 % xuống ≤ 5 %.
- Thêm biến thể cho các khung lặp nhiều nhất do `eval_repeat` liệt kê, để câu lặp nguyên văn ≤ 1,5 mỗi bản luận.
- Kiểm từ nối: "Cho dù thế", "Bên cạnh đó", "Cùng thế ấy"… không đứng ở chỗ không có quan hệ đúng nghĩa.
- Bỏ câu rỗng, ví dụ "Cũng từ thế ấy, tốt.". Câu nào cũng phải có nội dung riêng.

**Cổng kiểm tra:** `readable.test.ts`, `eval_repeat` và `eval_deep3` đạt các đích ở mục 3.

### Giai đoạn 7. Phân xử mâu thuẫn (3–4 ngày, cần chủ site hoặc chuyên gia quyết)

**Việc làm**
- Ghi các hàng R02, R04, R06, R10, R11 của bảng mâu thuẫn, theo quyết định của chuyên gia.
- Giải mâu thuẫn thời điểm công danh: "đỗ đạt sớm" và "công danh đến muộn".
- Chỉnh trọng số cân (`domains.json → weigh`) và ngưỡng 0,2.
- Giảm "chưa phân xử" ở những chỗ đã có quan hệ trong sách. Chỗ còn lại phải nói điều gì sẽ quyết định.

**Cổng kiểm tra:** "chưa phân xử" ≤ 3 mỗi bản luận, và câu nào cũng nêu được điều gì sẽ quyết định.

### Giai đoạn 8. Thẩm định bằng người (song song từ giai đoạn 1)

**Việc làm**
- Bộ vàng: chủ site hoặc chuyên gia viết hoặc chọn 15 đoạn mẫu vào `docs/review/human_paragraphs.json`. Hiện mới có 1 đoạn.
- Chấm điểm 20 lá số bằng `tools/interpret/review_kit.ts` (trang `prose-rating.html`), thang 5, cho 5 chương:
  - Tổng quan, Mệnh, Quan Lộc, Phu Thê, Tổng luận.
- Duyệt thẻ khái niệm còn nháp, trong đó có 39 thẻ Hàm Số. Thẻ đã duyệt chuyển sang trạng thái `approved`.

**Cổng kiểm tra:** điểm trung bình ≥ 4,0 cho Tổng quan, Mệnh và Tổng luận trước khi gỡ nhãn "nháp".

### Giai đoạn 9. Nối với Luận riêng (1–2 ngày, sau giai đoạn 1)

- Luận riêng mức 2 và 3 nhận thêm phần trục lá số, bảng kết luận và thứ tự ưu tiên của giai đoạn 1, để bài mô hình viết bám đúng kết luận của sách.
- Chạy thử mức 2 và mức 3 với mô hình thật trên lá 2002, rồi ghi chất lượng, thời gian và chi phí. Việc này cần chủ site đăng nhập.

## 5. Thứ tự và cách chạy song song

```
Giai đoạn 0 ─► Giai đoạn 1 ─► Giai đoạn 3 ─► Giai đoạn 4 ─► Giai đoạn 7
          └─► Giai đoạn 2a (Huynh Đệ, Tử Tức, Phụ Mẫu)  ┐
          └─► Giai đoạn 2b (Nô Bộc, Thiên Di, Tật Ách, Điền Trạch) ┘─► Giai đoạn 5
Giai đoạn 6 chạy suốt; giai đoạn 8 bắt đầu khi giai đoạn 1 xong; giai đoạn 9 sau giai đoạn 1.
```

- Mỗi phiên làm việc chỉ sửa tệp của mình.
- Các tệp sinh ra (`knowledge.json`, `base_rates.json`, chỉ số) chỉ được tạo lại một lần, trên nhánh gộp, theo thứ tự trong `docs/audit/HAM-SO.md`.
- Tổng thời gian ước tính là 4–5 tuần nếu chạy hai đến ba phiên song song. Thời gian chờ chủ site duyệt chưa tính vào.

## 6. Các quyết định cần chủ site

1. Thứ tự ưu tiên: bắt đầu từ giai đoạn 1 (mở đầu và kết luận), hay giai đoạn 2 (các cung mỏng)?
2. Nạp gói Hàm Số phần Mệnh (giai đoạn 3): đồng ý không? Việc này sẽ đổi một số kết luận trên lá 2002, và sẽ được liệt kê trước để duyệt.
3. Ai chấm điểm và viết đoạn mẫu (giai đoạn 8): chủ site, hay mời chuyên gia?
4. Các mục đang chờ từ trước:
   - điều kiện Bị chú trang 117 cho các luật 7a–7i;
   - 45 mục khai thác bị bỏ qua trong `quotes_cung_bay.json`;
   - quy ước chọn sao trung tâm trên lá 1991 (Kình Dương hay Cự Môn);
   - trọng số cân.
5. Độ dài mong muốn của chương Vận hạn: rút còn 1.600–2.000 chữ như trên, hay giữ dài nhưng gọn hơn?
