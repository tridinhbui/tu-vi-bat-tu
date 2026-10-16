"""Lưu niên thập nhị thần (串宫十二神), 八字真宗 pp.39-42: the twelve gods are laid on the twelve branches starting from the flow-year branch
(Thái Tuế = no.1) and each of the seven pillar branches (year, month, day, hour, thai nguyên, mệnh cung, thân cung) takes the god it falls on;
stems take the god of their 'borrowed branch' (天干寄支: Giáp-Dần, Ất-Mão, Bính-Tỵ, Đinh-Ngọ, Mậu-Tuất, Kỷ-Sửu, Canh-Thân, Tân-Dậu, Nhâm-Hợi, Quý-Tý).
The luck pillar's god is 'the root of the year' (p.42 note 3). The glosses paraphrase the book's verses; disease/death wording of Tang Môn, Điếu Khách,
Bệnh Phù and Bạch Hổ is deliberately softened to 'buồn phiền, bất an' and no event is asserted. Pairing with auspicious stars (配吉星) is NOT evaluated."""
from __future__ import annotations

from .bazi import BaziChart
from .ganzhi import BRANCHES_VI, STEMS_VI

GODS = [  # name, rating (tot / trung / xau_nho / xau_lon), gloss, categories (the book's 十二神归类)
    ("Thái Tuế", "trung", "phiền tâm, việc dễ không thuận, lời ra tiếng vào, tiền của dễ hao", []),
    ("Thanh Long", "tot", "hỷ thần: làm việc gặp quý nhân, tin vui, phúc lộc", ["quý nhân", "sự nghiệp", "kinh động/xa nhà", "hôn nhân", "văn bằng"]),
    ("Tang Môn", "xau_lon", "sao buồn phiền, lo âu, dễ có chuyện không vui", ["hao tài", "tiểu nhân"]),
    ("Lục Hợp", "tot", "hợp hòa, hỷ sự: người đã lập gia đình có tin vui về con, người chưa có dễ gặp duyên", ["quý nhân", "tài vận", "hôn nhân", "văn bằng", "con cái"]),
    ("Quan Phù", "xau_nho", "vừa có hỷ (hồng loan) vừa có thị phi, thủ tục, bị cản trở trong việc cần có người can thiệp", ["sự nghiệp", "tài vận", "hôn nhân"]),
    ("Tiểu Hao", "xau_nho", "đảo điên, chịu thiệt mà không được lòng, tiền bạc dễ hao, thị phi phiền não", ["hao tài", "con cái"]),
    ("Đại Hao", "xau_lon", "không tốt lành: hao tài, tiểu nhân trở mặt", ["hao tài"]),
    ("Chu Tước", "xau_lon", "thị phi nhiều, tiểu nhân gây rắc rối, có oan khó phân giải", ["tiểu nhân", "quan tụng"]),
    ("Bạch Hổ", "xau_lon", "hay gặp trắc trở, tiền của thất thoát, nhiều việc khó khăn", ["kinh động/xa nhà"]),
    ("Quý Thần", "tot", "trăm việc hanh thông, quý nhân giúp đỡ khắp nơi, người và của đều vượng", ["quý nhân", "sự nghiệp", "hôn nhân"]),
    ("Điếu Khách", "xau_nho", "nhiều thị phi, tiểu nhân gây chuyện, mọi việc kém thuận", ["tiểu nhân", "kinh động/xa nhà"]),
    ("Bệnh Phù", "xau_nho", "làm việc không thuận tâm, phiền não, bất an trong lòng", []),
]
RATING_VI = {"tot": "cát", "trung": "trung tính", "xau_nho": "hung nhỏ", "xau_lon": "hung lớn"}
STEM_BORROW = {0: 2, 1: 3, 2: 5, 3: 6, 4: 10, 5: 1, 6: 8, 7: 9, 8: 11, 9: 0}          # stem index -> borrowed branch index (p.40)
SRC = "八字真宗 pp.39-42"


def god_of(branch: int, year_branch: int) -> dict:
    n = (branch - year_branch) % 12
    name, rating, gloss, cats = GODS[n]
    return {"no": n + 1, "god": name, "rating": rating, "rating_vi": RATING_VI[rating], "gloss": gloss, "categories": cats}


def _branch_of(gz: str) -> int:
    return BRANCHES_VI.index(gz.split()[1])


def twelve_gods(chart: BaziChart, year_branch: int, luck_name: str | None) -> dict:
    """year_branch: branch index of the flow year (Thái Tuế). luck_name: current đại vận pillar name or None."""
    cols = {}
    for key, label in (("year", "năm"), ("month", "tháng"), ("day", "ngày"), ("hour", "giờ")):
        p = chart.pillars[key]
        cols[key] = {"label": f"trụ {label}", "pillar": f"{STEMS_VI[p.stem]} {BRANCHES_VI[p.branch]}", "branch_god": god_of(p.branch, year_branch),
                     "stem_god": god_of(STEM_BORROW[p.stem], year_branch)}
    for key, label in (("thai_yuan", "thai nguyên"), ("ming_gong", "mệnh cung"), ("shen_gong", "thân cung")):
        gz = chart.extras[key]
        cols[key] = {"label": label, "pillar": gz, "branch_god": god_of(_branch_of(gz), year_branch)}
    out = {"flow_year_branch": BRANCHES_VI[year_branch], "columns": cols, "source": SRC, "luck": None}
    if luck_name:
        lb = _branch_of(luck_name)
        ls = STEMS_VI.index(luck_name.split()[0])
        out["luck"] = {"pillar": luck_name, "branch_god": god_of(lb, year_branch), "stem_god": god_of(STEM_BORROW[ls], year_branch),
                       "note": "Thần ở trụ đại vận là gốc của cả năm: nếu là hung thì cả năm kém thuận dù có sao tốt (p.42, ghi chú 3)"}
    gods = [c["branch_god"] for c in cols.values()]
    tally = {r: sum(1 for g in gods if g["rating"] == r) for r in RATING_VI}
    out["tally"] = {RATING_VI[r]: n for r, n in tally.items()}
    cats: dict[str, list[str]] = {}
    for key, c in cols.items():
        for cat in c["branch_god"]["categories"]:
            cats.setdefault(cat, []).append(f"{c['label']} ({c['branch_god']['god']})")
    out["categories"] = cats
    out["caveats"] = ["Sách đòi xét thêm 'phối cát tinh/hung tinh' và 'bị cái đầu' (盖头) trong cùng trụ: hệ thống chưa xét, nên đây chỉ là xu hướng.",
                      "Chỉ thần ở chi của bảy trụ và ở đại vận được dùng; thiên can và địa chi của lưu niên không mang thần (chỉ dùng làm Thái Tuế)."]
    return out
