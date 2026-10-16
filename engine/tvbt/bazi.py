"""Bát Tự (Tứ Trụ) calculation. Produces FACTS only: pillars, hidden stems, ten gods, twelve
growth stages, luck pillars, and raw stem/branch relations. No interpretation, no 'hóa' claims."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

import sxtwl

from . import astro
from .calendar_core import NormalizedBirth
from .ganzhi import (BRANCHES_VI, ELEMENTS, STEM_ELEMENT, STEMS_VI, controls, cycle_index, from_cycle,
                     generates, gz_name, stem_polarity, tiger_month_stem)
from .trace import Trace

HIDDEN_STEMS = {  # 藏干: main, middle, residual
    0: [9], 1: [5, 9, 7], 2: [0, 2, 4], 3: [1], 4: [4, 1, 9], 5: [2, 6, 4],
    6: [3, 5], 7: [5, 3, 1], 8: [6, 8, 4], 9: [7], 10: [4, 7, 3], 11: [8, 0],
}
STAGES = ["Trường Sinh", "Mộc Dục", "Quan Đới", "Lâm Quan", "Đế Vượng", "Suy", "Bệnh", "Tử", "Mộ",
          "Tuyệt", "Thai", "Dưỡng"]
GROWTH_START = {0: 11, 2: 2, 4: 2, 6: 5, 8: 8, 1: 6, 3: 9, 5: 9, 7: 0, 9: 3}  # yin start = yin_reverse school

STEM_COMBINE = {frozenset((0, 5)): "Thổ", frozenset((1, 6)): "Kim", frozenset((2, 7)): "Thủy",
                frozenset((3, 8)): "Mộc", frozenset((4, 9)): "Hỏa"}
STEM_CLASH = [frozenset((0, 6)), frozenset((1, 7)), frozenset((2, 8)), frozenset((3, 9))]
SIX_COMBINE = [frozenset(p) for p in [(0, 1), (2, 11), (3, 10), (4, 9), (5, 8), (6, 7)]]
SIX_CLASH = [frozenset((i, i + 6)) for i in range(6)]
HARM = [frozenset(p) for p in [(0, 7), (1, 6), (2, 5), (3, 4), (8, 11), (9, 10)]]
DESTROY = [frozenset(p) for p in [(0, 9), (1, 4), (2, 11), (3, 6), (5, 8), (7, 10)]]
TRIAD = {"Thủy": (8, 0, 4), "Mộc": (11, 3, 7), "Hỏa": (2, 6, 10), "Kim": (5, 9, 1)}
MEETING = {"Mộc": (2, 3, 4), "Hỏa": (5, 6, 7), "Kim": (8, 9, 10), "Thủy": (11, 0, 1)}
PENALTY_TRIPLES = {"vô ân": (2, 5, 8), "thị thế": (1, 10, 7)}
PENALTY_PAIR = frozenset((0, 3))
SELF_PENALTY = {4, 6, 9, 11}


def ten_god(day_stem: int, other: int) -> str:
    de, oe = STEM_ELEMENT[day_stem], STEM_ELEMENT[other]
    same = stem_polarity(day_stem) == stem_polarity(other)
    if de == oe:
        return "Tỉ Kiên" if same else "Kiếp Tài"
    if generates(de, oe):
        return "Thực Thần" if same else "Thương Quan"
    if controls(de, oe):
        return "Thiên Tài" if same else "Chính Tài"
    if controls(oe, de):
        return "Thất Sát" if same else "Chính Quan"
    return "Thiên Ấn" if same else "Chính Ấn"


def growth_stage(stem: int, branch: int) -> str:
    start = GROWTH_START[stem]
    step = 1 if stem % 2 == 0 else -1
    return STAGES[((branch - start) * step) % 12]


@dataclass
class Pillar:
    stem: int
    branch: int
    name: str
    hidden: list[dict]            # [{stem, name, element, ten_god}]
    stem_ten_god: str | None      # None for day master
    stage_vs_day_master: str


@dataclass
class LuckPillar:
    index: int
    stem: int
    branch: int
    name: str
    start_age: float
    start_year_approx: float
    ten_god: str


@dataclass
class BaziChart:
    pillars: dict[str, Pillar]
    day_master: int
    day_master_element: str
    luck_direction: str
    luck_start: dict
    luck_pillars: list[LuckPillar]
    relations: dict
    jie_used: dict
    trace: Trace
    school: dict


def _jie_instants(year: int):
    """Sorted (jqIndex, utc_jd) for jie (odd) terms plus lichun marker, spanning year-1..year+1."""
    return [(i, jd) for i, jd in astro.all_terms_around(year) if i % 2 == 1]


def _pillar(day_stem: int, stem: int, branch: int, is_dm: bool) -> Pillar:
    hidden = [{"stem": h, "name": STEMS_VI[h], "element": STEM_ELEMENT[h], "ten_god": ten_god(day_stem, h)}
              for h in HIDDEN_STEMS[branch]]
    return Pillar(stem, branch, gz_name(stem, branch), hidden,
                  None if is_dm else ten_god(day_stem, stem), growth_stage(day_stem, branch))


def _relations(pillars: dict[str, Pillar]) -> dict:
    keys = list(pillars)
    rel: dict[str, list] = {k: [] for k in ["stem_combine", "stem_clash", "branch_six_combine",
                                             "branch_clash", "branch_harm", "branch_destroy",
                                             "branch_triad_complete", "branch_meeting_complete",
                                             "branch_penalty", "branch_self_penalty"]}
    for i in range(4):
        for j in range(i + 1, 4):
            a, b = pillars[keys[i]], pillars[keys[j]]
            pair_s, pair_b = frozenset((a.stem, b.stem)), frozenset((a.branch, b.branch))
            where = f"{keys[i]}-{keys[j]}"
            if pair_s in STEM_COMBINE:
                rel["stem_combine"].append({"pillars": where, "stems": [a.stem, b.stem],
                                            "potential_element": STEM_COMBINE[pair_s], "transforms": None})
            if pair_s in STEM_CLASH:
                rel["stem_clash"].append({"pillars": where, "stems": [a.stem, b.stem]})
            for key, table in [("branch_six_combine", SIX_COMBINE), ("branch_clash", SIX_CLASH),
                               ("branch_harm", HARM), ("branch_destroy", DESTROY)]:
                if pair_b in table:
                    rel[key].append({"pillars": where, "branches": [a.branch, b.branch]})
            if pair_b == PENALTY_PAIR:
                rel["branch_penalty"].append({"kind": "vô lễ", "pillars": where})
            if a.branch == b.branch and a.branch in SELF_PENALTY:
                rel["branch_self_penalty"].append({"pillars": where, "branch": a.branch})
    present = {p.branch: k for k, p in pillars.items()}
    for el, tri in TRIAD.items():
        if all(b in present for b in tri):
            rel["branch_triad_complete"].append({"element": el, "branches": list(tri)})
    for el, tri in MEETING.items():
        if all(b in present for b in tri):
            rel["branch_meeting_complete"].append({"element": el, "branches": list(tri)})
    for kind, tri in PENALTY_TRIPLES.items():
        if all(b in present for b in tri):
            rel["branch_penalty"].append({"kind": kind, "branches": list(tri)})
    return rel


def compute(nb: NormalizedBirth, n_luck: int = 10) -> BaziChart:
    tr = Trace()
    b = nb.input
    birth_jd = astro.utc_to_jd(nb.utc)
    jie = sorted(_jie_instants(nb.utc.year), key=lambda t: t[1])
    lichun = [(i, jd) for i, jd in jie if i == 3]

    # Year pillar: latest Lichun at or before the instant of birth
    ly_jd = max(jd for _, jd in lichun if jd <= birth_jd)
    bazi_year = astro.jd_to_utc(ly_jd).astimezone(astro.BEIJING).year
    y_idx = (bazi_year - 4) % 60
    ys, yb = from_cycle(y_idx)
    tr.add("bazi.year", "Year pillar changes at the instant of Lập Xuân (not 1 Jan / Tet)",
           {"birth_utc": nb.utc.isoformat(), "lichun_utc": astro.jd_to_utc(ly_jd).isoformat()},
           {"bazi_year": bazi_year, "pillar": gz_name(ys, yb)}, rule="tu_binh_lichun_year")

    # Month pillar: latest jie at or before birth
    prev_idx, prev_jd = max(((i, jd) for i, jd in jie if jd <= birth_jd), key=lambda t: t[1])
    mb = ((prev_idx + 1) // 2) % 12
    ms = (tiger_month_stem(ys) + (mb - 2) % 12) % 10
    tr.add("bazi.month", "Month pillar from the latest jie (節); stem via ngũ hổ độn",
           {"jie_index": prev_idx, "jie_utc": astro.jd_to_utc(prev_jd).isoformat(), "year_stem": STEMS_VI[ys]},
           gz_name(ms, mb), rule="five_tigers_rule")

    # Day pillar from the rule date
    sd = sxtwl.fromSolar(nb.rule_date.year, nb.rule_date.month, nb.rule_date.day).getDayGZ()
    ds, db = sd.tg, sd.dz
    tr.add("bazi.day", "Day pillar from sxtwl for the Zi-rule date", {"date": nb.rule_date.isoformat()},
           gz_name(ds, db), rule="sxtwl_day_gz")

    # Hour pillar from clock hour; stem via ngũ thử độn from the day stem
    hb = ((nb.clock.hour + 1) // 2) % 12
    hs = (ds % 5 * 2 + hb) % 10
    tr.add("bazi.hour", "Hour pillar: branch from clock hour, stem via ngũ thử độn",
           {"clock_hour": nb.clock.hour, "day_stem": STEMS_VI[ds], "zi_rule": b.zi_rule}, gz_name(hs, hb),
           rule="five_rats_rule")

    pillars = {
        "year": _pillar(ds, ys, yb, False), "month": _pillar(ds, ms, mb, False),
        "day": _pillar(ds, ds, db, True), "hour": _pillar(ds, hs, hb, False),
    }

    # Luck pillars
    forward = (stem_polarity(ys) == "dương") == (b.gender == "male")
    if forward:
        tgt = min((jd for i, jd in jie if jd > birth_jd))
        tgt_idx = next(i for i, jd in jie if jd == tgt)
    else:
        tgt, tgt_idx = prev_jd, prev_idx
    days = abs(tgt - birth_jd)
    age = days / 3.0  # 3 days = 1 year (so 1 day = 4 months, 2 hours = 10 days)
    yrs = int(age)
    rem_months = (age - yrs) * 12
    mons = int(rem_months)
    dys = round((rem_months - mons) * 30, 1)
    tr.add("bazi.luck.start", "Khởi vận: distance to the adjacent jie / 3 days per year",
           {"direction": "thuận" if forward else "nghịch", "target_jie_index": tgt_idx,
            "target_jie_utc": astro.jd_to_utc(tgt).isoformat(), "days": round(days, 4)},
           {"age_years": round(age, 4), "years": yrs, "months": mons, "days": dys},
           rule="three_days_one_year")
    luck = []
    m_idx = cycle_index(ms, mb)
    for k in range(1, n_luck + 1):
        s, br = from_cycle((m_idx + (k if forward else -k)) % 60)
        sa = age + 10 * (k - 1)
        luck.append(LuckPillar(k, s, br, gz_name(s, br), round(sa, 3),
                               round(nb.local.year + sa, 2), ten_god(ds, s)))
    chart = BaziChart(
        pillars=pillars, day_master=ds, day_master_element=STEM_ELEMENT[ds],
        luck_direction="thuận" if forward else "nghịch",
        luck_start={"years": yrs, "months": mons, "days": dys, "age_years": round(age, 4)},
        luck_pillars=luck, relations=_relations(pillars),
        jie_used={"prev_jie_index": prev_idx, "prev_jie_utc": astro.jd_to_utc(prev_jd).isoformat()},
        trace=tr,
        school={"year_boundary": "lichun_instant", "month_boundary": "jie_instant",
                "growth_yin": "yin_reverse", "luck_conversion": "3_days_per_year",
                "zi_rule": b.zi_rule, "review_status": "unverified"},
    )
    return chart
