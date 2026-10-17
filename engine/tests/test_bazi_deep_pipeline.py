import json
from pathlib import Path

import pytest

from bazi_deep_util import EX, HOA1, SAVED, TONG1, view
from tvbt.bazi_deep import facts as bzf, pipeline
from tvbt.bazi_deep.profile import DEFAULT
from tvbt.knowledge.schema import validate_pack

EXPECTED = json.loads((Path(__file__).parent / "golden/bazi_deep_expected.json").read_text("utf-8"))
BASELINE = json.loads((Path(__file__).parent / "golden/bazi_deep_baseline.json").read_text("utf-8"))


def run(k, **kw):
    return pipeline.analyse(view(k, **kw) if k in EX else view(k, **kw))


def test_pack_is_valid_and_every_new_rule_is_draft():
    rules, sources = pipeline.load_structure_pack()
    assert validate_pack(rules, sources, pipeline.KNOWN) == []
    assert rules and all(r.reviewStatus == "draft" for r in rules)
    assert all(not s.verified and s.locator is None for s in sources)       # nothing here is source-verified yet


def test_a_verified_flag_on_these_unverified_sources_is_rejected():
    rules, sources = pipeline.load_structure_pack()
    import dataclasses
    bad = [dataclasses.replace(rules[0], reviewStatus="verified")]
    assert any("verified" in p for p in validate_pack(bad, sources, pipeline.KNOWN))


def test_every_claim_in_the_pack_has_vietnamese_phrasing():
    rules, _ = pipeline.load_structure_pack()
    claims = json.loads((pipeline.DATA / "claims_vi.json").read_text("utf-8"))
    for r in rules:
        for c in r.consequences:
            if c["kind"] == "finding":
                assert c["claim"] in claims, c["claim"]


def test_every_fact_a_rule_reads_is_produced_for_every_example():
    rules, _ = pipeline.load_structure_pack()
    from tvbt.knowledge import dsl
    for k in list(EX) + ["HOA1", "TONG1", "SAVED"]:
        out = run({"HOA1": HOA1, "TONG1": TONG1, "SAVED": SAVED}.get(k, k))
        for r in rules:
            for leaf in pipeline.engine._leaf_facts(r.conditions) if hasattr(pipeline.engine, "_leaf_facts") else []:
                assert leaf in out["facts"] or leaf.startswith("derived."), (k, r.id, leaf)
        assert out["reasoning"]["pack_problems"] == []
        assert all(not p["missing_facts"] or all(m.startswith("derived.") for m in p["missing_facts"]) for p in out["reasoning"]["pending"]), k


def test_pipeline_matches_the_reviewed_snapshot_for_all_fifteen_examples():
    for k in EX:
        o = run(k)
        got = {"levels": [o["strength_raw"]["level"], o["strength_after"]["level"]],
               "inner": [(c["name"], c["state"]) for c in o["geju"]["inner"]], "outer": [(c["name"], c["quality"]) for c in o["geju"]["outer"]],
               "hua_state": o["facts"]["bazi.hua_state"], "cuc": o["facts"]["bazi.cuc_formed"],
               "fired": sorted(f[0] for f in o["reasoning"]["fired"])}
        assert json.loads(json.dumps(got)) == EXPECTED[k], k


def test_findings_carry_provenance_down_to_an_analyzer_step():
    o = run("EX3")
    f = next(x for x in o["reasoning"]["findings"] if x["claim"] == "bt_cach_bai_chua_cuu")
    kinds = [c["kind"] for c in f["chain"]]
    assert "rule" in kinds and "source" in kinds and "fact" in kinds
    fact = next(c for c in f["chain"] if c["kind"] == "fact")
    assert fact["origin"] == "geju.evaluate" and "trạng thái cách" in fact["text"]


def test_multi_hop_rule_uses_a_derived_fact_and_reports_depth_two():
    o = pipeline.reason({"chart": {**run("EX3")["facts"], "bazi.geju_state": "bai", "bazi.dm_ambiguous": True, "bazi.geju_outer_quality": ""}})
    fired = {f[0]: f[2] for f in o["fired"]}
    assert fired["BT_ST_GEJU_BAI"] == 1 and fired["BT_ST_CUU_NEEDED"] == 2
    assert o["derived"]["derived.bazi.can_xet_cuu_ung"] is True


def test_exception_blocks_the_rule_and_is_reported():
    base = {"chart": {**run("EX3")["facts"], "bazi.geju_state": "bai", "bazi.geju_outer_quality": "chân"}}
    o = pipeline.reason(base)
    assert any(b["rule"] == "BT_ST_GEJU_BAI" for b in o["blocked"])
    assert "bt_cach_bai_chua_cuu" not in {f["claim"] for f in o["findings"]}
    assert "derived.bazi.can_xet_cuu_ung" not in o["derived"]


def test_phu_uc_findings_are_suppressed_when_the_level_is_ambiguous_or_outer_cach_is_true():
    claims = lambda o: {f["claim"] for f in o["reasoning"]["findings"]}
    assert "bt_dm_nhuoc_phu_uc" not in claims(run("EX2"))          # EX2: weak but ambiguous
    assert "bt_dm_nhuoc_phu_uc" in claims(run("EX3"))
    assert "bt_dm_nhuoc_phu_uc" not in claims(run(TONG1))          # true Tòng: phù ức must not be asserted


def test_text_is_deterministic_and_has_no_forecast_wording():
    for k in EX:
        a, b = run(k)["reasoning"]["text"], run(k)["reasoning"]["text"]
        assert a == b
        low = a.lower()
        assert "chắc chắn sẽ" not in low and "nhất định sẽ" not in low


def test_nothing_in_the_output_claims_verified_basis():
    for k in EX:
        assert all(f["basis"] == "draft" for f in run(k)["reasoning"]["findings"]), k
        assert run(k)["profile"]["review_status"] == "draft"


def test_profile_swap_changes_only_documented_outputs():
    v = view("EX1")
    a = pipeline.analyse(v, with_rules=False)
    b = pipeline.analyse(v, DEFAULT.with_(cuc_share={"meeting": 0.0, "triad": 0.0, "semi": 0.0, "cung": 0.0}, cuc_thau_bonus=0.0), with_rules=False)
    assert a["strength_after"]["ratio"] != b["strength_after"]["ratio"]
    assert a["strength_raw"] == b["strength_raw"]                        # nguyên cục does not depend on the cục policy
    assert a["interactions"][0]["kind"] == b["interactions"][0]["kind"]


def test_old_pipeline_outputs_are_untouched_regression():
    """The frozen pre-upgrade view of EX1-EX15 still reproduces from the unchanged old functions."""
    import importlib.util, sys
    spec = importlib.util.spec_from_file_location("bz_base", Path(__file__).resolve().parent.parent.parent / "tools/bazi_deep_baseline.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    for k, t in EX.items():
        assert mod.old_view(t) == BASELINE[k], k


def test_tu_lenh_days_flow_through_the_pipeline():
    o = pipeline.analyse(view("EX1", 3.0), with_rules=False)
    assert o["season"]["command"]["name"] == "Mậu"
    assert pipeline.analyse(view("EX1"), with_rules=False)["season"]["command"] is None


def test_from_bazi_converts_birth_instant_to_days_into_month():
    from tvbt import bazi
    from tvbt.bazi_deep.model import ChartView
    from tvbt.calendar_core import BirthInput, normalize
    nb = normalize(BirthInput(1990, 12, 15, 10, 0, "Asia/Ho_Chi_Minh", "male"))
    bz = bazi.compute(nb)
    v = ChartView.from_bazi(bz, nb.utc)
    assert v.name() == " / ".join(bz.pillars[k].name for k in ("year", "month", "day", "hour"))
    assert 0 <= v.days_into_month < 32                                   # Đại Tuyết 7 Dec -> about 8 days in
    assert 7 < v.days_into_month < 9.5
    o = pipeline.analyse(v, with_rules=False)
    assert o["season"]["command"] is not None
