"""Golden tests transcribed from the cited books (independent of our algorithm).
SRC_THUC_HANH = Tử Vi Thực Hành (Dịch Lý Huyền Cơ); SRC_KHAO_LUAN = Tử Vi Khảo Luận (Hoàng Thường - Hàm Chương)."""
import pytest

from tvbt import tuvi
from tvbt.calendar_core import BirthInput, normalize
from tvbt.ganzhi import BRANCHES_VI, STEMS_VI, branch_stem_from_year, nap_am_element

B = {n: i for i, n in enumerate(BRANCHES_VI)}
# p.12 cục table: year-stem pair -> {palace branches: cục number}. Cells the book omits/misprints are not asserted.
CUC_TABLE = {
    (0, 5): {("Tý", "Sửu"): 2, ("Dần", "Mão", "Tuất", "Hợi"): 6, ("Thìn", "Tỵ"): 3, ("Ngọ", "Mùi"): 5, ("Thân", "Dậu"): 4},
    (1, 6): {("Tý", "Sửu"): 6, ("Dần", "Mão", "Tuất", "Hợi"): 5, ("Thìn", "Tỵ"): 4, ("Ngọ", "Mùi"): 3, ("Thân", "Dậu"): 2},
    (2, 7): {("Tý", "Sửu"): 5, ("Mão", "Tuất", "Hợi"): 3, ("Thìn", "Tỵ"): 2, ("Ngọ", "Mùi"): 4, ("Thân", "Dậu"): 6},
    (3, 8): {("Tý", "Sửu"): 3, ("Mão", "Tuất", "Hợi"): 4, ("Thìn", "Tỵ"): 6, ("Ngọ", "Mùi"): 2, ("Thân", "Dậu"): 5},
    (4, 9): {("Mão", "Tuất", "Hợi"): 2, ("Thìn", "Tỵ"): 5, ("Ngọ", "Mùi"): 6, ("Thân", "Dậu"): 3},
}


@pytest.mark.parametrize("pair", list(CUC_TABLE))
def test_cuc_table_p12(pair):
    for stem in pair:
        for branches, want in CUC_TABLE[pair].items():
            for b in branches:
                el = nap_am_element(branch_stem_from_year(stem, B[b]), B[b])
                assert tuvi.CUC_BY_ELEMENT[el] == want, (STEMS_VI[stem], b)
    # Mậu/Quý at Tý, Sửu: book prints "Kim ngũ cục" (typo; Kim is tứ cục) — element Kim is asserted only
    for stem in (4, 9):
        for b in ("Tý", "Sửu"):
            assert nap_am_element(branch_stem_from_year(stem, B[b]), B[b]) == "Kim"


def test_tuvi_position_worked_examples_pp14_17():
    assert tuvi.tuvi_position(12, 3)[0] == B["Tỵ"]    # Mộc tam cục, ngày 12 -> Tỵ
    assert tuvi.tuvi_position(24, 3)[0] == B["Dậu"]   # same cục, ngày 24 -> Dậu
    assert tuvi.tuvi_position(11, 6)[0] == B["Dần"]   # Hỏa lục cục, ngày 11 -> Dần


def stars(year, month=6, day=15, hour=12, gender="male"):
    c = tuvi.compute(normalize(BirthInput(year, month, day, hour, 0, "Asia/Ho_Chi_Minh", gender)))
    return c, {s.name: BRANCHES_VI[s.branch] for s in c.stars}


def test_khoi_viet_verse_p19():
    want = {1984: ("Sửu", "Mùi"), 1988: ("Sửu", "Mùi"),   # Giáp, Mậu
            1985: ("Tý", "Thân"), 1989: ("Tý", "Thân"),   # Ất, Kỷ
            1986: ("Hợi", "Dậu"), 1987: ("Hợi", "Dậu"),   # Bính, Đinh
            1990: ("Ngọ", "Dần"), 1991: ("Ngọ", "Dần"),   # Canh, Tân
            1992: ("Mão", "Tỵ"), 1993: ("Mão", "Tỵ")}     # Nhâm, Quý
    for y, (k, v) in want.items():
        _, s = stars(y)
        assert (s["Thiên Khôi"], s["Thiên Việt"]) == (k, v), y


def test_year_branch_stars_pp21_23():
    _, s = stars(1991)   # Mùi year
    # p.23 states the RULE (Mão = Tý, count backwards to the birth-year branch). Its printed example for a Mùi
    # year says Tý/Ngọ, which contradicts that rule (counting back from Mão reaches Thân at Mùi): rule used.
    assert s["Hồng Loan"] == "Thân" and s["Thiên Hỷ"] == "Dần"
    assert s["Thái Tuế"] == "Mùi" and s["Thiên Không"] == "Thân"      # p.25 worked example
    assert s["Đào Hoa"] == "Tý"                                       # Hợi Mão Mùi -> Tý
    assert s["Thiên Mã"] == "Tỵ"                                      # Hợi Mão Mùi -> Tỵ
    for y, dao, ma in [(1986, "Mão", "Thân"), (1984, "Dậu", "Dần"), (1989, "Ngọ", "Hợi")]:  # Dần/Thân/Tỵ groups
        # 1986 Dần-group? 1986 is Dần year; 1984 Tý; 1989 Tỵ
        _, s = stars(y)
        assert (s["Đào Hoa"], s["Thiên Mã"]) == (dao, ma), y


def test_loc_ton_kinh_da_p24():
    _, s = stars(1990)  # Canh -> Lộc Tồn Thân; Kình Dậu, Đà Mùi
    assert (s["Lộc Tồn"], s["Kình Dương"], s["Đà La"]) == ("Thân", "Dậu", "Mùi")


def test_dia_kiep_khong_p24_25():
    _, s = stars(1990, hour=4)   # giờ Dần: Kiếp Sửu, Không Dậu (book example)
    assert (s["Địa Kiếp"], s["Địa Không"]) == ("Sửu", "Dậu")


def test_hoa_linh_p25():
    # 1990 Canh = dương, male -> Hỏa thuận, Linh nghịch. Ngọ year (Dần Ngọ Tuất): Hỏa starts Sửu, Linh Mão. giờ Dần = 2 steps
    _, s = stars(1990, hour=4)
    assert (s["Hỏa Tinh"], s["Linh Tinh"]) == ("Mão", "Sửu")   # Sửu+2 ; Mão-2
    _, s = stars(1990, hour=4, gender="female")                  # dương nữ -> reversed
    assert (s["Hỏa Tinh"], s["Linh Tinh"]) == ("Hợi", "Tỵ")      # Sửu-2 ; Mão+2


def test_tu_hoa_canh_both_books():
    c, _ = stars(1990)
    assert [c.tu_hoa[k]["star"] for k in ("Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ")] == \
        ["Thái Dương", "Vũ Khúc", "Thiên Đồng", "Thái Âm"]


def test_menh_worked_example_p12():
    # Kỷ Mùi (1979), tháng 5, giờ Dần -> Mệnh Thìn, Mộc tam cục. Find a 1979 date in lunar month 5.
    nb = normalize(BirthInput(1979, 6, 3, 4, 0, "Asia/Ho_Chi_Minh", "male"))
    assert nb.lunar.month == 5 and nb.lunar.year == 1979
    c = tuvi.compute(nb)
    assert BRANCHES_VI[c.menh_branch] == "Thìn" and c.cuc["name"] == "Mộc tam cục"
