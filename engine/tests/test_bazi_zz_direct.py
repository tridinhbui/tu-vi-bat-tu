"""八字真宗 pp.51-58 direct-judgement facts and rules (occupation by hour pillar, marriage by month/day branch)."""
from tvbt import bazi, calendar_core as cc
from tvbt.knowledge.loader import load_all
from tvbt.reasoning import engine, facts

RULES, SOURCES = load_all()


def run(y, m, d, h, g="male"):
    bz = bazi.compute(cc.normalize(cc.BirthInput(y, m, d, h, 0, "Asia/Ho_Chi_Minh", g)))
    f = facts.bazi_facts(bz, zz=True)
    res = engine.run(RULES, SOURCES, f, system="bat_tu")
    return f["chart"], {x.claim for x in res.findings}


def test_default_facts_are_unchanged_for_the_old_view():
    bz = bazi.compute(cc.normalize(cc.BirthInput(1990, 5, 17, 8, 30, "Asia/Ho_Chi_Minh", "male")))
    assert not any(k.startswith("bazi.hour_stem") or k.startswith("bazi.month_main") for k in facts.bazi_facts(bz)["chart"])


def test_facts_and_rules_on_a_known_chart():
    f, claims = run(1990, 5, 17, 8)          # Canh Ngọ / Tân Tỵ / Nhâm Ngọ / Giáp Thìn
    assert f["bazi.hour_stem"] == "Giáp" and f["bazi.hour_stem_group"] == "thuc_thuong"
    assert f["bazi.month_main_god"] == "Thiên Tài" and f["bazi.day_main_god"] == "Chính Tài"      # Tỵ 本气 Bính, Ngọ 本气 Đinh vs Nhâm
    # the occupation judgements (p.52) read the pillar left of the Quan pillar since DEEP-BAZI-2 (data/bazi_deep/pack_zz_kin.json); the hour-pillar
    # rules are gone from this pack
    assert not any(c.startswith("bt_zz_nghe_") for c in claims)
    assert "bt_zz_hn_nguyet_kien_tai_quan_an" in claims and "bt_zz_hn_nhat_chi_tai" in claims
    assert "bt_zz_hn_nguyet_kien_thuong_kieu_sat" not in claims




def test_transparency_root_and_polarity_facts():
    f, claims = run(1990, 5, 17, 8)
    assert f["bazi.an_tho_can"] is True                                   # Tân (Chính Ấn) on the month stem
    assert isinstance(f["bazi.an_rooted"], bool) and isinstance(f["bazi.all_yin"], bool)
    assert ("bt_zz_hoc_an_tho_can_co_can" in claims) != ("bt_zz_hoc_an_tho_hu" in claims)      # exactly one of the two education readings
    assert not f["bazi.all_yin"] and "bt_zz_nam_thuan_am_mem_yeu" not in claims




def test_blade_horse_tables_follow_the_manual_p72():
    from tvbt.ganzhi import BRANCHES_VI
    bz = bazi.compute(cc.normalize(cc.BirthInput(1990, 5, 17, 8, 0, "Asia/Ho_Chi_Minh", "male")))   # day master Nhâm, day branch Ngọ
    f = facts.bazi_facts(bz, zz=True)["chart"]
    assert f["bazi.ma_in_chart"] is False            # Ngọ day -> horse at Thân; chart branches are Ngọ Tỵ Ngọ Thìn
    assert f["bazi.ren_count"] == 0                  # Nhâm blade = Tý, none in chart
    assert f["bazi.wen_chang_in_chart"] in (True, False)
    import tvbt.reasoning.facts as fx
    assert fx.STEMS_VI[8] == "Nhâm" and BRANCHES_VI[0] == "Tý"


def test_total_rule_count():
    assert sum(r.id.startswith("BT_ZZ_DIRECT_") for r in RULES) == 29     # 20 moved to data/bazi_deep/pack_zz_kin.json (DEEP-BAZI-2)
