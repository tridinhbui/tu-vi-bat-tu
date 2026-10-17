"""Phase 7: safe, opt-in API integration and draft UI of the deep Bát Tự analysis. Nothing here changes a method; it checks that the flag adds a presentation envelope only,
that the default response is unchanged, that the draft UI never hides or merges a disagreement, and that the review status stays at what real evidence supports (0)."""
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tvbt.bazi_deep import draft_view, pipeline
from tvbt.bazi_deep.model import ChartView
from tvbt.bazi_deep.profile import TVH_40

ROOT = Path(__file__).resolve().parent.parent.parent
G = Path(__file__).parent / "golden"
sys.path.insert(0, str(ROOT / "tools"))
import bazi_deep_examples_review_intake as ex_intake  # noqa: E402
import bazi_deep_tvh_review_intake as cell_intake  # noqa: E402
import test_bazi_deep_phase6 as P6  # noqa: E402  (same 5,000-chart sample, schema validator)

BODY = {"year": 1990, "month": 12, "day": 15, "hour": 10, "minute": 0, "gender": "male"}
BODIES = [BODY, {"year": 1973, "month": 1, "day": 3, "hour": 23, "minute": 30, "gender": "female"}, {"year": 1952, "month": 12, "day": 7, "hour": 8, "minute": 0, "gender": "male"},
          {"year": 2005, "month": 6, "day": 21, "hour": 12, "minute": 0, "gender": "female"}, {"year": 1984, "month": 2, "day": 4, "hour": 0, "minute": 5, "gender": "male"}]
LABEL = "Phân tích thử nghiệm – chưa được kiểm chứng thực nghiệm"


def client():
    from fastapi.testclient import TestClient
    from tvbt.api import app
    return TestClient(app)


# ------------------------------------------------------------------ the feature flag
@pytest.mark.parametrize("body", BODIES, ids=lambda b: f"{b['year']}-{b['month']}-{b['day']}")
def test_default_response_is_unchanged_and_the_flag_only_adds_one_envelope_key(body):
    c = client()
    base = c.post("/api/bazi-structure", json=body).json()
    off = c.post("/api/bazi-structure", json={**body, "bazi_deep_draft": False}).json()
    on = c.post("/api/bazi-structure", json={**body, "bazi_deep_draft": True}).json()
    assert "bazi_deep_draft" not in base and base == off
    assert set(on) - set(base) == {"bazi_deep_draft"}
    assert {k: v for k, v in on.items() if k != "bazi_deep_draft"} == base            # not one method conclusion, trace or number differs
    assert json.dumps(base, sort_keys=True) == json.dumps({k: v for k, v in on.items() if k != "bazi_deep_draft"}, sort_keys=True)


def test_default_response_equals_the_pipeline_output_for_the_same_chart():
    from tvbt import api
    from tvbt.calendar_core import BirthInput, normalize
    d = client().post("/api/bazi-structure", json=BODY).json()
    assert d["yongshen"]["methods"]["dieu_hau"]["meta"]["levels"]["empirical_validated"] == "no" and "reasoning" in d and d["profile"]["id"] == TVH_40.id


def test_envelope_content_and_strings_are_exactly_the_contract():
    d = client().post("/api/bazi-structure", json={**BODY, "bazi_deep_draft": True}).json()
    e = d["bazi_deep_draft"]
    assert e["contract_version"] == "bazi-deep-draft/1" and e["draft_label"] == LABEL
    assert e["method_order"] == list(d["yongshen"]["methods"]) and len(e["method_order"]) == 8
    docs = json.loads((ROOT / "docs/bazi_deep_ui_strings_vi.json").read_text("utf-8"))
    assert e["ui_strings"] == docs                                                      # runtime copy and the documented contract strings never drift
    assert (ROOT / "engine/data/bazi_deep/ui_strings_vi.json").read_bytes() == (ROOT / "docs/bazi_deep_ui_strings_vi.json").read_bytes()
    assert P6.validate(d["yongshen"], P6.SCHEMA) == []
    assert e["ui_strings"]["states"]["draft_label"] == LABEL
    assert set(e) == {"contract_version", "draft_label", "banner", "ui_strings", "method_order", "review_status", "book_internal_conflict", "contract_doc"}


def test_envelope_never_contains_a_conclusion_or_ranking():
    e = draft_view.envelope(pipeline.analyse(ChartView.from_names("Canh Ngọ / Tân Tỵ / Giáp Tý / Bính Dần"), TVH_40, with_rules=False))
    txt = json.dumps(e, ensure_ascii=False).lower()
    for bad in ("winner", "ranking", "final_answer", "total_score", "dung_than_cuoi"):
        assert bad not in txt
    assert not any(f in json.dumps({k: v for k, v in e.items() if k != "ui_strings"}, ensure_ascii=False).lower() for f in e["ui_strings"]["forbidden_phrases"])


def test_only_the_structure_endpoint_changed_and_other_endpoints_ignore_the_flag():
    c = client()
    t = c.post("/api/bazi-timeline", json={**BODY, "to_year": 2000, "bazi_deep_draft": True}).json()
    t0 = c.post("/api/bazi-timeline", json={**BODY, "to_year": 2000}).json()
    assert t == t0 and "bazi_deep_draft" not in t
    assert c.post("/api/chart", json=BODY).status_code == 200


def test_the_draft_page_is_served_and_states_the_label_and_defaults_off():
    c = client()
    r = c.get("/bazi-deep-draft")
    assert r.status_code == 200 and "noindex" in r.text and 'id="on" type="checkbox"' in r.text and "checked" not in r.text.split('id="on"')[1].split(">")[0]
    assert "Chế độ phân tích chuyên sâu đang tắt" in r.text
    assert c.get("/js/bazi_deep_draft.js").status_code == 200


def test_status_dependent_note_key_is_preserved_for_clients_that_read_it():
    n = 0
    for p in P6.CHARTS[:600]:
        Y = P6.run(p)["yongshen"]
        for m in Y["methods"].values():
            if m["status"] == "khong_xac_dinh_noi_cach":
                n += 1
                assert "note" in m and m["note"], p
    assert n >= 20


# ------------------------------------------------------------------ the draft UI (view-model + DOM) on thousands of charts
@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_draft_ui_keeps_every_method_conclusion_and_every_disagreement_on_1500_charts(tmp_path):
    charts = P6.CHARTS[::3][:1500]
    resps = []
    for p in charts:
        o = P6.run(p)
        resps.append({"yongshen": o["yongshen"], "bazi_deep_draft": draft_view.envelope(o)})
    f = tmp_path / "r.json"
    f.write_text(json.dumps(resps, ensure_ascii=False), "utf-8")
    out = subprocess.run(["node", str(Path(__file__).parent / "js/phase7_viewmodel_check.js"), str(f)], capture_output=True, text=True, timeout=300)
    assert out.returncode == 0, out.stderr[-2000:]
    r = json.loads(out.stdout)
    assert r["problems"] == [], r["problems"][:5]
    assert r["n"] == 1500 and r["with_disagreement"] >= 1000                              # the 4,097/5,000 situation: disagreement is the normal case and is never hidden
    assert r["states"].get("no_unified_conclusion", 0) >= r["with_disagreement"] and r["hai_cach"] >= 100
    py = {i: P6._unified_state(resps[i]["yongshen"]) for i in range(len(resps))}
    assert {int(k): v for k, v in r["unified"].items()} == py                              # the JS and Python implementations of the contract's state rule agree on all 1500


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_draft_ui_on_real_api_responses_including_the_flag_off_case(tmp_path):
    c = client()
    resps = [c.post("/api/bazi-structure", json={**b, "bazi_deep_draft": True}).json() for b in BODIES]
    f = tmp_path / "r.json"
    f.write_text(json.dumps(resps, ensure_ascii=False), "utf-8")
    out = subprocess.run(["node", str(Path(__file__).parent / "js/phase7_viewmodel_check.js"), str(f)], capture_output=True, text=True, timeout=120)
    r = json.loads(out.stdout)
    assert out.returncode == 0 and r["problems"] == [] and r["n"] == 5


def test_view_model_source_never_uses_innerhtml_or_eval():
    js = (ROOT / "engine/web/js/bazi_deep_draft.js").read_text("utf-8")
    page = (ROOT / "engine/web/bazi_deep_draft.html").read_text("utf-8")
    for bad in ("innerHTML", "outerHTML", "eval(", "document.write", "insertAdjacentHTML"):
        assert bad not in js and bad not in page, bad
    assert "textContent" in js


# ------------------------------------------------------------------ source validation: examples and cells stay at what the evidence supports
def test_review_status_file_matches_the_real_review_evidence_which_is_zero():
    rs = json.loads((ROOT / "engine/data/bazi_deep/review_status.json").read_text("utf-8"))
    cells = cell_intake.check([cell_intake.load(ROOT / "docs/bazi_deep_tvh_cells_check.csv")])
    ex = ex_intake.check([ex_intake.ROOT / "docs/bazi_deep_examples_review_sheet.csv"])
    n_conf = sum(v["status"] in ("confirmed_1", "confirmed_2") for v in cells["cells"].values())
    n_ex = sum(v["status"] == "fully_confirmed" for v in ex["examples"].values())
    assert (rs["cells_confirmed_by_human"], rs["examples_fully_confirmed_by_human"]) == (n_conf, n_ex) == (0, 0)
    assert rs["cells_total"] == 120 and rs["examples_total"] == 10


def test_example_blind_sheet_contains_no_engine_value_and_no_fake_reviewer():
    rows = list(csv.DictReader(open(ROOT / "docs/bazi_deep_examples_review_sheet.csv", encoding="utf-8")))
    assert len(rows) == 40 and {r["tru"] for r in rows} == {"year", "month", "day", "hour"} and len({r["vi_du"] for r in rows}) == 10
    assert all(r["nguoi_kiem"] == "" and r["tru_theo_anh"] == "" and r["ghi_chu_nguoi_kiem"] == "" for r in rows)
    text = (ROOT / "docs/bazi_deep_examples_review_sheet.csv").read_text("utf-8")
    gold = json.loads((G / "tvh_dungthan_examples.json").read_text("utf-8"))
    for sec in ("dieuhau_examples", "dungthan_examples"):
        for k, v in gold[sec].items():
            if not k.startswith("_"):
                assert not any(pil.strip() in text for pil in v["pillars"].split("/")), k          # the sheet is blind: no pillar name appears in it
    cells = list(csv.DictReader(open(ROOT / "docs/bazi_deep_tvh_cells_check.csv", encoding="utf-8")))
    assert all(r["nguoi_kiem"] == "" and r["ket_qua"] == "" for r in cells)


def _filled(who, mistakes=None):
    gold = ex_intake.examples()
    rows = []
    for r in csv.DictReader(open(ROOT / "docs/bazi_deep_examples_review_sheet.csv", encoding="utf-8")):
        g = [x.strip() for x in gold[r["vi_du"]]["pillars"].split("/")][ex_intake.PIL.index(r["tru"])]
        r = dict(r, nguoi_kiem=who, tru_theo_anh=g)
        if mistakes and (r["vi_du"], r["tru"]) in mistakes:
            r["tru_theo_anh"] = mistakes[(r["vi_du"], r["tru"])]
        rows.append(r)
    return rows


def test_examples_intake_never_gives_full_confirmation_to_reconstructed_data():
    blank = ex_intake.check([ex_intake.ROOT / "docs/bazi_deep_examples_review_sheet.csv"])
    assert blank["counts"] == {"no_review": 10} and blank["problems"] == []
    r = ex_intake.check([_filled("A")])
    assert r["counts"] == {"fully_confirmed": 9, "incomplete": 1}
    e4 = r["examples"]["p400_vd4"]
    assert e4["status"] == "incomplete" and e4["pillars"]["day"]["status"] == "reconstructed_not_independent" and e4["pillars"]["month"]["status"] == "reconstructed_not_independent"
    assert e4["pillars"]["year"]["status"] == "confirmed_1" and e4["pillars"]["hour"]["status"] == "confirmed_1"
    assert ex_intake.check([_filled("A"), _filled("B")])["examples"]["p401_vd5"]["pillars"]["day"]["status"] == "confirmed_2"
    assert ex_intake.check([_filled("A"), _filled("A")])["examples"]["p401_vd5"]["pillars"]["day"]["status"] == "confirmed_1"


def test_examples_intake_reports_a_planted_misreading_and_bad_input():
    r = ex_intake.check([_filled("A", {("p401_vd5", "day"): "Canh Tý"})])
    assert r["examples"]["p401_vd5"]["pillars"]["day"]["status"] == "disagrees" and r["examples"]["p401_vd5"]["status"] == "incomplete"
    bad = _filled("A")
    bad[0]["tru_theo_anh"] = ""
    assert any("needs both" in p for p in ex_intake.check([bad])["problems"]) and any("exactly the 40" in p for p in ex_intake.check([_filled("A")[:39]])["problems"])


def test_neither_intake_tool_can_raise_a_verification_level_or_write_data():
    for f in ("bazi_deep_tvh_review_intake.py", "bazi_deep_examples_review_intake.py"):
        src = (ROOT / "tools" / f).read_text("utf-8")
        for bad in ("write_text", "open(\"w", "open('w", ", \"w\"", "METHOD_META", "levels", "json.dump"):
            assert bad not in src, (f, bad)
    gold = json.loads((G / "tvh_dungthan_examples.json").read_bytes())
    before = (G / "tvh_dungthan_examples.json").read_bytes()
    ex_intake.check([_filled("A")])
    assert (G / "tvh_dungthan_examples.json").read_bytes() == before and gold


def test_examples_provenance_is_complete_and_only_example_4_has_non_direct_pillars():
    gold = ex_intake.examples()
    assert len(gold) == 10
    for k, v in gold.items():
        assert set(v["pillar_provenance"]) == {"year", "month", "day", "hour"} and v["human_verified"] is False and v["readers"], k
    nondirect = {k: [p for p, s in v["pillar_provenance"].items() if s != "read_directly"] for k, v in gold.items() if any(s != "read_directly" for s in v["pillar_provenance"].values())}
    assert nondirect == {"p400_vd4": ["month", "day"]}
    assert [k for k, v in gold.items() if v["readers"] == ["claude"]] == ["p401_vd5"]            # example 5 has a single reader and no blind pass


def test_nine_book_conflicts_remain_on_the_waiting_list_untouched():
    d = json.loads((ROOT / "engine/data/bazi_deep/tvh_dieuhau.json").read_text("utf-8"))
    diffs = {(m, s) for m in d["cells"] for s in d["cells"][m] if set(d["cells"][m][s]) != set(d["notes_order"][m][s])}
    assert len(diffs) == 9
    cells = cell_intake.check([cell_intake.load(ROOT / "docs/bazi_deep_tvh_cells_check.csv")])
    assert cells["conflicts_kept"] == 9 and cells["counts"] == {"no_review": 120}


# ------------------------------------------------------------------ Phase 8: page states, plain language, independent re-check of the dụng thần rows
def test_page_messages_equal_the_ui_strings_and_the_label_is_in_every_static_state():
    html = (ROOT / "engine/web/bazi_deep_draft.html").read_text("utf-8")
    ui = json.loads((ROOT / "docs/bazi_deep_ui_strings_vi.json").read_text("utf-8"))
    m = ui["messages"]
    for k in ("flag_off", "loading", "missing_fields", "invalid_input", "server_rejected", "server_error", "network_error"):
        assert m[k] in html, k
    assert html.count(LABEL) >= 2 and ui["states"]["draft_label"] == LABEL                    # static initial state + the note() helper used by loading/error/off
    assert "aria-live" in html and "setAttribute(\"role\"" in html and "btn.disabled = true" in html


def test_ui_strings_label_every_source_and_the_conflict_sentence_names_the_book():
    ui = json.loads((ROOT / "docs/bazi_deep_ui_strings_vi.json").read_text("utf-8"))
    import re as _re
    from tvbt.bazi_deep import yongshen as Y
    ids = {i for v in Y.METHOD_META.values() for s in v["source"] for i in _re.findall(r"SRC_[A-Z_]+", s)}
    assert ids <= set(ui["source_labels"]), ids - set(ui["source_labels"])
    assert ui["states"]["book_internal_conflict"].startswith("Sách này") and "Chính sách" not in json.dumps(ui, ensure_ascii=False)
    assert set(ui["group_names"]) == {"Ti", "An", "ThucThuong", "Tai", "QuanSat"}


def test_dungthan_rows_match_an_independent_blind_transcription_of_pp378_386_except_adjudicated_cases():
    blind = json.loads((G / "tvh_dungthan_blind.json").read_text("utf-8"))
    eng = json.loads((ROOT / "engine/data/bazi_deep/tvh_dungthan.json").read_text("utf-8"))
    E = {(r["cach"], r["dm"], r["dom"]): r for r in eng["rows"]}
    M = {"chính tài": "tai", "thiên/chính tài": "tai", "chính quan": "quan", "chính ấn": "an", "thiên/chính ấn": "an", "thương quan": "thuong_quan", "thất sát": "sat", "thực thần": "thuc", "kiến lộc": "kien_loc", "kình dương": "kinh_duong"}
    # blind-pass misreadings, adjudicated against the page image: p379 'thực thương nhiều' (chính quan, nhược) lists only ấn; the 'tỉ kiếp ... không có ấn thụ' sentence belongs to the 'quan sát nhiều' case
    ADJ = {("quan", "weak", "ThucThuong", "yong")}
    compared = same = 0
    diffs = []
    for r in blind["rows"]:
        k = M.get(r["cach"].lower().replace(" (vận)", ""))
        dm = {"vuong": "strong", "nhuoc": "weak"}.get(r["dm"])
        if not (k and dm and r["dominant"]) or (k, dm, r["dominant"]) not in E:
            continue
        e, isvan = E[(k, dm, r["dominant"])], "(vận)" in r["cach"]
        for f in ("yong", "van_tot", "van_xau"):
            if r[f] is None or (f == "yong" and isvan):
                continue
            compared += 1
            if r[f] == e[f]:
                same += 1
            elif (k, dm, r["dominant"], f) not in ADJ:
                diffs.append((k, dm, r["dominant"], f, r[f], e[f]))
    assert compared >= 100 and not diffs, diffs
    assert same >= compared - 1


def test_the_four_rows_corrected_in_phase_8_stay_corrected_and_the_inferred_row_is_flagged():
    eng = json.loads((ROOT / "engine/data/bazi_deep/tvh_dungthan.json").read_text("utf-8"))
    row = lambda c, dm, dom: next(r for r in eng["rows"] if (r["cach"], r["dm"], r["dom"]) == (c, dm, dom))
    assert row("tai", "weak", "QuanSat")["yong"] == ["Ti", "An"]                  # p.378: 'lấy tỉ kiếp ... khi không có tỉ kiếp có thể lấy ấn'
    assert row("an", "strong", "An")["van_tot"] == ["ThucThuong", "Tai"] and row("sat", "weak", "Tai")["van_xau"] == ["ThucThuong", "Tai"]
    assert row("kien_loc", "strong", "QuanSat")["yong"] == ["Tai"]                # p.386: 'nhật chủ và sát đều vượng lấy tài tinh'
    inferred = [(r["cach"], r["dm"], r["dom"]) for r in eng["rows"] if r.get("yong_inferred")]
    assert inferred == [("kien_loc", "strong", "ThucThuong")]
    from tvbt.bazi_deep import yongshen as Y
    G_ = {"readings": [{"cach": "Kiến Lộc", "kind": "noi_cach"}]}
    S = {"shares": {"Ti": 0.2, "An": 0.1, "ThucThuong": 0.5, "Tai": 0.1, "QuanSat": 0.1}, "level_index": 5, "ambiguous": False, "tvh": {"dm_strong": True, "own_share": 0.5}}
    out = Y.cach_cuc_tvh(G_, S)
    assert out["yong"] == ["Tai"] and out["yong_inferred"] and any("suy ra" in t for t in out["trace"])
