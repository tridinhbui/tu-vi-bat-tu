from types import SimpleNamespace as NS

from tvbt import van_han_tt as vt

NAMES = ["Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch", "Quan Lộc", "Nô Bộc", "Thiên Di", "Tật Ách", "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ"]
BR = "Tý Sửu Dần Mão Thìn Tỵ Ngọ Mùi Thân Dậu Tuất Hợi".split()


def chart(van, van_branch=4, tu_hoa=None, others=None):
    pal = [{"name": n, "branch_index": i, "branch": BR[i], "stars": [], "major_stars": [], "major_dignity": {}, "minor_dignity": {}} for i, n in enumerate(NAMES)]
    v = pal[van_branch]
    v["major_stars"] = van.get("major", [])
    v["stars"] = van.get("major", []) + van.get("aux", [])
    v["major_dignity"] = van.get("dig", {})
    for i, st in (others or {}).items():
        pal[i]["stars"] = st
    return NS(palaces=pal, tu_hoa=tu_hoa or {}), v


def texts(*a, **k):
    tv, v = chart(*a, **k)
    return " ".join(x["text"] for x in vt.read(tv, v))


def test_good_and_hard_readings_follow_brightness():
    assert "tiền tài tấn nghiệp" in texts({"major": ["Thái Dương"], "dig": {"Thái Dương": "miếu"}})
    t = texts({"major": ["Thái Dương"], "dig": {"Thái Dương": "hãm"}}, tu_hoa={"Hóa Kỵ": {"star": "Thái Dương", "branch": 4}})
    assert "hao tài" in t and "tiền tài tấn nghiệp" not in t
    assert "tiền tài tấn nghiệp" not in texts({"major": ["Thái Dương"], "dig": {"Thái Dương": "hãm"}})


def test_tu_vi_with_sat_pha_tham_in_tam_phuong_and_tu_hoa_readings():
    t = texts({"major": ["Tử Vi"]}, others={0: ["Phá Quân"]})            # branch 0 is in the tam phương of branch 4
    assert "bị giáng" in t
    assert "dựng nghiệp mới" in texts({"major": ["Vũ Khúc"]}, tu_hoa={"Hóa Quyền": {"star": "Vũ Khúc", "branch": 4}})
    assert "mất chức" in texts({"major": ["Thiên Đồng"], "dig": {"Thiên Đồng": "hãm"}}, others={0: ["Kình Dương"]})
    assert texts({"major": ["Cự Môn"]}) == ""                              # stars without a verse here produce nothing
