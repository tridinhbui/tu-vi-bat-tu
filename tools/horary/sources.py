"""Page access for the horary source books (public-domain scans, Wellcome Library via archive.org).

    python tools/horary/sources.py text  LILLY 121          # OCR text of printed page 121
    python tools/horary/sources.py image LILLY 104 OUTDIR   # PNG of the page (verify tables, glyphs, OCR doubts)
    python tools/horary/sources.py find  LILLY "void of course" [--from 100 --to 130]
    python tools/horary/sources.py check                      # validate every quote in engine/data/horary/*.json

The scans live outside the repo (HORARY_SOURCES, default ~/Downloads/horary_sources): fetch them with `fetch` (archive.org ids
are in WORKS). OCR is 17th-century type: long s reads as f, planet/sign glyphs read as noise, so `find` and `check` compare a
normalised form (f/s folded, punctuation and spacing dropped). A quote that is not on its page fails `check`.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(os.environ.get("HORARY_SOURCES", Path.home() / "Downloads" / "horary_sources"))

# leaf (1-based PDF page) = printed page + offset; offsets measured from the running heads (e.g. Lilly leaf 155 = p.121,
# leaf 856 = p.822: the 1647 book's misnumbered pages keep the same offset, so the printed number is the citation).
WORKS = {
    "LILLY": {"ia": "b30338724", "dir": "lilly1647", "offset": 34,
              "cite": "William Lilly, Christian Astrology (London, 1647), Wellcome Library copy, archive.org b30338724, Public Domain Mark"},
    "BONATUS_1886": {"ia": "b24884054", "dir": "b24884054", "offset": 28,
                     "cite": "Guido Bonatus, The 146 Considerations, tr. Henry Coley (Anima Astrologiae, 1676), reprint London: Redway 1886, "
                             "archive.org b24884054, Public Domain Mark"},
    "BONATUS_1676": {"ia": "b30335735", "dir": "b30335735", "offset": None,
                     "cite": "Anima Astrologiae (London, 1676), Wellcome Library copy, archive.org b30335735, Public Domain Mark (image check only: "
                             "the OCR is unusable)"},
    "PTOLEMY": {"ia": "b29293066", "dir": "b29293066", "offset": 36,
                "cite": "Ptolemy, Tetrabiblos, tr. J. M. Ashmand (London, 1822), archive.org b29293066, Public Domain Mark"},
}


def _pdf(work: str) -> Path:
    w = WORKS[work]
    return BASE / w["dir"] / f"{w['ia']}.pdf"


def fetch(work: str) -> None:
    w = WORKS[work]
    d = BASE / w["dir"]
    d.mkdir(parents=True, exist_ok=True)
    for name in (f"{w['ia']}.pdf", f"{w['ia']}_djvu.txt"):
        if not (d / name).exists():
            urllib.request.urlretrieve(f"https://archive.org/download/{w['ia']}/{name}", d / name)


def _doc(work: str):
    import pymupdf
    return pymupdf.open(_pdf(work))


def leaf(work: str, page: int) -> int:
    off = WORKS[work]["offset"]
    if off is None:
        raise SystemExit(f"{work}: no page offset; cite it by leaf")
    return page + off


def page_text(work: str, page: int) -> str:
    return _doc(work)[leaf(work, page) - 1].get_text()


def norm(s: str) -> str:
    """Fold the OCR's long-s confusions and drop everything but letters and digits."""
    s = s.lower().replace("ſ", "s").replace("ﬁ", "fi").replace("ﬂ", "fl").replace("&", "and")
    s = re.sub(r"[^a-z0-9]", "", s)
    return s.replace("f", "s").replace("u", "v").replace("j", "i").replace("y", "i")


def quote_on_page(work: str, page: int, quote: str, span: int = 1) -> float:
    """Best fuzzy ratio of the quote against the page text (and `span` pages either side, for quotes that run over a page)."""
    pages = [page_text(work, p) for p in range(page - span, page + span + 1) if p > 0]
    hay, needle = norm(" ".join(pages)), norm(quote)
    if not needle:
        return 0.0
    if needle in hay:
        return 1.0
    best, n = 0.0, len(needle)
    step = max(1, n // 8)
    for i in range(0, max(1, len(hay) - n + 1), step):
        r = SequenceMatcher(None, needle, hay[i:i + n]).ratio()
        if r > best:
            best = r
            if best > 0.97:
                break
    return best


def find(work: str, pattern: str, lo: int | None = None, hi: int | None = None) -> None:
    doc, off = _doc(work), WORKS[work]["offset"] or 0
    rx = re.compile(norm(pattern))
    for i in range(doc.page_count):
        p = i + 1 - off
        if (lo and p < lo) or (hi and p > hi):
            continue
        if rx.search(norm(doc[i].get_text())):
            print(f"p.{p} (leaf {i + 1})")


def image(work: str, page: int, out: str, zoom: float = 2.0) -> None:
    import pymupdf
    doc = _doc(work)
    lf = leaf(work, page) if WORKS[work]["offset"] is not None else page
    pix = doc[lf - 1].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
    Path(out).mkdir(parents=True, exist_ok=True)
    path = Path(out) / f"{work.lower()}_p{page}.png"
    pix.save(path)
    print(path)


def check(threshold: float = 0.80) -> int:
    """Every `sources[].quote` in engine/data/horary/*.json must be on its cited page (fuzzy, OCR-tolerant)."""
    bad = 0
    for f in sorted((ROOT / "engine" / "data" / "horary").glob("*.json")):
        data = json.loads(f.read_text())
        for item in _walk(data):
            for s in item.get("sources", []):
                if not s.get("quote") or s.get("work") not in WORKS or s.get("page") is None:
                    continue
                r = quote_on_page(s["work"], int(s["page"]), s["quote"])
                if r < threshold:
                    bad += 1
                    print(f"{f.name}: {item.get('id')} {s['work']} p.{s['page']} ratio {r:.2f}: {s['quote'][:70]!r}")
    print("quote check:", "OK" if not bad else f"{bad} failing")
    return bad


def _walk(x):
    if isinstance(x, dict):
        if "sources" in x:
            yield x
        for v in x.values():
            yield from _walk(v)
    elif isinstance(x, list):
        for v in x:
            yield from _walk(v)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        raise SystemExit(__doc__)
    cmd = a[0]
    if cmd == "text":
        print(page_text(a[1], int(a[2])))
    elif cmd == "image":
        image(a[1], int(a[2]), a[3] if len(a) > 3 else ".")
    elif cmd == "find":
        lo = int(a[a.index("--from") + 1]) if "--from" in a else None
        hi = int(a[a.index("--to") + 1]) if "--to" in a else None
        find(a[1], a[2], lo, hi)
    elif cmd == "fetch":
        for w in (a[1:] or WORKS):
            fetch(w)
    elif cmd == "check":
        sys.exit(1 if check() else 0)
    else:
        raise SystemExit(__doc__)
