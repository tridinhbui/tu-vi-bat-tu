"""Regression fixtures for the TypeScript interpretation pipeline: chart facts exactly as /api/facts returns them, plus the Python rule
engine's fired findings for the same chart (the TS engine must reproduce them exactly). Run after any rule-pack or fact change:
    .venv/bin/python tools/interpret/make_fixtures.py"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engine"))
from fastapi.testclient import TestClient  # noqa: E402

from tvbt.api import app  # noqa: E402
from tvbt.knowledge.loader import load_all  # noqa: E402
from tvbt.reasoning import engine  # noqa: E402

CHARTS = [{"year": 1990, "month": 5, "day": 17, "hour": 10, "minute": 30, "gender": "male", "to_year": 2026, "label": "regression 17/05/1990"},
          {"year": 2001, "month": 3, "day": 10, "hour": 10, "minute": 30, "gender": "male", "to_year": 2026, "label": "Cự Môn hãm hóa Lộc"},
          {"year": 2002, "month": 1, "day": 9, "hour": 8, "minute": 0, "gender": "female", "to_year": 2026, "label": "review 09/01/2002"}]
rnd = random.Random(20261018)
for _ in range(5):
    CHARTS.append({"year": rnd.randint(1945, 2025), "month": rnd.randint(1, 12), "day": rnd.randint(1, 28), "hour": rnd.randint(0, 23), "minute": 15,
                   "gender": rnd.choice(["male", "female"]), "to_year": 2026, "label": "random"})


def main():
    client = TestClient(app)
    rules, sources = load_all()
    out = []
    for c in CHARTS:
        body = {k: v for k, v in c.items() if k != "label"}
        f = client.post("/api/facts", json=body).json()
        res = engine.run(rules, sources, f["base"], system="tu_vi")
        fired = sorted({(x.rule_id, x.subject, x.claim, x.effect, x.basis) for x in res.findings})
        out.append({"label": c["label"], "birth": body, "facts": f, "python_fired": [list(x) for x in fired]})
    dst = ROOT / "src" / "interpret" / "test" / "fixtures" / "charts.json"
    dst.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), "utf-8")
    print(dst, dst.stat().st_size, "bytes,", len(out), "charts")


if __name__ == "__main__":
    main()
