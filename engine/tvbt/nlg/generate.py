"""Deterministic NLG: structured Interpretation -> plan -> sentences -> Vietnamese text.

Every content sentence carries provenance (finding ids / rule ids). Nothing is rendered that is
not an inferred finding; depth levels add analysis layers (facts, counter-evidence, rule trace,
philosophical limits), not filler.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field

from ..knowledge.schema import KnowledgeRule, Source
from ..reasoning.conflict import resolve
from ..reasoning.engine import InferenceResult
from . import lexicon as lx

CONNECT = {
    "add": ["Ngoài ra", "Điểm đáng chú ý là", "Khi xét cùng"],
    "contrast": ["Tuy nhiên", "Ngược lại", "Dù vậy"],
    "cause": ["Vì vậy", "Trong điều kiện này", "Do đó"],
}


@dataclass
class Interpretation:
    subject: str
    claim: str
    effect: str
    status: str
    basis: str
    supporting: list[str]
    opposing: list[str]
    finding_ids: list[str]
    facts: list[str]
    sources: list[str]
    resolution: str | None
    scope: str = "natal"


@dataclass
class Sentence:
    text: str
    provenance: list[str] = field(default_factory=list)
    kind: str = "content"   # content | caveat | meta


def subject_vi(s: str) -> str:
    return "toàn lá số" if s == "chart" else "cung " + s.split(":", 1)[1]


FACT_VI = {
    "palace.name": "cung {v}", "palace.branch": "tọa tại {v}", "palace.own_major_stars": "chính tinh trong cung: {v}",
    "palace.tam_phuong_majors": "chính tinh trong tam phương tứ chính: {v}",
    "palace.tam_phuong_stars": "các sao trong tam phương tứ chính: {v}",
    "palace.tam_phuong_tu_hoa": "Tứ Hóa trong tam phương: {v}",
    "palace.sat_pha_tham_in_tam_phuong": "Thất Sát, Phá Quân, Tham Lang cùng nằm trong tam phương",
    "bazi.day_master_stem": "Nhật Chủ là {v}", "bazi.missing_elements": "tám chữ nhìn thấy vắng hành: {v}",
    "palace.own_stars": "các sao trong cung: {v}", "palace.neighbor_majors": "chính tinh ở hai cung giáp: {v}", "palace.neighbor_stars": "các sao ở hai cung giáp: {v}", "palace.tu_hoa": "sao hóa trong cung: {v}",
    "bazi.dm_has_root": "Nhật Chủ có căn trong tàng can", "bazi.dm_element": "hành Nhật Chủ: {v}",
}
GROUP_VI = {"tu_phu_vu_tuong": "Tử – Phủ – Vũ – Tướng", "sat_pha_liem_tham": "Sát – Phá – Liêm – Tham",
            "co_nguyet_dong_luong": "Cơ – Nguyệt – Đồng – Lương", "cu_nhat_nguyet": "Cự – Nhật – Nguyệt"}
_FACT_RE = re.compile(r"^(?P<k>[\w.]+)=(?P<v>.*) @(?P<s>.+)$")


def pretty_fact(label: str) -> str:
    m = _FACT_RE.match(label)
    if not m:
        return label
    k, v = m["k"], m["v"]
    try:
        val = ast.literal_eval(v)
    except Exception:
        val = v
    if isinstance(val, list):
        val = ", ".join(val[:8]) + (f" (và {len(val) - 8} sao khác)" if len(val) > 8 else "") if val else "không có"
    if k == "palace.tuan":
        return "cung có Tuần" if val else "cung không có Tuần"
    if k == "palace.triet":
        return "cung có Triệt" if val else "cung không có Triệt"
    if k.startswith("palace.dignity."):
        return f"độ sáng của {k.split('.', 2)[2]}: {val}"
    if k.startswith("derived.group."):
        return f"thuộc nhóm sao {GROUP_VI.get(k.rsplit('.', 1)[1], k)}"
    tpl = FACT_VI.get(k)
    if tpl is None:
        return label
    return tpl.format(v=val) if "{v}" in tpl else tpl


def build_interpretations(res: InferenceResult, rules: list[KnowledgeRule], sources: list[Source]) -> list[Interpretation]:
    report = {(e["subject"], e["claim"]): e for e in resolve(res, rules)}
    rmap = {r.id: r for r in rules}
    out = []
    for (subj, claim), e in sorted(report.items()):
        fs = [f for f in res.findings if f.subject == subj and f.claim == claim]
        facts: list[str] = []
        for f in fs:
            facts += [pretty_fact(res.nodes[n].label) for n, k in res.why(f.id)["kinds"].items() if k == "fact"]
        srcs = sorted({s for f in fs for s in rmap[f.rule_id].sourceIds})
        sup_eff = next((f.effect for f in fs if f.effect == "support"), fs[0].effect)
        out.append(Interpretation(subj, claim, sup_eff, e["status"], fs[0].basis if all(
            f.basis == fs[0].basis for f in fs) else "draft", e["supporting"], e["opposing"],
            [f.id for f in fs], sorted(set(facts)), srcs, e["resolution"]))
    return out


def _pick(kind: str, i: int) -> str:
    opts = CONNECT[kind]
    return opts[i % len(opts)]


def realize(interps: list[Interpretation], level: int = 1) -> list[Sentence]:
    if not 1 <= level <= 5:
        raise ValueError("level must be 1..5")
    out: list[Sentence] = []
    by_subj: dict[str, list[Interpretation]] = {}
    for it in interps:
        by_subj.setdefault(it.subject, []).append(it)
    n = 0
    for subj in sorted(by_subj, key=lambda s: (s != "chart", s)):
        out.append(Sentence(f"Về {subject_vi(subj)}:", kind="meta"))
        for it in by_subj[subj]:
            entry = lx.CLAIMS.get(it.claim)
            label = entry["label"] if entry else f"“{it.claim}” (chưa có mô tả tiếng Việt)"
            prov = it.finding_ids + it.supporting + it.opposing
            lead = "Có thể nhận thấy" if it.status in ("supported", "qualified") else "Chưa thể khẳng định"
            out.append(Sentence(f"{lead} một dấu hiệu {lx.EFFECT_VI[it.effect]} {label}; nhận định này "
                                f"{lx.STATUS_VI[it.status]}.", prov))
            if level >= 2 and it.facts:
                out.append(Sentence(f"{_pick('cause', n)}, nhận định dựa trên các dữ kiện: "
                                    + "; ".join(it.facts) + ".", prov))
            if level >= 3:
                if it.opposing and it.supporting:
                    out.append(Sentence(f"{_pick('contrast', n)}, quy tắc {', '.join(it.opposing)} đi theo chiều đối lập "
                                        f"với {', '.join(it.supporting)}. " + (it.resolution or ""), prov))
                elif it.opposing and not it.supporting:
                    out.append(Sentence(f"Chỉ có quy tắc hạn chế ({', '.join(it.opposing)}), không có quy tắc hỗ trợ đi kèm.", prov))
                else:
                    out.append(Sentence(f"{_pick('add', n)} chưa có quy tắc đối lập nào trong bộ quy tắc hiện hành khớp với dữ kiện này.", prov))
            if level >= 4:
                out.append(Sentence(f"Truy vết: quy tắc {', '.join(it.supporting + it.opposing)}; nguồn "
                                    f"{', '.join(it.sources) or 'chưa có'}; {lx.BASIS_VI[it.basis]}.", prov, "meta"))
            n += 1
    if level >= 5:
        for p in lx.PHILOSOPHY:
            out.append(Sentence(p, kind="caveat"))
    out.append(Sentence(lx.DISCLAIMER, kind="caveat"))
    return out


def render(sentences: list[Sentence]) -> str:
    return "\n".join(s.text for s in sentences)
