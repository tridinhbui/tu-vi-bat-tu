"""Cross-palace holistic reasoning. A lens (data/semantic/ontology.json `lenses`) names palaces read together and the question they answer.
Nothing is concluded from a lens by itself: it reports (1) the geometry fact that links the palaces (tam phương or not), (2) explicit relations
between propositions of DIFFERENT palaces of the lens, (3) a domain that recurs across the palaces, aligned or divergent. With none of these,
it says the rule set gives no grounded link instead of inventing one."""
from __future__ import annotations

from .grammar import Discourse, Paragraph, Sentence, cap, np_of, PALACE_TOPIC
from .reasoner import Edge, Proposition
from .semantics import lexicon

TAM_PHUONG_OF_MENH = {"Quan Lộc", "Tài Bạch", "Thiên Di"}


def resolve_palaces(names: list[str], than: str | None) -> list[str]:
    out = []
    for n in names:
        n = than if n == "Thân" else n
        if n and n not in out:
            out.append(n)
    return out


def lens_paragraph(lens: dict, props: dict[str, Proposition], edges: list[Edge], than: str | None, d: Discourse) -> tuple[Paragraph, dict]:
    pals = resolve_palaces(lens["palaces"], than)
    para = Paragraph("cross", facet=lens["id"])
    mine = {pid: p for pid, p in props.items() if p.palace in pals}
    geo = []
    for p in pals:
        if p == "Mệnh":
            continue
        if p in TAM_PHUONG_OF_MENH:
            geo.append(f"{p} nằm trong tam phương tứ chính của Mệnh nên sao ở đó hội chiếu về Mệnh")
        elif p == than:
            geo.append(f"Thân cư {p}, nên cung này được đọc như nơi con người dồn sức về sau")
        else:
            geo.append(f"{p} không thuộc tam phương của Mệnh, nên quan hệ với Mệnh là quan hệ chủ đề chứ không phải hội chiếu")
    intro = f"Đặt {lens['name']} cạnh nhau để xem {lens['question']}." + (" Về vị trí, " + "; ".join(geo) + "." if geo else "")
    d.start_paragraph()
    para.sentences.append(Sentence(intro, "intro", "tinh_toan"))
    focus = set(lens.get("focus_domains", []))
    cross = [e for e in edges if e.a in mine and e.b in mine and mine[e.a].palace != mine[e.b].palace
             and (not focus or {mine[e.a].domain, mine[e.b].domain} & focus)]
    cross.sort(key=lambda e: ({"contradicts": 0, "qualifies": 1, "supports": 2}.get(e.type, 3), -(mine[e.a].salience + mine[e.b].salience), e.a, e.b))
    told = 0
    used: set[str] = set()
    for e in cross:
        a, b = mine[e.a], mine[e.b]
        if told >= 3 or (e.a in used and e.b in used) or d.pair_told(a, b):
            continue
        if e.type == "supports" or e.type == "elaborates":
            s = f"Chủ đề {np_of(a)} ở cung {a.palace} gặp lại ở cung {b.palace} dưới dạng {np_of(b)}: hai cung cùng chiều" + (f" ({e.synth})." if e.synth else ".")
            basis = "he_thong"
        elif e.type == "contradicts":
            s = (f"Ở cung {a.palace} là {np_of(a)}, còn ở cung {b.palace} là {np_of(b)}. Cung {a.palace} nói về {PALACE_TOPIC.get(a.palace, 'chủ đề của nó')}, "
                 f"cung {b.palace} nói về {PALACE_TOPIC.get(b.palace, 'chủ đề của nó')}; hai điều kiện đều thỏa nên hai chiều cùng tồn tại, sách không xếp thứ tự.")
            basis = "dieu_kien"
        elif e.type in ("qualifies", "conditions", "mitigates"):
            s = f"{cap(np_of(a))} (cung {a.palace}) và {np_of(b)} (cung {b.palace}) nên được đọc cùng nhau: {e.synth or 'hai nhận định điều chỉnh lẫn nhau'}."
            basis = "sach" if e.basis == "sach" else "he_thong"
        else:
            continue
        para.sentences.append(Sentence(s, "interaction", basis, sorted(set(a.rules) | set(b.rules)), [a.id, b.id]))
        d.tell_pair(a, b)
        used |= {a.id, b.id}
        told += 1
    # domain recurrence not already covered by an edge
    if told == 0:
        by_dom: dict[str, list[Proposition]] = {}
        for p in mine.values():
            if not focus or p.domain in focus:
                by_dom.setdefault(p.domain, []).append(p)
        for dom, ps in sorted(by_dom.items()):
            palset = {p.palace for p in ps}
            if len(palset) < 2:
                continue
            ps = sorted(ps, key=lambda p: -p.salience)
            pos = [p for p in ps if p.polarity == "+"]
            neg = [p for p in ps if p.polarity == "-"]
            dn = lexicon()["ontology"]["domains"][dom].lower()
            if pos and neg and pos[0].palace != neg[0].palace:
                s = (f"Chủ đề {dn} xuất hiện ở nhiều cung theo hai chiều: {np_of(pos[0])} ở cung {pos[0].palace}, nhưng {np_of(neg[0])} ở cung {neg[0].palace}. "
                     "Đây là hai tầng khác nhau của cùng một chủ đề, không phải hai kết luận loại trừ nhau.")
                para.sentences.append(Sentence(s, "interaction", "he_thong", sorted(set(pos[0].rules) | set(neg[0].rules)), [pos[0].id, neg[0].id]))
                told += 1
            elif len(ps) >= 2 and ps[0].palace != ps[1].palace and ps[0].polarity == ps[1].polarity:
                s = f"Chủ đề {dn} được ghi ở cả cung {ps[0].palace} ({np_of(ps[0])}) lẫn cung {ps[1].palace} ({np_of(ps[1])}), cùng một chiều."
                para.sentences.append(Sentence(s, "interaction", "he_thong", sorted(set(ps[0].rules) | set(ps[1].rules)), [ps[0].id, ps[1].id]))
                told += 1
            if told >= 2:
                break
    if told == 0:
        para.sentences.append(Sentence("Giữa các cung này, bộ quy tắc hiện có không cho thấy điểm giao nhau nào đủ căn cứ để nối; hệ thống không tự suy ra mối liên hệ.", "limit", "he_thong"))
    return para, {"lens": lens["id"], "palaces": pals, "links": told}
