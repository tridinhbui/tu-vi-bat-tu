import pytest

from bazi_deep_util import EX, HOA1, SAVED, TONG1, view
from tvbt.bazi_deep import geju, interact, strength
from tvbt.bazi_deep.profile import DEFAULT
from tvbt.ganzhi import BRANCHES_VI, STEMS_VI


def G(v, profile=DEFAULT):
    R = interact.resolve(v, profile)
    S = strength.compute(v, profile, R)
    return geju.analyse(v, profile, R, S)


def test_lu_and_nhan_tables_against_the_classical_lists():
    lu = {"Giáp": "Dần", "Ất": "Mão", "Bính": "Tỵ", "Đinh": "Ngọ", "Mậu": "Tỵ", "Kỷ": "Ngọ", "Canh": "Thân", "Tân": "Dậu", "Nhâm": "Hợi", "Quý": "Tý"}
    assert {STEMS_VI[s]: BRANCHES_VI[b] for s, b in geju.LU.items()} == lu
    nhan = {"Giáp": "Mão", "Bính": "Ngọ", "Mậu": "Ngọ", "Canh": "Dậu", "Nhâm": "Tý"}
    assert {STEMS_VI[s]: BRANCHES_VI[b] for s, b in geju.NHAN.items()} == nhan


@pytest.mark.parametrize("name,cach", [("EX1", "Kiến Lộc"), ("EX6", "Kiến Lộc"), ("EX15", "Kiến Lộc"), ("EX7", "Kiến Lộc"), ("EX9", "Dương Nhận"),
                                       ("EX2", "Chính Quan"), ("EX3", "Chính Quan"), ("EX4", "Thất Sát"), ("EX5", "Chính Tài"),
                                       ("EX11", "Chính Tài"), ("EX12", "Chính Ấn"), ("EX13", "Chính Ấn")])
def test_inner_cach_follows_the_month_branch(name, cach):
    assert geju.inner_candidates(view(name), DEFAULT)[0]["name"] == cach


def test_thau_wins_over_unrevealed_main_and_multiple_thau_are_all_candidates():
    c = geju.inner_candidates(view("EX14"), DEFAULT)          # Kỷ in Dần: Giáp (Chính Quan, year) and Bính (Chính Ấn, month) both thấu
    assert [x["name"] for x in c] == ["Chính Quan", "Chính Ấn"]
    c11 = geju.inner_candidates(view("EX11"), DEFAULT)[0]
    assert c11["tou"] == [] and "không thấu" in c11["basis"]      # falls back to the main qi


def test_nguyet_kiep_and_yin_nhan_is_a_profile_choice():
    from tvbt.bazi_deep.model import ChartView
    kiep = ChartView.from_names("Ất Hợi / Mậu Dần / Ất Dậu / Đinh Hợi")          # Ất in Dần: the main qi Giáp is Kiếp Tài
    assert geju.inner_candidates(kiep, DEFAULT)[0]["name"] == "Nguyệt Kiếp"
    ding = ChartView.from_names("Bính Tuất / Ất Mùi / Đinh Mùi / Canh Tuất")        # Đinh in Mùi: Nhận of a yin stem
    assert geju.inner_candidates(ding, DEFAULT)[0]["name"] != "Âm Nhận"
    assert geju.inner_candidates(ding, DEFAULT.with_(yin_nhan=True))[0]["name"] == "Âm Nhận"
    assert G(ding, DEFAULT.with_(yin_nhan=True))["inner"][0]["state"] in ("thanh", "bai", "chua_ro", "thanh_nhung_bi_pha")


def test_thuong_kien_quan_is_bai_and_unsaved_in_ex3():
    c = G(view("EX3"))["inner"][0]
    ids = {b["id"]: b["saved_by"] for b in c["bai"]}
    assert c["state"] == "bai" and ids["quan_bi_xung_lenh"] is None          # nguyệt lệnh bị xung kề, không có hợp giải
    tk = next(b for b in c["bai"] if b["id"] == "thuong_kien_quan")
    assert "month.stem" in tk["evidence"] and tk["saved_by"] == "any:An" and tk["saved_strength"].startswith("yếu")   # Quý ẩn trong Tý: chỉ cứu yếu


def test_cuu_ung_turns_bai_into_bai_co_cuu():
    c = G(view(SAVED))["inner"][0]
    assert c["name"] == "Chính Quan" and c["state"] == "bai_co_cuu"
    assert [(b["id"], b["saved_by"]) for b in c["bai"]] == [("thuong_kien_quan", "visible:An")]


def test_cach_thanh_but_lenh_bi_pha_is_distinguished_from_clean_thanh():
    assert G(view("EX1"))["inner"][0]["state"] == "thanh"
    assert G(view("EX10"))["inner"][0]["state"] == "thanh_nhung_bi_pha"      # Dần bị Thân xung kề


def test_quan_sat_hon_tap_detected_and_not_saved_when_nothing_restrains_it():
    v = view("EX7")                      # Nhâm (Chính Quan) and Quý (Thất Sát) are both on the stems, but Nhâm is bound by its hợp with Đinh
    R = interact.resolve(v)
    ctx = geju.Ctx(v, DEFAULT, R, strength.compute(v, DEFAULT, R))
    assert geju.pred(ctx, "bound:Quan")[0] and not geju.pred(ctx, "both_visible:Quan+Sat")[0]     # 'hợp Quan lưu Sát', not a plain hỗn tạp
    assert geju.pred(ctx, "visible:Sat")[0]


def test_hon_tap_bai_for_chinh_quan_cach():
    from tvbt.bazi_deep.model import ChartView
    # Nhật Chủ Bính: Quan = Quý, Sát = Nhâm. Quý và Nhâm cùng thấu, tháng Tý (bản khí Quý = Chính Quan)
    v = ChartView.from_names("Nhâm Dần / Nhâm Tý / Bính Tuất / Quý Tỵ")
    out = G(v)
    c = out["inner"][0]
    assert c["name"] == "Chính Quan" and "quan_sat_hon_tap" in [b["id"] for b in c["bai"]]
    assert next(b for b in c["bai"] if b["id"] == "quan_sat_hon_tap")["saved_by"] is None


def test_tong_chan_replaces_the_inner_cach():
    out = G(view(TONG1))
    assert [(o["name"], o["quality"]) for o in out["outer"]] == [("Tòng Sát", "chân")]
    assert out["readings"][0]["kind"] == "ngoai_cach" and out["arbitration"] == "ngoại cách chân thay nội cách"


def test_tong_gia_keeps_two_readings_and_never_replaces():
    out = G(view("EX4"))
    assert [(o["name"], o["quality"]) for o in out["outer"]] == [("Tòng Sát", "giả")]
    kinds = [r["kind"] for r in out["readings"]]
    assert kinds[0] == "noi_cach" and "ngoai_cach_gia" in kinds and out["arbitration"] == "giữ cả hai cách đọc"


def test_hoa_chan_is_outer_cach_and_gia_is_kept_beside_inner():
    assert [(o["name"], o["quality"]) for o in G(view(HOA1))["outer"]][0] == ("Hóa Thổ", "chân")
    o5 = G(view("EX5"))["outer"]
    assert ("Hóa Thổ", "giả") in [(o["name"], o["quality"]) for o in o5]
    assert "lenh_khong_bi_pha" in next(o for o in o5 if o["name"] == "Hóa Thổ")["evidence"]["unmet"]


def test_no_outer_cach_for_a_rooted_strong_day_master():
    for k in ("EX1", "EX13", "EX8"):
        assert G(view(k))["outer"] == [], k
    assert [(o["name"], o["quality"]) for o in G(view("EX15"))["outer"]] == [("Tòng Cường", "chân")]      # Ất, Mão tháng: Tỉ Kiếp + Ấn, no Tài Quan


def test_every_definition_is_draft_and_predicates_parse():
    import json
    d = json.loads((geju.DATA / "geju_defs.json").read_text("utf-8"))
    assert d["_status"] == "draft"
    v = view("EX1"); R = interact.resolve(v); Sx = strength.compute(v, DEFAULT, R); ctx = geju.Ctx(v, DEFAULT, R, Sx)
    for name, c in d["defs"].items():
        exprs = list(c["thanh_any"]) + list(c["bai"].values()) + [x for l in c["cuu"].values() for x in l]
        for e in exprs:
            geju.pred(ctx, e)                      # raises on an unknown predicate
        assert set(c["cuu"]) == set(c["bai"]), name
    with pytest.raises(ValueError):
        geju.pred(ctx, "bogus:X")


def test_cach_analysis_is_deterministic_for_all_examples():
    for k in EX:
        assert G(view(k)) == G(view(k))
