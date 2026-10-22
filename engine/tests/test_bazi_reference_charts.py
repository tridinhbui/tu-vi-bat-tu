"""Bát Tự reference charts computed from a birth date and time (audit 2026-10-22, S2 step 2).

Every expected value below was derived by hand from the printed tables, never copied from engine output:
  - year pillar: the Lập Xuân instant (八字真宗 [ZZ] p.23: 正月建寅 立春); cycle index (Y - 4) mod 60, stem = idx mod 10, branch = idx mod 12;
  - month pillar: the last of the twelve jie before birth (ZZ p.23 table: 小寒 → 丑, 大雪 → 子, 寒露 → 戌 …), stem by 五虎遁
    (ZZ p.20: 甲己丙寅, 乙庚戊寅, 丙辛庚寅, 丁壬壬寅, 戊癸甲寅);
  - day pillar: whole days from 1900-01-01 = 甲戌 (cycle 10), cross-checked against 2000-01-01 = 戊午 (cycle 54);
  - hour pillar: branch by clock hour, stem by 五鼠遁 (ZZ p.20 and the p.35 row: 甲己甲子, 乙庚丙子, 丙辛戊子, 丁壬庚子, 戊癸壬子);
  - hidden stems: ZZ pp.7-8 (main, middle, residual as in TVH p.342); ten gods: ZZ p.17; twelve stages: ZZ pp.24-25;
  - luck: ZZ p.23 (陽年男 / 陰年女 thuận to the next jie, 陰年男 / 陽年女 nghịch to the last; 3 days = 1 year), pillars stepping from the month.
The book examples are Thiệu Vĩ Hoa, Dự Đoán Theo Tứ Trụ (TVH) pp.397-399 ("Các ví dụ về chọn dụng thần", lunar birth date and hour printed)
and pp.400-401, and 八字真宗 pp.45-46 (串宫神流年直断命例: pillars, 胎元, 命宫, 身宫 and the đại vận of 1999-2001 printed, no birth date)."""
import datetime as dt
import math

import pytest

from tvbt import bazi, temporal
from tvbt.calendar_core import BirthInput, normalize
from tvbt.lunar_input import lunar_to_solar


def chart(y, m, d, h, mi, gender, tz="Asia/Ho_Chi_Minh"):
    nb = normalize(BirthInput(y, m, d, h, mi, tz, gender))
    return nb, bazi.compute(nb)


def names(c):
    return {k: p.name for k, p in c.pillars.items()}


def hidden(c, k):
    return [(h["name"], h["ten_god"]) for h in c.pillars[k].hidden]


# ---------------------------------------------------------------- 09/01/2002 04:30 nam (the owner's chart, Asia/Ho_Chi_Minh = UTC+7)
def test_2002_01_09_0430_nam():
    nb, c = chart(2002, 1, 9, 4, 30, "male")
    # year: 9 Jan 2002 is before Lập Xuân 2002 (4 Feb) → Bát Tự year 2001: (2001-4) mod 60 = 17 → 辛巳 Tân Tỵ
    # month: after 小寒 (5 Jan 2002) → 丑; 丙辛 → 庚寅, counting on: 辛卯 壬辰 癸巳 甲午 乙未 丙申 丁酉 戊戌 己亥 庚子 辛丑 → Tân Sửu
    # day: 2000-01-01 戊午 (54) + 366 + 365 + 8 = 54 + 739 = 793 ≡ 13 → 丁丑 Đinh Sửu
    # hour: 04:30 → 寅; 丁壬 → 庚子, 辛丑, 壬寅 → Nhâm Dần
    assert names(c) == {"year": "Tân Tỵ", "month": "Tân Sửu", "day": "Đinh Sửu", "hour": "Nhâm Dần"}
    # hidden stems (ZZ pp.7-8) with ten gods against 丁 (ZZ p.17: 丙 劫财, 庚 正财, 戊 伤官, 己 食神, 癸 七杀, 辛 偏财, 甲 正印)
    assert hidden(c, "year") == [("Bính", "Kiếp Tài"), ("Canh", "Chính Tài"), ("Mậu", "Thương Quan")]
    assert hidden(c, "month") == hidden(c, "day") == [("Kỷ", "Thực Thần"), ("Quý", "Thất Sát"), ("Tân", "Thiên Tài")]
    assert hidden(c, "hour") == [("Giáp", "Chính Ấn"), ("Bính", "Kiếp Tài"), ("Mậu", "Thương Quan")]
    # stem ten gods: 辛 偏财 (Thiên Tài) twice, 壬 正官
    assert [c.pillars[k].stem_ten_god for k in ("year", "month", "hour")] == ["Thiên Tài", "Thiên Tài", "Chính Quan"]
    # twelve stages of 丁 (ZZ pp.24-25 row 丁: 酉申未午巳辰卯寅丑子亥戌 = 长生 … 养): 巳 帝旺, 丑 墓, 寅 死
    assert [c.pillars[k].stage_vs_day_master for k in ("year", "month", "day", "hour")] == ["Đế Vượng", "Mộ", "Mộ", "Tử"]
    # luck: 辛 is yin, male → nghịch, back to 小寒 (5 Jan 2002, evening Beijing time): ~3.37 days / 3 = 1.1 years (1 y 1 m)
    assert c.luck_direction == "nghịch"
    assert round(c.luck_start["age_years"], 1) == 1.1 and (c.luck_start["years"], c.luck_start["months"]) == (1, 1)
    assert [l.name for l in c.luck_pillars[:4]] == ["Canh Tý", "Kỷ Hợi", "Mậu Tuất", "Đinh Dậu"]
    # the luck year rule (BZ-5/6): Mậu Tuất starts in February 2023 and holds 2023 (most of that Bát Tự year) to 2032
    mt = c.luck_pillars[2]
    assert mt.start_date.startswith("2023-02") and mt.first_year == 2023
    assert temporal.bazi_year(c, 2002, 2026)["luck_pillar"] == "Mậu Tuất"


# ---------------------------------------------------------------- 01/01/1911 12:30 nam (Asia/Ho_Chi_Minh: Phù Liễn mean time +07:06:30 then)
def test_1911_01_01_1230_nam():
    nb, c = chart(1911, 1, 1, 12, 30, "male")
    assert nb.utc == dt.datetime(1911, 1, 1, 5, 23, 30, tzinfo=dt.timezone.utc)      # tzdb Asia/Ho_Chi_Minh: PLMT until 1911-05-01
    # year: before Lập Xuân 1911 → 1910: 1906 mod 60 = 46 → 庚戌 Canh Tuất
    # month: after 大雪 (Dec 1910), before 小寒 (6 Jan 1911) → 子; 乙庚 → 戊寅 … 丙戌 丁亥 戊子 → Mậu Tý
    # day: 1900-01-01 甲戌 (10) + 11·365 + 2 (1904, 1908) = 10 + 4017 = 4027 ≡ 7 → 辛未 Tân Mùi; check: + 32507 days to 2000-01-01 → 54 戊午
    # hour: 12:30 → 午; 丙辛 → 戊子 己丑 庚寅 辛卯 壬辰 癸巳 甲午 → Giáp Ngọ
    assert names(c) == {"year": "Canh Tuất", "month": "Mậu Tý", "day": "Tân Mùi", "hour": "Giáp Ngọ"}
    # ten gods against 辛 (ZZ p.17): 庚 劫财, 戊 正印, 甲 正财; hidden 戌 戊辛丁, 子 癸, 未 己丁乙, 午 丁己
    assert [c.pillars[k].stem_ten_god for k in ("year", "month", "hour")] == ["Kiếp Tài", "Chính Ấn", "Chính Tài"]
    assert hidden(c, "year") == [("Mậu", "Chính Ấn"), ("Tân", "Tỉ Kiên"), ("Đinh", "Thất Sát")]
    assert hidden(c, "month") == [("Quý", "Thực Thần")]
    assert hidden(c, "day") == [("Kỷ", "Thiên Ấn"), ("Đinh", "Thất Sát"), ("Ất", "Thiên Tài")]
    assert hidden(c, "hour") == [("Đinh", "Thất Sát"), ("Kỷ", "Thiên Ấn")]
    # stages of 辛 (ZZ pp.24-25 row 辛: 子亥戌酉申未午巳辰卯寅丑): 戌 冠带, 子 长生, 未 衰, 午 病
    assert [c.pillars[k].stage_vs_day_master for k in ("year", "month", "day", "hour")] == ["Quan Đới", "Trường Sinh", "Suy", "Bệnh"]
    # luck: 庚 yang, male → thuận to 小寒 1911 (6 Jan): ~5.2 days → 1.7 years; from 戊子: 己丑 庚寅 辛卯
    assert c.luck_direction == "thuận" and round(c.luck_start["age_years"], 1) == 1.7
    assert [l.name for l in c.luck_pillars[:3]] == ["Kỷ Sửu", "Canh Dần", "Tân Mão"]
    # 空亡 of 辛未 (xun 甲子: 戌亥) and 胎元 = month stem + 1, branch + 3 (ZZ pp.35-36): 己卯
    assert c.extras["kong_wang_day"] == ["Tuất", "Hợi"] and c.extras["thai_yuan"] == "Kỷ Mão"


# ---------------------------------------------------------------- TVH pp.397-401: the male examples with a printed lunar date and hour
TVH = [
    # (example, lunar day, month, year, hour, printed pillars year/month/day/hour, printed first luck pillars, printed start age, page)
    ("vd1", 2, 11, 1952, 8, ("Nhâm Thìn", "Tân Hợi", "Mậu Tuất", "Bính Thìn"), ["Nhâm Tý", "Quý Sửu", "Giáp Dần"], 6, "397"),
    ("vd2", 10, 9, 1975, 0, ("Ất Mão", "Bính Tuất", "Quý Tỵ", "Nhâm Tý"), ["Ất Dậu", "Giáp Thân", "Quý Mùi"], 2, "398"),
    ("vd3", 29, 9, 1970, 18, ("Canh Tuất", "Bính Tuất", "Tân Tỵ", "Đinh Dậu"), ["Đinh Hợi", "Mậu Tý", "Kỷ Sửu"], 4, "399"),
    # Ví dụ 4 (nữ, p.400) is not used: its stem row is typeset out of line with the columns, so the printed pillars cannot be read reliably
    ("vd5", 25, 9, 1966, 18, ("Bính Ngọ", "Mậu Tuất", "Canh Ngọ", "Ất Dậu"), ["Kỷ Hợi", "Canh Tý", "Tân Sửu"], 1, "400-401"),
]


@pytest.mark.parametrize("ex", TVH, ids=[x[0] for x in TVH])
def test_tvh_examples_from_their_printed_birth(ex):
    """The book prints the birth as a lunar date and an hour branch (giờ Thìn / Tý / Dậu); the clock hour used is inside that branch, and
    the zone is China's (+08), the author's. Ví dụ 3 prints "Ngày 129": the only day of lunar month 9 of 1970 whose pillar is the printed
    Tân Tỵ is the 29th (lunar 9/12 is Giáp Tý), so 29 is used.
    Ví dụ 1 is a book-internal discrepancy, kept visible: the page prints the month Tân Hợi ("lệnh th.10") and the first luck Nhâm Tý, but
    lunar 2/11/1952 is 18 December 1952 (day 戊戌 by the day count: cycle 10 on 1900-01-01, + 19344 days ≡ 34), eleven days after 大雪 (7 Dec), so the
    month by the jie rule of ZZ p.23 is 壬子 Nhâm Tý and the first luck 癸丑. The page's own start age, 6, fits that date (19 days to 小寒
    = 6.3 years) and does not fit a birth in the Hợi month. The other three pillars agree with the page."""
    name, ld, lm, ly, hour, printed, luck, age, page = ex
    (sol,) = lunar_to_solar(ld, lm, ly, False, "cn")
    nb, c = chart(sol.year, sol.month, sol.day, hour, 0, "male", "Asia/Shanghai")
    got = (c.pillars["year"].name, c.pillars["month"].name, c.pillars["day"].name, c.pillars["hour"].name)
    if name == "vd1":
        assert sol == dt.date(1952, 12, 18)
        assert (got[0], got[2], got[3]) == (printed[0], printed[2], printed[3]) and got[1] == "Nhâm Tý"
        assert [l.name for l in c.luck_pillars[:2]] == ["Quý Sửu", "Giáp Dần"]          # one step on from the page, as the month is
    else:
        assert got == printed, (name, page)
        assert [l.name for l in c.luck_pillars[:3]] == luck
    # the page prints whole start ages and does not say how it rounds: 2, 4, 1 are the computed 1.58, 3.47, 0.15 rounded up, 6 is 6.21
    # rounded down; the check is that the printed age is the computed one rounded one way or the other
    a = c.luck_start["age_years"]
    assert age in (math.floor(a), math.ceil(a)), (name, a)


# ---------------------------------------------------------------- 八字真宗 pp.45-46: 乾造 癸未 / 乙丑 / 乙未 / 戊寅, 大运 庚申 in 1999, 2000, 2001
def test_zz_p45_example_pillars_palaces_and_luck():
    """The page prints no birth date. 乙丑 month of a 癸未 year is 小寒 1944 (6 Jan) to 立春 (5 Feb); counting from 1900-01-01 甲戌, 1944-01-01
    is cycle 0 (甲子: 10 + 44·365 + 10 leap days = 10 + 16070 ≡ 0), so the only 乙未 (31) day in that month is 1 February 1944; the 寅 hour of an
    乙 day is 戊寅 (乙庚 → 丙子 丁丑 戊寅). What the page prints is then checked: 胎元 丙辰, 命宫 甲寅, 身宫 丙辰, and
    the đại vận 庚申 in force in each of 1999, 2000 and 2001."""
    nb, c = chart(1944, 2, 1, 4, 0, "male", "Asia/Shanghai")
    assert names(c) == {"year": "Quý Mùi", "month": "Ất Sửu", "day": "Ất Mùi", "hour": "Mậu Dần"}
    assert (c.extras["thai_yuan"], c.extras["ming_gong"], c.extras["shen_gong"]) == ("Bính Thìn", "Giáp Dần", "Bính Thìn")
    assert c.luck_direction == "nghịch"                               # 癸 yin, male
    for y in (1999, 2000, 2001):
        assert temporal.bazi_year(c, 1944, y)["luck_pillar"] == "Canh Thân", y
