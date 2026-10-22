"""Pipeline: ChartView -> season/position -> interaction resolver -> strength (before/after) -> cách cục -> dụng thần methods
-> flat facts -> symbolic rule engine (draft pack) -> findings with provenance. Deterministic; no network, no LLM."""
from __future__ import annotations

import json
from pathlib import Path

from ..ganzhi import BRANCHES_VI, STEMS_VI
from ..knowledge.schema import load_pack, validate_pack
from ..nlg import generate as nlg, lexicon as lx
from ..reasoning import engine
from . import facts as bzf, flow, geju, interact, patterns, position, season, strength, yongshen, temporal_deep
from .model import ChartView
from .profile import DATA, DEFAULT, TVH_40, SchoolProfile

KNOWN = {"bazi.*", "chart.*", "derived.*"}


def load_structure_pack(name: str = "pack_structure.json"):
    return load_pack(DATA / name)


def _jsonable(o):
    if isinstance(o, dict):
        return {k: _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(x) for x in o]
    if isinstance(o, set):
        return sorted(_jsonable(x) for x in o)
    return o


def reason(base: dict, pack: str = "pack_structure.json") -> dict:
    rules, sources = load_structure_pack(pack)
    problems = validate_pack(rules, sources, KNOWN)
    lx.CLAIMS.update({k: {"label": v, "gloss": ""} for k, v in json.loads((DATA / "claims_vi.json").read_text("utf-8")).items() if not k.startswith("_")})
    res = engine.run(rules, sources, base, system="bat_tu")
    interps = nlg.build_interpretations(res, rules, sources)
    findings = []
    for f in res.findings:
        why = res.why(f.id)
        chain = []
        for label, kind in zip(why["chain"], why["kinds"].values()):
            if kind == "fact":
                name = label.split("=")[0]
                chain.append({"text": bzf.FACT_VI.get(name, name).replace("{v}", label.split("=", 1)[1].rsplit(" @", 1)[0]) if "{v}" in bzf.FACT_VI.get(name, "") else bzf.FACT_VI.get(name, label),
                              "kind": kind, "origin": bzf.FACT_ORIGIN.get(name)})
            else:
                chain.append({"text": label, "kind": kind})
        findings.append({"claim": f.claim, "effect": f.effect, "rule_id": f.rule_id, "depth": f.depth, "status": f.status, "basis": f.basis, "chain": chain,
                         "opposed_by": why["opposed_by"]})
    return {"pack_problems": problems, "findings": findings, "fired": [list(x) for x in res.fired], "blocked": res.blocked, "conflicts": res.conflicts,
            "pending": [p for p in res.pending if not p["missing_facts"] or True][:30], "derived": res.derived.get("chart", {}),
            "text": nlg.render(nlg.realize(interps, 3)), "all_rules_draft": all(r.reviewStatus == "draft" for r in rules)}


def analyse(view: ChartView, profile: SchoolProfile = TVH_40, with_rules: bool = True) -> dict:
    trace = []
    raw = interact.detect(view)
    trace.append({"step": "interact.detect", "n": len(raw)})
    R = interact.resolve(view, profile, raw)
    trace.append({"step": "interact.resolve", "order": list(profile.interact_order), "n_effects": len(R.steps), "cuc": [c["id"] for c in R.cuc]})
    S0 = strength.compute(view, profile, None)
    S1 = strength.compute_hybrid(view, profile, R) if profile.strength_method == "tvh_40" else strength.compute(view, profile, R)
    trace.append({"step": "strength.compute", "before": S0["level"], "after": S1["level"], "profile": profile.id})
    G = geju.analyse(view, profile, R, S1)
    trace.append({"step": "geju.analyse", "inner": [c["name"] for c in G["inner"]], "outer": [o["name"] for o in G["outer"]], "arbitration": G["arbitration"]})
    Y = yongshen.run(view, profile, R, S1, G)
    trace.append({"step": "yongshen.run", "methods": list(Y["methods"])})
    cl = season.climate(view, S1["by_element"])
    NL = flow.nguyen_luu(S1, profile)
    P = patterns.evaluate_all(geju.Ctx(view, profile, R, S1))
    trace.append({"step": "patterns.evaluate_all", "n": len(P)})
    base = bzf.build(view, R, S0, S1, G, Y, cl, P, NL)
    out = {
        "pillars": view.name(), "profile": {"id": profile.id, "review_status": profile.review_status},
        "season": {"month_states": S1["month_states"], "command": S1["command"], "climate": cl},
        "position": {"tou": position.tou(view), "dm_roots_raw": S0["roots"], "dm_roots_after": S1["roots"]},
        "interactions": _jsonable([{k: v for k, v in r.items()} for r in R.interactions]),
        "stem_controls": interact.stem_controls(view),
        "resolution": _jsonable({"cuc": R.cuc, "mult": R.mult, "opened_kho": R.opened, "stem_element_override": R.stem_element, "dm_hua": R.dm_hua, "steps": R.steps}),
        "strength_raw": S0, "strength_after": S1, "geju": G, "patterns": P, "nguyen_luu": NL, "yongshen": Y, "facts": base["chart"], "trace": trace,
    }
    if with_rules:
        out["reasoning"] = reason(base)
    return out


def timeline(view: ChartView, profile: SchoolProfile, luck: list[dict], years: list[tuple[int, int, int]], with_rules: bool = True) -> dict:
    """Extended-chart timeline (natal + luck, natal + luck + year). Each entry gets draft findings from pack_temporal.json."""
    out = temporal_deep.timeline(view, profile, luck, years)
    if with_rules:
        for e in out["luck"] + out["years"]:
            r = reason(bzf.temporal_facts(e), "pack_temporal.json")
            e["findings"] = [{"claim": f["claim"], "effect": f["effect"], "rule_id": f["rule_id"], "basis": f["basis"], "chain": f["chain"]} for f in r["findings"]]
            e["pack_problems"] = r["pack_problems"]
    return out


_GROUP_VI = {"Ti": "Tỉ Kiếp", "ThucThuong": "Thực Thương", "Tai": "Tài", "QuanSat": "Quan Sát", "An": "Ấn"}


# 歲運 rules whose premise is a draft method (docs/audit/bazi.md BZ-11): the role "dụng/hỷ" comes from the system's cách table or from phù ức,
# neither checked against a page, so the verified TTT sentence would stand on an unchecked premise. They are not passed to the prose.
_DRAFT_PREMISE = ("_CACH_CUC", "_PHU_UC")
# thần sát whose Vietnamese gloss (data/shensha.json) says what the 说明 column of 八字真宗 pp.21-22 prints; the others are told by position only
# (the hung ones on purpose, and 正桃花 / 桃花 / 红鸾, whose gloss softens the printed words)
_SHENSHA_GLOSS_OK = {"天乙贵人", "文昌贵人", "学堂贵人", "金舆", "十干禄", "飞刃", "将星", "驿马", "华盖", "月德", "天喜", "三台"}
_PIL = ("year", "month", "day", "hour")


def _year_pillar(y: int) -> tuple[int, int]:
    """The sexagenary pillar of a Bát Tự year (from Lập Xuân): Giáp Tý = 1984."""
    return (y - 4) % 10, (y - 4) % 12


def _events(view: ChartView, stem: int, branch: int) -> list[dict]:
    """What a temporal pillar (luck or year) meets in the natal chart, as positions, by the tables of 八字真宗 pp.19-20 (the same tables as the
    natal relations, bazi._relations: ten 干冲克 pairs, pairwise 支三刑, 半合 only with the middle branch): which natal pillar, stem or branch,
    what kind. The page prints tables only, so nothing here says what a relation means. temporal_deep.overlay is not used for this: it keeps
    the four-pair stem clash and the single 子卯 penalty its draft effect sizes were calibrated on."""
    from ..bazi import (DESTROY, HARM, MEETING, PENALTY_PAIR, PENALTY_PAIRS, SELF_PENALTY, SIX_CLASH, SIX_COMBINE, STEM_CLASH_KIND, STEM_COMBINE, TRIAD)
    from .position import KHO
    out = []
    nb = {view.branch(p): p for p in _PIL[::-1]}            # first pillar holding each branch (year first)
    for p in _PIL:
        ns, nbr = view.stem(p), view.branch(p)
        pair_s, pair_b = frozenset((stem, ns)), frozenset((branch, nbr))
        if pair_s in STEM_COMBINE:
            out.append({"kind": "stem_combine", "targets": [p], "part": "stem", "element": STEM_COMBINE[pair_s]})
        if pair_s in STEM_CLASH_KIND:
            out.append({"kind": "stem_clash" if STEM_CLASH_KIND[pair_s] == "xung" else "stem_control", "targets": [p], "part": "stem"})
        if stem == ns and branch == nbr:
            out.append({"kind": "phuc_ngam", "targets": [p], "part": "pillar"})
        if pair_s in STEM_CLASH_KIND and pair_b in SIX_CLASH:
            out.append({"kind": "phan_ngam", "targets": [p], "part": "pillar"})
        if pair_b in SIX_COMBINE:
            out.append({"kind": "branch_six_combine", "targets": [p], "part": "branch"})
        if pair_b in SIX_CLASH:
            out.append({"kind": "branch_clash", "targets": [p], "part": "branch", "opens_kho": nbr in KHO})
        if pair_b in PENALTY_PAIRS or pair_b == PENALTY_PAIR or (branch == nbr and branch in SELF_PENALTY):
            out.append({"kind": "branch_penalty", "targets": [p], "part": "branch"})
        if pair_b in HARM:
            out.append({"kind": "branch_harm", "targets": [p], "part": "branch"})
        if pair_b in DESTROY:
            out.append({"kind": "branch_destroy", "targets": [p], "part": "branch"})
    done = set()
    for kind, table in (("branch_triad", TRIAD), ("branch_meeting", MEETING)):
        for el, tri in table.items():
            if branch in tri and all(o in nb for o in tri if o != branch):
                out.append({"kind": kind, "targets": [nb[o] for o in tri if o != branch], "part": "branch", "element": el})
                done.add(el)
    for el, tri in TRIAD.items():                              # 半合局: the middle branch must be one of the two (八字真宗 p.20)
        if el in done or branch not in tri:
            continue
        for o in tri:
            if o != branch and o in nb and tri[1] in (branch, o):
                out.append({"kind": "branch_semi_triad", "targets": [nb[o]], "part": "branch", "element": el})
    return out


def _tvh_role(Y: dict, group: str, element: str) -> str | None:
    """'tot' / 'xau' for a luck or year group by Thiệu Vĩ Hoa's table of vận hỷ/kỵ per cách (pp.378-386), or by the special cách's elements
    (pp.385-386); None when the table gives no row (two readings at the 40% border, no inner cách, the group not named)."""
    c = Y["methods"]["cach_cuc_tvh"]
    if c["status"] == "ap_dung":
        return "tot" if group in (c.get("van_tot") or []) else "xau" if group in (c.get("van_xau") or []) else None
    t = Y["methods"]["thuan_the_tvh"]
    if t["status"] == "ap_dung":
        if t.get("van_tot_elements") is not None:
            return "tot" if element in (t.get("van_tot_elements") or []) else "xau" if element in (t.get("van_xau_elements") or []) else None
        return "tot" if group in t.get("yong", []) + t.get("xi", []) else "xau" if group in t.get("ji", []) else None
    return None


def _pillar_facts(view: ChartView, Y: dict, stem: int, branch: int) -> dict:
    """What a temporal pillar is, as computed facts: the stem's ten god, the branch's hidden stems and their ten gods, the day master's growth
    stage at the branch (八字真宗 pp.24-25 table), and the role of the stem and of the branch's main qi by the TVH tables."""
    from ..bazi import HIDDEN_STEMS, growth_stage
    from ..ganzhi import BRANCH_ELEMENT, STEM_ELEMENT
    from .temporal_deep import _group
    hid = HIDDEN_STEMS[branch]
    sg, bg = _group(view, stem), _group(view, hid[0])
    dh = yongshen._flat(Y["methods"]["dieu_hau"])
    return {"stem": STEMS_VI[stem], "branch": BRANCHES_VI[branch], "ten_god": view.god(stem), "branch_god": view.god(hid[0]),
            "hidden": [{"stem": STEMS_VI[h], "ten_god": view.god(h)} for h in hid], "stage": growth_stage(view.dm, branch),
            "stem_group": _GROUP_VI.get(sg, sg), "branch_group": _GROUP_VI.get(bg, bg), "stem_element": STEM_ELEMENT[stem], "branch_element": BRANCH_ELEMENT[branch],
            "tvh": {"stem": _tvh_role(Y, sg, STEM_ELEMENT[stem]), "branch": _tvh_role(Y, bg, BRANCH_ELEMENT[branch])},
            "dieu_hau": {"stem": dh.get(sg), "branch": dh.get(bg)}}


def prose_summary(view: ChartView, luck: list[dict], years: list[int] | None = None) -> dict:
    """What the reader prose (src/interpret/prose/bazi.ts) needs from the structure analysis, flattened: the day master's strength by
    Thiệu Vĩ Hoa's score (SRC_TVH_DIEM; the verified rules BT_TVH_* decide vượng/nhược/biên), the climate and the điều hậu table cell
    (SRC_TVH_DIEUHAU, verified), the phù ức reading(s) (system principle), the cách from the month with Thiệu Vĩ Hoa's dụng thần and vận
    hỷ/kỵ table (pp.378-386) and his thành bại sentences (pp.367-369, verified rules BT_TVH_TB_*), the verified structure findings with their
    Vietnamese claim, the four pillars' nạp âm and growth stages, the thần sát of 八字真宗 pp.21-22, per luck pillar its stem and branch (ten
    gods, hidden stems, growth stage), what it does to each natal pillar (hợp, xung, hình, hại, phá, phục/phản ngâm, tam hợp/hội: positions)
    and its verified 歲運 findings (TTT), and the same for the requested years (lưu niên). Labels say which parts are verified."""
    from types import SimpleNamespace
    from .. import shensha
    from ..ganzhi import nap_am_name
    a = analyse(view)
    claims = {k: v for k, v in json.loads((DATA / "claims_vi.json").read_text("utf-8")).items() if not k.startswith("_")}
    S, Y = a["strength_after"], a["yongshen"]["methods"]
    tvh = S.get("tvh") or {}
    dh = Y.get("dieu_hau", {}) or {}
    tab = dh.get("table") or {}
    pu = Y.get("phu_uc", {}) or {}
    alts = pu.get("alternatives") or ([pu] if pu.get("yong") else [])
    grp = lambda xs: [_GROUP_VI.get(x, x) for x in xs or []]
    tb_verdict = {f"BT_TVH_TB_{x['id'].upper().replace('.', '_')}": x["verdict"] for c in a["geju"]["inner"][:1] for x in c.get("tvh_danh_gia", [])}
    verified = [{"rule_id": f["rule_id"], "claim": f["claim"], "text": claims.get(f["claim"], f["claim"]), **({"verdict": tb_verdict[f["rule_id"]]} if f["rule_id"] in tb_verdict else {})}
                for f in a.get("reasoning", {}).get("findings", []) if f["basis"] == "verified"]
    ys = [(y, *_year_pillar(y)) for y in years or []]
    tl = timeline(view, profile_default(), luck, ys)
    border = bool(tvh) and bool(S.get("ambiguous"))
    ok = lambda fs: [{"rule_id": f["rule_id"], "text": claims.get(f["claim"], f["claim"])} for f in fs
                     if f["basis"] == "verified" and not f["rule_id"].endswith(_DRAFT_PREMISE) and "THIENKHAC" not in f["rule_id"]]
    lk = []
    for e, L in zip(tl["luck"], luck):
        roles = e.get("roles", {}).get("dieu_hau", {})
        cc = next((c for c in e.get("can_chi", []) if c["label"] == "luck"), None)
        lk.append({"index": e["index"], "pillar": e["pillars"][0], "ten_god": (e.get("ten_gods") or [None])[0], "level": e.get("level"),
                   "effect": e.get("effect"), "can_chi": [c["relation"] for c in e.get("can_chi", [])],
                   "can_chi_detail": cc and {"relation": cc["relation"], "mitigated": cc["mitigated"], "aggravated": cc["aggravated"]},
                   "dieu_hau": {"stem": roles.get("stem_role"), "branch": roles.get("branch_role")},
                   **{k: v for k, v in _pillar_facts(view, a["yongshen"], L["stem"], L["branch"]).items() if k != "dieu_hau"},
                   "events": _events(view, L["stem"], L["branch"]), "findings": ok(e.get("findings", []))})
    yr = []
    for e, (y, s, b) in zip(tl["years"], ys):
        pf = _pillar_facts(view, a["yongshen"], s, b)
        cc = next((c for c in e.get("can_chi", []) if c["label"] == "year"), None)
        ev = _events(view, s, b) + [{"kind": x["kind"], "targets": ["luck"], "part": "pillar"} for x in e["events"]
                                                    if x["kind"] in ("thien_khac_dia_xung", "tue_van_tinh_lam")]
        fs = []
        # 天克地冲 between the year and the luck pillar (TTT, verified): the rule's premise is the day master's strength; the natal verdict of the
        # TVH 40% rule is used (the extended chart has no TVH score, BZ-10), and nothing is said at the border
        if any(x["kind"] == "thien_khac_dia_xung" for x in ev) and tvh and not border:
            rid = "BT_TTT_THIENKHAC_VUONG" if tvh.get("dm_strong") else "BT_TTT_THIENKHAC_NHUOC"
            fs.append({"rule_id": rid, "text": claims.get(rid.lower().replace("bt_ttt_thienkhac", "bt_ttt_thien_khac"), rid)})
        yr.append({"year": y, "pillar": f"{STEMS_VI[s]} {BRANCHES_VI[b]}", "luck": e["pillars"][0] if len(e["pillars"]) > 1 else None, **pf,
                   "can_chi_detail": cc and {"relation": cc["relation"], "mitigated": cc["mitigated"], "aggravated": cc["aggravated"]},
                   "events": ev, "findings": fs})
    cct, ttv = Y.get("cach_cuc_tvh", {}) or {}, Y.get("thuan_the_tvh", {}) or {}
    inner = a["geju"]["inner"][0] if a["geju"]["inner"] else None
    pv = SimpleNamespace(**{k: SimpleNamespace(stem=view.stem(k), branch=view.branch(k)) for k in _PIL})
    from ..ganzhi import STEMS_HAN
    ss = [{"vi": x["vi"], "kind": x["kind"], "pillar": x["pillar"], "at": STEMS_VI[STEMS_HAN.index(x["at"])] if x["at"] in STEMS_HAN else x["at"], "gloss": x["gloss"] if x["zh"] in _SHENSHA_GLOSS_OK else None}
          for x in shensha.find(vars(pv))]
    return {
        "strength": {"dm_strong": tvh.get("dm_strong"), "own_share": tvh.get("own_share"), "threshold": tvh.get("threshold"),
                     "season_state": S.get("season_state"), "by_element": S.get("by_element"), "src": tvh and "TVH pp.331-355",
                     "tvh_totals": {k: round(v, 1) for k, v in (tvh.get("totals") or {}).items()}},
        "climate": {"label": (dh.get("climate") or {}).get("label"), "han_noan": (dh.get("han_noan") or {}).get("state")},
        "dieu_hau": {"cell": tab.get("cell"), "need": dh.get("need_elements", []), "avoid": dh.get("avoid_elements", []), "satisfied": tab.get("satisfied"),
                     "stems": [{k: s.get(k) for k in ("stem", "ten_god", "rank", "visible", "hidden")} for s in tab.get("yong_stems", [])],
                     "verified": dh.get("status") == "bang_TVH_verified", "src": "TVH pp.389-396"},
        "phu_uc": [{"level": x.get("level"), "yong": grp(x.get("yong")), "xi": grp(x.get("xi")), "ji": grp(x.get("ji"))} for x in alts],
        "geju": {"inner": [{"name": c["name"], "state": c.get("state")} for c in a["geju"]["inner"]],
                 "outer": [{"name": o["name"], "quality": o.get("quality")} for o in a["geju"]["outer"]], "verified": False},
        # Thiệu Vĩ Hoa's dụng thần by cách (pp.378-386, verified transcription): the cách from the month, the 40% verdict, the largest group,
        # the dụng thần and the luck groups the book calls good / bad; or the special cách (pp.369-376) with its elements
        "cach_tvh": {"status": cct.get("status"), "cach": cct.get("cach") or (inner or {}).get("name"), "dm": cct.get("dm"), "dominant": _GROUP_VI.get(cct.get("dominant"), cct.get("dominant")),
                     "yong": grp(cct.get("yong_alternatives") or cct.get("yong")), "van_tot": grp(cct.get("van_tot")), "van_xau": grp(cct.get("van_xau")), "page": cct.get("page"),
                     "special": ttv.get("outer") if ttv.get("status") == "ap_dung" else None,
                     "special_tot": ttv.get("van_tot_elements") or grp(ttv.get("yong", []) + ttv.get("xi", [])) if ttv.get("status") == "ap_dung" else [],
                     "special_xau": ttv.get("van_xau_elements") or grp(ttv.get("ji", [])) if ttv.get("status") == "ap_dung" else []},
        "pillars": {k: {"nap_am": nap_am_name(view.stem(k), view.branch(k)), "stage": view.stage(view.dm, k)} for k in _PIL},
        "shensha": ss,
        "verified": verified, "luck": lk, "years": yr,
    }


def profile_default():
    from .profile import TVH_40
    return TVH_40
