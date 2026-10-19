"""A fact given as disagreeing alternatives (a CONFLICT star-dignity cell) is read three-valued by the rule evaluator: TRUE when every
reading satisfies the condition, FALSE when none does, else UNKNOWN; no reading is picked. The cases are shared with the TS port
(src/interpret/test/engine.test.ts), and the fact base carries the alternatives for exactly the CONFLICT cells."""
import json
from pathlib import Path

import pytest

from tvbt import dignity, tuvi
from tvbt.calendar_core import BirthInput, normalize
from tvbt.knowledge import dsl
from tvbt.reasoning import facts

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((ROOT / "src" / "interpret" / "test" / "fixtures" / "dsl_alternatives.json").read_text("utf-8"))["cases"]


@pytest.mark.parametrize("case", CASES, ids=[c["why"] for c in CASES])
def test_shared_cases(case):
    world = (lambda n: case["world"].get(n)) if "world" in case else None
    assert dsl.evaluate(case["expr"], case["facts"], world) is case["want"]


@pytest.mark.parametrize("school", ["thuc_hanh", "toan_thu", "khao_luan"])
def test_fact_base_carries_alternatives_for_exactly_the_conflict_cells(school):
    seen = 0
    for i in range(80):
        b = normalize(BirthInput(1950 + i % 60, 1 + i % 12, 1 + (i * 7) % 28, (i * 5) % 24, 15, "Asia/Ho_Chi_Minh", "male" if i % 2 else "female"))
        c = tuvi.compute(b, dignity_school=school)
        base = facts.tuvi_facts(c)
        for p in c.palaces:
            f = base[f"palace:{p['name']}"]
            for s in p["stars"]:
                r = dignity.classify(s, p["branch"], school)
                alt = f.get(f"{dsl.ALT}palace.dignity.{s}")
                if r["status"] == "CONFLICT":
                    seen += 1
                    assert alt == [a["value"] for a in r["alternatives"]]
                    assert f.get(f"palace.dignity.{s}", "unspecified") == "unspecified"     # never a picked reading
                else:
                    assert alt is None
    if school != "thuc_hanh":
        assert seen, "the sample should meet some CONFLICT cell"
