"""Phase 6 control set (KL pp.237-247, 6 charts / 10 structure rows): engine baseline, school variants and the INDEPENDENT oracle, with the book's own
verdict kept in a separate column. Mismatches are pinned as findings; nothing is adjusted to make them agree."""
import collections
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import control_charts_phase6 as C  # noqa: E402
import oracle_tuvi_independent as O  # noqa: E402
from tvbt import calendar_core as cc, lunar_input, tuvi  # noqa: E402
from tvbt.formation_explain import analyse  # noqa: E402
from tvbt.knowledge.formation import load_formations  # noqa: E402
from tvbt.knowledge.loader import load_experimental  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
VARS = load_formations(ROOT / "engine/data/experimental/formations_school_variants.json")
BASE = load_experimental()[1]
SPEC = O.V()


def prod_chart(name):
    c = C.CHARTS[name]
    sol = lunar_input.lunar_to_solar(c["ld"], c["lm"], c["ly"], False, "vn")[0]
    return tuvi.compute(cc.normalize(cc.BirthInput(sol.year, sol.month, sol.day, 2 * c["hb"], 0, "Asia/Ho_Chi_Minh", "male" if c["male"] else "female")))


@pytest.mark.parametrize("row", C.ROWS, ids=[f"{r[0]}-{r[1][7:]}" for r in C.ROWS])
def test_row_states_are_pinned_and_oracle_agrees_with_production(row):
    chart, fid, says, quote, bst, vst, basis = row
    c = C.CHARTS[chart]
    tv, o = prod_chart(chart), O.chart(c["ly"], c["lm"], c["ld"], c["hb"], c["male"])
    base = {x["id"]: x["state"] for x in analyse(tv, BASE)}
    var = {x["id"]: x["state"] for x in analyse(tv, VARS)}
    assert base[fid] == bst
    for suf, s in vst.items():
        assert var[fid + suf] == s and O.state(SPEC[fid + suf], o) == s, (chart, fid + suf)
    # every other formation stays quiet on this chart under the variants listed for it (no silent extra activation)
    active = {k for k, v in var.items() if v != "khong_hien"}
    assert {k for k in active if k.split("@")[0] == fid} == {fid + s for s in vst}


def test_chart_data_is_consistent_with_the_printed_pillars():
    names = {"han_cao_to": "Giáp Ngọ", "hang_vo": "Đinh Mão", "khong_minh": "Tân Dậu", "han_tin": "Giáp Tuất", "nu_quy_mao": "Quý Mão", "mau_ty_pha_san": "Mậu Tý"}
    for k, want in names.items():
        assert prod_chart(k).year_gz == want, k


def test_han_tin_printed_chart_matches_the_engine():
    """the new chart: majors/Tứ Hóa printed on KL pp.242-243 (Mệnh Liêm Tướng, Tài Tử Phủ + Tả Phụ + Lộc Tồn, Quan Vũ Khúc, Di Phá Quân, Ách Thiên Cơ)."""
    tv = prod_chart("han_tin")
    maj = {p["name"]: set(p["major_stars"]) for p in tv.palaces}
    assert maj["Mệnh"] == {"Liêm Trinh", "Thiên Tướng"} and maj["Tài Bạch"] == {"Tử Vi", "Thiên Phủ"}
    assert maj["Quan Lộc"] == {"Vũ Khúc"} and maj["Thiên Di"] == {"Phá Quân"} and maj["Tật Ách"] == {"Thiên Cơ"}
    assert {"Tả Phụ", "Lộc Tồn"} <= set(next(p for p in tv.palaces if p["name"] == "Tài Bạch")["stars"])
    assert {k: v["star"] for k, v in tv.tu_hoa.items()} == {"Hóa Lộc": "Liêm Trinh", "Hóa Quyền": "Phá Quân", "Hóa Khoa": "Vũ Khúc", "Hóa Kỵ": "Thái Dương"}
    assert tv.cuc["name"] == "Thổ ngũ cục"


def test_verdict_table_is_pinned_and_mismatches_are_kept():
    cnt = collections.Counter()
    for chart, fid, says, quote, bst, vst, basis in C.ROWS:
        cnt[(basis, "base", C.verdict(says, bst))] += 1
        for s in vst.values():
            cnt[(basis, "var", C.verdict(says, s))] += 1
    assert dict(cnt) == {("tong_the", "base", "khop"): 2, ("ten", "base", "khong_khop"): 2, ("ten", "var", "khong_khop"): 2, ("ten", "var", "khop"): 4,
                         ("tong_the", "base", "khong_khop"): 1, ("ten", "base", "khop"): 2, ("tong_the", "base", "sach_khong_xet"): 3,
                         ("tong_the", "var", "khop"): 5, ("tong_the", "var", "sach_khong_xet"): 4}
    # the two remaining mismatches among STRUCTURES THE BOOK NAMES are the KL-221 reading of Cơ Nguyệt Đồng Lương, which carries no breaker
    left = [(r[0], r[1][7:], s) for r in C.ROWS if r[6] == "ten" for suf, s in r[5].items() if C.verdict(r[2], s) == "khong_khop"]
    assert left == [("hang_vo", "CO_NGUYET_DONG_LUONG", "thanh"), ("mau_ty_pha_san", "CO_NGUYET_DONG_LUONG", "thanh_thuong")]


def test_quotes_exist_on_the_printed_pages_when_the_books_are_present():
    pytest.importorskip("fitz")
    sys.path.insert(0, str(ROOT / "tools"))
    import book_text as bt
    if not bt.available("KL"):
        pytest.skip("books not available on this machine")
    for chart, fid, says, (book, page, text), *_ in C.ROWS:
        assert bt.quote_on_page(book, page, text), (chart, page, text)


def test_oracle_reproduces_the_han_tin_chart_printed_in_the_book():
    """KL pp.242-243, from the book text: Mệnh Liêm Trinh + Thiên Tướng; Tài Tử Vi + Thiên Phủ + Tả Phụ + Lộc Tồn; Quan Vũ Khúc; Di Phá Quân; Ách Thiên Cơ + Khôi;
    Phụ Mẫu holds Thiên Hình, Hỏa Tinh, Thiên Việt (printed 'PHỤ ... THIÊN HÌNH ... HỎA TINH'). Uses the oracle only (no production)."""
    c = C.CHARTS["han_tin"]
    o = O.chart(c["ly"], c["lm"], c["ld"], c["hb"], c["male"])
    at = lambda i: (o["menh"] + i) % 12
    order = ["Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch", "Quan Lộc", "Nô Bộc", "Thiên Di", "Tật Ách", "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ"]
    pal = {n: at(i) for i, n in enumerate(order)}
    assert O.majors_at(o, {pal["Mệnh"]}) == {"Liêm Trinh", "Thiên Tướng"} and O.majors_at(o, {pal["Tài Bạch"]}) == {"Tử Vi", "Thiên Phủ"}
    assert O.majors_at(o, {pal["Quan Lộc"]}) == {"Vũ Khúc"} and O.majors_at(o, {pal["Thiên Di"]}) == {"Phá Quân"} and O.majors_at(o, {pal["Tật Ách"]}) == {"Thiên Cơ"}
    assert {"Tả Phụ", "Lộc Tồn"} <= O.stars_at(o, {pal["Tài Bạch"]}) and "Thiên Khôi" in O.stars_at(o, {pal["Tật Ách"]})
    assert {"Thiên Hình", "Hỏa Tinh", "Thiên Việt"} <= O.stars_at(o, {pal["Phụ Mẫu"]})
    assert o["carriers"] == {"Hóa Lộc": "Liêm Trinh", "Hóa Quyền": "Phá Quân", "Hóa Khoa": "Vũ Khúc", "Hóa Kỵ": "Thái Dương"} and o["cuc"] == 5
