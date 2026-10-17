"""'Nhập hạn ca' of Tử Vi Đẩu Số Toàn Thư pp.97-105 as sentences about a vận palace (đại hạn or tiểu hạn). Each star's entry has a good reading (the star
bright in the palace, or with the companions the verse names) and a hard reading (star dim, with sát tinh / Hóa Kỵ). Paraphrased; the verses' death,
injury, disease and prison outcomes are softened to 'khó khăn, hao tài, tranh chấp'. Nothing says an event WILL happen.
Standalone on purpose: it reads only the chart palaces, so it can be called next to van_han.read without touching that module."""
from __future__ import annotations

SRC = "Toàn Thư pp.97-105"
GOOD = {"miếu", "vượng", "đắc"}
SAT = ("Kình Dương", "Đà La", "Địa Không", "Địa Kiếp", "Hỏa Tinh", "Linh Tinh")
CAT = ("Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt")


def _level(v: dict, star: str):
    return {**v.get("minor_dignity", {}), **v.get("major_dignity", {})}.get(star)


def read(tv, v: dict) -> list[dict]:
    """tv: TuViChart (or an object with .palaces and .tu_hoa); v: the vận palace dict."""
    stars = set(v["stars"])
    majors = set(v["major_stars"])
    hoa = {k for k, x in tv.tu_hoa.items() if x.get("branch") == v["branch_index"]}
    by_b = {p["branch_index"]: p for p in tv.palaces}
    b = v["branch_index"]
    tam = {(b + d) % 12 for d in (0, 4, 8, 6)}
    tp_stars = {s for i in tam for s in by_b[i]["stars"]}
    tp_hoa = {k for k, x in tv.tu_hoa.items() if x.get("branch") in tam}
    sat_tp = [s for s in SAT if s in tp_stars]
    cat_tp = [s for s in CAT if s in tp_stars]
    out: list[dict] = []

    def add(t):
        out.append({"text": t, "src": SRC})

    def lv(s):
        return _level(v, s)

    star = lambda s: s in majors
    good = lambda s: lv(s) in GOOD
    dim = lambda s: lv(s) == "hãm"

    if star("Tử Vi"):
        add("Hạn đến Tử Vi ở thế đẹp, nhiều sao tốt: phúc lộc đầy đủ, người thường kiếm thêm tiền, người có chức dễ thăng tiến.")
        if tp_stars & {"Thất Sát", "Phá Quân", "Tham Lang"}:
            add("Tử Vi nhập hạn nhưng tam phương có Thất Sát, Phá Quân hoặc Tham Lang: người thường kém thuận lợi, người có chức dễ bị giáng.")
    if star("Thiên Cơ"):
        if hoa & {"Hóa Khoa", "Hóa Quyền", "Hóa Lộc"}:
            add("Hạn Thiên Cơ gặp Khoa, Quyền hoặc Lộc: ra vào làm ăn, kinh doanh được quý nhân giúp đỡ, vinh hiển.")
        else:
            add("Hạn Thiên Cơ: cuộc sống kém yên ổn, việc nhà rối rắm, việc bên ngoài nhiều.")
    if star("Thái Dương"):
        if good("Thái Dương"):
            add("Hạn Thái Dương đắc địa: tiền tài tấn nghiệp, vợ chồng hòa hợp, người đi học hay làm công chức dễ hiển đạt.")
        elif dim("Thái Dương") and (sat_tp or "Hóa Kỵ" in hoa):
            add("Hạn Thái Dương hãm địa lại gặp sát tinh hoặc Hóa Kỵ: việc dễ hỏng, hao tài.")
    if star("Vũ Khúc"):
        if good("Vũ Khúc"):
            add("Hạn Vũ Khúc nhập miếu: tiền tài hưng vượng" + ("; thêm Văn Xương, Tả Hữu thì phúc lộc song toàn." if stars & {"Văn Xương", "Tả Phụ", "Hữu Bật"} else "."))
        if "Hóa Quyền" in hoa:
            add("Hạn Vũ Khúc có Hóa Quyền: cầu mưu việc gì cũng dễ thành.")
        if dim("Vũ Khúc"):
            add("Hạn Vũ Khúc hãm địa: người làm công chức dễ gặp rắc rối pháp lý, dân thường dễ mắc nợ.")
    if star("Thiên Đồng"):
        if good("Thiên Đồng"):
            add("Hạn Thiên Đồng đắc địa: hỷ khí đầy cửa, tài lộc phát đạt, nên gây dựng việc mới, gia đạo hạnh phúc.")
        elif dim("Thiên Đồng") and sat_tp:
            add("Hạn Thiên Đồng hãm địa gặp sát tinh: làm việc đầu tốt cuối hỏng, dễ mất chức, nợ nần.")
    if star("Liêm Trinh") and good("Liêm Trinh") and cat_tp:
        add("Hạn Liêm Trinh ở thế vượng có cát tinh phò trợ: tiền của tự nhiên tích súc, mưu cầu thăng chức dễ thành.")
    if star("Thiên Phủ"):
        add("Hạn Thiên Phủ: chủ về tài lộc, thêm tiền thêm mừng, thuận cho việc xây dựng nhà cửa" +
            ("; có đủ Khoa, Quyền, Lộc thì có thể định ngày phát triển tài năng." if {"Hóa Khoa", "Hóa Quyền", "Hóa Lộc"} <= tp_hoa else "."))
    if star("Thái Âm"):
        if good("Thái Âm"):
            add("Hạn Thái Âm: tài lộc phong phú, trăm việc hanh thông, lập gia đình hay thêm con, nhà cửa hưng vượng" +
                ("; có Hỏa, Linh thì vẫn vướng rắc rối." if stars & {"Hỏa Tinh", "Linh Tinh"} else "."))
        elif dim("Thái Âm") and sat_tp:
            add("Hạn Thái Âm hãm địa gặp Dương, Đà, Linh, Hỏa: rất bất lợi, nhiều khó khăn.")
    if star("Tham Lang"):
        if good("Tham Lang"):
            add("Hạn Tham Lang miếu vượng: mọi việc hài hòa" + ("; có Khoa, Lộc thì thành tựu, dễ hoạnh phát." if hoa & {"Hóa Khoa", "Hóa Lộc"} else "."))
        if v["branch"] in ("Thìn", "Tuất", "Sửu", "Mùi") and "Hỏa Tinh" in stars:
            add("Hạn Tham Lang ở Tứ mộ gặp Hỏa Tinh: có thể hoạnh phát, phú quý nổi tiếng trong vùng.")
        if dim("Tham Lang"):
            add("Hạn Tham Lang hãm địa: nên tiết chế ham muốn, chơi bời dễ hao tài.")
    if star("Phá Quân"):
        if good("Phá Quân"):
            add("Hạn Phá Quân miếu địa: phúc lộc dồi dào" + ("; thêm Xương, Khôi, Việt thì cuộc sống phong quang." if stars & {"Văn Xương", "Thiên Khôi", "Thiên Việt"} else "."))
        elif dim("Phá Quân") or sat_tp:
            add("Hạn Phá Quân gặp sát tinh: dễ thất thoát, hao tài.")
    if "Lộc Tồn" in stars:
        add("Hạn Lộc Tồn: rất tốt, mưu sự hay, người có chức dễ chuyển chức, người thường phát tài; cũng là hạn thuận cho hôn nhân, con cái.")
    if "Kình Dương" in stars and v["branch"] in ("Thìn", "Tuất", "Sửu", "Mùi"):
        add("Hạn Kình Dương ở Tứ mộ: ít sợ họa; có Tử Vi, Văn Xương, Thiên Phủ thì tài và quan đều hiển đạt.")
    if "Hỏa Tinh" in stars:
        if good("Hỏa Tinh"):
            add("Hạn Hỏa Tinh đắc địa: rất tốt, làm quan dễ thăng chức, buôn bán phát tài.")
        elif dim("Hỏa Tinh"):
            add("Hạn Hỏa Tinh hãm địa: dễ gặp việc bất ngờ, tiền bạc gian khó.")
    if "Linh Tinh" in stars and star("Tham Lang"):
        add("Hạn Linh Tinh gặp Tham Lang: có thể phú quý nổi danh.")
    if "Thiên Mã" in stars and (majors & {"Tử Vi", "Thiên Phủ"} or "Lộc Tồn" in stars):
        add("Hạn Thiên Mã gặp Tử, Phủ hoặc Lộc Tồn: rất tốt, người có chức càng hiển đạt, học trò dễ đỗ đạt.")
    if "Hóa Lộc" in hoa:
        add("Hạn Hóa Lộc: dễ có địa vị, tiền bạc tự nhiên súc tích, làm ăn phát đạt.")
    if "Hóa Quyền" in hoa:
        add("Hạn Hóa Quyền: quan lộc cao thăng, tài bạch thêm, có thể dựng nghiệp mới, gia đạo an khang" +
            ("; gặp Vũ Khúc, Tham Lang thì làm việc gì cũng trót lọt." if majors & {"Vũ Khúc", "Tham Lang"} else "."))
    if "Hóa Khoa" in hoa and "Văn Xương" in stars:
        add("Hạn Hóa Khoa gặp Văn Xương: người đi học đỗ đạt nổi danh, trăm việc dễ thành.")
    if "Hóa Kỵ" in hoa:
        if sat_tp:
            add("Hạn Hóa Kỵ gặp sát tinh: tiền tài dễ tan, có thể mất chức, nhiều trở ngại.")
        else:
            add("Hạn Hóa Kỵ: việc tiến thoái vô thường, công danh khó toại.")
    return out
