"""pack_khao_luan_sao_cung.json (tools/build_kl_sao_cung_pack.py, KL pp.84-117 'X ở các cung'): every rule has a quote that is on its page of the
PDF (skipped when the book is absent), and the rules fire on the book's conditions and not elsewhere."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import book_text  # noqa: E402

from tvbt.knowledge.loader import load_all  # noqa: E402
from tvbt.reasoning import engine  # noqa: E402

PACK = json.loads((ROOT / "engine" / "data" / "pack_khao_luan_sao_cung.json").read_text("utf-8"))["rules"]
QUOTES = json.loads((ROOT / "engine" / "data" / "pack_khao_luan_sao_cung.quotes.json").read_text("utf-8"))["quotes"]
RULES, SOURCES = load_all()


def test_every_rule_has_a_quote_and_a_page_cite():
    q = {x["rule"] for x in QUOTES}
    assert {r["id"] for r in PACK} == q
    for r in PACK:
        page = next(x["page"] for x in QUOTES if x["rule"] == r["id"])
        assert f"[KL p.{page}]" in r["description"], r["id"]


@pytest.mark.skipif(not book_text.available("KL"), reason="Tử Vi Khảo Luận PDF not present")
def test_quotes_are_on_their_page():
    bad = [x for x in QUOTES if not book_text.quote_on_page("KL", x["page"], x["quote"])]
    assert not bad, bad


def fired(name, branch, own):
    p = {"palace.name": name, "palace.branch": branch, "palace.own_major_stars": list(own), "palace.own_stars": list(own), "palace.tuan": False, "palace.triet": False}
    res = engine.run(RULES, SOURCES, {"chart": {"chart.system": "tu_vi"}, "palace:" + name: p}, system="tu_vi")
    return {f.rule_id for f in res.findings}


def test_book_conditions():
    assert "TV_KL_SAO_CUNG_QUAN_LOC_VU_PHU" in fired("Quan Lộc", "Ngọ", ["Vũ Khúc", "Thiên Phủ"])
    assert "TV_KL_SAO_CUNG_QUAN_LOC_VU_PHU" not in fired("Tài Bạch", "Ngọ", ["Vũ Khúc", "Thiên Phủ"])
    assert "TV_KL_SAO_CUNG_TAI_BACH_CU_DAN" in fired("Tài Bạch", "Dần", ["Cự Môn", "Thái Dương"])
    assert "TV_KL_SAO_CUNG_TAI_BACH_CU_DAN" not in fired("Tài Bạch", "Thân", ["Cự Môn", "Thái Dương"])
    assert "TV_KL_SAO_CUNG_DIEN_TRACH_PHA" in fired("Điền Trạch", "Dần", ["Phá Quân", "Vũ Khúc"])
    assert "TV_KL_SAO_CUNG_DIEN_TRACH_PHA" not in fired("Điền Trạch", "Thìn", ["Phá Quân"])
    assert "TV_KL_SAO_CUNG_QUAN_LOC_NHAT_NGUYET_SUU_MUI" in fired("Quan Lộc", "Sửu", ["Thái Dương", "Thái Âm"])
