"""Conflict classification between clusters/evidence. Never sums or ranks. Types:
  (no tension)       different aspect or different star anchor: the findings simply coexist and are never compared
  both_hold          opposite valence, same star anchor, different triggers that are ALL satisfied (both rules fired): two forces coexist, no book orders them
  refinement         one rule's conditions strictly contain the other's: the specific one qualifies the general (general stays the baseline)
  school_divergence  same trigger, opposite valence, different books: both shown, neither preferred
  unresolved         same trigger, opposite valence, same book: a real conflict, reported as such
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .evidence import Cluster, Evidence

MATRIX = json.loads((Path(__file__).resolve().parent.parent.parent / "data" / "deep" / "conflict_matrix.json").read_text("utf-8"))
_DISTINCT = ("palace.dignity.", "palace.tuan", "palace.triet", "palace.tu_hoa", "palace.tam_phuong_tu_hoa", "palace.tam_phuong_stars", "palace.own_stars", "palace.branch")


@dataclass
class Tension:
    kind: str
    subject: str
    aspect: str
    a: str                      # rule ids
    b: str
    condition: list[str] = field(default_factory=list)
    explanation: str = ""
    matrix_ids: list[str] = field(default_factory=list)


def _key(leaf):
    return (leaf[0], repr(leaf[2]))


FACT_VI = [("palace.dignity.", "độ sáng của {0}"), ("palace.own_stars", "{0} cùng cung"), ("palace.own_major_stars", "chính tinh {0} cùng cung"),
           ("palace.tam_phuong_stars", "{0} trong tam phương"), ("palace.tam_phuong_majors", "chính tinh {0} trong tam phương"),
           ("palace.tam_phuong_tu_hoa", "{0} trong tam phương"), ("palace.tu_hoa", "{0} tại cung"), ("palace.tuan", "Tuần tại cung"),
           ("palace.triet", "Triệt tại cung"), ("palace.branch", "cung tại {0}"), ("palace.neighbor_stars", "{0} giáp cung"), ("palace.neighbor_majors", "{0} giáp cung")]


def _vi(leaf) -> str:
    f, op, v = leaf
    val = ", ".join(v) if isinstance(v, list) else str(v)
    for pre, tpl in FACT_VI:
        if f.startswith(pre):
            return tpl.format(f[len(pre):] if pre.endswith(".") else val) + (f" = {val}" if pre.endswith(".") else "")
    return f"{f} {op} {val}"


def _trigger(e: Evidence, other: Evidence) -> list[str]:
    """Leaves of e that the other rule does not share, in Vietnamese (the part of e's trigger that is specific to it)."""
    ko = {_key(x) for x in other.leaves}
    return sorted({_vi(x) for x in e.leaves if _key(x) not in ko and x[0] != "palace.name"})


def classify(a: Evidence, b: Evidence) -> Tension | None:
    """Two findings are comparable only if they are about the same palace and the same aspect (or, for the un-aspected bucket, the same star); everything else simply coexists.
    Both findings fired, so both triggers hold in this chart: the question is whether a book orders them, not which one 'wins'."""
    if a.aspect != b.aspect or a.aspect == "nhan_dien":
        return None
    if a.aspect == "tong_hop" and not set(a.anchors) & set(b.anchors):
        return None      # an un-aspected bucket is too coarse to compare unless both hang on the same star
    if {a.polarity, b.polarity} != {"thuan", "nghich"}:
        return None
    ka, kb = {_key(x) for x in a.leaves}, {_key(x) for x in b.leaves}
    mk = lambda kind, expl, cond=(): Tension(kind, a.subject if a.subject == b.subject else f"{a.subject} / {b.subject}", a.aspect, a.rule_id, b.rule_id, list(cond), expl)
    ta, tb = _trigger(a, b), _trigger(b, a)
    if ka < kb or kb < ka:
        spec, gen = (b, a) if ka < kb else (a, b)
        return mk("refinement", f"{gen.rule_id} là nhận định nền; {spec.rule_id} chỉ thêm điều kiện ({'; '.join(_trigger(spec, gen)) or '—'}) nên điều chỉnh nó khi điều kiện ấy có mặt. Hai điều kiện cùng thỏa trong lá số này, vì vậy nhận định nền được đọc kèm điều chỉnh.", ta + tb)
    if ta or tb:
        return mk("both_hold", f"Cả hai cùng đúng trong lá số vì hai điều kiện kích hoạt khác nhau đều thỏa: (1) {'; '.join(ta) or 'điều kiện chung'} → thiên về {'nâng đỡ' if a.polarity == 'thuan' else 'hạn chế'}; (2) {'; '.join(tb) or 'điều kiện chung'} → thiên về {'nâng đỡ' if b.polarity == 'thuan' else 'hạn chế'}. "
                  "Sách trong bộ quy tắc không xếp thứ tự giữa hai lực này, nên đọc là hai mặt đồng thời (có thuận có nghịch), không phải một bên triệt tiêu bên kia.", ta + tb)
    if not set(a.schools) & set(b.schools):
        return mk("school_divergence", f"Hai nhận định đến từ hai sách khác nhau ({', '.join(a.schools)} / {', '.join(b.schools)}), cùng điều kiện, ngược chiều; hệ thống không ưu tiên sách nào.")
    return mk("unresolved", "Hai quy tắc cùng sách, cùng điều kiện nhưng ngược chiều; chưa có căn cứ để chọn nên được báo như một mâu thuẫn thật.")


def find_tensions(clusters: list[Cluster]) -> list[Tension]:
    """Compared within (chapter, aspect): the palaces that narrate the same topic. Pairs are ordered by rule id so output is deterministic."""
    out, seen = [], set()
    by_scope: dict[tuple, list[Evidence]] = {}
    for c in clusters:
        by_scope.setdefault((c.chapter, c.aspect), []).extend(c.items)
    for _, evs in sorted(by_scope.items()):
        evs = sorted(evs, key=lambda e: (e.rule_id, e.claim))
        for i, a in enumerate(evs):
            for b in evs[i + 1:]:
                t = classify(a, b)
                if t and (t.a, t.b) not in seen:
                    seen.add((t.a, t.b))
                    out.append(t)
    return out


def matrix_hits(palaces: list[dict], year_stem: str) -> list[dict]:
    """Which known source tensions actually touch THIS chart."""
    hit = []
    has = lambda f: any(f(p) for p in palaces)
    for e in MATRIX["entries"]:
        t = e["trigger"]
        if (t == "year_stem:Nhâm" and year_stem == "Nhâm") or (t == "tuan_triet" and has(lambda p: p["tuan"] or p["triet"])) or \
           (t == "sat_pha_tham" and has(lambda p: "Thất Sát" in p["major_stars"] or "Phá Quân" in p["major_stars"] or "Tham Lang" in p["major_stars"])) or \
           (t.startswith("cu_mon") and has(lambda p: "Cự Môn" in p["major_stars"] and p["branch"] in ("Tý", "Ngọ"))) or \
           (t.endswith("kinh_ngo") and has(lambda p: "Kình Dương" in p["stars"] and p["branch"] == "Ngọ")) or \
           (t == "tu_phu_dong_cung" and has(lambda p: "Tử Vi" in p["major_stars"] and "Thiên Phủ" in p["major_stars"])):
            hit.append(e)
    return hit
