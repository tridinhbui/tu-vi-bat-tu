# Interpretation engine audit (2026-10-18)

**Scope.** I audited the whole interpretation path of Thiên Bàn at `origin/main` 6c10cf5:

- calculation (`engine/tvbt/tuvi.py`, `aux_stars.py`, `bazi.py`, `temporal.py`);
- the rule packs (`engine/data/pack_*.json`) and the rule engine (`engine/tvbt/reasoning/`, `knowledge/`);
- the production report (`/api/reasoning`, `/api/analysis`, `/api/year`, `engine/web/js`);
- the flagged-off layers (`synthesis/`, `bazi_deep/`, `src/interpret/`).

**Reference chart.** 17/05/1990 10:30, nam, TP.HCM. Its 20-page production PDF (`~/Downloads/Thiên Bàn — Tử Vi và Bát Tự.pdf`, printed 18/10/2026 13:48) is the before-state.

**Method.** Four read-only sub-audits gathered the evidence. Their full reports are in [audit/](audit/):

- [bazi.md](audit/bazi.md)
- [tuvi-calc.md](audit/tuvi-calc.md)
- [rules.md](audit/rules.md)
- [architecture.md](audit/architecture.md)

I re-checked every P0 below on the printed page before changing code. Book pages are PDF pages; for these books the PDF page equals the printed page.

**Who reviewed what.** All of this is the assistant's work. **No practitioner has reviewed it.** "Verified" means only that the cited page says what the rule or qualifier says. It does not mean the doctrine has been validated.

Severity: **P0** = wrong or misleading output now; **P1** = important gap; **P2** = polish.

Status: **FIXED** (in this branch, tested) · **MITIGATED** (the evidence layer exposes or contains it, but the root data is unchanged) · **OPEN** · **NEEDS SOURCE** · **NEEDS DECISION** (a convention only the owner or a reviewer can choose).

---

## 1. P0 findings

| ID | Finding | Root cause | Components | Evidence | Fix | Status |
|---|---|---|---|---|---|---|
| TV-1 | Thiên Quý counted in the wrong direction (wrong on ~25 of 30 birth days; reference chart: Ngọ instead of Tý) | formula counted thuận from Văn Khúc | `aux_stars.py` | KL p.28 ("đếm nghịch đến ngày sinh … lùi lại một cung"), TH p.19 | `Khúc − (day − 2)` | **FIXED**, `test_thien_quy_counts_backward_from_van_khuc_kl_p28` |
| TV-7 | The year card "Lưu Tứ Hóa theo sách" printed KL pp.195-197 advice ("lanh chanh, soi mói…", "dễ mang nỗi nhục về tiền bạc") for the flow year | KL pp.195-197 is about the **birth-year** stem ("Tuổi Bính…", "suốt đời"); none of the three books has a lưu Tứ Hóa rule (KL pp.41-42 and TH p.114 list nine lưu stars, no Tứ Hóa) | `temporal.tuvi_year`, `web/js/tuvi.js`, `ui.js` | KL pp.41-42, 195-197 | positions only, labelled "thông lệ phổ biến, chưa đối chiếu sách"; the natal Tứ Hóa advice (Tuổi Canh) stays in `analysis.py`, where it is correctly applied | **FIXED**, `test_luu_tu_hoa_is_not_given_birth_year_advice` |
| BZ-1 | Thiên can xung/khắc table had 4 pairs, labelled verified against 八字真宗 p.20, which prints 10 (and calls 甲庚 克, not 冲); the 2026 Bính against natal Canh was missing | incomplete transcription | `bazi.py`, `temporal.py`, `compare.py` | ZZ p.20 「干冲克」 | `STEM_CLASH_KIND` with 10 pairs and kind xung/khắc. bazi_deep and compare_deep keep the old 4-pair set (`STEM_CLASH_LEGACY4`), because their draft effect sizes were calibrated on it | **FIXED**, `test_stem_clash_table_is_the_ten_pairs_of_zz_p20` |
| BZ-2 | Hình was only reported when all three branches of 寅巳申 / 丑戌未 were present | the page states 刑 pair by pair | `bazi.py` | ZZ p.20 「支三刑」; p.19 grid (巳申 = 合·刑·破) | `PENALTY_PAIRS` → natal `branch_penalty` kind "tương hình" | **FIXED**, `test_pairwise_penalty_zz_p20` |
| BZ-3 | Đại vận / lưu niên × natal never reported any hình (2026 Ngọ × natal Ngọ, đại vận Thân × natal Tỵ) | `_rel_with_natal` had no 刑 | `temporal.py` | ZZ pp.19-20 | pair 刑, 子卯 and 自刑 on repeated 辰午酉亥 | **FIXED**, `test_reference_2026_year_and_luck_interactions_include_hinh_and_bing_geng` |
| RL-1 | "Về già sung túc, an nhàn" (Tật Ách) fired on 88% of charts, including palaces holding Tham Lang, Không Kiếp or Hóa Kỵ | (a) "Khoa Quyền Lộc" read in the whole tam phương instead of the palace; (b) the "Tối kỵ … Tham Lang, Hóa Kỵ, Không Kiếp" sentence on the same page was not tested | `tools/build_kl_palace_pack.py` → `pack_khao_luan_cung.json` | KL p.218 | stars and Hóa in the palace, plus the exclusion; fixed in the builder, then the pack was regenerated and `fix_giap` run | **FIXED** (88% → 46% on 200 charts), `test_tat_ach_rule_tests_the_exclusion_on_kl_p218` |
| RL-5 / AR-3 | One chart fact shown as many "căn cứ". Reference chart: Lộc Tồn + Thiên Mã at Thân gives 7 cards; Cơ Cự Mão gives 4. 250 verified rules share an identical condition with another | one finding per rule; `_merge_corroborated` merges only identical claim ids | `api.py`, UI | [audit/rules.md](audit/rules.md) RL-5 | conclusion layer: trigger atoms → nested-trigger clusters; support is counted in **books**, not rules. Each conclusion says "N câu từ K sách … là một căn cứ" | **MITIGATED** in `/api/interpretation`; production cards unchanged (§4) |
| RL-2 / AR-1 | Opposite readings shown side by side with no relation (e.g. "quyền quý" vs "khó đạt công danh"); conflict resolution never fires | `conflict.resolve` groups by identical claim id, and no rule declares `conflictsWith` | `reasoning/conflict.py` | 1401 claims for 1437 rules | conclusion layer pairs support and limit in the same palace by shared trigger or topic. Each pair gets a relation kind (`same_trigger`, `nested`, `coexisting`, `complementary`), and is never averaged or scored | **MITIGATED** (evidence layer). `conflict.py` itself unchanged |
| AR-4 | Production cards print "Điều kiện hạn chế: hạn chế: …" | `limit:` claim phrases already start with "hạn chế:" | `web/js/ui.js` | UI | strip the duplicate prefix | **FIXED** |
| BZ-4 | Draft "thiếu hành" rule (`BT_ZZ_MISSING_THỔ`) fires on a chart that holds 4 Thổ hidden stems | `missing_elements` ignores hidden stems; ZZ p.27 uses 缺 as a strength level, not "not visible" | `reasoning/facts.py`, `pack_bazi_zhenzong.json` | ZZ p.27 | the app already drops drafts (`app.js` keeps only verified findings). The operational definition of 缺 is not on the page | **NEEDS SOURCE**; the drafts stay hidden |

## 2. P1 findings

| ID | Finding | Status / action |
|---|---|---|
| TV-10 | Lưu Kình/Đà ignored KL p.42's direction (dương nam / âm nữ thuận, else nghịch). Lưu Tang Môn, Bạch Hổ, Khốc and Hư (KL p.41) were missing | **FIXED** in `temporal_facts.luu_tinh`, with page labels per star. The book's own Lưu Hư example contradicts its rule; the rule is used (see the docstring). Test: `test_luu_kinh_da_direction_follows_kl_p42` |
| RL-3 | No disqualifiers in production. Named configurations (Lộc Mã giao trì, etc.) were judged by name | **MITIGATED**: `data/qualifiers.json` holds 9 page-checked qualifiers (KL pp.140, 141, 142, 197; TT p.20), evaluated per conclusion as met / not met / unknown, with their open questions. Unsourced breakers in `formations_experimental.json` stay experimental |
| RL-4 / AR-2 | ~55 negative readings marked `effect: support`; polarity was guessed from words in a flagged-off module | **MITIGATED**: conclusion polarity = rule effect, else the tone of the reading (`claim_tone`); mixed tone stays neutral and is never set against anything. The pack `effect` fields are unchanged. **OPEN**: fix at the builders |
| RL-6 | Toàn Thư base readings ("Có sao X") fire next to their own "cùng Y" refinement on 73% of charts | **MITIGATED**: these become one cluster or a `nested` relation. The "narrower reading first" convention is **not applied** (NEEDS DECISION, §5.1) |
| RL-7 | Worked-example remarks turned into general rules (e.g. "tuổi Tý Ngọ Mão Dậu → trách nhiệm cao", 35% of charts) | **MITIGATED**: conclusions resting only on birth-year or sex facts are flagged `generic`, kept apart and never counted as evidence for the chart. **OPEN**: demote at the builders |
| RL-8 / AR-5 | Tuần/Triệt ignored by the readings it should modify. No vô chính diệu borrowing | **FIXED (layer)**: KL p.141 Tuần/Triệt is a qualifier on every reading of the palace. TT p.18 borrowing (xung chiếu as chủ, tam hợp as khách; both empty → only khách) is in the dossier. The rules themselves are not re-evaluated with borrowed stars, because no source says the borrowed stars act like the palace's own |
| RL-9 | Deterministic family claims ("hôn nhân phải qua nhiều lần mới thành", "con cái dễ có") | **MITIGATED**: Phu Thê / Tử Tức / Tật Ách get a scope guard in every chapter. **NEEDS DECISION**: whether to demote these rules to draft |
| TV-2 | Lưu Hà table matches neither book for Canh, Đinh, Tân (KL p.29 ≠ TH p.26 ≠ code) | **OPEN, NEEDS DECISION** (the books disagree; pick a school). The star is unverified and used by no rule |
| TV-3 | KL pp.74-115 brightness for the 14 chính tinh is not in the repo and differs from TH on 7/14 cells of the reference chart (e.g. Thái Dương Sửu: TH hãm, KL đắc; Vũ Khúc Tý: blank in TH, vượng in KL/TT) | **OPEN**: needs a transcription from page images and a school selector. The engine already reports "bảng đang dùng không ghi vị trí này" for unspecified cells |
| TV-4/5 | The Canh (Đồng Khoa/Âm Kỵ vs Âm Khoa/Đồng Kỵ) and Nhâm (Tả Phụ vs Thiên Phủ Khoa) disputes are not disclosed in the UI | **OPEN** (data exists in `experimental/tu_hoa_tables.json`) |
| TV-6 | Tiểu hạn direction: KL pp.39-40 uses âm/dương; the code follows TH p.27 (nam thuận, nữ nghịch). The two differ for every âm-stem birth | **NEEDS DECISION** (silent school choice today) |
| TV-8 | UI "cát n · hung m" counts use uncited sets that include unverified-placement stars (the wrong Thiên Quý among them) | **OPEN**. The evidence layer uses only Lục cát / Lục sát, Lộc Tồn and Thiên Mã, from verified placements |
| TV-11 | Đại hạn Tứ Hóa (by the decade palace's stem) has no source, yet the flagged synthesis marks it as checked | **MITIGATED**: the period chapter labels it NEEDS SOURCE |
| BZ-5/6 | Luck-pillar year labels and "Hiện tại" can be a year off; Python, TS and the frontend disagree on 2026 (TS says Ất Dậu, which only starts 23 Dec) | **OPEN** |
| BZ-7 | Late-Tý option pairs today's day pillar with today's Tý stem | **NEEDS SOURCE** |
| BZ-8 | Northern births 1960–75 mapped to Asia/Ho_Chi_Minh (UTC+8 then) are 1 h off | **OPEN** (place → tz mapping) |
| BZ-9/10 | Strength: the verified TVH 40% rule gives nhược (38.4%) for the reference chart, but bazi_deep adds an invented ±3% band and the timeline forces another method | **FIXED (layer)**: `bazi_reading.strength_tvh` applies the book's rule strictly and says so; ZZ p.27 three-test rule shown alongside; no verdict invented when they disagree |
| BZ-11 | "Verified" temporal rules sit on draft premises (cách cục table from memory) | **OPEN** (engine: effective basis = min(rule, premise)) |
| BZ-12 | 八字真宗 direct-judgement rules loaded but never fired (`zz=True` unused); 126/300 charts would get both a good and a bad marriage reading | **OPEN**: keep off until a conflict policy is chosen (NEEDS DECISION) |
| AR-6 | Four interpretation stacks (production, synthesis, deep-reading, TS) disagree on the same chart; tam phương computed in 9+ places | **OPEN**: the new layer reuses `positions.py`, the rule engine and `temporal_facts` instead of adding a fifth taxonomy (see REASONING-ENGINE-DESIGN.md §8 for the retirement plan) |
| AR-7 | `/api/deep-reading?experimental=true` → HTTP 500; `/api/synthesis` with `toan_thu` depends on the previous request | **OPEN** (flagged-off) |

## 3. P2 findings (abridged; details in audit/)

- Stale scope text (scope.js says thần sát / nạp âm are not placed) — BZ-13.
- Bán hợp not reported — BZ-14.
- "vô ân / thị thế" names not on the cited page — BZ-15.
- Distant hợp shown as "tiềm năng hóa" with no distance. **FIXED in the layer**: `span` is given, plus TVH pp.336-338 (only adjacent ngũ hợp transform) — BZ-16.
- `analysis.py` relations sentence omits hình — BZ-17.
- The element bar chart double counts. The layer labels counts as counts, never as strength — BZ-18.
- Age labels do not say tuổi thực vs mụ — BZ-19.
- No near-boundary warning — BZ-21.
- ~30 aux formulas labelled "unverified" are printed in KL pp.26-36 and TH pp.19-27 — TV-9.
- Trường Sinh school variant (KL pp.33-34) not disclosed — TV-12.
- Leap-month citation out of context — TV-13.
- 23h convention unsourced — TV-14.
- Mệnh chủ / Thân chủ unsourced (no table in KL/TH/TT). The dossier says so — TV-17.
- ~30 rules can never fire ("hội" read as same palace) — RL-10.
- Vận rules outside the review system — RL-12.

## 4. What is unchanged in production on purpose

- The production readings, their rule packs (except RL-1) and the `/api/reasoning` payload are unchanged.
- The evidence layer is behind `TVBT_DEEP_INTERPRETATION` (`POST /api/interpretation`, plus a "Luận giải có căn cứ (thử nghiệm)" box in the chapters when the endpoint answers).

**Visible production changes when this branch ships:**

- Thiên Quý position (TV-1).
- More Bát Tự relations: the 6 extra 干冲克 pairs, pairwise hình, hình in year and luck.
- Fewer Tật Ách "về già sung túc" readings.
- The lưu Tứ Hóa card without book advice.
- No "hạn chế: hạn chế:".

## 5. Decisions needed (owner or reviewer)

1. **Precedence convention.** Should a narrower rule be read before a broader one in the same palace (the TS pipeline's "narrower first")? Today it is reported as `nested` and **not applied**.
2. **Toàn Thư tr.20 wording.** "Đồng hành" (Tử Vi with Tả Hữu): tam phương (system reading) or same palace? And what does "không vong" mean on that page?
3. **KL tr.142 "Không Kiếp chiếu" (lộc đảo).** Is one of the two stars enough? Does the rule apply to Lộc Mã in the same palace outside Mệnh–Thiên Di?
4. **Toàn Thư tr.18 "thành phá".** Is "Quý" = Thiên Khôi / Thiên Việt? Is the "sao tốt in bản cung" precondition needed for the 14 chính tinh?
5. **Schools.** Tiểu hạn direction (KL vs TH). Chính tinh brightness (TH vs KL tables). Lưu Hà table. Canh / Nhâm Tứ Hóa disclosure.
6. **Family claims.** Should "hôn nhân phải qua nhiều lần", "con cái dễ có, khá giả" and similar be demoted to draft?
7. **八字真宗 direct judgements.** Conflict policy before `zz=True` is wired.

## 6. Production readiness

- The calculation fixes and the RL-1 rule fix are source-verified and tested. They are safe to ship once the owner approves.
- The evidence layer is **not production-ready as a primary reading**:
  - it has had no practitioner review;
  - 9 qualifiers cover only a few high-frequency configurations;
  - polarity still depends partly on wording;
  - the decisions in §5 are open.
- It is ready for internal review behind the flag. See INTERPRETATION-QUALITY-REPORT.md.
