"""Static content pages, generated from the project's own sourced data (no hand-written star meanings, no AI text).

Writes into engine/web (served as static assets by the Worker):
  bai-viet/                      article index
  bai-viet/sao/<slug>/           one article per star: glossary intro + dignity table + every VERIFIED rule that names the star
  bai-viet/cung/<slug>/          one article per palace: every VERIFIED rule seated in that palace, grouped by star
  bai-viet/cach-cuc/<slug>/      one article per named cách cục of Tử Vi Thực Hành (pp.72-74) plus verified rules naming it
  gioi-thieu/  hoi-dap/  xem-ngay/   about, FAQ and the month calendar shell (its data comes from /api/calendar)
  sitemap.xml  robots.txt

Every statement is the project's Vietnamese paraphrase of a rule (claims_vi.json) with the book and page the rule cites; draft
rules are left out. Run: .venv/bin/python tools/build_site.py  (test_sitegen.py fails when the committed pages are stale).
"""
from __future__ import annotations

import html
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from .knowledge.loader import DATA, PACKS

WEB = Path(__file__).resolve().parent.parent / "web"
ORIGIN = "https://tu-vi-bat-tu.tridinhbui0901.workers.dev"
CONTENT_DATE = "2026-10-21"    # bump when the article data changes meaningfully (dateModified in structured data)
SITE = "Thiên Bàn"

MAJOR = ["Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh", "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn",
         "Thiên Tướng", "Thiên Lương", "Thất Sát", "Phá Quân"]
TU_HOA = ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"]
PALACES = ["Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch", "Quan Lộc", "Nô Bộc", "Thiên Di", "Tật Ách", "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ"]
BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
DIGNITY_SCHOOLS = [("thuc_hanh", "Thực Hành"), ("toan_thu", "Toàn Thư"), ("khao_luan", "Khảo Luận")]
BOOK_ORDER = ["SRC_THUC_HANH", "SRC_KHAO_LUAN", "SRC_TOAN_THU", "SRC_TVNL_TOAN_THU", "SRC_TVNL_1974", "SRC_HAM_SO"]
# A few TH cách names cannot be cut out of the claim text by the generic rule (the name itself contains "ở").
CACH_NAME_OVERRIDE = {"Phá Quân ở Mão hoặc Dậu": "Phá Quân ở Mão Dậu"}
CACH_MIN_LEN = 4

esc = lambda s: html.escape(str(s), quote=True)


def slug(s: str) -> str:
    s = s.replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


# ---------------------------------------------------------------- data
def _json(name: str):
    return json.loads((DATA / name).read_text("utf-8"))


def load() -> dict:
    """Everything the pages are made of, read once."""
    claims = _json("claims_vi.json")
    sources = {s["id"]: s for s in _json("sources.json")["sources"]}
    rules, draft = [], Counter()
    for name in PACKS:
        pack = _json(name)
        for s in pack.get("sources", []):
            sources.setdefault(s["id"], s)
        for r in pack["rules"]:
            if r["reviewStatus"] != "verified":
                draft[r["system"]] += 1
                continue
            r = dict(r, _pack=name)
            rules.append(r)
    return {"claims": claims, "sources": sources, "rules": rules, "draft": draft,
            "glossary": _json("glossary_vi.json"), "dignity": _json("dignity_kb.json")}


_CITE = re.compile(r"\b(KL|TH|TT|TL|NL|HS)\s*(?:pp?\.)\s*(\d+(?:\s*[-–]\s*\d+)?(?:\s*,\s*\d+(?:\s*[-–]\s*\d+)?)*)")


def cite_of(rule: dict) -> tuple[str, str] | None:
    """(source id, 'tr. 72') from the rule's bracketed locator; None when the rule cites no page."""
    for br in reversed(re.findall(r"\[([^\[\]]+)\]", rule["description"])):
        m = _CITE.search(br)
        if m:
            pages = re.sub(r"\s+", "", m.group(2)).replace("–", "-").replace(",", ", ")
            return rule["sourceIds"][0], f"tr. {pages}"
    return None


def statement(rule: dict, claims: dict) -> dict | None:
    """The reader-facing line of a verified rule: the project's paraphrase + book + page."""
    finding = next((c for c in rule["consequences"] if c.get("kind") == "finding"), None)
    cite = cite_of(rule)
    if not finding or not cite:
        return None
    claim = finding["claim"]
    text = claims.get("limit:" + claim) if finding.get("effect") == "limit" else None
    text = text or claims.get(claim)
    if not text:
        return None
    text = re.sub(r"^khuynh hướng\s+", "", text.strip())
    return {"id": rule["id"], "text": text[0].upper() + text[1:], "source": cite[0], "page": cite[1], "tags": tags(rule, text),
            "effect": finding.get("effect", "neutral"), "system": rule["system"]}


def _top_leaves(cond):
    """Leaves that must ALL hold (top-level AND terms), so a tag never comes from inside an 'any' or a 'not'."""
    if isinstance(cond, dict) and "all" in cond:
        for c in cond["all"]:
            yield from _top_leaves(c)
    elif isinstance(cond, dict) and "fact" in cond:
        yield cond


def tags(rule: dict, text: str) -> list[str]:
    """Conditions the paraphrase may leave unsaid but a reader needs: gender, the palace's branch, the year stem or branch."""
    out, low = [], text.lower()
    for leaf in _top_leaves(rule["conditions"]):
        f, v = leaf["fact"], leaf.get("value")
        vals = [x for x in (v if isinstance(v, list) else [v]) if isinstance(x, str)]
        if f == "chart.gender" and vals and leaf.get("operator", "eq") in ("eq", "in"):
            g = "nữ" if vals[0] in ("nữ", "female") else "nam"
            if g + " mệnh" not in low and "đàn ông" not in low and "đàn bà" not in low:
                out.append(f"{g} mệnh")
        elif f == "palace.branch" and vals and leaf.get("operator", "eq") in ("eq", "in") and not any(b in text for b in vals):
            out.append("cung ở " + ", ".join(vals))
        elif f in ("chart.year_stem", "chart.year_branch") and vals and not any(b in text for b in vals):
            out.append("tuổi " + ", ".join(vals))
    return out


def _leaves(cond, neg=False):
    if not isinstance(cond, dict):
        return
    for k in ("all", "any"):
        for c in cond.get(k, []):
            yield from _leaves(c, neg)
    if "not" in cond:
        yield from _leaves(cond["not"], True)
    if "fact" in cond or "ref" in cond:
        yield cond, neg


def stars_named(rule: dict) -> list[str]:
    """Stars a rule requires to be present (anything under a 'not' is left out: 'không gặp Kình' is not about Kình)."""
    out: list[str] = []
    for leaf, neg in _leaves(rule["conditions"]):
        if neg:
            continue
        fact = leaf.get("fact") or leaf.get("ref", {}).get("fact", "")
        vals: list = []
        if fact.startswith("palace.dignity."):
            vals = [fact.split(".", 2)[2]]
        elif "star" in fact or fact.split(".")[-1].endswith("hoa"):
            v = leaf.get("value")
            vals = v if isinstance(v, list) else [v]
        for v in vals:
            if isinstance(v, str) and v not in out:
                out.append(v)
    return out


def palaces_of(rule: dict) -> list[str]:
    for leaf, neg in _leaves(rule["conditions"]):
        if not neg and leaf.get("fact") == "palace.name":
            v = leaf["value"]
            return [x for x in (v if isinstance(v, list) else [v]) if x in PALACES]
    return []


def _book_key(sid: str) -> tuple:
    return (BOOK_ORDER.index(sid) if sid in BOOK_ORDER else 9, sid)


def _page_key(p: str) -> int:
    m = re.search(r"\d+", p)
    return int(m.group()) if m else 0


def _sort(items: list[dict]) -> list[dict]:
    seen, out = set(), []
    for it in sorted(items, key=lambda x: (BOOK_ORDER.index(x["source"]) if x["source"] in BOOK_ORDER else 9, _page_key(x["page"]), x["text"])):
        k = (it["text"], it["source"], it["page"], tuple(it.get("tags", ())))
        if k not in seen:
            seen.add(k)
            out.append(it)
    return out


def _norm(c):
    if "all" in c or "any" in c:
        k = "all" if "all" in c else "any"
        return (k, frozenset(_norm(x) for x in c[k]))
    if "not" in c:
        return ("not", _norm(c["not"]))
    if "count" in c:
        return ("count", c.get("operator", "eq"), c.get("value"), frozenset(_norm(x) for x in c["count"]))
    f = c.get("fact") or ("ref", c["ref"].get("palace"), c["ref"].get("fact"))
    if isinstance(f, str):
        f = f.replace("own_major_stars", "own_stars")
    v, op = c.get("value"), c.get("operator", "eq")
    if isinstance(v, list) and len(v) == 1 and op == "in":
        v, op = v[0], "eq"
    if isinstance(v, list):
        v = tuple(sorted(map(str, v)))
    return (f, op, v)


def conjuncts(cond) -> frozenset:
    """A condition as the set of its top-level AND terms (nested 'all' flattened). A ⊆ B means B implies A."""
    if isinstance(cond, dict) and "all" in cond:
        return frozenset().union(*(conjuncts(x) for x in cond["all"])) if cond["all"] else frozenset()
    return frozenset([_norm(cond)])


def cach_name(text: str) -> str | None:
    """'cách Lộc Mã giao trì (Lộc và Mã đồng cung) ở cung Mệnh' -> 'Lộc Mã giao trì'."""
    m = re.match(r"(?:khuynh hướng\s+)?cách\s+(.+)", text.strip(), re.I)
    if not m:
        return None
    body = m.group(1)
    for k, v in CACH_NAME_OVERRIDE.items():
        if body.startswith(k):
            return v
    name = re.split(r"\s*[(;:\[]|\s+ở\s+", body, maxsplit=1)[0].strip(" ,.")
    return name if len(name) >= CACH_MIN_LEN else None


def build_model(data: dict | None = None) -> dict:
    """Articles as plain data (also what the tests inspect)."""
    d = data or load()
    claims, gl = d["claims"], d["glossary"]
    tv = [r for r in d["rules"] if r["system"] == "tu_vi"]
    by_star: dict[str, list] = defaultdict(list)
    by_palace: dict[str, list] = defaultdict(list)
    cach: dict[str, dict] = {}
    for r in tv:
        st = statement(r, claims)
        if not st:
            continue
        named = stars_named(r)
        pals = palaces_of(r)
        for s in named:
            by_star[s].append({**st, "group": pals[0] if pals else "Khác"})
        lead = next((s for s in named if s in MAJOR), named[0] if named else "Điều kiện khác")
        for p in pals:
            by_palace[p].append({**st, "group": lead})
        if r["_pack"] == "pack_thuc_hanh_cach.json":
            nm = cach_name(claims.get(r["consequences"][0].get("claim", ""), ""))
            if nm:
                c = cach.setdefault(slug(nm), {"name": nm, "items": [], "stars": []})
                c["items"].append({**st, "group": pals[0] if pals else "Khác"})
                c["stars"] += [s for s in named if s not in c["stars"]]
    # verified rules elsewhere that are about the same cách: they name it ("cách Song Lộc"), or their condition contains every
    # condition of the TH rule (so they describe a special case of it, e.g. Toàn Thư on Song Lộc with Hóa Quyền as well)
    cach_rules = defaultdict(list)
    for r in tv:
        if r["_pack"] == "pack_thuc_hanh_cach.json":
            nm = cach_name(claims.get(r["consequences"][0].get("claim", ""), ""))
            if nm:
                cach_rules[slug(nm)].append(conjuncts(r["conditions"]))
    for r in tv:
        if r["_pack"] == "pack_thuc_hanh_cach.json":
            continue
        st = statement(r, claims)
        if not st:
            continue
        low, mine = (r["description"] + " " + st["text"]).lower(), conjuncts(r["conditions"])
        for k, c in cach.items():
            if "cách " + c["name"].lower() in low or any(sig <= mine for sig in cach_rules[k]):
                c.setdefault("related", []).append({**st, "group": (palaces_of(r) or ["Khác"])[0]})

    minor = gl.get("minor", {})
    stars = []
    for s in MAJOR + [m for m in minor if m not in MAJOR] + TU_HOA:
        items = _sort(by_star.get(s, []))
        if not items and s not in MAJOR:
            continue
        g = gl["stars"].get(s) or minor.get(s) or {}
        stars.append({"name": s, "slug": slug(s), "kind": "chính tinh" if s in MAJOR else ("Tứ Hóa" if s in TU_HOA else g.get("kind", "phụ tinh")),
                      "plain": g.get("plain", ""), "ex": g.get("ex", ""), "items": items, "dignity": dignity_rows(d["dignity"], s)})
    palaces = []
    for p in PALACES:
        g = gl["palaces"].get(p, {})
        palaces.append({"name": p, "slug": slug(p), "plain": g.get("plain", ""), "ask": g.get("ask", ""), "items": _sort(by_palace.get(p, []))})
    cachs = sorted(({**c, "slug": k, "items": _sort(c["items"]), "related": _sort(c.get("related", []))} for k, c in cach.items()),
                   key=lambda c: c["name"].lower())
    return {"stars": stars, "palaces": palaces, "cach": cachs, "sources": d["sources"], "rules": d["rules"], "draft": d["draft"],
            "dignity": d["dignity"], "glossary": gl}


def dignity_rows(kb: dict, star: str) -> list[dict]:
    rows = []
    for school, label in DIGNITY_SCHOOLS:
        cells = kb["resolved"].get(school, {}).get(star)
        if not cells:
            continue
        vals, locs = [], []
        for b in BRANCHES:
            c = cells.get(b) or {}
            ok = c.get("status") == "VERIFIED" and c.get("value")
            vals.append(c["value"] if ok else "")
            if ok and c.get("locator") and c["locator"] not in locs:
                locs.append(c["locator"])
        if any(vals):
            rows.append({"school": label, "values": vals, "locators": locs})
    return rows


# ---------------------------------------------------------------- html
NAV = [("/bai-viet/", "Bài viết"), ("/kinh-dich/", "Kinh Dịch"), ("/xem-ngay/", "Xem ngày"), ("/chiem-tinh/", "Chiêm tinh"), ("/hoi-dap/", "Hỏi đáp"), ("/gioi-thieu/", "Giới thiệu")]
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 600'%3E%3Ccircle cx='300' cy='300' r='280' fill='none' "
           "stroke='%23282923' stroke-width='28'/%3E%3Cpath d='M300 130L340 300L300 470L260 300Z' fill='%23A7432C'/%3E%3C/svg%3E")


def _ld(obj) -> str:
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>"


def shell(path: str, title: str, desc: str, body: str, *, crumbs: list[tuple[str, str]] = (), ld: list = (), og_type: str = "website",
          scripts: list[str] = (), styles: list[str] = ()) -> str:
    url = ORIGIN + path
    full = f"{title} | {SITE}" if SITE not in title else title
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="{h}"{cur if path.startswith(h) else ""}>{esc(t)}</a>' for h, t in NAV)
    crumb_html = ""
    lds = list(ld)
    if crumbs:
        trail = [("/", SITE)] + list(crumbs)
        crumb_html = '<nav class="crumbs" aria-label="Đường dẫn"><ol>' + "".join(
            f'<li><a href="{esc(h)}">{esc(t)}</a></li>' if i < len(trail) - 1 else f'<li aria-current="page">{esc(t)}</li>'
            for i, (h, t) in enumerate(trail)) + "</ol></nav>"
        lds.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": t, "item": ORIGIN + h} for i, (h, t) in enumerate(trail)]})
    script_tags = "".join(f'<script type="module" src="{s}"></script>' for s in ["/js/pwa.js", "/js/ref.js", "/js/feedback.js", "/js/ask.js", *scripts])
    return f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(full)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(url)}">
<meta property="og:site_name" content="{SITE}">
<meta property="og:locale" content="vi_VN">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(url)}">
<meta property="og:image" content="{ORIGIN}/icons/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#FAF6EF">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" href="{FAVICON}">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/app.css">
<link rel="stylesheet" href="/css/content.css">
{"".join(f'<link rel="stylesheet" href="{x}">' for x in styles)}
{"".join(_ld(x) for x in lds)}
</head>
<body class="cpage">
<a class="skip" href="#main">Bỏ qua điều hướng</a>
<header class="site-header stuck"><div class="wrap hdr">
<a class="brand" href="/" aria-label="{SITE}, trang chủ"><span class="brand-t"><b>{SITE}</b><small>Tử Vi · Bát Tự</small></span></a>
<nav class="nav cnav" aria-label="Điều hướng chính">{nav}</nav>
<a class="btn btn-sm hdr-cta" href="/#lap-la-so">Lập lá số</a>
</div></header>
<main id="main" class="wrap cmain">
{crumb_html}
{body}
</main>
<footer class="site-footer"><div class="wrap foot cfoot">
<div><b>{SITE}</b><p>Tử Vi · Bát Tự có thể truy vết.</p></div>
<p class="foot-note">Diễn giải theo hệ biểu tượng truyền thống, không phải dự báo hay chẩn đoán. Tử Vi và Bát Tự chưa được khoa học kiểm chứng là phương pháp dự báo.
<a class="link" href="/bai-viet/">Bài viết</a> · <a class="link" href="/kinh-dich/">Kinh Dịch</a> · <a class="link" href="/xem-ngay/">Xem ngày</a> · <a class="link" href="/hoi-dap/">Hỏi đáp</a> · <a class="link" href="/gioi-thieu/">Cách Thiên Bàn luận giải</a> · <a class="link" href="/library">Quy tắc và nguồn</a></p>
</div></footer>
{script_tags}
</body>
</html>
"""


def book_title(sources: dict, sid: str) -> str:
    s = sources.get(sid, {})
    return s.get("title", sid)


def _items_html(items: list[dict], sources: dict) -> str:
    return "<ul class=\"claims\">" + "".join(
        f'<li><span>{esc(it["text"])}</span>{_tags_html(it)} <cite>{esc(book_title(sources, it["source"]))}, {esc(it["page"])}</cite></li>' for it in items) + "</ul>"


def _tags_html(it: dict) -> str:
    return f' <small class="cond">{esc(" · ".join(it["tags"]))}</small>' if it.get("tags") else ""


def _groups_html(items: list[dict], sources: dict, order: list[str], label) -> str:
    groups: dict[str, list] = defaultdict(list)
    for it in items:
        groups[it["group"]].append(it)
    keys = [k for k in order if k in groups] + sorted(k for k in groups if k not in order)
    out = []
    for i, k in enumerate(keys):
        g = groups[k]
        out.append(f'<details class="cgroup"{" open" if i == 0 else ""}><summary><b>{esc(label(k))}</b><span class="n">{len(g)} nhận định</span></summary>'
                   f"{_items_html(g, sources)}</details>")
    return "".join(out)


def _sources_html(items: list[dict], sources: dict, extra: list[str] = ()) -> str:
    pages: dict[str, set] = defaultdict(set)
    for it in items:
        pages[it["source"]].add(it["page"])
    li = []
    for sid in sorted(pages, key=_book_key):
        s = sources.get(sid, {})
        pp = ", ".join(sorted((p.replace("tr. ", "") for p in pages[sid]), key=lambda p: (_page_key(p), p)))
        li.append(f'<li><b>{esc(s.get("title", sid))}</b>{" (" + esc(s["author"]) + ")" if s.get("author") else ""}: trang {esc(pp)}.</li>')
    li += [f"<li>{x}</li>" for x in extra]
    return ('<section class="csources" aria-labelledby="src-h"><h2 id="src-h">Nguồn của bài này</h2><ul>' + "".join(li) + "</ul>"
            '<p class="note">Số trang là trang ghi trong quy tắc của hệ thống (với Thực Hành, Khảo Luận và Toàn Thư, trang in trùng trang PDF). '
            'Các câu ở trên là lời diễn lại ngắn của Thiên Bàn, không phải trích nguyên văn. Xem toàn bộ quy tắc ở <a class="link" href="/library">Thư viện quy tắc và nguồn</a>.</p></section>')


READ_NOTE = ('<aside class="cnote"><b>Cách đọc bài này.</b> Mỗi dòng là điều một cuốn sách Tử Vi viết khi gặp điều kiện nêu trong ngoặc, '
             "được Thiên Bàn diễn lại ngắn gọn và ghi trang. Đó là khuynh hướng theo cách đọc truyền thống, không phải dự báo cho một người cụ thể: "
             "một lá số thật có nhiều yếu tố cùng lúc và nhiều câu có thể kéo ngược nhau. Tử Vi chưa được khoa học kiểm chứng là phương pháp dự báo.</aside>")
CTA = '<p class="ccta"><a class="btn" href="/#lap-la-so">Lập lá số để xem điều này trong lá số của bạn</a></p>'


def _article_ld(path: str, title: str, desc: str, items: list[dict], sources: dict) -> dict:
    books = sorted({it["source"] for it in items}, key=_book_key)
    org = {"@type": "Organization", "name": SITE, "url": ORIGIN + "/"}
    return {"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc, "inLanguage": "vi",
            "url": ORIGIN + path, "mainEntityOfPage": ORIGIN + path, "dateModified": CONTENT_DATE, "author": org, "publisher": org,
            "image": ORIGIN + "/icons/og.png",
            "citation": [{"@type": "Book", "name": sources.get(b, {}).get("title", b), **({"author": {"@type": "Person", "name": sources[b]["author"]}} if sources.get(b, {}).get("author") else {})} for b in books]}


def _clip(s: str, n: int = 155) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1].rsplit(" ", 1)[0] + "…"


def star_page(st: dict, m: dict) -> tuple[str, str]:
    path = f"/bai-viet/sao/{st['slug']}/"
    title = f"Sao {st['name']} trong Tử Vi: sách nói gì"
    n = len(st["items"])
    desc = _clip(f"Sao {st['name']} ({st['kind']}): {st['plain'] or 'ý nghĩa theo sách'} {n} nhận định từ Tử Vi Thực Hành, Khảo Luận, Toàn Thư, mỗi câu ghi trang.")
    dig = ""
    if st["dignity"]:
        rows = "".join(f"<tr><th scope=\"row\">{esc(r['school'])}</th>" + "".join(f"<td>{esc(v) or '·'}</td>" for v in r["values"]) + "</tr>" for r in st["dignity"])
        locs = "; ".join(f"{r['school']}: {', '.join(r['locators'])}" for r in st["dignity"] if r["locators"])
        dig = (f'<section aria-labelledby="dg-h"><h2 id="dg-h">Độ sáng theo cung</h2><p>Ba sách xếp độ sáng (miếu, vượng, đắc, lợi, bình, hãm) của sao {esc(st["name"])} '
               f'ở mười hai cung không hoàn toàn giống nhau. Ô "·" là sách không in hoặc hệ thống chưa đối chiếu được.</p>'
               f'<div class="tscroll"><table class="dtable"><thead><tr><th scope="col">Bảng</th>' + "".join(f'<th scope="col">{b}</th>' for b in BRANCHES) +
               f"</tr></thead><tbody>{rows}</tbody></table></div><p class=\"note\">Trang của bảng: {esc(locs.replace('TH p.', 'TH tr.').replace('TT p.', 'TT tr.').replace('KL p.', 'KL tr.'))}.</p></section>")
    intro = (f'<p class="lead">{esc(st["plain"])}</p><p class="note">Đoạn trên là giải thích phổ thông do Thiên Bàn soạn để người mới dễ hình dung, không phải lời sách.</p>'
             if st["plain"] else "")
    body_items = (f'<section aria-labelledby="cl-h"><h2 id="cl-h">Sách nói gì khi có {esc(st["name"])}</h2><p>{n} nhận định đã đối chiếu sách, xếp theo cung mà sao đóng.</p>'
                  + _groups_html(st["items"], m["sources"], PALACES, lambda k: f"Ở cung {k}" if k in PALACES else "Điều kiện khác") + "</section>") if n else \
        '<p class="note">Chưa có quy tắc đã đối chiếu sách nào nêu riêng sao này.</p>'
    dig_src = [f"Bảng độ sáng: {esc(r['school'])} ({esc(', '.join(r['locators']))})" for r in st["dignity"] if r["locators"]]
    body = (f'<article class="carticle"><p class="eyebrow">{esc(st["kind"])}</p><h1>Sao {esc(st["name"])}</h1>{intro}{READ_NOTE}{dig}{body_items}{CTA}'
            f'{_sources_html(st["items"], m["sources"], dig_src)}{_related(m, "sao", st["slug"])}</article>')
    return path, shell(path, title, desc, body, crumbs=[("/bai-viet/", "Bài viết"), ("/bai-viet/#sao", "Sao"), (path, st["name"])],
                       ld=[_article_ld(path, title, desc, st["items"], m["sources"])], og_type="article")


def palace_page(p: dict, m: dict) -> tuple[str, str]:
    path = f"/bai-viet/cung/{p['slug']}/"
    title = f"Cung {p['name']} trong Tử Vi: sách nói gì"
    n = len(p["items"])
    desc = _clip(f"Cung {p['name']}: {p['plain']} {n} nhận định từ sách Tử Vi về các sao ở cung {p['name']}, mỗi câu ghi trang.")
    star_order = MAJOR + [s["name"] for s in m["stars"] if s["name"] not in MAJOR]
    body = (f'<article class="carticle"><p class="eyebrow">Cung</p><h1>Cung {esc(p["name"])}</h1>'
            + (f'<p class="lead">{esc(p["plain"])}</p><p class="note">Đoạn trên là giải thích phổ thông do Thiên Bàn soạn, không phải lời sách.'
               + (f' Câu hỏi cung này trả lời: <i>{esc(p["ask"].replace("Hỏi: ", ""))}</i>' if p["ask"] else "") + "</p>" if p["plain"] else "")
            + READ_NOTE
            + (f'<section aria-labelledby="cl-h"><h2 id="cl-h">Sách nói gì về cung {esc(p["name"])}</h2><p>{n} nhận định đã đối chiếu sách, xếp theo sao chính có trong điều kiện.</p>'
               + _groups_html(p["items"], m["sources"], star_order, lambda k: k if k in star_order else "Điều kiện khác") + "</section>"
               if n else '<p class="note">Chưa có quy tắc đã đối chiếu sách nào cho cung này.</p>')
            + CTA + _sources_html(p["items"], m["sources"]) + _related(m, "cung", p["slug"]) + "</article>")
    return path, shell(path, title, desc, body, crumbs=[("/bai-viet/", "Bài viết"), ("/bai-viet/#cung", "Cung"), (path, p["name"])],
                       ld=[_article_ld(path, title, desc, p["items"], m["sources"])], og_type="article")


def cach_page(c: dict, m: dict) -> tuple[str, str]:
    path = f"/bai-viet/cach-cuc/{c['slug']}/"
    title = f"Cách {c['name']} trong Tử Vi"
    n = len(c["items"])
    n += len(c["related"])
    desc = _clip(f"Cách {c['name']} trong Tử Vi: điều kiện thành cách theo Tử Vi Thực Hành và điều các sách khác nói thêm, {n} nhận định có ghi trang.")
    links = ", ".join(f'<a class="link" href="/bai-viet/sao/{slug(s)}/">{esc(s)}</a>' for s in c["stars"] if any(x["name"] == s for x in m["stars"]))
    body = (f'<article class="carticle"><p class="eyebrow">Cách cục</p><h1>Cách {esc(c["name"])}</h1>'
            f'<p class="lead">Cách cục là một thế phối hợp sao được sách đặt tên. Bài này gom những gì sách đã đối chiếu nói về cách {esc(c["name"])}: '
            f'điều kiện thành cách nằm trong từng câu, trong ngoặc.</p>'
            + (f"<p>Sao liên quan: {links}.</p>" if links else "") + READ_NOTE
            + f'<section aria-labelledby="cl-h"><h2 id="cl-h">Sách nói gì</h2>'
            + _groups_html(c["items"], m["sources"], PALACES, lambda k: f"Ở cung {k}" if k in PALACES else "Điều kiện khác") + "</section>"
            + (f'<section aria-labelledby="rl-h"><h2 id="rl-h">Sách khác nói thêm</h2><p>Những quy tắc nêu đúng tên cách này, hoặc có điều kiện bao gồm '
               f'đủ điều kiện của cách và thêm điều kiện riêng.</p>{_items_html(c["related"], m["sources"])}</section>' if c["related"] else "")
            + _star_boxes(c["stars"], m)
            + '<p class="note">Bảng lá số của Thiên Bàn nhận ra cách cục theo điều kiện viết trong quy tắc; khi sách dùng chữ "gặp", "hội", hệ thống đọc là '
              'có trong tam phương tứ chính, và cách đọc đó được ghi kèm quy tắc.</p>'
            + CTA + _sources_html(c["items"] + c["related"], m["sources"]) + _related(m, "cach-cuc", c["slug"]) + "</article>")
    return path, shell(path, title, desc, body, crumbs=[("/bai-viet/", "Bài viết"), ("/bai-viet/#cach-cuc", "Cách cục"), (path, c["name"])],
                       ld=[_article_ld(path, title, desc, c["items"] + c["related"], m["sources"])], og_type="article")


def _star_boxes(names: list[str], m: dict) -> str:
    """Short glossary note for each star of the cách that has its own article."""
    known = {s["name"]: s for s in m["stars"]}
    boxes = [f'<li><a href="/bai-viet/sao/{known[n]["slug"]}/"><b>{esc(n)}</b></a> {esc(known[n]["plain"])}</li>'
             for n in names if n in known and known[n]["plain"]]
    return (f'<section aria-labelledby="sb-h"><h2 id="sb-h">Các sao trong cách</h2><ul class="plain">{"".join(boxes)}</ul>'
            '<p class="note">Giải thích phổ thông do Thiên Bàn soạn, không phải lời sách.</p></section>') if boxes else ""


def _related(m: dict, kind: str, current: str) -> str:
    pools = {"sao": [(f"/bai-viet/sao/{s['slug']}/", s["name"]) for s in m["stars"] if s["name"] in MAJOR],
             "cung": [(f"/bai-viet/cung/{p['slug']}/", p["name"]) for p in m["palaces"]],
             "cach-cuc": [(f"/bai-viet/cach-cuc/{c['slug']}/", c["name"]) for c in m["cach"]][:16]}
    head = {"sao": "Các chính tinh khác", "cung": "Các cung khác", "cach-cuc": "Cách cục khác"}[kind]
    links = [f'<a href="{h}">{esc(t)}</a>' for h, t in pools[kind] if not h.rstrip("/").endswith("/" + current)]
    return f'<nav class="crelated" aria-label="{head}"><h2>{head}</h2><p>{" ".join(links)}</p></nav>'


def index_page(m: dict) -> tuple[str, str]:
    path = "/bai-viet/"
    title = "Bài viết: ý nghĩa sao, cung và cách cục Tử Vi theo sách"
    n = sum(len(s["items"]) for s in m["stars"])
    desc = "Ý nghĩa 14 chính tinh, các phụ tinh, 12 cung và các cách cục Tử Vi, tổng hợp từ Tử Vi Thực Hành, Khảo Luận và Toàn Thư; mỗi nhận định ghi trang sách."
    card = lambda h, t, sub: f'<li><a href="{h}"><b>{esc(t)}</b><small>{esc(sub)}</small></a></li>'
    major = "".join(card(f"/bai-viet/sao/{s['slug']}/", s["name"], f"{len(s['items'])} nhận định") for s in m["stars"] if s["name"] in MAJOR)
    hoa = "".join(card(f"/bai-viet/sao/{s['slug']}/", s["name"], f"{len(s['items'])} nhận định") for s in m["stars"] if s["name"] in TU_HOA)
    minor = "".join(card(f"/bai-viet/sao/{s['slug']}/", s["name"], f"{len(s['items'])} nhận định") for s in m["stars"] if s["name"] not in MAJOR + TU_HOA)
    pal = "".join(card(f"/bai-viet/cung/{p['slug']}/", "Cung " + p["name"], f"{len(p['items'])} nhận định") for p in m["palaces"])
    cc = "".join(card(f"/bai-viet/cach-cuc/{c['slug']}/", c["name"], f"{len(c['items'])} nhận định") for c in m["cach"])
    body = (f'<p class="eyebrow">Bài viết</p><h1>Sao, cung và cách cục theo sách</h1>'
            f'<p class="lead">Mỗi bài gom những gì sách Tử Vi nói về một sao, một cung hoặc một cách cục, từ các quy tắc Thiên Bàn đã đối chiếu từng trang. '
            f'Không có câu nào do AI viết; mỗi câu ghi tên sách và trang.</p>{READ_NOTE}'
            f'<section id="sao"><h2>Chính tinh</h2><ul class="cards">{major}</ul><h2>Tứ Hóa</h2><ul class="cards">{hoa}</ul>'
            f'<h2>Phụ tinh</h2><ul class="cards cards-sm">{minor}</ul></section>'
            f'<section id="cung"><h2>Mười hai cung</h2><ul class="cards">{pal}</ul></section>'
            f'<section id="cach-cuc"><h2>Cách cục</h2><p class="note">Các cách có tên trong Tử Vi Thực Hành (tr. 72-74), cùng những câu ở sách khác nêu đúng tên cách đó.</p><ul class="cards cards-sm">{cc}</ul></section>')
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "description": desc, "url": ORIGIN + path, "inLanguage": "vi"}
    return path, shell(path, title, desc, body, crumbs=[(path, "Bài viết")], ld=[ld])


# ---------------------------------------------------------------- about / FAQ / calendar shell
def facts(m: dict) -> dict:
    by_src = Counter(r["sourceIds"][0] if r["sourceIds"] else "" for r in m["rules"])
    cells = Counter()
    for school, _ in DIGNITY_SCHOOLS:
        for star, row in m["dignity"]["resolved"].get(school, {}).items():
            cells[school] += sum(1 for c in row.values() if c.get("status") == "VERIFIED")
    return {"verified": len(m["rules"]), "draft": sum(m["draft"].values()), "by_src": by_src, "cells": cells,
            "articles": len(m["stars"]) + len(m["palaces"]) + len(m["cach"])}


def about_page(m: dict) -> tuple[str, str]:
    path = "/gioi-thieu/"
    f = facts(m)
    title = "Cách Thiên Bàn luận giải"
    desc = "Thiên Bàn lập lá số bằng thuật toán thiên văn và luận giải bằng quy tắc lấy từ sách Tử Vi, Bát Tự có ghi trang. Điều gì đã kiểm, điều gì chưa, và vì sao không dùng AI để bịa nhận định."
    src_rows = "".join(f"<tr><td>{esc(m['sources'].get(s, {}).get('title', s))}</td><td>{esc(m['sources'].get(s, {}).get('author', ''))}</td><td>{n}</td></tr>"
                       for s, n in f["by_src"].most_common() if s)
    body = f"""<article class="carticle">
<p class="eyebrow">Giới thiệu</p><h1>Cách Thiên Bàn luận giải</h1>
<p class="lead">Thiên Bàn làm hai việc tách biệt: <b>tính</b> lá số (vị trí sao, can chi, độ sáng) bằng thuật toán, rồi <b>đọc</b> lá số bằng các quy tắc chép từ sách, mỗi quy tắc ghi tên sách và trang. Trang này nói thật cách hai việc đó được làm, và chỗ nào còn chưa chắc.</p>

<h2>1. Lập lá số: tính toán, không đoán</h2>
<ul class="plain">
<li>Lịch âm tính từ thời điểm trăng mới và trung khí thiên văn (thư viện PyEphem, sxtwl), theo múi giờ Việt Nam UTC+7 (UTC+8 trước 1968). Bộ kiểm thử so lịch âm và tiết khí với bảng chuyển đổi của Đài Thiên văn Hồng Kông cho các năm 1901-2100 (khi chọn lịch Trung Quốc, UTC+8).</li>
<li>Cách an sao lấy theo Tử Vi Thực Hành và Tử Vi Khảo Luận; mỗi công thức có trang sách trong hồ sơ kiểm định của dự án.</li>
<li>Độ sáng sao có ba bảng, chép từ ảnh trang của ba sách, và bạn chọn bảng nào dùng: Thực Hành ({f['cells']['thuc_hanh']} ô đã đối chiếu), Toàn Thư ({f['cells']['toan_thu']} ô), Khảo Luận ({f['cells']['khao_luan']} ô). Ô sách không in thì để trống, không tự điền.</li>
<li>Đối chiếu độc lập hiện mới có <b>một</b> lá số chép tay từ một trang lá số phổ thông, khớp toàn bộ 12 cung, 14 chính tinh và khoảng một trăm phụ tinh. Một lá không đủ để nói là đúng tuyệt đối; thêm 35.120 lá ngẫu nhiên chỉ kiểm tính nhất quán (mỗi sao an đúng một lần, quan hệ giữa các sao đúng như sách), không chứng minh công thức.</li>
</ul>

<h2>2. Luận giải: quy tắc có trang sách</h2>
<p>Mỗi quy tắc là một điều kiện (ví dụ "cung Mệnh có Thiên Cơ ở thế miếu, vượng hoặc đắc") và một nhận định mà sách nêu cho điều kiện đó, được diễn lại ngắn bằng lời của Thiên Bàn. Hiện có <b>{f['verified']}</b> quy tắc đã đối chiếu với trang sách và <b>{f['draft']}</b> quy tắc còn là bản nháp (chưa đối chiếu, hoặc có cách hiểu riêng của hệ thống). Bài luận giải chỉ dùng quy tắc đã đối chiếu.</p>
<div class="tscroll"><table class="stable"><thead><tr><th>Sách</th><th>Tác giả</th><th>Quy tắc đã đối chiếu</th></tr></thead><tbody>{src_rows}</tbody></table></div>
<p>Bộ suy luận chạy hoàn toàn theo quy tắc: cùng ngày giờ sinh luôn ra cùng một bài. Nó xét điều kiện của từng quy tắc trên lá số, ghi lại vì sao quy tắc được áp dụng, cân những nhận định kéo ngược nhau, rồi xếp thành các chương. Bấm vào một nhận định trong bài luận giải để xem quy tắc và trang sách của nó.</p>

<h2>3. AI dùng ở đâu, và không dùng ở đâu</h2>
<ul class="plain">
<li><b>Bài luận giải chuẩn</b> (các chương Tử Vi, Bát Tự) không do AI viết. Mọi câu đến từ quy tắc nói trên.</li>
<li><b>Trợ lý hỏi đáp</b> và <b>luận giải sâu</b> (tính bằng xu) do một mô hình ngôn ngữ AI viết, dựa trên dữ kiện lá số và bài luận giải chuẩn. Mô hình được dặn không thêm sao, cung hay nhận định ngoài những gì có sẵn, nhưng AI vẫn có thể diễn đạt sai; khi phần trả lời khác bài luận giải chuẩn, hãy tin bài luận giải chuẩn.</li>
<li>Các bài viết ở mục <a class="link" href="/bai-viet/">Bài viết</a> được sinh tự động từ chính các quy tắc đã đối chiếu, không có đoạn nào do AI viết.</li>
</ul>

<h2>4. Điều đã kiểm và điều chưa kiểm</h2>
<div class="twocol">
<div><h3>Đã đối chiếu sách</h3><ul class="plain">
<li>Cách an 14 chính tinh và phần lớn phụ tinh, Tuần, Triệt, Tràng Sinh, đại hạn, tiểu hạn.</li>
<li>Bảng Tứ Hóa (Khảo Luận tr. 36).</li>
<li>Nguyệt hạn từng tháng (Thực Hành tr. 115).</li>
<li>Chín sao lưu sách có ghi (Khảo Luận tr. 41-42, Thực Hành tr. 114).</li>
<li>Các bảng quan hệ can chi của Bát Tự (八字真宗, các trang bảng).</li>
</ul></div>
<div><h3>Chưa đối chiếu hoặc còn tranh cãi</h3><ul class="plain">
<li>Một số sao lưu thông lệ (Khôi, Việt, Xương, Khúc, Đào Hoa, Hồng Loan, lưu Tứ Hóa) không có trong ba sách: chỉ hiện trên bảng với nét chấm, không đưa vào luận giải.</li>
<li>Tên cách cục do bảng lá số tự nhận diện theo vị trí sao được đánh dấu "chưa đối chiếu"; chỉ các cách có trong quy tắc đã đối chiếu mới vào bài luận giải.</li>
<li>Cân lượng (xưng cốt) và lai nhân cung: ba sách không in quy tắc, nên không làm.</li>
<li>Mốc đổi múi giờ lịch Việt Nam (1967 hay 1968) và lịch miền Nam trước 1976: các nguồn khác nhau.</li>
<li>Ngày hoàng đạo, sao ngày: chưa có sách nguồn (xem <a class="link" href="/xem-ngay/">Xem ngày</a>).</li>
</ul></div>
</div>

<h2>5. Điều Thiên Bàn không nói</h2>
<p>Tử Vi và Bát Tự là hệ biểu tượng truyền thống. Chúng chưa được khoa học kiểm chứng là phương pháp dự báo, và Thiên Bàn không nói lá số "chính xác" hay có "cơ sở khoa học". Phần tính toán có thể kiểm lại; phần ý nghĩa là cách đọc của sách, được trình bày kèm nguồn để bạn tự đánh giá. Với sức khỏe, pháp lý, tiền bạc và các quyết định lớn, hãy hỏi người có chuyên môn.</p>
<p class="ccta"><a class="btn" href="/#lap-la-so">Lập lá số</a> <a class="btn btn-ghost" href="/library">Xem thư viện quy tắc</a></p>
</article>"""
    ld = {"@context": "https://schema.org", "@type": "AboutPage", "name": title, "description": desc, "url": ORIGIN + path, "inLanguage": "vi"}
    return path, shell(path, title, desc, body, crumbs=[(path, "Giới thiệu")], ld=[ld])


FAQ = [
    ("Tôi không biết gì về Tử Vi, có xem được không?",
     "Được. Chỉ cần ngày, giờ, giới tính và nơi sinh. Bài luận giải viết bằng lời thường; thuật ngữ nào cũng có giải thích khi bạn chạm vào. "
     "Nếu muốn tìm hiểu thêm, mục Bài viết giải thích từng sao, từng cung theo sách."),
    ("Phần nào miễn phí?",
     "Lập lá số Tử Vi và Bát Tự, bảng lá số, bài luận giải chuẩn theo các chương, lưu lá số trên máy và tải PDF đều miễn phí, không cần tài khoản. "
     "Khi đăng nhập, bạn hỏi Bát Bát (chat AI) miễn phí 2 câu mỗi ngày; mỗi lần nạp xu có thêm 30 ngày chat, tới 30 câu mỗi ngày. "
     "Luận giải bằng AI và các câu hỏi thêm dùng xu."),
    ("Luận giải có đáng tin không?",
     "Phần tính toán (lịch âm, vị trí sao, độ sáng) được kiểm bằng bảng lịch độc lập và trang sách, nhưng đối chiếu với lá số thật mới có ít mẫu. "
     "Phần ý nghĩa là cách đọc của sách Tử Vi, mỗi câu ghi trang để bạn tự kiểm. Tử Vi chưa được khoa học kiểm chứng là phương pháp dự báo; "
     "hãy xem luận giải như một góc nhìn để suy ngẫm, không phải lời tiên đoán."),
    ("Tôi không rõ giờ sinh thì sao?",
     "Đánh dấu ô \"Tôi không rõ giờ sinh\". Thiên Bàn lập lá số cho cả mười hai giờ và chỉ ra điều gì giữ nguyên (ba trụ đầu của Bát Tự, nhiều sao theo năm và tháng) "
     "và điều gì đổi theo giờ (cung Mệnh, cung Thân, Cục). Nếu nhớ khoảng giờ, bạn có thể so vài giờ gần nhau."),
    ("Tôi nhập sai ngày sinh, sửa thế nào?",
     "Bấm \"Lập lá số khác\" và nhập lại; lá số được tính mới mỗi lần. Lá số đã lưu thì xóa ở danh sách \"Lá số bạn đã lưu\" rồi lưu bản đúng. "
     "Nếu bạn chỉ biết ngày âm lịch, chọn \"Âm lịch\" ở ô ngày sinh, hệ thống tự đổi sang dương lịch."),
    ("Dữ liệu của tôi được giữ thế nào?",
     "Ngày giờ sinh được xử lý tức thời để lập lá số và không được lưu, trừ khi bạn bấm lưu. Lá số đã lưu nằm trong trình duyệt của bạn; "
     "khi đăng nhập Google, lá số đó được đồng bộ vào tài khoản. Khi bạn chat với Bát Bát hoặc dùng luận giải bằng AI, dữ kiện lá số và câu hỏi được gửi tới Anthropic (mô hình Claude) để soạn câu trả lời; "
     "tin nhắn chat không được lưu trên máy chủ Thiên Bàn. "
     "Thống kê truy cập chỉ đếm tổng số, không gắn với người hay ngày sinh. Muốn xóa tài khoản, hãy nhắn qua nút Góp ý."),
    ("Thiên Bàn có dùng AI để viết luận giải không?",
     "Bài luận giải chuẩn thì không: mọi câu đến từ quy tắc lấy từ sách có ghi trang. Chỉ Bát Bát (chat) và luận giải bằng AI dùng mô hình AI, và hai phần đó được ghi rõ."),
    ("Vì sao Xem ngày không có ngày hoàng đạo?",
     "Ngày hoàng đạo, sao tốt xấu của ngày lấy từ sách lịch pháp như Ngọc Hạp Thông Thư, mà Thiên Bàn chưa có trong kho nguồn. "
     "Trang Xem ngày chỉ hiển thị phần tính được: âm lịch, can chi, tiết khí và ngày xung với tuổi."),
]


def faq_page() -> tuple[str, str]:
    path = "/hoi-dap/"
    title = "Hỏi đáp về Thiên Bàn"
    desc = "Không biết Tử Vi có xem được không, phần nào miễn phí, luận giải đáng tin đến đâu, không rõ giờ sinh, sửa ngày sinh và bảo mật dữ liệu."
    qa = "".join(f'<details class="faq"{" open" if i == 0 else ""}><summary><h2>{esc(q)}</h2></summary><p>{esc(a)}</p></details>' for i, (q, a) in enumerate(FAQ))
    body = f'<article class="carticle"><p class="eyebrow">Hỏi đáp</p><h1>Câu hỏi thường gặp</h1>{qa}<p class="note">Câu hỏi khác? Bấm nút Góp ý ở góc màn hình.</p></article>'
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    return path, shell(path, title, desc, body, crumbs=[(path, "Hỏi đáp")], ld=[ld])


def calendar_page() -> tuple[str, str]:
    path = "/xem-ngay/"
    title = "Xem ngày: lịch âm dương, can chi, tiết khí"
    desc = "Lịch tháng với ngày dương lịch và âm lịch (lịch Việt Nam), can chi ngày tháng năm, tiết khí và ngày xung với tuổi của bạn."
    body = f"""<article class="carticle cal-page">
<p class="eyebrow">Xem ngày</p><h1>Lịch âm dương và can chi</h1>
<p class="lead">Lịch tháng theo lịch Việt Nam: ngày âm, can chi của ngày, tháng, năm, tiết khí, và những ngày có địa chi xung với tuổi của bạn.</p>
<form class="cal-ctl" id="cal-ctl" onsubmit="return false">
<button type="button" class="btn btn-ghost btn-sm" id="cal-prev" aria-label="Tháng trước">‹</button>
<label class="fld"><span>Tháng</span><select id="cal-m"></select></label>
<label class="fld"><span>Năm</span><input id="cal-y" type="number" inputmode="numeric" min="1901" max="2099"></label>
<button type="button" class="btn btn-ghost btn-sm" id="cal-next" aria-label="Tháng sau">›</button>
<button type="button" class="btn btn-ghost btn-sm" id="cal-today">Hôm nay</button>
<label class="fld"><span>Tuổi (năm sinh âm lịch)</span><input id="cal-birth" type="number" inputmode="numeric" min="1901" max="2099" placeholder="vd. 1990"></label>
</form>
<p class="note" id="cal-tuoi" aria-live="polite"></p>
<div id="cal-grid" class="cal-grid" aria-live="polite"><p class="note">Đang tải lịch…</p></div>
<section class="cal-detail" id="cal-detail" aria-live="polite"></section>
<aside class="cnote"><b>Phần không có ở đây.</b> Ngày hoàng đạo hay hắc đạo, sao tốt xấu của ngày, giờ hoàng đạo và mọi điểm "tốt xấu" theo phần trăm đều lấy từ sách lịch pháp (Ngọc Hạp Thông Thư, Hiệp Kỷ Biện Phương Thư). Thiên Bàn chưa có các sách này trong kho nguồn nên không hiển thị, thay vì tự đặt ra.</aside>
<section><h2>Các con số được tính thế nào</h2><ul class="plain">
<li><b>Âm lịch</b>: tháng bắt đầu vào ngày có trăng mới, tháng chứa Đông Chí là tháng 11, năm có 13 tháng thì tháng đầu tiên không chứa trung khí là tháng nhuận. Lịch Việt Nam tính theo múi giờ UTC+7 (UTC+8 trước 1968), nên đôi khi lệch một ngày hoặc một tháng so với lịch Trung Quốc.</li>
<li><b>Can chi ngày</b> theo chu kỳ 60 ngày liên tục; <b>can chi tháng âm</b> theo ngũ hổ độn từ can của năm âm lịch (tháng Giêng là tháng Dần). Tháng nhuận không được gán can chi vì Thiên Bàn chưa có nguồn cho quy ước đó.</li>
<li><b>Trụ năm, trụ tháng Bát Tự</b> đổi ở thời điểm tiết khí (Lập Xuân, Kinh Trập…), không đổi vào mùng một Tết. Ngày có tiết ghi giờ đổi trụ.</li>
<li><b>Ngày xung tuổi</b>: địa chi của ngày đối xung với địa chi năm sinh (Tý-Ngọ, Sửu-Mùi, Dần-Thân, Mão-Dậu, Thìn-Tuất, Tỵ-Hợi), theo bảng lục xung 八字真宗 tr. 19-20 mà lá số cũng dùng. Đó chỉ là quan hệ giữa hai chữ, không phải lời phán ngày xấu.</li>
<li>Năm sinh tính theo âm lịch: người sinh trước Tết thuộc năm âm lịch trước.</li>
</ul></section>
</article>"""
    ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Xem ngày " + SITE, "applicationCategory": "LifestyleApplication",
          "operatingSystem": "Web", "url": ORIGIN + path, "inLanguage": "vi", "description": desc, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "VND"}}
    return path, shell(path, title, desc, body, crumbs=[(path, "Xem ngày")], ld=[ld], scripts=["/js/xem_ngay.js"])


def kinh_dich_page() -> tuple[str, str]:
    """Gieo quẻ Kinh Dịch and Mai Hoa Dịch Số: a static shell, js/kinh_dich.js draws everything from /api/kinh-dich/* and /api/mai-hoa/*."""
    path = "/kinh-dich/"
    title = "Kinh Dịch: gieo quẻ và lập quẻ Mai Hoa"
    desc = ("Gieo ba đồng tiền sáu lần hoặc lập quẻ Mai Hoa theo giờ, theo số; xem quẻ chủ, quẻ biến, quẻ hỗ, lời kinh, lời bàn của Trình Di, "
            "Chu Hy và phần diễn giải, mỗi câu dẫn về chỗ nó dựa vào.")
    topics = [("", "Chung"), ("su_nghiep", "Sự nghiệp"), ("tai_chinh", "Tài chính"), ("kinh_doanh", "Kinh doanh"), ("hoc_tap", "Học tập"),
              ("tinh_cam", "Tình cảm"), ("gia_dinh", "Gia đình"), ("lua_chon", "Lựa chọn")]
    chips = "".join(f'<label><input type="radio" name="kd-topic" value="{v}"{" checked" if not v else ""}><span>{esc(t)}</span></label>' for v, t in topics)
    body = f"""<article class="carticle kd-page" id="kd">
<p class="eyebrow">Kinh Dịch</p><h1>Gieo quẻ, lập quẻ</h1>
<p class="lead">Hỏi một việc cụ thể, gieo ba đồng tiền sáu lần, hoặc lập quẻ Mai Hoa theo giờ và theo số. Lời đọc đi từ kinh văn và lời bàn của
Trình Di, Chu Hy, qua bản dịch Ngô Tất Tố, đến phần diễn giải cho hoàn cảnh hôm nay, tách bạch từng lớp.</p>
<div class="seg seg-wide kd-mode" role="tablist" aria-label="Cách lập quẻ">
<button type="button" role="tab" data-mode="gieo" aria-pressed="true">Gieo quẻ Kinh Dịch</button>
<button type="button" role="tab" data-mode="mai-hoa" aria-pressed="false">Lập quẻ Mai Hoa</button>
</div>

<section class="kd-ask" id="kd-ask">
<label class="fld"><span>Điều bạn muốn hỏi</span><textarea id="kd-q" rows="2" maxlength="300" placeholder="vd. Có nên nhận lời mời làm việc ở công ty mới không?"></textarea></label>
<fieldset class="fld"><legend>Chủ đề</legend><div class="kd-chips" role="radiogroup">{chips}</div></fieldset>
<p class="note small">Câu hỏi chỉ lưu trên máy của bạn, không gửi đi.</p>
</section>

<section class="kd-stage" id="kd-gieo" data-stage="gieo">
<div class="kd-cast">
<div class="kd-coins" id="kd-coins" aria-hidden="true"><span class="coin"></span><span class="coin"></span><span class="coin"></span></div>
<div class="kd-build" id="kd-build" aria-live="polite"></div>
</div>
<div class="kd-actions">
<button type="button" class="btn" id="kd-toss">Gieo lần 1 / 6</button>
<button type="button" class="btn btn-ghost btn-sm" id="kd-reset" hidden>Gieo lại</button>
</div>
<details class="kd-manual"><summary>Đã có quẻ? Nhập từng hào</summary>
<p class="note small">Chọn từ hào Đầu (dưới cùng) lên hào Trên. 7 và 8 là hào tĩnh, 9 và 6 là hào động.</p>
<div class="kd-manual-lines" id="kd-manual-lines"></div>
<button type="button" class="btn btn-sm" id="kd-manual-go">Xem quẻ này</button>
</details>
</section>

<section class="kd-stage" id="kd-maihoa" data-stage="mai-hoa" hidden>
<div class="kd-mh-form">
<label class="fld"><span>Cách lập</span><span class="sel"><select id="mh-method">
<option value="thoi_gian">Theo năm, tháng, ngày, giờ</option>
<option value="vat_so">Theo số vật đếm được</option>
<option value="thanh_am">Theo số tiếng nghe được</option>
<option value="chu">Theo số chữ (từ 11 chữ)</option>
<option value="truong_xich">Theo trượng, thước</option>
<option value="xich_thon">Theo thước, tấc</option>
<option value="vat_phuong">Theo vật và hướng (Hậu thiên)</option>
</select></span></label>
<label class="fld"><span>Thời điểm lập quẻ</span><input id="mh-moment" type="datetime-local"></label>
<div id="mh-fields"></div>
<button type="button" class="btn" id="mh-go">Lập quẻ</button>
</div>
</section>

<section class="kd-result" id="kd-result" hidden aria-live="polite"></section>

<aside class="cnote"><b>Đọc lời quẻ thế nào cho đúng.</b> Lời quẻ là hệ biểu tượng cổ để suy ngẫm, không phải lời báo trước điều chắc chắn xảy ra.
Phần kinh văn và lời bàn của Trình Di, Chu Hy được giữ nguyên theo bản dịch Ngô Tất Tố; phần diễn giải hiện đại và lời khuyên là của Thiên Bàn,
đang ở dạng bản nháp, luôn ghi rõ dựa vào câu nào của sách.</aside>
</article>
<div class="kd-sheet" id="kd-sheet" role="dialog" aria-modal="true" aria-labelledby="kd-sheet-h" hidden><div class="kd-sheet-in" tabindex="-1"></div></div>"""
    ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Kinh Dịch " + SITE, "applicationCategory": "LifestyleApplication",
          "operatingSystem": "Web", "url": ORIGIN + path, "inLanguage": "vi", "description": desc, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "VND"}}
    return path, shell(path, title, desc, body, crumbs=[(path, "Kinh Dịch")], ld=[ld], scripts=["/js/kinh_dich.js"], styles=["/css/iching.css"])


# ---------------------------------------------------------------- whole site
def render(m: dict | None = None) -> dict[str, str]:
    """{file path relative to engine/web: content}."""
    m = m or build_model()
    pages = [index_page(m), about_page(m), faq_page(), calendar_page(), kinh_dich_page()]
    pages += [star_page(s, m) for s in m["stars"]] + [palace_page(p, m) for p in m["palaces"]] + [cach_page(c, m) for c in m["cach"]]
    out = {path.strip("/") + "/index.html": doc for path, doc in pages}
    urls = ["/", "/library"] + [p for p, _ in pages]
    out["sitemap.xml"] = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                          + "".join(f"<url><loc>{esc(ORIGIN + u)}</loc><lastmod>{CONTENT_DATE}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    out["robots.txt"] = f"User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /admin\n\nSitemap: {ORIGIN}/sitemap.xml\n"
    return out


GENERATED_DIRS = ["bai-viet", "gioi-thieu", "hoi-dap", "xem-ngay", "kinh-dich"]


def write(out: dict[str, str], web: Path = WEB) -> int:
    import shutil
    for d in GENERATED_DIRS:                 # a renamed article must not leave its old page behind
        shutil.rmtree(web / d, ignore_errors=True)
    for rel, doc in out.items():
        p = web / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(doc, "utf-8")
    return len(out)
