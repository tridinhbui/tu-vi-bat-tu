# Star dignity audit — Miếu · Vượng · Đắc · (Lợi) · Bình · Hãm for every star of Thiên Bàn

Knowledge base `dignity-kb-1`, 2026-10-18. Full 102-star × 12-branch × 3-school matrix: [STAR-DIGNITY-COVERAGE.md](STAR-DIGNITY-COVERAGE.md)
(generated). Phụ tinh transcription detail: [AUX-DIGNITY.md](AUX-DIGNITY.md).

## 1. Architecture: one authority, three readers

```
page images ─► tools/build_aux_dignity.py (phụ tinh) ─┐
               tools/build_dignity_kb.py (chính tinh) ─┴─► engine/data/dignity_kb.json   (+ dignity_vn.json / dignity_toanthu.json, generated)
                                                               │
            ┌──────────────────────────────────────────────────┼───────────────────────────────────────────┐
  engine/tvbt/dignity.py classify()            src/interpret/dignity.ts classify()           /api/dignity/classify
  → tuvi.py palace.dignity_status (badges)       → graph.ts star nodes + dignity_from edges     (one cell, JSON)
  → major_dignity / minor_dignity → rule facts   → planner.ts citations (book + page)
```

The results are precomputed per school, star and branch, so both languages only look them up. Neither language recomputes
anything, which means the two pipelines cannot drift apart. Tests prove they agree on every star of every palace of 70 fixture charts
(TS) and of 1,728 charts per school (Python).

**Result** for `(star, branch, school)`:

| status | carries | used by rules / badges |
|---|---|---|
| `VERIFIED` | value, printed term, book, page, `legacy`?, `variants` (what the other books say) | yes: the level |
| `CONFLICT` | the book's own two readings with pages | no level. Badge `?` lists both; rule facts get `unspecified` |
| `UNVERIFIED` | reason (book silent / unreadable / experimental), `variants` | nothing |
| `NOT_APPLICABLE` | reason (a book says brightness is not asked) | nothing |

* **Inputs** are star (name, id or alias; NFC/NFD, any case or tone placement), branch, and school (`thuc_hanh`, the default;
  `toan_thu`; `khao_luan`).
* **Ids** are mark-stripped slugs. `Quan Phủ`/`Quan Phù` would collide, so they get explicit ids, and a bare `quan phu` refuses to
  resolve.
* **Fallback:** chính tinh never fall back. For phụ tinh, if the chosen book has no table for the star at all, the next book is
  used for the whole star (TH → TT → KL), and the result names it. A tabulated star's unnamed branch stays UNVERIFIED.
* **Never:** a default "bình", a level from a star's cát/hung group, a level from another star, or a cell mixed from two books.

## 2. Audit of the previous implementation (before this change)

* Chính tinh came from `dignity_vn.json` (TH) and `dignity_toanthu.json` (TT). Phụ tinh came from `dignity_aux.json` (aux-dignity-1).
  There was no status: "unknown" and "conflicting" were the same `None`. The variants inside a book lived only in free-text notes.
* **Polarity vs dignity:** none of the code derives brightness from cát/hung. `starKind` (cát/trung/hung colour) and
  `CAT_STARS`/`SAT_STARS` counts are separate from dignity. Nothing silently defaults to "bình".
* **Stale text:** `analysis.py` said phụ-tinh brightness had no verified data. Fixed.
* **Wrong citation:** `planner.ts` printed "Thực Hành tr.N" even under the Toàn Thư school. It now cites the book the level came
  from.
* **Transcription errors**, found by re-reading every Thực Hành chính tinh header (pp.29–48) from the page image:
  * **Thiên Cơ Dần/Thân** was stored *vượng*. The header says "Vượng thì Mão Dậu, **Địa** Dần Thân", so these are **đắc**. "Địa" means
    đắc here, as in Tử Vi p.29 and Thiên Phủ p.37.
  * **Thiên Cơ Thìn/Tuất** was stored *bình*. The header says "Bình nơi Tỵ, Hợi, **Ích** Thìn Tuất". "Ích" is not on the scale, so
    these cells are now UNVERIFIED.
* **Readings kept but now documented:**
  * Thiên Đồng Dần ("**Lợi** về độc chiếm nơi Dần") was stored đắc. It stays đắc, marked `legacy`.
  * Thái Âm Mùi/Thân ("lợi ích") is stored đắc. This one is confirmed by p.40 prose: "cung đắc địa thôi (không phải Miếu, Vượng)".
  * The ambiguous Liêm Trinh / Phá Quân "Cùng là Mão Dậu" are confirmed hãm by p.37 and p.49 prose.
* **Toàn Thư** chính tinh pages pp.21–40 were image-checked. Every phú line matches. What was new is the conflicts in the book's own
  voice (§4).
* **Khảo Luận** chính tinh (pp.186–190) was never captured before. It is now the `khao_luan` school, with 13 stars (it gives no
  Tử Vi table).

## 3. Coverage (reachable cells only; `—` cells no chart can produce are excluded)

| School | Reachable cells | VERIFIED | CONFLICT | UNVERIFIED | NOT_APPLICABLE |
|---|---|---|---|---|---|
| Thực Hành (default) | 1030 | 299 (29.0%) | 1 | 706 | 24 |
| Toàn Thư | 1030 | 264 (25.6%) | 12 | 730 | 24 |
| Khảo Luận | 1030 | 305 (29.6%) | 5 | 696 | 24 |

All 102 stars are inventoried: the 98 placed stars plus the 4 Tứ Hóa. In the default school:

* **19 stars are fully verified.** That is 11 of the 14 chính tinh (not Thiên Cơ: Thìn, Tuất; not Thái Dương: Mùi, Thân; not
  Vũ Khúc: 6 cells the book does not name), plus Văn Khúc, Lộc Tồn, Kình Dương, Đà La, Đại Hao, Tiểu Hao, Hỏa Tinh and Kiếp Sát.
* **19 stars are partly classified**, i.e. the book names only some branches.
* **2 stars are not applicable:** Thiên Thương and Thiên Sứ (TT p.54).
* **62 stars have no classification in any book.** These include Khôi Việt, Đào Hồng Hỷ, Quang Quý, Thai Tọa, the 12 Trường Sinh
  stages, most of the Thái Tuế and Lộc Tồn rings, and Tứ Hóa (kept experimental).

The 29% is not a gap to fill. It is how much the books actually classify. A 100% coverage figure would only be possible by
inventing levels.

## 4. Conflicts (the book prints two readings in its own voice) — never resolved by the software

| School | Star | Branch | Readings |
|---|---|---|---|
| Toàn Thư | Thái Âm | Tý, Sửu / Hợi, Tuất | phú vượng / miếu vs Hi Di đắc (p.31) |
| Toàn Thư | Tham Lang | Tý | vượng and hãm (p.32) |
| Toàn Thư | Văn Xương | Thìn, Tỵ, Ngọ, Mão, Dậu | phú list vs the song and its gloss (p.41; p.42 says it cannot be settled) |
| Toàn Thư | Kình Dương | Tý | vượng (phú 1) vs hãm (phú 4), p.50 |
| Thực Hành | Linh Tinh | Tỵ | under both Miếu and Hãm, p.64 |
| Khảo Luận | Tham Lang | Thìn, Tuất, Dần, Thân | p.189 vs p.101 |

School disagreements (different books) are not conflicts: each school returns its own value, and `variants` lists the others. For
example, Thiên Cơ Thìn is UNVERIFIED in TH, bình in TT and miếu in KL. Reported third-party readings (phú nôm, "Tử Vi Việt") appear as
`variants` with `reported`, never as results.

## 5. Integration

* **Chart UI** (`engine/web/js/tuvi.js`): badges for chính and phụ tinh come from `palace.dignity_status`.
  * VERIFIED prints the book's term in the existing compact badge, with the book, the page and the other books in the tooltip.
  * CONFLICT prints a dashed "?" whose tooltip lists the readings.
  * UNVERIFIED and NOT_APPLICABLE print nothing. The glossary has entries for "Lợi" and for "chưa thống nhất".
* **Interpretation:** rules see only VERIFIED levels, and everything else is `unspecified` (the DSL's unknown). The TS planner
  cites the actual book and page.
* **Knowledge graph** (`graph.ts`): star nodes carry `dignity`, `dignityStatus`, term, book, page, alternatives and variants. A
  `dignity_from` edge links each star placement to its source node with the branch and pages. The KG session's trigger atoms read
  the same rule facts.
* **API:** `GET /api/dignity/classify?star=&branch=&school=`.

## 6. Tests and results (2026-10-18)

* Python: `engine/tests/test_dignity_kb.py` (33) and `test_aux_dignity.py` (56).
  * They check that the builder output equals the committed KB and that every placed star is inventoried.
  * Every star × 12 branches × 3 schools has exactly one status, and only VERIFIED has a level.
  * 25 cells are pinned from the page images, and stars with no table stay unclassified whatever their cát/hung group.
  * Badges, level fields and rule facts are checked identical over 1,728 charts per school, with every chính tinh in all 12 địa chi.
  * The API is covered.
* TS: `src/interpret/test/dignity.test.ts`.
  * The Python `dignity_status` equals the TS `classify` (status, level, term, book, page, alternatives, variants) on every star of
    every palace of 70 charts, and the graph, level fields and fact base agree.
  * The TS slug equals the Python slug, normalisation works, and pinned cells across the three schools hold.
* `tools/dignity_coverage.py --check` passes: an exhaustive placement sweep of 60 years × every day × 12 hours.
* Regression against HEAD 582d05c:
  * Star placement, palaces, Tứ Hóa, đại hạn and cục are **identical on 600 charts**.
  * Thực Hành findings: **−3** (`TV_TH_MV_MENH_CO_MIEU_VUONG`, Thiên Cơ at Dần/Thân is now đắc).
  * Toàn Thư school findings: **−63** on 44 of 120 charts, all from the new CONFLICT cells (Thái Âm, Văn Xương).

## 7. Open research gaps and decisions for a reviewer

1. **Three-valued use of CONFLICT — done (dignity-kb-2).** A CONFLICT cell still reaches the facts as
   `palace.dignity.<star> = "unspecified"` (badges, sentences and every other reader are unchanged). Its readings also go to the
   rule evaluator as `alt:palace.dignity.<star> = [v1, v2]` (`reasoning/facts.py`). A condition on that fact is TRUE when every
   reading satisfies it, FALSE when none does, and UNKNOWN otherwise. A reading with no level (`null`) is unknown. No reading is
   ever picked. Python `knowledge/dsl.py` (`ALT`, `_leaf`) and TS `src/interpret/dsl.ts` (`ALT`, `leaf`) share the cases in
   `src/interpret/test/fixtures/dsl_alternatives.json`. `fixtures/conflicts.json` (`tools/interpret/make_conflict_fixtures.py`) holds
   Toàn Thư charts covering every Toàn Thư CONFLICT cell, checked for TS↔Python parity.
   A/B over 120 seeded births, Tử Vi rules: Thực Hành is unchanged (7,946 findings, +0 −0). Toàn Thư gains 53 (7,762 → 7,815) and
   loses none. Of the 63 Toàn Thư findings dignity-kb-1 lost against b560c45, 53 come back: Thái Âm Tý/Sửu/Tuất/Hợi and Văn Xương
   Tỵ/Thìn, where both readings are bright. The other 10 stay UNKNOWN (pending) on purpose. Nine read Văn Xương Mão/Dậu, where one
   reading has no level (`[đắc, null]`, `[miếu, null]`). One reads Văn Xương Ngọ, where the readings disagree (`[hãm, lợi]`).
2. **Legacy lợi → đắc** cells: Thiên Đồng Dần (TH), Văn Xương Hợi (TH) and six Văn Xương cells (TT). Keep them, or make them `lợi`?
3. **Thiên Cơ Thìn/Tuất (TH)**, printed "Ích": read as lợi, or leave unverified?
4. `TV_TT_MENH_KINH_MIEU` requires exactly "miếu". Under TH, Kình at tứ mộ is "đắc" (AUX-DIGNITY.md).
5. **No book tabulates** Khôi Việt, Đào Hồng Hỷ, Quang Quý, Thai Tọa, the rings, or Tứ Hóa (experimental only). A new source would
   be needed: Hi Di's Chinese text, or 紫微斗數全書 itself rather than a translation.
6. The API offers only the `thuc_hanh` and `toan_thu` schools. `khao_luan` is available in the classifier but not exposed in the
   UI.
