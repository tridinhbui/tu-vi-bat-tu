"""Generates engine/data/tarot/pack_tarot_pkt.json: the card readings the Tarot page shows, from A. E. Waite's text of The Pictorial Key
to the Tarot as reissued by L. W. de Laurence (The Illustrated Key to the Tarot: The Veil of Divination, Chicago, 1916; Library of
Congress scan, archive.org illustratedkeyto01dela). Its pagination is NOT the 1911 Rider pagination: every page here is the printed page
of the 1916 issue, cited "PKT (1916) tr. N". Source record: SRC_PKT in engine/data/sources.json.

Input: tools/data/tarot_pkt_entries.json, hand-made entries {card, orientation, page, quote_en, text_vi, category, note?}:
  quote_en   Waite's words as printed on that page (at least 4 words; "…" marks words left out, each part is found in order on the page)
  text_vi    a Vietnamese paraphrase of that quote only, framed as what the card suggests ("theo Waite, lá này gợi đến …"), never a forecast
  category   "divinatory" (Part III "Divinatory Meanings" / "Reversed", or Section 3 for the Trumps Major), "another_reading" (a reading Waite
             reports as another account), "description" (the card's description, where it states a meaning)
  note       what Waite gives for that card and orientation that was left out, and why (death, illness, pregnancy or childbirth, accidents,
             prison or crime, sexual conduct, legal or financial instructions, lines framed as a certain future event)

Checks (the build stops on any failure): the card exists in engine/data/tarot/deck.json; orientation upright or reversed; a page; a quote of
at least 4 words; a Vietnamese text free of the banned wording of src/interpret/wording.ts (read from that file, so the two never drift);
the same quote is not used twice for one card. When the PDF is present ($TVBT_BOOKS_DIR or ~/Downloads) every quote must be on its page:
the text layer is OCR, so a part that is not found word for word is accepted when a window of the page matches it at ratio >= FUZZY
(the OCR misreads letters: "honorahle", "sham tight"); such matches are listed by the build and by engine/tests/test_tarot_pack.py.
    .venv/bin/python tools/build_tarot_pack.py"""
import json
import os
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "engine" / "data" / "tarot"
SRC = json.loads((ROOT / "tools" / "data" / "tarot_pkt_entries.json").read_text("utf-8"))
DECK = {c["id"] for c in json.loads((D / "deck.json").read_text("utf-8"))["cards"]}
SOURCE = {"id": "SRC_PKT", "title": "The Pictorial Key to the Tarot", "author": "A. E. Waite", "year": 1916,
          "edition": "Waite's text as reissued in L. W. de Laurence, The Illustrated Key to the Tarot: The Veil of Divination (Chicago, 1916); "
                     "Library of Congress scan, archive.org illustratedkeyto01dela. Pages are this issue's printed pages, not the 1911 Rider pages.",
          "cite": "PKT (1916)"}
PDF_NAMES = ["PictorialKeyToTheTarot.pdf", "pictorial-key-to-the-tarot.pdf", "The Pictorial Key to the Tarot.pdf", "pkt.pdf"]
CATEGORIES = ("divinatory", "another_reading", "description")
MIN_WORDS = 4
FUZZY = 0.86


def banned() -> list[re.Pattern]:
    """The banned patterns, read from the TypeScript list (src/interpret/wording.ts): JS \\b…\\b/i literals become Python regexes."""
    ts = (ROOT / "src" / "interpret" / "wording.ts").read_text("utf-8")
    body = ts[ts.index("BANNED"):ts.index("];")]
    return [re.compile(p, re.I) for p in re.findall(r"/(\\b[^/]+\\b)/i", body)]


def pdf_path() -> Path | None:
    base = Path(os.environ.get("TVBT_BOOKS_DIR", "~/Downloads")).expanduser()
    return next((base / n for n in PDF_NAMES if (base / n).exists()), None)


def norm(s: str) -> str:
    """Letters and digits only, lower case: dashes become spaces, a hyphen (and the line break after it) is dropped."""
    s = unicodedata.normalize("NFKC", s).replace("—", " ").replace("–", " ")
    s = re.sub(r"-\s*", "", s).lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def parts(quote: str) -> list[str]:
    return [p for p in (norm(x) for x in quote.split("…")) if p]


def words(quote: str) -> int:
    return sum(len(p.split()) for p in parts(quote))


def problems(entries: list[dict], pats: list[re.Pattern]) -> list[str]:
    out, seen = [], set()
    for i, e in enumerate(entries):
        tag = f"entry {i} ({e.get('card')}/{e.get('orientation')})"
        if e.get("card") not in DECK:
            out.append(f"{tag}: unknown card")
        if e.get("orientation") not in ("upright", "reversed"):
            out.append(f"{tag}: orientation must be upright or reversed")
        if e.get("category") not in CATEGORIES:
            out.append(f"{tag}: category must be one of {CATEGORIES}")
        page = e.get("page")
        if not ((isinstance(page, int) and page > 0) or (isinstance(page, str) and re.fullmatch(r"\d+(-\d+)?", page))):
            out.append(f"{tag}: page missing")
        if words(str(e.get("quote_en", ""))) < MIN_WORDS:
            out.append(f"{tag}: quote_en needs at least {MIN_WORDS} words")
        key = (e.get("card"), norm(str(e.get("quote_en", ""))))
        if key in seen:
            out.append(f"{tag}: the same quote twice for this card")
        seen.add(key)
        text = str(e.get("text_vi", "")).strip()
        if len(text) < 3:
            out.append(f"{tag}: text_vi missing")
        if any(p.search(re.sub(r"“[^”]*”", " ", text)) for p in pats):
            out.append(f"{tag}: text_vi uses banned wording")
    return out


@lru_cache(maxsize=None)
def page_words(pdf: str, pdf_index: int) -> tuple[str, ...]:
    import fitz  # PyMuPDF, in the project venv
    return tuple(norm(fitz.open(pdf)[pdf_index].get_text()).split())


def find(part: str, page: tuple[str, ...], start: int) -> tuple[int, float] | None:
    """Where a normalised part sits in the page words from `start` on: (end index, 1.0) word for word, else the best fuzzy window."""
    w = part.split()
    n = len(w)
    for i in range(start, len(page) - n + 1):
        if list(page[i:i + n]) == w:
            return i + n, 1.0
    best = None
    for size in (n - 1, n, n + 1):
        for i in range(start, len(page) - size + 1):
            r = SequenceMatcher(None, part, " ".join(page[i:i + size])).ratio()
            if r >= FUZZY and (best is None or r > best[1]):
                best = (i + size, r)
    return best


def check_quote(e: dict, pdf: Path, offset: int) -> tuple[bool, float]:
    """(found, lowest ratio over the parts) for a quote on its printed page(s)."""
    first, last = (int(x) for x in (str(e["page"]).split("-") * 2)[:2])
    page = sum((page_words(str(pdf), p + offset - 1) for p in range(first, last + 1)), ())
    pos, low = 0, 1.0
    for part in parts(e["quote_en"]):
        hit = find(part, page, pos)
        if not hit:
            return False, 0.0
        pos, low = hit[0], min(low, hit[1])
    return True, low


def quotes_off_page(entries: list[dict], pdf: Path, offset: int) -> tuple[list[str], list[str]]:
    """(quotes not on their page, quotes found only through the OCR-tolerant match)."""
    bad, fuzzy = [], []
    for e in entries:
        ok, r = check_quote(e, pdf, offset)
        tag = f"{e['card']}/{e['orientation']} p.{e['page']}: {e['quote_en']}"
        if not ok:
            bad.append("not on the page: " + tag)
        elif r < 1.0:
            fuzzy.append(f"OCR match {r:.2f}: {tag}")
    return bad, fuzzy


def main() -> None:
    entries = SRC["entries"]
    errs = problems(entries, banned())
    pdf, offset = pdf_path(), SRC.get("pdf_offset")
    if entries and pdf and isinstance(offset, int):
        bad, fuzzy = quotes_off_page(entries, pdf, offset)
        errs += bad
        for f in fuzzy:
            print(f, file=sys.stderr)
    elif entries:
        print("note: quotes not checked against the PDF (book absent or pdf_offset not set)", file=sys.stderr)
    if errs:
        sys.exit("\n".join(errs))
    order = {c: i for i, c in enumerate(sorted(DECK))}
    entries = sorted(entries, key=lambda e: (order[e["card"]], e["orientation"] != "upright"))   # stable: the file's order within a card
    keep = ("card", "orientation", "page", "quote_en", "text_vi", "category")
    doc = {"note": "Built by tools/build_tarot_pack.py from tools/data/tarot_pkt_entries.json. Each entry: Waite's words (quote_en) on the "
                   "printed page of the 1916 issue, and a Vietnamese paraphrase of those words only. Notes on what was left out stay in "
                   "the entries file.",
           "source": SOURCE,
           "entries": [{k: e[k] for k in keep} for e in entries]}
    (D / "pack_tarot_pkt.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(len(entries), "entries")


if __name__ == "__main__":
    main()
