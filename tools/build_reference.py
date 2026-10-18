#!/usr/bin/env python3
"""Builds engine/web/js/reference.json, the data behind the /reference page ("Tra cứu có nguồn").

Everything rule-like is *generated from the rule packs* (no hand-copied text), so the page cannot drift from the engine:
per star -> per palace -> readings with book, page, review status and an evidence tier; brightness tables of both schools
and their disagreements; Bát Tự readings grouped by topic. Reviewer evidence (verbatim, machine-checked quotes) is joined
from engine/data/source_evidence.json when present. Hand-written, hedged editorial text lives in
engine/data/reference_editorial_vi.json and is merged unchanged.

Evidence tiers (shown to the reader):
  checked     status verified AND a reviewer read the cited page and found it supports the rule's claim and conditions (quote in evidence file)
  partial     status verified AND a reviewer read the page: core supported, but the rule is narrower/wider/stronger than the page (see evidence 'issue')
  sourced     status verified, page cited, paraphrased by the project; not individually re-read
  draft       status draft: the book is cited but the condition/operationalisation is the project's, or not fully checked
  hypothesis  no book behind it (experimental / from-memory / system convention)

Run: python tools/build_reference.py   (tests/test_reference.py fails if the output is stale)
"""
from __future__ import annotations

import glob
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "engine"
DATA = ROOT / "data"
OUT = ROOT / "web" / "js" / "reference.json"

TIERS = ("checked", "partial", "sourced", "draft", "hypothesis")
CITE = re.compile(r"\[(KL|TH|TT)\s+pp?\.\s*(\d+)(?:\s*[-–]\s*(\d+))?")
PDF_CITE = re.compile(r"(?:八字真宗\s*)?PDF\s+pp?\.\s*(\d+)(?:\s*[-–]\s*(\d+))?")
BOOK_NAME = {"KL": "Tử Vi Khảo Luận", "TH": "Tử Vi Thực Hành", "TT": "Tử Vi Đẩu Số Toàn Thư", "ZZ": "八字真宗 (Bát Tự Chân Tông)",
             "TTT": "Trích Thiên Tủy", "TVH": "Dự Đoán Theo Tứ Trụ (Thiệu Vĩ Hoa)", "TBCT": "Tử Bình Chân Thuyên (chưa đối chiếu)",
             "SYS": "Quy ước của hệ thống", "EXP": "Giả thuyết thử nghiệm"}
SRC_BOOK = {"SRC_KHAO_LUAN": "KL", "SRC_THUC_HANH": "TH", "SRC_TOAN_THU": "TT", "SRC_BAZI_ZHENZONG": "ZZ", "SRC_TBCT": "TBCT",
            "SRC_ZIPING_ZHENQUAN": "TBCT", "SRC_SYSTEM_STRUCT": "SYS", "SRC_EXPERIMENTAL": "EXP", "SRC_EXPERIMENTAL_PHI": "EXP",
            "SRC_TVDS_TAN_BIEN": "EXP"}
for k in ("SRC_TVH_CACH", "SRC_TVH_DIEM", "SRC_TVH_DIEUHAU", "SRC_TVH_DUNGTHAN"):
    SRC_BOOK[k] = "TVH"
for k in ("NGUYETLENH", "SUYVUONG", "NGUYENLUU", "THONGQUAN", "QUANSAT", "THUONGQUAN", "THANHTROC", "HANTHU", "TONG", "HOA", "TUEVAN"):
    SRC_BOOK["SRC_TTT_" + k] = "TTT"

MAJOR = ["Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh", "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn",
         "Thiên Tướng", "Thiên Lương", "Thất Sát", "Phá Quân"]
MINOR = ["Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt", "Lộc Tồn", "Kình Dương", "Đà La", "Hỏa Tinh",
         "Linh Tinh", "Địa Không", "Địa Kiếp", "Thiên Mã", "Hồng Loan", "Thiên Hỷ", "Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"]
PALACES = ["Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch", "Quan Lộc", "Nô Bộc", "Thiên Di", "Tật Ách", "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ"]
OWN_FACTS = {"palace.own_major_stars", "palace.own_stars"}
HOI_FACTS = {"palace.tam_phuong_stars", "palace.rel.tp_stars", "palace.tam_phuong_majors", "palace.rel.tp_majors", "palace.rel.opp_stars",
             "palace.rel.opp_majors", "palace.rel.flank_stars", "palace.neighbor_stars", "palace.neighbor_majors"}


def load(p):
    return json.loads(Path(p).read_text("utf-8"))


def claims():
    out = {}
    for rel in ("claims_vi.json", "bazi_deep/claims_vi.json"):
        out.update(load(DATA / rel))
    return out


def atoms(cond, mode="all"):
    """Flatten a condition tree into (fact, operator, value, in_any) atoms."""
    out = []
    if not isinstance(cond, dict):
        return out
    if "fact" in cond:
        out.append((cond["fact"], cond.get("operator", "eq"), cond.get("value"), mode))
        return out
    for k in ("all", "any", "not"):
        if k in cond:
            v = cond[k]
            for x in (v if isinstance(v, list) else [v]):
                out += atoms(x, "any" if k == "any" else ("not" if k == "not" else mode))
    return out


def as_list(v):
    return v if isinstance(v, list) else [v]


def claim_text(r, cl):
    """Same phrasing the UI uses: a 'limit' finding reads claims['limit:<id>'] when it exists (util.js claimPhrase)."""
    out = []
    for c in r.get("consequences", []):
        if isinstance(c, dict) and c.get("claim"):
            out.append((c.get("effect") == "limit" and cl.get("limit:" + c["claim"])) or cl.get(c["claim"], ""))
    return " ".join(x for x in out if x).strip()


def parse_rule(r):
    own, hoi, pal, br, extra = [], [], None, None, []
    own_any, hoi_any = [], []
    gender = None
    for fact, op, val, mode in atoms(r.get("conditions", {})):
        if mode == "not":
            extra.append("loại trừ điều kiện")
            continue
        if fact == "palace.name" and op == "eq":
            pal = val
        elif fact in OWN_FACTS and op in ("contains", "contains_all", "contains_any"):
            (own_any if (mode == "any" or op == "contains_any") else own).extend(as_list(val))
        elif fact in HOI_FACTS and op in ("contains", "contains_all", "contains_any"):
            (hoi_any if (mode == "any" or op == "contains_any") else hoi).extend(as_list(val))
        elif fact == "palace.branch" and op in ("in", "eq"):
            br = as_list(val)
        elif fact == "chart.gender":
            gender = val
        elif fact in ("palace.tuan", "palace.triet"):
            nm = {"palace.tuan": "Tuần", "palace.triet": "Triệt"}[fact]
            extra.append("có Tuần hoặc Triệt" if (mode == "any" and val) else ("có " + nm if val else "không có " + nm))
        elif fact.startswith("palace.dignity."):
            extra.append(f"{fact.split('.', 2)[2]} ở mức " + (", ".join(as_list(val)) if op in ("eq", "in") else "theo bảng độ sáng"))
    extra = list(dict.fromkeys(extra))
    return {"pal": pal, "own": list(dict.fromkeys(own)), "hoi": list(dict.fromkeys(hoi)), "own_any": list(dict.fromkeys(own_any)),
            "hoi_any": list(dict.fromkeys(hoi_any)), "br": br, "gender": gender, "extra": extra}


def cite_of(r, srcs):
    d = r.get("description", "")
    m = CITE.search(d)
    if m:
        a, b = m.group(2), m.group(3)
        return m.group(1), (f"{a}-{b}" if b and b != a else a)
    m = PDF_CITE.search(d)
    if m:
        a, b = m.group(1), m.group(2)
        return "ZZ", (f"{a}-{b}" if b and b != a else a)
    for s in r.get("sourceIds", []):
        if s in SRC_BOOK:
            loc = (srcs.get(s) or {}).get("locator")
            return SRC_BOOK[s], loc
    return None, None


def tier(r, ev):
    srcs = r.get("sourceIds", [])
    books = {SRC_BOOK.get(s) for s in srcs}
    if not srcs or books <= {"EXP", "SYS", "TBCT"}:
        return "hypothesis"
    if r.get("reviewStatus") != "verified":
        return "draft"
    if ev and ev.get("verdict") in ("faithful", "unsupported_on_page"):   # the latter = page cite was wrong and has been corrected
        return "checked"
    if ev and ev.get("verdict") == "partly":
        return "partial"
    return "sourced"


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    a = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return (c - a) / d, (c + a) / d


def audit_tokens(ev, stars_out):
    """Numbers quoted in the editorial text, computed from the audit data (never typed by hand)."""
    ents = list(ev.values())
    rnd = [e for e in ents if e.get("sampled_as") == "sample" and e.get("status_at_review") == "verified"]
    tok = {"ev": {"n": len(ents)}, "dignity": {"diff": sum(len(c["dignity"]["diff"]) for c in stars_out.values())}, "base": {}}
    if rnd:
        k = sum(e["verdict"] == "faithful" for e in rnd)
        lo, hi = wilson(k, len(rnd))
        tok["ev"].update(random_n=len(rnd), random_faithful_pct=round(100 * k / len(rnd)), random_ci_lo=round(100 * lo), random_ci_hi=round(100 * hi),
                         random_partly_pct=round(100 * sum(e["verdict"] == "partly" for e in rnd) / len(rnd)),
                         random_wrong_pct=round(100 * sum(e["verdict"] in ("misread", "unsupported_on_page") for e in rnd) / len(rnd)))
    p = ROOT.parent / "docs" / "reading_base_rate.json"
    if p.exists():
        b = load(p)
        tok["base"] = {"n": b["n_charts"], "median_findings": b["distribution"]["findings"]["median"],
                       "median_menh_support": b["distribution"]["menh_supporting"]["median"],
                       "share_pos_menh_pct": round(100 * b["share_charts_with_wealth_rank_success_reading_at_menh"])}
    return tok


def resolve_tokens(node, tok):
    if isinstance(node, str):
        def sub(m):
            try:
                return str(tok[m.group(1)][m.group(2)])
            except KeyError:
                raise SystemExit(f"unresolved editorial token {m.group(0)}")
        return re.sub(r"\{\{(\w+)\.(\w+)\}\}", sub, node)
    if isinstance(node, list):
        return [resolve_tokens(x, tok) for x in node]
    if isinstance(node, dict):
        return {k: (v if k.startswith('_') else resolve_tokens(v, tok)) for k, v in node.items()}
    return node


def build() -> dict:
    cl = claims()
    srcs = {}
    for p in glob.glob(str(DATA / "**" / "sources*.json"), recursive=True):
        for s in load(p).get("sources", []):
            srcs[s["id"]] = s
    ev_path = DATA / "source_evidence.json"
    ev = {e["rule_id"]: e for e in load(ev_path)["entries"]} if ev_path.exists() else {}
    editorial = load(DATA / "reference_editorial_vi.json") if (DATA / "reference_editorial_vi.json").exists() else {}

    tv_files = [p for p in sorted(glob.glob(str(DATA / "pack_*.json"))) if "bazi" not in p]
    bt_files = sorted(glob.glob(str(DATA / "pack_bazi_*.json"))) + [str(DATA / "bazi_deep" / "pack_structure.json"), str(DATA / "bazi_deep" / "pack_temporal.json")]

    # ---------------- Tử Vi ----------------
    by_star = defaultdict(lambda: defaultdict(dict))        # star -> palace -> merge-key -> entry
    n_rules = 0
    for f in tv_files:
        for r in load(f)["rules"]:
            if r.get("system") != "tu_vi":
                continue
            n_rules += 1
            pr = parse_rule(r)
            stars = [(s, "own") for s in pr["own"] + pr["own_any"]] + [(s, "hoi") for s in pr["hoi"] + pr["hoi_any"]]
            if not stars:
                continue
            text = claim_text(r, cl)
            if not text:
                continue
            bk, pg = cite_of(r, srcs)
            e = ev.get(r["id"])
            src = {"id": r["id"], "b": bk, "p": pg, "st": "v" if r.get("reviewStatus") == "verified" else "d", "tier": tier(r, e)}
            if e:
                src["ev"] = {k: e.get(k) for k in ("verdict", "quote", "quote_page", "quote_verified", "context_note", "qualifier", "issue", "gloss_vi", "reading_method")}
            for star, role in stars:
                if star not in MAJOR and star not in MINOR:
                    continue
                pal = pr["pal"] or "_"
                key = (text, tuple(pr["own"]), tuple(pr["hoi"]), tuple(pr["own_any"]), tuple(pr["hoi_any"]), tuple(pr["br"] or ()), pr["gender"], role)
                slot = by_star[star][pal]
                if key in slot:
                    slot[key]["src"].append(src)
                else:
                    slot[key] = {"t": text, "role": role, "with": [s for s in pr["own"] + pr["hoi"] if s != star],
                                 "any": [s for s in pr["own_any"] + pr["hoi_any"] if s != star], "br": pr["br"], "g": pr["gender"],
                                 "x": pr["extra"], "src": [src]}

    def pack_star(star):
        pal_out, cnt = {}, Counter()
        for pal in PALACES + ["_"]:
            lst = list(by_star[star].get(pal, {}).values())
            if not lst:
                continue
            for it in lst:
                it["src"].sort(key=lambda s: (s["st"] != "v", s["b"] or "", s["p"] or ""))
                best = min(TIERS.index(s["tier"]) for s in it["src"])
                it["tier"] = TIERS[best]
                cnt[it["tier"]] += 1
            lst.sort(key=lambda it: (TIERS.index(it["tier"]), it["role"] != "own", it["t"]))
            pal_out[pal] = lst
        return {"palaces": pal_out, "count": dict(cnt), "total": sum(cnt.values())}

    prof = load(DATA / "star_profiles.json")["stars"]
    gl = load(DATA / "glossary_vi.json")
    dth, dtt = load(DATA / "dignity_vn.json")["stars"], load(DATA / "dignity_toanthu.json")["stars"]
    br12 = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
    stars_out = {}
    for s in MAJOR:
        card = pack_star(s)
        a, b = dth.get(s, {}).get("levels", {}), dtt.get(s, {}).get("levels", {})
        card["profile"] = {"element": prof[s]["element"], "dau": prof[s]["dau"], "domain": prof[s]["domain"], "loc": prof[s]["locator"]}
        card["plain"] = gl["stars"][s]["plain"]
        card["dignity"] = {"thuc_hanh": a, "toan_thu": b,
                           "diff": [{"br": x, "th": a[x], "tt": b[x]} for x in br12 if x in a and x in b and a[x] != b[x]],
                           "th_loc": dth.get(s, {}).get("locator"), "tt_loc": dtt.get(s, {}).get("locator")}
        stars_out[s] = card
    minor_out = {}
    for s in MINOR:
        card = pack_star(s)
        if card["total"]:
            minor_out[s] = card
            m = gl["minor"].get(s)
            if m:
                card["plain"] = m["plain"]
                card["kind"] = m.get("kind")

    # Tứ Hóa
    th = load(DATA / "tu_hoa_vi.json")
    tu_hoa = {"source": th["source"], "locator": th["locator"], "meaning": th["meaning"], "position_notes": th["position_notes"],
              "weight_note": th["weight_note"], "by_stem": th["by_stem"]}

    # ---------------- Bát Tự ----------------
    bt = defaultdict(list)
    for f in bt_files:
        for r in load(f)["rules"]:
            text = claim_text(r, cl) or r.get("description", "")
            bk, pg = cite_of(r, srcs)
            e = ev.get(r["id"])
            ent = {"id": r["id"], "t": text, "d": r.get("description"), "st": "v" if r.get("reviewStatus") == "verified" else "d", "b": bk, "p": pg,
                   "tier": tier(r, e), "cat": r.get("category")}
            if e:
                ent["ev"] = {k: e.get(k) for k in ("verdict", "quote", "quote_page", "quote_book", "quote_verified", "context_note", "qualifier", "issue", "gloss_vi", "reading_method")}
            name = Path(f).stem
            grp = {"pack_bazi_zhenzong": "nhat_chu", "pack_bazi_napam": "nap_am", "pack_bazi_zz_direct": "truc_doan",
                   "pack_structure": "cau_truc", "pack_temporal": "van_nien"}.get(name, name)
            bt[grp].append(ent)
    web_path = DATA / "source_evidence_web.json"
    if web_path.exists():
        W = load(web_path)
        names = {**{f"geju:{k}": f"Cách {k}" for k in load(DATA / "bazi_deep" / "geju_defs.json")["defs"]},
                 **{f"pattern:{k}": "Cấu trúc " + v["vi"] for k, v in load(DATA / "bazi_deep" / "patterns_defs.json")["defs"].items()}}
        bt["tbct"] = [{"id": e["rule_id"], "t": names.get(e["rule_id"], e["rule_id"]), "st": "d", "b": "TBCT", "p": e.get("chapter"), "tier": "hypothesis",
                       "web": {k: e.get(k) for k in ("verdict", "chapter", "quote", "quote_url", "second_host_agrees", "gloss_vi", "issue", "qualifier")}}
                      for e in W["entries"]]
        tbct_notes = W["file_level_notes"]
    else:
        tbct_notes = []
    dh = load(DATA / "bazi_deep" / "tvh_dieuhau.json")
    sha = load(DATA / "shensha.json")

    uniq = {}
    for card in list(stars_out.values()) + list(minor_out.values()):
        for lst in card["palaces"].values():
            for it in lst:
                for sr in it["src"]:
                    uniq[sr["id"]] = sr["tier"]
    for lst in bt.values():
        for x in lst:
            uniq[x["id"]] = x["tier"]
    all_tiers = Counter(uniq.values())

    out = {
        "version": 1,
        "note": "Generated by tools/build_reference.py from engine/data packs. Do not edit by hand.",
        "books": BOOK_NAME,
        "tiers": {"checked": "Đã đối chiếu: người đọc trang sách, có trích nguyên văn (máy kiểm lại trích dẫn có nằm trên trang), quy tắc khớp điều kiện",
                  "partial": "Khớp một phần: đã đối chiếu trang sách, lõi đúng nhưng quy tắc hẹp hơn, rộng hơn hoặc mạnh hơn trang (xem phần chênh lệch)",
                  "sourced": "Có nguồn: đã diễn đạt lại từ trang sách có ghi số trang, chưa được đọc lại riêng từng câu",
                  "draft": "Nháp: có sách nhưng điều kiện hoặc cách vận hành là của hệ thống, hoặc chưa kiểm đủ",
                  "hypothesis": "Giả thuyết: không có sách đứng sau (thử nghiệm, quy ước hoặc viết theo trí nhớ)"},
        "tier_counts": {t: all_tiers.get(t, 0) for t in TIERS}, "tier_counts_note": "đếm theo quy tắc (mỗi quy tắc một lần, dù xuất hiện ở nhiều sao)",
        "tu_vi": {"stars": stars_out, "minor": minor_out, "tu_hoa": tu_hoa, "palaces": PALACES,
                  "palace_plain": {p: gl["palaces"][p] for p in PALACES}},
        "bat_tu": {"groups": dict(bt), "tbct_notes": tbct_notes, "dieu_hau": {"cells": dh["cells"], "notes_order": dh["notes_order"], "source": dh["_source"], "note": dh["_note"]},
                   "than_sat": {"source": sha["source"], "locator": sha["locator"], "note": sha["note"], "tables": sha["tables"]}},
        "editorial": resolve_tokens({k: v for k, v in editorial.items() if not k.startswith("_")}, audit_tokens(ev, stars_out)),
        "audit_stats": audit_tokens(ev, stars_out),
    }
    out["_scanned"] = n_rules
    return out


def main():
    out = build()
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), "utf-8")
    print(f"wrote {OUT.relative_to(ROOT.parent)} ({OUT.stat().st_size // 1024} KB); tiers {out['tier_counts']}; tv rules scanned {out['_scanned']}")


if __name__ == "__main__":
    main()
