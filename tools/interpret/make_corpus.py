"""Stratified 1,000-chart corpus for the interpretation pipeline (prose plan P0): chart facts exactly as /api/facts returns them plus the
Python rule engine's fired findings, so the TS engine can be held to parity and the prose layer measured on the same charts. Written
gzipped to src/interpret/test/fixtures/corpus1000.json.gz.
    .venv/bin/python tools/interpret/make_corpus.py [--pool 8000] [--n 1000]
Selection: a seeded pool of random birth records -> facts -> greedy cover of the Mệnh-centred strata below, each stratum wanted QUOTA
times (fewer if the pool has fewer), then filled to N by the rarest-stratum score. Deterministic for a given pool size and seed."""
import argparse
import gzip
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

SAT = {"Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"}
QUOTA = 6


def strata(f):
    """Configurations the Mệnh chapter must handle; one chart covers many."""
    P = {p["name"]: p for p in f["palaces"]}
    by_idx = {p["branch_index"]: p for p in f["palaces"]}
    m = P["Mệnh"]
    i = m["branch_index"]
    tp = [m, by_idx[(i + 4) % 12], by_idx[(i + 8) % 12], by_idx[(i + 6) % 12]]
    majors = "+".join(sorted(m["major_stars"])) or "VCD"
    out = {f"menh:{m['branch']}:{majors}", f"menh_major:{majors}", "gender:" + f["gender"]}
    for s, d in m["major_dignity"].items():
        out.add(f"dig:{s}:{d}")
    if m["tuan"]: out.add("menh_tuan")
    if m["triet"]: out.add("menh_triet")
    if m["is_than"]: out.add("than_menh")
    for h, v in f["tu_hoa"].items():
        if v["branch"] == i: out.add("menh_" + h)
    own_sat = SAT & set(m["stars"])
    for s in own_sat: out.add("menh_sat:" + s)
    nsat = sum(1 for p in tp for s in p["stars"] if s in SAT)
    out.add("tp_sat_0" if nsat == 0 else "tp_sat_4+" if nsat >= 4 else "tp_sat_mid")
    if {"Lộc Tồn", "Thiên Mã"} <= {s for p in tp for s in p["stars"]}: out.add("tp_loc_ma")
    if {"Tả Phụ", "Hữu Bật"} & set(m["stars"]): out.add("menh_ta_huu")
    if {"Văn Xương", "Văn Khúc"} & set(m["stars"]): out.add("menh_xuong_khuc")
    if f["birth_year"] < 1950: out.add("old")
    if f["birth_year"] > 2015: out.add("child")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", type=int, default=8000)
    ap.add_argument("--n", type=int, default=1000)
    a = ap.parse_args()
    client = TestClient(app)
    rnd = random.Random(20261018)
    pool = []
    for k in range(a.pool):
        b = {"year": rnd.randint(1930, 2024), "month": rnd.randint(1, 12), "day": rnd.randint(1, 28), "hour": rnd.randint(0, 23),
             "minute": rnd.choice([0, 15, 30, 45]), "gender": rnd.choice(["male", "female"]), "to_year": 2026}
        r = client.post("/api/facts", json={**b, "dignity_school": "thuc_hanh"})
        if r.status_code == 200:
            f = r.json()
            pool.append((b, f, strata(f)))
        if k % 1000 == 0:
            print("pool", k, file=sys.stderr)
    freq = {}
    for _, _, ss in pool:
        for x in ss:
            freq[x] = freq.get(x, 0) + 1
    want = {x: min(QUOTA, c) for x, c in freq.items()}
    chosen, taken = [], set()
    while len(chosen) < a.n:
        best, score = None, 0
        for j, c in enumerate(pool):
            if j in taken:
                continue
            s = sum(1 for x in c[2] if want[x] > 0)
            if s > score:
                best, score = j, s
        if best is None:
            break
        taken.add(best)
        chosen.append(pool[best])
        for x in pool[best][2]:
            want[x] -= 1
    rest = sorted((j for j in range(len(pool)) if j not in taken), key=lambda j: (min(freq[x] for x in pool[j][2]), j))
    chosen += [pool[j] for j in rest[: a.n - len(chosen)]]
    rules, sources = load_all()
    out = []
    for b, f, ss in chosen:
        res = engine.run(rules, sources, f["base"], system="tu_vi")
        bres = engine.run(rules, sources, f["bazi"]["base"], system="bat_tu")
        out.append({"birth": b, "strata": sorted(ss), "facts": f,
                    "python_fired": [list(x) for x in sorted({(x.rule_id, x.subject, x.claim, x.effect, x.basis) for x in res.findings})],
                    "python_fired_bazi": [list(x) for x in sorted({(x.rule_id, x.subject, x.claim, x.effect, x.basis) for x in bres.findings})]})
    dst = ROOT / "src" / "interpret" / "test" / "fixtures" / "corpus1000.json.gz"
    dst.write_bytes(gzip.compress(json.dumps(out, ensure_ascii=False, separators=(",", ":")).encode(), mtime=0))
    short = sorted(x for x, w in want.items() if w > 0)
    cells = sorted({x for _, _, ss in chosen for x in ss if x.startswith("menh:")})
    print(dst, dst.stat().st_size, "bytes,", len(out), "charts;", len(cells), "Mệnh branch×star cells;",
          len(short), "strata under quota:", short[:20])


if __name__ == "__main__":
    main()
