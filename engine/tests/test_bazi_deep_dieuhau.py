import json

from bazi_deep_util import EX, view
from tvbt.bazi_deep import dieuhau, geju, interact, strength, yongshen
from tvbt.bazi_deep.profile import DEFAULT
from tvbt.ganzhi import BRANCHES_HAN, STEMS_HAN


def test_table_has_120_cells_of_valid_distinct_stems_and_is_flagged_unchecked():
    d = json.loads((dieuhau.DATA / "dieu_hau_ctbg_draft.json").read_text("utf-8"))
    assert d["_status"].startswith("draft") and d["checked_cells"] == []
    assert set(d["cells"]) == set(STEMS_HAN)
    for s, row in d["cells"].items():
        assert set(row) == set(BRANCHES_HAN)
        for cell in row.values():
            assert 1 <= len(cell) <= 4 and len(set(cell)) == len(cell) and all(c in STEMS_HAN for c in cell), (s, cell)


def test_lookup_orders_stems_and_reports_presence():
    r = dieuhau.lookup(view("EX1"))                       # Giáp sinh tháng Dần
    assert [x["stem"] for x in r["yong_stems"]] == ["Bính", "Quý"] and r["yong_stems"][0]["rank"].startswith("chính") and r["chu"] == "Bính"
    assert r["yong_stems"][0]["visible"] is True and r["yong_stems"][1]["hidden"] is True       # Bính on the stems; Quý hidden in Tý
    assert r["satisfied"] is True and r["status"] == "tap_va_thu_tu_TVH_verified" and r["checked"] is True and r["src"] == "SRC_TVH_DIEUHAU"
    e8 = dieuhau.lookup(view("EX8"))                      # Bính sinh tháng Tý
    assert e8["yong_stems"][0]["stem"] == "Nhâm" and e8["satisfied"] is False


def test_method_gives_ten_god_roles_from_the_table_and_keeps_coarse_climate_aside():
    v = view("EX1"); R = interact.resolve(v); S = strength.compute(v, DEFAULT, R)
    m = yongshen.dieu_hau(v, S)
    assert m["status"] == "bang_TVH_verified" and m["yong"] == ["ThucThuong"] and m["xi"] == ["An"] and m["source"] == "SRC_TVH_DIEUHAU"
    assert "climate" in m and "Thiệu Vĩ Hoa" in m["note"] and "tr.391-396" in m["note"]      # the ranking inside a cell now follows the book's notes


def test_method_stays_separate_from_phu_uc_and_cach_cuc_in_comparison():
    v = view("EX3"); R = interact.resolve(v); S = strength.compute(v, DEFAULT, R); G = geju.analyse(v, DEFAULT, R, S)
    Y = yongshen.run(v, DEFAULT, R, S, G)
    assert Y["methods"]["dieu_hau"]["yong"] != [] and Y["methods"]["phu_uc"]["method"] == "phu_uc"
    rows = {r["group"]: r["roles"] for r in Y["comparison"]["rows"]}
    assert any("dieu_hau" in roles for roles in rows.values())


def test_every_example_gets_a_lookup():
    for k in EX:
        r = dieuhau.lookup(view(k))
        assert r["yong_stems"] and r["yong_stems"][0]["group"] in ("Ti", "An", "Tai", "QuanSat", "ThucThuong")


def test_tvh_table_is_complete_and_the_memory_based_draft_agrees_with_it_mostly():
    import json
    tvh = json.loads((dieuhau.DATA / "tvh_dieuhau.json").read_text("utf-8"))["cells"]
    assert set(tvh) == {"Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu"}
    assert all(len(row) == 10 and all(row[s] for s in row) for row in tvh.values())
    same = first = 0
    for bi, vm in zip("寅卯辰巳午未申酉戌亥子丑", ["Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu"]):
        for hi, vs in zip("甲乙丙丁戊己庚辛壬癸", ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]):
            d = {STEMS_HAN_VI[c] for c in dieuhau.TABLE[hi][bi]}
            same += d == set(tvh[vm][vs])
            first += STEMS_HAN_VI[dieuhau.TABLE[hi][bi][0]] in tvh[vm][vs]
    assert same == 108 and first == 120      # 12 cells of the memory-based draft differ from the book; its first stem is always one of the book's stems


STEMS_HAN_VI = dict(zip("甲乙丙丁戊己庚辛壬癸", ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]))


# Documented differences between the TVH table (pp.389-390) and his note list (pp.391-396): the note names extra stems or leaves one out.
NOTE_DIFFS = {("Bính", "Ngọ"), ("Bính", "Thân"), ("Đinh", "Thìn"), ("Mậu", "Ngọ"), ("Tân", "Thân"), ("Tân", "Dậu"), ("Nhâm", "Thìn"), ("Quý", "Ngọ"), ("Quý", "Mùi")}


def test_note_order_covers_every_cell_and_matches_the_table_except_documented_cells():
    d = json.loads((dieuhau.DATA / "tvh_dieuhau.json").read_text("utf-8"))
    diffs = set()
    for mon, row in d["cells"].items():
        for dm, cell in row.items():
            order = d["notes_order"][mon][dm]
            assert order and len(set(order)) == len(order)
            if set(order) != set(cell):
                diffs.add((dm, mon))
    assert diffs == NOTE_DIFFS


def test_lookup_chief_stem_is_first_of_the_note_when_in_the_table():
    d = json.loads((dieuhau.DATA / "tvh_dieuhau.json").read_text("utf-8"))
    r = dieuhau.lookup(view("EX8"))                                       # Bính sinh tháng Tý: Nhâm first
    assert r["chu"] == d["notes_order"]["Tý"]["Bính"][0] == "Nhâm"
    for x in r["yong_stems"]:
        assert x["stem"] in d["cells"]["Tý"]["Bính"]
