"""Independent reference values for the horary tests, from the Swiss Ephemeris (pyswisseph, Moshier analytical mode, no data files).

    python tools/horary/make_swe_fixture.py      # writes engine/tests/fixtures/horary_swe_reference.json

pyswisseph is AGPL: it is used here only on a developer machine to produce the fixture; it is not a dependency of the engine and
is not in the Docker image. Moshier mode is accurate to about 1″ for the planets and a few ″ for the Moon (Swiss Ephemeris docs),
which is the tolerance the tests use.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import swisseph as swe

OUT = Path(__file__).resolve().parents[2] / "engine" / "tests" / "fixtures" / "horary_swe_reference.json"
IDS = {"sun": 0, "moon": 1, "mercury": 2, "venus": 3, "mars": 4, "jupiter": 5, "saturn": 6}


def main() -> None:
    rnd = random.Random(20261025)
    cases = []
    for _ in range(60):
        jd = 2433282.5 + rnd.random() * (2488069.5 - 2433282.5)          # 1950 .. 2100
        lat, lon = round(rnd.uniform(-60, 60), 4), round(rnd.uniform(-180, 180), 4)
        planets = {}
        for p, i in IDS.items():
            x, _ = swe.calc_ut(jd, i, swe.FLG_MOSEPH | swe.FLG_SPEED)
            planets[p] = {"lon": x[0], "lat": x[1], "speed": x[3]}
        houses = {}
        for name, code in (("regiomontanus", b"R"), ("alcabitius", b"B"), ("placidus", b"P")):
            c, am = swe.houses_ex(jd, lat, lon, code, swe.FLG_MOSEPH)
            houses[name] = list(c)
        _, am = swe.houses_ex(jd, lat, lon, b"R", swe.FLG_MOSEPH)
        cases.append({"jd_ut": jd, "lat": lat, "lon": lon, "planets": planets, "houses": houses, "armc": am[2], "asc": am[0], "mc": am[1]})
    armc_cases = []
    for _ in range(300):
        armc, lat, eps = rnd.uniform(0, 360), rnd.uniform(-66, 66), rnd.uniform(23.2, 23.6)
        row = {"armc": armc, "lat": lat, "eps": eps}
        for name, code in (("regiomontanus", b"R"), ("alcabitius", b"B")):
            row[name] = list(swe.houses_armc(armc, lat, eps, code)[0])
        armc_cases.append(row)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"generator": "tools/horary/make_swe_fixture.py", "swisseph": swe.version, "mode": "Moshier (FLG_MOSEPH)",
                               "cases": cases, "armc_cases": armc_cases}, indent=1))
    print(OUT, len(cases), len(armc_cases))


if __name__ == "__main__":
    main()
