"""Vietnamese narrative grammar: Semantic IR -> discourse plan -> sentence plan -> realisation -> validation.

No template is a fixed sentence about a star. Templates are DISCOURSE FUNCTIONS (claim, grounding, reinforcement, contrast, concession,
condition, sequence, synthesis, reflection) with slots filled from propositions, chart-grounded triggers and book names. Each function has
several equivalent realisations; the choice is deterministic (a hash of the propositions involved) and skips realisations and sentence
openers already used in the chapter, so two charts with different content read differently while the same chart always reads the same.

Discourse state (per chapter) prevents the usual failures of sentence-joining generators:
  * a proposition is narrated in full once; a pair of concepts is related once (whatever palaces repeat it);
  * a condition is named explicitly, and referred back to ('cùng điều kiện ấy') only from the very next sentence of the same paragraph;
  * two grounds that share a chart fact are presented as two views of one fact, never as independent evidence.

Every sentence carries `provenance` (rule ids) and a `basis`:
  sach       the content is a book reading (or a book sentence that itself pairs two readings)
  dieu_kien  the sentence explains how two readings' CONDITIONS relate (refinement / both hold / divergence)
  he_thong   a reading frame or reflection the system defines; always labelled, never presented as a book claim
  tinh_toan  chart facts (positions), no interpretation
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .reasoner import Edge, Proposition, Theme
from .semantics import lexicon, stable_hash

BANNED = [r"\bchắc chắn\b", r"\bnhất định sẽ\b", r"\bđịnh mệnh\b", r"\bsố phận đã\b", r"\bkhông thể tránh\b", r"\btai họa\b", r"\bsẽ bị\b",
          r"\btuyệt đối\b", r"\bluôn luôn\b", r"\bchính xác \d+%"]
CONTENT_KINDS = ("claim", "ground", "support", "contrast", "condition")


@dataclass
class Sentence:
    text: str
    kind: str                       # intro | claim | ground | support | contrast | interaction | condition | reflection | synthesis | limit
    basis: str = "sach"
    provenance: list[str] = field(default_factory=list)
    props: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"text": self.text, "kind": self.kind, "basis": self.basis, "provenance": self.provenance, "props": self.props}


@dataclass
class Paragraph:
    role: str                       # intro | anchor | theme | cross | synthesis
    sentences: list[Sentence] = field(default_factory=list)
    facet: str = ""

    @property
    def text(self) -> str:
        return " ".join(s.text for s in self.sentences)

    def to_dict(self) -> dict:
        return {"role": self.role, "facet": self.facet, "text": self.text, "sentences": [s.to_dict() for s in self.sentences]}


# ---------------------------------------------------------------- realisation resources (discourse functions, not star sentences)

T = {
    "lead_first": ["Ở phương diện {facet}, nét nổi bật nhất là {np}.", "Điều lá số nói rõ nhất về {facet} là {np}.", "Khi xét {facet}, trọng tâm nằm ở {np}."],
    "lead_next": ["Bên cạnh đó, về {facet}, lá số nghiêng về {np}.", "Chuyển sang {facet}, điểm đáng chú ý là {np}.",
                  "Ở một lớp khác — {facet} — nổi lên {np}.", "Về {facet}, điều cần nói đến là {np}."],
    "lead_multi": ["Ở phương diện {facet}, {np} là nét được nhiều căn cứ độc lập cùng chỉ tới.",
                   "Về {facet}, {np} không đến từ một chỉ dấu riêng lẻ mà từ nhiều vị trí sao khác nhau."],
    "ground_one": ["Căn cứ là {trig}, theo {books}.", "Nhận định này xuất phát từ {trig} ({books}).", "Điều đó dựa trên {trig}, như {books} ghi nhận."],
    "ground_shared": ["{books} cùng ghi nhận điều này cho cùng một điều kiện ({trig}), nên đây là một căn cứ được nhiều sách xác nhận chứ không phải nhiều căn cứ riêng.",
                      "Với điều kiện {trig}, {books} đều ghi như vậy; vì chung một dữ kiện gốc, hệ thống tính đây là một căn cứ."],
    "ground_multi": ["Nó không chỉ dựa vào {trig1} ({books1}) mà còn được {trig2} ({books2}) củng cố.",
                     "Có hai nguồn dữ kiện độc lập: {trig1} theo {books1}, và {trig2} theo {books2}."],
    "ground_overlap": ["Điều này được ghi ở hai chỗ — khi {trig1} ({books1}) và khi {trig2} ({books2}); hai điều kiện cùng đứng trên một dữ kiện nên được tính là hai cách nhìn bổ sung, không phải hai căn cứ độc lập.",
                       "Có hai câu cùng chỉ về đây: {trig1} theo {books1}, và {trig2} theo {books2}. Vì chung dữ kiện gốc, đây là một căn cứ được nhìn từ hai phía."],
    "support": ["Cùng chiều với đó, {np} ({trig}).", "{Np} bổ sung thêm cho hướng này, xuất phát từ {trig}.", "Đi kèm còn có {np}, ghi nhận khi {trig}."],
    "support_synth": ["{Np} ({trig}) đi cùng hướng này — {synth}."],
    "support_same": ["{Where} cũng ghi nhận theo cùng chiều ({trig}, {books}).", "Nhận định ấy còn được ghi ở {where} ({trig}, {books})."],
    "support_after_many": ["Đi cùng {short} còn có {items}.", "Gắn với {short} là {items}."],
    "contrast_open": ["Tuy nhiên, lá số cũng ghi nhận {np} khi {trig}.", "Đặt cạnh đó là {np}, xuất phát từ {trig}.", "Mặt khác, {trig} lại gắn với {np}."],
    "frame": {
        "capacity_vs_tendency": ["Hai nhận định này không loại trừ nhau: một bên nói về năng lực, bên kia nói về khuynh hướng đi kèm năng lực ấy. Đọc cùng nhau, chúng phác họa {synth}.",
                                 "Năng lực và khuynh hướng ở đây đi cùng nhau chứ không triệt tiêu nhau; ghép lại, đó là {synth}."],
        "capacity_vs_expression": ["Cần phân biệt năng lực với cách năng lực ấy biểu hiện ra ngoài: {synth}.",
                                   "Điểm cần chú ý là sự khác biệt giữa có năng lực và dùng năng lực ra sao — {synth}."],
        "strength_and_excess": ["Hai nét này là hai đầu của cùng một phẩm chất: {synth}.", "Không nên đọc đây là hai tính cách trái ngược; đúng hơn, {synth}."],
        "inner_vs_outer": ["Cách đọc hợp lý là tách động lực bên trong khỏi hành vi bên ngoài: {synth}.", "Bên trong và bên ngoài ở đây không trùng nhau: {synth}."],
        "potential_vs_retention": ["Khả năng tạo ra và khả năng giữ lại là hai chuyện khác nhau: {synth}.", "Ở đây cần tách chuyện có nguồn lợi với chuyện giữ được nguồn lợi: {synth}."],
        "tendency_vs_circumstance": ["Khuynh hướng và hoàn cảnh để nó biểu hiện không phải là một: {synth}.", "Hai chiều này cùng có mặt, như những mặt khác nhau của cùng một con đường: {synth}."],
        "sequence": ["Về nhịp độ, {synth}.", "Xét theo thời gian, {synth}."],
    },
    "attest_here": ["Chính {book} cũng đặt hai nét này trong cùng một câu: “{reading}”.", "Sự ghép đôi này không phải do hệ thống tự đặt ra: {book} viết “{reading}”."],
    "attest_lib": ["Cách ghép này có tiền lệ trong sách — {book} viết “{reading}” cho một trường hợp khác — nên ở lá số này nó là khung đọc tham khảo."],
    "frame_system": ["Đây là khung diễn giải của hệ thống để nối hai nhận định, không phải một câu sách.", "(Cách nối này là khung đọc của hệ thống, không phải lời sách.)"],
    "refinement": [
        "{gbooks} ghi nhận {gnp} cho trường hợp chung ({gtrig}); {sbooks}, khi xét riêng {strig} — đúng với lá số này — lại ghi {snp}. Nhận định sau có điều kiện cụ thể hơn nhưng sách không nói nó thay thế nhận định trước, nên cả hai được giữ: nét chung vẫn đứng, kèm điều chỉnh của trường hợp riêng.",
        "Ở đây có một quan hệ chung – riêng: với {gtrig}, {gbooks} nói đến {gnp}; còn khi thêm điều kiện {strig} (lá số này thỏa), {sbooks} nghiêng về {snp}. Điều kiện riêng điều chỉnh chứ không xóa nhận định chung.",
    ],
    "both_hold": ["Ở chiều ngược lại, {btrig} lại chỉ về {bnp} ({bbooks}). Cả hai điều kiện cùng có mặt trong lá số và sách không xếp thứ tự giữa chúng, nên đây là hai lực cùng tồn tại chứ không phải bên này xóa bên kia.",
                  "Song {btrig} lại gắn với {bnp} theo {bbooks}. Hai điều kiện kích hoạt khác nhau và đều thỏa, nên bản đọc trung thực là có cả hai, không chọn một."],
    "both_hold_cross": ["{Bnp} lại được ghi ở {bpal} ({btrig}, {bbooks}). {Apal} nói về {atopic}, còn {bpal} nói về {btopic}; hai nhận định thuộc hai tầng khác nhau nên được đọc song song chứ không triệt tiêu nhau.",
                        "Ở {bpal}, {btrig} lại gắn với {bnp} ({bbooks}). Vì {apal} và {bpal} nói về hai chủ đề khác nhau ({atopic} / {btopic}), hai chiều này cùng tồn tại."],
    "school_divergence": ["Ở điểm này, {abooks} và {bbooks} đọc ngược nhau trên cùng một điều kiện ({trig}); hệ thống chưa có căn cứ để chọn nên trình bày cả hai."],
    "unresolved": ["Cùng một sách ({abooks}) đưa ra hai nhận định ngược nhau trên cùng điều kiện ({trig}); đây là mâu thuẫn thật trong nguồn và chưa thể phân xử."],
    "mitigates": ["{book} có ghi một điều kiện làm nhẹ phần bất lợi này: “{reading}”.", "Cũng cần đặt cạnh câu của {book}: “{reading}” — một điều kiện giảm nhẹ mà lá số này thỏa."],
    "conditions": ["Về nhịp độ, {np} ({trig}) cho thấy {synth}.", "Xét theo thời gian, {np} ({trig}): {synth}."],
    "sensitive": "Theo cách luận truyền thống (không phải dự báo), ",
}

PALACE_TOPIC = {"Tài Bạch": "chuyện tiền bạc", "Quan Lộc": "công việc và địa vị", "Phu Thê": "hôn nhân", "Phúc Đức": "đời sống tinh thần và phúc phần",
                "Điền Trạch": "nhà cửa, cơ nghiệp", "Thiên Di": "hoàn cảnh khi ra ngoài xã hội", "Tử Tức": "con cái", "Huynh Đệ": "anh em",
                "Phụ Mẫu": "cha mẹ", "Nô Bộc": "bạn bè, cộng sự", "Tật Ách": "sức khỏe", "Mệnh": "con người và khuynh hướng của chính mình",
                "chart": "thế chung theo năm sinh"}


def pal_vi(p: str) -> str:
    return "tầng chung của lá số (theo năm sinh)" if p == "chart" else f"cung {p}"


class Discourse:
    """Chapter-level discourse state."""

    def __init__(self, chapter: str):
        self.chapter = chapter
        self.used: set = set()
        self.openers: list[str] = []
        self.narrated: set[str] = set()
        self.told_pairs: set[frozenset] = set()
        self.last_trigs: set[str] = set()
        self.cur_trigs: set[str] = set()
        self.anchors: list[str] = []

    def pick(self, key: str, options: list[str], *seed) -> str:
        n = len(options)
        start = stable_hash(self.chapter, key, *seed) % n
        for k in range(n):
            o = options[(start + k) % n]
            if (key, o) not in self.used and _opener(o) not in self.openers[-3:]:
                self.used.add((key, o))
                return o
        for k in range(n):
            o = options[(start + k) % n]
            if _opener(o) not in self.openers[-1:]:
                return o
        return options[start]

    def start_paragraph(self):
        self.last_trigs, self.cur_trigs = set(), set()

    def end_sentence(self, s: "Sentence"):
        self.openers.append(_opener(s.text))
        self.last_trigs, self.cur_trigs = self.cur_trigs, set()

    def trig(self, t: str, ref: bool = True) -> str:
        """A condition is referred back to only from the sentence right after the one that named it."""
        if not t:
            return "các vị trí sao liên quan"
        if ref and t in self.last_trigs and t not in self.cur_trigs:
            self.cur_trigs.add(t)
            return "cùng điều kiện ấy"
        self.cur_trigs.add(t)
        return t

    def pair_told(self, a: Proposition, b: Proposition, palaces: bool = False) -> bool:
        return (frozenset((a.concept, b.concept)), frozenset((a.palace, b.palace)) if palaces else None) in self.told_pairs

    def tell_pair(self, a: Proposition, b: Proposition):
        self.told_pairs.add((frozenset((a.concept, b.concept)), None))
        self.told_pairs.add((frozenset((a.concept, b.concept)), frozenset((a.palace, b.palace))))


def _opener(text: str) -> str:
    w = re.sub(r"[^\wÀ-ỹ ]", " ", text).split()
    return " ".join(w[:2]).lower()


def cap(s: str) -> str:
    return s[:1].upper() + s[1:] if s else s


def books(xs) -> str:
    xs = list(xs)
    if not xs:
        return "bộ quy tắc"
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " và " + xs[-1]


def np_of(p: Proposition) -> str:
    """Noun phrase for a proposition; a reading the books give only under a condition is never stated as a plain trait."""
    np = lexicon()["concepts"][p.concept]["np"]
    if p.modality == "potential" and not np.startswith("khả năng"):
        np = "khả năng " + np
    elif p.modality == "condition":
        np += " (khi điều kiện sách nêu kèm được thỏa)"
    return np


def short_of(p: Proposition) -> str:
    s = lexicon()["concepts"][p.concept].get("short") or lexicon()["concepts"][p.concept]["np"]
    return s + " (có điều kiện)" if p.modality in ("condition", "potential") else s


def _tt(ev) -> str:
    return ev.chart_trigger or ev.trigger_text


def _trig(p: Proposition, d: Discourse, ref: bool = True) -> str:
    return d.trig(_tt(p.roots[0].evidence[0]), ref)


def _prov(*ps) -> list[str]:
    out = []
    for p in ps:
        for r in (p.rules if isinstance(p, Proposition) else p):
            if r not in out:
                out.append(r)
    return out


def _add(para: Paragraph, d: Discourse, s: Sentence | None):
    if s is not None:
        para.sentences.append(s)
        d.end_sentence(s)


# ---------------------------------------------------------------- paragraph planning for one theme

def theme_paragraph(th: Theme, d: Discourse, first: bool, props: dict[str, Proposition], max_counters: int = 2) -> Paragraph:
    onto = lexicon()["ontology"]["facets"]
    d.start_paragraph()
    para = Paragraph("theme", facet=th.facet)
    lead, main = _lead_of(th), th.main
    multi = sum(r.weight for r in lead.roots) >= 2
    key = "lead_multi" if multi and first else ("lead_first" if first else "lead_next")
    text = d.pick(key, T[key], lead.id, th.facet).format(facet=th.name, np=np_of(lead))
    if lead.sensitive:
        text = T["sensitive"] + text[0].lower() + text[1:]
    _add(para, d, Sentence(cap(text), "claim", "sach", _prov(lead), [lead.id]))
    d.narrated.add(lead.id)
    _add(para, d, _ground(lead, d))
    told_counter = False
    if lead is not main:
        e = next(e for p, e in th.counters if p is lead)
        for s in _contrast(main, lead, e, d, props, swap=True):
            _add(para, d, s)
        d.narrated.add(main.id)
        told_counter = True
    sups = [(p, e) for p, e in th.supports if p.id not in d.narrated and p.id != lead.id]
    sups.sort(key=lambda x: (x[0].concept != main.concept, x[1] is None, -x[0].salience))
    seen_concepts = {lead.concept, main.concept}
    after: list[Proposition] = []
    n = 0
    for p, e in sups:
        if n >= 3:
            break
        if p.concept in seen_concepts and p.concept != main.concept:
            continue
        if p.concept == main.concept:
            s = d.pick("support_same", T["support_same"], p.id).format(Where=cap(pal_vi(p.palace)), where=pal_vi(p.palace), trig=_trig(p, d, False), books=books(p.books))
        elif e is not None and e.synth and e.type == "supports" and not d.pair_told(main, p):
            s = d.pick("support_synth", T["support_synth"], p.id).format(Np=cap(np_of(p)), trig=_trig(p, d), synth=e.synth)
            d.tell_pair(main, p)
        elif lead is not main:
            after.append(p)
            seen_concepts.add(p.concept)
            n += 1
            continue
        else:
            s = d.pick("support", T["support"], p.id).format(Np=cap(np_of(p)), np=np_of(p), trig=_trig(p, d))
        _add(para, d, Sentence(cap(s), "support", "sach", _prov(p), [p.id]))
        d.narrated.add(p.id)
        seen_concepts.add(p.concept)
        n += 1
    if after:
        items = " và ".join(f"{np_of(p)} ({d.trig(_tt(p.roots[0].evidence[0]), False)})" for p in after)
        s = d.pick("support_after_many", T["support_after_many"], main.id).format(short=short_of(main), items=items)
        _add(para, d, Sentence(cap(s), "support", "sach", _prov(*after), [p.id for p in after]))
        d.narrated |= {p.id for p in after}
    cnts = [(p, e) for p, e in th.counters if p is not lead and p is not main]
    cnts.sort(key=lambda x: (x[1] is None, {"contradicts": 0, "qualifies": 1}.get(x[1].type if x[1] else "", 2),
                             {"refinement": 0, "unresolved": 0, "school_divergence": 0}.get(x[1].resolution if x[1] else "", 1), x[0].palace != main.palace, -x[0].salience))
    k = 0
    for p, e in cnts:
        if k >= max_counters:
            break
        base = main if e is None or main.id in (e.a, e.b) else props.get(e.a if e.b == p.id else e.b, main)
        contra = e is not None and e.type == "contradicts"
        if d.pair_told(base, p, palaces=contra) or (e is None and p.id in d.narrated):
            continue
        for s in _contrast(base, p, e, d, props):
            _add(para, d, s)
        d.narrated.add(p.id)
        told_counter = told_counter or e is not None
        k += 1
    for s in _conditions(th.conditions, d, props):
        _add(para, d, s)
    refl = onto.get(th.facet, {}).get("reflection")
    if refl and told_counter:
        _add(para, d, Sentence(refl, "reflection", "he_thong", [], [lead.id]))
    return para


def _lead_of(th: Theme) -> Proposition:
    """Narrative order: when the main proposition is the 'tendency / excess' side of a frame (edge.b), lead with the capacity / strength side."""
    for p, e in th.counters:
        if e is not None and e.type == "qualifies" and e.b == th.main.id and e.a == p.id and p.facet == th.facet and p.kind != "rescue":
            return p
    return th.main


def _ground(p: Proposition, d: Discourse) -> Sentence:
    key = ("ground", frozenset(p.rules))
    if key in d.used:
        return Sentence(f"Căn cứ của {short_of(p)} cũng là những câu sách vừa nêu ({books(p.books)}).", "ground", "sach", _prov(p), [p.id])
    d.used.add(key)
    rs = sorted(p.roots, key=lambda r: (-r.weight, -len(r.books), r.atoms))
    tr = lambda r: d.trig(_tt(r.evidence[0]), False)
    if len(rs) >= 2:
        key = "ground_multi" if rs[1].weight >= 1 else "ground_overlap"
        s = d.pick(key, T[key], p.id).format(trig1=tr(rs[0]), books1=books(rs[0].books), trig2=tr(rs[1]), books2=books(rs[1].books))
    elif len(rs[0].books) >= 2:
        s = d.pick("ground_shared", T["ground_shared"], p.id).format(books=cap(books(rs[0].books)), trig=tr(rs[0]))
    else:
        s = d.pick("ground_one", T["ground_one"], p.id).format(trig=tr(rs[0]), books=books(rs[0].books))
    return Sentence(cap(s), "ground", "sach", _prov(p), [p.id])


def _contrast(a: Proposition, b: Proposition, e: Edge | None, d: Discourse, props, swap: bool = False) -> list[Sentence]:
    """Relate b to a. With swap=True, `b` was the paragraph lead and `a` is the theme's main proposition being introduced."""
    d.tell_pair(a, b)
    intro = a if swap else b
    if e is None:
        s = d.pick("contrast_open", T["contrast_open"], intro.id).format(np=np_of(intro), trig=_trig(intro, d))
        return [Sentence(cap(s), "contrast", "sach", _prov(intro), [intro.id])]
    other = props.get(e.b if e.a == a.id else e.a, b)
    out: list[Sentence] = []
    if e.type == "contradicts":
        det = e.detail
        if e.resolution == "refinement":
            gen, spec = props[det["general"]], props[det["specific"]]
            s = d.pick("refinement", T["refinement"], e.a, e.b).format(
                gbooks=cap(books(det["general_books"])), gnp=np_of(gen), gtrig=d.trig(det["general_trigger"], False),
                sbooks=books(det["specific_books"]), strig=d.trig(det["specific_trigger"], False), snp=np_of(spec))
            out.append(Sentence(cap(s), "interaction", "dieu_kien", det["general_rules"] + det["specific_rules"], [gen.id, spec.id]))
        elif e.resolution == "both_hold":
            x, y = (a, intro) if swap else (a, other)
            if x.palace == y.palace:
                s = d.pick("both_hold", T["both_hold"], e.a, e.b).format(btrig=_trig(y, d), bnp=np_of(y), bbooks=books(y.books))
            else:
                s = d.pick("both_hold_cross", T["both_hold_cross"], e.a, e.b).format(
                    Bnp=cap(np_of(y)), bnp=np_of(y), bpal=pal_vi(y.palace), btrig=_trig(y, d, False), bbooks=books(y.books), Apal=cap(pal_vi(x.palace)),
                    apal=pal_vi(x.palace), atopic=PALACE_TOPIC.get(x.palace, "chủ đề của nó"), btopic=PALACE_TOPIC.get(y.palace, "chủ đề của nó"))
            out.append(Sentence(cap(s), "interaction", "dieu_kien", _prov(x, y), [x.id, y.id]))
        else:
            s = d.pick(e.resolution, T[e.resolution], e.a, e.b).format(abooks=books(a.books), bbooks=books(other.books), trig=d.trig(det.get("a_trigger", ""), False))
            out.append(Sentence(cap(s), "interaction", "dieu_kien", _prov(a, other), [a.id, other.id]))
        return out
    if intro.id not in d.narrated:
        s = d.pick("contrast_open", T["contrast_open"], intro.id).format(np=np_of(intro), trig=_trig(intro, d))
        out.append(Sentence(cap(s), "contrast", "sach", _prov(intro), [intro.id]))
    if e.frame and e.synth:
        f = d.pick("frame:" + e.frame, T["frame"][e.frame], e.a, e.b).format(synth=e.synth)
        out.append(Sentence(cap(f), "interaction", "sach" if e.basis == "sach" else "he_thong", _prov(a, other), [a.id, other.id]))
        here = [x for x in e.attested if x.get("scope") == "lá số này"]
        lib = [x for x in e.attested if x.get("scope") != "lá số này"]
        if here:
            ev = next((v for p in (a, other) for v in p.evidence if v.rule_id == here[0]["rule"]), None)
            if ev is not None:
                out.append(Sentence(d.pick("attest_here", T["attest_here"], e.a, e.b).format(book=books(ev.schools), reading=ev.reading), "interaction", "sach", [ev.rule_id], [a.id, other.id]))
        elif lib and ("lib", lib[0]["rule"]) not in d.used:
            d.used.add(("lib", lib[0]["rule"]))
            out.append(Sentence(T["attest_lib"][0].format(book=_book_of_cites(lib[0]["cites"]), reading=_short_reading(lib[0]["reading"])), "interaction", "sach", [lib[0]["rule"]], [a.id, other.id]))
        elif ("frame_system_told",) not in d.used:
            d.used.add(("frame_system_told",))       # said once per chapter; later framed sentences carry the he_thong basis mark
            out.append(Sentence(d.pick("frame_system", T["frame_system"], e.a, e.b), "interaction", "he_thong", [], [a.id, other.id]))
    return out


def _conditions(edges: list[Edge], d: Discourse, props) -> list[Sentence]:
    """Mitigations and sequence conditions; several palaces stating the same condition concept are told once, with all their triggers."""
    out = []
    groups: dict[tuple, list[Edge]] = {}
    for e in edges:
        c = props.get(e.a)
        if c is None or c.id in d.narrated:
            continue
        groups.setdefault((e.type, c.concept), []).append(e)
    for (typ, concept), es in list(groups.items())[:2]:
        synth = es[0].synth
        cs = [props[e.a] for e in es]
        if typ == "mitigates":
            m = cs[0]
            s = d.pick("mitigates", T["mitigates"], m.id).format(book=books(m.books), reading=_short_reading(m.best.reading))
            out.append(Sentence(cap(s), "condition", "sach", _prov(m), [m.id] + [e.b for e in es]))
        elif typ == "conditions":
            cs = list({c.id: c for c in cs}.values())
            trig = "; ".join(dict.fromkeys(d.trig(_tt(c.roots[0].evidence[0]), False) for c in cs))
            s = d.pick("conditions", T["conditions"], cs[0].id).format(np=np_of(cs[0]), trig=trig, synth=synth)
            out.append(Sentence(cap(s), "condition", "he_thong", _prov(*cs), [c.id for c in cs]))
        for c in cs:
            d.narrated.add(c.id)
    return out


def _book_of_cites(cites) -> str:
    c = " ".join(cites)
    return "Khảo Luận" if "KL" in c else "Thực Hành" if "TH" in c else "Toàn Thư" if "TT" in c else "Nghiệm Lý (Thiên Lương)" if "TL" in c else "Nghiệm Lý 1974 (Thiên Lương)" if "NL" in c else "một sách trong bộ quy tắc"


def _short_reading(r: str) -> str:
    r = re.sub(r"^(khuynh hướng|hạn chế:)\s*", "", r)
    return re.sub(r";.*$", "", r).strip()


# ---------------------------------------------------------------- validation

def validate(paragraphs: list[Paragraph], props: dict[str, Proposition], edges: list[Edge]) -> dict:
    """Post-generation checks. Offending sentences are DROPPED (degrade to less text), never rewritten into something stronger."""
    issues = []
    seen_text: set[str] = set()
    for para in paragraphs:
        keep = []
        for s in para.sentences:
            if s.kind in CONTENT_KINDS and not s.provenance:
                issues.append({"type": "no_provenance", "text": s.text}); continue
            if any(re.search(b, s.text, re.I) for b in BANNED):
                issues.append({"type": "banned_wording", "text": s.text}); continue
            if s.text in seen_text and s.kind not in ("limit",):
                issues.append({"type": "duplicate", "text": s.text}); continue
            for pid in s.props:
                p = props.get(pid)
                if p and s.kind == "claim" and p.modality in ("potential", "condition") and not re.search(r"có thể|khả năng|khi|nếu|điều kiện", s.text):
                    issues.append({"type": "stronger_than_evidence", "text": s.text})
            seen_text.add(s.text)
            keep.append(s)
        para.sentences = keep
        if any(props[pid].sensitive for s in keep if s.kind == "claim" for pid in s.props if pid in props) and "truyền thống" not in para.text:
            issues.append({"type": "sensitive_unframed", "facet": para.facet})
    narrated = {pid for p in paragraphs for s in p.sentences for pid in s.props}
    for e in edges:
        if e.type == "contradicts" and e.resolution in ("unresolved", "school_divergence") and e.a in narrated and e.b in narrated:
            if not any(set(s.props) >= {e.a, e.b} and s.kind == "interaction" for p in paragraphs for s in p.sentences):
                issues.append({"type": "conflict_untold", "a": e.a, "b": e.b})
    sents = [s for p in paragraphs for s in p.sentences]
    openers = [_opener(s.text) for s in sents]
    repeats = sum(1 for i in range(1, len(openers)) if openers[i] == openers[i - 1])
    return {"issues": issues, "metrics": {"sentences": len(sents), "paragraphs": len(paragraphs), "distinct_openers": len(set(openers)),
                                          "consecutive_same_opener": repeats,
                                          "by_basis": {b: sum(1 for s in sents if s.basis == b) for b in ("sach", "dieu_kien", "he_thong", "tinh_toan")}}}
