#!/usr/bin/env python3
"""Snapshot 梅花易數 (zh.wikisource, 卷一–三 + main page) into
engine/data/mai_hoa/source_zh.json, split into sections by heading.

    python tools/mai_hoa_snapshot.py                 # fetch live (action=raw)
    python tools/mai_hoa_snapshot.py --from-dir DIR  # use saved <page>.raw files

Each section keeps its heading path (卷二/體用生克篇之二/求財占第十), the raw
wikitext of the section and a cleaned `text` (markup removed, one paragraph
per line). Rule quotes and translations are checked against `text`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "engine" / "data" / "mai_hoa" / "source_zh.json"
UA = "ThienBanResearch/1.0 (tribd.tec research; Mai Hoa source snapshot)"
API = "https://zh.wikisource.org/w/api.php"
PAGES = [("k0", "梅花易數"), ("k1", "梅花易數/卷一"), ("k2", "梅花易數/卷二"), ("k3", "梅花易數/卷三")]


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def raw_url(title: str) -> str:
    return "https://zh.wikisource.org/w/index.php?title=" + urllib.parse.quote(title) + "&action=raw"


def revision(title: str) -> dict:
    q = urllib.parse.urlencode({"action": "query", "prop": "revisions", "rvprop": "ids|timestamp",
                                "format": "json", "formatversion": "2", "titles": title})
    page = json.loads(_get(API + "?" + q))["query"]["pages"][0]
    rev = page["revisions"][0]
    return {"revid": rev["revid"], "revision_timestamp": rev["timestamp"]}


def clean(wikitext: str) -> str:
    t = re.sub(r"\{\{[^{}]*\}\}", "", wikitext)
    t = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", t)
    t = re.sub(r"\[\[([^\]]*)\]\]", r"\1", t)
    t = t.replace("'''", "").replace("<poem>", "").replace("</poem>", "")
    lines = []
    for line in t.split("\n"):
        line = line.strip().strip("　").strip()
        if line.startswith("*"):
            line = line.lstrip("*").strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


HEADING = re.compile(r"^(=+)\s*(.*?)\s*(=+)\s*$")


def split_sections(key: str, wikitext: str) -> list[dict]:
    """Split on =/==/===/==== headings. A heading's own text (before its first
    child heading) becomes a section when it is not empty; leaf headings always
    become sections (empty ones are flagged)."""
    stack: list[tuple[int, str, list[int]]] = []  # (level, name, index path)
    counters: dict[tuple, int] = {}
    blocks: list[dict] = []
    cur = None
    for line in wikitext.split("\n"):
        m = HEADING.match(line)
        if m and len(m.group(1)) == len(m.group(3)):
            level, name = len(m.group(1)), m.group(2)
            while stack and stack[-1][0] >= level:
                stack.pop()
            parent_idx = tuple(stack[-1][2]) if stack else ()
            if level == 1:
                idx: list[int] = []  # 卷 level: the page key already names it
            else:
                counters[parent_idx] = counters.get(parent_idx, 0) + 1
                idx = list(parent_idx) + [counters[parent_idx]]
            stack.append((level, name, idx))
            cur = {"level": level, "names": [s[1] for s in stack], "idx": idx, "lines": []}
            blocks.append(cur)
        elif cur is not None:
            cur["lines"].append(line)
        elif line.strip():
            blocks.append({"level": 0, "names": [], "idx": [], "lines": [line]})
            cur = blocks[-1]
    out = []
    for i, b in enumerate(blocks):
        raw = "\n".join(b["lines"]).strip("\n")
        text = clean(raw)
        has_child = i + 1 < len(blocks) and blocks[i + 1]["level"] > b["level"]
        if not text and has_child:
            continue
        if b["level"] == 0 and not text:
            continue
        sid = key + ("." + ".".join(str(n) for n in b["idx"]) if b["idx"] else "")
        sec = {"id": sid, "path": "/".join(b["names"]), "heading": b["names"][-1] if b["names"] else "",
               "wikitext": raw, "text": text}
        if not text:
            sec["empty"] = True
        out.append(sec)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-dir", type=Path, help="directory with <title with / as _>.raw files")
    ap.add_argument("--fetched", default=date.today().isoformat())
    args = ap.parse_args()

    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    old_pages = {p["title"]: p for p in old.get("pages", [])}
    pages, sections = [], []
    for key, title in PAGES:
        if args.from_dir:
            data = (args.from_dir / (title.replace("/", "_") + ".raw")).read_bytes()
        else:
            data = _get(raw_url(title))
        rev = revision(title)
        wikitext = data.decode("utf-8")
        pages.append({
            "key": key, "title": title,
            "url": "https://zh.wikisource.org/wiki/" + title,
            "raw_url": raw_url(title),
            "oldid_url": f"https://zh.wikisource.org/w/index.php?oldid={rev['revid']}",
            **rev,
            "fetched": args.fetched,
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
            "wikitext": wikitext,
        })
        prev = old_pages.get(title)
        if prev and prev["sha256"] != pages[-1]["sha256"]:
            print(f"WARNING: {title} changed since the stored snapshot (revid {prev['revid']} -> {rev['revid']})")
        for s in split_sections(key, wikitext):
            s["page"] = key
            sections.append(s)

    doc = {
        "id": "WEB:zh_meihua",
        "title": "梅花易數",
        "attributed_author": "邵雍 (traditional attribution)",
        "license": "public domain (classical text); Wikisource transcription, {{PD-old}}",
        "note": ("Snapshot of the zh.wikisource 梅花易數 pages. `text` is the section with wiki markup removed "
                 "(templates, links, ''' and <poem>), one paragraph per line; `wikitext` is the raw section. "
                 "The page `sha256` is over the exact bytes returned by action=raw. Rebuild with "
                 "tools/mai_hoa_snapshot.py."),
        "edition": old.get("edition", {}),
        "pages": pages,
        "sections": sections,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    print(f"wrote {OUT} ({len(sections)} sections)")


if __name__ == "__main__":
    main()
