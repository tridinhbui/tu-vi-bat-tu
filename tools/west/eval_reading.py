"""Quality metrics of the Western reading over many charts (no language model involved).

  audit       issue counts from western.reading.audit over the corpus
  strip       share of sentences that are still identical across charts after chart words (planets, signs, numbers) are
              blanked: high = boilerplate that says nothing about the chart
  common      share of distinct paragraph texts that appear in >= 50% of the charts
  critical    birth time moved by 2 hours: share of natal paragraphs whose text changes (should be high)
  inert       longitude moved by 0.001 degree: share whose text changes (should be ~0)

    python tools/west/eval_reading.py [N]
"""
from __future__ import annotations

import collections
import datetime as dt
import random
import re
import statistics
import sys
import time

sys.path.insert(0, "engine")
from western.chart import BirthData, compute  # noqa: E402
from western.reading import build  # noqa: E402
from western.reading.audit import sentences  # noqa: E402
from western.reading.vocab import PLANET_VI, SIGN_VI  # noqa: E402

WHEN = dt.datetime(2026, 10, 25, tzinfo=dt.timezone.utc)
CITIES = [(10.8231, 106.6297, "Asia/Ho_Chi_Minh"), (21.0285, 105.8542, "Asia/Hanoi"), (48.8566, 2.3522, "Europe/Paris"),
          (40.7128, -74.006, "America/New_York"), (35.6762, 139.6503, "Asia/Tokyo"), (-33.8688, 151.2093, "Australia/Sydney"),
          (51.5072, -0.1276, "Europe/London"), (-23.5505, -46.6333, "America/Sao_Paulo"), (55.7558, 37.6173, "Europe/Moscow")]
WORDS = sorted(list(PLANET_VI.values()) + list(SIGN_VI.values()), key=len, reverse=True)


def strip(s: str) -> str:
    for w in WORDS:
        s = s.replace(w, "X")
    return re.sub(r"\d+([.,]\d+)?", "N", s)


def natal_texts(r: dict) -> dict:
    return {p["id"]: p["text"] for ch in r["chapters"] if ch["id"] != "thoi_van" for p in ch["paragraphs"]}


def main(n: int):
    rnd = random.Random(42)
    charts = []
    for _ in range(n):
        lat, lon, tz = rnd.choice(CITIES)
        y, m, d = rnd.randint(1930, 2015), rnd.randint(1, 12), rnd.randint(1, 28)
        h, mi = rnd.randint(0, 23), rnd.randint(0, 59)
        try:
            charts.append(BirthData(y, m, d, h, mi, lat, lon, tz))
        except Exception:
            pass
    t0 = time.time()
    audits = collections.Counter()
    sent_counter = collections.Counter()
    para_counter = collections.Counter()
    n_sent = 0
    crit, inert = [], []
    for i, b in enumerate(charts):
        try:
            c = compute(b)
        except Exception:
            continue
        r = build(c, "deep", rnd.choice([None, "male", "female"]), WHEN)
        audits.update(r["audit"]["counts"])
        texts = natal_texts(r)
        for t in set(texts.values()):
            para_counter[strip(t)] += 1
        seen = set()
        for t in texts.values():
            for s in sentences(t):
                n_sent += 1
                k = strip(s)
                if k not in seen:
                    sent_counter[k] += 1
                    seen.add(k)
        if i < 40:
            b2 = BirthData(b.year, b.month, b.day, (b.hour + 2) % 24, b.minute, b.lat, b.lon, b.tz)
            b3 = BirthData(b.year, b.month, b.day, b.hour, b.minute, b.lat, b.lon + 0.001, b.tz)
            for bb, acc in ((b2, crit), (b3, inert)):
                try:
                    t2 = natal_texts(build(compute(bb), "deep", r["gender"], WHEN))
                except Exception:
                    continue
                common = set(texts) & set(t2)
                acc.append(sum(texts[k] != t2[k] for k in common) / max(1, len(common)))
    N = len(charts)
    boiler = sum(v for v in sent_counter.values() if v >= N * 0.5)
    print(f"charts {N}, sentences {n_sent}, {time.time() - t0:.1f}s")
    print("audit issues:", dict(audits))
    print(f"strip: distinct stripped sentences in >=50% of charts: {sum(1 for v in sent_counter.values() if v >= N * 0.5)} "
          f"({boiler / max(1, sum(sent_counter.values())):.1%} of sentence occurrences)")
    print(f"common paragraphs (stripped, >=50% charts): {sum(1 for v in para_counter.values() if v >= N * 0.5)} of {len(para_counter)}")
    if crit:
        print(f"critical (2 h later): {statistics.mean(crit):.1%} of natal paragraphs change")
    if inert:
        print(f"inert (0.001 deg east): {statistics.mean(inert):.1%} change")
    print("most repeated stripped sentences:")
    for s, v in sent_counter.most_common(12):
        print(f"  {v:4d}  {s[:150]}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 60)
