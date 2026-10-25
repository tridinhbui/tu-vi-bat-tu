"""Synastry reading: Ptolemy IV.7 (friendship from the four places) and IV.5 (marriage from the luminaries)."""
from __future__ import annotations

from .compose import Para, listing, srcs
from .vocab import ASPECT_WITH, P, num

PLACE_VI = {"sun": "Mặt Trời", "moon": "Mặt Trăng", "asc": "cung Mọc", "lot": "Lot of Fortune"}
REL_VI = {"same": "cùng một cung", "sextile": "lục hợp theo cung", "trine": "tam hợp theo cung", "square": "vuông góc theo cung",
          "opposition": "đối nhau", "disjunct": "không nhìn thấy nhau (cách 1 hoặc 5 cung)"}


def build(syn: dict, name_a: str = "người thứ nhất", name_b: str = "người thứ hai", gender_a: str | None = None, gender_b: str | None = None) -> list[dict]:
    pt = syn["ptolemy"]
    paras = []
    rel = {k: v for k, v in pt["places"].items() if v}
    close = [k for k, v in rel.items() if v["relation"] == "same"]
    soft = [k for k, v in rel.items() if v["relation"] in ("trine", "sextile")]
    hard = [k for k, v in rel.items() if v["relation"] in ("opposition", "disjunct")]
    sq = [k for k, v in rel.items() if v["relation"] == "square"]
    lines = [f"{PLACE_VI[k]} của hai người {REL_VI[v['relation']]}" for k, v in rel.items()]
    t = ("Ptolemy so sánh bốn điểm có quyền lớn nhất trong hai lá số, Mặt Trời, Mặt Trăng, cung Mọc và Lot of Fortune, để xét tình bạn hay sự đối nghịch (IV.7). "
         + "Ở đây " + listing(lines) + ". ")
    if close or pt["exchanges"]:
        t += ("Cùng cung hoặc đổi chỗ cho nhau là điều Ptolemy coi là nền của tình thân bền chặt"
              + (f" ({listing([PLACE_VI[k] for k in close])})" if close else "") + ". ")
    if soft:
        t += f"Tam hợp, lục hợp ({listing([PLACE_VI[k] for k in soft])}) cho thiện cảm, nhẹ hơn mức trên. "
    if sq:
        t += f"Vuông góc ({listing([PLACE_VI[k] for k in sq])}) cho những va chạm nhỏ. "
    if hard:
        t += f"Đối nhau hay không nhìn thấy nhau ({listing([PLACE_VI[k] for k in hard])}) là chỗ Ptolemy nói dễ sinh bất đồng lâu dài. "
    kinds = []
    if rel.get("sun") and rel.get("moon") and {rel["sun"]["relation"], rel["moon"]["relation"]} <= {"same", "trine", "sextile"}:
        kinds.append("tình thân do chọn lựa (qua hai sao sáng)")
    if rel.get("lot") and rel["lot"]["relation"] in ("same", "trine", "sextile"):
        kinds.append("sự gắn bó vì việc chung, lợi ích chung (qua Lot)")
    if rel.get("asc") and rel["asc"]["relation"] in ("same", "trine", "sextile"):
        kinds.append("sự gắn bó qua niềm vui hay nỗi khó chung (qua cung Mọc)")
    if kinds:
        t += "Theo ba loại Ptolemy phân biệt, mối quan hệ này nghiêng về " + listing(kinds) + "."
    paras.append(Para("syn.friends", "Hai lá số theo Ptolemy: thân hay nghịch", t.strip(), "hellenistic", srcs("PTOL_TETRA:IV.7 pp.413-415"), [], "overview",
                      steps=["So theo cung (không theo độ): cùng cung, cách 2, 3, 4, 6 cung; cách 1 hoặc 5 cung là 'không nhìn thấy nhau'.",
                             "Lot of Fortune tính theo công thức của Ptolemy cho cả hai (III.10)."]).as_dict())
    lum = pt["luminaries"]
    if gender_a in ("male", "female") and gender_b in ("male", "female") and gender_a != gender_b:
        moon_key = "moon_a-sun_b" if gender_a == "male" else "sun_a-moon_b"
        r = lum[moon_key]
        t2 = (f"Với hôn nhân, Ptolemy xét hai sao sáng của hai lá số và coi trọng nhất Mặt Trăng của người chồng với Mặt Trời của người vợ (IV.5). "
              f"Ở đây hai điểm ấy {REL_VI[r]}. ")
    else:
        rs = [v for v in lum.values()]
        r = "trine" if "trine" in rs else "sextile" if "sextile" in rs else "square" if "square" in rs else rs[0]
        t2 = ("Với hôn nhân, Ptolemy xét hai sao sáng (Mặt Trời, Mặt Trăng) của hai lá số (IV.5); ông coi trọng nhất Mặt Trăng của người chồng với Mặt Trời của người vợ, "
              "nên khi biết giới tính hai người Thiên Bàn sẽ xét đúng cặp ấy. Nhìn chung các cặp sao sáng ở đây " +
              listing([f"{'Mặt Trời' if k.startswith('sun') else 'Mặt Trăng'} người thứ nhất với {'Mặt Trời' if k.endswith('sun_b') else 'Mặt Trăng'} người thứ hai {REL_VI[v]}" for k, v in lum.items()]) + ". ")
    if r in ("trine", "sextile", "same"):
        t2 += "Ptolemy nói khi hai sao sáng hài hòa như vậy thì hôn nhân phần nhiều bền lâu."
    elif r in ("opposition", "square", "disjunct"):
        t2 += "Ptolemy xếp vị trí này vào nhóm dễ chia lìa; đó là một chứng trong nhiều chứng, không phải lời phán quyết."
    paras.append(Para("syn.marriage", "Hai sao sáng theo Ptolemy", t2, "hellenistic", srcs("PTOL_TETRA:IV.5 pp.397-399"), [], "overview").as_dict())
    asp = syn["aspects"][:8]
    if asp:
        t3 = ("Các góc hợp chặt nhất giữa hai lá số: " + listing([f"{P(x['a'])} của người thứ nhất {ASPECT_WITH[x['type']]} {P(x['b'])} của người thứ hai (lệch {num(x['orb'])}°)" for x in asp]) +
              ". Đây là dữ kiện hình học; ý nghĩa của từng cặp hành tinh trong so sánh hai lá số là cách đọc của chiêm tinh hiện đại, chưa có nguồn đã kiểm trong thư viện Thiên Bàn.")
        paras.append(Para("syn.aspects", "Góc hợp giữa hai lá số", t3, "calc", srcs("CONV_ORBS"), [], "deep", tier="calc").as_dict())
    return paras
