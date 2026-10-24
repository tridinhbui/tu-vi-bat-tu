"""DEEP-3 Tử Vi mining (2026-10-24): raw page entries, each with the verbatim quote that tools/book_text.quote_on_page finds on its page
(a PDF page, a 'WEB:<id>' snapshot section, or a 'SCAN:<id>' transcribed page). One output file per source family in engine/data/kg/mined/:

    deep3_tt.json    Toàn Thư (Vũ Tài Lục): Nam Mệnh ca pp.64-76, phú nôm Tật Ách / Huynh Đệ / Tử Tức pp.91-93, nữ mệnh pp.112-120,
                     cách cục and the 12-cung hợp cách / phá cách verses pp.141-149
    deep3_kl.json    Khảo Luận: named cách pp.43-48, chính tinh groups and 'thế đứng' pp.166-186, sao giải / chế pp.202-206
    deep3_th.json    Thực Hành: ngũ hành of the stars pp.79-81, sao nhập hạn pp.130-133 (text layer scrambled: read on the page images)
    deep3_web.json   紫微斗數全書 卷一 / 卷二 (zh.wikisource snapshot, engine/data/sources_web): 兄弟 / 子女 / 奴仆 / 父母 and the 局 lists
    deep3_scan.json  Thiên Lương, Tử Vi Nghiệm Lý Toàn Thư, 21-page scan pp.13-15 (engine/data/sources_scan/tvnl_scan.txt)

Every entry: id, book, page, palace, heading, quote, quote_checked, condition_text, reading_vi, polarity, concepts, skip (reason, or None),
notes, and duplicate_of when another verified rule already reads the same line.  Run:  .venv/bin/python tools/mining/deep3/build.py"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import book_text  # noqa: E402

OUT = {"tt": "deep3_tt.json", "kl": "deep3_kl.json", "th": "deep3_th.json", "web": "deep3_web.json", "scan": "deep3_scan.json"}
SOURCE = {
    "tt": "Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục) pp.64-76, 91-93, 112-120, 141-149",
    "kl": "Tử Vi Khảo Luận pp.43-48, 166-186, 202-206",
    "th": "Tử Vi Thực Hành pp.79-81, 130-133 (page images read; quotes are contiguous fragments of the text layer)",
    "web": "紫微斗數全書 卷一 / 卷二, zh.wikisource snapshot of 2026-10-24 (engine/data/sources_web/index.json)",
    "scan": "Thiên Lương, Tử Vi Nghiệm Lý Toàn Thư, scan pp.13-15 transcribed in engine/data/sources_scan/tvnl_scan.txt",
}
PAGES = {k: [] for k in OUT}
ENTRIES = {k: [] for k in OUT}
CUR = {"fam": None}


def family(name):
    CUR["fam"] = name


def page(book, p, note, img=True):
    PAGES[CUR["fam"]].append({"book": book, "page": p, "image_checked": img, "note": note})


def E(id, book, p, palace, heading, quote, cond_text, reading, pol, concepts, skip=None, notes="", dup=None, **extra):
    e = {"id": id, "book": book, "page": p, "palace": palace, "heading": heading, "quote": quote, "quote_checked": None,
         "condition_text": cond_text, "reading_vi": reading, "polarity": pol, "concepts": list(concepts), "skip": skip, "notes": notes}
    if dup:
        e["duplicate_of"] = dup
    e.update(extra)
    ENTRIES[CUR["fam"]].append(e)


for f in sorted(glob.glob(os.path.join(HERE, "p_*.py"))):
    exec(open(f, encoding="utf-8").read())

bad, ids = [], set()
for fam, es in ENTRIES.items():
    for e in es:
        assert e["id"] not in ids, e["id"]
        ids.add(e["id"])
        e["quote_checked"] = bool(book_text.quote_on_page(e["book"], e["page"], e["quote"]))
        if not e["quote_checked"]:
            bad.append((e["id"], e["book"], e["page"], e["quote"]))
    if not es:
        continue
    out = os.path.join(ROOT, "engine", "data", "kg", "mined", OUT[fam])
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"source": SOURCE[fam], "pages_read": PAGES[fam], "entries": es}, fh, ensure_ascii=False, indent=1)
    u = sum(1 for e in es if not e["skip"] and not e.get("duplicate_of"))
    print(f"{OUT[fam]}: entries={len(es)} usable={u} skip={sum(1 for e in es if e['skip'])} dup={sum(1 for e in es if e.get('duplicate_of'))}")
for b in bad:
    print("BAD QUOTE", b)
sys.exit(1 if bad else 0)
