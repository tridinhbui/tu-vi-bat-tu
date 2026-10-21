"""All 14 chính tinh in all 12 branches under each selectable dignity table: the chart's major_dignity is exactly the table's VERIFIED cell
(blank otherwise), so the board and the rules read one explicitly selected system and never a mix."""
import pytest

from tvbt import dignity
from tvbt.ganzhi import BRANCHES_VI

MAJORS = ["Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh", "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn", "Thiên Tướng",
          "Thiên Lương", "Thất Sát", "Phá Quân"]


@pytest.mark.parametrize("school", ["thuc_hanh", "khao_luan", "toan_thu"])
def test_every_cell_comes_from_the_selected_school(school):
    for s in MAJORS:
        for b in BRANCHES_VI:
            r = dignity.classify(s, b, school)
            assert r["school"] == school or r["status"] != "VERIFIED"
            assert dignity.dignity(s, b, school) == (r["value"] if r["status"] == "VERIFIED" else None)


def test_thuc_hanh_is_the_default_and_khao_luan_matches_the_reference_board():
    from tvbt.api import BirthReq, _compute
    _, _, th = _compute(BirthReq(year=2002, month=1, day=9, hour=4, minute=30, gender="male"))
    assert th.school["dignity_school"] == "thuc_hanh"
    _, _, kl = _compute(BirthReq(year=2002, month=1, day=9, hour=4, minute=30, gender="male", dignity_school="khao_luan"))
    got = {s: d for p in kl.palaces for s, d in p["major_dignity"].items()}
    assert got["Thái Dương"] == "miếu" and got["Thiên Phủ"] == "đắc" and got["Thiên Cơ"] == "vượng" and got["Thiên Đồng"] == "hãm"
