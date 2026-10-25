"""Synastry: two natal charts side by side.

Geometry: aspects from each body/angle of chart A to each of chart B (orb scheme as for the natal chart) and each chart's
bodies placed in the other's houses. Rule: Ptolemy compares the four places of greatest authority, Sun, Moon, Ascendant and
Lot of Fortune, sign by sign (Tetrabiblos IV.7, friendship), and the luminaries of the two charts (IV.5, marriage).
"""
from __future__ import annotations

from . import houses as H, kb
from .aspects import _orb_for
from .zodiac import angdiff, sign_distance, sign_index

POINTS = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto", "chiron", "north_node")
SIGN_REL = {0: "same", 1: "disjunct", 2: "sextile", 3: "square", 4: "trine", 5: "disjunct", 6: "opposition"}


def _pts(c: dict) -> dict:
    out = {k: {"lon": c["bodies"][k]["lon"] if k in c["bodies"] else c["points"][k]["lon"]} for k in POINTS}
    if "angles" in c:
        out["asc"] = {"lon": c["angles"]["asc"]["lon"]}
        out["mc"] = {"lon": c["angles"]["mc"]["lon"]}
    return out


def inter_aspects(a: dict, b: dict, scheme_id: str = "thienban") -> list[dict]:
    scheme = kb.aspects()["orb_schemes"][scheme_id]
    defs = [d for d in kb.aspects()["aspects"] if d["family"] == "major"]
    pa, pb = _pts(a), _pts(b)
    out = []
    for x, vx in pa.items():
        for y, vy in pb.items():
            if x in ("asc", "mc") and y in ("asc", "mc"):
                continue
            sep = abs(angdiff(vx["lon"], vy["lon"]))
            best = None
            for d in defs:
                mo = _orb_for(scheme, x, y, d)
                if mo is None:
                    continue
                orb = abs(sep - d["angle"])
                if orb <= mo and (best is None or orb / mo < best[1] / best[2]):
                    best = (d["id"], orb, mo)
            if best:
                out.append({"a": x, "b": y, "type": best[0], "orb": round(best[1], 3), "max_orb": best[2]})
    return sorted(out, key=lambda r: r["orb"])


def overlays(a: dict, b: dict) -> dict:
    """Bodies of A in B's houses (B's chosen system), and of B in A's."""
    def place(src, dst):
        if "houses" not in dst:
            return None
        cs = [c["lon"] for c in dst["houses"]["cusps"][dst["houses"]["system"]]]
        return {k: H.house_of(v["lon"], cs) for k, v in _pts(src).items() if k not in ("asc", "mc")}
    return {"a_in_b": place(a, b), "b_in_a": place(b, a)}


def _lot(c: dict) -> float | None:
    if "angles" not in c:
        return None
    return (c["angles"]["asc"]["lon"] + c["bodies"]["moon"]["lon"] - c["bodies"]["sun"]["lon"]) % 360.0      # Ptolemy III.10


def ptolemy_places(a: dict, b: dict) -> dict:
    """IV.7: sign relation of each of the four places of authority between the two charts, plus exchanges."""
    la = {"sun": a["bodies"]["sun"]["lon"], "moon": a["bodies"]["moon"]["lon"], "asc": a.get("angles", {}).get("asc", {}).get("lon"), "lot": _lot(a)}
    lb = {"sun": b["bodies"]["sun"]["lon"], "moon": b["bodies"]["moon"]["lon"], "asc": b.get("angles", {}).get("asc", {}).get("lon"), "lot": _lot(b)}
    rel = {}
    for k in la:
        if la[k] is None or lb[k] is None:
            rel[k] = None
            continue
        n = sign_distance(la[k], lb[k])
        rel[k] = {"relation": SIGN_REL[min(n, 12 - n)], "degrees": round(abs(angdiff(la[k], lb[k])), 2)}
    exchanges = []
    keys = [k for k in la if la[k] is not None and lb[k] is not None]
    for i, x in enumerate(keys):
        for y in keys[i + 1:]:
            if sign_index(la[x]) == sign_index(lb[y]) and sign_index(la[y]) == sign_index(lb[x]):
                exchanges.append([x, y])
    lum = {}
    for x in ("sun", "moon"):
        for y in ("sun", "moon"):
            n = sign_distance(la[x], lb[y])
            lum[f"{x}_a-{y}_b"] = SIGN_REL[min(n, 12 - n)]
    return {"places": rel, "exchanges": exchanges, "luminaries": lum}


def compare(a: dict, b: dict, scheme_id: str = "thienban") -> dict:
    return {"aspects": inter_aspects(a, b, scheme_id), "overlays": overlays(a, b), "ptolemy": ptolemy_places(a, b)}
