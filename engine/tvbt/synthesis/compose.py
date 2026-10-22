"""Composer: evidence clusters + structures + tensions -> ten chapters, conclusion first, details nested.
Rules of the house: (1) a finding is narrated in exactly ONE chapter, others only point to it; (2) no scoring — supports and limits are listed and the
conclusion is a CONDITIONAL sentence naming what decides it; (3) sensitive topics (hôn nhân, sức khỏe, tuổi thọ, giàu nghèo) are always framed as
what tradition records, not as a prediction; (4) nothing is marked verified here — `basis` is copied from the rule."""
from __future__ import annotations

from .. import temporal, tuvi as tv_mod
from ..ganzhi import STEMS_VI
from . import taxonomy as tx
from .conflicts import MATRIX, Tension, find_tensions, matrix_hits
from .evidence import Cluster, Evidence, build, cluster
from .structures import SAT, CAT, Structure, detect_all

SENSITIVE = {"hon_nhan": "chuyện hôn nhân", "suc_khoe": "sức khỏe", "tuoi_tho": "tuổi thọ", "tai": "tiền của, phúc lộc"}
CHAPTER_STRUCT = {"TAM_HOA_HOI_MENH": "ban_menh", "SAT_PHA_THAM": "cach_cuc", "CU_MON_HOA_LOC": "cach_cuc", "THAN_QUAN_VCD": "cong_danh",
                  "CO_NGUYET_PHU_THE": "quan_he", "KINH_DUONG_TU_MO": "cach_cuc"}
VERIF_VI = {"da_doi_chieu": "đã đối chiếu câu sách có trang", "mot_phan": "mới đối chiếu từng thành phần, tổ hợp chưa có câu sách", "chua_du_nguon": "chưa đủ nguồn"}


def _order(e: Evidence):
    return (0 if e.basis == "verified" else 1, -len(e.leaves), e.claim)


def _star_text(p) -> str:
    if not p["major_stars"]:
        return "không có chính tinh (vô chính diệu)"
    return ", ".join(f"{s} ({p['major_dignity'].get(s) or 'độ sáng chưa rõ'})" for s in p["major_stars"])


def _palace_position(g, name: str) -> dict:
    """vị trí sao → quan hệ cung, as plain facts."""
    p = g.ps[name]
    opp, th = g.opp(p), g.tam_hop(p)
    tt = [x for x, f in (("Tuần", p["tuan"]), ("Triệt", p["triet"])) if f]
    hoa = g.hoa_in([p])
    return {"palace": name, "branch": p["branch"], "text":
            f"Cung {name} an tại {p['stem']} {p['branch']}: {_star_text(p)}. Đối cung {opp['name']} ({_star_text(opp)}). "
            f"Tam hợp {th[0]['name']} ({_star_text(th[0])}) và {th[1]['name']} ({_star_text(th[1])})."
            + (f" Cung có {' và '.join(tt)}." if tt else "") + (f" Sao hóa tại cung: {', '.join(hoa)}." if hoa else "")}


def _line(c: Cluster) -> dict:
    """One narrated line per cluster+valence bucket: the best-supported claim, and how many sibling claims fold into it."""
    items = sorted({(e.claim, e.effect): e for e in c.items}.values(), key=_order)
    head = items[0]
    return {"claim": head.claim, "text": head.label, "effect": head.effect, "valence": head.valence, "aspect": head.aspect, "basis": head.basis,
            "anchor": c.anchor, "palace": c.palace, "rule_id": head.rule_id, "cites": sorted({x for e in c.items for x in e.cites}),
            "schools": sorted({s for e in c.items for s in e.schools}), "folded": len(items) - 1,
            "also": [{"claim": e.claim, "text": e.label} for e in items[1:]]}


def _buckets(cs: list[Cluster]):
    sup, lim, neu = [], [], []
    for c in cs:
        if c.aspect == "nhan_dien":
            continue
        byv: dict[str, list[Evidence]] = {}
        for e in c.items:
            side = {"nghich": "lim", "thuan": "sup"}.get(e.polarity, "neu")
            byv.setdefault(side, []).append(e)
        for side, items in byv.items():
            sub = Cluster(c.key, c.subject, c.palace, c.aspect, c.anchor, c.chapter, items)
            {"sup": sup, "lim": lim, "neu": neu}[side].append(_line(sub))
    key = lambda l: (0 if l["basis"] == "verified" else 1, l["palace"] or "", l["claim"])
    return sorted(sup, key=key), sorted(lim, key=key), sorted(neu, key=key)


def _soften(text: str, aspect: str) -> str:
    if aspect in SENSITIVE:
        return f"theo truyền thống ghi nhận về {SENSITIVE[aspect]} (không phải dự báo): {text}"
    return text


def _fmt(lines: list[dict], limit=4) -> list[str]:
    out = []
    for l in lines[:limit]:
        t = _soften(l["text"], l["aspect"])
        cite = f" [{'; '.join(l['cites'])}]" if l["cites"] else ""
        out.append(f"{t}{cite}" + (f" — cùng chủ đề còn {l['folded']} quy tắc khác" if l["folded"] else ""))
    if len(lines) > limit:
        out.append(f"… và {len(lines) - limit} nhận định khác trong phần mở rộng")
    return out


def _tension_text(ts: list[Tension]) -> list[str]:
    out = []
    for t in ts:
        out.append({"refinement": "Điều chỉnh", "both_hold": "Đồng thời đúng", "school_divergence": "Hai trường phái", "unresolved": "Mâu thuẫn chưa phân xử"}[t.kind] + f" ({t.a} ↔ {t.b}): " + t.explanation)
    return out


def _short(l: dict) -> str:
    return l["text"].split(" (")[0].strip()


def _conclusion(name: str, head: str, sup, lim, ts: list[Tension], structs: list[Structure]) -> str:
    """Conditional synthesis. No weighting: it names the leading item of each side and says what the reading depends on."""
    parts = [f"{name}: {head}" if head else name]
    if sup and lim:
        parts.append(f"Nâng đỡ nổi bật là ‘{_short(sup[0])}’; đối trọng là ‘{_short(lim[0])}’")
        if any(t.kind in ("both_hold", "refinement") for t in ts):
            parts.append("Hai phía cùng tồn tại vì điều kiện kích hoạt của cả hai đều thỏa (xem ‘điều kiện đọc’); sách không xếp thứ tự giữa chúng, nên bản luận là thành tựu có kèm trở ngại, không cái nào triệt tiêu cái nào")
        else:
            parts.append("Hai phía thuộc những mặt khác nhau của cung nên không mâu thuẫn; chúng đọc song song")
    elif sup:
        parts.append(f"Chỉ có nhận định nâng đỡ được kích hoạt, nổi bật là ‘{_short(sup[0])}’; vắng nhận định hạn chế trong bộ quy tắc hiện có không có nghĩa là không có hạn chế")
    elif lim:
        parts.append(f"Chỉ có nhận định hạn chế được kích hoạt, nổi bật là ‘{_short(lim[0])}’; bộ quy tắc không có nhận định nâng đỡ tương ứng nên đây là điểm cần tự điều chỉnh")
    else:
        parts.append("Không có nhận định định tính nào được kích hoạt ngoài dữ kiện vị trí")
    if any(t.kind in ("unresolved", "school_divergence") for t in ts):
        parts.append("Có chỗ các sách nói khác nhau mà chưa có căn cứ để chọn; hệ thống trình bày cả hai")
    for s in structs:
        if s.present:
            parts.append(f"Cấu trúc đáng chú ý: {s.name} ({VERIF_VI[s.verification]})")
    return ". ".join(parts) + "."


def _chain(position_text: str, structs, tensions, conclusion) -> list[dict]:
    ch = [{"step": "vi_tri_sao", "text": position_text}]
    for s in structs:
        if s.present:
            ch.append({"step": "cach_cuc", "text": f"{s.name}: " + "; ".join(f"{'✓' if p['ok'] else '✗'} {p['text']}" for p in s.premises)})
    if tensions:
        ch.append({"step": "dieu_kien", "text": " | ".join(_tension_text(tensions[:3]))})
    ch.append({"step": "ket_luan", "text": conclusion})
    return ch


def _sources(lines, structs) -> list[dict]:
    cites = {}
    for l in lines:
        for c in l["cites"]:
            cites[c] = {"cite": c, "schools": l["schools"], "basis": l["basis"]}
    for s in structs:
        if s.present:
            for c in s.cites:
                cites.setdefault(c, {"cite": c, "schools": [], "basis": "cấu trúc: " + s.verification})
    return sorted(cites.values(), key=lambda d: d["cite"])


def _verification(lines, structs) -> str:
    v = sum(1 for l in lines if l["basis"] == "verified")
    parts = [f"{v}/{len(lines)} nhận định có quy tắc đã đối chiếu sách (trạng thái lấy nguyên từ bộ quy tắc, hệ thống này không tự nâng cấp)"] if lines else []
    parts += [f"{s.name}: {VERIF_VI[s.verification]}" for s in structs if s.present]
    return "; ".join(parts) or "chỉ có dữ kiện vị trí, không có nhận định cần đối chiếu"


def build_deep_reading(tv, bz, rules, sources, claims_vi, birth_year: int, year: int | None = None, formations=None) -> dict:
    from ..reasoning import engine, facts
    from .structures import Geo
    base = facts.tuvi_facts(tv)
    res = engine.run(rules, sources, base, system="tu_vi", formations=formations)
    evs = build(res.findings, rules, claims_vi)
    clusters = cluster(evs)
    tensions = find_tensions(clusters)
    structs = detect_all(tv.palaces, tv.tu_hoa)
    g = Geo(tv.palaces, tv.tu_hoa)
    year = year or birth_year + 30
    chapters = []

    def chapter_clusters(cid): return [c for c in clusters if c.chapter == cid]

    def chapter_tensions(cs):
        ids = {e.rule_id for c in cs for e in c.items}
        return [t for t in tensions if t.a in ids and t.b in ids]  # both sides narrated in this chapter

    def chapter_structs(cid): return [s for s in structs if CHAPTER_STRUCT.get(s.id) == cid and s.present]

    palaces_of = {"ban_menh": ["Mệnh"], "tinh_cach": ["Phúc Đức"], "cong_danh": ["Quan Lộc"], "tai_bach": ["Tài Bạch", "Điền Trạch"],
                  "quan_he": ["Phu Thê", "Nô Bộc", "Tử Tức", "Huynh Đệ", "Phụ Mẫu"], "muoi_hai_cung": ["Thiên Di", "Tật Ách"]}
    titles = dict(tx.CHAPTERS)
    for cid in ("ban_menh", "tinh_cach", "cong_danh", "tai_bach", "quan_he", "muoi_hai_cung"):
        cs = chapter_clusters(cid)
        sup, lim, neu = _buckets(cs)
        ts = chapter_tensions(cs)
        ss = chapter_structs(cid)
        pos = " ".join(_palace_position(g, n)["text"] for n in palaces_of[cid][:2])
        names = " & ".join(palaces_of[cid][:2])
        head = "; ".join(f"{n} — {_star_text(g.ps[n])}" for n in palaces_of[cid][:2])
        concl = _conclusion(titles[cid] if cid != "muoi_hai_cung" else "Thiên Di và Tật Ách", head, sup, lim, ts, ss)
        chapters.append({"id": cid, "title": titles[cid], "conclusion": concl, "supports": _fmt(sup), "limits": _fmt(lim), "neutral": _fmt(neu, 2),
                         "reasoning_chain": _chain(pos, ss, ts, concl), "reading_conditions": _tension_text(ts)[:6] + ([f"… và {len(ts) - 6} chỗ khác trong phần mở rộng"] if len(ts) > 6 else []),
                         "sources": _sources(sup + lim + neu, ss), "verification": _verification(sup + lim + neu, ss),
                         "details": {"tensions": [t.__dict__ for t in ts], "supports": sup, "limits": lim, "neutral": neu, "structures": [s.__dict__ for s in ss],
                                     "positions": [_palace_position(g, n) for n in palaces_of[cid]]}})

    # --- Cách cục: structures + draft formations + chart-level classification labels
    cs = chapter_clusters("cach_cuc") + [c for c in clusters if c.aspect == "nhan_dien"]
    ss = [s for s in structs if s.present and CHAPTER_STRUCT.get(s.id) == "cach_cuc"]
    labels = sorted({e.label for c in cs for e in c.items if c.aspect == "nhan_dien"})
    forms = [f for f in (res.formations or []) if f.get("state") not in (None, "khong_hien")]
    concl = ("Cách cục được đọc như các luận điểm có điều kiện: " + ("; ".join(s.name for s in ss) if ss else "chưa có cấu trúc đặc biệt nào hiện") +
             ". Mỗi cấu trúc nêu rõ điều kiện tiên quyết, yếu tố nâng, yếu tố phá và mức nguồn; hệ thống không cộng điểm để quyết ‘thành’ hay ‘phá’ cách.")
    chapters.append({"id": "cach_cuc", "title": titles["cach_cuc"], "conclusion": concl,
                     "supports": [x for s in ss for x in s.supports][:6], "limits": [x for s in ss for x in s.limiters][:6], "neutral": labels[:4],
                     "reasoning_chain": _chain("Nhận diện cách cục từ vị trí chính tinh và sát/cát tinh trong tam phương tứ chính của từng cung có liên quan.", ss, chapter_tensions(cs), concl),
                     "reading_conditions": _tension_text(chapter_tensions(cs)) + [s.caveat for s in ss if s.caveat],
                     "sources": _sources([], ss), "verification": _verification([], ss) + ("; có %d cách cục bản nháp đang hiện (chưa đối chiếu)" % len(forms) if forms else ""),
                     "details": {"structures": [s.__dict__ for s in ss], "draft_formations": [{"id": f["id"], "name": f["name_vi"], "state": f["state"], "text": f.get("text")} for f in forms]}})

    # --- Đại hạn & lưu niên
    ty = temporal.tuvi_year(tv, year)
    dh = ty["dai_han"]
    stem_i = STEMS_VI.index(dh["stem"])
    dh_hoa = dict(zip(("Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"), tv_mod.hoa_of(tv, stem_i)))
    star_pal = {s: p["name"] for p in tv.palaces for s in p["major_stars"] + p["stars"]}
    landing = {h: star_pal.get(s) for h, s in dh_hoa.items()}
    natal_pal = {h: star_pal.get(v["star"]) for h, v in tv.tu_hoa.items()}
    stack = [f"{h} đại hạn ({dh_hoa[h]}) cùng rơi vào sao với {h} nguyên cục" for h in dh_hoa if dh_hoa[h] == tv.tu_hoa[h]["star"]]
    ky_cross = [f"Hóa Kỵ đại hạn tại cung {landing['Hóa Kỵ']} trong khi Hóa Lộc nguyên cục ở {natal_pal['Hóa Lộc']}"] if landing["Hóa Kỵ"] and landing["Hóa Kỵ"] != natal_pal["Hóa Lộc"] else ["Hóa Kỵ đại hạn cùng cung với Hóa Lộc nguyên cục: hai hóa chồng lên nhau, sách trích chưa phân xử"]
    dh_cs = [c for c in clusters if c.palace == dh["palace"] and c.aspect != "nhan_dien"]
    dsup, dlim, _ = _buckets(dh_cs)
    concl = (f"Năm {year} (tuổi mụ {ty['age_tuoi_mu']}) nằm trong đại hạn {dh['age_from']}–{dh['age_to']} tại cung {dh['palace']} ({dh['stem']} {dh['branch']}). "
             f"Đại hạn không tạo ra nhận định mới: nó chọn cung nguyên cục nào được ‘bật sáng’ trong giai đoạn này — ở đây là {dh['palace']}, cùng với việc bốn hóa theo can {dh['stem']} đáp xuống " +
             ", ".join(f"{h} → {landing[h]}" for h in dh_hoa) + ". " +
             (f"Cung này mang {len(dsup)} nhận định nâng đỡ và {len(dlim)} nhận định hạn chế nguyên cục, đọc xem ở chương tương ứng." if dh_cs else "Cung này không có nhận định nguyên cục nào được kích hoạt.") +
             " Lưu niên chỉ ghi vị trí và lời sách theo từng sao hóa; không dự báo sự kiện.")
    chapters.append({"id": "dai_han_luu_nien", "title": titles["dai_han_luu_nien"], "conclusion": concl,
                     "supports": [f"{h}: {r['advice']} ({r['src']})" for r in ty["luu_tu_hoa_reading"] for h in [r["hoa"]] if h in ("Hóa Lộc", "Hóa Quyền", "Hóa Khoa")],
                     "limits": [f"{r['hoa']}: {r['advice']} ({r['src']})" for r in ty["luu_tu_hoa_reading"] if r["hoa"] == "Hóa Kỵ"],
                     "neutral": stack or [],
                     "reasoning_chain": [{"step": "vi_tri_sao", "text": f"Đại hạn tại {dh['palace']} (can {dh['stem']}), tiểu hạn tại {ty['tieu_han_palace']}, lưu Thái Tuế tại {ty['luu_thai_tue_palace']}."},
                                         {"step": "quan_he_cung", "text": "Tứ Hóa đại hạn đáp: " + ", ".join(f"{h}→{landing[h]}" for h in dh_hoa)},
                                         {"step": "dieu_kien", "text": " ; ".join(ky_cross + stack)}, {"step": "ket_luan", "text": concl}],
                     "reading_conditions": ["Tứ Hóa lưu dùng bảng đang chạy trong tính toán; tuổi Nhâm phụ thuộc R05"] if tv.year_gz.startswith("Nhâm") else [],
                     "sources": [{"cite": "Khảo Luận pp.195-197", "schools": ["Khảo Luận"], "basis": "sach"}, {"cite": "Khảo Luận pp.233-236", "schools": ["Khảo Luận"], "basis": "sach"}, {"cite": "Thực Hành p.27", "schools": ["Thực Hành"], "basis": "verified"}],
                     "verification": "phần tính vị trí đã đối chiếu (Thực Hành p.27); phần lời sách theo sao hóa lấy từ Khảo Luận, chưa có quy tắc đại hạn giao thoa nguyên cục nên chỉ nêu vị trí",
                     "details": {"year": ty, "dai_han_hoa": landing, "natal_hoa": natal_pal, "stack_notes": stack}})

    # --- Tổng quan (pointers only; no repeated findings) and Chuyên sâu
    present = [s for s in structs if s.present]
    n_unres = sum(1 for t in tensions if t.kind in ("unresolved", "school_divergence"))
    menh = g.ps["Mệnh"]
    mh = matrix_hits(tv.palaces, tv.year_gz.split()[0])
    axis = [l for l in _buckets(chapter_clusters("ban_menh"))[0] + _buckets(chapter_clusters("ban_menh"))[1] if l["basis"] == "verified"][:2]
    tong = (f"Mệnh tại {menh['branch']} với {_star_text(menh)}, Thân cư {next(p['name'] for p in tv.palaces if p['is_than'])}; {tv.cuc['name']}, bản mệnh {tv.menh_nap_am} ({tv.menh_cuc_relation}); {tv.yin_yang_gender}, đại hạn {tv.dai_han_direction}. "
            f"Từ {len(res.findings)} nhận định được kích hoạt, hệ thống rút ra {len([c for c in clusters if c.aspect != 'nhan_dien'])} cụm chủ đề, {len(tensions)} chỗ trái chiều (trong đó {n_unres} chưa thể phân xử) và {len(present)} cấu trúc đặc biệt"
            + (": " + ", ".join(s.name for s in present) if present else "")
            + ". " + (("Trục chính của Bản Mệnh: " + "; ".join(f"‘{_short(l)}’" for l in axis) + ". ") if axis else "")
            + "Chi tiết nằm ở từng chương; chương này không lặp lại.")
    chapters.insert(0, {"id": "tong_quan", "title": titles["tong_quan"], "conclusion": tong, "supports": [], "limits": [], "neutral": [],
                        "reasoning_chain": [{"step": "vi_tri_sao", "text": _palace_position(g, "Mệnh")["text"]}, {"step": "ket_luan", "text": tong}],
                        "reading_conditions": [], "sources": [], "verification": "tóm tắt cấu trúc; số liệu lấy từ các chương sau",
                        "pointers": {c["id"]: c["title"] for c in chapters if c["id"] != "tong_quan"}, "details": {}})
    mhc = next(c for c in chapters if c["id"] == "muoi_hai_cung")
    mhc["details"]["table"] = [{"palace": n, "branch": g.ps[n]["branch"], "majors": g.ps[n]["major_stars"], "tuan": g.ps[n]["tuan"], "triet": g.ps[n]["triet"],
                                "hoa": g.hoa_in([g.ps[n]]), "chapter": tx.chapter_of(f"palace:{n}", "tong_hop") if n not in ("Mệnh",) else "ban_menh",
                                "n_findings": sum(len(c.items) for c in clusters if c.palace == n)} for n in tx.PALACE_CHAPTER | {"Mệnh": ""} if n in g.ps]
    mhc["conclusion"] = ("Mười hai cung được liệt kê dưới dạng bảng vị trí; chỉ Thiên Di và Tật Ách được luận ở đây, mười cung còn lại luận ở chương chứa chúng để không lặp. " + mhc["conclusion"])
    chapters.append({"id": "chuyen_sau", "title": titles["chuyen_sau"],
                     "conclusion": "Phần này là hồ sơ kiểm chứng: mọi chỗ trái chiều, mọi điểm nguồn mâu thuẫn từ Phase 7 chạm vào lá số này, và các quy tắc chưa đủ nguồn mà hệ thống cố ý không suy diễn.",
                     "supports": [], "limits": [], "neutral": [],
                     "reasoning_chain": [{"step": "dieu_kien", "text": "; ".join(f"{e['id']} {e['topic']} ({e['status']})" for e in mh) or "Không có điểm mâu thuẫn nguồn đã biết nào chạm vào lá số này."},
                                         {"step": "ket_luan", "text": "Mọi mục trên được giữ ở trạng thái ‘chưa phân xử’: hệ thống không chọn trường phái và không đánh dấu verified."}],
                     "reading_conditions": [e["policy"] for e in mh],
                     "sources": [{"cite": c, "schools": [], "basis": e["status"]} for e in mh for c in e["sources"]],
                     "verification": "không có mục nào được tự đánh dấu verified; policy chưa đủ nguồn xem bên dưới",
                     "details": {"tensions": [t.__dict__ for t in tensions], "source_conflicts": mh, "unverified_policies": MATRIX["unverified_policies"],
                                 "structures_absent": [{"id": s.id, "name": s.name, "premises": s.premises} for s in structs if not s.present],
                                 "pipeline": {"findings": len(res.findings), "evidence": len(evs), "clusters": len(clusters), "tensions": len(tensions)}}})
    order = [c for c, _ in tx.CHAPTERS]
    chapters.sort(key=lambda c: order.index(c["id"]))
    return {"enabled": True, "engine": "deep-interpretation-v0", "year": year, "chapters": chapters,
            "meta": {"findings": len(res.findings), "clusters": len(clusters), "tensions": len(tensions), "structures_present": [s.id for s in present],
                     "note": "Mọi nhận định lấy từ bộ quy tắc hiện có; basis được giữ nguyên, không tự nâng cấp. Không có điểm số."}}
