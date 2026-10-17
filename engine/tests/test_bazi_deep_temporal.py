import copy

import pytest

from bazi_deep_util import EX, view
from tvbt.bazi_deep import pipeline, temporal_deep as td
from tvbt.bazi_deep.model import ChartView
from tvbt.bazi_deep.profile import DEFAULT


def A(name_or_view, *pillars):
    v = view(name_or_view) if isinstance(name_or_view, str) else name_or_view
    nat = td.natal_bundle(v)
    return v, nat, td.analyse_extended(v, DEFAULT, nat, list(pillars))


def test_temporal_pillar_must_have_valid_parity():
    with pytest.raises(ValueError):
        td.tp("luck", 0, 1)
    assert td.tp("luck", 4, 8)["name"] == "Mậu Thân"


def test_overlay_never_mutates_the_natal_resolution():
    v = view("EX1"); nat = td.natal_bundle(v)
    before = copy.deepcopy((nat["R"].mult, nat["R"].shifts, nat["R"].opened, nat["R"].interactions))
    td.analyse_extended(v, DEFAULT, nat, [td.tp("luck", 4, 8), td.tp("year", 8, 4)])
    assert (nat["R"].mult, nat["R"].shifts, nat["R"].opened, nat["R"].interactions) == before


def test_luck_clash_on_the_lenh_downgrades_the_cach_and_weakens_the_natal_branch():
    v, nat, o = A("EX1", td.tp("luck", 4, 8))               # Mậu Thân: Thân xung Dần (nguyệt lệnh)
    assert o["cach"]["natal"] == ["Kiến Lộc", "thanh"] and o["cach"]["extended"] == ["Kiến Lộc", "thanh_nhung_bi_pha"] and o["effect"] == "pha_cach"
    kinds = {e["kind"] for e in o["events"]}
    assert "branch_clash" in kinds
    R2, *_ = td.overlay(v, DEFAULT, nat["R"], [td.tp("luck", 4, 8)])
    assert R2.mult["month.branch"] < nat["R"].mult.get("month.branch", 1.0)


def test_year_clash_on_a_kho_opens_it_only_in_the_extended_chart():
    v = view("EX1"); nat = td.natal_bundle(v)
    R2, _, _, ev = td.overlay(v, DEFAULT, nat["R"], [td.tp("year", 8, 4)])      # Nhâm Thìn: Thìn xung Tuất (day branch)
    assert "day" in R2.opened and "day" not in nat["R"].opened
    assert any(e["kind"] == "branch_clash" and e.get("opens_kho") for e in ev)


def test_temporal_branch_completing_a_tam_hop_is_recorded_and_moves_strength():
    v, nat, o = A("EX3", td.tp("luck", 8, 8))                 # Nhâm Thân completes Thân–Tý–Thìn
    assert "branch_triad" in o["event_kinds"]
    assert o["ratio"][1] != o["ratio"][0]
    R2, *_ = td.overlay(v, DEFAULT, nat["R"], [td.tp("luck", 8, 8)])
    assert R2.shifts["hour.branch"][0] == "Thủy" and R2.shifts["day.branch"][0] == "Thủy"


def test_semi_triad_from_a_temporal_branch():
    v, nat, o = A("EX1", td.tp("luck", 4, 8))                 # Thân + natal Tý: sinh–vượng bán hợp Thủy
    assert any(e["kind"] == "branch_semi_triad" and e["element"] == "Thủy" for e in o["events"])


def test_phuc_ngam_phan_ngam_tinh_lam_and_thien_khac_dia_xung():
    _, _, o = A("EX1", td.tp("luck", 0, 0))                   # Giáp Tý == the year pillar
    assert "phuc_ngam" in o["event_kinds"]
    _, _, o = A("EX1", td.tp("luck", 6, 6))                   # Canh Ngọ vs Giáp Tý: stem clash + branch clash
    assert "phan_ngam" in o["event_kinds"]
    _, _, o = A("EX1", td.tp("luck", 0, 0), td.tp("year", 0, 0))
    assert "tue_van_tinh_lam" in o["event_kinds"]
    _, _, o = A("EX1", td.tp("luck", 0, 0), td.tp("year", 6, 6))     # Canh (Kim) khắc Giáp (Mộc) and Ngọ xung Tý
    assert "thien_khac_dia_xung" in o["event_kinds"]


def test_temporal_stem_combine_binds_the_natal_stem_without_evaluating_hoa():
    v, nat, o = A("EX1", td.tp("year", 5, 5))                 # Kỷ hợp Giáp (the Nhật Chủ and the year stem)
    ev = [e for e in o["events"] if e["kind"] == "stem_combine"]
    assert ev and all(e["status"] == "hop_khong_hoa" and "không xét hóa" in e["note"] for e in ev)


def test_effect_classification_covers_all_four_outcomes_across_the_examples():
    seen = {}
    for k in EX:
        v = view(k); nat = td.natal_bundle(v)
        for n in range(60):
            o = td.analyse_extended(v, DEFAULT, nat, [td.tp("luck", n % 10, n % 12)])
            seen.setdefault(o["effect"], (k, n))
    assert set(seen) == {"pha_cach", "tro_cach", "doi_cach", "trung_tinh"}


def test_doi_cach_when_a_temporal_stem_makes_a_hidden_month_stem_thau():
    _, _, o = A("EX11", td.tp("luck", 9, 9))                  # Quý Dậu: Quý is hidden in Thìn (month) and now on the stems
    assert o["effect"] == "doi_cach" and o["cach"]["natal"][0] == "Chính Tài" and o["cach"]["extended"][0] == "Thiên Ấn"


def test_roles_are_reported_per_method_and_never_merged():
    _, _, o = A("EX1", td.tp("luck", 4, 8))
    assert set(o["roles"]) == {"phu_uc", "dieu_hau", "cach_cuc", "cach_cuc_tvh", "thong_quan", "thuan_the"}
    assert o["roles"]["cach_cuc"]["stem_group"] == "Tai"
    assert "final" not in o and "role" not in o


def test_month_pillars_follow_five_tigers():
    ms = td.month_pillars(0)                                  # Giáp year: Bính Dần ... Đinh Sửu
    assert ms[0] == (2, 2) and ms[1] == (3, 3) and ms[11] == (3, 1)


def test_timeline_picks_luck_by_exact_start_and_labels_everything_draft():
    v = view("EX1")
    luck = [{"index": 1, "stem": 4, "branch": 8, "start_year_exact": 2000.0}, {"index": 2, "stem": 5, "branch": 9, "start_year_exact": 2010.5}]
    tl = pipeline.timeline(v, DEFAULT, luck, [(2000, 6, 6), (2005, 1, 1), (2010, 2, 2), (2011, 8, 4)])
    assert tl["review_status"] == "draft"
    assert [y["pillars"][0] for y in tl["years"]] == ["Mậu Thân", "Mậu Thân", "Mậu Thân", "Kỷ Dậu"]     # 2010.5 > 2010.09 -> still luck #1 in 2010; luck #2 from 2011
    assert [y["labels"] for y in tl["years"]][0] == ["luck", "year"]
    assert all(e["pack_problems"] == [] for e in tl["luck"] + tl["years"])


def test_timeline_findings_come_from_the_draft_temporal_pack_with_provenance():
    v = view("EX1")
    tl = pipeline.timeline(v, DEFAULT, [{"index": 1, "stem": 4, "branch": 8, "start_year_exact": 2000.0}], [])
    f = {x["claim"]: x for x in tl["luck"][0]["findings"]}
    assert "bt_van_pha_cach" in f and f["bt_van_pha_cach"]["basis"] == "draft"          # the system's own temporal rule stays draft
    kinds = [c["kind"] for c in f["bt_van_pha_cach"]["chain"]]
    assert "rule" in kinds and "fact" in kinds and "source" in kinds
    origin = next(c["origin"] for c in f["bt_van_pha_cach"]["chain"] if c["kind"] == "fact")
    assert "temporal_deep" in origin


def test_method_roles_become_separate_findings():
    v = view("EX1")
    tl = pipeline.timeline(v, DEFAULT, [{"index": 1, "stem": 4, "branch": 8, "start_year_exact": 2000.0}], [])
    claims = {x["claim"] for x in tl["luck"][0]["findings"]}
    assert "bt_van_dung_cach_cuc" in claims and "bt_van_ky_phu_uc" in claims        # same stem: dụng by cách cục, kỵ by phù ức
    assert not any(c in claims for c in ("bt_van_ky_cach_cuc", "bt_van_dung_phu_uc"))


def test_temporal_pack_is_valid_draft_and_has_vietnamese_claims():
    import json
    from tvbt.knowledge.schema import validate_pack
    rules, sources = pipeline.load_structure_pack("pack_temporal.json")
    assert validate_pack(rules, sources, pipeline.KNOWN) == []
    assert all(r.reviewStatus == ("verified" if r.id.startswith("BT_TTT_") else "draft") for r in rules)
    claims = json.loads((pipeline.DATA / "claims_vi.json").read_text("utf-8"))
    assert all(c["claim"] in claims for r in rules for c in r.consequences if c["kind"] == "finding")


def test_timeline_is_deterministic_and_has_no_forecast_wording():
    v = view("EX3")
    luck = [{"index": 1, "stem": 8, "branch": 8, "start_year_exact": 2001.0}]
    a = pipeline.timeline(v, DEFAULT, luck, [(2003, 9, 7)])
    assert a == pipeline.timeline(v, DEFAULT, luck, [(2003, 9, 7)])
    blob = str(a).lower()
    assert "chắc chắn sẽ" not in blob and "nhất định" not in blob
