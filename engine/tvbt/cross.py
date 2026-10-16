"""Comparison layer. Keeps the two engines separate; only aligns by discussion TOPIC.
It never equates a Tử Vi palace with a BaZi ten-god, and never claims agreement raises probability."""
from __future__ import annotations

import dataclasses

from . import bazi, tuvi
from .calendar_core import BirthInput, normalize

TOPIC_MAP = {  # topic -> (tu_vi palace name, bat_tu ten gods that MAY be discussed under it). A discussion index only.
    "career": ("Quan Lộc", ["Chính Quan", "Thất Sát", "Chính Tài", "Chính Ấn"]),
    "wealth": ("Tài Bạch", ["Chính Tài", "Thiên Tài", "Thực Thần", "Thương Quan"]),
    "relationship": ("Phu Thê", ["Chính Tài", "Chính Quan"]),
}
CAVEAT = ("Hai hệ thống dùng quy tắc và đơn vị khác nhau; việc cùng bàn một chủ đề không có nghĩa là tương đương "
          "hay làm tăng độ chắc chắn.")


def compare_systems(tv_interps: list, bz_interps: list) -> dict:
    """tv_interps / bz_interps: nlg.generate.Interpretation lists from SEPARATE inference runs."""
    out = {"shared_topics": [], "tuvi_only": [], "bazi_only": [], "caveat": CAVEAT}
    tv_by = {i.claim: i for i in tv_interps}
    bz_by = {i.claim: i for i in bz_interps}
    for claim in sorted(set(tv_by) | set(bz_by)):
        a, b = tv_by.get(claim), bz_by.get(claim)
        if a and b:
            out["shared_topics"].append({"claim": claim, "tuvi": {"status": a.status, "rules": a.supporting + a.opposing},
                                         "bazi": {"status": b.status, "rules": b.supporting + b.opposing}})
        elif a:
            out["tuvi_only"].append(claim)
        else:
            out["bazi_only"].append(claim)
    return out


def compare_charts(a: BirthInput, b: BirthInput) -> dict:
    """What changes between two birth hypotheses (e.g. uncertain birth hour)."""
    na, nb = normalize(a), normalize(b)
    ba, bb = bazi.compute(na), bazi.compute(nb)
    ta, tb = tuvi.compute(na), tuvi.compute(nb)
    diff = {"bazi_pillars": {k: [ba.pillars[k].name, bb.pillars[k].name] for k in ba.pillars
                             if ba.pillars[k].name != bb.pillars[k].name},
            "tuvi": {}}
    for key in ("menh_branch", "than_branch"):
        if getattr(ta, key) != getattr(tb, key):
            diff["tuvi"][key] = [getattr(ta, key), getattr(tb, key)]
    if ta.cuc != tb.cuc:
        diff["tuvi"]["cuc"] = [ta.cuc["name"], tb.cuc["name"]]
    sa = {s.name: s.branch for s in ta.stars}
    sb = {s.name: s.branch for s in tb.stars}
    diff["tuvi"]["moved_stars"] = sorted(n for n in sa if sa[n] != sb[n])
    diff["tuvi"]["unchanged_star_count"] = sum(1 for n in sa if sa[n] == sb[n])
    diff["luck_direction_changed"] = ba.luck_direction != bb.luck_direction
    diff["note"] = "Interpretations depending on changed items lose validity; recompute via inference."
    return diff
