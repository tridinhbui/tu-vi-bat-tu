"""Secondary progressions: the sky of the n-th day after birth stands for the n-th year of life.

Day-for-a-year: a moment `years` (tropical years of 365.24219 days) after birth maps to the ephemeris instant
birth + years days. Progressed planets are ordinary apparent positions at that instant. Progressed angles need a rule of
their own (schools differ); offered: 'solar_arc' (MC advances by the progressed Sun's arc, the default here),
'solar_arc_ra' (the ARMC advances by the progressed Sun's arc in right ascension) and 'naibod' (MC advances by the Sun's
mean motion 0°59'08.33" per year). The progressed Ascendant follows from the progressed MC, natal
latitude and the obliquity of the progressed instant. Aspects to the natal chart are found with a 1° orb (convention).
"""
from __future__ import annotations

import datetime as dt

import numpy as np

from . import ephemeris as E, houses as H, kb
from .zodiac import SIGNS, angdiff, deg_in_sign, fmt_in_sign, sign_index

TROPICAL_YEAR = 365.242190
NAIBOD_DEG_PER_YEAR = 0.98564733          # Sun's mean daily motion (59'08.33")
PROGRESSED = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn")
UTC = dt.timezone.utc


def _p(lon):
    return {"lon": round(lon % 360, 6), "sign": SIGNS[sign_index(lon)], "deg": round(deg_in_sign(lon), 6), "fmt": fmt_in_sign(lon)}


def progressed_jd(natal: dict, when: dt.datetime) -> tuple[float, float]:
    """(ephemeris JD UT of the progressed day, age in tropical years at `when`)."""
    jd_birth = natal["time"]["jd_ut"]
    jd_when = float(E.time_utc(when).ut1)
    years = (jd_when - jd_birth) / TROPICAL_YEAR
    return jd_birth + years, years


def _angles(natal: dict, jd_p: float, years: float, method: str, sun_p: float) -> dict | None:
    if "angles" not in natal:
        return None
    lat = natal["input"]["lat"]
    t = E.time_jd_ut(jd_p)
    _, eps, _ = E.sidereal_and_obliquity(t)
    if method == "solar_arc_ra":
        ra_arc = E.positions("sun", t).ra - natal["bodies"]["sun"]["ra"]
        armc = float((natal["angles"]["armc"] + ra_arc) % 360)
        mc = H.midheaven(armc, eps)
    else:
        arc = angdiff(sun_p, natal["bodies"]["sun"]["lon"]) % 360 if method == "solar_arc" else NAIBOD_DEG_PER_YEAR * years
        mc = (natal["angles"]["mc"]["lon"] + arc) % 360
        # ARMC whose MC is that longitude: right ascension of the ecliptic point mc
        import math
        armc = math.degrees(math.atan2(math.sin(math.radians(mc)) * math.cos(math.radians(eps)), math.cos(math.radians(mc)))) % 360
    asc = H.ascendant(armc, eps, lat)
    return {"mc": _p(mc), "asc": _p(asc), "armc": armc, "method": method}


def chart(natal: dict, when: dt.datetime, angle_method: str = "solar_arc") -> dict:
    jd_p, years = progressed_jd(natal, when)
    t = E.time_jd_ut(jd_p)
    bodies = {}
    for n in PROGRESSED:
        p = E.positions(n, t)
        bodies[n] = {**_p(p.lon), "speed": round(p.speed, 6), "retrograde": p.speed < 0}
    out = {"when": when.astimezone(UTC).isoformat(), "age_years": round(years, 4),
           "progressed_date_utc": (dt.datetime(2000, 1, 1, 12, tzinfo=UTC) + dt.timedelta(days=jd_p - 2451545.0)).isoformat(),
           "bodies": bodies, "angles": _angles(natal, jd_p, years, angle_method, bodies["sun"]["lon"])}
    if "houses" in natal:
        cs = [c["lon"] for c in natal["houses"]["cusps"][natal["houses"]["system"]]]
        for b in bodies.values():
            b["natal_house"] = H.house_of(b["lon"], cs)
    out["moon_phase"] = round((bodies["moon"]["lon"] - bodies["sun"]["lon"]) % 360, 3)
    return out


def _real_date(natal: dict, jd_p: float) -> str:
    years = jd_p - natal["time"]["jd_ut"]
    jd_real = natal["time"]["jd_ut"] + years * TROPICAL_YEAR
    return (dt.datetime(2000, 1, 1, 12, tzinfo=UTC) + dt.timedelta(days=jd_real - 2451545.0)).replace(microsecond=0).isoformat()


def timeline(natal: dict, from_age: float, to_age: float, orb: float = 1.0,
             bodies=PROGRESSED, aspects=("conjunction", "opposition", "trine", "square", "sextile")) -> dict:
    """Exact progressed aspects to natal points, sign and natal-house ingresses of progressed bodies, between two ages.
    Times are real-life dates (the progressed instant mapped back through the day-for-a-year key)."""
    jd_b = natal["time"]["jd_ut"]
    j0, j1 = jd_b + from_age, jd_b + to_age
    defs = {d["id"]: d["angle"] for d in kb.aspects()["aspects"]}
    targets = {**{k: v["lon"] for k, v in natal["bodies"].items()}, "north_node": natal["points"]["north_node"]["lon"]}
    if "angles" in natal:
        targets.update(asc=natal["angles"]["asc"]["lon"], mc=natal["angles"]["mc"]["lon"])
    events = []
    cusps = [c["lon"] for c in natal["houses"]["cusps"][natal["houses"]["system"]]] if "houses" in natal else None

    from .transits import Track, _root
    tracks = {}

    def root(body, target, a, b):
        tr = tracks[body]
        g = lambda x: angdiff(tr.at(x) % 360.0, target)
        return _root(g, a, b, g(a))

    for body in bodies:
        tracks[body] = Track(body, j0, j1, 0.05)
        sel = (tracks[body].grid >= j0) & (tracks[body].grid <= j1 + 0.05)
        grid = tracks[body].grid[sel]
        lon = tracks[body].lon[sel]
        for tname, L in targets.items():
            if tname == body:
                continue
            for asp in aspects:
                for target in sorted({round((L + defs[asp]) % 360, 9) % 360, round((L - defs[asp]) % 360, 9) % 360}):
                    g = (lon - target + 180) % 360 - 180
                    for k in np.nonzero((np.sign(g[:-1]) != np.sign(g[1:])) & (np.abs(g[:-1]) < 20))[0]:
                        x = root(body, target, grid[k], grid[k + 1])
                        spd = abs(tracks[body].speed(x))                             # degrees per progressed day = per year of life
                        events.append({"type": "aspect", "progressed": body, "natal": tname, "aspect": asp, "date": _real_date(natal, x),
                                       "age": round(float(x - jd_b), 3), "years_in_orb": round(float(2 * orb / spd), 2) if spd > 1e-4 else None,
                                       "retrograde": bool(tracks[body].speed(x) < 0)})
        sign = (lon // 30).astype(int)
        for k in np.nonzero(sign[:-1] != sign[1:])[0]:
            fwd = ((lon[k + 1] - lon[k] + 180) % 360 - 180) > 0
            edge = float((sign[k + 1] if fwd else sign[k]) * 30 % 360)
            x = root(body, edge, grid[k], grid[k + 1])
            events.append({"type": "ingress", "progressed": body, "sign": SIGNS[int(sign[k + 1])], "date": _real_date(natal, x),
                           "age": round(float(x - jd_b), 3), "retrograde": not fwd})
        if cusps:
            hs = np.array([H.house_of(float(v), cusps) for v in lon])
            for k in np.nonzero(hs[:-1] != hs[1:])[0]:
                fwd = ((lon[k + 1] - lon[k] + 180) % 360 - 180) > 0
                edge = cusps[(int(hs[k + 1]) - 1) if fwd else (int(hs[k]) - 1)]
                x = root(body, edge, grid[k], grid[k + 1])
                events.append({"type": "house", "progressed": body, "house": int(hs[k + 1]), "date": _real_date(natal, x),
                               "age": round(float(x - jd_b), 3), "retrograde": not fwd, "system": natal["houses"]["system"]})
        if body not in ("sun", "moon"):            # stations: the progressed planet turns retrograde or direct
            un = tracks[body].un[sel]
            d = np.diff(un)
            for k in np.nonzero(np.sign(d[:-1]) != np.sign(d[1:]))[0]:
                fa = tracks[body].speed(grid[k])
                x = _root(tracks[body].speed, grid[k], grid[k + 2], fa)
                events.append({"type": "station", "progressed": body, "turns": "retrograde" if fa > 0 else "direct",
                               "lon": round(float(tracks[body].at(x)) % 360.0, 4), "date": _real_date(natal, x),
                               "age": round(float(x - jd_b), 3)})
    events.sort(key=lambda e: e["age"])
    return {"orb": orb, "from_age": from_age, "to_age": to_age, "events": events,
            "key": "1 ngày sau khi sinh = 1 năm cuộc đời (năm chí tuyến 365,24219 ngày)"}
