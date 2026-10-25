"""Ngô Tất Tố's Kinh Dịch (book id KD): page transcriptions -> per-quẻ JSON, plus the checks used to trust them.

    python tools/kinh_dich_ntt.py assemble PAGES_DIR      # PAGES_DIR/p<page>.txt -> engine/data/kinh_dich/ntt/{pages.txt,<n>.json}
    python tools/kinh_dich_ntt.py wiki WIKI_DIR OUT_DIR    # vi.wikisource raw pages (vi_<n>.wiki) -> the same segment shape
    python tools/kinh_dich_ntt.py cer A_DIR B_DIR N...     # character error rate per layer between two sets of <n>.json
    python tools/kinh_dich_ntt.py han                      # Hán of every segment vs the zh.wikisource 周易 fixture

Page transcription format (one file per printed page, written by the transcribers; see docs/KINH-DICH-NTT-TRANSCRIPTION.md):
`=== p.N`, `@cont <layer> [join]`, `@heading`, `@seg <kind> [N|dung]`, layer lines `@han @am @nghia @trinh_di @chu_hy @tien_nho
@other <<label>>` (an untagged line is a further paragraph of the running layer), `@fn n text`, `@note`.  Footnote marks `[^n]` are
renamed `[^<page>.<n>]` so they stay unique inside a segment that runs over several pages."""
from __future__ import annotations

import difflib
import html
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "engine" / "data" / "kinh_dich" / "ntt"
HAN_FIXTURE = ROOT / "engine" / "tests" / "fixtures" / "zhouyi_han_segments.json"

# Mục lục of the book (printed pp.667-669): the name as the book prints it and the printed page where each quẻ starts.
TOC = [
    ("Kiền", 63), ("Khôn", 101), ("Truân", 120), ("Mông", 130), ("Nhu", 141), ("Tụng", 150), ("Sư", 160), ("Ty", 170),
    ("Tiểu Súc", 180), ("Lý", 189), ("Thái", 196), ("Bĩ", 206), ("Đồng Nhân", 213), ("Đại Hữu", 222), ("Khiêm", 230), ("Dự", 238),
    ("Tùy", 246), ("Cổ", 255), ("Lâm", 264), ("Quán", 272), ("Phệ hạp", 280), ("Bí", 289), ("Bác", 298), ("Phục", 305),
    ("Vô Vọng", 314), ("Đại Súc", 323), ("Di", 332), ("Đại Quá", 341), ("Tập Khảm", 349), ("Ly", 358), ("Hàm", 367), ("Hằng", 377),
    ("Độn", 386), ("Đại Tráng", 394), ("Tấn", 402), ("Minh Di", 410), ("Gia Nhân", 420), ("Khuê", 428), ("Kiển", 438), ("Giải", 447),
    ("Tổn", 457), ("Ích", 468), ("Quải", 479), ("Cấu", 490), ("Tụy", 500), ("Thăng", 511), ("Khốn", 518), ("Tỉnh", 529),
    ("Cách", 538), ("Đỉnh", 547), ("Chấn", 555), ("Cấn", 563), ("Tiệm", 571), ("Quy Muội", 579), ("Phong", 588), ("Lữ", 598),
    ("Tốn", 606), ("Đoái", 614), ("Hoán", 621), ("Tiết", 629), ("Trung Phu", 635), ("Tiểu Quá", 642), ("Ký Tế", 651), ("Vị Tế", 658),
]
LAST_PAGE = 665                                  # Vị Tế ends on p.665; p.666 is not in the scan, the Mục lục follows on p.667
NAME_HAN = ("乾 坤 屯 蒙 需 訟 師 比 小畜 履 泰 否 同人 大有 謙 豫 隨 蠱 臨 觀 噬嗑 賁 剝 復 无妄 大畜 頤 大過 坎 離 咸 恒 遯 大壯 晉 明夷 家人 睽 "
            "蹇 解 損 益 夬 姤 萃 升 困 井 革 鼎 震 艮 漸 歸妹 豐 旅 巽 兌 渙 節 中孚 小過 既濟 未濟").split()
LAYERS = ("han", "am", "nghia", "trinh_di", "chu_hy")
STANDARD_LABEL = {"am": "Dịch âm", "nghia": "Dịch nghĩa", "trinh_di": "Truyện của Trình Di", "chu_hy": "Bản nghĩa của Chu Hy",
                  "tien_nho": "Lời bàn của Tiên Nho"}
KINDS = {"intro", "thoan", "hao", "dung", "thoan_truyen", "dai_tuong", "tieu_tuong", "van_ngon", "unknown"}


# ---------------------------------------------------------------- page transcriptions -> segments

def read_pages(pages_dir: Path) -> dict[int, str]:
    out = {}
    for f in sorted(pages_dir.glob("p*.txt")):
        txt = f.read_text("utf-8").strip("\n")
        m = re.match(r"=== p\.(\d+)", txt)
        if not m or int(m.group(1)) != int(f.stem[1:]):
            raise ValueError(f"{f}: first line must be '=== p.{f.stem[1:]}'")
        out[int(m.group(1))] = txt
    return out


def _new_seg(kind: str, arg: str | None, page: int) -> dict:
    seg = {"kind": kind, "page": page, "page_end": page}
    if kind in ("hao", "tieu_tuong") and arg:
        if arg == "dung":
            seg["dung"] = True
        else:
            seg["hao"] = int(arg)
    return seg


def parse_pages(pages: dict[int, str]) -> tuple[list[dict], list[dict]]:
    """-> (blocks, notes): headings and segments in book order; segment layers hold lists of paragraphs"""
    blocks, notes = [], []
    seg = None
    layer = None          # (segment, key) of the running layer; key is a layer name or ('other', index)
    join_next = False     # '@cont <layer> join': the page's first line goes on with the previous page's paragraph

    def pars_of(key):
        return seg[key] if isinstance(key, str) else seg["other_commentary"][key[1]]["paragraphs"]

    def add(text: str):
        nonlocal join_next
        pars = pars_of(layer)
        if join_next and pars:
            pars[-1] = pars[-1].rstrip() + " " + text.strip()
        else:
            pars.append(text.strip())
        join_next = False

    for page in sorted(pages):
        fns = {}
        for raw in pages[page].split("\n")[1:]:
            line = raw.rstrip()
            if not line.strip():
                continue
            line = re.sub(r"\[\^(\d+)\]", lambda m: f"[^{page}.{m.group(1)}]", line)
            if not line.startswith("@"):
                if layer is None:
                    raise ValueError(f"p.{page}: text before any layer: {line[:60]}")
                seg["page_end"] = page
                add(line)
                continue
            tag, _, rest = line[1:].partition(" ")
            rest = rest.strip()
            if tag == "cont":
                name, _, j = rest.partition(" ")
                if seg is None:
                    raise ValueError(f"p.{page}: @cont with no running segment")
                layer = _layer_key(seg, name, None, cont=True)
                join_next = j.strip() == "join"
            elif tag == "heading":
                blocks.append({"heading": rest, "page": page})
            elif tag == "seg":
                kind, _, arg = rest.partition(" ")
                if kind not in KINDS:
                    raise ValueError(f"p.{page}: unknown kind {kind}")
                seg = _new_seg(kind, arg.strip() or None, page)
                blocks.append(seg)
                layer, join_next = None, False
            elif tag in ("han", "am", "nghia", "trinh_di", "chu_hy", "tien_nho", "other"):
                if seg is None:
                    raise ValueError(f"p.{page}: layer before @seg")
                label = None
                m = re.match(r"<<(.*?)>>\s*", rest)
                if m:
                    label, rest = m.group(1), rest[m.end():]
                seg["page_end"] = page
                layer, join_next = _layer_key(seg, tag, label), False
                if rest:
                    add(rest)
            elif tag == "fn":
                n, _, text = rest.partition(" ")
                fns[n] = text.strip()
            elif tag == "note":
                notes.append({"page": page, "note": rest})
            else:
                raise ValueError(f"p.{page}: unknown tag @{tag}")
        # a footnote belongs to the segment whose text carries its mark
        for n, text in fns.items():
            mark = f"[^{page}.{n}]"
            owner = next((b for b in reversed(blocks) if "kind" in b and mark in json.dumps(b, ensure_ascii=False)), None)
            if owner is None:
                owner = next((b for b in reversed(blocks) if "kind" in b), None)
                notes.append({"page": page, "note": f"footnote {n} has no mark in the text"})
            owner.setdefault("footnotes", []).append({"mark": f"{page}.{n}", "page": page, "text": text})
    return blocks, notes


def _layer_key(seg: dict, tag: str, label, cont: bool = False):
    if tag in ("tien_nho", "other"):
        oc = seg.setdefault("other_commentary", [])
        if cont:                                  # go on with the last commentary of that tag
            for i in range(len(oc) - 1, -1, -1):
                if oc[i]["tag"] == tag:
                    return ("other", i)
        oc.append({"tag": tag, "label": label if label is not None else STANDARD_LABEL.get(tag, ""), "paragraphs": []})
        seg.setdefault("order", []).append(f"other:{len(oc) - 1}")
        return ("other", len(oc) - 1)
    if label is not None:
        seg.setdefault("labels", {})[tag] = label
    if tag not in seg:
        seg[tag] = []
        seg.setdefault("order", []).append(tag)
    return tag


# ---------------------------------------------------------------- segments -> quẻ files

def split_by_que(blocks: list[dict]) -> dict[int, dict]:
    """a quẻ starts at its '@heading QUẺ …' line; the TOC order gives its number"""
    ques, cur = {}, None
    names = [n for n, _ in TOC]
    for b in blocks:
        if "heading" in b and b["heading"].upper().startswith("QUẺ "):
            title = b["heading"][4:].strip()
            n = _match_name(title, names)
            cur = {"number": n, "name_vi": names[n - 1], "name_han": NAME_HAN[n - 1], "heading": [b["heading"]],
                   "segments": [], "pages": [b["page"], b["page"]]}
            ques[n] = cur
            continue
        if cur is None:
            continue
        if "heading" in b:
            cur["heading"].append(b["heading"])
            continue
        cur["segments"].append(b)
        cur["pages"][1] = max(cur["pages"][1], b["page_end"])
    return ques


def _match_name(title: str, names: list[str]) -> int:
    key = lambda s: unicodedata.normalize("NFC", s).upper().replace("Ỵ", "Y").replace("Ý", "Y")
    for i, n in enumerate(names):
        if key(n) == key(title):
            return i + 1
    raise ValueError(f"heading 'QUẺ {title}' matches no quẻ of the Mục lục")


def finish_segment(seg: dict) -> dict:
    out = {"kind": seg["kind"]}
    for k in ("hao", "dung"):
        if k in seg:
            out[k] = seg[k]
    for k in LAYERS:
        if k in seg:
            out[k] = "\n".join(seg[k])
    if seg.get("other_commentary"):
        out["other_commentary"] = [{"label": oc["label"], "text": "\n".join(oc["paragraphs"])} for oc in seg["other_commentary"]]
    if seg.get("labels"):
        out["printed_labels"] = seg["labels"]
    if seg.get("footnotes"):
        out["footnotes"] = seg["footnotes"]
    out["order"] = seg.get("order", [])
    out["page"] = seg["page"]
    if seg["page_end"] != seg["page"]:
        out["page_end"] = seg["page_end"]
    return out


def assemble(pages_dir: Path) -> None:
    pages = read_pages(pages_dir)
    blocks, notes = parse_pages(pages)
    ques = split_by_que(blocks)
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "pages.txt", "w", encoding="utf-8") as f:
        for p in sorted(pages):
            f.write(pages[p].rstrip("\n") + "\n\n")
    for n, q in sorted(ques.items()):
        old = OUT / f"{n}.json"
        status = {}
        if old.exists():                       # keep the check results of an earlier run (recomputed by `check`)
            prev = json.loads(old.read_text("utf-8"))
            status = {i: s.get("status") for i, s in enumerate(prev["segments"]) if s.get("status")}
        doc = {"number": n, "name_vi": q["name_vi"], "name_han": q["name_han"], "source": "KD", "translator": "Ngô Tất Tố",
               "heading": q["heading"], "pages": q["pages"], "segments": [finish_segment(s) for s in q["segments"]]}
        for i, s in enumerate(doc["segments"]):
            if i in status:
                s["status"] = status[i]
        (OUT / f"{n}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(f"{len(pages)} pages, {len(ques)} quẻ: {sorted(ques)}")
    for n in notes:
        print(f"  note p.{n['page']}: {n['note']}")


# ---------------------------------------------------------------- vi.wikisource -> the same shape (for the CER check)

WIKI_LABELS = {"Dịch âm": "am", "Dịch nghĩa": "nghia", "Truyện của Trình Di": "trinh_di", "Bản nghĩa của Chu Hy": "chu_hy"}


def wiki_clean(s: str) -> str:
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"\[\[(?:Hình|File|Tập tin):[^\]]*\]\]", "[hình]", s)
    for _ in range(3):
        s = re.sub(r"\{\{(?:tooltip|khác|g|gc)\|([^{}|]*)(?:\|[^{}]*)?\}\}", r"\1", s)
    s = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("'''", "").replace("''", "")
    return html.unescape(s).strip()


def wiki_refs(s: str) -> list[str]:
    return [wiki_clean(r) for r in re.findall(r"<ref[^>]*>(.*?)</ref>", s, flags=re.S)]


def parse_wiki(raw: str) -> list[dict]:
    body = raw.split("}}", 1)[1]
    segs, cur, key = [], None, None
    lines = body.split("\n")
    i = 0
    while i < len(lines):
        ln = lines[i].strip()
        i += 1
        if not ln or ln.startswith(("{|", "|", "{{clr", "----", "<div", "</div")) or ln == "{{g|GIẢI NGHĨA}}":
            continue
        if ln.startswith("{{g|LỜI KINH"):
            block = ln
            while "}}" not in block[len("{{g|LỜI KINH"):] and i < len(lines):
                block += "\n" + lines[i]
                i += 1
            han = block[len("{{g|LỜI KINH"):]
            han = han[: han.rfind("}}")]
            cur = {"han": [wiki_clean(han)], "order": ["han"], "refs": []}
            segs.append(cur)
            key = "han"
            continue
        if ln.startswith("{{g|"):
            if cur is None and not segs:             # quẻ title before the intro
                continue
            continue
        m = re.match(r"'''([^']+?)\.?\s*-\s*'''\s*(.*)", ln)
        if m:
            label = m.group(1).strip().rstrip(".")
            text = m.group(2)
            if cur is None:
                cur = {"order": [], "refs": []}
                segs.append(cur)
            k = WIKI_LABELS.get(label)
            if k:
                cur.setdefault(k, [])
                if k not in cur["order"]:
                    cur["order"].append(k)
                key = k
            else:
                cur.setdefault("other_commentary", []).append({"label": label, "paragraphs": []})
                key = ("other", len(cur["other_commentary"]) - 1)
            cur["refs"] += wiki_refs(text)
            _wiki_add(cur, key, wiki_clean(text))
            continue
        if cur is not None and key is not None:
            cur["refs"] += wiki_refs(ln)
            _wiki_add(cur, key, wiki_clean(ln))
    out = []
    for s in segs:
        o = {k: "\n".join(s[k]) for k in LAYERS if k in s}
        if s.get("other_commentary"):
            o["other_commentary"] = [{"label": c["label"], "text": "\n".join(c["paragraphs"])} for c in s["other_commentary"]]
        o["footnotes"] = [{"text": r} for r in s["refs"]]
        out.append(o)
    return out


def _wiki_add(cur, key, text):
    if not text:
        return
    if isinstance(key, str):
        cur.setdefault(key, []).append(text)
    else:
        cur["other_commentary"][key[1]]["paragraphs"].append(text)


def wiki(wiki_dir: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in sorted(wiki_dir.glob("vi_*.wiki")):
        n = int(f.stem[3:])
        segs = parse_wiki(f.read_text("utf-8"))
        (out_dir / f"{n}.json").write_text(json.dumps({"number": n, "segments": segs}, ensure_ascii=False, indent=1), "utf-8")
        print(n, len(segs), "segments")


# ---------------------------------------------------------------- character error rate

TONES = {"\u0300", "\u0301", "\u0303", "\u0309", "\u0323"}


def norm_vi(s: str, tone_free_place: bool = True) -> str:
    """for comparison only: footnote marks, drawings and formatting out; quotes and dashes unified; whitespace collapsed; with
    tone_free_place the tone mark of each word is moved to its end (old 'hoà/suý' vs new 'hòa/súy' placement is a convention, not a reading)"""
    s = re.sub(r"\[\^[\d.]+\]", "", s)
    s = re.sub(r"\[hình[^\]]*\]", "", s)
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").replace("…", "...")
    s = re.sub(r"[–—-]", "-", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = unicodedata.normalize("NFD", s)
    if tone_free_place:
        def mv(m):
            w = m.group(0)
            t = "".join(c for c in w if c in TONES)
            return "".join(c for c in w if c not in TONES) + t
        s = re.sub(r"\w+", mv, s)
    return unicodedata.normalize("NFC", s)


def levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def edit_distance(a: str, b: str) -> tuple[int, list[tuple[str, str]]]:
    """difflib alignment, exact Levenshtein inside each differing stretch -> (distance, differing stretches)"""
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    d, diffs = 0, []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        x, y = a[i1:i2], b[j1:j2]
        d += levenshtein(x, y) if x and y and len(x) * len(y) < 4_000_000 else max(len(x), len(y))
        diffs.append((a[max(0, i1 - 25):i2 + 25], b[max(0, j1 - 25):j2 + 25]))
    return d, diffs


def layer_text(doc: dict, layer: str) -> str:
    parts = []
    for s in doc["segments"]:
        if layer == "other":
            parts += [c["text"] for c in s.get("other_commentary", [])]
        elif layer == "footnotes":
            parts += [f["text"] for f in s.get("footnotes", [])]
        elif s.get(layer):
            parts.append(s[layer])
    return "\n".join(parts)


def cer(a_dir: Path, b_dir: Path, numbers: list[int], layers=("am", "nghia", "trinh_di", "chu_hy", "other", "footnotes"),
        show: int = 0) -> dict:
    """a = reference (Wikisource / first pass), b = transcription; CER = edit distance / reference length"""
    res = {}
    for layer in layers:
        tot = dist = 0
        for n in numbers:
            a = norm_vi(layer_text(json.loads((a_dir / f"{n}.json").read_text("utf-8")), layer))
            b = norm_vi(layer_text(json.loads((b_dir / f"{n}.json").read_text("utf-8")), layer))
            d, diffs = edit_distance(a, b)
            tot += len(a)
            dist += d
            for x, y in diffs[:show]:
                print(f"  [{n} {layer}] A: {x!r}\n  {' ' * len(str(n))}  B: {y!r}")
        res[layer] = {"chars": tot, "edits": dist, "cer": round(dist / tot, 5) if tot else None}
    return res


# ---------------------------------------------------------------- Hán check against zh.wikisource 周易

VARIANTS = str.maketrans({"无": "無", "爲": "為", "衆": "眾", "羣": "群", "脩": "修", "恒": "恆", "旣": "既", "卽": "即", "敎": "教",
                          "説": "說", "兊": "兌", "吿": "告", "竝": "並", "潜": "潛", "啓": "啟", "麤": "粗", "猶": "猶", "於": "於",
                          "眞": "真", "內": "内", "嶮": "險", "隂": "陰", "陽": "陽", "徳": "德", "飮": "飲", "淸": "清", "禮": "禮",
                          "跡": "迹", "蹟": "迹", "寧": "寧", "甯": "寧", "强": "強", "嘗": "嘗", "鄕": "鄉", "冝": "宜", "叙": "敘",
                          "敍": "敘", "况": "況", "凖": "準", "从": "從", "歎": "嘆", "鈎": "鉤", "穉": "稚", "敺": "驅", "毘": "毗",
                          "牀": "床", "噐": "器", "惪": "德", "温": "溫", "䘮": "喪", "尙": "尚", "黃": "黃", "吳": "吳", "戶": "戶"})
HAN_PUNCT = re.compile(r"[\s,.:;!?，。：；！？、「」『』“”\"'()（）\[\]…·\-]")


def norm_han(s: str) -> str:
    s = re.sub(r"\[\?\]", "?", s)
    return HAN_PUNCT.sub("", unicodedata.normalize("NFKC", s)).translate(VARIANTS)


def han_reference() -> dict[int, list[dict]]:
    return {h["number"]: h["segments"] for h in json.loads(HAN_FIXTURE.read_text("utf-8"))["hexagrams"]}


def seg_key(s: dict):
    if s["kind"] in ("hao", "tieu_tuong"):
        return (s["kind"], "dung" if s.get("dung") else s.get("hao"))
    return (s["kind"], None)


LABEL_PREFIX = re.compile(r"^(?:彖曰|象曰|文言曰|(?:初|上)[六九]|[六九][二三四五]|用[六九])")


def han_check(doc: dict, ref: list[dict]) -> dict:
    """compare the concatenated Hán of every (kind, hao) group; -> {key: (ok, book, reference)}"""
    book: dict = {}
    for s in doc["segments"]:
        if s["kind"] == "intro":
            continue
        book.setdefault(seg_key(s), []).append(s.get("han", ""))
    want: dict = {}
    for s in ref:
        txt = s["text"]
        if s["kind"] == "van_ngon":
            txt = txt.replace("\n:\n", "\n")
        want.setdefault(seg_key(s), []).append(txt)
    out = {}
    for k in set(book) | set(want):
        b = norm_han("".join(book.get(k, [])))
        w = norm_han("".join(want.get(k, [])))
        b_cmp = _strip_labels(b, k)
        w_cmp = _strip_labels(w, k)
        if k[0] == "thoan":
            w_cmp = w_cmp[len(norm_han(doc["name_han"]).translate(VARIANTS)):] if w_cmp.startswith(norm_han(doc["name_han"])) else w_cmp
            b_cmp = b_cmp[len(norm_han(doc["name_han"])):] if b_cmp.startswith(norm_han(doc["name_han"])) else b_cmp
        ok = b_cmp == w_cmp or ("?" in b_cmp and len(b_cmp) == len(w_cmp)
                                and all(x == y or x == "?" for x, y in zip(b_cmp, w_cmp)))
        out[k] = (ok, b_cmp, w_cmp)
    return out


def _strip_labels(s: str, k) -> str:
    # the book prints 彖曰/象曰/初九… inside LỜI KINH; the reference has them as structure
    s = re.sub(r"(彖曰|象曰|文言曰)", "", s)
    if k[0] in ("hao", "dung"):
        s = re.sub(r"^((?:初|上)[六九]|[六九][二三四五]|用[六九])", "", s)
    return s


def han(numbers=None) -> int:
    ref = han_reference()
    bad = 0
    for f in sorted(OUT.glob("[0-9]*.json"), key=lambda p: int(p.stem)):
        doc = json.loads(f.read_text("utf-8"))
        if numbers and doc["number"] not in numbers:
            continue
        for k, (ok, b, w) in sorted(han_check(doc, ref[doc["number"]]).items(), key=str):
            if not ok:
                bad += 1
                print(f"{doc['number']} {k}: book {b}\n{' ' * len(str(doc['number']))} {' ' * len(str(k))}  ref  {w}")
    print("mismatching groups:", bad)
    return bad


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "assemble":
        assemble(Path(args[0]))
    elif cmd == "wiki":
        wiki(Path(args[0]), Path(args[1]))
    elif cmd == "cer":
        r = cer(Path(args[0]), Path(args[1]), [int(x) for x in args[2:] if x.isdigit()], show=int(next(
            (a.split("=")[1] for a in args if a.startswith("--show=")), 0)))
        print(json.dumps(r, indent=1))
    elif cmd == "han":
        han([int(x) for x in args] or None)
