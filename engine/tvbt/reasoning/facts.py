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


def _zz_direct_facts(c: BaziChart) -> dict:
    """八字真宗 pp.51-58 (nghề nghiệp theo trụ giờ, hôn nhân theo nguyệt lệnh / nhật chi): ten god of the month and day branch (本气 = first hidden stem),
    ten-god group of the hour stem, whether the month / day branch suffers 刑冲穿害 or is combined, and whether the month branch is 空亡."""
    rel = c.relations
    where = lambda key, who: any(who in r["pillars"].split("-") for r in rel.get(key, []))
    bad = lambda who: any(where(k, who) for k in ("branch_clash", "branch_harm", "branch_destroy", "branch_penalty")) or where("branch_self_penalty", who)
    hour, month, day = c.pillars["hour"], c.pillars["month"], c.pillars["day"]
    branches = {p.branch for p in c.pillars.values()}
    stems = {p.stem for p in c.pillars.values()}
    return {"bazi.hour_stem": STEMS_VI[hour.stem], "bazi.hour_stem_group": TEN_GOD_GROUP.get(hour.stem_ten_god or ""),
            "bazi.month_main_god": month.hidden[0]["ten_god"], "bazi.day_main_god": day.hidden[0]["ten_god"],
            "bazi.month_branch_hurt": bad("month"), "bazi.day_branch_hurt": bad("day"), "bazi.month_branch_combined": where("branch_six_combine", "month"),
            "bazi.month_branch_kong": "month" in c.extras.get("kong_wang_in_chart", []),
            "bazi.has_yin_shen_jia": {2, 8} <= branches and 0 in stems}


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
