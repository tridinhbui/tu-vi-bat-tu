# Plan khắc phục bản đánh giá chuyên sâu 33 trang (2026-11-07)

Nguồn: bản "Đánh giá chuyên sâu bản luận giải Thiên Bàn (33 trang)" chủ dự án gửi ngày 2026-11-07. Bản này chấm thấp nhất ba phần: tổng hợp cát hung (2/10), đại vận và lưu niên (3/10), kết luận cuối (3/10).

Lá kiểm là lá của chủ dự án: **09/01/2002 04:30, nam, bảng Khảo Luận**. Tứ trụ Tân Tỵ · Tân Sửu · Đinh Sửu · Nhâm Dần. Mệnh ở Tuất có Cự Môn hóa Lộc và Kình Dương. Thân cư Quan Lộc ở Dần.

Mọi câu trích dưới đây là đầu ra hiện tại của main 792dcbed, chạy lại qua `proseAllChapters` (đúng đường `/api/interpret`) với facts mới lấy từ `/api/facts`. Không lấy câu nào từ trí nhớ.

Plan này không thay các plan cũ. `TUVI-ENHANCE-PLAN.md` (EP) và `TUVI-REVIEW-PLAN.md` (RP) vẫn giữ nguyên. Ở đây chỉ có những việc bản 33 trang đòi mà hai plan kia chưa làm, hoặc đã làm nhưng chưa tới gốc.

---

## 1. Đối chiếu từng điểm với code hiện tại

Bản đánh giá đúng ở phần lớn các điểm. Có hai điểm chỉ đúng một nửa: phần mềm đã làm nhưng người đọc không thấy.

| # | Điểm nhận xét | Trên main hiện nay | Nguyên nhân gốc |
|---|---|---|---|
| 1 | Nhật chủ nhược suy từ "25% tám chữ", chưa thấy nguyệt lệnh, tàng can, thông căn | **Đúng một nửa.** Phép chấm độ Thiệu Vĩ Hoa (`bazi_deep/tvh_score.py`) đã tính lệnh tháng ±1/5, tàng can, can có gốc 36 độ, hư phù 9 độ. Ngưỡng 40% có nguồn là TVH tr.355. Nhưng đoạn chính chỉ nói "giữ khoảng một phần tư sức của tám chữ", nên đọc lên giống như đếm chữ. Bảng độ thì nằm trong phần gập [sâu]. Phần mềm không nói "nhược có căn" (có Bính ở Tỵ Đế Vượng, Giáp và Bính ở Dần) và không loại trừ tòng cách thành lời. | Đoạn chính thiếu bảng yếu tố. Thang mức chỉ có nhược/vượng/hơi. Độ chắc của kết luận không được truyền xuống các phần sau. |
| 2 | Dụng thần là đáp án cho mọi vận; phù ức và điều hậu khác nhau thì ưu tiên bên nào | **Đúng, và có một lỗi cụ thể.** Câu "lấy Giáp (Chính Ấn) làm chính, **khác với** dụng thần Tỉ Kiếp… chỉ nên đọc là có điều kiện" là sai. Giáp là Ấn, mà Ấn chính là hỷ thần trong phép phù ức. Hỏa là dụng thần ở cả hai phép. Như vậy hai phép **cùng chiều** về Mộc và Hỏa. Chỗ vênh thật chỉ có ở can Canh (điều hậu phụ, nhưng là Tài, tức kỵ). | `bazi_deep.ts` so hai phép theo **nhóm dụng thần**, không so theo **bản đồ hỷ/kỵ từng hành**. Vận được chấm theo nhóm thập thần, chưa tính chế hóa: vận Mậu Tuất chấm "Thực Thương xì hơi" là nặng, dù phần [sâu] có ghi "can Mậu khắc can giờ Nhâm, chữ đang khắc dụng thần". |
| 3 | Mạch Quan → Ấn → Thân bị coi là đứt | **Đúng.** Có câu "không có Ấn, nên mạch Tài sinh Quan, Quan sinh Ấn chưa nối được tới nhật chủ". Nhưng cùng chương lại có câu "Tài ở trụ năm, tháng, còn Ấn ở trụ ngày, giờ, đường chức vụ dễ đi lên đều". Nhâm ngồi trên Dần, mà Dần tàng Giáp. | Mạch được xét có/không theo can đứng sát. Không có cấp mạnh/vừa/yếu (thấu hay tàng, cùng trụ hay cách trụ). Hai luật trái nhau được phát cùng lúc mà không có câu nối. |
| 4 | Tử Vi không có cơ chế giải xung đột; "chưa phân xử" khắp nơi | **Đúng.** Quan Lộc: "Kết lại, xét chung các cung, đường công danh còn hai mặt chưa phân xử được." Tổng luận: "Đường công danh còn hai mặt ngang nhau… hôn nhân hai phía ngang sức". | `reason/ledger.ts weighSides` chỉ cân **câu nặng nhất mỗi bên**, cộng thêm số chỗ. Nó không đưa vào cân những yếu tố cấu trúc đã có trong `evidence.ts`: Tứ Hóa trong tam phương, cung vô chính diệu mượn sao, quan hệ chế hóa của `kg/che_hoa.json`. Khi lệch dưới mức 0,2 thì dừng ở `chua_phan_xu`, không nói điều gì sẽ làm cán cân nghiêng. |
| 5 | Câu sách đơn lẻ thành kết luận nặng | **Đúng, đủ cả sáu ví dụ.** Văn Khúc ở Tài Bạch thích cờ bạc (HS tr.233). Không Kiếp hãm ở Điền Trạch bị chiếm đoạt, phá sản (HS tr.162). Thiên Tướng ở Phụ Mẫu cha mẹ thọ (HS tr.132). Thiên Hình ở Tử Tức hiếm con (TH tr.104, TT tr.92). Tật Ách dễ bạo bệnh (Thiên Lương). Thân cư Quan Lộc ngoài 40 tuổi (TH cách). Câu cuối nằm ngay ở đoạn chính Quan Lộc: "Dù có cát tinh hội, cũng phải ngoài 40 tuổi mới nhẹ bước thanh vân." | Luật không có **hạng mức nặng**. Câu nặng và câu nhẹ đi chung một đường vào văn bản. Câu sức khỏe, thọ yểu, con cái chỉ được che bằng thông báo `sensitive` của chương. |
| 6 | Đại vận: 93–102 "thuận nhất"; hai hệ không đối chiếu; "1.000 lá mẫu" không nói rõ cách làm | **Đúng.** Tổng luận có câu "Chặng thuận nhất của đời là đại hạn 93–102 tuổi". Quan Lộc có câu "công danh nổi lên ở các chặng 83–92 tuổi (…mức nhiều thử thách)". Chặng hiện tại Tử Vi chấm Thuận (23–32, Phu Thê), còn Bát Tự chấm Mậu Tuất "nặng hơn nhẹ", và không có câu nào nối hai bên. | `tong_luan.ts` xếp hạng trên mọi chặng, không có khung tuổi. `course.ts` gọi "nổi lên" cho chặng hạn vào cung, bất kể mức. Không có bảng đối chiếu hai hệ. Cách lấy mẫu và độ ổn định của `index_norms` không hiện ra cho người đọc. |
| 7 | Cách cục kết luận tuyệt đối | **Đúng, và có lỗi sự thật.** "Đứng ở cung Mệnh, cách xấu này ảnh hưởng mạnh lên cả đời người… ở cung Mệnh không có chỗ đỡ." Thực tế Đào Hoa và Thiên Không **ở Tài Bạch (Ngọ)**, chiếu về Mệnh qua tam hợp. Cùng cung đó có Thái Dương miếu hóa Quyền và Văn Khúc hóa Khoa. | `cach_cuc.ts` không phân biệt đồng cung với chiếu. Phần mềm chỉ tìm chỗ đỡ ở cung Mệnh, nên không thấy cứu giải ngay trong cung đang mang cách. Câu xếp hạng "có sức nặng nhất" không nêu lý do. Mẫu câu có chữ "cả đời". |
| 8 | Câu máy móc, gán sai nguyên nhân, lỗi tiêu đề | **Đúng.** (a) Tổng luận: "phần tích lũy, nhà cửa: chỗ phải gắng sức, do Văn Khúc ở cung Tài Bạch". (b) Quan Lộc: đoạn chính chỉ viết "với Thân cư Quan Lộc, công danh đến muộn", trong khi luật TH tr.75 là "Thân cư Quan Lộc **gặp** Tuần Triệt, Kiếp Hỏa hoặc Hóa Kỵ hội". Câu Đọc sâu "yếu tố làm nên nó… Văn Xương hóa Kỵ" là **đúng** (đính chính 2026-11-08); lỗi nằm ở đoạn chính bỏ mất điều kiện. (c) Tổng luận "chỗ dựa đứng đầu là khả năng kiếm tiền" rồi ngay câu sau "Biểu đồ… cho cung Tài Bạch thấp hơn mức thường gặp". (d) Tiêu đề chương Công danh: "Cung Quan Lộc và cung đối Thiên Di", ở `engine/web/js/report.js:665`. | `groundOf` / `ground()` lấy sao đầu danh sách, không lấy **sao làm nền cho phán quyết**. Lớp sâu tự ghép nguyên nhân mà không có quan hệ sách. Dòng dẫn chương Công danh viết tay sai. |

---

## 2. Nguyên tắc cho đợt này

Giữ nguyên các quyết định cũ:
- không dùng LLM;
- chỉ nói câu sách đã đối trang;
- câu tổng hợp phải gắn nhãn `he_thong` và chỉ ghép từ câu sách đã nói (review-19);
- không đưa phổ thông vào;
- không chẩn đoán sức khỏe.

Thêm bốn luật mới, mọi giai đoạn đều theo:

1. **Kết luận bốn phần.** Mọi kết luận tổng hợp, ở cả Tử Vi lẫn Bát Tự, đều mang bốn thứ, vừa trong dữ liệu vừa trong câu chữ:
   - **yếu tố chi phối**: sao, chữ hoặc quan hệ nào quyết định;
   - **yếu tố làm giảm hoặc cứu giải**;
   - **điều chưa đủ căn cứ**;
   - **độ chắc**: rõ, vừa hoặc tạm.

   Thiếu yếu tố chi phối thì không được viết câu kết.
2. **"Chưa phân xử" không còn là một câu kết.** Nó chỉ được dùng khi hai bên cân bằng thật. Lúc đó câu phải nói điều gì sẽ làm cán cân nghiêng, ví dụ chặng đại hạn nào hoặc yếu tố nào.
3. **Câu nặng không đi đường thường.** Phá sản, bệnh, thọ yểu, con cái, đổ vỡ hôn nhân, tật xấu, mốc tuổi cố định và "cả đời" đều có đường riêng (G1).
4. **Nguyên nhân phải là nguyên nhân thật.** "do X", "nhờ X", "yếu tố làm nên nó là X" chỉ được viết khi X nằm trong `stars` của chính câu sách làm nền cho phán quyết đó. Có test kiểm.
5. **`severity` và `confidence` là hai trục riêng** (quyết định 2026-11-07).
   - `confidence` nói kết luận vững tới đâu theo hệ quy tắc.
   - `severity` nói câu nặng tới đâu khi hiện cho người đọc.

   Một câu có điều kiện kích hoạt đúng hoàn toàn, tức `confidence` cao, vẫn có thể có `severity` cao, nên vẫn không vào kết luận chính. Hai trục được tính và lưu tách nhau. Không trục nào suy ra từ trục kia.
6. **Không dùng trọng số để ép hai phương pháp về một kết luận.** Hai phương pháp, hoặc hai hệ, vẫn bất đồng thì kết quả giữ nguyên chỗ bất đồng đó. Câu tổng hợp được phép có, nhưng phải nói rõ phần nào chưa giải quyết.

**Tiêu chí nghiệm thu chung** (quyết định 2026-11-07). Mỗi kết luận, ở cả dữ liệu lẫn câu chữ, phải trả lời được bốn câu:
- (a) Vì sao kết luận này xuất hiện: dữ kiện nào, quy tắc nào đã kích hoạt?
- (b) Điều kiện nào khiến nó đúng theo hệ quy tắc?
- (c) Yếu tố nào làm giảm hoặc đảo chiều nó?
- (d) Hệ thống còn chưa biết điều gì?

Thiếu một câu trả lời thì không được viết kết luận. Bộ test bất biến ở G-INV kiểm tiêu chí này trên mọi lá.

**Chuẩn cho một đoạn luận** (bổ sung 2026-11-07, kiểm ở G10). Một đoạn chỉ đạt khi trả lời được ba câu:
1. Tổ hợp này có ý nghĩa riêng ở đâu? Đoạn phải phân tích quan hệ giữa các thành phần, không giải thích từng sao một.
2. Vì sao chọn kết luận tổng hợp này? Đoạn phải nêu cấu trúc chi phối, điều kiện làm mạnh, điều kiện làm yếu và chỗ bất đồng chưa giải.
3. Người đọc hiểu thêm được gì về cấu trúc của lá số này? Một lời tốt hay xấu thêm vào không tính là hiểu thêm.

**Luật 7. Hai lõi tách nhau.** Lõi suy luận (G9) dựng ra bản phân tích có cấu trúc. Lõi diễn đạt (G10) chỉ được nói những gì bản phân tích có. Lõi diễn đạt không được thêm sự kiện, tính cách hay dự báo. Mọi mệnh đề trong câu phải có `evidence_id` hợp lệ. Mệnh đề không có thì bị chặn, hoặc chuyển thành "minh họa" có nhãn theo `illustration-policy`.

Không dùng LLM ở cả hai lõi. Một bản luận yếu viết mượt hơn chỉ làm cái sai khó thấy hơn.

---

## 3. Các giai đoạn

Thứ tự đi từ lỗi sai sự thật, qua phần gốc Bát Tự, phần gốc Tử Vi, rồi tới vận hạn và cuối cùng là câu chữ. G0 và G1 nhỏ, làm ngay. G2–G5 là phần "triệt để".

### G0. Lỗi sai sự thật (nhỏ, làm trước)

| Việc | Tệp | Xong khi |
|---|---|---|
| Dòng dẫn Công danh đổi thành "Cung Quan Lộc, cung xung chiếu Phu Thê và cung Thiên Di (bối cảnh bên ngoài)". Rà hết các `lead` khác trong mảng `chapters` | `engine/web/js/report.js:665`, rồi `tools/build_site.py` để cập nhật mã phiên bản tài sản | Không còn lead nào đặt sai tên cung đối |
| Cách cục nói đúng chỗ đứng: "Đào Hoa, Thiên Không ở Tài Bạch, chiếu về Mệnh qua tam hợp". Tìm chỗ đỡ trong **cả cung mang cách lẫn cung Mệnh** | `src/interpret/prose/cach_cuc.ts` | Trên lá kiểm: câu nhắc Thái Dương miếu hóa Quyền và Văn Khúc hóa Khoa đồng cung. Không còn "ở cung Mệnh không có chỗ đỡ" |
| Bỏ chữ "cả đời", "suốt đời" khỏi mọi mẫu câu tổng hợp (câu sách thì giữ nguyên văn) | `content/prose/*.json` | `quick_check` có luật cấm |
| Test nguyên nhân thật (luật 4 ở mục 2): mọi "do / nhờ / nền ở / yếu tố làm nên" trong tong_luan, luan, luan_deep | `test/attribution.test.ts` (mới); sửa `groundOf` trong `tong_luan.ts`, `ground()` trong `luan.ts:951`, lớp nhịp trong `luan_deep.ts` | Ba câu sai ở mục 1, dòng 8a–8c, biến mất. Test chạy trên benchmark20 |
| Tổng luận không tự mâu thuẫn với biểu đồ: miền "đứng đầu" mà biểu đồ cung thấp hơn mức thường thì gọi là "có điều kiện", không gọi "chỗ dựa đứng đầu" | `prose/tong_luan.ts` (`radarLine`) | Lá kiểm không còn cặp câu (c) |

### G1. Kiểm toán câu nặng (bước 3 trong "ba việc" của bản đánh giá)

1. **Hạng mức nặng cho từng luật.** Lưu ở tệp mới `engine/data/kg/claim_severity.json`, dạng `{ruleId: class}`. Có các hạng sau:
   - `vat_chat_nang`: phá sản, bị chiếm đoạt, tán gia;
   - `suc_khoe`: bệnh, bạo bệnh, tai nạn;
   - `tho_yeu`: thọ, yểu, chết sớm;
   - `sinh_san`: hiếm con, muộn con, sát con;
   - `hon_nhan_vo`: ly hôn, góa, tái giá;
   - `tat_xau`: cờ bạc, phóng đãng, trộm cắp;
   - `moc_tuoi`: "ngoài 40 tuổi"…;
   - `tuyet_doi`: "cả đời", "không bao giờ".

   Lọc bằng từ khóa trên `description` và `quotes_*`, rồi duyệt tay. Tạo bản ghi duyệt `rule_review_2026-11.json`.
2. **Đối lại điều kiện với trang sách** cho mọi luật thuộc các hạng trên. Kiểm điều kiện bắt buộc và ngoại lệ, ví dụ HS tr.162 ghi "hãm địa", TL ghi điều kiện Phụ Mẫu. Mở rộng `tools/interpret/audit_widening.py` thành `audit_conditions.py`. Luật mã hóa rộng hơn trang sách thì sửa thẳng trong pack, vì sinh lại pack sẽ mất các sửa trước đó (xem `synthesis-ledger-s1`).
3. **Đường nói riêng** trong `prose/checked.ts` và `select.ts`. Câu nặng **không bao giờ** vào kết luận chính, câu kết chương hay Tổng luận (quyết định Q2). Cụ thể theo từng hạng:
   - `suc_khoe`, `tho_yeu`, `sinh_san`: chỉ vào phần "Đọc sâu", và chỉ khi đủ ba điều kiện:
     - trích đúng câu sách, có trang;
     - điều kiện kích hoạt đã đối với trang sách (bước 2) và đều có mặt trên lá;
     - ghi rõ "quan niệm truyền thống, chưa được xác minh thực nghiệm".

     Câu nào khẳng định một việc cụ thể (sẽ mắc bệnh nặng, đoản thọ, vô sinh, người thân sẽ mất) thì không trích thành dự báo về người xem. Thay vào đó, viết **mô tả trung tính về ý nghĩa của tổ hợp sao trong sách**, ví dụ "sách xếp tổ hợp này vào nhóm chủ về tai ách". Lời sách gốc chỉ giữ trong panel nguồn.
   - `vat_chat_nang`, `hon_nhan_vo`, `tat_xau`: chỉ vào đoạn chính khi có **hai căn cứ độc lập** cùng chiều. Không đủ thì đưa vào Đọc sâu theo mẫu trên.
   - `moc_tuoi`: nói thành "sách cho là đến muộn (sách nêu mốc ngoài 40)". Sau đó đặt cạnh mức các đại hạn sau mốc đó (nối với G4).
   - Luật có Hóa Lộc, Quyền hoặc Khoa trên chính sao của câu (ví dụ Văn Khúc hóa Khoa ở Tài Bạch) mà câu sách không nói tới Hóa: thêm nhãn "câu sách chưa xét Hóa Khoa đi kèm". Không đảo nghĩa câu, vì đảo là tự đặt luật.
4. **Đo:** công cụ mới `tools/interpret/eval_severity.ts --n 1000`. Đếm câu thuộc từng hạng ở đoạn chính và ở Đọc sâu.

**Xong khi:** đoạn chính trên corpus1000 không còn câu `suc_khoe` / `tho_yeu` / `sinh_san` nào. Mọi câu `vat_chat_nang` / `tat_xau` ở đoạn chính đều có hai căn cứ. Trên lá kiểm, sáu câu ở mục 1, dòng 5, đều đã chuyển đường hoặc gắn đủ điều kiện.

### G9. Holistic Interpretation Engine: luận tổ hợp thay cho luận từng sao (bổ sung 2026-11-07)

Đây là thay đổi lõi. Đơn vị cơ bản của việc luận đổi từ **`rule`** ("Thiên Việt ở Quan Lộc → được trọng dụng") sang **`configuration`**: một cấu trúc gồm nhiều yếu tố và các quan hệ giữa chúng.

G2–G6 sẽ dựng trên lớp này, nên G9 làm ngay sau G0–G1.

**Đã có gì, dùng lại gì.** Không viết lại từ đầu. Bốn mảnh hiện có đang rời nhau:
- `graph.ts`: đồ thị của từng lá, có node cung, sao, Hóa, finding và cạnh tam hợp, xung chiếu, giáp;
- `reason/structures.ts`: cách cục với boosters, breakers, rescuers, các trạng thái thành, phá, được cứu, cùng 6 bộ dò cấu trúc;
- `kg/combos.json` (bố cục KL tr.180-186) và `kg/che_hoa.json` (63 quan hệ chế hóa);
- `evidence.ts` và `ledger.ts`.

G9 gộp chúng thành một lớp duy nhất.

**G9.1 Đồ thị đầy đủ của lá.** Mở rộng `graph.ts`:
- **Node**: sao kèm trạng thái (độ sáng theo sách đang dùng, Hóa đi theo), cung, Tuần, Triệt, Thân.
- **Cạnh**: đồng cung, xung chiếu, tam hợp, giáp, nhị hợp, mượn sao (cung vô chính diệu), chế (theo `che_hoa.json`), hóa (Tứ Hóa gốc, Tứ Hóa của vận).

Phía Bát Tự có đồ thị riêng (`bazi_deep/graph.py`, mới):
- **Node**: can, chi, tàng can, kèm vai trong bản đồ hỷ kỵ;
- **Cạnh**: sinh, khắc, hợp, xung, hình, hại, phá, thông căn, thấu, đứng sát.

Đồ thị chỉ là cấu trúc dữ liệu. **Không kết luận nào được sinh ra từ việc đếm cạnh hay đếm node.**

**G9.2 Cấu hình (configuration) là đơn vị luận.** Một `Configuration` gồm:
- `id`, `topic` (công danh, tiền bạc…), `level` (cấp 1–6, xem bảng dưới);
- `core`: các node làm nòng cốt, ví dụ "Quan Lộc vô chính diệu ở Dần, mượn Cơ Âm vượng";
- `members`: các node đi kèm, mỗi node có `role`. Có năm vai:
  - `nen`: tạo tính chất;
  - `bien_tinh`: làm đổi tính chất của cả tổ hợp, ví dụ Hóa Quyền trên Thái Dương miếu;
  - `tro_luc`: thêm sức, ví dụ Thiên Việt, Tả Phụ;
  - `tru`: làm giảm, ví dụ Kình Dương, Hóa Kỵ;
  - `pha`: phá cả cấu trúc. Vai này chỉ được gán khi có câu sách;
- `relations`: các cạnh của đồ thị nối các thành viên;
- `rules`: các câu sách đã đối trang **mô tả chính tổ hợp đó hoặc một phần của nó**;
- `state`: thành, có điều kiện, bị phá, được cứu, chưa đủ dữ kiện;
- `questions`: các câu mà cấu hình phải trả lời, ví dụ cung vô chính diệu mượn sức từ đâu, Hóa Quyền đổi gì, sát tinh trừ tới đâu, có phá toàn bộ không;
- `activation`: chặng vận nào kích hoạt phần nào của cấu hình. G6 dùng trường này.

Cấu hình được nhận diện bằng **mẫu cấu hình** (`engine/data/kg/configurations.json`, mới). Mỗi mẫu là một biểu thức DSL trên đồ thị, kèm nguồn sách. Mẫu lấy từ ba chỗ:
1. cách cục đã đối trang trong `formations_verified`;
2. bố cục KL trong `combos.json`;
3. các khung đọc mà sách tự dạy, ví dụ cung vô chính diệu mượn sao đối cung (KL tr.218/222), hay ý nghĩa Tứ Hóa trên tam phương Mệnh, Tài, Quan.

Mỗi mẫu có `source` hoặc `he_thong`, như mọi phần khác. Mẫu `he_thong` chỉ được **gom** các câu sách lại với nhau, không được thêm nghĩa.

**G9.3 Thành viên làm đổi tính chất, không chỉ cộng điểm.** Mỗi vai có phép tác động riêng lên tổ hợp. Không có phép cộng 5 thuận trừ 2 nghịch.
- `bien_tinh` đổi `state` hoặc đổi `scope` của tổ hợp, ví dụ từ "có khả năng tổ chức" thành "đảm nhận quyền hạn".
- `tru` hạ `strength` một bậc, và chỉ trên mặt mà câu sách chỉ ra.
- `pha` đổi `state` thành bị phá. Nếu có `rescue`, trạng thái thành được cứu.

Thứ tự áp dụng cố định: nền, rồi biến tính, rồi trợ lực, rồi trừ và phá, rồi cứu giải. Mỗi bước để lại một dòng vết. Bộ giải xung đột của G4 chạy **trên cấu hình**, không chạy trên danh sách câu.

**G9.4 Thang cấp độ, và trần cấp độ.**

| Cấp | Đơn vị xét |
|---|---|
| 1 | Một sao ở một vị trí |
| 2 | Chính tinh và các sao đồng cung |
| 3 | Tam phương tứ chính và Tứ Hóa |
| 4 | Cách cục, phá cách, cứu giải |
| 5 | Liên hệ Mệnh, Tài, Quan, Phúc, Di |
| 6 | Đại vận, lưu niên tác động lên cấu trúc nguyên cục |

Một kết luận chỉ được có `scope` bằng **cấp cao nhất mà chứng cứ của nó đạt tới**. Nhận định cấp 1 không tự lên thành kết luận cấp 5 hay 6. Trường `level` được lưu trong mọi kết luận, và bất biến INV-12 kiểm trần này.

Phía Bát Tự có thang tương ứng:
1. một chữ;
2. một trụ;
3. quan hệ với nhật chủ;
4. cách và dụng thần;
5. toàn cục;
6. vận và năm.

**G9.5 Đầu ra là bản phân tích có cấu trúc** (`reason/analysis.ts`, mới). Mỗi chủ đề có một bản:

```
{ topic, level, dominant_configuration, supporting_evidence[], limiting_evidence[],
  interactions[], rescues[], unresolved_conditions[], activation[],
  conclusion: { type: thuan|co_dieu_kien|nghieng_ve|chua_phan_xu|..., scope, confidence, severity },
  evidence_ids[] }
```

Mọi `evidence_id` trỏ về một ruleId đã kích hoạt cộng các node của đồ thị, hoặc về một bước tính có nhãn. Bản phân tích này là đầu vào duy nhất của G10, và được trả ra ở `/api/interpretation` để kiểm.

**Xong khi:**
- Quan Lộc của lá kiểm được nhận diện thành một cấu hình duy nhất: vô chính diệu mượn Cơ Âm, biến tính bởi Thái Dương miếu hóa Quyền, trợ lực Việt và Phụ, bị Kình Dương và Hóa Kỵ trừ. Cấu hình trả lời đủ 6 câu trong `questions`, câu nào chưa đủ căn cứ thì nói là chưa đủ.
- Trên benchmark20, ≥ 90% kết luận miền có `dominant_configuration`.
- Không kết luận nào vượt trần cấp độ.

### G2. Bát Tự: vượng nhược và dụng thần làm lại từ gốc (việc 1 trong "ba việc")

*Dựng trên đồ thị và cấu hình Bát Tự của G9. Vượng nhược, bản đồ hỷ kỵ và mạch thập thần đều là cấu hình cấp 3–5.*

**G2.1 Bảng yếu tố ở đoạn chính, không giấu trong phần gập.** Dữ liệu đã có sẵn trong `tvh_score.score()` và `strength.compute()`, chỉ cần đưa ra. Đoạn vượng nhược đổi thành một bảng ngắn cùng một câu kết:
- từng chữ: trụ, can hoặc tàng can (bản khí, trung khí, dư khí), hành, nhóm, độ;
- phần lệnh tháng cộng hoặc trừ;
- gốc của nhật chủ: chi nào, ở giai đoạn trường sinh nào;
- tổng của phe mình so với mốc 40% (TVH tr.355).

Câu "một phần tư sức của tám chữ" bỏ đi. Thay bằng câu nói rõ là cân theo độ có tính mùa và tàng can.

**G2.2 Thang mức đủ bậc và độ chắc.** Mỗi kết luận vượng nhược mang ba thông tin:
- **mức**: nhược hoặc vượng, theo quy tắc 40% của sách;
- **gốc**: có căn hay vô căn, lấy từ `roots` và `root_grade`;
- **tòng**: đã loại trừ hay chưa, xét theo điều kiện tòng có nguồn trong `geju.py`, và nói thành lời "có căn ở Tỵ, Dần nên không xét tòng".

**Độ chắc** đo bằng phép thử nhiễu. Chạy lại quyết định vượng nhược với 3 hồ sơ trọng số:
- TVH thuần;
- hồ sơ hệ thống `compute()`;
- hồ sơ đổi `hidden_frac` / `dist_factor` ±20%.

Ba hồ sơ cùng ra một bên thì độ chắc là "vững". Khác nhau thì là "tạm xác định", và câu kết nói rõ là tạm. Tệp sửa: `strength.py` (thêm `stability()`), `pipeline.py`, `prose/bazi_deep.ts`, `content/prose/bat_tu.json`.

**G2.3 Bản đồ hỷ/kỵ từng hành, thay cho "nhóm dụng thần".** Gộp ba nguồn thành một bảng năm hành:
- phù ức (TVH tr.378-386);
- điều hậu (TVH tr.389-396, TTT);
- cách.

Mỗi ô ghi: hành, vai trong từng phép, và chỗ đồng thuận hay vênh. Hai phép **cùng chiều** khi can điều hậu thuộc nhóm dụng hoặc hỷ của phép phù ức. Trên lá kiểm, Giáp và Hỏa cùng chiều, Canh vênh. Tệp sửa: `bazi_deep/yongshen.py`, `pipeline.reconcile`, và `reconcileTs` ở phía TS.

Cách xử lý chỗ vênh theo **quyết định Q1**: không cố định bên nào được ưu tiên. Hai phép được đánh giá song song, rồi phân xử theo điều kiện của chính nguyên cục:
- **Cùng chiều**: độ vững của nhận định về hành đó tăng lên, và câu chữ nói rõ là hai phép cùng chỉ một hướng.
- **Khác chiều**: xét ba điều, mỗi điều thành một bước vết có nhãn:
  1. *Vấn đề khí hậu nặng tới đâu.* Luật hàn noãn (TTT) có phát không. Chỉ số nóng lạnh của lá cách xa mức giữa bao nhiêu. Có chữ điều hậu nào đã đứng sẵn trong nguyên cục chưa.
  2. *Điều kiện của từng phép đã thỏa chưa.* Bảng điều hậu xét theo can ngày và tháng. Phù ức thì xét vượng nhược đang ở độ chắc nào (G2.2): nếu vượng nhược chỉ "tạm" thì phù ức không đủ sức thắng.
  3. *Tương tác với các thần khác.* Chữ ấy hợp, khắc hay chế ai trong nguyên cục. Ví dụ, Canh là Tài, sẽ làm nặng thêm phe Tài vốn đang vượng.
- **Không phân xử được**: nêu cả hai kết quả có điều kiện, ví dụ "theo phép cân bằng thì Canh là kỵ; theo khí hậu thì Canh là can phụ cần có". Chỗ bất đồng được giữ trong dữ liệu (`unresolved: true`) và trong câu chữ, không gộp thành một điểm số.

Không có trọng số nào cộng hai phép thành một con số. Phân xử chỉ được làm bằng các điều kiện có tên kể trên, và mỗi điều kiện hiện ra trong vết.

**G2.4 Chấm vận theo vai thật của chữ trong vận.** Mỗi can và chi của vận đi qua bốn bước theo thứ tự, mỗi bước một dòng vết:
1. vai theo bản đồ G2.3;
2. tương tác với nguyên cục, lấy từ `interact.py` và `kg/bazi_luck_relations.json`: hợp giữ, xung, hình, **chế hóa kỵ thần** (ví dụ Mậu khắc Nhâm, mà Nhâm đang khắc dụng thần), mở kho, tàng dụng thần;
3. điều hậu;
4. phán quyết, kèm yếu tố chi phối.

Kết quả của bước 2 phải làm đổi được phán quyết. Hiện nay bước này chỉ được kể ra trong phần [sâu].

Phán quyết của vận mang theo độ chắc của G2.2. Nếu vượng nhược chỉ "tạm", câu vận phải có điều kiện "nếu nhật chủ nhược như trên".

**Xong khi:**
- Lá kiểm không còn câu "khác với dụng thần Tỉ Kiếp".
- Vận Mậu Tuất nêu việc Mậu chế Nhâm trong phán quyết, không chỉ trong phần [sâu].
- Bộ ví dụ có nhãn của TVH vẫn đạt độ khớp như cũ: `engine/tests/test_bazi_deep_fidelity.py`.
- `bazi_reconcile.test.ts` xanh.

### G3. Bát Tự: mạch thập thần có cấp, và một phán quyết nguyên cục

**G3.1 Mạch có cấp.** Mạch Tài → Quan → Ấn → Thân, và Thực → Tài, được chấm:
- **mạnh**: thấu can và đứng sát;
- **vừa**: thấu ở can, tàng ở chi cùng trụ (Nhâm trên Dần tàng Giáp), hoặc cách một trụ;
- **yếu**: chỉ tàng và cách xa;
- **đứt**: thiếu hẳn một khâu.

Cấp là quy ước `he_thong`, có ghi nhãn. Câu sách (ZZ, TVH, luật trụ bên trái) chỉ phát ở cấp mà trang sách mô tả. Tệp sửa: `bazi_deep/flow.py`, `kin.py`, `prose/bazi_kin.ts`.

**G3.2 Không phát hai luật trái nhau mà thiếu câu nối.** Ví dụ "chưa nối được" và "dễ đi lên đều". Trước khi phát, chạy cặp luật qua bảng đối nghịch mới `bazi_deep/opposed.json`. Có đối nghịch thì giữ câu đúng cấp mạch và nói rõ vì sao bỏ câu kia.

**G3.3 Phán quyết nguyên cục duy nhất.** Hiện có hai câu trái nhau:
- "Tài vượng, nhật chủ nhược… nên hung";
- "nhật chủ nhược, Tài vượng, có Ấn hoặc Tỉ Kiếp hộ thân được đánh giá là mệnh tốt".

Đưa cả hai vào `reconcile` thành một phán quyết. Câu sau có điều kiện "có hộ thân", nên xét hộ thân ấy mạnh tới đâu, theo cấp mạch G3.1 và gốc G2.2.

**Xong khi:** test mới `bazi_contradiction.test.ts` cho kết quả 0 cặp câu đối nghịch trên 300 lá mà không có câu nối. Lá kiểm còn đúng một câu kết cho thế cát hung của cả lá.

### G4. Tử Vi: bộ giải xung đột thật (việc 2 trong "ba việc", phần lớn nhất)

*Chạy trên các cấu hình của G9. Bảng yếu tố dưới đây là các vai `nen`, `bien_tinh`, `tro_luc`, `tru`, `pha` của thành viên, không phải các điểm cộng trừ rời nhau.*

**G4.1 Cân toàn bộ chứng cứ, không chỉ câu nặng nhất.** Viết lại `weighSides` trong `reason/ledger.ts` thành `adjudicateDomain()`. Bộ này nhận đủ các yếu tố mà `evidence.ts` đã gom. Mỗi yếu tố có trọng số trong `domains.json weigh` (quy ước có nhãn):

| Yếu tố | Đã có dữ liệu ở |
|---|---|
| Chính tinh của cung và độ sáng theo sách đang dùng; cung vô chính diệu mượn sao thì giảm một bậc | `evidence.ts`, `tiers.ts`, `dignity` |
| Tứ Hóa: sao nào, đứng ở đâu trong tam phương tứ chính (Lộc, Quyền, Khoa cộng; Kỵ trừ, hoặc "mixed" nếu sao mang Kỵ) | `evidence.ts ky_carrier`, `tu_hoa` |
| Vị trí: đồng cung > xung chiếu > tam hợp > giáp | `positions.ts`, `structures.ts` |
| Lục cát, lục sát theo tầng sao (T1–T6) | `tiers.ts` |
| Tuần, Triệt trên cung | `evidence.ts` |
| Quan hệ chế hóa có sách, ví dụ "Khôi Việt sợ Kình Đà…" làm nhẹ Thiên Việt | `kg/che_hoa.json` (63 mục) |
| Câu sách trực tiếp của cung trên đúng mặt của miền đó | ledger `pos` / `neg` |

**Đầu ra** là `DomainJudgement`, gồm:
- `lean`: thuận, nghịch hoặc cân;
- `strength`: rõ, vừa hoặc nhẹ;
- `dominant[]`, `reducers[]`, `rescue[]`, `unknown[]`;
- `confidence`;
- bảng yếu tố đã cân, để hiện trong panel chứng cứ.

**G4.2 Luật không đếm sao.** Một bên có nhiều sao hơn không tự thắng. Yếu tố `count` chỉ được làm lý do phụ, không bao giờ là lý do duy nhất. Có test kiểm.

**G4.3 Cân bằng thật thì nói điều sẽ làm nghiêng.** Khi `|thuận − nghịch| < margin`, câu kết phải nêu yếu tố treo, ví dụ "Tứ Hóa của đại hạn 33–42 sẽ quyết định". Yếu tố treo lấy từ `vanhan` / `course`.

**G4.4 Bộ kiểm định do chủ dự án chấm** (quyết định Q3). Xây khung bộ kiểm định trước, rồi mới chấm.

Bộ chính có 30 tình huống, chia ba nhóm, mỗi nhóm 10:
- **A**: tổ hợp thuận lợi, có yếu tố bất lợi nhẹ;
- **B**: xung đột mạnh, có cứu giải hoặc chế hóa;
- **C**: thiếu điều kiện thành cách, có ngoại lệ, hoặc là quy tắc dễ bị suy diễn quá mức.

Mỗi tình huống là một tệp trong `src/interpret/test/fixtures/gold/<id>.json`, gồm:
- `chart`: facts của lá;
- `domain`: miền đang xét, hoặc cách, hoặc vận;
- `evidence`: các ruleId và yếu tố phải được kích hoạt;
- `expected`: lean, strength, dominant, reducers;
- `forbidden`: những kết luận và cụm từ bị cấm;
- `why`: lý do của người chấm.

Mình soạn sẵn tình huống, danh sách chứng cứ và một bản nháp kết luận để chủ dự án sửa, nên chủ dự án không phải viết từ đầu.

**Chống khớp quá mức (overfitting).**
- Trọng số trong `domains.json` chỉ được chỉnh theo 30 tình huống này.
- Một **tập kiểm định độc lập** khoảng 15 tình huống, cũng chia theo A, B, C, chọn ngẫu nhiên từ corpus1000, được chấm **trước** khi chỉnh trọng số. Tập này không được nhìn vào trong lúc chỉnh. Tệp nằm ở `fixtures/gold_holdout/`.
- Báo cáo ghi độ khớp trên cả hai tập.
- Nếu độ khớp trên tập kiểm định thấp hơn tập chính quá 15 điểm thì không nhận bộ trọng số đó.

Bộ kiểm định chỉ đo **tính nhất quán, độ đủ của chứng cứ và chất lượng lập luận** theo hệ quy tắc. Nó không chứng minh khả năng dự đoán thực tế của Tử Vi hay Bát Tự. Báo cáo phải ghi rõ điều này.

**G4.5 Mẫu câu kết bốn phần**, đặt trong `content/prose/luan.json ledger.*`, lấy đoạn Quan Lộc mẫu trong bản đánh giá làm đích. Thử trên lá kiểm, câu kết Quan Lộc phải:
- nêu thế Cơ Âm vượng chiếu từ Phu Thê;
- nêu Thái Dương miếu hóa Quyền ở Tài Bạch cùng Tả Phụ và Thiên Việt;
- nêu sức trừ của Kình Dương ở Mệnh và Văn Xương hóa Kỵ ở Phu Thê;
- nói rõ chưa ấn định được mốc 40 tuổi, và lý do.

**Xong khi:**
- `eval_synthesis.ts` trên corpus1000 cho tỉ lệ miền dừng ở "chưa phân xử" ≤ 10%. Phải đo mức hiện tại trước khi sửa và ghi vào báo cáo.
- Độ khớp ≥ 80% trên bộ 30 tình huống và ≥ 70% trên tập kiểm định độc lập.
- Không tình huống nào chứa kết luận nằm trong `forbidden`.
- `readable.test` và `luan.test` xanh.
- Số câu bị lọc bỏ (strip) không vượt ngưỡng hiện tại.

### G5. Cách cục: thành, phá, cứu giải, trước khi xếp hạng

1. Mỗi cách mang thêm các trường mới:
   - `where`: đồng cung với Mệnh, hay chiếu từ cung nào;
   - `state`: thành, phá hoặc được cứu, theo điều kiện có nguồn trong `formations_verified`, mỗi trạng thái có `meaning` riêng;
   - `rescue[]`: tìm trong cung mang cách và trong tam phương Mệnh.
2. Sức nặng của một cách được tính theo `where` × `state`, có nhãn quy ước. Câu "cách X có sức nặng nhất" chỉ được nói kèm lý do. Câu cách cục phải đối chiếu với phán quyết miền Mệnh của G4. Ví dụ, nếu Mệnh có Hóa Lộc và tam phương có Quyền, Khoa, thì một cách xấu chỉ chiếu tới không thể được gọi là nặng nhất mà không giải thích.
3. Tệp sửa: `prose/cach_cuc.ts`, `engine/tvbt/cach_cuc.py` (trường `where`), `content/prose/cach_cuc*.json`.

**Xong khi:** trên lá kiểm, cách Đào hoa Thiên không được nói là "chiếu từ Tài Bạch, có Quyền và Khoa đồng cung đỡ một phần". Câu xếp hạng có lý do. Không còn "cả đời".

### G6. Vận hạn: vận tác động lên nguyên cục, khung tuổi, đối chiếu hai hệ, công khai thang chấm

**G6.0 Vận được luận như tác động lên cấu trúc nguyên cục**, không chấm từng vận như một lá riêng. Với mỗi chặng:
- Liệt kê các cấu hình nguyên cục mà chặng đó **kích hoạt**, theo trường `activation` của G9.2: cung hạn rơi vào thành viên nào, Tứ Hóa của hạn đổi vai thành viên nào, can chi của vận hợp, xung hay chế chữ nào của nguyên cục.
- Câu luận nói chặng ấy làm phần nào của cấu trúc phát huy hoặc suy yếu, ví dụ "đại hạn 33–42 đưa Hóa Kỵ vào X, nên phần trợ lực của cấu hình công danh bị trừ".
- Mức chỉ số (`indices.ts`) vẫn giữ để vẽ biểu đồ. Nhưng câu luận phải đi từ cấu hình được kích hoạt, không đi từ con số.

Phía Bát Tự cũng vậy: vận được đọc như can chi của vận tác động lên đồ thị nguyên cục, theo các bước của G2.4.

1. **Ba dạng đánh giá vận** (quyết định Q4). Toàn bộ đại hạn và đại vận vẫn nằm trong dữ liệu, và vẫn được luận từng chặng. Riêng phần tổng quan tách ra ba dạng:

   | Dạng | Phạm vi |
   |---|---|
   | Đại vận hiện tại | chặng mười năm đang đi |
   | Đại vận đáng chú ý sắp tới | 20–30 năm tiếp theo, tức hai đến ba chặng kế |
   | Xếp hạng toàn đời | các chặng **bắt đầu trước 80 tuổi** |

   Chặng bắt đầu từ 80 tuổi trở đi không được chọn làm "chặng thuận nhất / thấp nhất đời".

   **Không gọi một chặng là tốt nhất hay thấp nhất** khi có một trong hai điều sau:
   - nó hơn chặng kế tiếp dưới một bậc mức, hoặc dưới ngưỡng chênh `index_norms.rank_margin`, một quy ước có nhãn;
   - nó **đổi hạng** khi chấm lại bằng các biến thể thang chấm: 5 mẫu corpus khác nhau ở bước 3, và các tiểu hạn TH/KL.

   Gặp trường hợp đó, câu chữ nói "vài chặng ngang nhau", rồi kể các chặng ấy ra.

   `course.ts` không gọi "nổi lên" cho chặng có mức thử thách. Gọi đúng tên: "hạn vào chính cung Quan Lộc, mức nhiều thử thách".
2. **Bảng đối chiếu hai hệ theo thập niên.** Đặt trong chương Tổng luận và phần đại hạn. Mỗi hàng có:
   - đại hạn Tử Vi (tuổi âm, cung, mức);
   - đại vận Bát Tự (năm, can chi, phán quyết G2.4);
   - cột "cùng chiều / vênh", kèm một câu lý do mỗi bên.

   Không gộp hai bên thành một điểm vì đây là hai hệ khác nhau. Khi vênh thì nói rõ là vênh. Tuổi được quy về năm dương lịch để hai bên thẳng hàng. Tệp sửa: `prose/tong_luan.ts`, `prose/vanhan.ts`, và một khối mới trong `report.js`.
3. **Công khai thang chấm.** Thêm một mục "Cách chấm mức" có thể mở ra, nói rõ:
   - mẫu 1.000 lá được sinh thế nào (`make_corpus.py`: ngày giờ ngẫu nhiên đều, phân bố năm sinh);
   - ngưỡng phân vị 12/33/67/88%;
   - **độ ổn định**: sinh 5 mẫu 1.000 lá khác nhau, đo tỉ lệ chặng giữ nguyên mức. Công cụ mới `eval_indices.ts --stability`, kết quả ghi vào `docs/INDICES-EVAL.md`.

   Câu ghi chú bỏ chữ "xếp theo phân vị của 1.000 lá số mẫu" đứng trơ. Thay bằng "xếp hạng theo quy tắc của hệ thống, chưa phải dự báo đã hiệu chuẩn".
4. **Nối câu mốc tuổi với vận.** Câu "đến muộn, ngoài 40" (G1) được đặt cạnh mức các đại hạn sau 40 tuổi. Nếu các chặng đó thấp, câu phải nói là hai bên chưa khớp.

**Xong khi:**
- Lá kiểm không còn "93–102 thuận nhất" và "nổi lên ở 83–92".
- Ba dạng đánh giá vận đều có trên lá kiểm.
- Bảng hai hệ phủ đủ các thập niên bắt đầu trước 80 tuổi.
- Số đo độ ổn định có trong INDICES-EVAL.
- Mọi chặng được gọi là "nhất" đều qua được phép thử đổi hạng.

### G7. Truy vết và câu chữ

1. **Vai của chứng cứ.** Mỗi `LedgerItem` có thêm `role` với ba giá trị:
   - `truc_tiep`: câu sách ở chính cung, đúng mặt của miền;
   - `gian_tiep`: từ tam phương, xung chiếu hoặc mượn sao;
   - `phu_tro`: sao nhỏ ở tầng T5–T6.

   Câu kết chỉ được dựa trên chứng cứ trực tiếp, hoặc gián tiếp có nói rõ. Panel chứng cứ (`/api/interpretation`) hiện cột này.
2. **Câu khuyên không tự đứng một mình.** Cấm các câu "Nên giữ nhịp", "Cần đi chậm và chắc", "kiên nhẫn" nếu không gắn với yếu tố chi phối của chặng hoặc miền. Mở rộng `adviceSource` sang `vanhan.ts` và `tong_luan.ts`. Thêm luật vào `quick_check`.
3. Tả Phụ hãm mà câu nói "được người trên tin cậy": khi sao hãm đi với câu sách tốt, câu phải nói thế hãm làm nhẹ bớt ý đó. Câu này cần có mẫu câu và trang sách cho độ sáng của Tả Phụ. Nếu sách đang dùng không cho Tả Phụ độ sáng thì không hiện "(Hãm Địa)". Kiểm `dignity_kb`.

### G10. Deep Narrative Engine: viết theo mạch lập luận (bổ sung 2026-11-07)

Thay công thức "Vì sao A nên B. Bên cạnh đó, sao C cho thấy D. Ngoài ra…" bằng cách viết đi theo **mạch lập luận của bản phân tích G9.5**, không đi theo thứ tự luật kích hoạt.

Lõi diễn đạt vẫn là máy tất định: kế hoạch đoạn, khung câu và bộ ghép câu. Nó dựng tiếp trên `prose/narrative.ts`, `discourse.ts` và `realize.ts`, không dùng LLM (luật 7).

**G10.1 Đoạn năm lớp.** Mỗi đoạn luận một cấu hình theo năm lớp, mỗi lớp lấy từ một trường của bản phân tích:

| Lớp | Nội dung | Lấy từ |
|---|---|---|
| 1. Bản chất | Cấu trúc tổng thể biểu thị xu hướng gì theo hệ truyền thống | `dominant_configuration`, cùng tính chất sao có trang sách trong `star_nature.json` (trường `explains`) |
| 2. Cơ chế | Các thành viên phối hợp với nhau ra sao để tạo xu hướng đó | `members` theo vai, `relations` |
| 3. Mâu thuẫn nội tại | Điểm mạnh đi kèm giới hạn nào, và vì sao | `limiting_evidence`, `interactions` |
| 4. Điều kiện chuyển hóa | Điều gì làm cấu trúc phát huy hay suy yếu, gồm cả chặng vận | `rescues`, `activation`, `unresolved_conditions` |
| 5. Biểu hiện và giới hạn | Có thể hiểu thế nào trong đời sống, và phần nào chưa kết luận được | `conclusion.scope`, `confidence`, phần chưa biết |

Lớp nào không có dữ liệu thì bỏ lớp đó. Không lấp bằng câu chung chung.

Lớp 1 và lớp 5 chỉ được nói tính chất có nguồn. Ví dụ "Cơ Âm thiên về suy xét, tổ chức" chỉ được nói khi `star_nature.json` có câu sách cho tính chất đó. Không có thì câu ấy không được viết.

**G10.2 Ràng buộc nguồn ở mức mệnh đề.** Mỗi mệnh đề trong câu mang `evidence_id`. Bộ ghép câu (`realize.ts`) từ chối mọi khung câu có slot nội dung không gắn được với một trường của bản phân tích. Câu không có `evidence_id` hợp lệ thì bị chặn, hoặc thành "minh họa" có nhãn, gắn với đúng một mệnh đề có nguồn (`illustration-policy`).

**G10.3 Từ nối đi theo quan hệ, không theo thói quen.** Từ nối được chọn từ loại quan hệ giữa hai mệnh đề:
- bổ trợ: "hai khuynh hướng ấy đỡ cho nhau";
- nhân quả: chỉ khi có cạnh trong đồ thị hoặc quan hệ sách;
- tương phản;
- điều kiện;
- nhượng bộ.

Các từ "bên cạnh đó", "ngoài ra", "cho thấy", "vì vậy" có hạn mức theo mật độ. Mỗi đoạn phải có tiến triển: mỗi câu thêm vào một `evidence_id` mới hoặc một quan hệ mới. Câu chỉ nhắc lại ý trước thì bị bỏ.

**G10.4 Bộ đo chất lượng văn bản** (`tools/interpret/eval_narrative.ts`, mở rộng `eval_deep3`). Mỗi tiêu chí có một số đo tự động. Ngoài ra, chủ dự án chấm tay 20 đoạn theo phiếu 1–5 điểm.

| Tiêu chí | Số đo |
|---|---|
| Liền mạch | Mỗi đoạn có đúng một `thesis`, mọi câu khác là con của nó trong kế hoạch đoạn |
| Nhân quả | Tỉ lệ từ nhân quả có cạnh hoặc quan hệ sách đứng sau là 100%. Số câu chỉ có "vì" mà không có cơ chế |
| Đặc thù | Thử bỏ tên sao: độ giống sau khi bỏ (strip sim, đã có, ngưỡng 0,0655). Thử đổi lá: cùng khung đoạn trên 50 lá khác nhau, độ giống nội dung |
| Đa chiều | Tỉ lệ đoạn có cả lớp 3 và lớp 4 khi cấu hình có thành viên `tru` |
| Tiết chế | 0 từ tuyệt đối (INV-11), 0 câu nặng ở đoạn chính (INV-6) |
| Chiều sâu | Tỉ lệ đoạn luận một cấu hình cấp ≥ 3 so với đoạn liệt kê sao cấp 1 |
| Tự nhiên | dup5 / skel5 (đã có), mật độ từ nối thói quen, `eval_repeat` |

**G10.5 Bước phản biện trước khi xuất** (`prose/critic.ts`, mới). Bước này chạy tất định trên bản luận đã ghép. Mỗi câu hỏi phản biện thành một phép kiểm. Đoạn trượt thì bị viết lại theo cách gọn hơn, hoặc bỏ, và ghi vào `quality.warnings`:

| Câu hỏi phản biện | Phép kiểm |
|---|---|
| Bỏ tên sao đi, đoạn này có dùng được cho hàng nghìn lá khác không? | Thử bỏ tên sao và thử đổi lá ở mức đoạn |
| Có kết luận nào dựa trên một sao mà bị nâng thành nhận định cả đời không? | Trần cấp độ (INV-12) và INV-11 |
| Có hai câu nói cùng một ý không? | Trùng `evidence_id` hoặc trùng `concept` trong cùng chương |
| Có yếu tố quan trọng nào bị bỏ sót vì không nằm trong nhóm luật được chọn không? | So thành viên `nen` và `bien_tinh` của cấu hình chi phối với các node được nói ra. Node `bien_tinh` không được nhắc thì trượt |
| Có kết luận nào mâu thuẫn với phần khác không? | INV-3, INV-4 |
| Đảo một yếu tố then chốt thì kết luận có đổi hợp lý không? | Kiểm thử phản chứng, xem dưới |

**G10.6 Kiểm thử phản chứng ở mức cấu hình.** Mở rộng `counterfactual100` (đã có khung `critical` / `inert`) bằng các phép đổi nhắm vào cấu hình, ví dụ:
- bỏ Hóa Quyền khỏi Thái Dương;
- đưa Kình Dương ra khỏi tam phương;
- cho Quan Lộc một chính tinh;
- đổi tháng sinh Sửu thành Ngọ (Bát Tự).

Mỗi phép đổi có kỳ vọng viết sẵn theo luật của mẫu cấu hình. Ví dụ, bỏ `bien_tinh` thì `scope` phải hẹp lại, còn đổi một sao `tro_luc` thì `state` giữ nguyên. Số đo: tỉ lệ phản ứng đúng ≥ 90%, và với phép đổi không ảnh hưởng (`inert`) thì văn bản phải giữ nguyên.

**Xong khi:**
- Đoạn Quan Lộc của lá kiểm đạt đủ năm lớp và ba câu chuẩn ở mục 2.
- Mọi mệnh đề có `evidence_id`.
- Các số đo G10.4 trên benchmark20 không kém mức hiện tại, và đặc thù cùng chiều sâu phải tốt hơn rõ.
- Bước phản biện không còn đoạn trượt nào ở đoạn chính.
- Phiếu chấm tay trung bình ≥ 4/5.

Đoạn Quan Lộc mẫu trong bản bổ sung chỉ là **đích về chất lượng giải thích**. Không câu nào của nó được chép vào khung câu. Mọi tính chất trong đoạn phải ra từ dữ liệu có nguồn.

**G10.7 Chuẩn giọng văn** (đề xuất của chủ dự án, 2026-11-08). Prompt gốc được lưu nguyên văn ở `docs/plans/NARRATIVE-STYLE-PROMPT.md`. Prompt ấy viết cho một mô hình ngôn ngữ. Ở đây nó được dùng theo hai cách, cách thứ hai cần chủ dự án quyết (Q5).

*Cách 1 (mặc định, không dùng LLM).* Chuyển prompt thành luật cho bộ ghép câu và bước phản biện G10.5:

| Ý trong prompt | Thành luật gì |
|---|---|
| Ba giọng theo từng phần: Mệnh/Thân khái quát và liên kết; 12 cung, cách cục, dụng thần nặng lập luận và cơ chế; vận hạn điềm tĩnh, có trình tự | Mỗi chương mang trường `register`, có ba bộ khung câu và ba bảng từ nối riêng. Thứ tự năm lớp G10.1 được đổi theo giọng (vận hạn: bối cảnh, rồi kích hoạt, rồi điều kiện) |
| Cấm lặp "Vì có sao A nên", "Bên cạnh đó", "Ngoài ra", "Điều này cho thấy", "Về mặt tốt / xấu", "tốt xấu đan xen", "không phải… mà là…" | Thêm vào luật `quick_check`: hạn mức theo mật độ cho từng cụm, riêng "không phải… mà là…" thì cấm hẳn trong câu của hệ thống |
| Không lạm dụng tính từ (huy hoàng, phi thường, định mệnh, xuất chúng, đại phú đại quý) | Danh sách cấm trong câu của hệ thống. Câu sách trích thì giữ nguyên lời sách |
| Thuật ngữ được giải thích ngắn ở lần đầu xuất hiện | Bảng chú giải `content/prose/glossary.json`, mỗi mục có trang sách hoặc nhãn `he_thong`. Bộ ghép câu chèn lời chú giải ở lần gặp đầu trong báo cáo |
| Câu ngắn để nhấn, câu dài để phát triển lập luận; không câu cụt rời rạc | Số đo nhịp: độ lệch chuẩn độ dài câu trong đoạn có ngưỡng dưới, số câu dưới 8 chữ đứng liền nhau có ngưỡng trên |
| Không để mọi cung có cùng số đoạn, cùng nhịp mở, cùng kiểu kết | Số đo `skel5` mở rộng cho câu mở và câu kết của chương. Tỉ lệ chương trùng khung mở và khung kết có ngưỡng trên |
| 9 câu tự biên tập | Ánh xạ vào bước phản biện G10.5. Câu 1–5 và 8 đã có phép kiểm. Câu 6 ("kết luận mạnh hơn chứng cứ") kiểm bằng cách so từ mức độ của câu với `confidence`. Câu 7 ("đọc thành tiếng có tự nhiên không") thuộc phiếu chấm tay |
| Trung thực: không thêm sao, trạng thái, thời điểm, không nâng mức chắc, không đoán biến cố nặng | Đã có ở luật 4–7, INV-1, INV-6, INV-12, INV-13 |

*Cách 2 (cần quyết định, Q5).* Thêm một **lớp biên tập văn bằng LLM** chạy sau lõi tất định, dùng đúng prompt này. Lớp này được bao bởi các rào chắn:
- **Đầu vào:** bản phân tích G9.5 cộng bản nháp tất định. Mô hình không nhận gì khác.
- **Bộ kiểm đầu ra,** chạy tất định trên mỗi đoạn:
  - mọi tên sao, cung, Hóa, can chi, số tuổi, năm và trang trong văn bản mới phải có trong đầu vào;
  - mỗi câu mới phải ánh xạ được vào ít nhất một `evidence_id` của bản nháp;
  - không câu nào mang từ mức độ mạnh hơn `confidence`;
  - INV-1, 6, 11, 12, 13 phải xanh.
- **Trượt thì giữ bản tất định.** Một đoạn trượt bộ kiểm thì người đọc nhận bản tất định của đoạn đó, và lần trượt được ghi lại.
- **Bật bằng cờ riêng,** cache theo lá số, có nhãn "văn bản đã được biên tập lại".

Đổi lại: văn mượt hơn hẳn. Cái giá: rủi ro "sai sâu hơn" mà chính chủ dự án đã nêu, chi phí cho mỗi lần luận, văn bản không còn tất định, và đi ngược quyết định giữ hệ không dùng LLM từ trước đến nay.

**Xong khi (cách 1):**
- Luật giọng văn có trong `quick_check`.
- Ba giọng có mặt trên lá kiểm.
- Mật độ các cụm cấm giảm ít nhất một nửa so với mức hiện tại trên benchmark20.
- Phiếu chấm tay mục "tự nhiên" trung bình ≥ 4/5.

### G-INV. Bộ test bất biến xuyên báo cáo (đề xuất của chủ dự án, 2026-11-07)

Đây là lớp kiểm thử chạy trên **toàn bộ báo cáo đã ghép**, không chạy trên từng module riêng lẻ. Đầu vào là đúng `proseAllChapters` cộng `checkedOnly`, tức báo cáo người đọc thấy, cùng với facts và ledger.

Bộ này dựng **ngay đầu đợt**, cùng lúc với G0. Lần đầu chạy nó sẽ đỏ, vì chính nó ghi lại các lỗi của bản đánh giá. Mỗi giai đoạn sau đó làm xanh dần từng bất biến. Từ đó trở đi, bộ test là cổng phải qua trước mỗi lần push.

Tệp:
- `src/interpret/test/invariants.test.ts`: chạy trên lá kiểm, site_sample_1990 và benchmark20;
- `tools/interpret/eval_invariants.ts --n 300`: chạy trên corpus, in số vi phạm theo từng bất biến.

Để kiểm được bằng máy, mỗi câu tổng hợp phải mang `trace` có cấu trúc (G7.1 và luật 4), không phải chuỗi chữ. Phần "mở rộng trace" vì thế thuộc G-INV.

| Mã | Bất biến | Cách kiểm |
|---|---|---|
| INV-1 Vị trí | Sao được nói là "ở, tọa thủ, đứng ở, đồng cung" cung X thì phải có mặt ở X trong facts. Sao "chiếu, hội chiếu, xung chiếu" thì phải đúng nằm trong tam phương hoặc xung chiếu của X. Cung đối của X phải đúng | Bóc cụm "<sao> … ở cung <X>" và các động từ vị trí ra khỏi câu, rồi so với `palaces` |
| INV-2 Nguyên nhân | Mọi "do / nhờ / vì / nền ở / yếu tố làm nên" trong Tổng luận, câu kết chương và Đọc sâu phải truy được tới một ruleId đã kích hoạt **và** dữ kiện kích hoạt nó. Sao được nêu tên phải thuộc `stars` của rule đó | Đọc `trace.cause = {ruleId, facts[]}`. Câu nào có từ nguyên nhân mà thiếu trường này thì trượt |
| INV-3 Đối nghịch xuyên chương | Hai chương có phán quyết trái chiều về cùng một miền hay cùng một mặt thì một trong hai phải ghi rõ điều kiện tạo ra sự khác biệt: khác mặt, khác thời, khác hệ hoặc khác phép | So `DomainVerdict` và phán quyết Bát Tự giữa các chương. Cặp trái chiều phải có `trace.diffReason` |
| INV-4 Tổng luận khớp chương | Tổng luận không được mạnh hơn hay khác chiều với phán quyết miền của chương gốc. Thứ hạng "đứng đầu" không được trái với biểu đồ cung mà không có câu giải thích | So `tong_luan` với `ledger` và radar |
| INV-5 Bốn câu hỏi | Mọi đối tượng kết luận (`DomainJudgement`, phán quyết vận, phán quyết nguyên cục Bát Tự, cách cục) đều có đủ `why`, `conditions`, `reducers` và `unknown`, và câu chữ có nói ra cả bốn | Kiểm dữ liệu, rồi kiểm có slot tương ứng trong câu |
| INV-6 Câu nặng | Không câu nào có `severity` ≥ nặng xuất hiện trong đoạn chính, câu kết chương hay Tổng luận. Câu nặng trong Đọc sâu phải có trang, điều kiện và nhãn "chưa xác minh thực nghiệm" | Đọc `trace.severity` cùng chỗ đứng của đoạn |
| INV-7 Bản đồ hỷ kỵ | Một hành có cùng một vai (dụng, hỷ, kỵ, nhàn) ở mọi chương Bát Tự. Câu nói hai phép "khác nhau" chỉ được viết khi ô đó thật sự vênh | So các câu với bảng G2.3 |
| INV-8 Mạch Bát Tự | Không có cặp câu đối nghịch trong `opposed.json` cùng hiện mà thiếu câu nối (G3.2) | Bóc cặp từ trace |
| INV-9 Hạng "nhất" | "Thuận nhất / thấp nhất / nặng nhất / đứng đầu" chỉ xuất hiện khi qua ngưỡng chênh và phép thử đổi hạng (G6.1, G5.2) | Đọc `trace.rank = {margin, stable}` |
| INV-10 Mốc tuổi | Câu có mốc tuổi phải đặt cạnh mức các chặng tương ứng. Câu không được nói "thành công sau X" nếu không kèm mức của các chặng sau X | Bóc số tuổi rồi so với `decades` |
| INV-11 Không tuyệt đối | Câu tổng hợp không chứa "cả đời / suốt đời / chắc chắn / không bao giờ" (câu sách trích nguyên văn được miễn) | Lọc chuỗi theo `basis` |
| INV-12 Trần cấp độ | `conclusion.scope` không vượt cấp cao nhất mà chứng cứ của nó đạt tới (G9.4) | Đọc `level` của từng `evidence_id` |
| INV-13 Mệnh đề có nguồn | Mọi mệnh đề nội dung có `evidence_id` hợp lệ, hoặc mang nhãn minh họa (G10.2) | Đọc trace ở mức mệnh đề |

**Xong khi:** `eval_invariants` trên 300 lá cho 0 vi phạm ở INV-1, 2, 4, 6, 7, 11, 12, 13. Các bất biến còn lại ≤ 1% số kết luận. Mọi vi phạm còn sót được liệt kê trong báo cáo G8, kèm lý do.

### G8. Kiểm chứng và trả bài

- Báo cáo `docs/audit/THIEN-BAN-33.md` có:
  - bảng "trước / sau" cho từng điểm của bản đánh giá trên lá kiểm;
  - số đo corpus: tỉ lệ chưa phân xử, số câu nặng ở đoạn chính, số cặp câu đối nghịch Bát Tự, độ ổn định vượng nhược, độ ổn định mức vận.
- Ví dụ trước và sau ở `docs/examples/thien-ban-33-truoc-sau.md`, gồm đoạn Quan Lộc, vượng nhược, vận Mậu Tuất, cách cục, Tổng luận.
- Chạy test theo `testing-lessons`:
  - `npm run check:prose` trước;
  - sau đó chỉ test của các module đã sửa;
  - toàn bộ một lần, chạy tách ra bằng `nohup`, trước khi push;
  - golden cập nhật bằng `UPDATE_GOLDEN=1`.
- Chuỗi sinh lại khi đổi trạng thái luật (G1), theo thứ tự: `refire_fixtures.py` → `base_rates.ts` → `build.ts` → `index_norms.ts` → `build_site.py`.

---

## 4. Quyết định của chủ dự án (2026-11-07)

| # | Câu hỏi | Quyết định | Ghi vào |
|---|---|---|---|
| Q1 | Phù ức và điều hậu vênh nhau | Không cố định bên nào. Hai phép đánh giá song song: cùng chiều thì tăng độ vững, khác chiều thì phân xử theo điều kiện cụ thể của nguyên cục. Không phân xử được thì nêu hai kết quả có điều kiện. Không dùng trọng số tùy ý để ép hai phép về một kết luận | G2.3, G2.4, luật 6 |
| Q2 | Câu sức khỏe, thọ yểu, con cái | Để trong Đọc sâu, có kiểm soát: trích đúng, kiểm điều kiện, ghi "quan niệm truyền thống chưa xác minh thực nghiệm". Câu khẳng định cụ thể đổi thành mô tả trung tính. Không bao giờ vào kết luận chính hay Tổng luận. `severity` là trục riêng, không phụ thuộc `confidence` | G1.3, luật 5, INV-6 |
| Q3 | Bộ tình huống chấm tay | 30 tình huống (A, B, C, mỗi nhóm 10), mỗi tình huống có chứng cứ, kết luận mong đợi, kết luận bị cấm và lý do. Có thêm một tập kiểm định độc lập để chống khớp quá mức. Bộ này không chứng minh khả năng dự đoán | G4.4 |
| Q4 | Khung xếp hạng vận | 80 tuổi, toàn bộ vận vẫn giữ trong dữ liệu. Tách ba dạng: hiện tại, 20–30 năm tới, toàn đời. Không gọi "nhất" khi chênh nhỏ hoặc khi đổi hạng theo cách chấm | G6.1, INV-9 |
| Thêm | Bộ test bất biến xuyên báo cáo, cùng tiêu chí nghiệm thu bốn câu hỏi | Nhận | G-INV, mục 2 |
| Q5 | Có thêm lớp biên tập văn bằng LLM (G10.7 cách 2) không? | 2026-11-08: thử, có kiểm. Chỉ vài chỗ nhỏ, không toàn bộ. Tiết kiệm token hết mức. Cách 1 vẫn làm | G10.7, mục 6 |
| Thêm | G9 luận tổ hợp (đơn vị luận là cấu hình, có đồ thị và thang 6 cấp), G10 lõi diễn đạt theo mạch lập luận (đoạn 5 lớp, phản biện, kiểm thử phản chứng). Hai lõi tách nhau, không dùng LLM. Chuẩn đoạn luận có ba câu hỏi | Nhận. Thứ tự: G0–G1, rồi G9, rồi G2–G5, rồi G6, rồi G10, rồi G7–G8 | G9, G10, mục 2, mục 5 |

---

## 5. Thứ tự và cách chia việc

Thứ tự theo đề xuất bổ sung 2026-11-07: G9 và G10 không xếp sau G0–G8. Lõi tổ hợp đi trước để các phần khác dựng trên nó.

1. **G-INV (khung, cùng INV-1, 2, 4, 11) + G0 + G1**: một nhánh, làm ngay, đẩy lên main trước. Không chờ G9, vì đây là lỗi sai sự thật, điều kiện luật và câu nặng.
2. **G9**: đồ thị, cấu hình, thang cấp độ, bản phân tích có cấu trúc, cho cả Tử Vi lẫn Bát Tự, cùng INV-12.
   - Mẫu cấu hình Tử Vi và Bát Tự có thể soạn song song.
   - Kiểu `Configuration` / `Analysis` chung phải chốt trước.
3. **G2 + G3** (Bát Tự, cùng INV-7, INV-8) và **G4 + G5** (Tử Vi, cùng INV-3, INV-5): hai nhánh song song trên cấu trúc G9. Hai bên không đụng tệp của nhau. Chỉ `invariants.test.ts` là chung, và mỗi nhánh chỉ thêm khối bất biến của mình.
   - **Bộ tình huống G4.4** soạn song song với nhánh Tử Vi. Tập kiểm định độc lập được chấm trước khi chỉnh trọng số.
4. **G6** (cùng INV-9, INV-10): vận như tác động lên nguyên cục, sau khi hai nhánh trên đã nhập.
5. **G10** (cùng INV-13): lõi diễn đạt, bước phản biện, kiểm thử phản chứng cấu hình, dựng trên bản phân tích đã kiểm.
6. **G7 + G8**: truy vết, bảng trước/sau, kiểm định trên bộ lá đa dạng. Toàn bộ bất biến phải xanh.

Ước lượng:

| Phần | Cỡ việc |
|---|---|
| G-INV, G0, G1 | vừa |
| G9 | lớn, lõi mới |
| G2–G3 | vừa đến lớn |
| G4–G5 | lớn |
| G6 | vừa |
| G10 | lớn |
| G7–G8 | nhỏ đến vừa |

Đây là một đợt nhiều phiên làm việc, không phải một lần sửa.

---

## 6. Trạng thái

### Nhánh 1: G-INV (một phần), G0, G1 — 2026-11-08, nhánh `feat/thien-ban-33-g0`

**Đã làm**

- **G-INV.** `src/interpret/invariants.ts`, `test/invariants.test.ts` và `tools/interpret/eval_invariants.ts` kiểm năm bất biến: INV-1 (vị trí, kể cả cách cục "chiếu về"), INV-2 (nguyên nhân trong Tổng luận), INV-4, INV-6 và INV-11. Phạm vi chạy: lá chủ dự án, lá mẫu của trang và benchmark20, kết quả 0 vi phạm. Trên 40 lá corpus cũng 0 vi phạm. Lượt đo 300 lá chạy trên code giữa chừng, nên các vi phạm nó báo đã được sửa sau đó. Fixture mới: `fixtures/owner_2002_kl_2026-11.json`.
- **G0:**
  - Dòng dẫn chương Công danh (`report.js`).
  - Cách cục:
    - nói đúng chỗ sao của cách đứng, tức "chiếu về từ cung X";
    - tìm chỗ đỡ ở cả cung mang sao;
    - gọi sao theo đúng Hóa nó mang;
    - chiếu về thì hạ một bậc;
    - xếp hạng có lý do, ngang bậc thì nói là ngang;
    - bỏ chữ "cả đời".
  - Tổng luận:
    - mỗi miền đứng chung một hạng có nền riêng;
    - sao mượn được nêu ở cung nó thật sự đứng;
    - miền mạnh nhất mà biểu đồ cung của nó thấp thì không gọi là "chỗ dựa đứng đầu";
    - trace mang `cause`.
  - Câu "Thân cư Quan Lộc" nói đủ điều kiện gặp Hóa Kỵ.
  - Câu chứng và câu giảm nhẹ không còn chép điều kiện sách khi điều kiện đó không đúng như chữ trên lá (`narrative.ts condGround`).
- **G1:**
  - `engine/data/kg/claim_severity.json` gồm 108 luật đã duyệt tay, do `tools/interpret/build_claim_severity.py` sinh ra.
  - `prose/severity.ts`:
    - câu nặng rời đoạn chính;
    - Đọc sâu nhận một dòng trung tính, chỉ nêu những sao có thật trên lá, kèm trang và lời "chưa được kiểm chứng bằng thực nghiệm";
    - câu mốc tuổi được nói là "mốc chung của lời cổ".
  - Sổ phán quyết không để câu nặng đứng một mình làm nền cho kết luận.
  - `tools/interpret/audit_conditions.py` kiểm 108 luật nặng: 3 cảnh báo, cả 3 đều là báo nhầm.
- **G6.1 (một phần).** Xếp hạng "chặng thuận nhất / thấp nhất" chỉ xét các đại hạn bắt đầu trước 80 tuổi, ở Tổng luận và ở dòng đại hạn của từng cung. Câu "nổi lên ở các chặng" đã bỏ.

**Đính chính.** Mục 1, dòng 8b: xem lại ở bảng trên.

**Chưa làm**
- INV-3, 5, 7–10, 12, 13.
- Kiểm nguyên nhân ở `luan.ts` / `luan_deep.ts`. INV-2 hiện chỉ kiểm Tổng luận.
- Phép thử đổi hạng và ngưỡng chênh cho "chặng nhất" (G6.1).
- G2–G10.

### Lớp biên tập LLM, bản thử — 2026-11-08

Theo quyết định Q5: thử, chỉ vài chỗ nhỏ, tiết kiệm token.

**Mã nguồn** nằm ở `src/interpret/refine/`:
- `refine.ts`:
  - `polishScore` / `selectParagraphs` chọn tất định tối đa 6 đoạn đọc máy móc nhất, chỉ ở phần đọc chính, mỗi đoạn có từ 3 đến 8 câu;
  - một lời gọi cho cả báo cáo, dùng `claude-opus-5-5` ở effort `low`;
  - lời dặn khoảng 150 từ, đầu vào và đầu ra dạng dòng (`#c.p`, rồi các dòng `0,1| câu`), giới hạn đầu ra 6.000 token.
- `verify.ts`: bộ kiểm tất định. Đoạn nào trượt thì giữ bản cũ.
- `preview.ts`: `/api/admin/refine-preview`, chỉ dành cho admin, không cache, không tới người đọc.

**Số đo trên lá của chủ dự án:** máy chọn 2 đoạn, đầu vào khoảng 1.900 ký tự.

**Chưa làm:** chưa chạy với mô hình thật (máy làm việc không có khóa API); chưa đưa lớp này vào báo cáo của người đọc.

### G9 bản 1 (Tử Vi) — 2026-11-08

**Đã làm**

- `src/interpret/reason/configuration.ts`: đơn vị luận là **cấu hình** của một cung. Gồm:
  - sao chủ (`nen`), kể cả sao mượn khi cung vô chính diệu;
  - các thành viên có vai: `bien_tinh` (Tứ Hóa trên thành viên), `tro_luc` (cát tinh, chính tinh sáng ở tam phương), `tru` (sát tinh, chính tinh hãm, Hóa Kỵ, và sát tinh mà sách nói chế một thành viên), `pha` (cách đã đối trang bị phá);
  - quan hệ: mượn, Hóa, chế hóa (`che_hoa.json`).

  Các vai tác động theo thứ tự cố định (sao chủ, biến tính, trợ lực, trừ, Tuần/Triệt, phá). Mỗi bước có một dòng vết. Không có phép đếm sao.

  Mỗi cấu hình trả lời 6 câu: sao chủ mang tính chất gì (`star_nature`, có trang), mượn sức từ đâu, yếu tố nào đổi tính chất, trợ lực ở mức nào, yếu tố nào làm giảm và có phá cả tổ hợp không, chặng nào kích hoạt.
- `src/interpret/reason/analysis.ts`: bản phân tích có cấu trúc cho từng miền. Nó nối phán quyết của sổ phán quyết với cấu hình của cung chính, gồm chứng cứ thuận và nghịch, tương tác, cứu giải, điều chưa giải (với miền "chưa phân xử" thì nêu đại hạn có thể làm nghiêng), độ chắc, mức nặng, cấp độ và `evidence_ids`.
  - **Trần cấp độ:** một miền chỉ đạt cấp 5 khi có câu sách ở ít nhất hai cung trong bộ Mệnh, Tài, Quan, Di.
  - **API:** `/api/interpret` với `chapter: 'all'` và `analysis: true` trả bản phân tích. Không hỏi thì không trả, để báo cáo thường không nặng thêm.
- **INV-12** trong `invariants.ts`: miền được Tổng luận xếp đầu hay cuối phải có chứng cứ từ cấp 3 trở lên.
- **Số đo:**
  - Trên lá chủ dự án cộng benchmark20: 126/126 kết luận miền có cấu hình chi phối, 0 vi phạm INV-12.
  - Quan Lộc của lá chủ dự án gồm: Cơ Âm vượng mượn từ Phu Thê; Thái Dương hóa Quyền và Văn Khúc hóa Khoa biến tính; Cự Môn hóa Lộc biến tính một phần tư bậc vì Cự Môn hãm; Tả Phụ, Thiên Việt, Thiên Khôi trợ lực; Văn Xương hóa Kỵ, Đà La, Tiểu Hao, Kình Dương ("Khôi Việt sợ Kình Đà", KL tr.145) trừ. Kết quả: có điều kiện, sức "rõ".

**Chưa làm**
- Đồ thị Bát Tự (G9.1 phía Bát Tự).
- `configurations.json`: mẫu cấu hình theo cách cục và bố cục KL. Bản 1 dựng cấu hình theo cung, chưa theo mẫu có tên.
- Cấu hình cấp 5 nối Mệnh, Tài, Quan thành một đơn vị riêng.
- Lời luận chưa đọc bản phân tích. Việc đó thuộc G4 (giải xung đột chạy trên cấu hình) và G10 (diễn đạt).

### G4 bản 1 — 2026-11-08

**Đã làm**

- **Cân theo cấu hình** (`ledger.ts configWeigh`). Khi hai mặt đối đầu, không có câu sách phân xử và thang cân cũ không thấy bên nào nặng hơn rõ, cấu hình của cung chính quyết định chiều nghiêng. Ngưỡng ở `domains.json`: sức ≥ 2,5 nghiêng thuận, ≤ 1,5 nghiêng khó. Cách điểm giữa dưới 0,75 bậc thì nói là "chỉ nghiêng nhẹ". Lý do nêu tên yếu tố dẫn và yếu tố làm giảm chính.
- **G4.2.** Lời cân mà lý do duy nhất là "nhiều chỗ đứng hơn" không còn được tính.
- **G4.3.** Miền vẫn ngang thì câu kết nêu đại hạn gần nhất (từ chặng hiện tại, trước 80 tuổi) chạm vào sao của tổ hợp. Miền nghiêng nhờ cấu hình thì có thêm câu "đó mới là chiều nghiêng chung của tổ hợp…" kèm chặng sẽ thử nó.
- **Nền của mỗi mặt.** Mặt khó không còn được gán nguyên nhân cho Hóa tốt hay cát tinh, mặt thuận không còn được gán cho sát tinh hay Hóa Kỵ. Ví dụ: "trở ngại trong công việc đến từ Kình Dương ở cung Mệnh", thay cho "…Hóa Lộc, Hóa Khoa và Hóa Quyền".
- **Số đo trên 300 lá** (`tools/interpret/eval_verdicts.ts`): "chưa phân xử" giảm từ 21,5% xuống 10,3% (đích ≤ 10%). Trường hợp cân chỉ nhờ đếm chỗ đứng giảm từ 101 xuống 0.
- **G4.4.** Đã có khung: `tools/interpret/make_gold_cases.ts` sinh 30 tình huống A/B/C và 15 tình huống kiểm định độc lập (các lá khác) ở `fixtures/gold/`, cùng phiếu chấm `docs/gold/PHIEU-CHAM.md`.

**Chưa làm**
- Chủ dự án chấm phiếu, rồi mới chỉnh trọng số và ngưỡng theo phiếu. Tập kiểm định chấm trước, không mở trong lúc chỉnh.
- Câu kết đủ bốn phần cho mọi miền (G4.5). Mới có yếu tố dẫn, yếu tố làm giảm và chặng thử; "điều chưa biết" chỉ có trong bản phân tích, chưa vào lời luận.

### Bát Tự: G9.1, G2.1–G2.4, G3.1 bản 1 — 2026-11-08

**Đã làm**

- **G9.1.** `reason/bazi_graph.ts` dựng đồ thị lá số:
  - nút: can và tàng can, mỗi nút có vai trong bản đồ hỷ kỵ;
  - cạnh: sinh, khắc giữa các chữ đứng sát, cùng trụ, thông căn, hợp, xung, hình, hại;
  - mạch Quan → Ấn → thân và Tài → Quan có cấp;
  - bản đồ năm hành.

  API trả đồ thị trong `analysis.bazi` khi có `analysis: true`.
- **G2.3, bản đồ hỷ kỵ.** Can điều hậu thuộc nhóm dụng hay hỷ của phép cân bằng thì tính là cùng chiều. Trên lá chủ dự án, Giáp (Ấn, hỷ thần) cùng chiều, nên câu "khác với dụng thần Tỉ Kiếp" đã bỏ. Chỗ vênh (Canh) được phân xử bằng các điều kiện có tên theo Q1: can phụ, vượng nhược đã rõ, Tài là nhóm đang nhiều nhất. Kết quả: ở Canh theo phép cân bằng, khí hậu là điều kiện phụ. Khi không đủ điều kiện, câu nêu cả hai kết quả có điều kiện.
- **G2.1, G2.2.** Đoạn chính nói rõ sức được cân theo độ, có lệnh tháng và tàng can, không đếm chữ. Câu "có gốc ở chi năm Tỵ (Bính) và chi giờ Dần (Bính)… không vào cách tòng". Chữ "sức của tám chữ" đổi thành "tổng số độ".
- **G3.1.** Câu "chưa nối được" đổi thành "chưa tính là chảy vào nhật chủ" (đúng điều kiện ZZ tr.50). Thêm câu "chi giờ Dần có tàng Giáp (Chính Ấn) ngay dưới Nhâm (Chính Quan): đường Quan sinh Ấn, Ấn sinh thân có thật, chỉ ở mức vừa".
- **G2.4.** Vận nặng mà can vận khắc chính chữ đang khắc dụng thần (Mậu khắc Nhâm) thì đoạn chính nói ra, và phán quyết giảm một bậc độ chắc. Phán quyết vẫn là nặng.

**G3.2, G3.3 (2026-11-08)**

- `engine/data/bazi_deep/opposed.json` liệt kê các cặp lời về thế chung đi ngược nhau. Lời "thành" của bảng thành bại (TVH tr.367–369, điều kiện "có Ấn / Tỉ Kiếp hộ thân, sinh thân") đối với lời "hung" (TVH tr.171, cùng nhóm ấy "nhẹ" hay "không có").
- Khi cả hai cùng bắn, `bazi_kin.ts` nói chúng chỉ khác nhau ở sức đỡ thân, đo sức ấy trên lá (phần độ, không tính chính nhật chủ, và có lộ lên can hay không), rồi nói lời nào đứng với nguyên cục và lời kia thành khi nào.
- Lá chủ dự án: Ấn và Tỉ Kiếp chừng 18% và không lộ lên can, nên lời hung đứng với nguyên cục, còn lời tốt thành khi vận mang Ấn, Tỉ Kiếp tới.
- Test trên 61 lá: mọi cặp cùng bắn đều có câu phán quyết.

**Chưa làm**
- Phép thử nhiễu cho độ chắc vượng nhược (G2.2).
- Câu chữ Bát Tự còn lặp "Bên cạnh đó… Ngoài ra…" (G10).
