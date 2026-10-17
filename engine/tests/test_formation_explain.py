"""Every (formation, state) cell must be explained in plain Vietnamese: which stars, which palaces, which relation, which condition.
Fixtures are real charts found by tools/scan_formation_samples.py; the verdicts are pinned as regression guards."""
import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tvbt.api import app
from tvbt.formation_explain import analyse
from tvbt.knowledge import dsl
from tvbt.knowledge.formation import Formation, from_dict
from tvbt.reasoning.formation_eval import evaluate_formation

FX = json.loads((Path(__file__).parent / "fixtures" / "formation_charts.json").read_text("utf-8"))
client = TestClient(app)
STATES = {"khong_hien", "hinh_thuc", "thanh", "thanh_thuong", "bi_pha", "pha_duoc_cuu"}
CODEISH = re.compile(r"[A-Za-zÀ-ỹ]+_[A-Za-zÀ-ỹ_]+")          # an internal id such as sat_dong_cung or Thiên_Tướng_ham
CHAIN = ["Dữ kiện", "Quan hệ", "Cách cục"]


def formations(birth):
    r = client.post("/api/formations", json=birth)
    assert r.status_code == 200
    return {f["id"]: f for f in r.json()["formations"]}


def visible_strings(f):
    out = [f["text"], f["state_vi"], f["core"]["because"], *f["missing"], *f["caveats"]]
    for e in f["evidence"]:
        out += [e["label"], e["because"], e["kind_vi"], *e.get("rescues", [])]
    for s in f["chain"]:
        out += [s["step"], s["text"]]
    return out


@pytest.mark.parametrize("cell", FX["cells"], ids=lambda c: f"{c['formation'][8:]}-{c['state']}-{c['birth']['year']}{c['birth']['month']:02d}{c['birth']['day']:02d}h{c['birth']['hour']}{c['birth']['gender'][0]}")
def test_pinned_cell_is_stable_and_fully_explained(cell):
    f = formations(cell["birth"])[cell["formation"]]
    assert f["state"] == cell["state"] and f["state"] in STATES
    for s in visible_strings(f):
        assert not CODEISH.search(s), f"internal code leaked into visible text: {s!r}"
    assert f["experimental"] is True and f["review"] == "draft"
    assert [s["step"] for s in f["chain"]][:3] == CHAIN
    if f["state"] == "khong_hien":
        assert f["chain"][-1]["step"] == "Tổng luận" and "không xét tiếp" in f["chain"][-1]["text"]
        return
    # the structure is visible: stars, palaces and relations are named
    assert f["core"]["active"] and f["core"]["items"], "core must name the stars/palaces that form the structure"
    assert all(i["palace"] and (i.get("star") or i.get("note") is not None) for i in f["core"]["items"])
    assert any(i.get("role") for i in f["core"]["items"]) or f["anchor"] in f["core"]["because"]
    assert f["name_vi"] in f["text"] and f["anchor"] in f["text"]
    active = [e for e in f["evidence"] if e["active"]]
    for e in active:
        assert e["because"], f"active condition {e['label']!r} must say which stars/palaces satisfied it"
        assert e["items"] and all(i["palace"] for i in e["items"])
    by = lambda k: [e for e in active if e["kind"] == k]
    last = f["chain"][-1]
    assert last["step"] == "Tổng luận" and last["text"].startswith(f["state_vi"])
    if f["state"] == "bi_pha":
        assert by("breakers") and f["uncovered"], "bị phá must name the breaker that nothing rescues"
        assert "chưa được cứu" in last["text"]
    if f["state"] == "pha_duoc_cuu":
        assert by("breakers") and by("rescuers") and not f["uncovered"]
        assert all(r["rescues"] for r in by("rescuers")), "a rescuer must say which breaker it rescues"
    if f["state"] in ("thanh", "thanh_thuong"):
        assert by("boosters") and not by("breakers")
    if f["state"] == "hinh_thuc":
        assert not by("breakers")
        assert f["downgraded"] or (not by("boosters") and f["missing"]), "hình thức is either lowered by a refutation or says what is missing"


def test_many_refutations_are_listed_and_lower_one_rung():
    cases = FX["special"]["many_refutations"]
    assert cases, "fixture needs charts with several refutations"
    for c in cases:
        f = formations(c["birth"])[c["formation"]]
        refs = [e for e in f["evidence"] if e["kind"] == "refutations" and e["active"]]
        assert len(refs) >= 2 and all(e["because"] for e in refs)
        step = next(s for s in f["chain"] if s["step"] == "Phản chứng")
        assert all(e["label"] in step["text"] for e in refs)
        assert f["state"] in STATES


def test_downgrade_by_refutation_is_explained():
    for c in FX["special"]["downgraded"]:
        f = formations(c["birth"])[c["formation"]]
        assert f["downgraded"] and f["state"] in ("thanh", "hinh_thuc")
        assert "hạ" in f["chain"][-1]["text"] and "hạ một bậc" in f["text"]


def test_multiple_uncovered_breakers_all_named():
    for c in FX["special"]["many_uncovered"]:
        f = formations(c["birth"])[c["formation"]]
        assert f["state"] == "bi_pha" and len(f["uncovered"]) >= 2
        assert sum(1 for e in f["evidence"] if e["kind"] == "breakers" and e["active"]) >= 2


def test_unknown_core_is_reported_as_insufficient_data_not_false():
    f = from_dict({"id": "X", "name_vi": "Thử", "anchor": "Mệnh", "core": {"fact": "palace.no_such_fact", "operator": "eq", "value": 1},
                   "boosters": [{"id": "b", "label": "b", "when": {"fact": "palace.tuan", "operator": "eq", "value": True}}]})
    d = evaluate_formation(f, {"palace.tuan": True}, None)
    assert d["state"] == "chua_du_du_kien" and d["core"] is None and any("thiếu dữ kiện" in c for c in d["caveats"])


def test_unknown_refutation_is_a_caveat_not_a_silent_false():
    f = from_dict({"id": "Y", "name_vi": "Thử", "anchor": "Mệnh", "core": {"fact": "palace.tuan", "operator": "eq", "value": True},
                   "boosters": [{"id": "b", "label": "b", "when": {"fact": "palace.tuan", "operator": "eq", "value": True}}],
                   "refutations": [{"id": "r", "label": "r", "when": {"fact": "palace.tp_rank.Thất Sát", "operator": "lte", "value": 0}}]})
    d = evaluate_formation(f, {"palace.tuan": True}, None)
    assert d["state"] == "thanh" and d["unknown"] and any("chưa đủ dữ kiện" in c for c in d["caveats"])


def test_all_ten_formations_reach_every_reachable_state_in_the_scan():
    cov = FX["coverage"]
    ids = {k.split("|")[0] for k in cov}
    assert len(ids) == 10
    gaps = sorted(f"{i[8:]}:{s}" for i in ids for s in STATES if f"{i}|{s}" not in cov)
    # recorded gap list (observed in the 25,000-chart scan); a NEW gap means the engine or the scan changed
    assert gaps == FX.get("known_gaps", gaps), gaps


def test_endpoint_is_additive_and_the_production_reading_is_unchanged():
    b = dict(year=1990, month=5, day=17, hour=10, minute=30, gender="male")
    plain = client.post("/api/reasoning", json=b).json()
    again = client.post("/api/reasoning", json={**b, "experimental": False}).json()
    assert plain == again and "experimental" not in plain
    client.post("/api/formations", json=b)
    assert client.post("/api/reasoning", json=b).json() == plain
