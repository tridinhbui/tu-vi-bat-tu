"""Phase 6 full scan (same 116,928 charts as scan_variant_reach.py). For every chart:
  - compare the INDEPENDENT oracle (engine/tests/oracle_tuvi_independent.py, no tvbt import) with production: Mệnh/Thân/cục, every star position,
    Tứ Hóa carriers, Tuần/Triệt, and the state of every school variant;
  - collect sensitivity statistics for the 17 variants and for the 10 baseline formations (activation, breakage, pairwise disagreement).
Writes engine/tests/fixtures/formation_oracle_full.json and formation_variant_stats.json. Mismatches are REPORTED, never patched away."""
import collections
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine")); sys.path.insert(0, str(ROOT / "engine/tests"))
import oracle_tuvi_independent as O  # noqa: E402
from tvbt import calendar_core as cc, lunar_input, tuvi  # noqa: E402
from tvbt.formation_explain import analyse  # noqa: E402
from tvbt.knowledge.formation import load_formations  # noqa: E402
from tvbt.knowledge.loader import load_experimental  # noqa: E402

VARS = load_formations(ROOT / "engine/data/experimental/formations_school_variants.json")
BASE = load_experimental()[1]
SPEC = O.V()
YEARS = list(range(2014, 2024)) + [1978, 1988, 1998, 2008]
bad, ex = collections.Counter(), {}
n = 0
st = collections.defaultdict(collections.Counter)          # id -> state counts (production)
pair = collections.Counter()                               # (variantA, variantB) -> both fire & states differ
both = collections.Counter()                               # (variantA, variantB) -> both fire
vs_base = collections.defaultdict(collections.Counter)     # variant -> {'both_fire','differ'} vs its baseline formation
fam = collections.defaultdict(list)
for f in VARS:
    fam[f.id.split("@")[0]].append(f.id)
for ly in YEARS:
    for lm in range(1, 13):
        for ld in range(1, 30):
            try:
                sol = lunar_input.lunar_to_solar(ld, lm, ly, False, "vn")[0]
            except Exception:
                continue
            for hb in range(12):
                for male in (True, False):
                    tv = tuvi.compute(cc.normalize(cc.BirthInput(sol.year, sol.month, sol.day, 2 * hb, 0, "Asia/Ho_Chi_Minh", "male" if male else "female")))
                    c = O.chart(ly, lm, ld, hb, male)
                    n += 1
                    key = (ly, lm, ld, hb, male)
                    if (tv.menh_branch, tv.than_branch, tv.cuc["n"]) != (c["menh"], c["than"], c["cuc"]):
                        bad["menh_than_cuc"] += 1; ex.setdefault("menh_than_cuc", key)
                    prod = {s.name: s.branch for s in tv.stars}
                    for s, p in c["pos"].items():
                        if prod.get(s) != p:
                            bad["pos:" + s] += 1; ex.setdefault("pos:" + s, key)
                    for tag, v in tv.tu_hoa.items():
                        if v["branch"] != c["pos"][c["carriers"][tag]]:
                            bad["hoa:" + tag] += 1; ex.setdefault("hoa:" + tag, key)
                    if {p["branch_index"] for p in tv.palaces if p["tuan"]} != c["tuan"]:
                        bad["tuan"] += 1; ex.setdefault("tuan", key)
                    if {p["branch_index"] for p in tv.palaces if p["triet"]} != c["triet"]:
                        bad["triet"] += 1; ex.setdefault("triet", key)
                    got = {x["id"]: x["state"] for x in analyse(tv, VARS)}
                    base = {x["id"]: x["state"] for x in analyse(tv, BASE)}
                    for vid, s in got.items():
                        st[vid][s] += 1
                        if O.state(SPEC[vid], c) != s:
                            bad["state:" + vid] += 1; ex.setdefault("state:" + vid, key)
                    for bid, s in base.items():
                        st[bid][s] += 1
                    for b, ids in fam.items():
                        for a, z in itertools.combinations(ids, 2):
                            if got[a] != "khong_hien" and got[z] != "khong_hien":
                                both[(a, z)] += 1
                                pair[(a, z)] += got[a] != got[z]
                        for a in ids:
                            if got[a] != "khong_hien" and base[b] != "khong_hien":
                                vs_base[a]["both_fire"] += 1
                                vs_base[a]["differ"] += got[a] != base[b]
                            vs_base[a]["variant_only"] += got[a] != "khong_hien" and base[b] == "khong_hien"
                            vs_base[a]["baseline_only"] += got[a] == "khong_hien" and base[b] != "khong_hien"
(ROOT / "engine/tests/fixtures/formation_oracle_full.json").write_text(json.dumps(
    {"charts": n, "years": YEARS, "mismatches": dict(bad), "first_examples": {k: list(v) for k, v in ex.items()}}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
(ROOT / "engine/tests/fixtures/formation_variant_stats.json").write_text(json.dumps(
    {"charts": n, "states": {k: dict(v) for k, v in sorted(st.items())},
     "pairs": {f"{a}|{z}": {"both_fire": both[(a, z)], "differ": pair[(a, z)]} for (a, z) in sorted(both)},
     "vs_baseline": {k: dict(v) for k, v in sorted(vs_base.items())}}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(n, dict(bad))
