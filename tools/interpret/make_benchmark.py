"""Reasoner benchmark (plan quirky-tinkering-rabin R0): 20 labelled Mệnh configurations + one-factor counterfactuals of each.
    .venv/bin/python tools/interpret/make_benchmark.py
Writes src/interpret/test/fixtures/benchmark20.json (one chart per configuration, the worked example first) and
src/interpret/test/fixtures/counterfactual100.json.gz (about five variants per benchmark chart).

A counterfactual changes ONE element of the computed chart (a sát tinh in Mệnh, the dignity of the Mệnh chính tinh, a Hóa on Mệnh, Tuần at Mệnh,
or a control star) and rebuilds the fact base through the same /api/facts code path (tvbt.api.chart_facts with the computed chart swapped in),
so every derived fact (tam phương lists, typed positions, counts) stays consistent with the change. Some variants are not astronomically
possible charts (a Kình Dương without its Lộc Tồn); they test the interpretation, not the calendar, and say so in `synthetic`.

Every variant carries `expect`:
  critical  the element is one the Mệnh reading must react to: the voiced content should change, and the change should touch the element;
  inert     a control: a star no Tử Vi rule condition mentions, removed from Mệnh, or a minor star removed from Tật Ách. The Mệnh reading
            should stay the same."""
import copy
import gzip
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engine"))

import tvbt.api as api  # noqa: E402
from tvbt.api import BirthReq  # noqa: E402

SAT = ["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"]
CAT = ["Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"]
OK = {"miếu", "vượng", "đắc"}
REF = {"year": 1991, "month": 3, "day": 2, "hour": 8, "minute": 30, "gender": "male", "to_year": 2026}

# star names that appear anywhere in a Tử Vi rule's conditions or exceptions: removing any other star cannot change which rules fire
_RULE_TEXT = " ".join(json.dumps([r.get("conditions"), r.get("exceptions")], ensure_ascii=False)
                      for f in sorted((ROOT / "engine" / "data").glob("pack_*.json")) if "bazi" not in f.name
                      for r in json.loads(f.read_text())["rules"])


def mentioned(star: str) -> bool:
    return f'"{star}"' in _RULE_TEXT


def geo(tv):
    by = {p["branch_index"]: p for p in tv.palaces}
    m = next(p for p in tv.palaces if p["name"] == "Mệnh")
    i = m["branch_index"]
    tp = [m, by[(i + 4) % 12], by[(i + 8) % 12], by[(i + 6) % 12]]
    nb = [by[(i - 1) % 12], by[(i + 1) % 12]]
    return m, tp, nb


def labels(tv) -> set[str]:
    m, tp, nb = geo(tv)
    tpm = {s for p in tp for s in p["major_stars"]}
    tps = {s for p in tp for s in p["stars"]}
    hoa_tp = {h for h, v in tv.tu_hoa.items() if v["branch"] in {p["branch_index"] for p in tp}}
    hoa_m = {h for h, v in tv.tu_hoa.items() if v["branch"] == m["branch_index"]}
    maj, dig = m["major_stars"], m["major_dignity"]
    out = set()
    if not maj: out.add("menh_vcd")
    if set(maj) & {"Thất Sát", "Phá Quân", "Tham Lang"} and {"Thất Sát", "Phá Quân", "Tham Lang"} <= tpm: out.add("sat_pha_tham")
    if {"Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"} <= tpm and set(maj) & {"Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"}: out.add("co_nguyet_dong_luong")
    if {"Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"} <= tpm and set(maj) & {"Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"}: out.add("tu_phu_vu_tuong")
    for s in ("Thái Dương", "Thái Âm"):
        if s in maj and dig.get(s) == "hãm": out.add("nhat_nguyet_ham")
        if s in maj and dig.get(s) in ("miếu", "vượng"): out.add("nhat_nguyet_sang")
    if {"Hóa Lộc", "Hóa Quyền", "Hóa Khoa"} <= hoa_tp: out.add("tam_hoa_hoi")
    if "Hóa Kỵ" in hoa_m: out.add("hoa_ky_menh")
    if m["tuan"]: out.add("tuan_menh")
    if m["triet"]: out.add("triet_menh")
    if "Kình Dương" in m["stars"] and m["branch"] == "Ngọ": out.add("kinh_ngo")
    if "Cự Môn" in maj and m["branch"] in ("Tý", "Ngọ"): out.add("cu_ty_ngo")
    if {"Thiên Khôi", "Thiên Việt"} <= {s for p in nb for s in p["stars"]}: out.add("khoi_viet_giap")
    if "Lộc Tồn" in m["stars"]: out.add("loc_ton_menh")
    if {"Địa Không", "Địa Kiếp"} & set(m["stars"]): out.add("khong_kiep_menh")
    if "Tử Vi" in maj: out.add("tu_vi_menh")
    if m["is_than"]: out.add("than_menh")
    if len(set(CAT) & tps) >= 4: out.add("cat_tu_hoi")
    if sum(1 for p in tp for s in p["stars"] if s in SAT) >= 4 and any(d == "hãm" for d in dig.values()): out.add("sat_nang_ham")
    return out


WANT = ["menh_vcd", "sat_pha_tham", "co_nguyet_dong_luong", "tu_phu_vu_tuong", "nhat_nguyet_ham", "nhat_nguyet_sang", "tam_hoa_hoi",
        "hoa_ky_menh", "tuan_menh", "triet_menh", "kinh_ngo", "cu_ty_ngo", "khoi_viet_giap", "loc_ton_menh", "khong_kiep_menh", "tu_vi_menh",
        "than_menh", "cat_tu_hoi", "sat_nang_ham"]


def facts_of(birth: dict, tv=None) -> dict:
    """/api/facts for `birth`, optionally with the computed Tử Vi chart replaced by `tv` (a mutated copy)."""
    req = BirthReq(**birth)
    if tv is None:
        return api.chart_facts(req)
    orig = api._compute
    nb, bz, _ = orig(req)
    api._compute = lambda r: (nb, bz, tv)
    try:
        return api.chart_facts(req)
    finally:
        api._compute = orig


def remove_star(tv, palace, star):
    p = next(x for x in tv.palaces if x["name"] == palace)
    p["stars"] = [s for s in p["stars"] if s != star]
    p["major_stars"] = [s for s in p["major_stars"] if s != star]
    for k in ("minor_dignity", "major_dignity", "minor_dignity_src", "dignity_status"):
        p.get(k, {}).pop(star, None)
    for h in [h for h, v in tv.tu_hoa.items() if v["star"] == star and v["branch"] == p["branch_index"]]:
        del tv.tu_hoa[h]


def variants(birth, tv) -> list[dict]:
    m, tp, nb = geo(tv)
    out = []

    def add(kind, expect, element, note, fn, synthetic=False):
        t = copy.deepcopy(tv)
        fn(t)
        out.append({"kind": kind, "expect": expect, "element": element, "note": note, "synthetic": synthetic, "tv": t})

    sat = [s for s in SAT if s in m["stars"]]
    if sat:
        s = sat[0]
        add("remove_sat", "critical", s, f"bỏ {s} khỏi Mệnh", lambda t: remove_star(t, "Mệnh", s), True)
    else:
        def add_kinh(t):
            p = next(x for x in t.palaces if x["name"] == "Mệnh")
            p["stars"] = p["stars"] + ["Kình Dương"]
        add("add_sat", "critical", "Kình Dương", "thêm Kình Dương vào Mệnh (độ sáng không rõ)", add_kinh, True)
    if m["major_stars"]:
        s = m["major_stars"][0]
        d = m["major_dignity"].get(s)
        nd = "miếu" if d == "hãm" else "hãm"

        def flip(t):
            p = next(x for x in t.palaces if x["name"] == "Mệnh")
            p["major_dignity"][s] = nd
            p.get("dignity_status", {}).pop(s, None)
        add("flip_dignity", "critical", s, f"{s}: {d} → {nd}", flip, True)
    hoa_m = [h for h, v in tv.tu_hoa.items() if v["branch"] == m["branch_index"]]
    if hoa_m:
        h = hoa_m[0]
        add("remove_hoa", "critical", h, f"bỏ {h} ({tv.tu_hoa[h]['star']}) khỏi Mệnh", lambda t: t.tu_hoa.pop(h), True)
    elif m["major_stars"]:
        s = m["major_stars"][0]
        add("add_hoa_ky", "critical", "Hóa Kỵ", f"đặt Hóa Kỵ lên {s} ở Mệnh", lambda t: t.tu_hoa.__setitem__("Hóa Kỵ", {"star": s, "branch": m["branch_index"]}), True)

    def tt(t):
        p = next(x for x in t.palaces if x["name"] == "Mệnh")
        p["tuan"] = not p["tuan"]
    add("toggle_tuan", "critical", "Tuần", ("bỏ" if m["tuan"] else "thêm") + " Tuần ở Mệnh", tt, True)
    quiet = [s for s in m["stars"] if s not in m["major_stars"] and not mentioned(s)]
    if quiet:
        s = quiet[0]
        add("remove_unmentioned", "inert", s, f"bỏ {s} (không luật nào nhắc) khỏi Mệnh", lambda t: remove_star(t, "Mệnh", s))
    else:
        ta = next(x for x in tv.palaces if x["name"] == "Tật Ách")
        minor = [s for s in ta["stars"] if s not in ta["major_stars"] and not mentioned(s)] or [s for s in ta["stars"] if s not in ta["major_stars"]]
        if minor:
            s = minor[0]
            add("remove_tat_ach_minor", "inert", s, f"bỏ {s} khỏi Tật Ách", lambda t: remove_star(t, "Tật Ách", s))
    return out


def main():
    rnd = random.Random(20261020)
    charts = [{"label": "ref_cu_tuat", "labels": [], "birth": REF}]
    _, _, tv = api._compute(BirthReq(**REF))
    charts[0]["labels"] = sorted(labels(tv))
    got = set()
    tries = 0
    while len(got) < len(WANT) and tries < 20000:
        tries += 1
        b = {"year": rnd.randint(1935, 2020), "month": rnd.randint(1, 12), "day": rnd.randint(1, 28), "hour": rnd.randint(0, 23),
             "minute": rnd.choice([0, 30]), "gender": rnd.choice(["male", "female"]), "to_year": 2026}
        try:
            _, _, tv = api._compute(BirthReq(**b))
        except Exception:
            continue
        ls = labels(tv)
        for w in WANT:
            if w in ls and w not in got:
                got.add(w)
                charts.append({"label": w, "labels": sorted(ls), "birth": b})
                break
    missing = [w for w in WANT if w not in got]
    bench, cf = [], []
    for c in charts:
        f = facts_of(c["birth"])
        bench.append({**c, "facts": f})
        _, _, tv = api._compute(BirthReq(**c["birth"]))
        for v in variants(c["birth"], tv):
            t = v.pop("tv")
            cf.append({"base": c["label"], **v, "birth": c["birth"], "facts": facts_of(c["birth"], t)})
    fx = ROOT / "src" / "interpret" / "test" / "fixtures"
    (fx / "benchmark20.json").write_text(json.dumps(bench, ensure_ascii=False, separators=(",", ":")))
    (fx / "counterfactual100.json.gz").write_bytes(gzip.compress(json.dumps(cf, ensure_ascii=False, separators=(",", ":")).encode(), mtime=0))
    kinds = {}
    for v in cf:
        kinds[v["kind"]] = kinds.get(v["kind"], 0) + 1
    print(len(bench), "benchmark charts; missing:", missing, "|", len(cf), "variants", kinds, "| tries", tries)


if __name__ == "__main__":
    main()
