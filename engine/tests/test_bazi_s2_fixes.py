"""Audit 2026-10-22 S2: the open Bát Tự calculation findings of docs/audit/bazi.md, one test each."""
import datetime as dt
import re
from pathlib import Path

from tvbt import analysis, bazi
from tvbt.api import BirthReq
from tvbt.calendar_core import ASIA_HANOI, BirthInput, normalize, zone_of

ENGINE = Path(__file__).resolve().parents[1]


def chart(y, m, d, h, mi=0, gender="male", tz="Asia/Ho_Chi_Minh"):
    return bazi.compute(normalize(BirthInput(y, m, d, h, mi, tz, gender)))


# ---------------------------------------------------------------- BZ-8: the birthplace's civil zone
def test_bz8_north_vietnam_uses_asia_hanoi_from_tzdb_backzone():
    """tzdb backzone Zone Asia/Hanoi: +08 from 1947-04-01 until October 1954, +07 since; Asia/Ho_Chi_Minh (the south) is +08 from 1959-12-31
    23:00 to 1975-06-13. A Hà Nội birth of 1965 given the southern zone was an hour off."""
    off = lambda tz, y, m=6: normalize(BirthInput(y, m, 1, 12, 0, tz, "male")).local.utcoffset()
    assert off("Asia/Hanoi", 1965) == dt.timedelta(hours=7) and off("Asia/Ho_Chi_Minh", 1965) == dt.timedelta(hours=8)
    assert off("Asia/Hanoi", 1950) == dt.timedelta(hours=8) and off("Asia/Hanoi", 1954, 11) == dt.timedelta(hours=7)
    assert off("Asia/Hanoi", 1990) == off("Asia/Ho_Chi_Minh", 1990) == dt.timedelta(hours=7)
    assert zone_of("Asia/Hanoi") is ASIA_HANOI
    # the round trip UTC -> local -> UTC holds across the 1954 change
    for t in (dt.datetime(1954, 9, 30, 15, tzinfo=dt.timezone.utc), dt.datetime(1954, 10, 1, 3, tzinfo=dt.timezone.utc)):
        assert t.astimezone(ASIA_HANOI).astimezone(dt.timezone.utc) == t


def test_bz8_the_hour_matters_for_a_northern_birth_near_a_jie():
    """大雪 1965 fell at 15:46 Beijing time on 7 December (07:46 UTC; HKO almanac), i.e. 14:46 in Hà Nội (+07) and 15:46 on the southern
    clock (+08). A Hà Nội birth at 15:15 is after the jie (子 month, 戊子 in a 乙巳 year); read on the southern clock it would be before it
    (亥 month, 丁亥)."""
    north = chart(1965, 12, 7, 15, 15, tz="Asia/Hanoi")
    south = chart(1965, 12, 7, 15, 15, tz="Asia/Ho_Chi_Minh")
    assert (north.pillars["month"].name, south.pillars["month"].name) == ("Mậu Tý", "Đinh Hợi")


def test_bz8_the_page_maps_northern_cities_to_asia_hanoi():
    js = (ENGINE / "web" / "js" / "util.js").read_text("utf-8")
    assert "placeTz" in js and re.search(r"NORTH = new Set\(\['Hà Nội', 'Hải Phòng', 'Vinh'\]\)", js)
    app = (ENGINE / "web" / "js" / "app.js").read_text("utf-8")
    assert "form.tz.value = placeTz(form.place.value)" in app and "form.tz.value = 'Asia/Ho_Chi_Minh'" not in app


# ---------------------------------------------------------------- BZ-14: bán hợp in production
def test_bz14_semi_triad_needs_the_middle_branch_zz_p20():
    """半合局 (ZZ p.20): two branches of a tam hợp, one of them the middle one. 子辰 (vượng–mộ) is one, 申辰 (sinh–mộ, no middle) is not."""
    P = lambda s, b, dm=False: bazi._pillar(0, s, b, dm)
    rel = bazi._relations({"year": P(0, 0), "month": P(2, 4), "day": P(0, 2, True), "hour": P(6, 10)})      # 子 / 辰 / 寅 / 戌
    semi = {(r["pillars"], r["element"]) for r in rel["branch_semi_triad"]}
    assert semi == {("year-month", "Thủy")}                       # 子辰 holds 子, the middle of 申子辰; 寅戌 (Hỏa, no 午) is not a bán hợp
    rel = bazi._relations({"year": P(8, 8), "month": P(2, 4), "day": P(0, 2, True), "hour": P(6, 6)})        # 申 / 辰 / 寅 / 午
    semi = {(r["pillars"], r["element"]) for r in rel["branch_semi_triad"]}
    assert ("day-hour", "Hỏa") in semi and not any(p == "year-month" for p, _ in semi)   # 寅午 yes; 申辰 (no 子) no
    # a complete triad is reported as such, not as three bán hợp
    full = bazi._relations({"year": bazi._pillar(0, 8, 8, False), "month": bazi._pillar(0, 0, 0, False),
                            "day": bazi._pillar(0, 4, 4, True), "hour": bazi._pillar(0, 2, 2, False)})
    assert full["branch_triad_complete"] and not full["branch_semi_triad"]


# ---------------------------------------------------------------- BZ-17: the relations sentence names hình
def test_bz17_relations_sentence_names_hinh():
    """1990-05-17 10:30 nam: Ngọ (year) – Ngọ (day) 自刑 (ZZ p.20 辰午酉亥自刑) was in the relation panel but not in the sentence."""
    import tvbt.api as api
    nb, bz, tv = api._compute(BirthReq(year=1990, month=5, day=17, hour=10, minute=30, gender="male"))
    assert bz.relations["branch_self_penalty"]
    text = " ".join(b["text"] for b in analysis.analyse(tv, bz)["quan-he"])
    assert "tự hình giữa trụ năm và trụ ngày" in text, text


# ---------------------------------------------------------------- BZ-23: dead conditions
def test_bz23_no_dead_conditions_left():
    for rel in ("tvbt/reasoning/facts.py", "tvbt/bazi_deep/interact.py", "tvbt/bazi_deep/temporal_deep.py", "tvbt/bazi_deep/tvh_score.py",
                "tvbt/bazi_deep/pipeline.py"):
        src = (ENGINE / rel).read_text("utf-8")
        code = "\n".join(l.split("#", 1)[0] for l in src.splitlines())
        assert " or True" not in code and "not in ()" not in code, rel


# ---------------------------------------------------------------- BZ-9/10: one strength verdict in the reading
def test_bz9_reading_gets_the_book_side_even_near_the_line():
    """TVH p.355 calls 39.6% "hơi nhược": a verdict. The facts for the prose carry the 40%-rule side always, and the system's ±3% band only as
    `near_threshold`; the cách table is read on the book's side (no two-reading row)."""
    from tvbt.bazi_deep import pipeline, strength
    from tvbt.bazi_deep.model import ChartView
    from tvbt.bazi_deep.profile import TVH_40
    import tvbt.api as api
    found = 0
    for y in range(1960, 2000):
        for m in (1, 4, 7, 10):
            nb, bz, tv = api._compute(BirthReq(year=y, month=m, day=15, hour=10, minute=0, gender="male"))
            v = ChartView.from_bazi(bz, nb.utc, "male")
            S = strength.compute_hybrid(v, TVH_40)
            if not S.get("ambiguous"):
                continue
            d = pipeline.prose_summary(v, [{"index": l.index, "stem": l.stem, "branch": l.branch, "start_year_exact": l.start_year_exact} for l in bz.luck_pillars])
            assert d["strength"]["near_threshold"] is True and d["strength"]["dm_strong"] in (True, False)
            assert d["strength"]["dm_strong"] == (d["strength"]["own_share"] >= 0.40)
            assert d["cach_tvh"]["status"] != "hai_cach_doc"
            found += 1
            if found >= 2:
                return
    assert found, "no near-threshold chart in the sweep"
