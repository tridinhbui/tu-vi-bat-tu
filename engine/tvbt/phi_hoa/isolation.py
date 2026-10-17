"""School isolation: a Phi Tinh rule reads only `phi.*` / neutral geometry facts and may assert only `derived.phi.*`;
a rule of any other school may not read `phi.*` or `derived.phi.*`. Returns a list of problems (empty = clean)."""
from __future__ import annotations

from ..knowledge import dsl

NEUTRAL = ("palace.", "chart.", "time.")          # geometry / names shared by every school (no doctrine)


def _reads(rule) -> set[str]:
    exprs = [rule.conditions] + list(rule.exceptions)
    return {f for e in exprs for _, f in dsl.leaves(e)}


def validate_isolation(rules) -> list[str]:
    errs = []
    for r in rules:
        phi_rule = r.schoolId.startswith("phi_tinh")
        for f in _reads(r):
            is_phi = f.startswith(("phi.", "derived.phi."))
            if is_phi and not phi_rule:
                errs.append(f"{r.id}: school {r.schoolId!r} may not read Phi Hóa fact {f!r}")
            if phi_rule and not (is_phi or f.startswith(NEUTRAL)):
                errs.append(f"{r.id}: Phi Hóa rule reads non-neutral fact {f!r} (other schools' doctrine is off limits)")
        for c in r.consequences:
            if c.get("kind") == "assert":
                if phi_rule and not c["fact"].startswith("derived.phi."):
                    errs.append(f"{r.id}: Phi Hóa rule asserts {c['fact']!r}; must be derived.phi.*")
                if not phi_rule and c["fact"].startswith("derived.phi."):
                    errs.append(f"{r.id}: only Phi Hóa rules may assert {c['fact']!r}")
    return errs
