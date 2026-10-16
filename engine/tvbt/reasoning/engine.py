"""Forward-chaining inference with provenance graph, exceptions, and three-valued conditions.

Deterministic: rules ordered by (-priority, id); subjects ordered by name. Derived facts feed later
rules (multi-hop) until a fixpoint or MAX_DEPTH. A rule fires at most once per (rule, subject).
Contradictory re-assertion of a derived fact is recorded as a conflict, never overwritten.
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
    if "fact" in expr:
        return [expr["fact"]]
    key = next(iter(expr))
    sub = expr[key] if isinstance(expr[key], list) else [expr[key]]
    return [f for e in sub for f in _leaf_facts(e)]


def run(rules: list[KnowledgeRule], sources: list[Source], base: dict[str, dict],
        system: str | None = None) -> InferenceResult:
    nodes: dict[str, Node] = {}
    edges: list[Edge] = []
    derived: dict[str, dict[str, Any]] = {s: {} for s in base}
    findings: list[Finding] = []
    pending: list[dict] = []
    blocked: list[dict] = []
    conflicts: list[dict] = []
    fired: list[tuple[str, str, int]] = []
    done: set[tuple[str, str]] = set()
    src = {s.id: s for s in sources}
    ordered = sorted((r for r in rules if system is None or r.system == system), key=lambda r: (-r.priority, r.id))

    def facts_of(subject):
        d = dict(base.get("chart", {}))
        d.update(base[subject])
        d.update(derived[subject])
        if subject != "chart":
            d.update({k: v for k, v in derived["chart"].items()})
        return d

    for depth in range(1, MAX_DEPTH + 1):
        progressed = False
        for r in ordered:
            subjects = sorted(s for s in base if s != "chart") if r.subject == "palace" else ["chart"]
            for subj in subjects:
                if (r.id, subj) in done:
                    continue
                facts = facts_of(subj)
                cond = dsl.evaluate(r.conditions, facts)
                if cond is None:
                    continue  # re-checked next round; reported as pending at the end if still unknown
                done.add((r.id, subj))
                if cond is False:
                    continue
                rid = f"rule:{r.id}@{subj}"
                nodes[rid] = Node(rid, "rule", f"{r.id} [{r.reviewStatus}] @{subj}", {"description": r.description})
                for f in _leaf_facts(r.conditions):
                    fid = _fact_node(nodes, subj, f, facts.get(f))
                    edges.append(Edge(rid, fid, "derived_from"))
                for sid in r.sourceIds:
                    nid = f"source:{sid}"
                    nodes.setdefault(nid, Node(nid, "source", f"{sid} ({'verified' if src[sid].verified else 'unverified'})"))
                    edges.append(Edge(rid, nid, "sourced_from"))
                exc = [e for e in r.exceptions if dsl.evaluate(e, facts) is True]
                if exc:
                    blocked.append({"rule": r.id, "subject": subj, "exception": exc[0]})
                    bid = f"blocked:{r.id}@{subj}"
                    nodes[bid] = Node(bid, "blocked", f"{r.id} suppressed by exception @{subj}")
                    for f in _leaf_facts(exc[0]):
                        edges.append(Edge(_fact_node(nodes, subj, f, facts.get(f)), rid, "suppresses"))
                    continue
                fired.append((r.id, subj, depth))
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
                        fid = _fact_node(nodes, tgt, name, val)
                        nodes[fid].kind = "fact"
                        nodes[fid].data["derived"] = True
                        edges.append(Edge(fid, rid, "derived_from"))
                    elif c.get("kind") == "finding":
                        fid = f"finding:{r.id}:{c['claim']}@{subj}"
                        f = Finding(fid, subj, c["claim"], c.get("effect", "support"), r.id, depth, basis=basis)
                        findings.append(f)
                        nodes[fid] = Node(fid, "finding", f"{c['claim']} ({f.effect}) @{subj}",
                                          {"scope": c.get("scope"), "depth": depth})
                        edges.append(Edge(fid, rid, "derived_from"))
        if not progressed:
            break
    for r in ordered:
        for subj in (sorted(s for s in base if s != "chart") if r.subject == "palace" else ["chart"]):
            if (r.id, subj) not in done:
                facts = facts_of(subj)
                missing = sorted({f for f in _leaf_facts(r.conditions) if f not in facts})
                pending.append({"rule": r.id, "subject": subj, "missing_facts": missing})
    return InferenceResult(nodes, edges, findings, derived, pending, blocked, conflicts, fired)
