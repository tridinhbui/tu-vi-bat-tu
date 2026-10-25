"""Phase 4: school/experimental isolation from the engine to the API to the UI source.
Nothing from the Phi Hóa school, the experimental cách cục, the layer rules or the lưu tinh may appear in the default (verified-only) outputs,
and no endpoint other than the opt-in blocks may carry them."""
import json
import re
import warnings
from pathlib import Path

from fastapi.testclient import TestClient

from tvbt.api import app
from tvbt.knowledge.loader import load_all, load_experimental, load_experimental_layers, load_experimental_phi_hoa

warnings.filterwarnings("ignore")
WEB = Path(__file__).resolve().parent.parent / "web"
B = dict(year=1990, month=5, day=17, hour=10, minute=30, gender="male")
B2 = dict(year=1975, month=11, day=3, hour=23, minute=5, gender="female")
# strings that exist ONLY in experimental material
LEAK = [r"phi\.", r"derived\.phi", r"phi_tinh", r"experimental_draft", r"\bph_[a-z_]+", r"\bly_[a-z_]+", r"\bLY_[A-Z_]+", r"\bPH_[A-Z_]+", r"\bXR_[A-Z_]+",
        r"CACH_X_", r"cach:CACH", r"SRC_EXPERIMENTAL", r"Lưu Lộc Tồn", r"Lưu Kình Dương", r"Lưu Đà La", r"Lưu Thiên (Khôi|Việt|Mã)", r"luu_tinh", r"time\.luu"]


def leaks(obj):
    s = json.dumps(obj, ensure_ascii=False)
    return sorted({m.group(0) for pat in LEAK for m in re.finditer(pat, s)})


def default_responses():
    c = TestClient(app)
    out = {
        "chart": c.post("/api/chart", json=B), "analysis": c.post("/api/analysis", json=B), "reasoning": c.post("/api/reasoning", json=B),
        "reasoning_toan_thu": c.post("/api/reasoning", json={**B, "dignity_school": "toan_thu"}),
        "year": c.post("/api/year", json={**B, "to_year": 2024}), "year2": c.post("/api/year", json={**B2, "to_year": 2031}),
        "bazi_structure": c.post("/api/bazi-structure", json=B), "bazi_timeline": c.post("/api/bazi-timeline", json=B),
        "twelve": c.post("/api/twelve-gods", json=B), "hour_sweep": c.post("/api/hour-sweep", json={**B, "hour": 0}),
        "compare": c.post("/api/compare-charts", json={"a": B, "b": B2}), "compare_hours": c.post("/api/compare-hours", json={"a": B, "b": {**B, "hour": 12}}),
        "rules": c.get("/api/rules"), "claims": c.get("/api/claims"), "dignity": c.get("/api/dignity"), "dignity_cmp": c.get("/api/dignity/compare"),
    }
    return {k: r for k, r in out.items()}


def test_default_outputs_of_every_endpoint_contain_no_experimental_material():
    for name, r in default_responses().items():
        assert r.status_code == 200, (name, r.status_code, r.text[:200])
        assert leaks(r.json()) == [], (name, leaks(r.json()))


def test_verified_overall_reading_has_no_experimental_text():
    c = TestClient(app)
    j = c.post("/api/reasoning", json=B).json()
    text = json.dumps(j["systems"], ensure_ascii=False)
    assert "thử nghiệm" not in text.lower() and "chưa đối chiếu sách" not in text
    a = json.dumps(c.post("/api/analysis", json=B).json(), ensure_ascii=False)
    assert "thử nghiệm" not in a.lower()


def test_experimental_flag_only_adds_a_separate_block_and_leaves_the_rest_byte_identical():
    c = TestClient(app)
    for path, body, keep in [("/api/reasoning", B, ("systems", "pack_problems", "dignity_school")), ("/api/year", {**B, "to_year": 2024}, ("bazi", "tuvi"))]:
        plain = c.post(path, json=body).json()
        flagged = c.post(path, json={**body, "experimental": True}).json()
        assert set(flagged) - set(plain) == {"experimental"}
        assert {k: flagged[k] for k in keep} == {k: plain[k] for k in keep}, path
        assert leaks({k: v for k, v in flagged.items() if k != "experimental"}) == []
        assert flagged["experimental"]["status"] == "draft"


def test_each_experimental_block_carries_only_its_own_school():
    c = TestClient(app)
    r = c.post("/api/reasoning", json={**B, "experimental": True}).json()["experimental"]
    assert all(f["claim"].startswith(("cach:CACH_X_", "xr_")) for f in r["findings"]) and "phi" not in json.dumps(r, ensure_ascii=False).lower().replace("phi_", "")
    y = c.post("/api/year", json={**B, "to_year": 2024, "experimental": True}).json()["experimental"]
    assert all(f["claim"].startswith("ly_") for f in y["findings"]) and not re.search(r"phi\.|ph_|PH_", json.dumps(y, ensure_ascii=False))
    p = c.post("/api/phi-hoa", json=B).json()
    assert all(f["claim"].startswith("ph_") for f in p["interpretation"]["findings"])
    assert not re.search(r"Lưu |ly_|CACH_X_|cach:", json.dumps(p, ensure_ascii=False))


def test_compare_charts_experimental_stays_labelled_and_free_of_phi_and_luu():
    c = TestClient(app)
    j = c.post("/api/compare-charts", json={"a": {**B, "experimental": True}, "b": {**B2, "experimental": True}}).json()
    assert not re.search(r"phi\.|PH_|ph_|Lưu Lộc|Lưu Kình|luu_tinh", json.dumps(j, ensure_ascii=False))


def test_engine_level_no_experimental_rule_or_school_in_production_registry():
    prod, sources = load_all()
    xr, xf, xs = load_experimental()
    lr, ls = load_experimental_layers()
    pr, ps = load_experimental_phi_hoa()
    prod_ids = {r.id for r in prod}
    assert not prod_ids & ({r.id for r in xr} | {f.id for f in xf} | {r.id for r in lr} | {r.id for r in pr})
    assert all(r.schoolId not in ("experimental_draft", "phi_tinh_draft") for r in prod)
    assert not {s.id for s in sources} & {s.id for s in xs + ls + ps}
    for r in xr + lr + pr:
        assert r.reviewStatus == "draft"
    assert all(f.reviewStatus == "draft" and f.experimental for f in xf)
    ids = {r["id"] for r in TestClient(app).get("/api/rules").json()["rules"]} if "rules" in TestClient(app).get("/api/rules").json() else set()
    assert not ids & ({r.id for r in lr} | {r.id for r in pr} | {f.id for f in xf})


def test_ui_source_gates_experimental_endpoints_and_never_calls_phi_hoa():
    js = "\n".join(p.read_text("utf-8") for p in sorted((WEB / "js").glob("*.js")))
    html = (WEB / "index.html").read_text("utf-8")
    assert "/api/phi-hoa" not in js and "/api/phi-hoa" not in html          # the Phi Hóa endpoint has no UI at all
    for line in js.splitlines():
        if "/api/formations" in line:
            assert "expOn()" in line, line.strip()[:160]                      # only fetched in ?thu-nghiem mode
    # the generic request flag is only ever set from the experimental toggle
    for line in js.splitlines():
        if re.search(r"experimental\s*:", line):
            assert "exp" in line.split("experimental")[1][:12], line.strip()[:160]
    assert not re.search(r"Phi Hóa|Phi Tinh|phi_hoa|Lưu Lộc Tồn", js + html)
    # the year panel posts the plain request: no experimental flag
    for m in re.finditer(r"post\('/api/year'[^\n]*", js):
        assert "experimental" not in m.group(0)


def test_leak_detector_has_teeth():
    assert leaks({"a": "xem phi.tu_hoa"}) and leaks({"a": "ly_ky_chong_tang"}) and leaks({"a": "Lưu Lộc Tồn ở Mệnh"}) and leaks({"a": "CACH_X_TU_PHU"})
    assert leaks({"a": "Tử Vi, Thiên Phủ, Lưu Hà"}) == []                  # the natal star 'Lưu Hà' is not a lưu tinh


DEFAULT_ROUTES = {"/api/chart", "/api/analysis", "/api/bazi-structure", "/api/bazi-timeline", "/api/year", "/api/twelve-gods", "/api/reasoning",
                  "/api/compare-charts", "/api/lunar-to-solar", "/api/hour-sweep", "/api/compare-hours", "/api/rules", "/api/claims",
                  "/api/dignity/compare", "/api/dignity", "/api/hoang-dao"}
OPT_IN_ROUTES = {"/api/formations", "/api/phi-hoa"}                   # draft material; never called by default UI flows (Phi Hóa: not at all)
USER_SUPPLIED = {"/api/rules/test"}                                   # evaluates a rule the CALLER sends; not a source of readings
# Routes that reached main after this guard was written (merged 2026-10-21) and are covered by their own tests;
# listed so that any route added from here on still has to be classified above.
LATER_ROUTES = {"/api/calendar", "/api/deep-reading", "/api/dignity/classify", "/api/facts", "/api/growth/compass", "/api/growth/dialogue",
                "/api/growth/journal-review", "/api/growth/navigate", "/api/growth/profile", "/api/interpretation", "/api/synthesis",
                # Kinh Dịch / Mai Hoa (2026-10-25): their own system, no Tử Vi material; covered by tests/test_kinh_dich_*.py and test_mai_hoa_text.py
                "/api/kinh-dich/cast", "/api/kinh-dich/reading", "/api/kinh-dich/text/{n}", "/api/mai-hoa/cast", "/api/mai-hoa/reading"}


def test_route_inventory_forces_review_of_every_new_endpoint():
    routes = {r.path for r in app.routes if getattr(r, "methods", None) and r.path.startswith("/api")}
    assert routes == DEFAULT_ROUTES | OPT_IN_ROUTES | USER_SUPPLIED | LATER_ROUTES, (
        "a new /api route appeared: decide whether it is default (add a leak test) or opt-in experimental", sorted(routes ^ (DEFAULT_ROUTES | OPT_IN_ROUTES | USER_SUPPLIED | LATER_ROUTES)))


def test_lunar_to_solar_and_remaining_default_routes_are_clean():
    c = TestClient(app)
    r = c.post("/api/lunar-to-solar", json=dict(year=1990, month=4, day=23))
    assert r.status_code == 200 and leaks(r.json()) == []
    r = c.get("/api/hoang-dao", params=dict(y=1990, m=5, d=17, h=10, mi=30))     # cung hoàng đạo: computed facts only
    assert r.status_code == 200 and leaks(r.json()) == []


def test_opt_in_routes_are_not_part_of_the_default_flow_of_the_tested_endpoints():
    exercised = {"/api/chart", "/api/analysis", "/api/bazi-structure", "/api/bazi-timeline", "/api/year", "/api/twelve-gods", "/api/reasoning", "/api/compare-charts",
                 "/api/hour-sweep", "/api/compare-hours", "/api/rules", "/api/claims", "/api/dignity", "/api/dignity/compare", "/api/lunar-to-solar", "/api/hoang-dao"}
    assert exercised == DEFAULT_ROUTES and not exercised & OPT_IN_ROUTES
