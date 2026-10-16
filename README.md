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
- Verified: lunar converter equals sxtwl 1900–2049 at UTC+8 except 4 explained windows; nạp âm method vs named table;
  hand-derived pillar/Tử Vi anchors in `engine/tests`.
- **Unverified** (`review_status: unverified`): every Tử Vi star-placement table (Khôi/Việt, Hỏa/Linh direction,
  Tứ Hóa Canh, Tuần/Triệt, Trường Sinh start, leap-month rule) is from the common Vietnamese procedure and still
  needs checking against a cited edition. The VN lunar calendar (UTC+7) is not yet compared with an official almanac.
- Not supported yet: miếu/hãm brightness, minor stars (Thiên Hình, Riêu, Y, Đức…), tiểu hạn, lưu niên,
  lunar-date input, uncertain-birth-hour comparison, true solar time uses NOAA EOT (not JPL).
- Phase 2 foundation (rule DSL, validator, draft pack) and Phase 3 engine (facts, forward chaining, provenance graph, conflict resolver) are in; all rules remain draft. Phase 4 NLG (deterministic, 5 depth levels, per-sentence provenance) is in. Phase 5 (temporal facts, chart comparison, cross-system comparison layer) is in. Next: Phase 6 (web UI, explorer, rule editor) — not started.
