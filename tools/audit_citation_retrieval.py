#!/usr/bin/env python3
"""Citation retrieval test (stronger than star-presence): rank the cited page among ALL pages of the book.

For each rule citing [KL|TH|TT p.N], build a query from the rule's Vietnamese claim text + description (citation stripped),
score every page of that book by TF-IDF cosine over accent-folded unigrams+bigrams, and record the rank of the best cited page.
A random citation would rank ~N/2. Reported as top-1 / top-3 / top-10 hit rates, and a review queue of rules whose
cited page ranks worse than --queue-rank (default 10).

Plausibility only: a high rank means the page shares the rule's vocabulary, not that the paraphrase is faithful.
Needs the books ($TVBT_BOOKS_DIR). Independent of the engine.
"""
from __future__ import annotations

import argparse, collections, json, math, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import book_text as B  # noqa: E402
import audit_source_anchors as A  # noqa: E402

STOP = set("la va cua co khong thi se duoc nhu cho nay mot cac nhung khi ma neu thi o trong voi den tu do ra the".split())


def toks(s):
    w = [x for x in A.fold(s).split() if x not in STOP and not x.isdigit() and len(x) > 1]
    return w + [a + "_" + b for a, b in zip(w, w[1:])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--queue-rank", type=int, default=10)
    a = ap.parse_args()
    claims = json.load(open(os.path.join(A.DATA, "claims_vi.json"), encoding="utf-8"))
    idx = {}
    for bk in ("KL", "TH", "TT"):
        n = len(B._doc(bk))
        docs = [collections.Counter(toks(B.page_text(bk, p))) for p in range(1, n + 1)]
        df = collections.Counter(t for d in docs for t in d)
        idf = {t: math.log((n + 1) / (c + 1)) + 1 for t, c in df.items()}
        vec = []
        for d in docs:
            v = {t: (1 + math.log(c)) * idf[t] for t, c in d.items()}
            nrm = math.sqrt(sum(x * x for x in v.values())) or 1
            vec.append({t: x / nrm for t, x in v.items()})
        idx[bk] = (vec, idf, n)
    rows = []
    for rel, r in A.load_rules():
        d = r.get("description", "")
        for m in A.CITE.finditer(d):
            bk = m.group(1)
            vec, idf, n = idx[bk]
            q_txt = CITE_STRIP(d) + " " + " ".join(claims.get(c["claim"], "") for c in r.get("consequences", []) if isinstance(c, dict) and c.get("claim"))
            q = collections.Counter(toks(q_txt))
            qv = {t: (1 + math.log(c)) * idf.get(t, 0) for t, c in q.items() if t in idf}
            qn = math.sqrt(sum(x * x for x in qv.values())) or 1
            sc = [sum(qv.get(t, 0) * x for t, x in pv.items()) / qn for pv in vec]
            order = sorted(range(n), key=lambda i: -sc[i])
            rank_of = {p + 1: k + 1 for k, p in enumerate(order)}
            pages = A.pages_of(m)
            best = min(rank_of.get(p, n) for p in pages)
            rows.append({"rule": r["id"], "pack": rel, "book": bk, "pages": f"{pages[0]}-{pages[-1]}" if len(pages) > 1 else str(pages[0]),
                         "rank": best, "top": [i + 1 for i in order[:3]], "status": r.get("reviewStatus"), "n_pages": n})
    summ = {}
    for bk in ("KL", "TH", "TT"):
        rs = [x for x in rows if x["book"] == bk]
        t = len(rs)
        summ[bk] = {"cites": t, "top1": round(100 * sum(x["rank"] == 1 for x in rs) / t, 1),
                    "top3": round(100 * sum(x["rank"] <= 3 for x in rs) / t, 1),
                    "top10": round(100 * sum(x["rank"] <= 10 for x in rs) / t, 1),
                    "queue(rank>%d)" % a.queue_rank: sum(x["rank"] > a.queue_rank for x in rs),
                    "median_rank": sorted(x["rank"] for x in rs)[t // 2], "pages_in_book": rs[0]["n_pages"]}
    out = {"summary": summ, "queue": sorted([x for x in rows if x["rank"] > a.queue_rank], key=lambda x: -x["rank"]), "rows": rows}
    if a.out:
        open(a.out, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps(summ, ensure_ascii=False, indent=1))


def CITE_STRIP(d):
    return A.CITE.sub("", d).replace("paraphrased", "")


if __name__ == "__main__":
    main()
