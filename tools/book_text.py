"""Read the three project books straight from their PDFs (not from the rule registry).

The tuviglobal PDFs carry a VNI-Windows text layer ("TÖÛ VI KHAÛO LUAÄN"); `decode` turns it into Unicode so quotes can be
checked against the printed page. Pages whose text layer is scanned/garbled must be read as images (see `render`).
Saved web snapshots of public-domain classical texts (engine/data/sources_web/, owner decision 2026-10-24) are checked with book='WEB:<id>'
and the chapter title in place of the page. Books are NOT part of the repository: they are looked up in $TVBT_BOOKS_DIR (default ~/Downloads) and every consumer must
cope with their absence (tests skip).  Printed page number = PDF index + 1 (checked on KL, TH, TT); Tử Vi Hàm Số (HS, a Word
print of the 1972 book) starts with a blank cover page, so its printed page N is PDF page N + 1 (`PDF_OFFSET`)."""
from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from pathlib import Path

BOOK_FILES = {"KL": "TuViKhaoLuan.pdf", "TH": "TuViThucHanh.pdf", "TT": "Tử Vi Đẩu Số Toàn Thư.pdf", "HS": "tu-vi-ham-so.pdf",
              "KD": "KINH DỊCH TRỌN BỘ.PDF"}
BOOK_NAMES = {"KL": "Tử Vi Khảo Luận", "TH": "Tử Vi Thực Hành", "TT": "Tử Vi Đẩu Số Toàn Thư", "HS": "Tử Vi Hàm Số",
              "KD": "Kinh Dịch (Ngô Tất Tố dịch)"}
PDF_OFFSET = {"HS": 1}

# KD (Kinh Dịch, Ngô Tất Tố) is an image scan with no text layer (only a download watermark) whose printed numbers are not PDF + 1:
# blank pages were dropped from the scan, so printed = PDF page + offset with the offset stepping up.  Read from the running heads of
# all 666 pages (2026-10-25): printed 60, 62, 366 and 666 are not in the scan.  Its page text comes from the committed transcription.
KD_OFFSETS = ((1, 57, 2), (58, 58, 3), (59, 361, 4), (362, 660, 5), (661, 666, 6))   # (first PDF page, last PDF page, printed - PDF)
KD_PAGES = Path(__file__).resolve().parent.parent / "engine" / "data" / "kinh_dich" / "ntt" / "pages.txt"


def pdf_page(book: str, page: int) -> int:
    """1-based PDF page of a printed page number"""
    if book != "KD":
        return page + PDF_OFFSET.get(book, 0)
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
    return decode(_doc(book)[pdf_page(book, page) - 1].get_text())


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
    if book in ENGLISH:
        return en_match(book, page, quote)["ok"]
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


# ---------------------------------------------------------------- English astrology books (cung hoàng đạo, owner 2026-10-25)
# AL = Alan Leo, "Astrology for All", 4th ed. 1910 (archive.org dli.ernet.19807; Digital Library of India scan, OCR text layer);
# CA = William Lilly, "Christian Astrology", 1st ed. 1647 (Wellcome Collection b30338724; the OCR reads the long s as 'f');
# TB = Ptolemy, "Tetrabiblos", J. M. Ashmand's translation, 1822 (Wellcome Collection b29293066). Not Robbins.
# Same rule as the Vietnamese books: not in the repository, looked up in $TVBT_BOOKS_DIR, consumers skip when absent. Their text layer
# is OCR, never VNI, so they are read without `decode`.
# EN_PAGE_RANGES: printed page -> PDF page, measured on the page images (render the header strip) and only for the ranges checked;
# a page outside them is refused. AL drifts (the scan skips leaves: printed 49-50 and 63-64 are missing), so it has one range per run.
ENGLISH = {"AL", "CA", "TB"}
BOOK_FILES.update({"AL": "AstrologyForAll.pdf", "CA": "ChristianAstrology.pdf", "TB": "Tetrabiblos.pdf"})
BOOK_NAMES.update({"AL": "Astrology for All", "CA": "Christian Astrology", "TB": "Tetrabiblos"})
EN_PAGE_RANGES: dict[str, list[tuple[int, int, int]]] = {
    # (first printed page, last printed page, PDF page - printed page)
    "AL": [(5, 48, 15),        # images: printed 13 = PDF 28, 16 = PDF 31, 31 = PDF 46, 48 = PDF 63
           (51, 62, 13)],      # images: printed 51 = PDF 64, 62 = PDF 75 (printed 49-50 are not in the scan)
    "CA": [(61, 103, 34)],     # images: printed 93 = PDF 127, 99 = PDF 133 (the "+35" reported earlier is one too many)
    "TB": [(4, 54, 36)],       # images: printed 34 = PDF 70, 42 = PDF 78, 45 = PDF 81 (the "+37" reported earlier is one too many)
}
LONG_S = {"CA"}               # matching folds f and s together for these books ("Seafon" = "Season")
FUZZY_MIN = 0.9               # a quote the OCR garbled slightly still counts when 90 % of its letters line up with the page

_LIGATURES = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl", "ﬅ": "st", "ﬆ": "st"}
_QUOTES = {"‘": "'", "’": "'", "‚": "'", "‛": "'", "′": "'", "`": "'", "´": "'",
           "“": '"', "”": '"', "„": '"', "‟": '"', "″": '"', "«": '"', "»": '"'}


def en_clean(s: str) -> str:
    """English page text as it reads: ligatures and curly quotes made plain, soft hyphens dropped, a word hyphenated across a line
    break joined ("astro-" or "astro¬" + line break + "logy" -> "astrology"), OCR spacing collapsed (runs of spaces, a space
    before , ; : . ! ? or inside brackets), line breaks made spaces. A real hyphen inside a line ("well-known") is kept."""
    import unicodedata
    s = unicodedata.normalize("NFKC", s)
    for a, b in {**_LIGATURES, **_QUOTES}.items():
        s = s.replace(a, b)
    s = s.replace("­", "").replace("‐", "-").replace("‑", "-").replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"(\w)[-¬][ \t]*\n[ \t]*(\w)", r"\1\2", s)          # hyphenated line break
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r" ([,;:.!?)\]])", r"\1", s)
    s = re.sub(r"([(\[]) ", r"\1", s)
    return s.strip()


def en_norm(s: str) -> str:
    """For reading: en_clean, lower case, punctuation and quote marks dropped, dashes made spaces."""
    s = en_clean(s).lower()
    s = re.sub(r"[‒–—―-]", " ", s)
    s = re.sub(r"[\"'.,;:!?()\[\]]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def en_key(s: str, book: str = "") -> str:
    """For matching: letters and digits only (OCR spacing and punctuation never matter), lower case; f and s folded for LONG_S books."""
    k = re.sub(r"[^a-z0-9]", "", en_clean(s).lower())
    return k.replace("f", "s") if book in LONG_S else k


def en_pdf_page(book: str, page: int) -> int:
    """PDF page (1-based) of printed page `page`; ValueError outside the measured ranges."""
    if book not in ENGLISH:
        raise ValueError(f"{book} is not an English book")
    for a, b, off in EN_PAGE_RANGES.get(book, []):
        if a <= page <= b:
            return page + off
    raise ValueError(f"{book} p.{page}: printed page outside the measured ranges {EN_PAGE_RANGES.get(book)}; measure it on the image first")


def en_page_text(book: str, page: int) -> str:
    """Printed page `page` of an English book, cleaned (en_clean)."""
    return en_clean(_doc(book)[en_pdf_page(book, page) - 1].get_text())


def _best_window(hay: str, needle: str) -> float:
    """Best similarity (difflib ratio) of `needle` with a same-length window of `hay`, tried around every place where a 6-letter
    piece of the needle occurs exactly."""
    import difflib
    n = len(needle)
    if n < 12:
        return 0.0
    cands = set()
    for k in range(0, n - 6, 3):
        chunk, start = needle[k:k + 6], 0
        while (i := hay.find(chunk, start)) >= 0:
            cands.add(i - k)
            start = i + 1
    sm, best = difflib.SequenceMatcher(None, autojunk=False), 0.0
    sm.set_seq2(needle)
    for c in cands:
        for d in (-4, -2, 0, 2, 4):
            a = max(0, c + d)
            sm.set_seq1(hay[a:a + n])
            best = max(best, sm.ratio())
    return best


def en_match(book: str, page: int, quote: str) -> dict:
    """Is `quote` on printed page `page`? {'ok', 'exact', 'score'}: exact on the letters-only key, else the best fuzzy window
    (FUZZY_MIN or more counts: the OCR misreads a letter here and there, e.g. 'Asteology')."""
    hay, needle = en_key(en_page_text(book, page), book), en_key(quote, book)
    if needle and needle in hay:
        return {"ok": True, "exact": True, "score": 1.0}
    sc = _best_window(hay, needle)
    return {"ok": sc >= FUZZY_MIN, "exact": False, "score": round(sc, 3)}
