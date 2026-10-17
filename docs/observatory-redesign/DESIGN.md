# Digital Eastern Observatory — result-page redesign

Scope: the Bát Tự and Tử Vi *result* pages (`#chart-view`). Home, learning, compare and library pages are untouched.
No calculation, rule, API contract, school or provenance logic changes. Every value shown comes from the existing `/api/chart`, `/api/year`, `/api/reasoning`, `/api/analysis` responses.

## 1. Audit of the existing result page

| # | What exists | Problem |
|---|---|---|
| 1 | `res-head`: 3.8rem H1 "Lá số đã được lập", meta line, three chips, two buttons (~390px tall) | The chart starts below the fold at 1440×900. The title says nothing the user does not know. |
| 2 | `summaryBazi` / `summaryTuvi`: a boxed section with four equal cards, then findings cards, then limits, then buttons (~1300px) | Pure text, shown *before* the chart. Four identical cards. Violates "chart first, explain second". |
| 3 | `.r-sec` header ("Bốn trụ, tám chữ" / "Mười hai cung của bạn") + `.sec-sub` | A second hero-size heading over the chart. Repeats the page title role. |
| 4 | Four pillars as four identical rounded cards with shadow | Cards, not a structure. No alignment of stem / branch / hidden-stem rows across pillars, no relations drawn. |
| 5 | Five Elements pentagon in a floating card | Good component, but isolated from the pillars; no seasonal Qi anywhere. |
| 6 | Đại vận: a row of small chips under the chart; Tử Vi đại hạn: *only* in the report, a static list | Not interactive, not tied to the chart. Tử Vi cycles cannot be explored. |
| 7 | Tử Vi board: navy/indigo (`--indigo`) block, 16 independent rounded cards | Off-brief colour (indigo reads purple-ish), dark island inside a paper page, no hierarchy between Mệnh/Thân/chính tinh/phụ tinh/Tứ Hóa. |
| 8 | Drawer for palace detail | Good idea, but long stacked sections; evidence level mixed with facts. |
| 9 | Report chapters (`rp-layout`) | The right place for deep reading, but every chapter repeats the same eyebrow / border pattern. Kept; restyled so the three evidence tiers look different. |

Duplicated layouts: (2)+(4)+(5) are the same "card grid"; `.bs-c`, `.facts>div`, `.summary-strip>div`, `.tg-rows>div`, `.tp-p` are five variants of one small bordered box; `.tl-i` timeline chips are rendered the same for Bát Tự đại vận, Tử Vi đại hạn and months.

## 2. Two compositions, one language

### Shared system
* **Paper & ink**: ivory ground `#FAF6EF`, parchment `#F0E7D8`, charcoal ink `#282923`, muted cinnabar `#A7432C` (only for Nhật Chủ / Mệnh / sourced seal), brass `#B08A53` (rules, ticks, Thân). No purple, no navy. The Tử Vi board moves from indigo to the same paper.
* **Type**: Newsreader (display, editorial) for glyphs, names, numbers. Inter for tiny precise labels (uppercase, tracked). Han glyphs from the data tables (`STEMS`, `BRANCHES`, `EL`).
* **Lines not boxes**: 1px hairlines, corner ticks, ruler marks. One bounded "plate" per page; everything else is open page with rules.
* **Evidence tiers — one marker system used on both pages and in the reports**:
  * **Dữ kiện tính toán** — solid ink square, plain text. Raw chart data.
  * **Theo sách** — cinnabar seal (filled ring), a rule verified against a cited book page.
  * **Giả thuyết / quy tắc nháp** — dashed outline, brass. Draft rules and experimental formations; shown only in *Chuyên sâu* (as today).
* **One focal point per screen**: the plate (pillars / twelve palaces). Everything else answers a selection.
* **Progressive disclosure**: a single contextual *reading panel* replaces repeated cards. Default state shows only identity; selecting reveals facts → book readings → drafts.
* **Motion**: 180–320ms ease, only for selection, line drawing and the timeline needle; all off under `prefers-reduced-motion`.

### A. Bát Tự — "The Energy Architecture"
Asymmetric two-column stage. **Left (≈ 8/12): the pillar plate** — four tall manuscript columns on a ruled plate with a left ruler (Thiên can / Địa chi / Tàng can / Thập thần / Trường sinh). Day pillar stands taller with a cinnabar Nhật Chủ seal. Above the plate, two relation lanes (Can, Chi) draw arcs between pillars from `bazi.relations`. **Right (4/12): the reading panel** (sticky). Below: *Ngũ Hành* pentagon (existing component, restyled) beside the *Khí tháng* seasonal dial (12 branches, month branch = Nguyệt lệnh, the four pillar branches placed on the ring, Trường sinh of the month). Full-width **Đại vận timeline**: nine tablets on a ruled age axis with a "now" needle; selecting one opens its ten years (annual pillars from `/api/year`); selecting a year shows its interactions with the natal chart.

### B. Tử Vi — "The Twelve Palaces"
**Centerpiece: the real 12-palace plate** on paper — shared hairlines, no cards. Hierarchy inside a cell: palace name (serif, small caps) → **chính tinh** (large serif, with Miếu/Vượng… mark) → **phụ tinh** (small sans; cát `+`, sát `–`, trung tính plain) → **Tứ Hóa** as round Han seals (祿權科忌). Mệnh has a cinnabar rule and 命 seal; Thân a brass 身 seal. Centre holds identity (Can Chi năm, Cục, Bản mệnh, Mệnh/Thân chủ). Selecting (or hovering) a palace draws Tam Phương Tứ Chính (opposite axis solid cinnabar, tam hợp dashed brass) and dims the other eight. **Right: contextual panel** (bottom sheet on phones). **Below the plate: cycle timeline** — twelve đại hạn along an age axis; selecting one marks its palace on the plate and opens its ten years; selecting a year marks tiểu hạn and lưu Thái Tuế on the plate and shows lưu Tứ Hóa and book readings.

### Modes and devices
* *Dễ hiểu* / *Chuyên sâu* keep their meaning: drafts and raw reasoning stay behind *Chuyên sâu*.
* ≥1180px: plate + sticky panel. 768–1179: plate full width, panel as bottom sheet. ≤820: **field notebook** — ruled paper, margin line, palace list (existing "Tổng quan") as notebook entries, the full plate scrolls sideways, pillars stay four columns with row captions above each band.

## 3. Out of scope / guarantees
* No change to `engine/tvbt/**`, API shapes, rule packs, schools. Experimental formations remain behind `?thu-nghiem`.
* No deploy. Preview only on a local server.

## 4. What was built

Files (all presentation; nothing under `engine/tvbt/**`, `engine/data/**`, `engine/tests/**` was touched):

| File | Role |
|---|---|
| `engine/web/css/atlas.css` (new) | Shared system (tokens, plate frame, evidence tiers, timeline), Bát Tự stage, Tử Vi plate, bottom sheet, notebook mode |
| `engine/web/js/atlas.js` (new) | `EV` tier markers + `tier()`/`evLegend()`, per-chart `/api/year` cache (`yearData`), timeline helpers |
| `engine/web/js/bazi.js` | `renderBazi` rebuilt: pillar plate, relation arcs, seasonal dial, Ngũ Hành (existing component), đại vận → năm timeline, reading panel. Returns the same `{counts, parts}` for the report |
| `engine/web/js/tuvi.js` | `renderTuvi` rebuilt: 12-palace plate, hover/select Tam Phương Tứ Chính, panel/bottom sheet, đại hạn → năm timeline with board badges. Returns the same `{highlight, clearHighlight, select, byName, menh, than, timelineHtml}` |
| `engine/web/index.html` | `#chart-view` reordered: slim masthead → system switch → plate → quick read → full report. All ids/`data-go`/`data-depth` kept |
| `engine/web/css/app.css` | 207 superseded selectors removed (old pillar cards, summary strip, dark Tử Vi board, drawer). Home/learn/library pages pixel-diffed before/after: unchanged apart from sub-pixel noise |
| `.claude/launch.json` (new, untracked) | Local preview server entry (port 8765); not part of the redesign, delete if unwanted |

Data used on screen: `bazi.pillars/hidden/relations/luck_pillars/jie_used`, `tuvi.palaces/structure/tu_hoa/dai_han/stars`, `reasoning.findings` (verified vs draft split by `basis`), `/api/year` (`annual_pillar`, `luck_vs_natal`, `months`, `tieu_han_*`, `luu_thai_tue_*`, `luu_tu_hoa*`). No new calculation; the only arithmetic is the year label of a 10-year period (Bát Tự: `ceil(start_year_exact)`; Tử Vi: `req.year + tuổi mụ − 1`, the formula `insights.currentPhase` already uses).

Provenance rules preserved: the three tiers (calc / theo sách / giả thuyết) are separate blocks; drafts and experimental formations stay `pro-only`; the verified/draft badge text on `finding-card` is unchanged; findings are routed to a pillar/element by claim id for display only — unmatched ones stay in the report chapters.

## 5. Test matrix (local, Chromium, sample chart 17/05/1990 10:30 Nam)

* Screenshots at 375 / 768 / 1024 / 1440 for both tabs, before and after (`before-*.png`, `after-*.png`, `compare-*.png`, `after-state-*.png`).
* Interaction script at all four widths: select pillar, relation arc, element, đại vận, year; select palace, hover preview, đại hạn, year; close sheet. 0 page errors / 0 console errors.
* Keyboard only: pillar header, arc, timeline tab (Space), element, palace focus-preview, Enter select, Esc clear.
* Modes: Dễ hiểu and Chuyên sâu; `?thu-nghiem` (experimental condition highlight → 4 palaces + 4 stars lit); unknown birth hour view; saved charts/compare untouched.
* Contrast of text tokens on plate/paper ≥ 4.5:1 after darkening `--ink-3` and `--ev-hyp`.
* `pytest` (engine): 1074 passed, 1 skipped, 2 xfailed.

## 6. Evaluation

**Hierarchy.** Chart start moved from roughly 2,400 px (Bát Tự) / 2,800 px (Tử Vi) down the page at 1440 to ≈ 280 px; at 375 the plate is on the first screen. Each page has one focal object; the panel, instruments and timeline answer selections. Inside the Tử Vi cell the order is palace label → chính tinh (largest serif) → phụ tinh (small sans, +/– signs) → Tứ Hóa seals; Mệnh/Thân carry their own seals and rules.

**Readability.** Han glyphs, names and element marks share one baseline grid on the plate; ruled rows replace boxes; muted tones meet 4.5:1. Dense Tử Vi cells wrap rather than truncate; below 700 px the 12 palaces are a ruled notebook list (existing "Tổng quan" idea) with the full plate one tap away.

**Interaction.** Every selection changes exactly one panel; arcs, board lines, badges and timeline needle give immediate spatial feedback; hover previews Tam Phương Tứ Chính without committing. Phones get a bottom sheet for palaces and an inline panel placed next to the control that was used.

**Known limits / next steps**
* Full-page height is not shorter (the report is intentionally unchanged below the plate): Bát Tự 10.8k → 11.2k px, Tử Vi 16.0k → 16.0k px at 1440. A second pass could fold report chapters behind the panel.
* Only Chromium was exercised; no Safari/Firefox pass yet.
* Pillar cells are mouse-clickable; keyboard users use the pillar header buttons (same action).
* Tử Vi tam phương lines are drawn centre-to-centre and cross neighbouring text; anchoring them to cell corners would be cleaner.
* Not deployed.
