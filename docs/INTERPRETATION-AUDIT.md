# Audit of the deterministic interpretation engine (interpret-1.0.0 audit, applied to interpret-2.0.0)

**Date:** 2026-10-18.

**Scope:** the TypeScript pipeline in `src/interpret/`, the Công danh example for 17/05/1990, the rule packs it depends on, and a 70-chart
sweep over all 10 chapters. The audit was done on the 3-chapter v1.0 text (§1) and then **applied to the 10-chapter v2 engine on `main`**;
the v2 results are in §3–§6. v2's own planner, themes and shared chapter state are unchanged except for the fixes listed in §3.

**Who did what.** Everything below was done by the assistant: reading rule conditions against the book paraphrases in the rule packs,
re-running the pipeline, and writing code and tests. **No practitioner has reviewed this work.** Two kinds of claims are kept apart
throughout:

- **Automated validation:** checks a program runs (validator, regression tests, sweep). They bound defects a reader would notice. They do
  not certify that an interpretation is good.
- **Expert review:** a human practitioner reading the chapters against the books. It **has not happened**. All 10 content modules are
  `draft`, and every output says so (`quality.editorial.allApproved = false`).

Production is unchanged. `/api/interpret` still answers 404 unless `TVBT_INTERPRET=1`, and `wrangler.jsonc` has no D1/R2 bindings.

---

## 1. Sentence-by-sentence review of the v1.0 Công danh example (1,474 words)

The v1.0 text is kept in [examples/cong-danh-17-05-1990-v1.0.md](examples/cong-danh-17-05-1990-v1.0.md). The current text is in
[examples/cong-danh-17-05-1990.md](examples/cong-danh-17-05-1990.md). Verdicts:

- **OK:** accurate against the rule and the chart.
- **Defect:** wrong, overstated or misleading.
- **Weak:** accurate but unnatural, redundant or filler.

| # | v1.0 sentence (abridged) | Verdict | Finding | Fixed in 1.1 |
|---|---|---|---|---|
| 1 | Quan Lộc an tại Canh Thìn: Tử Vi (vượng), Thiên Tướng (vượng), đi cùng Địa Kiếp | OK | Dignities and the sát star match the chart. | Unchanged facts; joined with the opening sentence. |
| 2 | Tam phương: Mệnh (Vũ Khúc và Thiên Phủ (vượng)) … | **Defect** | Omits Tứ Hóa: Vũ Khúc carries **Hóa Quyền** in Mệnh, the only natal Hóa in the career frame. Tuần/Triệt shown only for the xung chiếu palace. | Star labels carry their Hóa ("Vũ Khúc hóa Quyền"), and every frame palace shows Tuần/Triệt. |
| 3 | Phu Thê cũng là cung Thân cư | OK | | |
| 4 | Profiles "(Thực Hành tr.29–30, Thực Hành tr.44)" | Weak | Same book cited twice. | `mergeCites` gives "Thực Hành tr.29–30, 44". |
| 5 | "quyền quý" và "trong ngoài đều có quyền quý" (Toàn Thư tr.78–80); "văn võ đều hay…" (Toàn Thư tr.78–80) | Weak | Citation repeated inside one sentence. | A citation shared by consecutive items is written once. |
| 6 | the two "quyền quý" sentences are one ground | OK | Correct independence reasoning (same rule condition seen from two stars). | Kept. |
| 7 | "khó đạt công danh" khi Địa Kiếp tại Quan Lộc, **Quan Lộc an tại Thìn** | **Defect** | The rule tests "Kiếp/Không **hãm**" (branch ∉ Dần Thân Tỵ Hợi). Rendering it as "an tại Thìn" names the wrong condition. | Brightness branch lists render as "có Địa Kiếp hãm địa ở Thìn". |
| 8 | "công danh tầm thường" khi … Linh Tinh (từ Phu Thê) hội về | Weak | Linh Tinh is counted from a palace under **Tuần**, and the text does not say so. | "Linh Tinh (từ Phu Thê, nơi có Tuần)". |
| 9 | "gian truân" **khi Thiên Tướng và Địa Kiếp** | **Defect** | Condition is incomplete: the palace was removed by the "name the palace once" rule. | Conditions render relative to the paragraph's palace: "khi có Thiên Tướng và Địa Kiếp trong cung". |
| 10 | the limiting readings share Địa Kiếp, so they are one factor | OK | Good reasoning. | Kept. |
| 11 | Other palaces: "học nhiều nhưng khó đạt thành tựu tương xứng"; **"tự tin ('ta đây'), dễ bị ganh ghét"** | **Defect** | The second is a Mệnh personality reading. It was routed into career limits because "ganh ghét" matched a `career.support` concept. | Readings outside the focus palace need a chapter facet; `career.support` is accepted only from the focus and environment palaces. |
| 12–13 | Dominance: "năm tiêu chí", followed by a semicolon list of five criteria | Weak | Mechanical: the criteria are enumerated rather than argued. | One policy statement, then each pair argued by its operative criterion. The full criteria stay in `argument.dominance[].criteria`. |
| 14–16 | Verdict on "quyền quý" vs "công danh tầm thường"; "Toàn Thư tự đặt hai câu…" | OK in substance, weak in form | Three sentences said the same thing twice. | Two sentences. The relation is computed as `sat_qualifier`: the limiting sentence only adds sát stars to Tử Vi. |
| 17–18 | "văn võ đều hay" vs "gian truân" | OK | | Kept, shorter. |
| 19 | "hay gặp người sang giúp" vs "dễ bị ganh ghét" (Thiên Di vs Mệnh) | **Defect** | Not a contradiction: being helped and being envied are compatible, in different palaces. It existed only because of #11. | Tensions only inside one palace, with a `contradicts` relation or the same facet. |
| 20 | "Ngoài cung Thìn, chương còn phải đọc…" | Weak | Filler lead. | Lead kept only when a real cross-palace item follows. |
| 21 | **"tạo được uy quyền hiển hách … chỉ đứng được vì Tử Vi nằm ở cung Quan Lộc"** | **Defect (factual)** | The rule is "Hóa Quyền gặp Tử **hoặc** Phủ". Thiên Phủ sits in Mệnh itself, so the reading holds **without** Tử Vi in Quan Lộc. The claim of necessity was false. | Necessity is now tested **counterfactually**: the condition is re-evaluated with the star removed from the chiếu palaces. The text now says Tử Vi "cũng thỏa điều kiện ấy, nhưng câu này không phụ thuộc vào đó". |
| 22 | "lập nghiệp nơi xa … cần Lộc Tồn và Thiên Mã ở Tài Bạch" | OK | Both stars are necessary (verified counterfactually). | Kept, and still in Công danh (`life.mobility` added to the chapter facets). |
| 23 | Tử – Phủ – Vũ – Tướng group (Khảo Luận tr.166–167) | OK | | |
| 24 | Thiên Di: Thất Sát, Thiên Khôi, Địa Không | Weak | Thiên Di has **Triệt**; the text is silent. | No verified rule tests Triệt there, so the text records it and says it is not interpreted. |
| 25 | Timing: "công danh sớm…" khi **Đào Hồng đối mặt theo tuổi Ngọ** | Weak | That rule holds for every person born in a Ngọ year (no star of this chart is involved), and the text did not say so. | The condition reads "thế chung của mọi lá số tuổi Ngọ". The evidence carries `specificity = 0` / `generic`. |
| 26–27 | The two timing readings conflict; both are kept | OK | | Rewritten: quotes, conditions and pages appear once. |
| 28 | Decade 46–55, age 37 now | OK | Arithmetic verified (Hỏa lục cục, dương nam thuận). | |
| 29 | Vận readings: "…: **theo sách** đây lại là dịp đi lên" | **Defect** | The system's own voice inside a quoted reading. | Removed from quotes. The validator now fails on `editorial_leak`. |
| 30 | The vận readings conflict, so no conclusion | OK | | |
| 31 | "chặng đại hạn đến tương đối muộn cùng chiều…" | Weak | Juxtaposition with no rule (filler, in 17 of 48 charts). | Removed. |
| 32 | Decade Tứ Hóa: 66–75 Hóa Quyền, **96–105** Hóa Khoa | **Defect** | Lists decades no reader can use. Misses the year: **the 2026 tiểu hạn falls in Quan Lộc**, and lưu Hóa Kỵ (Liêm Trinh) falls in Tài Bạch, inside the frame. The existing PDF mentions the tiểu hạn. | Only the current, next and focus decades, grouped per decade. A year paragraph covers the tiểu hạn and lưu Hóa in the frame (Khảo Luận pp.195–197). |
| 33 | Scope notes: same star pair, Mệnh readings not transferred | OK | | |
| 34 | One draft excluded ("danh vọng, địa vị cao") | OK | | Harsh drafts are now counted, never quoted. |
| 35 | Synthesis: "triển vọng địa vị và sự đa năng" + re-quoted readings | Weak | Re-quotes sentences already quoted twice. Does not state the dominance verdict. | Concepts instead of quotes. The verdict is stated: "Địa Kiếp … hạ mức độ của tiềm năng ấy chứ không xóa nó". |
| 36 | **"sách nghiêng về thành tựu đến muộn"** | **Defect (unsupported)** | One early and one late reading: nothing licensed "nghiêng". | A lean exists only when the planner computes one: one side alone with chart-specific grounds, or one side generic while the other stands on stars. Here the lean is late **by the stated specificity convention**, and the text says so. The validator fails on any "nghiêng về" without planner support. |
| 37 | "Khi con đường không thẳng, …" | Weak | Generic reflection, identical on 12 of 48 charts. | Removed. |

**Summary:** 37 sentences.

- 9 **defects**: 2 factual (#21 false necessity, #36 unsupported lean), 1 wrong condition (#7), 1 incomplete condition (#9), 1 misrouted
  reading (#11), 1 false tension (#19), 1 leak (#29), 2 omissions (#2 Tứ Hóa, #32 year).
- 11 weak.
- 17 OK.

## 2. Rule activation, checked against the rule sources

The audit found rules that fire on charts their own reading excludes. These are fixed in the **builders**, so a regeneration cannot bring
them back, and guarded by `engine/tests/test_rule_integrity.py`.

| Defect | Example | Fix |
|---|---|---|
| A brightness condition written in the reading but not tested | "**miếu địa:** văn võ đều tài…" (Tả Phụ, Quan Lộc) fired with Tả Phụ of unknown brightness; "rất xấu **khi Thái Âm hãm**" fired whatever Thái Âm's brightness | `tools/data/toan_thu_palace_star.txt` encodes Văn Khúc, Tả Phụ (Quan Lộc) and Liêm Trinh (Phúc Đức) as the `mieu` variant. The builder drafts phrases with untested clauses ("được cát tinh trợ … thì", "gặp sát tinh thì", "nhập miếu" outside `mieu`, "khi X hãm"). |
| An absence clause not tested | "văn võ đều có khả năng, **cần không gặp sát tinh**" (Thiên Đồng, Quan Lộc) fired with Linh Tinh in the palace | The builder adds `palace.khi.sat_tp ≤ 0`. |
| "độc thủ" not tested | "độc thủ: bình thường, toàn chuyện danh hão" (Đà La, Quan Lộc) fired beside chính tinh | The builder adds `palace.has_no_major = true` (11 rules). |
| "Đắc địa" not tested | "Tử Vi hoặc Thiên Phủ **đắc địa** đồng cung Kình Dương" | Dignity leaves added (`build_th_menh_verse_pack.py`). |
| Giáp fix lived only in the generated JSON | Regenerating the Mệnh verse pack silently restored "Nhật Nguyệt giáp" with both stars on one side | `tools/fix_giap.py` (idempotent, run after any pack build). A test fails if an unordered pair reappears. |

Net effect on `pack_toan_thu_palaces.json` (382 rules):

- 3 rules renamed to the `mieu` variant.
- 13 verified rules became drafts, because their phrase carries a condition the rule does not test.
- 11 rules gained the `độc thủ` condition.
- 1 rule gained the "no sát" condition.

Drafts went from 24 to 37.

**These packs also feed the live Python app, so its readings become more conservative when this ships.**

## 3. What was ported into the v2 engine (and what v2 already did better)

v2 already narrates themes (a lead, supports, counters), says brightness once, and covers ten chapters. The audit's findings that still
applied to v2, and their fixes:

| v2 behaviour found in the audit | Fix | Test |
|---|---|---|
| "…đứng được là nhờ Tử Vi nằm ở cung Quan Lộc" for `Hóa Quyền gặp Tử hoặc Phủ`: false, Thiên Phủ in Mệnh already satisfies the condition | **Counterfactual necessity** in `graph.ts`: the rule is re-evaluated without the star in the palaces that chiếu in. Only necessary dependencies are claimed (`deps` in `planner.ts`); Lộc Tồn + Thiên Mã in Tài Bạch for "lập nghiệp nơi xa" stay | `pipeline.test.ts` (1990), `validate.ts` error `unsupported_conclusion` |
| A Mệnh temperament reading ("tự tin, dễ bị ganh ghét") was set against the Thiên Di environment because the cue "ganh ghét" is `career.support` | A reading of another palace whose dominant domain is not the section's, and whose only section cue is `career.support`, is not a section reading; a counter must share a palace with its theme | 1990 test |
| "khó đạt công danh … Quan Lộc ở Thìn" for a rule that tests Địa Kiếp **hãm** | A branch leaf in a brightness rule is rendered "(thế hãm)" / "(thế sáng)" | 1990 test |
| The system's voice inside quotes: "theo sách đây lại là dịp đi lên" | Stripped at the source (`splitReading`, vận readings); the validator fails on `editorial_leak` | validator |
| Generic reflection ("Khi con đường không thẳng…") on every chapter of a facet | Removed (`syn.reflect` stays empty) | 1990 test |
| The same quote narrated in two themes or sections ("số nghèo khổ", "nhân hậu, hay thay đổi…") — two **errors** on the sweep charts | Twin claims are folded in the planner; a later section of a combined chapter drops quotes an earlier one told; further grounds that restate the lead's quote are merged into one clause | sweep test |
| "Tiền bạc dễ kiếm" etc. flagged `contradiction_not_explained` although the theme's counter argues against the lead | The validator accepts a pair when the counter's sentence names the lead of the theme the favourable reading belongs to | sweep test |
| Công danh left out "lập nghiệp nơi xa" (`life.mobility`) | `life.mobility` is a Công danh facet | 1990 test |

Rule data fixed at the source (builders, not generated JSON) and guarded by `engine/tests/test_rule_integrity.py` (§2) is on this branch too.

## 4. Sweep over 70 charts × 10 chapters (700 chapters)

70 charts = the 30 regression charts of v2 plus 40 coverage charts chosen by greedy cover from 1,500 seeded births
(`tools/interpret/make_sweep.py`): Quan Lộc / Mệnh vô chính diệu, Tuần or Triệt in Quan Lộc, each Tứ Hóa in Quan Lộc, Thân cư Quan Lộc,
0 and 4+ sát in the tam phương, Lộc Mã in the frame, the current decade being the Quan Lộc decade, children, people over 66, and each of
the 14 chính tinh in Quan Lộc. Run: `node tools/interpret/evaluate.ts --sweep` (full table in
[examples/interpret-eval-70.md](examples/interpret-eval-70.md)).

| | v2 as on `main` (measured on the same 70 charts) | after the port |
|---|---|---|
| Chapters with an **error** | 2 (`duplicated_meaning`) | 0 |
| Warnings (700 chapters) | 16 | 13 |
| `contradiction_not_explained` | 5 | 1 |
| Công danh words (min / median / max) | 508 / 967 / 1,496 | 509 / 968 / 1,411 |
| Time per chapter, median | 2–12 ms after a shared ~37 ms inference | same |

The warning count falls only a little, and it is not uniformly better: Mệnh goes from 0 to 2 warnings (`excessive_repetition`,
`near_duplicate_sentence`), because it now keeps readings that the old routing dropped, and Công danh from 3 to 4. The two *errors* and
the contradiction warnings are what the port fixes; the repetition warnings are a template problem that remains open.

Remaining warnings (honest list): `excessive_repetition` ×5, `near_duplicate_sentence` ×3, `possible_inflation` ×3 (Điền Trạch / Phu Thê
with a single ground — these chapters are short because the evidence is thin, and the warning says so), `weak_personalization` ×1,
`contradiction_not_explained` ×1.

**Similarity between charts.** Median verbatim overlap of book sentences between two charts is 0%, but the maximum is 33–64% depending on
the chapter. That maximum is between charts that share the same chính tinh in the same palace (the 40 coverage charts include many
Cự Môn / Thiên Đồng pairs), where identical sentences are *correct*: the same rule fires. It is not a template problem, but it does mean two
people with the same Quan Lộc configuration receive overlapping Công danh paragraphs.

## 5. Storage, determinism, caching, CPU (verified locally; not on Cloudflare)

- Every chart × chapter renders identically on a second run (tested on 8 charts and again in the sweep test).
- D1: the real schema and seed load into `node:sqlite`; the D1 store gives the same text as the bundle (v2 test). The audit's isolate
  memo (`loadKnowledge`) is in the 1.1 commit `565c676` on `feat/observatory-result-pages`, **not** ported to this branch; v2's store
  loads D1 per request.
- CPU: shared inference median 36 ms (max 57), chapters 2–12 ms (max 28). Node numbers, not the Workers runtime.
- Not verified: a real D1/R2 deployment, Workers CPU, the Cache API on `workers.dev`, the end-to-end route with the container.

## 6. Coverage and what is still missing

- **Chapters:** ten, as on `main` (Mệnh, Công danh, Tài Bạch, Điền Trạch, Phu Thê, Phúc Đức, Phụ Mẫu/Huynh Đệ/Tử Tức, Thiên Di/Nô Bộc/Tật
  Ách, Đại hạn–tiểu hạn, Bát Tự). All twelve cung are covered; Mệnh–Thân is read inside the Mệnh chapter, not as a separate synthesis.
- **Thin chapters.** Điền Trạch, Phu Thê, Phúc Đức and Phụ Mẫu/Huynh Đệ/Tử Tức have a median of 2–3 independent grounds (≈ 530–580
  words). That is what the **verified rules** support. Making them longer would require new verified rules from the books (the Tử Vi
  books cover them mostly in verse that has not been audited), not better templates.
- **Not encoded as rules, so not interpreted:** Tuần/Triệt as a general modifier of the stars in the palace; borrowing stars from the
  opposite palace for a vô chính diệu palace; Tứ Hóa interactions between palaces (the text records positions only).
- **Bát Tự:** only the verified `bat_tu` rules are narrated. Bát Tự and Tử Vi are never mixed.

## 7. For the expert reviewer (not done)

1. **Precedence convention.** Is "the narrower condition is read first; adding only sát stars is a degree adjustment" acceptable? Where
   should it not apply (e.g. Nhật Nguyệt Sửu Mùi with Triệt or Hóa Kỵ)?
2. **"Gặp" in rule conditions:** tam phương or same palace? (E.g. "Thiên Phủ kỵ nhất gặp Tuần, Triệt hoặc Thiên, Địa Không" fires with Địa
   Không in the xung chiếu palace.)
3. **Tuần/Triệt and vô chính diệu** as general rules, with page references.
4. **Dignity schools.** Tử Vi at Thìn; Vũ Khúc's missing entry; "miếu địa" read as miếu/vượng/đắc.
5. **Content modules.** All are `draft`. Approve, request changes or retire each with `npm run editorial -- submit|approve|request-changes`;
   the author cannot approve their own module.

Until then, no output should be described as expert quality, and `TVBT_INTERPRET` stays unset in production.
