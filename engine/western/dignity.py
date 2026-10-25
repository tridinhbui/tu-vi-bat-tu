"""Essential dignities of a planet at a longitude, from the tables in kb/dignities.json. Classical seven planets only."""
from __future__ import annotations

from . import kb
from .zodiac import ELEMENT, SIGNS, deg_in_sign, sign_index

CLASSICAL = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn")


def _opposite(sign: str) -> str:
    return SIGNS[(SIGNS.index(sign) + 6) % 12]


def domicile_lord(sign: str) -> str:
    return kb.dignities()["domicile"]["table"][sign][0]


def modern_lord(sign: str) -> str:
    return next(s["modern_ruler"] for s in kb.core()["signs"] if s["id"] == sign)


def exaltation_lord(sign: str) -> str | None:
    e = kb.dignities()["exaltation"]["table"].get(sign)
    return e[0] if e else None


def triplicity_lords(sign: str, scheme: str) -> list[str]:
    return kb.dignities()["triplicity"][scheme]["table"][ELEMENT[SIGNS.index(sign)]]


def term_lord(lon: float, scheme: str) -> str | None:
    table = kb.dignities()["terms"][scheme]["table"]
    sign, d = SIGNS[sign_index(lon)], deg_in_sign(lon)
    for planet, end in table.get(sign, []):
        if d < end:
            return planet
    return None


def face_lord(lon: float) -> str:
    f = kb.dignities()["faces"]
    order = f["order"]
    return order[(order.index(f["start"]) + int((lon % 360.0) // 10.0)) % 7]


def essential(planet: str, lon: float, is_day: bool | None, triplicity: str = "dorothean", terms: str = "egyptian") -> dict:
    """Which essential dignities and debilities `planet` holds at `lon`, plus the lord of each dignity of that degree."""
    sign = SIGNS[sign_index(lon)]
    trip = triplicity_lords(sign, triplicity)
    trip_ruler = None
    if is_day is not None:
        trip_ruler = trip[0] if is_day else trip[1]
    lords = {"domicile": domicile_lord(sign), "exaltation": exaltation_lord(sign), "triplicity": trip,
             "triplicity_ruler": trip_ruler, "term": term_lord(lon, terms), "face": face_lord(lon)}
    if planet not in CLASSICAL:
        return {"lords": lords, "has": [], "debilities": [], "peregrine": None, "classical": False}
    has = []
    if planet in kb.dignities()["domicile"]["table"][sign]:
        has.append("domicile")
    if lords["exaltation"] == planet:
        has.append("exaltation")
    # by sect when the sect is known (Lilly counts only the ruler of the sect); Dorothean participating lord counts too
    if (trip_ruler == planet) or (is_day is None and planet in trip[:2]) or (triplicity == "dorothean" and len(trip) > 2 and trip[2] == planet):
        has.append("triplicity")
    if lords["term"] == planet:
        has.append("term")
    if lords["face"] == planet:
        has.append("face")
    debilities = []
    if planet in kb.dignities()["domicile"]["table"][_opposite(sign)]:
        debilities.append("detriment")
    if exaltation_lord(_opposite(sign)) == planet:
        debilities.append("fall")
    peregrine = not (set(has) & {"domicile", "exaltation", "triplicity", "term", "face"})
    scores = kb.dignities()["scores"]["essential"]
    score = sum(scores[h] for h in has) + sum(scores[d] for d in debilities) + (scores["peregrine"] if peregrine else 0)
    return {"lords": lords, "has": has, "debilities": debilities, "peregrine": peregrine, "score": score, "classical": True}


def almuten(lon: float, is_day: bool, triplicity: str = "ptolemaic", terms: str = "ptolemaic") -> list[str]:
    """Planet(s) with the most essential dignity at a degree (Lilly's scores: domicile 5, exaltation 4, triplicity 3, term 2, face 1)."""
    sc = kb.dignities()["scores"]["essential"]
    tot = {p: 0 for p in CLASSICAL}
    sign = SIGNS[sign_index(lon)]
    tot[domicile_lord(sign)] += sc["domicile"]
    if exaltation_lord(sign):
        tot[exaltation_lord(sign)] += sc["exaltation"]
    trip = triplicity_lords(sign, triplicity)
    tot[trip[0] if is_day else trip[1]] += sc["triplicity"]
    if term_lord(lon, terms):
        tot[term_lord(lon, terms)] += sc["term"]
    tot[face_lord(lon)] += sc["face"]
    best = max(tot.values())
    return [p for p, v in tot.items() if v == best]
