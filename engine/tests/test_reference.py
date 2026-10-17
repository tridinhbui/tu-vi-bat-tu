"""/reference data: generated from the packs (must be fresh), consistent with the engine, and the page/route exist."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import build_reference  # noqa: E402

REF = json.loads((ROOT / "engine" / "web" / "js" / "reference.json").read_text("utf-8"))


def test_reference_json_is_fresh():
    assert REF == json.loads(json.dumps(build_reference.build(), ensure_ascii=False)), "run: python tools/build_reference.py"


def test_every_tu_vi_rule_with_a_star_condition_is_reachable_from_some_star_card():
    ids = {s["id"] for c in list(REF["tu_vi"]["stars"].values()) + list(REF["tu_vi"]["minor"].values())
           for lst in c["palaces"].values() for it in lst for s in it["src"]}
    assert len(ids) > 1000
    assert sum(REF["tier_counts"].values()) >= len(ids)


def test_dignity_tables_match_engine_and_diff_is_exact():
    from tvbt import dignity
    from tvbt.ganzhi import BRANCHES_VI
    diff = dignity.compare(list(BRANCHES_VI))
    assert REF["audit_stats"]["dignity"]["diff"] == len(diff)
    for d in diff:
        row = REF["tu_vi"]["stars"][d["star"]]["dignity"]
        assert row["thuc_hanh"][d["branch"]] == d["thuc_hanh"] and row["toan_thu"][d["branch"]] == d["toan_thu"]


def test_limit_findings_use_the_limit_phrasing_the_ui_shows():
    """KL p.55: Tử Phủ with Tuần/Triệt is a LIMIT; the reference must say 'giảm/kém', never the neutral 'hưởng nhiều phúc lộc'."""
    items = [it for lst in REF["tu_vi"]["stars"]["Thiên Phủ"]["palaces"].values() for it in lst
             if any(s["id"] == "TV_KL_PHU_TU_PHU_TUAN_TRIET" for s in it["src"])]
    assert items and "hưởng nhiều phúc lộc" not in items[0]["t"]


def test_corrected_rules_do_not_appear_as_sourced():
    mo = [it for lst in REF["tu_vi"]["minor"].values() for pal in lst["palaces"].values() for it in pal
          if any(s["id"] == "TV_TH_AUX2_TAI_BACH_MO" for s in it["src"])]
    for it in mo:
        assert it["tier"] in ("draft", "hypothesis")


def test_editorial_tokens_resolved_and_honest():
    txt = json.dumps(REF["editorial"], ensure_ascii=False)
    assert "{{" not in txt
    assert "Giả thuyết" in REF["tiers"]["hypothesis"] or "giả thuyết" in REF["tiers"]["hypothesis"].lower()
    assert any("không" in p and "dự báo" in p for sec in REF["editorial"]["sections"] for p in sec["paras"])
    st = REF["audit_stats"]["ev"]
    assert st["random_n"] >= 100 and st["random_ci_lo"] <= st["random_faithful_pct"] <= st["random_ci_hi"]


def test_route_and_page_exist():
    from fastapi.testclient import TestClient
    from tvbt.api import app
    c = TestClient(app)
    assert c.get("/reference").status_code == 200
    j = c.get("/api/evidence").json()
    assert len(j["entries"]) >= 200 and "web" in j
    assert c.get("/js/reference.json").status_code == 200
