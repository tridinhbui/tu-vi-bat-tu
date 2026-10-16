"""Tử Vi Đẩu Số chart calculation — Vietnamese school pack "vn_tan_bien_draft".

FACTS only. Every star placement records the rule id that produced it. Rule tables transcribed
from memory of the common Vietnamese procedure are marked review_status="unverified" in
SCHOOL_PACK until checked against a cited edition. Not implemented in this phase (reported
explicitly in `unsupported`): miếu/vượng/đắc/hãm brightness, Tuần/Triệt placement nuances,
trung/tiểu tinh beyond the listed set, tiểu hạn, lưu niên.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from . import calendar_core as cc
from .ganzhi import (BRANCHES_VI, STEMS_VI, branch_stem_from_year, controls, cycle_index, from_cycle,
                     generates, gz_name, nap_am_element, nap_am_name, stem_polarity, year_cycle_index)
from .trace import Trace

LeapRule = Literal["split_15", "same_month", "next_month"]

SCHOOL_PACK = {
    "schoolId": "vn_tan_bien_draft", "version": "0.1.0",
    "leap_month_rule": "split_15 (day<=15 -> same month, >15 -> next month)",
    "tu_hoa_table": "VN (Canh: Dương Vũ Âm Đồng)",
    "khoi_viet": "verse 甲戊庚牛羊 / 乙己鼠猴鄉 / 丙丁豬雞位 / 壬癸兔蛇藏 / 六辛逢馬虎",
    "huoling_direction": "by yin-yang/gender, start by year-branch triad",
    "review_status": "unverified",
    "reviewed_by_tests": ["nap_am cross-check", "tuvi_phu_mirror", "known worked examples (see tests)"],
}

PALACES = ["Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch", "Quan Lộc", "Nô Bộc", "Thiên Di", "Tật Ách",
           "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ"]  # increasing branch index from Mệnh
CUC_BY_ELEMENT = {"Thủy": 2, "Mộc": 3, "Kim": 4, "Thổ": 5, "Hỏa": 6}
CUC_NAME = {2: "Thủy nhị cục", 3: "Mộc tam cục", 4: "Kim tứ cục", 5: "Thổ ngũ cục", 6: "Hỏa lục cục"}
CUC_ELEMENT = {v: k for k, v in CUC_BY_ELEMENT.items()}

LOC_TON = {0: 2, 1: 3, 2: 5, 3: 6, 4: 5, 5: 6, 6: 8, 7: 9, 8: 11, 9: 0}
KHOI_VIET = {0: (1, 7), 4: (1, 7), 6: (1, 7), 1: (0, 8), 5: (0, 8), 2: (11, 9), 3: (11, 9),
             7: (6, 2), 8: (3, 5), 9: (3, 5)}  # stem -> (Khôi, Việt)
TU_HOA = {  # stem -> (Lộc, Quyền, Khoa, Kỵ)
    0: ("Liêm Trinh", "Phá Quân", "Vũ Khúc", "Thái Dương"),
    1: ("Thiên Cơ", "Thiên Lương", "Tử Vi", "Thái Âm"),
    2: ("Thiên Đồng", "Thiên Cơ", "Văn Xương", "Liêm Trinh"),
    3: ("Thái Âm", "Thiên Đồng", "Thiên Cơ", "Cự Môn"),
    4: ("Tham Lang", "Thái Âm", "Hữu Bật", "Thiên Cơ"),
    5: ("Vũ Khúc", "Tham Lang", "Thiên Lương", "Văn Khúc"),
    6: ("Thái Dương", "Vũ Khúc", "Thái Âm", "Thiên Đồng"),
    7: ("Cự Môn", "Thái Dương", "Văn Khúc", "Văn Xương"),
    8: ("Thiên Lương", "Tử Vi", "Tả Phụ", "Vũ Khúc"),
    9: ("Phá Quân", "Cự Môn", "Thái Âm", "Tham Lang"),
}
TRIAD_GROUP = {2: 0, 6: 0, 10: 0, 8: 1, 0: 1, 4: 1, 5: 2, 9: 2, 1: 2, 11: 3, 3: 3, 7: 3}
THAI_TUE_RING = ["Thái Tuế", "Thiếu Dương", "Tang Môn", "Thiếu Âm", "Quan Phù", "Tử Phù", "Tuế Phá",
                 "Long Đức", "Bạch Hổ", "Phúc Đức", "Điếu Khách", "Trực Phù"]
LOC_TON_RING = ["Bác Sĩ", "Lực Sĩ", "Thanh Long", "Tiểu Hao", "Tướng Quân", "Tấu Thư", "Phi Liêm",
                "Hỷ Thần", "Bệnh Phù", "Đại Hao", "Phục Binh", "Quan Phủ"]
TRUONG_SINH_RING = ["Trường Sinh", "Mộc Dục", "Quan Đới", "Lâm Quan", "Đế Vượng", "Suy", "Bệnh", "Tử",
                    "Mộ", "Tuyệt", "Thai", "Dưỡng"]
TRUONG_SINH_START = {"Thủy": 8, "Thổ": 8, "Mộc": 11, "Kim": 5, "Hỏa": 2}
HOA_START = {0: 1, 1: 2, 2: 3, 3: 9}
LINH_START = {0: 3, 1: 10, 2: 10, 3: 10}
MAJOR_NAMES = ["Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh", "Thiên Phủ",
               "Thái Âm", "Tham Lang", "Cự Môn", "Thiên Tướng", "Thiên Lương", "Thất Sát", "Phá Quân"]


@dataclass
class StarPlacement:
    name: str
    branch: int
    group: str
    rule: str


@dataclass
class TuViChart:
    year_gz: str
    lunar: dict
    effective_lunar_month: int
    menh_branch: int
    than_branch: int
    palaces: list[dict]
    cuc: dict
    menh_element: str
    menh_nap_am: str
    menh_cuc_relation: str
    yin_yang_gender: str
    dai_han_direction: str
    stars: list[StarPlacement]
    tu_hoa: dict
    tuan: list[int]
    triet: list[int]
    dai_han: list[dict]
    structure: dict
    unsupported: list[str]
    trace: Trace
    school: dict
    warnings: list[str] = field(default_factory=list)


def _m(i: int) -> int:
    return i % 12


def effective_month(lunar: cc.LunarDate, rule: LeapRule) -> tuple[int, str]:
    if not lunar.is_leap:
        return lunar.month, "non-leap month"
    if rule == "same_month":
        return lunar.month, "leap month counted as its own number"
    if rule == "next_month":
        return (lunar.month % 12) + 1, "leap month counted as next month"
    if lunar.day <= 15:
        return lunar.month, "leap month day<=15 -> same month"
    return (lunar.month % 12) + 1, "leap month day>15 -> next month"


def relation(menh_el: str, cuc_el: str) -> str:
    if menh_el == cuc_el:
        return "bình hòa (cùng hành)"
    if generates(cuc_el, menh_el):
        return "Cục sinh Mệnh"
    if generates(menh_el, cuc_el):
        return "Mệnh sinh Cục"
    if controls(cuc_el, menh_el):
        return "Cục khắc Mệnh"
    return "Mệnh khắc Cục"


def tuvi_position(day: int, cuc: int) -> tuple[int, dict]:
    x = 0
    while (day + x) % cuc:
        x += 1
    q = (day + x) // cuc
    pos = _m(2 + q - 1 + (-x if x % 2 else x))
    return pos, {"day": day, "cuc": cuc, "pad_x": x, "quotient": q,
                 "rule": "start Dần, advance quotient-1, then x back if odd else forward"}


def compute(nb: cc.NormalizedBirth, leap_rule: LeapRule = "split_15", n_dai_han: int = 12) -> TuViChart:
    tr = Trace()
    b = nb.input
    L = nb.lunar
    ycyc = year_cycle_index(L.year)
    ys, yb = from_cycle(ycyc)
    tr.add("tv.year", "Lunar-year Can Chi (Tử Vi uses the lunar year, not Lập Xuân)",
           {"lunar_year": L.year}, gz_name(ys, yb))
    month, why = effective_month(L, leap_rule)
    tr.add("tv.month", "Effective lunar month (leap-month rule)", {"lunar_month": L.month, "leap": L.is_leap,
           "day": L.day, "rule": leap_rule}, {"month": month, "why": why}, rule=leap_rule)
    hb = ((nb.clock.hour + 1) // 2) % 12
    # hour 23 under late_zi_same_day is still Tý (hb=0) of the same lunar day

    menh = _m(2 + (month - 1) - hb)
    than = _m(2 + (month - 1) + hb)
    tr.add("tv.menh_than", "Mệnh: from Dần count to month, then back by hour; Thân: forward by hour",
           {"month": month, "hour_branch": BRANCHES_VI[hb]},
           {"menh": BRANCHES_VI[menh], "than": BRANCHES_VI[than]}, rule="menh_than_standard")

    palace_by_branch = {_m(menh + i): PALACES[i] for i in range(12)}
    stems = {br: branch_stem_from_year(ys, br) for br in range(12)}
    tr.add("tv.palace_stems", "Can of each cung via ngũ hổ độn from year stem", {"year_stem": STEMS_VI[ys]},
           {BRANCHES_VI[br]: STEMS_VI[s] for br, s in stems.items()}, rule="five_tigers_rule")

    ms = stems[menh]
    me_el = nap_am_element(ms, menh)
    cuc_n = CUC_BY_ELEMENT[me_el]
    tr.add("tv.cuc", "Cục from nạp âm of the Mệnh palace Can Chi", {"menh_gz": gz_name(ms, menh)},
           {"cuc": CUC_NAME[cuc_n], "nap_am": nap_am_name(ms, menh)}, rule="nap_am_cuc")

    menh_el = nap_am_element(ys, yb)
    rel = relation(menh_el, CUC_ELEMENT[cuc_n])
    tr.add("tv.menh_cuc", "Bản mệnh (nạp âm năm sinh) vs Cục element",
           {"menh_nap_am": nap_am_name(ys, yb), "cuc_element": CUC_ELEMENT[cuc_n]}, rel)

    yy = f"{stem_polarity(ys)} {'nam' if b.gender == 'male' else 'nữ'}"
    forward = (stem_polarity(ys) == "dương") == (b.gender == "male")
    dirn = "thuận" if forward else "nghịch"
    tr.add("tv.direction", "Âm dương nam nữ -> chiều đại hạn/vòng Lộc Tồn/Trường Sinh", {"yy": yy}, dirn)
    sgn = 1 if forward else -1

    stars: list[StarPlacement] = []

    def put(name: str, pos: int, group: str, rule: str):
        stars.append(StarPlacement(name, _m(pos), group, rule))

    tv, info = tuvi_position(L.day if not (L.is_leap and leap_rule != "same_month") else L.day, cuc_n)
    tr.add("tv.tuvi_pos", "Tử Vi position from lunar day & cục", info, BRANCHES_VI[tv], rule="tuvi_pos")
    for name, off in [("Tử Vi", 0), ("Thiên Cơ", -1), ("Thái Dương", -3), ("Vũ Khúc", -4),
                      ("Thiên Đồng", -5), ("Liêm Trinh", -8)]:
        put(name, tv + off, "chính tinh (Tử Vi hệ)", "tuvi_group_counterclockwise")
    ph = _m(4 - tv)
    tr.add("tv.thienphu_pos", "Thiên Phủ mirrors Tử Vi across the Dần–Thân axis", {"tuvi": BRANCHES_VI[tv]},
           BRANCHES_VI[ph], rule="thienphu_mirror")
    for name, off in [("Thiên Phủ", 0), ("Thái Âm", 1), ("Tham Lang", 2), ("Cự Môn", 3), ("Thiên Tướng", 4),
                      ("Thiên Lương", 5), ("Thất Sát", 6), ("Phá Quân", 10)]:
        put(name, ph + off, "chính tinh (Thiên Phủ hệ)", "thienphu_group_clockwise")

    put("Tả Phụ", 4 + (month - 1), "phụ tinh", "ta_phu_by_month")
    put("Hữu Bật", 10 - (month - 1), "phụ tinh", "huu_bat_by_month")
    put("Văn Xương", 10 - hb, "phụ tinh", "van_xuong_by_hour")
    put("Văn Khúc", 4 + hb, "phụ tinh", "van_khuc_by_hour")
    lt = LOC_TON[ys]
    put("Lộc Tồn", lt, "phụ tinh", "loc_ton_by_year_stem")
    put("Kình Dương", lt + 1, "sát tinh", "kinh_duong")
    put("Đà La", lt - 1, "sát tinh", "da_la")
    for i, n in enumerate(LOC_TON_RING):
        put(n, lt + sgn * i, "vòng Lộc Tồn", "loc_ton_ring_direction_by_yinyang")
    kh, vi = KHOI_VIET[ys]
    put("Thiên Khôi", kh, "phụ tinh", "khoi_viet_verse")
    put("Thiên Việt", vi, "phụ tinh", "khoi_viet_verse")
    grp = TRIAD_GROUP[yb]
    put("Thiên Mã", {0: 8, 1: 2, 2: 11, 3: 5}[grp], "phụ tinh", "thien_ma_by_year_branch")
    put("Hỏa Tinh", HOA_START[grp] + sgn * hb, "sát tinh", "hoa_tinh_triad_hour")
    put("Linh Tinh", LINH_START[grp] + sgn * hb, "sát tinh", "linh_tinh_triad_hour")
    put("Địa Kiếp", 11 + hb, "sát tinh", "dia_kiep_by_hour")
    put("Địa Không", 11 - hb, "sát tinh", "dia_khong_by_hour")
    put("Đào Hoa", {0: 9, 1: 6, 2: 3, 3: 0}[grp], "phụ tinh", "dao_hoa_by_year_branch")
    hl = _m(3 - yb)
    put("Hồng Loan", hl, "phụ tinh", "hong_loan_by_year_branch")
    put("Thiên Hỷ", hl + 6, "phụ tinh", "thien_hy_opposite_hong_loan")
    put("Thiên Không", yb + 1, "phụ tinh", "thien_khong_year_branch_plus_1")
    for i, n in enumerate(THAI_TUE_RING):
        put(n, yb + i, "vòng Thái Tuế", "thai_tue_ring")
    ts = TRUONG_SINH_START[CUC_ELEMENT[cuc_n]]
    for i, n in enumerate(TRUONG_SINH_RING):
        put(n, ts + sgn * i, "vòng Trường Sinh", "truong_sinh_ring_by_cuc")

    # Tứ Hóa
    th = dict(zip(["Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"], TU_HOA[ys]))
    placed = {s.name: s.branch for s in stars}
    th_pos = {k: {"star": v, "branch": placed.get(v)} for k, v in th.items()}
    tr.add("tv.tu_hoa", "Tứ Hóa by year stem", {"year_stem": STEMS_VI[ys]},
           {k: f"{v['star']}@{BRANCHES_VI[v['branch']]}" for k, v in th_pos.items()}, rule="tu_hoa_vn")

    # Tuần / Triệt
    xun_start = ycyc - ycyc % 10
    sb = xun_start % 12
    tuan = [_m(sb + 10), _m(sb + 11)]
    triet = {0: (8, 9), 5: (8, 9), 1: (6, 7), 6: (6, 7), 2: (4, 5), 7: (4, 5), 3: (2, 3), 8: (2, 3),
             4: (0, 1), 9: (0, 1)}[ys]
    tr.add("tv.tuan_triet", "Tuần = the two void branches of the xun; Triệt by year stem",
           {"xun_start_branch": BRANCHES_VI[sb]},
           {"tuan": [BRANCHES_VI[x] for x in tuan], "triet": [BRANCHES_VI[x] for x in triet]},
           rule="tuan_triet_standard")

    # Đại hạn
    dh = []
    for i in range(n_dai_han):
        pb = _m(menh + sgn * i)
        dh.append({"index": i + 1, "branch": BRANCHES_VI[pb], "palace": palace_by_branch[pb],
                   "age_from": cuc_n + 10 * i, "age_to": cuc_n + 10 * i + 9,
                   "stem": STEMS_VI[stems[pb]]})
    tr.add("tv.dai_han", "Đại hạn: first decade starts at Mệnh at age = cục number; direction by yin-yang",
           {"cuc": cuc_n, "direction": dirn}, [f"{d['age_from']}-{d['age_to']} {d['palace']}" for d in dh],
           rule="dai_han_direction")

    palaces = []
    for br in range(12):
        palaces.append({
            "branch": BRANCHES_VI[br], "branch_index": br, "stem": STEMS_VI[stems[br]],
            "name": palace_by_branch[br], "is_than": br == than,
            "stars": [s.name for s in stars if s.branch == br],
            "major_stars": [s.name for s in stars if s.branch == br and s.group.startswith("chính tinh")],
            "tuan": br in tuan, "triet": br in triet,
        })
    structure = {BRANCHES_VI[br]: {
        "same": BRANCHES_VI[br], "opposite": BRANCHES_VI[_m(br + 6)],
        "tam_hop": [BRANCHES_VI[_m(br + 4)], BRANCHES_VI[_m(br + 8)]],
        "giap": [BRANCHES_VI[_m(br - 1)], BRANCHES_VI[_m(br + 1)]],
    } for br in range(12)}
    warnings = []
    if L.is_leap:
        warnings.append(f"Born in a leap lunar month; Tử Vi month depends on rule '{leap_rule}'.")
    return TuViChart(
        year_gz=gz_name(ys, yb),
        lunar={"day": L.day, "month": L.month, "year": L.year, "leap": L.is_leap},
        effective_lunar_month=month, menh_branch=menh, than_branch=than, palaces=palaces,
        cuc={"n": cuc_n, "name": CUC_NAME[cuc_n], "element": CUC_ELEMENT[cuc_n]},
        menh_element=menh_el, menh_nap_am=nap_am_name(ys, yb), menh_cuc_relation=rel,
        yin_yang_gender=yy, dai_han_direction=dirn, stars=stars, tu_hoa=th_pos, tuan=tuan, triet=list(triet),
        dai_han=dh, structure=structure,
        unsupported=["miếu/vượng/đắc/hãm brightness (no verified table yet)", "Thiên Hình/Thiên Riêu/Thiên Y",
                     "Nguyệt Đức/Thiên Đức/other minor stars", "tiểu hạn, lưu niên, lưu Tứ Hóa",
                     "Tuần/Triệt school variants", "late-Tý (23h) lunar-day edge under late_zi_same_day"],
        trace=tr, school=SCHOOL_PACK, warnings=warnings)
