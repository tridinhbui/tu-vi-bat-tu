"""A/B regression: proves a change did not alter the PRODUCTION readings.
Usage:  python tools/ab_regression.py <engine_dir_A> <engine_dir_B> [python]
Each dir is an `engine/` folder (e.g. `git archive HEAD` extracted vs the working tree). For a fixed grid of 18 births it hashes
/api/chart, /api/analysis, /api/reasoning (+ the list of tu_vi findings) and /api/year (3 years: tiểu hạn + vận readings) in a subprocess per dir, then reports any difference.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

PROBE = r'''
import sys, json, hashlib, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, ".")
from fastapi.testclient import TestClient
from tvbt.api import app
GRID = [dict(year=y, month=m, day=d, hour=h, minute=15, gender=g)
        for (y, m, d, h) in [(1984,2,9,5),(1990,5,17,10),(1975,11,3,23),(2001,8,28,14),(1968,1,15,0),(1993,12,1,7),(1988,7,7,19),(1979,3,21,12),(2010,10,10,3)]
        for g in ("male", "female")]
H = lambda o: hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True, default=str).encode()).hexdigest()
c = TestClient(app); out = {}
for b in GRID:
    k = f"{b['year']}-{b['month']}-{b['day']}T{b['hour']}/{b['gender']}"
    rea = c.post("/api/reasoning", json=b).json()
    out[k] = {"chart": H(c.post("/api/chart", json=b).json()), "analysis": H(c.post("/api/analysis", json=b).json()),
              "reasoning": H(rea), "year": H([c.post("/api/year", json={**b, "to_year": ty}).json() for ty in (2012, 2024, 2040)]), "findings": sorted(f"{f['subject']}|{f['claim']}|{f['effect']}|{f['rule_id']}" for f in rea["systems"]["tu_vi"]["findings"])}
print(json.dumps(out, sort_keys=True))
'''


def probe(engine_dir: str, py: str) -> dict:
    r = subprocess.run([py, "-c", PROBE], cwd=engine_dir, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr)
    return json.loads(r.stdout.strip().splitlines()[-1])


if __name__ == "__main__":
    a, b = sys.argv[1], sys.argv[2]
    py = sys.argv[3] if len(sys.argv) > 3 else sys.executable
    A, B = probe(a, py), probe(b, py)
    bad = [(k, f) for k in A for f in A[k] if A[k][f] != B.get(k, {}).get(f)]
    print(f"{len(A)} births x {len(next(iter(A.values())))} outputs compared: " + ("IDENTICAL" if not bad else f"{len(bad)} DIFFERENCES"))
    for k, f in bad[:20]:
        print("  differs:", k, f)
    sys.exit(1 if bad else 0)
