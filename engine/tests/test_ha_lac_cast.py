"""Hà Lạc caster (plan steps H2/H3): tvbt.ha_lac against every example worked in the book.

Golden data: engine/data/ha_lac/golden_part1.json (Phần I of the 1974 book, pp.43-96) and worked_examples.json (the five charts of the
Phần II extract, pp.122-128). Each number there was transcribed from the printed page, not produced by this code."""
import datetime as dt
import json
from pathlib import Path

import pytest

from tvbt import ha_lac as H
from tvbt.calendar_core import BirthInput

D = Path(__file__).resolve().parents[1] / "data" / "ha_lac"
G = json.loads((D / "golden_part1.json").read_text("utf-8"))
W = json.loads((D / "worked_examples.json").read_text("utf-8"))
HX = json.loads((D / "hexagrams.json").read_text("utf-8"))
BY_NAME = {name: n for n, (name, _, _) in H.HEXAGRAMS.items()}


def lines(name):
    _, up, lo = H.HEXAGRAMS[BY_NAME[name]]
    return H.lines_of(up, lo)


def spans(dv):
    return [[d["hao"], d["from_age"], d["to_age"]] for d in dv]


def test_hexagram_table_agrees_with_the_part_ii_data():
    for h in HX["hexagrams"]:
        name, up, lo = H.HEXAGRAMS[h["number"]]
        assert (name, up, lo) == (h["name"], h["upper"], h["lower"])
        assert H.hexagram(H.lines_of(up, lo))["full_name"].lower() == h["full_name"].lower()
    assert len({(u, l) for _, u, l in H.HEXAGRAMS.values()}) == 64


def test_reductions_pp45_46():
    for cap, key in ((25, "duong"), (30, "am")):
        for total, want in G["reductions"][key].items():
            assert H.reduce_sum(int(total), cap) == want, (key, total)


@pytest.mark.parametrize("c", G["charts"], ids=lambda c: c["id"])
def test_part_i_charts(c):
    p = H.Pillars(*(tuple(c[k]) for k in ("year", "month", "day", "hour")))
    r = H.cast(p, male=c["male"], bazi_year=1973, after_winter_solstice=c.get("hoa_cong_term", 0) in (0, 6),
               hoa_cong_term=c.get("hoa_cong_term", 0))
    assert r["sum_duong"]["total"] == c["sum_duong"] and r["sum_am"]["total"] == c["sum_am"]
    assert r["sum_duong"]["trigram"] == c["trigram_duong"] and r["sum_am"]["trigram"] == c["trigram_am"]
    assert r["tien_thien"]["name"] == c["tien_thien"]
    for k in ("hoa_cong", "thien_nguyen_khi", "dia_nguyen_khi"):
        if k in c:
            assert r[k]["trigram"] == c[k], k
    if "nguyen_duong" in c:
        assert r["tien_thien"]["nguyen_duong_hao"] == c["nguyen_duong"]
        assert r["hau_thien"]["name"] == c["hau_thien"] and r["hau_thien"]["nguyen_duong_hao"] == c["nguyen_duong_ht"]
    if "dai_van_tt" in c:
        assert spans(r["tien_thien"]["dai_van"]) == c["dai_van_tt"]
    if "dai_van_ht" in c:
        assert spans(r["hau_thien"]["dai_van"]) == c["dai_van_ht"]
    for want in c.get("dai_van_ht_partial", []):
        assert want in spans(r["hau_thien"]["dai_van"])
    for k, where in c.get("where_printed", {}).items():
        assert set(where) <= set(r[k]["where"]), (k, where, r[k]["where"])
        if not where:
            assert r[k]["where"] == [], k
    for k, present in c.get("main_only", {}).items():
        assert ("chính T.T" in r[k]["where"]) == present, k


@pytest.mark.parametrize("c", G["nguyen_duong"]["cases"], ids=lambda c: c["que"])
def test_nguyen_duong_pp72_77(c):
    hours = H.BRANCHES_VI[:6] if c["hours"] == "duong" else H.BRANCHES_VI[6:]
    got = [H.nguyen_duong(lines(c["que"]), h, male=True, after_winter_solstice=True) for h in hours]
    assert got == c["hao"]


def test_thuan_hao_tables_pp78_83():
    for c in G["thuan_hao"]["cases"]:
        seasons = [True, False] if c["season"] == "any" else [c["season"] == "dc_hc"]
        for after_dc in seasons:
            for pol in ("duong", "am"):
                hours = H.BRANCHES_VI[:6] if pol == "duong" else H.BRANCHES_VI[6:]
                got = [H.nguyen_duong(lines(c["que"]), h, male=c["male"], after_winter_solstice=after_dc) for h in hours]
                assert got == c[pol], (c, after_dc, pol)
    for e in G["thuan_hao"]["examples"]:
        for after_dc in ([True, False] if e["season"] == "any" else [e["season"] == "dc_hc"]):
            assert H.nguyen_duong(lines(e["que"]), e["hour"], male=e["male"], after_winter_solstice=after_dc) == e["hao"], e


def test_hau_thien_ho_and_dai_van_pp84_86():
    for c in G["hau_thien"]["cases"]:
        ht, nd = H.hau_thien(lines(c["tien_thien"]), c["nguyen_duong"])
        assert H.hexagram(ht)["name"] == c["hau_thien"] and nd == c["nguyen_duong_ht"]
    for c in G["ho"]["cases"]:
        assert H.ho(lines(c["que"])) == {"upper": c["upper"], "lower": c["lower"]}
    for c in G["dai_van"]["cases"]:
        tt = lines(c["tien_thien"])
        dv = H.dai_van(tt, c["nguyen_duong"])
        assert spans(dv) == c["tt"]
        ht, nd = H.hau_thien(tt, c["nguyen_duong"])
        assert spans(H.dai_van(ht, nd, dv[-1]["to_age"] + 1)) == c["ht"]


@pytest.mark.parametrize("c", G["luu_nien"]["cases"], ids=lambda c: f'{c["que"]}-{c["hao"]}')
def test_luu_nien_pp88_96(c):
    got = H.luu_nien(lines(c["que"]), c["hao"], c["start_age"], bool(c["first_year_duong"]))
    assert [g["name"] for g in got] == c["years"]
    assert [g["age"] for g in got] == list(range(c["start_age"], c["start_age"] + len(c["years"])))


def test_year_polarity_of_the_book_years():
    assert H.year_is_duong(2024) and not H.year_is_duong(2001)  # Giáp Thìn (p.93), Tân Tỵ (p.94)


# ---------------------------------------------------------------- the Phần II extract's worked charts

EXTRA = {  # facts not on the page but implied by it: the year (era) and the quarter of the Hóa công printed with each chart
    "p122_mong": (1936, True, 6), "p125_canh_ngo": (1150, False, 12), "p126_at_hoi": (1155, False, 12),
    "p127_binh_dan": (1206, False, 18), "p127_mau_ty": (1168, True, 0),
}


def _span(d):
    a, b = d.get("reading") or (d["from"], d["to"])
    return [d["hao"], a, b]


@pytest.mark.parametrize("e", W["examples"], ids=lambda e: e["id"])
def test_extract_worked_charts(e):
    b = e["birth"]
    p = H.Pillars(*(tuple(b[k].split()) for k in ("year", "month", "day", "hour")))
    year, after_dc, term = EXTRA[e["id"]]
    r = H.cast(p, male=True, bazi_year=year, after_winter_solstice=after_dc, hoa_cong_term=term)
    assert r["polarity"] == (e["sex_polarity"] or "Dương nam")
    assert r["sum_am"]["total"] == e["sum_am"]["total"] and r["sum_duong"]["total"] == e["sum_duong"]["total"]
    tt, ht = r["tien_thien"], r["hau_thien"]
    assert tt["number"] == e["tien_thien"]["number"] and ht["number"] == e["hau_thien"]["number"]
    assert tt["nguyen_duong_hao"] == e["tien_thien"]["nguyen_duong_hao"]
    want_ht = e["hau_thien"]["nguyen_duong_hao"] or e["hau_thien"].get("nguyen_duong_candidates", [None])[0]
    if want_ht:
        assert ht["nguyen_duong_hao"] == want_ht
    if e["tien_thien"]["ho"]:
        assert tt["ho"] == e["tien_thien"]["ho"] and ht["ho"] == e["hau_thien"]["ho"]
    got = spans(tt["dai_van"])
    for d in e["tien_thien"]["dai_van"]:
        assert _span(d) in got, d
    got = spans(ht["dai_van"])
    for d in e["hau_thien"]["dai_van"]:
        if not d.get("position_uncertain"):
            assert _span(d) in got, d
    assert ht["dai_van"][0]["from_age"] == e["hau_thien"]["start_age"]
    for k in ("hoa_cong", "thien_nguyen_khi", "dia_nguyen_khi"):
        if e[k]["trigram"]:
            assert r[k]["trigram"] == e[k]["trigram"], k
        if e[k]["present"] is False:
            assert r[k]["where"] == [], k
        if e[k]["present"]:
            assert r[k]["where"], k


def test_p122_tue_van_age_15_is_que_cach():
    e = W["examples"][0]
    p = H.Pillars(("Bính", "Tý"), ("Quý", "Tỵ"), ("Bính", "Ngọ"), ("Tân", "Mão"))
    r = H.cast(p, male=True, bazi_year=1936, after_winter_solstice=True, hoa_cong_term=6)
    ln = H.luu_nien_at(r, 1936, e["tue_van_example"]["age"])
    assert ln["number"] == e["tue_van_example"]["to"]["number"] and ln["changed_hao"] == e["tue_van_example"]["to"]["hao"]


# ---------------------------------------------------------------- from a birth date

def test_cast_birth_uses_the_engine_pillars():
    from tvbt import bazi
    from tvbt.calendar_core import normalize
    b = BirthInput(1990, 5, 17, 8, 30, "Asia/Ho_Chi_Minh", "male")
    r = H.cast_birth(b)
    ch = bazi.compute(normalize(b))
    assert [(x["can"], x["chi"]) for x in r["pillars"]] == [(H.STEMS_VI[v.stem], H.BRANCHES_VI[v.branch]) for v in ch.pillars.values()]
    assert r["bazi_year"] == 1990 and r["hoa_cong"]["trigram"] == "Chấn"  # 17 May: after Xuân Phân, before Hạ Chí
    assert r["hau_thien"]["dai_van"][0]["from_age"] == r["tien_thien"]["dai_van"][-1]["to_age"] + 1
    assert H.luu_nien_at(r, r["bazi_year"], 30)["age"] == 30


def test_lap_xuan_decides_the_year():
    before = H.cast_birth(BirthInput(1990, 2, 3, 12, 0, "Asia/Ho_Chi_Minh", "female"))
    after = H.cast_birth(BirthInput(1990, 2, 5, 12, 0, "Asia/Ho_Chi_Minh", "female"))
    assert before["pillars"][0]["can"] == "Kỷ" and after["pillars"][0]["can"] == "Canh"
    assert before["hoa_cong"]["trigram"] == after["hoa_cong"]["trigram"] == "Khảm"


def test_summary_for_prose():
    r = H.cast_birth(BirthInput(1990, 5, 17, 8, 30, "Asia/Ho_Chi_Minh", "male"))
    s = H.summary(r, age=36)
    json.dumps(s, ensure_ascii=False)
    assert s["validated"] and s["tien_thien"]["name"] == r["tien_thien"]["full_name"]
    assert s["dai_van_now"]["from_age"] <= 36 <= s["dai_van_now"]["to_age"]
    ln = s["luu_nien_now"]
    assert ln["reading"]["que"] == ln["que"] and s["nguyen_duong_reading"]["que"] == s["tien_thien"]["name"]
    for n in range(1, 65):
        for h in range(1, 7):
            r = H.hao_reading(n, h)
            assert r["que"] == H.HEXAGRAMS[n][0] or r["que"].endswith(" " + H.HEXAGRAMS[n][0]), (n, h)
            assert (r["y_hao"] or r["menh_hop_cach"])["text"] and r["page_note"]
    assert H.hao_reading(65, 1) is None
