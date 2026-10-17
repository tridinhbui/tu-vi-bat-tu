"""Phase 4 source audit of the 10 draft cách cục (definition v2).

Writes engine/data/experimental/formation_source_audit.json and docs/PHASE4_BANG_NGUON_CACH_CUC.md.

Evidence tiers (strictest first). NOTHING in this audit reaches T0, so every element stays `draft`:
  T0  book_read_direct      a printed page read and transcribed in THIS audit            -> none (no book is available to this session)
  T1  registry_verified     a pack rule with a page and reviewStatus=verified            -> NOT independent evidence: it is the project's own
                                                                                           earlier reading, stored as a PARAPHRASE
  T2  registry_draft        a pack rule with a page but reviewStatus=draft
  T3  classical_web_single  a line of 紫微斗數全書 retrieved from zh.wikisource.org via a fetch tool that summarises pages;
                            one web copy, not checked against a printed edition
  T4  hypothesis            design choice of the draft, no source found
A source only SUPPORTS an element when the provenance status is `khop`; `lien_quan`, `long_hon`, `chat_hon`, `khac` are listed as related
but give no support. The tier of an element is the best tier among the sources that support it, else `T4`.

The original text of the registry rules is NOT stored in the repo (the packs hold Vietnamese paraphrases), so for T1/T2 rows the column
`nguyen_van` says so instead of inventing a quotation. Only T3 rows carry original Chinese."""
import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENG = ROOT / "engine"
DOC = ROOT / "docs" / "PHASE4_BANG_NGUON_CACH_CUC.md"
OUT = ENG / "data" / "experimental" / "formation_source_audit.json"
URL = "https://zh.wikisource.org/wiki/紫微斗數全書/卷一"

TIERS = {"T0": "đọc trực tiếp trang sách trong lần audit này", "T1": "luật trong registry, đã verified (diễn giải, không độc lập)",
         "T2": "luật trong registry, còn draft", "T3": "câu phú gốc từ một bản web, chưa đối chiếu bản in", "T4": "giả thuyết thiết kế"}

# Classical lines retrieved (zh.wikisource, via a summarising fetch tool). `zh` is as returned; `vi` is a close literal rendering by the auditor.
CLASSICAL = {
    "C_TP_DONG": dict(sec="斗數骨髓賦", zh="紫府同宮終身福厚", vi="Tử Phủ đồng cung, suốt đời phúc dày."),
    "C_TP_TRIEU": dict(sec="斗數骨髓賦", zh="紫府朝垣食祿萬鍾", vi="Tử Phủ chầu viên (triều viên), hưởng lộc muôn chung."),
    "C_CNDL": dict(sec="斗數骨髓賦", zh="七殺破軍宜出外，機月同梁作吏人", vi="Thất Sát, Phá Quân nên ra ngoài; Cơ Nguyệt Đồng Lương làm hạng lại viên (viên chức)."),
    "C_NN_MINH": dict(sec="斗數骨髓賦", zh="日月並明佐九重於堯殿", vi="Nhật Nguyệt cùng sáng, giúp chín tầng cung điện vua Nghiêu."),
    "C_NN_BOI": dict(sec="太微賦", zh="日月最嫌反背", vi="Nhật Nguyệt rất ngại bị phản bối (đảo ngược)."),
    "C_NLTT": dict(sec="太微賦", zh="太陽居午，謂之日麗中天，有專權之貴，敵國之富", vi="Thái Dương ở Ngọ gọi là Nhật lệ trung thiên: có cái quý chuyên quyền, cái giàu địch quốc."),
    "C_TTAN": dict(sec="斗數骨髓賦", zh="子午巨門石中隱玉，明祿暗祿錦上添花", vi="Cự Môn ở Tý Ngọ là ngọc ẩn trong đá; minh lộc, ám lộc thêm hoa trên gấm."),
    "C_TTAN_PHU": dict(sec="論石中隱玉格（以檢索工具轉述）", zh="巨門子午二宮逢，身命逢之必貴榮，更得三方科祿照，石中隱玉是豐隆",
                       vi="Cự Môn gặp ở hai cung Tý Ngọ, thân hoặc mệnh gặp ắt vinh quý; lại được tam phương Khoa, Lộc chiếu thì ngọc ẩn trong đá là thịnh vượng."),
    "C_MDDK": dict(sec="太微賦", zh="馬頭帶劍，鎮衛邊疆", vi="Đầu ngựa đeo gươm, trấn giữ biên cương."),
    "C_MDDK_CHU": dict(sec="定貴局（chú）", zh="馬頭帶劍 謂馬有刃是也不是居午格", vi="Mã đầu đới kiếm: nghĩa là (Thiên) Mã có 'nhận' (lưỡi), chứ không phải cách ở cung Ngọ."),
    "C_KV": dict(sec="定貴局（chú）", zh="坐貴向貴 謂魁鉞在命迭相坐拱是也", vi="Tọa quý hướng quý: Khôi Việt ở Mệnh, thay nhau tọa và củng chiếu."),
}
# (formation, role, element id or None for core) -> [(classical id, correspondence, note)]
CLASS_LINKS = {
    ("CACH_X_TU_PHU_DONG_CUNG", "core", None): [("C_TP_DONG", "khop", "khớp tên và vị trí đồng cung; câu phú không nêu điều kiện thành/phá")],
    ("CACH_X_TU_PHU_VU_TUONG", "core", None): [("C_TP_TRIEU", "lien_quan", "chỉ nói Tử Vi + Thiên Phủ chầu viên, không nói Vũ Khúc, Thiên Tướng")],
    ("CACH_X_CO_NGUYET_DONG_LUONG", "core", None): [("C_CNDL", "lien_quan", "chỉ nêu tên nhóm và 'làm lại viên'; không nêu vị trí tam phương hay số sao")],
    ("CACH_X_SAT_PHA_LIEM_THAM", "core", None): [("C_CNDL", "lien_quan", "câu phú chỉ nói Thất Sát, Phá Quân; không nêu Liêm Trinh, Tham Lang hay tam phương")],
    ("CACH_X_NHAT_NGUYET_TINH_MINH", "boosters", "nhat_nguyet_deu_sang"): [("C_NN_MINH", "khop", "'tịnh minh' = cùng sáng; câu phú không nêu ngưỡng độ sáng")],
    ("CACH_X_NHAT_NGUYET_TINH_MINH", "refutations", "Thái_Dương_ham"): [("C_NN_BOI", "lien_quan", "'phản bối' là sai vị trí/đảo ngược, không nhất thiết đồng nghĩa 'hãm' theo bảng")],
    ("CACH_X_NHAT_NGUYET_TINH_MINH", "refutations", "Thái_Âm_ham"): [("C_NN_BOI", "lien_quan", "như trên")],
    ("CACH_X_NHAT_LE_TRUNG_THIEN", "core", None): [("C_NLTT", "khop", "Thái Dương ở Ngọ")],
    ("CACH_X_THACH_TRUNG_AN_NGOC", "core", None): [("C_TTAN", "khop", "Cự Môn ở Tý/Ngọ"), ("C_TTAN_PHU", "khop", "cũng Tý/Ngọ; nói 'thân hoặc mệnh'")],
    ("CACH_X_THACH_TRUNG_AN_NGOC", "boosters", "tam_hoa_hoi_du"): [("C_TTAN_PHU", "khac", "câu phú chỉ nêu Khoa và Lộc (科祿) chiếu, KHÔNG nêu Quyền; sách Việt (KL p.58, TT p.34) đòi đủ Khoa+Quyền+Lộc")],
    ("CACH_X_MA_DAU_DOI_KIEM", "core", None): [("C_MDDK", "lien_quan", "chỉ nêu tên và 'trấn giữ biên cương'"),
                                              ("C_MDDK_CHU", "khac", "chú giải nói 'Mã có nhận' và phủ nhận đó là cách ở Ngọ; định nghĩa nháp (Kình Dương ở Ngọ, theo KL p.64 trong registry) CÓ THỂ mâu thuẫn")],
    ("CACH_X_KHOI_VIET_GIAP_MENH", "core", None): [("C_KV", "lien_quan", "'tọa quý hướng quý' là Khôi Việt tọa/củng Mệnh, không phải kẹp hai bên (giáp)")],
}
# Conflicts between sources (not between the draft and one source).
CONFLICTS = [
    dict(id="X_MDDK_NGO", formation="CACH_X_MA_DAU_DOI_KIEM", sides=["KL p.64 (registry, draft): Kình Dương ở Ngọ", "chú giải 定貴局 (T3): 'Mã có nhận', không phải cách ở cung Ngọ"],
         effect="điều kiện lõi của cách chưa thể coi là đã xác định; giữ draft, cần đọc lại cả hai trang sách"),
    dict(id="X_TTAN_HOA", formation="CACH_X_THACH_TRUNG_AN_NGOC", sides=["KL p.58 và TT p.34 (registry, verified): Khoa+Quyền+Lộc đủ", "phú gốc (T3): tam phương có Khoa, Lộc chiếu (không nêu Quyền)"],
         effect="booster 'tam_hoa_hoi_du' chặt hơn câu phú; cần xem bản chú Việt có thêm Quyền hay không"),
    dict(id="X_TRIET_GIAI", formation="*", sides=["mọi bản nháp v1: Triệt giải sát tinh (đã bỏ ở v2)", "TH pp.94-95 (registry, verified): Tuần/Triệt bất lợi cho Phủ, Tướng, Âm, Lương"],
         effect="đã loại khỏi v2; ghi lại để không tái xuất hiện"),
]


def render(e):
    if "fact" in e:
        return f"{e['fact']} {e.get('operator', 'eq')} {json.dumps(e['value'], ensure_ascii=False)}"
    if "ref" in e:
        return f"[{e['ref']['palace']}].{e['ref']['fact']} {e.get('operator', 'eq')} {json.dumps(e['value'], ensure_ascii=False)}"
    if "count" in e:
        return f"đếm({'; '.join(render(x) for x in e['count'])}) {e['operator']} {e['value']}"
    k = next(iter(e))
    if k == "not":
        return "KHÔNG(" + render(e["not"]) + ")"
    return ("VÀ" if k == "all" else "HOẶC") + "(" + "; ".join(render(x) for x in e[k]) + ")"


def build():
    packs = {}
    for f in sorted(glob.glob(str(ENG / "data" / "pack_*.json"))):
        for r in json.load(open(f, encoding="utf-8"))["rules"]:
            packs[r["id"]] = r
    prov = json.load(open(ENG / "data" / "experimental" / "formation_provenance.json", encoding="utf-8"))["formations"]
    forms = json.load(open(ENG / "data" / "experimental" / "formations_experimental.json", encoding="utf-8"))["formations"]
    out = {"version": 1, "tiers": TIERS, "classical_url": URL, "classical": CLASSICAL, "conflicts": CONFLICTS, "formations": {}}
    for F in forms:
        fid = F["id"]
        rows = []
        els = [("core", None, "lõi", F["core"], None)] + [(r, e["id"], e["label"], e["when"], e.get("rescues")) for r in ("boosters", "breakers", "rescuers", "refutations") for e in F[r]]
        for role, eid, label, when, rescues in els:
            p = prov[fid]["core"] if role == "core" else prov[fid][role][eid]
            srcs = []
            for s in p["sources"]:
                rule = packs[s["rule"]]
                tier = "T1" if s["review"] == "verified" else "T2"
                sup = p["status"] == "khop"
                srcs.append(dict(kind="registry", rule=s["rule"], book=s["source"], page=s["page"], review=s["review"], tier=tier, supports=sup, independent=False,
                                 nguyen_van="không có trong repo (registry chỉ lưu diễn giải)", registry_paraphrase=rule["description"],
                                 registry_condition=render(rule["conditions"]), correspondence=p["status"]))
            for cid, corr, note in CLASS_LINKS.get((fid, role, eid), []):
                c = CLASSICAL[cid]
                sup = corr == "khop"
                srcs.append(dict(kind="classical_web", id=cid, section=c["sec"], zh=c["zh"], vi_literal=c["vi"], url=URL, tier="T3", supports=sup, independent=False,
                                 retrieved_via="WebFetch (tóm tắt trang), chưa đối chiếu bản in", correspondence=corr, note=note))
            best = min((s["tier"] for s in srcs if s["supports"]), default="T4")          # T1 < T2 < T3 < T4 lexicographically
            rows.append(dict(role=role, id=eid or "core", label=label, machine=render(when), rescues=rescues, provenance_status=p["status"], provenance_note=p["note"],
                             effective_tier=best, supports=[s.get("rule") or s["id"] for s in srcs if s["supports"]], sources=srcs, verdict="draft"))
        tiers = [r["effective_tier"] for r in rows]
        out["formations"][fid] = dict(name_vi=F["name_vi"], reviewStatus=F["reviewStatus"], definition_version=F.get("definition_version"),
                                      summary={t: tiers.count(t) for t in ("T1", "T2", "T3", "T4")}, elements=rows)
    return out


def markdown(a):
    L = ["# Phase 4 — bảng nguồn cho 10 cách cục (định nghĩa v2)", "",
         "Sinh bởi `tools/build_formation_source_audit.py`. **Không điều kiện nào đạt T0 (đọc trực tiếp trang sách)**, nên toàn bộ vẫn `draft`.", "",
         "| Tầng | Ý nghĩa |", "|---|---|"] + [f"| {k} | {v} |" for k, v in TIERS.items()] + [
        "", "Registry **không phải bằng chứng độc lập**: nó là cách các phiên trước đã đọc sách, lưu dưới dạng diễn giải tiếng Việt, không có nguyên văn.",
        "Chỉ nguồn có mức tương ứng `khop` mới tính là *ủng hộ*; `lien_quan`/`long_hon`/`chat_hon`/`khac` chỉ liệt kê là liên quan.", "",
        "## Xung đột giữa các nguồn", ""]
    for c in a["conflicts"]:
        L += [f"- **{c['id']}** ({c['formation']}): " + " ↔ ".join(c["sides"]) + f". Hệ quả: {c['effect']}."]
    L += ["", "## Câu phú gốc đã truy xuất (T3)", "", f"Nguồn: {URL}. Qua công cụ tóm tắt, một bản web; bản dịch là dịch sát nghĩa của người audit.", "",
          "| id | mục | nguyên văn | dịch sát nghĩa |", "|---|---|---|---|"]
    L += [f"| {k} | {v['sec']} | {v['zh']} | {v['vi']} |" for k, v in a["classical"].items()]
    for fid, F in a["formations"].items():
        L += ["", f"## {F['name_vi']} (`{fid}`)", "", "Tóm tắt tầng hiệu lực: " + ", ".join(f"{t}={n}" for t, n in F["summary"].items() if n) + ".", "",
              "| vai trò | điều kiện máy hóa | tầng | nguồn (sách, trang, review) | mức tương ứng | ghi chú |", "|---|---|---|---|---|---|"]
        for r in F["elements"]:
            src = "; ".join(f"{s['book'].replace('SRC_', '')} {s['page']} [{s['review']}] `{s['rule']}`" if s["kind"] == "registry" else f"{s['section']}「{s['zh']}」" for s in r["sources"]) or "—"
            corr = ", ".join(sorted({s['correspondence'] for s in r["sources"]})) or "khong_co_nguon"
            L.append(f"| {r['role']}:{r['id']} | `{r['machine'][:150]}` | {r['effective_tier']} | {src} | {corr} | {r['provenance_note'][:140]} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    a = build()
    OUT.write_text(json.dumps(a, ensure_ascii=False, indent=1) + "\n", "utf-8")
    DOC.write_text(markdown(a), "utf-8")
    n = sum(len(F["elements"]) for F in a["formations"].values())
    print(n, "elements;", {t: sum(F["summary"].get(t, 0) for F in a["formations"].values()) for t in ("T1", "T2", "T3", "T4")})
