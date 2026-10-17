"""Formation (cách cục) schema: a structure with a life cycle, not a flat rule.

    core        -> the structure is visible at all (without it the state is `khong_hien`)
    boosters    -> evidence that makes it stronger (thành / thành_thượng)
    breakers    -> evidence that breaks it (phá cách)
    rescuers    -> evidence that neutralises named breakers (cứu giải)
    refutations -> counter-evidence shown next to the verdict (phản chứng); lowers a thành by one rung

All five are DSL expressions over the facts of the anchor palace, so they can use the typed positional facts and cross-palace refs.
Formations are DATA. A formation with reviewStatus != verified is never loaded by production (`loader.load_all`).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from . import dsl
from .schema import REVIEW

STATES = ("khong_hien", "hinh_thuc", "thanh", "thanh_thuong", "bi_pha", "pha_duoc_cuu", "chua_du_du_kien")


@dataclass
class Evidence:
    id: str
    label: str
    when: dict
    rescues: list[str] = field(default_factory=list)      # rescuers only: breaker ids ("*" = every breaker)


@dataclass
class Formation:
    id: str
    name_vi: str
    anchor: str
    core: dict
    kind: str = "cat"
    school: str = "experimental_draft"
    boosters: list[Evidence] = field(default_factory=list)
    breakers: list[Evidence] = field(default_factory=list)
    rescuers: list[Evidence] = field(default_factory=list)
    refutations: list[Evidence] = field(default_factory=list)
    thuong_at: int = 2
    sourceIds: list[str] = field(default_factory=list)
    reviewStatus: str = "draft"
    experimental: bool = True
    provenance: str = ""
    note: str = ""
    definition_version: int = 1


def _ev(items: list[dict]) -> list[Evidence]:
    return [Evidence(**i) for i in items]


def from_dict(d: dict) -> Formation:
    d = dict(d)
    for k in ("boosters", "breakers", "rescuers", "refutations"):
        d[k] = _ev(d.get(k, []))
    return Formation(**d)


def load_formations(path: Path) -> list[Formation]:
    return [from_dict(x) for x in json.loads(Path(path).read_text(encoding="utf-8"))["formations"]]


def validate_formations(fs: list[Formation], known_facts: set[str], palace_names: set[str]) -> list[str]:
    errs: list[str] = []
    if len({f.id for f in fs}) != len(fs):
        errs.append("duplicate formation ids")
    for f in fs:
        if f.reviewStatus not in REVIEW:
            errs.append(f"{f.id}: bad reviewStatus")
        if f.reviewStatus == "verified":
            errs.append(f"{f.id}: formations cannot be 'verified' without a verified source with locator (none supported yet)")
        if f.anchor not in palace_names:
            errs.append(f"{f.id}: unknown anchor palace {f.anchor!r}")
        for label, exprs in [("core", [f.core])] + [(k, [e.when for e in getattr(f, k)]) for k in ("boosters", "breakers", "rescuers", "refutations")]:
            for e in exprs:
                try:
                    dsl.validate(e, known_facts)
                except dsl.RuleError as ex:
                    errs.append(f"{f.id}.{label}: {ex}")
        ids = [e.id for k in ("boosters", "breakers", "rescuers", "refutations") for e in getattr(f, k)]
        if len(set(ids)) != len(ids):
            errs.append(f"{f.id}: evidence ids must be unique inside a formation")
        bids = {b.id for b in f.breakers}
        for r in f.rescuers:
            if not r.rescues:
                errs.append(f"{f.id}: rescuer {r.id} rescues nothing")
            for x in r.rescues:
                if x != "*" and x not in bids:
                    errs.append(f"{f.id}: rescuer {r.id} names unknown breaker {x}")
        if not f.boosters:
            errs.append(f"{f.id}: needs at least one booster (else thành is undefined)")
    return errs
