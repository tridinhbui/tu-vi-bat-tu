# tu-vi-bat-tu

Deterministic Tử Vi Đẩu Số & Bát Tự engine. **No LLM**: calendar/astronomy + rule data + (later) inference graph.
This is a research tool for a traditional symbolic system, not scientific evidence of fate.

## Phase 1 — Correctness Foundation (this commit)
`engine/tvbt/`: `astro` (solar terms via sxtwl, new moons via PyEphem) · `lunar_vn` (lunisolar rules at any UTC offset)
· `calendar_core` (IANA tz, DST gap/ambiguity, true solar time, Zi-hour rule) · `bazi` · `tuvi` · `trace`.
Every value is emitted with a `CalculationTrace`. Output = **facts only**; interpretation starts in Phase 3.

```bash
python3 -m venv .venv && .venv/bin/pip install -e "engine[dev]"
cd engine && ../.venv/bin/python -m pytest -q
../.venv/bin/python -m tvbt.cli 1990-05-17 10:30 --gender male --lon 106.7
```

## Honest status
- **Checked against books** (page-cited in `engine/data/sources.json`, golden tests in `engine/tests/test_book_golden.py` and
  `test_bazi_book_golden.py`): Tử Vi — Mệnh/Thân, cục table, Tử Vi/Thiên Phủ groups, Khôi Việt, Tả Hữu, Xương Khúc, Lộc Tồn/Kình/Đà,
  Bác Sĩ/Thái Tuế/Trường Sinh rings, Hồng Loan/Thiên Hỷ, Đào Hoa, Thiên Mã, Hỏa/Linh, Địa Kiếp/Không, Tuần/Triệt, Tứ Hóa (see dispute below);
  Bát Tự — ngũ hổ/ngũ thử độn, 12 stages (yin reverse), stem/branch relations, luck-start rule, month by jie.
  Checking found and fixed 4 real bugs (Khôi Việt for Canh, Linh Tinh direction, Đào Hoa mapping, Tứ Hóa Canh).
- Tứ Hóa disputes resolved: Khảo Luận's own prose (pp.196-197) agrees with Thực Hành (Tân-Lộc = Cự Môn, Nhâm-Khoa = Tả Phụ); only its p.36 table misprints. Tứ Hóa meanings and per-star advice are now in the analysis (`data/tu_hoa_vi.json`). The Thực Hành printed Hồng Loan example and Thiên Mã "cước" contradict its own rules (rules used).
- Since then verified: Bát Tự hidden stems + ten-god tables (八字真宗 pp.7-17), đại hạn and tiểu hạn rules (Thực Hành p.27), leap-month default = same month
  number (Khảo Luận p.41; other conventions selectable).
- VN lunar calendar: UTC+7 since 1968 (North/unified) is consistent with Wikipedia's Vietnamese-calendar article (1984-85 month-11 divergence reproduced); the 1967/68
  switch date differs between sources (VASTI vs Wikipedia) and the South (`vn_south`, UTC+8 to 1975) is unverified. No official almanac comparison yet.
- **Still unverified**: all interpretation rules (the rule pack is draft; no book *interpretation* has been encoded yet).
- **Interpretation rules encoded so far** (`engine/data/pack_khao_luan.json`, all paraphrased with page cites, source Tử Vi Khảo Luận pp.50-51, 166-167):
  star-group classification (verified, structural) and 6 hedged Mệnh-palace readings (4 verified, 2 draft because they need our own operationalisation of
  'cát tinh'/'gặp sát'). Harm-prediction aphorisms (prison, suicide, early death) are deliberately skipped.
- **Star brightness** (miếu/vượng/đắc/bình/hãm) for the 14 chính tinh is now transcribed from Tử Vi Thực Hành pp.29-48
  (`engine/data/dignity_vn.json`); unlisted branches stay *unspecified* (Vũ Khúc and Thái Dương have gaps). Disputed: Tham Lang Tý/Ngọ vs Khảo Luận.
  22 dignity-gated Mệnh temperament rules (`pack_thuc_hanh.json`, verified) and 25 Bát Tự rules from 八字真宗 (`pack_bazi_zhenzong.json`:
  10 day-master tables ×2 verified, 5 missing-element rules draft). Generator: `tools/build_packs.py`. Manual's 强旺弱中和 element states are NOT
  implemented (the book gives no computable thresholds).
- **Two brightness schools** are kept apart: Thực Hành (default, from page images) and Toàn Thư/Vũ Tài Lục (PDF text layer, not yet cross-read);
  they disagree on dozens of cells (`/api/dignity/compare`). `dignity_school` selects one; with `toan_thu` the Thực Hành-based temperament rules are
  downgraded to draft (mixed schools are not verified). 15 verse-aphorism rules for Mệnh/Tài Bạch/Thiên Di/Tử Tức (`pack_thuc_hanh_palaces.json`).
- **Rule library & tester**: `/library` (read-only list of rules, sources, brightness disagreement) and `POST /api/rules/test` (stateless validate + dry-run;
  nothing stored, no code executed). Publishing a rule = committing it to a pack file.
- **Structure analysis** (`engine/tvbt/analysis.py`, `POST /api/analysis`): per-chapter layered prose (Tượng/Khí/Thế/Cách/Biến/Phản/Tổng) built from the computed charts,
  each block tagged tính toán / theo sách (with page) / định nghĩa hệ thống. 31 more star-combination rules (`pack_thuc_hanh_combos.json`), tiểu hạn and lưu nguyệt (Bát Tự) in the year view.
- Rule inventory now ~230: Khảo Luận phú đoán (pp.49-73) 69 rules (`pack_khao_luan_phu*.json`), Thực Hành dignity 22 + combos 31 + verse 15, 八字真宗 25, group rules 12.
  Where two passages disagree on strength (e.g. Hóa Lộc vs Tứ Mộ, Tử Phủ vs Tuần/Triệt) the resolver shows the documented limiter; two books agreeing
  (Mệnh + Tuần/Triệt) appear as two supporting rules for one claim.
- Palace summary rules (`pack_khao_luan_cung.json`, 48) from Khảo Luận pp.214-220 for Tài Bạch, Quan Lộc, Phúc Đức, Phu Thê, Tử Tức, Tật Ách, Thiên Di, Nô Bộc, Điền Trạch,
  Phụ Mẫu and the Mệnh 'giáp' (neighbour) readings; palace definitions in the analysis now cite the same pages. A typical chart now yields ~15-20 Tử Vi findings.
- Khảo Luận pp.220-224 (what each star/pair means at Mệnh, incl. Đào Hồng by branch): 57 rules in `pack_khao_luan_chinh_tinh.json`; chart-level fact `chart.tu_vi_branch` gates the
  vô-chính-diệu readings. Total rule inventory ~340.
- 八字真宗 pp.31-32: day-pillar nạp âm personality readings (30 rules, `pack_bazi_napam.json`); the book's own pillar→nạp âm list validates our nạp âm table for all 30 rows.
- Bát Tự thai nguyên, mệnh cung, thân cung and 空亡 now computed (`BaziChart.extras`); the book's full 命宫 and 身宫 tables (144 cells each), 胎元 and 空亡 tables are golden tests.
- Thần sát tables (八字真宗 pp.21-22) and Khảo Luận's five-step đại hạn method (pp.230-233: tam hợp element vs birth year, xung chiếu, nhị hợp, Thái Tuế triad) are in the analysis;
  the five worked examples of the book are tests. The analysis chapter list now also has a 12-palace walk-through (~70 blocks per chart).
- Vận reading (`tvbt/van_han.py`, Khảo Luận pp.233-236): how Mệnh meets the đại hạn / tiểu hạn palace (Tử Phủ Vũ Tướng vs sát tinh, vô chính diệu vs Sát Phá Tham, Tuần↔Triệt,
  Nhật Nguyệt vs Đào Hồng Hỷ…, Thái Tuế/Quan Phù/Bạch Hổ vận, Sát/Phá/Tham by position, life-stage labels); lưu niên Tứ Hóa advice from pp.195-197. Opposite conditions that both match are shown as unresolved.
- Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục) pp.21-28: 68 rules (`pack_toan_thu.json`: major stars through Phá Quân, plus Xương Khúc, Tả Hữu, Khôi Việt, Lộc Tồn, Lộc Mã, Tứ Hóa, Kình, Hỏa Linh). Auxiliary-star brightness for 24 phụ tinh (Thực Hành, Toàn Thư and Khảo Luận, cell by cell, disputed cells kept experimental) is in `dignity_aux.json`, built by `tools/build_aux_dignity.py` (see `docs/AUX-DIGNITY.md`); where the claim equals one from Khảo Luận the API merges them into one card that lists the second book as corroboration. New chart fact `chart.year_stem` gates year-stem conditions.
- Not supported: minor-star brightness, minor stars (Thiên Hình, Riêu, Y, Đức…), tiểu hạn, lunar-date input.
- Books received but not yet used: Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục), 方術紀異 (Vương Đình Chi). Fortune-telling claims in the books
  (injury, death, children) are intentionally not implemented.

## Deploy
Python service (FastAPI also serves the UI). Cloudflare: `wrangler.jsonc` + `src/index.ts` route all requests to a Cloudflare Container built from `Dockerfile` (requires Workers Paid). Alternative: `render.yaml` (Render).
- Tử Vi Thực Hành pp.50-117 now fully read (page images, not the broken text layer): 43 auxiliary-star rules (`pack_thuc_hanh_aux.json`), 55 on sát tinh / Lục Bại / Không Kiếp / Trường Sinh and Thái Tuế rings (`pack_thuc_hanh_aux2.json`), 64 named cách-cục with sinh-vượng-bại-tuyệt, season and hour of birth (`pack_thuc_hanh_cach.json`), 45 Mệnh verse/career rules (`pack_thuc_hanh_menh_verse.json`), 53 per-star Nam/Nữ readings by brightness (`pack_thuc_hanh_star_menh.json`) and 134 palace-verse rules for Huynh Đệ, Phu Thê, Tử Tức, Tài, Di, Nô, Quan, Điền, Phúc, Phụ Mẫu and Nữ mệnh (`pack_thuc_hanh_palaces2.json`). pp.115-117 đại tiểu hạn phát/thất lợi patterns are in the vận readings. Total ~810 rules (676 verified, 136 draft). Chart facts added: `chart.gender`, `chart.menh_element`, `chart.menh_stage_th`, `chart.birth_season`, `chart.season_relation`, `chart.hour_matches_season`, `chart.hour_menh_polarity`.
- Deliberately NOT encoded from those pages: Giải Ách (illness), death/injury/prison/accident lines, child-survival counts, sexual-reputation lines, and every line that depends on the unverified auxiliary stars (Long Phượng, Hoa Cái, Thiên Hình, Thiên Riêu, Khốc Hư, Quan Phúc, Quốc Ấn, Cô Quả...). Page 79-81 verses of brightness per branch disagree with the pp.29-48 tables and were not used.
- 八字真宗 pp.39-42: lưu niên thập nhị thần (`tvbt/bazi_twelve.py`, `POST /api/twelve-gods`): numbering and 天干寄支 table are golden-tested against the book's p.41 table. The pairing with auspicious stars and 盖头 is NOT evaluated. Still not encoded from that book: pp.43-96 (lưu niên case studies, wealth/job/children direct-judgement lists, which need new facts such as 截脚, 流入日主, star transparency).

## Beginner experience (UI)
- Result pages open in **Dễ hiểu** mode (plain-language summary, verified readings only, hard/one-sided traits folded, no rule ids); **Chuyên sâu** shows the full provenance (rule ids, sources, inference trace, drafts). The choice is remembered in `localStorage`.
- Interactive glossary: any `[data-gl]` element opens a short explanation. Data = `engine/data/glossary_vi.json` (hand-written, educational only) + `star_profiles.json`, built into `engine/web/js/glossary.json` by `python tools/build_glossary.py` (`tests/test_beginner_ux.py` fails if it is stale).
- Learning journey (`#hoc`, lessons in `engine/web/js/learn.js`) and the summary/filter logic (`engine/web/js/beginner.js`) are static JS: no LLM, no new API.
- Tử Vi Khảo Luận pp.63-83: 103 rules (`pack_khao_luan_stars.json`: Lộc, Tả Hữu, Kình Đà, Hỏa Linh, Không Kiếp, Tứ Hóa, Lục Bại phú; Tử Vi, Thiên Cơ, Thái Dương by position and palace). pp.237-246: 24 chart-level principles (`pack_khao_luan_cases.json`) and **five of the book's worked example charts are golden tests** (`tests/test_book_examples.py`: Hán Cao Tổ, Hạng Võ, Khổng Minh, a female Quý Mão chart, a Mậu Tý chart): all twelve palaces' major stars, the four Tứ Hóa carriers and the legible Tả Hữu / Xương Khúc / Khôi Việt / Không Kiếp / Hỏa Linh / Lộc Tồn placements equal the printed charts (Hán Cao Tổ's hour is recovered uniquely as Ngọ). New chart facts: `chart.can_chi_relation`, `chart.menh_dac_chinh`, `chart.am_duong_ly`. `tvbt/cuu_dieu.py` implements the pp.271-272 sao chiếu mạng table (golden-tested on the book's four examples); it is not yet wired into an API endpoint.
- Not encoded from Khảo Luận pp.249-290: the nạp âm marriage-compatibility essays (pp.248-260, which the author himself cautions against over-using), age/calendar tricks and day selection (pp.261-270), the bát hạn list (no table printed), the philosophical essays (pp.274-280, 286-290) and the star-keyword lists of pp.281-283.
- Tử Vi Đẩu Số Toàn Thư pp.77-165: 382 'có sao X' palace readings for Thiên Di, Quan Lộc, Tài Bạch, Phu Thê, Phúc Đức, Phụ Mẫu, Nô Bộc, Điền Trạch (`pack_toan_thu_palaces.json`, generated from the reviewed text table `tools/data/toan_thu_palace_star.txt`), 57 numbered-phú rules not already held elsewhere (`pack_toan_thu_phu.json`) and 11 positive nữ-mệnh readings (`pack_toan_thu_nu.json`). `tvbt/van_han_tt.py` turns the 'nhập hạn ca' of pp.97-105 into vận-palace sentences (standalone: not yet called from `van_han.read`, which is being reworked as data). Rule inventory ~1,700. Not encoded: Tật Ách and the khắc-phu/khắc-tử, death, prison and adultery lines; pp.53-62 (auxiliary stars whose placement is unverified), pp.63-76 (per-star Mệnh poems that largely repeat pp.21-52), pp.121-146 (ngũ hành essays and sample chart readings).
- 八字真宗 pp.51-58 direct judgement: 26 rules (`pack_bazi_zz_direct.json`): occupation by the hour pillar (ten-god group of the hour stem, the stem's trades) and marriage by the month branch / day branch (ten god of its 本气, 刑冲穿害, 合, 空亡). The facts live behind `facts.bazi_facts(chart, zz=True)` so the frozen old-pipeline baseline is untouched; `api.py` call sites were switched to `zz=True` in the working tree but that file also carries another session's uncommitted work, so until it is committed these rules stay pending in the API. Not encoded from pp.43-96: officialdom/prison, parents' lifespan, illness, wealth and education lists (they need 透干/通根/截脚/流入日主 facts), second-marriage and infidelity lines, and the case studies.
- 八字真宗 pp.60-96 (partial): 12 more direct-judgement rules, 49 in total: 羊刃 (table p.72; many blades, blade in thai/thân/mệnh, blade combined, 刃-杀-印 together), 驿马 (by day branch: in chart, at hour pillar, void, clashed, combined), 文昌 by year stem, and sibling hints from the month stem/branch. Skipped on purpose because they are folk-calamity or death/illness lore: 关煞 of children, 天罗地网, 黄泉煞, 追魂煞, 阴箭, parents'/own lifespan tables, 桃花 readings, the 作法/cúng pages (pp.88-96) and divination imagery.
