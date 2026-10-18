"""QA for the Personal Growth layer (tvbt/growth, /api/growth/*).

What is locked here:
  * feature flag: OFF -> 404 and every existing endpoint byte-identical with the flag ON or OFF;
  * grounding: every insight names anchors that are independently verified against the chart;
  * the three layers are separate and honest about their source; every insight has questions, a situation and a 7-30 day practice;
  * personalization: content follows the chart (Mệnh stars, Tứ Hóa palaces, year stem, VCD, Thân) and the reader's own context;
  * boundaries: no fatalism, no decision taken for the reader, crisis and fate questions handled before any chart content;
  * journal review is stateless and treats the reader's resonance as evidence that outranks the chart.
"""
from __future__ import annotations

import dataclasses
import itertools
import json
import random

import pytest
from fastapi.testclient import TestClient

from tvbt import bazi, tuvi
from tvbt.api import app
from tvbt.bazi_deep import pipeline
from tvbt.bazi_deep.model import ChartView
from tvbt.calendar_core import BirthInput, normalize
from tvbt.growth import decide, dialogue, journal, kb, navigator, profile, signals, text

client = TestClient(app)
SAMPLE = {"year": 1990, "month": 5, "day": 17, "hour": 10, "minute": 30, "gender": "male", "to_year": 2026}


def build(y, m, d, h, mi=0, g="male", year_now=None):
    nb = normalize(BirthInput(y, m, d, h, mi, "Asia/Ho_Chi_Minh", g, None, "vn", "early_zi_next_day", False))
    bz, tv = bazi.compute(nb), tuvi.compute(nb)
    deep = pipeline.analyse(ChartView.from_bazi(bz, nb.utc, g))
    sg = signals.read(tv, bz, deep, year_now or min(y + 35, 2049))
    return tv, bz, deep, sg, profile.build(sg)


def population(n=120, seed=11):
    R = random.Random(seed)
    for _ in range(n):
        yield (R.randint(1925, 2035), R.randint(1, 12), R.randint(1, 28), R.randint(0, 23), R.randint(0, 59), R.choice(["male", "female"]))


POP = [build(*b) for b in population()]


def items(pr):
    return pr["lessons"] + pr["blind_spots"]


# ------------------------------------------------------------------------------------------------------------- flag
def test_flag_off_returns_404(monkeypatch):
    monkeypatch.delenv("TVBT_GROWTH", raising=False)
    assert client.post("/api/growth/profile", json=SAMPLE).status_code == 404
    for path, body in [("/api/growth/dialogue", {"birth": SAMPLE, "question": "Tại sao?"}), ("/api/growth/navigate", {"birth": SAMPLE}),
                       ("/api/growth/compass", {"birth": SAMPLE}), ("/api/growth/journal-review", {"birth": SAMPLE})]:
        assert client.post(path, json=body).status_code == 404


def test_existing_endpoints_identical_with_flag_on(monkeypatch):
    monkeypatch.delenv("TVBT_GROWTH", raising=False)
    off = {p: client.post(p, json=SAMPLE).content for p in ("/api/chart", "/api/reasoning", "/api/analysis", "/api/year")}
    monkeypatch.setenv("TVBT_GROWTH", "1")
    on = {p: client.post(p, json=SAMPLE).content for p in off}
    assert on == off
    assert client.post("/api/growth/profile", json=SAMPLE).status_code == 200


def test_determinism(monkeypatch):
    monkeypatch.setenv("TVBT_GROWTH", "1")
    a = client.post("/api/growth/profile", json=SAMPLE).json()
    b = client.post("/api/growth/profile", json=SAMPLE).json()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


# -------------------------------------------------------------------------------------------------------- grounding
def test_every_insight_is_anchored_in_verified_chart_facts():
    for tv, bz, deep, sg, pr in POP:
        ids = {a["id"] for a in pr["anchors"]}
        for it in items(pr) + [pr["stage"]]:
            assert it["anchors"], it.get("id")
            assert set(it["anchors"]) <= ids, (it.get("id"), set(it["anchors"]) - ids)
        for a in pr["anchors"]:
            assert signals.verify_anchor(a, tv, bz), a
            if "dm_level" in a["check"]:
                assert a["check"]["dm_level"] == deep["facts"]["bazi.dm_level"]
        for dom, c in pr["compass"].items():
            assert set(c["anchors"]) <= ids


def test_three_layers_are_separate_and_honest():
    for *_, pr in POP:
        for it in items(pr):
            L = it["layers"]
            texts = [L["bieu_tuong"]["text"], L["tam_ly"]["text"], L["doi_song"]["text"]]
            assert all(t.strip() for t in texts) and len(set(texts)) == 3, it["id"]
            assert L["bieu_tuong"]["source"] in ("sach", "pho_thong", "he_thong")
            if L["bieu_tuong"]["source"] == "sach":
                assert L["bieu_tuong"]["cites"], it["id"]
            assert L["tam_ly"]["concept"]["name"] and L["tam_ly"]["concept"]["ref"]
            assert "không chứng minh" in L["tam_ly"]["note"]


def test_every_insight_has_reflection_situation_and_practice():
    for *_, pr in POP:
        for it in items(pr):
            e = it["exercise"]
            assert len(e["questions"]) >= 2, it["id"]
            assert e["scenario"]["situation"].strip() and e["scenario"]["try"].strip(), it["id"]
            assert e["practices"] and all(7 <= p["days"] <= 30 and p["action"].strip() and p["track"].strip() for p in e["practices"]), it["id"]
        assert pr["practices"] and len({p["id"] for p in pr["practices"]}) == len(pr["practices"])


# ---------------------------------------------------------------------------------------------------- personalization
def test_star_lessons_follow_menh_stars_exactly():
    for tv, bz, deep, sg, pr in POP:
        got = {it["star"] for it in pr["lessons"] if it["id"].startswith("L_STAR_")}
        assert got == set(sg.menh_stars)
        m = next(p for p in tv.palaces if p["name"] == "Mệnh")
        if m["major_stars"]:
            assert sg.menh_stars == m["major_stars"] and not sg.vcd
        else:
            opp = next(p for p in tv.palaces if p["branch_index"] == (m["branch_index"] + 6) % 12)
            assert sg.vcd and sg.borrowed == opp["major_stars"]
            assert any(it["id"] == "L_MENH_VCD" for it in pr["lessons"])


def test_year_stem_advice_and_hoa_palaces_match_the_chart():
    by_stem = kb.book("tu_hoa_vi")["by_stem"]
    for tv, bz, deep, sg, pr in POP:
        adv = next(it for it in pr["lessons"] if it["id"] == "L_YEAR_STEM_ADVICE")
        for a in by_stem[str(sg.year_stem)]:
            assert a["advice"] in adv["layers"]["bieu_tuong"]["text"]
        by_b = {p["branch_index"]: p["name"] for p in tv.palaces}
        ky = next((it for it in pr["lessons"] if it["id"] == "L_HOA_HOA_KY"), None)
        assert ky and ky["palace"] == by_b[tv.tu_hoa["Hóa Kỵ"]["branch"]]
        lo = by_b[tv.tu_hoa["Hóa Lộc"]["branch"]]
        assert any(it["id"] == "B_LOC_KY_SAME" for it in pr["blind_spots"]) == (lo == ky["palace"])


def test_compass_tendencies_name_stars_actually_in_the_domain_palaces():
    for tv, bz, deep, sg, pr in POP[:40]:
        ps = {p["name"]: p for p in tv.palaces}
        for dom, c in pr["compass"].items():
            for t in c["tendencies"]:
                if " ở cung " in t["from"]:
                    star, pal = t["from"].split(" ở cung ")
                    star = star.replace("Hình tượng ", "")
                    if star.startswith("Hóa"):
                        assert sg.hoa[star]["palace"] == pal
                    else:
                        if pal == "Mệnh (mượn)":
                            assert sg.vcd and star in sg.borrowed
                        else:
                            assert star in ps[pal]["major_stars"], (t, pal)


def test_profiles_differ_across_people():
    sets = [frozenset(it["id"] for it in items(pr)) for *_, pr in POP]
    js = [len(a & b) / len(a | b) for a, b in itertools.combinations(sets, 2)]
    assert sum(js) / len(js) < 0.6
    fingerprints = {json.dumps([it["layers"]["doi_song"]["text"] for it in items(pr)], ensure_ascii=False) for *_, pr in POP}
    assert len(fingerprints) / len(POP) > 0.9


def test_hour_changes_menh_and_therefore_the_top_lesson():
    seen = set()
    for h in range(0, 24, 2):
        *_, sg, pr = build(1990, 5, 17, h)
        seen.add((tuple(sg.menh_stars), pr["lessons"][0]["id"]))
    assert len({top for _, top in seen}) >= 4


def test_sample_chart_case_study():
    """Hand-checked against the sample chart (17/05/1990 10:30, nam): Mệnh Tý có Vũ Khúc + Thiên Phủ; Hóa Lộc (Thái Dương) và Hóa Kỵ
    (Thái Âm) cùng ở Phụ Mẫu (Sửu); Thân cư Phu Thê; năm Canh."""
    tv, bz, deep, sg, pr = build(1990, 5, 17, 10, 30, year_now=2026)
    ids = {it["id"] for it in items(pr)}
    assert {"L_STAR_VU_KHUC", "L_STAR_THIEN_PHU", "B_PAIR_VU_KHUC_THIEN_PHU", "B_LOC_KY_SAME", "L_THAN", "L_GROUP_TU_PHU_VU_TUONG"} <= ids
    assert next(it for it in pr["blind_spots"] if it["id"] == "B_LOC_KY_SAME")["palace"] == "Phụ Mẫu"
    assert next(it for it in pr["lessons"] if it["id"] == "L_THAN")["palace"] == "Phu Thê"
    assert "Canh" in next(it for it in pr["lessons"] if it["id"] == "L_YEAR_STEM_ADVICE")["title"]
    assert pr["control_bias"]["kind"] == "over"     # Vũ Khúc and Thiên Phủ both lean to over-control in the data
    assert pr["stage"]["lines"] and "Điền Trạch" in pr["stage"]["lines"][0]


# ------------------------------------------------------------------------------------------------- content and data QA
def test_star_content_is_complete_specific_and_unique():
    S = kb.stars()
    assert set(S) == set(kb.book("star_profiles")["stars"])
    fields = ("need", "gift", "lesson", "skill", "psych", "shadow", "questions", "scenario", "practices", "domains", "control_bias", "values", "ham_note", "signal_words")
    for name, d in S.items():
        assert all(d.get(f) for f in fields), name
        assert d["psych"]["concept"] in kb.load("concepts")["concepts"]
        assert set(d["domains"]) == {"career", "money", "love", "family"}
        assert all(v in kb.load("concepts")["values"] for v in d["values"])
        assert all(7 <= p["days"] <= 30 for p in d["practices"])
    for key in ("gift", "need", "skill"):
        assert len({d[key] for d in S.values()}) == 14, key
    assert len({d["shadow"]["habit"] for d in S.values()}) == 14
    assert len({q for d in S.values() for q in d["questions"]}) == 14 * 3


def test_keywords_are_multi_syllable_to_avoid_folded_ambiguity():
    """'tiền'/'tiến'/'tiên' all fold to 'tien': single-syllable keywords are banned everywhere."""
    D = kb.load("dialogue")
    words = [w for d in kb.stars().values() for w in d["signal_words"]] + D["crisis"] + D["distress"] + D["fate"]["patterns"] + D["fate"]["decision_patterns"]
    words += [w for t in (D["intents"], D["domains"]) for ws in t.values() for w in ws]
    words += navigator.HINT_OUTSIDE + navigator.HINT_CONTROL + navigator.HINT_INFLUENCE
    assert [w for w in words if len(w.split()) < 2] == []
    assert all(w == text.fold(w) for w in words)


def test_no_fatalism_no_deciding_no_cliches_anywhere():
    for *_, pr in POP:
        bad = [(s, text.lint(s)) for s in text.walk_strings(pr) if text.lint(s)]
        assert not bad, bad[:3]
        for q in ("Tại sao tôi luôn mắc kẹt?", "Tôi nên thay đổi điều gì trong công việc?", "Điểm mạnh nào tôi chưa tận dụng?", "Lá số nói gì về tính cách tôi?"):
            a = dialogue.answer(pr, q, {"situation": "dạo này nhiều việc"})
            assert not [s for s in text.walk_strings(a) if text.lint(s)]
        n = navigator.navigate(pr, "career", "công việc chậm", [{"text": "kỹ năng", "zone": "control"}])
        c = decide.decide(pr, "career", "chuyển việc", ["A", "B"], ["an_toan"], {"A": {"an_toan": 3}, "B": {"an_toan": 4}})
        assert not [s for s in [*text.walk_strings(n), *text.walk_strings(c)] if text.lint(s)]


def test_lint_is_word_bounded():
    assert text.lint("Gần đây điều gì làm bạn thấy là chính mình nhất?") == []
    assert text.lint("Hãy là chính mình!") == ["hay la chinh minh"]
    assert text.lint("Năm sau bạn chắc chắn sẽ giàu") == ["chac chan se"]


# --------------------------------------------------------------------------------------------------------- dialogue
PR = POP[0][4]
SAMPLE_PR = build(1990, 5, 17, 10, 30, year_now=2026)[4]


@pytest.mark.parametrize("q,intent", [("Tại sao tôi luôn mắc kẹt ở đây?", "stuck_why"), ("Tôi nên thay đổi điều gì?", "change_what"),
                                      ("Điểm mạnh nào tôi chưa tận dụng?", "strength"), ("Điểm mù của tôi là gì?", "blind")])
def test_dialogue_intents(q, intent):
    a = dialogue.answer(SAMPLE_PR, q)
    assert a["intent"] == intent and a["reply"]
    assert all(p["label"] and p["layer"] for p in a["reply"])
    assert a["grounding"] and set(a["grounding"]) <= {it["id"] for it in items(SAMPLE_PR)}


def test_dialogue_uses_what_the_reader_shares():
    q = "Tại sao tôi luôn mắc kẹt?"
    a = dialogue.answer(SAMPLE_PR, q, {"situation": "Tôi làm việc nhiều, bận rộn suốt, không có thời gian cho gia đình"})
    b = dialogue.answer(SAMPLE_PR, q, {"situation": "Tôi sợ mất ổn định nên không dám đổi việc, chưa phải lúc"})
    assert a["grounding"][0] == "B_STAR_VU_KHUC" and b["grounding"][0] == "B_STAR_THIEN_PHU"
    assert "bận rộn suốt" in a["reply"][0]["text"] and a["reply"][0]["layer"] == "tu_ban"
    c = dialogue.answer(SAMPLE_PR, "Tôi nên thay đổi điều gì trong tình cảm?")
    assert c["domain"] == "love" and c["grounding"][0] == "L_THAN"     # Thân cư Phu Thê in this chart
    assert any("Phá Quân ở cung Phu Thê" in p["text"] for p in c["reply"])   # the reader's own Phu Thê star, not a generic line
    v = dialogue.answer(SAMPLE_PR, q, {"values": ["tu_do"]})
    assert any("Tự do" in p["text"] for p in v["reply"])


def test_dialogue_rotates_with_exclude():
    a = dialogue.answer(SAMPLE_PR, "Tại sao tôi luôn mắc kẹt?")
    b = dialogue.answer(SAMPLE_PR, "Tại sao tôi luôn mắc kẹt?", exclude=a["grounding"])
    assert a["grounding"][0] != b["grounding"][0]


def test_dialogue_fate_and_decision_boundaries():
    f = dialogue.answer(SAMPLE_PR, "Bao giờ tôi lấy được vợ?")
    assert f["boundary"] == "fate" and f["grounding"] == [] and "không đưa ra dự đoán" in f["reply"][0]["text"]
    d = dialogue.answer(SAMPLE_PR, "Tôi có nên nghỉ việc không?")
    assert d["boundary"] == "decision" and "không chọn thay" in d["reply"][0]["text"]
    u = dialogue.answer(SAMPLE_PR, "hôm nay trời đẹp")
    assert u["intent"] == "unknown" and u["grounding"] == []


def test_dialogue_crisis_comes_before_everything():
    for q, ctx in [("Tôi muốn chết", None), ("Tại sao tôi luôn mắc kẹt?", {"situation": "tôi không muốn sống nữa"})]:
        a = dialogue.answer(SAMPLE_PR, q, ctx)
        assert a["boundary"] == "crisis" and a["grounding"] == []
        assert "115" in a["reply"][0]["text"] and "096 306 1414" in a["reply"][0]["text"]
        assert len(a["reply"]) == 1


def test_dialogue_distress_suggests_professional_help():
    a = dialogue.answer(SAMPLE_PR, "Tại sao tôi luôn mắc kẹt?", {"situation": "mất ngủ, kiệt sức, lo âu kéo dài"})
    assert any(p["layer"] == "an_toan" and "nhà tâm lý" in p["text"] for p in a["reply"])


# -------------------------------------------------------------------------------------------------------- navigator
def test_navigator_keeps_the_readers_own_sorting():
    cs = [{"text": "sếp quyết định thăng chức", "zone": "control"}, {"text": "thị trường khó khăn", "zone": "unsure"},
          {"text": "thói quen ngủ muộn", "zone": "unsure"}, {"text": "đồng nghiệp hay đùn việc", "zone": "influence"}]
    r = navigator.navigate(SAMPLE_PR, "career", "Ba năm không thăng tiến", cs)
    assert [i["text_user"] for i in r["zones"]["control"]] == ["sếp quyết định thăng chức"]   # never moved by the engine
    hints = {i["text_user"]: i["hint"]["zone"] for i in r["zones"]["unsure"]}
    assert hints == {"thị trường khó khăn": "outside", "thói quen ngủ muộn": "control"}
    assert all("hint" not in i for z in ("control", "influence") for i in r["zones"][z])
    assert r["bias_check"]["kind"] == "over" and len(r["steps"]) == 4


def test_navigator_no_false_pattern_from_folded_words():
    r = navigator.navigate(SAMPLE_PR, "career", "Ba năm không thăng tiến", [])
    assert r["pattern_hits"] == []                                 # 'thăng tiến' must not match 'tiền bạc'
    r2 = navigator.navigate(SAMPLE_PR, "career", "Tôi làm việc nhiều, bận rộn cả tuần", [])
    assert [h["insight"] for h in r2["pattern_hits"]] == ["B_STAR_VU_KHUC"]


def test_navigator_safety_and_distress():
    assert navigator.navigate(SAMPLE_PR, "self", "tôi muốn tự tử", [])["safety"]["kind"] == "crisis"
    r = navigator.navigate(SAMPLE_PR, "self", "trầm cảm", [], duration="Nhiều năm")
    assert r["notes"]


# ---------------------------------------------------------------------------------------------------------- compass
def test_compass_mirrors_the_readers_ratings_and_never_chooses():
    r = decide.decide(SAMPLE_PR, "career", "ở lại hay chuyển", ["Ở lại", "Chuyển"], ["an_toan", "tu_do", "khong_ton_tai"],
                      {"Ở lại": {"an_toan": 5, "tu_do": 1}, "Chuyển": {"an_toan": 2, "tu_do": 5}})
    assert [v["id"] for v in r["values"]] == ["an_toan", "tu_do"]
    assert {m["option"]: m["total"] for m in r["matrix"]} == {"Ở lại": 6, "Chuyển": 7}
    assert "gần nhau" in r["notes"][0]
    for s in [r["ownership"], *r["notes"], *r["values_reflection"]]:
        assert "Ở lại" not in s and "Chuyển" not in s
    assert any("Tự do" in s and "không nằm trong hình tượng" in s for s in r["values_reflection"])
    assert {t["id"] for t in r["tools"]} == {"reversibility", "ten_ten_ten", "premortem", "values"}


# ---------------------------------------------------------------------------------------------------------- journal
def _entries(n=8):
    return [{"date": f"2026-09-{i + 1:02d}", "text": "làm việc nhiều, bận rộn" if i < n // 2 else "đi dạo cùng gia đình", "mood": 2 if i < n // 2 else 4,
             "insight_id": "B_STAR_VU_KHUC", "resonance": "dung", "practice_id": "L_STAR_VU_KHUC#0", "practice_done": i != 2} for i in range(n)]


def test_journal_review_tracks_change_over_time():
    r = journal.review(SAMPLE_PR, _entries())
    assert r["count"] == 8 and r["mood"]["trend"]["delta"] == 2.0 and "cao hơn" in r["mood"]["trend"]["text"]
    assert r["resonance"][0]["dung"] == 8 and "hành vi cụ thể" in r["resonance"][0]["verdict"]
    p = r["practices"][0]
    assert p["days_done"] == 7 and p["target_days"] == 7 and p["best_streak"] == 5      # day 3 skipped: 4,5,6,7,8 is the longest run
    ws = next(w for w in r["word_shifts"] if w["insight"] == "B_STAR_VU_KHUC")
    assert (ws["early"], ws["late"]) == (4, 0) and "ít hơn" in ws["text"]
    assert r["barnum"]["id"] == "barnum" and "không lưu" in r["privacy"]


def test_journal_resonance_verdicts_respect_the_reader():
    one = journal.review(SAMPLE_PR, [{"date": "2026-09-01", "text": "x", "insight_id": "L_STAR_THIEN_PHU", "resonance": "dung"}])
    assert one["resonance"][0]["verdict"].startswith("Mới có một lần")
    no = journal.review(SAMPLE_PR, [{"date": f"2026-09-0{i}", "text": "x", "insight_id": "L_STAR_THIEN_PHU", "resonance": "khong"} for i in range(1, 4)])
    assert "Trải nghiệm của bạn được ưu tiên" in no["resonance"][0]["verdict"]
    assert journal.review(SAMPLE_PR, [])["count"] == 0


def test_journal_api_is_stateless(monkeypatch):
    monkeypatch.setenv("TVBT_GROWTH", "1")
    a = client.post("/api/growth/journal-review", json={"birth": SAMPLE, "entries": _entries()}).json()
    b = client.post("/api/growth/journal-review", json={"birth": SAMPLE, "entries": _entries(2)}).json()
    assert a["count"] == 8 and b["count"] == 2


# --------------------------------------------------------------------------------------------------------------- API
def test_api_endpoints_end_to_end(monkeypatch):
    monkeypatch.setenv("TVBT_GROWTH", "1")
    r = client.post("/api/growth/dialogue", json={"birth": SAMPLE, "question": "Tại sao tôi luôn mắc kẹt?", "context": {"situation": "bận rộn suốt"}})
    assert r.status_code == 200 and r.json()["grounding"]
    r = client.post("/api/growth/navigate", json={"birth": SAMPLE, "domain": "career", "situation": "chậm", "concerns": [{"text": "a", "zone": "bogus"}]})
    assert r.status_code == 422
    r = client.post("/api/growth/compass", json={"birth": SAMPLE, "domain": "money", "decision": "mua nhà", "options": ["Mua", "Thuê"], "values": ["an_toan"],
                                                  "ratings": {"Mua": {"an_toan": 4}}})
    assert r.status_code == 200 and r.json()["domain"] == "money"
    assert client.post("/api/growth/dialogue", json={"birth": SAMPLE, "question": ""}).status_code == 422
    assert client.post("/api/growth/profile", json={**SAMPLE, "year": 1800}).status_code == 422


def test_no_insight_tells_the_same_palace_twice():
    for tv, bz, deep, sg, pr in POP:
        ids = [it["id"] for it in items(pr)]
        assert len(ids) == len(set(ids))
        if sg.than["name"] == "Phúc Đức":
            assert "B_GAP_PHUC" not in ids


def test_population_exercises_every_insight_family():
    fam = {it["id"].rsplit("_", 1)[0] if it["id"].startswith(("L_STAR", "B_STAR", "L_DM", "B_PHUC")) else it["id"] for *_, pr in POP for it in items(pr)}
    prefixes = {"L_MENH_VCD", "B_PAIR", "B_GAP_THAN", "B_GAP_PHUC", "B_LOC_KY_SAME", "B_MENH_TUAN_TRIET", "B_MENH_CUC", "B_CROSS_SYSTEM",
                "B_ELEM_EXCESS", "B_ELEM_LACK", "L_BAZI_YONG", "L_THAN", "L_HOA_HOA_KHOA", "B_HOA_HOA_QUYEN", "B_BAZI_STRENGTH"}
    missing = {p for p in prefixes if not any(f.startswith(p) for f in fam)}
    assert not missing, missing
