"""Fetches the 78 Waite–Smith card scans from Wikimedia Commons and writes engine/data/tarot/images.json + engine/web/tarot/img/*.webp.

Source: Commons category "Rider-Waite-Smith tarot deck (TaionWC)", the "Pam-A" printing of Pamela Colman Smith's original drawings
(the 1909 deck, as first printed; not the Universal Waite, the Radiant deck or the 1971 US Games redraw). Owner approval 2026-10-25.

For every file the page's own licence section is read (wikitext) together with the licence Commons reports (extmetadata). A file is used
only when its licence section carries a PD template (PD-old…, PD-US…, PD-…expired) AND Commons reports "Public domain"; any other file is
listed under "skipped" with the reason, and the page shows the typographic card face for it.

Each original is downloaded into a fresh, EMPTY directory given on the command line (downloads are kept apart from code), its SHA-1 is
checked against Commons, its SHA-256 recorded, and two WebP files are made: ~300 px and ~600 px wide. Needs Pillow with WebP support:
    python3 -I tools/fetch_tarot_images.py --dir /path/to/new/empty/dir
"""
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECK = json.loads((ROOT / "engine" / "data" / "tarot" / "deck.json").read_text("utf-8"))
OUT_JSON = ROOT / "engine" / "data" / "tarot" / "images.json"
OUT_IMG = ROOT / "engine" / "web" / "tarot" / "img"
API = "https://commons.wikimedia.org/w/api.php"
CATEGORY = "Category:Rider-Waite-Smith tarot deck (TaionWC)"
UA = "ThienBan-tarot-build/0.1 (https://tu-vi-bat-tu.tridinhbui0901.workers.dev/tarot/)"
WIDTHS = (300, 600)
PD_TEMPLATE = re.compile(r"\{\{\s*(PD-[^}]*)\}\}", re.I)
SUIT_FILE = {"Wands": "W", "Cups": "C", "Swords": "S", "Pents": "P"}


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 + 3 * attempt)


def api(**params) -> dict:
    return json.loads(get(API + "?" + urllib.parse.urlencode({"format": "json", **params})))


def card_id(title: str) -> str | None:
    m = re.fullmatch(r"File:RWS Tarot (\d\d) .+\.jpg", title)
    if m:
        return f"M{m.group(1)}"
    m = re.fullmatch(r"File:(Wands|Cups|Swords|Pents)(\d\d)\.jpg", title)
    return f"{SUIT_FILE[m.group(1)]}{m.group(2)}" if m else None


def licence_section(wikitext: str) -> str:
    i = wikitext.find("{{int:license-header}}")
    return wikitext[i:] if i >= 0 else wikitext


def strip_html(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


def main() -> None:
    if "--dir" not in sys.argv:
        sys.exit(__doc__)
    dl = Path(sys.argv[sys.argv.index("--dir") + 1])
    dl.mkdir(parents=True, exist_ok=True)
    if any(dl.iterdir()):
        sys.exit(f"{dl} is not empty: downloads go into a fresh, empty directory")
    from PIL import Image  # system Pillow; imported late so --help works without it

    titles = [m["title"] for m in api(action="query", list="categorymembers", cmtitle=CATEGORY, cmtype="file", cmlimit=500)["query"]["categorymembers"]]
    by_card = {card_id(t): t for t in titles if card_id(t)}
    cards = {c["id"]: c for c in DECK["cards"]}
    assert set(by_card) == set(cards), sorted(set(cards) ^ set(by_card))
    info = {}
    for i in range(0, len(titles), 25):
        chunk = "|".join(titles[i:i + 25])
        q = api(action="query", titles=chunk, prop="imageinfo|revisions", iiprop="url|sha1|size|extmetadata", rvprop="content", rvslots="main")
        for p in q["query"]["pages"].values():
            info[p["title"]] = p
        time.sleep(1)

    OUT_IMG.mkdir(parents=True, exist_ok=True)
    images, skipped = [], []
    for c in DECK["cards"]:
        title = by_card[c["id"]]
        p = info[title]
        ii = p["imageinfo"][0]
        meta = {k: v.get("value") for k, v in ii.get("extmetadata", {}).items()}
        text = p["revisions"][0]["slots"]["main"]["*"]
        templates = ["{{" + t.strip() + "}}" for t in PD_TEMPLATE.findall(licence_section(text))]
        short = strip_html(meta.get("LicenseShortName", ""))
        page_url = ii["descriptionurl"]
        if not templates or short != "Public domain":
            skipped.append({"card": c["id"], "slug": c["slug"], "commons_url": page_url, "licence": short,
                            "reason": "the page does not state a public-domain licence"})
            continue
        url = ii["url"].split("?")[0]
        raw = get(url)
        (dl / url.rsplit("/", 1)[1]).write_bytes(raw)
        assert hashlib.sha1(raw).hexdigest() == ii["sha1"], title
        files = {}
        with Image.open(dl / url.rsplit("/", 1)[1]) as im:
            im = im.convert("RGB")
            assert im.size == (ii["width"], ii["height"]), title
            for w in WIDTHS:
                h = round(im.height * w / im.width)
                out = OUT_IMG / f"{c['slug']}-{w}.webp"
                im.resize((w, h), Image.LANCZOS).save(out, "WEBP", quality=80, method=6)
                files[str(w)] = {"path": f"/tarot/img/{out.name}", "width": w, "height": h, "sha256": hashlib.sha256(out.read_bytes()).hexdigest()}
        images.append({
            "card": c["id"], "slug": c["slug"], "commons_file": title, "commons_url": page_url, "original_url": url,
            "licence": " ".join(templates), "licence_short_name": short,
            "licence_categories": [x for x in (meta.get("Categories") or "").split("|") if x.startswith("PD") or x.startswith("CC-PD")],
            "author": strip_html(meta.get("Artist", "")), "date": strip_html(meta.get("DateTimeOriginal", "")),
            "printing": "Pam-A" if "Pam-A" in strip_html(meta.get("ImageDescription", "")) else "", "source": strip_html(meta.get("Credit", "")),
            "sha256": hashlib.sha256(raw).hexdigest(), "commons_sha1": ii["sha1"], "width": ii["width"], "height": ii["height"], "files": files,
        })
        print(c["id"], title, templates[0], flush=True)
        time.sleep(0.5)
    doc = {
        "note": "Ảnh lá bài Waite–Smith (bản in 'Pam-A' của tranh gốc Pamela Colman Smith) từ Wikimedia Commons, chủ nhà duyệt 2026-10-25. "
                "Mỗi tệp: trang tệp trên Commons, giấy phép đúng như trang ghi (mẫu PD trong mục giấy phép), SHA-256 của tệp gốc đã tải, kích thước gốc, "
                "và hai bản WebP (~300 px, ~600 px). Tệp nào trang không ghi phạm vi công cộng thì nằm ở 'skipped' và trang dùng mặt bài chữ. "
                "Tạo lại: python3 -I tools/fetch_tarot_images.py --dir <thư mục mới, trống>.",
        "category": "https://commons.wikimedia.org/wiki/" + CATEGORY.replace(" ", "_"),
        "fields": {"commons_url": "trang tệp trên Commons", "licence": "mẫu giấy phép in trong mục Licensing của trang",
                   "licence_short_name": "giấy phép Commons báo (extmetadata)", "sha256": "SHA-256 của tệp gốc đã tải",
                   "commons_sha1": "SHA-1 Commons công bố, đã so khớp", "width": "chiều rộng tệp gốc (px)", "height": "chiều cao tệp gốc (px)",
                   "files": "các bản WebP phục vụ trên trang"},
        "images": images, "skipped": skipped,
    }
    OUT_JSON.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(len(images), "images,", len(skipped), "skipped")


if __name__ == "__main__":
    main()
