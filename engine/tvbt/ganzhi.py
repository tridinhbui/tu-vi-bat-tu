"""Heavenly Stems / Earthly Branches primitives. Pure data + pure functions."""
from __future__ import annotations

STEMS_VI = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
STEMS_HAN = list("甲乙丙丁戊己庚辛壬癸")
BRANCHES_VI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
BRANCHES_HAN = list("子丑寅卯辰巳午未申酉戌亥")

ELEMENTS = ["Mộc", "Hỏa", "Thổ", "Kim", "Thủy"]  # generating order
STEM_ELEMENT = ["Mộc", "Mộc", "Hỏa", "Hỏa", "Thổ", "Thổ", "Kim", "Kim", "Thủy", "Thủy"]
BRANCH_ELEMENT = ["Thủy", "Thổ", "Mộc", "Mộc", "Thổ", "Hỏa", "Hỏa", "Thổ", "Kim", "Kim", "Thổ", "Thủy"]


def stem_polarity(stem: int) -> str:
    return "dương" if stem % 2 == 0 else "âm"


def branch_polarity(branch: int) -> str:
    return "dương" if branch % 2 == 0 else "âm"


def cycle_index(stem: int, branch: int) -> int:
    """Index 0..59 in the sexagenary cycle (Giáp Tý = 0). Stem/branch parity must match."""
    if stem % 2 != branch % 2:
        raise ValueError(f"invalid stem/branch pair {stem},{branch}")
    for n in range(60):
        if n % 10 == stem and n % 12 == branch:
            return n
    raise ValueError("unreachable")


def from_cycle(n: int) -> tuple[int, int]:
    return n % 10, n % 12


def gz_name(stem: int, branch: int) -> str:
    return f"{STEMS_VI[stem]} {BRANCHES_VI[branch]}"


def generates(a: str, b: str) -> bool:
    return ELEMENTS.index(b) == (ELEMENTS.index(a) + 1) % 5


def controls(a: str, b: str) -> bool:
    return ELEMENTS.index(b) == (ELEMENTS.index(a) + 2) % 5


def year_cycle_index(year: int) -> int:
    """Cycle index of a (lunar or solar-term) year number. 4 CE = Giáp Tý."""
    return (year - 4) % 60


def tiger_month_stem(year_stem: int) -> int:
    """Stem of the Dần month/palace for a given year stem (五虎遁)."""
    return [2, 4, 6, 8, 0][year_stem % 5]


def branch_stem_from_year(year_stem: int, branch: int) -> int:
    """Stem assigned to month/palace `branch` counting from Dần (五虎遁)."""
    return (tiger_month_stem(year_stem) + (branch - 2) % 12) % 10


def nap_am_element(stem: int, branch: int) -> str:
    """Nạp âm element via the classical stem-value + branch-value method."""
    sv = {0: 1, 1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 4, 7: 4, 8: 5, 9: 5}[stem]
    bv = {0: 0, 1: 0, 6: 0, 7: 0, 2: 1, 3: 1, 8: 1, 9: 1, 4: 2, 5: 2, 10: 2, 11: 2}[branch]
    s = sv + bv
    if s > 5:
        s -= 5
    return {1: "Kim", 2: "Thủy", 3: "Hỏa", 4: "Thổ", 5: "Mộc"}[s]


# Independent reference: 30 named nạp âm, index = cycle_index // 2
NAP_AM_NAMES = [
    ("Hải Trung Kim", "Kim"), ("Lư Trung Hỏa", "Hỏa"), ("Đại Lâm Mộc", "Mộc"), ("Lộ Bàng Thổ", "Thổ"),
    ("Kiếm Phong Kim", "Kim"), ("Sơn Đầu Hỏa", "Hỏa"), ("Giản Hạ Thủy", "Thủy"), ("Thành Đầu Thổ", "Thổ"),
    ("Bạch Lạp Kim", "Kim"), ("Dương Liễu Mộc", "Mộc"), ("Tuyền Trung Thủy", "Thủy"), ("Ốc Thượng Thổ", "Thổ"),
    ("Tích Lịch Hỏa", "Hỏa"), ("Tùng Bách Mộc", "Mộc"), ("Trường Lưu Thủy", "Thủy"), ("Sa Trung Kim", "Kim"),
    ("Sơn Hạ Hỏa", "Hỏa"), ("Bình Địa Mộc", "Mộc"), ("Bích Thượng Thổ", "Thổ"), ("Kim Bạch Kim", "Kim"),
    ("Phú Đăng Hỏa", "Hỏa"), ("Thiên Hà Thủy", "Thủy"), ("Đại Dịch Thổ", "Thổ"), ("Thoa Xuyến Kim", "Kim"),
    ("Tang Đố Mộc", "Mộc"), ("Đại Khê Thủy", "Thủy"), ("Sa Trung Thổ", "Thổ"), ("Thiên Thượng Hỏa", "Hỏa"),
    ("Thạch Lựu Mộc", "Mộc"), ("Đại Hải Thủy", "Thủy"),
]


def nap_am_name(stem: int, branch: int) -> str:
    return NAP_AM_NAMES[cycle_index(stem, branch) // 2][0]
