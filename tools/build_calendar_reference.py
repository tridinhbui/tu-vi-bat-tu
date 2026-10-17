"""Independent calendar reference: Hong Kong Observatory 'Gregorian-Lunar Calendar Conversion Table' text files (1901-2100, UTC+8), downloaded from
https://www.hko.gov.hk/tc/gts/time/calendar/text/files/T<year>c.txt into a directory given as argv[1]. Stores only what the tests need:
every lunar-month start (solar date, month number, leap flag) and every solar-term date.  Output: engine/tests/fixtures/calendar_reference_hko.json
HKO is the Chinese civil calendar (UTC+8): it is a reference for calendar 'cn', NOT for the Vietnamese calendar (UTC+7)."""
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = Path(sys.argv[1])
NUM = {"正": 1, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10, "十一": 11, "十二": 12}
out = {"source": "Hong Kong Observatory, Gregorian-Lunar Calendar Conversion Table (UTC+8)", "years": {}}
for y in range(1901, 2101):
    starts, terms = [], []
    for ln in (src / f"T{y}c.txt").read_text("utf-8-sig").splitlines():
        m = re.match(r"(\d{4})年(\d{2}|\d)月(\d{2}|\d)日\s+(\S+)\s+星期\S\s*(\S*)", ln)
        if not m:
            continue
        d = dt.date(int(m[1]), int(m[2]), int(m[3])).isoformat()
        lunar, term = m[4], m[5]
        if lunar.endswith("月"):
            leap = lunar.startswith("閏")
            name = lunar[1:-1] if leap else lunar[:-1]
            starts.append([d, NUM[name], leap])
        if term:
            terms.append([d, term])
    assert len(starts) in (12, 13) and len(terms) == 24, (y, len(starts), len(terms))
    out["years"][str(y)] = {"month_starts": starts, "terms": terms}
(ROOT / "engine/tests/fixtures/calendar_reference_hko.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
print(len(out["years"]), "years")
