"""Essential and accidental dignities, reception and solar phase, after Lilly (Christian Astrology pp.101-116).

Tables come from engine/data/horary/tables_lilly.json (p.104 essential table, p.107 orbs, p.113 solar distances, p.115
fortitude/debility points), transcribed from the page images. Where Lilly leaves a parameter open the engine's choice is
named in the output (`choice`) and documented in the rule record it cites.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, asdict
from functools import lru_cache

from . import kb
from .astro import TRAD

SIGN_NAMES = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius",
              "Pisces")
BENEFICS, MALEFICS = ("jupiter", "venus"), ("saturn", "mars")


@lru_cache(maxsize=1)
def table() -> dict:
    rows = kb.tables()["essential"]["rows"]
    return {s: kb.lower(rows[name]) | {"_name": name} for s, name in enumerate(SIGN_NAMES)}


@lru_cache(maxsize=1)
def orbs(column: str = "lilly") -> dict[str, float]:
    """Each planet's full orb in degrees. column 'lilly' = the value Lilly prints first on p.107 (Saturn 10, Jupiter 12,
    Mars 7.30, Sun 17, Venus 8, Mercury 7, Moon 12.30); 'other' = the right-hand column, which equals his planet chapters."""
    rows = kb.tables()["orbs"]["p107_table"]["rows"]
    return {k.lower(): v[column][0] + v[column][1] / 60.0 for k, v in rows.items()}


@lru_cache(maxsize=1)
def mean_motion() -> dict[str, float]:
    """Mean daily motion in degrees (Lilly's planet chapters). Mars is printed '31 degr. 27 min.' on p.65, an evident slip
    for 31 minutes 27 seconds (his diurnal motion beside it is 32-44 minutes); the table records it that way."""
    rows = kb.tables()["mean_motion"]["rows"]
    return {k.lower(): v["mean"][0] + v["mean"][1] / 60 + v["mean"][2] / 3600 for k, v in rows.items()}


def solar_limits() -> dict:
    sd = kb.tables()["sun_distances"]
    return {"cazimi": sd["cazimi_max_arcmin"] / 60.0, "combust": sd["combust_max_deg"], "beams": sd["under_beams_max_deg"],
            "combust_same_sign": sd.get("combust_same_sign_required", True)}


# ------------------------------------------------------------------ essential

def sign_of(lon: float) -> int:
    return int(lon // 30) % 12


def lords(lon: float, is_day: bool) -> dict:
    """Who rules each essential dignity of the degree `lon` (Lilly's table)."""
    r = table()[sign_of(lon)]
    deg = lon % 30
    term = next(p for p, end in r["terms"] if deg < end)
    face = next(p for p, end in r["faces"] if deg < end)
    trip = r["triplicity"]["day" if is_day else "night"]
    exalt = r["exaltation"][0] if r["exaltation"] else None
    return {"house": r["house"], "exaltation": exalt if exalt in TRAD else None, "exaltation_printed": exalt,
            "triplicity": trip, "term": term, "face": face, "detriment": r["detriment"],
            "fall": r["fall"] if r["fall"] in TRAD else None}


@dataclass
class Essential:
    planet: str
    sign: str
    has: list[str]
    debilities: list[str]
    peregrine: bool
    score: int
    lords: dict
    rule: str = "lilly.dignity.essential_table"

    def as_dict(self):
        return asdict(self)


def essential(planet: str, lon: float, is_day: bool) -> Essential:
    pts = kb.tables()["essential"]["scores"]
    L = lords(lon, is_day)
    has = [k for k in ("house", "exaltation", "triplicity", "term", "face") if L[k] == planet]
    deb = [k for k in ("detriment", "fall") if L[k] == planet]
    peregrine = not has
    score = sum(pts[k] for k in has) + sum(pts[k] for k in deb)
    if peregrine:
        score += next(r["points"] for r in kb.tables()["fortitudes"]["rows"] if r["key"] == "peregrine")
    return Essential(planet, SIGN_NAMES[sign_of(lon)], has, deb, peregrine, score, L)


# ------------------------------------------------------------------ reception

def receptions(chart) -> list[dict]:
    """Every reception among the seven planets: `by` receives `planet` when `planet` stands in a dignity of `by`.
    Mutual when each is in the other's dignity (Lilly scores mutual reception by house as +5, by exaltation as +4)."""
    out = []
    for a in TRAD:
        La = lords(chart.bodies[a].lon, chart.is_day)
        for kind in ("house", "exaltation", "triplicity", "term", "face"):
            b = La[kind]
            if b and b != a and b in TRAD:
                out.append({"planet": a, "by": b, "dignity": kind})
    for r in out:
        back = [x["dignity"] for x in out if x["planet"] == r["by"] and x["by"] == r["planet"]]
        r["mutual_with"] = back
    return out


def reception_between(recs: list[dict], a: str, b: str) -> dict:
    """How a and b receive each other: {'a_by_b': [...], 'b_by_a': [...], 'mutual': bool, 'strong': bool}.
    'strong' = reception by house or exaltation (the two Lilly scores like essential dignity)."""
    ab = [r["dignity"] for r in recs if r["planet"] == a and r["by"] == b]
    ba = [r["dignity"] for r in recs if r["planet"] == b and r["by"] == a]
    major = {"house", "exaltation"}
    return {"a_by_b": ab, "b_by_a": ba, "mutual": bool(ab and ba),
            "strong": bool(set(ab) & major) or bool(set(ba) & major),
            "mutual_major": bool(set(ab) & major) and bool(set(ba) & major)}


# ------------------------------------------------------------------ solar phase

def elongation(chart, p: str) -> float:
    """Signed distance planet - Sun in (-180, 180]: positive = east of the Sun (occidental, sets after it)."""
    return (chart.bodies[p].lon - chart.bodies["sun"].lon + 180.0) % 360.0 - 180.0


def solar_phase(chart, p: str) -> dict:
    if p == "sun":
        return {"state": "sun"}
    lim = solar_limits()
    e = elongation(chart, p)
    d = abs(e)
    same_sign = sign_of(chart.bodies[p].lon) == sign_of(chart.bodies["sun"].lon)
    if d <= lim["cazimi"] and same_sign:
        st = "cazimi"
    elif d <= lim["combust"] and (same_sign or not lim["combust_same_sign"]):
        st = "combust"
    elif d <= lim["beams"]:
        st = "under_beams"
    else:
        st = "free"
    return {"state": st, "distance": d, "same_sign": same_sign, "oriental": e < 0, "occidental": e > 0,
            "rule": {"cazimi": "lilly.sun.cazimi", "combust": "lilly.sun.combust", "under_beams": "lilly.sun.under_beams",
                     "free": "lilly.sun.free"}[st],
            "choice": "Ngoài 8°30′ mà trong 17° thì tính 'dưới tia nắng' (Lilly không nói có cần cùng cung hay không)."
            if st == "under_beams" else None}


# ------------------------------------------------------------------ fixed stars of the p.115 table

_STARS = {   # Hipparcos (ESA 1997) J2000 position and proper motion: RA h, Dec deg, pmRA* mas/yr, pmDec mas/yr
    "cor_leonis": ("Regulus (Cor Leonis)", 10 + 8 / 60 + 22.311 / 3600, 11 + 58 / 60 + 1.95 / 3600, -248.73, 5.59),
    "spica": ("Spica Virginis", 13 + 25 / 60 + 11.579 / 3600, -(11 + 9 / 60 + 40.75 / 3600), -42.35, -30.67),
    "caput_algol": ("Caput Algol", 3 + 8 / 60 + 10.132 / 3600, 40 + 57 / 60 + 20.33 / 3600, 2.99, -1.66),
}


def star_longitudes(jd_ut: float) -> dict[str, float]:
    """Apparent ecliptic longitude of date of the three stars Lilly scores. Lilly prints their 1647 places (24 Leo, 18 Libra,
    20 Taurus); the stars have since moved about 5° in longitude by precession, so the engine uses their place at the date
    of the question (choice recorded in lilly.dignity.fixed_stars)."""
    from . import astro
    if not astro.in_range(jd_ut):                       # study charts: PyEphem's own star catalogue, precessed to the date
        import ephem
        d = ephem.Date(jd_ut - 2415020.0)
        out = {}
        for k, name in (("cor_leonis", "Regulus"), ("spica", "Spica"), ("caput_algol", "Algol")):
            s = ephem.star(name)
            s.compute(d, epoch=d)
            out[k] = math.degrees(ephem.Ecliptic(ephem.Equatorial(s.g_ra, s.g_dec, epoch=d), epoch=d).lon) % 360.0
        return out
    from skyfield.api import Star
    from skyfield.framelib import ecliptic_frame
    from western import ephemeris as W
    t = W.time_jd_ut(jd_ut)
    out = {}
    for k, (_, ra, dec, pmra, pmdec) in _STARS.items():
        s = Star(ra_hours=ra, dec_degrees=dec, ra_mas_per_year=pmra, dec_mas_per_year=pmdec)
        _, lon, _ = W.earth().at(t).observe(s).apparent().frame_latlon(ecliptic_frame)
        out[k] = lon.degrees % 360.0
    return out


# ------------------------------------------------------------------ accidental

@dataclass
class Accidental:
    planet: str
    items: list[dict] = field(default_factory=list)       # {key, label_en, points, detail}
    score: int = 0
    rule: str = "lilly.dignity.fortitude_table"

    def as_dict(self):
        return asdict(self)


LABEL_VI = {   # Vietnamese labels of the p.115 rows (the English label_en stays the transcription of the page)
    "angular_10_1": "Ở Thiên Đỉnh hoặc nhà 1", "angular_7_4_succedent_11": "Ở nhà 7, 4 hoặc 11", "succedent_2_5": "Ở nhà 2 hoặc 5",
    "cadent_9": "Ở nhà 9", "cadent_3": "Ở nhà 3", "direct": "Thuận hành", "swift": "Đi nhanh hơn trung bình",
    "superiors_oriental": "Thổ, Mộc, Hỏa ở phương đông (mọc trước Mặt Trời)", "inferiors_occidental": "Thủy, Kim ở phương tây (lặn sau Mặt Trời)",
    "moon_increasing_or_occidental": "Trăng đang tròn dần", "free_from_combustion_and_beams": "Không bị đốt, không dưới tia nắng",
    "cazimi": "Ở tim Mặt Trời (cazimi)", "partile_conj_jupiter_venus": "Hội hợp đúng độ với Mộc hoặc Kim",
    "partile_conj_north_node": "Hội hợp đúng độ với La Hầu", "partile_trine_jupiter_venus": "Tam hợp đúng độ với Mộc hoặc Kim",
    "partile_sextile_jupiter_venus": "Lục hợp đúng độ với Mộc hoặc Kim", "conj_cor_leonis": "Hội hợp sao Regulus (Cor Leonis)",
    "conj_spica": "Hội hợp sao Spica", "cadent_12": "Ở nhà 12", "cadent_6_succedent_8": "Ở nhà 6 hoặc 8", "retrograde": "Nghịch hành",
    "slow": "Đi chậm hơn trung bình", "superiors_occidental": "Thổ, Mộc, Hỏa ở phương tây", "inferiors_oriental": "Thủy, Kim ở phương đông",
    "moon_decreasing": "Trăng đang khuyết dần", "combust": "Bị Mặt Trời đốt", "under_beams": "Dưới tia nắng Mặt Trời",
    "partile_conj_saturn_mars": "Hội hợp đúng độ với Thổ hoặc Hỏa", "partile_conj_south_node": "Hội hợp đúng độ với Kế Đô",
    "besieged": "Bị Thổ và Hỏa vây", "partile_opposition_saturn_mars": "Xung chiếu đúng độ với Thổ hoặc Hỏa",
    "partile_square_saturn_mars": "Vuông góc đúng độ với Thổ hoặc Hỏa", "conj_caput_algol": "Hội hợp sao Algol (trong 5°)",
}


def _row(key: str) -> dict:
    return next(r for r in kb.tables()["fortitudes"]["rows"] if r["key"] == key)


def _partile(l1: float, l2: float, angle: int) -> bool:
    """Partile: the aspect is exact by whole degree — the two planets are in the same degree-number of their signs and the
    signs are in that aspect (lilly.aspect.partile)."""
    d1, d2 = int(l1 % 30), int(l2 % 30)
    sd = (sign_of(l1) - sign_of(l2)) % 12
    ok_sign = sd in {0: (0,), 60: (2, 10), 90: (3, 9), 120: (4, 8), 180: (6,)}[angle]
    return d1 == d2 and ok_sign


HOUSE_KEYS = {1: "angular_10_1", 10: "angular_10_1", 7: "angular_7_4_succedent_11", 4: "angular_7_4_succedent_11",
              11: "angular_7_4_succedent_11", 2: "succedent_2_5", 5: "succedent_2_5", 9: "cadent_9", 3: "cadent_3",
              12: "cadent_12", 8: "cadent_6_succedent_8", 6: "cadent_6_succedent_8"}


def accidental(chart, p: str, stars: dict[str, float] | None = None, star_orb: float = 5.0) -> Accidental:
    b = chart.bodies[p]
    acc = Accidental(p)

    def add(key, detail=None):
        r = _row(key)
        acc.items.append({"key": key, "label_en": r["label_en"], "label_vi": LABEL_VI.get(key, r["label_en"]), "points": r["points"],
                          "detail": detail})

    add(HOUSE_KEYS[b.house], f"nhà {b.house}")
    if p not in ("sun", "moon"):
        add("retrograde" if b.retrograde else "direct", f"{b.speed:+.4f}°/ngày")
    mm = mean_motion()[p]
    add("swift" if abs(b.speed) > mm else "slow", f"|{abs(b.speed):.4f}| so với trung bình {mm:.4f}°/ngày")
    e = elongation(chart, p) if p != "sun" else 0.0
    if p in ("saturn", "jupiter", "mars"):
        add("superiors_oriental" if e < 0 else "superiors_occidental", f"cách Mặt Trời {e:+.2f}°")
    elif p in ("venus", "mercury"):
        add("inferiors_occidental" if e > 0 else "inferiors_oriental", f"cách Mặt Trời {e:+.2f}°")
    elif p == "moon":
        add("moon_increasing_or_occidental" if e > 0 else "moon_decreasing", f"cách Mặt Trời {e:+.2f}°")
    if p != "sun":
        sp = solar_phase(chart, p)
        if sp["state"] == "cazimi":
            add("cazimi", f"{sp['distance'] * 60:.1f}′ từ tâm Mặt Trời")
        elif sp["state"] == "combust":
            add("combust", f"{sp['distance']:.2f}° cùng cung Mặt Trời")
        elif sp["state"] == "under_beams":
            add("under_beams", f"{sp['distance']:.2f}° từ Mặt Trời")
        else:
            add("free_from_combustion_and_beams", f"{sp['distance']:.2f}° từ Mặt Trời")
    for q in BENEFICS + MALEFICS:
        if q == p:
            continue
        lq = chart.bodies[q].lon
        for angle, ben_key, mal_key in ((0, "partile_conj_jupiter_venus", "partile_conj_saturn_mars"),
                                        (120, "partile_trine_jupiter_venus", None), (60, "partile_sextile_jupiter_venus", None),
                                        (180, None, "partile_opposition_saturn_mars"), (90, None, "partile_square_saturn_mars")):
            key = ben_key if q in BENEFICS else mal_key
            if key and _partile(b.lon, lq, angle):
                add(key, f"với {q}")
    for nk, key in (("north", "partile_conj_north_node"), ("south", "partile_conj_south_node")):
        if _partile(b.lon, chart.nodes[nk], 0):
            add(key, f"{'La Hầu' if nk == 'north' else 'Kế Đô'} {chart.nodes[nk]:.2f}°")
    if p not in MALEFICS and besieged(chart, p):
        add("besieged", "giữa Thổ tinh và Hỏa tinh")
    stars = stars if stars is not None else star_longitudes(chart.jd_ut)
    for sk, key in (("cor_leonis", "conj_cor_leonis"), ("spica", "conj_spica"), ("caput_algol", "conj_caput_algol")):
        d = abs((b.lon - stars[sk] + 180) % 360 - 180)
        if d <= star_orb:
            add(key, f"cách {d:.2f}° (sao ở {stars[sk]:.2f}°)")
    acc.score = sum(i["points"] for i in acc.items)
    return acc


def besieged(chart, p: str) -> bool:
    """Lilly's 'besieged of Saturn and Mars' (lilly.besieged): the planet stands between the bodies of the two malefics.
    Engine reading recorded in the rule: by bodies only, all three in one sign, and no other planet between them."""
    ls, lm, lp = chart.bodies["saturn"].lon, chart.bodies["mars"].lon, chart.bodies[p].lon
    if not (sign_of(ls) == sign_of(lm) == sign_of(lp)):
        return False
    lo, hi = sorted((ls, lm))
    if not lo < lp < hi:
        return False
    others = [q for q in TRAD if q not in (p, "saturn", "mars") and lo < chart.bodies[q].lon < hi and sign_of(chart.bodies[q].lon) == sign_of(lp)]
    return not others


def strength(chart, p: str) -> dict:
    es = essential(p, chart.bodies[p].lon, chart.is_day)
    ac = accidental(chart, p)
    return {"planet": p, "essential": es.as_dict(), "accidental": ac.as_dict(), "essential_score": es.score,
            "accidental_score": ac.score, "total": es.score + ac.score,
            "note": "Lilly cho điểm trong bảng tr.115 nhưng không nói cách cộng gộp (tr.116); tổng chỉ để so sánh, không tự quyết định phán đoán."}
