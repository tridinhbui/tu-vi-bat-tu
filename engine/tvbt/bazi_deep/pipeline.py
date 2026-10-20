"""Pipeline: ChartView -> season/position -> interaction resolver -> strength (before/after) -> cách cục -> dụng thần methods
-> flat facts -> symbolic rule engine (draft pack) -> findings with provenance. Deterministic; no network, no LLM."""
from __future__ import annotations

import json
from pathlib import Path

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


def prose_summary(view: ChartView, luck: list[dict]) -> dict:
    """What the reader prose (src/interpret/prose/bazi.ts) needs from the structure analysis, flattened: the day master's strength by
    Thiệu Vĩ Hoa's score (SRC_TVH_DIEM; the verified rules BT_TVH_* decide vượng/nhược/biên), the climate and the điều hậu table cell
    (SRC_TVH_DIEUHAU, verified), the phù ức reading(s) (system principle), the cách from the month (draft definitions), the verified
    structure findings with their Vietnamese claim, and per luck pillar its ten god, what it does to the cách and the climate, and its
    verified 歲運 findings (TTT). Labels say which parts are verified."""
    a = analyse(view)
    claims = {k: v for k, v in json.loads((DATA / "claims_vi.json").read_text("utf-8")).items() if not k.startswith("_")}
    S, Y = a["strength_after"], a["yongshen"]["methods"]
    tvh = S.get("tvh") or {}
    dh = Y.get("dieu_hau", {}) or {}
    tab = dh.get("table") or {}
    pu = Y.get("phu_uc", {}) or {}
    alts = pu.get("alternatives") or ([pu] if pu.get("yong") else [])
    grp = lambda xs: [_GROUP_VI.get(x, x) for x in xs or []]
    verified = [{"rule_id": f["rule_id"], "claim": f["claim"], "text": claims.get(f["claim"], f["claim"])}
                for f in a.get("reasoning", {}).get("findings", []) if f["basis"] == "verified"]
    tl = timeline(view, profile_default(), luck, [])
    lk = []
    for e in tl["luck"]:
        roles = e.get("roles", {}).get("dieu_hau", {})
        lk.append({"index": e["index"], "pillar": e["pillars"][0], "ten_god": (e.get("ten_gods") or [None])[0], "level": e.get("level"),
                   "effect": e.get("effect"), "can_chi": [c["relation"] for c in e.get("can_chi", [])],
                   "dieu_hau": {"stem": roles.get("stem_role"), "branch": roles.get("branch_role")},
                   "findings": [{"rule_id": f["rule_id"], "text": claims.get(f["claim"], f["claim"])} for f in e.get("findings", []) if f["basis"] == "verified"]})
    return {
        "strength": {"dm_strong": tvh.get("dm_strong"), "own_share": tvh.get("own_share"), "threshold": tvh.get("threshold"),
                     "season_state": S.get("season_state"), "by_element": S.get("by_element"), "src": tvh and "TVH pp.331-355"},
        "climate": {"label": (dh.get("climate") or {}).get("label"), "han_noan": (dh.get("han_noan") or {}).get("state")},
        "dieu_hau": {"cell": tab.get("cell"), "need": dh.get("need_elements", []), "avoid": dh.get("avoid_elements", []), "satisfied": tab.get("satisfied"),
                     "stems": [{k: s.get(k) for k in ("stem", "ten_god", "rank", "visible", "hidden")} for s in tab.get("yong_stems", [])],
                     "verified": dh.get("status") == "bang_TVH_verified", "src": "TVH pp.389-396"},
        "phu_uc": [{"level": x.get("level"), "yong": grp(x.get("yong")), "xi": grp(x.get("xi")), "ji": grp(x.get("ji"))} for x in alts],
        "geju": {"inner": [{"name": c["name"], "state": c.get("state")} for c in a["geju"]["inner"]],
                 "outer": [{"name": o["name"], "quality": o.get("quality")} for o in a["geju"]["outer"]], "verified": False},
        "verified": verified, "luck": lk,
    }


def profile_default():
    from .profile import TVH_40
    return TVH_40
