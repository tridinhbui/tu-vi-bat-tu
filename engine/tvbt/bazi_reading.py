"""Bát Tự assessment layer (docs/REASONING-ENGINE-DESIGN.md §5): a transparent, source-labelled reading of the natal chart and its periods.

What it does, in order, and on what authority:
  1 Nhật Chủ and Nguyệt Lệnh            calculation (bazi.py), season by month branch.
  2 strength, two methods side by side   八字真宗 p.27: "以得令、得位、得生为旺，以失令、失位、无生为弱" — all three present = vượng, all three
                                         absent = nhược, anything else = the book gives no verdict. The three tests are operationalised below
                                         (the book does not define them; marked as such).
                                         Thiệu Vĩ Hoa, Dự Đoán Theo Tứ Trụ pp.331-355: degree scoring and the 40% rule, applied strictly (the
                                         book's example 6, 0.396, is called nhược; no tolerance band is added here).
  3 Thập Thần, visible and hidden        calculation.
  4 interactions                         八字真宗 pp.19-20 (hợp, 干冲克, lục hợp, tam hợp, xung, hình, hại, phá); a hợp is a POTENTIAL
                                         combination; whether it transforms is not decided (TVH pp.336-338 only considers adjacent ngũ hợp).
  5 Dụng / Hỷ / Kỵ                       not concluded: the methods in the repo are draft or school-specific; the điều hậu cell of Thiệu Vĩ Hoa
                                         (pp.389-396, origin of the table unknown per p.388) is shown as one school's list.
  6 periods                              đại vận and lưu niên interactions with the natal pillars, structural only.
Element counts are shown as counts and never called strength.
"""
from __future__ import annotations

from .bazi import BaziChart
from .ganzhi import BRANCHES_VI, ELEMENTS, STEM_ELEMENT, STEMS_VI, generates

SEASON = {2: "xuân", 3: "xuân", 4: "xuân", 5: "hạ", 6: "hạ", 7: "hạ", 8: "thu", 9: "thu", 10: "thu", 11: "đông", 0: "đông", 1: "đông"}
PILLAR_VI = {"year": "Năm", "month": "Tháng", "day": "Ngày", "hour": "Giờ"}
REL_VI = {"stem_combine": "thiên can hợp", "stem_clash": "thiên can xung/khắc", "branch_six_combine": "địa chi lục hợp",
          "branch_clash": "địa chi lục xung", "branch_harm": "địa chi hại", "branch_destroy": "địa chi phá", "branch_penalty": "địa chi hình",
          "branch_self_penalty": "tự hình", "branch_triad_complete": "tam hợp đủ bộ", "branch_meeting_complete": "tam hội đủ bộ"}
ORDER = ["year", "month", "day", "hour"]


def _gen_of(el: str) -> str:
    return next(e for e in ELEMENTS if generates(e, el))


def strength_zz(c: BaziChart) -> dict:
    """八字真宗 p.27 three-test rule. Operationalisation (NOT printed in the book, open to review):
    得令: the month branch's main hidden stem has the day master's element or generates it.
    得位: some branch hides a stem of the day master's element (a root).
    得生: some stem other than the day master, or some branch's main hidden stem, generates the day master (an Ấn)."""
    dm = c.day_master_element
    gen = _gen_of(dm)
    month_main = STEM_ELEMENT[c.pillars["month"].hidden[0]["stem"]]
    lenh = month_main in (dm, gen)
    roots = [k for k in ORDER for h in c.pillars[k].hidden if h["element"] == dm]
    vi = bool(roots)
    sinh_src = [f"{PILLAR_VI[k]} (can {STEMS_VI[c.pillars[k].stem]})" for k in ORDER if k != "day" and STEM_ELEMENT[c.pillars[k].stem] == gen]
    sinh_src += [f"{PILLAR_VI[k]} (chi, bản khí {c.pillars[k].hidden[0]['name']})" for k in ORDER if c.pillars[k].hidden[0]["element"] == gen]
    sinh = bool(sinh_src)
    tests = {"dac_lenh": lenh, "dac_vi": vi, "dac_sinh": sinh}
    verdict = "vượng" if all(tests.values()) else "nhược" if not any(tests.values()) else None
    return {"method": "Ba tiêu chí đắc lệnh – đắc vị – đắc sinh", "source": "八字真宗, tr.27", "tests": tests,
            "detail": {"month_main_element": month_main, "roots": sorted(set(roots)), "sinh_from": sinh_src},
            "verdict": verdict,
            "verdict_vi": (f"theo tiêu chí này: {verdict}" if verdict else
                           "sách chỉ kết luận khi cả ba cùng có (vượng) hoặc cùng không (nhược); ở đây các tiêu chí không cùng chiều nên sách không cho kết luận"),
            "operationalisation": "Sách không định nghĩa ba tiêu chí; hệ thống hiểu đắc lệnh = bản khí chi tháng cùng hành hoặc sinh Nhật Chủ, "
                                  "đắc vị = có tàng can cùng hành Nhật Chủ trong địa chi, đắc sinh = có can hoặc bản khí chi sinh Nhật Chủ."}


def strength_tvh(c: BaziChart) -> dict | None:
    """Thiệu Vĩ Hoa pp.331-355 degree scoring and 40% rule, strictly as printed (no tolerance band)."""
    try:
        from .bazi_deep import tvh_score
        from .bazi_deep.model import ChartView
        v = ChartView.from_names(" / ".join(c.pillars[k].name for k in ORDER))
        r = tvh_score.score(v)
    except Exception as e:  # pragma: no cover - scoring must never break the reading
        return {"method": "Thiệu Vĩ Hoa, 40%", "error": str(e)}
    share = r["own_share"]
    return {"method": "Chấm độ và ngưỡng 40% (phe mình = cùng hành + hành sinh)", "source": "Thiệu Vĩ Hoa, Dự Đoán Theo Tứ Trụ, tr.331-355",
            "totals": r["totals"], "own_share": share, "threshold": r["threshold"], "verdict": "vượng" if r["dm_strong"] else "nhược",
            "near_threshold": abs(share - r["threshold"]) < 0.03,
            "notes": r["notes"].get("unsupported", []) + r["notes"].get("assumptions", []),
            "caveat": "Sách không cho biên dung sai quanh 40%; ví dụ 6 của sách (39,6%) được gọi là nhược. Bản bazi_deep thêm một biên ±3% do hệ thống tự đặt; ở đây không dùng biên đó."}


def interactions(c: BaziChart) -> list[dict]:
    out = []
    for key, items in c.relations.items():
        for r in items:
            pillars = r.get("pillars", "")
            ps = pillars.split("-") if pillars else []
            span = abs(ORDER.index(ps[0]) - ORDER.index(ps[1])) if len(ps) == 2 else None
            d = {"kind": key, "kind_vi": REL_VI.get(key, key), "pillars": [PILLAR_VI[p] for p in ps], "span": span, "source": "八字真宗, tr.19-20"}
            if key == "stem_clash":
                d["kind_vi"] = "thiên can " + r.get("kind", "xung")
            if key == "branch_penalty" and r.get("kind"):
                d["subtype"] = r["kind"]
            if key == "stem_combine":
                d["potential_element"] = r.get("potential_element")
                d["transform"] = "chưa xét"
                d["note"] = ("hợp kề nhau; hóa hay không còn tùy điều kiện (mùa, thấu can, xung phá) mà hệ thống chưa xét" if span == 1 else
                             "hai can cách xa nhau; Thiệu Vĩ Hoa (tr.336-338) chỉ xét ngũ hợp của can kề nhau, nên theo cách này không xét hóa")
            out.append(d)
    return out


def ten_gods(c: BaziChart) -> dict:
    vis = {PILLAR_VI[k]: c.pillars[k].stem_ten_god for k in ORDER if k != "day"}
    hid = {PILLAR_VI[k]: [f"{h['name']} ({h['ten_god']})" for h in c.pillars[k].hidden] for k in ORDER}
    return {"visible": vis, "hidden": hid}


def element_counts(c: BaziChart) -> dict:
    from .ganzhi import BRANCH_ELEMENT
    vis = {e: 0 for e in ELEMENTS}
    for k in ORDER:
        vis[STEM_ELEMENT[c.pillars[k].stem]] += 1
        vis[BRANCH_ELEMENT[c.pillars[k].branch]] += 1
    hidden = {e: sum(1 for k in ORDER for h in c.pillars[k].hidden if h["element"] == e) for e in ELEMENTS}
    return {"visible_8": vis, "hidden": hidden, "note": "Đây là số lần xuất hiện, không phải độ mạnh; độ mạnh xem mục phương pháp."}


def periods(c: BaziChart, birth_year: int, year: int) -> dict:
    from . import temporal
    y = temporal.bazi_year(c, birth_year, year)
    fmt = lambda xs: [{"with": PILLAR_VI.get(x["with"], x["with"]), "kind": x["kind"].replace("_", " "), "from": x["from"]} for x in xs]
    return {"year": year, "annual_pillar": y["annual_pillar"], "annual_ten_god": y["annual_stem_ten_god"], "luck_pillar": y["luck_pillar"],
            "luck_ten_god": y["luck_stem_ten_god"], "luck_changes_within_year": y["luck_changes_within_year"],
            "annual_vs_natal": fmt(y["annual_vs_natal"]), "luck_vs_natal": fmt(y["luck_vs_natal"]),
            "scope": "Tương tác cấu trúc giữa chữ của năm/vận và chữ gốc; không phải dự đoán sự kiện. Hệ thống chưa có quy tắc đã đối chiếu "
                     "nào nói một tương tác cụ thể ứng với chuyện gì."}


def build(c: BaziChart, birth_year: int, year: int | None = None) -> dict:
    dm = STEMS_VI[c.day_master]
    mb = c.pillars["month"].branch
    zz, tvh = strength_zz(c), strength_tvh(c)
    try:
        from .bazi_deep import dieuhau
        from .bazi_deep.model import ChartView
        dh = dieuhau.lookup(ChartView.from_names(" / ".join(c.pillars[k].name for k in ORDER)))
    except Exception:  # pragma: no cover
        dh = None
    verdicts = {v for v in (zz["verdict"], (tvh or {}).get("verdict")) if v}
    agree = len(verdicts) == 1 and zz["verdict"] is not None
    strength_summary = (
        f"Hai phương pháp cùng cho kết quả {next(iter(verdicts))}." if agree else
        f"Theo Thiệu Vĩ Hoa (ngưỡng 40%): {tvh['verdict']} (phe mình {tvh['own_share'] * 100:.1f}%). Theo 八字真宗 tr.27: {zz['verdict_vi']}. "
        "Vì hai phương pháp không cùng đưa ra kết luận, hệ thống nêu cả hai và không tự chọn." if tvh and "verdict" in tvh else zz["verdict_vi"])
    return {
        "nhat_chu": {"stem": dm, "element": c.day_master_element, "month_branch": BRANCHES_VI[mb], "season": SEASON[mb],
                     "month_main_element": STEM_ELEMENT[c.pillars["month"].hidden[0]["stem"]], "stage_in_month": c.pillars["month"].stage_vs_day_master},
        "strength": {"methods": [m for m in (zz, tvh) if m], "summary": strength_summary,
                     "rule": "Không suy độ mạnh từ số lượng hành; chỉ dùng tiêu chí có trong sách."},
        "ten_gods": ten_gods(c), "element_counts": element_counts(c), "interactions": interactions(c),
        "dung_than": {"status": "chưa kết luận",
                      "why": "Các phương pháp chọn Dụng thần trong hệ thống (phù ức, cách cục, thông quan) còn ở dạng nháp hoặc phụ thuộc trường phái; "
                             "chưa có phương pháp nào được duyệt để kết luận.",
                      "school_lists": [{"method": "Điều hậu (bảng trong Thiệu Vĩ Hoa tr.389-396)", "cell": dh.get("cell"),
                                        "stems": [f"{s['stem']} ({s['ten_god']}, {s['rank']})" for s in dh.get("yong_stems", [])],
                                        "caveat": "Thiệu Vĩ Hoa (tr.388) nói bảng do độc giả gửi, không rõ xuất xứ; đây là danh sách của một trường phái, không phải kết luận."}]
                      if dh else []},
        "periods": periods(c, birth_year, year) if year else None,
    }
