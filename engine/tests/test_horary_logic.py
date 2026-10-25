"""Horary logic on constructed configurations (no ephemeris): pair states, prohibition, frustration, translation, collection,
the void Moon, dignities, reception, solar phase, besieging, considerations, the classifier and the weighing of testimonies."""
from types import SimpleNamespace as NS

import pytest

from horary import considerations as K, dignity as D, events as E, judgment as J, questions as Q, relations as R
from horary.astro import TRAD

ORBS = {"saturn": 10, "jupiter": 12, "mars": 7.5, "sun": 17, "venus": 8, "mercury": 7, "moon": 12.5}
T0 = 2461000.0


def body(p, lon, speed, house=1):
    return NS(id=p, lon=lon % 360, speed=speed, retrograde=speed < 0, house=house, lat=0.0, traditional=True)


def mk_chart(pos, houses=None, is_day=True, cusps=None):
    houses = houses or {}
    bodies = {p: body(p, lon, sp, houses.get(p, 1)) for p, (lon, sp) in pos.items()}
    return NS(jd_ut=T0, bodies=bodies, is_day=is_day, cusps=cusps or [30.0 * i for i in range(12)], asc=0.0,
              nodes={"north": 300.0, "south": 120.0}, planetary_hour={"available": False}, fortune=0.0)


def mk_ev(perfs=(), stations=(), ingresses=()):
    return {"jd0": T0, "back": 45, "fwd": 400, "perfections": sorted(perfs, key=lambda p: p.jd),
            "stations": list(stations), "ingresses": list(ingresses), "max_residual_arcsec": 0.0}


def perf(a, b, angle, dt, la=0.0, lb=0.0):
    return E.Perfection(a, b, angle, T0 + dt, la, lb, False, False)


# a sky where nothing else is near: all planets far apart, slow, so only the pairs we set up are in orb
FAR = {"sun": (100.0, 1.0), "moon": (215.0, 13.0), "mercury": (330.0, 1.2), "venus": (45.0, 1.1),
       "mars": (160.0, 0.6), "jupiter": (270.0, 0.1), "saturn": (5.0, 0.05)}


def test_pair_state_applying_and_separating():
    pos = dict(FAR, mars=(10.0, 0.6), saturn=(15.0, 0.05))          # Mars 5 deg behind Saturn, faster: applying conjunction
    ch = mk_chart(pos)
    ev = mk_ev([perf("mars", "saturn", 0, 9.1)])
    st = R.pair_state(ch, ev, "mars", "saturn", ORBS)
    assert (st.angle, st.motion, st.applier, st.within_orb) == (0, "applying", "mars", True)
    assert st.next_perfection_jd == pytest.approx(T0 + 9.1)
    pos2 = dict(FAR, mars=(20.0, 0.6), saturn=(15.0, 0.05))
    st2 = R.pair_state(mk_chart(pos2), mk_ev([perf("mars", "saturn", 0, -8.0)]), "mars", "saturn", ORBS)
    assert st2.motion == "separating" and st2.last_perfection_jd == pytest.approx(T0 - 8.0)


def test_retrograde_slower_planet_applies_by_its_own_motion():
    pos = dict(FAR, mercury=(118.0, -0.8), jupiter=(112.0, 0.1))     # Mercury retrograde moving back onto Jupiter
    st = R.pair_state(mk_chart(pos), mk_ev([perf("mercury", "jupiter", 0, 6.7)]), "mercury", "jupiter", ORBS)
    assert st.motion == "applying" and st.applier == "mercury"


def test_whole_sign_vs_orb():
    pos = dict(FAR, venus=(28.0, 1.1), saturn=(91.0, 0.05))           # square 63 deg apart -> nearest is sextile... use trine
    st = R.pair_state(mk_chart(pos), mk_ev(), "venus", "saturn", ORBS)
    assert st.angle == 60 and not st.by_sign                          # 28 Aries to 1 Cancer: three signs apart, a sextile only by orb


def test_prohibition_interposer_in_orb_and_first():
    # L1 Mars applying to L2 Saturn (perfects in 10 days); Venus is applying to Saturn within orb and perfects in 3 days
    pos = dict(FAR, mars=(10.0, 0.6), saturn=(16.0, 0.05), venus=(13.0, 1.1))
    ch = mk_chart(pos)
    ev = mk_ev([perf("venus", "saturn", 0, 2.8), perf("mars", "saturn", 0, 10.9)])
    pairs = R.all_pairs(ch, ev, ORBS)
    cfg = R.configurations(ch, ev, pairs, "mars", "saturn", ORBS)
    kinds = [c.kind for c in cfg]
    assert "perfection" in kinds and "prohibition" in kinds
    pro = next(c for c in cfg if c.kind == "prohibition")
    assert pro.planets[0] == "venus" and pro.detail["by_body"]


def test_moon_is_never_the_interposer_between_the_querents_significators():
    pos = dict(FAR, mars=(10.0, 0.6), saturn=(16.0, 0.05), moon=(8.0, 13.0))
    ch = mk_chart(pos)
    ev = mk_ev([perf("moon", "saturn", 0, 0.6), perf("mars", "saturn", 0, 10.9)])
    cfg = R.configurations(ch, ev, R.all_pairs(ch, ev, ORBS), "mars", "saturn", ORBS)
    assert "prohibition" not in [c.kind for c in cfg]


def test_frustration_heavier_planet_meets_another_first():
    # Venus applies to Mars; Mars itself perfects with Jupiter (in orb, applying) before Venus arrives
    pos = dict(FAR, venus=(40.0, 1.1), mars=(46.0, 0.6), jupiter=(49.0, 0.1))
    ch = mk_chart(pos)
    ev = mk_ev([perf("mars", "jupiter", 0, 6.0), perf("venus", "mars", 0, 12.0)])
    cfg = R.configurations(ch, ev, R.all_pairs(ch, ev, ORBS), "venus", "mars", ORBS)
    fr = next(c for c in cfg if c.kind == "frustration")
    assert fr.planets[:2] == ["mars", "jupiter"] and fr.detail["by_body"]


def test_translation_of_light():
    # Saturn (L1) and Jupiter (LQ) apart (no aspect in orb); the Moon has just left Saturn and applies to Jupiter by trine
    pos = dict(FAR, saturn=(10.0, 0.05), jupiter=(145.0, 0.1), moon=(17.0, 13.0))
    ch = mk_chart(pos)
    ev = mk_ev([perf("moon", "saturn", 0, -0.55), perf("moon", "jupiter", 120, 0.6)])
    cfg = R.configurations(ch, ev, R.all_pairs(ch, ev, ORBS), "saturn", "jupiter", ORBS)
    tr = next(c for c in cfg if c.kind == "translation")
    assert tr.planets == ["moon", "saturn", "jupiter"] and tr.detail["aspect_to"] == "trine"


def test_collection_of_light():
    # Venus (L1) and Mercury (LQ) do not behold each other; both apply to a heavier Saturn
    # Venus 62 deg behind Saturn closing to a sextile, Mercury 88 deg ahead opening to a square; Venus-Mercury 150 deg: no aspect
    pos = dict(FAR, venus=(43.0, 1.1), mercury=(193.0, 1.3), saturn=(105.0, 0.03), sun=(300.0, 1.0), moon=(330.0, 13.0))
    ch = mk_chart(pos)
    ev = mk_ev([perf("venus", "saturn", 60, 1.9), perf("mercury", "saturn", 90, 1.6)])
    pairs = R.all_pairs(ch, ev, ORBS)
    assert not R.get(pairs, "venus", "mercury").within_orb
    cfg = R.configurations(ch, ev, pairs, "venus", "mercury", ORBS)
    assert any(c.kind == "collection" and c.planets[0] == "saturn" for c in cfg)


def test_void_of_course_by_sign_and_by_orb():
    pos = dict(FAR, moon=(27.0, 13.0))
    ch = mk_chart(pos)
    ev = mk_ev([perf("moon", "mars", 120, 1.0)], ingresses=[E.Ingress("moon", T0 + 0.23, 0, 1, False)])
    mc = R.moon_course(ch, ev, ORBS)
    assert mc["voc_by_sign"] is True                                 # the trine perfects only after the Moon enters Taurus
    ev2 = mk_ev([perf("moon", "mars", 120, 0.1)], ingresses=[E.Ingress("moon", T0 + 0.23, 0, 1, False)])
    assert R.moon_course(ch, ev2, ORBS)["voc_by_sign"] is False


# ------------------------------------------------------------------ dignities (Lilly p.104 / p.115)

def test_p104_cells_spot_checked_against_the_page_image():
    t = D.table()
    assert t[0]["terms"] == [["jupiter", 6], ["venus", 14], ["mercury", 21], ["mars", 26], ["saturn", 30]]
    assert t[2]["terms"] == [["mercury", 7], ["jupiter", 14], ["venus", 21], ["saturn", 25], ["mars", 30]]
    assert t[3]["triplicity"] == {"day": "mars", "night": "mars"}
    assert t[1]["exaltation"] == ["moon", 3] and t[11]["exaltation"] == ["venus", 27]
    assert [f[0] for f in t[0]["faces"]] == ["mars", "sun", "venus"]
    assert t[6]["fall"] == "sun" and t[6]["detriment"] == "mars"


def test_essential_scores_and_peregrine():
    sun_in_aries_day = D.essential("sun", 18.0, True)                # exaltation 4 + triplicity 3 (+ face: Aries 10-20 is the Sun's) 1
    assert set(sun_in_aries_day.has) == {"exaltation", "triplicity", "face"} and sun_in_aries_day.score == 8
    sun_in_aries_night = D.essential("sun", 18.0, False)             # Lilly p.102: by night the Sun gets no triplicity in Aries
    assert "triplicity" not in sun_in_aries_night.has
    sat_aries = D.essential("saturn", 9.7, True)
    assert sat_aries.peregrine and sat_aries.debilities == ["fall"] and sat_aries.score == -9


def test_mutual_reception_by_house():
    ch = mk_chart(dict(FAR, sun=(215.0, 1.0), mars=(135.0, 0.5)))     # Sun in Scorpio, Mars in Leo
    rec = D.reception_between(D.receptions(ch), "sun", "mars")
    assert rec["mutual"] and "house" in rec["a_by_b"] and "house" in rec["b_by_a"] and rec["mutual_major"]


@pytest.mark.parametrize("dist,same,state", [(0.2, True, "cazimi"), (0.3, True, "combust"), (8.4, True, "combust"),
                                             (8.4, False, "under_beams"), (16.9, False, "under_beams"), (17.1, False, "free")])
def test_solar_phase_limits(dist, same, state):
    sun = 15.0 if same else 29.0
    planet = sun + dist if same else sun + dist          # 29 Aries + 8.4 = 7 Taurus: other sign
    ch = mk_chart(dict(FAR, sun=(sun, 1.0), mercury=(planet, 1.4)))
    if same:
        assert int(planet // 30) == int(sun // 30)
    assert D.solar_phase(ch, "mercury")["state"] == state


def test_besieged_needs_both_malefics_in_the_sign_and_nothing_between():
    ch = mk_chart(dict(FAR, saturn=(2.0, 0.05), mars=(9.0, 0.6), venus=(5.0, 1.1)))
    assert D.besieged(ch, "venus")
    ch2 = mk_chart(dict(FAR, saturn=(2.0, 0.05), mars=(9.0, 0.6), venus=(5.0, 1.1), mercury=(4.0, 1.4)))
    assert not D.besieged(ch2, "venus")
    ch3 = mk_chart(dict(FAR, saturn=(28.0, 0.05), mars=(33.0, 0.6), venus=(29.0, 1.1)))
    assert not D.besieged(ch3, "venus")


# ------------------------------------------------------------------ considerations and weighing

def frame(topic="career", sub="obtain_post", party="self"):
    f = Q.Frame("Câu hỏi thử", topic, sub, party, confirmed=True).resolve()
    f["text"] = "Câu hỏi thử"
    return f


def test_considerations_flag_early_late_ascendant_and_saturn():
    ch = mk_chart(dict(FAR, saturn=(1.0, 0.05)), houses={"saturn": 1})
    ch.asc = 28.5
    ch.cusps = [28.5 + 30 * i for i in range(12)]
    ids = {c.id for c in K.check(ch, frame(), {"voc_by_sign": False, "voc_by_orb": False})}
    assert "lilly.consider.asc_late_degrees" in ids and "lilly.consider.saturn_in_ascendant" in ids
    ch.asc, ch.cusps = 1.2, [1.2 + 30 * i for i in range(12)]
    assert "lilly.consider.asc_early_degrees" in {c.id for c in K.check(ch, frame(), {"voc_by_sign": False, "voc_by_orb": False})}


def T(id_, pol, tier, jd=None, **data):
    return J.Testimony(id_, pol, tier, id_, "", jd=jd, data=data)


def test_weighing_first_event_decides_and_lower_tiers_never_overturn():
    cons = []
    assert J._weigh([T("perfection.trine", 1, "decisive", T0 + 3), T("essential.saturn", -1, "moderate")], cons)["label"] == "favourable"
    assert J._weigh([T("perfection.trine", 1, "decisive", T0 + 9), T("prohibition", -1, "decisive", T0 + 2)], cons)["label"] == "unfavourable"
    assert J._weigh([T("separation", -1, "decisive", T0 - 2), T("essential.venus", 1, "moderate")], cons)["label"] == "unfavourable"
    assert J._weigh([T("translation", 1, "decisive", T0 + 1, weak=True)], cons)["label"] == "conditional"
    assert J._weigh([T("essential.venus", 1, "moderate")], cons)["label"] == "unclear"


def test_weighing_lowers_confidence_with_cautions():
    c = [NS(applies=True, severity="strong_caution", id="lilly.consider.asc_late_degrees")]
    assert J._weigh([T("perfection.trine", 1, "decisive", T0 + 3)], c)["confidence"] == "low"


# ------------------------------------------------------------------ classifier

@pytest.mark.parametrize("q,topic,sub,party,house", [
    ("Tôi có được nhận vào công ty ABC sau buổi phỏng vấn không?", "career", "obtain_post", "self", 10),
    ("Em trai tôi có xin được việc không?", "career", "obtain_post", "sibling", 12),
    ("Mẹ tôi có bán được nhà không?", "property", "sell", "mother", 1),
    ("Tôi có tìm lại được chiếc nhẫn bị thất lạc không?", "lost", "lost_item", "self", 2),
    ("Anh ấy có quay lại với tôi không?", "love", "reconcile", "self", 7),
    ("Có mua được căn hộ ở Cầu Giấy không?", "property", "buy", "self", 4),
    ("Tôi có đỗ kỳ thi IELTS không?", "study", "exam", "self", 10),
])
def test_classifier_readings(q, topic, sub, party, house):
    c = Q.classify(q)
    r = c.readings[0]
    assert (r.topic, r.subtype, r.party, r.quesited_house) == (topic, sub, party, house)


@pytest.mark.parametrize("q,kind", [("Mẹ tôi mổ có thành công không?", "health"), ("Tôi có thắng kiện không?", "legal"),
                                    ("Bà tôi sống được bao lâu nữa?", "death"), ("Tôi có mang thai không?", "pregnancy")])
def test_restricted_topics_are_never_judged(q, kind):
    assert kind in {r["kind"] for r in Q.classify(q).restricted}


@pytest.mark.parametrize("q", ["Tôi có đỗ vào Học viện Ngoại giao không?", "Sửa chữa nhà xong có bán được không?",
                               "Anh ấy bỏ tôi rồi, có quay lại không?", "Tôi có mở được cửa hàng không?"])
def test_no_false_restriction_or_kinship(q):
    c = Q.classify(q)
    assert not c.restricted and all(r.party == "self" for r in c.readings)


def test_ambiguous_questions_ask_for_confirmation():
    assert Q.classify("hôm nay thế nào").ambiguous
    assert Q.classify("chuyến đi Nhật tháng sau có suôn sẻ không").ambiguous            # short or long journey?
    assert "should" in Q.classify("Có nên đầu tư vào cổ phiếu này không?").form


def test_derived_house_arithmetic():
    assert Q.derived(7, 10) == 4 and Q.derived(3, 10) == 12 and Q.derived(10, 4) == 1 and Q.derived(1, 2) == 2
