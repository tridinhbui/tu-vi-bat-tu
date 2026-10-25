"""Regression chart 09/01/2002 04:30 Hà Nội (audit of 2026-10-25): positions and houses against Swiss Ephemeris 2.10, Lilly's
five-degree rule, Lilly's own dignity points, progressed Mercury's retrograde loop, and transit passes grouped by loop.

Swiss values: pyswisseph 2.10 (dev-only oracle, tools/west/make_swe_reference.py), calc_ut at 2002-01-08 21:30 UT, Hà Nội
21.0245 N 105.8412 E. Swiss reads the time as UT1; we convert UTC to UT1 (-0.115 s in Jan 2002), so angles and cusps differ by
about 1.7 arcseconds (0.115 s of sidereal rotation) while body positions agree to well under one arcsecond.
"""
import collections
import datetime as dt

import pytest

from western import chart as C, progressions as P, transits as T
from western.reading import build
from western.reading.facts import Facts

UTC = dt.timezone.utc
BIRTH = C.BirthData(2002, 1, 9, 4, 30, 21.0245, 105.8412, "Asia/Ho_Chi_Minh", place="Hà Nội")
SWE_BODIES = {"sun": 288.430378, "moon": 233.08866, "mercury": 306.990228, "venus": 287.096303, "mars": 352.656588,
              "jupiter": 99.604953, "saturn": 68.861582, "uranus": 322.83929, "neptune": 307.724594, "pluto": 256.312126,
              "chiron": 273.00412}
SWE_RETRO = {"jupiter", "saturn"}
SWE_CUSPS = {"placidus": [258.264458, 289.039931, 322.399573, 356.290156, 27.192115, 53.969384],
             "regiomontanus": [258.264458, 287.290369, 321.392688, 356.290156, 26.527516, 52.631907]}
SWE_MERCURY_STATIONS = [(2452293.368, 314.4846, "retrograde"), (2452314.2276, 298.6303, "direct")]


def arcsec(a, b):
    return abs((a - b + 180) % 360 - 180) * 3600


@pytest.fixture(scope="module")
def natal():
    return C.compute(BIRTH)


def test_positions_and_retrogrades_match_swiss(natal):
    for n, lon in SWE_BODIES.items():
        assert arcsec(natal["bodies"][n]["lon"], lon) < 1.0, n
        assert natal["bodies"][n]["retrograde"] == (n in SWE_RETRO), n


def test_angles_and_cusps_match_swiss(natal):
    for sys, ref in SWE_CUSPS.items():
        for i, lon in enumerate(ref):
            assert arcsec(natal["houses"]["cusps"][sys][i]["lon"], lon) < 3.0, (sys, i + 1)
    assert natal["angles"]["asc"]["fmt"] == "18°15′" and natal["angles"]["mc"]["fmt"] == "26°17′"


def test_each_house_system_places_the_planets_as_computed(natal):
    f = Facts(natal)
    # Placidus (the wheel) / whole sign (Valens) / Lilly = Regiomontanus with the five-degree rule (Christian Astrology p.33)
    expect = {"sun": (1, 2, 2), "venus": (1, 2, 2), "mercury": (2, 3, 2), "jupiter": (7, 8, 7), "mars": (3, 4, 4), "moon": (11, 12, 12)}
    for p, (pl, ws, li) in expect.items():
        assert (natal["bodies"][p]["house"], natal["bodies"][p]["house_ws"], f.house_lilly(p)) == (pl, ws, li), p


def test_lilly_points_use_lillys_tables_not_the_chart_options(natal):
    moon = natal["conditions"]["moon"]
    # Dorothean water triplicity lists the Moon; Lilly's table gives water to Mars by day and night, so in Lilly's count the Moon
    # in Scorpio has only her fall (-4) and is peregrine (-5)
    assert "triplicity" in moon["essential"]["has"] and "score" not in moon["essential"]
    assert moon["lilly"] == {"has": [], "debilities": ["fall"], "peregrine": True, "score": -9, "tables": "lilly"}


def test_progressed_mercury_turns_back_into_capricorn_and_stations(natal):
    ev = [e for e in P.timeline(natal, 0, 40)["events"] if e["progressed"] == "mercury"]
    st = [e for e in ev if e["type"] == "station"]
    assert [(e["turns"], round(e["lon"], 2)) for e in st] == [(t, round(l, 2)) for _, l, t in SWE_MERCURY_STATIONS]
    for e, (jd, _, _) in zip(st, SWE_MERCURY_STATIONS):
        assert abs(e["age"] - (jd - natal["time"]["jd_ut"])) < 0.01          # progressed day = year of life
    ing = [e for e in ev if e["type"] == "ingress"]
    assert [(e["sign"], e["retrograde"], e["date"][:10]) for e in ing] == [("capricorn", True, "2028-04-21"), ("aquarius", False, "2037-11-06")]


def test_transit_passes_of_one_retrograde_loop_share_a_cycle(natal):
    ev = T.find(natal, dt.datetime(2026, 1, 1, tzinfo=UTC), dt.datetime(2027, 1, 1, tzinfo=UTC), transiting=("jupiter", "saturn"))
    jup_sun = [e for e in ev if (e["transiting"], e["aspect"], e["natal"]) == ("jupiter", "opposition", "sun")]
    assert len(jup_sun) == 2 and len({e["cycle"] for e in jup_sun}) == 1
    sat_jup = [e for e in ev if (e["transiting"], e["aspect"], e["natal"]) == ("saturn", "square", "jupiter")]
    assert len(sat_jup) == 3 and len({e["cycle"] for e in sat_jup}) == 1 and {e["side"] for e in sat_jup} == {"behind"}
    keys = collections.Counter((e["transiting"], e["aspect"], e["natal"], e["side"], e["start"], e["end"]) for e in ev)
    assert max(keys.values()) == 1


def test_reading_names_venus_in_the_second_for_lilly_and_never_leaks_a_placeholder(natal):
    r = build(natal, "deep", None, dt.datetime(2026, 10, 25, tzinfo=UTC))
    money = next(p for ch in r["chapters"] for p in ch["paragraphs"] if p["id"] == "tc.lilly")
    assert "Ở Nhà 2 có Mặt Trời, Sao Thủy và Sao Kim" in money["text"]
    for ch in r["chapters"]:
        for p in ch["paragraphs"]:
            assert "{" not in p["text"] and "}" not in p["text"], p["id"]
            for e in p["evidence"]:
                if e.get("house"):
                    assert e["system"], (p["id"], e)
