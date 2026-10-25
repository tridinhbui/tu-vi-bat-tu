"""The horary chart: the sky for the moment and place the question was received.

Input is the civil time and place of the question; output is facts only (positions, houses, motion, day/night, planetary
hour) with a trace. A stored chart keeps its input, the engine version and the ephemeris used, and `fingerprint()` hashes
the computed facts, so reopening a saved question recomputes the same chart or says that it changed.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
from dataclasses import dataclass, field, asdict

from tvbt.trace import Trace
from western import timeutil
from western import houses as WH
from western.zodiac import SIGNS, sign_index, deg_in_sign

from . import astro, events, houses as H

ENGINE_VERSION = "horary-0.1.0"
WEEKDAY_RULER = ("moon", "mars", "mercury", "jupiter", "venus", "saturn", "sun")      # Python weekday(): Monday = 0
CHALDEAN = ("saturn", "jupiter", "mars", "sun", "venus", "mercury", "moon")


@dataclass
class HoraryInput:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    tz: str
    lat: float
    lon: float
    second: int = 0
    fold: int = 0
    place: str = ""
    utc_offset_hours: float | None = None      # when the user gives the offset instead of a zone
    house_system: str = "regiomontanus"
    node: str = "mean"                         # mean | true
    fortune: str = "lilly"                     # lilly: Asc + Moon - Sun by day and night | sect: reversed by night
    near_cusp_deg: float = 0.0                 # Lilly's "within N degrees of the next cusp counts in it"; set by the school
    julian_calendar: bool = False              # Old Style date (Lilly's examples); civil time is then local mean time


@dataclass
class Body:
    id: str
    lon: float
    lat: float
    speed: float
    ra: float
    dec: float
    sign: str
    deg: float
    house: int
    house_by_cusp_rule: bool
    retrograde: bool
    altitude: float
    traditional: bool


@dataclass
class HoraryChart:
    input: dict
    utc: str
    jd_ut: float
    ephemeris: dict
    armc: float
    obliquity: float
    asc: float
    mc: float
    cusps: list[float]
    bodies: dict[str, Body]
    nodes: dict
    fortune: float
    is_day: bool
    planetary_hour: dict
    engine: str = ENGINE_VERSION
    trace: Trace = field(default_factory=Trace)

    def body(self, p: str) -> Body:
        return self.bodies[p]

    def as_dict(self) -> dict:
        d = asdict(self)
        d["trace"] = [asdict(s) for s in self.trace.steps]
        return d


def _altitude(ra: float, dec: float, lst: float, lat: float) -> float:
    ha = math.radians((lst - ra) % 360.0)
    d, f = math.radians(dec), math.radians(lat)
    return math.degrees(math.asin(math.sin(f) * math.sin(d) + math.cos(f) * math.cos(d) * math.cos(ha)))


def _resolve(inp: HoraryInput, tr: Trace) -> tuple[float, str]:
    if inp.julian_calendar:
        # Old Style date, local mean time of the place (Lilly's practice): UT = LMT - longitude/15
        frac = (inp.hour + inp.minute / 60 + inp.second / 3600) / 24 - inp.lon / 360.0
        jd = astro.julian_calendar_to_jd(inp.year, inp.month, inp.day) + frac
        tr.add("time.julian", "Old Style date and local mean time to UT", {"date": [inp.year, inp.month, inp.day],
               "lmt": f"{inp.hour:02d}:{inp.minute:02d}", "lon": inp.lon}, {"jd_ut": jd}, rule="julian calendar; LMT = UT + lon/15 h")
        return jd, f"JD {jd:.5f} (Old Style input)"
    rt = timeutil.resolve(inp.year, inp.month, inp.day, inp.hour, inp.minute, inp.tz, inp.lon, second=inp.second,
                          fold=inp.fold, utc_offset_hours=inp.utc_offset_hours)
    tr.steps.extend(rt.trace.steps)
    u = rt.utc
    jd = astro.gregorian_to_jd(u.year, u.month, u.day + (u.hour + u.minute / 60 + (u.second + u.microsecond / 1e6) / 3600) / 24)
    return jd, u.isoformat()


def planetary_hour(jd: float, lat: float, lon: float) -> dict:
    """Planetary day and hour (unequal hours): the day runs from sunrise, the daylight and the night are each split into 12
    equal parts, the first hour of the day belongs to the day's ruler and the rest follow the Chaldean order."""
    ev = astro.sun_events(jd - 1.2, jd + 1.2, lat, lon)
    rises = [j for j, up in ev if up]
    sets = [j for j, up in ev if not up]
    rise = max((r for r in rises if r <= jd), default=None)
    if rise is None:
        return {"available": False, "reason": "Không có Mặt Trời mọc/lặn quanh thời điểm này (vùng cực): không tính được giờ hành tinh."}
    sset = min((s for s in sets if s > rise), default=None)
    nrise = min((r for r in rises if r > rise), default=None)
    if sset is None or nrise is None:
        return {"available": False, "reason": "Không đủ thời điểm mọc/lặn để chia giờ hành tinh."}
    local = dt.datetime(2000, 1, 1) + dt.timedelta(days=rise + lon / 360.0 - astro.gregorian_to_jd(2000, 1, 1))
    day_ruler = WEEKDAY_RULER[local.weekday()]
    if jd < sset:
        length, k0, start = (sset - rise) / 12, 0, rise
    else:
        length, k0, start = (nrise - sset) / 12, 12, sset
    k = min(11, int((jd - start) // length)) + k0
    ruler = CHALDEAN[(CHALDEAN.index(day_ruler) + k) % 7]
    return {"available": True, "day_ruler": day_ruler, "hour_ruler": ruler, "hour_number": k + 1, "is_day_hour": k < 12,
            "sunrise_jd": rise, "sunset_jd": sset, "next_sunrise_jd": nrise, "hour_length_min": round(length * 1440, 2),
            "hour_start_jd": start + (k - k0) * length, "hour_end_jd": start + (k - k0 + 1) * length,
            "sunrise_rule": "upper limb, refraction 34′ (horizon −0°50′)"}


def compute(inp: HoraryInput) -> HoraryChart:
    tr = Trace()
    jd, utc = _resolve(inp, tr)
    src = astro.source(jd)
    gast, eps, _dpsi = astro.sidereal_obliquity(jd)
    armc = (gast + inp.lon) % 360.0
    cusps = H.cusps(inp.house_system, armc, eps, inp.lat)
    asc, mc = cusps[0], WH.midheaven(armc, eps)
    tr.add("angles", "ARMC from GAST + east longitude; cusps by the house system", {"gast": gast, "lon": inp.lon, "lat": inp.lat,
           "eps": eps, "system": inp.house_system}, {"armc": armc, "asc": asc, "mc": mc, "cusps": cusps}, rule="spherical astronomy")
    pos = astro.positions(jd)
    bodies = {}
    for p, x in pos.items():
        h, moved = H.house_of(x.lon, cusps, inp.near_cusp_deg)
        bodies[p] = Body(p, x.lon, x.lat, x.speed, x.ra, x.dec, SIGNS[sign_index(x.lon)], deg_in_sign(x.lon), h, moved,
                         x.speed < 0, _altitude(x.ra, x.dec, armc, inp.lat), p in astro.TRAD)
    nd = astro.nodes(jd)
    node_lon = nd["true"] if inp.node == "true" and nd["true"] is not None else nd["mean"]
    sun, moon = pos["sun"].lon, pos["moon"].lon
    is_day = bodies["sun"].altitude > 0
    if inp.fortune == "sect" and not is_day:
        fortune = (asc + sun - moon) % 360.0
    else:
        fortune = (asc + moon - sun) % 360.0
    tr.add("sect", "Day chart when the Sun's centre is above the horizon (geometric altitude)", {"sun_alt": bodies["sun"].altitude}, is_day)
    tr.add("fortune", "Part of Fortune", {"rule": inp.fortune, "asc": asc, "sun": sun, "moon": moon, "day": is_day}, fortune)
    ph = planetary_hour(jd, inp.lat, inp.lon)
    tr.add("planetary_hour", "Planetary day and hour from local sunrise/sunset", {"lat": inp.lat, "lon": inp.lon}, ph)
    return HoraryChart(asdict(inp), utc, jd, src, armc, eps, asc, mc, cusps, bodies,
                       {"mean": nd["mean"], "true": nd["true"], "used": inp.node if node_lon is not None else "mean",
                        "north": node_lon, "south": (node_lon + 180.0) % 360.0},
                       fortune, is_day, ph, trace=tr)


def fingerprint(chart: HoraryChart) -> str:
    """Hash of the computed facts (rounded to 1e-6 degree), for 'the saved chart is unchanged' checks."""
    core = {"engine": chart.engine, "jd": round(chart.jd_ut, 9), "asc": round(chart.asc, 6), "mc": round(chart.mc, 6),
            "cusps": [round(c, 6) for c in chart.cusps],
            "bodies": {k: [round(b.lon, 6), round(b.speed, 6), b.house] for k, b in sorted(chart.bodies.items())}}
    return hashlib.sha256(json.dumps(core, sort_keys=True).encode()).hexdigest()[:16]


def timeline(chart: HoraryChart, back: float = 45.0, fwd: float = 400.0) -> dict:
    return events.search(chart.jd_ut, back, fwd)
