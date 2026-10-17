"""Find REAL charts (computed by the engine) that land in each (formation, state) cell, to pin as regression fixtures.

Usage: python tools/scan_formation_samples.py [N] > engine/tests/fixtures/formation_charts.json
Deterministic: a fixed-seed sample of birth data in 1950-2010. The pinned verdicts are regression guards (engine output),
NOT independent proof that the draft formation definitions are right; the independent cross-check lives in
tests/test_formation_oracle.py."""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "engine"
sys.path.insert(0, str(ROOT))

from tvbt import tuvi  # noqa: E402
from tvbt.calendar_core import BirthInput, normalize  # noqa: E402
from tvbt.formation_explain import analyse  # noqa: E402
from tvbt.knowledge.loader import load_experimental  # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 6000
_, XF, _ = load_experimental()
rng = random.Random(20261017)
cells: dict[tuple[str, str], list] = defaultdict(list)
special: dict[str, list] = defaultdict(list)
seen = 0
for _ in range(N):
    y, m, d = rng.randint(1950, 2010), rng.randint(1, 12), rng.randint(1, 28)
    h, g = rng.randint(0, 23), rng.choice(["male", "female"])
    b = BirthInput(y, m, d, h, 0, "Asia/Ho_Chi_Minh", g)
    tv = tuvi.compute(normalize(b))
    seen += 1
    for f in analyse(tv, XF):
        key = (f["id"], f["state"])
        rec = {"birth": dict(year=y, month=m, day=d, hour=h, minute=0, gender=g)}
        if len(cells[key]) < 3:
            cells[key].append({**rec, "formation": f["id"], "state": f["state"]})
        act = lambda k: [e["id"] for e in f["evidence"] if e["kind"] == k and e["active"]]
        if len(act("refutations")) >= 2 and len(special["many_refutations"]) < 6:
            special["many_refutations"].append({**rec, "formation": f["id"], "state": f["state"], "refutations": act("refutations")})
        if f["downgraded"] and len(special["downgraded"]) < 6:
            special["downgraded"].append({**rec, "formation": f["id"], "state": f["state"]})
        if len(f["uncovered"]) >= 2 and len(special["many_uncovered"]) < 4:
            special["many_uncovered"].append({**rec, "formation": f["id"], "state": f["state"], "uncovered": f["uncovered"]})
        if f["state"] == "pha_duoc_cuu" and len(act("rescuers")) >= 2 and len(special["many_rescuers"]) < 4:
            special["many_rescuers"].append({**rec, "formation": f["id"], "state": f["state"]})
out = {"seed": 20261017, "scanned": seen, "cells": [c for v in cells.values() for c in v],
       "special": special,
       "coverage": {f"{k[0]}|{k[1]}": len(v) for k, v in sorted(cells.items())}}
print(json.dumps(out, ensure_ascii=False, indent=1))
