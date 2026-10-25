"""Integrity of the Mai Hoa source snapshot, translation, rule extract and
golden book examples (engine/data/mai_hoa/, tests/golden/mai_hoa_book_examples.json)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parents[1] / "data" / "mai_hoa"
GOLDEN = Path(__file__).resolve().parent / "golden" / "mai_hoa_book_examples.json"

TRIGRAMS = set("乾兌離震巽坎艮坤")


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def source():
    return _load(DATA / "source_zh.json")


@pytest.fixture(scope="module")
def sections(source):
    return {s["id"]: s for s in source["sections"]}


@pytest.fixture(scope="module")
def text():
    return _load(DATA / "text.json")


@pytest.fixture(scope="module")
def rules():
    return _load(DATA / "rules_extract.json")


@pytest.fixture(scope="module")
def golden():
    return _load(GOLDEN)


def test_snapshot_pages_hash(source):
    keys = [p["key"] for p in source["pages"]]
    assert keys == ["k0", "k1", "k2", "k3"]
    for p in source["pages"]:
        data = p["wikitext"].encode("utf-8")
        assert hashlib.sha256(data).hexdigest() == p["sha256"], p["title"]
        assert p["revid"] and p["fetched"] and p["url"].startswith("https://zh.wikisource.org/")


def test_section_ids_unique_and_paths(source):
    ids = [s["id"] for s in source["sections"]]
    assert len(ids) == len(set(ids))
    for s in source["sections"]:
        if s["page"] != "k0":
            assert s["path"].startswith(("卷一/", "卷二/", "卷三/")), s["path"]
    assert any(s["path"] == "卷二/體用生克篇之二/求財占第十" for s in source["sections"])


def test_text_covers_every_section(text, sections):
    entries = text["sections"]
    ids = [e["id"] for e in entries]
    assert len(ids) == len(set(ids))
    assert set(ids) == set(sections)
    for e in entries:
        s = sections[e["id"]]
        assert e["path"] == s["path"]
        assert e["han"] == s["text"]
        assert e["dich_gia"] == "Thiên Bàn"
        assert e["status"] == "draft"
        assert isinstance(e["notes"], list)
        if s.get("empty"):
            assert e.get("empty") is True
            continue
        assert e["vi"].strip(), e["id"]
        assert e["vi"].count("\n") == e["han"].count("\n"), e["id"]


def test_rule_quotes_are_substrings(rules, sections):
    ids = [r["id"] for r in rules["rules"]]
    assert len(ids) == len(set(ids))
    kinds = set(rules["kinds"])
    undefined = {u["id"] for u in rules["undefined"]}
    for r in rules["rules"]:
        assert r["kind"] in kinds, r["id"]
        assert r["han_quote"] and r["han_quote"] in sections[r["section"]]["text"], r["id"]
        assert r["vi"].strip(), r["id"]
        for u in r.get("undefined", []):
            assert u in undefined, (r["id"], u)


RELATIONS = {"the_khac_dung", "dung_khac_the", "the_sinh_dung", "dung_sinh_the", "ty_hoa"}


def test_relation_clauses(rules):
    by_id = {r["id"]: r for r in rules["rules"]}
    for rid in ("t.five_relations", "p.nhan_su"):
        assert "han_by_relation" in by_id[rid], rid
    for r in rules["rules"]:
        f = r.get("formula") or {}
        if r["kind"] == "topic" and RELATIONS & set(f):
            assert "han_by_relation" in r, r["id"]
        if "han_by_relation" not in r:
            continue
        han, vi = r["han_by_relation"], r["vi_by_relation"]
        assert han and set(han) <= RELATIONS, r["id"]
        assert set(han) == set(vi), r["id"]
        for k, clause in han.items():
            assert clause and clause in r["han_quote"], (r["id"], k)
            assert vi[k].strip(), (r["id"], k)


def test_sinh_khac_the_have_real_translation(rules):
    for r in rules["rules"]:
        if r["id"].startswith(("t.sinh_the.", "t.khac_the.")):
            assert "xem bản dịch" not in r["vi"] and len(r["vi"]) > 60, r["id"]


def test_rules_cover_required_material(rules):
    by_section = {}
    for r in rules["rules"]:
        by_section.setdefault(r["section"], set()).add(r["kind"])
    # all 18 topic chapters of 體用生克篇之二
    for n in range(1, 19):
        assert f"k2.2.{n}" in by_section, f"topic chapter k2.2.{n} has no rule"
    ids = {r["id"] for r in rules["rules"]}
    for rid in ["c.gua_mod8", "c.yao_mod6", "c.hu", "c.hu_qian_kun", "c.nam_thang_ngay_gio", "c.vat_so",
                "c.thanh_am", "c.chu_1", "c.chu_11_plus", "c.truong_xich", "c.xich_thon", "c.vi_nhan",
                "c.tu_ky", "c.dong_vat", "c.tinh_vat", "c.hau_thien_doan_phap", "t.assign", "t.five_relations"]:
        assert rid in ids, rid


REQUIRED_EXAMPLES = {"guan_mei", "mu_dan", "lin_ye_kou_men", "jin_ri_dong_jing", "xi_lin_si", "lao_ren_you_se",
                     "shao_nian_xi_se", "niu_ai_ming", "ji_bei_ming", "ku_zhi_zhui_di"}


def test_golden_examples_fields(golden, sections):
    ex = golden["examples"]
    ids = [e["id"] for e in ex]
    assert len(ids) == len(set(ids))
    assert REQUIRED_EXAMPLES <= set(ids)
    assert sum(1 for e in ex if e["id"].startswith("bian_shi_")) == 8
    for e in ex:
        for f in ("id", "name", "section", "kind", "method", "han_quote", "inputs", "book", "hand_check",
                  "arithmetic_ok", "discrepancies"):
            assert f in e, (e["id"], f)
        assert e["han_quote"] in sections[e["section"]]["text"], e["id"]
        b = e["book"]
        assert (b.get("hexagram") or e["inputs"].get("hexagram")
                or (b.get("upper") and b.get("lower")) or (e["inputs"].get("upper") and e["inputs"].get("lower"))), e["id"]
        for f in ("upper", "lower", "the", "yong", "bian_trigram"):
            if b.get(f) is not None:
                assert b[f] in TRIGRAMS, (e["id"], f)
        for t in b.get("hu") or []:
            assert t in TRIGRAMS, e["id"]
        ml = b.get("moving_line")
        assert ml is None or 1 <= ml <= 6, e["id"]
        if not e["arithmetic_ok"]:
            assert e["discrepancies"], e["id"]


def test_golden_book_arithmetic_is_self_consistent(golden):
    """Where the book states sums and remainders, they must agree with mod 8 / mod 6
    (remainder 0 → 8 / 6) — a check of the transcription, not of any engine."""
    tt = {"乾": 1, "兌": 2, "離": 3, "震": 4, "巽": 5, "坎": 6, "艮": 7, "坤": 8}
    for e in golden["examples"]:
        b = e["book"]
        for side in ("upper", "lower"):
            if f"{side}_sum" in b and b.get(side):
                r = b[f"{side}_sum"] % 8 or 8
                assert tt[b[side]] == r, (e["id"], side)
        if "line_sum" in b and b.get("moving_line"):
            assert (b["line_sum"] % 6 or 6) == b["moving_line"], e["id"]
        inp = e["inputs"]
        if {"year_number", "lunar_month", "lunar_day", "hour_number"} <= inp.keys() and "upper_sum" in b:
            extra = inp.get("surname_strokes", 0)
            assert b["upper_sum"] == inp["year_number"] + inp["lunar_month"] + inp["lunar_day"] + extra, e["id"]
            assert b["lower_sum"] == b["upper_sum"] + inp["hour_number"], e["id"]
