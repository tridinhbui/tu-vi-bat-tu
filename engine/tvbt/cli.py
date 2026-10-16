import argparse
import dataclasses
import json

from . import bazi, tuvi
from .calendar_core import BirthInput, normalize


def main():
    p = argparse.ArgumentParser(description="Compute Tu Vi + Bat Tu facts (no interpretation).")
    p.add_argument("date", help="YYYY-MM-DD"); p.add_argument("time", help="HH:MM")
    p.add_argument("--tz", default="Asia/Ho_Chi_Minh"); p.add_argument("--gender", choices=["male", "female"], required=True)
    p.add_argument("--lon", type=float); p.add_argument("--calendar", choices=["vn", "cn"], default="vn")
    p.add_argument("--zi", choices=["early_zi_next_day", "late_zi_same_day"], default="early_zi_next_day")
    p.add_argument("--true-solar", action="store_true")
    a = p.parse_args()
    y, m, d = map(int, a.date.split("-")); h, mi = map(int, a.time.split(":"))
    nb = normalize(BirthInput(y, m, d, h, mi, a.tz, a.gender, a.lon, a.calendar, a.zi, a.true_solar))
    out = {"bazi": dataclasses.asdict(bazi.compute(nb)), "tuvi": dataclasses.asdict(tuvi.compute(nb)),
           "normalization_trace": dataclasses.asdict(nb.trace)}
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
