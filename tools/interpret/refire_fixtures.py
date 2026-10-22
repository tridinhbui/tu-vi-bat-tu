"""Recompute the Python engine's Tử Vi firings (`python_fired`) of the stored TS test fixtures after a rule-pack change (a review status, a
condition tightened to its page), keeping every stored fact as it is. Regenerating the fixtures from scratch (make_fixtures.py, make_corpus.py,
make_conflict_fixtures.py) would also pick up unrelated engine changes; this only re-runs the rules.
    .venv/bin/python tools/interpret/refire_fixtures.py"""
import gzip
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engine"))
from tvbt.knowledge.loader import load_all  # noqa: E402
from tvbt.reasoning import engine  # noqa: E402

FX = ROOT / "src" / "interpret" / "test" / "fixtures"
rules, sources = load_all()


def fired(base):
    res = engine.run(rules, sources, base, system="tu_vi")
    return [list(x) for x in sorted({(x.rule_id, x.subject, x.claim, x.effect, x.basis) for x in res.findings})]


def refire(items):
    n = 0
    for c in items:
        new = fired(c["facts"]["base"])
        n += new != c["python_fired"]
        c["python_fired"] = new
    return n


for name in ("charts.json", "conflicts.json"):
    p = FX / name
    items = json.loads(p.read_text("utf-8"))
    print(name, refire(items), "changed")
    p.write_text(json.dumps(items, ensure_ascii=False, separators=(",", ":")), "utf-8")
p = FX / "menh_cu_tuat.json"
one = json.loads(p.read_text("utf-8"))
print(p.name, refire([one]), "changed")
p.write_text(json.dumps(one, ensure_ascii=False, separators=(",", ":")) if "\n" not in p.read_text("utf-8").strip() else json.dumps(one, ensure_ascii=False, indent=1), "utf-8")
p = FX / "corpus1000.json.gz"
items = json.loads(gzip.decompress(p.read_bytes()).decode("utf-8"))
print(p.name, refire(items), "changed")
p.write_bytes(gzip.compress(json.dumps(items, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), mtime=0))
