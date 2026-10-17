"""Intake validator for the human blind check of the 10 worked examples (Thiệu Vĩ Hoa tr.387-401).
The reviewer fills docs/bazi_deep_examples_review_sheet.csv (one row per example pillar; the sheet contains NO engine value, so the reading is blind) with the pillar as printed
(e.g. 'Quý Mão'). This tool compares with tests/golden/tvh_dungthan_examples.json and reports per pillar and per example. It never edits data and never raises a verification level:
  pillar status:  no_review | confirmed_1 | confirmed_2 | disagrees | reconstructed_not_independent
  A pillar whose provenance is 'derived' or 'reconstructed' (example 4) can only reach 'reconstructed_not_independent': a person who reads the same broken page and agrees with the
  reconstruction has not confirmed the original data.
  example status: 'fully_confirmed' only when all four pillars are directly read AND confirmed by >= 1 human; otherwise 'incomplete' (with the reason) or 'no_review'.
Usage: python tools/bazi_deep_examples_review_intake.py filled1.csv [filled2.csv]"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GOLD = json.loads((ROOT / "engine/tests/golden/tvh_dungthan_examples.json").read_text("utf-8"))
PIL = ("year", "month", "day", "hour")
NORM = {"kỉ": "Kỷ", "kì": "Kỷ", "tị": "Tỵ", "tí": "Tý", "quí": "Quý"}


def _norm(x: str) -> str:
    out = []
    for w in (x or "").split():
        w = NORM.get(w.lower(), w.lower())
        out.append(w[:1].upper() + w[1:])
    return " ".join(out)


def examples() -> dict:
    out = {}
    for sec in ("dieuhau_examples", "dungthan_examples"):
        for k, v in GOLD[sec].items():
            if not k.startswith("_"):
                out[k] = v
    return out


def check(files: list) -> dict:
    ex = examples()
    problems, seen = [], {}
    for fi, src in enumerate(files):
        rows = src if isinstance(src, list) else list(csv.DictReader(open(src, encoding="utf-8", newline="")))
        keys = sorted((r["vi_du"], r["tru"]) for r in rows)
        if keys != sorted((k, p) for k in ex for p in PIL):
            problems.append(f"file {fi}: does not contain exactly the 40 (ví dụ, trụ) rows")
        for r in rows:
            who, seen_p = (r.get("nguoi_kiem") or "").strip(), (r.get("tru_theo_anh") or "").strip()
            if not who and not seen_p:
                continue
            if not who or not seen_p:
                problems.append(f"{r['vi_du']}/{r['tru']}: needs both nguoi_kiem and tru_theo_anh")
                continue
            seen.setdefault((r["vi_du"], r["tru"]), []).append((who, _norm(seen_p)))
    res = {}
    for k, v in ex.items():
        gold = [x.strip() for x in v["pillars"].split("/")]
        pills = {}
        for p, g in zip(PIL, gold):
            revs = seen.get((k, p), [])
            prov = v["pillar_provenance"][p]
            if not revs:
                st = "no_review"
            elif any(s != g for _, s in revs):
                st = "disagrees"
            elif prov != "read_directly":
                st = "reconstructed_not_independent"
            else:
                st = "confirmed_2" if len({w for w, _ in revs}) >= 2 else "confirmed_1"
            pills[p] = {"status": st, "provenance": prov, "reviewers": [w for w, _ in revs]}
        sts = {x["status"] for x in pills.values()}
        if sts == {"no_review"}:
            ex_st, why = "no_review", "chưa ai điền"
        elif sts <= {"confirmed_1", "confirmed_2"}:
            ex_st, why = "fully_confirmed", "bốn trụ đọc trực tiếp và đã có người xác nhận"
        else:
            ex_st, why = "incomplete", ", ".join(f"{p}: {x['status']}" for p, x in pills.items() if x["status"] not in ("confirmed_1", "confirmed_2"))
        res[k] = {"pillars": pills, "status": ex_st, "reason": why}
    counts = {}
    for r in res.values():
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    return {"examples": res, "counts": counts, "problems": problems}


def main(argv):
    r = check(argv[1:] or [ROOT / "docs/bazi_deep_examples_review_sheet.csv"])
    print("counts:", r["counts"])
    for p in r["problems"]:
        print("PROBLEM:", p)
    for k, v in r["examples"].items():
        if v["status"] not in ("no_review", "fully_confirmed"):
            print(k, v["status"], v["reason"])
    return 1 if r["problems"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
