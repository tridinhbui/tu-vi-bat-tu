> Evidence file of the 2026-10-18 interpretation-engine audit (read-only sub-audit, consolidated in ../INTERPRETATION-ENGINE-AUDIT.md). Paths under `scratchpad/` refer to the auditing session's temporary folder and are not in the repository. Statuses here are as found on 6c10cf5, BEFORE the fixes; see the consolidated audit for what was fixed.

# Architecture audit: the interpretation and report pipelines

Scope: worktree `interp-engine-audit` at 6c10cf5. The audit was read-only. Paths are relative to the repo root; `engine/` holds the Python code and `src/` the TypeScript.

Reference chart: 17/05/1990 10:30, male, lon 106.7.
- Production outputs are in `scratchpad/ref_1990_{chart,reasoning,analysis,year,facts}.json`.
- TypeScript chapter outputs are in `scratchpad/ts/ts_<chapter>.json`.
- Synthesis and deep-module outputs are in `scratchpad/py/*.json`.
- Frontend simulation scripts are in `scratchpad/fe/`.

Baseline tests:
- Python: 1293 passed, 2 skipped, 2 xfailed (109 s).
- TypeScript: `node --test src/interpret/test/*.test.ts` gives 76 pass, 0 fail.

Note: `engine/tvbt/reasoning/conclusions.py` appeared as an untracked file while this audit ran. It is a conclusion/cluster layer that some other session is still writing. It is **not** part of the audited baseline, but section 6 is written to fit it.

---

## 1. Pipeline map

### 1a. PRODUCTION (live, no flag)

```
BirthReq ─► calendar_core.normalize ─► bazi.compute / tuvi.compute   (api.py:44-49, _compute)
   │
   ├─/api/chart ───────────── dataclasses.asdict(bz, tv) ──────────────────────────────► board UI (tuvi.js, bazi.js), "Dữ kiện tính toán", p12
   │
   ├─/api/reasoning (api.py:233-255)
   │    load_all()  (1437 rules, 25 packs, re-read from disk on every request, ~12 ms)
   │    facts.tuvi_facts(tv) ─┐   facts.bazi_facts(bz)
   │      (+positions.typed_facts: self/opp/trine/flank/nhi_hop roles, khi counts, dignity_rank)
   │    engine.run(rules, base, system)  forward chaining, (rule, subject) fires once, MAX_DEPTH 6   (reasoning/engine.py:99-196)
   │      → Finding{id, subject, claim, effect, rule_id, depth, status, basis, notes} + provenance graph Node/Edge
   │    nlg.build_interpretations → conflict.resolve (groups by (subject, claim))   (nlg/generate.py:86-101, reasoning/conflict.py:27-94)
   │    nlg.realize/render → systems.*.text   (never read by the UI)
   │    _merge_corroborated: one card per (subject, claim, effect)   (api.py:208-222)
   │    → {findings[+why chain, corroborated_by], pending, blocked, conflicts(=derived-fact only), text}
   │                                    │
   │                                    ▼  app.js:142 keeps basis==='verified' only
   │                       report.js chOf()/topicChapter (facet from /api/claims) → chapter cards, p12 "NHẬN ĐỊNH",
   │                       beginner.js classify()/isCare → "Điểm cần cân nhắc" (easy mode, now dead at HEAD)
   │
   ├─/api/analysis (api.py:59-64 → analysis.analyse, analysis.py:154-339)
   │    View(tv,bz): own tam(), CAT/SAT lists, star_phrase; star_profiles.json, tu_hoa_vi.json; van_han.read per đại hạn
   │    → chapters{id: [Block{layer: Tượng|Khí|Thế|Cách|Dụng|Biến|Phản|Tổng, text, basis: tinh_toan|sach|he_thong, src[]}]}
   │                                    ▼ report.js:104 blocks() / blockSys() regex → "Phân tích cấu trúc" (pro mode only)
   │
   ├─/api/year (api.py:171-178 → temporal.bazi_year / tuvi_year, temporal.py:44-111)
   │    tiểu hạn palace + van_han.read (data/van_han_rules.json, its own mini rule set via dsl.evaluate),
   │    lưu Thái Tuế palace, lưu Tứ Hóa (natal landing + KL pp.195-197 advice), current đại hạn (no đại hạn Tứ Hóa)
   │                                    ▼ yearCard (beginner.js:79-96), yearExplorer (ui.js:50-91), tuvi.js drawer
   │
   └─/api/claims (api.py:365-387): label, plus tone/facet computed by synthesis.semantics.claim_tone/claim_facet
                                     (keyword cue matching on the Vietnamese label) → UI routing and care classification
```

Per-finding data (production): `Finding` (engine.py:35-45) plus `why` = backward chain labels, `kinds`, `opposed_by`, `chain_vi` (api.py:225-230), plus `corroborated_by[{rule_id, sources, basis}]`.
- No topic, polarity, conditions, school or open-questions field.
- Tone is a separate, text-derived lookup.

How conflicts are handled:
- `conflict.resolve` compares support against limit only inside the same `(subject, claim)`.
- The packs have 1401 distinct claims for 1437 rules. Only 3 claims receive both effects, and 0 rules declare `conflictsWith`. In practice the resolver never fires.
  - Reference chart: statuses are `supported` 59 and `limited` 12; there is no `unresolved`.
  - The `conflicts` field carries derived-fact clashes only (`res.conflicts`, api.py:252). The claim-level report goes only into the unused `text`.
- Vận contradictions are detected by substring: `"đi lên" in joined and "đi xuống" in joined` (van_han.py:114-115).

How text is produced:
- The UI builds prose from `claims_vi.json` labels: "Khuynh hướng …" and "Căn cứ trên lá số: <parenthesised trigger>".
- analysis.py uses f-string templates.
- nlg templates exist but are discarded.

### 1b. Python synthesis (`engine/tvbt/synthesis/`; TVBT_DEEP_INTERPRETATION, off)

```
/api/synthesis (api.py:121-138) → chapters.build_synthesis (chapters.py:463-479)
   facts.tuvi_facts → engine.run AGAIN (chapters.py:57-60) → semantics.annotate (SemanticEvidence: concept, facet, polarity,
   modality, root, chart_trigger, cites, schools, applicability) → reasoner.group (Proposition per concept@palace,
   Roots dedup, shared star = weight 0.5) → reasoner.relate (relations.json + book "nhưng" pairs; classify_contradiction:
   refinement | both_hold | school_divergence | unresolved) → themes → grammar (discourse templates, stable_hash variants)
   → validate → per-chapter paragraphs with sentence provenance
/api/deep-reading (api.py:67-83) → compose.build_deep_reading: a SECOND synthesis stack (evidence/conflicts/taxonomy/structures)
```

- Consumer: report.js:18-34 `synthHtml`, called by app.js:139 (optional; a 404 is swallowed).
- /api/deep-reading has no consumer.

### 1c. TypeScript (`src/interpret/`, interpret-2.1.0; TVBT_INTERPRET, off)

```
Worker /api/interpret (src/index.ts:23-43) → container /api/facts (Python facts, decades with đại hạn Tứ Hóa, year, bazi)
  → pipeline.prepare: engine.ts (port of engine.py, no formations) → semantic.ts (port of semantics.py) → graph.ts
    (palace/star/hóa/finding nodes, tam_hợp/xung/giáp edges, counterfactual depends_on)
  → planner.ts (Claim{id=role|concept|palace, grounds[root, books, independent], rules}, roles base/support/qualifier/cross/
    environment/timing, dominance qualified_base|both_hold) → generator.ts (editorial modules content/*.json, FNV variant)
  → validate.ts (grounding, banned words, contradictions, filler, budget) → cache (R2 → D1 → Cache API)
```

- Knowledge: `generated/knowledge.json` (1.36 MB) is built by `tools/interpret/build.ts`, which regex-parses Python sources (build.ts:15-16, 52-58).
- Consumer: none in the UI.

### 1d. Other deep modules

| Module | Endpoint / flag | Consumer | Notes |
|---|---|---|---|
| bazi_deep (pipeline.py:56-96) | /api/bazi-structure, /api/bazi-timeline; no flag | growth_api, compare_deep (internal); no web/js | interact → strength → geju → yongshen → facts → engine.run(pack_structure) |
| phi_hoa | /api/phi-hoa; no flag | none | PhiGraph → phi.* facts → engine.run (experimental rules) |
| formation_eval + formation_explain | /api/formations | app.js:140 only with `?thu-nghiem` | full state machine: thanh / bi_pha / pha_duoc_cuu… with core / boosters / breakers / rescuers / refutations |
| cach_cuc.py | tv.extras (tuvi.py:322) | report.js:221 | a third, independent cách-cục detector |
| reasoning/layers.py + temporal_facts.py | /api/year `experimental` | none | the only multi-layer vận facts (đại hạn / lưu Tứ Hóa / kỵ layers) |
| growth | /api/growth/* (TVBT_GROWTH) | growth.js | anchors with machine checks |
| van_han_tt.py, cuu_dieu.py | none | tests only | dead in production |

---

## 2. Production reproduction and comparison with the PDF

**Timings and determinism (TestClient, M-series Mac; median of 5 warm runs):**

| Endpoint | First call | Warm | Response size | Deterministic |
|---|---|---|---|---|
| /api/chart | 30 ms | 3 ms | 32 KB | yes |
| /api/reasoning | 85 ms | 77 ms | 145 KB | yes |
| /api/analysis | 8 ms | 2 ms | 34 KB | yes |
| /api/year (2026) | 2 ms | 2 ms | 6 KB | yes |
| /api/facts | 5 ms | 4 ms | 75 KB | yes |
| /api/synthesis (flag on) | 183 ms | 76 ms | 91 KB | yes, except AR-9 |
| /api/deep-reading (flag on) | 89 ms | 61 ms | 102 KB | yes; HTTP 500 with experimental=true (AR-10) |
| TS prepare + chapter | 59–100 ms | 40–51 ms (2.7–12.9 ms with prepare cached) | — | yes (14 runs, 2 processes) |
| TS, all 10 chapters for one chart | — | 96 ms | — | yes |

Breakdown of /api/reasoning:
- `engine.run` for tu_vi takes 43 ms: 1332 rules × 12 palaces.
- `load_all` takes 12 ms and is not cached.
- `build_interpretations` takes 4 ms; why-chains take 2 ms.
- The UI also fires /api/synthesis whenever it is enabled, which runs the engine a second time.

**Reference output:**
- Tử Vi: 71 findings (52 verified, 19 draft), 8 pending, 0 blocked, 0 conflicts. Effects: 54 support, 12 limit, 5 neutral. Only 1 finding has `corroborated_by`.
- Bát Tự: 4 findings, all neutral.

**PDF vs current code:**
- The PDF was printed in the old "Dễ hiểu" mode. Before 6c10cf5, print.js forced `depth='easy'`. At HEAD the print shows the pro markup instead. The next PDF will therefore:
  - lose the summaries, the folds and the primers;
  - gain about 52 finding cards with "Vì sao" accordions (about 108 copies of "Không có quy tắc đối lập nào khớp…"), the "Phân tích cấu trúc" blocks and a JSON trace that will likely be clipped.
- Content gaps visible in the PDF for this chart (all reproducible from the JSON):
  1. **Công danh contradiction is left unexplained.** "văn võ đều hay", "quyền quý" and "trong ngoài đều có quyền quý" are printed next to "khó đạt công danh" and "danh vọng đến muộn".
     - The two "quyền quý" cards are mirror rules with the same trigger and the same book: TV_TT_PAL_QUAN_LOC_TU_VI_WITH_THIEN_TUONG_P and TV_TT_PAL_QUAN_LOC_THIEN_TUONG_WITH_TU_VI_P.
     - All three limits rest on the single Địa Kiếp at Thìn: TH_AUX2_QUAN_LOC_KK_HAM, TH_P2_QUAN_LOC_TUONG_KHONG_KIEP and TT_PAL_QUAN_LOC_TU_VI_SAT_M (via `khi.sat_tp ≥ 1`).
  2. **Polarity is mislabelled.** `khong_kiep_quan_ham_kho_dat_cong_danh` has `effect: support`, so it is shown as a main card while the real limit cards are hidden.
     - Across the packs, 88 rules have support effect with negative tone, and 244 support rules have no tone at all.
  3. **Limit findings are invisible in easy mode.** Ten verified limit findings were printed 0 times, e.g. "hôn nhân dễ đổ vỡ", "công danh tầm thường", "gian truân".
  4. **Some palaces are wrongly reported as empty.**
     - "2/12 cung chưa có luận giải": Tật Ách and Tử Tức are vô chính diệu, and the rules key on `own_major_stars`, so there is no borrowing.
     - Huynh Đệ is reported empty even though it has a verified limit finding.
  5. **Tuần/Triệt is printed but never modifies anything.** Triệt on Thiên Di (which holds Địa Không and the "danh đến muộn" trigger); Tuần on Phu Thê, where Thân sits.
  6. **Vận is positional only.**
     - The 2026 tiểu hạn at Quan Lộc gives "hai điều kiện trái chiều… không kết luận".
     - Lưu Tứ Hóa is described without reference to natal findings. Đại hạn Tứ Hóa is not in /api/year.
  7. **Print defects.** The đại vận and đại hạn timelines are cut off ("57 tuổi Đinh Chính T", "56–65 Nô B"), and care cards print after the next chapter's heading.

---

## 3. Requirement coverage matrix

Legend: Y = yes, P = partial, N = no.
- PROD = /api/reasoning + /api/analysis + /api/year + UI.
- SYN = /api/synthesis. DR = /api/deep-reading. TS = src/interpret.
- FORM = formation_eval/explain. BZD = bazi_deep.

| Requirement | PROD | SYN | DR | TS | FORM | BZD |
|---|---|---|---|---|---|---|
| conclusion_id | P (finding id = rule:claim@subject, engine.py:182) | P (Proposition.id concept@palace, reasoner.py:104) | N (tuple keys) | P (Claim.id, planner.ts:21) | Y | P |
| topic | P (client facet routing, report.js:76-82, 184) | Y (facet/domain, semantics.py:55) | P (buggy slug aspect, taxonomy.py:17) | Y (concept/facet) | Y (anchor palace) | P |
| contributing_facts | P (why chain of raw fact labels; `any` alternatives not resolved; engine.py:144-146) | P (chart_trigger; khi counts dropped, semantics.py:283-306) | P/wrong (evidence.py:56-66 drops not/any) | P (Ground.root, chartCondition, semantic.ts:91-137) | Y | Y (FACT_ORIGIN) |
| supporting_rules | P (corroborated_by, same claim only, api.py:208) | Y | Y | Y | Y (boosters) | Y |
| opposing_rules | N in practice (resolve only within same claim, conflict.py:31-56) | P (relations.json pairs; role=limits discarded, reasoner.py:102) | Y (lim + tensions) | P (theme level only) | Y (breakers/refutations) | P |
| applicability_conditions | P (rule conditions only in /api/rules) | P (trigger_text + applicability.json) | N | P (text only) | Y (core) | P |
| invalidating_conditions | P (`exceptions`: 2 rules; `blocked` not shown) | N | N | N (blocked dropped, engine.ts:41) | Y (formation_eval.py:48-70) | P |
| source_references | Y (sourceIds, why chain) | Y (cites per sentence) | Y | Y (books/cites) | Y | P |
| school | N (`schoolId` is `vn_dlhc_draft` for 1331 rules; only the book is meaningful) | P (book-level) | P | N (Rule.school unread) | P | P (profile) |
| evidence_status | Y (basis verified/draft; `disputed` collapses) | Y | Y | Y (binary) | Y | Y |
| unresolved_questions | N (`pending` emptied by UI, app.js:142) | P (closing limit sentence) | Y (chuyen_sau) | N | Y (missing_for_next_level) | N |
| final_interpretation | P (per-finding label; no per-conclusion synthesis) | Y (paragraphs) | Y | Y (paragraphs) | Y (render_vi) | P |
| Evidence independence / shared-trigger dedup | N (73 groups / 159 rules with identical conditions; only same-claim merge) | P (root dedup + 0.5 weight; broken by khi counts and `any`) | P (distinct books) | P (boolean independence, planner.ts:148; cross-claim not deduped) | N | N |
| Conflict resolution over claims / triggers / contexts / periods / school | N (same-claim specificity only; vận by substring) | P (claims, triggers, palace context; no periods; school = book overlap) | P (aspect, anchor, leaves, school) | P (stars, book, specificity, sát vs chính, lexicon; no periods or school) | P (declared breakers) | P (timeline periods) |
| L1 bản cung | Y (91% of rules key on own stars) | Y | Y | Y | Y | n/a |
| L2 tam phương with đồng cung / tam hợp / xung / giáp distinguished | P (typed facts exist in positions.py:10-61, but 76 rules use the merged `tam_phuong_stars`; analysis says "tam phương" only) | P (renders xung as "hội chiếu", semantics.py:289) | P | P (rendering distinguishes; no weighting) | Y (roles in formation conditions) | n/a |
| L3 named configurations with qualifiers / disqualifiers | P (cach_cuc.py names; analysis "≥3 sao" only; FORM gated) | P (6 Mệnh-centric detectors, structures.py) | crash with formations (AR-10) | N | Y (but experimental-only) | P (geju) |
| L4 Mệnh–Thân–Cục | P (facts + analysis prose, analysis.py:164) | P | P | P (slots) | N | n/a |
| L5 vận: đại hạn / tiểu hạn / lưu Thái Tuế / lưu Tứ Hóa | P (đại hạn palace + KL readings; tiểu hạn + van_han.read; lưu TT palace; lưu Tứ Hóa advice; no đại hạn Tứ Hóa in /api/year; no overlay with natal) | P (positional) | P | P (timeline.ts) | N | Y (timeline re-run) |
| L6 synthesis per palace | N | Y (per chapter) | Y | Y | Y (Tổng luận) | P |
| Vô chính diệu borrowing | P (prose only, analysis.py:314-315; rules do not re-evaluate with opposite majors) | N | N | P (Mệnh prose; `f.opp_borrow` dead) | N | n/a |
| Tuần/Triệt modifier | N (only as a condition in ~50 rules; 2 rules have exceptions) | N | N (un-valenced) | N | P (as breaker facts if authored) | n/a |
| Report chapters (Nhận định tổng quan / Cơ sở / Hỗ trợ / Hạn chế & mâu thuẫn / Tổng hợp / Điều kiện & giới hạn) | P (Dữ kiện tính toán / Diễn giải truyền thống / Điểm cần cân nhắc; no synthesis or conditions section) | P (implicit) | Y mostly (conclusion / chain / supports / limits / conditions / verification) | P (FRAME / themes / ENV / TIMING / LIMITS / SYN) | P | N |
| Determinism | Y | P (cache bug AR-9; salience leak AR-14) | Y | Y (localeCompare risk) | Y | Y |
| Cloudflare compatible | Y (Python runs in a CF Container behind the Worker, wrangler.jsonc) | Y (same container) | Y | Y in principle (Worker, crypto.subtle only; ~40 ms CPU per uncached chapter; not tested on workerd) | Y | Y |
| LLM-free | Y | Y | Y | Y | Y | Y |

---

## 4. Issues

| ID | Severity | Issue | Root cause | Evidence | Fix |
|---|---|---|---|---|---|
| AR-1 | High | Conflict resolution is inert in production. Opposite readings of one palace are shown side by side with no verdict, e.g. Quan Lộc "quyền quý" vs "khó đạt công danh / công danh tầm thường / gian truân". | Claims are per-rule slugs (1401 claims for 1437 rules), so `(subject, claim)` groups never contain both effects, and `conflictsWith` is unused (0 rules). | conflict.py:29-31; status counts 59/12/0 unresolved; PDF p.12-13 | Group by palace + topic + polarity over trigger atoms, not by claim (conclusion layer, section 6). |
| AR-2 | High | Polarity is not a field. `effect` means "rule asserts the claim", tone is guessed from label keywords at runtime, and 88 negative claims carry `effect: support`. | Schema has no `polarity`; synthesis.semantics.claim_tone is used by production /api/claims. | api.py:365-387; beginner.js:21-27; KK_HAM shown as a main card | Add a `polarity` (+ / - / mixed) to the claim lexicon at build time, checked by a test; stop deriving tone in the browser. |
| AR-3 | High | Shared triggers count as separate evidence: one Địa Kiếp gives 3 limits, Lộc Tồn + Thiên Mã gives 7 Tài Bạch items, and mirror rules give 2 "quyền quý" cards. | No trigger-level dedup; `_merge_corroborated` only merges identical claims. | 73 identical-condition groups (159 rules); api.py:208-222; fe report §2 | Deduplicate on trigger atoms and count independence in distinct (book, atom-set). |
| AR-4 | High | Limit findings vanished in the printed (easy) report, and at HEAD every finding is printed raw with doubled "hạn chế: hạn chế:". | beginner.js:29-37 drops `effect==='limit'`; ui.js:16 adds a prefix to an already "hạn chế:" phrase; util.js:68 claimLabel ignores effect. | fe report §2 and §5 | Render server-built conclusions with explicit support and opposition sections, not client-classified findings. |
| AR-5 | High | Four pipelines (PROD, SYN, DR, TS) plus FORM interpret the same findings with different taxonomies and reach different conclusions for the same chart. | Each new effort added a layer instead of extending the production chain. | Công danh: PROD lists cards without a verdict; SYN leads with "trở ngại" (limit-led); TS gives `qualified_base` (potential stands, reduced); DR gives support vs limit. Cách cục: cach_cuc.py has 4 names, FORM gives TPVT=thanh, SYN says "không có cấu trúc nào". | Choose one evidence layer in Python, retire DR, and freeze TS until it consumes that layer. |
| AR-6 | Med | Tam phương geometry is re-implemented in 9+ places; cát/sát lists in 8+ copies; the frontend `starKind` uses 33/31-star classes that contradict the server's 6/6. | No shared geometry module is enforced. | facts.py:65, positions.py:23, analysis.py:57/96/314, structures.py:46, van_han_tt.py:24, temporal_facts.py:76, growth/signals.py:65/168, phi_hoa/graph.py:58, graph.ts:31, make_sweep.py:27; util.js:43-45 vs positions.py:18; graph.ts:14 CAT includes Lộc Tồn + Thiên Mã | Make positions.py canonical (`roles_of(palace)`, `CAT_STARS`, `SAT_STARS`) and pass everything through facts. |
| AR-7 | Med | Đại hạn Tứ Hóa landing is computed in 4 places with different lookup scopes, and is absent from /api/year. | Ad hoc copies. | api.py:98-100, chapters.py:410, compose.py:206, temporal_facts.py:26 | Use temporal_facts.layered as the single source and expose it in /api/year. |
| AR-8 | Med | Vô chính diệu borrowing and the Tuần/Triệt modifier are missing from inference. | Rules key on `own_major_stars`; Tuần/Triệt are plain facts. | Tật Ách and Tử Tức empty; Triệt on Thiên Di ignored | Use qualifier tables in the conclusion layer: VCD gives `borrowed_majors` (opp) with lowered confidence; Tuần/Triệt give `modifier` on conclusions whose trigger atoms sit in that palace (sourced per KL/TH, otherwise marked as a system convention). |
| AR-9 | Med | /api/synthesis output depends on call order for dignity_school=toan_thu. | book_pairings cache keyed on rule ids only. | chapters.py:24-32; api.py:131-133 | Include reviewStatus in the key or drop the cache. |
| AR-10 | Med | /api/deep-reading with experimental=true returns HTTP 500. | Formation ids are not in rmap. | evidence.py:83; formation_eval.py:125 | Retire DR (AR-5), or guard the lookup. |
| AR-11 | Med | Rule conditions are rendered wrongly: "cung tại Tỵ, Hợi, Dần, Thân" for `not_in`, and every `any` alternative is listed as present. | Leaf flattening ignores operators. | evidence.py:56-66; conflicts.py:36-48; semantics.root_of :221-235 | One `trigger_atoms(expr, facts)` that returns only true leaves with their operator; reuse it everywhere. |
| AR-12 | Med | The production endpoint imports a flagged-off module. | /api/claims → synthesis.semantics. | api.py:374-387; synthesis/__init__.py:3 | Move tone/facet into the claim lexicon build step (see AR-2). |
| AR-13 | Low | `load_all()`, `tu_hoa_vi.json` and claims are re-read on every request (~12 ms of 77 ms); `lx.CLAIMS` global is mutated per request. | No cache. | api.py:236-237; temporal.py:93-95; bazi_deep/pipeline.py:35 | `lru_cache` the loaders; pass the lexicon explicitly. |
| AR-14 | Low | Synthesis salience leaks across chapters. | Proposition.salience is mutated per chapter. | reasoner.py:273; crosspalace.py:43 | Copy per chapter. |
| AR-15 | Low | TS knowledge drift is not enforced. build.ts regex-parses Python; fixtures freeze `python_fired`. | No CI parity on a fresh rebuild. | build.ts:15-16, 52-58 | Add a test that rebuilds and diffs, or freeze TS. |
| AR-16 | Low | Dead code: van_han_tt.py, cuu_dieu.py, /api/deep-reading stack, easy-mode UI (easyReadings, PRIMER, CARE_INTRO, classify().draft), `f.opp_borrow`, TS `blocked`/`conflicts`, nlg `text` output. | Superseded layers were kept. | agent reports | Delete after the conclusion layer lands. |
| AR-17 | Low | Repeated disclaimers and boilerplate in the PDF: | Copied caveats in report.js, beginner.js, ui.js, tuvi.js and bazi.js. | report.js:109-110, 135, 211; beginner.js:41, 44, 72, 95, 117; ui.js:77, 83 | One report-level "Điều kiện và giới hạn" section; per-conclusion conditions instead of generic caveats. |
| | | • "Đây là cách đọc theo hệ biểu tượng…" ×9 | | | |
| | | • "không phải" ×25 | | | |
| | | • "THEO SÁCH ĐÃ ĐỐI CHIẾU" ×49 | | | |
| | | • "Căn cứ trên lá số:" ×47 | | | |
| | | • the year card ×4 | | | |
| | | • Tứ Hóa ×4 | | | |
| | | • each positive finding 2–3× | | | |
| | | • "Mở chế độ Chuyên sâu" still refers to a removed toggle | | | |
| AR-18 | Low | UI says "Bị giới hạn bởi quy tắc đối lập" for `limited` findings whose `opposed_by` is empty. | `status` limited just means effect=limit. | ui.js:29; conflict.py:58-61 | Status comes from the conclusion layer. |
| AR-19 | Low | Bát Tự block "Tàng can của nguyệt lệnh" is misrouted to Tử Vi Cách cục; 14 `muoi-hai-cung` analysis blocks (including VCD borrowing prose) are never rendered. | blockSys regex on text; no `system` field. | report.js:69, 104 | Add `system` to analysis Block. |
| AR-20 | Low | van_han_tt.py:88 fires "Hạn Phá Quân gặp sát tinh" with no sát present. Synthesis calls Thiên Di "tam phương… hội chiếu". | Logic slips. | van_han_tt.py:88; crosspalace.py:31 | Fix when consolidating. |

---

## 5. Duplicated logic summary

- **Inference:** engine.py is ported to engine.ts and dsl.py to dsl.ts. Parity holds today: the same 72 findings fire on the reference chart.
- **Semantics:** semantics.py is ported to semantic.ts and has already drifted (NORM `rel.*` keys, EDITORIAL entries, independence weighting).
- **Two Python synthesis stacks:** compose/evidence/conflicts/taxonomy and semantics/reasoner/grammar/chapters. Each has its own SCHOOL map, cite regex and conflict classifier.
- **Three cách-cục systems:** cach_cuc.py, formation_eval (data/experimental/formations_experimental.json) and synthesis/structures.py. They give different answers.
- **Tiểu hạn:** temporal.py:87 and temporal_facts.py:19.
- **Vận readings:** van_han.py (data rules), van_han_tt.py (code), analysis.dai_van_reading.

---

## 6. Recommendation: one evidence-graph layer inside the production Python chain

**Placement.** Put the layer in `engine/tvbt/reasoning/` as a pure post-processor of `engine.run`.
- This is where the untracked `conclusions.py` already sits.
- It runs in the existing CF Container, so it needs no new runtime, no LLM, and stays deterministic.

### 6.1 Modules

1. `reasoning/positions.py` becomes the canonical geometry module.
   - Add `roles_of(branch) -> dict[role, branch]`, `ROLE_KIND = {self: 'dong_cung', trine1/2: 'tam_hop', opp: 'xung_chieu', flank_*: 'giap', nhi_hop: 'nhi_hop'}`, `CAT_STARS` and `SAT_STARS`.
   - analysis.View.tam, structures.Geo, temporal_facts, growth/signals, van_han_tt and graph.ts should read `palace.rel_names` from facts rather than recomputing.
2. `reasoning/atoms.py`: `trigger_atoms(expr, facts, world, here) -> list[Atom(fact, op, value, palace, role, star)]`.
   - Only true leaves; operator kept; `any` reduced to its satisfied branch; `khi.*` counts expanded to the stars counted.
   - Replaces evidence._leaves, semantics.root_of and semantic.ts root. Fixes AR-11 and AR-3.
3. `reasoning/conclusions.py` (finish the untracked file): `build(res, rules, claims, base, qualifiers, temporal=None) -> list[Conclusion]`, where `Conclusion` holds:
   - `conclusion_id = f"{palace}:{topic}:{polarity}"`, `topic`, `palace`, `layer` (ban_cung | tam_phuong | cach_cuc | menh_than_cuc | van | synthesis);
   - `contributing_facts: list[Atom]`, `supporting_rules` / `opposing_rules: list[RuleRef{rule_id, book, page, school, basis}]`;
   - `independent_books: int` (distinct book × distinct atom set);
   - `applicability_conditions` (rule conditions, rendered from atoms), `invalidating_conditions` (exceptions + qualifier hits + Tuần/Triệt + breakers);
   - `source_references`, `school`, `evidence_status` (verified | draft | system_convention);
   - `conflict: {kind: same_trigger | nested | coexisting | period | school, resolution, note}`;
   - `unresolved_questions: list[str]`, `final_interpretation: str` (template, deterministic).
   - Reuse, not rewrite:
     - `conflict._specificity` for nested triggers;
     - `reasoner.classify_contradiction` logic for refinement, both_hold and school_divergence (move it here and delete it from synthesis);
     - `formation_eval.evaluate_formation` for L3 (promote the verified subset of formations out of experimental; they already have core / boosters / breakers / rescuers);
     - `temporal_facts.layered` / `time_facts` for L5 (đại hạn Tứ Hóa, lưu Tứ Hóa, kỵ / lộc layers), joined to natal conclusions by palace and topic.
4. `data/qualifiers.json`, read by `conclusions.evaluate_qualifiers`. Holds:
   - VCD borrowing: `borrow_from: opp`, confidence downgrade, KL pp.220-222;
   - Tuần/Triệt modifier: scope = conclusions whose atoms sit in the palace, effect = `dampen` / `reverse_for_ham`, sourced TH p.30-31 / KL p.233, otherwise `system_convention`;
   - all of it data-driven and reviewable.
5. `data/claims_vi.json` gains build-time fields `polarity`, `topic` and `facet`, validated in `knowledge/schema.validate_pack`.
   - `/api/claims` serves them, and synthesis.semantics leaves the production import path (AR-2, AR-12).

### 6.2 API

The change is additive, so the UI does not break.
- `/api/reasoning` adds `systems.tu_vi.conclusions` (and `bat_tu`) next to the untouched `findings`.
- Each `Conclusion` lists `finding_ids`, so the existing "Vì sao" chains keep working.
- `/api/year` adds `dai_han_tu_hoa` and `overlays` from temporal_facts.
- Cache `load_all` / claims / qualifiers with `lru_cache` (AR-13).

### 6.3 Report rendering

Move the frontend to conclusions, one chapter at a time:

| Report section | Source |
|---|---|
| Nhận định tổng quan | top conclusions by layer L1–L4 |
| Cơ sở luận giải | contributing_facts + typed tam phương |
| Yếu tố hỗ trợ | supporting rules, grouped by independent book |
| Điểm hạn chế và mâu thuẫn | opposing rules + conflict.kind, replacing the "Điểm cần cân nhắc" fold and beginner.js `isCare` |
| Luận giải tổng hợp | final_interpretation per chapter |
| Điều kiện và giới hạn | one section collecting applicability and invalidating conditions and unresolved_questions; replaces the 9+ per-block disclaimers |

### 6.4 Avoiding a fourth pipeline

- **SYN:** keep only grammar.py as the realiser for `final_interpretation`. Delete compose/evidence/conflicts/taxonomy (the DR stack) and reasoner/semantics once conclusions cover them.
- **TS:** freeze `src/interpret` (flag stays off). If the Worker path is revived, it should consume `conclusions` from `/api/facts` rather than re-run inference, which removes the semantic.ts drift.
- **Retire** cach_cuc.py name detection in favour of formation_eval verdicts, and delete van_han_tt.py and cuu_dieu.py.

### 6.5 Guards

- A determinism test over a 70-chart sweep (tools/interpret/make_sweep.py), checked by output hash.
- A test that every Conclusion with both supporting and opposing rules carries a `conflict.kind`.
- A test that no conclusion counts two rules with the same atom set as independent.
- Performance budget: the conclusion layer should add 10 ms or less over the 43 ms `engine.run`. A rough estimate for pure-Python grouping over about 70 findings is 2–5 ms.
