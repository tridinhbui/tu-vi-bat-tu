"""Pipeline: ChartView -> season/position -> interaction resolver -> strength (before/after) -> cách cục -> dụng thần methods
-> flat facts -> symbolic rule engine (draft pack) -> findings with provenance. Deterministic; no network, no LLM."""
from __future__ import annotations

import json
from pathlib import Path

from ..knowledge.schema import load_pack, validate_pack
from ..nlg import generate as nlg, lexicon as lx
from ..reasoning import engine
from . import facts as bzf, geju, interact, position, season, strength, yongshen
from .model import ChartView
from .profile import DATA, DEFAULT, SchoolProfile

KNOWN = {"bazi.*", "chart.*", "derived.*"}


def load_structure_pack():
    return load_pack(DATA / "pack_structure.json")


def _jsonable(o):
    if isinstance(o, dict):
        return {k: _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(x) for x in o]
    if isinstance(o, set):
        return sorted(_jsonable(x) for x in o)
    return o


def reason(base: dict) -> dict:
    rules, sources = load_structure_pack()
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


def analyse(view: ChartView, profile: SchoolProfile = DEFAULT, with_rules: bool = True) -> dict:
    trace = []
    raw = interact.detect(view)
    trace.append({"step": "interact.detect", "n": len(raw)})
    R = interact.resolve(view, profile, raw)
    trace.append({"step": "interact.resolve", "order": list(profile.interact_order), "n_effects": len(R.steps), "cuc": [c["id"] for c in R.cuc]})
    S0 = strength.compute(view, profile, None)
    S1 = strength.compute(view, profile, R)
    trace.append({"step": "strength.compute", "before": S0["level"], "after": S1["level"], "profile": profile.id})
    G = geju.analyse(view, profile, R, S1)
    trace.append({"step": "geju.analyse", "inner": [c["name"] for c in G["inner"]], "outer": [o["name"] for o in G["outer"]], "arbitration": G["arbitration"]})
    Y = yongshen.run(view, profile, R, S1, G)
    trace.append({"step": "yongshen.run", "methods": list(Y["methods"])})
    cl = season.climate(view, S1["by_element"])
    base = bzf.build(view, R, S0, S1, G, Y, cl)
    out = {
        "pillars": view.name(), "profile": {"id": profile.id, "review_status": profile.review_status},
        "season": {"month_states": S1["month_states"], "command": S1["command"], "climate": cl},
        "position": {"tou": position.tou(view), "dm_roots_raw": S0["roots"], "dm_roots_after": S1["roots"]},
        "interactions": _jsonable([{k: v for k, v in r.items()} for r in R.interactions]),
        "stem_controls": interact.stem_controls(view),
        "resolution": _jsonable({"cuc": R.cuc, "mult": R.mult, "opened_kho": R.opened, "stem_element_override": R.stem_element, "dm_hua": R.dm_hua, "steps": R.steps}),
        "strength_raw": S0, "strength_after": S1, "geju": G, "yongshen": Y, "facts": base["chart"], "trace": trace,
    }
    if with_rules:
        out["reasoning"] = reason(base)
    return out
