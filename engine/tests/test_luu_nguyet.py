"""Annual layer of the reference chart (tests/reference_charts/2002-01-09_0430_nam.json) for 2026: lưu stars and nguyệt hạn.
The board shows L.Kình Dương at Ngọ; Khảo Luận p.42 puts lưu Kình one palace BEHIND lưu Lộc Tồn for âm nam (here Thìn) and lưu Đà ahead
(Ngọ). The book's rule is kept (a verified calculation is not changed to match a screenshot); the disagreement is asserted, not hidden."""
from tvbt.api import BirthReq, _compute
from tvbt.temporal import tuvi_year

_, _, TV = _compute(BirthReq(year=2002, month=1, day=9, hour=4, minute=30, gender="male"))
Y = tuvi_year(TV, 2026)
LUU = {x["name"]: x["palace"] for x in Y["luu_stars"]}


def test_luu_stars_match_the_reference_board():
    want = {"Thái Tuế": "Tài Bạch", "Tang Môn": "Phu Thê", "Bạch Hổ": "Quan Lộc", "Thiên Khốc": "Phúc Đức", "Thiên Hư": "Phúc Đức",
            "Lộc Tồn": "Tật Ách", "Thiên Mã": "Phu Thê", "Thiên Khôi": "Phụ Mẫu", "Thiên Việt": "Huynh Đệ", "Văn Xương": "Phu Thê",
            "Văn Khúc": "Tài Bạch", "Đào Hoa": "Nô Bộc", "Hồng Loan": "Huynh Đệ", "Kiếp Sát": "Phụ Mẫu", "Hóa Lộc": "Thiên Di",
            "Hóa Quyền": "Phu Thê", "Hóa Khoa": "Phu Thê", "Hóa Kỵ": "Điền Trạch"}
    assert {k: LUU[k] for k in want} == want


def test_luu_kinh_da_follow_khao_luan_p42_not_the_board():
    assert LUU["Kình Dương"] == "Thiên Di" and LUU["Đà La"] == "Tài Bạch"


def test_book_and_convention_stars_are_labelled():
    basis = {x["name"]: x["basis"] for x in Y["luu_stars"]}
    assert basis["Thái Tuế"].startswith("KL") and basis["Đào Hoa"] == "thông lệ"


def test_nguyet_han_th_p115_matches_the_reference_board():
    assert Y["nguyet_han"] == {"Phúc Đức": 1, "Điền Trạch": 2, "Quan Lộc": 3, "Nô Bộc": 4, "Thiên Di": 5, "Tật Ách": 6, "Tài Bạch": 7,
                               "Tử Tức": 8, "Phu Thê": 9, "Huynh Đệ": 10, "Mệnh": 11, "Phụ Mẫu": 12}
