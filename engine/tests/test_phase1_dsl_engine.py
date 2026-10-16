"""Phase 1 engine mechanics with SYNTHETIC fixture rules (not doctrine): cross-palace refs, count, new operators, three-valued logic,
exceptions, conflictsWith, multi-hop assert chains. Doctrine-looking content lives only in data/experimental and is tested elsewhere."""
import pytest

from phase1_helpers import base_facts
from tvbt.knowledge import dsl
from tvbt.knowledge.schema import KnowledgeRule, Source, validate_pack
from tvbt.reasoning import conflict, engine

F = {"palace.*", "chart.*", "bazi.*", "derived.*"}
SRC = [Source("S_FIX", "synthetic fixture", None, None, False)]


def R(id, cond, cons, status="draft", exc=None, conflicts=None, prio=0, subject="palace"):
    return KnowledgeRule(id, "tu_vi", "fix", "fixture", id, cond, cons, exceptions=exc or [], conflictsWith=conflicts or [],
                         priority=prio, sourceIds=["S_FIX"], reviewStatus=status, subject=subject)


def fact(n, op="eq", v=True):
    return {"fact": n, "operator": op, "value": v}


def ref(p, n, op="eq", v=True):
    return {"ref": {"palace": p, "fact": n}, "operator": op, "value": v}


def world_of(base):
    return lambda name: base.get(f"palace:{name}")


# ---- new operators ------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("op,want,got,res", [
    ("contains_any", ["a", "z"], ["a", "b"], True), ("contains_any", ["y", "z"], ["a", "b"], False),
    ("contains_all", ["a", "b"], ["a", "b", "c"], True), ("contains_all", ["a", "q"], ["a", "b"], False),
    ("not_contains", "q", ["a"], True), ("not_contains", "a", ["a"], False)])
def test_new_list_operators(op, want, got, res):
    assert dsl.evaluate({"fact": "x", "operator": op, "value": want}, {"x": got}) is res


def test_incomparable_values_are_unknown_not_false():
    assert dsl.evaluate(fact("x", "gte", 2), {"x": None}) is None


def test_validation_rejects_bad_shapes():
    for bad in [{"ref": {"palace": "opp"}, "operator": "eq", "value": 1},                     # missing fact
                {"ref": {"palace": "opp", "fact": "nope.x"}, "operator": "eq", "value": 1},   # unknown fact namespace
                {"count": [], "operator": "gte", "value": 1},
                {"count": [fact("palace.a")], "operator": "contains", "value": 1},
                {"fact": "palace.a", "operator": "contains_any", "value": "notalist"}]:
        with pytest.raises(dsl.RuleError):
            dsl.validate(bad, F)
    dsl.validate({"count": [fact("palace.a"), ref("opp", "palace.b")], "operator": "gte", "value": 1}, F)


# ---- ref: reading another palace -------------------------------------------------------------------------------------------
def test_ref_by_role_and_by_name():
    b = base_facts([("star", "Tử Vi", "Thiên Di"), ("star", "Tả Phụ", "Quan Lộc")])
    f, w = b["palace:Mệnh"], world_of(b)
    assert dsl.evaluate(ref("opp", "palace.own_major_stars", "contains", "Tử Vi"), f, w) is True
    assert dsl.evaluate(ref("trine1", "palace.own_stars", "contains", "Tả Phụ"), f, w) is True
    assert dsl.evaluate(ref("Quan Lộc", "palace.own_stars", "contains", "Tả Phụ"), f, w) is True
    assert dsl.evaluate(ref("opp", "palace.own_stars", "contains", "Tả Phụ"), f, w) is False


def test_ref_without_world_or_unknown_target_is_unknown():
    b = base_facts()
    assert dsl.evaluate(ref("opp", "palace.name", "eq", "Thiên Di"), b["palace:Mệnh"]) is None
    assert dsl.evaluate(ref("Không Có Cung", "palace.name", "eq", "x"), b["palace:Mệnh"], world_of(b)) is None
    assert dsl.evaluate(ref("opp", "palace.nonexistent", "eq", 1), b["palace:Mệnh"], world_of(b)) is None


def test_ref_role_is_relative_to_the_palace_being_evaluated():
    b = base_facts([("star", "Cự Môn", "Thiên Di")])
    # from Quan Lộc the xung chiếu palace is Phu Thê/other, NOT Thiên Di: the same role resolves differently per subject
    assert dsl.evaluate(ref("opp", "palace.own_stars", "contains", "Cự Môn"), b["palace:Mệnh"], world_of(b)) is True
    assert dsl.evaluate(ref("opp", "palace.own_stars", "contains", "Cự Môn"), b["palace:Quan Lộc"], world_of(b)) is False


# ---- count -------------------------------------------------------------------------------------------------------------------
def test_count_gte_and_three_valued_bounds():
    c = {"count": [fact("a"), fact("b"), fact("c")], "operator": "gte", "value": 2}
    assert dsl.evaluate(c, {"a": True, "b": True, "c": False}) is True
    assert dsl.evaluate(c, {"a": True, "b": False, "c": False}) is False
    assert dsl.evaluate(c, {"a": True, "b": False}) is None            # c unknown: could be 1 or 2 -> undecided
    assert dsl.evaluate(c, {"a": True, "b": True}) is True             # already 2 true: unknown c cannot change the answer
    assert dsl.evaluate(c, {"a": False, "b": False}) is False          # at most 1 even if c is true


# ---- engine: cross-palace rules, exceptions, multi-hop, conflictsWith ------------------------------------------------------
def test_engine_rule_reads_other_palaces_and_records_provenance():
    b = base_facts([("star", "Tử Vi", "Mệnh"), ("star", "Thiên Phủ", "Thiên Di")])
    r = R("X1", {"all": [fact("palace.name", "eq", "Mệnh"), ref("opp", "palace.own_major_stars", "contains", "Thiên Phủ"),
                         fact("palace.own_major_stars", "contains", "Tử Vi")]},
          [{"kind": "finding", "claim": "demo_tu_phu_doi_chieu"}])
    assert validate_pack([r], SRC, F) == []
    res = engine.run([r], SRC, b)
    f = [x for x in res.findings if x.claim == "demo_tu_phu_doi_chieu"]
    assert [x.subject for x in f] == ["palace:Mệnh"]
    chain = " | ".join(res.why(f[0].id)["chain"])
    assert "palace:Thiên Di" in chain and "palace.own_major_stars" in chain          # the fact read from ANOTHER palace is in the why-chain


def test_engine_exception_with_ref_blocks_and_explains():
    b = base_facts([("star", "Tử Vi", "Mệnh"), ("star", "Kình Dương", "Thiên Di")])
    base_cond = {"all": [fact("palace.name", "eq", "Mệnh"), fact("palace.own_major_stars", "contains", "Tử Vi")]}
    exc = [ref("opp", "palace.own_stars", "contains", "Kình Dương")]
    res = engine.run([R("X2", base_cond, [{"kind": "finding", "claim": "c2"}], exc=exc)], SRC, b)
    assert not res.findings and res.blocked and res.blocked[0]["rule"] == "X2"
    res2 = engine.run([R("X2", base_cond, [{"kind": "finding", "claim": "c2"}], exc=exc)], SRC, base_facts([("star", "Tử Vi", "Mệnh")]))
    assert [x.claim for x in res2.findings] == ["c2"] and not res2.blocked


def test_engine_multi_hop_across_palaces_depth_and_order_independence():
    b = base_facts([("star", "Tử Vi", "Mệnh"), ("star", "Tả Phụ", "Thiên Di")])
    r1 = R("H1", {"all": [fact("palace.name", "eq", "Mệnh"), ref("opp", "palace.own_stars", "contains", "Tả Phụ")]},
           [{"kind": "assert", "fact": "derived.menh_duoc_ta", "value": True, "scope": "chart"}])
    r2 = R("H2", {"all": [fact("palace.name", "eq", "Quan Lộc"), fact("derived.menh_duoc_ta")]},
           [{"kind": "assert", "fact": "derived.step2", "value": True}], prio=-1)
    r3 = R("H3", {"all": [fact("palace.name", "eq", "Quan Lộc"), fact("derived.step2")]}, [{"kind": "finding", "claim": "hop3"}], prio=-2)
    a = engine.run([r1, r2, r3], SRC, b)
    c = engine.run([r3, r2, r1], SRC, b)                       # rule order in the list must not matter
    fa, fc = [x for x in a.findings if x.claim == "hop3"], [x for x in c.findings if x.claim == "hop3"]
    assert len(fa) == 1 and fa[0].depth == 3 and (fa[0].subject, fa[0].depth) == (fc[0].subject, fc[0].depth)
    assert [("H1", "palace:Mệnh")] == [(x[0], x[1]) for x in a.fired if x[0] == "H1"]


def test_engine_pending_when_ref_target_fact_never_appears():
    b = base_facts()
    r = R("P1", {"all": [fact("palace.name", "eq", "Mệnh"), ref("opp", "derived.never_asserted")]}, [{"kind": "finding", "claim": "x"}])
    res = engine.run([r], SRC, b)
    assert not res.findings and any(p["rule"] == "P1" and p["subject"] == "palace:Mệnh" for p in res.pending)


def test_conflicts_with_declared_between_different_claims_is_unresolved_when_unverified():
    b = base_facts([("star", "Tử Vi", "Mệnh")])
    cond = {"all": [fact("palace.name", "eq", "Mệnh"), fact("palace.own_major_stars", "contains", "Tử Vi")]}
    ra = R("CA", cond, [{"kind": "finding", "claim": "claim_a", "effect": "support"}], conflicts=["CB"])
    rb = R("CB", cond, [{"kind": "finding", "claim": "claim_b", "effect": "limit"}], conflicts=["CA"])
    assert validate_pack([ra, rb], SRC, F) == []
    res = engine.run([ra, rb], SRC, b)
    rep = [r for r in conflict.resolve(res, [ra, rb]) if r.get("declared")]
    assert len(rep) == 1 and rep[0]["status"] == "unresolved" and {f.status for f in res.findings} == {"unresolved"}


def test_conflicts_with_not_triggered_when_only_one_side_fires():
    b = base_facts([("star", "Tử Vi", "Mệnh")])
    cond = {"all": [fact("palace.name", "eq", "Mệnh"), fact("palace.own_major_stars", "contains", "Tử Vi")]}
    ra = R("CA", cond, [{"kind": "finding", "claim": "claim_a"}], conflicts=["CB"])
    rb = R("CB", {"all": [fact("palace.name", "eq", "Mệnh"), fact("palace.own_major_stars", "contains", "Thiên Phủ")]},
           [{"kind": "finding", "claim": "claim_b", "effect": "limit"}], conflicts=["CA"])
    res = engine.run([ra, rb], SRC, b)
    assert not [r for r in conflict.resolve(res, [ra, rb]) if r.get("declared")]


def test_validate_pack_rejects_conflicts_with_unknown_rule():
    r = R("Z", fact("palace.name", "eq", "Mệnh"), [{"kind": "finding", "claim": "z"}], conflicts=["NOPE"])
    assert any("conflictsWith unknown rule" in e for e in validate_pack([r], SRC, F))
