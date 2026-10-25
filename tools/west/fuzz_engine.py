"""Invariants of the Western engine over many charts (positions are checked against Swiss Ephemeris in engine/tests; this checks
that what is built on them hangs together).

  houses      every system's twelve cusps go round the zodiac once; house_of agrees with the cusps; Lilly's five-degree house
              differs from the Regiomontanus house only within five degrees of a cusp, and then is the next house
  dignity     Lilly's points do not depend on the chart's table options
  transits    a 120-day search: no two events share planet, aspect, point, side and span; exact hits lie inside their span;
              sign ingresses go in the direction of the planet's motion
  progress    progressed ingresses flagged retrograde happen while the planet moves backwards; stations alternate

    python tools/west/fuzz_engine.py [N]
"""
from __future__ import annotations

import collections
import datetime as dt
import random
import sys
import time

sys.path.insert(0, "engine")
from western import chart as C, houses as H, progressions as PR, transits as T  # noqa: E402
from western.zodiac import angdiff  # noqa: E402

UTC = dt.timezone.utc
CITIES = [(10.82, 106.63, "Asia/Ho_Chi_Minh"), (21.03, 105.85, "Asia/Hanoi"), (48.86, 2.35, "Europe/Paris"), (-33.87, 151.21, "Australia/Sydney"),
          (40.71, -74.01, "America/New_York"), (64.15, -21.94, "Atlantic/Reykjavik"), (-54.8, -68.3, "America/Argentina/Ushuaia"), (69.65, 18.96, "Europe/Oslo")]


def main(n: int):
    rnd = random.Random(2002)
    bad = collections.Counter()
    ex = {}
    t0 = time.time()

    def fail(kind, msg):
        bad[kind] += 1
        ex.setdefault(kind, msg)

    for i in range(n):
        lat, lon, tz = rnd.choice(CITIES)
        b = C.BirthData(rnd.randint(1901, 2099), rnd.randint(1, 12), rnd.randint(1, 28), rnd.randint(0, 23), rnd.randint(0, 59), lat, lon, tz)
        try:
            c = C.compute(b)
        except Exception as e:  # noqa: BLE001
            fail("compute", f"{b}: {e}")
            continue
        for sys_, cs in c["houses"]["cusps"].items():
            if not cs:
                continue
            lons = [x["lon"] for x in cs]
            if abs(sum((lons[(k + 1) % 12] - lons[k]) % 360 for k in range(12)) - 360) > 1e-6:
                fail("cusps_order", f"{b} {sys_}")
        used = [x["lon"] for x in c["houses"]["cusps"][c["houses"]["system"]]]
        regio = [x["lon"] for x in c["houses"]["cusps"]["regiomontanus"]] if c["houses"]["cusps"].get("regiomontanus") else None
        for name, p in c["bodies"].items():
            h = p["house"]
            a, z = used[h - 1], used[h % 12]
            if not ((p["lon"] - a) % 360 < (z - a) % 360 + 1e-9):
                fail("house_of", f"{b} {name}")
            if regio:
                hr, hl = H.house_of(p["lon"], regio), p["house_lilly"]
                if hl != hr:
                    nxt = regio[hr % 12]
                    if not (hl == hr % 12 + 1 and (nxt - p["lon"]) % 360 <= 5.0 + 1e-9):
                        fail("lilly_5deg", f"{b} {name} regio {hr} lilly {hl}")
        if i % 10 == 0:
            c2 = C.compute(b, C.ChartOptions(triplicity="ptolemaic", terms="lilly"))
            if any(c["conditions"][p]["lilly"] != c2["conditions"][p]["lilly"] for p in C.CLASSICAL):
                fail("lilly_points", str(b))
        if i % 4 == 0:
            a = dt.datetime(rnd.randint(1950, 2080), rnd.randint(1, 12), 1, tzinfo=UTC)
            ev = T.find(c, a, a + dt.timedelta(days=120), transiting=("sun", "mercury", "venus", "mars", "jupiter", "saturn"))
            keys = collections.Counter((e["transiting"], e["aspect"], e["natal"], e["side"], e["start"], e["end"]) for e in ev)
            if keys and max(keys.values()) > 1:
                fail("transit_dup", str(b))
            for e in ev:
                for x in e["exact"]:
                    if (e["start"] and x < e["start"]) or (e["end"] and x > e["end"]):
                        fail("exact_outside", f"{b} {e['transiting']} {e['aspect']} {e['natal']}")
            for s in T.ingresses_and_stations(a, a + dt.timedelta(days=120), bodies=("mercury", "venus", "mars")):
                if s["type"] == "ingress":
                    from western import ephemeris as E
                    t = E.time_utc(dt.datetime.fromisoformat(s["time"]))
                    sp = E.positions(s["body"], t).speed
                    if (sp < 0) != s["retrograde"] and abs(sp) > 1e-3:
                        fail("ingress_direction", f"{s}")
        if i % 8 == 0:
            tl = PR.timeline(c, 0, 60, bodies=("mercury", "venus", "mars"))
            for body in ("mercury", "venus", "mars"):
                st = [e["turns"] for e in tl["events"] if e["progressed"] == body and e["type"] == "station"]
                if any(st[k] == st[k + 1] for k in range(len(st) - 1)):
                    fail("stations_alternate", f"{b} {body} {st}")
            for e in tl["events"]:
                if e["type"] == "ingress" and e["progressed"] in ("mercury", "venus", "mars"):
                    from western import ephemeris as E
                    jd = c["time"]["jd_ut"] + e["age"]
                    sp = E.positions(e["progressed"], E.time_jd_ut(jd)).speed
                    if (sp < 0) != e["retrograde"] and abs(sp) > 1e-3:
                        fail("progressed_ingress_direction", f"{b} {e}")
    print(f"{n} charts, {time.time() - t0:.0f}s")
    print("violations:", dict(bad) or "none")
    for k, v in ex.items():
        print(f"  {k}: {v[:300]}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 200)
