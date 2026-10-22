# S2 — Bát Tự: sửa tính toán, lá tham chiếu, lớp phân xử phương pháp (audit 2026-10-22)

Phần Bát Tự của kế hoạch `quirky-tinkering-rabin` (bước 2–5). Gốc: `e186628`. Danh mục lỗi gốc: [bazi.md](bazi.md), [../INTERPRETATION-ENGINE-AUDIT.md](../INTERPRETATION-ENGINE-AUDIT.md) §1–3, [../AUDIT-2026-10-22.md](../AUDIT-2026-10-22.md) C1–C5. Văn trước/sau: [../examples/bazi-S2-2002.md](../examples/bazi-S2-2002.md), [../examples/bazi-S2-1911.md](../examples/bazi-S2-1911.md).

Viết tắt nguồn: **ZZ** = 八字真宗 (Bát Tự Chân Tông, PDF có lớp chữ); **TVH** = Thiệu Vĩ Hoa, *Dự Đoán Theo Tứ Trụ* (bản quét, trang in = trang PDF); **TTT** = *Trích Thiên Tủy*.

## 1. Đã sửa (kèm bằng chứng)

| Mã | Lỗi | Sửa | Nguồn | Test |
|---|---|---|---|---|
| BZ-1 | bazi_deep (`interact.py`, `temporal_deep.py`) và `compare_deep.py` còn bảng can xung 4 cặp `STEM_CLASH_LEGACY4`; test vàng chỉ kiểm 4 cặp | cả ba đọc `STEM_CLASH_KIND` 10 cặp, kèm loại xung/khắc như trang in; `STEM_CLASH_LEGACY4` bỏ. Hệ số tác động nháp (`stem_clash_adj/_far`) chỉ áp cho 4 cặp đã hiệu chỉnh; 6 cặp mới được ghi nhận (`status: ghi_nhan`) mà **không** gán hệ số (trang sách không cho độ lớn) | ZZ tr.20 「干冲克」 | `test_bazi_book_golden.py::test_stem_relations_p20` (đủ 10 cặp + loại), `::test_bazi_deep_uses_the_ten_pair_stem_table_p20`; `compare_deep_expected.json` tái tạo (+2 quan hệ trực tiếp ở 3 cặp mẫu) |
| BZ-5/6 | trang dùng `start_year_approx` (bỏ tháng sinh) cho nhãn năm và "Hiện tại"; Python, TS, trang chia năm cho đại vận theo ba cách khác nhau | **một luật chung**: năm Bát Tự Y (Lập Xuân ≈ Y+0,09 → Y+1,09) thuộc đại vận đang hiệu lực ở giữa năm (Y+0,59) — `bazi.luck_first_year`, `temporal.bazi_year`, `atlas.js luckFirstYear/periodYears`; vận hiện tại trên trang theo đúng ngày `start_date` (`luckIndexOn`); `/api/facts` `bazi.luck[]` có `start_year` theo luật ấy và `start_date`. Đây là quy ước hiển thị (không sách nào bàn), ghi trong mã | — (tính toán) | `test_bazi_deep_luck.py::test_a_year_gets_the_luck_in_force_for_most_of_it_and_the_rule_is_shared`; `test_bazi_reference_charts.py` (Mậu Tuất từ 23/02/2023 giữ năm 2023; 庚申 giữ 1999–2001 ở mẫu ZZ) |
| BZ-8 | mọi nơi sinh → `Asia/Ho_Chi_Minh`; miền Bắc 1960–1975 lệch 1 giờ (múi đó là +08 ở miền Nam) | Hà Nội, Hải Phòng, Vinh → `Asia/Hanoi` (`util.js placeTz`, `app.js`, `profile.js`); engine dựng `Asia/Hanoi` từ dòng Zone của tzdb *backzone* (+08 từ 1947-04-01 đến 10/1954, +07 từ đó) vì tzdata cài sẵn không có; `Intl` trên trình duyệt đọc `Asia/Bangkok` thay cho tên này | tzdb `asia` (chú thích Eggert 2024, theo Trần Tiến Bình, *Lịch Việt Nam thế kỷ XX–XXI* tr.49-50) và `backzone` | `test_bazi_s2_fixes.py::test_bz8_*` (bù giờ 1950/1954/1965/1990; sinh Hà Nội 07/12/1965 15:15: tháng 戊子 theo +07, 丁亥 nếu đọc theo +08) |
| BZ-9/10 | dải ±0,03 quanh 40% (`strength._band`) cho "hai cách đọc", trong khi TVH tr.355 gọi 39,6% là "hơi nhược"; văn có thể đặt "cực nhược"/"trung hòa" cạnh "nhược" | engine giữ dải như **quy ước hiển thị có nhãn** (`profile.tvh_margin`, `METHOD_META`); văn luôn nói phía của quy tắc 40%: `prose_summary.strength.dm_strong` luôn quyết định, `near_threshold` chỉ làm chữ "hơi" (như ví dụ của sách), dải nằm trong ghi chú câu; bảng dụng thần theo cách đọc ở phía sách khi ở biên (`cach_tvh.near_threshold`) | TVH tr.355 (ví dụ 6) | `test_bazi_s2_fixes.py::test_bz9_*`; `deep.test.ts` (lá 1990: 38% → "hơi nhược", ghi chú dải); `bazi_reconcile.test.ts` (văn không có nhãn bảy mức) |
| BZ-13 | `scope.js` (khung "Phạm vi luận giải" Bát Tự) nói thần sát, nạp âm, vượng/nhược, cách cục "chưa có" trong khi báo cáo đã có | viết lại phần Bát Tự: điều đã tính (TVH 40%, bảng dụng thần theo cách, bảng điều hậu và ghi chú xuất xứ của nó, phân xử khi hai bảng khác nhau, thần sát, không vong, nạp âm, 10 cặp can) và điều chưa đưa vào (phù ức, nghĩa của hợp/xung…, hóa can xa, lưu nguyệt) | ZZ tr.19-26, TVH tr.336-338, 355, 378-396 | (văn bản giao diện) |
| BZ-14 | `bazi.py` (đường production) không báo bán hợp | `branch_semi_triad`: hai chi của một tam hợp, một trong hai là chi giữa; không báo khi đủ tam hợp; nhãn ở `bazi.js`, `bazi_reading.py`, `prose/bazi.ts` | ZZ tr.20 半合局 | `test_bazi_s2_fixes.py::test_bz14_*` (子辰 có; 寅戌, 申辰 không) |
| BZ-17 | câu quan hệ của `analysis.py` bỏ hình (lá 1990: Ngọ–Ngọ tự hình) | câu nêu đủ lục hợp, bán hợp, xung, hại, phá, hình, tự hình, hình đủ bộ, can hợp, can xung/khắc | ZZ tr.19-20 | `test_bazi_s2_fixes.py::test_bz17_*` |
| BZ-23 | `or True` (`facts.py`, `interact.py`, `tvh_score.py`, `pipeline.py`), `tb not in ()` (`temporal_deep.py`) | bỏ, giữ nguyên hành vi | — | `test_bazi_s2_fixes.py::test_bz23_*` |
| luck_role.yong | vai trò điều hậu xét theo **nhóm thập thần**: Ất (cùng nhóm Ấn với Giáp) bị gọi "đúng là hành lá số cần", và luật TTT "cái đầu" bắn trên tiền đề đó (Ất Mùi lá 2002; Quý Tỵ, Ất Mùi lá 1911) | vai trò theo **tên can** ô bảng nêu: can đứng đầu = dụng, can khác ô nêu = hỷ (`pipeline._dh_role`, `temporal_deep._roles` cho luật TTT 歲運) | TVH tr.389-396 | `test_bazi_deep_prose_summary.py::test_dieu_hau_role_is_by_the_stem_the_cell_names`, `::test_no_draft_premise_rules_reach_the_prose` |
| "cần Hỏa" ghi sai nguồn | "theo bảng điều hậu, lá số cần Hỏa" (Hỏa là chỉ số hàn–nhiệt của hệ thống, `yongshen.py` `need_elements`; ô bảng chỉ nêu Giáp, Canh); "nên bớt Thủy" cùng gốc | khung câu nêu can của ô bảng ("về điều hậu, can nên có là Giáp và Canh"); hành chỉ được nói qua luật TTT hàn noãn đã bắn (`need_rule`); `dieu_hau.need_src = he_thong` trong facts | TVH tr.389-396; TTT tr.113-114 | `test_need_element_is_the_heat_index_not_the_table`; `bazi_reconcile.test.ts` |

## 2. Lá tham chiếu Bát Tự từ ngày giờ sinh (`engine/tests/test_bazi_reference_charts.py`)

Mọi giá trị kỳ vọng suy tay từ bảng (đếm ngày từ 1900-01-01 = 甲戌, đối chiếu 2000-01-01 = 戊午; 五虎遁, 五鼠遁 ZZ tr.20, 35; tiết ZZ tr.23; tàng can ZZ tr.7-8; thập thần ZZ tr.17; trường sinh ZZ tr.24-25), cách suy viết ngay trong test; không lấy output engine làm kỳ vọng.

| Lá | Tứ trụ | Khởi vận | Kết quả |
|---|---|---|---|
| 09/01/2002 04:30 nam | Tân Tỵ / Tân Sửu / Đinh Sửu / Nhâm Dần | nghịch, 1,1 năm; Canh Tý, Kỷ Hợi, Mậu Tuất, Đinh Dậu | khớp; tàng can, thập thần, trường sinh khớp |
| 01/01/1911 12:30 nam | Canh Tuất / Mậu Tý / Tân Mùi / Giáp Ngọ | thuận, 1,7 năm; Kỷ Sửu, Canh Dần, Tân Mão | khớp (giờ Phù Liễn +07:06:30 của tzdb) |
| TVH Ví dụ 2 (tr.398) — âm 10/9/1975 giờ Tý | Ất Mão / Bính Tuất / Quý Tỵ / Nhâm Tý | nghịch, Ất Dậu… (sách: 2 tuổi) | khớp |
| TVH Ví dụ 3 (tr.399) — âm 29/9/1970 giờ Dậu ("Ngày 129" in lỗi; chỉ ngày 29 cho trụ Tân Tỵ) | Canh Tuất / Bính Tuất / Tân Tỵ / Đinh Dậu | thuận, Đinh Hợi… (sách: 4 tuổi) | khớp |
| TVH Ví dụ 5 (tr.400-401) — âm 25/9/1966 giờ Dậu | Bính Ngọ / Mậu Tuất / Canh Ngọ / Ất Dậu | thuận, Kỷ Hợi… (sách: 1 tuổi) | khớp |
| TVH Ví dụ 1 (tr.397) — âm 2/11/1952 giờ Thìn | sách in Nhâm Thìn / **Tân Hợi** / Mậu Tuất / Bính Thìn | sách in Nhâm Tý… 6 tuổi | **bất đồng nội tại của sách**: âm 2/11/1952 = 18/12/1952, sau Đại Tuyết (7/12) 11 ngày nên tháng theo tiết là Nhâm Tý; tuổi khởi vận 6 của chính trang sách chỉ khớp ngày 18/12. Năm, ngày, giờ khớp. Test ghi rõ bất đồng |
| ZZ tr.45-46 (串宫神流年直断命例) | 癸未 / 乙丑 / 乙未 / 戊寅 (không in ngày sinh; ngày 乙未 duy nhất trong tháng 乙丑 năm đó là 01/02/1944) | 胎元 丙辰, 命宫 甲寅, 身宫 丙辰, đại vận 庚申 cho 1999, 2000, 2001 | khớp mọi điều trang in |

Tuổi khởi vận sách in là số nguyên mà không nói cách làm tròn (1,58→2; 3,47→4; 0,15→1 nhưng 6,21→6); test chỉ đòi tuổi sách in là tuổi tính được làm tròn lên hoặc xuống. TVH Ví dụ 4 (nữ, tr.400) không dùng: hàng can in lệch cột, không đọc chắc được.

## 3. Lớp phân xử phương pháp (bước 3)

- `pipeline.reconcile` (Python, facts `luck[].reconcile`, `years[].reconcile`) và `reconcileTs` (TS, cho facts cũ như corpus1000; test bắt hai bên trùng nhau trên mọi trụ có cả hai): mỗi đại vận / lưu niên một kết luận từ **bảng dụng thần theo cách** (TVH tr.378-386: cân nhật chủ với nhóm nhiều nhất) và **bảng điều hậu** (TVH tr.389-396: hàn noãn của tháng sinh, xét theo tên can) cộng hành mà luật TTT hàn noãn đã bắn yêu cầu.
  - cùng thuận → khẳng định ("Hai cách xét cùng thuận… lúc nên chủ động tiến");
  - cách xấu mà điều hậu thuận → nói rõ chỗ khác (cân bằng thân–tài vs khí hàn), kết luận có điều kiện ("thuận hay nặng tùy lúc có nhóm X đi kèm") kèm các năm nên tiến trong chặng;
  - can và chi tách hai phía → "tốt xấu đan xen: can … thuận, chi … nặng", không cân bên nào hơn;
  - cách xấu, không bảng nào đỡ → câu chuyển từ dữ kiện (chi còn tàng can thuộc nhóm dụng thần / can điều hậu) và hướng xử lý (các năm nên tiến), không bao giờ trơ "vận xấu";
  - mức tin cậy nói một lần ở chương Cách cục (phần "chỗ hai cách xét khác nhau"): bảng theo cách đi cùng phép chấm điểm sức nhật chủ; bảng điều hậu chính Thiệu Vĩ Hoa ghi do độc giả gửi, chưa rõ xuất xứ (tr.388); `METHOD_META` đầy đủ ở ghi chú câu.
- Tổng kết đọc **cùng** các kết luận đó (`classOf`); test toàn báo cáo bắt một đại vận mang hai kết luận.
- Phù ức vẫn draft, không vào văn; test chặn mọi câu lập luận kiểu phù ức.

## 4. Khung chương (bước 4)

Chương Cách cục & dụng thần: (1) cấu trúc — cách, bảng dụng thần; (2) điểm tựa và giới hạn — câu thành bại TVH, nhóm dụng thần nằm ở đâu trong tứ trụ; (3) khí hậu — điều hậu, luật TTT; (4) chỗ hai cách xét khác nhau — và mức tin cậy; (5) kết luận có điều kiện; (6) nguồn — danh sách sách/trang của chương trong ô "Căn cứ" (`report.js btSources`), không chen vào văn. Mỗi đoạn đại vận / lưu niên chạy cùng thứ tự trong một đoạn (đầu đề → hai phía → tương tác với nguyên cục → chỗ vênh → kết luận). Cổng đọc dễ: không từ phương pháp (cùng regex `readable.test.ts`).

## 5. Test (bước 5) — `src/interpret/test/bazi_reconcile.test.ts`

Trên benchmark20 + lá 2002 + lá 1990 và **corpus1000** (1.000 lá, 8.810 đoạn đại vận, 0 lỗi): một kết luận mỗi đại vận trong cả báo cáo; đoạn có cả ý tốt và xấu phải kết bằng câu phân xử; không vận "nặng" trơ; không câu lặp; câu `sach` phải trỏ luật verified, câu `tinh_toan` phải có bảng/trang; không chương rỗng; 0 câu `pho_thong`; không từ phương pháp; không nhãn bảy mức; không ghi "bảng điều hậu… cần <hành>"; can nào được gọi "can điều hậu" phải là can ô bảng nêu; thứ tự phần của chương Cách cục. Thêm: các phát hiện audit trên lá 2002 (Canh Tý, Kỷ Hợi, Mậu Tuất, Ất Mùi, "cần Hỏa").

## 6. Còn mở

| Mã | Trạng thái | Ghi chú |
|---|---|---|
| BZ-1 (hệ số) | **NEEDS SOURCE** | 6 cặp can mới (戊甲, 己乙, 庚丙, 辛丁, 壬戊, 癸己) được báo nhưng không có hệ số tác động trong khí thế nháp; trang ZZ tr.20 chỉ in bảng |
| BZ-4 | **NEEDS SOURCE** | định nghĩa "khuyết" (ZZ tr.27); luật nháp vẫn ẩn |
| BZ-7 | **NEEDS SOURCE** | giờ Tý muộn |
| BZ-8 (phần còn lại) | **OPEN** | "Nơi khác / ngoài Việt Nam" vẫn nhập IANA tay; giờ địa phương miền Nam thời chiến (tzdb: "chưa rõ") không xử lý; `Intl` hiển thị ngày tiết của trẻ sinh miền Bắc trước 10/1954 lệch tối đa 1 giờ (chỉ hiển thị) |
| BZ-11 | **OPEN** | cơ sở hiệu lực = min(luật, tiền đề) chưa lan trong engine; văn đã lọc `_CACH_CUC`, `_PHU_UC` |
| BZ-12 | **OPEN / NEEDS DECISION** | chính sách mâu thuẫn cho luật ZZ trực tiếp |
| BZ-15 | **NEEDS SOURCE** | tên "vô ân / thị thế" không có ở ZZ tr.20 |
| BZ-16 | **OPEN** | trang vẫn ghi "tiềm năng hóa" cho can hợp xa (văn S2 không nói hóa) |
| BZ-18, 19, 20, 21, 22 | **OPEN** | biểu đồ đếm chữ; nhãn tuổi thực/mụ; tháng khởi vận TS làm tròn; cảnh báo sát tiết; không vong của chi vận |
| Luật năm–vận | quy ước | "năm thuộc vận hiệu lực ở giữa năm Bát Tự" là quy ước hiển thị, không sách nào bàn; `luck_changes_within_year` và `start_date` nói khi đổi vận rơi trong năm |
| corpus1000 | giữ nguyên | không tái tạo (facts cũ); TS fallback `reconcileTs` quyết, test đảm bảo trùng với Python ở nơi có cả hai |
