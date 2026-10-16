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
        if r.id.startswith("TV_TH_VERSE_") or r.id.startswith("TV_KL_"):
            def walk(e):
                if "fact" in e:
                    v = e.get("value")
                    if e.get("operator") == "contains" and e["fact"] in ("palace.own_stars", "palace.own_major_stars", "palace.tam_phuong_majors", "palace.tam_phuong_stars"):
                        assert v in known, (r.id, v)
                else:
                    for x in e[next(iter(e))] if isinstance(e[next(iter(e))], list) else [e[next(iter(e))]]:
                        walk(x)
            walk(r.conditions)
