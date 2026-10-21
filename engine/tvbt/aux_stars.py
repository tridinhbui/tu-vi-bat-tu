"""Auxiliary (phụ tinh) placements beyond the book-verified core set.

Every formula here is the commonly printed Vietnamese procedure, transcribed from general knowledge and NOT yet
checked against a cited page of a cited edition. They are therefore placed in their own group
(GROUP) and listed as review_status="unverified" in tuvi.SCHOOL_PACK["rule_review"]["aux_stars"]; the UI marks them.
Nothing here changes the verified stars, and no interpretation rule consumes these stars.

Branch indices: 0 Tý … 11 Hợi. Stems: 0 Giáp … 9 Quý. `month` is the effective lunar month (1-12), `day` the lunar day,
`hb` the birth-hour branch (Tý=0).
"""
from __future__ import annotations

GROUP = "phụ tinh (chưa đối chiếu sách)"
# Stars whose formula IS printed in the books (audit docs/audit/tuvi-calc.md TV-9; TH p.26 page image for Văn Tinh / Thiên Trù): rule -> pages
GROUP_SRC = "phụ tinh (đã đối chiếu sách)"
SOURCED = {
    "quoc_an_loc_ton_plus_8": "TH p.22 (trước Lộc Tồn 9 vị); KL p.29",
    "duong_phu_loc_ton_plus_5": "TH p.22; KL p.29",
    "thai_phu_van_khuc_plus_2": "TH p.19; KL p.27",
    "phong_cao_van_khuc_minus_2": "TH p.19; KL p.27",
    "giai_than_with_phuong_cac": "TH p.20; KL p.31",
    "van_tinh_by_year_stem": "TH p.26 (39> Văn Tinh)",
    "thien_tru_by_year_stem": "TH p.26 (37> Lưu Hà – Thiên Trù, second branch)",
}
# TH p.26: year stem -> branch
VAN_TINH = {0: 5, 1: 6, 2: 8, 3: 9, 4: 8, 5: 9, 6: 11, 7: 0, 8: 2, 9: 3}
THIEN_TRU = {0: 5, 1: 6, 2: 0, 3: 5, 4: 6, 5: 8, 6: 2, 7: 6, 8: 9, 9: 10}


def group_of(rule: str) -> str:
    return GROUP_SRC if rule in SOURCED else GROUP

# Stars the common 14+ star procedure also has but which are NOT placed here (formula not confidently known).
NOT_PLACED = [
    "Tiểu hạn/lưu niên xem ở mục Đại hạn & lưu niên; lưu Lộc Tồn, lưu Kình Đà, lưu Mã chưa được an",
]

# year stem -> branch
THIEN_QUAN = {0: 7, 1: 4, 2: 5, 3: 2, 4: 3, 5: 9, 6: 11, 7: 9, 8: 10, 9: 6}
THIEN_PHUC = {0: 9, 1: 8, 2: 0, 3: 11, 4: 3, 5: 2, 6: 6, 7: 5, 8: 6, 9: 5}
LUU_HA = {0: 9, 1: 10, 2: 7, 3: 8, 4: 5, 5: 6, 6: 4, 7: 3, 8: 11, 9: 2}
# year-branch season group (Hợi Tý Sửu / Dần Mão Thìn / Tỵ Ngọ Mùi / Thân Dậu Tuất) -> Cô Thần, Quả Tú
CO_THAN = [2, 5, 8, 11]
QUA_TU = [10, 1, 4, 7]
# triad group of year branch (0 Dần Ngọ Tuất, 1 Thân Tý Thìn, 2 Tỵ Dậu Sửu, 3 Hợi Mão Mùi)
TRIAD = {2: 0, 6: 0, 10: 0, 8: 1, 0: 1, 4: 1, 5: 2, 9: 2, 1: 2, 11: 3, 3: 3, 7: 3}
HOA_CAI = {0: 10, 1: 4, 2: 1, 3: 7}
KIEP_SAT = {0: 11, 1: 5, 2: 2, 3: 8}


def place(*, ys: int, yb: int, month: int, day: int, hb: int, menh: int, than: int, placed: dict[str, int]):
    """Yield (name, branch, rule_id)."""
    out = []
    add = lambda n, p, r: out.append((n, p % 12, r))
    add("Thiên Khốc", 6 - yb, "thien_khoc_from_ngo_back_to_year")
    add("Thiên Hư", 6 + yb, "thien_hu_from_ngo_forward_to_year")
    add("Long Trì", 4 + yb, "long_tri_from_thin_forward_to_year")
    add("Phượng Các", 10 - yb, "phuong_cac_from_tuat_back_to_year")
    add("Giải Thần", 10 - yb, "giai_than_with_phuong_cac")
    add("Văn Tinh", VAN_TINH[ys], "van_tinh_by_year_stem")
    add("Thiên Trù", THIEN_TRU[ys], "thien_tru_by_year_stem")
    if "Lộc Tồn" in placed:
        add("Quốc Ấn", placed["Lộc Tồn"] + 8, "quoc_an_loc_ton_plus_8")
        add("Đường Phù", placed["Lộc Tồn"] + 5, "duong_phu_loc_ton_plus_5")
    if "Văn Khúc" in placed:
        add("Thai Phụ", placed["Văn Khúc"] + 2, "thai_phu_van_khuc_plus_2")
        add("Phong Cáo", placed["Văn Khúc"] - 2, "phong_cao_van_khuc_minus_2")
    g = (yb + 1) // 3 % 4
    add("Cô Thần", CO_THAN[g], "co_than_by_season_of_year_branch")
    add("Quả Tú", QUA_TU[g], "qua_tu_by_season_of_year_branch")
    add("Thiên Quan", THIEN_QUAN[ys], "thien_quan_by_year_stem")
    add("Thiên Phúc", THIEN_PHUC[ys], "thien_phuc_by_year_stem")
    add("Thiên Thọ", than + yb, "thien_tho_from_than_forward_to_year")
    add("Thiên Tài", menh + yb, "thien_tai_from_menh_forward_to_year")
    add("Thiên Thương", menh + 5, "thien_thuong_at_no_boc")
    add("Thiên Sứ", menh + 7, "thien_su_at_tat_ach")
    add("Thiên La", 4, "thien_la_fixed_thin")
    add("Địa Võng", 10, "dia_vong_fixed_tuat")
    add("Thiên Hình", 9 + month - 1, "thien_hinh_from_dau_by_month")
    add("Thiên Riêu", 1 + month - 1, "thien_rieu_from_suu_by_month")
    add("Thiên Y", 1 + month - 1, "thien_y_with_thien_rieu")
    add("Thiên Giải", 8 + month - 1, "thien_giai_from_than_by_month")
    add("Địa Giải", 7 + month - 1, "dia_giai_from_mui_by_month")
    add("Đẩu Quân", yb - (month - 1) + hb, "dau_quan_year_back_month_forward_hour")
    t = TRIAD[yb]
    add("Hoa Cái", HOA_CAI[t], "hoa_cai_by_year_triad")
    add("Kiếp Sát", KIEP_SAT[t], "kiep_sat_by_year_triad")
    add("Phá Toái", 5 if yb in (0, 6, 3, 9) else 9 if yb in (2, 8, 5, 11) else 1, "pha_toai_by_year_branch")
    add("Lưu Hà", LUU_HA[ys], "luu_ha_by_year_stem")
    add("Thiên Đức", 9 + yb, "thien_duc_from_dau_forward_to_year")
    add("Nguyệt Đức", 5 + yb, "nguyet_duc_from_ty_forward_to_year")
    if "Tả Phụ" in placed:
        add("Tam Thai", placed["Tả Phụ"] + day - 1, "tam_thai_from_ta_phu_by_day")
        add("Bát Tọa", placed["Hữu Bật"] - (day - 1), "bat_toa_from_huu_bat_by_day")
        add("Ân Quang", placed["Văn Xương"] + day - 2, "an_quang_from_van_xuong_by_day")
        # KL p.28 / TH p.19: from Văn Khúc as day 1 count NGHỊCH to the birth day, then step back one palace (audit TV-1: was counted thuận)
        add("Thiên Quý", placed["Văn Khúc"] - (day - 2), "thien_quy_from_van_khuc_back_by_day")
    return out
