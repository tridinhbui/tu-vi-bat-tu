"""Dev-only: independent reference values from Swiss Ephemeris (pyswisseph, AGPL-3.0) for the Western-astrology tests.

Swiss Ephemeris is NOT a dependency of the site (its licence is AGPL or a paid professional licence); it is used only here,
in a throw-away virtualenv, to produce numbers the tests compare against. Astro.com computes with Swiss Ephemeris, so this
is the closest offline stand-in for "what Astro.com shows". Run:

    python3 -m venv /tmp/swe && /tmp/swe/bin/pip install pyswisseph numpy
    # Swiss data files sepl_18.se1 semo_18.se1 seas_18.se1 from https://github.com/aloistr/swisseph/tree/master/ephe
    /tmp/swe/bin/python tools/west/make_swe_reference.py /path/to/ephe

writes engine/tests/fixtures/west_swe_reference.json.
"""
from __future__ import annotations

import json
import pathlib
import random
import sys

import swisseph as swe

OUT = pathlib.Path(__file__).resolve().parents[2] / "engine" / "tests" / "fixtures" / "west_swe_reference.json"
BODIES = {"sun": swe.SUN, "moon": swe.MOON, "mercury": swe.MERCURY, "venus": swe.VENUS, "mars": swe.MARS, "jupiter": swe.JUPITER,
          "saturn": swe.SATURN, "uranus": swe.URANUS, "neptune": swe.NEPTUNE, "pluto": swe.PLUTO, "chiron": swe.CHIRON,
          "mean_node": swe.MEAN_NODE, "true_node": swe.TRUE_NODE}
HSYS = {"placidus": b"P", "equal": b"A", "whole_sign": b"W", "porphyry": b"O", "koch": b"K", "regiomontanus": b"R"}


def case(jd_ut: float, lat: float, lon: float) -> dict:
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    out = {"jd_ut": jd_ut, "lat": lat, "lon": lon, "deltat_days": swe.deltat(jd_ut), "bodies": {}, "houses": {}}
    jd_tt = jd_ut + out["deltat_days"]
    for name, code in BODIES.items():
        xx, ret = swe.calc(jd_tt, code, flags)            # TT input isolates the ephemeris from the delta-T model
        out["bodies"][name] = {"lon": xx[0], "lat": xx[1], "dist": xx[2], "speed": xx[3]}
    nut = swe.calc(jd_tt, swe.ECL_NUT, 0)[0]
    out["true_obliquity"], out["nutation_lon"] = nut[0], nut[2]
    for name, code in HSYS.items():
        try:
            cusps, ascmc = swe.houses(jd_ut, lat, lon, code)
        except swe.Error as e:
            out["houses"][name] = {"error": str(e)}
            continue
        out["houses"][name] = {"cusps": list(cusps), "asc": ascmc[0], "mc": ascmc[1], "armc": ascmc[2], "vertex": ascmc[3]}
    out["sidtime_hours"] = swe.sidtime(jd_ut)
    return out


def main():
    swe.set_ephe_path(sys.argv[1] if len(sys.argv) > 1 else "")
    rnd = random.Random(20261025)
    cases = []
    for _ in range(240):                                   # random instants 1900-2100, latitudes inside the polar circles
        jd = swe.julday(1900, 1, 1, 0) + rnd.random() * 73049
        cases.append(case(jd, round(rnd.uniform(-66, 66), 4), round(rnd.uniform(-180, 180), 4)))
    for lat in (-60, -45, -10.5, 0.0, 10.82, 21.03, 51.48, 64.0, 70.0):   # fixed latitudes incl. one beyond the polar circle
        cases.append(case(swe.julday(1990, 5, 17, 3.5), lat, 106.66))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"generator": "pyswisseph " + swe.version, "cases": cases}, indent=0))
    print(len(cases), "cases ->", OUT)


if __name__ == "__main__":
    main()
