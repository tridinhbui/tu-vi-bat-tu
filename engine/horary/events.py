"""Exact event search over real ephemeris time: aspect perfections, stations and sign ingresses of the seven traditional
planets around the moment of the question.

Method: apparent longitudes from the ephemeris (engine/western, DE440s) are sampled every 6 hours; inside each sampling
interval the longitude is the local cubic through the four nearest samples (the Moon's 4th derivative keeps that within
~0.01″); roots are found on that cubic, then every root is checked against the ephemeris itself and corrected by one
Newton step, and the remaining residual is reported. Nothing is extrapolated from the speeds at the moment of the question:
an applying aspect can fail because a planet turns retrograde first (refranation), and only the real motion shows it.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from functools import lru_cache

import numpy as np

from . import astro
from .astro import TRAD

ASPECTS = {0: "conjunction", 60: "sextile", 90: "square", 120: "trine", 180: "opposition"}
STEP = 0.25


@dataclass(frozen=True)
class Perfection:
    a: str              # the faster planet at the moment of perfection (the one that applies)
    b: str
    angle: int
    jd: float
    lon_a: float
    lon_b: float
    retro_a: bool
    retro_b: bool

    def as_dict(self):
        return asdict(self) | {"kind": "perfection", "aspect": ASPECTS[self.angle]}


@dataclass(frozen=True)
class Station:
    planet: str
    jd: float
    lon: float
    turns: str          # "retrograde" | "direct"

    def as_dict(self):
        return asdict(self) | {"kind": "station"}


@dataclass(frozen=True)
class Ingress:
    planet: str
    jd: float
    sign_from: int
    sign_to: int
    retrograde: bool

    def as_dict(self):
        return asdict(self) | {"kind": "ingress"}


def _wrap(x):
    return (np.asarray(x) + 180.0) % 360.0 - 180.0


def _weights(s):
    """Lagrange weights for nodes at -1, 0, 1, 2 (equal spacing) and their derivatives (per unit s)."""
    w = np.stack([-s * (s - 1) * (s - 2) / 6, (s + 1) * (s - 1) * (s - 2) / 2, -(s + 1) * s * (s - 2) / 2, (s + 1) * s * (s - 1) / 6])
    dw = np.stack([-(3 * s * s - 6 * s + 2) / 6, (3 * s * s - 4 * s - 1) / 2, -(3 * s * s - 2 * s - 2) / 2, (3 * s * s - 1) / 6])
    return w, dw


class Grid:
    def __init__(self, jd0: float, back: float, fwd: float):
        self.t = np.arange(jd0 - back, jd0 + fwd + STEP / 2, STEP)
        self.lon = {p: astro.longitudes(self.t, p) for p in TRAD}
        self.u = {p: np.degrees(np.unwrap(np.radians(v))) for p, v in self.lon.items()}     # continuous longitude

    def cubic(self, p: str, k: np.ndarray, s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Interpolated continuous longitude and its rate (deg/day) of planet p in interval k at fraction s."""
        n = len(self.t)
        kk = np.clip(k, 1, n - 3)
        s = s + (k - kk)                                   # edge intervals: same cubic, s outside [0, 1]
        idx = kk[None, :] + np.array([-1, 0, 1, 2])[:, None]
        y = self.u[p][idx]
        w, dw = _weights(s)
        return (w * y).sum(0), (dw * y).sum(0) / STEP


def _bisect(fn, k: np.ndarray, iters: int = 48) -> np.ndarray:
    """Root of fn(k, s) in s in [0, 1] for every interval k (sign change assumed)."""
    lo, hi = np.zeros(len(k)), np.ones(len(k))
    flo = fn(k, lo)
    for _ in range(iters):
        mid = (lo + hi) / 2
        fm = fn(k, mid)
        left = np.sign(fm) == np.sign(flo)
        lo, flo = np.where(left, mid, lo), np.where(left, fm, flo)
        hi = np.where(left, hi, mid)
    return (lo + hi) / 2


def search(jd0: float, back: float = 45.0, fwd: float = 400.0) -> dict:
    """All perfections among the seven planets (Ptolemaic aspects), stations and ingresses in [jd0-back, jd0+fwd]."""
    return _search(round(float(jd0), 7), float(back), float(fwd))


@lru_cache(maxsize=32)
def _search(jd0: float, back: float, fwd: float) -> dict:
    G = Grid(jd0, back, fwd)
    t = G.t
    residuals = []

    # ---- perfections: roots on the cubic first, then one batched ephemeris check per planet
    found = []          # (a, b, angle, signed angle, jd array, va, vb)
    for i, a in enumerate(TRAD):
        for b in TRAD[i + 1:]:
            d = _wrap(G.lon[a] - G.lon[b])
            for angle in ASPECTS:
                for sgn in ((1,) if angle in (0, 180) else (1, -1)):
                    g = _wrap(d - sgn * angle)
                    ok = (np.abs(g[:-1]) < 60) & (np.abs(g[1:]) < 60) & (np.sign(g[:-1]) != np.sign(g[1:]))
                    ok |= (g[:-1] == 0)
                    k = np.where(ok)[0]
                    if not len(k):
                        continue

                    def fn(k, s, a=a, b=b, ang=sgn * angle):
                        return _wrap(G.cubic(a, k, s)[0] - G.cubic(b, k, s)[0] - ang)

                    s = _bisect(fn, k)
                    found.append((a, b, angle, sgn * angle, t[k] + s * STEP, G.cubic(a, k, s)[1], G.cubic(b, k, s)[1]))

    def exact(rows):
        """Ephemeris longitudes of both planets of every row at its times, one vectorised call per planet."""
        want: dict[str, list] = {}
        for r, (a, b, *_rest) in enumerate(rows):
            want.setdefault(a, []).append(r)
            want.setdefault(b, []).append(r)
        out = {}
        for planet, rs in want.items():
            times = np.concatenate([rows[r][4] for r in rs])
            lon = astro.longitudes(times, planet)
            pos = 0
            for r in rs:
                n = len(rows[r][4])
                out[(r, planet)] = lon[pos:pos + n]
                pos += n
        return out

    perfections = []
    if found:
        L = exact(found)
        fixed = []
        for r, (a, b, angle, ang, jd, va, vb) in enumerate(found):
            res = _wrap(L[(r, a)] - L[(r, b)] - ang)
            residuals.extend(np.abs(res).tolist())
            fixed.append((a, b, angle, ang, jd - res / (va - vb), va, vb))
        L = exact(fixed)
        for r, (a, b, angle, ang, jd, va, vb) in enumerate(fixed):
            ea, eb = L[(r, a)], L[(r, b)]
            for j in range(len(jd)):
                fast = abs(va[j]) >= abs(vb[j])
                fa, fb = (a, b) if fast else (b, a)
                perfections.append(Perfection(fa, fb, angle, float(jd[j]), float(ea[j] if fast else eb[j]),
                                              float(eb[j] if fast else ea[j]), bool((va[j] if fast else vb[j]) < 0),
                                              bool((vb[j] if fast else va[j]) < 0)))
    perfections.sort(key=lambda e: e.jd)

    # ---- stations (Sun and Moon never station)
    stations = []
    for p in TRAD:
        if p in ("sun", "moon"):
            continue
        v = G.cubic(p, np.arange(len(t) - 1), np.zeros(len(t) - 1))[1]
        k = np.where(np.sign(v[:-1]) != np.sign(v[1:]))[0]
        if not len(k):
            continue
        s = _bisect(lambda k, s, p=p: G.cubic(p, k, s)[1], k)
        jd = t[k] + s * STEP
        lon = astro.longitudes(jd, p)
        for j in range(len(k)):
            stations.append(Station(p, float(jd[j]), float(lon[j]), "retrograde" if v[k[j]] > 0 else "direct"))
    stations.sort(key=lambda e: e.jd)

    # ---- ingresses
    ingresses = []
    for p in TRAD:
        u = G.u[p]
        si = np.floor(u / 30.0)
        k = np.where(si[:-1] != si[1:])[0]
        if not len(k):
            continue
        boundary = np.where(si[k + 1] > si[k], si[k + 1], si[k]) * 30.0
        s = _bisect(lambda kk, s, p=p, bd=boundary: G.cubic(p, kk, s)[0] - bd, k)
        jd = t[k] + s * STEP
        for j in range(len(k)):
            ingresses.append(Ingress(p, float(jd[j]), int(si[k[j]] % 12), int(si[k[j] + 1] % 12), bool(si[k[j] + 1] < si[k[j]])))
    ingresses.sort(key=lambda e: e.jd)

    return {"jd0": jd0, "back": back, "fwd": fwd, "perfections": perfections, "stations": stations, "ingresses": ingresses,
            "max_residual_arcsec": float(max(residuals, default=0.0) * 3600)}


def next_ingress(ev: dict, planet: str, after: float):
    return next((x for x in ev["ingresses"] if x.planet == planet and x.jd > after), None)


def stations_between(ev: dict, planets, t0: float, t1: float) -> list[Station]:
    return [s for s in ev["stations"] if s.planet in planets and t0 < s.jd < t1]


def pair_perfections(ev: dict, a: str, b: str) -> list[Perfection]:
    return [p for p in ev["perfections"] if {p.a, p.b} == {a, b}]
