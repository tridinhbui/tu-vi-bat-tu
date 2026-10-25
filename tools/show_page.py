"""Print a book page's decoded text, or render it as a PNG (for pages whose text layer scrambles line order, e.g. many TH pages).

    python tools/show_page.py KL 218            # decoded text of Tử Vi Khảo Luận p.218
    python tools/show_page.py TH 114 --image DIR  # DIR/TH_114.png
    python tools/show_page.py KL 218 --check "quote text"  # is the quote on the page (book_text.quote_on_page)?

    python tools/show_page.py WEB:CTBG 三春甲木 --check "丙火为尊"   # a saved web snapshot, by chapter

    python tools/show_page.py KD 160 --image DIR  # Kinh Dịch (Ngô Tất Tố) scan: DIR/KD_160.png; text = committed transcription

Books: KL, TH, TT, KD (tools/book_text.py); WEB:<id> for engine/data/sources_web/. Printed page number == PDF page number, except KD
(book_text.KD_OFFSETS)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import book_text  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    book, page = argv[0], (argv[1] if argv[0].startswith("WEB:") else int(argv[1]))
    if book.startswith("WEB:"):
        if "--check" in argv:
            ok = book_text.quote_on_page(book, page, argv[argv.index("--check") + 1])
            print("ON PAGE" if ok else "NOT ON PAGE")
            return 0 if ok else 1
        print(book_text.web_text(book[4:], page))
        return 0
    if "--image" in argv:
        d = Path(argv[argv.index("--image") + 1])
        d.mkdir(parents=True, exist_ok=True)
        print(book_text.render(book, page, str(d / f"{book}_{page}.png"), zoom=2.0))
        return 0
    if "--check" in argv:
        q = argv[argv.index("--check") + 1]
        ok = book_text.quote_on_page(book, page, q)
        print("ON PAGE" if ok else "NOT ON PAGE")
        return 0 if ok else 1
    print(book_text.page_text(book, page))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
