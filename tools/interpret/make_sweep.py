"""Sweep corpus for the interpretation pipeline: diverse charts chosen to COVER configurations (not random), so that template and
reasoning defects show up across the cases the planner must handle. Written gzipped to src/interpret/test/fixtures/sweep.json.gz.
    .venv/bin/python tools/interpret/make_sweep.py
Selection: 1,500 seeded random birth records -> facts -> greedy cover of the feature list below (each feature wanted at least twice),
then filled to 40 charts by the rarest-feature score. The 8 regression charts in charts.json are kept separate."""
import gzip
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engine"))
from fastapi.testclient import TestClient  # noqa: E402

from tvbt.api import app  # noqa: E402

MAJORS = ["Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh", "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn",
          "Thiên Tướng", "Thiên Lương", "Thất Sát", "Phá Quân"]
SAT = {"Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"}


def features(f):
    P = {p["name"]: p for p in f["palaces"]}
    by_idx = {p["branch_index"]: p for p in f["palaces"]}
    q, m = P["Quan Lộc"], P["Mệnh"]
    tp = [q, by_idx[(q["branch_index"] + 4) % 12], by_idx[(q["branch_index"] + 8) % 12], by_idx[(q["branch_index"] + 6) % 12]]
    hoa_at = {h: by_idx[v["branch"]]["name"] for h, v in f["tu_hoa"].items()}
    out = set()
    out.add("ql_vcd" if not q["major_stars"] else "ql_pair" if len(q["major_stars"]) == 2 else "ql_single")
    for s in q["major_stars"]:
        out.add("ql_major:" + s)
    if not m["major_stars"]:
        out.add("menh_vcd")
    if q["tuan"]: out.add("ql_tuan")
    if q["triet"]: out.add("ql_triet")
    if m["tuan"] or m["triet"]: out.add("menh_tt")
    for h, pal in hoa_at.items():
        if pal == "Quan Lộc": out.add("ql_" + h)
        if pal in [x["name"] for x in tp] and h == "Hóa Kỵ": out.add("tp_hoa_ky")
    if q["is_than"]: out.add("than_ql")
    nsat = sum(1 for p in tp for s in p["stars"] if s in SAT)
    out.add("tp_sat_0" if nsat == 0 else "tp_sat_4+" if nsat >= 4 else "tp_sat_mid")
    if {"Lộc Tồn", "Thiên Mã"} <= {s for p in tp for s in p["stars"]}: out.add("tp_loc_ma")
    y = f["year"]
    dq = next((d for d in f["decades"] if d["palace"] == "Quan Lộc"), None)
    if dq and dq["age_from"] <= y["age_tuoi_mu"] <= dq["age_to"]: out.add("now_in_ql_decade")
    if dq and y["age_tuoi_mu"] > dq["age_to"]: out.add("passed_ql_decade")
    if y.get("tieu_han_palace") == "Quan Lộc": out.add("year_ql")
    out.add("gender:" + f["gender"])
    if f["birth_year"] < 1960: out.add("old")
    if f["birth_year"] > 2015: out.add("child")
    return out


def main():
    client = TestClient(app)
    rnd = random.Random(20261019)
    pool = []
    for _ in range(1500):
        b = {"year": rnd.randint(1930, 2024), "month": rnd.randint(1, 12), "day": rnd.randint(1, 28), "hour": rnd.randint(0, 23),
             "minute": rnd.choice([0, 15, 30, 45]), "gender": rnd.choice(["male", "female"]), "to_year": 2026}
        r = client.post("/api/facts", json=b)
        if r.status_code != 200:
            continue
        f = r.json()
        pool.append((b, f, features(f)))
    want = {}
    for _, _, fs in pool:
        for x in fs:
            want[x] = 2
    chosen = []
    while len(chosen) < 40:
        best = max((c for c in pool if c not in chosen), key=lambda c: (sum(1 for x in c[2] if want.get(x, 0) > 0),
                                                                          -sum(len([o for o in pool if x in o[2]]) for x in c[2]) / 1e6))
        if sum(1 for x in best[2] if want.get(x, 0) > 0) == 0:
            break
        chosen.append(best)
        for x in best[2]:
            want[x] = want.get(x, 0) - 1
    rest = sorted((c for c in pool if c not in chosen), key=lambda c: min(len([o for o in pool if x in o[2]]) for x in c[2]))
    chosen += rest[: 40 - len(chosen)]
    out = [{"label": "sweep " + ",".join(sorted(x for x in fs if not x.startswith("gender"))[:6]), "birth": b, "features": sorted(fs), "facts": f}
           for b, f, fs in chosen]
    dst = ROOT / "src" / "interpret" / "test" / "fixtures" / "sweep.json.gz"
    dst.write_bytes(gzip.compress(json.dumps(out, ensure_ascii=False, separators=(",", ":")).encode(), mtime=0))
    cover = {}
    for _, _, fs in chosen:
        for x in fs:
            cover[x] = cover.get(x, 0) + 1
    missing = sorted(x for x in want if x not in cover)
    print(dst, dst.stat().st_size, "bytes,", len(out), "charts; features covered", len(cover), "missing", missing)


if __name__ == "__main__":
    main()
