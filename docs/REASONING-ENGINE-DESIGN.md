# Reasoning engine design (evidence-1.0)

**Goal.** Turn isolated rule matches into source-grounded, conditional conclusions that a reader can trace, with no language model and no numeric scoring.

The engine is implemented as a post-processor of the existing rule engine. It runs inside the production Python container (the same place as `/api/reasoning`), so it is Cloudflare-compatible today: the Worker proxies to the container. It does not add a fifth interpretation stack: it reuses `positions.py`, `knowledge/dsl.py`, `reasoning/engine.py`, `temporal_facts.py`, `synthesis/semantics.claim_tone` and `bazi_deep/tvh_score.py`.

## 1. Pipeline

```
chart (tuvi.py, bazi.py)                       calculation, unchanged except the audited fixes
  -> facts (reasoning/facts.py, positions.py)  objective facts per palace: own / xung chiếu / tam hợp / giáp kept apart
  -> rules (engine.run over data/pack_*.json)  one finding per rule that fires (verified-only by default)
  -> trigger atoms (conclusions.trigger_atoms) the chart facts that actually made each condition TRUE
  -> clusters (conclusions.cluster)            same palace + same direction + nested triggers = one conclusion
  -> qualifiers (data/qualifiers.json)         page-cited conditions that void / weaken / modify / are required for durability
  -> relations (conclusions.build)             support × limit pairs: same_trigger | nested | coexisting | complementary
  -> dossiers (dossier.build)                  six layers × 12 palaces
  -> period layer (temporal_facts.layered)     đại hạn, tiểu hạn, lưu Thái Tuế, lưu stars (KL pp.41-42), lưu/decade Tứ Hóa (labelled)
  -> Bát Tự (bazi_reading.build)               methods side by side, interactions, periods
  -> report (report.build)                     chapters with six fixed sections
```

Entry point: `tvbt.reasoning.interpretation.run(tv, bz, birth_year, year)`. API: `POST /api/interpretation`, which answers 404 unless `TVBT_DEEP_INTERPRETATION=1`. Cost: about 50 ms median per chart (200-chart sweep, max 75 ms).

## 2. Conclusion record

Every conclusion (`conclusions.Conclusion`) carries:

| field | meaning |
|---|---|
| `conclusion_id`, `topic`, `palace`, `aspect` | identity; topic = palace · aspect |
| `polarity` | support / limit / neutral. A rule whose effect is `limit` always limits; otherwise the tone of the reading's own words decides; mixed tone stays neutral |
| `contributing_facts` | the trigger atoms in Vietnamese ("Lộc Tồn ở Tài Bạch") |
| `supporting_rules` | rule id, reading, the book's own trigger wording, basis, books, page cites |
| `opposing_rules` | rules of the limiting conclusions it is related to |
| `applicability_conditions` | the book's trigger wording and any absence clauses ("không gặp sát tinh") |
| `invalidating_conditions` | evaluated qualifiers: effect, status (met / not_met / unknown), the chart facts that met it, source, open question |
| `source_references`, `school` | "Tử Vi Khảo Luận, tr.216", the books |
| `evidence_status`, `independent_sources`, `rule_count` | verified / draft / mixed; distinct books; rules |
| `generic` | rests only on birth-year or sex facts (shared by every chart of that year and sex) |
| `shared_basis_with` | conclusions in other palaces that rest on the same atoms (one fact, not two reasons) |
| `conflicts` | relation kind, shared facts, extra conditions of the narrower side, resolution, note |
| `unresolved_questions` | open operationalisations, unspecified brightness, draft rules |
| `final_interpretation` | the assembled sentence (template, no LLM) |

## 3. Trigger atoms and evidence independence

`trigger_atoms(expr, facts)` walks the rule condition and keeps only the sub-conditions that are true.

- For `any`, only the satisfied branches count.
- `not` contributes nothing: an absence is a condition, not a fact of the chart.
- Star facts are located in the palace that actually holds the star, using the role-typed facts of `positions.py` (own, xung chiếu, tam hợp, giáp).
- A sát/cát count leaf is expanded into the sát/cát stars actually present.
- Dignity leaves fold into their star.

**Two readings are the same evidence when their trigger signatures are nested** (A ⊆ B) in the same palace and direction. A cluster's support is its number of **distinct books**. The reasoning: several rules from one book are one voice, and several books reading the same fact are corroboration of one fact, not several facts.

## 4. Relations instead of resolution

The relation kinds are computed from trigger signatures. Counting conditions are kept for this step, so "Tử Vi + sát" is not mistaken for "Tử Vi".

| kind | test | what the reader is told |
|---|---|---|
| `same_trigger` | same atoms, same topic, opposite direction | the books disagree on the same fact; both kept |
| `complementary` | shared atoms, different topics | one fact, two different sides; not a contradiction |
| `nested` | one trigger ⊂ the other | the extra conditions of the narrower one; both kept. "Narrower first" is NOT applied (decision pending) |
| `coexisting` | different facts, same specific topic | both hold; read as a potential with a limit, not added or subtracted |

Pairs are formed only within one palace, and only when the two conclusions share a fact or a specific topic. Generic conclusions are never paired.

Readings of different palaces are never treated as contradictions. Natal readings and period readings are in different chapters, so a natal reading and a period reading are never set against each other.

## 5. Qualifiers (`data/qualifiers.json`)

A qualifier is a page-cited condition about a configuration, read on the page and paraphrased. Effects: `voids`, `weakens`, `modifies`, `requires_for_durability`, `strengthens`.

- It is selected by the conclusion's palace, its trigger stars standing **in** that palace, its aspect or its polarity.
- Its condition is evaluated in the rule DSL on that palace.
- Qualifiers never make a rule fire or stop firing.
- Ambiguous book words are operationalised explicitly, and the choice is shown as an open question.

Version 1.0 has nine qualifiers:

- Lộc Tồn + Không Kiếp đồng cung, KL p.142
- Lộc Tồn + Thái Tuế for durability, KL p.142
- Lộc đảo, KL p.142
- Lộc Tồn + Hóa Lộc đồng cung, KL p.142
- Khôi Việt under Tuần/Triệt/Kỵ, KL p.140
- Tuần/Triệt general modifier, KL p.141
- Tử Vi without Tả Hữu, TT p.20
- Tử Vi in Quan/Mệnh with Tả Hữu / Tướng / Lộc Mã, TT p.20
- Song Lộc at Mệnh-Tài-Quan, KL p.197

To add one: read the page, write the entry with `source` and any `open_question_vi`, then add a positive and a negative chart test.

## 6. Palace dossier: six layers

`dossier.build` returns, for **every** palace:

1. **bản cung**:
   - chính tinh, with brightness only from the selected table. An empty cell says so; nothing is guessed.
   - phụ tinh split into verified placement and common formula.
   - aux brightness with its source; Tứ Hóa; Tuần/Triệt; Trường Sinh stage.
   - thủ / đồng / vô chính diệu (TT p.17).
2. **tam phương**:
   - đồng cung, xung chiếu, hội chiếu (tam hợp) and giáp, kept apart.
   - giáp pairs.
   - chủ / khách (TT pp.17-18).
   - explicit vô chính diệu borrowing (TT p.18), with its limit stated.
3. **cách**:
   - rule-recognised configurations, with their qualifiers.
   - name-only detections, labelled unverified.
   - for Mệnh and Thân, the TT p.18 "thành phá" test, with its operationalisation listed as open questions.
4. **Mệnh–Thân–Cục**: on the Mệnh and Thân palaces only. Mệnh chủ / Thân chủ are marked NEEDS SOURCE.
5. **vận**:
   - which đại hạn the palace rules.
   - whether the year's đại hạn, tiểu hạn or lưu Thái Tuế is here or in its tam phương.
   - the lưu stars and the Tứ Hóa layers here.
6. **tổng hợp**: themes, supports, limits, met conditions, alternatives, open questions, and scope guards for Tật Ách, Phu Thê and Tử Tức.

## 7. Report

Chapters:

- Mệnh, Thân và Cục
- Tính cách
- Công danh (Quan Lộc + Thiên Di)
- Tài lộc (Tài Bạch + Điền Trạch)
- Quan hệ (Phu Thê, Tử Tức, Huynh Đệ, Phụ Mẫu, Nô Bộc)
- Tật Ách (biểu tượng)
- Vận hạn năm X
- Bát Tự

Each chapter has the same six sections: Nhận định tổng quan, Cơ sở luận giải, Yếu tố hỗ trợ, Điểm hạn chế và mâu thuẫn, Luận giải tổng hợp, Điều kiện và giới hạn.

The symbolic-reading disclaimer is said once, in the header. Generic and structural-label readings are listed under the limits section, never as support. Citations give book and page; the rule id is in the data.

**Period chapter.** It separates structure (the natal chapters) from activation (which palaces the year touches):

- It cites KL p.41 that lưu stars are transient and weigh less than the stars of the đại / tiểu hạn palace.
- It runs `van_han.read` (KL pp.233-236) for the đại hạn and tiểu hạn palaces.
- It labels lưu Tứ Hóa and decade Tứ Hóa as unsourced conventions.
- It never names an event, a date, an illness or a sum of money.

**Bát Tự chapter.**

- Two strength methods are shown side by side:
  - 八字真宗 p.27: all of đắc lệnh / đắc vị / đắc sinh → vượng; none → nhược; otherwise no verdict.
  - Thiệu Vĩ Hoa pp.331-355: strict 40%.
- No verdict is invented when they disagree.
- Element counts are labelled as counts.
- Interactions are shown with their span. A hợp is a potential combination; transformation is not decided.
- Thập Thần, visible and hidden.
- The verified 八字真宗 readings.
- Dụng thần: not concluded; the TVH điều hậu cell is shown as one school's list, with the book's own caveat about its origin.
- Year and luck interactions, structural only.

## 8. What stays outside, and the retirement plan

- **The production cards** (`/api/reasoning`) are unchanged. The next step is to render conclusions instead of raw findings once the decisions in INTERPRETATION-ENGINE-AUDIT.md §5 are taken.
- **`src/interpret/` (TS)** keeps its own tables: 4-pair stem clash, its own taxonomy. Freeze it, or port these fixes, before it is ever switched on.
- **`synthesis/` and `/api/deep-reading`** overlap with this layer. Once this layer is reviewed, retire deep-reading and keep synthesis only as a narrative experiment.
- **Rule-pack fixes belong in the builders**, not here: effect signs (RL-4), worked-example rules (RL-7), "hội" read as same palace (RL-10).

## 9. Determinism and tests

- All functions are pure, and every sort in the pipeline is fixed.
- `engine/tests/test_evidence_engine.py` holds 30 tests derived from pages and geometry:
  - calculations: Thiên Quý, the 干冲克 table, pairwise hình, year/luck hình, lưu Kình direction, lưu Tứ Hóa;
  - rule exclusion (KL p.218);
  - evidence independence and qualifiers;
  - contrasting charts: Lộc Tồn voided by Không Kiếp, Khôi without Triệt, ZZ vượng and nhược charts, "chưa thành";
  - vô chính diệu borrowing, scope guards, report structure, forbidden phrases;
  - edge charts: leap month, late Tý, both sides of Lập Xuân 2024;
  - determinism and performance.
