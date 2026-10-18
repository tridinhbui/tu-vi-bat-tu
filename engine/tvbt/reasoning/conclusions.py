"""Conclusion layer: rule findings -> trigger atoms -> evidence clusters -> conclusions with explicit support, opposition,
conditions and open questions. Deterministic, no scoring, no language model.

Why this layer exists (docs/INTERPRETATION-ENGINE-AUDIT.md, RL/AR findings): the rule engine fires one finding per rule, and the UI
showed each as a separate "căn cứ". Seven rules that all read "Lộc Tồn ở Tài Bạch" then looked like seven reasons. Here a finding is
reduced to the chart facts that actually made its condition true (its *trigger atoms*), and findings of one palace whose triggers are
nested (one is a subset of the other) and that point the same way become ONE conclusion. Independent support is counted in distinct
books, never in rules.

Pipeline position:  chart facts -> rule engine (engine.run) -> **atoms -> clusters -> conflicts -> qualifiers** -> conclusions -> report.
Nothing here changes what a rule says or whether it fired; this layer only groups, relates and annotates.

Conflict handling (no averaging, no precedence invented):
  same_trigger      both directions read off the same chart facts: the books disagree; kept as unresolved alternatives.
  nested            the opposing rule adds conditions to the other's trigger: the narrower reading applies to this chart, the broader
                    one is its general case. This ordering is a SYSTEM CONVENTION (marked as such), pending expert review.
  coexisting        different chart facts, same palace and topic: both hold; written as "A, đồng thời B" without saying which wins.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ..knowledge import dsl
from ..synthesis import taxonomy as tx
from ..synthesis.semantics import claim_tone
from .positions import CAT_STARS as CAT, SAT_STARS as SAT

DATA = Path(__file__).resolve().parent.parent.parent / "data"

BOOK = {"SRC_KHAO_LUAN": "Tử Vi Khảo Luận", "SRC_THUC_HANH": "Tử Vi Thực Hành", "SRC_TOAN_THU": "Tử Vi Đẩu Số Toàn Thư",
        "SRC_TVDS_TAN_BIEN": "Tử Vi Đẩu Số Tân Biên (nháp)", "SRC_BAZI_ZHENZONG": "八字真宗 (Bát Tự Chân Tông)"}
BOOK_SHORT = {"KL": "Tử Vi Khảo Luận", "TH": "Tử Vi Thực Hành", "TT": "Tử Vi Đẩu Số Toàn Thư"}
_CITE = re.compile(r"\[((?:TH|KL|TT)\s*(?:pp?\.)?\s*[^\]]*?)\]")
_PAREN = re.compile(r"\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$")

# Star facts and the palaces (roles) they range over. Values are role names of positions.ROLES / dsl.ROLES.
_STAR_FACT_ROLES = {
    "palace.own_stars": ("self",), "palace.own_major_stars": ("self",),
    "palace.tam_phuong_stars": ("self", "trine1", "trine2", "opp"), "palace.tam_phuong_majors": ("self", "trine1", "trine2", "opp"),
    "palace.rel.tp_stars": ("self", "trine1", "trine2", "opp"), "palace.rel.tp_majors": ("self", "trine1", "trine2", "opp"),
    "palace.neighbor_stars": ("flank_prev", "flank_next"), "palace.neighbor_majors": ("flank_prev", "flank_next"),
    "palace.rel.flank_stars": ("flank_prev", "flank_next"),
    "palace.rel.trine_stars": ("trine1", "trine2"), "palace.rel.trine_majors": ("trine1", "trine2"),
}
for _r in ("self", "opp", "trine1", "trine2", "flank_prev", "flank_next", "nhi_hop"):
    _STAR_FACT_ROLES[f"palace.rel.{_r}_stars"] = (_r,)
    _STAR_FACT_ROLES[f"palace.rel.{_r}_majors"] = (_r,)
_HOA_FACT_ROLES = {"palace.tu_hoa": ("self",), "palace.tam_phuong_tu_hoa": ("self", "trine1", "trine2", "opp"),
                   "palace.rel.tp_hoa": ("self", "trine1", "trine2", "opp"), "palace.rel.trine_hoa": ("trine1", "trine2")}
for _r in ("self", "opp", "trine1", "trine2", "flank_prev", "flank_next", "nhi_hop"):
    _HOA_FACT_ROLES[f"palace.rel.{_r}_hoa"] = (_r,)

GENERIC_FACTS = {"chart.year_branch", "chart.year_stem", "chart.can_chi_relation", "chart.year_polarity", "chart.gender", "chart.am_duong_ly"}
_REL_VI = {"can_sinh_chi": "can sinh chi", "chi_sinh_can": "chi sinh can", "can_khac_chi": "can khắc chi", "chi_khac_can": "chi khắc can", "hoa": "can chi hòa"}
CHART_FACT_VI = {
    "chart.year_branch": lambda v: f"năm sinh {v}",
    "chart.year_stem": lambda v: f"can năm {v}",
    "chart.year_polarity": lambda v: f"năm sinh {v}",
    "chart.gender": lambda v: f"giới {v}",
    "chart.am_duong_ly": lambda v: "âm dương thuận lý" if v == "thuan_ly" else "âm dương nghịch lý",
    "chart.can_chi_relation": lambda v: f"năm sinh {_REL_VI.get(v, v)}",
    "chart.menh_dac_chinh": lambda v: "Mệnh đóng cung cùng âm dương với tuổi (đắc chính)" if v else "Mệnh đóng cung khác âm dương với tuổi",
    "chart.season_relation": lambda v: {"vuong": "hành Mệnh vượng theo mùa sinh", "tuong": "hành Mệnh được mùa sinh tương trợ (Tướng)"}.get(v, f"mùa sinh: {v}"),
    "chart.hour_menh_polarity": lambda v: "giờ sinh cùng âm dương với cung Mệnh" if v == "thuan_ly" else "giờ sinh khác âm dương với cung Mệnh",
    "chart.hour_matches_season": lambda v: "giờ sinh hợp mùa" if v else "giờ sinh không hợp mùa",
    "chart.menh_stage_th": lambda v: f"Mệnh ở {v} địa theo hành Mệnh",
    "chart.menh_cuc_relation": lambda v: f"quan hệ Cục – Mệnh: {v}",
    "chart.tu_vi_branch": lambda v: f"Tử Vi ở {v}",
    "chart.menh_element": lambda v: f"hành Mệnh {v}",
    "chart.birth_season": lambda v: f"sinh mùa {v}",
}
DERIVED_VI = {"derived.group.tu_phu_vu_tuong": "nhóm Tử – Phủ – Vũ – Tướng trong tam phương Mệnh",
              "derived.group.sat_pha_liem_tham": "nhóm Sát – Phá – Liêm – Tham trong tam phương Mệnh",
              "derived.group.co_nguyet_dong_luong": "nhóm Cơ – Nguyệt – Đồng – Lương trong tam phương Mệnh"}

ROLE_VI = {"self": "đồng cung", "opp": "xung chiếu", "trine1": "hội chiếu (tam hợp)", "trine2": "hội chiếu (tam hợp)",
           "flank_prev": "giáp", "flank_next": "giáp", "nhi_hop": "nhị hợp"}


@dataclass(frozen=True)
class Atom:
    """One chart fact a rule's condition actually used. kind: star | hoa | dignity | tuan_triet | vcd | than | chart | count."""
    kind: str
    name: str
    palace: str | None = None
    value: Any = None

    @property
    def key(self) -> tuple:
        """Identity used to decide whether two triggers are the same chart fact (dignity folds into its star)."""
        if self.kind == "dignity":
            return ("star", self.name, self.palace)
        return (self.kind, self.name, self.palace)

    @property
    def generic(self) -> bool:
        """Facts fixed by the birth year and sex alone: every chart of that year and sex has them (no star of THIS chart involved)."""
        return self.kind == "chart" and self.name in GENERIC_FACTS

    def vi(self) -> str:
        if self.kind == "star":
            return f"{self.name} ở {self.palace}" if self.palace else self.name
        if self.kind == "hoa":
            return f"{self.name} ở {self.palace}" if self.palace else self.name
        if self.kind == "dignity":
            return f"{self.name} ({self.value}) ở {self.palace}"
        if self.kind == "tuan_triet":
            return f"{self.name} đóng ở {self.palace}"
        if self.kind == "branch":
            return f"{self.palace} ở {self.value}"
        if self.kind == "vcd":
            return f"{self.palace} vô chính diệu"
        if self.kind == "than":
            return f"Thân cư {self.palace}"
        if self.kind == "chart":
            f = CHART_FACT_VI.get(self.name)
            return f(self.value) if f else f"{self.name.split('.', 1)[1]} = {self.value}"
        if self.kind == "derived":
            return DERIVED_VI.get(self.name, self.name.split(".", 1)[1].replace("_", " "))
        if self.kind == "count":
            if self.name.startswith("palace.khi.") and self.value == 0:
                grp = "sát tinh" if ".sat_" in self.name else "cát tinh"
                where = {"self": "trong cung", "tp": "trong tam phương tứ chính", "flank": "ở hai cung giáp"}[self.name.rsplit("_", 1)[1]]
                return f"không có {grp} (nhóm sáu sao) {where}"
            return f"{self.name} = {self.value}"
        return f"{self.name} = {self.value}"


def _palace_of_star(star: str, roles, facts: dict) -> list[str]:
    names = facts.get("palace.rel_names") or {}
    out = []
    for r in roles:
        if star in (facts.get(f"palace.rel.{r}_stars") or []):
            n = names.get(r)
            if n and n not in out:
                out.append(n)
    return out


def _palace_of_hoa(hoa: str, roles, facts: dict) -> list[str]:
    names = facts.get("palace.rel_names") or {}
    return [names[r] for r in roles if hoa in (facts.get(f"palace.rel.{r}_hoa") or []) and names.get(r)]


def _leaf_atoms(fact: str, op: str, value: Any, facts: dict, here: str | None) -> list[Atom]:
    if fact == "palace.name":
        return []
    vals = value if isinstance(value, list) else [value]
    got = facts.get(fact)
    if fact in _STAR_FACT_ROLES and op in ("contains", "contains_any", "contains_all"):
        present = [v for v in vals if isinstance(got, list) and v in got]
        return [Atom("star", s, p) for s in present for p in (_palace_of_star(s, _STAR_FACT_ROLES[fact], facts) or [None])]
    if fact in _HOA_FACT_ROLES and op in ("contains", "contains_any", "contains_all"):
        present = [v for v in vals if isinstance(got, list) and v in got]
        return [Atom("hoa", h, p) for h in present for p in (_palace_of_hoa(h, _HOA_FACT_ROLES[fact], facts) or [None])]
    if fact.startswith("palace.dignity.") or fact.startswith("palace.dignity_rank."):
        star = fact.split(".", 2)[2]
        lv = facts.get(f"palace.dignity.{star}") or got
        return [Atom("dignity", star, here, lv)]
    if fact.startswith("palace.tp_rank."):
        star = fact.split(".", 2)[2]
        pal = (_palace_of_star(star, ("self", "trine1", "trine2", "opp"), facts) or [here])[0]
        return [Atom("dignity", star, pal, got)]
    if fact in ("palace.tuan", "palace.triet") and got:
        return [Atom("tuan_triet", "Tuần" if fact.endswith("tuan") else "Triệt", here)]
    if fact in ("palace.rel.opp_tuan", "palace.rel.opp_triet") and got:
        opp = (facts.get("palace.rel_names") or {}).get("opp")
        return [Atom("tuan_triet", "Tuần" if fact.endswith("tuan") else "Triệt", opp)]
    if fact == "palace.branch":
        return [Atom("branch", "vị trí", here, got)]
    if fact == "palace.has_no_major" and got:
        return [Atom("vcd", "vô chính diệu", here)]
    if fact == "palace.is_than" and got:
        return [Atom("than", "Thân", here)]
    if fact.startswith("chart.") or fact.startswith("bazi."):
        return [Atom("chart", fact, None, tuple(got) if isinstance(got, list) else got)]
    if fact.startswith("derived."):
        return [Atom("derived", fact, here, got)]
    if fact.startswith("palace.khi.") and isinstance(got, int):
        grp = SAT if ".sat_" in fact else CAT
        roles = {"self": ("self",), "tp": ("self", "trine1", "trine2", "opp"), "flank": ("flank_prev", "flank_next")}[fact.rsplit("_", 1)[1]]
        found = [Atom("star", st, p) for st in grp for p in _palace_of_star(st, roles, facts)]
        return found or [Atom("count", fact, here, got)]
    return [Atom("count", fact, here, got)]


def trigger_atoms(expr: dict, facts: dict, world=None, here: str | None = None) -> list[Atom]:
    """Atoms of the sub-conditions that are TRUE and made `expr` true. `not` leaves contribute nothing (an absence is a condition,
    not a fact of the chart). For `any`, only the satisfied branches count."""
    if dsl.evaluate(expr, facts, world) is not True:
        return []
    if "all" in expr:
        return [a for e in expr["all"] for a in trigger_atoms(e, facts, world, here)]
    if "any" in expr:
        return [a for e in expr["any"] if dsl.evaluate(e, facts, world) is True for a in trigger_atoms(e, facts, world, here)]
    if "count" in expr:
        return [a for e in expr["count"] if dsl.evaluate(e, facts, world) is True for a in trigger_atoms(e, facts, world, here)]
    if "not" in expr:
        return []
    if "ref" in expr:
        name = dsl.resolve_palace(expr["ref"]["palace"], facts)
        other = world(name) if (world and name) else None
        if not other:
            return []
        return _leaf_atoms(expr["ref"]["fact"], expr.get("operator", "eq"), expr.get("value"), other, name)
    return _leaf_atoms(expr["fact"], expr.get("operator", "eq"), expr.get("value"), facts, here)


def absence_conditions(expr: dict) -> list[str]:
    """Human-readable 'không có X' clauses a rule tests (they matter for the reader: the reading depends on an absence)."""
    out = []
    if "not" in expr:
        inner = expr["not"]
        if "fact" in inner and isinstance(inner.get("value"), (str, list)):
            v = inner["value"]
            out.append("không có " + (", ".join(v) if isinstance(v, list) else v))
    elif "fact" in expr and expr.get("operator") in ("not_contains",):
        out.append(f"không có {expr['value']}")
    elif "fact" in expr and expr["fact"].startswith("palace.khi.sat") and expr.get("operator") == "lte" and expr.get("value") == 0:
        out.append("không gặp sát tinh")
    else:
        key = "count" if "count" in expr else next(iter(expr), None)
        if key in ("all", "any", "count"):
            for e in expr[key]:
                out += absence_conditions(e)
    return out


# ---------------------------------------------------------------------------------------------------------------------------------
@dataclass
class Reading:
    rule_id: str
    claim: str
    text: str                 # the reading, without the trigger parenthesis
    trigger_text: str         # the book's own trigger wording (parenthesis of the claim label)
    effect: str               # support | limit | neutral
    basis: str                # verified | draft
    books: list[str]
    cites: list[str]          # "KL p.216"
    atoms: list[Atom]
    absences: list[str]
    tone: str | None = None   # '+', '-', '~' or None, read off the reading's words (synthesis.semantics.claim_tone)


@dataclass
class Conclusion:
    conclusion_id: str
    topic: str
    palace: str | None
    aspect: str
    polarity: str                          # support | limit | neutral
    contributing_facts: list[str]
    supporting_rules: list[dict]
    opposing_rules: list[dict] = field(default_factory=list)
    applicability_conditions: list[str] = field(default_factory=list)
    invalidating_conditions: list[dict] = field(default_factory=list)
    source_references: list[str] = field(default_factory=list)
    school: list[str] = field(default_factory=list)
    evidence_status: str = "verified"     # verified | draft | mixed
    independent_sources: int = 0
    rule_count: int = 0
    generic: bool = False                  # rests only on chart-wide facts (birth year etc.)
    shared_basis_with: list[str] = field(default_factory=list)
    conflicts: list[dict] = field(default_factory=list)
    unresolved_questions: list[str] = field(default_factory=list)
    final_interpretation: str = ""
    period: str = "natal"


def split_label(label: str) -> tuple[str, str]:
    """'khuynh hướng X (trigger)' -> ('X', 'trigger')."""
    m = _PAREN.search(label or "")
    body, trig = (label[: m.start()], m.group(1)) if m else (label or "", "")
    body = re.sub(r"^khuynh hướng\s+", "", body.strip())
    body = re.sub(r"^hạn chế:\s*", "", body)
    return body.strip(), trig.strip()


def _cites(desc: str) -> list[str]:
    out = []
    for c in _CITE.findall(desc or ""):
        c = re.sub(r"\s+", " ", c.strip())
        if c not in out:
            out.append(c)
    return out


def cite_vi(c: str) -> str:
    """'KL p.216' -> 'Tử Vi Khảo Luận, tr.216'."""
    m = re.match(r"(KL|TH|TT)\s*(pp?\.)?\s*(.*)", c)
    if not m:
        return c
    return f"{BOOK_SHORT[m.group(1)]}, tr.{m.group(3).strip()}"


def readings_from(res, rules, claims: dict, base: dict) -> list[tuple[str, Reading]]:
    """(subject, Reading) for every finding, with its trigger atoms computed against the same facts the engine used."""
    rmap = {r.id: r for r in rules}

    def facts_of(subject):
        d = dict(base.get("chart", {}))
        d.update(base.get(subject, {}))
        d.update(res.derived.get(subject, {}))
        if subject != "chart":
            d.update(res.derived.get("chart", {}))
        return d

    def world(name):
        s = f"palace:{name}"
        return facts_of(s) if s in base else None

    out = []
    seen = set()
    for f in res.findings:
        r = rmap.get(f.rule_id)
        if r is None or (f.subject, r.id) in seen:
            continue
        seen.add((f.subject, r.id))
        here = f.subject.split(":", 1)[1] if f.subject.startswith("palace:") else None
        fx = facts_of(f.subject)
        atoms = list(dict.fromkeys(trigger_atoms(r.conditions, fx, world, here)))
        label = (claims.get(f.claim) or {}).get("label", f.claim) if isinstance(claims.get(f.claim), dict) else claims.get(f.claim, f.claim)
        text, trig = split_label(label)
        out.append((f.subject, Reading(r.id, f.claim, text, trig, f.effect, f.basis, sorted({BOOK.get(s, s) for s in r.sourceIds}),
                                       _cites(r.description), atoms, absence_conditions(r.conditions),
                                       "-" if f.effect == "limit" else claim_tone(label))))
    return out


def _sig(rd: Reading) -> frozenset:
    return frozenset(a.key for a in rd.atoms if not a.generic and a.kind != "count")


class _UF:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, i):
        while self.p[i] != i:
            self.p[i] = self.p[self.p[i]]
            i = self.p[i]
        return i

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


def _dedupe(atoms) -> list[Atom]:
    """One atom per chart fact; a star's dignity atom replaces its plain star atom."""
    out: dict[tuple, Atom] = {}
    for a in atoms:
        k = a.key if a.kind in ("star", "dignity") else (a.kind, a.name, a.palace, str(a.value))
        if k not in out or (a.kind == "dignity" and out[k].kind == "star"):
            out[k] = a
    return list(out.values())


def _polarity(rd: Reading) -> str:
    """Direction of a reading for the reader: a rule whose effect is 'limit' always limits; otherwise the words decide ('+' favourable,
    '-' unfavourable). Mixed or unclassified wording stays neutral and is never set against another reading."""
    if rd.effect == "limit" or rd.tone == "-":
        return "limit"
    return "support" if rd.tone == "+" else "neutral"


def cluster(items: list[tuple[str, Reading]]) -> list[tuple[str, str, list[Reading]]]:
    """Group readings of one subject and one polarity whose trigger signatures are nested (A ⊆ B). Readings resting only on
    chart-wide facts stay alone. Classification labels (menh_nhom_*, cach_*) are kept apart from readings."""
    groups: dict[tuple[str, str, bool], list[Reading]] = {}
    for subj, rd in items:
        lab = rd.claim.startswith(tx.LABEL_PREFIX)
        groups.setdefault((subj, _polarity(rd), lab), []).append(rd)
    out = []
    for (subj, pol, lab), rds in sorted(groups.items(), key=lambda kv: (kv[0][0] != "palace:Mệnh", kv[0])):
        uf = _UF(len(rds))
        sigs = [_sig(r) for r in rds]
        for i in range(len(rds)):
            for j in range(i + 1, len(rds)):
                a, b = sigs[i], sigs[j]
                if a and b and (a <= b or b <= a):
                    uf.union(i, j)
        buckets: dict[int, list[Reading]] = {}
        for i, r in enumerate(rds):
            buckets.setdefault(uf.find(i), []).append(r)
        for _, b in sorted(buckets.items()):
            out.append((subj, "label" if lab else pol, b))
    return out


# ---------------------------------------------------------------------------------------------------------------------------------
def load_qualifiers() -> list[dict]:
    p = DATA / "qualifiers.json"
    return json.loads(p.read_text("utf-8"))["qualifiers"] if p.exists() else []


def _qualifier_applies(q: dict, palace: str | None, atoms: list[Atom], aspect: str, polarity: str) -> bool:
    t = q["target"]
    if t.get("palace") and t["palace"] != palace:
        return False
    if t.get("palace_in") and palace not in t["palace_in"]:
        return False
    if t.get("aspect") and t["aspect"] != aspect:
        return False
    if t.get("polarity") and t["polarity"] != polarity:
        return False
    if t.get("skip_if_atom") and any(a.kind == t["skip_if_atom"] for a in atoms):
        return False
    if t.get("any_reading"):
        return palace is not None
    stars = {a.name for a in atoms if a.kind in ("star", "dignity") and a.palace == palace}
    need, anyof = t.get("stars_all", []), t.get("stars_any", [])
    if not need and not anyof:
        return palace is not None
    return all(s in stars for s in need) and (not anyof or any(s in stars for s in anyof))


def evaluate_qualifiers(palace: str | None, atoms: list[Atom], facts_world, qualifiers: list[dict], aspect: str = "",
                        polarity: str = "") -> list[dict]:
    """Qualifiers are source-cited conditions under which a reading is weakened, voided or made durable (data/qualifiers.json).
    Only trigger stars standing IN the conclusion's palace select a qualifier (a star seen by chiếu is the other palace's business).
    status: 'met' (the condition is on this chart), 'not_met', 'unknown' (a fact the condition needs is missing)."""
    out = []
    if palace is None:
        return out
    fx = facts_world(f"palace:{palace}")
    if fx is None:
        return out
    wv = lambda n: facts_world(f"palace:{n}")
    for q in qualifiers:
        if not _qualifier_applies(q, palace, atoms, aspect, polarity):
            continue
        v = dsl.evaluate(q["when"], fx, wv)
        status = "met" if v is True else "not_met" if v is False else "unknown"
        hit = list(dict.fromkeys(a.vi() for a in trigger_atoms(q["when"], fx, wv, palace))) if v is True else []
        out.append({"id": q["id"], "effect": q["effect"], "status": status, "text": q["text_vi"], "scope": q.get("scope_vi", ""),
                    "on_chart": hit, "source": q["source"], "review": q.get("review", "verified"),
                    "question": q.get("open_question_vi") if status != "not_met" else None})
    return out


RESOLUTION = {
    "same_trigger": ("unresolved", "Cùng một dữ kiện nhưng sách cho hai chiều về cùng một chuyện; giữ cả hai, chưa có căn cứ để chọn."),
    "complementary": ("both_hold", "Cùng một dữ kiện, sách nêu hai mặt khác nhau; không mâu thuẫn."),
    "nested": ("both_hold",
               "Một câu đòi thêm điều kiện so với câu kia và cả hai điều kiện đều khớp lá số. Việc coi câu hẹp hơn là đúng hơn chỉ là quy ước "
               "đề xuất của hệ thống (chưa được chuyên gia duyệt), nên không được áp dụng: cả hai được nêu."),
    "coexisting": ("both_hold", "Hai dữ kiện khác nhau cùng có mặt; cả hai cùng đúng, sách không nói bên nào át bên nào."),
}


def _csig(rd: Reading) -> frozenset:
    """Signature for relating two readings: like _sig but counting conditions (e.g. 'gặp sát tinh') are kept, so a rule that adds a
    sát condition is not mistaken for the broader one."""
    return frozenset(a.key if a.kind in ("star", "dignity") else (a.kind, a.name, a.palace) for a in rd.atoms if not a.generic)


def _conflict_kind(a: list[Reading], b: list[Reading]) -> str:
    sa = frozenset().union(*[_csig(r) for r in a]) if a else frozenset()
    sb = frozenset().union(*[_csig(r) for r in b]) if b else frozenset()
    if sa and sa == sb:
        return "same_trigger"
    if sa and sb and (sa < sb or sb < sa):
        return "nested"
    return "coexisting"


def _topic(palace: str | None, aspect: str) -> str:
    asp = {"tai": "tài lộc", "danh": "công danh, địa vị", "tri": "trí tuệ, học vấn", "hon_nhan": "hôn nhân", "tinh": "tính cách",
           "suc_khoe": "sức khỏe (biểu tượng)", "tuoi_tho": "thọ (biểu tượng)", "tong_hop": "tổng quát", "nhan_dien": "nhận diện cấu trúc"}
    return f"{palace or 'Toàn lá số'} · {asp.get(aspect, aspect)}"


def _aspect(rds: list[Reading], palace: str | None) -> str:
    asp = [tx.aspect_of(r.claim, palace) for r in rds]
    return max(set(asp), key=lambda x: (asp.count(x), x)) if asp else "tong_hop"


def build(res, rules, claims: dict, base: dict, qualifiers: list[dict] | None = None, verified_only: bool = False) -> list[Conclusion]:
    """Turn an InferenceResult into conclusions. `base` = the fact dict given to engine.run (facts.tuvi_facts output)."""
    qualifiers = load_qualifiers() if qualifiers is None else qualifiers
    items = readings_from(res, rules, claims, base)
    if verified_only:
        items = [(s, r) for s, r in items if r.basis == "verified"]

    def world(subject):
        if subject not in base:
            return None
        d = dict(base.get("chart", {}))
        d.update(base[subject])
        d.update(res.derived.get(subject, {}))
        return d

    out: list[Conclusion] = []
    clusters = cluster(items)
    for n, (subj, pol, rds) in enumerate(clusters):
        palace = subj.split(":", 1)[1] if subj.startswith("palace:") else None
        atoms = _dedupe(a for r in rds for a in r.atoms)
        books = sorted({b for r in rds for b in r.books})
        basis = {r.basis for r in rds}
        aspect = "nhan_dien" if pol == "label" else _aspect(rds, palace)
        c = Conclusion(
            conclusion_id=f"C{n + 1:03d}",
            topic=_topic(palace, aspect), palace=palace, aspect=aspect, polarity="neutral" if pol == "label" else pol,
            contributing_facts=[a.vi() for a in atoms if not a.generic and a.kind != "count"] or [a.vi() for a in atoms],
            supporting_rules=[{"rule_id": r.rule_id, "reading": r.text, "book_trigger": r.trigger_text, "basis": r.basis,
                               "books": r.books, "cites": [cite_vi(x) for x in r.cites]} for r in rds],
            applicability_conditions=sorted({r.trigger_text for r in rds if r.trigger_text} | {x for r in rds for x in r.absences}),
            source_references=sorted({cite_vi(x) for r in rds for x in r.cites}),
            school=books,
            evidence_status="verified" if basis == {"verified"} else ("draft" if basis == {"draft"} else "mixed"),
            independent_sources=len(books), rule_count=len(rds),
            generic=all(a.generic or a.kind == "count" for a in atoms) if atoms else True,
        )
        c.invalidating_conditions = evaluate_qualifiers(palace, atoms, world, qualifiers, aspect, c.polarity)
        out.append(c)
        c._readings = rds  # type: ignore[attr-defined]  (kept for conflict analysis; not serialised)

    # shared basis across subjects (e.g. Mệnh's "Vũ Khúc được Lộc Mã" and Tài Bạch's "Lộc Tồn, Thiên Mã"): one fact, not two reasons
    keys = {c.conclusion_id: frozenset(k for r in c._readings for k in _sig(r)) for c in out}  # type: ignore[attr-defined]
    for c in out:
        for d in out:
            if c is not d and keys[c.conclusion_id] & keys[d.conclusion_id] and c.palace != d.palace:
                c.shared_basis_with.append(d.conclusion_id)

    # relations between a supporting and a limiting conclusion of the same palace. Pairs are formed only when they share a trigger fact
    # or speak to the same specific topic; readings resting on birth-year facts alone are never paired (they say nothing about this chart).
    for c in out:
        if c.polarity != "support" or c.generic:
            continue
        for d in out:
            if d.polarity != "limit" or d.palace != c.palace or d.generic:
                continue
            shared = keys[c.conclusion_id] & keys[d.conclusion_id]
            same_topic = d.aspect == c.aspect and c.aspect not in ("tong_hop", "nhan_dien")
            if not shared and not same_topic:
                continue
            kind = _conflict_kind(c._readings, d._readings)  # type: ignore[attr-defined]
            if kind == "same_trigger" and not same_topic:
                kind = "complementary"
            rel = {"with": d.conclusion_id, "kind": kind,
                   "shared_facts": sorted({a.vi() for r in c._readings for a in r.atoms if a.key in shared})}  # type: ignore[attr-defined]
            rel["resolution"], rel["note"] = RESOLUTION[kind]
            if kind == "nested":
                sc = frozenset().union(*[_csig(r) for r in c._readings])  # type: ignore[attr-defined]
                sd = frozenset().union(*[_csig(r) for r in d._readings])  # type: ignore[attr-defined]
                narrow, wide, extra_keys = (d, c, sd - sc) if sc < sd else (c, d, sc - sd)
                allat = {(a.key if a.kind in ("star", "dignity") else (a.kind, a.name, a.palace)): a
                         for x in (c, d) for r in x._readings for a in r.atoms}  # type: ignore[attr-defined]
                rel["narrower"] = narrow.conclusion_id
                rel["extra_facts"] = sorted(allat[k].vi() for k in extra_keys if k in allat)
            c.conflicts.append(rel)
            c.opposing_rules += [{"rule_id": r.rule_id, "reading": r.text, "book_trigger": r.trigger_text, "basis": r.basis,
                                  "cites": [cite_vi(x) for x in r.cites], "conclusion": d.conclusion_id} for r in d._readings]  # type: ignore[attr-defined]
            d.conflicts.append({**rel, "with": c.conclusion_id})

    for c in out:
        c.unresolved_questions = _questions(c, base)
        c.final_interpretation = _final(c, {x.conclusion_id: x for x in out})
    for c in out:
        del c._readings  # type: ignore[attr-defined]
    return out


def _questions(c: Conclusion, base: dict) -> list[str]:
    qs = []
    for q in c.invalidating_conditions:
        if q.get("question"):
            qs.append(q["question"])
    if c.evidence_status != "verified":
        qs.append("Có quy tắc chưa đối chiếu sách (nháp) trong căn cứ.")
    fx = base.get(f"palace:{c.palace}", {}) if c.palace else {}
    for s in fx.get("palace.own_major_stars", []):
        if fx.get(f"palace.dignity.{s}") == "unspecified" and any(s in f for f in c.contributing_facts):
            qs.append(f"Bảng độ sáng đang dùng không ghi vị trí của {s} ở {fx.get('palace.branch')}; mức sáng của sao này chưa xác định.")
    return list(dict.fromkeys(qs))


def _join(xs: list[str]) -> str:
    xs = [x for x in xs if x]
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " và " + xs[-1] if xs else ""


def _final(c: Conclusion, by_id: dict) -> str:
    readings = list(dict.fromkeys(r["reading"] for r in c.supporting_rules))
    facts_txt = _join(c.contributing_facts[:4])
    if c.aspect == "nhan_dien":
        s = f"{_join(readings)[:1].upper()}{_join(readings)[1:]} (dựa trên {facts_txt})."
    else:
        head = "Sách lưu ý" if c.polarity == "limit" else "Sách ghi"
        s = f"{head}: {_join(readings)}. Căn cứ trên lá số: {facts_txt}."
    if c.rule_count > 1:
        s += f" {c.rule_count} câu từ {c.independent_sources} sách cùng dựa trên dữ kiện này, nên đây là một căn cứ, không phải {c.rule_count}."
    met = [q for q in c.invalidating_conditions if q["status"] == "met"]
    unmet = [q for q in c.invalidating_conditions if q["status"] == "not_met"]
    for q in met:
        lead = {"strengthens": "Điều kiện tăng thêm có mặt", "requires_for_durability": "Điều kiện để bền có mặt",
                "modifies": "Yếu tố làm thay đổi tính chất sao có mặt"}.get(q["effect"], "Điều kiện giới hạn có mặt")
        s += f" {lead}: {q['text']} ({q['source']})."
    for q in unmet:
        if q["effect"] in ("requires_for_durability", "requires"):
            s += f" Điều kiện sách đòi hỏi chưa có trên lá số: {q['text']} ({q['source']})."
    for k in c.conflicts:
        other = by_id.get(k["with"])
        if other is None:
            continue
        o_read = _join(list(dict.fromkeys(r["reading"] for r in other.supporting_rules))[:2])
        if k["kind"] == "complementary":
            s += f" Cùng dữ kiện ấy, sách còn nêu một mặt khác: {o_read}."
        elif k["kind"] == "coexisting":
            s += f" Đồng thời sách ghi {o_read}; hai điều cùng đúng, đọc như một tiềm năng có giới hạn chứ không cộng trừ."
        elif k["kind"] == "same_trigger":
            s += f" Cùng dữ kiện ấy, sách cũng ghi {o_read}; hai cách đọc được giữ song song."
        else:
            extra = _join(k.get("extra_facts", [])[:3])
            if k.get("narrower") == other.conclusion_id:
                s += f" Khi có thêm {extra or 'điều kiện khác'} (lá số này có), sách ghi {o_read}; hai câu được nêu cùng nhau."
            else:
                s += f" Câu này đòi thêm {extra or 'điều kiện'} so với câu {o_read}; cả hai đều khớp lá số và được nêu cùng nhau."
    return s


def to_dict(cs: list[Conclusion]) -> list[dict]:
    return [asdict(c) for c in cs]
