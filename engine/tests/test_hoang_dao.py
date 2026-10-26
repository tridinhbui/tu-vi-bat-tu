"""Cung hoàng đạo (Western sun sign, tvbt/hoang_dao.py): the boundaries are the trung khí instants, they agree with an independent PyEphem
computation, the birth instant goes through calendar_core.normalize (historical zones), the API block, and the readings scaffolding
(no reading without a cited page; the word 'AI' and a bare 'cung' never appear in the new pages)."""
import datetime as dt
import json
import math
import re
import sys
from pathlib import Path

import ephem
import pytest
from fastapi.testclient import TestClient

from tvbt import astro, hoang_dao as hd, sitegen
from tvbt.api import app
from tvbt.calendar_core import BirthInput, normalize

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "engine" / "web"
sys.path.insert(0, str(ROOT / "tools"))
UTC = dt.timezone.utc
ICT = dt.timezone(dt.timedelta(hours=7))


def _ephem_lon(jd: float) -> float:
    """Apparent geocentric ecliptic longitude of the Sun (true equinox of date), degrees, from PyEphem."""
    d = ephem.Date(jd - 2415020.0)
    s = ephem.Sun()
    s.compute(d, epoch=d)
    return math.degrees(ephem.Ecliptic(ephem.Equatorial(s.g_ra, s.g_dec, epoch=d), epoch=d).lon)


def _ephem_crossing(target: float, near_jd: float) -> float:
    """UTC JD when PyEphem's Sun reaches `target` degrees, searched within two days of near_jd (bisection to ~0.01 s)."""
    a, b = near_jd - 2, near_jd + 2
    f = lambda j: ((_ephem_lon(j) - target + 180) % 360) - 180
    assert f(a) < 0 < f(b)
    for _ in range(45):
        m = (a + b) / 2
        a, b = (m, b) if f(m) < 0 else (a, m)
    return (a + b) / 2


def test_signs_and_glyphs():
    assert [s[1] for s in hd.SIGNS] == ["Bạch Dương", "Kim Ngưu", "Song Tử", "Cự Giải", "Sư Tử", "Xử Nữ", "Thiên Bình", "Bọ Cạp", "Nhân Mã",
                                         "Ma Kết", "Bảo Bình", "Song Ngư"]
    assert hd.sign_info(7)["label"] == "Bọ Cạp (Thiên Yết)"
    assert set(hd.GLYPHS) == {s[0] for s in hd.SIGNS}
    js = (WEB / "js" / "hoangdao.js").read_text("utf-8")
    js_glyphs = dict(re.findall(r'^\s*"([a-z-]+)": "([^"]+)",$', js, re.M))
    assert js_glyphs == hd.GLYPHS                      # the page and the card draw the same glyphs
    assert all(re.fullmatch(r"[MmLlHhVvCcSsAaZz0-9 .,\-]+", p) for p in hd.GLYPHS.values())


def test_term_to_sign_mapping():
    # sxtwl jqIndex: 0 Đông Chí (270°) = Ma Kết, 2 Đại Hàn = Bảo Bình, 4 Vũ Thủy = Song Ngư, 6 Xuân Phân = Bạch Dương, 12 Hạ Chí = Cự Giải
    assert [hd.SIGNS[hd.sign_index_of_term(j)][1] for j in (0, 2, 4, 6, 12, 18)] == ["Ma Kết", "Bảo Bình", "Song Ngư", "Bạch Dương", "Cự Giải", "Thiên Bình"]


@pytest.mark.parametrize("year", [1900, 1925, 1950, 1975, 1990, 2000, 2024, 2049])
def test_boundaries_are_the_trung_khi_instants(year):
    zhong = {round(jd, 9): jq for jq, jd in astro.all_terms_around(year) if jq % 2 == 0}
    ing = hd.ingresses(year)
    assert len(ing) >= 30 and all(b[1] > a[1] for a, b in zip(ing, ing[1:]))
    for i, jd, jq in ing:
        assert zhong[round(jd, 9)] == jq and hd.sign_index_of_term(jq) == i
    for a, b in zip(ing, ing[1:]):
        assert b[0] == (a[0] + 1) % 12                 # the signs follow one another, none skipped


@pytest.mark.parametrize("year", [1900, 1913, 1938, 1959, 1968, 1976, 1999, 2012, 2031, 2049])
def test_agrees_with_independent_pyephem_within_two_minutes(year):
    worst = 0.0
    for jq, jd in astro.solar_terms(year):
        if jq % 2:
            continue
        target = 30 * hd.sign_index_of_term(jq)
        worst = max(worst, abs(_ephem_crossing(target, jd) - jd) * 1440)
    assert worst < 2.0, f"{year}: {worst:.2f} min"


def _at(t: dt.datetime) -> dict:
    return hd.sun_sign_at(t, ICT)


def test_just_before_and_just_after_an_ingress():
    i, jd, _ = next(x for x in hd.ingresses(2024) if x[2] == 6 and astro.jd_to_utc(x[1]).year == 2024)   # Xuân Phân 2024
    t = astro.jd_to_utc(jd)
    assert t.strftime("%Y-%m-%d %H:%M") == "2024-03-20 03:06"
    before, after = _at(t - dt.timedelta(minutes=1)), _at(t + dt.timedelta(minutes=1))
    assert before["sun_sign"]["name"] == "Song Ngư" and after["sun_sign"]["name"] == "Bạch Dương"
    assert before["near_cusp"] and after["near_cusp"] and before["cusp_hours"] == after["cusp_hours"] == 0.0
    assert before["next_ingress"]["sign"] == "Bạch Dương" and after["ingress"]["sign"] == "Bạch Dương"
    assert after["ingress"]["text"] == "10:06 ngày 20/03/2024" and after["ingress"]["term"] == "Xuân Phân"
    # one conclusion only, with the exact ingress time
    assert "sinh sát ranh giới" in before["note"].lower() and "vẫn là Song Ngư" in before["note"] and "10:06:" in before["note"]
    assert "nên cung hoàng đạo là Bạch Dương" in after["note"] and " hoặc " not in after["note"]
    mid = _at(t + dt.timedelta(days=15))
    assert not mid["near_cusp"] and mid["note"] is None and mid["sun_sign"]["name"] == "Bạch Dương"
    edge = _at(t + dt.timedelta(hours=23, minutes=50))
    assert edge["near_cusp"] and _at(t + dt.timedelta(hours=24, minutes=10))["note"] is None


def test_birth_through_normalize_south_plus_eight_era():
    # Sài Gòn, 1965: Asia/Ho_Chi_Minh is UTC+8 then. Đông Chí 1964 fell at 19:49 UTC on 21/12 = 03:49 on 22/12 in UTC+8.
    nb = normalize(BirthInput(1964, 12, 22, 3, 30, "Asia/Ho_Chi_Minh", "male"))
    w = hd.sun_sign(nb)
    assert nb.utc.hour == 19 and nb.utc.day == 21                  # 03:30 at UTC+8, not UTC+7
    assert w["sun_sign"]["name"] == "Nhân Mã" and w["next_ingress"]["utc_offset"] == "UTC+8"
    assert w["next_ingress"]["text"] == "03:49 ngày 22/12/1964" and w["near_cusp"]
    later = hd.sun_sign(normalize(BirthInput(1964, 12, 22, 4, 0, "Asia/Ho_Chi_Minh", "male")))
    assert later["sun_sign"]["name"] == "Ma Kết"
    # the same wall time read as UTC+7 would be an hour later in absolute time: the zone matters at the boundary
    assert hd.sun_sign_at(dt.datetime(1964, 12, 22, 3, 30, tzinfo=ICT), ICT)["sun_sign"]["name"] == "Ma Kết"


def test_lookup_and_periods():
    w = hd.lookup(1990, 5, 17, 10, 30)
    assert w["sun_sign"]["name"] == "Kim Ngưu" and w["ingress"]["text"] == "15:26 ngày 20/04/1990"
    rows = hd.sign_periods("ma-ket", range(2024, 2026))
    assert [r["year"] for r in rows] == [2024, 2025] and rows[0]["to"]["local"].startswith("2025-01")
    with pytest.raises(ValueError):
        hd.lookup(2023, 2, 30, 0, 0)


def test_api_chart_block_and_lookup():
    c = TestClient(app)
    r = c.post("/api/chart", json={"year": 1990, "month": 5, "day": 17, "hour": 10, "minute": 30, "gender": "male"}).json()
    w = r["western"]
    assert {"sun_sign", "ingress", "next_ingress", "cusp_hours"} <= set(w)
    assert w["sun_sign"]["name"] == "Kim Ngưu" and w["cusp_hours"] > 24 and not w["near_cusp"]
    g = c.get("/api/hoang-dao", params={"y": 1964, "m": 12, "d": 22, "h": 3, "mi": 30, "tz": "Asia/Ho_Chi_Minh"})
    assert g.status_code == 200 and g.json()["sun_sign"]["name"] == "Nhân Mã" and "max-age" in g.headers["cache-control"]
    assert c.get("/api/hoang-dao", params={"y": 2023, "m": 2, "d": 30}).status_code == 422
    assert c.get("/api/hoang-dao", params={"y": 1800, "m": 1, "d": 1}).status_code == 422


RULES = json.loads((ROOT / "tools" / "data" / "hoang_dao_rules.json").read_text("utf-8"))
PACK = json.loads((ROOT / "engine" / "data" / "hoang_dao" / "pack.json").read_text("utf-8"))
SLUGS = [s[0] for s in hd.SIGNS]


def test_pack_is_built_from_the_entries_and_kept_apart_from_the_rule_packs():
    from tvbt.knowledge.loader import PACKS
    import build_hoang_dao_pack as b
    assert {"sign", "book", "page", "quote", "reading", "use", "topic", "facts"} <= set(RULES["fields"])
    pack, quotes = b.build(RULES["entries"])
    assert pack == PACK and quotes == json.loads((ROOT / "engine" / "data" / "hoang_dao" / "quotes.json").read_text("utf-8"))   # rebuilt
    assert not any("hoang" in p for p in PACKS) and not list((ROOT / "engine" / "data").glob("pack_*hoang*"))
    good = {"id": "x1", "sign": "bach-duong", "book": "AL", "page": 13, "topic": "trait", "quote": "one two three four five six",
            "reading": "người thuộc cung hoàng đạo này…", "use": "reading"}
    assert b.check(good) == []
    for bad in ({"reading": "cung này"}, {"book": "XX"}, {"page": "12"}, {"quote": "five words only right here"}, {"topic": "health"},
                {"book": "CA"}, {"facts": {"element": "fire"}}, {"topic": "classification", "facts": {"ruler": "Uranus"}}):
        assert b.check({**good, **bad}), bad
    src = {s["id"] for s in json.loads((ROOT / "engine" / "data" / "sources.json").read_text("utf-8"))["sources"]}
    assert {"SRC_ALAN_LEO_AFA", "SRC_LILLY_CA", "SRC_PTOLEMY_TETRABIBLOS"} <= src
    assert next(s for s in PACK["sources"] if s["code"] == "TB")["edition"].startswith("J. M. Ashmand")       # not Robbins


def test_every_sign_has_cited_readings_and_facts():
    for slug in SLUGS:
        rs = hd.readings(slug)
        char = [r for r in rs if r["topic"] in ("trait", "work")]
        assert 8 <= len(char) <= 16 and all(r["book"] == "AL" for r in char), slug          # Alan Leo for the character
        assert all(r["book"] in ("CA", "TB") or r["topic"] for r in rs)
        assert all(r["topic"] == "classification" for r in rs if r["book"] in ("CA", "TB")), slug   # Lilly / Ptolemy: classification only
        f = hd.facts(slug)
        assert set(f) == {"element", "modality", "ruler"}, slug
        assert all(c["page"] > 0 and c["short"] in ("Alan Leo", "Lilly", "Ptolemy") for v in f.values() for c in v["cites"])
    el = {s: hd.facts(s)["element"]["value"] for s in SLUGS}
    assert [el[s] for s in SLUGS] == ["fire", "earth", "air", "water"] * 3                   # the order every book gives
    mod = [hd.facts(s)["modality"]["value"] for s in SLUGS]
    assert mod == ["cardinal", "fixed", "mutable"] * 4
    assert [hd.facts(s)["ruler"]["value"] for s in SLUGS] == ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars",
                                                               "Jupiter", "Saturn", "Saturn", "Jupiter"]


def test_entries_leave_out_what_the_owner_excluded():
    words = re.compile(r"\b(health|disease|illness|ailment|death|die|accident|prison|crime|sex|lust|passion|marr\w*|pregnan\w*|children|"
                       r"women|men become|Hindu|race|drink|medicine|Neptune|Uranus|Moon in|aspect|house of the zodiac)\b", re.I)
    for e in RULES["entries"]:
        assert len(e["quote"].split()) >= 6, e["id"]
        assert not words.search(e["quote"]) or e["topic"] == "classification", (e["id"], e["quote"])
        assert not re.search(r"\b(sức khỏe|bệnh|chết|tai nạn|hôn nhân|kết hôn|con cái|tình dục)\b", e["reading"], re.I), e["id"]
        assert not re.search(r"\bAI\b", e["reading"]) and not re.search(r"\bcung\b(?! hoàng đạo)", e["reading"], re.I), e["id"]


def test_lookup_carries_the_readings():
    w = hd.lookup(1990, 5, 17, 10, 30)
    assert w["reading_status"] is None and w["facts"]["element"]["label"] == "Đất" and w["facts"]["ruler"]["label"] == "Sao Kim"
    assert any(r["reading"].startswith("Chậm mà chắc") and r["short"] == "Alan Leo" and r["page"] == 16 for r in w["readings"])


def test_book_text_english_normalisation():
    import book_text as bt
    assert {"AL", "CA", "TB"} <= set(bt.BOOK_FILES) and bt.ENGLISH == {"AL", "CA", "TB"}
    assert bt.en_clean("The ﬁrst sign , “Aries” is astro-\n  logy ( fire ) well-known") == 'The first sign, "Aries" is astrology (fire) well-known'
    assert bt.en_clean("Baby¬\nlonian") == "Babylonian"
    assert bt.en_norm("“The Ram’s” sign—bold") == bt.en_norm('"The Rams" sign - bold')
    assert bt.en_key("the Seafon of the yeer", "CA") == bt.en_key("the Season of the yeer", "CA")       # long s read as f (1647)
    assert bt.en_key("Seafon", "AL") != bt.en_key("Season", "AL")
    assert bt.decode("aø") == "à" and "KL" in bt.BOOK_FILES      # the Vietnamese books are untouched


def test_page_maps_follow_the_measured_offsets():
    import book_text as bt
    assert bt.en_pdf_page("AL", 13) == 28 and bt.en_pdf_page("AL", 48) == 63 and bt.en_pdf_page("AL", 51) == 64   # the scan skips pp.49-50
    assert bt.en_pdf_page("CA", 93) == 127 and bt.en_pdf_page("TB", 42) == 78
    for book, page in (("AL", 49), ("AL", 300), ("CA", 200), ("TB", 1)):
        with pytest.raises(ValueError):
            bt.en_pdf_page(book, page)


QUOTES = json.loads((ROOT / "engine" / "data" / "hoang_dao" / "quotes.json").read_text("utf-8"))["quotes"]


def _book(code: str) -> bool:
    import book_text as bt
    return bt.available(code)


@pytest.mark.parametrize("q", QUOTES, ids=lambda q: q["id"])
def test_every_quote_is_on_its_page(q):
    import book_text as bt
    if not bt.available(q["book"]):
        pytest.skip(f"{q['book']} PDF not present ($TVBT_BOOKS_DIR)")
    assert bt.quote_on_page(q["book"], q["page"], q["quote"]), q


@pytest.mark.skipif(not (_book("AL") and _book("CA") and _book("TB")), reason="English PDFs not present")
def test_quote_check_has_teeth():
    import book_text as bt
    q = "they are leaders in ideals and pioneers of advanced thought"
    assert bt.en_match("AL", 13, q)["exact"] and not bt.en_match("AL", 14, q)["ok"] and not bt.en_match("AL", 16, q)["ok"]
    assert not bt.en_match("AL", 13, "they are followers in ideals and enemies of advanced thought")["ok"]
    assert bt.en_match("CA", 97, "of the watry Triplicity, fixed and North, the house and joy of Mars")["ok"]
    assert not bt.en_match("TB", 42, "Mars is dry in nature, and beneath the sphere of Jupiter")["ok"]                # that is p.43

def _new_pages() -> dict[str, str]:
    out = sitegen.render()
    return {k: v for k, v in out.items() if k.startswith("bai-viet/hoang-dao/") or k.startswith("cung-hoang-dao/")}


def _visible(doc: str) -> str:
    main = doc.split('<main id="main"', 1)[1].split("</main>", 1)[0]
    main = re.sub(r"<(script|svg)\b.*?</\1>", " ", main, flags=re.S)
    return re.sub(r"<[^>]+>", " ", main)


def test_new_pages_words():
    pages = _new_pages()
    assert len(pages) == 14 and "cung-hoang-dao/index.html" in pages and "bai-viet/hoang-dao/bo-cap/index.html" in pages
    for rel, doc in pages.items():
        assert not re.search(r"\bAI\b", doc), rel
        text = _visible(doc)
        bare = re.findall(r"\bcung\b(?! hoàng đạo)(?! của lá số Tử Vi)", text, re.I)
        assert not bare, (rel, re.findall(r".{30}\bcung\b(?! hoàng đạo).{30}", text, re.I)[:3])
        assert not re.search("[♈-♓]", doc), rel             # glyphs are SVG, never the ♈ characters
    for f in ("hoangdao.js", "hoangdao_page.js"):
        js = (WEB / "js" / f).read_text("utf-8")
        assert not re.search(r"\bAI\b", js) and not re.search("[♈-♓]", js), f
    sign = pages["bai-viet/hoang-dao/bach-duong/index.html"]
    assert "Xuân Phân" in sign and "10:06 ngày 20/03/2024" in sign and "[Alan Leo, tr. 13]" in sign and "[Ptolemy, tr. 43]" in sign
    assert "Nguồn của bài này" in sign and "Ashmand" in sign and '"@type":"Book"' in sign
    assert "/js/hoangdao_page.js" in pages["cung-hoang-dao/index.html"]
    sm = sitegen.render()["sitemap.xml"]
    assert f"<loc>{sitegen.ORIGIN}/cung-hoang-dao/</loc>" in sm and f"<loc>{sitegen.ORIGIN}/bai-viet/hoang-dao/song-ngu/</loc>" in sm
    from tvbt import sitenav
    assert any(it[1] == "/cung-hoang-dao/" and it[2] == "Cung hoàng đạo" for it in sitenav.ITEMS)


def test_chart_page_keeps_tu_vi_and_western_apart():
    """Owner 2026-10-25 ('bị lẫn lộn'): the Western sun sign is not drawn on the Tử Vi / Bát Tự chart page (no card in the Tử Vi pane,
    no chip among Nhật Chủ / Cục / Nạp âm); it lives on /cung-hoang-dao/ and the sign pages, under Chiêm tinh in the menu."""
    app_js = (WEB / "js" / "app.js").read_text("utf-8")
    assert "hoangdao" not in app_js.lower()
    html = (WEB / "index.html").read_text("utf-8")
    assert "hoangdao-host" not in html and "hd-card" not in html
    shares = (ROOT / "src" / "account" / "shares.ts").read_text("utf-8")
    assert 'k === "western"' in shares                                            # the Worker drops the block from hidden shares
