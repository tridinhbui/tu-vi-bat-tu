# Tử Vi đọc sâu — đợt 2 (2026-10-23): không bỏ sót luận điểm, tri thức cho 7 cung mỏng, Đọc sâu cho mọi cung, liên kết cung, đại hạn

Kế hoạch: `~/.claude/plans/quirky-tinkering-rabin.md` (P0, P1 tri thức, chiều sâu, liên kết, Đại hạn). "Trước" = main `6ba6a68`; "sau" = main
sau đợt này. Nguyên tắc giữ: không mục tiêu số chữ; mọi câu = dữ kiện lá số + luật/trang sách có kiểm (hoặc lời hệ thống có nhãn); không câu
phổ thông; minh họa có nhãn, gắn đúng một câu sách; không bịa luật; không đổi engine tính toán và giao diện.

## 1. P0 — không luận điểm verified nào bị rơi im lặng

Nguyên nhân (audit đầu đợt): bộ lọc của `reason/plan.ts` (giới hạn 2–3 luận điểm, 2 claim/seat, 4 modifier; Barnum; timing không có sao dựa)
và chương rơi về đường cũ. Sửa:

| Việc | Ở đâu |
|---|---|
| Giới hạn chỉ áp cho phần chính; phần còn lại sang **Đọc sâu** theo mục | `reason/depth.ts` (mọi cung), `prose/luan_deep.ts` |
| Barnum hạ khỏi phần chính, không xóa: nói trong Đọc sâu với chỗ đứng riêng | như trên; `luanSaid` (strip/Barnum) đo phần chính |
| Luật thời điểm không có sao dựa (VCD, Thân cư) nói như đặc điểm cung | `plan.ts` timings nhận nguyên tử `vcd`/`than` |
| Luật cùng ý (khái niệm@cung) với câu đã nói trong chương: gắn làm **đồng chứng** (`trace.also`), không viết lại | `luan_deep.ts`; `evidence.rules` gồm cả đồng chứng |
| 74 luật verified không có lời đọc được (dấu `:` / ngoặc / ghi chú review): lời đọc sạch, cùng ý, bỏ chữ tuyệt đối | `engine/data/kg/rule_voice.json`, `narrative.ts splitReading` |
| Chương không còn rơi về chương cũ khi có Đọc sâu: phần chính trống → hai mục Đọc sâu đầu lên làm phần chính | `luan.ts` (`promoted`) |
| Luật một khái niệm thứ hai của cùng một luật vừa nói bằng lời sách: không lặp bằng thẻ | `narrative.ts argueThesis` |
| Luật không nói thì ghi lý do trong `evidence.untold` | `guarded`, `event`, `timing_main` (Phu Thê, quy tắc của chủ), `domain_unexplained` |
| **Mượn sao cung vô chính diệu** (TT tr.18, quyết định của chủ) | `reason/borrow.ts`: đọc lại cung VCD với chính tinh cung xung chiếu (độ sáng ở chỗ sao đứng); luật chỉ bắn khi mượn, đứng trên sao mượn → câu "Mượn … từ cung …, cung X phần nào cho thấy …", ghi chú TT tr.18 trong `trace.note`, không vào ledger/tổng hợp, sao mượn không bao giờ được viết là tọa thủ |

Gate (1.000 lá, `tools/interpret/eval_deep.ts`, nay đếm cả đồng chứng và lý do):

| Luật verified bắn ở cung mà không chương nào nói | Trước | Sau | Lý do được ghi (sau) |
|---|---|---|---|
| Mệnh | 10.972 (mọi lá) | **0** | guarded 465 (luật mà vị trí sao không đúng chữ sách — R1) |
| Quan Lộc / Tài Bạch | 8 / 256 | **0 / 0** | Tài: guarded 23 |
| Thiên Di | 728 | **0** | — |
| Phu Thê | 525 | **0** | event 278, timing_main 226 (Phu Thê không thời điểm/sự kiện trong Đọc sâu) |
| Phúc Đức / Nô Bộc / Phụ Mẫu | 425 / 154 / 318 | **0 / 0 / 0** | — |
| Điền / Tử Tức / Huynh Đệ / Tật Ách | 13 / 19 / 1 / 0 | **0** | Tật Ách: domain_unexplained 7 |

7 luật Mệnh "bắn mà không ai nói" của audit (CU_THU_MENH, HONG_LOAN, KINH_DA, PHU_MENH_CO_PHA_KINH, AUX2_MENH_MOC_DUC, SAT4_THU_MENH,
DHK_05_TY) và `TV_TH_CU_HAM_GIAN_XAO_DA_NGHI` nay nằm trong Đọc sâu Mệnh (“Thêm về tính cách / năng lực / đường đời”); một luận điểm đi ngược
một câu đã nói thì mở bằng khung “Ở chiều ngược lại / Song cũng có mặt khác”, một luận điểm mà sách đã giới hạn (reducer đã nói) thì nói ở dạng
bị giới hạn.

## 2. P1 — tri thức cho 7 cung mỏng (có trang, có kiểm)

Khai thác lại (lần trước mất): 4 luồng đọc ảnh trang, kết quả thô **commit ngay** ở `engine/data/kg/mined/` (365 mục + 116 câu bản chất/quan hệ;
mọi câu trích qua `book_text.quote_on_page`), kèm tệp nguồn từng trang `tools/mining/`.

- `engine/data/pack_cung_bay.json` (`tools/build_cung_bay_pack.py`): **122 luật verified** — Nô Bộc 21, Thiên Di 22, Phúc Đức 25, Phụ Mẫu 10,
  Tử Tức 25, Huynh Đệ 13, Tật Ách 5 (KL pp.55–220, TH pp.99–113). Câu trích lấy từ mục khai thác, kiểm bằng `engine/tests/test_cung_bay.py`
  (+ điều kiện bắn). Điều kiện không rộng hơn trang: “gặp” không ghi vị trí đọc trong cung; “lũ …” cần ≥2 sao; “đắc địa/sáng” = miếu/vượng/đắc.
  45 mục bỏ có lý do ghi trong `quotes_cung_bay.json` (`skipped`): chết/khắc/mất sớm, bệnh và mọi trạng thái sức khỏe, tù, trộm, tiếng xấu,
  tướng mạo, sinh đôi/khác cha mẹ/con nuôi/số con (sự kiện), cặp sao không thể đồng cung theo chữ in (Tham–Vũ Thìn/Tuất, Liêm–Tham Dần/Thân,
  Tử–Phá Tí/Ngọ…), câu mà trang không phân định. Tật Ách chỉ nhận điều sao **làm** ở cung (cứu giải / tối kỵ, KL tr.218, 76), không kết luận sức khỏe.
- **39 khái niệm mịn** (tách khái niệm quá thô): `ally.helpful/overstep/fickle/resent/dispute/few/powerful/slander/greedy/drain`,
  `travel.helped/gain/dispute/toil/mixed/costly`, `fortune.*` (11), `parents.*` (5), `kin.talented/prosper/wayward/filial/good/adverse`,
  `health.shielded/exposed`; thẻ đọc đầy đủ (`tools/data/cung_bay_cards.json`); 30 luật cũ đổi liên kết cho đúng nghĩa (vd. “oán chủ” →
  `ally.resent`, “cha mẹ hay bất hòa” trước là `rel.strain` của hôn nhân → `parents.strain`).
- `star_nature.json`: 58 → **95 câu bản chất**, 9 → **22 quan hệ cung** (`tools/add_star_nature_cung_bay.py`); `use` mới allies, travel,
  fortune, children, siblings, parents, health; Thái Dương = cha (KL tr.85), Thái Âm = mẹ (tr.100), Thiên Đồng chủ tể cung Phúc (tr.90), Tuần
  Triệt che cung VCD (tr.146), các sao cứu giải mạnh (tr.120), Phá Quân chủ phu thê/nô bộc/tử tức (tr.116), bảng chữ khóa tr.118… Câu bản chất
  “ở cung nào cũng …” (hao tán, cản trở, Hóa Kỵ…) được phép giải thích giới hạn của cung mới; câu khác chỉ là cấu trúc cung.

## 3. Đọc sâu cho mọi cung (bảng cấu hình)

`reason/depth.ts` + `prose/luan_deep.ts` không còn nhánh viết cứng cho 4 domain: bảng `engine/data/kg/domains.json` → `depth` (cung, `use`,
mục, ánh xạ khái niệm→mục, mục cấu trúc/giới hạn/Quyền/liên kết/kết luận, cờ `noTiming`/`noEvents`/`noVerdict`, quan hệ cung) và tiêu đề ở
`content/prose/depth.json`. Thêm Mệnh, Thiên Di, Phúc Đức, Nô Bộc, Tử Tức, Huynh Đệ, Phụ Mẫu, Tật Ách (không kết luận). Cung người khác giữ
quy tắc cùng chủ thể. Phu Thê: mục “Cách trò chuyện” nhận nhận thức/lời nói/tính khí trước nét khác của người phối ngẫu; vẫn không thời điểm/sự kiện.

Không lặp: yếu tố kích hoạt nói một lần mỗi chương; câu khẳng định đã nêu mọi yếu tố thì không thêm câu kích hoạt; nhắc lại dùng tên ngắn của
khái niệm; nền dài (>4 tên) gọi sao cung khác theo cung; độ sáng của sao không có mặt không bao giờ là chỗ đứng.

## 4. Liên kết giữa các chương

Quan hệ có trang, nói kèm phía của lá số và verdict ledger của miền liên quan: **Mệnh↔Quan Lộc** (KL tr.215 “Quan, Di, Tài ảnh hưởng nhiều
đến Mệnh” + verdict công danh), **Tài↔Điền** (tr.216 chế tài, tr.219 nhà đất), **Phu Thê↔Phúc Đức** (TH tr.96, chỉ nữ mệnh, + verdict hôn
nhân), **Thiên Di↔Nô Bộc** (KL tr.218 “Thiên Di là chỗ giao thiệp”), Phúc cứu Mệnh Thân (tr.215, chỉ khi Mệnh có sát/hãm và Phúc có sao sáng),
Mệnh–Phúc đỡ Di/Tật (tr.215, chỉ khi cung có sát), Phụ Mẫu quá đẹp thì Tật kém (tr.220, chỉ khi Phụ Mẫu sáng, không sát). Câu chung không áp
cho lá thì không nói. Đọc sâu không nói một luận điểm đi ngược phía đã nói của một miền mà ledger không có verdict có điều kiện để giải thích
(`domain_unexplained`).

## 5. Đại hạn (`prose/vanhan.ts`, `prose/vanhan_books.ts`, `engine/data/kg/van_han_books.json`)

- Câu nhập hạn Toàn Thư **pp.96–106** (trước: cụm “pp.97–105” chung, cơ sở phổ thông nên bị lọc hết): 51 câu có trang riêng (đã kiểm ảnh;
  trang Hóa Kỵ là 106, Tử Vi 96–97), điều kiện theo câu thơ, **Tứ Hóa theo can của hạn** (TT tr.105 Lộc/Quyền/Khoa), câu bổ sung Cự Môn tr.100,
  Thiên Tướng 100–101, Lương/Sát 101–102, Đà La 103, Không/Kiếp 104; bỏ chết/bệnh/tù/sinh con.
- Khảo Luận pp.233–236: chính tinh của hạn đắc/hãm, hãm có Tuần/Triệt giải; hung tinh đắc/hãm và “quan thầy” (Không Kiếp–Phá Quân, Hỏa Linh–
  Tham Lang, Kình Đà–Thất Sát); câu mở cho hạn Thất Sát/Phá Quân/Tham Lang; chặng đời theo cung và chiều hạn (thuận/nghịch).
- Hóa Quyền/Khoa của hạn (khung `hoa_qk` có sẵn, chưa dùng); TH tr.119 đại tiểu hạn trùng phùng (năm hiện tại).
- Khung đa dạng hơn (tam hợp, mức, Hóa Lộc/Kỵ, lead TT, chặng đời); không chữ “sức khỏe … thuận/vướng”.
- Phát hiện khi kiểm trang (ghi, chưa sửa code Python): `engine/tvbt/van_han_tt.py` có các điều kiện rộng hơn trang (Kình/Tham Tứ Mộ theo cung thay
  vì tuổi, Hóa Kỵ nhập miếu áp cho mọi Hóa Kỵ, Thái Dương hãm dùng HOẶC thay vì VÀ, Thiên Mã dùng HOẶC…). Văn Tử Vi không còn dùng mô-đun ấy.

## 6. Số đo (1.000 lá, trung bình mỗi chương; trước → sau)

| Chương | chữ | Đọc sâu | đơn vị | luận điểm | cơ chế | phản bác | tương tác | chữ/đơn vị | chương 0 đơn vị | lặp |
|---|---|---|---|---|---|---|---|---|---|---|
| Mệnh | 483 → 792 | 0 → 311 | 14,5 → 29,1 | 7,3 → 16,0 | 0 | 1,9 → 2,7 | 4,0 → 9,0 | 34,5 → **27,6** | 0 | 0,05 → 0,08 |
| Quan Lộc | 322 → 305 | 145 → 144 | 10,2 → 10,1 | 2,8 → 3,1 | 2,6 | 1,8 → 1,6 | 2,2 → 1,9 | 34,1 → 32,5 | 1 | 0,06 |
| Tài Bạch | 385 → 378 | 150 → 148 | 12,2 → 12,8 | 2,5 → 3,3 | 1,9 | 1,6 | 2,2 → 2,0 | 32,7 → 30,7 | 0 | 0,10 |
| Thiên Di | 155 → 283 | 0 → 116 | **4,4 → 10,5** | 2,8 → 5,3 | 0 → 1,3 | 1,2 → 1,8 | 0,4 → 2,2 | 41,0 → **28,9** | 4 → 0 | 0,02 → 0,05 |
| Phu Thê | 235 → 246 | 74 → 84 | 6,8 → 8,0 | 2,5 → 2,7 | 1,6 → 1,3 | 1,1 | 0,5 → 1,4 | 36,8 → 32,2 | 3 → 0 | 0,05 |
| Phúc Đức | 129 → 184 | 0 → 58 | **3,4 → 6,9** | 2,0 → 3,4 | 0 → 0,9 | 1,2 → 1,5 | 0,2 → 1,1 | 43,5 → **28,7** | 57 → 0 | 0,02 → 0,03 |
| Điền Trạch | 218 → 215 | 86 → 79 | 6,7 → 7,4 | 2,2 → 2,5 | 0,9 | 2,1 → 2,3 | 1,5 → 1,7 | 35,3 → 31,1 | 15 → 0 | 0,07 → 0,08 |
| Nô Bộc | 122 → 244 | 0 → 88 | **2,6 → 9,0** | 1,6 → 3,6 | 0 → 1,3 | 1,1 → 1,5 | 0 → 2,6 | 53,0 → **27,8** | 35 → 0 | 0,04 → 0,08 |
| Tử Tức | 144 → 183 | 0 → 46 | **3,9 → 6,5** | 2,0 → 3,0 | 0 → 1,2 | 1,9 → 1,8 | 0 → 0,5 | 40,1 → **30,8** | 59 → 9 | 0,05 → 0,04 |
| Huynh Đệ | 105 → 155 | 0 → 45 | **2,2 → 5,2** | 1,5 → 2,4 | 0 → 1,1 | 0,7 → 1,2 | 0 → 0,5 | 54,0 → **34,7** | 106 → 39 | 0,02 → 0,03 |
| Phụ Mẫu | 144 → 211 | 0 → 61 | **3,8 → 7,7** | 2,6 → 4,4 | 0 → 1,2 | 1,3 → 1,4 | 0 → 0,8 | 42,0 → **29,2** | 18 → 0 | 0,05 → 0,06 |
| Tật Ách | 109 → 180 | 0 → 46 | **2,5 → 5,6** | 1,3 → 2,0 | 0 → 1,0 | 1,3 → 1,6 | 0 → 1,1 | 48,1 → **35,3** | 48 → 0 | 0,09 |

Đọc: mọi chương mỏng sâu hơn **mà gọn hơn** (chữ/đơn vị giảm 9–25 chữ): phần thêm là luận điểm, cơ chế, tương tác — không phải khung. Lặp
giữa các lá khác cấu hình (trigram, bỏ tên) vẫn ≤ 0,10 (đã cắt các câu quan hệ chung không áp cho lá; thêm biến thể khung).
Tỷ lệ câu có nguồn sách (200 lá, mọi câu chương luận): sách 38,2 % → **47,5 %**, hệ thống 23,2 % → 16,5 %, tính toán 25,2 % → 24,4 %,
minh họa 8,0 % → 7,4 %, lời khuyên 5,5 % → 4,2 %; câu kết luận có luật đi kèm 98,7 % → 98,8 %.

Lá cổng (đơn vị, trước → sau; số chữ trong ngoặc):

| Lá | Mệnh | Quan | Tài | Di | Phối | Phúc | Điền | Nô | Tử | Bào | Phụ | Tật |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2002 | 19→36 | 9→14 | 12→12 | 2→7 | 12→13 | 2→9 | 10→11 | **1→7** (32→196) | 4→5 | 4→7 | 2→5 | 4→6 |
| 1911 | 13→26 | 10→13 | 10→9 | 9→11 | 5→5 | 5→12 | 0→4 | 1→3 | 2→6 | 5→6 | 2→7 | 3→3 |
| 1971 | 13→22 | 11→11 | 15→14 | 2→7 | 4→4 | 5→14 | 13→12 | 2→9 | 4→5 | 2→3 | 3→7 | 4→7 |

Văn trước/sau đầy đủ (mọi chương + đại hạn) của ba lá: [docs/examples/deep-tuvi-2-truoc-sau.md](../examples/deep-tuvi-2-truoc-sau.md).

## 7. Cổng chất lượng

`eval_synthesis.ts --n 1000`: luận điểm lớn một sao **0**, yếu tố hạn chế không đối diện **0** / 13.816, mâu thuẫn chưa giải thích **0**, verdict
khác nhau **0**, lỗi chặn **0**. `readable.test` (không chữ phương pháp; câu TB ≤ 23 chữ, ≤ 5 % quá 35 chữ; Barnum/strip phần chính Mệnh
benchmark20 ≤ 40,55 % / 0,0655): xanh. `positions_text` (sao mượn/chiếu/hội viết đúng; 400 lá): xanh. `validate`, `pytest` (1.797 passed),
`test:auth` 94/94, `node --test src/interpret/test` 233/233, parity TS↔Python sau refire. Các lá tham chiếu: golden cập nhật sau khi đọc lại.

## 8. Khoảng trống, chưa làm

- **Mệnh và Thân so với sao hạn** (KL tr.234: so cả sao Mệnh **và Thân**): luật VH_* (Python) mới so Mệnh; chưa thêm vế Thân.
- **TH tr.114** lưu Khốc Hư (đã có trong chỉ số `indices.ts`), lưu Mã gặp lưu Tuần/Triệt (cần vị trí lưu Tuần/Triệt — chưa tính); **TH tr.119**
  “tuổi kỵ năm” (TT tr.106 chính tác giả coi là lời giang hồ) chưa nói.
- Đuôi luật `van_han_rules.json` bị khung cắt (vd. `{sat_in}`, `{good}`) chưa khôi phục.
- `van_han_tt.py` (Python) giữ điều kiện cũ; văn Tử Vi không dùng nữa, nhưng API facts vẫn trả `decades[].tt`.
- Tri thức còn mỏng thật: Huynh Đệ (39/1.000 chương 0 đơn vị), Tử Tức (9) — sách nói về số anh em/con, sinh đôi, khác cha mẹ (đều là sự kiện,
  không nói). 45 mục khai thác bị bỏ có lý do (`quotes_cung_bay.json`), một số chờ chủ dự án quyết (đọc “Ngoài vị trí Dần Thân” KL tr.113;
  tai nạn có tính là sức khỏe không).
- Sao mượn: luật có position guard không đọc trên sao mượn; luật bắn cả trong lá thật và lá mượn chỉ tính một lần (lá thật).
- `luanSaid` (strip/Barnum) đo phần chính; Đọc sâu theo thiết kế chứa câu phổ biến bị hạ — đo riêng ở bảng §6.
