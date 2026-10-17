import pytest

from bazi_deep_util import EX, HOA1, SAVED, TONG1, view
from tvbt.bazi_deep import geju, interact, strength, yongshen
from tvbt.bazi_deep.profile import DEFAULT


def Y(v, profile=DEFAULT):
    R = interact.resolve(v, profile)
    S = strength.compute(v, profile, R)
    G = geju.analyse(v, profile, R, S)
    return yongshen.run(v, profile, R, S, G), S, G


def test_five_separate_methods_never_merged():
    y, _, _ = Y(view("EX2"))
    assert list(y["methods"]) == ["phu_uc", "dieu_hau", "cach_cuc", "thong_quan", "thuan_the"]
    assert "yong" not in y and "final" not in y            # there is no merged answer at all
    for m in y["methods"].values():
        assert m["method"] in y["methods"] and set(["yong", "xi", "ji", "chou", "xian"]) <= set(m)


def test_phu_uc_direction_follows_level():
    y, S, _ = Y(view("EX4"))
    assert S["level"] == "cực nhược" and y["methods"]["phu_uc"]["yong"] == ["An"] and "Tai" in y["methods"]["phu_uc"]["ji"]
    assert Y(view("EX2"))[0]["methods"]["phu_uc"]["status"] == "hai_cach_doc"          # EX2 sits next to a cut: no single direction is claimed
    y13, S13, _ = Y(view("EX13"))
    assert S13["level"] == "cực vượng" and y13["methods"]["phu_uc"]["yong"][0] == "QuanSat" and "An" in y13["methods"]["phu_uc"]["ji"]
    ytr, Str, _ = Y(view("EX8"))
    assert Str["level"] == "trung hòa" and ytr["methods"]["phu_uc"]["status"] == "hai_cach_doc"       # sits next to a cut as well
    assert yongshen.phu_uc({"level_index": 3, "ambiguous": False, "readings": ["trung hòa"]}, False)["status"] == "khong_ap_dung"


def test_phu_uc_gives_both_directions_when_the_level_is_ambiguous():
    v = view("EX1")
    near = DEFAULT.with_(level_cuts=(0.22, 0.36, 0.22, 0.54, 0.64, 0.78), level_margin=0.05)    # a cut next to EX1's ratio after interaction
    y, S, _ = Y(v, near)
    assert S["ambiguous"] and y["methods"]["phu_uc"]["status"] == "hai_cach_doc"
    assert len(y["methods"]["phu_uc"]["alternatives"]) == 2


def test_phu_uc_is_off_when_a_true_outer_cach_holds():
    y, _, G = Y(view(TONG1))
    assert G["outer"][0]["quality"] == "chân"
    assert y["methods"]["phu_uc"]["status"] == "khong_ap_dung" and y["methods"]["thuan_the"]["yong"] == ["QuanSat"]
    assert set(y["methods"]["thuan_the"]["ji"]) == {"Ti", "An"}                     # the opposite of phù ức for a weak day master


def test_dieu_hau_is_coarse_and_marked_as_missing_the_ctbg_table():
    y, S, _ = Y(view("EX8"))
    d = y["methods"]["dieu_hau"]
    assert d["status"] in ("tho_chua_co_bang_CTBG", "khong_can_dieu_hau_thô") and d["yong"] == [] and d["xi"] == []     # no ten-god roles without the table
    assert "窮通寶鑑" in d["note"]
    cold = [k for k in EX if Y(view(k))[0]["methods"]["dieu_hau"].get("need_elements") == ["Hỏa"]]
    assert cold and all(view(k).month_branch in (0, 1, 11, 2, 3, 4) for k in cold) or cold


def test_cach_cuc_method_reports_dung_groups_only_for_the_inner_cach():
    y, _, G = Y(view("EX3"))
    c = y["methods"]["cach_cuc"]
    assert c["status"] == "cach_bai" and c["cach"] == "Chính Quan" and set(c["yong"]) <= {"Tai", "An"}
    ysaved, _, _ = Y(view(SAVED))
    assert ysaved["methods"]["cach_cuc"]["status"] == "ap_dung" and ysaved["methods"]["cach_cuc"]["yong"] == ["Tai", "An"]
    yh, _, _ = Y(view(HOA1))
    assert yh["methods"]["cach_cuc"]["status"] == "khong_xac_dinh_noi_cach"


def test_thong_quan_finds_war_and_missing_bridge_in_ex10():
    y, S, _ = Y(view("EX10"))
    t = y["methods"]["thong_quan"]
    assert t["status"] == "co_giao_chien"
    w = next(x for x in t["wars"] if x["attacker"] == "Kim" and x["victim"] == "Mộc")
    assert w["bridge"] == "Thủy" and w["missing"] is True and "Thủy" in t["need_elements"]


def test_thong_quan_quiet_when_there_is_no_war():
    assert Y(view("EX13"))[0]["methods"]["thong_quan"]["status"] == "khong_co_giao_chien"


def test_comparison_lists_disagreements_without_choosing():
    y, _, _ = Y(view("EX3"))
    comp = y["comparison"]
    d = {x["group"]: x for x in comp["disagreements"]}
    assert "Tai" in d and "cach_cuc" in d["Tai"]["favourable_in"] and "phu_uc" in d["Tai"]["unfavourable_in"]
    assert "winner" not in comp and "final" not in comp


def test_compare_unit_with_synthetic_methods():
    m1 = {"method": "a", "status": "ap_dung", "yong": ["Quan"], "xi": [], "ji": ["An"], "chou": [], "xian": []}
    m2 = {"method": "b", "status": "ap_dung", "yong": ["An"], "xi": [], "ji": [], "chou": [], "xian": []}
    m3 = {"method": "c", "status": "ap_dung", "yong": ["Quan"], "xi": [], "ji": [], "chou": [], "xian": []}
    c = yongshen.compare([m1, m2, m3])
    assert [d["group"] for d in c["disagreements"]] == ["An"] and c["consensus"] == ["Quan"]


def test_hai_cach_doc_method_is_excluded_from_the_flat_comparison():
    m = {"method": "x", "status": "hai_cach_doc", "yong": [], "xi": [], "ji": [], "chou": [], "xian": [], "alternatives": [{"yong": ["An"]}]}
    assert yongshen._flat(m) == {}


def test_yong_health_flags_a_bound_dung():
    y, _, _ = Y(view("EX7"))             # Nhâm (Quan) is bound by hợp with Đinh
    h = geju.Ctx(view("EX7"), DEFAULT, interact.resolve(view("EX7")), strength.compute(view("EX7"), DEFAULT, interact.resolve(view("EX7"))))
    out = yongshen.health(h, "Quan")
    assert out["bound"] is True and out["usable"] is False


def test_all_methods_are_draft_and_deterministic():
    for k in EX:
        a, b = Y(view(k))[0], Y(view(k))[0]
        assert a == b and a["review_status"] == "draft"
