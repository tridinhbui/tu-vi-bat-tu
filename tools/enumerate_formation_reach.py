"""Exhaustively enumerate every (formation, state) cell reachable over one full sexagenary cycle.

Years 1950-2009 (60 consecutive lunar years = every year-stem/branch pair), EVERY solar day, 12 hour-branches, both genders
= ~526k charts, which covers every combination of lunar month/day/hour/year. A cell absent here cannot occur for the engine's
chart space; the script also prints a witness for every reachable cell.

Usage: python tools/enumerate_formation_reach.py > engine/tests/fixtures/formation_reach.json"""
import datetime as dt
import json
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "engine"
sys.path.insert(0, str(ROOT))

from tvbt import tuvi  # noqa: E402
from tvbt.calendar_core import BirthInput, normalize  # noqa: E402
from tvbt.formation_explain import analyse  # noqa: E402
from tvbt.knowledge.loader import load_experimental  # noqa: E402

_, XF, _ = load_experimental()


def run_year(y: int):
    seen, wit, ev = Counter(), {}, Counter()
    d = dt.date(y, 1, 1)
    while d.year == y:
        for h in range(0, 24, 2):          # 0,2,...,22 = one representative hour per branch
            for g in ("male", "female"):
                tv = tuvi.compute(normalize(BirthInput(d.year, d.month, d.day, h, 0, "Asia/Ho_Chi_Minh", g)))
                for f in analyse(tv, XF):
                    k = f"{f['id']}|{f['state']}"
                    seen[k] += 1
                    if f['state'] != 'khong_hien':
                        ev[f"{f['id']}|core"] += 1
                        for e in f['evidence']:
                            if e['active']:
                                ev[f"{f['id']}|{e['kind']}|{e['id']}"] += 1
                    wit.setdefault(k, dict(year=d.year, month=d.month, day=d.day, hour=h, minute=0, gender=g))
        d += dt.timedelta(days=1)
    return seen, wit, ev


if __name__ == "__main__":
    tot, wit, evt = Counter(), {}, Counter()
    with Pool() as p:
        for s, w, e in p.imap_unordered(run_year, range(1950, 2010)):
            tot.update(s)
            evt.update(e)
            for k, v in w.items():
                wit.setdefault(k, v)
    ids = [f.id for f in XF]
    states = ["khong_hien", "hinh_thuc", "thanh", "thanh_thuong", "bi_pha", "pha_duoc_cuu"]
    out = {"charts_per_formation": sum(v for k, v in tot.items() if k.startswith(ids[0] + "|")),
           "counts": dict(sorted(tot.items())), "evidence_active_when_core_true": dict(sorted(evt.items())), "witness": dict(sorted(wit.items())),
           "unreachable": sorted(f"{i}|{s}" for i in ids for s in states if f"{i}|{s}" not in tot)}
    print(json.dumps(out, ensure_ascii=False, indent=1))
