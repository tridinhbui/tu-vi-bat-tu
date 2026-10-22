"""Golden values transcribed from 八字真宗 (SRC_BAZI_ZHENZONG), PDF pp.19-25, 35 — independent of our code."""
from tvbt import bazi
from tvbt.calendar_core import BirthInput, normalize
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
    # 「干冲克」 prints ten pairs, each stem against the one seven places on; three of them are 克, the rest 冲 (audit BZ-1)
    printed = {"甲庚": "khắc", "乙辛": "xung", "丙壬": "xung", "丁癸": "xung", "戊甲": "khắc", "己乙": "xung", "庚丙": "xung", "辛丁": "xung",
               "壬戊": "xung", "癸己": "khắc"}
    assert {frozenset(ST[c] for c in pair): kind for pair, kind in printed.items()} == bazi.STEM_CLASH_KIND
    assert set(bazi.STEM_CLASH) == set(bazi.STEM_CLASH_KIND)


def test_bazi_deep_uses_the_ten_pair_stem_table_p20():
    """bazi_deep (natal interactions and the luck/year overlay) reads the same ten 干冲克 pairs as production (audit BZ-1)."""
    from tvbt.bazi_deep import interact, temporal_deep
    from tvbt.bazi_deep.model import ChartView
    assert not hasattr(bazi, "STEM_CLASH_LEGACY4")
    # 庚 year against 丙 hour: 庚丙冲 is one of the six pairs the old four-pair table lacked
    v = ChartView.from_names("Canh Tý / Bính Dần / Mậu Ngọ / Bính Thìn")
    kinds = {(tuple(r["pillars"]), r.get("subtype")) for r in interact.detect(v) if r["kind"] == "stem_clash"}
    assert {(("year", "month"), "xung"), (("year", "hour"), "xung")} <= kinds
    assert temporal_deep.STEM_CLASH is bazi.STEM_CLASH_KIND


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


def test_day_pillar_nap_am_table_pp31_32():
    """The book lists each nạp âm with its first day pillar (PDF pp.31-32): our computed nạp âm names must agree for all 30 rows."""
    import json
    from tvbt.ganzhi import cycle_index, nap_am_name
    from tvbt.knowledge.loader import DATA
    pillars = json.loads((DATA / "pack_bazi_napam.json").read_text("utf-8"))["pillars"]
    assert len(pillars) == 30
    for pil, vi in pillars.items():
        assert nap_am_name(ST[pil[0]], BR[pil[1]]) == vi, pil
        # the paired next pillar (乙丑 for 甲子 ...) shares the nạp âm
        n = cycle_index(ST[pil[0]], BR[pil[1]])
        assert nap_am_name((n + 1) % 10, (n + 1) % 12) == vi


def test_napam_rule_fires_for_day_pillar():
    from tvbt.knowledge.loader import load_all
    from tvbt.reasoning import engine, facts
    rules, srcs = load_all()
    c = bazi.compute(normalize(BirthInput(2000, 1, 1, 12, 0, "Asia/Ho_Chi_Minh", "male")))      # Mậu Ngọ day -> Thiên Thượng Hỏa
    f = facts.bazi_facts(c)
    assert f["chart"]["bazi.day_nap_am"] == "Thiên Thượng Hỏa"
    res = engine.run(rules, srcs, f, system="bat_tu")
    assert "bt_nap_am_ngay_thien_thuong_hoa" in {x.claim for x in res.findings}


MING = ["卯寅丑子亥戌酉申未午巳辰", "寅丑子亥戌酉申未午巳辰卯", "丑子亥戌酉申未午巳辰卯寅", "子亥戌酉申未午巳辰卯寅丑", "亥戌酉申未午巳辰卯寅丑子",
        "戌酉申未午巳辰卯寅丑子亥", "酉申未午巳辰卯寅丑子亥戌", "申未午巳辰卯寅丑子亥戌酉", "未午巳辰卯寅丑子亥戌酉申",
        "午巳辰卯寅丑子亥戌酉申未", "巳辰卯寅丑子亥戌酉申未午", "辰卯寅丑子亥戌酉申未午巳"]
SHEN = ["卯辰巳午未申酉戌亥子丑寅", "辰巳午未申酉戌亥子丑寅卯", "巳午未申酉戌亥子丑寅卯辰", "午未申酉戌亥子丑寅卯辰巳", "未申酉戌亥子丑寅卯辰巳午",
        "申酉戌亥子丑寅卯辰巳午未", "酉戌亥子丑寅卯辰巳午未申", "戌亥子丑寅卯辰巳午未申酉", "亥子丑寅卯辰巳午未申酉戌",
        "子丑寅卯辰巳午未申酉戌亥", "丑寅卯辰巳午未申酉戌亥子", "寅卯辰巳午未申酉戌亥子丑"]


def test_ming_gong_shen_gong_tables_pp37_38():
    month_branches = [BR[c] for c in "寅卯辰巳午未申酉戌亥子丑"]       # columns: month 1..12
    for hb in range(12):                                              # rows: hour 子..亥
        for col, mb in enumerate(month_branches):
            assert bazi.ming_gong_branch(mb, hb) == BR[MING[hb][col]], ("ming", hb, col)
            assert bazi.shen_gong_branch(mb, hb) == BR[SHEN[hb][col]], ("shen", hb, col)


def test_thai_yuan_and_kong_wang_tables():
    assert bazi.thai_yuan(ST["丙"], BR["申"]) == (ST["丁"], BR["亥"])             # worked example p.20: 丙申 month -> 丁亥
    assert bazi.thai_yuan(ST["甲"], BR["寅"]) == (ST["乙"], BR["巳"])             # 胎元速查表 p.36, row 甲月 col 正月
    assert bazi.thai_yuan(ST["癸"], BR["丑"]) == (ST["甲"], BR["辰"])             # row 癸月 col 十二月
    # 空亡速查表 p.37 (stem column, branch row -> the two void branches)
    for (stem, br), want in {("甲", "子"): "戌亥", ("甲", "戌"): "申酉", ("丙", "子"): "申酉", ("戊", "子"): "午未", ("庚", "子"): "辰巳",
                             ("壬", "子"): "寅卯", ("乙", "丑"): "戌亥", ("癸", "亥"): "子丑", ("甲", "辰"): "寅卯"}.items():
        assert set(bazi.kong_wang(ST[stem], BR[br])) == {BR[c] for c in want}, (stem, br)
