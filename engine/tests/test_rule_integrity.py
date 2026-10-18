"""Rule-activation integrity over every loaded pack (found in the deterministic-pipeline audit of 17/05/1990 and the 40-chart sweep).
1. 'giáp' pairs must require the two stars on opposite sides of the palace (tools/fix_giap.py rewrites them; a regenerated pack that
   brings back an unordered pair fails here).
2. A verified rule whose reading carries a brightness condition must test it: 'miếu địa: …', 'nhập miếu', 'đắc địa thì …', 'khi X hãm'
   written into the phrase with no palace.dignity / palace.branch leaf means the rule fires on charts the book excludes."""
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from fix_giap import packs, unordered_pairs  # noqa: E402

from tvbt.knowledge import dsl  # noqa: E402,F401  (import check: the loader's DSL is the one under test elsewhere)

RULES = [(p, r) for p in packs() for r in json.loads((ROOT / "engine" / "data" / p).read_text("utf-8"))["rules"]]
DIGNITY_CLAUSE = re.compile(r"(^|: |\()(miếu địa|nhập miếu|đắc địa thì|miếu vượng thì)|khi \S+ \S+ hãm")


@pytest.mark.parametrize("pack,rule", [(p, r) for p, r in RULES if unordered_pairs(r["conditions"])], ids=lambda x: x if isinstance(x, str) else x["id"])
def test_no_unordered_giap_pair(pack, rule):
    pytest.fail(f"{rule['id']} in {pack}: two flank 'contains' leaves in one all — run tools/fix_giap.py")


def test_giap_rewrite_is_ordered():
    from fix_giap import fix
    e, n = fix({"all": [{"fact": "palace.name", "value": "Mệnh"}, {"fact": "palace.rel.flank_stars", "operator": "contains", "value": "Thái Dương"},
                        {"fact": "palace.rel.flank_stars", "operator": "contains", "value": "Thái Âm"}]})
    assert n == 1 and unordered_pairs(e) == 0
    assert e["all"][1]["any"][0]["all"][0]["fact"] == "palace.rel.flank_prev_stars"


def test_verified_rules_test_the_dignity_their_reading_names():
    bad = []
    for p, r in RULES:
        if r.get("system") != "tu_vi" or r.get("reviewStatus") != "verified":
            continue
        desc = r.get("description", "")
        phrase = desc.split("(paraphrased)", 1)[-1]
        if DIGNITY_CLAUSE.search(phrase) and not re.search(r"palace\.(dignity|branch)", json.dumps(r["conditions"], ensure_ascii=False)):
            bad.append(f"{r['id']} ({p}): {phrase.strip()[:90]}")
    assert not bad, "\n".join(bad)
