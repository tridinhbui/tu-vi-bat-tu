"""Phase 5: independent validation and cross-school isolation of the deep Bát Tự engine. No new method is tested here; everything checks what already exists.
Three verification levels are kept apart: transcription_verified, source_rule_verified, empirical_validated. Nothing in the module is empirical_validated."""
import json
import random
import re
from pathlib import Path

import pytest

from tvbt.bazi_deep import dieuhau, geju, pipeline, yongshen
from tvbt.bazi_deep.model import ChartView
from tvbt.bazi_deep.profile import DEFAULT, TVH_40

G = Path(__file__).parent / "golden"
BOOK = json.loads((G / "tvh_dungthan_examples.json").read_text("utf-8"))
BLIND = json.loads((G / "tvh_examples_blind.json").read_text("utf-8"))["examples"]
S10 = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
B12 = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
TVH_METHODS = ("cach_cuc_tvh", "thuan_the_tvh")
SYS_METHODS = ("cach_cuc", "thuan_the")


def _cyc(i):
    return f"{S10[i % 10]} {B12[i % 12]}"


def _chart(y, mb, d, hb):
    ms = (((y % 10) % 5) * 2 + 2 + ((mb - 2) % 12)) % 10          # five-tiger rule
    hs = ((d % 10) * 2 + hb) % 10                                  # five-rat rule
    return f"{_cyc(y)} / {S10[ms]} {B12[mb]} / {_cyc(d)} / {S10[hs]} {B12[hb]}"


def sample(n, seed):
    r = random.Random(seed)
    return [_chart(r.randrange(60), r.randrange(12), r.randrange(60), r.randrange(12)) for _ in range(n)]


CHARTS = sample(1200, 20261017)
_cache = {}


def run(p, profile=TVH_40):
    k = (p, profile.id, id(profile))
    if k not in _cache:
        _cache[k] = pipeline.analyse(ChartView.from_names(p), profile, with_rules=False)
    return _cache[k]


def core(m):
    return {k: v for k, v in m.items() if k not in ("meta", "trace", "table", "climate")}


# ------------------------------------------------------------------ the sample itself covers the cases the task names
def classify(o):
    keys = set()
    out = o["geju"]["outer"]
    sys_chan = [x for x in out if x.get("kind") not in yongshen.TVH_KINDS and x["quality"] == "chân"]
    tvh_out = [x for x in out if x.get("kind") in yongshen.TVH_KINDS]
    tv = o["strength_after"]["tvh"]
    if sys_chan:
        keys.add("system_outer_chan")
    if tvh_out:
        keys.add("tvh_special")
    if sys_chan and not tvh_out:
        keys.add("system_only")
    if tvh_out and not sys_chan:
        keys.add("tvh_only")
    if any(x.get("kind") == "tong_tvh" for x in tvh_out):
        keys.add("tvh_tong")
    if abs(tv["own_share"] - 0.40) < DEFAULT.tvh_margin:
        keys.add("near_40")
    if o["geju"]["readings"] and o["geju"]["readings"][0]["cach"] == "Thất Sát" and tv["dm_strong"]:
        keys.add("sat_vuong_strong_dm")
    if o["yongshen"]["comparison"]["disagreements"]:
        keys.add("conflicting_dung_than")
    return keys


def test_the_sample_is_big_enough_in_every_special_class():
    from collections import Counter
    c = Counter(k for p in CHARTS for k in classify(run(p)))
    assert len(CHARTS) == 1200 and len(set(CHARTS)) > 1100
    for k, n in (("system_outer_chan", 10), ("tvh_special", 40), ("system_only", 5), ("tvh_only", 30), ("tvh_tong", 5), ("near_40", 40), ("sat_vuong_strong_dm", 10), ("conflicting_dung_than", 500)):
        assert c[k] >= n, (k, c[k])


# ------------------------------------------------------------------ forward isolation: TVH on/off never changes the system methods
def test_turning_the_tvh_profile_on_never_changes_the_system_methods_on_1200_charts():
    for p in CHARTS:
        a, b = run(p, DEFAULT), run(p, TVH_40)
        for m in SYS_METHODS:
            assert core(a["yongshen"]["methods"][m]) == core(b["yongshen"]["methods"][m]), (m, p)
        assert a["yongshen"]["methods"]["dieu_hau"]["yong"] == b["yongshen"]["methods"]["dieu_hau"]["yong"], p
        assert [c["name"] for c in a["geju"]["inner"]] == [c["name"] for c in b["geju"]["inner"]], p


def test_phu_uc_and_thong_quan_are_also_unchanged_by_the_tvh_profile():
    for p in CHARTS:
        a, b = run(p, DEFAULT), run(p, TVH_40)
        for m in ("phu_uc", "thong_quan", "khuyet_hanh"):
            assert core(a["yongshen"]["methods"][m]) == core(b["yongshen"]["methods"][m]), (m, p)


# ------------------------------------------------------------------ reverse isolation: changing system-only inputs never changes the TVH methods
SYSTEM_ONLY_CHANGES = [
    {"level_cuts": (0.10, 0.20, 0.30, 0.60, 0.70, 0.90)}, {"level_margin": 0.10}, {"presence_share": 0.20}, {"thuong_vuong": 0.10},
    {"tong_cuong_min": 0.40}, {"tong_vuong_ti": 0.30}, {"tong_foe_max": 0.30}, {"tong_the_each": 0.05}, {"tong_dominant_share": 0.30}, {"tong_chan_tia": 0.50},
    {"tong_gia_tia": 0.60}, {"tong_max_ratio": 0.60}, {"war_share": 0.05}, {"bridge_min": 0.50}, {"hua_du_share": 0.10}, {"flow_min": 0.30},
    {"hidden_frac": {1: (1.0,), 2: (0.5, 0.5), 3: (0.4, 0.3, 0.3)}}, {"season_factor": {"vượng": 3.0, "tướng": 2.0, "hưu": 1.0, "tù": 0.2, "tử": 0.1}},
    {"class_weight": {"ban_khi": 1.0, "trung_khi": 1.0, "du_khi": 1.0}}, {"kho_policy": "tu_co_can"},
]


@pytest.mark.parametrize("change", SYSTEM_ONLY_CHANGES, ids=lambda c: next(iter(c)))
def test_changing_a_system_only_parameter_does_not_change_the_tvh_methods(change):
    alt = TVH_40.with_(**change)
    for p in CHARTS[:300]:
        a, b = run(p, TVH_40), pipeline.analyse(ChartView.from_names(p), alt, with_rules=False)
        for m in TVH_METHODS:
            assert core(a["yongshen"]["methods"][m]) == core(b["yongshen"]["methods"][m]), (change, m, p)
        assert a["strength_after"]["tvh"] == b["strength_after"]["tvh"], (change, p)


TVH_ONLY_CHANGES = [{"tvh_no_help": 0.40}, {"tvh_tong_main": 0.10}, {"chuyen_vuong_chars": 3}, {"chuyen_vuong_share": 0.30}, {"tvh_margin": 0.10}]


@pytest.mark.parametrize("change", TVH_ONLY_CHANGES, ids=lambda c: next(iter(c)))
def test_changing_a_tvh_only_parameter_does_not_change_cach_cuc_or_thuan_the_of_the_system(change):
    alt = TVH_40.with_(**change)
    for p in CHARTS[:300]:
        a, b = run(p), pipeline.analyse(ChartView.from_names(p), alt, with_rules=False)
        for m in SYS_METHODS + ("phu_uc", "thong_quan", "dieu_hau", "khuyet_hanh"):
            assert core(a["yongshen"]["methods"][m]) == core(b["yongshen"]["methods"][m]), (change, m, p)
        assert [(c["name"], c["state"]) for c in a["geju"]["inner"]] == [(c["name"], c["state"]) for c in b["geju"]["inner"]], (change, p)
        assert [x["name"] for x in a["geju"]["outer"] if x.get("kind") not in yongshen.TVH_KINDS] == [x["name"] for x in b["geju"]["outer"] if x.get("kind") not in yongshen.TVH_KINDS], (change, p)


def test_headline_geju_under_tvh_equals_the_system_geju_plus_tvh_additions():
    for p in CHARTS:
        a, b = run(p, DEFAULT), run(p, TVH_40)
        assert [(c["name"], c["state"]) for c in a["geju"]["inner"]] == [(c["name"], c["state"]) for c in b["geju"]["inner"]], p
        assert [(x["name"], x["quality"]) for x in a["geju"]["outer"]] == [(x["name"], x["quality"]) for x in b["geju"]["outer"] if x.get("kind") not in yongshen.TVH_KINDS], p


def test_the_system_only_perturbations_really_do_move_the_system_side():
    """Non-vacuity of the reverse-isolation test: most of the perturbations change some system method on some chart."""
    moved = 0
    for change in SYSTEM_ONLY_CHANGES:
        alt = TVH_40.with_(**change)
        for p in CHARTS[:300]:
            b = pipeline.analyse(ChartView.from_names(p), alt, with_rules=False)["yongshen"]["methods"]
            a = run(p)["yongshen"]["methods"]
            if any(core(a[m]) != core(b[m]) for m in ("phu_uc", "cach_cuc", "thong_quan", "thuan_the")):
                moved += 1
                break
    assert moved >= 12                                                  # measured: the others (e.g. tong_gia_tia, flow_min) do not feed any yongshen method


def test_tvh_methods_never_see_the_systems_outer_cach_and_the_system_never_sees_tvhs():
    n_sys = n_tvh = 0
    for p in CHARTS:
        o = run(p)
        M = o["yongshen"]["methods"]
        out = o["geju"]["outer"]
        sys_chan = [x for x in out if x.get("kind") not in yongshen.TVH_KINDS and x["quality"] == "chân"]
        tvh_out = [x for x in out if x.get("kind") in yongshen.TVH_KINDS]
        if sys_chan and not tvh_out and o["geju"]["inner"]:
            n_sys += 1
            assert M["cach_cuc_tvh"]["status"] != "khong_xac_dinh_noi_cach" or not any(r for r in [o["geju"]["inner"][0]["name"]] if r in yongshen.TVH_DT["cach_key"]), p
            assert M["thuan_the_tvh"]["status"] == "khong_chan", p
        if tvh_out and not sys_chan:
            n_tvh += 1
            assert M["thuan_the"]["status"] in ("khong_chan", "chi_co_gia"), p                 # the TVH special cách never feed the system's thuận thế
            assert M["cach_cuc"]["status"] != "khong_xac_dinh_noi_cach" or not o["geju"]["inner"], p
    assert n_sys >= 5 and n_tvh >= 30


# ------------------------------------------------------------------ edge cases
def test_near_40_percent_flag_and_two_readings_agree_everywhere():
    n = 0
    for p in CHARTS:
        o = run(p)
        c = o["yongshen"]["methods"]["cach_cuc_tvh"]
        if "threshold" not in c:
            continue
        tv = o["strength_after"]["tvh"]
        assert c["threshold"]["near_threshold"] == (abs(tv["own_share"] - 0.40) < c["threshold"]["margin_heuristic"]), p
        assert (c["status"] == "hai_cach_doc") == c["threshold"]["near_threshold"], p
        assert c["threshold"]["book_rule_reading"] == ("vượng" if tv["own_share"] >= 0.40 else "nhược"), p
        if c["status"] == "hai_cach_doc":
            n += 1
            assert [a["follows_book_rule"] for a in c["alternatives"]].count(True) == 1
    assert n >= 30


def test_tong_and_special_cach_are_always_chan_exclusive_with_phu_uc_of_the_same_school():
    n = 0
    for p in CHARTS:
        o = run(p)
        M = o["yongshen"]["methods"]
        tvh = [x for x in o["geju"]["outer"] if x.get("kind") in yongshen.TVH_KINDS and x["quality"] == "chân"]
        if tvh:
            n += 1
            assert M["thuan_the_tvh"]["status"] == "ap_dung" and M["thuan_the_tvh"]["outer"] == tvh[0]["name"], p
            assert M["cach_cuc_tvh"]["status"] == "khong_xac_dinh_noi_cach", p              # an outer cách replaces the inner one inside the TVH school
            assert M["thuan_the_tvh"]["meta"]["levels"]["empirical_validated"] == "no"
    assert n >= 40


def test_conflicting_dung_than_is_listed_not_resolved():
    n = 0
    for p in CHARTS[:400]:
        C = run(p)["yongshen"]["comparison"]
        for d in C["disagreements"]:
            n += 1
            assert d["favourable_in"] and d["unfavourable_in"] and not set(d["favourable_in"]) & set(d["unfavourable_in"])
            assert set(d["favourable_in"]) | set(d["unfavourable_in"]) <= set(C["methods"])
        assert C["no_final_answer"] is True and set(C) == {"rows", "disagreements", "consensus", "methods", "no_final_answer", "note"}
    assert n >= 300


def test_sat_vuong_charts_resolve_to_a_row_consistent_with_their_strength():
    n = 0
    for p in CHARTS:
        o = run(p)
        if "sat_vuong_strong_dm" not in classify(o):
            continue
        c = o["yongshen"]["methods"]["cach_cuc_tvh"]
        n += 1
        if c["status"] == "ap_dung":
            assert c["dm"] == "vượng" and c["yong"] and c["page"], p
        elif c["status"] == "hai_cach_doc":
            assert {a["dm_vi"] for a in c["alternatives"]} == {"vượng", "nhược"}
    assert n >= 10


# ------------------------------------------------------------------ trace and metadata stability
def test_metadata_and_trace_are_identical_across_repeated_runs_and_json_roundtrip():
    for p in CHARTS[:200]:
        a = pipeline.analyse(ChartView.from_names(p), TVH_40, with_rules=False)["yongshen"]
        b = pipeline.analyse(ChartView.from_names(p), TVH_40, with_rules=False)["yongshen"]
        assert json.dumps(a, ensure_ascii=False) == json.dumps(b, ensure_ascii=False), p
        assert json.loads(json.dumps(a, ensure_ascii=False)) == a, p


META_KEYS = {"levels", "source", "verification", "applies_when", "strength_basis", "applied"}
LEVEL_KEYS = {"transcription_verified", "source_rule_verified", "empirical_validated", "why"}


def test_every_method_on_every_chart_has_the_same_metadata_shape_and_a_nonempty_trace():
    for p in CHARTS[:400]:
        Y = run(p)["yongshen"]
        assert list(Y["methods"]) == ["phu_uc", "dieu_hau", "cach_cuc", "cach_cuc_tvh", "thong_quan", "thuan_the", "thuan_the_tvh", "khuyet_hanh"]
        for name, m in Y["methods"].items():
            assert set(m["meta"]) == META_KEYS, (name, p)
            assert set(m["meta"]["levels"]) == LEVEL_KEYS and m["meta"]["levels"]["empirical_validated"] == "no", (name, p)
            assert m["trace"] and all(isinstance(t, str) and t for t in m["trace"]), (name, p)
            assert m["meta"]["applied"] == (m["status"] in yongshen.APPLIED)


def test_levels_are_not_inferred_from_one_another():
    L = {k: v["levels"] for k, v in yongshen.METHOD_META.items()}
    assert all(v["empirical_validated"] == "no" for v in L.values())                # nothing in the module has independent predictive evidence
    assert all(v["source_rule_verified"] != "yes" for v in L.values())              # no method's whole formula is claimed to equal the source's
    assert {k for k, v in L.items() if v["transcription_verified"] == "yes"} == {"dieu_hau", "cach_cuc_tvh", "thuan_the", "thuan_the_tvh"}
    for k, v in yongshen.METHOD_META.items():
        assert (v["verification"] == "draft") == (v["levels"]["source_rule_verified"] == "no"), k
        assert v["levels"]["why"]


def test_cited_source_ids_exist_and_are_registered_as_verified_where_a_level_says_yes():
    reg = {x["id"]: x for x in json.loads((dieuhau.DATA / "sources_books.json").read_text("utf-8"))["sources"]}
    for k, v in yongshen.METHOD_META.items():
        ids = {m for s in v["source"] for m in re.findall(r"SRC_[A-Z_]+", s)}
        assert ids <= set(reg), (k, ids - set(reg))
        if v["levels"]["transcription_verified"] == "yes":
            assert ids and all(str(reg[i]["verified"]) == "True" for i in ids), k
    assert "SRC_DOIVAN_LCM" not in {m for v in yongshen.METHOD_META.values() for s in v["source"] for m in re.findall(r"SRC_[A-Z_]+", s)}   # the unverified popular book is never a source


def _pages(locator):
    out = set()
    for a, b in re.findall(r"(\d{3})(?:-(\d{3}))?", locator):
        out |= set(range(int(a), int(b or a) + 1))
    return out


def test_the_source_entries_cover_the_pages_actually_used():
    reg = {x["id"]: x for x in json.loads((dieuhau.DATA / "sources_books.json").read_text("utf-8"))["sources"]}
    assert {386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396} <= _pages(reg["SRC_TVH_DIEUHAU"]["locator"])
    assert {376, 380, 386, 397, 398, 399, 400} <= _pages(reg["SRC_TVH_DUNGTHAN"]["locator"])


# ------------------------------------------------------------------ the worked examples again, with the independent blind transcription
def _norm(x):
    x = re.sub(r"\s*\(.*", "", x.lower()).strip()
    x = x.replace("kỉ", "kỷ").replace("tị", "tỵ").replace("quí", "quý").replace("tí", "tý")
    return " ".join(w.capitalize() for w in x.split())


BLIND_MAP = {"D0": ("dieuhau_examples", "p387_intro"), "D1": ("dieuhau_examples", "p387_vd1"), "D2": ("dieuhau_examples", "p388_vd2"), "D3": ("dieuhau_examples", "p388_vd3"),
             "D4": ("dieuhau_examples", "p388_vd4"), "E1": ("dungthan_examples", "p397_vd1"), "E2": ("dungthan_examples", "p398_vd2"), "E3": ("dungthan_examples", "p399_vd3"),
             "E4": ("dungthan_examples", "p400_vd4")}


@pytest.mark.parametrize("bk", list(BLIND_MAP))
def test_example_inputs_equal_the_independent_blind_transcription(bk):
    sec, key = BLIND_MAP[bk]
    mine = [x.strip() for x in BOOK[sec][key]["pillars"].split("/")]
    bl = BLIND[bk]["pillars"]
    assert mine == [_norm(bl[p]) for p in ("year", "month", "day", "hour")]


def test_example_4_inputs_are_reconstructed_and_say_so_and_agree_with_the_calendar():
    ex = BOOK["dungthan_examples"]["p400_vd4"]
    assert ex["reconstructed"] is True and "bảng in" in ex["reconstruction_basis"] and BLIND["E4"]["reconstructed"] is True
    import datetime as dt
    i = (10 + (dt.date(1974, 1, 2) - dt.date(1900, 1, 1)).days) % 60                  # 1900-01-01 is Giáp Tuất
    assert _cyc(i) == "Quý Mão" == ex["pillars"].split(" / ")[2]


def test_example_4_pinned_result_does_not_match_the_book_and_the_cause_is_named():
    ex = BOOK["dungthan_examples"]["p400_vd4"]["book"]
    o = run(BOOK["dungthan_examples"]["p400_vd4"]["pillars"])
    tv = o["strength_after"]["tvh"]
    assert tv["dm_strong"] is True and tv["own_share"] == pytest.approx(0.7598, abs=1e-4) and o["strength_after"]["level"] == "cực vượng"      # MATCHES the book's verdict (cực vượng)
    outer = {x["name"]: x for x in o["geju"]["outer"]}
    assert outer["Tòng Vượng"]["quality"] == "chân" and outer["Nhuận Hạ"]["quality"] == "chân"           # the engine reads an outer cách; the book reads an ordinary vượng chart
    M = o["yongshen"]["methods"]
    assert M["cach_cuc_tvh"]["status"] == "khong_xac_dinh_noi_cach"                                       # NO MATCH: TVH's own special cách replaces the inner cách
    assert M["thuan_the_tvh"]["need_elements"] == ["Thủy"] and "ThucThuong" not in M["thuan_the_tvh"]["yong"]       # NO MATCH: book picks Giáp mộc (Thực Thương)
    assert M["dieu_hau"]["yong"] == ["Tai"] and ex["dung_than_groups"] == ["ThucThuong"]                    # NO MATCH: Quý tháng Tý puts Bính first
    assert M["phu_uc"]["status"] == "khong_ap_dung"                                                       # the system's Tòng Vượng chân switches phù ức off
    pu = yongshen.phu_uc({**o["strength_after"]}, False)                                                  # if phù ức were applied (as the book does), it AGREES with the book
    assert "ThucThuong" in pu["yong"] and set(ex["ky_than_groups"]) <= set(pu["ji"]) and "QuanSat" in pu["yong"]
    assert M["khuyet_hanh"]["yong"] == ["Tai"]                                                            # NO MATCH


# ------------------------------------------------------------------ API: every method keeps its own conclusion, nothing sums into a final dụng thần
FORBIDDEN = re.compile(r"final|winner|chosen|best|total_score|grand|overall|dung_than_cuoi|ket_luan_cuoi", re.I)


def _keys(x, path=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield f"{path}/{k}", k
            yield from _keys(v, f"{path}/{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from _keys(v, f"{path}[{i}]")


API_BODIES = [{"year": 1990, "month": 12, "day": 15, "hour": 10, "minute": 0, "gender": "male"}, {"year": 1973, "month": 1, "day": 3, "hour": 23, "minute": 30, "gender": "female"},
              {"year": 1952, "month": 12, "day": 7, "hour": 8, "minute": 0, "gender": "male"}, {"year": 2005, "month": 6, "day": 21, "hour": 12, "minute": 0, "gender": "female"}]


@pytest.mark.parametrize("body", API_BODIES, ids=lambda b: f"{b['year']}-{b['month']}-{b['day']}")
def test_api_structure_response_keeps_methods_separate_with_metadata_and_no_final_answer(body):
    from fastapi.testclient import TestClient
    from tvbt.api import app
    d = TestClient(app).post("/api/bazi-structure", json=body).json()
    Y = d["yongshen"]
    assert list(Y["methods"]) == ["phu_uc", "dieu_hau", "cach_cuc", "cach_cuc_tvh", "thong_quan", "thuan_the", "thuan_the_tvh", "khuyet_hanh"]
    for name, m in Y["methods"].items():
        assert set(m["meta"]) == META_KEYS and m["trace"] and m["meta"]["levels"]["empirical_validated"] == "no", name
    assert Y["comparison"]["no_final_answer"] is True and Y["isolation"]["tvh_school"] == "tvh_40"
    bad = [path for path, k in _keys(d) if FORBIDDEN.search(k) and k != "no_final_answer"]
    assert not bad, bad
    assert "yong" not in Y and "yong" not in d and "dung_than" not in d


def test_api_timeline_roles_are_per_method_and_there_is_no_merged_role():
    from fastapi.testclient import TestClient
    from tvbt.api import app
    d = TestClient(app).post("/api/bazi-timeline", json={**API_BODIES[0], "to_year": 2012}).json()
    for e in d["luck"] + d["years"]:
        assert list(e["roles"]) == ["phu_uc", "dieu_hau", "cach_cuc", "cach_cuc_tvh", "thong_quan", "thuan_the", "thuan_the_tvh", "khuyet_hanh"]
    bad = [path for path, k in _keys(d) if FORBIDDEN.search(k) and k != "no_final_answer"]
    assert not bad, bad


def test_method_output_metadata_and_trace_match_the_reviewed_snapshot_on_ex1_to_ex15():
    from bazi_deep_util import EX
    snap = json.loads((G / "bazi_deep_yongshen_snapshot.json").read_text("utf-8"))["charts"]
    assert set(snap) == set(EX)
    for k, t in EX.items():
        Y = pipeline.analyse(ChartView.from_names(t), TVH_40, with_rules=False)["yongshen"]
        got = {n: {"status": m["status"], "yong": m["yong"], "xi": m["xi"], "ji": m["ji"], "meta": m["meta"], "trace": m["trace"]} for n, m in Y["methods"].items()}
        got["_comparison_methods"], got["_isolation"] = Y["comparison"]["methods"], Y["isolation"]
        assert json.loads(json.dumps(got, ensure_ascii=False)) == snap[k], k
