"""DEEP-BAZI-2 (2026-10-23): the 八字真宗 judgements of pp.50-65 in data/bazi_deep/pack_zz_kin.json, read by tvbt.bazi_deep.kin.
  - every rule's printed words stand in the committed text layer of its page (data/bazi_deep/mined/zz_pNN.txt), and that text layer is the
    PDF's own when the PDF is on this machine;
  - the facts reproduce the manual's own worked examples (pp.50-53, 58): 财流入日主, 官流入日主, the pillar left of the Quan pillar (左柱),
    its strength (坐下通根) and the 无根 the examples name;
  - the owner chart (09/01/2002 04:30 nam): Tài strong and not flowing into the day master -> tài vận bình thường (p.50 断语条件 2), the work
    field read at the pillar left of the Quan pillar (the day pillar), not the hour pillar."""
import glob
import json
import os
import re
import unicodedata

import pytest

from tvbt.bazi_deep import kin, pipeline
from tvbt.bazi_deep.model import ChartView
from tvbt.bazi_deep.profile import DATA
from tvbt.knowledge.schema import validate_pack

MINED = DATA / "mined"
norm = lambda t: re.sub(r"\s+", "", unicodedata.normalize("NFC", t))


def page_text(page: str, book: str = "zz") -> str:
    n = int(page.removeprefix("p."))
    return norm((MINED / f"{book}_p{n}.txt").read_text("utf-8"))


def test_pack_is_valid_and_every_rule_has_its_words():
    rules, sources, meta = kin.pack()
    assert validate_pack(rules, sources, {"bazi.*", "chart.*"}) == []
    assert {r.id for r in rules} == set(meta)
    for r in rules:
        m = meta[r.id]
        assert norm(m["quote"]) in page_text(m["page"], m.get("book", "zz")), (r.id, m["quote"])
        assert m["topic"] in {"wealth", "work", "rank", "parents", "marriage", "siblings", "year", "character",
                              "children", "study", "fortune", "yong"}           # the last four: DEEP-3 (2026-10-24)
        # DEEP-3 HARSH rules (a printed verdict on morality / intelligence, a slur on a spouse) keep their checked quote but stay draft
        assert r.reviewStatus == ("draft" if m.get("harsh") else "verified"), r.id


@pytest.mark.parametrize("book,pattern", [("zz", "*真宗*.pdf"), ("ttt", "Trích Thiên Tủy.pdf")])
def test_mined_pages_are_the_pdf_text_layer(book, pattern):
    pdfs = sorted(glob.glob(os.path.expanduser(f"~/Downloads/{pattern}")))
    if not pdfs:
        pytest.skip(f"{pattern} not on this machine")
    pymupdf = pytest.importorskip("pymupdf")
    d = pymupdf.open(pdfs[0])
    for f in MINED.glob(f"{book}_p*.txt"):
        n = int(f.stem.removeprefix(f"{book}_p"))
        assert norm(f.read_text("utf-8")) == norm(d[n - 1].get_text()), f.name


def _kin(name: str, gender: str = "male"):
    v = ChartView.from_names(name, gender=gender)
    return kin.natal(v, pipeline.analyse(v)["strength_after"].get("tvh"))


def test_book_examples_flow_into_the_day_master():
    # p.50 example 1: "此造申金正财生子水七杀，而子水七杀生卯木偏印，此为财流入日主"
    assert _kin("Mậu Thân / Giáp Tý / Đinh Mão / Nhâm Dần")["facts"]["bazi.k.tai_flow"] is True
    # p.51 example 3: "此造财星虽旺，但未流入日主"
    k = _kin("Quý Hợi / Mậu Ngọ / Quý Tỵ / Đinh Tỵ")
    assert k["facts"]["bazi.k.tai_flow"] is False and "Tai" in k["facts"]["bazi.k.vuong"]
    assert "BT_ZZK_W24" in [f["rule_id"] for f in k["findings"]]
    # p.53 example 3: "七杀虽无根，但有生，又生月干印星，谓'官旺流入日主'"
    k = _kin("Canh Dần / Quý Mùi / Giáp Tuất / Mậu Tuất")
    assert k["facts"]["bazi.k.quan_flow"] is True and k["facts"]["bazi.k.quan_trans_rooted"] is False
    # p.58 example 2: "此造正财自坐墓库，但未流入日主（天干金不生异柱地支水）"
    assert _kin("Tân Sửu / Kỷ Hợi / Bính Ngọ / Mậu Tuất")["facts"]["bazi.k.tai_flow"] is False


def test_book_examples_left_pillar():
    # p.53 example 1: Quan (酉) in the month -> the left pillar is the year: "左柱（年柱）天干劫财为自由业 ... 甲坐下通根旺效益好"
    k = _kin("Giáp Dần / Quý Dậu / Ất Hợi / Nhâm Ngọ")
    assert k["detail"]["work"]["left"] == "year" and k["facts"]["bazi.k.work_group"] == "Ti" and k["facts"]["bazi.k.work_strong"] is True
    assert {"BT_ZZK_OG_TI", "BT_ZZK_O06A"} <= {f["rule_id"] for f in k["findings"]}
    # p.53 example 2: Quan (卯) in the year -> the left pillar is the hour: "左柱气弱，丙火印弱"
    k = _kin("Tân Mão / Canh Tý / Mậu Tý / Bính Thìn")
    assert k["detail"]["work"]["left"] == "hour" and k["facts"]["bazi.k.work_group"] == "An" and k["facts"]["bazi.k.work_strong"] is False
    assert {"BT_ZZK_OG_AN", "BT_ZZK_O06B"} <= {f["rule_id"] for f in k["findings"]}


def test_book_example_rootless_stem():
    # p.51 example 2: "此造偏财透干无根无生" — 戊 has 戊 only as 申's residual qi and in 辰 two pillars away
    c = kin.Chart(ChartView.from_names("Mậu Thân / Tân Dậu / Giáp Thìn / Nhâm Thân"), None)
    assert c.rooted(("year", "stem")) is False


def test_owner_chart_2002():
    k = _kin("Tân Tỵ / Tân Sửu / Đinh Sửu / Nhâm Dần")
    ids = {f["rule_id"] for f in k["findings"]}
    # Tài strong (the largest group) and no Ấn at the day branch, month stem or hour stem: not flowing -> ordinary (p.50 断语条件 2)
    assert "BT_ZZK_W24" in ids and "BT_ZZK_W25" not in ids
    # the Quan is the hour stem 壬, so the work pillar is the day pillar (not the hour pillar the old HOUR_GROUP rules read)
    assert k["detail"]["work"]["left"] == "day" and "BT_ZZK_OS_DINH" in ids and not any(i.startswith("BT_ZZK_OG_") for i in ids)
    # 日主入日支墓 (p.57 #24): Đinh at Sửu is Mộ
    assert "BT_ZZK_M24M" in ids
    assert all(f["cause"] and "{" not in f["cause"] for f in k["findings"])


def test_book_internal_conflicts_are_kept_apart():
    """pairs of judgements that would contradict each other never fire together (the conditions in tools/build_bazi_kin_pack.py)"""
    pairs = [("BT_ZZK_R03", "BT_ZZK_R08"), ("BT_ZZK_R03", "BT_ZZK_R06"), ("BT_ZZK_W13", "BT_ZZK_W14"), ("BT_ZZK_W05", "BT_ZZK_W06"), ("BT_ZZK_S27", "BT_ZZK_S28"),
             ("BT_ZZK_W24", "BT_ZZK_W25"), ("BT_ZZK_R01", "BT_ZZK_R08"), ("BT_ZZK_Y22", "BT_ZZK_Y23"),
             ("BT_TVHK_W08", "BT_TVHK_W11"), ("BT_TVHK_H01", "BT_TVHK_H02"), ("BT_TVHK_S04", "BT_TVHK_S07"), ("BT_TTTK_QUY6", "BT_TTTK_TIEN4"), ("BT_TTTK_QUY1", "BT_TTTK_TIEN8"),
             # REVIEW-19 W6: combinations and the groups
             ("BT_TVHK_PT_TSS1", "BT_TVHK_PT_TSS2"), ("BT_TVHK_PT_TST3", "BT_TVHK_PT_TKQ"), ("BT_TVHK_G03", "BT_TVHK_W08"), ("BT_TVHK_G18", "BT_TVHK_W08"),
             ("BT_TVHK_G07", "BT_TVHK_W12"), ("BT_TVHK_G06", "BT_TVHK_W13"), ("BT_TVHK_PT_TKD1", "BT_TVHK_PT_TKD2"), ("BT_TVHK_G10", "BT_TVHK_G11"),
             ("BT_TVHK_PT_TPA1", "BT_TTTK_QUY6")]
    import itertools
    from tvbt.ganzhi import BRANCHES_VI, STEMS_VI
    pil = [f"{STEMS_VI[i % 10]} {BRANCHES_VI[i % 12]}" for i in range(60)]
    n = 0
    for a, b, c, d in itertools.islice(itertools.product(pil[::7], pil[::5], pil[::3], pil[::11]), 0, 1500):
        v = ChartView.from_names(f"{a} / {b} / {c} / {d}", gender="female")
        F, D = kin.natal_facts(v, pipeline.analyse(v, with_rules=False)["strength_after"].get("tvh"))
        ids = {f["rule_id"] for f in kin.fire(F, D["vars"])}
        for x, y in pairs:
            assert not ({x, y} <= ids), (v.name(), x, y)
        n += 1
    assert n > 1000


def test_natal_and_year_rules_fire_apart():
    """a year's facts carry the natal strength facts, but only the year judgements (topic 'year') are read there"""
    v = ChartView.from_names("Tân Tỵ / Tân Sửu / Đinh Sửu / Nhâm Dần", gender="male")
    tvh = pipeline.analyse(v)["strength_after"].get("tvh")
    nat = kin.natal(v, tvh, {"hi": ["Tỉ Kiếp"], "ky": ["Tài"], "yong": ["Tỉ Kiếp"]})
    y = kin.year(v, tvh, nat["facts"], 2, 6, (4, 10))
    assert all(f["topic"] == "year" for f in y["findings"]) and all(f["topic"] != "year" for f in nat["findings"])


def test_year_judgements_on_2002():
    from tvbt.api import BirthReq, chart_facts
    f = chart_facts(BirthReq(year=2002, month=1, day=9, hour=4, minute=30, gender="male", to_year=2026, dignity_school="khao_luan"))
    ys = {y["year"]: {x["rule_id"] for x in y["kin"]["findings"]} for y in f["bazi"]["deep"]["years"]}
    assert "BT_ZZK_Y14" in ys[2028]          # 申 fills the chart's void (丁丑 xun: 申酉) and carries Chính Tài
    assert "BT_ZZK_Y01" in ys[2027]          # 未 (a 库) clashes the 丑 of the month and day
