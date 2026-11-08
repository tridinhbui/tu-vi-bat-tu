"""Condition fidelity of the grave rules (plan THIEN-BAN-33 G1.2): for every rule in engine/data/kg/claim_severity.json, compare the
condition the book states (the bracket of the rule's description) with what the rule's encoded conditions actually test:
  star       a star the book condition names that no encoded leaf tests (the rule fires without it)
  dignity    the book says hãm / đắc / miếu / vượng / sáng but no encoded leaf tests a brightness or a branch list
  branch     the book names branches (Tý, Ngọ …) but no encoded leaf tests the branch
A finding means the rule may fire more widely than the page; each one is read against the page before the pack is patched in place
(packs are patched in place: regenerating them drops later fixes, see the synthesis-ledger notes).
  python3 tools/interpret/audit_conditions.py [--all]
"""
import glob, json, re, sys, unicodedata

SEV = json.load(open("engine/data/kg/claim_severity.json"))["rules"]
STARS = sorted(set(json.load(open("engine/data/dignity_kb.json"))["stars"]) | {
    "Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp", "Thiên Hình", "Thiên Riêu", "Thiên Khốc", "Thiên Hư", "Đại Hao", "Tiểu Hao",
    "Tang Môn", "Bạch Hổ", "Điếu Khách", "Quan Phù", "Phục Binh", "Cô Thần", "Quả Tú", "Đẩu Quân", "Thiên Không", "Phá Toái", "Kiếp Sát", "Hóa Kỵ",
    "Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Lộc Tồn", "Thiên Mã", "Đào Hoa", "Hồng Loan", "Thiên Hỷ", "Bệnh Phù", "Thiên Thọ", "Thiên Y", "Đế Vượng", "Trường Sinh",
    "Mộc Dục", "Suy", "Tuyệt", "Thai", "Tuần", "Triệt"}, key=len, reverse=True)
BRANCH = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]


def leaves(e):
    if isinstance(e, dict):
        if "fact" in e:
            yield e
        for k in ("all", "any", "count"):
            for x in e.get(k, []):
                yield from leaves(x)
        if "not" in e:
            yield from leaves(e["not"])


def main():
    rules = {}
    for fn in glob.glob("engine/data/pack_*.json"):
        d = json.load(open(fn))
        for r in (d.get("rules", d) if isinstance(d, dict) else d):
            rules[r["id"]] = (fn, r)
    out = []
    for rid, sev in sorted(SEV.items()):
        if rid not in rules:
            continue
        fn, r = rules[rid]
        cond = unicodedata.normalize("NFC", sev["cond"])
        ls = list(leaves(r.get("conditions", {})))
        blob = json.dumps(ls, ensure_ascii=False)
        rest, miss = cond, []
        for s in STARS:
            if s in rest:
                rest = rest.replace(s, " ")
                short = s.split()[-1]
                if s not in blob and not (s.startswith("Hóa") and s in blob) and not (s in ("Tuần", "Triệt") and ("tuan" in blob or "triet" in blob)):
                    miss.append(s)
        f = []
        if miss:
            f.append(f"star:{','.join(miss)}")
        if re.search(r"\bhãm|\bđắc|\bmiếu|\bvượng|\bsáng\b", cond) and not re.search(r"dignity|branch", blob):
            f.append("dignity")
        if any(re.search(rf"(?<!\w){b}(?!\w)", cond) for b in BRANCH) and "branch" not in blob and "dignity" not in blob:
            f.append("branch")
        if f or "--all" in sys.argv:
            out.append((rid, sev["class"], f, cond, fn.split("/")[-1]))
    for rid, cls, f, cond, fn in out:
        print(f"{cls:13} {rid:52} {' '.join(f):28} | {cond[:90]}  [{fn}]")
    print(len(out), "finding(s) of", len(SEV))


main()
