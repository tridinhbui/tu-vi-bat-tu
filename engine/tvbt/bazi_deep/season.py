"""Tầng Khí: vượng–tướng–hưu–tù–tử theo nguyệt lệnh, nhân nguyên tư lệnh, hàn–nhiệt."""
from __future__ import annotations

from ..ganzhi import BRANCHES_VI, BRANCH_ELEMENT, ELEMENTS, STEMS_VI, STEM_ELEMENT, controls, generates
from .model import ChartView
from .profile import DEFAULT, SchoolProfile


def season_states(branch: int) -> dict[str, str]:
    """State of each of the five elements in the month of `branch` (generic rule: vượng = element of the month;
    tướng = element it generates; hưu = element that generates it; tù = element that controls it; tử = element it controls)."""
    v = BRANCH_ELEMENT[branch]
    out = {v: "vượng"}
    for e in ELEMENTS:
        if e == v:
            continue
        out[e] = ("tướng" if generates(v, e) else "hưu" if generates(e, v) else "tù" if controls(e, v) else "tử")
    return out


def command(view: ChartView, profile: SchoolProfile = DEFAULT) -> dict | None:
    """Stem 'in command' (tư lệnh) at the birth moment, or None when days-into-month is unknown / the profile does not use it."""
    if not profile.use_tu_lenh or view.days_into_month is None:
        return None
    rows = profile.tu_lenh_rows().get(BRANCHES_VI[view.month_branch])
    if not rows:                     # a verified table may cover only some months (ttt_ntt_v1 has only tháng Dần)
        return None
    d, acc = view.days_into_month, 0.0
    for i, (st, n) in enumerate(rows):
        acc += n
        if d < acc or i == len(rows) - 1:
            stem = STEMS_VI.index(st)
            from ..bazi import HIDDEN_STEMS
            return {"stem": stem, "name": st, "element": STEM_ELEMENT[stem], "day_in_month": round(d, 2), "segment": i,
                    "in_hidden_stems": stem in HIDDEN_STEMS[view.month_branch], "table": profile.tu_lenh_table,
                    "near_boundary": min(abs(d - (acc - n)), abs(d - acc)) < 1.0}
    return None


# --- hàn nhiệt (coarse, he_thong): base from month, shifted by relative Hỏa/Thủy strength supplied by the caller
HEAT_BASE = {"Tý": -2, "Sửu": -1, "Hợi": -1, "Dần": 0, "Mão": 0, "Thìn": 0, "Tỵ": 1, "Ngọ": 2, "Mùi": 1, "Thân": 0, "Dậu": 0, "Tuất": 0}


def climate(view: ChartView, element_totals: dict[str, float]) -> dict:
    base = HEAT_BASE[BRANCHES_VI[view.month_branch]]
    tot = sum(element_totals.values()) or 1.0
    adj = round((element_totals.get("Hỏa", 0) - element_totals.get("Thủy", 0)) / tot * 3, 2)
    heat = base + adj
    label = "cực hàn" if heat <= -2 else "hàn" if heat <= -1 else "cực nhiệt" if heat >= 2.5 else "nhiệt" if heat >= 1.5 else "ôn hòa"
    return {"base": base, "adjust": adj, "heat": round(heat, 2), "label": label, "moist": None,
            "note": "chỉ số nhiệt thô (he_thong, draft); độ ẩm/táo chưa được tính"}
