from pathlib import Path

import pytest

from tvbt.knowledge import dsl
from tvbt.knowledge.schema import KnowledgeRule, Source, load_pack, validate_pack

FACTS = {"palace.sat_pha_tham_in_tam_phuong", "bazi.dm_has_root", "star.dignity", "x.n"}
PACK = Path(__file__).parent.parent / "data" / "pack_vn_draft.json"


def test_pack_valid_and_nothing_marked_verified():
    rules, sources = load_pack(PACK)
    assert validate_pack(rules, sources, FACTS) == []
    assert all(r.reviewStatus == "draft" for r in rules)  # honest: no source checked yet


def test_verified_requires_verified_source():
    rules, sources = load_pack(PACK)
    rules[0].reviewStatus = "verified"
    assert any("requires verified sources" in e for e in validate_pack(rules, sources, FACTS))


def test_rejects_unknown_fact_operator_and_code_injection():
    for bad in [{"fact": "nope", "value": 1}, {"fact": "x.n", "operator": "eval", "value": 1},
                {"fact": "x.n", "operator": "in", "value": 3}, {"__import__": "os"}, {"all": []}]:
        with pytest.raises(dsl.RuleError):
            dsl.validate(bad, FACTS)


def test_three_valued_evaluation():
    e = {"all": [{"fact": "x.n", "operator": "gte", "value": 2}, {"fact": "star.dignity", "operator": "in", "value": ["dac"]}]}
    assert dsl.evaluate(e, {"x.n": 3, "star.dignity": "dac"}) is True
    assert dsl.evaluate(e, {"x.n": 1}) is False          # one False decides
    assert dsl.evaluate(e, {"x.n": 3}) is None           # missing fact -> unknown, never silently False
    assert dsl.evaluate({"not": e}, {"x.n": 3}) is None
    assert dsl.evaluate({"any": e["all"]}, {"x.n": 3}) is True


def test_unknown_source_and_conflict_refs_detected():
    r = KnowledgeRule("R1", "tu_vi", "s", "c", "d", {"fact": "x.n", "value": 1}, [{"k": 1}],
                      conflictsWith=["R9"], sourceIds=["S9"])
    errs = validate_pack([r], [Source("S1", "t", None, None)], FACTS)
    assert any("unknown source" in e for e in errs) and any("conflictsWith" in e for e in errs)
