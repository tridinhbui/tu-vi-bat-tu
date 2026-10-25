"""Natal chart assembly: time zones, unknown time, polar latitudes, aspects, configurations, rulership structure."""
import pytest

from western import aspects as A, chart as C, timeutil as T
from western.zodiac import fmt_in_sign, sign_of

HCM = dict(lat=10.8231, lon=106.6297, tz="Asia/Ho_Chi_Minh")


def test_dst_gap_is_refused_and_fold_picks_the_offset():
    with pytest.raises(T.TimeError):
        T.resolve(2021, 3, 14, 2, 30, "America/New_York", -74.0)
    a = T.resolve(2021, 11, 7, 1, 30, "America/New_York", -74.0, fold=0)
    b = T.resolve(2021, 11, 7, 1, 30, "America/New_York", -74.0, fold=1)
    assert a.ambiguous and b.ambiguous and a.offset_hours == -4 and b.offset_hours == -5 and a.dst and not b.dst


def test_birthplace_mean_time_before_standard_time():
    r = T.resolve(1900, 3, 1, 12, 0, "Asia/Ho_Chi_Minh", 105.85)     # tzdb: LMT until 1906; Hanoi longitude
    assert r.lmt and abs(r.offset_hours - 105.85 / 15) < 1 / 3600


def test_northern_vietnam_backzone_differs_from_saigon_1960s():
    assert T.resolve(1965, 6, 1, 8, 0, "Asia/Hanoi", 105.85).offset_hours == 7
    assert T.resolve(1965, 6, 1, 8, 0, "Asia/Ho_Chi_Minh", 106.63).offset_hours == 8


def test_full_chart_structure():
    c = C.compute(C.BirthData(1990, 5, 17, 10, 30, **HCM))
    assert c["time"]["utc"].startswith("1990-05-17T03:30")
    assert c["bodies"]["sun"]["sign"] == "taurus" and c["angles"]["asc"]["sign"] == "leo"
    assert c["sect"]["is_day"] and c["lots"]["fortune"]["formula"] == "ASC + Moon - Sun"
    assert len(c["houses"]["cusps"]["placidus"]) == 12 and c["houses"]["system"] == "placidus"
    # whole-sign houses start at 0 Leo, so every cusp sits on a sign boundary
    assert all(abs(p["deg"]) < 1e-9 for p in c["houses"]["cusps"]["whole_sign"])
    # Saturn in Capricorn: domicile; it is the only self-ruled classical planet and the end of every chain here
    assert "domicile" in c["conditions"]["saturn"]["essential"]["has"]
    assert c["dispositors"]["final"] == "saturn"
    assert {"a": "sun", "b": "venus", "by": "mixed"} in c["receptions"]


def test_lot_of_fortune_rules_by_school():
    night = C.BirthData(1990, 5, 18, 2, 30, **HCM)         # night; the waning Moon (Aquarius) has risen
    c = C.compute(night)                                    # Ptolemy III.10: same formula by day and night
    assert not c["sect"]["is_day"] and c["lots"]["fortune"]["formula"] == "ASC + Moon - Sun"
    assert C.compute(night, C.ChartOptions(lot_rule="sect"))["lots"]["fortune"]["formula"] == "ASC + Sun - Moon"
    v = C.compute(night, C.ChartOptions(lot_rule="valens"))["lots"]
    assert v["moon_altitude"] > 0 and v["fortune"]["formula"] == "ASC + Sun - Moon"     # Valens III.14: Moon still up
    late = C.compute(C.BirthData(1990, 5, 17, 22, 30, **HCM), C.ChartOptions(lot_rule="valens"))  # night, Moon not yet risen
    assert not late["sect"]["is_day"] and late["lots"]["moon_altitude"] < 0 and late["lots"]["fortune"]["formula"] == "ASC + Moon - Sun"


def test_unknown_time_has_no_houses_and_flags_the_moon():
    c = C.compute(C.BirthData(1990, 5, 17, None, None, **HCM))
    assert "angles" not in c and "houses" not in c and "no_time" in c["warnings"]
    assert "moon_day_range" in c and all("asc" not in (a["a"], a["b"]) for a in c["aspects"])


def test_polar_birth_falls_back_to_porphyry():
    c = C.compute(C.BirthData(1990, 1, 10, 12, 0, lat=69.65, lon=18.96, tz="Europe/Oslo"))     # Tromsø
    assert c["houses"]["system"] == "porphyry" and "placidus_polar_fallback_porphyry" in c["warnings"]


def test_applying_and_separating():
    pts = {"mars": {"lon": 10.0, "speed": 0.6}, "saturn": {"lon": 13.0, "speed": 0.03}}
    a = A.find(pts)[0]
    assert a.type == "conjunction" and a.applying is True        # faster Mars behind slower Saturn: closing in
    pts["mars"]["lon"] = 16.0
    assert A.find(pts)[0].applying is False


def test_patterns_from_synthetic_points():
    p = lambda lon: {"lon": lon, "speed": 0.0}
    gt = A.find({"sun": p(0), "moon": p(120), "mars": p(240)})
    assert [x["type"] for x in A.patterns(gt, {"sun": 1, "moon": 1, "mars": 1})] == ["grand_trine"]
    pts = {"sun": p(0), "moon": p(90), "mars": p(180), "venus": p(270)}
    found = A.patterns(A.find(pts), pts)
    assert [x["type"] for x in found] == ["grand_cross"]      # its four T-squares are folded into it
    pts = {"sun": p(0), "moon": p(60), "mars": p(210)}
    assert any(x["type"] == "yod" and x["apex"] == "mars" for x in A.patterns(A.find(pts), pts))


def test_sign_formatting_never_rounds_into_the_next_sign():
    assert fmt_in_sign(29.99999) == "29°59′" and sign_of(29.99999) == "aries"


def test_fixed_stars_match_swiss_ephemeris():
    """Lilly's stars (western/stars.py) against swetest 2.10.04 (Astrodienst, -xf<star>; Spica from pyswisseph's built-in star),
    1 Jan 0h UT: within 0.1"."""
    from western import ephemeris as E, stars
    ref = {1900: {"regulus": 148.4477070, "spica": 202.4496, "algol": 54.7827961, "aldebaran": 68.4010860, "pollux": 111.8459366,
                  "zubenelgenubi": 223.6899558, "antares": 248.3661421},
           2050: {"regulus": 150.5324074, "spica": 204.54213, "algol": 56.8735639, "aldebaran": 70.4975959, "pollux": 113.9159133,
                  "zubenelgenubi": 225.7809905, "antares": 250.4597659}}
    for y, want in ref.items():
        got = stars.longitudes(E.timescale().utc(y, 1, 1))
        for k, v in want.items():
            assert abs(got[k] - v) * 3600 < 0.1, (y, k, got[k], v)


def test_lilly_scores_star_conjunctions_within_five_degrees():
    from western.reading.facts import Facts
    c = C.compute(C.BirthData.from_dict(dict(year=1990, month=5, day=17, hour=10, minute=30, lat=10.8231, lon=106.6297, tz="Asia/Ho_Chi_Minh")))
    f = Facts(c)
    for p in ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"):
        lines = dict(f.lilly_accidental(p))
        for star, key in (("regulus", "conj_cor_leonis"), ("spica", "conj_spica"), ("algol", "conj_caput_algol")):
            d = abs((c["bodies"][p]["lon"] - c["fixed_stars"][star]["lon"] + 180) % 360 - 180)
            assert (key in lines) == (d <= 5.0), (p, star, d)


def test_lilly_five_degree_rule_on_cusps():
    from western.houses import house_of, house_of_lilly
    cusps = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
    assert (house_of(25.1, cusps), house_of_lilly(25.1, cusps)) == (1, 2)      # 4.9 degrees before the 2nd cusp
    assert house_of_lilly(24.9, cusps) == 1                                     # 5.1 degrees before: stays
    assert house_of_lilly(356.0, cusps) == 1 and house_of_lilly(1.0, cusps) == 1   # across 0 Aries, onto the Ascendant
    small = [0, 3, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]              # a 3-degree house (high latitude)
    assert house_of_lilly(1.0, small) == 1 and house_of_lilly(2.5, small) == 2  # the nearest cusp wins


def test_lilly_points_are_independent_of_the_chart_tables():
    a = C.compute(C.BirthData(1990, 5, 17, 10, 30, **HCM), C.ChartOptions(triplicity="dorothean", terms="egyptian"))
    b = C.compute(C.BirthData(1990, 5, 17, 10, 30, **HCM), C.ChartOptions(triplicity="ptolemaic", terms="ptolemaic"))
    assert all(a["conditions"][p]["lilly"] == b["conditions"][p]["lilly"] for p in ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"))
