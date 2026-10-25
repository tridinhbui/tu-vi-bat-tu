"""Angles and house cusps from ARMC, true obliquity and geographic latitude (spherical astronomy, no approximation).

Formulas: Ascendant and MC are the intersections of the ecliptic with the horizon and the meridian; Placidus trisects each
cusp's own diurnal / nocturnal semi-arc (iterated to 1e-10 degree, as in the Swiss Ephemeris documentation, sect. 6.5);
Equal starts at the Ascendant; Whole Sign starts at 0 degrees of the rising sign; Porphyry trisects the quadrants
(used only as the documented fallback when Placidus is undefined beyond the polar circles); Regiomontanus divides the
celestial equator into 30-degree arcs from the meridian and projects them onto the ecliptic through the north and south
points of the horizon (Lilly's house system, used by the readings that follow Christian Astrology).
"""
from __future__ import annotations

import math

SYSTEMS = ("placidus", "whole_sign", "equal", "porphyry", "regiomontanus")

_r, _d = math.radians, math.degrees


def _norm(x: float) -> float:
    return x % 360.0


class PolarHouses(ValueError):
    """Placidus has no solution: some cusp's semi-arc does not exist (circumpolar ecliptic points)."""


def ascendant(armc: float, eps: float, lat: float) -> float:
    a, e, f = _r(armc), _r(eps), _r(lat)
    return _norm(_d(math.atan2(math.cos(a), -(math.sin(a) * math.cos(e) + math.tan(f) * math.sin(e)))))


def midheaven(armc: float, eps: float) -> float:
    a, e = _r(armc), _r(eps)
    return _norm(_d(math.atan2(math.sin(a), math.cos(a) * math.cos(e))))


def _ra_to_lon(ra: float, eps: float) -> float:
    """Ecliptic longitude of the ecliptic point with right ascension `ra`."""
    a = _r(ra)
    return _norm(_d(math.atan2(math.sin(a), math.cos(a) * math.cos(_r(eps)))))


def _placidus_cusp(armc: float, eps: float, lat: float, frac: float, above: bool) -> float:
    """Cusp whose meridian distance is `frac` of its own semi-arc: above the horizon from the MC (houses 11, 12),
    below from the IC (houses 3, 2)."""
    tf, se = math.tan(_r(lat)), math.sin(_r(eps))
    ra = armc + (frac * 90.0 if above else 180.0 - frac * 90.0)          # start: equal division of the equator
    lon = _ra_to_lon(ra, eps)
    for _ in range(100):
        dec = math.asin(se * math.sin(_r(lon)))
        x = -tf * math.tan(dec)
        if abs(x) > 1.0:
            raise PolarHouses("Placidus: cusp would be circumpolar at this latitude")
        sda = _d(math.acos(x))                                             # semi-diurnal arc of that declination
        ra = armc + frac * sda if above else armc + 180.0 - frac * (180.0 - sda)
        new = _ra_to_lon(ra, eps)
        if abs((new - lon + 180.0) % 360.0 - 180.0) < 1e-10:
            return new
        lon = new
    raise PolarHouses("Placidus: iteration did not converge")


def cusps(system: str, armc: float, eps: float, lat: float) -> list[float]:
    """Twelve cusp longitudes, cusp 1 first."""
    asc, mc = ascendant(armc, eps, lat), midheaven(armc, eps)
    if system == "equal":
        return [_norm(asc + 30.0 * i) for i in range(12)]
    if system == "whole_sign":
        return [_norm(math.floor(asc / 30.0) * 30.0 + 30.0 * i) for i in range(12)]
    if system == "porphyry":
        q1 = (asc - mc) % 360.0                     # MC -> ASC (houses 10-12)
        q2 = 180.0 - q1                             # ASC -> IC (houses 1-3)
        c = [0.0] * 12
        c[9], c[0], c[3], c[6] = mc, asc, _norm(mc + 180), _norm(asc + 180)
        c[10], c[11] = _norm(mc + q1 / 3), _norm(mc + 2 * q1 / 3)
        c[1], c[2] = _norm(asc + q2 / 3), _norm(asc + 2 * q2 / 3)
        for i in (4, 5, 7, 8):
            c[i] = _norm(c[i - 6] + 180)
        return c
    if system == "regiomontanus":
        c = [0.0] * 12
        c[0], c[9] = asc, mc
        f, e = _r(lat), _r(eps)
        for i, h in ((10, 30.0), (11, 60.0), (1, 120.0), (2, 150.0)):
            r = _r(armc + h)
            # the house circle through the horizon's north/south points has pole height p, tan p = tan(lat) * sin(H);
            # H = 90 gives the Ascendant formula, H = 180 the IC
            tp = math.tan(f) * math.sin(_r(h))
            c[i] = _norm(_d(math.atan2(math.sin(r), math.cos(r) * math.cos(e) - tp * math.sin(e))))
        c[3], c[6] = _norm(mc + 180), _norm(asc + 180)
        for i in (4, 5, 7, 8):
            c[i] = _norm(c[i - 6] + 180)
        return c
    if system == "placidus":
        if abs(lat) >= 90.0 - eps:
            raise PolarHouses("Placidus is undefined beyond the polar circles")
        c = [0.0] * 12
        c[0], c[9] = asc, mc
        c[10] = _placidus_cusp(armc, eps, lat, 1 / 3, True)
        c[11] = _placidus_cusp(armc, eps, lat, 2 / 3, True)
        c[1] = _placidus_cusp(armc, eps, lat, 2 / 3, False)
        c[2] = _placidus_cusp(armc, eps, lat, 1 / 3, False)
        c[3], c[6] = _norm(mc + 180), _norm(asc + 180)
        for i in (4, 5, 7, 8):
            c[i] = _norm(c[i - 6] + 180)
        return c
    raise ValueError(f"unknown house system {system!r}")


def house_of(lon: float, cusp_list: list[float]) -> int:
    """House number 1-12 holding ecliptic longitude `lon` (a cusp belongs to the house it opens)."""
    for i in range(12):
        a, b = cusp_list[i], cusp_list[(i + 1) % 12]
        if (lon - a) % 360.0 < (b - a) % 360.0:
            return i + 1
    return 12
