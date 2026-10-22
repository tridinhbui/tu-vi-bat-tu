"""Chapter-specific synthesis ('Luận giải tổng hợp'): one composed section per existing report chapter.

Order inside a chapter: an intro of chart facts → theme paragraphs (most salient first; each later paragraph opens as a continuation, never
restarts) → a cross-palace paragraph → a closing synthesis that names the integrated picture and its limits. A proposition is narrated in full
once per chapter; the facet ontology decides its home chapter, so the personality chapter is built from Mệnh AND Phúc Đức readings instead of
Phúc Đức alone. The detailed rule list of each chapter is untouched and stays the evidence layer underneath.
"""
from __future__ import annotations

from functools import lru_cache

from .. import temporal, tuvi as tv_mod
from ..ganzhi import STEMS_VI
from .crosspalace import lens_paragraph, resolve_palaces
from .grammar import Discourse, Paragraph, Sentence, books, cap, np_of, short_of, theme_paragraph, validate, PALACE_TOPIC, _lead_of, _contrast, T
from .reasoner import Edge, Proposition, build_themes, group, relate, salience
from .semantics import annotate, book_pairings, lexicon
from .structures import Geo, detect_all

ENGINE = "synthesis-v1"
MAX_THEMES = 5
VERIF_VI = {"da_doi_chieu": "đã đối chiếu câu sách có trang", "mot_phan": "mới đối chiếu từng thành phần; tổ hợp chưa có câu sách", "chua_du_nguon": "chưa đủ nguồn"}

_PAIR_CACHE: dict[int, dict] = {}


def _pairings(rules, claims):
    key = hash(tuple(r.id for r in rules))
    if key not in _PAIR_CACHE:
        _PAIR_CACHE.clear()
        _PAIR_CACHE[key] = book_pairings(rules, claims)
    return _PAIR_CACHE[key]


def _stars_of(p: dict) -> str:
    if not p["major_stars"]:
        return "vô chính diệu"
    return ", ".join(f"{s} ({p['major_dignity'].get(s)})" if p["major_dignity"].get(s) else s for s in p["major_stars"])


def _palace_line(p: dict, hoa: list[str]) -> str:
    extra = [x for x in ("Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp", "Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc",
                         "Thiên Khôi", "Thiên Việt", "Lộc Tồn", "Thiên Mã", "Hồng Loan", "Đào Hoa") if x in p["stars"]]
    s = f"cung {p['name']} an tại {p['branch']} ({_stars_of(p)}"
    if hoa:
        s += "; " + ", ".join(hoa)
    if extra:
        s += "; có " + ", ".join(extra)
    tt = [x for x, f in (("Tuần", p["tuan"]), ("Triệt", p["triet"])) if f]
    if tt:
        s += "; " + " và ".join(tt)
    return s + ")"


class Context:
    def __init__(self, tv, rules, sources, claims, formations=None):
        from ..reasoning import engine, facts
        self.tv = tv
        self.base = facts.tuvi_facts(tv)
        self.res = engine.run(rules, sources, self.base, system="tu_vi", formations=formations)
        self.geo = Geo(tv.palaces, tv.tu_hoa)
        self.ann = annotate(self.res.findings, rules, claims, tv.palaces, self.geo, self.base)
        self.props = group(self.ann.evidence)
        self.edges = relate(self.props, _pairings(rules, claims))
        self.than = next((p["name"] for p in tv.palaces if p["is_than"]), None)
        self.ps = {p["name"]: p for p in tv.palaces}

    def hoa_at(self, name: str) -> list[str]:
        br = self.ps[name]["branch_index"]
        return [f"{k} ({v['star']})" for k, v in self.tv.tu_hoa.items() if v["branch"] == br]


# ---------------------------------------------------------------- topic chapters

def topic_chapter(ctx: Context, cid: str) -> dict:
    lx = lexicon()
    onto = lx["ontology"]
    title = onto["chapters"][cid]["title"]
    pals = resolve_palaces(onto["chapters"][cid]["palaces"], ctx.than)
    facets = [f for f, v in onto["facets"].items() if v["home"] == cid]
    scope = {pid: p for pid, p in ctx.props.items() if p.palace in pals or (p.palace == "chart" and cid in ("tinh_cach", "ban_menh", "quan_he"))}
    themes = build_themes(list(scope.values()), ctx.edges, facets, cid, ctx.than)
    d = Discourse(cid)
    paras: list[Paragraph] = []
    own = [n for n in onto["chapters"][cid]["palaces"] if n != "Thân"]
    intro = Paragraph("intro")
    intro.sentences.append(Sentence(cap(f"{title} được đọc chủ yếu qua " + "; ".join(_palace_line(ctx.ps[n], ctx.hoa_at(n)) for n in own[:3]) + "."), "intro", "tinh_toan"))
    if ctx.than and ctx.than not in own[:3] and cid != "ban_menh":
        intro.sentences.append(Sentence(f"Thân cư {ctx.than}, nên các nhận định ở cung này cũng được tính khi cân nhắc thứ tự chủ đề.", "intro", "tinh_toan"))
    paras.append(intro)
    d.anchors = []
    if cid == "ban_menh":
        paras += anchor_paragraphs(ctx, d)
    shown, rest = [], []
    for th in themes:
        if th.main.id in d.narrated:
            nxt = next((p for p in th.members if p.id not in d.narrated and p.kind != "rescue"), None)
            if nxt is None:
                continue
            th.main = nxt
        if len(shown) >= MAX_THEMES:
            rest.append(th)
            continue
        lead = _lead_of(th)
        paras.append(theme_paragraph(th, d, not shown, scope))
        th.lead_id = lead.id
        shown.append(th)
    if rest:
        items = [th for th in rest if th.main.id not in d.narrated][:4]
        if items:
            s = "Ngoài ra, lá số còn ghi nhận " + "; ".join(f"{np_of(th.main)} ({th.name})" for th in items) + " — những nhận định này ít căn cứ hơn nên chỉ được nêu ngắn."
            paras.append(Paragraph("theme", [Sentence(s, "support", "sach", sorted({r for th in items for r in th.main.rules}), [th.main.id for th in items])], "rest"))
            d.narrated |= {th.main.id for th in items}
    cross_meta = []
    for lens in onto["lenses"]:
        if lens["chapter"] == cid:
            lp = resolve_palaces(lens["palaces"], ctx.than)
            p, meta = lens_paragraph(lens, scope | {k: v for k, v in ctx.props.items() if v.palace in lp}, ctx.edges, ctx.than, d)
            paras.append(p)
            cross_meta.append(meta)
    if cid == "ban_menh":
        tp = than_paragraph(ctx, d)
        if tp:
            paras.append(tp)
    paras.append(_closing(cid, title, shown, ctx, d, scope))
    val = validate(paras, ctx.props, ctx.edges)
    paras = [p for p in paras if p.sentences]
    tdicts = []
    for t in shown + rest:
        x = t.to_dict()
        lead = ctx.props.get(getattr(t, "lead_id", t.main.id), t.main)
        x["lead"] = {"id": lead.id, "concept": lead.concept, "rules": lead.rules}
        tdicts.append(x)
    return {"id": cid, "title": title, "paragraphs": [p.to_dict() for p in paras], "themes": tdicts,
            "cross": cross_meta, "validation": val, "empty": not shown and cid != "ban_menh"}


MINOR_ORDER = ["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp", "Lộc Tồn", "Thiên Mã", "Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc",
               "Thiên Khôi", "Thiên Việt", "Hồng Loan", "Đào Hoa"]
DOMAIN_SHORT = {"identity": "tính cách", "career": "công danh", "finance": "tài chính", "life": "nhịp đời", "inner": "đời sống tinh thần",
                "wellbeing": "sức khỏe", "relationships": "quan hệ"}
ORDINAL = ["Trục thứ nhất của bản mệnh là", "Lớp thứ hai đến từ", "Lớp thứ ba là", "Thêm một lớp nữa là"]


def anchor_paragraphs(ctx: Context, d: Discourse) -> list[Paragraph]:
    """Bản Mệnh, star by star: the readings that hang on each star of Mệnh are gathered ACROSS domains, so the reader sees how Cự Môn, its
    Hóa Lộc, Kình–Hỏa or Hồng Loan each colour several life areas, and where a more specific condition qualifies the general reading."""
    m = ctx.ps["Mệnh"]
    hoa = [k for k, v in ctx.tv.tu_hoa.items() if v["branch"] == m["branch_index"]]
    order = list(m["major_stars"]) + hoa + [x for x in MINOR_ORDER if x in m["stars"]]
    props = [p for p in ctx.props.values() if p.palace == "Mệnh"]
    groups: dict[str, list[Proposition]] = {a: [] for a in order}
    partners: dict[str, list] = {a: [] for a in order}
    for p in props:
        stars = [s for ev in p.evidence for s in ev.present_stars]
        a = next((x for x in order if x in stars), None)
        if a:
            groups[a].append(p)
            partners[a].append({s for s in stars if s in order and s != a and order.index(s) > order.index(a)})
    out = []
    pid = {p.id: p for p in props}
    homes = {f: v["home"] for f, v in lexicon()["ontology"]["facets"].items()}
    titles = {k: v["title"] for k, v in lexicon()["ontology"]["chapters"].items()}
    for a in [x for x in order if groups[x]][:4]:
        ps = sorted(groups[a], key=lambda p: (-sum(r.weight for r in p.roots), p.id))
        d.start_paragraph()
        para = Paragraph("anchor", facet=a)
        if a in m["major_stars"]:
            label = f"{a}" + (f" ({m['major_dignity'][a]})" if m["major_dignity"].get(a) else "") + " thủ Mệnh"
        elif a in hoa:
            label = f"{a} tại Mệnh (hóa từ {ctx.tv.tu_hoa[a]['star']})"
        else:
            n = len(partners[a])
            co = sorted({s for ss in partners[a] for s in ss if sum(s in x for x in partners[a]) * 2 > n}, key=order.index)
            label = f"{a}" + (f" ({m['minor_dignity'].get(a)})" if m["minor_dignity"].get(a) else "") + (" cùng " + ", ".join(co) if co else "") + " tại Mệnh"
        sens = any(p.sensitive for p in ps)
        doms: dict[str, list[Proposition]] = {}
        for p in ps:
            if p.kind != "rescue":
                doms.setdefault(p.domain, []).append(p)
        bits, listed = [], []
        for dom, xs in sorted(doms.items(), key=lambda kv: -max(sum(r.weight for r in p.roots) for p in kv[1])):
            px = [p for p in xs if p.polarity != "-"][:3]
            nx = [p for p in xs if p.polarity == "-"][:3]
            listed += px + nx
            pos = list(dict.fromkeys(short_of(p) for p in px))
            neg = list(dict.fromkeys(short_of(p) for p in nx))
            dn = DOMAIN_SHORT.get(dom, dom)
            pos = [x for x in pos if x != dn] or ([] if pos else pos)
            if not pos and not neg:
                bits.append(f"về {dn}, có một nhận định riêng")
                continue
            b = f"về {dn}, " + (", ".join(pos[:3]) if pos else "")
            if neg:
                b += (" nhưng cũng " if pos else "") + ", ".join(neg[:3])
            bits.append(b)
        chs = sorted({titles.get(homes[p.facet], "") for p in ps if p.kind != "rescue"} - {"", "Bản Mệnh"})
        k = len(out)
        s = (f"{ORDINAL[min(k, 3)]} {label}: các nhận định " + ("(theo cách luận truyền thống) " if sens else "") +
             f"gắn với vị trí này trải trên {len(doms)} lĩnh vực — " + "; ".join(bits) + ".")
        if chs:
            s += " Phân tích từng mặt nằm ở chương " + ", ".join(chs) + "."
        para.sentences.append(Sentence(s, "claim", "sach", sorted({r for p in listed for r in p.rules}), [p.id for p in listed]))
        d.end_sentence(para.sentences[-1])
        for e in ctx.edges:
            if e.type == "contradicts" and e.resolution == "refinement" and e.a in pid and e.b in pid and {e.a, e.b} <= {p.id for p in ps}:
                det = e.detail
                gen, spec = pid[det["general"]], pid[det["specific"]]
                s = (f"Trong đó có một quan hệ chung – riêng: {books(det['general_books'])} ghi {short_of(gen)} cho trường hợp chung, còn {books(det['specific_books'])} "
                     f"khi xét riêng {det['specific_trigger']} (đúng với lá số này) lại nghiêng về {short_of(spec)}; điều kiện riêng điều chỉnh chứ không xóa nhận định chung.")
                para.sentences.append(Sentence(s, "interaction", "dieu_kien", det["general_rules"] + det["specific_rules"], [gen.id, spec.id]))
                d.end_sentence(para.sentences[-1])
                break
        resc = [p for p in ps if p.kind == "rescue"] + [pid[e.a] for e in ctx.edges if e.type == "mitigates" and e.b in {p.id for p in ps} and e.a in pid]
        if resc and resc[0].id not in d.narrated:
            r = resc[0]
            s = d.pick("mitigates", T["mitigates"], r.id).format(book=books(r.books), reading=r.best.reading)
            para.sentences.append(Sentence(cap(s), "condition", "sach", r.rules, [r.id]))
            d.end_sentence(para.sentences[-1])
            d.narrated.add(r.id)
        out.append(para)
        d.anchors.append(label)
    return out


def than_paragraph(ctx: Context, d: Discourse) -> Paragraph | None:
    if not ctx.than:
        return None
    d.start_paragraph()
    if ctx.than == "Mệnh":
        return Paragraph("cross", [Sentence("Thân cư Mệnh: Mệnh và Thân cùng một cung, nên những gì nói ở trên đồng thời là trọng tâm của nửa sau cuộc đời theo cách đọc truyền thống.", "intro", "he_thong")], "than")
    ps = sorted([p for p in ctx.props.values() if p.palace == ctx.than and p.kind != "rescue"], key=lambda p: (-sum(r.weight for r in p.roots), p.id))
    s = f"Thân cư {ctx.than}: theo cách đọc truyền thống, nửa sau cuộc đời dồn sức vào {PALACE_TOPIC.get(ctx.than, 'chủ đề của cung ấy')}."
    para = Paragraph("cross", [Sentence(s, "intro", "he_thong")], "than")
    if ps:
        titles = {k: v["title"] for k, v in lexicon()["ontology"]["chapters"].items()}
        home = lexicon()["ontology"]["facets"][ps[0].facet]["home"]
        para.sentences.append(Sentence(f"Ở cung này, nổi bật là {' và '.join(np_of(p) for p in ps[:2])} (chi tiết ở chương {titles.get(home, home)}).", "claim", "sach",
                                       sorted({r for p in ps[:2] for r in p.rules}), [p.id for p in ps[:2]]))
    return para


def _closing(cid: str, title: str, shown, ctx: Context, d: Discourse, scope) -> Paragraph:
    para = Paragraph("synthesis")
    if not shown and not (cid == "ban_menh" and getattr(d, "anchors", None)):
        para.sentences.append(Sentence(f"Bộ quy tắc đã đối chiếu sách chưa có nhận định nào đủ điều kiện cho chương {title} trên lá số này; hệ thống không viết thêm thay vì suy đoán.", "limit", "he_thong"))
        return para
    if cid == "ban_menh" and getattr(d, "anchors", None):
        a = d.anchors
        s = ("Tóm lại, bản mệnh được dựng từ " + (f"{len(a)} lớp sao: " + ", ".join(a[:-1]) + " và " + a[-1] if len(a) > 1 else a[0]) +
             ". Mỗi lớp tô màu nhiều lĩnh vực cùng lúc, nên cùng một vị trí sao có thể vừa nâng đỡ ở lĩnh vực này vừa đặt giới hạn ở lĩnh vực khác; các chương sau đọc từng lĩnh vực với đầy đủ điều kiện.")
        para.sentences.append(Sentence(s, "synthesis", "he_thong", sorted({r for p in ctx.props.values() if p.palace == "Mệnh" for r in p.rules})[:12], []))
        shown = []
    heads = [th for th in shown[:3]]
    tension = next(((th, p, e) for th in heads for p, e in th.counters if e is not None and e.type in ("qualifies", "contradicts")), None)
    lead_of = lambda th: ctx.props.get(getattr(th, "lead_id", th.main.id), th.main)
    names = [np_of(lead_of(th)) for th in heads]
    lead = "Tóm lại, " + (f"chân dung ở chương này dựng trên {len(names)} lớp: " + ", ".join(names[:-1]) + " và " + names[-1] if len(names) > 1 else f"trọng tâm của chương này là {names[0]}") if names else ""
    if tension:
        th, p, e = tension
        x = lead_of(th)
        y = th.main if x is not th.main and p is x else p
        lead += f"; điểm cần đọc kỹ nhất là quan hệ giữa {np_of(x)} và {np_of(y)}, " + ("vì đó là hai mặt của cùng một nét chứ không phải hai kết luận loại trừ nhau" if e.type == "qualifies"
                                                                                             else "vì đó là hai chiều cùng có điều kiện kích hoạt trong lá số")
    if lead:
        para.sentences.append(Sentence(lead + ".", "synthesis", "he_thong", sorted({r for th in heads for r in th.main.rules}), [th.main.id for th in heads]))
    n_draft = sum(1 for x in ctx.ann.drafts if _in_scope(x["subject"], scope))
    n_unm = sum(1 for x in ctx.ann.unmapped if _in_scope(x["subject"], scope) and "why" not in x)
    n_exc = sum(1 for x in ctx.ann.excluded if _in_scope(x["subject"], scope) and "lặp" not in x["reason"])
    lim = "Mỗi nhận định chỉ có nghĩa trong điều kiện của quy tắc sinh ra nó"
    extra = []
    if n_draft:
        extra.append(f"{n_draft} nhận định từ quy tắc nháp")
    if n_unm:
        extra.append(f"{n_unm} nhận định chưa có ánh xạ ngữ nghĩa")
    if n_exc:
        extra.append(f"{n_exc} nhận định bị loại vì điều kiện trong bộ quy tắc rộng hơn câu sách")
    if extra:
        lim += "; " + ", ".join(extra) + " không được đưa vào phần tổng hợp (vẫn xem được trong danh sách chi tiết bên dưới)"
    para.sentences.append(Sentence(lim + ".", "limit", "he_thong"))
    return para


def _in_scope(subject: str, scope: dict) -> bool:
    pal = subject.split(":", 1)[1] if ":" in subject else "chart"
    return any(p.palace == pal for p in scope.values())


# ---------------------------------------------------------------- overview

def overview(ctx: Context, chapters: dict[str, dict]) -> dict:
    tv, m = ctx.tv, ctx.ps["Mệnh"]
    d = Discourse("tong_quan")
    paras = []
    p1 = Paragraph("intro")
    hoa = ctx.hoa_at("Mệnh")
    p1.sentences.append(Sentence(cap(f"Mệnh an tại {m['stem']} {m['branch']} với {_stars_of(m)}" + (f", có {', '.join(hoa)}" if hoa else "") +
                                     f"; Thân cư {ctx.than}; {tv.cuc['name']}, bản mệnh {tv.menh_nap_am} ({tv.menh_cuc_relation}); {tv.yin_yang_gender}."), "intro", "tinh_toan"))
    paras.append(p1)

    def top(cid, k=1):
        return [t for t in chapters.get(cid, {}).get("themes", [])][:k]

    con = lexicon()["concepts"]

    def txt(t):
        return np_of(ctx.props[t["lead"]["id"]]) if t["lead"]["id"] in ctx.props else con[t["lead"]["concept"]]["np"]

    def cnp(c):
        return np_of(ctx.props[c["prop"]["id"]]) if c["prop"]["id"] in ctx.props else con[c["prop"]["concept"]]["np"]

    def counter(t):
        lead = t["lead"]["id"]
        cs = [x for x in t["counters"] if x["edge"] and x["edge"]["type"] in ("qualifies", "contradicts")]
        if t["main"]["id"] != lead:
            cs = [{"prop": t["main"], "edge": next((x["edge"] for x in t["counters"] if x["prop"]["id"] == lead), None)}] + cs
        return next((c for c in cs if c["prop"]["id"] != lead and c["edge"]), None)

    ident = top("tinh_cach", 2)
    if ident:
        prov = sorted({r for t in ident for r in t["lead"]["rules"]})
        p2 = Paragraph("theme", [Sentence("Hình ảnh con người nổi lên trước hết qua " + " và ".join(txt(t) for t in ident) + ".", "claim", "sach", prov, [t["lead"]["id"] for t in ident])], "identity")
        c = counter(ident[0])
        if c:
            synth = next((r.get("synth") for r in lexicon()["relations"] if {r["a"], r["b"]} == {ident[0]["lead"]["concept"], c["prop"]["concept"]}), "")
            p2.sentences.append(Sentence(f"Đi cùng nét ấy là {cnp(c)}" + (f" — {synth}" if synth else "") + "; chương Tính cách phân tích hai mặt này cạnh nhau thay vì để chúng đứng riêng.",
                                         "interaction", "dieu_kien" if c["edge"]["type"] == "contradicts" else "he_thong", c["prop"]["rules"], [ident[0]["lead"]["id"], c["prop"]["id"]]))
        paras.append(p2)
    work = [(cid, t) for cid in ("cong_danh", "tai_bach") for t in top(cid)]
    if work:
        bits, prov = [], []
        for cid, t in work:
            c = counter(t)
            label = {"cong_danh": "công danh", "tai_bach": "tài chính"}[cid]
            b = f"về {label}, lá số nghiêng về {txt(t)}"
            if c:
                x, y = txt(t), cnp(c)
                if con[c["prop"]["concept"]]["pol"] == "+" and con[t["lead"]["concept"]]["pol"] == "-":
                    x, y = y, x
                b = f"về {label}, lá số ghi cả {x} lẫn {y}"
                prov += c["prop"]["rules"]
            bits.append(b)
            prov += t["lead"]["rules"]
        paras.append(Paragraph("theme", [Sentence("Theo cách luận truyền thống (không phải dự báo), " + "; ".join(bits) + ". Đây là những khuynh hướng có điều kiện, các chương Công danh và Tài Bạch nêu rõ từng điều kiện.",
                                                  "claim", "sach", sorted(set(prov)), [t["lead"]["id"] for _, t in work])], "work"))
    life = top("ban_menh") + top("quan_he")
    if life:
        s = "Ở tầng đời sống, theo cách luận truyền thống, " + "; ".join(txt(t) for t in life) + " là những chủ đề được nêu rõ nhất (xem chương Bản Mệnh và Quan hệ)."
        paras.append(Paragraph("theme", [Sentence(s, "claim", "sach", sorted({r for t in life for r in t["lead"]["rules"]}), [t["lead"]["id"] for t in life])], "life"))
    kinds = {}
    for e in ctx.edges:
        if e.type == "contradicts":
            kinds[e.resolution] = kinds.get(e.resolution, 0) + 1
    n_ev = len({e.rule_id for e in ctx.ann.evidence})
    s = (f"Phần tổng hợp dùng {n_ev} quy tắc đã đối chiếu sách trên tổng số {len({f.rule_id for f in ctx.res.findings})} quy tắc được kích hoạt; "
         f"{len(ctx.ann.drafts)} nhận định nháp và {len([x for x in ctx.ann.unmapped if 'why' not in x])} nhận định chưa ánh xạ chỉ nằm trong danh sách chi tiết. ")
    if kinds:
        s += ("Các chỗ trái chiều được phân loại theo điều kiện: " + ", ".join(f"{n} {VI_RES[k]}" for k, n in sorted(kinds.items())) + ". ")
    s += "Không có điểm số tổng hợp: thứ tự trình bày chỉ phản ánh vai trò cấu trúc và mức độ trực tiếp của căn cứ."
    paras.append(Paragraph("synthesis", [Sentence(s, "limit", "he_thong")]))
    val = validate(paras, ctx.props, ctx.edges)
    return {"id": "tong_quan", "title": "Tổng quan Tử Vi", "paragraphs": [p.to_dict() for p in paras if p.sentences], "themes": [], "cross": [], "validation": val, "empty": not ident}


VI_RES = {"refinement": "quan hệ chung – riêng", "both_hold": "cặp cùng đúng ở hai điều kiện khác nhau", "school_divergence": "chỗ hai sách đọc khác nhau",
          "unresolved": "mâu thuẫn thật chưa phân xử"}


# ---------------------------------------------------------------- đại hạn & lưu niên

def dai_han(ctx: Context, year: int) -> dict:
    tv = ctx.tv
    ty = temporal.tuvi_year(tv, year)
    dh = ty["dai_han"]
    d = Discourse("dai_han")
    paras = []
    if dh is None:
        first = min(tv.dai_han, key=lambda x: x["age_from"]) if tv.dai_han else None
        s = f"Năm {year} (tuổi mụ {ty['age_tuoi_mu']}) chưa vào đại hạn đầu tiên" + (f" (bắt đầu từ {first['age_from']} tuổi tại cung {next(p['name'] for p in tv.palaces if p['branch'] == first['branch'])})" if first else "") + \
            "; phần đại hạn chưa có gì để đọc, chỉ có lưu niên theo vị trí."
        paras.append(Paragraph("intro", [Sentence(s, "intro", "tinh_toan")]))
        paras.append(Paragraph("synthesis", [Sentence("Phần thời gian chỉ ghi vị trí và lời sách theo từng sao hóa; hệ thống không dự báo sự kiện.", "limit", "he_thong")]))
        return {"id": "dai_han", "title": "Đại hạn & lưu niên", "year": year, "paragraphs": [p.to_dict() for p in paras], "themes": [], "cross": [],
                "validation": validate(paras, ctx.props, ctx.edges), "empty": True}
    p1 = Paragraph("intro", [Sentence(f"Năm {year} (tuổi mụ {ty['age_tuoi_mu']}) nằm trong đại hạn {dh['age_from']}–{dh['age_to']} tại cung {dh['palace']} ({dh['stem']} {dh['branch']}); "
                                      f"tiểu hạn ở cung {ty['tieu_han_palace']}, lưu Thái Tuế ở cung {ty['luu_thai_tue_palace']}.", "intro", "tinh_toan")])
    paras.append(p1)
    P = dh["palace"]
    here = sorted([p for p in ctx.props.values() if p.palace == P and p.kind != "rescue"], key=lambda p: (-sum(r.weight for r in p.roots), p.id))
    p2 = Paragraph("theme", facet="dai_han_palace")
    topic = PALACE_TOPIC.get(P, "chủ đề của cung ấy")
    p2.sentences.append(Sentence(f"Theo cách đọc đại hạn truyền thống, giai đoạn này đặt {topic} lên trước; đại hạn không tạo ra nhận định mới mà làm nổi lên những gì nguyên cục đã ghi ở cung {P}.", "intro", "he_thong"))
    if here:
        for i, p in enumerate(here[:2]):
            ev = p.roots[0].evidence[0]
            p2.sentences.append(Sentence(("Ở cung này, nguyên cục ghi " if i == 0 else "Cung này cũng ghi ") + f"{np_of(p)} ({d.trig(ev.chart_trigger or ev.trigger_text, False)}, theo {books(p.books)}).", "claim", "sach", p.rules, [p.id]))
        if len(here) >= 2:
            e = next((e for e in ctx.edges if e.type == "contradicts" and {e.a, e.b} == {here[0].id, here[1].id}), None)
            if e is not None:
                p2.sentences += [x for x in _contrast(here[0], here[1], e, d, ctx.props) if x.kind == "interaction"]
        menh_link = [(p, q, e) for e in ctx.edges for p in here[:3] for q in ctx.props.values()
                     if q.palace in ("Mệnh", ctx.than) and q.palace != P and {e.a, e.b} == {p.id, q.id}]
        if menh_link:
            p, q, e = menh_link[0]
            p2.sentences.append(Sentence(f"Điều này cần được đặt cạnh chân dung chung ở cung {q.palace}: {np_of(q)} — " + (e.synth or "hai nhận định điều chỉnh lẫn nhau") + ".", "interaction",
                                         "dieu_kien" if e.type == "contradicts" else "he_thong", sorted(set(p.rules) | set(q.rules)), [p.id, q.id]))
    else:
        p2.sentences.append(Sentence(f"Bộ quy tắc đã đối chiếu không có nhận định nguyên cục nào được kích hoạt ở cung {P}, nên phần này chỉ nêu vị trí.", "limit", "he_thong"))
    paras.append(p2)
    stem_i = STEMS_VI.index(dh["stem"])
    dh_hoa = dict(zip(("Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"), tv_mod.hoa_of(tv, stem_i)))
    star_pal = {s: p["name"] for p in tv.palaces for s in p["major_stars"] + p["stars"]}
    landing = {h: star_pal.get(s) for h, s in dh_hoa.items()}
    p3 = Paragraph("theme", facet="dai_han_hoa")
    p3.sentences.append(Sentence(f"Bốn hóa theo can {dh['stem']} của đại hạn đáp xuống: " + ", ".join(f"{h} ({dh_hoa[h]}) ở cung {landing[h] or 'không xác định'}" for h in dh_hoa) + ".", "intro", "tinh_toan"))
    ky_pal = landing.get("Hóa Kỵ")
    kp = sorted([p for p in ctx.props.values() if p.palace == ky_pal], key=lambda p: -sum(r.weight for r in p.roots))
    if ky_pal and kp:
        p3.sentences.append(Sentence(f"Hóa Kỵ đại hạn rơi vào cung {ky_pal}, nơi nguyên cục ghi {np_of(kp[0])}. Bộ quy tắc không có luật giao thoa giữa Tứ Hóa đại hạn và nguyên cục, "
                                     "nên đây chỉ là đặt hai dữ kiện cạnh nhau để người đọc lưu ý, không phải một kết luận.", "interaction", "he_thong", kp[0].rules, [kp[0].id]))
    paras.append(p3)
    rd = {r["hoa"]: r for r in ty["luu_tu_hoa_reading"]}
    p4 = Paragraph("theme", facet="luu_nien")
    for h in ("Hóa Lộc", "Hóa Kỵ"):
        r = rd.get(h)
        if r:
            p4.sentences.append(Sentence(f"Lưu niên {year}: {h} lưu ở cung {r['palace']} ({r['star']}); {r['src']} khuyên “{r['advice']}” và ghi “{r['position_note']}”.", "claim", "sach", [r["src"]], []))
    if p4.sentences:
        paras.append(p4)
    paras.append(Paragraph("synthesis", [Sentence("Phần thời gian chỉ ghi vị trí và lời sách theo từng sao hóa; hệ thống không dự báo sự kiện và không tự suy luận giao thoa nhiều tầng khi sách không có quy tắc.", "limit", "he_thong")]))
    val = validate(paras, ctx.props, ctx.edges)
    return {"id": "dai_han", "title": "Đại hạn & lưu niên", "year": year, "paragraphs": [p.to_dict() for p in paras if p.sentences], "themes": [], "cross": [], "validation": val, "empty": False}


# ---------------------------------------------------------------- cách cục

def cach_cuc(ctx: Context) -> dict:
    structs = [s for s in detect_all(ctx.tv.palaces, ctx.tv.tu_hoa) if s.present]
    paras = []
    if not structs:
        paras.append(Paragraph("intro", [Sentence("Trong sáu cấu trúc đặc biệt hệ thống kiểm tra, không có cấu trúc nào hiện trên lá số này; phần cách cục chỉ còn danh sách nhận diện theo tên ở bên dưới.", "limit", "he_thong")]))
    for i, s in enumerate(structs):
        p = Paragraph("theme", facet=s.id)
        ok = [x["text"] for x in s.premises if x["ok"]]
        no = [x["text"] for x in s.premises if not x["ok"]]
        p.sentences.append(Sentence(["Cấu trúc đáng chú ý nhất là ", "Một cấu trúc khác là ", "Thêm vào đó là ", "Cuối cùng là "][min(i, 3)] + f"{s.name}: " + "; ".join(ok) + ("" if not no else "; chưa thỏa: " + "; ".join(no)) + ".", "intro", "tinh_toan"))
        if s.supports:
            p.sentences.append(Sentence("Điều nâng cấu trúc này lên: " + "; ".join(s.supports) + ".", "support", "sach", s.cites, []))
        if s.limiters:
            p.sentences.append(Sentence(f"Ngược lại, những gì hạn chế hoặc phá cấu trúc ở cung {s.palaces[0] if s.palaces else 'này'}: " + "; ".join(s.limiters) + ".", "contrast", "sach", s.cites, []))
        if s.rescuers:
            p.sentences.append(Sentence("Bù lại có yếu tố cứu giải: " + "; ".join(s.rescuers) + ".", "condition", "sach", s.cites, []))
        if s.reading:
            p.sentences.append(Sentence(s.reading, "interaction", "dieu_kien", s.cites, []))
        p.sentences.append(Sentence(f"Về mức đối chiếu, cấu trúc này {VERIF_VI[s.verification]}." + (f" {s.caveat}" if s.caveat else ""), "limit", "he_thong"))
        paras.append(p)
    val = validate(paras, ctx.props, ctx.edges)
    return {"id": "cach_cuc", "title": "Cách cục", "paragraphs": [p.to_dict() for p in paras if p.sentences], "themes": [], "cross": [], "validation": val, "empty": not structs}


# ---------------------------------------------------------------- entry point

def build_synthesis(tv, rules, sources, claims, birth_year: int, year: int | None = None, formations=None) -> dict:
    ctx = Context(tv, rules, sources, claims, formations)
    chapters = {cid: topic_chapter(ctx, cid) for cid in ("tinh_cach", "ban_menh", "cong_danh", "tai_bach", "quan_he")}
    chapters["tong_quan"] = overview(ctx, chapters)
    chapters["dai_han"] = dai_han(ctx, max(year or birth_year + 30, birth_year))
    chapters["cach_cuc"] = cach_cuc(ctx)
    order = ["tong_quan", "ban_menh", "tinh_cach", "cong_danh", "tai_bach", "quan_he", "dai_han", "cach_cuc"]
    rels = {}
    for e in ctx.edges:
        k = e.type + (":" + e.resolution if e.resolution else "")
        rels[k] = rels.get(k, 0) + 1
    return {"engine": ENGINE, "chapters": [chapters[c] for c in order],
            "coverage": {"findings": len(ctx.res.findings), "evidence": len(ctx.ann.evidence), "propositions": len(ctx.props), "relations": rels,
                         "drafts_excluded": len(ctx.ann.drafts), "unmapped": ctx.ann.unmapped, "excluded": ctx.ann.excluded,
                         "verified_rules_used": len({e.rule_id for e in ctx.ann.evidence})},
            "semantic_ir": [{k: (list(v) if isinstance(v, tuple) else v) for k, v in e.__dict__.items()} for e in ctx.ann.evidence],
            "note": "Không dùng mô hình ngôn ngữ: mọi câu được dựng từ mệnh đề ngữ nghĩa có truy vết quy tắc. Không có điểm số; thứ tự trình bày là ưu tiên cấu trúc, không phải xác suất."}
