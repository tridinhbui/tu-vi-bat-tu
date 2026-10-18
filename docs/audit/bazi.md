> Evidence file of the 2026-10-18 interpretation-engine audit (read-only sub-audit, consolidated in ../INTERPRETATION-ENGINE-AUDIT.md). Paths under `scratchpad/` refer to the auditing session's temporary folder and are not in the repository. Statuses here are as found on 6c10cf5, BEFORE the fixes; see the consolidated audit for what was fixed.

# Bát Tự audit (read-only) — worktree `interp-engine-audit` @ 6c10cf5

Reference chart: 17/05/1990 10:30 male, HCMC (lon 106.7, Asia/Ho_Chi_Minh). Python: `.venv/bin/python` run from `engine/`.
Books: 八字真宗 = `~/Downloads/bát tự chân tông -[ChienNguyen] 八字真宗.pdf` (ZZ); Thiệu Vĩ Hoa = `Dự Đoán Theo Tứ Trụ` (TVH, scan).
Note: `tools/show_page.py` does not exist in this worktree; pages were read with an equivalent pymupdf script in the scratchpad.
Test state: `pytest tests/test_bazi*.py tests/test_calendar_and_bazi.py tests/test_dignity_and_bazi_rules.py` → 447 passed, 1 skipped (zz API wiring), 2 xfailed.

Reproduced production facts for the reference chart: pillars Canh Ngọ / Tân Tỵ / Nhâm Ngọ / Ất Tỵ; relations = stem_combine year–hour (Kim, transforms null), stem_clash month–hour, branch_self_penalty year–day; luck thuận, start 6.601 y (6y 7m 6.4d) on 1996-12-23; 2026 = Bính Ngọ, luck Giáp Thân, `luck_changes_within_year: true` (Ất Dậu starts 2026-12-23).

---

## Findings

### BZ-1 (P0) Stem xung/khắc table has 4 pairs; the cited source lists 10
- **Root cause**: `STEM_CLASH` = 甲庚 乙辛 丙壬 丁癸 only, but the rule is marked `verified` against ZZ p.20. ZZ p.20 (干冲克) lists ten: 甲庚克, 乙辛冲, 丙壬冲, 丁癸冲, 戊甲克, 己乙冲, 庚丙冲, 辛丁冲, 壬戊冲, 癸己克. That is each stem against the stem seven places on, and the book labels three of them 克 rather than 冲.
- **Affected**: `engine/tvbt/bazi.py:26` (and the `rule_review` claim at :281); `temporal.py:5,24-25` (lưu niên/đại vận/lưu nguyệt); `bazi_deep/interact.py:49-50`; `bazi_deep/temporal_deep.py:66-71,74` (also phản ngâm); `analysis.py:272` text; `reasoning/facts.py` (zz facts inherit it). Test `tests/test_bazi_book_golden.py::test_stem_relations_p20` only checks that the 4 pairs are present, so the 6 missing pairs go untested.
- **Evidence**: for the reference chart in 2026, lưu niên Bính against natal Canh (year stem) is 庚丙冲 per ZZ p.20, and it is missing from `annual_vs_natal`. Output only has can_hợp month and can_xung day. Luck Giáp against natal Canh is shown as "xung"; the book calls it 克.
- **Fix**: use the 10-pair table with a subtype (`xung` | `khac`) and extend the golden test to all 10. **Source-supported (ZZ p.20).** Draft effect sizes in bazi_deep must say whether 戊甲/癸己/庚丙… get the same multipliers (that part NEEDS SOURCE; TVH's khắc-gần/cách-ngôi rule in `tvh_score.py` already treats all khắc generically).

### BZ-2 (P0) Pairwise 三刑 (寅巳, 巳申, 申寅, 丑戌, 戌未, 未丑) missing in production
- **Root cause**: `_relations` only reports hình when all three branches are present (`PENALTY_TRIPLES`), plus 子卯 and the 自刑 pairs. ZZ states 刑 pairwise: p.20 "寅刑巳、巳刑申、申刑寅；丑刑戌、戌刑未、未刑丑", and the p.19 grid marks 刑 in the 寅巳 (刑害 / 刑克), 巳申 (合 刑破), 寅申 (刑冲), 丑戌, 丑未 (刑冲) and 戌未 (刑破) cells.
- **Affected**: `bazi.py:165-178` (natal); `temporal.py:15-26` (no hình at all, see BZ-3); `temporal_deep.py:82` (only 自刑 and 子卯 for temporal pillars). `bazi_deep/interact.py:72-80` *does* detect pairs (`ban_hinh_*`), so production and deep disagree.
- **Evidence**: luck Giáp Thân against natal Tỵ (month, hour) shows only "lục hợp + phá"; the book cell 巳申 = 合·刑·破, so the hình is missing. Natal charts holding Dần–Tỵ show only hại, not hình.
- **Fix**: add pair hình to all relation paths, keeping the triple as its own "đủ bộ" record. **Source-supported (ZZ pp.19-20).**

### BZ-3 (P0) Lưu niên/đại vận × natal: no hình of any kind in the production temporal path
- **Root cause**: `temporal._rel_with_natal` (`temporal.py:15-26`) checks lục hợp, xung, hại, phá and can hợp/xung only. It has no 自刑, no 子卯 and no 三刑 pairs, and no completion of tam hợp or tam hội. The frontend already has labels waiting for them (`web/js/bazi.js:22` YEAR_REL has `chi_hình`, `chi_tam_hợp`, `chi_tam_hội`), but the backend never emits them.
- **Evidence**: in 2026, lưu niên Ngọ against natal Ngọ (year and day) is 自刑 per ZZ p.20, and it is not listed. `bazi_deep` timeline does list it (`branch_penalty from year with year.branch / day.branch`). When the only interaction is a hình, the UI prints "Không có tương tác đáng kể" (`bazi.js:258`).
- **Fix**: share one relation function across natal, luck, year and month, and also report year×luck relations (today only `luck_vs_annual_clash`, which is never rendered). **Source-supported (ZZ pp.19-20).**

### BZ-4 (P0) Draft "thiếu hành" reading shown in production on a chart that has the element
- **Root cause**: `facts.bazi_facts` builds `bazi.missing_elements` from the 4 stems plus the 4 branch main elements; hidden stems are ignored (`reasoning/facts.py:168,171`). Draft rules `BT_ZZ_MISSING_*` (`data/pack_bazi_zhenzong.json`) fire, and `report.js:127` puts `bt_thieu_hanh_*` into the Nhật Chủ chapter, where it renders as a "Quy tắc nháp" card. The same chart's "Tổng quan" notice says "Chỉ các nhận định đã đối chiếu sách mới được hiển thị" (`report.js:136`). The finding is also in the `/api/reasoning` narrative text.
- **Evidence**: for the reference chart `/api/reasoning` returns `BT_ZZ_MISSING_THỔ` (basis draft), whose text paraphrases to "lacks loyalty, because the chart has no Thổ" (claims_vi `bt_thieu_hanh_thổ`). Yet the chart holds Kỷ in both Ngọ and Mậu in both Tỵ. TVH scoring gives Thổ 24° (vs Kim 43.2°), and `bazi_deep` khuyet_hanh reports "ngũ hành đủ". The TS chapter already separates hidden-only elements (`src/interpret/bazi.ts` `hiddenOnly`), so Python and TS disagree. ZZ p.27 uses 缺 as one level of a strength scale (强/旺/弱/缺/中和 per element), not as "not visible".
- **Fix**: do not render draft findings in production chapters (or at least not character judgements). If kept, 缺 must at least mean "absent from stems and from all hidden stems". **The operational definition of 缺 NEEDS SOURCE (ZZ pp.26-27 gives no criterion).**

### BZ-5 (P1) Luck "year" label and "Hiện tại" marker use `start_year_approx` (can be a year off)
- **Root cause**: `web/js/bazi.js:55-57` uses `l.start_year_approx` (= birth year + age, ignoring the birth month; `bazi.py:252`) for `curIdx` and for the `Math.round(...)` year label in `parts.luck` (the report's Đại vận chapter).
- **Evidence**: 1990-12-20 female: Đinh Hợi labelled 1994, but `start_date` is 1995-03-21. 1985-10-30 male: Ất Dậu labelled 1992, actually 1993-02-02. 1991-11-25 female: Canh Tý labelled 1995, actually 1996-01-24.
- **Fix**: use `start_date` / `start_year_exact` everywhere and remove `start_year_approx`. Computation fix, no source needed.

### BZ-6 (P1) Year-to-luck assignment differs between frontend, Python and TS
- **Root cause**: Python `temporal.bazi_year` takes the luck active at `year + 0.09` (≈ Lập Xuân). The frontend strip uses `periodYears` = `ceil(start_year_exact)` .. `ceil(next)-1` (`web/js/atlas.js:27-29`). TS uses `int(start_date[:4]) <= year` (`api.py:112`, `src/interpret/bazi.ts` `cur`).
- **Evidence**: 1991-11-25 female: Canh Tý starts 1996.063. `/api/year 1996` says Canh Tý, but the strips are Canh Tý 1997–2006, so 1996 is in no strip. For the reference chart in 2026, Python says Giáp Thân (correct for most of the BaZi year), while TS says Ất Dậu "bắt đầu khoảng năm 2026" (it starts 23 Dec). `luck_changes_within_year` (`temporal.py:70`) is never rendered, so the Dec-2026 change goes unmentioned.
- **Fix**: one shared function that uses the exact Lập Xuân instant of each year and shows a "đổi vận trong năm (ngày …)" note. Computation fix.

### BZ-7 (P1) Late-Zi (夜子) option combines today's day pillar with today's Tý stem
- **Root cause**: with `zi_rule=late_zi_same_day`, `rule_date` stays on the same day and the hour stem is `ds%5*2` of that same day (`calendar_core.py:105-107`, `bazi.py:213-214`).
- **Evidence**: 2024-03-10 23:30 late_zi gives Quý Dậu day / Nhâm Tý hour. Nhâm Tý is the Tý hour that *opens* the Quý Dậu day (00:00–01:00). As 夜子时 is usually described, the day pillar stays and the hour takes the *next* day's Tý stem (Giáp Tý here). Early-Zi works correctly: next-day Giáp Tuất / Giáp Tý, the same as 00:30.
- **Fix**: decide the school. Either take the next day's stem for the late-Zi hour, or document the current variant in the UI and trace (today the trace and UI only say "Cùng ngày đến hết 24h"). **NEEDS SOURCE**: none of the three books settles it; ZZ p.71 only gives the 五鼠遁 formula. Already flagged `convention` in `rule_review`.

### BZ-8 (P1) Northern-Vietnam births 1960–1975 get the South's UTC+8 civil offset
- **Root cause**: the place selector maps every city (Hà Nội, Hải Phòng, Vinh …) to `Asia/Ho_Chi_Minh` (`web/js/app.js:79-86`). IANA gives that zone +08:00 from 1960 to 1975 (checked: offsets 1955/60/65/75 = +8, 1976 = +7). IANA files Hanoi under `Asia/Bangkok` (+7).
- **Impact**: UTC is off by 1 h for northern births, which shifts jie comparisons (year/month pillar within an hour of a jie), moves khởi vận by about 5 days (1 h = 5 days at 3 days/year), and moves the true-solar-time hour pillar by a whole hour when "giờ mặt trời" is on.
- **Fix**: use per-city zones (northern cities → `Asia/Bangkok` or explicit historical offsets). **NEEDS SOURCE** to confirm the DRV civil time and the exact cut-over dates (tzdb `asia` file comments; `calendar_core.vn_calendar_offset` already notes the sources disagree for the lunar calendar).

### BZ-9 (P1) The verified TVH 40% rule is overridden by an invented ±0.03 "trung hòa" band
- **Root cause**: `strength._band` (`bazi_deep/strength.py:111-117`) reports |share−0.40| < `tvh_margin` = 0.03 (`profile.py:24`, draft) as level "trung hòa", ambiguous. That blocks phu_uc and `cach_cuc_tvh` (`hai_cach_doc`).
- **Evidence**: TVH p.355, example 6: 78 vs 78.8 (share 0.396) is labelled "nhật chủ hơi nhược", a decisive verdict inside the system's band. Reference chart, `tvh_score.score`: Thủy 24 + Kim 43.2 = 67.2 of 175.2, own_share 0.3836 < 0.40 → `dm_strong: false`. `/api/bazi-structure` nevertheless says "trung hòa, ambiguous" and fires draft `BT_ST_LEVEL_AMBIG`. With `tvh_margin=0.0` it gives level "thiên nhược", verified `BT_TVH_NHUOC`, `cach_cuc_tvh` = Thiên Ấn cách with dụng Tỉ (Thủy), which agrees with TVH điều hậu (Nhâm born in Tỵ: chính = Nhâm, hỷ = Ấn).
- **Fix**: report the binary verdict and add a "sát ngưỡng" *note* instead of a third level (book wording "hơi nhược/hơi vượng"). **Source-supported (TVH p.355).**

### BZ-10 (P1) Three different strength verdicts for one chart across bazi_deep endpoints
- **Evidence**: `/api/bazi-structure` (tvh40 + margin) says trung hòa; `/api/bazi-timeline` natal (forced `strength_method="he_thong"`, `temporal_deep.py:191,214`) says **cực nhược**; strict TVH says nhược. pack_temporal `BT_TTT_THIENKHAC_NHUOC` ("gặp đại hung") and `_VUONG` key on the he_thong level.
- **Fix**: before any wiring, use one strength decision (TVH for natal) and state explicitly that temporal pillars have no TVH counterpart. Not source-blocked for natal. **Temporal strength NEEDS SOURCE.**

### BZ-11 (P1) "Verified" rules that sit on draft premises
- `pack_temporal.json`: `BT_TTT_TIETCUOC_CACH_CUC`, `…CAIDAU_CACH_CUC`, `…_PHU_UC` are `verified`, but their premise ("can vận là dụng/hỷ theo cách cục / phù ức") comes from `geju_defs.json` (`_status: draft`, entered from memory of 子平真诠, "CHƯA đối chiếu") or from phù ức (draft by `yongshen.METHOD_META`). For 2026 the timeline fires `BT_TTT_TIETCUOC_CACH_CUC` as verified.
- The command (tư lệnh) table `data/bazi_deep/tu_lenh.json` is also draft from memory, and it contradicts `HIDDEN_STEMS`: Ngọ = [Bính 10, Kỷ 9, Đinh 11] vs code Ngọ = Đinh, Kỷ.
- **Fix**: effective basis = min(rule basis, premise basis), propagated in the engine. Engine fix; the premises themselves NEED SOURCE (子平真诠 text, 渊海子平/三命通会 tư lệnh tables).

### BZ-12 (P1) 八字真宗 direct judgements (`bazi_facts(zz=True)`): status and wiring risks
- **Status**: 49 rules (33 verified, 16 draft) in `data/pack_bazi_zz_direct.json` are **loaded in production** (`knowledge/loader.py:10` PACKS). No caller passes `zz=True` (`api.py:110,245`), so they stay pending forever. Test `tests/test_bazi_zz_tables.py::test_api_integration_when_wired` is skipped. Docs `INTERPRETATION-PIPELINE.md:78,282` say the same.
- **What it would output for the reference chart** (run with zz=True): verified HOUR_GROUP_THUC_THUONG (occupation), M_TAI_QUAN_AN (harmonious marriage), D_TAI (gain through spouse), E_AN_ROOT, WEN_CHANG; draft D_HURT (day branch hình/xung), HOUR_STEM_AT.
- **Risks**:
  1. `_zz_direct_facts.bad()` reads production `relations`, so it inherits BZ-1/BZ-2 (no pairwise hình, only 4 stem pairs). It also counts the *non-adjacent* Ngọ–Ngọ year–day 自刑 as "day branch hurt" (`day_branch_hurt: true` for the reference chart).
  2. No `conflictsWith` or `exceptions` in any of the 49 rules. In a 300-chart random sweep, 126/300 charts got both a positive and a negative marriage reading.
  3. Occupation by hour stem depends entirely on the hour pillar: Tý rule (BZ-7), unknown hour (UI defaults to 12:00, `app.js:107`), true solar time. There is no confidence gate.
  4. Văn Xương is looked up by **year** stem and includes thai/mệnh/thân branches (`facts.py:93,159`); confirm against ZZ pp.72-74.
  5. The "rooted" test uses any hidden stem of the same element, residual qi included.
- **Fix**: keep off until BZ-1/2 are fixed; add conflict pairs and an hour-confidence gate; soften the marriage wording. Rule texts are source-supported (ZZ pp.51-58); the **conflict policy NEEDS a decision**.

### BZ-13 (P2) User-facing scope text is stale and contradicts what is shown
- `web/js/scope.js:24-26` says thần sát, không vong and nạp âm "chưa được an". But `analysis.py:173-185` shows không vong, thai/mệnh/thân cung and thần sát (ZZ pp.21-22) in the report, and the verified nạp âm reading `BT_ZZ_NAPAM_*` is displayed.
- It says no source gives a threshold for vượng/nhược, while the repo has a verified TVH p.355 40% rule (`BT_TVH_*` verified). Accurate wording: "đã có trong /api/bazi-structure nhưng chưa đưa vào báo cáo". Same with the "Cách cục…" notice (`report.js:147`).
- `INTERPRETATION-PIPELINE.md:282` ("strength … have no verified … rules") is half true: verified but not wired.

### BZ-14 (P2) Bán hợp: production omits it; bazi_deep's "cung" variant conflicts with ZZ p.20
- ZZ p.20 defines 半合局 as needing the middle branch (left+middle or middle+right). Production `_relations` never reports bán hợp.
- `bazi_deep/interact.py:19,64-67` adds a `cung` semi (sinh+mộ, no middle). That contradicts the p.20 text, although the p.19 grid marks 子辰 / 申辰 as 三合 (book-internal tension).
- **Fix**: add bán hợp (sinh–vượng, vượng–mộ) to production; mark `cung` as school-dependent. **Source-supported for the first part.**

### BZ-15 (P2) Names "vô ân" / "thị thế" are not in the cited page
- `bazi.py:33` and the golden test assert 寅巳申 = "vô ân" and 丑戌未 = "thị thế". ZZ p.20 prints the 刑 without names, and schools assign these two names differently.
- **Fix**: drop the names, or cite a source that gives them (e.g. 三命通会). **NEEDS SOURCE** if kept.

### BZ-16 (P2) "Tiềm năng hóa" shown for 遥合 with no distance information
- Production lists Canh (year) – Ất (hour) as a "tiềm năng hóa Kim" hợp (`bazi.js` relText) with no `adjacent`/span field. `bazi_deep` marks it `khong_ke`. TVH scoring only counts adjacent ngũ hợp (`tvh_score.py:57-59,128-131`, from pp.336-338).
- **Fix**: add `span` to production relations and state "cách xa, theo Thiệu Vĩ Hoa không xét hóa". Source-supported (TVH), school-dependent.

### BZ-17 (P2) The `analysis.py` relations sentence omits hình
- `analysis.py:271-275` lists only lục hợp, xung, hại, phá, can hợp and can xung. For the reference chart the text leaves out the Ngọ–Ngọ tự hình that the relation panel shows, and still cites "八字真宗 PDF pp.19-20".

### BZ-18 (P2) The "Cân bằng Ngũ Hành" bar chart equates raw counts with balance, and double counts
- `web/js/insights.js:13-21`: each branch counts once by its main element as a "visible" character, and its hidden stems then count again (Ngọ = Hỏa visible + Đinh hidden). Residual qi gets the same weight as main qi. The reference chart shows Thổ 0+4 vs Kim 2+2, while TVH degrees give Thổ 24 vs Kim 43.2 and Hỏa 84.
- **Fix**: rename it to "Số lần xuất hiện" or show TVH degrees, and add a line saying counts are not strength. Computation/UX fix.

### BZ-19 (P2) Age labels do not say which age is meant
- Luck labels are `Math.round(start_age)` (exact age, rounded: 6.6 → "7 tuổi"; `bazi.js:57,131,235,236`). `analysis.py:294` uses `:.0f`. The Tử Vi side uses tuổi mụ (`temporal.py:77`). `bazi_year.age` is a Gregorian difference.
- **Fix**: label "tuổi thực (khoảng)" or show the start date.

### BZ-20 (P2) TS khởi-vận months can differ from Python by one month
- `api.py:111` rounds `luck_start_age` to 0.1 y and TS derives months from that (`bazi.ts` `bz.luck_start`). Example: 6.66 y gives Python "6 năm 7 tháng" (floor) but TS "6 tuổi 8 tháng".
- **Fix**: send years/months/days from Python.

### BZ-21 (P2) No warning when a pillar sits near a boundary
- 2024-02-04 15:26 vs 15:27 (Lập Xuân 08:26:53 UTC) flips year and month pillar, luck direction (female: thuận → nghịch) and the luck sequence. `/api/hour-sweep` exists for hours but there is no jie-proximity or hour-edge flag in the bazi output.
- **Fix**: add `near_jie_minutes`, `near_hour_edge_minutes` and `near_zi_boundary` facts plus a UI caveat.

### BZ-22 (P2) Đại vận branch falls in the day pillar's không vong; not surfaced
- Giáp Thân (2017–2026) has branch Thân, which is in the không vong of Nhâm Ngọ (Thân, Dậu); so does the next luck, Ất Dậu. Not flagged in temporal facts. Reading it NEEDS SOURCE.

### BZ-23 (P2) Code smells and dead conditions
- `reasoning/facts.py:166` `k != "day" or True` (always true).
- Unused `yin` lambda in `_zz_direct_facts`.
- `temporal_deep.py:103` `tb not in ()`.
- `interact.py:261` `(r["adjacent"] or True)`.
- `lunar`/`gender` only male/female.
- Performance is fine: `/api/year` about 1.6 ms per call after warm-up; `/api/bazi-timeline` for 80 years under 0.1 s.

---

## Verified CORRECT (with evidence)
- **Year pillar at the Lập Xuân instant, month pillar by jie** (`bazi.py:189-204`). 2024 Lập Xuân = 2024-02-04 08:26:53 UTC (sxtwl; HKO 16:27 HKT). 15:26 VN gives Quý Mão / Ất Sửu and 15:27 gives Giáp Thìn / Bính Dần (run). ZZ p.23 has the 12-jie table. jqIndex mapping checked: odd = jie, 3 = Lập Xuân → Dần.
- **Day pillar**: Nhâm Ngọ for 1990-05-17. 3516 days before 2000-01-01 (戊午, idx 54): 54−36 = 18 = 壬午.
- **Hour branch and stem**: `((h+1)//2)%12`; 五鼠遁 and 五虎遁 golden-tested (ZZ p.20, p.35 row). Early-Zi 23:30 equals 00:30 of the next day (Giáp Tuất / Giáp Tý), as expected.
- **True solar time**: clock = civil + 4·(lon − offset·15) + EoT = UTC + 4·lon + EoT, which is correct even with DST. Reference: 10:40:41, pillars unchanged.
- **Luck pillars**: direction by year-stem polarity × sex (ZZ p.23). The continuous days/3 conversion equals the book's "1 day = 4 months, 1 shichen = 10 days". Reference: target Mang Chủng 1990-06-05 22:46 UTC, 19.803 days → 6.601 y = 6y 7m 6.4d, start 1996-12-23. Sequence Nhâm Ngọ → Quý Mùi → Giáp Thân (2016-12-23) → Ất Dậu (2026-12-23). Matches the production description.
- **Hidden stems**: sets match ZZ pp.7-8 (`test_hidden_stem_sets_pp7_8`). Main/middle/residual order matches the TVH p.342 degree table (`tvh_score.HID_DEG`: Tỵ = Bính 18 / Canh 9 / Mậu 3). Production "Tỵ: Bính chính, Canh trung, Mậu dư" is correct.
- **Ten gods**: ZZ p.17, 100 stem cells plus branch rows golden-tested. Reference checked by hand: Canh Thiên Ấn, Tân Chính Ấn, Ất Thương Quan, Đinh Chính Tài, Kỷ Chính Quan, Bính Thiên Tài, Mậu Thất Sát.
- **12 trường sinh (yin reverse)**: ZZ pp.24-25 full table golden. Nhâm at Ngọ = Thai, at Tỵ = Tuyệt.
- **Branch tables**: lục hợp, lục xung, hại, phá, tam hợp, tam hội, 子卯 and 自刑 {辰午酉亥} match ZZ p.20. **Ngọ–Ngọ tự hình (year–day) is correct** (p.20 辰午酉亥自刑; p.19 grid 午午 = 刑).
- **Stem relations shown for the reference chart**: Canh–Ất hợp Kim and Tân–Ất xung are correct (ZZ p.20). 2026 Bính–Tân hợp (month) and Bính–Nhâm xung (day) are correct. Luck Thân × Tỵ lục hợp + phá is correct (but hình is missing, BZ-2).
- **Không vong** Thân/Dậu for Nhâm Ngọ (Giáp Tuất xun); thai nguyên Nhâm Thân (Tân+1, Tỵ+3, ZZ pp.35-36).
- **Leap months** do not affect Bát Tự: 2023-03-25 (in lunar leap month 2) gives Quý Mão / Ất Mão by jie.
- **TVH scoring** reproduces for the reference chart: heaven Kim 36 / Thủy 24; earth Hỏa 70 / Thổ 24 / Kim 18; lệnh Hỏa +1/5, Kim −1/5; share 0.3836. TVH điều hậu cell (壬 in 巳) chính Nhâm, hỷ Ấn.
- **Production refusal to conclude vượng/nhược, cách cục, dụng thần** is honest about wiring. The stated reason ("no source gives a threshold") is outdated (BZ-13).
- **Production temporal output** contains no event-prediction wording. `bazi_twelve` glosses are softened and not used by the web UI.
