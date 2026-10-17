"""Phase 6: production-readiness checks. Nothing here adds a method. It covers: 5,000-chart two-way school isolation, the proposed API contract (schema + UI strings),
backward compatibility with d0c3ab8, no leak of experimental content, provenance of examples 4 and 5, and the reviewer intake for the 120 cells."""
import copy
import csv
import json
import random
import re
import sys
from pathlib import Path

import pytest

from tvbt.bazi_deep import dieuhau, pipeline, yongshen
from tvbt.bazi_deep.model import ChartView
from tvbt.bazi_deep.profile import DEFAULT, TVH_40

ROOT = Path(__file__).resolve().parent.parent.parent
G = Path(__file__).parent / "golden"
BOOK = json.loads((G / "tvh_dungthan_examples.json").read_text("utf-8"))
S10 = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
B12 = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
SYS = ("phu_uc", "dieu_hau", "cach_cuc", "thong_quan", "thuan_the", "khuyet_hanh")
TVH = ("cach_cuc_tvh", "thuan_the_tvh")


def _cyc(i):
    return f"{S10[i % 10]} {B12[i % 12]}"


def _chart(y, mb, d, hb):
    ms = (((y % 10) % 5) * 2 + 2 + ((mb - 2) % 12)) % 10
    hs = ((d % 10) * 2 + hb) % 10
    return f"{_cyc(y)} / {S10[ms]} {B12[mb]} / {_cyc(d)} / {S10[hs]} {B12[hb]}"


def sample5000():
    """Every (day pillar × month branch) pair appears at least once (720 charts, random year and hour), the rest is uniform random."""
    r = random.Random(61017)
    out = [_chart(r.randrange(60), mb, d, r.randrange(12)) for d in range(60) for mb in range(12)]
    out += [_chart(r.randrange(60), r.randrange(12), r.randrange(60), r.randrange(12)) for _ in range(5000 - len(out))]
    return out


CHARTS = sample5000()
_cache = {}


def run(p, profile=TVH_40):
    k = (p, id(profile))
    if k not in _cache:
        _cache[k] = pipeline.analyse(ChartView.from_names(p), profile, with_rules=False)
    return _cache[k]


def core(m):
    return {k: v for k, v in m.items() if k not in ("meta", "trace", "table", "climate")}


def innerkey(o):
    return [(c["name"], c["state"]) for c in o["geju"]["inner"]]


def sys_outer(o):
    return [(x["name"], x["quality"]) for x in o["geju"]["outer"] if x.get("kind") not in yongshen.TVH_KINDS]


# ------------------------------------------------------------------ 2. 5,000-chart two-way isolation
def test_sample_has_5000_distinct_enough_charts_covering_every_day_pillar_and_month():
    assert len(CHARTS) == 5000 and len(set(CHARTS)) >= 4800
    days = {c.split(" / ")[2] for c in CHARTS}
    months = {c.split(" / ")[1].split()[1] for c in CHARTS}
    assert len(days) == 60 and len(months) == 12


def test_special_classes_are_all_well_populated_in_the_5000():
    from collections import Counter
    c = Counter()
    for p in CHARTS:
        o = run(p)
        a = run(p, DEFAULT)
        tv = o["strength_after"]["tvh"]
        tvh_out = [x for x in o["geju"]["outer"] if x.get("kind") in yongshen.TVH_KINDS]
        sys_chan = [x for x in a["geju"]["outer"] if x["quality"] == "chân"]
        c["system_chan"] += bool(sys_chan)
        c["tvh_special"] += bool(tvh_out)
        c["tvh_tong"] += any(x["kind"] == "tong_tvh" for x in tvh_out)
        c["tvh_chuyen_or_hoa"] += any(x["kind"] != "tong_tvh" for x in tvh_out)
        c["both"] += bool(sys_chan and tvh_out)
        c["near_40"] += abs(tv["own_share"] - 0.40) < DEFAULT.tvh_margin
        c["exactly_around_40"] += abs(tv["own_share"] - 0.40) < 0.005
        c["strong"] += tv["dm_strong"]
        c["weak"] += not tv["dm_strong"]
        c["disagree"] += bool(o["yongshen"]["comparison"]["disagreements"])
        c["no_inner"] += not o["geju"]["inner"]
    for k, n in (("system_chan", 50), ("tvh_special", 150), ("tvh_tong", 20), ("tvh_chuyen_or_hoa", 50), ("both", 10), ("near_40", 150), ("strong", 1500), ("weak", 1500), ("disagree", 2000)):
        assert c[k] >= n, (k, c[k])


def test_forward_invariant_tvh_profile_on_or_off_never_changes_the_system_side_in_5000_charts():
    for p in CHARTS:
        a, b = run(p, DEFAULT), run(p)
        for m in SYS:
            assert core(a["yongshen"]["methods"][m]) == core(b["yongshen"]["methods"][m]), (m, p)
        assert innerkey(a) == innerkey(b) and sys_outer(a) == [(x["name"], x["quality"]) for x in b["geju"]["outer"] if x.get("kind") not in yongshen.TVH_KINDS], p
        assert [c["name"] for c in a["geju"]["inner"]] == [c["name"] for c in b["geju"]["inner"]]
        assert a["yongshen"]["methods"]["cach_cuc_tvh"]["meta"]["strength_basis"].startswith("he_thong") and "tvh" not in a["strength_after"]


SYSTEM_ONLY = [{"level_cuts": (0.10, 0.20, 0.30, 0.60, 0.70, 0.90)}, {"presence_share": 0.20}, {"thuong_vuong": 0.10}, {"tong_cuong_min": 0.40}, {"tong_vuong_ti": 0.30}, {"tong_foe_max": 0.30},
               {"tong_the_each": 0.05}, {"tong_dominant_share": 0.30}, {"tong_chan_tia": 0.50}, {"tong_gia_tia": 0.60}, {"tong_max_ratio": 0.60}, {"war_share": 0.05}, {"bridge_min": 0.50},
               {"hua_du_share": 0.10}, {"flow_min": 0.30}, {"hidden_frac": {1: (1.0,), 2: (0.5, 0.5), 3: (0.4, 0.3, 0.3)}},
               {"season_factor": {"vượng": 3.0, "tướng": 2.0, "hưu": 1.0, "tù": 0.2, "tử": 0.1}}, {"class_weight": {"ban_khi": 1.0, "trung_khi": 1.0, "du_khi": 1.0}}, {"kho_policy": "tu_co_can"},
               {"level_margin": 0.10}]
TVH_ONLY = [{"tvh_no_help": 0.40}, {"tvh_tong_main": 0.10}, {"chuyen_vuong_chars": 3}, {"chuyen_vuong_share": 0.30}, {"tvh_margin": 0.10}]


@pytest.mark.parametrize("change", SYSTEM_ONLY, ids=lambda c: next(iter(c)))
def test_reverse_invariant_changing_a_system_only_parameter_never_changes_tvh_on_1667_charts(change):
    alt = TVH_40.with_(**change)
    # season_factor and class_weight also feed interact.resolve (the shared interaction layer), which decides which stems are still 'active'; that only touches the
    # presence annotation yong_health, never a method's status/yong/xi/ji. Every other parameter must not change even that.
    sl = CHARTS[::3]                                     # 1,667 charts × 20 perturbations (the profile-toggle invariants above run on all 5,000)
    drop = ("yong_health", "xi_health") if set(change) & {"season_factor", "class_weight"} else ()
    strip = lambda m: {k: v for k, v in core(m).items() if k not in drop}
    for p in sl:
        a = run(p)
        b = pipeline.analyse(ChartView.from_names(p), alt, with_rules=False)
        for m in TVH:
            assert strip(a["yongshen"]["methods"][m]) == strip(b["yongshen"]["methods"][m]), (change, m, p)
        assert a["strength_after"]["tvh"] == b["strength_after"]["tvh"], (change, p)
        assert [x for x in a["geju"]["outer"] if x.get("kind") in yongshen.TVH_KINDS] == [x for x in b["geju"]["outer"] if x.get("kind") in yongshen.TVH_KINDS], (change, p)


@pytest.mark.parametrize("change", TVH_ONLY, ids=lambda c: next(iter(c)))
def test_forward_invariant_changing_a_tvh_only_parameter_never_changes_the_system_side_on_1667_charts(change):
    alt = TVH_40.with_(**change)
    for p in CHARTS[::3]:
        a = run(p)
        b = pipeline.analyse(ChartView.from_names(p), alt, with_rules=False)
        for m in SYS:
            assert core(a["yongshen"]["methods"][m]) == core(b["yongshen"]["methods"][m]), (change, m, p)
        assert innerkey(a) == innerkey(b) and sys_outer(a) == sys_outer(b), (change, p)


def test_tvh_methods_see_only_tvh_cach_and_the_system_methods_only_system_cach_on_5000_charts():
    n = 0
    for p in CHARTS:
        o, a = run(p), run(p, DEFAULT)
        M = o["yongshen"]["methods"]
        tvh_out = [x for x in o["geju"]["outer"] if x.get("kind") in yongshen.TVH_KINDS and x["quality"] == "chân"]
        sys_chan = [x for x in a["geju"]["outer"] if x["quality"] == "chân"]
        if tvh_out:
            assert M["thuan_the_tvh"]["status"] == "ap_dung" and M["thuan_the_tvh"]["outer"] == tvh_out[0]["name"] and M["cach_cuc_tvh"]["status"] == "khong_xac_dinh_noi_cach", p
        else:
            assert M["thuan_the_tvh"]["status"] == "khong_chan", p
            if o["geju"]["inner"] and sys_chan:
                n += 1
                assert M["cach_cuc_tvh"]["status"] != "khong_xac_dinh_noi_cach" or o["geju"]["inner"][0]["name"] not in yongshen.TVH_DT["cach_key"], p
        if sys_chan:
            assert M["cach_cuc"]["status"] == "khong_xac_dinh_noi_cach" and M["phu_uc"]["status"] == "khong_ap_dung", p
        assert not any(k in M["thuan_the"] for k in ("threshold",)) and M["thuan_the"]["status"] in ("khong_chan", "chi_co_gia", "ap_dung")
    assert n >= 20


def test_threshold_40_is_consistent_with_the_flag_the_two_readings_and_the_rule_on_5000_charts():
    n_two = 0
    for p in CHARTS:
        o = run(p)
        c = o["yongshen"]["methods"]["cach_cuc_tvh"]
        tv = o["strength_after"]["tvh"]
        assert tv["dm_strong"] == (tv["own_share"] >= 0.40) or abs(tv["own_share"] - 0.40) < 1e-4, p        # rounding of own_share to 4 dp only matters at the edge
        if "threshold" not in c:
            continue
        t = c["threshold"]
        assert t["near_threshold"] == (abs(tv["own_share"] - 0.40) < t["margin_heuristic"]) and (c["status"] == "hai_cach_doc") == t["near_threshold"], p
        if t["near_threshold"]:
            n_two += 1
            assert sorted(a["dm_vi"] for a in c["alternatives"]) == ["nhược", "vượng"] and sum(a["follows_book_rule"] for a in c["alternatives"]) == 1, p
            assert o["yongshen"]["methods"]["phu_uc"]["meta"]["strength_basis"].startswith("he_thong")
    assert n_two >= 150


def test_phu_uc_never_reads_the_40_percent_decision_by_design():
    differing_from_tvh_decision = 0
    for p in CHARTS[:1500]:
        o = run(p)
        pu = o["yongshen"]["methods"]["phu_uc"]
        tv = o["strength_after"]["tvh"]
        if pu["status"] == "ap_dung":
            sys_weak = pu["level"] in ("cực nhược", "nhược", "thiên nhược")
            differing_from_tvh_decision += sys_weak == tv["dm_strong"]
        assert pu["meta"]["strength_basis"].startswith("he_thong") and "tách khỏi" in pu["meta"]["strength_basis"], p
    assert differing_from_tvh_decision >= 100          # the two decisions really disagree on many charts: this is the intended consequence of isolation, not an accident


def test_repeated_runs_are_byte_identical_on_a_500_chart_slice():
    for p in CHARTS[::10]:
        a = json.dumps(pipeline.analyse(ChartView.from_names(p), TVH_40, with_rules=False)["yongshen"], ensure_ascii=False)
        assert a == json.dumps(run(p)["yongshen"], ensure_ascii=False), p


# ------------------------------------------------------------------ 4. API contract: schema + UI strings
SCHEMA = json.loads((ROOT / "docs/bazi_deep_yongshen_contract.schema.json").read_text("utf-8"))
UI = json.loads((ROOT / "docs/bazi_deep_ui_strings_vi.json").read_text("utf-8"))
_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None), "number": (int, float)}


def validate(x, sch, root=SCHEMA, path="$"):
    """Minimal JSON-Schema subset validator (no new dependency): $ref, type (string or list), required, properties, additionalProperties(schema), enum, const, items, minItems, minLength."""
    errs = []
    if "$ref" in sch:
        node = root
        for part in sch["$ref"].lstrip("#/").split("/"):
            node = node[part]
        return validate(x, node, root, path)
    if "type" in sch:
        ts = sch["type"] if isinstance(sch["type"], list) else [sch["type"]]
        if not any(isinstance(x, _TYPES[t]) and not (t == "number" and isinstance(x, bool)) for t in ts):
            return [f"{path}: type {type(x).__name__} not in {ts}"]
    if "const" in sch and x != sch["const"]:
        errs.append(f"{path}: {x!r} != const {sch['const']!r}")
    if "enum" in sch and x not in sch["enum"]:
        errs.append(f"{path}: {x!r} not in {sch['enum']}")
    if isinstance(x, str) and len(x) < sch.get("minLength", 0):
        errs.append(f"{path}: shorter than {sch['minLength']}")
    if isinstance(x, dict):
        for k in sch.get("required", []):
            if k not in x:
                errs.append(f"{path}: missing {k}")
        for k, sub in sch.get("properties", {}).items():
            if k in x:
                errs += validate(x[k], sub, root, f"{path}.{k}")
        ap = sch.get("additionalProperties")
        if isinstance(ap, dict):
            for k, v in x.items():
                if k not in sch.get("properties", {}):
                    errs += validate(v, ap, root, f"{path}.{k}")
    if isinstance(x, list):
        if len(x) < sch.get("minItems", 0):
            errs.append(f"{path}: fewer than {sch['minItems']} items")
        if "items" in sch:
            for i, v in enumerate(x):
                errs += validate(v, sch["items"], root, f"{path}[{i}]")
    return errs


def test_the_schema_validator_itself_rejects_what_it_should():
    ok = run(CHARTS[0])["yongshen"]
    assert validate(ok, SCHEMA) == []
    bad = copy.deepcopy(ok)
    bad["methods"]["phu_uc"]["meta"]["levels"]["empirical_validated"] = "yes"
    del bad["methods"]["dieu_hau"]["trace"]
    bad["comparison"]["no_final_answer"] = False
    bad["methods"]["cach_cuc"]["meta"]["levels"]["source_rule_verified"] = "proven"
    errs = validate(bad, SCHEMA)
    assert any("empirical_validated" in e for e in errs) and any("missing trace" in e for e in errs) and any("no_final_answer" in e for e in errs) and any("source_rule_verified" in e for e in errs)


def test_every_pipeline_output_in_a_500_chart_slice_satisfies_the_contract():
    for p in CHARTS[::10]:
        assert validate(run(p)["yongshen"], SCHEMA) == [], p


API_BODIES = [{"year": 1990, "month": 12, "day": 15, "hour": 10, "minute": 0, "gender": "male"}, {"year": 1973, "month": 1, "day": 3, "hour": 23, "minute": 30, "gender": "female"},
              {"year": 1952, "month": 12, "day": 7, "hour": 8, "minute": 0, "gender": "male"}, {"year": 2005, "month": 6, "day": 21, "hour": 12, "minute": 0, "gender": "female"}]


@pytest.mark.parametrize("body", API_BODIES, ids=lambda b: f"{b['year']}-{b['month']}-{b['day']}")
def test_api_response_satisfies_the_contract_and_exposes_the_conflict_flag_where_the_ui_will_look(body):
    from fastapi.testclient import TestClient
    from tvbt.api import app
    d = TestClient(app).post("/api/bazi-structure", json=body).json()
    assert validate(d["yongshen"], SCHEMA) == []
    tb = d["yongshen"]["methods"]["dieu_hau"]["table"]
    assert "book_internal_conflict" in tb and (tb["book_internal_conflict"] is None or set(tb["book_internal_conflict"]) == {"note_only", "table_only"})
    text = json.dumps(d, ensure_ascii=False)
    assert "experimental" not in text.lower() and "formation_provenance" not in text


def test_ui_strings_label_every_enum_value_and_never_overclaim():
    lv = SCHEMA["definitions"]["level"]["enum"]
    for k in ("transcription_verified", "source_rule_verified", "empirical_validated"):
        assert k in UI["level_names"]
        assert set(UI["level_values"][k]) == set(lv), k
    assert set(UI["method_titles"]) == set(SCHEMA["properties"]["methods"]["required"])
    assert set(UI["verification_badges"]) == {"verified", "partial", "draft"}
    for s in ("no_unified_conclusion", "agreement_not_proof", "single_method", "two_readings", "book_internal_conflict", "reconstructed_example", "draft_banner"):
        assert UI["states"][s]
    texts = [t for d in (UI["level_names"], UI["level_values"]["transcription_verified"], UI["level_values"]["source_rule_verified"], UI["level_values"]["empirical_validated"], UI["verification_badges"], UI["states"], UI["method_titles"]) for t in d.values()]
    for t in texts:
        low = t.lower()
        assert not any(f in low for f in UI["forbidden_phrases"]), t
    assert "Chưa có kiểm chứng" in UI["level_values"]["empirical_validated"]["no"]


def _unified_state(Y):
    """The rule the contract tells the UI to apply (documented in docs/BAZI_DEEP_API_CONTRACT.md); kept here only to test that the data it needs is always present."""
    applied = [n for n, m in Y["methods"].items() if m["meta"]["applied"]]
    if Y["comparison"]["disagreements"]:
        return "no_unified_conclusion"
    if len(applied) >= 2 and Y["comparison"]["consensus"]:
        return "agreement_not_proof"
    return "single_method" if len(applied) == 1 else "no_unified_conclusion"


def test_the_ui_state_rule_never_yields_a_unified_conclusion_and_all_states_occur():
    seen = set()
    for p in CHARTS[:1500]:
        seen.add(_unified_state(run(p)["yongshen"]))
    assert seen == {"no_unified_conclusion", "agreement_not_proof", "single_method"} or seen == {"no_unified_conclusion", "agreement_not_proof"}
    assert "no_unified_conclusion" in seen and "agreement_not_proof" in seen


# ------------------------------------------------------------------ 5. backward compatibility, experimental leak, provenance
def _paths(x, p=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield f"{p}/{k}"
            yield from _paths(v, f"{p}/{k}")
    elif isinstance(x, list):
        for v in x:
            yield from _paths(v, p + "[]")


def test_every_response_key_of_d0c3ab8_still_exists_additive_only():
    from fastapi.testclient import TestClient
    from tvbt.api import app
    old = json.loads((G / "api_keypaths_d0c3ab8.json").read_text("utf-8"))
    C = TestClient(app)
    bodies = [API_BODIES[0], API_BODIES[1], API_BODIES[2]]
    for ep, extra in (("/api/bazi-structure", {}), ("/api/bazi-timeline", {"to_year": 2000})):
        now = set()
        for b in bodies:
            now |= set(_paths(C.post(ep, json={**b, **extra}).json()))
        # a method's free-text `note` exists only for some statuses (e.g. cach_cuc_tvh 'khong_xac_dinh_noi_cach'); since Phase 5 the system's outer cách no longer
        # replaces the TVH inner cách, so for 1990-12-15 that status, and with it that note, legitimately disappears. Nothing else may.
        status_dependent = re.compile(r"^/yongshen/methods/[a-z_]+/note$")
        missing = [p for p in old[ep] if p not in now and not status_dependent.match(p)]
        assert not missing, (ep, missing[:10])


def test_bazi_deep_code_and_data_never_read_experimental_content():
    for f in list((ROOT / "engine/tvbt/bazi_deep").glob("*.py")) + list((ROOT / "engine/data/bazi_deep").glob("*.json")):
        t = f.read_text("utf-8").lower()
        assert "experimental" not in t and "formation_provenance" not in t and "formations_experimental" not in t, f.name


def test_every_fixture_names_its_source_pages_and_marks_reconstruction():
    for k, v in BOOK["dungthan_examples"].items():
        assert v["page"] and v["pillars"] and v["book"]["dm_verdict"] and v["book"]["steps"], k
    for k, v in BOOK["dieuhau_examples"].items():
        if not k.startswith("_"):
            assert v["page"] in (387, 388) and v["dung_than_groups"], k
    assert [k for k, v in BOOK["dungthan_examples"].items() if v.get("reconstructed")] == ["p400_vd4"]


# ------------------------------------------------------------------ 1. examples 4 and 5: reconstructed versus read directly
def test_example_4_provenance_is_given_per_pillar_and_only_the_day_is_reconstructed():
    b = BOOK["dungthan_examples"]["p400_vd4"]["pillar_basis"]
    assert b["year"].startswith("read_directly") and b["hour"].startswith("read_directly") and b["month"].startswith("derived") and b["day"].startswith("reconstructed")


def test_example_5_is_read_directly_and_its_result_is_pinned_as_partial():
    ex = BOOK["dungthan_examples"]["p401_vd5"]
    assert ex["reconstructed"] is False and ex["pillar_basis"].startswith("read_directly") and "chưa có lượt chép mù" in ex["pillar_basis"]
    o = run(ex["pillars"])
    tv = o["strength_after"]["tvh"]
    assert tv["dm_strong"] is True and tv["own_share"] == pytest.approx(0.5013, abs=1e-4)                   # book: vượng — MATCH
    M = o["yongshen"]["methods"]
    book = set(ex["book"]["dung_than_groups"])                                                               # Thủy (ThucThuong) and Mộc (Tai)
    d = M["dieu_hau"]
    assert set(d["yong"] + d["xi"]) == book                                                                  # MATCH as a set (Canh tháng Tuất: giáp, nhâm)
    assert M["khuyet_hanh"]["need_elements"] == ["Thủy"] and M["khuyet_hanh"]["yong"] == ["ThucThuong"]     # PARTIAL: finds Thủy, not Mộc
    c = M["cach_cuc_tvh"]
    assert c["yong"] == ["QuanSat"] and "QuanSat" in ex["book"]["ky_than_groups"]                           # CONFLICT: the table's dụng is the book's kỵ (Hỏa)
    assert "Ti" in c["ji"] and ex["book"]["hi_than_groups"] == ["Ti"]                                      # CONFLICT: the table's kỵ includes the book's hỉ (Kim)
    assert M["phu_uc"]["yong"] == ["QuanSat", "ThucThuong", "Tai"] and "Ti" in M["phu_uc"]["ji"]            # partial: contains the book's picks, also rejects its hỉ


# ------------------------------------------------------------------ 1. reviewer intake for the 120 cells
sys.path.insert(0, str(ROOT / "tools"))
import bazi_deep_tvh_review_intake as intake  # noqa: E402


def _template():
    with open(ROOT / "docs/bazi_deep_tvh_cells_check.csv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _fill(rows, who, mistakes=None):
    out = []
    for r in rows:
        r = dict(r)
        m, s = r["thang"], r["can_ngay"]
        r.update(nguoi_kiem=who, bang_theo_anh=" ".join(dieuhau._TVH[m][s]), chu_thich_theo_anh=" ".join(dieuhau._ORDER[m][s]), ket_qua="khop")
        if mistakes and (m, s) in mistakes:
            r.update(mistakes[(m, s)])
        out.append(r)
    return out


def test_blank_template_is_all_no_review_and_the_nine_conflicts_stay_flagged():
    r = intake.check([_template()])
    assert r["counts"] == {"no_review": 120} and r["conflicts_kept"] == 9 and r["problems"] == []


def test_one_reviewer_matching_everything_gives_confirmed_1_and_two_give_confirmed_2_but_conflicts_stay():
    t = _template()
    r1 = intake.check([_fill(t, "A")])
    assert r1["counts"] == {"confirmed_1": 120} and r1["conflicts_kept"] == 9
    r2 = intake.check([_fill(t, "A"), _fill(t, "B")])
    assert r2["counts"] == {"confirmed_2": 120} and r2["conflicts_kept"] == 9
    assert sum(c["book_internal_conflict"] for c in r2["cells"].values()) == 9               # confirmation of the transcription never resolves a book conflict
    same = intake.check([_fill(t, "A"), _fill(t, "A")])
    assert same["counts"] == {"confirmed_1": 120}                                           # the same person twice is not a second reviewer


def test_a_planted_discrepancy_is_found_and_reported_exactly():
    t = _template()
    r = intake.check([_fill(t, "A", {("Thìn", "Ất"): {"bang_theo_anh": "Quý Bính", "ket_qua": "khop"}, ("Tuất", "Kỷ"): {"ket_qua": "khong_doc_duoc"}})])
    assert r["cells"][("Thìn", "Ất")]["status"] == "disagrees" and r["cells"][("Tuất", "Kỷ")]["status"] == "unreadable"
    assert r["counts"] == {"confirmed_1": 118, "disagrees": 1, "unreadable": 1}
    assert r["cells"][("Thìn", "Ất")]["differences"][0]["table_seen"] == ["Quý", "Bính"]


def test_two_reviewers_who_differ_are_a_disagreement_and_bad_input_is_reported():
    t = _template()
    r = intake.check([_fill(t, "A"), _fill(t, "B", {("Dần", "Giáp"): {"chu_thich_theo_anh": "Quý Bính"}})])
    assert r["cells"][("Dần", "Giáp")]["status"] == "disagrees" and r["counts"]["confirmed_2"] == 119
    bad = _fill(t, "A")
    bad[0]["ket_qua"] = "ok"
    bad[1]["nguoi_kiem"] = ""
    pr = intake.check([bad])["problems"]
    assert len(pr) == 2 and any("not in" in x for x in pr) and any("without nguoi_kiem" in x for x in pr)
    assert any("exactly the 120" in x for x in intake.check([t[:119]])["problems"])


def test_the_intake_never_writes_engine_data():
    f = ROOT / "engine/data/bazi_deep/tvh_dieuhau.json"
    before = f.read_bytes()
    intake.check([_fill(_template(), "A")])
    assert f.read_bytes() == before
