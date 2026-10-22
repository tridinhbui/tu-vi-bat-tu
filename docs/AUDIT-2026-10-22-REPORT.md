# Báo cáo bàn giao: audit + tầng tổng hợp Tử Vi – Bát Tự (2026-10-22)

Phạm vi: yêu cầu "chuyển từ khớp luật → ghép câu sang kiểm chứng → tương tác → phân xử mâu thuẫn → tổng hợp → luận giải". Cơ sở trước: `4927f34`. Sau: `main` gồm `e186628` (audit + trường phái tính toán), `2076753` (S2 Bát Tự), `c525cb7` (S1 tổng hợp Tử Vi). 137 tệp đổi, +5.406 / −588 dòng.

Tài liệu chi tiết: bảng lỗi có bằng chứng [`docs/AUDIT-2026-10-22.md`](AUDIT-2026-10-22.md) · Tử Vi [`docs/audit/S1-tuvi.md`](audit/S1-tuvi.md) · Bát Tự [`docs/audit/S2-bazi.md`](audit/S2-bazi.md) · ví dụ trước/sau [`docs/examples/s1-2002-truoc-sau.md`](examples/s1-2002-truoc-sau.md), [`s1-1911-truoc-sau.md`](examples/s1-1911-truoc-sau.md), [`bazi-S2-2002.md`](examples/bazi-S2-2002.md), [`bazi-S2-1911.md`](examples/bazi-S2-1911.md).

## 1. Tiêu chí nghiệm thu

| Tiêu chí | Kết quả |
|---|---|
| Không còn lỗi P0 đã xác minh | **PARTIAL** — mọi P0 tính toán Tử Vi và P0 luận giải đã sửa; còn BZ-8 phần ngoài miền Bắc (nhập múi giờ tay cho nơi sinh ngoài VN, giờ miền Nam thời chiến chưa rõ trong tzdb) — xem §5 |
| Không còn kết luận mâu thuẫn chưa giải thích | **PASS** (bổ sung 2026-10-22, §7) — trên 1.000 lá: cặp chương nói ngược nhau không có kết luận giải thích 4.284 → 27 → **0**; một lĩnh vực có hai kết luận khác nhau trong cùng báo cáo: **0** (Tử Vi); Bát Tự: test mâu thuẫn toàn báo cáo xanh |
| Mỗi kết luận quan trọng có chuỗi bằng chứng | **PASS** cho cấu trúc (dữ kiện → luật → tương tác → nhận định qua `PalaceEvidence` + `DomainLedger`, trace từng câu); **PASS** cho "không kết luận lớn từ một sao": 2.221 → 102 → **0** câu luận điểm dựa một luật sao phụ mà không có cung khác xác nhận hoặc lời hạ thành "chiều hướng" (§7) |
| Nội dung tổng hợp nhiều yếu tố | **PASS** — cung có yếu tố hạn chế mà chương không đối diện: 69,9 % → **0 %**; yếu tố hạn chế không được nhắc: 8.287 → **0** |
| Lá hồi quy 09/01/2002 (Tân Tỵ, Mệnh Mậu Tuất, Cự Môn hóa Lộc, Quan Lộc VCD, Phu Thê Cơ–Âm) | **PASS** — test riêng: Phu Thê nêu Cơ–Âm vượng + Văn Xương hóa Kỵ + Đà La + Tuần, kết luận có điều kiện; Quan Lộc dùng Cơ–Âm mượn + Thân cư; Mệnh và Quan Lộc cùng kết luận công danh; Tài Bạch đủ ba phần |
| Test đạt, không hồi quy tính toán | xem §4 |

## 2. Lỗi đã sửa (tóm tắt — bằng chứng đầy đủ trong bảng audit)

**Tính toán Tử Vi** (phiên chính, `e186628`)
- A1 Lưu Hà (TV-2): bảng cũ trộn KL/TH và Canh không khớp sách nào. Giữ mặc định = bảng phổ biến (tuvi.vn #13405 đặt Canh ở Thìn) theo quyết định của chủ, **ghi rõ** "Canh không khớp sách nào"; thêm lựa chọn KL tr.29 / TH tr.26.
- A2 Tiểu hạn (TV-6): mặc định TH tr.27 (khớp nguyệt hạn tuvi.vn 12/12), thêm KL tr.39-40; lá 2002 năm 2026: TH → Phu Thê, KL → Tài Bạch (đã kiểm trên trang thật).
- A3 Bảng Tứ Hóa (TV-4/5): KL (mặc định) / TH / 全書. Mọi chỗ tra Tứ Hóa (gốc, đại hạn, lưu niên) đi qua `tuvi.hoa_of(chart, stem)`.
- A4 Tứ Hóa đưa vào 3 lá tham chiếu (tuvi.vn #260902, #13405, mới #598191 = 24/05/1971 10:30 nam) + so trong `tools/compare_reference.py`.
- A5 Tài liệu lỗi thời (scope.js, CALCULATION-ACCURACY, STAR-DIGNITY-AUDIT, `SCHOOL_PACK`).
- Ô "Tính theo sách nào" dưới bảng lá số: mỗi mục ghi sách + trang, đổi được; link chia sẻ giữ lựa chọn (và không còn làm rơi bảng độ sáng Thực Hành).

**Áp dụng quy tắc & tổng hợp Tử Vi** (S1, `c525cb7`)
- Lớp mới `src/interpret/reason/evidence.ts` (PalaceEvidence 12 cung: chính tinh thật hoặc mượn xung chiếu cho VCD, cát/sát trong cung và tam phương, Tứ Hóa gắn sao mang nó, Tuần/Triệt, cách cục, giáp, Thân cư, luật đã bắn kể cả facet thời điểm) và `reason/ledger.ts` + `engine/data/kg/domains.json` (kết luận theo lĩnh vực một lần cho cả báo cáo: thuận / có điều kiện / hai chiều / trở ngại, kèm chuỗi bằng chứng).
- `plan.ts`: yếu tố hạn chế có mặt phải được đối diện; sao mang Hóa Kỵ không làm điểm cộng thuần; luận điểm một sao phải kèm cảnh báo trừ khi có cung khác xác nhận; facet thời điểm (muộn, hoàn cảnh đặc biệt) được nói.
- Đối chiếu trang luật draft mang ý hạn chế (`engine/data/kg/rule_review_2026-10-22.json`): 22+ luật nâng verified khi câu trang khớp (vd. KL tr.217 "Gặp lũ sát tinh Kình Đà Không Kiếp thì dễ tan vỡ"; TH tr.75 "Quan Lộc: Có Tuần Triệt, Kiếp Hỏa, Kỵ hội đàn ông muộn công danh" — thêm điều kiện nam đúng trang); 30 luật giữ draft có ghi lý do (đọc "gặp" rộng hơn trang, thiếu điều kiện hãm địa…).
- Vận hạn: bỏ kết luận đếm tone; nghĩa Hóa lấy từ bảng phổ thông không còn gắn nhãn sách; mỗi đại hạn liên hệ nguyên cục.

**Bát Tự** (S2, `2076753`)
- BZ-1 bảng 10 cặp can xung/khắc ZZ tr.20 trong bazi_deep; BZ-5/6 ngày khởi vận chính xác trên trang; BZ-8 Asia/Hanoi cho nơi sinh miền Bắc; BZ-9/10 kết luận vượng nhược theo sách; BZ-13 ô phạm vi; BZ-14 bán hợp; BZ-17 hình trong câu quan hệ; BZ-23 điều kiện chết.
- Lá tham chiếu Bát Tự từ ngày giờ sinh, kiểm tay theo bảng có trang (`engine/tests/test_bazi_reference_charts.py`).
- Lớp phân xử phương pháp: mỗi đại vận / năm ghép kết luận cách TVH với điều hậu; trùng thì khẳng định, khác thì nói rõ khác ở đâu và kết luận có điều kiện; tổng kết dùng **cùng** kết luận; "cần Hỏa" ghi đúng nguồn (Trích Thiên Tủy, khí lạnh cần sưởi), không còn gán cho bảng điều hậu; không còn vận trơ "vận xấu".

## 3. Ví dụ trước / sau (lá 2002, văn người đọc thấy trên trang thật)

**Phu Thê** — trước: "…Văn Xương ở Phu Thê, người phối ngẫu đẹp… người vợ hiền hậu, vợ chồng chung lưng đến bạc đầu… **Tóm lại**, lòng nhân hậu là phần sáng nhất của cung này." (Đà La, Hóa Kỵ, Tuần chỉ có ở câu khung.)
Sau: "…Chính Văn Xương lại mang Hóa Kỵ, nên điểm tốt ấy đi kèm điều không êm… Mặt khác, Phu Thê có Đà La, nên tình cảm khó bền, dễ đổ vỡ. Về thời điểm, Tuần án ngữ cung Phu Thê, nên hôn nhân xảy ra trong hoàn cảnh đặc biệt… Đà La, Tuần và Văn Xương hóa Kỵ ở cung Phu Thê khiến hôn nhân có mặt thuận, song kèm điều kiện."

**Quan Lộc (VCD, Thân cư)** — trước: "chủ nhân lá số có duyên với thành quả: bỏ công là thấy kết quả." (một sao Thiên Việt).
Sau: "Dần là cung Quan Lộc vô chính diệu; sao chủ phải mượn là Thiên Cơ (Vượng Địa) và Thái Âm (Vượng Địa)… với Thân cư Quan Lộc, công danh đến muộn. Cân cả hai phía, xét chung các cung, đường công danh có lợi thế nhưng không trọn." Mệnh cùng kết luận: "đường công danh … có cả sự thuận lợi … lẫn trở ngại …; điều nối hai mặt ấy là công danh đến muộn."

**Bát Tự, đại vận Canh Tý** — trước: "…đều thuộc vận xấu. Nhìn từ phía khác, xét điều hậu, can Canh thuộc nhóm hỗ trợ cho dụng thần, nên vận này khá thuận." (hai phán đoán ngược, không phân xử; tổng kết bỏ điều hậu).
Sau: "Ở vận Canh Tý, hai cách xét không trùng nhau: nhóm Tài của can Canh là vận xấu theo cách, vì nhật chủ nhược mà nhóm Tài đã nhiều nhất; còn về khí hậu, can Canh lại đúng chỗ lá số cần." Tổng kết: "Canh Tý (từ 1 tuổi) thuận hay nặng tùy lúc có nhóm Tỉ Kiếp đi kèm."

**Bát Tự, đại vận Mậu Tuất (hiện tại)** — trước: trơ "vận xấu". Sau: nêu chỗ dựa ("chi Tuất còn tàng Đinh (Tỉ Kiên), thuộc nhóm dụng thần Tỉ Kiếp") và các năm nên tiến (2024, 2026, 2027).

## 4. Kết quả test (chạy lại trên `main` sau khi gộp cả ba luồng)

Chạy trên `c525cb7` (đủ ba luồng), 2026-10-22:

| Bộ | Kết quả |
|---|---|
| `npx tsc -p tsconfig.json` | sạch |
| `node --test src/interpret/test/*.test.ts` | **220 pass, 0 fail** |
| `npm run test:auth` | **85 pass, 0 fail** |
| `cd engine && pytest -q` | **1.766 passed**, 2 skipped, 2 xfailed |
| `tools/compare_reference.py` (3 lá tuvi.vn, có Tứ Hóa) | 1911 OK (3 khai báo), 1971 OK (3), 2002 OK (4) — mọi khác biệt là ô KL để trống hoặc bảng Tứ Hóa Canh của 全書 |
| oracle Tử Vi độc lập (116.928 lá, trong pytest) | khớp |
| Trang thật (`/api/chart`, `/api/interpret`) | nhãn trường phái hiện đúng; chọn tiểu hạn KL cho Tài Bạch năm 2026; văn Phu Thê / Quan Lộc / Mệnh / Bát Tự như §3 |

Test mới đáng chú ý: `engine/tests/test_school_variants.py` (trường phái theo trang), `test_reference_charts.py` (3 lá tham chiếu, có Tứ Hóa), `test_bazi_reference_charts.py`; `src/interpret/test/` S1 (lá hồi quy 2002, metamorphic thêm/bớt Kỵ/Đà La/Tuần ở Phu Thê, mâu thuẫn toàn báo cáo, câu không nguồn, trùng lặp, chương rỗng) và `bazi_reconcile.test.ts`.

## 5. Còn bất đồng trường phái (không phải lỗi — ghi rõ trên trang, cho chọn)

- Độ sáng: KL (mặc định) / TH / TT; KL để trống Tử Vi Dậu, Sửu, Ngọ và Liêm Trinh Sửu.
- Tứ Hóa: KL = TH trừ Nhâm-Khoa (Tả Phụ vs Thiên Phủ); **tuvi.vn dùng bảng 全書 cho Canh** (Khoa Thái Âm, Kỵ Thiên Đồng — thấy trên #598191 và #260902 năm xem 2030, #13405 gốc). Giữ KL vì hai sách của dự án cùng ghi; 全書 chọn được.
- Tiểu hạn TH tr.27 / KL tr.39-40 · Lưu Hà bảng phổ biến / KL tr.29 / TH tr.26 · Lưu Kình/Đà theo KL tr.42 (khác tuvi.vn) · lịch vn / vn_utc7 / cn.
- R01–R11 (phạm vi "hội/gặp/chiếu", Tuần/Triệt giúp hay hại, ngưỡng sát tinh…) — vẫn mở; các luật S1 giữ draft phần lớn vì chữ "gặp" có thể đọc rộng/hẹp.
- Bát Tự dụng thần: cách TVH (partial), bảng điều hậu (TVH tr.388 nói không rõ gốc), phù ức (draft, không vào văn).
- Tử Vi và Bát Tự có thể khác nhau về cùng một năm (lá 2002: năm 2026 Tử Vi "Trung bình", Bát Tự "cả hai cách xét đều thuận") — hai hệ độc lập, không ép khớp.

## 6. Chưa giải quyết

| Mục | Trạng thái |
|---|---|
| 102 câu luận điểm lớn dựa một luật sao phụ chưa có cung khác xác nhận | **ĐÃ SỬA** → 0 (§7): không có luật verified xác nhận nên các câu được hạ thành "chiều hướng" |
| 27 cặp chương ngược nhau chưa có kết luận giải thích (corpus 1.000) | **ĐÃ SỬA** → 0 (§7) |
| Phu Thê lá 2002: câu tổng hợp "sự hòa hợp và sự trắc trở tình cảm cùng đúng, ở những thời điểm khác nhau" là suy luận của hệ thống, không có câu sách nói "khác thời điểm" | **ĐÃ SỬA** — khung đổi thành "… cùng có mặt; điều nối hai mặt ấy là {luật thời điểm}"; lá 2002 nối bằng luật Tuần KL tr.217 (§7) |
| Văn một số chỗ còn vụng, lặp chữ (Tài Bạch: "tài lộc của khả năng kiếm tiền chỉ đến một mức, vì tài lộc giảm đi nhiều"; "cách giữ và quản lý tiền cần nhiều công sức nhất ở chỗ sự khó giữ của") | **ĐÃ SỬA** cho ba phần Tài Bạch (§7); readable.test xanh. Câu "tài lộc giảm đi nhiều" vẫn lặp chữ "tài lộc" với lời sách |
| Quan Lộc lá 2002 còn ngắn (3 câu) vì ít luật verified cho VCD | **PARTIAL** — thêm một câu sách đã đọc trên ảnh trang (TH tr.75, §7), nay 5 câu. **BLOCKED** phần còn lại: luật Cơ–Âm (KL tr.80, TT tr.78-80) chỉ áp được nếu Quan Lộc VCD mượn sao đối cung, mà KL tr.218/222 chỉ nói phép mượn cho Mệnh/Thiên Di; luật Khôi Việt (TH tr.110) đã nói ở chương Mệnh nên không nói lại |
| BZ-8 phần còn lại, BZ-11, BZ-12 (cần quyết định), BZ-16, BZ-18–22 | **OPEN** (`docs/audit/S2-bazi.md` §6) |
| Cân lượng, Lai nhân cung | **BLOCKED** — không có trong KL/TH/TT |
| Chỉ có 3 lá tham chiếu Tử Vi độc lập (+ oracle 116.928 lá) | giới hạn kiểm chứng ngoài |

## 7. Bổ sung 2026-10-22: đóng các mục FAILED / OPEN của §1 và §6

Số đo dùng `node tools/interpret/eval_synthesis.ts --n 1000` trên corpus 1.000 lá. Trước = `4be316e` (main), sau = commit này.

| Số đo (1.000 lá) | Trước | Sau |
|---|---|---|
| Câu luận điểm lớn dựa một luật sao phụ, không có lời "chiều hướng", không có cung khác xác nhận | 102 / 8.722 | **0** / 8.719 |
| Cặp chương nói ngược nhau về một lĩnh vực mà báo cáo không có kết luận giải thích | 27 | **0** |
| Một lĩnh vực có hai kết luận khác nhau trong cùng báo cáo | 0 | 0 |
| Cung có yếu tố hạn chế mà chương không đối diện | 0 / 8.248 | 0 / 8.248 |
| Chương có lỗi chặn | 0 | 0 |

**Luận điểm một sao (102 → 0).** Không tìm được luật verified nào xác nhận, nên không thêm luật xác nhận nào. Mọi câu đều được hạ thành "chiều hướng" ngay trong khung. Có ba lỗi trong lớp chặn:
- 89 câu là luật TL tr.128 ("Tật Ách có Tuần, Triệt…: cường độ tật ách được giảm bớt"). Luật này đứng trên Tuần/Triệt, nhưng `plan.ts` chỉ lấy tên sao/Hóa nên danh sách sao rỗng và lời "chiều hướng" không được thêm. Nay Tuần/Triệt được tính là chỗ đứng của luận điểm: "Có điều, điều này mới dựa vào Tuần, nên chỉ nên xem là một chiều hướng."
- 12 câu (Hồng Loan / Đào Hoa / Lộc Tồn ở Quan Lộc, Thiên Di) bỏ lời cảnh báo vì có một câu "cung khác xác nhận". Câu ấy đã nói ở chương trước nên bị lọc trùng, và lời cảnh báo mất theo. Nay câu xác nhận đã nói ở chương khác thì không được tính.
- 1 câu là luật độ số theo tuổi (KL tr.225-227, "tuổi Dậu"), luật không có sao nào. Nay câu ghi "Riêng tuổi Dậu thì chưa đủ để kết luận; đây mới là một chiều hướng."
- Bộ đo được chỉnh khớp với định nghĩa của `plan.ts`: luật cấp lá số (độ số) đi cùng trong một luận điểm được tính là luật thứ hai. Kết quả là một câu ra khỏi số đếm (Tử Phù + tuổi Dậu, hai luật) và một câu vào (chỉ tuổi Dậu, câu đã kể ở trên).

**Mâu thuẫn (27 → 0).** 27 cặp nằm trên 13 lá, đều ở lĩnh vực tiền bạc:
- 2 lá có mâu thuẫn thật: Phúc Đức có Địa Không/Địa Kiếp, "số nghèo khổ" (KL tr.65: "Không, Kiếp thủ cung Tài hoặc cung Phúc"), trong khi Tài Bạch/Quan Lộc nói thuận. Phúc Đức được thêm vào phần "khả năng kiếm tiền" của `domains.json`, có ghi trích KL tr.65 và KL tr.216. Ledger nay phân xử cả hai phía thành kết luận có điều kiện. Chương nói phía ngược lại (Phúc Đức, hoặc Mệnh khi Thân cư Phúc Đức) dẫn **cùng** kết luận đó bằng một câu ngắn ("Xét chung các cung, khả năng kiếm tiền …"), qua `echoLedger` trong `prose/luan.ts`.
- 11 lá là tiền của người khác: "cha mẹ vất vả, chẳng giàu" (KL tr.220, Phụ Mẫu) đặt cạnh "con cái khá giả" hay tài lộc của đương số. Hệ thống vẫn xem tài sản của cha mẹ, con cái, anh em, bạn đời là chuyện của họ (`PROSE_SPECS.bond`). Bộ đo trước gom mọi facet `finance.*` vào tiền của đương số; nay câu về người khác không còn là một phía của lĩnh vực đương số. Nếu tính theo cách cũ thì còn **22** cặp, và cả 22 đều là câu KL tr.220 về cha mẹ. Đó không phải mâu thuẫn, nên không ép qua ledger.

**Phu Thê lá 2002.** Khung `both_timing` "… cùng đúng, ở những thời điểm khác nhau" được thay bằng "… cùng có mặt; điều nối hai mặt ấy là {link}". Văn nay: "Xét chung, sự hòa hợp và sự trắc trở tình cảm cùng có mặt; điều nối hai mặt ấy là hôn nhân xảy ra trong hoàn cảnh đặc biệt, đôi lứa ban đầu ngỡ ngàng." Chỗ nối là luật Tuần `TV_KL_CUNG_PHU_THE_TT`, KL tr.217.

**Tài Bạch ba phần (lá 2002).**

| Phần | Trước | Sau |
|---|---|---|
| kiếm | "tài lộc của khả năng kiếm tiền chỉ đến một mức, vì tài lộc giảm đi nhiều" | "phần thuận có thật, nhờ Cự Môn hóa Lộc ở cung Mệnh, song bị giới hạn: tài lộc giảm đi nhiều" |
| giữ | "cách giữ và quản lý tiền cần nhiều công sức nhất ở chỗ sự khó giữ của" | "chỗ đòi hỏi nhiều công sức nhất ở phần này là tiền bạc khó giữ" |
| tích lũy | "phía vướng của phần tích lũy, nhà cửa nặng hơn: …" | "phía vướng của phần này nặng hơn: …" |

Thay đổi đi kèm:
- Khung `both_book` nêu đúng luật bị sách thu hẹp: Hóa Lộc ở Tứ Mộ, KL `TV_KL_PHU2_HOA_LOC_TU_MO`. Trước đó khung nêu sao mạnh nhất của phía thuận.
- Câu chính của một phần gọi phần ấy là "phần này", vì tiêu đề đoạn đã nêu tên phần.
- Cụm danh từ của `fin.volatile` đổi thành "tiền bạc khó giữ".
- Bỏ chữ "Hóa Kỵ" lặp khi đã có "Văn Xương hóa Kỵ".
- readable.test xanh. Barnum/strip của chương Mệnh trên benchmark20: 40,2 % / 0,063, dưới cổng 40,55 % / 0,0655.

**Quan Lộc lá 2002.** Đọc ảnh TH tr.75 thì mục "Thân cư tại cung — Quan Lộc" còn câu: "Nếu có Cát tinh hội cũng phải ngoài 40 tuổi mới nhẹ bước thanh vân."
- Thêm luật `TV_TH_CACH_QUAN_LOC_THAN_TT_CAT`, verified.
- Luật giữ đúng điều kiện của câu trước trong cùng mục: Thân cư Quan Lộc, nam, có Tuần Triệt / Kiếp Hỏa / Kỵ hội.
- "Cát tinh hội" được đọc là Tả Hữu, Xương Khúc hoặc Khôi Việt hội, như luật Thiên Di cùng trang.
- Hồ sơ luật ở `rule_review_2026-10-22.json`, có test pytest.

Chương Quan Lộc nói câu này ngay sau "công danh đến muộn": "Về nhịp đi của công danh, với Thân cư Quan Lộc, công danh đến muộn. Dù có cát tinh hội, cũng phải ngoài 40 tuổi mới nhẹ bước thanh vân."

Phần còn lại BLOCKED. Các luật Cơ–Âm ở Quan Lộc (KL tr.80, TT tr.78-80) chỉ áp được nếu Quan Lộc VCD mượn chính tinh đối cung. KL tr.218/222 chỉ nói phép mượn cho Mệnh/Thiên Di, nên không suy rộng sang Quan Lộc (`docs/TUVI-DEEP-INTERPRETATION-ROADMAP.md`). Luật Khôi Việt (TH tr.110) bắn ở Quan Lộc nhưng đã được nói ở chương Mệnh, và quy tắc "không nói một luận điểm hai lần" vẫn giữ.

Chạy lại sau khi đổi luật: `refire_fixtures.py`, `base_rates.ts`, `index_norms.ts`, `build.ts`, `build_site.py`, goldens.


Kết quả test trên cây đã gộp `origin/main` (`d9bdc15`): `tsc` sạch · `node --test src/interpret/test/*.test.ts` **220 pass, 0 fail** · `npm run test:auth` **88 pass, 0 fail** · `cd engine && pytest -q` **1.767 passed**, 2 skipped, 2 xfailed.
