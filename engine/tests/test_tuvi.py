import itertools

import pytest

from tvbt import tuvi
from tvbt.calendar_core import BirthInput, normalize
from tvbt.ganzhi import BRANCHES_VI


def chart(y, m, d, h=12, g="male", cal="vn", **kw):
    return tuvi.compute(normalize(BirthInput(y, m, d, h, 0, "Asia/Ho_Chi_Minh", g, calendar=cal)), **kw)


def test_tuvi_position_known_values():
    # Thủy nhị cục: day 1 -> Sửu, day 2 -> Dần (classical table)
    assert tuvi.tuvi_position(1, 2)[0] == 1
    assert tuvi.tuvi_position(2, 2)[0] == 2
    # Mộc tam cục day 1 -> Thìn
    assert tuvi.tuvi_position(1, 3)[0] == 4
    # Hỏa lục cục day 1 -> Dậu (classical table)
    assert tuvi.tuvi_position(1, 6)[0] == 9


def test_mirror_and_all_majors_once():
    for day, cuc in itertools.product(range(1, 31), [2, 3, 4, 5, 6]):
        tv, _ = tuvi.tuvi_position(day, cuc)
        assert (tv + (4 - tv) % 12) % 12 == 4 % 12
    c = chart(1990, 5, 17)
    majors = [s.name for s in c.stars if s.group.startswith("chính tinh")]
    assert sorted(majors) == sorted(tuvi.MAJOR_NAMES) and len(set(majors)) == 14


def test_menh_than_formula():
    # lunar month 1, hour Tý -> Mệnh and Thân both at Dần
    from tvbt.calendar_core import LunarDate
    # exercise via a real date: Tet 1990 (27 Jan), 00:30 -> hour Tý
    c = tuvi.compute(normalize(BirthInput(1990, 1, 27, 0, 30, "Asia/Ho_Chi_Minh", "male")))
    assert BRANCHES_VI[c.menh_branch] == "Dần" and BRANCHES_VI[c.than_branch] == "Dần"


def test_palace_order_opposites():
    c = chart(1990, 5, 17)
    byname = {p["name"]: p["branch_index"] for p in c.palaces}
    assert (byname["Thiên Di"] - byname["Mệnh"]) % 12 == 6
    assert (byname["Quan Lộc"] - byname["Mệnh"]) % 12 == 4
    assert (byname["Tài Bạch"] - byname["Mệnh"]) % 12 == 8
    assert (byname["Huynh Đệ"] - byname["Mệnh"]) % 12 == 11


def test_cuc_via_known_pair():
    # Giáp year: Dần palace = Bính Dần, so Tý palace = Bính Tý -> Giản Hạ Thủy -> Thủy nhị cục (hand-derived).
    # Mệnh at Tý needs lunar month 1 and hour Dần (2+0-2=0): Tet 1984, 04:00.
    c = tuvi.compute(normalize(BirthInput(1984, 2, 2, 4, 0, "Asia/Ho_Chi_Minh", "male")))
    assert BRANCHES_VI[c.menh_branch] == "Tý"
    assert c.palaces[0]["stem"] == "Bính"
    assert c.cuc["name"] == "Thủy nhị cục"


def test_tu_hoa_vn_table_giap_year():
    c = chart(1984, 6, 1)  # Giáp year
    assert c.tu_hoa["Hóa Lộc"]["star"] == "Liêm Trinh" and c.tu_hoa["Hóa Kỵ"]["star"] == "Thái Dương"


def test_direction_rule():
    assert chart(1984, 6, 1, g="male").dai_han_direction == "thuận"    # dương nam
    assert chart(1984, 6, 1, g="female").dai_han_direction == "nghịch"  # dương nữ
    assert chart(1985, 6, 1, g="female").dai_han_direction == "thuận"   # âm nữ


def test_dai_han_first_age_equals_cuc():
    c = chart(1990, 5, 17)
    assert c.dai_han[0]["age_from"] == c.cuc["n"] and c.dai_han[0]["palace"] == "Mệnh"
    assert c.dai_han[1]["age_from"] == c.cuc["n"] + 10


def test_leap_month_rules_differ_and_warn():
    # 2020-06-01 is leap 4th month, day 10 -> same month under split_15; next under next_month
    a = chart(2020, 6, 1, leap_rule="split_15")
    b = chart(2020, 6, 1, leap_rule="next_month")
    assert a.effective_lunar_month == 4 and b.effective_lunar_month == 5
    assert a.warnings


def test_tuan_pair_for_giap_ty_xun():
    c = chart(1984, 6, 1)  # Giáp Tý: xun begins Tý -> void Tuất, Hợi
    assert sorted(BRANCHES_VI[x] for x in c.tuan) == ["Hợi", "Tuất"]


def test_invariants_over_many_births():
    for y, m, d, h in itertools.product([1955, 1984, 2001], [1, 6, 11], [3, 18, 29], [0, 5, 13, 22]):
        c = chart(y, m, d, h)
        assert len({s.branch for s in c.stars if s.group == "vòng Lộc Tồn"}) == 12
        assert len({s.branch for s in c.stars if s.group == "vòng Thái Tuế"}) == 12
        assert len({s.branch for s in c.stars if s.group == "vòng Trường Sinh"}) == 12
        assert len(c.stars) == len({s.name for s in c.stars})


def test_determinism():
    a = chart(1990, 5, 17); b = chart(1990, 5, 17)
    assert [(s.name, s.branch) for s in a.stars] == [(s.name, s.branch) for s in b.stars]
