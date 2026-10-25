"""Layers 2-6 of the judgment: significators, relations, the course of the matter, timing and the weighed conclusion.

Method (docs/HORARY-ENGINE.md): Lilly's own order of judging (lilly.method.what_to_judge): first whether the significators
of querent and quesited come together (by aspect, translation or collection: lilly.perfection.*) and nothing cuts the
coming-together off first (prohibition, frustration, refranation); then by what or whose means (the translating or
collecting planet, described by the houses it rules), how well (dignity, reception, house positions), when (lilly.timing.*),
and the cautions. Every testimony carries its planets, houses, aspect, exact times, the rule id and the book page.

The engine's own operationalisation, stated rather than hidden: testimonies are ranked in four tiers — decisive (whether
the significators perfect), strong (conditions Lilly attaches to that perfection: reception, the aspect's own requirements,
combustion of a significator, the void Moon), moderate (the Moon's application, house positions, overall dignity) and minor —
and a lower tier never overturns a higher one; it changes the verdict only to 'conditional'. When the decisive tier is empty
or split, the verdict is 'unclear' (lilly.consider.equal_testimonies), never a forced yes/no.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict

from . import considerations, dignity, events as E, kb, questions, relations as R
from .astro import TRAD
from .houses import ANGULARITY

TIER_ORDER = {"decisive": 0, "strong": 1, "moderate": 2, "minor": 3}
GOOD_HOUSES = {1, 10, 7, 4, 11, 5, 2, 9, 3}           # not 6, 8, 12 (Lilly's p.115 debility houses)
SIGN_QUALITY = ("moveable", "fixed", "common") * 4     # Aries cardinal(moveable), Taurus fixed, Gemini common ...


@dataclass
class Testimony:
    id: str
    polarity: int               # +1 for the matter, -1 against, 0 neutral information
    tier: str                   # decisive | strong | moderate | minor
    vi: str                     # the finding, one Vietnamese sentence
    why_vi: str                 # what the rule says, in Vietnamese
    planets: list[str] = field(default_factory=list)
    houses: list[int] = field(default_factory=list)
    aspect: str | None = None
    jd: float | None = None
    rule: str = ""
    data: dict = field(default_factory=dict)

    def as_dict(self):
        return asdict(self) | {"sources": kb.cite(self.rule)}


def _vi(p: str) -> str:
    return {"sun": "Mặt Trời", "moon": "Mặt Trăng", "mercury": "Thủy tinh", "venus": "Kim tinh", "mars": "Hỏa tinh",
            "jupiter": "Mộc tinh", "saturn": "Thổ tinh"}.get(p, p)


ASPECT_VI = {"conjunction": "hội hợp", "sextile": "lục hợp", "square": "vuông góc", "trine": "tam hợp", "opposition": "xung chiếu"}


def houses_ruled(chart, p: str) -> list[int]:
    return [h for h in range(1, 13) if questions.ruler_of_house(chart, h) == p]


def _place_kind(chart, *planets) -> str:
    kinds = {ANGULARITY[chart.bodies[p].house] for p in planets}
    if kinds == {"angular"}:
        return "angular"
    if kinds == {"cadent"}:
        return "cadent"
    if kinds == {"succedent"}:
        return "succedent"
    return "+".join(sorted(kinds))


def timing(chart, cfg: R.Config, degrees: float) -> dict:
    """Lilly's measures of time for a perfecting configuration (symbolic), beside the ephemeris date of the perfection
    (astronomical fact). Neither is presented as a predicted date."""
    a, b = cfg.planets[0], cfg.planets[1]
    kinds = sorted({ANGULARITY[chart.bodies[a].house], ANGULARITY[chart.bodies[b].house]})
    if kinds == ["cadent"]:
        unit = "ngày"
    elif kinds == ["succedent"]:
        unit = "tuần"
    elif kinds == ["cadent", "succedent"]:
        unit = "tuần"
    else:
        unit = "tháng"                       # angular, or angular mixed with either (p.175: 'one angular ... months')
    q = SIGN_QUALITY[dignity.sign_of(chart.bodies[a].lon)]
    sign_unit = {"moveable": "tuần", "common": "tháng", "fixed": "năm"}[q]
    n = round(degrees, 1)
    return {
        "degrees_to_perfection": degrees,
        "house_rule": {"value": n, "unit": unit, "houses": kinds, "rule": "lilly.timing.general_house_rule",
                       "vi": f"Còn khoảng {n}° tới khi góc hợp chính xác; theo vị trí nhà ({', '.join(kinds)}) mỗi độ ứng một {unit}: khoảng {n} {unit}."},
        "sign_rule": {"value": n, "unit": sign_unit, "sign_quality": q, "rule": "lilly.timing.sign_quality",
                      "vi": f"Theo tính chất cung của {_vi(a)} ({q}) mỗi độ ứng một {sign_unit}: khoảng {n} {sign_unit}."},
        "ephemeris": {"jd": cfg.jd, "days": cfg.jd - chart.jd_ut if cfg.jd else None,
                      "vi": "Đây là thời điểm thiên văn góc hợp chính xác, không phải ngày dự báo sự việc."},
        "caveat": "Lilly tự nói đây là thước đo tượng trưng, phải 'pha nghệ thuật với lý trí' theo bản chất việc "
                  "(lilly.method.mix_art_and_reason); Thiên Bàn không đưa ra ngày cụ thể.",
    }


def _degrees_left(chart, a: str, b: str, angle: int) -> float:
    d = abs((chart.bodies[a].lon - chart.bodies[b].lon + 180) % 360 - 180)
    return abs(d - angle)


def judge(chart, frame_d: dict, school: str = "lilly") -> dict:
    ev = E.search(chart.jd_ut)
    orbs = dignity.orbs("lilly")
    pairs = R.all_pairs(chart, ev, orbs)
    sig = questions.significators(chart, frame_d)
    L1, LQ = sig["querent"]["planet"], sig["quesited"]["planet"]
    qh = frame_d["quesited_house"]
    mc = R.moon_course(chart, ev, orbs)
    cons = considerations.check(chart, frame_d, mc)
    recs = dignity.receptions(chart)
    strength = {p: dignity.strength(chart, p) for p in TRAD}
    T: list[Testimony] = []

    main = R.configurations(chart, ev, pairs, L1, LQ, orbs) if L1 != LQ else []
    moon_cfg = R.configurations(chart, ev, pairs, "moon", LQ, orbs) if "moon" not in (L1, LQ) else []
    rec = dignity.reception_between(recs, L1, LQ) if L1 != LQ else None

    # ---------- layer 3/4: does the matter come together, and does anything cut it off first?
    blockers = [c for c in main if c.kind in ("prohibition", "frustration", "abscission", "refranation")]
    first_block = min((c.jd for c in blockers if c.jd), default=None)

    for c in main:
        if c.kind == "perfection":
            asp = c.detail["aspect"]
            blocked = first_block is not None and first_block < c.jd
            ok, why, tier_pol = _aspect_conditions(chart, asp, L1, LQ, rec, mc, strength)
            T.append(Testimony(f"perfection.{asp}", -1 if blocked or not ok else +1, "decisive",
                f"{_vi(c.planets[0])} đang tiến tới góc {ASPECT_VI[asp]} với {_vi(c.planets[1])} (còn {c.detail['orb']:.2f}°)"
                + (", nhưng có sự cắt ngang trước khi góc hợp thành" if blocked else ""),
                why, c.planets, [chart.bodies[p].house for p in c.planets], asp, c.jd,
                f"lilly.perfection.{'sextile_trine' if asp in ('sextile', 'trine') else asp}",
                {"orb": c.detail["orb"], "blocked": blocked, "conditions_met": ok, **tier_pol}))
        elif c.kind == "translation":
            t, frm, to = c.planets
            received = bool([r for r in recs if r["planet"] == t and r["by"] == frm and r["dignity"] in ("house", "triplicity", "term")])
            blocked = first_block is not None and first_block < c.jd
            T.append(Testimony("translation", -1 if blocked else +1, "decisive",
                f"{_vi(t)} vừa rời {_vi(frm)} và đang tiến tới {_vi(to)}: chuyển ánh sáng (translation of light)"
                + ("" if received else " — nhưng không được chủ tinh mà nó vừa rời tiếp nhận"),
                "Lilly: khi hai chủ tinh không nối với nhau, một hành tinh rời chủ tinh này rồi tiến tới chủ tinh kia sẽ chuyển "
                "sức mạnh của bên này sang bên kia; người do hành tinh đó đại diện sẽ đưa việc tới kết quả. Lilly đòi hỏi hành "
                "tinh chuyển ánh sáng được chủ tinh nó vừa rời tiếp nhận (theo nhà, tam hợp hoặc giới hạn).",
                c.planets, [chart.bodies[p].house for p in c.planets], c.detail.get("aspect_to"), c.jd, "lilly.perfection.translation",
                {"translator": t, "translator_rules_houses": houses_ruled(chart, t), "received_by_first": received, "blocked": blocked,
                 "weak": not received}))
        elif c.kind == "collection":
            col = c.planets[0]
            they_receive = all(any(r["planet"] == col and r["by"] == s for r in recs) for s in (L1, LQ))
            T.append(Testimony("collection", +1 if they_receive else 0, "decisive" if they_receive else "moderate",
                f"Cả {_vi(L1)} và {_vi(LQ)} cùng tiến tới {_vi(col)}, hành tinh nặng hơn: thu ánh sáng (collection of light)"
                + ("" if they_receive else " — nhưng điều kiện 'cả hai cùng tiếp nhận nó' không đạt"),
                "Lilly: hai chủ tinh không nhìn nhau mà cùng chiếu tới một hành tinh nặng hơn và cả hai cùng tiếp nhận nó trong "
                "phẩm chất của mình, thì hành tinh đó gom ánh sáng và kết thúc việc; đó là một người có liên quan tới cả hai bên.",
                c.planets, [chart.bodies[p].house for p in c.planets], None, c.jd, "lilly.perfection.collection",
                {"collector": col, "collector_rules_houses": houses_ruled(chart, col), "they_receive_him": they_receive}))
        elif c.kind in ("prohibition", "frustration", "abscission"):
            T.append(Testimony(c.kind, -1, "decisive",
                {"prohibition": f"{_vi(c.planets[0])} tới {_vi(c.planets[1])} trước (góc {ASPECT_VI.get(c.detail['aspect'], '')}), cắt ngang sự gặp gỡ của hai chủ tinh",
                 "frustration": f"{_vi(c.planets[0])} kết hợp với {_vi(c.planets[1])} trước khi {_vi(c.planets[2])} kịp tới: việc bị phá giữa chừng",
                 "abscission": f"{_vi(c.planets[0])} gặp {_vi(c.planets[1])} trước khi tới {_vi(c.planets[2])}"}[c.kind],
                "Lilly: khi hai chủ tinh đang tiến tới nhau mà một hành tinh khác đến với một trong hai trước, sự gặp gỡ bị ngăn; "
                "người do hành tinh đó đại diện cản trở việc.",
                c.planets, [chart.bodies[p].house for p in c.planets], c.detail.get("aspect"), c.jd,
                {"prohibition": "lilly.prohibition", "frustration": "lilly.frustration", "abscission": "lilly.prohibition"}[c.kind],
                {"interferer_rules_houses": houses_ruled(chart, c.planets[0])}))
        elif c.kind == "refranation":
            st = c.detail["station"]
            T.append(Testimony("refranation", -1, "decisive",
                f"{_vi(L1)} và {_vi(LQ)} đang tiến tới nhau nhưng {_vi(st['planet'])} đổi chiều (đứng rồi "
                f"{'nghịch' if st['turns'] == 'retrograde' else 'thuận'} hành) trước khi góc hợp thành",
                "Lilly: hai hành tinh đang tiến tới góc hợp mà một trong hai quay lui trước khi tới thì việc không thành (refranation).",
                [L1, LQ], [chart.bodies[L1].house, chart.bodies[LQ].house], None, st["jd"], "lilly.refranation", c.detail))
        elif c.kind == "same_planet":
            T.append(Testimony("same_ruler", 0, "decisive", f"Một hành tinh ({_vi(L1)}) chủ cả nhà 1 và nhà {qh}",
                "Khi một sao chủ cả hai bên, việc được xét qua Mặt Trăng và tình trạng của chính sao đó.", [L1], [1, qh],
                rule="lilly.significator.lord_of_house"))

    ps = R.get(pairs, L1, LQ) if L1 != LQ else None
    if ps and ps.motion == "separating" and ps.within_orb:
        T.append(Testimony("separation", -1, "decisive",
            f"{_vi(L1)} và {_vi(LQ)} đang tách khỏi góc {ASPECT_VI[E.ASPECTS[ps.angle]]} (đã chính xác lúc trước)",
            "Lilly: sự tiếp cận của các chủ tinh cho thấy ý muốn của hai bên; sự tách rời thường là mất (privation): ít hy vọng thành "
            "việc mong muốn.", [L1, LQ], [], E.ASPECTS[ps.angle], ps.last_perfection_jd, "lilly.method.application_separation"))
    if L1 != LQ and not any(t.tier == "decisive" for t in T):
        T.append(Testimony("no_connection", -1, "decisive",
            f"{_vi(L1)} và {_vi(LQ)} không tiến tới góc hợp nào trong orb, không có hành tinh nào chuyển hay thu ánh sáng giữa hai bên",
            "Theo bốn cách thành sự của Lilly (hội hợp, góc hợp, chuyển ánh sáng, thu ánh sáng), không có cách nào hiện diện.",
            [L1, LQ], [], rule="lilly.method.what_to_judge"))

    # ---------- strong tier: reception, the void Moon, combustion of a significator
    if rec and (rec["a_by_b"] or rec["b_by_a"]):
        T.append(Testimony("reception", +1, "strong",
            "Hai chủ tinh có tiếp nhận: " + "; ".join(filter(None, [
                f"{_vi(L1)} đứng trong phẩm chất của {_vi(LQ)} ({', '.join(rec['a_by_b'])})" if rec["a_by_b"] else "",
                f"{_vi(LQ)} đứng trong phẩm chất của {_vi(L1)} ({', '.join(rec['b_by_a'])})" if rec["b_by_a"] else ""]))
            + (" — tiếp nhận lẫn nhau" if rec["mutual"] else ""),
            "Lilly: tiếp nhận làm việc dễ thành và là điều kiện để góc xung có thể thành; tiếp nhận lẫn nhau theo nhà được tính "
            "như phẩm chất nhà (+5).", [L1, LQ], [], rule="lilly.reception", data=rec))
    if mc["voc_by_sign"]:
        strong_sigs = all(strength[p]["essential_score"] >= 4 for p in {L1, LQ})
        T.append(Testimony("moon_voc", -1 if not strong_sigs else 0, "strong",
            "Mặt Trăng vô hành (không tạo góc hợp chính xác nào trước khi rời cung)",
            "Lilly: Trăng vô hành thì việc khó thành, trừ khi các chủ tinh chính rất mạnh.", ["moon"], [chart.bodies["moon"].house],
            rule="lilly.consider.moon_void_of_course", data={"significators_strong": strong_sigs}))
    for p, role in ((L1, "người hỏi"), (LQ, "việc được hỏi")):
        if p == "sun":
            continue
        sp = dignity.solar_phase(chart, p)
        if sp["state"] == "combust":
            T.append(Testimony(f"combust.{p}", -1, "strong", f"{_vi(p)} (chủ tinh {role}) bị Mặt Trời đốt ({sp['distance']:.1f}°)",
                "Lilly: hành tinh bị đốt mất sức, như người bị che lấp, không tự làm được việc của mình.", [p],
                [chart.bodies[p].house], rule="lilly.sun.combust"))
        elif sp["state"] == "cazimi":
            T.append(Testimony(f"cazimi.{p}", +1, "strong", f"{_vi(p)} (chủ tinh {role}) ở tim Mặt Trời (cazimi)",
                "Lilly: hành tinh ở tim Mặt Trời được tăng sức (+5).", [p], [chart.bodies[p].house], rule="lilly.sun.cazimi"))

    # ---------- moderate tier: the Moon, house positions, strength
    for c in moon_cfg:
        if c.kind == "perfection":
            asp = c.detail["aspect"]
            T.append(Testimony("moon_applies_quesited", +1 if asp != "opposition" else -1, "moderate",
                f"Mặt Trăng (đồng chủ tinh của người hỏi) tiến tới góc {ASPECT_VI[asp]} với {_vi(LQ)}",
                "Lilly: Mặt Trăng là đồng chủ tinh của người hỏi; lần tiếp cận kế tiếp của Trăng cho thấy diễn biến kế tiếp.",
                ["moon", LQ], [chart.bodies["moon"].house, chart.bodies[LQ].house], asp, c.jd, "lilly.method.moon_cosignificator"))
        if c.kind == "translation" and c.planets[0] == "moon":
            pass   # already counted when L1 is the 'from' or 'to' of a Moon translation in `main`
    if chart.bodies[LQ].house == 1 or chart.bodies[L1].house == qh:
        who = "việc tự đến với người hỏi" if chart.bodies[LQ].house == 1 else "người hỏi tự tìm tới việc"
        T.append(Testimony("house_position", +1, "minor",
            f"{_vi(LQ)} ở nhà 1" if chart.bodies[LQ].house == 1 else f"{_vi(L1)} ở nhà {qh} (nhà của việc)",
            f"Lilly: {who}; nhưng chỉ vị trí nhà thì chưa đủ, cần thêm Mặt Trăng chuyển ánh sáng (lilly.perfection.house_position).",
            [LQ if chart.bodies[LQ].house == 1 else L1], [chart.bodies[LQ].house], rule="lilly.perfection.house_position"))
    for p, role in ((L1, "người hỏi"), (LQ, "việc được hỏi")):
        s = strength[p]
        es = s["essential"]
        if es["has"] or es["debilities"] or es["peregrine"]:
            desc = (", ".join({"house": "ở nhà riêng", "exaltation": "ở thế vượng", "triplicity": "ở tam hợp", "term": "ở giới hạn riêng",
                               "face": "ở diện riêng"}[k] for k in es["has"]) or "không có phẩm chất (peregrine)")
            if es["debilities"]:
                desc += ", " + ", ".join({"detriment": "ở thế hãm", "fall": "ở thế suy"}[k] for k in es["debilities"])
            T.append(Testimony(f"essential.{p}", +1 if s["essential_score"] > 0 else -1 if s["essential_score"] < 0 else 0, "moderate",
                f"{_vi(p)} (chủ tinh {role}) {desc}: điểm phẩm chất thiết yếu {s['essential_score']:+d}",
                "Lilly: phẩm chất thiết yếu cho biết hành tinh có sức làm việc của mình hay không; nó quyết định việc thành nhanh hay "
                "chậm, dễ hay khó, không tự quyết định có thành hay không.", [p], [chart.bodies[p].house],
                rule="lilly.dignity.essential_table", data={"score": s["essential_score"]}))
        acc_house = ANGULARITY[chart.bodies[p].house]
        T.append(Testimony(f"house.{p}", +1 if acc_house == "angular" else -1 if chart.bodies[p].house in (6, 8, 12) else 0, "minor",
            f"{_vi(p)} ở nhà {chart.bodies[p].house} ({'nhà góc' if acc_house == 'angular' else 'nhà nối' if acc_house == 'succedent' else 'nhà rơi'})",
            "Lilly: nhà góc mạnh nhất, nhà nối kế đó, nhà rơi yếu; nhà 6, 8, 12 bị trừ điểm.", [p], [chart.bodies[p].house],
            rule="lilly.house.angular_succedent_cadent"))
        if p not in ("sun", "moon") and chart.bodies[p].retrograde:
            T.append(Testimony(f"retro.{p}", -1, "minor", f"{_vi(p)} (chủ tinh {role}) nghịch hành",
                "Lilly cho hành tinh nghịch hành −5 trong bảng sức mạnh tr.115.", [p], [chart.bodies[p].house], rule="lilly.motion.retrograde"))
    sn = chart.nodes["south"]
    from .houses import house_of
    sn_house = house_of(sn, chart.cusps)[0]
    if sn_house == qh:
        T.append(Testimony("cauda_in_quesited", -1, "minor", f"Kế Đô (Cauda Draconis) ở nhà {qh}, nhà của việc",
            "Lilly: Kế Đô ở nhà nào thì báo tổn hại, trở ngại cho việc của nhà đó.", [], [qh], rule="lilly.method.cauda_draconis"))

    verdict = _weigh(T, cons)
    timing_out = None
    pos = [t for t in T if t.tier == "decisive" and t.polarity > 0 and t.jd]
    if pos:
        first = min(pos, key=lambda t: t.jd)
        cfg = next(c for c in main if c.jd == first.jd)
        if cfg.kind == "perfection":
            deg = _degrees_left(chart, cfg.planets[0], cfg.planets[1], {v: k for k, v in E.ASPECTS.items()}[cfg.detail["aspect"]])
        elif cfg.kind == "translation":
            t, _, to = cfg.planets
            deg = _degrees_left(chart, t, to, {v: k for k, v in E.ASPECTS.items()}[cfg.detail["aspect_to"]])
            cfg = R.Config(cfg.kind, [t, to], cfg.jd, cfg.detail, cfg.rule)
        else:
            deg = None
        timing_out = timing(chart, cfg, deg) if deg is not None else None

    return {"frame": frame_d, "significators": sig, "considerations": [c.as_dict() for c in cons],
            "testimonies": sorted([t.as_dict() for t in T], key=lambda t: (TIER_ORDER[t["tier"]], -abs(t["polarity"]))),
            "verdict": verdict, "timing": timing_out, "moon_course": mc,
            "configurations": {"main": [c.as_dict() for c in main], "moon": [c.as_dict() for c in moon_cfg]},
            "pairs": {f"{a}-{b}": v.as_dict() for (a, b), v in pairs.items()},
            "strength": strength, "receptions": recs, "orbs": orbs,
            "timeline": _timeline(chart, ev, {L1, LQ, "moon"}),
            "events_residual_arcsec": ev["max_residual_arcsec"]}


def _aspect_conditions(chart, asp: str, L1: str, LQ: str, rec, mc, strength) -> tuple[bool, str, dict]:
    hs = {p: chart.bodies[p].house for p in (L1, LQ)}
    dign = {p: bool(strength[p]["essential"]["has"]) for p in (L1, LQ)}
    if asp == "conjunction":
        kind = _place_kind(chart, L1, LQ)
        speed = {"angular": "không trở ngại", "succedent": "thành nhưng không nhanh", "cadent": "rất mất thời gian, nhiều khó khăn"}
        return True, ("Lilly: chủ Mệnh và chủ việc hội hợp, không bị ngăn hay quay lui trước khi hợp, thì việc thành; ở nhà góc thì "
                      "không trở ngại, nhà nối thì chậm hơn, nhà rơi thì rất mất thời gian và vất vả. Ở đây: "
                      + speed.get(kind, "các chủ tinh ở loại nhà khác nhau") + "."), {"place": kind}
    if asp in ("sextile", "trine"):
        good = all(h in GOOD_HOUSES for h in hs.values()) and all(dign.values())
        return True, ("Lilly: các chủ tinh tiến tới lục hợp hoặc tam hợp từ nhà tốt, nơi có phẩm chất, không bị góc xấu chen vào, "
                      "thì việc thành." + ("" if good else " Ở đây điều kiện 'nhà tốt và có phẩm chất' chưa trọn, nên việc thành kém trọn vẹn.")), \
            {"conditions_full": good}
    if asp == "square":
        ok = all(dign.values()) and all(h in GOOD_HOUSES for h in hs.values())
        return ok, ("Lilly: góc vuông cũng thành việc nếu mỗi hành tinh có phẩm chất ở độ của mình và tiến tới từ nhà thích hợp; "
                    "nếu không thì không." + (" Điều kiện đạt." if ok else " Điều kiện không đạt.")), {"conditions_full": ok}
    if asp == "opposition":
        moon_ok = bool(mc["last_separation"] and LQ in (mc["last_separation"]["a"], mc["last_separation"]["b"])) and any(
            L1 in (p["a"], p["b"]) for p in mc["perfections_in_sign"][:1])
        ok = bool(rec and rec["mutual"] and "house" in rec["a_by_b"] and "house" in rec["b_by_a"]) and moon_ok
        return ok, ("Lilly: góc xung đôi khi thành việc, nhưng chỉ khi có tiếp nhận lẫn nhau theo nhà, từ nhà thân thiện và Mặt "
                    "Trăng rời chủ việc để tiến tới chủ Mệnh; và ông hiếm thấy việc thành theo cách này mà người hỏi không thà "
                    "rằng nó đừng thành." + (" Các điều kiện đạt: việc có thể thành nhưng kèm tranh chấp hay hối tiếc." if ok
                                              else " Các điều kiện không đạt.")), {"regret": ok}
    return False, "", {}


def _weigh(T: list[Testimony], cons) -> dict:
    dec = [t for t in T if t.tier == "decisive"]
    pos = [t for t in dec if t.polarity > 0]
    neg = [t for t in dec if t.polarity < 0]
    first_pos = min((t.jd for t in pos if t.jd), default=None)
    first_neg = min((t.jd for t in neg if t.jd and t.id not in ("separation",)), default=None)
    strong = [t for t in T if t.tier == "strong"]
    s_neg = [t for t in strong if t.polarity < 0]
    s_pos = [t for t in strong if t.polarity > 0]
    reasons = []
    if pos and (first_neg is None or (first_pos is not None and first_pos < first_neg)):
        cond = [t for t in pos if t.data.get("weak") or t.data.get("regret") or t.data.get("conditions_full") is False]
        if s_neg or cond:
            label, vi = "conditional", "Thuận nhưng có điều kiện"
            reasons.append("Có cách thành sự, nhưng kèm điều kiện hoặc trở ngại ở tầng mạnh: " +
                           "; ".join(t.vi for t in (s_neg + cond)))
        else:
            label, vi = "favourable", "Thuận"
            reasons.append("Có cách thành sự không bị cắt ngang: " + "; ".join(t.vi for t in pos))
    elif neg and not pos:
        label, vi = "unfavourable", "Không thuận"
        reasons.append("Không có cách thành sự, hoặc sự gặp gỡ bị cắt ngang: " + "; ".join(t.vi for t in neg))
    elif pos and neg:
        label, vi = "unfavourable", "Không thuận"
        reasons.append("Sự cắt ngang xảy ra trước khi việc kịp thành: " + "; ".join(t.vi for t in neg if t.jd == first_neg))
    else:
        label, vi = "unclear", "Chưa rõ"
        reasons.append("Không có chứng cứ quyết định ở bên nào (Lilly: khi chứng cứ cân bằng thì hoãn luận).")
    caution = [c for c in cons if c.applies and c.severity in ("caution", "strong_caution")]
    strong_c = [c for c in caution if c.severity == "strong_caution"]
    confidence = "low" if len(strong_c) >= 1 or len(caution) >= 3 else "medium" if caution else "high"
    if label in ("favourable", "conditional") and len(s_neg) > len(s_pos) + 1:
        label, vi = "unclear", "Chưa rõ"
        reasons.append("Có cách thành sự nhưng nhiều chứng cứ mạnh chống lại, nên không kết luận.")
    return {"label": label, "vi": vi, "confidence": confidence, "reasons": reasons,
            "cautions": [c.id for c in caution],
            "method": "Thứ tự xét theo Lilly (lilly.method.what_to_judge); tầng chứng cứ là cách vận hành của Thiên Bàn (docs/HORARY-ENGINE.md)."}


def _timeline(chart, ev: dict, planets: set[str]) -> list[dict]:
    """Events involving the significators and the Moon from 3 days before to 60 days after the question (Aspect Timeline)."""
    t0 = chart.jd_ut
    out = []
    for p in ev["perfections"]:
        if t0 - 3 <= p.jd <= t0 + 60 and ({p.a, p.b} & planets):
            out.append(p.as_dict())
    for s in ev["stations"]:
        if t0 - 3 <= s.jd <= t0 + 120 and s.planet in planets:
            out.append(s.as_dict())
    for g in ev["ingresses"]:
        if t0 - 3 <= g.jd <= t0 + 60 and g.planet in planets:
            out.append(g.as_dict())
    out.sort(key=lambda e: e["jd"])
    return out
