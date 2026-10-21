"""Fixture for src/interpret/test/indices.test.ts: the tiểu hạn and lưu Thái Tuế palace of 2016-2036 for each benchmark20 chart, as the
Python engine computes them (temporal.tuvi_year). The TS indices derive the other years from the viewed year's; this pins them to Python.
    .venv/bin/python tools/interpret/tieu_han_years.py   (from the repo root)"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engine"))
from tvbt import temporal  # noqa: E402
from tvbt.api import BirthReq, _compute  # noqa: E402

FX = ROOT / "src" / "interpret" / "test" / "fixtures"
out = {}
for x in json.loads((FX / "benchmark20.json").read_text("utf-8")):
    _, _, tv = _compute(BirthReq(**{k: v for k, v in x["birth"].items() if k != "to_year"}))
    out[x["label"]] = {y: [(t := temporal.tuvi_year(tv, y))["tieu_han_palace"], t["luu_thai_tue_palace"]] for y in range(2016, 2037)}
(FX / "tieu_han_years.json").write_text(json.dumps(out, ensure_ascii=False) + "\n", "utf-8")
