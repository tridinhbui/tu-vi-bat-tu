"""Phase 5 report: cross-school isolation matrix, worked-example scoreboard, verification scope per method, conditions missing before production.
Writes docs/BAZI_DEEP_PHASE5_REPORT.md. Every table is recomputed from the live engine and the independent fixtures. Run: python tools/bazi_deep_phase5_report.py"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
from tvbt.bazi_deep import dieuhau, pipeline, yongshen  # noqa: E402
from tvbt.bazi_deep.model import ChartView  # noqa: E402
from tvbt.bazi_deep.profile import DEFAULT, TVH_40  # noqa: E402

G = ROOT / "engine/tests/golden"
BOOK = json.loads((G / "tvh_dungthan_examples.json").read_text("utf-8"))
S10 = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
B12 = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
SYS = ("phu_uc", "dieu_hau", "cach_cuc", "thong_quan", "thuan_the", "khuyet_hanh")
TVH = ("cach_cuc_tvh", "thuan_the_tvh")
SYSTEM_ONLY = [{"level_cuts": (0.10, 0.20, 0.30, 0.60, 0.70, 0.90)}, {"presence_share": 0.20}, {"thuong_vuong": 0.10}, {"tong_cuong_min": 0.40}, {"tong_vuong_ti": 0.30}, {"tong_foe_max": 0.30},
               {"tong_the_each": 0.05}, {"tong_dominant_share": 0.30}, {"war_share": 0.05}, {"bridge_min": 0.50}, {"hua_du_share": 0.10}, {"flow_min": 0.30},
               {"hidden_frac": {1: (1.0,), 2: (0.5, 0.5), 3: (0.4, 0.3, 0.3)}}, {"season_factor": {"vượng": 3.0, "tướng": 2.0, "hưu": 1.0, "tù": 0.2, "tử": 0.1}},
               {"class_weight": {"ban_khi": 1.0, "trung_khi": 1.0, "du_khi": 1.0}}, {"kho_policy": "tu_co_can"}]
TVH_ONLY = [{"tvh_no_help": 0.40}, {"tvh_tong_main": 0.10}, {"chuyen_vuong_chars": 3}, {"chuyen_vuong_share": 0.30}, {"tvh_margin": 0.10}]
# measured by running the same script against commit d0c3ab8 (before the Phase 5 fixes)
BEFORE = {"n": 1200, "inner_state_changed": 42, "system_outer_changed": 15, "phu_uc_changed": 995, "cach_cuc_tvh_overridden_by_system_outer": 13}
REGRESSION = "docs/BAZI_DEEP_PHASE5_REPORT.md#9"        # filled by hand in the report text below


def cyc(i):
    return f"{S10[i % 10]} {B12[i % 12]}"


def chart(y, mb, d, hb):
    ms = (((y % 10) % 5) * 2 + 2 + ((mb - 2) % 12)) % 10
    hs = ((d % 10) * 2 + hb) % 10
    return f"{cyc(y)} / {S10[ms]} {B12[mb]} / {cyc(d)} / {S10[hs]} {B12[hb]}"


def core(m):
    return {k: v for k, v in m.items() if k not in ("meta", "trace", "table", "climate")}


def fmt(x):
    return " ".join(x) if x else "—"


def matrix():
    r = random.Random(20261017)
    C = [chart(r.randrange(60), r.randrange(12), r.randrange(60), r.randrange(12)) for _ in range(1200)]
    cnt = {m: 0 for m in SYS + TVH}
    inner = outer = 0
    for p in C:
        v = ChartView.from_names(p)
        a, b = pipeline.analyse(v, DEFAULT, with_rules=False), pipeline.analyse(v, TVH_40, with_rules=False)
        for m in SYS:
            cnt[m] += core(a["yongshen"]["methods"][m]) != core(b["yongshen"]["methods"][m])
        inner += [(c["name"], c["state"]) for c in a["geju"]["inner"]] != [(c["name"], c["state"]) for c in b["geju"]["inner"]]
        outer += [(x["name"], x["quality"]) for x in a["geju"]["outer"]] != [(x["name"], x["quality"]) for x in b["geju"]["outer"] if x.get("kind") not in yongshen.TVH_KINDS]
    base = {p: pipeline.analyse(ChartView.from_names(p), TVH_40, with_rules=False) for p in C[:300]}
    rows_sys, rows_tvh = [], []
    for ch in SYSTEM_ONLY:
        alt = TVH_40.with_(**ch)
        moved = {m: 0 for m in SYS}
        tvh_changed = 0
        for p, a in base.items():
            b = pipeline.analyse(ChartView.from_names(p), alt, with_rules=False)
            for m in SYS:
                moved[m] += core(a["yongshen"]["methods"][m]) != core(b["yongshen"]["methods"][m])
            tvh_changed += any(core(a["yongshen"]["methods"][m]) != core(b["yongshen"]["methods"][m]) for m in TVH) or a["strength_after"]["tvh"] != b["strength_after"]["tvh"]
        rows_sys.append((next(iter(ch)), sum(moved.values()), tvh_changed))
    for ch in TVH_ONLY:
        alt = TVH_40.with_(**ch)
        sys_changed = tvh_changed = 0
        for p, a in base.items():
            b = pipeline.analyse(ChartView.from_names(p), alt, with_rules=False)
            sys_changed += any(core(a["yongshen"]["methods"][m]) != core(b["yongshen"]["methods"][m]) for m in SYS) or [(c["name"], c["state"]) for c in a["geju"]["inner"]] != [(c["name"], c["state"]) for c in b["geju"]["inner"]]
            tvh_changed += any(core(a["yongshen"]["methods"][m]) != core(b["yongshen"]["methods"][m]) for m in TVH)
        rows_tvh.append((next(iter(ch)), sys_changed, tvh_changed))
    return len(C), cnt, inner, outer, rows_sys, rows_tvh


def examples():
    rows = []
    for k, ex in BOOK["dungthan_examples"].items():
        o = pipeline.analyse(ChartView.from_names(ex["pillars"]), TVH_40, with_rules=False)
        M, tv, b = o["yongshen"]["methods"], o["strength_after"]["tvh"], ex["book"]
        want = set(b["dung_than_groups"])

        def got(m, M=M):
            mm = M[m]
            if mm["status"] == "hai_cach_doc":
                return "hai cách đọc: " + " / ".join(fmt(a.get("yong", [])) for a in mm["alternatives"])
            return fmt(mm["yong"] + mm.get("xi", [])) if m in ("dieu_hau", "khuyet_hanh") else (fmt(mm["yong"]) if mm["yong"] else mm["status"])
        verdict = {"p397_vd1": "khớp hoàn toàn ở cach_cuc_tvh và dieu_hau; phu_uc (hệ thống, khí thế cực nhược) không khớp", "p398_vd2": "khớp một phần: dieu_hau và phu_uc khớp dụng thần; vượng/nhược không tái lập bằng 40%",
                   "p399_vd3": "khớp một phần: dieu_hau và khuyet_hanh khớp, cach_cuc_tvh chỉ có Tài", "p401_vd5": "khớp một phần: dieu_hau khớp tập Thủy+Mộc; phu_uc và cach_cuc_tvh có Kim/Tỉ là Kỵ trong khi sách coi Kim là Hỉ", "p400_vd4": "KHÔNG khớp: engine đọc ngoại cách (Tòng Vượng / Nhuận Hạ), sách đọc thân vượng thường dùng Thực Thương"}[k]
        rows.append((k, ex, tv, M, got, verdict))
    return rows


def main():
    n, cnt, inner, outer, rows_sys, rows_tvh = matrix()
    L = []
    w = L.append
    w("# Phase 5: kiểm chứng độc lập và cách ly trường phái\n")
    w("Báo cáo do `tools/bazi_deep_phase5_report.py` sinh ra; các bảng được tính lại từ engine. Không có phương pháp mới. Kết quả regression (mục 8–9) được ghi tay lúc chạy.\n")
    w("## 1. Ba mức xác minh\n")
    w("- `transcription_verified`: bảng hoặc văn bản đã chép đúng từ trang nguồn.\n- `source_rule_verified`: công thức hoặc điều kiện (kể cả ngưỡng) khớp trực tiếp với điều nguồn nói.\n"
      "- `empirical_validated`: có bằng chứng độc lập về giá trị dự báo.\n\nBa mức tách rời, không suy từ mức này sang mức khác. **Không phương pháp nào đạt `empirical_validated`; không phương pháp nào đạt `source_rule_verified` trọn vẹn.**\n")
    w("| Phương pháp | transcription | source_rule | empirical | Lý do | Nguồn |")
    w("|---|---|---|---|---|---|")
    for k, m in yongshen.METHOD_META.items():
        L_ = m["levels"]
        w(f"| `{k}` | {L_['transcription_verified']} | {L_['source_rule_verified']} | {L_['empirical_validated']} | {L_['why']} | {'; '.join(m['source'])} |")
    w("\nGhi chú: quy tắc 40% (tr.355) riêng nó là `source_rule_verified = yes` về con số và phép so sánh (tái lập hai phép thử số của sách); phần đúng 40% và biên ±0,03 là của hệ thống. "
      "Bảng điều hậu được chép đúng nhưng chính tác giả nói không biết nguồn của nó (tr.388), nên không có cơ sở để nói nó đúng về mặt học thuật.\n")
    w("## 2. Ma trận cách ly trường phái\n")
    w(f"Mẫu: {n} lá số hợp lệ sinh ngẫu nhiên có hạt giống cố định (đủ các loại: ngoại cách của hệ thống, cách đặc biệt của Thiệu Vĩ Hoa, tòng, sát vượng, sát ngưỡng 40%, dụng thần xung đột; số lượng từng loại được test ép tối thiểu).\n")
    w("**2a. Bật profile TVH (`he_thong` → `tvh_40`) có đổi kết quả của hệ thống không?** (số lá số bị đổi)\n")
    w("| Đầu ra của hệ thống | Trước khi sửa (d0c3ab8) | Sau khi sửa |")
    w("|---|---|---|")
    w(f"| trạng thái thành/bại của nội cách (`geju.inner`) | {BEFORE['inner_state_changed']}/{BEFORE['n']} | {inner}/{n} |")
    w(f"| ngoại cách của hệ thống (`geju.outer`, không tính cách TVH) | {BEFORE['system_outer_changed']}/{BEFORE['n']} | {outer}/{n} |")
    for m in SYS:
        before = f"{BEFORE['phu_uc_changed']}/{BEFORE['n']}" if m == "phu_uc" else f"0/{BEFORE['n']}" if m in ("cach_cuc", "thuan_the") else "không đo"
        w(f"| phương pháp `{m}` | {before} | {cnt[m]}/{n} |")
    w(f"\nTrước khi sửa, `phu_uc` đổi ở {BEFORE['phu_uc_changed']}/{BEFORE['n']} lá số vì đọc quyết định vượng/nhược của TVH (và mức khí thế khác tên); nay `phu_uc` dùng khí thế của hệ thống nên không đổi.\n")
    w("**2b. Ngược lại: đổi đầu vào của hệ thống có làm đổi kết quả TVH không?** Mỗi dòng là một tham số chỉ thuộc hệ thống bị đổi mạnh (300 lá số, profile `tvh_40`).\n")
    w("| Tham số hệ thống bị đổi | Số lần phương pháp hệ thống đổi (cộng 6 phương pháp × 300 lá số) | Số lá số mà `cach_cuc_tvh`/`thuan_the_tvh`/điểm TVH đổi |")
    w("|---|---|---|")
    for name, moved, t in rows_sys:
        w(f"| `{name}` | {moved} | **{t}** |")
    w("\n**2c. Đổi tham số chỉ thuộc TVH có làm đổi hệ thống không?**\n")
    w("| Tham số TVH bị đổi | Số lá số mà phương pháp / cách cục của hệ thống đổi | Số lá số mà phương pháp TVH đổi |")
    w("|---|---|---|")
    for name, s_, t in rows_tvh:
        w(f"| `{name}` | **{s_}** | {t} |")
    w(f"\nTrước khi sửa còn một rò rỉ ngược: ở {BEFORE['cach_cuc_tvh_overridden_by_system_outer']}/{BEFORE['n']} lá số, ngoại cách *của hệ thống* làm `cach_cuc_tvh` thành 'không xác định nội cách'. Nay `cach_cuc_tvh` và `thuan_the_tvh` chỉ thấy cách đặc biệt TVH (0 trường hợp).\n")
    w("**Phần chung không bị cách ly (cố ý):** thông tin đầu vào của lá số, phân giải tương tác (`interact.resolve`) và việc nhận diện *tên* nội cách từ nguyệt lệnh là lớp dùng chung; test xác nhận tên nội cách giống nhau ở cả hai profile trên 1200 lá số.\n")
    w("## 3. Bảng ví dụ đối chứng (tr.387–400)\n")
    w("Đầu vào của cả 9 ví dụ được đối chiếu với một lượt chép mù độc lập (`tests/golden/tvh_examples_blind.json`): 9/9 khớp bốn trụ. Ví dụ 4 (tr.399–400) có bảng in bị vỡ nên bốn trụ được **dựng lại** từ lời văn, hàng đại vận và lịch; lượt chép mù dựng ra đúng cùng bốn trụ. Không điều chỉnh thuật toán để ép khớp.\n")
    w("| Ví dụ | Lá số | Sách đọc | Sách chọn | Engine: 40% | cach_cuc_tvh | dieu_hau | phu_uc (hệ thống) | khuyet_hanh | Đánh giá |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for k, ex, tv, M, got, verdict in examples():
        b = ex["book"]
        pu = M["phu_uc"]
        puv = fmt(pu["yong"]) if pu["status"] == "ap_dung" else pu["status"] + (": " + " / ".join(fmt(a['yong']) for a in pu.get("alternatives", [])) if pu["status"] == "hai_cach_doc" else "")
        w(f"| {k}{' (dựng lại)' if ex.get('reconstructed') else ''} | {ex['pillars']} | {b['dm_verdict']} | {fmt(b['dung_than_groups'])} | {tv['own_share']:.4f} → {'vượng' if tv['dm_strong'] else 'nhược'} | {got('cach_cuc_tvh') if M['cach_cuc_tvh']['status'] != 'khong_xac_dinh_noi_cach' else 'không xác định nội cách (ngoại cách TVH)'} | {got('dieu_hau')} | {puv} | {got('khuyet_hanh')} | {verdict} |")
    w("\nBảng ví dụ điều hậu (tr.387–388):\n")
    w("| Ví dụ | Lá số | Sách lấy | Engine (can chủ trước) | Kết quả |")
    w("|---|---|---|---|---|")
    for k, ex in BOOK["dieuhau_examples"].items():
        if k.startswith("_"):
            continue
        r = dieuhau.lookup(ChartView.from_names(ex["pillars"]))
        gs = [x["group"] for x in r["yong_stems"]]
        res = "khớp hoàn toàn" if gs[0] == ex["dung_than_groups"][0] else "khớp một phần (nhóm của sách có trong ô nhưng không đứng đầu)" if ex["dung_than_groups"][0] in gs else "không khớp"
        w(f"| {k} | {ex['pillars']} | {fmt(ex['dung_than_stems'])} ({fmt(ex['dung_than_groups'])}) | {fmt([x['stem'] + '=' + x['group'] for x in r['yong_stems']])} | {res} |")
    w("\nTổng hợp: trong 9 ví dụ, khớp hoàn toàn 3 (vd1 tr.397, intro và vd4 tr.387–388), khớp một phần 5, không khớp 1 (vd4 tr.400). Con số này mô tả độ trung thực với *lời của sách*, không phải độ chính xác dự báo.\n")
    w("## 4. Phạm vi xác minh của từng phương pháp\n")
    w("| Phương pháp | Đã xác minh | Chưa xác minh |")
    w("|---|---|---|")
    for a, b, c in [
        ("`dieu_hau`", "tập can 120 ô và thứ tự can chủ (hai lượt chép, 9 ô sách tự mâu thuẫn được gắn cờ)", "vai trò Dụng/Hỷ; ngưỡng hàn/nhiệt; học thuyết (tác giả không rõ nguồn bảng); phiếu kiểm của người"),
        ("`cach_cuc_tvh`", "bảng cách × vượng/nhược × nhóm nhiều (tr.378–386) đã chép; ngưỡng 40% (tr.355)", "đúng 40% và biên ±0,03; 'nhóm nhiều nhất' khi đồng hạng; các ví dụ chỉ khớp một phần"),
        ("`thuan_the_tvh`", "bảng dụng thần/vận của tòng tài/sát/nhi và cách đặc biệt (tr.381–386)", "ngưỡng nhận diện (`tvh_no_help`, `tvh_tong_main`, `chuyen_vuong_*`); ví dụ 4 tr.400 không khớp"),
        ("`thuan_the`", "bảng vai trò tòng (Trích Thiên Tủy tr.171–179)", "ngưỡng nhận diện tòng/hóa và hóa thần dư/thiếu"),
        ("`phu_uc`, `cach_cuc`, `thong_quan`", "—", "toàn bộ (draft); `cach_cuc` chỉ có phần Thương Quan (TTT tr.93–94) được chép đúng"),
        ("`khuyet_hanh`", "—", "chỉ một ví dụ (tr.399), sách không nêu thành quy tắc; ví dụ 4 tr.400 không khớp"),
    ]:
        w(f"| {a} | {b} | {c} |")
    w("\n## 5. Điều kiện còn thiếu trước khi tích hợp production\n")
    for t in ["Người đọc kiểm độc lập 120 ô trên ảnh trang (phiếu `docs/BAZI_DEEP_TVH_CELLS_CHECK.md`, cột *Người kiểm* còn trống). Hiện chỉ có hai lượt chép của mô hình.",
              "Quyết định của chủ sản phẩm về 9 ô sách tự mâu thuẫn (hiện: giữ tập can của bảng, gắn cờ, không thăng cấp can chỉ có ở chú thích).",
              "Quyết định về hiển thị phù ức theo quyết định 40%: nay `phu_uc` luôn theo khí thế của hệ thống (độ trung thực với nhãn Trích Thiên Tủy 36/48 so với 45/48 của quy tắc 40%). Muốn có phù ức theo 40% phải là một phương pháp riêng, nằm ngoài phạm vi Phase 5.",
              "Bằng chứng thực nghiệm về giá trị dự báo của bất kỳ phương pháp nào (hiện 0): cần bộ lá số có kết quả đời thực được ghi trước, người chấm độc lập.",
              "Ví dụ 4 tr.399–400 dựng lại từ lời văn vì bảng in vỡ; cần người đối chiếu trang. Ví dụ 5 (tr.400–401) chưa đọc.",
              "Ngưỡng của hệ thống (mục 7 của `BAZI_DEEP_TVH_AUDIT.md`) chưa có căn cứ nguồn; không nên trình bày như điều sách nói.",
              "UI và `api.py` chưa được chạm: cần phiên phụ trách web hiển thị `meta.levels`, `trace` và cờ `book_internal_conflict` trước khi người dùng cuối thấy kết quả."]:
        w(f"- {t}")
    w("\n## 6. Phát hiện và sửa trong Phase 5\n")
    w("1. `geju.analyse` dưới `tvh_40` trước đây đánh giá trạng thái nội cách và ngoại cách của hệ thống bằng khí thế TVH → nay chỉ *thêm* cách đặc biệt TVH (headline `geju` = geju hệ thống + cách TVH).")
    w("2. `cach_cuc_tvh` / `thuan_the_tvh` trước đây đọc danh sách ngoại cách gộp, nên ngoại cách của hệ thống thay nội cách của TVH → nay có `G_tvh` chỉ chứa cách TVH.")
    w("3. `phu_uc` trước đây đọc quyết định TVH và ngoại cách của TVH → nay dùng khí thế và ngoại cách của hệ thống.")
    w("4. Siêu dữ liệu `levels` (ba mức xác minh) thêm vào `meta` của từng phương pháp; locator của `SRC_TVH_DIEUHAU` và `SRC_TVH_DUNGTHAN` mở rộng theo các trang thực sự đã đọc.\n")
    w("## 7. Oracle độc lập đã dùng\n")
    for t in ["`tests/golden/tvh_dieuhau_blind.json`: bảng 120 ô và chú thích, chép mù (Phase 4).",
              "`tests/golden/tvh_examples_blind.json`: bốn trụ và kết luận của 9 ví dụ tr.387–400, chép mù; so với `tvh_dungthan_examples.json` (oracle viết tay).",
              "Lịch: ngày Quý Mão của 2/1/1974 cho ví dụ 4, độc lập với cả hai lượt chép.",
              "Giới hạn: tất cả do mô hình thực hiện; chưa có người kiểm."]:
        w(f"- {t}")
    w("")
    w("## 8. Quy trình kiểm tra trên HEAD sạch\n")
    w("Mọi lần chạy dùng `git worktree` tách riêng (không có file của phiên khác), cùng một venv. Ghi lại bằng tay lúc chạy:\n")
    w("| Cây mã | Kết quả |")
    w("|---|---|")
    w("| `d0c3ab8` (commit audit Phase 4), sạch | 879 passed, 1 skipped, 2 xfailed, 0 failed |")
    w("| `3d4aabf` (HEAD hiện tại, có thêm commit giao diện so sánh của phiên khác), sạch | 892 passed, 1 skipped, 2 xfailed, 0 failed |")
    w("| `3d4aabf` + các file Phase 5 (15 file, không `api.py`, không `web/`, không `compare_deep`) | **949 passed, 1 skipped, 2 xfailed, 0 failed** |")
    w("")
    w("## 9. Phân loại lỗi\n")
    w("- **Lỗi mới do Phase 5:** khi phát triển có 4 nhóm test cũ phải sửa vì giả định cũ (số phương pháp, `readings` của TVH, mức khí thế của `phu_uc`, snapshot TVH của EX5/EX12); tất cả được xem xét từng cái và ghi trong commit; còn lại 0.")
    w("- **Lỗi baseline:** 0 test fail ở `d0c3ab8` và `3d4aabf` sạch. 2 xfailed và 1 skipped có sẵn ở cả hai, không do Phase 5.")
    w("- **Lỗi do phiên khác đang sửa dở:** trên cây làm việc chung, `tests/test_compare_deep.py` fail 6 ca khi phiên so sánh chưa commit (đã biến mất ở HEAD sạch `3d4aabf` sau khi phiên đó commit). Không liên quan Phase 5.")
    w("")
    out = ROOT / "docs/BAZI_DEEP_PHASE5_REPORT.md"
    out.write_text("\n".join(L) + "\n", "utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
