import pytest

from bazi_deep_util import EX, view
from tvbt.bazi_deep import position, season
from tvbt.bazi_deep.model import ChartView
from tvbt.bazi_deep.profile import DEFAULT
from tvbt.ganzhi import BRANCHES_VI


def test_example_charts_are_valid_ganzhi_and_follow_five_tigers_five_rats():
    from tvbt.ganzhi import tiger_month_stem
    for k, t in EX.items():
        v = ChartView.from_names(t)                    # raises on stem/branch parity
        assert v.stems[1] == (tiger_month_stem(v.stems[0]) + (v.branches[1] - 2) % 12) % 10, k
        assert v.stems[3] == (v.stems[2] % 5 * 2 + v.branches[3]) % 10, k


def test_season_states_generic_rule_matches_the_textbook_table():
    st = season.season_states(BRANCHES_VI.index("Dần"))
    assert st == {"Mộc": "vượng", "Hỏa": "tướng", "Thủy": "hưu", "Kim": "tù", "Thổ": "tử"}
    assert season.season_states(BRANCHES_VI.index("Ngọ")) == {"Hỏa": "vượng", "Thổ": "tướng", "Mộc": "hưu", "Thủy": "tù", "Kim": "tử"}
    assert season.season_states(BRANCHES_VI.index("Dậu")) == {"Kim": "vượng", "Thủy": "tướng", "Thổ": "hưu", "Hỏa": "tù", "Mộc": "tử"}
    assert season.season_states(BRANCHES_VI.index("Tý")) == {"Thủy": "vượng", "Mộc": "tướng", "Kim": "hưu", "Thổ": "tù", "Hỏa": "tử"}
    # tứ quý: Thổ vượng, Kim tướng, Hỏa hưu, Mộc tù, Thủy tử
    for b in ("Thìn", "Tuất", "Sửu", "Mùi"):
        assert season.season_states(BRANCHES_VI.index(b)) == {"Thổ": "vượng", "Kim": "tướng", "Hỏa": "hưu", "Mộc": "tù", "Thủy": "tử"}


def test_every_branch_has_exactly_one_of_each_state():
    for b in range(12):
        assert sorted(season.season_states(b).values()) == sorted(["vượng", "tướng", "hưu", "tù", "tử"])


def test_tu_lenh_segments_and_unknown_days():
    p = DEFAULT
    assert season.command(view("EX1"), p) is None                       # days unknown -> no claim
    assert season.command(view("EX1", 3.0), p)["name"] == "Mậu"          # Dần: Mậu 7, Bính 7, Giáp 16
    assert season.command(view("EX1", 10.0), p)["name"] == "Bính"
    assert season.command(view("EX1", 20.0), p)["name"] == "Giáp"
    assert season.command(view("EX1", 99.0), p)["name"] == "Giáp"        # clamps to the last segment
    assert season.command(view("EX1", 6.5), p)["near_boundary"] is True
    assert season.command(view("EX1", 3.0), p.with_(use_tu_lenh=False)) is None


def test_tu_lenh_table_totals_30_days_and_flags_stems_outside_the_hidden_list():
    rows = DEFAULT.tu_lenh_rows()
    assert set(rows) == set(BRANCHES_VI)
    assert all(sum(d for _, d in r) == 30 for r in rows.values())
    c = season.command(view("EX1", 0.5), DEFAULT)     # Mậu in Dần IS a hidden stem
    assert c["in_hidden_stems"] is True
    c2 = season.command(ChartView.from_names("Giáp Tý / Đinh Mão / Giáp Tuất / Giáp Tý", 1.0), DEFAULT)   # Giáp is not in Mão's verified hidden list
    assert c2["name"] == "Giáp" and c2["in_hidden_stems"] is False


def test_roots_grade_by_class_stage_and_char():
    r = position.roots(view("EX1"), view("EX1").dm)
    top = max(r, key=lambda x: x["score"])
    assert (top["pillar"], top["class"], top["same_char"], top["stage"]) == ("month", "ban_khi", True, "Lâm Quan")
    assert position.root_grade(r) == "mạnh"
    assert position.root_grade(position.roots(view("EX4"), view("EX4").dm)) == "không"      # no Mộc hidden anywhere
    assert position.root_grade([]) == "không"


def test_unopened_kho_halves_root_and_opening_restores_it():
    # Nhâm DM: Thìn is its Mộ khố and hides Quý (same element, residual)
    v2 = ChartView.from_names("Nhâm Tý / Giáp Thìn / Nhâm Thìn / Canh Tý")
    closed = max(x["score"] for x in position.roots(v2, 8) if x["pillar"] == "day")
    opened = max(x["score"] for x in position.roots(v2, 8, opened={"day"}) if x["pillar"] == "day")
    assert opened == pytest.approx(closed * 2, abs=2e-3)
    assert max(x["score"] for x in position.roots(v2, 8, DEFAULT.with_(kho_policy="tu_co_can")) if x["pillar"] == "day") == pytest.approx(opened, abs=2e-3)


def test_roots_shrink_when_branch_is_taken_by_a_cuc():
    v = view("EX1")
    base = position.roots(v, v.dm)
    sh = position.roots(v, v.dm, shifts={"month.branch": ("Hỏa", 0.7)})
    b = next(x for x in base if x["pillar"] == "month"); s = next(x for x in sh if x["pillar"] == "month")
    assert s["score"] == pytest.approx(b["score"] * 0.3, abs=1e-3)


def test_tou_reports_same_char_and_adjacency():
    t2 = {x["stem"]: x for x in position.tou(view("EX2"))}
    assert t2["Ất"]["tou_same_char"] == ["month"] and t2["Ất"]["ten_god"] == "Chính Quan"
    t1 = {x["stem"]: x for x in position.tou(view("EX1"))}
    assert t1["Bính"]["tou_same_char"] == ["month"] and t1["Giáp"]["same_as_day_master"] is True
    assert t1["Mậu"]["tou_same_char"] == []


def test_climate_is_coarse_and_flagged():
    cl = season.climate(view("EX8"), {"Hỏa": 1.0, "Thủy": 5.0, "Mộc": 2.0, "Thổ": 0.5, "Kim": 0.5})
    assert cl["label"] in ("hàn", "cực hàn") and cl["moist"] is None and "thô" in cl["note"]
