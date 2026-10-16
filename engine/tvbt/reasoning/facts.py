"""Fact extraction: calculated charts -> flat fact dicts per subject. Only objective facts here."""
from __future__ import annotations

from ..bazi import BaziChart
from ..ganzhi import BRANCHES_VI, BRANCH_ELEMENT, ELEMENTS, STEMS_VI, STEM_ELEMENT, nap_am_name
from ..tuvi import TuViChart

FACT_NAMES = {"palace.*", "chart.*", "bazi.*", "derived.*"}  # wildcard namespaces for validation


def tuvi_facts(c: TuViChart) -> dict[str, dict]:
    by_branch = {p["branch_index"]: p for p in c.palaces}
    out: dict[str, dict] = {"chart": {"chart.system": "tu_vi", "chart.cuc": c.cuc["name"],
                                       "chart.menh_cuc_relation": c.menh_cuc_relation,
                                       "chart.menh_branch": BRANCHES_VI[c.menh_branch],
                                       "chart.tu_vi_branch": next((p["branch"] for p in c.palaces if "Tử Vi" in p["major_stars"]), None)}}
    for br, p in by_branch.items():
        tp = [br, (br + 4) % 12, (br + 8) % 12, (br + 6) % 12]
        majors = [m for t in tp for m in by_branch[t]["major_stars"]]
        stars = [m for t in tp for m in by_branch[t]["stars"]]
        out[f"palace:{p['name']}"] = {
            "palace.name": p["name"], "palace.branch": p["branch"], "palace.is_than": p["is_than"],
            "palace.own_stars": p["stars"], "palace.own_major_stars": p["major_stars"],
            **{f"palace.dignity.{k}": (v or "unspecified") for k, v in p["major_dignity"].items()},
            "palace.has_no_major": not p["major_stars"],
            "palace.tam_phuong_majors": majors, "palace.tam_phuong_stars": stars,
            "palace.tuan": p["tuan"], "palace.triet": p["triet"],
            "palace.sat_pha_tham_in_tam_phuong": all(x in majors for x in ("Thất Sát", "Phá Quân", "Tham Lang")),
            "palace.neighbor_majors": [m for t in ((br - 1) % 12, (br + 1) % 12) for m in by_branch[t]["major_stars"]],
            "palace.neighbor_stars": [m for t in ((br - 1) % 12, (br + 1) % 12) for m in by_branch[t]["stars"]],
            "palace.tam_phuong_tu_hoa": sorted({k for t in tp for k, v in c.tu_hoa.items() if v["branch"] == t}),
            "palace.tu_hoa": [k for k, v in c.tu_hoa.items() if v["branch"] == br],
        }
    return out


def bazi_facts(c: BaziChart) -> dict[str, dict]:
    dm_el = c.day_master_element
    roots = [k for k, p in c.pillars.items() if k != "day" or True
             for h in p.hidden if STEM_ELEMENT[h["stem"]] == dm_el]
    visible_el = {STEM_ELEMENT[p.stem] for p in c.pillars.values()} | {BRANCH_ELEMENT[p.branch] for p in c.pillars.values()}
    return {"chart": {"chart.system": "bat_tu", "bazi.day_master_stem": STEMS_VI[c.day_master],
                      "bazi.day_nap_am": nap_am_name(c.pillars["day"].stem, c.pillars["day"].branch),
                      "bazi.missing_elements": [e for e in ELEMENTS if e not in visible_el], "bazi.dm_element": dm_el, "bazi.dm_has_root": bool(roots),
                      "bazi.dm_root_pillars": sorted(set(roots)),
                      "bazi.month_branch": BRANCHES_VI[c.pillars["month"].branch],
                      "bazi.dm_stage_in_month": c.pillars["month"].stage_vs_day_master}}
