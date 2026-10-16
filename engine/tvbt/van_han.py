"""Reading of a 'vận' palace (đại hạn or tiểu hạn) after Tử Vi Khảo Luận pp.233-236.
The book's idea: the stars of the vận palace are the events/people waiting at the door; the person brings the Mệnh stars to stay
among them, so the useful question is how the Mệnh configuration meets the vận configuration. Facts in, sourced sentences out;
nothing here says an event WILL happen."""
from __future__ import annotations

from .tuvi import TuViChart

SRC = "Khảo Luận pp.233-236"
SAT4 = ("Kình Dương", "Đà La", "Địa Không", "Địa Kiếp", "Hỏa Tinh", "Linh Tinh")
GROUPS = {
    "tu_phu_vu_tuong": ("Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"),
    "sat_pha_tham": ("Thất Sát", "Phá Quân", "Tham Lang"),
    "co_nguyet_dong_luong": ("Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"),
}
STAGE_THUAN = {"Mệnh": "tuổi thơ", "Phụ Mẫu": "tuổi thanh thiếu niên", "Phúc Đức": "tuổi thành niên", "Điền Trạch": "tuổi thành danh",
               "Quan Lộc": "tuổi nổi danh", "Nô Bộc": "tuổi già", "Thiên Di": "tuổi nghỉ ngơi"}
STAGE_NGHICH = {"Mệnh": "tuổi thơ", "Huynh Đệ": "tuổi thanh thiếu niên", "Phu Thê": "tuổi thành niên", "Tử Tức": "tuổi thành danh",
                "Tài Bạch": "tuổi nổi danh", "Thiên Di": "tuổi nghỉ ngơi"}
DOMAIN = {"Mệnh": "chính mình", "Phụ Mẫu": "cha mẹ, người bề trên", "Phúc Đức": "đời sống tinh thần, họ hàng", "Điền Trạch": "nhà cửa, đất đai",
          "Quan Lộc": "công danh, sự nghiệp", "Nô Bộc": "bạn bè, người cộng tác", "Thiên Di": "giao thiệp bên ngoài, đi xa", "Tật Ách": "thể trạng",
          "Tài Bạch": "tiền bạc", "Tử Tức": "con cái", "Phu Thê": "hôn nhân", "Huynh Đệ": "anh chị em"}
SAT_POS = {"Thất Sát": [(("Dần", "Thân"), "muôn sự dễ thành"), (("Mão", "Dậu"), "muôn sự dở dang")],
           "Phá Quân": [(("Tý", "Ngọ"), "bạn bè đông đủ"), (("Mão", "Dậu"), "cô đơn, lẻ bóng")],
           "Tham Lang": [(("Thìn", "Tuất", "Mùi"), "giàu sang hiển hách"), (("Tý", "Ngọ", "Mão", "Dậu"), "hao tài, phóng túng")]}


def _stars(p) -> set[str]:
    return set(p["stars"])


def _has_group(p, g) -> bool:
    return any(s in p["major_stars"] for s in GROUPS[g])


def life_stage(direction: str, palace: str) -> str | None:
    return (STAGE_THUAN if direction == "thuận" else STAGE_NGHICH).get(palace)


def read(tv: TuViChart, van_palace: str) -> list[dict]:
    """Sentences about how the Mệnh palace meets the given vận palace."""
    by_n = {p["name"]: p for p in tv.palaces}
    m, v = by_n["Mệnh"], by_n[van_palace]
    vs = _stars(v)
    out: list[dict] = []

    def add(t):
        out.append({"text": t, "src": SRC})

    if van_palace == "Mệnh":
        joined = " ".join(o["text"] for o in out)
    if "đi lên" in joined and "đi xuống" in joined:
        out.append({"text": "Hai điều kiện trái chiều của sách (đi lên và đi xuống) cùng khớp, nên hệ thống không kết luận hạn này đi lên hay đi xuống.", "src": SRC})
    return out
    sat_in = [s for s in SAT4 if s in vs]
    if _has_group(m, "tu_phu_vu_tuong"):
        if sat_in:
            add(f"Mệnh có Tử Phủ Vũ Tướng mà cung vận có {', '.join(sat_in)}: theo sách đây lại là dịp đi lên.")
        if _has_group(v, "co_nguyet_dong_luong") or any(s in v["major_stars"] for s in ("Tử Vi", "Thiên Phủ")):
            add("Mệnh có Tử Phủ Vũ Tướng gặp cung vận có Cơ Nguyệt Đồng Lương hoặc Tử Phủ: theo sách là thế đi xuống.")
    if not m["major_stars"] and _has_group(v, "sat_pha_tham"):
        add("Mệnh vô chính diệu gặp cung vận có Sát Phá Tham: theo sách là dịp đi lên, như người thất nghiệp lâu ngày có việc thực tế.")
    if (m["tuan"] and v["triet"]) or (m["triet"] and v["tuan"]):
        add("Mệnh bị Tuần mà vận có Triệt (hoặc ngược lại): theo sách như được tháo cũi xổ lồng.")
    if "Thái Dương" in m["major_stars"] or "Thái Âm" in m["major_stars"]:
        pass
    if "Thái Dương" in m["major_stars"] and "Thái Âm" in m["major_stars"]:
        if {"Đào Hoa", "Hồng Loan", "Thiên Hỷ"} & vs:
            add("Mệnh có Nhật Nguyệt cần vận có Đào, Hồng, Hỷ mới khá được phần nào: cung vận này có.")
        elif sat_in and any(s in ("Kình Dương", "Đà La") for s in sat_in):
            add("Mệnh có Nhật Nguyệt mà vận gặp Kình, Đà thì theo sách càng tồi hơn.")
    if "Cự Môn" in m["major_stars"] and "Thái Dương" in m["major_stars"] and _has_group(v, "sat_pha_tham"):
        add("Mệnh có Cự Nhật cần vận có Sát Phá Tham mới là dịp làm nên sự nghiệp lớn: cung vận này có.")
    if _has_group(m, "co_nguyet_dong_luong"):
        good = [s for s in ("Văn Xương", "Văn Khúc") if s in vs] + [h for h in ("Hóa Khoa", "Hóa Quyền", "Hóa Lộc") if h in {x["star"] for x in []}]
        tu_hoa_here = [k for k, x in tv.tu_hoa.items() if x["branch"] == v["branch_index"] and k in ("Hóa Khoa", "Hóa Quyền", "Hóa Lộc")]
        if good or tu_hoa_here:
            add(f"Mệnh có Cơ Nguyệt Đồng Lương cần vận có Xương Khúc, Khoa Quyền Lộc thì có địa vị, tài lộc: cung vận có {', '.join(good + tu_hoa_here)}.")
        if any(s in vs for s in ("Kình Dương", "Đà La", "Địa Không", "Địa Kiếp")):
            add("Mệnh có Cơ Nguyệt Đồng Lương mà vận gặp Kình, Đà, Không, Kiếp: theo sách dễ trắng tay.")
    if all(s in m["major_stars"] for s in ("Vũ Khúc", "Thiên Tướng")):
        if any(s in v["major_stars"] for s in ("Tử Vi", "Thiên Phủ")):
            add("Mệnh có Vũ Tướng gặp vận Tử Phủ: theo sách là một bước lên quan.")
        if _has_group(v, "sat_pha_tham"):
            add("Mệnh có Vũ Tướng gặp vận Sát Phá Tham: theo sách là giàu sang chóng vánh.")
    # the three big luck-bringing positions
    if "Thái Tuế" in vs:
        t = []
        if any(s in vs for s in ("Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt")):
            t.append("gặp Xương Khúc hoặc Khôi Việt thì tài lộc công danh rực rỡ")
        if any(s in vs for s in ("Đà La",)) or any(x["star"] and x["branch"] == v["branch_index"] for k, x in tv.tu_hoa.items() if k == "Hóa Kỵ"):
            t.append("gặp Đà, Kỵ thì dễ vướng thị phi, kiện tụng")
        add("Vận đến cung có Thái Tuế: sách xem là một trong ba vận lớn về công danh, mừng nhiều hơn lo" + (": " + "; ".join(t) if t else "") + ".")
    if "Quan Phù" in vs:
        t = []
        if "Văn Xương" in vs or "Văn Khúc" in vs:
            t.append("gặp Xương Khúc thì công danh đến dễ")
        if "Liêm Trinh" in v["major_stars"] and any(x["branch"] == v["branch_index"] for k, x in tv.tu_hoa.items() if k == "Hóa Kỵ"):
            t.append("gặp Liêm trinh hóa Kỵ thì dễ kiện tụng")
        add("Vận đến cung có Quan Phù: sách xem là vận để mong công danh" + (": " + "; ".join(t) if t else "") + ".")
    if "Bạch Hổ" in vs:
        t = ["gặp Tấu Thư, Phi Liêm thì giàu sang" ] if ("Tấu Thư" in vs or "Phi Liêm" in vs) else []
        add("Vận đến cung có Bạch Hổ: sách xem là vận cần can đảm dám làm dám chịu mới giàu sang uy quyền" + (": " + "; ".join(t) if t else "") + ".")
    # three big luck of wealth, by position
    for star, rules in SAT_POS.items():
        if star in v["major_stars"]:
            for branches, txt in rules:
                if v["branch"] in branches:
                    add(f"Vận có {star} ở {v['branch']}: theo sách {txt}.")
    joined = " ".join(o["text"] for o in out)
    if "đi lên" in joined and "đi xuống" in joined:
        out.append({"text": "Hai điều kiện trái chiều của sách (đi lên và đi xuống) cùng khớp, nên hệ thống không kết luận hạn này đi lên hay đi xuống.", "src": SRC})
    return out
