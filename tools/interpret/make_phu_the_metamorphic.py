"""Metamorphic fixture for the domain ledger (plan quirky-tinkering-rabin step 5, S1): the owner's regression chart (09/01/2002 04:30, nam,
Khảo Luận dignity) with the limiting elements of Phu Thê — Hóa Kỵ on Văn Xương, Đà La, Tuần — removed one at a time and all together, and a
chart with all three removed then each added back. Every variant is rebuilt through /api/facts (tvbt.api.chart_facts with the computed chart
swapped in, as make_benchmark.py does), so every derived fact stays consistent. Variants are not astronomically possible charts; they test the
interpretation, not the calendar.
    .venv/bin/python tools/interpret/make_phu_the_metamorphic.py   →   src/interpret/test/fixtures/phu_the_metamorphic.json"""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engine"))
sys.path.insert(0, str(ROOT / "tools" / "interpret"))
import tvbt.api as api  # noqa: E402
from tvbt.api import BirthReq  # noqa: E402
from make_benchmark import remove_star  # noqa: E402

BIRTH = {"year": 2002, "month": 1, "day": 9, "hour": 4, "minute": 30, "gender": "male", "to_year": 2026, "dignity_school": "khao_luan"}
PT = "Phu Thê"


def facts_of(tv):
    req = BirthReq(**BIRTH)
    orig = api._compute
    nb, bz, _ = orig(req)
    api._compute = lambda r: (nb, bz, tv)
    try:
        return api.chart_facts(req)
    finally:
        api._compute = orig


def pal(t):
    return next(p for p in t.palaces if p["name"] == PT)


def no_ky(t):
    t.tu_hoa.pop("Hóa Kỵ", None)


def no_da(t):
    remove_star(t, PT, "Đà La")


def no_tuan(t):
    pal(t)["tuan"] = False


def add_ky(t):
    t.tu_hoa["Hóa Kỵ"] = {"star": "Văn Xương", "branch": pal(t)["branch_index"]}


def add_da(t):
    p = pal(t)
    p["stars"] = p["stars"] + ["Đà La"]


def add_tuan(t):
    pal(t)["tuan"] = True


def main():
    _, _, tv = api._compute(BirthReq(**BIRTH))
    out = []

    def var(name, element, change, *fns, start=None):
        t = copy.deepcopy(start or tv)
        for f in fns:
            f(t)
        out.append({"name": name, "element": element, "change": change, "facts": facts_of(t)})
        return t

    var("base", None, None)
    var("remove_ky", "Hóa Kỵ", "remove", no_ky)
    var("remove_da", "Đà La", "remove", no_da)
    var("remove_tuan", "Tuần", "remove", no_tuan)
    clean = var("clean", None, "remove_all", no_ky, no_da, no_tuan)
    var("add_ky", "Hóa Kỵ", "add", add_ky, start=clean)
    var("add_da", "Đà La", "add", add_da, start=clean)
    var("add_tuan", "Tuần", "add", add_tuan, start=clean)
    dst = ROOT / "src" / "interpret" / "test" / "fixtures" / "phu_the_metamorphic.json"
    dst.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), "utf-8")
    print(dst, len(out))


if __name__ == "__main__":
    main()
