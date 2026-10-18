#!/usr/bin/env python3
"""How many readings does the Tử Vi rule library produce for a RANDOM chart?

Why it matters: if nearly every chart receives several 'wealth / rank / success' readings and several 'limits', then
finding that a famous person's chart "fits" its readings is expected under chance and shows nothing. This script
measures that base rate through the real API (/api/reasoning) on random birth data. Deterministic (seed fixed).

usage: python tools/measure_reading_base_rate.py [N=400] [--out docs/reading_base_rate.json]
Keyword classes are a rough text heuristic on the Vietnamese claim phrases, not a semantic classifier.
"""
import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from fastapi.testclient import TestClient  # noqa: E402
from tvbt.api import app  # noqa: E402

SEED = 20261017
POS = ("giàu", "phú", "quý", "sang", "công danh", "phát", "danh vọng", "thành công")


def quant(v):
    v = sorted(v)
    n = len(v)
    return {"min": v[0], "q1": v[n // 4], "median": v[n // 2], "q3": v[3 * n // 4], "max": v[-1]}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n = int(args[0]) if args else 400
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    c = TestClient(app)
    random.seed(SEED)
    cl = json.load(open(os.path.join(ROOT, "engine", "data", "claims_vi.json"), encoding="utf-8"))
    rows = []
    for _ in range(n):
        b = dict(year=random.randint(1950, 2005), month=random.randint(1, 12), day=random.randint(1, 28),
                 hour=random.randint(0, 23), minute=0, gender=random.choice(["male", "female"]))
        f = c.post("/api/reasoning", json=b).json()["systems"]["tu_vi"]["findings"]
        sup = [x for x in f if x["status"] == "supported" and x.get("effect") == "support"]
        lim = [x for x in f if x.get("effect") == "limit"]
        menh = [x for x in sup if x["subject"] == "palace:Mệnh"]
        txt = lambda x: cl.get(x["claim"], "")  # noqa: E731
        pos_any = [x for x in sup if any(w in txt(x) for w in POS)]
        pos_menh = [x for x in menh if any(w in txt(x) for w in POS)]
        rows.append({"findings": len(f), "supporting": len(sup), "limits": len(lim), "menh_supporting": len(menh),
                     "menh_wealth_rank_success": len(pos_menh), "wealth_rank_success_any": len(pos_any)})
    res = {"n_charts": n, "seed": SEED, "birth_years": "1950-2005", "dignity_school": "thuc_hanh (default)",
           "distribution": {k: quant([r[k] for r in rows]) for k in rows[0]},
           "share_charts_with_wealth_rank_success_reading_anywhere": sum(r["wealth_rank_success_any"] > 0 for r in rows) / n,
           "share_charts_with_wealth_rank_success_reading_at_menh": sum(r["menh_wealth_rank_success"] > 0 for r in rows) / n,
           "share_charts_with_a_limit_finding": sum(r["limits"] > 0 for r in rows) / n,
           "note": "Keyword heuristic on Vietnamese claim text. A chart that 'fits' its readings is the expected outcome for any chart."}
    # the book's own worked example (Hán Cao Tổ, KL pp.237-238; lunar 13/11 of a Giáp Ngọ year, hour Ngọ, male), rebuilt as in tests/test_book_examples.py
    from tvbt import lunar_input
    sol = lunar_input.lunar_to_solar(13, 11, 2014, False, "vn")[0]
    f = c.post("/api/reasoning", json=dict(year=sol.year, month=sol.month, day=sol.day, hour=12, minute=0, gender="male")).json()["systems"]["tu_vi"]["findings"]
    sup = [x for x in f if x["status"] == "supported" and x.get("effect") == "support"]
    res["book_example_han_cao_to"] = {"solar_date": str(sol), "findings": len(f), "supporting": len(sup),
                                      "limits": len([x for x in f if x.get("effect") == "limit"]),
                                      "menh_supporting": len([x for x in sup if x["subject"] == "palace:Mệnh"]),
                                      "menh_wealth_rank_success": len([x for x in sup if x["subject"] == "palace:Mệnh" and any(w in cl.get(x["claim"], "") for w in POS)]),
                                      "percentile_of_findings_among_random": round(100 * sum(r["findings"] <= len(f) for r in rows) / n)}
    txt = json.dumps(res, ensure_ascii=False, indent=1)
    if out:
        open(os.path.join(ROOT, out), "w", encoding="utf-8").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
