"""'Đối thoại với lá số': deterministic question answering over the growth profile plus what the reader shares about their situation.
No language model: intent and domain come from reviewable keyword tables (data/growth/dialogue.json); the answer is assembled from the
reader's own profile, each paragraph labelled with the layer it belongs to. Order of checks: crisis -> fate/decision boundary -> intent.
`exclude` lets the client rotate: insights already used in this conversation are offered last."""
from __future__ import annotations

from . import kb
from .navigator import _pattern_hits, safety
from .text import clip, hits

LAYER = {"tu_ban": "Từ điều bạn chia sẻ", "bieu_tuong": "Biểu tượng truyền thống", "tam_ly": "Góc nhìn tâm lý học", "doi_song": "Đời sống thực",
         "thu": "Thử trong 7–30 ngày", "ranh_gioi": "Giới hạn của lá số", "an_toan": "An toàn của bạn"}


def _p(layer: str, text: str, **kw) -> dict:
    return {"layer": layer, "label": LAYER[layer], "text": text, **kw}


def _detect(table: dict, text: str, default=None):
    best, n = default, 0
    for k, keys in table.items():
        h = len(hits(text, keys))
        if h > n:
            best, n = k, h
    return best


def _rank(items: list[dict], domain: str | None, text: str, exclude: set) -> list[dict]:
    def key(it):
        hit = bool(hits(text, it.get("signal_words") or []))
        dom = 2 if domain and domain in it["domains"] else (1 if "self" in it["domains"] else 0)
        return (it["id"] in exclude, not hit, -dom, -it["priority"])
    return sorted(items, key=key)


def _insight_paras(it: dict) -> list[dict]:
    L = it["layers"]
    out = [_p("bieu_tuong", L["bieu_tuong"]["text"] + (f" [{'; '.join(L['bieu_tuong']['cites'])}]" if L["bieu_tuong"]["cites"] else "") +
              f" ({L['bieu_tuong']['source_label']})", insight=it["id"]),
           _p("tam_ly", f"{L['tam_ly']['concept']['name']}: {L['tam_ly']['text']} ({L['tam_ly']['concept']['ref']}). {L['tam_ly']['note']}", insight=it["id"]),
           _p("doi_song", L["doi_song"]["text"], insight=it["id"])]
    return out


def _practice_para(it: dict) -> dict:
    p = it["exercise"]["practices"][0]
    return _p("thu", f"{p['days']} ngày: {p['action']} Cách theo dõi: {p['track']}", insight=it["id"], practice=f"{it['id']}#0")


def answer(profile: dict, question: str, context: dict | None = None, exclude: list[str] | None = None) -> dict:
    D, C = kb.load("dialogue"), kb.load("concepts")
    ctx = context or {}
    situation = ctx.get("situation") or ""
    text = f"{question} {situation}"
    ex = set(exclude or [])
    s = safety(text)
    if s:
        return {"intent": "crisis", "boundary": "crisis", "reply": [_p("an_toan", s["text"])], "follow_up": s["follow_up"], "grounding": []}
    domain = ctx.get("domain") if ctx.get("domain") in C["domain_questions"] else _detect(D["domains"], text)
    intent = _detect(D["intents"], question)
    reply, grounding, follow = [], [], []
    if situation.strip():
        reply.append(_p("tu_ban", f"Bạn chia sẻ: «{clip(situation, 220)}». Câu trả lời dưới đây dựa trên điều đó cùng với lá số; nếu chỗ nào không khớp, hoàn cảnh thật của bạn được ưu tiên.",
                        echo=clip(situation, 220)))
    if hits(question, D["fate"]["decision_patterns"]):
        reply.append(_p("ranh_gioi", D["fate"]["decision_reply"]))
        intent = intent or "change_what"
        boundary = "decision"
    elif hits(question, D["fate"]["patterns"]):
        reply.append(_p("ranh_gioi", D["fate"]["reply"]))
        boundary = "fate"
        if intent is None:
            return {"intent": "fate", "boundary": boundary, "domain": domain, "reply": reply, "grounding": [],
                    "follow_up": ["Điều bạn thực sự mong muốn ở chuyện này là gì?", "Điều gì trong chuyện này nằm trong tay bạn?"]}
    else:
        boundary = None
    if intent is None:
        if not situation.strip():
            return {"intent": "unknown", "boundary": boundary, "domain": domain, "reply": reply + [_p("doi_song", D["unknown_reply"])], "grounding": [], "follow_up": []}
        intent = "stuck_why"
    pats = _pattern_hits(profile, text)
    ls, bs = profile["lessons"], profile["blind_spots"]
    if intent in ("stuck_why", "blind", "meaning"):
        it = _rank(bs, domain, text, ex)[0] if bs else None
        if it:
            grounding.append(it["id"])
            reply.append(_p("doi_song", f"Một mô thức có thể liên quan (theo lá số): {it['title']}.", insight=it["id"]))
            reply += _insight_paras(it)
            sh = it.get("shadow")
            if sh:
                reply.append(_p("doi_song", "Dấu hiệu để tự nhận diện: " + "; ".join(sh["signals"]) + ".", insight=it["id"]))
            reply.append(_practice_para(it))
            follow += it["exercise"]["questions"][:2]
        if intent == "meaning" and ls:
            l0 = _rank(ls, domain, text, ex)[0]
            grounding.append(l0["id"])
            reply.append(_p("doi_song", f"Bài học nổi bật nhất trong hồ sơ của bạn: {l0['title']}. {l0['layers']['doi_song']['text']}", insight=l0["id"]))
    elif intent == "change_what":
        it = _rank(ls, domain, text, ex)[0] if ls else None
        if it:
            grounding.append(it["id"])
            reply.append(_p("doi_song", f"Một hướng thay đổi gắn với lá số: {it['title']}." + (f" Năng lực nên rèn: {it['skill']}." if it.get("skill") else ""), insight=it["id"]))
            reply += _insight_paras(it)
            reply.append(_practice_para(it))
            reply.append(_p("tam_ly", "Viết lại thành một câu 'Khi [tình huống cụ thể], tôi sẽ [hành động nhỏ]'. Kế hoạch dạng này được nghiên cứu cho thấy dễ thành hành động hơn mục tiêu chung chung "
                                      f"({kb.concept('implementation_intention')['ref']})."))
            follow += it["exercise"]["questions"][:2]
    elif intent == "strength":
        gifts = [x for x in _rank(ls, None, text, ex) if x.get("gift")]
        if gifts:
            for g in gifts[:2]:
                grounding.append(g["id"])
                reply.append(_p("bieu_tuong", g["layers"]["bieu_tuong"]["text"], insight=g["id"]))
                reply.append(_p("doi_song", f"Thế mạnh theo hình tượng: {g['gift']}.", insight=g["id"]))
        for h in ("Hóa Lộc", "Hóa Quyền"):
            a = next((x for x in profile["anchors"] if x["id"] == f"hoa.{h}"), None)
            if a:
                pal = a["check"]["palace"]
                reply.append(_p("bieu_tuong", f"{a['text']} Theo truyền thống, đây là nơi {kb.load('palaces')['hoa'][h]['theme']}: {kb.load('palaces')['growth_area'][pal]['area']}."))
        y = next((x for x in ls if x["id"] == "L_BAZI_YONG"), None)
        if y:
            grounding.append(y["id"])
            reply.append(_p("doi_song", y["layers"]["doi_song"]["text"], insight=y["id"]))
        dl = C["domains"].get(domain, {}).get("label")
        reply.append(_p("doi_song", ("Câu hỏi để tìm điểm mạnh chưa tận dụng: " + (f"trong {dl.lower()}, " if dl else "") +
                                     "bạn đã thật sự dùng những thế mạnh trên chưa, hay chỉ dùng chúng ở nơi bạn đã thấy an toàn?")))
        follow += ["Thế mạnh nào người khác hay khen ở bạn mà bạn ít coi trọng?", "Nếu dùng thế mạnh đó ở lĩnh vực đang bế tắc, bước đầu tiên là gì?"]
    cp = profile["compass"].get(domain or "")
    if cp and intent in ("stuck_why", "change_what", "blind"):
        own = [t for t in cp["tendencies"] if "ở cung Mệnh" not in t["from"]][:2]
        if own:
            reply.append(_p("doi_song", f"Riêng về {cp['label'].lower()}, lá số còn gợi ý những xu hướng để bạn tự kiểm tra: " +
                            " ".join(f"({t['from']}) {t['text']}" for t in own), anchors=cp["anchors"]))
    for p in pats:
        if p["insight"] not in grounding:
            reply.append(_p("tu_ban", p["text"], insight=p["insight"]))
    if ctx.get("values"):
        vs = [C["values"][v] for v in ctx["values"] if v in C["values"]]
        if vs:
            reply.append(_p("tu_ban", f"Bạn đã chọn các giá trị: {', '.join(vs)}. Hãy dùng chúng làm tiêu chí khi thử các gợi ý trên; gợi ý nào đi ngược giá trị của bạn thì bỏ qua."))
    if hits(text, D["distress"]):
        reply.append(_p("an_toan", D["distress_note"]))
    if not domain:
        follow.append(D["domain_hint"])
    if domain in C["domain_questions"]:
        follow.append(C["domain_questions"][domain][0])
    return {"intent": intent, "boundary": boundary, "domain": domain, "reply": reply, "grounding": grounding, "follow_up": follow[:4],
            "note": "Câu trả lời được ghép từ hồ sơ lá số của bạn bằng quy tắc cố định, không dùng AI tạo sinh. Hãy coi đây là gợi ý để tự hỏi, không phải lời phán."}
