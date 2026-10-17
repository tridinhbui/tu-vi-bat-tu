"""Cách đặc biệt theo Thiệu Vĩ Hoa pp.369-376 kiểm bằng chính các ví dụ của sách (mỗi cách 2-5 lá số), cộng bảng thành/bại và bảng dụng thần pp.367-386."""
import json

import pytest

from tvbt.bazi_deep import geju, interact, strength, tvh_cach, yongshen
from tvbt.bazi_deep.model import ChartView
from tvbt.bazi_deep.profile import DEFAULT, TVH_40

BOOK = {
    "Khúc Trực": ["Quý Mão / Giáp Dần / Giáp Dần / Giáp Tý", "Quý Hợi / Giáp Dần / Ất Mão / Quý Mùi", "Ất Mùi / Kỷ Mão / Giáp Dần / Ất Hợi", "Đinh Hợi / Nhâm Dần / Giáp Thìn / Mậu Thìn", "Nhâm Dần / Quý Mão / Giáp Thìn / Mậu Thìn"],
    "Viêm Thượng": ["Đinh Tỵ / Bính Ngọ / Bính Ngọ / Ất Mùi", "Giáp Tuất / Bính Dần / Bính Ngọ / Canh Dần", "Giáp Ngọ / Bính Dần / Đinh Mão / Bính Ngọ", "Ất Mùi / Tân Tỵ / Bính Ngọ / Giáp Ngọ"],
    "Gia Sắc": ["Mậu Thìn / Kỷ Mùi / Mậu Thìn / Quý Sửu", "Mậu Thìn / Kỷ Mùi / Kỷ Tỵ / Mậu Thìn", "Kỷ Tỵ / Mậu Thìn / Mậu Tuất / Kỷ Mùi", "Bính Thìn / Mậu Tuất / Kỷ Sửu / Kỷ Tỵ", "Đinh Sửu / Đinh Mùi / Kỷ Sửu / Mậu Thìn"],
    "Tòng Cách": ["Mậu Thân / Tân Dậu / Canh Tuất / Ất Dậu", "Mậu Thân / Tân Dậu / Tân Tỵ / Kỷ Sửu", "Canh Thân / Ất Dậu / Canh Tuất / Ất Dậu", "Mậu Thân / Canh Thân / Tân Dậu / Mậu Tuất", "Mậu Thân / Canh Thân / Canh Thân / Giáp Thân"],
    "Nhuận Hạ": ["Nhâm Thân / Nhâm Tý / Nhâm Thìn / Canh Tý", "Nhâm Thân / Tân Hợi / Nhâm Tý / Canh Tý", "Nhâm Tý / Quý Sửu / Tân Hợi / Bính Thân", "Tân Hợi / Canh Tý / Quý Sửu / Nhâm Tý"],
    "Tòng Tài": ["Mậu Tuất / Bính Thìn / Ất Mùi / Bính Tuất"],
    "Tòng Sát": ["Nhâm Tý / Quý Sửu / Bính Tý / Canh Tý", "Bính Dần / Giáp Ngọ / Canh Ngọ / Bính Tuất"],
    "Tòng Nhi": ["Ất Tỵ / Bính Tuất / Ất Mùi / Bính Tuất", "Mậu Tý / Tân Dậu / Kỷ Dậu / Nhâm Thân"],
    "Hóa Mộc": ["Bính Dần / Canh Dần / Đinh Mão / Nhâm Dần", "Giáp Thìn / Đinh Mão / Nhâm Dần / Giáp Thìn"],
    "Hóa Hỏa": ["Bính Dần / Quý Tỵ / Mậu Thìn / Mậu Ngọ"],
    "Hóa Thổ": ["Đinh Mùi / Giáp Thìn / Kỷ Dậu / Mậu Thìn", "Mậu Thìn / Bính Thìn / Giáp Tý / Kỷ Sửu"],
    "Hóa Kim": ["Giáp Thân / Nhâm Thân / Ất Sửu / Canh Thìn", "Mậu Tuất / Tân Dậu / Ất Dậu / Canh Thìn"],
    "Hóa Thủy": ["Nhâm Tý / Quý Sửu / Tân Hợi / Bính Thân", "Giáp Thìn / Bính Tý / Tân Hợi / Nhâm Thìn"],
}
KNOWN_GAPS = {   # the engine does not reproduce these; reasons documented
    "Giáp Tuất / Giáp Ngọ / Đinh Tỵ / Nhâm Dần": "Viêm Thượng ví dụ 2: sách coi Nhâm là hư phù vô lực, nhưng Canh trong Tỵ (tạp khí) cho Nhâm chỗ dựa theo phép thử của chính sách (ví dụ 1 trang 347 tính như vậy)",
    "Nhâm Dần / Nhâm Tý / Đinh Hợi / Quý Sửu": "Nhuận Hạ ví dụ 4: cần 'thê tòng phu hóa' (Đinh–Nhâm), chưa hỗ trợ",
}


def names(text):
    v = ChartView.from_names(text)
    return [c["name"].replace(" (TVH)", "") for c in tvh_cach.special(v, strength.compute_hybrid(v, TVH_40), TVH_40)]


@pytest.mark.parametrize("cach,text", [(c, t) for c, ts in BOOK.items() for t in ts])
def test_book_example_is_recognised(cach, text):
    assert cach in names(text), (cach, text, names(text))


@pytest.mark.xfail(strict=True, reason="documented gap")
@pytest.mark.parametrize("text", sorted(KNOWN_GAPS))
def test_known_gaps_are_still_gaps(text):
    cach = "Viêm Thượng" if "Ngọ" in text else "Nhuận Hạ"
    assert cach in names(text)


def test_known_gap_reasons_are_written_down():
    assert all(len(v) > 30 for v in KNOWN_GAPS.values())


def test_ordinary_charts_are_not_special():
    for t in ("Giáp Tý / Bính Dần / Giáp Tuất / Canh Ngọ", "Tân Mão / Đinh Dậu / Giáp Thìn / Giáp Tý", "Canh Thân / Ất Dậu / Ất Dậu / Tân Tỵ"):
        assert names(t) == [], t


def test_an_enemy_stem_with_root_breaks_chuyen_vuong_but_a_rootless_one_does_not():
    base = "Quý Mão / Giáp Dần / Giáp Dần / Giáp Tý"
    assert "Khúc Trực" in names(base)
    assert "Khúc Trực" not in names("Quý Dậu / Giáp Dần / Giáp Dần / Giáp Tý")        # Dậu khắc mộc is in the chart
    v = ChartView.from_names("Canh Dần / Giáp Dần / Giáp Dần / Giáp Tý")                  # Canh on the stem
    r = tvh_cach.score(v)
    rooted = r["notes"]["steps"][0]["root"][0]                                             # Mậu in Dần gives Canh a root under the book's own test
    assert rooted and "Khúc Trực" not in names("Canh Dần / Giáp Dần / Giáp Dần / Giáp Tý")


def test_special_cach_replaces_the_inner_cach_in_the_reading_and_selects_thuan_the():
    v = ChartView.from_names("Quý Mão / Giáp Dần / Giáp Dần / Giáp Tý")
    R = interact.resolve(v, TVH_40)
    S = strength.compute_hybrid(v, TVH_40, R)
    G = geju.analyse(v, TVH_40, R, S)
    assert any(o["name"] == "Khúc Trực" and o["kind"] == "chuyen_vuong" for o in G["outer"])
    Y = yongshen.run(v, TVH_40, R, S, G)
    assert Y["methods"]["thuan_the"]["outer"] in ("Khúc Trực", "Tòng Vượng") and Y["methods"]["phu_uc"]["status"] == "khong_ap_dung"


# ---------- thành / bại sentences
def test_every_thanh_bai_rule_parses_and_is_labelled():
    d = json.loads((geju.DATA / "tvh_thanhbai.json").read_text("utf-8"))
    assert d["_status"] == "verified_text"
    v = ChartView.from_names("Giáp Tý / Bính Dần / Giáp Tuất / Canh Ngọ")
    R = interact.resolve(v, TVH_40); S = strength.compute_hybrid(v, TVH_40, R); ctx = geju.Ctx(v, TVH_40, R, S)
    for cach, rules in d["rules"].items():
        for r in rules:
            assert r["verdict"] in ("tot", "xau") and r["page"] and len(r["text"]) > 20
            for e in r["all"]:
                geju.pred(ctx, e)


def test_tot_and_xau_are_reported_side_by_side_not_summed():
    v = ChartView.from_names("Quý Dậu / Ất Mão / Mậu Tý / Đinh Tỵ")                       # EX2: Chính Quan with both good and bad sentences
    R = interact.resolve(v, TVH_40); S = strength.compute_hybrid(v, TVH_40, R)
    G = geju.analyse(v, TVH_40, R, S)
    dg = G["inner"][0]["tvh_danh_gia"]
    assert {x["verdict"] for x in dg} == {"tot", "xau"} and "score" not in G["inner"][0]


# ---------- dụng thần decision table
def test_dungthan_table_is_complete_and_consistent():
    d = yongshen.TVH_DT
    groups = {"Ti", "An", "Tai", "QuanSat", "ThucThuong"}
    keys = set(d["cach_key"].values())
    assert keys == {"tai", "quan", "an", "thuong_quan", "sat", "thuc", "kien_loc", "kinh_duong"}
    for k in keys:
        dms = {r["dm"] for r in d["rows"] if r["cach"] == k}
        assert dms == {"strong", "weak"}, k
    for r in d["rows"]:
        assert set(r["yong"]) <= groups and set(r["van_tot"] or []) <= groups and set(r["van_xau"] or []) <= groups and r["dom"] in groups and r["page"]
        assert not (set(r["yong"][:1]) & set(r["van_xau"] or [])), r          # the main dụng thần is never in the same row's bad-vận list
    assert len({(r["cach"], r["dm"], r["dom"]) for r in d["rows"]}) == len(d["rows"])


def test_dungthan_rows_quote_the_books_examples():
    row = yongshen._tvh_row
    assert row("quan", "strong", "Ti")["yong"][0] == "QuanSat" and row("quan", "weak", "Tai")["yong"][0] == "Ti"      # PDF p.378-379
    assert row("sat", "strong", "QuanSat")["yong"] == ["ThucThuong"] and row("sat", "weak", "Tai")["van_xau"] == ["Tai", "ThucThuong"]   # pp.380, 384
    assert row("thuong_quan", "weak", "ThucThuong")["van_tot"] == ["QuanSat", "An"]                                  # p.385
    assert row("kien_loc", "weak", "Tai")["yong"] == ["Ti"] and row("kinh_duong", "weak", "Tai")["yong"] == ["An"]   # p.381


def test_cach_cuc_tvh_method_picks_by_strength_and_dominant_group():
    S = {"shares": {"Ti": 0.50, "An": 0.10, "ThucThuong": 0.10, "Tai": 0.10, "QuanSat": 0.20}, "level_index": 5, "ambiguous": False, "tvh": {"dm_strong": True}}
    G = {"readings": [{"cach": "Chính Quan", "kind": "noi_cach"}], "inner": [], "outer": []}
    m = yongshen.cach_cuc_tvh(G, S)
    assert m["status"] == "ap_dung" and m["dm"] == "vượng" and m["dominant"] == "Ti" and m["yong"] == ["QuanSat"] and m["ji"] == ["An", "Ti"]
    S2 = {**S, "ambiguous": True}
    m2 = yongshen.cach_cuc_tvh(G, S2)
    assert m2["status"] == "hai_cach_doc" and {a["dm"] for a in m2["alternatives"]} == {"strong", "weak"}
    assert yongshen.cach_cuc_tvh({"readings": [{"cach": "Hóa Thổ", "kind": "ngoai_cach"}], "inner": [], "outer": []}, S)["status"] == "khong_xac_dinh_noi_cach"


def test_cach_cuc_tvh_is_a_separate_method_in_the_comparison():
    v = ChartView.from_names("Tân Mão / Đinh Dậu / Giáp Thìn / Giáp Tý")
    R = interact.resolve(v, TVH_40); S = strength.compute_hybrid(v, TVH_40, R); G = geju.analyse(v, TVH_40, R, S)
    Y = yongshen.run(v, TVH_40, R, S, G)
    assert "cach_cuc_tvh" in Y["methods"] and Y["methods"]["cach_cuc_tvh"]["method"] == "cach_cuc_tvh"
    assert any("cach_cuc_tvh" in r["roles"] for r in Y["comparison"]["rows"])


def test_special_cach_dungthan_uses_the_cach_element_and_the_books_van_lists():
    S = {"by_element": {"Mộc": 0, "Hỏa": 0, "Thổ": 100, "Kim": 0, "Thủy": 0}, "dm_element": "Thổ"}
    out = yongshen.thuan_the({"outer": [{"name": "Gia Sắc", "kind": "chuyen_vuong", "quality": "chân", "element": "Thổ"}]}, S, TVH_40)
    assert out["need_elements"] == ["Thổ"] and out["van_tot_elements"] == ["Thổ", "Kim", "Thủy"] and out["van_xau_elements"] == ["Mộc", "Hỏa"]      # p.385
    t = yongshen.thuan_the({"outer": [{"name": "Tòng Sát (TVH)", "kind": "tong_tvh", "quality": "chân"}]}, S, TVH_40)
    assert t["yong"] == ["Tai"] and t["ji"] == ["An", "Ti"] and t["source"] == "SRC_TVH_DUNGTHAN"                                          # pp.381, 385
