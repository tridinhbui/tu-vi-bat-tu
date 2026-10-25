"""HTTP routes of the Western module, mounted by tvbt.api under /api/west. Stateless: nothing is stored."""
from __future__ import annotations

import copy
import datetime as _dt
import json
import threading
from collections import OrderedDict

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from . import chart as C, ephemeris as E, places, progressions as _P, returns as _R, transits as _T
from .timeutil import TimeError

router = APIRouter(prefix="/api/west", tags=["western"])
_UTC = _dt.timezone.utc
# The container is small (one process shared with Tử Vi and Bát Tự): Western computations run one at a time, so a burst of
# chart pages queues instead of starving everything else, and the natal chart is cached because one page asks for it in
# several requests (chart, reading, transits, progressions, profections).
_HEAVY = threading.BoundedSemaphore(1)
_CACHE: "OrderedDict[str, dict]" = OrderedDict()
_CACHE_LOCK = threading.Lock()


class BirthIn(BaseModel):
    year: int = Field(ge=1900, le=2100); month: int = Field(ge=1, le=12); day: int = Field(ge=1, le=31)
    hour: int | None = Field(None, ge=0, le=23); minute: int | None = Field(None, ge=0, le=59); second: int = Field(0, ge=0, le=59)
    lat: float = Field(ge=-90, le=90); lon: float = Field(ge=-180, le=180); tz: str = Field(min_length=1, max_length=64)
    place: str = Field("", max_length=120); name: str = Field("", max_length=80)
    fold: int = Field(0, ge=0, le=1); utc_offset_hours: float | None = Field(None, ge=-14, le=14)

    def birth(self) -> C.BirthData:
        return C.BirthData.from_dict(self.model_dump())


class OptionsIn(BaseModel):
    house_system: str = Field("placidus", pattern="^(placidus|whole_sign|equal|porphyry|regiomontanus)$")
    node: str = Field("true", pattern="^(true|mean)$")
    orbs: str = Field("thienban", pattern="^(thienban|lilly)$")
    minor_aspects: bool = True
    triplicity: str = Field("dorothean", pattern="^(dorothean|ptolemaic)$")
    terms: str = Field("egyptian", pattern="^(egyptian|ptolemaic|lilly)$")
    rulers: str = Field("traditional", pattern="^(traditional|modern)$")
    lot_rule: str = Field("ptolemy", pattern="^(ptolemy|valens|sect)$")
    solar_phase: str = Field("traditional", pattern="^traditional$")


class ChartReq(BaseModel):
    birth: BirthIn
    options: OptionsIn = OptionsIn()


def chart_or_422(birth: BirthIn, options: OptionsIn) -> dict:
    key = json.dumps([birth.model_dump(), options.model_dump()], sort_keys=True)
    with _CACHE_LOCK:
        hit = _CACHE.get(key)
        if hit is not None:
            _CACHE.move_to_end(key)
            return copy.deepcopy(hit)
    try:
        out = C.compute(birth.birth(), C.ChartOptions.from_dict(options.model_dump()))
    except (TimeError, E.OutOfRange, ValueError) as e:
        raise HTTPException(422, str(e))
    with _CACHE_LOCK:
        _CACHE[key] = out
        while len(_CACHE) > 64:
            _CACHE.popitem(last=False)
    return copy.deepcopy(out)


@router.get("/places")
def places_search(q: str = Query(min_length=2, max_length=80), limit: int = Query(10, ge=1, le=25)):
    return {"results": places.search(q, limit), "attribution": places.attribution()}


@router.post("/chart")
def natal(req: ChartReq):
    with _HEAVY:
        return _natal(req)


def _natal(req):
    return chart_or_422(req.birth, req.options)


# ---- forecasting ------------------------------------------------------------------------------------------------------


def _date(s: str) -> _dt.datetime:
    try:
        d = _dt.datetime.fromisoformat(s)
    except ValueError as e:
        raise HTTPException(422, f"ngày không hợp lệ: {s}") from e
    return d if d.tzinfo else d.replace(tzinfo=_UTC)


class TransitReq(ChartReq):
    start: str
    end: str
    transiting: list[str] | None = None
    aspects: list[str] = ["conjunction", "opposition", "trine", "square", "sextile"]


@router.post("/transits")
def transits(req: TransitReq):
    with _HEAVY:
        return _transits(req)


def _transits(req):
    a, b = _date(req.start), _date(req.end)
    bodies = tuple(req.transiting or [x for x in _T.TRANSITING if x != "moon"])
    if not set(bodies) <= set(_T.TRANSITING) or not set(req.aspects) <= {"conjunction", "opposition", "trine", "square", "sextile",
                                                                           "quincunx", "semisextile", "semisquare", "sesquiquadrate"}:
        raise HTTPException(422, "hành tinh hoặc góc hợp không hợp lệ")
    limit = 370 if "moon" in bodies else 3 * 366 + 1
    if not (0 < (b - a).days <= limit):
        raise HTTPException(422, f"khoảng thời gian phải dương và không quá {limit} ngày")
    natal = chart_or_422(req.birth, req.options)
    try:
        ev = _T.find(natal, a, b, transiting=bodies, aspects=tuple(req.aspects))
        sky = _T.ingresses_and_stations(a, b, bodies=tuple(x for x in bodies if x != "moon"))
    except E.OutOfRange as e:
        raise HTTPException(422, str(e))
    _score(natal, a, ev)
    from .reading.milestones import NOTABLE
    return {"start": a.isoformat(), "end": b.isoformat(), "orbs": _T.orb_table(), "events": ev, "sky": sky, "notable": NOTABLE,
            "score_note": "Điểm chọn mốc nổi bật (quy ước Thiên Bàn, western/reading/milestones.py): hành tinh đi qua (Mộc, Thổ, Thiên Vương 3; "
                          "Hỏa, Hải Vương, Diêm Vương, Chiron 1), điểm gốc (chủ năm +3, Mặt Trời/Mặt Trăng/ASC/MC +2, hành tinh khác +1), loại góc "
                          "(trùng tụ 3, đối và vuông 2, tam hợp và lục hợp 1), chính xác trong khung +1, lặp lại trong một vòng nghịch hành +1."}


def _score(natal: dict, when: _dt.datetime, ev: list[dict]) -> None:
    """Each event gets the score of its retrograde loop (western/reading/milestones.py), so the timeline can show only the notable ones."""
    from .reading import milestones as MS
    lord = None
    if "angles" in natal:
        try:
            lord = _R.profection(natal, _R.age_at(natal, when))["lord"]
        except (E.OutOfRange, ValueError):
            lord = None
    by = {r.get("cycle"): r for r in MS.rank(ev, natal, lord)}
    for e in ev:
        r = by.get(e.get("cycle"))
        e["score"], e["score_parts"] = (r["score"], r["score_parts"]) if r else (0, [])


class ProgressionReq(ChartReq):
    when: str
    angle_method: str = Field("solar_arc", pattern="^(solar_arc|solar_arc_ra|naibod)$")
    span_years: float = Field(5, ge=0.5, le=30)


@router.post("/progressions")
def progressions(req: ProgressionReq):
    with _HEAVY:
        return _progressions(req)


def _progressions(req):
    natal = chart_or_422(req.birth, req.options)
    when = _date(req.when)
    try:
        now = _P.chart(natal, when, req.angle_method)
        age = now["age_years"]
        tl = _P.timeline(natal, max(0.0, age - req.span_years / 2), age + req.span_years / 2)
    except E.OutOfRange as e:
        raise HTTPException(422, str(e))
    return {"natal_time": natal["time"], "progressed": now, "timeline": tl}


class ProfectionReq(ChartReq):
    when: str | None = None
    age: int | None = Field(None, ge=0, le=110)
    method: str = Field("whole_sign", pattern="^(whole_sign|degree)$")


@router.post("/profections")
def profections(req: ProfectionReq):
    with _HEAVY:
        return _profections(req)


def _profections(req):
    natal = chart_or_422(req.birth, req.options)
    if "angles" not in natal:
        raise HTTPException(422, "Annual profection cần giờ sinh: cung Mọc là điểm xuất phát")
    age = req.age if req.age is not None else _R.age_at(natal, _date(req.when) if req.when else _dt.datetime.now(_UTC))
    try:
        cur = _R.profection(natal, age, req.method)
    except E.OutOfRange as e:
        raise HTTPException(422, str(e))
    return {"current": cur, "cycle": _R.profection_cycle(natal, 96, req.method)}


class ReturnReq(ChartReq):
    year: int = Field(ge=1900, le=2100)
    lat: float | None = Field(None, ge=-90, le=90)
    lon: float | None = Field(None, ge=-180, le=180)
    tz: str | None = None
    place: str = ""


@router.post("/solar-return")
def solar_return(req: ReturnReq):
    with _HEAVY:
        return _solar_return(req)


def _solar_return(req):
    natal = chart_or_422(req.birth, req.options)
    if (req.lat is None) != (req.tz is None):
        raise HTTPException(422, "cần đủ vĩ độ, kinh độ và múi giờ của nơi xem Solar Return")
    try:
        return _R.solar_return(natal, req.year, req.lat, req.lon, req.tz, req.place, C.ChartOptions.from_dict(req.options.model_dump()))
    except (TimeError, E.OutOfRange, ValueError) as e:
        raise HTTPException(422, str(e))


# ---- reading ----------------------------------------------------------------------------------------------------------
class ReadingReq(ChartReq):
    mode: str = Field("deep", pattern="^(overview|deep)$")
    gender: str | None = Field(None, pattern="^(male|female)$")
    when: str | None = None


@router.post("/reading")
def reading(req: ReadingReq):
    with _HEAVY:
        return _reading(req)


# Whole readings (mode "deep") of the last charts read: switching Tổng quan / Đọc sâu, reloading or opening a package after reading
# serves from here. A reading for "now" is kept for the day (Thời vận names the date only).
_READINGS: "OrderedDict[str, dict]" = OrderedDict()


def _reading(req):
    from .reading import build, overview_of
    natal = chart_or_422(req.birth, req.options)
    when = _date(req.when) if req.when else _dt.datetime.now(_UTC)
    key = json.dumps([req.birth.model_dump(), req.options.model_dump(), req.gender, req.when or when.date().isoformat()], sort_keys=True)
    with _CACHE_LOCK:
        full = _READINGS.get(key)
        if full is not None:
            _READINGS.move_to_end(key)
    if full is None:
        try:
            full = build(natal, "deep", req.gender, when)
        except E.OutOfRange as e:
            raise HTTPException(422, str(e))
        with _CACHE_LOCK:
            _READINGS[key] = full
            while len(_READINGS) > 32:
                _READINGS.popitem(last=False)
    return overview_of(full) if req.mode == "overview" else copy.deepcopy(full)


# ---- synastry ---------------------------------------------------------------------------------------------------------
class SynastryReq(BaseModel):
    a: BirthIn
    b: BirthIn
    options: OptionsIn = OptionsIn()
    gender_a: str | None = Field(None, pattern="^(male|female)$")
    gender_b: str | None = Field(None, pattern="^(male|female)$")


@router.post("/synastry")
def synastry(req: SynastryReq):
    with _HEAVY:
        return _synastry(req)


def _synastry(req):
    from . import synastry as S
    from .reading import synastry as RS
    ca, cb = chart_or_422(req.a, req.options), chart_or_422(req.b, req.options)
    syn = S.compare(ca, cb, req.options.orbs)
    return {"a": ca, "b": cb, "synastry": syn, "reading": RS.build(syn, gender_a=req.gender_a, gender_b=req.gender_b)}
