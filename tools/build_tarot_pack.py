"""Generates engine/data/tarot/pack_tarot_pkt.json: the card readings the Tarot page may show, from A. E. Waite, The Pictorial Key to the
Tarot (London, 1911), Part III, "The Outer Method of the Oracles" / divinatory meanings of each card, upright and reversed.

Input: tools/data/tarot_pkt_entries.json, hand-reviewed entries {card, orientation, page, quote_en, text_vi}: the printed page, the book's
line verbatim, and a Vietnamese rendering of that line and nothing more (no added advice, no forecast). The pack is EMPTY until the book is
on this machine: src/tarot/reading.ts then shows each card's name and a neutral line that its meaning is being prepared from the book.

Checks (the build stops on any failure): the card id exists in engine/data/tarot/deck.json; orientation is upright or reversed; one entry per
card and orientation; a page number; a quote of at least a few words; a Vietnamese text free of the banned wording of
src/interpret/wording.ts (read from that file, so the two never drift). When the PDF is present ($TVBT_BOOKS_DIR or ~/Downloads, see PDF_NAMES)
and the entries file states its "pdf_offset" (PDF page = printed page + offset), every quote must be found on its page.
    .venv/bin/python tools/build_tarot_pack.py"""
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "engine" / "data" / "tarot"
SRC = json.loads((ROOT / "tools" / "data" / "tarot_pkt_entries.json").read_text("utf-8"))
DECK = {c["id"] for c in json.loads((D / "deck.json").read_text("utf-8"))["cards"]}
SOURCE = {"id": "SRC_WAITE_PKT_1911", "title": "The Pictorial Key to the Tarot", "author": "A. E. Waite", "year": 1911,
          "publisher": "William Rider & Son, London", "cite": "A. E. Waite, The Pictorial Key to the Tarot (1911)"}
PDF_NAMES = ["PictorialKeyToTheTarot.pdf", "pictorial-key-to-the-tarot.pdf", "The Pictorial Key to the Tarot.pdf", "pkt.pdf"]


def banned() -> list[re.Pattern]:
    """The banned patterns, read from the TypeScript list (src/interpret/wording.ts): JS \\b…\\b/i literals become Python regexes."""
    ts = (ROOT / "src" / "interpret" / "wording.ts").read_text("utf-8")
    body = ts[ts.index("BANNED"):ts.index("];")]
    return [re.compile(p, re.I) for p in re.findall(r"/(\\b[^/]+\\b)/i", body)]


def pdf_path() -> Path | None:
    base = Path(os.environ.get("TVBT_BOOKS_DIR", "~/Downloads")).expanduser()
    return next((base / n for n in PDF_NAMES if (base / n).exists()), None)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("—", "-")
    return re.sub(r"\s+", " ", re.sub(r"-\s*\n\s*", "", s)).strip().lower()


def problems(entries: list[dict], pats: list[re.Pattern]) -> list[str]:
    out, seen = [], set()
    for i, e in enumerate(entries):
        tag = f"entry {i} ({e.get('card')}/{e.get('orientation')})"
        if e.get("card") not in DECK:
            out.append(f"{tag}: unknown card")
        if e.get("orientation") not in ("upright", "reversed"):
            out.append(f"{tag}: orientation must be upright or reversed")
        key = (e.get("card"), e.get("orientation"))
        if key in seen:
            out.append(f"{tag}: duplicate card and orientation")
        seen.add(key)
        page = e.get("page")
        if not ((isinstance(page, int) and page > 0) or (isinstance(page, str) and re.fullmatch(r"\d+(-\d+)?", page))):
            out.append(f"{tag}: page missing")
        if len(str(e.get("quote_en", "")).split()) < 2:
            out.append(f"{tag}: quote_en missing")
        text = str(e.get("text_vi", "")).strip()
        if len(text) < 3:
            out.append(f"{tag}: text_vi missing")
        if any(p.search(re.sub(r"“[^”]*”", " ", text)) for p in pats):
            out.append(f"{tag}: text_vi uses banned wording")
    return out


def quotes_off_page(entries: list[dict], pdf: Path, offset: int) -> list[str]:
    import fitz  # PyMuPDF, in the project venv
    doc = fitz.open(pdf)
    bad = []
    for e in entries:
        first = int(str(e["page"]).split("-")[0])
        last = int(str(e["page"]).split("-")[-1])
        text = norm(" ".join(doc[p + offset - 1].get_text() for p in range(first, last + 1)))
        if norm(e["quote_en"]) not in text:
            bad.append(f"{e['card']}/{e['orientation']} p.{e['page']}: quote not on the page")
    return bad


def main() -> None:
    entries = SRC["entries"]
    errs = problems(entries, banned())
    pdf, offset = pdf_path(), SRC.get("pdf_offset")
    if entries and pdf and isinstance(offset, int):
        errs += quotes_off_page(entries, pdf, offset)
    elif entries:
        print("note: quotes not checked against the PDF (book absent or pdf_offset not set)", file=sys.stderr)
    if errs:
        sys.exit("\n".join(errs))
    order = {c: i for i, c in enumerate(sorted(DECK))}
    entries = sorted(entries, key=lambda e: (order[e["card"]], e["orientation"] != "upright"))
    doc = {"note": "Built by tools/build_tarot_pack.py from tools/data/tarot_pkt_entries.json. Each entry: the book's line (quote_en) on its "
                   "printed page, and a Vietnamese rendering of that line only. A card with no entry shows its name and a neutral line "
                   "(src/tarot/reading.ts).",
           "source": SOURCE,
           "entries": [{k: e[k] for k in ("card", "orientation", "page", "quote_en", "text_vi")} for e in entries]}
    (D / "pack_tarot_pkt.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(len(entries), "entries")


if __name__ == "__main__":
    main()
