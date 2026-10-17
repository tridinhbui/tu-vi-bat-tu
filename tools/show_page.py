#!/usr/bin/env python3
"""Print the text of one book page (or render it to PNG) for source checking.

usage: show_page.py BOOK PAGE [PAGE2 ...] [--image OUTDIR]
BOOK: KL | TH | TT (Tử Vi, VNI layer decoded) | ZZ (八字真宗) | TTT (Trích Thiên Tủy) | TVH (scan: image only)
PAGE is the PDF page number, 1-based (= printed number for KL/TH/TT/ZZ; see tools/book_text.py).
Books are read from $TVBT_BOOKS_DIR (default ~/Downloads)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import book_text as B

EXTRA = {"ZZ": "bát tự chân tông -[ChienNguyen] 八字真宗.pdf", "TTT": "Trích Thiên Tủy.pdf",
         "TVH": "Dự Đoán Theo Tứ Trụ - Thiệu Vĩ Hoa.pdf"}
_docs = {}


def doc(book):
    import fitz
    if book in B.BOOK_FILES:
        return B._doc(book)
    if book not in _docs:
        _docs[book] = fitz.open(str(B.books_dir() / EXTRA[book]))
    return _docs[book]


def text(book, page):
    d = doc(book)
    if not 1 <= page <= len(d):
        return ""
    t = d[page - 1].get_text()
    return B.decode(t) if book in B.BOOK_FILES else t


def image(book, page, outdir):
    import fitz
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, f"{book}_{page}.png")
    doc(book)[page - 1].get_pixmap(matrix=fitz.Matrix(1.6, 1.6)).save(out)
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    img = None
    if "--image" in a:
        i = a.index("--image"); img = a[i + 1]; a = a[:i] + a[i + 2:]
    book, pages = a[0].upper(), [int(x) for x in a[1:]]
    for p in pages:
        if img:
            print(image(book, p, img))
        else:
            print(f"===== {book} p.{p} =====")
            print(text(book, p))
