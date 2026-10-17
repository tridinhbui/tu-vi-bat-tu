"""Phase 7 dossiers.
 1. engine/data/experimental/formation_rule_dossier.json — the 11 rules Phase 6 said need an expert: verbatim passage, page, context before/after (from the PDF text layer when it
    is legible there; otherwise the page image was read directly and the entry says so), the readings that have a textual basis, the measured impact of each reading, a
    classification (nguon_xac_nhan | nguon_mau_thuan | nguon_chua_du) and the decision that stays open. NOTHING is marked verified and no reading is selected.
 2. engine/data/experimental/formation_variant_dossier.json — per variant: school and books, quoted conditions, assumed conditions, level per rule, conflicting variants.
Context strings are stored in the JSON so the tests and the report do not need the PDFs."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent)); sys.path.insert(0, str(ROOT / "engine/tests"))
import book_text as bt  # noqa: E402
import build_formation_audit as au  # noqa: E402

J = lambda p: json.load(open(ROOT / p, encoding="utf-8"))
RD, ST, TH = J("engine/tests/fixtures/readings_sensitivity.json"), J("engine/tests/fixtures/formation_variant_stats.json"), J("engine/tests/fixtures/tu_hoa_sensitivity.json")
VAR, AUD = J("engine/data/experimental/formations_school_variants.json"), J("engine/data/experimental/formation_audit.json")
pct = lambda a, b: round(100 * a / b, 1)


def passage(cid, width=320):
    book, page, quote, how = au.Q[cid]
    ctx = None
    if bt.available(book):
        t = re.sub(r"\s+", " ", bt.page_text(book, page))
        j = t.find(" ".join(quote.split()[:4]))
        if j < 0:
            j = t.lower().find(quote.split()[0].lower())
        if j >= 0:
            ctx = {"truoc": t[max(0, j - width):j].strip(), "sau": t[j + len(quote):j + len(quote) + width].strip()}
    return {"id": cid, "book": bt.BOOK_NAMES[book], "book_code": book, "page": page, "quote": quote, "how": how,
            "context": ctx or "văn bản của trang bị vỡ ở dòng này; đoạn đã được đọc trực tiếp từ ảnh trang, xem câu trích"}


A, B, B2, C = RD["A"], RD["B"], RD["B2"], RD["C"]
nA, nB, nB2, nC = RD["A_core"]["n"], RD["B_core"]["n"], RD["B2_core"]["n"], RD["C_core"]["n"]
D, E = RD["D"], RD["E"]
cn = RD["core_n"]


def dshare(vid, sc):
    return pct(D.get(f"CACH_X_{vid}|{sc}", 0), cn[f"CACH_X_{vid}"])


RULES = [
    dict(id="R01", title="Phạm vi của 'hội / gặp / thích' khi câu sách không nêu phạm vi", priority=1, classification="nguon_chua_du",
         question="Khi sách nói 'hội Tả Hữu', 'thiếu Tả Hữu', 'thích Xương Khúc...', phạm vi là đồng cung, đối cung, tam hợp hay cả tam phương tứ chính?",
         passages=["KL132_TPVT_TAHUU", "KL193_TPVT_XK", "KL85_NLTT", "KL62_KV_XUONGKHUC", "TT24_CNDL_CORE", "TT142_KQL", "KL53_NN_KQL"],
         readings=[dict(id="tp", text="tam phương tứ chính (đồng cung + đối cung + hai tam hợp) — cách đọc đang dùng cho điều kiện không nêu phạm vi", basis=["TT142_KQL", "TT24_CNDL_CORE"], implemented=True),
                   dict(id="hoi_chieu", text="mọi cung chiếu vào Mệnh, không tính chính cung Mệnh", basis=["KL62_KV_XUONGKHUC"], implemented=False),
                   dict(id="doi_cung", text="chỉ đối cung (xung chiếu)", basis=["KL67_XUNGCHIEU"], implemented=False),
                   dict(id="dong_cung", text="chỉ đồng cung", basis=["KL62_KV_XUONGKHUC"], implemented=False),
                   dict(id="tam_hop", text="chỉ hai cung tam hợp", basis=[], implemented=False)],
         evidence_for_distinguishing=("Chính các trang phân biệt đồng cung với chiếu khi cần: KL tr.62 'đồng cung hay hội chiếu', KL tr.66 'đồng cung hoặc chiếu', KL tr.67 'đồng cung hay xung chiếu', "
                                      "TT tr.142 'Chiếu thủ có cả ba Khoa, Quyền, Lộc', TT tr.24 'các cung tam hợp xung chiếu'. Vì vậy một câu chỉ nói 'hội' không tự động là đồng cung; nhưng cũng không có trang nào nói 'hội' = đủ cả tam phương tứ chính."),
         impact={"mo_ta": "tỷ lệ lá số (lõi đúng) đổi trạng thái khi đọc phạm vi khác tam phương",
                 "bang": {v: {sc: dshare(v, sc) for sc in ("hoi_chieu", "doi_cung", "dong_cung", "tam_hop")} for v in
                          ("TU_PHU_VU_TUONG@kl_132_193", "TU_PHU_VU_TUONG@th_115", "CO_NGUYET_DONG_LUONG@kl_221", "NHAT_LE_TRUNG_THIEN@kl_52_85", "SAT_PHA_LIEM_THAM@th_76_77")}},
         current="tam phương (đánh dấu `co_nguon_con_gia_dinh` ở từng quy tắc)", decision="chọn phạm vi cho từng câu 'hội/thích' hoặc giữ nhiều bản đọc song song"),
    dict(id="R02", title="Liệt kê 'Kiếp, Không, Kị' (TT tr.24): một trong ba hay đủ ba", priority=1, classification="nguon_chua_du",
         question="'Gặp Kiếp Không Hoá Kị xuống hạ cách': chỉ cần gặp một sao, một cặp, hay đủ cả ba? Và 'gặp' ở đâu: Mệnh/Thân hay cả tam hợp xung chiếu?",
         passages=["TT24_CNDL_CORE", "TT24_CNDL_BREAK", "TH116_CNDL"],
         readings=[dict(id="mot_trong_ba|tp", text="một trong ba sao, trong tam phương (đang dùng; ngữ cảnh câu: 'Mệnh thân và các cung tam hợp xung chiếu')", basis=["TT24_CNDL_CORE", "TT24_CNDL_BREAK"], implemented=True),
                   dict(id="cap_khong_kiep_hoac_ky|tp", text="cả cặp Không-Kiếp, hoặc Kỵ", basis=["TT24_CNDL_BREAK"], implemented=False),
                   dict(id="tu_hai_trong_ba|tp", text="ít nhất hai trong ba", basis=[], implemented=False),
                   dict(id="du_ca_ba|tp", text="đủ cả ba", basis=["TT24_CNDL_BREAK"], implemented=False),
                   dict(id="mot_trong_ba|dong_cung", text="một trong ba nhưng chỉ ở Mệnh/Thân (đọc 'gặp' hẹp nhất)", basis=[], implemented=False)],
         impact={"mo_ta": f"tỷ lệ phá của Cơ Nguyệt Đồng Lương trên {nA:,} lá số có lõi", "bang": {k: pct(v, nA) for k, v in A.items()}},
         current="một trong ba, tam phương: 82,1% bị phá", decision="đọc câu liệt kê và 'gặp' theo cách nào"),
    dict(id="R03", title="Ngưỡng sát tinh phá cách (≥1 sát tinh; ≥3 sát tinh + Kỵ) và hai breaker phân biệt kém", priority=1, classification="nguon_chua_du",
         question="Sách nói 'nhiều sát tinh' (TH tr.77) và 'bị sát tinh hội chiếu' (KL tr.62) mà không nêu số lượng. Bao nhiêu sát tinh, ở đâu, thì phá cách?",
         passages=["TH77_SPLT_HA", "TH116_SPLT", "KL62_KV_SAT", "KL199_HUNG", "KL85_SO", "KL85_TUAN_CUU"],
         readings=[dict(id="B|tp|sau_sat|>=1", text="≥1 trong sáu sát tinh ở tam phương (đang dùng cho Khôi Việt giáp Mệnh)", basis=["KL62_KV_SAT"], implemented=True),
                   dict(id="B|tp|sau_sat|>=2", text="≥2 sát tinh", basis=[], implemented=False), dict(id="B|tp|tu_sat|>=2", text="≥2 trong Tứ sát", basis=[], implemented=False),
                   dict(id="C|>=3+Ky", text="≥3 sát tinh VÀ Kỵ (đang dùng cho Sát Phá Liêm Tham — quy ước thiết kế)", basis=["TH77_SPLT_HA"], implemented=True)],
         impact={"mo_ta": "KVGM (2.784 lá số có lõi) và SPLT (29.328)",
                 "KVGM": {k: pct(v, nB) for k, v in B.items() if k.startswith(("tp|", "hoi_chieu|", "doi_cung|", "dong_cung|"))},
                 "KVGM_cau_truc_ma_cau_KL_mo_ta": {k: pct(v, nB2) for k, v in B2.items() if k.startswith(("tp|", "dong_cung|"))}, "SPLT": {k: pct(v, nC) for k, v in C.items()}},
         note=("Điều kiện của KL tr.62 mục 4 mô tả 'Cung mệnh CÓ Khôi Việt', không phải Khôi Việt GIÁP Mệnh; cả trên cấu trúc đúng như sách mô tả, 'ít nhất một sát tinh hội chiếu' vẫn đúng "
               "ở 83,1% lá số. Vậy tần suất cao không do việc lấy nhầm cấu trúc mà do ngưỡng 'một'. KL tr.199/85 còn nói Khoa, Tuần Triệt 'làm hung tinh lép vế / cứu giải' cho Thái Dương: sát tinh không luôn phá."),
         current="KVGM: ≥1 sát tinh (91,7% bị phá, cờ `chua_du_nguon`); SPLT: ≥3 sát tinh + Kỵ (quy ước)", decision="ngưỡng và tập sát tinh; có nên để Khoa/Tuần/Triệt làm giảm nhẹ"),
    dict(id="R04", title="'Chiếu' (KL tr.66) = đối cung hay cả tam phương; 'Khôi Việt chiếu' (KL tr.68)", priority=1, classification="nguon_chua_du",
         question="KL tr.66: Kỵ, Kình 'đồng cung hoặc chiếu vào'; KL tr.67 dùng riêng 'xung chiếu'. 'Chiếu' có rộng hơn 'xung chiếu' không?",
         passages=["KL66_TKGH", "KL67_XUNGCHIEU", "KL68_NN_KHOIVIET", "TT142_KQL"],
         readings=[dict(id="J|dong_cung+doi_cung", text="đồng cung hoặc xung chiếu (đối cung) — đang dùng", basis=["KL66_TKGH", "KL67_XUNGCHIEU"], implemented=True),
                   dict(id="J|tp", text="đồng cung hoặc chiếu từ mọi cung trong tam phương", basis=["KL66_TKGH"], implemented=False),
                   dict(id="J|dong_cung", text="chỉ đồng cung", basis=[], implemented=False)],
         impact={"mo_ta": "Tam kỳ gia hội: tỷ lệ bị phá theo cách đọc 'chiếu' (4.048 lá số có lõi)", "bang": {k: pct(v, RD["J_core"]["n"]) for k, v in RD["J"].items()},
                 "Nhat_Nguyet_ham_khong_Khoi_Viet_chieu": {k: pct(v, RD["K_core"]["n"]) for k, v in RD["K"].items()}},
         current="đối cung (28,5% bị phá)", decision="'chiếu' hẹp hay rộng; cùng câu hỏi cho 'Khôi Việt chiếu'"),
    dict(id="R05", title="Nhâm-Khoa: Thiên Phủ (TH) hay Tả Phụ (KL); Canh trong văn bản 全書 số hóa", priority=1, classification="nguon_mau_thuan",
         question="Đây là khác biệt trường phái, lỗi in hay lỗi diễn giải?",
         passages=["KL36_NHAM"],
         extra=[dict(book="TH", page=20, quote="Nhâm : Lương, Tử, Phủ, Vũ tú thị", how="đọc trực tiếp từ ảnh trang TH tr.20: chữ 'Phủ' rõ ràng trong câu thơ"),
                dict(book="TH", page=21, quote="Người sinh năm NHÂM: Lộc an với Thiên Lương, Quyền an với Tử vi, Khoa an với Thiên Phủ, Ky an với Vũ Khúc", how="đọc trực tiếp từ ảnh trang TH tr.21: văn xuôi gọi đích danh 'Thiên Phủ'"),
                dict(book="KL", page=197, quote="Tuổi Nhâm: Lương Vi Phụ Vũ ... Tả phụ, phải khéo léo, chăm chỉ mới có danh", how="đọc trực tiếp từ ảnh trang KL tr.197: bình riêng từng sao, 'Tả phụ' đứng ở vị trí Khoa (danh)"),
                dict(book="zh.wikisource.org (紫微斗數全書, 卷二, 安祿權科忌四星變化訣)", page=None, quote="壬梁紫府武宿是; 庚日武陰同為首", how="văn bản số hóa của một ấn bản, truy cập 2026-10-17 (nguồn NGOÀI ba sách của dự án)"),
                dict(book="zh.wikipedia.org (紫微斗數, 安四化星)", page=None, quote="bảng hai cột 紫微斗數全集 / 紫微斗數全書 khác nhau đúng hai hàng: 庚 và 壬 (左 / 府)", how="nguồn thứ cấp, chỉ dùng để xác nhận rằng hai hàng này vốn có hai biến thể truyền thống")],
         readings=[dict(id="KL", text="Nhâm-Khoa = Tả Phụ (production; Khảo Luận tr.36, tr.197)", basis=["KL36_NHAM"], implemented=True),
                   dict(id="TH", text="Nhâm-Khoa = Thiên Phủ (Thực Hành tr.20-21; trùng với 全書 số hóa)", basis=[], implemented=False),
                   dict(id="TT_WS", text="Thêm: Canh-Khoa Thái Âm, Kỵ Thiên Đồng (全書 số hóa; KL và TH đều ghi Khoa Thiên Đồng, Kỵ Thái Âm)", basis=[], implemented=False)],
         impact={"mo_ta": "trạng thái của 17 biến thể trong 16.704 lá số của hai năm Canh và hai năm Nhâm", "Canh": TH["Canh|TT_WS"]["differ"], "Nham": TH["Nhâm|TH"]["differ"]},
         verdict=("Không phải lỗi in của một chỗ (TH in Thiên Phủ ở cả câu thơ lẫn văn xuôi; trang có các lỗi in khác như 'Khao', 'Vự Môn', nên không thể loại trừ hoàn toàn một lỗi lặp, nhưng lặp ở hai chỗ khác dạng là dấu hiệu của chủ ý) và không phải lỗi diễn giải của dự án: "
                  "một văn bản 全書 số hóa độc lập cũng ghi 府, trong khi KL (và 全集 theo zh.wikipedia) ghi 左輔. Đây là khác biệt giữa hai dòng văn bản truyền thống; chưa có bằng chứng chọn bên nào."),
         current="Khảo Luận (Tả Phụ) làm mặc định; bảng của từng nguồn lưu riêng ở data/experimental/tu_hoa_tables.json; đề xuất tham số `tu_hoa_table` (KL mặc định, TH, TT_WS) hiển thị nhãn nguồn, không đổi âm thầm",
         decision="chọn bảng mặc định và có cho người dùng chọn không"),
    dict(id="R06", title="Độ sáng Thái Dương ở Thân/Mùi", priority=2, classification="nguon_chua_du",
         question="TH tr.31 liệt kê Thái Dương miếu ở Mão; vượng Ngọ, Tỵ, Thìn, Dần; bình Dậu; hãm Tuất, Hợi, Tí, Sửu — thiếu Thân và Mùi. Có được suy ra không?",
         passages=["TH31_SUN", "TH32_MUI_SUU"], readings=[dict(id=f"rank_{r}", text=f"gán Thân/Mùi mức {['hãm', 'bình', 'đắc', 'vượng', 'miếu'][r]}", basis=[], implemented=False) for r in range(5)],
         impact={"mo_ta": "Nhật Nguyệt tịnh minh (KL tr.53/68): lá số có lõi mà Thái Dương nằm ở Thân/Mùi", "so_la_so": RD["G"]["unknown_rank"], "tren": RD["G"]["core"],
                 "trang_thai_theo_muc": {r: {k.split("|")[1]: v for k, v in RD["G"].items() if k.startswith(f"state_if_rank_{r}|")} for r in range(5)}},
         note="TH tr.32 có dòng 'Từ Mùi đến Sửu bần cùng khốn' nằm giữa các câu về Thái Dương, nhưng không nêu mức sáng của Thân/Mùi; không đủ để suy ra.",
         current="để trống (kết quả 'chưa biết', điều kiện không được tính là sai)", decision="tra bảng độ sáng đầy đủ ở nguồn khác hoặc giữ trống"),
    dict(id="R07", title="Tuần/Triệt hai chiều (cứu hung tinh vs làm hại quý tinh vs điều kiện thuận)", priority=1, classification="nguon_mau_thuan",
         question="Tuần/Triệt là phản chứng, sao cứu, hay điều kiện thuận — tùy cách?",
         passages=["KL55_TP_TUAN", "TH94_PHU", "TH95_TUONG", "KL222_VT_TUAN", "KL85_NN_TUAN", "KL85_TUAN_CUU", "KL199_HUNG", "KL200_GIAI", "KL53_NN_TUAN", "KL106_TTAN", "TH43_TTAN"],
         readings=[dict(id="hai", text="làm hại: Tử Phủ, Phủ, Tướng, Vũ Tướng (KL tr.55, 222; TH tr.94-95)", basis=["KL55_TP_TUAN", "TH94_PHU", "TH95_TUONG", "KL222_VT_TUAN"], implemented=True),
                   dict(id="cuu", text="cứu: Thái Dương hãm, sát tinh gặp Thái Dương, 'hung tinh chịu lép vế' (KL tr.85, 199-200)", basis=["KL85_NN_TUAN", "KL85_TUAN_CUU", "KL199_HUNG", "KL200_GIAI"], implemented=False),
                   dict(id="thuan", text="điều kiện thuận: Nhật Nguyệt Sửu Mùi cần Tuần (KL tr.53); Cự Môn Tý Ngọ gặp Tuần/Triệt là kỳ cách (KL tr.106, TH tr.43)", basis=["KL53_NN_TUAN", "KL106_TTAN", "TH43_TTAN"], implemented=True)],
         impact={"mo_ta": "Tuần/Triệt đóng ở Mệnh khi lõi đúng", "Tu_Phu_Vu_Tuong": pct(RD["F_ref_active"]["CACH_X_TU_PHU_VU_TUONG@kl_132_193"], cn["CACH_X_TU_PHU_VU_TUONG@kl_132_193"]),
                 "Nhat_Nguyet": pct(RD["F_ref_active"]["CACH_X_NHAT_NGUYET_TINH_MINH@kl_53_68"], cn["CACH_X_NHAT_NGUYET_TINH_MINH@kl_53_68"]), "Thach_trung_an_ngoc": RD["F_ttan"]},
         current="hại ở Tử Phủ Vũ Tướng / Tử Phủ đồng cung; thuận trong lõi Thạch trung ẩn ngọc (KL106); không dùng ở Nhật Nguyệt; sao cứu chưa mô hình hóa",
         decision="Tuần/Triệt có thể đồng thời hại và cứu trong một lá số: cần quy tắc ưu tiên của chuyên gia"),
    dict(id="R08", title="Ba định nghĩa Thạch trung ẩn ngọc; hai kết cục Mã đầu đới kiếm; TT tr.142 coi Kình ở Ngọ là xấu", priority=2, classification="nguon_mau_thuan",
         question="Các định nghĩa có thật sự mâu thuẫn hay chỉ mô tả các tập khác nhau?",
         passages=["KL44_TTAN", "KL58_TTAN", "KL106_TTAN", "TH43_TTAN", "KL64_MDDK_XAU", "KL64_MDDK_TOT", "TT142_MDDK"],
         readings=[dict(id="kl44", text="Cự Môn ở Mệnh, Thiên Cơ ở Di, Tý/Ngọ", basis=["KL44_TTAN"], implemented=True), dict(id="kl58", text="Cự Môn Tý/Ngọ có Khoa Quyền Lộc tam hợp chiếu", basis=["KL58_TTAN"], implemented=True),
                   dict(id="kl106", text="Cự Môn Tý/Ngọ gặp Tuần/Triệt (hoặc Hóa Lộc)", basis=["KL106_TTAN", "TH43_TTAN"], implemented=True),
                   dict(id="kl64_xau", text="Kình ở Ngọ + Thất Sát + Thiên Hình đồng cung: xấu", basis=["KL64_MDDK_XAU"], implemented=True), dict(id="kl64_tot", text="Kình đồng cung, xa Thất Sát/Thiên Hình, gặp Khoa Quyền Lộc: tốt", basis=["KL64_MDDK_TOT"], implemented=True),
                   dict(id="tt142", text="Kình gặp Thiên Mã, tốt ở tứ mộ, xấu ở Ngọ", basis=["TT142_MDDK"], implemented=False)],
         impact={"mo_ta": "quy mô từng định nghĩa (lá số)", "Thach_trung": {"kl44": ST["states"]["CACH_X_THACH_TRUNG_AN_NGOC@kl_44"]["hinh_thuc"], "kl106": ST["states"]["CACH_X_THACH_TRUNG_AN_NGOC@kl_106"]["hinh_thuc"], "kl58": ST["states"]["CACH_X_THACH_TRUNG_AN_NGOC@kl_58"]["hinh_thuc"]},
                 "Ma_dau": {"kl_kinh_o_ngo_trong_menh": RD["H"]["kl_kinh_o_ngo_trong_menh"], "tt_kinh_cung_thien_ma_trong_menh": RD["H"]["tt_kinh_cung_thien_ma_trong_menh"]}},
         verdict=("Thạch trung ẩn ngọc: ba định nghĩa chọn ba tập lá số khác nhau (1.728 / 696 / 32 lá số) và sách không gắn kết luận tốt/xấu khác nhau cho chúng, nên chúng khác nhau về TÊN CÁCH chứ chưa mâu thuẫn về hệ quả. "
                  "Trong mô hình này Cự Môn ở Tý/Ngọ luôn có Thiên Cơ ở đối cung nên vế sau của KL tr.44 tự động đúng. Mã đầu đới kiếm: KL gắn tên cách với Kình ở Ngọ; TT tr.142 gắn với Kình gặp Thiên Mã. "
                  "Trong mô hình, Kình (Mão Thìn Ngọ Mùi Dậu Tuất Tý Sửu) và Thiên Mã (Dần Thân Tỵ Hợi) không bao giờ đồng cung, nên bản TT chỉ có nghĩa nếu 'gặp' rộng hơn đồng cung."),
         current="ba biến thể Thạch trung, hai biến thể Mã đầu; TT tr.142 chưa mô hình hóa", decision="định nghĩa nào là 'cách' của trường phái nào"),
    dict(id="R09", title="Tử Phủ đồng cung: TH tr.72 'Mệnh hay Thân' và TT tr.22 'Tỵ Hợi'; mệnh đề 'Giáp nhân'", priority=2, classification="nguon_mau_thuan",
         question="Neo ở Mệnh hay Thân? 'Tỵ Hợi' có phải Tử Phủ không? Câu 'vô sát tấu' chỉ áp cho tuổi Giáp?",
         passages=["TH72_TPDC", "TT22_TPDC_SAT", "TT22_TPDC_TYHOI", "TT22_GIAP", "TT22_TV_PHUBAT", "KL50_TUSAT_TYHOI", "KL68_NN_KHOIVIET"],
         readings=[dict(id="menh", text="chỉ neo ở Mệnh (đang dùng)", basis=["KL68_NN_KHOIVIET"], implemented=True), dict(id="menh_hay_than", text="Mệnh hoặc Thân (TH tr.72)", basis=["TH72_TPDC"], implemented=False),
                   dict(id="tt22_ty_hoi", text="TT tr.22 'Tử Phủ đồng cung lâm Tị Hợi' đọc là chép nhầm của 'Tử Sát đồng lâm Tỵ Hợi' (KL tr.50 mục 13, cùng vế sau 'nhất triều phú quí song toàn')", basis=["TT22_TPDC_TYHOI", "KL50_TUSAT_TYHOI"], implemented=False),
                   dict(id="giap_nhan", text="'vô sát tấu' chỉ cho tuổi Giáp (TT tr.22)", basis=["TT22_GIAP"], implemented=False)],
         impact={"mo_ta": "lá số", **{k: v for k, v in RD["I"].items()}},
         verdict=("Trong mô hình Tử Vi và Thiên Phủ không bao giờ cùng cung ở Tỵ/Hợi (0 lá số) nhưng Tử Vi và Thất Sát cùng cung ở Tỵ/Hợi (1.584 lá số có Mệnh ở đó); câu của TT trùng gần như nguyên văn với KL tr.50 mục 13 về Tử Sát. "
                  "Đây là bằng chứng văn bản gián tiếp cho nghi ngờ chép nhầm, KHÔNG phải kết luận."),
         current="chỉ Mệnh; câu 'Giáp nhân' và 'toàn y phụ bật' chưa mô hình hóa", decision="có thêm neo Thân; có tách mệnh đề tuổi Giáp"),
    dict(id="R10", title="Trang TH tr.72 và tr.74 (lớp chữ vỡ)", priority=2, classification="nguon_xac_nhan",
         question="Các câu trích phụ thuộc vào ảnh trang có đọc rõ không?",
         passages=["TH72_TPDC", "TH72_TPVT", "TH72_NNTM", "TH72_NLTT", "TH72_SPLT", "TH72_TAMHOA", "TH74_NN_TAN_HUNG", "TH74_TAMHOA"],
         readings=[], impact={"mo_ta": "cả hai trang đã được đọc trực tiếp từ ảnh ở độ phân giải 1.6x; mọi câu hiện được dùng đều đọc rõ"},
         verdict=("Đã xác nhận bằng ảnh: TH tr.72 mục 1, 4, 7, 12, 21, 22 và TH tr.74 mục 7 ('Nhật, Nguyệt tàn hung ... hãm tại Mệnh mà không có cứu tinh, hoặc hãm mà gặp sát tinh') cùng đoạn 'cứu giải bằng Tam hóa hội' "
                  "(chỉ cho Mệnh ở Bại/Tuyệt địa). TH tr.72 mục 12 là 'Tam Hoá liên châu' (ba cung liền), khác Tam kỳ gia hội. Câu trích của ảnh được ghi nguyên văn kể cả lỗi in ('hên châu', 'Khao'). "
                  "Quy tắc dựa vào câu chỉ có trong ảnh không bao giờ được xếp `doi_chieu_truc_tiep`."),
         current="TH tr.72/tr.74: `anh_doc_ro` hoặc `van_ban`; không còn trang `chua_du_nguon` vì chữ", decision="không còn"),
    dict(id="R11", title="Cơ chế: 2 yếu tố tăng thế = thành thượng; phản chứng hạ một bậc; không cộng điểm", priority=3, classification="nguon_chua_du",
         question="Có trang nào định nghĩa ngưỡng hay mức hạ?", passages=[],
         readings=[dict(id=f"thuong{t}|drop{d}", text=f"thành thượng từ {t} yếu tố; phản chứng hạ {d} bậc", basis=[], implemented=(t, d) == (2, 1)) for t in (1, 2, 3) for d in (0, 1, 2)],
         impact={"mo_ta": "tỷ lệ lá số (lõi đúng) đổi trạng thái khi đổi cơ chế", "bang": {v: {k.split("|", 1)[1]: pct(x, cn[f"CACH_X_{v}"]) for k, x in E.items() if k.startswith(f"CACH_X_{v}|") and x} for v in
                                                                                  ("TU_PHU_VU_TUONG@kl_132_193", "TU_PHU_VU_TUONG@th_115", "CO_NGUYET_DONG_LUONG@kl_221", "NHAT_LE_TRUNG_THIEN@kl_52_85", "SAT_PHA_LIEM_THAM@th_76_77")}},
         verdict="Không trang nào của ba sách nêu số yếu tố hay số bậc; TH tr.76-77 chỉ phân hạng (phi thường / thượng / trung / hạ) bằng 'hội cát tinh đủ bậc'. Đây là quy ước thiết kế và được hiển thị như vậy.",
         current="2 yếu tố, hạ một bậc, không cộng điểm", decision="giữ như quy ước hiển thị hay thay bằng phân hạng theo TH tr.76-77"),
]


def build_rules():
    out = []
    for r in RULES:
        r = dict(r)
        r["passages"] = [passage(c) for c in r.get("passages", [])]
        for rd in r["readings"]:
            rd["basis"] = [passage(c, 0) | {"context": None} for c in rd["basis"]]
        r.setdefault("extra", []); r.setdefault("verdict", ""); r.setdefault("note", "")
        r["trang_thai"] = "mo (cần chuyên gia)" if r["id"] != "R10" else "dong (đã đọc ảnh)"
        out.append(r)
    return out


def build_variants():
    rows = {(r["formation"], r["role"], r["id"]): r for r in AUD["rows"]}
    out = []
    for f in VAR["formations"]:
        m = VAR["meta"][f["id"]]
        base = m["base"]
        rules = []
        for key, lv in m["rules"].items():
            d = m["rule_detail"][key]
            role, cid = ("core", "core") if key == "core" else key.split(".", 1)
            ev = None
            if role != "core":
                ev = next((e for e in f[role] if e["id"] == cid), None)
            rules.append({"key": key, "label": ev["label"] if ev else "điều kiện lõi", "level": lv, "audit_status": d["audit_status"], "assumption": d["assumption"],
                          "cites": [passage(c) for c in d["cites"]], "dung_nguyen_van": lv == "doi_chieu_truc_tiep"})
        peers = [pid for pid in VAR["meta"] if VAR["meta"][pid]["base"] == base and pid != f["id"]]
        conflicts = []
        for pid in peers:
            k1, k2 = f"{f['id']}|{pid}", f"{pid}|{f['id']}"
            st_ = ST["pairs"].get(k1) or ST["pairs"].get(k2)
            conflicts.append({"variant": pid, "school": VAR["meta"][pid]["school_vi"], "title": VAR["meta"][pid]["title"],
                              "khac_nhau": (st_ or {}).get("differ"), "ca_hai_hien": (st_ or {}).get("both_fire")})
        states = ST["states"][f["id"]]
        out.append({"id": f["id"], "base": base, "school": m["school_vi"], "title": m["title"], "books": sorted({f"{c['book_code']} tr.{c['page']}" for c in m["cites"]}),
                    "rules": rules, "assumptions": [r["assumption"] for r in rules if r["assumption"]],
                    "quy_uoc_thiet_ke": [r["key"] for r in rules if r["level"] == "chua_du_nguon" and r["audit_status"] in ("chat_hon", "long_hon", "khop", "lien_quan") and "quy ước" in (r["assumption"] or "")],
                    "conflicting_variants": conflicts, "note": f["note"], "rescuers": "không có (không nguồn nào nói sao nào cứu cách nào)",
                    "kich_hoat_pct": round(100 * sum(q for s, q in states.items() if s != "khong_hien") / ST["charts"], 2), "reviewer": m["reviewer"], "verified": False})
    return out


if __name__ == "__main__":
    rules = build_rules()
    (ROOT / "engine/data/experimental/formation_rule_dossier.json").write_text(json.dumps({"version": 1, "note": "11 quy tắc cần chuyên gia: không quy tắc nào được đóng dấu verified; không cách đọc nào được chọn.", "rules": rules}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    vs = build_variants()
    (ROOT / "engine/data/experimental/formation_variant_dossier.json").write_text(json.dumps({"version": 1, "note": "Hồ sơ học thuật từng biến thể: trường phái, nguồn, điều kiện trích trực tiếp, điều kiện còn giả định, mức xác minh từng quy tắc, các trường phái đưa kết luận khác.", "variants": vs}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(len(rules), "rules;", len(vs), "variants")
