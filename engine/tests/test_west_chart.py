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


def test_night_chart_reverses_fortune_unless_disabled():
    night = C.BirthData(1990, 5, 17, 22, 30, **HCM)
    c = C.compute(night)
    assert not c["sect"]["is_day"] and c["lots"]["fortune"]["formula"] == "ASC + Sun - Moon"
    c2 = C.compute(night, C.ChartOptions(lot_reversal=False))
    assert c2["lots"]["fortune"]["formula"] == "ASC + Moon - Sun"


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
