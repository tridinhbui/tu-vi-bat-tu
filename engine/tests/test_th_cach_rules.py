"""Thực Hành pp.72-77: named patterns, sinh/vượng/bại/tuyệt table, season/hour facts."""
from tvbt import calendar_core as cc, tuvi
from tvbt.knowledge.loader import load_all
from tvbt.knowledge.schema import validate_pack
from tvbt.reasoning import engine, facts

RULES, SOURCES = load_all()


def pal(name="Mệnh", branch="Dần", own=(), opp=(), flank=(), tp=(), tphoa=(), hoa=(), dg=None, chart=None, **kw):
    p = {"palace.name": name, "palace.branch": branch, "palace.own_stars": list(own), "palace.own_major_stars": [s for s in own if s in (
         "Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng", "Thiên Lương", "Thiên Đồng", "Thái Dương", "Thái Âm", "Cự Môn", "Thiên Cơ", "Tham Lang", "Thất Sát", "Phá Quân", "Liêm Trinh")],
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
    # each palace's rule has its own claim, so the text names the palace the rule actually read (not "ở cung Mệnh")
    assert ("cach_loc_ma_giao_tri__th_cach_quan_loc_loc_ma", "support") in fired(pal("Quan Lộc", own=["Lộc Tồn", "Thiên Mã"]))
    assert not any(c.startswith("cach_loc_ma_giao_tri") for c, _ in fired(pal("Phụ Mẫu", own=["Lộc Tồn", "Thiên Mã"])))
    from tvbt.knowledge.loader import load_claims
    cl = load_claims()
    for pal_name, cid in (("Tài Bạch", "cach_loc_ma_giao_tri__th_cach_tai_bach_loc_ma"), ("Quan Lộc", "cach_loc_ma_giao_tri__th_cach_quan_loc_loc_ma"),
                          ("Thiên Di", "cach_loc_ma_giao_tri__th_cach_thien_di_loc_ma")):
        assert pal_name in cl[cid]["label"] and "Mệnh" not in cl[cid]["label"]


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


def test_star_menh_pack_gender_and_dignity():
    assert sum(r.id.startswith("TV_TH_STAR_") for r in RULES) == 53
    male, female = {"chart.gender": "nam"}, {"chart.gender": "nữ"}
    p = pal(own=["Tham Lang"], dg={"Tham Lang": "miếu"})
    assert ("nam_tham_hao_thang_kinh_doanh", "support") in fired(p, male) and ("nam_tham_hao_thang_kinh_doanh", "support") not in fired(p, female)
    assert ("nu_tham_dam_dang_bao_ton_ghen", "support") in fired(p, female)
    ham = pal(own=["Thiên Lương"], dg={"Thiên Lương": "hãm"})
    assert ("nam_luong_ham_doi_viec_chi_huong", "limit") in fired(ham, male) and ("nam_luong_thong_minh", "support") not in fired(ham, male)
    # cát tinh condition: Vũ Khúc sáng with no cát tinh in tam phương does not get the 'hiển đạt võ nghiệp' reading
    v = pal(own=["Vũ Khúc"], dg={"Vũ Khúc": "miếu"})
    assert ("nam_vu_hien_dat_vo_nghiep", "support") not in fired(v, male)
    v["palace.khi.cat_tp"] = 1
    assert ("nam_vu_hien_dat_vo_nghiep", "support") in fired(v, male)


def test_palaces2_pack_scoped_to_palace_and_gender():
    assert sum(r.id.startswith("TV_TH_P2_") for r in RULES) == 134
    assert ("hd_tuan_triet_anh_em_it_ly_tan", "limit") in fired(pal("Huynh Đệ", tuan=True) | {"palace.tuan": True})
    assert ("hd_tuan_triet_anh_em_it_ly_tan", "limit") not in fired(pal("Mệnh") | {"palace.tuan": True})            # scoped to Huynh Đệ
    assert ("pt_vu_sat_nhieu_lan_hon_phoi", "limit") in fired(pal("Phu Thê", own=["Vũ Khúc", "Thất Sát"]))
    assert ("tai_phu_vu_cua_truyen_nhieu_doi", "support") in fired(pal("Tài Bạch", own=["Thiên Phủ", "Vũ Khúc"]))
    assert ("quan_giap_xuong_khuc_hanh_thong", "support") in fired(pal("Quan Lộc", flank=["Văn Xương", "Văn Khúc"]))
    assert ("nu_tu_vi_hien_vuong_phu", "support") in fired(pal(own=["Tử Vi"]), {"chart.gender": "nữ"})
    assert ("nu_tu_vi_hien_vuong_phu", "support") not in fired(pal(own=["Tử Vi"]), {"chart.gender": "nam"})
    # Tử Tức: dương/âm branch matters for the 'con đầu' lines
    assert ("tu_nhat_cung_duong_con_dau_trai", "support") in fired(pal("Tử Tức", branch="Ngọ", own=["Thái Dương"]))
    assert ("tu_nhat_cung_duong_con_dau_trai", "support") not in fired(pal("Tử Tức", branch="Mùi", own=["Thái Dương"]))


def test_kl_stars_pack_by_branch_and_palace():
    n = sum(r.id.startswith("TV_KL_STAR_") for r in RULES)
    assert n == 103
    assert ("kl_tu_tuong_gioi_giang_vat_va", "support") in fired(pal(branch="Thìn", own=["Tử Vi", "Thiên Tướng"]))
    assert ("kl_tu_vi_don_thu_doc_lap_doc_doan", "support") in fired(pal(branch="Tý", own=["Tử Vi"]))
    assert ("kl_tu_vi_don_thu_doc_lap_doc_doan", "support") not in fired(pal(branch="Tý", own=["Tử Vi", "Thiên Phủ"]))   # đơn thủ only
    assert ("kl_co_phuc_bac_phuc", "limit") in fired(pal("Phúc Đức", branch="Tý", own=["Thiên Cơ"]))
    assert ("kl_co_phuc_bac_phuc", "limit") not in fired(pal("Mệnh", branch="Tý", own=["Thiên Cơ"]))
    assert ("kl_nhat_ban_dem_kem_minh_man", "limit") in fired(pal(branch="Hợi", own=["Thái Dương"]))
    assert ("kl_nhat_ban_dem_kem_minh_man", "limit") not in fired(pal(branch="Ngọ", own=["Thái Dương"]))
    assert ("kl_loc_ma_giao_tri_chung_nhan_sung_ai", "support") in fired(pal(own=["Lộc Tồn"], opp=["Thiên Mã"]))
    assert ("kl_loc_ma_dao_ky_khong_kiep", "limit") in fired(pal(own=["Lộc Tồn"], opp=["Thiên Mã"], tp=["Địa Kiếp"]))


def test_toan_thu_palace_star_pack():
    assert sum(r.id.startswith("TV_TT_PAL_") for r in RULES) == 382
    assert all(r.sourceIds == ["SRC_TOAN_THU"] for r in RULES if r.id.startswith("TV_TT_PAL_"))
    c = fired(pal("Tài Bạch", own=["Vũ Khúc", "Tham Lang"]))
    assert ("tt_tai_bach_vu_khuc_with_tham_lang_p", "support") in c
    c = fired(pal("Tài Bạch", own=["Thái Âm"], dg={"Thái Âm": "hãm"}))
    assert ("tt_tai_bach_thai_am_ham_m", "limit") in c and ("tt_tai_bach_thai_am_mieu_p", "support") not in c
    assert not any(k.startswith("tt_tai_bach") for k, _ in fired(pal("Mệnh", own=["Thái Âm"])))        # palace-scoped
    assert ("tt_phu_the_thien_tuong_base_p", "support") in fired(pal("Phu Thê", own=["Thiên Tướng"]))


def test_toan_thu_phu_pack():
    assert sum(r.id.startswith("TV_TT_PHU_") for r in RULES) == 57
    c = fired(pal(branch="Mùi", own=["Thái Dương"], tp=["Thái Âm"]) | {"palace.rel.trine_majors": ["Thái Dương", "Thái Âm"]})
    assert ("tt_phu_minh_chau_hai", "support") in c
    c = fired(pal(branch="Thìn", own=["Kình Dương"]) | {"palace.has_no_major": True})
    assert ("tt_phu_vcd_sat_dac_phat_nhanh", "support") in c and ("tt_phu_vcd_sat_dac_khong_ben", "limit") in c       # one rule, two consequences
    assert ("tt_phu_vcd_sat_dac_phat_nhanh", "support") not in fired(pal(branch="Dần", own=["Kình Dương"]) | {"palace.has_no_major": True})   # Kình đắc địa only at Tứ mộ
    assert ("tt_phu_nhat_nguyet_xuong_khuc_giap_nam_qui", "support") not in fired(pal(branch="Sửu", own=["Thái Dương", "Thái Âm"], flank=["Văn Xương", "Văn Khúc"]), {"chart.gender": "nữ"})


def test_toan_thu_nu_pack_is_female_only():
    assert sum(r.id.startswith("TV_TT_NU_") for r in RULES) == 11
    p = pal(own=["Thái Dương"], dg={"Thái Dương": "miếu"})
    assert ("tt_nu_nhat_thao_vat_gioi_giang", "support") in fired(p, {"chart.gender": "nữ"})
    assert ("tt_nu_nhat_thao_vat_gioi_giang", "support") not in fired(p, {"chart.gender": "nam"})
