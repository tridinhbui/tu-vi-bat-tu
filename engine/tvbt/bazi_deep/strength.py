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


def _band(share: float, margin: float) -> int:
    """Presentation bands (draft). The book's rule is only the 40% decision; |share-0.40| < margin is reported as the border (trung hòa)."""
    if abs(share - 0.40) < margin:
        return 3
    if share < 0.40:
        return 2 if share >= 0.30 else 1 if share >= 0.15 else 0
    return 4 if share < 0.50 else 5 if share < 0.65 else 6


def compute_hybrid(view: ChartView, profile: SchoolProfile = DEFAULT, resolved: Resolved | None = None) -> dict:
    """strength_method == 'tvh_40': the vượng/nhược DECISION (and the level shown) come from the Thiệu Vĩ Hoa scoring and its 40% rule, which agrees
    with the book-labelled cases much better than this system's own weights (see tests/test_bazi_deep_fidelity.py). Group shares and element totals used by
    cách cục / tòng detection stay from the system's own computation (compute()), because the scoring method has no counterpart for them.
    The result says so in `method` and carries the full scoring under `tvh`."""
    from .tvh_score import score
    S = compute(view, profile, resolved)
    r = score(view)
    idx = _band(r["own_share"], profile.tvh_margin)
    S.update({"level": LEVELS[idx], "level_index": idx, "ambiguous": idx == 3, "readings": [LEVELS[idx]] if idx != 3 else [LEVELS[2], LEVELS[4]],
              "margin": round(abs(r["own_share"] - 0.40), 4), "ratio_system": S["ratio"], "ratio": r["own_share"], "tvh": r,
              "method": "tvh_40 (quyết định vượng/nhược) + hệ thống (tỉ trọng nhóm)", "src": "SRC_TVH_DIEM"})
    return S


def compute_tvh(view: ChartView, profile: SchoolProfile = DEFAULT, resolved: Resolved | None = None) -> dict:
    """Same output shape as compute(), but the element totals, the vượng/nhược decision and the group shares come from tvh_score (Thiệu Vĩ Hoa)."""
    from .tvh_score import score
    r = score(view)
    dm_el = r["dm_element"]
    tot = sum(r["totals"].values()) or 1.0
    by_group = {g: 0.0 for g in GROUPS}
    for e, v in r["totals"].items():
        by_group[group_of_element(dm_el, e)] += v
    states = season_states(view.month_branch)
    cmd = command(view, profile)
    idx = _band(r["own_share"], profile.tvh_margin)
    rs = roots(view, view.dm, profile, resolved.mult if resolved else {}, resolved.opened if resolved else set(), resolved.shifts if resolved else {}) if dm_el == view.dm_element else []
    vis_help = [i for i in (0, 1, 3) if group_of_element(dm_el, STEM_ELEMENT[view.stems[i]]) in ("Ti", "An") and r["stem_deg"][i] >= 18]
    an_share = by_group["An"] / tot
    ambiguous = idx == 3
    readings = [LEVELS[idx]] if not ambiguous else [LEVELS[2], LEVELS[4]]
    return {
        "dm_element": dm_el, "season_state": states[dm_el], "month_states": states, "command": cmd,
        "axes": {"de_lenh": {"vượng": "đắc lệnh", "tướng": "được lệnh sinh"}.get(states[dm_el], "thất lệnh"), "de_dia": root_grade(rs),
                 "de_the": "đông" if len(vis_help) >= 2 else "có" if vis_help else "không", "de_sinh": "mạnh" if an_share >= 0.25 else "có" if an_share >= 0.08 else "yếu/không"},
        "roots": rs, "by_group": {k: round(v, 3) for k, v in by_group.items()}, "by_element": {k: round(v, 3) for k, v in r["totals"].items()},
        "shares": {k: round(v / tot, 4) for k, v in by_group.items()}, "ratio": r["own_share"], "level": LEVELS[idx], "level_index": idx,
        "margin": round(abs(r["own_share"] - 0.40), 4), "ambiguous": ambiguous, "readings": readings, "top_contributions": [], "n_contrib": 0,
        "profile": profile.id, "method": "tvh_40", "tvh": r, "src": "SRC_TVH_DIEM",
    }
