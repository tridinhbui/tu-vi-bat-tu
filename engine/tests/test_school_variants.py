"""Calculation items where the repo's books disagree (tuvi.VARIANTS): each option follows its cited page, the default is the
popular-board convention (owner's decision 2026-10-22), and the chart reports which source it used."""
from tvbt import aux_stars, temporal, tuvi
from tvbt.calendar_core import BirthInput, normalize
from tvbt.reasoning.temporal_facts import tieu_han_branch


def chart(y, m, d, h, mi, g="male", **kw):
    return tuvi.compute(normalize(BirthInput(y, m, d, h, mi, "Asia/Ho_Chi_Minh", g, None, "vn", "split", False)),
                        dignity_school="khao_luan", **kw)


def test_defaults_are_reported_with_their_source():
    c = chart(2002, 1, 9, 4, 30)
    assert c.school["variants"] == {"tu_hoa_table": "KL", "tieu_han_rule": "TH", "luu_ha_table": "board"}
    assert "Khảo Luận tr.36" in c.school["variant_labels"]["tu_hoa_table"]
    assert "Thực Hành tr.27" in c.school["variant_labels"]["tieu_han_rule"]
    assert "Canh không khớp sách nào" in c.school["variant_labels"]["luu_ha_table"]


def test_tieu_han_th_p27_vs_kl_p39_40():
    # audit TV-6: 1991 Tân Mùi (âm nam), year 2026 -> TH p.27 nam thuận = Tý; KL pp.39-40 âm nam nghịch = Dần
    assert temporal.tuvi_year(chart(1991, 6, 1, 10, 0), 2026)["tieu_han_branch"] == "Tý"
    assert temporal.tuvi_year(chart(1991, 6, 1, 10, 0, tieu_han_rule="KL"), 2026)["tieu_han_branch"] == "Dần"
    # dương nam: both books agree
    a, b = chart(1990, 5, 17, 10, 30), chart(1990, 5, 17, 10, 30, tieu_han_rule="KL")
    assert tieu_han_branch(a, 37) == tieu_han_branch(b, 37)


def test_luu_ha_tables_follow_their_pages():
    # KL p.29: Đinh Thân, Canh Mão, Tân Thìn; TH p.26: Đinh Thìn, Canh Thân, Tân Mão; seven other stems agree
    assert {s: aux_stars.LUU_HA_TABLES["KL"][s] for s in (3, 6, 7)} == {3: 8, 6: 3, 7: 4}
    assert {s: aux_stars.LUU_HA_TABLES["TH"][s] for s in (3, 6, 7)} == {3: 4, 6: 8, 7: 3}
    for s in (0, 1, 2, 4, 5, 8, 9):
        assert aux_stars.LUU_HA_TABLES["KL"][s] == aux_stars.LUU_HA_TABLES["TH"][s] == aux_stars.LUU_HA[s]
    # the board (tuvi.vn #13405, Canh Tuất 1911) shows Lưu Hà at Thìn: the default keeps it
    assert aux_stars.LUU_HA_TABLES["board"][6] == 4


def test_tu_hoa_tables_differ_only_where_the_sources_do():
    T = tuvi.TU_HOA_TABLES
    assert T["KL"] == tuvi.TU_HOA
    assert [s for s in range(10) if T["TH"][s] != T["KL"][s]] == [8] and T["TH"][8][2] == "Thiên Phủ"
    assert T["TT_WS"][6] == ("Thái Dương", "Vũ Khúc", "Thái Âm", "Thiên Đồng")    # 全書 Canh (the table tuvi.vn shows for lưu Canh)
    # every lookup goes through the chart's table: đại hạn / lưu niên Hóa change with the option
    c = chart(1971, 6, 16, 10, 30, tu_hoa_table="TT_WS")
    assert tuvi.hoa_of(c, 6)[2:] == ("Thái Âm", "Thiên Đồng")
    assert tuvi.hoa_of(chart(1971, 6, 16, 10, 30), 6)[2:] == ("Thiên Đồng", "Thái Âm")
