"""Static article system: every statement comes from a verified rule with a book page, pages carry SEO metadata, and the committed
pages are exactly what the generator makes (run tools/build_site.py after changing rule packs, claims or the glossary)."""
import json
import re
import struct
from pathlib import Path

import pytest

from tvbt import icons, sitegen as sg

WEB = sg.WEB


@pytest.fixture(scope="module")
def model():
    return sg.build_model()


@pytest.fixture(scope="module")
def out(model):
    return sg.render(model)


def test_committed_pages_are_up_to_date(out):
    stale = [rel for rel, doc in out.items() if not (WEB / rel).exists() or (WEB / rel).read_text("utf-8") != doc]
    assert not stale, f"run tools/build_site.py: {stale[:5]}"
    extra = [str(p.relative_to(WEB)) for d in sg.GENERATED_DIRS for p in (WEB / d).rglob("*") if p.is_file() and str(p.relative_to(WEB)) not in out]
    assert not extra, f"pages no longer generated: {extra[:5]}"


def test_icons_are_up_to_date(tmp_path):
    icons.write(tmp_path)
    for rel in list(icons.ICONS) + ["icons/og.png"]:
        assert (tmp_path / rel).read_bytes() == (WEB / rel).read_bytes(), rel
    png = (WEB / "icons/icon-512.png").read_bytes()
    assert png[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", png[16:24]) == (512, 512)


def test_every_statement_is_a_verified_rule_with_a_page(model):
    verified = {r["id"]: r for r in model["rules"]}
    items = [it for kind in ("stars", "palaces", "cach") for a in model[kind] for it in a["items"] + a.get("related", [])]
    assert len(items) > 1000
    for it in items:
        r = verified[it["id"]]                                    # KeyError = a draft rule leaked into an article
        assert r["reviewStatus"] == "verified" and r["system"] == "tu_vi"
        assert it["source"] in model["sources"] and it["source"] in r["sourceIds"]
        assert re.fullmatch(r"tr\. \d+(-\d+)?(, \d+(-\d+)?)*", it["page"]), it


def test_all_major_stars_and_palaces_have_articles(model):
    names = {s["name"] for s in model["stars"]}
    assert set(sg.MAJOR) <= names and set(sg.TU_HOA) <= names
    assert [p["name"] for p in model["palaces"]] == sg.PALACES
    assert all(s["items"] for s in model["stars"] if s["name"] in sg.MAJOR)
    assert all(s["dignity"] for s in model["stars"] if s["name"] in sg.MAJOR)
    assert len(model["cach"]) >= 25
    slugs = [s["slug"] for s in model["stars"]] + [p["slug"] for p in model["palaces"]] + [c["slug"] for c in model["cach"]]
    assert len(set(slugs)) == len(slugs) and all(re.fullmatch(r"[a-z0-9-]+", x) for x in slugs)


def test_cach_names_and_slugs():
    assert sg.cach_name("khuynh hướng cách Lộc Mã giao trì (Lộc và Mã đồng cung) ở cung Tài Bạch") == "Lộc Mã giao trì"
    assert sg.cach_name("cách Tử Phủ đồng cung ở Mệnh") == "Tử Phủ đồng cung"
    assert sg.cach_name("cách Phá Quân ở Mão hoặc Dậu (chỉ ở hai cung này)") == "Phá Quân ở Mão Dậu"
    assert sg.cach_name("giờ sinh thuận lý") is None
    assert sg.slug("Đà La") == "da-la" and sg.slug("Phu Thê") == "phu-the" and sg.slug("Hóa Kỵ") == "hoa-ky"


def test_statement_uses_the_limit_phrase_and_adds_missing_conditions(model):
    claims = sg.load()["claims"]
    rule = {"id": "X", "system": "tu_vi", "description": "demo [TH p.93]", "sourceIds": ["SRC_THUC_HANH"],
            "conditions": {"all": [{"fact": "palace.name", "value": "Mệnh"}, {"fact": "chart.gender", "value": "nữ"},
                                   {"fact": "palace.branch", "operator": "in", "value": ["Thìn", "Tuất"]}]},
            "consequences": [{"kind": "finding", "claim": "tu_phu_phuc_loc", "effect": "limit"}]}
    st = sg.statement(rule, claims)
    assert st["text"].lower().startswith(claims["limit:tu_phu_phuc_loc"][:20].lower())
    assert st["page"] == "tr. 93" and st["tags"] == ["nữ mệnh", "cung ở Thìn, Tuất"]
    # a condition under 'not' never makes the rule "about" that star
    neg = {"conditions": {"all": [{"fact": "palace.own_stars", "operator": "contains", "value": "Tử Vi"},
                                  {"not": {"fact": "palace.tam_phuong_stars", "operator": "contains", "value": "Kình Dương"}}]}}
    assert sg.stars_named(neg) == ["Tử Vi"]


def _head(doc: str) -> str:
    return doc.split("</head>")[0]


def test_pages_have_seo_metadata_and_sources(out):
    from tvbt.sitenav import HAND_PAGES        # hand-written pages: only their header comes from the generator
    pages = {k: v for k, v in out.items() if k.endswith(".html") and k not in HAND_PAGES}
    assert len(pages) >= 70
    for rel, doc in pages.items():
        h = _head(doc)
        path = "/" + rel[: -len("index.html")]
        assert re.search(r"<title>[^<]{10,}</title>", h), rel
        assert re.search(r'<meta name="description" content="[^"]{40,}">', h), rel
        assert f'<link rel="canonical" href="{sg.ORIGIN}{path}">' in h, rel
        assert 'property="og:title"' in h and 'property="og:image"' in h and 'rel="manifest"' in h, rel
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h):
            json.loads(block)
        assert "Altuvi" not in doc and "altuvi" not in doc.lower()
    for kind in ("sao", "cung", "cach-cuc"):
        for rel in (k for k in pages if k.startswith(f"bai-viet/{kind}/")):
            doc = pages[rel]
            assert "Nguồn của bài này" in doc and "chưa được khoa học kiểm chứng" in doc, rel
            ld = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', doc)]
            art = next(x for x in ld if x["@type"] == "Article")
            assert art["citation"] and all(c["@type"] == "Book" for c in art["citation"]), rel
            assert any(x["@type"] == "BreadcrumbList" for x in ld)


def test_faq_and_about_and_calendar_pages(out):
    faq = out["hoi-dap/index.html"]
    ld = next(json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', faq) if '"FAQPage"' in b)
    assert len(ld["mainEntity"]) == len(sg.FAQ) >= 6
    topics = " ".join(q for q, _ in sg.FAQ).lower()
    for t in ("không biết", "miễn phí", "tin", "giờ sinh", "sửa", "dữ liệu"):
        assert t in topics, t
    about = out["gioi-thieu/index.html"]
    assert "không do mô hình ngôn ngữ viết" in about and "do một mô hình ngôn ngữ viết" in about   # honest about where a model is and is not used
    assert "suy luận sâu" in about and "đối chiếu sách" in about and not re.search(r"\bAI\b", about + faq)   # owner 2026-10-25: never "AI"
    assert "chưa được khoa học kiểm chứng" in about
    cal = out["xem-ngay/index.html"]
    assert "Ngọc Hạp Thông Thư" in cal and "/js/xem_ngay.js" in cal


def test_sitemap_and_robots(out):
    sm = out["sitemap.xml"]
    locs = re.findall(r"<loc>([^<]+)</loc>", sm)
    pages = ["/" + k[: -len("index.html")] for k in out if k.endswith("index.html")]
    assert set(sg.ORIGIN + p for p in pages) <= set(locs) and sg.ORIGIN + "/" in locs
    assert len(locs) == len(set(locs))
    assert f"Sitemap: {sg.ORIGIN}/sitemap.xml" in out["robots.txt"] and "Disallow: /api/" in out["robots.txt"]


def test_manifest_is_installable():
    m = json.loads((WEB / "manifest.webmanifest").read_text("utf-8"))
    assert m["display"] == "standalone" and m["start_url"].startswith("/")
    sizes = {i["sizes"] for i in m["icons"]}
    assert {"192x192", "512x512"} <= sizes and any(i.get("purpose") == "maskable" for i in m["icons"])
    for i in m["icons"]:
        assert (WEB / i["src"].lstrip("/")).exists()
    sw = (WEB / "sw.js").read_text("utf-8")
    assert "addEventListener('fetch'" in sw and "/api/" in sw


def test_every_page_has_the_same_header(out):
    """One header everywhere (tvbt/sitenav.py): the same nav items in the same order, so the bar does not jump between pages; only
    aria-current differs, and it marks the page itself."""
    from tvbt import sitenav
    pages = {rel: doc for rel, doc in out.items() if rel.endswith(".html")}
    assert set(sitenav.HAND_PAGES) <= set(pages) and len(pages) > 100
    want = [(h, t) for _k, h, t, *_ in sitenav.ITEMS]
    current = re.compile(r' aria-current="page"')
    block = re.compile(r'<script>/\*nav-boot\*/.*?<script type="module" src="/js/nav\.js"></script>', re.S)
    canonical = current.sub("", block.search(out["bai-viet/index.html"]).group(0))
    for rel, doc in pages.items():
        assert sitenav.nav_list(doc) == want, rel
        assert doc.count('class="site-header') == 1, rel
        assert current.sub("", block.search(doc).group(0)) == canonical, rel
    assert 'data-k="bai-viet" aria-current="page"' in out["bai-viet/sao/tu-vi/index.html"]
    assert "Trang chủ" not in canonical and "aria-current" not in block.search(out["index.html"]).group(0)   # no home item (owner, 2026-10-25)
    assert "aria-current" not in block.search(out["privacy.html"]).group(0)
    assert not re.search(r"\bAI\b", canonical)
