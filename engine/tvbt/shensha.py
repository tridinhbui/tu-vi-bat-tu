"""Thần sát (神煞) lookups from 八字真宗 PDF pp.21-22. Pure table lookups; no outcome is stated for stars the book labels harmful."""
from __future__ import annotations

import json
from pathlib import Path

from .ganzhi import BRANCHES_HAN, BRANCHES_VI, STEMS_HAN

_DATA = json.loads((Path(__file__).resolve().parent.parent / "data" / "shensha.json").read_text("utf-8"))["tables"]
PILLAR_VI = {"year": "năm", "month": "tháng", "day": "ngày", "hour": "giờ"}


def find(pillars: dict) -> list[dict]:
    """pillars: {'year'|'month'|'day'|'hour': Pillar with .stem/.branch}. Returns stars present among the chart's branches."""
    ds, db = STEMS_HAN[pillars["day"].stem], BRANCHES_HAN[pillars["day"].branch]
    keys = {"by_day_stem": ds, "by_day_branch": db, "by_month_branch": BRANCHES_HAN[pillars["month"].branch],
            "by_year_branch": BRANCHES_HAN[pillars["year"].branch]}
    out = []
    for table, key in keys.items():
        for zh, t in _DATA[table].items():
            targets = t["row"][key]
            for pk, p in pillars.items():
                if pk == "day" and table in ("by_day_branch",):
                    continue                       # a star keyed on the day branch is not 'found' in the day branch itself
                if table == "by_year_branch" and pk == "year":
                    continue
                if BRANCHES_HAN[p.branch] in targets or (zh == "月德" and STEMS_HAN[p.stem] in targets):
                    out.append({"zh": zh, "vi": t["vi"], "kind": t["kind"], "gloss": t["gloss"], "table": table, "pillar": pk,
                                "pillar_vi": PILLAR_VI[pk], "at": BRANCHES_VI[p.branch] if BRANCHES_HAN[p.branch] in targets else STEMS_HAN[p.stem]})
    return out
