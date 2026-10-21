"""Builds engine/data/ha_lac/hexagrams.json from Part II of "Bát tự Hà Lạc" (dantocking.com PDF, 129 pages): hexagrams 24-64.

The PDF is untrusted input: run this with `python -I` (isolated mode) and never from inside the downloads folder. It is looked up in
$TVBT_BOOKS_DIR (default ~/Downloads) as HA_LAC_PDF; the book is NOT part of the repository.

What the tool does
  * parses the text layer (clean Unicode, printed page = PDF index + 1) into hexagram -> hào -> field, each field with the page it starts on;
  * keeps only structured facts (number, name, month, Nạp Giáp ages, âm/dương of each hào, which tuế-vận groups the book lists) plus a
    short quote anchor per hào (first words of the classical hào text, Hán-Việt) so a test can find it on the printed page;
  * the readings themselves are stored as PARAPHRASES (copyright): they are written by hand, kept in hexagrams.json and carried over on
    every rebuild; `--paraphrases FILE` imports new ones (same key layout as `paraphrase_keys`). Poems ("THƠ RẰNG") are never stored.
  * a guard refuses a paraphrase that repeats a long source field word for word.

    python -I tools/build_ha_lac.py            # rebuild, keep paraphrases already in hexagrams.json
    python -I tools/build_ha_lac.py --check    # rebuild in memory and fail if hexagrams.json differs
    python -I tools/build_ha_lac.py --dump-raw OUT.json   # verbatim parse for paraphrasing work; write it OUTSIDE the repo

Nothing here casts a hexagram for a person: Part I of the book (the casting method) is not in this PDF (docs/HA-LAC-PLAN.md, step H0)."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "engine" / "data" / "ha_lac" / "hexagrams.json"
HA_LAC_PDF = "Bát-tự-Hà-Lạc-dantocking.com.pdf"
PDF_PAGES = 129
FIRST, LAST = 24, 64

# King Wen order, Hán-Việt short name, upper / lower trigram. Standard Kinh Dịch facts, used to check what the parser reads.
TRIGRAM_LINES = {"Kiền": "111", "Đoài": "110", "Ly": "101", "Chấn": "100", "Tốn": "011", "Khảm": "010", "Cấn": "001", "Khôn": "000"}  # hào 1..3, 1 = dương
TRIGRAM_IMAGE = {"Kiền": "Thiên", "Đoài": "Trạch", "Ly": "Hỏa", "Chấn": "Lôi", "Tốn": "Phong", "Khảm": "Thủy", "Cấn": "Sơn", "Khôn": "Địa"}
KING_WEN = {
    24: ("Phục", "Khôn", "Chấn"), 25: ("Vô Vọng", "Kiền", "Chấn"), 26: ("Đại Súc", "Cấn", "Kiền"), 27: ("Di", "Cấn", "Chấn"),
    28: ("Đại Quá", "Đoài", "Tốn"), 29: ("Khảm", "Khảm", "Khảm"), 30: ("Ly", "Ly", "Ly"), 31: ("Hàm", "Đoài", "Cấn"),
    32: ("Hằng", "Chấn", "Tốn"), 33: ("Độn", "Kiền", "Cấn"), 34: ("Đại Tráng", "Chấn", "Kiền"), 35: ("Tấn", "Ly", "Khôn"),
    36: ("Minh Di", "Khôn", "Ly"), 37: ("Gia Nhân", "Tốn", "Ly"), 38: ("Khuê", "Ly", "Đoài"), 39: ("Kiển", "Khảm", "Cấn"),
    40: ("Giải", "Chấn", "Khảm"), 41: ("Tổn", "Cấn", "Đoài"), 42: ("Ích", "Tốn", "Chấn"), 43: ("Quải", "Đoài", "Kiền"),
    44: ("Cấu", "Kiền", "Tốn"), 45: ("Tụy", "Đoài", "Khôn"), 46: ("Thăng", "Khôn", "Tốn"), 47: ("Khốn", "Đoài", "Khảm"),
    48: ("Tỉnh", "Khảm", "Tốn"), 49: ("Cách", "Đoài", "Ly"), 50: ("Đỉnh", "Ly", "Tốn"), 51: ("Chấn", "Chấn", "Chấn"),
    52: ("Cấn", "Cấn", "Cấn"), 53: ("Tiệm", "Tốn", "Cấn"), 54: ("Quy Muội", "Chấn", "Đoài"), 55: ("Phong", "Chấn", "Ly"),
    56: ("Lữ", "Ly", "Cấn"), 57: ("Tốn", "Tốn", "Tốn"), 58: ("Đoài", "Đoài", "Đoài"), 59: ("Hoán", "Tốn", "Khảm"),
    60: ("Tiết", "Khảm", "Đoài"), 61: ("Trung Phu", "Tốn", "Đoài"), 62: ("Tiểu Quá", "Chấn", "Cấn"), 63: ("Ký Tế", "Khảm", "Ly"),
    64: ("Vị Tế", "Ly", "Khảm"),
}
STEMS = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
HAO_FIELDS = ("y_hao", "menh_hop_cach", "menh_khong_hop")
TUE_VAN_GROUPS = ("quan_chuc", "gioi_si", "nguoi_thuong")
NO_TUE_VAN = {(50, 1)}  # the book prints no "Xem tuế vận" block for quẻ 50 hào 1 (p.77)


def books_dir() -> Path:
    return Path(os.environ.get("TVBT_BOOKS_DIR", "~/Downloads")).expanduser()


def pdf_path() -> Path:
    return books_dir() / HA_LAC_PDF


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def fold(s: str) -> str:
    """Lower-case, no diacritics, single spaces: for matching headings with inconsistent capitals/accents."""
    s = unicodedata.normalize("NFD", nfc(s).replace("đ", "d").replace("Đ", "D"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"\s+", " ", s).strip()


def norm(s: str) -> str:
    """Same normalisation as tools/book_text.norm (used to compare a quote with a page)."""
    s = re.sub(r"\s+", " ", nfc(s).lower())
    return re.sub(r"[\"“”'’.,;:!?()\-–—…]", "", s).replace("  ", " ").strip()


def read_pages(path: Path) -> list[str]:
    import pymupdf  # PyMuPDF, only needed when the book is present
    with pymupdf.open(str(path)) as doc:
        return [nfc(p.get_text()) for p in doc]


# ---------------------------------------------------------------- parsing

HEX_RE = re.compile(r"^(\d{2})\)\.?\s+([A-ZÀ-Ỹ][A-ZÀ-Ỹ ]+)$")
HAO_RE = re.compile(r"^HÀO\s+([1-6])\s+(ÂM|DƯƠNG)\s*[:.]?\s*(.*)$")
FIELD_RE = [  # (key, regex on the folded line); value = text after the label
    ("y_hao", re.compile(r"^(y )?hao\s*[:;]?\s*(?![1-6]\b)")),  # one hào prints only "Hào:" (63.6)
    ("menh_hop_cach", re.compile(r"^menh hop cach\s*[:;]\s*")),
    ("menh_khong_hop", re.compile(r"^menh khong hop( cach)?\s*[:;]\s*")),
]
TV_RE = re.compile(r"^-\s*(quan chuc va gioi si|gioi si va nguoi thuong|quan chuc|gioi si|nguoi thuong|nu mang|buon ban|quan)\s*[:;]?\s*")
TV_KEYS = {"quan chuc": ["quan_chuc"], "quan": ["quan_chuc"], "gioi si": ["gioi_si"], "nguoi thuong": ["nguoi_thuong"],
           "quan chuc va gioi si": ["quan_chuc", "gioi_si"], "gioi si va nguoi thuong": ["gioi_si", "nguoi_thuong"],
           "nu mang": ["nu_mang"], "buon ban": ["buon_ban"], "chung": ["chung"]}


def fold1(s: str) -> str:
    """Per-character fold (same length as the NFC input), so a match end on the folded line is a cut point on the original."""
    out = []
    for c in s:
        b = unicodedata.normalize("NFD", c.replace("đ", "d").replace("Đ", "D"))[0].lower()
        out.append(b if len(b) == 1 else c)
    return "".join(out)


def _cut_label(line: str, folded_label_re: re.Pattern) -> str | None:
    """Text after a label matched on the folded line (labels vary in capitals, accents and ':' vs ';')."""
    m = folded_label_re.match(fold1(line.strip()))
    return None if not m else line.strip()[m.end():].lstrip(":; ").strip()


def lines_with_pages(pages: list[str]):
    for i, txt in enumerate(pages):
        for ln in txt.splitlines():
            ln = ln.strip()
            if ln:
                yield i + 1, ln


def parse(pages: list[str]) -> list[dict]:
    """Verbatim parse of pp.1-121. Returns raw records (text kept only in memory / --dump-raw, never written to the repo)."""
    hexes: list[dict] = []
    hx = hao = None
    cur: dict | None = None  # {"text": [...], "page": n} of the field being filled
    mode = None  # what the following lines belong to

    def start(target: dict, key: str, text: str, page: int):
        nonlocal cur
        target[key] = {"text": [text] if text else [], "page": page}
        cur = target[key]

    prev = ""
    for page, ln in lines_with_pages(pages):
        if page > 121:
            break
        prev_line, prev = prev, ln
        f = fold(ln)
        m = HEX_RE.match(ln)
        if m and hx is not None and int(m.group(1)) == hx["number"]:
            # quẻ 48's heading block is printed twice (pp.70 and 71); keep the first, skip the copy up to its first hào
            hx["reprinted_on"] = page
            cur, mode = None, "reprint"
            continue
        if m and FIRST <= int(m.group(1)) <= LAST:
            hx = {"number": int(m.group(1)), "heading": m.group(2).strip(), "page": page, "hao": [], "raw": {}}
            hexes.append(hx)
            hao, cur, mode = None, None, "head"
            continue
        if hx is None:
            continue
        m = HAO_RE.match(ln)
        if m:
            hao = {"hao": int(m.group(1)), "line": "dương" if m.group(2) == "DƯƠNG" else "âm", "page": page, "raw": {}}
            hx["hao"].append(hao)
            start(hao["raw"], "hao_tu", m.group(3), page)
            mode = "hao"
            continue
        if mode == "reprint":
            continue
        if f.startswith("tho rang"):
            cur, mode = None, "poem"
            continue
        if mode == "poem":
            continue
        tgt = hao["raw"] if hao else hx["raw"]
        if f.startswith("ten que"):
            start(tgt, "name_gloss", ln.split(":", 1)[1].strip() if ":" in ln else ln[7:].strip(), page)
            continue
        if f.startswith("thuoc thang"):
            start(tgt, "month", ln, page)
            continue
        if f == "loi tuong":
            start(tgt, "loi_tuong", "", page)
            continue
        if f == "luoc nghia":
            start(tgt, "luoc_nghia", "", page)
            continue
        if f in ("ha lac giai doan",):
            cur = None
            continue
        if f.startswith("nhung tuoi nap giap"):
            start(tgt, "nap_giap", "", page)
            continue
        if f.startswith("xem tue van"):
            tgt.setdefault("tue_van", [])
            cur, mode = None, "tv"
            continue
        hit = None
        for key, rx in FIELD_RE:
            rest = _cut_label(ln, rx)
            if rest is not None:
                hit = key
                break
        if hit and hao is not None:
            note = None
            if hit == "y_hao" and not fold(ln).startswith("y "):
                note = "printed label 'Hào:' (the 'Ý' is missing)"
            if hit == "menh_khong_hop" and "menh_khong_hop" in tgt and "menh_hop_cach" not in tgt:
                # 'Mệnh không hợp' printed twice: the first one stands where 'Mệnh hợp cách' belongs
                tgt["menh_hop_cach"] = tgt.pop("menh_khong_hop")
                tgt["menh_hop_cach"]["label_note"] = "printed as 'Mệnh không hợp' (label repeated); position is Mệnh hợp cách"
            elif hit == "menh_hop_cach" and "menh_hop_cach" in tgt and "menh_khong_hop" not in tgt:
                hit, note = "menh_khong_hop", "printed as 'Mệnh hợp cách' (label repeated); position is Mệnh không hợp"
            start(tgt, hit, rest, page)
            if note:
                tgt[hit]["label_note"] = note
            continue
        if hit:
            start(tgt, hit, rest, page)
            continue
        if mode == "tv" and hao is not None:
            m = TV_RE.match(fold1(ln))
            paragraph_end = len(prev_line) < 70 and prev_line.rstrip()[-1:] in ".!)"
            if m or cur is None or paragraph_end:
                # a labelled group, or an unlabelled paragraph that speaks of the year in general
                group = m.group(1) if m else "chung"
                rest = ln[m.end():].lstrip(":; ").strip() if m else ln
                entry = {"group": group, "keys": TV_KEYS[group], "text": [rest] if rest else [], "page": page}
                tgt["tue_van"].append(entry)
                cur = entry
                continue
        if cur is not None:
            if not cur["text"]:
                cur["page"] = page  # a label at the foot of a page whose text starts overleaf
            cur["text"].append(ln)
        else:
            hx.setdefault("unplaced", []).append((page, ln))
    for h in hexes:
        h["page_end"] = None
    for a, b in zip(hexes, hexes[1:]):
        a["page_end"] = b["page"]
    if hexes:
        hexes[-1]["page_end"] = 121
    return hexes


def joined(field: dict | None) -> str:
    if not field:
        return ""
    return re.sub(r"\s+", " ", " ".join(field["text"])).strip()


NAP_GIAP_RE = re.compile(r"((?:%s)(?:\s*(?:,|hoặc|và)\s*(?:%s))*)\s*:\s*([^;\n]+?)(?=[.;]|$)" % ("|".join(STEMS), "|".join(STEMS)))
FAVOURED_RE = re.compile(r"[Ll]ại sanh (?:từ )?tháng (\d{1,2})(?: đến tháng (\d{1,2}))?,? là cách công danh phú\s+quý[.,]?\s*")


def parse_nap_giap(field: dict | None) -> tuple[list[dict], dict | None, str]:
    """'Canh: Dần, Thìn, Ngọ' lines -> [{stems, branches}]; 'Lại sanh tháng N là cách công danh phú quý' -> {from, to};
    any further sentence (seasons where the fortune is thicker / thinner) is returned as text for a paraphrase."""
    lines = (field or {}).get("text", [])
    rows, rest = [], []
    for ln in lines:
        m = NAP_GIAP_RE.match(ln.strip())
        if m:
            # printed order is kept ("Quý hoặc Ất: Sửu, Hợi, Dậu")
            stems = re.findall(r"(?<!\w)(%s)(?!\w)" % "|".join(STEMS), m.group(1))
            br = re.findall(r"(?<!\w)(%s)(?!\w)" % "|".join(BRANCHES), m.group(2))
            rows.append({"stems": stems, "branches": br})
            tail = ln.strip()[m.end():].lstrip(".; ")
            if tail:
                rest.append(tail)
        else:
            rest.append(ln.strip())
    text = re.sub(r"\s+", " ", " ".join(rest)).strip()
    fav = None
    m = FAVOURED_RE.search(text)
    if m:
        fav = {"from": int(m.group(1)), "to": int(m.group(2) or m.group(1))}
        text = (text[:m.start()] + text[m.end():]).strip()
    return rows, fav, text


def month_of(field: dict | None) -> int | None:
    m = re.search(r"tháng\s+(\d{1,2})", joined(field), re.I)
    return int(m.group(1)) if m else None


def quote_anchor(text: str, max_words: int = 8) -> str:
    """First clause of the classical hào text (Hán-Việt), at most `max_words` words: a short anchor, not the reading."""
    first = re.split(r"[.,;:]", text, maxsplit=1)[0].strip()
    return " ".join(first.split()[:max_words])


# ---------------------------------------------------------------- output

def paraphrase_keys(raw_hexes: list[dict]) -> list[str]:
    """Every paraphrase slot: '24.tuong', '24.name_gloss', '24.nap_giap_note', '24.1.y_hao', '24.1.tue_van.quan_chuc', ..."""
    keys = []
    for h in raw_hexes:
        n = h["number"]
        keys += [f"{n}.name_gloss", f"{n}.tuong"]
        if parse_nap_giap(h["raw"].get("nap_giap"))[2]:
            keys.append(f"{n}.nap_giap_note")
        for a in h["hao"]:
            keys += [f"{n}.{a['hao']}.{k}" for k in HAO_FIELDS if a["raw"].get(k)]
            for e in a["raw"].get("tue_van", []):
                keys.append(f"{n}.{a['hao']}.tue_van.{'+'.join(e['keys'])}")
    return keys


def source_text(raw_hexes: list[dict]) -> dict[str, str]:
    """Verbatim source of each paraphrase key (for the paraphrasing work and the copy guard)."""
    src = {}
    for h in raw_hexes:
        n, r = h["number"], h["raw"]
        src[f"{n}.name_gloss"] = joined(r.get("name_gloss"))
        src[f"{n}.tuong"] = (joined(r.get("loi_tuong")) + " || " + joined(r.get("luoc_nghia"))).strip()
        other = parse_nap_giap(r.get("nap_giap"))[2]
        if other:
            src[f"{n}.nap_giap_note"] = other
        for a in h["hao"]:
            for k in HAO_FIELDS:
                if a["raw"].get(k):
                    src[f"{n}.{a['hao']}.{k}"] = joined(a["raw"][k])
            for e in a["raw"].get("tue_van", []):
                src[f"{n}.{a['hao']}.tue_van.{'+'.join(e['keys'])}"] = re.sub(r"\s+", " ", " ".join(e["text"])).strip()
    return src


def longest_shared_run(a: str, b: str) -> int:
    """Longest run of consecutive words (normalised) that two texts share."""
    x, y = norm(a).split(), norm(b).split()
    best, prev = 0, [0] * (len(y) + 1)
    for i in range(1, len(x) + 1):
        cur = [0] * (len(y) + 1)
        for j in range(1, len(y) + 1):
            if x[i - 1] == y[j - 1]:
                cur[j] = prev[j - 1] + 1
                best = max(best, cur[j])
        prev = cur
    return best


MAX_SHARED_RUN = 7  # a paraphrase may echo a short phrase of the book (a short quote), never 8+ words in a row


def too_close(para: str, src: str) -> bool:
    return longest_shared_run(para, src) > MAX_SHARED_RUN


def build(raw_hexes: list[dict], para: dict[str, str]) -> dict:
    src = source_text(raw_hexes)
    missing = [k for k in paraphrase_keys(raw_hexes) if not para.get(k)]
    if missing:
        raise SystemExit(f"{len(missing)} paraphrases missing, e.g. {missing[:5]} (import with --paraphrases)")
    copied = [k for k in src if k in para and too_close(para[k], src[k])]
    if copied:
        raise SystemExit(f"paraphrase repeats the source word for word: {copied[:5]}")

    out = []
    for h in raw_hexes:
        n, r = h["number"], h["raw"]
        name, upper, lower = KING_WEN[n]
        rows, fav, other = parse_nap_giap(r.get("nap_giap"))
        hx = {
            "number": n,
            "name": name,
            "full_name": h["heading"].title() if upper != lower else f"Thuần {name}",
            "heading_printed": h["heading"],
            "upper": upper, "lower": lower,
            "pages": [h["page"], h["page_end"]],
            **({"heading_reprinted_on": h["reprinted_on"]} if h.get("reprinted_on") else {}),
            "name_gloss": {"text": para[f"{n}.name_gloss"], "page": r["name_gloss"]["page"]},
            "month": {"value": month_of(r.get("month")), "page": r["month"]["page"]} if r.get("month") else None,
            "tuong": {"text": para[f"{n}.tuong"], "page": (r.get("loi_tuong") or r["luoc_nghia"])["page"]},
            "nap_giap": {"ages": rows, "favoured_birth_months": fav, "page": r["nap_giap"]["page"]} if r.get("nap_giap") else None,
            "hao": [],
        }
        if other:
            hx["nap_giap"]["note"] = para[f"{n}.nap_giap_note"]
        for a in sorted(h["hao"], key=lambda a: a["hao"]):
            ar = a["raw"]
            ho = {"hao": a["hao"], "line": a["line"], "page": a["page"],
                  "quote": {"text": quote_anchor(joined(ar["hao_tu"])), "page": ar["hao_tu"]["page"]}}
            for k in HAO_FIELDS:
                ho[k] = {"text": para[f"{n}.{a['hao']}.{k}"], "page": ar[k]["page"]} if ar.get(k) else None
                if ar.get(k, {}).get("label_note"):
                    ho[k]["label_note"] = ar[k]["label_note"]
            tv = {g: None for g in TUE_VAN_GROUPS}
            extra = []
            for e in ar.get("tue_van", []):
                key = '+'.join(e["keys"])
                item = {"text": para[f"{n}.{a['hao']}.tue_van.{key}"], "page": e["page"]}
                if len(e["keys"]) > 1:
                    item["shared_with"] = [g for g in e["keys"]]
                for g in e["keys"]:
                    if g in tv:
                        tv[g] = item
                    else:
                        extra.append({"group": g, **item})
            ho["tue_van"] = tv
            if extra:
                ho["tue_van_other"] = extra
            if not ar.get("tue_van"):
                ho["tue_van_printed"] = False
            hx["hao"].append(ho)
        out.append(hx)
    return {
        "source": {
            "title": "Bát tự Hà Lạc (Phần II: giải đoán 64 quẻ, bản dantocking.com)",
            "file": HA_LAC_PDF,
            "pdf_pages": PDF_PAGES,
            "page_note": "printed page = PDF page index + 1; this PDF starts at quẻ 24 and lacks Part I (casting method) and quẻ 1-23",
            "coverage": [FIRST, LAST],
        },
        "copyright": "Readings are paraphrased (short Vietnamese summaries), not the book's wording; 'quote' holds only the first words of the "
                     "classical hào text as a page anchor. Poems (THƠ RẰNG) are not stored.",
        "fields": {
            "name_gloss": "Tên quẻ: meaning of the name (paraphrase)",
            "month": "Thuộc tháng N (lunar month the book attaches to the quẻ)",
            "tuong": "Lời tượng + Lược nghĩa (paraphrase)",
            "nap_giap.ages": "Những tuổi Nạp Giáp: stems x branches as printed; note = extra condition printed under the list (paraphrase)",
            "hao[].line": "âm / dương as printed in the 'HÀO n ÂM|DƯƠNG' heading",
            "hao[].y_hao / menh_hop_cach / menh_khong_hop": "Ý hào, Mệnh hợp cách, Mệnh không hợp (paraphrase)",
            "hao[].tue_van": "Xem tuế vận per group (paraphrase); null = the book gives nothing for that group; shared_with = one printed line "
                             "covers several groups ('Quan chức và Giới sĩ'); tue_van_other = 'chung' (an unlabelled remark for everyone), "
                             "'nu_mang', 'buon_ban'; tue_van_printed=false = no Xem tuế vận block at all (50.1)",
            "hao[].quote": "first words (max 8) of the classical hào text in Hán-Việt, as printed: a page anchor",
            "label_note": "the printed label differs from the field's position (misprint); the field follows the position",
        },
        "hexagrams": out,
    }


def load_existing_paraphrases(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text("utf-8"))
    para = {}
    for h in data["hexagrams"]:
        n = h["number"]
        para[f"{n}.name_gloss"] = h["name_gloss"]["text"]
        para[f"{n}.tuong"] = h["tuong"]["text"]
        if h.get("nap_giap") and h["nap_giap"].get("note"):
            para[f"{n}.nap_giap_note"] = h["nap_giap"]["note"]
        for a in h["hao"]:
            for k in HAO_FIELDS:
                if a.get(k):
                    para[f"{n}.{a['hao']}.{k}"] = a[k]["text"]
            seen = set()
            for g, item in list(a["tue_van"].items()) + [(x["group"], x) for x in a.get("tue_van_other", [])]:
                if not item:
                    continue
                key = "+".join(item.get("shared_with", [g]))
                if key not in seen:
                    seen.add(key)
                    para[f"{n}.{a['hao']}.tue_van.{key}"] = item["text"]
    return para


def check_structure(raw: list[dict]) -> list[str]:
    """Problems that would make the data unreliable (each must be empty for a build)."""
    errs = []
    nums = [h["number"] for h in raw]
    if nums != list(range(FIRST, LAST + 1)):
        errs.append(f"hexagram numbers {nums}")
    for h in raw:
        n = h["number"]
        name, upper, lower = KING_WEN[n]
        if fold(name) not in fold(h["heading"]):
            errs.append(f"{n}: heading {h['heading']!r} does not name {name}")
        if [a["hao"] for a in h["hao"]] != [1, 2, 3, 4, 5, 6]:
            errs.append(f"{n}: hào order {[a['hao'] for a in h['hao']]}")
        lines = "".join("1" if a["line"] == "dương" else "0" for a in sorted(h["hao"], key=lambda a: a["hao"]))
        if lines != TRIGRAM_LINES[lower] + TRIGRAM_LINES[upper]:
            errs.append(f"{n}: âm/dương {lines} != {lower}/{upper}")
        for k in ("name_gloss", "month", "nap_giap"):
            if not h["raw"].get(k):
                errs.append(f"{n}: no {k}")
        if not (h["raw"].get("loi_tuong") or h["raw"].get("luoc_nghia")):
            errs.append(f"{n}: no Lời tượng / Lược nghĩa")
        if not parse_nap_giap(h["raw"].get("nap_giap"))[0]:
            errs.append(f"{n}: Nạp Giáp list not parsed")
        for a in h["hao"]:
            for k in HAO_FIELDS:
                if not a["raw"].get(k) or not joined(a["raw"][k]):
                    errs.append(f"{n}.{a['hao']}: no {k}")
            if not a["raw"].get("tue_van") and (n, a["hao"]) not in NO_TUE_VAN:
                errs.append(f"{n}.{a['hao']}: no tuế vận")
            if not joined(a["raw"].get("hao_tu")):
                errs.append(f"{n}.{a['hao']}: no hào text")
        if h.get("unplaced"):
            errs.append(f"{n}: unplaced lines {h['unplaced'][:3]}")
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pdf", type=Path, default=None)
    ap.add_argument("--paraphrases", type=Path, help="JSON {key: paraphrase} to import (overrides those in hexagrams.json)")
    ap.add_argument("--dump-raw", type=Path, help="write {key: verbatim source} for paraphrasing (outside the repo!) and stop")
    ap.add_argument("--check", action="store_true", help="fail if hexagrams.json is not what a rebuild would write")
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args(argv)
    pdf = a.pdf or pdf_path()
    if not pdf.exists():
        print(f"book not found: {pdf} (set TVBT_BOOKS_DIR)", file=sys.stderr)
        return 2
    raw = parse(read_pages(pdf))
    errs = check_structure(raw)
    if errs:
        print("\n".join(errs), file=sys.stderr)
        return 1
    if a.dump_raw:
        if ROOT in a.dump_raw.resolve().parents:
            print("refusing to write verbatim book text inside the repository", file=sys.stderr)
            return 2
        a.dump_raw.write_text(json.dumps(source_text(raw), ensure_ascii=False, indent=1), "utf-8")
        print(f"{len(source_text(raw))} source fields -> {a.dump_raw}")
        return 0
    para = load_existing_paraphrases(a.out)
    if a.paraphrases:
        para.update(json.loads(a.paraphrases.read_text("utf-8")))
    data = build(raw, para)
    text = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    if a.check:
        same = a.out.exists() and a.out.read_text("utf-8") == text
        print("hexagrams.json is up to date" if same else "hexagrams.json differs from a rebuild")
        return 0 if same else 1
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(text, "utf-8")
    print(f"{len(data['hexagrams'])} hexagrams -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
