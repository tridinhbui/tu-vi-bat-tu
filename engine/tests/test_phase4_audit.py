"""Phase 4: the source audit of the 10 cách cục, the lưu tinh audit, and the wording of every experimental sentence."""
import json
import re
import warnings
from pathlib import Path

from phase1_helpers import synth
from tvbt import tuvi
from tvbt.calendar_core import BirthInput, normalize
from tvbt.knowledge.loader import load_all, load_experimental, load_experimental_layers, load_experimental_phi_hoa
from tvbt.reasoning import temporal_facts as T
from tvbt.reasoning.formation_eval import STATE_VI, evaluate_formation, render_vi

warnings.filterwarnings("ignore")
DATA = Path(__file__).resolve().parent.parent / "data"
AUDIT = json.loads((DATA / "experimental" / "formation_source_audit.json").read_text("utf-8"))
XR, FORMS, _ = load_experimental()
LR, _ = load_experimental_layers()
PR, _ = load_experimental_phi_hoa()
PROD, _ = load_all()
PROD_BY_ID = {r.id: r for r in PROD}

# ---- 1-2. formation source audit -----------------------------------------------------------------------------------------
def test_audit_covers_every_element_of_every_formation_and_nothing_is_verified():
    assert set(AUDIT["formations"]) == {f.id for f in FORMS} and len(FORMS) == 10
    for f in FORMS:
        rows = AUDIT["formations"][f.id]["elements"]
        want = {"core:core"} | {f"{r}:{e.id}" for r in ("boosters", "breakers", "rescuers", "refutations") for e in getattr(f, r)}
        assert {f"{r['role']}:{r['id']}" for r in rows} == want, f.id
        assert f.reviewStatus == "draft" and AUDIT["formations"][f.id]["reviewStatus"] == "draft"
        assert all(r["verdict"] == "draft" for r in rows)


def test_no_element_reaches_tier_t0_and_registry_is_never_called_independent():
    assert "T0" not in {r["effective_tier"] for F in AUDIT["formations"].values() for r in F["elements"]}
    for F in AUDIT["formations"].values():
        for r in F["elements"]:
            for s in r["sources"]:
                assert s["independent"] is False
                if s["kind"] == "registry":
                    assert s["nguyen_van"].startswith("không có trong repo") and s["page"] and s["tier"] in ("T1", "T2")
                else:
                    assert s["tier"] == "T3" and s["zh"] and s["vi_literal"] and "chưa đối chiếu bản in" in s["retrieved_via"]


def test_tier_follows_support_rules():
    for F in AUDIT["formations"].values():
        for r in F["elements"]:
            sup = [s for s in r["sources"] if s["supports"]]
            assert (r["effective_tier"] == "T4") == (not sup)
            if sup:
                assert r["effective_tier"] == min(s["tier"] for s in sup)
            assert all(s["correspondence"] == "khop" for s in sup)                      # only an exact correspondence supports


def test_audit_is_not_stale_against_the_pack_rules_it_cites():
    for F in AUDIT["formations"].values():
        for r in F["elements"]:
            for s in r["sources"]:
                if s["kind"] == "registry":
                    rule = PROD_BY_ID[s["rule"]]
                    assert rule.reviewStatus == s["review"], (s["rule"], "review status changed: regenerate the audit")
                    assert s['page'] in rule.description, (s['rule'], s['page'], 'page no longer matches the rule: regenerate the audit')


def test_counts_and_known_source_conflicts_are_recorded():
    total = {t: sum(F["summary"].get(t, 0) for F in AUDIT["formations"].values()) for t in ("T1", "T2", "T3", "T4")}
    assert sum(total.values()) == 93 and total["T4"] > 60 and total["T1"] >= 8                      # most conditions are still hypotheses
    ids = {c["id"] for c in AUDIT["conflicts"]}
    assert {"X_MDDK_NGO", "X_TTAN_HOA", "X_TRIET_GIAI"} <= ids
    mddk = next(r for r in AUDIT["formations"]["CACH_X_MA_DAU_DOI_KIEM"]["elements"] if r["role"] == "core")
    assert any(s.get("correspondence") == "khac" for s in mddk["sources"])                         # the classical gloss disagrees with the Ngọ core
    ttan = next(r for r in AUDIT["formations"]["CACH_X_THACH_TRUNG_AN_NGOC"]["elements"] if r["id"] == "tam_hoa_hoi_du")
    assert any(s.get("correspondence") == "khac" for s in ttan["sources"])


def test_classical_lines_are_flagged_single_web_copy():
    assert AUDIT["classical_url"].startswith("https://zh.wikisource.org/")
    assert len(AUDIT["classical"]) >= 10 and all(v["zh"] and v["vi"] for v in AUDIT["classical"].values())


# ---- 6. lưu tinh ---------------------------------------------------------------------------------------------------------------
def test_luu_tinh_equal_the_natal_stars_of_a_chart_born_in_that_year():
    """The only thing the convention claims: flowing stars of year Y sit where the natal stars of a person born in year Y sit."""
    base = tuvi.compute(normalize(BirthInput(1990, 5, 17, 10, 30, "Asia/Ho_Chi_Minh", "male")))
    for year in (1984, 1991, 2000, 2024, 2037):
        born = tuvi.compute(normalize(BirthInput(year, 6, 15, 10, 0, "Asia/Ho_Chi_Minh", "male")))      # mid-year: same lunar year number
        natal = {s.name: BRANCHES[s.branch] if isinstance(s.branch, int) else s.branch for s in born.stars}
        L = T.luu_tinh(base, year)
        by_branch = {p["name"]: p["branch"] for p in base.palaces}
        want = {"Lưu Lộc Tồn": "Lộc Tồn", "Lưu Kình Dương": "Kình Dương", "Lưu Đà La": "Đà La", "Lưu Thiên Khôi": "Thiên Khôi",
                "Lưu Thiên Việt": "Thiên Việt", "Lưu Thiên Mã": "Thiên Mã"}
        for k, natal_name in want.items():
            assert by_branch[L[k]] == natal[natal_name], (year, k)


BRANCHES = "Tý Sửu Dần Mão Thìn Tỵ Ngọ Mùi Thân Dậu Tuất Hợi".split()


def test_luu_tinh_audit_record_says_experimental_and_names_the_missing_source():
    a = json.loads((DATA / "experimental" / "luu_tinh_audit.json").read_text("utf-8"))
    assert a["status"] == "experimental" and a["flow_rule_source"] is None and a["registry_rules_found"] == 0
    assert set(a["stars"]) == {"Lưu Lộc Tồn", "Lưu Kình Dương", "Lưu Đà La", "Lưu Thiên Khôi", "Lưu Thiên Việt", "Lưu Thiên Mã"}
    for s in a["stars"].values():
        assert s["natal_formula_review"] == "verified" and s["annual_flow_review"] == "none" and s["label"] == "experimental"
    # nothing in production registry describes a flowing star
    assert not [r.id for r in PROD if re.search(r"\bLưu (Lộc|Kình|Đà|Khôi|Việt|Thiên Mã)", r.description)]


# ---- 7. wording ---------------------------------------------------------------------------------------------------------------
CERTAIN = re.compile(r"chắc chắn|chắn chắn|nhất định|tất yếu|tất nhiên|đảm bảo|định mệnh|sẽ xảy ra|\bsẽ\b|\bắt\b|\bắt sẽ\b|tuyệt đối|không thể tránh|phải xảy ra|chắc hẳn|chắc là", re.I)


def test_no_certain_language_in_any_experimental_sentence():
    texts = [r.description for r in XR + LR + PR]
    texts += [f.name_vi for f in FORMS] + [e.label for f in FORMS for k in ("boosters", "breakers", "rescuers", "refutations") for e in getattr(f, k)]
    texts += list(STATE_VI.values())
    for t in texts:
        assert not CERTAIN.search(t), t
    for r in XR + LR + PR:
        assert r.description.startswith("[thử nghiệm"), r.id                                           # every experimental rule is labelled in its own text
        assert not CERTAIN.search(" ".join(c.get("claim", "") for c in r.consequences))


def test_rendered_formation_text_is_hedged_for_every_state():
    seen = set()
    for f in FORMS:
        for ops_state in range(3):
            facts = {"palace.name": "Mệnh"}
            d = evaluate_formation(f, facts)             # facts are missing -> chua_du_du_kien: still must render hedged text
            t = render_vi(f, d)
            assert not CERTAIN.search(t), t
            seen.add(d["state"])
    # real charts: every state label sentence carries the experimental disclaimer
    from phase1_helpers import base_facts
    for f in FORMS:
        d = evaluate_formation(f, base_facts([], "Tý")["palace:Mệnh"])
        t = render_vi(f, d)
        assert d["state"] == "khong_hien" or ("thử nghiệm" in t and "không dự báo" in t)
    assert "chua_du_du_kien" in seen


def test_api_warnings_are_hedged_and_label_the_mode():
    from fastapi.testclient import TestClient
    from tvbt.api import app
    c = TestClient(app)
    B = dict(year=1990, month=5, day=17, hour=10, minute=30, gender="male")
    ws = [c.post("/api/phi-hoa", json=B).json()["warning"], c.post("/api/reasoning", json={**B, "experimental": True}).json()["experimental"]["warning"],
          c.post("/api/year", json={**B, "to_year": 2024, "experimental": True}).json()["experimental"]["warning"]]
    for w in ws:
        assert "thử nghiệm" in w.lower() and ("không dự báo" in w or "chưa đối chiếu" in w.lower()) and not CERTAIN.search(w), w
