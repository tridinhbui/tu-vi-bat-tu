import json
from pathlib import Path

import pytest

from tvbt.bazi_deep import strength, tvh_score
from tvbt.bazi_deep.model import ChartView
from tvbt.bazi_deep.profile import DEFAULT, TVH_40

EX = json.loads((Path(__file__).parent / "golden/tvh_examples.json").read_text("utf-8"))["examples"]


def sc(text, days=None):
    return tvh_score.score(ChartView.from_names(text, days_into_month=days))


@pytest.mark.parametrize("name", sorted(EX))
def test_matches_the_books_worked_example_components(name):
    e = EX[name]
    r = sc(e["pillars"])
    assert r["stem_deg"] == e["stem_deg"]
    assert {k: v for k, v in r["heaven"].items() if v} == e["heaven"]
    if "earth" in e:
        assert {k: v for k, v in r["earth"].items() if v} == e["earth"]
    assert r["dm_strong"] is e["strong"]


def test_hidden_degree_table_matches_page_342_and_sums_to_30():
    for b, items in tvh_score.HID_DEG.items():
        assert sum(g for _, g in items) == 30
    assert tvh_score.HID_DEG[6] == [(3, 21), (5, 9)] and tvh_score.HID_DEG[11] == [(8, 21), (0, 9)]   # Ngọ: Đinh 21 Kỷ 9; Hợi: Nhâm 21 Giáp 9
    from tvbt.bazi import HIDDEN_STEMS
    for b in range(12):                                   # same hidden stems as the verified table of 八字真宗 used elsewhere
        assert {s for s, _ in tvh_score.HID_DEG[b]} == set(HIDDEN_STEMS[b])


def test_root_test_hu_phu_is_9_and_rooted_is_36():
    r = sc("Tân Mão / Canh Dần / Giáp Thìn / Ất Hợi")
    assert r["notes"]["steps"][0]["root"] == [False, False, True, True]
    assert r["notes"]["steps"][0]["deg"] == [9, 9, 36, 36]


def test_ngu_hop_not_hoa_makes_the_controlled_stem_24_and_both_hu_phu_stay_9():
    r = sc("Nhâm Thân / Đinh Mùi / Bính Thân / Tân Mão")
    assert r["hua_stem"] == {}                              # Đinh–Nhâm and Bính–Tân do not transform here (book example 6)
    assert r["stem_deg"][0] == 36 and r["stem_deg"][3] == 12


def test_tranh_hop_reduces_all_three_stems_to_24_before_other_effects():
    r = sc("Ất Dậu / Canh Thìn / Ất Dậu / Mậu Ngọ")        # Canh between two Ất
    steps = {s["step"]: s for s in r["notes"]["steps"]}
    assert "tranh hợp" in steps and steps["ngũ hợp"]["deg"][:3] == [24.0, 24.0, 24.0]


def test_xung_loss_table_follows_the_month_group():
    # month Dần: the branches opposite to its group (Thân, Dậu) lose 1/2, others 1/3; tứ khố clashes lose no bản khí
    r1 = sc("Giáp Thân / Bính Dần / Mậu Thân / Canh Thân")
    assert r1["xung"] and r1["khu_bi"]
    r2 = sc("Mậu Thìn / Bính Thìn / Mậu Tuất / Canh Tuất")
    assert r2["earth"]["Thổ"] > 0                           # Thìn–Tuất xung keeps its bản khí


def test_lenh_adjustment_is_plus_minus_one_fifth():
    r = sc("Ất Tỵ / Ất Dậu / Kỷ Mùi / Nhâm Thân")            # book example 1: Kim nắm lệnh
    assert r["lenh"] == "Kim"
    assert r["totals"]["Kim"] == pytest.approx(r["totals_before_lenh"]["Kim"] * 1.2, abs=0.01)
    assert r["totals"]["Mộc"] == pytest.approx(r["totals_before_lenh"]["Mộc"] * 0.8, abs=0.01)


def test_forty_percent_rule_and_border():
    r = sc("Ất Tỵ / Ất Dậu / Kỷ Mùi / Nhâm Thân")
    assert r["threshold"] == 0.40 and (r["own_share"] >= 0.40) == r["dm_strong"]
    hy = strength.compute_hybrid(ChartView.from_names("Ất Tỵ / Ất Dậu / Kỷ Mùi / Nhâm Thân"), TVH_40)
    assert hy["ambiguous"] is (abs(hy["ratio"] - 0.40) < TVH_40.tvh_margin) and hy["method"].startswith("tvh_40")


def test_tu_quy_month_without_days_assumes_tho_lenh_and_says_so():
    r = sc("Mậu Tuất / Kỷ Mùi / Giáp Tuất / Mậu Thìn")
    assert r["lenh"] == "Thổ" and any("Thổ nắm lệnh" in a for a in r["notes"]["assumptions"])
    assert sc("Mậu Tuất / Kỷ Mùi / Giáp Tuất / Mậu Thìn", days=2.0)["lenh"] == "Hỏa"     # first 12 days of Mùi still belong to the season element


def test_unsupported_cases_are_reported_not_hidden():
    r = sc("Ất Mão / Canh Thìn / Đinh Mão / Nhâm Dần")
    assert any("phu tòng thê hóa" in u for u in r["notes"]["unsupported"])


def test_hybrid_changes_only_the_decision_not_the_group_shares():
    v = ChartView.from_names("Giáp Tý / Bính Dần / Giáp Tuất / Canh Ngọ")
    a, b = strength.compute(v, DEFAULT), strength.compute_hybrid(v, TVH_40)
    assert a["shares"] == b["shares"] and a["by_element"] == b["by_element"]
    assert b["ratio_system"] == a["ratio"] and "tvh" in b


def test_deterministic():
    t = "Quý Hợi / Kỷ Mùi / Canh Tý / Kỷ Mão"
    assert sc(t) == sc(t)
