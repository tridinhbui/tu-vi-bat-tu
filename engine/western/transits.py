"""Transits: aspects from the moving planets to natal points, with the moments a contact enters orb, is exact, and leaves.

Method: sample each transiting body's apparent longitude on a grid (hourly for the Moon, every 6 h for Mercury..Mars,
daily beyond), find where the signed distance to each aspect target changes sign (exact) or dips inside the orb, then refine
every instant by bisection on the ephemeris itself to under a minute. A retrograde planet can hit a point up to three times
while staying near it; hits inside one continuous in-orb span are one event with several exact moments.
Also: sign ingresses and stations of the transiting planets in the same window. No scoring.
"""
from __future__ import annotations

import datetime as dt
import threading
from collections import OrderedDict
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


# Samples shared by every request: the grid of a step is the multiples of that step (jd = k * step), cut into chunks of CHUNK
# points, and a chunk once computed serves every later track of the same body and step: the sky around today is the same for every
# chart, so Thời vận, the transit list and the forecast panels of all visitors reuse it. Bounded LRU (~2 MB at most).
CHUNK = 64
_SAMPLES: "OrderedDict[tuple[str, float, int], np.ndarray]" = OrderedDict()
_SAMPLES_MAX = 1024
_SAMPLES_LOCK = threading.Lock()


def _samples(body: str, step: float, k0: int, k1: int) -> np.ndarray:
    """Apparent longitudes at jd = k * step for k0 <= k < k1, from the shared chunks (missing chunks in one ephemeris call)."""
    c0, c1 = k0 // CHUNK, (k1 - 1) // CHUNK
    with _SAMPLES_LOCK:
        have = {c: _SAMPLES[(body, step, c)] for c in range(c0, c1 + 1) if (body, step, c) in _SAMPLES}
        for c in have:
            _SAMPLES.move_to_end((body, step, c))
    missing = [c for c in range(c0, c1 + 1) if c not in have]
    if missing:
        ks = np.concatenate([np.arange(c * CHUNK, (c + 1) * CHUNK) for c in missing])
        vals = np.asarray(_lon(body, ks * step), dtype=float)
        with _SAMPLES_LOCK:
            for i, c in enumerate(missing):
                have[c] = _SAMPLES[(body, step, c)] = vals[i * CHUNK:(i + 1) * CHUNK]
            while len(_SAMPLES) > _SAMPLES_MAX:
                _SAMPLES.popitem(last=False)
    allv = np.concatenate([have[c] for c in range(c0, c1 + 1)])
    return allv[k0 - c0 * CHUNK:k1 - c0 * CHUNK]


class Track:
    """One body's apparent longitude sampled on a uniform grid (shared chunks, see _samples), then read anywhere by 4-point
    Lagrange (cubic) interpolation of the unwrapped longitude. On these steps the interpolation error is far below an arcsecond,
    so every root below is found on the polynomial instead of calling the ephemeris again."""

    def __init__(self, body: str, jd0: float, jd1: float, step: float):
        self.body, self.step = body, step
        k0, k1 = int(np.floor(jd0 / step)) - 2, int(np.ceil(jd1 / step)) + 3
        self.grid = np.arange(k0, k1) * step
        self.un = np.degrees(np.unwrap(np.radians(_samples(body, step, k0, k1))))
        self.lon = self.un % 360.0

    def _k(self, x: float) -> tuple[int, float]:
        k = int(np.clip((x - self.grid[0]) // self.step, 1, len(self.grid) - 3))
        return k, (x - self.grid[k]) / self.step

    def at(self, x: float) -> float:
        k, u = self._k(x)
        y0, y1, y2, y3 = (float(v) for v in self.un[k - 1:k + 3])
        return (-u * (u - 1) * (u - 2) / 6 * y0 + (u + 1) * (u - 1) * (u - 2) / 2 * y1
                - (u + 1) * u * (u - 2) / 2 * y2 + (u + 1) * u * (u - 1) / 6 * y3)

    def speed(self, x: float) -> float:
        h = self.step / 50
        return (self.at(x + h) - self.at(x - h)) / (2 * h)


def _root(f, a: float, b: float, fa: float) -> float:
    for _ in range(50):
        if b - a < 2e-5:                       # ~2 s
            break
        m = (a + b) / 2
        fm = f(m)
        if (fa <= 0) == (fm <= 0):
            a, fa = m, fm
        else:
            b = m
    return (a + b) / 2


def _bisect(tr: "Track", target: float, a: float, b: float, level: float, fa: float) -> float:
    """Root of |angdiff(lon, target)| - level (level 0: the signed crossing itself) between jd a and b, on the track."""
    if level == 0:
        g = lambda x: (tr.at(x) - target + 180.0) % 360.0 - 180.0
    else:
        g = lambda x: abs((tr.at(x) - target + 180.0) % 360.0 - 180.0) - level
    return _root(g, a, b, fa)


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
        tr = Track(body, jd0, jd1, step)
        sel = (tr.grid >= jd0) & (tr.grid <= jd1 + step)
        grid, lon = tr.grid[sel], tr.lon[sel]
        orb = orbs.get(body, orbs["default"])
        for tname in targets:
            L = pts[tname]["lon"]
            for asp in aspects:
                ang = defs[asp]
                for target in sorted({round((L + ang) % 360.0, 9) % 360.0, round((L - ang) % 360.0, 9) % 360.0}):
                    g = (lon - target + 180.0) % 360.0 - 180.0
                    inside = np.abs(g) <= orb
                    cross = (np.sign(g[:-1]) != np.sign(g[1:])) & (np.abs(g[:-1]) < 30) & (np.abs(g[1:]) < 30)
                    if not inside.any() and not cross.any():
                        continue
                    events += _events(tr, tname, asp, ang, target, orb, grid, g, inside, cross)
    out = [e.as_dict() for e in events]
    out.sort(key=lambda e: (e["exact"][0] if e["exact"] else (e["start"] or e["end"] or "")))
    return out


def _events(tr, tname, asp, ang, target, orb, grid, g, inside, cross) -> list[TransitEvent]:
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
        body = tr.body
        exacts = [_bisect(tr, target, grid[k], grid[k + 1], 0, g[k]) for k in range(i, j) if cross[k]]
        if not exacts and not inside[i:j + 1].any():
            i = j + 1
            continue
        if inside[i]:
            start = _bisect(tr, target, grid[i - 1], grid[i], orb, abs(g[i - 1]) - orb) if i > 0 else None
        else:
            start = _bisect(tr, target, grid[i], exacts[0], orb, abs(g[i]) - orb)
        if inside[j]:
            end = _bisect(tr, target, grid[j], grid[j + 1], orb, abs(g[j]) - orb) if j < n - 1 else None
        else:
            end = _bisect(tr, target, exacts[-1], grid[j], orb, -orb)
        retro = [bool(tr.speed(x) < 0) for x in exacts]
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
        tr = Track(body, jd0, jd1, step)
        sel = np.nonzero((tr.grid >= jd0) & (tr.grid <= jd1 + step))[0]
        grid, lon = tr.grid[sel], tr.lon[sel]
        sign = (lon // 30).astype(int)
        for k in np.nonzero(sign[:-1] != sign[1:])[0]:
            fwd = ((lon[k + 1] - lon[k] + 180) % 360 - 180) > 0
            target = float((sign[k + 1] if fwd else sign[k]) * 30 % 360)
            x = _bisect(tr, target, grid[k], grid[k + 1], 0, ((lon[k] - target + 180) % 360) - 180)
            out.append({"type": "ingress", "body": body, "time": _jd_to_iso(x), "sign": SIGNS[int(sign[k + 1])], "retrograde": not fwd})
        if body in ("sun", "moon"):
            continue
        d = np.diff(tr.un[sel])
        for k in np.nonzero(np.sign(d[:-1]) != np.sign(d[1:]))[0]:
            a, b = grid[k], grid[k + 2]
            fa = tr.speed(a)
            x = _root(tr.speed, a, b, fa)
            out.append({"type": "station", "body": body, "time": _jd_to_iso(x), "turns": "retrograde" if fa > 0 else "direct",
                        "lon": round(float(tr.at(x)) % 360.0, 4)})
    out.sort(key=lambda e: e["time"])
    return out
