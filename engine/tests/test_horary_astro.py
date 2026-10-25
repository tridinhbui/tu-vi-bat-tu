"""Horary astronomy against independent sources: Swiss Ephemeris (Moshier, fixture made by tools/horary/make_swe_fixture.py),
PyEphem (VSOP87/ELP), and Swiss Ephemeris house formulas; plus time handling and the event search."""
import json
import math
from pathlib import Path

import numpy as np
import pytest

from horary import astro, chart as C, events as E, houses as H

REF = json.loads((Path(__file__).parent / "fixtures" / "horary_swe_reference.json").read_text())


def d_arcsec(a, b):
    return abs((a - b + 180) % 360 - 180) * 3600


@pytest.mark.parametrize("case", REF["cases"][:60:3])
def test_planets_match_swiss_ephemeris(case):
    pos = astro.positions(case["jd_ut"], astro.TRAD)
    for p, ref in case["planets"].items():
        tol = 4.0 if p == "moon" else 2.0           # Moshier's own accuracy (DE440s is the reference standard)
        assert d_arcsec(pos[p].lon, ref["lon"]) < tol, (p, case["jd_ut"])
        assert abs(pos[p].lat - ref["lat"]) * 3600 < tol
        assert abs(pos[p].speed - ref["speed"]) < (2e-3 if p == "moon" else 1e-4)


def test_planets_match_pyephem_independent_theory():
    # 2062: the two libraries extrapolate delta-T differently (~40 s); the Moon moves 0.55"/s, hence the wider Moon tolerance
    for jd, moon_tol in ((2451545.0, 5.0), (2461338.25, 5.0), (2470000.5, 30.0)):
        sky = astro.positions(jd, astro.TRAD)
        ep = {p: astro._ephem_pos(p, jd) for p in astro.TRAD}
        for p in astro.TRAD:
            assert d_arcsec(sky[p].lon, ep[p].lon) < (moon_tol if p == "moon" else 3.0), (p, jd)


@pytest.mark.parametrize("row", REF["armc_cases"])
def test_regiomontanus_alcabitius_formulas_equal_swiss(row):
    for name in ("regiomontanus", "alcabitius"):
        mine = H.cusps(name, row["armc"], row["eps"], row["lat"])
        assert max(d_arcsec(a, b) for a, b in zip(mine, row[name])) < 1e-4, name


@pytest.mark.parametrize("case", REF["cases"][::4])
def test_full_chart_houses_match_swiss(case):
    gast, eps, _ = astro.sidereal_obliquity(case["jd_ut"])
    armc = (gast + case["lon"]) % 360
    assert d_arcsec(armc, case["armc"]) < 6.0            # UT1/delta-T models differ by a few arcseconds after 2050
    for name in ("regiomontanus", "alcabitius", "placidus"):
        mine = H.cusps(name, armc, eps, case["lat"])
        assert max(d_arcsec(a, b) for a, b in zip(mine, case["houses"][name])) < 12.0, name


def test_regiomontanus_equals_western_when_available():
    from western import houses as WH
    if "regiomontanus" not in getattr(WH, "SYSTEMS", ()):
        pytest.skip("engine/western has no Regiomontanus yet")
    for row in REF["armc_cases"][:50]:
        a = H.cusps("regiomontanus", row["armc"], row["eps"], row["lat"])
        b = WH.cusps("regiomontanus", row["armc"], row["eps"], row["lat"])
        assert max(d_arcsec(x, y) for x, y in zip(a, b)) < 0.01


def test_polar_latitude_is_refused_with_a_reason():
    with pytest.raises(H.PolarHouses):
        H.cusps("regiomontanus", 10.0, 23.44, 70.0)
    assert len(H.cusps("whole_sign", 10.0, 23.44, 70.0)) == 12


def test_near_cusp_rule_moves_a_planet_within_five_degrees():
    cusps = [0.0 + 30 * i for i in range(12)]
    assert H.house_of(27.0, cusps, 5.0) == (2, True)
    assert H.house_of(24.0, cusps, 5.0) == (1, False)
    assert H.house_of(27.0, cusps, 0.0) == (1, False)


# ------------------------------------------------------------------ time

def test_dst_gap_is_refused_and_ambiguous_time_follows_fold():
    from western.timeutil import TimeError
    with pytest.raises(TimeError):
        C.compute(C.HoraryInput(2026, 3, 29, 1, 30, "Europe/London", 51.5, -0.12))
    a = C.compute(C.HoraryInput(2026, 10, 25, 1, 30, "Europe/London", 51.5, -0.12, fold=0))
    b = C.compute(C.HoraryInput(2026, 10, 25, 1, 30, "Europe/London", 51.5, -0.12, fold=1))
    assert abs((b.jd_ut - a.jd_ut) * 24 - 1.0) < 1e-6           # BST then GMT: one hour apart


def test_utc_and_jd_agree():
    ch = C.compute(C.HoraryInput(2026, 10, 25, 9, 30, "Asia/Ho_Chi_Minh", 21.0285, 105.8542))
    assert ch.utc.startswith("2026-10-25T02:30:00")
    assert abs(ch.jd_ut - astro.gregorian_to_jd(2026, 10, 25 + 2.5 / 24)) < 1e-9


def test_julian_calendar_conversion_meeus():
    assert astro.julian_calendar_to_jd(333, 1, 27.5) == 1842713.0        # Meeus, Astronomical Algorithms, ex. 7.b
    assert astro.gregorian_to_jd(1957, 10, 4.81) == pytest.approx(2436116.31)   # ex. 7.a


def test_out_of_range_dates_use_the_pyephem_fallback_and_say_so():
    ch = C.compute(C.HoraryInput(1647, 6, 10, 15, 0, "UTC", 51.5, -0.12, julian_calendar=True))
    assert ch.ephemeris["fallback"] is True and ch.ephemeris["id"] == "pyephem"


def test_planetary_hour_day_ruler_and_sequence():
    # Sunday 2026-10-25, Hanoi: the first hour after sunrise belongs to the Sun, the fourth to the Moon (Chaldean order)
    ch = C.compute(C.HoraryInput(2026, 10, 25, 9, 30, "Asia/Ho_Chi_Minh", 21.0285, 105.8542))
    ph = ch.planetary_hour
    assert ph["day_ruler"] == "sun" and ph["hour_number"] == 4 and ph["hour_ruler"] == "moon"
    assert ph["hour_start_jd"] <= ch.jd_ut < ph["hour_end_jd"]


def test_fingerprint_is_stable_and_sensitive():
    i = C.HoraryInput(2026, 10, 25, 9, 30, "Asia/Ho_Chi_Minh", 21.0285, 105.8542)
    assert C.fingerprint(C.compute(i)) == C.fingerprint(C.compute(i))
    j = C.HoraryInput(2026, 10, 25, 9, 31, "Asia/Ho_Chi_Minh", 21.0285, 105.8542)
    assert C.fingerprint(C.compute(i)) != C.fingerprint(C.compute(j))


# ------------------------------------------------------------------ events

@pytest.fixture(scope="module")
def ev():
    return E.search(astro.gregorian_to_jd(2026, 10, 25.1), 45, 400)


def test_every_perfection_is_exact_on_the_ephemeris(ev):
    assert ev["max_residual_arcsec"] < 0.5                 # cubic before the Newton step
    sample = ev["perfections"][::17]
    for p in sample:
        la = astro.longitudes(np.array([p.jd]), p.a)[0]
        lb = astro.longitudes(np.array([p.jd]), p.b)[0]
        sep = abs((la - lb + 180) % 360 - 180)
        assert abs(sep - p.angle) * 3600 < 0.05


def test_perfections_against_swiss_fixture_free_check(ev):
    """At each perfection time, Swiss Ephemeris (if installed) must see the exact aspect too (Moshier tolerance)."""
    swe = pytest.importorskip("swisseph")
    ids = {"sun": 0, "moon": 1, "mercury": 2, "venus": 3, "mars": 4, "jupiter": 5, "saturn": 6}
    for p in ev["perfections"][::9]:
        la = swe.calc_ut(p.jd, ids[p.a], swe.FLG_MOSEPH)[0][0]
        lb = swe.calc_ut(p.jd, ids[p.b], swe.FLG_MOSEPH)[0][0]
        assert abs(abs((la - lb + 180) % 360 - 180) - p.angle) * 3600 < 5.0


def test_stations_are_speed_sign_changes(ev):
    assert ev["stations"]
    for s in ev["stations"]:
        before = astro.positions(s.jd - 0.02, (s.planet,))[s.planet].speed
        after = astro.positions(s.jd + 0.02, (s.planet,))[s.planet].speed
        assert (before > 0 > after) if s.turns == "retrograde" else (before < 0 < after)


def test_ingresses_sit_on_sign_boundaries(ev):
    for g in ev["ingresses"][::11]:
        lon = astro.longitudes(np.array([g.jd]), g.planet)[0]
        assert min(lon % 30, 30 - lon % 30) * 3600 < 1.0
