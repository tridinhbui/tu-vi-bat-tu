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
- Not supported: minor-star brightness, minor stars (Thiên Hình, Riêu, Y, Đức…), tiểu hạn, lunar-date input.
- Books received but not yet used: Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục), 方術紀異 (Vương Đình Chi). Fortune-telling claims in the books
  (injury, death, children) are intentionally not implemented.

## Deploy
Python service (FastAPI also serves the UI). Cloudflare: `wrangler.jsonc` + `src/index.ts` route all requests to a Cloudflare Container built from `Dockerfile` (requires Workers Paid). Alternative: `render.yaml` (Render).
