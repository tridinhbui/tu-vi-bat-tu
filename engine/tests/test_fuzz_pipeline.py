import random

from tvbt import analysis, bazi, temporal, tuvi
from tvbt.calendar_core import BirthInput, normalize
from tvbt.knowledge.loader import load_all
from tvbt.nlg import generate as nlg
from tvbt.reasoning import engine, facts


def test_full_pipeline_never_crashes_and_is_deterministic():
    rules, srcs = load_all()
    rnd = random.Random(7)
    for _ in range(60):
        y, m, d, h = rnd.randint(1900, 2049), rnd.randint(1, 12), rnd.randint(1, 28), rnd.randint(0, 23)
        nb = normalize(BirthInput(y, m, d, h, rnd.choice([0, 30]), "Asia/Ho_Chi_Minh", rnd.choice(["male", "female"]),
                                  calendar=rnd.choice(["vn", "cn", "vn_south"]), zi_rule=rnd.choice(["early_zi_next_day", "late_zi_same_day"])))
        bz, tv = bazi.compute(nb), tuvi.compute(nb)
        a1, a2 = analysis.analyse(tv, bz), analysis.analyse(tv, bz)
        assert a1 == a2
        temporal.tuvi_year(tv, y + 30); temporal.bazi_year(bz, y, y + 30)
        r1 = engine.run(rules, srcs, facts.tuvi_facts(tv), system="tu_vi")
        r2 = engine.run(rules, srcs, facts.tuvi_facts(tv), system="tu_vi")
        assert [(f.id, f.status) for f in r1.findings] == [(f.id, f.status) for f in r2.findings]
        nlg.realize(nlg.build_interpretations(r1, rules, srcs), 5)
