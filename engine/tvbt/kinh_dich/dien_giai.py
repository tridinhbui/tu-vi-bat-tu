"""The modern-interpretation layer (diễn giải hiện đại) of a quẻ: engine/data/kinh_dich/dien_giai/<n>.json, written by the system as a draft.

Every statement carries `from`: the segments of Ngô Tất Tố's book it rests on, each with an exact quote of one layer (dịch nghĩa, Trình Di,
Chu Hy). `traditional` is a quote, not a paraphrase: the line in which the commentary tells the diviner what the text means for them
(Chu Hy's 'đó là răn kẻ xem …'). The reader labels this layer as interpretation; lint() refuses a statement whose quote is not on its
segment, an unknown segment, a topic outside TOPICS, method words, absolute words and statements too short to say anything."""
from __future__ import annotations

import json
import re
from functools import lru_cache

from .texts import DATA, LAYERS, quẻ_texts

TOPICS = {"su_nghiep": "Sự nghiệp", "tai_chinh": "Tài chính", "kinh_doanh": "Kinh doanh", "hoc_tap": "Học tập",
          "tinh_cam": "Tình cảm", "gia_dinh": "Gia đình", "lua_chon": "Lựa chọn cá nhân"}
# the reader's own words never talk about books, pages or rules (src/interpret/prose/lint.ts META / ABSOLUTE, same lists)
META = ("sách ", "căn cứ", "quy tắc", "nhận định", "luận đoán", "hệ thống")
# a page reference ('trang 12', 'tr. 5'), not 'trang sức' / 'trang nghiêm'
PAGE_REF = re.compile(r"\b(trang|tr\.)\s*\d")
ABSOLUTE = ("chắc chắn", "nhất định", "suốt đời", "trọn đời", "không bao giờ", "luôn luôn", "tuyệt đối", "định mệnh")


@lru_cache(maxsize=None)
def load(n: int) -> dict | None:
    f = DATA / "dien_giai" / f"{n}.json"
    return json.loads(f.read_text("utf-8")) if f.exists() else None


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("“", '"').replace("”", '"')).strip()


def statements(d: dict):
    """(where, statement) for every statement with text and from."""
    q = d.get("que", {})
    for k in ("core", "image", "structure", "advice"):
        if q.get(k):
            yield f"que.{k}", q[k]
    for t, s in q.get("topics", {}).items():
        yield f"que.topics.{t}", s
    for i, s in enumerate(q.get("conditions", [])):
        yield f"que.conditions.{i}", s
    for h, x in d.get("hao", {}).items():
        for k in ("gist", "position", "advice"):
            if x.get(k):
                yield f"hao.{h}.{k}", x[k]
        for t, s in x.get("topics", {}).items():
            yield f"hao.{h}.topics.{t}", s
    if d.get("dung", {}).get("gist"):
        yield "dung.gist", d["dung"]["gist"]


def quotes(d: dict):
    for where, s in statements(d):
        for f in s.get("from", []):
            yield where, f
    if d.get("que", {}).get("traditional"):
        yield "que.traditional", d["que"]["traditional"]
    for h, x in d.get("hao", {}).items():
        if x.get("traditional"):
            yield f"hao.{h}.traditional", x["traditional"]
    if d.get("dung", {}).get("traditional"):
        yield "dung.traditional", d["dung"]["traditional"]


def lint(n: int) -> list[str]:
    d = load(n)
    if d is None:
        return [f"{n}: no file"]
    bad = []
    segs = quẻ_texts(n)["segments"]
    for where, f in quotes(d):
        seg = segs.get(f.get("seg"))
        if seg is None:
            bad.append(f"{where}: unknown segment {f.get('seg')}")
            continue
        if f.get("layer") not in LAYERS:
            bad.append(f"{where}: unknown layer {f.get('layer')}")
            continue
        if _norm(f.get("quote", "")) not in _norm(seg["layers"].get(f["layer"], "")):
            bad.append(f"{where}: quote not in {f['seg']}.{f['layer']}: {f.get('quote', '')[:40]}")
    for where, s in statements(d):
        t = s.get("text", "")
        if not s.get("from"):
            bad.append(f"{where}: no from")
        if len(t.split()) < 8:
            bad.append(f"{where}: too short")
        low = t.lower()
        for w in META + ABSOLUTE:
            if w in low:
                bad.append(f"{where}: '{w.strip()}'")
        if PAGE_REF.search(low):
            bad.append(f"{where}: page reference")
    q = d.get("que", {})
    for k in ("core", "image", "traditional", "advice"):
        if not q.get(k):
            bad.append(f"que.{k}: missing")
    if set(q.get("topics", {})) != set(TOPICS):
        bad.append(f"que.topics: want {sorted(TOPICS)}, have {sorted(q.get('topics', {}))}")
    for h in map(str, range(1, 7)):
        x = d.get("hao", {}).get(h, {})
        if not x.get("gist") or not x.get("traditional"):
            bad.append(f"hao.{h}: gist and traditional required")
        for t in x.get("topics", {}):
            if t not in TOPICS:
                bad.append(f"hao.{h}.topics: unknown topic {t}")
    if (n in (1, 2)) != bool(d.get("dung")):
        bad.append("dung: only and always for Kiền and Khôn")
    texts = [s["text"] for _, s in statements(d)]
    if len(texts) != len(set(texts)):
        bad.append("a statement is repeated")
    return bad
