"""Rule-based synthesis engine & Vietnamese narrative grammar (tvbt/synthesis: semantics, reasoner, grammar, crosspalace, chapters).

Covers: flag/API preservation, lexicon integrity, applicability guards, Semantic IR annotation (own paraphrase, limit effect, exception clauses,
book pairings), evidence independence, contradiction typing, narrative invariants (provenance, no drafts in prose, no banned wording, one full
narration per proposition, sensitive framing, determinism) over a sweep of real charts, and the reference chart from the request (Cự Môn hãm
thủ Mệnh + Hóa Lộc + Kình Dương + Hồng Loan)."""
from __future__ import annotations

import json
import random
import re
from functools import lru_cache
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tvbt import tuvi
from tvbt.api import app
from tvbt.calendar_core import BirthInput, normalize
from tvbt.knowledge.loader import load_all, load_claims
from tvbt.reasoning import engine, facts
from tvbt.synthesis import semantics as sm
from tvbt.synthesis.chapters import Context, build_synthesis
from tvbt.synthesis.grammar import BANNED
from tvbt.synthesis.reasoner import Proposition, Root, classify_contradiction, group
from tvbt.synthesis.structures import Geo

client = TestClient(app)
BODY = {"year": 1990, "month": 5, "day": 15, "hour": 10, "minute": 30, "gender": "male"}
REF = (2001, 3, 10, 10, "male")     # Mệnh Tuất: Cự Môn hãm + Hóa Lộc (tuổi Tân), Kình Dương, Hỏa Tinh, Hồng Loan


@lru_cache(maxsize=None)
def lib():
    rules, sources = load_all()
    return rules, sources, load_claims()


def chart(y, m, d, h, g="male"):
    return tuvi.compute(normalize(BirthInput(y, m, d, h, 30, "Asia/Ho_Chi_Minh", g)))


@lru_cache(maxsize=None)
def synth(y, m, d, h, g="male"):
    rules, sources, claims = lib()
    return build_synthesis(chart(y, m, d, h, g), rules, sources, claims, y, 2026)


@lru_cache(maxsize=None)
def ctx(y, m, d, h, g="male"):
    rules, sources, claims = lib()
    return Context(chart(y, m, d, h, g), rules, sources, claims)


def sweep(n=40, seed=11):
    rnd = random.Random(seed)
    return [(rnd.randint(1940, 2030), rnd.randint(1, 12), rnd.randint(1, 28), rnd.randint(0, 23), rnd.choice(["male", "female"])) for _ in range(n)]


def sentences(out):
    for c in out["chapters"]:
        for p in c["paragraphs"]:
            for s in p["sentences"]:
                yield c["id"], p, s


# ---------------------------------------------------------------- flag & API preservation

def test_flag_off_404_and_other_endpoints_unchanged(monkeypatch):
    monkeypatch.delenv("TVBT_DEEP_INTERPRETATION", raising=False)
    assert client.post("/api/synthesis", json=BODY).status_code == 404
    before = {u: client.post(u, json=BODY).text for u in ("/api/reasoning", "/api/analysis", "/api/chart")}
    monkeypatch.setenv("TVBT_DEEP_INTERPRETATION", "1")
    r = client.post("/api/synthesis", json={**BODY, "to_year": 2026})
    assert r.status_code == 200
    j = r.json()
    assert [c["id"] for c in j["chapters"]] == ["tong_quan", "ban_menh", "tinh_cach", "cong_danh", "tai_bach", "quan_he", "dai_han", "cach_cuc"]
    assert "semantic_ir" not in j
    assert "semantic_ir" in client.post("/api/synthesis", json={**BODY, "level": 5}).json()
    assert {u: client.post(u, json=BODY).text for u in before} == before


def test_no_language_model_in_runtime():
    src = " ".join(p.read_text("utf-8") for p in (Path(sm.__file__).parent).glob("*.py"))
    assert not re.search(r"\b(openai|anthropic|gemini|transformers|langchain|ollama|embedding)\b", src, re.I)


# ---------------------------------------------------------------- lexicon integrity

def test_lexicon_integrity():
    lx = sm.lexicon()
    facets, concepts = lx["ontology"]["facets"], lx["concepts"]
    for c in concepts.values():
        assert c["facet"] in facets, c["id"]
        assert c["pol"] in "+-~" and c["np"] and c["cues"]
        if c.get("opp"):
            assert c["opp"] in concepts and concepts[c["opp"]]["facet"] == c["facet"], c["id"]
    for r in lx["relations"]:
        assert r["a"] in concepts and r["b"] in concepts, r
        if r["type"] in ("qualifies", "conditions", "elaborates") and r.get("frame"):
            assert r["frame"] in lx["frames"], r
    for f in facets.values():
        assert f["home"] in lx["ontology"]["chapters"]
    for pal, pair in ((k, v) for k, v in lx["ontology"]["palace_concepts"].items() if k != "note"):
        assert all(x in concepts for x in pair), pal
    rules = {r.id for r in lib()[0]}
    assert all(g["rule"] in rules for g in lx["guards"].values())


# ---------------------------------------------------------------- Semantic IR annotation

def test_reading_split_keeps_tail_after_condition_and_drops_editorial_notes():
    core, trig = sm.split_reading("Cự Môn hãm ở Thìn/Tuất nhưng hóa Lộc (tuổi Tân) thì vẫn khá")
    assert "vẫn khá" in core and trig == "tuổi Tân"
    core, trig = sm.split_reading("nên lấy người ít tuổi hơn (nam), người lớn tuổi hơn (nữ); lập gia đình muộn mới tốt (Thiên Cơ ở Phu Thê)")
    assert trig == "Thiên Cơ ở Phu Thê" and "lập gia đình muộn" in core
    core, _ = sm.split_reading("vinh hoa (Hóa Quyền ở Mệnh); sách đòi 'nhập miếu' mà bảng độ sáng không có")
    assert "sách đòi" not in core


def test_cue_matching_longest_match_and_negation():
    ids = lambda t: [h[0] for h in sm.match_concepts(t)]
    assert ids("kém sáng suốt, đa nghi") == ["cog.dull", "cog.suspicious"]
    assert "fin.scarcity" in ids("khó giàu sang")
    assert "fin.abundance" in ids("không lo thiếu thốn")
    assert ids("nên khiêm nhường khéo léo để vươn lên") == []           # advice, not a description
    hits = sm.match_concepts("nghĩa khí nhưng nóng nảy")
    assert [(h[0], h[2]) for h in hits] == [("values.integrity", 0), ("temper.hot", 1)]


def test_reference_chart_annotation_guards_and_limit_effect():
    c = ctx(*REF)
    ev = {(e.rule_id, e.concept) for e in c.ann.evidence}
    # Hóa Lộc ở Tứ Mộ: the shared label says 'tài lộc thuận lợi'; the rule's own paraphrase and its 'limit' effect make it a limitation
    assert ("TV_KL_PHU2_HOA_LOC_TU_MO", "fin.scarcity") in ev and ("TV_KL_PHU2_HOA_LOC_TU_MO", "fin.abundance") not in ev
    # Hồng Loan gặp Thiên Không: the book says đồng cung / xung chiếu; here Thiên Không is only in a tam hợp palace -> the rule no longer fires
    assert not any(f.rule_id == "TV_KL_AUX_HONG_KHONG" for f in c.res.findings)
    # Quan Phủ: its own claim and sentence, not the shared label that adds Thái Tuế
    qp = [e for e in c.ann.evidence if e.rule_id == "TV_KL_AUX_QUAN_PHU_VIET"]
    assert qp and all("Thái Tuế" not in e.reading for e in qp) and qp[0].claim == "quan_phu_menh_mieng_tieng"
    # a chart-level structure asserted once per triad palace counts once
    assert sum(1 for e in c.ann.evidence if e.rule_id.startswith("TV_STRUCT_")) <= 1
    # the book itself pairs 'nghĩa khí' with 'nóng nảy'
    hl = [e for e in c.ann.evidence if e.rule_id == "TV_KL_AUX_HOA_LINH"]
    assert {e.concept for e in hl} == {"values.integrity", "temper.hot"} and all(e.paired_with for e in hl)
    # triggers are grounded in the chart: 'Kình hoặc Đà ở Mệnh' becomes the star actually present
    kd = next(e for e in c.ann.evidence if e.rule_id == "TV_KL_AUX_KINH_DA")
    assert kd.chart_trigger == "Kình Dương tại Mệnh" and "Đà La" not in kd.present_stars
    assert not c.ann.drafts or all(not any(e.rule_id == d["rule"] for e in c.ann.evidence) for d in c.ann.drafts)


def test_semantic_coverage_regression_guard():
    rules, sources, claims = lib()
    tot = mapped = 0
    for y, m, d, h, g in sweep(30, 3):
        tv = chart(y, m, d, h, g)
        base = facts.tuvi_facts(tv)
        res = engine.run(rules, sources, base, system="tu_vi")
        a = sm.annotate(res.findings, rules, claims, tv.palaces, Geo(tv.palaces, tv.tu_hoa), base)
        ver = {(f.rule_id, f.subject) for f in res.findings if f.basis == "verified" and not f.claim.startswith(sm.LABEL_PREFIX)}
        tot += len(ver)
        mapped += len({(e.rule_id, e.subject) for e in a.evidence})
    assert mapped / tot >= 0.9


# ---------------------------------------------------------------- independence & contradiction typing

def _ev(rule, concept, atoms, books=("Khảo Luận",), palace="Mệnh", pol="+"):
    return sm.SemanticEvidence(id=rule, rule_id=rule, finding_id=rule, subject=f"palace:{palace}", palace=palace, claim=rule, reading="", segment="",
                               concept=concept, facet=sm.lexicon()["concepts"][concept]["facet"], domain="identity", kind="trait", polarity=pol,
                               modality="tendency", role="asserts", trigger_text=rule, leaves=(), root=tuple(sorted(atoms)), stars=(), basis="verified",
                               schools=tuple(books), cites=())


def test_same_fact_in_several_books_is_one_ground():
    props = group([_ev("A", "career.authority", ["own:Kình Dương", "own:Hỏa Tinh"], ("Thực Hành",)),
                   _ev("B", "career.authority", ["own:Kình Dương", "own:Hỏa Tinh"], ("Toàn Thư",)),
                   _ev("C", "career.authority", ["own:Kình Dương", "dig:Kình Dương:miếu"], ("Toàn Thư",)),
                   _ev("D", "career.authority", ["own:Tử Vi", "own:Tả Phụ"], ("Khảo Luận",))])
    p = props["career.authority@Mệnh"]
    assert len(p.roots) == 3
    weights = sorted(r.weight for r in p.roots)
    assert weights == [0.5, 1.0, 1.0]       # C shares Kình Dương with A/B; D is independent; A+B are one root with two books
    assert next(r for r in p.roots if r.atoms == ("own:Hỏa Tinh", "own:Kình Dương")).books == ["Thực Hành", "Toàn Thư"]


def _prop(pid, concept, atoms, books, palace="Mệnh"):
    p = Proposition(pid, concept, "x", "identity", "trait", palace, "+")
    e = _ev(pid, concept, atoms, books, palace)
    p.evidence, p.roots = [e], [Root(tuple(sorted(atoms)), [e])]
    return p


def test_contradiction_classes():
    gen = _prop("a", "cog.sharp", ["own:Cự Môn"], ["Khảo Luận"])
    spec = _prop("b", "cog.dull", ["own:Cự Môn", "dig:Cự Môn:hãm"], ["Thực Hành"])
    assert classify_contradiction(gen, spec)[0] == "refinement"
    other = _prop("c", "cog.dull", ["own:Kình Dương"], ["Thực Hành"])
    assert classify_contradiction(gen, other)[0] == "both_hold"
    assert classify_contradiction(gen, _prop("d", "cog.dull", ["own:Cự Môn"], ["Toàn Thư"]))[0] == "school_divergence"
    assert classify_contradiction(gen, _prop("e", "cog.dull", ["own:Cự Môn"], ["Khảo Luận"]))[0] == "unresolved"
    assert classify_contradiction(gen, _prop("f", "cog.dull", ["own:Cự Môn", "dig:Cự Môn:hãm"], ["Thực Hành"], palace="Phúc Đức"))[0] == "both_hold"


# ---------------------------------------------------------------- the reference chart (request example)

def test_reference_chart_explains_relations_instead_of_listing():
    out = synth(*REF)
    ch = {c["id"]: c for c in out["chapters"]}
    tc = " ".join(p["text"] for p in ch["tinh_cach"]["paragraphs"])
    bm = " ".join(p["text"] for p in ch["ban_menh"]["paragraphs"])
    # Cự Môn thủ Mệnh (KL, chung) vs Cự Môn hãm (TH, riêng): a refinement, not two loose lines
    assert "quan hệ chung – riêng" in bm or "cho trường hợp chung" in tc
    assert "Cự Môn ở vị trí hãm" in tc
    # the Kình/Hỏa readings are framed (strength and excess / inner vs outer) and the KL sentence that pairs them is cited
    assert "nghĩa khí nhưng nóng nảy" in tc
    assert "hai đầu của cùng một phẩm chất" in tc or "không nên đọc đây là hai tính cách trái ngược" in tc.lower()
    # the TH rescue sentence for Cự Môn hãm ở Thìn/Tuất + Hóa Lộc is used as a mitigation, quoted
    assert "thì vẫn khá" in bm
    # Bản Mệnh is built around the stars of Mệnh, in order: chính tinh, then its Hóa, then Kình Dương
    anchors = [p for p in ch["ban_menh"]["paragraphs"] if p["role"] == "anchor"]
    assert anchors[0]["text"].startswith("Trục thứ nhất của bản mệnh là Cự Môn (hãm) thủ Mệnh")
    assert "Hóa Lộc tại Mệnh" in anchors[1]["text"] and "Kình Dương" in anchors[2]["text"]


def test_personality_chapter_draws_on_menh_not_only_phuc_duc():
    out = synth(*REF)
    tc = next(c for c in out["chapters"] if c["id"] == "tinh_cach")
    pals = {t["main"]["palace"] for t in tc["themes"]}
    assert "Mệnh" in pals and len(tc["themes"]) >= 4


# ---------------------------------------------------------------- narrative invariants over a sweep

@pytest.mark.parametrize("b", sweep(24, 5) + [REF])
def test_narrative_invariants(b):
    out = synth(*b)
    c = ctx(*b)
    fired = {f.rule_id for f in c.res.findings}
    verified = {f.rule_id for f in c.res.findings if f.basis == "verified"}
    for cid, p, s in sentences(out):
        assert not any(re.search(x, s["text"], re.I) for x in BANNED), s["text"]
        if s["kind"] in ("claim", "ground", "support", "contrast", "condition") and cid not in ("cach_cuc", "dai_han"):
            assert s["provenance"], s
            assert set(s["provenance"]) <= fired, (s["provenance"], s["text"])
            assert set(s["provenance"]) <= verified, s["text"]            # draft rules never reach the composed prose
        if s["basis"] == "he_thong":
            assert s["kind"] in ("interaction", "reflection", "synthesis", "limit", "intro", "condition"), s
    for ch in out["chapters"]:
        v = ch["validation"]
        assert not [i for i in v["issues"] if i["type"] in ("no_provenance", "banned_wording", "sensitive_unframed", "conflict_untold")], (ch["id"], v["issues"])
        assert v["metrics"]["consecutive_same_opener"] <= 2
        texts = [s["text"] for p in ch["paragraphs"] for s in p["sentences"] if s["kind"] != "limit"]
        assert len(texts) == len(set(texts)), ch["id"]
        claims = [pid for p in ch["paragraphs"] for s in p["sentences"] if s["kind"] == "claim" and p["role"] == "theme" for pid in s["props"]]
        assert len(claims) == len(set(claims)), (ch["id"], claims)   # a proposition is introduced as a claim at most once per chapter
        for p in ch["paragraphs"]:
            if p["role"] == "theme" and any(s["kind"] == "claim" for s in p["sentences"]):
                ids = [pid for s in p["sentences"] if s["kind"] == "claim" for pid in s["props"]]
                if any(c.props[i].sensitive for i in ids if i in c.props):
                    assert "truyền thống" in p["text"]


def test_deterministic():
    rules, sources, claims = lib()
    a = build_synthesis(chart(*REF), rules, sources, claims, 2001, 2026)
    b = build_synthesis(chart(*REF), rules, sources, claims, 2001, 2026)
    assert json.dumps(a, ensure_ascii=False, sort_keys=True) == json.dumps(b, ensure_ascii=False, sort_keys=True)


def test_empty_evidence_does_not_pad():
    """A chapter without grounded themes says so in one line instead of writing filler."""
    for b in sweep(30, 9):
        for ch in synth(*b)["chapters"]:
            if ch.get("empty") and ch["id"] not in ("cach_cuc",):
                theme = [p for p in ch["paragraphs"] if p["role"] == "theme"]
                assert not theme or all(len(p["sentences"]) <= 2 for p in theme)


# ---------------------------------------------------------------- review 17/05/1990: tone and chapter routing served with the claims

def test_claim_tone_handles_negation_and_conditional_phrases():
    assert sm.claim_tone("khuynh hướng tiền bạc đến tự nhiên, ít mất công lao khó nhọc (Lộc Tồn ở Tài Bạch)") == "+"
    assert sm.claim_tone("khuynh hướng không giàu thì sang (Nhật, Nguyệt giáp hai bên Mệnh)") == "+"
    assert sm.claim_tone("tính cách thường được mô tả là cẩn trọng, ít gây thị phi") != "-"
    assert sm.claim_tone("khuynh hướng khó đạt công danh (Kiếp/Không hãm đóng cung Quan)") == "-"
    assert sm.claim_tone("hạn chế: gian truân (Thiên Tướng đồng cung Không/Kiếp)") == "-"


def test_claims_endpoint_serves_tone_and_facet_for_routing():
    j = client.get("/api/claims").json()
    assert j["tone:tt_tai_bach_loc_ton_base_p"] == "+"
    # Mệnh readings about character route to Tính cách, family readings at Phúc Đức to Quan hệ (report.js topicChapter)
    menh_traits = [k for k, v in j.items() if not k.startswith(("tone:", "facet:", "limit:")) and "trọng hậu" in v]
    assert menh_traits and all(j.get("facet:" + k, "").startswith("identity.") for k in menh_traits)
    ho_hang = [k for k, v in j.items() if not k.startswith(("tone:", "facet:", "limit:")) and "họ hàng đông" in v]
    assert ho_hang and all(j.get("facet:" + k) == "relationships.family" for k in ho_hang)
