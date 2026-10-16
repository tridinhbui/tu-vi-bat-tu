"""KnowledgeRule + Source schemas and the pack loader/validator (Phase 2 foundation)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from . import dsl

REVIEW = {"draft", "verified", "disputed"}
SYSTEMS = {"tu_vi", "bat_tu"}


@dataclass
class Source:
    id: str
    title: str
    author: str | None
    locator: str | None        # chapter/page — None until actually checked
    verified: bool = False
    edition: str | None = None
    note: str | None = None


@dataclass
class KnowledgeRule:
    id: str
    system: str
    schoolId: str
    category: str
    description: str
    conditions: dict
    consequences: list[dict]
    exceptions: list[dict] = field(default_factory=list)
    conflictsWith: list[str] = field(default_factory=list)
    priority: int = 0
    sourceIds: list[str] = field(default_factory=list)
    reviewStatus: str = "draft"
    version: str = "0.1.0"
    subject: str = "chart"   # "chart" or "palace" (evaluated once per palace)


def validate_pack(rules: list[KnowledgeRule], sources: list[Source], known_facts: set[str]) -> list[str]:
    """Return a list of problems (empty = valid). Enforces: verified rules need verified sources."""
    errs: list[str] = []
    src = {s.id: s for s in sources}
    ids = {r.id for r in rules}
    if len(ids) != len(rules):
        errs.append("duplicate rule ids")
    for r in rules:
        if r.system not in SYSTEMS:
            errs.append(f"{r.id}: bad system")
        if r.reviewStatus not in REVIEW:
            errs.append(f"{r.id}: bad reviewStatus")
        try:
            dsl.validate(r.conditions, known_facts)
            for e in r.exceptions:
                dsl.validate(e, known_facts)
        except dsl.RuleError as e:
            errs.append(f"{r.id}: {e}")
        for sid in r.sourceIds:
            if sid not in src:
                errs.append(f"{r.id}: unknown source {sid}")
        for c in r.conflictsWith:
            if c not in ids:
                errs.append(f"{r.id}: conflictsWith unknown rule {c}")
        if r.reviewStatus == "verified" and not (r.sourceIds and all(src[s].verified for s in r.sourceIds if s in src)):
            errs.append(f"{r.id}: 'verified' requires verified sources with locator")
        if not r.consequences:
            errs.append(f"{r.id}: no consequences")
    return errs


def load_pack(path: Path) -> tuple[list[KnowledgeRule], list[Source]]:
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return [KnowledgeRule(**r) for r in d["rules"]], [Source(**s) for s in d["sources"]]
