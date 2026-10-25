"""pack_ham_so.json (tools/build_ham_so_pack.py, Tử Vi Hàm Số Quyển Nhì pp.84-233): every rule has a quote that is on its printed page of
the PDF (skipped when the book is absent), 'đắc / hãm địa' is read in the book's own table, and the rules fire on the book's conditions
and not elsewhere."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import book_text  # noqa: E402

from tvbt.knowledge.loader import load_all  # noqa: E402
from tvbt.knowledge.schema import load_pack  # noqa: E402
from tvbt.reasoning import engine  # noqa: E402

PACK = json.loads((ROOT / "engine" / "data" / "pack_ham_so.json").read_text("utf-8"))["rules"]
# the Mệnh readings are staged (not in the loader's PACKS, see the builder); their quotes and conditions are checked all the same
MENH_PATH = ROOT / "engine" / "data" / "experimental" / "pack_ham_so_menh.json"
MENH = json.loads(MENH_PATH.read_text("utf-8"))["rules"]
QUOTES = json.loads((ROOT / "engine" / "data" / "quotes_ham_so.json").read_text("utf-8"))["quotes"]
DIG = json.loads((ROOT / "engine" / "data" / "ham_so_dignity.json").read_text("utf-8"))
CLAIMS = json.loads((ROOT / "engine" / "data" / "claims_vi.json").read_text("utf-8"))
RULES, SOURCES = load_all()
BR = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]


def test_every_rule_has_a_quote_a_page_cite_and_a_claim():
    q = {x["rule"]: x for x in QUOTES}
    assert {r["id"] for r in PACK + MENH} == set(q)
    assert all(r["conditions"]["all"][0]["value"] != "Mệnh" for r in PACK) and all(r["conditions"]["all"][0]["value"] == "Mệnh" for r in MENH)
    for r in PACK + MENH:
        assert f"[HS p.{q[r['id']]['page']}]" in r["description"], r["id"]
        assert r["sourceIds"] == ["SRC_HAM_SO"] and r["schoolId"] == "ham_so"
    for r in PACK:
        claim = r["consequences"][0]["claim"]
        assert claim in CLAIMS, claim
    src = json.loads((ROOT / "engine" / "data" / "sources.json").read_text("utf-8"))["sources"]
    assert any(s["id"] == "SRC_HAM_SO" and s["verified"] for s in src)


def test_pack_is_loaded_and_the_menh_pack_is_not():
    ids = {r.id for r in RULES}
    assert {r["id"] for r in PACK} <= ids
    assert not ({r["id"] for r in MENH} & ids)


@pytest.mark.skipif(not book_text.available("HS"), reason="Tử Vi Hàm Số PDF not present")
def test_quotes_are_on_their_page():
    bad = [x for x in QUOTES if not book_text.quote_on_page("HS", x["page"], x["quote"])]
    assert not bad, bad


@pytest.mark.skipif(not book_text.available("HS"), reason="Tử Vi Hàm Số PDF not present")
def test_page_offset():
    # printed page N is PDF page N+1: the page header carries the printed number
    for n in (84, 140, 222):
        assert book_text.page_text("HS", n).split("\n")[2].strip() == str(n)


def test_own_dignity_table_is_a_partition():
    for star, t in DIG["stars"].items():
        seen = [b for lv in DIG["levels"] for b in t.get(lv, [])]
        doubled = {b for b in seen if seen.count(b) > 1}
        assert doubled == set(t.get("conflicts", {})), star
        assert set(BR) - set(seen) == set(t.get("missing", {})), star


STAGED, _ = load_pack(MENH_PATH)


def fired(name, branch, own, hoa=(), **chart):
    p = {"palace.name": name, "palace.branch": branch, "palace.own_major_stars": [s for s in own if s in MAJORS], "palace.own_stars": list(own),
         "palace.tu_hoa": list(hoa), "palace.tuan": False, "palace.triet": False, "palace.has_no_major": not any(s in MAJORS for s in own)}
    res = engine.run(RULES + STAGED, SOURCES, {"chart": {"chart.system": "tu_vi", **chart}, "palace:" + name: p}, system="tu_vi")
    return {f.rule_id for f in res.findings if f.rule_id.startswith("TV_HS_")}


MAJORS = {"Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh", "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn", "Thiên Tướng",
          "Thiên Lương", "Thất Sát", "Phá Quân"}


def test_every_rule_is_tied_to_its_palace():
    for r in PACK + MENH:
        first = r["conditions"]["all"][0]
        assert first["fact"] == "palace.name" and first["value"] in {"Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch", "Quan Lộc", "Nô Bộc", "Thiên Di",
                                                                     "Tật Ách", "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ"}, r["id"]


def test_book_conditions():
    # HS p.87: Cự Môn ở Di, 'nếu đắc địa' — in the book's own table (p.84) Mão is miếu, Tý vượng, Tỵ hãm
    assert "TV_HS_CU_MON_THIEN_DI_DI_DAC" in fired("Thiên Di", "Mão", ["Cự Môn", "Thiên Cơ"])
    assert "TV_HS_CU_MON_THIEN_DI_DI_DAC" in fired("Thiên Di", "Tý", ["Cự Môn"])
    assert "TV_HS_CU_MON_THIEN_DI_DI_DAC" not in fired("Thiên Di", "Tỵ", ["Cự Môn"])
    assert "TV_HS_CU_MON_THIEN_DI_DI_DAC" not in fired("Quan Lộc", "Mão", ["Cự Môn", "Thiên Cơ"])
    # HS p.88: Cự Môn ở Tài tại Dần
    assert "TV_HS_CU_MON_TAI_BACH_TAI_DAN" in fired("Tài Bạch", "Dần", ["Cự Môn", "Thái Dương"])
    assert "TV_HS_CU_MON_TAI_BACH_TAI_DAN" not in fired("Tài Bạch", "Thân", ["Cự Môn", "Thái Dương"])
    # Thiên Lương Tý is printed both vượng (p.124) and hãm (p.125): neither the đắc nor the hãm reading is told there
    told = fired("Mệnh", "Tý", ["Thiên Lương"])
    assert "TV_HS_THIEN_LUONG_MENH_NHANHAU" in told
    assert "TV_HS_THIEN_LUONG_MENH_DAC_THONGMINH" not in told and "TV_HS_THIEN_LUONG_MENH_HAM_KEMTM" not in told
    assert "TV_HS_THIEN_LUONG_MENH_DAC_THONGMINH" in fired("Mệnh", "Ngọ", ["Thiên Lương"])
    assert "TV_HS_THIEN_LUONG_MENH_HAM_KEMTM" in fired("Mệnh", "Hợi", ["Thiên Lương"])
