# Biểu đồ vận "Tổng quan lá số" — đánh giá (indices-3.2.0, 2026-10-24)

## 3.2.0 (2026-10-24): các luật nặng của Thực Hành tr.115-117, lời trung tính; IX.10 bù Kình Đà hãm

Chủ dự án quyết (2026-10-24):

1. Thêm các mục trước đây "chờ duyệt", tức những mục nói chuyện chết, tù, tai nạn, thương tật, bệnh, bỏng, chết đuối, tang. Người đọc chỉ thấy "theo sách rất bất lợi"; sự việc của sách chỉ nằm trong `docs/INDICES-TH115-117.md`. Có test chặn chữ sự việc lọt vào lời đọc.
2. Vế "không hề gì" của IX.10 bù phần hãm của Kình / Đà ở chính cung đại hạn, lưu đại hạn và tiểu hạn của người tuổi Thìn Tuất Sửu Mùi. Mục hãm KL tr.233 vẫn ở trong "Căn cứ", kèm mục bù `KL233_HAM_TH115_IX10` cùng trọng số.

25 luật mới (bên bất lợi, trọng số 1): IX.7, câu đầu IX.8, IX.11, đoán cách 5, thất lợi 6a, 6b, 6d, 6f-6m, 6o, có tang 7a-7i. Câu sau của IX.8 không tính được, vì sách không nói "sao giải cứu" là sao nào. Hai nhãn mới trong `van_han_rules.json`:

- `han: "tieu"` (6i, 6j): chỉ tính ở lớp tiểu hạn;
- `han: "trung_phung"` (IX.7): chỉ tính ở năm có tiểu hạn đứng đúng cung đại hạn đang đi. `van_han.read(..., han=)` dùng cùng nhãn ấy cho lời đọc đại hạn và tiểu hạn.

Cách đọc vị trí sao và số cung khớp của từng luật: xem `docs/INDICES-TH115-117.md`. Luật rộng nhất là 6a (1.356 cung vận trên 1.000 lá: Cơ Nguyệt Đồng Lương hoặc Cự Nhật gặp một sao trong Kình, Đà, Không, Kiếp, Phá Toái, Kiếp Sát). 7c không khớp lá nào.

Kèm theo: merge `main` ở máy (DEEP-3 Tử Vi, Bát Tự). `knowledge.json` và seed D1 được sinh lại; `corpus1000` lấy bản của main rồi tính lại câu đọc vận; golden `menh_cu_tuat.*` được sinh lại.

### Độ khớp (`node tools/interpret/eval_indices.ts`, tiểu hạn theo KL)

| Chỉ số | 3.1.0 (trước merge) | **3.2.0** |
|---|---|---|
| Chặng ở tam hợp Thái Tuế bị vẽ dưới "Trung bình" | 447 / 2.244 (19,9 %), 100 % có giải thích | 499 / 2.244 (22,2 %), 100 % có giải thích |
| Chặng có mức khác chiều lời sách | 2.241 / 10.000, 100 % có giải thích | 1.851 / 10.000, 100 % có giải thích |
| Năm có mức khác chiều lời sách của chính cung | 5.155 / 20.596 | 4.427 / 20.596 |
| Năm khác phía "Trung bình" với chặng của nó | 691 / 20.596, 100 % có giải thích | 726 / 20.596, 100 % có giải thích |
| Chặng / năm thiếu căn cứ | 0 | 0 |
| Năm mức, chặng / năm / tháng | 12 / 21 / 34 / 21 / 12 % | 12 / 21 / 34 / 21 / 12 % |
| Tháng trùng mức của năm | 63,5 % | 64,1 % |
| Tương quan điểm chặng với chất lượng bẩm sinh | 0,165 | 0,182 |
| Radar so với sổ cái (1.124 cặp) | cùng chiều 46,8 %, ngược 13,2 % | cùng chiều 45,6 %, ngược 13,2 % (đổi do merge DEEP-3, radar không đọc luật vận) |

**Số giai đoạn đổi mức** so với 3.1.0 trên cùng corpus đã merge:

- chặng: 2.503 / 10.000 (25 %), trong đó 99 chặng đổi từ hai bậc trở lên;
- năm: 4.811 / 20.596 (23 %), trong đó 72 năm đổi từ hai bậc trở lên.

Lý do: 25 luật đều ở bên bất lợi. Thang vẫn chia theo phân vị, nên năm mức giữ 12 / 21 / 34 / 21 / 12 %; chỉ thứ tự giữa các giai đoạn thay đổi.

Số lá có luật mới vào biểu đồ (đại vận hoặc năm): 6a 832, 7i 395, IX.10 bù hãm 339, 6k 299, 7g 286, 6b 240, DC5 188, IX.8 185, 6d 147, 7d 107, 7b 59, 7f 55, 6l 44, 6h 26, 7e 15, IX.11 15, 6i 14, 6j 15, IX.7 13, 6f 8, 7h 7, 6o 6, 6g 3, 7a 2, 6m 1.

Việc còn mở: (1) Bị chú tr.117 nói muốn đoán tang thì cách phải có sẵn ở cung Phụ Mẫu. Hệ thống không đoán tang nên chưa áp điều kiện này, chờ chủ dự án xem. (2) Lớp văn vận hạn (`van_han.json`) chưa có câu cho các luật mới, nên chương vận hạn bỏ qua chúng; biểu đồ vẫn dùng. (3) Ba luật "phát" cũ đọc rộng hơn trang sách (xem cuối `docs/INDICES-TH115-117.md`).


## 3.1.0 (2026-10-24): luật đại / tiểu hạn Thực Hành tr.115-117 (các mục "chờ duyệt" dưới đây đã thêm ở 3.2.0)

Bảng đối chiếu đủ từng mục (trang, nguyên văn, trạng thái) ở `docs/INDICES-TH115-117.md`. Mọi mục đã xem ảnh trang. Tóm tắt:

| Trạng thái | Mục |
|---|---|
| Đã thêm (6 luật) | IX.6 Giáp / Canh gặp Thiên Thương, Thiên Sứ ở Dần / Thân (bất lợi); IX.9 tuổi Thân gặp Thiên Thương (bất lợi); IX.10 tuổi Thìn Tuất Sửu Mùi gặp Kình Đà cùng Tử, Phủ, Xương, Khúc là "hoạnh phát" (thuận), còn khi không có các sao ấy là "không hề gì" (chỉ nói, không cộng trừ); 6n Sát Phá Tham hội Tang Hổ Khốc Khách, Đà, Thiên Thương (bất lợi) |
| Đã có từ trước | Đoán cách 1; thất lợi 6c, 6e |
| Chờ chủ dự án duyệt nội dung (chết, tù, tai nạn, thương tật, bệnh, bỏng, chết đuối, tang) | IX.7, IX.8, IX.11; đoán cách 5; thất lợi 6a, 6b, 6d, 6f-6m, 6o; có tang 7a-7i |
| Không tính được | IX.5 (Cự Môn không bao giờ ở tam phương của Sát Phá Tham); đoán cách 2-4 (sự kiện cưới, sinh con, tình duyên: không có chiều thuận / bất lợi) |

Fact mới của `vh.*` (`engine/tvbt/van_han.py`): can, chi năm sinh, sao trong tam phương tứ chính của cung vận, Thiên Thương / Thiên Sứ và Kình / Đà trong cung vận. Câu đọc vận trong `corpus1000` được tính lại bằng `tools/interpret/refresh_van_readings.py` (chỉ thay `decades[].readings`; công cụ dừng nếu câu của luật cũ đổi).

Số cung vận khớp trên 1.000 lá (mỗi lá 12 cung vận): IX.6 Giáp 14, IX.6 Canh 19, IX.9 76, IX.10 "hoạnh phát" 180, IX.10 "không hề gì" 444, 6n 17.

### Độ khớp (`node tools/interpret/eval_indices.ts`, tiểu hạn theo KL)

| Chỉ số | 3.0.0 | **3.1.0** |
|---|---|---|
| Chặng ở tam hợp Thái Tuế bị vẽ dưới "Trung bình" | 451 / 2.244 (20 %), 100 % có giải thích | 447 / 2.244 (19,9 %), 100 % có giải thích |
| Chặng có mức khác chiều lời sách | 2.240 / 10.000, 100 % có giải thích | 2.241 / 10.000, 100 % có giải thích |
| Chặng / năm thiếu căn cứ | 0 | 0 |
| Năm khác phía "Trung bình" với chặng của nó | 693 / 20.596, 100 % có giải thích | 691 / 20.596, 100 % có giải thích |
| Năm mức, chặng / năm / tháng | 12 / 21 / 34 / 21 / 12 % | 12 / 21 / 34 / 21 / 12 % |
| Tháng trùng mức của năm | 7,6 / 12 | 7,6 / 12 (63,5 %) |
| Tương quan điểm chặng với chất lượng bẩm sinh | 0,166 | 0,165 |
| Radar so với sổ cái (1.124 cặp) | cùng chiều 46,8 %, ngược 13,2 % | không đổi |

So với 3.0.0: 193 / 10.000 chặng và 451 / 20.596 năm đổi mức, tất cả chỉ một bậc. Không lá nào đổi từ hai bậc trở lên.

Lời đọc của IX.9 và 6n là "theo sách rất bất lợi", không dùng chữ "tai họa" / "tai ương" của sách (chủ dự án quyết, 2026-10-24). Việc còn chờ chủ dự án: (1) duyệt nội dung các mục "chờ duyệt"; (2) có cho IX.10 "không hề gì" triệt tiêu Kình / Đà hãm của lớp đắc hãm KL tr.233 ở tuổi Tứ Mộ không. Lớp văn vận hạn (`src/interpret/content/prose/van_han.json`) chưa có câu cho sáu luật mới, nên chương vận hạn bỏ qua chúng; biểu đồ vẫn dùng.


## 3.0.0 (2026-10-24): kế hoạch chủ dự án duyệt

Bốn quyết định của chủ dự án (2026-10-24), mỗi quyết định ứng với một thay đổi trong mã:

1. **Hướng tiểu hạn theo Khảo Luận tr.39-40 (âm dương)** là mặc định ở engine (`tuvi.DEFAULT_VARIANTS`, `api.BirthReq`). Tiểu hạn, nguyệt hạn (KL tr.40-41, TH tr.115: đếm từ cung tiểu hạn), lưu đại hạn và lưu Kình Đà (KL tr.42) dùng chung một trường phái. Facts ghi lại trường phái đã dùng (`tieu_han_rule`), biểu đồ ghi nó trong phụ đề. Thực Hành tr.27 (nam thuận, nữ nghịch) vẫn chọn được. Với âm nam và âm nữ, hai sách đi ngược nhau. Lá 09/01/2002 (âm nam): tiểu hạn 2026 ở Tài Bạch theo KL, ở Phu Thê theo TH.
2. **Bỏ lớp "độ vững" trừ hay cộng điểm.** Thực Hành tr.118 chỉ được nói thành lời, không cộng trừ: Mệnh sáng gặp hạn rực rỡ là "thêm gấm thêm hoa"; Mệnh hắc ám gặp hạn rực rỡ là "rồng mây gặp hội"; hạn tốt vừa là "cây khô gặp mùa xuân". Với hạn xấu trên Mệnh tối, lời văn nói rõ sách không nói thêm. Ngưỡng sáng / tối (±0,75 lần cỡ thường gặp) là thông lệ, có ghi.
3. **Tật Ách trên radar được giữ**, kèm câu: "đánh giá cát hung theo Tử Vi, không phải dự đoán sức khỏe hay chẩn đoán y khoa".
4. **Không có câu sách thì để mức "Trung bình" kèm nhãn "chưa đủ căn cứ"** (`insufficient`). Lời văn nói rõ đó không phải trung bình thật. Tháng không có gì để xét thì "Chưa xác định" (mức `null`), không tạo điểm giả.

Lớp mới và thay đổi, mỗi mục đều có sao, vị trí cung, quy tắc và trang trong phần "Căn cứ":

| Giai đoạn | Lớp | Trọng số | Nguồn |
|---|---|---|---|
| Đại vận | Cung vận: câu sách (KL tr.230-236, TH tr.115-117, TT diễn ý ×0,5); Nam / Bắc đẩu chính tinh của cung vận theo âm dương (TH tr.115 mục IX.1-2); đắc / hãm các chính tinh, trung tinh (Xương Khúc Tả Hữu, KL tr.36), hung tinh (Kình Đà Không Kiếp Hỏa Linh) của cung vận, xung chiếu, tam hợp, và nhị hợp khi nhị hợp sinh cho cung vận (KL tr.233 mục 3-4; độ sáng chỉ lấy loại VERIFIED, mỗi sao ½ câu; hãm có Tuần Triệt giải thì tốt; hung tinh gặp quan thầy ×1,5; khi tam hợp vận khắc xung chiếu thì không tính sao hãm của cung xung chiếu, KL tr.232) | 0,80 | sách |
| | Tứ Hóa theo can đại vận | 0,20, có trần | thông lệ |
| Năm | Đại vận đang đi | 0,30 | |
| | Cung tiểu hạn: câu sách, Nam / Bắc đẩu, đắc hãm (KL tr.40: đọc sao cung tiểu vận cùng phối chiếu) | 0,30 | sách |
| | Cung lưu đại hạn (TH tr.117-118; kiểm bằng ví dụ của sách: Tử 32 → Điền 33, Quan 34, Điền 35, Phúc 36 … Bào 39) | 0,15 | sách |
| | Bắc đẩu của cung đại vận ở năm năm đầu, Nam đẩu ở năm năm sau (TH tr.115 mục IX.3-4) | 0,10 | sách |
| | Lưu Khốc Hư ở tiểu hạn (TH tr.114) | 0,07 | sách |
| | Sao lưu khác 0,03, lưu Tứ Hóa 0,05 (bỏ khi can năm trùng can đại vận: cùng bốn sao đã tính ở chặng) | có trần | thông lệ |
| Tháng | Mức của năm + 0,25 × đắc hãm các sao của cung nguyệt hạn và tam phương | | vị trí TH tr.115, KL tr.40-41; tiêu chí KL tr.233 |

Nam / Bắc đẩu của từng sao lấy từ đầu mục mỗi sao trong Thực Hành (đã đối chiếu ảnh trang, 2026-10-24). Nam đẩu: Cơ, Nhật, Đồng, Phủ, Tướng, Lương, Sát, Khôi, Việt, Văn Khúc, Hỏa, Linh. Bắc đẩu: Vũ, Liêm, Nguyệt, Tham, Cự, Phá, Tả, Hữu, Văn Xương, Lộc Tồn, Kình, Đà. Tử Vi là cả hai. Mã, Không, Kiếp không ghi.

Bỏ khỏi điểm giai đoạn: nền bẩm sinh của cung (radar), độ vững, cung lưu Thái Tuế. Nhận định bẩm sinh không bao giờ vào điểm giai đoạn nữa.

**Không trừ trung bình.** Mỗi lớp chia cho cỡ thường gặp (rms) của chính nó, nên lớp không có gì góp 0. Năm mức vẫn là ngưỡng 12 / 33 / 67 / 88 % của các giai đoạn có căn cứ sách. Đã thử neo thang ở 0 (dấu của tổng là chiều của lời sách): 99,6 % chặng thành "Thuận" trở lên. Lý do là chất liệu sách đọc được nghiêng về thuận (bảng độ sáng có 3.879 chỗ đắc / miếu / vượng so với 1.601 chỗ hãm trên 300 lá; phần lớn câu sách về vận là câu tốt). Vì vậy "Thuận" nghĩa là thuận hơn các giai đoạn thường gặp, và khi mức khác chiều lời sách thì lời văn nói rõ. Đường giữa biểu đồ được vẽ ở tâm dải "Trung bình".

### Độ khớp trên 1.000 lá (`node tools/interpret/eval_indices.ts`, tiểu hạn theo KL)

| Chỉ số | 2.1.0 | **3.0.0** |
|---|---|---|
| Chặng ở tam hợp Thái Tuế (KL tr.233) bị vẽ dưới "Trung bình" | 336 / 2.244 (15 %), không giải thích | 451 / 2.244 (20 %), **100 % có câu giải thích** trong lời văn |
| Chặng có mức khác chiều lời sách của chính nó | 1.258 / 10.000, không giải thích | 2.240 / 10.000, **100 % có câu giải thích** ("lời sách vẫn nghiêng về thuận, nhưng ít điều thuận hơn những chặng thường gặp") |
| Chặng / năm không có lời sách bị chấm "thử thách" | 376 / 672 chặng | 0: không còn chặng nào thiếu căn cứ (lớp đắc hãm luôn có sao để xét); nếu có thì để "Trung bình · chưa đủ căn cứ" |
| Năm không có Khốc / Hư mà vẫn được cộng điểm | 12.769 / 20.596 | 0 (không trừ trung bình) |
| Năm khác phía "Trung bình" với chặng của nó | 55 / 1.686 năm cùng cung | 693 / 20.596 (3,4 %), **100 % có câu "khác chiều với chặng đang đi"** cùng lớp gây ra |
| Năm mức, chặng / năm / tháng | 12 / 21 / 34 / 21 / 12 % | 12 / 21 / 34 / 21 / 12 % (trên các giai đoạn có căn cứ) |
| Tháng trùng mức của năm | 7,6 / 12 | 7,6 / 12; tháng nhích theo đắc hãm cung tháng, không tạo biến động |
| Tương quan điểm chặng với chất lượng bẩm sinh | 0,231 | **0,166** |
| Radar so với kết luận sổ cái (Quan, Tài, Điền, Phu Thê; 300 lá) | — | cùng chiều 46,8 %, ngược chiều 13,2 % (1.124 cặp): chưa sửa ở đợt này |

Chưa làm ở đợt này: (a) các luật "thất lợi", "tang", "đoán cách" ở TH tr.116-117 (đã xử lý ở 3.1.0, xem trên). Nhiều luật nói chuyện tù tội, tai nạn, chết đuối, cần duyệt nội dung trước khi đưa vào. (b) Luật "cát tinh chiếm 2/3" của TH tr.117: sách không kèm danh sách cát tinh, nên chưa có căn cứ để đếm. (c) Nhật vận (KL tr.41, TH tr.115). (d) 13 % ngược chiều giữa radar và sổ cái. (e) `corpus1000` vẫn được lập bằng bảng độ sáng Thực Hành và tiểu hạn Thực Hành; bộ chuẩn đi lại tiểu hạn theo KL, còn độ sáng giữ như bộ mẫu.

Lá 09/01/2002 04:30 nam (theo KL), mười chặng 2.1.0 → 3.0.0: 3–12 Rất thử thách → Nhiều thử thách; 13–22 Rất thử thách → Nhiều thử thách (lời văn: KL coi tam hợp Thái Tuế là may mắn nhất, nhưng các lời sách khác kém hơn những chặng thường gặp); 23–32 Nhiều thử thách → Thuận; 43–52 Trung bình → Nhiều thử thách; 73–82 Trung bình → Nhiều thử thách; 83–92 Rất thử thách; 93–102 Thuận. Năm 2026: tiểu hạn Tài Bạch, lưu đại hạn Quan Lộc, "Trung bình".

---

# indices-2.1.0 (2026-10-21)

Track A của kế hoạch 2026-10-21: biểu đồ đại vận / năm / tháng đo **mức kích hoạt của thời vận trên cả lá số**, không dùng lại luận giải bẩm sinh của cung vận. Số liệu sinh bởi `node tools/interpret/index_norms.ts` trên `corpus1000.json.gz` (1.000 lá, bộ mẫu phân tầng, không phải dân số thật). Tất cả là kiểm tra tự động; chưa có chuyên gia chấm.

## Mô hình

**Sách trước, thông lệ sau** (quy tắc của chủ, 2026-10-21): các lớp có sách quyết định chiều; các lớp thông lệ cộng lại chỉ được thêm tối đa 0,5 × |phần có sách| (+ 0,15 khi cùng chiều hoặc sách không nói), nên chỉ nhấn thêm hoặc làm dịu, không lật được lời sách (`conventionCap`, phần `thong_le_cap` trong "Căn cứ").

| Giai đoạn | Lớp (mỗi lớp quy về điểm chuẩn z so với bộ mẫu) | Trọng số | Nguồn |
|---|---|---|---|
| Đại vận | Câu sách về cung vận | 0,65 | KL tr.230-236, TH tr.115-117; Toàn Thư tr.97-105 diễn ý × 0,5 |
| | Nền bẩm sinh của cung vận | 0,10 | nhận định đã đối chiếu sách (radar); chỉ là nền, không bao giờ được liệt kê là lý do |
| | Tứ Hóa theo can đại vận rơi vào cung vận, tam phương, Mệnh | 0,25, có trần | thông lệ (phi hóa), ba sách không có câu luận |
| | Độ vững: Mệnh + tam phương (nhận định đã đối chiếu, gồm cách cục sách) | hệ số ± 0,15 × z (giới hạn 1,5) | cách cục thử nghiệm (nháp) không còn dùng |
| Năm | Đại vận đang đi | 0,40 | |
| | Câu sách về cung tiểu hạn (năm xem: `year.tieu_han_tt/kl`) | 0,27 | như trên |
| | Nền bẩm sinh cung tiểu hạn | 0,08 | |
| | Lưu Khốc, Hư ở cung tiểu hạn (+ hung tinh) | 0,10 | TH tr.114 (đã xem ảnh trang), vị trí KL tr.41-42 |
| | Thông lệ: cung lưu Thái Tuế 0,04, sao lưu khác theo loại sao 0,04, lưu Tứ Hóa 0,07 | 0,15, có trần | KL tr.41 "không nặng ký" |
| Tháng | Mức của năm + 0,25 × z (nền bẩm sinh cung nguyệt hạn) | | vị trí TH tr.115 |

Năm mức (Rất thử thách · Nhiều thử thách · Trung bình · Thuận · Rất thuận) = ngưỡng 12 / 33 / 67 / 88 % của chính loại giai đoạn trên bộ mẫu. Dải Bát Tự dưới biểu đồ đại vận: vận nào mang thần điều hậu của bảng Thiệu Vĩ Hoa (tr.389-396; dụng / hỷ / không mang — bảng không định nghĩa kỵ), không cộng vào mức Tử Vi.

Sửa kèm: `rarity()` đọc theo cung của nhận định (`kg.baseRates.palaces`); trước đây mọi luật ngoài Mệnh cùng "trọng số 0,63".

## Kiểm tra

| Chỉ số | indices-1.0.0 | 2.0.0 | **2.1.0** |
|---|---|---|---|
| Tương quan điểm đại vận với chất lượng bẩm sinh của cung đại vận (10.000 chặng) | 0,424 | 0,243 | **0,231** |
| Tương quan với lớp câu sách / Tứ Hóa (thông lệ) / nền | — | 0,686 / 0,687 / 0,243 | **0,933 / 0,261 / 0,231** |
| Tương quan điểm năm với đại vận của nó | — | 0,796 | 0,804 |
| Năm mức, đại vận (corpus) | — | 10 / 20 / 40 / 20 / 10 % | **12 / 21 / 34 / 21 / 12 %** |
| Năm mức, chỉ đại vận hiện hành | — | 8,6 / 20,2 / 40,3 / 22,0 / 8,9 % | 11,3 / 20,5 / 34,5 / 22,9 / 10,8 % |
| Năm mức, năm / tháng | — | 10 / 20 / 40 / 20 / 10 % | 12 / 21 / 34 / 21 / 12 % |
| Lá có ≥ 3 chặng "Rất thử thách" / ≥ 3 "Rất thuận" (trên 1.000) | — | 85 / 86 | 146 / 116 |

2.0.0 → 2.1.0: 40,7 % chặng và 35,2 % năm trên corpus đổi mức (2,4 % chặng, 0,9 % năm đổi từ hai mức trở lên). Lá 09/01/2002 04:30 nam: 3/10 chặng đổi (23–32 Phu Thê "Thuận" → "Trung bình": sách −0,67 thắng Tứ Hóa thông lệ +0,68 bị giới hạn còn +0,23), 11/21 năm đổi (2026 "Rất thuận" → "Trung bình"); số chặng "Rất thử thách" 4 → 3. Lá 1911-01-01 12:30 nam: 4/10 chặng, 2/21 năm đổi.

Giới hạn còn lại: khi sách quyết định, các chặng cùng một tam hợp nhận cùng một câu Khảo Luận tr.230-233 (hành tam hợp của vận so với tuổi), nên trên một lá số các mức dễ dồn theo tam hợp hơn trước (146 lá có ≥ 3 chặng "Rất thử thách"). Đó là đúng lời sách, không phải lỗi thang.

Phản thực (`src/interpret/test/indices.test.ts`, lá tham chiếu Cự Môn Tuất): kiểm thêm rằng phần thông lệ luôn nằm trong trần và không lật chiều của sách trên cả benchmark20; đổi Tứ Hóa của chặng Phu Thê sang Tứ Hóa can Giáp → điểm chặng đổi > 0,3, các chặng khác giữ nguyên; bỏ một luật bẩm sinh ở cung ngoài tam phương của chặng và của Mệnh → điểm chặng không đổi; bỏ một luật trong tam phương của chặng → đổi < 0,15 (chỉ qua lớp nền). Chín sao lưu khớp Python (`year.luu_stars`) trên cả 1.000 lá; tiểu hạn và lưu Thái Tuế khớp Python trên benchmark20.

Văn: mỗi chặng / năm 2–4 câu, không mã luật, không "trọng số", không số thập phân; mã luật, trang, trọng số, điểm chuẩn và công thức chỉ ở phần "Căn cứ".
