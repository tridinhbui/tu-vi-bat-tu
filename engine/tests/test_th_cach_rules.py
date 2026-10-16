"""Thực Hành pp.72-77: named patterns, sinh/vượng/bại/tuyệt table, season/hour facts."""
from tvbt import calendar_core as cc, tuvi
from tvbt.knowledge.loader import load_all
from tvbt.knowledge.schema import validate_pack
from tvbt.reasoning import engine, facts

RULES, SOURCES = load_all()


def pal(name="Mệnh", branch="Dần", own=(), opp=(), flank=(), tp=(), tphoa=(), hoa=(), dg=None, chart=None, **kw):
    p = {"palace.name": name, "palace.branch": branch, "palace.own_stars": list(own), "palace.own_major_stars": [s for s in own if s in (
         "Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng", "Thái Dương", "Thái Âm", "Cự Môn", "Thiên Cơ", "Tham Lang", "Thất Sát", "Phá Quân", "Liêm Trinh")],
         "palace.rel.opp_stars": list(opp), "palace.rel.opp_majors": list(opp), "palace.rel.flank_stars": list(flank),
         "palace.rel.tp_stars": list(own) + list(opp) + list(tp), "palace.rel.tp_majors": list(own) + list(opp) + list(tp),
         "palace.rel.tp_hoa": list(tphoa), "palace.tu_hoa": list(hoa), "palace.tuan": False, "palace.triet": False, "palace.has_no_major": not own,
         "palace.khi.cat_tp": 0, "palace.khi.sat_tp": 0, "palace.is_than": False, "palace.rel.nhi_hop_stars": [], "palace.rel.nhi_hop_hoa": []}
    for k, v in (dg or {}).items():
        p["palace.dignity." + k] = v
    p.update(kw)
    return p


def fired(p, chart=None):
    base = {"chart": {"chart.system": "tu_vi", **(chart or {})}, "palace:" + p["palace.name"]: p}
    return {(f.claim, f.effect) for f in engine.run(RULES, SOURCES, base, system="tu_vi").findings}


def test_pack_valid():
    assert validate_pack(RULES, SOURCES, {"palace.*", "chart.*", "bazi.*", "derived.*"}) == []
    assert sum(r.id.startswith("TV_TH_CACH_") for r in RULES) == 64


def test_named_patterns_follow_branch_conditions():
    assert ("cach_tham_vu_dong_hanh", "support") in fired(pal(branch="Sửu", own=["Tham Lang", "Vũ Khúc"]))
    assert ("cach_tham_vu_dong_hanh", "support") not in fired(pal(branch="Dần", own=["Tham Lang", "Vũ Khúc"]))
    assert ("cach_nhat_le_trung_thien", "support") in fired(pal(branch="Ngọ", own=["Thái Dương"]))
    assert ("cach_nhat_le_trung_thien", "support") not in fired(pal(branch="Mão", own=["Thái Dương"]))
    assert ("cach_thien_at_quy_nhan", "support") in fired(pal(own=["Thiên Khôi"], opp=["Thiên Việt"]))
    assert ("cach_thien_at_quy_nhan", "support") not in fired(pal(own=["Thiên Khôi"], opp=["Thiên Khôi"]))


def test_pha_quan_ty_ngo_emits_both_sides():
    c = fired(pal(branch="Tý", own=["Phá Quân"]))
    assert ("cach_pha_quan_ty_ngo_hoanh_phat", "support") in c and ("cach_pha_quan_ty_ngo_hoanh_pha", "limit") in c


def test_loc_ma_only_on_the_four_palaces_and_not_on_others():
    assert ("cach_loc_ma_giao_tri", "support") in fired(pal("Quan Lộc", own=["Lộc Tồn", "Thiên Mã"]))
    assert ("cach_loc_ma_giao_tri", "support") not in fired(pal("Phụ Mẫu", own=["Lộc Tồn", "Thiên Mã"]))


def test_sinh_vuong_bai_tuyet_table_and_rescue():
    assert ("menh_tuyet_xu_phung_sinh", "support") in fired(pal(tphoa=["Hóa Khoa", "Hóa Quyền", "Hóa Lộc"]), {"chart.menh_stage_th": "tuyet"})
    c = fired(pal(), {"chart.menh_stage_th": "bai"})
    assert ("menh_bai_tuyet_dia_tham_tram", "limit") in c and ("menh_tuyet_xu_phung_sinh", "support") not in c


def test_chart_facts_from_real_chart_match_book_table():
    nb = cc.normalize(cc.BirthInput(1990, 5, 17, 8, 30, "Asia/Ho_Chi_Minh", "male"))
    ch = facts.tuvi_facts(tuvi.compute(nb))["chart"]
    assert ch["chart.birth_season"] == "hạ" and ch["chart.menh_element"] in ("Kim", "Mộc", "Thủy", "Hỏa", "Thổ")
    assert ch["chart.hour_menh_polarity"] in ("thuan_ly", "nghich_ly") and ch["chart.menh_stage_th"] in ("sinh", "vuong", "bai", "tuyet", "khac")
    assert facts.STAGE_TH["Kim"] == {"Tỵ": "sinh", "Dậu": "vuong", "Ngọ": "bai", "Dần": "tuyet"}       # TH p.74


def test_menh_verse_pack_conditions():
    assert sum(r.id.startswith("TV_TH_MV_") for r in RULES) == 45
    assert ("am_kinh_ngo_uy_hung_tuong_quan", "support") in fired(pal(branch="Ngọ", own=["Thái Âm", "Kình Dương"]))
    assert ("am_kinh_ngo_uy_hung_tuong_quan", "support") not in fired(pal(branch="Tý", own=["Thái Âm", "Kình Dương"]))
    c = fired(pal(branch="Thìn", own=["Tham Lang", "Hỏa Tinh"]))
    assert ("tu_mo_hoa_linh_tham_vu_uy_quyen", "support") in c
    c = fired(pal(branch="Thìn", own=["Tham Lang", "Hỏa Tinh"], tp=["Kình Dương"]))
    assert ("tu_mo_hoa_linh_tham_vu_uy_quyen", "support") not in c          # 'chớ ngộ Kình Dương' exception
    c = fired(pal(branch="Ngọ", own=["Tử Vi"]), {"chart.year_stem": "Đinh"})
    assert ("tu_vi_ngo_dinh_ky_tam_cong", "support") in c and ("tu_vi_ngo_at_giap_kha_mong", "support") not in c
