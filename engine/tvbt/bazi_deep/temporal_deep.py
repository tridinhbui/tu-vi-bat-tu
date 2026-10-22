"""Cục mở rộng (BZ-71–78): nguyên cục + đại vận + lưu niên (+ lưu nguyệt). Không viết lại các analyzer: một trụ vận/niên/nguyệt
được đặt lên nguyên cục dưới dạng (a) tương tác với từng chữ nguyên cục, (b) thêm sức vào khí thế, (c) thêm chữ thấu cho cách cục.
Sau đó chạy lại khí thế, cách cục, cấu trúc thập thần và dụng thần, rồi so với nguyên cục.
Quy ước hệ thống (draft, trong SchoolProfile): trụ vận/niên/nguyệt tác động lên toàn lá số nên coi là kề mọi trụ nguyên cục;
mùa lấy theo nguyệt lệnh nguyên cục; hợp với trụ vận chỉ được xem là 'trói' (không xét hóa)."""
from __future__ import annotations

import copy

from .interact import CALIBRATED_STEM_CLASH
from ..bazi import (DESTROY, HARM, HIDDEN_STEMS, MEETING, PENALTY_PAIR, SELF_PENALTY, SIX_CLASH, SIX_COMBINE, STEM_CLASH_KIND as STEM_CLASH, STEM_COMBINE, TRIAD)
from ..ganzhi import BRANCHES_VI, BRANCH_ELEMENT, STEM_ELEMENT, STEMS_VI, controls, generates, gz_name, tiger_month_stem
from . import geju, interact, patterns, strength, yongshen
from .model import PILLARS, ChartView, group_of
from .position import KHO
from .profile import DEFAULT, SchoolProfile
from .season import season_states

STATE_RANK = {"thanh": 5, "bai_co_cuu": 4, "thanh_nhung_bi_pha": 3, "bai_cuu_yeu": 3, "chua_ro": 2, "bai": 1, "khong_xac_dinh": 0}
ROLE_GROUP = {"Quan": "QuanSat", "Sat": "QuanSat", "Thuc": "ThucThuong", "Thuong": "ThucThuong"}


def tp(label: str, stem: int, branch: int) -> dict:
    if stem % 2 != branch % 2:
        raise ValueError("stem/branch parity")
    return {"label": label, "stem": stem, "branch": branch, "name": gz_name(stem, branch)}


def _pair(a: int, b: int, table) -> bool:
    return frozenset((a, b)) in table


def overlay(view: ChartView, profile: SchoolProfile, R, pillars: list[dict]):
    """Returns (R2, extras, extra_stems, events). R2 is a deep copy of the natal resolution with the temporal effects applied."""
    R2 = copy.deepcopy(R)
    events, extras, extra_stems = [], [], []
    states = season_states(view.month_branch)
    tmult: dict[str, float] = {}
    tshift: dict[str, tuple[str, float]] = {}
    natal_b = {view.branch(p): p for p in PILLARS}

    def ev(kind, label, with_, status, **kw):
        events.append({"kind": kind, "from": label, "with": with_, "status": status, **kw})

    def hit(p, cid, factor, why):
        R2.mult[cid] = max(0.2, round(R2.mult.get(cid, 1.0) * factor, 4))
        R2.steps.append({"effect": "mult", "char": cid, "factor": factor, "why": why})

    for T in pillars:
        lab, ts, tb = T["label"], T["stem"], T["branch"]
        cs, cb = f"{lab}.stem", f"{lab}.branch"
        extra_stems.append((cs, lab, ts, tb))
        for p in PILLARS:
            ns, nb = view.stem(p), view.branch(p)
            if frozenset((ts, ns)) in STEM_COMBINE:
                st = "hop_khong_hoa"                       # hóa is not evaluated for temporal pillars: treated as binding
                ev("stem_combine", lab, f"{p}.stem", st, note="không xét hóa với trụ vận/niên")
                R2.interactions.append({"id": f"T{len(R2.interactions)+1}", "kind": "stem_combine", "members": [f"{p}.stem", cs], "pillars": [p, lab], "span": 1, "adjacent": True, "status": st})
                if p != "day":
                    hit(p, f"{p}.stem", profile.bound_mult, f"{lab} hợp {p}")
                tmult[cs] = tmult.get(cs, 1.0) * profile.bound_mult
            if frozenset((ts, ns)) in STEM_CLASH:
                calibrated = frozenset((ts, ns)) in CALIBRATED_STEM_CLASH
                ev("stem_clash", lab, f"{p}.stem", "xung_ke" if calibrated else "ghi_nhan", subtype=STEM_CLASH[frozenset((ts, ns))])
                if p != "day" and calibrated:
                    hit(p, f"{p}.stem", profile.stem_clash_adj, f"{lab} xung {p}")
            if ts == ns and tb == nb:
                ev("phuc_ngam", lab, p, "phuc_ngam")
            if _pair(ts, ns, STEM_CLASH) and _pair(tb, nb, SIX_CLASH):
                ev("phan_ngam", lab, p, "phan_ngam")
            if _pair(tb, nb, SIX_COMBINE):
                ev("branch_six_combine", lab, f"{p}.branch", "formed")
                hit(p, f"{p}.branch", profile.luhe_mult, f"{lab} hợp {p}")
                tmult[cb] = tmult.get(cb, 1.0) * profile.luhe_mult
            if _pair(tb, nb, SIX_CLASH):
                opens = nb in KHO
                ev("branch_clash", lab, f"{p}.branch", "xung_kich", opens_kho=opens)
                R2.interactions.append({"id": f"T{len(R2.interactions)+1}", "kind": "branch_clash", "members": [f"{p}.branch", cb], "pillars": [p, lab], "span": 1, "adjacent": True, "status": "xung_nho"})
                hit(p, f"{p}.branch", profile.temporal_clash, f"{lab} xung {p}")
                tmult[cb] = tmult.get(cb, 1.0) * 0.9
                if opens:
                    R2.opened.add(p)
            light = p in profile.light_scope
            if tb == nb and tb in SELF_PENALTY or frozenset((tb, nb)) == PENALTY_PAIR:
                ev("branch_penalty", lab, f"{p}.branch", "co_hieu_luc" if light else "ghi_nhan")
                R2.interactions.append({"id": f"T{len(R2.interactions)+1}", "kind": "branch_penalty", "members": [f"{p}.branch", cb], "pillars": [p, lab], "span": 1, "adjacent": True, "status": "co_hieu_luc" if light else "ghi_nhan"})
                if light:
                    hit(p, f"{p}.branch", profile.penalty_adj, f"{lab} hình {p}")
            elif _pair(tb, nb, HARM) or _pair(tb, nb, DESTROY):
                ev("branch_harm_destroy", lab, f"{p}.branch", "co_hieu_luc" if light else "ghi_nhan")
                if light:
                    hit(p, f"{p}.branch", profile.harm_destroy_adj, f"{lab} hại/phá {p}")
        # completions of tam hợp / tam hội / bán hợp using the temporal branch as the missing member
        for kind, table in (("branch_triad", TRIAD), ("branch_meeting", MEETING)):
            for el, tri in table.items():
                if tb in tri:
                    others = [x for x in tri if x != tb]
                    if all(o in natal_b for o in others):
                        share = profile.cuc_share["triad" if kind == "branch_triad" else "meeting"]
                        ev(kind, lab, [f"{natal_b[o]}.branch" for o in others], "hoan_thanh_cuc", element=el, share=share)
                        tshift[cb] = (el, share)
                        for o in others:
                            cur = R2.shifts.get(f"{natal_b[o]}.branch")
                            if not cur or cur[1] < share:
                                R2.shifts[f"{natal_b[o]}.branch"] = (el, share)
        for el, tri in TRIAD.items():
            if tb in tri:
                idx = tri.index(tb)
                for j in range(3):
                    if j != idx and tri[j] in natal_b and (idx, j) in ((0, 1), (1, 0), (1, 2), (2, 1)) and cb not in tshift:
                        other = tri[j]
                        if all(x in natal_b for x in tri if x != tb):      # the full completion above already handled it
                            continue
                        share = profile.cuc_share["semi"]
                        ev("branch_semi_triad", lab, f"{natal_b[other]}.branch", "ban_hop", element=el, share=share)
                        tshift[cb] = (el, share)
                        cur = R2.shifts.get(f"{natal_b[other]}.branch")
                        if not cur or cur[1] < share:
                            R2.shifts[f"{natal_b[other]}.branch"] = (el, share)
        # contributions to the strength
        sw, bw = profile.temporal_weight[lab]
        el = STEM_ELEMENT[ts]
        extras.append({"char": cs, "element": el, "weight": sw * tmult.get(cs, 1.0) * profile.season_factor[states[el]], "note": f"thiên can {lab}"})
        hid = HIDDEN_STEMS[tb]
        fr = profile.hidden_frac[len(hid)]
        sh = tshift.get(cb)
        keep = 1.0 - (sh[1] if sh else 0.0)
        for i, h in enumerate(hid):
            e2 = STEM_ELEMENT[h]
            extras.append({"char": cb, "element": e2, "weight": bw * fr[i] * keep * tmult.get(cb, 1.0) * profile.season_factor[states[e2]], "note": f"tàng can {STEMS_VI[h]} ({lab})"})
        if sh:
            extras.append({"char": cb, "element": sh[0], "weight": bw * sh[1] * tmult.get(cb, 1.0) * profile.season_factor[states[sh[0]]], "note": f"hợp cục {sh[0]} ({lab})"})
    # relations among the temporal pillars themselves
    for i in range(len(pillars)):
        for j in range(i + 1, len(pillars)):
            a, b = pillars[i], pillars[j]
            if a["stem"] == b["stem"] and a["branch"] == b["branch"]:
                events.append({"kind": "tue_van_tinh_lam", "from": a["label"], "with": b["label"], "status": "tinh_lam"})
            if controls(STEM_ELEMENT[a["stem"]], STEM_ELEMENT[b["stem"]]) and _pair(a["branch"], b["branch"], SIX_CLASH) or controls(STEM_ELEMENT[b["stem"]], STEM_ELEMENT[a["stem"]]) and _pair(a["branch"], b["branch"], SIX_CLASH):
                events.append({"kind": "thien_khac_dia_xung", "from": a["label"], "with": b["label"], "status": "thien_khac_dia_xung"})
    return R2, extras, extra_stems, events


def can_chi_relation(view: ChartView, T: dict, others: list[dict]) -> dict:
    """Cái đầu / tiệt cước (Trích Thiên Tủy PDF pp.229-230). Thiên can sinh địa chi: phúc dày; địa chi sinh thiên can: khí tiết;
    thiên can khắc địa chi: cái đầu (cát hung giảm nửa); địa chi khắc thiên can: tiệt cước (chi không tải can, cả vận xấu).
    Giảm nhẹ: nguyên cục có thiên can khắc kẻ tấn công hoặc tiết kẻ tấn công; nặng thêm: nguyên cục có thiên can cùng hành kẻ tấn công."""
    se, be = STEM_ELEMENT[T["stem"]], BRANCH_ELEMENT[T["branch"]]
    if se == be:
        rel, atk = "dong_hanh", None
    elif generates(se, be):
        rel, atk = "can_sinh_chi", None
    elif generates(be, se):
        rel, atk = "chi_sinh_can", None
    elif controls(se, be):
        rel, atk = "cai_dau", se
    else:
        rel, atk = "tiet_cuoc", be
    out = {"label": T["label"], "pillar": T["name"], "relation": rel, "attacker": atk, "mitigated": False, "aggravated": False, "src": "SRC_TTT_TUEVAN"}
    if atk:
        els = [STEM_ELEMENT[view.stem(p)] for p in PILLARS] + [STEM_ELEMENT[o["stem"]] for o in others]
        out["mitigators"] = sorted({e for e in els if controls(e, atk) or generates(atk, e)})
        out["aggravators"] = sorted({e for e in els if e == atk})
        out["mitigated"] = bool(out["mitigators"]) and not out["aggravators"]
        out["aggravated"] = bool(out["aggravators"])
    return out


def _group(view: ChartView, stem: int) -> str:
    g = group_of(view.god(stem))
    return ROLE_GROUP.get(g, g)


def _roles(view: ChartView, Y: dict, T: dict) -> dict:
    sg = _group(view, T["stem"])
    bg = _group(view, HIDDEN_STEMS[T["branch"]][0])
    out = {}
    for name, m in Y["methods"].items():
        flat = yongshen._flat(m)
        out[name] = {"stem_group": sg, "stem_role": flat.get(sg), "branch_group": bg, "branch_role": flat.get(bg), "status": m["status"]}
        if name == "dieu_hau" and (m.get("table") or {}).get("yong_stems"):
            # the điều hậu cell names STEMS (TVH pp.389-396): a luck stem plays its role only when it is one of them, not when it merely shares
            # a ten-god group with one (Ất is not Giáp). The TTT 歲運 rules keyed on this role (cái đầu, tiệt cước) read it from here (S2).
            names = [x["stem"] for x in m["table"]["yong_stems"]]
            role = lambda st: None if STEMS_VI[st] not in names else "yong" if STEMS_VI[st] == names[0] else "xi"
            out[name].update({"stem_role": role(T["stem"]), "branch_role": role(HIDDEN_STEMS[T["branch"]][0]), "by": "stem_name"})
    return out


def natal_summary(view: ChartView, profile: SchoolProfile, R, S, extras=None) -> dict:
    G = geju.analyse(view, profile, R, S)
    return {"strength": S, "geju": G}


def analyse_extended(view: ChartView, profile: SchoolProfile, nat: dict, pillars: list[dict]) -> dict:
    profile = profile.with_(strength_method="he_thong")    # the scoring method of Thiệu Vĩ Hoa has no counterpart for extra temporal pillars
    """nat = {"R": Resolved, "S": natal strength (after interaction), "G": natal geju}; returns a compact comparison."""
    R2, extras, extra_stems, events = overlay(view, profile, nat["R"], pillars)
    S2 = strength.compute(view, profile, R2, extras)
    G2 = geju.analyse(view, profile, R2, S2, extra_stems)
    Y2 = yongshen.run(view, profile, R2, S2, G2)
    ctx = geju.Ctx(view, profile, R2, S2, extra_stems)
    P2 = patterns.evaluate_all(ctx)
    i1 = nat["G"]["inner"][0] if nat["G"]["inner"] else None
    i2 = G2["inner"][0] if G2["inner"] else None
    r1, r2 = (STATE_RANK[i1["state"]] if i1 else 0), (STATE_RANK[i2["state"]] if i2 else 0)
    if i1 and i2 and i1["name"] != i2["name"]:
        effect = "doi_cach"
    else:
        effect = "tro_cach" if r2 > r1 else "pha_cach" if r2 < r1 else "trung_tinh"
    old_p = {p["id"]: p["state"] for p in nat.get("P", [])}
    new_p = {p["id"]: p["state"] for p in P2}
    return {
        "pillars": [p["name"] for p in pillars], "labels": [p["label"] for p in pillars],
        "ten_gods": [view.god(p["stem"]) for p in pillars],
        "level_natal": nat["S"]["level"], "level": S2["level"], "ratio": [nat["S"]["ratio"], S2["ratio"]], "ambiguous": S2["ambiguous"],
        "cach": {"natal": [i1["name"], i1["state"]] if i1 else None, "extended": [i2["name"], i2["state"]] if i2 else None},
        "can_chi": [can_chi_relation(view, p, [q for q in pillars if q is not p]) for p in pillars], "level_index": S2["level_index"],
        "effect": effect, "events": events, "event_kinds": sorted({e["kind"] for e in events}),
        "roles": _roles(view, Y2, pillars[0]) if pillars else {},
        "patterns_gained": sorted(k for k in new_p if k not in old_p), "patterns_lost": sorted(k for k in old_p if k not in new_p),
        "patterns_changed": sorted(k for k in new_p if k in old_p and new_p[k] != old_p[k]),
        "yong_cach_cuc": Y2["methods"]["cach_cuc"].get("yong", []), "disagreements": [d["group"] for d in Y2["comparison"]["disagreements"]],
        "outer": [(o["name"], o["quality"]) for o in G2["outer"]],
    }


def natal_bundle(view: ChartView, profile: SchoolProfile = DEFAULT) -> dict:
    profile = profile.with_(strength_method="he_thong")    # comparisons with the extended chart must use the same strength method
    R = interact.resolve(view, profile)
    S = strength.compute(view, profile, R)
    G = geju.analyse(view, profile, R, S)
    P = patterns.evaluate_all(geju.Ctx(view, profile, R, S))
    return {"R": R, "S": S, "G": G, "P": P}


def month_pillars(year_stem: int) -> list[tuple[int, int]]:
    """The twelve lưu nguyệt pillars of a BaZi year (Dần ... Sửu) by ngũ hổ độn."""
    return [((tiger_month_stem(year_stem) + i) % 10, (2 + i) % 12) for i in range(12)]


def timeline(view: ChartView, profile: SchoolProfile, luck: list[dict], years: list[tuple[int, int, int]]) -> dict:
    """luck: [{index, stem, branch, start_year_exact}] ; years: [(year, stem, branch)] with BaZi-year pillars.
    Each year is evaluated on natal + the luck active at year + 0.09 (Lập Xuân) + the year."""
    nat = natal_bundle(view, profile)
    lucks = []
    for L in luck:
        lucks.append({"index": L["index"], "start_year_exact": L.get("start_year_exact"), **analyse_extended(view, profile, nat, [tp("luck", L["stem"], L["branch"])])})
    ys = []
    for (y, s, b) in years:
        active = [L for L in luck if L.get("start_year_exact") is not None and L["start_year_exact"] <= y + 0.09]
        pil = ([tp("luck", active[-1]["stem"], active[-1]["branch"])] if active else []) + [tp("year", s, b)]
        ys.append({"year": y, **analyse_extended(view, profile, nat, pil)})
    return {"natal": {"level": nat["S"]["level"], "cach": [(c["name"], c["state"]) for c in nat["G"]["inner"]], "patterns": [(p["id"], p["state"]) for p in nat["P"]]},
            "luck": lucks, "years": ys, "review_status": "draft"}
