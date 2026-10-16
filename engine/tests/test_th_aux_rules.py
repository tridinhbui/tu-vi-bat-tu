"""Thực Hành pp.50-55 auxiliary-star rules on hand-built facts."""
from tvbt.knowledge.loader import load_all
from tvbt.knowledge.schema import validate_pack
from tvbt.reasoning import engine

RULES, SOURCES = load_all()
F = {"palace.*", "chart.*", "bazi.*", "derived.*"}


def pal(name="Mệnh", branch="Dần", own=(), tp=(), hoa=(), tphoa=(), dg=None):
    p = {"palace.name": name, "palace.branch": branch, "palace.own_major_stars": [s for s in own if s in ("Vũ Khúc", "Tử Vi", "Thiên Lương", "Cự Môn")],
         "palace.tam_phuong_majors": list(tp), "palace.tam_phuong_stars": list(tp) + list(own), "palace.own_stars": list(own),
         "palace.tu_hoa": list(hoa), "palace.tam_phuong_tu_hoa": list(tphoa), "palace.neighbor_stars": [], "palace.tuan": False, "palace.triet": False,
         "palace.has_no_major": False}
    for k, v in (dg or {}).items():
        p["palace.dignity." + k] = v
    return p


def claims(p):
    res = engine.run(RULES, SOURCES, {"chart": {"chart.system": "tu_vi"}, "palace:" + p["palace.name"]: p}, system="tu_vi")
    return {(f.claim, f.effect) for f in res.findings}


def test_pack_valid():
    assert validate_pack(RULES, SOURCES, F) == []
    assert sum(r.id.startswith("TV_TH_AUX_") for r in RULES) == 43


def test_ta_huu_and_loc_pha():
    c = claims(pal(own=["Tả Phụ"]))
    assert ("ta_huu_nhan_hau_muu_tri", "support") in c
    assert ("loc_ton_pha_chieu_tien_thieu", "support") in claims(pal(own=["Lộc Tồn"], tp=["Phá Quân"]))


def rule_ids(p):
    res = engine.run(RULES, SOURCES, {"chart": {"chart.system": "tu_vi"}, "palace:" + p["palace.name"]: p}, system="tu_vi")
    return {f.rule_id for f in res.findings}


def test_hoa_loc_tu_mo_exception_tham_vu():
    rid = "TV_TH_AUX_MENH_HL_TU_MO"
    assert rid in rule_ids(pal(branch="Thìn", hoa=["Hóa Lộc"]))
    assert rid not in rule_ids(pal(branch="Thìn", hoa=["Hóa Lộc"], tp=["Tham Lang"]))


def test_dao_hong_only_in_own_palace_and_mismatch():
    assert ("quan_dao_hong_giau_sang", "support") in claims(pal("Quan Lộc", own=["Đào Hoa"]))
    assert ("quan_dao_hong_giau_sang", "support") not in claims(pal("Mệnh", own=["Đào Hoa"]))


def test_aux2_pack_branch_conditions_and_skips_harm():
    assert sum(r.id.startswith("TV_TH_AUX2_") for r in RULES) == 55
    c = claims(pal(branch="Thìn", own=["Kình Dương"]))
    assert ("kinh_dac_dia_cuong_cuong_dung_manh", "support") in c and ("kinh_cung_khac_hung_bao_lieu_linh", "support") not in c
    c = claims(pal(branch="Dần", own=["Kình Dương"]))
    assert ("kinh_cung_khac_hung_bao_lieu_linh", "support") in c
    assert ("hao_mao_dau_thong_minh_ham_choi_hoc_say", "support") in claims(pal(branch="Mão", own=["Đại Hao"]))
    assert ("khong_kiep_ham_quy_quyet_ich_ky", "support") in claims(pal(branch="Tý", own=["Địa Kiếp"]))
    assert ("khong_kiep_ham_quy_quyet_ich_ky", "support") not in claims(pal(branch="Dần", own=["Địa Kiếp"]))
    assert all("tu_vong" not in r.consequences[0].claim for r in RULES)
