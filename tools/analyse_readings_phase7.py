"""Phase 7 sensitivity of the school variants to the READINGS the audit had to assume (pure oracle, no production code), over the same
116,928 charts as the other scans. NOTHING here selects a reading: every reading that has a textual basis is reported side by side.
Writes engine/tests/fixtures/readings_sensitivity.json.

A. CNDL (TT p.24 'Gặp Kiếp Không Hoá Kị xuống hạ cách'): scope x composition grid of the breaker.
B. KVGM (KL p.62 mục 4 'Cung mệnh có Khôi Việt lại bị sát tinh hội chiếu'): scope x star set x threshold grid, ALSO on the structure the sentence
   literally describes (Khôi Việt in/hội chiếu Mệnh) — which is not the giáp structure.
C. SPLT (TH p.77 'nhiều sát tinh'): threshold x with/without Kỵ.
D. Scope of the rules whose sentence gives none ('hội', 'thích'): share of charts whose state changes when read as hội chiếu / đối cung / đồng cung / tam hợp instead of tam phương.
E. Mechanics: thuong_at 1/2/3 and refutation drop 0/1/2.
F. Tuần/Triệt: how often the refutation is active; Thạch trung ẩn ngọc enabling condition.
G. Thái Dương at Thân/Mùi (brightness not printed): charts affected and the states under every possible rank.
H. Mã đầu đới kiếm: KL definition (Kình at Ngọ in Mệnh) versus TT p.142's (Kình gặp Thiên Mã).
I. Tử Phủ đồng cung anchor (Mệnh vs Thân) and TT p.22's Tỵ/Hợi."""
import collections
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine/tests"))
import oracle_tuvi_independent as O  # noqa: E402

YEARS = list(range(2014, 2024)) + [1978, 1988, 1998, 2008]
LEAPLESS_DAYS = range(1, 30)
R = O.REGIONS
SIX, TU_SAT, KK = O.SAT, ("Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh"), ("Địa Không", "Địa Kiếp")
SPECS = {sc: O.V(sc) for sc in R}
BASE = SPECS["tp"]
CNDL_CORE = BASE["CACH_X_CO_NGUYET_DONG_LUONG@tt_24"]["core"]
KVGM_CORE = BASE["CACH_X_KHOI_VIET_GIAP_MENH@kl_44_62"]["core"]
SPLT_CORE = BASE["CACH_X_SAT_PHA_LIEM_THAM@th_76_77"]["core"]

cnt = collections.defaultdict(collections.Counter)
n = 0


def inreg(c, scope):
    return R[scope](c)


for ly in YEARS:
    for lm in range(1, 13):
        for ld in LEAPLESS_DAYS:
            for hb in range(12):
                for male in (True, False):
                    try:
                        c = O.chart(ly, lm, ld, hb, male)
                    except KeyError:
                        continue
                    n += 1
                    # ---- A
                    if CNDL_CORE(c):
                        cnt["A_core"]["n"] += 1
                        for sc in R:
                            reg = inreg(c, sc)
                            st, hoa = O.stars_at(c, reg), O.hoa_at(c, reg)
                            kiep, khong, ky = "Địa Kiếp" in st, "Địa Không" in st, "Hóa Kỵ" in hoa
                            comp = {"mot_trong_ba": kiep or khong or ky, "du_ca_ba": kiep and khong and ky, "cap_khong_kiep_hoac_ky": (kiep and khong) or ky,
                                    "tu_hai_trong_ba": (kiep + khong + ky) >= 2}
                            for k, v in comp.items():
                                cnt["A"][f"{sc}|{k}"] += bool(v)
                    # ---- B
                    if KVGM_CORE(c):
                        cnt["B_core"]["n"] += 1
                        for sc in R:
                            st = O.stars_at(c, inreg(c, sc))
                            for sname, sset in (("sau_sat", SIX), ("tu_sat", TU_SAT), ("khong_kiep", KK)):
                                k = sum(1 for s in sset if s in st)
                                for th in (1, 2, 3):
                                    cnt["B"][f"{sc}|{sname}|>={th}"] += k >= th
                    # the structure KL p.62 mục 4 literally names: Khôi Việt both in/hội chiếu Mệnh
                    tps = O.stars_at(c, O.tp(c))
                    if "Thiên Khôi" in tps and "Thiên Việt" in tps:
                        cnt["B2_core"]["n"] += 1
                        for sc in R:
                            st = O.stars_at(c, inreg(c, sc))
                            for sname, sset in (("sau_sat", SIX), ("tu_sat", TU_SAT)):
                                k = sum(1 for s in sset if s in st)
                                for th in (1, 2, 3):
                                    cnt["B2"][f"{sc}|{sname}|>={th}"] += k >= th
                    # ---- J: Tam kỳ gia hội breaker (KL tr.66 'đồng cung hoặc chiếu'; KL tr.67 separately says 'đồng cung hay xung chiếu')
                    if all(h in O.hoa_at(c, O.tp(c)) for h in ("Hóa Lộc", "Hóa Quyền", "Hóa Khoa")):
                        cnt["J_core"]["n"] += 1
                        for sc in ("dong_cung", "doi_cung", "tam_hop", "hoi_chieu", "tp"):
                            reg = inreg(c, sc)
                            cnt["J"][sc] += ("Hóa Kỵ" in O.hoa_at(c, reg)) or ("Kình Dương" in O.stars_at(c, reg))
                        reg = inreg(c, "dong_cung") | inreg(c, "doi_cung")
                        cnt["J"]["dong_cung+doi_cung (variant)"] += ("Hóa Kỵ" in O.hoa_at(c, reg)) or ("Kình Dương" in O.stars_at(c, reg))
                    # ---- K: Nhật Nguyệt hãm without Khôi/Việt chiếu (KL tr.68)
                    if O.four(["Thái Dương", "Thái Âm"]) if False else (O.majors_at(c, O.tp(c)) >= {"Thái Dương", "Thái Âm"}):
                        hãm = O.OR(O.lte(O.rank(c, "Thái Dương"), 0), O.lte(O.rank(c, "Thái Âm"), 0))
                        if hãm is True:
                            cnt["K_core"]["n"] += 1
                            for sc in ("doi_cung", "tam_hop", "hoi_chieu", "tp"):
                                st = O.stars_at(c, inreg(c, sc))
                                cnt["K"][sc] += ("Thiên Khôi" not in st) and ("Thiên Việt" not in st)
                    # ---- C
                    if SPLT_CORE(c):
                        cnt["C_core"]["n"] += 1
                        tps_, tph = O.stars_at(c, O.tp(c)), O.hoa_at(c, O.tp(c))
                        k = sum(1 for s in SIX if s in tps_)
                        for th in (1, 2, 3, 4):
                            cnt["C"][f">={th}"] += k >= th
                            cnt["C"][f">={th}+Ky"] += (k >= th) and ("Hóa Kỵ" in tph)
                    # ---- D / E / F
                    for vid in BASE:
                        base_state = O.state(BASE[vid], c)
                        if base_state == "khong_hien":
                            continue
                        cnt["core_n"][vid] += 1
                        for sc in ("hoi_chieu", "doi_cung", "dong_cung", "tam_hop"):
                            cnt["D"][f"{vid}|{sc}"] += O.state(SPECS[sc][vid], c) != base_state
                        for th, dr in itertools.product((1, 2, 3), (0, 1, 2)):
                            if (th, dr) != (2, 1):
                                cnt["E"][f"{vid}|thuong{th}|drop{dr}"] += O.state(BASE[vid], c, th, dr) != base_state
                        if BASE[vid]["ref"] and BASE[vid]["ref"][0](c) is True:
                            cnt["F_ref_active"][vid] += 1
                    # ---- F Thạch trung
                    if c["menh"] in (O.B["Tý"], O.B["Ngọ"]) and "Cự Môn" in O.majors_at(c, {c["menh"]}):
                        cnt["F_ttan"]["cu_mon_ty_ngo"] += 1
                        if c["menh"] in c["tuan"] or c["menh"] in c["triet"]:
                            cnt["F_ttan"]["tuan_triet_o_menh"] += 1
                        if "Hóa Lộc" in O.hoa_at(c, {c["menh"]}):
                            cnt["F_ttan"]["hoa_loc_o_menh"] += 1
                        if all(h in O.hoa_at(c, O.tp(c)) for h in ("Hóa Khoa", "Hóa Quyền", "Hóa Lộc")):
                            cnt["F_ttan"]["tam_hoa_trong_tam_phuong"] += 1
                        if "Thiên Cơ" in O.majors_at(c, {O.roles(c)["opp"]}):
                            cnt["F_ttan"]["thien_co_o_doi_cung"] += 1
                    # ---- G
                    sp = BASE["CACH_X_NHAT_NGUYET_TINH_MINH@kl_53_68"]
                    if sp["core"](c):
                        unknown = O.rank(c, "Thái Dương") is None or O.rank(c, "Thái Âm") is None
                        if unknown:
                            cnt["G"]["unknown_rank"] += 1
                            old_sun = dict(O.SUN)
                            for r in range(5):
                                O.SUN[O.B["Thân"]] = O.SUN[O.B["Mùi"]] = r
                                cnt["G"][f"state_if_rank_{r}|{O.state(sp, c)}"] += 1
                            O.SUN.clear(); O.SUN.update(old_sun)
                        cnt["G"]["core"] += 1
                    # ---- H
                    kinh_ngo = c["pos"]["Kình Dương"] == O.B["Ngọ"] and c["menh"] == O.B["Ngọ"]
                    cnt["H"]["kl_kinh_o_ngo_trong_menh"] += kinh_ngo
                    ma_kinh_menh = c["pos"]["Kình Dương"] == c["pos"]["Thiên Mã"] == c["menh"]
                    cnt["H"]["tt_kinh_cung_thien_ma_trong_menh"] += ma_kinh_menh
                    cnt["H"]["tt_kinh_ma_menh_o_tu_mo"] += ma_kinh_menh and c["menh"] in (4, 10, 1, 7)
                    cnt["H"]["tt_kinh_ma_menh_o_ngo"] += ma_kinh_menh and c["menh"] == 6
                    cnt["H"]["kinh_va_thien_ma_cung_cung_bat_ky"] += c["pos"]["Kình Dương"] == c["pos"]["Thiên Mã"]
                    # ---- I
                    tv_ph = c["pos"]["Tử Vi"] == c["pos"]["Thiên Phủ"]
                    cnt["I"]["tu_phu_dong_cung_o_menh"] += tv_ph and c["pos"]["Tử Vi"] == c["menh"]
                    cnt["I"]["tu_phu_dong_cung_o_than_khong_o_menh"] += tv_ph and c["pos"]["Tử Vi"] == c["than"] and c["pos"]["Tử Vi"] != c["menh"]
                    cnt["I"]["tu_phu_dong_cung_o_ty_hoi_bat_ky"] += tv_ph and c["pos"]["Tử Vi"] in (5, 11)
                    cnt["I"]["tu_sat_dong_cung_o_menh_ty_hoi"] += c["pos"]["Tử Vi"] == c["pos"]["Thất Sát"] == c["menh"] and c["menh"] in (5, 11)
out = {"charts": n, "years": YEARS, **{k: dict(v) for k, v in cnt.items()}}
(ROOT / "engine/tests/fixtures/readings_sensitivity.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(n)
for k in ("A_core", "B_core", "B2_core", "C_core", "G", "H", "I", "F_ttan"):
    print(k, dict(cnt[k]))
