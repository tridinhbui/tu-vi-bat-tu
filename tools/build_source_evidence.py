#!/usr/bin/env python3
"""Source-evidence pipeline (reviewer batches -> validated evidence file).

  batches  --outdir D        stratified sample + retrieval-flagged rules, split into reviewer batches (JSON)
  validate --in F... --out O merge reviewer answers, machine-check every quote against the page text, write the evidence file

A reviewer (human or model) reads the cited page and returns, per rule: verdict, the page it found support on, a VERBATIM
quote (<= 30 words) and notes. `validate` re-reads the PDF page and marks quote_verified true only if the quote (accent- and
punctuation-folded) occurs on that page. No quote is trusted without that check. Books: $TVBT_BOOKS_DIR.
"""
from __future__ import annotations
import argparse, collections, glob, json, os, random, re, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import audit_source_anchors as A  # noqa: E402
import show_page as SP  # noqa: E402

DATA = A.DATA
SEED = 20261017


def fold_q(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower().replace("đ", "d"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[\W_]+", "", s)  # drop ALL whitespace/punctuation: PDF line breaks are noisy


def claims():
    out = {}
    for rel in ("claims_vi.json", "bazi_deep/claims_vi.json"):
        out.update(json.load(open(os.path.join(DATA, rel), encoding="utf-8")))
    return out


def compact(r, cl):
    return {"id": r["id"], "status": r.get("reviewStatus"), "description": r.get("description"),
            "claims": [(c.get("effect") == "limit" and cl.get("limit:" + c["claim"])) or cl.get(c["claim"]) for c in r.get("consequences", []) if isinstance(c, dict) and c.get("claim")],
            "conditions": r.get("conditions"), "sourceIds": r.get("sourceIds")}


def cite_of(r):
    ms = list(A.CITE.finditer(r.get("description", "")))
    if ms:
        m = ms[0]
        p = A.pages_of(m)
        return {"book": m.group(1), "pages": [p[0], p[-1]]}
    m = re.search(r"PDF\s+pp?\.\s*(\d+)(?:\s*[-–]\s*(\d+))?", r.get("description", ""))
    if m:
        a = int(m.group(1)); b = int(m.group(2) or a)
        return {"book": "ZZ", "pages": [a, b]}
    return None


def cmd_batches(a):
    random.seed(SEED)
    cl = claims()
    pool = collections.defaultdict(list)
    for rel in sorted(glob.glob(os.path.join(DATA, "pack_*.json"))):
        name = os.path.basename(rel)
        for r in json.load(open(rel, encoding="utf-8"))["rules"]:
            c = cite_of(r)
            if c:
                pool[(c["book"], name)].append((r, c))
    picked = {}
    for (bk, name), rs in sorted(pool.items()):
        k = max(3, round(len(rs) * 0.09))
        for r, c in random.sample(rs, min(k, len(rs))):
            picked[r["id"]] = (r, c, "sample:" + name)
    retr = json.load(open(a.retrieval, encoding="utf-8"))["queue"] if a.retrieval else []
    byid = {r["id"]: (r, c) for lst in pool.values() for r, c in lst}
    for x in retr:
        if x["rule"] in byid and x["rule"] not in picked:
            picked[x["rule"]] = (*byid[x["rule"]], "retrieval-flagged")
    # TTT-sourced Bát Tự structure rules: all
    for r in json.load(open(os.path.join(DATA, "bazi_deep", "pack_structure.json"), encoding="utf-8"))["rules"] + \
            json.load(open(os.path.join(DATA, "bazi_deep", "pack_temporal.json"), encoding="utf-8"))["rules"]:
        if any(s.startswith("SRC_TTT") for s in r.get("sourceIds", [])):
            picked[r["id"]] = (r, {"book": "TTT", "pages": None}, "ttt-all")
    srcs = {s["id"]: s for s in json.load(open(os.path.join(DATA, "bazi_deep", "sources_books.json"), encoding="utf-8"))["sources"]}
    items = []
    for rid, (r, c, why) in picked.items():
        it = compact(r, cl); it["cite"] = c; it["why_sampled"] = why
        if c["book"] == "TTT":
            it["source_locators"] = [srcs[s].get("locator") for s in r["sourceIds"] if s in srcs]
        items.append(it)
    groups = collections.defaultdict(list)
    for it in items:
        bk = it["cite"]["book"]
        groups["BAZI" if bk in ("ZZ", "TTT") else bk].append(it)
    os.makedirs(a.outdir, exist_ok=True)
    plan = {"KL": 2, "TH": 2, "TT": 2, "BAZI": 1}
    n = 0
    for bk, lst in groups.items():
        lst.sort(key=lambda x: x["id"])
        k = plan.get(bk, 1)
        for i in range(k):
            part = lst[i::k]
            fn = os.path.join(a.outdir, f"batch_{bk}_{i + 1}.json")
            json.dump({"book": bk, "items": part}, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print(fn, len(part)); n += len(part)
    print("total", n)


def page_ok(book, page, quote):
    return fold_q(quote) in fold_q(SP.text(book, page))


def cmd_validate(a):
    merged = {}
    for fn in a.inp:
        d = json.load(open(fn, encoding="utf-8"))
        for e in d["entries"] if isinstance(d, dict) else d:
            merged[e["rule_id"]] = e
    meta = {}
    if a.batches:
        for fn in glob.glob(os.path.join(a.batches, "batch_*.json")):
            for it in json.load(open(fn, encoding="utf-8"))["items"]:
                meta[it["id"]] = {"sampled_as": it["why_sampled"].split(":")[0], "status_at_review": it["status"], "cite_book": it["cite"]["book"]}
    ov_path = os.path.join(ROOT, "tools", "data", "evidence_overrides.json")
    overrides = {k: v for k, v in json.load(open(ov_path, encoding="utf-8")).items() if not k.startswith("_")} if os.path.exists(ov_path) else {}
    out, bad = [], []
    for rid, e in sorted(merged.items()):
        e.update(meta.get(rid, {}))
        if rid in overrides:
            e["reviewer_verdict"] = e.get("verdict")
            e.update(overrides[rid])
        bk, pg, q = e.get("quote_book"), e.get("quote_page"), e.get("quote")
        if e.get("reading_method") == "image":
            e["quote_verified"] = None  # read from a page image: cannot be machine-checked
        else:
            e["quote_verified"] = bool(q and bk and pg and page_ok(bk, int(pg), q))
            if q and not e["quote_verified"]:
                bad.append(rid)
        out.append(e)
    json.dump({"version": 1,
               "note": "Per-rule source evidence. Entries were produced by model-assisted reading of the book page (Claude subagents, 2026-10-17); "
                       "quote_verified is machine-checked against the PDF text layer (null = read from a page image, not machine-checkable). "
                       "No second human reviewer yet. 'partly' / 'misread' / 'unsupported_on_page' entries are findings, not yet applied to rule conditions.",
               "entries": out}, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    cnt = collections.Counter(e.get("verdict") for e in out)
    print("entries", len(out), dict(cnt), "quote_verified", sum(1 for e in out if e["quote_verified"]), "failed:", bad)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("batches"); b.add_argument("--outdir", required=True); b.add_argument("--retrieval")
    v = sub.add_parser("validate"); v.add_argument("--in", dest="inp", nargs="+", required=True); v.add_argument("--out", required=True)
    v.add_argument("--batches", help="directory of batch_*.json: attaches sampled_as / status_at_review to each entry")
    a = ap.parse_args()
    {"batches": cmd_batches, "validate": cmd_validate}[a.cmd](a)
