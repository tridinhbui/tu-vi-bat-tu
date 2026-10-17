import json

from bazi_deep_util import EX, view
from tvbt.bazi_deep import dieuhau, geju, interact, strength, yongshen
from tvbt.bazi_deep.profile import DEFAULT
from tvbt.ganzhi import BRANCHES_HAN, STEMS_HAN


def test_table_has_120_cells_of_valid_distinct_stems_and_is_flagged_unchecked():
    d = json.loads((dieuhau.DATA / "dieu_hau_ctbg_draft.json").read_text("utf-8"))
    assert d["_status"].startswith("draft") and d["checked_cells"] == []
    assert set(d["cells"]) == set(STEMS_HAN)
    for s, row in d["cells"].items():
        assert set(row) == set(BRANCHES_HAN)
        for cell in row.values():
            assert 1 <= len(cell) <= 4 and len(set(cell)) == len(cell) and all(c in STEMS_HAN for c in cell), (s, cell)


def test_lookup_orders_stems_and_reports_presence():
    r = dieuhau.lookup(view("EX1"))                       # Giáp sinh tháng Dần
    assert [x["stem"] for x in r["yong_stems"]] == ["Bính", "Quý"] and r["yong_stems"][0]["rank"] == "chính"
    assert r["yong_stems"][0]["visible"] is True and r["yong_stems"][1]["hidden"] is True       # Bính on the stems; Quý hidden in Tý
    assert r["satisfied"] is True and r["status"] == "draft_tu_tri_nho" and r["checked"] is False
    e8 = dieuhau.lookup(view("EX8"))                      # Bính sinh tháng Tý
    assert e8["yong_stems"][0]["stem"] == "Nhâm" and e8["satisfied"] is False


def test_method_gives_ten_god_roles_from_the_table_and_keeps_coarse_climate_aside():
    v = view("EX1"); R = interact.resolve(v); S = strength.compute(v, DEFAULT, R)
    m = yongshen.dieu_hau(v, S)
    assert m["status"] == "bang_CTBG_draft" and m["yong"] == ["ThucThuong"] and m["xi"] == ["An"]
    assert "climate" in m and "draft" in m["note"] and "窮通寶鑑" in m["note"]


def test_method_stays_separate_from_phu_uc_and_cach_cuc_in_comparison():
    v = view("EX3"); R = interact.resolve(v); S = strength.compute(v, DEFAULT, R); G = geju.analyse(v, DEFAULT, R, S)
    Y = yongshen.run(v, DEFAULT, R, S, G)
    assert Y["methods"]["dieu_hau"]["yong"] != [] and Y["methods"]["phu_uc"]["method"] == "phu_uc"
    rows = {r["group"]: r["roles"] for r in Y["comparison"]["rows"]}
    assert any("dieu_hau" in roles for roles in rows.values())


def test_every_example_gets_a_lookup():
    for k in EX:
        r = dieuhau.lookup(view(k))
        assert r["yong_stems"] and r["yong_stems"][0]["group"] in ("Ti", "An", "Tai", "QuanSat", "ThucThuong")
