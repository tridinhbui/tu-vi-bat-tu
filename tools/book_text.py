"""Read the three project books straight from their PDFs (not from the rule registry).

The tuviglobal PDFs carry a VNI-Windows text layer ("TÖÛ VI KHAÛO LUAÄN"); `decode` turns it into Unicode so quotes can be
checked against the printed page. Pages whose text layer is scanned/garbled must be read as images (see `render`).
Saved web snapshots of public-domain classical texts (engine/data/sources_web/, owner decision 2026-10-24) are checked with book='WEB:<id>'
and the chapter title in place of the page. Books are NOT part of the repository: they are looked up in $TVBT_BOOKS_DIR (default ~/Downloads) and every consumer must
cope with their absence (tests skip).  Printed page number = PDF index + 1 (checked on all three books)."""
from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from pathlib import Path

BOOK_FILES = {"KL": "TuViKhaoLuan.pdf", "TH": "TuViThucHanh.pdf", "TT": "Tử Vi Đẩu Số Toàn Thư.pdf", "KD": "KINH DỊCH TRỌN BỘ.PDF"}
BOOK_NAMES = {"KL": "Tử Vi Khảo Luận", "TH": "Tử Vi Thực Hành", "TT": "Tử Vi Đẩu Số Toàn Thư", "KD": "Kinh Dịch (Ngô Tất Tố dịch)"}

# KD (Kinh Dịch, Ngô Tất Tố) is an image scan with no text layer (only a download watermark) whose printed numbers are not PDF + 1:
# blank pages were dropped from the scan, so printed = PDF page + offset with the offset stepping up.  Read from the running heads of
# all 666 pages (2026-10-25): printed 60, 62, 366 and 666 are not in the scan.  Its page text comes from the committed transcription.
KD_OFFSETS = ((1, 57, 2), (58, 58, 3), (59, 361, 4), (362, 660, 5), (661, 666, 6))   # (first PDF page, last PDF page, printed - PDF)
KD_PAGES = Path(__file__).resolve().parent.parent / "engine" / "data" / "kinh_dich" / "ntt" / "pages.txt"


def pdf_page(book: str, page: int) -> int:
    """1-based PDF page of a printed page number"""
    if book != "KD":
        return page
    for first, last, off in KD_OFFSETS:
        if first <= page - off <= last:
            return page - off
    raise KeyError(f"KD printed page {page} is not in the scan")


def books_dir() -> Path:
    return Path(os.environ.get("TVBT_BOOKS_DIR", "~/Downloads")).expanduser()


def available(book: str) -> bool:
    if book.startswith(("WEB:", "SCAN:")) or book == "KD":
        return _snapshot_file(book).exists()
    return (books_dir() / BOOK_FILES[book]).exists()


_M: dict[str, str] = {}
_low = {
    "a": ("àáảãạ", ["aø", "aù", "aû", "aõ", "aï"]), "ă": ("ăằắẳẵặ", ["aê", "aè", "aé", "aú", "aü", "aë"]),
    "â": ("âầấẩẫậ", ["aâ", "aà", "aá", "aå", "aã", "aä"]), "e": ("èéẻẽẹ", ["eø", "eù", "eû", "eõ", "eï"]),
    "ê": ("êềếểễệ", ["eâ", "eà", "eá", "eå", "eã", "eä"]), "i": ("ìíỉĩị", ["ì", "í", "æ", "ó", "ò"]),
    "o": ("òóỏõọ", ["oø", "où", "oû", "oõ", "oï"]), "ô": ("ôồốổỗộ", ["oâ", "oà", "oá", "oå", "oã", "oä"]),
    "ơ": ("ơờớởỡợ", ["ô", "ôø", "ôù", "ôû", "ôõ", "ôï"]), "u": ("ùúủũụ", ["uø", "uù", "uû", "uõ", "uï"]),
    "ư": ("ưừứửữự", ["ö", "öø", "öù", "öû", "öõ", "öï"]), "y": ("ỳýỷỹỵ", ["yø", "yù", "yû", "yõ", "î"]), "d": ("đ", ["ñ"]),
}
for _chars, _seqs in _low.values():
    for _c, _s in zip(_chars, _seqs):
        _M[_s] = _c
for _s, _c in list(_M.items()):
    _M[_s.upper()] = _c.upper()
_KEYS = sorted(_M, key=len, reverse=True)


def decode(s: str) -> str:
    out, i = [], 0
    while i < len(s):
        for k in _KEYS:
            if s.startswith(k, i):
                out.append(_M[k]); i += len(k); break
        else:
            out.append(s[i]); i += 1
    return "".join(out)


@lru_cache(maxsize=None)
def _doc(book: str):
    import fitz  # PyMuPDF, only needed when the books are present
    return fitz.open(str(books_dir() / BOOK_FILES[book]))


def page_text(book: str, page: int) -> str:
    if book == "KD":
        return snapshot_text("SCAN:KD", page)
    return decode(_doc(book)[page - 1].get_text())


def render(book: str, page: int, out: str, zoom: float = 1.5) -> str:
    _doc(book)[pdf_page(book, page) - 1].get_pixmap(matrix=__import__("fitz").Matrix(zoom, zoom)).save(out)
    return out


def norm(s: str) -> str:
    s = re.sub(r"\s+", " ", s.lower())
    return re.sub(r"[\"“”'’.,;:!?()\-–—]", "", s).replace("  ", " ").strip()


BAZI_MINED = Path(__file__).resolve().parent.parent / "engine" / "data" / "bazi_deep" / "mined"
BAZI_BOOKS = {"TTT": "ttt", "TVH": "tvh", "ZZ": "zz"}      # Trích Thiên Tủy, Thiệu Vĩ Hoa (scan, transcribed), 八字真宗: committed page text


def bazi_page_text(book: str, page: int) -> str:
    return (BAZI_MINED / f"{BAZI_BOOKS[book]}_p{int(page)}.txt").read_text("utf-8")


def web_text(src_id: str, chapter: str) -> str:
    return snapshot_text(f"WEB:{src_id}", chapter)


def quote_on_page(book: str, page, quote: str) -> bool:
    """book KL / TH / TT with a printed page number; TTT / TVH / ZZ (Bát Tự books) against the committed page text in
    engine/data/bazi_deep/mined/ (whitespace-insensitive: the Chinese text layer breaks lines inside words); 'WEB:<id>' / 'SCAN:<id>' (saved
    snapshots, DEEP-3 2026-10-24) with the chapter title / printed page as page: a WEB quote is labelled with its chapter, not a page"""
    if book in BAZI_BOOKS:
        sq = lambda t: re.sub(r"\s+", "", t)
        return sq(quote) in sq(bazi_page_text(book, page))
    if book.startswith(("WEB:", "SCAN:")):
        return norm(quote) in norm(snapshot_text(book, page))
    return norm(quote) in norm(page_text(book, page))


# Saved snapshots (owner decision 2026-10-24): 'WEB:<id>' is a public-domain classical text saved under engine/data/sources_web (cited by
# chapter: `page` is a heading of the snapshot, '' for the whole text); 'SCAN:<id>' is a scan with no text layer, transcribed from the page
# images into engine/data/sources_scan (`page` is the printed page, marked '=== p.N' in the file). Both are in the repository.
DATA = Path(__file__).resolve().parent.parent / "engine" / "data"


def _snapshot_file(book: str) -> Path:
    kind, sid = book.split(":", 1)
    if book == "SCAN:KD":
        return KD_PAGES
    if kind == "WEB":
        idx = json.loads((DATA / "sources_web" / "index.json").read_text("utf-8"))["sources"]
        return DATA / "sources_web" / idx[sid]["file"]
    return DATA / "sources_scan" / f"{sid}.txt"


@lru_cache(maxsize=None)
def snapshot_text(book: str, page) -> str:
    f = _snapshot_file(book)
    if f.suffix == ".json":                                  # Bát Tự snapshots: {chapters: [{chapter, text}]}, the exact chapter title
        return {c["chapter"]: c["text"] for c in json.loads(f.read_text("utf-8"))["chapters"]}[page]
    lines = f.read_text("utf-8").splitlines()
    if book.startswith("SCAN:"):
        head = lambda ln: re.match(r"^=== p\.(\d+)", ln)
        start = next(i for i, ln in enumerate(lines) if head(ln) and int(head(ln).group(1)) == int(page))
        end = next((i for i in range(start + 1, len(lines)) if head(lines[i])), len(lines))
        return "\n".join(lines[start + 1:end])
    if not page:
        return "\n".join(lines)
    level = lambda ln: len(ln) - len(ln.lstrip("=")) if ln.startswith("==") else 0
    start = next(i for i, ln in enumerate(lines) if level(ln) and page in ln)
    end = next((i for i in range(start + 1, len(lines)) if 0 < level(lines[i]) <= level(lines[start])), len(lines))
    return "\n".join(lines[start + 1:end])
