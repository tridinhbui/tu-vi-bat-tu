"""Build van_han_sources.json from entry modules; checks every quote."""
import json, sys, importlib.util, glob, os
ROOT = "/Users/buidinhtri/Desktop/tuvibattu/.claude/worktrees/agent-a94676969e59ceb88"
sys.path.insert(0, ROOT + "/tools")
import book_text
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = ROOT + "/engine/data/kg/mined/van_han_sources.json"
pages_read, entries, page_check = [], [], []
for f in sorted(glob.glob(HERE + "/p_*.py")):
    spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    pages_read += getattr(m, "PAGES", [])
    entries += getattr(m, "ENTRIES", [])
    page_check += getattr(m, "PAGE_CHECK", [])
COND_KEYS = ["own_major", "own_major_only", "own_stars", "branch", "dignity", "tam_phuong", "with_any", "not", "tuan_triet", "natal", "other"]
DEF = {"own_major": [], "own_major_only": False, "own_stars": [], "branch": [], "dignity": {}, "tam_phuong": [], "with_any": [], "not": [], "tuan_triet": None, "natal": {}, "other": ""}
ids = set(); bad = []
out_entries = []
for e in entries:
    assert e["id"] not in ids, e["id"]; ids.add(e["id"])
    ok = book_text.quote_on_page(e["book"], e["page"], e["quote"])
    if not ok: bad.append((e["id"], e["book"], e["page"], e["quote"]))
    c = dict(DEF); c.update(e.get("condition", {}))
    o = {"id": e["id"], "book": e["book"], "page": e["page"], "palace": e.get("palace", "Đại hạn"), "use": e["use"],
         "heading": e["heading"], "full_line": e["full_line"], "quote": e["quote"], "quote_checked": ok,
         "condition_text": e["condition_text"], "condition": {k: c[k] for k in COND_KEYS},
         "reading_vi": e["reading_vi"], "polarity": e["polarity"], "concepts": e.get("concepts", []),
         "timing": e.get("timing", False), "skip": e.get("skip"), "notes": e.get("notes", "")}
    if e.get("duplicate_of"): o["duplicate_of"] = e["duplicate_of"]
    out_entries.append(o)
doc = {"source": "Đại hạn / tiểu hạn / lưu niên lines: Tử Vi Khảo Luận pp.232-236, Tử Vi Thực Hành pp.114, 119, Tử Vi Đẩu Số Toàn Thư pp.97-106 (page images checked). condition.natal = what the natal chart (Mệnh/Thân/tuổi) must have; other condition keys describe the hạn palace (own_*) and its tam phương (tam_phuong/with_any).",
       "pages_read": pages_read, "entries": out_entries, "natures": [], "van_han_rules_page_check": page_check}
json.dump(doc, open(OUT, "w"), ensure_ascii=False, indent=1)
n = len(out_entries); sk = sum(1 for x in out_entries if x["skip"]); du = sum(1 for x in out_entries if x.get("duplicate_of"))
print(f"entries={n} skipped={sk} dup={du} page_check={len(page_check)}")
for b in bad: print("NOT ON PAGE:", b)
