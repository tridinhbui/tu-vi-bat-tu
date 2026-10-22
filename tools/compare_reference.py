"""Compare the engine's natal chart with hand-transcribed reference charts (engine/tests/reference_charts/*.json), palace by palace.
    .venv/bin/python tools/compare_reference.py [file ...]
Each fixture gives, per branch: palace name, stem, đại hạn start age, Tràng Sinh stage, Tuần/Triệt, Thân, chính tinh with the board's
dignity letter (compared under the fixture's dignity_school), and the other natal stars. Differences are printed and returned; a fixture
is independent evidence only for what it shows (randomized invariant tests are not reference validation).

Tứ Hóa ("hoa" in a fixture): "natal" (+ "natal_branch") = the board's own Hóa Lộc/Quyền/Khoa/Kỵ, compared with the engine's chart.tu_hoa;
"luu" (one entry or a list, each with "year", the stars and a "branch" map) = the board's L.Hóa for its năm xem, compared with the
engine's lưu Tứ Hóa for that year (the same table applied to the year stem). Boards print only the palace of a Hóa, so the fixture names
the star only where one star in that palace is what some Tứ Hóa table (data/experimental/tu_hoa_tables.json) gives. A school difference
(e.g. the board's Canh row = 紫微斗數全書, not Khảo Luận) is declared in known_gaps; hoa_info() says which tables the board matches."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
from tvbt.api import BirthReq, _compute  # noqa: E402
from tvbt.ganzhi import STEMS_VI, from_cycle, year_cycle_index  # noqa: E402
from tvbt import tuvi as _tuvi  # noqa: E402

LETTER = {"miếu": "M", "vượng": "V", "đắc": "Đ", "bình": "B", "hãm": "H", "lợi": "L"}
TS = {"Trường Sinh", "Mộc Dục", "Quan Đới", "Lâm Quan", "Đế Vượng", "Suy", "Bệnh", "Tử", "Mộ", "Tuyệt", "Thai", "Dưỡng"}
HOA = ("Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ")
DEFAULT_DIR = ROOT / "engine" / "tests" / "reference_charts"
_TABLES_JSON = json.loads((ROOT / "engine" / "data" / "experimental" / "tu_hoa_tables.json").read_text("utf-8"))
HOA_TABLES = {src: {stem: tuple(row[k] for k in HOA) for stem, row in tab.items()} for src, tab in _TABLES_JSON["tables"].items()}


def _chart(ref: dict):
    return _compute(BirthReq(**ref["birth"], dignity_school=ref.get("dignity_school", "thuc_hanh")))[2]


def _luu_entries(ref: dict) -> list[dict]:
    luu = (ref.get("hoa") or {}).get("luu")
    return [] if not luu else (luu if isinstance(luu, list) else [luu])


def _year_stem(year: int) -> int:
    return from_cycle(year_cycle_index(year))[0]


def _engine_row(tv, stem: int) -> tuple:
    """The engine's Tứ Hóa row for a stem under the table this chart was built with."""
    if hasattr(_tuvi, "hoa_of"):
        return tuple(_tuvi.hoa_of(tv, stem))
    return tuple(_tuvi.TU_HOA[stem])


def _star_branch(tv, star: str):
    return next((p["branch"] for p in tv.palaces if star in p["stars"] or star in p["major_stars"]), None)


def _hoa_diffs(ref: dict, tv) -> list[str]:
    h = ref.get("hoa") or {}
    diffs = []
    br_name = {p["branch_index"]: p["branch"] for p in tv.palaces}
    for k, want in (h.get("natal") or {}).items():
        got = tv.tu_hoa[k]
        got_br = br_name.get(got["branch"]) if isinstance(got["branch"], int) else got["branch"]
        want_br = (h.get("natal_branch") or {}).get(k, got_br)
        if (got["star"], got_br) != (want, want_br):
            diffs.append(f"natal {k}: {got['star']}@{got_br} != {want}@{want_br}")
    for e in _luu_entries(ref):
        row = dict(zip(HOA, _engine_row(tv, _year_stem(e["year"]))))
        for k in HOA:
            if k not in e and k not in (e.get("branch") or {}):
                continue
            got_br = _star_branch(tv, row[k])
            want_br = (e.get("branch") or {}).get(k, got_br)
            want = e.get(k, row[k])
            if (row[k], got_br) != (want, want_br):
                diffs.append(f"lưu Hóa {e['year']} {k}: {row[k]}@{got_br} != {e.get(k, '?')}@{want_br}")
    return diffs


def hoa_info(path: Path) -> list[str]:
    """Which Tứ Hóa tables reproduce the board's natal / lưu Hóa (information, never a failure)."""
    ref = json.loads(path.read_text())
    h = ref.get("hoa") or {}
    out = []
    rows = []
    if h.get("natal"):
        rows.append(("natal", ref["year_gz"].split()[0], h["natal"]))
    rows += [(f"lưu {e['year']}", STEMS_VI[_year_stem(e["year"])], {k: e[k] for k in HOA if k in e}) for e in _luu_entries(ref)]
    for label, stem, stars in rows:
        ok = [src for src, tab in HOA_TABLES.items() if all(dict(zip(HOA, tab[stem]))[k] == v for k, v in stars.items())]
        out.append(f"{label} ({stem}, {len(stars)}/4 sao xác định): bảng khớp {', '.join(ok) or 'không bảng nào'}")
    return out


def compare(path: Path) -> list[str]:
    ref = json.loads(path.read_text())
    al = ref.get("aliases", {})
    tv = _chart(ref)
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
    return diffs + _hoa_diffs(ref, tv)


if __name__ == "__main__":
    files = [Path(a) for a in sys.argv[1:]] or sorted(DEFAULT_DIR.glob("*.json"))
    bad = 0
    for f in files:
        d = compare(f)
        gaps = set(json.loads(f.read_text()).get("known_gaps", []))
        new = [x for x in d if x not in gaps]
        bad += bool(new)
        print(f"{f.name}: {'OK' if not new else str(len(new)) + ' khác biệt'}" + (f" ({len(d) - len(new)} đã khai báo trong known_gaps)" if len(d) > len(new) else ""))
        for x in d:
            print("  -" if x in new else "  ~", x)
        for x in hoa_info(f):
            print("  i", x)
        for x in sorted(gaps - set(d)):
            print("  ! known_gap không còn xuất hiện:", x)
    sys.exit(1 if bad else 0)
