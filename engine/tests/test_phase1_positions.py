"""Phase 1: role-typed positional facts, dignity_rank, and that the LEGACY facts are unchanged."""
import pytest

from phase1_helpers import base_facts, synth
from tvbt import tuvi
from tvbt.calendar_core import BirthInput, normalize
from tvbt.reasoning import facts, positions

M = "palace:Mệnh"


def test_roles_geometry_for_menh_at_ty():
    f = base_facts([("star", "Tử Vi", "Mệnh"), ("star", "Thiên Phủ", "Thiên Di"), ("star", "Vũ Khúc", "Quan Lộc"),
                    ("star", "Thiên Tướng", "Tài Bạch"), ("star", "Thiên Khôi", "Huynh Đệ"), ("star", "Thiên Việt", "Phụ Mẫu")])[M]
    assert f["palace.index"] == 0 and f["palace.branch"] == "Tý"
    names = f["palace.rel_names"]
    assert names == {"self": "Mệnh", "opp": "Thiên Di", "trine1": "Quan Lộc", "trine2": "Tài Bạch",
                     "flank_prev": "Huynh Đệ", "flank_next": "Phụ Mẫu", "nhi_hop": names["nhi_hop"]}
    assert f["palace.rel.self_majors"] == ["Tử Vi"]
    assert f["palace.rel.opp_majors"] == ["Thiên Phủ"]
    assert f["palace.rel.trine1_majors"] == ["Vũ Khúc"] and f["palace.rel.trine2_majors"] == ["Thiên Tướng"]
    assert sorted(f["palace.rel.trine_majors"]) == ["Thiên Tướng", "Vũ Khúc"]
    assert f["palace.rel.flank_prev_stars"] == ["Thiên Khôi"] and f["palace.rel.flank_next_stars"] == ["Thiên Việt"]
    assert sorted(f["palace.rel.tp_majors"]) == sorted(["Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"])
    assert set(f["palace.rel.tp_names"]) == {"Mệnh", "Thiên Di", "Quan Lộc", "Tài Bạch"}


def test_roles_are_distinct_unlike_the_legacy_merged_fact():
    f = base_facts([("star", "Thái Dương", "Thiên Di")])[M]
    assert "Thái Dương" in f["palace.tam_phuong_majors"]                     # legacy: cannot tell where
    assert f["palace.rel.opp_majors"] == ["Thái Dương"]                      # new: it is xung chiếu
    assert f["palace.rel.self_majors"] == [] and f["palace.rel.trine_majors"] == []


def test_nhi_hop_pairs_branches_summing_to_one_mod_12():
    for menh in ("Tý", "Dần", "Ngọ", "Hợi"):
        f = base_facts([], menh)[M]
        b = f["palace.index"]
        assert f["palace.rel_names"]["nhi_hop"] != "Mệnh" or b in (1, 7)     # b=1 or 7 pairs with itself ((1-b) % 12 == b? no: only b=7 -> 6)
    assert positions.branch_of("nhi_hop", 0) == 1 and positions.branch_of("nhi_hop", 5) == 8 and positions.branch_of("nhi_hop", 1) == 0


def test_hoa_and_tuan_triet_by_role():
    f = base_facts([("hoa", "Hóa Kỵ", "Thiên Di"), ("hoa", "Hóa Lộc", "Quan Lộc"), ("hoa", "Hóa Khoa", "Mệnh"),
                    ("triet", "Thiên Di"), ("tuan", "Mệnh")])[M]
    assert f["palace.rel.opp_hoa"] == ["Hóa Kỵ"] and f["palace.rel.trine_hoa"] == ["Hóa Lộc"] and f["palace.rel.self_hoa"] == ["Hóa Khoa"]
    assert f["palace.rel.tp_hoa"] == ["Hóa Lộc", "Hóa Khoa", "Hóa Kỵ"]
    assert f["palace.rel.opp_triet"] is True and f["palace.rel.opp_tuan"] is False and f["palace.tuan"] is True


@pytest.mark.parametrize("level,rank", [("miếu", 4), ("vượng", 3), ("đắc", 2), ("bình", 1), ("hãm", 0)])
def test_dignity_rank_ordinal(level, rank):
    f = base_facts([("star", "Thái Dương", "Quan Lộc"), ("dig", "Thái Dương", "Quan Lộc", level)])
    assert f["palace:Quan Lộc"]["palace.dignity_rank.Thái Dương"] == rank
    assert f[M]["palace.tp_rank.Thái Dương"] == rank                          # a tam-hợp star's rank is visible from Mệnh
    assert "palace.dignity_rank.Thái Dương" not in f[M]                        # ...but it is not Mệnh's OWN star


def test_unspecified_dignity_has_no_rank_never_a_guess():
    f = base_facts([("star", "Vũ Khúc", "Mệnh")])[M]                           # no dig op: the book gave no level
    assert "palace.dignity_rank.Vũ Khúc" not in f and "palace.tp_rank.Vũ Khúc" not in f


def test_cat_sat_counts():
    f = base_facts([("star", "Kình Dương", "Mệnh"), ("star", "Địa Kiếp", "Mệnh"), ("star", "Tả Phụ", "Thiên Di"),
                    ("star", "Hỏa Tinh", "Huynh Đệ")])[M]
    assert (f["palace.khi.sat_self"], f["palace.khi.cat_self"]) == (2, 0)
    assert (f["palace.khi.sat_tp"], f["palace.khi.cat_tp"], f["palace.khi.sat_flank"]) == (2, 1, 1)


# ---- regression: the legacy facts are exactly what they were --------------------------------------------------------------
@pytest.mark.parametrize("b", [(1990, 5, 17, 10, 30, "male"), (1975, 11, 3, 23, 5, "female"), (2001, 8, 28, 14, 0, "male")])
def test_legacy_facts_unchanged_on_real_charts(b):
    c = tuvi.compute(normalize(BirthInput(*b[:5], "Asia/Ho_Chi_Minh", b[5])))
    out = facts.tuvi_facts(c)
    by_branch = {p["branch_index"]: p for p in c.palaces}
    for p in c.palaces:
        br = p["branch_index"]
        tp = [br, (br + 4) % 12, (br + 8) % 12, (br + 6) % 12]
        f = out[f"palace:{p['name']}"]
        assert f["palace.tam_phuong_majors"] == [m for t in tp for m in by_branch[t]["major_stars"]]
        assert f["palace.tam_phuong_stars"] == [m for t in tp for m in by_branch[t]["stars"]]
        assert f["palace.neighbor_majors"] == [m for t in ((br - 1) % 12, (br + 1) % 12) for m in by_branch[t]["major_stars"]]
        assert f["palace.own_stars"] == p["stars"] and f["palace.tuan"] == p["tuan"]
        # new facts agree with the legacy ones where they overlap
        assert sorted(f["palace.rel.tp_stars"]) == sorted(f["palace.tam_phuong_stars"])
        assert sorted(f["palace.rel.flank_stars"]) == sorted(f["palace.neighbor_stars"])
        assert f["palace.rel.tp_hoa"] == f["palace.tam_phuong_tu_hoa"] or sorted(f["palace.rel.tp_hoa"]) == sorted(f["palace.tam_phuong_tu_hoa"])
