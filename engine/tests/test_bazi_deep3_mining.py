"""DEEP-3 Bát Tự mining (2026-10-24): the new page-checked knowledge.
  - every quote of hyky.json, thanh_pha.json and schools.json stands on its page (data/bazi_deep/mined/<book>_pN.txt) or in its web snapshot
    (data/sources_web/, book 'WEB:<id>', checked through tools/book_text.quote_on_page);
  - the element map of the five roles (Trích Thiên Tủy p.167) reproduces the page's own example;
  - the DEEP-3 rules of the kin packs fire on the books' own worked examples (TTT pp.101-106 chân thần, 八字真宗 p.29 日月合化 examples, a 正化 /
    妒合 / 鸳鸯合 chart), HARSH rules never fire, and pairs of opposite judgements on one condition never fire together;
  - dieu_hau_ctbg_draft.json: every cell read from the 穷通宝鉴 snapshot carries a quote that is in the snapshot."""
import json
import re
import sys
import unicodedata
from pathlib import Path

import pytest

from tvbt.bazi_deep import kin, pipeline
from tvbt.bazi_deep.model import ChartView
from tvbt.bazi_deep.profile import DATA

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import book_text  # noqa: E402

norm = lambda t: re.sub(r"\s+", "", unicodedata.normalize("NFC", t))


def _quotes(o, path=""):
    if isinstance(o, dict):
        if {"book", "page", "quote"} <= set(o) and isinstance(o["quote"], str):
            yield path, o
        for k, v in o.items():
            yield from _quotes(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _quotes(v, f"{path}[{i}]")


def _on_page(book: str, page: str, quote: str) -> bool:
    if book.startswith("WEB:"):
        return book_text.quote_on_page(book, page, quote)
    n = int(page.removeprefix("p."))
    return norm(quote) in norm((DATA / "mined" / f"{book}_p{n}.txt").read_text("utf-8"))


@pytest.mark.parametrize("name", ["hyky.json", "thanh_pha.json", "schools.json"])
def test_every_quote_is_on_its_page(name):
    d = json.loads((DATA / name).read_text("utf-8"))
    qs = list(_quotes(d))
    assert len(qs) > 10
    bad = [(p, o["book"], o["page"], o["quote"][:50]) for p, o in qs if not _on_page(o["book"], o["page"], o["quote"])]
    assert bad == []


def test_rule_ids_named_in_the_knowledge_files_exist():
    _, _, meta = kin.pack()
    for name in ("hyky.json", "thanh_pha.json", "schools.json"):
        text = (DATA / name).read_text("utf-8")
        for rid in set(re.findall(r"BT_(?:TTTK|TVHK|ZZK)_\w+\b(?!\*)", text)):
            assert rid in meta, (name, rid)


def test_role_map_reproduces_the_page_example():
    from tvbt.ganzhi import ELEMENTS, controls, generates
    rm = json.loads((DATA / "hyky.json").read_text("utf-8"))["role_map"]
    rel = {"dung_sinh": lambda d: next(e for e in ELEMENTS if generates(d, e)), "sinh_dung": lambda d: next(e for e in ELEMENTS if generates(e, d)),
           "dung_khac": lambda d: next(e for e in ELEMENTS if controls(d, e)), "khac_dung": lambda d: next(e for e in ELEMENTS if controls(e, d))}
    ex = rm["example"]
    for case in ("du", "thieu"):
        assert {role: rel[r](ex["dung"]) for role, r in rm[case].items()} == ex[case]
    # every element gets four distinct roles
    for d in ELEMENTS:
        for case in ("du", "thieu"):
            assert len({rel[r](d) for r in rm[case].values()} | {d}) == 5


_cap = {}


def _run(name: str, gender: str = "male"):
    orig = kin.natal

    def wrap(view, tvh, yong=None):
        r = orig(view, tvh, yong)
        _cap["facts"] = r["facts"]
        return r
    kin.natal = wrap
    try:
        s = pipeline.prose_summary(ChartView.from_names(name, gender=gender), [], [])
    finally:
        kin.natal = orig
    return _cap["facts"], {f["rule_id"] for f in s["kin"]["findings"]}


def test_ttt_chan_than_examples():
    # p.105 #195: "mừng nhất dần mộc chân thần đương lệnh, can giờ thấu lộ ất mộc nguyên thần. Dần thân xung nhau, gọi là có bệnh"
    _, ids = _run("Nhâm Thân / Nhâm Dần / Bính Tý / Ất Mùi")
    assert {"BT_TTTK_CT01", "BT_TTTK_CT02"} <= ids
    # p.105-106 #196: "can giờ giáp mộc, chân thần phát lộ. Hiềm nghi, năm ngộ canh thân, xung khắc giáp dần ... gọi là giả loạn chân"
    _, ids = _run("Canh Thân / Mậu Dần / Nhâm Tý / Giáp Thìn")
    assert {"BT_TTTK_CT01", "BT_TTTK_CT02"} <= ids
    # p.101 #188: "Mừng quan tinh đương lệnh, thấu mà sanh tài"
    _, ids = _run("Quý Dậu / Giáp Tý / Bính Dần / Ất Mùi")
    assert "BT_TTTK_CT01" in ids


def test_zz_day_month_combination_examples():
    # p.29 例 男命-月辛巳、日丙午 → 优型: "该男得之贤妻，妻子助夫旺财"
    f, ids = _run("Giáp Tý / Tân Tỵ / Bính Ngọ / Giáp Ngọ", "male")
    assert f["bazi.k.zz_hh"] == "uu" and "BT_ZZK_HH1" in ids
    # p.29 例 女命-月戊子，日癸酉 → 劣型 (HARSH: the fact is computed, the rule stays draft and never fires)
    f, ids = _run("Giáp Tý / Mậu Tý / Quý Dậu / Giáp Dần", "female")
    assert f["bazi.k.zz_hh"] == "liet" and not any(i.startswith("BT_ZZK_HH") for i in ids)


def test_zz_stem_combinations():
    f, ids = _run("Giáp Thìn / Kỷ Mùi / Bính Thân / Mậu Tuất")        # 甲己 on 辰未, month 未: 正化 土
    assert f["bazi.k.zz_zhenghua"] == ["Thổ"] and {"BT_ZZK_HZ0", "BT_ZZK_HZ1"} <= ids
    f, ids = _run("Giáp Tý / Kỷ Sửu / Ất Mão / Bính Tý")              # 甲己乙 consecutive: 妒合; 甲子·己丑: 鸳鸯合 (土, 土)
    assert f["bazi.k.zz_duhe"] is True and f["bazi.k.zz_yuanyang"] == ["year_month"] and {"BT_ZZK_DH1", "BT_ZZK_YY1"} <= ids
    f, _ = _run("Giáp Tý / Bính Dần / Kỷ Sửu / Giáp Tý")
    assert f["bazi.k.zz_duhe"] is False


def test_harsh_rules_are_draft_and_never_fire():
    rules, _, meta = kin.pack()
    harsh = {i for i, m in meta.items() if m.get("harsh")}
    assert harsh and all(r.reviewStatus == "draft" for r in rules if r.id in harsh)
    import itertools
    from tvbt.ganzhi import BRANCHES_VI, STEMS_VI
    pil = [f"{STEMS_VI[i % 10]} {BRANCHES_VI[i % 12]}" for i in range(60)]
    for a, b, c, d in itertools.islice(itertools.product(pil[::7], pil[::5], pil[::3], pil[::11]), 0, 300):
        _, ids = _run(f"{a} / {b} / {c} / {d}", "female")
        assert not ids & harsh


def test_hour_pillar_children_rules():
    f, ids = _run("Giáp Tý / Bính Dần / Kỷ Sửu / Giáp Tý")              # Kỷ day, hour branch 子 = Thiên Tài
    assert f["bazi.k.hour_branch_god"] == "Thiên Tài" and "BT_TVHK_K02" in ids


DEEP3_PAIRS = [("BT_TTTK_CC02", "BT_TTTK_CC03"), ("BT_TTTK_DUC1", "BT_TTTK_DUC2"), ("BT_TTTK_HK06", "BT_TTTK_HK07"), ("BT_TVHK_K07", "BT_TVHK_K08"),
               ("BT_TVHK_D09", "BT_TVHK_F42")]


def test_opposite_judgements_on_one_condition_never_fire_together():
    import itertools
    from tvbt.ganzhi import BRANCHES_VI, STEMS_VI
    pil = [f"{STEMS_VI[i % 10]} {BRANCHES_VI[i % 12]}" for i in range(60)]
    for a, b, c, d in itertools.islice(itertools.product(pil[::7], pil[::5], pil[::3], pil[::11]), 0, 600):
        _, ids = _run(f"{a} / {b} / {c} / {d}", "male")
        for x, y in DEEP3_PAIRS:
            assert not ({x, y} <= ids), (a, b, c, d, x, y)


def test_ctbg_snapshot_cells_carry_their_quote():
    d = json.loads((DATA / "dieu_hau_ctbg_draft.json").read_text("utf-8"))
    snap = d.get("snapshot")
    if not snap:
        pytest.skip("no 穷通宝鉴 cells read yet")
    n = 0
    for stem, row in snap["cells"].items():
        for br, c in row.items():
            if c.get("quote"):
                assert book_text.quote_on_page("WEB:CTBG", c["chapter"], c["quote"]), (stem, br)
                n += 1
    assert n >= 100
    # a cell is 'checked' only when the snapshot's ordered stems equal the memory draft's
    for key in d["checked_cells"]:
        stem, br = key.split("/")
        assert "".join(snap["cells"][stem][br]["yong"]) == d["cells"][stem][br]
