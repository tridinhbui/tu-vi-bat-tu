# S1 — Tử Vi: tầng tổng hợp và phân xử (2026-10-22)

Phần này dành cho `docs/AUDIT-2026-10-22-REPORT.md` (phiên cha ghép vào). Kế hoạch: `~/.claude/plans/quirky-tinkering-rabin.md`, bước 3, 4, 5 cho Tử Vi và
phần đối chiếu trang các luật draft mang ý hạn chế của bước 2. Chuỗi mới: facts → run → lift → resolve → **evidence** (mọi yếu tố cấu trúc của
cung) → **plan** (luận điểm, có chặn) → **ledger** (một kết luận cho mỗi lĩnh vực, toàn báo cáo) → luận cung / vận hạn.

## 1. Đối chiếu trang các luật draft mang ý hạn chế

52 luật draft bắn trên corpus1000 và mang ý hạn chế đã được đọc trên **ảnh trang sách**. Lý do đọc ảnh: lớp chữ của TH đảo thứ tự dòng. Hồ sơ
từng luật nằm ở `engine/data/kg/rule_review_2026-10-22.json`, gồm trang, câu trích nguyên văn, kết luận và lý do. Kết quả: **22 luật lên verified,
30 luật giữ draft**, mỗi luật giữ draft đều có lý do ghi trong hồ sơ.

| Luật | Trang | Câu trên trang | Kết quả |
|---|---|---|---|
| TV_KL_CUNG_PHU_THE_KINH_DA_KHONG_KIEP | KL tr.217 | “Gặp lũ sát tinh Kình Đà Không Kiếp thì dễ tan vỡ.” | verified (sao xét trong cung, như các luật verified cùng trang đọc chữ “gặp”) |
| TV_TH_CACH_QUAN_LOC_THAN_TT | TH tr.75 | “Quan Lộc: Có Tuần Triệt, Kiếp Hỏa, Kỵ hội đàn ông muộn công danh.” | verified; **thêm điều kiện nam** đúng như trang |
| TV_KL_CUNG_PHU_THE_SAT_PHA_LIEM_THAM | KL tr.217 | “Chẳng nên gặp đám Sát Phá Liêm Tham, dễ sinh một dạ hai lòng, bất hòa xa cách.” | verified |
| TV_KL_CUNG_PHUC_DUC_SAT_PHA_LIEM_THAM | KL tr.217 | “Gặp Sát Phá Liêm Tham: thì khắc tổ ly tông, hao tâm tổn trí.” | verified; khái niệm sửa từ fin.volatile thành fam.negative + inner.unrest |
| TV_KL_CUNG_THIEN_DI_SAT_PHA_THAM | KL tr.219 | “Di có Sát Phá Tham thì tranh giành, lam lũ.” | verified |
| TV_KL_CUNG_NO_BOC_THAM_ALONE, …_PHUC_BINH_KY | KL tr.219 | “Tham lang độc thủ: không trung thành”; “gặp lũ Phục binh, Hóa kỵ, Phá toái thì bạn bè, gia nhân phản chủ” | verified |
| TV_KL_CUNG_QUAN_LOC_SAT_TT | KL tr.216 | “gặp lũ Không Kiếp, Kình Đà, Hỏa Linh, Kiếp Sát, Hóa Kỵ, Tuần Triệt thì đỗ vỡ cơ đồ…” | **draft**: luật đọc “gặp” là tam phương, trang không nói hội/chiếu |
| TV_KL_CUNG_TAI_BACH_KHONG_KIEP | KL tr.216 | “bị lũ Không Kiếp, Liêm Tham, Song Hao ghé vào thì nghèo muôn thuở” | **draft**: “ghé vào” đọc rộng (bắn 58 % corpus), câu diễn ý làm nhẹ, thiếu Song Hao |
| TV_KL_CUNG_DIEN_TRACH_NGHEO | KL tr.220 | “… Không Kiếp hãm địa, Kình Đà, Tuần Triệt …” | **draft**: luật bỏ điều kiện hãm địa của Không Kiếp |
| 15 luật TH/KL/TT khác | TH tr.64, 68, 102, 104, 106, 108, 111, 113; KL tr.64; TT tr.78, 82, 88 | ví dụ TH tr.106: “Đà Không nghèo khó tai ương”, “Tuần Triệt trước đất cùng không” | verified; có kiểm tay ảnh TH tr.106 và TT tr.88 |
| 27 luật còn lại | | | **draft**: rộng hơn trang (thiếu độ sáng, thiếu sao đi kèm, “gặp” đọc là tam phương, điều kiện luôn đúng) hoặc trang có ý kiến ngược chiều (KL tr.79 Cơ gặp Tuần Triệt) |

Ba trang trích dẫn được sửa theo ảnh: TT tr.88 thay cho tr.87-88 và tr.88-89, TT tr.78 thay cho tr.77-78. Pack JSON được vá tại chỗ, vì chạy lại
`tools/build_*_pack.py` sẽ làm mất các sửa đổi sau khi sinh. Hai builder KL cung và TH cách đã được đồng bộ. Các builder TH phú cung, TH aux2 và TT
cung chưa đồng bộ; danh sách ở phần 8. Fixture `python_fired` được tính lại bằng `tools/interpret/refire_fixtures.py`, công cụ này chỉ chạy lại
luật và giữ nguyên dữ kiện. Đã chạy lại `base_rates.ts` và `index_norms.ts`: corr_decade_natal = 0,23.

## 2. `reason/evidence.ts`: PalaceEvidence cho 12 cung

Mỗi cung có các dữ kiện sau, đều thuộc basis tinh_toan:
- chính tinh và độ sáng. Cung VCD mượn chính tinh cung xung chiếu, mỗi sao ghi `borrowed: true`;
- chính tinh tam phương;
- cát/sát tinh, Lộc Tồn, Mã, Hao trong cung và tam phương;
- Tứ Hóa gắn với sao mang nó;
- Tuần/Triệt, cung giáp, Thân cư;
- cách cục draft (chỉ liệt kê, không đưa vào văn) và cấu trúc đặc biệt;
- các luật verified đã bắn, kể cả facet `*.timing`.

Mỗi yếu tố trong cung được gán vai trò theo quy ước hệ thống:
- **hạn chế**: Hóa Kỵ, sát tinh chưa được kiểm đắc, chính tinh hãm, Tuần/Triệt;
- **hai mặt**: sao mang Hóa Kỵ (ví dụ Văn Xương hóa Kỵ), Hóa tốt đóng trên sao hãm, sát tinh đắc;
- **hỗ trợ**: các yếu tố tốt còn lại.

## 3. `reason/plan.ts` (reasoner-0.4.0)

- `Claim.single`: kết luận lớn (công danh, tiền bạc, hôn nhân, sức khỏe) chỉ dựa vào một luật của sao phụ (tầng 4–6), không có cung khác xác nhận.
  Chương nói thêm “đây mới là một chiều hướng”.
- `Claim.kyCarrier`: luận điểm tốt đứng trên sao mang Hóa Kỵ không bao giờ là điểm cộng thuần. Câu thêm vào cho biết chính sao ấy mang Hóa Kỵ.
- `confront`: mọi yếu tố hạn chế trong cung kèm các luật verified đứng trên nó. Chương luận cung phải đối diện từng yếu tố theo thứ tự ưu tiên:
  1. một câu đọc luật đứng trên yếu tố ấy;
  2. nếu không có, một luật verified chưa nói;
  3. nếu vẫn không có, một câu cấu trúc có điều kiện.
  Chương cũ (cung không có gì để luận) cũng được thêm câu đối diện.
- `timings`: các luật verified về thời điểm của cung (rel.timing, career.late, …) được nói ra, không bị rơi vào course line. Ở Mệnh vẫn giữ bộ lọc
  Barnum.

## 4. `reason/ledger.ts` + `engine/data/kg/domains.json`

`domains.json` là quy ước hệ thống, có ghi nhãn và có trích KL tr.216 cho tiền bạc. Các lĩnh vực:
- **công danh**: Quan Lộc (cung chính), Mệnh, Tài Bạch, Thiên Di, cộng Thân cư;
- **tiền bạc**, chia ba phần:
  - kiếm tiền: Tài Bạch, Quan Lộc, Mệnh;
  - giữ tiền: Tài Bạch, cộng Kỵ, Không Kiếp, Hao;
  - tích lũy: Điền Trạch, cộng Lộc Tồn, Thiên Phủ;
- **hôn nhân**: Phu Thê, Phúc Đức, Mệnh, cộng Kỵ, Tuần/Triệt;
- **sức khỏe**: Tật Ách, Mệnh.

Mỗi lĩnh vực được phân xử **một lần** theo thứ tự của adjudicate.ts:
1. lời sách nối hai mặt (luật thời điểm, quan hệ sách);
2. nhận định cụ thể hơn thắng;
3. sao gốc hơn thắng;
4. còn lại thì hai chiều.

Không cộng điểm. Kết quả gồm `verdict` (thuận / có điều kiện / hai chiều / trở ngại) và chuỗi căn cứ (dữ kiện → luật → liên kết → kết luận).
Mệnh kết luận công danh qua Mệnh–Tài–Quan–Di. Tiền bạc kết luận ba phần ở chương Tài Bạch. Mọi chương nói cùng một kết luận; chương nói sau
chỉ nhắc ngắn rằng kết luận khớp.

## 5. Khung 6 phần của chương luận cung (`prose/luan.ts`, luan-0.2.0; `engine/web/js/report.js`)

Mỗi câu mang `trace.part` và mỗi đoạn mang `part`:
1. cấu trúc (khung cung);
2. hỗ trợ / hạn chế (các luận điểm);
3. tương tác (tam phương, cấu trúc, Thân);
4. mâu thuẫn và cách giải thích (yếu tố hạn chế, mặt ngược, câu “hai mặt nối nhau ở chỗ…”);
5. kết luận có điều kiện từ ledger;
6. nguồn: mục gập “Căn cứ của phần luận này” trong report.js, liệt kê từng lĩnh vực, chuỗi căn cứ và các trang đã dùng.

Khi người đọc bấm vào một câu kết luận, trang hiện “Kết luận chung”. Cổng Track B vẫn giữ: không từ phương pháp trong văn, mọi giải thích
phương pháp nằm trong note.

## 6. Vận hạn (`prose/vanhan.ts`)

- Mỗi đại hạn nối với nguyên cục. Nếu cung hạn là cung chính của một lĩnh vực, câu nhắc kết luận ledger của lĩnh vực ấy (ví dụ hạn Phu Thê 23–32
  của lá 2002 nhắc hôn nhân “thuận nhưng có điều kiện, vì có Đà La, Hóa Kỵ, Tuần”).
- Hóa Lộc / Hóa Kỵ theo can hạn được gắn nhãn thông lệ (he_thong). Nghĩa “Hóa ở cung nào gây điều ở cung ấy” lấy theo KL tr.195-197, và câu nêu
  lĩnh vực nguyên cục mà Hóa chạm tới.
- Năm hiện tại: các sao lưu rơi vào cung hạn (KL tr.41-42).
- **Bỏ kết luận đếm tone** ở dòng 137 cũ. Câu kết của mỗi hạn lấy **mức chỉ số indices.ts**, tức cùng mức với biểu đồ Tổng quan. Khi mức ngược với
  câu sách của hạn, câu kết nói rõ điều đó.
- **Sửa nhãn `sach`** của câu nghĩa Hóa trước đây lấy từ thẻ phổ thông (dòng 78 và 131 cũ). Câu lưu Hóa của năm cũng không dùng thẻ phổ thông nữa.

## 7. Kiểm thử và số đo

Test mới `src/interpret/test/synthesis.test.ts` (12 test):
- fixture 2002 khớp bảng tuvi.vn;
- evidence 12 cung;
- Phu Thê, Quan Lộc, Tài Bạch ba phần, Mệnh–Quan Lộc cùng kết luận;
- metamorphic thêm/bớt Kỵ, Đà La, Tuần (fixture `phu_the_metamorphic.json`, sinh bằng `tools/interpret/make_phu_the_metamorphic.py`);
- bộ kiểm mâu thuẫn toàn báo cáo, kèm test chứng minh bộ kiểm bắt được lỗi;
- yếu tố hạn chế, bước plan, câu trùng, chương rỗng;
- khung 6 phần;
- vận hạn khớp mức chỉ số;
- đầu ra route.

Các test cũ được sửa có lý do: chỗ cho phép câu kết luận ledger mang danh sách luật, slot mới trong luan.json, câu he_thong của vận hạn. Golden
được sinh lại vì luật lên verified và vì có câu mới.

Số đo trên 1.000 lá corpus (`node tools/interpret/eval_synthesis.ts --n 1000`; “trước” chạy cùng công cụ trên cây e186628):

METRICS_TABLE

Barnum/strip (eval_distinct, chương Mệnh, benchmark20): trước 40,5 % / 0,058; sau BARNUM_AFTER.

## 8. Còn mở (không nhận là xong)

- **Mâu thuẫn còn lại** CONTRA_AFTER cặp, chủ yếu ở lĩnh vực tiền bạc: các cung con cái, cha mẹ, nô bộc nói về tiền của người khác (“con cái khá
  giả”), không phải tiền của đương số. Bộ đo hiện gom theo facet `finance.*`.
- **Mâu thuẫn thời điểm trong công danh** chưa được ledger giải thích riêng. Lá 2002 có “đỗ đạt sớm” (Mệnh) và “công danh đến muộn” (Thân cư Quan
  Lộc). Ledger lấy câu thứ hai làm liên kết, còn câu thứ nhất vẫn nằm trong văn Mệnh.
- **Đà La ở Phu Thê lá 2002**: bảng KL không in độ sáng ở ô này, và bảng tuvi.vn cũng không. Văn không gọi là “hãm”; Đà La được xét là sát tinh
  chưa kiểm đắc. Bản kế hoạch ghi “Đà La hãm”, nhưng dữ liệu không có căn cứ cho chữ hãm.
- Builder chưa đồng bộ với trạng thái verified mới: `build_th_palaces2_pack.py`, `build_th_aux2_pack.py`, `build_kl_stars_pack.py`, builder TT
  cung. Nếu ai chạy lại các builder này, cần đối chiếu với `rule_review_2026-10-22.json`.
- Câu Hóa Quyền/Khoa của hạn vẫn là phổ thông và bị route lọc bỏ.
- 30 luật hạn chế còn draft: muốn dùng phải siết điều kiện theo trang. Danh sách điều kiện còn thiếu nằm trong hồ sơ.
