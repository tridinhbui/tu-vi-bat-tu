"""Refresh facts.bazi.deep (bazi_deep.pipeline.prose_summary), and the Bát Tự luck list and pillar relations, in the prose test fixtures,
leaving every other fact untouched, so the TS goldens of the Tử Vi chapters do not move when the Bát Tự facts grow (S2 2026-10-22: luck
start_year by the shared mid-year rule plus start_date, bán hợp and 10-pair can xung/khắc in the relations).
    .venv/bin/python tools/interpret/refresh_bazi_deep.py [--corpus]
--corpus also refreshes the same three facts in corpus1000.json.gz (DEEP-BAZI-2: so the 1,000-chart Bát Tự tests read the current deep facts,
the 八字真宗 kin layer included; the corpus's Tử Vi facts and its python_fired lists are left as they are).
Each fixture's birth is checked against its stored pillars and luck start before anything is written."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engine"))

import tvbt.api as api  # noqa: E402
from tvbt.api import BirthReq  # noqa: E402

FX = ROOT / "src" / "interpret" / "test" / "fixtures"
# births of the single-chart fixtures (the owner's chart 09/01/2002 04:30 nam; the 1990 chart of docs/examples/prose-depth.md)
SINGLE = {"ref_2002_01_09_kl.json": {"year": 2002, "month": 1, "day": 9, "hour": 4, "minute": 30, "gender": "male", "to_year": 2026, "dignity_school": "khao_luan"},
          "user_1990_nam.json": {"year": 1990, "month": 5, "day": 17, "hour": 10, "minute": 0, "gender": "male", "to_year": 2026, "dignity_school": "thuc_hanh"}}


def fresh(birth: dict, old: dict) -> dict:
    new = api.chart_facts(BirthReq(**birth))["bazi"]
    same = lambda d: ({k: v["name"] for k, v in d["pillars"].items()}, d["luck_start_age"], [l["name"] for l in d["luck"]])
    if same(new) != same(old):
        raise SystemExit(f"birth {birth} does not give the fixture's pillars: {same(new)} vs {same(old)}")
    return {k: new[k] for k in ("deep", "luck", "relations")}


def dump(p: Path, d) -> None:
    """write in the file's own JSON style (compact or spaced), so the diff shows only the deep facts"""
    compact = '":' in p.read_text("utf-8")[:200] and '": ' not in p.read_text("utf-8")[:200]
    p.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":") if compact else None), "utf-8")


def main():
    for name, birth in SINGLE.items():
        p = FX / name
        d = json.loads(p.read_text("utf-8"))
        d["bazi"].update(fresh(birth, d["bazi"]))
        dump(p, d)
        print("refreshed", name)
    p = FX / "benchmark20.json"
    bench = json.loads(p.read_text("utf-8"))
    for c in bench:
        c["facts"]["bazi"].update(fresh({"dignity_school": "thuc_hanh", **c["birth"]}, c["facts"]["bazi"]))
    dump(p, bench)
    print("refreshed benchmark20.json", len(bench))


def corpus():
    import gzip
    p = FX / "corpus1000.json.gz"
    items = json.loads(gzip.decompress(p.read_bytes()).decode("utf-8"))
    for c in items:
        c["facts"]["bazi"].update(fresh({"dignity_school": "thuc_hanh", **c["birth"]}, c["facts"]["bazi"]))
    p.write_bytes(gzip.compress(json.dumps(items, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), mtime=0))
    print("refreshed corpus1000.json.gz", len(items))


if __name__ == "__main__":
    main()
    if "--corpus" in sys.argv:
        corpus()
