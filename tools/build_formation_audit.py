"""Phase 2 scholarly audit of the 93 conditions of the 10 draft Tử Vi formations.

Unlike build_formation_provenance.py (which maps conditions to the page-cited rules already in the packs), every row here was
written after READING THE BOOK PAGES themselves (Khảo Luận = KL, Thực Hành = TH, Toàn Thư = TT; see tools/book_text.py).
Each citation carries a short quote; when the books are on disk the quote is checked against the decoded text layer of the cited
printed page (`quote_check = "van_ban"`), otherwise it is recorded as read from the page image (`"anh"`) or unchecked (`"chua_kiem"`).

Output: engine/data/experimental/formation_audit.json and docs/PHASE4_KIEM_TOAN_NGUON.md.
Nothing here edits a formation or marks anything verified; this layer only describes how the DRAFT relates to the books.

Alignment vocabulary (same as the provenance layer): khop | long_hon | chat_hon | khac | lien_quan | khong_co_nguon
Action vocabulary:
  giu_co_nguon       keep: a book states it in this role (still draft; page text not independently reviewed by a scholar)
  de_xuat_sua        books say something narrower/wider: change proposed to the definition owner, not applied here
  giu_gia_thuyet     no book basis in this role: keep only as a labelled design hypothesis, outside the "sourced" definition
  quy_uoc_thiet_ke   a threshold/convention of the design (shown as such, never as a classical conclusion)
  khong_the_xay_ra   condition can never fire in the model (see reach analysis): kept for completeness, explained in the report
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import book_text as bt  # noqa: E402

DEFS = ROOT / "engine" / "data" / "experimental" / "formations_experimental.json"
REACH = ROOT / "engine" / "tests" / "fixtures" / "formation_reach.json"
OUT_JSON = ROOT / "engine" / "data" / "experimental" / "formation_audit.json"
OUT_MD = ROOT / "docs" / "PHASE4_KIEM_TOAN_NGUON.md"

# --- citations: id -> (book, printed page, short quote, how it was read) ------------------------------------------------------
# method: "van_ban" = text layer (machine-checkable), "anh" = read from the page image (text layer garbled)
Q = {
 "TH72_TPDC": ("TH", 72, "Tử, Phủ đồng cung cáh (đóng ở Mệnh hay Thân)", "van_ban"),
 "TH72_TPVT": ("TH", 72, "Tử, Phủ, Vũ, Tướng cách", "van_ban"),
 "TH72_NNTM": ("TH", 72, "Nhật, Nguyệt tinh minh cách (Nhật ở Thìn, Tỵ, Nguyệt ở Dậu, Tuất, mà Mệnh đóng ở Nguyệt hay Nhật đều tốt)", "van_ban"),
 "TH72_NLTT": ("TH", 72, "Nhật lệ trung thiên cách ( Nhật cư Ngọ có Mệnh)", "van_ban"),
 "TH72_TAMHOA": ("TH", 72, "Tam Hóa liên châu: Khoa, Quyền, Lộc đi liền 3 cung đến Mệnh có 1 hóa", "anh"),
 "TH72_SPLT": ("TH", 72, "Sát, Phá, Liêm, Tham (mục 4 trong các quý cách lập thành ở 12 cung)", "anh"),
 "TH74_TAMHOA": ("TH", 74, "cần được cứu giải băng Tam hóa hội", "van_ban"),
 "TH74_NN_TAN_HUNG": ("TH", 74, "Nhật, Nguyệt hãm tại Mệnh không có cứu tinh, hoặc hãm mà gặp sát tinh (bần tiện cách số 7)", "anh"),
 "TH76_CATTINH": ("TH", 76, "Hồng Đào, Khoa Quyền. Lộc, Kình, Không", "van_ban"),
 "TH77_CNDL": ("TH", 77, "Nguyệt Đồng Lương hội Tả Hữu, Thai Cáo, Xương Khúc tất là hàng công chức", "van_ban"),
 "TH77_SPLT_HA": ("TH", 77, "Sát Phá Liêm Tham hội Vũ, Kình Đà", "van_ban"),
 "TH94_PHU": ("TH", 94, "Nhưng nếu Phủ gặp Tuần Triệt hay Thiên, Địa Không", "van_ban"),
 "TH95_TUONG": ("TH", 95, "Nhưng nếu Tướng miếu vượng đắc địa mà gặp Tuần Triệt án ngữ, chẳng khác nào như Tướng hãm địa", "van_ban"),
 "TH115_TPVT": ("TH", 115, "Tử, Phủ, Vũ, Tướng có sao Lộc, Long Phượng, Tả Hữu nhất định phát giàu có lớn", "van_ban"),
 "TH116_TPVT": ("TH", 116, "Tử Phủ Vũ Tướng găp phải Tam Không, Kiếp Kỵ Hình Đà hay gặp Linh Hỏa Tang Diêu thì bị giáng chức, phá tài", "van_ban"),
 "TH116_CNDL": ("TH", 116, "Cơ Nguyệt Đồng Lương hay Cự Nhật mà gặp Kình Đà, Không Kiếp hay Phá toái, Kiếp sát", "van_ban"),
 "TH116_SPLT": ("TH", 116, "Sát phá Liêm Tham mà gặp Nhị tam Không, Linh Hỏa Kình Kỵ", "van_ban"),
 "TH43_TTAN": ("TH", 43, "cần gặp được Tuần, Triệt hay Hóa Lộc thì ngọc mới lộ ra được", "van_ban"),
 "KL44_KVGM": ("KL", 44, "Mệnh ở giữa, Khôi một bên, Việt một bên", "van_ban"),
 "KL44_TTAN": ("KL", 44, "Thạch trung ẩn ngọc -Ngọc quí ở trong đá -Mệnh có Cự môn, Di có Thiên cơ ở Tí Ngọ", "van_ban"),
 "KL49_TV_TAHUU": ("KL", 49, "Mệnh có Tử vi mà không có tả Hữu hội họp là ông vua cô độc", "van_ban"),
 "KL50_TP_KINH": ("KL", 50, "Tử vi, Thiên phủ đồng cung với Kình dương, lực sĩ thì buôn bán giàu có", "van_ban"),
 "KL50_TP_KY": ("KL", 50, "Mệnh ở Dần có Hoá kỵ, Hóa quyền đồng cung với Tử Phủ là người mưu cơ tài trí", "van_ban"),
 "KL51_CNDL": ("KL", 51, "Mệnh có Cơ Nguyệt Đồng Lương hội chiếu thường là công chức", "van_ban"),
 "KL52_NLTT": ("KL", 52, "Mệnh có Thái dương ở Ngọ, vi như mặt trời chiếu sáng giữa trưa", "van_ban"),
 "KL53_NN_TINHMINH": ("KL", 53, "Nhật nguyệt thủ Mệnh bất như hợp chiếu tịnh minh", "van_ban"),
 "KL53_NN_TUAN": ("KL", 53, "rất cần Tuần không án ngữ ở Mệnh", "van_ban"),
 "KL53_NN_KQL": ("KL", 53, "lại không có Đào Hồng Hỉ hay Khoa Quyền Lộc hợp chiếu", "van_ban"),
 "KL55_TP_TUAN": ("KL", 55, "chỉ sợ Triệt Tuần án ngữ thì kém đi thôi", "van_ban"),
 "KL56_NN_HAM": ("KL", 56, "Mệnh có Nhật hay Nguyệt hãm địa gặp Kình, Đà, Không Kiếp thì bôn ba khốn khổ", "van_ban"),
 "KL56_NGUYET_TAHUU": ("KL", 56, "Mệnh có Thái âm đắc địa, hoặc Vũ khúc đắc địa được Lộc tồn, Tả Hữu hợp chiếu thì giàu lớn", "van_ban"),
 "KL58_TTAN": ("KL", 58, "Mệnh ở Tí Ngọ có Cự môn được Khoa Quyền Lộc tam hợp chiếu là cách ngọc ở trong đá", "van_ban"),
 "KL60_MDDK_SAT": ("KL", 60, "có Thất sát Kình dương toạ thủ, lại thêm nhiều sát tinh hội chiếu", "van_ban"),
 "KL62_KV_SAT": ("KL", 62, "Cung mệnh có Khôi Việt lại bị sát tinh hội chiếu thì mang bệnh tật khó chữa khỏi", "van_ban"),
 "KL62_KV_KY_HINH": ("KL", 62, "lại không bị Hóa kỵ Thiên hình cản phá thì giàu sang lớn", "van_ban"),
 "KL62_KV_XUONGKHUC": ("KL", 62, "Mệnh có Khôi Việt, Xương, Khúc và Lộc tồn đồng cung hay hội chiếu", "van_ban"),
 "KL64_MDDK_XAU": ("KL", 64, "Mệnh ở Ngọ, có Kình dương, gặp Thất sát, Thiên hình đồng cung là cách kiếm kể cổ ngựa", "van_ban"),
 "KL64_MDDK_TOT": ("KL", 64, "có Kình dương đồng cung, nhưng xa lánh được Thất sát, Thiên hình mà lại gặp được Khoa Quyền Lộc", "van_ban"),
 "KL66_TKGH": ("KL", 66, "Cung mệnh có Khoa, Quyền, Lộc hội họp mà lại bị Hóa kỵ, Kình dương đồng cung hoặc chiếu vào", "van_ban"),
 "KL67_KY_KHOA": ("KL", 67, "Cung mệnh tại Hợi, Tí có Hóa kỵ tọa thủ gặp Hoá khoa đồng cung hay xung chiếu", "van_ban"),
 "KL68_NN_KHOIVIET": ("KL", 68, "chỉ mong được Khôi Việt chiếu mới là tốt đẹp", "van_ban"),
 "KL85_NLTT": ("KL", 85, "Thái dương thích Xương, Khúc, Khoa, Quyền, Lộc", "van_ban"),
 "KL85_NN_TUAN": ("KL", 85, "Thái dương hãm địa, cần gặp Tuần, Triệt, cũng cần gặp Đào, Hồng, Hỉ giúp sức", "van_ban"),
 "KL96_PHU": ("KL", 96, "Nhưng nếu gặp Không Kiếp, Tuần Triệt, Kình Đà, Hỏa Linh thì tài lộc bị giảm đáng kể", "van_ban"),
 "KL106_TTAN": ("KL", 106, "Cự môn ở Tí Ngọ gặp Tuần Triệt là kỳ cách", "van_ban"),
 "KL132_KHOA": ("KL", 132, "Hóa khoa, một sao Đại cứu giải", "van_ban"),
 "KL132_TPVT_TAHUU": ("KL", 132, "cách Tử Phủ Vũ Tướng mà thiếu Tả Hữu", "van_ban"),
 "KL193_TPVT_XK": ("KL", 193, "Xương Khúc, Tử Phủ Vũ Tướng là người văn võ toàn tài", "van_ban"),
 "KL199_HUNG": ("KL", 199, "Hung tinh chịu lép vế khi gặp Khoa, Tuần Triệt, Tài Thọ, Quan Phúc", "van_ban"),
 "KL200_GIAI": ("KL", 200, "Những sao giải mạnh gồm Tuần Triệt, Thiên tài, Hóa khoa, Quan Phúc", "van_ban"),
 "KL221_SPLT": ("KL", 221, "Sát Phá Tham ở Mệnh là những người tích cực trong cuộc sống", "van_ban"),
 "KL222_VT_TUAN": ("KL", 222, "Mệnh có Vũ Tướng mà không bị Tuần Triệt án ngữ thì cuộc đời suôn", "van_ban"),
 "TT22_TPDC_SAT": ("TT", 22, "Tử Phủ đồng cung vô sát tấu", "van_ban"),
 "TT22_TPDC_TYHOI": ("TT", 22, "Tử Phủ đồng cung lâm Tị Hợi nhất triều phú quí song toàn", "van_ban"),
 "TT24_CNDL_CORE": ("TT", 24, "Mệnh thân và các cung tam hợp xang chiếu có đủ bốn sao trên đây", "van_ban"),
 "TT24_CNDL_BREAK": ("TT", 24, "Gặp Kiếp Không Hoá Kị xuống hạ cách", "van_ban"),
 "TT142_NNTM": ("TT", 142, "Thái Dương đều đứng ở miếu vượng địa chiếu sáng", "van_ban"),
 "TT142_MDDK": ("TT", 142, "phải ở tứ mộ địa mới hay, ở Ngọ cung xấu", "van_ban"),
 "TT142_KQL": ("TT", 142, "Khoa, Quyền lộc củng (Chiếu thủ có cả ba Khoa, Quyền, Lộc)", "van_ban"),
 "TT46_KV": ("TT", 46, "Đóng ở Mệnh cung sang quí nhiều phúc lộc", "van_ban"),
}

F = {"TPVT": "CACH_X_TU_PHU_VU_TUONG", "TPDC": "CACH_X_TU_PHU_DONG_CUNG", "CNDL": "CACH_X_CO_NGUYET_DONG_LUONG",
     "SPLT": "CACH_X_SAT_PHA_LIEM_THAM", "NNTM": "CACH_X_NHAT_NGUYET_TINH_MINH", "NLTT": "CACH_X_NHAT_LE_TRUNG_THIEN",
     "TTAN": "CACH_X_THACH_TRUNG_AN_NGOC", "MDDK": "CACH_X_MA_DAU_DOI_KIEM", "TKGH": "CACH_X_TAM_KY_GIA_HOI",
     "KVGM": "CACH_X_KHOI_VIET_GIAP_MENH"}
FID2K = {v: k for k, v in F.items()}


def R(status, cites=(), reason="", action="giu_co_nguon", stance="ung_ho", conflict="", convention=""):
    """One audit verdict. stance: ung_ho (book says it in this role) | nguoc (book says the opposite) | lien_quan | khong_noi."""
    return {"status": status, "cites": list(cites), "reason": reason, "action": action, "stance": stance,
            "school_conflict": conflict, "design_convention": convention}


NO = R("khong_co_nguon", [], "không tìm thấy trang sách nói điều này trong vai trò đó; giữ làm giả thuyết thiết kế", "giu_gia_thuyet", "khong_noi")
KHOA_CUU = R("lien_quan", ["KL132_KHOA"], "sách chỉ nói Hóa Khoa là sao giải nói chung (KL p.132), không nói Khoa có quyền cứu riêng cách cục này; "
             "không suy ra quyền cứu cách cục từ một đoạn khen sao tốt", "giu_gia_thuyet", "lien_quan")
TAMHOA_CUU = R("long_hon", ["TH74_TAMHOA"], "TH p.74 chỉ nói Tam Hóa cứu Mệnh ở bại địa/tuyệt địa (Tuyệt xứ phùng sinh); bản nháp khái quát thành cứu mọi yếu tố phá cách",
               "de_xuat_sua", "lien_quan", convention="'phá được cứu' là quy ước thiết kế, không phải kết luận cổ thư")
SCHOOL_TUAN = ("Tuần/Triệt có hai vai trò trái nhau trong sách: giải hung tinh/hãm tinh (KL p.199-201, p.85) và làm hại quý tinh "
               "(KL p.55, TH p.94-95); kết luận theo từng cách phải nêu trường phái")

# default verdict by (role, condition id); overridden per formation below
D = {
 ("boosters", "ta_huu_hoi"): NO, ("boosters", "xuong_khuc_hoi"): NO, ("boosters", "loc_hoi"): NO, ("boosters", "khoi_viet_hoi"): NO,
 ("breakers", "sat_dong_cung"): NO, ("breakers", "ky_dong_cung"): NO,
 ("rescuers", "khoa_dong_cung"): KHOA_CUU, ("rescuers", "tam_hoa_hoi_cuu"): TAMHOA_CUU,
 ("refutations", "tuan_triet_an_ngu"): R("khong_co_nguon", [], "không có trang nói Tuần/Triệt làm hại cách này; sách chỉ nói về từng sao", "giu_gia_thuyet", "khong_noi", SCHOOL_TUAN),
}
X = {  # (formation key, condition id) -> verdict; condition id "core" for the core
 ("TPVT", "core"): R("khop", ["TH72_TPVT", "KL132_TPVT_TAHUU"], "tên cách có trong danh sách quý cách (TH p.72 mục 7); sách không nêu vị trí chính xác, việc đòi cả bốn sao trong tam phương Mệnh là cách mô hình hóa chuẩn"),
 ("TPVT", "ta_huu_hoi"): R("khop", ["KL132_TPVT_TAHUU"], "KL p.132: cách Tử Phủ Vũ Tướng mà thiếu Tả Hữu thì 'đầu Ngô mình Sở'"),
 ("TPVT", "xuong_khuc_hoi"): R("long_hon", ["KL193_TPVT_XK"], "sách nói Xương Khúc đi với Tử Phủ Vũ Tướng thì văn võ toàn tài; bản nháp chấp nhận một trong hai sao"),
 ("TPVT", "loc_hoi"): R("khop", ["TH115_TPVT"], "TH p.115 (đại tiểu hạn): Tử Phủ Vũ Tướng gặp sao Lộc thì phát giàu; lưu ý sách nói về hạn, không về bản cách"),
 ("TPVT", "sat_dong_cung"): R("chat_hon", ["TH116_TPVT", "KL96_PHU"], "sách nói 'gặp' (Tam Không, Kiếp, Hình, Đà, Linh Hỏa) không giới hạn đồng cung; bản nháp chỉ tính đồng cung Mệnh", "de_xuat_sua"),
 ("TPVT", "ky_dong_cung"): R("chat_hon", ["TH116_TPVT"], "TH p.116 liệt kê Kỵ trong nhóm gặp phải thì giáng chức phá tài; không giới hạn đồng cung", "de_xuat_sua"),
 ("TPVT", "tuan_triet_an_ngu"): R("khop", ["KL222_VT_TUAN", "TH94_PHU", "TH95_TUONG"], "Vũ Tướng/Thiên Phủ/Thiên Tướng đều bị Tuần Triệt làm hại; việc 'hạ một bậc' là quy ước thiết kế", conflict=SCHOOL_TUAN, convention="hạ một bậc là quy ước thiết kế"),
 ("TPVT", "Thiên_Tướng_ham"): R("lien_quan", ["TH95_TUONG"], "TH p.95 nói Tướng gặp Tuần Triệt 'như hãm', không nói Tướng hãm hạ cả cách; điều kiện không thể xảy ra vì Thiên Tướng hãm chỉ ở Mão/Dậu, nơi không hình thành đủ bốn sao",
                                 "khong_the_xay_ra", "lien_quan"),
 ("TPDC", "core"): R("chat_hon", ["TH72_TPDC", "TT22_TPDC_SAT"], "TH p.72 mục 1: đóng ở Mệnh HAY Thân; bản nháp chỉ neo ở Mệnh. TT p.22 còn nhắc cả Tỵ/Hợi nơi mô hình không có Tử Phủ đồng cung (bất đồng nguồn)",
                     "de_xuat_sua", conflict="TT p.22 nói Tử Phủ đồng cung ở Tỵ/Hợi; mô hình (và KL p.49) chỉ có ở Dần/Thân"),
 ("TPDC", "ta_huu_hoi"): R("lien_quan", ["KL49_TV_TAHUU"], "KL p.49 nói Tử Vi cần Tả Hữu (tránh 'ông vua cô độc'), không nói riêng về Tử Phủ đồng cung", "giu_gia_thuyet", "lien_quan"),
 ("TPDC", "sat_dong_cung"): R("khac", ["TT22_TPDC_SAT", "KL50_TP_KINH"], "TT p.22: Tử Phủ đồng cung 'vô sát tấu' mới hưởng phúc (ủng hộ); nhưng KL p.50 nói Tử Phủ đồng cung với Kình Dương thì buôn bán giàu có (ngược lại)",
                          "de_xuat_sua", "nguoc", conflict="TT p.22 (sát tinh làm hỏng) trái KL p.50 (Kình Dương đồng cung vẫn giàu)"),
 ("TPDC", "ky_dong_cung"): R("khac", ["KL50_TP_KY"], "KL p.50: Tử Phủ cùng Hóa Kỵ, Hóa Quyền ở Dần là người mưu cơ tài trí; không coi Kỵ là yếu tố phá", "de_xuat_sua", "nguoc"),
 ("TPDC", "tam_hoa_hoi_cuu"): R("long_hon", ["TH74_TAMHOA"], "như mọi cách: Tam Hóa chỉ được sách nói là cứu bại/tuyệt địa. Ngoài ra điều kiện này KHÔNG BAO GIỜ đúng ở Dần/Thân (Tam Hóa không bao giờ hội đủ trong tam phương của Dần/Thân khi có Tử Vi+Thiên Phủ): ràng buộc hình học của mô hình",
                                "khong_the_xay_ra", "lien_quan", convention="'phá được cứu' là quy ước thiết kế"),
 ("TPDC", "tuan_triet_an_ngu"): R("khop", ["KL55_TP_TUAN", "TH94_PHU"], "KL p.55: Tử Phủ đồng cung chỉ sợ Triệt Tuần án ngữ; TH p.94: Thiên Phủ kỵ Tuần Triệt", conflict=SCHOOL_TUAN, convention="hạ một bậc là quy ước thiết kế"),
 ("CNDL", "core"): R("khop", ["TT24_CNDL_CORE", "KL51_CNDL"], "TT p.24 đòi đủ bốn sao ở Mệnh/Thân và tam hợp xung chiếu: trùng định nghĩa; KL p.51 chỉ nói 'hội chiếu'"),
 ("CNDL", "cat_tinh_hoi"): R("khop", ["TT24_CNDL_CORE", "TH77_CNDL"], "TT p.24: thiếu cát tinh trợ lực chỉ là công chức quèn; TH p.77 kể Tả Hữu, Thai Cáo, Xương Khúc (vẫn là công chức); danh sách 6 cát tinh là chọn lọc của bản nháp",
                              conflict="TT p.24 / TH p.77 coi hội cát tinh vẫn chỉ ở mức công chức; KL p.221 (ảnh) nói hội Khoa Quyền Lộc, Khôi Việt, Xương Khúc thì giáo sư danh tiếng: mức 'tốt' khác nhau giữa các sách"),
 ("CNDL", "khoa_quyen_loc_hoi"): R("khop", ["KL221_SPLT"], "KL p.221 (đọc từ ảnh trang): CNDL hội Khoa Quyền Lộc, Khôi Việt, Xương Khúc thì làm giáo sư danh tiếng", conflict="xem cat_tinh_hoi", stance="ung_ho"),
 ("CNDL", "khong_kiep_dong_cung"): R("chat_hon", ["TT24_CNDL_BREAK", "TH116_CNDL"], "TT p.24 và TH p.116: 'gặp' Kiếp, Không (không giới hạn đồng cung Mệnh)", "de_xuat_sua"),
 ("CNDL", "ky_dong_cung"): R("chat_hon", ["TT24_CNDL_BREAK"], "TT p.24: gặp Hóa Kị thì xuống hạ cách (áp dụng cho cả cấu trúc, không chỉ đồng cung Mệnh)", "de_xuat_sua"),
 ("CNDL", "tuan_triet_an_ngu"): R("lien_quan", ["TH94_PHU"], "TH p.94-95 chỉ nói Thái Âm, Thiên Lương gặp Tuần Triệt là bất lợi; không nói cả cách CNDL", "giu_gia_thuyet", "lien_quan", SCHOOL_TUAN),
 ("SPLT", "core"): R("lien_quan", ["TH72_SPLT"], "tên cách có trong TH p.72 mục 4 (đọc từ ảnh), nhưng sách không nêu số sao cần có; ngưỡng '3 trong 4 sao' là quy ước thiết kế",
                     "quy_uoc_thiet_ke", "lien_quan", convention="ngưỡng 3 trong 4 sao là quy ước thiết kế, sách không nêu"),
 ("SPLT", "khoa_quyen_hoi"): R("khop", ["TH76_CATTINH"], "TH p.76: Sát Phá Liêm Tham miếu vượng hội cát tinh gồm Khoa Quyền Lộc (nhóm phi thường cách)", conflict="TH p.76 cũng đếm Kình, Không trong nhóm cát hội; KL p.221 không coi sát tinh là yếu tố phá"),
 ("SPLT", "ta_huu_hoi"): R("lien_quan", ["TH76_CATTINH"], "danh sách cát tinh của TH p.76 là chung cho nhóm cách, không riêng Tả Hữu cho SPLT", "giu_gia_thuyet", "lien_quan"),
 ("SPLT", "xuong_khuc_hoi"): R("lien_quan", ["TH76_CATTINH"], "như trên", "giu_gia_thuyet", "lien_quan"),
 ("SPLT", "khoi_viet_hoi"): R("lien_quan", ["TH76_CATTINH"], "như trên", "giu_gia_thuyet", "lien_quan"),
 ("SPLT", "ba_sat_va_ky_trong_tam_phuong"): R("chat_hon", ["TH77_SPLT_HA", "TH116_SPLT"], "TH p.77: hạ cách khi hội Vũ, Kình Đà, Thiên Địa Không... 'nhiều' hung sát ở hãm địa; bản nháp đòi từ 3 sát tinh VÀ Hóa Kỵ. Con số 3 và điều kiện kèm Kỵ là quy ước thiết kế",
                                              "quy_uoc_thiet_ke", "lien_quan", conflict="TH p.76 xếp Kình, Không vào nhóm cát hội của SPLT, trái TH p.77", convention="ngưỡng '3 sát tinh + Kỵ' là quy ước thiết kế"),
 ("SPLT", "ky_dong_cung"): R("chat_hon", ["TH116_SPLT"], "TH p.116: gặp Linh Hỏa Kình Kỵ thì tù ngục vong gia; không giới hạn đồng cung", "de_xuat_sua"),
 ("SPLT", "Thất_Sát_ham"): NO,
 ("NNTM", "core"): R("long_hon", ["TH72_NNTM", "KL53_NN_TINHMINH"], "TH p.72: Nhật ở Thìn/Tỵ, Nguyệt ở Dậu/Tuất và Mệnh đóng ở Nhật hay Nguyệt; KL p.53 chỉ cần Nhật Nguyệt hợp chiếu Mệnh (ví dụ Mệnh Sửu). Bản nháp theo KL (rộng hơn TH)",
                     "de_xuat_sua", conflict="TH p.72 (vị trí cố định) khác KL p.53 (hợp chiếu tịnh minh)"),
 ("NNTM", "nhat_nguyet_deu_sang"): R("khop", ["TT142_NNTM", "KL53_NN_TINHMINH"], "TT p.142: cả hai sao ở miếu vượng; KL p.53: đắc địa; ngưỡng bản nháp 'đắc trở lên' theo KL", conflict="TT nói miếu vượng, KL nói đắc địa"),
 ("NNTM", "ta_huu_hoi"): R("lien_quan", ["KL56_NGUYET_TAHUU"], "KL p.56 nói Tả Hữu giúp Thái Âm/Vũ Khúc, không nói riêng Nhật Nguyệt tịnh minh", "giu_gia_thuyet", "lien_quan"),
 ("NNTM", "khoa_quyen_hoi"): R("lien_quan", ["KL53_NN_KQL"], "KL p.53 mục 8 nói Khoa Quyền Lộc hợp chiếu giúp Nhật Nguyệt Sửu Mùi; chưa phải cách tịnh minh", "giu_gia_thuyet", "lien_quan"),
 ("NNTM", "nhat_nguyet_ham_gap_sat"): R("khop", ["TH74_NN_TAN_HUNG", "KL56_NN_HAM"], "TH p.74 (bần tiện cách số 7, từ ảnh) và KL p.56: Nhật/Nguyệt hãm gặp sát tinh thì khốn khổ"),
 ("NNTM", "ky_dong_cung"): R("lien_quan", ["KL85_NN_TUAN"], "KL p.85 nói Thái Dương ghét Kỵ nhưng không nêu cho cách tịnh minh", "giu_gia_thuyet", "lien_quan"),
 ("NNTM", "khong_kiep_dong_cung"): R("lien_quan", ["KL56_NN_HAM"], "KL p.56 nói Nhật/Nguyệt HÃM gặp Không Kiếp; bản nháp áp dụng cho cả khi sáng", "giu_gia_thuyet", "lien_quan"),
 ("NNTM", "Thái_Dương_ham"): R("chat_hon", ["TH74_NN_TAN_HUNG", "KL68_NN_KHOIVIET"], "TH p.74: hãm tại Mệnh KHÔNG có cứu tinh mới là tàn hung; KL p.68 cho Khôi Việt chiếu là cứu. Bản nháp hạ mọi trường hợp hãm", "de_xuat_sua", conflict="Tuần/Triệt vừa cứu Nhật hãm (KL p.85) vừa hại Thái Âm (TH p.94)"),
 ("NNTM", "Thái_Âm_ham"): R("chat_hon", ["TH74_NN_TAN_HUNG", "KL68_NN_KHOIVIET"], "như Thái Dương hãm", "de_xuat_sua"),
 ("NNTM", "tuan_triet_an_ngu"): R("khac", ["KL53_NN_TUAN", "KL85_NN_TUAN"], "KL p.53 mục 11 nói Nhật Nguyệt Sửu Mùi RẤT CẦN Tuần án ngữ; KL p.85 Tuần Triệt giải Thái Dương hãm: ngược với việc coi Tuần/Triệt là phản chứng", "de_xuat_sua", "nguoc", SCHOOL_TUAN),
 ("NLTT", "core"): R("khop", ["TH72_NLTT", "KL52_NLTT"], "TH p.72 mục 22 và KL p.52: Thái Dương cư Ngọ ở Mệnh"),
 ("NLTT", "ta_huu_hoi"): NO,
 ("NLTT", "khoa_quyen_hoi"): R("khop", ["KL85_NLTT"], "KL p.85: Thái Dương thích Xương Khúc, Khoa Quyền Lộc"),
 ("NLTT", "xuong_khuc_hoi"): R("khop", ["KL85_NLTT"], "KL p.85: Thái Dương thích Xương Khúc, Khoa Quyền Lộc"),
 ("NLTT", "sat_dong_cung"): R("lien_quan", ["KL85_NN_TUAN"], "KL p.85 nêu Đà, Kỵ, Riêu là sao Thái Dương ghét; không nêu toàn bộ sát tinh và không riêng cho Ngọ", "giu_gia_thuyet", "lien_quan"),
 ("NLTT", "ky_dong_cung"): R("chat_hon", ["KL85_NN_TUAN"], "KL p.85: Thái Dương ghét Kỵ (không giới hạn đồng cung)", "de_xuat_sua"),
 ("NLTT", "tuan_triet_an_ngu"): R("khong_co_nguon", ["KL85_NN_TUAN"], "Tuần/Triệt trong sách giúp Thái Dương HÃM; với Thái Dương vượng ở Ngọ không có trang nói Tuần/Triệt gây hại", "giu_gia_thuyet", "khong_noi", SCHOOL_TUAN),
 ("NLTT", "Thái_Dương_ham"): R("khong_co_nguon", [], "Không thể xảy ra: Thái Dương ở Ngọ luôn vượng theo bảng miếu vượng, nên điều kiện (bảng độ sáng) không bao giờ đúng; đây không phải lỗi logic mà là hệ quả của bảng", "khong_the_xay_ra", "khong_noi"),
 ("TTAN", "core"): R("khop", ["KL58_TTAN", "KL44_TTAN"], "KL p.58: Mệnh ở Tí/Ngọ có Cự Môn; KL p.44 lại định nghĩa Mệnh Cự Môn + Di Thiên Cơ ở Tí Ngọ (ba định nghĩa khác nhau giữa KL p.44, KL p.58 và TH p.43)",
                     conflict="KL p.44 (Mệnh Cự, Di Cơ) / KL p.58 (cần Khoa Quyền Lộc) / KL p.106 và TH p.43 (cần Tuần Triệt hoặc Hóa Lộc) là ba điều kiện khác nhau"),
 ("TTAN", "tam_hoa_hoi_du"): R("khop", ["KL58_TTAN", "TT142_KQL"], "KL p.58: Khoa Quyền Lộc tam hợp chiếu là cách ngọc ở trong đá"),
 ("TTAN", "ta_huu_hoi"): NO,
 ("TTAN", "ky_hoac_kinh_dong_cung"): NO,
 ("TTAN", "tuan_triet_an_ngu"): R("khac", ["KL106_TTAN", "TH43_TTAN"], "KL p.106: Cự Môn Tí Ngọ gặp Tuần Triệt là kỳ cách; TH p.43: cần Tuần, Triệt hay Hóa Lộc: ngược với việc dùng Tuần/Triệt làm phản chứng", "de_xuat_sua", "nguoc", SCHOOL_TUAN),
 ("TTAN", "Cự_Môn_ham"): R("khong_co_nguon", [], "Không thể xảy ra: Cự Môn ở Tí/Ngọ luôn vượng theo bảng miếu vượng; không phải lỗi logic mà là hệ quả của bảng", "khong_the_xay_ra", "khong_noi"),
 ("MDDK", "core"): R("khop", ["KL64_MDDK_XAU", "KL64_MDDK_TOT", "TT142_MDDK"], "KL p.64 mục 5-6: Mệnh ở Ngọ có Kình Dương; TT p.142 nói Kình ở Ngọ là xấu (khác KL mục 6)",
                     conflict="KL p.64 mục 5 xấu / mục 6 tốt cùng một vị trí; TT p.142 cho rằng Kình ở Ngọ xấu"),
 ("MDDK", "khoa_quyen_loc_hoi"): R("khop", ["KL64_MDDK_TOT"], "KL p.64 mục 6: gặp Khoa Quyền Lộc thì sự nghiệp lớn về võ nghiệp (điều kiện kèm xa lánh Thất Sát, Thiên Hình)"),
 ("MDDK", "ta_huu_hoi"): NO,
 ("MDDK", "that_sat_trong_tam_phuong"): R("long_hon", ["KL64_MDDK_XAU", "KL60_MDDK_SAT"], "KL p.64 mục 5: Thất Sát, Thiên Hình ĐỒNG CUNG với Kình; KL p.60: Thất Sát Kình tọa thủ + nhiều sát tinh hội chiếu. Bản nháp tính cả tam phương", "de_xuat_sua"),
 ("MDDK", "sat_khac_dong_cung"): R("lien_quan", ["KL60_MDDK_SAT"], "KL p.60 nói 'nhiều sát tinh hội chiếu', không phải đồng cung", "giu_gia_thuyet", "lien_quan"),
 ("MDDK", "ky_dong_cung"): NO,
 ("MDDK", "tuan_triet_an_ngu"): NO,
 ("TKGH", "core"): R("khop", ["KL66_TKGH", "TT142_KQL"], "KL p.66 mục 10: Khoa, Quyền, Lộc hội họp ở Mệnh; TT p.142 Khoa Quyền Lộc củng. TH p.72 mục 12 'Tam Hóa liên châu' (ba cung liền) là điều kiện chặt hơn, khác tên",
                     conflict="TH p.72 mục 12 (ba cung liền) khác KL/TT (hội trong tam phương)"),
 ("TKGH", "hoa_o_ban_cung"): R("khop", ["TH72_TAMHOA"], "TH p.72 mục 12 (đọc từ ảnh): cần có một hóa ở chính cung Mệnh"),
 ("TKGH", "ta_huu_hoi"): NO,
 ("TKGH", "xuong_khuc_hoi"): NO,
 ("TKGH", "ky_hoac_kinh_dong_cung"): R("chat_hon", ["KL66_TKGH"], "KL p.66: Hóa Kỵ, Kình Dương 'đồng cung HOẶC CHIẾU' làm công danh mờ mịt; bản nháp chỉ tính đồng cung", "de_xuat_sua"),
 ("TKGH", "ta_huu_giai_ky"): R("khong_co_nguon", [], "không tìm thấy trang nói Tả Hữu giải Kỵ/Kình cho cách này", "giu_gia_thuyet", "khong_noi"),
 ("TKGH", "tuan_triet_an_ngu"): NO,
 ("KVGM", "core"): R("khop", ["KL44_KVGM", "TT46_KV"], "KL p.44 mục 9: Mệnh ở giữa, Khôi một bên, Việt một bên (tuổi Bính Đinh Nhâm Quý, Mệnh Thìn/Tuất)"),
 ("KVGM", "co_chinh_tinh"): NO,
 ("KVGM", "ta_huu_hoi"): NO,
 ("KVGM", "xuong_khuc_hoi"): R("khop", ["KL62_KV_XUONGKHUC"], "KL p.62 mục 2: Khôi Việt cùng Xương Khúc, Lộc Tồn thì giàu sang"),
 ("KVGM", "sat_dong_cung"): R("chat_hon", ["KL62_KV_SAT"], "KL p.62 mục 4: Khôi Việt bị sát tinh HỘI CHIẾU thì mang bệnh; bản nháp chỉ tính đồng cung", "de_xuat_sua"),
 ("KVGM", "ky_dong_cung"): R("chat_hon", ["KL62_KV_KY_HINH"], "KL p.62 mục 2: Hóa Kỵ, Thiên Hình cản phá thì mất giàu sang (không giới hạn đồng cung)", "de_xuat_sua"),
 ("KVGM", "vo_chinh_dieu"): NO,
 ("KVGM", "tuan_triet_an_ngu"): NO,
}


def conditions(defs):
    for f in defs:
        k = FID2K[f["id"]]
        yield k, f, "core", "core", "Điều kiện lõi", f["core"]
        for role in ("boosters", "breakers", "rescuers", "refutations"):
            for c in f[role]:
                yield k, f, role, c["id"], c["label"], c["when"]


def verify(book, page, quote):
    if not bt.available(book):
        return "chua_kiem"
    try:
        return "van_ban" if bt.quote_on_page(book, page, quote) else "SAI"
    except Exception:
        return "chua_kiem"


def build():
    defs = json.load(open(DEFS, encoding="utf-8"))["formations"]
    reach = json.load(open(REACH, encoding="utf-8"))
    dead = {(c if isinstance(c, str) else c.get("id")) for c in reach.get("never_active_conditions", [])} if isinstance(reach, dict) else set()
    rows, bad = [], []
    for k, f, role, cid, label, when in conditions(defs):
        v = X.get((k, cid)) or D.get((role, cid))
        if v is None:
            raise SystemExit(f"audit missing for {k} {role} {cid}")
        cites = []
        for q in v["cites"]:
            book, page, quote, method = Q[q]
            chk = verify(book, page, quote) if method == "van_ban" else "anh"
            if chk == "SAI":
                bad.append((q, book, page, quote))
            cites.append({"id": q, "book": bt.BOOK_NAMES[book], "book_code": book, "page": page, "quote": quote, "quote_check": chk})
        rows.append({"formation": f["id"], "formation_key": k, "name_vi": f["name_vi"], "role": role, "id": cid, "label": label,
                     "status": v["status"], "stance": v["stance"], "action": v["action"], "cites": cites, "reason": v["reason"],
                     "school_conflict": v["school_conflict"], "design_convention": v["design_convention"],
                     "machine_checked": bool(cites) and all(c["quote_check"] == "van_ban" for c in cites)})
    if bad:
        raise SystemExit("quote not found on cited page:\n" + "\n".join(map(str, bad)))
    return rows


def summary(rows):
    st = Counter(r["status"] for r in rows)
    act = Counter(r["action"] for r in rows)
    authenticated = [r for r in rows if r["status"] == "khop" and any(c["quote_check"] in ("van_ban", "anh") for c in r["cites"])
                     and r["stance"] == "ung_ho"]
    return {"total": len(rows), "by_status": dict(st), "by_action": dict(act),
            "authenticated_matching": len(authenticated),
            "khop_machine_checked": sum(1 for r in authenticated if r["machine_checked"]),
            "excluded_from_sourced": sum(1 for r in rows if r["action"] in ("giu_gia_thuyet", "khong_the_xay_ra") and r["status"] in ("khong_co_nguon", "lien_quan")),
            "school_conflicts": sum(1 for r in rows if r["school_conflict"]),
            "design_conventions": sum(1 for r in rows if r["design_convention"])}


def write(rows):
    OUT_JSON.write_text(json.dumps({"version": 1, "note": "Kiểm toán nguồn Phase 2: mỗi dòng ghi trang sách và câu trích ngắn; không dòng nào được đánh dấu verified.",
                                    "summary": summary(rows), "rows": rows}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


STATUS_VI = {"khop": "Khớp", "long_hon": "Lỏng hơn nguồn", "chat_hon": "Chặt hơn nguồn", "khac": "Khác/ngược nguồn",
             "lien_quan": "Chỉ liên quan", "khong_co_nguon": "Chưa có nguồn"}
ACTION_VI = {"giu_co_nguon": "giữ (có nguồn)", "de_xuat_sua": "đề xuất sửa", "giu_gia_thuyet": "giữ như giả thuyết",
             "quy_uoc_thiet_ke": "quy ước thiết kế", "khong_the_xay_ra": "không thể xảy ra"}
ROLE_VI = {"core": "lõi", "boosters": "tăng thế", "breakers": "phá", "rescuers": "cứu", "refutations": "phản chứng"}


def write_md(rows):
    s = summary(rows)
    L = ["# Phase 2 — Kiểm toán nguồn học thuật cho 10 cách cục Tử Vi (bản nháp)", "",
         "Tài liệu sinh bởi `tools/build_formation_audit.py` từ `engine/data/experimental/formation_audit.json`. Mọi dòng được viết sau khi **đọc trực tiếp trang sách** "
         "(Khảo Luận = KL, Thực Hành = TH, Toàn Thư = TT; số trang in = chỉ số PDF + 1). Câu trích được so với văn bản trang khi sách có trên máy "
         "(`van_ban`); các trang lỗi lớp chữ phải đọc từ ảnh (`anh`). **Không điều kiện nào được đánh dấu verified; toàn bộ cách cục vẫn là `draft`, chỉ hiện ở `?thu-nghiem`.**", "",
         "## 1. Tổng kết", "", f"- Tổng số điều kiện: **{s['total']}**",
         f"- Khớp nguồn (nguồn nói đúng vai trò này): **{s['by_status'].get('khop', 0)}**",
         f"- Có nguồn một phần nhưng định nghĩa nháp lỏng hơn / chặt hơn: **{s['by_status'].get('long_hon', 0)} / {s['by_status'].get('chat_hon', 0)}**",
         f"- Khác hoặc ngược nguồn: **{s['by_status'].get('khac', 0)}**",
         f"- Chỉ liên quan (nguồn nói về sao đó nhưng không đúng vai trò): **{s['by_status'].get('lien_quan', 0)}**",
         f"- Chưa tìm được nguồn: **{s['by_status'].get('khong_co_nguon', 0)}**",
         f"- Bị loại khỏi định nghĩa 'có nguồn' (giữ như giả thuyết riêng hoặc không thể xảy ra): **{s['excluded_from_sourced']}**",
         f"- Đề xuất sửa định nghĩa (chuyển cho chủ định nghĩa, chưa áp dụng): **{s['by_action'].get('de_xuat_sua', 0)}**",
         f"- Quy ước thiết kế được gắn nhãn: **{s['design_conventions']}**; bất đồng giữa trường phái được nêu: **{s['school_conflicts']}**", "",
         "## 2. Bảng kiểm toán 93 điều kiện", ""]
    cur = None
    for r in rows:
        if r["formation"] != cur:
            cur = r["formation"]
            L += ["", f"### {r['name_vi']} (`{cur}`)", "", "| Vai trò | Điều kiện | Mức khớp | Nguồn · trang · trích | Lý do | Xử lý |", "|---|---|---|---|---|---|"]
        cites = "<br>".join(f"{c['book_code']} p.{c['page']} ({c['quote_check']}): “{c['quote']}”" for c in r["cites"]) or "—"
        flags = ("; **trường phái:** " + r["school_conflict"] if r["school_conflict"] else "") + ("; **quy ước:** " + r["design_convention"] if r["design_convention"] else "")
        L.append(f"| {ROLE_VI[r['role']]} | `{r['id']}` — {r['label']} | {STATUS_VI[r['status']]} | {cites} | {r['reason']}{flags} | {ACTION_VI[r['action']]} |".replace("\n", " "))

    L += ["", "## 3. Ngưỡng và quy ước thiết kế (không phải kết luận cổ thư)", "",
          "- **'3 trong 4 sao' của Sát Phá Liêm Tham**: sách có tên cách (TH p.72 mục 4) nhưng không nêu số sao cần có. Đây là quy ước thiết kế.",
          "- **'2 yếu tố tăng thế' → *thành thượng***: không trang nào định nghĩa mức này; ngưỡng `thuong_at = 2` là quy ước. Thang bậc không cộng điểm: thêm sao tăng thế không vượt quá *thành thượng*.",
          "- **'3 sát tinh + Hóa Kỵ' (SPLT hạ cách)**: TH p.77 chỉ nói 'nhiều' hung sát ở hãm địa; con số 3 và việc kèm Kỵ là quy ước.",
          "- **'Phá được cứu'**: TH p.74 chỉ nói Tam Hóa cứu Mệnh ở bại/tuyệt địa; KL p.132 chỉ gọi Hóa Khoa là sao giải nói chung. Việc một sao cứu một yếu tố phá của một cách cụ thể là quy ước thiết kế; không dùng đoạn khen sao tốt để suy ra quyền cứu.",
          "- **Phản chứng hạ một bậc**: quy ước (sách chỉ nói sao bị Tuần/Triệt/hãm thì kém đi).", "",
          "## 4. Bốn điều kiện không bao giờ kích hoạt", "",
          "| Điều kiện | Phân loại | Giải thích |", "|---|---|---|",
          "| Thiên Tướng hãm (TPVT) | **hạn chế vị trí sao** | Thiên Tướng chỉ hãm ở Mão/Dậu, nơi bốn sao Tử Phủ Vũ Tướng không thể cùng tam phương Mệnh. Không phải mâu thuẫn logic của luật. |",
          "| Thái Dương hãm (NLTT) | **bảng miếu vượng** | cách đòi Thái Dương ở Ngọ, mà bảng cho Ngọ là vượng. Điều kiện đúng về logic nhưng bị bảng loại trừ. |",
          "| Cự Môn hãm (TTAN) | **bảng miếu vượng** | cách đòi Cự Môn ở Tý/Ngọ, bảng cho là vượng. |",
          "| Tam Hóa hội cứu (TPDC) | **hạn chế hình học của mô hình** | xem mục 5. |", "",
          "Không điều kiện nào bị sửa để tăng tỷ lệ kích hoạt; chúng giữ nguyên và bị gắn nhãn `không thể xảy ra`.", "",
          "## 5. Tử Phủ đồng cung × *phá được cứu* — bất khả thi trong mô hình", "",
          "Tử Vi và Thiên Phủ cùng cung chỉ khi Tử Vi ở Dần/Thân (Thiên Phủ đối xứng qua trục Dần–Thân). Khi đó cả 14 chính tinh có vị trí cố định; chỉ Tả/Hữu (theo tháng) và Xương/Khúc (theo giờ) thay đổi. Để *phá được cứu* cần (A) Hóa Khoa và Hóa Kỵ cùng ở cung Mệnh, hoặc (B) Hóa Lộc, Quyền, Khoa cùng hội trong tam phương.", "",
          "(A) Hóa Kỵ chỉ có thể nằm trong cung Mệnh nếu sao mang Kỵ là phụ tinh: chỉ có Kỷ (Kỵ = Văn Khúc) và Tân (Kỵ = Văn Xương); ở tám can còn lại Kỵ rơi vào một chính tinh có vị trí cố định khác cung Tử Phủ. Với Kỷ, Hóa Khoa là Thiên Lương (chính tinh, Thiên Phủ + 5 cung) nên không ở cung Mệnh. Với Tân, Khoa = Văn Khúc và Kỵ = Văn Xương, mà hai sao này chỉ trùng cung ở Sửu/Mùi, không bao giờ ở Dần/Thân. (B) kiểm bằng liệt kê 10 can × 2 vị trí × 12 tháng × 12 giờ. Cả hai được test trong `engine/tests/test_formation_geometry.py` và xác nhận lại trên mọi lá số thật có Tử Phủ đồng cung.", "",
          "## 6. Bất đồng giữa các trường phái (giữ riêng, không gộp)", "",
          "- **Tuần/Triệt**: vừa là sao giải hung/hãm tinh mạnh (KL p.199-201, p.85, p.289) vừa làm hại quý tinh (KL p.55, p.222; TH p.94-95). Cách kết luận phụ thuộc cách cục. Thạch trung ẩn ngọc và Nhật Nguyệt Sửu Mùi thì Tuần/Triệt là điều kiện *cần* (KL p.106, TH p.43, KL p.53).",
          "- **Thạch trung ẩn ngọc**: ba định nghĩa — Mệnh Cự Môn + Di Thiên Cơ (KL p.44), Cự Môn Tý/Ngọ + Khoa Quyền Lộc tam hợp (KL p.58, TT p.34), Cự Môn Tý/Ngọ gặp Tuần/Triệt hoặc Hóa Lộc (KL p.106, TH p.43).",
          "- **Mã đầu đới kiếm**: xấu khi Kình + Thất Sát/Thiên Hình đồng cung (KL p.64 mục 5), tốt khi xa lánh Thất Sát/Thiên Hình mà gặp Khoa Quyền Lộc (mục 6); TT p.142 cho Kình ở Ngọ là xấu.",
          "- **Tử Phủ đồng cung**: 'vô sát tấu' (TT p.22) trái KL p.50 (Kình Dương, Hóa Kỵ đồng cung vẫn giàu/mưu trí); TT p.22 còn nhắc Tỵ/Hợi trong khi mô hình chỉ có Dần/Thân; TH p.72 cho phép đóng ở Mệnh hay Thân.",
          "- **Nhật Nguyệt tịnh minh**: TH p.72 vị trí cố định (Nhật Thìn/Tỵ, Nguyệt Dậu/Tuất); KL p.53 chỉ cần hợp chiếu; TT p.142 'miếu vượng', KL p.53 'đắc địa'.",
          "- **Sát Phá Liêm Tham**: TH p.76 xếp Kình, Không vào nhóm cát hội của Thân Sát Phá Liêm Tham, trái TH p.77 coi hội sát tinh nhiều là hạ cách.",
          "- **Cơ Nguyệt Đồng Lương**: TT p.24 / TH p.77 coi hội cát tinh vẫn chỉ ở mức công chức; KL p.221 nói hội Khoa Quyền Lộc, Khôi Việt, Xương Khúc thì giáo sư danh tiếng.", "",
          "## 7. Bộ lá số đối chứng (KL pp.237-246)", "",
          "| Lá số | Cách cục | Engine | Nhận xét của sách | Kết quả |", "|---|---|---|---|---|",
          "| Hán Cao Tổ | Tử Phủ Vũ Tướng | thành thượng | thế rất mạnh | đồng ý |",
          "| Hạng Võ | Cơ Nguyệt Đồng Lương | thành | thất bại (Triệt + Địa Kiếp ở Tài; Tuần ở Quan) | **không khớp** |",
          "| Hạng Võ | Tam kỳ gia hội | thành | số xấu tổng thể (Cự + Kỵ ở Di) | **không khớp** |",
          "| Khổng Minh | Nhật Nguyệt tịnh minh | thành thượng | thông minh tuyệt vời | đồng ý |",
          "| Nữ Quý Mão | Cơ Nguyệt Đồng Lương, Khôi Việt giáp Mệnh | thành | sách không gọi tên | không xét |",
          "| Mậu Tý phá sản | Nhật Nguyệt tịnh minh | bị phá | âm dương lạc hãm, phá sản | đồng ý |",
          "| Mậu Tý phá sản | Cơ Nguyệt Đồng Lương | thành thượng | Cơ + Kỵ + Hỏa Linh phá sản | **không khớp** |", "",
          "Cả ba trường hợp không khớp cùng nguyên nhân: sách tính Triệt/Tuần/Kỵ/sát tinh trên cả tam phương hoặc cung chiếu; bản nháp chỉ tính khi đồng cung Mệnh. Engine **không được chỉnh** để khớp; ghi nhận là phát hiện (đề xuất sửa ở mục 8). Số mẫu rất nhỏ (7 cặp có nhận xét) nên không thể suy ra độ chính xác.", "",
          "## 8. Đề xuất sửa định nghĩa (chủ định nghĩa quyết định; chưa áp dụng)", "",
          "1. Mở rộng phạm vi phá từ 'đồng cung Mệnh' sang 'đồng cung hoặc chiếu' cho Tam kỳ gia hội (KL p.66), và sang tam phương cho Cơ Nguyệt Đồng Lương (TT p.24).",
          "2. Mã đầu đới kiếm: phá khi Thất Sát/Thiên Hình ĐỒNG CUNG (KL p.64), không phải mọi Thất Sát trong tam phương.",
          "3. Bỏ 'Tuần/Triệt' làm phản chứng cho Thạch trung ẩn ngọc và Nhật Nguyệt tịnh minh (sách coi là điều kiện thuận), hoặc tách theo trường phái.",
          "4. Tử Phủ đồng cung: neo ở Mệnh hoặc Thân (TH p.72); tách nhánh 'vô sát' (TT p.22) khỏi nhánh Kình/Kỵ (KL p.50).",
          "5. Nhật/Nguyệt hãm: chỉ hạ khi không có cứu tinh (TH p.74), thêm Khôi Việt chiếu làm cứu (KL p.68).",
          "6. Khôi Việt giáp Mệnh: sát tinh và Kỵ/Hình tính cả hội chiếu (KL p.62).", ""]
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    rows = build()
    write(rows)
    write_md(rows)
    print(json.dumps(summary(rows), ensure_ascii=False, indent=1))
