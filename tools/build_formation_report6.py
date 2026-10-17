"""docs/PHASE6_INDEPENDENT_VALIDATION.md — pure formatting of pinned data (audit, variants, proposals, scans, control set). No judgement lives here."""
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine/tests"))
import control_charts_phase6 as C  # noqa: E402

J = lambda p: json.load(open(ROOT / p, encoding="utf-8"))
AUD, VAR = J("engine/data/experimental/formation_audit.json"), J("engine/data/experimental/formations_school_variants.json")
PRO, ORC, ST = J("engine/data/experimental/formation_proposals.json"), J("engine/tests/fixtures/formation_oracle_full.json"), J("engine/tests/fixtures/formation_variant_stats.json")
META = VAR["meta"]
N = ST["charts"]
LV = {"doi_chieu_truc_tiep": "đối chiếu trực tiếp", "co_nguon_con_gia_dinh": "có nguồn còn giả định", "chua_du_nguon": "chưa đủ nguồn"}
REL = {"chua": "không triển khai (chưa đủ căn cứ)", "bo": "bỏ khỏi biến thể", "mo_rong": "mở rộng phạm vi", "thu_hep": "thu hẹp", "thay_the": "thay bằng điều kiện của sách", "giu": "giữ, khai báo cách đọc"}
VERD = {"khop": "khớp", "khong_khop": "KHÔNG khớp", "khong_quyet_dinh": "không quyết định", "sach_khong_xet": "sách không xét"}
SAYS = {"xac_nhan": "sách xác nhận", "phu_dinh": "sách phủ định", "khong_ket_luan": "sách không kết luận"}
short = lambda s: s.replace("CACH_X_", "")
fire = lambda v: sum(q for s, q in v.items() if s != "khong_hien")
REGRESSION = J("docs/phase6_regression.json") if (ROOT / "docs/phase6_regression.json").exists() else {}


def main():
    L = ["# Phase 6 — Kiểm chứng độc lập và chuẩn hoá 17 biến thể cách cục Tử Vi (bản nháp)", "",
         "Sinh bởi `tools/build_formation_report6.py` từ dữ liệu đã ghim (audit, biến thể, đề xuất, quét 116.928 lá số, bộ lá số đối chứng). Mọi cách cục và biến thể vẫn `draft`, chỉ hiện ở `?thu-nghiem`; "
         "**không dùng `verified`** vì chưa có thẩm định độc lập của chuyên gia. Định nghĩa gốc `formations_experimental.json` (của phiên khác) không bị sửa.", "",
         "## 1. Chốt provenance (đếm lại sau khi thêm cờ giả định từng quy tắc)", ""]
    c = collections.Counter(x for m in META.values() for x in m["rules"].values())
    L += [f"Tổng **{sum(c.values())}** quy tắc trong 17 biến thể: **{c['doi_chieu_truc_tiep']}** `doi_chieu_truc_tiep`, **{c['co_nguon_con_gia_dinh']}** `co_nguon_con_gia_dinh`, **{c['chua_du_nguon']}** `chua_du_nguon`. "
          "Con số 15 xuất hiện trong tin nhắn bàn giao Phase 5 (đếm trước khi thêm cờ giả định) không khớp file đã commit, vốn ghi 8 `doi_chieu_truc_tiep`; cả hai **đã bị thay thế** bởi số trên, tính theo từng quy tắc "
          "sau khi cờ giả định được gắn cho từng quy tắc và một trích dẫn sai chủ đề của audit (KL tr.221, Cơ Nguyệt Đồng Lương) được sửa.", "",
          "- `doi_chieu_truc_tiep`: mọi trích dẫn của quy tắc được máy so với văn bản trang, câu sách đã xác định phạm vi, không có giả định của mô hình.",
          "- `co_nguon_con_gia_dinh`: có trang sách nói đúng chủ đề nhưng còn giả định (phạm vi, ngưỡng, tập sao, một-trong-các-sao).",
          "- `chua_du_nguon`: trang chỉ đọc được từ ảnh, hoặc là quy ước thiết kế (3 trong 4 sao; 3 sát tinh + Kỵ), hoặc quy tắc gốc chỉ 'liên quan'.", "",
          "| Biến thể | Sách · trang | đối chiếu trực tiếp | có nguồn còn giả định | chưa đủ nguồn |", "|---|---|---|---|---|"]
    for vid, m in META.items():
        cc = collections.Counter(m["rules"].values())
        pages = ", ".join(sorted({f"{x['book_code']} tr.{x['page']}" for x in m["cites"]}))
        L.append(f"| `{short(vid)}` | {pages} | {cc['doi_chieu_truc_tiep']} | {cc['co_nguon_con_gia_dinh']} | {cc['chua_du_nguon']} |")
    L += ["", "Ghi chú về cơ chế (áp cho mọi biến thể, không phải kết luận cổ thư): thang `hình thức → thành → thành thượng` (thành thượng = từ 2 yếu tố tăng thế), mỗi phản chứng hạ một bậc, "
          "không cộng điểm, breaker không được cứu thì `bị phá`. Biến thể không có sao cứu.", "",
          "### Sửa audit trong Phase 6", "",
          "Một test mới (`test_every_cited_quote_speaks_about_the_condition_it_supports`) kiểm từng câu trích có nói đến chủ thể của điều kiện. Nó phát hiện: (1) audit gắn câu về Sát Phá Tham (KL tr.221) cho điều kiện của Cơ Nguyệt Đồng Lương — "
          "đã thay bằng hai câu đúng chủ đề; (2) hai điều kiện Kỵ của Nhật Nguyệt/Nhật lệ trung thiên trích câu về Tuần/Triệt thay vì câu 'Thái dương ghét ... Kỵ' (KL tr.85); (3) ba điều kiện cát tinh của Sát Phá Liêm Tham trích sai câu (TH tr.76). "
          "Các số trang của lá số đối chứng cũng được sửa (Hạng Võ tr.238, Khổng Minh tr.240, Nữ Quý Mão tr.244, Mậu Tý tr.245–246; trước đó ghi tr.239/241/243). Phép kiểm này chỉ là kiểm từ khoá, KHÔNG chứng minh ý nghĩa câu trích.", "",
          "## 2. Hai mươi lăm đề xuất sửa, từng đề xuất", "",
          "Quan hệ: *mở rộng* = điều kiện mới đúng ở mọi nơi điều kiện gốc đúng; *thu hẹp* = ngược lại; *thay bằng* = không chứa nhau. Số liệu trước/sau tính trên mẫu "
          f"{PRO['sample_charts']:,} lá số, chỉ ở những lá số mà lõi baseline đúng.", "",
          "| # | Cách · điều kiện gốc | Nguồn · trang · trích | Cách hiểu mới | Giả định | Biến thể | Xử lý | Trước → sau (gốc đúng / mới đúng / chỉ gốc / chỉ mới) | Regression |", "|---|---|---|---|---|---|---|---|---|"]
    for p in PRO["proposals"]:
        cite = "<br>".join(f"{x['book_code']} tr.{x['page']}: “{x['quote']}”" for x in p["cites"])
        b = p["before_after"]
        ba = f"{b['base_true']} / {b['var_true']} / {b['base_only']} / {b['var_only']} (trên {b['n_base_core']})" if b else "—"
        why = f" — {p['not_implemented_reason']}" if p["not_implemented_reason"] else ""
        L.append(f"| {p['id']} | {p['name_vi']} · `{p['condition']}` | {cite} | {p['new_reading']} | {p['assumption'] or '—'} | {', '.join(v.split('@')[1] for v in p['variants']) or '—'} | {REL[p['relation']]}{why} | {ba} | `{p['regression_test'].split('/')[-1]}` |")
    rc = collections.Counter(p["relation"] for p in PRO["proposals"])
    L += ["", f"Tổng: {rc['mo_rong']} mở rộng, {rc['thu_hep']} thu hẹp, {rc['thay_the']} thay bằng, {rc['giu']} giữ, **{rc['bo']} bỏ** (chủ yếu sao cứu), **{rc['chua']} không triển khai** vì sách dùng 'gặp' trong ngữ cảnh chưa xác định phạm vi.", "",
          "## 3. Oracle độc lập", "",
          "`engine/tests/oracle_tuvi_independent.py` **không import `tvbt`**. Nó tự an: Mệnh/Thân, cục (Ngũ Hổ Độn + nạp âm), Tử Vi, Thiên Phủ và hai hệ chính tinh, Tả/Hữu, Xương/Khúc, Khôi/Việt (TH tr.19), Lộc Tồn/Kình/Đà (TH tr.21), "
          "Địa Không/Địa Kiếp, Hỏa/Linh, Thiên Hình, Lực Sĩ, Tứ Hóa (TH tr.20–21, KL tr.36, tr.196–197), Triệt (TH tr.20), Tuần (giáp tuần), độ sáng Thái Dương (TH tr.31) và Thái Âm (TH tr.39); "
          "rồi tự hiện thực 17 biến thể từ nhãn tiếng Việt của từng điều kiện (không từ DSL) với logic ba giá trị.", "",
          f"- **So sánh toàn bộ {ORC['charts']:,} lá số** (mười năm liên tiếp × mọi ngày âm × 12 giờ × 2 giới + 4 năm Mậu): số sai khác = **{sum(ORC['mismatches'].values())}** trên Mệnh/Thân/cục, vị trí mọi sao, Tứ Hóa, Tuần/Triệt và trạng thái của cả 17 biến thể.",
          "- **Oracle tự tái hiện các lá số in trong sách** (5 lá số của phiên khác + Hàn Tín) về chính tinh từng cung, phụ tinh đọc được và Tứ Hóa — mà không dùng bất cứ hàm sản xuất nào.",
          "- **Kiểm đột biến**: 4 đột biến có chủ đích trong sản xuất (đổi phạm vi tam phương → đồng cung, đối cung → giáp cung, Tuần sai cung, hội chiếu → giáp) đều bị oracle phát hiện; so sánh không rỗng.",
          "- Test không phải xác nhận vòng tròn: oracle không đọc `tuvi.py`, `positions.py`, bảng độ sáng JSON hay DSL.", "",
          "**Giới hạn của oracle (không che giấu):**", "",
          "1. Ngày dương lịch ↔ âm lịch vẫn do `lunar_input` sản xuất cung cấp; oracle nhận ngày âm. Lịch pháp không được kiểm chứng ở đây.",
          "2. Công thức Địa Không/Kiếp, Hỏa/Linh (điểm khởi + chiều), Thiên Hình, Lực Sĩ được gõ theo quy tắc chuẩn, **không** theo một trang sách tôi đã đọc; chỉ được xác nhận gián tiếp qua các lá số in trong sách (Địa Không/Kiếp, Hỏa/Linh, Thiên Hình, Lộc Tồn).",
          "3. Độ sáng Thái Dương tại Thân/Mùi không in trong dòng TH tr.31 mà lớp chữ còn đọc được → để trống (kết quả 'chưa biết'), không đoán; nếu sách đầy đủ có giá trị thì kết quả Nhật Nguyệt tịnh minh có thể đổi.",
          "4. Hai bảng độ sáng cùng trang với bảng của sản xuất (TH tr.31, tr.39); sự độc lập nằm ở việc gõ lại từ văn bản trang, không ở chọn nguồn khác.",
          "5. **Bất đồng trường phái ảnh hưởng đến cả hai phía**: TH tr.21 in Nhâm-Khoa = Thiên Phủ, KL tr.197 in Tả Phụ; sản xuất và oracle đều theo KL. Dưới cách đọc của TH mọi lá số năm Nhâm có sao Khoa khác, nên Tam Hóa/Tam kỳ gia hội của các năm đó cũng khác. "
          "Ghi chú 'agree on all ten stems' trong `tuvi.py` không đúng cho Nhâm. Cần chuyên gia quyết định, tôi không chọn.", "",
          "## 4. Xung đột trường phái (giữ nguyên, không hợp nhất)", "",
          "| Cách | Các biến thể giữ riêng | Mức bất đồng đo được trên các lá số mà cả hai cùng hiện |", "|---|---|---|"]
    for k, v in ST["pairs"].items():
        a, z = k.split("|")
        L.append(f"| {short(a).split('@')[0]} | `{short(a).split('@')[1]}` vs `{short(z).split('@')[1]}` | {v['differ']:,}/{v['both_fire']:,} ({100 * v['differ'] / v['both_fire']:.1f}%) |")
    L += ["", "- **Cơ Nguyệt Đồng Lương**: TT tr.24 (Kiếp, Không, Kị trong tam hợp xung chiếu thì hạ cách) và KL tr.221 (không nêu yếu tố phá) khác nhau ở 97,7% lá số cả hai cùng nhận. Đây là bất đồng thật giữa hai sách, không phải lỗi mô hình.",
          "- **Tử Phủ đồng cung**: TT tr.22 coi sát tinh làm hỏng; KL tr.50 coi Kình Dương, Kỵ + Quyền đồng cung là tốt. Khác nhau đúng ở 658 lá số có sát tinh đồng cung.",
          "- **Thạch trung ẩn ngọc**: ba định nghĩa mô tả ba tập lá số khác nhau (KL tr.44: 1.728; KL tr.106/TH tr.43: 696; KL tr.58: chỉ 32). Chúng không mâu thuẫn trên phần giao vì không có yếu tố tăng thế/phá để so.",
          "- **Mã đầu đới kiếm**: hai kết cục trái nhau của cùng KL tr.64; chỉ khác ở 94 lá số vì điều kiện Thất Sát + Thiên Hình đồng cung hiếm.",
          "- **Tuần/Triệt hai chiều** được giữ hai hướng ở các biến thể khác nhau (hại ở Tử Phủ Vũ Tướng, Tử Phủ đồng cung; thuận ở Thạch trung ẩn ngọc; không là phản chứng ở Nhật Nguyệt).",
          "- Không có tổng kết 'trường phái nào đúng hơn'; không biến thể nào được ưu tiên.", "",
          "## 5. Lá số đối chứng mở rộng (KL tr.237–247)", "",
          "Sáu lá số có đủ ngày giờ sinh in trong sách (thêm Hàn Tín so với Phase 5), mười hàng cách. Ba loại nhận xét của sách được tách: *xác nhận*, *phủ định*, *không kết luận*; "
          "và tách theo mức bằng chứng: **ten** = nhận xét nêu đích danh các sao của cách; **tong_the** = sách chỉ nhận xét chung về lá số. Hàng 'không quyết định' là trạng thái trung tính (hình thức).", "",
          "| Lá số · trang | Cách | Sách | Căn cứ | Trích | Gốc | Biến thể → trạng thái (kết quả) |", "|---|---|---|---|---|---|---|"]
    cnt = collections.Counter()
    for chart, fid, says, (bk, pg, q), bst, vst, basis in C.ROWS:
        vtxt = "; ".join(f"`{k[1:]}` → {s} ({VERD[C.verdict(says, s)]})" for k, s in vst.items())
        L.append(f"| {C.CHARTS[chart]['label']} tr.{C.CHARTS[chart]['page']} | {short(fid)} | {SAYS[says]} | {basis} | {bk} tr.{pg}: “{q}” | {bst} ({VERD[C.verdict(says, bst)]}) | {vtxt} |")
        cnt[(basis, "gốc", C.verdict(says, bst))] += 1
        for s in vst.values():
            cnt[(basis, "biến thể", C.verdict(says, s))] += 1
    L += ["", "Tóm tắt (đếm theo hàng gốc / theo từng biến thể):", "", "| Căn cứ | Phiên bản | khớp | KHÔNG khớp | sách không xét |", "|---|---|---|---|---|"]
    for basis in ("ten", "tong_the"):
        for ver in ("gốc", "biến thể"):
            L.append(f"| {basis} | {ver} | {cnt[(basis, ver, 'khop')]} | {cnt[(basis, ver, 'khong_khop')]} | {cnt[(basis, ver, 'sach_khong_xet')]} |")
    L += ["", "Hai điểm không khớp còn lại trong nhóm 'ten' đều là bản KL tr.221 của Cơ Nguyệt Đồng Lương, bản không có breaker (Hạng Võ: thành; Mậu Tý: thành thượng) — đúng là bất đồng giữa KL và TT. "
          "Các biến thể được viết từ trang sách trước khi so với các lá số này; không điều kiện nào được chỉnh để ép khớp. Mẫu rất nhỏ (6 lá số), nên không dùng để suy ra độ chính xác. "
          "Hàng 'tong_the' là bằng chứng yếu hơn vì sách không nêu đích danh cách.", "",
          f"## 6. Độ nhạy trên {N:,} lá số", "",
          "Tỷ lệ kích hoạt = lõi đúng / tổng. Tỷ lệ bị phá = `bị phá` / lõi đúng. Cột cuối: so với baseline.", "",
          "| Biến thể | Kích hoạt | Bị phá | Trạng thái hiện (lá số) | Chỉ baseline hiện | Khác baseline (cả hai hiện) |", "|---|---|---|---|---|---|"]
    for k, v in ST["states"].items():
        if "@" not in k or not fire(v):
            continue
        bb = ST["vs_baseline"][k]
        states = ", ".join(f"{s} {q:,}" for s, q in v.items() if s != "khong_hien")
        bp = v.get("bi_pha", 0) / fire(v)
        flag = " ⚠ phân biệt kém" if bp > 0.5 else (" (0 do thiết kế: không breaker)" if bp == 0 and not next(f for f in VAR["formations"] if f["id"] == k)["breakers"] else "")
        L.append(f"| `{short(k)}` | {100 * fire(v) / N:.2f}% | {100 * bp:.1f}%{flag} | {states} | {bb['baseline_only']:,} | {bb['differ']:,}/{bb['both_fire']:,} |")
    L += ["", "Phát hiện:", "",
          "- Chín biến thể không có breaker nên tỷ lệ bị phá 0% là hệ quả thiết kế (sách không nêu phạm vi phá đủ rõ), **không phải** bằng chứng cách đó bền.",
          "- Hai breaker **phân biệt kém**: Cơ Nguyệt Đồng Lương theo TT tr.24 (82,1% bị phá) và Khôi Việt giáp Mệnh theo KL tr.62 (91,7%), vì 'có ít nhất một sát tinh/Không-Kiếp/Kỵ trong tam phương' hầu như luôn đúng. "
          "Ngưỡng 'một' là cách đọc của tôi; sách nói 'bị sát tinh hội chiếu' mà không nêu số lượng. Cần chuyên gia quyết định.",
          "- Không biến thể nào đạt `bị phá nhưng được cứu` (không có sao cứu). Không biến thể nào hiện khi lõi baseline vắng.",
          "- Điều kiện không thể xảy ra trong mô hình (giữ nguyên, đã có test): Thiên Tướng hãm (TPVT), Thái Dương hãm ở Ngọ (NLTT), Cự Môn hãm ở Tý/Ngọ (TTAN), Tam Hóa hội cứu của Tử Phủ đồng cung; "
          "và Tử Phủ đồng cung × phá được cứu bất khả thi theo hình học của mô hình (`test_formation_geometry.py`) — đó là giới hạn của cách an sao và bảng Tứ Hóa đang dùng, không phải kết luận theo mọi trường phái.", "",
          "## 7. Kiểm tra tích hợp", "",
          "- `formations_experimental.json` giữ 10 cách, `definition_version` 2, không id chứa `@`. API `/api/formations` mặc định trả đúng 10 id baseline; `analyse()` chỉ chạy biến thể khi được truyền rõ ràng.",
          "- Không file giao diện hay module sản xuất nào tham chiếu `formations_school_variants`; luận giải chính không chứa id cách cục thử nghiệm. Không thay đổi UI hay API.", "",
          "## 8. Regression", ""]
    if REGRESSION:
        L += [f"- Worktree sạch của HEAD `{REGRESSION['head']}`: **{REGRESSION['summary']}**.", f"- Ghi chú: {REGRESSION['note']}"]
    else:
        L += ["- (chưa chạy)"]
    L += ["", "## 9. Quy tắc cần chuyên gia xác nhận", "",
          "1. Phạm vi của 'hội/gặp' khi câu sách không nêu (Tả Hữu, Xương Khúc, Lộc, Khoa Quyền Lộc, sát tinh): baseline đọc là tam phương.",
          "2. Liệt kê 'Kiếp, Không, Kị' (TT tr.24): một trong số đó là đủ hay phải đủ cả ba.",
          "3. Ngưỡng của sát tinh phá (≥1 sát tinh, '≥3 sát tinh + Kỵ'), và hai breaker phân biệt kém ở mục 6.",
          "4. 'Chiếu' (KL tr.66) = đối cung hay cả tam phương; 'Khôi Việt chiếu' (KL tr.68).",
          "5. Nhâm-Khoa là Tả Phụ (KL) hay Thiên Phủ (TH); Canh-Tân Khôi Việt (Ngọ, Dần) theo TH tr.19 nhưng lớp chữ trang đó bị vỡ, nguồn ghi trong `tuvi.py`.",
          "6. Độ sáng Thái Dương ở Thân/Mùi (dòng TH tr.31 bị cắt).",
          "7. Tuần/Triệt vừa cứu hung tinh vừa hại quý tinh: chọn theo cách cụ thể nào.",
          "8. Ba định nghĩa Thạch trung ẩn ngọc; hai kết cục của Mã đầu đới kiếm; TT tr.142 coi Kình ở Ngọ là xấu và chỉ tốt ở tứ mộ.",
          "9. TT tr.22 nhắc Tử Phủ đồng cung ở Tỵ/Hợi (mô hình chỉ có Dần/Thân) và TH tr.72 cho phép đóng ở Mệnh hay Thân.",
          "10. Trang TH tr.72, tr.74 chỉ đọc được từ ảnh: cần người đối chiếu trực tiếp sách giấy.",
          "11. Ngưỡng cơ chế: 2 yếu tố tăng thế → thành thượng; phản chứng hạ một bậc; không cộng điểm."]
    (ROOT / "docs/PHASE6_INDEPENDENT_VALIDATION.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
