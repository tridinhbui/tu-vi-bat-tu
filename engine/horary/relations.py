"""Relations between planets at the moment of the question, read from the real event timeline (events.py).

Facts only, no verdict: for each pair the nearest Ptolemaic aspect, its orb, whether it is applying or separating, when it
perfects (or why it will not), and the third-planet configurations around the significators — translation and collection
of light, prohibition, frustration, refranation — each with the exact times and the rule id of the definition used. The
definitions and their sources live in engine/data/horary/*.json; `school` carries the numbers (orbs) the rules need.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field

import numpy as np

from . import astro, events as E
from .astro import TRAD

SPEED_ORDER = ("moon", "mercury", "venus", "sun", "mars", "jupiter", "saturn")      # by mean motion, lightest first
ASPECT_ANGLES = (0, 60, 90, 120, 180)


def _wrap(x: float) -> float:
    return (x + 180.0) % 360.0 - 180.0


def lighter(a: str, b: str) -> bool:
    """a is the lighter (faster by nature) planet. Used only where the tradition speaks of the lighter planet; actual
    application is always decided by the real motion."""
    return SPEED_ORDER.index(a) < SPEED_ORDER.index(b)


@dataclass
class PairState:
    a: str
    b: str
    angle: int                      # nearest Ptolemaic aspect
    orb: float                      # |separation - angle|, degrees
    moiety_sum: float               # half the sum of the two planets' orbs
    within_orb: bool
    by_sign: bool                   # the signs themselves are in that aspect (conjunction = same sign)
    motion: str                     # applying | separating | stationary_pair
    applier: str | None             # the planet that applies (faster at the moment), when applying
    next_perfection_jd: float | None
    perfection_before_sign_change: bool | None
    last_perfection_jd: float | None
    refranation: dict | None        # approach broken by a station before perfecting
    rule: str = "lilly.aspect.application"

    def as_dict(self):
        return asdict(self)


def _sign(lon: float) -> int:
    return int(lon // 30) % 12


def _by_sign(la: float, lb: float, angle: int) -> bool:
    d = (_sign(la) - _sign(lb)) % 12
    return d in {0: (0,), 60: (2, 10), 90: (3, 9), 120: (4, 8), 180: (6,)}[angle]


def pair_state(chart, ev: dict, a: str, b: str, orbs: dict[str, float]) -> PairState:
    A, B = chart.bodies[a], chart.bodies[b]
    d = _wrap(A.lon - B.lon)
    best = min(((abs(abs(d) - ang), ang) for ang in ASPECT_ANGLES))
    orb, angle = best
    g = (abs(d) - angle) * (1 if d >= 0 else -1)          # signed distance from exactness along the a-b direction
    rel = A.speed - B.speed
    closing = g * rel < 0                                   # |separation - angle| is shrinking
    if abs(rel) < 1e-6:
        motion = "stationary_pair"
    else:
        motion = "applying" if closing else "separating"
    t0 = chart.jd_ut
    perfs = [p for p in E.pair_perfections(ev, a, b) if p.angle == angle]
    nxt = next((p for p in perfs if p.jd > t0), None)
    last = next((p for p in reversed(perfs) if p.jd <= t0), None)
    refr = None
    applier = None
    before_sign = None
    if motion == "applying":
        applier = a if abs(A.speed) >= abs(B.speed) else b
        refr = _approach_broken(chart, ev, a, b, angle, nxt.jd if nxt else t0 + ev["fwd"])
        if nxt is not None:
            ia, ib = E.next_ingress(ev, a, t0), E.next_ingress(ev, b, t0)
            before_sign = all(x is None or x.jd > nxt.jd for x in (ia, ib))
    ms = (orbs[a] + orbs[b]) / 2.0
    return PairState(a, b, angle, orb, ms, orb <= ms, _by_sign(A.lon, B.lon, angle), motion, applier,
                     nxt.jd if nxt else None, before_sign, last.jd if last else None, refr)


def _approach_broken(chart, ev: dict, a: str, b: str, angle: int, until: float) -> dict | None:
    """Refranation test: while a and b are closing on `angle`, does the closing stop (a station turns the motion) before the
    aspect perfects? Checked on the ephemeris, 6-hourly, between now and the perfection (or the end of the window)."""
    t0 = chart.jd_ut
    sts = E.stations_between(ev, {a, b}, t0, until)
    if not sts:
        return None
    tt = np.arange(t0, min(until, t0 + ev["fwd"]), 0.25)
    if len(tt) < 3:
        return None
    la, lb = astro.longitudes(tt, a), astro.longitudes(tt, b)
    dist = np.abs(np.abs((la - lb + 180) % 360 - 180) - angle)
    turn = np.where(np.diff(dist) > 0)[0]
    if not len(turn) or tt[turn[0]] >= until - 0.5:
        return None
    k = int(turn[0])
    st = min(sts, key=lambda s: abs(s.jd - tt[k]))
    return {"station": st.as_dict(), "closest_jd": float(tt[k]), "closest_orb": float(dist[k]),
            "rule": "lilly.refranation"}


def all_pairs(chart, ev: dict, orbs: dict[str, float]) -> dict[tuple[str, str], PairState]:
    out = {}
    for i, a in enumerate(TRAD):
        for b in TRAD[i + 1:]:
            out[(a, b)] = pair_state(chart, ev, a, b, orbs)
    return out


def get(pairs: dict, a: str, b: str) -> PairState:
    return pairs.get((a, b)) or pairs[(b, a)]


# ---------------------------------------------------------------- configurations around two significators

@dataclass
class Config:
    kind: str                       # perfection | translation | collection | prohibition | frustration | refranation | none
    planets: list[str]
    jd: float | None
    detail: dict = field(default_factory=dict)
    rule: str = ""

    def as_dict(self):
        return asdict(self)


def configurations(chart, ev: dict, pairs: dict, s1: str, s2: str, orbs: dict[str, float],
                   require_orb: bool = True) -> list[Config]:
    """Every configuration that bears on whether s1 and s2 come together, in time order. `require_orb`: an application
    counts only within the moieties (Lilly); otherwise a whole-sign application that perfects before either planet changes
    sign is also listed (as `by_sign`), for schools that judge that way."""
    t0 = chart.jd_ut
    out: list[Config] = []
    if s1 == s2:
        return [Config("same_planet", [s1], None, {"note": "Cùng một hành tinh chủ quản cả hai bên."}, "lilly.significator.lord_of_house")]
    ps = get(pairs, s1, s2)
    perf_jd = None
    if ps.motion == "applying" and ps.next_perfection_jd is not None and ps.refranation is None:
        if ps.within_orb or not require_orb:
            perf_jd = ps.next_perfection_jd
            out.append(Config("perfection", [ps.applier, s2 if ps.applier == s1 else s1], perf_jd,
                              {"aspect": E.ASPECTS[ps.angle], "orb": ps.orb, "within_orb": ps.within_orb,
                               "before_sign_change": ps.perfection_before_sign_change, "by_sign": ps.by_sign},
                              {0: "lilly.perfection.conjunction", 60: "lilly.perfection.sextile_trine", 90: "lilly.perfection.square",
                               120: "lilly.perfection.sextile_trine", 180: "lilly.perfection.opposition"}[ps.angle]))
    if ps.motion == "applying" and ps.refranation is not None:
        out.append(Config("refranation", [s1, s2], ps.refranation["station"]["jd"], ps.refranation, "lilly.refranation"))

    # third-planet perfections with either significator before s1-s2 perfects (or within the window if they never do)
    horizon = perf_jd if perf_jd is not None else (ps.next_perfection_jd or t0 + 60.0)
    if perf_jd is not None:
        applied_to = s2 if ps.applier == s1 else s1
        applier = ps.applier
        for p in ev["perfections"]:
            if not (t0 < p.jd < perf_jd):
                continue
            third = ({p.a, p.b} - {s1, s2})
            if len(third) != 1 or {p.a, p.b} == {s1, s2}:
                continue
            x = third.pop()
            # Engine reading of Lilly's 'interposes his body or aspect' (lilly.prohibition): the third planet's contact counts only
            # if it is already in force at the question (within the moieties and applying, Lilly p.60/p.110: influence begins
            # within orb) and is the very contact that perfects first. The Moon, co-significator of the querent, is never the
            # interposer between the querent's own significators.
            if x == "moon":
                continue
            st3 = get(pairs, x, applied_to if applied_to in (p.a, p.b) else applier)
            if not (st3.within_orb and st3.motion == "applying" and st3.next_perfection_jd is not None
                    and abs(st3.next_perfection_jd - p.jd) < 1e-6):
                continue
            if applied_to in (p.a, p.b) and p.a == applied_to:
                # the heavier planet itself goes to another first (Lilly: frustration; defined for the conjunction)
                out.append(Config("frustration", [applied_to, x, applier], p.jd,
                                  {"aspect": E.ASPECTS[p.angle], "by_body": p.angle == 0,
                                   "note": "hành tinh được tiến tới lại kết hợp với hành tinh khác trước",
                                   "extension": None if p.angle == 0 else "Lilly định nghĩa frustration cho hội hợp; trường hợp góc chiếu là cách mở rộng của Thiên Bàn"},
                                  "lilly.frustration"))
            else:
                # a third planet interposes its body or aspect with either significator first (Lilly: prohibition)
                met = applied_to if applied_to in (p.a, p.b) else applier
                out.append(Config("prohibition", [x, met, applied_to if met == applier else applier], p.jd,
                                  {"aspect": E.ASPECTS[p.angle], "interposer": x, "met": met, "by_body": p.angle == 0,
                                   "note": "hành tinh thứ ba chen vào trước"}, "lilly.prohibition"))

    # translation of light: a lighter planet separating from one significator and applying to the other
    for t in TRAD:
        if t in (s1, s2):
            continue
        for frm, to in ((s1, s2), (s2, s1)):
            pf, pt = get(pairs, t, frm), get(pairs, t, to)
            if not (pf.motion == "separating" and pf.within_orb and pt.motion == "applying" and pt.within_orb):
                continue
            if pt.next_perfection_jd is None or pt.refranation is not None:
                continue
            if not (lighter(t, frm) and lighter(t, to)) and abs(chart.bodies[t].speed) < max(abs(chart.bodies[frm].speed), abs(chart.bodies[to].speed)):
                continue
            out.append(Config("translation", [t, frm, to], pt.next_perfection_jd,
                              {"from": frm, "to": to, "separated_jd": pf.last_perfection_jd, "aspect_from": E.ASPECTS[pf.angle],
                               "aspect_to": E.ASPECTS[pt.angle]}, "lilly.translation"))

    # collection of light: both significators apply to a heavier planet that neither has reached
    if not any(c.kind == "perfection" for c in out):
        for c in TRAD:
            if c in (s1, s2):
                continue
            p1, p2 = get(pairs, s1, c), get(pairs, s2, c)
            if (p1.motion == "applying" and p2.motion == "applying" and p1.within_orb and p2.within_orb
                    and p1.applier == s1 and p2.applier == s2 and p1.next_perfection_jd and p2.next_perfection_jd
                    and not p1.refranation and not p2.refranation):
                out.append(Config("collection", [c, s1, s2], max(p1.next_perfection_jd, p2.next_perfection_jd),
                                  {"collector": c, "aspect_1": E.ASPECTS[p1.angle], "aspect_2": E.ASPECTS[p2.angle],
                                   "reception_checked_in": "judgment"}, "lilly.collection"))
    out.sort(key=lambda c: c.jd if c.jd is not None else 1e12)
    return out


# ---------------------------------------------------------------- the Moon's course

def moon_course(chart, ev: dict, orbs: dict[str, float]) -> dict:
    """The Moon's perfections until she leaves her sign, her last separation, and void-of-course under both readings:
    by sign (no perfection of any Ptolemaic aspect before the sign ends) and by orb (no application within moieties)."""
    t0 = chart.jd_ut
    ing = E.next_ingress(ev, "moon", t0)
    end = ing.jd if ing else t0 + 3
    mp = [p for p in ev["perfections"] if "moon" in (p.a, p.b)]
    nxt = [p for p in mp if t0 < p.jd < end]
    last = next((p for p in reversed(mp) if p.jd <= t0), None)
    after = [p for p in mp if p.jd >= end][:1]
    within = []
    for p in TRAD:
        if p == "moon":
            continue
        st = pair_state(chart, ev, "moon", p, orbs)
        if st.motion == "applying" and st.within_orb:
            within.append(p)
    return {"sign_exit_jd": end, "next_sign": ing.sign_to if ing else None,
            "perfections_in_sign": [p.as_dict() for p in nxt],
            "last_separation": last.as_dict() if last else None,
            "first_after_sign": after[0].as_dict() if after else None,
            "voc_by_sign": not nxt, "voc_by_orb": not within, "applying_within_orb": within,
            "rule": "lilly.voc.definition"}
