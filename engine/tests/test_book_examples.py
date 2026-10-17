"""Golden tests from the worked example charts of Tử Vi Khảo Luận pp.237-243 (Hán Cao Tổ, Hạng Võ, Khổng Minh).
Each chart is rebuilt from the book's lunar data (year pillar, lunar month/day, hour, sex) by using a modern year with the same stem-branch, and the
major stars of ALL twelve palaces, the Tứ Hóa carriers and the clearly legible Tả Hữu / Xương Khúc / Khôi Việt / Không Kiếp / Hỏa Linh / Lộc Tồn
placements must equal the printed chart. Hán Cao Tổ's hour is not printed in the legible text; exactly one hour (Ngọ) reproduces the chart.
Kình/Đà are not asserted: the book's palace blocks are not unambiguous in the PDF text layer for those two stars."""
import pytest

from tvbt import calendar_core as cc, lunar_input, tuvi

CHARTS = {
    "han_cao_to": dict(year=2014, month=11, day=13, hb=6, gender="male", cuc="Thổ ngũ cục", pillar="Giáp Ngọ",
        majors={"Huynh Đệ": {"Thiên Cơ"}, "Mệnh": {"Tử Vi"}, "Phụ Mẫu": set(), "Phúc Đức": {"Phá Quân"}, "Phu Thê": {"Thất Sát"}, "Điền Trạch": set(),
                "Tử Tức": {"Thái Dương", "Thiên Lương"}, "Quan Lộc": {"Liêm Trinh", "Thiên Phủ"}, "Tài Bạch": {"Vũ Khúc", "Thiên Tướng"},
                "Tật Ách": {"Cự Môn", "Thiên Đồng"}, "Thiên Di": {"Tham Lang"}, "Nô Bộc": {"Thái Âm"}},
        minors={"Tài Bạch": {"Tả Phụ", "Lộc Tồn"}, "Thiên Di": {"Hữu Bật"}, "Huynh Đệ": {"Địa Không", "Địa Kiếp"}, "Phụ Mẫu": {"Hỏa Tinh"},
                "Điền Trạch": {"Linh Tinh"}, "Phu Thê": {"Văn Xương"}, "Quan Lộc": {"Văn Khúc"}, "Tật Ách": {"Thiên Khôi"}},
        hoa={"Hóa Lộc": "Liêm Trinh", "Hóa Quyền": "Phá Quân", "Hóa Khoa": "Vũ Khúc", "Hóa Kỵ": "Thái Dương"}),
    "hang_vo": dict(year=1987, month=8, day=12, hb=3, gender="male", cuc="Thủy nhị cục", pillar="Đinh Mão",
        majors={"Mệnh": {"Thiên Cơ"}, "Phụ Mẫu": {"Tử Vi", "Phá Quân"}, "Điền Trạch": {"Thiên Phủ"}, "Phu Thê": {"Thái Dương"}, "Tử Tức": {"Vũ Khúc", "Thất Sát"},
                "Quan Lộc": {"Thái Âm"}, "Tài Bạch": {"Thiên Đồng", "Thiên Lương"}, "Tật Ách": {"Thiên Tướng"}, "Thiên Di": {"Cự Môn"}, "Nô Bộc": {"Liêm Trinh", "Tham Lang"}},
        minors={"Mệnh": {"Hỏa Tinh", "Lộc Tồn"}, "Phụ Mẫu": {"Văn Xương", "Văn Khúc"}, "Phúc Đức": {"Địa Không"}, "Tài Bạch": {"Địa Kiếp"}, "Tật Ách": {"Linh Tinh"},
                "Tử Tức": {"Hữu Bật"}, "Nô Bộc": {"Tả Phụ", "Thiên Khôi"}, "Điền Trạch": {"Thiên Việt"}},
        hoa={"Hóa Lộc": "Thái Âm", "Hóa Quyền": "Thiên Đồng", "Hóa Khoa": "Thiên Cơ", "Hóa Kỵ": "Cự Môn"}),
    "khong_minh": dict(year=1981, month=4, day=10, hb=10, gender="male", cuc="Kim tứ cục", pillar="Tân Dậu",
        majors={"Huynh Đệ": {"Tử Vi"}, "Mệnh": set(), "Phụ Mẫu": {"Phá Quân"}, "Phúc Đức": set(), "Điền Trạch": {"Liêm Trinh", "Thiên Phủ"}, "Quan Lộc": {"Thái Âm"},
                "Nô Bộc": {"Tham Lang"}, "Thiên Di": {"Cự Môn", "Thiên Đồng"}, "Tật Ách": {"Vũ Khúc", "Thiên Tướng"}, "Tài Bạch": {"Thái Dương", "Thiên Lương"},
                "Tử Tức": {"Thất Sát"}, "Phu Thê": {"Thiên Cơ"}},
        minors={"Mệnh": {"Tả Phụ", "Hữu Bật"}, "Tật Ách": {"Văn Khúc"}, "Nô Bộc": {"Văn Xương"}, "Phúc Đức": {"Địa Kiếp"}, "Thiên Di": {"Địa Không"}, "Phu Thê": {"Hỏa Tinh"}},
        hoa={"Hóa Lộc": "Cự Môn", "Hóa Quyền": "Thái Dương", "Hóa Khoa": "Văn Khúc", "Hóa Kỵ": "Văn Xương"}),
    "nu_quy_mao": dict(year=1963, month=5, day=20, hb=2, gender="female", cuc="Thổ ngũ cục", pillar="Quý Mão",
        majors={"Tài Bạch": {"Thiên Đồng", "Thái Âm"}, "Tử Tức": {"Vũ Khúc", "Tham Lang"}, "Phu Thê": {"Thái Dương", "Cự Môn"}, "Huynh Đệ": {"Thiên Tướng"}, "Mệnh": {"Thiên Cơ", "Thiên Lương"},
                "Phụ Mẫu": {"Tử Vi", "Thất Sát"}, "Phúc Đức": set(), "Điền Trạch": set(), "Quan Lộc": set(), "Nô Bộc": {"Liêm Trinh", "Phá Quân"}, "Thiên Di": set(), "Tật Ách": {"Thiên Phủ"}},
        minors={}, hoa={"Hóa Lộc": "Phá Quân", "Hóa Quyền": "Cự Môn", "Hóa Khoa": "Thái Âm", "Hóa Kỵ": "Tham Lang"}),
    "mau_ty_pha_san": dict(year=1948, month=1, day=4, hb=10, gender="male", cuc="Thổ ngũ cục", pillar="Mậu Tý",
        majors={"Tài Bạch": {"Thiên Cơ"}, "Tử Tức": {"Tử Vi", "Phá Quân"}, "Phu Thê": set(), "Huynh Đệ": {"Thiên Phủ"}, "Mệnh": {"Thái Âm"}, "Phụ Mẫu": {"Liêm Trinh", "Tham Lang"},
                "Phúc Đức": {"Cự Môn"}, "Điền Trạch": {"Thiên Tướng"}, "Quan Lộc": {"Thiên Đồng", "Thiên Lương"}, "Nô Bộc": {"Vũ Khúc", "Thất Sát"}, "Thiên Di": {"Thái Dương"}, "Tật Ách": set()},
        minors={"Thiên Di": {"Hữu Bật"}, "Nô Bộc": {"Địa Kiếp"}, "Tử Tức": {"Địa Không"}, "Mệnh": {"Tả Phụ"}}, hoa={"Hóa Lộc": "Tham Lang", "Hóa Quyền": "Thái Âm", "Hóa Khoa": "Hữu Bật", "Hóa Kỵ": "Thiên Cơ"}),
}


def build(c):
    sol = lunar_input.lunar_to_solar(c["day"], c["month"], c["year"], False, "vn")[0]
    return tuvi.compute(cc.normalize(cc.BirthInput(sol.year, sol.month, sol.day, 2 * c["hb"], 0, "Asia/Ho_Chi_Minh", c["gender"])))


@pytest.mark.parametrize("name", list(CHARTS))
def test_book_example_chart_matches(name):
    c = CHARTS[name]
    tv = build(c)
    assert tv.year_gz == c["pillar"] and tv.cuc["name"] == c["cuc"]
    stars = {p["name"]: set(p["stars"]) for p in tv.palaces}
    majors = {p["name"]: set(p["major_stars"]) for p in tv.palaces}
    assert {k: majors[k] for k in c["majors"]} == c["majors"]
    for pal, want in c["minors"].items():
        assert want <= stars[pal], (pal, want - stars[pal])
    assert {k: v["star"] for k, v in tv.tu_hoa.items()} == c["hoa"]


def test_han_cao_to_hour_is_unique_and_menh_equals_than():
    c = CHARTS["han_cao_to"]
    hits = []
    for hb in range(12):
        tv = build({**c, "hb": hb})
        if {p["name"]: set(p["major_stars"]) for p in tv.palaces if p["name"] in c["majors"]} == c["majors"]:
            hits.append(hb)
    assert hits == [6]                                                 # Ngọ only
    tv = build(c)
    assert next(p for p in tv.palaces if p["name"] == "Mệnh")["is_than"]          # the book prints "MỆNH THÂN" in one palace


def test_chart_level_principles_match_the_authors_remarks():
    """The author's remarks on the three charts (pp.238-240): Hạng Võ 'ngọn nuôi gốc', 'Mệnh âm ở cung dương không đắc chính', 'Âm Nam nghịch lý';
    Khổng Minh 'Can Tân đồng hành Chi Dậu', 'Mệnh âm ở cung âm (Mùi) đắc chính', 'Âm Nam nghịch lý'; Hán Cao Tổ Mệnh dương ở Thân... dương."""
    from tvbt.reasoning import facts
    f = {n: facts.tuvi_facts(build(c))["chart"] for n, c in CHARTS.items()}
    assert (f["hang_vo"]["chart.can_chi_relation"], f["hang_vo"]["chart.menh_dac_chinh"], f["hang_vo"]["chart.am_duong_ly"]) == ("chi_sinh_can", False, "nghich_ly")
    assert (f["khong_minh"]["chart.can_chi_relation"], f["khong_minh"]["chart.menh_dac_chinh"], f["khong_minh"]["chart.am_duong_ly"]) == ("hoa", True, "nghich_ly")
    assert f["han_cao_to"]["chart.menh_dac_chinh"] is True and f["han_cao_to"]["chart.am_duong_ly"] == "thuan_ly"
