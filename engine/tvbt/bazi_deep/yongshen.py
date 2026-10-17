"""Dụng Thần Engine: MỖI PHƯƠNG PHÁP MỘT BẢNG RIÊNG (Dụng / Hỷ / Kỵ / Cừu / Nhàn theo nhóm thập thần), không trộn.
Phương pháp: phù ức, điều hậu (thô, chưa có bảng 窮通寶鑑), cách cục, thông quan, thuận thế (tòng/hóa). Sau cùng
compare() chỉ đặt các bảng cạnh nhau và chỉ ra chỗ bất đồng; không có bước nào chọn 'đáp án cuối'.
Mọi bảng vai trò là he_thong/draft (Tử Bình Chân Thuyên, Tích Thiên Tủy chưa được đối chiếu)."""
from __future__ import annotations

import json

from ..ganzhi import ELEMENTS, STEM_ELEMENT, controls, generates
from ..bazi import HIDDEN_STEMS
from .geju import Ctx, pred
from .model import ChartView
from .profile import DATA, LEVELS, SchoolProfile
from .season import climate
from .strength import GROUP_VI

ROLES = ["yong", "xi", "ji", "chou", "xian"]
TONG_ROLES = json.loads((DATA / "tong_roles.json").read_text("utf-8"))
TQ = json.loads((DATA / "thuong_quan_dung.json").read_text("utf-8"))
TVH_DT = json.loads((DATA / "tvh_dungthan.json").read_text("utf-8"))


def _table(method: str, status: str, **roles) -> dict:
    t = {r: list(roles.get(r, [])) for r in ROLES}
    extra = {k: v for k, v in roles.items() if k not in ROLES}
    return {"method": method, "status": status, **t, **extra}


def phu_uc(S: dict, outer_chan: bool) -> dict:
    """Nhược -> Ấn/Tỉ; vượng -> khắc tiết hao. Chỉ chạy khi khí thế rõ và không có ngoại cách chân."""
    if outer_chan:
        return _table("phu_uc", "khong_ap_dung", note="ngoại cách chân: phù ức không áp dụng")
    lv = S["level_index"]
    if S["ambiguous"]:
        alts = []
        for name in S["readings"]:
            alts.append(phu_uc({**S, "level_index": LEVELS.index(name), "ambiguous": False}, False))
        return {"method": "phu_uc", "status": "hai_cach_doc", "alternatives": [dict(a, level=n) for a, n in zip(alts, S["readings"])],
                "yong": [], "xi": [], "ji": [], "chou": [], "xian": []}
    if lv <= 2:
        return _table("phu_uc", "ap_dung", level=LEVELS[lv], yong=["An"], xi=["Ti"], ji=["Tai", "QuanSat", "ThucThuong"])
    if lv >= 4:
        return _table("phu_uc", "ap_dung", level=LEVELS[lv], yong=["QuanSat", "ThucThuong", "Tai"], ji=["An", "Ti"])
    return _table("phu_uc", "khong_ap_dung", level=LEVELS[lv], note="trung hòa: phù ức không nghiêng về phía nào")


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
    t["need_elements"], t["avoid_elements"] = (["Hỏa"], ["Thủy"]) if h <= -1 else (["Thủy"], ["Hỏa"]) if h >= 1.5 else ([], [])
    t["han_noan"] = han_noan(view, cl)
    t["note"] = "Tập can dùng được lấy từ bảng dụng thần dự bị của Thiệu Vĩ Hoa (tr.389-390, đã đối chiếu); can 'chính' chọn theo thứ tự bảng 窮通寶鑑 nhập từ trí nhớ (draft). Vai trò: can chính là Dụng, các can còn lại là Hỷ. Chỉ số nhiệt thô chỉ để đối chiếu."
    return t


def cach_cuc(geju: dict, tq: dict | None = None) -> dict:
    prim = geju["readings"][0] if geju["readings"] else None
    if not prim or prim["kind"] != "noi_cach":
        return _table("cach_cuc", "khong_xac_dinh_noi_cach", note="nội cách không lập được hoặc bị ngoại cách thay")
    c = next(x for x in geju["inner"] if x["name"] == prim["cach"])
    if tq and tq.get("style"):               # Thương Quan: the book's own five styles replace the generic table
        return _table("cach_cuc", "ap_dung_ttt_thuong_quan", cach=c["name"], cach_state=c["state"], yong=tq["yong"], xi=tq["xi"], ji=tq["ji"], style=tq["style"], source=tq["src"], van=tq["van"])
    if c["state"] in ("bai",):
        return _table("cach_cuc", "cach_bai", cach=c["name"], yong=c["yong_groups"], bai=[b["id"] for b in c["bai"]],
                      note="cách bại chưa được cứu: dụng thần nêu theo bảng nhưng cần coi là vô lực")
    return _table("cach_cuc", "ap_dung", cach=c["name"], cach_state=c["state"], yong=c["yong_groups"])


def _tvh_row(key: str, dm: str, dom: str):
    return next((r for r in TVH_DT["rows"] if r["cach"] == key and r["dm"] == dm and r["dom"] == dom), None)


def cach_cuc_tvh(geju: dict, S: dict) -> dict:
    """Dụng thần theo cách của Thiệu Vĩ Hoa (pp.378-386): (cách, nhật chủ vượng/nhược theo quy tắc 40%, nhóm nhiều nhất) -> dụng thần và vận tốt/xấu.
    Method separate from cach_cuc (which follows the system's own draft tables and Trích Thiên Tủy for Thương Quan)."""
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
    order = sorted(S["shares"], key=lambda g: -S["shares"][g])

    def pick(dm):
        for g in order:
            row = _tvh_row(key, dm, g)
            if row:
                return g, row
        return None, None
    options = [("strong", "vượng"), ("weak", "nhược")] if border else [("strong" if strong else "weak", "vượng" if strong else "nhược")]
    res = []
    for dm, vi in options:
        g, row = pick(dm)
        if row is None:
            res.append({"dm": dm, "dm_vi": vi, "status": "khong_co_dong"})
            continue
        res.append({"dm": dm, "dm_vi": vi, "dominant": g, "yong": row["yong"], "van_tot": row["van_tot"], "van_xau": row["van_xau"], "page": row["page"]})
    if border:
        return {"method": "cach_cuc_tvh", "status": "hai_cach_doc", "cach": cach, "alternatives": res, "yong": [], "xi": [], "ji": [], "chou": [], "xian": [], "source": "SRC_TVH_DUNGTHAN"}
    r0 = res[0]
    if "yong" not in r0:
        return _table("cach_cuc_tvh", "khong_co_dong", cach=cach, dm=r0["dm_vi"])
    return _table("cach_cuc_tvh", "ap_dung", cach=cach, dm=r0["dm_vi"], dominant=r0["dominant"], yong=[r0["yong"][0]], yong_alternatives=r0["yong"],
                  xi=[g for g in (r0["van_tot"] or []) if g not in r0["yong"][:1]], ji=r0["van_xau"] or [], van_tot=r0["van_tot"], van_xau=r0["van_xau"], page=r0["page"], source="SRC_TVH_DUNGTHAN")


def thong_quan(S: dict, profile: SchoolProfile) -> dict:
    sh = {e: S["by_element"][e] / (sum(S["by_element"].values()) or 1) for e in ELEMENTS}
    wars = []
    for a in ELEMENTS:
        for b in ELEMENTS:
            if controls(a, b) and sh[a] >= profile.war_share and sh[b] >= profile.war_share:
                bridge = next(x for x in ELEMENTS if generates(a, x) and generates(x, b))
                wars.append({"attacker": a, "victim": b, "bridge": bridge, "bridge_share": round(sh[bridge], 3), "missing": sh[bridge] < profile.bridge_min})
    if not wars:
        return _table("thong_quan", "khong_co_giao_chien")
    return _table("thong_quan", "co_giao_chien", wars=wars, need_elements=sorted({w["bridge"] for w in wars if w["missing"]}))


def thuan_the(geju: dict, S: dict | None = None, profile: SchoolProfile | None = None) -> dict:
    """Dụng thần thuận thế cho tòng/hóa. Vai trò lấy từ data/bazi_deep/tong_roles.json (Trích Thiên Tủy pp.171-179, verified text);
    hóa thần: 'vượng mà có dư cần tiết thần hóa thần, suy mà không đủ cần thần sinh trợ' (PDF pp.175-176)."""
    ch = [o for o in geju["outer"] if o["quality"] == "chân"]
    if not ch:
        gia = [o["name"] for o in geju["outer"]]
        return _table("thuan_the", "khong_chan" if not gia else "chi_co_gia", candidates=gia)
    n = ch[0]["name"]
    kind = ch[0].get("kind")
    if kind == "tong_tvh":                    # Thiệu Vĩ Hoa pp.381, 385: dụng thần and vận of tòng tài / tòng sát / tòng nhi
        r = TVH_DT["tong"][n]
        return _table("thuan_the", "ap_dung", outer=n, yong=r["yong"], xi=[g for g in r["van_tot"] if g not in r["yong"]], ji=r["van_xau"], source="SRC_TVH_DUNGTHAN", note=r.get("note", ""))
    if kind in ("chuyen_vuong", "hoa_tvh"):   # pp.381-382, 385-386: take the element of the cách as dụng thần
        key = n.replace(" (TVH)", "")
        r = TVH_DT["special"].get(key, {})
        el = ch[0].get("element") or r.get("element") or key.split()[-1]
        return _table("thuan_the", "ap_dung", outer=n, need_elements=[el], van_tot_elements=r.get("van_tot"), van_xau_elements=r.get("van_xau"), source="SRC_TVH_DUNGTHAN",
                      note="cách đặc biệt lấy theo thế vượng: dụng thần là hành của chính cách (tr.381-382)")
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


def health(ctx: Ctx, group: str) -> dict:
    """Dụng có dùng được không (BZ-42): hiện diện, thấu hay chỉ tàng, có bị hợp trói không."""
    vis = ctx.vis_in(group) if group in ("Ti", "An", "Tai", "Quan", "Sat", "QuanSat", "Thuc", "Thuong", "ThucThuong") else []
    any_, why = pred(ctx, f"any:{group}")
    bound = pred(ctx, f"bound:{group}")[0]
    return {"group": group, "present": any_, "visible": bool(vis), "bound": bound, "usable": any_ and not bound}


def run(view: ChartView, profile: SchoolProfile, R, S: dict, geju: dict) -> dict:
    ctx = Ctx(view, profile, R, S)
    outer_chan = any(o["quality"] == "chân" for o in geju["outer"])
    tq = thuong_quan_dung(ctx, S, geju, profile)
    methods = [phu_uc(S, outer_chan), dieu_hau(view, S), cach_cuc(geju, tq), cach_cuc_tvh(geju, S), thong_quan(S, profile), thuan_the(geju, S, profile)]
    for m in methods:
        for role in ("yong", "xi"):
            m[f"{role}_health"] = [health(ctx, g) for g in m.get(role, [])]
    return {"methods": {m["method"]: m for m in methods}, "thuong_quan": tq, "comparison": compare(methods), "review_status": "draft",
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
    return {"rows": rows, "disagreements": disagreements, "consensus": [r["group"] for r in rows if len(set(r["roles"].values())) == 1 and len(r["roles"]) >= 2]}
