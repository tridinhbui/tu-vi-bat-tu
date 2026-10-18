#!/usr/bin/env python3
"""Page-anchor audit: does the page a rule cites actually mention what the rule is about?

Independent of the engine: reads rule packs as plain JSON and the PDFs through tools/book_text.py.
For each rule citing [KL|TH|TT p.N] it takes the star names the rule talks about (found in its id, description and
condition values) and looks for them on the cited pages (accent-insensitive; the VNI text layers are noisy).

Verdicts per rule:
  anchored      every named star appears on the cited page(s)
  partial       some do
  near          none/some on the cited pages but all of them within +-1 page (printing offset or range edge)
  miss          none within +-1 page
  no_tokens     the rule names no star (structure / palace-only rules): not testable this way
  unreadable    the cited page has too little recognisable text (scan/garbled layer)

This is a *plausibility* check on the citation, not proof that the paraphrase is right. Books are not in the repo
($TVBT_BOOKS_DIR, default ~/Downloads); without them the script exits with a message.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import book_text as B  # noqa: E402

DATA = os.path.join(ROOT, "engine", "data")

CITE = re.compile(r"\[(KL|TH|TT)\s+pp?\.\s*(\d+)(?:\s*[-–]\s*(\d+))?")

STARS = [
    "Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh", "Thiên Phủ", "Thái Âm", "Tham Lang",
    "Cự Môn", "Thiên Tướng", "Thiên Lương", "Thất Sát", "Phá Quân", "Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc",
    "Thiên Khôi", "Thiên Việt", "Lộc Tồn", "Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp",
    "Hồng Loan", "Thiên Hỷ", "Thiên Mã", "Đào Hoa", "Thiên Hình", "Thiên Riêu", "Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ",
    "Tuần", "Triệt",
]
# short forms the books use constantly; matched as whole words only
ALIAS = {
    "Tử Vi": ["Tử"], "Thiên Phủ": ["Phủ"], "Vũ Khúc": ["Vũ"], "Thiên Tướng": ["Tướng"], "Liêm Trinh": ["Liêm"],
    "Tham Lang": ["Tham"], "Cự Môn": ["Cự"], "Thất Sát": ["Sát"], "Phá Quân": ["Phá"], "Thái Dương": ["Nhật"],
    "Thái Âm": ["Nguyệt"], "Thiên Đồng": ["Đồng"], "Thiên Lương": ["Lương"], "Thiên Cơ": ["Cơ"],
    "Kình Dương": ["Kình"], "Đà La": ["Đà"], "Hỏa Tinh": ["Hỏa"], "Linh Tinh": ["Linh"], "Địa Không": ["Không"],
    "Địa Kiếp": ["Kiếp"], "Văn Xương": ["Xương"], "Văn Khúc": ["Khúc"], "Thiên Khôi": ["Khôi"], "Thiên Việt": ["Việt"],
    "Tả Phụ": ["Tả"], "Hữu Bật": ["Hữu"], "Hóa Kỵ": ["Kỵ", "Kị"], "Hóa Lộc": ["Lộc"], "Hóa Quyền": ["Quyền"],
    "Hóa Khoa": ["Khoa"], "Hồng Loan": ["Hồng"], "Đào Hoa": ["Đào"], "Thiên Mã": ["Mã"], "Thiên Hỷ": ["Hỷ", "Hỉ"],
}


def fold(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower().replace("đ", "d"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]", " ", s)


def words(s: str) -> str:
    return " " + re.sub(r"\s+", " ", fold(s)) + " "


def token_present(star: str, padded_text: str) -> bool:
    forms = [star] + ALIAS.get(star, [])
    # Hóa X may also be written 'X' only; Hoá/Hóa folds identically
    return any(f" {fold(f).strip()} " in padded_text for f in forms)


def rule_stars(rule: dict) -> list[str]:
    blob = rule.get("description", "") + " " + json.dumps(rule.get("conditions", {}), ensure_ascii=False)
    # only the descriptive part: drop the citation brackets
    blob = CITE.sub("", blob)
    fb = words(blob)
    return [s for s in STARS if f" {fold(s).strip()} " in fb]


def pages_of(m) -> list[int]:
    a = int(m.group(2))
    b = int(m.group(3)) if m.group(3) else a
    if b < a or b - a > 12:
        b = a
    return list(range(a, b + 1))


def load_rules():
    out = []
    for path in sorted(glob.glob(os.path.join(DATA, "pack_*.json")) + glob.glob(os.path.join(DATA, "**", "pack_*.json"), recursive=True)):
        rel = os.path.relpath(path, DATA)
        for r in json.load(open(path, encoding="utf-8")).get("rules", []):
            out.append((rel, r))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    for bk in ("KL", "TH", "TT"):
        if not B.available(bk):
            print(f"book {bk} not found in {B.books_dir()} - set TVBT_BOOKS_DIR", file=sys.stderr)
            return 2

    cache: dict[tuple[str, int], str] = {}

    def ptext(bk, p):
        if (bk, p) not in cache:
            n = len(B._doc(bk))
            cache[(bk, p)] = words(B.page_text(bk, p)) if 1 <= p <= n else ""
        return cache[(bk, p)]

    rows, summary = [], collections.defaultdict(collections.Counter)
    for rel, r in load_rules():
        ms = list(CITE.finditer(r.get("description", "")))
        if not ms:
            continue
        stars = rule_stars(r)
        for m in ms:
            bk, pages = m.group(1), pages_of(m)
            txt = " ".join(ptext(bk, p) for p in pages)
            near = " ".join(ptext(bk, p) for p in range(min(pages) - 1, max(pages) + 2))
            readable = len(txt.split()) > 80
            if not stars:
                v = "no_tokens"
            elif not readable:
                v = "unreadable"
            else:
                hit = [s for s in stars if token_present(s, txt)]
                hit_near = [s for s in stars if token_present(s, near)]
                if len(hit) == len(stars):
                    v = "anchored"
                elif hit:
                    v = "partial"
                elif len(hit_near) == len(stars):
                    v = "near"
                else:
                    v = "miss"
            summary[bk][v] += 1
            rows.append({"rule": r["id"], "pack": rel, "book": bk, "pages": f"{pages[0]}-{pages[-1]}" if len(pages) > 1 else str(pages[0]),
                         "stars": stars, "verdict": v, "status": r.get("reviewStatus")})
    out = {"summary": {k: dict(v) for k, v in summary.items()}, "rows": rows}
    txt = json.dumps(out, ensure_ascii=False, indent=1)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(txt)
    print(json.dumps(out["summary"], ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
