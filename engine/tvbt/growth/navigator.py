"""'Khi cuộc đời bế tắc': a guided self-assessment. The reader names the problem, sorts concerns into kiểm soát được / ảnh hưởng được /
ngoài tầm tay, and gets the right questions — the generic method plus chart-specific prompts. The engine never sorts for the reader:
for items marked 'chưa rõ' it only offers a keyword HINT, labelled as such."""
from __future__ import annotations

from . import kb
from .text import clip, fold, hits

ZONES = {"control": "Kiểm soát được", "influence": "Ảnh hưởng được", "outside": "Ngoài tầm tay", "unsure": "Chưa rõ"}
# explicit, reviewable hint lists (folded); a hint is never a classification
HINT_OUTSIDE = ["thi truong", "kinh te", "thoi tiet", "qua khu", "nguoi khac nghi", "chinh sach", "dich benh", "tuoi tac", "di truyen", "so phan", "ho nghi", "sep quyet"]
HINT_CONTROL = ["toi se", "minh se", "thoi quen", "lich trinh", "hoc them", "luyen tap", "giac ngu", "chi tieu", "cua toi", "cua minh", "cach toi", "cach minh", "thoi gian"]
HINT_INFLUENCE = ["sep toi", "dong nghiep", "vo toi", "chong toi", "ban be", "con toi", "bo me", "khach hang", "doi nhom", "nguoi yeu", "gia dinh"]


def safety(text: str) -> dict | None:
    D = kb.load("dialogue")
    if hits(text, D["crisis"]):
        return {"kind": "crisis", **D["crisis_reply"]}
    return None


def _hint(text: str) -> tuple[str, str] | None:
    for zone, keys in (("outside", HINT_OUTSIDE), ("control", HINT_CONTROL), ("influence", HINT_INFLUENCE)):
        h = hits(text, keys)
        if h:
            return zone, h[0]
    return None


def _pattern_hits(profile: dict, text: str) -> list[dict]:
    out = []
    for b in profile["blind_spots"]:
        h = hits(text, b.get("signal_words") or [])
        if h:
            out.append({"insight": b["id"], "title": b["title"], "words": h,
                        "text": f"Cách bạn mô tả có vài từ gần với mô thức '{b['shadow']['habit']}' (đã nêu ở mục Điểm mù). Đây chỉ là gợi ý để bạn tự kiểm tra, không phải kết luận."})
    return out


def navigate(profile: dict, domain: str, situation: str, concerns: list[dict], duration: str = "", tried: str = "") -> dict:
    C, D = kb.load("concepts"), kb.load("dialogue")
    domain = domain if domain in C["domain_questions"] else "self"
    all_text = " ".join([situation, tried] + [c.get("text", "") for c in concerns])
    s = safety(all_text)
    if s:
        return {"safety": s}
    zones = {z: [] for z in ZONES}
    for c in concerns[:20]:
        z = c.get("zone") if c.get("zone") in ZONES else "unsure"
        item = {"text_user": clip(c.get("text", ""), 160)}
        if z == "unsure":
            h = _hint(c.get("text", ""))
            if h:
                item["hint"] = {"zone": h[0], "label": ZONES[h[0]], "because": h[1],
                                "note": "Gợi ý dựa trên từ khóa, chỉ để bạn cân nhắc. Bạn là người quyết định mục này thuộc cột nào."}
        zones[z].append(item)
    steps = [{**st, "concept": kb.concept(st["concept"])} for st in C["stuck_steps"]]
    chart_q = []
    for it in profile["lessons"] + profile["blind_spots"]:
        if domain in it["domains"] and it.get("palace"):
            chart_q.append({"from": it["title"], "question": it["exercise"]["questions"][0], "insight": it["id"]})
    top = profile["blind_spots"][0] if profile["blind_spots"] else None
    if top:
        chart_q.append({"from": top["title"], "question": top["exercise"]["questions"][0], "insight": top["id"]})
    pats = _pattern_hits(profile, all_text)
    linked = {p["insight"] for p in pats}
    acts = [p for p in profile["practices"] if p["insight"] in linked] + [p for p in profile["practices"] if domain in p["domains"] and p["insight"] not in linked]
    notes = []
    if hits(all_text, D["distress"]) or fold(duration) in ("tren 6 thang", "nhieu nam"):
        notes.append(D["distress_note"])
    focus = [z for z in ("control", "influence") if zones[z]]
    summary = (f"Bạn có {len(zones['control'])} mục kiểm soát được, {len(zones['influence'])} mục ảnh hưởng được, {len(zones['outside'])} mục ngoài tầm tay"
               + (f" và {len(zones['unsure'])} mục chưa rõ" if zones["unsure"] else "") + ". "
               + ("Năng lượng nên đi vào cột " + " và ".join(ZONES[z].lower() for z in focus) + "." if focus else
                  "Chưa có mục nào ở cột kiểm soát được hay ảnh hưởng được; hãy thử tìm một bước nhỏ nhất bạn làm được, dù chỉ là hỏi thêm thông tin."))
    return {"domain": domain, "domain_label": C["domains"].get(domain, {}).get("label", "Sức khỏe" if domain == "health" else domain),
            "echo": clip(situation, 300), "steps": steps, "zones": zones, "zone_labels": ZONES, "summary": summary,
            "bias_check": profile["control_bias"], "domain_questions": C["domain_questions"][domain], "chart_questions": chart_q[:4],
            "pattern_hits": pats, "actions": acts[:3], "stage": profile["stage"], "notes": notes,
            "reminder": "Đây là khung để bạn tự đánh giá. Lá số không cho biết vấn đề sẽ kết thúc ra sao; điều bạn chọn làm tiếp theo mới là phần quyết định."}
