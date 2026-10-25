"""Kinh Dịch and Mai Hoa casts: stateless, the request carries everything the cast is computed from (coin faces, line values, or the
moment and numbers of a Mai Hoa cast), so a stored cast can always be recomputed. Facts only; the reading is on the Worker."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel, Field, model_validator

from .kinh_dich import coins, core, doc_hao, mai_hoa

Face = Literal["lung", "chu"]


class KinhDichReq(BaseModel):
    tosses: list[list[Face]] | None = None              # six tosses of three coins, hào 1 first
    values: list[int] | None = None                     # or six line values 6/7/8/9
    hexagram: int | None = Field(None, ge=1, le=64)     # or a King Wen number with the moving hào
    moving: list[int] = []

    @model_validator(mode="after")
    def one_input(self):
        if sum(x is not None for x in (self.tosses, self.values, self.hexagram)) != 1:
            raise ValueError("give exactly one of tosses, values, hexagram")
        return self


class MaiHoaReq(BaseModel):
    method: Literal["thoi_gian", "vat_so", "thanh_am", "chu", "truong_xich", "xich_thon", "vat_phuong"]
    moment: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}")   # local time in Việt Nam when the cast is made
    count: int | None = Field(None, ge=1, le=100000)
    words: int | None = Field(None, ge=11, le=1000)
    zhang: int | None = Field(None, ge=1, le=1000)
    chi: int | None = Field(None, ge=1, le=1000)
    cun: int | None = Field(None, ge=1, le=1000)
    object_trigram: str | None = None
    direction: str | None = None
    # the four numbers of 年月日時起例 typed by hand (e.g. to replay a book example); otherwise read from the moment
    year_branch: int | None = Field(None, ge=1, le=12)
    lunar_month: int | None = Field(None, ge=1, le=12)
    lunar_day: int | None = Field(None, ge=1, le=30)
    hour_branch: int | None = Field(None, ge=1, le=12)


def kinh_dich_cast(req: KinhDichReq) -> dict:
    if req.tosses is not None:
        values = coins.values_from_tosses(req.tosses)
        c = core.cast(values)
        c["tosses"] = req.tosses
        c["cites"]["coins"] = coins.COIN_CITE
    elif req.values is not None:
        c = core.cast(req.values)
    else:
        c = core.from_hexagram(req.hexagram, req.moving)
    c["system"] = "kinh_dich"
    c["reading_rule"] = doc_hao.resolve(c)
    return c


def mai_hoa_cast(req: MaiHoaReq) -> dict:
    t = mai_hoa.time_inputs(datetime.fromisoformat(req.moment[:16]))
    hour = req.hour_branch or t["hour_branch"]
    month = req.lunar_month or t["month"]
    m = req.method
    if m == "thoi_gian":
        manual = [req.year_branch, req.lunar_month, req.lunar_day, req.hour_branch]
        if any(x is not None for x in manual) and not all(x is not None for x in manual):
            raise ValueError("give all four of year_branch, lunar_month, lunar_day, hour_branch, or none")
        if all(x is not None for x in manual):
            r = mai_hoa.by_time(req.year_branch, req.lunar_month, req.lunar_day, req.hour_branch)
        else:
            r = mai_hoa.by_time(t["year_branch"], t["month"], t["day"], t["hour_branch"], leap=t["leap"])
            r["notes"].append(mai_hoa.TIME_NOTE)
    elif m in ("vat_so", "thanh_am"):
        if req.count is None:
            raise ValueError("count is required")
        r = (mai_hoa.by_count if m == "vat_so" else mai_hoa.by_sound)(req.count, hour, month=month)
    elif m == "chu":
        if req.words is None:
            raise ValueError("words is required")
        r = mai_hoa.by_words(req.words, month=month)
    elif m == "truong_xich":
        if req.zhang is None or req.chi is None:
            raise ValueError("zhang and chi are required")
        r = mai_hoa.by_zhang_chi(req.zhang, req.chi, month=month)
    elif m == "xich_thon":
        if req.chi is None or req.cun is None:
            raise ValueError("chi and cun are required")
        r = mai_hoa.by_chi_cun(req.chi, req.cun, hour, month=month)
    else:
        if req.object_trigram is None or req.direction is None:
            raise ValueError("object_trigram and direction are required")
        r = mai_hoa.by_object_direction(req.object_trigram, req.direction, hour, month=month)
    r["system"] = "mai_hoa"
    r["moment"] = req.moment[:16]
    r["calendar"] = t
    return r


def register(app):
    @app.post("/api/kinh-dich/cast")
    def kinh_dich(req: KinhDichReq):
        try:
            return kinh_dich_cast(req)
        except ValueError as e:
            raise HTTPException(422, str(e))

    @app.post("/api/mai-hoa/cast")
    def mai_hoa_route(req: MaiHoaReq):
        try:
            return mai_hoa_cast(req)
        except ValueError as e:
            raise HTTPException(422, str(e))
