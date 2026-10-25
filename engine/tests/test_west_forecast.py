"""Forecasting engines against Swiss Ephemeris event times (tools/west/make_swe_events.py) and against their own definitions."""
import datetime as dt
import json
import pathlib

import pytest

from western import ephemeris as E, progressions as P, returns as R, transits as T
from western.chart import BirthData, compute
from western.zodiac import angdiff, sign_index

EV = json.loads((pathlib.Path(__file__).parent / "fixtures" / "west_swe_events.json").read_text())
UTC = dt.timezone.utc
SEC = 1 / 86400
HCM = dict(lat=10.8231, lon=106.6297, tz="Asia/Ho_Chi_Minh")


def _jd(iso: str) -> float:
    t = dt.datetime.fromisoformat(iso)
    return 2451545.0 + (t - dt.datetime(2000, 1, 1, 12, tzinfo=UTC)).total_seconds() / 86400


def test_solar_returns_match_swiss_solcross():
    for c in EV["solar_returns"]:
        jd = R.return_jd(c["sun"], c["jd_return_ut"] + 1.3)          # start a day off, as the engine does from the birthday
        assert abs(jd - c["jd_return_ut"]) < 5 * SEC                  # 5 s: the two delta-T models differ by up to 3.4 s after 2050


@pytest.fixture(scope="module")
def events_2026_2027():
    return T.ingresses_and_stations(dt.datetime(2026, 1, 1, tzinfo=UTC), dt.datetime(2028, 1, 1, tzinfo=UTC),
                                    bodies=("mercury", "venus", "mars", "jupiter", "saturn"))


def test_ingresses_match_swiss(events_2026_2027):
    ours = [e for e in events_2026_2027 if e["type"] == "ingress"]
    assert len(ours) == len(EV["ingresses"])
    for ref in EV["ingresses"]:
        m = min((e for e in ours if e["body"] == ref["body"]), key=lambda e: abs(_jd(e["time"]) - ref["jd_ut"]))
        assert abs(_jd(m["time"]) - ref["jd_ut"]) < 60 * SEC


def test_stations_match_swiss(events_2026_2027):
    ours = [e for e in events_2026_2027 if e["type"] == "station"]
    assert len(ours) == len(EV["stations"])
    for ref in EV["stations"]:
        m = min((e for e in ours if e["body"] == ref["body"]), key=lambda e: abs(_jd(e["time"]) - ref["jd_ut"]))
        assert m["turns"] == ref["turns"] and abs(_jd(m["time"]) - ref["jd_ut"]) < 10 / 1440   # a station is flat: 10 min


def test_transit_exact_times_match_swiss():
    for ref in EV["transits"]:
        natal = {"bodies": {"sun": {"lon": ref["target"]}}, "points": {}}
        found = T.find(natal, dt.datetime(2026, 1, 1, tzinfo=UTC), dt.datetime(2030, 1, 1, tzinfo=UTC),
                       transiting=(ref["body"],), targets=("sun",), aspects=("conjunction",))
        ours = sorted(_jd(x) for e in found for x in e["exact"])
        assert len(ours) == len(ref["exact_jd_ut"])
        for a, b in zip(ours, ref["exact_jd_ut"]):
            assert abs(a - b) < 60 * SEC


def test_transit_window_brackets_the_exact_moment_and_respects_the_orb():
    n = compute(BirthData(1990, 5, 17, 10, 30, **HCM))
    for e in T.find(n, dt.datetime(2026, 1, 1, tzinfo=UTC), dt.datetime(2026, 7, 1, tzinfo=UTC), transiting=("mars", "saturn")):
        for x in e["exact"]:
            assert (e["start"] is None or e["start"] <= x) and (e["end"] is None or x <= e["end"])
        for edge in (e["start"], e["end"]):
            if edge:
                lon = E.longitude(e["transiting"], E.time_jd_ut(_jd(edge)))
                natal = {**n["bodies"], **n["points"], **n["angles"]}[e["natal"]]["lon"]
                sep = abs(angdiff(lon, natal))
                assert abs(abs(sep - e["angle"]) - e["orb"]) < 0.01


def test_profection_cycle_is_twelve_years_whole_sign():
    n = compute(BirthData(1990, 5, 17, 10, 30, **HCM))
    cyc = R.profection_cycle(n, 96)
    assert all(c["house"] == c["age"] % 12 + 1 for c in cyc)
    assert all(cyc[i]["sign"] == cyc[i + 12]["sign"] and cyc[i]["lord"] == cyc[i + 12]["lord"] for i in range(85))
    p = R.profection(n, 36)
    assert p["sign"] == n["angles"]["asc"]["sign"] and p["lord"] == "sun" and p["start_utc"] < p["end_utc"]


def test_profection_years_start_at_the_solar_return():
    n = compute(BirthData(1990, 5, 17, 10, 30, **HCM))
    sr = R.solar_return(n, 2026)
    assert R.profection(n, 36)["start_utc"] == sr["exact_utc"]
    assert R.age_at(n, dt.datetime(2026, 5, 16, 20, 0, tzinfo=UTC)) == 35      # 32 minutes before the return
    assert R.age_at(n, dt.datetime(2026, 5, 16, 21, 0, tzinfo=UTC)) == 36


def test_day_for_a_year_key():
    n = compute(BirthData(1990, 5, 17, 10, 30, **HCM))
    when = dt.datetime(2020, 5, 17, 3, 30, tzinfo=UTC)
    jd_p, years = P.progressed_jd(n, when)
    assert abs(jd_p - (n["time"]["jd_ut"] + years)) < 1e-9 and 29.99 < years < 30.01
    pc = P.chart(n, when)
    assert abs(angdiff(pc["bodies"]["sun"]["lon"], E.positions("sun", E.time_jd_ut(jd_p)).lon)) < 1e-6


def test_progressed_moon_ingress_dates_map_back_to_the_ephemeris():
    n = compute(BirthData(1990, 5, 17, 10, 30, **HCM))
    tl = P.timeline(n, 0, 30, bodies=("moon",))
    ing = [e for e in tl["events"] if e["type"] == "ingress"]
    assert 10 <= len(ing) <= 13                                       # the progressed Moon takes ~27 years to go round
    for e in ing:
        lon = E.longitude("moon", E.time_jd_ut(n["time"]["jd_ut"] + e["age"]))
        assert min(lon % 30, 30 - lon % 30) < 0.01 and sign_index(lon + 0.02) == ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra",
                                                                                 "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"].index(e["sign"])
