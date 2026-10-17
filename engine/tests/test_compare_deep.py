"""Two-chart comparison, multi-layer (compare_deep + compare_tuvi). Facts only: these tests pin the tables, the tiering,
the experimental gate and the independence of the Tử Vi side. Regenerate the golden file with:  python tests/test_compare_deep.py --regen"""
import ast
import json
import sys
from pathlib import Path

import pytest

from tvbt import compare, compare_deep as cd, compare_tuvi
from tvbt.api import BirthReq, _compute
from tvbt.bazi_deep.model import ChartView

ROOT = Path(__file__).resolve().parent
GOLDEN = ROOT / "golden" / "compare_deep_expected.json"
PAIRS = {
    "tôi_mẹ": (dict(year=1990, month=5, day=17, hour=10, minute=30, gender="male"), dict(year=1962, month=3, day=9, hour=6, minute=0, gender="female")),
    "tôi_1985": (dict(year=1990, month=5, day=17, hour=10, minute=30, gender="male"), dict(year=1985, month=11, day=3, hour=8, minute=0, gender="female")),
    "cùng_một_người": (dict(year=1990, month=5, day=17, hour=10, minute=30, gender="male"),) * 2,
    "tôi_tòng_tài": (dict(year=1990, month=5, day=17, hour=10, minute=30, gender="male"), dict(year=1955, month=1, day=21, hour=14, minute=0, gender="male")),
}


def run(a: dict, b: dict, experimental: bool = False) -> dict:
    na, ba, ta = _compute(BirthReq(**a))
    nb, bb, tb = _compute(BirthReq(**b))
    return compare.compare_full(na, ba, ta, a["gender"], nb, bb, tb, b["gender"], experimental)["v2"]


def view(text: str) -> ChartView:
    return ChartView.from_names(text)


def rel_kinds(items):
    return sorted((i["kind"], i["data"]["members"][0]["slot"], i["data"]["members"][1]["slot"]) for i in items if i["layer"] == "bazi" and "members" in i["data"])


def summary(r: dict) -> dict:
    return {"default_ids": sorted(i["id"] for i in r["items"]), "tiers": {t: len(v["ids"]) for t, v in r["tiers"].items()},
            "strength": {o: [r["structure"][o]["strength"]["side"], r["structure"][o]["strength"]["reason"], round(r["structure"][o]["strength"]["own_share"], 3)] for o in "ab"}}


# ---------------------------------------------------------------- rule file and sources
def test_every_rule_has_a_status_and_verified_rules_have_a_known_source():
    for rid, r in cd.RULES.items():
        assert r["status"] in ("verified", "partial", "draft"), rid
        assert r["text"] and r["title"], rid
        assert r["evidence"] in ("calc", "sourced", "hypothesis"), rid
        assert (r["evidence"] == "hypothesis") == (r["status"] == "draft"), rid          # a draft rule is always a hypothesis, and only those
        if r["status"] != "draft" and r["evidence"] == "sourced":
            assert r["source"] in cd.SOURCES and cd.SOURCES[r["source"]]["verified"] and r["locator"], rid


def test_balance_rule_text_matches_the_dungthan_table():
    d = json.loads((ROOT.parent / "data" / "bazi_deep" / "tvh_dungthan.json").read_text("utf-8"))["rows"]
    ok = sum(1 for r in d if set(r["yong"]) <= ({"Ti", "An"} if r["dm"] == "weak" else {"ThucThuong", "Tai", "QuanSat"}))
    assert (len(d), ok) == (51, 50)
    assert "51 dòng" in cd.RULES["CMP_BALANCE"]["text"] and "50 dòng" in cd.RULES["CMP_BALANCE"]["text"]
    assert cd.RULES["CMP_BALANCE"]["status"] == "draft"


# ---------------------------------------------------------------- relations from the tables
def test_cross_relations_known_pairs():
    a, b = view("Canh Ngọ / Tân Tỵ / Nhâm Ngọ / Ất Tỵ"), view("Nhâm Dần / Quý Mão / Bính Ngọ / Tân Mão")
    items = cd._relation_items(cd._tokens("a", a), cd._tokens("b", b))
    kinds = {(i["kind"], i["data"]["members"][0]["slot"], i["data"]["members"][1]["slot"]) for i in items}
    assert ("stem_combine", "month", "day") in kinds          # Tân (A) + Bính (B)
    assert ("stem_clash", "day", "day") in kinds              # Nhâm + Bính
    assert ("stem_clash", "hour", "hour") in kinds            # Ất + Tân
    assert ("branch_destroy", "day", "month") in kinds        # Ngọ + Mão phá
    assert ("branch_harm", "month", "year") in kinds          # Tỵ + Dần hại
    assert ("branch_self_penalty", "day", "day") in kinds     # Ngọ + Ngọ
    assert all(i["data"]["members"][0]["owner"] == "a" and i["data"]["members"][1]["owner"] == "b" for i in items)
    assert not any(i["kind"] == "stem_combine" and i["data"]["table_element"] != "Thủy" for i in items)


@pytest.mark.parametrize("pa,pb,kind", [("Giáp Tý", "Kỷ Sửu", "stem_combine"), ("Giáp Tý", "Canh Ngọ", "stem_clash"), ("Giáp Tý", "Kỷ Mão", "branch_penalty")])
def test_single_pillar_tables(pa, pb, kind):
    a, b = view(f"{pa} / {pa} / {pa} / {pa}"), view(f"{pb} / {pb} / {pb} / {pb}")
    assert any(i["kind"] == kind for i in cd._relation_items(cd._tokens("a", a), cd._tokens("b", b)))


def test_groups_need_both_people_and_do_not_double_count():
    # A: Thân + Tý; B: Thìn  -> full tam hợp Thủy, and no semi group inside it
    a, b = view("Giáp Thân / Giáp Tý / Giáp Thân / Giáp Tý"), view("Canh Thìn / Canh Thìn / Canh Thìn / Canh Thìn")
    g = cd._groups(cd._tokens("a", a), cd._tokens("b", b))
    kinds = {i["kind"] for i in g}
    assert "branch_triad" in kinds and "branch_semi_triad" not in kinds
    assert all({m["owner"] for m in i["data"]["members"]} == {"a", "b"} for i in g)
    # a triad completed inside ONE chart is natal, not a comparison fact
    solo = cd._groups(cd._tokens("a", view("Giáp Thân / Giáp Tý / Giáp Thìn / Giáp Thân")), cd._tokens("b", view("Canh Ngọ / Canh Ngọ / Canh Ngọ / Canh Ngọ")))
    assert not any(i["kind"] == "branch_triad" for i in solo)


def test_semi_triad_and_school_dependent_items():
    a, b = view("Giáp Thân / Giáp Thân / Giáp Thân / Giáp Thân"), view("Canh Tý / Canh Tý / Canh Tý / Canh Tý")
    g = cd._groups(cd._tokens("a", a), cd._tokens("b", b))
    assert g and all(i["kind"] == "branch_semi_triad" and i["rule"] == "CMP_SEMI_TRIAD" and i["school_dependent"] for i in g)
    a2, b2 = view("Giáp Thân / Giáp Thân / Giáp Thân / Giáp Thân"), view("Canh Thìn / Canh Thìn / Canh Thìn / Canh Thìn")
    assert all(i["rule"] == "CMP_CUNG_TRIAD" and i["experimental"] for i in cd._groups(cd._tokens("a", a2), cd._tokens("b", b2)))
    a3, b3 = view("Giáp Dần / Giáp Dần / Giáp Dần / Giáp Dần"), view("Tân Tỵ / Tân Tỵ / Tân Tỵ / Tân Tỵ")
    assert all(i["rule"] == "CMP_BAN_HINH" and i["experimental"] for i in cd._groups(cd._tokens("a", a3), cd._tokens("b", b3)))


# ---------------------------------------------------------------- Thập Thần both ways
def test_ten_god_two_way_matches_the_table():
    from tvbt.bazi import ten_god
    r = run(*PAIRS["tôi_mẹ"])
    a_sees_b = next(i for i in r["items"] if i["id"] == "bz.ten_god.a_sees_b")["data"]
    b_sees_a = next(i for i in r["items"] if i["id"] == "bz.ten_god.b_sees_a")["data"]
    nham, binh = 8, 2   # stems
    assert [x for x in a_sees_b["rows"] if x["kind"] == "stem" and x["is_day_master"]][0]["ten_god"] == ten_god(nham, binh) == "Thiên Tài"
    assert [x for x in b_sees_a["rows"] if x["kind"] == "stem" and x["is_day_master"]][0]["ten_god"] == ten_god(binh, nham) == "Thất Sát"
    assert sum(a_sees_b["counts"].values()) == len(a_sees_b["rows"])


# ---------------------------------------------------------------- structure before interactions
def test_structure_is_per_chart_and_borderline_is_not_decided():
    r = run(*PAIRS["tôi_mẹ"])
    a, b = r["structure"]["a"], r["structure"]["b"]
    assert (a["strength"]["side"], a["strength"]["reason"], a["strength"]["decided"]) == (None, "borderline", False)   # 38.4% is within 3 points of 40%: no side at all
    assert (b["strength"]["side"], b["strength"]["reason"], b["strength"]["decided"]) == ("vượng", "ok", True)
    assert a["month"]["branch"] == "Tỵ" and b["month"]["branch"] == "Mão" and a["has_root"] is False and b["has_root"] is True
    ids = {i["id"] for i in r["items"]}
    assert "ins.border.a" in ids and "ins.border.b" not in ids
    ex = run(*PAIRS["tôi_mẹ"], experimental=True)
    assert not any(i["id"] == "bz.balance.support.a" for i in ex["items"])               # no direction for a borderline chart
    assert any(i["id"] == "bz.balance.support.b" for i in ex["items"])


def side_of(text: str, gender: str = "male"):
    """A Side built from four pillars only (no birth time): enough for the structure and the Bát Tự relations."""
    from tvbt.bazi import BaziChart  # noqa: F401
    _, bz, tv = _compute(BirthReq(year=1990, month=5, day=17, hour=10, minute=30, gender=gender))
    return cd.Side(bz, ChartView.from_names(text), tv)


def test_special_structures_are_never_forced_into_vuong_or_nhuoc():
    for text in ("Nhâm Tý / Quý Sửu / Bính Tý / Canh Tý",        # Tòng Sát (Thiệu Vĩ Hoa example)
                 "Mậu Tuất / Bính Thìn / Ất Mùi / Bính Tuất",    # Tòng Tài
                 "Mậu Thân / Tân Dậu / Canh Tuất / Ất Dậu"):     # Tòng Cách (chuyên vượng)
        s = cd.structure("a", side_of(text))
        assert s["special"], text
        assert s["strength"]["side"] is None and s["strength"]["decided"] is False and s["strength"]["reason"] == "special"
    plain = cd.structure("a", side_of("Giáp Tý / Bính Dần / Giáp Tuất / Canh Ngọ"))
    assert plain["special"] == []


def test_special_chart_gets_an_insufficient_item_and_no_balance_direction():
    a = side_of("Nhâm Tý / Quý Sửu / Bính Tý / Canh Tý")
    b = side_of("Giáp Tý / Bính Dần / Giáp Tuất / Canh Ngọ", "female")
    r = cd.analyse(a, b, experimental=True)
    ids = {i["id"] for i in r["items"]}
    assert "ins.special.a" in ids and "bz.balance.support.a" not in ids and "bz.balance.limit.a" not in ids
    it = next(i for i in r["items"] if i["id"] == "ins.special.a")
    assert it["tier"] == "insufficient" and it["rule"] == "CMP_SPECIAL" and it["status"] == "partial"
    assert "không nói Nhật Chủ A vượng hay nhược" in it["plain"]


def test_missing_data_is_reported_not_guessed(monkeypatch):
    def boom(_v):
        raise KeyError("thiếu tháng sinh")
    monkeypatch.setattr(cd.tvh_score, "score", boom)
    a = side_of("Nhâm Tý / Quý Sửu / Bính Tý / Canh Tý")
    b = side_of("Giáp Tý / Bính Dần / Giáp Tuất / Canh Ngọ", "female")
    r = cd.analyse(a, b, experimental=True)
    st = r["structure"]["a"]["strength"]
    assert st["reason"] == "missing" and st["side"] is None and "thiếu tháng sinh" in r["structure"]["a"]["error"]
    ids = {i["id"] for i in r["items"]}
    assert {"ins.missing.a", "ins.missing.b"} <= ids and not any(i.startswith("bz.balance") for i in ids)
    assert any(i["kind"].startswith("stem_") or i["kind"].startswith("branch_") for i in r["items"])      # relations still reported


def test_evidence_classes_keep_hypotheses_out_of_sourced_and_calc():
    r = run(*PAIRS["tôi_mẹ"], experimental=True)
    by = lambda ev: {i["kind"] for i in r["items"] if i["evidence"] == ev}
    assert {"balance", "role", "season_other"} <= by("hypothesis")
    assert not (by("calc") | by("sourced")) & {"balance", "role", "element_fill", "season_other", "reinforce", "disperse"}
    assert {"stem_combine", "stem_clash", "branch_destroy", "ten_god_view"} <= by("sourced")
    assert {"placement", "geometry", "element_count"} <= by("calc")
    d = run(*PAIRS["tôi_mẹ"])
    assert {i["evidence"] for i in d["items"]} <= {"calc", "sourced"}
    assert {x["id"] for x in d["sources"]} >= {"SRC_BAZI_ZHENZONG", "SRC_TVH_DIEM", "SRC_THUC_HANH"}


def test_v1_response_fields_are_unchanged():
    na, ba, ta = _compute(BirthReq(**PAIRS["tôi_mẹ"][0])); nb, bb, tb = _compute(BirthReq(**PAIRS["tôi_mẹ"][1]))
    full = compare.compare_full(na, ba, ta, "male", nb, bb, tb, "female")
    old = compare.compare(ba, bb)
    assert {k: v for k, v in full.items() if k != "v2"} == old
    assert set(old) == {"a", "b", "ten_god_of_b_for_a", "ten_god_of_a_for_b", "element_link", "day_master_stems", "day_branches", "note"}


# ---------------------------------------------------------------- tiers and the experimental gate
def test_default_mode_keeps_every_limitation_visible():
    ids = {i["id"] for i in run(*PAIRS["tôi_mẹ"])["items"]}
    assert {"ins.yongshen", "ins.time", "ins.tuvi", "ins.hoa", "ins.border.a"} <= ids      # limits are never hidden with the drafts


def test_real_special_chart_is_not_forced_to_a_side():
    r = run(*PAIRS["tôi_tòng_tài"], experimental=True)
    b = r["structure"]["b"]
    assert b["special"][0]["name"] == "Tòng Tài (TVH)" and b["strength"]["side"] is None and b["strength"]["reason"] == "special"
    assert "ins.special.b" in {i["id"] for i in r["items"]} and not any(i["id"].startswith("bz.balance") and i["id"].endswith(".b") for i in r["items"])


@pytest.mark.parametrize("key", list(PAIRS))
def test_default_mode_contains_no_draft_item_and_experimental_is_a_superset(key):
    d, e = run(*PAIRS[key]), run(*PAIRS[key], experimental=True)
    ids = [i["id"] for i in d["items"]]
    assert len(ids) == len(set(ids))
    assert not any(i["status"] == "draft" or i["experimental"] for i in d["items"])
    assert set(ids) <= {i["id"] for i in e["items"]}
    assert d["hidden_experimental"] == len(e["items"]) - len(d["items"]) > 0
    assert all(i["rule"] in d["rules"] for i in d["items"])
    assert all(i["status"] == "draft" for i in e["items"] if i["experimental"])


@pytest.mark.parametrize("key", list(PAIRS))
def test_support_and_limit_tiers_are_empty_until_a_verified_rule_exists(key):
    d = run(*PAIRS[key])
    assert d["tiers"]["support"]["ids"] == [] and d["tiers"]["limit"]["ids"] == []
    assert d["tiers"]["insufficient"]["ids"] and d["tiers"]["direct"]["ids"]
    e = run(*PAIRS[key], experimental=True)
    for i in e["items"]:
        if i["tier"] in ("support", "limit"):
            assert i["experimental"]


def test_every_item_points_to_a_rule_with_source_info():
    r = run(*PAIRS["tôi_mẹ"], experimental=True)
    for i in r["items"]:
        rule = r["rules"][i["rule"]]
        assert rule["status"] == i["status"] and rule["evidence"] == i["evidence"]
        if i["evidence"] == "sourced":
            assert rule["source"] and rule["source"]["verified"]
        assert (i["evidence"] == "hypothesis") == i["experimental"]


# ---------------------------------------------------------------- no score, no verdict
def _keys(o):
    if isinstance(o, dict):
        for k, v in o.items():
            yield k
            yield from _keys(v)
    elif isinstance(o, list):
        for x in o:
            yield from _keys(x)


def test_no_score_or_verdict_anywhere():
    r = run(*PAIRS["tôi_mẹ"], experimental=True)
    banned = {"score", "percent", "match", "compat", "verdict", "rating", "good", "bad", "tốt", "xấu"}
    assert not [k for k in _keys(r) if any(b in k.lower() for b in banned)]
    text = json.dumps(r, ensure_ascii=False)
    for word in ("hợp nhau", "không hợp", "xung khắc", "hôn nhân tốt", "nên cưới"):
        assert word not in text
    assert "không mặc định là tốt hay xấu" in r["principle"]


def test_swapping_people_swaps_the_relations():
    a, b = PAIRS["tôi_mẹ"]
    ab, ba = run(a, b), run(b, a)
    flip = lambda kinds: sorted((k, y, x) for k, x, y in kinds)
    assert rel_kinds(ab["items"]) == flip(rel_kinds(ba["items"])) or sorted(k for k, _, _ in rel_kinds(ab["items"])) == sorted(k for k, _, _ in rel_kinds(ba["items"]))
    assert ab["structure"]["a"] == {**ba["structure"]["b"], "owner": "a"}


# ---------------------------------------------------------------- Tử Vi side: independent engine
def test_tuvi_module_does_not_import_the_bazi_engine():
    src = (Path(cd.__file__).parent / "compare_tuvi.py").read_text("utf-8")
    mods = []
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.ImportFrom):
            mods.append(n.module or "")
        elif isinstance(n, ast.Import):
            mods += [x.name for x in n.names]
    assert not [m for m in mods if "bazi" in m or "compare_deep" in m or "temporal" in m], mods


@pytest.mark.parametrize("i,j,code", [(0, 0, "cùng_vị_trí"), (0, 6, "xung_chiếu"), (0, 4, "tam_hợp"), (0, 8, "tam_hợp"), (0, 1, "liền_kề"), (0, 11, "liền_kề"), (0, 2, "không"), (3, 5, "không")])
def test_tuvi_geometry(i, j, code):
    assert compare_tuvi.geometry(i, j)[0] == code


def test_tuvi_pairs_use_each_charts_own_palaces():
    r = run(*PAIRS["cùng_một_người"])
    pair = next(i for i in r["items"] if i["id"] == "tv.pair.Mệnh.Mệnh")["data"]
    assert pair["geometry"] == "cùng_vị_trí" and set(pair["shared_own_major_stars"]) == set(pair["a"]["major_stars"])
    assert set(r["tuvi_structure"]["a"]) >= {"Mệnh", "Thân", "Phu Thê", "Phúc Đức"}
    assert next(i for i in r["items"] if i["id"] == "tv.pair.Mệnh.Phu_Thê")["data"]["b"]["palace"] == "Phu Thê"


# ---------------------------------------------------------------- regression on saved pairs + API
@pytest.mark.parametrize("key", list(PAIRS))
def test_golden(key):
    assert summary(run(*PAIRS[key])) == json.loads(GOLDEN.read_text("utf-8"))[key]


def test_api_returns_v1_and_v2_and_honours_the_experimental_flag():
    from fastapi.testclient import TestClient
    from tvbt.api import app
    c = TestClient(app)
    a, b = PAIRS["tôi_mẹ"]
    r = c.post("/api/compare-charts", json={"a": a, "b": b}).json()
    assert "ten_god_of_b_for_a" in r and r["v2"]["version"] == 2 and not r["v2"]["experimental"]
    r2 = c.post("/api/compare-charts", json={"a": {**a, "experimental": True}, "b": b}).json()
    assert r2["v2"]["experimental"] and len(r2["v2"]["items"]) > len(r["v2"]["items"])


if __name__ == "__main__" and "--regen" in sys.argv:
    GOLDEN.write_text(json.dumps({k: summary(run(*v)) for k, v in PAIRS.items()}, ensure_ascii=False, indent=1), "utf-8")
    print("wrote", GOLDEN)


# ---------------------------------------------------------------- one comparison UI, no CSS leftovers
WEB = ROOT.parent / "web"


def test_exactly_one_compare_entry_and_no_leftovers_of_the_old_uis():
    html = (WEB / "index.html").read_text("utf-8")
    assert html.count('id="cmp-host"') == 1 and html.count('id="cpx-dlg"') == 1
    assert "compare-out" not in html and "compare-hint" not in html
    js = {p.name: p.read_text("utf-8") for p in (WEB / "js").glob("*.js")}
    assert [n for n, t in js.items() if 'id="cmp-open"' in t] == ["compare.js"]
    assert "renderCompare(" not in js["mine.js"] and "sv-cmp" not in js["mine.js"]
    assert [n for n, t in js.items() if "initCompare" in t and n != "compare.js"] == ["app.js"]
    css = (WEB / "css" / "app.css").read_text("utf-8")
    for dead in (".sv-cmp", ".cmp-pick", ".cmp-dlg", ".cmp-host", ".cmp-in", ".cmp-rel", ".cpx-tier", ".cpx-b-"):
        assert dead not in css, dead


def test_every_cpx_class_used_by_the_ui_has_a_css_rule():
    import re
    css = (WEB / "css" / "app.css").read_text("utf-8")
    used = set()
    for name in ("compare.js", "compare_ui.js"):
        used |= set(re.findall(r"\bcpx-[a-z0-9-]+", (WEB / "js" / name).read_text("utf-8")))
    ids = {"cpx-dlg", "cpx-dlg-b", "cpx-s", "cpx-s-", "cpx-ev-", "cpx-ev-calc", "cpx-ev-src", "cpx-ev-hyp"}   # ids and the three evidence classes built from a template
    missing = sorted(c for c in used - ids if f".{c}" not in css)
    assert missing == [], missing
    assert all(f".{c}" in css for c in ("cpx-ev-calc", "cpx-ev-src", "cpx-ev-hyp"))


def test_compare_js_survives_a_pre_v2_response():
    src = (WEB / "js" / "compare.js").read_text("utf-8")
    assert "if (!res.v2)" in src and "legacy(" in src
