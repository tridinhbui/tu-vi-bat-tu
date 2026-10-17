"""Provenance, reachability and 'no score summing' checks for the 10 DRAFT formations.

Everything stays draft: nothing here may mark a formation verified. The provenance file records, per condition, how the draft
relates to page-cited rules already in the packs; these tests make sure each cited rule really exists, has the stated review
status and page, and that every condition of every formation is accounted for."""
import glob
import json
from pathlib import Path

from fastapi.testclient import TestClient

from tvbt.api import app
from tvbt.formation_explain import analyse
from tvbt.knowledge.formation import from_dict
from tvbt.knowledge.loader import load_experimental
from tvbt.reasoning.formation_eval import evaluate_formation

ROOT = Path(__file__).resolve().parent.parent
PROV = json.loads((ROOT / "data" / "experimental" / "formation_provenance.json").read_text("utf-8"))
REACH = json.loads((Path(__file__).parent / "fixtures" / "formation_reach.json").read_text("utf-8"))
_, XF, _ = load_experimental()
RULES = {r["id"]: r for p in glob.glob(str(ROOT / "data" / "pack_*.json")) for r in json.load(open(p, encoding="utf-8"))["rules"]}
STATUSES = {"khop", "long_hon", "chat_hon", "khac", "lien_quan", "khong_co_nguon"}
KINDS = ("boosters", "breakers", "rescuers", "refutations")
client = TestClient(app)


def components(fid):
    comp = PROV["formations"][fid]
    yield "core", None, comp["core"]
    for k in KINDS:
        for eid, e in comp[k].items():
            yield k, eid, e


def test_every_condition_of_every_formation_has_a_provenance_entry_and_vice_versa():
    assert {f.id for f in XF} == set(PROV["formations"])
    for f in XF:
        for k in KINDS:
            assert {e.id for e in getattr(f, k)} == set(PROV["formations"][f.id][k]), f"{f.id}.{k}"


def test_statuses_are_in_the_vocabulary_and_khop_always_cites_a_rule():
    for f in XF:
        for kind, eid, c in components(f.id):
            assert c["status"] in STATUSES and c["note"] is not None
            if c["status"] != "khong_co_nguon":
                assert c["sources"], f"{f.id}.{kind}.{eid}: '{c['status']}' needs at least one cited rule"
            if c["status"] == "khop" and not any(s["review"] == "verified" for s in c["sources"]):
                assert "nháp" in c["note"], f"{f.id}.{kind}.{eid}: matches a source that is itself only a draft, so say so"


def test_every_cited_rule_exists_with_the_stated_review_status_and_page():
    n = 0
    for f in XF:
        for kind, eid, c in components(f.id):
            for s in c["sources"]:
                r = RULES[s["rule"]]
                n += 1
                assert r["reviewStatus"] == s["review"], f"{s['rule']} review status drifted"
                assert s["page"] and s["page"].split(None, 1)[1].rstrip(",") in r["description"], f"{s['rule']} page not in rule text"
                assert s["source"] in r["sourceIds"]
    assert n >= 60


def test_nothing_is_verified_and_everything_stays_experimental():
    assert all(f.reviewStatus != "verified" and f.experimental for f in XF)
    out = client.post("/api/formations", json=dict(year=1990, month=5, day=17, hour=10, minute=30, gender="male")).json()
    assert out["status"] == "draft" and "chưa đối chiếu sách" in out["warning"]
    assert all(f["experimental"] and f["review"] == "draft" for f in out["formations"])
    assert "experimental" not in client.post("/api/reasoning", json=dict(year=1990, month=5, day=17, hour=10, minute=30, gender="male")).json()


def test_api_attaches_a_source_to_every_condition_and_a_summary_per_formation():
    out = client.post("/api/formations", json=dict(year=2008, month=3, day=2, hour=12, minute=0, gender="male")).json()
    for f in out["formations"]:
        assert f["core"]["source"] and f["source_summary"]["total"] == 1 + sum(len(PROV["formations"][f["id"]][k]) for k in KINDS)
        assert all(e["source"] for e in f["evidence"])
        assert "chưa có nguồn" in f["source_summary"]["text"] or f["source_summary"]["khong_co_nguon"] == 0


# ---------------------------------------------------------------- reachability (exhaustive scan, 525,960 charts)
def test_scan_covers_a_full_sexagenary_cycle_of_every_day_hour_and_gender():
    assert REACH["charts_per_formation"] == 21915 * 12 * 2 == 525960


def test_the_only_unreachable_cell_is_explained_as_a_definition_property():
    assert REACH["unreachable"] == ["CACH_X_TU_PHU_DONG_CUNG|pha_duoc_cuu"]
    assert [x["cell"] for x in PROV["known_impossible"]] == REACH["unreachable"]
    assert all(x["kind"] == "theo_dinh_nghia" and "không phải lỗi engine" in x["reason"] for x in PROV["known_impossible"])
    ev = REACH["evidence_active_when_core_true"]
    f = "CACH_X_TU_PHU_DONG_CUNG"
    assert ev.get(f"{f}|rescuers|tam_hoa_hoi_cuu", 0) == 0, "Tam Hóa never gathers in the tam phương of Dần/Thân together with Tử Phủ"
    assert ev[f"{f}|breakers|ky_dong_cung"] > 0 and ev[f"{f}|rescuers|khoa_dong_cung"] > 0, "both halves exist separately, they just never coincide"


def test_ma_dau_doi_kiem_thanh_thuong_is_now_reachable_after_the_v2_definition():
    c = REACH["counts"]
    assert c["CACH_X_MA_DAU_DOI_KIEM|thanh_thuong"] == 598
    # v1 had a tautological refutation (Kình Dương hãm, always true when Kình sits at Ngọ); v2 dropped it
    assert not any(e.id == "Kình_Dương_ham" for f in XF if f.id == "CACH_X_MA_DAU_DOI_KIEM" for e in f.refutations)


def test_khoi_viet_giap_menh_pha_duoc_cuu_is_reachable():
    assert REACH["counts"]["CACH_X_KHOI_VIET_GIAP_MENH|pha_duoc_cuu"] == 448


def test_every_reachable_cell_has_a_witness_that_reproduces():
    from tvbt import tuvi
    from tvbt.calendar_core import BirthInput, normalize
    assert len(REACH["witness"]) == 59
    for cell, b in REACH["witness"].items():
        fid, state = cell.split("|")
        tv = tuvi.compute(normalize(BirthInput(b["year"], b["month"], b["day"], b["hour"], b["minute"], "Asia/Ho_Chi_Minh", b["gender"])))
        got = next(x["state"] for x in analyse(tv, XF) if x["id"] == fid)
        assert got == state, (cell, b, got)


def test_dead_and_always_conditions_are_all_explained_in_the_provenance():
    ev = REACH["evidence_active_when_core_true"]
    dead = set()
    for f in XF:
        core_n = ev.get(f"{f.id}|core", 0)
        for k in KINDS:
            for e in getattr(f, k):
                n = ev.get(f"{f.id}|{k}|{e.id}", 0)
                r = PROV["formations"][f.id][k][e.id].get("reach", {})
                assert r["active"] == n and r["never"] == (n == 0) and r["always"] == (n == core_n)
                if n == 0 or n == core_n:
                    assert r.get("reason"), f"{f.id}.{k}.{e.id} is dead/always but unexplained"
                    dead.add(f"{f.id.removeprefix('CACH_X_')}.{e.id}")
    assert dead == {"TU_PHU_VU_TUONG.Thiên_Tướng_ham", "TU_PHU_DONG_CUNG.tam_hoa_hoi_cuu", "NHAT_LE_TRUNG_THIEN.Thái_Dương_ham", "THACH_TRUNG_AN_NGOC.Cự_Môn_ham"}


# ---------------------------------------------------------------- the ladder never sums scores
def F(boosters=0, breakers=0, rescuers=(), refutations=0, thuong_at=2):
    t = lambda v: {"fact": "x", "operator": "eq", "value": v}
    ev = lambda p, n, w: [{"id": f"{p}{i}", "label": f"{p}{i}", "when": t(w)} for i in range(n)]
    return from_dict({"id": "T", "name_vi": "Thử", "anchor": "Mệnh", "core": t(1), "thuong_at": thuong_at,
                      "boosters": ev("b", max(boosters, 1), 1 if boosters else 0), "breakers": ev("k", breakers, 1),
                      "rescuers": [{"id": "r", "label": "r", "when": t(1), "rescues": list(rescuers)}] if rescuers else [],
                      "refutations": ev("f", refutations, 1)})


def st(f):
    return evaluate_formation(f, {"x": 1}, None)["state"]


def test_more_boosters_do_not_raise_beyond_thanh_thuong():
    assert st(F(boosters=2)) == st(F(boosters=6)) == "thanh_thuong"


def test_refutations_lower_exactly_one_rung_however_many_there_are():
    assert st(F(boosters=3, refutations=1)) == st(F(boosters=3, refutations=4)) == "thanh"
    assert st(F(boosters=1, refutations=1)) == st(F(boosters=1, refutations=3)) == "hinh_thuc"


def test_boosters_never_offset_an_uncovered_breaker():
    assert st(F(boosters=6, breakers=1)) == "bi_pha"
    assert st(F(boosters=6, breakers=2, rescuers=["k0"])) == "bi_pha"        # one of two breakers still uncovered
    assert st(F(boosters=0, breakers=2, rescuers=["k0", "k1"])) == "pha_duoc_cuu"


def test_refutations_do_not_change_a_broken_or_rescued_verdict():
    assert st(F(boosters=2, breakers=1, refutations=3)) == "bi_pha"
    assert st(F(boosters=2, breakers=1, rescuers=["k0"], refutations=3)) == "pha_duoc_cuu"


def test_a_rescued_breaker_is_not_a_good_chart():
    assert st(F(boosters=6, breakers=1, rescuers=["k0"])) == "pha_duoc_cuu"     # still labelled as having been broken
