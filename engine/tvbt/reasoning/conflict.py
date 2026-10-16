"""Conflict detection & resolution over findings. No score summing.

Procedure (matches the spec's ordered checks):
 1. group findings by (subject, claim)   2. opposing effects (support vs limit) = conflict
 3. declared `conflictsWith` pairs also count (even when the two rules reach DIFFERENT claims on the same subject)   4. specificity = number of leaf conditions
 5. a more specific rule wins ONLY if it is verified with verified sources (else we can't claim
    the school documents that precedence)  6. otherwise status = "unresolved" and both are shown.
Statuses: supported | qualified (supported but limited by a counter-finding) | limited | unresolved
"""
from __future__ import annotations

from collections import defaultdict

from ..knowledge.schema import KnowledgeRule
from .engine import Finding, InferenceResult, Edge


def _specificity(r: KnowledgeRule) -> int:
    def n(e):
        if "fact" in e or "ref" in e:
            return 1
        v = e["count"] if "count" in e else e[next(iter(e))]
        return sum(n(x) for x in (v if isinstance(v, list) else [v]))
    return n(r.conditions)


def resolve(res: InferenceResult, rules: list[KnowledgeRule]) -> list[dict]:
    rmap = {r.id: r for r in rules}
    groups: dict[tuple[str, str], list[Finding]] = defaultdict(list)
    for f in res.findings:
        groups[(f.subject, f.claim)].append(f)
    report = []
    for (subj, claim), fs in sorted(groups.items()):
        sup = [f for f in fs if f.effect in ("support", "neutral")]
        lim = [f for f in fs if f.effect == "limit"]
        entry = {"subject": subj, "claim": claim, "supporting": [f.rule_id for f in sup],
                 "opposing": [f.rule_id for f in lim], "resolution": None}
        if sup and lim:
            best_s = max(sup, key=lambda f: _specificity(rmap[f.rule_id]))
            best_l = max(lim, key=lambda f: _specificity(rmap[f.rule_id]))
            ss, sl = _specificity(rmap[best_s.rule_id]), _specificity(rmap[best_l.rule_id])
            documented = (ss != sl)
            winner = best_s if ss > sl else best_l
            if documented and winner.basis == "verified":
                entry["resolution"] = f"specific rule {winner.rule_id} takes precedence (verified)"
                status = "supported" if winner in sup else "limited"
            else:
                entry["resolution"] = ("unresolved: opposing rules, precedence not documented by a verified "
                                       "source; both readings are shown")
                status = "unresolved"
            for f in fs:
                f.status = status
                if f.effect == "limit":
                    res.edges.append(Edge(f.id, best_s.id, "opposes"))
            entry["status"] = status
        else:
            entry["status"] = "supported"
            for f in fs:
                f.status = "supported" if f.effect != "limit" else "limited"
            entry["status"] = fs[0].status
        entry["basis"] = "verified" if all(f.basis == "verified" for f in fs) else "draft (unverified rules)"
        report.append(entry)
    # declared conflicts between rules that conclude different claims on the same subject
    seen_pairs: set[frozenset] = set()
    for fa in res.findings:
        ra = rmap.get(fa.rule_id)
        for other in (ra.conflictsWith if ra else []):
            for fb in res.findings:
                if fb.rule_id != other or fb.subject != fa.subject or fb.claim == fa.claim:
                    continue
                key = frozenset((fa.id, fb.id))
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                rb = rmap.get(other)
                if ra is None or rb is None:
                    continue
                sa, sb = _specificity(ra), _specificity(rb)
                win = fa if sa > sb else fb if sb > sa else None
                if win is not None and win.basis == "verified":
                    status = "supported" if win is fa else "limited"
                    resolution = f"specific rule {win.rule_id} takes precedence (verified)"
                    loser = fb if win is fa else fa
                    loser.status = "limited"
                    win.status = "supported"
                else:
                    status = "unresolved"
                    resolution = "unresolved: rules declare conflictsWith each other; precedence not documented by a verified source; both readings are shown"
                    fa.status = fb.status = "unresolved"
                res.edges.append(Edge(fb.id, fa.id, "opposes"))
                report.append({"subject": fa.subject, "claim": f"{fa.claim} <-> {fb.claim}", "supporting": [fa.rule_id], "opposing": [fb.rule_id],
                               "resolution": resolution, "status": status, "declared": True,
                               "basis": "verified" if fa.basis == fb.basis == "verified" else "draft (unverified rules)"})
    return report
