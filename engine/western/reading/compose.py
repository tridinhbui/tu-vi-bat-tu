"""Paragraph objects and the small amount of grammar the chapters share.

A paragraph never mixes schools: `school` is one of hellenistic / traditional / modern, or 'compare' for the paragraphs
that set two schools' results side by side (and say so). Every paragraph carries the chart evidence it rests on and the
source pages; `steps` is the reasoning shown in Đọc sâu.
"""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field

from .vocab import P, S, at, src

TIER = {"calc": "calc", "src": "src", "hyp": "hyp"}


@dataclass
class Para:
    id: str
    heading: str
    text: str
    school: str
    sources: list[dict]
    evidence: list[dict] = field(default_factory=list)
    level: str = "deep"                   # "overview" paragraphs make the short reading; Đọc sâu shows all
    tier: str = "src"
    steps: list[str] = field(default_factory=list)
    polarity: int = 0                     # +1 supports, -1 hinders, 0 neutral (used by the audit)
    topic: str = ""
    keys: list[str] = field(default_factory=list)     # chart facts this paragraph asserts (audit: contradictions)

    def as_dict(self) -> dict:
        return asdict(self)


def srcs(*refs: str) -> list[dict]:
    return [src(r) for r in refs if r]


def ev_planet(chart: dict, p: str, house: int | None = None, house_label: str = "Nhà") -> dict:
    lab = at(chart, p)
    if house:
        lab += f", {house_label} {house}"
    return {"kind": "planet", "id": p, "label": lab}


def ev_house(n: int, label: str) -> dict:
    return {"kind": "house", "id": str(n), "label": label}


def ev_point(chart: dict, k: str) -> dict:
    return {"kind": "point", "id": k, "label": at(chart, k)}


def ev_aspect(a: str, b: str, kind: str, label: str) -> dict:
    return {"kind": "aspect", "id": f"{a}-{kind}-{b}", "label": label}


def pick(seed: str, options: list[str]) -> str:
    """Deterministic choice: the same chart always reads the same, different charts vary."""
    h = int(hashlib.sha1(seed.encode("utf-8")).hexdigest()[:8], 16)
    return options[h % len(options)]


def listing(items: list[str], n: int | None = None) -> str:
    items = [i for i in items if i][: n or len(items)]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " và " + items[-1]


def cap(s: str) -> str:
    return s[:1].upper() + s[1:] if s else s


def planet_list(ps: list[str]) -> str:
    return listing([P(p) for p in ps])


def sign_list(ss: list[str]) -> str:
    return listing([S(s) for s in ss])
