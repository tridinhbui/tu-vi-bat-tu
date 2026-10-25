"""Read the three project books straight from their PDFs (not from the rule registry).

The tuviglobal PDFs carry a VNI-Windows text layer ("TÖÛ VI KHAÛO LUAÄN"); `decode` turns it into Unicode so quotes can be
checked against the printed page. Pages whose text layer is scanned/garbled must be read as images (see `render`).
Books are NOT part of the repository: they are looked up in $TVBT_BOOKS_DIR (default ~/Downloads) and every consumer must
cope with their absence (tests skip).  Printed page number = PDF index + 1 (checked on KL, TH, TT); Tử Vi Hàm Số (HS, a Word
print of the 1972 book) starts with a blank cover page, so its printed page N is PDF page N + 1 (`PDF_OFFSET`)."""
from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path

BOOK_FILES = {"KL": "TuViKhaoLuan.pdf", "TH": "TuViThucHanh.pdf", "TT": "Tử Vi Đẩu Số Toàn Thư.pdf", "HS": "tu-vi-ham-so.pdf"}
BOOK_NAMES = {"KL": "Tử Vi Khảo Luận", "TH": "Tử Vi Thực Hành", "TT": "Tử Vi Đẩu Số Toàn Thư", "HS": "Tử Vi Hàm Số"}
PDF_OFFSET = {"HS": 1}


def books_dir() -> Path:
    return Path(os.environ.get("TVBT_BOOKS_DIR", "~/Downloads")).expanduser()


def available(book: str) -> bool:
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
    return decode(_doc(book)[page - 1 + PDF_OFFSET.get(book, 0)].get_text())


def render(book: str, page: int, out: str, zoom: float = 1.5) -> str:
    _doc(book)[page - 1 + PDF_OFFSET.get(book, 0)].get_pixmap(matrix=__import__("fitz").Matrix(zoom, zoom)).save(out)
    return out


def norm(s: str) -> str:
    s = re.sub(r"\s+", " ", s.lower())
    return re.sub(r"[\"“”'’.,;:!?()\-–—]", "", s).replace("  ", " ").strip()


def quote_on_page(book: str, page: int, quote: str) -> bool:
    return norm(quote) in norm(page_text(book, page))
