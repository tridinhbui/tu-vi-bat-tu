> Evidence file of the 2026-10-18 interpretation-engine audit (read-only sub-audit, consolidated in ../INTERPRETATION-ENGINE-AUDIT.md). Paths under `scratchpad/` refer to the auditing session's temporary folder and are not in the repository. Statuses here are as found on 6c10cf5, BEFORE the fixes; see the consolidated audit for what was fixed.

# Tử Vi chart-calculation audit (read-only)

Worktree: `.claude/worktrees/interp-engine-audit` (branch `feat/interp-engine-audit`, HEAD 6c10cf5). No repo files edited.
Method: ran `tvbt.tuvi.compute`, `temporal.tuvi_year` and `reasoning.temporal_facts.layered` on the reference chart and on edge cases. Hand-derived every placement from the code formulas. Compared formulas with KL (Khảo Luận), TH (Thực Hành) and TT (Toàn Thư), using the decoded text layer. Every TH verse was checked against its page image (TH pp.19, 20, 22, 24, 26, 29, 31, 33, 34, 35; KL p.29).
Baseline: `pytest tests/test_book_golden.py test_aux_stars_cach_cuc.py test_tuvi.py test_van_han.py test_tu_hoa_tables.py` gives 45 passed.
The in-progress `dignity_aux.json` in the main checkout was not considered.

Page notation: "KL p.28" is the printed page, which equals the PDF page for all three books.

---

## 1. Issues

### TV-1 · P0 · Thiên Quý is counted in the wrong direction (wrong cung on about 25 of 30 birth days)
- **Root cause:** `engine/tvbt/aux_stars.py:70`, `add("Thiên Quý", placed["Văn Khúc"] + day - 2, ...)`. This counts **thuận** from Văn Khúc.
- **Evidence:** Both books count **nghịch**:
  - TH p.19 (page image): the verse says Thiên Quý takes Khúc and counts "nghịch về ngày đẻ, một cung lùi"; the cước repeats "tính nghịch đến ngày đẻ rồi cũng lùi lại 1 cung".
  - KL p.28: "Thiên quí: Khởi từ cung có Văn khúc… đếm nghịch đến ngày sinh… lùi lại một cung".
  - In both books Thiên Quý is the mirror image of Ân Quang, the same way Bát Tọa mirrors Tam Thai. The mirror holds because Xương + Khúc ≡ 2 (mod 12).
- **Reference chart:** the code puts Thiên Quý at **Ngọ (Thiên Di)**. The book puts it at **Tý (Mệnh)**: Khúc Dậu, counted nghịch 23 days, gives Hợi, and stepping back one gives Tý. That is also the mirror of Ân Quang at Dần.
- **Coverage:** the code is right only when 2·day ≡ 4 (mod 12), i.e. days 2, 8, 14, 20, 26. No test covers Thiên Quý or Ân Quang.
- **Fix:** `placed["Văn Khúc"] - (day - 2)`. Add a golden test for the mirror property, `(AnQuang + ThienQuy) % 12 == 2`, plus the reference value (Tý).
- **Ambiguity:** one minority reading takes "lùi" as counter-clockwise, giving Khúc − day (Hợi here). Either reading differs from the code. The mirror reading is supported by the book's symmetric diagrams (KL p.28).
- **Status:** source-supported.

### TV-2 · P1 · Lưu Hà table matches neither book (Canh, Đinh, Tân)
- **Root cause:** `aux_stars.py:24`, `LUU_HA = {…, 3: 8 (Đinh Thân), 6: 4 (Canh Thìn), 7: 3 (Tân Mão), …}`.
- **Evidence:**
  - KL p.29 (page image, table plus prose example "tuổi Canh tại cung Mão"): Đinh Thân, **Canh Mão, Tân Thìn**.
  - TH p.26 (page image, verse "37> Lưu Hà – Thiên Trù", first branch of each pair): **Đinh Thìn, Canh Thân, Tân Mão**.
  - The two books agree on the other 7 stems.
  - The code has Đinh from KL, Tân from TH, and Canh from neither.
- **Reference chart:** the code puts Lưu Hà at Thìn (Quan Lộc). KL gives Mão (Điền Trạch); TH gives Thân (Tài Bạch).
- **Fix:** choose one book per school, mark the three stems as disputed, and add a golden test from KL p.29.
- **Status:** source-supported. The choice of school is a decision.

### TV-3 · P1 · Thái Dương and other chính tinh brightness: KL has a complete "Thế đứng" table that is missing from the repo and disagrees with TH on 7 of 14 star cells in the reference chart
- **Root cause:** `dignity.py:12` offers only `thuc_hanh` (TH) and `toan_thu` (TT). The note in `dignity_vn.json` lists only Tham Lang Tý/Ngọ as disputed.
- **Evidence (KL brightness tables, "Thế đứng của …"):**
  - Tử Vi: p.75
  - Thiên Cơ: p.79
  - Thái Dương: pp.82-83, which gives miếu Tỵ Ngọ, vượng Dần Mão Thìn, **đắc Sửu Mùi**, hãm Thân Dậu Tuất Hợi. KL p.85 repeats "đắc địa ở những cung ban ngày (Sửu, Dần, Mão, Thìn, Tỵ, Ngọ)".
  - Vũ Khúc: p.87, which gives miếu Thìn Tuất Sửu Mùi, **vượng Dần Thân Tý Ngọ**, đắc Mão Dậu, hãm Tỵ Hợi.
  - Thiên Đồng: p.89
  - Liêm Trinh: p.92
  - Thiên Phủ: p.95
  - Thái Âm: p.98
  - Tham Lang: p.101
  - Cự Môn: p.104
  - Thiên Tướng: p.107
  - Thiên Lương: p.109
  - Thất Sát: p.112
  - Phá Quân: p.115

**Reference-chart cells, by school:**

| Cell | TH (production) | KL | TT |
|---|---|---|---|
| Thái Dương Sửu | **hãm** (TH p.31, image) | **đắc** (KL pp.83, 85) | – |
| Thái Âm Sửu | miếu | bình | – |
| Vũ Khúc Tý | none (TH p.34 prose only) | **vượng** | vượng |
| Thiên Phủ Tý | vượng | miếu | miếu |
| Tham Lang Dần | đắc | vượng | – |
| Thiên Cơ Mão | vượng | miếu | – |
| Liêm Trinh Thân | miếu | vượng | – |
| Thiên Đồng Hợi | miếu | bình | – |
| Tử Vi Thìn | vượng | vượng | vượng |
| Cự Môn Mão | miếu | miếu | – |
| Thiên Tướng Thìn | vượng | vượng | – |
| Thất Sát Ngọ | miếu | miếu | – |
| Phá Quân Tuất | đắc | đắc | – |
| Thiên Lương Tỵ | hãm | hãm | – |

- **Mixed schools:** production also uses a *KL* Tứ Hóa table (Nhâm Khoa = Tả Phụ) together with a *TH* brightness table.
- **Fix:** transcribe KL pp.74-115 into `dignity_kl.json` (image-checked) as a third school. Disclose the per-cell disagreements in the UI next to each brightness label. Keep the default as it is until the user decides.
- **Status:** source-supported. The default school is a decision.

### TV-4 · P1 · Canh Tứ Hóa dispute not disclosed in the UI
- **Production:** Canh = Nhật Lộc, Vũ Quyền, **Đồng Khoa, Âm Kỵ** (`tuvi.py:75`).
- **Books:** both repo books agree on this:
  - KL p.36 table
  - TH p.20 verse "Canh: Nhật, Vũ, Đồng, Âm" (image) and p.21 prose
  - golden test `test_tu_hoa_canh_both_books`
- **The variant:** **Âm Khoa / Đồng Kỵ** (庚：日武陰同) is recorded in `data/experimental/tu_hoa_tables.json` from the digitized 紫微斗數全書 (external source). From general knowledge it is also the table of many popular Vietnamese charting sites. That second claim is NOT in the three books, so it NEEDS SOURCE.
- **UI:** shows nothing about the dispute. `grep Canh web/js/tuvi.js` finds no hit. `scope.js` only mentions Tuần/Triệt variants.
- **Reference chart:** the dispute swaps Hóa Khoa and Hóa Kỵ between Huynh Đệ (Thiên Đồng, Hợi) and Phụ Mẫu (Thái Âm, Sửu).
- **Fix:** add a per-chart disclosure for Canh and Nhâm years, e.g. "Bảng Tứ Hóa theo KL/TH; một số bản (全書) ghi Canh: Âm Khoa, Đồng Kỵ". Wire the existing `tu_hoa_tables.json` behind an explicit parameter, as its own note proposes.
- **Status:** the production table is source-supported. The external variant NEEDS SOURCE inside the three books.

### TV-5 · P1 · Nhâm Tứ Hóa: the project's own two books disagree, and the UI does not say so
- **The disagreement:**
  - Production `tuvi.py:77` follows KL p.36 / p.197: Nhâm Khoa = **Tả Phụ**.
  - TH p.20 (verse, image: "Lương, Tử, Phủ, Vũ") and TH p.21 (prose) give **Thiên Phủ**.
- **Where it is documented:** `SCHOOL_PACK` (tuvi.py:48) and the dossier.
- **Where it surfaces:** only in the flagged synthesis (`synthesis/compose.py:226`, "tuổi Nhâm phụ thuộc R05"). It is not in the chart UI.
- **Fix:** same as TV-4 (shared disclosure).
- **Status:** source-supported; the choice is a decision.

### TV-6 · P1 · Tiểu hạn direction: KL disagrees with TH, undisclosed (affects every âm-stem birth)
- **Code:** `temporal.py:88-90` and `reasoning/temporal_facts.py:21-23` use TH p.27: nam thuận, nữ nghịch.
- **KL pp.39-40:** dương nam / âm nữ thuận, âm nam / dương nữ nghịch. KL says explicitly that many books still use nam thuận, nữ nghịch, and leaves the choice to the reader.
- **Who is affected:** dương-stem births agree under both books. Âm nam and âm nữ get different palaces.
  - Example: 1991 Tân Mùi male, year 2026. TH gives Tý; KL gives Dần.
- **Reference chart:** unaffected (dương nam).
- **Fix:** add a disclosure, and optionally a `tieu_han_rule` option.
- **Status:** source-supported (both pages).

### TV-7 · P1 · "Lưu Tứ Hóa theo sách" applies birth-year advice to the flow year
- **Root cause:** `temporal.py:94-101` takes `tu_hoa_vi.json` advice for the **flow-year** stem and cites "Khảo Luận pp.195-197". The UI shows it under "Lưu Tứ Hóa theo sách" (`web/js/tuvi.js:215`).
- **Evidence:** KL pp.195-197 describes the natal Tứ Hóa of a person *born* in each stem ("Tuổi Giáp … tuổi Giáp phải liều lĩnh như Phá quân…"). It says nothing about a flowing year.
- **Wider gap:** none of the three books gives a lưu Tứ Hóa rule. KL's list of nine "sao lưu động" (pp.41-42) has no lưu Tứ Hóa.
- **What is solid:** the positions (year stem through the natal table) are a common convention, but they are unsourced in the repo.
- **Fix:** re-label the positions as "quy ước phổ biến, chưa có trong ba sách". Remove the "theo sách" label and the KL citation from the per-year advice, or reword it as natal-stem meaning.
- **Status:** NEEDS SOURCE for lưu Tứ Hóa.

### TV-8 · P1 · UI cát/hung counts are unsourced and mostly built on "unverified" placements
- **Where the counts come from:** `web/js/util.js:43-45` (POS/NEG sets, no citation) feeds `insights.js:41,49` ("Phụ tinh cát: 8 · sát/hung tinh: 15"), `report.js:188-203` and `tuvi.js:36,80,121-128`.
- **Reference-chart Mệnh tam phương (Tý, Ngọ, Thìn, Thân), cát 8:**
  - Thiên Khôi and Lộc Tồn are verified.
  - Thiên Phúc, Thiên Tài, Thiên Quý (wrong cung, TV-1), Phượng Các, Thiên Thọ and Thiên Y are from the unverified group.
  - So 6 of 8 come from the unverified group.
- **Hung 15:**
  - Hỏa Tinh, Địa Không, Địa Kiếp, Phục Binh, Bệnh Phù, Điếu Khách and Tang Môn come from verified tables.
  - Thiên Khốc, Thiên Hư, Thiên Hình, Quả Tú, Cô Thần, Thiên La, Thiên Riêu and Lưu Hà (disputed, TV-2) are unverified.
  - So 8 of 15 come from the unverified group.
- **Comparison with analysis.py:** `analysis.py:16-17` uses only Lục cát and Lục sát (CAT/SAT, consistent with TH p.29 "Tứ Sát"). The UI and the analysis therefore count different things.
- **Classification versus the book:** TH pp.18-26 does group stars into a "Cát tinh" block (items 3-25) and a "XẾP LOẠI HUNG TINH" block (items 26-39, image p.24), and the book stresses that the grouping only serves the layout (TH p.19, p.23). util.js contradicts that grouping in places:
  - Thiên Y is in TH's hung block (with Hình, Diêu) but is POS in code.
  - Đẩu Quân is in TH's hung block but neutral in code.
  - Thiên Mã and Đào Hoa are in TH's cát block but neutral in code.
- **Internal inconsistencies in util.js:**
  - Only Thanh Long is POS in the Bác Sĩ ring; Bác Sĩ, Hỷ Thần and Tấu Thư are neutral.
  - Phúc Đức is POS but Long Đức is neutral, and Tuế Phá is neutral.
  - "Thái Phụ" is a misspelling of Thai Phụ, which is not placed anyway.
- **Fix:** (a) count only stars whose placement is verified, or show the unverified count separately; (b) source the sets from TH pp.18-26 (cite the page) or say "phân loại sắp xếp theo thông lệ"; (c) align the UI with analysis.py's CAT/SAT.
- **Status:** partly source-supported (TH grouping). The rest NEEDS SOURCE.

### TV-9 · P2 · About 30 "unverified" aux formulas are in fact printed in KL pp.26-32, 36 and TH pp.19-27; Quốc Ấn, Đường Phù, Thai Phụ, Phong Cáo and Giải Thần could be placed
- **Where the label is:** `tuvi.py:52` (`aux_stars: unverified, chưa đối chiếu trang sách`), `aux_stars.py:1-6,13`. `tests/test_aux_stars_cach_cuc.py:23-24` asserts the label.
- **What the books say:** every formula in `aux_stars.py` except TV-1 and TV-2 matches **both** books (see the registry). Both books also give formulas for the five unplaced stars, and they agree:
  - **Quốc Ấn** = Lộc Tồn + 8: TH p.22 "trước Lộc Tồn 9 vị"; KL p.29 "đếm nghịch đến 5".
  - **Đường Phù** = Lộc Tồn + 5: TH p.22 "nghịch lại 8 cung"; KL p.29 "thuận đến 6".
  - **Thai Phụ** = Khúc + 2 and **Phong Cáo** = Khúc − 2: TH p.19; KL p.27.
  - **Giải Thần** sits with Phượng Các: TH p.20; KL p.31.
- **Worked examples usable as golden tests:**
  - KL pp.30-32, Ất Mão year: Long Trì and Phượng Các at Mùi, Hoa Cái Mùi, Hồng Loan Tý, Đào Hoa Tý, Thiên Mã Tỵ, Quả Tú Sửu, Khốc Mão, Hư Dậu, Nguyệt Đức Thân, Kiếp Sát Thân, Phá Toái Tỵ.
  - TH p.24, Mùi year with Mệnh Thìn and Thân Tuất: Thiên Đức Thìn, Nguyệt Đức Tý, Thiên Tài Hợi, Thiên Thọ Tỵ. Born in month 5: Thiên Giải Tý, Địa Giải Hợi.
  - TH p.25: born in month 6 gives Thiên Hình Dần and Riêu/Y Ngọ. A Dần year gives Khốc Thìn and Hư Thân.
- **Stale message:** `aux_stars.NOT_PLACED` says the formulas are "chưa chắc công thức", which is wrong. It also says lưu Lộc, Kình, Đà and Mã are not placed, while `temporal_facts.luu_tinh` places them in the experimental layer.
- **Fix:** cite these pages per star, move the stars to verified, place the 5 missing stars, and add the golden tests above.
- **Status:** source-supported.

### TV-10 · P2 · Lưu Kình/Đà ignore KL's direction rule; lưu Khôi/Việt unsourced (experimental only)
- **Code:** `reasoning/temporal_facts.py:34-45` always puts Lưu Kình at Lưu Lộc Tồn + 1 and Lưu Đà at − 1.
- **KL p.42:** Lưu Kình goes before (thuận) for dương nam / âm nữ, and the other way round for âm nam / dương nữ.
- **Lưu Khôi/Việt:** not among KL's nine lưu stars (pp.41-42).
- **Sourced but missing:** Lưu Tang Môn (Thái Tuế + 2) and Lưu Bạch Hổ (opposite), Lưu Khốc and Lưu Hư (KL p.41).
- **Exposure:** only through `/api/year?experimental` and the flagged synthesis.
- **Fix:** apply the direction rule, drop or label lưu Khôi/Việt, and add the KL lưu stars if needed.
- **Status:** source-supported.

### TV-11 · P2 · Đại hạn (decade) Tứ Hóa has no source but is presented as verified in the flagged synthesis
- **Code:**
  - `reasoning/temporal_facts.py:56,62`: experimental, carries a warning, acceptable.
  - `synthesis/compose.py:204-228` and `synthesis/chapters.py:411-421`: text "bốn hóa theo can … đáp xuống …", with `verification: "phần tính vị trí đã đối chiếu (Thực Hành p.27)"`.
- **Evidence:** p.27 covers only the đại hạn ages and direction. None of KL, TH or TT has a decade-stem Tứ Hóa (searched "can cung", "tứ hóa đại", "hóa đại hạn").
- **Fix:** label it "quy ước Phi Hóa / tam hợp phái, chưa có trong ba sách". The feature is behind TVBT_DEEP_INTERPRETATION, which is off.
- **Status:** NEEDS SOURCE.

### TV-12 · P2 · Trường Sinh school variant not disclosed
- **Code:** `tuvi.py:87,253-255` starts at tứ sinh for every chart, as in TH p.22. KL pp.33-34 also chooses this school.
- **The other school:** KL pp.33-34 documents it: âm nam and dương nữ start at tứ chính, so that Mộ always falls in tứ mộ. KL says "Mọi người chưa thống nhất".
- **Fix:** add a disclosure line.
- **Status:** source-supported.

### TV-13 · P2 · Leap-month citation is out of context
- **Code:** `tuvi.py:26,55` cites KL p.41 for natal birth-month handling (`same_month`).
- **Evidence:** KL p.41's sentence ("năm Quí Mùi có hai tháng Năm (nhuận), chúng tôi vẫn coi cả hai tháng đều là tháng Năm") sits inside **NGUYỆT VẬN** (monthly luck). It is not about placing Mệnh or Thân. No natal leap-month rule was found in KL, TH or TT.
- **Behaviour today:** the API cannot choose a rule (`leap_rule` is not in BirthReq), but it does warn.
- **Edge-case runs:**
  - 2020-06-15 (24/4 nhuận): same_month gives Mệnh Tý; split_15 and next_month give Mệnh Sửu.
  - 2020-06-01 (10/4 nhuận): same_month and split_15 give Tý; next_month gives Sửu.
- **Fix:** re-word the citation as "KL p.41 (về nguyệt vận) — áp dụng tương tự cho tháng sinh là suy diễn".
- **Status:** NEEDS SOURCE for the natal rule.

### TV-14 · P2 · Default hour mapping vs TH pp.4-5 seasonal hour table
- **Code:** `tuvi.py:179` uses fixed civil 2-hour blocks (Tý = 23:00-00:59), as in KL p.269. True solar time is opt-in only (`use_true_solar_time`).
- **TH pp.4-5:** the hour table shifts with the month and with the 1968 clock. For example, Tý is 01:10-03:19 in months 1 and 9 and 02:20-04:19 in month 5. That table effectively uses local solar time.
- **Reference chart:** unaffected. True solar time is about 10:40, still Tỵ.
- **Note:** TT and KL do not say which day 23:xx belongs to. The default `early_zi_next_day` (calendar_core.py:106) moves the lunar day, and at Tết eve the lunar **year**: 2021-02-11 23:30 female gives Tân Sửu and Mệnh Dần under early_zi_next_day, but Canh Tý and Mệnh Sửu under late_zi_same_day.
- **Fix:** disclose both conventions on charts born at 23:xx.
- **Status:** NEEDS SOURCE for the 23h convention.

### TV-15 · P2 · Aux brightness silently mixes schools
- **Code:** `dignity.py:50-54` with `tuvi.py:297`. Under the default `thuc_hanh`, Kình, Đà and Hỏa brightness fall back to TT (TT pp.50-52), with no per-cell source label in `minor_dignity`.
- **Reference chart:** Hỏa miếu Ngọ, Đà miếu Mùi and Kình hãm Dậu are TT values shown under the TH school.
- **Missing tables:** none for Linh, Không, Kiếp, Khôi, Việt or Lộc Tồn.
- **Note:** this is being reworked in the main checkout (dignity_aux.json), which is outside this audit.
- **Status:** a policy item.

### TV-16 · P2 · Minor code hygiene
- `tuvi.py:5-7`: the module docstring says brightness, tiểu hạn and lưu niên are not implemented. That is stale.
- `tuvi.py:215`: no-op ternary, `L.day if … else L.day`.
- `aux_stars.py:1-6`: says "no interpretation rule consumes these stars". That is true for packs, but `synthesis/structures.py:207-212` reads Thiên Hình. The Thiên Hình formula is correct per KL p.26 and TH p.25.
- `van_han_tt.py:41`: the Tử Vi "thế đẹp, nhiều sao tốt" sentence fires whenever Tử Vi is present, with no brightness or companion check. This is interpretation and outside calculation scope; noted for completeness.

### TV-17 · P2 · Mệnh chủ / Thân chủ unsourced; one UI view hides the label
- **Code:** `cach_cuc.py:12-23`. The tables match the common convention: Mệnh chủ by Mệnh branch (Tý Tham Lang, Sửu/Hợi Cự Môn, Dần/Tuất Lộc Tồn, Mão/Dậu Văn Khúc, Thìn/Thân Liêm Trinh, Tỵ/Mùi Vũ Khúc, Ngọ Phá Quân); Thân chủ by year branch (Tý Linh, Ngọ Hỏa, Sửu/Mùi Tướng, Dần/Thân Lương, Mão/Dậu Đồng, Thìn/Tuất Xương, Tỵ/Hợi Cơ).
- **Evidence:** no table in KL, TH or TT (searched "Mệnh chủ" / "Thân chủ"). Both are correctly marked `review: unverified`.
- **UI:** `report.js:213` shows "chưa đối chiếu sách", but `tuvi.js:58` shows Mệnh chủ / Thân chủ with no label.
- **Status:** NEEDS SOURCE.

---

## 2. Aux-star registry

Columns: formula in code (file:line) · source and page · golden test · positional notes in sources · brightness table in repo (source) · rules using the star · UI class (util.js:43-44), and whether that class is sourced.
"Both" means KL and TH print the same formula. "TH-grp" means the star's block in the TH pp.18-26 layout grouping (cát = items 3-25, hung = items 26-39).

| Star(s) | Formula (code) | Source / page | Golden test | Positional notes in sources | Brightness table (repo) | Used by rules? | UI class / sourced? |
|---|---|---|---|---|---|---|---|
| Tả Phụ / Hữu Bật | tuvi.py:227-228 (Thìn+m−1 / Tuất−(m−1)) | Both: KL p.26, TH p.19 | test_book_examples (book charts), oracle_tuvi_independent | Tứ mộ đắc (TH p.51) | dignity_aux_th.json (TH p.51) | yes (many packs) | cát / TH-grp cát ✓ |
| Văn Xương / Văn Khúc | tuvi.py:229-230 | Both: KL p.27, TH p.19 | test_book_examples, oracle | Ngọ Tuất hãm, etc. | aux_th (TH p.50), minor (TT pp.41,43) | yes | cát / ✓ |
| Thiên Khôi / Việt | tuvi.py:238-239, KHOI_VIET:66 | Both: KL p.30, TH p.19 (Canh Tân Ngọ Dần) | test_khoi_viet_verse_p19 | – | NONE | yes | cát / ✓ |
| Lộc Tồn | tuvi.py:232, LOC_TON:65 | Both: KL p.28, TH p.21 | test_loc_ton_kinh_da_p24 | – | NONE | yes | cát / ✓ |
| Thiên Mã (by year) | tuvi.py:241 | Both: KL pp.31-32, TH p.21 | test_year_branch_stars_pp21_23 | Tỵ Dần đắc (TH p.52) | aux_th (TH p.52; only Tỵ, Dần) | yes | **neutral** / TH-grp cát → mismatch |
| Kình Dương / Đà La | tuvi.py:233-234 | Both: KL p.29, TH p.24 | test_loc_ton_kinh_da_p24 | Tứ mộ miếu (TT) | minor (TT pp.50-51) only, fallback under TH (TV-15) | yes | hung / ✓ |
| Hỏa / Linh | tuvi.py:242-243, HOA_START/LINH_START:88-89 | Both: KL p.27 (table), TH p.25 (direction by âm dương nam nữ) | test_hoa_linh_p25 (male and female) | Hỏa: Dần Ngọ Tuất miếu (TT) | Hỏa: minor (TT p.52). Linh: NONE | yes | hung / ✓ |
| Địa Không / Kiếp | tuvi.py:244-245 | Both: KL p.27, TH p.24-25 | test_dia_kiep_khong_p24_25 | – | NONE | yes | hung / ✓ |
| Thiên Không | tuvi.py:250 (Thái Tuế + 1) | Both: KL p.30, TH p.25 | test_year_branch_stars_pp21_23 | – | NONE | yes | hung / ✓ |
| Đào Hoa / Hồng Loan / Thiên Hỷ | tuvi.py:246-249 | Both: KL p.31, TH p.23 (TH's Mùi example contradicts its own rule; KL's Ất Mão example gives Hồng Loan Tý, consistent with the rule) | test_year_branch_stars_pp21_23 | – | NONE | yes | Hồng, Hỷ cát; **Đào neutral** (TH-grp cát) |
| Thiên Khốc / Hư | aux_stars.py:38-39 | Both: KL p.32, TH p.25 | none (self-test only: test_sample_positions_1990, mirror test) | Hư sits with Tuế Phá (KL p.32) | NONE | no | hung / TH-grp hung ✓ |
| Thiên Hình / Thiên Riêu (Diêu) / Thiên Y | aux_stars.py:53-55 | Both: KL p.26, TH p.25 | none (self-test) | – | NONE | Thiên Hình: synthesis/structures.py:211 | Hình, Riêu hung; **Y cát** but TH-grp hung → mismatch |
| Cô Thần / Quả Tú | aux_stars.py:42-44 | Both: KL p.32, TH p.25 | none (self-test) | Cô always tứ sinh, Quả tứ mộ (KL p.32) | NONE | no (BaZi shensha.json is a separate system) | hung / TH-grp hung ✓ |
| Thiên Đức / Nguyệt Đức | aux_stars.py:64-65 | Both: KL pp.30-31 (Thiên Đức with Phúc Đức of the Thái Tuế ring), TH p.24 | none | – | NONE | no | cát / TH-grp cát ✓ |
| Long Trì / Phượng Các | aux_stars.py:40-41 | Both: KL p.31, TH p.20 | none (self-test) | – | NONE | no | cát / TH-grp cát ✓ |
| Tam Thai / Bát Tọa | aux_stars.py:67-68 | Both: KL pp.27-28, TH pp.19-20 | none | mirror pair | NONE | no | cát / ✓ |
| Ân Quang / Thiên Quý | aux_stars.py:69-70 | Both: KL p.28, TH p.19. **Thiên Quý formula WRONG (TV-1)** | none | mirror pair | NONE | no | cát / ✓ |
| Thiên Quan / Thiên Phúc | aux_stars.py:22-23,45-46 | Both: KL p.29 table, TH pp.23-24 (all 10 stems match code) | none | – | NONE | no | cát / TH-grp cát ✓ |
| Hoa Cái | aux_stars.py:30,60 | Both: KL p.31, TH p.23 | none | always tứ mộ | NONE | no | cát / TH-grp cát ✓ |
| Thiên Giải / Địa Giải | aux_stars.py:56-57 | Both: KL p.26, TH p.24 | none | – | NONE | no | cát / TH-grp cát ✓ |
| Giải Thần | NOT PLACED | Both: sits with Phượng Các (KL p.31, TH p.20) | – | – | NONE | no | cát (unused) |
| Lưu Hà | aux_stars.py:24,63 | KL p.29 vs TH p.26 **disagree (TV-2); code matches neither** | none | – | NONE | no | hung / TH-grp hung ✓ |
| Kiếp Sát | aux_stars.py:31,61 | Both: KL p.31, TH p.26 | none | always tứ sinh | NONE | no | hung / ✓ |
| Phá Toái | aux_stars.py:62 | Both: KL p.31, TH p.26 | none | always Tỵ, Dậu or Sửu | NONE | no | hung / ✓ |
| Thiên Thương / Thiên Sứ | aux_stars.py:49-50 (Nô Bộc / Tật Ách) | Both: KL p.36, TH p.26 (no gender variant in these books) | none (self-test) | fixed palaces | NONE | no | hung / TH-grp hung ✓ |
| Thiên La / Địa Võng | aux_stars.py:51-52 | KL p.36 | none (self-test) | fixed Thìn / Tuất | NONE | no | hung / not in TH list |
| Đẩu Quân | aux_stars.py:58 | Both: KL p.32 ("tiểu Thái tuế"), TH p.25 ("Nguyệt tướng") | none | – | NONE | no | **neutral** / TH-grp hung → mismatch |
| Thiên Tài / Thiên Thọ | aux_stars.py:47-48 | Both: KL p.32, TH p.24 (worked example) | none | KL p.195 (meaning) | NONE | no | cát / TH-grp cát ✓ |
| Quốc Ấn | NOT PLACED | Both: Lộc Tồn + 8 (KL p.29, TH p.22) | – | – | NONE | no | cát (unused) |
| Đường Phù | NOT PLACED | Both: Lộc Tồn + 5 (KL p.29, TH p.22) | – | – | NONE | no | cát (unused) |
| Phong Cáo (and Thai Phụ) | NOT PLACED | Both: Khúc − 2 / Khúc + 2 (KL p.27, TH p.19) | – | – | NONE | no | cát; util.js spells "Thái Phụ" (typo) |

No aux brightness table was invented. Every "NONE" in the brightness column is a real gap in the repo; KL and TH have prose for some of these stars (e.g. Kình tứ mộ).

---

## 3. Items verified CORRECT (with evidence)

**Reference chart** (17/05/1990 10:30, male, HCMC). Every value below was hand-derived and matches the output.

- **Calendar:** lunar date 23/4 Canh Ngọ. Hour 10:30 is Tỵ (hb = 5).
- **Mệnh / Thân:** Mệnh = Dần + 3 − 5 = **Tý**; Thân = Dần + 3 + 5 = **Tuất** (Phu Thê). Formula: KL p.18, TH p.12 (golden `test_menh_worked_example_p12`), TH p.27.
- **Cục:** ngũ hổ độn for Canh starts Dần at Mậu, so Tý is Mậu Tý, nạp âm Tích Lịch Hỏa: **Hỏa lục cục** (golden `test_cuc_table_p12`).
- **Bản mệnh:** Lộ Bàng Thổ, as on the landing mock.
- **Tử Vi:** day 23, cục 6, pad 1, quotient 4, giving **Thìn** (worked examples TH pp.14, 17 and KL p.24). The 14 chính tinh then follow:
  - Cơ Mão, Dương Sửu, Vũ Tý, Đồng Hợi, Liêm Thân.
  - Phủ Tý (mirrored on the Dần–Thân axis), Âm Sửu, Tham Dần, Cự Mão, Tướng Thìn, Lương Tỵ, Sát Ngọ, Phá Tuất.
  - Sources: KL pp.24-25.
- **Core aux stars:**
  - Tả, Hữu Mùi; Xương Tỵ; Khúc Dậu.
  - Lộc Tồn Thân; Kình Dậu; Đà Mùi; Khôi Ngọ; Việt Dần.
  - Mã Thân; Hỏa Ngọ (Sửu + 5, thuận); Linh Tuất (Mão − 5, nghịch).
  - Kiếp Thìn; Không Ngọ.
  - Đào Mão; Hồng Dậu; Hỷ Mão; Thiên Không Mùi.
- **Aux formulas checked against KL and TH:**
  - Khốc, Hư Tý; Long Tuất; Phượng Thìn; Cô Thân; Quả Thìn.
  - Quan Hợi; Phúc Ngọ; Tài Ngọ; Thọ Thìn.
  - Thương Tỵ (Nô Bộc); Sứ Mùi (Tật Ách); La Thìn; Võng Tuất.
  - Hình Tý; Riêu, Y Thìn; Thiên Giải Hợi; Địa Giải Tuất; Đẩu Quân Thân.
  - Hoa Cái Tuất; Kiếp Sát Hợi; Phá Toái Tỵ.
  - Thiên Đức Mão; Nguyệt Đức Hợi.
  - Tam Thai Tỵ; Bát Tọa Dậu; Ân Quang Dần.
  - Only **Thiên Quý (TV-1)** and **Lưu Hà (TV-2)** are wrong.
- **Tuần / Triệt:**
  - Tuần **Tuất, Hợi** (Giáp Tý xun): KL p.35, TH p.20.
  - Triệt **Ngọ, Mùi** (Ất/Canh): KL pp.34-35, TH p.20.
- **Rings:**
  - Trường Sinh for Hỏa cục starts at Dần, thuận for dương nam (Đế Vượng Ngọ, Mộ Tuất): TH p.22, KL p.33.
  - Bác Sĩ starts at Lộc Tồn (Thân), thuận: TH p.22, KL p.28.
  - Thái Tuế starts at Ngọ and is always thuận: TH p.22, KL p.30.
- **Natal Tứ Hóa Canh:** Nhật Lộc (Sửu), Vũ Quyền (Tý), Đồng Khoa (Hợi), Âm Kỵ (Sửu). KL p.36 and TH pp.20-21 (image) agree. Both books also confirm the other 8 stems as coded (KL's misprint of Tân-Lộc is already handled).
- **Đại hạn:**
  - The first decade starts at Mệnh at age = cục (6), thuận for dương nam / âm nữ: TH p.27, KL p.37.
  - Output: 6 Mệnh, 16 Phụ Mẫu, 26 Phúc Đức, 36 Điền Trạch (Kỷ), …
- **2026:**
  - tuổi mụ 37.
  - Tiểu hạn: start Thìn (Dần Ngọ Tuất) plus 36 thuận gives **Thìn, Quan Lộc** (TH p.27; KL pp.39-40 gives the same for dương nam).
  - Lưu Thái Tuế **Ngọ** (Thiên Di): KL p.41.
  - Lưu Tứ Hóa Bính = Đồng Lộc (Huynh Đệ), Cơ Quyền (Điền Trạch), Xương Khoa (Nô Bộc), Liêm Kỵ (Tài Bạch). These positions are computed correctly, but the rule itself is unsourced (TV-7).
  - Đại hạn 36-45 Điền Trạch (Kỷ). Experimental decade Tứ Hóa: Kỷ = Vũ Lộc (Mệnh), Tham Quyền (Phúc), Lương Khoa (Nô), Khúc Kỵ (Tử Tức). This is unsourced (TV-11).

**Brightness and conventions:**
- **Tử Vi at Thìn = vượng:** TH p.29 (image: "Vượng thì Thìn Tuất"), KL p.75 ("vượng địa như Thìn, Tuất") and TT p.21 all agree.
- **Thái Dương Sửu = hãm** is correct *per TH p.31* (image), but disputed by KL (TV-3).
- **Vũ Khúc Tý is blank under TH:** correct. TH p.34 gives only miếu Sửu Mùi Thìn Tuất and hãm Tỵ Hợi; Mão Dậu are only called "khá". KL p.87 and TT both say vượng.
- **Hỏa / Linh direction** by âm dương nam nữ (Hỏa thuận and Linh nghịch for dương nam / âm nữ): TH p.25 and KL p.27. The golden test covers both sexes.
- **Thiên Mã** is placed by year-branch triad, not by month: KL pp.31-32, TH p.21.
- **Thiên Không** = cung after Thái Tuế, i.e. with Thiếu Dương: KL p.30, TH p.25 (Mùi year gives Thân; tested).
- **Đẩu Quân:** from Thái Tuế count nghịch by month, then thuận by hour: KL p.32, TH p.25.
- **Year boundary:** Tử Vi uses the lunar (Tết) year (`tuvi.py:174`, trace). 2021-02-08 gives Canh Tý for Tử Vi while Bát Tự gives Tân Sửu (Lập Xuân), as intended.
- **Calendar differences:** VN and CN calendars differ correctly. 2007-02-17 is VN 1/1/2007 but CN 30/12/2006. 1985-01-21 is VN 1/1/1985 but CN 1/12/1984.
- **First day of a lunar month:** 1990-05-24 (1/5) gives Tử Vi at Dậu (day 1, cục 6, pad 5 odd, so Dần + 0 − 5 = Dậu). Correct.
- **23:xx with the default `early_zi_next_day`:** uses the next lunar day and the Tý hour, consistent with 00:30 the next morning (both give Tử Vi Mùi and Mệnh Tỵ). The convention itself is TV-14.
- **Aux-star rule usage:** no Tử Vi pack rule consumes the unverified aux stars. Only the BaZi `shensha.json` shares some names (a separate system). The exception is the Thiên Hình mention in synthesis (TV-16).
