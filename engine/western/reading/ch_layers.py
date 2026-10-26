"""Layers 1-3 of the reading: each planet by sign and house, the main aspects, and the cross-chapter synthesis."""
from __future__ import annotations

from .. import dignity
from ..zodiac import ELEMENT, MODALITY, SIGNS, sign_index
from .ch_core import M, described, lilly_condition
from .compose import Para, ev_in, cap, ev_aspect, ev_planet, listing, pick, planet_list, srcs
from .facts import CLASSICAL, Facts
from .vocab import ASPECT_NOUN, ASPECT_WITH, ELEMENT_VI, MODALITY_VI, P, S, num

LILLY_SIGN = {"fire": "nóng và khô, khí chất mật vàng", "earth": "lạnh và khô, khí chất u sầu", "air": "nóng và ẩm, khí chất huyết",
              "water": "lạnh và ẩm, khí chất đàm"}                                  # Lilly p.87 (triplicities) and pp.93-99
LILLY_ASPECT_FULL = {   # Lilly pp.106-107, Ptolemy I.13
    "conjunction": "Lilly nói trùng tụ chỉ được gọi là góc chiếu một cách gượng ép: nó tốt hay xấu tùy hai hành tinh có thân nhau hay không (tr.106); Ptolemy không xếp nó vào các cấu hình.",
    "sextile": "Với Lilly, lục hợp là một lời của tình thân và sự hòa thuận, chỉ nhẹ hơn tam hợp (tr.106); Ptolemy cho nó vào nhóm hài hòa vì hai cung cùng giống (I.13).",
    "trine": "Lilly gọi tam hợp là dấu hiệu mạnh nhất của tình thân và hòa thuận (tr.106-107); với Ptolemy đây là góc hài hòa (I.13).",
    "square": "Lilly đọc góc vuông là sự bất hòa chưa trọn, vẫn còn đường hòa giải (tr.106); Ptolemy xếp nó vào nhóm bất hòa (I.13).",
    "opposition": "Với Lilly, góc đối là sự đối nghịch trọn vẹn (tr.107); Ptolemy cũng xếp nó vào nhóm bất hòa (I.13)."}
LILLY_ASPECT = {"conjunction": "tốt hay xấu tùy hai hành tinh hợp nhau hay không"}
THEME = {"sun": "chuyện uy quyền và danh dự (Mặt Trời)", "moon": "đời sống cảm xúc và thân thể (Mặt Trăng)", "mercury": "trí óc và lời nói (Sao Thủy)",
         "venus": "niềm vui và tình cảm (Sao Kim)", "mars": "sức mạnh và sự tranh đua (Sao Hỏa)", "jupiter": "sự rộng lượng và lòng tin (Sao Mộc)",
         "saturn": "sự nghiêm khắc và những giới hạn (Sao Thổ)", "asc": "thân thể và cách bạn hiện ra (cung Mọc)", "mc": "nghề nghiệp và địa vị (Thiên Đỉnh)"}
FRIENDS = {"jupiter": {"venus", "sun", "moon", "mercury"}, "venus": {"jupiter", "moon", "mercury", "sun"}, "saturn": set(), "mars": {"venus"}}


def _house_topic(f: Facts, p: str) -> str | None:
    h = f.house_lilly(p)
    return M["houses"][str(h)]["lilly"]["vi"] if h else None


PLANET_Q = {"sun": ("hot", "dry"), "moon": ("cold", "moist"), "mercury": ("cold", "dry"), "venus": ("cold", "moist"), "mars": ("hot", "dry"),
            "jupiter": ("hot", "moist"), "saturn": ("cold", "dry")}                    # Lilly pp.58-81 (each planet's own nature)
SIGN_Q = {"fire": ("hot", "dry"), "earth": ("cold", "dry"), "air": ("hot", "moist"), "water": ("cold", "moist")}
Q_VI = {"hot": "nóng", "cold": "lạnh", "moist": "ẩm", "dry": "khô"}


def planets(f: Facts) -> list[Para]:
    c, out = f.c, []
    good = [p for p in CLASSICAL if f.lilly_state(p) == "well"]
    bad = [p for p in CLASSICAL if f.lilly_state(p) == "ill"]
    ang = [p for p in CLASSICAL if f.house_lilly(p) in (1, 4, 7, 10)]
    summ = []
    if good:
        summ.append(f"{planet_list(good)} đắc thế theo tổng điểm của Lilly (phẩm vị cộng vị trí và chuyển động)")
    if bad:
        summ.append(f"{planet_list(bad)} thất thế")
    if ang:
        summ.append(f"{planet_list(ang)} đứng ở các nhà góc, nơi hành tinh có sức tác động mạnh nhất")
    if summ:
        out.append(Para("hd.summary", "Hành tinh mạnh, yếu", cap("; ".join(summ)) + ". ⟦Mỗi hành tinh dưới đây được đọc theo ba lớp của Lilly: chất của sao (nóng, lạnh, ẩm, khô) đặt cạnh chất của cung nó đứng "
                    "(cùng chất thì nét của sao được tăng thêm, trái chất thì bị kìm bớt, vì Lilly nói các chất trái nhau triệt tiêu nhau, tr.534); "
                    "nhà nó đứng (mảng đời, tr.50-56); và chủ của cung ấy (dispositor), vì việc của sao phải đi qua chủ tinh của nó.⟧", "traditional",
                        srcs("LILLY_CA:p.104", "LILLY_CA:p.115"), [ev_planet(c, p) for p in (good + bad)[:4]], "overview", topic="hanh_tinh",
                        steps=["Đắc thế / thất thế: tổng điểm bản chất theo Lilly ≥ +4 / ≤ -4 (ngưỡng của Thiên Bàn)."]))
    houses_told: set[int] = set()
    patterns: dict = {}
    sign_house_seen: dict = {}
    groups: dict = {}
    grouped: list[str] = []
    disp_told: dict[str, str] = {}
    for p in CLASSICAL:
        b = f.b[p]
        el = ELEMENT[sign_index(b["lon"])]
        disp = dignity.domicile_lord(b["sign"])
        h = f.house_lilly(p)
        pq, sq = PLANET_Q[p], SIGN_Q[el]
        same = [Q_VI[q] for q in pq if q in sq]
        contra = [Q_VI[q] for q in pq if q not in sq]
        mate = sign_house_seen.get((b["sign"], h))
        if mate:                                              # planets sharing sign and house with one already read: told together below
            verdict = ("cùng chất với cung" if len(same) == 2 else f"hợp chất {same[0]}, trái chất {contra[0]}" if same else "trái chất với cung")
            groups.setdefault((b["sign"], h, mate), []).append(
                f"{P(p)} ở {b['fmt']} ({verdict}; {lilly_condition(f, p, with_house=False)}" + (f"; dựa vào {P(disp)}" if disp != p else "; ở chính nhà của mình") + ")")
            grouped.append(p)
            continue
        sign_house_seen[(b["sign"], h)] = P(p)
        pattern = (tuple(same), tuple(contra))
        prev = patterns.get(pattern)
        t = f"{P(p)} ({' và '.join(Q_VI[q] for q in pq)}) ở {b['fmt']} {S(b['sign'])}, cung {ELEMENT_VI[el]} ({' và '.join(Q_VI[q] for q in sq)}): "
        if prev:
            t += f"cùng thế với {prev}. "
        elif len(same) == 2:
            t += "cùng chất hoàn toàn, nên bản chất của sao được nhân lên. "
        elif same:
            t += f"cùng chất {same[0]} nhưng trái chất {contra[0]}, nên một mặt của sao được tăng, mặt kia bị kìm. "
        else:
            t += "trái chất hoàn toàn, nên sao phải làm việc của mình trong một nền không hợp với nó. "
        patterns.setdefault(pattern, P(p))
        if h:
            if h in houses_told:
                t += f"Nó cũng ở Nhà {h}. "
            else:
                t += f"Ở Nhà {h}{f.house_note('traditional', p)}, sao này góp vào {_house_topic(f, p)}. "
                houses_told.add(h)
        t += f"{P(p)} {lilly_condition(f, p, with_house=False)}. "
        if disp == p:
            t += pick(f"{p}.own.{b['sign']}.{h}", [f"{S(b['sign'])} là nhà của chính {P(p)}, nên nó tự làm chủ việc của mình.",
                                                   f"Đứng trong {S(b['sign'])}, nhà của mình, {P(p)} không phải dựa vào chủ tinh nào khác.",
                                                   f"{P(p)} làm chủ {S(b['sign'])}, cung nó đứng, nên việc của nó do chính nó quyết."])
        elif disp in disp_told:
            t += f"{P(p)} cũng dựa vào {P(disp)}."
        else:
            st = f.lilly_state(disp)
            where = f" (Nhà {f.house_lilly(disp)})" if f.house_lilly(disp) else ""
            lines = {"well": [f"Chủ tinh {P(disp)}{where} đắc thế, nên việc của {P(p)} có chỗ dựa.",
                              f"{P(p)} dựa vào {P(disp)}{where}, một chủ tinh đắc thế: đó là điểm cộng.",
                              f"Nhờ chủ tinh {P(disp)}{where} đắc thế, {P(p)} được nâng lên."],
                     "ill": [f"Chủ tinh {P(disp)}{where} thất thế, nên việc của {P(p)} khó đi trọn.",
                             f"{P(p)} phải dựa vào {P(disp)}{where}, một chủ tinh thất thế: đó là chỗ yếu.",
                             f"Vì chủ tinh {P(disp)}{where} thất thế, việc của {P(p)} dễ bị chậm lại."],
                     "mixed": [f"Chủ tinh {P(disp)}{where} ở mức lưng chừng.", f"{P(p)} dựa vào {P(disp)}{where}, một chủ tinh không mạnh không yếu.",
                               f"Chủ tinh của {P(p)} là {P(disp)}{where}, phẩm vị lưng chừng."]}[st]
            t += pick(f"{p}.disp", lines)
            disp_told[disp] = P(p)
        out.append(Para(f"hd.{p}", f"{P(p)} ở {S(b['sign'])}" + (f", Nhà {h}" if h else ""), t, "traditional",
                        srcs("LILLY_CA:p.87", "LILLY_CA:pp.50-56", "LILLY_CA:p.104"),
                        [ev_in(f, p, "traditional")], "deep", topic="hanh_tinh", keys=[f"planet:{p}:{b['sign']}"]))
    for gi, ((sg, h, mate), items) in enumerate(groups.items()):
        out.append(Para(f"hd.group.{sg}.{h}", f"Cùng ở {S(sg)}" + (f", Nhà {h}" if h else ""),
                        f"Cùng ở {S(sg)}" + (f", Nhà {h}" if h else "") + f" với {mate} còn có: " + "; ".join(items) + "." +
                        (" Các sao tụ một chỗ nhuộm lẫn nhau, nên mảng đời của nhà ấy được nói tới nhiều lần trong lá số." if gi == 0 else ""),
                        "traditional", srcs("LILLY_CA:p.87", "LILLY_CA:p.104"), [ev_in(f, x, "traditional") for x in grouped if f.b[x]["sign"] == sg and f.house_lilly(x) == h],
                        "deep", topic="hanh_tinh"))
    vp = M["valens_planet"]
    lines = [f"{P(p)} ({vp[p].split(';')[0]}) ở Nhà {f.place_ws(p)}{f.house_note('hellenistic', p)}" if f.time_known else f"{P(p)}: {vp[p].split(';')[0]}" for p in CLASSICAL]
    out.append(Para("hd.valens", "Các hành tinh theo Valens", "⟦Valens ghi những việc mỗi hành tinh chủ về (I.1) và đọc chúng theo chỗ trọn cung; mỗi chỗ đem những việc ấy vào mảng đời của nó (IV.12).⟧ " +
                    ("Theo Valens, tính nhà trọn cung: " if f.time_known else "Theo Valens: ") + "; ".join(lines) + ".", "hellenistic", srcs("VALENS_ANTH:I.1", "VALENS_ANTH:IV.12"),
                    [], "deep", topic="hanh_tinh"))
    for i, p in enumerate(("uranus", "neptune")):
        b = f.b[p]
        hm = f.house_modern(p)
        hs = f" Nhà {hm} {f.system_vi('modern')}" if hm else ""
        tail = " ⟦Sao này đi chậm, nên người cùng thế hệ có cùng cung; điểm riêng của từng người là nhà nó đứng và các góc nó tạo với hành tinh cá nhân.⟧"
        out.append(Para(f"hd.{p}", f"{P(p)} ở {S(b['sign'])}" + (f", Nhà {hm}" if hm else ""),
                        f"{P(p)} ở {b['fmt']} {S(b['sign'])}" + ("," + hs if hs else "") + f". Alan Leo coi sao này {M['planets'][p]['leo']['vi']}." + tail,
                        "modern", srcs("LEO:How to Judge a Nativity", "LEO:The Art of Synthesis"), [ev_planet(c, p)], "deep", topic="hanh_tinh"))
    pl = f.b["pluto"]
    ch = f.b["chiron"]
    out.append(Para("hd.pluto_chiron", "Sao Diêm Vương và Chiron", f"Sao Diêm Vương ở {pl['fmt']} {S(pl['sign'])}, Chiron ở {ch['fmt']} {S(ch['sign'])}. "
                    "Cả hai được phát hiện sau thời của các tác giả trong thư viện Thiên Bàn (1930 và 1977), nên ở đây chỉ ghi vị trí, không luận ý nghĩa.",
                    "calc", [], [ev_planet(c, "pluto"), ev_planet(c, "chiron")], "deep", tier="calc", topic="hanh_tinh"))
    return out


def _conj_verdict(f: Facts, x: str, y: str) -> str:
    """What a bodily conjunction does, from the natures the books give (Lilly pp.58-81, pp.113-115; Ptolemy I.5)."""
    for a, b in ((x, y), (y, x)):
        if a == "sun" and b in f.c["conditions"] and f.c["conditions"][b].get("solar", {}).get("phase") in ("combust", "under_beams"):
            told = f.__dict__.setdefault("_concepts", set())
            if "combust_told" in told:
                return f"{P(b)} cũng bị Mặt Trời che"
            told.add("combust_told")
            return f"{P(b)} bị Mặt Trời che: theo Lilly, sao bị đốt hay dưới tia khó tự thể hiện, việc của nó chìm vào việc của Mặt Trời"
        if a == "sun" and b in f.c["conditions"] and f.c["conditions"][b].get("solar", {}).get("phase") == "cazimi":
            return f"{P(b)} nằm ngay tim Mặt Trời (cazimi): Lilly coi đây là vị trí được tăng sức mạnh"
    ben = [p for p in (x, y) if p in ("jupiter", "venus")]
    mal = [p for p in (x, y) if p in ("saturn", "mars")]
    other = lambda p: y if p == x else x
    if ben and not mal:
        return f"{P(ben[0])}, một cát tinh, làm thuận việc của {P(other(ben[0]))}"
    if mal and not ben:
        return f"{P(mal[0])}, một hung tinh, làm việc của {P(other(mal[0]))} nặng nề hơn"
    if ben and mal:
        return f"cát tinh {P(ben[0])} và hung tinh {P(mal[0])} kéo về hai phía, nên kết quả tùy sao nào mạnh hơn"
    if "mercury" in (x, y):
        return f"Sao Thủy mang màu của {P(other('mercury'))}, như Lilly nói về sao này"
    return f"việc của {P(x)} và việc của {P(y)} đi cùng nhau"


def aspects(f: Facts) -> list[Para]:
    c, out = f.c, []
    main = [a for a in c["aspects"] if a["family"] == "major" and a["a"] in CLASSICAL + ("asc", "mc") and a["b"] in CLASSICAL + ("asc", "mc")]
    main = [a for a in main if not ({a["a"], a["b"]} <= {"asc", "mc"})][:7]
    told: set[str] = set()
    told_app = False
    for a in main:
        x, y, k = a["a"], a["b"], a["type"]
        app = a["applying"]
        kind = LILLY_ASPECT.get(k, "")
        if k == "conjunction" and x in FRIENDS and y in FRIENDS:
            kind += f"; {P(x)} và {P(y)} là " + ("hai sao thân nhau" if y in FRIENDS.get(x, set()) else "hai sao không hợp nhau")
        t = f"{P(x)} {ASPECT_WITH[k]} {P(y)}, lệch {num(a['orb'], 2)}°" + (f", đang {'tiến tới' if app else 'tách ra'}" if app is not None else "") + ". "
        if k not in told:
            t += LILLY_ASPECT_FULL[k] + " "
            told.add(k)
        if k == "conjunction" and "hai sao" in kind:
            t += cap(kind.split("; ")[-1]) + ". "
        verdict = ("dễ nâng đỡ nhau" if k in ("trine", "sextile") else "dễ va vào nhau và cần được điều hòa" if k in ("square", "opposition")
                   else _conj_verdict(f, x, y))
        # what each side stands for, in a few words (Valens I.1; the angles: Lilly pp.50, 55)
        tx, ty = THEME.get(x, P(x)), THEME.get(y, P(y))
        if k == "conjunction":
            t += f"Ở đây {tx} và {ty} trộn vào nhau: {verdict}."
        else:
            t += pick(f"{x}{y}{k}", [f"Góc này nối {tx} với {ty}, nên hai mảng ấy {verdict}.", f"Nói cách khác, {tx} và {ty} {verdict}.",
                                     f"Trong đời sống, đó là chỗ {tx} gặp {ty}: chúng {verdict}."])
        if app is not None and not told_app:
            t += " ⟦Theo Ptolemy (I.24), sao đi nhanh hơn 'tiến tới' sao đi chậm khi khoảng cách còn nhỏ, và 'tách ra' khi đã vượt qua.⟧"
            told_app = True
        out.append(Para(f"gh.{x}.{y}", f"{P(x)} {ASPECT_WITH[k]} {P(y)}", t, "compare", srcs("LILLY_CA:pp.106-107", "PTOL_TETRA:I.13 p.75", "PTOL_TETRA:I.24 p.113", "VALENS_ANTH:I.1"),
                        [ev_aspect(x, y, k, f"{P(x)} {ASPECT_WITH[k]} {P(y)} ({num(a['orb'], 2)}°)")], "overview" if len(out) < 2 else "deep",
                        polarity=+1 if k in ("trine", "sextile") else -1 if k in ("square", "opposition") else 0, topic="goc_hop", keys=[f"aspect:{x}:{y}:{k}"]))
    return out


def synthesis(f: Facts, chapters: list[dict]) -> list[Para]:
    """Which planets the different methods keep pointing to, and where the chapters pull in different directions."""
    roles: dict[str, list[str]] = {}
    labels = {"geniture": "chủ lá số theo Lilly", "manners": "sao chủ tính cách theo Lilly", "soul_ruler": "sao cai quản tâm hồn theo Ptolemy",
              "action": "chủ hành nghiệp theo Ptolemy", "profession_lilly": "sao chủ nghề theo Lilly", "wealth_ruler": "chủ Lot of Fortune theo Ptolemy",
              "seventh_lord": "chủ Nhà 7", "ruler": "hành tinh dẫn dắt theo Alan Leo"}
    for ch in chapters:
        for p in ch["paragraphs"]:
            for k in p.get("keys", []):
                parts = k.split(":")
                if parts[0] in labels and len(parts) > 1:
                    for pl in parts[1].split("+"):
                        if pl in CLASSICAL:
                            roles.setdefault(pl, [])
                            if labels[parts[0]] not in roles[pl]:
                                roles[pl].append(labels[parts[0]])
    ranked = sorted(roles.items(), key=lambda kv: -len(kv[1]))
    out = []
    if ranked and len(ranked[0][1]) >= 2:
        top = [(p, r) for p, r in ranked if len(r) >= 2][:3]
        lines = [f"{P(p)} là {listing(r)}" for p, r in top]
        p0 = top[0][0]
        st = f.lilly_state(p0)
        t = ("Gom các chương lại, có những hành tinh mà nhiều phép độc lập cùng chỉ tới: " + "; ".join(lines) + ". "
             f"Khi các trường phái bắt đầu từ những chỗ khác nhau mà gặp nhau ở {P(p0)}, đó là trục chính của lá số; "
             f"{P(p0)} lại {'đắc thế, nên trục này có chỗ dựa vững' if st == 'well' else 'thất thế, nên trục này là chỗ cần chăm chút và rèn luyện nhiều nhất' if st == 'ill' else 'ở mức lưng chừng, nên trục này mạnh hay yếu tùy cách sống'}.")
        out.append(Para("th.axis", "Trục chính của lá số", t, "compare", srcs("LILLY_CA:p.531", "PTOL_TETRA:III.13 p.339", "PTOL_TETRA:IV.4 p.381", "LILLY_CA:pp.624-625"),
                        [ev_planet(f.c, p) for p, _ in top], "overview", topic="tong_hop", keys=[f"axis:{p0}"]))
    pos = [ch["title"] for ch in chapters if any(p.get("polarity", 0) > 0 for p in ch["paragraphs"])]
    neg = [ch["title"] for ch in chapters if any(p.get("polarity", 0) < 0 for p in ch["paragraphs"])]
    both = [x for x in pos if x in neg]
    t2 = ""
    if pos:
        t2 += f"Các chương có chứng thuận rõ: {listing([x for x in pos if x not in both])}. " if [x for x in pos if x not in both] else ""
    if neg:
        only_neg = [x for x in neg if x not in both]
        t2 += f"Các chương nghiêng về thử thách: {listing(only_neg)}. " if only_neg else ""
    if both:
        t2 += (f"Ở {listing(both)}, các phép cho kết quả trái chiều; mỗi chương đã đặt chúng cạnh nhau, và cách đọc hợp lý là cả hai cùng có mặt: "
               "điều thuận là nguồn lực, điều nghịch là chỗ cần để tâm.")
    if t2:
        out.append(Para("th.balance", "Thuận và nghịch giữa các chương", t2.strip(), "compare", srcs("LILLY_CA:p.104", "PTOL_TETRA:III.2 p.233"), [], "overview",
                        topic="tong_hop", steps=["Mỗi đoạn mang một dấu thuận/nghịch theo chứng của chính phép nó; chương nào có cả hai thì xếp vào nhóm trái chiều."]))
    return out
