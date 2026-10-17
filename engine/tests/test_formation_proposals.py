"""Phase 6: the 25 audit proposals, one regression each (data/experimental/formation_proposals.json built by tools/build_formation_proposals.py)."""
import collections
import json
from pathlib import Path

import pytest

from tvbt import calendar_core as cc, lunar_input, tuvi
from tvbt.formation_explain import _Chart
from tvbt.knowledge import dsl

ROOT = Path(__file__).resolve().parents[2]
DOC = json.loads((ROOT / "engine/data/experimental/formation_proposals.json").read_text("utf-8"))
PROPS = DOC["proposals"]
VAR = {f["id"]: f for f in json.loads((ROOT / "engine/data/experimental/formations_school_variants.json").read_text("utf-8"))["formations"]}
BASE = {f["id"]: f for f in json.loads((ROOT / "engine/data/experimental/formations_experimental.json").read_text("utf-8"))["formations"]}
AUDIT = json.loads((ROOT / "engine/data/experimental/formation_audit.json").read_text("utf-8"))["rows"]


def test_exactly_the_25_audit_proposals_are_listed_once():
    keys = [(p["formation"], p["role"], p["condition"]) for p in PROPS]
    assert len(keys) == len(set(keys)) == 25
    assert set(keys) == {(r["formation"], r["role"], r["id"]) for r in AUDIT if r["action"] == "de_xuat_sua"}
    assert collections.Counter(p["relation"] for p in PROPS) == {"chua": 6, "bo": 10, "mo_rong": 4, "thu_hep": 2, "thay_the": 2, "giu": 1}
    for p in PROPS:
        assert p["cites"] and p["new_reading"] and p["regression_test"]
        if p["relation"] in ("chua", "bo"):
            assert p["not_implemented_reason"]


def _ids(f, role):
    return {c["id"] for c in f[role]}


def test_unimplemented_and_dropped_stay_out_of_variants():
    for p in PROPS:
        variants = [v for vid, v in VAR.items() if vid.split("@")[0] == p["formation"]]
        if p["relation"] == "chua":
            # not implemented: no variant of the formation carries a widened/rewritten version of this condition
            for v in variants:
                if p["role"] != "core":                         # P04 (anchor Mệnh/Thân) has no per-condition id: only the anchor limitation applies
                    assert p["condition"] not in _ids(v, p["role"]), (p["id"], v["id"])
            assert p["variants"] == []
        if p["relation"] == "bo":
            for vid in p["variants"]:
                assert p["condition"] not in _ids(VAR[vid], p["role"]), (p["id"], vid)
    # the rescuer is gone from EVERY variant
    assert all(not v["rescuers"] for v in VAR.values())
    # specific 'gặp' proposals were not widened: TPVT / SPLT / NLTT / KVGM-Kỵ breakers do not exist in any variant
    for f, ids in (("TU_PHU_VU_TUONG", {"sat_dong_cung", "ky_dong_cung"}), ("SAT_PHA_LIEM_THAM", {"ky_dong_cung"}), ("NHAT_LE_TRUNG_THIEN", {"ky_dong_cung"}), ("KHOI_VIET_GIAP_MENH", {"ky_dong_cung"})):
        for vid, v in VAR.items():
            if vid.startswith("CACH_X_" + f):
                assert not (_ids(v, "breakers") & ids), vid


def _sample(n=360):
    k = 0
    for ly in range(2014, 2024):
        for lm in (2, 5, 8, 11):
            for ld in (4, 18):
                for hb in range(0, 12, 2):
                    for g in ("male", "female"):
                        try:
                            sol = lunar_input.lunar_to_solar(ld, lm, ly, False, "vn")[0]
                        except Exception:
                            continue
                        yield tuvi.compute(cc.normalize(cc.BirthInput(sol.year, sol.month, sol.day, 2 * hb, 0, "Asia/Ho_Chi_Minh", g)))
                        k += 1
                        if k >= n:
                            return


def _when(f, role, cid):
    return f["core"] if role == "core" else next(c["when"] for c in f[role] if c["id"] == cid)


@pytest.mark.parametrize("p", [p for p in PROPS if p["before_after"]], ids=lambda p: p["id"])
def test_relation_holds_on_the_sample(p):
    """live check on a fresh sample + the stored 11,520-chart figures: the declared relation between the original and the replacement."""
    b = p["before_after"]
    rel = p["relation"]
    stored = {"mo_rong": b["base_only"] == 0 and b["var_only"] > 0, "thu_hep": b["var_only"] == 0 and b["base_only"] > 0,
              "giu": b["base_only"] == b["var_only"] == 0, "thay_the": b["base_only"] > 0 and b["var_only"] > 0}[rel]
    assert stored, (p["id"], b)
    bf, vf = BASE[p["formation"]], VAR[p["variants"][0]]
    bw, vw = _when(bf, p["role"], p["condition"]), _when(vf, p["role"], p["variant_condition"])
    seen = {"base_only": 0, "var_only": 0, "core": 0}
    for tv in _sample():
        ch = _Chart(tv)
        facts = ch.facts_of("palace:Mệnh")
        if dsl.evaluate(bf["core"], facts, ch.world) is not True:
            continue
        a, c = dsl.evaluate(bw, facts, ch.world), dsl.evaluate(vw, facts, ch.world)
        if a is None or c is None:
            continue
        seen["core"] += 1
        seen["base_only"] += a and not c
        seen["var_only"] += c and not a
    if rel == "mo_rong":
        assert seen["base_only"] == 0
    if rel == "thu_hep":
        assert seen["var_only"] == 0
    if rel == "giu":
        assert seen["base_only"] == seen["var_only"] == 0
