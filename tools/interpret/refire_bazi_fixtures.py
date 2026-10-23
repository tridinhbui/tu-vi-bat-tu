"""Recompute the Python engine's Bát Tự firings (`python_fired_bazi`) of the stored TS test fixtures after a Bát Tự rule-pack change, keeping every
stored fact as it is (the Bát Tự twin of refire_fixtures.py; DEEP-BAZI-2 moved the 八字真宗 wealth / occupation rules out of pack_bazi_zz_direct).
    .venv/bin/python tools/interpret/refire_bazi_fixtures.py"""
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
    res = engine.run(rules, sources, base, system="bat_tu")
    return [list(x) for x in sorted({(x.rule_id, x.subject, x.claim, x.effect, x.basis) for x in res.findings})]


def refire(items):
    n = 0
    for c in items:
        if "python_fired_bazi" not in c:
            continue
        new = fired(c["facts"]["bazi"]["base"])
        n += new != c["python_fired_bazi"]
        c["python_fired_bazi"] = new
    return n


p = FX / "charts.json"
items = json.loads(p.read_text("utf-8"))
print(p.name, refire(items), "changed")
p.write_text(json.dumps(items, ensure_ascii=False, separators=(",", ":")), "utf-8")
p = FX / "corpus1000.json.gz"
items = json.loads(gzip.decompress(p.read_bytes()).decode("utf-8"))
print(p.name, refire(items), "changed")
p.write_bytes(gzip.compress(json.dumps(items, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), mtime=0))
