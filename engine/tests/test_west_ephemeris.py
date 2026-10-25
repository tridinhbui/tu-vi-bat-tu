"""Western engine astronomy against two independent references.

1. Swiss Ephemeris 2.10 (the library Astro.com computes with), 249 random instants 1900-2100 and latitudes -66..+70
   (fixture made by tools/west/make_swe_reference.py; Swiss is a dev-only tool, never imported by the site).
2. JPL Horizons observer tables (quantity 31: apparent ecliptic longitude/latitude of date, geocentre), fetched 2026-10-25.
"""
import json
import pathlib

import pytest

from western import ephemeris as E, houses as H

REF = json.loads((pathlib.Path(__file__).parent / "fixtures" / "west_swe_reference.json").read_text())["cases"]
d = lambda a, b: (a - b + 180) % 360 - 180
ARCSEC = 1 / 3600


def _tt(c):
    return E.timescale().tt_jd(c["jd_ut"] + c["deltat_days"])     # Swiss delta T, so only the ephemerides are compared


@pytest.mark.parametrize("name,tol", [(n, 0.05) for n in E.PLANETS] + [("chiron", 2.0)])
def test_bodies_match_swiss(name, tol):
    worst = max(abs(d(E.positions(name, _tt(c)).lon, c["bodies"][name]["lon"])) for c in REF) / ARCSEC
    worst_lat = max(abs(E.positions(name, _tt(c)).lat - c["bodies"][name]["lat"]) for c in REF) / ARCSEC
    assert worst < tol and worst_lat < tol


def test_speed_and_retrograde_flag_match_swiss():
    for c in REF:
        t = _tt(c)
        for n in E.PLANETS:
            p, r = E.positions(n, t), c["bodies"][n]
            assert abs(p.speed - r["speed"]) < 10 * ARCSEC
            if abs(r["speed"]) > 1e-3:
                assert (p.speed < 0) == (r["speed"] < 0)


def test_lunar_nodes_match_swiss():
    for c in REF:
        t = _tt(c)
        assert abs(d(E.moon_osculating_node(t), c["bodies"]["true_node"]["lon"])) < 0.5 * ARCSEC
        assert abs(d(E.moon_mean_node(t), c["bodies"]["mean_node"]["lon"])) < 0.5 * ARCSEC


@pytest.mark.parametrize("system", ["placidus", "equal", "whole_sign", "porphyry"])
def test_house_cusps_and_angles_match_swiss(system):
    checked = 0
    for c in REF:
        t = E.timescale().ut1_jd(c["jd_ut"])
        gast, eps, _ = E.sidereal_and_obliquity(t)
        armc = (gast + c["lon"]) % 360
        r = c["houses"][system]
        if "error" in r:                       # Swiss refuses Placidus beyond the polar circle: so must we
            with pytest.raises(H.PolarHouses):
                H.cusps(system, armc, eps, c["lat"])
            continue
        # sidereal time agrees to 0.002" up to 2050; later the UT1 extrapolations of the two libraries drift (< 2")
        tol = (0.01 if c["jd_ut"] < 2469807.5 else 6.0) * ARCSEC
        cs = H.cusps(system, armc, eps, c["lat"])
        assert max(abs(d(a, b)) for a, b in zip(cs, r["cusps"])) < tol
        assert abs(d(H.ascendant(armc, eps, c["lat"]), r["asc"])) < tol
        assert abs(d(H.midheaven(armc, eps), r["mc"])) < tol
        checked += 1
    assert checked > 200


# (UT, Horizons body id, apparent ecliptic lon, lat) from https://ssd.jpl.nasa.gov/api/horizons.api, QUANTITIES=31, CENTER=500@399
HORIZONS = [
    ((2000, 1, 1, 12, 0), "sun", 280.3689092, 0.0002381), ((2000, 1, 1, 12, 0), "moon", 223.3237860, 5.1707422),
    ((2000, 1, 1, 12, 0), "mars", 327.9632921, -1.0677752), ((2000, 1, 1, 12, 0), "jupiter", 25.2530685, -1.2621868),
    ((2000, 1, 1, 12, 0), "chiron", 251.6176090, 4.0717061),
    ((1990, 5, 17, 3, 30), "sun", 55.9825693, 0.0000335), ((1990, 5, 17, 3, 30), "moon", 317.8620847, 0.6715215),
    ((1990, 5, 17, 3, 30), "mars", 349.5556671, -1.7470039), ((1990, 5, 17, 3, 30), "jupiter", 99.8547732, 0.1449052),
    ((1990, 5, 17, 3, 30), "chiron", 103.3452259, -6.3980861),
    ((1969, 7, 20, 20, 17), "sun", 117.9107302, -0.0001002), ((1969, 7, 20, 20, 17), "moon", 187.8737519, -1.3631482),
    ((1969, 7, 20, 20, 17), "mars", 242.7732832, -3.3930191), ((1969, 7, 20, 20, 17), "jupiter", 180.7462243, 1.2191714),
    ((1969, 7, 20, 20, 17), "chiron", 6.8273609, 3.0106479),
]


@pytest.mark.parametrize("ut,name,lon,lat", HORIZONS)
def test_matches_jpl_horizons(ut, name, lon, lat):
    import datetime as dt
    t = E.time_utc(dt.datetime(*ut, tzinfo=dt.timezone.utc))     # Horizons 'UT' is UT1 before 1972, UTC after
    p = E.positions(name, t)
    tol = (2.0 if name == "chiron" else 0.5) * ARCSEC      # Horizons uses its own delta T for UT; the Moon moves 0.5"/s
    assert abs(d(p.lon, lon)) < tol and abs(p.lat - lat) < tol


def test_out_of_range_is_refused():
    with pytest.raises(E.OutOfRange):
        E.time_jd_ut(2400000.5)
