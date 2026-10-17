"""Sensitivity of the 17 school variants to the Tứ Hóa table (Canh and Nhâm are the only stems on which the sources disagree).
Pure oracle (no production code). Every lunar day x month x 12 hours x 2 genders of two Canh years and two Nhâm years.
Writes engine/tests/fixtures/tu_hoa_sensitivity.json. It does NOT choose a table."""
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine/tests"))
import oracle_tuvi_independent as O  # noqa: E402

SPEC = O.V()
YEARS = {"Canh": [2010, 2020], "Nhâm": [2012, 2022]}
res = {}
for stem, years in YEARS.items():
    for table in ("TH", "TT_WS"):
        diff, fire, n = collections.Counter(), collections.Counter(), 0
        for ly in years:
            for lm in range(1, 13):
                for ld in range(1, 30):
                    for hb in range(12):
                        for male in (True, False):
                            a, b = O.chart(ly, lm, ld, hb, male, "KL"), O.chart(ly, lm, ld, hb, male, table)
                            n += 1
                            for vid, sp in SPEC.items():
                                sa, sb = O.state(sp, a), O.state(sp, b)
                                if sa != "khong_hien" or sb != "khong_hien":
                                    fire[vid] += 1
                                if sa != sb:
                                    diff[vid] += 1
        res[f"{stem}|{table}"] = {"charts": n, "differ": {k.replace("CACH_X_", ""): v for k, v in sorted(diff.items())}, "either_fires": {k.replace("CACH_X_", ""): v for k, v in sorted(fire.items())}}
(ROOT / "engine/tests/fixtures/tu_hoa_sensitivity.json").write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
for k, v in res.items():
    print(k, v["charts"], {a: b for a, b in v["differ"].items()})
