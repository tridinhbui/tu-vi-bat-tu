"""Track C (plan quirky-tinkering-rabin): the Bát Tự structure facts the reader prose needs (bazi_deep.pipeline.prose_summary via /api/facts).
Checked on the owner's chart 09/01/2002 04:30 nam (Tân Tỵ / Tân Sửu / Đinh Sửu / Nhâm Dần) and the 1990 golden chart."""
import pytest

from tvbt import api
from tvbt.api import BirthReq


@pytest.fixture(scope="module")
def owner():
    return api.chart_facts(BirthReq(year=2002, month=1, day=9, hour=4, minute=30, gender="male", to_year=2026))["bazi"]["deep"]


def luck(d, name):
    return next(x for x in d["luck"] if x["pillar"] == name)


def kinds(x, target):
    return {e["kind"] for e in x["events"] if target in e["targets"]}


def test_lieu_nien_three_years(owner):
    assert [y["year"] for y in owner["years"]] == [2026, 2027, 2028]
    y = owner["years"][0]
    assert (y["pillar"], y["luck"], y["ten_god"], y["branch_god"]) == ("Bính Ngọ", "Mậu Tuất", "Kiếp Tài", "Tỉ Kiên")


def test_relations_follow_zz_p20_tables(owner):
    # 丑刑戌 (支三刑 pairwise) and 壬戊冲 (干冲克, ten pairs): both missing from the overlay's calibrated tables
    mt = luck(owner, "Mậu Tuất")
    assert kinds(mt, "month") == {"branch_penalty"} and kinds(mt, "day") == {"branch_penalty"} and kinds(mt, "hour") == {"stem_clash"}
    kh = luck(owner, "Kỷ Hợi")
    assert kinds(kh, "year") == {"branch_clash"} and kinds(kh, "hour") == {"branch_six_combine", "branch_destroy"}
    bt = luck(owner, "Bính Thân")
    assert "phan_ngam" in kinds(bt, "hour")                     # 丙壬冲 + 寅申冲
    dd = luck(owner, "Đinh Dậu")
    assert any(e["kind"] == "branch_triad" and e["element"] == "Kim" for e in dd["events"])
    gn = luck(owner, "Giáp Ngọ")                                # 半合: 寅午 holds the middle branch 午
    assert any(e["kind"] == "branch_semi_triad" and e["element"] == "Hỏa" and e["targets"] == ["hour"] for e in gn["events"])


def test_tvh_table_and_verdicts(owner):
    c = owner["cach_tvh"]
    assert (c["status"], c["cach"], c["dm"], c["dominant"], c["yong"], c["van_tot"]) == ("ap_dung", "Thiên Tài", "nhược", "Tài", ["Tỉ Kiếp"], ["Tỉ Kiếp"])
    assert luck(owner, "Đinh Dậu")["tvh"] == {"stem": "tot", "branch": "xau"}
    assert any(v["rule_id"] == "BT_TVH_TB_TAI_2" and v["verdict"] == "tot" for v in owner["verified"])


def test_natal_extras(owner):
    assert [owner["pillars"][k]["nap_am"] for k in ("year", "month", "day", "hour")] == ["Bạch Lạp Kim", "Bích Thượng Thổ", "Giản Hạ Thủy", "Kim Bạch Kim"]
    assert owner["pillars"]["year"]["stage"] == "Đế Vượng"
    ss = {(x["vi"], x["pillar"]) for x in owner["shensha"]}
    assert ("Phi Nhận", "day") in ss and ("Dương Nhận", "year") in ss
    assert all(x["gloss"] is None for x in owner["shensha"] if x["kind"] == "hung")


def test_no_draft_premise_rules_reach_the_prose(owner):
    ids = [f["rule_id"] for x in owner["luck"] for f in x["findings"]]
    assert ids and not any(i.endswith(("_CACH_CUC", "_PHU_UC")) for i in ids)
    assert "BT_TTT_CAIDAU_DIEU_HAU" in ids


def test_shensha_stem_named_in_vietnamese():
    d = api.chart_facts(BirthReq(year=1990, month=5, day=17, hour=10, minute=0, gender="male", to_year=2026))["bazi"]["deep"]
    assert all(not any("一" <= ch <= "鿿" for ch in x["at"]) for x in d["shensha"])
