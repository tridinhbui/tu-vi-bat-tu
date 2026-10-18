# Deterministic interpretation pipeline (TypeScript + Cloudflare D1/R2)

The Tử Vi interpretation layer runs in the Worker as plain TypeScript. Nothing calls a language model at runtime: there is no LLM, AI API,
Workers AI or AI Gateway. The Python engine in the container still computes the chart, and serves it to the Worker as facts through
`POST /api/facts`. Everything after that step is deterministic TypeScript in `src/interpret/`.

```
birth record ─► container /api/facts ─► facts (palaces, stars, Tứ Hóa, decades, current year; Bát Tự pillars + bat_tu fact base)
                                            │
  1 Knowledge graph        graph.ts         │ per-chart nodes/edges; rule conditions become depends_on edges between palaces
  2 Rule inference         dsl.ts, engine.ts│ forward chaining over 1,437 book rules; exact parity with the Python engine
     + semantic evidence   semantic.ts      │ book reading → concept, facet, polarity; condition rendered from the chart's true leaves
  3 Narrative planning     planner.ts       │ argument graph per section: roles, grounds, dominance, tensions, THEMES (lead + supports + counters)
  4 Narrative generation   generator.ts     │ shared + per-chapter content modules (JSON) realized with slots, variants, shared chapter state
                           timeline.ts      │   time chapter (decades + year), bazi.ts: Bát Tự chapter
  5 Quality validation     validate.ts      ▼ grounding, unsupported conclusions, repetition, contradictions, inflation, budget
                                       ChapterOutput { paragraphs, text, quality, argument, trace }
```

Entry point: `interpret(chart, chapter, knowledge)` in `src/interpret/pipeline.ts` (engine `interpret-2.0.0`). Chapters
(`src/interpret/chapters.ts`):

| id | title | read from |
|---|---|---|
| `menh` | Mệnh, Thân và tính cách | Mệnh (+ Thân, Phúc Đức) |
| `cong_danh` | Công danh | Quan Lộc in its tam phương; environment from Thiên Di |
| `tai_bach` | Tài Bạch | Tài Bạch (+ Điền Trạch); finance notice |
| `dien_trach` | Điền Trạch | Điền Trạch; finance notice |
| `phu_the` | Phu Thê | Phu Thê (+ Phúc Đức); relationships notice |
| `phuc_duc` | Phúc Đức | Phúc Đức |
| `gia_dao` | Phụ Mẫu, Huynh Đệ và Tử Tức | three sections; relationships notice |
| `di_no_tat` | Thiên Di, Nô Bộc và Tật Ách | three sections; health notice |
| `van_han` | Đại hạn và tiểu hạn | the engine's decades, the year, lưu Tứ Hóa (timeline.ts) |
| `bat_tu` | Bát Tự: tứ trụ và nhật chủ | pillars + verified `bat_tu` rules only (bazi.ts) |

A chapter spec is data: palace(s), the concept facets that make a reading from Mệnh / Thân / another palace belong to it, the
environment palace, linked palaces and the sensitivity notice. Prose comes from the shared modules (`content/_shared.json`, chapter `*`)
plus the chapter's own module file; no chapter copies another's templates.

## How a chapter argues (v2)

1. **Claims.** Every verified reading that fired is one evidence item; the planner gives it a *primary concept*. The concept is taken from
   the domain the reading talks about most (two finance concepts against one of temperament make a finance reading), preferring a facet of
   the section inside that domain. Readings with the same concept, role and palace form one claim; its grounds are deduplicated by root
   star atoms (independence).
2. **Roles.** base (focus palace, on a major star), qualifier (focus palace, limiting or on a sát star), support, cross (Mệnh / Thân /
   chart readings of the section's facets), environment (the environment palace), timing.
3. **Dominance.** A qualifier is weighed against the base reading it can limit (same major star, same facet, or a lexicon relation), with
   the five public criteria. A qualifier unrelated to every base reading is not forced into a pair.
4. **Themes.** Positive themes: a lead and up to three readings of the same facet that go the same way (a reading the lexicon opposes to
   the lead never counts as support; a reading of another palace is narrated with its palace named). Limiting readings are assigned to the
   theme they argue with most directly (dominance pair > same facet > same palace > lexicon relation), globally, best link first; leftovers
   lead negative themes. Themes beyond the budget, and in combined chapters single-sentence themes beyond the first two, become "những
   điểm phụ".
5. **Opposition.** `opposedPair()` (planner.ts) is the one definition of "two readings that pull against each other", shared by the
   planner, the realizer and the validator. The realizer guarantees that every opposed pair is read together: a minor or cross reading that
   opposes a theme is narrated inside it as a counter; two opposed readings in different themes get a back-reference in the later one
   quoting both; two opposed minor points are said to be opposed in the minor-points paragraph.
6. **Shared chapter state.** The sections of a chapter share one `NarrativeState`: a star's brightness, the brightness principle
   (Khảo Luận p.233), a cross-palace dependency and a context clause ("Mệnh ở Tỵ") are explained once; a star group written out once is
   then called by its conventional name ("Lộc Mã", "Cơ Nguyệt Đồng Lương"); variants rotate per passage. A gender condition is never
   shortened and a star list is never split (`shortCond`, unit-tested).
7. **Conditions.** The rendered condition lists every satisfied leaf, including what a rule requires to be absent ("không có Tả Phụ và Hữu
   Bật hội chiếu") and the tam phương / cát-tinh counts, so two readings with opposite meaning never appear to have the same trigger.

### Bát Tự chapter

`/api/facts` also returns `bazi`: the fact base `facts.bazi_facts(bz)` that `/api/analysis` uses for system `bat_tu` (same call, so the same
rules fire; parity is tested on every fixture), plus pillars, ten gods, hidden stems, luck pillars. The chapter narrates the pillars and
luck as computed facts, and only the verified rules that fire: day-master character (八字真宗 PDF pp.25–26) and day-pillar nạp âm (PDF
pp.31–32). It says explicitly that strength (vượng suy), useful god (dụng thần) and structure (cách cục) are not read, and that the manual's
direct judgements (PDF pp.51–58; 49 rules on the `zz` facts) are verified but not wired into the API (`facts.bazi_facts(zz=True)` is still off in
`api.py`; `engine/tests/test_bazi_zz_tables.py` documents the integration point). Bát Tự and Tử Vi are never mixed in one sentence.

## What each stage guarantees

- **Rule inference.** The DSL uses three-valued logic: all / any / not / count / fact / ref. `src/interpret/test/engine.test.ts` checks
  that the same rules fire, with the same claims, as in Python, on 30 fixture charts for `tu_vi` and for `bat_tu`
  (`tools/interpret/make_fixtures.py`: 3 reviewed charts, 5 random dates, 2 edge dates and one chart for each rare configuration found by
  a deterministic scan: Mệnh / Quan Lộc / Tài Bạch / Phu Thê vô chính diệu, Tuần or Triệt on Mệnh, Tuần + Triệt on Quan Lộc, Hóa Kỵ in
  Mệnh / Quan Lộc, Hóa Lộc in Tài Bạch, Thân in Quan Lộc / Mệnh / Thiên Di, Tử Vi in Mệnh, Sát Phá Tham hãm in Mệnh, Thái Dương hãm in
  Mệnh, Không Kiếp in Mệnh, Lộc Tồn in Mệnh, Tật Ách with three sát stars, Cơ Âm in Điền Trạch).
- **Rule activation fixes made before synthesis.** The 17/05/1990 chart showed that the 27 "giáp" (flanking) rules fired when both stars
  sat in one neighbouring palace. Each rule now requires A on one side and B on the other
  (`palace.rel.flank_prev_*` / `flank_next_*`). The Python tests cover this, including negative cases.
- **Evidence.** A rule's reading is split from its condition. Concepts come from the semantic lexicon
  (`engine/data/semantic/concepts.json`), using the longest cue and handling negators. Grounds are deduplicated by root star atoms, so two
  readings written for the same condition count as one independent ground.
- **Planning.**
  - When a favourable reading and a limiting reading coexist, the planner applies five public criteria:
    1. same major star or not;
    2. same book or not;
    3. which condition is more specific;
    4. which side rests on a major star and which on a malefic star;
    5. how many independent grounds each side has.
  - The text says the books do not rank the readings; the criteria are the system's convention.
  - Tensions come only from a `contradicts` relation or the same facet.
  - Timing readings that disagree (early vs late) are both kept.
  - Rules written for Mệnh only are not applied to Quan Lộc; the chapter lists them as scope notes.
- **Generation.** Content modules (`src/interpret/content/*.json`; `_shared.json` applies to every chapter unless a module lists the
  chapter in `exceptChapters`) hold passages. A module may repeat over a list of the argument graph (`each`, e.g. one paragraph per theme)
  or merge its repetitions into one paragraph (`merge`):
  - Each passage has a basis (`sach`, `dieu_kien`, `tinh_toan` or `he_thong`), gate conditions and variants.
  - Templates use slots `{x}`, list slots `{list:name}` and optional segments `{?slot|text}`.
  - A variant is picked by a hash of the chart (FNV), not at random, and repeated openers are avoided.
  - Over 1,500 words, lists are shortened by salience. Reasoning paragraphs are never shortened. Text is never padded.
- **Validation.**
  - Errors: missing_source (a book sentence whose rules did not fire verified), unsupported evaluation, banned wording (fatalistic or
    harmful words, checked outside quotes), duplicated meaning across modules, missing notice in a sensitive chapter.
  - Warnings: contradiction_not_explained, near_duplicate_sentence, excessive_repetition (repeated 4-grams outside quotes and page
    citations), repeated_openers, weak_personalization, generic_filler, possible_inflation (words per evidence unit), over_budget,
    thin_for_evidence.
  - Every output also carries an editorial status. While any module is unapproved, the output includes a notice saying so.

## Knowledge base and storage

- `npm run build:knowledge` (`tools/interpret/build.ts`) compiles the rule packs, sources, claim labels, semantic lexicon, star profiles and
  content modules into:
  - `src/interpret/generated/knowledge.json`: bundled into the Worker. The `version` is a content hash.
  - `migrations/interpret/0002_seed.sql`: the same content, relational. Module layout (`order`, `each`, `merge`, `exceptChapters`) and
    passage layout (`each`, `followups`) are stored in `layout_json` columns, so the D1 store rebuilds exactly the bundled modules (tested
    on every chapter). The reference tables (palace roles, star groups, life stages, Tứ Hóa notes, brightness locators) travel in the
    bundle.
- `migrations/interpret/0001_schema.sql` holds these tables:

  | Table | Holds |
  |---|---|
  | `sources`, `rules`, `claims` | rules, evidence and citations |
  | `concepts`, `concept_relations` | semantic lexicon |
  | `kg_nodes`, `kg_edges` | knowledge graph |
  | `content_modules`, `module_passages`, `module_reviews` | paragraph templates and the editorial workflow |
  | `interpretations` | output cache |
  | `argument_graphs` | argument graphs |
  | `kb_meta` | knowledge-base metadata |

- `src/interpret/store.ts`:
  - `BundledStore` uses the bundled JSON. This is what runs when no binding exists.
  - `D1Store` reads the same knowledge from D1. A test runs the real schema and seed under `node:sqlite` and checks that the text is
    identical to the bundled store's.
  - `LayeredCache` checks R2 (`interpretations/<key>.json`), then the D1 `interpretations` table, then the Workers Cache API.
  - The cache key is SHA-256 of the chart facts (Tử Vi facts, decades, year and the Bát Tự facts), chapter, engine version and knowledge
    version. Changing a rule or a module therefore
    invalidates old outputs automatically.

### Turning it on (not done in this repository)

The route `/api/interpret` answers 404 unless `TVBT_INTERPRET=1`. Production keeps it off. `wrangler.jsonc` has **no** D1/R2 bindings on
purpose; adding them before the resources exist breaks the deploy. To enable:

```bash
npx wrangler d1 create tvbt-interpret
```

```bash
npx wrangler d1 execute tvbt-interpret --remote --file migrations/interpret/0001_schema.sql
```

```bash
npx wrangler d1 execute tvbt-interpret --remote --file migrations/interpret/0002_seed.sql
```

```bash
npx wrangler r2 bucket create tvbt-interpret-cache
```

Then add to `wrangler.jsonc`, using the database id that the first command prints:

```jsonc
"d1_databases": [{ "binding": "INTERPRET_DB", "database_name": "tvbt-interpret", "database_id": "<id>" }],
"r2_buckets":   [{ "binding": "INTERPRET_CACHE", "bucket_name": "tvbt-interpret-cache" }],
"vars":         { "TVBT_INTERPRET": "1" }
```

Both bindings are optional. With neither, the route uses the bundled knowledge and the edge cache.

Request:

```
POST /api/interpret { ...birth record, "chapter": "cong_danh" }
```

The response header `x-interpret-cache` is `hit` or `miss`.

### Cost

Measured on the 30 regression charts (Node 24, development machine; Worker numbers will differ): the shared inference for a chart
(rules + evidence + graph) costs 35 ms median, 55 ms max; each chapter then adds 2–15 ms median (Mệnh is the heaviest, 26 ms max). Inference
is computed once per chart object and shared by the chapters of one request. A cached
request costs one R2 or D1 read. There is no per-token cost. The bundled knowledge adds about 200 KB gzip to the Worker.

## Editorial workflow

Modules move through `draft → in_review → approved` (or `retired`). Each step is recorded in the module's `reviews` and seeded into
`module_reviews`.

```bash
npm run editorial -- lint
```

```bash
npm run editorial -- preview 0 tai_bach
```

```bash
npm run editorial -- submit CD.40.DOMINANCE --by "<editor>"
```

```bash
npm run editorial -- approve CD.40.DOMINANCE --by "<expert>" --notes "..."
```

```bash
npm run editorial -- request-changes CD.40.DOMINANCE --by "<expert>" --notes "..."
```

- **`lint`** checks unique ids, known roles, statuses and bases, and banned fatalistic wording. A `sach` passage must quote fired rules
  through a slot or declare cites. Quotes must be balanced. Lint also reports passages that never render on the regression charts.
  Approval stores a hash of the passages; editing an approved module without sending it back to draft fails lint.
- **`preview`** prints a chapter (default `cong_danh`) for a regression chart, each sentence with its basis and rule ids.
- `node tools/interpret/evaluate.ts` runs every chapter on every regression chart and prints length, independent grounds, pass rate,
  warnings, how many book sentences two charts share word for word, and CPU time; `--md <file>` writes the report
  ([docs/examples/interpret-eval-30.md](examples/interpret-eval-30.md)); `--chart <i> [chapter]` prints the text with its warnings.
- **`approve`** refuses when the reviewer is the module's author. Run `npm run build:knowledge` after any change.

**Current status:** all 27 active modules (shared and per-chapter) are `draft`; `S.45.CROSS` is `retired` (cross-palace readings are now
told inside the themes). They were written by the assistant and have not been reviewed by a practitioner.
The pipeline reports this on every output (`quality.editorial.allApproved = false`). Do not describe the output as expert-quality until
the modules are approved.

## Tests

```bash
npm run test:interpret
```

```bash
npm run typecheck
```

`node --test` (74 tests) covers:
- DSL semantics; Python parity on all 30 fixture charts, for `tu_vi` and for `bat_tu`;
- the 17/05/1990 Công danh chapter: quality pass with 0 warnings, 800–1,500 words, content assertions (configuration, one-ground
  counting, brightness said once, same-book counter, cross-palace link, timing);
- every chapter × every chart: no quality error, every `sach` sentence rests on verified rules that fired (or the engine's time
  readings), no banned wording outside quotes, ≤ 1,550 words, deterministic;
- every opposed pair narrated together, every sensitive chapter carries its notice;
- length follows evidence (a chapter without grounds stays ≤ 450 words);
- personalization (median share of word-for-word identical book sentences between two charts ≤ 5%);
- rare configurations (vô chính diệu, Tuần + Triệt, Hóa Kỵ in Mệnh, Thân in Quan Lộc, a 96-year-old and a 3-year-old in the time chapter);
- combined chapters (one frame per palace, one notice, one synthesis); Bát Tự (pillars from the engine, only `BT_` rules, no dụng thần claim);
- condition shortening and citation rendering;
- D1 migrations + seed under `node:sqlite` produce the same text as the bundle for every chapter; a cache round-trip.

Examples (verbatim output, every chapter): [17/05/1990](examples/interpret-v2-17-05-1990.md),
[Mệnh vô chính diệu](examples/interpret-v2-menh-vo-chinh-dieu.md), [Tuần + Triệt ở Quan Lộc](examples/interpret-v2-tuan-triet-quan-loc.md).
Evaluation over 30 charts: [interpret-eval-30.md](examples/interpret-eval-30.md). The v1 Công danh output, kept for comparison:
[cong-danh-17-05-1990.md](examples/cong-danh-17-05-1990.md).

## Before / after (Công danh, 17/05/1990)

| | v1 (`interpret-1.0.0`) | v2 (`interpret-2.0.0`) |
|---|---|---|
| organisation | by mechanism: favourable list, limiting list, a separate "dominance" paragraph | by argument: each theme states its lead reading, what supports it, what limits it, and how the two relate, in one paragraph |
| limiting readings | listed together, then weighed in a later paragraph | placed next to the reading they limit, same-book counter first ("Ngay trong Toàn Thư đã có câu hãm bớt…") |
| brightness | one sentence | attached to the theme it modifies; the Khảo Luận p.233 principle said once per chapter |
| environment | Phu Thê (opposite Quan Lộc) | Thiên Di (opposite Mệnh), the outside world |
| conditions | "Mệnh ở Tỵ" repeated with every reading | context clauses said once; absent-star requirements and cát/sát counts rendered |
| chapters | Công danh only | ten chapters, including the time chapter and a Bát Tự chapter |

## What still needs a human expert

- Every module is a draft written by the assistant: wording, the order of arguments and the system's conventions (the five criteria, "both
  hold", the theme grouping) need a practitioner's review before any module is approved.
- The semantic lexicon decides which concept a reading expresses; corpus checks found and fixed over-broad cues (e.g. "vẹn toàn" no longer
  means marital harmony), but the lexicon has not been reviewed reading by reading.
- Bát Tự: strength, useful god and structure have no verified, wired rules; the 八字真宗 direct judgements wait for the `zz=True`
  integration decision.
- Health, money and relationship chapters carry notices; their readings are symbolic and must never be presented as diagnosis or advice.
