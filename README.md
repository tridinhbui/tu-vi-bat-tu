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
- **Disputed between sources**: Tứ Hóa Tân-Lộc (Thực Hành: Cự Môn; Khảo Luận: Thiên Cơ → Cự Môn used) and Nhâm-Khoa
  (Thực Hành prints "Phủ", Khảo Luận says Tả Phụ → Tả Phụ used). The Thực Hành printed Hồng Loan example and Thiên Mã "cước" contradict its own rules (rules used).
- **Still unverified**: Bát Tự hidden stems and ten-god table (not cell-checked), đại hạn details, leap-month rule (convention), VN lunar calendar (UTC+7)
  vs an official almanac, all interpretation rules (the rule pack is draft; no book *interpretation* has been encoded yet).
- **Interpretation rules encoded so far** (`engine/data/pack_khao_luan.json`, all paraphrased with page cites, source Tử Vi Khảo Luận pp.50-51, 166-167):
  star-group classification (verified, structural) and 6 hedged Mệnh-palace readings (4 verified, 2 draft because they need our own operationalisation of
  'cát tinh'/'gặp sát'). Harm-prediction aphorisms (prison, suicide, early death) are deliberately skipped.
- Not supported: miếu/hãm brightness, minor stars (Thiên Hình, Riêu, Y, Đức…), tiểu hạn, Bát Tự thai nguyên/mệnh cung, lunar-date input.
- Books received but not yet used: Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục), 方術紀異 (Vương Đình Chi). Fortune-telling claims in the books
  (injury, death, children) are intentionally not implemented.

## Deploy
Python service (FastAPI also serves the UI). Cloudflare: `wrangler.jsonc` + `src/index.ts` route all requests to a Cloudflare Container built from `Dockerfile` (requires Workers Paid). Alternative: `render.yaml` (Render).
