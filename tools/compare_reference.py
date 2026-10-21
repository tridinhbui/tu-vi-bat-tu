"""Compare the engine's natal chart with hand-transcribed reference charts (engine/tests/reference_charts/*.json), palace by palace.
    .venv/bin/python tools/compare_reference.py [file ...]
Each fixture gives, per branch: palace name, stem, đại hạn start age, Tràng Sinh stage, Tuần/Triệt, Thân, chính tinh with the board's
dignity letter (compared under the fixture's dignity_school), and the other natal stars. Differences are printed and returned; a fixture
is independent evidence only for what it shows (randomized invariant tests are not reference validation)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
from tvbt.api import BirthReq, _compute  # noqa: E402

LETTER = {"miếu": "M", "vượng": "V", "đắc": "Đ", "bình": "B", "hãm": "H", "lợi": "L"}
TS = {"Trường Sinh", "Mộc Dục", "Quan Đới", "Lâm Quan", "Đế Vượng", "Suy", "Bệnh", "Tử", "Mộ", "Tuyệt", "Thai", "Dưỡng"}
DEFAULT_DIR = ROOT / "engine" / "tests" / "reference_charts"


def compare(path: Path) -> list[str]:
    ref = json.loads(path.read_text())
    al = ref.get("aliases", {})
    _, _, tv = _compute(BirthReq(**ref["birth"], dignity_school=ref.get("dignity_school", "thuc_hanh")))
    by = {p["branch"]: p for p in tv.palaces}
    dh = {d["branch"]: d["age_from"] for d in tv.dai_han}
    diffs = []
    if ref.get("year_gz") and ref["year_gz"] != tv.year_gz:
        diffs.append(f"year {tv.year_gz} != {ref['year_gz']}")
    for k in ("day", "month", "year"):
        if ref.get("lunar") and ref["lunar"][k] != tv.lunar[k]:
            diffs.append(f"lunar {k} {tv.lunar[k]} != {ref['lunar'][k]}")
    if ref.get("cuc") and ref["cuc"] != tv.cuc["name"]:
        diffs.append(f"cục {tv.cuc['name']} != {ref['cuc']}")
    for br, r in ref["palaces"].items():
        p = by[br]
        tag = f"{br} {r['name']}"
        for f, got, want in [("name", p["name"], r["name"]), ("stem", p["stem"], r.get("stem", p["stem"])), ("đại hạn", dh.get(br), r.get("dai_han", dh.get(br))),
                             ("tuần", bool(p["tuan"]), bool(r.get("tuan"))), ("triệt", bool(p["triet"]), bool(r.get("triet"))), ("thân", bool(p["is_than"]), bool(r.get("than")))]:
            if got != want:
                diffs.append(f"{tag}: {f} {got} != {want}")
        stage = next((s for s in p["stars"] if s in TS), None)
        if r.get("stage") and stage != r["stage"]:
            diffs.append(f"{tag}: Tràng Sinh {stage} != {r['stage']}")
        if set(p["major_stars"]) != set(r["majors"]):
            diffs.append(f"{tag}: chính tinh {sorted(p['major_stars'])} != {sorted(r['majors'])}")
        for s, letter in r["majors"].items():
            got = LETTER.get(p["major_dignity"].get(s) or "", "")
            if letter and got != letter:
                diffs.append(f"{tag}: {s} dignity {got or '—'} != {letter} ({ref.get('dignity_school', 'thuc_hanh')})")
        want = {al.get(s, s) for s in r["stars"]}
        have = {s for s in p["stars"] if s not in p["major_stars"] and s not in TS}
        for s in sorted(want - have):
            where = next((q["branch"] for q in tv.palaces if s in q["stars"]), "không an")
            diffs.append(f"{tag}: thiếu {s} (engine: {where})")
        for s in sorted(have - want):
            diffs.append(f"{tag}: thừa {s}")
    return diffs


if __name__ == "__main__":
    files = [Path(a) for a in sys.argv[1:]] or sorted(DEFAULT_DIR.glob("*.json"))
    bad = 0
    for f in files:
        d = compare(f)
        bad += bool(d)
        print(f"{f.name}: {'OK' if not d else str(len(d)) + ' khác biệt'}")
        for x in d:
            print("  -", x)
    sys.exit(1 if bad else 0)
