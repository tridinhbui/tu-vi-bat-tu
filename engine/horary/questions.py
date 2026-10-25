"""What is being asked: topic, the house of the matter, the parties, and the significators.

The classifier is a transparent keyword/rule table (no statistics, no LLM). It never decides alone: it proposes one or more
readings of the question with the words that triggered them, flags what is ambiguous or outside the product's limits, and
the user confirms or corrects the reading before any chart is judged. A confirmed reading (`Frame`) is what the judgment uses.

Houses follow Lilly (Christian Astrology, Book II): querent = 1st house and its lord, with the Moon as co-significator
(lilly.method.querent_significators, lilly.method.moon_cosignificator); the matter = the house it belongs to; a matter of
another person is read from that person's house taken as an ascendant (lilly.method.derived_houses).
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field, asdict

# ------------------------------------------------------------------ catalogue

PARTIES = {   # who the matter belongs to -> their house counted from the querent's ascendant (Lilly's house meanings)
    "self":    {"house": 1,  "vi": "chính người hỏi"},
    "sibling": {"house": 3,  "vi": "anh chị em"},
    "father":  {"house": 4,  "vi": "cha"},
    "child":   {"house": 5,  "vi": "con"},
    "employee": {"house": 6, "vi": "người làm thuê / cấp dưới"},
    "partner": {"house": 7,  "vi": "vợ/chồng, người yêu, đối tác hoặc đối phương"},
    "mother":  {"house": 10, "vi": "mẹ"},
    "friend":  {"house": 11, "vi": "bạn bè"},
}

TOPICS: dict[str, dict] = {
    "career": {"vi": "Sự nghiệp", "subtypes": {
        "obtain_post": {"vi": "Có được công việc / vị trí / chức vụ mong muốn không", "house": 10,
                        "rules": ["lilly.topic.career.office"]},
        "promotion": {"vi": "Có được thăng chức không", "house": 10, "rules": ["lilly.topic.career.office"]},
        "keep_post": {"vi": "Có giữ được công việc hiện tại không", "house": 10, "rules": ["lilly.topic.career.continue"]},
    }},
    "finance": {"vi": "Tài chính", "caution": "finance", "subtypes": {
        "gain": {"vi": "Có thu được khoản tiền / lợi nhuận đang mong không", "house": 2, "rules": ["lilly.topic.money.gain"]},
        "loan_back": {"vi": "Có đòi lại được tiền đã cho vay không", "house": 8, "rules": ["lilly.topic.money.lent"]},
        "deal": {"vi": "Một giao dịch / khoản đầu tư sẽ diễn biến thế nào (tiền của mình)", "house": 2,
                 "rules": ["lilly.topic.money.gain"]},
    }},
    "business": {"vi": "Kinh doanh", "caution": "finance", "subtypes": {
        "partnership": {"vi": "Hợp tác với một người / đối tác có thành không", "house": 7, "rules": ["lilly.topic.business.partnership"]},
        "contract": {"vi": "Hợp đồng / thỏa thuận với bên kia có ký được không", "house": 7, "rules": ["lilly.topic.business.contract"]},
        "buy_sell": {"vi": "Có mua / bán được món hàng không", "house": 7, "rules": ["lilly.topic.business.buy_sell"]},
        "rival": {"vi": "Cạnh tranh với một đối thủ cụ thể", "house": 7, "rules": ["lilly.topic.business.adversary"]},
    }},
    "love": {"vi": "Tình cảm", "subtypes": {
        "relationship": {"vi": "Mối quan hệ có tiến tới không", "house": 7, "rules": ["lilly.topic.love.marriage"]},
        "marriage": {"vi": "Có kết hôn với người này không", "house": 7, "rules": ["lilly.topic.love.marriage"]},
        "reconcile": {"vi": "Có làm lành / quay lại được không", "house": 7, "rules": ["lilly.topic.love.reconcile"]},
    }},
    "study": {"vi": "Học tập", "subtypes": {
        "exam": {"vi": "Có đỗ kỳ thi này không", "house": 10, "rules": ["lilly.topic.study.none"]},
        "admission": {"vi": "Có được nhận vào trường / khóa học không", "house": 9, "rules": ["lilly.topic.study.none"]},
        "scholarship": {"vi": "Có được học bổng không", "house": 10, "rules": ["lilly.topic.study.none"]},
    }},
    "property": {"vi": "Nhà đất", "caution": "finance", "subtypes": {
        "buy": {"vi": "Có mua được nhà / đất này không", "house": 4, "rules": ["lilly.topic.property.buy_sell"]},
        "sell": {"vi": "Có bán được nhà / đất không", "house": 4, "rules": ["lilly.topic.property.buy_sell"]},
        "rent": {"vi": "Có thuê được / nên thuê nơi này không", "house": 4, "rules": ["lilly.topic.property.rent"]},
        "move": {"vi": "Chuyển nơi ở có tốt không", "house": 4, "rules": ["lilly.topic.property.remove"]},
    }},
    "lost": {"vi": "Đồ vật thất lạc", "subtypes": {
        "lost_item": {"vi": "Đồ bị thất lạc có tìm lại được không, ở đâu", "house": 2, "rules": ["lilly.topic.lost.goods"]},
        "stolen": {"vi": "Đồ bị lấy cắp có lấy lại được không", "house": 2, "rules": ["lilly.topic.lost.theft"]},
    }},
    "travel": {"vi": "Du lịch / đi xa", "subtypes": {
        "short_trip": {"vi": "Chuyến đi gần có suôn sẻ không", "house": 3, "rules": ["lilly.topic.travel.short"]},
        "long_trip": {"vi": "Chuyến đi xa / ra nước ngoài có thuận không", "house": 9, "rules": ["lilly.topic.travel.long"]},
        "plan_change": {"vi": "Kế hoạch đi có bị trở ngại / thay đổi không", "house": 9, "rules": ["lilly.topic.travel.long"]},
    }},
}

# outside the product's limits: classified, explained, never judged
RESTRICTED = {
    "health": {"vi": "sức khỏe, bệnh tật, phẫu thuật, thuốc men",
               "why": "Thiên Bàn không luận đoán bệnh tật hay kết quả điều trị. Hãy hỏi bác sĩ hoặc cơ sở y tế."},
    "death": {"vi": "sống chết, tuổi thọ, tai nạn",
              "why": "Thiên Bàn không đưa ra dự đoán về sự sống, cái chết hay tai nạn của bất kỳ ai."},
    "pregnancy": {"vi": "mang thai, sinh nở, giới tính thai nhi",
                  "why": "Thiên Bàn không luận đoán về thai sản. Hãy hỏi bác sĩ sản khoa."},
    "legal": {"vi": "kết quả vụ kiện, án phạt, tù tội, tranh chấp pháp lý",
              "why": "Thiên Bàn không dự đoán kết quả pháp lý. Hãy hỏi luật sư hoặc cơ quan có thẩm quyền."},
    "third_party_private": {"vi": "theo dõi, kiểm tra đời tư của người khác (ngoại tình, nơi ở, bí mật)",
                            "why": "Thiên Bàn không luận về đời tư của một người khác không đặt câu hỏi."},
}

CAUTIONS = {
    "finance": "Đây không phải lời khuyên tài chính hay đầu tư. Quyết định tiền bạc cần dựa trên thông tin thực tế, "
               "và nếu cần thì hỏi chuyên gia tài chính có giấy phép.",
}

# ------------------------------------------------------------------ keyword rules (Vietnamese; matched without diacritics)


def fold(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower().replace("đ", "d").replace("Đ", "d"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip()


# (topic, subtype, pattern) - patterns are on the folded text; \b word edges
KEYWORDS: list[tuple[str, str, str]] = [
    ("career", "obtain_post", r"\b(xin (duoc )?viec|co duoc viec|duoc viec|kiem duoc viec|phong van|trung tuyen|duoc nhan vao (lam|cong ty)|nhan viec|offer|ung tuyen|vi tri|cong viec moi|duoc tuyen)\b"),
    ("career", "promotion", r"\b(thang chuc|len chuc|bo nhiem|thang tien|tang luong|len luong)\b"),
    ("career", "keep_post", r"\b(giu duoc (viec|cong viec|chuc)|bi (sa thai|cho nghi|duoi viec)|mat viec|nghi viec)\b"),
    ("career", "obtain_post", r"\b(chuyen viec|nhay viec|doi viec)\b"),
    ("finance", "gain", r"\b(thu duoc tien|kiem duoc tien|co tien|loi nhuan|thu nhap|lam giau|duoc thuong)\b"),
    ("finance", "loan_back", r"\b(doi (duoc )?no|tra no|cho (\w+ )?vay|doi lai tien|lay lai tien|no tien)\b"),
    ("finance", "deal", r"\b(dau tu|chung khoan|co phieu|crypto|tien ao|giao dich|thuong vu|lai lo|sinh loi)\b"),
    ("business", "partnership", r"\b(hop tac|hun von|gop von|lam an chung|doi tac|lien doanh)\b"),
    ("business", "contract", r"\b(hop dong|ky ket|thoa thuan|deal|chot don|ky duoc)\b"),
    ("business", "buy_sell", r"\b(ban duoc|mua duoc|ban hang|mua ban|ban (xe|do|lo hang|hang))\b"),
    ("business", "rival", r"\b(doi thu|canh tranh|thau|dau thau)\b"),
    ("love", "relationship", r"\b(nguoi yeu|tinh cam|yeu nhau|hen ho|crush|thich (anh|em|co|chi)|moi quan he|tien toi)\b"),
    ("love", "marriage", r"\b(ket hon|cuoi (anh|em|co|chi|nhau|vo|chong)|dam cuoi|lay (anh|em|co|chi|nhau|chong|vo)|hon nhan|cau hon)\b"),
    ("love", "reconcile", r"\b(lam lanh|quay lai|tai hop|hoa giai|nong lai|lien lac lai)\b"),
    ("study", "exam", r"\b(ky thi|do (ky thi|dai hoc|tot nghiep|bang|chung chi)|thi (dau|do|truot|dat)|dau (dai hoc|ky thi)|truot|diem thi|bao ve luan an|ielts|toefl)\b"),
    ("study", "admission", r"\b(nhap hoc|trung tuyen (truong|dai hoc)|duoc nhan vao truong|du hoc|vao truong|ho so (truong|du hoc))\b"),
    ("study", "scholarship", r"\b(hoc bong)\b"),
    ("property", "buy", r"\b(mua (duoc )?(nha|dat|can ho|chung cu|manh dat|lo dat)|dat coc (nha|dat|can ho))\b"),
    ("property", "sell", r"\b(ban (duoc )?(nha|dat|can ho|chung cu|manh dat|lo dat))\b"),
    ("property", "rent", r"\b(thue (nha|phong|can ho|mat bang)|cho thue)\b"),
    ("property", "move", r"\b(chuyen nha|don nha|chuyen cho o|doi cho o|chuyen den)\b"),
    ("lost", "lost_item", r"\b(mat (chiec|cai|cuon|vi|dien thoai|chia khoa|giay to|do|nhan|dong ho|tui|the|so|meo|cho)|that lac|danh roi|de quen|bo quen|tim (lai )?(duoc|thay) (chiec|cai|cuon|vi|dien thoai|chia khoa|giay to|do|nhan|meo|cho)|khong thay (dau|dau ca))\b"),
    ("lost", "stolen", r"\b(bi trom|bi lay cap|bi cuop|ke trom|mat trom)\b"),
    ("travel", "short_trip", r"\b(di cong tac|chuyen di|ve que|di (choi|ve) (gan|cuoi tuan))\b"),
    ("travel", "long_trip", r"\b(di xa|ra nuoc ngoai|xuat canh|visa|dinh cu|chuyen bay|du lich|chuyen di)\b"),
    ("travel", "plan_change", r"\b(hoan chuyen|huy chuyen|doi lich (bay|di)|tro ngai chuyen di)\b"),
]

PRECEDENCE = [(("business", "buy_sell"), ("property", "buy")), (("business", "buy_sell"), ("property", "sell")),
              (("love", "relationship"), ("love", "marriage")), (("love", "relationship"), ("love", "reconcile")),
              (("finance", "gain"), ("finance", "loan_back"))]

RESTRICTED_KEYWORDS: list[tuple[str, str]] = [
    ("health", r"\b(benh|om|ung thu|phau thuat|mo (tim|nao|ruot)|thuoc|chua khoi|nhap vien|xet nghiem|suc khoe|tri lieu)\b"),
    ("death", r"\b(chet|qua doi|mat (som|di)|tho bao lau|song duoc|tai nan|tu vong)\b"),
    ("pregnancy", r"\b(co thai|mang thai|bau|sinh con|sinh trai|sinh gai|vo sinh|sinh no)\b"),
    ("legal", r"\b(kien|vu an|toa an|bi bat|ngoi tu|an phat|xu an|thang kien|thua kien|tranh chap)\b"),
    ("third_party_private", r"\b(ngoai tinh|lua doi|phan boi|co nguoi khac|theo doi|bi mat cua)\b"),
]

# Kinship words are matched WITH diacritics when the question has them: folded, "bỏ tôi" (left me) reads as "bo toi" (my
# father) and "mà tôi" as "ma toi". Unaccented questions use the folded list, which keeps only unambiguous phrases.
# words that only mean something with their diacritics ("mổ" = surgery, "mở" = open): matched on the accented text
RESTRICTED_ACCENTED: list[tuple[str, str]] = [
    ("health", r"(\bmổ\b|phẫu thuật|\bốm\b|bệnh|đi khám|khám bệnh|chữa bệnh|chữa trị|chữa khỏi|uống thuốc|nằm viện|nhập viện|bệnh viện|sức khỏe|sức khoẻ)"),
    ("death", r"(chết|qua đời|mất sớm|tử vong|sống được|thọ)"),
    ("pregnancy", r"(có thai|mang thai|có bầu|sinh con|sảy thai)"),
    ("legal", r"(kiện|tòa|toà án|bị bắt|ngồi tù|án phạt|xử án)"),
]

PARTY_KEYWORDS: list[tuple[str, str]] = [
    ("sibling", r"(anh trai|chị gái|em trai|em gái|anh chị em|chị ruột|anh ruột|em ruột)"),
    ("father", r"(bố tôi|cha tôi|bố em|ba tôi|bố mình|cha mình|ba mình)"),
    ("mother", r"(mẹ tôi|mẹ em|mẹ mình|má tôi)"),
    ("child", r"(con tôi|con em|con trai tôi|con gái tôi|con mình|đứa con)"),
    ("friend", r"(bạn tôi|bạn thân|người bạn|bạn em|bạn mình)"),
    ("employee", r"(nhân viên của tôi|cấp dưới|người làm của)"),
]
PARTY_KEYWORDS_FOLDED: list[tuple[str, str]] = [
    ("sibling", r"\b(anh trai|chi gai|em trai|em gai|anh chi em)\b"),
    ("mother", r"\b(me toi|me em|me minh)\b"),
    ("child", r"\b(con trai toi|con gai toi)\b"),
    ("friend", r"\b(ban than)\b"),
]

FORM = [   # what kind of answer is asked; horary judges "will it happen", "where", "when", "how"
    ("should", r"\b(co nen|nen hay khong|nen (chon|lam|di|mua|ban))\b"),
    ("when", r"\b(khi nao|bao gio|luc nao|bao lau nua)\b"),
    ("where", r"\b(o dau|cho nao|huong nao)\b"),
    ("yesno", r"\b(co .* khong|duoc khong|khong\??$|hay khong)\b"),
]


@dataclass
class Reading:
    topic: str
    subtype: str
    party: str
    querent_house: int
    quesited_house: int
    matched: list[str]
    note: str = ""

    def as_dict(self):
        return asdict(self)


@dataclass
class Classification:
    text: str
    readings: list[Reading]
    restricted: list[dict]
    form: list[str]
    ambiguous: bool
    reasons: list[str] = field(default_factory=list)
    needs_confirmation: bool = True

    def as_dict(self):
        return asdict(self) | {"readings": [r.as_dict() for r in self.readings]}


def derived(party_house: int, topic_house: int) -> int:
    """The topic_house-th house counted from party_house taken as the 1st (Lilly's turned chart)."""
    return (party_house - 1 + topic_house - 1) % 12 + 1


def classify(text: str) -> Classification:
    t = fold(text)
    reasons: list[str] = []
    if len(t) < 8:
        return Classification(text, [], [], [], True, ["Câu hỏi quá ngắn để hiểu; hãy viết rõ việc gì, của ai."])
    restricted = [{"kind": k, **RESTRICTED[k], "matched": m.group(0)} for k, rx in RESTRICTED_KEYWORDS if (m := re.search(rx, t))]
    low = text.lower()
    for k, rx in RESTRICTED_ACCENTED:
        if k not in {r["kind"] for r in restricted} and (m := re.search(rx, low)):
            restricted.append({"kind": k, **RESTRICTED[k], "matched": m.group(0)})
    hits: dict[tuple[str, str], list[str]] = {}
    for topic, sub, rx in KEYWORDS:
        for m in re.finditer(rx, t):
            hits.setdefault((topic, sub), []).append(m.group(0))
    party = "self"
    accented = fold(text) != re.sub(r"\s+", " ", text.lower()).strip()
    plist, ptext = (PARTY_KEYWORDS, text.lower()) if accented else (PARTY_KEYWORDS_FOLDED, t)
    party_hits = [(p, m.group(0)) for p, rx in plist if (m := re.search(rx, ptext))]
    if len({p for p, _ in party_hits}) > 1:
        reasons.append("Câu hỏi nhắc tới nhiều người (" + ", ".join(w for _, w in party_hits) + "): hãy chọn việc này là của ai.")
    elif party_hits:
        party = party_hits[0][0]
    for loser, winner in PRECEDENCE:                  # a more specific reading of the same words wins
        if loser in hits and winner in hits:
            del hits[loser]
    readings = []
    for (topic, sub), words in sorted(hits.items(), key=lambda kv: -len(kv[1])):
        th = TOPICS[topic]["subtypes"][sub]["house"]
        ph = PARTIES[party]["house"]
        note = ""
        # a partner-topic about the partner's matter would double-count: love/partnership questions are already 7th-house
        qh = th if party == "self" else derived(ph, th)
        if party != "self":
            note = f"Việc của {PARTIES[party]['vi']}: nhà {th} tính từ nhà {ph} (nhà của người đó) = nhà {qh} của lá số."
        readings.append(Reading(topic, sub, party, 1, qh, words, note))
    form = [f for f, rx in FORM if re.search(rx, t)]
    topics = {r.topic for r in readings}
    if not readings and not restricted:
        reasons.append("Không nhận ra chủ đề; hãy chọn chủ đề và loại câu hỏi.")
    if len(topics) > 1:
        reasons.append("Câu hỏi có thể thuộc nhiều chủ đề (" + ", ".join(TOPICS[x]["vi"] for x in topics) + "): hãy chọn một.")
    if "should" in form:
        reasons.append("Câu hỏi dạng 'có nên…': chiêm tinh vấn sự xem việc có thành hay không và diễn biến ra sao; "
                       "quyết định nên hay không vẫn là của bạn. Có thể đổi thành 'việc … có thành không'.")
    if re.search(r"\b(va|hoac|hay la)\b.*\b(khong)\b.*\b(va|hoac)\b", t):
        reasons.append("Câu hỏi gồm nhiều việc; mỗi lá số chỉ nên hỏi một việc.")
    ambiguous = bool(reasons) or len(readings) != 1
    return Classification(text, readings, restricted, form, ambiguous, reasons)


@dataclass
class Frame:
    """A confirmed reading of the question: the only input the judgment accepts."""
    text: str
    topic: str
    subtype: str
    party: str = "self"
    quesited_house: int | None = None          # override only when the user picks it explicitly
    confirmed: bool = False

    def resolve(self) -> dict:
        if self.topic not in TOPICS or self.subtype not in TOPICS[self.topic]["subtypes"]:
            raise ValueError("chủ đề hoặc loại câu hỏi không hợp lệ")
        if self.party not in PARTIES:
            raise ValueError("người liên quan không hợp lệ")
        st = TOPICS[self.topic]["subtypes"][self.subtype]
        th = st["house"]
        ph = PARTIES[self.party]["house"]
        qh = self.quesited_house or (th if self.party == "self" else derived(ph, th))
        return {"topic": self.topic, "subtype": self.subtype, "party": self.party, "topic_vi": TOPICS[self.topic]["vi"],
                "subtype_vi": st["vi"], "querent_house": 1, "party_house": ph, "quesited_house": qh, "rules": st["rules"],
                "caution": CAUTIONS.get(TOPICS[self.topic].get("caution", "")),
                "derived_note": None if self.party == "self" else
                f"Việc của {PARTIES[self.party]['vi']}: nhà {th} tính từ nhà {ph} = nhà {qh} (lilly.method.derived_houses)."}


def ruler_of_house(chart, house: int) -> str:
    """Lord of the sign on the cusp (lilly.significator.lord_of_house)."""
    from . import dignity
    return dignity.table()[dignity.sign_of(chart.cusps[house - 1])]["house"]


def significators(chart, frame: dict) -> dict:
    q1 = ruler_of_house(chart, frame["querent_house"])
    q2 = ruler_of_house(chart, frame["quesited_house"])
    out = {"querent": {"planet": q1, "house": 1, "rule": "lilly.significator.lord_of_house"},
           "quesited": {"planet": q2, "house": frame["quesited_house"], "rule": "lilly.significator.lord_of_house"},
           "moon": {"planet": "moon", "role": "co-significator of the querent", "rule": "lilly.method.moon_cosignificator"},
           "same_ruler": q1 == q2}
    if frame["party"] != "self":
        out["party"] = {"planet": ruler_of_house(chart, frame["party_house"]), "house": frame["party_house"]}
    if frame["topic"] == "lost":
        out["fortune"] = {"point": "fortune", "lon": chart.fortune, "rule": "lilly.topic.lost.goods"}
    return out
