"""Derived facts for the readings, each computed the way its own school computes it.

Lilly (Christian Astrology): his dignity table (p.104), essential and accidental points (pp.101-103, 115), Regiomontanus
houses, moieties of orbs (p.107), Lord of the Geniture (p.531), complexion (pp.532-534), significator of manners (pp.535-536).
Ptolemy (Tetrabiblos): five modes of domination (III.2) with his own triplicities and terms, places of 30 degrees starting
5 degrees above the horizon (III.10), ruler of the soul (III.13), lord of action (IV.4), ruler of the Lot (IV.2).
Valens (Anthologies): whole-sign places, the sect light's triangle lords and their grading by place (II.2).
Where a book leaves a threshold open, the choice is Thiên Bàn's and is named as such in `operational`.
"""
from __future__ import annotations

import itertools
import math
from functools import cached_property

from .. import dignity, ephemeris as E, houses as H, kb
from .. import stars as STARS
from ..zodiac import ELEMENT, MODALITY, SIGNS, angdiff, deg_in_sign, sign_distance, sign_index

CLASSICAL = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn")
FIVE = ("mercury", "venus", "mars", "jupiter", "saturn")
BENEFICS, MALEFICS = ("jupiter", "venus"), ("saturn", "mars")
QUALITY = {"fire": ("hot", "dry"), "earth": ("cold", "dry"), "air": ("hot", "moist"), "water": ("cold", "moist")}
# Lilly p.533 'The Quality of the Planets' (oriental, occidental)
PLANET_QUALITY = {"saturn": (("cold", "moist"), ("dry",)), "jupiter": (("hot", "moist"), ("moist",)), "mars": (("hot", "dry"), ("dry",)),
                  "venus": (("hot", "moist"), ("moist",)), "mercury": (("hot",), ("dry",))}
LILLY_MEAN = {"saturn": 2 / 60 + 1 / 3600, "jupiter": 4 / 60 + 59 / 3600, "mars": 31 / 60 + 27 / 3600, "sun": 59 / 60 + 8 / 3600,
              "venus": 59 / 60 + 8 / 3600, "mercury": 59 / 60 + 8 / 3600, "moon": 13 + 10 / 60 + 36 / 3600}       # pp.57-80
PTOLEMAIC_ASPECTS = {0: "conjunction", 2: "sextile", 3: "square", 4: "trine", 6: "opposition"}
STRONG, WEAK = 10, 0          # see OPERATIONAL['well_dignified']
ESS_VI = {"domicile": "ở nhà của mình", "exaltation": "ở cung tôn vinh", "triplicity": "làm chủ nhóm nguyên tố", "term": "ở giới hạn của mình",
          "face": "ở diện của mình", "detriment": "ở cung tổn hại", "fall": "ở cung suy hãm", "peregrine": "lạc chỗ"}
_ACC = {"retrograde": "nghịch hành", "direct": "đi thuận", "swift": "đi nhanh", "slow": "đi chậm", "superiors_oriental": "mọc trước Mặt Trời",
        "superiors_occidental": "lặn sau Mặt Trời", "inferiors_occidental": "đi sau Mặt Trời", "inferiors_oriental": "đi trước Mặt Trời",
        "moon_increasing_or_occidental": "trăng đang tròn dần", "moon_decreasing": "trăng đang khuyết", "cazimi": "nằm ngay tim Mặt Trời",
        "combust": "bị Mặt Trời đốt", "under_beams": "dưới tia Mặt Trời", "free_from_combustion_and_beams": "không bị Mặt Trời che",
        "besieged": "bị Sao Thổ và Sao Hỏa vây", "partile_conj_north_node": "trùng La Hầu", "partile_conj_south_node": "trùng Kế Đô",
        "conj_cor_leonis": "sát Cor Leonis", "conj_spica": "sát Spica", "conj_caput_algol": "sát Caput Algol"}


def ACC_VI(k: str) -> str:
    if k.startswith("house_"):
        return f"ở Nhà {k[6:]}"
    base = k.split(":")[0]
    if base.startswith("partile_"):
        return "chiếu đúng độ với " + ("cát tinh" if "jupiter_venus" in base else "hung tinh")
    return _ACC.get(base, base)


SYSTEM_VI = {"lilly": "theo cách chia của Lilly", "ws": "tính trọn cung", "ptolemy": "theo chỗ 30° của Ptolemy",
             "modern": "theo hệ nhà đang chọn"}
OPERATIONAL = {
    "well_dignified": "Thiên Bàn gọi một hành tinh là 'đắc thế' (mạnh) khi tổng điểm theo bảng Lilly, gồm điểm bản chất (tr.104, tr.101-103) "
                      "và điểm ngẫu nhiên (nhà, chiều đi, tốc độ, khoảng cách với Mặt Trời, góc chiếu đúng độ, định tinh; tr.115), từ +10 trở lên; "
                      "'thất thế' (yếu) khi từ 0 trở xuống; ở giữa là mức vừa. Lilly không đặt ngưỡng số và không nói hai phần cộng thế nào (tr.116); "
                      "Thiên Bàn cộng thẳng như Lilly làm khi chọn sao chủ lá số (tr.531). Mốc giữa đặt quanh +5 vì một sao không có gì đặc biệt "
                      "(không phẩm vị, đi thuận, không bị Mặt Trời che) đã được khoảng chừng ấy điểm theo bảng tr.115.",
    "partile": "partile = cùng số độ trong cung (ví dụ 9° Bạch Dương và 9° Sư Tử), theo ví dụ của Lilly tr.107.",
    "besieged": "'bị vây' = Sao Thổ và Sao Hỏa ở hai bên trong cùng một cung; Lilly không định nghĩa thêm ở tr.115.",
    "morning_appearance": "'mới mọc buổi sáng' (Ptolemy IV.4) được hiểu là hành tinh đi trước Mặt Trời và đã cách xa ít nhất 15°; "
                          "Ptolemy không cho con số, 15° là mức Thiên Bàn chọn.",
    "polar_houses": "Trong vòng cực, Placidus và Regiomontanus có lúc không cho mười hai nhà theo đúng thứ tự; khi đó Thiên Bàn chia nhà theo "
                    "Porphyry (chia đều mỗi góc phần tư) cho cả bánh xe lẫn phần của Lilly.",
    "lilly_houses": "Nhà theo Lilly = cách chia Regiomontanus, và theo lời Lilly (tr.33) một hành tinh cách đỉnh nhà không quá 5° "
                    "được tính vào nhà của đỉnh gần nó nhất; vì thế số nhà theo Lilly có thể khác số nhà trên bánh xe (Placidus).",
    "ptolemy_place": "'chỗ' theo Ptolemy III.10: mỗi chỗ 30°, chỗ thứ nhất bắt đầu 5° phía trên điểm Mọc.",
    "fixed_stars": "'đồng độ với định tinh' = cách định tinh không quá 5° theo kinh độ hoàng đạo, con số Lilly cho ở tr.616 (và tr.115 với Caput Algol); "
                   "tr.115 không ghi khoảng cách cho Cor Leonis và Spica, Thiên Bàn dùng cùng 5°. Lilly in vị trí định tinh của năm 1647; "
                   "do tuế sai, định tinh nay đã dịch thêm khoảng 5°, nên Thiên Bàn tính vị trí của chính ngày sinh (dữ liệu Hipparcos).",
}


def _q(planet: str, oriental: bool) -> tuple[str, ...]:
    return PLANET_QUALITY[planet][0 if oriental else 1]


class Facts:
    def __init__(self, chart: dict, gender: str | None = None):
        self.c = chart
        self.gender = gender
        self.time_known = "angles" in chart
        self.is_day = chart.get("sect", {}).get("is_day")
        self.b = chart["bodies"]
        self.lon = {n: v["lon"] for n, v in {**chart["bodies"], **chart["points"], **chart.get("angles", {}),
                                               **{k: v for k, v in chart.get("lots", {}).items() if isinstance(v, dict)}}.items()
                    if isinstance(v, dict) and "lon" in v}

    # ---------------------------------------------------------------- houses of each school
    @cached_property
    def regio(self) -> list[float] | None:
        if not self.time_known:
            return None
        t = E.time_jd_ut(self.c["time"]["jd_ut"])
        _, eps, _ = E.sidereal_and_obliquity(t)
        try:
            return H.cusps("regiomontanus", self.c["angles"]["armc"], eps, self.c["input"]["lat"])
        except H.PolarHouses:          # beyond the polar circles: Porphyry, as the chart does for Placidus (named in OPERATIONAL)
            self.regio_fallback = True
            return H.cusps("porphyry", self.c["angles"]["armc"], eps, self.c["input"]["lat"])

    def house_lilly(self, name: str) -> int | None:
        """Regiomontanus with Lilly's five-degree rule (p.33): the house Lilly himself would read the planet in."""
        return H.house_of_lilly(self.lon[name], self.regio) if self.regio else None

    def house_modern(self, name: str) -> int | None:
        """The house system chosen for the chart (Placidus by default, the tables Alan Leo worked with)."""
        if not self.time_known:
            return None
        return H.house_of(self.lon[name], [x["lon"] for x in self.c["houses"]["cusps"][self.c["houses"]["system"]]])

    def house(self, school: str, name: str) -> int | None:
        return {"traditional": self.house_lilly, "hellenistic": self.place_ws, "ptolemy": self.place_ptolemy}.get(school, self.house_modern)(name)

    def house_note(self, school: str, name: str, inner: bool = False) -> str:
        """' (Nhà 1 nếu chia theo Placidus, Nhà 2 tính trọn cung)' the first time a planet whose house differs between the
        reading's house systems is placed by a school; '' otherwise. Keeps one planet from carrying two numbers unexplained."""
        if not self.time_known or name not in self.lon:
            return ""
        told = self.__dict__.setdefault("_house_note", set())
        mine = self.house(school, name)
        others = {"traditional": ("lilly", self.house_lilly(name)), "hellenistic": ("ws", self.place_ws(name)),
                  "modern": ("modern", self.house_modern(name))}
        own_key = {"traditional": "lilly", "hellenistic": "ws", "ptolemy": None}.get(school, "modern")
        diff = [(k, n) for k, n in others.values() if k != own_key and n is not None and n != mine]
        if not diff or name in told:
            return ""
        told.add(name)
        label = lambda k: self.system_vi("modern") if k == "modern" else SYSTEM_VI[k]
        body = ", ".join(f"Nhà {n} {label(k)}" for k, n in diff)
        return f"; {body}" if inner else f" ({body})"

    def system_vi(self, school: str) -> str:
        return {"traditional": SYSTEM_VI["lilly"], "hellenistic": SYSTEM_VI["ws"], "ptolemy": SYSTEM_VI["ptolemy"]}.get(
            school, f"theo {self.c['houses']['system'].replace('_', ' ').title()}" if self.time_known else "")

    def place_ws(self, name_or_lon) -> int | None:
        if not self.time_known:
            return None
        lon = self.lon[name_or_lon] if isinstance(name_or_lon, str) else name_or_lon
        return sign_distance(self.lon["asc"], lon) + 1

    def place_ptolemy(self, name: str) -> int | None:
        if not self.time_known:
            return None
        return int(((self.lon[name] - (self.lon["asc"] - 5.0)) % 360.0) // 30.0) + 1

    def cusp_margin(self, school: str, name: str) -> float | None:
        """Degrees between the point and the nearest edge of the house it is read in by `school` (Lilly: cusp ± his 5 degrees,
        whole sign: the sign edge, Ptolemy: the 30-degree places). A birth time off by about 4 minutes moves the angles by about
        one degree, so this says how much the house reading leans on the exact time."""
        if not self.time_known or name not in self.lon:
            return None
        lon = self.lon[name]
        if school == "hellenistic":
            edges = [math.floor(self.lon["asc"] / 30.0) * 30.0 + 30.0 * i for i in range(12)]
            asc_m = min(deg_in_sign(self.lon["asc"]), 30 - deg_in_sign(self.lon["asc"]))
            return round(min(asc_m, min(abs(angdiff(lon, e)) for e in edges)), 2)
        if school == "ptolemy":
            edges = [self.lon["asc"] - 5.0 + 30.0 * i for i in range(12)]
        elif school == "traditional" and self.regio:
            edges = [c - 5.0 for c in self.regio]
        else:
            edges = [x["lon"] for x in self.c["houses"]["cusps"][self.c["houses"]["system"]]]
        return round(min(abs(angdiff(lon, e)) for e in edges), 2)

    def valens_grade(self, p: str) -> str | None:
        """II.2 grading of a place counted by whole sign: at an angle, following one, or preceding one."""
        pl = self.place_ws(p)
        return None if pl is None else "angular" if pl in (1, 4, 7, 10) else "succedent" if pl in (2, 5, 8, 11) else "cadent"

    def lilly_honour_grade(self, p: str) -> tuple[str, str]:
        """pp.615-617 as read for Sự nghiệp: ('high' domicile/exaltation, 'mid' some dignity, 'low' none) and angularity in Lilly's houses."""
        e = self.lilly_essential(p)
        h = self.house_lilly(p)
        g = "high" if set(e["has"]) & {"domicile", "exaltation"} else "mid" if e["has"] else "low"
        return g, "angular" if h in (1, 4, 7, 10) else "succedent" if h in (2, 5, 11) else "cadent"      # p.615 counts the 8th with the cadents

    def ptolemy_strong(self, p: str) -> bool:
        """IV.2 'in power': in its own (familiar) place, or angular / in the 11th by Ptolemy's places."""
        return self.honourable(p) or self.place_ptolemy(p) in (1, 10, 7, 4, 11)

    # ---------------------------------------------------------------- Lilly's dignities and points
    def lilly_essential(self, p: str, lon: float | None = None) -> dict:
        return dignity.lilly_essential(p, self.lon[p] if lon is None else lon, self.is_day)

    def partile(self, a: str, b: str) -> str | None:
        """Lilly's partile aspect between two points: same degree number, Ptolemaic sign distance."""
        la, lb = self.lon[a], self.lon[b]
        if int(deg_in_sign(la)) != int(deg_in_sign(lb)):
            return None
        n = sign_distance(la, lb)
        return PTOLEMAIC_ASPECTS.get(min(n, 12 - n))

    def platick(self, a: str, b: str) -> str | None:
        """Aspect within the sum of the two moieties (half orbs) of Lilly p.107."""
        orbs = kb.aspects()["orb_schemes"]["lilly"]["planet_orbs"]
        if a not in orbs or b not in orbs:
            return None
        sep = abs(angdiff(self.lon[a], self.lon[b]))
        lim = (orbs[a] + orbs[b]) / 2
        for ang, name in ((0, "conjunction"), (60, "sextile"), (90, "square"), (120, "trine"), (180, "opposition")):
            if abs(sep - ang) <= lim:
                return name
        return None

    def lilly_accidental(self, p: str) -> list[tuple[str, int]]:
        """Lines of Lilly's p.115 table that apply to planet p (fixed stars within OPERATIONAL['fixed_stars']). Without a birth time
        the house lines are left out; motion and the distance from the Sun hardly change within the day (the Moon's partile
        aspects can, so they are left out too)."""
        rows = {r["key"]: r["points"] for r in kb.dignities()["accidental"]["rows"]}
        out: list[tuple[str, int]] = []
        h = self.house_lilly(p) if self.time_known else None
        if h:
            out.append((f"house_{h}", kb.dignities()["accidental"]["house_points"][str(h)]))
        cond = self.c["conditions"][p]
        if p not in ("sun", "moon"):
            out.append(("retrograde", rows["retrograde"]) if self.b[p]["retrograde"] else ("direct", rows["direct"]))
        spd = abs(self.b[p]["speed"])
        out.append(("swift", rows["swift"]) if spd > LILLY_MEAN[p] else ("slow", rows["slow"]))
        if p != "sun":
            oriental = cond["solar"]["oriental"]
            if p in ("saturn", "jupiter", "mars"):
                out.append(("superiors_oriental", rows["superiors_oriental"]) if oriental else ("superiors_occidental", rows["superiors_occidental"]))
            elif p in ("venus", "mercury"):
                out.append(("inferiors_occidental", rows["inferiors_occidental"]) if not oriental else ("inferiors_oriental", rows["inferiors_oriental"]))
            else:
                waxing = self.c["moon_phase"]["waxing"]
                out.append(("moon_increasing_or_occidental", rows["moon_increasing_or_occidental"]) if waxing else ("moon_decreasing", rows["moon_decreasing"]))
            phase = cond["solar"]["phase"]
            if phase == "cazimi":
                out.append(("cazimi", rows["cazimi"]))
            elif phase == "combust":
                out.append(("combust", rows["combust"]))
            elif phase == "under_beams":
                out.append(("under_beams", rows["under_beams"]))
            else:
                out.append(("free_from_combustion_and_beams", rows["free_from_combustion_and_beams"]))
        for o in BENEFICS:
            if o != p:
                a = self.partile(p, o)
                key = {"conjunction": "partile_conj_jupiter_venus", "trine": "partile_trine_jupiter_venus", "sextile": "partile_sextile_jupiter_venus"}.get(a)
                if key:
                    out.append((f"{key}:{o}", rows[key]))
        for o in MALEFICS:
            if o != p:
                a = self.partile(p, o)
                key = {"conjunction": "partile_conj_saturn_mars", "opposition": "partile_opposition_saturn_mars", "square": "partile_square_saturn_mars"}.get(a)
                if key:
                    out.append((f"{key}:{o}", rows[key]))
        if int(deg_in_sign(self.lon[p])) == int(deg_in_sign(self.lon["north_node"])) and self.b[p]["sign"] == self.c["points"]["north_node"]["sign"]:
            out.append(("partile_conj_north_node", rows["partile_conj_north_node"]))
        if int(deg_in_sign(self.lon[p])) == int(deg_in_sign(self.lon["south_node"])) and self.b[p]["sign"] == self.c["points"]["south_node"]["sign"]:
            out.append(("partile_conj_south_node", rows["partile_conj_south_node"]))
        if p not in MALEFICS and self.b["saturn"]["sign"] == self.b["mars"]["sign"] == self.b[p]["sign"]:
            lo, hi = sorted((self.lon["saturn"], self.lon["mars"]))
            if lo < self.lon[p] < hi and hi - lo < 30:
                out.append(("besieged", rows["besieged"]))
        for star in self.stars_near(p, STARS.LILLY_115):
            out.append((STARS.LILLY_115[star], rows[STARS.LILLY_115[star]]))
        return out

    def stars_near(self, p: str, stars) -> list[str]:
        """The stars (keys of chart['fixed_stars']) within Lilly's 5° of point p, nearest first."""
        fs = self.c.get("fixed_stars") or {}
        near = [(abs(angdiff(self.lon[p], fs[k]["lon"])), k) for k in stars if k in fs and p in self.lon]
        return [k for d, k in sorted(near) if d <= STARS.ORB]

    def lilly_total(self, p: str) -> dict:
        ess = self.lilly_essential(p)
        acc = self.lilly_accidental(p)
        return {"essential": ess, "accidental": acc, "accidental_score": sum(v for _, v in acc), "total": ess["score"] + sum(v for _, v in acc)}

    def lilly_state(self, p: str) -> str:
        """'well' / 'ill' / 'mixed' by Lilly's essential and accidental points together (see OPERATIONAL['well_dignified'])."""
        s = self.lilly_total(p)["total"]
        return "well" if s >= STRONG else "ill" if s <= WEAK else "mixed"

    def strength_why(self, p: str, n: int = 3) -> str:
        """'+14: ở cung tôn vinh, ở Nhà 10, đi thuận': the total and the lines that weigh most, for the reader to check."""
        t = self.lilly_total(p)
        e = t["essential"]
        sc = kb.dignities()["scores"]["essential"]
        items = [(sc[k], ESS_VI[k]) for k in e["has"] + e["debilities"]] + ([(sc["peregrine"], ESS_VI["peregrine"])] if e["peregrine"] else [])
        items += [(v, ACC_VI(k)) for k, v in t["accidental"] if v]
        common = {"đi thuận", "không bị Mặt Trời che"}          # what most planets get: named only when nothing else weighs
        items.sort(key=lambda x: (x[1] in common, -abs(x[0])))
        return f"tổng {t['total']:+d} điểm, trong đó có ".replace("-", "−") + ", ".join(f"{x} {v:+d}".replace("-", "−") for v, x in items[:n])

    @cached_property
    def lord_of_geniture(self) -> dict | None:
        """Lilly p.531: the planet with most essential and accidental dignities (ties share the rule)."""
        if not self.time_known:
            return None
        tot = {p: self.lilly_total(p)["total"] for p in CLASSICAL}
        best = max(tot.values())
        lords = [p for p, v in tot.items() if v == best]
        return {"lords": lords, "totals": tot}

    # ---------------------------------------------------------------- Lilly: complexion and manners
    def lilly_complexion(self) -> dict | None:
        """Testimonies of hot/cold/moist/dry from Lilly's five significators (pp.532-534)."""
        if not self.time_known:
            return None
        tally = {"hot": 0, "cold": 0, "moist": 0, "dry": 0}
        lines: list[dict] = []

        def add(label: str, quals: tuple[str, ...], weight: int = 1):
            for q in quals:
                tally[q] += weight
            lines.append({"from": label, "qualities": list(quals), "weight": weight})

        asc_sign = SIGNS[sign_index(self.lon["asc"])]
        add(f"sign:{asc_sign}", QUALITY[ELEMENT[sign_index(self.lon["asc"])]])
        lord = dignity.domicile_lord(asc_sign)
        lg = self.lord_of_geniture
        triple = lg and lord in lg["lords"]
        for name, w in [(lord, 3 if triple else 1)]:
            add(f"lord_asc:{name}", self._planet_quality(name), w)
            add(f"lord_asc_sign:{self.b[name]['sign']}", QUALITY[ELEMENT[sign_index(self.lon[name])]], w)
        in_first = [p for p in CLASSICAL if self.house_lilly(p) == 1]
        for p in in_first:
            add(f"in_asc:{p}", self._planet_quality(p), 2 if p == "moon" else 1)
        for node, as_ in (("north_node", ("jupiter",)), ("south_node", ("saturn", "mars"))):
            if self.house_lilly(node) == 1:
                for a in as_:
                    add(f"in_asc:{node}~{a}", self._planet_quality(a))
        for p in CLASSICAL:
            if p not in in_first and p != "moon":
                if self._partile_to_point(p, "asc"):
                    add(f"partile_asc:{p}", self._planet_quality(p))
        add("moon", self._planet_quality("moon"), 2 if "moon" in in_first else 1)
        add(f"moon_sign:{self.b['moon']['sign']}", QUALITY[ELEMENT[sign_index(self.lon["moon"])]])
        for p in CLASSICAL:
            if p != "moon" and self.platick(p, "moon"):
                add(f"aspects_moon:{p}", self._planet_quality(p))
        add(f"sun_quarter:{self.b['sun']['sign']}", self._sun_quality())
        if lg and len(lg["lords"]) == 1 and not triple:
            g = lg["lords"][0]
            add(f"lord_geniture:{g}", self._planet_quality(g))
        hot = tally["hot"] - tally["cold"]
        moist = tally["moist"] - tally["dry"]
        kind = None
        if hot and moist:
            kind = {(True, True): "sanguine", (True, False): "choleric", (False, False): "melancholic", (False, True): "phlegmatic"}[(hot > 0, moist > 0)]
        malefic_mix = [m for m in MALEFICS for target in ("asc", "moon") if m != target and self._evil_aspect(m, target)]
        return {"tally": tally, "lines": lines, "temperament": kind, "hot_minus_cold": hot, "moist_minus_dry": moist,
                "lord_counted_thrice": bool(triple), "malefic_mixture": sorted(set(malefic_mix))}

    def _planet_quality(self, p: str) -> tuple[str, ...]:
        if p == "sun":
            return self._sun_quality()
        if p == "moon":
            el = self.c["moon_phase"]["elongation"]
            return (("hot", "moist"), ("hot", "dry"), ("cold", "dry"), ("cold", "moist"))[int(el // 90) % 4]     # Lilly p.533
        return _q(p, self.c["conditions"][p]["solar"]["oriental"])

    def _sun_quality(self) -> tuple[str, ...]:
        return (("hot", "moist"), ("hot", "dry"), ("cold", "dry"), ("cold", "moist"))[sign_index(self.lon["sun"]) // 3]   # Lilly p.533

    def _partile_to_point(self, p: str, point: str) -> str | None:
        la, lb = self.lon[p], self.lon[point]
        if int(deg_in_sign(la)) != int(deg_in_sign(lb)):
            return None
        n = sign_distance(la, lb)
        return PTOLEMAIC_ASPECTS.get(min(n, 12 - n))

    def _evil_aspect(self, m: str, target: str) -> bool:
        orbs = kb.aspects()["orb_schemes"]["lilly"]["planet_orbs"]
        sep = abs(angdiff(self.lon[m], self.lon[target]))
        lim = (orbs[m] + orbs.get(target, orbs[m])) / 2 if target in orbs else orbs[m] / 2
        return any(abs(sep - a) <= lim for a in (90, 180))

    def manners_significator(self) -> dict | None:
        """Lilly pp.535-536: planet in the ascending sign; else joined to the Moon or Mercury; else the Lord of the Ascendant;
        else partile to the Moon and Mercury; else the planet with most essential dignity in their places."""
        if not self.time_known:
            return None
        asc_sign = SIGNS[sign_index(self.lon["asc"])]
        rising = [p for p in CLASSICAL if self.b[p]["sign"] == asc_sign]
        if rising:
            return {"step": 1, "planets": rising, "why": "in_ascending_sign"}
        joined = sorted(((min(abs(angdiff(self.lon[p], self.lon[x])) for x in ("moon", "mercury")
                               if self.b[p]["sign"] == self.b[x]["sign"] and self.platick(p, x) == "conjunction"), p)
                          for p in CLASSICAL if p not in ("moon", "mercury")
                          and any(self.b[p]["sign"] == self.b[x]["sign"] and self.platick(p, x) == "conjunction" for x in ("moon", "mercury"))))
        if joined:       # the nearest one leads; a second only when it is almost as close (within 1 degree more)
            lead = [p for d, p in joined if d <= joined[0][0] + 1.0][:2]
            return {"step": 2, "planets": lead, "why": "joined_moon_or_mercury"}
        lord = dignity.domicile_lord(asc_sign)
        return {"step": 3, "planets": [lord], "why": "lord_of_ascendant", "dispositor": dignity.domicile_lord(self.b[lord]["sign"])}

    def lilly_profession(self) -> dict | None:
        """Lilly pp.624-625: of Mars, Venus and Mercury, the one that (1) is in the 10th, 1st or 7th in its own dignities and not
        combust; else (2) rules the MC sign and is in essential dignity; else (3) is in partile aspect to the Moon; else (4) aspects
        the Moon within orbs; else (5) rises before the Sun."""
        if not self.time_known:
            return None
        three = ("mars", "venus", "mercury")
        mc_lord = dignity.domicile_lord(self.c["angles"]["mc"]["sign"])
        ess = {p: self.lilly_essential(p) for p in three}
        free = {p: self.c["conditions"][p]["solar"]["phase"] not in ("combust", "under_beams") for p in three}
        tests = [
            [p for p in three if self.house_lilly(p) in (10, 1, 7) and ess[p]["has"] and free[p]],
            [p for p in three if p == mc_lord and ess[p]["has"]],
            [p for p in three if self.partile(p, "moon")],
            [p for p in three if self.platick(p, "moon")],
            [p for p in three if self.c["conditions"][p]["solar"]["oriental"]],
        ]
        for i, found in enumerate(tests, 1):
            if found:
                sig = found[0] if len(found) == 1 else max(found, key=lambda x: self.lilly_total(x)["total"])
                partner = next((o for o in three if o != sig and self.platick(sig, o) in ("conjunction", "sextile", "trine")), None)
                mods = [o for o in ("jupiter", "saturn", "sun", "moon") if self.platick(sig, o)]
                e = ess[sig]
                strong = bool(e["has"]) and not any(self.partile(sig, m) for m in MALEFICS) and self.house_lilly(sig) in (1, 4, 7, 10) \
                    and self.c["conditions"][sig]["solar"]["oriental"]
                weak = (not e["has"]) or self.house_lilly(sig) in (3, 6, 9, 12)
                return {"test": i, "candidates": found, "significator": sig, "partner": partner, "modifiers": mods,
                        "skilled": i <= 2, "fame": "strong" if strong else "weak" if weak else "middle"}
        return {"test": None, "candidates": [], "significator": None}

    # ---------------------------------------------------------------- Ptolemy
    def ptolemy_dominators(self, lon: float) -> dict[str, list[str]]:
        """III.2: which planets hold the place at `lon` by domicile, exaltation, triplicity, term and by phase/aspect."""
        sign = SIGNS[sign_index(lon)]
        claims: dict[str, list[str]] = {p: [] for p in CLASSICAL}
        claims[dignity.domicile_lord(sign)].append("domicile")
        if dignity.exaltation_lord(sign):
            claims[dignity.exaltation_lord(sign)].append("exaltation")
        trip = kb.dignities()["triplicity"]["ptolemaic"]["table"][ELEMENT[sign_index(lon)]]
        if self.is_day is not None:
            claims[trip[0 if self.is_day else 1]].append("triplicity")
        if ELEMENT[sign_index(lon)] == "water" and self.is_day is not None:      # I.18: Venus by day, Moon by night co-rule water
            claims["venus" if self.is_day else "moon"].append("triplicity_co")
        t = dignity.term_lord(lon, "ptolemaic")
        if t:
            claims[t].append("term")
        for p in CLASSICAL:
            n = sign_distance(self.lon[p], lon)
            if min(n, 12 - n) in (2, 3, 4, 6) or n == 0:
                claims[p].append("aspect")
        return {p: v for p, v in claims.items() if v}

    def soul_ruler(self) -> dict:
        """III.13: the planet (of the five) that dominates both Mercury and the Moon."""
        dm, dl = self.ptolemy_dominators(self.lon["mercury"]), self.ptolemy_dominators(self.lon["moon"])
        score = {p: len(dm.get(p, [])) + len(dl.get(p, [])) for p in FIVE}
        both = {p: s for p, s in score.items() if dm.get(p) and dl.get(p)}
        pool = both or score
        best = max(pool.values())
        rulers = [p for p, s in pool.items() if s == best]
        return {"rulers": rulers, "claims_mercury": dm, "claims_moon": dl, "score": score, "dominates_both": bool(both)}

    def honourable(self, p: str) -> bool:
        """III.13 'honourable' read as: in own domicile/exaltation/triplicity (Ptolemy's own familiarity) and not under the beams."""
        sign = SIGNS[sign_index(self.lon[p])]
        trip = kb.dignities()["triplicity"]["ptolemaic"]["table"][ELEMENT[sign_index(self.lon[p])]]
        own = p in kb.dignities()["domicile"]["table"][sign] or dignity.exaltation_lord(sign) == p or p in trip
        return own and self.c["conditions"][p].get("solar", {}).get("phase") is None

    def lord_of_action(self) -> dict | None:
        """IV.4: the planet that has most recently made its morning appearance nearest the Sun, and the planet at the MC
        (especially with the Moon applying); else the ruler of the MC sign."""
        if not self.time_known:
            return None
        morning = []
        for p in FIVE:
            el = -self.c["conditions"][p]["solar"]["elongation"]               # > 0: rises before the Sun
            if el >= 15.0:
                morning.append((el, p))
        morning_p = min(morning)[1] if morning else None
        at_mc = [p for p in FIVE if self.place_ptolemy(p) == 10]
        cand = sorted(set(([morning_p] if morning_p else []) + at_mc))
        out = {"morning": morning_p, "at_mc": at_mc}
        if cand:
            out["lords"] = [p for p in cand if p in ("mercury", "venus", "mars")] or cand
            out["fallback"] = False
        else:
            out["lords"] = [dignity.domicile_lord(self.c["angles"]["mc"]["sign"])]
            out["fallback"] = True
        q = [p for p in out["lords"] if p in ("mercury", "venus", "mars")]
        out["quality"] = q
        out["testimony"] = [p for p in ("jupiter", "saturn") if any(self._configured(p, x) for x in q)]
        return out

    def _configured(self, a: str, b: str) -> bool:
        n = sign_distance(self.lon[a], self.lon[b])
        return min(n, 12 - n) in (0, 2, 3, 4, 6)

    def lot_ptolemy(self) -> float | None:
        if not self.time_known:
            return None
        return (self.lon["asc"] + self.lon["moon"] - self.lon["sun"]) % 360.0          # III.10: same by day and night

    def fortune_ruler_ptolemy(self) -> dict | None:
        lot = self.lot_ptolemy()
        if lot is None:
            return None
        d = self.ptolemy_dominators(lot)
        d5 = {p: v for p, v in d.items() if p in FIVE}
        best = max(len(v) for v in d5.values())
        return {"lot": lot, "rulers": [p for p, v in d5.items() if len(v) == best], "claims": d5}

    # ---------------------------------------------------------------- Valens
    def valens_sect_lords(self) -> dict | None:
        """II.2: the sect light's triangle lords (first, second, co-working) and the grade of the place each holds."""
        if not self.time_known:
            return None
        light = "sun" if self.is_day else "moon"
        el = ELEMENT[sign_index(self.lon[light])]
        t = kb.dignities()["triplicity"]["dorothean"]["table"][el]
        first, second = (t[0], t[1]) if self.is_day else (t[1], t[0])
        def grade(p):
            pl = self.place_ws(p)
            return "fortunate" if pl in (1, 4, 7, 10, 11, 5) else "moderate" if pl in (2, 8) else "base"
        return {"light": light, "element": el, "first": first, "second": second, "co": t[2],
                "grades": {first: grade(first), second: grade(second), t[2]: grade(t[2])},
                "places": {first: self.place_ws(first), second: self.place_ws(second), t[2]: self.place_ws(t[2])}}

    # ---------------------------------------------------------------- the Moon's separation and application
    def moon_contacts(self) -> dict:
        """The last Ptolemaic aspect the Moon perfected and the next one it will perfect (with the moving planets),
        searched over the Moon's travel through about 30 degrees either way (2.4 days), on interpolated tracks."""
        import numpy as np
        from ..transits import Track, _root
        jd = self.c["time"]["jd_ut"]
        moon = Track("moon", jd - 2.5, jd + 2.5, 1 / 24)
        cands = []
        for p in ("sun", "mercury", "venus", "mars", "jupiter", "saturn"):
            tp = Track(p, jd - 2.5, jd + 2.5, 0.25)
            grid = moon.grid[(moon.grid >= jd - 2.4) & (moon.grid <= jd + 2.4)]
            lp = np.array([tp.at(x) for x in grid])
            lm = np.array([moon.at(x) for x in grid])
            for ang in (0, 60, -60, 90, -90, 120, -120, 180):
                g = (lm - lp - ang + 180.0) % 360.0 - 180.0
                for k in np.nonzero((np.sign(g[:-1]) != np.sign(g[1:])) & (np.abs(g[:-1]) < 20))[0]:
                    f = lambda x: (moon.at(x) - tp.at(x) - ang + 180.0) % 360.0 - 180.0
                    x = _root(f, float(grid[k]), float(grid[k + 1]), float(g[k]))
                    cands.append((x - jd, p, PTOLEMAIC_ASPECTS[{0: 0, 60: 2, 90: 3, 120: 4, 180: 6}[abs(ang)]]))
        out = {"applies_to": None, "separated_from": None}
        fut = [c for c in cands if c[0] > 0]
        past = [c for c in cands if c[0] <= 0]
        if fut:
            d, pl, asp = min(fut)
            out["applies_to"] = {"planet": pl, "aspect": asp, "days": round(float(d), 3)}
        if past:
            d, pl, asp = max(past)
            out["separated_from"] = {"planet": pl, "aspect": asp, "days": round(float(-d), 3)}
        return out

    # ---------------------------------------------------------------- Leo
    def leo_counts(self) -> dict:
        """Art of Synthesis Method I: planets (ten) by triplicity and quadruplicity."""
        el = {k: [] for k in ("fire", "earth", "air", "water")}
        mo = {k: [] for k in ("cardinal", "fixed", "mutable")}
        for p in E.PLANETS:
            i = sign_index(self.lon[p])
            el[ELEMENT[i]].append(p)
            mo[MODALITY[i]].append(p)
        return {"element": el, "modality": mo}

    def leo_centres(self) -> dict:
        """Method II: quadruplicity of Sun, Moon and Ascendant."""
        q = {k: MODALITY[sign_index(self.lon[k])] for k in ("sun", "moon") + (("asc",) if self.time_known else ())}
        return q
