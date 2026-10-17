"""Full-table and population checks for the 八字真宗 羊刃 / 驿马 / 文昌 facts, against an independent oracle written from the printed Han strings.
Rules under test: 驿马 is taken from the DAY branch (p.73, rows 日支 → 马星), 文昌 from the YEAR stem (p.56, 生年干), 羊刃 from the DAY stem (p.72).
No school variants are mixed: e.g. 驿马 by year branch and 文昌 by day stem are explicitly shown to give different answers on some charts."""
import dataclasses
import random

import pytest

from tvbt import bazi, calendar_core as cc
from tvbt.ganzhi import BRANCHES_HAN, BRANCHES_VI, STEMS_HAN
from tvbt.knowledge.loader import load_all
from tvbt.knowledge.schema import validate_pack
from tvbt.reasoning import engine, facts

RULES, SOURCES = load_all()
B = lambda ch: BRANCHES_HAN.index(ch)
# literal strings copied from the manual (pp.72, 73, 56)
REN_ROW = dict(zip("甲乙丙丁戊己庚辛壬癸", "卯寅午巳午巳酉申子亥"))
LU_ROW = dict(zip("甲乙丙丁戊己庚辛壬癸", "寅卯巳午巳午申酉亥子"))
MA_GROUPS = {"寅午戌": "申", "申子辰": "寅", "巳酉丑": "亥", "亥卯未": "巳"}
WEN_ROW = dict(zip("甲乙丙丁戊己庚辛壬癸", "巳午申酉申酉亥子寅卯"))


def test_full_tables_equal_the_printed_rows():
    assert facts.ZZ_REN == [B(REN_ROW[s]) for s in STEMS_HAN]
    assert facts.ZZ_LU == [B(LU_ROW[s]) for s in STEMS_HAN]
    assert facts.ZZ_WEN == [B(WEN_ROW[s]) for s in STEMS_HAN]
    assert {b: facts.ZZ_MA[b] for b in range(12)} == {B(d): B(m) for grp, m in MA_GROUPS.items() for d in grp}
    assert len(facts.ZZ_MA) == 12 and set(facts.ZZ_MA.values()) == {B(c) for c in "申寅亥巳"}


def test_ren_equals_lu_plus_one_for_yang_stems_and_is_the_printed_yin_exception():
    # yang stems: 刃 is the branch after 禄 (甲 寅→卯); the manual prints yin stems differently (乙 刃寅 = 乙's own 禄 is 卯, 刃 is the branch before)
    for i, s in enumerate(STEMS_HAN):
        d = (facts.ZZ_REN[i] - facts.ZZ_LU[i]) % 12
        assert d == (1 if i % 2 == 0 else 11)


def chart_set(n=500, seed=11):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        y, m, d, h = rnd.randint(1925, 2035), rnd.randint(1, 12), rnd.randint(1, 28), rnd.randint(0, 23)
        out.append(bazi.compute(cc.normalize(cc.BirthInput(y, m, d, h, 0, "Asia/Ho_Chi_Minh", rnd.choice(["male", "female"])))))
    return out


CHARTS = chart_set()


def oracle(bz):
    """Independent re-derivation from the Han rows, using only pillar stems/branches, the relation lists and the void branches."""
    P = bz.pillars
    dstem = STEMS_HAN[P["day"].stem]
    dbr = BRANCHES_HAN[P["day"].branch]
    others = [BRANCHES_HAN[P[k].branch] for k in ("year", "month", "hour")]
    ren = REN_ROW[dstem]
    ma = next(m for grp, m in MA_GROUPS.items() if dbr in grp)
    wen = WEN_ROW[STEMS_HAN[P["year"].stem]]
    tmm = [bz.extras[k].split()[1] for k in ("thai_yuan", "ming_gong", "shen_gong")]
    tmm_han = [BRANCHES_HAN[BRANCHES_VI.index(x)] for x in tmm]
    void = {BRANCHES_HAN[BRANCHES_VI.index(x)] for x in bz.extras["kong_wang_day"]}
    pairs = lambda key: [{BRANCHES_HAN[b] for b in r["branches"]} for r in bz.relations[key]]
    comb, clash = pairs("branch_six_combine"), pairs("branch_clash")
    return {"bazi.ren_count": sum(1 for b in others + [dbr] if b == ren), "bazi.ren_in_tmm": ren in tmm_han,
            "bazi.ren_combined": any(ren in p for p in comb),
            "bazi.ma_in_chart": ma in others, "bazi.ma_in_hour": BRANCHES_HAN[P["hour"].branch] == ma,
            "bazi.ma_void": ma in void and ma in others, "bazi.ma_clashed": any(ma in p for p in clash),
            "bazi.ma_combined": ma in others and any(ma in p for p in comb),
            "bazi.wen_chang_in_chart": wen in others + [dbr] + tmm_han}


def test_hurt_facts_handle_every_relation_shape_including_three_branch_penalties():
    triple = pair = 0
    for bz in CHARTS:
        f = facts.bazi_facts(bz, zz=True)["chart"]
        for who in ("month", "day"):
            b = bz.pillars[who].branch
            other = [bz.pillars[k].branch for k in bz.pillars if k != who]
            pair_hit = any(frozenset((b, o)) in tbl for o in other for tbl in (bazi.SIX_CLASH, bazi.HARM, bazi.DESTROY))
            tri_hit = any(b in r.get("branches", []) for r in bz.relations["branch_penalty"] if "pillars" not in r)
            if tri_hit:
                triple += 1
            if pair_hit or tri_hit:
                assert f[f"bazi.{who}_branch_hurt"] is True
                pair += 1
    assert triple > 0 and pair > 50           # both the pair shape and the triple shape occur in the sample


def test_population_matches_oracle_and_covers_both_outcomes():
    seen = {k: set() for k in oracle(CHARTS[0])}
    for bz in CHARTS:
        want, got = oracle(bz), facts.bazi_facts(bz, zz=True)["chart"]
        for k, v in want.items():
            assert got[k] == v, (k, bz.pillars["day"].name, got[k], v)
            seen[k].add(v if isinstance(v, bool) else min(v, 1))
    for k, outcomes in seen.items():                       # every fact takes both values somewhere in the sample (no dead branch)
        assert outcomes == {True, False} or outcomes == {0, 1}, (k, outcomes)


def test_ma_uses_day_branch_and_wen_uses_year_stem_not_the_variants():
    differ_ma = differ_wen = 0
    for bz in CHARTS:
        P = bz.pillars
        by_day = facts.ZZ_MA[P["day"].branch]
        by_year = facts.ZZ_MA[P["year"].branch]                      # the school variant that must NOT be used
        others = [P[k].branch for k in ("year", "month", "hour")]
        got = facts.bazi_facts(bz, zz=True)["chart"]["bazi.ma_in_chart"]
        assert got == (by_day in others)
        if (by_day in others) != (by_year in others):
            differ_ma += 1
        by_day_stem = facts.ZZ_WEN[P["day"].stem]                     # variant: 文昌 by day stem (must NOT be used)
        tmm = [BRANCHES_VI.index(bz.extras[k].split()[1]) for k in ("thai_yuan", "ming_gong", "shen_gong")]
        pool = others + [P["day"].branch] + tmm
        got_w = facts.bazi_facts(bz, zz=True)["chart"]["bazi.wen_chang_in_chart"]
        assert got_w == (facts.ZZ_WEN[P["year"].stem] in pool)
        if (facts.ZZ_WEN[P["year"].stem] in pool) != (by_day_stem in pool):
            differ_wen += 1
    assert differ_ma > 20 and differ_wen > 20                         # the variants really differ, so the assertions above are meaningful


def test_zz_flag_off_means_no_zz_rule_can_fire():
    zz_claims = {c["claim"] for r in RULES if r.id.startswith("BT_ZZ_DIRECT_") for c in r.consequences}
    for bz in CHARTS[:60]:
        base = facts.bazi_facts(bz)                                   # default: what production uses until the API is wired
        assert not any(k.startswith(("bazi.hour_stem", "bazi.month_main", "bazi.ren_", "bazi.ma_", "bazi.wen_")) for k in base["chart"])
        got = {f.claim for f in engine.run(RULES, SOURCES, base, system="bat_tu").findings}
        assert not (got & zz_claims)
        got_on = {f.claim for f in engine.run(RULES, SOURCES, facts.bazi_facts(bz, zz=True), system="bat_tu").findings}
        assert got_on & zz_claims                                     # and with the flag the same chart does get zz findings


def test_pack_loads_validates_and_every_condition_fact_is_produced():
    zz = [r for r in RULES if r.id.startswith("BT_ZZ_DIRECT_")]
    assert len(zz) == 49 and validate_pack(zz, SOURCES, {"bazi.*", "chart.*"}) == []
    produced = set(facts.bazi_facts(CHARTS[0], zz=True)["chart"])
    def leaves(c):
        if isinstance(c, dict):
            if "fact" in c:
                yield c["fact"]
            for v in c.values():
                yield from leaves(v) if isinstance(v, (dict, list)) else ()
        elif isinstance(c, list):
            for x in c:
                yield from leaves(x)
    for r in zz:
        for f in leaves(r.conditions):
            assert f in produced, (r.id, f)
        assert r.sourceIds == ["SRC_BAZI_ZHENZONG"] and r.reviewStatus in ("verified", "draft") and "[PDF p." in r.description


def test_unverified_rules_stay_draft():
    draft = {r.id for r in RULES if r.id.startswith("BT_ZZ_DIRECT_") and r.reviewStatus == "draft"}
    for rid in ("BT_ZZ_DIRECT_HOUR_STEM_GIAP", "BT_ZZ_DIRECT_S_PURE_YIN_M", "BT_ZZ_DIRECT_S_PURE_YANG_F", "BT_ZZ_DIRECT_S_TMM_YIN_M", "BT_ZZ_DIRECT_S_TMM_YANG_F"):
        assert rid in draft


def test_api_integration_when_wired():
    import inspect
    from fastapi.testclient import TestClient
    from tvbt import api
    if "zz=True" not in inspect.getsource(api):
        pytest.skip("api.py does not yet pass zz=True: the 49 rules stay pending in the API (integration point: the two facts.bazi_facts(bz) call sites)")
    r = TestClient(api.app).post("/api/reasoning", json={"year": 1990, "month": 5, "day": 17, "hour": 8, "minute": 0, "tz": "Asia/Ho_Chi_Minh", "gender": "male"})
    assert r.status_code == 200 and r.json()["pack_problems"] == []
    claims = {f["claim"] for f in r.json()["systems"]["bat_tu"]["findings"]}
    assert any(c.startswith("bt_zz_") for c in claims)


def test_gender_fact_is_recovered_from_the_chart_and_character_rules_are_reachable():
    rnd = random.Random(5)
    fired = set()
    for _ in range(400):
        g = rnd.choice(["male", "female"])
        bz = bazi.compute(cc.normalize(cc.BirthInput(rnd.randint(1925, 2035), rnd.randint(1, 12), rnd.randint(1, 28), rnd.randint(0, 23), 0, "Asia/Ho_Chi_Minh", g)))
        f = facts.bazi_facts(bz, zz=True)
        assert f["chart"]["chart.gender"] == ("nam" if g == "male" else "nữ")
        fired |= {x.claim for x in engine.run(RULES, SOURCES, f, system="bat_tu").findings}
    zz = {c["claim"] for r in RULES if r.id.startswith("BT_ZZ_DIRECT_") for c in r.consequences}
    assert len(fired & zz) >= 40, sorted(zz - fired)       # nearly every rule fires on some chart; the rest are the rare pure-polarity cases
    assert not (zz - fired - {"bt_zz_nam_thuan_am_mem_yeu", "bt_zz_nu_thuan_duong_cuong", "bt_zz_nam_thai_than_menh_am", "bt_zz_nu_thai_than_menh_duong", "bt_zz_dan_than_giap_buon_ban", "bt_zz_nhan_sat_an_cung_hien_qui", "bt_zz_ma_khong_vong_kem_thanh_tuu"}), sorted(zz - fired)
