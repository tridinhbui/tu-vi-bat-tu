"""Evidence layer: findings -> Evidence (with page cite, school, leaf conditions) -> Cluster (same palace + aspect + anchor star).
Duplicates are removed by (palace, claim); corroboration counts DISTINCT books, not rules (several rules from one book are one voice)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import taxonomy as tx

SCHOOL = {"SRC_THUC_HANH": "Thực Hành", "SRC_KHAO_LUAN": "Khảo Luận", "SRC_TOAN_THU": "Toàn Thư", "SRC_TVDS_TAN_BIEN": "Tân Biên (nháp)", "SRC_TVNL_TOAN_THU": "Nghiệm Lý (Thiên Lương)", "SRC_TVNL_1974": "Nghiệm Lý 1974 (Thiên Lương)"}
_CITE = re.compile(r"\[((?:TH|KL|TT|TL|NL)[^\]]*?)\]")


@dataclass
class Evidence:
    rule_id: str
    subject: str
    palace: str | None
    claim: str
    label: str
    effect: str
    basis: str                   # verified | draft  (as stored on the rule; never upgraded here)
    schools: list[str]
    cites: list[str]
    leaves: list[tuple]          # (fact, operator, value) of the rule's conditions
    anchors: list[str]
    aspect: str
    valence: str
    description: str = ""

    @property
    def polarity(self) -> str:
        """thuan | nghich | trung_tinh. A rule whose effect is 'limit' always limits, whatever the claim words suggest."""
        return "nghich" if (self.effect == "limit" or self.valence == "nghich") else "thuan" if self.valence == "thuan" else "trung_tinh"


@dataclass
class Cluster:
    key: tuple
    subject: str
    palace: str | None
    aspect: str
    anchor: str | None
    chapter: str
    items: list[Evidence] = field(default_factory=list)

    @property
    def books(self) -> list[str]:
        return sorted({s for e in self.items for s in e.schools})

    @property
    def verified(self) -> bool:
        return any(e.basis == "verified" for e in self.items)


def _leaves(expr, out):
    if "fact" in expr:
        out.append((expr["fact"], expr.get("operator", "eq"), expr.get("value")))
    elif "ref" in expr:
        out.append((f"ref:{expr['ref']}:{expr.get('fact', '')}", expr.get("operator", "eq"), expr.get("value")))
    else:
        v = expr["count"] if "count" in expr else expr[next(iter(expr))]
        for x in (v if isinstance(v, list) else [v]):
            if isinstance(x, dict):
                _leaves(x, out)
    return out


def _anchors(leaves) -> list[str]:
    out = []
    for f, _, v in leaves:
        for x in (v if isinstance(v, list) else [v]):
            if isinstance(x, str) and x in tx.MAJORS and x not in out and not f.startswith("palace.tam_phuong"):
                out.append(x)
    return out


def build(findings, rules, claims_vi) -> list[Evidence]:
    rmap = {r.id: r for r in rules}
    seen: set[tuple] = set()
    out = []
    for f in findings:
        r = rmap[f.rule_id]
        key = (f.subject, f.claim, f.effect, r.id)
        if key in seen:
            continue
        seen.add(key)
        leaves = _leaves(r.conditions, [])
        pal = f.subject.split(":", 1)[1] if ":" in f.subject else None
        cites = _CITE.findall(r.description)
        out.append(Evidence(r.id, f.subject, pal, f.claim, (claims_vi.get(f.claim) or {}).get("label", f.claim), f.effect, f.basis,
                            sorted({SCHOOL.get(s, s) for s in r.sourceIds}), cites, leaves, _anchors(leaves),
                            tx.aspect_of(f.claim, pal), tx.valence_of(f.claim), r.description))
    return out


def cluster(evs: list[Evidence]) -> list[Cluster]:
    """Group by (subject, aspect, anchor). A rule that reaches the same (subject, claim) from several books stays ONE evidence line per rule but
    one cluster; classification labels (nhan_dien) get their own cluster per subject and are never narrated as readings."""
    cl: dict[tuple, Cluster] = {}
    for e in evs:
        anchor = e.anchors[0] if e.anchors else None
        key = (e.subject, e.aspect, anchor)
        if key not in cl:
            cl[key] = Cluster(key, e.subject, e.palace, e.aspect, anchor, tx.chapter_of(e.subject, e.aspect))
        cl[key].items.append(e)
    return sorted(cl.values(), key=lambda c: (c.subject != "palace:Mệnh", c.subject, c.aspect, c.anchor or ""))
