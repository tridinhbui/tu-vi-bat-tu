#!/usr/bin/env python3
"""Inventory and provenance audit of the rule library (read-only).

Reads every rule pack under engine/data, resolves claim texts, and reports per
pack: rule count, review status, source ids, page-locator coverage, claim-text
coverage and depth. Also builds a topic coverage matrix (Thiên Can ... trường
phái) from rule ids/descriptions/conditions. Writes JSON to stdout or --out.

Nothing here changes data or the engine.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "engine", "data")

# "[KL pp.166-167]", "[TH p.72]", "(PDF p.67)", "tr.386-388", "八字真宗 pp.7-17"
PAGE_RE = re.compile(r"(?:\bpp?\.\s*\d+|\btr\.\s*\d+|\btrang\s*\d+)", re.I)

PACK_GLOBS = [
    "pack_*.json",
    "bazi_deep/pack_*.json",
    "van_han_rules.json",
    "experimental/pack_*.json",
]

CLAIM_FILES = ["claims_vi.json", "bazi_deep/claims_vi.json"]


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def rules_in(path):
    d = load(path)
    return d.get("rules", []) if isinstance(d, dict) else d


def claim_ids(rule):
    out = []
    for c in rule.get("consequences", []):
        if isinstance(c, dict) and c.get("claim"):
            out.append(c["claim"])
    return out


def build_claims():
    claims = {}
    for rel in CLAIM_FILES:
        claims.update(load(os.path.join(DATA, rel)))
    return claims


# Topic coverage: key -> (label, regex over id+description+conditions+claim text)
TOPICS = {
    "bazi": {
        "Thiên Can (10)": r"\b(Giáp|Ất|Bính|Đinh|Mậu|Kỷ|Canh|Tân|Nhâm|Quý)\b|day.?master|nhật chủ|bazi\.dm",
        "Địa Chi (12)": r"\b(Tý|Sửu|Dần|Mão|Thìn|Tỵ|Ngọ|Mùi|Thân|Dậu|Tuất|Hợi)\b|branch",
        "Ngũ hành": r"ngũ hành|element|\b(Mộc|Hỏa|Thổ|Kim|Thủy)\b",
        "Âm dương": r"âm dương|polarity|yin|yang|dương can|âm can",
        "Thập Thần": r"thập thần|ten.?god|chính quan|thất sát|thương quan|thực thần|chính ấn|thiên ấn|chính tài|thiên tài|tỉ kiên|kiếp tài",
        "Tàng can": r"tàng can|hidden|藏干|bản khí|trung khí|dư khí",
        "Vượng suy / thân cường nhược": r"vượng|nhược|suy|strength|cường|40%",
        "Dụng thần / hỉ kỵ": r"dụng thần|yongshen|hỉ thần|kỵ thần|điều hậu|phù ức|thông quan|bệnh dược",
        "Cách cục Bát Tự": r"cách cục|geju|chính quan cách|thất sát cách|tòng|hóa khí|thương quan.*cách|đặc biệt",
        "Đại vận / lưu niên": r"đại vận|luck|lưu niên|temporal|tiểu vận|lưu nguyệt",
        "Hình xung hợp hại": r"xung|hợp|hình|hại|phá|relation|tam hợp|lục hợp",
        "Thần sát": r"thần sát|shensha|thiên ất|đào hoa|dịch mã|dương nhẫn|văn xương|空亡|không vong",
        "Nạp âm": r"nạp âm|napam",
    },
    "tuvi": {
        "Chính tinh (14)": r"Tử Vi|Thiên Phủ|Thái Dương|Thái Âm|Vũ Khúc|Thiên Đồng|Liêm Trinh|Tham Lang|Cự Môn|Thiên Tướng|Thiên Lương|Thất Sát|Phá Quân|Thiên Cơ",
        "Phụ tinh cát (Tả Hữu Xương Khúc Khôi Việt Lộc Tồn)": r"Tả Phụ|Hữu Bật|Văn Xương|Văn Khúc|Thiên Khôi|Thiên Việt|Lộc Tồn|Tả Hữu|Xương Khúc|Khôi Việt",
        "Sát tinh (Kình Đà Hỏa Linh Không Kiếp)": r"Kình Dương|Đà La|Hỏa Tinh|Linh Tinh|Địa Không|Địa Kiếp|sát tinh|Không Kiếp|Kình Đà|Hỏa Linh",
        "Phụ tinh khác (Hồng Loan, Thiên Mã, Đào Hoa, Hình, Riêu...)": r"Hồng Loan|Thiên Hỷ|Thiên Mã|Đào Hoa|Thiên Hình|Thiên Riêu|Cô Thần|Quả Tú|Long Trì|Phượng Các|Hoa Cái|Quốc Ấn|Tang Môn|Bạch Hổ|Thiên Khốc|Thiên Hư",
        "Vòng Trường Sinh / Bác Sĩ / Thái Tuế": r"Trường Sinh|Bác Sĩ|Thái Tuế|Quan Phù|Tuế Phá|vòng",
        "12 cung": r"Mệnh|Phụ Mẫu|Phúc Đức|Điền Trạch|Quan Lộc|Nô Bộc|Thiên Di|Tật Ách|Tài Bạch|Tử Tức|Phu Thê|Huynh Đệ|palace",
        "Tam phương tứ chính": r"tam phương|tứ chính|xung chiếu|hội chiếu|tam hợp|surround|opposite",
        "Tứ Hóa": r"Hóa Lộc|Hóa Quyền|Hóa Khoa|Hóa Kỵ|Tứ Hóa|tu_hoa|phi hóa",
        "Miếu vượng đắc hãm": r"miếu|vượng|đắc địa|hãm|brightness|dignity",
        "Tuần / Triệt": r"Tuần|Triệt",
        "Cách cục Tử Vi": r"cách cục|cách cuộc|cách\b|formation|CACH_",
        "Đại hạn / tiểu hạn / lưu niên": r"đại hạn|tiểu hạn|lưu niên|lưu nguyệt|vận hạn|van_han|nhập hạn",
        "Cục / Mệnh-Thân / nạp âm": r"ngũ hành cục|\bcục\b|Thân cư|Mệnh Thân|nạp âm|am_duong_ly|âm dương lý",
    },
}


def classify_system(pack_path, rule):
    s = rule.get("system")
    if s:
        return s
    return "bat_tu" if "bazi" in pack_path or "zhenzong" in pack_path else "tu_vi"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()

    claims = build_claims()
    sources = {}
    for p in glob.glob(os.path.join(DATA, "**", "sources*.json"), recursive=True):
        d = load(p)
        for s in d.get("sources", []):
            sources[s["id"]] = s
    for p in glob.glob(os.path.join(DATA, "pack_*.json")) + glob.glob(os.path.join(DATA, "**", "pack_*.json"), recursive=True):
        d = load(p)
        if isinstance(d, dict):
            for s in d.get("sources", []):
                if isinstance(s, dict) and "id" in s:
                    sources.setdefault(s["id"], s)

    packs = []
    seen = set()
    all_rules = []
    for g in PACK_GLOBS:
        for path in sorted(glob.glob(os.path.join(DATA, g))):
            if path in seen:
                continue
            seen.add(path)
            rs = rules_in(path)
            rel = os.path.relpath(path, DATA)
            st = collections.Counter(r.get("reviewStatus", "?") for r in rs)
            src = collections.Counter(s for r in rs for s in r.get("sourceIds", []))
            with_page = sum(1 for r in rs if PAGE_RE.search(r.get("description", "")))
            cids = [c for r in rs for c in claim_ids(r)]
            resolved = [c for c in cids if c in claims]
            lens = [len(claims[c]) for c in resolved]
            systems = collections.Counter(classify_system(rel, r) for r in rs)
            packs.append({
                "pack": rel, "rules": len(rs), "status": dict(st), "systems": dict(systems),
                "sources": dict(src), "with_page_locator": with_page,
                "claims_referenced": len(cids), "claims_resolved": len(resolved),
                "claim_len_median": int(statistics.median(lens)) if lens else 0,
                "claim_len_mean": int(statistics.mean(lens)) if lens else 0,
            })
            for r in rs:
                all_rules.append((rel, r))

    # unresolved claim ids and orphan claims
    used = {c for _, r in all_rules for c in claim_ids(r)}
    for _, r in all_rules:                                   # a 'limit' finding is phrased by claims['limit:<id>'] (web/js/util.js claimPhrase)
        for c in r.get("consequences", []):
            if isinstance(c, dict) and c.get("claim") and c.get("effect") == "limit":
                used.add("limit:" + c["claim"])
    exp_ids = {c for rel, r in all_rules if rel.startswith("experimental") for c in claim_ids(r)}
    unresolved = sorted(c for c in used - set(claims) if c.removeprefix("limit:") not in exp_ids and not (c.startswith("limit:") and c[6:] in claims))   # limit:<id> falls back to <id>
    unresolved_experimental = sorted(c for c in exp_ids if c not in claims)
    orphans = sorted(set(claims) - used)

    # source verification state per rule
    src_state = collections.Counter()
    for _, r in all_rules:
        ids = r.get("sourceIds", [])
        if not ids:
            src_state["no_source"] += 1
        elif all(sources.get(i, {}).get("verified") for i in ids):
            src_state["all_sources_verified"] += 1
        elif any(i not in sources for i in ids):
            src_state["source_id_not_in_registry"] += 1
        else:
            src_state["has_unverified_source"] += 1

    # review status vs source verification mismatch (verified rule but unverified source)
    mismatch = []
    for rel, r in all_rules:
        if r.get("reviewStatus") == "verified":
            bad = [i for i in r.get("sourceIds", []) if not sources.get(i, {}).get("verified")]
            if bad or not r.get("sourceIds"):
                mismatch.append({"id": r["id"], "pack": rel, "sources": r.get("sourceIds"), "unverified": bad})

    # topic coverage
    texts = []
    for rel, r in all_rules:
        t = " ".join([r.get("id", ""), r.get("description", ""), json.dumps(r.get("conditions", {}), ensure_ascii=False),
                      " ".join(claims.get(c, "") for c in claim_ids(r))])
        texts.append((rel, r, t))
    coverage = {}
    for sysname, topics in TOPICS.items():
        coverage[sysname] = {}
        for label, rx in topics.items():
            pat = re.compile(rx, re.I)
            hits = [(rel, r) for rel, r, t in texts
                    if classify_system(rel, r) == ("bat_tu" if sysname == "bazi" else "tu_vi") and pat.search(t)]
            st = collections.Counter(r.get("reviewStatus", "?") for _, r in hits)
            srcs = collections.Counter(s for _, r in hits for s in r.get("sourceIds", []))
            coverage[sysname][label] = {"rules": len(hits), "verified": st.get("verified", 0),
                                        "draft": st.get("draft", 0), "sources": dict(srcs.most_common(5))}

    out = {
        "totals": {
            "rules": len(all_rules),
            "claims": len(claims),
            "status": dict(collections.Counter(r.get("reviewStatus", "?") for _, r in all_rules)),
            "systems": dict(collections.Counter(classify_system(rel, r) for rel, r in all_rules)),
            "source_state": dict(src_state),
        },
        "sources_registry": {k: {"title": v.get("title"), "verified": v.get("verified"), "locator": v.get("locator")}
                             for k, v in sorted(sources.items())},
        "packs": packs,
        "unresolved_claim_ids": unresolved,
        "unresolved_claim_ids_experimental_packs": unresolved_experimental,
        "orphan_claims": orphans,
        "verified_with_unverified_source": mismatch,
        "coverage": coverage,
    }
    txt = json.dumps(out, ensure_ascii=False, indent=1)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(txt)
    else:
        print(txt)


if __name__ == "__main__":
    main()
