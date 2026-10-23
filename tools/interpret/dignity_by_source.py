"""Per-source brightness (owner review 2026-10-22, DEEP-TUVI §Correctness item 8): a rule taken from Thực Hành, Toàn Thư or Khảo Luận tests a star's
brightness in ITS OWN book's table, not in the table the chart was drawn with. This rewrites every Tử Vi rule's leaf on palace.dignity.<star>
into palace.dignity@<school>.<star> (evaluated by both engines' DSL: engine/tvbt/knowledge/dsl.py _own_book_dignity, src/interpret/dsl.ts
ownBookDignity), for rules whose only source is one of the three books. A cell the book leaves empty falls back to the chart's table at
evaluation time. Rules of other sources (Thiên Lương, Nghiệm Lý: no table of their own) are left on the chart's table.
    .venv/bin/python tools/interpret/dignity_by_source.py            (rewrite packs in place; idempotent)
    .venv/bin/python tools/interpret/dignity_by_source.py --count    (how many corpus firings change against the chart's-table evaluation)"""
import gzip
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engine"))
from tvbt.knowledge.loader import PACKS  # noqa: E402

D = ROOT / "engine" / "data"
SCHOOL = {"SRC_THUC_HANH": "thuc_hanh", "SRC_TOAN_THU": "toan_thu", "SRC_KHAO_LUAN": "khao_luan"}


def rewrite(c, school):
    n = 0
    if isinstance(c, dict):
        for key in ("fact",):
            if isinstance(c.get(key), str) and c[key].startswith("palace.dignity."):
                c[key] = f"palace.dignity@{school}.{c[key][len('palace.dignity.'):]}"; n += 1
        if isinstance(c.get("ref"), dict) and str(c["ref"].get("fact", "")).startswith("palace.dignity."):
            c["ref"]["fact"] = f"palace.dignity@{school}.{c['ref']['fact'][len('palace.dignity.'):]}"; n += 1
        for k in ("all", "any", "count"):
            for x in c.get(k, []) if isinstance(c.get(k), list) else []:
                n += rewrite(x, school)
        if isinstance(c.get("not"), dict):
            n += rewrite(c["not"], school)
    return n


def main():
    rules = 0
    for pack in PACKS:
        path = D / pack
        data = json.loads(path.read_text("utf-8"))
        dirty = False
        for r in data["rules"]:
            src = r.get("sourceIds", [])
            if r.get("system") != "tu_vi" or len(src) != 1 or src[0] not in SCHOOL:
                continue
            if rewrite(r["conditions"], SCHOOL[src[0]]):
                rules += 1; dirty = True
        if dirty:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=1), "utf-8")
    print(f"{rules} rules rewritten")


def count():
    """Firings on the corpus with each rule on its own book's table vs on the chart's table (the stored facts, drawn with Khảo Luận)."""
    from tvbt.knowledge.loader import load_all
    from tvbt.knowledge import dsl
    from tvbt.reasoning import engine
    rules, sources = load_all()
    corpus = json.loads(gzip.decompress((ROOT / "src/interpret/test/fixtures/corpus1000.json.gz").read_bytes()))
    own = lambda b: {(f.rule_id, f.subject) for f in engine.run(rules, sources, b, system="tu_vi").findings}
    orig = dsl._own_book_dignity
    diff, total = [], 0
    for c in corpus:
        a = own(c["facts"]["base"])
        dsl._own_book_dignity = lambda facts, name: (f"palace.dignity.{name.split('.', 1)[1].split('.', 1)[1]}", None)
        b = own(c["facts"]["base"])
        dsl._own_book_dignity = orig
        total += len(a)
        diff.append(len(a ^ b))
    print(f"corpus {len(corpus)} charts: {sum(diff)} firings differ ({sum(1 for d in diff if d)} charts), of {total} firings on own-book tables")


if __name__ == "__main__":
    count() if "--count" in sys.argv else main()
