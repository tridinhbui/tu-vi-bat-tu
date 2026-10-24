"""Recompute the vận readings (`facts.decades[].readings`, van_han.read_traced) of corpus1000 after rules are added to
engine/data/van_han_rules.json, keeping every other stored fact as it is (make_corpus.py would also pick up unrelated engine changes).
Fails if a reading of a rule that already existed changes: only the new rules may add sentences.
    .venv/bin/python tools/interpret/refresh_van_readings.py NEW_RULE_ID [NEW_RULE_ID ...]"""
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engine"))
from tvbt import van_han  # noqa: E402
from tvbt.api import BirthReq, _compute  # noqa: E402

CORPUS = ROOT / "src" / "interpret" / "test" / "fixtures" / "corpus1000.json.gz"


def main(new: set[str]) -> int:
    corpus = json.loads(gzip.open(CORPUS).read())
    fired: Counter = Counter()
    for ch in corpus:
        _, _, tv = _compute(BirthReq(**ch["birth"]))
        for d in ch["facts"]["decades"]:
            rd = van_han.read_traced(tv, d["palace"])
            old = [r for r in rd if r["rule_id"] not in new]
            if old != d["readings"]:
                print("an existing reading changed:", ch["birth"], d["palace"], d["readings"], old)
                return 1
            fired.update(r["rule_id"] for r in rd if r["rule_id"] in new)
            d["readings"] = rd
    CORPUS.write_bytes(gzip.compress(json.dumps(corpus, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), mtime=0))
    for k in sorted(new):
        print(f"{k}: {fired[k]} decade palaces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(set(sys.argv[1:])))
