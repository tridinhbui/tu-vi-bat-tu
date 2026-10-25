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
    # the board walks the tiểu hạn by Thực Hành p.27 (nam thuận): tiểu hạn 2026 at Thân, tháng Giêng at Tý
    _, _, th = _compute(BirthReq(year=2002, month=1, day=9, hour=4, minute=30, gender="male", tieu_han_rule="TH"))
    yt = tuvi_year(th, 2026)
    assert yt["tieu_han_branch"] == "Thân"
    assert yt["nguyet_han"] == {"Phúc Đức": 1, "Điền Trạch": 2, "Quan Lộc": 3, "Nô Bộc": 4, "Thiên Di": 5, "Tật Ách": 6, "Tài Bạch": 7,
                                "Tử Tức": 8, "Phu Thê": 9, "Huynh Đệ": 10, "Mệnh": 11, "Phụ Mẫu": 12}


def test_nguyet_han_follows_the_default_khao_luan_tieu_han():
    # the default since 2026-10-24 is Khảo Luận pp.39-40 (âm nam nghịch): tiểu hạn 2026 at Ngọ; the same count (KL pp.40-41, TH p.115)
    # from there puts tháng Giêng two palaces on from the board's, at Tuất
    assert Y["tieu_han_branch"] == "Ngọ" and Y["tieu_han_rule"] == "KL"
    assert Y["nguyet_han"] == {"Mệnh": 1, "Phụ Mẫu": 2, "Phúc Đức": 3, "Điền Trạch": 4, "Quan Lộc": 5, "Nô Bộc": 6, "Thiên Di": 7,
                               "Tật Ách": 8, "Tài Bạch": 9, "Tử Tức": 10, "Phu Thê": 11, "Huynh Đệ": 12}
