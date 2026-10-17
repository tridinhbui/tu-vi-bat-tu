"""Reach scan for the school variants: every lunar day x 12 hour branches x 2 genders over ten consecutive years (all ten year stems) plus extra
Mậu years (Kình Dương at Ngọ needs a Mậu year). Writes engine/tests/fixtures/formation_variants_reach.json: per variant, the states that occur
(with counts). A variant/state that never occurs is REPORTED, never 'fixed'."""
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
from tvbt import calendar_core as cc, lunar_input, tuvi  # noqa: E402
from tvbt.formation_explain import analyse  # noqa: E402
from tvbt.knowledge.formation import load_formations  # noqa: E402

V = load_formations(ROOT / "engine/data/experimental/formations_school_variants.json")
YEARS = list(range(2014, 2024)) + [1978, 1988, 1998, 2008]
c = collections.defaultdict(collections.Counter)
n = 0
for y in YEARS:
    for m in range(1, 13):
        for d in range(1, 30):
            try:
                sol = lunar_input.lunar_to_solar(d, m, y, False, "vn")[0]
            except Exception:
                continue
            for hb in range(12):
                for g in ("male", "female"):
                    tv = tuvi.compute(cc.normalize(cc.BirthInput(sol.year, sol.month, sol.day, 2 * hb, 0, "Asia/Ho_Chi_Minh", g)))
                    n += 1
                    for x in analyse(tv, V):
                        c[x["id"]][x["state"]] += 1
out = {"charts": n, "years": YEARS, "variants": {k: dict(v) for k, v in sorted(c.items())}}
(ROOT / "engine/tests/fixtures/formation_variants_reach.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(n, "charts")
for k, v in sorted(c.items()):
    print(k.split("CACH_X_")[1], {s: q for s, q in v.items() if s != "khong_hien"})
