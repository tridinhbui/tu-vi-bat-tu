"""Star natures and palace relations for the seven thin palaces (plan 2026-10-23 P1), from the page-checked natures of engine/data/kg/mined
(quote and page taken from the mined entry): new `use` values allies, travel, fortune, children, siblings, parents, health (health: what a
star DOES at Tật Ách — cứu giải — never a health state). Also widens the `use` / `explains` of the natures Khảo Luận states for ANY palace
("đóng ở cung nào cũng …", "đi đến đâu cũng …") to the new palaces. Idempotent; test: engine/tests/test_star_nature.py."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KG = ROOT / "engine" / "data" / "kg"
MINED = {}
for f in sorted((KG / "mined").glob("kl_*.json")):
    for n in json.loads(f.read_text("utf-8")).get("natures", []):
        MINED.setdefault(n["id"], n)

NEW_USES = ["allies", "travel", "fortune", "children", "siblings", "parents", "health"]
PEOPLE = ["ally.", "kin.", "parents.", "travel.", "fortune.", "health.", "life.blessed", "life.hardship", "outside."]
# (id, mined id, star, also, text, use, pol, explains, palace)
E = [
 ("khoi_viet.quy_nhan", "khoi_viet.quy_nhan", "Thiên Khôi", ["Thiên Việt"], "thực sự là hai quý nhân", ["allies", "travel"], "+", ["travel.helped", "social.support", "outside.favorable", "ally.powerful"], None),
 ("ta_huu.tay_sai", "ta_huu.tay_sai", "Tả Phụ", ["Hữu Bật"], "tượng trưng cho người phụ tá, người giúp việc, người bảo vệ", ["allies"], "+", ["ally.helpful", "ally.many", "ally.loyal"], None),
 ("ta_huu.nguoi_doi_giup", "giai.nguoi_doi_giup", "Tả Phụ", ["Hữu Bật"], "biểu hiện sự giúp đỡ của người đời", ["travel", "siblings", "children"], "+", ["travel.helped", "kin.many"], None),
 ("quang_quy.troi_giup", "quang_quy.troi_giup", "Ân Quang", ["Thiên Quý"], "biểu hiện sự giúp đỡ của Trời", ["fortune", "travel", "children"], "+", ["fortune.protected", "travel.helped", "life.blessed", "kin.filial"], None),
 ("thanh_long.giao_te", "thanh_long.giao_te", "Thanh Long", [], "tượng trưng cho thành công trong giao tế", ["travel", "allies"], "+", ["outside.favorable", "travel.helped", "ally.many"], None),
 ("song_hao.du_lich", "song_hao.du_lich", "Đại Hao", ["Tiểu Hao"], "còn biểu hiện cho sự đi lại, du lịch", ["travel"], "±", ["life.mobility", "travel.costly"], None),
 ("tu_duc.ban_tot", "tu_duc.ban_tot", "Long Đức", ["Phúc Đức", "Nguyệt Đức", "Thiên Đức"], "là bộ sao của người bạn tốt hay giúp đỡ", ["allies"], "+", ["ally.helpful", "ally.loyal"], None),
 ("thien_ma.du_lich", "thien_ma.du_lich", "Thiên Mã", [], "tượng trưng cho thay đổi, đi lại, du lịch", ["travel"], "±", ["life.mobility", "outside.active", "travel.toil", "kin.apart"], None),
 ("hoa_quyen.di_chuyen", "hoa_quyen.di_chuyen", "Hóa Quyền", [], "còn tượng trưng cho di chuyển, du lịch", ["travel"], "±", ["life.mobility", "outside.active"], None),
 ("hoa_ky.do_ky", "hoa_ky.do_ky", "Hóa Kỵ", [], "chủ đố kỵ, ghen ghét, dèm pha", ["allies", "travel", "siblings", "children", "parents"], "-", ["ally.slander", "ally.disloyal", "ally.resent", "travel.dispute", "kin.strain", "parents.strain"], None),
 ("tham_lang.giao_te", "tham_lang.giao_te", "Tham Lang", [], "thích giao tế, hay lui tới chốn đông vui", ["allies", "travel"], "±", ["ally.many", "ally.greedy", "outside.active"], None),
 ("cu_mon.dieu_tieng", "cu_mon.chu_khoa", "Cự Môn", [], "chủ điều tiếng", ["travel", "allies", "parents", "siblings"], "-", ["travel.dispute", "ally.resent", "parents.strain", "kin.strain"], None),
 ("liem_trinh.soi_moi", "liem_trinh.chu_khoa", "Liêm Trinh", [], "hay soi mói, xét nét", ["allies", "travel"], "-", ["ally.resent", "travel.dispute"], None),
 ("pha_quan.chu_no_tu", "pha_quan.chu_no_boc", "Phá Quân", [], "chủ các việc phu thê, nô bộc và tử tức, mà vào số là hao", ["allies", "children"], "-", ["ally.drain", "ally.weak", "ally.fickle", "kin.few"], None),
 ("thien_tuong.phuc_duc", "thien_tuong.chu_khoa", "Thiên Tướng", [], "chủ phúc đức", ["fortune"], "+", ["life.blessed"], None),
 ("tu_vi.cuu_kho", "tu_vi.chu_khoa", "Tử Vi", [], "cứu khổ cứu nạn", ["fortune", "health"], "+", ["life.mitigated", "health.shielded", "life.blessed"], None),
 ("thien_dong.chu_te_phuc", "thien_dong.chu_te_phuc", "Thiên Đồng", [], "là sao chủ tể của cung Phúc Đức", ["fortune"], "+", ["life.blessed", "inner.peace"], "Phúc Đức"),
 ("thien_luong.phuc_tho", "thien_luong.chu_phuc_tho", "Thiên Lương", [], "là sao chủ về phúc thọ", ["fortune"], "+", ["life.blessed", "inner.peace"], None),
 ("thien_tuong.dong_dau_phuc_day", "thien_tuong.dong_dau_phuc_day", "Thiên Tướng", [], "đóng ở đâu thì phúc ở đó", ["fortune", "parents"], "+", ["life.blessed", "parents.prosper", "fam.positive", "kin.harmony"], None),
 ("tu_vi.ban_phuc", "tu_vi.ban_phuc", "Tử Vi", [], "ban phúc nhiều hơn lộc, ban sức khỏe và cứu giải nhiều hơn tiền bạc", ["fortune", "parents"], "+", ["life.blessed", "life.mitigated", "kin.harmony"], None),
 ("quan_phuc.phuc_tinh", "quan_phuc.phuc_tinh", "Thiên Quan", ["Thiên Phúc"], "đều là phúc tinh, chủ cứu giải, đức độ", ["fortune", "health"], "+", ["life.blessed", "fortune.clan_prosper", "life.mitigated", "health.shielded"], None),
 ("thai_duong.cha", "thai_duong.bieu_tuong_cha", "Thái Dương", [], "là biểu tượng người cha", ["parents"], "±", ["parents.", "fam.", "kin.harmony", "kin.strain"], None),
 ("thai_am.me", "thai_am.bieu_tuong_me", "Thái Âm", [], "là biểu tượng người mẹ", ["parents"], "±", ["parents.", "fam.", "kin.harmony", "kin.strain"], None),
 ("tham_lang.it_hop_tu", "kl102_tham_lang_it_hop_tu", "Tham Lang", [], "ít hợp với cung Tử Tức", ["children"], "-", ["kin.late", "kin.wayward", "kin.few"], "Tử Tức"),
 ("loc_ton.cham_tre", "kl133_loc_ton_cham_tre", "Lộc Tồn", [], "cũng có nghĩa là chậm trễ", ["children"], "-", ["kin.late"], None),
 ("phi_liem.hiem_muon", "kl137_phi_liem_hiem_muon", "Phi Liêm", [], "tượng trưng cho mau mắn, lanh lợi và hiếm muộn", ["children", "siblings"], "-", ["kin.few", "kin.late"], None),
 ("long_phuong.sinh_no", "kl149_long_phuong_sinh_no", "Long Trì", ["Phượng Các"], "chủ may mắn trong hôn nhân và sinh nở", ["children"], "+", ["kin.good", "kin.many"], None),
 ("truong_sinh.sinh_de", "kl160_truong_sinh_sinh_de", "Trường Sinh", [], "tượng trưng cho bền vững, tốt cho sinh đẻ", ["children", "siblings"], "+", ["kin.many", "kin.good"], None),
 ("de_vuong.sinh_no", "kl162_de_vuong_giai_benh", "Đế Vượng", [], "gia tăng phúc thọ, giải trừ bệnh tật, tai họa, lợi cho sinh nở", ["children", "siblings", "health"], "+", ["kin.many", "kin.good", "health.shielded"], None),
 ("suy.sa_sut", "kl162_suy_sa_sut", "Suy", [], "chủ yếu đuối, suy thoái, ở cung nào cũng tượng trưng sa sút", ["children", "fortune", "siblings"], "-", ["kin.few", "fortune.clan_decline"], None),
 ("khong_kiep.bat_kha_khang", "kl126_khong_kiep_nghiep_chuong", "Địa Không", ["Địa Kiếp"], "tượng trưng cho những trường hợp bất khả kháng, khó chế ngự", ["children", "siblings", "parents", "allies", "health"], "-",
  ["kin.wayward", "kin.apart", "kin.burden", "parents.apart", "parents.burden", "ally.disloyal", "health.exposed"], None),
 ("hoa_linh.xa_anh_em", "kl200_hoa_linh_xa_anh_em", "Hỏa Tinh", ["Linh Tinh"], "thích cô độc, xa lánh anh em", ["siblings"], "-", ["kin.apart", "kin.strain"], "Huynh Đệ"),
 ("thien_phu.giai_tai_ach", "kl96_thien_phu_giai_tai_ach", "Thiên Phủ", [], "là sao giải tai ách", ["health"], "+", ["health.shielded", "life.mitigated"], None),
 ("thien_luong.cuu_giai", "kl109_thien_luong_cuu_giai", "Thiên Lương", [], "có tính cứu giải tai họa, bệnh tật", ["health"], "+", ["health.shielded", "life.mitigated"], None),
 ("cuu_giai.manh", "kl120_cuu_giai_manh", "Vũ Khúc", ["Hóa Khoa", "Tử Vi", "Thiên Phủ", "Thiên Lương", "Thiên Đồng", "Tuần", "Triệt"], "là một trong các sao cứu giải mạnh", ["health"], "+", ["health.shielded", "life.mitigated"], None),
 ("thien_y.cuu_giai", "kl122_thien_y_cuu_giai", "Thiên Y", [], "là sao cứu giải bệnh tật", ["health"], "+", ["health.shielded"], None),
 ("tuan_triet.bao_ve_vcd", "kl146_tuan_triet_bao_ve_vcd", "Tuần", ["Triệt"], "bảo vệ cung vô chính diệu, che chắn không cho hung tinh bên ngoài xâm nhập", ["health", "fortune", "children", "siblings"], "+", ["health.shielded", "life.mitigated"], None),
 ("tu_duc.giai_nho", "kl149_tu_duc_giai_benh_nho", "Thiên Đức", ["Nguyệt Đức", "Long Đức", "Phúc Đức"], "giải trừ các tai họa nhỏ", ["health"], "+", ["health.shielded", "life.mitigated"], None),
]
# (id, mined id, palace, text, when, with, chapters)
REL = [
 ("than.di", "than.di", "Thiên Di", "Thân cư Thiên Di thì phải bôn ba ngoài xã hội, lấy nghĩa khí, trung tín mà giao tiếp bạn bè mới mong thành đạt", "than", None, None),
 ("no.giau_ngheo_vi_ban", "no.giau_ngheo_vi_ban", "Nô Bộc", "giàu có thể nhờ bạn mà nghèo cũng có thể vì bạn", None, ["Tài Bạch"], ["no_boc"]),
 ("no.tuy_ket_hop", "no.tuy_ket_hop", "Nô Bộc", "sao ở cung Nô Bộc tốt hay xấu còn tùy vào sự kết hợp với các sao khác", None, None, None),
 ("di.giao_thiep", "di.giao_thiep", "Thiên Di", "Thiên Di là chỗ giao thiệp bên ngoài, gần hay xa đều thuộc Thiên Di", None, ["Nô Bộc"], ["thien_di", "no_boc"]),
 ("di.chinh_tinh_nhan_vat", "di.chinh_tinh_nhan_vat", "Thiên Di", "chính tinh ở Thiên Di là hình ảnh những người mình thường gặp", None, ["Thiên Di"], ["thien_di"]),
 ("di.menh_phuc_do", "menh_phuc.di_tat_van_do", "Thiên Di", "Mệnh và Phúc Đức tốt thì Thiên Di, Tật Ách có gặp hung sát tinh cũng đỡ xấu", None, ["Mệnh", "Phúc Đức"], ["thien_di", "tat_ach"]),
 ("phuc.cuu_menh_than", "phuc.cuu_menh_than", "Phúc Đức", "Mệnh, Thân gặp hung sát tinh mà cung Phúc Đức có phúc tinh đắc địa thì có thể cứu vãn", None, ["Mệnh"], ["phuc_duc"]),
 ("phuc.dep_hon_cac_cung", "phuc.dep_hon_cac_cung", "Phúc Đức", "cung Phúc Đức đẹp thì dù các cung khác xấu cũng không đáng lo lắm, còn Phúc Đức xấu mà các cung khác đẹp thì đừng vội mừng", None, None, ["phuc_duc"]),
 ("phuc.nu_menh_phu_phuc", "th.nu_menh_phu_phuc", "Phúc Đức", "xem số nữ mệnh phải xét cả cung Phu Thê và cung Phúc Đức mới luận được hay dở", "nu", ["Phu Thê", "Phúc Đức"], ["phu_the", "phuc_duc"]),
 ("phu_mau.qua_dep_tat_kem", "phu_mau.qua_dep_tat_kem", "Phụ Mẫu", "cung Phụ Mẫu quá đẹp thì cung Tật Ách lại heo hút", None, ["Tật Ách"], ["phu_mau"]),
 ("tu.ve_gia", "kl218_tu_ve_gia", "Tử Tức", "cung Tử Tức cũng là hình ảnh đời mình lúc về già", None, None, ["tu_tuc"]),
 ("tat.tho_au_cuoi_doi", "kl218_tat_tho_au_ve_gia", "Tật Ách", "cung Tật Ách là hình ảnh thuở đầu đời và cũng là hình ảnh lúc cuối đời", None, None, ["tat_ach"]),
 ("menh.quan_di_tai", "menh.quan_di_tai", "Mệnh", "các cung Quan Lộc, Thiên Di, Tài Bạch có nhiều ảnh hưởng đến Mệnh", None, ["Quan Lộc", "Thiên Di", "Tài Bạch"], ["menh"]),
]
GENERIC = ["hoa_ky.cung", "hoa_loc.tien", "song_hao.giam", "kinh_da.can_tro", "khong_kiep.pha", "hoa_linh.hao_mon", "khoi_viet.loi", "thien_tuong.on_dinh", "tu_vi.cuu_giai", "ta_huu.phu_ta"]
# natures whose words fit any palace's limit or plenty ("ở cung nào cũng …"): they may explain a reading of the new palaces; the others only
# take the new uses (told as the palace's structure, never as the reason of a reading)
EXPLAINS_ANY = {"hoa_ky.cung", "hoa_loc.tien", "song_hao.giam", "kinh_da.can_tro", "khong_kiep.pha", "hoa_linh.hao_mon"}

d = json.loads((KG / "star_nature.json").read_text("utf-8"))
ent = {e["id"]: e for e in d["entries"]}
for nid, mid, star, also, text, use, pol, explains, palace in E:
    m = MINED[mid]
    e = {"id": nid, "star": star, **({"also": also} if also else {}), "page": m["page"], "quote": m["quote"], "text": text, "use": use,
         **({"pol": pol} if pol != "+" else {}), "explains": explains, **({"palace": palace} if palace else {}), **({"book": m["book"]} if m["book"] != "KL" else {})}
    ent[nid] = e
for gid in GENERIC:
    g = ent[gid]
    g["use"] = list(dict.fromkeys(g["use"] + NEW_USES))
    if "explains" in g and gid in EXPLAINS_ANY:
        g["explains"] = list(dict.fromkeys(g["explains"] + PEOPLE))
    elif "explains" in g:
        g["explains"] = [x for x in g["explains"] if x not in PEOPLE]
d["entries"] = list(ent.values())
rel = {r["id"]: r for r in d["relations"]}
for rid, mid, palace, text, when, with_, chapters in REL:
    m = MINED[mid]
    rel[rid] = {"id": rid, "palace": palace, "page": m["page"], "quote": m["quote"], "text": text, **({"when": when} if when else {}), **({"with": with_} if with_ else {}),
                **({"chapters": chapters} if chapters else {}), **({"book": m["book"]} if m["book"] != "KL" else {})}
d["relations"] = list(rel.values())
(KG / "star_nature.json").write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", "utf-8")
print(len(d["entries"]), "entries,", len(d["relations"]), "relations")
