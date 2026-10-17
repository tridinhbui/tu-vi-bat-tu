"""Generates data/pack_toan_thu_palaces.json from tools/data/toan_thu_palace_star.txt: Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục) pp.77-89, the 'Có sao X' readings of
Thiên Di, Quan Lộc, Tài Bạch, Phu Thê, Phúc Đức, Phụ Mẫu, Nô Bộc and Điền Trạch, one line per (palace, star, condition). Paraphrased and page-cited
(Thiên Di pp.77-78, Quan Lộc pp.78-80, Tài Bạch pp.80-81, Phu Thê pp.82-83, Phúc Đức pp.83-84, Phụ Mẫu pp.86-87, Nô Bộc pp.87-88, Điền Trạch pp.88-89).
Not encoded: Tật Ách (illness), Huynh Đệ/Tử Tức (the book's own text is thin), and every 'khắc/hình khắc/tảo khắc' or death/prison/injury statement.
Variants: base = star in the palace; mieu/ham = star bright/dim in the palace; with:A|B = star shares the palace with A (or B); sat = a sát tinh in the tam phương.
Status: verified unless the paraphrase carries an extra clause the rule does not test (then draft)."""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
D = ROOT.parent / "engine" / "data"
PAGES = {"Thiên Di": "pp.77-78", "Quan Lộc": "pp.78-80", "Tài Bạch": "pp.80-81", "Phu Thê": "pp.82-83", "Phúc Đức": "pp.83-84", "Phụ Mẫu": "pp.86-87",
         "Nô Bộc": "pp.87-88", "Điền Trạch": "pp.88-89"}
MAJORS = {"Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh", "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn", "Thiên Tướng", "Thiên Lương", "Thất Sát", "Phá Quân"}
has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
GOOD, HAM = ["miếu", "vượng", "đắc"], ["hãm"]
slug = lambda t: unicodedata.normalize("NFD", t.replace("Đ", "D").replace("đ", "d")).encode("ascii", "ignore").decode().upper().replace(" ", "_").replace("|", "_").replace(":", "_")
rules, claims, seen = [], {}, {}
for raw in (ROOT / "data" / "toan_thu_palace_star.txt").read_text("utf-8").splitlines():
    if not raw.strip() or raw.startswith("#"):
        continue
    pal, star, var, tone, phrase = [x.strip() for x in raw.split("|", 4)]
    own = has("palace.own_major_stars" if star in MAJORS else "palace.own_stars", star)
    conds = [{"fact": "palace.name", "value": pal}, own]
    if var == "mieu":
        conds.append({"fact": f"palace.dignity.{star}", "operator": "in", "value": GOOD})
    elif var == "ham":
        conds.append({"fact": f"palace.dignity.{star}", "operator": "in", "value": HAM})
    elif var == "sat":
        conds.append({"fact": "palace.khi.sat_tp", "operator": "gte", "value": 1})
    elif var.startswith("with:"):
        others = var[5:].split("|")
        conds.append({"any": [has("palace.own_major_stars" if o in MAJORS else "palace.own_stars", o) for o in others]})
    elif var != "base":
        raise SystemExit("bad variant " + raw)
    key = (pal, star, var, tone)
    seen[key] = seen.get(key, 0) + 1
    suffix = "" if seen[key] == 1 else f"_{seen[key]}"
    rid = f"TV_TT_PAL_{slug(pal)}_{slug(star)}_{slug(var)}_{'P' if tone == '+' else 'M'}{suffix}"
    claim = f"tt_{slug(pal).lower()}_{slug(star).lower()}_{slug(var).lower()}_{'p' if tone == '+' else 'm'}{suffix.lower()}"
    status = "draft" if re.search(r"thêm |nếu |miễn là", phrase) else "verified"
    effect = "support" if tone == "+" else "limit"
    ctx = {"base": "", "mieu": ", thế sáng", "ham": ", thế hãm", "sat": ", gặp sát tinh"}.get(var, f", đồng cung {var[5:].replace('|', ' hoặc ')}" if var.startswith("with:") else "")
    vi = f"{phrase} ({star} ở {pal}{ctx})"
    rules.append({"id": rid, "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "tt_palace_star",
        "description": f"Tử Vi Đẩu Số Toàn Thư, 'có sao {star}' ở cung {pal} (paraphrased): {vi} [TT {PAGES[pal]}]",
        "conditions": {"all": conds}, "consequences": [{"kind": "finding", "claim": claim, "effect": effect, "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": ["SRC_TOAN_THU"], "reviewStatus": status, "version": "0.1.0", "subject": "palace"})
    claims[claim] = ("khuynh hướng " if effect == "support" else "hạn chế: ") + vi
    if effect == "limit":
        claims["limit:" + claim] = "hạn chế: " + vi
ids = [r["id"] for r in rules]
assert len(ids) == len(set(ids))
json.dump({"sources": [], "rules": rules}, open(D / "pack_toan_thu_palaces.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8"))
for k, v in claims.items():
    cur.setdefault(k, v)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules), sum(r["reviewStatus"] == "draft" for r in rules))
