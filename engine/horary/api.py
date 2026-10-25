"""HTTP API for horary (mounted at /api/horary by tvbt/api.py). Stateless: the container stores nothing; saved questions
live in the Worker's D1 (src/horary/), which sends back the stored input to recompute the same chart."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from . import chart as C, houses as H, judgment as J, kb, narrative as N, questions as Q
from .astro import TRAD

router = APIRouter(prefix="/api/horary", tags=["horary"])
SCHOOLS = {"lilly": {"vi": "Lilly (Christian Astrology, 1647)", "house_system": "regiomontanus", "near_cusp_deg": 5.0,
                     "fortune": "lilly", "node": "mean"}}


class Moment(BaseModel):
    year: int = Field(ge=1600, le=2150)
    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=31)
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)
    second: int = Field(0, ge=0, le=59)
    tz: str = Field("Asia/Ho_Chi_Minh", max_length=64)
    lat: float = Field(ge=-89.9, le=89.9)
    lon: float = Field(ge=-180, le=180)
    place: str = Field("", max_length=120)
    fold: int = Field(0, ge=0, le=1)
    utc_offset_hours: float | None = Field(None, ge=-14, le=14)
    julian_calendar: bool = False
    house_system: str | None = Field(None, pattern="^(regiomontanus|alcabitius|whole_sign|placidus|equal|porphyry)$")
    school: str = Field("lilly", pattern="^lilly$")

    def to_input(self) -> C.HoraryInput:
        s = SCHOOLS[self.school]
        return C.HoraryInput(self.year, self.month, self.day, self.hour, self.minute, self.tz, self.lat, self.lon, self.second,
                             self.fold, self.place, self.utc_offset_hours, self.house_system or s["house_system"], s["node"],
                             s["fortune"], s["near_cusp_deg"], self.julian_calendar)


class FrameIn(BaseModel):
    text: str = Field(min_length=3, max_length=500)
    topic: str
    subtype: str
    party: str = "self"
    quesited_house: int | None = Field(None, ge=1, le=12)
    confirmed: bool = False


class ClassifyReq(BaseModel):
    text: str = Field(min_length=1, max_length=500)


class JudgeReq(BaseModel):
    moment: Moment
    frame: FrameIn
    fingerprint: str | None = None         # from a saved question: the response says whether the chart is unchanged


def _chart(m: Moment) -> C.HoraryChart:
    try:
        return C.compute(m.to_input())
    except H.PolarHouses as e:
        raise HTTPException(422, str(e))
    except Exception as e:  # noqa: BLE001 - invalid date / DST gap / unknown zone come back as 422 with the reason
        if e.__class__.__name__ in ("TimeError", "ValueError", "OutOfRange"):
            raise HTTPException(422, str(e))
        raise


def chart_view(ch: C.HoraryChart) -> dict:
    d = ch.as_dict()
    d["fingerprint"] = C.fingerprint(ch)
    d["traditional"] = list(TRAD)
    return d


@router.get("/catalog")
def catalog():
    return {"topics": {k: {"vi": v["vi"], "subtypes": {s: {"vi": x["vi"], "house": x["house"]} for s, x in v["subtypes"].items()},
                           "caution": Q.CAUTIONS.get(v.get("caution", ""))} for k, v in Q.TOPICS.items()},
            "parties": Q.PARTIES, "restricted": Q.RESTRICTED, "house_systems": H.SYSTEMS, "schools": SCHOOLS,
            "disclaimer": N.DISCLAIMER}


@router.post("/classify")
def classify(req: ClassifyReq):
    return Q.classify(req.text).as_dict()


@router.post("/chart")
def chart(m: Moment):
    return chart_view(_chart(m))


@router.post("/judge")
def judge(req: JudgeReq):
    if not req.frame.confirmed:
        raise HTTPException(400, "Câu hỏi chưa được xác nhận: hãy xác nhận chủ đề và cách hiểu trước khi luận.")
    restricted = Q.classify(req.frame.text).restricted
    if restricted:
        raise HTTPException(422, {"restricted": restricted})
    try:
        fr = Q.Frame(req.frame.text, req.frame.topic, req.frame.subtype, req.frame.party, req.frame.quesited_house, True).resolve()
    except ValueError as e:
        raise HTTPException(422, str(e))
    fr["text"] = req.frame.text
    ch = _chart(req.moment)
    j = J.judge(ch, fr)
    fp = C.fingerprint(ch)
    return {"chart": chart_view(ch), "judgment": j, "reading": N.compose(ch, fr, j),
            "unchanged": None if req.fingerprint is None else req.fingerprint == fp, "fingerprint": fp, "engine": C.ENGINE_VERSION}


@router.get("/rules")
def rules():
    return {"works": kb.WORKS, "rules": [{k: r.get(k) for k in ("id", "category", "title_vi", "title_en", "statement_vi", "effect",
                                                                  "school", "status", "engine_choice", "dispute", "sources")}
                                         for r in kb.rules().values()]}
