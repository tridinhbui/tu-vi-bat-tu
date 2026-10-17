"""Cách cục đặc biệt theo Thiệu Vĩ Hoa (Dự Đoán Theo Tứ Trụ, trang in 369-376, bản dịch Việt): chuyên vượng (khúc trực, viêm thượng, gia sắc/gia tường,
tòng cách, nhuận hạ), tòng tài / tòng sát / tòng nhi và hóa khí. Mỗi cách có các điều kiện NGUYÊN VĂN của sách; chỗ sách nói 'rất nhiều' hay 'vượng'
được vận hành bằng ngưỡng trong SchoolProfile (draft). Các ví dụ của sách (mỗi cách 2-5 lá số) là bộ kiểm thử trong tests/test_bazi_deep_tvh_cach.py.
Một can 'phá cách' chỉ tính khi có chỗ dựa theo phép thử chỗ dựa của chính sách (can hư phù vô lực không phá cách: ví dụ 2 và 3 của viêm thượng)."""
from __future__ import annotations

from ..ganzhi import BRANCH_ELEMENT, STEM_ELEMENT, STEMS_VI
from .model import ChartView
from .profile import SchoolProfile
from .tvh_score import score

NAMES = {"Mộc": ("Khúc Trực", (0, 1), {2, 3, 4, 7, 11}, "Kim", {6, 7}, {9}),          # (name, DM stems, month branches, enemy element, enemy stems, enemy branches)
         "Hỏa": ("Viêm Thượng", (2, 3), {5, 6, 7, 2, 10}, "Thủy", {8, 9}, {11, 0}),
         "Thổ": ("Gia Sắc", (4, 5), {4, 10, 1, 7}, "Mộc", {0, 1}, {2, 3}),
         "Kim": ("Tòng Cách", (6, 7), {8, 9, 10}, "Hỏa", {2, 3}, {5, 6}),
         "Thủy": ("Nhuận Hạ", (8, 9), {11, 0, 4, 8, 1}, "Thổ", {4, 5}, {10, 7})}
# enemy stems: Mộc <- Canh Tân (+ Dậu); Hỏa <- Nhâm Quý (+ Hợi Tý); Thổ <- Giáp Ất (+ Dần Mão); Kim <- Bính Đinh (+ Ngọ Tỵ); Thủy <- Mậu Kỷ (+ Tuất Mùi)
ENEMY_STEMS = {"Mộc": {6, 7}, "Hỏa": {8, 9}, "Thổ": {0, 1}, "Kim": {2, 3}, "Thủy": {4, 5}}
ENEMY_BRANCHES = {"Mộc": {9}, "Hỏa": {11, 0}, "Thổ": {2, 3}, "Kim": {5, 6}, "Thủy": {10, 7}}
DM_STEMS = {"Mộc": (0, 1), "Hỏa": (2, 3), "Thổ": (4, 5), "Kim": (6, 7), "Thủy": (8, 9)}
MONTHS = {"Mộc": {2, 3, 4, 7, 11}, "Hỏa": {5, 6, 7, 2, 10}, "Thổ": {4, 10, 1, 7}, "Kim": {8, 9, 10}, "Thủy": {11, 0, 4, 8, 1}}
CHUYEN = {"Mộc": "Khúc Trực", "Hỏa": "Viêm Thượng", "Thổ": "Gia Sắc", "Kim": "Tòng Cách", "Thủy": "Nhuận Hạ"}
KHO = {1, 4, 7, 10}


def chuyen_vuong(view: ChartView, r: dict, profile: SchoolProfile) -> list[dict]:
    root = r["notes"]["steps"][0]["root"]
    out = []
    el = {s: STEM_ELEMENT[s] for s in view.stems}
    for E, name in CHUYEN.items():
        dm_hoa = r["hua_stem"].get("day") == E          # e.g. book example 3 of nhuận hạ: Bính–Tân hóa Thủy, day stem Tân
        if view.dm not in DM_STEMS[E] and not dm_hoa:
            continue
        ev = {}
        ev["can_ngay"] = True
        mb = view.month_branch
        ev["thang_dung"] = mb in MONTHS[E] or (E == "Thổ" and set(view.branches) >= {4, 10, 1, 7})
        formed = [u for u in r["branch_units"] if u["el"] == E]
        chars = sum(STEM_ELEMENT[s] == E for s in view.stems) + sum(BRANCH_ELEMENT[b] == E for b in view.branches)
        if E == "Thổ":
            ev["du_kho"] = sum(b in KHO for b in view.branches) >= 3
        else:
            ev["cuc_hoac_nhieu"] = bool(formed) or chars >= profile.chuyen_vuong_chars
        enemy_st = [STEMS_VI[s] for i, s in enumerate(view.stems) if s in ENEMY_STEMS[E] and root[i]]
        enemy_br = [b for b in view.branches if b in ENEMY_BRANCHES[E] and not (E == "Kim" and b == 5 and any(u["el"] == "Kim" for u in formed))]
        ev["khong_bi_pha"] = not enemy_st and not enemy_br
        ev["enemy"] = {"can_co_goc": enemy_st, "chi": enemy_br}
        need = ["thang_dung", "khong_bi_pha"] + (["du_kho"] if E == "Thổ" else ["cuc_hoac_nhieu"])
        if all(ev[k] for k in need):
            out.append({"name": name, "kind": "chuyen_vuong", "quality": "chân", "element": E, "evidence": ev, "src": "SRC_TVH_CACH"})
    return out


def tong_tvh(view: ChartView, S: dict, r: dict, profile: SchoolProfile) -> list[dict]:
    from .strength import GROUPS, group_of_element
    tot = sum(r["totals"].values()) or 1.0
    sh = {g: 0.0 for g in GROUPS}
    for e, v in r["totals"].items():          # group shares from the SCORED totals (hóa, xung, lệnh already applied), as the book's own method does
        sh[group_of_element(r["dm_element"], e)] += v / tot
    root_dm = r["root_main"][2]         # tòng needs "không có khí gốc": a 3-9 degree tạp khí does not count (book examples tòng tài 1, tòng nhi 1)
    out = []
    if r["dm_strong"] or root_dm:
        return out
    ti_an = sh["Ti"] + sh["An"]

    def has(group_gods):                      # "có Tài / có Quan Sát..." = the group shows on a stem or is the main qi of a branch
        gods = {view.god(s) for p, s in view.visible_stems(include_day=False)} | {view.god(view.hidden(p)[0]["stem"]) for p in ("year", "month", "day", "hour")}
        return bool(gods & set(group_gods))
    if ti_an <= profile.tvh_no_help and sh["Tai"] >= profile.tvh_tong_main:
        out.append({"name": "Tòng Tài (TVH)", "kind": "tong_tvh", "quality": "chân", "evidence": {"tai": round(sh["Tai"], 4), "ti_an": round(ti_an, 4)}, "src": "SRC_TVH_CACH"})
    if ti_an <= profile.tvh_no_help and sh["QuanSat"] >= profile.tvh_tong_main and sh["ThucThuong"] <= profile.tvh_no_help and has(("Chính Tài", "Thiên Tài")):
        out.append({"name": "Tòng Sát (TVH)", "kind": "tong_tvh", "quality": "chân", "evidence": {"quan_sat": round(sh["QuanSat"], 4), "co_tai": True}, "src": "SRC_TVH_CACH"})
    month_gods = {view.god(view.stem("month"))} | {h["ten_god"] for h in view.hidden("month")}
    if month_gods & {"Thực Thần", "Thương Quan"} and sh["ThucThuong"] >= profile.tvh_tong_main and has(("Chính Tài", "Thiên Tài")) and sh["QuanSat"] + sh["An"] <= profile.tvh_no_help:
        out.append({"name": "Tòng Nhi (TVH)", "kind": "tong_tvh", "quality": "chân", "evidence": {"thuc_thuong": round(sh["ThucThuong"], 4), "chi_thang_co_thuc_thuong": True}, "src": "SRC_TVH_CACH"})
    return out


def hoa_khi(view: ChartView, r: dict, profile: SchoolProfile) -> list[dict]:
    hs = r["hua_stem"]
    if "day" not in hs:
        return []
    E = hs["day"]
    mb = view.month_branch
    ev = {"hoa_than": E, "chi_thang_cung_hanh": BRANCH_ELEMENT[mb] == E or E in {STEM_ELEMENT[s] for s, g in __import__("tvbt.bazi_deep.tvh_score", fromlist=["HID_DEG"]).HID_DEG[mb] if g >= 9}}
    tot = sum(r["totals"].values()) or 1.0
    ev["chuyen_vuong"] = r["own_share"] >= profile.chuyen_vuong_share        # phe mình of the transformed day master (hóa thần + the element that generates it)
    ev["note_hy_than"] = "điều kiện 4 (hỉ thần thực thương xì hơi thế vượng) chưa kiểm"
    if ev["chi_thang_cung_hanh"] and ev["chuyen_vuong"]:
        return [{"name": f"Hóa {E} (TVH)", "kind": "hoa_tvh", "quality": "chân", "evidence": ev, "src": "SRC_TVH_CACH"}]
    return []


def special(view: ChartView, S: dict, profile: SchoolProfile) -> list[dict]:
    r = S.get("tvh") or score(view)
    return chuyen_vuong(view, r, profile) + tong_tvh(view, S, r, profile) + hoa_khi(view, r, profile)
