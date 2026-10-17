"""Builds engine/data/experimental/formation_provenance.json: for EVERY component of the 10 draft formations, how it relates to
the page-cited rules already in the packs. Curated by hand; nothing here changes a formation or marks anything verified.

Status vocabulary (alignment of the DRAFT definition with the cited rule):
  khop            the draft says the same thing as the cited rule
  long_hon        the draft is looser than the source (accepts more than the source does)
  chat_hon        the draft is stricter than the source
  khac            the draft says something different from the source (or contradicts its spirit)
  lien_quan       the source speaks about the same stars/structure, but not in this role/condition
  khong_co_nguon  no cited rule in the packs; a design hypothesis of the draft
Rule ids are looked up in the packs: book, page and review status come from the pack, never typed here."""
import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "engine"
R = {}
for f in sorted(glob.glob(str(ROOT / "data" / "pack_*.json"))):
    for r in json.load(open(f, encoding="utf-8"))["rules"]:
        R[r["id"]] = r

KL55, KL228 = "TV_KL_PHU_TU_PHU_TUAN_TRIET", "TV_KL_AUX_TUAN_TRIET"
KL58, TT34 = "TV_KL_PHU_CU_TY_NGO_TAM_HOA", "TV_TT_MENH_CU_TY_NGO_TAM_HOA"
KL64, KL66, KL215 = "TV_KL_STAR_MENH_KINH_PHUC_LOC", "TV_KL_STAR_MENH_TAM_KY_KY_KINH", "TV_KL_CUNG_MENH_GIAP_KHOI_VIET"
TH72, KL52, TT24, KL221, KL221B = "TV_TH_CACH_MENH_NHAT_NGO", "TV_KL_PHU_DUONG_NGO", "TV_TT_MENH_CNDL_CONG_CHUC", "TV_KL_CT_CNDL", "TV_KL_CT_CNDL_KQL_KV_XK"
KL224A, KL224B, TH77, TH76 = "TV_KL_CT_NHAT_NGUYET_DONG_CUNG", "TV_KL_CT_NHAT_NGUYET_CHIEU", "TV_TH_CACH_MENH_HA_CACH", "TV_TH_CACH_THIEN_DI_THAN_SPLT"
KL67, TH53, TH74B = "TV_KL_STAR_MENH_KY_KHOA", "TV_TH_AUX_MENH_HKY_KHOA", "TV_TH_CACH_MENH_BT_NN_TAN_HUNG"
TH94PHU, TH95TUONG, TH95CU = "TV_TH_STAR_THIEN_PHU_NAM_TUAN_TRIET", "TV_TH_STAR_THIEN_TUONG_NAM_TUAN_TRIET", "TV_TH_STAR_CU_MON_NAM_HAM_SAT"
KL217 = "TV_KL_CUNG_PHUC_DUC_TU_PHU_VU_TUONG"
TH74 = "TV_TH_CACH_MENH_SV_CUU_GIAI"


def C(status, rules=(), note=""):
    return {"status": status, "rules": list(rules), "note": note}


NO = C("khong_co_nguon", note="giả thuyết thiết kế của bản nháp, chưa có luật nguồn trong kho")
KY_KHOA = C("lien_quan", [KL67, TH53], "nguồn chỉ nói Hóa Kỵ gặp Hóa Khoa ở Hợi/Tý (kết quả tốt); bản nháp khái quát cho mọi vị trí")
TAM_HOA_CUU = C("long_hon", [TH74], "nguồn nói Mệnh ở bại địa hoặc tuyệt địa mà được Tam Hóa hội thì được cứu giải; bản nháp khái quát cho mọi yếu tố phá cách")
TUAN_TRIET = C("lien_quan", [KL228], "nguồn: Tuần hoặc Triệt đóng ở Mệnh thì vui ít buồn nhiều (điểm kém); việc coi đó là phản chứng hạ một bậc là suy diễn của bản nháp")
KHOA_QUYEN_LOC = C("khop", [KL64], "KL p.64: gặp Khoa, Quyền, Lộc (luật nguồn còn ở mức nháp)")

P = {
 "CACH_X_TU_PHU_VU_TUONG": {
  "core": C("lien_quan", [KL217], "nguồn có nhóm Tử Phủ Vũ Tướng ở các cung khác (Phúc Đức, Tử Tức, Nô Bộc); không có luật nói bốn sao hội ở tam phương Mệnh thành một cách"),
  "boosters": {"ta_huu_hoi": NO, "xuong_khuc_hoi": NO, "loc_hoi": NO},
  "breakers": {"sat_dong_cung": NO, "ky_dong_cung": NO},
  "rescuers": {"khoa_dong_cung": KY_KHOA, "tam_hoa_hoi_cuu": TAM_HOA_CUU},
  "refutations": {"tuan_triet_an_ngu": C("lien_quan", [TH94PHU, KL228], "nguồn: Thiên Phủ gặp Tuần/Triệt là điều kỵ nhất (TH p.94); chưa có nguồn cho cả nhóm bốn sao"),
                  "Thiên_Tướng_ham": C("lien_quan", [TH95TUONG], "nguồn nói Thiên Tướng gặp Tuần/Triệt như hãm; không nói Tướng hãm hạ cả cách")}},
 "CACH_X_TU_PHU_DONG_CUNG": {
  "core": C("lien_quan", [KL55], "KL p.55 lấy Tử Vi và Thiên Phủ đồng cung ở Mệnh làm khung nhưng không gọi là một cách"),
  "boosters": {"ta_huu_hoi": NO, "xuong_khuc_hoi": NO, "khoi_viet_hoi": NO},
  "breakers": {"sat_dong_cung": NO, "ky_dong_cung": NO},
  "rescuers": {"khoa_dong_cung": KY_KHOA, "tam_hoa_hoi_cuu": TAM_HOA_CUU},
  "refutations": {"tuan_triet_an_ngu": C("khop", [KL55, TH94PHU], "KL p.55: Tử Phủ bị Tuần hoặc Triệt án ngữ thì phúc lộc kém đi; TH p.94: Thiên Phủ kỵ Tuần, Triệt")}},
 "CACH_X_CO_NGUYET_DONG_LUONG": {
  "core": C("khop", [TT24, KL221], "Toàn Thư p.24: Mệnh đủ bốn sao Cơ Nguyệt Đồng Lương trong tam phương"),
  "boosters": {"cat_tinh_hoi": C("lien_quan", [TT24, KL221B], "TT p.24: thiếu cát tinh trợ lực thì chỉ ở mức công chức bình thường; KL p.221 (nháp): hội Khôi Việt, Xương Khúc thì hợp đường học thuật"),
               "khoa_quyen_loc_hoi": C("lien_quan", [KL221B], "luật nháp có trang (KL p.221): hội Khoa Quyền Lộc thì hợp đường học thuật")},
  "breakers": {"khong_kiep_dong_cung": NO, "ky_dong_cung": NO},
  "rescuers": {"khoa_dong_cung": KY_KHOA, "tam_hoa_hoi_cuu": TAM_HOA_CUU},
  "refutations": {"tuan_triet_an_ngu": TUAN_TRIET}},
 "CACH_X_SAT_PHA_LIEM_THAM": {
  "core": C("lien_quan", [TH77, TH76], "ngưỡng ba trong bốn sao là quy ước của bản nháp; nguồn nói về chính tinh Sát Phá Liêm Tham ở Mệnh/Thân"),
  "boosters": {"khoa_quyen_hoi": C("lien_quan", [TH76], "nguồn (nháp): miếu vượng, hội nhiều cát tinh thì có thể phát mạnh, nói cho Thân cư Thiên Di"),
               "ta_huu_hoi": C("lien_quan", [TH76]), "xuong_khuc_hoi": C("lien_quan", [TH76]), "khoi_viet_hoi": C("lien_quan", [TH76])},
  "breakers": {"ba_sat_va_ky_trong_tam_phuong": C("khop", [TH77], "TH p.77 (luật nguồn còn ở mức nháp): hạ cách khi từ ba sát tinh hội kèm Hóa Kỵ"),
               "ky_dong_cung": C("lien_quan", [TH77])},
  "rescuers": {"khoa_dong_cung": KY_KHOA, "tam_hoa_hoi_cuu": TAM_HOA_CUU},
  "refutations": {"tuan_triet_an_ngu": TUAN_TRIET, "Thất_Sát_ham": C("lien_quan", [TH76], "nguồn đòi chính tinh nhập miếu vượng mới phát mạnh")}},
 "CACH_X_NHAT_NGUYET_TINH_MINH": {
  "core": C("khop", [KL224A, KL224B], "hai luật có trang: Nhật Nguyệt đồng cung hoặc chiếu Mệnh"),
  "boosters": {"nhat_nguyet_deu_sang": C("lien_quan", [TH74B], "nguồn (nháp) nói Nhật hoặc Nguyệt hãm gặp sát tinh là tàn hung, nên độ sáng có liên quan"),
               "ta_huu_hoi": NO, "khoa_quyen_hoi": NO},
  "breakers": {"nhat_nguyet_ham_gap_sat": C("long_hon", [TH74B], "TH p.74 (nháp): Nhật hoặc Nguyệt hãm Ở MỆNH gặp sát tinh; bản nháp xét sát tinh trong cả tam phương"),
               "ky_dong_cung": NO, "khong_kiep_dong_cung": C("lien_quan", [TH74B], "nguồn nói sát tinh gặp Nhật/Nguyệt hãm; không nói riêng Không Kiếp")},
  "rescuers": {"khoa_dong_cung": KY_KHOA, "tam_hoa_hoi_cuu": TAM_HOA_CUU},
  "refutations": {"Thái_Dương_ham": C("long_hon", [TH74B], "nguồn đòi hãm VÀ gặp sát tinh mới là tàn hung; bản nháp chỉ cần hãm"),
                  "Thái_Âm_ham": C("long_hon", [TH74B], "như trên"), "tuan_triet_an_ngu": TUAN_TRIET}},
 "CACH_X_NHAT_LE_TRUNG_THIEN": {
  "core": C("khop", [TH72, KL52], "Thực Hành p.72: Thái Dương cư Ngọ có Mệnh là cách Nhật lệ trung thiên"),
  "boosters": {"ta_huu_hoi": NO, "khoa_quyen_hoi": NO, "xuong_khuc_hoi": NO},
  "breakers": {"sat_dong_cung": NO, "ky_dong_cung": NO},
  "rescuers": {"khoa_dong_cung": KY_KHOA, "tam_hoa_hoi_cuu": TAM_HOA_CUU},
  "refutations": {"tuan_triet_an_ngu": TUAN_TRIET, "Thái_Dương_ham": C("lien_quan", [TH74B], "nguồn nói Thái Dương hãm gặp sát tinh là tàn hung")}},
 "CACH_X_THACH_TRUNG_AN_NGOC": {
  "core": C("khop", [KL58, TT34], "cả hai luật nguồn lấy Cự Môn ở Tý/Ngọ làm nền"),
  "boosters": {"tam_hoa_hoi_du": C("khop", [KL58, TT34], "hai luật nguồn: Cự Môn ở Tý/Ngọ hội đủ Khoa, Quyền, Lộc thì như ngọc ẩn trong đá"),
               "ta_huu_hoi": NO},
  "breakers": {"ky_hoac_kinh_dong_cung": C("khop", [KL66], "KL p.66: khi Khoa Quyền Lộc hội mà Hóa Kỵ hoặc Kình đồng cung thì mờ mịt; áp cho cấu trúc Tam Hóa hội của cách này")},
  "rescuers": {"khoa_dong_cung": KY_KHOA},
  "refutations": {"tuan_triet_an_ngu": TUAN_TRIET, "Cự_Môn_ham": C("lien_quan", [TH95CU], "nguồn: Cự Môn hãm hội sát tinh thì suốt đời cùng khổ")}},
 "CACH_X_MA_DAU_DOI_KIEM": {
  "core": C("khop", [KL64], "KL p.64 (luật còn ở mức nháp): Kình Dương ở Ngọ"),
  "boosters": {"khoa_quyen_loc_hoi": KHOA_QUYEN_LOC, "ta_huu_hoi": NO},
  "breakers": {"that_sat_trong_tam_phuong": C("khop", [KL64], "KL p.64 (luật nguồn còn ở mức nháp): tránh Thất Sát; sao Hình chưa được kiểm nên chưa đưa vào"),
               "sat_khac_dong_cung": NO, "ky_dong_cung": NO},
  "rescuers": {"khoa_dong_cung": KY_KHOA, "tam_hoa_hoi_cuu": TAM_HOA_CUU},
  "refutations": {"tuan_triet_an_ngu": TUAN_TRIET}},
 "CACH_X_TAM_KY_GIA_HOI": {
  "core": C("khop", [KL66], "Khoa, Quyền, Lộc cùng hội ở tam phương Mệnh"),
  "boosters": {"hoa_o_ban_cung": NO, "ta_huu_hoi": NO, "xuong_khuc_hoi": NO},
  "breakers": {"ky_hoac_kinh_dong_cung": C("khop", [KL66], "KL p.66: Hóa Kỵ hoặc Kình Dương đồng cung thì công danh mờ mịt")},
  "rescuers": {"ta_huu_giai_ky": NO},
  "refutations": {"tuan_triet_an_ngu": TUAN_TRIET}},
 "CACH_X_KHOI_VIET_GIAP_MENH": {
  "core": C("khop", [KL215], "Khôi, Việt giáp hai bên Mệnh"),
  "boosters": {"co_chinh_tinh": NO, "ta_huu_hoi": NO, "xuong_khuc_hoi": NO},
  "breakers": {"sat_dong_cung": NO, "ky_dong_cung": NO},
  "rescuers": {"khoa_dong_cung": KY_KHOA, "tam_hoa_hoi_cuu": TAM_HOA_CUU},
  "refutations": {"vo_chinh_dieu": NO, "tuan_triet_an_ngu": TUAN_TRIET}},
}


def resolve(c):
    out = {**c, "sources": []}
    for rid in out.pop("rules"):
        r = R[rid]
        page = re.findall(r"\[((?:KL|TH|TT)\s*pp?\.[\d\-–, ]+)", r["description"])
        out["sources"].append({"rule": rid, "source": (r.get("sourceIds") or [""])[0], "page": page[0] if page else "", "review": r["reviewStatus"]})
    return out


# Why a condition is dead (never active) or always active, found by tools/enumerate_formation_reach.py. Curated: the builder refuses
# to run if the scan finds a dead/always condition that has no entry here, so a definition change forces a human look.
REACH_REASON = {
 ("CACH_X_TU_PHU_VU_TUONG", "refutations", "Thiên_Tướng_ham"): "Thiên Tướng chỉ hãm ở Mão và Dậu (bảng Thực Hành), mà khi Tử Phủ Vũ Tướng hội đủ ở tam phương thì Thiên Tướng không bao giờ rơi vào hai cung đó",
 ("CACH_X_TU_PHU_DONG_CUNG", "rescuers", "tam_hoa_hoi_cuu"): "Tử Phủ đồng cung chỉ ở Dần hoặc Thân; Hóa Lộc, Quyền, Khoa chưa bao giờ cùng hội đủ trong tam phương của hai cung này (vét cạn 525.960 lá số)",
 ("CACH_X_NHAT_LE_TRUNG_THIEN", "refutations", "Thái_Dương_ham"): "cách đòi Thái Dương ở Ngọ, mà bảng Thực Hành xếp Thái Dương ở Ngọ là vượng, không thể hãm",
 ("CACH_X_THACH_TRUNG_AN_NGOC", "refutations", "Cự_Môn_ham"): "cách đòi Cự Môn ở Tý hoặc Ngọ, mà bảng Thực Hành xếp Cự Môn ở hai cung này là vượng, không thể hãm",
}
IMPOSSIBLE = {
 "CACH_X_TU_PHU_DONG_CUNG|pha_duoc_cuu": "bất khả thi THEO ĐỊNH NGHĨA VÀ HÌNH HỌC LÁ SỐ, không phải lỗi engine: Tử Phủ đồng cung chỉ xảy ra ở Dần hoặc Thân. Muốn được cứu thì phải có Hóa Khoa đồng cung với Hóa Kỵ, nhưng với mọi can năm hai sao Khoa và Kỵ không bao giờ cùng cung với Tử Vi và Thiên Phủ; hoặc phải có Tam Hóa đủ ba trong tam phương, điều chưa từng xảy ra ở hai cung này (vét cạn 525.960 lá số)",
}


def main():
    form = json.load(open(ROOT / "data" / "experimental" / "formations_experimental.json", encoding="utf-8"))["formations"]
    out = {"version": 1, "note": "Hand-curated alignment of the DRAFT formations with page-cited rules in the packs. No formation is verified.", "formations": {}}
    for f in form:
        mine = P[f["id"]]
        comps = {"core": resolve(mine["core"])}
        for kind in ("boosters", "breakers", "rescuers", "refutations"):
            comps[kind] = {e["id"]: resolve(mine[kind][e["id"]]) for e in f[kind]}
        out["formations"][f["id"]] = comps
    reach_path = ROOT / "tests" / "fixtures" / "formation_reach.json"
    if reach_path.exists():
        reach = json.load(open(reach_path, encoding="utf-8"))
        ev, n_all = reach["evidence_active_when_core_true"], reach["charts_per_formation"]
        missing = []
        for fid, comps in out["formations"].items():
            core_n = ev.get(f"{fid}|core", 0)
            comps["core"]["reach"] = {"core_true": core_n, "of": n_all}
            for kind in ("boosters", "breakers", "rescuers", "refutations"):
                for eid, e in comps[kind].items():
                    n = ev.get(f"{fid}|{kind}|{eid}", 0)
                    e["reach"] = {"active": n, "core_true": core_n, "never": n == 0, "always": n == core_n}
                    if (e["reach"]["never"] or e["reach"]["always"]) and (fid, kind, eid) not in REACH_REASON:
                        missing.append((fid, kind, eid))
                    if (fid, kind, eid) in REACH_REASON:
                        e["reach"]["reason"] = REACH_REASON[(fid, kind, eid)]
        if missing:
            raise SystemExit(f"dead/always conditions without a curated reason: {missing}")
        bad = [c for c in reach["unreachable"] if c not in IMPOSSIBLE]
        if bad:
            raise SystemExit(f"unreachable cells without a curated explanation: {bad}")
        out["known_impossible"] = [{"cell": c, "kind": "theo_dinh_nghia", "reason": IMPOSSIBLE[c]} for c in reach["unreachable"]]
        out["reach_scan"] = {"charts_per_formation": n_all, "range": "60 năm liên tiếp (1950-2009), mọi ngày dương lịch, 12 chi giờ, hai giới"}
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
