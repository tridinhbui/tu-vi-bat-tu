"""Dev-only: event times from Swiss Ephemeris for the forecasting tests (solar returns, ingresses, stations, transit exacts).

Independent of the site's own search code: Swiss positions (pyswisseph, AGPL, never shipped) with a plain bisection here, or
Swiss' own swe.solcross_ut for the Sun. Same virtualenv as make_swe_reference.py:

    /tmp/swe/bin/python tools/west/make_swe_events.py /path/to/ephe    # -> engine/tests/fixtures/west_swe_events.json
"""
from __future__ import annotations

import json
import pathlib
import random
import sys

import swisseph as swe

OUT = pathlib.Path(__file__).resolve().parents[2] / "engine" / "tests" / "fixtures" / "west_swe_events.json"
FL = swe.FLG_SWIEPH | swe.FLG_SPEED
P = {"mercury": swe.MERCURY, "venus": swe.VENUS, "mars": swe.MARS, "jupiter": swe.JUPITER, "saturn": swe.SATURN}


def lon(jd, body):
    return swe.calc_ut(jd, body, FL)[0][0]


def speed(jd, body):
    return swe.calc_ut(jd, body, FL)[0][3]


def d(a, b):
    return (a - b + 180) % 360 - 180


def bisect(f, a, b):
    fa = f(a)
    for _ in range(60):
        m = (a + b) / 2
        fm = f(m)
        if (fa <= 0) == (fm <= 0):
            a, fa = m, fm
        else:
            b = m
    return (a + b) / 2


def main():
    swe.set_ephe_path(sys.argv[1] if len(sys.argv) > 1 else "")
    rnd = random.Random(7)
    out = {"generator": "pyswisseph " + swe.version, "solar_returns": [], "ingresses": [], "stations": [], "transits": []}
    for _ in range(40):
        jd_birth = swe.julday(1930, 1, 1, 0) + rnd.random() * 30000
        sun = lon(jd_birth, swe.SUN)
        y = swe.revjul(jd_birth)[0] + rnd.randint(1, 60)
        jd_ret = swe.solcross_ut(sun, swe.julday(y, 1, 1, 0), FL)
        out["solar_returns"].append({"jd_birth_ut": jd_birth, "sun": sun, "year": y, "jd_return_ut": jd_ret})
    for name, code in P.items():                                   # 2026-2027: every sign ingress and station
        jd, end = swe.julday(2026, 1, 1, 0), swe.julday(2028, 1, 1, 0)
        step = 0.25
        while jd < end:
            a, b = lon(jd, code), lon(jd + step, code)
            if int(a // 30) != int(b // 30):
                edge = (int(b // 30) * 30) % 360 if d(b, a) > 0 else (int(a // 30) * 30) % 360
                out["ingresses"].append({"body": name, "jd_ut": bisect(lambda x: d(lon(x, code), edge), jd, jd + step), "sign_index": int(b // 30)})
            if speed(jd, code) * speed(jd + step, code) < 0:
                out["stations"].append({"body": name, "jd_ut": bisect(lambda x: speed(x, code), jd, jd + step),
                                        "turns": "retrograde" if speed(jd, code) > 0 else "direct"})
            jd += step
    for _ in range(20):                                             # Saturn and Jupiter conjunct a random natal degree
        target = rnd.uniform(0, 360)
        for name in ("jupiter", "saturn"):
            code = P[name]
            jd, end = swe.julday(2026, 1, 1, 0), swe.julday(2030, 1, 1, 0)
            hits = []
            while jd < end:
                if (d(lon(jd, code), target) <= 0) != (d(lon(jd + 1, code), target) <= 0) and abs(d(lon(jd, code), target)) < 5:
                    hits.append(bisect(lambda x: d(lon(x, code), target), jd, jd + 1))
                jd += 1
            out["transits"].append({"body": name, "target": target, "exact_jd_ut": hits})
    OUT.write_text(json.dumps(out, indent=0))
    print({k: len(v) for k, v in out.items() if isinstance(v, list)}, "->", OUT)


if __name__ == "__main__":
    main()
