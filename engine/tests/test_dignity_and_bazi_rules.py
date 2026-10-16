import json

from tvbt import bazi, dignity, tuvi
from tvbt.calendar_core import BirthInput, normalize
from tvbt.knowledge.loader import DATA, load_all, load_claims
from tvbt.knowledge.schema import validate_pack
from tvbt.reasoning import engine, facts

RULES, SOURCES = load_all()
F = {"palace.*", "chart.*", "bazi.*", "derived.*"}
BR = "Tý Sửu Dần Mão Thìn Tỵ Ngọ Mùi Thân Dậu Tuất Hợi".split()


def test_packs_valid_every_claim_has_vietnamese_phrasing():
    assert validate_pack(RULES, SOURCES, F) == []
    claims = load_claims()
    used = {c["claim"] for r in RULES for c in r.consequences if c.get("kind") == "finding"}
    assert used <= set(claims), used - set(claims)


def test_dignity_table_shape_and_text_layer_crosscheck():
    t = json.loads((DATA / "dignity_vn.json").read_text("utf-8"))["stars"]
    assert len(t) == 14
    for s in t.values():
        assert set(s["levels"]) <= set(BR) and set(s["levels"].values()) <= {"miếu", "vượng", "đắc", "bình", "hãm"}
    # values read from the PDF's text layer (independent of the page-image transcription): headers like "THAM LANG miếu : Sửu, Mùi, Thìn"
    assert {b for b, v in t["Tham Lang"]["levels"].items() if v == "miếu"} >= {"Sửu", "Mùi", "Thìn"}
    assert {b for b, v in t["Thiên Tướng"]["levels"].items() if v == "miếu"} == {"Dần", "Thân"}
    assert {b for b, v in t["Thiên Lương"]["levels"].items() if v == "miếu"} == {"Ngọ", "Tuất", "Thìn"}
    assert dignity.dignity("Tử Vi", "Ngọ") == "miếu" and dignity.dignity("Vũ Khúc", "Mão") is None  # unspecified stays None


def run_tv(**kw):
    p = {"palace.name": "Mệnh", "palace.branch": "Tý", "palace.own_major_stars": ["Thiên Cơ"], "palace.tam_phuong_majors": ["Thiên Cơ"],
         "palace.tam_phuong_stars": ["Thiên Cơ"], "palace.tam_phuong_tu_hoa": [], "palace.own_stars": ["Thiên Cơ"]}
    p.update(kw)
    res = engine.run(RULES, SOURCES, {"chart": {}, "palace:Mệnh": p}, system="tu_vi")
    return {f.claim for f in res.findings}


def test_dignity_gated_rules():
    assert "co_tot_thong_minh_muu_tri" in run_tv(**{"palace.dignity.Thiên Cơ": "miếu"})
    assert "co_ham_kem_nhanh_van_du_an" in run_tv(**{"palace.dignity.Thiên Cơ": "hãm"})
    c = run_tv(**{"palace.dignity.Thiên Cơ": "bình"})
    assert not any(x.startswith("co_") and x.endswith(("_nhanh_van_du_an", "_muu_tri")) for x in c)
    assert "co_tot_thong_minh_muu_tri" not in run_tv(**{"palace.dignity.Thiên Cơ": "unspecified"})   # no guessing


def test_real_chart_dignity_flows_into_facts():
    c = tuvi.compute(normalize(BirthInput(1990, 5, 17, 10, 30, "Asia/Ho_Chi_Minh", "male")))
    f = facts.tuvi_facts(c)["palace:Mệnh"]       # Mệnh Tý: Vũ Khúc + Thiên Phủ (see test_tuvi)
    assert f["palace.dignity.Thiên Phủ"] == "vượng" and f["palace.dignity.Vũ Khúc"] == "unspecified"


def test_bazi_day_master_and_missing_element():
    c = bazi.compute(normalize(BirthInput(2000, 1, 1, 12, 0, "Asia/Ho_Chi_Minh", "male")))   # Kỷ Mão, Bính Tý, Mậu Ngọ, Mậu Ngọ
    f = facts.bazi_facts(c)["chart"]
    assert f["bazi.day_master_stem"] == "Mậu" and f["bazi.missing_elements"] == ["Kim"]       # hand-derived: no metal anywhere
    res = engine.run(RULES, SOURCES, facts.bazi_facts(c), system="bat_tu")
    claims = {x.claim for x in res.findings}
    assert {"bt_ri_gan_lam_thap_than_mậu", "bt_ri_gan_ngu_hanh_mậu", "bt_thieu_hanh_kim"} <= claims
    assert not any("giáp" in x or "canh" in x for x in claims)
    draft = next(x for x in res.findings if x.claim == "bt_thieu_hanh_kim")
    assert draft.basis == "draft"                                                              # operationalisation is ours


def run_palace(name, branch="Tý", own=(), majors=(), tam_majors=(), hoa=(), tam_hoa=(), tuan=False, triet=False):
    p = {"palace.name": name, "palace.branch": branch, "palace.own_stars": list(own), "palace.own_major_stars": list(majors),
         "palace.tam_phuong_majors": list(tam_majors) or list(majors), "palace.tam_phuong_stars": list(own),
         "palace.tam_phuong_tu_hoa": list(tam_hoa), "palace.tu_hoa": list(hoa), "palace.tuan": tuan, "palace.triet": triet}
    res = engine.run(RULES, SOURCES, {"chart": {}, f"palace:{name}": p}, system="tu_vi")
    return {f.claim for f in res.findings}


def test_verse_rules_palace_specific_and_literal():
    assert "thoi_tre_van_va_lo_toan" in run_palace("Mệnh", triet=True)
    assert "thoi_tre_van_va_lo_toan" not in run_palace("Phu Thê", triet=True)          # Mệnh-only
    assert "hay_lo_nghi_vien_vong" in run_palace("Mệnh", majors=["Cự Môn"], hoa=["Hóa Kỵ"])
    assert "hay_lo_nghi_vien_vong" not in run_palace("Mệnh", majors=["Cự Môn"])
    assert "de_vuong_thi_phi" in run_palace("Mệnh", branch="Tuất", majors=["Cự Môn"])
    assert "de_vuong_thi_phi" not in run_palace("Mệnh", branch="Mão", majors=["Cự Môn"])
    assert "giau_ben_sau_30_tuoi" in run_palace("Tài Bạch", majors=["Vũ Khúc", "Tham Lang"])
    assert "giau_ben_sau_30_tuoi" not in run_palace("Tài Bạch", majors=["Vũ Khúc"])
    assert "danh_den_muon" in run_palace("Thiên Di", own=["Địa Kiếp"])
    assert "quyen_quy_cong_khanh" in run_palace("Mệnh", branch="Ngọ", majors=["Tử Vi"], tam_majors=["Tử Vi", "Thiên Phủ"])
    assert "quyen_quy_cong_khanh" not in run_palace("Mệnh", branch="Tý", majors=["Tử Vi"], tam_majors=["Tử Vi", "Thiên Phủ"])
    assert "tieng_tam_van_chuong" in run_palace("Mệnh", tam_hoa=["Hóa Khoa", "Hóa Quyền", "Hóa Lộc"])
    assert "tieng_tam_van_chuong" not in run_palace("Mệnh", tam_hoa=["Hóa Khoa", "Hóa Lộc"])


def test_star_names_used_by_rules_exist_in_engine():
    chart = tuvi.compute(normalize(BirthInput(1990, 5, 17, 10, 30, "Asia/Ho_Chi_Minh", "male")))
    known = {s.name for s in chart.stars}
    for r in RULES:
        if r.id.startswith(("TV_TH_VERSE_", "TV_KL_", "TV_TH_COMBO_")):
            def walk(e):
                if "fact" in e:
                    v = e.get("value")
                    if e.get("operator") == "contains" and e["fact"] in ("palace.own_stars", "palace.own_major_stars", "palace.tam_phuong_majors", "palace.tam_phuong_stars"):
                        assert v in known, (r.id, v)
                else:
                    for x in e[next(iter(e))] if isinstance(e[next(iter(e))], list) else [e[next(iter(e))]]:
                        walk(x)
            walk(r.conditions)


def run_combo(star, level, tam_stars=(), tam_hoa=(), tuan=False, own=(), branch="Tý"):
    p = {"palace.name": "Mệnh", "palace.branch": branch, "palace.own_stars": [star, *own], "palace.own_major_stars": [star, *own],
         "palace.tam_phuong_majors": [star], "palace.tam_phuong_stars": [star, *tam_stars], "palace.tam_phuong_tu_hoa": list(tam_hoa),
         "palace.tu_hoa": [], "palace.tuan": tuan, "palace.triet": False, f"palace.dignity.{star}": level}
    res = engine.run(RULES, SOURCES, {"chart": {}, "palace:Mệnh": p}, system="tu_vi")
    return {f.claim: f.basis for f in res.findings}


def test_combo_rules_follow_the_book_conditions():
    c = run_combo("Tử Vi", "miếu", tam_stars=["Văn Xương"])
    assert c["tu_vi_cat_uy_quyen"] == "verified"
    assert "tu_vi_cat_uy_quyen" not in run_combo("Tử Vi", "bình", tam_stars=["Văn Xương"])
    assert "tu_vi_cat_uy_quyen" not in run_combo("Tử Vi", "miếu")
    assert "tu_vi_cat_uy_quyen" in run_combo("Tử Vi", "miếu", tam_hoa=["Hóa Lộc"])
    assert "co_tot_tuan_triet_ly_huong" in run_combo("Thiên Cơ", "miếu", tuan=True)
    assert "co_tot_tuan_triet_ly_huong" not in run_combo("Thiên Cơ", "hãm", tuan=True)
    assert "co_ham_tuan_triet_do_phan" in run_combo("Thiên Cơ", "hãm", tuan=True)
    assert run_combo("Vũ Khúc", "miếu", tam_stars=["Địa Kiếp"])["vu_tot_gap_kiep_sat_tien_phu_hau_ban"] == "draft"
    assert "tu_vi_tham_bi_quan" in run_combo("Tử Vi", "bình", own=["Tham Lang"], branch="Mão")
    assert "tu_vi_tham_bi_quan" not in run_combo("Tử Vi", "miếu", own=["Tham Lang"], branch="Ngọ")


def mk_palace(branch="Tý", own=(), tam=(), tam_hoa=(), tuan=False, no_major=False, dig=None, name="Mệnh"):
    majors = [s for s in own if s in tuvi.MAJOR_NAMES]
    p = {"palace.name": name, "palace.branch": branch, "palace.own_stars": list(own), "palace.own_major_stars": majors,
         "palace.tam_phuong_majors": list({*majors, *[s for s in tam if s in tuvi.MAJOR_NAMES]}), "palace.tam_phuong_stars": list({*own, *tam}),
         "palace.tam_phuong_tu_hoa": list(tam_hoa), "palace.tu_hoa": [h for h in tam_hoa if False], "palace.tuan": tuan, "palace.triet": False,
         "palace.has_no_major": no_major}
    for k, v in (dig or {}).items():
        p[f"palace.dignity.{k}"] = v
    return p


def claims_for(p, resolve=False):
    res = engine.run(RULES, SOURCES, {"chart": {}, f"palace:{p['palace.name']}": p}, system="tu_vi")
    if resolve:
        from tvbt.reasoning import conflict
        return {r["claim"]: r for r in conflict.resolve(res, RULES)}
    return {f.claim for f in res.findings}


def test_khao_luan_phu_rules():
    assert "tu_phu_phuc_loc" in claims_for(mk_palace(own=["Tử Vi", "Thiên Phủ"]))
    assert "tu_vi_ta_huu_uy_quyen" in claims_for(mk_palace(own=["Tử Vi", "Tả Phụ", "Hữu Bật"]))
    assert "tu_vi_ta_huu_uy_quyen" not in claims_for(mk_palace(own=["Tử Vi", "Tả Phụ"], tam=["Hữu Bật"]))     # đồng cung means same palace
    assert "tu_vi_thieu_phu_tro" in claims_for(mk_palace(own=["Tử Vi"]))
    assert "tu_vi_thieu_phu_tro" not in claims_for(mk_palace(own=["Tử Vi"], tam=["Tả Phụ"]))
    assert "vcd_nhat_nguyet_thong_minh" in claims_for(mk_palace(no_major=True, tam=["Thái Dương", "Thái Âm"]))
    assert "duong_ty_loc_lau_dai" in claims_for(mk_palace(branch="Tỵ", own=["Thái Dương"], tam=["Cự Môn"]))
    assert "duong_hoi_cong_danh_trac_tro" not in claims_for(mk_palace(branch="Tỵ", own=["Thái Dương"], tam=["Cự Môn"]))
    assert "tham_vu_truoc_ngheo_sau_giau" in claims_for(mk_palace(branch="Mùi", own=["Tham Lang", "Vũ Khúc"]))
    assert "tham_vu_truoc_ngheo_sau_giau" not in claims_for(mk_palace(branch="Tý", own=["Tham Lang", "Vũ Khúc"]))
    assert "vu_dac_dia_uy_quyen" in claims_for(mk_palace(own=["Vũ Khúc"], dig={"Vũ Khúc": "vượng"}))
    assert "vu_dac_dia_uy_quyen" not in claims_for(mk_palace(own=["Vũ Khúc"], dig={"Vũ Khúc": "hãm"}))
    assert "loc_ton_an_ngon_mac_dep" in claims_for(mk_palace(own=["Lộc Tồn"]))


def test_documented_limiting_rule_wins_over_general_one_and_is_traceable():
    r = claims_for(mk_palace(own=["Tử Vi", "Thiên Phủ"], tuan=True), resolve=True)["tu_phu_phuc_loc"]
    assert r["supporting"] == ["TV_KL_PHU_TU_PHU_PHUC_LOC"] and r["opposing"] == ["TV_KL_PHU_TU_PHU_TUAN_TRIET"]
    assert r["status"] == "limited" and "verified" in r["resolution"]          # the book itself says Tuần/Triệt reduces it
    r0 = claims_for(mk_palace(own=["Tử Vi", "Thiên Phủ"]), resolve=True)["tu_phu_phuc_loc"]
    assert r0["status"] == "supported" and r0["basis"] == "verified"


def test_khao_luan_phu2_rules_and_neighbor_facts():
    assert "hoa_loc_tai_loc_tot" in claims_for({**mk_palace(own=["Vũ Khúc"]), "palace.tu_hoa": ["Hóa Lộc"], "palace.branch": "Tý"})
    r = claims_for({**mk_palace(own=["Vũ Khúc"]), "palace.tu_hoa": ["Hóa Lộc"], "palace.branch": "Thìn"}, resolve=True)["hoa_loc_tai_loc_tot"]
    assert r["status"] == "limited"                               # Tứ Mộ lowers it, per the same passage
    assert "thoi_tre_van_va_lo_toan" in claims_for(mk_palace(tuan=True))                       # corroborated by a second book
    res = engine.run(RULES, SOURCES, {"chart": {}, "palace:Mệnh": mk_palace(tuan=True)}, system="tu_vi")
    assert {f.rule_id for f in res.findings if f.claim == "thoi_tre_van_va_lo_toan"} >= {"TV_KL_PHU2_TUAN_TRIET", "TV_TH_VERSE_MENH_TRIET_TUAN"}
    assert "liem_sat_giap_danh_muon" in claims_for({**mk_palace(), "palace.neighbor_majors": ["Liêm Trinh", "Thất Sát"]})
    assert "liem_sat_giap_danh_muon" not in claims_for({**mk_palace(), "palace.neighbor_majors": ["Liêm Trinh"]})
    ph = {**mk_palace(branch="Hợi", own=["Thái Âm", "Văn Khúc"], name="Phu Thê")}
    assert "phu_the_am_khuc_hoi_bat_doi_sang" in claims_for(ph)
    assert "phu_the_am_khuc_hoi_bat_doi_sang" not in claims_for({**ph, "palace.name": "Mệnh"})
    chart = tuvi.compute(normalize(BirthInput(1990, 5, 17, 10, 30, "Asia/Ho_Chi_Minh", "male")))
    f = facts.tuvi_facts(chart)["palace:Mệnh"]                    # Mệnh Tý: neighbours Hợi (Thiên Đồng) and Sửu (Thái Dương, Thái Âm)
    assert set(f["palace.neighbor_majors"]) == {"Thiên Đồng", "Thái Dương", "Thái Âm"}


def palace_run(name, **kw):
    p = mk_palace(name=name, **kw)
    p.setdefault("palace.is_than", False)
    res = engine.run(RULES, SOURCES, {"chart": {}, f"palace:{name}": p}, system="tu_vi")
    return {f.claim: f for f in res.findings}


def test_khao_luan_cung_rules():
    assert "tai_loc_ma_giao_tri" in palace_run("Tài Bạch", own=["Lộc Tồn"], tam=["Thiên Mã"])
    assert "tai_loc_ma_giao_tri" not in palace_run("Tài Bạch", own=["Lộc Tồn"])                      # needs Mã chiếu
    assert "tai_loc_ma_giao_tri" not in palace_run("Quan Lộc", own=["Lộc Tồn"], tam=["Thiên Mã"])    # palace-specific
    assert "phoi_dep_doi_hoa_thuan" in palace_run("Phu Thê", own=["Thiên Phủ"])
    assert "phoi_thai_duong_lap_gia_dinh_tre" in palace_run("Phu Thê", own=["Thái Dương"])
    assert "phoi_tuan_triet_hoan_canh_dac_biet" in palace_run("Phu Thê", tuan=True)
    assert "no_sat_vu_ban_phan_boi" in palace_run("Nô Bộc", own=["Thất Sát", "Vũ Khúc"])
    assert "no_sat_ban_tan_tam" in palace_run("Nô Bộc", own=["Thất Sát"])                              # độc thủ
    assert "no_sat_ban_tan_tam" in palace_run("Nô Bộc", own=["Thất Sát", "Tử Vi"])                     # or with Tử Vi
    assert "no_sat_ban_tan_tam" not in palace_run("Nô Bộc", own=["Thất Sát", "Vũ Khúc"])
    assert "mau_tu_vi_sat_con_khong_hop_tinh" in palace_run("Phụ Mẫu", own=["Tử Vi", "Thất Sát"])
    assert "di_vo_chinh_dieu_tha_noi" in palace_run("Thiên Di", no_major=True)
    p = {**mk_palace(name="Mệnh"), "palace.neighbor_majors": ["Thái Dương", "Thái Âm"], "palace.is_than": False}
    assert "menh_giap_nhat_nguyet_hien_dat" in {f.claim for f in engine.run(RULES, SOURCES, {"chart": {}, "palace:Mệnh": p}, system="tu_vi").findings}


def test_group_facts_chain_into_palace_rules():
    # Phúc Đức with Tử Phủ Vũ Tướng stars: group rule fires first (derived fact), then the palace rule (multi-hop)
    res = engine.run(RULES, SOURCES, {"chart": {}, "palace:Phúc Đức": {**mk_palace(name="Phúc Đức", own=["Vũ Khúc"]), "palace.is_than": False}}, system="tu_vi")
    f = next(x for x in res.findings if x.claim == "phuc_nhom_tu_phu_vu_tuong")
    assert f.depth == 2 and f.basis == "draft"


def ct_run(base_chart=None, **kw):
    p = mk_palace(**kw)
    p.setdefault("palace.is_than", False)
    res = engine.run(RULES, SOURCES, {"chart": base_chart or {}, f"palace:{p['palace.name']}": p}, system="tu_vi")
    return {f.claim for f in res.findings}


def test_khao_luan_chinh_tinh_rules():
    assert "tv_tuong_co_danh_vat_va" in ct_run(branch="Thìn", own=["Tử Vi", "Thiên Tướng"])
    assert "tv_tuong_co_danh_vat_va" not in ct_run(branch="Tý", own=["Tử Vi", "Thiên Tướng"])
    assert "vu_don_thu_giau" in ct_run(own=["Vũ Khúc"]) and "vu_don_thu_giau" not in ct_run(own=["Vũ Khúc", "Thất Sát"])
    assert "vu_tuong_doi_suon_se" in ct_run(own=["Vũ Khúc", "Thiên Tướng"])
    assert "vu_tuong_doi_suon_se" not in ct_run(own=["Vũ Khúc", "Thiên Tướng"], tuan=True)                 # the book's own exception
    assert "tuong_tuan_su_nghiep_be_tac" in ct_run(own=["Thiên Tướng"], tuan=True)
    assert "hong_don_thu_luy_tinh" in ct_run(branch="Mão", own=["Hồng Loan"])
    assert "hong_don_thu_luy_tinh" not in ct_run(branch="Mão", own=["Hồng Loan", "Đào Hoa"])
    assert "dao_hong_cung_cong_danh_tinh_cam_den_mau" in ct_run(branch="Mão", own=["Hồng Loan", "Đào Hoa"])
    assert "hong_tu_sinh_dac_cach" in ct_run(branch="Thân", own=["Hồng Loan"])
    assert "nhat_nguyet_chieu_menh_tot_dep" in ct_run(tam=["Thái Dương", "Thái Âm"])
    assert "nhat_nguyet_chieu_menh_tot_dep" not in ct_run(own=["Thái Dương", "Thái Âm"])
    # chart-level fact (Tử Vi position) gates the vô-chính-diệu readings
    base = {"chart.tu_vi_branch": "Ngọ"}
    assert "vcd_ty_ngo_thong_minh_noi_danh" in ct_run(base, branch="Sửu", no_major=True, tam=["Thái Dương", "Thái Âm"])
    assert "vcd_ty_ngo_thong_minh_noi_danh" not in ct_run({"chart.tu_vi_branch": "Thìn"}, branch="Sửu", no_major=True, tam=["Thái Dương", "Thái Âm"])
    # real chart: the fact exists
    chart = tuvi.compute(normalize(BirthInput(1990, 5, 17, 10, 30, "Asia/Ho_Chi_Minh", "male")))
    assert facts.tuvi_facts(chart)["chart"]["chart.tu_vi_branch"] == "Thìn"


def test_second_source_corroborates_and_api_merges():
    p = {**mk_palace(own=["Tử Vi", "Tả Phụ", "Hữu Bật"]), "palace.is_than": False}
    res = engine.run(RULES, SOURCES, {"chart": {"chart.year_stem": "Giáp"}, "palace:Mệnh": p}, system="tu_vi")
    srcs = {r.sourceIds[0] for r in RULES if r.id in {f.rule_id for f in res.findings if f.claim == "tu_vi_ta_huu_uy_quyen"}}
    assert srcs == {"SRC_KHAO_LUAN", "SRC_TOAN_THU"}                    # same claim, two independent books
    q = {**mk_palace(branch="Ngọ", own=["Thái Dương"]), "palace.is_than": False}
    for stem, want in (("Canh", True), ("Giáp", False)):
        r = engine.run(RULES, SOURCES, {"chart": {"chart.year_stem": stem}, "palace:Mệnh": q}, system="tu_vi")
        assert ("duong_ngo_tuoi_tot_phu_quy" in {f.claim for f in r.findings}) is want
    from fastapi.testclient import TestClient
    from tvbt.api import app
    out = TestClient(app).post("/api/reasoning", json={"year": 1990, "month": 5, "day": 17, "hour": 10, "minute": 30, "gender": "male"}).json()
    f = out["systems"]["tu_vi"]["findings"]
    keys = [(x["subject"], x["claim"], x["effect"]) for x in f]
    assert len(keys) == len(set(keys))                                   # merged: no duplicate cards


def tt_run(stem="Giáp", **kw):
    p = {**mk_palace(**kw), "palace.is_than": False}
    res = engine.run(RULES, SOURCES, {"chart": {"chart.year_stem": stem}, f"palace:{p['palace.name']}": p}, system="tu_vi")
    return {f.claim for f in res.findings}


def test_toan_thu_second_batch():
    assert "phu_tuong_ngo_tuat_giap_cao_quy" in tt_run(branch="Ngọ", own=["Thiên Phủ"], tam=["Thiên Tướng"])
    assert "phu_tuong_ngo_tuat_giap_cao_quy" not in tt_run("Canh", branch="Ngọ", own=["Thiên Phủ"], tam=["Thiên Tướng"])
    assert "phu_tuat_giap_ky_kha_gia" in tt_run("Kỷ", branch="Tuất", own=["Thiên Phủ"])
    assert "phu_tuat_giap_ky_kha_gia" not in tt_run("Kỷ", branch="Tuất", own=["Thiên Phủ"], tam=["Kình Dương"])   # Tứ Sát cancels
    assert "phu_the_am_khuc_hoi_bat_doi_sang" in tt_run(name="Phu Thê", branch="Mão", own=["Thái Âm", "Văn Khúc"])
    assert "am_ty_tuoi_binh_dinh_phu_quy" in tt_run("Đinh", branch="Tý", own=["Thái Âm"])
    assert "cu_co_mao_cong_khanh" in tt_run("Bính", branch="Mão", own=["Cự Môn", "Thiên Cơ"])
    assert "cu_co_mao_cong_khanh" not in tt_run("Giáp", branch="Mão", own=["Cự Môn", "Thiên Cơ"])
    assert "cndl_dan_than_suon_se" in tt_run(branch="Dần", tam=["Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"])
    assert "luong_thien_di_buon_ban_lon" in tt_run(name="Thiên Di", own=["Thiên Lương", "Tả Phụ"])


def test_minor_star_dignity_and_toan_thu_third_batch():
    from tvbt import dignity
    assert dignity.minor_dignity("Kình Dương", "Thìn") == "miếu" and dignity.minor_dignity("Văn Xương", "Dần") == "hãm"
    assert dignity.minor_dignity("Đà La", "Tỵ") == "bình" and dignity.minor_dignity("Hỏa Tinh", "Hợi") == "hãm"
    chart = tuvi.compute(normalize(BirthInput(1990, 5, 17, 10, 30, "Asia/Ho_Chi_Minh", "male")))
    assert any(p["minor_dignity"] for p in chart.palaces)
    assert "kinh_mieu_phu_quy_danh_vang" in tt_run(own=["Kình Dương"], dig={"Kình Dương": "miếu"})
    assert "kinh_mieu_phu_quy_danh_vang" not in tt_run(own=["Kình Dương"], dig={"Kình Dương": "hãm"})
    assert "khoa_quyen_loc_hoi_phu_quy_song_toan" in tt_run(tam_hoa=["Hóa Khoa", "Hóa Quyền", "Hóa Lộc"])
    assert "khoa_quyen_loc_hoi_phu_quy_song_toan" not in tt_run(tam_hoa=["Hóa Khoa", "Hóa Quyền"])
    assert "ta_huu_tai_quan_chieu_day_du" in tt_run(tam=["Tả Phụ", "Hữu Bật"])
    assert "ta_huu_tai_quan_chieu_day_du" not in tt_run(own=["Tả Phụ", "Hữu Bật"])
    assert "dien_loc_ton_vang_ngoc_day_nha" in tt_run(name="Điền Trạch", own=["Lộc Tồn"])
    assert "xuong_khuc_ty_hoi_quy_hoac_phu" in tt_run(branch="Hợi", own=["Văn Xương", "Văn Khúc"])
