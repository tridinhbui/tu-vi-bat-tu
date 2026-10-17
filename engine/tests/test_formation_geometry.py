"""Tử Phủ đồng cung × 'phá được cứu' is IMPOSSIBLE IN THE MODEL — by construction, not by sampling.

The model puts Tử Vi and Thiên Phủ in one palace only when Tử Vi is at Dần or Thân (Thiên Phủ mirrors Tử Vi across the Dần–Thân axis).
Then all fourteen major stars have FIXED positions, so the only free stars are the four helpers Tả/Hữu (by month) and Xương/Khúc (by hour).
'Phá được cứu' for this formation needs one of:
  (A) Hóa Kỵ and Hóa Khoa both in the Mệnh palace (khoa_dong_cung rescues ky_dong_cung), or
  (B) Hóa Lộc, Quyền and Khoa all in the tam phương (tam_hoa_hoi_cuu rescues everything).
Both are refuted below, stem by stem, with the star formulas — and then confirmed on every real chart that satisfies Tử Phủ đồng cung."""
import pytest

from tvbt import calendar_core as cc, lunar_input, tuvi
from tvbt.tuvi import TU_HOA

STEMS_VI = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
TP = {2, 8}                                                    # Dần, Thân: the only palaces where Tử Vi and Thiên Phủ can be together
FIXED = {}                                                     # major star -> offset from the Tử Vi / Thiên Phủ anchor
for n, o in [("Tử Vi", 0), ("Thiên Cơ", -1), ("Thái Dương", -3), ("Vũ Khúc", -4), ("Thiên Đồng", -5), ("Liêm Trinh", -8)]:
    FIXED[n] = ("tv", o)
for n, o in [("Thiên Phủ", 0), ("Thái Âm", 1), ("Tham Lang", 2), ("Cự Môn", 3), ("Thiên Tướng", 4), ("Thiên Lương", 5), ("Thất Sát", 6), ("Phá Quân", 10)]:
    FIXED[n] = ("ph", o)


def major_pos(star, tv_pos):
    kind, o = FIXED[star]
    return (tv_pos + o) % 12 if kind == "tv" else ((4 - tv_pos) + o) % 12


def tam_phuong(b):
    return {b, (b + 6) % 12, (b + 4) % 12, (b + 8) % 12}


def helper_positions(month, hb):
    return {"Tả Phụ": (4 + month - 1) % 12, "Hữu Bật": (10 - (month - 1)) % 12, "Văn Xương": (10 - hb) % 12, "Văn Khúc": (4 + hb) % 12}


def all_positions(star_names, tv_pos, month, hb):
    h = helper_positions(month, hb)
    return {s: (h[s] if s in h else major_pos(s, tv_pos)) for s in star_names}


def test_tu_vi_and_thien_phu_only_share_dan_than():
    assert {tv for tv in range(12) if major_pos("Tử Vi", tv) == major_pos("Thiên Phủ", tv)} == TP


def test_xuong_khuc_never_meet_in_dan_or_than():
    """the only helper pair that could carry both Khoa and Kỵ (Tân: Khoa Văn Khúc, Kỵ Văn Xương)."""
    meet = {helper_positions(1, hb)["Văn Xương"] for hb in range(12) if helper_positions(1, hb)["Văn Xương"] == helper_positions(1, hb)["Văn Khúc"]}
    assert meet == {1, 7}                                      # Sửu, Mùi — never Dần/Thân


@pytest.mark.parametrize("stem", range(10))
@pytest.mark.parametrize("tv_pos", sorted(TP))
def test_case_A_khoa_and_ky_never_share_the_tu_phu_palace(stem, tv_pos):
    loc, quyen, khoa, ky = TU_HOA[stem]
    for month in range(1, 13):
        for hb in range(12):
            p = all_positions([khoa, ky], tv_pos, month, hb)
            assert not (p[khoa] == tv_pos and p[ky] == tv_pos), (STEMS_VI[stem], tv_pos, month, hb)


@pytest.mark.parametrize("stem", range(10))
@pytest.mark.parametrize("tv_pos", sorted(TP))
def test_case_B_tam_hoa_never_gather_in_the_tam_phuong(stem, tv_pos):
    loc, quyen, khoa, ky = TU_HOA[stem]
    tpset = tam_phuong(tv_pos)
    for month in range(1, 13):
        for hb in range(12):
            p = all_positions([loc, quyen, khoa], tv_pos, month, hb)
            assert not all(p[s] in tpset for s in (loc, quyen, khoa)), (STEMS_VI[stem], tv_pos, month, hb)


def test_real_charts_confirm_the_argument_and_the_enumeration_is_not_vacuous():
    """every real chart in which Mệnh holds Tử Vi + Thiên Phủ: Khoa and Kỵ never coincide there, Tam Hóa never gather, 'phá được cứu' never occurs."""
    from tvbt.formation_explain import analyse
    from tvbt.knowledge.loader import load_experimental
    fs = [f for f in load_experimental()[1] if f.id == "CACH_X_TU_PHU_DONG_CUNG"]
    n = 0
    for year in range(2014, 2024):                              # ten consecutive years = ten stems
        for month in range(1, 13):
            for day in (1, 7, 13, 19, 25, 29):
                try:
                    sol = lunar_input.lunar_to_solar(day, month, year, False, "vn")[0]
                except Exception:
                    continue
                for hb in range(12):
                    tv = tuvi.compute(cc.normalize(cc.BirthInput(sol.year, sol.month, sol.day, 2 * hb, 0, "Asia/Ho_Chi_Minh", "male")))
                    menh = next(p for p in tv.palaces if p["name"] == "Mệnh")
                    if not {"Tử Vi", "Thiên Phủ"} <= set(menh["major_stars"]):
                        continue
                    n += 1
                    hoa = {k: v["branch"] for k, v in tv.tu_hoa.items()}
                    mb = tv.menh_branch
                    assert not (hoa["Hóa Khoa"] == mb == hoa["Hóa Kỵ"])
                    assert not all(hoa[k] in tam_phuong(mb) for k in ("Hóa Lộc", "Hóa Quyền", "Hóa Khoa"))
                    assert analyse(tv, fs)[0]["state"] != "pha_duoc_cuu"
    assert n >= 50, n                                          # the check really ran on many Tử Phủ đồng cung charts
