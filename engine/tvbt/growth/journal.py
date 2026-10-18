"""'Nhật ký trưởng thành': entries live in the reader's browser; this stateless review compares them with the reading and with themselves over
time. Nothing is stored server-side. Resonance ratings are treated as the reader's evidence, which outranks the chart."""
from __future__ import annotations

from datetime import date

from . import kb
from .text import clip, hits

RES = {"dung": "đúng với tôi", "mot_phan": "đúng một phần", "khong": "không đúng với tôi"}


def _d(s: str) -> date | None:
    try:
        return date.fromisoformat(str(s)[:10])
    except ValueError:
        return None


def review(profile: dict, entries: list[dict]) -> dict:
    C = kb.load("concepts")
    es = sorted([e for e in entries if _d(e.get("date"))], key=lambda e: e["date"])[:1000]
    if not es:
        return {"count": 0, "message": "Chưa có ghi chép nào. Hãy bắt đầu bằng một dòng: hôm nay điều gì khiến bạn nghĩ về bản thân?", "barnum": kb.concept("barnum")}
    ins = {i["id"]: i for i in profile["lessons"] + profile["blind_spots"]}
    first, last = _d(es[0]["date"]), _d(es[-1]["date"])
    half = len(es) // 2
    moods = [int(e["mood"]) for e in es if str(e.get("mood", "")).isdigit() and 1 <= int(e["mood"]) <= 5]
    early = [int(e["mood"]) for e in es[:half] if str(e.get("mood", "")).isdigit()] if half else []
    late = [int(e["mood"]) for e in es[half:] if str(e.get("mood", "")).isdigit()]
    trend = None
    if len(early) >= 2 and len(late) >= 2:
        a, b = sum(early) / len(early), sum(late) / len(late)
        trend = {"early": round(a, 2), "late": round(b, 2), "delta": round(b - a, 2),
                 "text": ("Tâm trạng trung bình trong nửa sau nhật ký cao hơn nửa đầu." if b - a >= 0.5 else
                          "Tâm trạng trung bình trong nửa sau nhật ký thấp hơn nửa đầu. Hãy nhẹ nhàng với mình; nếu kéo dài, hãy trò chuyện với người bạn tin hoặc người chuyên môn." if a - b >= 0.5 else
                          "Tâm trạng trung bình tương đối ổn định giữa hai nửa nhật ký.")}
    doms = {}
    for e in es:
        d = e.get("domain") or "self"
        doms[d] = doms.get(d, 0) + 1
    res = {}
    for e in es:
        iid, r = e.get("insight_id"), e.get("resonance")
        if iid in ins and r in RES:
            x = res.setdefault(iid, {"insight": iid, "title": ins[iid]["title"], "dung": 0, "mot_phan": 0, "khong": 0})
            x[r] += 1
    for x in res.values():
        n = x["dung"] + x["mot_phan"] + x["khong"]
        x["verdict"] = ("Mới có một lần đối chiếu; cần thêm vài lần nữa, ở những hoàn cảnh khác nhau, mới thấy được xu hướng." if n < 2 else
                        "Bạn nhiều lần thấy nhận định này đúng với trải nghiệm. Hãy ghi lại hành vi cụ thể, để 'đúng' dựa trên việc đã xảy ra chứ không chỉ cảm giác." if x["dung"] / n >= 0.6 else
                        "Bạn thường thấy nhận định này không đúng. Trải nghiệm của bạn được ưu tiên hơn lá số; có thể bỏ qua nhận định này." if x["khong"] / n >= 0.6 else
                        "Bạn thấy nhận định này đúng một phần. Phần nào đúng, trong hoàn cảnh nào? Đó là phần đáng giữ.")
    prac = {}
    for e in es:
        pid = e.get("practice_id")
        if pid:
            x = prac.setdefault(pid, {"practice": pid, "days_logged": 0, "days_done": 0, "dates": set()})
            x["days_logged"] += 1
            if e.get("practice_done"):
                x["days_done"] += 1
                x["dates"].add(e["date"][:10])
    pmap = {p["id"]: p for p in profile["practices"]}
    for pid, x in prac.items():
        target = pmap.get(pid, {}).get("days")
        ds = sorted(_d(d) for d in x.pop("dates"))
        streak = best = 0
        for i, d in enumerate(ds):
            streak = streak + 1 if i and (d - ds[i - 1]).days == 1 else 1
            best = max(best, streak)
        x.update({"target_days": target, "best_streak": best, "action": pmap.get(pid, {}).get("action"),
                  "text": (f"Đã làm {x['days_done']}/{target} ngày" if target else f"Đã làm {x['days_done']} ngày") + f", chuỗi dài nhất {best} ngày."})
    shifts = []
    if half:
        for iid, b in ins.items():
            words = b.get("signal_words") or []
            if not words:
                continue
            e1 = sum(1 for e in es[:half] if hits(e.get("text", ""), words))
            e2 = sum(1 for e in es[half:] if hits(e.get("text", ""), words))
            if e1 + e2 >= 2:
                shifts.append({"insight": iid, "title": b["title"], "early": e1, "late": e2,
                               "text": ("Những từ gắn với mô thức này xuất hiện ít hơn ở nửa sau nhật ký." if e2 < e1 else
                                        "Những từ gắn với mô thức này xuất hiện nhiều hơn ở nửa sau nhật ký; có thể đây là chủ đề đang cần bạn chú ý." if e2 > e1 else
                                        "Những từ gắn với mô thức này xuất hiện đều ở cả hai nửa nhật ký.")})
    untouched = [{"insight": i["id"], "title": i["title"]} for i in (profile["lessons"] + profile["blind_spots"])[:6] if i["id"] not in res]
    weeks = max(1, ((last - first).days // 7) + 1)
    return {"count": len(es), "from": str(first), "to": str(last), "weeks": weeks, "mood": {"n": len(moods), "trend": trend},
            "domains": [{"domain": d, "label": C["domains"].get(d, {}).get("label", "Sức khỏe" if d == "health" else d), "count": n} for d, n in sorted(doms.items(), key=lambda kv: -kv[1])],
            "resonance": sorted(res.values(), key=lambda x: x["insight"]), "practices": list(prac.values()), "word_shifts": shifts[:6],
            "not_yet_reflected": untouched[:3], "latest": [{"date": e["date"][:10], "echo": clip(e.get("text", ""), 120)} for e in es[-3:]],
            "next_questions": ["Điều gì bạn làm khác đi so với lúc bắt đầu ghi nhật ký?", "Nhận định nào bạn muốn kiểm chứng tiếp trong tháng tới?"],
            "barnum": kb.concept("barnum"),
            "privacy": "Nhật ký chỉ lưu trong trình duyệt của bạn. Bản đánh giá này được tính khi bạn yêu cầu và máy chủ không lưu lại."}
