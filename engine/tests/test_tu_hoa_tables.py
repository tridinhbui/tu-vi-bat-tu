"""Phase 7: Tứ Hóa tables per source. Production keeps the Khảo Luận table; Thực Hành and a digitized 全書 differ on Nhâm-Khoa (and the 全書 also on Canh). Nothing is switched."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oracle_tuvi_independent as O  # noqa: E402
from tvbt import tuvi  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
T = json.loads((ROOT / "engine/data/experimental/tu_hoa_tables.json").read_text("utf-8"))
SENS = json.loads((ROOT / "engine/tests/fixtures/tu_hoa_sensitivity.json").read_text("utf-8"))
STEMS = T["stems"]


def test_default_table_in_production_equals_the_khao_luan_table_and_nothing_was_switched():
    for i, st in enumerate(STEMS):
        assert tuple(T["tables"]["KL"][st].values()) == tuvi.TU_HOA[i], st
        assert tuple(T["tables"]["KL"][st].values()) == O.TU_HOA_TABLES["KL"][i]
    assert T["sources"]["KL"]["default_in_production"] and not T["sources"]["TH"]["default_in_production"] and not T["sources"]["TT_WS"]["default_in_production"]


def test_the_disagreement_is_exactly_nham_khoa_and_for_the_external_text_canh():
    assert T["differs_from_KL"]["TH"] == {"Nhâm": {"Hóa Khoa": ["Tả Phụ", "Thiên Phủ"]}}
    assert T["differs_from_KL"]["TT_WS"] == {"Canh": {"Hóa Khoa": ["Thiên Đồng", "Thái Âm"], "Hóa Kỵ": ["Thái Âm", "Thiên Đồng"]}, "Nhâm": {"Hóa Khoa": ["Tả Phụ", "Thiên Phủ"]}}
    # KL and TH agree on Canh (both: Khoa Thiên Đồng, Kỵ Thái Âm)
    assert T["tables"]["KL"]["Canh"] == T["tables"]["TH"]["Canh"]


def test_the_production_note_no_longer_claims_agreement_on_all_ten_stems():
    note = tuvi.SCHOOL_PACK["rule_review"]["tu_hoa"][1]
    assert "agree on all ten" not in note and "DISAGREE on Nhâm-Khoa" in note and "nine of the ten" in note


def test_sensitivity_of_the_variants_to_the_table():
    """Canh: the swap of Khoa/Kỵ between Thiên Đồng and Thái Âm changes no variant state (both stars sit in the Cơ Nguyệt Đồng Lương tam phương together).
    Nhâm: Khoa on Thiên Phủ instead of Tả Phụ changes only two variants, in a minority of Nhâm-year charts."""
    assert SENS["Canh|TH"]["differ"] == SENS["Canh|TT_WS"]["differ"] == {}
    assert SENS["Nham|TH".replace("Nham", "Nhâm")]["differ"] == SENS["Nhâm|TT_WS"]["differ"] == {"NHAT_LE_TRUNG_THIEN@kl_52_85": 32, "SAT_PHA_LIEM_THAM@th_76_77": 408}
    assert SENS["Nhâm|TH"]["charts"] == 16704


def test_the_oracle_follows_the_chosen_table_only_when_asked():
    a, b = O.chart(2022, 5, 10, 3, True), O.chart(2022, 5, 10, 3, True, "TH")
    assert a["carriers"]["Hóa Khoa"] == "Tả Phụ" and b["carriers"]["Hóa Khoa"] == "Thiên Phủ" and a["pos"] == b["pos"]


def test_khao_luan_table_line_exists_in_the_pdf_text_layer():
    pytest.importorskip("fitz")
    sys.path.insert(0, str(ROOT / "tools"))
    import book_text as bt
    if not bt.available("KL"):
        pytest.skip("books not on this machine")
    assert bt.quote_on_page("KL", 36, "Nhâm Lương Vi Phụ Vũ") and bt.quote_on_page("KL", 36, "Canh Nhật Vũ Đồng Âm")
