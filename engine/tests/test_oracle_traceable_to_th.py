"""Phase 7: every star the independent oracle places is tied to a printed passage of Tử Vi Thực Hành (TH) and to that book's own WORKED EXAMPLE, so the oracle is checked against the
book, not only against production. 'how' says how the sentence was verified: van_ban = found in the PDF text layer (machine), anh_doc_ro = read in the page image (the text layer of that
line is garbled) — the test pins which is which."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oracle_tuvi_independent as O  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
B = O.B

SOURCES = [  # (formula, book page, verbatim sentence, how)
    ("Địa Kiếp thuận / Địa Không nghịch từ Hợi", 24, "Kiếp thì thuận đến giờ sinh", "van_ban"),
    ("Địa Không nghịch", 24, "Địa không lại nghịch phân minh đôi đường", "anh_doc_ro"),
    ("Kình trước Lộc Tồn", 24, "Kình đứng trước cung Lộc Tồn", "van_ban"),
    ("Đà sau Lộc Tồn", 24, "Đà la lại đứng sau lưng đó mà", "anh_doc_ro"),
    ("Thiên Hình từ Dậu theo tháng", 25, "Thiên hình lấy Dậu tháng Giêng", "van_ban"),
    ("Hỏa/Linh khởi điểm theo nhóm chi năm", 25, "Dần Ngọ Tuất nhân : Sửu Mão phương", "anh_doc_ro"),
    ("Hỏa thuận / Linh nghịch cho dương nam âm nữ", 25, "DƯƠNG NAM, ÂM NỮ : Hỏa tinh tính thuận giờ sinh", "van_ban"),
    ("Thiên Mã theo nhóm chi năm", 21, "Mã tại Thân", "van_ban"),
    ("Lộc Tồn Giáp", 21, "Người sinh năm GIÁP: Lộc Tồn an ở Dần", "anh_doc_ro"),
    ("Khôi Việt Giáp Mậu", 19, "Sinh năm GIÁP, MẬU an ở Sửu, Mùi", "van_ban"),
    ("Tứ Hóa Nhâm (TH in Thiên Phủ)", 21, "Khoa an với Thiên Phủ, Ky an với Vũ Khúc", "anh_doc_ro"),
]


def test_each_formula_has_a_printed_sentence_and_its_verification_mode_is_pinned():
    pytest.importorskip("fitz")
    sys.path.insert(0, str(ROOT / "tools"))
    import book_text as bt
    if not bt.available("TH"):
        pytest.skip("books not on this machine (the pinned fixtures carry the evidence)")
    for name, page, quote, how in SOURCES:
        found = bt.quote_on_page("TH", page, quote)
        assert found == (how == "van_ban"), (name, page, how, found)


def stars(c, branch):
    return {s for s, p in c["pos"].items() if p == branch}


def test_th24_worked_example_loc_ton_ngo_kinh_mui_da_ty():
    c = O.chart(2017, 3, 10, 6, True)                       # Đinh Dậu year: Lộc Tồn at Ngọ
    assert (c["pos"]["Lộc Tồn"], c["pos"]["Kình Dương"], c["pos"]["Đà La"]) == (B["Ngọ"], B["Mùi"], B["Tỵ"])


def test_th25_worked_examples_dia_kiep_khong_thien_hinh_and_hoa_linh():
    c = O.chart(1990, 6, 10, 2, True)                       # giờ Dần: 'Địa kiếp an ở Sửu, Địa không an ở Dậu'; tháng 6: 'Thiên Hình đóng ở cung Dần'
    assert (c["pos"]["Địa Kiếp"], c["pos"]["Địa Không"], c["pos"]["Thiên Hình"]) == (B["Sửu"], B["Dậu"], B["Dần"])
    # Dần Ngọ Tuất year, dương nam: Hỏa khởi Sửu, Linh khởi Mão, Hỏa thuận / Linh nghịch theo giờ
    c0, c1 = O.chart(1986, 5, 10, 0, True), O.chart(1986, 5, 10, 1, True)   # Bính Dần
    assert (c0["pos"]["Hỏa Tinh"], c0["pos"]["Linh Tinh"]) == (B["Sửu"], B["Mão"]) and (c1["pos"]["Hỏa Tinh"], c1["pos"]["Linh Tinh"]) == (B["Dần"], B["Dần"])
    # âm nam (Đinh Mão 1987, nhóm Hợi Mão Mùi: Hỏa khởi Dậu, Linh khởi Tuất): the directions swap
    c2, c3 = O.chart(1987, 5, 10, 0, True), O.chart(1987, 5, 10, 1, True)
    assert (c2["pos"]["Hỏa Tinh"], c2["pos"]["Linh Tinh"]) == (B["Dậu"], B["Tuất"]) and (c3["pos"]["Hỏa Tinh"], c3["pos"]["Linh Tinh"]) == (B["Thân"], B["Hợi"])


def test_th21_thien_ma_and_th19_khoi_viet_and_th22_luc_si():
    assert O.chart(2018, 5, 10, 0, True)["pos"]["Thiên Mã"] == B["Thân"]                 # Mậu Tuất (Dần Ngọ Tuất -> Thân)
    assert O.chart(2020, 5, 10, 0, True)["pos"]["Thiên Mã"] == B["Dần"]                  # Canh Tý (Thân Tý Thìn -> Dần)
    assert O.chart(2013, 5, 10, 0, True)["pos"]["Thiên Mã"] == B["Hợi"]                  # Quý Tỵ (Tỵ Dậu Sửu -> Hợi)
    assert O.chart(2015, 5, 10, 0, True)["pos"]["Thiên Mã"] == B["Tỵ"]                   # Ất Mùi (Hợi Mão Mùi -> Tỵ)
    c = O.chart(2014, 5, 10, 0, True)                                                    # Giáp Ngọ: Khôi Sửu, Việt Mùi; Lộc Tồn Dần
    assert (c["pos"]["Thiên Khôi"], c["pos"]["Thiên Việt"], c["pos"]["Lộc Tồn"]) == (B["Sửu"], B["Mùi"], B["Dần"])
    assert O.chart(2014, 5, 10, 0, True)["pos"]["Lực Sĩ"] == (B["Dần"] + 1) % 12        # dương nam: Bác Sĩ at Lộc Tồn, Lực Sĩ next clockwise
    assert O.chart(2014, 5, 10, 0, False)["pos"]["Lực Sĩ"] == (B["Dần"] - 1) % 12       # dương nữ: the other way


def test_th20_tuan_and_triet_lists():
    giap = {1974: ("Tý", "Sửu"), 1964: ("Dần", "Mão"), 1954: ("Thìn", "Tỵ"), 1944: ("Ngọ", "Mùi"), 1994: ("Thân", "Dậu"), 1984: ("Tuất", "Hợi")}    # 'Người thuộc Giáp Dần: Tí Sửu ...'
    for y, (a, b) in giap.items():
        assert O.chart(y, 5, 10, 0, True)["tuan"] == {B[a], B[b]}, y
    assert O.chart(1975, 5, 10, 0, True)["tuan"] == {B["Tý"], B["Sửu"]}                  # Ất Mão belongs to the same Giáp-Dần decade
    triet = {0: ("Thân", "Dậu"), 5: ("Thân", "Dậu"), 1: ("Ngọ", "Mùi"), 6: ("Ngọ", "Mùi"), 2: ("Thìn", "Tỵ"), 7: ("Thìn", "Tỵ"), 3: ("Dần", "Mão"), 8: ("Dần", "Mão"), 4: ("Tý", "Sửu"), 9: ("Tý", "Sửu")}
    for stem, (a, b) in triet.items():
        assert O.chart(1984 + stem, 5, 10, 0, True)["triet"] == {B[a], B[b]}, stem


def test_th12_worked_example_menh_than_cuc():
    """TH p.12: Kỷ Mùi (1979), tháng 5, giờ Dần -> Mệnh tại Thìn."""
    c = O.chart(1979, 5, 10, 2, True)
    assert c["menh"] == B["Thìn"]
