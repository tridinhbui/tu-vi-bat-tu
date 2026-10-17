"""Phase 6 integration: variants are opt-in data. The baseline, the default API and the main reading are unaffected by their existence."""
import json
from pathlib import Path

from fastapi.testclient import TestClient

from tvbt.api import app
from tvbt.formation_explain import analyse
from tvbt.knowledge.formation import load_formations
from tvbt.knowledge.loader import load_experimental

ROOT = Path(__file__).resolve().parents[2]
client = TestClient(app)
BIRTH = {"year": 1990, "month": 5, "day": 17, "hour": 10, "minute": 0, "gender": "male", "timezone": "Asia/Ho_Chi_Minh", "calendar": "vn"}


def _birth_ok():
    r = client.post("/api/formations", json=BIRTH)
    assert r.status_code == 200, r.text
    return r.json()


def test_default_formations_endpoint_returns_only_the_ten_baseline_formations():
    d = _birth_ok()
    ids = [f["id"] for f in d["formations"]]
    base = [f.id for f in load_experimental()[1]]
    assert ids == base and len(ids) == 10 and not any("@" in i for i in ids)
    assert all(f["review"] == "draft" and f["experimental"] for f in d["formations"])


def test_loader_and_analyse_never_pick_variants_unless_handed_to_them():
    fs = load_experimental()[1]
    assert len(fs) == 10 and all("@" not in f.id for f in fs)
    variants = load_formations(ROOT / "engine/data/experimental/formations_school_variants.json")
    assert len(variants) == 17
    # explicit selection: handing the variants to the same analysis function evaluates them, nothing else
    r = client.post("/api/formations", json=BIRTH)
    from tvbt import calendar_core as cc, tuvi
    tv = tuvi.compute(cc.normalize(cc.BirthInput(1990, 5, 17, 10, 0, "Asia/Ho_Chi_Minh", "male")))
    assert {x["id"] for x in analyse(tv, variants)} <= {f.id for f in variants}
    assert {x["id"] for x in analyse(tv, fs)} <= {f.id for f in fs}
    assert [f["id"] for f in r.json()["formations"]] == [f.id for f in fs]


def test_baseline_definition_file_keeps_its_shape():
    doc = json.loads((ROOT / "engine/data/experimental/formations_experimental.json").read_text("utf-8"))
    assert list(doc) == ["formations"] and len(doc["formations"]) == 10
    assert all(f["definition_version"] == 2 and f["reviewStatus"] == "draft" and f["experimental"] for f in doc["formations"])
    assert not any("@" in f["id"] for f in doc["formations"])


def test_main_reading_and_ui_do_not_reference_variants():
    for p in list((ROOT / "engine/web").rglob("*.js")) + list((ROOT / "engine/web").rglob("*.html")):
        assert "school_variants" not in p.read_text("utf-8"), p
    for p in (ROOT / "engine/tvbt").rglob("*.py"):
        assert "formations_school_variants" not in p.read_text("utf-8"), p
    # default reading endpoints carry no experimental formation id
    for path in ("/api/chart", "/api/reasoning"):
        r = client.post(path, json=BIRTH)
        if r.status_code == 200:
            assert "CACH_X_" not in r.text and "@kl_" not in r.text and "@tt_" not in r.text and "@th_" not in r.text, path
