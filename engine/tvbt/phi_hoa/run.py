"""Run the EXPERIMENTAL Phi Hóa rules on a chart: graph (facts) -> rules (inference with trace). Opt-in only."""
from __future__ import annotations

from ..knowledge.loader import load_experimental_phi_hoa
from ..knowledge.schema import validate_pack
from ..reasoning import conflict, engine, facts
from ..tuvi import TuViChart
from . import facts as phi_facts_mod, graph as phi_graph
from .isolation import validate_isolation

KNOWN = {"palace.*", "chart.*", "bazi.*", "derived.*", "phi.*"}


def run_phi_hoa(tv: TuViChart, table_id: str = "tam_hop_vn") -> dict:
    rules, srcs = load_experimental_phi_hoa()
    g = phi_graph.build(tv, table_id)
    base = facts.tuvi_facts(tv)
    for subj, extra in phi_facts_mod.phi_facts(tv, g).items():
        base[subj].update(extra)
    res = engine.run(rules, srcs, base, system="tu_vi")
    ids = {r.id for r in rules}
    return {"graph": g, "result": res, "rules": rules,
            "findings": [f for f in res.findings if f.rule_id in ids],
            "blocked": [b for b in res.blocked if b["rule"] in ids],
            "conflicts": [c for c in conflict.resolve(res, rules) if c.get("declared")],
            "problems": validate_pack(rules, srcs, KNOWN) + validate_isolation(rules)}
