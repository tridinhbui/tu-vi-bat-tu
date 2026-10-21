"""Bát Tự Hà Lạc: casting the birth hexagram (quẻ Tiên Thiên / Hậu Thiên), Nguyên đường, quẻ hỗ, Hóa công, Thiên / Địa nguyên khí,
đại vận and lưu niên.

Every rule is transcribed from Học-Năng, "Bát-Tự Hà-Lạc Lược-Khảo" (Sài Gòn 1974), Phần I (scanned PDF
"(kinhdich)-Sách bat-tu-ha-lac-dantocking.com.pdf"; printed page = PDF page + 2 in Phần I). Page cites below are printed pages.
Nothing here interprets: readings of the quẻ / hào live in engine/data/ha_lac/hexagrams.json (Phần II, quẻ 24-64, from a text-layer
extract) and hexagrams_1_23.json (Phần II, quẻ 1-23, read from the scan; printed pp.139-277).

  p.35-36  bảng trị số of the 10 can and 12 chi (Hà Đồ)            p.41  8 quẻ of Lạc Thư with their numbers (nạp giáp)
  p.42     dương nam / âm nữ: dương quái above; âm nam / dương nữ: âm quái above
  p.44-46  reduce the sums: dương > 25 minus 25 once, âm > 30 minus 30 once; >= 10 keep the units, an exact multiple of 10 keeps its tens
  p.47-48  number 5 by Tam Nguyên (Thượng 1864-1923, Trung 1924-1983, Hạ 1984-2043)
  p.49     Hóa công by the quarter between the solstices / equinoxes;  p.50  Thiên nguyên khí from the year can, Địa from the year chi
  p.70-77  Nguyên đường from the birth hour (three câu ca);  p.77-83  quẻ thuần Kiền / Khôn (Bảng thuần hào I, II)
  p.84     Hậu Thiên: swap the two quái, flip the Nguyên đường hào;  p.85  quẻ hỗ (hào 2-4, 3-5)
  p.85-86  đại vận: from the Nguyên đường upward, hào dương 9 years, hào âm 6;  Hậu Thiên continues from its Nguyên đường
  p.87-90  lưu niên of a đại vận hào âm (6 years) and hào dương (9 years: thế / ứng first)
  p.21     the year changes at Lập Xuân; p.31 the 12 two-hour periods: the pillars are ordinary Bát Tự pillars (tvbt.bazi)."""
from __future__ import annotations

from dataclasses import dataclass

from .ganzhi import BRANCHES_VI, STEMS_VI

SOURCE = "Học-Năng, Bát-Tự Hà-Lạc Lược-Khảo (1974), Phần I"

# p.35: Mậu 1, Ất/Quý 2, Canh 3, Tân 4, Nhâm/Giáp 6, Đinh 7, Bính 8, Kỷ 9 (5 stands alone)
STEM_NUMBER = {"Giáp": 6, "Ất": 2, "Bính": 8, "Đinh": 7, "Mậu": 1, "Kỷ": 9, "Canh": 3, "Tân": 4, "Nhâm": 6, "Quý": 2}
# p.36: Hợi Tý 1·6 (Thủy), Tỵ Ngọ 2·7 (Hỏa), Dần Mão 3·8 (Mộc), Thân Dậu 4·9 (Kim), Thìn Tuất Sửu Mùi 5·10 (Thổ)
BRANCH_NUMBERS = {"Tý": (1, 6), "Hợi": (1, 6), "Tỵ": (2, 7), "Ngọ": (2, 7), "Dần": (3, 8), "Mão": (3, 8), "Thân": (4, 9), "Dậu": (4, 9),
                  "Thìn": (5, 10), "Tuất": (5, 10), "Sửu": (5, 10), "Mùi": (5, 10)}
# p.40-41: Lạc Thư numbers of the 8 quái
TRIGRAM_OF_NUMBER = {1: "Khảm", 2: "Khôn", 3: "Chấn", 4: "Tốn", 6: "Kiền", 7: "Đoài", 8: "Cấn", 9: "Ly"}
# hào 1..3 of each quái, 1 = dương (vạch liền)
TRIGRAM_LINES = {"Kiền": (1, 1, 1), "Đoài": (1, 1, 0), "Ly": (1, 0, 1), "Chấn": (1, 0, 0),
                 "Tốn": (0, 1, 1), "Khảm": (0, 1, 0), "Cấn": (0, 0, 1), "Khôn": (0, 0, 0)}
LINES_TRIGRAM = {v: k for k, v in TRIGRAM_LINES.items()}
TRIGRAM_IMAGE = {"Kiền": "Thiên", "Đoài": "Trạch", "Ly": "Hỏa", "Chấn": "Lôi", "Tốn": "Phong", "Khảm": "Thủy", "Cấn": "Sơn", "Khôn": "Địa"}
# King Wen number, name, upper, lower (the book's 'Đồ biểu 64 quẻ', last pages of the book)
HEXAGRAMS = {
    1: ("Kiền", "Kiền", "Kiền"), 2: ("Khôn", "Khôn", "Khôn"), 3: ("Truân", "Khảm", "Chấn"), 4: ("Mông", "Cấn", "Khảm"),
    5: ("Nhu", "Khảm", "Kiền"), 6: ("Tụng", "Kiền", "Khảm"), 7: ("Sư", "Khôn", "Khảm"), 8: ("Tỷ", "Khảm", "Khôn"),
    9: ("Tiểu Súc", "Tốn", "Kiền"), 10: ("Lý", "Kiền", "Đoài"), 11: ("Thái", "Khôn", "Kiền"), 12: ("Bĩ", "Kiền", "Khôn"),
    13: ("Đồng Nhân", "Kiền", "Ly"), 14: ("Đại Hữu", "Ly", "Kiền"), 15: ("Khiêm", "Khôn", "Cấn"), 16: ("Dự", "Chấn", "Khôn"),
    17: ("Tùy", "Đoài", "Chấn"), 18: ("Cổ", "Cấn", "Tốn"), 19: ("Lâm", "Khôn", "Đoài"), 20: ("Quan", "Tốn", "Khôn"),
    21: ("Phệ Hạp", "Ly", "Chấn"), 22: ("Bí", "Cấn", "Ly"), 23: ("Bác", "Cấn", "Khôn"), 24: ("Phục", "Khôn", "Chấn"),
    25: ("Vô Vọng", "Kiền", "Chấn"), 26: ("Đại Súc", "Cấn", "Kiền"), 27: ("Di", "Cấn", "Chấn"), 28: ("Đại Quá", "Đoài", "Tốn"),
    29: ("Khảm", "Khảm", "Khảm"), 30: ("Ly", "Ly", "Ly"), 31: ("Hàm", "Đoài", "Cấn"), 32: ("Hằng", "Chấn", "Tốn"),
    33: ("Độn", "Kiền", "Cấn"), 34: ("Đại Tráng", "Chấn", "Kiền"), 35: ("Tấn", "Ly", "Khôn"), 36: ("Minh Di", "Khôn", "Ly"),
    37: ("Gia Nhân", "Tốn", "Ly"), 38: ("Khuê", "Ly", "Đoài"), 39: ("Kiển", "Khảm", "Cấn"), 40: ("Giải", "Chấn", "Khảm"),
    41: ("Tổn", "Cấn", "Đoài"), 42: ("Ích", "Tốn", "Chấn"), 43: ("Quải", "Đoài", "Kiền"), 44: ("Cấu", "Kiền", "Tốn"),
    45: ("Tụy", "Đoài", "Khôn"), 46: ("Thăng", "Khôn", "Tốn"), 47: ("Khốn", "Đoài", "Khảm"), 48: ("Tỉnh", "Khảm", "Tốn"),
    49: ("Cách", "Đoài", "Ly"), 50: ("Đỉnh", "Ly", "Tốn"), 51: ("Chấn", "Chấn", "Chấn"), 52: ("Cấn", "Cấn", "Cấn"),
    53: ("Tiệm", "Tốn", "Cấn"), 54: ("Quy Muội", "Chấn", "Đoài"), 55: ("Phong", "Chấn", "Ly"), 56: ("Lữ", "Ly", "Cấn"),
    57: ("Tốn", "Tốn", "Tốn"), 58: ("Đoài", "Đoài", "Đoài"), 59: ("Hoán", "Tốn", "Khảm"), 60: ("Tiết", "Khảm", "Đoài"),
    61: ("Trung Phu", "Tốn", "Đoài"), 62: ("Tiểu Quá", "Chấn", "Cấn"), 63: ("Ký Tế", "Khảm", "Ly"), 64: ("Vị Tế", "Ly", "Khảm"),
}
NUMBER_OF = {(u, l): n for n, (_, u, l) in HEXAGRAMS.items()}
# p.49: the quarter after each of these terms (sxtwl jqIndex: 0 Đông Chí, 6 Xuân Phân, 12 Hạ Chí, 18 Thu Phân)
HOA_CONG = {0: "Khảm", 6: "Chấn", 12: "Ly", 18: "Đoài"}
# p.50 (Thìn is a hand correction in the scan: 'Tân, Thìn, Tỵ thuộc Tốn')
NGUYEN_KHI_STEM = {"Giáp": "Kiền", "Nhâm": "Kiền", "Ất": "Khôn", "Quý": "Khôn", "Bính": "Cấn", "Đinh": "Đoài", "Mậu": "Khảm",
                   "Kỷ": "Ly", "Canh": "Chấn", "Tân": "Tốn"}
NGUYEN_KHI_BRANCH = {"Tuất": "Kiền", "Hợi": "Kiền", "Mùi": "Khôn", "Thân": "Khôn", "Sửu": "Cấn", "Dần": "Cấn", "Dậu": "Đoài",
                     "Tý": "Khảm", "Ngọ": "Ly", "Mão": "Chấn", "Thìn": "Tốn", "Tỵ": "Tốn"}
DUONG_STEMS = {"Giáp", "Bính", "Mậu", "Canh", "Nhâm"}


def hexagram(lines) -> dict:
    """lines: hào 1..6, 1 = dương."""
    lines = tuple(lines)
    lower, upper = LINES_TRIGRAM[lines[:3]], LINES_TRIGRAM[lines[3:]]
    n = NUMBER_OF[(upper, lower)]
    name = HEXAGRAMS[n][0]
    full = f"Thuần {name}" if upper == lower else f"{TRIGRAM_IMAGE[upper]} {TRIGRAM_IMAGE[lower]} {name}"
    return {"number": n, "name": name, "full_name": full, "upper": upper, "lower": lower,
            "lines": ["dương" if x else "âm" for x in lines]}


def lines_of(upper: str, lower: str) -> tuple[int, ...]:
    return TRIGRAM_LINES[lower] + TRIGRAM_LINES[upper]


# ---------------------------------------------------------------- numbers and sums (pp.35-48)

def pillar_numbers(stem: str, branch: str) -> list[int]:
    return [STEM_NUMBER[stem], *BRANCH_NUMBERS[branch]]


def sums(pillars: list[tuple[str, str]]) -> dict:
    """pillars: [(can, chi)] for year, month, day, hour. Odd numbers go to the dương sum, even ones to the âm sum (p.42-43)."""
    nums = [x for s, b in pillars for x in pillar_numbers(s, b)]
    duong, am = [x for x in nums if x % 2], [x for x in nums if not x % 2]
    return {"duong_terms": duong, "am_terms": am, "duong": sum(duong), "am": sum(am)}


def reduce_sum(total: int, cap: int) -> int:
    """p.44-46: dương (cap 25) / âm (cap 30): subtract the cap once if the total exceeds it; a remainder >= 10 keeps its units digit,
    except an exact multiple of 10, which keeps its tens digit (20 -> 2, 30 -> 3, 40 -> 4)."""
    n = total - cap if total > cap else total
    if n >= 10:
        n = n // 10 if n % 10 == 0 else n % 10
    return n


def tam_nguyen(year: int) -> str:
    """p.48: Thượng 1864-1923, Trung 1924-1983, Hạ 1984-2043 (one 180-year cycle; other years repeat it every 180 years)."""
    return ("Thượng", "Trung", "Hạ")[((year - 1864) % 180) // 60]


def trigram_of(number: int, *, male: bool, duong_year: bool, year: int) -> str:
    if number != 5:
        return TRIGRAM_OF_NUMBER[number]
    # p.47-48: 5 has no quái on Lạc Thư
    nguyen = tam_nguyen(year)
    if nguyen == "Thượng":
        return "Cấn" if male else "Khôn"
    if nguyen == "Hạ":
        return "Ly" if male else "Đoài"
    return "Cấn" if male == duong_year else "Khôn"  # Trung: dương nam / âm nữ Cấn, dương nữ / âm nam Khôn


# ---------------------------------------------------------------- Nguyên đường (pp.70-83)

_THUAN_SEQ = {"lower_up": (1, 2, 3, 1, 2, 3), "upper_up": (4, 5, 6, 4, 5, 6),
              "upper_down": (6, 5, 4, 6, 5, 4), "lower_down": (3, 2, 1, 3, 2, 1)}


def nguyen_duong(lines, hour_branch: str, *, male: bool, after_winter_solstice: bool) -> int:
    """Hào of the Nguyên đường. after_winter_solstice: born after Đông Chí and before Hạ Chí (only used for quẻ thuần Kiền / Khôn)."""
    lines = tuple(lines)
    b = BRANCHES_VI.index(hour_branch)
    pol, k = (1 if b < 6 else 0), b % 6  # giờ dương Tý..Tỵ count from Tý, giờ âm Ngọ..Hợi from Ngọ
    if lines in ((1,) * 6, (0,) * 6):
        kien = lines[0] == 1
        if kien == male:  # Kiền nam, Khôn nữ: no season (Bảng thuần hào I)
            mode = "lower_up" if pol else "upper_up"
        else:  # Kiền nữ, Khôn nam: by season, Khôn nam with the seasons reversed (Bảng thuần hào II)
            from_top = after_winter_solstice if kien else not after_winter_solstice
            mode = ("upper_down" if pol else "lower_down") if from_top else ("lower_up" if pol else "upper_up")
        return _THUAN_SEQ[mode][k]
    own = [i + 1 for i, x in enumerate(lines) if x == pol]
    other = [i + 1 for i, x in enumerate(lines) if x != pol]
    # câu ca 1-2: 1-3 hào of the hour's kind are counted twice (đếm đi, đếm lại); câu ca 3: 4-5 hào once; then the other hào, bottom up
    seq = own + own + other if len(own) <= 3 else own + other
    return seq[k]


def hau_thien(lines, nd: int) -> tuple[tuple[int, ...], int]:
    """p.84: flip the Nguyên đường hào, then the lower quái becomes the upper one and vice versa; the Nguyên đường moves with its quái."""
    x = list(lines)
    x[nd - 1] ^= 1
    new = tuple(x[3:] + x[:3])
    return new, (nd + 3 if nd <= 3 else nd - 3)


def ho(lines) -> dict:
    """p.85: inner hỗ = hào 2-4, outer hỗ = hào 3-5."""
    lines = tuple(lines)
    return {"upper": LINES_TRIGRAM[lines[2:5]], "lower": LINES_TRIGRAM[lines[1:4]]}


def dai_van(lines, nd: int, start_age: int = 1) -> list[dict]:
    """p.85-86: from the Nguyên đường upward and round again; hào dương 9 years, hào âm 6."""
    out, age = [], start_age
    for i in range(6):
        h = (nd - 1 + i) % 6 + 1
        n = 9 if lines[h - 1] else 6
        out.append({"hao": h, "line": "dương" if lines[h - 1] else "âm", "from_age": age, "to_age": age + n - 1})
        age += n
    return out


def luu_nien(lines, hao: int, start_age: int, first_year_duong: bool) -> list[dict]:
    """p.87-90: the yearly quẻ inside one đại vận. Each year's quẻ comes from the previous year's quẻ (changes accumulate).
    Hào âm: flip hào, hào+1, ... (6 years). Hào dương (9 years): year 1 flips the hào (thế) only in an âm year, year 2 flips the
    ứng hào (thế ± 3), year 3 flips the thế again, then thế+1 ... thế, one hào a year."""
    cur = list(lines)
    if lines[hao - 1]:
        ung = hao + 3 if hao <= 3 else hao - 3
        flips = [hao if not first_year_duong else None, ung, hao] + [(hao + i) % 6 + 1 for i in range(6)]
    else:
        flips = [(hao - 1 + i) % 6 + 1 for i in range(6)]
    out = []
    for i, f in enumerate(flips):
        if f is not None:
            cur[f - 1] ^= 1
        out.append({"age": start_age + i, "changed_hao": f, **hexagram(cur)})
    return out


# ---------------------------------------------------------------- Hóa công, nguyên khí (pp.49-50)

def places(trigram: str, tt, ht) -> list[str]:
    """Where a quái appears: chính / hỗ of Tiên Thiên (T.T) and Hậu Thiên (H.T)."""
    out = []
    for tag, lines in (("T.T", tt), ("H.T", ht)):
        h = hexagram(lines)
        if trigram in (h["upper"], h["lower"]):
            out.append(f"chính {tag}")
        if trigram in ho(lines).values():
            out.append(f"hỗ {tag}")
    return out


# ---------------------------------------------------------------- the whole cast

@dataclass(frozen=True)
class Pillars:
    year: tuple[str, str]
    month: tuple[str, str]
    day: tuple[str, str]
    hour: tuple[str, str]


def cast(p: Pillars, *, male: bool, bazi_year: int, after_winter_solstice: bool, hoa_cong_term: int) -> dict:
    """p: the four pillars (can, chi); bazi_year: the year as counted from Lập Xuân; after_winter_solstice: born after Đông Chí and
    before Hạ Chí; hoa_cong_term: sxtwl index (0, 6, 12, 18) of the last solstice / equinox before the birth."""
    pillars = [p.year, p.month, p.day, p.hour]
    s = sums(pillars)
    duong_year = p.year[0] in DUONG_STEMS
    rd, ra = reduce_sum(s["duong"], 25), reduce_sum(s["am"], 30)
    q_d = trigram_of(rd, male=male, duong_year=duong_year, year=bazi_year)
    q_a = trigram_of(ra, male=male, duong_year=duong_year, year=bazi_year)
    duong_above = male == duong_year  # p.42
    upper, lower = (q_d, q_a) if duong_above else (q_a, q_d)
    tt = lines_of(upper, lower)
    nd = nguyen_duong(tt, p.hour[1], male=male, after_winter_solstice=after_winter_solstice)
    ht, nd_ht = hau_thien(tt, nd)
    dv_tt = dai_van(tt, nd)
    dv_ht = dai_van(ht, nd_ht, dv_tt[-1]["to_age"] + 1)
    hc = HOA_CONG[hoa_cong_term]
    tnk, dnk = NGUYEN_KHI_STEM[p.year[0]], NGUYEN_KHI_BRANCH[p.year[1]]
    return {
        "source": SOURCE,
        "polarity": ("Dương" if duong_year else "Âm") + (" nam" if male else " nữ"),
        "pillars": [{"can": a, "chi": b, "numbers": pillar_numbers(a, b)} for a, b in pillars],
        "sum_duong": {"terms": s["duong_terms"], "total": s["duong"], "number": rd, "trigram": q_d},
        "sum_am": {"terms": s["am_terms"], "total": s["am"], "number": ra, "trigram": q_a},
        "tam_nguyen": tam_nguyen(bazi_year) if 5 in (rd, ra) else None,
        "tien_thien": {**hexagram(tt), "nguyen_duong_hao": nd, "ho": ho(tt), "dai_van": dv_tt},
        "hau_thien": {**hexagram(ht), "nguyen_duong_hao": nd_ht, "ho": ho(ht), "dai_van": dv_ht},
        "hoa_cong": {"trigram": hc, "where": places(hc, tt, ht)},
        "thien_nguyen_khi": {"trigram": tnk, "where": places(tnk, tt, ht)},
        "dia_nguyen_khi": {"trigram": dnk, "where": places(dnk, tt, ht)},
    }


def year_is_duong(year: int) -> bool:
    return (year - 4) % 2 == 0  # Giáp (1984, 1924, ...) is dương


def dai_van_at(c: dict, age: int) -> tuple[str, dict] | None:
    for side in ("tien_thien", "hau_thien"):
        for d in c[side]["dai_van"]:
            if d["from_age"] <= age <= d["to_age"]:
                return side, d
    return None


def luu_nien_at(c: dict, bazi_year: int, age: int) -> dict | None:
    """Lưu niên quẻ at an age (tuổi, 1 in the birth year), for a person born in bazi_year."""
    hit = dai_van_at(c, age)
    if not hit:
        return None
    side, d = hit
    lines = tuple(1 if x == "dương" else 0 for x in c[side]["lines"])
    first_year = bazi_year + d["from_age"] - 1
    seq = luu_nien(lines, d["hao"], d["from_age"], year_is_duong(first_year))
    return {"side": side, "dai_van": d, **seq[age - d["from_age"]]}


# ---------------------------------------------------------------- from a birth (engine calendar)

def season_facts(birth_utc_jd: float, year: int) -> tuple[bool, int]:
    """(after Đông Chí and before Hạ Chí, sxtwl index of the last solstice / equinox) at the instant of birth."""
    from . import astro
    terms = [(i, jd) for i, jd in astro.all_terms_around(year) if i in HOA_CONG and jd <= birth_utc_jd]
    last = max(terms, key=lambda t: t[1])[0]
    return last in (0, 6), last


def cast_birth(b) -> dict:
    """b: tvbt.calendar_core.BirthInput. Pillars from tvbt.bazi (year at Lập Xuân, month at each tiết, the engine's Tý-hour rule)."""
    from . import astro, bazi
    from .calendar_core import normalize
    nb = normalize(b)
    ch = bazi.compute(nb)
    pl = {k: (STEMS_VI[v.stem], BRANCHES_VI[v.branch]) for k, v in ch.pillars.items()}
    jd = astro.utc_to_jd(nb.utc)
    after_dc, term = season_facts(jd, nb.utc.year)
    bazi_year = _bazi_year(nb)
    c = cast(Pillars(pl["year"], pl["month"], pl["day"], pl["hour"]), male=b.gender == "male", bazi_year=bazi_year,
             after_winter_solstice=after_dc, hoa_cong_term=term)
    c["bazi_year"] = bazi_year
    return c


def _bazi_year(nb) -> int:
    from . import astro
    jd = astro.utc_to_jd(nb.utc)
    lichun = [x for i, x in astro.all_terms_around(nb.utc.year) if i == 3 and x <= jd]
    return astro.jd_to_utc(max(lichun)).astimezone(astro.BEIJING).year


# ---------------------------------------------------------------- for prose (luận giải)

_READINGS: dict | None = None


def readings() -> dict[int, dict]:
    """Phần II paraphrases by quẻ number: hexagrams_1_23.json (quẻ 1-23, scan, printed pages) + hexagrams.json (quẻ 24-64, extract)."""
    global _READINGS
    if _READINGS is None:
        import json
        from pathlib import Path
        d = Path(__file__).resolve().parent.parent / "data" / "ha_lac"
        _READINGS = {h["number"]: h for f in ("hexagrams_1_23.json", "hexagrams.json")
                     for h in json.loads((d / f).read_text("utf-8"))["hexagrams"]}
    return _READINGS


def hao_reading(number: int, hao: int) -> dict | None:
    h = readings().get(number)
    if not h:
        return None
    a = h["hao"][hao - 1]
    return {"que": h["full_name"], "hao": hao, "line": a["line"], "y_hao": a["y_hao"], "menh_hop_cach": a["menh_hop_cach"],
            "menh_khong_hop": a["menh_khong_hop"], "tue_van": a["tue_van"], "tue_van_other": a.get("tue_van_other", []),
            "page_note": "Phần II, printed pages of the 1974 scan" if h.get("source") == "scan"
            else "Phần II extract (dantocking.com), pages as given"}


def summary(c: dict, age: int | None = None) -> dict:
    """Compact, JSON-ready facts for a 'Về Bát Tự Hà Lạc' paragraph. c = cast() / cast_birth(); age = tuổi (1 in the birth year).
    The book itself warns that hào words are not to be read literally (Phần II p.123: 'hào từ vị khả vi cứ'), so prose should
    present these as suggestions."""
    tt, ht = c["tien_thien"], c["hau_thien"]
    out = {
        "validated": True,
        "validation": "tests/test_ha_lac_cast.py: every example worked in Phần I (pp.43-96) and the five charts of the Phần II extract",
        "source": c["source"],
        "polarity": c["polarity"],
        "tien_thien": {"number": tt["number"], "name": tt["full_name"], "nguyen_duong_hao": tt["nguyen_duong_hao"],
                       "nguyen_duong_line": tt["lines"][tt["nguyen_duong_hao"] - 1], "years": [tt["dai_van"][0]["from_age"], tt["dai_van"][-1]["to_age"]]},
        "hau_thien": {"number": ht["number"], "name": ht["full_name"], "nguyen_duong_hao": ht["nguyen_duong_hao"],
                      "nguyen_duong_line": ht["lines"][ht["nguyen_duong_hao"] - 1], "from_age": ht["dai_van"][0]["from_age"]},
        "hoa_cong": {"trigram": c["hoa_cong"]["trigram"], "present": bool(c["hoa_cong"]["where"]), "where": c["hoa_cong"]["where"]},
        "thien_nguyen_khi": {"trigram": c["thien_nguyen_khi"]["trigram"], "present": bool(c["thien_nguyen_khi"]["where"]),
                             "where": c["thien_nguyen_khi"]["where"]},
        "dia_nguyen_khi": {"trigram": c["dia_nguyen_khi"]["trigram"], "present": bool(c["dia_nguyen_khi"]["where"]),
                           "where": c["dia_nguyen_khi"]["where"]},
        "nguyen_duong_reading": hao_reading(tt["number"], tt["nguyen_duong_hao"]),
        "readings_coverage": "quẻ 1-64 (Phần II: 1-23 from the 1974 scan, 24-64 from the extract)",
    }
    if age is not None and "bazi_year" in c:
        hit = dai_van_at(c, age)
        if hit:
            side, d = hit
            num = c[side]["number"]
            out["dai_van_now"] = {"side": side, "que": c[side]["full_name"], **d, "reading": hao_reading(num, d["hao"])}
            ln = luu_nien_at(c, c["bazi_year"], age)
            out["luu_nien_now"] = {"age": age, "que": ln["full_name"], "number": ln["number"], "changed_hao": ln["changed_hao"],
                                   # a dương year leaves the thế hào of a dương đại vận unchanged: that hào is the year's hào (p.87)
                                   "reading": hao_reading(ln["number"], ln["changed_hao"] or d["hao"])}
    return out
