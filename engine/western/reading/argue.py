"""The 'Tóm tắt' paragraph that opens each life chapter: a thesis, why, what pulls the other way, a conclusion for this chart,
how it may show, and how far it depends on the birth time.

Nothing new is asserted here. Every claim below is the result of a rule the chapter's own paragraphs already apply (same Facts
methods, same thresholds), restated for a reader who has never studied astrology. What is Thiên Bàn's own is the weighing, and it
is written down in the paragraph's steps (Đọc sâu):

  weight 3  a testimony the book itself counts as several (Lilly p.616: a royal star on a significator = three testimonies)
  weight 2  the main significator of the chapter's own rule (Lilly's significator of manners, Ptolemy's ruler of the soul,
            the lord of action, the ruler of the Lot, the lord of the 7th...)
  weight 1  a supporting or modifying testimony (a planet in the house, the state of a general significator, a sign type)

  thesis      the topic (usually a planet) with the largest total weight; ties go to the earlier rule in the chapter
  verdict     'thuận' / 'nghịch' when one side weighs more than twice the other, 'hai mặt' when both sides are present and
              closer than that, 'nhẹ' when the chapter has little either way
  agreement   said only when two or more schools reach the same topic by their own methods

The paragraph is school 'compare' and says it is a summary (tong_hop); it cites the sources of the claims it gathers.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .. import dignity, kb
from ..zodiac import SIGNS, sign_index, deg_in_sign
from .compose import Para, cap, ev_in, ev_planet, ev_point, listing, pick, planet_list, srcs
from .facts import BENEFICS, CLASSICAL, MALEFICS, Facts
from .vocab import ASPECT_NOUN, P, S, TEMPERAMENT_VI

M = kb.load("meanings")
SCHOOL_NAME = {"traditional": "Lilly", "hellenistic": "Ptolemy và Valens", "ptolemy": "Ptolemy", "valens": "Valens", "modern": "Alan Leo"}
STATE = {"well": "mạnh", "ill": "yếu", "mixed": "ở mức vừa"}


@dataclass
class Claim:
    key: str                         # the topic it speaks about ("planet:mercury", "field", "temperament"...)
    about: str                       # that topic in words for the reader
    pol: int                         # +1 helps, -1 hinders, 0 describes
    w: int                           # 1-3, see the module docstring
    why: str                         # the reason in plain words, a clause with its own subject
    author: str                      # Lilly / Ptolemy / Valens / Alan Leo
    src: str
    show: list[str] = field(default_factory=list)       # how it may show, in the book's own words
    ev: list[dict] = field(default_factory=list)
    timed: list[tuple[str, str]] = field(default_factory=list)   # (school, point) or ("cusp", n) whose house the claim rests on
    pick: bool = False               # the method itself chose this planet (only picks count as schools agreeing)
    warn: list[str] = field(default_factory=list)       # the book's traits of the weak planet, said as 'cần coi chừng', never as a portrait


# --------------------------------------------------------------------------------------------- plain-language glosses
GLOSS = {
    "đắc thế": "đắc thế, tức được cung đang đứng nâng sức",
    "thất thế": "thất thế, tức cung đang đứng làm nó yếu đi",
    "lạc chỗ": "lạc chỗ, tức không có phẩm vị nào ở độ đang đứng; bảng điểm của Lilly trừ cho trường hợp này ngang với một cung tổn hại",
    "nhà góc": "nhà góc (Nhà 1, 4, 7, 10, nơi một hành tinh tác động mạnh nhất)",
    "nhà suy": "nhà suy (Nhà 3, 6, 9, 12, nơi hành tinh khó phát huy)",
    "bị Mặt Trời đốt": "bị Mặt Trời đốt, tức đứng quá gần Mặt Trời nên khó tự thể hiện",
    "nghịch hành": "nghịch hành, tức nhìn từ Trái Đất thì sao như đang đi lùi",
    "góc hài hòa": "góc hài hòa (tam hợp 120° hoặc lục hợp 60°, kiểu nâng đỡ nhau)",
    "góc căng": "góc căng (vuông 90° hoặc đối 180°, kiểu va chạm, thúc ép)",
    "cát tinh": "cát tinh (Sao Mộc, Sao Kim: sao mang điều thuận)",
    "hung tinh": "hung tinh (Sao Thổ, Sao Hỏa: sao mang sức cản)",
}
# What each planet stands for, in a few words a newcomer can hold on to (Valens I.1, Lilly pp.57-81).
SIG_SHORT = {"sun": "sao của uy quyền và danh dự", "moon": "sao của đời sống cảm xúc và thân thể", "mercury": "sao của trí óc và chữ nghĩa",
             "venus": "sao của niềm vui và tình cảm", "mars": "sao của sức mạnh và tranh đua", "jupiter": "sao của sự rộng lượng và công bằng",
             "saturn": "sao của sự kín đáo và nghiêm khắc"}


def gloss(f: Facts, term: str) -> str:
    seen = f.__dict__.setdefault("_gloss", set())
    if term in seen or term not in GLOSS:
        return term
    seen.add(term)
    return GLOSS[term]


def _short(items: list[str], n: int) -> list[str]:
    """The first n traits, without the books' framing lines ('vẫn cùng một bản chất nhưng mờ nhạt' is a remark, not a trait)."""
    return [x.split(";")[0].strip() for x in items if not x.startswith("vẫn ")][:n]


def _nature(p: str) -> str:
    return SIG_SHORT.get(p, "")


def _state_words(f: Facts, p: str) -> str:
    st = f.lilly_state(p)
    if st == "ill" and not f.lilly_essential(p)["debilities"]:
        # Lilly's table gives a planet with no dignity at its degree -5, as much as a detriment: weak, but for another reason
        return f"đang {gloss(f, 'lạc chỗ')}"
    return f"đang {gloss(f, 'đắc thế')}" if st == "well" else f"đang {gloss(f, 'thất thế')}" if st == "ill" else "có sức ở mức vừa"


def _once(f: Facts, key: str) -> bool:
    """True the first time `key` is asked in this reading: long explanations are given once, later chapters refer to them."""
    seen = f.__dict__.setdefault("_said", set())
    if key in seen:
        return False
    seen.add(key)
    return True


# --------------------------------------------------------------------------------------------- composing the summary
def _margin(f: Facts, s: str, p: str) -> float | None:
    if p == "asc_sign":
        return min(deg_in_sign(f.lon["asc"]), 30 - deg_in_sign(f.lon["asc"]))
    if s == "cusp" and f.regio:
        c = f.regio[int(p) - 1]
        return min(deg_in_sign(c), 30 - deg_in_sign(c))
    return f.cusp_margin(s, p)


def _time_note(f: Facts, cid: str, used: list[Claim]) -> str:
    if not f.time_known:
        return ""
    pts = [(s, p) for c in used for s, p in c.timed]
    if not pts:
        names = [P(n) for n in dict.fromkeys(e["id"] for c in used for e in c.ev if e["kind"] == "planet")][:3]
        return f" Kết luận này chỉ dựa vào cung và góc chiếu của {listing(names)}, nên không đổi dù giờ sinh lệch vài chục phút." if names and _once(f, "time:sign") else ""
    m, s, p = min(((_margin(f, s, p), s, p) for s, p in pts if _margin(f, s, p) is not None), default=(None, None, None))
    if m is None:
        return ""
    minutes = max(1, round(m * 4))
    who = "cung Mọc" if p == "asc_sign" else f"đỉnh Nhà {p}" if s == "cusp" else P(p)
    if not _once(f, "time:explained"):
        # explained in full in the first summary; later ones name a point only once
        return f" Độ nhạy với giờ sinh: {who}, khoảng {minutes} phút." if _once(f, f"time:{who}:{minutes}") else ""
    _once(f, f"time:{who}:{minutes}")
    if minutes <= 20:
        return (f" Cần biết: nếu giờ sinh sai quá khoảng {minutes} phút, vị trí nhà của {who} có thể đổi (các nhà xoay chừng 1° mỗi 4 phút) "
                f"và phần dựa vào nhà cần đọc lại." + (" Như vậy phần này chỉ đúng khi giờ sinh thật chính xác." if minutes <= 3 else "")
                + " Các chương sau chỉ ghi gọn độ nhạy này.")
    return (f" Phần dựa vào nhà đứng vững nếu giờ sinh sai dưới khoảng {minutes} phút (chỗ nhạy nhất là {who}; các nhà xoay chừng 1° mỗi 4 phút). "
            f"Các chương sau chỉ ghi gọn độ nhạy này.")


def _reasons(f: Facts, cid: str, whys: list[str]) -> str:
    if not whys:
        return ""
    if len(whys) == 1:
        return " " + pick(f"{cid}.why1", ["Lý do chính: ", "Điều đó đến từ chỗ ", "Căn nguyên ở chỗ "]).replace("Căn nguyên ở chỗ ", "Gốc của nó là ") + whys[0] + "."
    num = {2: "hai", 3: "ba"}[len(whys)]
    lead = pick(f"{cid}.whyn", [f"Có {num} lý do: ", f"Lá số cho thấy điều đó qua {num} điểm: ", f"{cap(num)} điều dẫn tới kết luận này: "])
    return " " + lead + "; ".join(f"({i}) {w}" for i, w in enumerate(whys, 1)) + "."


CONCL = {   # chapter -> verdict -> what the balance means in practice (the thesis already said what it is)
    "tinh_cach": {"thuận": "Nói cách khác, những nét ấy thường tự hiện ra mà không cần gắng", "nghịch": "Nói cách khác, những nét tốt có thật nhưng cần được rèn mới hiện ra trọn",
                  "hai mặt": "Nói cách khác, mặt sáng và mặt cần để ý cùng có mặt; mặt nào trội lên tùy hoàn cảnh", "nhẹ": "Đây là nét nền hơn là điểm nhấn"},
    "tu_duy": {"thuận": "Trong thực tế, việc học có nền vững để đi xa", "nghịch": "Trong thực tế, muốn học sâu thì phương pháp và nhẫn nại quan trọng hơn sự nhanh nhạy",
               "hai mặt": "Trong thực tế, biết chỗ nào sắc, chỗ nào vướng giúp chọn cách học", "nhẹ": "Lá số không có dấu hiệu mạnh về cách học, theo chiều nào"},
    "cam_xuc": {"thuận": "Trong thực tế, cảm xúc có nơi neo đậu, ít khi bị cuốn đi", "nghịch": "Trong thực tế, nề nếp và những chỗ dựa quen thuộc giúp nhiều hơn là cố gồng",
                "hai mặt": "Trong thực tế, có chỗ dựa nhưng cũng có lúc chao; nhận ra lúc nào là lúc nào là bước đầu", "nhẹ": "Đời sống cảm xúc khá êm, ít biến động lớn"},
    "su_nghiep": {"thuận": "Trong thực tế, đường nghề có nhiều chỗ được nâng đỡ", "nghịch": "Trong thực tế, chỗ đứng trong nghề thường phải tự tạo hơn là chờ được nâng",
                  "hai mặt": "Trong thực tế, có điểm tựa thật nhưng cũng có chỗ vướng nên tính trước", "nhẹ": "Danh vọng (đọc qua Mặt Trời và chủ Thiên Đỉnh) không phải điểm nhấn của lá số này; điều nó nói rõ nhất là loại việc hợp với bạn"},
    "tai_chinh": {"thuận": "Trong thực tế, tiền đến và ở lại khá thuận", "nghịch": "Trong thực tế, giữ được tiền nhờ kỷ luật và kế hoạch hơn là nhờ vận",
                  "hai mặt": "Trong thực tế, có điểm tựa để kiếm tiền nhưng cũng có chỗ hở khi giữ tiền", "nhẹ": "Chuyện tiền bạc không nghiêng hẳn về phía nào"},
    "quan_he": {"thuận": "Trong thực tế, đây là nền tốt để vun đắp", "nghịch": "Trong thực tế, quan hệ lâu dài cần nói ra và vun đắp nhiều hơn mức trung bình",
                "hai mặt": "Trong thực tế, có điểm tựa nhưng cũng có chỗ dễ vấp, nên nói ra sớm", "nhẹ": "Chuyện gắn bó lâu dài không có dấu hiệu mạnh theo chiều nào"},
    "gia_dinh": {"thuận": "Đây là nguồn lực bạn có thể dựa vào khi cần", "nghịch": "Vì vậy chỗ dựa của bạn phần nhiều là do tự gây dựng",
                 "hai mặt": "Gia đình vừa là nguồn lực vừa có phần nặng", "nhẹ": "Gia đình gốc không phải điểm nhấn của lá số"},
    "dinh_huong": {"thuận": "Trong thực tế, điều bạn muốn và điều đời mang tới dễ đi cùng một hướng", "nghịch": "Trong thực tế, hướng đi nên được chọn có ý thức, vì điều mình muốn và điều đời mang tới dễ tách nhau",
                   "hai mặt": "Trong thực tế, hướng đi có sức dẫn, nhưng điều mình muốn và điều đời mang tới chưa chắc trùng nhau", "nhẹ": "Hướng đi không bị kéo mạnh về phía nào"},
}


def _lord_years(f: Facts, p: str, n: int = 2) -> list[int]:
    """The next ages (from the reading date's age) at which planet p is lord of the profected year (whole-sign profection)."""
    if not f.time_known or "age_now" not in f.__dict__:
        return []
    a0 = f.__dict__["age_now"]
    if a0 > 90:
        return []
    asc_i = sign_index(f.lon["asc"])
    return [a for a in range(a0, a0 + 13) if dignity.domicile_lord(SIGNS[(asc_i + a) % 12]) == p][:n]


def summarize(f: Facts, cid: str, heading: str, claims: list[Claim], thesis, tilt: str = "") -> Para | None:
    claims = [c for c in claims if c]
    if not claims:
        return None
    weight: dict[str, int] = {}
    for c in claims:
        weight[c.key] = weight.get(c.key, 0) + c.w
    order = [c.key for c in claims]
    top_key = max(weight, key=lambda k: (weight[k], -order.index(k)))
    top = [c for c in claims if c.key == top_key]
    pos = sum(c.w for c in claims if c.pol > 0)
    neg = sum(c.w for c in claims if c.pol < 0)
    verdict = ("nhẹ" if pos + neg <= 1 else "thuận" if pos >= 2 * neg else "nghịch" if neg >= 2 * pos else "hai mặt")
    side = 1 if pos >= neg else -1
    text = thesis(top_key, top, claims, verdict).strip()
    ranked = sorted(claims, key=lambda c: (-c.w, claims.index(c)))
    support = [c for c in top if c.pol == side] + [c for c in ranked if c not in top and c.pol == side]
    if not support:            # a descriptive claim is given as a reason only when nothing argues either way
        support += ([c for c in top if c.pol == 0 and c.show] or [c for c in top if c.pol == 0])[:2]
    contra = [c for c in ranked if c.pol == -side]
    text += _reasons(f, cid, [c.why for c in support[:3]])
    by_planet: dict[str, set] = {}
    for c in claims:
        pl = next((e["id"] for e in c.ev if e["kind"] == "planet"), None)
        if c.pick and pl:
            by_planet.setdefault(pl, set()).add(c.author)
    agree = next(((pl, sorted(a)) for pl, a in by_planet.items() if len(a) >= 2), None)
    if agree:
        pl, who = agree
        text += (f" {listing(who)} đi theo những phép khác nhau mà cùng chọn {P(pl)}, nên điều này đáng tin hơn một chứng lẻ." if _once(f, "agree")
                 else f" Cả {listing(who)}, mỗi người theo phép riêng, đều chọn {P(pl)}.")
    if contra:
        text += " " + pick(f"{cid}.contra", ["Kéo về phía ngược lại: ", "Chiều ngược lại: ", "Điều làm cán cân bớt nghiêng: "]) + "; ".join(c.why for c in contra[:2]) + "."
    concl = CONCL[cid][verdict]
    if pos or neg:
        concl += f" (dấu hiệu ủng hộ nặng {pos}, dấu hiệu ngược lại nặng {neg})"
    text += " " + concl + "."
    if verdict == "hai mặt" and tilt:
        yrs = _lord_years(f, tilt)
        if yrs:
            ages = listing([str(y) for y in yrs])
            text += (f" Bên nào trội lên thường lộ rõ hơn vào những năm {P(tilt)} làm chủ năm theo phép đếm năm (profection), gần nhất là năm {ages} tuổi."
                     if _once(f, f"tilt:{tilt}") else f" Năm {ages} tuổi ({P(tilt)} làm chủ năm) cũng là lúc nên để ý mảng này.")
    for c in top:
        if c.warn and c.pol < 0 and _once(f, f"warn:{c.ev[0]['id'] if c.ev else c.key}"):
            text += f" Khi {P(c.ev[0]['id']) if c.ev and c.ev[0]['kind'] == 'planet' else 'sao này'} yếu, sách tả những nét cần coi chừng: {listing(c.warn)}."
            break
    shows = [s for c in top if c.pol in (side, 0) for s in c.show if s and s not in text][:3]
    if shows:
        holder = next((e["id"] for c in top for e in c.ev if e["kind"] == "planet"), None)
        text += f" Với {P(holder)}, sách mô tả cụ thể: {listing(shows)}." if holder else f" Sách mô tả cụ thể: {listing(shows)}."
    text += _time_note(f, cid, support[:3] + contra[:2])
    steps = ["Cách gom (của Thiên Bàn, không phải của một tác giả): mỗi chứng là kết quả một phép của chính chương này; trọng số 3 khi sách tự tính "
             "chứng ấy bằng nhiều chứng, 2 cho sao chủ của phép, 1 cho chứng phụ; chủ đề có tổng trọng số lớn nhất là ý chính; "
             "'hai mặt' khi bên nhẹ hơn vẫn nặng quá một nửa bên kia."] + [
        f"{'+' if c.pol > 0 else '−' if c.pol < 0 else '·'}{c.w} · {c.author} · {c.why}" for c in claims]
    ev, seen = [], set()
    for c in support[:3] + contra[:2]:
        for e in c.ev:
            k = (e["kind"], e["id"])
            if k not in seen:
                seen.add(k)
                ev.append(e)
    return Para(f"{cid}.tom_tat", heading, text, "compare", srcs(*dict.fromkeys(c.src for c in claims)), ev, "overview",
                steps=steps, polarity=0, topic=cid, keys=[f"thesis:{top_key}", f"verdict:{verdict}"], layer="summary")


# --------------------------------------------------------------------------------------------- Tính cách
def _manners_planet(f: Facts) -> tuple[str, str] | None:
    ms = f.manners_significator()
    if not ms:
        return None
    p = ms["planets"][0]
    if p in ("sun", "moon"):
        p = dignity.domicile_lord(f.b[p]["sign"])
        if p in ("sun", "moon"):
            return None
    return p, ms["why"]


def personality(f: Facts) -> Para | None:
    cl: list[Claim] = []
    mp = _manners_planet(f)
    if mp:
        p, how = mp
        st = f.lilly_state(p)
        mm = M["lilly_manners"][p]
        via = {"in_ascending_sign": "đứng ngay trong cung Mọc", "joined_moon_or_mercury": "đi sát Mặt Trăng hoặc Sao Thủy",
               "lord_of_ascendant": "làm chủ cung Mọc"}[how]
        traits = mm["well"][:3] if st != "ill" else mm["well"][:2]
        cl.append(Claim(f"planet:{p}", f"nét của {P(p)}", {"well": 1, "ill": -1}.get(st, 0), 2,
                        f"{P(p)} {via}, nên Lilly lấy nó làm sao chủ tính cách, và nó {_state_words(f, p)}", "Lilly",
                        f"LILLY_CA:{mm['loc']}", _short(traits, 3), [ev_in(f, p, "traditional")],
                        [("asc_sign", "asc_sign")] if how != "joined_moon_or_mercury" else [], pick=True,
                        warn=_short(mm["ill"], 2) if st == "ill" else []))
    sr = f.soul_ruler()
    r = sr["rulers"][0]
    hon = f.honourable(r)
    soul = M["ptolemy_soul"][r]
    cl.append(Claim(f"planet:{r}", f"nét của {P(r)}", 1 if hon else -1, 2,
                    f"theo Ptolemy, {P(r)} chi phối cả cách nghĩ (đọc từ Sao Thủy) lẫn cách cảm (đọc từ Mặt Trăng) của bạn"
                    + (", và nó đang đứng ở chỗ quen thuộc của mình" if hon else ", nhưng nó đang ở chỗ lạ"), "Ptolemy",
                    "PTOL_TETRA:III.13 pp.333-361", _short(soul["honourable"][:3] if hon else soul["honourable"][:2], 3), [ev_planet(f.c, r)], pick=True,
                    warn=[] if hon else _short(soul["opposite"], 2)))
    lg = f.lord_of_geniture
    if lg and len(lg["lords"]) == 1:
        g = lg["lords"][0]
        cl.append(Claim(f"planet:{g}", f"nét của {P(g)}", 1 if lg["totals"][g] >= 5 else 0, 1,
                        f"{P(g)} gom nhiều điểm sức mạnh nhất trong lá số ({lg['totals'][g]:+d} theo cách cộng của Lilly)", "Lilly", "LILLY_CA:p.531",
                        _short(M["planets"][g]["lilly_well"]["vi"], 2), [ev_in(f, g, "traditional")], [("traditional", g)], pick=True))
    cx = f.lilly_complexion()
    if cx and cx["temperament"]:
        k = cx["temperament"]
        clear = abs(cx["hot_minus_cold"]) > 1 and abs(cx["moist_minus_dry"]) > 1
        cl.append(Claim("temperament", f"khí chất {TEMPERAMENT_VI[k].split(' (')[0]}", 0, 2 if clear else 1,
                        f"đếm các chứng nóng, lạnh, ẩm, khô theo Lilly thì khí chất nghiêng về {TEMPERAMENT_VI[k].split(' (')[0]}"
                        + ("" if clear else " (chỉ nghiêng nhẹ)"), "Lilly", "LILLY_CA:p.539", [M["lilly_temperament_manners"][k]],
                        [ev_point(f.c, "asc")], [("asc_sign", "asc_sign")]))
    sun = f.b["sun"]["sign"]
    cl.append(Claim("sun_sign", f"Mặt Trời ở {S(sun)}", 0, 1, f"Mặt Trời ở {S(sun)}, phần Alan Leo gọi là cái lõi bền của con người", "Alan Leo",
                    "LEO:How to Judge a Nativity pp.72-86", [M["leo_sun"][sun]], [ev_planet(f.c, "sun")]))

    def thesis(key, top, all_, verdict):
        if key.startswith("planet:"):
            p = key.split(":")[1]
            traits = listing([t for c in top for t in c.show][:3])
            out = (f"Nét nổi bật nhất trong tính cách của bạn mang màu của {P(p)}, {_nature(p)}: {traits}." if len(top) >= 2
                   else f"Tính cách của bạn nghiêng về màu của {P(p)}, {_nature(p)}: {traits}.")
            if mp and mp[0] != p:
                other = next(c for c in all_ if c.key == f"planet:{mp[0]}")
                out += (f" Lớp ngoài, tức cách bạn hiện ra và cư xử với người khác, lại mang màu {P(mp[0])}, {_nature(mp[0])}: {listing(other.show[:2])}."
                        if other.show else "")
            elif r != p:
                inner = next(c for c in all_ if c.key == f"planet:{r}")
                out += (f" Lớp bên trong, tức cách bạn nghĩ và cảm, lại mang màu {P(r)}, {_nature(r)}: {listing(inner.show[:2])}." if inner.show else "")
            return out
        c = top[0]
        return f"Nét nền của tính cách bạn là {c.about}: {listing(c.show)}."
    tilt = mp[0] if mp else r
    return summarize(f, "tinh_cach", "Tóm tắt: tính cách", cl, thesis, tilt=tilt)


# --------------------------------------------------------------------------------------------- Tư duy
def mind(f: Facts) -> Para | None:
    cl: list[Claim] = []
    lm = f.platick("mercury", "moon")
    wm = f.lilly_state("mercury")
    mm = M["lilly_manners"]["mercury"]
    cl.append(Claim("planet:mercury", "Sao Thủy", {"well": 1, "ill": -1}.get(wm, 0), 2, f"Sao Thủy, sao của trí óc, {_state_words(f, 'mercury')}", "Lilly",
                    "LILLY_CA:p.543", _short(mm["well"][:3], 3), [ev_in(f, "mercury", "traditional")], warn=_short(mm["ill"], 2) if wm == "ill" else []))
    if lm in ("sextile", "trine"):
        cl.append(Claim("planet:mercury", "Sao Thủy", 1, 1, f"Sao Thủy và Mặt Trăng nối nhau bằng {gloss(f, 'góc hài hòa')}, điều Lilly coi là dấu hiệu tiếp thu tốt",
                        "Lilly", "LILLY_CA:p.543", [], [ev_planet(f.c, "moon")]))
    elif lm in ("square", "opposition"):
        cl.append(Claim("mind_link", "mối nối lý trí và cảm xúc", -1, 1, f"Sao Thủy và Mặt Trăng nối nhau bằng {gloss(f, 'góc căng')}, điều Lilly coi là khiến việc tiếp thu kém trơn tru",
                        "Lilly", "LILLY_CA:p.543", ["suy nghĩ và cảm xúc hay giằng co, học tốt nhất khi có phương pháp và thời gian"], [ev_planet(f.c, "moon")]))
    sol = f.c["conditions"]["mercury"].get("solar", {}).get("phase")
    if sol in ("combust", "under_beams"):
        cl.append(Claim("planet:mercury", "Sao Thủy", -1, 1, f"Sao Thủy {gloss(f, 'bị Mặt Trời đốt') if sol == 'combust' else 'nằm dưới tia Mặt Trời'}, nên Lilly cho rằng nó khó tự thể hiện",
                        "Lilly", "LILLY_CA:pp.113-114", [], [ev_planet(f.c, "mercury")]))
    if f.b["mercury"]["retrograde"]:
        cl.append(Claim("planet:mercury", "Sao Thủy", -1, 1, f"Sao Thủy đang {gloss(f, 'nghịch hành')}, Lilly trừ điểm cho sao đi lùi", "Lilly", "LILLY_CA:p.115", [], [ev_planet(f.c, "mercury")]))
    from ..zodiac import MODALITY
    mk = MODALITY[sign_index(f.lon["mercury"])]
    cls = {"fixed": "solid", "mutable": "bicorporeal"}.get(mk, "solstitial_equinoctial")
    cl.append(Claim("mind_sign", "kiểu tâm trí", 0, 1, f"Sao Thủy ở {S(f.b['mercury']['sign'])}, loại cung mà Ptolemy gắn với một kiểu tâm trí riêng", "Ptolemy",
                    "PTOL_TETRA:III.13 p.335", [M["sign_soul"][cls]], [ev_planet(f.c, "mercury")]))
    if f.time_known:
        h = f.house_lilly("mercury")
        if h in (3, 9):
            cl.append(Claim("planet:mercury", "Sao Thủy", 0, 1, f"Sao Thủy ở Nhà {h} theo cách chia của Lilly, nơi gắn với {M['houses'][str(h)]['lilly']['vi'].split(',')[0]}",
                            "Lilly", M["houses"][str(h)]["lilly"]["src"], [], [ev_in(f, "mercury", "traditional")], [("traditional", "mercury")]))

    def thesis(key, top, all_, verdict):
        if key == "planet:mercury":
            word = {"thuận": "nhanh và có chỗ dựa", "nghịch": "có năng lực nhưng cần phương pháp để đi xa", "hai mặt": "sắc ở vài chỗ, vướng ở vài chỗ", "nhẹ": "ở mức nền, không có điểm nghẽn rõ"}[verdict]
            traits = listing([t for c in top for t in c.show][:3])
            return f"Về trí óc, bạn {word} (đọc qua Sao Thủy)" + (f": {traits}." if traits else ".")
        c = top[0]
        return f"Cách bạn suy nghĩ mang dấu {c.about}: {listing(c.show)}."
    return summarize(f, "tu_duy", "Tóm tắt: tư duy và học tập", cl, thesis, tilt="mercury")


# --------------------------------------------------------------------------------------------- Cảm xúc
def emotions(f: Facts) -> Para | None:
    cl: list[Claim] = []
    st = f.lilly_state("moon")
    mm = M["planets"]["moon"]
    cl.append(Claim("planet:moon", "Mặt Trăng", {"well": 1, "ill": -1}.get(st, 0), 2, f"Mặt Trăng, sao của đời sống cảm xúc, {_state_words(f, 'moon')}", "Lilly",
                    "LILLY_CA:p.81", _short(mm["lilly_well"]["vi"][:3] if st != "ill" else ["khi thiếu chỗ dựa tinh thần, nề nếp đều đặn giúp giữ thăng bằng"], 3),
                    [ev_in(f, "moon", "traditional")]))
    app = f.moon_contacts()["applies_to"]
    if app:
        pa, asp = app["planet"], app["aspect"]
        soft = asp in ("sextile", "trine")
        hard = asp in ("square", "opposition")
        pol = (0 if hard else 1) if pa in BENEFICS else (0 if soft else -1) if pa in MALEFICS else 0
        what = ("dễ tìm về sự dễ chịu và hòa giải" if pa in BENEFICS and not hard else "dễ gặp sức cản, cần thời gian để lắng" if pa in MALEFICS and not soft
                else "gặp sức cản nhưng có lối ra" if pa in MALEFICS else "vẫn tìm về sự dễ chịu, nhưng qua chút giằng co" if pa in BENEFICS
                else "gắn với lý trí hay với cái tôi nhiều hơn với người khác")
        kind = gloss(f, "cát tinh") if pa in BENEFICS else gloss(f, "hung tinh") if pa in MALEFICS else "một sao trung tính"
        cl.append(Claim("moon_way", "cách cảm xúc vận hành", pol, 2,
                        f"lúc bạn sinh, Mặt Trăng đang tiến tới {ASPECT_NOUN[asp]} với {P(pa)}, {kind}; Ptolemy đọc phần cảm theo sao mà Mặt Trăng hướng tới, nên cảm xúc {what}", "Ptolemy",
                        "PTOL_TETRA:III.13 p.333", [f"cảm xúc {what}"], [ev_planet(f.c, "moon"), ev_planet(f.c, pa)]))
    ph = f.c["moon_phase"]
    mod = M["ptolemy_soul_mod"]["moon_waxing" if ph["waxing"] else "moon_waning"]
    cl.append(Claim("moon_phase", "pha Mặt Trăng", 0, 1, f"Mặt Trăng {'đang tròn dần' if ph['waxing'] else 'đang khuyết dần'} lúc sinh, điều Ptolemy dùng để điều chỉnh tính cách",
                    "Ptolemy", f"PTOL_TETRA:III.13 {mod['loc']}", [mod["vi"]], [ev_planet(f.c, "moon")]))
    ms = f.b["moon"]["sign"]
    cl.append(Claim("planet:moon", "Mặt Trăng", 0, 1, f"Mặt Trăng ở {S(ms)}, phần Alan Leo gọi là nhân cách, tức cảm xúc và giác quan", "Alan Leo",
                    "LEO:How to Judge a Nativity pp.72-86", [M["leo_moon"][ms]], [ev_planet(f.c, "moon")]))

    def thesis(key, top, all_, verdict):
        if key == "planet:moon":
            word = {"thuận": "có nền vững", "nghịch": "nhạy và dễ chao", "hai mặt": "vừa có chỗ dựa vừa có lúc chao đảo", "nhẹ": "khá êm, ít biến động lớn"}[verdict]
            li = next((c for c in top if c.author == "Lilly"), None)
            leo = next((c for c in top if c.author == "Alan Leo"), None)
            out = f"Ở bạn, đời sống cảm xúc {word} (đọc qua Mặt Trăng ở {S(f.b['moon']['sign'])})" + (f": {listing(li.show[:2])}." if li and li.show else ".")
            if leo and leo.show:
                out += f" Alan Leo thêm một nét khác, có thể cùng tồn tại, cho Mặt Trăng ở {S(f.b['moon']['sign'])}: {leo.show[0]}."
            return out
        return f"Cảm xúc của bạn vận hành theo kiểu: {listing([t for c in top for t in c.show][:2])}."
    return summarize(f, "cam_xuc", "Tóm tắt: cảm xúc", cl, thesis, tilt="moon")


# --------------------------------------------------------------------------------------------- Sự nghiệp
def career(f: Facts) -> Para | None:
    if not f.time_known:
        return None
    cl: list[Claim] = []
    la = f.lord_of_action()
    q = la["quality"]
    acts = M["ptolemy_action"]
    keyset = "+".join(sorted(q, key=["mercury", "venus", "mars"].index)) if q else ""
    if keyset in acts:
        sig = q[0]
        pl = f.place_ptolemy(sig)
        pol = 1 if pl in (1, 10, 7, 4) else -1 if pl in (3, 6, 9, 12) else 0
        cl.append(Claim("field", acts[keyset]["field"], pol, 2,
                        f"{planet_list(q)} là sao Ptolemy chọn để định loại công việc (sao {'vừa mọc buổi sáng' if la['morning'] in q else 'đứng ở đỉnh trời' if set(q) & set(la['at_mc']) else 'chủ Thiên Đỉnh'})"
                        + (f" và đứng ở {gloss(f, 'nhà góc')}" if pol > 0 else f" nhưng đứng ở {gloss(f, 'nhà suy')}" if pol < 0 else ""),
                        "Ptolemy", f"PTOL_TETRA:IV.4 {acts[keyset]['loc']}", [acts[keyset]["field"]],
                        [ev_in(f, p, "ptolemy") for p in q], [("ptolemy", sig)], pick=True))
    lp = f.lilly_profession()
    if lp and lp.get("significator"):
        sg = lp["significator"]
        info = M["lilly_profession"].get(sg)
        if info:
            pol = {"strong": 1, "weak": -1}.get(lp["fame"], 0)
            fld = info["field"].split(";")[0].split(":")[0]
            cl.append(Claim("field" if not cl else "field_lilly", fld, pol, 2,
                            f"{P(sg)} là sao chủ nghề theo phép thử của Lilly" + (", lại có phẩm vị, ở góc và mọc trước Mặt Trời" if pol > 0 else ", nhưng còn yếu hoặc ở nhà suy" if pol < 0 else ""),
                            "Lilly", f"LILLY_CA:{info['loc']}", [fld], [ev_in(f, sg, "traditional")], [("traditional", sg)], pick=True))
    mc_sign = f.c["angles"]["mc"]["sign"]
    lmc = dignity.domicile_lord(mc_sign)
    for who, p in (("Mặt Trời, sao chính của danh vọng", "sun"), (f"{P(lmc)}, chủ của Thiên Đỉnh", lmc)):
        g, a = f.lilly_honour_grade(p)
        if g == "high" or (g == "low" and a == "cadent") or (g != "low" and a == "angular"):
            pol = 1 if g == "high" or a == "angular" else -1
            cl.append(Claim("honour", "sự ghi nhận", pol, 2 if p == "sun" else 1,
                            f"{who}, " + ("có phẩm vị mạnh" if g == "high" else "không có phẩm vị" if g == "low" else "có chút phẩm vị")
                            + (f" và đứng ở {gloss(f, 'nhà góc')}" if a == "angular" else f", lại ở {gloss(f, 'nhà suy')}" if a == "cadent" else ""),
                            "Lilly", "LILLY_CA:pp.615-617", [], [ev_in(f, p, "traditional")], [("traditional", p)]))
    in10 = [p for p in CLASSICAL if f.house_lilly(p) == 10]
    for p in in10:
        if p in BENEFICS or p in MALEFICS:
            cl.append(Claim("honour", "sự ghi nhận", 1 if p in BENEFICS else -1, 1, f"{P(p)} là {gloss(f, 'cát tinh') if p in BENEFICS else gloss(f, 'hung tinh')} đứng ở Nhà 10 (nhà của địa vị)",
                            "Lilly", "LILLY_CA:pp.615-617", [M["houses"]["10"]["lilly"]["vi"].split(",")[0]], [ev_in(f, p, "traditional")], [("traditional", p)]))
    from .. import stars as STARS
    for p in dict.fromkeys(["sun", "moon", lmc] + in10):
        near = f.stars_near(p, STARS.ROYAL_616)
        if near:
            cl.append(Claim("honour", "sự ghi nhận", 1, 3, f"{P(p)} đứng sát {STARS.SHORT[near[0]]}, một định tinh mà Lilly tính bằng ba chứng thăng tiến",
                            "Lilly", "LILLY_CA:p.616", [], [ev_planet(f.c, p)]))
    g = f.valens_grade(dignity.domicile_lord(SIGNS[(sign_index(f.c["lots"]["fortune"]["lon"]) + 9) % 12]))
    rr = dignity.domicile_lord(SIGNS[(sign_index(f.c["lots"]["fortune"]["lon"]) + 9) % 12])
    if g in ("angular", "cadent"):
        cl.append(Claim("honour", "sự ghi nhận", 1 if g == "angular" else -1, 1,
                        f"theo Valens, sao trông coi địa vị của bạn ({P(rr)}) " + ("đứng ở một góc, chỗ mạnh" if g == "angular" else "đứng ở chỗ khó phát huy (ngay trước một góc)"), "Valens", "VALENS_ANTH:II.17",
                        [], [ev_in(f, rr, "hellenistic")], [("hellenistic", rr)]))

    def thesis(key, top, all_, verdict):
        fields = [c.about for c in all_ if c.key in ("field", "field_lilly")]
        hon = [c for c in all_ if c.key == "honour"]
        hp = sum(c.w for c in hon if c.pol > 0) - sum(c.w for c in hon if c.pol < 0)
        rec = "dễ được ghi nhận" if hp >= 2 else "phải tự tạo chỗ đứng nhiều hơn mới được ghi nhận" if hp <= -2 else "được ghi nhận ở mức vừa"
        if fields:
            same = len(fields) >= 2 and fields[0] == fields[1]
            sigs = planet_list(list(dict.fromkeys(e["id"] for c in all_ if c.key in ("field", "field_lilly") for e in c.ev if e["kind"] == "planet")))
            return (f"Công việc hợp với bạn nhất là {fields[0]}" + ("" if same or len(fields) < 2 else f", và cũng mở sang {fields[1]}")
                    + f" (đọc qua sao chủ nghề: {sigs}); về mặt danh tiếng, lá số cho thấy bạn {rec}.")
        return f"Về sự nghiệp, điều lá số nói rõ nhất là chuyện danh tiếng: bạn {rec}."
    sig = (q[0] if q else None) or (lp or {}).get("significator") or lmc
    return summarize(f, "su_nghiep", "Tóm tắt: sự nghiệp", cl, thesis, tilt=sig)


# --------------------------------------------------------------------------------------------- Tài chính
def money(f: Facts) -> Para | None:
    if not f.time_known:
        return None
    cl: list[Claim] = []
    fr = f.fortune_ruler_ptolemy()
    r = fr["rulers"][0]
    w_src = M["ptolemy_wealth"].get(r)
    if w_src:
        strong = f.ptolemy_strong(r)
        cl.append(Claim("source", w_src, 1 if strong else 0, 2,
                        f"{P(r)} là sao nắm điểm của cải (Lot of Fortune) theo Ptolemy" + (", và nó đang có sức" if strong else ", nhưng nó đang yếu"),
                        "Ptolemy", "PTOL_TETRA:IV.2 p.375", [w_src], [ev_in(f, r, "ptolemy")], [("ptolemy", r)]))
    if r == "saturn" and f._configured("saturn", "jupiter"):
        cl.append(Claim("source", "của thừa kế", 1, 1, "Sao Thổ nắm điểm của cải và chiếu Sao Mộc, trường hợp Ptolemy nói tới của thừa kế", "Ptolemy", "PTOL_TETRA:IV.2 p.375",
                        ["của thừa kế"], [ev_planet(f.c, "saturn"), ev_planet(f.c, "jupiter")]))
    sign2 = SIGNS[sign_index(f.regio[1])] if f.regio else None
    if sign2:
        l2 = dignity.domicile_lord(sign2)
        lf = dignity.domicile_lord(f.c["lots"]["fortune"]["sign"])
        roles: dict[str, list[str]] = {}
        for role, p in (("chủ Nhà 2 (nhà tiền bạc)", l2), ("chủ của cung chứa Part of Fortune", lf), ("sao chủ của cải nói chung", "jupiter")):
            roles.setdefault(p, []).append(role)
        for p, rs in roles.items():
            st = f.lilly_state(p)
            if st != "mixed":
                timed = ([("cusp", "2")] if p == l2 else []) + ([("traditional", "fortune")] if p == lf else [])
                cl.append(Claim("keep", "việc kiếm và giữ tiền", 1 if st == "well" else -1, len(rs),
                                f"{P(p)}, {'vừa là ' + ', vừa là '.join(rs) if len(rs) > 1 else rs[0]}, {_state_words(f, p)}", "Lilly", "LILLY_CA:p.552",
                                [], [ev_in(f, p, "traditional")], timed))
        for p in [p for p in CLASSICAL if f.house_lilly(p) == 2]:
            if p in BENEFICS or p in MALEFICS:
                cl.append(Claim("keep", "việc kiếm và giữ tiền", 1 if p in BENEFICS else -1, 1,
                                f"{P(p)}, {'một ' + gloss(f, 'cát tinh') if p in BENEFICS else 'một ' + gloss(f, 'hung tinh')}, đứng trong Nhà 2 theo cách chia của Lilly",
                                "Lilly", "LILLY_CA:p.552", [], [ev_in(f, p, "traditional")], [("traditional", p)]))
    acc = dignity.domicile_lord(SIGNS[(sign_index(f.c["lots"]["fortune"]["lon"]) + 10) % 12])
    g = f.valens_grade(acc)
    if g in ("angular", "cadent"):
        cl.append(Claim("keep", "việc kiếm và giữ tiền", 1 if g == "angular" else -1, 1,
                        f"theo Valens, sao trông coi 'nơi thành tựu' về của cải ({P(acc)}) " + ("đứng ở một góc, chỗ mạnh" if g == "angular" else "đứng ở chỗ khó phát huy (ngay trước một góc)"),
                        "Valens", "VALENS_ANTH:II.20", [], [ev_in(f, acc, "hellenistic")], [("hellenistic", acc)]))
    merc = f.lilly_state("mercury")
    if merc != "mixed":
        cl.append(Claim("trade", "buôn bán", 1 if merc == "well" else -1, 1, f"Sao Thủy, sao của buôn bán, {_state_words(f, 'mercury')}", "Lilly", "LILLY_CA:p.77",
                        ["đầu óc buôn bán" if merc == "well" else "việc buôn bán cần quy trình chặt chẽ"], [ev_in(f, "mercury", "traditional")]))

    def thesis(key, top, all_, verdict):
        src_ = [c for c in all_ if c.key == "source"]
        lead = (f"Tiền bạc đến với bạn chủ yếu qua {src_[0].about} (theo {P(r)}, sao nắm điểm của cải)" if src_
                else f"Lá số không chỉ rõ một nguồn tiền riêng ({P(r)} nắm điểm của cải nhưng Ptolemy không cho nguồn lợi riêng cho trường hợp này)")
        tone = {"thuận": "và các dấu hiệu giữ của nghiêng về phía thuận", "nghịch": "nhưng việc giữ được tiền đòi hỏi kỷ luật hơn là trông vào vận",
                "hai mặt": "còn chuyện giữ tiền thì có cả điểm tựa lẫn chỗ hở", "nhẹ": "và chuyện giữ tiền không nghiêng hẳn về phía nào"}[verdict]
        return f"{lead}, {tone}."
    return summarize(f, "tai_chinh", "Tóm tắt: tài chính", cl, thesis, tilt=r)


# --------------------------------------------------------------------------------------------- Quan hệ
def relations(f: Facts) -> Para | None:
    if not f.time_known or not f.regio:
        return None
    cl: list[Claim] = []
    s7 = SIGNS[sign_index(f.regio[6])]
    l7 = dignity.domicile_lord(s7)
    st = f.lilly_state(l7)
    cl.append(Claim(f"planet:{l7}", f"{P(l7)}", {"well": 1, "ill": -1}.get(st, 0), 2,
                    f"{P(l7)} làm chủ Nhà 7, nhà của hôn nhân và người bạn đời, và {_state_words(f, l7)}", "Lilly", "LILLY_CA:pp.600-602",
                    _short(M["planets"][l7]["lilly_well"]["vi"] if st != "ill" else M["planets"][l7]["lilly_ill"]["vi"], 2), [ev_in(f, l7, "traditional")], [("cusp", "7")]))
    for p in [p for p in CLASSICAL if f.house_lilly(p) == 7]:
        if p in BENEFICS or p in MALEFICS:
            cl.append(Claim("seventh", "Nhà 7", 1 if p in BENEFICS else -1, 1, f"{P(p)}, {'một ' + gloss(f, 'cát tinh') if p in BENEFICS else 'một ' + gloss(f, 'hung tinh')}, đứng trong Nhà 7",
                            "Lilly", "LILLY_CA:p.587", [], [ev_in(f, p, "traditional")], [("traditional", p)]))
    if f.gender in ("male", "female"):
        a, b = ("venus", "moon") if f.gender == "male" else ("sun", "mars")
        for p in (a, b):
            s_ = f.lilly_state(p)
            if s_ != "mixed":
                cl.append(Claim(f"planet:{p}", P(p), 1 if s_ == "well" else -1, 1, f"{P(p)}, sao Lilly dùng cho chuyện vợ chồng ở lá số {'nam' if f.gender == 'male' else 'nữ'}, {_state_words(f, p)}",
                                "Lilly", f"LILLY_CA:p.{587 if f.gender == 'male' else 600}", [], [ev_in(f, p, "traditional")]))
        lasc = dignity.domicile_lord(f.c["angles"]["asc"]["sign"])
        if lasc != l7 and f.platick(lasc, l7) in ("sextile", "trine"):
            cl.append(Claim("concord", "sự hòa hợp", 1, 2, f"chủ cung Mọc ({P(lasc)}) và chủ Nhà 7 ({P(l7)}) chiếu nhau bằng {gloss(f, 'góc hài hòa')}, dấu hiệu Lilly coi là hòa thuận",
                            "Lilly", "LILLY_CA:p.602", ["hai người dễ hiểu ý nhau"], [ev_planet(f.c, lasc), ev_planet(f.c, l7)]))
    day = f.is_day
    lot = (f.lon["asc"] + (f.lon["venus"] - f.lon["jupiter"] if day else f.lon["jupiter"] - f.lon["venus"])) % 360
    lr = dignity.domicile_lord(SIGNS[sign_index(lot)])
    g = f.valens_grade(lr)
    if g in ("angular", "cadent"):
        cl.append(Claim("lot", "điểm hôn nhân", 1 if g == "angular" else -1, 1, f"theo Valens, sao trông coi điểm hôn nhân ({P(lr)}) " + ("đứng ở một góc, chỗ mạnh" if g == "angular" else "đứng ở chỗ khó phát huy (ngay trước một góc), dù bản thân nó mạnh hay yếu"),
                        "Valens", "VALENS_ANTH:II.37", [], [ev_in(f, lr, "hellenistic")], [("hellenistic", lr)]))

    def thesis(key, top, all_, verdict):
        c = [x for x in all_ if x.key == f"planet:{l7}"][0]
        look = (f" Theo Lilly, tính nết người bạn đời được tả qua {P(l7)}: {listing(c.show)}." if c.show and c.pol >= 0 else
                f" Lilly tả người bạn đời qua {P(l7)}; sao này đang yếu, nên phần ấy nói về chỗ hai người dễ va nhau hơn là về một người cụ thể." if c.show else "")
        tone = {"thuận": "có nhiều điểm tựa", "nghịch": "cần nhiều vun đắp hơn mức trung bình", "hai mặt": "vừa có điểm tựa vừa có chỗ dễ vấp", "nhẹ": "không có dấu hiệu mạnh theo chiều nào"}[verdict]
        return f"Trong chuyện gắn bó lâu dài, lá số của bạn {tone} (đọc qua Nhà 7 ở {S(s7)} và chủ của nó là {P(l7)}).{look}"
    return summarize(f, "quan_he", "Tóm tắt: quan hệ và hôn nhân", cl, thesis, tilt=l7)


# --------------------------------------------------------------------------------------------- Gia đình
def family(f: Facts) -> Para | None:
    if not f.time_known or not f.regio:
        return None
    cl: list[Claim] = []
    day = f.is_day
    for n, who, extra in ((4, "người cha", "sun" if day else "saturn"), (10, "người mẹ", "venus" if day else "moon")):
        l = dignity.domicile_lord(SIGNS[sign_index(f.regio[n - 1])])
        sigs = list(dict.fromkeys([l, extra] + [p for p in CLASSICAL if f.house_lilly(p) == n]))
        ok = [x for x in sigs if f.lilly_state(x) == "well"]
        bad = [x for x in sigs if f.lilly_state(x) == "ill"]
        if ok or bad:
            pol = 1 if len(ok) > len(bad) else -1 if len(bad) > len(ok) else 0
            cl.append(Claim(f"parent{n}", f"chỗ dựa từ {who}", pol, 2 if pol else 1,
                            f"với {who}, trong các sao Lilly xét (chủ Nhà {n}, {P(extra)}{', các sao ở Nhà ' + str(n) if len(sigs) > 2 else ''}) thì "
                            + (f"{planet_list(ok)} mạnh" if ok else "") + (", " if ok and bad else "") + (f"{planet_list(bad)} yếu" if bad else ""),
                            "Lilly", "LILLY_CA:pp.569-570", [], [ev_in(f, x, "traditional") for x in sigs[:2]], [("cusp", str(n))]))
    pat = [x for x in (["sun"] if day else ["saturn", "moon"]) if any(f.platick(x, b) in ("conjunction", "sextile", "trine") for b in BENEFICS)]
    if pat:
        cl.append(Claim("patrimony", "gia sản", 1, 1, f"{planet_list(pat)} được {gloss(f, 'cát tinh')} chiếu tốt, dấu hiệu Lilly đọc là gia sản có nền", "Lilly", "LILLY_CA:pp.572-573",
                        ["gia đình có nền, và người sinh làm nó tăng thêm"], [ev_planet(f.c, x) for x in pat]))
    l3 = dignity.domicile_lord(SIGNS[sign_index(f.regio[2])])
    s3 = f.lilly_state(l3)
    if s3 != "mixed":
        cl.append(Claim("siblings", "anh chị em", 1 if s3 == "well" else -1, 1, f"{P(l3)}, chủ Nhà 3 (anh chị em), {_state_words(f, l3)}", "Lilly", "LILLY_CA:pp.564-565",
                        [], [ev_in(f, l3, "traditional")]))

    if not cl:                 # every significator at middling strength: say so, on the lords themselves
        for n, who in ((4, "người cha"), (10, "người mẹ")):
            l = dignity.domicile_lord(SIGNS[sign_index(f.regio[n - 1])])
            cl.append(Claim(f"parent{n}", f"chỗ dựa từ {who}", 0, 1, f"với {who}, chủ Nhà {n} là {P(l)}, có sức ở mức vừa", "Lilly", "LILLY_CA:pp.569-570",
                            [], [ev_in(f, l, "traditional")], [("cusp", str(n))]))

    def thesis(key, top, all_, verdict):
        tone = {"thuận": "là một chỗ dựa thật", "nghịch": "là nơi bạn thường phải tự đứng vững nhiều hơn là được đỡ", "hai mặt": "vừa nâng đỡ vừa có phần nặng nề", "nhẹ": "không phải điểm nhấn của lá số"}[verdict]
        return f"Gia đình gốc {tone}, theo cách Lilly đọc các sao của cha (Nhà 4), mẹ (Nhà 10) và anh chị em (Nhà 3)."
    return summarize(f, "gia_dinh", "Tóm tắt: gia đình", cl, thesis)


# --------------------------------------------------------------------------------------------- Định hướng
def direction(f: Facts) -> Para | None:
    if not f.time_known:
        return None
    cl: list[Claim] = []
    asc = f.c["angles"]["asc"]["sign"]
    lord = dignity.domicile_lord(asc)
    h = f.house_modern(lord)
    dignified = bool(set(f.lilly_essential(lord)["has"]) & {"domicile", "exaltation"})
    lg = f.lord_of_geniture
    ruler = lord if (dignified or h in (1, 10, 7, 9, 11)) else (lg["lords"][0] if lg else lord)
    cl.append(Claim(f"planet:{ruler}", P(ruler), 1 if ruler == lord else 0, 2,
                    (f"{P(lord)} làm chủ cung Mọc và đủ điều kiện Alan Leo đặt ra (có phẩm vị hoặc đứng ở nhà mạnh), nên nó là hành tinh dẫn dắt" if ruler == lord
                     else f"chủ cung Mọc ({P(lord)}) chưa đủ điều kiện của Alan Leo, nên vai dẫn dắt chuyển sang {P(ruler)}, sao mạnh nhất lá số"),
                    "Alan Leo", "LEO:The Art of Synthesis", _short(M["planets"][ruler]["lilly_well"]["vi"], 2), [ev_planet(f.c, ruler)], [("modern", lord), ("asc_sign", "asc_sign")], pick=True))
    if lg and len(lg["lords"]) == 1:
        g = lg["lords"][0]
        cl.append(Claim(f"planet:{g}", P(g), 1 if lg["totals"][g] >= 5 else 0, 1, f"{P(g)} là sao chủ lá số theo cách cộng điểm của Lilly", "Lilly", "LILLY_CA:p.531",
                        _short(M["planets"][g]["lilly_well"]["vi"], 2), [ev_in(f, g, "traditional")], [("traditional", g)], pick=True))
    fort, spirit = f.c["lots"]["fortune"], f.c["lots"]["spirit"]
    sr = dignity.domicile_lord(spirit["sign"])
    concord = f.b[sr]["sign"] in (fort["sign"], SIGNS[(sign_index(fort["lon"]) + 9) % 12])
    cl.append(Claim("concord", "điều mình muốn và điều đời mang tới", 1 if concord else -1, 2,
                    (f"chủ của điểm Daimon (tâm trí, dự định) là {P(sr)}, đứng ngay ở chỗ của Fortune hay chỗ thứ 10 của nó, trường hợp Valens gọi là rạng rỡ" if concord
                     else f"theo Valens, điểm chỉ ý muốn của bạn (Daimon) và điểm chỉ những gì đời mang tới (Fortune) không có liên hệ thuận với nhau, nên hai thứ ấy có thể đi hai đường"),
                    "Valens", "VALENS_ANTH:II.19", [], [ev_point(f.c, "fortune"), ev_point(f.c, "spirit")], [("hellenistic", "spirit")]))

    def thesis(key, top, all_, verdict):
        if key.startswith("planet:"):
            p = key.split(":")[1]
            traits = listing([t for c in top for t in c.show][:3])
            return f"Hướng đi của đời bạn được dẫn dắt bởi {P(p)}, {_nature(p)}: khi sống đúng với nó, bạn {traits}." if traits else f"Hướng đi của đời bạn được dẫn dắt bởi {P(p)}, {_nature(p)}."
        return "Điều lá số nói rõ nhất về hướng đi là sự ăn khớp giữa điều bạn muốn và điều đời mang tới."
    return summarize(f, "dinh_huong", "Tóm tắt: định hướng cuộc sống", cl, thesis, tilt=ruler)


SUMMARIES = {"tinh_cach": personality, "tu_duy": mind, "cam_xuc": emotions, "su_nghiep": career, "tai_chinh": money,
             "quan_he": relations, "gia_dinh": family, "dinh_huong": direction}
