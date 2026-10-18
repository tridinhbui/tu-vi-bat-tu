"""Personal Growth endpoints (tvbt/growth). Behind TVBT_GROWTH (default OFF): with the flag off every route answers 404 and no other endpoint
changes. All routes are stateless: birth data and journal entries are processed in memory and never stored."""

from datetime import date
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field


class Concern(BaseModel):
    text: str = Field("", max_length=400)
    zone: str = Field("unsure", pattern="^(control|influence|outside|unsure)$")


class Entry(BaseModel):
    date: str = Field(max_length=32)
    text: str = Field("", max_length=4000)
    domain: Optional[str] = Field(None, max_length=16)
    mood: Optional[int] = Field(None, ge=1, le=5)
    insight_id: Optional[str] = Field(None, max_length=80)
    resonance: Optional[str] = Field(None, pattern="^(dung|mot_phan|khong)$")
    practice_id: Optional[str] = Field(None, max_length=90)
    practice_done: bool = False


class Ctx(BaseModel):
    situation: str = Field("", max_length=1500)
    domain: Optional[str] = Field(None, max_length=16)
    values: list[str] = Field(default_factory=list, max_length=8)


def register(app, birth_model, compute):
    def guard():
        from .growth import enabled
        if not enabled():
            raise HTTPException(404, "growth layer is disabled")

    def profile_of(req):
        from .bazi_deep import pipeline
        from .bazi_deep.model import ChartView
        from .growth import profile, signals
        nb, bz, tv = compute(req)
        deep = pipeline.analyse(ChartView.from_bazi(bz, nb.utc, req.gender))
        sg = signals.read(tv, bz, deep, req.to_year or date.today().year)
        return profile.build(sg)

    class NavReq(BaseModel):
        birth: birth_model  # type: ignore[valid-type]
        domain: str = Field("self", max_length=16)
        situation: str = Field("", max_length=1500)
        concerns: list[Concern] = Field(default_factory=list, max_length=20)
        duration: str = Field("", max_length=40)
        tried: str = Field("", max_length=1000)

    class DecideReq(BaseModel):
        birth: birth_model  # type: ignore[valid-type]
        domain: str = Field("career", max_length=16)
        decision: str = Field("", max_length=600)
        options: list[str] = Field(default_factory=list, max_length=4)
        values: list[str] = Field(default_factory=list, max_length=5)
        ratings: dict[str, dict[str, int]] = Field(default_factory=dict)

    class JournalReq(BaseModel):
        birth: birth_model  # type: ignore[valid-type]
        entries: list[Entry] = Field(default_factory=list, max_length=1000)

    class DialogueReq(BaseModel):
        birth: birth_model  # type: ignore[valid-type]
        question: str = Field(min_length=1, max_length=600)
        context: Ctx = Field(default_factory=Ctx)
        exclude: list[str] = Field(default_factory=list, max_length=60)

    @app.post("/api/growth/profile")
    def growth_profile(req: birth_model):  # type: ignore[valid-type]
        """Life lessons, blind spots, compass per domain, current-stage lens, practices. Draft; three layers per insight."""
        guard()
        return profile_of(req)

    @app.post("/api/growth/navigate")
    def growth_navigate(req: NavReq):
        guard()
        from .growth.navigator import navigate
        return navigate(profile_of(req.birth), req.domain, req.situation, [c.model_dump() for c in req.concerns], req.duration, req.tried)

    @app.post("/api/growth/compass")
    def growth_compass(req: DecideReq):
        guard()
        from .growth.decide import decide
        return decide(profile_of(req.birth), req.domain, req.decision, req.options, req.values, req.ratings)

    @app.post("/api/growth/journal-review")
    def growth_journal(req: JournalReq):
        guard()
        from .growth.journal import review
        return review(profile_of(req.birth), [e.model_dump() for e in req.entries])

    @app.post("/api/growth/dialogue")
    def growth_dialogue(req: DialogueReq):
        guard()
        from .growth.dialogue import answer
        return answer(profile_of(req.birth), req.question, req.context.model_dump(), req.exclude)
