"""Regression fixtures for the TypeScript interpretation pipeline: chart facts exactly as /api/facts returns them, plus the Python rule
engine's fired findings for the same chart (the TS engine must reproduce them exactly). Run after any rule-pack or fact change:
    .venv/bin/python tools/interpret/make_fixtures.py"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engine"))
from fastapi.testclient import TestClient  # noqa: E402

from tvbt.api import app  # noqa: E402
from tvbt.knowledge.loader import load_all  # noqa: E402
from tvbt.reasoning import engine  # noqa: E402

CHARTS = [{"year": 1990, "month": 5, "day": 17, "hour": 10, "minute": 30, "gender": "male", "to_year": 2026, "label": "regression 17/05/1990"},
          {"year": 2001, "month": 3, "day": 10, "hour": 10, "minute": 30, "gender": "male", "to_year": 2026, "label": "Cự Môn hãm hóa Lộc"},
          {"year": 2002, "month": 1, "day": 9, "hour": 8, "minute": 0, "gender": "female", "to_year": 2026, "label": "review 09/01/2002"}]
rnd = random.Random(20261018)
for _ in range(5):
    CHARTS.append({"year": rnd.randint(1945, 2025), "month": rnd.randint(1, 12), "day": rnd.randint(1, 28), "hour": rnd.randint(0, 23), "minute": 15,
                   "gender": rnd.choice(["male", "female"]), "to_year": 2026, "label": "random"})

# rare or contradictory configurations: the first chart (deterministic scan) that matches each predicate is added, so the regression set
# covers what random dates seldom produce. Predicates read only the facts /api/facts returns.
def _p(f, name):
    return next(p for p in f["palaces"] if p["name"] == name)


def _hoa_in(f, name, hoa):
    return f["tu_hoa"][hoa]["branch"] == _p(f, name)["branch_index"]


TARGETS = [
    ("Mệnh vô chính diệu", lambda f: not _p(f, "Mệnh")["major_stars"]),
    ("Quan Lộc vô chính diệu", lambda f: not _p(f, "Quan Lộc")["major_stars"]),
    ("Tài Bạch vô chính diệu", lambda f: not _p(f, "Tài Bạch")["major_stars"]),
    ("Phu Thê vô chính diệu, nữ", lambda f: not _p(f, "Phu Thê")["major_stars"] and f["gender"] == "female"),
    ("Tuần tại Mệnh", lambda f: _p(f, "Mệnh")["tuan"] and not _p(f, "Mệnh")["triet"]),
    ("Triệt tại Mệnh", lambda f: _p(f, "Mệnh")["triet"] and not _p(f, "Mệnh")["tuan"]),
    ("Tuần Triệt cùng ở Quan Lộc", lambda f: _p(f, "Quan Lộc")["tuan"] and _p(f, "Quan Lộc")["triet"]),
    ("Hóa Kỵ tại Mệnh", lambda f: _hoa_in(f, "Mệnh", "Hóa Kỵ")),
    ("Hóa Kỵ tại Quan Lộc", lambda f: _hoa_in(f, "Quan Lộc", "Hóa Kỵ")),
    ("Hóa Lộc tại Tài Bạch", lambda f: _hoa_in(f, "Tài Bạch", "Hóa Lộc")),
    ("Thân cư Quan Lộc", lambda f: _p(f, "Quan Lộc")["is_than"]),
    ("Thân Mệnh đồng cung", lambda f: _p(f, "Mệnh")["is_than"]),
    ("Thân cư Thiên Di", lambda f: _p(f, "Thiên Di")["is_than"]),
    ("Tử Vi tại Mệnh", lambda f: "Tử Vi" in _p(f, "Mệnh")["major_stars"]),
    ("Sát Phá Tham hãm tại Mệnh", lambda f: any(_p(f, "Mệnh")["major_dignity"].get(s) == "hãm" for s in ("Thất Sát", "Phá Quân", "Tham Lang"))),
    ("Thái Dương hãm tại Mệnh", lambda f: _p(f, "Mệnh")["major_dignity"].get("Thái Dương") == "hãm"),
    ("Không Kiếp cùng tại Mệnh", lambda f: {"Địa Không", "Địa Kiếp"} <= set(_p(f, "Mệnh")["stars"])),
    ("Lộc Tồn tại Mệnh", lambda f: "Lộc Tồn" in _p(f, "Mệnh")["stars"]),
    ("Tật Ách nhiều sát tinh", lambda f: len({"Kình Dương", "Đà La", "Địa Không", "Địa Kiếp", "Hỏa Tinh", "Linh Tinh"} & set(_p(f, "Tật Ách")["stars"])) >= 3),
    ("Thiên Cơ Thái Âm tại Điền Trạch", lambda f: {"Thiên Cơ", "Thái Âm"} <= set(_p(f, "Điền Trạch")["major_stars"])),
]
EDGES = [{"year": 1931, "month": 2, "day": 17, "hour": 23, "minute": 40, "gender": "female", "to_year": 2026, "label": "sinh 1931, giờ Tý muộn"},
         {"year": 2024, "month": 12, "day": 31, "hour": 0, "minute": 5, "gender": "male", "to_year": 2026, "label": "sinh cuối 2024, giờ Tý sớm"}]


def _scan(client):
    found, srnd = [], random.Random(7)
    todo = list(TARGETS)
    for _ in range(4000):
        if not todo:
            break
        body = {"year": srnd.randint(1940, 2015), "month": srnd.randint(1, 12), "day": srnd.randint(1, 28), "hour": srnd.randint(0, 23), "minute": 15,
                "gender": srnd.choice(["male", "female"]), "to_year": 2026}
        f = client.post("/api/facts", json=body).json()
        for t in list(todo):
            if t[1](f):
                found.append({**body, "label": t[0]})
                todo.remove(t)
                break
    if todo:
        print("not found:", [t[0] for t in todo])
    return found


def main():
    client = TestClient(app)
    CHARTS.extend(EDGES)
    CHARTS.extend(_scan(client))
    rules, sources = load_all()
    out = []
    for c in CHARTS:
        body = {k: v for k, v in c.items() if k != "label"}
        f = client.post("/api/facts", json=body).json()
        res = engine.run(rules, sources, f["base"], system="tu_vi")
        fired = sorted({(x.rule_id, x.subject, x.claim, x.effect, x.basis) for x in res.findings})
        bres = engine.run(rules, sources, f["bazi"]["base"], system="bat_tu")
        bfired = sorted({(x.rule_id, x.subject, x.claim, x.effect, x.basis) for x in bres.findings})
        out.append({"label": c["label"], "birth": body, "facts": f, "python_fired": [list(x) for x in fired], "python_fired_bazi": [list(x) for x in bfired]})
    dst = ROOT / "src" / "interpret" / "test" / "fixtures" / "charts.json"
    dst.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), "utf-8")
    print(dst, dst.stat().st_size, "bytes,", len(out), "charts")


if __name__ == "__main__":
    main()
