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


@app.post("/api/year")
def year(req: BirthReq):
    nb, bz, tv = _compute(req)
    y = req.to_year or req.year + 30
    return {"bazi": temporal.bazi_year(bz, req.year, y), "tuvi": temporal.tuvi_year(tv, y)}


@app.post("/api/reasoning")
def reasoning(req: BirthReq):
    nb, bz, tv = _compute(req)
    rules, sources = load_all()
    lx.CLAIMS.update(load_claims())
    if req.dignity_school != "thuc_hanh":
        # the temperament readings are Thực Hành's, keyed to ITS brightness table; mixing schools is not verified
        import dataclasses as _dc
        rules = [_dc.replace(r, reviewStatus="draft") if r.category == "star_dignity" else r for r in rules]
    probs = validate_pack(rules, sources, {"palace.*", "chart.*", "bazi.*", "derived.*"})
    out = {"pack_problems": probs, "systems": {}, "dignity_school": req.dignity_school,
           "mixed_school_warning": req.dignity_school != "thuc_hanh"}
    for system, base in [("tu_vi", facts.tuvi_facts(tv)), ("bat_tu", facts.bazi_facts(bz))]:
        res = engine.run(rules, sources, base, system=system)
        interps = nlg.build_interpretations(res, rules, sources)
        out["systems"][system] = {
            "findings": [{**dataclasses.asdict(f), "why": res.why(f.id)} for f in res.findings],
            "pending": res.pending[:20], "blocked": res.blocked, "conflicts": res.conflicts,
            "text": nlg.render(nlg.realize(interps, req.level)),
        }
    return out


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
