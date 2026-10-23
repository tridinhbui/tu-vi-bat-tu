import json, sys, glob, os
ROOT = "/Users/buidinhtri/Desktop/tuvibattu/.claude/worktrees/agent-a94676969e59ceb88"
sys.path.insert(0, ROOT + "/tools")
import book_text
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = ROOT + "/engine/data/kg/mined/kl_tu_tuc_huynh_de_tat_ach.json"
PAGES, ENTRIES, NATURES = [], [], []


def C(own_major=(), only=False, own_stars=(), branch=(), dignity=None, tam=(), with_any=(), not_=(), tt=None, other=""):
    return {"own_major": list(own_major), "own_major_only": only, "own_stars": list(own_stars), "branch": list(branch),
            "dignity": dignity or {}, "tam_phuong": list(tam), "with_any": list(with_any), "not": list(not_),
            "tuan_triet": tt, "other": other}


def page(book, p, note, img=True):
    PAGES.append({"book": book, "page": p, "image_checked": img, "note": note})


def E(id, book, p, palace, heading, full_line, quote, cond_text, cond, reading, pol, concepts,
      timing=False, skip=None, notes="", dup=None):
    e = {"id": id, "book": book, "page": p, "palace": palace, "heading": heading, "full_line": full_line,
         "quote": quote, "quote_checked": None, "condition_text": cond_text, "condition": cond,
         "reading_vi": reading, "polarity": pol, "concepts": concepts, "timing": timing, "skip": skip, "notes": notes}
    if dup:
        e["duplicate_of"] = dup
    ENTRIES.append(e)


def N(id, kind, star, palace, book, p, quote, full_line, text, use, pol, explains=(), notes=""):
    NATURES.append({"id": id, "kind": kind, "star": star, "palace": palace, "book": book, "page": p, "quote": quote,
                    "quote_checked": None, "full_line": full_line, "text": text, "use": list(use), "pol": pol,
                    "explains": list(explains), "notes": notes})


for f in sorted(glob.glob(HERE + "/p_*.py")):
    exec(open(f, encoding="utf-8").read())
bad = []
ids = set()
for x in ENTRIES + NATURES:
    assert x["id"] not in ids, x["id"]
    ids.add(x["id"])
    x["quote_checked"] = bool(book_text.quote_on_page(x["book"], x["page"], x["quote"]))
    if not x["quote_checked"]:
        bad.append((x["id"], x["book"], x["page"], x["quote"]))
doc = {"source": "Tử Vi Khảo Luận (KL) star sections pp.63-155 + palace chapter p.218 (Cung Tử, Cung Tật) for Tử Tức / "
                 "Huynh Đệ / Tật Ách; Tử Vi Thực Hành (TH) pp.99-101 Huynh Đệ draft checks",
       "pages_read": PAGES, "entries": ENTRIES, "natures": NATURES}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=1)
u = sum(1 for e in ENTRIES if not e["skip"] and not e.get("duplicate_of"))
print(f"entries={len(ENTRIES)} usable={u} skip={sum(1 for e in ENTRIES if e['skip'])} "
      f"dup={sum(1 for e in ENTRIES if e.get('duplicate_of'))} natures={len(NATURES)} pages={len(PAGES)}")
for b in bad:
    print("BAD QUOTE", b)
