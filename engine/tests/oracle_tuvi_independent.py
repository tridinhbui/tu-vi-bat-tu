"""INDEPENDENT oracle for the school variants. It imports NOTHING from `tvbt`: star positions, palace geometry, Tuần/Triệt, Tứ Hóa and the
state ladder are re-derived here from the printed rules (Thực Hành pp.19-22, 31, 39; Khảo Luận pp.36, 196-197) and from the variants' own
Vietnamese labels, so a test that compares it with production cannot merely confirm production's own logic.

Source of each table (typed from the book page text, not copied from the code):
  Mệnh/Thân from month+hour; Ngũ Hổ Độn + nạp âm -> cục (the classic table); Tử Vi by day/cục; Thiên Phủ mirror (4 - Tử Vi);
  Tả/Hữu by month, Xương/Khúc by hour, Khôi/Việt TH p.19 (Canh, Tân -> Ngọ, Dần), Lộc Tồn TH p.21, Kình/Đà = Lộc ±1,
  Triệt TH p.20, Tuần by Giáp-tuần (TH p.20), Tứ Hóa TH pp.20-21 / KL p.36, p.196-197 (Nhâm-Khoa: KL says Tả Phụ, TH says Phủ -> see NHAM_KHOA),
  Thái Dương brightness TH p.31, Thái Âm brightness TH p.39.
Three-valued logic (True / False / None) is used exactly where a brightness is not printed (Thái Dương at Thân/Mùi)."""

BR = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
B = {n: i for i, n in enumerate(BR)}

MAJOR_TV = [("Tử Vi", 0), ("Thiên Cơ", -1), ("Thái Dương", -3), ("Vũ Khúc", -4), ("Thiên Đồng", -5), ("Liêm Trinh", -8)]
MAJOR_PH = [("Thiên Phủ", 0), ("Thái Âm", 1), ("Tham Lang", 2), ("Cự Môn", 3), ("Thiên Tướng", 4), ("Thiên Lương", 5), ("Thất Sát", 6), ("Phá Quân", 10)]
MAJORS = [n for n, _ in MAJOR_TV + MAJOR_PH]

DAN_STEM = {0: 2, 5: 2, 1: 4, 6: 4, 2: 6, 7: 6, 3: 8, 8: 8, 4: 0, 9: 0}           # Ngũ Hổ Độn: stem of the Dần palace by year stem
NAP_AM = [[4, 2, 6, 4, 2, 6], [2, 6, 5, 2, 6, 5], [6, 5, 3, 6, 5, 3], [5, 3, 4, 5, 3, 4], [3, 4, 2, 3, 4, 2]]   # [stem//2][branch//2] -> cục
KHOI_VIET = {0: (1, 7), 4: (1, 7), 1: (0, 8), 5: (0, 8), 2: (11, 9), 3: (11, 9), 6: (6, 2), 7: (6, 2), 8: (3, 5), 9: (3, 5)}   # TH p.19
LOC_TON = {0: 2, 1: 3, 2: 5, 3: 6, 4: 5, 5: 6, 6: 8, 7: 9, 8: 11, 9: 0}                                                      # TH p.21
TRIET = {0: (8, 9), 5: (8, 9), 1: (6, 7), 6: (6, 7), 2: (4, 5), 7: (4, 5), 3: (2, 3), 8: (2, 3), 4: (0, 1), 9: (0, 1)}      # TH p.20
NHAM_KHOA = "Tả Phụ"                                                                                                          # KL p.197; TH p.21 prints Thiên Phủ
TU_HOA = {0: ("Liêm Trinh", "Phá Quân", "Vũ Khúc", "Thái Dương"), 1: ("Thiên Cơ", "Thiên Lương", "Tử Vi", "Thái Âm"),
          2: ("Thiên Đồng", "Thiên Cơ", "Văn Xương", "Liêm Trinh"), 3: ("Thái Âm", "Thiên Đồng", "Thiên Cơ", "Cự Môn"),
          4: ("Tham Lang", "Thái Âm", "Hữu Bật", "Thiên Cơ"), 5: ("Vũ Khúc", "Tham Lang", "Thiên Lương", "Văn Khúc"),
          6: ("Thái Dương", "Vũ Khúc", "Thiên Đồng", "Thái Âm"), 7: ("Cự Môn", "Thái Dương", "Văn Khúc", "Văn Xương"),
          8: ("Thiên Lương", "Tử Vi", NHAM_KHOA, "Vũ Khúc"), 9: ("Phá Quân", "Cự Môn", "Thái Âm", "Tham Lang")}
HOA = ("Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ")
# Per-source Tứ Hóa tables (Lộc, Quyền, Khoa, Kỵ). KL = production's table. The two others differ from it ONLY on Canh and Nhâm:
#   TH: Nhâm-Khoa = Thiên Phủ (verse p.20 and prose p.21). Canh agrees with KL (Khoa Thiên Đồng, Kỵ Thái Âm).
#   TT_WS: a digitized 紫微斗數全書 verse (zh.wikisource.org/wiki/紫微斗數全書/卷二, "安祿權科忌四星變化訣"): 庚 日武陰同 (Khoa Thái Âm, Kỵ Thiên Đồng), 壬 梁紫府武.
# EXTERNAL reference, not one of the three books of the project; kept to size the effect of the disagreement, never used as default.
TU_HOA_TABLES = {}
TRIAD = {2: 0, 6: 0, 10: 0, 8: 1, 0: 1, 4: 1, 5: 2, 9: 2, 1: 2, 11: 3, 3: 3, 7: 3}
HOA_START, LINH_START = {0: 1, 1: 2, 2: 3, 3: 9}, {0: 3, 1: 10, 2: 10, 3: 10}
# brightness as rank miếu 4 / vượng 3 / đắc 2 / bình 1 / hãm 0; missing = not printed
SUN = {3: 4, 6: 3, 5: 3, 4: 3, 2: 3, 9: 1, 10: 0, 11: 0, 0: 0, 1: 0}
MOON = {11: 4, 0: 4, 1: 4, 9: 3, 10: 3, 7: 2, 8: 2, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
SAT = ("Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp")
CAT6 = ("Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt")


TU_HOA_TABLES["KL"] = TU_HOA
TU_HOA_TABLES["TH"] = {**TU_HOA, 8: ("Thiên Lương", "Tử Vi", "Thiên Phủ", "Vũ Khúc")}
TU_HOA_TABLES["TT_WS"] = {**TU_HOA, 6: ("Thái Dương", "Vũ Khúc", "Thái Âm", "Thiên Đồng"), 8: ("Thiên Lương", "Tử Vi", "Thiên Phủ", "Vũ Khúc")}


def chart(ly, lm, ld, hb, male, hoa_table="KL"):
    """lunar year (Gregorian number of the lunar year), lunar month 1-12, lunar day, hour branch 0-11, gender -> positions."""
    ys, yb = (ly - 4) % 10, (ly - 4) % 12
    menh = (2 + lm - 1 - hb) % 12
    than = (2 + lm - 1 + hb) % 12
    stem_m = (DAN_STEM[ys] + (menh - 2) % 12) % 10
    cuc = NAP_AM[stem_m // 2][menh // 2]
    x = 0
    while (ld + x) % cuc:
        x += 1
    q = (ld + x) // cuc
    tv = (2 + q - 1 + (-x if x % 2 else x)) % 12
    pos = {}
    for n, o in MAJOR_TV:
        pos[n] = (tv + o) % 12
    ph = (4 - tv) % 12
    for n, o in MAJOR_PH:
        pos[n] = (ph + o) % 12
    pos["Tả Phụ"], pos["Hữu Bật"] = (4 + lm - 1) % 12, (10 - (lm - 1)) % 12
    pos["Văn Xương"], pos["Văn Khúc"] = (10 - hb) % 12, (4 + hb) % 12
    pos["Thiên Khôi"], pos["Thiên Việt"] = KHOI_VIET[ys]
    lt = LOC_TON[ys]
    pos["Lộc Tồn"], pos["Kình Dương"], pos["Đà La"] = lt, (lt + 1) % 12, (lt - 1) % 12
    fwd = (ys % 2 == 0) == male                                           # dương nam / âm nữ go clockwise
    sgn = 1 if fwd else -1
    pos["Lực Sĩ"] = (lt + sgn) % 12
    g = TRIAD[yb]
    pos["Hỏa Tinh"] = (HOA_START[g] + sgn * hb) % 12
    pos["Linh Tinh"] = (LINH_START[g] - sgn * hb) % 12
    pos["Địa Kiếp"], pos["Địa Không"] = (11 + hb) % 12, (11 - hb) % 12
    pos["Thiên Hình"] = (9 + lm - 1) % 12
    pos["Thiên Mã"] = {0: 8, 1: 2, 2: 11, 3: 5}[g]                          # TH p.21: Dần Ngọ Tuất -> Thân; Thân Tý Thìn -> Dần; Tỵ Dậu Sửu -> Hợi; Hợi Mão Mùi -> Tỵ
    hoa_at = {}
    for tag, star in zip(HOA, TU_HOA_TABLES[hoa_table][ys]):
        hoa_at.setdefault(pos[star], set()).add(tag)
    start = (yb - ys) % 12
    tuan = {(start + 10) % 12, (start + 11) % 12}
    triet = set(TRIET[ys])
    return dict(pos=pos, menh=menh, than=than, cuc=cuc, tv=tv, hoa_at=hoa_at, tuan=tuan, triet=triet, ys=ys, yb=yb, carriers=dict(zip(HOA, TU_HOA_TABLES[hoa_table][ys])))


# ---- palace geometry -------------------------------------------------------------------------------------------------------------
def roles(c):
    m = c["menh"]
    return {"self": m, "opp": (m + 6) % 12, "trine1": (m + 4) % 12, "trine2": (m + 8) % 12, "prev": (m - 1) % 12, "next": (m + 1) % 12}


def stars_at(c, branches):
    return {s for s, p in c["pos"].items() if p in branches}


def majors_at(c, branches):
    return {s for s in stars_at(c, branches) if s in MAJORS}


def hoa_at(c, branches):
    return set().union(*[c["hoa_at"].get(b, set()) for b in branches])


def tp(c):
    r = roles(c)
    return {r["self"], r["opp"], r["trine1"], r["trine2"]}


# ---- three-valued helpers ----------------------------------------------------------------------------------------------------------
def AND(*xs):
    return False if False in xs else (None if None in xs else True)


def OR(*xs):
    return True if True in xs else (None if None in xs else False)


def rank(c, star):
    """brightness of a star standing in the tam phương; None = not printed in the book (unknown, never guessed)."""
    p = c["pos"][star]
    if p not in tp(c):
        return None
    return (SUN if star == "Thái Dương" else MOON).get(p)


def gte(r, n):
    return None if r is None else r >= n


def lte(r, n):
    return None if r is None else r <= n


# ---- variants, written from the Vietnamese labels of each condition ------------------------------------------------------------------
REGIONS = {
    "tp": lambda c: tp(c),                                                         # đồng cung + đối cung + hai tam hợp (production's reading of 'hội')
    "hoi_chieu": lambda c: tp(c) - {roles(c)["self"]},                             # everything that 'chiếu' on Mệnh, without Mệnh itself
    "doi_cung": lambda c: {roles(c)["opp"]},                                       # xung chiếu only
    "dong_cung": lambda c: {roles(c)["self"]},                                     # same palace only
    "tam_hop": lambda c: {roles(c)["trine1"], roles(c)["trine2"]},                 # the two tam hợp palaces only
}


def V(scope="tp"):
    """scope: how the rules whose SENTENCE gives no scope ('hội', 'thích', 'cần') are read; rules whose scope the page states stay fixed.
    The core always uses the tam phương (it defines the structure)."""
    reg = REGIONS[scope]
    S = lambda c, k: stars_at(c, {roles(c)[k]})
    TPS = lambda c: stars_at(c, tp(c))
    TPM = lambda c: majors_at(c, tp(c))
    TPH = lambda c: hoa_at(c, tp(c))
    RS = lambda c: stars_at(c, reg(c))
    RH = lambda c: hoa_at(c, reg(c))
    has = lambda xs, ys_: all(y in xs for y in ys_)
    anyin = lambda xs, ys_: any(y in xs for y in ys_)
    on_menh_tuan = lambda c: c["menh"] in c["tuan"] or c["menh"] in c["triet"]
    ham_sat = lambda c: AND(OR(lte(rank(c, "Thái Dương"), 0), lte(rank(c, "Thái Âm"), 0)), sum(1 for s in SAT if s in TPS(c)) >= 1)
    sang = lambda c: AND(gte(rank(c, "Thái Dương"), 2), gte(rank(c, "Thái Âm"), 2))
    four = lambda names: (lambda c: has(TPM(c), names))
    TPVT = ["Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"]
    CNDL = ["Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"]
    ALL3 = ("Hóa Khoa", "Hóa Quyền", "Hóa Lộc")
    cnt4 = lambda c: sum(1 for s in ("Thất Sát", "Phá Quân", "Liêm Trinh", "Tham Lang") if s in TPM(c))

    def th72_core(c):
        m, r = c["menh"], roles(c)
        sm = majors_at(c, {r["self"]})
        if m == B["Thìn"]:
            return "Thái Dương" in sm and "Thái Âm" in majors_at(c, {r["opp"]})
        if m == B["Tuất"]:
            return "Thái Âm" in sm and "Thái Dương" in majors_at(c, {r["opp"]})
        if m == B["Tỵ"]:
            return "Thái Dương" in sm and "Thái Âm" in majors_at(c, {r["trine1"]})
        if m == B["Dậu"]:
            return "Thái Âm" in sm and "Thái Dương" in majors_at(c, {r["trine2"]})
        return False

    ma = lambda c: c["menh"] == B["Ngọ"] and "Kình Dương" in S(c, "self")
    return {
        "CACH_X_TU_PHU_VU_TUONG@kl_132_193": dict(core=four(TPVT), boost=[lambda c: has(RS(c), ("Tả Phụ", "Hữu Bật")), lambda c: anyin(RS(c), ("Văn Xương", "Văn Khúc"))],
                                                   brk=[], ref=[on_menh_tuan]),
        "CACH_X_TU_PHU_VU_TUONG@th_115": dict(core=four(TPVT), boost=[lambda c: "Lộc Tồn" in RS(c) or "Hóa Lộc" in RH(c), lambda c: has(RS(c), ("Tả Phụ", "Hữu Bật"))],
                                               brk=[], ref=[on_menh_tuan]),
        "CACH_X_TU_PHU_DONG_CUNG@tt_22": dict(core=lambda c: has(majors_at(c, {c["menh"]}), ("Tử Vi", "Thiên Phủ")), boost=[lambda c: has(RS(c), ("Tả Phụ", "Hữu Bật"))],
                                               brk=[lambda c: anyin(S(c, "self"), SAT)], ref=[on_menh_tuan]),
        "CACH_X_TU_PHU_DONG_CUNG@kl_50": dict(core=lambda c: has(majors_at(c, {c["menh"]}), ("Tử Vi", "Thiên Phủ")),
                                               boost=[lambda c: anyin(RS(c), ("Văn Xương", "Văn Khúc")), lambda c: anyin(RS(c), ("Thiên Khôi", "Thiên Việt")), lambda c: "Hóa Khoa" in RH(c),
                                                      lambda c: has(S(c, "self"), ("Kình Dương", "Lực Sĩ")),
                                                      lambda c: c["menh"] == B["Dần"] and has(hoa_at(c, {c["menh"]}), ("Hóa Kỵ", "Hóa Quyền"))],
                                               brk=[], ref=[on_menh_tuan]),
        "CACH_X_CO_NGUYET_DONG_LUONG@tt_24": dict(core=four(CNDL), boost=[lambda c: anyin(RS(c), CAT6)], brk=[lambda c: anyin(TPS(c), ("Địa Không", "Địa Kiếp")),
                                                                                                                   lambda c: "Hóa Kỵ" in TPH(c)], ref=[]),
        "CACH_X_CO_NGUYET_DONG_LUONG@kl_221": dict(core=four(CNDL), boost=[lambda c: anyin(RS(c), CAT6), lambda c: anyin(RH(c), ALL3)], brk=[], ref=[]),
        "CACH_X_SAT_PHA_LIEM_THAM@th_76_77": dict(core=lambda c: cnt4(c) >= 3, boost=[lambda c: anyin(RH(c), ("Hóa Khoa", "Hóa Quyền"))],
                                                   brk=[lambda c: sum(1 for s in SAT if s in TPS(c)) >= 3 and "Hóa Kỵ" in TPH(c)], ref=[]),
        "CACH_X_NHAT_NGUYET_TINH_MINH@th_72": dict(core=th72_core, boost=[sang], brk=[ham_sat], ref=[]),
        "CACH_X_NHAT_NGUYET_TINH_MINH@kl_53_68": dict(core=four(["Thái Dương", "Thái Âm"]), boost=[sang], brk=[ham_sat],
                                                       ref=[lambda c: AND(OR(lte(rank(c, "Thái Dương"), 0), lte(rank(c, "Thái Âm"), 0)),
                                                                          "Thiên Khôi" not in TPS(c), "Thiên Việt" not in TPS(c))]),
        "CACH_X_NHAT_LE_TRUNG_THIEN@kl_52_85": dict(core=lambda c: c["menh"] == B["Ngọ"] and "Thái Dương" in majors_at(c, {c["menh"]}),
                                                     boost=[lambda c: anyin(RH(c), ("Hóa Khoa", "Hóa Quyền")), lambda c: anyin(RS(c), ("Văn Xương", "Văn Khúc"))], brk=[], ref=[]),
        "CACH_X_THACH_TRUNG_AN_NGOC@kl_44": dict(core=lambda c: c["menh"] in (B["Tý"], B["Ngọ"]) and "Cự Môn" in majors_at(c, {c["menh"]})
                                                  and "Thiên Cơ" in majors_at(c, {roles(c)["opp"]}), boost=[], brk=[], ref=[]),
        "CACH_X_THACH_TRUNG_AN_NGOC@kl_58": dict(core=lambda c: c["menh"] in (B["Tý"], B["Ngọ"]) and "Cự Môn" in majors_at(c, {c["menh"]}) and has(TPH(c), ALL3),
                                                  boost=[], brk=[], ref=[]),
        "CACH_X_THACH_TRUNG_AN_NGOC@kl_106": dict(core=lambda c: c["menh"] in (B["Tý"], B["Ngọ"]) and "Cự Môn" in majors_at(c, {c["menh"]})
                                                   and (on_menh_tuan(c) or "Hóa Lộc" in hoa_at(c, {c["menh"]})), boost=[], brk=[], ref=[]),
        "CACH_X_MA_DAU_DOI_KIEM@kl_64_xau": dict(core=ma, boost=[], brk=[lambda c: has(S(c, "self"), ("Thất Sát", "Thiên Hình"))], ref=[]),
        "CACH_X_MA_DAU_DOI_KIEM@kl_64_tot": dict(core=ma, boost=[lambda c: has(RH(c), ALL3) and "Thất Sát" not in S(c, "self") and "Thiên Hình" not in S(c, "self")],
                                                  brk=[], ref=[]),
        "CACH_X_TAM_KY_GIA_HOI@kl_66": dict(core=lambda c: has(TPH(c), ("Hóa Lộc", "Hóa Quyền", "Hóa Khoa")), boost=[],
                                             brk=[lambda c: "Hóa Kỵ" in hoa_at(c, {roles(c)["self"], roles(c)["opp"]}) or "Kình Dương" in stars_at(c, {roles(c)["self"], roles(c)["opp"]})],
                                             ref=[]),
        "CACH_X_KHOI_VIET_GIAP_MENH@kl_44_62": dict(
            core=lambda c: (c["pos"]["Thiên Khôi"] == roles(c)["prev"] and c["pos"]["Thiên Việt"] == roles(c)["next"])
            or (c["pos"]["Thiên Việt"] == roles(c)["prev"] and c["pos"]["Thiên Khôi"] == roles(c)["next"]),
            boost=[lambda c: anyin(RS(c), ("Văn Xương", "Văn Khúc"))], brk=[lambda c: sum(1 for s in SAT if s in TPS(c)) >= 1], ref=[]),
    }


def state(spec, c, thuong_at=2, drop=1):
    """ladder of the evaluator: breaker -> bi_pha (no rescuers in the variants); boosters >= thuong_at -> thanh_thuong, >= 1 -> thanh, 0 -> hinh_thuc;
    an active refutation lowers it by `drop` rungs (the evaluator's convention is 1). `thuong_at` and `drop` are parameters ONLY for sensitivity runs."""
    core = spec["core"](c)
    if core is None:
        return "chua_du_du_kien"
    if not core:
        return "khong_hien"
    on = lambda fs: [f for f in fs if f(c) is True]
    if on(spec["brk"]):
        return "bi_pha"
    n = len(on(spec["boost"]))
    rungs = ["hinh_thuc", "thanh", "thanh_thuong"]
    i = 2 if n >= thuong_at else 1 if n >= 1 else 0
    if on(spec["ref"]) and i >= 1:
        i = max(0, i - drop)
    return rungs[i]
