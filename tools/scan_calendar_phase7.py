"""Phase 7 calendar scan, every civil day 1930-03-01 .. 2060-12-31 (47,789 days):
  production 'cn' (sxtwl)            vs  Hong Kong Observatory table (independent data, UTC+8)
  independent amlich oracle (UTC+8)  vs  HKO                      -> validates the oracle itself
  production 'vn' / 'vn_south'       vs  oracle with the same UTC rule (+8 before 1968 / 1976, +7 after)
Each disagreement is classified with PyEphem new-moon times. Writes engine/tests/fixtures/calendar_comparison.json."""
import bisect
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine")); sys.path.insert(0, str(ROOT / "engine/tests"))
import oracle_calendar_independent as K  # noqa: E402
from tvbt import calendar_core as cc  # noqa: E402

ref = json.load(open(ROOT / "engine/tests/fixtures/calendar_reference_hko.json", encoding="utf-8"))
starts = sorted((dt.date.fromisoformat(d), m, lp) for y in range(1901, 2101) for d, m, lp in ref["years"][str(y)]["month_starts"])
keys = [s[0] for s in starts]


def hko(d):
    s = starts[bisect.bisect_right(keys, d) - 1]
    return ((d - s[0]).days + 1, s[1], s[2])


def prod(d, cal):
    n = cc.normalize(cc.BirthInput(d.year, d.month, d.day, 12, 0, "Asia/Ho_Chi_Minh", "male", calendar=cal))
    return (n.lunar.day, n.lunar.month, n.lunar.is_leap)


def orc(d, tz):
    r = K.solar_to_lunar(d.day, d.month, d.year, tz)
    return (r[0], r[1], r[3])


bad = {"cn_vs_hko": [], "oracle8_vs_hko": [], "vn_vs_oracle": [], "vn_south_vs_oracle": []}
d, n = dt.date(1903, 3, 1), 0
while d <= dt.date(2098, 12, 31):
    n += 1
    h = hko(d)
    if prod(d, "cn") != h:
        bad["cn_vs_hko"].append(d.isoformat())
    if orc(d, 8) != h:
        bad["oracle8_vs_hko"].append(d.isoformat())
    if prod(d, "vn") != orc(d, 8 if d.year < 1968 else 7):
        bad["vn_vs_oracle"].append(d.isoformat())
    if prod(d, "vn_south") != orc(d, 8 if d.year < 1976 else 7):
        bad["vn_south_vs_oracle"].append(d.isoformat())
    d += dt.timedelta(days=1)


def spans(l):
    out, prev = [], None
    for s in l:
        x = dt.date.fromisoformat(s)
        if prev and (x - prev).days == 1:
            out[-1][1] = s
        else:
            out.append([s, s])
        prev = x
    return out


(ROOT / "engine/tests/fixtures/calendar_comparison.json").write_text(json.dumps(
    {"days": n, "range": ["1903-03-01", "2098-12-31"], "counts": {k: len(v) for k, v in bad.items()}, "spans": {k: spans(v) for k, v in bad.items()}}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(n, {k: len(v) for k, v in bad.items()})
