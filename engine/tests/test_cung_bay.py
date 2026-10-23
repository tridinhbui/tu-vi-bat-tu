"""pack_cung_bay.json (tools/build_cung_bay_pack.py, the seven thin palaces from KL pp.55-220 and TH pp.99-113, plan 2026-10-23 P1): every rule
has a quote that is on its page of the PDF (skipped when the book is absent), every quote comes from the raw mined entry it names
(engine/data/kg/mined), the skipped entries say why, and the rules fire on the book's conditions and not elsewhere."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import book_text  # noqa: E402

from tvbt.knowledge.loader import load_all  # noqa: E402
from tvbt.reasoning import engine  # noqa: E402

PACK = json.loads((ROOT / "engine" / "data" / "pack_cung_bay.json").read_text("utf-8"))["rules"]
Q = json.loads((ROOT / "engine" / "data" / "quotes_cung_bay.json").read_text("utf-8"))
QUOTES, SKIPPED = Q["quotes"], Q["skipped"]
MINED = {e["id"]: e for f in sorted((ROOT / "engine" / "data" / "kg" / "mined").glob("kl_*.json")) for e in json.loads(f.read_text("utf-8"))["entries"]}
RULES, SOURCES = load_all()


def test_every_rule_has_a_quote_from_its_mined_entry():
    assert {r["id"] for r in PACK} == {x["rule"] for x in QUOTES}
    for x in QUOTES:
        e = MINED[x["mined"]]
        assert (e["book"], e["page"], e["quote"]) == (x["book"], x["page"], x["quote"]), x["rule"]
        assert not e.get("skip"), x["rule"]
        r = next(r for r in PACK if r["id"] == x["rule"])
        assert f"[{x['book']} p.{x['page']}]" in r["description"], x["rule"]
    for k, why in SKIPPED.items():
        assert k in MINED and why, k


@pytest.mark.skipif(not (book_text.available("KL") and book_text.available("TH")), reason="Tử Vi Khảo Luận / Thực Hành PDF not present")
def test_quotes_are_on_their_page():
    bad = [x for x in QUOTES if not book_text.quote_on_page(x["book"], x["page"], x["quote"])]
    assert not bad, bad


def fired(name, branch, own, stars=(), hoa=()):
    p = {"palace.name": name, "palace.branch": branch, "palace.own_major_stars": list(own), "palace.own_stars": list(own) + list(stars), "palace.tu_hoa": list(hoa),
         "palace.tuan": False, "palace.triet": False, "palace.has_no_major": not own}
    res = engine.run(RULES, SOURCES, {"chart": {"chart.system": "tu_vi"}, "palace:" + name: p}, system="tu_vi")
    return {f.rule_id for f in res.findings}


def test_book_conditions():
    assert "TV_KL7_NO_BOC_PHA_LIEM" in fired("Nô Bộc", "Mão", ["Phá Quân", "Liêm Trinh"])
    assert "TV_KL7_NO_BOC_PHA_LIEM" not in fired("Nô Bộc", "Mão", ["Phá Quân"])
    assert "TV_KL7_NO_BOC_LIEM_DOC" in fired("Nô Bộc", "Dần", ["Liêm Trinh"])
    assert "TV_KL7_NO_BOC_LIEM_DOC" not in fired("Nô Bộc", "Tuất", ["Liêm Trinh", "Thiên Phủ"])
    assert "TV_KL7_THIEN_DI_PHA_TY_NGO" in fired("Thiên Di", "Tý", ["Phá Quân"])
    assert "TV_KL7_THIEN_DI_PHA_TY_NGO" not in fired("Thiên Di", "Thìn", ["Phá Quân"])
    assert "TV_KL7_PHUC_DUC_PHA" in fired("Phúc Đức", "Thìn", ["Phá Quân"]) and "TV_KL7_PHUC_DUC_PHA" not in fired("Phúc Đức", "Ngọ", ["Phá Quân"])
    assert "TV_KL7_TU_TUC_SAT" in fired("Tử Tức", "Tý", ["Thất Sát"]) and "TV_KL7_TU_TUC_SAT" not in fired("Tử Tức", "Dần", ["Thất Sát"])
    # a group of stars ('lũ Riêu Đà Kỵ') needs two of them
    assert "TV_KL7_THIEN_DI_RIEU_DA_KY_KK" not in fired("Thiên Di", "Tý", ["Cự Môn"], stars=["Đà La"])
    assert "TV_KL7_THIEN_DI_RIEU_DA_KY_KK" in fired("Thiên Di", "Tý", ["Cự Môn"], stars=["Đà La"], hoa=["Hóa Kỵ"])
    assert "TV_KL7_TAT_ACH_TOI_KY" in fired("Tật Ách", "Tý", ["Tham Lang"])
    assert "TV_KL7_NO_BOC_HOA_KY" in fired("Nô Bộc", "Tý", ["Cự Môn"], hoa=["Hóa Kỵ"])
