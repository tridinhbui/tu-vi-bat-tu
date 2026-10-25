"""Aspects between chart points and the classic multi-planet configurations. Geometry only; meaning lives in the reading."""
from __future__ import annotations

import itertools
from dataclasses import dataclass, asdict

from . import kb
from .zodiac import angdiff, sign_distance

LUMINARIES = {"sun", "moon"}
ANGLES = {"asc", "mc"}
PATTERN_BODIES = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto")


@dataclass
class Aspect:
    a: str
    b: str
    type: str
    angle: float
    orb: float                 # |actual separation - exact angle|, degrees
    max_orb: float
    applying: bool | None      # None when an angle takes part (natal angles do not move along the zodiac like planets)
    exactness: float           # 1 at exact, 0 at the edge of the orb
    whole_sign: bool           # the two points are also the right number of signs apart
    family: str

    def as_dict(self):
        return asdict(self)


def _orb_for(scheme: dict, a: str, b: str, asp: dict) -> float | None:
    if scheme.get("planet_orbs"):                                   # moiety scheme (Lilly): Ptolemaic aspects only
        if asp["family"] != "major":
            return None
        po = scheme["planet_orbs"]
        if a not in po or b not in po:
            return None
        return (po[a] + po[b]) / 2.0
    fam = scheme["major"] if asp["family"] == "major" else scheme["minor"]
    orb = fam.get(asp["id"])
    if orb is None:
        return None
    if asp["family"] == "major" and (a in LUMINARIES or b in LUMINARIES):
        orb += scheme.get("luminary_bonus", {}).get(asp["id"], 0)
    for p in (a, b):                                                # nodes, Chiron, lots take their own (smaller) orb
        if p in scheme.get("point_orbs", {}):
            orb = min(orb, scheme["point_orbs"][p])
    if a in ANGLES or b in ANGLES:
        orb *= scheme.get("angle_orb_factor", 1.0)
    return orb


def find(points: dict[str, dict], scheme_id: str = "thienban", minor: bool = True,
         only_conj: frozenset[str] = frozenset({"fortune", "south_node"})) -> list[Aspect]:
    """All aspects among `points` ({name: {lon, speed}}). Points listed in `only_conj` take part in conjunctions only."""
    scheme = kb.aspects()["orb_schemes"][scheme_id]
    defs = [d for d in kb.aspects()["aspects"] if minor or d["family"] == "major"]
    out: list[Aspect] = []
    names = list(points)
    for a, b in itertools.combinations(names, 2):
        if {a, b} <= ANGLES or {a, b} == {"north_node", "south_node"}:
            continue
        pa, pb = points[a], points[b]
        sep = abs(angdiff(pb["lon"], pa["lon"]))
        best = None
        for d in defs:
            if d["id"] != "conjunction" and (a in only_conj or b in only_conj):
                continue
            mo = _orb_for(scheme, a, b, d)
            if mo is None:
                continue
            orb = abs(sep - d["angle"])
            if orb <= mo and (best is None or orb / mo < best[1] / best[2]):
                best = (d, orb, mo)
        if not best:
            continue
        d, orb, mo = best
        applying = None
        if a not in ANGLES and b not in ANGLES and pa.get("speed") is not None and pb.get("speed") is not None:
            # orb shrinks <=> the signed gap moves toward the exact angle
            x = angdiff(pb["lon"], pa["lon"])                         # signed b - a
            target = d["angle"] if x >= 0 else -d["angle"]
            rate = pb["speed"] - pa["speed"]
            applying = (x - target) * rate < 0 if orb > 1e-9 else False
        ws = "signs_apart" in d and sign_distance(pa["lon"], pb["lon"]) in (d["signs_apart"], (12 - d["signs_apart"]) % 12)
        out.append(Aspect(a, b, d["id"], d["angle"], round(orb, 4), mo, applying, round(1 - orb / mo, 3), ws, d["family"]))
    out.sort(key=lambda x: (x.family != "major", x.orb))
    return out


def sign_aspects(points: dict[str, dict]) -> list[dict]:
    """Hellenistic whole-sign aspects (Ptolemaic configurations counted by sign, no orb)."""
    by_signs = {d["signs_apart"]: d for d in kb.aspects()["aspects"] if d["family"] == "major"}
    out = []
    for a, b in itertools.combinations(list(points), 2):
        n = sign_distance(points[a]["lon"], points[b]["lon"])
        n = min(n, 12 - n)
        if n in by_signs:
            out.append({"a": a, "b": b, "type": by_signs[n]["id"], "signs_apart": n})
    return out


def patterns(aspects: list[Aspect], points: dict[str, dict]) -> list[dict]:
    body = [p for p in PATTERN_BODIES if p in points]
    rel: dict[frozenset, str] = {frozenset((x.a, x.b)): x.type for x in aspects if x.a in body and x.b in body}
    has = lambda p, q, t: rel.get(frozenset((p, q))) == t
    found: list[dict] = []
    for p, q, r in itertools.combinations(body, 3):
        if has(p, q, "trine") and has(q, r, "trine") and has(p, r, "trine"):
            found.append({"type": "grand_trine", "bodies": [p, q, r]})
    for p, q in itertools.combinations(body, 2):
        if has(p, q, "opposition"):
            for r in body:
                if r not in (p, q) and has(p, r, "square") and has(q, r, "square"):
                    found.append({"type": "t_square", "bodies": [p, q, r], "apex": r})
        if has(p, q, "sextile"):
            for r in body:
                if r not in (p, q) and has(p, r, "quincunx") and has(q, r, "quincunx"):
                    found.append({"type": "yod", "bodies": [p, q, r], "apex": r})
    for quad in itertools.combinations(body, 4):
        pairs = [(x, y) for x, y in itertools.combinations(quad, 2)]
        kinds = sorted(rel.get(frozenset(pr), "") for pr in pairs)
        if kinds == sorted(["opposition"] * 2 + ["square"] * 4):
            found.append({"type": "grand_cross", "bodies": list(quad)})
        if kinds == sorted(["opposition"] * 2 + ["trine"] * 2 + ["sextile"] * 2):
            found.append({"type": "mystic_rectangle", "bodies": list(quad)})
    for gt in [f for f in found if f["type"] == "grand_trine"]:
        for corner in gt["bodies"]:
            others = [x for x in gt["bodies"] if x != corner]
            for d in body:
                if d not in gt["bodies"] and has(d, corner, "opposition") and all(has(d, o, "sextile") for o in others):
                    found.append({"type": "kite", "bodies": gt["bodies"] + [d], "tail": d, "head": corner})
    # a grand cross contains four T-squares: keep the larger figure only
    crosses = [set(f["bodies"]) for f in found if f["type"] == "grand_cross"]
    return [f for f in found if not (f["type"] == "t_square" and any(set(f["bodies"]) <= c for c in crosses))]
