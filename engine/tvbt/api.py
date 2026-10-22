"""HTTP API + static UI host. No external AI calls. Birth data is processed in-memory and never stored."""
from __future__ import annotations

import dataclasses
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import bazi, cross, temporal, tuvi
from .calendar_core import BirthInput, normalize
from .ganzhi import BRANCHES_VI
from .knowledge.loader import load_all, load_claims
from .knowledge.schema import validate_pack
from .nlg import generate as nlg, lexicon as lx
from .reasoning import engine, facts

ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="tvbt", version="0.1.0")
# Same paths the Worker serves as static assets, so local/uvicorn runs match production.
app.mount("/css", StaticFiles(directory=ROOT / "web" / "css"), name="css")
app.mount("/js", StaticFiles(directory=ROOT / "web" / "js"), name="js")


class BirthReq(BaseModel):
    year: int = Field(ge=1900, le=2049); month: int = Field(ge=1, le=12); day: int = Field(ge=1, le=31)
    hour: int = Field(ge=0, le=23); minute: int = Field(ge=0, le=59)
    tz: str = "Asia/Ho_Chi_Minh"; gender: str = Field(pattern="^(male|female)$")
    longitude: float | None = None; calendar: str = Field("vn", pattern="^(vn|vn_south|vn_utc7|cn)$")
    zi_rule: str = Field("early_zi_next_day", pattern="^(early_zi_next_day|late_zi_same_day)$")
    use_true_solar_time: bool = False; level: int = Field(3, ge=1, le=5)
    to_year: int | None = None
    # khao_luan: KL "Thế đứng", the table popular boards use — the default since 2026-10-21 (owner's decision, so the board matches them);
    # thuc_hanh / toan_thu stay selectable on the board
    dignity_school: str = Field("khao_luan", pattern="^(thuc_hanh|toan_thu|khao_luan)$")
    # where the books disagree (tuvi.VARIANTS): defaults = popular-board convention, each choice is reported back in chart.school
    tu_hoa_table: str = Field("KL", pattern="^(KL|TH|TT_WS)$")
    tieu_han_rule: str = Field("TH", pattern="^(TH|KL)$")
    luu_ha_table: str = Field("board", pattern="^(board|KL|TH)$")
    experimental: bool = False      # opt-in: also evaluate the DRAFT cách cục + engine-demo rules (never part of production readings)

    def birth(self) -> BirthInput:
        return BirthInput(self.year, self.month, self.day, self.hour, self.minute, self.tz, self.gender,
                          self.longitude, self.calendar, self.zi_rule, self.use_true_solar_time)


def _compute(req: BirthReq):
    try:
        nb = normalize(req.birth())
    except Exception as e:  # invalid date, DST gap, unknown tz, missing longitude
        raise HTTPException(422, str(e))
    return nb, bazi.compute(nb), tuvi.compute(nb, dignity_school=req.dignity_school, tu_hoa_table=req.tu_hoa_table,
                                                tieu_han_rule=req.tieu_han_rule, luu_ha_table=req.luu_ha_table)


@app.post("/api/chart")
def chart(req: BirthReq):
    nb, bz, tv = _compute(req)
    return {"bazi": dataclasses.asdict(bz), "tuvi": dataclasses.asdict(tv),
            "normalization_trace": dataclasses.asdict(nb.trace)}


@app.post("/api/analysis")
def analysis_endpoint(req: BirthReq):
    """Deterministic structure analysis (see analysis.py): sourced prose per chapter, each block tagged by layer and basis."""
    from . import analysis
    nb, bz, tv = _compute(req)
    return {"chapters": analysis.analyse(tv, bz), "dignity_school": req.dignity_school}


@app.post("/api/deep-reading")
def deep_reading(req: BirthReq):
    """Synthesised ten-chapter reading (tvbt/synthesis). Behind TVBT_DEEP_INTERPRETATION (default OFF): with the flag off this answers 404 and no
    other endpoint changes. Draft formations are included only when the caller already opted into `experimental`."""
    from .synthesis import enabled
    if not enabled():
        raise HTTPException(404, "deep interpretation is disabled")
    from .synthesis.compose import build_deep_reading
    nb, bz, tv = _compute(req)
    rules, sources = load_all()
    claims = load_claims()
    forms = None
    if req.experimental:
        from .knowledge.loader import load_experimental
        xr, forms, xs = load_experimental()
        rules, sources = rules + xr, sources + [s for s in xs if s.id not in {x.id for x in sources}]
    return build_deep_reading(tv, bz, rules, sources, claims, req.year, req.to_year, forms)


@app.post("/api/facts")
def chart_facts(req: BirthReq):
    """Chart facts for the TypeScript interpretation pipeline (src/interpret): the same fact base the Python rule engine reads
    (reasoning/facts.py), plus palaces, Tứ Hóa, every đại hạn with its stem's Tứ Hóa landing and the Khảo Luận / Thực Hành vận
    readings for it, and the requested year. Pure data, nothing interpreted; the TS engine runs the rules itself."""
    from . import analysis, van_han
    from .ganzhi import STEMS_VI
    nb, bz, tv = _compute(req)
    from . import van_han_tt
    from .ganzhi import BRANCHES_VI as _BR
    ybr = _BR.index(tv.year_gz.split(" ")[1])
    base = facts.tuvi_facts(tv)
    star_pal = {s: p["name"] for p in tv.palaces for s in p["stars"]}
    decades = []
    for d in tv.dai_han:
        pal = next(p for p in tv.palaces if p["branch"] == d["branch"])
        stem = pal["stem"]
        hoa = dict(zip(("Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"), tuvi.hoa_of(tv, STEMS_VI.index(stem))))
        decades.append({**d, "palace": pal["name"], "stem": stem, "hoa": {k: {"star": v, "palace": star_pal.get(v)} for k, v in hoa.items()},
                        "readings": van_han.read_traced(tv, pal["name"]),
                        # Toàn Thư nhập hạn ca (van_han_tt, pp.97-105, paraphrased, page check pending) and Khảo Luận pp.230-233 as data
                        "tt": van_han_tt.read(tv, pal), "kl": analysis.dai_van_facts(tv, pal["branch_index"], ybr)})
    year = req.to_year or req.year + 30
    # Bát Tự: the fact base the Python engine reads for system 'bat_tu' (the same call as /api/analysis, so the same rules can fire), and
    # the computed pillars, ten gods and luck pillars for the chapter's frame. Data only.
    from .ganzhi import BRANCHES_VI
    pil = {k: {"name": p.name, "stem": STEMS_VI[p.stem], "branch": BRANCHES_VI[p.branch], "stem_ten_god": p.stem_ten_god,
               "hidden": [{"stem": h["name"], "element": h["element"], "ten_god": h["ten_god"]} for h in p.hidden],
               "stage": p.stage_vs_day_master} for k, p in bz.pillars.items()}
    # zz=True: the 八字真宗 direct-judgement facts (pp.50-74), so its verified rules can fire in the TS prose; /api/reasoning keeps the old view
    bazi_out = {"base": facts.bazi_facts(bz, zz=True), "pillars": pil, "day_master": STEMS_VI[bz.day_master], "day_master_element": bz.day_master_element,
                "luck_direction": bz.luck_direction, "luck_start_age": round(bz.luck_start["age_years"], 1),
                "luck": [{"name": lp.name, "start_age": round(lp.start_age, 1), "start_year": int(lp.start_date[:4]) if lp.start_date else None,
                          "ten_god": lp.ten_god} for lp in bz.luck_pillars],
                "kong_wang_day": bz.extras.get("kong_wang_day", []),
                # pillar relations (hợp, xung, hại, phá, hình) for the per-chapter Bát Tự prose; pillar ids as "year-hour"
                "relations": {k: [{"pillars": r["pillars"]} for r in v if "pillars" in r] for k, v in bz.relations.items()},
                # structure analysis for the prose: strength (TVH), điều hậu (TVH table), phù ức, cách, luck pillars (bazi_deep.pipeline)
                "deep": _bazi_deep(bz, nb, req.gender, [year, year + 1, year + 2])}
    return {"engine": "tvbt-facts-1", "dignity_school": req.dignity_school, "birth_year": req.year, "lunar_year": tv.lunar["year"],
            "gender": req.gender, "year_gz": tv.year_gz, "cuc": tv.cuc, "menh_nap_am": tv.menh_nap_am, "menh_cuc_relation": tv.menh_cuc_relation,
            "yin_yang_gender": tv.yin_yang_gender, "dai_han_direction": tv.dai_han_direction,
            "palaces": tv.palaces, "tu_hoa": tv.tu_hoa, "base": base, "decades": decades, "year": _year_facts(tv, year, ybr), "bazi": bazi_out}


def _bazi_deep(bz, nb, gender: str, years: list[int] | None = None) -> dict | None:
    """The structure analysis for the Bát Tự prose, with the lưu niên of `years` (the requested year and the two after it)."""
    from .bazi_deep import pipeline
    from .bazi_deep.model import ChartView
    try:
        luck = [{"index": l.index, "stem": l.stem, "branch": l.branch, "start_year_exact": l.start_year_exact} for l in bz.luck_pillars]
        return pipeline.prose_summary(ChartView.from_bazi(bz, nb.utc, gender), luck, years)
    except Exception:  # the analysis is an extra: a chart it cannot read keeps the rest of the facts
        return None


def _year_facts(tv, year: int, ybr: int) -> dict:
    """The requested year (temporal.tuvi_year) plus, for its tiểu hạn palace, the Toàn Thư nhập hạn ca readings and the Khảo Luận
    pp.230-233 facts, the same two views the đại hạn paragraphs use."""
    from . import analysis, van_han_tt
    y = temporal.tuvi_year(tv, year)
    pal = next((p for p in tv.palaces if p["name"] == y.get("tieu_han_palace")), None)
    if pal:
        y["tieu_han_tt"] = van_han_tt.read(tv, pal)
        y["tieu_han_kl"] = analysis.dai_van_facts(tv, pal["branch_index"], ybr)
    return y


@app.post("/api/synthesis")
def synthesis(req: BirthReq):
    """'Luận giải tổng hợp' for each Tử Vi report chapter (tvbt/synthesis/chapters.py): Semantic IR -> symbolic reasoning -> Vietnamese narrative
    grammar, every sentence traced to rule ids. No language model. Behind TVBT_DEEP_INTERPRETATION (default OFF): with the flag off this answers 404
    and nothing else changes. `to_year` picks the year for the đại hạn chapter; level 5 also returns the Semantic IR."""
    from .synthesis import enabled
    if not enabled():
        raise HTTPException(404, "synthesis is disabled")
    from .synthesis.chapters import build_synthesis
    nb, bz, tv = _compute(req)
    rules, sources = load_all()
    if req.dignity_school != "thuc_hanh":
        import dataclasses as _dc
        rules = [_dc.replace(r, reviewStatus="draft") if r.category in ("star_dignity", "star_combination") else r for r in rules]
    out = build_synthesis(tv, rules, sources, load_claims(), req.year, req.to_year)
    if req.level < 5:
        out.pop("semantic_ir", None)
    return out


@app.post("/api/interpretation")
def interpretation(req: BirthReq):
    """Evidence engine (tvbt/reasoning/interpretation.py): rule findings reduced to conclusions with trigger facts, independent sources,
    source-cited qualifiers and conflict relations; six-layer dossiers for all 12 palaces; period layer; Bát Tự assessment with the
    methods side by side; chapters with six fixed sections. No language model, no score. Behind TVBT_DEEP_INTERPRETATION (default OFF)."""
    from .synthesis import enabled
    if not enabled():
        raise HTTPException(404, "interpretation engine is disabled")
    from .reasoning.interpretation import run
    nb, bz, tv = _compute(req)
    out = run(tv, bz, req.year, req.to_year or req.year, req.dignity_school)
    if req.level < 5:
        out.pop("dossiers", None)
    return out


@app.post("/api/bazi-structure")
def bazi_structure(req: BirthReq):
    """Bát Tự structure analysis (bazi_deep): khí thế before/after interactions, tương tác, cách cục, dụng thần per method, findings.
    Every rule involved is `draft`; the response says so. No LLM, no storage."""
    from .bazi_deep import pipeline
    from .bazi_deep.model import ChartView
    nb, bz, _ = _compute(req)
    return pipeline.analyse(ChartView.from_bazi(bz, nb.utc, req.gender))


class TimelineReq(BirthReq):
    from_year: int | None = None


@app.post("/api/bazi-timeline")
def bazi_timeline(req: TimelineReq):
    """Extended-chart timeline: for each đại vận and each lưu niên, re-run khí thế / cách cục / cấu trúc / dụng thần on natal + luck (+ year)
    and compare with the natal chart. Draft rules only; describes structure, predicts no event."""
    from .bazi_deep import pipeline
    from .bazi_deep.model import ChartView
    from .bazi_deep.profile import TVH_40 as DEFAULT
    nb, bz, _ = _compute(req)
    y0 = req.from_year or req.year
    y1 = min(req.to_year or req.year + 80, y0 + 120)
    view = ChartView.from_bazi(bz, nb.utc, req.gender)
    luck = [{"index": l.index, "stem": l.stem, "branch": l.branch, "start_year_exact": l.start_year_exact} for l in bz.luck_pillars]
    years = [(y, *temporal.annual_pillar(y)) for y in range(y0, y1 + 1)]
    return pipeline.timeline(view, DEFAULT, luck, years)


@app.post("/api/year")
def year(req: BirthReq):
    nb, bz, tv = _compute(req)
    y = req.to_year or req.year + 30
    out = {"bazi": temporal.bazi_year(bz, req.year, y), "tuvi": temporal.tuvi_year(tv, y)}
    if req.experimental:
        out["experimental"] = _experimental_layers(tv, y)
    return out


def _experimental_layers(tv, year: int) -> dict:
    """Phase-2 draft: how bản mệnh / đại hạn / lưu niên stack on each palace, plus draft interaction rules. Opt-in; production fields above are untouched."""
    from .knowledge.loader import load_experimental_layers
    from .reasoning import layers
    from .reasoning.temporal_facts import time_facts
    r = layers.run_layers(tv, year)
    res = r["result"]
    stack = {k.split(":", 1)[1]: {n[5:]: v for n, v in f.items() if n in ("time.layers", "time.natal_hoa", "time.dai_han_hoa", "time.luu_hoa", "time.ky_layers", "time.loc_layers")}
             for k, f in time_facts(tv, year).items() if k.startswith("palace:")}
    return {"status": "draft", "warning": "Cấu trúc vận hạn đa tầng thử nghiệm, chưa đối chiếu sách; chỉ mô tả cách các tầng chồng lên nhau, không dự báo.",
            "pack_problems": validate_pack(*load_experimental_layers(), {"palace.*", "chart.*", "bazi.*", "derived.*", "time.*"}),
            "layers": r["layers"], "stack_by_palace": stack,
            "findings": [{**dataclasses.asdict(f), "why": _why_vi(res.why(f.id))} for f in r["findings"]],
            "blocked": r["blocked"], "conflicts": r["conflicts"]}


@app.post("/api/twelve-gods")
def twelve(req: BirthReq):
    """Lưu niên thập nhị thần (八字真宗 pp.39-42) for the flow year `to_year` (default: birth year + 30)."""
    from . import bazi_twelve
    nb, bz, tv = _compute(req)
    y = req.to_year or req.year + 30
    yb = temporal.annual_pillar(y)[1]
    luck = temporal.bazi_year(bz, req.year, y)["luck_pillar"]
    return {"year": y, **bazi_twelve.twelve_gods(bz, yb, luck)}


def _merge_corroborated(findings: list[dict], rules) -> list[dict]:
    """One card per (subject, claim): further rules that reach the same claim are listed as corroboration (with their sources)."""
    rmap = {r.id: r for r in rules}
    merged: dict[tuple, dict] = {}
    for f in findings:
        k = (f["subject"], f["claim"], f["effect"])
        if k not in merged:
            f["corroborated_by"] = []
            merged[k] = f
        else:
            first = merged[k]
            first["corroborated_by"].append({"rule_id": f["rule_id"], "sources": rmap[f["rule_id"]].sourceIds, "basis": f["basis"]})
            if f["basis"] == "verified":
                first["basis"] = "verified"
    return list(merged.values())


def _why_vi(why: dict) -> dict:
    """Adds chain_vi: the same chain with fact nodes written in Vietnamese (other nodes unchanged)."""
    from .nlg.generate import pretty_fact
    kinds = list(why.get("kinds", {}).values())
    why["chain_vi"] = [pretty_fact(c) if (kinds[i] if i < len(kinds) else "") == "fact" else c for i, c in enumerate(why["chain"])]
    return why


@app.post("/api/reasoning")
def reasoning(req: BirthReq):
    nb, bz, tv = _compute(req)
    rules, sources = load_all()
    lx.CLAIMS.update(load_claims())
    if req.dignity_school != "thuc_hanh":
        # the temperament readings are Thực Hành's, keyed to ITS brightness table; mixing schools is not verified
        import dataclasses as _dc
        rules = [_dc.replace(r, reviewStatus="draft") if r.category in ("star_dignity", "star_combination") else r for r in rules]
    probs = validate_pack(rules, sources, {"palace.*", "chart.*", "bazi.*", "derived.*"})
    out = {"pack_problems": probs, "systems": {}, "dignity_school": req.dignity_school,
           "mixed_school_warning": req.dignity_school != "thuc_hanh"}
    for system, base in [("tu_vi", facts.tuvi_facts(tv)), ("bat_tu", facts.bazi_facts(bz))]:
        res = engine.run(rules, sources, base, system=system)
        interps = nlg.build_interpretations(res, rules, sources)
        out["systems"][system] = {
            "findings": _merge_corroborated([{**dataclasses.asdict(f), "why": _why_vi(res.why(f.id))} for f in res.findings], rules),
            "pending": res.pending[:20], "blocked": res.blocked, "conflicts": res.conflicts,
            "text": nlg.render(nlg.realize(interps, req.level)),
        }
    if req.experimental:
        out["experimental"] = _experimental(tv, rules, sources)
    return out


def _experimental(tv, rules, sources) -> dict:
    """Phase-1 draft structures (data/experimental): kept apart from `systems` so the production reading is byte-identical."""
    from .knowledge.loader import load_experimental
    from .knowledge.formation import validate_formations
    from .reasoning import conflict
    from .tuvi import PALACES
    xr, xf, xs = load_experimental()
    known = {"palace.*", "chart.*", "bazi.*", "derived.*"}
    problems = validate_formations(xf, known, set(PALACES)) + validate_pack(xr, xs, known)
    allr, alls = rules + xr, sources + [s for s in xs if s.id not in {x.id for x in sources}]
    res = engine.run(allr, alls, facts.tuvi_facts(tv), system="tu_vi", formations=xf)
    xids = {r.id for r in xr} | {f.id for f in xf}
    mine = [f for f in res.findings if f.rule_id in xids]
    return {"status": "draft", "warning": "Cấu trúc thử nghiệm, chưa đối chiếu sách; không thuộc kết quả luận giải chính thức.",
            "pack_problems": problems, "formations": res.formations,
            "findings": [{**dataclasses.asdict(f), "why": _why_vi(res.why(f.id))} for f in mine],
            "blocked": [b for b in res.blocked if b["rule"] in xids],
            "conflicts": [c for c in conflict.resolve(res, allr) if c.get("declared")]}


@app.post("/api/compare-charts")
def compare_charts(a: BirthReq, b: BirthReq):
    """Facts only: the two Nhật Chủ and day branches side by side (see compare.py)."""
    from . import compare
    (na, ba, ta), (nb, bb, tb) = _compute(a), _compute(b)
    return compare.compare_full(na, ba, ta, a.gender, nb, bb, tb, b.gender, a.experimental or b.experimental)


class LunarReq(BaseModel):
    year: int = Field(ge=1900, le=2049); month: int = Field(ge=1, le=12); day: int = Field(ge=1, le=30)
    leap: bool = False; calendar: str = Field("vn", pattern="^(vn|vn_utc7|cn)$")


@app.post("/api/lunar-to-solar")
def lunar_to_solar_endpoint(req: LunarReq):
    """Convert a lunar birthday to the solar date the chart engine expects (exact matches only)."""
    from .lunar_input import lunar_to_solar
    try:
        hits = lunar_to_solar(req.day, req.month, req.year, req.leap, req.calendar)
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not hits:
        raise HTTPException(422, "Không có ngày dương lịch nào khớp với ngày âm lịch này (có thể tháng không có ngày 30 hoặc không phải tháng nhuận).")
    s = hits[0]
    return {"solar": {"year": s.year, "month": s.month, "day": s.day}, "matches": len(hits)}


@app.get("/api/calendar")
def calendar_month(year: int, month: int, calendar: str = "vn", branch: int | None = None):
    """Xem ngày: one month of solar/lunar dates, can chi, solar terms and lục xung with a birth-year branch (computed parts only)."""
    from fastapi.responses import JSONResponse
    from . import xem_ngay
    try:
        body = xem_ngay.month_view(year, month, calendar, branch)
    except ValueError as e:
        raise HTTPException(422, str(e))
    # the same month always gives the same answer: let the browser and the edge keep it
    return JSONResponse(body, headers={"cache-control": "public, max-age=86400"})


@app.post("/api/hour-sweep")
def hour_sweep(req: BirthReq):
    """For an unknown birth hour: what each of the 12 hour branches would give, so the UI can show what does not depend on it."""
    out = []
    for i, name in enumerate(BRANCHES_VI):
        h = 0 if i == 0 else 2 * i
        r = BirthReq(**{**req.model_dump(), "hour": h, "minute": 0})
        nb, bz, tv = _compute(r)
        menh = next(p for p in tv.palaces if p["name"] == "Mệnh")
        out.append({"hour_branch": name, "range": ("23:00–00:59" if i == 0 else f"{2 * i - 1:02d}:00–{2 * i:02d}:59"),
                    "pillars": {k: p.name for k, p in bz.pillars.items()}, "luck_direction": bz.luck_direction,
                    "luck_start": bz.luck_start, "menh_branch": BRANCHES_VI[tv.menh_branch], "than_branch": BRANCHES_VI[tv.than_branch],
                    "menh_stem": menh["stem"], "cuc": tv.cuc["name"], "menh_major_stars": menh["major_stars"],
                    "than_palace": next(p["name"] for p in tv.palaces if p["is_than"])})
    return {"hours": out}


@app.post("/api/compare-hours")
def compare_hours(a: BirthReq, b: BirthReq):
    try:
        return cross.compare_charts(a.birth(), b.birth())
    except Exception as e:
        raise HTTPException(422, str(e))


@app.get("/api/rules")
def rules():
    """Read-only rule & source library. Editing is intentionally not exposed over HTTP (no auth layer yet)."""
    rs, srcs = load_all()
    return {"rules": [dataclasses.asdict(r) for r in rs], "sources": [dataclasses.asdict(x) for x in srcs],
            "problems": validate_pack(rs, srcs, {"palace.*", "chart.*", "bazi.*", "derived.*"})}


class RuleTestReq(BaseModel):
    rule: dict
    birth: BirthReq


@app.post("/api/rules/test")
def rule_test(req: RuleTestReq):
    """Stateless rule editor backend: validate a draft rule (typed DSL, no code execution) and dry-run it on a chart.
    Nothing is stored; publish by committing the rule to a pack file."""
    from .knowledge.schema import KnowledgeRule
    try:
        r = KnowledgeRule(**req.rule)
    except TypeError as e:
        raise HTTPException(422, f"bad rule fields: {e}")
    rs, srcs = load_all()
    problems = validate_pack([r], srcs, {"palace.*", "chart.*", "bazi.*", "derived.*"})
    if problems:
        return {"valid": False, "problems": problems, "findings": []}
    nb, bz, tv = _compute(req.birth)
    base = facts.tuvi_facts(tv) if r.system == "tu_vi" else facts.bazi_facts(bz)
    res = engine.run(rs + [r] if r.id not in {x.id for x in rs} else rs, srcs, base, system=r.system)
    mine = [f for f in res.findings if f.rule_id == r.id]
    return {"valid": True, "problems": [], "fired_on": [f.subject for f in mine],
            "pending": [p for p in res.pending if p["rule"] == r.id][:5],
            "blocked": [b for b in res.blocked if b["rule"] == r.id]}


@app.get("/api/claims")
def claims_vi():
    """Vietnamese phrasing for each claim id, used by the UI to label findings, plus 'tone:<claim>' (+ / - / ~) and 'facet:<claim>' (leading idea, used for chapter routing) read by the semantic lexicon
    (tvbt/synthesis/semantics.py: longest-cue matching with negation), so the plain-language mode never files 'ít mất công lao khó nhọc'
    under 'Điểm cần cân nhắc' because it contains 'khó'."""
    return _claims_with_tone()


@lru_cache(maxsize=1)
def _claims_with_tone() -> dict:
    import json
    from .synthesis.semantics import claim_facet, claim_tone
    raw = json.loads((ROOT / "data" / "claims_vi.json").read_text("utf-8"))
    out = dict(raw)
    for k, v in raw.items():
        if k.startswith("limit:"):
            continue
        t, f = claim_tone(v), claim_facet(v)
        if t:
            out["tone:" + k] = t
        if f:
            out["facet:" + k] = f
    return out


@app.get("/api/dignity/compare")
def dignity_compare():
    from .dignity import compare
    from .ganzhi import BRANCHES_VI
    d = compare(list(BRANCHES_VI))
    return {"disagreements": d, "count": len(d), "schools": ["thuc_hanh", "toan_thu"],
            "note": "Both are published variants; neither is declared correct. The default is Thực Hành."}


@app.get("/api/dignity")
def dignity_table():
    import json
    return json.loads((ROOT / "data" / "dignity_vn.json").read_text("utf-8"))


@app.get("/api/dignity/classify")
def dignity_classify(star: str, branch: str, school: str = "thuc_hanh"):
    """One cell of the shared dignity knowledge base (engine/data/dignity_kb.json): status, level if VERIFIED, source, other books."""
    from fastapi import HTTPException
    from .dignity import classify
    try:
        return classify(star, branch, school)
    except ValueError as e:
        raise HTTPException(422, str(e))


from . import formation_api  # noqa: E402  (opt-in draft cách-cục explanations)
formation_api.register(app, BirthReq, _compute)


@app.get("/library")
def library():
    return FileResponse(ROOT / "web" / "library.html")


@app.get("/")
def index():
    return FileResponse(ROOT / "web" / "index.html")

from . import phi_hoa_api  # noqa: E402  (opt-in draft Phi Hóa school)
phi_hoa_api.register(app, BirthReq, _compute)
from . import growth_api  # noqa: E402  (Personal Growth layer, behind TVBT_GROWTH)
growth_api.register(app, BirthReq, _compute)

# Everything else under web/ (generated article pages, xem-ngay, manifest, service worker, icons): last, so it never shadows an API
# route. Production serves these as Worker static assets; this mount makes a local uvicorn run match.
app.mount("/", StaticFiles(directory=ROOT / "web", html=True), name="web")
