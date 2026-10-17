"""HTTP API + static UI host. No external AI calls. Birth data is processed in-memory and never stored."""
from __future__ import annotations

import dataclasses
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
    longitude: float | None = None; calendar: str = Field("vn", pattern="^(vn|vn_south|cn)$")
    zi_rule: str = Field("early_zi_next_day", pattern="^(early_zi_next_day|late_zi_same_day)$")
    use_true_solar_time: bool = False; level: int = Field(3, ge=1, le=5)
    to_year: int | None = None
    dignity_school: str = Field("thuc_hanh", pattern="^(thuc_hanh|toan_thu)$")
    experimental: bool = False      # opt-in: also evaluate the DRAFT cách cục + engine-demo rules (never part of production readings)

    def birth(self) -> BirthInput:
        return BirthInput(self.year, self.month, self.day, self.hour, self.minute, self.tz, self.gender,
                          self.longitude, self.calendar, self.zi_rule, self.use_true_solar_time)


def _compute(req: BirthReq):
    try:
        nb = normalize(req.birth())
    except Exception as e:  # invalid date, DST gap, unknown tz, missing longitude
        raise HTTPException(422, str(e))
    return nb, bazi.compute(nb), tuvi.compute(nb, dignity_school=req.dignity_school)


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


@app.post("/api/bazi-structure")
def bazi_structure(req: BirthReq):
    """Bát Tự structure analysis (bazi_deep): khí thế before/after interactions, tương tác, cách cục, dụng thần per method, findings.
    Every rule involved is `draft`; the response says so. No LLM, no storage."""
    from .bazi_deep import pipeline
    from .bazi_deep.model import ChartView
    nb, bz, _ = _compute(req)
    return pipeline.analyse(ChartView.from_bazi(bz, nb.utc, req.gender))


@app.post("/api/year")
def year(req: BirthReq):
    nb, bz, tv = _compute(req)
    y = req.to_year or req.year + 30
    return {"bazi": temporal.bazi_year(bz, req.year, y), "tuvi": temporal.tuvi_year(tv, y)}


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


class LunarReq(BaseModel):
    year: int = Field(ge=1900, le=2049); month: int = Field(ge=1, le=12); day: int = Field(ge=1, le=30)
    leap: bool = False; calendar: str = Field("vn", pattern="^(vn|cn)$")


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
    """Vietnamese phrasing for each claim id, used by the UI to label findings."""
    import json
    return json.loads((ROOT / "data" / "claims_vi.json").read_text("utf-8"))


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


@app.get("/library")
def library():
    return FileResponse(ROOT / "web" / "library.html")


@app.get("/")
def index():
    return FileResponse(ROOT / "web" / "index.html")
