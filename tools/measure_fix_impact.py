#!/usr/bin/env python3
"""How often does each audited rule currently fire on a random chart? (= how many charts a fix would change)

Runs the real API on N random births (seeded) and records, per rule id of tools/data/fix_classes.json, the share of charts where the rule
produces a supported/limited finding. Tử Vi rules via /api/reasoning, Bát Tự rules via /api/bazi-structure (default flags: the 八字真宗
direct rules are not active there, so they read 0%).  Writes docs/source_audit_fix_impact.json."""
import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from fastapi.testclient import TestClient  # noqa: E402
from tvbt.api import app  # noqa: E402

SEED, N = 20261018, int(sys.argv[1]) if len(sys.argv) > 1 else 300


def ids_in(x, out):
    if isinstance(x, dict):
        if isinstance(x.get("rule_id"), str) and x.get("status") in ("supported", "limited"):
            out.add(x["rule_id"])
        for v in x.values():
            ids_in(v, out)
    elif isinstance(x, list):
        for v in x:
            ids_in(v, out)


def main():
    cls = {k: v for k, v in json.load(open(os.path.join(ROOT, "tools", "data", "fix_classes.json"), encoding="utf-8")).items() if not k.startswith("_")}
    c = TestClient(app)
    random.seed(SEED)
    hits = {k: 0 for k in cls}
    for _ in range(N):
        b = dict(year=random.randint(1950, 2005), month=random.randint(1, 12), day=random.randint(1, 28), hour=random.randint(0, 23), minute=0,
                 gender=random.choice(["male", "female"]))
        seen = set()
        ids_in(c.post("/api/reasoning", json=b).json()["systems"]["tu_vi"]["findings"], seen)
        ids_in(c.post("/api/bazi-structure", json=b).json(), seen)
        for k in cls:
            hits[k] += k in seen
    out = {"n_charts": N, "seed": SEED, "birth_years": "1950-2005",
           "note": "share of random charts on which the rule currently yields a supported/limited finding (default API flags)",
           "rules": {k: round(100 * v / N, 1) for k, v in hits.items()}}
    json.dump(out, open(os.path.join(ROOT, "docs", "source_audit_fix_impact.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(out["rules"], ensure_ascii=False))


if __name__ == "__main__":
    main()
