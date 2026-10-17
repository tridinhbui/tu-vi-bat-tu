"""Phase 2: multi-layer time facts (bản mệnh · đại hạn · tiểu hạn · lưu Thái Tuế · lưu Tứ Hóa · đại hạn Tứ Hóa) as per-palace facts,
so the same rule engine and DSL that read the natal chart can read how the layers STACK on each palace.

FACTS only (geometry + the Tứ Hóa-by-stem table the engine already uses). No reading is made here and no event is predicted.
Layers:  natal  : Tứ Hóa of the birth-year stem                       (palace.tu_hoa, already a fact)
         đại hạn: Tứ Hóa of the STEM of the đại hạn palace (`dai_han[].stem`)
         lưu    : Tứ Hóa of the stem of the year being looked at
Which palace each hóa lands on is "the palace holding that star" in the natal chart (the usual tam hợp-school convention).
"""
from __future__ import annotations

from ..ganzhi import BRANCHES_VI, STEMS_VI, from_cycle, year_cycle_index
from ..tuvi import KHOI_VIET, LOC_TON, TRIAD_GROUP, TU_HOA, TuViChart

HOA = ("Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ")
LAYER_VI = {"natal": "bản mệnh", "dai_han": "đại hạn", "luu": "lưu niên"}


def tieu_han_branch(chart: TuViChart, age: int) -> int:
    """Tiểu hạn (SRC_THUC_HANH p.27), the same rule temporal.tuvi_year uses."""
    start = {0: 4, 1: 10, 2: 7, 3: 1}[TRIAD_GROUP[from_cycle(year_cycle_index(chart.lunar["year"]))[1]]]
    male = chart.yin_yang_gender.endswith("nam")
    return (start + (age - 1) * (1 if male else -1)) % 12


def _hoa_landing(chart: TuViChart, stem: int) -> dict[str, str | None]:
    """{'Hóa Lộc': palace name holding that star, ...} for a given stem."""
    out = {}
    for k, star in zip(HOA, TU_HOA[stem]):
        out[k] = next((p["name"] for p in chart.palaces if star in p["stars"]), None)
    return out


def luu_tinh(chart: TuViChart, year: int) -> dict[str, str]:
    """Lưu (flowing) stars of a year: {'Lưu Lộc Tồn': palace name, ...}.
    CONVENTION, not verified as a flow rule: the natal tables the engine already uses (Lộc Tồn/Kình/Đà and Khôi/Việt by stem, Thiên Mã by
    branch triad — Thực Hành pp.19-24) are applied to the stem/branch of the year being read. Lưu Xương/Khúc, lưu Hỏa/Linh etc. are NOT
    produced: no table for them has been checked."""
    ys, yb = year_cycle_index(year) % 10, year_cycle_index(year) % 12
    by_branch = {p["branch_index"]: p["name"] for p in chart.palaces}
    lt = LOC_TON[ys]
    kh, vi = KHOI_VIET[ys]
    ma = {0: 8, 1: 2, 2: 11, 3: 5}[TRIAD_GROUP[yb]]
    pos = {"Lưu Lộc Tồn": lt, "Lưu Kình Dương": (lt + 1) % 12, "Lưu Đà La": (lt - 1) % 12, "Lưu Thiên Khôi": kh, "Lưu Thiên Việt": vi, "Lưu Thiên Mã": ma}
    return {k: by_branch[v] for k, v in pos.items()}


def layered(chart: TuViChart, year: int) -> dict:
    """Pure function of (finished chart, year). Returns the layer description used by the fact builder and shown in the API."""
    age = year - chart.lunar["year"] + 1                      # tuổi mụ
    dh = next((d for d in chart.dai_han if d["age_from"] <= age <= d["age_to"]), None)
    ys = year_cycle_index(year) % 10
    yb = year_cycle_index(year) % 12
    by_branch = {p["branch_index"]: p for p in chart.palaces}
    th = by_branch[tieu_han_branch(chart, age)]["name"] if age >= 1 else None
    dh_stem = STEMS_VI.index(dh["stem"]) if dh else None
    return {
        "year": year, "age": age, "year_stem": STEMS_VI[ys],
        "dai_han": dh, "dai_han_palace": dh["palace"] if dh else None, "dai_han_stem": dh["stem"] if dh else None,
        "tieu_han_palace": th, "luu_thai_tue_palace": by_branch[yb]["name"],
        "luu_hoa": _hoa_landing(chart, ys),
        "dai_han_hoa": _hoa_landing(chart, dh_stem) if dh else {},
        "luu_tinh": luu_tinh(chart, year),
        "natal_hoa": {k: (next((p["name"] for p in chart.palaces if p["branch_index"] == v["branch"]), None)) for k, v in chart.tu_hoa.items()},
    }


def time_facts(chart: TuViChart, year: int) -> dict[str, dict]:
    """{'chart': {...}, 'palace:<name>': {...}} to merge into the natal facts (keys all start with `time.`)."""
    L = layered(chart, year)
    out: dict[str, dict] = {"chart": {"time.year": year, "time.age": L["age"], "time.year_stem": L["year_stem"],
                                      "time.has_dai_han": L["dai_han"] is not None}}
    if L["dai_han"]:
        out["chart"]["time.dai_han_stem"] = L["dai_han_stem"]
    menh = next(p for p in chart.palaces if p["name"] == "Mệnh")["branch_index"]
    tp_of_menh = {(menh + d) % 12 for d in (0, 4, 8, 6)}
    for p in chart.palaces:
        n = p["name"]
        layers = [tag for tag, pal in (("dai_han", L["dai_han_palace"]), ("tieu_han", L["tieu_han_palace"]),
                                       ("luu_thai_tue", L["luu_thai_tue_palace"])) if pal == n]
        by_layer = {"natal": [k for k in HOA if L["natal_hoa"].get(k) == n],
                    "dai_han": [k for k in HOA if L["dai_han_hoa"].get(k) == n],
                    "luu": [k for k in HOA if L["luu_hoa"].get(k) == n]}
        ky_layers = [LAYER_VI[t] for t in ("natal", "dai_han", "luu") if "Hóa Kỵ" in by_layer[t]]
        loc_layers = [LAYER_VI[t] for t in ("natal", "dai_han", "luu") if "Hóa Lộc" in by_layer[t]]
        out[f"palace:{n}"] = {
            "time.layers": layers,                              # which time-palaces coincide here
            "time.natal_hoa": by_layer["natal"], "time.dai_han_hoa": by_layer["dai_han"], "time.luu_hoa": by_layer["luu"],
            "time.ky_layers": ky_layers, "time.loc_layers": loc_layers,
            "time.hoa_layer_count": sum(len(v) for v in by_layer.values()),
            "time.luu_tinh": [k for k, pal in L["luu_tinh"].items() if pal == n],
            "time.ky_n": len(ky_layers), "time.loc_n": len(loc_layers),
            "time.in_tp_of_menh": p["branch_index"] in tp_of_menh,        # palace sits in Mệnh's tam phương tứ chính
        }
    return out
