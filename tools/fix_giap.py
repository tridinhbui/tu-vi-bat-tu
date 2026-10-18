"""Rewrites unordered 'giáp' (flanking) pairs in every rule pack so that the two stars must sit on OPPOSITE sides of the palace.
    .venv/bin/python tools/fix_giap.py          (idempotent; run after regenerating any pack)
A pair  {fact: palace.rel.flank_stars | palace.neighbor_stars, contains A} + {same fact, contains B}  inside one `all` is true when A and
B are both in ONE neighbouring palace, which the books never call giáp. It becomes
    any[ all[flank_prev contains A, flank_next contains B], all[flank_prev contains B, flank_next contains A] ].
test_rule_integrity.py fails if an unordered pair reappears."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLANK = {"palace.rel.flank_stars": "stars", "palace.neighbor_stars": "stars", "palace.rel.flank_majors": "majors", "palace.neighbor_majors": "majors"}


def leaf(e):
    return isinstance(e, dict) and e.get("fact") in FLANK and e.get("operator") == "contains" and isinstance(e.get("value"), str)


def ordered(kind, a, b):
    p, n = f"palace.rel.flank_prev_{kind}", f"palace.rel.flank_next_{kind}"
    has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
    return {"any": [{"all": [has(p, a), has(n, b)]}, {"all": [has(p, b), has(n, a)]}]}


def fix(e):
    """Returns (expr, number of pairs rewritten)."""
    if not isinstance(e, dict):
        return e, 0
    n = 0
    for key in ("all", "any", "count"):
        if isinstance(e.get(key), list):
            items = []
            for x in e[key]:
                y, m = fix(x)
                items.append(y)
                n += m
            if key == "all":
                flank = [i for i, x in enumerate(items) if leaf(x)]
                while len(flank) >= 2:
                    i, j = flank[0], flank[1]
                    a, b = items[i], items[j]
                    items[i] = ordered(FLANK[a["fact"]] if FLANK[a["fact"]] == FLANK[b["fact"]] else "stars", a["value"], b["value"])
                    items.pop(j)
                    n += 1
                    flank = [k for k, x in enumerate(items) if leaf(x)]
            e = {**e, key: items}
    if isinstance(e.get("not"), dict):
        y, m = fix(e["not"])
        e = {**e, "not": y}
        n += m
    return e, n


def unordered_pairs(e):
    if not isinstance(e, dict):
        return 0
    n = sum(unordered_pairs(x) for k in ("all", "any", "count") for x in (e.get(k) or []))
    if isinstance(e.get("all"), list) and sum(1 for x in e["all"] if leaf(x)) >= 2:
        n += 1
    return n + unordered_pairs(e.get("not"))


def packs():
    loader = (ROOT / "engine" / "tvbt" / "knowledge" / "loader.py").read_text("utf-8")
    return json.loads(re.search(r"^PACKS = (\[.*\])$", loader, re.M).group(1).replace("'", '"'))


def main():
    total = 0
    for name in packs():
        path = ROOT / "engine" / "data" / name
        raw = path.read_text("utf-8")
        d = json.loads(raw)
        changed = 0
        for r in d.get("rules", []):
            r["conditions"], m = fix(r["conditions"])
            changed += m
        if changed:
            indent = 1 if raw.startswith('{\n "') else 2
            path.write_text(json.dumps(d, ensure_ascii=False, indent=indent) + ("\n" if raw.endswith("\n") else ""), "utf-8")
            print(f"{name}: {changed} pair(s) rewritten")
        total += changed
    print("total", total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
