"""Fact extraction: calculated charts -> flat fact dicts per subject. Only objective facts here."""
from __future__ import annotations

from ..bazi import BaziChart
from ..ganzhi import BRANCHES_VI, BRANCH_ELEMENT, ELEMENTS, STEMS_VI, STEM_ELEMENT, nap_am_name
from ..tuvi import TuViChart
from . import positions

FACT_NAMES = {"palace.*", "chart.*", "bazi.*", "derived.*"}  # wildcard namespaces for validation


# Tử Vi Thực Hành p.74: the Mệnh branch by Mệnh element -> sinh / vượng / bại / tuyệt địa.
STAGE_TH = {"Kim": {"Tỵ": "sinh", "Dậu": "vuong", "Ngọ": "bai", "Dần": "tuyet"}, "Mộc": {"Hợi": "sinh", "Mão": "vuong", "Tý": "bai", "Thân": "tuyet"},
            "Hỏa": {"Dần": "sinh", "Ngọ": "vuong", "Mão": "bai", "Hợi": "tuyet"}, "Thủy": {"Thân": "sinh", "Tý": "vuong", "Dậu": "bai", "Tỵ": "tuyet"}}
STAGE_TH["Thổ"] = STAGE_TH["Thủy"]                      # the book groups Thủy-Thổ in one row
# pp.75-76: season by lunar month; Mệnh element 'vượng' when it matches the season, 'tướng' when the season generates it.
SEASON_OF = {1: "xuân", 2: "xuân", 3: "xuân", 4: "hạ", 5: "hạ", 6: "hạ", 7: "thu", 8: "thu", 9: "thu", 10: "đông", 11: "đông", 12: "đông"}
SEASON_VUONG = {"xuân": "Mộc", "hạ": "Hỏa", "thu": "Kim", "đông": "Thủy"}
SEASON_TUONG = {"xuân": "Hỏa", "hạ": "Thổ", "thu": "Thủy", "đông": "Mộc"}
SEASON_HOURS = {"xuân": {"Dậu", "Thìn", "Tỵ"}, "hạ": {"Mão", "Mùi", "Hợi"}, "thu": {"Ngọ", "Thân", "Dần"}, "đông": {"Sửu", "Tuất", "Tý"}}
YANG_BRANCHES = {"Tý", "Dần", "Thìn", "Ngọ", "Thân", "Tuất"}


def _th_season_facts(c: TuViChart) -> dict:
    mb = BRANCHES_VI[c.menh_branch]
    yp, gd = c.yin_yang_gender.split()
    out = {"chart.gender": gd, "chart.year_polarity": yp, "chart.menh_element": c.menh_element, "chart.menh_stage_th": STAGE_TH.get(c.menh_element, {}).get(mb, "khac")}
    season = SEASON_OF.get(c.effective_lunar_month)
    hb = c.extras.get("hour_branch")
    if season:
        out["chart.birth_season"] = season
        out["chart.season_relation"] = ("vuong" if SEASON_VUONG[season] == c.menh_element else
                                        "tuong" if SEASON_TUONG[season] == c.menh_element else "khac")
        if hb is not None:
            out["chart.hour_matches_season"] = BRANCHES_VI[hb] in SEASON_HOURS[season]
    if hb is not None:
        out["chart.hour_menh_polarity"] = "thuan_ly" if (BRANCHES_VI[hb] in YANG_BRANCHES) == (mb in YANG_BRANCHES) else "nghich_ly"
    return out


def _kl_principle_facts(c: TuViChart) -> dict:
    """Khảo Luận pp.238-246 (worked examples): the year's stem-branch relation ('gốc nuôi ngọn' etc.), whether the Mệnh sits on a palace of its own
    polarity ('đắc chính') and whether sex and year polarity agree ('thuận lý')."""
    from ..ganzhi import controls, generates, stem_polarity
    s_name, b_name = c.year_gz.split()
    se, be = STEM_ELEMENT[STEMS_VI.index(s_name)], BRANCH_ELEMENT[BRANCHES_VI.index(b_name)]
    rel = ("can_sinh_chi" if generates(se, be) else "chi_sinh_can" if generates(be, se) else "can_khac_chi" if controls(se, be)
           else "chi_khac_can" if controls(be, se) else "hoa")
    yp, gd = c.yin_yang_gender.split()
    menh_yang = c.menh_branch % 2 == 0
    return {"chart.can_chi_relation": rel, "chart.menh_dac_chinh": (yp == "dương") == menh_yang,
            "chart.am_duong_ly": "thuan_ly" if (yp, gd) in (("dương", "nam"), ("âm", "nữ")) else "nghich_ly"}


def tuvi_facts(c: TuViChart) -> dict[str, dict]:
    by_branch = {p["branch_index"]: p for p in c.palaces}
    out: dict[str, dict] = {"chart": {"chart.system": "tu_vi", "chart.cuc": c.cuc["name"],
                                       "chart.menh_cuc_relation": c.menh_cuc_relation,
                                       "chart.menh_branch": BRANCHES_VI[c.menh_branch],
                                       "chart.year_stem": c.year_gz.split()[0], "chart.year_branch": c.year_gz.split()[1],
                                       "chart.tu_vi_branch": next((p["branch"] for p in c.palaces if "Tử Vi" in p["major_stars"]), None),
                                       **_th_season_facts(c), **_kl_principle_facts(c)}}
    typed = positions.typed_facts(c.palaces, c.tu_hoa)
    for br, p in by_branch.items():
        tp = [br, (br + 4) % 12, (br + 8) % 12, (br + 6) % 12]
        majors = [m for t in tp for m in by_branch[t]["major_stars"]]
        stars = [m for t in tp for m in by_branch[t]["stars"]]
        out[f"palace:{p['name']}"] = {
            "palace.name": p["name"], "palace.branch": p["branch"], "palace.is_than": p["is_than"],
            "palace.own_stars": p["stars"], "palace.own_major_stars": p["major_stars"],
            **{f"palace.dignity.{k}": (v or "unspecified") for k, v in {**p["minor_dignity"], **p["major_dignity"]}.items()},
            "palace.has_no_major": not p["major_stars"],
            "palace.tam_phuong_majors": majors, "palace.tam_phuong_stars": stars,
            "palace.tuan": p["tuan"], "palace.triet": p["triet"],
            "palace.sat_pha_tham_in_tam_phuong": all(x in majors for x in ("Thất Sát", "Phá Quân", "Tham Lang")),
            "palace.neighbor_majors": [m for t in ((br - 1) % 12, (br + 1) % 12) for m in by_branch[t]["major_stars"]],
            "palace.neighbor_stars": [m for t in ((br - 1) % 12, (br + 1) % 12) for m in by_branch[t]["stars"]],
            "palace.tam_phuong_tu_hoa": sorted({k for t in tp for k, v in c.tu_hoa.items() if v["branch"] == t}),
            "palace.tu_hoa": [k for k, v in c.tu_hoa.items() if v["branch"] == br],
            **typed[p["name"]],          # Phase 1: role-typed positions (đồng cung / tam hợp / xung chiếu / giáp), dignity_rank, counts
        }
    return out


TEN_GOD_GROUP = {"Thực Thần": "thuc_thuong", "Thương Quan": "thuc_thuong", "Thiên Ấn": "an", "Chính Ấn": "an", "Thất Sát": "quan", "Chính Quan": "quan",
                 "Thiên Tài": "tai", "Chính Tài": "tai", "Tỉ Kiên": "ty_kiep", "Kiếp Tài": "ty_kiep"}


# 八字真宗 tables, as printed. 羊刃 and 禄神 by DAY stem (p.72); 驿马 by DAY branch (p.73, 'tam hợp' groups); 文昌 by YEAR stem (p.56).
ZZ_LU = [2, 3, 5, 6, 5, 6, 8, 9, 11, 0]
ZZ_REN = [3, 2, 6, 5, 6, 5, 9, 8, 0, 11]
ZZ_MA = {2: 8, 6: 8, 10: 8, 8: 2, 0: 2, 4: 2, 5: 11, 9: 11, 1: 11, 11: 5, 3: 5, 7: 5}
ZZ_WEN = [5, 6, 8, 9, 8, 9, 11, 0, 2, 3]


def _gender_fact(c: BaziChart) -> dict:
    """chart.gender: the sex the caller supplied when it is on the chart (`extras["gender_input"]`, source 'input'); only for a chart built without it is the sex
    recovered from the luck direction (source 'inferred'). The inference is the inverse of the 起运 rule (forward for yang-male and yin-female), so it is exact for charts
    this engine built, but it is a derivation, never evidence on its own: rules that need the sex should read chart.gender_source too."""
    g = c.extras.get("gender_input")
    if g in ("male", "female"):
        return {"chart.gender": "nam" if g == "male" else "nữ", "chart.gender_source": "input"}
    yang = c.pillars["year"].stem % 2 == 0
    return {"chart.gender": "nam" if yang == (c.luck_direction == "thuận") else "nữ", "chart.gender_source": "inferred"}


def _zz_direct_facts(c: BaziChart) -> dict:
    """八字真宗 pp.51-58 (nghề nghiệp theo trụ giờ, hôn nhân theo nguyệt lệnh / nhật chi): ten god of the month and day branch (本气 = first hidden stem),
    ten-god group of the hour stem, whether the month / day branch suffers 刑冲穿害 or is combined, and whether the month branch is 空亡."""
    rel = c.relations
    # relation entries name their pillars ("year-day") except the three-branch penalties, which only list branches
    where = lambda key, who: any((who in r["pillars"].split("-")) if "pillars" in r else (c.pillars[who].branch in r.get("branches", [])) for r in rel.get(key, []))
    bad = lambda who: any(where(k, who) for k in ("branch_clash", "branch_harm", "branch_penalty")) or where("branch_self_penalty", who)      # 刑冲穿: 破 is not in the manual's list and 绝 is not modelled
    hour, month, day = c.pillars["hour"], c.pillars["month"], c.pillars["day"]
    branches = {p.branch for p in c.pillars.values()}
    stems = {p.stem for p in c.pillars.values()}
    # 透干 / 通根 (八字真宗 pp.50-53, 56): a ten god is 'transparent' when a non-day stem carries it, 'rooted' when some branch hides a stem of the same element
    hidden_el = {STEM_ELEMENT[h["stem"]] for p in c.pillars.values() for h in p.hidden}
    carried = {}
    for k, p in c.pillars.items():
        if k != "day" and p.stem_ten_god:
            carried.setdefault(p.stem_ten_god, []).append(STEM_ELEMENT[p.stem])
    transparent = lambda g: g in carried
    rooted = lambda g: any(e in hidden_el for e in carried.get(g, []))
    all_hidden_gods = {h["ten_god"] for p in c.pillars.values() for h in p.hidden} | set(carried)
    yin = lambda stem_i, br_i: stem_i % 2 == 1 and br_i % 2 == 1
    chars = [(p.stem, p.branch) for p in c.pillars.values()]
    tmm = []
    for key in ("thai_yuan", "ming_gong", "shen_gong"):
        s_n, b_n = c.extras[key].split()
        tmm.append((STEMS_VI.index(s_n), BRANCHES_VI.index(b_n)))
    # 羊刃 / 驿马 / 文昌 (八字真宗 pp.56, 72-74): tables as printed in the manual
    others = [p.branch for k, p in c.pillars.items() if k != "day"]
    tmm_b = [b for _, b in tmm]
    ren_b, ma_b = ZZ_REN[c.day_master], ZZ_MA[day.branch]
    all_pairs = [r["branches"] for r in rel.get("branch_six_combine", [])]
    clash_pairs = [r["branches"] for r in rel.get("branch_clash", [])]
    kong = {BRANCHES_VI.index(x) for x in c.extras["kong_wang_day"]}
    gods_all = all_hidden_gods
    return {"bazi.hour_stem": STEMS_VI[hour.stem], "bazi.hour_stem_group": TEN_GOD_GROUP.get(hour.stem_ten_god or ""),
            "bazi.month_main_god": month.hidden[0]["ten_god"], "bazi.day_main_god": day.hidden[0]["ten_god"],
            "bazi.month_branch_hurt": bad("month"), "bazi.day_branch_hurt": bad("day"), "bazi.month_branch_combined": where("branch_six_combine", "month"),
            "bazi.month_branch_kong": "month" in c.extras.get("kong_wang_in_chart", []),
            **_gender_fact(c),
            "bazi.has_yin_shen_jia": {2, 8} <= branches and 0 in stems,
            "bazi.ren_count": sum(1 for b in others + [day.branch] if b == ren_b), "bazi.ren_in_tmm": ren_b in tmm_b,
            "bazi.ren_combined": any(ren_b in pr for pr in all_pairs),
            "bazi.ren_sat_an_all": ("Thất Sát" in gods_all) and bool({"Chính Ấn", "Thiên Ấn"} & gods_all) and ren_b in others + [day.branch],
            "bazi.ma_in_chart": ma_b in others, "bazi.ma_in_hour": hour.branch == ma_b, "bazi.ma_void": ma_b in kong and ma_b in others,
            "bazi.ma_clashed": any(ma_b in pr for pr in clash_pairs), "bazi.ma_combined": ma_b in others and any(ma_b in pr for pr in all_pairs),
            "bazi.wen_chang_in_chart": ZZ_WEN[c.pillars["year"].stem] in others + [day.branch] + tmm_b,
            "bazi.month_stem_hurt_god": (c.pillars["month"].stem_ten_god or "") in ("Thiên Ấn", "Thương Quan", "Thất Sát"),
            "bazi.chinh_tai_tho_can": transparent("Chính Tài"), "bazi.chinh_tai_rooted": rooted("Chính Tài"),
            "bazi.thien_tai_tho_can": transparent("Thiên Tài"), "bazi.thien_tai_rooted": rooted("Thiên Tài"),
            "bazi.no_wealth_star": not ({"Chính Tài", "Thiên Tài"} & all_hidden_gods),
            "bazi.an_tho_can": transparent("Chính Ấn") or transparent("Thiên Ấn"),
            "bazi.an_rooted": rooted("Chính Ấn") or rooted("Thiên Ấn"),
            "bazi.quan_sat_both_rooted": all(transparent(g) and rooted(g) for g in ("Chính Quan", "Thất Sát")),
            "bazi.all_yin": all(x % 2 == 1 for sb in chars for x in sb), "bazi.all_yang": all(x % 2 == 0 for sb in chars for x in sb),
            "bazi.tmm_all_yin": all(x % 2 == 1 for sb in tmm for x in sb), "bazi.tmm_all_yang": all(x % 2 == 0 for sb in tmm for x in sb)}


def bazi_facts(c: BaziChart, zz: bool = False) -> dict[str, dict]:
    """zz=True adds the 八字真宗 direct-judgement facts (hour-pillar group, month/day branch ten god and state); default off so the frozen old-pipeline view is unchanged."""
    dm_el = c.day_master_element
    roots = [k for k, p in c.pillars.items() if k != "day" or True
             for h in p.hidden if STEM_ELEMENT[h["stem"]] == dm_el]
    visible_el = {STEM_ELEMENT[p.stem] for p in c.pillars.values()} | {BRANCH_ELEMENT[p.branch] for p in c.pillars.values()}
    return {"chart": {"chart.system": "bat_tu", "bazi.day_master_stem": STEMS_VI[c.day_master],
                      "bazi.day_nap_am": nap_am_name(c.pillars["day"].stem, c.pillars["day"].branch),
                      "bazi.missing_elements": [e for e in ELEMENTS if e not in visible_el], "bazi.dm_element": dm_el, "bazi.dm_has_root": bool(roots),
                      "bazi.dm_root_pillars": sorted(set(roots)),
                      "bazi.month_branch": BRANCHES_VI[c.pillars["month"].branch],
                      "bazi.dm_stage_in_month": c.pillars["month"].stage_vs_day_master, **(_zz_direct_facts(c) if zz else {})}}
