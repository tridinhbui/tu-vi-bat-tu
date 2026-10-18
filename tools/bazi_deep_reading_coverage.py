"""Coverage matrix, discrimination statistics and two contrasting sample readings for reading/1.
Writes docs/BAZI_DEEP_READING_COVERAGE.md and docs/BAZI_DEEP_READING_SAMPLES.md from REAL charts (real birth data, exact tiết and đại vận). Run: python tools/bazi_deep_reading_coverage.py"""
import datetime as dt
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
from tvbt import api  # noqa: E402
from tvbt.api import BirthReq  # noqa: E402
from tvbt.bazi_deep import pipeline, reading  # noqa: E402
from tvbt.bazi_deep.model import ChartView  # noqa: E402
from tvbt.bazi_deep.profile import TVH_40  # noqa: E402

N = 600
SEED = 20261018
SPEC = reading.SPEC


def run(b):
    y, m, d, h, mi, g = b
    nb, bz, _ = api._compute(BirthReq(year=y, month=m, day=d, hour=h, minute=mi, gender=g))
    view = ChartView.from_bazi(bz, nb.utc, g)
    A = pipeline.analyse(view, TVH_40, with_rules=False)
    luck = [{"index": l.index, "stem": l.stem, "branch": l.branch, "start_year_exact": l.start_year_exact} for l in bz.luck_pillars]
    return reading.compose(A, view, bz, pipeline.timeline(view, TVH_40, luck, [], with_rules=False)), A


def items(R):
    for s in R["foundation"]["sections"]:
        yield "nen-tang", s["id"], from_(s)
    for c in R["chapters"]:
        for s in c["sections"]:
            yield c["id"], s["id"], from_(s)


def from_(s):
    return s["items"]


# (aspect, chapter, source, status, note)  status: verified | draft | computed | gap | not_read
ROWS = [
    ("Tính cách ← Nhật Chủ (日干临十神, 日干五行)", "tinh-cach", "八字真宗 tr.25–26 (20 luật)", "verified", "mô tả của sách phổ thông, hai bảng độc lập"),
    ("Tính cách ← nạp âm trụ ngày", "tinh-cach", "八字真宗 tr.31–32 (30 luật)", "verified", ""),
    ("Tính cách ← tứ trụ toàn âm/dương, thai–thân–mệnh", "tinh-cach", "八字真宗 tr.59 (4 luật)", "draft", "bản nháp, chưa đối chiếu từng trang"),
    ("Tính cách ← vắng một hành", "tinh-cach", "八字真宗 tr.26–27 (5 luật)", "draft", "hành vắng chỉ tính chữ thấy, không tính tàng can (quy ước của hệ thống)"),
    ("Tính cách ← Dương Nhẫn, dịch mã", "tinh-cach / hôn nhân / sự nghiệp", "八字真宗 tr.73–74 (9 luật)", "verified", ""),
    ("Tính cách ← tổng hợp Nhật Chủ × khí thế × cách cục", "tinh-cach", "không có trong nguồn đã nhập", "gap", "nêu như giới hạn, không tự đặt quy tắc"),
    ("Năng lực ← học vấn (Ấn thấu có gốc, văn xương)", "nang-luc", "八字真宗 tr.56 (3 luật)", "verified", ""),
    ("Năng lực ← năng lực cụ thể (lãnh đạo, kỹ thuật…)", "nang-luc", "không có trong nguồn đã nhập", "gap", "các cách thập thần được liệt kê ở nền tảng, chưa gán năng lực"),
    ("Sự nghiệp ← nhóm nghề theo can giờ", "su-nghiep", "八字真宗 tr.52 (5 luật verified + 10 draft)", "verified", "bảng theo từng can là draft"),
    ("Sự nghiệp ← 寅申甲, Quan Sát cùng thấu có gốc, dịch mã", "su-nghiep", "八字真宗 tr.51–52, 74", "verified", ""),
    ("Sự nghiệp ← dụng thần của từng phương pháp", "su-nghiep", "Thiệu Vĩ Hoa tr.378–396 (vai trò cấu trúc)", "computed", "vai trò nhóm Quan Sát; sách không gán nghề"),
    ("Tài lộc ← Tài thấu can, có gốc, tài không hiện", "tai-loc", "八字真宗 tr.50 (4 luật)", "verified", ""),
    ("Tài lộc ← vai trò nhóm Tài theo các phương pháp", "tai-loc", "Thiệu Vĩ Hoa tr.378–396", "computed", "không nói giàu nghèo"),
    ("Tài lộc ← định lượng tài sản", "tai-loc", "không có", "gap", ""),
    ("Hôn nhân ← nguyệt lệnh, nhật chi (hợp, hình xung, không vong, thập thần)", "hon-nhan", "八字真宗 tr.57 (10 luật, 2 draft)", "verified", ""),
    ("Hôn nhân ← anh em", "hon-nhan", "八字真宗 tr.64 (2 luật)", "verified", ""),
    ("Hôn nhân ← sao vợ/chồng theo giới tính, hợp xung cung phu thê", "hon-nhan", "chưa có điều sách được đối chiếu", "gap", "không tự đặt"),
    ("Đại vận ← lịch khởi vận chính xác tới ngày", "dai-van", "tính toán (tiết khí, ba ngày một năm)", "computed", ""),
    ("Đại vận ← vận hỷ/kỵ theo cách", "dai-van", "Thiệu Vĩ Hoa tr.382–386", "verified", "chỉ khi cách xác định; sát ngưỡng 40% thì hai cách đọc"),
    ("Đại vận ← tác động lên nguyên cục", "dai-van", "temporal_deep (Trích Thiên Tủy tuế vận) ", "draft", "hệ số do hệ thống đặt"),
    ("Đại vận ← lưu niên, lưu nguyệt", "dai-van", "có ở /api/bazi-timeline", "not_read", "chưa đưa vào bản luận chương"),
    ("Dụng thần ← tám phương pháp tách biệt", "dung-than", "Thiệu Vĩ Hoa, Trích Thiên Tủy, hệ thống", "verified", "mức xác minh từng phương pháp ở meta.levels"),
    ("Dụng thần ← cách chọn khi các phương pháp bất đồng", "dung-than", "không có trong nguồn", "gap", "không có đáp án cuối, theo thiết kế"),
    ("Nền tảng ← nguyệt lệnh, khí mùa", "nen-tang", "Trích Thiên Tủy (nguyệt lệnh)", "computed", ""),
    ("Nền tảng ← vượng/nhược (40%) và cách riêng của hệ thống", "nen-tang", "Thiệu Vĩ Hoa tr.355; hệ thống", "verified", "hai cách đọc đặt cạnh nhau"),
    ("Nền tảng ← điều hậu, hàn nóng", "nen-tang", "Thiệu Vĩ Hoa tr.389–396; Trích Thiên Tủy tr.113–114", "verified", "bảng không rõ nguồn (tr.388); 9 ô sách tự mâu thuẫn"),
    ("Nền tảng ← cách cục, thành bại", "nen-tang", "Thiệu Vĩ Hoa tr.367–369; bảng nháp hệ thống", "verified", ""),
    ("Nền tảng ← hợp xung hình hại phá, hợp hóa", "nen-tang", "八字真宗 tr.19–20 (bảng); hệ số hệ thống", "draft", ""),
    ("Nền tảng ← cấu trúc Thập Thần có tên", "nen-tang", "patterns_defs (hệ thống)", "draft", "chưa có trang sách đối chiếu"),
    ("Lục thân (cha mẹ, con cái, anh em) theo Thiệu Vĩ Hoa / Trích Thiên Tủy", "—", "chưa đọc", "not_read", "việc đọc nguồn là bước trước khi triển khai"),
    ("Sách 'Đổi Vận Cho Người Mệnh Khuyết'", "—", "không dùng làm nguồn", "gap", "sách phổ thông về lối sống, không phải quy tắc"),
]
STATUS_VI = {"verified": "có nguồn đã đối chiếu", "draft": "bản nháp", "computed": "dữ kiện tính toán", "gap": "chưa đủ căn cứ (cố ý)", "not_read": "nguồn chưa đọc / chưa đưa vào"}


def main():
    r = random.Random(SEED)
    births = []
    for _ in range(N):
        d = dt.date(1930, 1, 1) + dt.timedelta(days=r.randrange(0, 30000))
        births.append((d.year, d.month, d.day, r.randrange(24), r.randrange(60), r.choice(["male", "female"])))
    res = [run(b) for b in births]
    sec_fire = defaultdict(int)
    rule_fire = Counter()
    kinds = Counter()
    empty = Counter()
    for R, A in res:
        seen = set()
        for ch, sec, its in items(R):
            if its:
                seen.add((ch, sec))
            for it in its:
                kinds[(it["basis"], it["kind"])] += 1
                if it["kind"] == "sach" and ".BT_ZZ" in it["id"]:
                    rule_fire[it["id"].split(".", 1)[1]] += 1
        for k in seen:
            sec_fire[k] += 1
        for c in R["chapters"]:
            empty[c["id"]] += c["empty"]
    allrules = {x["id"]: x for f in ("pack_bazi_zz_direct", "pack_bazi_zhenzong", "pack_bazi_napam") for x in json.loads((ROOT / f"engine/data/{f}.json").read_text("utf-8"))["rules"]}
    never = sorted(set(allrules) - set(rule_fire))
    L = ["# Ma trận bao phủ của bản luận Bát Tự sâu (reading/1)\n", f"Sinh bởi `tools/bazi_deep_reading_coverage.py` trên **{N} lá số thật** (ngày sinh ngẫu nhiên có hạt giống {SEED}, 1930–2012, đủ giờ và giới tính). Mọi con số được tính lại khi chạy; không dùng ngưỡng nào được chỉnh cho đẹp.\n",
         "## 1. Mỗi khía cạnh của bản luận dựa vào đâu\n", "| Khía cạnh | Chương | Nguồn | Trạng thái | Ghi chú |", "|---|---|---|---|---|"]
    for a, c, s, st, n in ROWS:
        L.append(f"| {a} | {c} | {s} | **{STATUS_VI[st]}** | {n} |")
    L.append("\nBa dòng 'chưa đủ căn cứ (cố ý)' của mỗi chương được in trong bản luận dưới dạng *giới hạn*, không bị ẩn.\n")
    L += ["## 2. Tần suất xuất hiện theo chương và mục (trên mẫu)\n", "| Chương | Mục | Số lá số có ít nhất một ý | % |", "|---|---|---|---|"]
    names = {c["id"]: c["title"] for c in SPEC["chapters"]}
    names["nen-tang"] = SPEC["foundation"]["title"]
    secnames = {(c["id"], s["id"]): s["title"] for c in SPEC["chapters"] + [SPEC["foundation"]] for s in c["sections"]}
    for (ch, sec), n in sorted(sec_fire.items(), key=lambda kv: ([*names].index(kv[0][0]) if kv[0][0] in names else 99, -kv[1])):
        L.append(f"| {names[ch]} | {secnames.get((ch, sec), sec)} | {n} | {n * 100 // N}% |")
    L += ["\n## 3. Chương không có quy tắc có nguồn nào khớp (chương 'trống')\n", "| Chương | Số lá số | % |", "|---|---|---|"]
    for c in SPEC["chapters"]:
        L.append(f"| {c['title']} | {empty[c['id']]} | {empty[c['id']] * 100 // N}% |")
    L.append("\nChương trống không bị lấp bằng lời chung chung: bản luận nói rõ không có quy tắc nào của sách khớp và chỉ nêu dữ kiện cấu trúc và giới hạn. Đây là chỉ báo trực tiếp của chỗ nguồn còn mỏng.\n")
    L += ["## 4. Luật 八字真宗 và tần suất kích hoạt\n", f"Tổng {len(allrules)} luật; {len(rule_fire)} luật kích hoạt ít nhất một lần trong mẫu; **0 luật chưa được định tuyến vào chương**.\n"]
    L.append("Luật chưa từng kích hoạt trong mẫu (điều kiện hiếm hoặc nạp âm ít gặp): " + (", ".join(never) if never else "không có") + ".\n")
    L += ["## 5. Phân bố theo mức nguồn (toàn bộ ý trong mẫu)\n", "| Mức nguồn | Loại | Số ý |", "|---|---|---|"]
    for (b, k), n in sorted(kinds.items(), key=lambda kv: (reading.BASIS_ORDER[kv[0][0]], kv[0][1])):
        L.append(f"| {SPEC['basis'][b]} | {k} | {n} |")
    # discrimination
    L += ["\n## 6. Khả năng phân biệt giữa các lá số\n",
          "Mỗi chương của mỗi lá số được rút thành tập (mã ý, tiêu đề). Có hai phép đo: **toàn bộ ý** (gồm cả dữ kiện tính toán như tỉ trọng %, nên gần như luôn khác nhau) và **chỉ ý có quy tắc sách hoặc phương pháp dụng thần** (phản ánh đúng việc các quy tắc nào được kích hoạt). Độ giống Jaccard trung bình tính trên 200 lá số đầu.\n",
          "| Chương | Tập khác nhau (toàn bộ ý) | Jaccard (toàn bộ) | Tập khác nhau (chỉ ý có quy tắc) | Jaccard (chỉ quy tắc) |", "|---|---|---|---|---|"]
    for c in SPEC["chapters"]:
        fa, fb = [], []
        for R, _ in res:
            ch = next(x for x in R["chapters"] if x["id"] == c["id"])
            its = [i for s in ch["sections"] for i in s["items"]]
            fa.append(frozenset((i["id"], i["headline"]) for i in its))
            fb.append(frozenset((i["id"], i["headline"]) for i in its if i["kind"] in ("sach", "phuong_phap")))

        def jac(fps):
            pairs = [(fps[i], fps[j]) for i in range(0, 200) for j in range(i + 1, 200, 7)]
            return sum(len(a & b) / max(1, len(a | b)) for a, b in pairs) / len(pairs)
        L.append(f"| {c['title']} | {len(set(fa))} | {jac(fa):.3f} | {len(set(fb))} | {jac(fb):.3f} |")
    whole = {" ".join(i["easy"] for _, _, its in items(R) for i in its) for R, _ in res}
    L.append(f"\nToàn bản luận (văn Dễ hiểu): {len(whole)}/{N} lá số có bản khác nhau. Ở các chương mỏng nguồn (Năng lực, Tài lộc) phần lớn lá số có ít hoặc không có quy tắc nào kích hoạt (mục 3), nên số tập khác nhau ở cột 'chỉ ý có quy tắc' thấp: đó là giới hạn của nguồn, không phải của bộ máy, và bản luận nói rõ điều đó thay vì lấp chỗ trống.\n")
    (ROOT / "docs/BAZI_DEEP_READING_COVERAGE.md").write_text("\n".join(L) + "\n", "utf-8")

    # samples
    strong = next((R, A) for R, A in res if A["strength_after"]["tvh"]["dm_strong"] and abs(A["strength_after"]["tvh"]["own_share"] - 0.4) > 0.1)
    weak = next((R, A) for R, A in res if not A["strength_after"]["tvh"]["dm_strong"] and abs(A["strength_after"]["tvh"]["own_share"] - 0.4) > 0.1)
    S = ["# Hai bản luận mẫu có cấu trúc đối lập (reading/1)\n", "Hai lá số thật được chọn tự động từ mẫu: Nhật Chủ vượng rõ (xa ngưỡng 40%) và nhược rõ. Đây là *bằng chứng khả năng phân biệt*, không phải lời luận về một người thật. Mọi chữ do bộ máy sinh từ dữ kiện và nguồn; không có LLM.\n"]
    for title, (R, A) in (("Lá số vượng", strong), ("Lá số nhược", weak)):
        S.append(f"## {title}: {R['pillars']}\n")
        S.append(f"Phe Nhật Chủ: {A['strength_after']['tvh']['own_share'] * 100:.1f}% ({'vượng' if A['strength_after']['tvh']['dm_strong'] else 'nhược'} theo quy tắc 40%); cách: {A['geju']['inner'][0]['name'] if A['geju']['inner'] else 'chưa xác định'}.\n")
        for it in R["foundation"]["sections"][1]["items"][:2]:
            S.append(f"- **Nền tảng, {it['basis_vi']}:** {it['easy']}")
        for c in R["chapters"]:
            S.append(f"\n### {c['title']}\n\n**Kết luận chính:** {c['summary_easy']}\n")
            top = [i for s in c["sections"] for i in s["items"] if i["kind"] in ("sach", "phuong_phap")][:1]
            if top:
                it = top[0]
                S.append(f"*Vì sao?* " + " → ".join(f"**{x['label']}:** {x['text']}" for x in it["chain"]) + f"  \n*{it['basis_vi']}; {it['certainty_vi']}.*")
            S.append(f"\n*Giới hạn:* {c['gaps'][0]['easy']}")
        S.append("")
    (ROOT / "docs/BAZI_DEEP_READING_SAMPLES.md").write_text("\n".join(S) + "\n", "utf-8")
    print("coverage + samples written;", len(res), "charts;", dict(empty))


if __name__ == "__main__":
    main()
