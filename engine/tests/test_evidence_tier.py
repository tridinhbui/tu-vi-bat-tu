"""Result cards: the 5-tier label computed in the browser (web/js/tier.js) must equal the tier on the /reference page
(tools/build_reference.tier, stored in web/js/reference.json) for every rule that fires, and the evidence behind it must be
the machine-checked entry served by /api/evidence."""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "engine" / "web" / "js"
sys.path.insert(0, str(ROOT / "tools"))
import build_reference  # noqa: E402

REF = json.loads((WEB / "reference.json").read_text("utf-8"))
needs_node = pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")

CHARTS = [dict(year=1990, month=5, day=17, hour=10, minute=30, gender="male"),
          dict(year=1984, month=11, day=2, hour=23, minute=10, gender="female"),
          dict(year=1975, month=3, day=29, hour=5, minute=0, gender="male"),
          dict(year=2001, month=8, day=8, hour=14, minute=45, gender="female"),
          dict(year=1968, month=1, day=30, hour=0, minute=20, gender="male"),
          dict(year=1996, month=12, day=21, hour=19, minute=5, gender="female")]


def ref_tiers():
    out = {}

    def walk(o):
        if isinstance(o, dict):
            if "id" in o and "tier" in o:
                out[o["id"]] = o["tier"]
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(REF)
    return out


def run_node(payload):
    js = (WEB / "tier.js").read_text("utf-8")
    code = js + """
const input = JSON.parse(require('fs').readFileSync(0, 'utf8'));
setEvidence(input.entries);
process.stdout.write(JSON.stringify(input.findings.map(f => tierOf(f, evidenceFor(f)))));
"""
    # tier.js is an ES module; strip `export` so the same text runs as a CommonJS script
    code = re.sub(r"^export ", "", code, flags=re.M)
    r = subprocess.run(["node", "-e", code], input=json.dumps(payload), capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def test_no_book_set_matches_build_reference():
    js = (WEB / "tier.js").read_text("utf-8")
    ids = set(re.findall(r"'(SRC_[A-Z_]+)'", re.search(r"NO_BOOK = new Set\(\[(.*?)\]\)", js, re.S).group(1)))
    assert ids == {s for s, b in build_reference.SRC_BOOK.items() if b in ("EXP", "SYS", "TBCT")}
    assert set(build_reference.TIERS) == {"checked", "partial", "sourced", "draft", "hypothesis"}
    labels = re.search(r"TIER_TXT = \{(.*?)\}", js, re.S).group(1)
    assert set(re.findall(r"(\w+):", labels)) == set(build_reference.TIERS)


@needs_node
def test_browser_tier_equals_reference_tier_on_real_findings():
    from fastapi.testclient import TestClient
    from tvbt.api import app
    c = TestClient(app)
    entries = c.get("/api/evidence").json()["entries"]
    findings = []
    for b in CHARTS:
        d = c.post("/api/reasoning", json=b).json()
        for sysname in ("tu_vi", "bat_tu"):
            findings += d["systems"][sysname]["findings"]
    got = run_node({"entries": entries, "findings": findings})
    want, seen = ref_tiers(), {}
    n_cmp = 0
    for f, t in zip(findings, got):
        seen[t] = seen.get(t, 0) + 1
        if f["rule_id"] in want:
            n_cmp += 1
            assert t == want[f["rule_id"]], (f["rule_id"], t, want[f["rule_id"]])
    assert n_cmp >= 200, n_cmp          # most fired rules are on the reference page, so the comparison is not vacuous
    assert {"checked", "sourced", "hypothesis"} <= set(seen), seen


@needs_node
def test_every_evidence_entry_maps_to_checked_or_partial_for_a_verified_rule():
    """Hand-built finding: a verified, sourced rule takes its tier from the verdict alone (same table as tier())."""
    entries = [{"rule_id": f"R{i}", "verdict": v} for i, v in enumerate(["faithful", "unsupported_on_page", "partly", "misread", "cannot_verify"])]
    mk = lambda i, basis="verified", src="SRC_KHAO_LUAN": {"rule_id": f"R{i}", "basis": basis, "why": {"kinds": {f"source:{src}": "source"}}}
    fs = [mk(i) for i in range(5)] + [mk(0, "draft"), mk(0, src="SRC_EXPERIMENTAL"), mk(9)]
    assert run_node({"entries": entries, "findings": fs}) == ["checked", "checked", "partial", "sourced", "sourced", "draft", "hypothesis", "sourced"]
    for f, w in zip(fs[:5], ["checked", "checked", "partial", "sourced", "sourced"]):
        e = next(x for x in entries if x["rule_id"] == f["rule_id"])
        assert build_reference.tier({"sourceIds": ["SRC_KHAO_LUAN"], "reviewStatus": "verified"}, e) == w


def test_card_markup_only_adds_to_the_existing_ui():
    ui = (WEB / "ui.js").read_text("utf-8")
    assert "Xem nguyên văn" in ui and "evidenceExpander" in ui
    assert "Đã đối chiếu với sách" in ui and "Quy tắc nháp, chưa xác minh" in ui       # fallback labels kept
    bg = (WEB / "beginner.js").read_text("utf-8")
    assert "partialNote" in bg and "Khớp một phần" in bg
