"""Beginner-experience layer: glossary data integrity, lesson links, and the 'Dễ hiểu' content filter (run in node, no DOM)."""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tvbt.api import app

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
sys.path.insert(0, str(ROOT.parent / "tools"))
import build_glossary  # noqa: E402

B = {"year": 1990, "month": 5, "day": 17, "hour": 10, "minute": 30, "gender": "male"}
c = TestClient(app)
G = json.loads((WEB / "js" / "glossary.json").read_text("utf-8"))


def test_glossary_json_is_not_stale():
    assert G == build_glossary.build(), "run: python tools/build_glossary.py"


def test_glossary_covers_every_star_palace_and_ten_god_in_a_real_chart():
    t = c.post("/api/chart", json=B).json()["tuvi"]
    for p in t["palaces"]:
        assert f"palace:{p['name']}" in G["terms"], p["name"]
        for s in p["major_stars"]:
            assert f"star:{s}" in G["terms"] and G["terms"][f"star:{s}"]["facts"], s  # star_profiles merged in
    assert len(G["gods"]) == 10 and all(f"god:{g}" in G["terms"] for g in G["gods"])
    assert {f"can:{n}" for n in "Giáp Ất Bính Đinh Mậu Kỷ Canh Tân Nhâm Quý".split()} <= set(G["terms"])
    assert len([k for k in G["terms"] if k.startswith("chi:")]) == 12
    assert {f"dg:{k}" for k in ("miếu", "vượng", "đắc", "bình", "hãm")} <= set(G["terms"])


def test_every_star_in_a_real_chart_has_its_own_explanation_not_the_generic_fallback():
    t = c.post("/api/chart", json=B).json()["tuvi"]
    missing = [s["name"] for s in t["stars"] if f"star:{s['name']}" not in G["terms"]]
    assert not missing, missing


def test_tu_hoa_table_matches_engine_for_canh_year():
    t = c.post("/api/chart", json=B).json()["tuvi"]  # 1990 = Canh
    row = dict(G["terms"]["x:tu-hoa-table"]["table"])["Canh"]
    assert row == [t["tu_hoa"][k]["star"] for k in ("Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ")]


def test_every_glossary_lesson_link_exists_in_learn_js():
    lessons = set(re.findall(r"^  '([a-z0-9-]+)': \{ title:", (WEB / "js" / "learn.js").read_text("utf-8"), re.M))
    assert {"gioi-thieu", "tv-1", "tv-2", "tv-3", "tv-4", "tv-5", "tv-6", "tv-7", "bt-1", "bt-2", "bt-3", "bt-4"} <= lessons
    assert {t["lesson"] for t in G["terms"].values()} <= lessons


def test_no_internal_ids_in_public_web_code():
    js = "".join((WEB / "js" / n).read_text("utf-8") for n in ("tuvi.js", "beginner.js", "app.js", "glossary.js"))
    assert "schoolId" not in js and "vn_dlhc" not in js
    for html in ("index.html",):
        assert "vn_dlhc" not in (WEB / html).read_text("utf-8")


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_easy_mode_filter_hides_drafts_and_folds_hard_traits():
    reason = c.post("/api/reasoning", json=B).json()
    findings = [f for s in reason["systems"].values() for f in s["findings"]]
    script = f"""
      import {{ classify, parsePhrase, easyCard }} from '{(WEB / "js" / "beginner.js").as_uri()}';
      import {{ CLAIMS }} from '{(WEB / "js" / "util.js").as_uri()}';
      let d = ''; for await (const x of process.stdin) d += x;
      const {{ findings, claims }} = JSON.parse(d); Object.assign(CLAIMS, claims);
      const c = classify(findings);
      console.log(JSON.stringify({{ show: c.show.map(f => [f.basis, parsePhrase(f).core]), care: c.care.map(f => [f.basis, parsePhrase(f).core]), draft: c.draft.length, card: c.show[0] ? easyCard(c.show[0]) : '' }}));
    """
    out = subprocess.run(["node", "--input-type=module", "-e", script], input=json.dumps({"findings": findings, "claims": c.get("/api/claims").json()}),
                         capture_output=True, text=True, check=True).stdout
    r = json.loads(out)
    assert r["show"] and all(b == "verified" for b, _ in r["show"] + r["care"])  # drafts never appear as headline or folded readings
    assert r["draft"] == sum(1 for f in findings if f["basis"] != "verified") > 0
    text = " ".join(t for _, t in r["show"]).lower()
    for hard in ("khó đạt", "nghèo", "thất bại", "tranh cãi", "ganh ghét", "kiêu căng"):
        assert hard not in text, hard  # hard/one-sided traits are folded, not headlined
    assert any("tranh cãi" in t or "ganh" in t for _, t in r["care"])
    assert "Theo sách đã đối chiếu" in r["card"] and "SRC_" not in r["card"] and "TV_" not in r["card"]  # no rule ids in easy cards


def test_year_endpoint_has_fields_for_this_year_card():
    from fastapi.testclient import TestClient
    from tvbt.api import app
    r = TestClient(app).post("/api/year", json=dict(year=1990, month=5, day=17, hour=10, minute=30, gender="male", to_year=2026)).json()
    b, t = r["bazi"], r["tuvi"]
    assert b["annual_pillar"] and b["annual_stem_ten_god"] and b["luck_pillar"] and "annual_vs_natal" in b
    assert t["tieu_han_palace"] and t["luu_thai_tue_palace"] and t["luu_tu_hoa_reading"]
