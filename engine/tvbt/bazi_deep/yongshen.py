"""Dụng Thần Engine: MỖI PHƯƠNG PHÁP MỘT BẢNG RIÊNG (Dụng / Hỷ / Kỵ / Cừu / Nhàn theo nhóm thập thần), không trộn.
Phương pháp: phù ức, điều hậu (thô, chưa có bảng 窮通寶鑑), cách cục, thông quan, thuận thế (tòng/hóa). Sau cùng
compare() chỉ đặt các bảng cạnh nhau và chỉ ra chỗ bất đồng; không có bước nào chọn 'đáp án cuối'.
Mọi bảng vai trò là he_thong/draft (Tử Bình Chân Thuyên, Tích Thiên Tủy chưa được đối chiếu)."""
from __future__ import annotations

from ..ganzhi import ELEMENTS, controls, generates
from .geju import Ctx, pred
from .model import ChartView
from .profile import LEVELS, SchoolProfile
from .season import climate
from .strength import GROUP_VI

ROLES = ["yong", "xi", "ji", "chou", "xian"]


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
    t = _table("dieu_hau", "bang_CTBG_draft", yong=[main], xi=[g for g in groups if g != main], table=tb, climate=cl)
    h = cl["heat"]
    t["need_elements"], t["avoid_elements"] = (["Hỏa"], ["Thủy"]) if h <= -1 else (["Thủy"], ["Hỏa"]) if h >= 1.5 else ([], [])
    t["note"] = "Ô bảng điều hậu nhập từ trí nhớ, chưa đối chiếu 窮通寶鑑 (draft). Vai trò: can đầu của ô là Dụng, các can sau là Hỷ. Chỉ số nhiệt thô chỉ để đối chiếu."
    return t


def cach_cuc(geju: dict) -> dict:
    prim = geju["readings"][0] if geju["readings"] else None
    if not prim or prim["kind"] != "noi_cach":
        return _table("cach_cuc", "khong_xac_dinh_noi_cach", note="nội cách không lập được hoặc bị ngoại cách thay")
    c = next(x for x in geju["inner"] if x["name"] == prim["cach"])
    if c["state"] in ("bai",):
        return _table("cach_cuc", "cach_bai", cach=c["name"], yong=c["yong_groups"], bai=[b["id"] for b in c["bai"]],
                      note="cách bại chưa được cứu: dụng thần nêu theo bảng nhưng cần coi là vô lực")
    return _table("cach_cuc", "ap_dung", cach=c["name"], cach_state=c["state"], yong=c["yong_groups"])


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


def thuan_the(geju: dict) -> dict:
    ch = [o for o in geju["outer"] if o["quality"] == "chân"]
    if not ch:
        gia = [o["name"] for o in geju["outer"]]
        return _table("thuan_the", "khong_chan" if not gia else "chi_co_gia", candidates=gia)
    n = ch[0]["name"]
    if n == "Tòng Tài":
        return _table("thuan_the", "ap_dung", outer=n, yong=["Tai"], xi=["ThucThuong", "QuanSat"], ji=["Ti", "An"])
    if n == "Tòng Sát":
        return _table("thuan_the", "ap_dung", outer=n, yong=["QuanSat"], xi=["Tai"], ji=["An", "Ti"])
    if n == "Tòng Nhi":
        return _table("thuan_the", "ap_dung", outer=n, yong=["ThucThuong"], xi=["Tai"], ji=["An"])
    return _table("thuan_the", "ap_dung", outer=n, note="hóa khí: dụng là hóa thần và hành sinh ra nó (chưa chuyển sang vai trò thập thần)")


def health(ctx: Ctx, group: str) -> dict:
    """Dụng có dùng được không (BZ-42): hiện diện, thấu hay chỉ tàng, có bị hợp trói không."""
    vis = ctx.vis_in(group) if group in ("Ti", "An", "Tai", "Quan", "Sat", "QuanSat", "Thuc", "Thuong", "ThucThuong") else []
    any_, why = pred(ctx, f"any:{group}")
    bound = pred(ctx, f"bound:{group}")[0]
    return {"group": group, "present": any_, "visible": bool(vis), "bound": bound, "usable": any_ and not bound}


def run(view: ChartView, profile: SchoolProfile, R, S: dict, geju: dict) -> dict:
    ctx = Ctx(view, profile, R, S)
    outer_chan = any(o["quality"] == "chân" for o in geju["outer"])
    methods = [phu_uc(S, outer_chan), dieu_hau(view, S), cach_cuc(geju), thong_quan(S, profile), thuan_the(geju)]
    for m in methods:
        for role in ("yong", "xi"):
            m[f"{role}_health"] = [health(ctx, g) for g in m.get(role, [])]
    return {"methods": {m["method"]: m for m in methods}, "comparison": compare(methods), "review_status": "draft",
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
