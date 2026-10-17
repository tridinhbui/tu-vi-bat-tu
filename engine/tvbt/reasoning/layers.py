"""Run the multi-layer (bản mệnh · đại hạn · lưu niên) EXPERIMENTAL rules on a chart for a given year.
Combines natal facts, Phase-2 time facts and the Phase-1 formation verdicts, so a layer rule can chain on a cách cục (multi-hop)."""
from __future__ import annotations

from ..knowledge.loader import load_experimental, load_experimental_layers
from ..tuvi import TuViChart
from . import conflict, engine, facts, temporal_facts


def run_layers(tv: TuViChart, year: int) -> dict:
    _, formations, fsrc = load_experimental()
    rules, srcs = load_experimental_layers()
    base = facts.tuvi_facts(tv)
    for subj, extra in temporal_facts.time_facts(tv, year).items():
        base[subj].update(extra)
    res = engine.run(rules, srcs + [s for s in fsrc if s.id not in {x.id for x in srcs}], base, system="tu_vi", formations=formations)
    ids = {r.id for r in rules}
    mine = [f for f in res.findings if f.rule_id in ids]
    return {"layers": temporal_facts.layered(tv, year), "result": res, "findings": mine, "rules": rules,
            "conflicts": [c for c in conflict.resolve(res, rules) if c.get("declared")],
            "blocked": [b for b in res.blocked if b["rule"] in ids]}
