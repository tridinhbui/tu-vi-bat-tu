# Deterministic interpretation pipeline (TypeScript + Cloudflare D1/R2)

The Tử Vi interpretation layer runs in the Worker as plain TypeScript. Nothing calls a language model at runtime: there is no LLM, AI API,
Workers AI or AI Gateway. The Python engine in the container still computes the chart, and serves it to the Worker as facts through
`POST /api/facts`. Everything after that step is deterministic TypeScript in `src/interpret/`.

```
birth record ─► container /api/facts ─► facts (palaces, stars, Tứ Hóa, decades, current year)
                                            │
  1 Knowledge graph        graph.ts         │ per-chart nodes/edges; rule conditions become depends_on edges between palaces
  2 Rule inference         dsl.ts, engine.ts│ forward chaining over 1,437 book rules; exact parity with the Python engine
     + semantic evidence   semantic.ts      │ book reading → concept, facet, polarity; condition rendered from the chart's true leaves
  3 Narrative planning     planner.ts       │ argument graph: base / qualifier / cross / environment / timing; dominance; tensions
  4 Narrative generation   generator.ts     │ editorial content modules (JSON) realized with slots, variants, word budget
  5 Quality validation     validate.ts      ▼ grounding, unsupported conclusions, repetition, contradictions, inflation, budget
                                       ChapterOutput { paragraphs, text, quality, argument, trace }
```

Entry point: `interpret(chart, chapter, knowledge)` in `src/interpret/pipeline.ts`. The chapters are `cong_danh`, `tai_bach` and `menh`
(engine `interpret-1.1.0`).

One planner, one generator and one set of generic content modules (`content/core.json`) serve every chapter. `chapters.ts` gives each
chapter:
- its focus palace;
- the semantic facets in scope;
- the environment palace (Thiên Di / Điền Trạch / Phúc Đức);
- the linked palaces;
- its timing concepts.

No rule and no template is duplicated per chapter.

The audit that produced 1.1 is in [INTERPRETATION-AUDIT.md](INTERPRETATION-AUDIT.md): a sentence-by-sentence review, rule-activation
fixes, a 48-chart sweep, and the separation of automated validation from expert review.

## What each stage guarantees

- **Rule inference.** The DSL uses three-valued logic: all / any / not / count / fact / ref. `src/interpret/test/engine.test.ts` checks
  that the same rules fire, with the same claims, as in Python, on 8 fixture charts (`tools/interpret/make_fixtures.py`).
- **Rule activation fixes made before synthesis.**
  - The 27 "giáp" (flanking) rules fired when both stars sat in one neighbouring palace. Each rule now requires A on one side and B on the
    other. `tools/fix_giap.py` re-applies this after any pack rebuild.
  - Toàn Thư palace rules whose reading names a brightness, an absence of sát tinh, or "độc thủ" now test it, or stay drafts.
  - `engine/tests/test_rule_integrity.py` guards both fixes.
- **Evidence.** A rule's reading is split from its condition. Concepts come from the semantic lexicon
  (`engine/data/semantic/concepts.json`), using the longest cue and handling negators. Grounds are deduplicated by root star atoms, so two
  readings written for the same condition count as one independent ground.
- **Cross-palace dependencies** are tested counterfactually. A reading "needs" a star in another palace only if the rule fails when that
  star is removed from the palaces that chiếu in. Otherwise the text says that star also satisfies the condition but is not relied on.
- **Planning.**
  - When a favourable reading and a limiting reading coexist, the planner applies five public criteria:
    1. same major star or not;
    2. same book or not;
    3. which condition is more specific;
    4. which side rests on a major star and which on a malefic star;
    5. how many independent grounds each side has.
  - The resulting relation is one of:
    - narrower case read first (`specific_qualifier` / `specific_base`);
    - added sát stars, read as a degree adjustment (`sat_qualifier`);
    - both hold.
  - The text says the books do not rank the readings; the precedence is the system's stated convention.
  - Tensions come only from a `contradicts` relation or the same facet.
  - Timing readings that disagree (early vs late) are both kept. A lean is stated only when one side is absent, or when one side rests on
    the year branch or gender alone while the other rests on stars of this chart.
  - Rules written for Mệnh only are not applied to Quan Lộc; the chapter lists them as scope notes.
- **Generation.** Content modules (`src/interpret/content/cong_danh.json`) hold passages:
  - Each passage has a basis (`sach`, `dieu_kien`, `tinh_toan` or `he_thong`), gate conditions and variants.
  - Templates use slots `{x}`, list slots `{list:name}` and optional segments `{?slot|text}`.
  - A variant is picked by a hash of the chart (FNV), not at random, and repeated openers are avoided.
  - Over 1,500 words, lists are shortened by salience. Reasoning paragraphs are never shortened. Text is never padded.
- **Validation.**
  - Errors: missing_source, unsupported_conclusion, banned_wording, contradiction_not_explained.
  - Warnings: duplicated_meaning, near_duplicate_sentence, excessive_repetition, repeated_openers, weak_personalization, possible_inflation,
    over_budget, thin_for_evidence.
  - Every output also carries an editorial status. While any module is unapproved, the output includes a notice saying so.

## Knowledge base and storage

- `npm run build:knowledge` (`tools/interpret/build.ts`) compiles the rule packs, sources, claim labels, semantic lexicon, star profiles and
  content modules into:
  - `src/interpret/generated/knowledge.json`: bundled into the Worker. The `version` is a content hash.
  - `migrations/interpret/0002_seed.sql`: the same content, relational.
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
    identical to the bundled store's for every chapter.
  - `loadKnowledge` keeps the D1 knowledge per isolate, keyed by `kb_meta.version`. A request costs one row; the full read happens once
    per isolate, and again only after a new seed.
  - `LayeredCache` checks R2 (`interpretations/<key>.json`), then the D1 `interpretations` table, then the Workers Cache API.
  - The cache key is SHA-256 of the chart facts, chapter, engine version and knowledge version. Changing a rule or a module therefore
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
POST /api/interpret { ...birth record, "chapter": "cong_danh" | "tai_bach" | "menh" }
```

The response header `x-interpret-cache` is `hit` or `miss`.

### Cost

One chapter costs about 40 ms of CPU uncached (median over 144 renders on Node; p95 52 ms): rule inference over 1,437 rules plus planning
and realization. This needs the Workers Paid CPU limit, which the container deployment already requires. A cached
request costs one R2 or D1 read. There is no per-token cost. The bundled knowledge adds about 200 KB gzip to the Worker.

## Editorial workflow

Modules move through `draft → in_review → approved` (or `retired`). Each step is recorded in the module's `reviews` and seeded into
`module_reviews`.

```bash
npm run editorial -- lint
```

```bash
npm run editorial -- preview 0
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
- **`preview`** prints the chapter for a regression chart, each sentence with its basis and rule ids.
- **`approve`** refuses when the reviewer is the module's author. Run `npm run build:knowledge` after any change.

**Current status:** all 10 modules are `draft`. They were written by the assistant and have not been reviewed by a practitioner.
The pipeline reports this on every output (`quality.editorial.allApproved = false`). Do not describe the output as expert-quality until
the modules are approved.

## Tools

```bash
node tools/interpret/sweep.ts cong_danh
```

```bash
node tools/interpret/example.ts 0
```

```bash
.venv/bin/python tools/interpret/make_sweep.py
```

```bash
.venv/bin/python tools/fix_giap.py
```

- `sweep.ts`: quality, words, CPU and recurring sentence templates over the 48-chart corpus.
- `example.ts`: writes the chapters of a corpus chart to `docs/examples/`.
- `make_sweep.py`: rebuilds the coverage corpus (`sweep.json.gz`).
- `fix_giap.py`: re-applies the giáp ordering after any pack rebuild.

## Tests

```bash
npm run test:interpret
```

```bash
npm run typecheck
```

`node --test` covers:
- DSL semantics and Python parity on all fixture charts;
- the 17/05/1990 regression chapter: quality pass with 0 warnings, 800–1,500 words, specific content assertions, grounding of every `sach`
  sentence, determinism, personalization limits;
- D1 parity through `node:sqlite`;
- a cache round-trip.

`node --test` also covers `reasoning.test.ts` (counterfactual necessity, condition rendering, timing lean, dominance relations) and
`sweep.test.ts` (the per-chapter gate over all 48 charts).

Example output for 17/05/1990:
- [Công danh](examples/cong-danh-17-05-1990.md)
- [Tài bạch](examples/tai-bach-17-05-1990.md)
- [Mệnh](examples/menh-17-05-1990.md)

The v1.0 Công danh text, kept for before/after comparison, is [cong-danh-17-05-1990-v1.0.md](examples/cong-danh-17-05-1990-v1.0.md).
