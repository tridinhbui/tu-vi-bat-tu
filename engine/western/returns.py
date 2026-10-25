"""Solar returns and annual profections.

Solar return: the instant the Sun's apparent longitude comes back to its natal value (Lilly, Christian Astrology p.734:
"to the same degree and minute"), found by Newton steps on the ephemeris to under a second; the chart is cast for that
instant at a place the user picks (birthplace by default).

Annual profection: the Ascendant moves one sign (Hellenistic, whole-sign houses) or 30 degrees (Lilly pp.715-716, cusps keep
their natal degrees) for every completed year of life; the ruler of the sign reached is the lord of the year. The year runs
from one solar return to the next (Lilly p.715: the profectional year begins at the revolution).
"""
from __future__ import annotations

import datetime as dt

from tvbt.calendar_core import zone_of

from . import chart as C, dignity, ephemeris as E, houses as H
from .zodiac import SIGNS, angdiff, deg_in_sign, fmt_in_sign, sign_index

UTC = dt.timezone.utc


def _iso(jd_ut: float) -> str:
    return (dt.datetime(2000, 1, 1, 12, tzinfo=UTC) + dt.timedelta(days=jd_ut - 2451545.0)).replace(microsecond=0).isoformat()


def return_jd(natal_sun: float, approx_jd_ut: float) -> float:
    jd = approx_jd_ut
    for _ in range(12):
        p = E.positions("sun", E.time_jd_ut(jd))
        step = angdiff(natal_sun, p.lon) / p.speed
        jd += step
        if abs(step) < 1e-7:
            break
    return jd


def solar_return_jd(natal: dict, year: int) -> float:
    b = natal["input"]
    m, d = b["month"], min(b["day"], 28 if b["month"] == 2 else b["day"])
    approx = float(E.time_utc(dt.datetime(year, m, d, 12, tzinfo=UTC)).ut1)
    return return_jd(natal["bodies"]["sun"]["lon"], approx)


def chart_at_utc(utc: dt.datetime, lat: float, lon: float, tz: str, opts: C.ChartOptions | None = None, place: str = "") -> dict:
    local = utc.astimezone(zone_of(tz))
    fold = 1 if local.fold else 0
    b = C.BirthData(local.year, local.month, local.day, local.hour, local.minute, lat, lon, tz, place=place,
                    second=local.second, fold=fold)
    out = C.compute(b, opts)
    out["time"]["exact_utc"] = utc.isoformat()
    return out


def solar_return(natal: dict, year: int, lat: float | None = None, lon: float | None = None, tz: str | None = None,
                 place: str = "", opts: C.ChartOptions | None = None) -> dict:
    jd = solar_return_jd(natal, year)
    utc = dt.datetime(2000, 1, 1, 12, tzinfo=UTC) + dt.timedelta(days=jd - 2451545.0)
    nb = natal["input"]
    lat, lon, tz = (lat, lon, tz) if lat is not None else (nb["lat"], nb["lon"], nb["tz"])
    sr = chart_at_utc(utc, lat, lon, tz, opts, place or nb.get("place", ""))
    sun_err = abs(angdiff(sr["bodies"]["sun"]["lon"], natal["bodies"]["sun"]["lon"])) * 3600
    rel = {}
    if "houses" in natal and "angles" in sr:
        ncs = [c["lon"] for c in natal["houses"]["cusps"][natal["houses"]["system"]]]
        rel["sr_asc_in_natal_house"] = H.house_of(sr["angles"]["asc"]["lon"], ncs)
        rel["sr_planets_in_natal_houses"] = {n: H.house_of(b["lon"], ncs) for n, b in sr["bodies"].items()}
        rel["natal_asc_in_sr_house"] = sr["angles"]["asc"] and H.house_of(natal["angles"]["asc"]["lon"],
                                                                         [c["lon"] for c in sr["houses"]["cusps"][sr["houses"]["system"]]])
        hits = []
        for ang in ("asc", "mc", "dsc", "ic"):
            for n, b in natal["bodies"].items():
                orb = abs(angdiff(sr["angles"][ang]["lon"], b["lon"]))
                if orb <= 3.0:
                    hits.append({"sr_angle": ang, "natal": n, "orb": round(orb, 3)})
        rel["sr_angles_on_natal_planets"] = sorted(hits, key=lambda h: h["orb"])
    return {"year": year, "exact_utc": utc.replace(microsecond=0).isoformat(), "sun_error_arcsec": round(sun_err, 3),
            "place": {"lat": lat, "lon": lon, "tz": tz, "name": place or nb.get("place", "")}, "chart": sr, "relation": rel}


def profection(natal: dict, age: int, method: str = "whole_sign") -> dict:
    if "angles" not in natal:
        raise ValueError("profection cần giờ sinh (cần cung Mọc)")
    asc = natal["angles"]["asc"]["lon"]
    if method == "whole_sign":
        sign_i = (sign_index(asc) + age) % 12
        lon = sign_i * 30.0 + deg_in_sign(asc)
    else:                                                        # Lilly: the Ascendant's own degree advances 30 per year
        lon = (asc + 30.0 * age) % 360
        sign_i = sign_index(lon)
    sign = SIGNS[sign_i]
    lord = dignity.domicile_lord(sign)
    house_ws = (sign_i - sign_index(asc)) % 12 + 1
    occupants = [n for n, b in natal["bodies"].items() if b["sign"] == sign]
    lb = natal["bodies"][lord]
    nb = natal["input"]
    start = solar_return_jd(natal, nb["year"] + age)
    end = solar_return_jd(natal, nb["year"] + age + 1)
    return {"age": age, "method": method, "sign": sign, "lon": round(lon, 4), "fmt": fmt_in_sign(lon), "house": house_ws,
            "lord": lord, "lord_natal": {"sign": lb["sign"], "house": lb.get("house"), "house_ws": lb.get("house_ws"),
                                         "retrograde": lb["retrograde"],
                                         "essential": natal["conditions"][lord].get("essential", {}).get("has"),
                                         "debilities": natal["conditions"][lord].get("essential", {}).get("debilities"),
                                         "solar": natal["conditions"][lord].get("solar", {}).get("phase")},
            "natal_planets_in_sign": occupants, "start_utc": _iso(start), "end_utc": _iso(end)}


def profection_cycle(natal: dict, upto: int = 96, method: str = "whole_sign") -> list[dict]:
    """The profected sign and lord for every age 0..upto (no dates; the 12-year cycle at a glance)."""
    asc = natal["angles"]["asc"]["lon"]
    out = []
    for age in range(upto + 1):
        si = (sign_index(asc) + age) % 12 if method == "whole_sign" else sign_index((asc + 30.0 * age) % 360)
        out.append({"age": age, "sign": SIGNS[si], "house": (si - sign_index(asc)) % 12 + 1, "lord": dignity.domicile_lord(SIGNS[si])})
    return out


def age_at(natal: dict, when: dt.datetime) -> int:
    """Completed years at `when`, counted from solar return to solar return."""
    y = when.year
    jd_when = float(E.time_utc(when).ut1)
    sr = solar_return_jd(natal, y)
    return (y - natal["input"]["year"]) - (1 if jd_when < sr else 0)
