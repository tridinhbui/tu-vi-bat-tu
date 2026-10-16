"""Forward-chaining inference with provenance graph, exceptions, and three-valued conditions.

Deterministic: rules ordered by (-priority, id); subjects ordered by name. Derived facts feed later
rules (multi-hop) until a fixpoint or MAX_DEPTH. A rule fires at most once per (rule, subject).
Contradictory re-assertion of a derived fact is recorded as a conflict, never overwritten.
Phase 1: conditions may read other palaces (`ref`) and count sub-conditions; `formations` (cách cục with core / boosters / breakers /
rescuers / refutations) are evaluated first, and their outcome is asserted as derived facts so ordinary rules can chain on it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..knowledge import dsl
from ..knowledge.schema import KnowledgeRule, Source

MAX_DEPTH = 6


@dataclass
class Node:
    id: str
    kind: str      # fact | rule | finding | source | blocked
    label: str
    data: dict = field(default_factory=dict)


@dataclass
class Edge:
    src: str
    dst: str
    kind: str      # derived_from | supports | opposes | suppresses | belongs_to | sourced_from


@dataclass
class Finding:
    id: str
    subject: str
    claim: str
    effect: str            # support | limit | neutral
    rule_id: str
    depth: int
    status: str = "supported"
    basis: str = "draft"   # draft | verified
    notes: list[str] = field(default_factory=list)


@dataclass
class InferenceResult:
    nodes: dict[str, Node]
    edges: list[Edge]
    findings: list[Finding]
    derived: dict[str, dict[str, Any]]
    pending: list[dict]
    blocked: list[dict]
    conflicts: list[dict]
    fired: list[tuple[str, str, int]]
    formations: list[dict] = field(default_factory=list)

    def why(self, finding_id: str) -> dict:
        """Backward chain: everything a finding depends on, down to base facts and sources."""
        seen, order = set(), []
        stack = [finding_id]
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            order.append(n)
            stack.extend(e.dst for e in self.edges if e.src == n and e.kind in ("derived_from", "sourced_from"))
        opp = [e.src for e in self.edges if e.dst == finding_id and e.kind in ("opposes", "suppresses")]
        return {"chain": [self.nodes[n].label for n in order if n in self.nodes],
                "kinds": {n: self.nodes[n].kind for n in order if n in self.nodes},
                "opposed_by": [self.nodes[n].label for n in opp if n in self.nodes]}


def _fact_node(res_nodes, subject, name, value):
    nid = f"fact:{subject}:{name}"
    res_nodes.setdefault(nid, Node(nid, "fact", f"{name}={value!r} @{subject}"))
    return nid


def _leaf_facts(expr) -> list[str]:
    return [f for _, f in dsl.leaves(expr)]


def _targets(expr, facts: dict, subj: str, derived: dict | None = None) -> list[tuple[str, str]]:
    """(subject, fact) pairs a condition reads; a `ref` leaf points at another palace's subject. A DERIVED fact that a palace rule reads
    but that was asserted at chart scope is attributed to "chart", so its provenance edge reaches the rule that asserted it."""
    out = []
    for pal, f in dsl.leaves(expr, facts):
        tsub = subj if pal is None else f"palace:{pal}"
        if derived is not None and f.startswith("derived.") and f not in derived.get(tsub, {}) and f in derived.get("chart", {}):
            tsub = "chart"
        out.append((tsub, f))
    return out


def run(rules: list[KnowledgeRule], sources: list[Source], base: dict[str, dict],
        system: str | None = None, formations: list | None = None) -> InferenceResult:
    nodes: dict[str, Node] = {}
    edges: list[Edge] = []
    derived: dict[str, dict[str, Any]] = {s: {} for s in base}
    findings: list[Finding] = []
    pending: list[dict] = []
    blocked: list[dict] = []
    conflicts: list[dict] = []
    fired: list[tuple[str, str, int]] = []
    done: set[tuple[str, str]] = set()
    fdepth: dict[tuple[str, str], int] = {}   # derived fact -> derivation depth
    src = {s.id: s for s in sources}
    ordered = sorted((r for r in rules if system is None or r.system == system), key=lambda r: (-r.priority, r.id))

    def facts_of(subject):
        d = dict(base.get("chart", {}))
        d.update(base[subject])
        d.update(derived[subject])
        if subject != "chart":
            d.update({k: v for k, v in derived["chart"].items()})
        return d

    def world(name: str):
        return facts_of(f"palace:{name}") if f"palace:{name}" in base else None

    formation_out: list[dict] = []
    if formations:
        from .formation_eval import run_formations
        formation_out = run_formations(formations, base, facts_of, world, derived, fdepth, nodes, edges, findings)

    for depth in range(1, MAX_DEPTH + 1):
        progressed = False
        for r in ordered:
            subjects = sorted(s for s in base if s != "chart") if r.subject == "palace" else ["chart"]
            for subj in subjects:
                if (r.id, subj) in done:
                    continue
                facts = facts_of(subj)
                cond = dsl.evaluate(r.conditions, facts, world)
                if cond is None:
                    continue  # re-checked next round; reported as pending at the end if still unknown
                done.add((r.id, subj))
                if cond is False:
                    continue
                rid = f"rule:{r.id}@{subj}"
                nodes[rid] = Node(rid, "rule", f"{r.id} [{r.reviewStatus}] @{subj}", {"description": r.description})
                for tsub, f in _targets(r.conditions, facts, subj, derived):
                    fid = _fact_node(nodes, tsub, f, facts_of(tsub).get(f) if tsub in base else None)
                    edges.append(Edge(rid, fid, "derived_from"))
                for sid in r.sourceIds:
                    nid = f"source:{sid}"
                    nodes.setdefault(nid, Node(nid, "source", f"{sid} ({'verified' if src[sid].verified else 'unverified'})"))
                    edges.append(Edge(rid, nid, "sourced_from"))
                exc = [e for e in r.exceptions if dsl.evaluate(e, facts, world) is True]
                if exc:
                    blocked.append({"rule": r.id, "subject": subj, "exception": exc[0]})
                    bid = f"blocked:{r.id}@{subj}"
                    nodes[bid] = Node(bid, "blocked", f"{r.id} suppressed by exception @{subj}")
                    for tsub, f in _targets(exc[0], facts, subj, derived):
                        edges.append(Edge(_fact_node(nodes, tsub, f, facts_of(tsub).get(f) if tsub in base else None), rid, "suppresses"))
                    continue
                rdepth = 1 + max([fdepth.get((tsub, f), fdepth.get(("chart", f), 0)) for tsub, f in _targets(r.conditions, facts, subj, derived)] + [0])
                fired.append((r.id, subj, rdepth))
                progressed = True
                basis = "verified" if r.reviewStatus == "verified" and all(
                    src[s].verified for s in r.sourceIds) else "draft"
                for c in r.consequences:
                    if c.get("kind") == "assert":
                        name, val = c["fact"], c.get("value", True)
                        tgt = "chart" if c.get("scope") == "chart" else subj
                        if name in derived[tgt] and derived[tgt][name] != val:
                            conflicts.append({"type": "derived_fact", "fact": name, "subject": tgt,
                                              "values": [derived[tgt][name], val], "rule": r.id})
                            continue
                        derived[tgt][name] = val
                        fdepth[(tgt, name)] = rdepth
                        fid = _fact_node(nodes, tgt, name, val)
                        nodes[fid].kind = "fact"
                        nodes[fid].data["derived"] = True
                        edges.append(Edge(fid, rid, "derived_from"))
                    elif c.get("kind") == "finding":
                        fid = f"finding:{r.id}:{c['claim']}@{subj}"
                        f = Finding(fid, subj, c["claim"], c.get("effect", "support"), r.id, rdepth, basis=basis)
                        findings.append(f)
                        nodes[fid] = Node(fid, "finding", f"{c['claim']} ({f.effect}) @{subj}",
                                          {"scope": c.get("scope"), "depth": rdepth})
                        edges.append(Edge(fid, rid, "derived_from"))
        if not progressed:
            break
    for r in ordered:
        for subj in (sorted(s for s in base if s != "chart") if r.subject == "palace" else ["chart"]):
            if (r.id, subj) not in done:
                facts = facts_of(subj)
                missing = sorted({f for tsub, f in _targets(r.conditions, facts, subj)
                                  if f not in (facts if tsub == subj else (facts_of(tsub) if tsub in base else {}))})
                pending.append({"rule": r.id, "subject": subj, "missing_facts": missing})
    return InferenceResult(nodes, edges, findings, derived, pending, blocked, conflicts, fired, formation_out)
