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
    assert not any(i.endswith(("_CACH_CUC", "_PHU_UC")) for i in ids)
    # S2: the cái đầu / tiệt cước rules need a luck stem the điều hậu cell names. The owner's cell (Đinh, tháng Sửu) names Giáp and Canh;
    # Ất Mùi used to fire BT_TTT_CAIDAU_DIEU_HAU because Ất shares Giáp's ten-god group (Ấn). It no longer does.
    ate = next(x for x in owner["luck"] if x["pillar"] == "Ất Mùi")
    assert "BT_TTT_CAIDAU_DIEU_HAU" not in [f["rule_id"] for f in ate["findings"]] and ate["dieu_hau"]["stem"] is None


def test_dieu_hau_role_is_by_the_stem_the_cell_names(owner):
    """luck_role.yong only for the cell's chính stem (Giáp), xi for the other stem it names (Canh); Ất (same group as Giáp) gets nothing."""
    by = {x["pillar"]: x["dieu_hau"] for x in owner["luck"]}
    assert owner["dieu_hau"]["table"] == ["Giáp", "Canh"]
    assert by["Giáp Ngọ"]["stem"] == "yong" and by["Canh Tý"]["stem"] == "xi" and by["Ất Mùi"]["stem"] is None
    assert by["Bính Thân"]["branch"] == "xi"            # Thân's main qi is Canh


def test_need_element_is_the_heat_index_not_the_table(owner):
    """'cần Hỏa' comes from the system's cold/heat index (he_thong) and is voiced through the fired TTT hàn noãn rule; the table names stems."""
    dh = owner["dieu_hau"]
    assert dh["need"] == ["Hỏa"] and dh["need_src"] == "he_thong"
    assert dh["need_rule"] == "BT_TTT_HANNOAN_CAN_NOAN" and dh["need_rule_element"] == "Hỏa"
    assert "Hỏa" not in dh["table"] and all(len(x) <= 5 for x in dh["table"])


def test_reconcile_one_verdict_per_luck_pillar(owner):
    """Plan step 3: the cách table and the điều hậu table combined into one verdict per luck pillar (owner chart, hand-checked against the
    tables: Thiên Tài cách, nhật chủ nhược, Tài largest → vận tốt Tỉ Kiếp, vận xấu Tài / Quan Sát / Thực Thương, TVH pp.378, 383; điều hậu
    Đinh tháng Sửu → Giáp (chính), Canh, TVH pp.389-396)."""
    v = {x["pillar"]: x["reconcile"] for x in owner["luck"]}
    assert v["Canh Tý"]["agree"] == "khac" and v["Canh Tý"]["verdict"] == "co_dieu_kien"       # Tài (bad by cách) but Canh is a điều hậu stem
    assert v["Kỷ Hợi"]["verdict"] == "nang" and [x["stem"] for x in v["Kỷ Hợi"]["support"]] == ["Giáp"]
    assert v["Mậu Tuất"]["verdict"] == "nang" and [x["stem"] for x in v["Mậu Tuất"]["support"]] == ["Đinh"]
    assert v["Giáp Ngọ"]["verdict"] == "thuan" and v["Giáp Ngọ"]["agree"] == "cung"
    assert v["Đinh Dậu"]["agree"] == "tron"                                                  # Đinh good, Dậu (Tài) bad
    mt = next(x for x in owner["luck"] if x["pillar"] == "Mậu Tuất")
    # owner review 2026-10-22: the years follow each year's own verdict (2024 Giáp Thìn: Thìn bad; 2027 Đinh Mùi: Mùi bad, hình + phá the luck Tuất)
    assert [y["year"] for y in mt["good_years"]] == [2025, 2026]


def test_shensha_stem_named_in_vietnamese():
    d = api.chart_facts(BirthReq(year=1990, month=5, day=17, hour=10, minute=0, gender="male", to_year=2026))["bazi"]["deep"]
    assert all(not any("一" <= ch <= "鿿" for ch in x["at"]) for x in d["shensha"])


def test_luck_relation_rule(owner):
    """W3 (2026-10-25, engine/data/kg/bazi_luck_relations.json, he_thong): a luck pillar's relations with the natal chart move or confirm
    its verdict; a year is judged by the tables alone. Owner chart: Mậu Tuất hình the month and day Sửu, Ất Mùi phản ngâm the month pillar
    (both already nặng: confirmed), Bính Thân's stem hợp the two Tân (Thủy = Quan Sát, vận xấu), Giáp Ngọ bán hợp Hỏa with the hour Dần."""
    from tvbt.bazi_deep.pipeline import reconcile
    v = {x["pillar"]: x["reconcile"] for x in owner["luck"]}
    assert (v["Mậu Tuất"]["rel"]["rule"], v["Mậu Tuất"]["rel"]["effect"], v["Mậu Tuất"]["verdict"]) == ("BT_HT_LUCK_REL_CAP", "confirm", "nang")
    assert any(e["kind"] == "phan_ngam" and e["targets"] == ["month"] for e in v["Ất Mùi"]["rel"]["events"])
    assert v["Bính Thân"]["rel"]["rule"] == "BT_HT_LUCK_REL_HOP_KY" and v["Bính Thân"]["agree"] == "tron"
    assert v["Giáp Ngọ"]["rel"]["rule"] == "BT_HT_LUCK_REL_HOP_DUNG" and v["Giáp Ngọ"]["verdict"] == "thuan"
    assert all("rel" not in y["reconcile"] for y in owner["years"])
    clash = [{"kind": "branch_clash", "targets": ["month"], "part": "branch"}]
    good = {"stem": "tot", "branch": "tot"}
    assert reconcile(good, {"stem": "yong"}, False, clash)["verdict"] == "co_dieu_kien"
    assert reconcile(good, {"stem": "yong"}, False, [{"kind": "branch_clash", "targets": ["hour"], "part": "branch"}])["verdict"] == "thuan"
    hop = [{"kind": "stem_combine", "targets": ["year"], "part": "stem", "element": "Thủy"}]
    assert reconcile({"stem": None, "branch": None}, {}, False, hop, {"Thủy"}, set())["verdict"] == "kha_thuan"
    assert reconcile(good, {"stem": "yong"}, False, hop, set(), {"Thủy"})["verdict"] == "kha_thuan"
    assert reconcile({"stem": None, "branch": None}, {}, False, hop, {"Thủy"}, {"Thủy"})["verdict"] == "trung"   # both sides: neither
