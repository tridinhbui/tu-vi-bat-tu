"""Independent cross-check of the draft cách-cục engine.

The oracle below re-implements the 10 draft formations from the DEFINITIONS in data/experimental/formations_experimental.json
using only the raw chart (tv.palaces / tv.tu_hoa), NOT the DSL, typed facts or evaluator. It must agree with the engine on the
state and on every active evidence id over thousands of charts. This verifies the machinery (geometry, DSL, ladder); it does not
verify that the formations themselves match any book (they are drafts, `reviewStatus=draft`)."""
import random

import pytest

from tvbt import tuvi
from tvbt.calendar_core import BirthInput, normalize
from tvbt.formation_explain import analyse
from tvbt.knowledge.loader import load_experimental

SAT = {"Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"}
RANK = {"miếu": 4, "vượng": 3, "đắc": 2, "bình": 1, "hãm": 0}
_, XF, _ = load_experimental()
FDEF = {f.id: f for f in XF}


class Raw:
    def __init__(self, tv):
        self.tv = tv
        self.by_b = {p["branch_index"]: p for p in tv.palaces}
        self.m = tv.menh_branch
        self.me = self.by_b[self.m]
        self.opp = self.by_b[(self.m + 6) % 12]
        self.t1, self.t2 = self.by_b[(self.m + 4) % 12], self.by_b[(self.m + 8) % 12]
        self.fp, self.fn = self.by_b[(self.m - 1) % 12], self.by_b[(self.m + 1) % 12]
        self.tp = [self.me, self.opp, self.t1, self.t2]
        self.hoa_b = {k: v["branch"] for k, v in tv.tu_hoa.items()}

    def stars(self, ps):
        return [s for p in ps for s in p["stars"]]

    def majors(self, ps):
        return [s for p in ps for s in p["major_stars"]]

    def hoa_in(self, ps):
        bs = {p["branch_index"] for p in ps}
        return {k for k, b in self.hoa_b.items() if b in bs}

    def rank(self, star):
        for p in self.tp:
            lv = {**p["minor_dignity"], **p["major_dignity"]}.get(star)
            if star in p["stars"]:
                return RANK.get(lv) if lv else None
        return None


def oracle(r: Raw, fid: str):
    me, tp = r.me, r.tp
    self_s, tp_s, tp_m = set(r.stars([me])), set(r.stars(tp)), set(r.majors(tp))
    self_hoa, tp_hoa = r.hoa_in([me]), r.hoa_in(tp)
    sat_self = sum(1 for s in me["stars"] if s in SAT)
    has = lambda pool, *xs: all(x in pool for x in xs)
    anyin = lambda pool, *xs: any(x in pool for x in xs)
    ev = {
        "ta_huu_hoi": has(tp_s, "Tả Phụ", "Hữu Bật"), "xuong_khuc_hoi": anyin(tp_s, "Văn Xương", "Văn Khúc"),
        "loc_hoi": "Lộc Tồn" in tp_s or "Hóa Lộc" in tp_hoa, "khoi_viet_hoi": anyin(tp_s, "Thiên Khôi", "Thiên Việt"),
        "khoa_quyen_hoi": anyin(tp_hoa, "Hóa Khoa", "Hóa Quyền"),
        "sat_dong_cung": anyin(self_s, *SAT), "ky_dong_cung": "Hóa Kỵ" in self_hoa,
        "khong_kiep_dong_cung": anyin(self_s, "Địa Không", "Địa Kiếp"), "sat_tu_hai_tro_len": sat_self >= 2,
        "sat_khac_dong_cung": anyin(self_s, "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"),
        "ky_trong_tam_phuong": "Hóa Kỵ" in tp_hoa, "khoa_dong_cung": "Hóa Khoa" in self_hoa,
        "tuan_an_ngu": bool(me["tuan"]), "triet_an_ngu": bool(me["triet"]),
        "hoa_o_ban_cung": anyin(self_hoa, "Hóa Lộc", "Hóa Quyền", "Hóa Khoa"),
        "co_chinh_tinh": bool(me["major_stars"]), "vo_chinh_dieu": not me["major_stars"],
        "ta_huu_giai_ky": has(tp_s, "Tả Phụ", "Hữu Bật"),
        # definition v2
        "tuan_triet_an_ngu": bool(me["tuan"]) or bool(me["triet"]),
        "tam_hoa_hoi_cuu": has(tp_hoa, "Hóa Lộc", "Hóa Quyền", "Hóa Khoa"), "tam_hoa_hoi_du": has(tp_hoa, "Hóa Lộc", "Hóa Quyền", "Hóa Khoa"),
        "cat_tinh_hoi": anyin(tp_s, "Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"),
        "khoa_quyen_loc_hoi": anyin(tp_hoa, "Hóa Khoa", "Hóa Quyền", "Hóa Lộc"),
        "ba_sat_va_ky_trong_tam_phuong": sum(1 for x in r.stars(tp) if x in SAT) >= 3 and "Hóa Kỵ" in tp_hoa,
        "ky_hoac_kinh_dong_cung": "Hóa Kỵ" in self_hoa or "Kình Dương" in self_s,
        "that_sat_trong_tam_phuong": "Thất Sát" in tp_s,
    }
    rd, ra = r.rank("Thái Dương"), r.rank("Thái Âm")
    ev["nhat_nguyet_ham_gap_sat"] = ((rd is not None and rd <= 0) or (ra is not None and ra <= 0)) and sum(1 for x in r.stars(tp) if x in SAT) >= 1
    ev["nhat_nguyet_deu_sang"] = (r.rank("Thái Dương") is not None and r.rank("Thái Âm") is not None
                                  and r.rank("Thái Dương") >= 2 and r.rank("Thái Âm") >= 2)
    for s in ("Thiên Tướng", "Thất Sát", "Thái Dương", "Thái Âm", "Cự Môn", "Kình Dương"):
        ev[f"{s.replace(' ', '_')}_ham"] = r.rank(s) is not None and r.rank(s) <= 0
    cores = {
        "CACH_X_TU_PHU_VU_TUONG": has(tp_m, "Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"),
        "CACH_X_TU_PHU_DONG_CUNG": has(set(me["major_stars"]), "Tử Vi", "Thiên Phủ"),
        "CACH_X_CO_NGUYET_DONG_LUONG": all(x in tp_m for x in ("Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương")),
        "CACH_X_SAT_PHA_LIEM_THAM": sum(x in tp_m for x in ("Thất Sát", "Phá Quân", "Liêm Trinh", "Tham Lang")) >= 3,
        "CACH_X_NHAT_NGUYET_TINH_MINH": has(tp_m, "Thái Dương", "Thái Âm"),
        "CACH_X_NHAT_LE_TRUNG_THIEN": me["branch"] == "Ngọ" and "Thái Dương" in me["major_stars"],
        "CACH_X_THACH_TRUNG_AN_NGOC": me["branch"] in ("Tý", "Ngọ") and "Cự Môn" in me["major_stars"],
        "CACH_X_MA_DAU_DOI_KIEM": me["branch"] == "Ngọ" and "Kình Dương" in me["stars"],
        "CACH_X_TAM_KY_GIA_HOI": has(tp_hoa, "Hóa Lộc", "Hóa Quyền", "Hóa Khoa"),
        "CACH_X_KHOI_VIET_GIAP_MENH": ("Thiên Khôi" in r.fp["stars"] and "Thiên Việt" in r.fn["stars"]) or ("Thiên Việt" in r.fp["stars"] and "Thiên Khôi" in r.fn["stars"]),
    }
    f = FDEF[fid]
    core = cores[fid]
    if not core:
        return "khong_hien", {k: set() for k in ("boosters", "breakers", "rescuers", "refutations")}
    act = {k: {e.id for e in getattr(f, k) if ev[e.id]} for k in ("boosters", "breakers", "rescuers", "refutations")}
    covered = set()
    for e in f.rescuers:
        if e.id in act["rescuers"]:
            covered |= {b.id for b in f.breakers} if "*" in e.rescues else set(e.rescues)
    uncovered = act["breakers"] - covered
    if uncovered:
        return "bi_pha", act
    if act["breakers"]:
        return "pha_duoc_cuu", act
    n = len(act["boosters"])
    state = "thanh_thuong" if n >= f.thuong_at else "thanh" if n >= 1 else "hinh_thuc"
    low = {"thanh_thuong": "thanh", "thanh": "hinh_thuc"}
    if act["refutations"] and state in low:
        state = low[state]
    return state, act


def _charts(n, seed):
    rng = random.Random(seed)
    for _ in range(n):
        yield BirthInput(rng.randint(1950, 2010), rng.randint(1, 12), rng.randint(1, 28), rng.randint(0, 23), 0,
                         "Asia/Ho_Chi_Minh", rng.choice(["male", "female"]))


def test_engine_agrees_with_independent_oracle_on_4000_charts():
    disagreements = []
    cells = set()
    for b in _charts(4000, 7):
        tv = tuvi.compute(normalize(b))
        r = Raw(tv)
        for res in analyse(tv, XF):
            st, act = oracle(r, res["id"])
            eng = {k: {e["id"] for e in res["evidence"] if e["kind"] == k and e["active"]} for k in act}
            cells.add((res["id"], st))
            if st != res["state"] or (st != "khong_hien" and eng != act):
                disagreements.append((b, res["id"], st, res["state"]))
    assert not disagreements, disagreements[:5]
    assert len(cells) >= 45, f"oracle sample too narrow: {len(cells)} (formation,state) cells"
