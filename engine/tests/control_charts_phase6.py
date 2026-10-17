"""Phase 6 control set: the worked example charts of Tử Vi Khảo Luận (pp.237-247) with what the BOOK says about each structure,
kept separate from what the engine says. Nothing here is tuned to make them agree; disagreements stay in the table.

book_says : "xac_nhan"        the commentary supports the structure/its favourable reading
            "phu_dinh"        the commentary contradicts it (the structure fails / is broken)
            "khong_ket_luan"  the commentary names no such structure
direction of an engine state: thuan = thanh|thanh_thuong, han_che = bi_pha, trung = hinh_thuc|pha_duoc_cuu.  Agreement is only claimed when both
point the same way; 'trung' never counts as agreement or disagreement ("khong_quyet_dinh")."""

# input = LUNAR date as printed in the book + a modern lunar year with the same stem-branch (the book prints the year pillar only)
CHARTS = {
    "han_cao_to": dict(ly=2014, lm=11, ld=13, hb=6, male=True, label="Hán Cao Tổ (Giáp Ngọ)", page=237),
    "hang_vo": dict(ly=1987, lm=8, ld=12, hb=3, male=True, label="Hạng Võ (Đinh Mão)", page=238),
    "khong_minh": dict(ly=1981, lm=4, ld=10, hb=10, male=True, label="Khổng Minh (Tân Dậu)", page=240),
    "han_tin": dict(ly=1994, lm=11, ld=5, hb=6, male=True, label="Hàn Tín (Giáp Tuất)", page=242),
    "nu_quy_mao": dict(ly=1963, lm=5, ld=20, hb=2, male=False, label="Nữ Quý Mão", page=244),
    "mau_ty_pha_san": dict(ly=1948, lm=1, ld=4, hb=10, male=True, label="Mậu Tý phá sản", page=246),
}

# (chart, baseline formation id, book_says, quote, baseline state, {variant suffix: state}, basis)
# basis: "ten"      the commentary names the structure's own stars (e.g. 'Đồng Lương ngọ Triệt', 'Nhật Nguyệt ... chiếu hư không')
#        "tong_the" the structure is NOT named; only the book's overall reading of the chart is used (weaker evidence, reported in its own column)
F = "CACH_X_"
ROWS = [
    ("han_cao_to", F + "TU_PHU_VU_TUONG", "xac_nhan", ("KL", 237, "Phải công nhận đây là một lá số có nhiều ưu điểm về công danh sự nghiệp lâu bền"),
     "thanh_thuong", {"@kl_132_193": "thanh_thuong", "@th_115": "thanh_thuong"}, "tong_the"),
    ("hang_vo", F + "CO_NGUYET_DONG_LUONG", "phu_dinh", ("KL", 238, "Cung Tài có Đồng Lương ngọ Triệt lại gặp Địa kiếp thì dù Tướng Ấn cũng chẳng giữ được sự nghiệp lâu dài"),
     "thanh", {"@tt_24": "bi_pha", "@kl_221": "thanh"}, "ten"),
    ("hang_vo", F + "TAM_KY_GIA_HOI", "phu_dinh", ("KL", 238, "Cung Di, có Cự Kỵ là cách tử nạn về sông nước"),
     "thanh", {"@kl_66": "bi_pha"}, "tong_the"),
    ("khong_minh", F + "NHAT_NGUYET_TINH_MINH", "xac_nhan", ("KL", 240, "là người thông minh tuyệt vời, tài ba xuất chúng được kính nể cầu cạnh"),
     "thanh_thuong", {"@kl_53_68": "thanh"}, "ten"),
    ("han_tin", F + "TU_PHU_VU_TUONG", "xac_nhan", ("KL", 242, "Hơn nữa lại còn giữ Song Lộc, Hóa Lộc ở Mệnh, có Lộc tồn ở Tài chiếu lên giàu sang phú quí một thời"),
     "thanh_thuong", {"@kl_132_193": "thanh_thuong", "@th_115": "thanh_thuong"}, "tong_the"),
    ("han_tin", F + "TAM_KY_GIA_HOI", "khong_ket_luan", ("KL", 242, "Đây là một lá số đẹp nhưng không có hậu"),
     "thanh_thuong", {"@kl_66": "hinh_thuc"}, "tong_the"),
    ("nu_quy_mao", F + "CO_NGUYET_DONG_LUONG", "khong_ket_luan", ("KL", 244, "Người tuổi Quí Mão, Can Quí (Thủy) sinh Chi Mão (Mộc), tương sinh"),
     "thanh", {"@tt_24": "thanh", "@kl_221": "thanh_thuong"}, "tong_the"),
    ("nu_quy_mao", F + "KHOI_VIET_GIAP_MENH", "khong_ket_luan", ("KL", 244, "Người tuổi Quí Mão, Can Quí (Thủy) sinh Chi Mão (Mộc), tương sinh"),
     "thanh", {"@kl_44_62": "bi_pha"}, "tong_the"),
    ("mau_ty_pha_san", F + "NHAT_NGUYET_TINH_MINH", "phu_dinh", ("KL", 245, "Lá số phá sản Âm dương lạc hãm cung Mệnh"),
     "bi_pha", {"@kl_53_68": "bi_pha"}, "ten"),
    ("mau_ty_pha_san", F + "CO_NGUYET_DONG_LUONG", "phu_dinh", ("KL", 246, "bởi cách Thiên cơ Hóa kỵ gặp Hỏa Linh đốt cháy ra tro"),
     "thanh_thuong", {"@tt_24": "bi_pha", "@kl_221": "thanh_thuong"}, "ten"),
]


def direction(state):
    return "thuan" if state in ("thanh", "thanh_thuong") else "han_che" if state == "bi_pha" else "trung" if state in ("hinh_thuc", "pha_duoc_cuu") else "khong_hien"


def verdict(book_says, state):
    d = direction(state)
    if book_says == "khong_ket_luan":
        return "sach_khong_xet"
    if d in ("trung", "khong_hien"):
        return "khong_quyet_dinh"
    return "khop" if (book_says == "xac_nhan") == (d == "thuan") else "khong_khop"
