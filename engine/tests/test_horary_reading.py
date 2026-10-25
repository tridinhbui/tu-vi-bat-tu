"""Audit of the horary output on many real charts: every cited rule exists in the KB with a source, the text never leaks ids or
English planet names, never repeats a sentence, agrees with the chart and the judgment, and keeps its disclaimers."""
import re
from functools import lru_cache

import pytest

from horary import chart as C, judgment as J, kb, narrative as N, questions as Q

TOPICS = [("career", "obtain_post"), ("love", "reconcile"), ("lost", "lost_item"), ("property", "buy"), ("travel", "long_trip"),
          ("finance", "loan_back"), ("business", "contract"), ("study", "exam")]
MOMENTS = [(2026, m, d, h) for m in (1, 4, 7, 10) for d in (3, 17) for h in (6, 15)]


@lru_cache(maxsize=None)
def run(moment, topic, sub, party="self"):
    y, m, d, h = moment
    ch = C.compute(C.HoraryInput(y, m, d, h, 20, "Asia/Ho_Chi_Minh", 21.0285, 105.8542, place="Hà Nội", near_cusp_deg=5))
    fr = Q.Frame("Câu hỏi thử nghiệm", topic, sub, party, confirmed=True).resolve()
    fr["text"] = "Câu hỏi thử nghiệm"
    j = J.judge(ch, fr)
    return ch, fr, j, N.compose(ch, fr, j)


CASES = [(mo, t, s) for i, mo in enumerate(MOMENTS) for (t, s) in TOPICS[i % 4: i % 4 + 4]]


def paragraphs(n):
    yield from n["quick"]["paragraphs"]
    for s in n["deep"]["sections"]:
        yield from s["paragraphs"]


@pytest.mark.parametrize("mo,topic,sub", CASES)
def test_every_ref_resolves_to_a_sourced_rule_or_a_testimony(mo, topic, sub):
    ch, fr, j, n = run(mo, topic, sub)
    known = {t["id"] for t in j["testimonies"]} | {c["id"] for c in j["considerations"]}
    for p in paragraphs(n):
        for r in p["refs"]:
            if r in known:
                continue
            rule = kb.rule(r)
            assert rule is not None, f"unknown rule id {r}"
            assert rule.get("sources"), f"rule {r} has no source"
    for t in j["testimonies"]:
        assert kb.rule(t["rule"]) is not None, f"testimony {t['id']} cites unknown rule {t['rule']}"
    for r in fr["rules"]:
        assert kb.rule(r) is not None, f"topic rule {r} missing from the KB"


@pytest.mark.parametrize("mo,topic,sub", CASES)
def test_text_hygiene(mo, topic, sub):
    _, _, _, n = run(mo, topic, sub)
    text = " ".join(p["text"] for p in paragraphs(n))
    assert not re.search(r"\b(lilly|bonatti|ptolemy)\.[a-z_]+", text), "rule id leaked into the prose"
    assert not re.search(r"\b(sun|moon|mercury|venus|mars|jupiter|saturn)\b", text), "English planet id in the prose"
    assert "None" not in text and "nan" not in text.split()
    assert N.DISCLAIMER in text


@pytest.mark.parametrize("mo,topic,sub", CASES)
def test_deep_reading_never_repeats_a_sentence(mo, topic, sub):
    _, _, _, n = run(mo, topic, sub)
    seen = {}
    for s in n["deep"]["sections"]:
        for p in s["paragraphs"]:
            for sent in re.split(r"(?<=[.!?])\s+", p["text"]):
                if len(sent) < 40 or sent in N.DISCLAIMER:
                    continue
                assert sent not in seen, f"repeated in {s['id']} and {seen[sent]}: {sent}"
                seen[sent] = s["id"]


@pytest.mark.parametrize("mo,topic,sub", CASES[:12])
def test_text_agrees_with_chart_and_judgment(mo, topic, sub):
    ch, fr, j, n = run(mo, topic, sub)
    assert n["quick"]["title"] == j["verdict"]["vi"] == n["deep"]["title"]
    sec = {s["id"]: s for s in n["deep"]["sections"]}
    assert [s["id"] for s in n["deep"]["sections"]] == ["context", "overview", "significators", "strength", "aspects", "balance",
                                                       "course", "conclusion", "care"]
    L1 = j["significators"]["querent"]["planet"]
    first = sec["significators"]["paragraphs"][0]["text"]
    assert N.PLANET[L1] in first and N._deg(ch.bodies[L1].lon) in first and f"nhà {ch.bodies[L1].house}" in first
    concl = sec["conclusion"]["paragraphs"][0]["text"]
    assert concl.startswith(N.VERDICT_HEAD[j["verdict"]["label"]])
    if j["timing"]:
        assert str(j["timing"]["house_rule"]["value"]) in " ".join(p["text"] for p in sec["conclusion"]["paragraphs"])


def test_finance_and_study_cautions_are_shown():
    _, _, _, n = run(MOMENTS[0], "finance", "loan_back")
    assert Q.CAUTIONS["finance"] in " ".join(p["text"] for p in n["quick"]["paragraphs"])
    _, _, _, n = run(MOMENTS[0], "study", "exam")
    care = next(s for s in n["deep"]["sections"] if s["id"] == "care")
    assert any("Lilly không có chương riêng về thi cử" in p["text"] for p in care["paragraphs"])


def test_same_input_same_text():
    a = run(MOMENTS[3], "love", "reconcile")[3]
    y, m, d, h = MOMENTS[3]
    C_ = C.compute(C.HoraryInput(y, m, d, h, 20, "Asia/Ho_Chi_Minh", 21.0285, 105.8542, place="Hà Nội", near_cusp_deg=5))
    fr = Q.Frame("Câu hỏi thử nghiệm", "love", "reconcile", confirmed=True).resolve()
    fr["text"] = "Câu hỏi thử nghiệm"
    b = N.compose(C_, fr, J.judge(C_, fr))
    assert a == b
