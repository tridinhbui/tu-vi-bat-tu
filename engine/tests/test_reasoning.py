"""Engine-mechanics tests use SYNTHETIC fixture rules (clearly not doctrine) — separate from the knowledge pack."""
from tvbt import bazi, tuvi
from tvbt.calendar_core import BirthInput, normalize
from tvbt.knowledge.schema import KnowledgeRule, Source, validate_pack
from tvbt.reasoning import conflict, engine, facts

SRC = [Source("S_FIX", "synthetic fixture", None, None, False), Source("S_OK", "synthetic verified", "x", "p.1", True)]
F = {"palace.*", "chart.*", "bazi.*", "derived.*"}


def R(id, cond, cons, subject="palace", status="draft", src=("S_FIX",), exc=None, prio=0):
    return KnowledgeRule(id, "tu_vi", "fix", "fixture", id, cond, cons, exceptions=exc or [], priority=prio,
                         sourceIds=list(src), reviewStatus=status, subject=subject)


def base():
    c = tuvi.compute(normalize(BirthInput(1990, 5, 17, 10, 30, "Asia/Ho_Chi_Minh", "male")))
    return facts.tuvi_facts(c)


def test_multi_hop_and_provenance():
    rules = [
        R("H1", {"fact": "palace.own_major_stars", "operator": "contains", "value": "Tử Vi"},
          [{"kind": "assert", "fact": "derived.has_tu_vi", "value": True}]),
        R("H2", {"all": [{"fact": "derived.has_tu_vi", "value": True}, {"fact": "palace.is_than", "value": False}]},
          [{"kind": "assert", "fact": "derived.step2", "value": True}], prio=-1),
        R("H3", {"fact": "derived.step2", "value": True}, [{"kind": "finding", "claim": "demo_claim"}], prio=-2),
    ]
    assert validate_pack(rules, SRC, F) == []
    res = engine.run(rules, SRC, base())
    f = [x for x in res.findings if x.claim == "demo_claim"]
    assert len(f) == 1 and f[0].depth == 1 + 0 or f[0].depth >= 1
    chain = res.why(f[0].id)["chain"]
    assert any("H1" in c for c in chain) and any("S_FIX (unverified)" in c for c in chain)
    assert f[0].subject == "palace:Quan Lộc"  # Tử Vi sits in Quan Lộc for this chart (see test_tuvi)


def test_deterministic_and_no_refire():
    rules = [R("A", {"fact": "palace.has_no_major", "value": True}, [{"kind": "finding", "claim": "c"}])]
    a, b = engine.run(rules, SRC, base()), engine.run(rules, SRC, base())
    assert a.fired == b.fired and len(a.fired) == len(set((r, s) for r, s, _ in a.fired))


def test_exception_suppresses_and_is_recorded():
    rules = [R("E", {"fact": "palace.has_no_major", "value": True}, [{"kind": "finding", "claim": "c"}],
               exc=[{"fact": "palace.triet", "value": False}])]
    res = engine.run(rules, SRC, base())
    triet_palaces = {f.subject for f in res.findings}
    blocked_palaces = {b['subject'] for b in res.blocked}
    assert res.blocked and res.findings and not (triet_palaces & blocked_palaces)


def test_missing_fact_is_pending_not_false():
    rules = [R("P", {"fact": "palace.nonexistent", "value": 1}, [{"kind": "finding", "claim": "c"}])]
    res = engine.run(rules, SRC, base())
    assert not res.findings and res.pending and res.pending[0]["missing_facts"] == ["palace.nonexistent"]


def test_contradictory_derived_fact_is_conflict_not_overwrite():
    rules = [R("X1", {"fact": "palace.name", "value": "Mệnh"}, [{"kind": "assert", "fact": "derived.k", "value": 1}]),
             R("X2", {"fact": "palace.name", "value": "Mệnh"}, [{"kind": "assert", "fact": "derived.k", "value": 2}], prio=-1)]
    res = engine.run(rules, SRC, base())
    assert res.conflicts and res.derived["palace:Mệnh"]["derived.k"] == 1


def test_conflict_unresolved_when_unverified_and_resolved_when_verified_specific():
    gen = R("G", {"fact": "palace.name", "value": "Mệnh"}, [{"kind": "finding", "claim": "t", "effect": "support"}])
    spec_draft = R("S", {"all": [{"fact": "palace.name", "value": "Mệnh"}, {"fact": "palace.is_than", "value": False}]},
                   [{"kind": "finding", "claim": "t", "effect": "limit"}])
    res = engine.run([gen, spec_draft], SRC, base())
    rep = conflict.resolve(res, [gen, spec_draft])
    assert rep[0]["status"] == "unresolved" and "both readings" in rep[0]["resolution"]
    spec_ok = R("S", spec_draft.conditions, spec_draft.consequences, status="verified", src=("S_OK",))
    res2 = engine.run([gen, spec_ok], SRC, base())
    rep2 = conflict.resolve(res2, [gen, spec_ok])
    assert rep2[0]["status"] == "limited" and "verified" in rep2[0]["resolution"]


def test_bazi_facts_structural_only():
    c = bazi.compute(normalize(BirthInput(2000, 1, 1, 12, 0, "Asia/Ho_Chi_Minh", "male")))
    f = facts.bazi_facts(c)["chart"]
    assert f["bazi.dm_element"] == "Thổ" and f["bazi.dm_has_root"] is True
