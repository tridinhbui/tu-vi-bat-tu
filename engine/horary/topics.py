"""Topic rules from Lilly's Book II chapters, added to the general judgment as testimonies and answers.

Each function reads the computed facts (pairs, receptions, positions) and returns (testimonies, answers). Answers are the
'where / by whom / how' parts Lilly gives for a topic (place of a lost thing, the buyer's and seller's willingness), each
with its rule id. Nothing here names or describes a person who may have taken something: Lilly describes thieves, Thiên Bàn
does not, because a description drawn from a chart could fall on an innocent person.
"""
from __future__ import annotations

from . import dignity, relations as R
from .astro import TRAD
from .houses import ANGULARITY
from .judgment import ASPECT_VI, Testimony, _vi
from .questions import ruler_of_house

SIGN_VI = ("Bạch Dương", "Kim Ngưu", "Song Tử", "Cự Giải", "Sư Tử", "Xử Nữ", "Thiên Bình", "Bọ Cạp", "Nhân Mã", "Ma Kết", "Bảo Bình", "Song Ngư")
# lilly.land.directions_of_signs (p.204): the quarter each sign signifies
DIRECTION = {0: "đông", 4: "đông lệch bắc", 8: "đông lệch nam", 6: "tây", 2: "tây lệch nam", 10: "tây lệch bắc",
             3: "bắc", 7: "bắc lệch đông", 11: "bắc lệch tây", 9: "nam", 1: "nam lệch đông", 5: "nam lệch tây"}
QUARTER = {0: "đông", 4: "đông", 8: "đông", 6: "tây", 2: "tây", 10: "tây", 3: "bắc", 7: "bắc", 11: "bắc", 9: "nam", 1: "nam", 5: "nam"}
ELEMENT_PLACE = {0: "gần tường, vách ngăn hoặc chỗ có lửa, bếp", 1: "dưới sàn, sát mặt đất", 2: "chỗ cao, phía trên mặt sàn",
                 3: "gần chỗ ẩm, nước, bếp nước"}                     # fire, earth, air, water (lilly.lost.mislaid_place_by_sign)
BENEFICS, MALEFICS = {"jupiter", "venus"}, {"saturn", "mars"}


def _sign(lon: float) -> int:
    return int(lon // 30) % 12


def _applies(pairs, a: str, b: str) -> R.PairState | None:
    """a and b are joined: an application within the moieties that perfects with no station breaking it first."""
    if a == b:
        return None
    st = R.get(pairs, a, b)
    return st if st.motion == "applying" and st.within_orb and st.next_perfection_jd and not st.refranation else None


def _in(chart, p: str, h: int) -> bool:
    return chart.bodies[p].house == h


def _house_planets(chart, h: int) -> list[str]:
    return [p for p in TRAD if chart.bodies[p].house == h]


def _T(id_, pol, tier, vi, why, rule, planets=(), houses=(), **data) -> Testimony:
    return Testimony(f"topic.{id_}", pol, tier, vi, why, list(planets), list(houses), rule=rule, data=data)


# ------------------------------------------------------------------ lost things

def lost(chart, frame, pairs, strength) -> tuple[list[Testimony], dict]:
    T, A = [], {}
    owner = frame["party_house"]
    h2 = frame["quesited_house"]                      # the 2nd from the owner's house (lilly.lost.mislaid_significators)
    L1, L2 = ruler_of_house(chart, 1), ruler_of_house(chart, h2)
    L4, L7, L8 = ruler_of_house(chart, 4), ruler_of_house(chart, 7), ruler_of_house(chart, 8)
    moon = chart.bodies["moon"]
    disp = dignity.table()[_sign(moon.lon)]["house"]

    # recovery by the Moon (Chap. L, p.319-323)
    hits = [x for x in (L1, L2, disp) if x != "moon" and _applies(pairs, "moon", x)]
    if hits:
        T.append(_T("lost.moon_applies", +1, "decisive",
                    "Mặt Trăng đang tiến tới " + ", ".join(_vi(x) for x in dict.fromkeys(hits)) + " (chủ nhà 1, chủ nhà của đồ, hoặc chủ cung Trăng đang đứng)",
                    "Lilly (chương L): Mặt Trăng là sao chỉ đồ mất; Trăng tiến tới chủ nhà 1, chủ nhà 2 hoặc chủ cung của chính nó thì đồ sẽ tìm thấy.",
                    "lilly.lost.moon_significator_recovery", ["moon", *hits]))
    elif moon.house in (1, 2) or moon.house == h2:
        T.append(_T("lost.moon_place", +1, "moderate", f"Mặt Trăng ở nhà {moon.house}",
                    "Lilly: Trăng ở nhà 1 hoặc nhà 2 vẫn cho hy vọng tìm thấy.", "lilly.lost.moon_significator_recovery", ["moon"], [moon.house]))
    else:
        T.append(_T("lost.moon_none", -1, "decisive", "Mặt Trăng không tiến tới chủ nhà 1, chủ nhà của đồ hay chủ cung của nó, cũng không ở nhà 1 hoặc 2",
                    "Lilly (chương L): khi Trăng không tiến tới ai trong số đó, và không ở nhà 1 hay nhà 2, đồ không tìm thấy.",
                    "lilly.lost.moon_significator_recovery", ["moon"]))
    # how much is recovered (p.399)
    if L2 != "moon" and _applies(pairs, "moon", L2):
        dm, d2 = strength["moon"]["essential"], strength[L2]["essential"]
        acc_ok = strength["moon"]["accidental_score"] > 0 and strength[L2]["accidental_score"] > 0
        if dm["has"] and d2["has"]:
            deg, vi = "full", "tìm lại trọn vẹn"
        elif dm["peregrine"] and d2["peregrine"] and not acc_ok:
            deg, vi = "discovery", "biết được đồ ở đâu nhưng khó lấy lại"
        else:
            deg, vi = "partial", "tìm lại được một phần"
        A["recovery_degree"] = {"value": deg, "vi": vi, "rule": "lilly.lost.recovery_degree_of_dignity"}
    # aphorisms (pp.356-359)
    pro, con = [], []
    if _in(chart, L8, 1) or (L8 != L1 and _sign(chart.bodies[L8].lon) == _sign(chart.bodies[L1].lon)):
        pro.append(f"chủ nhà 8 ({_vi(L8)}) ở nhà 1 hoặc cùng cung với chủ nhà 1")
    if _in(chart, L2, 1):
        pro.append(f"chủ nhà của đồ ({_vi(L2)}) ở nhà 1")
    if _in(chart, L1, h2):
        pro.append(f"chủ nhà 1 ({_vi(L1)}) ở nhà của đồ (tìm được sau khi tìm lâu)")
    if _in(chart, L7, 1):
        pro.append(f"chủ nhà 7 ({_vi(L7)}) ở nhà 1")
    if _in(chart, L1, 7):
        pro.append(f"chủ nhà 1 ({_vi(L1)}) ở nhà 7 (tìm được sau khi hỏi han nhiều)")
    if L8 != L2 and _applies(pairs, L8, L2):
        pro.append(f"chủ nhà 8 và chủ nhà của đồ tiến tới nhau")
    if _in(chart, L8, h2):
        pro.append(f"chủ nhà 8 ({_vi(L8)}) ở nhà của đồ")
    if moon.house == h2 and any(_in(chart, b, h2) for b in BENEFICS):
        pro.append("Mặt Trăng ở nhà của đồ cùng một sao cát")
    s, m = chart.bodies["sun"], chart.bodies["moon"]
    if abs(abs((s.lon - m.lon + 180) % 360 - 180) - 120) <= (dignity.orbs()["sun"] + dignity.orbs()["moon"]) / 2:
        pro.append("Mặt Trời và Mặt Trăng tam hợp nhau")
    if s.house == 1 and _sign(s.lon) not in (6, 10):
        pro.append("Mặt Trời ở nhà 1 (không ở Thiên Bình hay Bảo Bình)")
    if "exaltation" in strength[L2]["essential"]["has"]:
        pro.append(f"chủ nhà của đồ ({_vi(L2)}) ở cung vượng")
    for x in ("saturn", "mars"):
        if _in(chart, x, h2):
            con.append(f"{_vi(x)} ở nhà của đồ")
    from .houses import house_of
    if house_of(chart.nodes["south"], chart.cusps)[0] == h2:
        con.append("Kế Đô ở nhà của đồ")
    if _in(chart, L2, 8):
        con.append(f"chủ nhà của đồ ({_vi(L2)}) ở nhà 8")
    if L2 != "sun" and dignity.solar_phase(chart, L2)["state"] == "combust":
        con.append(f"chủ nhà của đồ ({_vi(L2)}) bị đốt")
    if ANGULARITY[chart.bodies[L2].house] == "cadent":
        con.append(f"chủ nhà của đồ ({_vi(L2)}) ở nhà rơi")
    if L8 != L2 and _applies(pairs, L2, L8):
        con.append("chủ nhà của đồ tiến tới chủ nhà 8")
    if s.altitude < 0 and m.altitude < 0:
        con.append("cả hai vầng sáng đều ở dưới đường chân trời")
    if pro or con:
        pol = +1 if len(pro) > len(con) else -1 if len(con) > len(pro) else 0
        T.append(_T("lost.aphorisms", pol, "moderate",
                    f"Các câu cách ngôn của Lilly về tìm lại đồ: {len(pro)} dấu hiệu thuận" + (f" ({'; '.join(pro)})" if pro else "")
                    + f", {len(con)} dấu hiệu nghịch" + (f" ({'; '.join(con)})" if con else ""),
                    "Lilly (tr.356-359) liệt kê các dấu hiệu tìm lại và không tìm lại; Thiên Bàn đếm từng dấu hiệu có mặt.",
                    "lilly.lost.recovery_aphorisms", data_pro=pro, data_con=con))

    # where: inside the house by the house of lord 2; quarter by the majority of eight signs; kind of place by the element
    kind = ANGULARITY[chart.bodies[L2].house]
    h = chart.bodies[L2].house
    where = {1: "chỗ người hỏi hay lui tới hoặc hay cất đồ của mình", 10: "phòng khách, phòng ăn hoặc nơi làm việc, cửa hàng",
             7: "chỗ vợ/chồng hoặc người giúp việc hay ở", 4: "phần cũ nhất hoặc giữa nhà, chỗ người lớn tuổi nhất trong nhà ở"}.get(h)
    A["in_house"] = {"vi": ("Đồ vẫn ở trong nhà" + (f", có lẽ ở {where}" if where else "")) if kind == "angular"
                     else "Chủ nhà của đồ không ở nhà góc: Lilly chỉ nói rõ trường hợp nhà góc (đồ ở trong nhà).",
                     "rule": "lilly.lost.mislaid_significators", "lord": L2, "house": h}
    pts = {"Điểm Mọc": chart.asc, f"chủ nhà 1 ({_vi(L1)})": chart.bodies[L1].lon, "đỉnh nhà 4": chart.cusps[3],
           f"chủ nhà 4 ({_vi(L4)})": chart.bodies[L4].lon, "Mặt Trăng": moon.lon, "đỉnh nhà của đồ": chart.cusps[h2 - 1],
           f"chủ nhà của đồ ({_vi(L2)})": chart.bodies[L2].lon, "Điểm May Mắn": chart.fortune}
    count: dict[str, list[str]] = {}
    for name, lon in pts.items():
        count.setdefault(QUARTER[_sign(lon)], []).append(name)
    best = sorted(count.items(), key=lambda kv: -len(kv[1]))
    tie = len(best) > 1 and len(best[0][1]) == len(best[1][1])
    A["quarter"] = {"value": None if tie else best[0][0], "votes": {k: v for k, v in count.items()},
                    "vi": ("Hướng: các dấu hiệu chia đều, chưa chỉ được một hướng." if tie
                           else f"Hướng: phía {best[0][0]} ({len(best[0][1])}/8 dấu hiệu: {', '.join(best[0][1])})."),
                    "rule": "lilly.lost.mislaid_place_by_sign"}
    strongest = max((L2, "moon"), key=lambda p: strength[p]["essential_score"])
    A["kind_of_place"] = {"vi": f"Loại chỗ: {ELEMENT_PLACE[_sign(chart.bodies[strongest].lon) % 4]} (theo nguyên tố cung của {_vi(strongest)}).",
                          "rule": "lilly.lost.mislaid_place_by_sign", "by": strongest}
    d = abs((moon.lon - chart.bodies[L1].lon + 180) % 360 - 180)
    A["distance"] = {"vi": ("Gần người mất, trong hoặc quanh nhà" if d <= 30 else "Trong khu vực người mất đang sống" if d <= 70
                            else "Ở xa"), "degrees": d, "rule": "lilly.lost.place_and_distance"}
    inside = kind == "angular"
    far = d > 70
    if inside and far:
        A["place_conflict"] = {"vi": "Hai cách của Lilly cho kết quả khác nhau: theo chương đồ để quên (tr.202) chủ nhà của đồ ở nhà góc nên đồ "
                                     "ở trong nhà; theo chương đồ mất (tr.320) Mặt Trăng cách chủ nhà 1 hơn 70° nên đồ ở xa. Hai chương dùng cho "
                                     "hai trường hợp (để quên trong nhà / mất ở ngoài); bạn biết rõ trường hợp nào hơn, nên Thiên Bàn không chọn thay.",
                               "rule": "lilly.lost.place_and_distance"}
    if frame["subtype"] == "stolen":
        A["thief"] = {"vi": "Lilly có quy tắc mô tả kẻ lấy đồ qua hành tinh; Thiên Bàn không dùng, vì một mô tả rút ra từ lá số có thể "
                            "khiến người vô tội bị nghi oan. Nếu bị trộm, hãy báo cơ quan công an.", "rule": "lilly.lost.thief_significator"}
    return T, A


# ------------------------------------------------------------------ property

def property_(chart, frame, pairs, strength) -> tuple[list[Testimony], dict]:
    T, A = [], {}
    L1, L4, L7 = ruler_of_house(chart, 1), ruler_of_house(chart, 4), ruler_of_house(chart, 7)
    if frame["subtype"] in ("buy", "sell") and L1 != L7:
        st = _applies(pairs, L7, L1)
        if st and st.applier == L7:
            T.append(_T("land.seller_willing", +1, "moderate", f"Chủ nhà 7 ({_vi(L7)}, bên bán) tiến tới chủ nhà 1 ({_vi(L1)})",
                        "Lilly: chủ nhà 7 tiến tới chủ nhà 1 bằng góc thân thiện thì người bán sẵn lòng.", "lilly.land.buy_perfection", [L7, L1]))
        st = _applies(pairs, L1, L7)
        if st:
            asp = ASPECT_VI[{0: "conjunction", 60: "sextile", 90: "square", 120: "trine", 180: "opposition"}[st.angle]]
            easy = st.angle in (0, 60, 120)
            T.append(_T("land.bargain", +1 if easy else 0, "moderate",
                        f"Chủ nhà 1 và chủ nhà 7 (người mua và người bán) tiến tới góc {asp}",
                        "Lilly: hội hợp, lục hợp, tam hợp thì hai bên thỏa thuận không mấy vất vả; vuông hoặc xung thì cuối cùng cũng mặc cả "
                        "xong nhưng nhiều lời, dễ đổ vỡ và mất thời gian.", "lilly.land.buy_perfection", [L1, L7]))
    if frame["subtype"] == "buy":
        if _in(chart, L1, 4) or _in(chart, "moon", 4) or _in(chart, L4, 1):
            T.append(_T("land.position", +1, "moderate",
                        "Chủ nhà 1 hoặc Mặt Trăng ở nhà 4, hoặc chủ nhà 4 ở nhà 1",
                        "Lilly: chủ nhà 1 hay Trăng ở nhà 4, hoặc chủ nhà 4 ở nhà 1, thì người hỏi mua được.", "lilly.land.buy_perfection"))
        if L4 != "moon" and _applies(pairs, "moon", L4) and L1 != "moon":
            A["via_broker"] = {"vi": "Mặt Trăng nối nhà 4 với người hỏi: theo Lilly việc mua có thể thành qua người môi giới hoặc người đưa tin.",
                               "rule": "lilly.land.buy_perfection"}
    bad4 = [p for p in _house_planets(chart, 4) if p in MALEFICS and (strength[p]["essential"]["peregrine"] or chart.bodies[p].retrograde)]
    good4 = [p for p in _house_planets(chart, 4) if p in BENEFICS]
    if good4:
        T.append(_T("land.good_fourth", +1, "minor", f"{' và '.join(_vi(p) for p in good4)} ở nhà 4",
                    "Lilly: Mộc tinh, Kim tinh hoặc La Hầu ở nhà 4 thì tài sản tốt, bền lâu, đáng tiền.", "lilly.land.goodness_of_property", good4, [4]))
    if bad4 or chart.bodies[L4].retrograde:
        T.append(_T("land.bad_fourth", -1, "minor",
                    (f"{' và '.join(_vi(p) for p in bad4)} (sao hung, yếu) ở nhà 4" if bad4 else f"Chủ nhà 4 ({_vi(L4)}) nghịch hành"),
                    "Lilly: sao hung yếu ở nhà 4, hoặc chủ nhà 4 nghịch hành, suy, hãm thì tài sản không bền với con cháu.",
                    "lilly.land.goodness_of_property", bad4 or [L4], [4]))
    return T, A


# ------------------------------------------------------------------ money lent

def loan(chart, frame, pairs, strength, recs) -> tuple[list[Testimony], dict]:
    T = []
    L1, L8 = ruler_of_house(chart, 1), ruler_of_house(chart, 8)
    for q in (L1, "moon"):
        if q == L8:
            continue
        st = _applies(pairs, q, L8)
        if st and L8 in MALEFICS:
            received = any(r["planet"] == q and r["by"] == L8 for r in recs)
            T.append(_T("money.malefic_lender", +1 if received else -1, "strong",
                        f"{_vi(q)} tiến tới {_vi(L8)}, chủ nhà 8 là sao hung, " + ("có tiếp nhận" if received else "không tiếp nhận"),
                        "Lilly: sao hung làm chủ nhà 8 mà tiếp nhận chủ nhà 1 hoặc Trăng thì vẫn được; không tiếp nhận thì khó hoặc không bao giờ, "
                        "và vất vả đến mức muốn chưa từng đòi.", "lilly.money.loan_or_debt", [q, L8], [8]))
            break
    return T, {}


# ------------------------------------------------------------------ business

def business(chart, frame, pairs, strength) -> tuple[list[Testimony], dict]:
    T, A = [], {}
    L1, L7 = ruler_of_house(chart, 1), ruler_of_house(chart, 7)
    sub = frame["subtype"]
    if sub == "buy_sell":
        if L7 != "moon" and _applies(pairs, "moon", L7):
            T.append(_T("business.moon_to_seller", +1, "moderate", f"Mặt Trăng tiến tới chủ nhà 7 ({_vi(L7)})",
                        "Lilly: Trăng gặp chủ nhà 7 thì người hỏi mua được, và nhanh.", "lilly.business.buying_selling_commodities", ["moon", L7]))
        if _in(chart, L7, 1):
            A["eager"] = {"vi": "Chủ nhà 7 ở nhà 1: theo Lilly bên kia nài nỉ người hỏi.", "rule": "lilly.business.buying_selling_commodities"}
        elif _in(chart, L1, 7):
            A["eager"] = {"vi": "Chủ nhà 1 ở nhà 7: theo Lilly người hỏi là người muốn mua (bán) hơn.", "rule": "lilly.business.buying_selling_commodities"}
    if sub in ("partnership", "contract"):
        n1, n7 = _qualities(L1), _qualities(L7)
        if n1 and n7:
            agree = bool(n1 & n7 & {"hot", "cold"}) and bool(n1 & n7 & {"dry", "moist"})
            T.append(_T("business.natures", +1 if agree else -1, "moderate",
                        f"{_vi(L1)} và {_vi(L7)} {'cùng' if agree else 'khác'} tính chất (nóng/lạnh, khô/ẩm)",
                        "Lilly (chương LII): chủ nhà 1 và chủ nhà 7 hợp tính chất thì hai bên hòa hợp; không hợp thì thường xuyên cãi vã.",
                        "lilly.business.partnership_whether", [L1, L7]))
        L2, L8 = ruler_of_house(chart, 2), ruler_of_house(chart, 8)
        s2, s8 = strength[L2]["total"], strength[L8]["total"]
        A["who_gains"] = {"vi": ("Bên hỏi có lợi hơn" if s2 > s8 else "Bên kia có lợi hơn" if s8 > s2 else "Hai bên ngang nhau")
                          + f" (chủ nhà 2 {_vi(L2)} {s2:+d}, chủ nhà 8 {_vi(L8)} {s8:+d}).", "rule": "lilly.business.partnership_whether"}
    return T, A


def _qualities(p: str) -> set[str] | None:
    from .considerations import _nature
    return _nature(p)


# ------------------------------------------------------------------ love

def love(chart, frame, pairs, strength) -> tuple[list[Testimony], dict]:
    T, A = [], {}
    L1, L7 = ruler_of_house(chart, 1), ruler_of_house(chart, 7)
    if L1 == L7:
        return T, A
    if _in(chart, L7, 1) or _in(chart, L1, 7):
        A["who_loves_more"] = {
            "vi": "Có hai cách đọc trong Lilly: theo các tác giả xưa (tr.305), "
                  + ("chủ nhà 7 ở nhà 1 thì người kia yêu hơn" if _in(chart, L7, 1) else "chủ nhà 1 ở nhà 7 thì người hỏi yêu hơn")
                  + "; theo kinh nghiệm riêng của Lilly (tr.317), điều ngược lại mới đúng. Thiên Bàn nêu cả hai.",
            "rule": "lilly.love.who_loves_most"}
    if _in(chart, L7, 7) and "house" in strength[L7]["essential"]["has"]:
        T.append(_T("love.free_party", -1, "moderate", f"Chủ nhà 7 ({_vi(L7)}) ở chính nhà 7, trong cung nhà của mình",
                    "Lilly: chủ nhà 7 ở nhà 7, nhất là trong cung nhà của nó, thì người kia không vướng tình, ít nghĩ đến hôn nhân.",
                    "lilly.love.who_loves_most", [L7], [7]))
    st = R.get(pairs, L1, L7)
    if st.within_orb:
        good = st.angle in (60, 120)
        A["agreement"] = {"vi": ("Nếu việc thành, hai chủ tinh tam hợp/lục hợp: theo Lilly hai người hòa thuận." if good else
                                 "Nếu việc thành, hai chủ tinh vuông hoặc xung: theo Lilly dễ có va chạm." if st.angle in (90, 180)
                                 else "Hai chủ tinh hội hợp."), "rule": "lilly.love.agreement_after"}
    return T, A


def reconcile(chart, frame, pairs, strength) -> tuple[list[Testimony], dict]:
    T, A = love(chart, frame, pairs, strength)
    L1, L7 = ruler_of_house(chart, 1), ruler_of_house(chart, 7)
    def to_asc(p):
        d = abs((chart.bodies[p].lon - chart.asc + 180) % 360 - 180)
        for ang in (0, 60, 120):
            if abs(d - ang) <= dignity.orbs()[p] / 2:
                return ang, abs(d - ang)
        return None
    a7, a1 = to_asc(L7), to_asc(L1)
    if a7:
        T.append(_T("love.seventh_beholds_asc", +1, "moderate",
                    f"Chủ nhà 7 ({_vi(L7)}) chiếu tới độ Mọc bằng góc {ASPECT_VI[{0: 'conjunction', 60: 'sextile', 120: 'trine'}[a7[0]]]} (lệch {a7[1]:.1f}°)",
                    "Lilly: chủ nhà 7 chiếu tốt tới điểm Mọc (như chủ nhà 1) thì người vắng mặt sẽ trở lại và được đón nhận.",
                    "lilly.love.reconciliation", [L7], [1, 7]))
    return T, A


# ------------------------------------------------------------------ journeys

def travel(chart, frame, pairs, strength) -> tuple[list[Testimony], dict]:
    T, A = [], {}
    L1 = ruler_of_house(chart, 1)
    if frame["subtype"] == "short_trip":
        L3 = ruler_of_house(chart, 3)
        ok = []
        if L1 != L3 and (L3 in dignity.lords(chart.bodies[L1].lon, chart.is_day).values()):
            ok.append(f"chủ nhà 1 đứng trong phẩm chất của chủ nhà 3 ({_vi(L3)})")
        if _in(chart, L1, 3):
            ok.append("chủ nhà 1 ở nhà 3")
        st = R.get(pairs, L1, L3) if L1 != L3 else None
        if st and st.within_orb and st.angle in (0, 60, 120):
            ok.append(f"chủ nhà 1 và chủ nhà 3 ở góc {ASPECT_VI[{0: 'conjunction', 60: 'sextile', 120: 'trine'}[st.angle]]}")
        if L3 != "moon" and _applies(pairs, "moon", L3):
            ok.append("Mặt Trăng tiến tới chủ nhà 3")
        if _in(chart, "moon", 3):
            ok.append("Mặt Trăng ở nhà 3")
        if ok:
            T.append(_T("journey.short", +1, "moderate", "Dấu hiệu chuyến đi gần: " + "; ".join(ok),
                        "Lilly: một trong các dấu hiệu này (hoặc nhiều) cho thấy người hỏi sẽ đi và đi thuận lợi.", "lilly.journey.short_whether"))
        # Lilly: the strongest in essential dignity of the 3rd-cusp sign, lord 3's sign and the Moon's sign gives the direction;
        # engine reading: the sign holding the strongest of lord 3 and the Moon, the 3rd cusp when neither has dignity
        cand = [(strength[x]["essential_score"], chart.bodies[x].lon) for x in (L3, "moon") if strength[x]["essential"]["has"]]
        lon = max(cand)[1] if cand else chart.cusps[2]
        A["direction"] = {"vi": f"Hướng đi thuận theo Lilly: phía {DIRECTION[_sign(lon)]} (cung {SIGN_VI[_sign(lon)]}).", "rule": "lilly.journey.short_whether"}
    else:
        notes = {1: "lúc khởi đầu", 10: "trên đường đi", 7: "ở nơi đến", 4: "khi trở về"}
        good = [(h, p) for h in (1, 10, 7, 4) for p in _house_planets(chart, h) if p in BENEFICS]
        if good:
            T.append(_T("journey.angles", +1, "moderate",
                        "Sao cát ở nhà góc: " + "; ".join(f"{_vi(p)} ở nhà {h} (thuận {notes[h]})" for h, p in good),
                        "Lilly: sao cát ở nhà 1 thì thuận lúc đầu, ở Thiên Đỉnh thì thuận trên đường, ở nhà 7 thì vừa ý nơi đến, ở nhà 4 thì "
                        "thuận khi về.", "lilly.journey.success_by_angles", [p for _, p in good]))
        from .houses import house_of
        bad = [p for p in _house_planets(chart, 9) if p in MALEFICS]
        if house_of(chart.nodes["south"], chart.cusps)[0] == 9:
            bad.append("south_node")
        if bad:
            T.append(_T("journey.ninth_malefic", -1, "moderate",
                        "Ở nhà 9 có " + ", ".join("Kế Đô" if p == "south_node" else _vi(p) for p in bad),
                        "Lilly: Thổ tinh, Hỏa tinh hoặc Kế Đô ở nhà 9 thì đường đi xấu, có trở ngại.", "lilly.journey.ninth_house_general",
                        [p for p in bad if p != "south_node"], [9]))
        L9 = ruler_of_house(chart, 9)
        q = ("moveable", "fixed", "common")[_sign(chart.bodies[L9].lon) % 3]
        A["length"] = {"vi": {"fixed": f"Chủ nhà 9 ({_vi(L9)}) ở cung cố định: theo Lilly dễ ở lại lâu.",
                              "common": f"Chủ nhà 9 ({_vi(L9)}) ở cung biến đổi: theo Lilly người đi dễ đổi ý, chuyển từ chuyến này sang chuyến khác.",
                              "moveable": f"Chủ nhà 9 ({_vi(L9)}) ở cung khởi đầu: chuyến đi thường nhanh."}[q],
                       "rule": "lilly.journey.length_and_return"}
    return T, A


def apply(chart, frame, pairs, strength, recs) -> tuple[list[Testimony], dict]:
    t = frame["topic"]
    if t == "lost":
        return lost(chart, frame, pairs, strength)
    if t == "property":
        return property_(chart, frame, pairs, strength)
    if t == "finance" and frame["subtype"] == "loan_back":
        return loan(chart, frame, pairs, strength, recs)
    if t == "business":
        return business(chart, frame, pairs, strength)
    if t == "love":
        return reconcile(chart, frame, pairs, strength) if frame["subtype"] == "reconcile" else love(chart, frame, pairs, strength)
    if t == "travel":
        return travel(chart, frame, pairs, strength)
    return [], {}
