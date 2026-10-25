"""Rule-based Vietnamese reading of a judged horary chart. No LLM, no randomness: the same chart gives the same text.

Two modes: `quick` (the conclusion, its main ground, the main condition, the symbolic time, the caution) and `deep` (nine
sections, including how conflicting testimonies were ranked and why). Every paragraph carries `refs`: the testimony ids and
rule ids it rests on, so the page can show the ground of each sentence. Sentences are built from the judgment's facts and
the planets' roles in this question (the querent, the matter, the Moon, a third party), never from a list of stars, and an
explanation of a rule is given once, where it first matters.
"""
from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo

from . import dignity, questions
from .houses import ANGULARITY
from .judgment import ASPECT_VI, houses_ruled

PLANET = {"sun": "Mặt Trời", "moon": "Mặt Trăng", "mercury": "Thủy tinh", "venus": "Kim tinh", "mars": "Hỏa tinh",
          "jupiter": "Mộc tinh", "saturn": "Thổ tinh"}
SIGN = ("Bạch Dương", "Kim Ngưu", "Song Tử", "Cự Giải", "Sư Tử", "Xử Nữ", "Thiên Bình", "Bọ Cạp", "Nhân Mã", "Ma Kết", "Bảo Bình",
        "Song Ngư")
HOUSE_KIND = {"angular": "nhà góc", "succedent": "nhà nối", "cadent": "nhà rơi"}

QUESITED = {
    ("career", "obtain_post"): "công việc hay vị trí bạn đang nhắm tới", ("career", "promotion"): "chức vụ mới",
    ("career", "keep_post"): "công việc hiện tại", ("finance", "gain"): "khoản tiền bạn trông đợi",
    ("finance", "loan_back"): "tiền của người đang giữ khoản nợ", ("finance", "deal"): "khoản lợi từ giao dịch",
    ("business", "partnership"): "người đối tác", ("business", "contract"): "bên kia của thỏa thuận",
    ("business", "buy_sell"): "bên mua bán còn lại", ("business", "rival"): "đối thủ",
    ("love", "relationship"): "người ấy", ("love", "marriage"): "người ấy", ("love", "reconcile"): "người ấy",
    ("study", "exam"): "thành công trong kỳ thi", ("study", "admission"): "nhà trường", ("study", "scholarship"): "học bổng",
    ("property", "buy"): "căn nhà hay mảnh đất", ("property", "sell"): "căn nhà hay mảnh đất", ("property", "rent"): "nơi định thuê",
    ("property", "move"): "nơi ở", ("lost", "lost_item"): "món đồ", ("lost", "stolen"): "món đồ bị lấy",
    ("travel", "short_trip"): "chuyến đi", ("travel", "long_trip"): "chuyến đi", ("travel", "plan_change"): "chuyến đi",
}

VERDICT_LEAD = {
    "favourable": "Theo cách luận của Lilly, lá số nghiêng về việc thành.",
    "conditional": "Theo cách luận của Lilly, việc có đường để thành, nhưng thành có điều kiện.",
    "unfavourable": "Theo cách luận của Lilly, lá số không cho thấy việc thành.",
    "unclear": "Theo cách luận của Lilly, lá số chưa đủ căn cứ để nói việc thành hay không.",
}
CONFIDENCE_VI = {"high": "Lá số không có lời cảnh báo nào về tính hợp lệ.",
                 "medium": "Lá số có lời lưu ý về tính hợp lệ, nên kết luận cần được giữ ở mức vừa phải.",
                 "low": "Lá số có lời cảnh báo mạnh về tính hợp lệ: Lilly khuyên thận trọng khi luận, nên kết luận chỉ có giá trị tham khảo thấp."}

DISCLAIMER = ("Phép tính vị trí các hành tinh ở đây là thiên văn chính xác và kiểm tra được. Còn phán đoán là theo quy tắc của "
              "truyền thống chiêm tinh vấn sự (Lilly, 1647); chưa có bằng chứng khoa học đáng tin cậy rằng phương pháp này dự "
              "báo được sự việc. Hãy xem đây là một cách nhìn để suy ngẫm, không phải lời tiên đoán hay lời khuyên thay cho "
              "thông tin thực tế và người có chuyên môn.")


def _p(text: str, refs=()) -> dict:
    return {"text": text, "refs": list(refs)}


def _when(chart, jd: float | None) -> str:
    if jd is None:
        return ""
    u = dt.datetime(2000, 1, 1, 12, tzinfo=dt.timezone.utc) + dt.timedelta(days=jd - 2451545.0)
    try:
        local = u.astimezone(ZoneInfo(chart.input["tz"])) if not chart.input.get("julian_calendar") else u
    except Exception:  # noqa: BLE001
        local = u
    return local.strftime("%H:%M ngày %d/%m/%Y") + ("" if not chart.input.get("julian_calendar") else " (UT)")


def _deg(lon: float) -> str:
    d = lon % 30
    return f"{int(d)}°{int(round((d % 1) * 60)) % 60:02d}′ {SIGN[int(lon // 30) % 12]}"


def _strength_phrase(st: dict) -> str:
    es = st["essential"]
    parts = []
    for k in es["has"]:
        parts.append({"house": "đang ở nhà riêng của mình", "exaltation": "ở cung vượng (exaltation)",
                      "triplicity": "có phẩm chất tam hợp", "term": "chỉ có phẩm chất nhỏ của giới hạn (term)",
                      "face": "chỉ có phẩm chất nhỏ nhất, diện (face)"}[k])
    if es["peregrine"]:
        parts.append("không có phẩm chất thiết yếu nào (peregrine)")
    for k in es["debilities"]:
        parts.append({"detriment": "lại ở cung hãm (detriment)", "fall": "lại ở cung suy (fall)"}[k])
    return ", ".join(parts)


def _role_line(chart, j, p: str, role: str) -> str:
    b = chart.bodies[p]
    st = j["strength"][p]
    kind = HOUSE_KIND[ANGULARITY[b.house]]
    motion = ""
    if p not in ("sun", "moon"):
        motion = ", đang nghịch hành" if b.retrograde else ""
    sp = dignity.solar_phase(chart, p) if p != "sun" else {"state": "sun"}
    sun = {"combust": ", bị Mặt Trời đốt", "under_beams": ", còn dưới tia nắng Mặt Trời", "cazimi": ", ở tim Mặt Trời"}.get(sp["state"], "")
    return (f"{role} là {PLANET[p]}, ở {_deg(b.lon)}, nhà {b.house} ({kind}){motion}{sun}; {PLANET[p]} "
            f"{_strength_phrase(st)} (điểm thiết yếu {st['essential_score']:+d}, ngẫu nhiên {st['accidental_score']:+d}).")


def _house_people(h: int) -> str:
    from . import kb
    r = kb.rule(f"lilly.house.{h}.meaning")
    if r and r.get("persons_vi"):
        return ", ".join(r["persons_vi"][:3])
    return f"những người và việc của nhà {h}"


LEAN = {   # the deep overview's closing line: same verdict as VERDICT_LEAD, other words (the reading never repeats a sentence)
    "favourable": "Nhìn chung, thế cục nghiêng về phía việc thành.",
    "conditional": "Thế cục mở ra một lối để việc thành, nhưng lối ấy còn vướng.",
    "unfavourable": "Nhìn chung, thế cục nghiêng về phía việc không thành.",
    "unclear": "Thế cục chưa ngả hẳn về bên nào.",
}
VERDICT_HEAD = {"favourable": "Kết luận: thuận.", "conditional": "Kết luận: thuận nhưng có điều kiện.",
                "unfavourable": "Kết luận: không thuận.", "unclear": "Kết luận: chưa rõ."}


def _mechanism(t: dict) -> str:
    """A testimony told as what it does to the matter, in a few words (used in the conclusion instead of repeating it)."""
    d, i = t["data"], t["id"]
    if i.startswith("perfection"):
        return (f"hai chủ tinh sẽ gặp nhau bằng góc {ASPECT_VI[t['aspect']]}" if t["polarity"] > 0
                else f"góc {ASPECT_VI[t['aspect']]} giữa hai chủ tinh " + ("bị cắt ngang trước khi thành" if d.get("blocked") else "không đủ điều kiện Lilly đặt ra"))
    if i == "translation":
        return f"{PLANET[d['translator']]} làm cầu nối giữa hai bên"
    if i == "collection":
        return f"{PLANET[d['collector']]} gom ánh sáng của cả hai bên"
    if i == "reception":
        return "hai chủ tinh tiếp nhận lẫn nhau"
    if i == "separation":
        return "hai chủ tinh đang rời xa nhau sau một lần gặp đã qua"
    if i == "no_connection":
        return "không có đường nào nối hai bên"
    if i == "prohibition":
        return f"{PLANET[t['planets'][0]]} chen vào trước khi hai bên kịp gặp"
    if i == "frustration":
        return f"{PLANET[t['planets'][0]]} đi gặp {PLANET[t['planets'][1]]} trước"
    if i == "refranation":
        return f"{PLANET[d['station']['planet']]} quay lui trước khi hai bên kịp gặp"
    if i == "moon_voc":
        return "Mặt Trăng vô hành"
    if i.startswith("combust"):
        return f"{PLANET[t['planets'][0]]} bị Mặt Trời đốt"
    if i == "same_ruler":
        return "một hành tinh đại diện cho cả hai bên"
    if i == "topic.lost.moon_applies":
        return "Mặt Trăng, sao chỉ đồ mất, đang tiến tới " + _lower_first(t["vi"].split("tiến tới ", 1)[-1].split(" (")[0])
    if i == "topic.lost.moon_none":
        return "Mặt Trăng, sao chỉ đồ mất, không tiến tới chủ tinh nào giúp tìm lại"
    return _lower_first(t["vi"])


def _conditions(t: dict) -> str | None:
    d = t["data"]
    if t["id"] == "translation" and d.get("weak"):
        return f"{PLANET[d['translator']]} không được chủ tinh nó vừa rời tiếp nhận, điều Lilly đòi hỏi ở tr.126 (dù tr.111 không đòi)"
    if d.get("conditions_full") is False:
        return f"góc {ASPECT_VI[t['aspect']]} thiếu điều kiện 'nhà tốt và có phẩm chất' của Lilly"
    if d.get("regret"):
        return "theo Lilly việc thành bằng góc xung thường kèm tranh chấp hoặc hối tiếc"
    return None


def _join(xs: list[str]) -> str:
    xs = [x for x in xs if x]
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " và " + xs[-1] if xs else ""


def compose(chart, frame: dict, j: dict) -> dict:
    sig = j["significators"]
    L1, LQ = sig["querent"]["planet"], sig["quesited"]["planet"]
    qname = QUESITED.get((frame["topic"], frame["subtype"]), "việc được hỏi")
    v = j["verdict"]
    tests = j["testimonies"]
    dec = [t for t in tests if t["tier"] == "decisive"]
    pos = [t for t in dec if t["polarity"] > 0]
    neg = [t for t in dec if t["polarity"] < 0]
    strong = [t for t in tests if t["tier"] == "strong"]
    conds = [c for c in (_conditions(t) for t in pos) if c] + [_mechanism(t) for t in strong if t["polarity"] < 0]
    note126 = ", điều Lilly đòi hỏi ở tr.126 (dù tr.111 không đòi)"
    conds = [c if i == 0 or note126 not in conds[0] else c.replace(note126, "") for i, c in enumerate(conds)]
    ground = _main_ground(chart, j, L1, LQ, qname)

    # ---------------- quick
    quick = [_p(VERDICT_LEAD[v["label"]] + " " + ground, [t["id"] for t in dec])]
    if conds and v["label"] in ("favourable", "conditional"):
        quick.append(_p("Điều kiện đi kèm: " + "; ".join(conds[:2]) + ".", [t["id"] for t in pos + strong]))
    if j["timing"]:
        tm = j["timing"]
        quick.append(_p(f"Về thời gian, thước đo tượng trưng của Lilly cho khoảng {tm['house_rule']['value']} {tm['house_rule']['unit']} "
                        f"(theo vị trí nhà) hoặc {tm['sign_rule']['value']} {tm['sign_rule']['unit']} (theo tính chất cung); "
                        "đây không phải ngày dự báo.", [tm["house_rule"]["rule"], tm["sign_rule"]["rule"]]))
    ans = j.get("answers") or {}
    if frame["topic"] == "lost" and ans:
        keys = ("quarter", "place_conflict", "recovery_degree") if "place_conflict" in ans else ("in_house", "quarter", "distance", "recovery_degree")
        quick.append(_p(" ".join(ans[k]["vi"].rstrip(".") + "." for k in keys if k in ans), [ans[k]["rule"] for k in keys if k in ans]))
    quick.append(_p(CONFIDENCE_VI[v["confidence"]], v["cautions"]))
    if frame.get("caution"):
        quick.append(_p(frame["caution"]))

    # ---------------- deep
    S = []
    inp = chart.input
    place = inp.get("place") or f"{inp['lat']:.4f}, {inp['lon']:.4f}"
    ctx = [_p(f"Câu hỏi: “{frame.get('text', '')}”. Thiên Bàn hiểu đây là câu hỏi về {frame['topic_vi'].lower()} "
              f"({frame['subtype_vi'][:1].lower() + frame['subtype_vi'][1:]}): người hỏi ở nhà 1, {qname} ở nhà {frame['quesited_house']}."
              + (f" {frame['derived_note']}" if frame.get("derived_note") else ""), ["lilly.method.quesited_house"]),
           _p(f"Lá số lập cho lúc câu hỏi được tiếp nhận, {_when(chart, chart.jd_ut)} tại {place}, hệ nhà "
              f"{inp['house_system'].replace('_', ' ').title()}. Điểm Mọc ở {_deg(chart.asc)}, Thiên Đỉnh ở {_deg(chart.mc)}; "
              f"đây là lá số {'ban ngày' if chart.is_day else 'ban đêm'}"
              + (f", giờ hành tinh của {PLANET[chart.planetary_hour['hour_ruler']]} trong ngày của {PLANET[chart.planetary_hour['day_ruler']]}."
                 if chart.planetary_hour.get("available") else "."), ["lilly.consider.time_of_question"])]
    S.append({"id": "context", "title": "Câu hỏi và bối cảnh", "paragraphs": ctx})

    b1, bq = chart.bodies[L1], chart.bodies[LQ]
    ps = j["pairs"].get(f"{L1}-{LQ}") or j["pairs"].get(f"{LQ}-{L1}")
    if L1 == LQ:
        rel = f"Cả bạn lẫn {qname} đều do {PLANET[L1]} đại diện, ở nhà {b1.house}."
    else:
        rel = (f"Bạn được {PLANET[L1]} đại diện, đứng ở nhà {b1.house} ({HOUSE_KIND[ANGULARITY[b1.house]]}); {qname} được "
               f"{PLANET[LQ]} đại diện, ở nhà {bq.house} ({HOUSE_KIND[ANGULARITY[bq.house]]}). ")
        if ps and ps["within_orb"]:
            asp = ASPECT_VI[{0: 'conjunction', 60: 'sextile', 90: 'square', 120: 'trine', 180: 'opposition'}[ps['angle']]]
            rel += (f"Hai hành tinh đang tiến dần về góc {asp}, còn cách {ps['orb']:.1f}°." if ps["motion"] == "applying"
                    else f"Hai hành tinh vừa đi qua góc {asp} và đang rời nhau.")
        else:
            rel += "Giữa hai hành tinh không có góc hợp nào nằm trong orb."
    over = [_p(rel, ["lilly.significator.lord_of_house", "lilly.aspect.application"])]
    mech = [t for t in dec if t["id"] in ("translation", "collection", "reception", "prohibition", "frustration", "refranation")]
    if mech:
        over.append(_p("Điều đáng chú ý nhất trong thế cục: " + _join([_mechanism(t) for t in mech[:3]]) + ". " + LEAN[v["label"]],
                       [t["id"] for t in mech[:3]]))
    else:
        over.append(_p(LEAN[v["label"]], [t["id"] for t in dec]))
    if j["moon_course"]["perfections_in_sign"]:
        nxt = j["moon_course"]["perfections_in_sign"][0]
        other = nxt["b"] if nxt["a"] == "moon" else nxt["a"]
        over.append(_p(f"Mặt Trăng, người đồng hành của bạn trong lá số, sắp tạo góc {ASPECT_VI[nxt['aspect']]} với {PLANET[other]} "
                       f"({_when(chart, nxt['jd'])}); theo Lilly, lần tiếp cận kế tiếp của Trăng cho biết diễn biến kế tiếp.",
                       ["lilly.method.separation_past_application_future"]))
    S.append({"id": "overview", "title": "Tổng quan thế cục", "paragraphs": over})

    sigp = [_p(_role_line(chart, j, L1, "Đại diện cho bạn (chủ nhà 1)"), ["lilly.significator.lord_of_house"])]
    if LQ != L1:
        sigp.append(_p(_role_line(chart, j, LQ, f"Đại diện cho {qname} (chủ nhà {frame['quesited_house']})"),
                       ["lilly.significator.lord_of_house"]))
    else:
        sigp.append(_p(f"Cùng một hành tinh chủ cả nhà 1 và nhà {frame['quesited_house']}: khi đó Lilly xét qua Mặt Trăng và tình trạng "
                       f"của chính {PLANET[L1]}.", ["lilly.significator.lord_of_house"]))
    if "moon" not in (L1, LQ):
        sigp.append(_p(_role_line(chart, j, "moon", "Đồng chủ tinh của bạn"), ["lilly.method.moon_cosignificator"]))
    S.append({"id": "significators", "title": "Chủ tinh đại diện cho các bên", "paragraphs": sigp})

    s1, s2 = j["strength"][L1], j["strength"][LQ]
    comp = []
    if L1 != LQ:
        stronger = L1 if s1["total"] > s2["total"] else LQ if s2["total"] > s1["total"] else None
        comp.append(_p(
            f"Theo bảng điểm sức mạnh của Lilly (tr.115), {PLANET[L1]} được {s1['total']:+d} còn {PLANET[LQ]} được {s2['total']:+d}: "
            + (f"bên {'của bạn' if stronger == L1 else qname} có thế mạnh hơn. " if stronger else "hai bên ngang nhau. ")
            + "Lilly cho điểm nhưng không nói cách cộng gộp, nên con số chỉ để so sánh. Theo cách ông luận, sức mạnh cho biết việc thành "
              "nhanh hay chậm, dễ hay khó, chứ không tự quyết định việc có thành hay không.",
            ["lilly.dignity.fortitude_table", "lilly.perfection.conjunction"]))
    S.append({"id": "strength", "title": "Sức mạnh và vị trí của các hành tinh", "paragraphs": comp})

    inter = [_p(_config_sentence(chart, c, L1, LQ, qname), [c["rule"]]) for c in j["configurations"]["main"]]
    if not inter and ps:
        inter.append(_p(f"Giữa {PLANET[L1]} và {PLANET[LQ]}, góc gần nhất là "
                        f"{ASPECT_VI[{0: 'conjunction', 60: 'sextile', 90: 'square', 120: 'trine', 180: 'opposition'}[ps['angle']]]}, lệch "
                        f"{ps['orb']:.2f}° trong khi orb cho phép là {ps['moiety_sum']:.2f}°; hai hành tinh đang "
                        f"{'tiến tới' if ps['motion'] == 'applying' else 'tách ra'}.", ["lilly.aspect.application", "lilly.orbs.moiety_rule"]))
    S.append({"id": "aspects", "title": "Các góc hợp và tương tác quan trọng", "paragraphs": inter})

    bal = []
    if pos:
        bal.append(_p("Điểm tựa của việc: " + _join([_mechanism(t) for t in pos]) + ".", [t["id"] for t in pos]))
    if neg:
        bal.append(_p("Điều chặn đường: " + _join([_mechanism(t) for t in neg]) + ".", [t["id"] for t in neg]))
    if strong:
        bal.append(_p("Ở tầng điều kiện: " + "; ".join(_lower_first(t["vi"]) for t in strong) + ".", [t["id"] for t in strong]))
    bal += _conflicts(j)
    S.append({"id": "balance", "title": "Yếu tố thuận lợi, trở ngại và mâu thuẫn", "paragraphs": bal})

    S.append({"id": "course", "title": "Diễn biến theo cách luận truyền thống", "paragraphs": _course(chart, j, L1, LQ, qname)})

    head = VERDICT_HEAD[v["label"]]
    if v["label"] in ("favourable", "conditional"):
        first = min((t for t in pos if t.get("jd")), key=lambda t: t["jd"], default=pos[0] if pos else None)
        why = f" Lý do chính: {_mechanism(first)}" if first else ""
        why += (", và không có hành tinh nào chen ngang trước lúc ấy." if v["label"] == "favourable" else
                f"; điều giữ kết luận ở mức có điều kiện là {_join(conds[:2])}." if conds else ".")
    elif v["label"] == "unfavourable":
        why = " Lý do chính: " + _join([_mechanism(t) for t in neg[:2]]) + "." if neg else ""
        if pos:
            why += " Có lối thành sự, nhưng điều chặn đường đến trước."
    else:
        why = " Không có chứng cứ quyết định ở bên nào; Lilly khuyên hoãn luận khi chứng cứ cân bằng."
    concl = [_p(head + why, [t["id"] for t in dec])]
    ans = j.get("answers") or {}
    if ans:
        concl.append(_p("Những điều Lilly nói riêng cho loại câu hỏi này: " + " ".join(a["vi"].rstrip(".") + "." for a in ans.values()),
                        [a["rule"] for a in ans.values()]))
    if j["timing"]:
        tm = j["timing"]
        concl.append(_p(tm["house_rule"]["vi"] + " " + tm["sign_rule"]["vi"] + " " + tm["caveat"]
                        + f" (Góc hợp chính xác về thiên văn: {_when(chart, tm['ephemeris']['jd'])}.)",
                        [tm["house_rule"]["rule"], tm["sign_rule"]["rule"], "lilly.method.mix_art_and_reason"]))
    S.append({"id": "conclusion", "title": "Kết luận có điều kiện và căn cứ", "paragraphs": concl})

    care = [_p(f"{c['vi']}. {c['effect_vi']}", [c["id"]]) for c in j["considerations"] if c["applies"]]
    care.append(_p(CONFIDENCE_VI[v["confidence"]], v["cautions"]))
    if frame.get("caution"):
        care.append(_p(frame["caution"]))
    if frame["topic"] == "study":
        care.append(_p("Lilly không có chương riêng về thi cử, nhập học hay học bổng; nhà được dùng ở đây là cách vận dụng nghĩa các nhà "
                       "của ông, không phải quy tắc có sẵn trong sách.", ["lilly.study.none"]))
    care.append(_p(DISCLAIMER))
    S.append({"id": "care", "title": "Những điểm cần thận trọng", "paragraphs": care})

    return {"quick": {"title": v["vi"], "paragraphs": quick + [_p(DISCLAIMER)]}, "deep": {"title": v["vi"], "sections": S}}


def _lower_first(s: str) -> str:
    return s[:1].lower() + s[1:] if s and not s[:2].isupper() and not s.startswith(tuple(PLANET.values())) else s


def _main_ground(chart, j, L1, LQ, qname) -> str:
    dec = [t for t in j["testimonies"] if t["tier"] == "decisive"]
    ids = {t["id"] for t in dec}
    who = f"{PLANET[L1]} (đại diện cho bạn) và {PLANET[LQ]} (đại diện cho {qname})"
    first = next((t for t in dec if t["polarity"] > 0), None)
    block = next((t for t in dec if t["polarity"] < 0), None)
    lm = next((t for t in dec if t["id"] in ("topic.lost.moon_applies", "topic.lost.moon_none")), None)
    if lm:
        return _mechanism(lm)[:1].upper() + _mechanism(lm)[1:] + "; theo chương đồ mất của Lilly, đây là phép thử chính." + (
            " Bên cạnh đó, " + _lower_first(_mechanism(first)) + "." if first and first is not lm and first["polarity"] > 0 else "")
    if "same_ruler" in ids:
        return f"Một hành tinh duy nhất, {PLANET[L1]}, đại diện cho cả bạn lẫn {qname}, nên chính tình trạng của nó và Mặt Trăng quyết định."
    if first and first["id"] == "translation":
        t = first["data"]["translator"]
        hs = first["data"]["translator_rules_houses"]
        return (f"{who} không tự nối với nhau, nhưng {PLANET[t]} chuyển ánh sáng từ bên này sang bên kia: việc có thể thành nhờ "
                f"một người trung gian, theo Lilly là người thuộc nhà {', '.join(map(str, hs)) or '?'} "
                f"({'; '.join(_house_people(h) for h in hs[:2])}).")
    if first and first["id"] == "collection":
        c = first["data"]["collector"]
        return (f"{who} không nhìn nhau, nhưng cả hai cùng hướng về {PLANET[c]}, hành tinh nặng hơn; theo Lilly đó là một người có "
                f"liên quan tới cả hai bên đứng ra kết thúc việc.")
    if first and first["id"].startswith("perfection"):
        asp = first["aspect"]
        return f"{who} đang tiến tới góc {ASPECT_VI[asp]}{' và điều kiện Lilly đặt cho góc này đã đạt' if first['data'].get('conditions_met', True) else ''}."
    if block:
        if block["id"] == "separation":
            return f"{who} đang rời xa nhau sau một góc hợp đã qua: theo Lilly, sự tách rời là dấu hiệu mất, ít hy vọng việc thành."
        if block["id"] == "no_connection":
            return f"{who} không tạo góc hợp nào trong orb và không có hành tinh nào làm cầu nối giữa hai bên."
        if block["id"] == "refranation":
            return f"{who} đang tiến tới nhau nhưng một bên quay lui trước khi kịp gặp (refranation)."
        if block["id"].startswith("perfection"):
            return f"{who} có tiến tới nhau, nhưng {_lower_first(block['vi'])}."
        return _lower_first(block["vi"]) + "."
    return ""


def _config_sentence(chart, c, L1, LQ, qname) -> str:
    k = c["kind"]
    when = _when(chart, c.get("jd"))
    if k == "perfection":
        a, b = c["planets"]
        d = c["detail"]
        tail = "" if d.get("before_sign_change", True) else " — dù góc hợp chỉ chính xác sau khi một trong hai đổi cung"
        return (f"{PLANET[a]} tiến tới góc {ASPECT_VI[d['aspect']]} với {PLANET[b]}, còn {d['orb']:.2f}°, chính xác lúc {when}{tail}.")
    if k == "translation":
        t, frm, to = c["planets"]
        return (f"{PLANET[t]} đã rời {PLANET[frm]} và sẽ tới {PLANET[to]} lúc {when}, mang ánh sáng của bên này sang bên kia "
                f"(chuyển ánh sáng, translation of light).")
    if k == "collection":
        col, a, b = c["planets"]
        return f"Cả {PLANET[a]} và {PLANET[b]} cùng tiến tới {PLANET[col]}; góc cuối cùng chính xác lúc {when} (thu ánh sáng, collection of light)."
    if k == "prohibition":
        x, met, other = c["planets"]
        return (f"Trước khi hai chủ tinh gặp nhau, {PLANET[x]} {'hội hợp' if c['detail'].get('by_body') else 'chiếu tới'} {PLANET[met]} "
                f"trước, lúc {when}: sự gặp gỡ với {PLANET[other]} bị chen ngang (prohibition).")
    if k == "frustration":
        to, x, frm = c["planets"]
        return f"{PLANET[to]} kết hợp với {PLANET[x]} lúc {when}, trước khi {PLANET[frm]} kịp tới: việc bị phá giữa chừng (frustration)."
    if k == "refranation":
        st = c["detail"]["station"]
        return (f"{PLANET[st['planet']]} đứng lại rồi đổi chiều lúc {_when(chart, st['jd'])}, trước khi góc hợp giữa hai chủ tinh "
                f"thành (refranation).")
    return ""


def _conflicts(j) -> list[dict]:
    """Where testimonies point different ways: say which outranks which and why (deep mode)."""
    T = j["testimonies"]
    out = []
    dec_pos = [t for t in T if t["tier"] == "decisive" and t["polarity"] > 0]
    dec_neg = [t for t in T if t["tier"] == "decisive" and t["polarity"] < 0]
    low_pos = [t for t in T if t["tier"] in ("moderate", "minor") and t["polarity"] > 0]
    low_neg = [t for t in T if t["tier"] in ("moderate", "minor") and t["polarity"] < 0]
    if dec_pos and dec_neg:
        a = min((t for t in dec_pos if t.get("jd")), key=lambda t: t["jd"], default=None)
        b = min((t for t in dec_neg if t.get("jd")), key=lambda t: t["jd"], default=None)
        if a and b:
            first, second = (a, b) if a["jd"] < b["jd"] else (b, a)
            out.append(_p(f"Ở tầng quyết định có cả dấu hiệu thành lẫn dấu hiệu cản. Thiên Bàn xét theo thứ tự thời gian thiên văn: "
                          f"điều xảy ra trước là “{_lower_first(first['vi'])}”, nên nó định hướng kết luận; điều kia đến sau.",
                          [first["id"], second["id"]]))
    if dec_pos and low_neg:
        out.append(_p("Một số yếu tố yếu (như " + ", ".join(_lower_first(t["vi"]) for t in low_neg[:2]) + ") đi ngược với cách thành sự. "
                      "Theo Lilly, việc có thành hay không do sự tiếp cận của các chủ tinh quyết định; phẩm chất và vị trí nhà cho biết "
                      "thành nhanh hay chậm, dễ hay khó, nên chúng làm giảm chất lượng chứ không đảo kết luận.",
                      [t["id"] for t in low_neg[:2]] + ["lilly.method.what_to_judge", "lilly.perfection.conjunction"]))
    if dec_neg and low_pos:
        out.append(_p("Ngược lại, có những điểm sáng (như " + ", ".join(_lower_first(t["vi"]) for t in low_pos[:2]) + "), nhưng chúng "
                      "không tạo ra cách thành sự: một hành tinh mạnh mà không nối được với bên kia thì vẫn không đưa việc tới kết quả.",
                      [t["id"] for t in low_pos[:2]] + ["lilly.method.application_separation"]))
    if not out:
        out.append(_p("Các chứng cứ chính không mâu thuẫn nhau đáng kể."))
    return out


def _course(chart, j, L1, LQ, qname) -> list[dict]:
    mc = j["moon_course"]
    out = []
    if mc["last_separation"]:
        ls = mc["last_separation"]
        other = ls["b"] if ls["a"] == "moon" else ls["a"]
        hs = houses_ruled(chart, other)
        out.append(_p(f"Trước lúc hỏi, Mặt Trăng vừa rời góc {ASPECT_VI[ls['aspect']]} với {PLANET[other]} ({_when(chart, ls['jd'])}). "
                      f"Theo Lilly, lần tách gần nhất cho biết điều đã xảy ra trước câu hỏi, mang tính chất của nhà mà {PLANET[other]} "
                      f"cai quản (nhà {', '.join(map(str, hs))}).", ["lilly.method.separation_past_application_future"]))
    role = {L1: f"{PLANET[L1]} (bạn)", LQ: f"{PLANET[LQ]} ({qname})"}
    if L1 == LQ:
        role = {L1: f"{PLANET[L1]} (cả hai bên)"}
    steps = []
    for ev in j["timeline"]:
        if ev["jd"] <= chart.jd_ut or len(steps) >= 5:
            continue
        day = _when(chart, ev["jd"]).split(" ngày ")[-1]
        if ev["kind"] == "perfection" and {ev["a"], ev["b"]} & {L1, LQ} and "moon" not in (ev["a"], ev["b"]):
            steps.append(f"ngày {day}, {role.get(ev['a'], PLANET[ev['a']])} tạo góc {ASPECT_VI[ev['aspect']]} với {role.get(ev['b'], PLANET[ev['b']])}")
        elif ev["kind"] == "station" and ev["planet"] in (L1, LQ):
            steps.append(f"ngày {day}, {role[ev['planet']]} đứng lại rồi chuyển {'nghịch' if ev['turns'] == 'retrograde' else 'thuận'} hành")
        elif ev["kind"] == "ingress" and ev["planet"] in (L1, LQ):
            steps.append(f"ngày {day}, {role[ev['planet']]} sang cung {SIGN[ev['sign_to']]}")
    if steps:
        out.append(_p("Theo dòng thời gian thiên văn sau lúc hỏi: " + "; ".join(steps) + ". Đây là các sự kiện của bầu trời, giúp thấy thứ "
                      "tự các bước trong cách luận, không phải lịch hẹn của sự việc.", ["lilly.aspect.application", "lilly.motion.stationary"]))
    if mc["voc_by_sign"]:
        out.append(_p(f"Mặt Trăng không tạo thêm góc hợp chính xác nào trước khi rời cung lúc {_when(chart, mc['sign_exit_jd'])} "
                      "(vô hành). Lilly coi đó là dấu hiệu việc khó tiến triển.", ["lilly.consider.moon_void_of_course"]))
    elif mc["perfections_in_sign"]:
        seq = ", rồi ".join(f"góc {ASPECT_VI[p['aspect']]} với {PLANET[p['b'] if p['a'] == 'moon' else p['a']]}" for p in mc["perfections_in_sign"])
        out.append(_p(f"Trong phần còn lại của cung hiện tại, Mặt Trăng lần lượt tạo {seq}, rồi rời cung lúc {_when(chart, mc['sign_exit_jd'])}.",
                      ["lilly.method.separation_past_application_future"]))
    return out
