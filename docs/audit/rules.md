> Evidence file of the 2026-10-18 interpretation-engine audit (read-only sub-audit, consolidated in ../INTERPRETATION-ENGINE-AUDIT.md). Paths under `scratchpad/` refer to the auditing session's temporary folder and are not in the repository. Statuses here are as found on 6c10cf5, BEFORE the fixes; see the consolidated audit for what was fixed.

# Audit: Tử Vi rule packs and the rule engine (production `/api/reasoning`, verified findings only)

Date: 2026-10-18. Worktree `feat/interp-engine-audit`, head 6c10cf5. **Read-only:** no repo file was changed.

**Method.**
- **Reference chart.** 17/05/1990 10:30, male, lon 106.7 (Canh Ngọ, dương nam, Hỏa lục cục, Mệnh Tý). It was run through `tvbt.api.reasoning()`.
- **Sweeps.** Seeded random births, 1930–2025, any hour and sex. Each was run through the same steps as the API (`facts.tuvi_facts` → `engine.run` → `conflict.resolve` → `_merge_corroborated`) and then filtered to `basis=='verified'`, as `web/js/app.js:142` does:
  - 400 charts (seed 20261018), the main statistics;
  - its first 50 charts (§3);
  - 2,000 charts (seed 7), for dead rules.
- **Page checks.** 18 cited pages were opened as page images, using `tools/book_text.py render` (there is no `tools/show_page.py` in this worktree).
- **Prior audit.** The fixes listed in `docs/INTERPRETATION-AUDIT.md` §2 still hold: `tests/test_rule_integrity.py` gives 2 passed, 1 skipped; the Đà La độc thủ, Tả Phụ miếu and Thiên Đồng "no sát" conditions are present.

Scripts and pickles: `scratchpad/a/` (`run_ref.py`, `static.py`, `sweep.py`, `analyse.py`, `cofire.py`, `refdup.py`).

Scale: 1,332 Tử Vi rules, of which **1,139 are verified**, in 23 packs. Exceptions are used by 2 verified rules. `conflictsWith` is used by **0** rules. Hóa Kỵ is excluded by **0** rules. Tuần/Triệt is excluded by 1 rule.

---

## Issues

### RL-1 (P0): "Về già sung túc, an nhàn" (Tật Ách) fires on 87–88% of all charts and ignores the book's own "tối kỵ" clause

- **Rule:** `TV_KL_CUNG_TAT_ACH_CUOI_DOI`, built from `tools/build_kl_palace_pack.py:53`.
- **Root cause:** the condition is an `any` over 11 leaves:
  - any single one of Tử, Phủ, Vũ, Tướng, Tả, Hữu, Khôi or Việt in the palace, **or**
  - any of Hóa Lộc, Quyền or Khoa anywhere in the palace's **tam phương** (4 of the 12 palaces).
  
  Three Hóa scattered over the chart almost always reach one of the four palaces.
- **Firing rate:** 88.0% of 400 charts and 86.6% of 2,000. In 43% of the firings (750 of 1,731), the **only** trigger is a Hóa somewhere in the tam phương.
- **What the page says (KL p.218, image checked).** "Cung Tật cần có Tử Phủ Vũ Tướng, hoặc Sát Phá Tham, Tả Hữu, Khoa Quyền Lộc, Khôi Việt … giầu sang vào lúc cuối đời". The same paragraph then adds: "**Tối kỵ cho cung Tật khi có Tham lang, Hóa kỵ, Không Kiếp dự vào**".
  - The rule never tests that exclusion: 415 of 1,731 firings (24%) have Tham Lang or Không/Kiếp in the palace itself.
  - The page names the stars in pairs ("Tả Hữu", "Khôi Việt"); the rule accepts one star of a pair. It also widens "Khoa Quyền Lộc" from "in the palace" to "in the tam phương".
- **Reference chart.** It fires on Tả Phụ + Hữu Bật in a palace that is vô chính diệu, with Triệt, Đà La and Thiên Không. The same page lists Triệt and Thiên Không as rescuers, so this particular instance is defensible. The rule as written is not.
- **Fix:**
  - Require a pair (Tả+Hữu, Khôi+Việt; the Khôi–Việt pair is necessarily split, so read it as "giáp or chiếu", NEEDS SOURCE) or a Tử-Phủ-Vũ-Tướng star in the palace.
  - Require Hóa Khoa/Quyền/Lộc **in** the palace, not in the tam phương.
  - Add an exception for Tham Lang, Hóa Kỵ, Địa Không or Địa Kiếp in the palace (source-supported, KL p.218).
  - Until that is done, demote the rule to draft.

### RL-2 (P0): Opposite verified readings fire on the same palace with no explanation; conflict detection cannot see them

- **Root cause:**
  - `conflict.resolve` only compares findings with the **same claim id**, plus declared `conflictsWith` pairs. Every claim id is per rule, and no rule declares `conflictsWith`. The API therefore never marks real contradictions; each card shows "supported" or "limited" on its own.
  - About 55 negative readings carry `effect: support` (RL-4), so even an effect-based check would miss them.
- **Evidence (2,000 charts):**
  - `TV_KL_CUNG_PHU_MAU_SAO_TOT` ("cha mẹ khá giả…") **and** `TV_KL_CUNG_PHU_MAU_HUNG` ("cha mẹ vất vả, chẳng giàu") co-fire on **19.3%** of charts, for example with Cơ Cự or Đồng Cự in Phụ Mẫu. Both come from the same KL p.220 list, and the book does not rank them.
  - `TV_TH_VERSE_DI_KHONG_KIEP` ("danh vọng đến muộn", effect support) and `TV_TH_P2_THIEN_DI_KHONG_KIEP` ("ngoài giao thiệp lắm trắc trở", effect limit) have the identical condition and co-fire on 16.6% of charts.
  - `TV_KL_CUNG_PHU_THE_DEP_DOI` ("vợ chồng hòa thuận, đẹp đôi, bền lâu") fires with Không/Kiếp in Phu Thê on 6.0% of charts, alongside `TV_TH_P2_PHU_THE_KHONG_KIEP` ("hai ba lần dang dở"). KL p.217, the **same paragraph**, says "Gặp lũ sát tinh Kình Đà Không Kiếp thì dễ tan vỡ". That half was built as draft (`build_kl_palace_pack.py:49`), so only the optimistic half is shown.
  - **Reference chart, Mệnh:** "phúc lộc song toàn" (`TV_TH_STAR_THIEN_PHU_NAM_CAT`) next to "cùng khổ, chỉ tu hành mới yên thân" (`…_NAM_TUAN_TRIET`). TH p.94 (image checked) links the two with "**Nhưng** Phủ kỵ nhất…", so the second is the disqualifier of the first, not a parallel reading.
  - **Reference chart, Quan Lộc:** "quyền quý ×2" and "văn võ đều hay" stand next to "khó đạt công danh" (shown as support, RL-4) and "công danh tầm thường".
  - **400-chart sweep:** a mean of 15 verified support-versus-limit pairs per chart share a trigger star on the same palace. None of them is linked by the conflict code.
- **Fix:**
  - Encode book disqualifiers as `exceptions` on the positive rule (TH p.94, KL p.217, KL p.218 are source-supported).
  - Declare `conflictsWith` for same-page opposite pairs.
  - Make `conflict.resolve` also group by (subject, trigger) when effects or polarity differ.
  - Where the book gives no precedence (KL p.220), show the pair as "unresolved" with both quotes. Do not show two independent verified cards.

### RL-3 (P1): Disqualifiers are not encoded anywhere in production; named cách cục are judged by name alone

- **Root cause:**
  - Every builder writes `"exceptions": [], "conflictsWith": []` (for example `build_kl_palace_pack.py:87`).
  - The formation machinery with breakers and rescuers (`formation_eval.py`) is used only by 10 **draft** formations in `data/experimental/formations_experimental.json`. Production never loads them (`loader.load_experimental`).
  - None of the 10 is Lộc Mã giao trì, Song Lộc, Tả Hữu giáp or Không Kiếp.
- **Evidence:**
  - `TV_TH_CACH_TAI_BACH_LOC_MA` outputs the bare label "cách Lộc Mã giao trì (Lộc và Mã đồng cung)". TH p.72 (image checked) is a **list of names**: "20. Lộc, Mã giao trì cách (ở Mệnh, Tài, Quan, Thiên di đều tốt)". It contains no reading and **no "đồng cung"**. KL p.216 defines it differently: "Lộc tồn thủ có Mã chiếu hoặc ngược lại".
  - Disqualifiers printed on the cited pages but not encoded:
    - TH p.106: "Tuần Triệt trước đất cũng không", "Đà Không nghèo khó", "Kiếp Không khốn khó";
    - KL p.216: "Nhược bằng bị lũ Không Kiếp, Liêm Tham, Song Hao ghé vào thì nghèo";
    - TT p.159 #96: "nếu gặp Tứ Sát Kình Đà Không Kiếp Hóa Kị lại là nô khi chủ".
  - The single disqualifier-like rule, `TV_TH_MV_MENH_LOC_MA_TRIET` ("Lộc Mã gặp Triệt thì mất ích lợi"), is a separate claim and **never fires** in 2,000 charts.
  - **Reference chart, Lộc Tồn + Thiên Mã at Thân (Tài Bạch):** 7 readings from one fact (RL-5). Đà La and Kình Dương always flank Lộc Tồn, so "Kình Đà giáp" can never act as a breaker either.
- **Fix:**
  - Move the cách rules (`pack_thuc_hanh_cach.json`, 52 verified) to formations with breakers taken from the pages above (source-supported for Lộc Mã: TH p.106, KL p.216).
  - Output nothing for name-only list items (TH p.72) unless another page gives the reading.
  - Drop "(Lộc và Mã đồng cung)" from the label, since it is not in the source.

### RL-4 (P1): About 55 clearly negative verified readings carry `effect: support`

- **Root cause:** the builders default `effect` to `support`. Only phrases a builder marks become `limit`.
- **Evidence:** a keyword scan finds 86 candidates. Hand review leaves about 55 unambiguous ones, for example:
  - `TV_TH_AUX2_QUAN_LOC_KK_HAM` "khó đạt công danh" (reference chart);
  - `TV_TH_AUX2_MENH_KK_HAM` "quỷ quyệt, ích kỷ";
  - `TV_TH_AUX2_MENH_HOA_HAM` "nham hiểm, gian tà";
  - `TV_TH_AUX2_MENH_KINH_KHAC` "hung bạo… gian trá";
  - `TV_KL_PHU2_BA_KHONG` "khó giàu sang" (fires on 29%);
  - `TV_KL_AUX_TUAN_TRIET` "vui ít buồn nhiều" (34%);
  - `TV_TH_VERSE_MENH_TRIET_TUAN` and `TV_KL_PHU2_TUAN_TRIET` "thời trẻ nhiều vất vả" (34%);
  - `TV_KL_CUNG_PHU_MAU_HUNG` "cha mẹ vất vả, chẳng giàu" (46%);
  - `TV_TH_AUX2_TU_TUC_PHI_LIEM` "số con có phần ít đi";
  - `TV_TH_AUX2_MENH_KK_DAO_HONG` "duyên nợ dang dở, phải trải qua vài lần cưới xin".
  
  Effects:
  - The UI (`ui.js:16`) prints "Có thể nhận thấy một dấu hiệu liên quan đến … quỷ quyệt", not "Điều kiện hạn chế".
  - `conflict.resolve` cannot pair these readings.
  - The TS interpret pipeline uses the same field to build its support and counter themes.
- **Fix:** add a polarity field (or set `effect: limit`) in the builders. Add an integrity test that fails on negative lexemes with `support`. The list is in `scratchpad/a`, as output of the inline scan; it can be regenerated.

### RL-5 (P1): Evidence inflation: the same trigger is counted many times, and `_merge_corroborated` almost never merges

- **Root cause:**
  - `_merge_corroborated` (`api.py:208`) keys on `(subject, claim, effect)`.
  - Builders mint a claim id per rule, and some deliberately add a `__<rule>` suffix: 21 such ids, for example `duong_mui_dau_cham_sau_luoi` and `…__tt_menh_duong_than`, which have the identical text.
  - 1,110 distinct claim ids serve 1,138 verified findings. 62 identical reading texts are spread over 145 claim ids.
- **Static count:** 250 verified rules share an identical normalised condition with another rule, in 116 groups (71 of them cross-pack). Examples:
  - 4× Lộc Tồn @ Tài Bạch: KL p.216, TT ×2, TT p.159;
  - 4× Tả/Hữu @ Mệnh;
  - 4× Song Lộc @ Mệnh;
  - 3× Tuần/Triệt @ Mệnh.
- **Reference chart:**
  - **Lộc Tồn and Thiên Mã @ Thân give 7 verified cards:** Tài Bạch ×6 (`KL_CUNG_TAI_BACH_LOC_MA`, `KL_CUNG_TAI_BACH_LOC_TON`, `TH_CACH_TAI_BACH_LOC_MA`, `TH_P2_TAI_BACH_MA_TON`, `TT_PAL_TAI_BACH_LOC_TON_BASE_P`, `TT_PHU_TAI_BACH_LOC_TON`) plus Mệnh `KL_PHU_VU_LOC_MA`. Only 1 of these was merged.
  - Điền Trạch Cơ Cự Mão ×4: KL p.80, TH p.111 ×2, TT p.88.
  - Quan Lộc Tử–Tướng ×2: TT p.78–80, the same sentence seen from both stars.
  - Overall: 52 cards but only 41 distinct (palace, trigger-star set) pairs.
- **50-chart sweep:**
  - median 49 verified cards against a median of 34.5 distinct triggers, so **≈30% inflation**;
  - 5.2 extra cards per chart with an identical condition;
  - merge absorbs 0.8 cards per chart.
- **400-chart sweep:** 4.5 identical-condition extras per chart (390 of 400 charts affected); 9.7 identical-trigger extras (every chart).
- **Fix:**
  - Merge on a canonical condition signature (the `canon()` in `scratchpad/a/static.py`) **and** on normalised claim text.
  - Show one card with N book citations.
  - Count independent grounds by trigger, not by rule, wherever "corroboration" or strength is computed (TS planner `specificity` too).

### RL-6 (P1): Toàn Thư "Có sao X …; cùng Y …" entries: the base reading fires together with its own "cùng Y" refinement

- **Root cause:** `build_tt_palace_pack.py` emits `BASE` (star X present) and `WITH_Y` rules from one sentence. The base rule does not exclude the co-stars that the same sentence treats separately.
- **Evidence:** 72.7% of 2,000 charts show a base reading together with one of its own variants. The top cases are Phu Thê Thiên Đồng, Tài Bạch Vũ Khúc and Phúc Đức Cự Môn.
- **Reference chart:** "tự mình gây dựng nhà cửa, không hưởng của tiên tổ" (`TT_PAL_DIEN_TRACH_THIEN_CO_BASE_M`, a limit) sits next to the Cơ-Cự-Mão readings. TT p.88 (text checked): "Có sao Thiên Cơ tự mình gây dựng nhà cửa không được hưởng của tiên tổ ; **cùng Cự Môn tại Mão cung nhiều ruộng vườn nhà cửa**".
- **Fix:** the base rule should require that none of the sentence's `cùng` co-stars is present. This is source-supported by the sentence structure. There are 88 verified base rules.

### RL-7 (P1): Worked-example remarks are generalised into chart-wide rules

- **Rules:** `pack_khao_luan_cases.json`, 22 verified, cited as KL pp.238–246, "nguyên tắc nêu trong các lá số mẫu".
- **Evidence:** KL p.244 (image checked) is commentary on **one** example chart: "5. Người tuổi Mão nằm trong tứ chính, có tinh thần trách nhiệm cao…". `TV_KL_CASE_MENH_TU_CHINH` turns this into "every Tý/Ngọ/Mão/Dậu-year person" and fires on 34.8%. The siblings fire at similar rates:
  - `KL_CASE_MENH_KHONG_DAC_CHINH` 46.8% (from item 3, "Mệnh âm đóng cung dương **ở Thìn**");
  - `KL_CASE_MENH_TU_MO` 34%;
  - `DAC_CHINH_DUONG` 27%;
  - `GOC_PHA_NGON` 24.5%;
  - `CUC_KHAC_MENH` 20%;
  - `TAI_BACH_THAN` 16.8%.
- **Overlap:** these rules read no star (31 verified rules read only `palace.name` and `chart.*`). With `TV_TH_CACH_MENH_THUAN_LY`/`NGHICH_LY` (an exhaustive 52/48% pair), every Mệnh gets 2–5 generic cards.
- **Fix:**
  - Keep only the rules where the book states the principle in general terms (check p.238 for "đắc chính"); demote the rest to draft (NEEDS SOURCE).
  - Label generic, year-only rules as "chung cho mọi người tuổi …", as the TS pipeline already does with `specificity=0`. The Python UI does not.

### RL-8 (P1): Tuần/Triệt is ignored by the readings it should modify; the borrowing rule for vô chính diệu palaces does not exist

- **Evidence:** in the 400-chart sweep, 6,987 verified palace findings fall in a palace that has Tuần or Triệt. **5,838 (84%) come from rules that do not read Tuần/Triệt**, 4,474 of them favourable.
  - 46 verified rules *require* Tuần/Triệt (as a negative reading); 1 excludes it.
  - 20 verified rules test vô chính diệu, and **0** read the opposite palace's stars.
  - Reference chart: Thiên Di (Triệt) gives "sống ở bên ngoài nhiều" and "hay gặp người sang giúp". Tật Ách (Triệt) gives RL-1.
  - Books state Tuần/Triệt as a disqualifier on pages already cited: TH p.53 "Quyền gặp Tuần, Triệt, công danh trắc trở"; TH p.94; TH p.106.
- **Fix:** a palace-level modifier (Tuần/Triệt) attached as an exception to favourable star rules, but only where a cited page says so. This needs the reviewer's school decision (prior audit §7.3): NEEDS SOURCE for a general rule.

### RL-9 (P1): Deterministic family, marriage and children claims shown as verified findings

- **Evidence (rates over 2,000 charts):**
  - `TV_KL_CUNG_TU_TUC_PHU_TINH` "con cái dễ có, khá giả, xinh đẹp" fires on **60%**: any one of 10 minor stars, including Mộc Dục, Dưỡng and Trường Sinh. KL p.218 also says "Không có con có thể là lũ: Hình, Kỵ, … Tuần, Triệt" and that half is not encoded. The book itself warns that the probabilities "cũng chẳng đáng tin".
  - Marriage-count claims: `TH_P2_PHU_THE_KHONG_KIEP` "hai ba lần dang dở mới toàn" (14%), `TT_PAL_PHU_THE_PHA_QUAN_BASE_M` "hôn nhân dễ đổ vỡ" (8%), `…LIEM_TRINH_BASE_M` "nhiều lần dang dở" (8%), `…THAT_SAT_BASE_M` (8%), `TH_P2_PHU_THE_PHA_TT` "phải qua nhiều lần mới thành".
  - Children: `TH_P2_TU_TUC_HIEM_CON` "số hiếm con" (7%), `TT_PHU_TU_TUC_TU_VU` "nhiều con trai", `TH_P2_TU_TUC_DONG_AM` "đủ cả trai gái".
  - Wealth: "số nghèo khổ" ×2 (15%), "vốn dễ phá sản" (7.6%).
  - The pages support the wording (TH p.102 says "3 tao", softened to "nhiều lần").
- **Tật Ách:** no verified diagnosis readings exist. Tật Ách has only **1** verified rule (RL-1). No verified rule outputs death or illness, which is good.
- **Fix:** add a `sensitivity` tag (marriage count, children, poverty). For tagged rules, render as "sách xưa cho rằng…" with the book's own caveat, or exclude them from the default reading. Product decision.

### RL-10 (P2): About 30 verified rules can never fire, because "X hội Y" or "X, Y ở …" was encoded as both stars in one palace

- **Evidence:** 55 verified rules never fire in 2,000 charts. At least 30 are structurally impossible:
  - Tử Vi + Thiên Đồng / Thiên Cơ / Vũ Khúc in one palace (`TT_PAL_PHU_THE_TU_VI_WITH_THIEN_DONG_P`, `TT_PAL_PHUC_DUC_TU_VI_WITH_THIEN_CO_P`, `TT_PHU_TU_TUC_TU_VU`, "Tử Vi hội Vũ Khúc");
  - Thiên Tướng + Thiên Cơ / Thái Dương; Liêm + Đồng; Lương + Nguyệt;
  - both Khôi **and** Việt in Mệnh (`KL_PHU_KHOI_VIET_MENH`, `TT_MENH_KHOI_VIET_MENH`);
  - Xương + Khúc + Lộc Tồn; Xương Khúc in Tỵ/Hợi; Vũ Phá + Xương Khúc (KL p.54 #2 says "gặp Xương Khúc", either star);
  - Song Hao, Tang–Hổ, Lực Sĩ + Tướng Quân, Tấu Thư + Bác Sĩ, Thanh Long + Lộc Tồn (KL p.229 and TH pp.99, 101, 108, 110 name pairs that are always opposite or apart);
  - Tham Lang + Kình Dương at Dần (TT p.159 #98: Kình never stands at Dần. The book adds "Nếu không có Kình Dương thì Đà La cũng vậy", and that variant is missing).
  
  Some of these are faithful to wording that is physically impossible.
- **Fix:** an integrity test that enumerates co-location feasibility (the sweep already does this), plus re-reading "hội" as tam hợp/chiếu and "Khôi Việt"/"Song Hao" as "either star". NEEDS SOURCE per rule for the reading of "hội".

### RL-11 (P2): Page and condition mismatches found in the sample

- **`TV_TH_P2_HUYNH_DE_TT` (fires on 31.5%).** TH p.99 says "Triệt Tuần **xung củng**, đấu đàng **ly tông**", which is Tuần/Triệt chiếu into the palace, with the meaning "leave the clan". The rule tests Tuần/Triệt **in** Huynh Đệ and claims "anh em ít, mỗi người một ngả". "chẳng nhiều" belongs to the next line (Địa Kiếp, Thiên Không). This is the only Huynh Đệ reading the reference chart gets.
- **`TV_TH_STAR_THIEN_PHU_NAM_TUAN_TRIET`.** Địa Không is accepted anywhere in the tam phương including xung chiếu (prior audit §7.2, still open). It fires on the reference chart from Địa Không in Thiên Di.
- **`TV_TH_AUX2_QUAN_LOC_KK_HAM`.** "hãm" is a branch list (not Dần Thân Tỵ Hợi) instead of the dignity table, and the effect is wrong (RL-4).
- **Asymmetric verification:** "Hóa Quyền gặp Tử, Phủ" is verified (TH p.53, supported), while "Quyền gặp Sát tinh… thất bại" on the same page is draft. The reference chart has Hỏa Tinh, Địa Không and Địa Kiếp in the Mệnh tam phương, so only the flattering reading shows.
- **`TV_KL_DHK_06_NGO` (chart level).** It fires for every Ngọ-year person. Prior audit #25 fixed the generic label only in TS; the Python UI shows it unlabelled.

### RL-12 (P2): Vận rules are outside the review system

- **Evidence:**
  - `data/van_han_rules.json` holds 28 rules with no `reviewStatus`, a single range citation ("Khảo Luận pp.233-236"), and the editorial voice "theo sách…" inside the reading text. The prior audit (#29) stripped that voice only in TS.
  - `van_han_tt.py` (TT pp.97–105) is code, not data.
  - Opposite vận readings are reconciled by one generic sentence (`van_han.py:115`).
- **Fix:** move them to the KnowledgeRule schema with per-rule pages and a review status.

---

## Page checks (18 rules)

| Rule | Cited | Verdict |
|---|---|---|
| `KL_CUNG_TAT_ACH_CUOI_DOI` | KL p.218 | **Partial:** omits "Tối kỵ … Tham lang, Hóa kỵ, Không Kiếp", splits pairs, widens Hóa to the tam phương (RL-1) |
| `KL_CUNG_PHU_THE_TT` | KL p.217 | Supported ("chỉ nói lên cuộc hôn phối xảy ra trong một hoàn cảnh đặc biệt") |
| `KL_CUNG_PHU_THE_DEP_DOI` | KL p.217 | Supported, but the same paragraph's "Kình Đà Không Kiếp thì dễ tan vỡ" is draft only (RL-2) |
| `KL_CASE_MENH_TU_CHINH` | KL p.244 | **Overgeneralised:** one example, "tuổi Mão" (RL-7) |
| `TH_AUX_MENH_HQ_TU_PHU` | TH p.53 | Supported; the "Quyền gặp Sát" line on the same page is draft (RL-11) |
| `TH_AUX2_QUAN_LOC_KK_HAM` | TH p.68 | Text supported; **effect inverted** (RL-4) |
| `TT_PAL_PHUC_DUC_THIEN_VIET_BASE_P` | TT p.84 | Supported (the book says "Khôi Việt") |
| `TT_PHU_TAI_BACH_LOC_TON` | TT p.159 #103 | Supported |
| `TT_PHU_MENH_THAM_KINH_DAN` | TT p.159 #98 | Faithful but impossible; the Đà La variant on the same line is missing |
| `TH_CACH_TAI_BACH_LOC_MA` | TH p.72 | **Name list only;** "đồng cung" not in the source (RL-3) |
| `KL_CUNG_TAI_BACH_LOC_MA` | KL p.216 | Supported; the "Không Kiếp … thì nghèo" breaker is not encoded |
| `KL_CUNG_PHU_MAU_SAO_TOT` / `_HUNG` | KL p.220 | Both supported; co-fire on 19% (RL-2) |
| `TT_PAL_DIEN_TRACH_THIEN_CO_BASE_M` | TT p.88 | **Overridden** by "cùng Cự Môn tại Mão" in the same sentence (RL-6) |
| `TT_PHU_MENH_PHU_TUONG_DONG_LUONG` | TT p.151 | Supported |
| `TH_STAR_THIEN_PHU_NAM_CAT` / `_TUAN_TRIET` | TH p.94 | Supported, but "Nhưng" makes the second a disqualifier of the first (RL-2) |
| `KL_PHU_VU_LOC_MA` | KL p.54 #3 | Supported; #2 and #8 on the same page are encoded as impossible (RL-10) |
| `TH_P2_TAI_BACH_MA_TON` | TH p.106 | Supported; "Tuần Triệt trước đất cũng không" is not encoded |
| `TH_P2_HUYNH_DE_TT` | TH p.99 | **Mismatch:** "xung củng", "ly tông" (RL-11) |
| `TH_P2_PHU_THE_PHA_TT` | TH p.102 | Supported ("3 tao" → "nhiều lần") |
| `TH_VERSE_MENH_THAI` | TH p.85 | Supported |
| `KL_AUX_TUE_PHA`, `KL_AUX_TUONG_QUAN` | KL p.229 | Supported; the Song Hao and Tang Hổ rules from the same list are dead (RL-10) |

No page-number offsets were found: printed page equals PDF page, and every sampled quote is on the cited page.

---

## Coverage

### Verified rules and firing per palace (400-chart sweep, verified cards after merge)

| Palace | Rules (all / verified) | Charts with ≥1 card | Median cards | Mean |
|---|---|---|---|---|
| Mệnh | 676 / 598 | 100% | 22 | 23.3 |
| Tài Bạch | 114 / 96 | 92% | 3 | 3.4 |
| Quan Lộc | 93 / 78 | 87% | 2 | 2.6 |
| Thiên Di | 89 / 78 | 100% | 4 | 4.2 |
| Phu Thê | 77 / 55 | 89% | 2 | 2.7 |
| Phúc Đức | 77 / 64 | 93% | 2 | 2.7 |
| Điền Trạch | 65 / 55 | 83% | 2 | 2.4 |
| Nô Bộc | 55 / 48 | 79% | 1 | 1.6 |
| Phụ Mẫu | 45 / 35 | 88% | 2 | 2.2 |
| Tử Tức | 14 / **9** | 76% (60% from one rule) | 1 | 1.1 |
| Huynh Đệ | 9 / **6** | 56% | 1 | 0.7 |
| Tật Ách | 1 / **1** | 88% (that one rule) | 1 | 0.9 |
| chart-level | 12 / 12 | 100% | 1 | 1.0 |

Mệnh holds 52% of the verified rules and 47% of a chart's cards. Tật Ách, Huynh Đệ and Tử Tức are effectively unread. Their high "charts with ≥1 card" figures come from the generic rules in RL-1, RL-9 and RL-11.

### Stars in verified rule conditions (98 stars appear in charts; 65 are used)

- **Chính tinh:** each is used by 67–148 rules (Tử Vi 148, Thiên Cơ 111, Vũ Khúc 108 … Thất Sát 67).
- **Lục cát and lục sát:** 20–67 each (Hữu Bật 67, Tả Phụ 66, Văn Xương 66, Văn Khúc 63; Địa Không 42, Địa Kiếp 41, Kình 40, Hỏa 36, Linh 30, **Đà La 20**).
- **Lộc Tồn 74, Thiên Mã 42, Khôi and Việt 39 each.** "Phúc Đức" scores 64, but that number is inflated by the palace of the same name.
- **Minor stars:** Hồng Loan 21, Đào Hoa 18, Song Hao 12, Thái Tuế 11, Thiên Không 7, Tấu Thư and Tướng Quân 7. Every other minor star is used by ≤6 rules.
- **Unused (33):** Thiên Hình, Thiên Riêu, Thiên Khốc, Thiên Hư, Hoa Cái, Cô Thần, Quả Tú, Long Trì, Phượng Các, Tam Thai, Bát Tọa, Ân Quang, Thiên Quý, Thiên Quan, Thiên Phúc, Thiên Đức, Nguyệt Đức, Long Đức, Thiên Thọ, Thiên Tài, Thiên Y, Thiên La, Địa Võng, Địa Giải, Thiên Giải, Đẩu Quân, Kiếp Sát, Phá Toái, Lưu Hà, Thiên Thương, Thiên Sứ, Tử, Bệnh.
  - Some are cited on pages already encoded: KL p.218's Tử Tức list includes Long Trì, Phượng Các and Thiên/Nguyệt/Long Đức; "Khốc Hư Tí Ngọ" appears at TH p.85 and TT p.159 #109 (it applies to the reference chart's Mệnh).

### Other structural features (verified rules)

| Feature | Count |
|---|---|
| Uses the merged tam phương (own + tam hợp + xung chiếu, prior audit §7.2) | 138 |
| Uses role-typed positions | 42 |
| Tests brightness | 201 |
| Tests branch | 231 |
| Tests gender | 72 |
| Tứ Hóa leaves (no inter-palace Hóa interaction) | 108 |
| Hóa Kỵ as a trigger | 15 |
| Hóa Kỵ as an exclusion | 0 |
| Giáp (flank) | 26 |
| Thân cư (`is_than`) | 5 |
| Cục / Mệnh–Cục relation | 2 |
| Vô chính diệu | 20 (0 with borrowing) |
| Exceptions | 2 |
| `conflictsWith` | 0 |
| Never fire in 2,000 charts | 55 |

---

## Firing rate (verified rules, 400 charts; the 2,000-chart run agrees within ±4 pt)

| Rate | Rule | Effect | Reading (abridged) |
|---|---|---|---|
| 88.0% | TV_KL_CUNG_TAT_ACH_CUOI_DOI | support | về già sung túc, an nhàn |
| 60.5% | TV_KL_CUNG_TU_TUC_PHU_TINH | support | con cái dễ có, khá giả, xinh đẹp |
| 52.0% | TV_TH_CACH_MENH_NGHICH_LY | limit | giờ sinh nghịch lý: độ số kém bớt |
| 48.0% | TV_TH_CACH_MENH_THUAN_LY | support | giờ sinh thuận lý (complement of the row above: 100% of charts get one) |
| 46.8% | TV_KL_CASE_MENH_KHONG_DAC_CHINH | limit | ra đời gặp trở ngại lúc ban đầu |
| 46.2% | TV_KL_CUNG_PHU_MAU_SAO_TOT | support | cha mẹ khá giả, con cái hòa thuận |
| 46.2% | TV_KL_CUNG_PHU_MAU_HUNG | support (sic) | cha mẹ vất vả, chẳng giàu |
| 41.2% | TV_TH_CACH_MENH_MUA_SINH | support | thuận mùa sinh |
| 35.0% | TV_KL_CUNG_PHU_THE_DEP_DOI | support | vợ chồng hòa thuận, đẹp đôi, bền lâu |
| 34.8% | TV_KL_CASE_MENH_TU_CHINH | support | tinh thần trách nhiệm cao (year branch only) |
| 34.0% | TV_TH_VERSE_MENH_TRIET_TUAN / TV_KL_PHU2_TUAN_TRIET / TV_KL_AUX_TUAN_TRIET | support (sic) | thời trẻ vất vả / vui ít buồn nhiều (3 rules, 1 trigger) |
| 34.0% | TV_TH_P2_PHUC_DUC_TT | limit | phúc bị kìm hãm |
| 34.0% | TV_KL_CASE_MENH_TU_MO | limit | phải cố gắng giành chỗ đứng |
| 32.2% | TV_TT_PHU_MENH_PHU_TUONG_DONG_LUONG | support | tính tình hiếu thuận |
| 31.5% | TV_TH_P2_HUYNH_DE_TT | limit | anh em ít, mỗi người một ngả |
| 29.2% | TV_KL_PHU2_BA_KHONG | support (sic) | khó giàu sang |
| 28.5% | TV_KL_CUNG_PHU_THE_TT | support | hôn nhân trong hoàn cảnh đặc biệt |
| 27.8 / 27.3 / 27.0% | TV_KL_MENH_{TU_PHU_VU_TUONG, SAT_PHA_LIEM_THAM, CO_NGUYET_DONG_LUONG} | neutral | star-group classification |
| 27.0% | TV_KL_CT_CNDL | support | hàng trí thức, công bộc |
| 27.0% | TV_KL_CASE_MENH_DAC_CHINH_DUONG | support | đúng chỗ của mình |
| 26.5% | TV_TT_PHU_MENH_SAT_KIEP_THAM | limit | tính tình thất thường |
| 26.2% | TV_KL_CASE_MENH_DAC_CHINH_AM | support | mềm dẻo, khôn khéo |
| 25.8% | TV_TH_AUX_MENH_DH_CHIEU | support | đẹp hơn khi Đào Hồng xung chiếu |
| 25.8% | TV_KL_CT_NHAT_NGUYET_CHIEU | support | thông minh sáng suốt, dễ thành công |

- 26 verified rules fire on more than 25% of charts, and about 95 on more than 10%.
- Draft rules with high rates are hidden by the UI: `KL_CUNG_DIEN_TRACH_NGHEO` 62%, `KL_CUNG_TAI_BACH_KHONG_KIEP` 57%, `KL_CUNG_THIEN_DI_QUY_NHAN` 49%, `TV_STRUCT_SAT_PHA_THAM_001` 100%.
- 1,046 of 1,139 verified rules fired at least once in 400 charts.

---

## Proposed order of work

1. **RL-1 and RL-9:** demote or re-condition the three near-universal family/old-age rules (Tật Ách, Tử Tức phụ tinh, Phụ Mẫu pair).
2. **RL-4:** fix the effect sign (mechanical).
3. **RL-5:** merge by condition signature and normalised text (code-only, in `api.py`).
4. **RL-2 and RL-3:** encode same-page disqualifiers as `exceptions` (sources listed above), add `conflictsWith` for same-page opposite pairs, and extend `conflict.resolve` to same-trigger opposite effects.
5. **RL-6:** TT base rules exclude their `cùng` co-stars.
6. **RL-7 and RL-8:** reviewer decisions (worked-example generalisation; Tuần/Triệt as a general modifier). NEEDS SOURCE.
7. **RL-10 to RL-12:** feasibility test, page fixes, vận rules into the schema.
