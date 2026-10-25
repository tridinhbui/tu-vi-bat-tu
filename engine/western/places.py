"""Birthplace search over the GeoNames gazetteer (engine/data/western/places.json.gz, built by tools/west/build_places.py)."""
from __future__ import annotations

import gzip
import json
import re
import unicodedata
from functools import lru_cache

from .ephemeris import DATA


def fold(s: str) -> str:
    """Lower-case, no diacritics (đ -> d), single spaces: 'Thành phố Hồ Chí Minh' -> 'thanh pho ho chi minh'."""
    s = s.replace("đ", "d").replace("Đ", "D").replace("ð", "d").replace("Ð", "D")   # Ð (Eth) appears in GeoNames
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return " ".join(s.lower().replace(",", " ").replace("-", " ").split())


@lru_cache(maxsize=1)
def _table():
    """Rows kept compact (one '|key|key|' string and a tuple each): the container has 256 MiB for the whole site."""
    raw = json.loads(gzip.decompress((DATA / "places.json.gz").read_bytes()))
    rows = []
    for name, ascii_, alts, country, admin1, lat, lon, tz, pop in raw["rows"]:
        keys = "|" + "|".join(sorted({fold(name), fold(ascii_), *(fold(a) for a in alts)})) + "|"
        rows.append((keys, (_display(name, alts, country), name, admin1, country, lat, lon, tz, pop)))
    return raw["source"], rows


_FIELDS = ("name", "geonames_name", "admin1", "country", "lat", "lon", "tz", "population")


# letters only Vietnamese uses among Latin scripts (so "Hanoí" in Spanish spelling is not taken for "Hà Nội")
_VI_ONLY = re.compile("[ăâđêôơưạảẹẻẽịỉọỏụủỳỷỹỵấầẩẫậắằẳẵặếềểễệốồổỗộớờởỡợứừửữựÐ]", re.I)


def _display(name: str, alts: list[str], country: str) -> str:
    """Vietnamese spelling of a Vietnamese place when GeoNames lists it ('Da Nang' -> 'Đà Nẵng')."""
    if country != "Việt Nam":
        return name
    if name == "Ho Chi Minh City":
        return "TP Hồ Chí Minh"
    if _VI_ONLY.search(name):
        return name
    squash = lambda s: fold(s).replace(" ", "")
    return next((a for a in alts if _VI_ONLY.search(a) and squash(a) == squash(name)), name)


def search(q: str, limit: int = 10) -> list[dict]:
    q = fold(q)
    if len(q) < 2:
        return []
    words = q.split()
    head, rest = words[0], words[1:]
    scored = []
    for keys, row in _table()[1]:
        if f"|{q}|" in keys:
            best = 0
        elif f"|{q}" in keys:
            best = 1
        elif f" {q}" in keys:
            best = 2
        elif rest and f"|{head}" in keys and all(w in fold(row[2] + " " + row[3]).split() for w in rest):
            best = 1                      # "hue viet nam", "paris france": first word is the place, the rest its region
        else:
            continue
        scored.append((best, -row[7], row))
    scored.sort(key=lambda x: (x[0], x[1]))
    return [dict(zip(_FIELDS, r)) for _, _, r in scored[:limit]]


def attribution() -> str:
    return _table()[0]
