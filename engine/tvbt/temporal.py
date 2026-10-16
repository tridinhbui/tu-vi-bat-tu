"""Temporal facts: Bát Tự lưu niên/đại vận interactions and Tử Vi đại hạn/lưu niên. FACTS only —
no event predictions. Natal data is never recomputed per year (pure functions over a finished chart)."""
from __future__ import annotations

from .bazi import BaziChart, HARM, DESTROY, SIX_CLASH, SIX_COMBINE, STEM_CLASH, STEM_COMBINE, ten_god
from .ganzhi import BRANCHES_VI, STEMS_VI, from_cycle, gz_name, year_cycle_index
from .tuvi import TU_HOA, TuViChart


def annual_pillar(year: int) -> tuple[int, int]:
    """Lưu niên pillar for a BaZi (Lập Xuân-based) year number."""
    return from_cycle(year_cycle_index(year))


def _rel_with_natal(chart: BaziChart, stem: int, branch: int, label: str) -> list[dict]:
    out = []
    for k, p in chart.pillars.items():
        pb, ps = frozenset((branch, p.branch)), frozenset((stem, p.stem))
        for name, tbl in [("lục hợp", SIX_COMBINE), ("xung", SIX_CLASH), ("hại", HARM), ("phá", DESTROY)]:
            if pb in tbl:
                out.append({"with": k, "kind": f"chi_{name}", "from": label})
        if ps in STEM_COMBINE:
            out.append({"with": k, "kind": "can_hợp", "from": label, "transforms": None})
        if ps in STEM_CLASH:
            out.append({"with": k, "kind": "can_xung", "from": label})
    return out


def bazi_months(chart: BaziChart, year: int) -> list[dict]:
    """Lưu nguyệt: the 12 monthly pillars of a BaZi year (Dần month to Sửu month), by ngũ hổ độn from the annual stem (八字真宗 p.20).
    Month boundaries are the jie, so each entry names its jie rather than a Gregorian month."""
    from .ganzhi import tiger_month_stem
    ys, _ = annual_pillar(year)
    jie_names = ["Lập Xuân", "Kinh Trập", "Thanh Minh", "Lập Hạ", "Mang Chủng", "Tiểu Thử", "Lập Thu", "Bạch Lộ", "Hàn Lộ", "Lập Đông", "Đại Tuyết", "Tiểu Hàn"]
    out = []
    for i in range(12):
        br = (2 + i) % 12
        st = (tiger_month_stem(ys) + i) % 10
        out.append({"jie": jie_names[i], "pillar": gz_name(st, br), "ten_god": ten_god(chart.day_master, st),
                    "vs_natal": _rel_with_natal(chart, st, br, "lưu nguyệt")})
    return out


def bazi_year(chart: BaziChart, birth_year: int, year: int) -> dict:
    age = year - birth_year
    luck = None
    for lp in chart.luck_pillars:
        if lp.start_age <= age < lp.start_age + 10:
            luck = lp
    s, b = annual_pillar(year)
    dm = chart.day_master
    return {
        "year": year, "age": age, "annual_pillar": gz_name(s, b), "annual_stem_ten_god": ten_god(dm, s),
        "luck_pillar": luck.name if luck else None,
        "luck_stem_ten_god": luck.ten_god if luck else None,
        "annual_vs_natal": _rel_with_natal(chart, s, b, "lưu niên"),
        "luck_vs_natal": _rel_with_natal(chart, luck.stem, luck.branch, "đại vận") if luck else [],
        "months": bazi_months(chart, year),
        "luck_vs_annual_clash": bool(luck and frozenset((luck.branch, b)) in SIX_CLASH),
        "scope": "temporal",
    }


def tuvi_year(chart: TuViChart, year: int) -> dict:
    age = year - chart.lunar["year"] + 1  # tuổi mụ
    dh = next((d for d in chart.dai_han if d["age_from"] <= age <= d["age_to"]), None)
    s, b = annual_pillar(year)
    by_branch = {p["branch"]: p for p in chart.palaces}
    tt = by_branch[BRANCHES_VI[b]]
    hoa = {}
    for k, star in zip(["Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"], TU_HOA[s]):
        pal = next((p["name"] for p in chart.palaces if star in p["stars"]), None)
        hoa[k] = {"star": star, "natal_palace": pal}
    # tiểu hạn (SRC_THUC_HANH p.27): age 1 sits at Thìn/Tuất/Mùi/Sửu for Dần-Ngọ-Tuất / Thân-Tý-Thìn / Tỵ-Dậu-Sửu / Hợi-Mão-Mùi births
    from .tuvi import TRIAD_GROUP
    start = {0: 4, 1: 10, 2: 7, 3: 1}[TRIAD_GROUP[from_cycle(year_cycle_index(chart.lunar["year"]))[1]]]
    male = chart.yin_yang_gender.endswith("nam")
    th = (start + (age - 1) * (1 if male else -1)) % 12
    from . import van_han
    import json as _json
    from pathlib import Path as _Path
    data = _json.loads((_Path(__file__).resolve().parent.parent / "data" / "tu_hoa_vi.json").read_text("utf-8"))
    advice = data["by_stem"][str(s)]
    hoa_read = []
    for k, adv in zip(["Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"], advice):
        pal = hoa[k]["natal_palace"]
        spec = data.get("position_notes_by_palace", {}).get(k, {}).get(pal)
        hoa_read.append({"hoa": k, "star": adv["star"], "palace": pal, "advice": adv["advice"],
                         "position_note": spec or (data["position_notes"][k] if pal else None), "src": "Khảo Luận pp.195-197"})
    th_palace = by_branch[BRANCHES_VI[th]]["name"]
    return {
        "luu_tu_hoa_reading": hoa_read,
        "tieu_han_reading": van_han.read(chart, th_palace),
        "tieu_han_topic": van_han.DOMAIN.get(th_palace),
        "year": year, "age_tuoi_mu": age, "tieu_han_branch": BRANCHES_VI[th], "tieu_han_palace": by_branch[BRANCHES_VI[th]]["name"], "annual_pillar": gz_name(s, b),
        "dai_han": dh, "luu_thai_tue_palace": tt["name"], "luu_thai_tue_branch": tt["branch"],
        "luu_tu_hoa": hoa, "scope": "temporal",
        "note": "Tiểu hạn: age 1 by year-branch triad (Thực Hành p.27); the vận reading follows Khảo Luận pp.233-236; lưu Tứ Hóa uses the natal table and the per-stem advice of Khảo Luận pp.195-197.",
    }


def timeline(bz: BaziChart, tv: TuViChart, birth_year: int, to_age: int = 100) -> list[dict]:
    return [{"bazi": bazi_year(bz, birth_year, y), "tuvi": tuvi_year(tv, y)}
            for y in range(birth_year, birth_year + to_age + 1)]
