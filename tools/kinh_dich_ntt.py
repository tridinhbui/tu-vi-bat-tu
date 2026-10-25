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
                if tag == "han" and seg.get("han") and len(seg.get("order", [])) > 1:
                    # a second LỜI KINH under one @seg (a transcriber kept several Thoán truyện blocks together): one block, one segment
                    seg = _new_seg(seg["kind"], None, page) | {k: seg[k] for k in ("hao", "dung") if k in seg}
                    blocks.append(seg)
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
            if n == "cont":                       # the bottom of this page goes on with the previous page's last footnote
                last = next(b for b in reversed(blocks) if b.get("footnotes"))["footnotes"][-1]
                last["text"] = last["text"].rstrip() + " " + text
                last["page_end"] = page
                continue
            marks = [f"[^{page}.{m}]" for m in n.split(",")]
            owner = next((b for b in reversed(blocks) if "kind" in b and any(m in json.dumps(b, ensure_ascii=False) for m in marks)), None)
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
    key = lambda s: unicodedata.normalize("NFC", s).upper()
    for i, n in enumerate(names):
        if key(n) == key(title):
            return i + 1
    for i, n in enumerate(names):                 # the heading of quẻ 8 is printed "QUẺ TỴ" (the Mục lục has "Ty")
        if key(n) == key(title).replace("Ỵ", "Y"):
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


def assemble(pages_dir: Path, out: Path = OUT) -> None:
    pages = read_pages(pages_dir)
    blocks, notes = parse_pages(pages)
    ques = split_by_que(blocks)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "pages.txt", "w", encoding="utf-8") as f:
        for p in sorted(pages):
            f.write(pages[p].rstrip("\n") + "\n\n")
    for n, q in sorted(ques.items()):
        old = out / f"{n}.json"
        status = {}
        if old.exists():                       # keep the check results of an earlier run (recomputed by `check`)
            prev = json.loads(old.read_text("utf-8"))
            status = {i: s.get("status") for i, s in enumerate(prev["segments"]) if s.get("status")}
        doc = {"number": n, "name_vi": q["name_vi"], "name_han": q["name_han"], "source": "KD", "translator": "Ngô Tất Tố",
               "heading": q["heading"], "pages": q["pages"], "segments": [finish_segment(s) for s in q["segments"]]}
        for i, s in enumerate(doc["segments"]):
            if i in status:
                s["status"] = status[i]
        (out / f"{n}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", "utf-8")
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
    s = re.sub(r"\{\{[^{}]*\}\}", "", s)
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
                cur["order"].append(f"other:{key[1]}")
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
        o["order"] = s["order"]
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


def segment_text(s: dict) -> str:
    """the Vietnamese text of a segment in book order, whatever layer each paragraph was filed under (Hán and footnotes left out)"""
    parts = []
    for key in s.get("order", []):
        if key.startswith("other:"):
            parts.append(s["other_commentary"][int(key[6:])]["text"])
        elif key != "han" and s.get(key):
            parts.append(s[key])
    return "\n".join(parts)


def layer_text(doc: dict, layer: str) -> str:
    parts = []
    for s in doc["segments"]:
        if layer == "all":
            parts.append(segment_text(s))
        elif layer == "other":
            parts += [c["text"] for c in s.get("other_commentary", [])]
        elif layer == "footnotes":
            parts += [f["text"] for f in s.get("footnotes", [])]
        elif s.get(layer):
            parts.append(s[layer])
    return "\n".join(parts)


def cer(a_dir: Path, b_dir: Path, numbers: list[int], layers=("all", "am", "nghia", "trinh_di", "chu_hy", "other", "footnotes"),
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


def seg_diffs(a_dir: Path, b_dir: Path, numbers: list[int], layers=("am", "nghia", "trinh_di", "chu_hy", "other", "footnotes")):
    """segment-by-segment differences (segments paired in book order; the counts must agree) with the page of b's segment"""
    out = []
    for n in numbers:
        A = json.loads((a_dir / f"{n}.json").read_text("utf-8"))["segments"]
        B = json.loads((b_dir / f"{n}.json").read_text("utf-8"))["segments"]
        if len(A) != len(B):
            out.append({"n": n, "error": f"segment count {len(A)} vs {len(B)}"})
            continue
        for i, (sa, sb) in enumerate(zip(A, B)):
            for layer in layers:
                a = norm_vi(layer_text({"segments": [sa]}, layer))
                b = norm_vi(layer_text({"segments": [sb]}, layer))
                sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
                for op, i1, i2, j1, j2 in sm.get_opcodes():
                    if op != "equal":
                        out.append({"n": n, "seg": i, "kind": list(seg_key(sb)), "layer": layer, "pages": [sb["page"], sb.get("page_end", sb["page"])],
                                    "ref": a[i1:i2], "ours": b[j1:j2], "ref_ctx": a[max(0, i1 - 30):i2 + 30], "ours_ctx": b[max(0, j1 - 30):j2 + 30]})
    return out


def gate(numbers: list[int], work: Path) -> dict:
    """transcription error rate on the Wikisource quẻ after looking at the print: of the places where our text differs from Wikisource,
    those where the print agrees with Wikisource ('ref') or with neither are our errors; '[?]' marks are counted apart"""
    out = {"chars": 0, "errors": 0, "uncertain_marks": 0, "unclear": 0, "edition_differences": 0}
    for n in numbers:
        docs = [json.loads((work / "wikijson" / f"{n}.json").read_text("utf-8"))]
        out["chars"] += len(norm_vi(layer_text(docs[0], "all")))
        diffs, verdicts = [], []
        for part in ("", "a", "b"):
            f = work / f"diffs{n}{part}.json"
            if f.exists() and (work / "adjud" / f"{n}{part}.json").exists() and (part or not (work / f"diffs{n}a.json").exists()):
                diffs += [json.loads(f.read_text("utf-8"))]
                verdicts += [json.loads((work / "adjud" / f"{n}{part}.json").read_text("utf-8"))]
        for d, v in zip(diffs, verdicts):
            for x in v:
                item = d[x["i"]]
                if "[?]" in item["ours"]:
                    out["uncertain_marks"] += item["ours"].count("[?]")
                elif x["verdict"] in ("ref", "neither"):
                    out["errors"] += levenshtein(item["ref"], item["ours"]) if item["layer"] != "other" or item["ref"] and item["ours"] else 0
                elif x["verdict"] == "unclear":
                    out["unclear"] += 1
                else:
                    out["edition_differences"] += 1
    out["cer"] = round(out["errors"] / out["chars"], 5)
    return out


# ---------------------------------------------------------------- Hán check against zh.wikisource 周易

# glyph variants of one character (異體字), mapped to the form zh.wikisource uses; for comparison only, the stored text keeps the print.
# Different characters (車/轝, 祐/佑, 弗/不 …) are NOT here: where the book prints one, it is recorded in ntt/misprints.json.
VARIANTS = str.maketrans({"无": "無", "爲": "為", "衆": "眾", "羣": "群", "恒": "恆", "旣": "既", "卽": "即", "敎": "教", "説": "說",
                          "兊": "兌", "吿": "告", "竝": "並", "潜": "潛", "啓": "啟", "眞": "真", "內": "内", "隂": "陰", "徳": "德",
                          "飮": "飲", "淸": "清", "强": "強", "鄕": "鄉", "冝": "宜", "敍": "敘", "况": "況", "凖": "準", "温": "溫",
                          "䘮": "喪", "尙": "尚", "黄": "黃", "静": "靜", "弑": "弒", "劳": "勞", "户": "戶", "戸": "戶", "晋": "晉",
                          "盗": "盜", "衞": "衛", "既": "既", "顛": "顚", "床": "牀", "麤": "麁", "畧": "略", "汙": "污", "峯": "峰",
                          "脩": "修", "疇": "疇", "畴": "疇", "彊": "強", "沈": "沉", "於": "於", "効": "效", "虚": "虛", "冰": "冰",
                          "絶": "絕", "麽": "麼", "鉤": "鈎", "旡": "無", "亯": "享", "鷄": "雞", "雚": "雚", "牆": "墻", "墙": "墻"})
HAN_PUNCT = re.compile(r"[\s,.:;!?，。：；！？、「」『』“”\"'()（）\[\]…·\-]")


def norm_han(s: str) -> str:
    s = s.replace("[?]", "〓")                            # an unreadable character stays one character
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
        ok = b_cmp == w_cmp
        out[k] = (ok, b_cmp, w_cmp)
    return out


def _strip_labels(s: str, k) -> str:
    # the book prints 彖曰/象曰/初九… inside LỜI KINH; the reference has them as structure
    s = re.sub(r"(彖曰|象曰|文言曰)", "", s)
    if k[0] in ("hao", "dung"):
        s = re.sub(r"^((?:初|上)[六九]|[六九][二三四五]|用[六九])", "", s)
    return s


def han_diffs(doc: dict, ref: list[dict]) -> list[dict]:
    """character-level differences of every mismatching (kind, hao) group, each placed on the segment (and page) where it falls"""
    out = []
    for key, (ok, _b, _w) in han_check(doc, ref).items():
        if ok:
            continue
        segs = [s for s in doc["segments"] if s["kind"] != "intro" and seg_key(s) == key]
        chars, owner = [], []
        for s in segs:
            t = _strip_labels(norm_han(s.get("han", "")), key)
            chars.append(t)
            owner += [s] * len(t)
        book = "".join(chars)
        want = _strip_labels(norm_han("".join((r["text"].replace("\n:\n", "\n") for r in ref if seg_key(r) == key))), key)
        if key[0] == "thoan":
            nm = norm_han(doc["name_han"])
            book, owner = (book[len(nm):], owner[len(nm):]) if book.startswith(nm) else (book, owner)
            want = want[len(nm):] if want.startswith(nm) else want
        sm = difflib.SequenceMatcher(None, book, want, autojunk=False)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "equal":
                continue
            s = owner[min(i1, len(owner) - 1)] if owner else (segs[0] if segs else None)
            out.append({"n": doc["number"], "kind": key[0], "hao": key[1], "page": s["page"] if s else None,
                        "page_end": s.get("page_end", s["page"]) if s else None, "han_printed_line": s.get("han", "") if s else "",
                        "ours": book[i1:i2], "ref": want[j1:j2], "ours_ctx": book[max(0, i1 - 6):i2 + 6], "ref_ctx": want[max(0, j1 - 6):j2 + 6]})
    return out


def page_compare_text(txt: str) -> str:
    """a page transcription for comparing two transcribers: notes dropped, tags kept (they carry the structure), text normalised"""
    lines = [ln for ln in txt.split("\n")[1:] if ln.strip() and not ln.startswith("@note")]
    return "\n".join(norm_vi(ln) for ln in lines)


def pass2_diffs(work: Path) -> list[dict]:
    """check (c): differences between the first and the independent second transcription of the sampled pages"""
    out = []
    for f in sorted((work / "pass2").glob("p*.txt"), key=lambda p: int(p.stem[1:])):
        page = int(f.stem[1:])
        a = page_compare_text((work / "pass1" / f.name).read_text("utf-8"))
        b = page_compare_text(f.read_text("utf-8"))
        sm = difflib.SequenceMatcher(None, b, a, autojunk=False)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op != "equal":
                out.append({"page": page, "pages": [page, page], "layer": "page", "ref": b[i1:i2], "ours": a[j1:j2],
                            "ref_ctx": b[max(0, i1 - 30):i2 + 30], "ours_ctx": a[max(0, j1 - 30):j2 + 30]})
    return out


def structure_problems(doc: dict) -> list[str]:
    """check (b): 6 hào and 6 tiểu tượng, a lời quẻ, Thoán truyện and Đại tượng; dụng / Văn ngôn only in Kiền and Khôn"""
    import collections
    c = collections.Counter(seg_key(s) for s in doc["segments"])
    # one hào text or tiểu tượng may be printed as several LỜI KINH blocks (e.g. Phong tiểu tượng 4, p.595)
    out = [f"{k} {h}: none" for k in ("hao", "tieu_tuong") for h in range(1, 7) if not c[(k, h)]]
    out += [f"{k}: none" for k in ("thoan", "thoan_truyen", "dai_tuong") if not c[(k, None)]]
    special = c[("dung", None)] + c[("tieu_tuong", "dung")] + c[("van_ngon", None)]
    if doc["number"] in (1, 2):
        out += [f"{k}: none" for k in (("dung", None), ("tieu_tuong", "dung"), ("van_ngon", None)) if not c[k]]
    elif special:
        out.append("dụng / Văn ngôn outside Kiền and Khôn")
    if c[("unknown", None)]:
        out.append("unknown block")
    if [s["page"] for s in doc["segments"]] != sorted(s["page"] for s in doc["segments"]):
        out.append("pages not in order")
    return out


def finalize(work: Path, out: Path = OUT) -> None:
    """write the checked quẻ: every quẻ whose pages are all transcribed; a segment is 'verified' when (a) its Hán matches 周易 or every
    difference was seen on the print (ntt/misprints.json), (b) its quẻ has the full structure, it has no [?], and any of its pages in
    the second-transcription sample agrees after the differences were settled on the image"""
    pages = read_pages(work / "pass1")
    blocks, _notes = parse_pages(pages)
    ques = split_by_que(blocks)
    seen = {}                                                     # (n, kind, hao, ours, ref) -> verdict on the print
    for f in sorted(work.glob("handiffs_*.json")):
        v = work / "adjud" / f"han_{f.stem.split('_', 1)[1]}.json"
        if not v.exists():
            continue
        items = json.loads(f.read_text("utf-8"))
        for x in json.loads(v.read_text("utf-8")):
            it = items[x["i"]]
            seen[(it["n"], it["kind"], str(it["hao"]), it["ours"], it["ref"])] = x
    absent = json.loads((work / "absent.json").read_text("utf-8")) if (work / "absent.json").exists() else []
    sample = [int(x) for x in (work / "sample_pass2.txt").read_text().split()]
    pass2 = json.loads((work / "pass2_result.json").read_text("utf-8")) if (work / "pass2_result.json").exists() else {}
    ref = han_reference()
    misprints, written = [], []
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "pages.txt", "w", encoding="utf-8") as f:
        for p in sorted(pages):
            f.write(pages[p].rstrip("\n") + "\n\n")
    for n, q in sorted(ques.items()):
        first = TOC[n - 1][1]
        last = TOC[n][1] if n < 64 else LAST_PAGE
        if any(p not in pages for p in range(first, last + 1) if p not in (365, 366)):
            continue
        doc = {"number": n, "name_vi": q["name_vi"], "name_han": q["name_han"], "source": "KD", "translator": "Ngô Tất Tố",
               "heading": q["heading"], "pages": q["pages"], "segments": [finish_segment(s) for s in q["segments"]]}
        struct = structure_problems(doc)
        han_open = {}
        for key, (ok, b, w) in han_check(doc, ref[n]).items():
            if ok:
                continue
            diffs = [d for d in han_diffs(doc, ref[n]) if (d["kind"], d["hao"]) == key]
            verdicts = [seen.get((n, d["kind"], str(d["hao"]), d["ours"], d["ref"])) for d in diffs]
            if diffs and all(v and v["verdict"] == "ours" for v in verdicts):
                misprints.append({"number": n, "kind": key[0], "hao": key[1], "book": b, "reference": w,
                                  "differences": [{"page": d["page"], "book": d["ours"], "zhouyi": d["ref"], "print": v["print"]}
                                                  for d, v in zip(diffs, verdicts)], "checked": "seen on the page image"})
            else:
                han_open[key] = [v["verdict"] if v else "not yet checked" for v in verdicts]
        for s in doc["segments"]:
            for a in absent:
                if (a["number"], a["kind"], a.get("hao"), a["page"]) == (n, s["kind"], s.get("hao"), s["page"]) \
                        and s.get("han", "").startswith(a.get("han_starts", "")):
                    s["absent"] = a["layers"]
            why = []
            if struct:
                why.append("structure: " + "; ".join(struct))
            if seg_key(s) in han_open:
                why.append("Hán differs from 周易 and the difference is not settled on the print")
            if "[?]" in json.dumps(s, ensure_ascii=False):
                why.append("has unreadable characters [?]")
            for p in range(s["page"], s.get("page_end", s["page"]) + 1):
                if p in sample and pass2.get(str(p)) != "agree":
                    why.append(f"p.{p} is in the second-transcription sample and its differences are not settled")
            s["status"] = "unverified" if why else "verified"
            if why:
                s["status_reason"] = why
        (out / f"{n}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", "utf-8")
        written.append(n)
    (out / "misprints.json").write_text(json.dumps({"note": "Hán of LỜI KINH lines where this printing differs from zh.wikisource 周易, "
        "each difference seen on the page image; the transcription keeps the print", "han": misprints}, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print("written:", written)


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
        assemble(Path(args[0]), Path(args[1]) if len(args) > 1 else OUT)
    elif cmd == "wiki":
        wiki(Path(args[0]), Path(args[1]))
    elif cmd == "cer":
        r = cer(Path(args[0]), Path(args[1]), [int(x) for x in args[2:] if x.isdigit()], show=int(next(
            (a.split("=")[1] for a in args if a.startswith("--show=")), 0)))
        print(json.dumps(r, indent=1))
    elif cmd == "diffs":
        d = seg_diffs(Path(args[0]), Path(args[1]), [int(x) for x in args[3:]])
        Path(args[2]).write_text(json.dumps(d, ensure_ascii=False, indent=1), "utf-8")
        print(len(d), "differences")
    elif cmd == "gate":
        print(json.dumps(gate([int(x) for x in args[1:]], Path(args[0])), indent=1))
    elif cmd == "handiffs":
        ref, out = han_reference(), []
        src = Path(args[0])
        for f in sorted(src.glob("[0-9]*.json"), key=lambda p: int(p.stem)):
            doc = json.loads(f.read_text("utf-8"))
            if args[2:] and str(doc["number"]) not in args[2:]:
                continue
            out += han_diffs(doc, ref[doc["number"]])
        Path(args[1]).write_text(json.dumps(out, ensure_ascii=False, indent=1), "utf-8")
        print(len(out), "Hán differences")
    elif cmd == "pass2diffs":
        d = pass2_diffs(Path(args[0]))
        Path(args[1]).write_text(json.dumps(d, ensure_ascii=False, indent=1), "utf-8")
        chars = sum(len(page_compare_text(f.read_text("utf-8"))) for f in (Path(args[0]) / "pass2").glob("p*.txt"))
        print(len(d), "differences on", len(list((Path(args[0]) / "pass2").glob("p*.txt"))), "pages,", chars, "chars")
    elif cmd == "finalize":
        finalize(Path(args[0]))
    elif cmd == "han":
        han([int(x) for x in args] or None)
