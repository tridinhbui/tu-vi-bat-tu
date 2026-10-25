"""Fetch 2060 Chiron heliocentric state vectors from JPL Horizons and store them for engine/western/ephemeris.py.

The JPL DE ephemerides hold only the Sun, Moon and planets, so Chiron comes from Horizons' own numerical integration
(small-body solution "JPL#171", Sun from DE441). Vectors: ICRF, centre = Sun body centre (500@10), TDB, au and au/day,
every 4 days from 1899-01-01 to 2101-01-01. engine/western/ephemeris.py interpolates them with cubic Hermite splines.

    python tools/west/build_chiron.py        # writes engine/data/western/chiron_1899_2101.npz
"""
from __future__ import annotations

import json
import pathlib
import re
import urllib.parse
import urllib.request

import numpy as np

OUT = pathlib.Path(__file__).resolve().parents[2] / "engine" / "data" / "western" / "chiron_1899_2101.npz"
API = "https://ssd.jpl.nasa.gov/api/horizons.api"
JD0, JD1, CHUNK = 2414655.5, 2488438.5, 4 * 4600     # 1899-01-01 .. 2101-01-05 TDB; chunks stay on one 4-day grid
SPANS = [(f"JD{a}", f"JD{min(a + CHUNK, JD1)}") for a in np.arange(JD0, JD1, CHUNK)]


def fetch(start: str, stop: str) -> tuple[str, np.ndarray]:
    q = {"format": "text", "COMMAND": "'2060;'", "OBJ_DATA": "NO", "MAKE_EPHEM": "YES", "EPHEM_TYPE": "'VECTORS'",
         "CENTER": "'500@10'", "START_TIME": f"'{start}'", "STOP_TIME": f"'{stop}'", "STEP_SIZE": "'4 d'",
         "REF_PLANE": "'FRAME'", "REF_SYSTEM": "'ICRF'", "VEC_TABLE": "'2'", "OUT_UNITS": "'AU-D'", "CSV_FORMAT": "'YES'"}
    with urllib.request.urlopen(API + "?" + urllib.parse.urlencode(q), timeout=120) as r:
        text = r.read().decode()
    body = text.split("$$SOE")[1].split("$$EOE")[0]
    rows = [[float(c) for i, c in enumerate(line.split(",")[:8]) if i != 1] for line in body.strip().splitlines()]
    return text, np.array(rows)


def main():
    parts, header = [], ""
    for a, b in SPANS:
        text, arr = fetch(a, b)
        header = header or text.split("$$SOE")[0]
        parts.append(arr)
    data = np.concatenate(parts)
    _, keep = np.unique(data[:, 0], return_index=True)       # span edges repeat one row
    data = data[keep]
    assert np.all(np.diff(data[:, 0]) == 4.0), "rows must be every 4 days"
    soln = re.search(r"\{source: (JPL#\d+)\}", header)
    meta = {"source": "JPL Horizons API (https://ssd.jpl.nasa.gov/api/horizons.api)", "target": "2060 Chiron",
            "solution": soln.group(1) if soln else None, "center": "Sun body centre (500@10)", "frame": "ICRF",
            "time_scale": "TDB", "units": "au, au/day", "step_days": 4}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, jd_tdb=data[:, 0], pos=data[:, 1:4], vel=data[:, 4:7], meta=json.dumps(meta))
    print(f"{len(data)} rows {data[0, 0]}..{data[-1, 0]} -> {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
