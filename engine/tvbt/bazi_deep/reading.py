"""Bát Tự deep reading composer (reading/1): seven chapters built from the deterministic analysis, with an explicit chain
dữ kiện -> quy tắc -> điều kiện -> kết luận for every statement, a fixed basis vocabulary and no LLM.

Architecture (docs/BAZI_DEEP_INTERPRETATION_ARCHITECTURE.md):
  analysis (pipeline.analyse)  +  rule engine over the 八字真宗 packs  +  timeline
        -> providers (generic code, one per evidence layer) -> Items {basis, direction, chain, sources, certainty}
        -> chapter spec (data/bazi_deep/reading_spec.json) routes Items into 7 chapters + a foundation block
        -> composer orders, summarises (headlines of the chosen Items only), pairs opposing Items without merging them.
Nothing here writes a sentence about a particular chart: every sentence is a template whose slots are filled from computed facts or from a cited rule's own text.
Basis vocabulary: tinh_toan (computed fact) | co_nguon (reading attributed to a cited page) | truong_phai (school/draft hypothesis) | chua_du_can_cu (insufficient basis)."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field

from ..ganzhi import BRANCH_ELEMENT, BRANCHES_VI, STEMS_VI
from .model import GOD_GROUPS, PIL_VI, PILLARS, ChartView, group_of
from .profile import DATA, TVH_40

SPEC = json.loads((DATA / "reading_spec.json").read_text("utf-8"))
SRC_BOOKS = {s["id"]: s for s in json.loads((DATA / "sources_books.json").read_text("utf-8"))["sources"]}
UI = json.loads((DATA / "ui_strings_vi.json").read_text("utf-8"))
SRC_ZZ = {"SRC_BAZI_ZHENZONG": {"id": "SRC_BAZI_ZHENZONG", "title": "八字真宗 (Bát Tự Chân Tông)"}}
BASIS_ORDER = {"co_nguon": 0, "tinh_toan": 1, "truong_phai": 2, "chua_du_can_cu": 3}
GV = SPEC["group_vi"]
STATE_VI = {"thanh": "thành", "thanh_nhung_bi_pha": "thành nhưng bị phá", "bai": "bại", "bai_cuu_yeu": "bại nhưng được cứu yếu", "bai_co_cuu": "bại nhưng được cứu", "chua_ro": "chưa rõ"}
POLARITY_DIR = {"cat": "thuan", "hung": "bat_loi"}
EFFECT_VI = {"pha_cach": "phá cách", "tro_cach": "trợ cách", "doi_cach": "đổi cách", "trung_tinh": "không đổi cách"}
ROLE_VI = {"yong": "Dụng", "xi": "Hỷ", "ji": "Kỵ", "chou": "Cừu", "xian": "Nhàn"}


@dataclass
class Item:
    id: str
    chapter: str
    section: str
    basis: str
    headline: str
    easy: str
    expert: str
    chain: list[dict] = field(default_factory=list)
    sources: list[dict] = field(default_factory=list)
    direction: str = "trung_tinh"          # thuan | bat_loi | trung_tinh | cau_truc
    school: str = "he_thong"               # he_thong | tvh | ttt | zz
    review: str = "computed"               # verified | draft | computed
    kind: str = "cau_truc"                 # sach (a cited book rule) | phuong_phap (a dụng thần method) | cau_truc (structural role) | tinh_toan | gioi_han
    pillar_refs: list[str] = field(default_factory=list)
    caveats: list[str] = field(default_factory=list)
    refs: list[str] = field(default_factory=list)
    counter: list[str] = field(default_factory=list)
    table: list[dict] | None = None

    def out(self) -> dict:
        d = asdict(self)
        for k in ("headline", "easy", "expert"):
            d[k] = vi(d[k])
        d["chain"] = [{**c, "text": vi(c["text"])} for c in d["chain"]]
        d["caveats"] = [vi(c) for c in d["caveats"]]
        for sct in d["sources"]:
            sct["title"] = vi(sct["title"])
            if sct.get("page"):
                sct["page"] = vi(sct["page"])
        d["basis_vi"] = SPEC["basis"][self.basis]
        d["certainty_vi"] = SPEC["certainty"][self.basis]
        if d["table"] is None:
            del d["table"]
        return d


_TOK = {**UI["token_labels"], "pha_cach": "phá cách", "tro_cach": "trợ cách", "doi_cach": "đổi cách", "trung_tinh": "không đổi cách", "bai_cuu_yeu": "bại nhưng được cứu yếu",
        "dm": "Nhật Chủ", "cach_cuc_tvh": "cách cục theo Thiệu Vĩ Hoa", "thuan_the": "thuận thế", "khong_xac_dinh_noi_cach": "chưa xác định nội cách", "ban_khi": "bản khí", "trung_khi": "trung khí", "du_khi": "dư khí"}
_TOK_RE = re.compile(r"\b(" + "|".join(sorted((re.escape(k) for k in _TOK if len(k) > 3), key=len, reverse=True)) + r")\b")
_GRP = {"Ti": GV["Ti"], "An": GV["An"], "Tai": GV["Tai"], "QuanSat": GV["QuanSat"], "ThucThuong": GV["ThucThuong"]}


def vi(text: str) -> str:
    """Last-mile cleaning of every text field: internal identifiers, source ids and Python list reprs become plain Vietnamese. Idempotent."""
    t = str(text)
    t = re.sub(r"SRC_[A-Z_]+", lambda m: UI["source_labels"].get(m.group(0), m.group(0)), t)
    t = re.sub(r"\s*→ khóa bảng '?\w+'?", "", t)
    t = re.sub(r"\[([^\[\]]*)\]", lambda m: re.sub(r"'", "", m.group(1)), t)
    t = re.sub(r"'(Ti|An|Tai|QuanSat|ThucThuong)'", lambda m: _GRP[m.group(1)], t)
    t = _TOK_RE.sub(lambda m: _TOK[m.group(1)], t)
    t = re.sub(r"\b(Ti|An|Tai)=", lambda m: _GRP[m.group(1)] + "=", t)
    return t


def step(kind: str, text: str) -> dict:
    return {"step": kind, "label": SPEC["chain_steps"][kind], "text": text}


def chain(du_kien: str, quy_tac: str, dieu_kien: str, ket_luan: str) -> list[dict]:
    return [step("du_kien", du_kien), step("quy_tac", quy_tac), step("dieu_kien", dieu_kien), step("ket_luan", ket_luan)]


def src(sid: str, page: str | None = None) -> dict:
    s = SRC_BOOKS.get(sid) or SRC_ZZ.get(sid) or {"id": sid, "title": sid}
    out = {"id": sid, "title": s.get("title", sid)}
    if page:
        out["page"] = page
    elif s.get("locator"):
        out["page"] = s["locator"]
    return out


# ---------------------------------------------------------------- vocabulary helpers
def gname(g: str) -> str:
    return GV.get(g, g)


def glist(gs: list[str]) -> str:
    return ", ".join(gname(g) for g in gs) if gs else "không có"


def plain_tokens(text: str) -> str:
    """Technical identifiers inside engine evidence strings -> Vietnamese (for the expert text)."""
    t = str(text)
    for k, v in GV.items():
        t = re.sub(rf"\b{k}\b", v, t)
    t = re.sub(r"\b(year|month|day|hour)\.stem\b", lambda m: f"can {PIL_VI[m.group(1)]}", t)
    t = re.sub(r"\b(year|month|day|hour)\.branch\b", lambda m: f"chi {PIL_VI[m.group(1)]}", t)
    t = re.sub(r"\('(year|month|day|hour)', '([^']+)'\)", lambda m: f"({PIL_VI[m.group(1)]}: {m.group(2)})", t)
    t = t.replace("ban_khi", "bản khí").replace("trung_khi", "trung khí").replace("du_khi", "dư khí").replace("thấu [", "thấu [")
    t = t.replace("'", "")
    return t


def pc(view: ChartView, p: str, kind: str = "stem") -> str:
    if kind == "stem":
        s = view.stem(p)
        god = "Nhật Chủ" if p == "day" else view.god(s)
        return f"can {PIL_VI[p]} {STEMS_VI[s]} ({god})"
    return f"chi {PIL_VI[p]} {BRANCHES_VI[view.branch(p)]}"


def four_pillars(view: ChartView) -> str:
    return " – ".join(f"{PIL_VI[p].capitalize()}: {STEMS_VI[view.stem(p)]} {BRANCHES_VI[view.branch(p)]}" for p in PILLARS)


def group_of_stem(view: ChartView, stem: int) -> str:
    return group_of(view.god(stem))


# ---------------------------------------------------------------- foundation providers
def f_nguyet_lenh(A: dict, view: ChartView) -> list[Item]:
    S, season = A["strength_after"], A["season"]
    mb, el, state = BRANCHES_VI[view.month_branch], S["dm_element"], S["season_state"]
    plain = SPEC["season_state_plain"].get(state, state)
    cmd = season.get("command") or {}
    tu = (f"Tư lệnh: {cmd['name']} ({cmd['element']}), {cmd['day_in_month']} ngày kể từ tiết." if cmd and cmd.get("day_in_month") is not None else "Chưa biết ngày vào tiết nên chưa xét tư lệnh.")
    return [Item(
        id="nen-tang.nguyet-lenh", chapter="nen-tang", section="nguyet-lenh", basis="tinh_toan", school="ttt", review="computed",
        headline=f"Nhật Chủ {STEMS_VI[view.dm]} ({el}) sinh tháng {mb}: thế “{state}”",
        easy=f"Bạn sinh vào tháng {mb}, khí của tháng thuộc hành {BRANCH_ELEMENT[view.month_branch]}. Lúc đó hành của Nhật Chủ ({el}) {plain}. Đây là yếu tố nặng nhất khi xét sức của Nhật Chủ.",
        expert=f"Nguyệt lệnh {mb} ({BRANCH_ELEMENT[view.month_branch]}); Nhật Chủ {STEMS_VI[view.dm]} hành {el} ở trạng thái {state} (vượng–tướng–hưu–tù–tử). {tu}",
        chain=chain(f"Chi tháng {mb} ({BRANCH_ELEMENT[view.month_branch]}); Nhật Chủ {STEMS_VI[view.dm]} hành {el}",
                    "Nguyệt lệnh quyết định hành nào được mùa giúp; năm trạng thái vượng–tướng–hưu–tù–tử (Trích Thiên Tủy, chương nguyệt lệnh)",
                    f"{el} gặp mùa {BRANCH_ELEMENT[view.month_branch]} → {state}", f"Nhật Chủ ở thế “{state}”: {plain}"),
        sources=[src("SRC_TTT_NGUYETLENH")], pillar_refs=["month.branch", "day.stem"],
        caveats=["Bảng vượng–tướng–hưu–tù–tử là tra cứu; ý nghĩa 'nặng nhất' là nguyên tắc của Trích Thiên Tủy, không phải con số."])]


def f_khi_the(A: dict, view: ChartView) -> list[Item]:
    S = A["strength_after"]
    tv = S["tvh"]
    own = tv["own_share"]
    near = abs(own - 0.40) < TVH_40.tvh_margin
    strong = tv["dm_strong"]
    shares = sorted(S["shares"].items(), key=lambda kv: -kv[1])
    items = []
    reading = "vượng" if strong else "nhược"
    items.append(Item(
        id="nen-tang.khi-the-tvh", chapter="nen-tang", section="khi-the", basis="co_nguon", school="tvh", review="verified",
        headline=f"Phe Nhật Chủ chiếm {own * 100:.1f}% tổng sức: đọc là {reading}" + (" (sát ngưỡng 40%)" if near else ""),
        easy=f"Gộp sức của các hành đồng hành với Nhật Chủ (cùng hành và hành sinh ra nó), được {own * 100:.1f}% tổng sức. Theo Thiệu Vĩ Hoa, từ 40% trở lên là vượng, dưới là nhược, nên lá số này đọc là {reading}." +
             (" Vì con số sát ngưỡng, kết luận này có thể đảo chiều nếu cách tính khác đi một chút; hãy xem đây là một khả năng, không phải điều chắc." if near else ""),
        expert=f"Điểm TVH (độ, tr.331–355): phe mình = {own:.4f} so với ngưỡng 0,40 (tr.355: lớn hơn → vượng, nhỏ hơn → nhược; đúng 40% tính là vượng theo quy ước hệ thống) → {reading}." +
               (f" |share − 0,40| < {TVH_40.tvh_margin}: biên hiển thị của hệ thống, nên cả hai cách đọc được giữ." if near else ""),
        chain=chain(f"Tổng điểm các hành: {', '.join(f'{k} {v:.1f}' for k, v in tv['totals'].items())}; phe mình = {own:.4f}",
                    "Thiệu Vĩ Hoa tr.355: Nhật Chủ vượng khi phe mình lớn hơn 40% tổng độ, nhược khi nhỏ hơn",
                    f"{own:.4f} {'≥' if strong else '<'} 0,40" + ("; nằm trong biên ±0,03 nên có hai cách đọc" if near else ""),
                    f"Nhật Chủ {reading}" + (" hoặc ngược lại (sát ngưỡng)" if near else "")),
        sources=[src("SRC_TVH_DIEM", "tr.331–355")], pillar_refs=["day.stem", "month.branch"],
        caveats=["Ngưỡng 40% là của sách; biên ±0,03 và quy ước đúng 40% là của hệ thống.", "Tính điểm chưa hỗ trợ phu tòng thê hóa, thê tòng phu hóa, uyên ương hợp hóa."]))
    axes = S["axes"]
    items.append(Item(
        id="nen-tang.khi-the-he-thong", chapter="nen-tang", section="khi-the", basis="truong_phai", school="he_thong", review="draft",
        headline=f"Cách tính riêng của hệ thống: {S['level']}",
        easy=f"Theo cách tính riêng của hệ thống (khác cách của Thiệu Vĩ Hoa), Nhật Chủ ở mức “{S['level']}”: {axes['de_lenh']} về mùa, {axes['de_dia']} về gốc rễ, {axes['de_the']} về người hỗ trợ trên thiên can.",
        expert=f"Hệ thống (he_thong, draft): đắc lệnh = {axes['de_lenh']}; đắc địa (thông căn) = {axes['de_dia']}; đắc thế (thiên can hỗ trợ) = {axes['de_the']}; đắc sinh (Ấn) = {axes['de_sinh']} → {S['level']}. Tỉ trọng nhóm: " +
               ", ".join(f"{gname(k)} {v * 100:.0f}%" for k, v in shares) + ".",
        chain=chain(f"Tỉ trọng nhóm: {', '.join(f'{gname(k)} {v * 100:.0f}%' for k, v in shares)}",
                    "Các tiêu chí đắc lệnh, đắc địa, đắc thế (八字真宗 tr.26); trọng số do hệ thống đặt", "; ".join(f"{k}: {v}" for k, v in axes.items()), f"Mức khí thế của hệ thống: {S['level']}"),
        sources=[src("SRC_BAZI_ZHENZONG", "tr.26 (ba tiêu chí)")], pillar_refs=["day.stem", "month.branch"],
        caveats=["Hai cách đọc vượng/nhược đến từ hai cách tính khác nhau; chúng được đặt cạnh nhau, không trộn."]))
    top, second = shares[0], shares[1]
    items.append(Item(
        id="nen-tang.nhom-nhieu", chapter="nen-tang", section="khi-the", basis="tinh_toan", school="tvh", review="computed",
        headline=f"Nhóm nhiều nhất: {gname(top[0])}",
        easy=f"Trong lá số, nhóm {gname(top[0])} ({SPEC['group_plain'][top[0]]}) nhiều nhất, chiếm {top[1] * 100:.0f}% ; kế đó là {gname(second[0])} ({second[1] * 100:.0f}%).",
        expert=f"Tỉ trọng theo tổng điểm TVH: " + ", ".join(f"{gname(k)} {v * 100:.1f}%" for k, v in shares) + ". Nhóm nhiều nhất là khóa tra bảng dụng thần theo cách (tr.378–386).",
        chain=chain(", ".join(f"{gname(k)} {v * 100:.1f}%" for k, v in shares), "Thiệu Vĩ Hoa tr.378–386 chọn dụng thần theo (cách, vượng/nhược, nhóm nhiều nhất)", f"nhóm lớn nhất: {gname(top[0])}", f"Khóa tra bảng: {gname(top[0])}"),
        sources=[src("SRC_TVH_DUNGTHAN", "tr.378–386")]))
    return items


def f_han_noan(A: dict, view: ChartView) -> list[Item]:
    items = []
    cl = A["season"]["climate"]
    dh = A["yongshen"]["methods"]["dieu_hau"]
    tb = dh["table"]
    stems = tb["yong_stems"]
    chu = stems[0]["stem"] if stems else None
    if stems:
        first = stems[0]
        state = "thấu can" if first["visible"] else "chỉ tàng trong chi" if first["hidden"] else "không có trong lá số"
        direction = "thuan" if first["visible"] else "trung_tinh" if first["hidden"] else "bat_loi"
        names = ", ".join(f"{x['stem']} ({gname(x['group'])})" for x in stems)
        conflict = tb.get("book_internal_conflict")
        cav = ["Chính tác giả ghi (tr.388) rằng bảng điều hậu do một độc giả tặng và ông không biết nguồn; ở đây chỉ bảo đảm bản chép khớp trang in, chưa phải học thuyết đã kiểm chứng."]
        if conflict:
            cav.append("Ô này nằm trong số chín ô mà bảng và chú thích của sách tự mâu thuẫn: " + f"chú thích có thêm {', '.join(conflict['note_only']) or '—'}, bảng có thêm {', '.join(conflict['table_only']) or '—'}; hệ thống giữ bảng và không chọn bên nào.")
        items.append(Item(
            id="nen-tang.dieu-hau", chapter="nen-tang", section="han-noan", basis="co_nguon", school="tvh", review="verified", direction=direction,
            headline=f"Điều hậu: ưu tiên {chu}, {state}",
            easy=f"Với {STEMS_VI[view.dm]} sinh tháng {BRANCHES_VI[view.month_branch]}, sách Thiệu Vĩ Hoa xếp thứ tự can cần dùng để cân bằng khí hậu: {names}. Can đứng đầu là {chu}; trong lá số {chu} {state}.",
            expert=f"Bảng điều hậu TVH (tr.389–390; thứ tự theo chú thích tr.391–396): {names}. Can chủ {chu}: {state}. Vai trò Dụng/Hỷ gán cho can chủ/các can còn lại là quy ước của hệ thống.",
            chain=chain(f"{STEMS_VI[view.dm]} sinh tháng {BRANCHES_VI[view.month_branch]}; các can có mặt: " + "; ".join(f"{x['stem']} {'thấu' if x['visible'] else 'tàng' if x['hidden'] else 'vắng'}" for x in stems),
                        "Thiệu Vĩ Hoa tr.389–396: ô (can ngày × tháng) liệt kê can điều hậu theo thứ tự ưu tiên", f"can chủ {chu}: {state}", f"Dụng thần điều hậu hướng về nhóm {gname(first['group'])}"),
            sources=[src("SRC_TVH_DIEUHAU")], pillar_refs=["day.stem", "month.branch"], caveats=cav))
    items.append(Item(
        id="nen-tang.han-nong", chapter="nen-tang", section="han-noan", basis="truong_phai", school="he_thong", review="draft",
        headline=f"Khí hậu thô: {cl['label']}",
        easy=f"Về hàn–nóng, chỉ số thô của hệ thống đọc lá số này là “{cl['label']}”. Đây là thước đo đơn giản của hệ thống, chưa tính độ ẩm khô.",
        expert=f"Chỉ số nhiệt thô {cl['heat']} (nền {cl['base']}, điều chỉnh {cl['adjust']}); nhãn {cl['label']}. Trích Thiên Tủy tr.113–114: hàn quá mà noãn hữu khí thì cần noãn; hàn quá mà noãn vô khí thì lấy hàn làm dụng. " + dh.get("han_noan", {}).get("note", ""),
        chain=chain(f"Chỉ số nhiệt {cl['heat']}", "Trích Thiên Tủy tr.113–114 (nguyên tắc hàn–noãn)", dh.get("han_noan", {}).get("note", "—"), f"Nhãn khí hậu: {cl['label']}"),
        sources=[src("SRC_TTT_HANTHU", "tr.113–114")], caveats=["Ngưỡng hàn/nóng là của hệ thống."]))
    return items


def f_cach_cuc(A: dict, view: ChartView) -> list[Item]:
    G = A["geju"]
    items: list[Item] = []
    if G["inner"]:
        c = G["inner"][0]
        st = STATE_VI.get(c["state"], c["state"])
        conds = [plain_tokens(x["evidence"]) for x in c["thanh"]]
        bads = [plain_tokens(x["evidence"]) for x in c["bai"]]
        direction = "thuan" if c["state"] == "thanh" else "bat_loi" if c["state"].startswith("bai") else "trung_tinh"
        items.append(Item(
            id="nen-tang.cach-chinh", chapter="nen-tang", section="cach-cuc", basis="truong_phai", school="he_thong", review="draft", direction=direction,
            headline=f"Cách {c['name']}: {st}",
            easy=f"Cách cục (khung chính của lá số) được lấy từ nguyệt lệnh là {c['name']}; xét điều kiện thành và bại, hệ thống đọc là “{st}”.",
            expert=f"Cách {c['name']} ({plain_tokens(c['basis'])}); trạng thái {st}. Điều kiện thành đạt: " + ("; ".join(conds) or "không") + ". Điều kiện bại: " + ("; ".join(bads) or "không") + f". Dụng thần theo bảng nháp của cách: {glist(c['yong_groups'])}.",
            chain=chain(plain_tokens(c["basis"]), "Tử Bình: lấy cách từ tàng can nguyệt lệnh có thấu hay không; thành/bại theo thập thần phối hợp (bảng nháp của hệ thống)",
                        "Thành: " + ("; ".join(conds) or "không có điều kiện thỏa") + " | Bại: " + ("; ".join(bads) or "không có điều kiện thỏa"), f"Cách {c['name']} {st}"),
            sources=[], pillar_refs=["month.branch"], caveats=["Bảng thành/bại này là bản nháp của hệ thống (chưa đối chiếu Tử Bình Chân Thuyên); xem lời của Thiệu Vĩ Hoa ở mục kế bên."]))
        tot = [x for x in c["tvh_danh_gia"] if x["verdict"] == "tot"]
        xau = [x for x in c["tvh_danh_gia"] if x["verdict"] == "xau"]
        for x in c["tvh_danh_gia"]:
            good = x["verdict"] == "tot"
            items.append(Item(
                id=f"nen-tang.tvh-{x['id']}", chapter="nen-tang", section="cach-cuc", basis="co_nguon", school="tvh", review="verified", direction="thuan" if good else "bat_loi",
                headline=("Tốt: " if good else "Xấu: ") + x["text"],
                easy=f"Thiệu Vĩ Hoa nhận xét về cách {c['name']}: “{x['text']}” ({'tốt' if good else 'xấu'}). Điều kiện này khớp lá số: " + "; ".join(plain_tokens(e) for e in x["evidence"]) + ".",
                expert=f"TVH tr.{x['page']}, luật {x['id']}: {x['text']} → {'tốt' if good else 'xấu'}. Bằng chứng: " + "; ".join(plain_tokens(e) for e in x["evidence"]) + ".",
                chain=chain("; ".join(plain_tokens(e) for e in x["evidence"]), f"Thiệu Vĩ Hoa tr.{x['page']}: {x['text']}", "đã thỏa các điều kiện trên (ngưỡng 'nhiều/nhẹ/mạnh' là của hệ thống)", f"Sách xếp vào loại {'tốt' if good else 'xấu'}"),
                sources=[src("SRC_TVH_CACH", f"tr.{x['page']}")], pillar_refs=["month.branch"],
                caveats=["Sách nói 'mệnh tốt/xấu' chung; không gán riêng cho một lĩnh vực."]))
        if tot and xau:
            for a in items:
                if a.id.startswith("nen-tang.tvh-"):
                    a.counter = [b.id for b in items if b.id.startswith("nen-tang.tvh-") and b.direction != a.direction]
    for o in G["outer"]:
        tvh = o.get("kind") in ("tong_tvh", "chuyen_vuong", "hoa_tvh")
        chan = o["quality"] == "chân"
        items.append(Item(
            id=f"nen-tang.ngoai-cach.{o['name']}", chapter="nen-tang", section="cach-cuc", basis="co_nguon" if tvh and chan else "truong_phai", school="tvh" if tvh else "he_thong",
            review="verified" if tvh else "draft", direction="cau_truc",
            headline=f"Ngoại cách {o['name']}: {'chân' if chan else 'giả'}",
            easy=(f"Lá số có dấu hiệu của ngoại cách {o['name']}. " + ("Điều kiện đủ (chân): theo trường phái này, lá số nên đọc theo thế của cách đặc biệt thay vì cách thông thường." if chan else "Điều kiện chưa đủ (giả): chỉ nêu như một khả năng; cách thông thường vẫn là cách đọc chính.")),
            expert=f"{o['name']} ({'Thiệu Vĩ Hoa' if tvh else 'hệ thống / Trích Thiên Tủy'}): {o['quality']}. Bằng chứng: {plain_tokens(json.dumps(o.get('evidence', {}), ensure_ascii=False))}.",
            chain=chain(plain_tokens(json.dumps(o.get("evidence", {}), ensure_ascii=False)), "Điều kiện nhận ngoại cách (ngưỡng nhận diện do hệ thống đặt từ lời sách)", f"chất lượng: {o['quality']}", f"{'Thay cách thông thường' if chan else 'Chưa đủ để thay cách thông thường'}"),
            sources=[src("SRC_TVH_CACH")] if tvh else [src("SRC_TTT_TONG")], caveats=["Ngưỡng nhận diện là của hệ thống; hai trường phái nhận diện ngoại cách độc lập, không bắt buộc đồng ý."]))
    if not items:
        items.append(Item(id="nen-tang.cach-khong-xac-dinh", chapter="nen-tang", section="cach-cuc", basis="chua_du_can_cu", headline="Chưa xác định được cách",
                          easy="Từ nguyệt lệnh của lá số này, hệ thống chưa xác định được cách một cách chắc chắn.", expert="Không có tàng can nguyệt lệnh hợp lệ để lập cách.", chain=chain("—", "—", "—", "Không kết luận")))
    return items


def f_tuong_tac(A: dict, view: ChartView) -> list[Item]:
    spec = SPEC["interaction"]
    items: list[Item] = []
    mat = [r for r in A["interactions"] if r.get("status") in spec["material"]]

    def rank(r):
        return (0 if any(m.startswith("month.") for m in r["members"]) else 1, r["kind"], r["id"])
    for r in sorted(mat, key=rank)[:10]:
        kind = spec["kind_vi"].get(r["kind"], r["kind"])
        what = spec["status_vi"].get(r["status"], r["status"])
        if r["kind"].startswith("stem"):
            chars = " và ".join(f"{pc(view, m.split('.')[0], 'stem')}" for m in r["members"])
        else:
            chars = " và ".join(f"{pc(view, m.split('.')[0], 'branch')}" for m in r["members"])
        pot = r.get("potential_element") or r.get("element")
        hits_month = any(m.startswith("month.") for m in r["members"])
        bad = r["kind"] in ("branch_clash", "branch_penalty", "branch_harm", "branch_destroy", "branch_self_penalty", "stem_clash") and r["status"] in ("xung_vao_cuc", "xung_nho", "xung_can_bang", "co_hieu_luc", "giang_co")
        good = r["status"] in ("formed", "chan_hoa")
        items.append(Item(
            id=f"nen-tang.tt.{r['id']}", chapter="nen-tang", section="tuong-tac", basis="tinh_toan", school="he_thong", review="computed",
            direction="bat_loi" if bad else "thuan" if good else "trung_tinh",
            headline=f"{kind.capitalize()} {chars}: {what.split(',')[0]}",
            easy=f"{chars} có quan hệ {kind}" + (f" (tiềm năng hóa {pot})" if pot else "") + f": {what}." + (" Quan hệ này chạm vào nguyệt lệnh nên ảnh hưởng đến cách và khí thế." if hits_month else ""),
            expert=f"{kind} {chars}; khoảng cách trụ {r.get('span', '?')} ({'kề' if r.get('adjacent') else 'cách vị'}); trạng thái {r['status']}: {what}." + (f" Hành tiềm năng {pot}." if pot else ""),
            chain=chain(f"{chars}; {'kề nhau' if r.get('adjacent') else 'cách vị'}", f"Bảng {kind} (八字真宗 tr.19–20); hệ số tác động và điều kiện hóa do hệ thống đặt", f"trạng thái: {r['status']}", what),
            sources=[src("SRC_BAZI_ZHENZONG", "tr.19–20 (bảng)")], pillar_refs=r["members"],
            caveats=["Có hay không có quan hệ là tra bảng; mức giảm/tăng và điều kiện thành hóa là quy ước của hệ thống (draft)."]))
    raw, after = A["strength_raw"]["level"], A["strength_after"]["level"]
    if A["facts"].get("bazi.level_changed_by_interaction"):
        items.append(Item(id="nen-tang.tt.doi-muc", chapter="nen-tang", section="tuong-tac", basis="truong_phai", school="he_thong", review="draft", direction="cau_truc",
                          headline=f"Tương tác làm đổi khí thế: {raw} → {after}",
                          easy=f"Nếu bỏ qua các quan hệ hợp xung ở trên, Nhật Chủ ở mức “{raw}”; sau khi tính chúng, mức này thành “{after}”.",
                          expert=f"Khí thế (hệ thống) trước tương tác: {raw}; sau tương tác: {after}.", chain=chain(f"{raw} → {after}", "Thứ tự giải: cục → hợp can → xung → hình/hại/phá", "xem các quan hệ liệt kê", f"Mức khí thế đổi từ {raw} sang {after}"), caveats=["Hệ số do hệ thống đặt."]))
    return items


def f_thap_than(A: dict, view: ChartView) -> list[Item]:
    items = []
    for p in A["patterns"]:
        pol = p.get("polarity", "")
        items.append(Item(
            id=f"nen-tang.tt-pattern.{p['id']}", chapter="nen-tang", section="thap-than", basis="truong_phai", school="he_thong", review=p.get("review_status", "draft"),
            direction=POLARITY_DIR.get(pol, "trung_tinh"),
            headline=f"{p['name']}: {p['state'].replace('_', ' ')}",
            easy=f"Cấu trúc Thập Thần “{p['name']}” có mặt trong lá số (trạng thái: {p['state'].replace('_', ' ')}). Đây là cách gọi tên mối quan hệ giữa các thập thần, hệ thống chưa gắn nó với một lời sách cụ thể.",
            expert=f"Pattern {p['id']} ({p['name']}), cực {pol or '—'}, trạng thái {p['state']}, bằng chứng: " + "; ".join(plain_tokens(e) for e in p.get("evidence", [])) + ".",
            chain=chain("; ".join(plain_tokens(e) for e in p.get("evidence", [])) or "—", "Định nghĩa pattern thập thần của hệ thống (patterns_defs, draft)", f"trạng thái {p['state']}", f"Có cấu trúc {p['name']}"),
            caveats=["Định nghĩa là bản nháp của hệ thống, chưa có trang sách đối chiếu."]))
    return items


# ---------------------------------------------------------------- 八字真宗 direct rules through the existing rule engine
def zz_items(bz, view: ChartView, A: dict) -> tuple[list[Item], list[dict]]:
    from ..knowledge.loader import load_all, load_claims
    from ..reasoning import engine, facts
    rules, sources = load_all()
    claims = load_claims()
    zr = [r for r in rules if r.id.startswith("BT_ZZ")]
    res = engine.run(rules, sources, facts.bazi_facts(bz, zz=True), system="bat_tu")
    rmap = {r.id: r for r in rules}
    route = SPEC["zz_routing"]
    direction = SPEC["zz_direction"]
    out: list[Item] = []
    unrouted: list[str] = []
    fv = SPEC["fact_vi"]
    for f in res.findings:
        r = rmap[f.rule_id]
        if not r.id.startswith("BT_ZZ"):
            continue
        dest = route["by_rule"].get(r.id) or next((v for k, v in route["by_prefix"].items() if r.id.startswith(k)), None) or route["by_category"].get(r.category)
        if dest is None:
            unrouted.append(r.id)
            continue
        label = claims.get(f.claim, {}).get("label", f.claim)
        page = re.search(r"\[(?:PDF )?pp?\.?\s*([\d,\- ]+)", r.description)
        pg = f"tr.{page.group(1).strip()}" if page else None
        why = res.why(f.id)
        facts_vi = []
        for n, k in why["kinds"].items():
            if k != "fact":
                continue
            m = re.match(r"^(?P<k>[\w.]+)=(?P<v>.*) @(?P<s>.+)$", res.nodes[n].label)
            if not m:
                continue
            v = m["v"].strip("'\"")
            v = SPEC["group_value_vi"].get(v, v)
            facts_vi.append(fv.get(m["k"], m["k"] + "={v}").format(v=v))
        verified = r.reviewStatus == "verified"
        d = "thuan" if r.id in direction["thuan"] else "bat_loi" if r.id in direction["bat_loi"] else "trung_tinh"
        pil = []
        if "hour" in r.description or "giờ" in label:
            pil.append("hour.stem")
        if "nguyệt" in label or "tháng" in label:
            pil.append("month.branch")
        if "nhật chi" in label or "chi ngày" in " ".join(facts_vi):
            pil.append("day.branch")
        out.append(Item(
            id=f"{dest[0]}.{r.id}", chapter=dest[0], section=dest[1], basis="co_nguon" if verified else "truong_phai", school="zz", review="verified" if verified else "draft", direction=d,
            kind="sach", headline=((facts_vi[0] + ": " + label) if r.category == "day_master_character" and facts_vi else (label[0].upper() + label[1:] if label else r.id)),
            easy=f"Vì lá số của bạn có " + "; ".join(facts_vi) + f", sách 八字真宗{(' (' + pg + ')') if pg else ''} ghi nhận: {label}.",
            expert=f"{label} [八字真宗 {pg or 'chưa rõ trang'}; luật {r.id}; {'đã đối chiếu trang' if verified else 'bản nháp, chưa đối chiếu trang'}]. Điều kiện đã thỏa: " + "; ".join(facts_vi) + ".",
            chain=chain("; ".join(facts_vi), f"八字真宗 {pg or ''}: {label}", "mọi điều kiện của luật đã thỏa; ngoại lệ trong luật: " + ("không có" if not r.exceptions else str(len(r.exceptions))), f"Sách nêu: {label}"),
            sources=[src("SRC_BAZI_ZHENZONG", pg)], pillar_refs=pil,
            caveats=["Đây là lời của một sách phổ thông về Bát Tự, chưa được kiểm chứng thực nghiệm." + ("" if verified else " Luật này còn là bản nháp (chưa đối chiếu từng trang).")]))
    return out, unrouted


# ---------------------------------------------------------------- chapter-specific structural items
def method_role_item(A: dict, chapter: str, section: str, group: str, view: ChartView) -> Item | None:
    Y = A["yongshen"]
    titles = {"phu_uc": "Phù ức", "dieu_hau": "Điều hậu", "cach_cuc": "Cách cục (hệ thống)", "cach_cuc_tvh": "Cách cục (Thiệu Vĩ Hoa)", "thong_quan": "Thông quan", "thuan_the": "Thuận thế (hệ thống)", "thuan_the_tvh": "Thuận thế (Thiệu Vĩ Hoa)", "khuyet_hanh": "Hành thiếu"}
    rows = []                                   # (method title, reading label or "", role key)
    for name, m in Y["methods"].items():
        if m["status"] == "hai_cach_doc":
            for alt in m["alternatives"]:
                role = next((r for r in ROLE_VI if group in alt.get(r, [])), None)
                if role:
                    rows.append((titles[name], f"cách đọc {alt.get('dm_vi') or alt.get('level')}", role))
            continue
        role = next((r for r in ROLE_VI if group in m.get(r, [])), None)
        if role and m["meta"]["applied"]:
            rows.append((titles[name], "", role))
    if not rows:
        return None
    parts = [f"{t}{' (' + lab + ')' if lab else ''}: {ROLE_VI[r]}" for t, lab, r in rows]
    roles = {r for _, _, r in rows}
    good, bad = roles & {"yong", "xi"}, roles & {"ji", "chou"}
    return Item(
        id=f"{chapter}.vai-tro.{group}", chapter=chapter, section=section, basis="co_nguon", school="he_thong", review="draft", kind="cau_truc",
        headline=f"{gname(group)} trong các phương pháp dụng thần: " + ("; ".join(parts[:3]) + (" …" if len(parts) > 3 else "")),
        easy=f"Nhóm {gname(group)} ({SPEC['group_plain'][group]}) được các phương pháp dụng thần xếp như sau: " + "; ".join(parts) + "." +
             (" Các phương pháp đi ngược chiều nhau về nhóm này, nên không thể nói chắc nó có lợi hay không." if good and bad else "") + " Đây là vai trò cấu trúc của nhóm này trong lá số; sách không nói rằng vai trò này đồng nghĩa với giàu hay thành đạt.",
        expert="Vai trò của nhóm " + gname(group) + " theo từng phương pháp (mỗi phương pháp độc lập, không cộng điểm): " + "; ".join(parts) + ".",
        chain=chain(f"Nhóm {gname(group)} có mặt trong bảng vai trò của {len(rows)} phương pháp/cách đọc", "Mỗi phương pháp dụng thần có bảng vai trò riêng (xem chương Dụng thần)", ("có mâu thuẫn giữa các phương pháp" if good and bad else "cùng chiều" if len(roles) == 1 else "nhiều vai trò khác nhau"), "; ".join(parts)),
        sources=[src("SRC_TVH_DUNGTHAN"), src("SRC_TVH_DIEUHAU")], caveats=["Vai trò là kết luận cấu trúc của từng phương pháp; chưa kiểm chứng thực nghiệm; không suy ra mức độ giàu nghèo hay thành bại."])


def day_branch_item(A: dict, view: ChartView) -> Item:
    h = view.hidden("day")
    parts = ", ".join(f"{STEMS_VI[x['stem']]} ({x['ten_god']})" for x in h)
    return Item(
        id="hon-nhan.nhat-chi-tang-can", chapter="hon-nhan", section="nhat-chi", basis="tinh_toan", school="he_thong", review="computed", kind="tinh_toan",
        headline=f"Nhật chi {BRANCHES_VI[view.branch('day')]} tàng {parts}",
        easy=f"Nhật chi (cung ngay dưới Nhật Chủ, được gọi là cung bạn đời) là {BRANCHES_VI[view.branch('day')]}, bên trong chứa: {parts}. Đây là thành phần của cung này; sách đã nhập không dựa vào nó để kết luận về người bạn đời.",
        expert=f"Nhật chi {BRANCHES_VI[view.branch('day')]} tàng can: {parts} (bản khí, trung khí, dư khí theo thứ tự).",
        chain=chain(f"Nhật chi {BRANCHES_VI[view.branch('day')]}", "Bảng tàng can của địa chi (tra bảng)", f"thập thần của từng tàng can so với Nhật Chủ", parts),
        sources=[src("SRC_BAZI_ZHENZONG", "tr.19–20 (bảng)")], pillar_refs=["day.branch"], caveats=["Gọi nhật chi là 'cung bạn đời' là cách nói thông dụng của hệ thống, không phải điều một trang sách đã nhập khẳng định."])


def shares_item(A: dict, chapter: str, section: str, group: str) -> Item:
    sh = A["strength_after"]["tvh"]["totals"]
    S = A["strength_after"]["shares"]
    v = S[group]
    return Item(
        id=f"{chapter}.ti-trong.{group}", chapter=chapter, section=section, basis="tinh_toan", school="tvh", review="computed", kind="tinh_toan",
        headline=f"{gname(group)} chiếm {v * 100:.0f}% tổng sức",
        easy=f"Nhóm {gname(group)} ({SPEC['group_plain'][group]}) chiếm khoảng {v * 100:.0f}% tổng sức các hành trong lá số" + (" — rất ít." if v < 0.08 else " — khá nhiều." if v > 0.3 else "."),
        expert=f"Tỉ trọng nhóm {gname(group)} = {v * 100:.1f}% (hệ thống he_thong; tổng điểm TVH các hành: " + ", ".join(f"{k} {x:.1f}" for k, x in sh.items()) + ").",
        chain=chain(f"Tổng điểm các hành: " + ", ".join(f"{k} {x:.1f}" for k, x in sh.items()), "Tỉ trọng nhóm = tổng điểm các hành thuộc nhóm / tổng điểm", f"{gname(group)} = {v * 100:.1f}%", f"{gname(group)} chiếm {v * 100:.0f}%"),
        caveats=["Đây là con số tính toán của hệ thống, không phải một nhận định của sách."])


# ---------------------------------------------------------------- đại vận
def van_items(A: dict, view: ChartView, bz, timeline: dict | None) -> list[Item]:
    items: list[Item] = []
    lp = bz.luck_pillars
    ls = bz.luck_start
    rows = []
    for l in lp[:9]:
        rows.append({"index": l.index, "pillar": f"{STEMS_VI[l.stem]} {BRANCHES_VI[l.branch]}", "start": getattr(l, "start_date", None) and str(l.start_date), "start_year": round(l.start_year_exact, 1),
                     "god": view.god(l.stem), "group": group_of_stem(view, l.stem)})
    items.append(Item(
        id="dai-van.lich", chapter="dai-van", section="lich", basis="tinh_toan", school="he_thong", review="computed", kind="tinh_toan",
        headline=f"Đại vận đầu {rows[0]['pillar']} bắt đầu {rows[0]['start'] or rows[0]['start_year']}",
        easy=f"Đại vận của bạn khởi lúc {ls['years']} tuổi {ls['months']} tháng (ngày {ls['start_date']}), đi theo chiều {'thuận' if bz.luck_direction in (1, 'forward', 'thuận') else 'nghịch'} qua các tháng; đại vận đầu là {rows[0]['pillar']} (can là {rows[0]['god']}). Mỗi đại vận kéo dài 10 năm; bảng liệt kê chín đại vận đầu.",
        expert=f"Khởi vận {ls['age_years']} tuổi (ba ngày bằng một năm, tính tới ngày: {ls['start_date']}); chiều {bz.luck_direction}; đại vận 1 = {rows[0]['pillar']} ({rows[0]['god']}); các đại vận kế tiếp theo thứ tự lục thập hoa giáp.",
        chain=chain(f"Tứ trụ {four_pillars(view)}; giới tính {'nam' if view.gender == 'male' else 'nữ' if view.gender == 'female' else 'chưa rõ'}; khoảng cách đến tiết: {ls['years']} năm {ls['months']} tháng {ls['days']} ngày", "Quy tắc khởi vận: thuận/nghịch theo âm dương của năm sinh và giới tính; ba ngày bằng một năm", f"đại vận đầu {rows[0]['pillar']}", f"Khởi vận {ls['start_date']}; danh sách đại vận (bảng)"),
        sources=[src("SRC_BAZI_ZHENZONG", "tr.19–20 (bảng)")], table=rows))
    Y = A["yongshen"]["methods"]["cach_cuc_tvh"]
    classify = []

    def cls(alt):
        tot, xau = alt.get("van_tot") or [], alt.get("van_xau") or []
        out = []
        for r in rows:
            out.append({"index": r["index"], "pillar": r["pillar"], "group": r["group"], "verdict": "tot" if r["group"] in tot else "xau" if r["group"] in xau else "khong_neu"})
        return out
    if Y["status"] == "ap_dung":
        classify = [("", Y)]
    elif Y["status"] == "hai_cach_doc":
        classify = [(a.get("dm_vi", ""), a) for a in Y["alternatives"] if "van_tot" in a]
    if classify:
        for label, alt in classify:
            tab = cls(alt)
            n_t = sum(1 for t in tab if t["verdict"] == "tot")
            n_x = sum(1 for t in tab if t["verdict"] == "xau")
            lab = f" (cách đọc {label})" if label else ""
            items.append(Item(
                id=f"dai-van.hy-ky{('.' + label) if label else ''}", chapter="dai-van", section="van-hy-ky", basis="co_nguon", school="tvh", review="verified", kind="sach",
                headline=f"Vận hỷ{lab}: {glist(alt['van_tot'])}; vận kỵ: {glist(alt['van_xau'])}",
                easy=f"Theo bảng của Thiệu Vĩ Hoa cho cách {A['geju']['inner'][0]['name']}{lab}, đại vận có can thuộc nhóm {glist(alt['van_tot'])} là thuận, thuộc nhóm {glist(alt['van_xau'])} là bất lợi. Trong 9 đại vận đầu có {n_t} vận thuận và {n_x} vận bất lợi theo bảng này." +
                     (" Hai cách đọc vượng/nhược cho hai bảng khác nhau, nên hai kết quả được nêu riêng." if label else ""),
                expert=f"TVH tr.{alt.get('page', '382–386')}: cách {A['geju']['inner'][0]['name']}, Nhật Chủ {label or Y.get('dm', '')}, nhóm nhiều nhất {gname(alt.get('dominant', ''))}: vận tốt {glist(alt['van_tot'])}; vận xấu {glist(alt['van_xau'])}. Chỉ xét can đại vận; tác động của địa chi nằm ở mục sau.",
                chain=chain(f"Cách {A['geju']['inner'][0]['name']}, nhóm nhiều nhất {gname(alt.get('dominant', ''))}, Nhật Chủ {label or Y.get('dm', '')}", f"Thiệu Vĩ Hoa tr.{alt.get('page', '382–386')}: hỉ/kị thần của vận theo cách", "đã tra đúng dòng bảng; ngưỡng 40% sát nên có hai cách đọc" if label else "đã tra đúng dòng bảng", f"Vận tốt {glist(alt['van_tot'])}; vận xấu {glist(alt['van_xau'])}"),
                sources=[src("SRC_TVH_DUNGTHAN", f"tr.{alt.get('page', '382–386')}")], table=tab,
                caveats=["Bảng của sách nói về nhóm thập thần của vận, không nói về sự kiện; chưa kiểm chứng thực nghiệm."] + (["Dòng bảng này có dụng thần do hệ thống suy ra: " + Y['yong_inferred']] if Y.get("yong_inferred") else [])))
    else:
        items.append(Item(
            id="dai-van.hy-ky.khong-xac-dinh", chapter="dai-van", section="van-hy-ky", basis="chua_du_can_cu", kind="gioi_han", headline="Chưa tra được vận hỷ/kỵ theo bảng của sách",
            easy="Bảng vận hỷ–kỵ của Thiệu Vĩ Hoa gắn với cách cục. Với lá số này cách chưa được xác định theo trường phái đó (ví dụ vì đang đọc ngoại cách), nên không có bảng để tra và hệ thống không tự bịa.",
            expert=f"cach_cuc_tvh.status = {Y['status']}; bảng vận (tr.382–386) chỉ có theo cách; không có dòng.", chain=chain(f"Trạng thái cách theo TVH: {Y['status']}", "Thiệu Vĩ Hoa tr.382–386: vận hỷ/kỵ theo cách", "không có dòng bảng", "Không kết luận về vận hỷ/kỵ"), sources=[src("SRC_TVH_DUNGTHAN", "tr.382–386")]))
        tt = A["yongshen"]["methods"]["thuan_the_tvh"]
        if tt["status"] == "ap_dung" and tt.get("van_tot_elements"):
            items.append(Item(id="dai-van.hy-ky.dac-biet", chapter="dai-van", section="van-hy-ky", basis="co_nguon", school="tvh", review="verified", kind="sach",
                              headline=f"Cách đặc biệt {tt['outer']}: vận tốt {', '.join(tt['van_tot_elements'])}", easy=f"Với cách đặc biệt {tt['outer']}, sách nêu vận hành {', '.join(tt['van_tot_elements'])} là tốt và {', '.join(tt.get('van_xau_elements') or [])} là xấu.",
                              expert=f"TVH tr.385–386: {tt['outer']}: vận tốt {tt['van_tot_elements']}, vận xấu {tt.get('van_xau_elements')}.", chain=chain(tt["outer"], "Thiệu Vĩ Hoa tr.385–386", "cách đặc biệt chân", "Vận tốt/xấu theo hành"), sources=[src("SRC_TVH_DUNGTHAN", "tr.385–386")]))
    if timeline:
        by = {e["index"]: e for e in timeline["luck"]}
        for r in rows:
            e = by.get(r["index"])
            if not e:
                continue
            ev = [x for x in e.get("events", []) if x.get("status") in ("formed", "chan_hoa", "co_hieu_luc", "xung_vao_cuc", "xung_nho", "tranh_hop")]
            ev_vi = "; ".join(f"{SPEC['interaction']['kind_vi'].get(x['kind'], x['kind'])} với {x['with'].replace('.stem', '').replace('.branch', '')}: {SPEC['interaction']['status_vi'].get(x['status'], x['status'])}" for x in ev[:4]) or "không có quan hệ đáng kể"
            changed = e["level"] != e["level_natal"]
            items.append(Item(
                id=f"dai-van.tac-dong.{r['index']}", chapter="dai-van", section="tac-dong", basis="truong_phai", school="he_thong", review="draft",
                direction="bat_loi" if e["effect"] == "pha_cach" else "thuan" if e["effect"] == "tro_cach" else "cau_truc" if e["effect"] == "doi_cach" else "trung_tinh",
                headline=f"Đại vận {r['pillar']}: {EFFECT_VI.get(e['effect'], e['effect'])}" + (f"; khí thế {e['level_natal']} → {e['level']}" if changed else ""),
                easy=f"Khi đại vận {r['pillar']} (can là {r['god']}) gắn vào nguyên cục: {ev_vi}. Khí thế của Nhật Chủ {'đổi từ ' + e['level_natal'] + ' sang ' + e['level'] if changed else 'giữ nguyên ' + e['level']}; hệ thống đọc tác động lên cách là “{EFFECT_VI.get(e['effect'], e['effect'])}”.",
                expert=f"Cục mở rộng (nguyên cục + đại vận {r['pillar']}): khí thế {e['level_natal']} → {e['level']}; cách nguyên cục {e['cach']['natal']}, cách mở rộng {e['cach']['extended']}; hiệu ứng {e['effect']}; sự kiện: {ev_vi}.",
                chain=chain(f"Nguyên cục + đại vận {r['pillar']} ({r['god']})", "Chạy lại khí thế và cách cục trên cục mở rộng (temporal_deep, draft); quan hệ can chi theo tuế vận (Trích Thiên Tủy)", ev_vi, f"Tác động: {EFFECT_VI.get(e['effect'], e['effect'])}"),
                sources=[src("SRC_TTT_TUEVAN")], caveats=["Mô tả tác động lên cấu trúc, không dự đoán sự kiện; hệ số do hệ thống đặt (draft)."], pillar_refs=[]))
    return items


# ---------------------------------------------------------------- dụng thần chapter
def roles_text(m: dict) -> str:
    parts = [f"{ROLE_VI[r]} {glist(m[r])}" for r in ("yong", "xi", "ji", "chou", "xian") if m.get(r)]
    if m.get("need_elements"):
        parts.append("hành cần " + ", ".join(m["need_elements"]))
    return "; ".join(parts) if parts else "không nêu nhóm Dụng, Hỷ hay Kỵ"


def dung_than_items(A: dict, view: ChartView) -> list[Item]:
    Y = A["yongshen"]
    titles = {"phu_uc": "Phù ức", "dieu_hau": "Điều hậu", "cach_cuc": "Cách cục (hệ thống / Trích Thiên Tủy)", "cach_cuc_tvh": "Cách cục (Thiệu Vĩ Hoa)", "thong_quan": "Thông quan", "thuan_the": "Thuận thế: tòng/hóa (hệ thống)", "thuan_the_tvh": "Thuận thế: cách đặc biệt (Thiệu Vĩ Hoa)", "khuyet_hanh": "Hành thiếu"}
    items: list[Item] = []
    for name, m in Y["methods"].items():
        lv = m["meta"]["levels"]
        napplied = not m["meta"]["applied"] and m["status"] != "hai_cach_doc"
        if napplied:
            basis = "tinh_toan"                   # 'does not apply to this chart' is a computed fact about applicability, not a gap in the sources
        elif lv["transcription_verified"] == "yes" and lv["source_rule_verified"] in ("partial", "yes"):
            basis = "co_nguon"
        else:
            basis = "truong_phai"
        title = titles[name]
        if m["status"] == "hai_cach_doc":
            parts = [f"cách đọc {a.get('dm_vi') or a.get('level')}: {roles_text(a)}" for a in m["alternatives"]]
            concl = "; ".join(parts)
            easy = f"{title}: lá số nằm sát ranh giới giữa hai mức nên có hai cách đọc — " + concl + ". Hệ thống không chọn một trong hai."
        elif m["meta"]["applied"]:
            concl = roles_text(m)
            easy = f"{title}: {concl}."
            if m.get("yong_inferred"):
                easy += " (Dụng thần của dòng bảng này do hệ thống suy ra, sách không nêu rõ.)"
        else:
            concl = "không áp dụng"
            easy = f"{title}: không áp dụng cho lá số này ({m['meta']['applies_when']})."
        direction = "cau_truc"
        items.append(Item(
            id=f"dung-than.{name}", chapter="dung-than", section="theo-phuong-phap", basis=basis, kind="tinh_toan" if napplied else "phuong_phap", school="tvh" if name.endswith("tvh") or name in ("dieu_hau",) else "he_thong", review="verified" if basis == "co_nguon" else "draft", direction=direction,
            headline=f"{title}: {concl}",
            easy=easy,
            expert=f"{title} — {concl}. Cơ sở khí thế: {plain_tokens(m['meta']['strength_basis'])}. Các bước: " + " → ".join(plain_tokens(t) for t in m["trace"]) + ".",
            chain=chain("; ".join(plain_tokens(t) for t in m["trace"][:3]), "; ".join(m["meta"]["source"]), m["meta"]["applies_when"], concl),
            sources=[src(re.search(r"SRC_[A-Z_]+", s).group(0), s.split(" ", 1)[1] if " " in s and s.startswith("SRC_") else None) if re.search(r"SRC_[A-Z_]+", s) else {"id": "he_thong", "title": s} for s in m["meta"]["source"]],
            caveats=[lv["why"], "Chưa có kiểm chứng thực nghiệm (empirical_validated = no)."] + (["Chín ô điều hậu mà sách tự mâu thuẫn: ô này thuộc số đó."] if name == "dieu_hau" and m["table"].get("book_internal_conflict") else [])))
    C = Y["comparison"]
    if C["disagreements"]:
        for d in C["disagreements"]:
            items.append(Item(
                id=f"dung-than.bat-dong.{d['group']}", chapter="dung-than", section="bat-dong", basis="tinh_toan", school="he_thong", review="computed", direction="cau_truc",
                headline=f"{d['label']}: thuận ở {len(d['favourable_in'])} phương pháp, bất lợi ở {len(d['unfavourable_in'])}",
                easy=f"Nhóm {d['label']} được một số phương pháp xếp là thuận ({', '.join(titles[x] for x in d['favourable_in'])}) nhưng phương pháp khác xếp là bất lợi ({', '.join(titles[x] for x in d['unfavourable_in'])}). Hai bên không thể cộng trừ cho nhau.",
                expert=f"Bất đồng nhóm {d['label']}: thuận ở {', '.join(titles[x] for x in d['favourable_in'])}; bất lợi ở {', '.join(titles[x] for x in d['unfavourable_in'])}. Không có quy tắc ưu tiên giữa các phương pháp trong nguồn.",
                chain=chain(f"Vai trò nhóm {d['label']} theo từng phương pháp", "Mỗi phương pháp độc lập; không cộng điểm giữa các phương pháp", f"thuận: {', '.join(titles[x] for x in d['favourable_in'])}; bất lợi: {', '.join(titles[x] for x in d['unfavourable_in'])}", "Mâu thuẫn được nêu, không giải quyết"),
                caveats=["Sách không nêu cách chọn giữa các phương pháp khi chúng bất đồng."]))
    if C["consensus"]:
        items.append(Item(
            id="dung-than.dong-thuan", chapter="dung-than", section="bat-dong", basis="tinh_toan", school="he_thong", review="computed", direction="cau_truc",
            headline=f"Nhóm các phương pháp cùng nêu: {glist(C['consensus'])}",
            easy=f"Các phương pháp áp dụng đều nêu nhóm {glist(C['consensus'])} với cùng vai trò. Sự đồng thuận không phải là bằng chứng rằng nó đúng; các phương pháp chia sẻ một số dữ kiện đầu vào.",
            expert=f"Đồng thuận (cùng vai trò ở ≥ 2 phương pháp, không có phương pháp nào trái chiều): {glist(C['consensus'])}.", chain=chain("Bảng vai trò của các phương pháp", "So khớp vai trò giữa phương pháp", "không có phương pháp trái chiều", f"Cùng nêu {glist(C['consensus'])}"), caveats=["Đồng thuận giữa các phương pháp dùng chung dữ kiện không phải là kiểm chứng độc lập."]))
    return items


# ---------------------------------------------------------------- composer
CH_REFS = {"tinh-cach": ["nen-tang.nguyet-lenh", "nen-tang.khi-the-tvh", "nen-tang.khi-the-he-thong"], "nang-luc": ["nen-tang.cach-chinh", "nen-tang.nhom-nhieu"], "su-nghiep": ["nen-tang.cach-chinh", "nen-tang.khi-the-tvh"],
           "tai-loc": ["nen-tang.khi-the-tvh", "nen-tang.nhom-nhieu"], "hon-nhan": ["nen-tang.nguyet-lenh"], "dai-van": ["nen-tang.cach-chinh"], "dung-than": ["nen-tang.dieu-hau", "nen-tang.cach-chinh"]}


def order_key(it: Item, sec_order: list[str]):
    return (sec_order.index(it.section) if it.section in sec_order else 99, BASIS_ORDER[it.basis], it.id)


def summarize(items: list[Item], gaps: list[dict]) -> tuple[str, str]:
    n = {b: sum(1 for i in items if i.basis == b and i.kind in ("sach", "phuong_phap", "tinh_toan")) for b in BASIS_ORDER}
    books = [i for i in items if i.kind in ("sach", "phuong_phap") and i.basis in ("co_nguon", "truong_phai")]
    pick = [i for i in books if i.basis == "co_nguon"][:3] or books[:3]
    tail = f" (Dựa trên {n['co_nguon']} diễn giải có nguồn, {n['truong_phai']} giả thuyết trường phái, {n['tinh_toan']} dữ kiện tính toán; còn {len(gaps)} chỗ chưa đủ căn cứ.)"
    if not pick:
        struct = [i for i in items if i.kind in ("cau_truc", "tinh_toan")]
        return ("Không có quy tắc nào của các sách đã nhập khớp lá số này trong chương này, nên hệ thống không đưa ra nhận định. Phần dưới chỉ nêu các dữ kiện cấu trúc liên quan và giới hạn." + tail,
                f"Không luật nào kích hoạt (sach/phuong_phap = 0); {len(struct)} mục cấu trúc/tính toán." + f" | gaps {len(gaps)}.")
    easy = "; ".join(i.headline.rstrip(".") for i in pick) + "." + tail
    expert = "; ".join(f"[{SPEC['basis'][i.basis]}] {i.headline.rstrip('.')}" for i in pick) + f" | co_nguon {n['co_nguon']}, truong_phai {n['truong_phai']}, tinh_toan {n['tinh_toan']}, gaps {len(gaps)}."
    return easy, expert


def pair_opposites(items: list[Item]) -> list[dict]:
    pairs = []
    by_sec: dict[str, list[Item]] = {}
    for i in items:
        by_sec.setdefault(i.section, []).append(i)
    for sec, xs in by_sec.items():
        good = [x for x in xs if x.direction == "thuan" and x.basis != "tinh_toan"]
        bad = [x for x in xs if x.direction == "bat_loi" and x.basis != "tinh_toan"]
        if good and bad:
            for g in good:
                g.counter = sorted(set(g.counter + [b.id for b in bad]))
            for b in bad:
                b.counter = sorted(set(b.counter + [g.id for g in good]))
            pairs.append({"section": sec, "thuan": [g.id for g in good], "bat_loi": [b.id for b in bad],
                          "note": "Hai nhóm điều kiện đi ngược chiều trong cùng một mục; cả hai được nêu và không cộng trừ cho nhau."})
    return pairs


def compose(analysis: dict, view: ChartView, bz, timeline: dict | None = None) -> dict:
    A = analysis
    found: list[Item] = []
    for prov in (f_nguyet_lenh, f_khi_the, f_han_noan, f_cach_cuc, f_tuong_tac, f_thap_than):
        found += prov(A, view)
    zz, unrouted = zz_items(bz, view, A)
    chap_items: dict[str, list[Item]] = {c["id"]: [] for c in SPEC["chapters"]}
    for it in zz:
        chap_items[it.chapter].append(it)
    chap_items["tai-loc"] += [shares_item(A, "tai-loc", "cau-truc", "Tai")]
    for ch, groups in (("tai-loc", ["Tai"]), ("su-nghiep", ["QuanSat"]), ("nang-luc", ["An", "ThucThuong"])):
        for g in groups:
            r = method_role_item(A, ch, "cau-truc", g, view)
            if r:
                chap_items[ch].append(r)
    chap_items["su-nghiep"].append(shares_item(A, "su-nghiep", "cau-truc", "QuanSat"))
    chap_items["nang-luc"].append(shares_item(A, "nang-luc", "cau-truc", "An"))
    chap_items["hon-nhan"].append(day_branch_item(A, view))
    chap_items["dai-van"] += van_items(A, view, bz, timeline)
    chap_items["dung-than"] += dung_than_items(A, view)
    byid = {i.id: i for i in found}
    chapters = []
    for c in SPEC["chapters"]:
        items = chap_items[c["id"]]
        sec_order = [s["id"] for s in c["sections"]]
        items.sort(key=lambda i: order_key(i, sec_order))
        gaps = c["gaps"]
        easy, expert = summarize(items, gaps)
        pairs = pair_opposites(items)
        top = [i for i in items if i.basis in ("co_nguon", "truong_phai")][:3] or items[:3]
        why = [{"headline": i.headline, "du_kien": next(s["text"] for s in i.chain if s["step"] == "du_kien"), "quy_tac": next(s["text"] for s in i.chain if s["step"] == "quy_tac"), "ket_luan": next(s["text"] for s in i.chain if s["step"] == "ket_luan"),
                "sources": i.sources, "basis": i.basis} for i in top if i.chain]
        chapters.append({
            "id": c["id"], "title": c["title"], "question": c["question"], "summary_easy": easy, "summary_expert": expert, "why": why,
            "sections": [{"id": s["id"], "title": s["title"], "items": [i.out() for i in items if i.section == s["id"]]} for s in c["sections"] if any(i.section == s["id"] for i in items)],
            "advantages": [i.id for i in items if i.direction == "thuan"], "disadvantages": [i.id for i in items if i.direction == "bat_loi"],
            "opposing": pairs, "gaps": [{"aspect": g["aspect"], "basis": "chua_du_can_cu", "basis_vi": SPEC["basis"]["chua_du_can_cu"], "easy": g["easy"], "expert": g["expert"]} for g in gaps],
            "refs": [{"id": r, "headline": byid[r].headline} for r in CH_REFS.get(c["id"], []) if r in byid],
            "n_items": len(items), "empty": not any(i.kind in ("sach", "phuong_phap") for i in items)})
    foundation = {"id": "nen-tang", "title": SPEC["foundation"]["title"], "question": SPEC["foundation"]["question"],
                  "sections": [{"id": s["id"], "title": s["title"], "items": [i.out() for i in found if i.section == s["id"]]} for s in SPEC["foundation"]["sections"] if any(i.section == s["id"] for i in found)]}
    allitems = found + [i for v in chap_items.values() for i in v]
    return {"version": SPEC["version"], "status": "draft", "label": SPEC["label"], "pillars": four_pillars(view), "foundation": foundation, "chapters": chapters, "limits": SPEC["limits_global"],
            "basis_vocabulary": SPEC["basis"], "unrouted_rules": unrouted,
            "counts": {b: sum(1 for i in allitems if i.basis == b) for b in BASIS_ORDER}, "item_ids": sorted(i.id for i in allitems)}
