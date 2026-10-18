"""Semantic Intermediate Representation (Semantic IR) between the rule engine and the narrative generator.

A fired finding is turned into one SemanticEvidence per CONCEPT its reading mentions. The narrative layer never reads the old claim strings to
guess meaning: it reads concept ids, facets, polarity, modality and the formal trigger of the rule. The book paraphrase is kept verbatim on the
evidence (`reading`, `segment`) so every sentence can be traced back.

Annotation is deterministic and data-driven (data/semantic/*.json):
  * the reading text is the rule's OWN paraphrase when its description carries one (claims are shared across rules, and a shared label can carry
    a condition the rule does not check), else the claim label;
  * concepts are found by greedy longest-first cue matching over the whole reading; a negator right before a cue flips it to the concept's `opp`;
  * a ' nhưng / mà / song ' inside ONE book sentence splits it into two groups — the book itself pairs those concepts (book_pairing);
  * effect='limit' always LIMITS the concept, whatever the label words say;
  * applicability guards (data/semantic/applicability.json) re-check or exclude rules whose pack condition is wider than the book sentence.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent.parent / "data" / "semantic"
SCHOOL = {"SRC_THUC_HANH": "Thực Hành", "SRC_KHAO_LUAN": "Khảo Luận", "SRC_TOAN_THU": "Toàn Thư", "SRC_TVDS_TAN_BIEN": "Tân Biên"}
_CITE = re.compile(r"\[((?:TH|KL|TT)[^\]]*?)\]")
_PARA = re.compile(r"paraphrased\)?[^:]{0,80}?:\s*(.+)$")
_CONTRAST = (" nhưng ", " mà ", " song ", " tuy ")
_CLAUSE = re.compile(r"[,;]| và | nhưng | mà | song | tuy ")
LABEL_PREFIX = ("menh_nhom_", "cach_", "cau_truc_")
RELATION_PALACES = ("Phu Thê", "Tử Tức", "Huynh Đệ", "Phụ Mẫu", "Nô Bộc")


@lru_cache(maxsize=1)
def lexicon() -> dict:
    load = lambda n: json.loads((DATA / n).read_text("utf-8"))
    onto, con, rel, app = load("ontology.json"), load("concepts.json"), load("relations.json"), load("applicability.json")
    concepts = {c["id"]: c for c in con["concepts"]}
    cues = sorted(((cue, c["id"]) for c in con["concepts"] for cue in c["cues"]), key=lambda x: (-len(x[0]), x[0]))
    return {"ontology": onto, "concepts": concepts, "cues": cues, "negators": con["negators"], "valence": con["valence_cues"],
            "relations": rel["relations"], "frames": rel["frames"], "guards": {g["rule"]: g for g in app["guards"]}, "auto": app["auto"]}


@dataclass
class SemanticEvidence:
    id: str
    rule_id: str
    finding_id: str
    subject: str
    palace: str | None
    claim: str
    reading: str                 # the rule's own paraphrase (book wording, never generated)
    segment: str                 # the clause of `reading` that carries this concept
    concept: str
    facet: str
    domain: str
    kind: str                    # capacity | trait | manifestation | outcome | timing | rescue | style
    polarity: str                # + | - | ~   (relative to the reader: supportive / limiting / neutral)
    modality: str                # tendency | potential | condition | limitation | rescue
    role: str                    # asserts | limits | mitigates
    trigger_text: str            # the condition as the book states it
    leaves: tuple                # formal condition leaves (fact, op, value-repr), palace.name removed
    root: tuple                  # normalised chart facts the rule stands on (independence key)
    stars: tuple
    basis: str                   # verified | draft (copied from the engine, never upgraded)
    schools: tuple
    cites: tuple
    applicability: str = "ok"    # ok | rechecked | relabelled
    applicability_note: str = ""
    paired_with: tuple = ()      # concepts the SAME book sentence sets against this one (' nhưng ')
    mapping: str = "cue"         # cue | palace_fallback
    chart_trigger: str = ""      # the condition leaves that are TRUE on this chart, in Vietnamese (falls back to trigger_text)
    facts_used: tuple = ()       # (fact, value) pairs read from the chart for those true leaves
    present_stars: tuple = ()    # stars/hóa named by those true leaves (what is actually on the chart)

    @property
    def sensitive(self) -> bool:
        return bool(lexicon()["ontology"]["facets"].get(self.facet, {}).get("sensitive"))


@dataclass
class Annotation:
    evidence: list[SemanticEvidence] = field(default_factory=list)
    unmapped: list[dict] = field(default_factory=list)      # fired findings no concept covers (stay in the evidence layer only)
    excluded: list[dict] = field(default_factory=list)      # applicability guards that removed a finding
    drafts: list[dict] = field(default_factory=list)        # draft findings kept out of synthesis


# ---------------------------------------------------------------- reading text

def _strip_cites(s: str) -> str:
    return _CITE.sub("", s).strip().rstrip(".").strip()


EDITORIAL = ("'", "‘", "“", "sách ", "đây là", "câu ", "độ sáng", "cùng nhận định", "chưa ", "đọc là", "nhưng sách", "bảng ", "tức ", "gọi là")


def _top_parens(text: str) -> list[tuple[int, int]]:
    out, depth, start = [], 0, -1
    for i, ch in enumerate(text):
        if ch == "(":
            if depth == 0:
                start = i
            depth += 1
        elif ch == ")" and depth:
            depth -= 1
            if depth == 0:
                out.append((start, i))
    return out


def split_reading(text: str) -> tuple[str, str]:
    """(core, trigger). The book states its condition in the LAST top-level parenthetical of a sentence ('…; lập gia đình muộn mới tốt
    (Thiên Cơ ở Phu Thê)'); earlier parentheses such as '(nam)' belong to the reading. A '; …' segment is kept unless it is an editorial
    note of the rule author ('sách đòi…', '\'gặp\' đọc là…')."""
    text = _strip_cites(text)
    for pre in ("khuynh hướng ", "hạn chế: "):
        if text.startswith(pre):
            text = text[len(pre):]
    segs = [x.strip() for x in text.split(";")]
    keep = [segs[0]] + [x for x in segs[1:] if x and not x.lower().startswith(EDITORIAL)]
    text = "; ".join(keep)
    trig = ""
    ps = _top_parens(text)
    if ps:
        a, b = ps[-1]
        trig = text[a + 1:b]
        text = (text[:a].rstrip() + " " + text[b + 1:].lstrip()).strip()
    core = text.strip(" ;,.")
    if not trig and ": " in core and len(core.split(": ", 1)[0]) <= 45:
        trig, core = core.split(": ", 1)      # 'Đào hoa gặp Thiên Không: duyên đến sớm…' — the book names the configuration first
    return core.strip(" ;,."), re.sub(r"^theo ", "", trig).strip()


def reading_of(rule, claim_label: str) -> tuple[str, str]:
    """The rule's OWN paraphrase when its description has one, else the shared claim label."""
    m = _PARA.search(rule.description)
    if m:
        return m.group(1).strip(), "description"
    return claim_label, "label"


# ---------------------------------------------------------------- concept matching

def match_concepts(core: str) -> list[tuple[str, str, int]]:
    """Greedy longest-first, non-overlapping cue matches -> [(concept, clause, group)] in reading order; group 1 follows a contrast word."""
    lx = lexicon()
    low = core.lower()
    taken = [False] * len(low)
    hits = []
    for cue, cid in lx["cues"]:
        start = 0
        while True:
            i = low.find(cue, start)
            if i < 0:
                break
            j = i + len(cue)
            word_ok = (i == 0 or not low[i - 1].isalnum()) and (j == len(low) or not low[j].isalnum())
            if word_ok and not any(taken[i:j]):
                for k in range(i, j):
                    taken[k] = True
                before = low[max(0, i - 10):i]
                neg = any(before.endswith(n) for n in lx["negators"])
                c = lx["concepts"][cid]
                if neg and c.get("opp"):
                    cid = c["opp"]
                elif neg and not c.get("opp") and c["pol"] in "+-":
                    start = j
                    continue              # negated with no counterpart: do not guess
                hits.append((i, cid))
            start = j
    hits.sort()
    cut = min([low.find(w) for w in _CONTRAST if low.find(w) >= 0] or [len(low)])
    out, seen = [], set()
    bounds = [0] + [m.end() for m in _CLAUSE.finditer(core)] + [len(core) + 1]
    for i, cid in hits:
        if cid in seen:
            continue
        seen.add(cid)
        lo = max(b for b in bounds if b <= i)
        hi = min([b for b in bounds if b > i] + [len(core)])
        clause = core[lo:hi].strip(" ,;")
        clause = re.sub(r"\s*(và|nhưng|mà|song|tuy)$", "", clause).strip()
        if clause.lower().startswith(("nên ", "cần ", "phải biết ")) and cid != "rel.timing":
            continue                      # advice the book gives, not a description of the person (partner-age advice is a timing reading)
        out.append((cid, clause, 1 if i > cut else 0))
    return out


def _valence(core: str) -> str | None:
    low = f" {core.lower()} "
    lx = lexicon()["valence"]
    p = any(f" {w}" in low for w in lx["+"])
    n = any(f" {w}" in low for w in lx["-"])
    return None if p == n else ("+" if p else "-")


# ---------------------------------------------------------------- formal trigger

def leaves(expr, out=None) -> list[tuple]:
    out = [] if out is None else out
    if "fact" in expr:
        out.append((expr["fact"], expr.get("operator", "eq"), expr.get("value")))
    elif "ref" in expr:
        out.append((f"ref:{expr['ref']['palace']}:{expr['ref']['fact']}", expr.get("operator", "eq"), expr.get("value")))
    elif "not" in expr:
        for x in leaves(expr["not"], []):
            out.append(("not:" + x[0], x[1], x[2]))
    else:
        v = expr["count"] if "count" in expr else expr[next(iter(expr))]
        for x in (v if isinstance(v, list) else [v]):
            if isinstance(x, dict):
                leaves(x, out)
    return out


_NORM = {"palace.own_major_stars": "own", "palace.own_stars": "own", "palace.tam_phuong_stars": "tp", "palace.tam_phuong_majors": "tp",
         "palace.tam_phuong_tu_hoa": "tp", "palace.rel.tp_hoa": "tp", "palace.tu_hoa": "own", "palace.rel.opp_stars": "opp", "palace.rel.opp_majors": "opp", "palace.neighbor_stars": "nb", "palace.neighbor_majors": "nb"}


def root_of(lv: list[tuple]) -> tuple:
    """Normalised atoms of a rule's condition: rules that stand on the same chart facts share a root (one voice, however many books say it)."""
    atoms = set()
    for f, op, v in lv:
        if f == "palace.name":
            continue
        vals = v if isinstance(v, list) else [v]
        if f in _NORM:
            for x in vals:
                atoms.add(f"{_NORM[f]}:{x}")
        elif f.startswith("palace.dignity."):
            atoms.add(f"dig:{f.rsplit('.', 1)[1]}:{','.join(map(str, vals))}")
        else:
            atoms.add(f"{f}:{','.join(map(str, vals))}")
    return tuple(sorted(atoms))


def _stars(lv) -> tuple:
    out = []
    for f, _, v in lv:
        for x in (v if isinstance(v, list) else [v]):
            if isinstance(x, str) and (f.startswith("palace.own") or f.startswith("palace.tu_hoa") or f.startswith("palace.tam_phuong") or f.startswith("palace.rel.")) and x not in out:
                out.append(x)
        if f.startswith("palace.dignity."):
            s = f.rsplit(".", 1)[1]
            if s not in out:
                out.append(s)
    return tuple(out)


# ---------------------------------------------------------------- chart-grounded trigger

def true_leaves(expr, facts: dict) -> list[dict]:
    """Leaves of a condition that hold on this chart (refs and negations are not expanded)."""
    from ..knowledge import dsl
    if "fact" in expr:
        return [expr] if dsl.evaluate(expr, facts, None) is True else []
    if "ref" in expr or "not" in expr:
        return []
    v = expr["count"] if "count" in expr else expr[next(iter(expr))]
    return [x for y in (v if isinstance(v, list) else [v]) if isinstance(y, dict) for x in true_leaves(y, facts)]


CHART_FACT_VI = {
    "chart.hour_matches_season": lambda v: "giờ sinh hợp mùa sinh" if v else "giờ sinh không hợp mùa sinh",
    "chart.hour_menh_polarity": lambda v: "giờ sinh và cung Mệnh khác âm dương" if v == "nghich_ly" else "giờ sinh và cung Mệnh cùng âm dương",
    "chart.menh_dac_chinh": lambda v: "Mệnh đắc chính (âm dương năm sinh hợp cung Mệnh)" if v else "Mệnh không đắc chính (âm dương năm sinh lệch cung Mệnh)",
    "chart.am_duong_ly": lambda v: "âm dương thuận lý" if v == "thuan_ly" else "âm dương nghịch lý",
    "chart.year_branch": lambda v: f"thế đứng Đào – Hồng – Thiên Không của tuổi {v}",
    "chart.menh_cuc_relation": lambda v: f"quan hệ Mệnh – Cục: {v}",
}


def chart_trigger(tl: list[dict], palace: str | None, facts: dict) -> tuple[str, tuple, tuple]:
    """Vietnamese phrase for the satisfied leaves, using the chart's own values (a book 'Kình hoặc Đà' becomes the star actually there)."""
    own, tp, nb, hoa, tphoa, extra, used, opp = [], [], [], [], [], [], [], []
    dig = {}
    for lf in tl:
        f, op, v = lf["fact"], lf.get("operator", "eq"), lf.get("value")
        val = facts.get(f)
        used.append((f, val if not isinstance(val, list) else tuple(val)))
        vals = v if isinstance(v, list) else [v]
        if isinstance(val, list):
            vals = [x for x in vals if x in val] or vals
        if f.startswith("palace.dignity."):
            dig[f.rsplit(".", 1)[1]] = val
        elif f in ("palace.own_stars", "palace.own_major_stars"):
            own += [x for x in vals if x not in own]
        elif f in ("palace.tam_phuong_stars", "palace.tam_phuong_majors"):
            tp += [x for x in vals if x not in tp]
        elif f in ("palace.neighbor_stars", "palace.neighbor_majors"):
            nb += [x for x in vals if x not in nb]
        elif f in ("palace.rel.opp_stars", "palace.rel.opp_majors"):
            opp += [x for x in vals if x not in opp]
        elif f == "palace.tu_hoa":
            hoa += [x for x in vals if x not in hoa]
        elif f in ("palace.tam_phuong_tu_hoa", "palace.rel.tp_hoa"):
            tphoa += [x for x in vals if x not in tphoa]
        elif f == "palace.branch":
            extra.append(f"{palace or 'cung'} an tại {val}")
        elif f in ("palace.tuan", "palace.triet") and val:
            extra.append(f"{palace or 'cung'} có " + ("Tuần" if f.endswith("tuan") else "Triệt"))
        elif f == "chart.gender":
            extra.append(f"{val} mệnh")
        elif f in CHART_FACT_VI:
            extra.append(CHART_FACT_VI[f](val))
    for s_ in dig:
        if s_ not in own and s_ not in tp:
            own.append(s_)
    tphoa = [x for x in tphoa if x not in hoa]
    tp = [x for x in tp if x not in own]
    star = lambda x: f"{x} ({dig[x]})" if x in dig and dig[x] not in (None, "unspecified") else x
    where = palace or "lá số"
    parts = []
    if own or hoa:
        parts.append(_join([star(x) for x in own] + hoa) + f" tại {where}")
    if opp:
        parts.append(_join(opp) + f" xung chiếu {where}")
    if tp or tphoa:
        parts.append(_join(tp + tphoa) + f" hội chiếu về {where}")
    if nb:
        parts.append(_join(nb) + f" giáp {where}")
    parts += extra
    present = tuple(dict.fromkeys(own + hoa + opp + tp + tphoa + nb))
    return ", ".join(parts), tuple(used), present


def _join(xs: list[str]) -> str:
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " và " + xs[-1] if xs else ""


# ---------------------------------------------------------------- applicability

def _scope_ok(guard: dict, palace: dict, geo) -> bool:
    star = guard["star"]
    if guard["scope"] == "dong_cung_doi_cung":
        return star in palace["stars"] or star in geo.opp(palace)["stars"]
    return True


def annotate(findings, rules, claims_vi, palaces=None, geo=None, base: dict | None = None) -> Annotation:
    """Fired findings -> SemanticEvidence. Draft rules and guarded rules are reported, not narrated."""
    lx = lexicon()
    facets, concepts, onto = lx["ontology"]["facets"], lx["concepts"], lx["ontology"]
    rmap = {r.id: r for r in rules}
    pal_by_name = {p["name"]: p for p in (palaces or [])}
    ann = Annotation()
    seen_struct: set[str] = set()
    seen: set[tuple] = set()
    for f in findings:
        r = rmap[f.rule_id]
        palace = f.subject.split(":", 1)[1] if ":" in f.subject else None
        if (r.id, f.subject, f.claim) in seen:
            continue
        seen.add((r.id, f.subject, f.claim))
        if lx["auto"].get("structural_duplicate") and r.id.startswith("TV_STRUCT_"):
            if r.id in seen_struct:
                ann.excluded.append({"rule": r.id, "subject": f.subject, "reason": "cấu trúc cấp lá số được khẳng định lặp ở nhiều cung; chỉ tính một lần"})
                continue
            seen_struct.add(r.id)
        label = (claims_vi.get(f.claim) or {}).get("label", f.claim)
        if f.claim.startswith(LABEL_PREFIX):
            ann.unmapped.append({"rule": r.id, "subject": f.subject, "claim": f.claim, "reading": label, "why": "nhãn phân loại, không phải nhận định"})
            continue
        if f.basis != "verified":
            ann.drafts.append({"rule": r.id, "subject": f.subject, "claim": f.claim, "label": label})
            continue
        guard = lx["guards"].get(r.id)
        applic, note = "ok", ""
        if guard and guard["action"] == "exclude":
            ann.excluded.append({"rule": r.id, "subject": f.subject, "reason": guard["reason"]})
            continue
        if guard and guard["action"] == "recheck_scope":
            p = pal_by_name.get(palace)
            if p is None or geo is None or not _scope_ok(guard, p, geo):
                ann.excluded.append({"rule": r.id, "subject": f.subject, "reason": guard["reason"] + " Kiểm tra lại theo câu sách: điều kiện không thỏa trên lá số này."})
                continue
            applic, note = "rechecked", guard["reason"] + " Đã kiểm tra lại theo câu sách: thỏa."
        text, src = reading_of(r, label)
        if guard and guard["action"] == "use_description":
            applic, note = "relabelled", guard["reason"]
        core, trig = split_reading(text)
        if src == "label" and not trig:
            trig = split_reading(label)[1]
        lv = [x for x in leaves(r.conditions) if x[0] != "palace.name"]
        ctext, used, present = "", (), ()
        if base is not None:
            fx = dict(base.get("chart", {}))
            fx.update(base.get(f.subject, {}))
            ctext, used, present = chart_trigger([x for x in true_leaves(r.conditions, fx) if x["fact"] != "palace.name"], palace, fx)
        common = dict(rule_id=r.id, finding_id=f.id, subject=f.subject, palace=palace, claim=f.claim, reading=_strip_cites(text),
                      trigger_text=trig, leaves=tuple((a, b, repr(c)) for a, b, c in lv), root=root_of(lv), stars=_stars(lv),
                      basis=f.basis, schools=tuple(sorted({SCHOOL.get(s, s) for s in r.sourceIds})), cites=tuple(_CITE.findall(r.description)),
                      applicability=applic, applicability_note=note, chart_trigger=ctext or trig, facts_used=used, present_stars=present)
        hits = match_concepts(core)
        mapped: list[tuple[str, str, int, str]] = []
        pc = onto["palace_concepts"].get(palace or "")
        for cid, clause, grp in hits:
            c = concepts[cid]
            if pc and palace in RELATION_PALACES and c["facet"].split(".")[0] not in ("relationships",) and cid not in ("life.mitigated",):
                # in a palace about another person, a trait or outcome describes THAT person: the palace topic, not the native
                cid = pc[1] if (c["pol"] == "-" or f.effect == "limit") else pc[0]
                how = "palace_fallback"
            elif pc and cid in ("life.blessed", "life.hardship") and palace != "Mệnh":
                cid, how = (pc[0] if cid == "life.blessed" else pc[1]), "palace_fallback"
            else:
                how = "cue"
            if all(m[0] != cid for m in mapped):
                mapped.append((cid, clause, grp, how))
        if not mapped and pc:
            v = "-" if f.effect == "limit" else _valence(core)
            if v:
                mapped.append((pc[0] if v == "+" else pc[1], core, 0, "palace_fallback"))
        # a sentence that names both sides of one axis: keep the side the rule's effect states
        ids = {m[0] for m in mapped}
        mapped = [m for m in mapped if not (concepts[m[0]].get("opp") in ids and
                                            ((f.effect == "limit" and concepts[m[0]]["pol"] == "+") or (f.effect != "limit" and concepts[m[0]]["pol"] == "-")))]
        if not mapped:
            ann.unmapped.append({"rule": r.id, "subject": f.subject, "claim": f.claim, "reading": core})
            continue
        groups = {g: [m[0] for m in mapped if m[2] == g] for g in (0, 1)}
        for i, (cid, clause, grp, how) in enumerate(mapped):
            c = concepts[cid]
            pol, role, modality = c["pol"], "asserts", "tendency"
            low = clause.lower()
            if "có thể" in low:
                modality = "potential"
            elif re.search(r"\b(nếu|khi|cần|mới|thì)\b", low):
                modality = "condition"
            if modality == "condition" and how == "cue" and ((f.effect == "limit" and c["pol"] == "+") or (f.effect != "limit" and c["pol"] == "-")):
                continue                  # an exception clause of the sentence ('… ; gặp Tham, Vũ thì lại rực rỡ'), not what this rule asserts
            if c["kind"] == "rescue":
                role, modality = "mitigates", "rescue"
            if f.effect == "limit":
                role, modality = ("limits" if pol == "+" else "asserts"), "limitation"
                pol = "-"
            ev = SemanticEvidence(id=f"{r.id}@{palace or 'chart'}#{i}", segment=clause, concept=cid, facet=c["facet"],
                                  domain=facets[c["facet"]]["domain"], kind=c["kind"], polarity=pol, modality=modality, role=role,
                                  paired_with=tuple(groups[1 - grp]) if groups[0] and groups[1] else (), mapping=how, **common)
            ann.evidence.append(ev)
    return ann


def book_pairings(rules, claims_vi) -> dict[frozenset, list[dict]]:
    """Concept pairs that a VERIFIED book sentence itself sets against each other ('A nhưng B'), over the whole rule library (not only fired
    rules). Used only to cite that a book frames two traits together; never to make a rule fire."""
    out: dict[frozenset, list[dict]] = {}
    for r in rules:
        if r.system != "tu_vi" or r.reviewStatus != "verified":
            continue
        for c in r.consequences:
            if c.get("kind") != "finding":
                continue
            text, _ = reading_of(r, (claims_vi.get(c["claim"]) or {}).get("label", c["claim"]))
            core, _ = split_reading(text)
            hits = match_concepts(core)
            a = [h[0] for h in hits if h[2] == 0]
            b = [h[0] for h in hits if h[2] == 1]
            for x in a:
                for y in b:
                    if x != y:
                        out.setdefault(frozenset((x, y)), []).append({"rule": r.id, "cites": _CITE.findall(r.description), "reading": _strip_cites(text)})
    return out


def claim_tone(label: str) -> str | None:
    """'+' | '-' | '~' (both sides) for a Vietnamese claim phrase, or None when no concept cue is found. 'hạn chế:' phrases are '-'."""
    if label.startswith("hạn chế"):
        return "-"
    core, _ = split_reading(label)
    pols = {lexicon()["concepts"][cid]["pol"] for cid, _, _ in match_concepts(core)}
    if "+" in pols and "-" in pols:
        return "~"
    return "+" if "+" in pols else "-" if "-" in pols else None


def claim_facet(label: str) -> str | None:
    """Facet of the first concept a claim phrase names (its leading idea), or None. Used to route readings to the chapter that answers
    the reader's question instead of the palace that fired them."""
    core, _ = split_reading(label)
    hits = match_concepts(core)
    return lexicon()["concepts"][hits[0][0]]["facet"] if hits else None


def stable_hash(*parts) -> int:
    return int(hashlib.sha1("|".join(map(str, parts)).encode("utf-8")).hexdigest()[:8], 16)
