"""Golden values transcribed from 八字真宗 (SRC_BAZI_ZHENZONG), PDF pp.19-25, 35 — independent of our code."""
from tvbt import bazi
from tvbt.ganzhi import BRANCHES_HAN, STEMS_HAN, tiger_month_stem

BR = {c: i for i, c in enumerate(BRANCHES_HAN)}
ST = {c: i for i, c in enumerate(STEMS_HAN)}


def b(s):  # branches string -> set of indexes
    return {BR[c] for c in s}


def test_twelve_growth_stages_table_pp24_25():
    # rows: day stem -> branches for 长生,沐浴,冠带,临官,帝旺,衰,病,死,墓,绝,胎,养
    table = {"甲": "亥子丑寅卯辰巳午未申酉戌", "乙": "午巳辰卯寅丑子亥戌酉申未", "丙": "寅卯辰巳午未申酉戌亥子丑",
             "丁": "酉申未午巳辰卯寅丑子亥戌", "戊": "寅卯辰巳午未申酉戌亥子丑", "己": "酉申未午巳辰卯寅丑子亥戌",
             "庚": "巳午未申酉戌亥子丑寅卯辰", "辛": "子亥戌酉申未午巳辰卯寅丑", "壬": "申酉戌亥子丑寅卯辰巳午未",
             "癸": "卯寅丑子亥戌酉申未午巳辰"}
    for stem, row in table.items():
        for i, br in enumerate(row):
            assert bazi.growth_stage(ST[stem], BR[br]) == bazi.STAGES[i], (stem, br)


def test_stem_relations_p20():
    for pair, el in [("甲己", "Thổ"), ("乙庚", "Kim"), ("丙辛", "Thủy"), ("丁壬", "Mộc"), ("戊癸", "Hỏa")]:
        assert bazi.STEM_COMBINE[frozenset(ST[c] for c in pair)] == el
    for pair in ["甲庚", "乙辛", "丙壬", "丁癸"]:
        assert frozenset(ST[c] for c in pair) in bazi.STEM_CLASH


def test_branch_relations_p20():
    six_combine = ["子丑", "寅亥", "卯戌", "辰酉", "巳申", "午未"]
    clash = ["子午", "丑未", "寅申", "卯酉", "辰戌", "巳亥"]
    harm = ["子未", "丑午", "寅巳", "卯辰", "申亥", "酉戌"]
    destroy = ["子酉", "午卯", "申巳", "寅亥", "辰丑", "戌未"]
    for tbl, pairs in [(bazi.SIX_COMBINE, six_combine), (bazi.SIX_CLASH, clash), (bazi.HARM, harm), (bazi.DESTROY, destroy)]:
        assert {frozenset(b(p)) for p in pairs} == set(tbl)
    assert {frozenset(b("子卯"))} == {bazi.PENALTY_PAIR}
    assert bazi.SELF_PENALTY == b("辰午酉亥")
    assert set(bazi.TRIAD["Thủy"]) == b("申子辰") and set(bazi.TRIAD["Mộc"]) == b("亥卯未")
    assert set(bazi.TRIAD["Hỏa"]) == b("寅午戌") and set(bazi.TRIAD["Kim"]) == b("巳酉丑")
    assert set(bazi.PENALTY_TRIPLES["vô ân"]) == b("寅巳申") and set(bazi.PENALTY_TRIPLES["thị thế"]) == b("丑戌未")


def test_five_tigers_and_rats_p20_p35():
    # 年起月: 甲己→丙(寅月), 乙庚→戊, 丙辛→庚, 丁壬→壬, 戊癸→甲
    for stems, first in [("甲己", "丙"), ("乙庚", "戊"), ("丙辛", "庚"), ("丁壬", "壬"), ("戊癸", "甲")]:
        for c in stems:
            assert tiger_month_stem(ST[c]) == ST[first]
    # 日起时 (五鼠遁): 甲己→甲子, 乙庚→丙子, 丙辛→戊子, 丁壬→庚子, 戊癸→壬子
    for stems, first in [("甲己", "甲"), ("乙庚", "丙"), ("丙辛", "戊"), ("丁壬", "庚"), ("戊癸", "壬")]:
        for c in stems:
            assert ST[c] % 5 * 2 % 10 == ST[first]
    # full row check from p.35: 丁壬 day hours: 庚子 辛丑 壬寅 癸卯 甲辰 乙巳 丙午 丁未 戊申 己酉 庚戌 辛亥
    row = "庚子辛丑壬寅癸卯甲辰乙巳丙午丁未戊申己酉庚戌辛亥"
    for i in range(12):
        assert (ST["丁"] % 5 * 2 + i) % 10 == ST[row[2 * i]] and BR[row[2 * i + 1]] == i


TEN = ["Tỉ Kiên", "Kiếp Tài", "Thực Thần", "Thương Quan", "Thiên Tài", "Chính Tài", "Thất Sát", "Chính Quan", "Thiên Ấn", "Chính Ấn"]
# 天干十神表, PDF p.17: row = day stem, columns = 比肩 劫财 食神 伤官 偏财 正财 七杀 正官 偏印 正印
STEM_TABLE = {"甲": "甲乙丙丁戊己庚辛壬癸", "乙": "乙甲丁丙己戊辛庚癸壬", "丙": "丙丁戊己庚辛壬癸甲乙", "丁": "丁丙己戊辛庚癸壬乙甲",
              "戊": "戊己庚辛壬癸甲乙丙丁", "己": "己戊辛庚癸壬乙甲丁丙", "庚": "庚辛壬癸甲乙丙丁戊己", "辛": "辛庚癸壬乙甲丁丙己戊",
              "壬": "壬癸甲乙丙丁戊己庚辛", "癸": "癸壬乙甲丁丙己戊辛庚"}


def test_ten_gods_stem_table_p17():
    for day, row in STEM_TABLE.items():
        for i, other in enumerate(row):
            assert bazi.ten_god(ST[day], ST[other]) == TEN[i], (day, other)


# 地支十神表 p.17 (rows 甲-己 legible): ten-god class of each branch's main (本气) hidden stem
BRANCH_TABLE = {"甲": ["寅", "卯", "巳", "午", "辰戌", "丑未", "申", "酉", "亥", "子"], "乙": ["卯", "寅", "午", "巳", "丑未", "辰戌", "酉", "申", "子", "亥"],
                "丙": ["巳", "午", "辰戌", "丑未", "申", "酉", "亥", "子", "寅", "卯"], "丁": ["午", "巳", "丑未", "辰戌", "酉", "申", "子", "亥", "卯", "寅"],
                "戊": ["辰戌", "丑未", "申", "酉", "亥", "子", "寅", "卯", "巳", "午"], "己": ["丑未", "辰戌", "酉", "申", "子", "亥", "卯", "寅", "午", "巳"]}


def test_branch_main_stem_ten_gods_p17():
    for day, cols in BRANCH_TABLE.items():
        for i, branches in enumerate(cols):
            for br in branches:
                main = bazi.HIDDEN_STEMS[BR[br]][0]
                assert bazi.ten_god(ST[day], main) == TEN[i], (day, br)


def test_hidden_stem_sets_pp7_8():
    # 藏干 per branch as printed in the per-day-stem tables (set comparison; the book's listing order differs from ours)
    book = {"子": "癸", "丑": "癸己辛", "寅": "丙甲戊", "卯": "乙", "辰": "乙戊癸", "巳": "戊丙庚", "午": "丁己", "未": "乙己丁",
            "申": "戊庚壬", "酉": "辛", "戌": "辛戊丁", "亥": "壬甲"}
    for br, stems in book.items():
        assert set(bazi.HIDDEN_STEMS[BR[br]]) == {ST[c] for c in stems}, br
