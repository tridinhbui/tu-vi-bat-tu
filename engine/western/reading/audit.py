"""Checks run on every reading before it is returned (and in the tests over many charts).

  untraceable  a source-tier paragraph with no source, or a source id the registry does not know
  school_mix   a paragraph citing a source of another school (only 'compare' paragraphs may)
  duplicate    two sentences sharing most of their word trigrams
  generic      a sentence that names nothing from the chart and no method or book (Barnum risk)
  forbidden    certainty words, death, illness names, crime words
  unreconciled a chapter with a supporting and a hindering paragraph and no comparison paragraph
"""
from __future__ import annotations

import re
import unicodedata

from .. import kb
from .vocab import PLANET_VI, SIGN_VI

FORBIDDEN = [r"\bchắc chắn sẽ\b", r"\bchắc chắn\b", r"\bnhất định sẽ\b", r"\bqua đời\b", r"\bchết\b", r"\btử vong\b", r"\bung thư\b", r"\btim mạch\b",
             r"\btiểu đường\b", r"\bhuyết áp\b", r"\bsát nhân\b", r"\bgiết\b", r"\btrộm\b", r"\bngoại tình\b", r"\bly hôn\b", r"\bphá sản\b"]
ALLOWED_NEGATED = [r"không luận (việc|chuyện|phần|bệnh|sinh tử)", r"không (đủ|được) để đoán chắc", r"không thay cho", r"Thiên Bàn không luận"]
BARNUM = ["bạn là người", "đôi khi bạn", "bạn có xu hướng che giấu", "bạn có tiềm năng", "nhạy cảm và sâu sắc", "thông minh và nhạy cảm"]
METHOD_WORDS = ("chương", "Lilly", "Ptolemy", "Valens", "Leo", "Thiên Bàn", "Regiomontanus", "Lot", "tr.", "chỗ", "Nhà ", "cung Mọc", "Thiên Đỉnh")
SCHOOL_OK = {"hellenistic": {"hellenistic", "astronomy", "convention", "data"}, "traditional": {"traditional", "astronomy", "convention", "data"},
             "modern": {"modern", "astronomy", "convention", "data"}, "calc": {"astronomy", "convention", "data", "modern", "hellenistic", "traditional"},
             "compare": {"hellenistic", "traditional", "modern", "astronomy", "convention", "data"}}


def _fold(s: str) -> str:
    s = "".join(ch for ch in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9đ ]+", " ", s.replace("đ", "d"))


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Ỹ(])", text) if s.strip()]


def _chart_tokens() -> list[str]:
    return list(PLANET_VI.values()) + list(SIGN_VI.values()) + ["°", "Nhà", "cung Mọc", "Thiên Đỉnh", "Fortune", "Daimon"]


def check(chapters: list[dict]) -> dict:
    src_reg = kb.sources()
    issues: list[dict] = []
    tokens = _chart_tokens()
    seen: list[tuple[str, set]] = []
    total_sent = 0
    for ch in chapters:
        pols = []
        has_compare = False
        for p in ch["paragraphs"]:
            pid = p["id"]
            if p["school"] == "compare":
                has_compare = True
            if p["tier"] == "src" and not p["sources"]:
                issues.append({"kind": "untraceable", "para": pid})
            for s in p["sources"]:
                if s["id"] not in src_reg:
                    issues.append({"kind": "untraceable", "para": pid, "source": s["id"]})
                    continue
                if src_reg[s["id"]]["school"] not in SCHOOL_OK[p["school"]]:
                    issues.append({"kind": "school_mix", "para": pid, "source": s["id"], "school": p["school"]})
            if p.get("polarity"):
                pols.append(p["polarity"])
            for sent in sentences(p["text"]):
                total_sent += 1
                low = sent.lower()
                for pat in FORBIDDEN:
                    if re.search(pat, low) and not any(re.search(a, sent) for a in ALLOWED_NEGATED):
                        issues.append({"kind": "forbidden", "para": pid, "pattern": pat, "sentence": sent})
                for b in BARNUM:
                    if b in low:
                        issues.append({"kind": "generic", "para": pid, "sentence": sent, "why": "barnum:" + b})
                person = re.search(r"\b(bạn|người ta|người này|tính cách|thường|hay|dễ)\b", low)
                if person and not any(t in sent for t in tokens) and not any(w in sent for w in METHOD_WORDS) and not re.search(r"\d", sent):
                    issues.append({"kind": "generic", "para": pid, "sentence": sent})
                words = _fold(sent).split()
                tri = {" ".join(words[i:i + 3]) for i in range(len(words) - 2)}
                if len(tri) >= 8 and p["tier"] != "calc":      # short sentences may share a shape
                    for other_pid, ot in seen:
                        j = len(tri & ot) / len(tri | ot)
                        if j > 0.6:
                            issues.append({"kind": "duplicate", "para": pid, "with": other_pid, "jaccard": round(j, 2), "sentence": sent})
                            break
                    seen.append((pid, tri))
        if 1 in pols and -1 in pols and not has_compare:
            issues.append({"kind": "unreconciled", "chapter": ch["id"]})
    kinds = {}
    for i in issues:
        kinds[i["kind"]] = kinds.get(i["kind"], 0) + 1
    return {"sentences": total_sent, "issues": issues, "counts": kinds, "ok": not issues}
