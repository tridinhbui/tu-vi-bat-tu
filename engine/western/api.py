"""HTTP routes of the Western module, mounted by tvbt.api under /api/west. Stateless: nothing is stored."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from . import chart as C, ephemeris as E, places
from .timeutil import TimeError

router = APIRouter(prefix="/api/west", tags=["western"])


class BirthIn(BaseModel):
    year: int = Field(ge=1900, le=2100); month: int = Field(ge=1, le=12); day: int = Field(ge=1, le=31)
    hour: int | None = Field(None, ge=0, le=23); minute: int | None = Field(None, ge=0, le=59); second: int = Field(0, ge=0, le=59)
    lat: float = Field(ge=-90, le=90); lon: float = Field(ge=-180, le=180); tz: str = Field(min_length=1, max_length=64)
    place: str = Field("", max_length=120); name: str = Field("", max_length=80)
    fold: int = Field(0, ge=0, le=1); utc_offset_hours: float | None = Field(None, ge=-14, le=14)

    def birth(self) -> C.BirthData:
        return C.BirthData.from_dict(self.model_dump())


class OptionsIn(BaseModel):
    house_system: str = Field("placidus", pattern="^(placidus|whole_sign|equal|porphyry)$")
    node: str = Field("true", pattern="^(true|mean)$")
    orbs: str = Field("thienban", pattern="^(thienban|lilly)$")
    minor_aspects: bool = True
    triplicity: str = Field("dorothean", pattern="^(dorothean|ptolemaic)$")
    terms: str = Field("egyptian", pattern="^(egyptian|ptolemaic)$")
    rulers: str = Field("traditional", pattern="^(traditional|modern)$")
    lot_reversal: bool = True
    solar_phase: str = Field("traditional", pattern="^(traditional|hellenistic)$")


class ChartReq(BaseModel):
    birth: BirthIn
    options: OptionsIn = OptionsIn()


def chart_or_422(birth: BirthIn, options: OptionsIn) -> dict:
    try:
        return C.compute(birth.birth(), C.ChartOptions.from_dict(options.model_dump()))
    except (TimeError, E.OutOfRange, ValueError) as e:
        raise HTTPException(422, str(e))


@router.get("/places")
def places_search(q: str = Query(min_length=2, max_length=80), limit: int = Query(10, ge=1, le=25)):
    return {"results": places.search(q, limit), "attribution": places.attribution()}


@router.post("/chart")
def natal(req: ChartReq):
    return chart_or_422(req.birth, req.options)
