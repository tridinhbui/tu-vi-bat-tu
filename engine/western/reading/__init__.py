"""Rule-based Vietnamese reading of a Western natal chart. No language model: every paragraph applies a cited rule to the chart.

build(chart) -> {version, chapters: [{id, title, paragraphs: [Para]}], audit, disclaimer, operational}
"""
from __future__ import annotations

import copy
import datetime as dt

from . import argue, audit, ch_core, ch_layers, ch_life, ch_time
from .facts import OPERATIONAL, Facts

VERSION = "west-reading-0.1.0"
DISCLAIMER = ("Chiêm tinh là một truyền thống diễn giải biểu tượng, không phải phương pháp dự báo đã được khoa học chứng minh. "
              "Mỗi đoạn dưới đây áp một quy tắc có ghi nguồn vào bản đồ sao của bạn; hãy đọc như một góc nhìn để tự suy ngẫm, "
              "không phải lời tiên đoán hay lời khuyên y tế, tài chính, pháp lý.")
CHAPTERS = [
    ("tong_quan", "Tổng quan bản đồ sao", ch_core.overview),
    ("hanh_tinh", "Từng hành tinh theo cung và nhà", ch_layers.planets),
    ("goc_hop", "Các góc hợp chính", ch_layers.aspects),
    ("tinh_cach", "Tính cách", ch_core.personality),
    ("tu_duy", "Tư duy và học tập", ch_core.mind),
    ("cam_xuc", "Cảm xúc", ch_core.emotions),
    ("su_nghiep", "Sự nghiệp", ch_life.career),
    ("tai_chinh", "Tài chính và kinh doanh", ch_life.money),
    ("quan_he", "Quan hệ và hôn nhân", ch_life.relations),
    ("gia_dinh", "Gia đình", ch_life.family),
    ("dinh_huong", "Định hướng cuộc sống", ch_life.direction),
]


def build(chart: dict, mode: str = "deep", gender: str | None = None, when: dt.datetime | None = None) -> dict:
    f = Facts(chart, gender)
    when = when or dt.datetime.now(dt.timezone.utc)
    if f.time_known:
        from .. import returns as R
        try:
            f.age_now = R.age_at(chart, when)
        except Exception:  # noqa: BLE001 - only the 'years when this planet rules' hint uses it
            pass
    chapters = []
    for cid, title, fn in CHAPTERS:
        paras = fn(f)
        lead = argue.SUMMARIES[cid](f) if cid in argue.SUMMARIES else None
        chapters.append({"id": cid, "title": title, "paragraphs": [p.as_dict() for p in ([lead] if lead else []) + paras]})
    chapters.append({"id": "tong_hop", "title": "Tổng hợp", "paragraphs": [p.as_dict() for p in ch_layers.synthesis(f, chapters)]})
    try:
        tv = [p.as_dict() for p in ch_time.cycles(f, when)]
    except Exception as e:  # noqa: BLE001 - an out-of-range date must not lose the natal reading
        tv = [{"id": "tv.error", "heading": "Thời vận", "text": f"Không tính được phần thời vận cho ngày này ({e}).", "school": "calc", "sources": [],
               "evidence": [], "level": "overview", "tier": "calc", "steps": [], "polarity": 0, "topic": "thoi_van", "keys": []}]
    chapters.append({"id": "thoi_van", "title": f"Thời vận ({when:%d/%m/%Y})", "paragraphs": tv})
    report = audit.check(chapters, f.time_known)
    out = {"version": VERSION, "mode": "deep", "chapters": chapters, "audit": report, "disclaimer": DISCLAIMER,
           "operational": OPERATIONAL, "gender": gender}
    return overview_of(out) if mode == "overview" else out


def overview_of(full: dict) -> dict:
    """The Tổng quan reading of a whole one: the overview-level paragraphs of each chapter (the audit ran on the whole reading)."""
    out = copy.deepcopy(full)
    out["mode"] = "overview"
    for ch in out["chapters"]:
        ch["paragraphs"] = [p for p in ch["paragraphs"] if p["level"] == "overview"]
    return out
