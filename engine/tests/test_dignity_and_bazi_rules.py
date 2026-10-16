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
