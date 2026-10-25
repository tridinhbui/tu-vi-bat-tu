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
    raw = json.loads(gzip.decompress((DATA / "places.json.gz").read_bytes()))
    rows = []
    for name, ascii_, alts, country, admin1, lat, lon, tz, pop in raw["rows"]:
        keys = {fold(name), fold(ascii_), *(fold(a) for a in alts)}
        rows.append((tuple(keys), {"name": _display(name, alts, country), "geonames_name": name, "admin1": admin1, "country": country, "lat": lat, "lon": lon, "tz": tz,
                                   "population": pop}))
    return raw["source"], rows


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
        best = None
        for k in keys:
            if k == q:
                s = 0
            elif k.startswith(q):
                s = 1
            elif (" " + q) in (" " + k):
                s = 2
            else:
                continue
            best = s if best is None else min(best, s)
        if best is None and rest:             # "hue viet nam", "paris france": first word is the place, the rest its region
            region = fold(row["admin1"] + " " + row["country"])
            if any(k == head or k.startswith(head) for k in keys) and all(w in region.split() for w in rest):
                best = 1
        if best is not None:
            scored.append((best, -row["population"], row))
    scored.sort(key=lambda x: (x[0], x[1]))
    return [r for _, _, r in scored[:limit]]


def attribution() -> str:
    return _table()[0]
