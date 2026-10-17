"""Dụng Thần Engine: MỖI PHƯƠNG PHÁP MỘT BẢNG RIÊNG (Dụng / Hỷ / Kỵ / Cừu / Nhàn theo nhóm thập thần), không trộn.
Phương pháp: phù ức, điều hậu (bảng + thứ tự của Thiệu Vĩ Hoa), cách cục (hệ thống/Trích Thiên Tủy), cách cục theo Thiệu Vĩ Hoa, thông quan,
thuận thế (tòng/hóa), khuyết hành (một ví dụ tr.399). Mỗi phương pháp mang `meta`: nguồn, mức xác minh riêng, điều kiện áp dụng, cơ sở khí thế và `trace` các bước.
Sau cùng compare() chỉ đặt các bảng cạnh nhau và chỉ ra chỗ bất đồng; không có bước nào chọn 'đáp án cuối' hay cộng điểm giữa các phương pháp."""
from __future__ import annotations

import json

from ..ganzhi import ELEMENTS, STEM_ELEMENT, controls, generates
from ..bazi import HIDDEN_STEMS
from .geju import Ctx, analyse as geju_analyse, build_readings, pred
from .model import ChartView
from .profile import DATA, DEFAULT as DEFAULT_PROFILE, LEVELS, SchoolProfile
from .season import climate
from .strength import GROUP_VI, compute as strength_compute

ROLES = ["yong", "xi", "ji", "chou", "xian"]
TONG_ROLES = json.loads((DATA / "tong_roles.json").read_text("utf-8"))
TQ = json.loads((DATA / "thuong_quan_dung.json").read_text("utf-8"))
TVH_DT = json.loads((DATA / "tvh_dungthan.json").read_text("utf-8"))

# Three separate levels, never inferred from one another (docs/BAZI_DEEP_TVH_AUDIT.md):
#   transcription_verified: the table/text was copied correctly from the source page;
#   source_rule_verified:   the formula/condition (including thresholds) matches the source's own statement;
#   empirical_validated:    independent evidence that the output predicts anything. NOTHING in this module has that, so it is "no" everywhere.
# Values: yes | partial | no | n/a.
# Per-method provenance. verification: verified = table/rule text read at a PDF page by Claude (no second human check yet); partial = verified table + system conventions;
# draft = this system's own convention or a single worked example. `applies_when` is the condition under which the method says anything.
METHOD_META = {
    "phu_uc": {"levels": {"transcription_verified": "n/a", "source_rule_verified": "no", "empirical_validated": "no", "why": "nguyên lý phổ thông của hệ thống, không có nguồn đối chiếu"}, "source": ["he_thong (nguyên lý phù ức phổ thông; ngưỡng cấp độ khí thế là của hệ thống)"], "verification": "draft",
               "applies_when": "không có ngoại cách chân và khí thế không ở mức trung hòa"},
    "dieu_hau": {"levels": {"transcription_verified": "yes", "source_rule_verified": "partial", "empirical_validated": "no", "why": "bảng và thứ tự chép khớp trang in (120/120 bảng, chú thích có 9 ô mâu thuẫn nội bộ); vai trò Dụng/Hỷ và ngưỡng hàn/nhiệt là của hệ thống"}, "source": ["SRC_TVH_DIEUHAU tr.389-390 (tập can)", "SRC_TVH_DIEUHAU tr.391-396 (thứ tự)", "SRC_TTT_HANTHU tr.113-114 (hàn/noãn)"], "verification": "partial",
                 "applies_when": "luôn tra được: mỗi (can ngày, tháng) có một ô. Việc gán can chính = Dụng, các can còn lại = Hỷ là quy ước của hệ thống; ngưỡng hàn/nhiệt là chỉ số thô của hệ thống"},
    "cach_cuc": {"levels": {"transcription_verified": "partial", "source_rule_verified": "no", "empirical_validated": "no", "why": "chỉ phần Thương Quan (TTT tr.93-94) chép khớp; phần còn lại là bảng nháp"}, "source": ["he_thong (bảng cách cục nháp)", "SRC_TTT_THUONGQUAN tr.93-94 (Thương Quan)"], "verification": "draft",
                 "applies_when": "nội cách đứng đầu; Thương Quan dùng năm mẫu của Trích Thiên Tủy"},
    "cach_cuc_tvh": {"levels": {"transcription_verified": "yes", "source_rule_verified": "partial", "empirical_validated": "no", "why": "bảng tr.378-386 chép khớp, quy tắc 40% khớp tr.355; biên ±0,03, quy ước đúng 40% và các ví dụ (1/3 khớp hoàn toàn) chưa đủ"}, "source": ["SRC_TVH_DUNGTHAN tr.378-386 (bảng cách × vượng/nhược × nhóm nhiều nhất)", "SRC_TVH_DIEM tr.355 (ngưỡng 40%)"], "verification": "partial",
                     "applies_when": "nội cách đứng đầu và có dòng trong bảng; 'nhóm nhiều nhất' lấy theo tổng điểm TVH; biên ±tvh_margin quanh 40% là ngưỡng hiển thị của hệ thống nên cho hai cách đọc"},
    "thong_quan": {"levels": {"transcription_verified": "n/a", "source_rule_verified": "no", "empirical_validated": "no", "why": "không có nguồn; ngưỡng của hệ thống"}, "source": ["he_thong (nguyên lý thông quan; ngưỡng war_share/bridge_min là của hệ thống)"], "verification": "draft",
                   "applies_when": "có hai hành khắc nhau cùng ≥ war_share"},
    "thuan_the": {"levels": {"transcription_verified": "yes", "source_rule_verified": "partial", "empirical_validated": "no", "why": "bảng vai trò TTT tr.171-179 chép khớp; ngưỡng nhận diện và hóa thần dư/thiếu là của hệ thống"}, "source": ["SRC_TTT_TONG tr.171-179 (vai trò các loại tòng)", "SRC_TTT_HOA tr.175-176 (hóa thần)"], "verification": "partial",
                  "applies_when": "chỉ khi hệ thống/Trích Thiên Tủy nhận ngoại cách chân (tòng/hóa); ngưỡng hóa thần dư/thiếu là của hệ thống; không dùng cách đặc biệt của Thiệu Vĩ Hoa"},
    "thuan_the_tvh": {"levels": {"transcription_verified": "yes", "source_rule_verified": "partial", "empirical_validated": "no", "why": "bảng tr.381-386 chép khớp; điều kiện nhận diện được vận hành bằng ngưỡng của hệ thống"}, "source": ["SRC_TVH_DUNGTHAN tr.381-386"], "verification": "partial",
                      "applies_when": "chỉ khi có cách đặc biệt chân theo Thiệu Vĩ Hoa (tòng tài/sát/nhi, chuyên vượng, hóa khí); các ngưỡng nhận diện là của hệ thống"},
    "khuyet_hanh": {"levels": {"transcription_verified": "n/a", "source_rule_verified": "no", "empirical_validated": "no", "why": "chỉ một ví dụ tr.399, sách không phát biểu thành quy tắc"}, "source": ["SRC_TVH_DUNGTHAN tr.399 (ví dụ 3: ngũ hành thiếu mộc, thủy thì dụng mộc, thủy)"], "verification": "draft",
                    "applies_when": "lá số thiếu hẳn một hành (kể cả tàng can). Sách chỉ có MỘT ví dụ, không phát biểu thành quy tắc chung"},
}
TVH_KINDS = ("tong_tvh", "chuyen_vuong", "hoa_tvh")      # outer-cách kinds produced by tvh_cach.special (Thiệu Vĩ Hoa), never by the system/Trích Thiên Tủy detector
APPLIED = {"ap_dung", "bang_TVH_verified", "co_giao_chien", "ap_dung_ttt_thuong_quan", "cach_bai"}


def _table(method: str, status: str, **roles) -> dict:
    t = {r: list(roles.get(r, [])) for r in ROLES}
    extra = {k: v for k, v in roles.items() if k not in ROLES}
    return {"method": method, "status": status, **t, **extra}


def phu_uc(S: dict, outer_chan: bool) -> dict:
    """Nhược -> Ấn/Tỉ; vượng -> khắc tiết hao. Chỉ chạy khi khí thế rõ và không có ngoại cách chân."""
    if outer_chan:
        return _table("phu_uc", "khong_ap_dung", note="ngoại cách chân: phù ức không áp dụng", trace=["có ngoại cách chân → phù ức bị loại"])
    lv = S["level_index"]
    basis = "tvh_40 (40%)" if S.get("tvh") else "he_thong"
    if S["ambiguous"]:
        alts = []
        for name in S["readings"]:
            alts.append(phu_uc({**S, "level_index": LEVELS.index(name), "ambiguous": False}, False))
        return {"method": "phu_uc", "status": "hai_cach_doc", "alternatives": [dict(a, level=n) for a, n in zip(alts, S["readings"])],
                "yong": [], "xi": [], "ji": [], "chou": [], "xian": [],
                "trace": [f"khí thế ở biên ({basis}): hai cách đọc {S['readings']}", "chạy phù ức cho từng cách đọc, không chọn"]}
    if lv <= 2:
        return _table("phu_uc", "ap_dung", level=LEVELS[lv], yong=["An"], xi=["Ti"], ji=["Tai", "QuanSat", "ThucThuong"],
                      trace=[f"khí thế {LEVELS[lv]} ({basis})", "nhược → Ấn làm Dụng, Tỉ Kiếp làm Hỷ; Tài, Quan Sát, Thực Thương là Kỵ"])
    if lv >= 4:
        return _table("phu_uc", "ap_dung", level=LEVELS[lv], yong=["QuanSat", "ThucThuong", "Tai"], ji=["An", "Ti"],
                      trace=[f"khí thế {LEVELS[lv]} ({basis})", "vượng → Quan Sát, Thực Thương, Tài khắc/tiết/hao làm Dụng; Ấn, Tỉ Kiếp là Kỵ"])
    return _table("phu_uc", "khong_ap_dung", level=LEVELS[lv], note="trung hòa: phù ức không nghiêng về phía nào", trace=[f"khí thế {LEVELS[lv]} ({basis}): không nghiêng"])


def dieu_hau(view: ChartView, S: dict) -> dict:
    """Bảng 窮通寶鑑 (draft, từ trí nhớ) cho vai trò thập thần; chỉ số nhiệt thô được giữ lại làm đối chiếu."""
    from . import dieuhau
    cl = climate(view, S["by_element"])
    tb = dieuhau.lookup(view)
    groups = []
    for x in tb["yong_stems"]:
        if x["group"] not in groups:
            groups.append(x["group"])
    main = tb["yong_stems"][0]["group"]
    t = _table("dieu_hau", "bang_TVH_verified", yong=[main], xi=[g for g in groups if g != main], table=tb, climate=cl, source="SRC_TVH_DIEUHAU")
    h = cl["heat"]
    t["trace"] = [f"ô bảng TVH: {tb['cell']}", "tập can dùng được (tr.389-390): " + ", ".join(x["stem"] for x in tb["yong_stems"]),
                  f"can chủ = đứng đầu chú thích thứ tự (tr.391-396): {tb['chu']}", "nhóm thập thần: " + ", ".join(f"{x['stem']}={x['group']}" for x in tb["yong_stems"]),
                  "hiện diện: " + (", ".join(f"{x['stem']}({'thấu' if x['visible'] else 'tàng' if x['hidden'] else 'vắng'})" for x in tb["yong_stems"]))]
    t["need_elements"], t["avoid_elements"] = (["Hỏa"], ["Thủy"]) if h <= -1 else (["Thủy"], ["Hỏa"]) if h >= 1.5 else ([], [])
    t["han_noan"] = han_noan(view, cl)
    t["note"] = "Tập can dùng được lấy từ bảng dụng thần dự bị của Thiệu Vĩ Hoa (tr.389-390, đã đối chiếu); can 'chính' là can đứng đầu trong chú thích thứ tự của sách (tr.391-396). Vai trò: can chính là Dụng, các can còn lại là Hỷ. Chỉ số nhiệt thô chỉ để đối chiếu."
    return t


def cach_cuc(geju: dict, tq: dict | None = None) -> dict:
    prim = geju["readings"][0] if geju["readings"] else None
    if not prim or prim["kind"] != "noi_cach":
        return _table("cach_cuc", "khong_xac_dinh_noi_cach", note="nội cách không lập được hoặc bị ngoại cách thay")
    c = next(x for x in geju["inner"] if x["name"] == prim["cach"])
    if tq and tq.get("style"):               # Thương Quan: the book's own five styles replace the generic table
        return _table("cach_cuc", "ap_dung_ttt_thuong_quan", cach=c["name"], cach_state=c["state"], yong=tq["yong"], xi=tq["xi"], ji=tq["ji"], style=tq["style"], source=tq["src"], van=tq["van"],
                      trace=[f"nội cách đầu: {c['name']} ({c['state']})", f"Thương Quan dùng mẫu '{tq['style']}' (Trích Thiên Tủy tr.93-94)"])
    if c["state"] in ("bai",):
        return _table("cach_cuc", "cach_bai", cach=c["name"], yong=c["yong_groups"], bai=[b["id"] for b in c["bai"]],
                      note="cách bại chưa được cứu: dụng thần nêu theo bảng nhưng cần coi là vô lực",
                      trace=[f"nội cách đầu: {c['name']} bại ({', '.join(b['id'] for b in c['bai'])}), chưa được cứu", f"bảng nháp của cách: {c['yong_groups']}"])
    return _table("cach_cuc", "ap_dung", cach=c["name"], cach_state=c["state"], yong=c["yong_groups"],
                  trace=[f"nội cách đầu: {c['name']} ({c['state']})", f"bảng nháp của cách: {c['yong_groups']}"])


def _tvh_row(key: str, dm: str, dom: str):
    return next((r for r in TVH_DT["rows"] if r["cach"] == key and r["dm"] == dm and r["dom"] == dom), None)


def cach_cuc_tvh(geju: dict, S: dict, profile: SchoolProfile | None = None) -> dict:
    """Dụng thần theo cách của Thiệu Vĩ Hoa (pp.378-386): (cách, nhật chủ vượng/nhược theo quy tắc 40%, nhóm nhiều nhất) -> dụng thần và vận tốt/xấu.
    Method separate from cach_cuc (which follows the system's own draft tables and Trích Thiên Tủy for Thương Quan).
    Origin of each number used here: 40% = SRC_TVH_DIEM tr.355 (the book says 'lớn hơn/nhỏ hơn'; '>=' at exactly 40% is this system's choice);
    the band `tvh_margin` around 40% that yields two readings is this system's display heuristic, NOT the book's; 'nhóm nhiều nhất' = largest share of the TVH totals."""
    margin = (profile or DEFAULT_PROFILE).tvh_margin
    prim = geju["readings"][0] if geju["readings"] else None
    if not prim or prim["kind"] != "noi_cach":
        return _table("cach_cuc_tvh", "khong_xac_dinh_noi_cach", note="nội cách không lập được hoặc bị ngoại cách thay")
    cach = prim["cach"]
    key = TVH_DT["cach_key"].get(cach)
    if key is None:
        return _table("cach_cuc_tvh", "khong_co_bang", cach=cach)
    tv = S.get("tvh")
    border = S.get("ambiguous") and tv is not None
    strong = tv["dm_strong"] if tv else S["level_index"] >= 4
    shares = S["shares"]
    if tv and tv.get("totals"):               # the book's own method: group shares from the scored totals (hóa, xung, lệnh applied)
        from .strength import GROUPS, group_of_element
        tot = sum(tv["totals"].values()) or 1.0
        shares = {g: 0.0 for g in GROUPS}
        for e, v in tv["totals"].items():
            shares[group_of_element(tv["dm_element"], e)] += v / tot
    order = sorted(shares, key=lambda g: -shares[g])

    def pick(dm):
        for g in order:
            row = _tvh_row(key, dm, g)
            if row:
                return g, row
        return None, None
    options = [("strong", "vượng"), ("weak", "nhược")] if border else [("strong" if strong else "weak", "vượng" if strong else "nhược")]
    own = tv.get("own_share") if tv else S.get("ratio")
    thr = {"rule": 0.40, "rule_src": "SRC_TVH_DIEM tr.355", "own_share": own, "book_rule_reading": "vượng" if strong else "nhược",
           "near_threshold": bool(border), "margin_heuristic": margin, "margin_src": "he_thong (không phải của sách)",
           "equality_choice": "đúng 40% tính là vượng (quy ước hệ thống; sách chỉ nói lớn hơn/nhỏ hơn)"}
    trace = [f"nội cách đầu: {cach} → khóa bảng '{key}'",
             f"phe mình = {own} so với ngưỡng 40% (tr.355) → sách đọc: {thr['book_rule_reading']}" + (f"; trong biên ±{margin} nên hiển thị cả hai cách đọc (biên là của hệ thống)" if border else ""),
             "nhóm nhiều nhất theo tỉ trọng tổng điểm TVH: " + ", ".join(f"{g}={shares[g]:.3f}" for g in order)]
    res = []
    for dm, vi in options:
        g, row = pick(dm)
        if row is None:
            res.append({"dm": dm, "dm_vi": vi, "status": "khong_co_dong"})
            continue
        res.append({"dm": dm, "dm_vi": vi, "dominant": g, "yong": row["yong"], "van_tot": row["van_tot"], "van_xau": row["van_xau"], "page": row["page"],
                    "follows_book_rule": vi == thr["book_rule_reading"], **({"yong_inferred": row["inferred_note"]} if row.get("yong_inferred") else {})})
    if border:
        return {"method": "cach_cuc_tvh", "status": "hai_cach_doc", "cach": cach, "alternatives": res, "yong": [], "xi": [], "ji": [], "chou": [], "xian": [], "source": "SRC_TVH_DUNGTHAN",
                "threshold": thr, "trace": trace + ["không chọn một cách đọc; mỗi cách đọc tra dòng riêng của bảng"]}
    r0 = res[0]
    if "yong" not in r0:
        return _table("cach_cuc_tvh", "khong_co_dong", cach=cach, dm=r0["dm_vi"], threshold=thr, trace=trace + ["bảng không có dòng cho tổ hợp này"])
    trace.append(f"dòng bảng tr.{r0['page']}: nhóm nhiều nhất {r0['dominant']} → dụng thần {r0['yong']}" + (" (dụng thần của dòng này do hệ thống suy ra, sách không nêu: " + r0["yong_inferred"] + ")" if r0.get("yong_inferred") else ""))
    return _table("cach_cuc_tvh", "ap_dung", cach=cach, dm=r0["dm_vi"], dominant=r0["dominant"], yong=[r0["yong"][0]], yong_alternatives=r0["yong"],
                  xi=[g for g in (r0["van_tot"] or []) if g not in r0["yong"][:1]], ji=r0["van_xau"] or [], van_tot=r0["van_tot"], van_xau=r0["van_xau"], page=r0["page"], source="SRC_TVH_DUNGTHAN", threshold=thr, trace=trace, **({"yong_inferred": r0["yong_inferred"]} if r0.get("yong_inferred") else {}))


def thong_quan(S: dict, profile: SchoolProfile) -> dict:
    sh = {e: S["by_element"][e] / (sum(S["by_element"].values()) or 1) for e in ELEMENTS}
    wars = []
    for a in ELEMENTS:
        for b in ELEMENTS:
            if controls(a, b) and sh[a] >= profile.war_share and sh[b] >= profile.war_share:
                bridge = next(x for x in ELEMENTS if generates(a, x) and generates(x, b))
                wars.append({"attacker": a, "victim": b, "bridge": bridge, "bridge_share": round(sh[bridge], 3), "missing": sh[bridge] < profile.bridge_min})
    if not wars:
        return _table("thong_quan", "khong_co_giao_chien", trace=[f"không có cặp hành khắc nhau cùng ≥ {profile.war_share} tổng điểm"])
    return _table("thong_quan", "co_giao_chien", wars=wars, need_elements=sorted({w["bridge"] for w in wars if w["missing"]}),
                  trace=[f"{w['attacker']} khắc {w['victim']} (cùng ≥ {profile.war_share}); cầu {w['bridge']} chiếm {w['bridge_share']}" + (" → thiếu cầu" if w["missing"] else " → có cầu") for w in wars])


def thuan_the(geju: dict, S: dict | None = None, profile: SchoolProfile | None = None) -> dict:
    """Dụng thần thuận thế cho tòng/hóa. Vai trò lấy từ data/bazi_deep/tong_roles.json (Trích Thiên Tủy pp.171-179, verified text);
    hóa thần: 'vượng mà có dư cần tiết thần hóa thần, suy mà không đủ cần thần sinh trợ' (PDF pp.175-176)."""
    ch = [o for o in geju["outer"] if o["quality"] == "chân" and o.get("kind") not in TVH_KINDS]
    if not ch:
        gia = [o["name"] for o in geju["outer"] if o.get("kind") not in TVH_KINDS]
        return _table("thuan_the", "khong_chan" if not gia else "chi_co_gia", candidates=gia)
    n = ch[0]["name"]
    if n in TONG_ROLES["types"]:
        r = TONG_ROLES["types"][n]
        return _table("thuan_the", "ap_dung", outer=n, yong=r["yong"], xi=r["xi"], ji=r["ji"], source=r["src"], source_note=r["note"])
    # Hóa X
    el = n.replace(" (TVH)", "").split()[-1]
    out = _table("thuan_the", "ap_dung", outer=n, source="SRC_TTT_HOA")
    if S is not None:
        tot = sum(S["by_element"].values()) or 1.0
        share = S["by_element"].get(el, 0.0) / tot
        du = share >= (profile.hua_du_share if profile else 0.5)
        gen = next(x for x in ELEMENTS if generates(el, x))
        src = next(x for x in ELEMENTS if generates(x, el))
        out.update(hoa_than=el, hoa_than_share=round(share, 3), hoa_than_du=du,
                   need_elements=[gen] if du else [src, el], note=("hóa thần vượng có dư: cần tiết thần hóa thần làm dụng" if du else "hóa thần suy không đủ: cần thần sinh trợ hóa thần làm dụng"))
    else:
        out["note"] = "hóa khí: dụng là hóa thần và hành sinh ra nó"
    return out


def thuan_the_tvh(geju: dict) -> dict:
    """Same question as thuan_the, answered ONLY from the Thiệu Vĩ Hoa special cách (tr.381-386); the system/Trích Thiên Tủy outer cách never feed this method."""
    ch = [o for o in geju["outer"] if o["quality"] == "chân" and o.get("kind") in TVH_KINDS]
    if not ch:
        return _table("thuan_the_tvh", "khong_chan", note="không có cách đặc biệt chân theo Thiệu Vĩ Hoa", trace=["không có cách đặc biệt TVH đạt điều kiện chân"])
    n, kind = ch[0]["name"], ch[0].get("kind")
    if kind == "tong_tvh":                    # tr.381, 385: dụng thần and vận of tòng tài / tòng sát / tòng nhi
        r = TVH_DT["tong"][n]
        return _table("thuan_the_tvh", "ap_dung", outer=n, yong=r["yong"], xi=[g for g in r["van_tot"] if g not in r["yong"]], ji=r["van_xau"], source="SRC_TVH_DUNGTHAN", note=r.get("note", ""),
                      trace=[f"cách đặc biệt TVH: {n}", f"bảng tr.381/385: dụng thần {r['yong']}"])
    key = n.replace(" (TVH)", "")                 # chuyen_vuong / hoa_tvh, tr.381-382, 385-386: the element of the cách is the dụng thần
    r = TVH_DT["special"].get(key, {})
    el = ch[0].get("element") or r.get("element") or key.split()[-1]
    return _table("thuan_the_tvh", "ap_dung", outer=n, need_elements=[el], van_tot_elements=r.get("van_tot"), van_xau_elements=r.get("van_xau"), source="SRC_TVH_DUNGTHAN",
                  note="cách đặc biệt lấy theo thế vượng: dụng thần là hành của chính cách (tr.381-382)", trace=[f"cách đặc biệt TVH: {n}", f"dụng thần = hành của cách: {el}"])


def _has_root(view: ChartView, element: str, classes=("ban_khi", "trung_khi")) -> bool:
    return any(h["element"] == element and h["class"] in classes for p in ("year", "month", "day", "hour") for h in view.hidden(p))


def han_noan(view: ChartView, cl: dict) -> dict:
    """Trích Thiên Tủy PDF pp.113-114: hàn quá mà noãn hữu khí thì cần noãn; hàn quá mà noãn vô khí thì lấy hàn làm dụng; noãn quá mà hàn hữu căn
    thì cần hàn; noãn quá mà hàn vô căn thì không lấy hàn làm dụng. Ngưỡng 'quá' là chỉ số nhiệt thô của hệ thống (draft)."""
    lab = cl["label"]
    if lab in ("cực hàn", "hàn"):
        warm = _has_root(view, "Hỏa")
        return {"state": "han_qua", "noan_huu_khi": warm, "direction": "can_noan" if warm else "thuan_han", "src": "SRC_TTT_HANTHU",
                "note": "hàn quá, hỏa có khí (bản khí/trung khí) nên cần noãn" if warm else "hàn quá, hỏa vô khí nên phản lại lấy hàn làm dụng"}
    if lab in ("nhiệt", "cực nhiệt"):
        cold = _has_root(view, "Thủy", ("ban_khi", "trung_khi", "du_khi"))
        return {"state": "noan_qua", "han_huu_can": cold, "direction": "can_han" if cold else "thuan_noan", "src": "SRC_TTT_HANTHU",
                "note": "noãn quá, thủy có căn nên cần hàn" if cold else "noãn quá, thủy vô căn nên không lấy hàn làm dụng"}
    return {"state": "on_hoa", "direction": None, "src": "SRC_TTT_HANTHU", "note": "chưa tới mức hàn/nhiệt quá theo chỉ số thô"}


def thuong_quan_dung(ctx, S: dict, geju: dict, profile: SchoolProfile) -> dict | None:
    """Năm cách Thương Quan dụng X (Trích Thiên Tủy PDF pp.93-94). Chỉ chạy khi nội cách đầu tiên là Thương Quan."""
    inner = geju["inner"][0] if geju["inner"] else None
    if not inner or inner["name"] != "Thương Quan":
        return None
    sh, idx = S["shares"], S["level_index"]
    tv = sh["ThucThuong"] >= profile.thuong_vuong
    has_sh = {"An": sh["An"], "Tai": sh["Tai"], "QuanSat": sh["QuanSat"]}
    has = lambda g: has_sh[g] >= profile.presence_share        # the book speaks of the group being in the chart at all; a hidden 3-degree stem is not that
    style = None
    if idx <= 2 and tv:
        style = "an" if has("An") else "kiep"
    elif idx >= 4 and not has("Tai") and not has("QuanSat"):
        style = "thuong"                     # PDF p.93: nhật chủ vượng, không có Tài Quan -> dụng Thương Quan (checked before 'tai')
    elif idx >= 4 and tv:
        style = "tai"
    elif idx >= 4 and not tv and sh["Tai"] < 0.10 and pred(ctx, "count_visible_ge:Ti=2")[0]:
        style = "quan"
    if style is None:
        return {"style": None, "note": "không khớp một trong năm mẫu của sách (nhật chủ ở mức trung hòa hoặc thiếu điều kiện)", "src": TQ["src"]}
    row = TQ["styles"][style]
    return {"style": style, "when": row["when"], "yong": row["yong"], "xi": row["xi"], "ji": row["ji"], "quan": row["quan"], "van": row["van"], "src": TQ["src"],
            "inputs": {"level": S["level"], "thuong_vuong": tv, "an": has("An"), "tai": has("Tai"), "quan_sat": has("QuanSat")}}


def khuyet_hanh(view: ChartView) -> dict:
    """Ngũ hành không đầy đủ → chọn hành thiếu làm dụng thần. Căn cứ DUY NHẤT: Thiệu Vĩ Hoa tr.399, ví dụ 3 ('thiếu mộc, thiếu thủy ... dụng thần nên chọn thủy, mộc').
    Sách không phát biểu đây là quy tắc chung, nên phương pháp này là draft. 'Có mặt' = có can thấu hoặc tàng can (mọi loại khí) của hành đó."""
    present = {STEM_ELEMENT[s] for s in view.stems} | {h["element"] for p in ("year", "month", "day", "hour") for h in view.hidden(p)}
    missing = [e for e in ELEMENTS if e not in present]
    from .strength import group_of_element
    trace = ["hành có mặt (thấu + tàng): " + ", ".join(e for e in ELEMENTS if e in present), "hành thiếu: " + (", ".join(missing) if missing else "không")]
    if not missing:
        return _table("khuyet_hanh", "khong_ap_dung", note="ngũ hành đủ", trace=trace)
    groups = []
    for e in missing:
        g = group_of_element(view.dm_element, e)
        if g not in groups:
            groups.append(g)
    return _table("khuyet_hanh", "ap_dung", yong=groups, need_elements=missing, note="một ví dụ của sách (tr.399); không có thứ tự ưu tiên giữa các hành thiếu", trace=trace + [f"nhóm so với Nhật Chủ: {groups}"])


def health(ctx: Ctx, group: str) -> dict:
    """Dụng có dùng được không (BZ-42): hiện diện, thấu hay chỉ tàng, có bị hợp trói không."""
    vis = ctx.vis_in(group) if group in ("Ti", "An", "Tai", "Quan", "Sat", "QuanSat", "Thuc", "Thuong", "ThucThuong") else []
    any_, why = pred(ctx, f"any:{group}")
    bound = pred(ctx, f"bound:{group}")[0]
    return {"group": group, "present": any_, "visible": bool(vis), "bound": bound, "usable": any_ and not bound}


def run(view: ChartView, profile: SchoolProfile, R, S: dict, geju: dict) -> dict:
    ctx = Ctx(view, profile, R, S)
    tvh_S = bool(S.get("tvh"))
    if tvh_S:           # isolation: the system / Trích Thiên Tủy school must not be altered by Thiệu Vĩ Hoa's scoring or his special cách, so it is recomputed from its own inputs
        sysp = profile.with_(strength_method="he_thong", id=profile.id + "+he_thong_view")
        S_sys = strength_compute(view, sysp, R)
        G_sys = geju_analyse(view, sysp, R, S_sys)
    else:
        sysp, S_sys, G_sys = profile, S, geju
    tvh_outer = [o for o in geju["outer"] if o.get("kind") in TVH_KINDS]       # reverse isolation: the TVH methods see only TVH outer cách, never the system's
    G_tvh = {**geju, "outer": tvh_outer, "readings": build_readings(geju["inner"], tvh_outer)[0]}
    outer_chan = any(o["quality"] == "chân" for o in G_sys["outer"])
    tq = thuong_quan_dung(Ctx(view, sysp, R, S_sys), S_sys, G_sys, sysp)
    methods = [phu_uc(S_sys, outer_chan), dieu_hau(view, S), cach_cuc(G_sys, tq), cach_cuc_tvh(G_tvh, S, profile), thong_quan(S, profile), thuan_the(G_sys, S_sys, sysp), thuan_the_tvh(G_tvh), khuyet_hanh(view)]
    basis = {"phu_uc": "he_thong (tách khỏi điểm TVH)" if tvh_S else "he_thong", "dieu_hau": "không dùng khí thế (chỉ bảng)",
             "cach_cuc": "he_thong (tách khỏi điểm TVH)", "cach_cuc_tvh": "tvh_40 (điểm TVH)" if tvh_S else "he_thong (dự phòng, không có điểm TVH)",
             "thong_quan": "he_thong (tỉ trọng hành)", "thuan_the": "he_thong (tách khỏi điểm TVH)", "thuan_the_tvh": "tvh_40 (cách đặc biệt TVH)" if tvh_S else "không có (profile không dùng TVH)",
             "khuyet_hanh": "không dùng khí thế (chỉ hiện diện hành)"}
    for m in methods:
        m["meta"] = dict(METHOD_META[m["method"]], strength_basis=basis[m["method"]], applied=m["status"] in APPLIED)
        m.setdefault("trace", [m.get("note") or f"trạng thái: {m['status']}"])
    for m in methods:
        for role in ("yong", "xi"):
            m[f"{role}_health"] = [health(ctx, g) for g in m.get(role, [])]
    return {"methods": {m["method"]: m for m in methods}, "thuong_quan": tq, "comparison": compare(methods), "review_status": "draft",
            "isolation": {"system_school_computed_from": "he_thong" if tvh_S else "profile hiện tại", "tvh_school": "tvh_40" if tvh_S else None,
                  "note": "cach_cuc và thuan_the dùng cách cục/khí thế của hệ thống ngay cả khi profile là tvh_40; cách đặc biệt và điểm TVH chỉ đi vào cach_cuc_tvh và thuan_the_tvh; ngược lại cach_cuc_tvh và thuan_the_tvh không thấy ngoại cách của hệ thống. phu_uc cũng dùng khí thế và ngoại cách của hệ thống; quyết định vượng/nhược 40% của Thiệu Vĩ Hoa chỉ xuất hiện ở strength_after và cach_cuc_tvh."},
            "note": "Các phương pháp không được gộp. Bảng 'comparison' chỉ liệt kê đồng thuận và bất đồng."}


def _flat(m: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    if m.get("status") == "hai_cach_doc":
        return out
    for r in ROLES:
        for g in m.get(r, []):
            out.setdefault(g, r)
    return out


def compare(methods: list[dict]) -> dict:
    per = {m["method"]: _flat(m) for m in methods}
    groups = sorted({g for d in per.values() for g in d})
    rows, disagreements = [], []
    for g in groups:
        roles = {meth: d[g] for meth, d in per.items() if g in d}
        good = [m for m, r in roles.items() if r in ("yong", "xi")]
        bad = [m for m, r in roles.items() if r in ("ji", "chou")]
        row = {"group": g, "label": GROUP_VI.get(g, g), "roles": roles}
        rows.append(row)
        if good and bad:
            disagreements.append({"group": g, "label": GROUP_VI.get(g, g), "favourable_in": good, "unfavourable_in": bad})
    applic = {m["method"]: {"status": m["status"], "applied": m["status"] in APPLIED, **{k: v for k, v in (m.get("meta") or {}).items() if k in ("verification", "applies_when", "strength_basis")}} for m in methods}
    return {"rows": rows, "disagreements": disagreements, "consensus": [r["group"] for r in rows if len(set(r["roles"].values())) == 1 and len(r["roles"]) >= 2],
            "methods": applic, "no_final_answer": True,
            "note": "Không có kết luận cuối: bất đồng được liệt kê cùng điều kiện áp dụng và mức xác minh của từng phương pháp; không cộng điểm giữa các phương pháp."}
