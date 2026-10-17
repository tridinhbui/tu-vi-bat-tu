"""Tầng Thế (vị trí): thông căn phân cấp, thấu can, khố, kề sát."""
from __future__ import annotations

from ..ganzhi import BRANCHES_VI, STEM_ELEMENT, STEMS_VI
from .model import CLASS_NAMES, PILLARS, ChartView
from .profile import DEFAULT, SchoolProfile

KHO = {1, 4, 7, 10}   # Sửu Thìn Mùi Tuất


def roots(view: ChartView, stem: int, profile: SchoolProfile = DEFAULT, mult: dict | None = None, opened: set | None = None, shifts: dict | None = None) -> list[dict]:
    """Every hidden stem (in any branch) of the same element as `stem`. score = class × growth stage × (1 same char, 0.7 same element),
    × branch multiplier from the interaction resolver, × 0.5 for an unopened khố when the profile says khố needs opening."""
    mult, opened, shifts = mult or {}, opened or set(), shifts or {}
    out = []
    for p in PILLARS:
        for i, h in enumerate(view.hidden(p)):
            if STEM_ELEMENT[h["stem"]] != STEM_ELEMENT[stem]:
                continue
            stage = view.stage(stem, p)
            same = h["stem"] == stem
            sc = profile.class_weight[CLASS_NAMES[i]] * profile.stage_weight[stage] * (1.0 if same else 0.7)
            if view.branch(p) in KHO and stage == "Mộ" and profile.kho_policy == "can_mo" and p not in opened:
                sc *= 0.5
            sc *= mult.get(f"{p}.branch", 1.0)
            if f"{p}.branch" in shifts:      # the branch's qi was partly re-assigned to a hợp/hội cục
                sc *= 1.0 - shifts[f"{p}.branch"][1]
            out.append({"pillar": p, "branch": BRANCHES_VI[view.branch(p)], "hidden": STEMS_VI[h["stem"]], "class": CLASS_NAMES[i],
                        "same_char": same, "stage": stage, "score": round(sc, 3)})
    return out


def root_grade(rs: list[dict]) -> str:
    m = max((r["score"] for r in rs), default=0.0)
    return "mạnh" if m >= 0.8 else "vừa" if m >= 0.45 else "yếu" if m > 0 else "không"


def tou(view: ChartView) -> list[dict]:
    """Hidden stems of the month branch (nguyệt lệnh) and whether the same character / same element is on the heavenly stems
    (year, month, hour; the day stem is the Nhật Chủ itself and is reported separately)."""
    out = []
    vis = [(p, view.stem(p)) for p in PILLARS if p != "day"]
    for i, h in enumerate(view.hidden("month")):
        same = [p for p, s in vis if s == h["stem"]]
        elem = [p for p, s in vis if STEM_ELEMENT[s] == STEM_ELEMENT[h["stem"]] and s != h["stem"]]
        out.append({"stem": STEMS_VI[h["stem"]], "class": CLASS_NAMES[i], "ten_god": h["ten_god"], "tou_same_char": same,
                    "tou_same_element": elem, "same_as_day_master": h["stem"] == view.dm,
                    "adjacent_to_month": "month" in same or any(ChartView.dist("month", p) == 1 for p in same)})
    return out


def adjacency(a: str, b: str) -> str:
    d = ChartView.dist(a, b)
    return "tọa" if d == 0 else "kề" if d == 1 else "cách_1" if d == 2 else "xa"
