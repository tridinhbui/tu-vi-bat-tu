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


def test_compare_charts_gives_facts_not_scores():
    a = B
    b = {"year": 1985, "month": 11, "day": 3, "hour": 8, "minute": 0, "gender": "female"}
    r = c.post("/api/compare-charts", json={"a": a, "b": b}).json()
    assert r["a"]["day_master"] == "Nhâm" and r["a"]["day_branch"] == "Ngọ"
    assert r["ten_god_of_b_for_a"] and r["ten_god_of_a_for_b"] and r["day_branches"] and r["element_link"]["text"]
    assert not any(k in r for k in ("score", "match", "verdict"))


def test_compare_known_relations():
    from tvbt.compare import compare
    from tvbt.api import _compute, BirthReq
    mk = lambda **k: _compute(BirthReq(**{**B, **k}))[1]
    same = compare(mk(), mk())
    assert same["day_master_stems"]["kind"] == "trùng" and same["day_branches"][0]["kind"] == "chi_trùng"
    assert same["ten_god_of_b_for_a"] == "Tỉ Kiên"


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_post_retries_5xx_but_not_4xx():
    script = f"""
      import {{ post }} from '{(WEB / "js" / "util.js").as_uri()}';
      const seq = (codes) => {{ let i = 0; globalThis.calls = 0; globalThis.fetch = async () => {{ calls++; const c = codes[Math.min(i++, codes.length - 1)]; return {{ ok: c < 400, status: c, json: async () => c < 400 ? {{ ok: 1 }} : {{ detail: c === 422 ? 'bad date' : undefined }} }}; }}; }};
      const out = {{}};
      seq([500, 500, 200]); out.recovered = [await post('/x', {{}}), calls];
      seq([422]); try {{ await post('/x', {{}}); }} catch (e) {{ out.client = [e.message, calls]; }}
      seq([500]); try {{ await post('/x', {{}}, {{ retries: 1 }}); }} catch (e) {{ out.giveup = [e.message, calls]; }}
      console.log(JSON.stringify(out));
    """
    r = json.loads(subprocess.run(["node", "--input-type=module", "-e", script], capture_output=True, text=True, check=True).stdout)
    assert r["recovered"] == [{"ok": 1}, 3]
    assert r["client"] == ["bad date", 1]  # a real validation error is shown at once, not retried
    assert r["giveup"][1] == 2 and "chưa phản hồi" in r["giveup"][0]


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_guide_scripts_use_only_chart_facts_and_verified_readings():
    chart = c.post("/api/chart", json=B).json()
    reason = c.post("/api/reasoning", json=B).json()
    script = f"""
      import {{ dialogueBazi, dialogueTuvi, parseMarkup, GUIDES }} from '{(WEB / "js" / "mascots.js").as_uri()}';
      import {{ CLAIMS }} from '{(WEB / "js" / "util.js").as_uri()}';
      let d = ''; for await (const x of process.stdin) d += x;
      const {{ chart, reason, claims, terms }} = JSON.parse(d); Object.assign(CLAIMS, claims);
      const ctx = {{ req: {json.dumps(B)}, reason }};
      console.log(JSON.stringify({{ bt: dialogueBazi(chart, ctx, terms), tv: dialogueTuvi(chart, ctx, terms), md: parseMarkup('a **b** c').map(x => [x.t, x.b]), guides: Object.keys(GUIDES) }}));
    """
    out = subprocess.run(["node", "--input-type=module", "-e", script], capture_output=True, text=True, check=True,
                         input=json.dumps({"chart": chart, "reason": reason, "claims": c.get("/api/claims").json(), "terms": G["terms"]})).stdout
    r = json.loads(out)
    assert r["md"] == [["a ", False], ["b", True], [" c", False]] and sorted(r["guides"]) == ["bat", "tu1", "tu2", "vi"]
    for key, pair, n in (("bt", {"bat", "tu2"}, 7), ("tv", {"tu1", "vi"}, 8)):
        turns = r[key]
        assert len(turns) == n and {t["who"] for t in turns} == pair  # each side is spoken by exactly its own two guides
        assert all(a["who"] != b["who"] for a, b in zip(turns, turns[1:]))  # the two guides take turns
        text = " ".join(t["t"] for t in turns)
        assert "Không phải dự báo" in text and not re.search(r"TV_|BT_|SRC_|nháp|chưa xác minh|undefined|NaN", text)
