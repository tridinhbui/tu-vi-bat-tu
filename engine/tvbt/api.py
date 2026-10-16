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
    longitude: float | None = None; calendar: str = Field("vn", pattern="^(vn|cn)$")
    zi_rule: str = Field("early_zi_next_day", pattern="^(early_zi_next_day|late_zi_same_day)$")
    use_true_solar_time: bool = False; level: int = Field(3, ge=1, le=5)
    to_year: int | None = None

    def birth(self) -> BirthInput:
        return BirthInput(self.year, self.month, self.day, self.hour, self.minute, self.tz, self.gender,
                          self.longitude, self.calendar, self.zi_rule, self.use_true_solar_time)


def _compute(req: BirthReq):
    try:
        nb = normalize(req.birth())
    except Exception as e:  # invalid date, DST gap, unknown tz, missing longitude
        raise HTTPException(422, str(e))
    return nb, bazi.compute(nb), tuvi.compute(nb)


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
    probs = validate_pack(rules, sources, {"palace.*", "chart.*", "bazi.*", "derived.*"})
    out = {"pack_problems": probs, "systems": {}}
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


@app.get("/")
def index():
    return FileResponse(ROOT / "web" / "index.html")
