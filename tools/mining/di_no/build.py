"""Builder: reads data_*.py modules (ENTRIES, NATURES, PAGES lists), checks quotes, writes the output JSON."""
import sys, json, glob, importlib.util, io, contextlib, os
import warnings
warnings.filterwarnings("ignore")
ROOT = "/Users/buidinhtri/Desktop/tuvibattu/.claude/worktrees/agent-a94676969e59ceb88"
sys.path.insert(0, ROOT + "/tools")
with contextlib.redirect_stderr(io.StringIO()):
    import book_text
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = ROOT + "/engine/data/kg/mined/kl_thien_di_no_boc.json"
COND_KEYS = ["own_major", "own_major_only", "own_stars", "branch", "dignity", "tam_phuong", "with_any", "not", "tuan_triet", "other"]
DEF = {"own_major": [], "own_major_only": False, "own_stars": [], "branch": [], "dignity": {}, "tam_phuong": [],
       "with_any": [], "not": [], "tuan_triet": None, "other": ""}
pages, entries, natures = [], [], []
for f in sorted(glob.glob(HERE + "/data_*.py")):
    spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    pages += getattr(m, "PAGES", [])
    entries += getattr(m, "ENTRIES", [])
    natures += getattr(m, "NATURES", [])
bad = []
ids = set()


def chk(e):
    if e["id"] in ids:
        bad.append(("DUPID", e["id"]))
    ids.add(e["id"])
    with contextlib.redirect_stderr(io.StringIO()):
        ok = book_text.quote_on_page(e.get("book", "KL"), e["page"], e["quote"])
    e["quote_checked"] = bool(ok)
    if not ok:
        bad.append((e["id"], e["page"], e["quote"]))


E_ORDER = ["id", "book", "page", "palace", "heading", "full_line", "quote", "quote_checked", "condition_text", "condition",
           "reading_vi", "polarity", "concepts", "timing", "skip", "duplicate_of", "notes"]
N_ORDER = ["id", "kind", "star", "palace", "book", "page", "quote", "quote_checked", "full_line", "text", "use", "pol",
           "explains", "duplicate_of", "notes"]
out_e = []
for e in entries:
    e = dict(e)
    e.setdefault("book", "KL")
    c = dict(DEF)
    c.update(e.get("condition", {}))
    e["condition"] = {k: c[k] for k in COND_KEYS}
    for k, v in (("timing", False), ("skip", None), ("notes", ""), ("polarity", "neutral"), ("concepts", [])):
        e.setdefault(k, v)
    chk(e)
    out_e.append({k: e[k] for k in E_ORDER if k in e} | {k: v for k, v in e.items() if k not in E_ORDER})
out_n = []
for n in natures:
    n = dict(n)
    n.setdefault("book", "KL")
    n.setdefault("notes", "")
    chk(n)
    out_n.append({k: n[k] for k in N_ORDER if k in n} | {k: v for k, v in n.items() if k not in N_ORDER})
doc = {"source": "Tử Vi Khảo Luận (KL): Thiên Di and Nô Bộc lines from the star sections (pp.63-155) and the palace "
                 "sections (pp.215-219), plus natures/relations bearing on these palaces",
       "pages_read": pages, "entries": out_e, "natures": out_n}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=1)
print("entries", len(out_e), "natures", len(out_n), "pages", len(pages))
print("skip", sum(1 for e in out_e if e.get("skip")), "dup", sum(1 for e in out_e if e.get("duplicate_of")))
for b in bad:
    print("BAD", b)
