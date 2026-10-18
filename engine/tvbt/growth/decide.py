"""'La bàn cuộc đời': a decision mirror. The reader brings the decision, the options, their own values and their own 1–5 ratings; the engine
lays out chart-based tendencies to check against, value overlap, the ratings they gave (summed, never weighted by the chart) and decision
tools. It never names a preferred option."""
from __future__ import annotations

from . import kb
from .navigator import safety
from .text import clip


def decide(profile: dict, domain: str, decision: str, options: list[str], values: list[str], ratings: dict) -> dict:
    C = kb.load("concepts")
    s = safety(" ".join([decision] + options))
    if s:
        return {"safety": s}
    domain = domain if domain in profile["compass"] else "career"
    cp = profile["compass"][domain]
    vals = [v for v in values if v in C["values"]][:5]
    chart_vals = [v["id"] for v in cp["chart_values"]]
    both, only_chart, only_user = [v for v in vals if v in chart_vals], [v for v in chart_vals if v not in vals], [v for v in vals if v not in chart_vals]
    lab = lambda vs: [C["values"][v] for v in vs]
    refl = []
    if both:
        refl.append(f"Giá trị bạn chọn trùng với những giá trị hình tượng lá số nghiêng về: {', '.join(lab(both))}. Đây có thể là chỗ bạn vững nhất khi quyết định.")
    if only_user:
        refl.append(f"Bạn chọn {', '.join(lab(only_user))} — những giá trị không nằm trong hình tượng lá số. Hãy tin lựa chọn của bạn: giá trị là điều bạn chọn sống theo, không phải điều lá số quy định.")
    if only_chart:
        refl.append(f"Hình tượng lá số nghiêng về {', '.join(lab(only_chart))} mà bạn không chọn. Câu hỏi để soi: những giá trị này có đang âm thầm kéo quyết định của bạn không, hay bạn đã thật sự đặt chúng xuống?")
    opts = [clip(o, 80) for o in options if o.strip()][:4]
    matrix = []
    for o in opts:
        r = ratings.get(o) or {}
        row = {"option": o, "scores": {v: max(1, min(5, int(r[v]))) for v in vals if v in r and str(r[v]).isdigit()}}
        row["total"] = sum(row["scores"].values())
        row["rated"] = len(row["scores"])
        matrix.append(row)
    notes = []
    if len(matrix) >= 2 and all(m["rated"] == len(vals) and vals for m in matrix):
        ts = sorted((m["total"] for m in matrix), reverse=True)
        if ts[0] - ts[1] <= max(1, round(0.1 * ts[0])):
            notes.append("Tổng điểm do chính bạn chấm giữa các lựa chọn gần nhau. Khi các con số gần nhau, chúng không giúp phân định; câu hỏi 10–10–10 hoặc một bước thử nhỏ có thể cho bạn thêm thông tin.")
        else:
            notes.append("Một lựa chọn có tổng điểm cao hơn theo chính cách bạn chấm. Trước khi dựa vào con số, hãy đọc lại phần 'xu hướng cần kiểm tra' bên dưới: điểm số có thể phản ánh thói quen cũ chứ không chỉ giá trị.")
    tools = []
    for t in C["decision_tools"]:
        tools.append({"id": t["id"], "concept": kb.concept(t["concept"]), "prompt": t["prompt"]})
    bias = [{"from": t["from"], "text": t["text"]} for t in cp["tendencies"]]
    return {"domain": domain, "domain_label": cp["label"], "echo": clip(decision, 300), "options": opts,
            "values": [{"id": v, "label": C["values"][v]} for v in vals], "values_reflection": refl, "matrix": matrix,
            "matrix_note": "Bảng chỉ cộng điểm do bạn tự chấm cho từng giá trị bạn chọn; lá số không cộng hay trừ điểm vào đây.",
            "tendencies_to_check": bias, "anchors": cp["anchors"], "questions": cp["questions"], "tools": tools, "notes": notes,
            "ownership": "Quyết định này là của bạn. Hệ thống chỉ đặt các yếu tố cạnh nhau để bạn nhìn rõ hơn; nó không chọn và không biết lựa chọn nào sẽ 'đúng'."}
