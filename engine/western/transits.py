"""Transits: aspects from the moving planets to natal points, with the moments a contact enters orb, is exact, and leaves.

Method: sample each transiting body's apparent longitude on a grid (hourly for the Moon, every 6 h for Mercury..Mars,
daily beyond), find where the signed distance to each aspect target changes sign (exact) or dips inside the orb, then refine
every instant by bisection on the ephemeris itself to under a minute. A retrograde planet can hit a point up to three times
while staying near it; hits inside one continuous in-orb span are one event with several exact moments.
Also: sign ingresses and stations of the transiting planets in the same window. No scoring.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

import numpy as np

from . import ephemeris as E, kb
from .zodiac import SIGNS, angdiff

UTC = dt.timezone.utc
STEP_DAYS = {"moon": 1 / 24, "sun": 0.25, "mercury": 0.25, "venus": 0.25, "mars": 0.25}
TRANSITING = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto", "chiron")
TARGETS = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto", "chiron",
           "north_node", "asc", "mc")


@dataclass
class TransitEvent:
    transiting: str
    natal: str
    aspect: str
    angle: float
    orb: float
    start: str | None          # ISO UTC when it enters orb (None if already in orb at the window start)
    end: str | None            # ISO UTC when it leaves orb (None if still in orb at the window end)
    exact: list[str] = field(default_factory=list)
    retro_at_exact: list[bool] = field(default_factory=list)
    min_orb: float = 0.0
    passes: int = 0

    def as_dict(self):
        return self.__dict__


def orb_table(scheme: str = "thienban_transit") -> dict:
    return kb.aspects()["transit_orbs"][scheme]


def _jd_to_iso(jd_ut: float) -> str:
    return (dt.datetime(2000, 1, 1, 12, tzinfo=UTC) + dt.timedelta(days=jd_ut - 2451545.0)).replace(microsecond=0).isoformat()


def _lon(body: str, jd_ut):
    return E.longitude(body, E.time_jd_ut(jd_ut))


def _bisect(body: str, target: float, a: float, b: float, level: float, fa: float) -> float:
    """Root of |angdiff(lon, target)| - level (level 0 -> signed exact crossing) between jd a and b, to ~20 s."""
    g = (lambda x: angdiff(float(_lon(body, x)), target)) if level == 0 else (lambda x: abs(angdiff(float(_lon(body, x)), target)) - level)
    for _ in range(40):
        if b - a < 2e-4:
            break
        m = (a + b) / 2
        fm = g(m)
        if (fa <= 0) == (fm <= 0):
            a, fa = m, fm
        else:
            b = m
    return (a + b) / 2


def find(natal: dict, start: dt.datetime, end: dt.datetime, transiting=TRANSITING, targets=TARGETS,
         aspects=("conjunction", "opposition", "trine", "square", "sextile"), orb_scheme: str = "thienban_transit") -> list[dict]:
    jd0, jd1 = float(E.time_utc(start).ut1), float(E.time_utc(end).ut1)
    defs = {d["id"]: d["angle"] for d in kb.aspects()["aspects"]}
    orbs = orb_table(orb_scheme)
    pts = {**natal["bodies"], **natal["points"], **natal.get("angles", {})}
    targets = [t for t in targets if t in pts and "lon" in pts[t]]
    events: list[TransitEvent] = []
    for body in transiting:
        step = STEP_DAYS.get(body, 1.0)
        grid = np.arange(jd0, jd1 + step, step)
        lon = np.asarray(_lon(body, grid))
        orb = orbs.get(body, orbs["default"])
        for tname in targets:
            L = pts[tname]["lon"]
            for asp in aspects:
                ang = defs[asp]
                for target in sorted({(L + ang) % 360.0, (L - ang) % 360.0}):
                    g = (lon - target + 180.0) % 360.0 - 180.0
                    inside = np.abs(g) <= orb
                    cross = (np.sign(g[:-1]) != np.sign(g[1:])) & (np.abs(g[:-1]) < 30) & (np.abs(g[1:]) < 30)
                    if not inside.any() and not cross.any():
                        continue
                    events += _events(body, tname, asp, ang, target, orb, grid, g, inside, cross)
    out = [e.as_dict() for e in events]
    out.sort(key=lambda e: (e["exact"][0] if e["exact"] else (e["start"] or e["end"] or "")))
    return out


def _events(body, tname, asp, ang, target, orb, grid, g, inside, cross) -> list[TransitEvent]:
    """Split the grid into continuous in-orb spans; a crossing between two samples outside the orb (a fast planet) is a span."""
    n = len(grid)
    flag = inside.copy()
    idx = np.nonzero(cross)[0]
    flag[idx] = True
    flag[idx + 1] = True
    out, i = [], 0
    while i < n:
        if not flag[i]:
            i += 1
            continue
        j = i
        while j + 1 < n and flag[j + 1]:
            j += 1
        exacts = [_bisect(body, target, grid[k], grid[k + 1], 0, g[k]) for k in range(i, j) if cross[k]]
        if not exacts and not inside[i:j + 1].any():
            i = j + 1
            continue
        if inside[i]:
            start = _bisect(body, target, grid[i - 1], grid[i], orb, abs(g[i - 1]) - orb) if i > 0 else None
        else:
            start = _bisect(body, target, grid[i], exacts[0], orb, abs(g[i]) - orb)
        if inside[j]:
            end = _bisect(body, target, grid[j], grid[j + 1], orb, abs(g[j]) - orb) if j < n - 1 else None
        else:
            end = _bisect(body, target, exacts[-1], grid[j], orb, -orb)
        retro = [E.positions(body, E.time_jd_ut(x)).speed < 0 for x in exacts]
        out.append(TransitEvent(body, tname, asp, ang, orb, _jd_to_iso(start) if start else None, _jd_to_iso(end) if end else None,
                                [_jd_to_iso(x) for x in exacts], retro,
                                0.0 if exacts else round(float(np.min(np.abs(g[i:j + 1]))), 4), len(exacts)))
        i = j + 1
    return out


def ingresses_and_stations(start: dt.datetime, end: dt.datetime, bodies=TRANSITING) -> list[dict]:
    jd0, jd1 = float(E.time_utc(start).ut1), float(E.time_utc(end).ut1)
    out = []
    for body in bodies:
        step = STEP_DAYS.get(body, 1.0)
        grid = np.arange(jd0, jd1 + step, step)
        lon = np.asarray(_lon(body, grid))
        sign = (lon // 30).astype(int)
        for k in np.nonzero(sign[:-1] != sign[1:])[0]:
            target = float(sign[k + 1] * 30 % 360) if (lon[k + 1] - lon[k]) % 360 < 180 else float(sign[k] * 30)
            x = _bisect(body, target, grid[k], grid[k + 1], 0, angdiff(lon[k], target))
            to = SIGNS[int(sign[k + 1])]
            out.append({"type": "ingress", "body": body, "time": _jd_to_iso(x), "sign": to,
                        "retrograde": bool(((lon[k + 1] - lon[k] + 180) % 360 - 180) < 0)})
        if body in ("sun", "moon"):
            continue
        d = (np.diff(lon) + 180) % 360 - 180
        for k in np.nonzero(np.sign(d[:-1]) != np.sign(d[1:]))[0]:
            a, b = grid[k], grid[k + 2]
            sp = lambda x: E.positions(body, E.time_jd_ut(x)).speed
            fa = sp(a)
            for _ in range(40):
                if b - a < 2e-4:
                    break
                m = (a + b) / 2
                if (sp(m) < 0) == (fa < 0):
                    a = m
                else:
                    b = m
            x = (a + b) / 2
            out.append({"type": "station", "body": body, "time": _jd_to_iso(x), "turns": "retrograde" if fa > 0 else "direct",
                        "lon": round(float(_lon(body, x)), 4)})
    out.sort(key=lambda e: e["time"])
    return out
