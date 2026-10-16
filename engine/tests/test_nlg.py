from tvbt import tuvi
from tvbt.calendar_core import BirthInput, normalize
from tvbt.knowledge.schema import KnowledgeRule, Source
from tvbt.nlg import generate as g, lexicon as lx
from tvbt.reasoning import engine, facts

SRC = [Source("S_FIX", "synthetic fixture", None, None, False)]


def R(id, cond, cons):
    return KnowledgeRule(id, "tu_vi", "fix", "fixture", id, cond, cons, sourceIds=["S_FIX"], subject="palace")


def setup():
    c = tuvi.compute(normalize(BirthInput(1990, 5, 17, 10, 30, "Asia/Ho_Chi_Minh", "male")))
    rules = [R("N1", {"fact": "palace.name", "value": "Mệnh"}, [{"kind": "finding", "claim": "demo_theme", "effect": "support"}]),
             R("N2", {"all": [{"fact": "palace.name", "value": "Mệnh"}, {"fact": "palace.is_than", "value": False}]},
               [{"kind": "finding", "claim": "demo_theme", "effect": "limit"}]),
             R("N3", {"fact": "palace.name", "value": "Quan Lộc"}, [{"kind": "finding", "claim": "unknown_claim"}])]
    res = engine.run(rules, SRC, facts.tuvi_facts(c))
    lx.CLAIMS["demo_theme"] = {"label": "chủ đề minh họa (fixture)", "gloss": ""}
    return g.build_interpretations(res, rules, SRC)


def test_every_content_sentence_has_provenance_and_is_deterministic():
    it = setup()
    for lv in range(1, 6):
        a, b = g.realize(it, lv), g.realize(it, lv)
        assert g.render(a) == g.render(b)
        assert all(s.provenance for s in a if s.kind == "content")
        assert a[-1].text == lx.DISCLAIMER


def test_depth_adds_layers_not_filler():
    it = setup()
    sizes = [len(g.realize(it, lv)) for lv in range(1, 6)]
    assert sizes == sorted(sizes) and sizes[0] < sizes[2] < sizes[3] < sizes[4]
    l3 = g.render(g.realize(it, 3))
    assert "N1" in l3 and "N2" in l3 and "chưa thể kết luận" in l3.lower()
    assert "nguồn S_FIX" in g.render(g.realize(it, 4)) and "chưa xác minh" in g.render(g.realize(it, 4))
    assert "Sinh khắc" in g.render(g.realize(it, 5)) and "Sinh khắc" not in g.render(g.realize(it, 4))


def test_unknown_claim_not_invented():
    t = g.render(g.realize(setup(), 1))
    assert "chưa có mô tả tiếng Việt" in t


def test_no_claim_outside_graph():
    it = setup()
    claims = {i.claim for i in it}
    t = g.render(g.realize(it, 4))
    assert claims == {"demo_theme", "unknown_claim"} and "Thất Sát" not in t
