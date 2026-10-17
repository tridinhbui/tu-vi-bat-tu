"""Audit of Điều Hậu and Dụng Thần after Thiệu Vĩ Hoa pp.386-399.
Oracles are INDEPENDENT of the engine data: tests/golden/tvh_dieuhau_blind.json was transcribed blind from the page images by a separate pass, and
tests/golden/tvh_dungthan_examples.json holds the book's own inputs and conclusions. Where the engine does not reproduce the book, the test pins the
divergence by name instead of hiding it."""
import copy
import json
from pathlib import Path

import pytest

from tvbt.bazi_deep import dieuhau, geju, pipeline, strength, tvh_score, yongshen
from tvbt.bazi_deep.model import PILLARS, ChartView, group_of
from tvbt.bazi_deep.profile import DEFAULT, TTT_NTT, TVH_40
from tvbt.ganzhi import STEMS_VI

G = Path(__file__).parent / "golden"
BLIND = json.loads((G / "tvh_dieuhau_blind.json").read_text("utf-8"))
BOOK = json.loads((G / "tvh_dungthan_examples.json").read_text("utf-8"))
ENGINE = json.loads((dieuhau.DATA / "tvh_dieuhau.json").read_text("utf-8"))
MONTHS = ["Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu"]
STEMS = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]


# ------------------------------------------------------------------ 1. the 120 cells
def test_engine_table_equals_the_independent_blind_transcription_in_all_120_cells():
    assert {m: ENGINE["cells"][m] for m in MONTHS} == {m: BLIND["table"][m] for m in MONTHS}
    assert sum(len(v) for v in BLIND["table"].values()) == 120


# cells where the blind pass is known to be wrong or out of range, adjudicated against the page image (see 'adjudicated' in the fixture)
ADJUDICATED = {("Mùi", "Tân"): ["Nhâm", "Canh", "Giáp"], ("Sửu", "Quý"): ["Bính", "Đinh"]}


def test_engine_note_order_equals_the_blind_transcription_except_adjudicated_cells():
    diff = {(m, s) for m in MONTHS for s in STEMS if ENGINE["notes_order"][m][s] != BLIND["notes"][m][s]}
    assert diff == set(ADJUDICATED)
    for (m, s), truth in ADJUDICATED.items():
        assert ENGINE["notes_order"][m][s] == truth
    # the first blind pass found a transcription error in the engine data (Ất, tháng Thìn: sách in 'quý, bính, mậu'); it is fixed and pinned here
    assert ENGINE["notes_order"]["Thìn"]["Ất"] == ["Quý", "Bính", "Mậu"] == BLIND["notes"]["Thìn"]["Ất"]


# (day stem, month): table set vs note set, hand-derived from the page images. kind: note_adds = the note names a stem the table lacks;
# table_adds = the table lists a stem the note omits; swap = one of each.
NINE = {
    ("Bính", "Ngọ"): ("swap", ["Canh"], ["Quý"]),
    ("Bính", "Thân"): ("swap", ["Mậu"], ["Quý"]),
    ("Đinh", "Thìn"): ("note_adds", ["Mậu"], []),
    ("Mậu", "Ngọ"): ("swap", ["Giáp"], ["Canh"]),
    ("Tân", "Thân"): ("swap", ["Mậu"], ["Canh"]),
    ("Tân", "Dậu"): ("note_adds", ["Đinh"], []),
    ("Nhâm", "Thìn"): ("note_adds", ["Bính"], []),
    ("Quý", "Ngọ"): ("swap", ["Tân"], ["Nhâm"]),
    ("Quý", "Mùi"): ("table_adds", [], ["Nhâm"]),
}


def _kind(note_only, table_only):
    return "swap" if note_only and table_only else "note_adds" if note_only else "table_adds"


def test_exactly_nine_cells_disagree_and_every_one_is_a_set_difference_not_an_order_difference():
    seen = {}
    for m in MONTHS:
        for s in STEMS:
            t, n = BLIND["table"][m][s], BLIND["notes"][m][s] if (m, s) not in ADJUDICATED else ADJUDICATED[(m, s)]
            if set(t) != set(n):
                seen[(s, m)] = (_kind([x for x in n if x not in t], [x for x in t if x not in n]), [x for x in n if x not in t], [x for x in t if x not in n])
    assert seen == NINE
    assert sum(1 for v in NINE.values() if v[0] == "swap") == 5 and sum(1 for v in NINE.values() if v[0] == "note_adds") == 3


def test_the_first_noted_stem_is_always_inside_the_table_so_the_chief_stem_is_never_in_conflict():
    for m in MONTHS:
        for s in STEMS:
            assert ENGINE["notes_order"][m][s][0] in ENGINE["cells"][m][s], (m, s)


def test_table_print_order_is_not_the_priority_order():
    n_same = sum(1 for m in MONTHS for s in STEMS if ENGINE["cells"][m][s] == ENGINE["notes_order"][m][s])
    n_chief_differs = sum(1 for m in MONTHS for s in STEMS if ENGINE["cells"][m][s][0] != ENGINE["notes_order"][m][s][0])
    assert n_same <= 10 and n_chief_differs >= 60          # measured: 7 identical lists, chief stem differs in most cells; so ranking MUST come from the notes


def test_lookup_reports_the_conflict_for_those_nine_cells_and_for_no_other_cell():
    n = 0
    for m in MONTHS:
        for s in STEMS:
            ds, mb = STEMS.index(s), (MONTHS.index(m) + 2) % 12        # MONTHS starts at Dần; branch index 0 = Tý
            v = _chart(ds, mb)
            r = dieuhau.lookup(v)
            c = r["book_internal_conflict"]
            assert r["chu"] == ENGINE["notes_order"][m][s][0]
            if (s, m) in NINE:
                n += 1
                assert c is not None and c["note_only"] == NINE[(s, m)][1] and c["table_only"] == NINE[(s, m)][2]
                assert [x["stem"] for x in r["yong_stems"]] == [x for x in ENGINE["notes_order"][m][s] if x in ENGINE["cells"][m][s]] + c["table_only"]   # note-only stems are not promoted
            else:
                assert c is None
    assert n == 9


def _chart(day_stem: int, month_branch: int) -> ChartView:
    """Build a valid chart with the requested day stem and month branch. Branch index 0=Tý; month stem by the five-tiger rule from a fixed year stem."""
    from tvbt.ganzhi import BRANCHES_VI
    year_stem = 0                                                      # Giáp year: Dần month = Bính
    month_stem = (2 + ((month_branch - 2) % 12)) % 10
    # day pillar must have matching parity; pick day branch Tý (even) for even stems, Sửu (odd) for odd stems
    day_branch = day_stem % 2
    hour_stem = (day_stem * 2 + 0) % 10
    names = f"{STEMS[year_stem]} Tý / {STEMS[month_stem]} {BRANCHES_VI[month_branch]} / {STEMS[day_stem]} {BRANCHES_VI[day_branch]} / {STEMS[hour_stem]} Tý"
    return ChartView.from_names(names)


# ------------------------------------------------------------------ 2. the three worked examples (tr.397-399)
EXS = {k: v for k, v in BOOK["dungthan_examples"].items() if k in ("p397_vd1", "p398_vd2", "p399_vd3")}      # the three examples of the original audit (tr.397-399); example 4 is in test_bazi_deep_phase5.py
BOOK_ROLES = {   # printed ten-god row of each example, year/month/hour (the day master is the 'Nhật nguyên'), reduced to our groups
    "p397_vd1": {"year": "Tai", "month": "ThucThuong", "hour": "An"},          # Tài, Thương, Kiêu
    "p398_vd2": {"year": "ThucThuong", "month": "Tai", "hour": "Ti"},          # Thực, Tài, Kiếp
    "p399_vd3": {"year": "Ti", "month": "QuanSat", "hour": "QuanSat"},         # Kiếp, Quan, Sát
}
BOOK_HIDDEN = {   # printed tàng-can row, as sets
    "p397_vd1": {"year": {"Ất", "Mậu", "Quý"}, "month": {"Giáp", "Nhâm"}, "day": {"Tân", "Đinh", "Mậu"}, "hour": {"Ất", "Mậu", "Quý"}},
    "p398_vd2": {"year": {"Ất"}, "month": {"Tân", "Đinh", "Mậu"}, "day": {"Canh", "Bính", "Mậu"}, "hour": {"Quý"}},
    "p399_vd3": {"year": {"Tân", "Đinh", "Mậu"}, "month": {"Tân", "Đinh", "Mậu"}, "day": {"Canh", "Bính", "Mậu"}, "hour": {"Tân"}},
}
_run = {}


def run(key, profile=TVH_40):
    if (key, profile.id) not in _run:
        _run[(key, profile.id)] = pipeline.analyse(ChartView.from_names(EXS[key]["pillars"]), profile, with_rules=False)
    return _run[(key, profile.id)]


@pytest.mark.parametrize("key", list(EXS))
def test_example_inputs_match_the_books_printed_ten_gods_and_hidden_stems(key):
    v = ChartView.from_names(EXS[key]["pillars"])
    for p, g in BOOK_ROLES[key].items():
        assert dieuhau.ROLE_GROUP.get(group_of(v.god(v.stem(p))), group_of(v.god(v.stem(p)))) == g, (key, p)
    for p, names in BOOK_HIDDEN[key].items():
        assert {STEMS_VI[h["stem"]] for h in v.hidden(p)} == names, (key, p)


def test_example1_vd1_every_step_and_result():
    ex = EXS["p397_vd1"]["book"]
    o = run("p397_vd1"); S = o["strength_after"]; tv = S["tvh"]
    assert ex["dm_verdict"] == "vượng" and tv["dm_strong"] is True and tv["own_share"] == pytest.approx(0.5523, abs=1e-4)       # step 1: 40% rule
    assert tv["totals"]["Thổ"] == max(tv["totals"].values())                                                                       # step 2: Thổ is the biggest element (kỵ thần Thổ in the book)
    M = o["yongshen"]["methods"]
    assert M["cach_cuc_tvh"]["status"] == "ap_dung" and M["cach_cuc_tvh"]["dominant"] == "Ti"
    assert M["cach_cuc_tvh"]["yong"] == ex["dung_than_groups"] == ["QuanSat"]                                                       # step 3: dụng thần Mộc = Quan Sát
    assert ex["ky_than_groups"][0] in M["cach_cuc_tvh"]["ji"]                                                                       # kỵ Thổ (Ti)
    assert M["dieu_hau"]["yong"] == ["QuanSat"]                                                                                    # Mậu tháng Hợi: 'giáp, bính', Giáp first
    pu = M["phu_uc"]                                                                                                               # the system's phù ức uses the SYSTEM's strength (cực nhược here), not the 40% rule
    assert pu["level"] == "cực nhược" and pu["yong"] == ["An"] and "QuanSat" not in pu["yong"]                                     # NO MATCH: system strength disagrees with the book's verdict (vượng)
    assert M["cach_cuc"]["yong"][0] != "QuanSat"                                                                                   # the system's own draft table does NOT reproduce the book here
    assert M["khuyet_hanh"]["status"] == "khong_ap_dung"


def test_example2_vd2_book_verdict_is_not_reproducible_by_the_books_own_40_percent_rule():
    ex = EXS["p398_vd2"]["book"]
    o = run("p398_vd2"); S = o["strength_after"]; tv = S["tvh"]
    assert ex["dm_verdict"] == "nhược"
    assert tv["own_share"] == pytest.approx(0.4185, abs=1e-4) and tv["dm_strong"] is True          # 40% rule says vượng; the book says nhược from a qualitative reading
    assert tv["dm_strong"] != (ex["dm_verdict"] == "vượng")                                          # documented divergence
    M = o["yongshen"]["methods"]
    c = M["cach_cuc_tvh"]
    assert c["status"] == "hai_cach_doc" and c["threshold"]["near_threshold"] is True and c["threshold"]["book_rule_reading"] == "vượng"
    alts = {a["dm_vi"]: a for a in c["alternatives"]}
    assert alts["nhược"]["yong"] == ex["dung_than_groups"] == ["An"] and alts["nhược"]["follows_book_rule"] is False         # the book's reading gives the book's dụng thần Kim
    assert alts["vượng"]["follows_book_rule"] is True and alts["vượng"]["yong"][0] == "QuanSat"                              # the rule's own reading does not
    assert M["dieu_hau"]["yong"] == ["An"] and "Ti" in M["dieu_hau"]["xi"]                                                  # Kim, with tỉ kiếp as hỷ — matches the book without needing the verdict
    pu = M["phu_uc"]
    assert pu["level"] == "nhược" and pu["yong"] == ex["dung_than_groups"] == ["An"] and ex["ky_than_groups"][0] in pu["ji"]        # system phù ức (nhược) matches the book here


def test_example3_vd3_strength_matches_cach_table_only_partly_and_dieu_hau_and_khuyet_hanh_match_the_book():
    ex = EXS["p399_vd3"]["book"]
    o = run("p399_vd3"); S = o["strength_after"]; tv = S["tvh"]
    assert tv["dm_strong"] is True and tv["own_share"] == pytest.approx(0.7373, abs=1e-4)
    assert tv["totals"]["Mộc"] == 0 and tv["totals"]["Thủy"] == 0                                    # 'thiếu mộc, thiếu thủy'
    assert o["geju"]["readings"][0]["cach"] == "Thất Sát"                                           # = Thiên Quan, the book's 'cách thiên quan'
    M = o["yongshen"]["methods"]
    want = set(ex["dung_than_groups"])
    c = M["cach_cuc_tvh"]
    assert c["yong"] == ["QuanSat"] and set(c["yong_alternatives"]) == {"QuanSat", "Tai"}           # PARTIAL: Tài is there, Thực Thương is not; the book chose by ngũ hành balance, not by its own table
    assert set(c["yong_alternatives"]) & want == {"Tai"} and want - set(c["yong_alternatives"]) == {"ThucThuong"}
    d = M["dieu_hau"]
    assert d["yong"] + d["xi"] == ["ThucThuong", "Tai"] and set(d["yong"] + d["xi"]) == want           # Tân tháng Tuất: 'nhâm, giáp' = Thủy then Mộc, same as the book
    k = M["khuyet_hanh"]
    assert k["status"] == "ap_dung" and set(k["yong"]) == want and sorted(k["need_elements"]) == sorted(ex["dung_than_elements"])
    assert k["meta"]["verification"] == "draft" and "tr.399" in k["meta"]["source"][0]               # single worked example, so draft


def test_summary_which_methods_reproduce_the_books_dung_than():
    """The one-line scoreboard of the audit: primary dụng thần group(s) of each method against the book, per example."""
    def prim(key, m):
        mm = run(key)["yongshen"]["methods"][m]
        return mm["yong"] if mm["status"] != "hai_cach_doc" else None
    book = {k: v["book"]["dung_than_groups"] for k, v in EXS.items()}
    assert prim("p397_vd1", "cach_cuc_tvh") == book["p397_vd1"] and prim("p397_vd1", "dieu_hau") == book["p397_vd1"]
    assert prim("p398_vd2", "dieu_hau") == book["p398_vd2"] and prim("p398_vd2", "cach_cuc_tvh") is None
    assert set(prim("p399_vd3", "khuyet_hanh")) == set(book["p399_vd3"]) and prim("p399_vd3", "dieu_hau") == ["ThucThuong"]


# ------------------------------------------------------------------ 2b. the five điều hậu illustrations (tr.387-388)
@pytest.mark.parametrize("key,verdict", [("p387_intro", "match"), ("p388_vd4", "match"), ("p387_vd1", "partial"), ("p388_vd2", "partial"), ("p388_vd3", "partial")])
def test_dieu_hau_illustrations_match_or_partially_match_the_book(key, verdict):
    ex = BOOK["dieuhau_examples"][key]
    r = dieuhau.lookup(ChartView.from_names(ex["pillars"]))
    groups = [x["group"] for x in r["yong_stems"]]
    if verdict == "match":
        assert groups[0] == ex["dung_than_groups"][0]                                                    # the chief stem has the book's group
    else:
        assert groups[0] != ex["dung_than_groups"][0] and ex["dung_than_groups"][0] in groups[1:]        # the book's pick is in the cell but is not ranked first


# ------------------------------------------------------------------ 3. the 40% threshold
def test_40_percent_decision_on_the_books_own_numbers_and_at_the_edge():
    share, strong = tvh_score.decide(78, 197)               # book tr.355 ví dụ 6: 78 < 78,8 → nhược
    assert strong is False and share < 0.40 and 0.40 * 197 == pytest.approx(78.8)
    assert tvh_score.decide(115, 218)[1] is True            # ví dụ 7: 115 > 87,2 → vượng
    assert tvh_score.decide(79.99, 200)[1] is False         # just below
    assert tvh_score.decide(80, 200)[1] is True and tvh_score.decide(80, 200)[0] == 0.40     # exactly 40%: the book is silent; this system counts it as vượng
    assert tvh_score.decide(80.01, 200)[1] is True          # just above
    assert tvh_score.THRESHOLD == 0.40


def test_the_ambiguity_band_is_this_systems_heuristic_and_is_labelled_so():
    S = {"shares": {"Ti": 0.4, "An": 0.1, "ThucThuong": 0.2, "Tai": 0.2, "QuanSat": 0.1}, "level_index": 3, "ambiguous": True, "readings": ["thiên nhược", "thiên vượng"],
         "tvh": {"own_share": 0.40, "dm_strong": True}}
    c = yongshen.cach_cuc_tvh({"readings": [{"cach": "Chính Tài", "kind": "noi_cach"}]}, S, DEFAULT)
    t = c["threshold"]
    assert t["rule_src"] == "SRC_TVH_DIEM tr.355" and t["margin_src"].startswith("he_thong") and "không phải của sách" in t["margin_src"]
    assert t["margin_heuristic"] == DEFAULT.tvh_margin == 0.03 and "quy ước hệ thống" in t["equality_choice"]


@pytest.mark.parametrize("share,margin,near,reading", [
    (0.3999, 0.03, True, "nhược"), (0.40, 0.03, True, "vượng"), (0.4001, 0.03, True, "vượng"),         # inside the heuristic band: two readings, rule reading flips at 40%
    (0.3999, 0.0, False, "nhược"), (0.40, 0.0, False, "vượng"), (0.4001, 0.0, False, "vượng"),         # band switched off: one reading, decided only by the book's rule
    (0.369, 0.03, False, "nhược"), (0.431, 0.03, False, "vượng"),                                       # just outside the band
])
def test_cach_cuc_tvh_just_below_at_and_above_the_threshold(share, margin, near, reading):
    own = share * 200
    strong = tvh_score.decide(own, 200)[1]
    S = {"shares": {"Ti": 0.45, "An": 0.10, "ThucThuong": 0.15, "Tai": 0.15, "QuanSat": 0.15}, "level_index": 3,
         "ambiguous": strength._band(share, margin) == 3, "tvh": {"own_share": share, "dm_strong": strong}}
    c = yongshen.cach_cuc_tvh({"readings": [{"cach": "Chính Tài", "kind": "noi_cach"}]}, S, DEFAULT.with_(tvh_margin=margin))
    assert c["threshold"]["near_threshold"] is near and c["threshold"]["book_rule_reading"] == reading
    if near:
        assert c["status"] == "hai_cach_doc" and {a["dm_vi"] for a in c["alternatives"]} == {"vượng", "nhược"}
        assert [a["dm_vi"] for a in c["alternatives"] if a["follows_book_rule"]] == [reading]
    else:
        assert c["status"] != "hai_cach_doc" and c["dm"] == reading


def _labelled():
    cases = json.loads((G / "ttt_cases.json").read_text("utf-8"))["cases"]
    out = [(v["pillars"], v["dm"] == "strong") for v in cases.values() if v["kind"] in ("tong", "thuong_quan")]
    out += [(v["pillars"], v["strong"]) for v in json.loads((G / "tvh_examples.json").read_text("utf-8"))["examples"].values()]
    out += [(v["pillars"], v["book"]["dm_verdict"] == "vượng") for v in EXS.values()]
    return out


def test_threshold_sensitivity_40_percent_is_on_a_plateau_not_a_tuned_optimum():
    lab = [(tvh_score.score(ChartView.from_names(p))["own_share"], s) for p, s in _labelled()]
    assert len(lab) == 55                                           # 48 Trích Thiên Tủy labels + 4 TVH scoring examples + the 3 audited examples
    agree = {t: sum((x >= t) == s for x, s in lab) for t in (0.30, 0.34, 0.36, 0.38, 0.39, 0.40, 0.41, 0.42, 0.44, 0.46, 0.50)}
    assert agree[0.40] >= 50 and agree[0.40] == 51           # measured 51/55 = 92.7% (one of the 4 misses is example 2, whose label the book's rule cannot reproduce)
    assert max(agree.values()) - agree[0.40] <= 1             # no nearby threshold does better by more than one chart: 40% is not distorted to fit
    assert all(abs(agree[t] - agree[0.40]) <= 2 for t in (0.38, 0.39, 0.41, 0.42, 0.44))
    assert agree[0.30] <= agree[0.40] - 3 and agree[0.50] <= agree[0.40]      # a clearly wrong threshold does worse


def test_ambiguity_band_sensitivity_counts_on_the_81_book_charts():
    cases = json.loads((G / "ttt_cases.json").read_text("utf-8"))["cases"]
    sh = [tvh_score.score(ChartView.from_names(v["pillars"]))["own_share"] for v in cases.values()]
    assert len(sh) == 81
    n = {m: sum(strength._band(x, m) == 3 for x in sh) for m in (0.0, 0.01, 0.02, 0.03, 0.05)}
    assert n == {0.0: 0, 0.01: 0, 0.02: 1, 0.03: 2, 0.05: 7}        # at the default margin only 2/81 charts get two readings; at ±5% it would be 7/81


# ------------------------------------------------------------------ 4/5. methods separate, each with source, verification and trace; no final answer
@pytest.mark.parametrize("key", list(EXS))
def test_every_method_has_its_own_source_verification_trace_and_basis(key):
    Y = run(key)["yongshen"]
    assert set(Y["methods"]) == {"phu_uc", "dieu_hau", "cach_cuc", "cach_cuc_tvh", "thong_quan", "thuan_the", "thuan_the_tvh", "khuyet_hanh"}
    for name, m in Y["methods"].items():
        meta = m["meta"]
        assert meta["source"] and all(isinstance(x, str) for x in meta["source"]), name
        assert meta["verification"] in ("verified", "partial", "draft"), name
        assert meta["applies_when"] and meta["strength_basis"] and isinstance(meta["applied"], bool), name
        assert m["trace"] and all(isinstance(x, str) and x for x in m["trace"]), name
    ver = {n: m["meta"]["verification"] for n, m in Y["methods"].items()}
    assert ver["phu_uc"] == ver["cach_cuc"] == ver["thong_quan"] == ver["khuyet_hanh"] == "draft"         # nothing here is verified wholesale
    assert ver["dieu_hau"] == ver["cach_cuc_tvh"] == ver["thuan_the"] == ver["thuan_the_tvh"] == "partial"
    assert "verified" not in ver.values()


def test_comparison_lists_disagreements_with_conditions_and_picks_no_winner():
    Y = run("p398_vd2")["yongshen"]
    C = Y["comparison"]
    assert C["no_final_answer"] is True and "Không có kết luận cuối" in C["note"]
    assert set(C) == {"rows", "disagreements", "consensus", "methods", "no_final_answer", "note"}          # no 'final', 'score' or 'winner' key
    assert set(C["methods"]) == set(Y["methods"])
    for name, info in C["methods"].items():
        assert info["applies_when"] and info["verification"] and info["strength_basis"]
    assert "yong" not in Y and "final" not in Y and "score" not in Y
    assert all(d["favourable_in"] and d["unfavourable_in"] for d in C["disagreements"])
    # a real disagreement exists in this example (Ấn is Dụng for the chart's điều hậu/phù ức-nhược reading, Kỵ for phù ức-vượng) and is shown, not resolved
    assert C["rows"] and not any("chosen" in d or "winner" in d for d in C["disagreements"])


def test_the_two_phu_uc_readings_of_a_border_chart_are_both_kept():
    pu = run("p399_vd3")["yongshen"]["methods"]["phu_uc"]            # the system's own strength is on the border for this chart
    assert pu["status"] == "hai_cach_doc" and len(pu["alternatives"]) == 2 and pu["yong"] == []


# ------------------------------------------------------------------ 6. school isolation
def _charts():
    cases = json.loads((G / "ttt_cases.json").read_text("utf-8"))["cases"]
    ex = json.loads((dieuhau.DATA.parent / "bazi_deep/examples.json").read_text("utf-8"))["charts"]
    return [v["pillars"] for v in cases.values()] + list(ex.values())


_pair = {}


def pair(p):
    if p not in _pair:
        v = ChartView.from_names(p)
        _pair[p] = (pipeline.analyse(v, DEFAULT, with_rules=False), pipeline.analyse(v, TVH_40, with_rules=False))
    return _pair[p]


def _core(m):
    return {k: v for k, v in m.items() if k not in ("meta", "trace", "table", "climate")}


def test_tvh_scoring_never_changes_the_system_schools_cach_cuc_or_thuan_the_on_96_charts():
    for p in _charts():
        a, b = pair(p)
        for m in ("cach_cuc", "thuan_the"):
            assert _core(a["yongshen"]["methods"][m]) == _core(b["yongshen"]["methods"][m]), (m, p)


def test_phu_uc_differs_between_profiles_only_through_the_vuong_nhuoc_decision():
    same = 0
    for p in _charts():
        a, b = pair(p)
        Sa, Sb = a["strength_after"], b["strength_after"]
        if (Sa["level_index"], Sa["ambiguous"]) == (Sb["level_index"], Sb["ambiguous"]):
            same += 1
            assert _core(a["yongshen"]["methods"]["phu_uc"]) == _core(b["yongshen"]["methods"]["phu_uc"]), p
    assert same >= 25                                                    # measured 28/96: the check is not vacuous


def test_inner_cach_identification_is_the_same_under_both_profiles():
    for p in _charts():
        a, b = pair(p)
        assert [c["name"] for c in a["geju"]["inner"]] == [c["name"] for c in b["geju"]["inner"]], p


def test_tvh_special_cach_only_exist_under_the_tvh_profile_and_only_feed_the_tvh_methods():
    n = 0
    for p in _charts():
        a, b = pair(p)
        assert all("(TVH)" not in o["name"] and o.get("kind") not in yongshen.TVH_KINDS for o in a["geju"]["outer"]), p
        assert "tvh" not in a["strength_after"], p
        assert a["yongshen"]["methods"]["thuan_the_tvh"]["status"] == "khong_chan"
        n += b["yongshen"]["methods"]["thuan_the_tvh"]["status"] == "ap_dung"
    assert n >= 5                                                        # the TVH methods do fire on TVH profile


def test_cach_cuc_tvh_does_not_mutate_its_inputs():
    o = pipeline.analyse(ChartView.from_names(EXS["p397_vd1"]["pillars"]), TVH_40, with_rules=False)
    Gj, S = o["geju"], o["strength_after"]
    g0, s0 = copy.deepcopy(Gj), copy.deepcopy(S)
    yongshen.cach_cuc_tvh(Gj, S, TVH_40)
    yongshen.thuan_the_tvh(Gj)
    assert Gj == g0 and S == s0


def test_yongshen_output_says_which_school_each_method_was_computed_from():
    Y = run("p397_vd1")["yongshen"]
    assert Y["isolation"]["system_school_computed_from"] == "he_thong" and Y["isolation"]["tvh_school"] == "tvh_40"
    assert Y["methods"]["cach_cuc"]["meta"]["strength_basis"].startswith("he_thong")
    assert Y["methods"]["cach_cuc_tvh"]["meta"]["strength_basis"].startswith("tvh_40")
    D = pair("Mậu Tuất / Kỷ Mùi / Giáp Tuất / Mậu Thìn")[0]["yongshen"]
    assert D["isolation"]["tvh_school"] is None and D["methods"]["cach_cuc_tvh"]["meta"]["strength_basis"].startswith("he_thong (dự phòng")
