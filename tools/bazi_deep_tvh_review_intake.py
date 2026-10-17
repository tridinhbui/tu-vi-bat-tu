"""Intake validator for the human review of the 120 điều hậu cells (Thiệu Vĩ Hoa tr.389-397).
A reviewer fills docs/bazi_deep_tvh_cells_check.csv (columns nguoi_kiem, bang_theo_anh, chu_thich_theo_anh, ket_qua, ghi_chu_nguoi_kiem) against the page images.
This tool NEVER edits engine data and NEVER resolves the 9 book-internal conflicts: it only reports, per cell, what the reviewer(s) saw versus the engine, and a status:
  no_review            nobody has filled the row
  confirmed_1          one reviewer's transcription equals the engine's (table and notes)
  confirmed_2          two different reviewers both equal the engine's
  disagrees            some reviewer's transcription differs from the engine's, or they differ from each other -> needs a human decision
  unreadable           the reviewer marked the cell unreadable
A cell flagged book_internal_conflict keeps the flag whatever the reviewers say (the conflict is in the book, not in the transcription).
Usage: python tools/bazi_deep_tvh_review_intake.py reviewer1.csv [reviewer2.csv ...]   (each file may be the same template filled by one person)"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENG = json.loads((ROOT / "engine/data/bazi_deep/tvh_dieuhau.json").read_text("utf-8"))
MONTHS = ["Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu"]
STEMS = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
RESULTS = {"khop", "sai_bang", "sai_chu_thich", "khong_doc_duoc"}
NORM = {"kỉ": "Kỷ", "kì": "Kỷ", "kỷ": "Kỷ"}


def _stems(text: str) -> list[str]:
    out = []
    for w in (text or "").replace(",", " ").split():
        w = w.strip().capitalize()
        out.append(NORM.get(w.lower(), w))
    return out


def load(path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check(files: list) -> dict:
    """files: list of csv paths (or list of row-lists). Returns {'cells': {(month, stem): {...}}, 'problems': [...], 'counts': {...}}."""
    problems = []
    seen: dict[tuple, list] = {}
    for fi, src in enumerate(files):
        rows = load(src) if not isinstance(src, list) else src
        keys = [(r["thang"], r["can_ngay"]) for r in rows]
        if sorted(keys) != sorted((m, s) for m in MONTHS for s in STEMS):
            problems.append(f"file {fi}: does not contain exactly the 120 (tháng, can ngày) rows")
        for r in rows:
            who = (r.get("nguoi_kiem") or "").strip()
            if not who and not (r.get("ket_qua") or "").strip():
                continue
            kq = (r.get("ket_qua") or "").strip()
            if not who:
                problems.append(f"{r['thang']}/{r['can_ngay']}: ket_qua without nguoi_kiem")
                continue
            if kq not in RESULTS:
                problems.append(f"{r['thang']}/{r['can_ngay']}: ket_qua '{kq}' not in {sorted(RESULTS)}")
                continue
            seen.setdefault((r["thang"], r["can_ngay"]), []).append({"who": who, "kq": kq, "table": _stems(r.get("bang_theo_anh")), "notes": _stems(r.get("chu_thich_theo_anh")), "note": r.get("ghi_chu_nguoi_kiem", "")})
    cells = {}
    for m in MONTHS:
        for s in STEMS:
            t, n = ENG["cells"][m][s], ENG["notes_order"][m][s]
            conflict = set(t) != set(n)
            revs = seen.get((m, s), [])
            if not revs:
                st = "no_review"
            elif any(x["kq"] == "khong_doc_duoc" for x in revs):
                st = "unreadable"
            else:
                eq = [x for x in revs if x["kq"] == "khop" and x["table"] == t and x["notes"] == n]
                bad = [x for x in revs if x not in eq]
                st = "disagrees" if bad else ("confirmed_2" if len({x["who"] for x in eq}) >= 2 else "confirmed_1")
            cells[(m, s)] = {"status": st, "book_internal_conflict": conflict, "reviewers": [x["who"] for x in revs],
                             "differences": [{"who": x["who"], "table_seen": x["table"], "notes_seen": x["notes"], "kq": x["kq"]} for x in revs if x["kq"] != "khop" or x["table"] != t or x["notes"] != n]}
    counts: dict[str, int] = {}
    for c in cells.values():
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    return {"cells": cells, "problems": problems, "counts": counts, "conflicts_kept": sum(c["book_internal_conflict"] for c in cells.values())}


def main(argv):
    files = argv[1:] or [ROOT / "docs/bazi_deep_tvh_cells_check.csv"]
    r = check(files)
    print("counts:", r["counts"], "| book_internal_conflict cells kept:", r["conflicts_kept"])
    for p in r["problems"]:
        print("PROBLEM:", p)
    for (m, s), c in r["cells"].items():
        if c["status"] in ("disagrees", "unreadable"):
            print(f"{s} × {m}: {c['status']} {c['differences']}")
    return 1 if r["problems"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
