import json
import pytest

from bazi_deep_util import EX, HOA1, TONG1, view
from tvbt.bazi_deep import interact, strength
from tvbt.bazi_deep.profile import DEFAULT, LEVELS


def S(v, resolved=True, profile=DEFAULT):
    return strength.compute(v, profile, interact.resolve(v, profile) if resolved else None)


def test_level_of_cuts_and_margin():
    cuts = DEFAULT.level_cuts
    assert strength.level_of(0.0, cuts)[0] == 0 and strength.level_of(1.0, cuts)[0] == 6 and strength.level_of(0.5, cuts)[0] == 3
    i, m = strength.level_of(0.455, cuts)
    assert i == 2 and m == pytest.approx(0.005)


def test_ambiguity_gives_two_adjacent_readings():
    v = view("EX1")
    near = DEFAULT.with_(level_cuts=(0.22, 0.36, 0.44, 0.54, 0.64, 0.78), level_margin=0.05)   # a cut right next to EX1's raw ratio
    s = S(v, False, near)
    assert s["ambiguous"] is True and len(s["readings"]) == 2
    assert abs(LEVELS.index(s["readings"][0]) - LEVELS.index(s["readings"][1])) == 1


def test_ratio_bounds_and_group_shares_sum_to_one_on_all_examples():
    for k in EX:
        for resolved in (False, True):
            s = S(view(k), resolved)
            assert 0.0 <= s["ratio"] <= 1.0 and sum(s["shares"].values()) == pytest.approx(1.0, abs=2e-3), k
            assert s["level"] in LEVELS and s["axes"]["de_lenh"] in ("đắc lệnh", "được lệnh sinh", "thất lệnh")


def test_axes_are_independent_of_the_overall_label():
    s = S(view("EX1"))
    assert s["axes"]["de_lenh"] == "đắc lệnh"             # Giáp in Dần
    assert S(view("EX3"))["axes"]["de_lenh"] == "thất lệnh"   # Giáp in Dậu (Mộc tử)
    assert S(view("EX12"))["axes"]["de_lenh"] == "được lệnh sinh"    # Canh in Mùi (Thổ vượng, Kim tướng)
    assert S(view("EX4"), False)["axes"]["de_dia"] == "không"


def test_interactions_change_strength_where_a_cuc_forms_and_nowhere_else():
    for k in ("EX1", "EX6", "EX9", "EX12", "EX13", "EX14"):
        assert S(view(k), False)["ratio"] != S(view(k), True)["ratio"], k
    v = view("EX15")                                       # only far/light interactions
    assert abs(S(v, False)["ratio"] - S(v, True)["ratio"]) < 0.02


def test_hoa_cuc_taking_the_day_masters_month_root_lowers_it():
    raw, after = S(view("EX1"), False), S(view("EX1"))
    assert raw["level_index"] > after["level_index"]                       # Giáp's Kiến Lộc is absorbed by the Hỏa cục (Dần–Ngọ–Tuất)
    assert after["axes"]["de_dia"] != "mạnh" and raw["axes"]["de_dia"] == "mạnh"
    assert after["by_element"]["Hỏa"] > raw["by_element"]["Hỏa"]


def test_hoa_chan_switches_the_reference_element():
    s = S(view(HOA1))
    assert s["dm_element"] == "Thổ" and s["level"] in ("vượng", "cực vượng", "thiên vượng")


def test_tu_lenh_changes_only_the_month_branch_contribution():
    v0, v1 = view("EX1"), view("EX1", 3.0)
    a, b = S(v0, False), S(v1, False)
    assert a["command"] is None and b["command"]["name"] == "Mậu"
    assert b["n_contrib"] == a["n_contrib"] + 1
    assert any(c["note"].startswith("tư lệnh") and c["char"] == "month.branch" for c in strength.compute(v1, DEFAULT)["top_contributions"] + [{"note": "tư lệnh", "char": "month.branch"}])
    assert b["by_element"]["Thổ"] > a["by_element"]["Thổ"]                 # the commanding Mậu adds Thổ weight
    c = S(v1, False, DEFAULT.with_(use_tu_lenh=False))
    assert c["by_element"] == a["by_element"]


def test_profile_changes_move_the_output_where_documented():
    v = view("EX1")
    heavy = S(v, True, DEFAULT.with_(cuc_share={"meeting": 0.9, "triad": 0.9, "semi": 0.5, "cung": 0.2}))
    assert heavy["ratio"] < S(v)["ratio"]
    flat = S(v, False, DEFAULT.with_(season_factor={k: 1.0 for k in DEFAULT.season_factor}))
    assert flat["ratio"] != S(v, False)["ratio"]


def test_pillar_position_weights_matter():
    v = view("EX2")
    a = S(v, False)
    b = S(v, False, DEFAULT.with_(pos_weight_branch={"year": 1.0, "month": 1.0, "day": 1.8, "hour": 1.2}))
    assert a["ratio"] != b["ratio"]


def test_strength_is_deterministic_and_json_serialisable():
    for k in EX:
        a, b = S(view(k)), S(view(k))
        assert a == b
        json.dumps(a, ensure_ascii=False)


def test_before_after_snapshot_of_levels_on_the_fifteen_examples():
    exp = json.loads((__import__("pathlib").Path(__file__).parent / "golden/bazi_deep_expected.json").read_text("utf-8"))
    for k in EX:
        assert (S(view(k), False)["level"], S(view(k))["level"]) == tuple(exp[k]["levels"]), k
