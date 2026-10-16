"""Bộ giải tương tác Can Chi. detect() lists every raw interaction with its position; resolve() applies them in the
profile's fixed order (cục -> can hợp -> xung -> hình/hại/phá) and returns multipliers, element shifts and a step trace.
Single ordered pass, no iteration. Which interactions exist is `tinh_toan` (tables of 八字真宗 pp.19-20, golden-tested);
every effect size and the hóa conditions are `he_thong` and `draft` (see SchoolProfile)."""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product

from ..bazi import (DESTROY, HARM, MEETING, PENALTY_PAIR, PENALTY_TRIPLES, SELF_PENALTY, SIX_CLASH, SIX_COMBINE,
                    STEM_CLASH, STEM_COMBINE, TRIAD)
from ..ganzhi import BRANCHES_VI, BRANCH_ELEMENT, STEM_ELEMENT, STEMS_VI, controls
from .model import PIL_VI, PILLARS, ChartView
from .position import KHO, root_grade, roots
from .profile import DEFAULT, SchoolProfile
from .season import season_states

PAIR_TABLES = [("branch_six_combine", SIX_COMBINE), ("branch_clash", SIX_CLASH), ("branch_harm", HARM), ("branch_destroy", DESTROY)]
SEMI_KIND = {(0, 1): "sinh_vuong", (1, 2): "vuong_mo", (0, 2): "cung"}   # indexes into TRIAD tuples (sinh, vượng, mộ)


def _cid(p: str, kind: str) -> str:
    return f"{p}.{kind}"


def _best_assignment(view: ChartView, needed: tuple[int, ...]) -> list[str] | None:
    cands = [[p for p in PILLARS if view.branch(p) == b] for b in needed]
    if any(not c for c in cands):
        return None
    best = min(product(*cands), key=lambda t: (max(PILLARS.index(x) for x in t) - min(PILLARS.index(x) for x in t), [PILLARS.index(x) for x in t]))
    return list(best)


def detect(view: ChartView) -> list[dict]:
    """All raw interactions (no effect applied). `adjacent` = the members sit in neighbouring pillars (span 1)."""
    out: list[dict] = []

    def add(kind, members, pillars, **kw):
        idx = [PILLARS.index(p) for p in pillars]
        span = max(idx) - min(idx)
        out.append({"id": f"I{len(out) + 1}", "kind": kind, "members": members, "pillars": pillars, "span": span, "adjacent": span == 1, **kw})

    for i in range(4):
        for j in range(i + 1, 4):
            a, b = PILLARS[i], PILLARS[j]
            ps = frozenset((view.stem(a), view.stem(b)))
            if ps in STEM_COMBINE:
                add("stem_combine", [_cid(a, "stem"), _cid(b, "stem")], [a, b], element=STEM_COMBINE[ps])
            if ps in STEM_CLASH:
                add("stem_clash", [_cid(a, "stem"), _cid(b, "stem")], [a, b])
            pb = frozenset((view.branch(a), view.branch(b)))
            for kind, tbl in PAIR_TABLES:
                if pb in tbl:
                    add(kind, [_cid(a, "branch"), _cid(b, "branch")], [a, b])
            if pb == PENALTY_PAIR:
                add("branch_penalty", [_cid(a, "branch"), _cid(b, "branch")], [a, b], subtype="vo_le")
            if view.branch(a) == view.branch(b) and view.branch(a) in SELF_PENALTY:
                add("branch_self_penalty", [_cid(a, "branch"), _cid(b, "branch")], [a, b])
    for el, tri in TRIAD.items():
        asg = _best_assignment(view, tri)
        if asg:
            add("branch_triad", [_cid(p, "branch") for p in asg], asg, element=el)
        else:
            for (x, y), sub in SEMI_KIND.items():
                pa = _best_assignment(view, (tri[x], tri[y]))
                if pa:
                    add("branch_semi_triad", [_cid(p, "branch") for p in pa], pa, element=el, subtype=sub)
    for el, tri in MEETING.items():
        asg = _best_assignment(view, tri)
        if asg:
            add("branch_meeting", [_cid(p, "branch") for p in asg], asg, element=el)
    for name, tri in PENALTY_TRIPLES.items():
        asg = _best_assignment(view, tri)
        if asg:
            add("branch_penalty", [_cid(p, "branch") for p in asg], asg, subtype=name)
        else:
            for x, y in ((0, 1), (1, 2), (0, 2)):
                pa = _best_assignment(view, (tri[x], tri[y]))
                if pa:
                    add("branch_penalty", [_cid(p, "branch") for p in pa], pa, subtype=f"ban_hinh_{name}")
    return out


def stem_controls(view: ChartView) -> list[dict]:
    """Directed khắc between heavenly stems (any distance, with adjacency)."""
    out = []
    for a in PILLARS:
        for b in PILLARS:
            if a != b and controls(STEM_ELEMENT[view.stem(a)], STEM_ELEMENT[view.stem(b)]):
                d = ChartView.dist(a, b)
                out.append({"from": _cid(a, "stem"), "to": _cid(b, "stem"), "dist": d, "adjacent": d == 1})
    return out


@dataclass
class Resolved:
    interactions: list[dict]
    mult: dict[str, float] = field(default_factory=dict)
    shifts: dict[str, tuple[str, float]] = field(default_factory=dict)       # branch char -> (element, share)
    stem_element: dict[str, str] = field(default_factory=dict)                # hóa chân: stem char -> new element
    opened: set[str] = field(default_factory=set)                              # pillars whose khố was opened
    cuc: list[dict] = field(default_factory=list)
    steps: list[dict] = field(default_factory=list)
    dm_element: str = ""
    dm_hua: str | None = None


def _hua_conditions(view: ChartView, rec: dict, raw: list[dict], profile: SchoolProfile) -> tuple[list[str], list[str], dict]:
    """Seven draft conditions for a real transformation (hóa). Returns (met, unmet, evidence)."""
    el = rec["element"]
    a, b = rec["pillars"]
    met, unmet, ev = [], [], {}

    def chk(name, ok, why=""):
        (met if ok else unmet).append(name)
        ev[name] = why

    chk("ke_sat", rec["adjacent"] or not profile.hua_requires_adjacent, f"{PIL_VI[a]}–{PIL_VI[b]}")
    chk("dac_lenh", BRANCH_ELEMENT[view.month_branch] == el, f"chi tháng {BRANCHES_VI[view.month_branch]} hành {BRANCH_ELEMENT[view.month_branch]}")
    pair_pils = set(rec["pillars"])
    others = [(p, view.stem(p)) for p in PILLARS if p not in pair_pils]
    thau = [p for p, s in others if STEM_ELEMENT[s] == el]
    base = [p for p in PILLARS if BRANCH_ELEMENT[view.branch(p)] == el]
    chk("hoa_than_co_can", bool(base) or bool(thau), f"chi cùng hành {el}: {[PIL_VI[p] for p in base]}; thấu: {[PIL_VI[p] for p in thau]}")
    killers = [p for p, s in others if controls(STEM_ELEMENT[s], el)]
    chk("khong_bi_khac", not killers, f"thiên can khắc {el}: {[PIL_VI[p] for p in killers]}")
    chk("khong_tranh_hop", not any(r is not rec and r["kind"] == "stem_combine" and set(r["members"]) & set(rec["members"]) for r in raw), "")
    weak = []
    for m in rec["members"]:
        s = view.stem(m.split(".")[0])
        if STEM_ELEMENT[s] != el and root_grade(roots(view, s, profile)) == "mạnh":
            weak.append(STEMS_VI[s])
    chk("khong_co_can_manh_cua_hanh_goc", not weak, f"có căn mạnh: {weak}")
    lenh_hit = [r for r in raw if "month.branch" in r["members"] and r["adjacent"] and r["kind"] in ("branch_clash", "branch_penalty", "branch_self_penalty")]
    chk("lenh_khong_bi_pha", not lenh_hit, f"nguyệt lệnh bị: {[r['kind'] for r in lenh_hit]}")
    return met, unmet, ev


def resolve(view: ChartView, profile: SchoolProfile = DEFAULT, raw: list[dict] | None = None) -> Resolved:
    raw = raw if raw is not None else detect(view)
    R = Resolved([dict(r) for r in raw])
    ints = R.interactions
    R.dm_element = view.dm_element
    states = season_states(view.month_branch)

    def mul(cid: str, f: float, why: str):
        R.mult[cid] = max(0.2, round(R.mult.get(cid, 1.0) * f, 4))
        R.steps.append({"effect": "mult", "char": cid, "factor": f, "why": why})

    for stage in profile.interact_order:
        if stage == "cuc":
            _stage_cuc(view, profile, R, mul)
        elif stage == "stem_combine":
            _stage_stem_combine(view, profile, R, raw, mul)
        elif stage == "clash":
            _stage_clash(view, profile, R, states, mul)
        elif stage == "xing_hai_po":
            _stage_light(view, profile, R, mul)
    return R


def _by_kind(R: Resolved, *kinds):
    return [r for r in R.interactions if r["kind"] in kinds]


def _stage_cuc(view, profile, R, mul):
    used: dict[str, str] = {}
    units = []
    for r in _by_kind(R, "branch_meeting"):
        units.append((0, r, "meeting"))
    for r in _by_kind(R, "branch_triad"):
        units.append((1, r, "triad"))
    for r in _by_kind(R, "branch_semi_triad"):
        units.append((2 if r["subtype"] != "cung" else 3, r, "semi" if r["subtype"] != "cung" else "cung"))
    for r in _by_kind(R, "branch_six_combine"):
        units.append((4, r, "luhe"))
    units.sort(key=lambda u: (u[0], u[1]["span"], u[1]["id"]))
    stems = {STEM_ELEMENT[view.stem(p)] for p in PILLARS if p != "day"}
    for _, r, ukind in units:
        if ukind in ("semi", "cung") and r["span"] > 2:
            r["status"] = "xa"
            continue
        if ukind == "luhe" and not r["adjacent"]:
            r["status"] = "khong_ke"
            continue
        taken = [m for m in r["members"] if m in used]
        if taken:
            r["status"] = "bi_tranh"
            r["taken_by"] = sorted({used[m] for m in taken})
            continue
        r["status"] = "formed"
        for m in r["members"]:
            used[m] = r["id"]
        if ukind == "luhe":
            for m in r["members"]:
                mul(m, profile.luhe_mult, f"lục hợp {r['id']} (hợp mà không hóa)")
            continue
        thau = r["element"] in stems
        share = profile.cuc_share[ukind] + (profile.cuc_thau_bonus if thau else 0.0)
        r["thau"] = thau
        r["share"] = round(share, 3)
        R.cuc.append({"id": r["id"], "kind": r["kind"], "subtype": r.get("subtype"), "element": r["element"], "members": r["members"], "share": r["share"], "thau": thau})
        for m in r["members"]:
            R.shifts[m] = (r["element"], share)
        R.steps.append({"effect": "cuc", "interaction": r["id"], "element": r["element"], "share": r["share"], "thau": thau})


def _stage_stem_combine(view, profile, R, raw, mul):
    combos = _by_kind(R, "stem_combine")
    for r in combos:
        partners = [o for o in combos if o is not r and set(o["members"]) & set(r["members"])]
        if not r["adjacent"] and profile.hua_requires_adjacent:
            r["status"] = "khong_ke"
            continue
        if partners:
            r["status"] = "tranh_hop"
            for m in r["members"]:
                mul(m, profile.tranh_hop_mult, f"tranh hợp {r['id']}")
            continue
        met, unmet, ev = _hua_conditions(view, r, raw, profile)
        r["hua_met"], r["hua_unmet"], r["hua_evidence"] = met, unmet, ev
        if not unmet:
            r["status"] = "chan_hoa"
            for m in r["members"]:
                R.stem_element[m] = r["element"]
            if "day.stem" in r["members"]:
                R.dm_hua = r["element"]
                R.dm_element = r["element"]
            R.steps.append({"effect": "hoa", "interaction": r["id"], "element": r["element"], "state": "chan_hoa"})
        elif {"ke_sat", "dac_lenh"} <= set(met) and len(unmet) <= 2:
            r["status"] = "gia_hoa"
            for m in r["members"]:
                mul(m, profile.gia_hoa_mult, f"giả hóa {r['id']}: thiếu {unmet}")
        else:
            r["status"] = "hop_khong_hoa"
            for m in r["members"]:
                mul(m, profile.bound_mult, f"hợp trói {r['id']}: thiếu {unmet}")


def _raw_strength(view, profile, states, p):
    return profile.pos_weight_branch[p] * profile.season_factor[states[BRANCH_ELEMENT[view.branch(p)]]]


def _stage_clash(view, profile, R, states, mul):
    cuc_of = {m: u for u in R.cuc for m in u["members"]}
    luhe = [r for r in _by_kind(R, "branch_six_combine") if r.get("status") == "formed"]
    for r in _by_kind(R, "stem_clash"):
        f = profile.stem_clash_adj if r["adjacent"] else profile.stem_clash_far
        r["status"] = "xung_ke" if r["adjacent"] else "xung_xa"
        for m in r["members"]:
            mul(m, f, f"can xung {r['id']}")
    for r in _by_kind(R, "branch_clash"):
        m1, m2 = r["members"]
        p1, p2 = r["pillars"]
        for p in r["pillars"]:
            if view.branch(p) in KHO and (r["adjacent"] or True):
                R.opened.add(p)
        hits = [(m, cuc_of[m]) for m in r["members"] if m in cuc_of]
        if len(hits) == 1:
            m, u = hits[0]
            other = m2 if m == m1 else m1
            if r["adjacent"]:
                old = R.shifts[m][1]
                for mm in u["members"]:
                    el, sh = R.shifts[mm]
                    R.shifts[mm] = (el, round(sh * 0.5, 3))
                mul(other, 0.8, f"xung vào cục {u['id']}")
                r["status"] = "xung_vao_cuc"
                R.steps.append({"effect": "cuc_halved", "interaction": u["id"], "by": r["id"], "share_before": old})
            else:
                r["status"] = "xung_xa_cuc"
                mul(other, profile.clash_far, f"xung xa cục {u['id']}")
            continue
        hop = next((h for h in luhe if set(h["members"]) & {m1, m2}), None)
        if hop is not None:
            if not r["adjacent"]:
                r["status"] = "hop_giai_xung"
                continue
            r["status"] = "giang_co"
            for m in r["members"]:
                mul(m, 0.8, f"giằng co hợp–xung {hop['id']}/{r['id']}")
            continue
        if not r["adjacent"]:
            r["status"] = "xung_xa"
            for m in r["members"]:
                mul(m, profile.clash_far, f"xung cách vị {r['id']}")
            continue
        s1, s2 = _raw_strength(view, profile, states, p1), _raw_strength(view, profile, states, p2)
        weak_f, strong_f, tie_f = profile.clash_adj
        if abs(s1 - s2) <= 0.05 * max(s1, s2):
            r["status"] = "xung_can_bang"
            mul(m1, tie_f, f"xung kề cân bằng {r['id']}"); mul(m2, tie_f, f"xung kề cân bằng {r['id']}")
        else:
            weak, strong = (m1, m2) if s1 < s2 else (m2, m1)
            r["status"] = "xung_nho"
            r["weaker"] = weak
            mul(weak, weak_f, f"vượng xung suy: {r['id']}"); mul(strong, strong_f, f"vượng xung suy: {r['id']}")


def _stage_light(view, profile, R, mul):
    for r in _by_kind(R, "branch_penalty", "branch_self_penalty", "branch_harm", "branch_destroy"):
        touches = any(m.split(".")[0] in profile.light_scope for m in r["members"])
        full = r["kind"] == "branch_penalty" and r.get("subtype") in ("vô ân", "thị thế")
        if not (r["adjacent"] or full):
            r["status"] = "xa"
            continue
        if not touches and not full:
            r["status"] = "ghi_nhan"
            continue
        f = (profile.penalty_full if full else profile.penalty_adj if r["kind"] in ("branch_penalty", "branch_self_penalty") else profile.harm_destroy_adj)
        r["status"] = "co_hieu_luc"
        for m in r["members"]:
            mul(m, f, f"{r['kind']} {r['id']}")
        if r["kind"] == "branch_penalty":
            for p in r["pillars"]:
                if view.branch(p) in KHO and r["adjacent"]:
                    R.opened.add(p)
