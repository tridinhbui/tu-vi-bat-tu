"""The texts of a quẻ, layer by layer: Hán (WEB:zh_zhouyi, engine/data/kinh_dich/zhouyi_han.json) and Ngô Tất Tố's dịch âm, dịch nghĩa,
Truyện of Trình Di, Bản nghĩa of Chu Hy and lời bàn of tiên nho (engine/data/kinh_dich/ntt/<n>.json, transcribed from the scan or taken from
Wikisource).

Ngô Tất Tố's segments are matched to the Hán segments by their Hán text, not by position: quẻ Kiền prints its seven hào before the Thoán and
the Tượng, the other quẻ interleave each hào with its Tiểu tượng, and the Thoán truyện is often split into several blocks."""
from __future__ import annotations

import json
import os
import re
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data" / "kinh_dich"
LAYERS = ("am", "nghia", "trinh_di", "chu_hy", "tien_nho")

# variant characters the two editions write differently (Wikisource 周易 vs the Hán printed in Ngô Tất Tố)
VARIANTS = str.maketrans({"無": "无", "潜": "潛", "黄": "黃", "羣": "群", "衆": "眾", "恆": "恒", "説": "說", "爲": "為", "眞": "真",
                          "於": "于", "躍": "躍", "裏": "裡", "强": "強", "倂": "併", "隂": "陰", "陽": "陽", "旣": "既", "卽": "即",
                          "吿": "告", "敎": "教", "淸": "清", "內": "内", "牀": "床", "鉉": "鉉"})


def norm_han(s: str) -> str:
    s = s.translate(VARIANTS)
    s = re.sub(r"^(彖曰|象曰|文言曰|初[九六]|[九六][二三四五]|上[九六]|用[九六])\s*[:：，,]?", "", s.strip())
    return re.sub(r"[^㐀-鿿]", "", s)


@lru_cache(maxsize=None)
def han_kb() -> dict:
    return {q["number"]: q for q in json.loads((DATA / "zhouyi_han.json").read_text("utf-8"))["hexagrams"]}


def ntt_dir() -> Path:
    return Path(os.environ.get("TVBT_KD_NTT_DIR") or DATA / "ntt")


def seg_key(s: dict) -> str:
    if s["kind"] in ("hao", "tieu_tuong") and "hao" in s:
        return f"{s['kind']}{s['hao']}"
    if s["kind"] == "tieu_tuong" and s.get("dung"):
        return "tieu_tuong_dung"
    return s["kind"]


def coverage(x: str, y: str) -> float:
    """Share of the characters of x found, in order, in y (the editions differ by a character here and there: 盤 / 磐, 户 / 戶)."""
    if not x:
        return 0.0
    return sum(b.size for b in SequenceMatcher(None, x, y, autojunk=False).get_matching_blocks()) / len(x)


def _match(han_segments: list[dict], ntt_han: str, start: int) -> int | None:
    """Index of the Hán segment this Ngô Tất Tố block belongs to: the best coverage of the block's Hán (at least 0.75), ties going to the
    first segment from `start` on, since the book keeps the canonical order within a quẻ."""
    x = norm_han(ntt_han)
    if len(x) < 2:
        return None
    order = list(range(start, len(han_segments))) + list(range(0, start))
    # the block's own heading narrows the kind: a short hào text (履霜，堅冰至) is also found inside its Tiểu tượng
    head = ntt_han.strip().translate(VARIANTS)
    label = re.match(r"(初[九六]|[九六][二三四五]|上[九六]|用[九六])\s*([:：,，])", head)
    if label:
        # '初六: 履霜…' is the hào; Kiền prints its Tiểu tượng lines with the label too ('用九, 天德不可為首也'): the hào first, then its
        # Tiểu tượng, whichever covers the block
        lab = label.group(1)
        pos = None if lab.startswith("用") else ("初二三四五上".index(lab[0] if lab[0] in "初上" else lab[1]) + 1)
        same = lambda s: (s.get("dung") or s["kind"] == "dung") if pos is None else s.get("hao") == pos
        first = [i for i in order if han_segments[i]["kind"] in ("hao", "dung") and same(han_segments[i])]
        then = [i for i in order if han_segments[i]["kind"] == "tieu_tuong" and same(han_segments[i])]
        for group in (first, then):
            for i in group:
                if coverage(x, norm_han(han_segments[i]["text"])) >= 0.75:
                    return i
        # a short hào text where the editions differ by a character (振恆，凶 / 震恆，凶): the label already names the hào
        return next((i for i in first if coverage(x, norm_han(han_segments[i]["text"])) >= 0.5), None)
    if re.match(r"(初[九六]|[九六][二三四五]|上[九六]|用[九六])", head):
        order = [i for i in order if han_segments[i]["kind"] == "van_ngon"]      # '初九曰: …', '九三重剛而不中…': Văn ngôn of Kiền / Khôn
    elif head.startswith("彖曰"):
        order = [i for i in order if han_segments[i]["kind"] == "thoan_truyen"]
    elif head.startswith("象曰"):
        order = [i for i in order if han_segments[i]["kind"] in ("dai_tuong", "tieu_tuong")]
    elif head.startswith("文言曰"):
        order = [i for i in order if han_segments[i]["kind"] == "van_ngon"]
    best, best_i = 0.0, None
    for i in order:
        c = coverage(x, norm_han(han_segments[i]["text"]))
        if c > best + 1e-9:
            best, best_i = c, i
    return best_i if best >= 0.75 else None


FOOTMARK = re.compile(r"\[\^[0-9.]+\]")


def labelled_key(b: dict) -> str | None:
    """The transcription labels each block (kind, hao, dung): its key, when it has one."""
    k = b.get("kind")
    if not k:
        return None
    if k in ("hao", "tieu_tuong") and b.get("hao"):
        return f"{k}{b['hao']}"
    if k == "tieu_tuong" and b.get("dung"):
        return "tieu_tuong_dung"
    return k


def block_layers(b: dict) -> dict:
    """Layers of one block, footnote marks taken out; other_commentary (lời bàn of the tiên nho and of named scholars) becomes tien_nho,
    each part headed by its printed label when that is not the generic 'Lời bàn của Tiên Nho'."""
    out = {}
    for layer in LAYERS:
        v = (b.get(layer) or "").strip()
        if v:
            out[layer] = FOOTMARK.sub("", v)
    parts = []
    for c in b.get("other_commentary") or []:
        t = FOOTMARK.sub("", (c.get("text") or "").strip())
        if t:
            lab = c.get("label", "")
            parts.append(t if lab in ("", "Lời bàn của Tiên Nho") else f"{lab}: {t}")
    if parts:
        out["tien_nho"] = (out.get("tien_nho", "") + "\n" + "\n".join(parts)).strip()
    return out


@lru_cache(maxsize=None)
def quẻ_texts(n: int) -> dict:
    """{key: {kind, hao?, han, chiem, layers: {am, nghia, trinh_di, chu_hy, tien_nho}, pages, ntt: bool}} for quẻ n, keys as seg_key."""
    q = han_kb()[n]
    out = {seg_key(s): {**{k: v for k, v in s.items() if k != "text"}, "han": s["text"], "layers": {}, "pages": [], "blocks": 0}
           for s in q["segments"]}
    f = ntt_dir() / f"{n}.json"
    unmatched = []
    if f.exists():
        ntt = json.loads(f.read_text("utf-8"))
        pos = 0
        for b in ntt["segments"]:
            key = labelled_key(b)
            if key == "intro" and key not in out:   # Trình Di's opening of the quẻ (why it follows the one before): no Hán of its own
                out["intro"] = {"kind": "intro", "han": "", "chiem": [], "layers": {}, "pages": [], "blocks": 0}
            if key not in out:                      # an unlabelled block (Wikisource copies): placed by its Hán text
                i = _match(q["segments"], b.get("han", ""), pos)
                if i is None:
                    unmatched.append(b.get("han", "")[:20])
                    continue
                pos = i
                key = seg_key(q["segments"][i])
            seg = out[key]
            seg["blocks"] += 1
            for layer, v in block_layers(b).items():
                seg["layers"][layer] = (seg["layers"].get(layer, "") + "\n" + v).strip()
            seg.setdefault("footnotes", []).extend(b.get("footnotes") or [])
            if b.get("status"):
                seg.setdefault("status", []).append(b["status"])
            if b.get("page") is not None:
                seg["pages"].append(b["page"])
    return {"number": n, "han": q["han"], "segments": out, "has_ntt": f.exists(), "unmatched": unmatched}
