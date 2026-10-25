"""Natal chart assembly: positions, angles, houses, points, conditions, aspects, rulership structure.

Every value here is either computed astronomy (positions, angles, cusps) or a mechanical table look-up whose table is cited
in kb/ (dignities, rulers, sect). Readings are produced elsewhere (western/reading/), from this output only.
"""
from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass

import numpy as np

from . import aspects as asp
from . import dignity, ephemeris as E, houses as H, kb
from .timeutil import resolve
from .zodiac import ELEMENT, MODALITY, SIGNS, angdiff, deg_in_sign, fmt_in_sign, sign_index

PLANETS10 = E.PLANETS
CLASSICAL = dignity.CLASSICAL
# Astronomical mean motions (deg/day), used only to say whether a planet moves faster or slower than its own average.
MEAN_MOTION = {"sun": 0.9856, "moon": 13.1764, "mercury": 0.9856, "venus": 0.9856, "mars": 0.5240, "jupiter": 0.0831,
               "saturn": 0.0335, "uranus": 0.0117, "neptune": 0.0060, "pluto": 0.0040, "chiron": 0.0196}


@dataclass
class ChartOptions:
    house_system: str = "placidus"
    node: str = "true"                     # "true" (osculating) or "mean"
    orbs: str = "thienban"
    minor_aspects: bool = True
    triplicity: str = "dorothean"
    terms: str = "egyptian"
    rulers: str = "traditional"            # "traditional" (7 planets) or "modern" (Uranus/Neptune/Pluto co-rule)
    lot_rule: str = "ptolemy"              # Fortune: "ptolemy" same formula day and night (Tetrabiblos III.10); "valens" reversed
                                           # by night only while the Moon is above the horizon (Valens III.14); "sect" reversed by night
    solar_phase: str = "traditional"       # combust / cazimi / beams limits (Lilly)

    @classmethod
    def from_dict(cls, d: dict | None) -> "ChartOptions":
        d = d or {}
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class BirthData:
    year: int
    month: int
    day: int
    hour: int | None                        # None = time unknown
    minute: int | None
    lat: float
    lon: float
    tz: str
    place: str = ""
    name: str = ""
    second: int = 0
    fold: int = 0
    utc_offset_hours: float | None = None

    @classmethod
    def from_dict(cls, d: dict) -> "BirthData":
        return cls(**{k: d[k] for k in cls.__dataclass_fields__ if k in d})


def _point(lon: float, speed: float | None = None, **extra) -> dict:
    out = {"lon": round(lon % 360.0, 6), "sign": SIGNS[sign_index(lon)], "deg": round(deg_in_sign(lon), 6),
           "fmt": fmt_in_sign(lon)}
    if speed is not None:
        out["speed"] = round(speed, 6)
    out.update(extra)
    return out


def _station_days(name: str, jd_ut: float) -> float | None:
    """Signed days to the nearest station (speed = 0) within +-30 days, or None. One vectorised ephemeris call on a half-day
    grid, roots found on the interpolated track (western.transits.Track)."""
    if name in ("sun", "moon"):
        return None
    from .transits import Track, _root
    try:
        tr = Track(name, jd_ut - 30.0, jd_ut + 30.0, 0.5)
    except E.OutOfRange:
        return None
    d = np.diff(tr.un)
    best = None
    for k in np.nonzero(np.sign(d[:-1]) != np.sign(d[1:]))[0]:
        a, b = float(tr.grid[k]), float(tr.grid[k + 2])
        root = _root(tr.speed, a, b, tr.speed(a)) - jd_ut
        if abs(root) <= 30.0 and (best is None or abs(root) < abs(best)):
            best = root
    return None if best is None else round(float(best), 3)


def compute(birth: BirthData, opts: ChartOptions | None = None) -> dict:
    opts = opts or ChartOptions()
    time_known = birth.hour is not None
    h, m = (birth.hour, birth.minute or 0) if time_known else (12, 0)
    rt = resolve(birth.year, birth.month, birth.day, h, m, birth.tz, birth.lon, birth.second, birth.fold, birth.utc_offset_hours)
    t = E.time_utc(rt.utc)
    jd_ut, jd_tt = float(t.ut1), float(t.tt)
    gast, eps, dpsi = E.sidereal_and_obliquity(t)

    bodies: dict[str, dict] = {}
    for name in E.BODIES:
        p = E.positions(name, t)
        bodies[name] = _point(p.lon, p.speed, lat=round(p.lat, 6), dec=round(p.dec, 6), ra=round(p.ra, 6),
                              dist_au=round(p.dist_au, 8), retrograde=p.speed < 0)
    node_fn = E.moon_osculating_node if opts.node == "true" else E.moon_mean_node
    node_lon = node_fn(t)
    node_speed = angdiff(node_fn(E.timescale().tt_jd(jd_tt + 0.5)), node_lon) / 0.5
    points = {"north_node": _point(node_lon, node_speed, kind=opts.node),
              "south_node": _point(node_lon + 180.0, node_speed, kind=opts.node)}

    out = {"input": {**birth.__dict__, "time_known": time_known}, "options": dict(opts.__dict__),
           "time": {"utc": rt.utc.isoformat(), "local": rt.local.isoformat(), "offset_hours": rt.offset_hours, "dst": rt.dst,
                    "lmt": rt.lmt, "ambiguous": rt.ambiguous, "jd_ut": jd_ut, "jd_tt": jd_tt,
                    "delta_t_s": round((jd_tt - jd_ut) * 86400, 3)},
           "astronomy": {"gast_deg": gast, "true_obliquity": eps, "nutation_lon": dpsi,
                         "ephemeris": "JPL DE440s (Skyfield); Chiron: JPL Horizons " + str(E.chiron_meta().get("solution"))},
           "bodies": bodies, "points": points, "trace": [s.__dict__ for s in rt.trace.steps], "warnings": []}

    is_day = None
    if not time_known:
        out["warnings"].append("no_time")
        out["moon_day_range"] = _moon_day_range(birth)
        out["sign_changes_today"] = _sign_changes_today(birth)
    else:
        armc = (gast + birth.lon) % 360.0
        asc, mc = H.ascendant(armc, eps, birth.lat), H.midheaven(armc, eps)
        out["angles"] = {"asc": _point(asc), "mc": _point(mc), "dsc": _point(asc + 180), "ic": _point(mc + 180), "armc": armc}
        cusp_sets = {}
        for s in H.SYSTEMS:
            try:
                cusp_sets[s] = H.cusps(s, armc, eps, birth.lat)
            except H.PolarHouses:
                cusp_sets[s] = None
        used = opts.house_system
        if cusp_sets.get(used) is None:
            out["warnings"].append("placidus_polar_fallback_porphyry")
            used = "porphyry"
        out["houses"] = {"system": used, "requested": opts.house_system,
                         "cusps": {s: ([_point(c) for c in cs] if cs else None) for s, cs in cusp_sets.items()}}
        allpts = {**bodies, **points}
        for pt in allpts.values():
            pt["house"] = H.house_of(pt["lon"], cusp_sets[used])
            pt["house_ws"] = H.house_of(pt["lon"], cusp_sets["whole_sign"])
        for k in ("asc", "mc", "dsc", "ic"):
            out["angles"][k]["house_ws"] = H.house_of(out["angles"][k]["lon"], cusp_sets["whole_sign"])
        out["sect"] = _sect(bodies, birth, t)
        is_day = out["sect"]["is_day"]
        out["lots"] = _lots(asc, bodies, is_day, opts.lot_rule, _altitude(bodies["moon"], birth, t), cusp_sets[used], cusp_sets["whole_sign"])
        out["house_rulers"] = _house_rulers(cusp_sets[used], cusp_sets["whole_sign"], allpts, opts)

    out["conditions"] = {n: _conditions(n, bodies, is_day, opts, jd_ut) for n in E.BODIES}
    asp_points = {n: {"lon": bodies[n]["lon"], "speed": bodies[n]["speed"]} for n in E.BODIES}
    asp_points["north_node"] = {"lon": points["north_node"]["lon"], "speed": node_speed}
    if time_known:
        asp_points["asc"] = {"lon": out["angles"]["asc"]["lon"], "speed": None}
        asp_points["mc"] = {"lon": out["angles"]["mc"]["lon"], "speed": None}
        asp_points["fortune"] = {"lon": out["lots"]["fortune"]["lon"], "speed": None}
    found = asp.find(asp_points, opts.orbs, opts.minor_aspects)
    if not time_known:   # the Moon moves ~13 degrees in a day: keep a Moon aspect only if its orb holds all day long
        found = [a for a in found if "moon" not in (a.a, a.b) or a.orb + 6.6 <= a.max_orb]
    out["aspects"] = [a.as_dict() for a in found]
    out["sign_aspects"] = asp.sign_aspects({n: asp_points[n] for n in CLASSICAL if time_known or n != "moon"})
    out["patterns"] = asp.patterns(found, asp_points)
    out["stelliums"] = _stelliums(bodies, time_known)
    out["dispositors"] = _dispositors(bodies, opts.rulers)
    out["receptions"] = _receptions(bodies)
    out["balance"] = _balance(bodies, time_known)
    out["moon_phase"] = _moon_phase(bodies)
    return out


def _altitude(b: dict, birth: BirthData, t) -> float:
    """Geometric altitude of a body's centre (degrees, no refraction)."""
    gast = E.sidereal_and_obliquity(t)[0]
    ha = math.radians((gast + birth.lon - b["ra"]) % 360.0)
    phi, dec = math.radians(birth.lat), math.radians(b["dec"])
    return math.degrees(math.asin(math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.cos(ha)))


def _sect(bodies: dict, birth: BirthData, t) -> dict:
    """Day chart when the Sun's centre is above the true horizon. Mercury's sect two ways: Ptolemy I.7 (morning star = diurnal)
    and Valens III.5 (the sect of the lord of the terms it occupies)."""
    alt = _altitude(bodies["sun"], birth, t)
    is_day = alt > 0
    merc_oriental = angdiff(bodies["sun"]["lon"], bodies["mercury"]["lon"]) > 0     # Mercury behind the Sun = rises first
    term_lord = dignity.term_lord(bodies["mercury"]["lon"], "egyptian")
    sect_of = {"sun": "diurnal", "jupiter": "diurnal", "saturn": "diurnal", "moon": "nocturnal", "venus": "nocturnal", "mars": "nocturnal"}
    return {"is_day": is_day, "sun_altitude": round(alt, 4), "borderline": abs(alt) < 1.0, "light": "sun" if is_day else "moon",
            "benefic_of_sect": "jupiter" if is_day else "venus", "malefic_of_sect": "saturn" if is_day else "mars",
            "benefic_contrary": "venus" if is_day else "jupiter", "malefic_contrary": "mars" if is_day else "saturn",
            "mercury_sect": "diurnal" if merc_oriental else "nocturnal",
            "mercury_sect_valens": sect_of.get(term_lord, "common"), }


def _lots(asc: float, bodies: dict, is_day: bool, rule: str, moon_alt: float, cusps_used: list, cusps_ws: list) -> dict:
    sun, moon = bodies["sun"]["lon"], bodies["moon"]["lon"]
    day_formula = is_day or rule == "ptolemy" or (rule == "valens" and moon_alt <= 0)
    fortune = asc + (moon - sun if day_formula else sun - moon)
    spirit = asc + (sun - moon if day_formula else moon - sun)
    mk = lambda x, f: _point(x, None, formula=f, house=H.house_of(x % 360, cusps_used), house_ws=H.house_of(x % 360, cusps_ws))
    return {"fortune": mk(fortune, "ASC + Moon - Sun" if day_formula else "ASC + Sun - Moon"),
            "spirit": mk(spirit, "ASC + Sun - Moon" if day_formula else "ASC + Moon - Sun"),
            "rule": rule, "moon_altitude": round(moon_alt, 4)}


def ruler(sign: str, scheme: str = "traditional") -> str:
    return dignity.modern_lord(sign) if scheme == "modern" else dignity.domicile_lord(sign)


def _house_rulers(cusps_used: list, cusps_ws: list, pts: dict, opts: ChartOptions) -> list[dict]:
    out = []
    for i in range(12):
        sign = SIGNS[sign_index(cusps_used[i])]
        r = ruler(sign, opts.rulers)
        ws_sign = SIGNS[sign_index(cusps_ws[i])]
        out.append({"house": i + 1, "cusp_sign": sign, "ruler": r, "traditional_ruler": dignity.domicile_lord(sign),
                    "modern_ruler": dignity.modern_lord(sign), "ruler_house": pts[r]["house"], "ruler_sign": pts[r]["sign"],
                    "ws_sign": ws_sign, "ws_ruler": dignity.domicile_lord(ws_sign)})
    return out


def _conditions(name: str, bodies: dict, is_day: bool | None, opts: ChartOptions, jd_ut: float) -> dict:
    b = bodies[name]
    c: dict = {"retrograde": b["retrograde"], "station_days": _station_days(name, jd_ut)}
    if MEAN_MOTION.get(name):
        c["speed_ratio"] = round(abs(b["speed"]) / MEAN_MOTION[name], 3)
    if name in CLASSICAL:
        c["essential"] = dignity.essential(name, b["lon"], is_day, opts.triplicity, opts.terms)
    if name != "sun":
        el = angdiff(b["lon"], bodies["sun"]["lon"])               # + = ahead of the Sun in the zodiac (sets after it)
        d = abs(el)
        lim = kb.dignities()["solar_phase"][opts.solar_phase]
        phase = None
        same_sign = b["sign"] == bodies["sun"]["sign"]
        if "cazimi_deg" in lim and d <= lim["cazimi_deg"]:
            phase = "cazimi"
        elif "combust_deg" in lim and d <= lim["combust_deg"] and (same_sign or not lim.get("combust_same_sign")):
            phase = "combust"
        elif d <= lim["beams_deg"]:
            phase = "under_beams"
        c["solar"] = {"elongation": round(el, 4), "distance": round(d, 4), "phase": phase, "oriental": el < 0,
                      "limits": opts.solar_phase}
    return c


def _stelliums(bodies: dict, time_known: bool) -> list[dict]:
    by_sign: dict[str, list] = {}
    by_house: dict[int, list] = {}
    for n in PLANETS10:
        by_sign.setdefault(bodies[n]["sign"], []).append(n)
        if time_known:
            by_house.setdefault(bodies[n]["house"], []).append(n)
    return ([{"by": "sign", "where": s, "bodies": v} for s, v in by_sign.items() if len(v) >= 3]
            + [{"by": "house", "where": h, "bodies": v} for h, v in by_house.items() if len(v) >= 3])


def _dispositors(bodies: dict, scheme: str) -> dict:
    """Chain of domicile rulers from each planet; final dispositor when every chain ends in one self-ruling planet."""
    pool = CLASSICAL if scheme == "traditional" else PLANETS10
    disp = {n: ruler(bodies[n]["sign"], scheme) for n in pool}
    chains = {}
    for n in pool:
        seen, cur = [n], n
        while disp[cur] not in seen:
            cur = disp[cur]
            seen.append(cur)
        chains[n] = seen
    self_ruled = [n for n in pool if disp[n] == n]
    ends = {ch[-1] for ch in chains.values()}
    final = self_ruled[0] if len(self_ruled) == 1 and ends == set(self_ruled) else None
    loops = []
    for n in pool:
        if disp[n] != n and disp.get(disp[n]) == n and sorted((n, disp[n])) not in loops:
            loops.append(sorted((n, disp[n])))
    return {"scheme": scheme, "dispositor": disp, "chains": chains, "final": final, "self_ruled": self_ruled, "mutual_loops": loops}


def _receptions(bodies: dict) -> list[dict]:
    """Mutual reception by domicile, by exaltation, or mixed, among the seven classical planets."""
    out = []
    for i, a in enumerate(CLASSICAL):
        for b in CLASSICAL[i + 1:]:
            sa, sb = bodies[a]["sign"], bodies[b]["sign"]
            dom = dignity.domicile_lord(sa) == b and dignity.domicile_lord(sb) == a
            exa = dignity.exaltation_lord(sa) == b and dignity.exaltation_lord(sb) == a
            mix = (dignity.domicile_lord(sa) == b and dignity.exaltation_lord(sb) == a) or \
                  (dignity.exaltation_lord(sa) == b and dignity.domicile_lord(sb) == a)
            for by, ok in (("domicile", dom), ("exaltation", exa), ("mixed", mix)):
                if ok:
                    out.append({"a": a, "b": b, "by": by})
    return out


def _balance(bodies: dict, time_known: bool) -> dict:
    """Plain counts of the ten planets by element, modality and hemisphere. No weights."""
    el = {k: [] for k in ("fire", "earth", "air", "water")}
    mo = {k: [] for k in ("cardinal", "fixed", "mutable")}
    for n in PLANETS10:
        i = sign_index(bodies[n]["lon"])
        el[ELEMENT[i]].append(n)
        mo[MODALITY[i]].append(n)
    out = {"element": el, "modality": mo}
    if time_known:
        above = [n for n in PLANETS10 if 7 <= bodies[n]["house"] <= 12]
        east = [n for n in PLANETS10 if bodies[n]["house"] in (10, 11, 12, 1, 2, 3)]
        out["hemisphere"] = {"above": above, "below": [n for n in PLANETS10 if n not in above],
                             "east": east, "west": [n for n in PLANETS10 if n not in east]}
    return out


def _moon_phase(bodies: dict) -> dict:
    el = (bodies["moon"]["lon"] - bodies["sun"]["lon"]) % 360.0
    names = ["new", "waxing_crescent", "first_quarter", "waxing_gibbous", "full", "waning_gibbous", "last_quarter", "waning_crescent"]
    return {"elongation": round(el, 4), "waxing": el < 180, "phase": names[int(((el + 22.5) % 360) // 45)],
            "illumination": round((1 - math.cos(math.radians(el))) / 2, 4)}


def _local_day_utc(birth: BirthData) -> tuple[dt.datetime, dt.datetime]:
    a = resolve(birth.year, birth.month, birth.day, 0, 0, birth.tz, birth.lon, 0, 0, birth.utc_offset_hours).utc
    b = resolve(birth.year, birth.month, birth.day, 23, 59, birth.tz, birth.lon, 59, 0, birth.utc_offset_hours).utc
    return a, b


def _moon_day_range(birth: BirthData) -> dict:
    a, b = _local_day_utc(birth)
    la, lb = E.positions("moon", E.time_utc(a)).lon, E.positions("moon", E.time_utc(b)).lon
    return {"start": _point(la), "end": _point(lb), "changes_sign": sign_index(la) != sign_index(lb)}


def _sign_changes_today(birth: BirthData) -> list[dict]:
    a, b = _local_day_utc(birth)
    out = []
    for n in E.BODIES:
        la, lb = E.positions(n, E.time_utc(a)).lon, E.positions(n, E.time_utc(b)).lon
        if sign_index(la) != sign_index(lb):
            out.append({"body": n, "from": SIGNS[sign_index(la)], "to": SIGNS[sign_index(lb)]})
    return out
