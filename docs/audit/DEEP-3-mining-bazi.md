# DEEP-3 — Bát Tự knowledge mining (2026-10-24)

Branch `claude/amazing-leakey-8afa25`. Scope: knowledge data under `engine/data/bazi_deep/` (+ the positional facts the new rules need in
`engine/tvbt/bazi_deep/kin.py`, the `WEB:<id>` check in `tools/book_text.py`, tests). Prose (`src/interpret/prose`, `src/interpret/reason`) untouched.

## 1. What was read

| Source | Pages / chapters | Raw text committed |
|---|---|---|
| Trích Thiên Tủy (TTT, text layer) | pp.59-78 (Bát Cách, Thể Dụng, Tinh Thần, Nguyệt Lệnh, Suy Vượng, Trung Hòa), 101-112 (Thanh/Trọc, Chân/Giả thần, Cương Nhu, Thuận Nghịch), 130-132 (Con Cái), 143-148 (Hà Tri), 161-170 (Tài Đức, Phấn Ức, Ân Oán, Nhàn Thần), 183-201 (Thuận/Phản/Chiến/Hợp cục, Quân/Thần/Mẫu/Tử), 229-233 (Tuế Vận) | `mined/ttt_pNNN.txt` (= PDF text layer, test-checked) |
| Thiệu Vĩ Hoa (TVH, scan) | pp.158-159 (con cái), 161-173 (phú/bần/quý/tiện, cát/hung theo dụng thần), 532, 546, 552-553 (quan, thi cử, danh) — transcriptions of 2026-10-23, spot-checked again against the page images (pp.158, 169, 553) | `mined/tvh_pNNN.txt` (already committed) |
| 八字真宗 (ZZ, text layer) | pp.26-30 (日干五行直断, 五行强旺弱缺, 七柱, 三字诀, 日月合化直断夫妻, 四柱干支合化), p.72 (羊刃 table, for schools.json) | `mined/zz_p26..30.txt`, `zz_p72.txt` |
| 穷通宝鉴 (CTBG, web) | zh.wikisource page 穷通宝鉴 rev. 2294674, 47 sections (all 40 stem×season sections) | `sources_web/qiongtongbaojian.json` (+ `index.json`) |
| 子平真詮 (TBCT, web) | **not saved**: zh.wikisource has no copy; ctext (子平真詮評注) blocks automated access and its terms forbid scraping — not worked around | `sources_web/zipingzhenquan.json` (empty, with the reason) |

Every judgement read is listed with its page, quote and a flag in `mined/rules_ttt_deep3.md`, `mined/rules_zz_26_30.md` (new) and
`mined/rules_148_173.md`, `mined/rules_519_556.md` (TVH, from 2026-10-23).

## 2. Counts per topic, before (main 743c094) and after

Verified rules of the kin packs (`pack_{zz,ttt,tvh}_kin.json`, fired by `tvbt.bazi_deep.kin` into `facts.bazi.deep.kin`):

| Topic | Before | After | New (TTT / TVH / ZZ) | Voiced by `bazi_kin.ts` today? |
|---|---|---|---|---|
| wealth | 66 | 83 | 1 / 15 / 1 | yes |
| rank | 39 | 72 | 1 / 32 / 0 | yes |
| work | 26 | 28 | 0 / 2 / 0 | yes |
| character | 4 | 14 | 2 / 2 / 6 | yes |
| marriage | 42 | 45 | 0 / 0 / 3 | yes |
| parents | 18 | 19 | 0 / 0 / 1 | yes |
| siblings, year | 20, 22 | 20, 22 | — | yes |
| **children** (new topic) | **0** | **11** | 2 / 9 / 0 | no — data only |
| **study** (new topic: học hành, thi cử) | 0 | 7 | 0 / 7 / 0 | no |
| **fortune** (new topic: cát / hung, thanh / trọc, chân thần by dụng-hỉ-kỵ) | 0 | 30 | 12 / 18 / 0 | no |
| **yong** (new topic: the dụng thần TTT Thể Dụng picks) | 0 | 10 | 10 / 0 / 0 | no |
| **total verified** | **237** | **361** | **28 / 85 / 11** | |

Plus 7 `draft` rules (ZZ, flag HARSH, §5) that never fire. Rules leaning on the TVH cách table's dụng / hỉ / kỵ (`hi: true`, said "nếu cách đứng được" like the earlier ones): 51 of the 124.

Dụng / hỉ / kỵ knowledge: before = 4 draft `yongshen` rules in `pack_structure.json` (unchanged); now `hyky.json` with 125 sourced
statements (roles, the TTT p.167 element map of hỉ / kỵ / cừu / nhàn — computable and test-reproduced —, the TTT p.63 dụng table, TVH
pp.170-173 cát / hung and phú / bần / quý / tiện tables, position of hỉ / kỵ, bệnh / dược, hợp / xung, luck principles) and the 40 `fortune` /
`yong` rules above. Children: 0 → 11 rules (no number, sex, birth timing or death of a child is voiced).

On the 1,000-chart corpus (`src/interpret/test/fixtures/corpus1000.json.gz`): 10.2 new findings per chart (fortune 2.68, rank 2.38, yong 1.29, study 1.28, children 0.98, wealth 0.96, character 0.43, work 0.17); the TTT Thể Dụng dụng thần agrees
with the TVH cách table's dụng list on 507 / 667 charts (76 %) where both give one. Never fired on the corpus: BT_ZZK_HZ3 (丙辛 化水 đúng phép:
rare), BT_TVHK_F21, BT_TVHK_CH14 (rare shapes), BT_TVHK_F25 (needs Quan Sát as dụng thần of a weak day master, which the TVH table never gives).

## 3. New files

Shapes of the three knowledge files follow the main session's request (2026-10-24) so `prose/bazi_deep.ts` reads them as-is:
`hyky.json` `{version, principles[{id, topic: dung|hy|ky|nhan|cuu, when{dm, group, role, relation}, text, book TTT|TVH|ZZ, page, quote,
reviewStatus}], role_map}`; `thanh_pha.json` `{version, cach[{cach (the 12 names of D.cach_tvh), thanh[], pha[], cuu[], reviewStatus}], general[],
tbct_draft}`; `schools.json` `{version, summary, topics[{id, topic, kind, sides[{school, statement, cite, quote, book, page|chapter}], engine}]}`.
Extra keys: result, rules, conditions, state, section (hyky); engine_id / engine_when (thanh_pha TVH items, linking tvh_thanhbai.json).
`tools/book_text.quote_on_page` checks TTT / TVH / ZZ quotes against `mined/` and `WEB:<id>` against `sources_web/`.

- `engine/data/bazi_deep/hyky.json` — dụng / hỉ / kỵ / cừu / nhàn thần logic with pages (§2).
- `engine/data/bazi_deep/thanh_pha.json` — cách thành / phá / cứu: per cách every TVH thành bại sentence of pp.367-369 (transcribed from the
  scan into `mined/tvh_p367-369.txt`, quoted, linked to the tvh_thanhbai.json encoding where one exists), TTT's own lines (Chính Quan cách, p.101), the general TTT principles (phá cách & cứu p.61, mộ khố xung pp.61-62, 70, thanh / trọc
  pp.101-103 with BT_TTTK_TR01-04, chân / giả thần pp.105-107 with BT_TTTK_CT01-02). The TBCT column keeps the `geju_defs.json` conditions as
  `draft` (no snapshot: §1) — **`geju_defs.json` is not replaced**.
- `engine/data/bazi_deep/schools.json` — 8 points of disagreement, each side with page / chapter: children star (TTT nguyên chú vs Nhâm thị
  pp.130-132), thân vượng Ấn vượng (TVH p.527 vs p.553 vs p.173), Quan as dụng thần (TVH p.167 vs p.173, TTT p.143), the 刃 table of the yin
  stems (ZZ p.28 vs p.72), Tài nhiều thân nhược (TTT p.191 vs TVH p.522), kiêu đoạt thực (TVH p.527 vs TTT p.63), dụng thần choice (TVH cách
  table vs TTT Thể Dụng), and điều hậu TVH vs 穷通宝鉴 (cell list).
- `engine/data/sources_web/` — snapshots + `index.json`; `tools/book_text.quote_on_page('WEB:<id>', chapter, quote)` and
  `tools/show_page.py WEB:CTBG <chapter> [--check "..."]`.
- `dieu_hau_ctbg_draft.json` — gained `snapshot` (120 cells read from 穷通宝鉴, each with chapter + quote; 109 from the month's own paragraph,
  11 from the season statement where the month has none: `from_season`), `checked_cells` (63 cells where the memory draft equals the text's
  ordered stems) and `disagreements`. Against TVH: the stem set differs from the TVH table in 53 cells, the first (chủ) stem differs from TVH's
  notes order in 13; the memory draft differs from the text in 50. The engine still takes the set from TVH and the order from TVH's notes;
  `cells` (memory) are untouched and remain the fallback order only.
- `tools/build_bazi_deep3_pack.py` (patches the three kin packs in place: replaces only the rules it owns, refuses to overwrite an older id),
  `tools/build_bazi_deep3_knowledge.py` (hyky / thanh_pha / schools).
- `engine/tvbt/bazi_deep/kin.py` `_deep3_facts`: positions only — day stem, hour stem / branch god, hour 刃, transparent gods, absent elements,
  groups next to the day master, where the cách table's dụng / hỉ / kỵ stand (near the day master, kỵ next to dụng, dụng weak, dụng holding the
  month attacked by a neighbour), and ZZ p.28-29 stem combinations (正化, 妒合, 鸳鸯合, 日月合化 优/劣).
- Tests: `engine/tests/test_bazi_deep3_mining.py` (every knowledge-file quote on its page / chapter; rule ids exist; p.167 role map reproduces the
  page's example; TTT pp.101-106 examples #188, #195, #196 fire CT01 / CT02 as the commentary says (chân thần; "có bệnh"; "giả loạn chân"); ZZ p.29
  examples 月辛巳日丙午 → 优 and 月戊子日癸酉 → 劣; 正化 / 妒合 / 鸳鸯合 charts; HARSH never fires; opposite
  judgements on one condition never fire together; CTBG cell quotes in the snapshot). `test_bazi_deep_kin.py` and `test_bazi_deep_dieuhau.py`
  adjusted for the new topics, the draft HARSH rules and the checked cells.

## 4. Choices that are the system's, not a page's

- 'vượng / nhiều / nặng', 'nhược / khinh / nhẹ' of a group: 25 % / 12 % of TVH degrees (as DEEP-BAZI-2); 'khinh' additionally requires the
  group present. 'Đứng sát / kề': same pillar or same row of neighbouring pillars. 'Kề nhật chủ': day branch, month stem, hour stem (ZZ p.50).
- CT02 checks only the 'kề sát … tương khắc' clause (a node of the group that controls the dụng group next to the month branch).
- ZZ 日月合化: '两干坐支与日干比和' read as "the element or a producer of it" (p.29 example 2 counts 酉 under 癸); man = yang day stem,
  woman = yin day stem (condition 5); 刃 from the p.28 table of that section. 鸳鸯合 '互相引化': the two transformed elements equal or producing
  each other; 午未 counts as Hỏa or Thổ. 正化 requires the two stems on neighbouring pillars.
- Narrowed against breadth or a same-condition contradiction: BT_TVHK_F15 (Quan dụng thần must be not weak and Tài present), D03 (Chính Quan
  transparent), D04 (Ấn not weak), D09 (only when Ấn is not kỵ: TVH p.173 says the opposite for Ấn kỵ — schools.json).

## 5. Skipped entries and why

### Trích Thiên Tủy (all in `mined/rules_ttt_deep3.md` with the flag)
- SENSITIVE (kept out): p.77 "tài khinh kiếp trọng không có vợ", "chế cường sát nhược không có con"; p.103 "nhật chủ khô … không bần cũng yểu";
  p.130 eleven judgements on the number / sex of children (and the number half of "con nhiều mà hiền", voiced only as "hiền"); p.132 counting
  children, birth timing by dụng thần; pp.145-148 thọ / yểu (lifespan).
- SUPERSEDED: p.130 nguyên chú "hỉ thần là Quan tinh, con cái hiền tài" (Nhâm thị rejects Quan as the children star on the same page; it would
  fire on ~45 % of charts) → schools.json.
- VAGUE (no fact can decide it): p.61 phá cách verdict (needs the cách broken / not, not a kin fact); p.63 "cân bằng" rows (T09, T10 in hyky);
  p.67 môn / địa (needs tư lệnh by day); p.77 'trung hòa'; p.103 'dụng thần khô'; p.107 giả thần đắc cục; p.161 dương trong âm ngoài; p.163
  thuần dương / thuần âm; p.185 tòng nhi + Tài (kin does not know the tòng verdict); p.194 'hợp nhiều'.
- LUCK (needs luck × year facts the kin layer does not compute): p.61, 101, 103, 144, 163 luck clauses; pp.229-233 chiến / xung / hòa / hảo of a
  luck pillar against a year — kept as data in hyky.json `luck_year` / `luck_principles`.
- DUP: p.67 tư lệnh Dần (tu_lenh.json), p.72 tòng cường (tong_roles.json), pp.229-230 cái đầu / tiệt cước and thiên khắc địa xung
  (pack_temporal.json), p.191 Tài đa thân nhược (BT_TVHK_G03).
- METHOD (principles, no chart verdict): 50 statements → hyky.json / thanh_pha.json.

### Thiệu Vĩ Hoa (rows flagged usable in the 2026-10-23 lists, on the DEEP-3 pages, not packed)
- Thần sát conditions (policy of DEEP-BAZI-2): p.158 thiên / nguyệt đức; p.159 quý nhân, trạch mã; p.546 quý địa + lộc mã, lộc; p.552 lộc
  (×3), dịch mã, tam kì (ất bính đinh), hai đức; p.553 lộc mã (×3), quý (×2), đức.
- Court / military titles (policy): p.532 "cực quý, là tướng", "vương hầu", "trấn thủ một vùng", "quan đài các", "nắm binh quyền", "lương thần",
  "bậc tướng" (×2), "thống lĩnh các tướng", "tướng có tài", "uy trấn biên cương", "quan cao trong triều", "quan trong nội các", "quan chức cao" (lộc hợp).
- Luck / timing: p.159 cuối vận × cung con (3 rows); p.162 dụng thần phát huy (→ hyky `timing`); p.165 vận thực thương gặp năm tài (2 rows);
  p.166 gặp vận ấn thụ, vận tỉ kiếp; p.169 vận ấn, tỉ kiếp đỡ; p.173 đại vận × lưu niên (→ hyky `timing`).
- Needs "dụng thần bị khắc / hợp / xung" (no such fact): p.164 "giàu nhất", p.165 "hỉ thần Tài … mới sinh quan", p.166 (2 rows), p.167
  "Quan dụng thần có lực, không bị khắc…", p.168 "dụng thần Ấn … không bị hợp, khắc, xung"; p.170-171 general cát / hung rows (→ hyky tables).
- Needs a count of a branch / position the facts lack: p.546 "kình dương nhiều", p.552 "kình dương nhiều" (×2), "tháng kình dương, ngày …",
  "trụ tháng gặp sát đồng thời với kình dương", "dần thân tị hợi nhiều", "mậu kỉ gặp bốn mùa", "quan hoặc thất sát sinh cho năm", "tài kho ở
  đất sinh vượng", p.553 "trụ giờ gặp một ngôi thiên quan", "năm tháng ngày giờ cùng một tuần", "mã tinh sinh tài", p.159 "mộ, tuyệt" of the
  children star, "đóng đúng bản cung" (method).
- DUP of a packed rule: p.164 "Thân vượng, tài có thể làm dụng thần" (BT_TVHK_W03 p.520), p.166 "Tỉ kiếp nhiều gánh được tài" (W08), p.166
  "Thân nhược, tài mạnh" (G02 / G03 / W11), p.168 "Thân vượng, sát mạnh, thực thần có lực" (PT_TCS1 p.535), p.171 "Tỉ kiếp nặng: ấn và kiếp đều
  nặng" (same condition as CH16), p.173 "Giàu: … tài tinh là dụng thần" (W03), p.552 "Thân vượng gặp quan" (HT02 p.546), p.552 "Ấn tàng, tài lộ"
  (D06 p.553), p.165 "Mệnh không có tài là mệnh nghèo" (G09 / W14 / G11 on the same condition).
- Breadth (holds for most charts, says nothing chart-specific): p.553 "Mệnh gặp ấn thụ là phúc rất dày", p.161 / p.165 general laws (→ hyky).
- Contradiction / misprint: p.173 "Sang: nhật chủ nhược, quan sát là dụng thần" (vs p.167; → schools.json); p.171 "Sát nặng: thân nhược kị
  sát lại còn gặp tài nhiều" (kept out: same shape as F06 / F27 already voiced); p.553 "Trụ ngày lộ thương quan" (the day stem is the day master:
  unreadable as printed).
- VAGUE: p.546 "Quan tinh không bị phá hại" (which damage), p.553 "Ấn ẩn" kept (D06), "Tài ít bị thương kiếp" (VAGUE in the list).

### 八字真宗 (all in `mined/rules_zz_26_30.md`)
- DUP: p.26 日干五行直断 (10 day-stem lines) is already the base pack `data/pack_bazi_zhenzong.json`, voiced in the portrait — not packed again.
- HARSH → packed as `draft`, never fire, **owner decision needed**: p.26-27 五行缺 rows (木 吝啬小气, 火 软弱消极, 土 无情无义, 金 无礼无义,
  水 智力不高), p.29 戊癸 正化 "薄情寡义", p.29 女命劣型 "母老虎，欺夫骂翁".
- SENSITIVE: p.26 胎记 (body marks), p.27 水太旺 "飘荡贪淫", p.28 三字诀 / 四字诀 (death, loneliness, lawsuits, spouse loss), p.29 争合
  (affairs), 鸳鸯合 日时 "体健寿长", p.30 闸合局 (death before an age); the 长命多寿 half of 丁壬 正化.
- VAGUE: 太旺 / 旺 / 弱 / 中和 rows of pp.26-27 (得令 / 得位 / 得生 as one verdict is not computed; a share threshold would be a system measure on a
  character verdict).
- METHOD / DUP: 七柱推柱法 (already in kin: thai / mệnh / thân cung), 纳音 (computed elsewhere).

## 6. Not done / open

- 子平真詮 is not in the repository: no public-domain snapshot was reachable within policy (wikisource none, ctext blocked). `geju_defs.json`
  stays memory-written `draft`; `thanh_pha.json` marks its TBCT column draft. Needs either a ctext API key, a manual export of the chapters by the
  owner, or another public-domain host the owner accepts.
- The four new topics (children, study, fortune, yong) reach `facts.bazi.deep.kin.findings` but are not voiced; `bazi_kin.ts` voices the new
  wealth / rank / work / character / marriage / parents rules automatically (goldens updated, §7).
- The TTT p.167 role map (cừu / nhàn thần) is data; the engine still takes hỉ / kỵ from the TVH cách table.
- Luck × year (TTT pp.229-233 chiến / xung / hòa / hảo) and the "dụng thần bị khắc / hợp / xung" family need new facts.
- HARSH rules: owner to decide whether any of them may be voiced (softened) or should be removed.

## 7. Verification

- `cd engine && pytest` — see the commit message for the run on this branch.
- `node --test src/interpret/test/*.test.ts`, goldens re-written with `UPDATE_GOLDEN=1` after reading the diff (only the Bát Tự kin lines move).
