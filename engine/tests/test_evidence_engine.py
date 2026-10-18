"""Regression tests for the interpretation-engine audit (docs/INTERPRETATION-ENGINE-AUDIT.md). Expectations come from the cited book pages
and from chart geometry, not from the engine's own previous output."""
import time

import pytest

from tvbt import aux_stars, bazi, temporal
from tvbt.api import BirthReq, _compute
from tvbt.knowledge import dsl
from tvbt.knowledge.loader import load_all
from tvbt.reasoning import interpretation as I
from tvbt.reasoning import temporal_facts as TF

REF = BirthReq(year=1990, month=5, day=17, hour=10, minute=30, gender="male", longitude=106.7)


@pytest.fixture(scope="module")
def ref():
    _, bz, tv = _compute(REF)
    return tv, bz, I.run(tv, bz, 1990, 2026)


def chart(y, m, d, h, mi, g):
    _, bz, tv = _compute(BirthReq(year=y, month=m, day=d, hour=h, minute=mi, gender=g))
    return tv, bz


def concl(out, palace, rule_id):
    return next(c for c in out["conclusions"] if c["palace"] == palace and any(r["rule_id"] == rule_id for r in c["supporting_rules"]))


def qual(c, qid):
    return next(q for q in c["invalidating_conditions"] if q["id"] == qid)


# ---------------------------------------------------------------- calculations (P0)
def test_thien_quy_counts_backward_from_van_khuc_kl_p28():
    """KL p.28 / TH p.19: from Văn Khúc as day 1 count nghịch to the birth day, then step back one palace => Khúc - (day - 2)."""
    for day in (1, 2, 3, 15, 23, 30):
        got = dict((n, b) for n, b, _ in aux_stars.place(ys=0, yb=0, month=1, day=day, hb=0, menh=0, than=0,
                                                         placed={"Tả Phụ": 4, "Hữu Bật": 10, "Văn Xương": 10, "Văn Khúc": 4}))
        assert got["Thiên Quý"] == (4 - (day - 2)) % 12, day


def test_reference_chart_thien_quy_in_menh(ref):
    tv, _, _ = ref
    menh = next(p for p in tv.palaces if p["name"] == "Mệnh")
    assert "Thiên Quý" in menh["stars"]          # Văn Khúc at Dậu, lunar day 23 -> Tý


def test_stem_clash_table_is_the_ten_pairs_of_zz_p20():
    k = bazi.STEM_CLASH_KIND
    assert len(k) == 10
    assert k[frozenset((0, 6))] == "khắc" and k[frozenset((4, 0))] == "khắc" and k[frozenset((9, 5))] == "khắc"     # 甲庚克 戊甲克 癸己克
    assert all(k[frozenset(p)] == "xung" for p in [(1, 7), (2, 8), (3, 9), (5, 1), (6, 2), (7, 3), (8, 4)])


def test_pairwise_penalty_zz_p20():
    assert {frozenset((2, 5)), frozenset((5, 8)), frozenset((8, 2)), frozenset((1, 10)), frozenset((10, 7)), frozenset((7, 1))} == bazi.PENALTY_PAIRS


def test_reference_2026_year_and_luck_interactions_include_hinh_and_bing_geng(ref):
    _, bz, _ = ref
    y = temporal.bazi_year(bz, 1990, 2026)
    ann = {(x["with"], x["kind"]) for x in y["annual_vs_natal"]}
    assert ("year", "chi_hình") in ann and ("day", "chi_hình") in ann          # 午午自刑 with the year and day pillars
    assert ("year", "can_xung") in ann                                         # 庚丙冲 (ZZ p.20), missing before
    luck = {(x["with"], x["kind"]) for x in y["luck_vs_natal"]}
    assert ("month", "chi_hình") in luck and ("hour", "chi_hình") in luck      # 巳申 = 合·刑·破 (ZZ p.19)
    assert ("year", "can_khắc") in luck                                        # 甲庚 is 克 per ZZ p.20


def test_luu_kinh_da_direction_follows_kl_p42():
    tv_m, _ = chart(1990, 5, 17, 10, 30, "male")      # dương nam -> Kình thuận
    tv_f, _ = chart(1990, 5, 17, 10, 30, "female")    # dương nữ -> Kình nghịch
    for tv, fwd in ((tv_m, True), (tv_f, False)):
        L = TF.luu_tinh(tv, 2026)
        pal = {p["name"]: p["branch_index"] for p in tv.palaces}
        lt = pal[L["Lưu Lộc Tồn"]]
        assert pal[L["Lưu Kình Dương"]] == (lt + (1 if fwd else -1)) % 12
        assert pal[L["Lưu Đà La"]] == (lt - (1 if fwd else -1)) % 12
    L = TF.luu_tinh(tv_m, 2026)                       # Bính Ngọ: Thái Tuế Ngọ, Tang Môn Thân, Bạch Hổ Dần (KL p.41 example pattern)
    br = {p["name"]: p["branch"] for p in tv_m.palaces}
    assert (br[L["Lưu Thái Tuế"]], br[L["Lưu Tang Môn"]], br[L["Lưu Bạch Hổ"]]) == ("Ngọ", "Thân", "Dần")


def test_luu_tu_hoa_is_not_given_birth_year_advice():
    tv, _ = chart(1990, 5, 17, 10, 30, "male")
    y = temporal.tuvi_year(tv, 2026)
    assert all(x["advice"] is None for x in y["luu_tu_hoa_reading"])


def test_tat_ach_rule_tests_the_exclusion_on_kl_p218():
    rules, _ = load_all()
    r = next(x for x in rules if x.id == "TV_KL_CUNG_TAT_ACH_CUOI_DOI")
    base = {"palace.name": "Tật Ách", "palace.own_stars": ["Tả Phụ"], "palace.tu_hoa": [], "palace.tam_phuong_tu_hoa": ["Hóa Lộc"]}
    assert dsl.evaluate(r.conditions, base) is True
    assert dsl.evaluate(r.conditions, {**base, "palace.own_stars": ["Tả Phụ", "Địa Kiếp"]}) is False
    assert dsl.evaluate(r.conditions, {**base, "palace.own_stars": ["Tham Lang"]}) is False
    assert dsl.evaluate(r.conditions, {**base, "palace.own_stars": ["Thiên Lương"]}) is False   # a Hóa in the tam phương no longer counts


# ---------------------------------------------------------------- conclusions and qualifiers
def test_one_fact_is_one_conclusion_with_independent_books(ref):
    _, _, out = ref
    c = concl(out, "Tài Bạch", "TV_KL_CUNG_TAI_BACH_LOC_TON")
    assert c["rule_count"] >= 5 and c["independent_sources"] == 3                 # KL p.216, TH p.106, TT pp.47/80-81/159
    assert set(c["contributing_facts"]) == {"Lộc Tồn ở Tài Bạch", "Thiên Mã ở Tài Bạch"}
    assert "một căn cứ" in c["final_interpretation"]


def test_loc_ton_qualifiers_kl_p142_p197(ref):
    _, _, out = ref
    c = concl(out, "Tài Bạch", "TV_KL_CUNG_TAI_BACH_LOC_TON")
    assert qual(c, "Q_KL142_LOC_TON_KHONG_KIEP")["status"] == "not_met"         # no Không/Kiếp in Thân itself
    assert qual(c, "Q_KL142_LOC_TON_THAI_TUE")["status"] == "not_met"           # Thái Tuế at Ngọ, outside Thân-Tý-Thìn
    assert qual(c, "Q_KL142_LOC_DAO")["status"] == "met"                        # Địa Kiếp at Thìn (tam hợp of Thân)
    assert qual(c, "Q_KL197_SONG_LOC")["status"] == "met"                       # Hóa Lộc at Sửu: not in Mệnh-Tài-Quan


def test_khoi_with_triet_is_qualified_kl_p140(ref):
    _, _, out = ref
    c = next(x for x in out["conclusions"] if x["palace"] == "Thiên Di" and "Thiên Khôi ở Thiên Di" in x["contributing_facts"])
    assert qual(c, "Q_KL140_KHOI_VIET_PHAM")["status"] == "met"


def test_tu_vi_without_ta_huu_is_flagged_tt_p20(ref):
    _, _, out = ref
    c = next(x for x in out["conclusions"] if x["palace"] == "Quan Lộc" and x["polarity"] == "support")
    assert qual(c, "Q_TT20_TU_VI_CO_QUAN")["status"] == "met"                   # Tả Hữu at Mùi, outside Thìn's tam phương


def test_loc_ton_with_khong_kiep_dong_cung_is_voided():
    tv, bz = chart(1970, 5, 9, 18, 15, "female")
    out = I.run(tv, bz, 1970, None)
    hits = [q for c in out["conclusions"] for q in c["invalidating_conditions"] if q["id"] == "Q_KL142_LOC_TON_KHONG_KIEP" and q["status"] == "met"]
    assert hits and hits[0]["effect"] == "voids"


def test_khoi_without_tuan_triet_is_not_qualified():
    tv, bz = chart(1971, 5, 1, 13, 15, "male")
    out = I.run(tv, bz, 1971, None)
    assert any(q["id"] == "Q_KL140_KHOI_VIET_PHAM" and q["status"] == "not_met" for c in out["conclusions"] for q in c["invalidating_conditions"])


def test_generic_birth_year_readings_are_not_counted_as_chart_evidence(ref):
    _, _, out = ref
    g = [c for c in out["conclusions"] if c["generic"]]
    assert g and all(all("năm sinh" in f or "giới" in f or "âm dương" in f for f in c["contributing_facts"]) for c in g)
    menh = next(ch for ch in out["report"]["chapters"] if ch["id"] == "menh")
    assert all(not x["generic"] for x in menh["sections"]["yeu_to_ho_tro"])


def test_conflicts_are_kept_not_averaged(ref):
    _, _, out = ref
    ql = [c for c in out["conclusions"] if c["palace"] == "Quan Lộc"]
    assert any(c["polarity"] == "support" for c in ql) and any(c["polarity"] == "limit" for c in ql)
    rels = [k for c in ql for k in c["conflicts"]]
    assert rels and all(k["resolution"] in ("both_hold", "unresolved") for k in rels)
    assert not any("điểm" in c["final_interpretation"].lower().split() for c in out["conclusions"])   # no score anywhere


# ---------------------------------------------------------------- palaces, vô chính diệu, scope
def test_all_twelve_palaces_have_six_layers_and_a_summary(ref):
    _, _, out = ref
    assert len(out["dossiers"]) == 12
    for d in out["dossiers"]:
        assert set(d["layers"]) == {"ban_cung", "tam_phuong", "cach", "menh_than_cuc", "van", "tong_hop"} and d["summary"]


def test_vo_chinh_dieu_borrows_from_opposite_tt_p18(ref):
    _, _, out = ref
    by = {d["palace"]: d for d in out["dossiers"]}
    assert by["Tử Tức"]["layers"]["tam_phuong"]["vo_chinh_dieu"]["chu"] == ["Thiên Cơ", "Cự Môn"]      # from Điền Trạch (Mão)
    assert by["Tật Ách"]["layers"]["tam_phuong"]["vo_chinh_dieu"]["chu"] == ["Thái Dương", "Thái Âm"]  # from Phụ Mẫu (Sửu)
    assert "Thiên Cơ" not in by["Tử Tức"]["layers"]["tam_phuong"]["khach"]                          # borrowed chủ is not also khách


def test_thanh_pha_tt_p18(ref):
    _, _, out = ref
    tp = next(d for d in out["dossiers"] if d["palace"] == "Mệnh")["layers"]["cach"]["thanh_pha"]
    assert tp["verdict"] == "thanh_co_pha" and any("Hỏa Tinh" in x for x in tp["harsh_met"])
    tv, bz = chart(1970, 1, 24, 11, 15, "male")
    out2 = I.run(tv, bz, 1970, None)
    assert next(d for d in out2["dossiers"] if d["palace"] == "Mệnh")["layers"]["cach"]["thanh_pha"]["verdict"] == "chua_thanh"


def test_scope_guards_for_tat_ach_phu_the_tu_tuc(ref):
    _, _, out = ref
    by = {d["palace"]: d for d in out["dossiers"]}
    for p in ("Tật Ách", "Phu Thê", "Tử Tức"):
        assert by[p]["layers"]["tong_hop"]["guard"]


def test_period_chapter_separates_structure_from_activation(ref):
    _, _, out = ref
    v = next(ch for ch in out["report"]["chapters"] if ch["id"] == "van_han")
    txt = " ".join(v["sections"]["co_so_luan_giai"])
    assert "Quan Lộc" in txt and "Thiên Di" in txt and "NEEDS SOURCE" in txt and "chưa đối chiếu" in txt
    assert any("không phải" in g or "Không nêu" in g for g in v["sections"]["dieu_kien_gioi_han"]["guards"])


def test_report_has_six_sections_and_one_header(ref):
    _, _, out = ref
    rep = out["report"]
    for ch in rep["chapters"]:
        assert {"nhan_dinh_tong_quan", "co_so_luan_giai", "yeu_to_ho_tro", "han_che_mau_thuan", "luan_giai_tong_hop", "dieu_kien_gioi_han"} <= set(ch["sections"])
    md = I.to_markdown(out)
    assert md.count("không phải dự báo sự kiện") == 1
    low = md.lower()
    for bad in ("chắc chắn sẽ", "nhất định sẽ", "suốt đời mang", "lanh chanh"):
        assert bad not in low


# ---------------------------------------------------------------- Bát Tự
def test_bazi_strength_methods_reference(ref):
    _, _, out = ref
    zz, tvh = out["bazi"]["strength"]["methods"]
    assert zz["tests"] == {"dac_lenh": False, "dac_vi": False, "dac_sinh": True} and zz["verdict"] is None    # ZZ p.27 gives no verdict
    assert tvh["verdict"] == "nhược" and abs(tvh["own_share"] - 0.3836) < 1e-3                               # TVH p.355, strict 40%


def test_bazi_zz_three_tests_all_present_or_absent():
    for (y, m, d, h, g), want in (((1970, 1, 3, 0, "female"), "vượng"), ((1970, 8, 22, 1, "male"), "nhược")):
        tv, bz = chart(y, m, d, h, 15, g)
        assert I.run(tv, bz, y, None)["bazi"]["strength"]["methods"][0]["verdict"] == want


def test_distant_stem_combine_is_potential_only(ref):
    _, _, out = ref
    h = next(x for x in out["bazi"]["interactions"] if x["kind"] == "stem_combine")
    assert h["transform"] == "chưa xét" and h["span"] == 3 and "cách xa" in h["note"]


# ---------------------------------------------------------------- edge cases, determinism, performance
@pytest.mark.parametrize("args", [(2020, 6, 1, 8, 0, "female"),       # lunar leap 4th month 2020
                                  (1990, 5, 17, 23, 30, "male"),      # late Tý hour
                                  (2024, 2, 4, 15, 26, "female"),     # minutes before Lập Xuân 2024
                                  (2024, 2, 4, 15, 27, "female")])
def test_edge_charts_run_and_are_deterministic(args):
    tv, bz = chart(*args)
    a, b = I.run(tv, bz, args[0], args[0] + 30), I.run(tv, bz, args[0], args[0] + 30)
    assert a == b and len(a["dossiers"]) == 12


def test_performance(ref):
    tv, bz, _ = ref
    t = time.perf_counter()
    for _ in range(5):
        I.run(tv, bz, 1990, 2026)
    assert (time.perf_counter() - t) / 5 < 0.5
