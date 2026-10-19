"""Parity fixtures for CONFLICT star-dignity cells (engine/data/dignity_kb.json): Toàn Thư charts chosen so that every Toàn Thư CONFLICT cell
(star, branch) occurs at least once, with the facts /api/facts returns and the Python engine's fired findings. The regression and sweep
fixtures are Thực Hành charts and almost never meet a CONFLICT cell; here the rule evaluator's three-valued reading of the alternatives
(knowledge/dsl.py ALT, src/interpret/dsl.ts) is exercised on whole charts. Run after any rule-pack, fact or knowledge-base change:
    .venv/bin/python tools/interpret/make_conflict_fixtures.py"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engine"))
from fastapi.testclient import TestClient  # noqa: E402

from tvbt import dignity  # noqa: E402
from tvbt.api import app  # noqa: E402
from tvbt.knowledge.loader import load_all  # noqa: E402
from tvbt.reasoning import engine  # noqa: E402

SCHOOL = "toan_thu"


def main():
    client = TestClient(app)
    rules, sources = load_all()
    todo = {(s, b) for s, row in dignity.kb()["resolved"][SCHOOL].items() for b, r in row.items() if r["status"] == "CONFLICT"}
    out, rnd = [], random.Random(20261018)
    for _ in range(6000):
        if not todo:
            break
        body = {"year": rnd.randint(1940, 2015), "month": rnd.randint(1, 12), "day": rnd.randint(1, 28), "hour": rnd.randint(0, 23), "minute": 15,
                "gender": rnd.choice(["male", "female"]), "to_year": 2026, "dignity_school": SCHOOL}
        f = client.post("/api/facts", json=body).json()
        hit = {(s, p["branch"]) for p in f["palaces"] for s in p["stars"]} & todo
        if not hit:
            continue
        todo -= hit
        res = engine.run(rules, sources, f["base"], system="tu_vi")
        fired = sorted({(x.rule_id, x.subject, x.claim, x.effect, x.basis) for x in res.findings})
        out.append({"label": ", ".join(f"{s} tại {b}" for s, b in sorted(hit)), "birth": body, "facts": {k: f[k] for k in ("dignity_school", "palaces", "base")},
                    "python_fired": [list(x) for x in fired]})
    if todo:
        print("never placed:", sorted(todo))
    dst = ROOT / "src" / "interpret" / "test" / "fixtures" / "conflicts.json"
    dst.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), "utf-8")
    print(dst, dst.stat().st_size, "bytes,", len(out), "charts")


if __name__ == "__main__":
    main()
