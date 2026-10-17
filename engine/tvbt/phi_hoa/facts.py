"""Flat `phi.*` facts per palace from a PhiGraph, for the rule engine. All keys start with `phi.`; no doctrine, no reading."""
from __future__ import annotations

from ..tuvi import TuViChart
from .graph import PhiGraph, build
from .tables import HOA

PAIRS = (("Hóa Lộc", "Hóa Kỵ"), ("Hóa Kỵ", "Hóa Lộc"), ("Hóa Lộc", "Hóa Lộc"), ("Hóa Kỵ", "Hóa Kỵ"))


def phi_facts(chart: TuViChart, graph: PhiGraph | None = None) -> dict[str, dict]:
    g = graph or build(chart)
    out: dict[str, dict] = {"chart": {"phi.table": g.table_id, "phi.table_status": g.table_status}}
    for p in chart.palaces:
        n = p["name"]
        f: dict = {"phi.stem": p["stem"]}
        for h in HOA:
            e = g.out[n][h]
            f[f"phi.out.{h}"] = e.dst
            f[f"phi.out_star.{h}"] = e.star
            f[f"phi.in.{h}"] = list(g.inc[n][h])
        f["phi.tu_hoa"] = [h for h in HOA if "tu_hoa" in g.out[n][h].kinds]
        f["phi.xung_phi"] = [h for h in HOA if "xung_phi" in g.out[n][h].kinds]
        f["phi.in_n"] = sum(len(v) for v in g.inc[n].values())
        f["phi.in_ky_n"], f["phi.in_loc_n"] = len(g.inc[n]["Hóa Kỵ"]), len(g.inc[n]["Hóa Lộc"])
        for a, b in PAIRS:           # [X] if  n --a--> X  and  X --b--> n  (X != n), else []
            x = g.out[n][a].dst
            f[f"phi.mutual.{a}>{b}"] = [x] if x and x != n and g.out[x][b].dst == n else []
        f["phi.loc_chain"] = g.chain("Hóa Lộc", n)
        f["phi.ky_chain"] = g.chain("Hóa Kỵ", n)
        f["phi.loc_chain_n"] = len(f["phi.loc_chain"])
        f["phi.ky_chain_n"] = len(f["phi.ky_chain"])
        out[f"palace:{n}"] = f
    return out
