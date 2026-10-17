"""Tầng Thế (khí thế): sức của từng chữ, từng nhóm sinh–khắc quanh Nhật Chủ, bốn trục đắc lệnh/địa/thế/sinh, thang vượng–nhược có biên.
compute(view, profile, resolved=None) is run twice by the pipeline: on the raw chart (resolved=None) and after the interaction
resolver, so the report can show what the interactions changed. All weights are SchoolProfile values (he_thong, draft)."""
from __future__ import annotations

from ..ganzhi import BRANCHES_VI, BRANCH_ELEMENT, ELEMENTS, STEM_ELEMENT, STEMS_VI, controls, generates
from ..bazi import HIDDEN_STEMS
from .interact import Resolved
from .model import PILLARS, PIL_VI, ChartView
from .position import root_grade, roots
from .profile import DEFAULT, LEVELS, SchoolProfile
from .season import command, season_states

GROUPS = ["Ti", "An", "ThucThuong", "Tai", "QuanSat"]
GROUP_VI = {"Ti": "Tỉ Kiếp", "An": "Ấn", "ThucThuong": "Thực Thương", "Tai": "Tài", "QuanSat": "Quan Sát"}


def group_of_element(dm_el: str, el: str) -> str:
    if el == dm_el:
        return "Ti"
    if generates(el, dm_el):
        return "An"
    if generates(dm_el, el):
        return "ThucThuong"
    if controls(dm_el, el):
        return "Tai"
    return "QuanSat"


def level_of(ratio: float, cuts) -> tuple[int, float]:
    i = sum(1 for c in cuts if ratio >= c)
    margin = min(abs(ratio - c) for c in cuts)
    return i, margin


def compute(view: ChartView, profile: SchoolProfile = DEFAULT, resolved: Resolved | None = None, extras: list[dict] | None = None) -> dict:
    mult = resolved.mult if resolved else {}
    shifts = resolved.shifts if resolved else {}
    stem_override = resolved.stem_element if resolved else {}
    opened = resolved.opened if resolved else set()
    dm_el = resolved.dm_element if resolved else view.dm_element
    states = season_states(view.month_branch)
    cmd = command(view, profile)
    contrib: list[dict] = []

    def add(cid, el, w, note):
        g = group_of_element(dm_el, el)
        contrib.append({"char": cid, "element": el, "group": g, "weight": round(w, 4), "note": note})

    for p in PILLARS:
        df = profile.dist_factor[ChartView.dist(p, "day")]
        if p != "day":
            cid = f"{p}.stem"
            el = stem_override.get(cid, STEM_ELEMENT[view.stem(p)])
            add(cid, el, profile.pos_weight_stem[p] * mult.get(cid, 1.0) * df * profile.season_factor[states[el]], "thiên can")
        bid = f"{p}.branch"
        fr = profile.hidden_frac[len(HIDDEN_STEMS[view.branch(p)])]
        bw = profile.pos_weight_branch[p] * mult.get(bid, 1.0) * df
        shift = shifts.get(bid)
        keep = 1.0 - (shift[1] if shift else 0.0)
        for i, h in enumerate(HIDDEN_STEMS[view.branch(p)]):
            el = STEM_ELEMENT[h]
            add(bid, el, bw * fr[i] * keep * profile.season_factor[states[el]], f"tàng can {STEMS_VI[h]}")
        if shift:
            add(bid, shift[0], bw * shift[1] * profile.season_factor[states[shift[0]]], f"hợp cục {shift[0]}")
        if p == "month" and cmd:
            el = cmd["element"]
            add(bid, el, bw * profile.tu_lenh_bonus * profile.season_factor[states[el]], f"tư lệnh {cmd['name']}")

    for e in (extras or []):           # temporal contributions: {char, element, weight, note}
        add(e["char"], e["element"], e["weight"], e["note"])

    by_group = {g: 0.0 for g in GROUPS}
    by_element = {e: 0.0 for e in ELEMENTS}
    for c in contrib:
        by_group[c["group"]] += c["weight"]
        by_element[c["element"]] += c["weight"]
    total = sum(by_group.values()) or 1.0
    help_ = by_group["Ti"] + by_group["An"]
    ratio = help_ / total
    idx, margin = level_of(ratio, profile.level_cuts)

    # --- bốn trục
    st = states[dm_el]
    de_lenh = {"vượng": "đắc lệnh", "tướng": "được lệnh sinh"}.get(st, "thất lệnh")
    rs = roots(view, view.dm, profile, mult, opened, shifts) if dm_el == view.dm_element else []
    grade = root_grade(rs)
    vis_help = [c for c in contrib if c["note"] == "thiên can" and c["group"] in ("Ti", "An")]
    de_the = "đông" if len(vis_help) >= 2 else "có" if vis_help else "không"
    an_share = by_group["An"] / total
    de_sinh = "mạnh" if an_share >= 0.25 else "có" if an_share >= 0.08 else "yếu/không"

    ambiguous = margin < profile.level_margin
    readings = [LEVELS[idx]]
    if ambiguous:
        near = min(profile.level_cuts, key=lambda c: abs(ratio - c))
        other = idx - 1 if ratio < near else idx + 1
        if 0 <= other < len(LEVELS):
            readings.append(LEVELS[other])
    return {
        "dm_element": dm_el, "season_state": st, "month_states": states, "command": cmd,
        "axes": {"de_lenh": de_lenh, "de_dia": grade, "de_the": de_the, "de_sinh": de_sinh},
        "roots": rs, "by_group": {k: round(v, 3) for k, v in by_group.items()}, "by_element": {k: round(v, 3) for k, v in by_element.items()},
        "shares": {k: round(v / total, 4) for k, v in by_group.items()},
        "ratio": round(ratio, 4), "level": LEVELS[idx], "level_index": idx, "margin": round(margin, 4), "ambiguous": ambiguous, "readings": readings,
        "top_contributions": sorted(contrib, key=lambda c: -c["weight"])[:6], "n_contrib": len(contrib),
        "profile": profile.id,
    }
