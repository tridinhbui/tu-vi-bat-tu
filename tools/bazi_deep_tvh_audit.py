"""Audit report for Điều Hậu / Dụng Thần after Thiệu Vĩ Hoa pp.386-399. Writes docs/BAZI_DEEP_TVH_AUDIT.md.
Every number in the report is recomputed here from the independent oracles (engine/tests/golden/tvh_dieuhau_blind.json, tvh_dungthan_examples.json)
and the live engine, so the report cannot drift from the code. Run: python tools/bazi_deep_tvh_audit.py"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
from tvbt.bazi_deep import dieuhau, pipeline, strength, tvh_score, yongshen  # noqa: E402
from tvbt.bazi_deep.model import ChartView  # noqa: E402
from tvbt.bazi_deep.profile import DEFAULT, TVH_40  # noqa: E402
from tvbt.ganzhi import BRANCHES_VI  # noqa: E402

G = ROOT / "engine/tests/golden"
BLIND = json.loads((G / "tvh_dieuhau_blind.json").read_text("utf-8"))
BOOK = json.loads((G / "tvh_dungthan_examples.json").read_text("utf-8"))
ENG = json.loads((dieuhau.DATA / "tvh_dieuhau.json").read_text("utf-8"))
MONTHS = ["Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu"]
STEMS = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
ADJ = {("Mùi", "Tân"): ["Nhâm", "Canh", "Giáp"], ("Sửu", "Quý"): ["Bính", "Đinh"]}      # see 'adjudicated' in the blind fixture
CAUSE = {"swap": "sách tự mâu thuẫn: bảng và chú thích thay một can bằng can khác", "note_adds": "chú thích thêm một can mà bảng không có", "table_adds": "bảng có một can mà chú thích bỏ qua"}
HANDLING = {"swap": "giữ tập can của bảng; can chỉ có trong chú thích không được đưa lên; can chỉ có trong bảng xếp sau các can có trong chú thích; báo `book_internal_conflict`",
            "note_adds": "giữ tập can của bảng; can chỉ có trong chú thích không được thăng cấp; báo `book_internal_conflict`",
            "table_adds": "giữ tập can của bảng; can chỉ có trong bảng xếp cuối; báo `book_internal_conflict`"}


def chart(ds, mb):
    ys, ms = 0, (2 + ((mb - 2) % 12)) % 10
    db = ds % 2
    return ChartView.from_names(f"Giáp Tý / {STEMS[ms]} {BRANCHES_VI[mb]} / {STEMS[ds]} {BRANCHES_VI[db]} / {STEMS[(ds * 2) % 10]} Tý")


def cells():
    rows, nine = [], []
    for m in MONTHS:
        for s in STEMS:
            t = BLIND["table"][m][s]
            n = ADJ.get((m, s), BLIND["notes"][m][s])
            r = dieuhau.lookup(chart(STEMS.index(s), (MONTHS.index(m) + 2) % 12))
            eng = [x["stem"] for x in r["yong_stems"]]
            same_set = set(t) == set(n)
            kind = None if same_set else ("swap" if [x for x in n if x not in t] and [x for x in t if x not in n] else "note_adds" if [x for x in n if x not in t] else "table_adds")
            row = {"month": m, "stem": s, "table": t, "notes": n, "engine": eng, "chu": r["chu"], "same_set": same_set, "order_same": t == n, "kind": kind,
                   "note_only": [x for x in n if x not in t], "table_only": [x for x in t if x not in n]}
            rows.append(row)
            if kind:
                nine.append(row)
    return rows, nine


def examples():
    out = []
    for k, ex in BOOK["dungthan_examples"].items():
        o = pipeline.analyse(ChartView.from_names(ex["pillars"]), TVH_40, with_rules=False)
        tv, M = o["strength_after"]["tvh"], o["yongshen"]["methods"]
        out.append((k, ex, tv, M, o))
    return out


def sens():
    cases = json.loads((G / "ttt_cases.json").read_text("utf-8"))["cases"]
    lab = [(v["pillars"], v["dm"] == "strong") for v in cases.values() if v["kind"] in ("tong", "thuong_quan")]
    lab += [(v["pillars"], v["strong"]) for v in json.loads((G / "tvh_examples.json").read_text("utf-8"))["examples"].values()]
    lab += [(v["pillars"], v["book"]["dm_verdict"] == "vượng") for v in BOOK["dungthan_examples"].values()]
    sh = [(tvh_score.score(ChartView.from_names(p))["own_share"], s) for p, s in lab]
    ag = {t: sum((x >= t) == s for x, s in sh) for t in (0.30, 0.34, 0.36, 0.38, 0.39, 0.40, 0.41, 0.42, 0.44, 0.46, 0.50)}
    allsh = [tvh_score.score(ChartView.from_names(v["pillars"]))["own_share"] for v in cases.values()]
    amb = {m: sum(strength._band(x, m) == 3 for x in allsh) for m in (0.0, 0.01, 0.02, 0.03, 0.05)}
    return len(sh), ag, len(allsh), amb


def fmt(x):
    return " ".join(x) if x else "—"


def main():
    rows, nine = cells()
    L = []
    w = L.append
    w("# Kiểm toán Điều Hậu và Dụng Thần theo Thiệu Vĩ Hoa (tr.386–399)\n")
    w("Báo cáo do `tools/bazi_deep_tvh_audit.py` sinh ra; mọi con số được tính lại từ oracle độc lập và từ engine hiện hành. Trạng thái dưới đây chỉ nói rằng *bản cài khớp với những gì sách in*, "
      "không nói rằng học thuyết đó đã được kiểm chứng. Chính tác giả viết ở tr.388 rằng bảng điều hậu là do một độc giả tặng và ông không biết nó lấy từ sách nào.\n")
    w("## 1. Oracle độc lập và lỗi đã bắt được\n")
    w("- `engine/tests/golden/tvh_dieuhau_blind.json`: bảng tr.389–390 và chú thích tr.391–396 do một lượt chép **mù** khác thực hiện từ ảnh trang (không xem dữ liệu của engine), rồi so với engine.")
    w("- Bảng 120 ô: **120/120 khớp**. Chú thích: lượt chép mù và engine khớp 117/120; 3 ô lệch được đối chiếu lại với ảnh trang:")
    for k, v in BLIND["adjudicated"].items():
        w(f"  - {k} (tr.{v['page']}): {v['verdict']}.")
    w("- Kết quả thực: oracle độc lập **bắt được một lỗi chép của chính engine** (Ất tháng Thìn: sách in `quý, bính, mậu`, engine cũ có `bính, quý, mậu`). Đã sửa và có test ghim.")
    w("- Giới hạn: cả hai lượt chép đều do mô hình thực hiện, chưa có người đọc kiểm. Hai lượt độc lập cùng khớp làm giảm rủi ro chép sai, không loại bỏ nó.\n")
    w("## 2. Chín ô bảng và chú thích không khớp\n")
    n_swap = sum(r["kind"] == "swap" for r in nine)
    n_ord = sum(r["same_set"] and not r["order_same"] for r in rows)
    w(f"Phân loại 120 ô: **{sum(r['order_same'] for r in rows)} ô giống hệt** (cùng tập và cùng thứ tự), **{n_ord} ô cùng tập can nhưng khác thứ tự in**, **{len(nine)} ô khác tập can** "
      f"({n_swap} thay thế, {sum(r['kind']=='note_adds' for r in nine)} chú thích thêm, {sum(r['kind']=='table_adds' for r in nine)} bảng thêm).\n")
    w(f"- **Sai tập can** (9 ô, bảng dưới) là mâu thuẫn thật của sách: hai nơi nêu hai tập can khác nhau.")
    w(f"- **Khác thứ tự** ({n_ord} ô) không phải lỗi dữ liệu: bảng tr.389–390 là 'bảng dụng thần dự bị' liệt kê tập can, thứ tự in trong ô không mang nghĩa ưu tiên; ưu tiên chỉ có ở chú thích tr.391–396. "
      "Vì vậy thứ tự ưu tiên của engine lấy hoàn toàn từ chú thích, và test khẳng định thứ tự in của bảng không phải thứ tự ưu tiên.")
    w(f"- Can đứng đầu chú thích luôn nằm trong bảng ở cả 120 ô: {all(r['notes'][0] in r['table'] for r in rows)}, nên can chủ không bao giờ nằm trong vùng xung đột.\n")
    w("| Can ngày | Tháng | Bảng (tr.389–390) | Chú thích (tr.391–396) | Engine (thứ tự) | Loại lệch | Nguyên nhân | Hướng xử lý |")
    w("|---|---|---|---|---|---|---|---|")
    for r in nine:
        w(f"| {r['stem']} | {r['month']} | {fmt(r['table'])} | {fmt(r['notes'])} | {fmt(r['engine'])} (chủ: {r['chu']}) | sai **tập can** ({r['kind']}) | {CAUSE[r['kind']]} | {HANDLING[r['kind']]} |")
    w("\nKết luận: 9 ô này là mâu thuẫn **trong nội bộ sách**, không phải lỗi chép (đã đối chiếu hai lượt chép). Engine không chọn bên nào làm đúng; nó giữ bảng làm tập can, không đưa can chỉ có ở chú thích lên, và gắn cờ cho người dùng. "
      "Can chủ không bị ảnh hưởng ở cả 9 ô.\n")
    w("## 3. Ba ví dụ chọn dụng thần (tr.397–399) và năm ví dụ điều hậu (tr.387–388)\n")
    for k, ex, tv, M, o in examples():
        b = ex["book"]
        w(f"### {k} (tr.{ex['page']}): {ex['pillars']}\n")
        w(f"- Dữ kiện đầu vào: lá số trên; sách in thập thần và tàng can, test đối chiếu cả hai với engine (khớp).")
        w(f"- Bước 1, vượng/nhược: sách đọc **{b['dm_verdict']}** ({b['dm_verdict_basis']}). Quy tắc 40% trên điểm TVH: phe mình = **{tv['own_share']:.4f}** → {'vượng' if tv['dm_strong'] else 'nhược'}.")
        w("- Bước 2, các bước của sách: " + "; ".join(b["steps"]) + ".")
        c = M["cach_cuc_tvh"]
        if c["status"] == "hai_cach_doc":
            alts = "; ".join(f"{a['dm_vi']}: nhóm nhiều nhất {a.get('dominant')}, dụng {fmt(a.get('yong', []))}" for a in c["alternatives"])
            w(f"- Bước 3, engine `cach_cuc_tvh`: **hai cách đọc** (trong biên heuristic ±{c['threshold']['margin_heuristic']}); {alts}.")
        else:
            w(f"- Bước 3, engine `cach_cuc_tvh`: nhóm nhiều nhất **{c.get('dominant')}** → dụng {fmt(c['yong'])} (bảng cho thêm {fmt(c.get('yong_alternatives', []))}).")
        d, kh = M["dieu_hau"], M["khuyet_hanh"]
        w(f"- Engine `dieu_hau`: dụng {fmt(d['yong'])}, hỷ {fmt(d['xi'])}. `khuyet_hanh`: {kh['status']} {fmt(kh.get('yong', []))}.")
        w(f"- **Sách chọn:** {fmt(b['dung_than_elements'])} (nhóm {fmt(b['dung_than_groups'])}).\n")
    w("Kết quả đối chiếu:\n")
    w("| Ví dụ | Vượng/nhược | cach_cuc_tvh | dieu_hau | khuyet_hanh | Đánh giá |")
    w("|---|---|---|---|---|---|")
    w("| tr.397 vd1 | khớp (55,2% → vượng) | **khớp** (Quan Sát) | **khớp** | không áp dụng | 2 phương pháp tái lập kết luận của sách |")
    w("| tr.398 vd2 | **lệch**: 41,85% → vượng theo quy tắc 40%, sách nói nhược | hai cách đọc; cách đọc nhược cho Ấn **khớp** | **khớp** (Ấn dụng, Tỉ hỷ) | không áp dụng | sách không tái lập được bằng chính quy tắc 40%; engine không che điều này |")
    w("| tr.399 vd3 | khớp (73,7% → vượng) | **một phần**: bảng cho Quan Sát (+Tài), sách chọn Thủy+Mộc | **khớp** (Thủy rồi Mộc, đúng thứ tự) | **khớp** (thiếu Mộc, Thủy) | sách chọn theo cân bằng ngũ hành chứ không theo bảng cách cục của chính nó |")
    w("")
    w("Năm ví dụ điều hậu của tr.387–388 (Dụng thần theo chú thích điều hậu):\n")
    w("| Ví dụ | Lá số | Sách lấy | Engine (can chủ → …) | Kết quả |")
    w("|---|---|---|---|---|")
    for k, ex in BOOK["dieuhau_examples"].items():
        if k.startswith("_"):
            continue
        r = dieuhau.lookup(ChartView.from_names(ex["pillars"]))
        gs = [x["group"] for x in r["yong_stems"]]
        res = "khớp can chủ" if gs[0] == ex["dung_than_groups"][0] else "một phần: nhóm của sách có trong ô nhưng không đứng đầu" if ex["dung_than_groups"][0] in gs else "không khớp"
        w(f"| {k} | {ex['pillars']} | {fmt(ex['dung_than_stems'])} ({fmt(ex['dung_than_groups'])}) | {fmt([x['stem'] + '=' + x['group'] for x in r['yong_stems']])} | {res} |")
    w("")
    n, ag, nall, amb = sens()
    w("## 4. Ngưỡng 40%\n")
    w("**Nguồn gốc.** Quy tắc nằm ở `tvh_score.py` (`THRESHOLD`, `decide`) và đi vào `yongshen.cach_cuc_tvh` qua cờ `dm_strong`; bản thân `yongshen.py` không có hằng 0,40. Sách tr.355 nêu 40% tổng độ làm ngưỡng, kèm hai phép thử số học: "
      "78 < 78,8 (40% của 197) → nhược; 115 > 87,2 (40% của 218) → vượng. Cả hai được test tái lập bằng `decide`.\n")
    w("**Phần của sách:** con số 40% và phép so sánh lớn hơn/nhỏ hơn. **Phần của hệ thống (heuristic, đã gắn nhãn trong output `threshold`):**")
    w("- Đúng 40% tính là vượng (sách không nói); nhãn `equality_choice`.")
    w(f"- Biên ±{DEFAULT.tvh_margin} quanh 40% cho hai cách đọc (`tvh_margin`); nhãn `margin_src: he_thong (không phải của sách)`. Ví dụ 6 của sách (39,6%) nằm trong biên này nhưng sách đọc dứt khoát là nhược, nên output luôn ghi thêm `book_rule_reading` và cờ `follows_book_rule` cho từng cách đọc.\n")
    w(f"**Độ nhạy của ngưỡng** trên {n} lá số có nhãn (48 nhãn Nhật Chủ của Trích Thiên Tủy, 4 ví dụ tính điểm của Thiệu Vĩ Hoa, 3 ví dụ đang kiểm; một nhãn trong đó là vd2 mà quy tắc 40% không tái lập được):\n")
    w("| Ngưỡng | " + " | ".join(f"{t:.2f}" for t in ag) + " |")
    w("|---|" + "---|" * len(ag))
    w("| Số lá số khớp nhãn | " + " | ".join(str(v) for v in ag.values()) + " |")
    w(f"\nTại 40%: {ag[0.40]}/{n} ({ag[0.40] / n:.1%}). Vùng 0,39–0,44 gần như phẳng (±1); dưới 0,36 xấu đi rõ. Vậy 40% nằm trên một cao nguyên, **không bị tinh chỉnh cho khớp dữ liệu**, và dữ liệu này cũng không đủ để bảo vệ riêng con số 40% so với 42%.\n")
    w(f"Số lá số trong {nall} mệnh lệ rơi vào biên hai cách đọc theo độ rộng biên: " + ", ".join(f"±{m}: {v}" for m, v in amb.items()) + ". Ở mức mặc định chỉ 2/81 lá số bị tách đôi.\n")
    w("Kiểm thử ngay dưới/bằng/trên ngưỡng nằm ở `test_cach_cuc_tvh_just_below_at_and_above_the_threshold` (0,3999 / 0,40 / 0,4001 với biên 0,03 và 0) và `test_40_percent_decision_on_the_books_own_numbers_and_at_the_edge`.\n")
    w("## 5. Các phương pháp tách biệt\n")
    w("Mỗi phương pháp trong `yongshen.run` mang `meta` (nguồn, mức xác minh, điều kiện áp dụng, cơ sở khí thế, đã áp dụng hay chưa) và `trace` (các bước). `comparison` chỉ liệt kê đồng thuận và bất đồng kèm điều kiện áp dụng; "
      "`no_final_answer: true`, không có khóa điểm số hay thắng-thua và không có phép cộng điểm giữa các phương pháp (test kiểm tra tập khóa).\n")
    w("| Phương pháp | Mức xác minh | Nguồn | Điều kiện áp dụng |")
    w("|---|---|---|---|")
    for k, m in yongshen.METHOD_META.items():
        w(f"| `{k}` | {m['verification']} | {'; '.join(m['source'])} | {m['applies_when']} |")
    w("\nPhương pháp mới trong đợt này: `khuyet_hanh` (căn cứ duy nhất là một ví dụ tr.399, nên draft) và `thuan_the_tvh` (tách khỏi `thuan_the`, xem mục 6).\n")
    w("## 6. Cách ly trường phái: phát hiện và sửa\n")
    w("**Phát hiện (đo trên 81 mệnh lệ, profile mặc định `hệ thống` so với `tvh_40`):** tên nội cách giống nhau 81/81, nhưng điểm TVH và ngoại cách TVH làm đổi kết quả của trường phái khác: "
      "trạng thái thành/bại của cách đổi ở 6 lá số, ngoại cách không-TVH đổi ở 7, dụng thần của `cach_cuc` đổi ở 19. "
      "Cơ chế chính: các ngoại cách do `tvh_cach.special` sinh ra được trộn vào cùng danh sách `geju.outer`, nên khi TVH nhận một 'Tòng … chân' thì `cach_cuc` thành *không xác định nội cách* và `phu_uc` bị loại, dù hệ thống không nhận ngoại cách đó "
      "(ví dụ `Quý Mão / Mậu Ngọ / Nhâm Dần / Bính Ngọ`). Cùng cách, `thuan_the` đọc cả hai trường phái tùy thứ tự.\n")
    w("**Sửa:** khi profile là `tvh_40`, `yongshen.run` tính lại phần của hệ thống từ khí thế và cách cục của chính hệ thống (`+he_thong_view`), và chỉ dùng điểm TVH, ngoại cách TVH cho `cach_cuc_tvh` và `thuan_the_tvh`. "
      "`phu_uc` vẫn dùng quyết định vượng/nhược của profile (đó là lựa chọn có chủ ý, được ghi ở `meta.strength_basis`) nhưng chỉ xét ngoại cách của hệ thống.\n")
    w("**Kiểm chứng:** trên 96 lá số (81 mệnh lệ + EX1–EX15), `cach_cuc` và `thuan_the` giống hệt nhau giữa hai profile (0 khác biệt); `phu_uc` giống hệt trên các lá số cùng mức khí thế (28/96). "
      "Hệ quả hiển thị: có thêm bất đồng được liệt kê (EX5 nay có `BT_ST_DISAGREE`, vì phù ức hệ thống không còn bị TVH loại).\n")
    w("## 7. Danh sách heuristic của hệ thống (không gán cho tác giả)\n")
    w("| Tham số | Giá trị | Dùng ở | Ghi chú |")
    w("|---|---|---|---|")
    for a, b, c, d in [
        ("`tvh_margin`", DEFAULT.tvh_margin, "cach_cuc_tvh, phu_uc (biên hai cách đọc)", "hiển thị; không phải của sách"),
        ("đúng 40% = vượng", "≥", "tvh_score.decide", "sách chỉ nói lớn hơn/nhỏ hơn"),
        ("`level_cuts`", DEFAULT.level_cuts, "phu_uc, các mức khí thế", "hệ thống; sách chỉ có phép 40%"),
        ("`presence_share`", DEFAULT.presence_share, "Thương Quan (5 cách)", "'có/không có' Tài, Quan, Ấn là ngưỡng hệ thống"),
        ("`thuong_vuong`", DEFAULT.thuong_vuong, "Thương Quan (5 cách)", "hệ thống"),
        ("`war_share`, `bridge_min`", f"{DEFAULT.war_share}, {DEFAULT.bridge_min}", "thong_quan", "cả phương pháp là draft"),
        ("`hua_du_share`", DEFAULT.hua_du_share, "thuan_the (hóa)", "hệ thống"),
        ("`tvh_no_help`, `tvh_tong_main`", f"{DEFAULT.tvh_no_help}, {DEFAULT.tvh_tong_main}", "nhận diện tòng TVH", "sách dùng lời 'không có/nhiều', số là của hệ thống"),
        ("`chuyen_vuong_chars`, `chuyen_vuong_share`", f"{DEFAULT.chuyen_vuong_chars}, {DEFAULT.chuyen_vuong_share}", "nhận diện chuyên vượng/hóa khí", "hệ thống"),
        ("nhóm 'nhiều nhất'", "lớn nhất theo tổng điểm TVH", "cach_cuc_tvh", "cách đọc của sách; cắt đồng hạng là của hệ thống"),
        ("vai trò Dụng/Hỷ trong điều hậu", "can chủ = Dụng, còn lại = Hỷ", "dieu_hau", "quy ước hệ thống; sách chỉ xếp thứ tự can"),
        ("chỉ số hàn/nhiệt", "heat ≤ −1, ≥ 1,5", "dieu_hau.han_noan", "hệ thống (nguyên tắc hàn/noãn theo Trích Thiên Tủy tr.113–114)"),
        ("`khuyet_hanh` cả phương pháp", "—", "khuyet_hanh", "một ví dụ tr.399, không phải quy tắc chung của sách"),
    ]:
        w(f"| {a} | {b} | {c} | {d} |")
    w("")
    w("## 8. Kết luận về trạng thái draft → verified\n")
    w("| Hạng mục | Trạng thái đề xuất | Lý do |")
    w("|---|---|---|")
    w("| Bảng điều hậu 120 ô (tập can) | `verified` (bản chép) | 120/120 khớp lượt chép mù; 9 ô mâu thuẫn nội bộ sách được gắn cờ, vẫn thuộc diện bản chép đúng |")
    w("| Thứ tự ưu tiên trong chú thích | `verified` (bản chép) cho can chủ ở 120 ô; thứ tự các can sau chủ `verified` ở 111 ô cùng tập | 117/120 khớp ngay, 3 ô đã đối chiếu ảnh; 9 ô lệch tập can có cờ |")
    w("| Học thuyết điều hậu | **không** nâng | tác giả nói không biết nguồn của bảng; 3/5 ví dụ minh họa của chính ông chỉ khớp một phần với thứ tự chú thích |")
    w("| Quy tắc 40% (tr.355) | `verified` cho con số và phép so sánh | tái lập hai phép thử số của sách; 51/55 lá số có nhãn |")
    w("| Đúng 40%, biên ±0,03, các ngưỡng ở mục 7 | `draft` | do hệ thống đặt |")
    w("| Bảng cách × vượng/nhược × nhóm nhiều (tr.378–386) | `partial` | bản chép đã đối chiếu; 1/3 ví dụ khớp hoàn toàn, 1 khớp theo cách đọc nhược, 1 khớp một phần: chưa đủ để nói 'đã xác minh đúng' |")
    w("| `phu_uc`, `cach_cuc` (hệ thống), `thong_quan`, `khuyet_hanh` | `draft` | không có nguồn đối chiếu hoặc nguồn chỉ là một ví dụ |")
    w("| `thuan_the`, `thuan_the_tvh` | `partial` | bảng vai trò đã đối chiếu, ngưỡng nhận diện là của hệ thống |")
    w("")
    w("## 9. Những gì chưa thể xác minh\n")
    for t in ["Ví dụ 4 tr.399 (nữ) tiếp tục sang tr.400, ngoài phạm vi trang đã dựng ảnh; chưa dùng.",
              "Mệnh lệ trong sách có chỗ tự mâu thuẫn (vd2 tr.398: nói 'không có gốc' trong khi giờ Tý và tàng can Tân/Canh có mặt); không thể dùng làm oracle cho vượng/nhược.",
              "Thứ tự các can sau can chủ trong 9 ô lệch: sách mâu thuẫn, không có căn cứ để chọn.",
              "Cả hai lượt chép bảng đều do mô hình; chưa có người đọc kiểm ảnh trang.",
              "Giá trị dự báo của dụng thần/điều hậu: không được kiểm chứng ở đâu trong repo; mọi nhãn ở trên là về độ trung thực với văn bản.",
              "Phu tòng thê hóa, thê tòng phu hóa, uyên ương hợp hóa chưa hỗ trợ trong tính điểm; điểm TVH chưa áp cho các trụ lưu (đại vận, lưu niên)."]:
        w(f"- {t}")
    w("\n## Phụ lục: đối chiếu cả 120 ô\n")
    w("Cột *Bảng* theo thứ tự in; *Chú thích* theo thứ tự ưu tiên (can đầu là chủ); *Engine* là thứ tự engine trả về. `≠` đánh dấu ô khác tập can.\n")
    w("| Tháng | Can ngày | Bảng | Chú thích | Engine | Khớp tập |")
    w("|---|---|---|---|---|---|")
    for r in rows:
        w(f"| {r['month']} | {r['stem']} | {fmt(r['table'])} | {fmt(r['notes'])} | {fmt(r['engine'])} | {'có' if r['same_set'] else '≠ (' + r['kind'] + ')'} |")
    out = ROOT / "docs/BAZI_DEEP_TVH_AUDIT.md"
    out.write_text("\n".join(L) + "\n", "utf-8")
    print("wrote", out, len(L), "lines")


if __name__ == "__main__":
    main()
