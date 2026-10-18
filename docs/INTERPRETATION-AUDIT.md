# Audit of the deterministic interpretation engine (interpret-1.0.0 → 1.1.0)

**Date:** 2026-10-18.

**Scope:** the TypeScript pipeline in `src/interpret/`, the Công danh example for 17/05/1990, the rule packs it depends on, and a 48-chart
sweep. It also covers the extension to the Mệnh and Tài Bạch chapters.

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

## 3. Cross-palace synthesis, Tam Phương Tứ Chính, Tứ Hóa, Tuần/Triệt, vận hạn

- **Tam phương tứ chính:** the frame is computed from branch geometry (+4, +8, +6). It was checked on 17/05/1990: Quan Lộc Thìn → Mệnh Tý,
  Tài Bạch Thân, Phu Thê Tuất.
- **Cross-palace dependencies are now counterfactual.** For each true leaf naming a star in another palace, the rule is re-evaluated with
  that star removed from the relation facts of the palaces that chiếu in.
  - Necessary → "chỉ thỏa vì …".
  - Not necessary → "cũng thỏa điều kiện ấy, nhưng câu này không phụ thuộc vào đó".
  - Not re-evaluable (derived facts) → no necessity is claimed.
  - Unit test: `reasoning.test.ts`.
- **Tứ Hóa:**
  - Natal Hóa are shown on the star in every frame palace.
  - Decade Hóa landing in the focus palace are listed for usable decades only.
  - Lưu Hóa of the current year that land in the focus palace, and lưu Hóa Kỵ anywhere in the frame, come with the Khảo Luận pp.195–197
    reading of that star's Hóa.
  - No rule interprets Hóa interactions further, and the text says so.
- **Tuần/Triệt:**
  - In the focus, opposite and environment palaces, when no reading **used by the chapter** tests them, the text records them without
    interpreting.
  - A star counted from a palace under Tuần/Triệt is marked where the condition names it.
  - The traditional view that Tuần/Triệt soften both good and bad stars is **not** encoded as a rule, and is therefore not applied.
- **Vận hạn:**
  - The decade through the focus palace and the Khảo Luận vận readings are shown. When two readings disagree, there is no conclusion.
  - The year's tiểu hạn is named when it falls in the focus palace. Its vận readings are not repeated when they equal the decade's.
- **Vô chính diệu:**
  - The text states the usual "mượn sao cung xung chiếu" practice and says the rule set does **not** encode it.
  - The opposite palace's readings are therefore not transferred.
- **Not validated:**
  - Whether Tử Vi at Thìn is "vượng" or "đắc" depends on the dignity school the engine was configured with.
  - Vũ Khúc at Tý shows no brightness (the school's table has no entry).
  - Both need a practitioner's decision, not a code change.

## 4. Sweep over 48 charts (8 regression + 40 coverage charts)

The 40 coverage charts are chosen by greedy cover from 1,500 seeded births (`tools/interpret/make_sweep.py`). They include:

- Quan Lộc and Mệnh vô chính diệu;
- Tuần or Triệt in Quan Lộc;
- each Tứ Hóa in Quan Lộc;
- Thân cư Quan Lộc;
- 0 and 4+ sát in the tam phương;
- Lộc Mã in the frame;
- the current decade being the Quan Lộc decade;
- children and people over 66;
- each of the 14 chính tinh in Quan Lộc.

Run it with `node tools/interpret/sweep.ts <chapter>`.

| Công danh | v1.0 | 1.1 |
|---|---|---|
| Errors | 0 (with the v1.0 validator) | 0 (with a **stricter** validator, §6) |
| Warnings | 13, on 10 charts | 1, on 1 chart (`weak_personalization`) |
| Words, min / median / max | 552 / 829 / 1,582 | 342 / 669 / 1,359 |
| Share of sentences whose template recurs in >50% of charts (median / max) | 0.11 / 0.16 | 0.04 / 0.11 |
| Sentence templates in ≥25% of charts | 19 | 12 (mostly fact sentences: the tam phương frame, the decade) |
| CPU per chapter, median / max (Node 24, Apple Silicon) | 46 / 181 ms | 39 / 74 ms |

| 1.1, all chapters | Errors | Warnings | Words, median (max) | Recurring share, median |
|---|---|---|---|---|
| Công danh | 0 | 1 | 669 (1,359) | 0.04 |
| Tài bạch | 0 | 0 | 676 (1,095) | 0.04 |
| Mệnh | 0 | 1 | 692 (1,273) | 0.05 |

Shorter chapters are intended. Filler was removed and nothing is padded. The thinnest charts end with "chương dừng ở các điều kiện đã nêu".

The sweep found defects that a single chart did not show. All are fixed:

- Positive readings on a bright sát star ("hợp đường chiến công, binh nghiệp", Linh Tinh at Sửu) were treated as limitations.
- Dominance pairs were built between readings with no shared star or comparable facet.
- A Mệnh reading was quoted twice (focus and link).
- Technical "độ số" classifications leaked into prose.
- "Đúng chỗ của mình (tuổi dương)" was presented as if it came from a star.
- A harsh reading ("cùng khổ, chỉ tu hành mới yên thân") was promoted to "the specific case that wins". It only added one sát star, which
  sits in a palace under Triệt. Adding only sát stars now means a degree adjustment, never an override.
- Editorial notes inside quotes ("hai sao sau chưa có trong hệ thống").

## 5. Planner, transitions and modules (what changed)

- **One planner for every chapter** (`chapters.ts`): focus palace, chapter facets, environment palace, linked palaces, timing concepts.
  Generic modules (`content/core.json`) use `{f.*}`/`{topic}` slots; only the Tử–Phủ–Vũ–Tướng note is Công-danh-specific. **No rule and
  no template is duplicated per chapter.**
- **Dominance:**
  - Relations are computed from the satisfied conditions:
    - `specific_qualifier`: the limiting condition contains the favourable one and adds a non-sát fact.
    - `sat_qualifier`: it only adds sát stars.
    - `specific_base`
    - `both_hold`
  - The text states once that the precedence is the system's convention, not the books'.
  - "Cùng một mục" is said only when every listed reading shares a page reference.
- **Tensions:** inside one palace only; the narrower side is identified in both directions. Several "both hold" pairs share one sentence
  and one verdict.
- **Timing:** early/late with specificity. Year-branch or gender-only readings are generic. A lean is stated only on chart-specific
  grounds.
- **Lists:**
  - Grouped by ground.
  - Conditions that only restate the palace's own chính tinh are dropped.
  - Equal conditions are merged, with one star order (chính tinh first).
  - Citations are merged.
  - At most two condition groups per item outside the focus palace.
- **Synthesis:** concepts rather than re-quoted sentences; the operative verdict; cross-palace contributions per palace (favourable /
  limiting); the timing lean only with planner support.
- **Provenance:** each sentence keeps only the rules of the slot values it contains (sentence-level, no longer passage-level).
- **Removed filler:** the reflection line, the "decade arrives late" juxtaposition, "Các nhận định bên dưới…", "Còn một chỗ trái chiều
  nữa.", and decades past age 85.

## 6. Validator changes (stricter in three places, aligned in two)

**Stricter: new errors.**

- `editorial_leak`: the system's voice inside a quote.
- `unsupported_conclusion` for "nghiêng về" without a planner lean.
- `unsupported_conclusion` for "chỉ thỏa / chỉ đứng được" without counterfactual necessity.

**Aligned with the planner.**

- `contradiction_not_explained`: now uses the same notion of opposition as the planner (same palace; `contradicts` relation or same
  facet). It accepts a pair the planner weighed even when the list shows only two of its favourable readings. Timing and generic readings
  are excluded; they have their own logic.
- `weak_personalization`: also counts a sentence that quotes or argues a reading fired by a **star** condition of this chart. Year- or
  gender-only rules do not count.

These two alignments loosen the v1.0 checks. They are disclosed here so that the drop in warnings is not read as better prose alone.

**Unchanged.** An inline page reference ("tr.78") counts as a source for a book sentence that carries no rule (star profiles, the group
note).

## 7. Storage, determinism, caching, CPU (verified locally; not yet on Cloudflare)

- **Deterministic:** every chart × chapter renders identically on a second run (tested on 8 × 3). There is no randomness; variants are
  chosen by FNV hash of the chart.
- **D1:**
  - The real schema and seed load into `node:sqlite`.
  - The D1 store gives byte-identical text to the bundled store for 3 charts × 3 chapters.
  - Re-applying the seed is idempotent (`module_reviews` is cleared first).
  - `loadKnowledge` keeps the knowledge per isolate, keyed by `kb_meta.version`: one row per request, the full read once (tested). Before,
    every request would have read about 3,000 rows.
  - An unseeded binding falls back to the bundle.
- **R2:**
  - An R2 hit is served first.
  - A put writes the body to R2 and only the pointer (`r2_key`) to D1 (tested with an in-memory R2).
  - The cache key changes with chapter, engine version (`interpret-1.1.0`) and knowledge version (tested).
- **CPU:**
  - Median 39 ms, p95 52 ms, max 82 ms per uncached chapter (144 renders).
  - 7 ms to parse the bundled knowledge (1.2 MB, 155 KB gzip).
  - Worker bundle 1.67 MB (`wrangler deploy --dry-run`).
  - This needs the Workers Paid CPU limit, which the container deployment already requires; it is above the free plan's 10 ms.
  - At Workers' CPU pricing, an uncached chapter costs about $0.000001. A cached one costs one R2/D1 read.
- **Not verified:**
  - A real D1/R2 deployment (no bindings exist).
  - CPU on the Workers runtime; the figures are from Node.
  - The Cache API on `workers.dev` (it only works on a custom domain).
  - The end-to-end route with the container.

## 8. Mệnh and Tài Bạch

The extension was made after Công danh met its **automated** gate:

- 0 errors and ≤ 3 warnings across 48 charts;
- no chapter over 1,500 words;
- recurring-template share median ≤ 0.08;
- no content template in more than half the charts;
- deterministic.

Both new chapters pass the same gate (§4). They reuse the planner and modules with chapter-specific facets:

- Mệnh leaves career and wealth readings to their chapters (counted, not repeated) and skips its own childhood decade.
- Tài Bạch reads Điền Trạch as accumulated wealth.

The expert gate has not been passed for any chapter.

## 9. Tests added

- `src/interpret/test/pipeline.test.ts`:
  - 1990 assertions for each defect in §1;
  - Mệnh and Tài Bạch on 1990;
  - grounding and determinism over 8 charts × 3 chapters;
  - sentence-level provenance;
  - D1 parity for every chapter and idempotent seed;
  - R2 cache layering;
  - cache keys;
  - the isolate memo.
- `src/interpret/test/reasoning.test.ts`: counterfactual necessity; condition rendering; editorial stripping; citation merging; timing lean
  over the corpus; dominance relations.
- `src/interpret/test/sweep.test.ts`: corpus diversity, plus the per-chapter gate over all 48 charts.
- `engine/tests/test_rule_integrity.py`: unordered giáp pairs; verified rules whose reading names a brightness they do not test.

## 10. For the expert reviewer (not done)

The remaining questions need a practitioner, not more code:

1. **Precedence convention.** Is "the narrower condition is read first; adding only sát stars is a degree adjustment" acceptable? Where
   should it not apply (e.g. Nhật Nguyệt Sửu Mùi with Triệt or Hóa Kỵ, which many readers treat as favourable)?
2. **"Gặp" in rule conditions.** Is it tam phương or same palace? (E.g. "Thiên Phủ kỵ nhất gặp Tuần, Triệt hoặc Thiên, Địa Không" fires
   with Địa Không in the xung chiếu palace.)
3. **Tuần/Triệt and vô chính diệu.** Should Tuần/Triệt be encoded as a general rule, and "mượn sao cung xung chiếu" as a reading rule,
   with page references?
4. **Dignity schools.** Tử Vi at Thìn; Vũ Khúc's missing entry; "miếu địa" read as miếu/vượng/đắc in the `mieu` variant.
5. **Content modules.** Approve, request changes or retire each module with `npm run editorial -- submit|approve|request-changes`. The
   author cannot approve their own module.

Until then, no output should be described as expert quality.
