"""Planet positions from JPL DE440s (1899-2101 excerpt) through Skyfield, plus Chiron from JPL Horizons vectors.

All positions are geocentric, apparent (light time, aberration, light deflection), referred to the true ecliptic and
equinox of date: the tropical zodiac as astrologers and Swiss Ephemeris use it by default. Nothing here is interpretation.
"""
from __future__ import annotations

import json
import math
import pathlib
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from skyfield.api import load, load_file
from skyfield.framelib import ecliptic_frame
from skyfield.vectorlib import VectorFunction

DATA = pathlib.Path(__file__).resolve().parents[1] / "data" / "western"
EPH_FILE = DATA / "de440s_1899_2101.bsp"
CHIRON_FILE = DATA / "chiron_1899_2101.npz"
# JD (TT) range served by the ephemeris excerpt, with a margin for light time and for searches that step past an edge.
JD_MIN, JD_MAX = 2414656.5, 2488433.5

PLANETS = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto")
BODIES = PLANETS + ("chiron",)
_SEGMENT = {"sun": "sun", "moon": "moon", "mercury": "mercury", "venus": "venus", "mars": "mars barycenter",
            "jupiter": "jupiter barycenter", "saturn": "saturn barycenter", "uranus": "uranus barycenter",
            "neptune": "neptune barycenter", "pluto": "pluto barycenter"}


class OutOfRange(ValueError):
    """The requested instant is outside 1899-2101, the span of the bundled ephemeris."""


@lru_cache(maxsize=1)
def timescale():
    return load.timescale(builtin=True)


@lru_cache(maxsize=1)
def _eph():
    return load_file(str(EPH_FILE))


class _ChironHelio(VectorFunction):
    """Heliocentric ICRF state of 2060 Chiron, cubic Hermite interpolation of 4-day Horizons vectors (tools/west/build_chiron.py)."""
    center, target = 10, 2002060

    def __init__(self):
        z = np.load(CHIRON_FILE)
        self.jd, self.pos, self.vel = z["jd_tdb"], z["pos"], z["vel"]
        self.meta = json.loads(str(z["meta"]))
        self.step = float(self.jd[1] - self.jd[0])

    def _at(self, t):
        tdb = np.asarray(t.tdb, dtype=float)
        i = np.clip(((tdb - self.jd[0]) // self.step).astype(int), 0, len(self.jd) - 2)
        h = self.step
        s = (tdb - self.jd[i]) / h
        p0, p1, v0, v1 = self.pos[i], self.pos[i + 1], self.vel[i] * h, self.vel[i + 1] * h
        s = s[..., None] if s.ndim else s
        h00, h10, h01, h11 = 2 * s**3 - 3 * s**2 + 1, s**3 - 2 * s**2 + s, -2 * s**3 + 3 * s**2, s**3 - s**2
        p = h00 * p0 + h10 * v0 + h01 * p1 + h11 * v1
        d00, d10, d01, d11 = 6 * s**2 - 6 * s, 3 * s**2 - 4 * s + 1, -6 * s**2 + 6 * s, 3 * s**2 - 2 * s
        v = (d00 * p0 + d10 * v0 + d01 * p1 + d11 * v1) / h
        return p.T, v.T, None, None


@lru_cache(maxsize=1)
def _chiron():
    return _eph()["sun"] + _ChironHelio()


def chiron_meta() -> dict:
    return _chiron().vector_functions[-1].meta


def body(name: str):
    return _chiron() if name == "chiron" else _eph()[_SEGMENT[name]]


def earth():
    return _eph()["earth"]


def time_utc(dt_utc) -> object:
    """Skyfield Time for an aware UTC datetime; raises OutOfRange outside the ephemeris.

    Before 1972 there were no leap seconds: civil clocks followed GMT / the old 'rubber' UTC, both within ~0.1 s of UT1,
    and Skyfield's pre-1972 UTC is off by a few seconds (2.7 s in 1969; the Moon moves 1.3" in that time). So an
    instant before 1972 is read as UT1, as Swiss Ephemeris' swe_utc_to_jd does."""
    import datetime as _dt
    u = dt_utc.astimezone(_dt.timezone.utc)
    if u.year < 1972:
        t = timescale().ut1(u.year, u.month, u.day, u.hour, u.minute, u.second + u.microsecond / 1e6)
    else:
        t = timescale().from_datetime(u)
    check_range(t)
    return t


def time_jd_ut(jd_ut: float | np.ndarray):
    t = timescale().ut1_jd(jd_ut)
    check_range(t)
    return t


def check_range(t):
    tt = np.atleast_1d(t.tt)
    if tt.min() < JD_MIN or tt.max() > JD_MAX:
        raise OutOfRange("ngày giờ nằm ngoài khoảng 1899-2101 của lịch thiên văn JPL DE440s đi kèm")


@dataclass(frozen=True)
class Position:
    lon: float          # ecliptic longitude of date, degrees [0, 360)
    lat: float          # ecliptic latitude, degrees
    dist_au: float
    speed: float        # longitude rate, degrees / day (negative = retrograde)
    ra: float           # right ascension of date, degrees
    dec: float          # declination of date, degrees


def positions(name: str, t) -> Position | list[Position]:
    """Apparent geocentric position of one body at Time t (scalar or array)."""
    ap = earth().at(t).observe(body(name)).apparent()
    lat, lon, dist = ap.frame_latlon(ecliptic_frame)
    ra, dec, _ = ap.radec(epoch="date")
    lon_d, lat_d = lon.degrees % 360.0, lat.degrees
    # Speed = central difference of the apparent longitude over +-1 hour. Skyfield's analytic rates of an apparent position
    # leave out the change of aberration, which moved Saturn's stations by up to 2 h against Swiss Ephemeris.
    h = 1.0 / 24.0
    ts = timescale()
    spd = ((longitude(name, ts.tt_jd(t.tt + h)) - longitude(name, ts.tt_jd(t.tt - h)) + 180.0) % 360.0 - 180.0) / (2 * h)
    if np.ndim(lon_d) == 0:
        return Position(float(lon_d), float(lat_d), float(dist.au), float(spd), float(ra._degrees), float(dec.degrees))
    return [Position(float(a), float(b), float(c), float(d), float(e), float(f))
            for a, b, c, d, e, f in zip(lon_d, lat_d, dist.au, spd, ra._degrees, dec.degrees)]


def longitude(name: str, t) -> np.ndarray | float:
    """Apparent ecliptic longitude only (vectorised; used by the event searches)."""
    ap = earth().at(t).observe(body(name)).apparent()
    lat, lon, _ = ap.frame_latlon(ecliptic_frame)
    return lon.degrees % 360.0


def sidereal_and_obliquity(t) -> tuple[float, float, float]:
    """(GAST in degrees, true obliquity of date in degrees, nutation in longitude in degrees)."""
    d_psi, d_eps = t._nutation_angles_radians
    eps = t._mean_obliquity_radians + d_eps
    return (t.gast * 15.0) % 360.0, math.degrees(eps), math.degrees(d_psi)


def moon_osculating_node(t) -> float:
    """True (osculating) lunar node: the ascending node of the Moon's instantaneous geocentric orbit, ecliptic of date."""
    geo = (body("moon") - earth()).at(t)
    r, v = geo.frame_xyz_and_velocity(ecliptic_frame)
    h = np.cross(r.au, v.au_per_d)
    return math.degrees(math.atan2(h[0], -h[1])) % 360.0


def moon_mean_node(t) -> float:
    """Mean lunar node, Meeus *Astronomical Algorithms* (2nd ed.) eq. 47.7, mean equinox of date, plus nutation in longitude."""
    T = (t.tt - 2451545.0) / 36525.0
    om = 125.0445479 - 1934.1362891 * T + 0.0020754 * T**2 + T**3 / 467441.0 - T**4 / 60616000.0
    return (om + sidereal_and_obliquity(t)[2]) % 360.0
