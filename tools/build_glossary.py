"""Generates engine/web/js/glossary.json (static asset used by the interactive glossary).

Sources: engine/data/glossary_vi.json (hand-written plain-language entries) merged with
engine/data/star_profiles.json (Thực Hành star headers: element, đẩu, domain, page locator).
Run: python tools/build_glossary.py   (tests/test_glossary.py fails if the output is stale)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "engine"
SRC = ROOT / "data" / "glossary_vi.json"
PROFILES = ROOT / "data" / "star_profiles.json"
TUHOA = ROOT / "data" / "tu_hoa_vi.json"
OUT = ROOT / "web" / "js" / "glossary.json"

STEM_HAN = dict(zip(["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"], "甲乙丙丁戊己庚辛壬癸"))
BRANCH_HAN = dict(zip(["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"], "子丑寅卯辰巳午未申酉戌亥"))
GOD_HAN = {"Tỉ Kiên": "比肩", "Kiếp Tài": "劫財", "Thực Thần": "食神", "Thương Quan": "傷官", "Thiên Tài": "偏財",
           "Chính Tài": "正財", "Thất Sát": "七殺", "Chính Quan": "正官", "Thiên Ấn": "偏印", "Chính Ấn": "正印"}
LESSON = {"star": "tv-3", "minor": "tv-3", "ring": "tv-3", "palace": "tv-2", "can": "bt-2", "chi": "bt-2", "god": "bt-3", "gg": "bt-3", "dg": "tv-3"}
ALIASES = {
    "Nhật Chủ": "c:nhat-chu", "Nguyệt lệnh": "c:nguyet-lenh", "Tàng can": "c:tang-can", "Trường sinh": "c:truong-sinh",
    "Đại vận": "c:dai-van", "Đại hạn": "c:dai-han", "Lưu niên": "c:luu-nien", "Tiểu hạn": "c:tieu-han",
    "Tam phương tứ chính": "c:tam-phuong", "Tứ Hóa": "c:tu-hoa", "Hóa Lộc": "c:hoa-loc", "Hóa Quyền": "c:hoa-quyen",
    "Hóa Khoa": "c:hoa-khoa", "Hóa Kỵ": "c:hoa-ky", "Tuần": "c:tuan", "Triệt": "c:triet", "Vô chính diệu": "c:vo-chinh-dieu",
    "vô chính diệu": "c:vo-chinh-dieu", "Thân cư": "c:than-cu", "Thập thần": "c:thap-than", "Thập Thần": "c:thap-than",
    "Ngũ Hành": "c:ngu-hanh", "Can Chi": "c:can-chi", "Bản mệnh": "c:nap-am", "Nạp âm": "c:nap-am",
    "Cục sinh Mệnh": "c:menh-cuc", "Độ sáng": "c:do-sang", "Thiên can": "c:can-chi", "Địa chi": "c:can-chi",
}


def build() -> dict:
    src = json.loads(SRC.read_text("utf-8"))
    prof = json.loads(PROFILES.read_text("utf-8"))["stars"]
    terms: dict[str, dict] = {}
    stars, minors = [], []
    for name, e in src["stars"].items():
        p = prof[name]
        stars.append(name)
        terms[f"star:{name}"] = {"kind": "Chính tinh", "title": name, "plain": e["plain"], "ex": e["ex"], "lesson": LESSON["star"],
                                 "facts": [["Hành", p["element"]], ["Thuộc", p["dau"]], ["Hay được gắn với", p["domain"]]], "src": p["locator"]}
    for name, e in src["minor"].items():
        minors.append(name)
        terms[f"star:{name}"] = {"kind": e["kind"].capitalize() if e["kind"] != "ring" else "Phụ tinh", "title": name, "plain": e["plain"], "lesson": LESSON["minor"]}
    for rname, e in src["rings"].items():
        terms[f"ring:{rname}"] = {"kind": "Nhóm sao", "title": rname, "plain": e["plain"], "lesson": LESSON["ring"]}
        for m in e["members"]:
            terms[f"star:{m}"] = {"kind": "Phụ tinh", "title": m, "plain": f"Một sao thuộc {rname.lower()}. {e['plain']}", "lesson": LESSON["ring"]}
            minors.append(m)
    for name, e in src["palaces"].items():
        terms[f"palace:{name}"] = {"kind": "Cung", "title": f"Cung {name}", "plain": e["plain"], "ex": f"{e['ask']} {e['ex']}", "lesson": LESSON["palace"]}
    for name, e in src["stems"].items():
        terms[f"can:{name}"] = {"kind": "Thiên can", "title": name, "han": STEM_HAN[name], "plain": e["plain"],
                                "facts": [["Hành", e["el"]], ["Âm dương", e["yy"]]], "lesson": LESSON["can"]}
    for name, e in src["branches"].items():
        terms[f"chi:{name}"] = {"kind": "Địa chi", "title": name, "han": BRANCH_HAN[name],
                                "plain": f"Địa chi tượng trưng bởi con {e['animal'].lower()}; cũng là tên của một khung giờ và một tháng trong năm.",
                                "facts": [["Hành", e["el"]], ["Giờ", e["hours"]], ["Tháng", e["month"]], ["Con giáp", e["animal"]]], "lesson": LESSON["chi"]}
    gods = []
    for name, e in src["gods"].items():
        gods.append(name)
        terms[f"god:{name}"] = {"kind": "Thập Thần", "title": name, "han": GOD_HAN[name], "plain": e["plain"], "ex": e["ex"],
                                "facts": [["Thuộc nhóm", e["group"]]], "lesson": LESSON["god"]}
    for name, e in src["godGroups"].items():
        terms[f"gg:{name}"] = {"kind": "Nhóm Thập Thần", "title": name, "plain": e["plain"], "lesson": LESSON["gg"]}
    for k, e in src["dignity"].items():
        terms[f"dg:{k}"] = {"kind": "Độ sáng", "title": e["title"], "plain": e["plain"], "lesson": LESSON["dg"]}
    for k, e in src["concepts"].items():
        terms[f"c:{k}"] = {"kind": "Khái niệm", "title": e["title"], "plain": e["plain"], "lesson": e.get("lesson", "gioi-thieu"),
                           **({"han": e["han"]} if "han" in e else {}), **({"ex": e["ex"]} if "ex" in e else {})}
    by = json.loads(TUHOA.read_text("utf-8"))["by_stem"]  # Tứ Hóa by year stem (Lộc, Quyền, Khoa, Kỵ), Khảo Luận pp.195-197
    terms["x:tu-hoa-table"] = {"kind": "Bảng", "title": "Tứ Hóa theo Can năm sinh", "plain": "", "lesson": "tv-5",
                               "table": [[n, [x["star"] for x in by[str(i)]]] for i, n in enumerate(src["stems"])]}
    for alias, key in ALIASES.items():
        assert key in terms, (alias, key)
    return {"terms": terms, "stars": sorted(set(stars + minors), key=lambda s: (-len(s), s)), "gods": gods, "aliases": ALIASES}


if __name__ == "__main__":
    OUT.write_text(json.dumps(build(), ensure_ascii=False, indent=1, sort_keys=False) + "\n", "utf-8")
    print("wrote", OUT, "terms:", len(json.loads(OUT.read_text("utf-8"))["terms"]))
