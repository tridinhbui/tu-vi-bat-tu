"""Orchestrator of the evidence engine: chart -> facts -> rules -> conclusions -> palace dossiers -> period layer -> Bát Tự assessment ->
report. Pure and deterministic; ~tens of ms per chart. Used by POST /api/interpretation (behind TVBT_DEEP_INTERPRETATION) and by tests."""
from __future__ import annotations

import dataclasses
from functools import lru_cache

from .. import bazi_reading
from ..knowledge.loader import load_all, load_claims
from . import conclusions as C
from . import dossier as D
from . import engine, facts, report, temporal_facts

ENGINE_VERSION = "evidence-1.0"


@lru_cache(maxsize=2)
def _knowledge(dignity_school: str):
    rules, sources = load_all()
    if dignity_school != "thuc_hanh":    # same policy as /api/reasoning: Thực Hành's temperament rules are keyed to its own brightness table
        rules = [dataclasses.replace(r, reviewStatus="draft") if r.category in ("star_dignity", "star_combination") else r for r in rules]
    return rules, sources, load_claims(), C.load_qualifiers()


def run(tv, bz, birth_year: int, year: int | None = None, dignity_school: str = "thuc_hanh", verified_only: bool = True) -> dict:
    rules, sources, claims, quals = _knowledge(dignity_school)
    base = facts.tuvi_facts(tv)
    res = engine.run(rules, sources, base, system="tu_vi")
    concl = C.build(res, rules, claims, base, qualifiers=quals, verified_only=verified_only)
    layered = temporal_facts.layered(tv, year) if year else None
    doss = D.build(tv, concl, layered, dignity_school)
    bz_read = bazi_reading.build(bz, birth_year, year) if bz is not None else None
    if bz_read is not None:   # the verified Bát Tự rule readings (八字真宗 tables), kept with their sources; never mixed with Tử Vi
        bres = engine.run(rules, sources, facts.bazi_facts(bz), system="bat_tu")
        bz_read["readings"] = [{"rule_id": r.rule_id, "reading": r.text, "trigger": r.trigger_text, "tone": r.tone, "basis": r.basis,
                                "sources": [C.cite_vi(x) for x in r.cites] or r.books}
                               for _, r in C.readings_from(bres, rules, claims, facts.bazi_facts(bz))
                               if r.basis == "verified" or not verified_only]
    rep = report.build(tv, concl, doss, layered, bz_read)
    return {"engine": ENGINE_VERSION, "year": year, "dignity_school": dignity_school,
            "conclusions": C.to_dict(concl), "dossiers": doss, "bazi": bz_read, "report": rep,
            "stats": {"findings": len(res.findings), "conclusions": len(concl),
                      "verified_findings": sum(1 for f in res.findings if f.basis == "verified")}}


def interpret(req, year: int | None = None) -> dict:
    """Convenience for scripts/tests: req is an api.BirthReq."""
    from ..api import _compute
    _, bz, tv = _compute(req)
    return run(tv, bz, req.year, year, req.dignity_school)


SECTION_TITLES = [("nhan_dinh_tong_quan", "Nhận định tổng quan"), ("co_so_luan_giai", "Cơ sở luận giải"), ("yeu_to_ho_tro", "Yếu tố hỗ trợ"),
                  ("han_che_mau_thuan", "Điểm hạn chế và mâu thuẫn"), ("luan_giai_tong_hop", "Luận giải tổng hợp"),
                  ("dieu_kien_gioi_han", "Điều kiện và giới hạn")]


def to_markdown(out: dict) -> str:
    rep = out["report"]
    lines = [f"> {rep['header']}", ""]
    for ch in rep["chapters"]:
        lines += [f"## {ch['title']}", ""]
        for key, title in SECTION_TITLES:
            sec = ch["sections"].get(key)
            lines.append(f"**{title}.**")
            if isinstance(sec, str):
                lines += [sec, ""]
            elif isinstance(sec, list):
                if not sec:
                    lines += ["(không có)", ""]
                for x in sec:
                    lines.append(f"- {x['text'] if isinstance(x, dict) else x}" + (f" [{'; '.join(x['sources'])}]" if isinstance(x, dict) and x.get("sources") else ""))
                lines.append("")
            elif isinstance(sec, dict):
                items = sec.get("items", []) + [{"text": r} for r in sec.get("relations", [])]
                items += [{"text": c} for c in sec.get("conditions", [])] + [{"text": "Câu hỏi mở: " + q} for q in sec.get("open_questions", [])]
                items += [{"text": g} for g in sec.get("guards", [])]
                items += [{"text": "Nhận diện cấu trúc: " + x["text"]} for x in sec.get("structural_labels", [])]
                items += [{"text": "Chỉ dựa trên năm sinh: " + x["text"]} for x in sec.get("generic", [])]
                if not items:
                    lines.append("(không có)")
                for x in items:
                    lines.append(f"- {x['text']}" + (f" [{'; '.join(x['sources'])}]" if x.get("sources") else ""))
                lines.append("")
        for pr in ch["sections"].get("period_readings", []):
            lines.append(f"*Mệnh gặp {pr['layer']} ({pr['palace']}):* " + ("; ".join(f"{r['text']} ({r['source']})" for r in pr["readings"]) or "không có điều kiện nào khớp"))
            lines.append("")
    return "\n".join(lines)
