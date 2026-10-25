"""Build engine/data/kinh_dich/zhouyi_han.json: the Hán text of the 64 quẻ split into segments, from the saved Wikisource 周易
(engine/data/sources_web/zh_zhouyi.json, WEB:zh_zhouyi). Each segment keeps the page it is read from, so book_text.quote_on_page can check it.

Per quẻ: thoan (卦辭), hao 1-6 (爻辭), dung (用九 / 用六, Kiền and Khôn), thoan_truyen (彖), dai_tuong (大象), tieu_tuong 1-6 (+ dụng),
van_ngon (文言, Kiền and Khôn; kept whole). Chiêm words (the omen words of Ngô Tất Tố's preface: nguyên cát … hữu hối) found in the
thoán and hào texts are listed per segment: a fact the reader may name, not a verdict.

  .venv/bin/python -I tools/build_kinh_dich_kb.py [--check]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "engine" / "data" / "sources_web" / "zh_zhouyi.json"
OUT = ROOT / "engine" / "data" / "kinh_dich" / "zhouyi_han.json"

HAN_NAMES = ("乾 坤 屯 蒙 需 訟 師 比 小畜 履 泰 否 同人 大有 謙 豫 隨 蠱 臨 觀 噬嗑 賁 剝 復 无妄 大畜 頤 大過 坎 離 "
             "咸 恒 遯 大壯 晉 明夷 家人 睽 蹇 解 損 益 夬 姤 萃 升 困 井 革 鼎 震 艮 漸 歸妹 豐 旅 巽 兌 渙 節 中孚 小過 既濟 未濟").split()
TRI = {"乾": (1, 1, 1), "兌": (1, 1, 0), "離": (1, 0, 1), "震": (1, 0, 0), "巽": (0, 1, 1), "坎": (0, 1, 0), "艮": (0, 0, 1), "坤": (0, 0, 0)}
HAO_LABEL = re.compile(r"^(初[九六]|[九六][二三四五]|上[九六]|用[九六])[：，:,]\s*")

# Ngô Tất Tố's preface ('Tượng và Chiêm'): good, best first — nguyên cát, cát hanh, cát, hanh, lợi, vô hối, vô cữu; bad, worst first —
# hung, lệ, vô du lợi, lận, hữu cữu, hữu hối. Matched on the Hán words, longest first; 无不利 is 'không gì không lợi', not 无…利; 不利
# (bất lợi) is not in the preface's list and has no rank. A word belongs to the clause it stands in (小人吉，大人否 names who it is for):
# the list is a fact the reader may point at, never a verdict on the whole quẻ.
CHIEM = [("元吉", "nguyên cát", "tot", 1), ("无攸利", "vô du lợi", "xau", 3), ("无不利", "vô bất lợi", "tot", 5), ("不利", "bất lợi", "xau", None), ("无咎", "vô cữu", "tot", 7),
         ("无悔", "vô hối", "tot", 6), ("悔亡", "hối vong", "tot", 6), ("有悔", "hữu hối", "xau", 6), ("有咎", "hữu cữu", "xau", 5),
         ("吉", "cát", "tot", 3), ("亨", "hanh", "tot", 4), ("利", "lợi", "tot", 5), ("凶", "hung", "xau", 1), ("厲", "lệ", "xau", 2),
         ("吝", "lận", "xau", 4), ("悔", "hối", "xau", 6), ("咎", "cữu", "xau", 5)]


def clean(s: str) -> str:
    s = re.sub(r"<span[^>]*>|</span>", "", s, flags=re.S)
    s = s.replace("'''", "").replace("-{", "").replace("}-", "")
    s = re.sub(r"\{\{另\|([^|}]*)\|[^}]*\}\}", r"\1", s)          # {{另|包|苞}}: the text's reading, the variant dropped
    s = re.sub(r"\{\{\*\|[^}]*\}\}", "", s)                         # {{*|一作太和}}: an editor's note
    s = re.sub(r"\{\{gap[^}]*\}\}|\{\{wj\}\}", "", s)
    return s.strip()


def chiem(text: str) -> list[dict]:
    found, rest = [], text
    for han, vi, side, rank in CHIEM:
        while han in rest:
            i = rest.index(han)
            found.append((i, {"han": han, "vi": vi, "side": side, "rank": rank}))
            rest = rest[:i] + "□" * len(han) + rest[i + len(han):]
    return [f for _, f in sorted(found, key=lambda x: x[0])]


def parse(n: int, page: str, wikitext: str) -> dict:
    lines = [ln.rstrip() for ln in re.sub(r"<span\s*\n", "<span ", wikitext).splitlines()]
    hdr = re.search(r"([乾坤震巽坎離艮兌])下([乾坤震巽坎離艮兌])上", clean(wikitext))
    q = {"number": n, "han": HAN_NAMES[n - 1], "page": page, "lower_han": hdr.group(1), "upper_han": hdr.group(2), "segments": []}
    section = None
    thoan: list[str] = []
    tuan: list[str] = []
    xiang_hao: list[str] = []
    van: list[str] = []
    yao: list[tuple[str, str]] = []
    dai = None
    for ln in lines:
        t = clean(ln)
        if re.match(r"^\*\s*易經", t):
            section = "jing"; continue
        if re.match(r"^\*\s*彖曰", t):
            section = "tuan"; continue
        if re.match(r"^\*\s*象曰", t):
            section = "xiang"; continue
        if re.match(r"^\*\s*文言曰", t):
            section = "wen"; continue
        if not t.startswith("*"):
            if t and section and not t.startswith(("[[", "{{", "|", "}}", ";")):
                section = None
            continue
        body = t.lstrip("*#").strip()
        if not body:
            continue
        if section == "jing":
            if t.startswith("*#"):
                m = HAO_LABEL.match(body)
                yao.append((m.group(1), body[m.end():]))
            else:
                thoan.append(body)
        elif section == "tuan":
            tuan.append(body)
        elif section == "xiang":
            if t.startswith("*#"):
                xiang_hao.append(body)
            elif dai is None:
                dai = body
        elif section == "wen":
            van.append(body)
    seg = q["segments"].append
    seg({"kind": "thoan", "text": "".join(thoan), "chiem": chiem("".join(thoan))})
    for i, (label, text) in enumerate(yao, start=1):
        if label.startswith("用"):
            seg({"kind": "dung", "label": label, "text": text, "chiem": chiem(text)})
        else:
            seg({"kind": "hao", "hao": i, "label": label, "text": text, "chiem": chiem(text)})
    seg({"kind": "thoan_truyen", "text": "".join(tuan)})
    seg({"kind": "dai_tuong", "text": dai or ""})
    for i, text in enumerate(xiang_hao, start=1):
        if i == 7:
            seg({"kind": "tieu_tuong", "dung": True, "text": text})
        else:
            seg({"kind": "tieu_tuong", "hao": i, "text": text})
    if van:
        seg({"kind": "van_ngon", "text": "\n".join(van)})
    return q


def build() -> dict:
    pages = {c["chapter"]: c for c in json.loads(SRC.read_text("utf-8"))["chapters"]}
    out = {"source": "WEB:zh_zhouyi", "note": "Hán text of 周易 from the saved Wikisource pages; chiêm words per Ngô Tất Tố's preface",
           "hexagrams": []}
    for n, name in enumerate(HAN_NAMES, start=1):
        page = f"周易/{name}"
        out["hexagrams"].append(parse(n, page, pages[page]["text"]))
    return out


def problems(kb: dict) -> list[str]:
    bad = []
    for q in kb["hexagrams"]:
        kinds = [s["kind"] for s in q["segments"]]
        hao = [s for s in q["segments"] if s["kind"] == "hao"]
        tt = [s for s in q["segments"] if s["kind"] == "tieu_tuong"]
        want_dung = q["number"] in (1, 2)
        if len(hao) != 6 or [s["hao"] for s in hao] != list(range(1, 7)):
            bad.append(f"{q['han']}: {len(hao)} hào")
        if len(tt) != 6 + want_dung:
            bad.append(f"{q['han']}: {len(tt)} tiểu tượng")
        if ("dung" in kinds) != want_dung or ("van_ngon" in kinds) != want_dung:
            bad.append(f"{q['han']}: dụng / văn ngôn")
        for s in q["segments"]:
            if not s["text"]:
                bad.append(f"{q['han']}: empty {s['kind']} {s.get('hao', '')}")
        # the 九 / 六 of each label must be the line the header's two quái give (an independent check of the split and of the header)
        lines = TRI[q["lower_han"]] + TRI[q["upper_han"]]
        want = [("初" if i == 1 else "上" if i == 6 else "") + ("九" if x else "六") + ("二三四五"[i - 2] if 1 < i < 6 else "")
                for i, x in enumerate(lines, start=1)]
        if [s["label"] for s in hao] != want:
            bad.append(f"{q['han']}: hào labels {[s['label'] for s in hao]} != {want}")
    return bad


if __name__ == "__main__":
    kb = build()
    bad = problems(kb)
    if "--check" in sys.argv:
        print("\n".join(bad) or "ok")
        sys.exit(1 if bad else 0)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(kb, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(OUT, len(kb["hexagrams"]), "quẻ;", "\n".join(bad) or "no problems")
