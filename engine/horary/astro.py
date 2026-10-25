"""Astronomy adapter for horary: everything comes from engine/western (JPL DE440s through Skyfield) for 1899-2101.

Outside that span (study charts such as Lilly's 1640s examples) PyEphem (VSOP87 / ELP-2000, an independent analytical
theory) is used and the chart says so in `ephemeris`. Nothing here judges anything.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from western import ephemeris as W

TRAD = ("saturn", "jupiter", "mars", "sun", "venus", "mercury", "moon")       # Chaldean order (slowest first)
OUTER = ("uranus", "neptune", "pluto")                                         # drawn on the wheel, never significators
JD_UNIX0 = 2440587.5


@dataclass(frozen=True)
class Pos:
    lon: float
    lat: float
    speed: float        # degrees/day in longitude, negative = retrograde
    ra: float
    dec: float
    dist_au: float


def in_range(jd_ut: float | np.ndarray) -> bool:
    try:
        W.time_jd_ut(np.atleast_1d(np.asarray(jd_ut, dtype=float)))
        return True
    except W.OutOfRange:
        return False


def source(jd_ut: float) -> dict:
    if in_range(jd_ut):
        return {"id": "de440s", "label": "JPL DE440s qua Skyfield (engine/western)", "fallback": False}
    return {"id": "pyephem", "label": "PyEphem VSOP87/ELP-2000 (ngoài khoảng 1899-2101 của DE440s đi kèm; dùng cho lá số nghiên cứu)",
            "fallback": True}


# ------------------------------------------------------------------ positions

def positions(jd_ut: float, bodies=TRAD + OUTER) -> dict[str, Pos]:
    if in_range(jd_ut):
        t = W.time_jd_ut(jd_ut)
        h = 1 / 24
        tt = W.time_jd_ut(np.array([jd_ut - h, jd_ut + h]))
        out = {}
        for b in bodies:
            p = W.positions(b, t)
            # speed = time derivative of the APPARENT longitude (central difference over +-1 h), as the Swiss Ephemeris reports it.
            # Skyfield's own rate leaves out the slow change of aberration (~1e-4 deg/day), enough to move a slow planet's station
            # by an hour; stations, retrogradation and application are all judged on the apparent longitude itself.
            l0, l1 = W.longitude(b, tt)
            out[b] = Pos(p.lon, p.lat, ((l1 - l0 + 180.0) % 360.0 - 180.0) / (2 * h), p.ra, p.dec, p.dist_au)
        return out
    return {b: _ephem_pos(b, jd_ut) for b in bodies}


def longitudes(jd_ut: np.ndarray, body: str) -> np.ndarray:
    """Vectorised apparent longitudes (the event search samples these on a grid)."""
    jd = np.atleast_1d(np.asarray(jd_ut, dtype=float))
    if in_range(jd):
        return np.atleast_1d(W.longitude(body, W.time_jd_ut(jd)))
    return np.array([_ephem_lonlat(body, float(j))[0] for j in jd])


def sidereal_obliquity(jd_ut: float) -> tuple[float, float, float]:
    """(GAST degrees, true obliquity degrees, nutation in longitude degrees). The fallback has no nutation: mean obliquity,
    GAST from PyEphem; the chart reports the fallback."""
    if in_range(jd_ut):
        return W.sidereal_and_obliquity(W.time_jd_ut(jd_ut))
    import ephem
    obs = ephem.Observer()
    obs.date, obs.lon, obs.lat, obs.pressure = jd_ut - 2415020.0, "0", "0", 0
    T = (jd_ut - 2451545.0) / 36525
    eps = 23.4392911111 - (46.8150 * T + 0.00059 * T * T - 0.001813 * T ** 3) / 3600
    return math.degrees(obs.sidereal_time()) % 360.0, eps, 0.0


def nodes(jd_ut: float) -> dict[str, float | None]:
    """Mean node (Lilly's era had only the mean node) and the osculating 'true' node when DE440s covers the date."""
    if in_range(jd_ut):
        t = W.time_jd_ut(jd_ut)
        return {"mean": W.moon_mean_node(t), "true": W.moon_osculating_node(t)}
    T = (jd_ut - 2451545.0) / 36525
    om = (125.0445479 - 1934.1362891 * T + 0.0020754 * T * T + T ** 3 / 467441 - T ** 4 / 60616000) % 360.0
    return {"mean": om, "true": None}


# ------------------------------------------------------------------ sunrise / sunset (planetary hours)

def sun_events(jd_start: float, jd_end: float, lat: float, lon: float) -> list[tuple[float, bool]]:
    """(jd_ut, is_rise) of every sunrise and sunset in the window: the Sun's upper limb on the horizon with standard
    refraction (-0.8333 degree), the almanac definition. Returns [] when the Sun neither rises nor sets (polar day/night)."""
    if in_range(jd_start) and in_range(jd_end):
        from skyfield import almanac
        from skyfield.api import wgs84
        f = almanac.sunrise_sunset(W._eph(), wgs84.latlon(lat, lon))
        ts = W.timescale()
        times, ups = almanac.find_discrete(ts.ut1_jd(jd_start), ts.ut1_jd(jd_end), f)
        return [(float(t.ut1), bool(u)) for t, u in zip(times, ups)]
    import ephem
    obs = ephem.Observer()
    obs.lat, obs.lon, obs.horizon, obs.pressure = str(lat), str(lon), "-0:50", 0
    sun, out, d = ephem.Sun(), [], jd_start
    while d < jd_end:
        obs.date = d - 2415020.0
        nxt = []
        for fn, rise in ((obs.next_rising, True), (obs.next_setting, False)):
            try:
                nxt.append((float(fn(sun)) + 2415020.0, rise))
            except (ephem.AlwaysUpError, ephem.NeverUpError):
                pass
        if not nxt:
            return out
        j, rise = min(nxt)
        if j > jd_end:
            break
        out.append((j, rise))
        d = j + 1e-4
    return out


# ------------------------------------------------------------------ PyEphem fallback

_EPH = {"sun": "Sun", "moon": "Moon", "mercury": "Mercury", "venus": "Venus", "mars": "Mars", "jupiter": "Jupiter",
        "saturn": "Saturn", "uranus": "Uranus", "neptune": "Neptune", "pluto": "Pluto"}


def _ephem_lonlat(name: str, jd_ut: float):
    import ephem
    body = getattr(ephem, _EPH[name])()
    d = ephem.Date(jd_ut - 2415020.0)
    body.compute(d, epoch=d)              # geocentric apparent, equinox of date
    ecl = ephem.Ecliptic(ephem.Equatorial(body.g_ra, body.g_dec, epoch=d), epoch=d)
    return math.degrees(ecl.lon) % 360.0, math.degrees(ecl.lat), body


def _ephem_pos(name: str, jd_ut: float) -> Pos:
    lon, lat, body = _ephem_lonlat(name, jd_ut)
    h = 1 / 24
    l0, l1 = _ephem_lonlat(name, jd_ut - h)[0], _ephem_lonlat(name, jd_ut + h)[0]
    speed = (((l1 - l0 + 180) % 360) - 180) / (2 * h)
    return Pos(lon, lat, speed, math.degrees(body.g_ra) % 360.0, math.degrees(body.g_dec), float(body.earth_distance))


# ------------------------------------------------------------------ calendar helpers

def julian_calendar_to_jd(year: int, month: int, day: float) -> float:
    """Julian Day of a date in the Julian (Old Style) calendar, 0h UT = .5 (Meeus ch. 7, B = 0). Lilly dates his questions
    Old Style; the test-suite uses this to rebuild his figures."""
    if month <= 2:
        year, month = year - 1, month + 12
    return math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day - 1524.5


def gregorian_to_jd(year: int, month: int, day: float) -> float:
    if month <= 2:
        year, month = year - 1, month + 12
    a = year // 100
    b = 2 - a + a // 4
    return math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + b - 1524.5
