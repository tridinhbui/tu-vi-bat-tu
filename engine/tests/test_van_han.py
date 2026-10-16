from types import SimpleNamespace as NS

from tvbt import temporal, tuvi, van_han
from tvbt.calendar_core import BirthInput, normalize

NAMES = ["Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch", "Quan Lộc", "Nô Bộc", "Thiên Di", "Tật Ách", "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ"]
BR = "Tý Sửu Dần Mão Thìn Tỵ Ngọ Mùi Thân Dậu Tuất Hợi".split()


def fake(menh=None, van=None, van_name="Quan Lộc", van_branch=4, tu_hoa=None):
    pal = []
    for i, n in enumerate(NAMES):
        base = {"name": n, "branch_index": i, "branch": BR[i], "stars": [], "major_stars": [], "tuan": False, "triet": False}
        pal.append(base)
    m = pal[0]; v = next(p for p in pal if p["name"] == van_name); v["branch_index"] = van_branch; v["branch"] = BR[van_branch]
    for tgt, spec in ((m, menh or {}), (v, van or {})):
        tgt["major_stars"] = list(spec.get("major", [])); tgt["stars"] = list(spec.get("major", [])) + list(spec.get("aux", []))
        tgt["tuan"] = spec.get("tuan", False); tgt["triet"] = spec.get("triet", False)
    return NS(palaces=pal, tu_hoa=tu_hoa or {})


def texts(tv, name="Quan Lộc"):
    return " ".join(x["text"] for x in van_han.read(tv, name))


def test_book_conditions_pp234_235():
    t = texts(fake({"major": ["Tử Vi", "Thiên Phủ"]}, {"aux": ["Kình Dương"]}))
    assert "đi lên" in t
    assert "đi xuống" in texts(fake({"major": ["Tử Vi"]}, {"major": ["Thiên Cơ", "Thái Âm"]}))
    assert "đi lên" in texts(fake({}, {"major": ["Thất Sát"]}))                          # Mệnh vô chính diệu meets Sát Phá Tham
    assert "đi lên" not in texts(fake({"major": ["Vũ Khúc"]}, {"major": ["Thất Sát"]}))
    assert "tháo cũi" in texts(fake({"tuan": True}, {"triet": True}))
    assert "tháo cũi" not in texts(fake({"tuan": True}, {"tuan": True}))
    assert "một bước lên quan" in texts(fake({"major": ["Vũ Khúc", "Thiên Tướng"]}, {"major": ["Tử Vi"]}))
    assert "trắng tay" in texts(fake({"major": ["Thiên Cơ"]}, {"aux": ["Địa Kiếp"]}))
    assert van_han.read(fake({"major": ["Tử Vi"]}, {"aux": ["Kình Dương"]}), "Mệnh") == []        # vận palace == Mệnh: nothing to compare


def test_three_big_luck_and_position_rules_p235_236():
    assert "công danh" in texts(fake(van={"aux": ["Thái Tuế", "Văn Xương"]})) and "rực rỡ" in texts(fake(van={"aux": ["Thái Tuế", "Văn Xương"]}))
    assert "Quan Phù" in texts(fake(van={"aux": ["Quan Phù"]})) and "Bạch Hổ" in texts(fake(van={"aux": ["Bạch Hổ", "Tấu Thư"]}))
    assert "muôn sự dễ thành" in texts(fake(van={"major": ["Thất Sát"]}, van_branch=2))        # Dần
    assert "dở dang" in texts(fake(van={"major": ["Thất Sát"]}, van_branch=3))                # Mão
    assert "giàu sang hiển hách" in texts(fake(van={"major": ["Tham Lang"]}, van_branch=4))   # Thìn
    assert "hao tài" in texts(fake(van={"major": ["Tham Lang"]}, van_branch=0))               # Tý
    assert "cô đơn" in texts(fake(van={"major": ["Phá Quân"]}, van_branch=9))                  # Dậu


def test_life_stage_labels_p234_235():
    assert van_han.life_stage("thuận", "Điền Trạch") == "tuổi thành danh" and van_han.life_stage("nghịch", "Tài Bạch") == "tuổi nổi danh"
    assert van_han.life_stage("thuận", "Thiên Di") == van_han.life_stage("nghịch", "Thiên Di") == "tuổi nghỉ ngơi"
    assert van_han.life_stage("thuận", "Huynh Đệ") is None


def test_year_payload_has_tieu_han_and_lưu_tứ_hóa_reading():
    tv = tuvi.compute(normalize(BirthInput(1990, 5, 17, 10, 30, "Asia/Ho_Chi_Minh", "male")))
    y = temporal.tuvi_year(tv, 2024)                       # Giáp year: Liêm Lộc, Phá Quyền, Vũ Khoa, Dương Kỵ
    assert [x["star"] for x in y["luu_tu_hoa_reading"]] == ["Liêm Trinh", "Phá Quân", "Vũ Khúc", "Thái Dương"]
    assert all(x["advice"] for x in y["luu_tu_hoa_reading"]) and y["tieu_han_topic"]
    assert isinstance(y["tieu_han_reading"], list)


def test_conflicting_book_conditions_are_reported_not_resolved():
    t = texts(fake({"major": ["Tử Vi", "Thiên Phủ"]}, {"major": ["Tử Vi"], "aux": ["Kình Dương"]}))
    assert "đi lên" in t and "đi xuống" in t and "không kết luận" in t
