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

<!-- METRICS -->
