"""Paragraph objects and the small amount of grammar the chapters share.

A paragraph never mixes schools: `school` is one of hellenistic / traditional / modern, or 'compare' for the paragraphs
that set two schools' results side by side (and say so). Every paragraph carries the chart evidence it rests on and the
source pages; `steps` is the reasoning shown in Đọc sâu.
"""
from __future__ import annotations

import hashlib
import re
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
    method: str = ""                      # how the source works, the same for every chart: shown in Đọc sâu, not in the text
    layer: str = ""                       # 'summary' (Đọc nhanh: the chapter's plain-language thesis), 'analysis' (the school paragraphs
                                          # of the main part), 'deep' (Đọc sâu); `level` stays what the paywall cuts by

    def __post_init__(self):
        if not self.layer:
            self.layer = "analysis" if self.level == "overview" else "deep"
        seen = set()
        self.evidence = [e for e in self.evidence if (e["kind"], e["id"]) not in seen and not seen.add((e["kind"], e["id"]))]
        """Sentences wrapped in ⟦…⟧ by the chapters are method talk: they move to `method`, the text keeps what is about this chart."""
        found = re.findall(r"⟦(.*?)⟧\s*", self.text, flags=re.S)
        if found:
            self.method = " ".join(x.strip() for x in found if x.strip())
            self.text = re.sub(r"⟦.*?⟧\s*", "", self.text, flags=re.S).strip()
            self.text = self.text[:1].upper() + self.text[1:]

    def as_dict(self) -> dict:
        return asdict(self)


def srcs(*refs: str) -> list[dict]:
    return [src(r) for r in refs if r]


def ev_planet(chart: dict, p: str, house: int | None = None, house_label: str = "Nhà") -> dict:
    lab = at(chart, p)
    if house:
        lab += f", {house_label} {house}"
    return {"kind": "planet", "id": p, "label": lab}


EV_SYSTEM = {"traditional": ("lilly", "Lilly"), "hellenistic": ("whole_sign", "trọn cung"), "ptolemy": ("ptolemy", "Ptolemy")}


def ev_in(f, p: str, school: str) -> dict:
    """A planet as evidence of a `school` paragraph, with the house that school reads it in and the house system named, so the
    chip and the wheel never show a number from another system."""
    n = f.house(school, p) if f.time_known else None
    key, short = EV_SYSTEM.get(school, (f.c["houses"]["system"] if f.time_known else None, None))
    short = short or (key or "").replace("_", " ").title()
    lab = at(f.c, p) + (f", {'chỗ' if school == 'ptolemy' else 'Nhà'} {n} ({short})" if n else "")
    return {"kind": "planet", "id": p, "label": lab, **({"house": n, "system": key} if n else {})}


def ev_house(n: int, label: str, system: str | None = None) -> dict:
    return {"kind": "house", "id": str(n), "label": label, **({"system": system} if system else {})}


def ev_point(chart: dict, k: str) -> dict:
    return {"kind": "point", "id": k, "label": at(chart, k)}


def ev_star(chart: dict, k: str) -> dict:
    st = chart["fixed_stars"][k]
    return {"kind": "star", "id": k, "label": f"{st['name'].split(' (')[0]} {st['fmt']}"}


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
