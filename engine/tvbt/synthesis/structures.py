"""Special-structure detectors (cấu trúc đặc biệt). Chart-agnostic: each detector reads positions, never a particular chart.

A Structure is a conditional argument, not a verdict: premises (checked), supports, limiters (breakers), rescuers, school variants, the sentence the
books actually give (`cites`) and an honest `verification` level:
  da_doi_chieu   every component the reading leans on has a verified pack rule with a page
  mot_phan       components have pages but the COMBINATION is not stated by a book (the engine only juxtaposes)
  chua_du_nguon  no book sentence found for this configuration; shown as a position fact only
This module never sets any rule to 'verified' and never picks between schools (see data/deep/conflict_matrix.json)."""
from __future__ import annotations

from dataclasses import dataclass, field

SAT = ["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"]
CAT = ["Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"]
TU_MO = ["Thìn", "Tuất", "Sửu", "Mùi"]
ORDER = ["Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch", "Quan Lộc", "Nô Bộc", "Thiên Di", "Tật Ách", "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ"]


@dataclass
class Structure:
    id: str
    name: str
    palaces: list[str]
    present: bool
    premises: list[dict] = field(default_factory=list)      # {"text", "ok"}
    supports: list[str] = field(default_factory=list)
    limiters: list[str] = field(default_factory=list)
    rescuers: list[str] = field(default_factory=list)
    variants: list[dict] = field(default_factory=list)      # school/scope readings, none preferred
    cites: list[str] = field(default_factory=list)
    verification: str = "chua_du_nguon"
    matrix_ids: list[str] = field(default_factory=list)
    reading: str = ""
    caveat: str = ""


class Geo:
    def __init__(self, palaces, tu_hoa, than_branch_name: str | None = None):
        self.ps = {p["name"]: p for p in palaces}
        self.by_b = {p["branch_index"]: p for p in palaces}
        self.hoa = tu_hoa
        self.hoa_at = {}
        for k, v in tu_hoa.items():
            self.hoa_at.setdefault(v["branch"], []).append(k)

    def opp(self, p):
        return self.by_b[(p["branch_index"] + 6) % 12]

    def tam_hop(self, p):
        return [self.by_b[(p["branch_index"] + d) % 12] for d in (4, 8)]

    def scope(self, p, kind="tam_phuong"):
        if kind == "dong_cung":
            return [p]
        if kind == "doi_cung":
            return [p, self.opp(p)]
        return [p, self.opp(p), *self.tam_hop(p)]

    def stars(self, ps):
        return [s for p in ps for s in p["stars"]]

    def hoa_in(self, ps):
        br = {p["branch_index"] for p in ps}
        return sorted(k for k, v in self.hoa.items() if v["branch"] in br)


def _tt(p):
    return ("Tuần" if p["tuan"] else "") + (" và " if p["tuan"] and p["triet"] else "") + ("Triệt" if p["triet"] else "")


def cu_mon_ham_hoa_loc(g: Geo) -> Structure:
    p = next((q for q in g.ps.values() if "Cự Môn" in q["major_stars"]), None)
    loc = g.hoa.get("Hóa Lộc", {})
    if not p or loc.get("star") != "Cự Môn":
        return Structure("CU_MON_HOA_LOC", "Cự Môn hóa Lộc", [], False)
    dig = p["major_dignity"].get("Cự Môn", "chưa rõ")
    ham = dig == "hãm"
    sc = g.scope(p)
    sat = [s for s in g.stars(sc) if s in SAT]
    ky = "Hóa Kỵ" in g.hoa_in(sc)
    s = Structure("CU_MON_HOA_LOC", "Cự Môn " + dig + " gặp Hóa Lộc", [p["name"]], True)
    s.premises = [{"text": f"Cự Môn tại {p['branch']} ({p['name']}), độ sáng: {dig}", "ok": True},
                  {"text": "Cự Môn bị hãm — điều kiện để áp dụng cách đọc ‘hãm gặp Lộc’", "ok": ham},
                  {"text": "Hóa Lộc rơi đúng vào Cự Môn (Lộc đồng cung với sao hóa)", "ok": True}]
    s.supports = ["Hóa Lộc gắn vào chính Cự Môn: sao hóa luôn thuộc sao gốc, nên Lộc bổ sung phần ‘lợi’ cho tính chất của Cự Môn (lời nói, thị phi, việc ngầm) hơn là xóa độ sáng"]
    if p["branch"] in ("Tý", "Ngọ"):
        s.supports.append("Cự Môn ở Tý/Ngọ: một số định nghĩa ‘Thạch trung ẩn ngọc’ coi Tuần/Triệt hoặc Hóa Lộc là điều kiện thành cách (KL tr.106, TH tr.43) — nhưng các định nghĩa khác nhau (R08)")
        s.matrix_ids.append("R08")
    if p["branch"] in TU_MO:
        s.limiters.append("Hóa Lộc đóng ở Tứ Mộ: tài lộc giảm nhiều (KL tr.66; TH tr.52 nói giảm quá nửa, trừ khi gặp Tham/Vũ)")
    if sat:
        s.limiters.append("Sát tinh trong tam phương tứ chính: " + ", ".join(sorted(set(sat))))
    if ky:
        s.limiters.append("Hóa Kỵ cũng nằm trong tam phương tứ chính (theo bảng Tứ Hóa đang dùng)")
    if p["tuan"] or p["triet"]:
        s.rescuers.append(f"Cung có {_tt(p)}: sách có hai chiều (hại quý tinh / cứu hung tinh / kỳ cách với Cự Môn Tý Ngọ) — R07, không tự chọn")
        s.matrix_ids.append("R07")
    s.cites = ["KL tr.66", "TH tr.52", "KL tr.106", "TH tr.43"]
    s.verification = "mot_phan"
    s.reading = ("Điều kiện tiên quyết ‘Cự Môn hãm’ " + ("đúng" if ham else "KHÔNG đúng (độ sáng: " + dig + "), nên không áp dụng cách đọc ‘hãm gặp Lộc’") +
                 ". Sách trong bộ quy tắc không có câu nói thẳng ‘Cự Môn hãm gặp Hóa Lộc’; hệ thống chỉ ghép các thành phần có câu sách (Hóa Lộc ở Tứ Mộ, Tuần/Triệt, Cự Môn Tý Ngọ). "
                 "Vì vậy kết luận mang tính điều kiện: Lộc cho thêm cơ hội về tài/danh qua lời nói và quan hệ, còn mức độ phát huy phụ thuộc vào sát tinh, Kỵ và Tuần/Triệt kể trên.")
    s.caveat = "Chưa có nguồn cho tổ hợp này; không được đọc thành ‘hãm biến thành tốt’."
    return s


def tam_hoa_hoi_menh(g: Geo) -> Structure:
    m = g.ps["Mệnh"]
    res = {}
    for kind in ("dong_cung", "doi_cung", "tam_phuong"):
        res[kind] = [h for h in g.hoa_in(g.scope(m, kind)) if h in ("Hóa Lộc", "Hóa Quyền", "Hóa Khoa")]
    full = len(set(res["tam_phuong"])) == 3
    s = Structure("TAM_HOA_HOI_MENH", "Tam Hóa (Lộc–Quyền–Khoa) hội Mệnh", ["Mệnh"], full)
    s.premises = [{"text": f"Phạm vi {k.replace('_', ' ')}: " + (", ".join(v) or "không có"), "ok": len(set(v)) == 3} for k, v in res.items()]
    if not full:
        return s
    ky = "Hóa Kỵ" in g.hoa_in(g.scope(m))
    sat = [x for x in g.stars(g.scope(m)) if x in SAT]
    s.supports = ["Ba hóa Lộc, Quyền, Khoa cùng chiếu về Mệnh trong tam phương tứ chính (TH tr.87 — tiếng tăm về văn chương, học vấn; TH tr.30–33 nêu Tam Hóa là một trong các cát tinh làm tăng thế chính tinh)"]
    if ky:
        s.limiters.append("Hóa Kỵ cũng nằm trong tam phương: bốn hóa tề tụ; sách trích không phân xử trường hợp này")
    if sat:
        s.limiters.append("Sát tinh trong tam phương: " + ", ".join(sorted(set(sat))))
    if not res["dong_cung"] and not res["doi_cung"]:
        s.limiters.append("Cả ba hóa chỉ đến từ hai cung tam hợp; nếu hiểu ‘hội’ hẹp hơn thì nhận định không còn đủ ba (R01)")
        s.matrix_ids.append("R01")
    s.variants = [{"scope": k, "holds": len(set(v)) == 3, "found": v} for k, v in res.items()]
    s.cites = ["TH tr.87", "TH tr.30", "TH tr.31", "TH tr.33"]
    s.verification = "da_doi_chieu"
    if "R01" not in s.matrix_ids:
        s.matrix_ids.append("R01")
    s.reading = "Tam Hóa hội Mệnh là điều kiện làm tăng thế của chính tinh tại Mệnh, không phải kết quả độc lập: giá trị đọc phải đi qua độ sáng của chính tinh chứa các hóa và qua việc sát tinh/Kỵ có cùng hội hay không."
    s.caveat = "Chữ ‘hội’ không nêu phạm vi trong sách; kết quả được báo theo ba phạm vi."
    return s


def than_cu_quan_loc_vcd(g: Geo) -> Structure:
    q = g.ps["Quan Lộc"]
    than = next((p for p in g.ps.values() if p["is_than"]), None)
    present = bool(than and than["name"] == "Quan Lộc" and not q["major_stars"])
    s = Structure("THAN_QUAN_VCD", "Thân cư Quan Lộc vô chính diệu", ["Quan Lộc"], present)
    s.premises = [{"text": "Thân cư Quan Lộc", "ok": bool(than and than["name"] == "Quan Lộc")}, {"text": "Quan Lộc không có chính tinh", "ok": not q["major_stars"]}]
    if not present:
        return s
    o = g.opp(q)
    s.supports = ["Mượn chính tinh cung đối (Phu Thê): " + (", ".join(o["major_stars"]) or "đối cung cũng không có chính tinh") + " — chỉ là cách đọc phụ trợ theo thói quen"]
    other = [x for x in g.stars(g.tam_hop(q)) if x in SAT + CAT]
    if other:
        s.supports.append("Phụ tinh ở hai cung tam hợp: " + ", ".join(sorted(set(other))))
    if q["tuan"] or q["triet"]:
        s.limiters.append(f"Quan Lộc có {_tt(q)}; sách chỉ bàn Tuần/Triệt ở Mệnh vô chính diệu (TH tr.53, bản nháp), không bàn riêng ở Quan Lộc")
    s.cites = ["KL tr.222 (Mệnh vô chính diệu — không áp cho Quan Lộc)", "KL tr.218 (Thiên Di vô chính diệu — không áp cho Quan Lộc)"]
    s.verification = "chua_du_nguon"
    s.matrix_ids = []
    s.reading = ("Hệ thống không có câu sách cho ‘Thân cư Quan Lộc vô chính diệu’. Điều rõ từ vị trí: nghề nghiệp/công danh là trọng tâm đời sống của chủ thể (Thân ở đó) và cung không tự có chính tinh nên tính chất do cung đối và tam hợp quyết định. "
                 "Việc mượn sao đối cung chỉ là phép đọc phụ trợ của một số trường phái, không phải quy tắc đã xác minh; không dùng để kết luận mức thành bại.")
    s.caveat = "Không suy diễn vượt nguồn (U_THAN_QUAN_VCD)."
    return s


def co_nguyet_phu_the(g: Geo) -> Structure:
    p = g.ps["Phu Thê"]
    co, am = "Thiên Cơ" in p["major_stars"], "Thái Âm" in p["major_stars"]
    present = co or am
    s = Structure("CO_NGUYET_PHU_THE", "Cơ / Nguyệt tại Phu Thê" + (" đồng cung" if co and am else ""), ["Phu Thê"], present)
    s.premises = [{"text": "Thiên Cơ ở Phu Thê", "ok": co}, {"text": "Thái Âm ở Phu Thê", "ok": am}]
    if not present:
        return s
    sc = g.scope(p)
    hoa_here = [h for h in g.hoa_in([p])]
    da = "Đà La" in p["stars"]
    da_sc = "Đà La" in g.stars(sc)
    ky = "Hóa Kỵ" in hoa_here
    ky_sc = "Hóa Kỵ" in g.hoa_in(sc)
    s.supports = ["Sách tả người phối ngẫu và tuổi kết hôn theo sao ở Phu Thê (TT tr.82–83; KL tr.80 cho Thiên Cơ ở Tỵ/Ngọ/Mùi)"]
    for flag, txt in ((p["tuan"] or p["triet"], f"Cung có {_tt(p)}"), (ky, "Hóa Kỵ đồng cung"), (da, "Đà La đồng cung")):
        if flag:
            s.limiters.append(txt)
    if not ky and ky_sc:
        s.limiters.append("Hóa Kỵ trong tam phương tứ chính (không đồng cung)")
    if not da and da_sc:
        s.limiters.append("Đà La trong tam phương tứ chính (không đồng cung)")
    if p["tuan"] or p["triet"]:
        s.matrix_ids.append("R07")
    s.cites = ["TT tr.82–83", "KL tr.80"]
    s.verification = "mot_phan"
    s.reading = ("Phần ‘sao nào ở Phu Thê’ có câu sách; phần ‘gặp Tuần/Kỵ/Đà’ chỉ có các câu chung về hung tinh/Tuần/Triệt (R07) chứ không có câu riêng cho Cơ Nguyệt ở Phu Thê. "
                 "Do đó điều được nói là: đặc điểm tuổi tác/tính cách người phối ngẫu theo sao, cộng thêm các yếu tố có thể làm quan hệ khó ổn định hoặc chậm; không kết luận về thành bại hôn nhân.")
    s.caveat = "Nhận định truyền thống về hôn nhân không phải dự báo."
    return s


def kinh_duong_tu_mo(g: Geo) -> list[Structure]:
    out = []
    for p in g.ps.values():
        if "Kình Dương" in p["stars"] and p["branch"] in TU_MO:
            s = Structure("KINH_DUONG_TU_MO", f"Kình Dương ở Tứ Mộ ({p['branch']}) — cung {p['name']}", [p["name"]], True)
            dig = p["minor_dignity"].get("Kình Dương") or "chưa rõ"
            sc = g.scope(p)
            hoa = "Hỏa Tinh" in p["stars"]
            bad = [x for x in g.stars(sc) if x in ("Địa Không", "Địa Kiếp", "Linh Tinh", "Đà La")]
            s.premises = [{"text": f"Kình Dương tại {p['branch']}, độ sáng: {dig}", "ok": True}, {"text": "Đồng cung Hỏa Tinh", "ok": hoa}]
            if hoa:
                s.supports.append("Kình Dương đồng cung Hỏa Tinh ở Tứ Mộ: uy quyền lớn (TT tr.50, nói riêng về cung Mệnh)")
            kq = [x for x in g.hoa_in(sc) if x in ("Hóa Quyền", "Hóa Khoa", "Hóa Lộc")]
            if kq:
                s.rescuers.append("Có " + ", ".join(kq) + " trong tam phương (KL tr.64 nêu ‘Kình gặp Khoa Quyền Lộc’ là thế tốt — với điều kiện xa Thất Sát/Thiên Hình)")
                s.matrix_ids.append("R08")
            if bad:
                s.limiters.append("Sát tinh khác trong tam phương: " + ", ".join(sorted(set(bad))))
            if any(x in ("Thất Sát", "Thiên Hình") for x in p["stars"]):
                s.limiters.append("Đồng cung Thất Sát/Thiên Hình: trong định nghĩa của TT tr.142 (Kình ở Ngọ) là thế xấu; ở Tứ Mộ không có câu tương ứng")
            s.cites = ["TT tr.50", "KL tr.64", "TT tr.142"]
            s.verification = "mot_phan" if p["name"] == "Mệnh" else "chua_du_nguon"
            s.reading = ("Tứ Mộ là nơi Kình Dương được xếp ở thế dễ dùng được (sức mạnh, quyết đoán), nhưng quy tắc trong bộ sách chỉ nêu rõ cho cung Mệnh có Hỏa Tinh. "
                         + ("Cung này không phải Mệnh nên chỉ ghi vị trí và các yếu tố đi kèm." if p["name"] != "Mệnh" else "Kết luận phụ thuộc Hỏa Tinh, Khoa–Quyền–Lộc và các sát tinh còn lại."))
            out.append(s)
    return out


def sat_pha_tham(g: Geo) -> Structure:
    m = g.ps["Mệnh"]
    sc = g.scope(m)
    stars = g.stars(sc)
    majors = [x for p in sc for x in p["major_stars"]]
    spt = [x for x in ("Thất Sát", "Phá Quân", "Tham Lang") if x in majors]
    present = len(spt) == 3
    s = Structure("SAT_PHA_THAM", "Sát – Phá – Tham trong tam phương Mệnh", ["Mệnh"], present)
    s.premises = [{"text": f"{x} trong tam phương tứ chính của Mệnh", "ok": x in spt} for x in ("Thất Sát", "Phá Quân", "Tham Lang")]
    if not present:
        return s
    sat = sorted({x for x in stars if x in SAT})
    cat = sorted({x for x in stars if x in CAT})
    ky = "Hóa Kỵ" in g.hoa_in(sc)
    gp = [{"threshold": "≥1 sát tinh", "breaks": len(sat) >= 1}, {"threshold": "≥2 sát tinh", "breaks": len(sat) >= 2},
          {"threshold": "≥3 sát tinh và Kỵ (quy ước thiết kế)", "breaks": len(sat) >= 3 and ky}]
    s.variants = gp
    s.supports = ["Cát tinh trong tam phương: " + (", ".join(cat) if cat else "không có")]
    s.limiters = ["Sát tinh trong tam phương: " + (", ".join(sat) if sat else "không có")] + (["Hóa Kỵ trong tam phương"] if ky else [])
    for m_id in ("R03", "R01"):
        s.matrix_ids.append(m_id)
    verdicts = {v["breaks"] for v in gp}
    s.cites = ["TH tr.77", "TH tr.116"]
    s.verification = "mot_phan"
    s.reading = ("Thế Sát–Phá–Tham là thế biến động, ‘làm nên’ hay ‘lao đao’ tùy cát/sát đi kèm (TH tr.77). " +
                 ("Ba ngưỡng sát tinh trong sách cho ba kết luận khác nhau về việc có bị phá cách hay không — phải trình bày cả ba." if len(verdicts) > 1 else
                  "Với dữ liệu này cả ba ngưỡng đều cho cùng kết luận " + ("‘phá cách’." if verdicts == {True} else "‘không phá cách’.")))
    s.caveat = "Ngưỡng phá cách chưa đủ nguồn (R03)."
    return s


def detect_all(palaces, tu_hoa) -> list[Structure]:
    g = Geo(palaces, tu_hoa)
    out = [cu_mon_ham_hoa_loc(g), tam_hoa_hoi_menh(g), than_cu_quan_loc_vcd(g), co_nguyet_phu_the(g), sat_pha_tham(g), *kinh_duong_tu_mo(g)]
    return out
