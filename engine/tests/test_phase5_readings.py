"""Phase 5: structure and honesty checks for the first-hand source readings (no definition changed, no status raised)."""
import json
import re
from pathlib import Path

from tvbt import tuvi
from tvbt.knowledge.loader import load_experimental
from tvbt.ganzhi import STEMS_VI

DATA = Path(__file__).resolve().parent.parent / "data" / "experimental"
D = json.loads((DATA / "source_readings_phase5.json").read_text("utf-8"))
R = D["readings"]
CLASSES = {"classic_web", "translation_commentary", "vn_treatise"}                      # `registry` is deliberately not a reading class
RELATIONS = {"khop", "long_hon", "chat_hon", "khac", "lien_quan"}


def test_readings_have_the_required_fields_and_valid_vocabulary():
    assert len({x["id"] for x in R}) == len(R) >= 27
    for x in R:
        assert x["source_class"] in CLASSES and x["relation_to_draft_v2"] in RELATIONS and x["topic"] in {"MDDK", "TTAN", "TUHOA"}
        assert x["page"] and x["method"] and x["paraphrase_vi"] and x["work"]


def test_quote_policy_chinese_only_from_the_classic_and_no_long_reproduction_of_modern_books():
    for x in R:
        if "zh" in x:
            assert x["source_class"] == "classic_web" and re.search(r"[一-鿿]", x["zh"])
        else:
            assert not re.search(r"[一-鿿]", x["paraphrase_vi"]) or x["source_class"] == "classic_web"
        if x["source_class"] != "classic_web":
            assert len(x["paraphrase_vi"]) <= 330, x["id"]            # a close paraphrase with a page number, not a reproduced passage


def test_every_book_reading_names_how_it_was_read_and_classic_is_flagged_single_web_copy():
    for x in R:
        if x["source_class"] == "classic_web":
            assert "WebFetch" in x["method"]
        else:
            assert "PDF" in x["method"]
    assert any("image" in x["method"] for x in R if x["id"] in ("T07", "H01"))      # the two pages whose text layer was garbled were read as images


def test_both_formations_have_documented_source_conflicts_and_stay_draft():
    ids = {c["id"] for c in D["conflicts"]}
    assert {"P5_MDDK_DEF", "P5_TTAN_DEF", "P5_TUHOA_NHAM"} <= ids
    _, forms, _ = load_experimental()
    for f in forms:
        assert f.reviewStatus == "draft" and f.experimental and f.definition_version == 2           # nothing edited, nothing promoted
    by = {x["id"]: x for x in R}
    assert by["T03"]["relation_to_draft_v2"] == "khac" and by["T07"]["relation_to_draft_v2"] == "khac"   # Tuần/Triệt: books use it as a condition FOR the cách
    assert by["M08"]["relation_to_draft_v2"] == "khac" and by["M06"]["relation_to_draft_v2"] == "khac"   # Thiên Mã appears in the books, not in the draft


def test_draft_refutation_tuan_triet_is_opposed_by_two_pages_and_cu_mon_ham_never_fires_per_tt_p34():
    _, forms, _ = load_experimental()
    ttan = next(f for f in forms if f.id == "CACH_X_THACH_TRUNG_AN_NGOC")
    assert "tuan_triet_an_ngu" in {e.id for e in ttan.refutations}                      # still in the draft (we do not edit to fit a source)
    from tvbt.dignity import dignity
    assert {dignity("Cự Môn", b) for b in ("Tý", "Ngọ")} == {"vượng"} or {dignity("Cự Môn", b) for b in ("Tý", "Ngọ")} <= {"vượng", "bình"}


def test_characterisation_of_the_tu_hoa_table_in_code_vs_the_books_read():
    t = tuvi.TU_HOA
    assert t[STEMS_VI.index("Canh")] == ("Thái Dương", "Vũ Khúc", "Thiên Đồng", "Thái Âm")      # KL p.196 and TH p.21 agree
    assert t[STEMS_VI.index("Nhâm")][2] == "Tả Phụ"                                           # KL p.197; TH p.21 prints Thiên Phủ -> conflict recorded
    nham = next(x for x in R if x["id"] == "H01")
    assert "THIÊN PHỦ" in nham["paraphrase_vi"] and nham["relation_to_draft_v2"] == "khac"


def test_no_production_code_reads_the_phase5_readings():
    root = Path(__file__).resolve().parent.parent / "tvbt"
    assert not [p for p in root.rglob("*.py") if "source_readings_phase5" in p.read_text("utf-8")]
