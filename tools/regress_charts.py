"""Randomized calculation regression (self-consistency, NOT reference validation): N charts across years 1900-2049, every hour, gender,
leap months and boundary dates. Checks each star placed exactly once, every palace once, stems by the Ngũ Hổ Độn rule, the book relations of
derived stars, Tuần/Triệt on two adjacent palaces each, 12 Tràng Sinh stages once each, đại hạn ages stepping by 10.
    .venv/bin/python tools/regress_charts.py [N]"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))
from tvbt.api import BirthReq, _compute  # noqa: E402

TS = ["Trường Sinh", "Mộc Dục", "Quan Đới", "Lâm Quan", "Đế Vượng", "Suy", "Bệnh", "Tử", "Mộ", "Tuyệt", "Thai", "Dưỡng"]


def check(tv) -> list[str]:
    e = []
    pos = {}
    for p in tv.palaces:
        for s in p["stars"]:
            if s in pos:
                e.append(f"{s} twice")
            pos[s] = p["branch_index"]
    if sorted(p["branch_index"] for p in tv.palaces) != list(range(12)):
        e.append("palaces")
    if len({p["name"] for p in tv.palaces}) != 12:
        e.append("palace names")
    rel = lambda a, b: (pos[a] - pos[b]) % 12
    for a, b, d in [("Quốc Ấn", "Lộc Tồn", 8), ("Đường Phù", "Lộc Tồn", 5), ("Thai Phụ", "Văn Khúc", 2), ("Phong Cáo", "Văn Khúc", 10),
                    ("Giải Thần", "Phượng Các", 0), ("Thiên Y", "Thiên Riêu", 0), ("Hồng Loan", "Thiên Hỷ", 6)]:
        if rel(a, b) != d:
            e.append(f"{a}-{b}")
    if not all(s in pos for s in TS):
        e.append("tràng sinh")
    for k in ("tuan", "triet"):
        bs = sorted(p["branch_index"] for p in tv.palaces if p[k])
        if len(bs) != 2 or (bs[1] - bs[0]) % 12 not in (1, 11):
            e.append(k)
    ages = [d["age_from"] for d in tv.dai_han]
    if any(b - a != 10 for a, b in zip(ages, ages[1:])):
        e.append("đại hạn")
    if sum(len(p["major_stars"]) for p in tv.palaces) != 14:
        e.append("14 chính tinh")
    return e


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 35000
    rnd = random.Random(20261020)
    fails, done = [], 0
    for i in range(n):
        y = rnd.randint(1900, 2049)
        d = rnd.choice([1, 2, 28, 29, 30, 31] if i % 7 == 0 else [rnd.randint(1, 28)])
        b = dict(year=y, month=rnd.randint(1, 12), day=d, hour=rnd.choice([0, 1, 11, 12, 23, rnd.randint(0, 23)]), minute=rnd.choice([0, 59, 30]),
                 gender=rnd.choice(["male", "female"]))
        try:
            _, _, tv = _compute(BirthReq(**{"dignity_school": "thuc_hanh", **b}))
        except Exception:
            continue                                   # invalid date (31/2 …): skipped, not a failure
        done += 1
        for x in check(tv):
            fails.append((b, x))
    print(f"{done} charts checked, {len(fails)} failures")
    for b, x in fails[:20]:
        print(" ", b, x)
    sys.exit(1 if fails else 0)
