# Tử Vi đọc sâu — audit độ sâu, sửa đúng–sai, tầng "Đọc sâu" (2026-10-22/23)

Phạm vi: làm luận giải Tử Vi sâu hơn về **phân tích**, không về số chữ — trước hết Quan Lộc, Tài Bạch, Phu Thê. Trước khi đào sâu, sửa
chín lỗi đúng–sai mà chủ dự án chỉ ra trên lá 09/01/2002 04:30 nam (§1). Không có chữ của mô hình ngôn ngữ lúc chạy; không luật hay
trang sách bịa; không câu phổ thông; câu minh họa theo chính sách mới (§4).

Công cụ đo: `tools/interpret/eval_deep.ts` (corpus 1.000 lá, `--gates` cho sáu lá cổng), `tools/interpret/eval_synthesis.ts`,
`tools/interpret/eval_distinct.ts`. "Trước" = `8a47abc` (main lúc bắt đầu); "sau" = nhánh này.

## §1. Correctness — chín lỗi của đợt rà soát chủ dự án (sửa ở gốc, mỗi lỗi có test hồi quy)

| # | Lỗi | Sửa ở đâu | Test |
|---|---|---|---|
| 1 | Sao **mượn** viết như **tọa thủ**: "Với Tham Lang hãm ở cung Nô Bộc" (Nô Bộc Mão VCD, Tham Lang ở Huynh Đệ Dậu) | `evidence.ts` đã đánh dấu `borrowed`; nay mọi chỗ viết yếu tố ấy đi qua một lối: khung `confront.major_ham_borrowed`, `confront_alone_borrowed` ("Mượn Tham Lang hãm từ cung Huynh Đệ…"), `elName` thêm "(mượn từ cung đối)" cho sao hãm / sao mang Kỵ được mượn; tầng đọc sâu không kể bản chất của sao mượn như sao của cung. Luật `own_major_stars` không bắn trên sao mượn (facts VCD để trống — đã kiểm) | `positions_text.test.ts`: mọi câu "<sao> … ở cung X" / "<sao> tọa X" trên benchmark20, 3 lá tham chiếu và 150 lá corpus phải khớp facts (ngồi thật, hoặc ghi rõ mượn / chiếu / hội / giáp); đã chạy 400 lá: 0 câu sai |
| 2 | Yếu tố **giảm nhẹ** biến thành kết luận **thuận**: Tật Ách "Triệt giảm cường độ tật ách" → "sức khỏe thuận, với điều kiện đi kèm"; vận hạn nhắc lại | `ledger.ts`: một luận điểm chỉ là câu sách làm nhẹ một giới hạn (reducer) không còn là "phía thuận" (`mitig`); chỉ có giới hạn + yếu tố giảm nhẹ → verdict mới `giam_nhe` ("có yếu tố giảm nhẹ"). Sức khỏe (`domains.json` `"verdict": false`) không bao giờ có verdict tốt/xấu (`khong_ket_luan`): chỉ nêu lời sách, hai phía thì "… được nêu ra; ở đây chỉ ghi lại hai điều ấy, không kết luận tốt hay xấu". Vận hạn bỏ qua miền không verdict. Thẻ khái niệm sức khỏe bỏ soft/minh họa/giá trị/lời khuyên | `correctness.test.ts` (2) |
| 3 | **Nhân quả đảo ngược**: "Thiên Tướng ở Phụ Mẫu chiếu về Tật Ách lại cho thấy nguy cơ tai ách, bạo bệnh" (TL tr.127: cha mẹ hiền **không đủ sức chống** Sát Phá Tham, Cự Nhật ở Tật) | Luật `TV_TL_TAT_ACH_NANG` thiếu nửa điều kiện của trang (sao xấu ở Tật Ách) → bổ sung; liên kết khái niệm có `protectors: ["Phụ Mẫu"]` (`kg/lift.ts`): sao Phụ Mẫu là phần che chở không đủ, không bao giờ là chỗ đứng của nhận định. Rà các luật "không đủ / không chế được": chỉ có luật này | `correctness.test.ts` (3) |
| 4 | **Sai chủ thể**: Tử Tức dẫn "cha mẹ khá giả, con cái hòa thuận" (Phụ Mẫu) làm xác nhận cho con cái | `plan.ts`: cung của người khác (Phu Thê, Tử Tức, Huynh Đệ, Phụ Mẫu, Nô Bộc) không xác nhận cũng không phản bác cung nào khác; chỉ hai cung của chính đương số trong tam phương mới xác nhận nhau | `correctness.test.ts` (4) |
| 5 | **Thời điểm** dùng để "hòa giải" hai mặt chất lượng: "điều nối hai mặt ấy là công danh đến muộn", Phu Thê "… hôn nhân xảy ra trong hoàn cảnh đặc biệt" | `ledger.ts`: thời điểm là một chiều riêng, không bao giờ là điều kiện của verdict hay mối nối hai phía. Hai phía mà không có câu sách phân xử → `chua_phan_xu` (nêu cả hai, mỗi phía với sao nó đứng trên, "chưa phân xử được"); hai phía thuộc hai phương diện khác nhau (facet khác, không đối nghịch trong KG) → `hai_mat` (khung "coexist" lấy từ bản sửa của chủ dự án). Specificity / tier không còn tự phân xử. Chỉ một quan hệ sách giữa hai phía mới cho `co_dieu_kien` | `correctness.test.ts` (5); 0 liên kết thời điểm trên 1.000 lá |
| 6 | Nhãn truy vết mâu thuẫn (`ui.js`: "Bị giới hạn bởi quy tắc đối lập" + "Không có quy tắc đối lập nào khớp") | `reasoning/conflict.py`: trạng thái từng nhận định tách ba loại — `adverse` (nhận định bất lợi tự thân), `limited` + `limited_by` (bị luật nào giới hạn, ghi tên), `unresolved`; `engine.py` thêm trường `limited_by`; `ui.js` và `nlg/lexicon.py` nói đúng từng loại | `engine/tests/test_audit_correctness.py::test_statuses_adverse_limited_unresolved` |
| 7 | Điều kiện luật **rộng hơn trang** | `tools/interpret/audit_widening.py` (quét mọi luật verified): 6 luật "nhập miếu" nhận cả vượng/đắc → thu về miếu (`TV_TH_AUX_MENH_HL_LUONG`, `TV_TH_CACH_MENH_VU_VAN_VO`, `TV_TT_PAL_TAI_BACH_LINH_TINH_MIEU_P`, `…PHU_MAU_VAN_KHUC_MIEU_P`, `…NO_BOC_LINH_TINH_MIEU_P`, `…DIEN_TRACH_HOA_TINH_MIEU_P`); 1 luật "đơn thủ" không loại chính tinh thứ hai → draft (`TV_TT_PAL_NO_BOC_VAN_XUONG_MIEU_P`); `TV_KL_STAR_MENH_TA_HUU_TU_MO` (KL tr.63 "Mộ phùng Tả Hữu … Mệnh ở tứ mộ có Tả Hữu": "phùng/có" không nói tọa thủ hay hội, điều kiện cũ nhận Tả Hữu trong tam phương) → draft có lý do. Hồ sơ: `engine/data/kg/rule_review_widening.json` | `test_audit_correctness.py::test_no_widened_rule_left` |
| 8 | **Trộn bảng độ sáng**: luật TH/TT xét bằng bảng KL | Mỗi luật của Thực Hành / Toàn Thư / Khảo Luận đọc độ sáng trong **bảng của chính sách đó**: lá `palace.dignity@<school>.<sao>` (`tools/interpret/dignity_by_source.py`, 224 luật), hai bộ máy cùng tra `dignity_kb.json` theo chi của cung (`engine/tvbt/knowledge/dsl.py _own_book_dignity`, `src/interpret/dsl.ts ownBookDignity`); sách không có ô → lùi về bảng lá số đang dùng. Parity TS↔Python giữ nguyên (72/72) | `test_audit_correctness.py::test_own_book_dignity`; **500 lượt bắn thay đổi trên 405/1.000 lá** (trên 74.303 lượt) |
| 9 | Câu **diễn giải thêm / lời khuyên** vượt quá câu sách | Mọi dòng hành vi của thẻ ("Người phối ngẫu thường lật đi lật lại…") nay là `minh_hoa`, gắn đúng một câu sách (`tied`), `checked.ts` bỏ khi câu sách bị bỏ; lời khuyên (`advice:`, câu TRANSFORM) có basis mới `loi_khuyen` — "Lời khuyên chung" trong ô căn cứ, khung "Gợi ý … vì {np}" (của chủ dự án) nêu luôn nhận định nó trả lời. Dòng minh họa của tôi "quen tự lo liệu chuyện tiền từ sớm" có thời điểm → sửa | `correctness.test.ts` (9), `depth.test.ts` |

Phân bố verdict trên 1.000 lá (trước → sau):

| Miền | Trước | Sau |
|---|---|---|
| công danh | có điều kiện(+) 783, hai chiều 102, trở ngại 40, thuận 39 | **chưa phân xử 353**, **hai mặt 435**, có điều kiện(+) 118, thuận 89 |
| kiếm tiền | có điều kiện(+) 617, hai chiều 208 | **chưa phân xử 726**, có điều kiện(+) 86, hai mặt 75, thuận 76 |
| giữ tiền | trở ngại 342, chưa đủ 596 | trở ngại 511, chưa đủ 394, chưa phân xử 45 |
| tích lũy | có điều kiện(+) 295, trở ngại 257, hai chiều 132 | **chưa phân xử 467**, có điều kiện(+) 170, trở ngại 126 |
| hôn nhân | có điều kiện(+) 513, có điều kiện(−) 261 | **chưa phân xử 460**, trở ngại 290, có điều kiện(+) 102 |
| sức khỏe | có điều kiện(+) 585, thuận 89, trở ngại 86 | **không kết luận 1.000** |
| Liên kết thời điểm dùng để nối hai mặt | 1.335 | **0** |
| Yếu tố giảm nhẹ thành phía thuận | 119 | **0** |

Phần lớn "có điều kiện" trước đây là hai mặt cùng facet mà không có câu sách nào phân xử; nay báo cáo nói thẳng như vậy.

Gộp từ bản sửa chưa commit của phiên "Thiên Bàn luận giải đánh giá" (đọc, không sửa checkout chính): bước chuỗi bằng chứng một dòng cho mỗi
luật, phân biệt hai phía cùng / khác phương diện (`facet_label`, khung `coexist`), lời khuyên "Gợi ý … vì {np}" kèm ghi chú, cờ `soft` để
không ghép hai điểm mạnh khi một bên đã bị làm mềm, sửa câu soft của thẻ. Không lấy: dùng thời điểm để "gỡ" khi giới hạn không nằm ở cung
lõi (trái mục 5), câu "bên nào trội sẽ lộ rõ ở chặng … tuổi" (lời hệ thống không có trang).

## §2. Audit độ sâu (corpus 1.000 lá, trước)

Đơn vị phân tích của một chương = luận điểm khác nhau (khái niệm do câu sách nói) + câu cơ chế (vì sao) + câu phản bác/giới hạn + câu
tương tác giữa cung/yếu tố + câu kết luận có điều kiện. Số chữ / đơn vị cho thấy phần độn.

Đo bằng `node tools/interpret/eval_deep.ts --n 1000` (định nghĩa từng chỉ số ở đầu tệp). Trung bình mỗi chương:

| Chương | chữ | đơn vị | luận điểm | cơ chế | phản bác | tương tác | có điều kiện | chữ/đơn vị | chương 0 đơn vị | lặp (trigram, khác cấu hình) |
|---|---|---|---|---|---|---|---|---|---|---|
| Quan Lộc | 166 | **4,4** | 2,1 | 0 | 1,4 | 0,7 | 0,2 | **43,8** | 65 | 0,04 |
| Tài Bạch | 202 | 7,8 | 1,8 | 0 | 1,2 | 1,6 | 3,2 | 28,6 | 7 | 0,06 |
| Phu Thê | 152 | 5,0 | 2,2 | 0 | 0,8 | 0,4 | 1,6 | 33,3 | 23 | 0,04 |
| Điền Trạch | 130 | 3,6 | 1,9 | 0 | 1,6 | 0,1 | 0 | 39,3 | 27 | 0,03 |
| Mệnh (đối chứng) | 465 | 15,3 | 7,2 | 0 | 1,8 | 4,6 | 1,6 | 31,5 | 0 | 0,05 |

Những gì có trong dữ kiện mà văn không nói (1.000 lá):

| Bỏ sót | Quan Lộc | Tài Bạch | Phu Thê | Điền Trạch |
|---|---|---|---|---|
| luật verified bắn ở cung mà không chương nào nói | 243 (170 lá) | 929 (498 lá) | 1.076 (550 lá) | 220 (131 lá) |
| Tứ Hóa gốc trong cung không được nhắc sau câu khung | 201 | 199 | 272 | 206 |
| hai chính tinh đồng cung không được đọc cùng nhau | 96 | 56 | 54 | 137 |
| Thân cư ở cung mà không nói sau câu khung | 140 | 162 | 157 | — |
| kết luận lĩnh vực mà chương không nói luận điểm nào nó gom | 226 | 1.793 | 72 | — |

Nhận xét:
- **Không có câu "vì sao"** ở bất kỳ chương nào: mọi luận điểm là lời sách + chỗ đứng, không có bản chất sao giải thích nó, dù sách (KL pp.84–199) nói rõ từng sao tượng trưng cho gì, cần cung nào.
- **Quan Lộc mỏng nhất**: 4,4 đơn vị, 43,8 chữ/đơn vị (khung + kết luận lặp lại chiếm phần lớn), 65 lá không có đơn vị nào. Trên lá 2002: **1 đơn vị** (98 chữ).
- **Tài Bạch kết luận mà không lý giải**: 1.793 câu kết luận gom luận điểm của Mệnh/Quan Lộc chưa từng được nói ở chương Tài Bạch. Luận điểm mạnh nhất của Tài Bạch 2002 (Thái Dương miếu: "no đủ, sung túc", TT pp.80-81) không được nói ở đâu cả.
- **Tứ Hóa** đứng trong cung bị bỏ qua sau câu khung ở ~20 % chương (Hóa Quyền ở Tài Bạch 2002: KL p.197 nói rõ "được người nể mình vì tiền").
- **Liên kết Mệnh–Thân–Quan–Tài–Phu–Phúc** gần như không có: Thân cư không được giải nghĩa (KL p.215 có câu cho từng cung); quan hệ Phúc/Quan "chế tài" Tài (KL p.216) không được dùng; Kỵ ở cung xung chiếu (Văn Xương hóa Kỵ ở Phu Thê → Quan Lộc 2002) không được nêu là nguồn của "công danh đến muộn".
- **Cấu hình thường và hiếm**: chương của cấu hình hiếm (< 1 % corpus) có nhiều đơn vị hơn (Tài Bạch 10,7 so với 7,5) — phần thường gặp đọc mỏng hơn, không phải phần hiếm.
- **Lặp giữa lá khác nhau** thấp (0,03–0,06) vì văn ngắn; đây là chỉ số phải giữ khi đào sâu.

Thiếu tri thức (khoảng trống), trước khi bổ sung: KL "X ở các cung" chỉ được đưa vào luật đến hết Thiên Cơ / đầu Thái Dương (pp.63–83); pp.84–155 (12 chính tinh còn lại và phụ tinh, mỗi sao có mục Quan / Tài / Phu thê / Điền) chưa có luật nào.

## §3. Bổ sung tri thức có trang

1. **`pack_khao_luan_sao_cung.json`** (`tools/build_kl_sao_cung_pack.py`): 81 luật KL pp.84–142, mục "X ở các cung" cho Quan, Tài, Phu thê/Phối, Điền của Thái Dương → Phá Quân và Xương Khúc, Không Kiếp, Song Hao, Lộc Tồn. Mỗi luật có câu trích nguyên văn trên trang (`engine/data/quotes_khao_luan_sao_cung.json`), kiểm bằng `engine/tests/test_kl_sao_cung.py` (đọc lại PDF) và đã đọc trên ảnh trang (thứ tự dòng, đúng tiêu đề). Bỏ có chủ ý: dòng Mệnh, vận, bệnh tật, tù tội, trộm, tiếng xấu về tình dục, tướng mạo; với Phu thê mọi dòng thời điểm/sự kiện; cặp sao không thể đồng cung (Tham–Vũ ở Thìn/Tuất, Tham–Liêm ở Tí/Ngọ, Đồng–Lương ở Tí/Mão — sách in như vậy); dòng quá mơ hồ ("phú quý bất thường").
2. **`engine/data/kg/star_nature.json`**: 58 câu bản chất sao (KL pp.85–197: "Thái dương … tượng trưng cho uy quyền, quan lộc, danh vọng nên rất cần ở cung Quan", "Vũ khúc cần cho cung Tài Lộc vì chủ tiền bạc", "Tả Hữu làm phụ tá … đi với phúc tinh thì … sáng hơn, … ác tinh … thêm xấu", Tứ Hóa pp.195–197, "Thất Sát là thầy Kình Đà", "Phá quân giải trừ được ác tính của Không Kiếp"…) và 9 câu quan hệ cung (KL pp.215–219: Thân cư từng cung, Phúc/Quan chế tài Tài, nhà đất là dạng bền của của cải). Mỗi câu có trích dẫn kiểm bằng `engine/tests/test_star_nature.py`, cờ `use` (lĩnh vực), `pol` (mặt), `explains` (luận điểm nó được phép giải thích), `tames` (sao nó chế).
3. Ba lượt đọc trang (KL pp.84–103, 101–120, 121–155 + 186–199 + 195–197 + 214–220) cho 739 mục; chỉ những mục điều kiện rõ được dùng. Các trang text layer lệch dòng so với ảnh: p.135, 136, 140, 151, 152, 155, 188, 189 (đã theo ảnh).

## §4. Tầng "Đọc sâu" (Quan Lộc, Tài Bạch, Phu Thê, Điền Trạch)

`src/interpret/reason/depth.ts` (dữ liệu, không câu chữ) + `src/interpret/prose/luan_deep.ts` (câu) — gọi trong `luanChapter` sau phần đọc ngắn; trên trang `report.js` gập dưới mục **Đọc sâu**, mỗi tiểu mục có tiêu đề. Mỗi đoạn phải có một mốc riêng của lá số (một luận điểm, một yếu tố kích hoạt, một liên kết, một tương tác); một đoạn chỉ nhắc lại thì bị bỏ.

| Loại câu | Nội dung | Basis |
|---|---|---|
| luận điểm | luật verified của cung chưa được nói ở đâu trong báo cáo, với chỗ đứng (mọi sao/Hóa nó cần, kèm cung) | sách (luật + trang) |
| cơ chế | bản chất sao mà luận điểm đứng trên, chỉ khi `explains` khớp luận điểm và cùng mặt (một giới hạn không bao giờ là "lý do" của một điểm mạnh); một luận điểm đã nói thì nhắc ngắn + lý do trong **một** câu | sách (KL trang) |
| kích hoạt | yếu tố của luận điểm nằm ngoài cung (Văn Xương hóa Kỵ ở Phu Thê xung chiếu Quan Lộc) | tính toán |
| tương tác | sao trong cung/tam phương chế sao xấu trong cung, theo câu sách (Thiên Phủ chế Kình Đà Hỏa Linh; Phá Quân giải Không Kiếp) | sách |
| liên kết | Thân cư (KL p.215), Tứ Hóa của Mệnh–Tài–Quan + nghĩa của từng Hóa (KL p.195), sao sách nối hai cung (Thái Dương: "hễ có danh thì dễ kiếm tiền", KL p.85), Phúc/Quan chế tài Tài (KL p.216) kèm phía lá số, Kỵ ở cung xung chiếu | sách / tính toán |
| có điều kiện | verdict của ledger với phía đỡ/phía vướng trong cung; Quan Lộc đặt công danh cạnh kiếm tiền | hệ thống (ledger) |
| minh họa | một câu cho đúng một luận điểm sách vừa nói (`minh_hoa.json`, 29 khái niệm), không sự kiện, không thời điểm, không sức khỏe | minh_hoa |

Quan Lộc: thiên hướng / thế mạnh / người nâng đỡ / quyền hành / nhịp / chỗ vướng / công danh→tiền bạc. Tài Bạch: tiền đến từ đâu / tích lũy / độ bền / cách tiêu / chỗ hao / Tài giữa các cung. Phu Thê: cách gắn với nhau / độ hợp / cách trò chuyện / nguồn căng thẳng / điều giữ êm / mặt thuận đứng được khi nào — **không** luận điểm nào có chữ sự kiện hay thời điểm (lọc theo lời luật: lần, dang dở, xa cách, sớm, muộn, cưới, góa…). Điền Trạch: nhà đất / điều làm hao / Điền và Tài.

Chính sách minh họa (`prose/checked.ts`): câu `minh_hoa` chỉ ở lại khi câu nó gắn (`tied` — Tử Vi; `attach` — Bát Tự) còn trong cùng đoạn và là câu sách có luật; dòng hành vi của thẻ khái niệm nay cũng là `minh_hoa` (trước đây ghi nhầm là "sách"). Ô căn cứ ghi "Minh họa" và số câu.

## §5. Số đo sau (1.000 lá; "trước → sau")

| Chương | chữ | trong đó Đọc sâu | đơn vị | cơ chế | tương tác | có điều kiện | chữ/đơn vị | có cơ chế | liên kết cung khác | chương 0 đơn vị | lặp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Quan Lộc | 166 → 322 | 145 | **4,4 → 10,2** | 0 → 2,6 | 0,7 → 2,2 | 0,2 → 0,9 | **43,8 → 34,1** | 0 → 96 % | 2,1 → 2,6 | 65 → 1 | 0,04 → 0,06 |
| Tài Bạch | 202 → 410 | 174 | **7,8 → 13,2** | 0 → 1,9 | 1,6 → 2,2 | 3,2 → 5,0 | 28,6 → 32,1 | 0 → 91 % | 2,3 → 3,8 | 7 → 0 | 0,06 → 0,11 |
| Phu Thê | 152 → 235 | 74 | **5,0 → 6,8** | 0 → 1,6 | 0,4 → 0,5 | 1,6 → 1,2 | 33,3 → 36,8 | 0 → 90 % | 0,3 → 0,5 | 23 → 3 | 0,04 → 0,05 |
| Điền Trạch | 130 → 218 | 86 | **3,6 → 6,7** | 0 → 0,9 | 0,1 → 1,5 | 0 → 0 | 39,3 → 35,4 | 0 → 62 % | 0,1 → 1,0 | 27 → 15 | 0,03 → 0,07 |
| Mệnh | 465 → 483 | 0 | 15,3 → 14,5 | 0 | 4,6 → 4,0 | 1,6 → 1,3 | 31,5 → 34,5 | — | 2,8 → 2,8 | 0 | 0,05 → 0,05 |

| Bỏ sót (1.000 lá), trước → sau | Quan Lộc | Tài Bạch | Phu Thê | Điền Trạch |
|---|---|---|---|---|
| luật verified không ai nói | 243 → **8** | 929 → **256** | 1.076 → **525** | 220 → **13** |
| Tứ Hóa trong cung không nhắc | 201 → **0** | 199 → **1** | 272 → **74** | 206 → 127 |
| cặp chính tinh không đọc cùng | 96 → 29 | 56 → 30 | 54 → 43 | 137 → 99 |
| Thân cư không giải nghĩa | 140 → **0** | 162 → **0** | 157 → **0** | — |
| kết luận không có luận điểm trong chương | 226 → 235 | 1.793 → 1.791 | 72 → 31 | — |

Cấu hình thường / hiếm (đơn vị): Quan Lộc 4,2 / 4,4 → 9,5 / 11,1; Tài Bạch 7,5 / 10,7 → 12,6 / 15,5; Phu Thê 4,8 / 5,1 → 6,7 / 8,0.

Cổng giữ nguyên: một sao kết luận lớn 0, yếu tố hạn chế không đối diện 0, verdict khác nhau trong một báo cáo 0, chương có lỗi chặn 0 (`eval_synthesis.ts`, xem §6); Barnum / strip Mệnh benchmark20 40,1 % / 0,064 (cổng 40,55 % / 0,0655); câu trung bình 21,0 chữ, 4,6 % quá 35 chữ (cổng 23 / 5 %).

Đánh giá thẳng:
- Quan Lộc và Điền Trạch sâu hơn mà **gọn hơn** (chữ/đơn vị giảm). Tài Bạch và Phu Thê sâu hơn nhưng chữ/đơn vị **tăng** (28,6 → 32,1; 33,3 → 36,8): câu liên kết sách (chế tài) và câu nhắc lại + lý do dài hơn một luận điểm đơn. Đã cắt: nhắc lại và lý do gộp một câu; Tài Bạch không nhắc lại kết luận ba phần; câu quan hệ sách viết chung với phía lá số.
- **Lặp** tăng ở Tài Bạch (0,06 → 0,11) và Điền Trạch (0,03 → 0,07): câu bản chất sao giống nhau giữa hai lá có cùng sao (đúng nghĩa), và khung liên kết cố định. Vẫn dưới mức của chương Mệnh cũ trong eval_prose, nhưng là điều phải theo dõi.
- "Kết luận không có luận điểm trong chương" của Tài Bạch không giảm: kết luận phần kiếm tiền gom luận điểm của Mệnh/Quan Lộc theo `domains.json`; câu Đọc sâu không nhắc lại các luận điểm ấy (đã nói ở chương Mệnh).

Lá cổng (`node tools/interpret/eval_deep.ts --gates`), đơn vị trước → sau (chữ/đơn vị):

| Lá | Quan Lộc | Tài Bạch | Phu Thê |
|---|---|---|---|
| 2002 (ref_2002_01_09_kl) | 1 → 9 (98 → 35,7) | 9 → 13 (21,6 → 28,5) | 10 → 12 (29,7 → 32,9) |
| 1911 | 5 → 10 (37,2 → 34,9) | 8 → 10 (30,8 → 37,4) | 2 → 5 (57,5 → 38,0) |
| 1971 | 6 → 11 (26,8 → 29,4) | 6 → 16 (28,7 → 28,9) | 0 → 4 (– → 33,0) |
| Tuần Triệt ở Quan Lộc | 9 → 16 (37,2 → 31,4) | 15 → 17 (19,4 → 29,0) | 3 → 4 (24,0 → 40,0) |
| Tài Bạch VCD | 5 → 6 (40,6 → 38,2) | 10 → 19 (27,1 → 29,5) | 4 → 7 (41,5 → 35,4) |
| Phu Thê VCD, nữ | 2 → 5 (60,5 → 39,4) | 9 → 13 (26,4 → 30,8) | 8 → 14 (24,3 → 29,2) |

Văn trước/sau đầy đủ của sáu lá: [docs/examples/deep-tuvi-truoc-sau.md](../examples/deep-tuvi-truoc-sau.md).

## §6. Kiểm thử

Mới: `src/interpret/test/depth.test.ts` (mọi câu Đọc sâu có bước, căn cứ trang/luật/tính toán, không phổ thông, không chữ phương pháp; minh họa gắn đúng một câu sách; Phu Thê không thời điểm/sự kiện; lá 2002 có Thái Dương là sao quan lộc hội về Quan Lộc VCD, Văn Xương hóa Kỵ ở Phu Thê đứng sau "công danh đến muộn", Tứ Hóa Mệnh–Tài–Quan, lý do tiền của Thái Dương, chế tài; mỗi câu bản chất nói một lần), `correctness.test.ts`, `positions_text.test.ts`, `engine/tests/test_audit_correctness.py`, `test_kl_sao_cung.py`, `test_star_nature.py`. Sửa theo chính sách mới (không nới cổng): golden các ví dụ, trung tâm lá mẫu Cự Môn có thể là ghế Kình Dương (TT "Kình miếu" nay bắn trên bảng TT), tỉ lệ chương Tật Ách rỗng 0,12 → 0,13 (TL p.127 lại đòi sao xấu ở Tật Ách), lật độ sáng giả trong bộ phản thực tế được đưa vào cả ba bảng.

## §7. Khoảng trống còn lại

- **Sức khỏe**: chỉ nêu lời sách; không có verdict. Các luận điểm sức khỏe cũ dựa thẻ phổ thông đã bỏ khỏi văn.
- **Tuần/Triệt** không có câu bản chất trong KL pp.186–199 → không có câu "vì sao" cho Tuần/Triệt.
- **Quan Lộc VCD**: vẫn không đọc Cơ–Âm mượn như sao của cung (KL pp.218, 222 chỉ nói phép mượn cho Mệnh/Thiên Di); thiên hướng của cung VCD chỉ nêu sao sáng hội từ tam hợp, nói rõ là hội về.
- **Thiên Di, Phúc Đức, Nô Bộc, Tử Tức, Huynh Đệ, Phụ Mẫu, Tật Ách** chưa có tầng Đọc sâu (Điền Trạch đã có). Phúc Đức và Thiên Di cần câu bản chất có thẻ `use` riêng.
- **Dòng KL bỏ qua có chủ ý** (§3) và các mục "và các sao khác" có điều kiện "hoặc" nhiều nhánh: chưa thành luật.
- **Ô trống của bảng sách**: luật đọc bảng của chính nó; khi sách đó không có ô, lùi về bảng của lá số — lượt bắn ấy chưa được gắn nhãn riêng trong ô căn cứ.
- **Trung tâm lá mẫu** (02/03/1991): nay có thể là Kình Dương thay vì Cự Môn vì TT "Kình miếu" bắn đúng bảng TT; chủ dự án nên xem lại quy ước chọn trung tâm.
