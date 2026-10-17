"""Phase 6: the independent oracle (tests/oracle_tuvi_independent.py, no `tvbt` import) against production.
Layers: (1) the oracle reproduces the book's own printed charts; (2) oracle == production on positions, Tứ Hóa, Tuần/Triệt and every variant state
on a sample; (3) mutation tests prove the comparison can fail; (4) the pinned full scan (116,928 charts) shows zero disagreement."""
import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oracle_tuvi_independent as O  # noqa: E402
from tvbt import calendar_core as cc, lunar_input, tuvi  # noqa: E402
from tvbt.formation_explain import analyse  # noqa: E402
from tvbt.knowledge.formation import load_formations  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
VARS = load_formations(ROOT / "engine/data/experimental/formations_school_variants.json")
SPEC = O.V()
PALACE_ORDER = ["Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch", "Quan Lộc", "Nô Bộc", "Thiên Di", "Tật Ách", "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ"]


def production(ly, lm, ld, hb, male):
    sol = lunar_input.lunar_to_solar(ld, lm, ly, False, "vn")[0]
    return tuvi.compute(cc.normalize(cc.BirthInput(sol.year, sol.month, sol.day, 2 * hb, 0, "Asia/Ho_Chi_Minh", "male" if male else "female")))


def sample():
    for ly in (2014, 2017, 2020):
        for lm in (2, 6, 11):
            for ld in (3, 14, 27):
                for hb in range(12):
                    for male in (True, False):
                        try:
                            lunar_input.lunar_to_solar(ld, lm, ly, False, "vn")
                        except Exception:
                            continue
                        yield ly, lm, ld, hb, male


def test_oracle_reproduces_the_books_printed_example_charts():
    """KL pp.237-246 data (CHARTS) is read as plain data; the oracle never sees production's star placement."""
    from test_book_examples import CHARTS
    for name, c in CHARTS.items():
        o = O.chart(c["year"], c["month"], c["day"], c["hb"], c["gender"] == "male")
        menh = o["menh"]
        for i, pal in enumerate(PALACE_ORDER):
            b = (menh + i) % 12
            if pal in c["majors"]:
                assert O.majors_at(o, {b}) == c["majors"][pal], (name, pal)
        for pal, want in c["minors"].items():
            b = (menh + PALACE_ORDER.index(pal)) % 12
            assert want <= O.stars_at(o, {b}), (name, pal, want)
        assert {k: v for k, v in o["carriers"].items()} == c["hoa"], name
        assert o["cuc"] == {"Thủy nhị cục": 2, "Mộc tam cục": 3, "Kim tứ cục": 4, "Thổ ngũ cục": 5, "Hỏa lục cục": 6}[c["cuc"]], name


def test_oracle_equals_production_on_positions_hoa_tuan_triet_and_variant_states():
    n = 0
    seen = set()
    for key in sample():
        tv = production(*key)
        o = O.chart(*key)
        assert (tv.menh_branch, tv.than_branch, tv.cuc["n"]) == (o["menh"], o["than"], o["cuc"]), key
        prod = {s.name: s.branch for s in tv.stars}
        for s, p in o["pos"].items():
            assert prod[s] == p, (key, s)
        for tag, v in tv.tu_hoa.items():
            assert v["branch"] == o["pos"][o["carriers"][tag]], (key, tag)
        assert {p["branch_index"] for p in tv.palaces if p["tuan"]} == o["tuan"], key
        assert {p["branch_index"] for p in tv.palaces if p["triet"]} == o["triet"], key
        for x in analyse(tv, VARS):
            assert O.state(SPEC[x["id"]], o) == x["state"], (key, x["id"])
            seen.add((x["id"], x["state"]))
        n += 1
    assert n >= 600
    assert len({s for _, s in seen}) >= 4                      # the sample exercises several states, not only 'khong_hien'


def wide():
    for ly in range(2014, 2024):
        for lm in range(1, 13):
            for ld in (4, 11, 18, 25):
                for hb in range(12):
                    for male in (True, False):
                        try:
                            lunar_input.lunar_to_solar(ld, lm, ly, False, "vn")
                        except Exception:
                            continue
                        yield ly, lm, ld, hb, male


def _mutated(vid, old, new):
    out = []
    for f in VARS:
        if f.id == vid:
            f = copy.deepcopy(f)
            blob = json.dumps({"c": f.core, "e": [(k, e.id, e.when) for k in ("boosters", "breakers", "refutations") for e in getattr(f, k)]}, ensure_ascii=False)
            assert old in blob, (vid, old)
            for k in ("boosters", "breakers", "refutations"):
                for e in getattr(f, k):
                    e.when = json.loads(json.dumps(e.when, ensure_ascii=False).replace(old, new))
            f.core = json.loads(json.dumps(f.core, ensure_ascii=False).replace(old, new))
        out.append(f)
    return out


@pytest.mark.parametrize("vid,old,new", [
    ("CACH_X_CO_NGUYET_DONG_LUONG@tt_24", "palace.rel.tp_stars", "palace.rel.self_stars"),          # breaker scope narrowed back to đồng cung
    ("CACH_X_TAM_KY_GIA_HOI@kl_66", "palace.rel.opp_hoa", "palace.rel.flank_prev_hoa"),             # đối cung -> wrong palace
    ("CACH_X_TU_PHU_VU_TUONG@kl_132_193", "palace.tuan", "palace.opp_tuan"),                       # Tuần on the wrong palace
    ("CACH_X_KHOI_VIET_GIAP_MENH@kl_44_62", "palace.khi.sat_tp", "palace.khi.sat_flank"),           # hội chiếu -> giáp
])
def test_mutated_production_is_caught_by_the_oracle(vid, old, new):
    mutated = _mutated(vid, old, new)
    diffs = examined = 0
    for key in wide():
        o = O.chart(*key)
        if SPEC[vid]["core"](o) is not True:                  # only charts where the formation exists can show a difference
            continue
        tv = production(*key)
        examined += 1
        for x in analyse(tv, mutated):
            if x["id"] == vid and O.state(SPEC[vid], o) != x["state"]:
                diffs += 1
        if examined >= 400 or diffs >= 3:
            break
    assert diffs > 0, f"the oracle comparison is vacuous for this condition ({examined} charts examined)"


def test_oracle_uses_no_production_code():
    src = (Path(__file__).resolve().parent / "oracle_tuvi_independent.py").read_text("utf-8")
    assert "import tvbt" not in src and "from tvbt" not in src and "from . " not in src


def test_nham_khoa_school_difference_is_the_only_tu_hoa_ambiguity_and_is_recorded():
    """TH p.21 prints Nhâm-Khoa = Thiên Phủ, KL p.197 prints Tả Phụ; production and the oracle follow KL. Under the TH reading the Khoa carrier moves in Nhâm years."""
    assert O.TU_HOA[8][2] == "Tả Phụ" == O.NHAM_KHOA
    th_alt = dict(O.TU_HOA)
    th_alt[8] = (*O.TU_HOA[8][:2], "Thiên Phủ", O.TU_HOA[8][3])
    moved = sum(1 for lm in range(1, 13) for hb in range(12)
                if (c := O.chart(2012, lm, 10, hb, True))["pos"]["Tả Phụ"] != c["pos"]["Thiên Phủ"])
    assert moved > 0                                                   # the two readings really place Khoa differently
    assert th_alt[8][2] != O.TU_HOA[8][2]


def test_pinned_full_scan_oracle_vs_production_has_no_disagreement():
    full = json.loads((ROOT / "engine/tests/fixtures/formation_oracle_full.json").read_text("utf-8"))
    assert full["charts"] == 116928
    assert full["mismatches"] == {}, full["first_examples"]
