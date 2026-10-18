"""Topic / aspect / valence taxonomy. Valence and aspect are HEURISTIC labels read off claim slugs; they only decide how findings are grouped and
displayed, never a score. Every table here is explicit so it can be reviewed."""
from __future__ import annotations

CHAPTERS = [
    ("tong_quan", "Tổng quan"), ("ban_menh", "Bản Mệnh"), ("tinh_cach", "Tính cách"), ("cong_danh", "Công danh"),
    ("tai_bach", "Tài Bạch"), ("quan_he", "Quan hệ"), ("dai_han_luu_nien", "Đại hạn & lưu niên"), ("cach_cuc", "Cách cục"),
    ("muoi_hai_cung", "12 cung"), ("chuyen_sau", "Luận giải chuyên sâu"),
]

# primary chapter of a palace (a finding is told in ONE chapter; other chapters only point to it)
PALACE_CHAPTER = {"Mệnh": "ban_menh", "Phúc Đức": "tinh_cach", "Quan Lộc": "cong_danh", "Tài Bạch": "tai_bach", "Điền Trạch": "tai_bach",
                  "Phu Thê": "quan_he", "Nô Bộc": "quan_he", "Tử Tức": "quan_he", "Huynh Đệ": "quan_he", "Phụ Mẫu": "quan_he",
                  "Thiên Di": "muoi_hai_cung", "Tật Ách": "muoi_hai_cung"}

# aspect keyword table, checked in order on the claim slug
ASPECT_KEYS = [("tai", ("tai", "loc", "giau", "tien", "kinh_doanh", "phu_quy", "ban_hang")),
               ("danh", ("quan", "danh", "chuc", "cong", "uy", "quyen", "vinh", "khoa_cu", "cong_chuc")),
               ("tri", ("thong_minh", "van_chuong", "hoc", "muu", "tri", "nghe")),
               ("hon_nhan", ("hon", "vo_chong", "phoi", "gia_dao", "tinh_duyen")),
               ("tinh", ("nhan_hau", "nong", "hien", "tinh", "thang_than", "nghiem", "gian", "hay_")),
               ("suc_khoe", ("benh", "tat", "sau_bi", "thuong")),
               ("tuoi_tho", ("tho_", "yeu"))]
POS = ("tot", "cat", "vinh", "phu_quy", "hien", "thanh", "thuan", "thong_minh", "uy_", "quyen_quy", "phuc", "nhan_hau", "thang", "dac", "sang")
NEG = ("ham", "kho", "lao", "tan", "hung", "tru_tr", "tranh_cai", "tre", "lo_toan", "thi_phi", "bi_quan", "khong_kiep", "xa_que", "sat", "ky", "tuan_triet_xa", "trac_tro", "yem_the", "phieu", "dang_ngan")
# claims that mention a rescue/limit pair are often 'tot_tuan_triet': Tuần/Triệt flips them, so they stay un-valenced
AMBIG = ("tuan_triet",)

# claims that are classification labels, not readings
LABEL_PREFIX = ("menh_nhom_", "cach_")

# the 14 chính tinh, used to anchor findings
MAJORS = ["Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh", "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn",
          "Thiên Tướng", "Thiên Lương", "Thất Sát", "Phá Quân"]


def _has(claim: str, keys) -> bool:
    toks = claim.split("_")
    for k in keys:
        k = k.strip("_")
        if "_" in k:
            if f"_{k}_" in f"_{claim}_":
                return True
        elif any(t == k or (len(k) >= 4 and t.startswith(k)) for t in toks):
            return True
    return False


def aspect_of(claim: str, palace: str | None) -> str:
    if claim.startswith(LABEL_PREFIX):
        return "nhan_dien"
    for asp, keys in ASPECT_KEYS:
        if _has(claim, keys):
            return asp
    return {"Tài Bạch": "tai", "Điền Trạch": "tai", "Quan Lộc": "danh", "Phu Thê": "hon_nhan", "Tật Ách": "suc_khoe"}.get(palace or "", "tong_hop")


def valence_of(claim: str) -> str:
    """'thuan' | 'nghich' | 'khong_ro'. Heuristic on the slug; ambiguous or mixed slugs stay 'khong_ro' and are never treated as a conflict side."""
    if _has(claim, AMBIG):
        return "khong_ro"
    p, n = _has(claim, POS), _has(claim, NEG)
    return "khong_ro" if p == n else ("thuan" if p else "nghich")


def chapter_of(subject: str, aspect: str) -> str:
    if subject == "chart":
        return "cach_cuc"
    pal = subject.split(":", 1)[1]
    base = PALACE_CHAPTER.get(pal, "muoi_hai_cung")
    if pal == "Mệnh":
        return {"tinh": "tinh_cach", "tri": "tinh_cach", "tai": "tai_bach", "danh": "cong_danh"}.get(aspect, "ban_menh")
    return base
