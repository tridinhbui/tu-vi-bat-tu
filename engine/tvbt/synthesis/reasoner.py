"""Symbolic synthesis & reasoning over the Semantic IR.

Pipeline (each step is a pure function, deterministic, auditable):
  1. group      SemanticEvidence -> Proposition (one concept in one palace). Only role='asserts'/'mitigates' evidence builds a proposition.
  2. dedup      inside a proposition, evidence standing on the SAME chart facts (same normalised root) is ONE voice, however many books or rules
                repeat it; a root that shares a chart fact with an earlier root counts half (it is not an independent ground).
  3. relate     explicit relations only: data/semantic/relations.json (he_thong frames) + book sentences that pair two concepts themselves.
  4. resolve    `contradicts` pairs are classified by their conditions, never by counting:
                  refinement         one side's facts strictly contain the other's: the specific one qualifies the general (both are kept)
                  both_hold          different facts, both satisfied in this chart: two forces coexist; no book orders them
                  school_divergence  same facts, different books, opposite readings
                  unresolved         same facts, same book, opposite readings: a real conflict, reported as such
                a `rescue` proposition mitigates outcome propositions of its palace that stand on one of its anchor stars.
  5. prioritise salience = structural weight of the palace for the chapter × Σ over independent roots (1 + anchor + specificity) + 0.5 per extra
                book. It orders themes; it is never shown as a probability or an accuracy.
  6. graph      Theme -> main proposition -> supports -> counters -> conditions, every node carrying rule ids and chart facts.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .semantics import SemanticEvidence, lexicon

MAJORS = {"Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh", "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn",
          "Thiên Tướng", "Thiên Lương", "Thất Sát", "Phá Quân", "Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"}
STRONG = {"Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt", "Lộc Tồn", "Thiên Mã", "Kình Dương", "Đà La", "Hỏa Tinh",
          "Linh Tinh", "Địa Không", "Địa Kiếp"}


@dataclass
class Root:
    atoms: tuple
    evidence: list[SemanticEvidence]
    weight: float = 1.0                    # 1.0 independent, 0.5 when it shares a chart fact with an earlier root of the same proposition

    @property
    def books(self) -> list[str]:
        return sorted({s for e in self.evidence for s in e.schools})

    @property
    def rules(self) -> list[str]:
        return sorted({e.rule_id for e in self.evidence})


@dataclass
class Proposition:
    id: str
    concept: str
    facet: str
    domain: str
    kind: str
    palace: str
    polarity: str
    evidence: list[SemanticEvidence] = field(default_factory=list)
    roots: list[Root] = field(default_factory=list)
    salience: float = 0.0
    salience_parts: dict = field(default_factory=dict)

    @property
    def books(self) -> list[str]:
        return sorted({s for e in self.evidence for s in e.schools})

    @property
    def rules(self) -> list[str]:
        return sorted({e.rule_id for e in self.evidence})

    @property
    def modality(self) -> str:
        ms = {e.modality for e in self.evidence}
        for m in ("tendency", "limitation", "rescue", "condition", "potential"):
            if m in ms:
                return m
        return "tendency"

    @property
    def sensitive(self) -> bool:
        return any(e.sensitive for e in self.evidence)

    @property
    def best(self) -> SemanticEvidence:
        return max(self.evidence, key=lambda e: (len(e.root), e.rule_id))


@dataclass
class Edge:
    a: str                                  # proposition ids
    b: str
    type: str                               # supports | qualifies | contradicts | amplifies | mitigates | elaborates | conditions
    frame: str = ""
    synth: str = ""
    basis: str = "he_thong"                 # he_thong | sach | dieu_kien
    resolution: str = ""                    # for contradicts: refinement | both_hold | school_divergence | unresolved
    detail: dict = field(default_factory=dict)
    attested: list = field(default_factory=list)


# ---------------------------------------------------------------- 1-2 group + dedup

def group(evidence: list[SemanticEvidence]) -> dict[str, Proposition]:
    props: dict[str, Proposition] = {}
    for e in evidence:
        if e.role == "limits":
            continue                         # a limiting reading of a positive concept is carried by the opposite proposition (see semantics)
        pid = f"{e.concept}@{e.palace or 'chart'}"
        p = props.get(pid)
        if p is None:
            p = props[pid] = Proposition(pid, e.concept, e.facet, e.domain, e.kind, e.palace or "chart", e.polarity)
        p.evidence.append(e)
    for p in props.values():
        p.polarity = _majority([e.polarity for e in p.evidence])
        by_root: dict[tuple, list] = {}
        for e in sorted(p.evidence, key=lambda e: (len(e.root), e.rule_id)):
            by_root.setdefault(e.root, []).append(e)
        roots = []
        for atoms, evs in sorted(by_root.items(), key=lambda kv: (len(kv[0]), kv[0])):
            w = 0.5 if any(root_stars(r.atoms) & root_stars(atoms) or set(r.atoms) & set(atoms) for r in roots) else 1.0
            roots.append(Root(atoms, evs, w))
        p.roots = roots
    return props


def root_stars(atoms) -> set[str]:
    """Stars a root stands on, whatever the location class (in palace / tam phương / dignity): two roots naming the same star share a fact."""
    out = set()
    for a in atoms:
        k, _, v = a.partition(":")
        if k in ("own", "tp", "nb"):
            out.add(v)
        elif k == "dig":
            out.add(v.split(":")[0])
    return out


def _majority(pols: list[str]) -> str:
    n = {x: pols.count(x) for x in "+-~"}
    return max("+-~", key=lambda x: (n[x], x == "~"))


# ---------------------------------------------------------------- 3-4 relate + resolve

def _rel_index():
    idx: dict[frozenset, dict] = {}
    for r in lexicon()["relations"]:
        idx[frozenset((r["a"], r["b"]))] = r
    return idx


def _trigger_texts(p: Proposition) -> list[str]:
    out = []
    for r in p.roots:
        t = r.evidence[0].trigger_text
        if t and t not in out:
            out.append(t)
    return out


def classify_contradiction(a: Proposition, b: Proposition) -> tuple[str, dict]:
    """Classify two opposed propositions by the facts their roots stand on. Every root pair is examined: a strict containment anywhere makes
    it a refinement (the specific reading qualifies the general one); an identical root makes it a school divergence or a real conflict."""
    pairs = [(ra, rb) for ra in a.roots for rb in b.roots]
    rank = lambda p: (0 if set(p[0].atoms) < set(p[1].atoms) or set(p[1].atoms) < set(p[0].atoms) else 1 if p[0].atoms == p[1].atoms else 2,
                      -len(set(p[0].atoms) & set(p[1].atoms)), -len(p[0].atoms) - len(p[1].atoms))
    ra, rb = min(pairs, key=rank)
    sa, sb = set(ra.atoms), set(rb.atoms)
    detail = {"a_trigger": ra.evidence[0].trigger_text, "b_trigger": rb.evidence[0].trigger_text, "a_books": ra.books, "b_books": rb.books,
              "a_rules": ra.rules, "b_rules": rb.rules, "same_palace": a.palace == b.palace}
    if a.palace == b.palace and (sa < sb or sb < sa):
        spec, gen = (b, a) if sa < sb else (a, b)
        rs, rg = (rb, ra) if sa < sb else (ra, rb)
        detail.update(specific=spec.id, general=gen.id, extra=sorted((sb - sa) if sa < sb else (sa - sb)),
                      specific_trigger=rs.evidence[0].trigger_text, general_trigger=rg.evidence[0].trigger_text,
                      specific_books=rs.books, general_books=rg.books, specific_rules=rs.rules, general_rules=rg.rules,
                      specific_reading=rs.evidence[0].segment, general_reading=rg.evidence[0].segment)
        return "refinement", detail
    if sa != sb or a.palace != b.palace:
        return "both_hold", detail
    if not set(ra.books) & set(rb.books):
        return "school_divergence", detail
    return "unresolved", detail


def relate(props: dict[str, Proposition], pairings: dict[frozenset, list[dict]] | None = None) -> list[Edge]:
    idx = _rel_index()
    pairings = pairings or {}
    plist = sorted(props.values(), key=lambda p: p.id)
    edges: list[Edge] = []
    for i, a in enumerate(plist):
        for b in plist[i + 1:]:
            rel = idx.get(frozenset((a.concept, b.concept)))
            if rel is None:
                continue
            x, y = (a, b) if rel["a"] == a.concept else (b, a)
            e = Edge(x.id, y.id, rel["type"], rel.get("frame", ""), rel.get("synth", ""))
            # book attestation: a fired rule pairs the two concepts in ONE sentence, else the library does
            same = sorted({ev.rule_id for ev in x.evidence if y.concept in ev.paired_with} | {ev.rule_id for ev in y.evidence if x.concept in ev.paired_with})
            if same:
                e.basis, e.attested = "sach", [{"rule": r, "scope": "lá số này"} for r in same]
            elif frozenset((x.concept, y.concept)) in pairings:
                e.attested = [{**d, "scope": "câu sách ở điều kiện khác"} for d in pairings[frozenset((x.concept, y.concept))][:2]]
            if rel["type"] == "contradicts":
                e.resolution, e.detail = classify_contradiction(x, y)
                e.basis = "dieu_kien"
            elif a.palace != b.palace:
                e.detail = {"cross_palace": [x.palace, y.palace]}
            edges.append(e)
    # rescue: a mitigating proposition softens outcome propositions of its palace anchored on one of its stars
    for m in plist:
        if m.kind != "rescue":
            continue
        stars = {s for ev in m.evidence for s in ev.stars}
        for p in plist:
            if p.palace == m.palace and p.polarity == "-" and p.kind in ("outcome", "timing") and p.id != m.id:
                hit = sorted(stars & {s for ev in p.evidence for s in ev.stars})
                if hit:
                    edges.append(Edge(m.id, p.id, "mitigates", "rescue", basis="sach",
                                      detail={"stars": hit, "rescue_reading": m.best.reading, "rescue_rules": m.rules},
                                      attested=[{"rule": r, "scope": "lá số này"} for r in m.rules]))
    return edges


# ---------------------------------------------------------------- 5 prioritise

def salience(p: Proposition, chapter: str, than_palace: str | None) -> tuple[float, dict]:
    weights = lexicon()["ontology"]["palace_weight"].get(chapter, {})
    w = weights.get(p.palace, 0)
    if than_palace and p.palace == than_palace:
        w = max(w, weights.get("Thân", 0))
    if p.palace == "chart":
        w = max(w, 1)
    parts = []
    total = 0.0
    for r in p.roots:
        stars = {s for e in r.evidence for s in e.stars}
        anchor = 1.0 if stars & MAJORS else 0.5 if stars & STRONG else 0.25
        spec = min(max(len(r.atoms) - 1, 0), 3) * 0.25
        score = r.weight * (1 + anchor + spec)
        total += score
        parts.append({"root": list(r.atoms), "rules": r.rules, "books": r.books, "independence": r.weight, "anchor": anchor, "specificity": spec, "score": round(score, 3)})
    books = max(len(p.books) - 1, 0) * 0.5
    s = round(w * total + books, 3)
    return s, {"palace_weight": w, "roots": parts, "book_bonus": books, "formula": "palace_weight × Σ independence·(1 + anchor + specificity) + 0.5·(books − 1)",
               "note": "thứ tự ưu tiên trình bày, không phải xác suất hay độ chính xác"}


# ---------------------------------------------------------------- 6 graph

@dataclass
class Theme:
    facet: str
    name: str
    main: Proposition
    members: list[Proposition]
    supports: list[tuple[Proposition, Edge | None]]
    counters: list[tuple[Proposition, Edge | None]]
    conditions: list[Edge]
    salience: float

    def to_dict(self) -> dict:
        P = lambda p: {"id": p.id, "concept": p.concept, "palace": p.palace, "polarity": p.polarity, "salience": p.salience,
                       "rules": p.rules, "books": p.books, "triggers": _trigger_texts(p), "independent_roots": sum(r.weight for r in p.roots)}
        E = lambda e: None if e is None else {"a": e.a, "b": e.b, "type": e.type, "frame": e.frame, "basis": e.basis, "resolution": e.resolution,
                                              "attested": e.attested, "detail": e.detail}
        return {"facet": self.facet, "name": self.name, "salience": self.salience, "main": P(self.main),
                "supports": [{"prop": P(p), "edge": E(e)} for p, e in self.supports],
                "counters": [{"prop": P(p), "edge": E(e)} for p, e in self.counters],
                "conditions": [E(e) for e in self.conditions]}


def build_themes(props: list[Proposition], edges: list[Edge], facets: list[str], chapter: str, than_palace: str | None) -> list[Theme]:
    """Themes for a chapter: one per facet in `facets` that has propositions. Supports/counters may come from any proposition passed in
    (cross-palace), but only through an explicit edge or the same facet."""
    onto = lexicon()["ontology"]["facets"]
    for p in props:
        p.salience, p.salience_parts = salience(p, chapter, than_palace)
    pid = {p.id: p for p in props}
    themes = []
    for fc in facets:
        mem = sorted([p for p in props if p.facet == fc and p.salience > 0], key=lambda p: (-p.salience, p.id))
        if not mem:
            continue
        main = next((p for p in mem if p.kind != "rescue"), mem[0])
        sup, cnt, cond, used = [], [], [], {main.id}
        for e in edges:
            if main.id not in (e.a, e.b):
                continue
            o = pid.get(e.b if e.a == main.id else e.a)
            if o is None or o.id in used:
                continue
            if e.type in ("supports", "elaborates", "amplifies"):
                sup.append((o, e)); used.add(o.id)
            elif e.type in ("qualifies", "contradicts"):
                cnt.append((o, e)); used.add(o.id)
            elif e.type in ("mitigates", "conditions"):
                cond.append(e); used.add(o.id)
        for p in mem:
            if p.id in used or p.kind == "rescue":
                continue
            used.add(p.id)
            (sup if p.polarity == main.polarity or "~" in (p.polarity, main.polarity) else cnt).append((p, None))
        # a same-concept proposition in another palace brings its own contradictions (e.g. the Tứ Mộ refinement of Hóa Lộc at Mệnh)
        for p, _ in list(sup):
            if p.concept != main.concept:
                continue
            for e in edges:
                if e.type == "contradicts" and p.id in (e.a, e.b):
                    o = pid.get(e.b if e.a == p.id else e.a)
                    if o is not None and o is not main:
                        cnt.append((o, e))
        # one entry per counter proposition: the most informative relation wins (a condition-based refinement or real conflict
        # explains more than 'both hold', and a same-palace relation more than a cross-palace one)
        rank = lambda pe: (pe[1] is None, {"refinement": 0, "unresolved": 0, "school_divergence": 0}.get(pe[1].resolution if pe[1] else "", 1),
                           pe[0].palace != main.palace)
        best: dict[str, tuple] = {}
        for pe in cnt:
            if pe[0].id not in best or rank(pe) < rank(best[pe[0].id]):
                best[pe[0].id] = pe
        cnt = sorted(best.values(), key=lambda pe: (rank(pe), -pe[0].salience, pe[0].id))
        # second-order: conditions/mitigations that touch the counters too
        for e in edges:
            if e.type in ("mitigates", "conditions") and e not in cond and ({e.a, e.b} & {p.id for p, _ in cnt + sup}):
                cond.append(e)
        sal = round(main.salience + 0.25 * sum(p.salience for p in mem[1:]), 3)
        themes.append(Theme(fc, onto[fc]["name"], main, mem, sup, cnt, cond, sal))
    return sorted(themes, key=lambda t: (-t.salience, t.facet))
