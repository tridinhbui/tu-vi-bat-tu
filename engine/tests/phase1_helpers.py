"""Synthetic charts for Phase-1 tests: a REAL calculated chart (so palace names, branches, stems are genuine) whose stars,
brightness, Tuần/Triệt and Tứ Hóa are replaced by an explicit spec. This isolates the engine from the star-placement tables.

ops (tuples):  ("star", name, palace) · ("hoa", "Hóa Kỵ", palace) · ("triet", palace) · ("tuan", palace) · ("dig", star, palace, level)
Palace names relative to Mệnh are fixed: Thiên Di = xung chiếu, Quan Lộc / Tài Bạch = tam hợp, Huynh Đệ / Phụ Mẫu = giáp (prev / next).
"""
from __future__ import annotations

import copy
import dataclasses
from functools import lru_cache

from tvbt import tuvi
from tvbt.calendar_core import BirthInput, normalize
from tvbt.ganzhi import BRANCHES_VI
from tvbt.knowledge.dsl import evaluate as dsl_eval  # noqa: F401  (re-export for tests)
from tvbt.reasoning import facts

SRC = None


@lru_cache(maxsize=None)
def _real_chart(menh_branch: int):
    for month in range(1, 13):
        for hour in range(0, 24, 2):
            c = tuvi.compute(normalize(BirthInput(1990, month, 15, hour, 10, "Asia/Ho_Chi_Minh", "male")))
            if c.menh_branch == menh_branch:
                return c
    raise AssertionError(f"no real chart with Mệnh at branch {menh_branch}")


def synth(ops=(), menh="Tý"):
    base = _real_chart(BRANCHES_VI.index(menh))
    pal = copy.deepcopy(base.palaces)
    for p in pal:
        p.update(stars=[], major_stars=[], minor_dignity={}, major_dignity={}, tuan=False, triet=False)
    by_name = {p["name"]: p for p in pal}
    hoa: dict = {}
    for op in ops:
        kind = op[0]
        if kind == "star":
            _, s, where = op
            by_name[where]["stars"].append(s)
            if s in tuvi.MAJOR_NAMES:
                by_name[where]["major_stars"].append(s)
        elif kind == "hoa":
            hoa[op[1]] = by_name[op[2]]["branch_index"]
        elif kind in ("triet", "tuan"):
            by_name[op[1]][kind] = True
        elif kind == "dig":
            _, s, where, lv = op
            (by_name[where]["major_dignity"] if s in tuvi.MAJOR_NAMES else by_name[where]["minor_dignity"])[s] = lv
    th = {k: {"star": "?", "branch": hoa.get(k)} for k in ("Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ")}
    return dataclasses.replace(base, palaces=pal, tu_hoa=th)


def base_facts(ops=(), menh="Tý"):
    return facts.tuvi_facts(synth(ops, menh))
