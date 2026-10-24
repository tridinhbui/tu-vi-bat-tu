"""DEEP-3 knowledge structures (plan Workstream C, 2026-10-24), all from the page-checked raw entries of engine/data/kg/mined/deep3_*.json:

    engine/data/kg/che_hoa.json   tamer -> tamed relations ("chế hóa"): Tuần / Triệt, Hóa Khoa, Hóa Lộc, Thiên Quan / Phúc, the stars that
                                  master or resist the sát tinh, the sát that spoil a star; with effect, conditions and page
    engine/data/kg/combos.json    the chính tinh groups (KL pp.166-167), the twelve 'thế đứng' of Tử Vi (KL pp.179-186), named pairs with their
                                  page-checked meaning, modifiers, and per palace the verified rules that read the pair there
    engine/data/kg/schools.json   points where Khảo Luận, Thực Hành, Toàn Thư (Vũ Tài Lục's translation), 紫微斗數全書 (Hán văn) and Thiên Lương
                                  disagree, each side with its statement and page / section
    engine/data/kg/star_nature.json   + Thực Hành p.80 'Hành của Nam Bắc tinh' (book TH; entries carry no domain they explain, so the depth layer
                                  does not voice them yet)
    engine/data/kg/van_han_books.json + Thực Hành pp.130-132 'Ảnh hưởng sao nhập hạn' (kind 'th', same condition vocabulary as the Toàn Thư entries)

Every item keeps the mined id; quote / page come from that entry (engine/tests/test_deep3_tuvi.py re-checks them).
    .venv/bin/python tools/build_deep3_kg.py"""
import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "engine" / "data"
KG = D / "kg"
MINED = {}
for f in sorted((KG / "mined").glob("deep3_*.json")):
    for e in json.loads(f.read_text("utf-8"))["entries"]:
        MINED[e["id"]] = e

SAT = ["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"]
CAT = ["Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"]
MAJORS = ["Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh", "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn", "Thiên Tướng",
          "Thiên Lương", "Thất Sát", "Phá Quân"]
GROUPS = {"@sat_tinh": SAT, "@cat_tinh": CAT, "@chinh_tinh": MAJORS, "@tuan_triet": ["Tuần", "Triệt"], "@moi_sao": ["*"]}


def src(mid, skipped_ok=False):
    """a skipped entry (not made a rule) can still be a side of a school difference: its quote was checked all the same"""
    e = MINED[mid]
    assert skipped_ok or not e.get("skip"), mid
    assert e["quote_checked"], mid
    return {"mined": mid, "book": e["book"], "page": e["page"], "quote": e["quote"]}


def cite(mid):
    e = MINED[mid]
    if e["book"].startswith("WEB:"):
        return f"TTH {e['book'].rsplit('_', 1)[1]} {e['page']}"
    if e["book"].startswith("SCAN:"):
        return f"TL scan p.{e['page']}"
    return f"{e['book']} p.{e['page']}"


# ================================================================ che_hoa.json
EFFECTS = {
    "giam_xau": "sao chế làm nhẹ cái xấu của sao bị chế",
    "giam_tot": "sao chế làm giảm cái tốt của sao bị chế",
    "pha_ham": "sao chế giải cái hãm của chính tinh",
    "hai_mat": "giảm cả cái tốt lẫn cái xấu",
    "khang": "sao bị nêu không làm hại được sao chế (sách: 'không sợ')",
    "tang": "sao chế làm sao kia mạnh thêm",
    "cong_don": "hai sao cùng chỗ thì sức cộng lại",
}
CH = []


def ch(id, mid, tamer, tamed, effect, text, where=None, nature=None, also=()):
    assert effect in EFFECTS, effect
    d = {"id": id, "tamer": tamer, "tamed": tamed, "effect": effect, "text": text, **({"where": where} if where else {}),
         "sources": [src(m) for m in [mid, *also]], "cites": sorted({cite(m) for m in [mid, *also]})}
    if nature:
        d["star_nature"] = nature
    CH.append(d)


TT_ = ["Tuần", "Triệt"]
ch("tuan_triet.hai_mat", "kl203_tuan_triet_giam", TT_, ["@moi_sao"], "hai_mat", "Tuần, Triệt là sao cản phá: giảm cả cái tốt lẫn cái xấu của các sao")
ch("tuan_triet.dac_thanh_ham", "kl203_tuan_triet_dac_thanh_ham", TT_, ["@chinh_tinh"], "giam_tot", "chính tinh đắc địa gặp Tuần, Triệt thì như hãm địa",
   where={"dignity": ["miếu", "vượng", "đắc"]})
ch("tuan_triet.pha_ham", "kl204_chinh_tinh_ham_can_tt", TT_, ["@chinh_tinh"], "pha_ham", "chính tinh hãm ở Mệnh cần Tuần, Triệt để phá hãm",
   where={"palace": "Mệnh", "dignity": ["hãm"]})
ch("tuan_triet.cong_don", "kl204_tuan_triet_cung_cho", TT_, ["@moi_sao"], "cong_don", "Tuần và Triệt cùng một cung thì sức cản, sức giúp đều mạnh hơn",
   where={"both": True})
ch("tuan.thien_phu", "kl203_phu_tuan", ["Tuần"], ["Thiên Phủ"], "giam_tot", "Thiên Phủ gặp Tuần thành kho rỗng", also=["kl96_phu_tuan_khong_triet"])
ch("triet.thien_ma", "kl203_ma_triet", ["Triệt"], ["Thiên Mã"], "giam_tot", "Thiên Mã gặp Triệt thành ngựa què")
ch("triet.thien_tuong", "kl203_tuong_triet", ["Triệt"], ["Thiên Tướng"], "giam_tot", "Thiên Tướng gặp Triệt thành tướng mất đầu")
ch("tuan_triet.tu_phu", "kl55_tu_phu_tuan_triet", TT_, ["Tử Vi", "Thiên Phủ"], "giam_tot", "Tử Phủ ở Mệnh gặp Tuần, Triệt thì phúc lộc kém đi", where={"palace": "Mệnh"})
ch("sat.tu_vi", "kl75_tu_vi_so", ["Kình Dương", "Đà La", "Địa Không", "Địa Kiếp", "Tuần", "Triệt"], ["Tử Vi"], "giam_tot",
   "Kình, Đà, Không, Kiếp, Tuần, Triệt biến Tử Vi thành kẻ côi cút, mất sức cứu giải", also=["kl186_tu_so"])
ch("tu_vi.khang_hoa_linh", "kl75_tu_vi_khong_so_hoa_linh", ["Tử Vi"], ["Hỏa Tinh", "Linh Tinh"], "khang", "Tử Vi không sợ Hỏa, Linh")
ch("hoa_linh.thien_co", "kl81_co_so_hoa_linh_thich_hao", ["Hỏa Tinh", "Linh Tinh"], ["Thiên Cơ"], "giam_tot", "Thiên Cơ rất sợ Hỏa, Linh")
ch("song_hao.thien_co", "kl81_co_so_hoa_linh_thich_hao", ["Đại Hao", "Tiểu Hao"], ["Thiên Cơ"], "tang", "Thiên Cơ rất thích Song Hao; Cự Cơ Mão Dậu gặp Song Hao thì phú quý")
ch("tuan_triet.nhat_sat", "kl85_nhat_tuan_triet_cuu", TT_, ["Kình Dương", "Đà La", "Địa Không", "Địa Kiếp"], "giam_xau",
   "Thái Dương gặp Kình, Đà, Không, Kiếp thì cần Tuần, Triệt cứu giải để giảm bớt đau thương", where={"with": ["Thái Dương"]})
ch("thien_dong.khang_tuan_triet", "kl91_dong_khong_so_tuan_triet", ["Thiên Đồng"], TT_, "khang", "Thiên Đồng không sợ Tuần, Triệt (có ý kiến cho là cần, để bớt thay đổi)")
ch("triet.tu_vi", "kl96_phu_tuan_khong_triet", ["Triệt"], ["Tử Vi"], "giam_tot", "Tử Vi rất sợ Triệt")
ch("thien_phu.khang_triet", "kl96_phu_tuan_khong_triet", ["Thiên Phủ"], ["Triệt"], "khang", "Thiên Phủ không sợ Triệt", also=["kl188_phu_so_khong"])
ch("ky_kk.thien_phu", "kl96_phu_so_ky_kk", ["Hóa Kỵ", "Địa Không", "Địa Kiếp"], ["Thiên Phủ"], "giam_tot", "Thiên Phủ sợ Hóa Kỵ và Không Kiếp: Mệnh dễ nghèo")
ch("thien_khong.thien_phu", "kl188_phu_so_khong", ["Tuần", "Thiên Không"], ["Thiên Phủ"], "giam_tot", "Thiên Phủ sợ Tuần không, Thiên không: kho trở nên rỗng")
ch("thien_phu.sat", "kl97_phu_giam_sat", ["Thiên Phủ"], ["@sat_tinh"], "giam_xau", "Thiên Phủ giảm bớt tính hung hăng của sát tinh", nature="thien_phu.che_sat")
ch("hoa_ky.tham_liem", "kl101_tham_liem_can_ky", ["Hóa Kỵ"], ["Tham Lang", "Liêm Trinh"], "giam_xau", "Tham Liêm đồng cung ở Tỵ, Hợi cần có Hóa Kỵ mới hóa giải nổi",
   where={"branch": ["Tỵ", "Hợi"], "both": True})
ch("hoa_khoa.cu_ham", "kl106_cu_ham_khoa", ["Hóa Khoa"], ["Cự Môn"], "pha_ham", "Cự Môn hãm cần Hóa Khoa cứu giải", where={"dignity": ["hãm"]})
ch("thien_tuong.sat", "kl108_tuong_che_sat", ["Thiên Tướng"], ["@sat_tinh"], "giam_xau", "Thiên Tướng không sợ sát tinh mà còn chế ngự được chúng")
ch("tuan_triet_hinh.thien_tuong", "kl108_tuong_so_tt_hinh", ["Tuần", "Triệt", "Thiên Hình"], ["Thiên Tướng"], "giam_tot",
   "Thiên Tướng sợ Tuần, Triệt, Thiên Hình: công danh trắc trở", also=["kl189_tuong_khong_so_kk"])
ch("thien_tuong.khang_kk", "kl189_tuong_khong_so_kk", ["Thiên Tướng"], ["Địa Không", "Địa Kiếp"], "khang", "Thiên Tướng không sợ Không Kiếp")
ch("thien_tuong.liem", "kl189_tuong_che_liem", ["Thiên Tướng"], ["Liêm Trinh"], "giam_xau", "Thiên Tướng chế ngự Liêm Trinh, canh chừng Phá Quân")
ch("tuan_triet_hoa_linh.thien_luong", "kl111_luong_so", ["Tuần", "Triệt", "Hỏa Tinh", "Linh Tinh"], ["Thiên Lương"], "giam_tot", "Thiên Lương sợ Tuần, Triệt, Hỏa, Linh")
ch("thien_luong.khang_kinh", "kl189_luong_khong_so_kinh", ["Thiên Lương"], ["Kình Dương"], "khang", "Thiên Lương không sợ Kình Dương")
ch("hao_kk_tt.thien_luong", "kl189_luong_khong_so_kinh", ["Đại Hao", "Tiểu Hao", "Địa Không", "Địa Kiếp", "Tuần", "Triệt"], ["Thiên Lương"], "giam_tot",
   "Thiên Lương gặp Song Hao, Không Kiếp, Tuần Triệt thì bị tai họa")
ch("tu_loc.that_sat", "kl113_sat_tu_loc_cuu", ["Tử Vi", "Lộc Tồn"], ["Thất Sát"], "giam_xau", "Thất Sát ở Mệnh hay gặp tai nạn, nhờ Tử Vi, Lộc Tồn cứu giải",
   where={"palace": "Mệnh"})
ch("that_sat.khang", "kl114_sat_khong_so", ["Thất Sát"], ["Tuần", "Triệt", "Kình Dương", "Đà La"], "khang",
   "Thất Sát không sợ Tuần Triệt, không ngán Kình Đà, còn sai khiến được chúng", nature="that_sat.che_kinh_da")
ch("pha_quan.kinh", "kl116_pha_che_kinh", ["Phá Quân"], ["Kình Dương"], "giam_xau", "Phá Quân chế ngự được Kình Dương")
ch("pha_quan.khang_tuan_triet", "kl117_pha_khong_so_tt", ["Phá Quân"], TT_, "khang", "Phá Quân không sợ Tuần Triệt")
ch("hoa_khoa.de_nhat_giai_than", "kl120_khoa_de_nhat_giai_than", ["Hóa Khoa"], ["@moi_sao"], "giam_xau", "Hóa Khoa là sao cứu giải mạnh nhất",
   nature="hoa_khoa.che_sat")
ch("thien_dia_giai", "kl120_thien_dia_giai", ["Thiên Giải", "Địa Giải"], ["@moi_sao"], "giam_xau", "Thiên Giải, Địa Giải là sao cứu giải nhỏ")
ch("kk.tu_vi", "kl125_kk_hoa_giai_tu", ["Địa Không", "Địa Kiếp"], ["Tử Vi"], "giam_tot", "một trong hai sao Không, Kiếp cũng đủ hóa giải hết hiệu lực của Tử Vi")
ch("xuong_khuc.khang_sat", "kl128_xuong_khuc_so_ky", ["Văn Xương", "Văn Khúc"], ["@sat_tinh"], "khang", "Xương Khúc không sợ sát tinh")
ch("hoa_ky.xuong_khuc", "kl128_xuong_khuc_so_ky", ["Hóa Kỵ"], ["Văn Xương", "Văn Khúc"], "giam_tot", "Xương Khúc chỉ sợ Hóa Kỵ")
ch("loc_ton.dao_hong", "kl133_loc_ton_che_dao_hong", ["Lộc Tồn"], ["Đào Hoa", "Hồng Loan"], "giam_xau", "Lộc Tồn chế ngự tính lả lơi của Đào Hồng")
ch("khoi_viet.bi_pha", "kl145_khoi_viet_so", ["Tuần", "Triệt", "Thiên Hình", "Hóa Kỵ", *SAT], ["Thiên Khôi", "Thiên Việt"], "giam_tot",
   "Khôi Việt sợ Tuần Triệt, Hình Kỵ, Kình Đà, Không Kiếp, Hỏa Linh: công danh trắc trở")
ch("triet.cat_tinh", "kl146_cat_tinh_so_triet", ["Triệt"], ["@cat_tinh"], "giam_tot", "cát tinh sợ Triệt vì không có dịp phát triển")
ch("khoa_khoc_hu.cu_dong", "kl180_cu_dong_khoa_khoc_hu", ["Hóa Khoa", "Thiên Khốc", "Thiên Hư"], ["Cự Môn", "Thiên Đồng"], "pha_ham",
   "Cự Đồng hãm có Hóa Khoa hoặc Khốc Hư chiếu mới khá được", where={"dignity": ["hãm"]})
ch("tham_lang.tu_vi", "kl186_tu_tham_ham", ["Tham Lang"], ["Tử Vi"], "giam_tot", "Tử Vi đi với Tham Lang thì coi như hãm, mất sức cứu giải", where={"same_palace": True})
ch("vu_khuc.sat", "kl187_vu_khac_sat", ["Vũ Khúc"], ["@sat_tinh"], "giam_xau", "Vũ Khúc đắc địa là khắc của các sát tinh", where={"tamer_dignity": ["miếu", "vượng", "đắc"]})
ch("thien_dong.khang_sat", "kl188_dong_khong_so_sat", ["Thiên Đồng"], ["@sat_tinh"], "khang", "Thiên Đồng không sợ sát tinh (KL p.91 lại nói không nên gặp: schools.json)")
ch("hoa_ky.liem", "kl188_liem_so_ky", ["Hóa Kỵ"], ["Liêm Trinh"], "giam_tot", "Liêm Trinh rất sợ Hóa Kỵ")
ch("tham_lang.hoa_linh", "kl190_tham_giai_hoa_linh", ["Tham Lang"], ["Hỏa Tinh", "Linh Tinh"], "giam_xau", "Tham Lang giải trừ ác tính của Hỏa Linh")
ch("quan_phuc", "kl194_quan_phuc", ["Thiên Quan", "Thiên Phúc"], ["@moi_sao"], "giam_xau", "Quan Phúc là sao cứu giải thuần túy; nặng thì cần đủ cả hai, có khi thêm Khôi Việt",
   also=["kl194_quan_phuc_nang"])
ch("tu_phu_nhat.khang_hoa_linh", "kl200_hoa_linh_khong_danh", ["Tử Vi", "Thiên Phủ", "Thái Dương"], ["Hỏa Tinh", "Linh Tinh"], "khang", "Hỏa Linh không đánh được Tử Vi, Thiên Phủ, Thái Dương")
ch("giai_manh.ngo_che", "kl200_ngo_che", ["@giai_manh"], ["@sat_tinh"], "giam_xau", "gặp sao giải mạnh thì hung sát tinh bị hóa giải, thành ra ngộ chế")
ch("tuan_triet.thien_hinh", "kl202_hinh_tuan_triet", TT_, ["Thiên Hình"], "giam_tot", "Thiên Hình gặp Tuần Triệt thành kiếm gãy: dễ mất việc")
ch("pha_toai.hien_tinh", "kl202_pha_toai_hao_hien", ["Phá Toái"], ["Tử Vi", "Thiên Phủ", "Thiên Lương", "Thiên Cơ"], "giam_tot", "Phá Toái làm hao tán các sao hiền")
ch("pha_toai.spt", "kl202_pha_toai_tang_spt", ["Phá Toái"], ["Thất Sát", "Phá Quân", "Tham Lang"], "tang", "Phá Toái làm bộ Sát Phá Tham mạnh thêm")
ch("song_hao.cu_mon", "kl203_song_hao_cu", ["Đại Hao", "Tiểu Hao"], ["Cự Môn"], "tang", "Song Hao cần cho Cự Môn ở Tài, Mệnh (rửa đá cho ngọc lộ ra)",
   where={"palace": ["Mệnh", "Tài Bạch"]})
ch("thieu_duong_hong.co_than", "kl204_co_than_thieu_duong_hong", ["Thiếu Dương", "Hồng Loan"], ["Cô Thần"], "giam_xau", "Cô Thần gặp Thiếu Dương và Hồng Loan thì đỡ cô đơn",
   where={"tuoi": ["Thìn", "Tuất", "Sửu", "Mùi"], "branch": ["Dần", "Thân", "Tỵ", "Hợi"]})
ch("tuan_triet.tat_ach", "tt91_tat_tuan_triet", TT_, ["@moi_sao"], "giam_xau", "Tuần Triệt ở Tật Ách: tai nào cũng khỏi, nạn nào cũng qua", where={"palace": "Tật Ách"})
ch("hoa_loc.nhat_ham_ky", "tt66_hoa_loc_do_hai", ["Hóa Lộc"], ["Thái Dương", "Hóa Kỵ"], "giam_xau", "Thái Dương hãm hội Hóa Kỵ, Mệnh vững có Hóa Lộc thì đỡ hại",
   where={"palace": "Mệnh", "dignity": ["hãm"]})
ch("cu_mieu.hung_tinh", "tt69_cu_mieu_do_hai", ["Cự Môn"], ["@sat_tinh"], "giam_xau", "Cự Môn miếu địa bị hung tinh phá thì đỡ hại hơn", where={"tamer_dignity": ["miếu"]})
ch("cat_tinh.dau_quan", "tt93_dau_quan_cat", ["@cat_tinh"], ["Đẩu Quân"], "giam_xau", "Đẩu Quân ở Tử Tức hiếm con, có cát tinh giao hội thì còn mong", where={"palace": "Tử Tức"})
ch("cat_tinh.hoa_ky", "tt76_hoa_ky_cat_lo", ["@cat_tinh"], ["Hóa Kỵ"], "giam_xau", "Hóa Kỵ có cát tinh trợ cứu thì giàu sang được, nhưng kèm nhiều lo lắng",
   also=["tt117_hoa_ky_cat_giam"])
ch("chinh_tinh_sinh_cung.lac_ham", "th79_lac_ham_chinh_tinh_sinh_cung", ["@chinh_tinh_sinh_cung"], ["@lac_ham"], "pha_ham",
   "sao lạc hãm (hành cung khắc hành sao) mà có chính tinh sinh được hành cung thì hóa tốt")
ch("tuan_triet.lac_ham", "th79_lac_ham_tuan_triet", TT_, ["@lac_ham"], "giam_tot", "sao lạc hãm gặp Tuần Triệt thì càng thêm xấu")
ch("hop_hanh_menh.sao_ham", "th79_ham_hop_hanh_menh", ["@hop_hanh_menh"], ["@chinh_tinh"], "pha_ham",
   "sao hãm mà hợp hành bản Mệnh thì khá hơn; sao đắc địa không hợp hành Mệnh thì kém đi", where={"palace": "Mệnh"})
ch("hoa_khoa.spt", "tl15_khoa_spt", ["Hóa Khoa"], ["Thất Sát", "Phá Quân", "Tham Lang"], "giam_xau",
   "Sát Phá Tham, nhất là hãm địa, gặp Hóa Khoa thì hung tinh ngộ chế (Thiên Lương)")
ch("tuan_triet.spt", "tl15_tuan_triet_spt", TT_, ["Thất Sát", "Phá Quân", "Tham Lang"], "hai_mat",
   "Sát Phá Tham gặp Tuần Triệt mất tính hung hãn, nhưng mất hết (Triệt) hay giảm hẳn tốc lực (Tuần) (Thiên Lương)")

CHE_HOA = {"version": "che-hoa-1", "date": "2026-10-24", "generated_by": "tools/build_deep3_kg.py",
           "note": "Quan hệ chế hóa giữa các sao theo trang sách (Khảo Luận, Toàn Thư, Thực Hành, Thiên Lương): 'tamer' tác động lên 'tamed' theo 'effect'. "
                   "Nhóm sao viết dạng '@...' (groups). 'where' là điều kiện sách nêu (palace, branch, dignity của sao bị chế, tamer_dignity, tuoi, both: các sao "
                   "phải cùng có mặt, same_palace). Chưa có tầng lập luận nào đọc tệp này (reason/ledger.ts weighSides sẽ đọc: plan Workstream C). "
                   "'star_nature' trỏ tới mục cùng nội dung trong star_nature.json (cùng trang hoặc trang tóm tắt).",
           "effects": EFFECTS, "groups": {**GROUPS, "@giai_manh": ["Hóa Khoa", "Thiên Quan", "Thiên Phúc", "Thiên Khôi", "Thiên Việt"],
                                          "@lac_ham": "sao có hành bị hành của cung khắc (TH p.79)", "@chinh_tinh_sinh_cung": "chính tinh có hành sinh hành của cung",
                                          "@hop_hanh_menh": "sao hợp hành bản Mệnh"},
           "entries": CH}

# ================================================================ combos.json
groups = [
    {"id": "tu_phu_vu_tuong", "name": "Tử Phủ Vũ Tướng", "stars": ["Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"], "kind": "hanh_dong",
     "nature": "hành động có lý luận", "sources": [src("kl166_tpvt")]},
    {"id": "sat_pha_liem_tham", "name": "Sát Phá Liêm Tham", "stars": ["Thất Sát", "Phá Quân", "Liêm Trinh", "Tham Lang"], "kind": "hanh_dong",
     "nature": "hành động mạnh mẽ", "sources": [src("kl167_splt")]},
    {"id": "co_nguyet_dong_luong", "name": "Cơ Nguyệt Đồng Lương", "stars": ["Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"], "kind": "ly_luan",
     "nature": "lý luận thuần túy", "sources": [src("kl167_cndl")]},
    {"id": "cu_nhat_nguyet", "name": "Cự Nhật, Nhật Nguyệt", "stars": ["Cự Môn", "Thái Dương", "Thái Âm"], "kind": "ly_luan",
     "nature": "lý luận thực hành", "sources": [src("kl167_cu_nhat")]},
]
kinds = [{"id": "hanh_dong", "name": "nhóm hành động", "meaning": "khi gặp nhóm hành động là lúc đang bận rộn, vất vả", "sources": [src("kl167_hanh_dong")]},
         {"id": "ly_luan", "name": "nhóm lý luận", "meaning": "khi gặp nhóm lý luận là lúc đang tính toán, suy nghĩ", "sources": [src("kl167_ly_luan")]}]
layouts = []


def lay(id, branch, name, mid, pol, reading=None):
    e = MINED[mid]
    layouts.append({"id": id, "tu_vi_branch": branch, "name": name, "reading": reading or e["reading_vi"], "pol": pol, "sources": [src(mid)]})


lay("tu_ngo", ["Ngọ"], "Tử Vi cư Ngọ", "kl180_tu_ngo", "+")
lay("tu_ty", ["Tý"], "Tử Vi cư Tý", "kl180_tu_ty", "-")
lay("tu_sat_ty", ["Tỵ"], "Tử Sát ở Tỵ", "kl181_tu_sat_ty", "+")
lay("tu_sat_hoi", ["Hợi"], "Tử Sát ở Hợi", "kl181_tu_sat_hoi", "-")
lay("tu_tuong_thin_tuat", ["Thìn", "Tuất"], "Tử Tướng ở Thìn, Tuất", "kl182_tu_tuong_thin", "+")
lay("tu_tham_mao", ["Mão"], "Tử Tham ở Mão", "kl182_tu_tham_mao", "-")
lay("tu_tham_dau", ["Dậu"], "Tử Tham ở Dậu", "kl183_tu_tham_dau", "+")
lay("tu_phu_dan", ["Dần"], "Tử Phủ ở Dần", "kl183_tu_phu_dan", "+")
lay("tu_phu_than", ["Thân"], "Tử Phủ ở Thân", "kl184_tu_phu_than", "+")
lay("tu_pha_suu", ["Sửu"], "Tử Phá ở Sửu", "kl184_tu_pha_suu_ben", "-")
lay("tu_pha_mui", ["Mùi"], "Tử Phá ở Mùi", "kl185_tu_pha_mui", "+")
pairs = [
    {"id": "co_am_dac", "stars": ["Thiên Cơ", "Thái Âm"], "when": {"dignity": ["miếu", "vượng", "đắc"]}, "meaning": "giàu", "context": "thế Tử Vi ở Ngọ",
     "sources": [src("kl180_co_am_giau")]},
    {"id": "duong_luong_dac", "stars": ["Thái Dương", "Thiên Lương"], "when": {"dignity": ["miếu", "vượng", "đắc"]}, "meaning": "sang", "context": "thế Tử Vi ở Ngọ",
     "sources": [src("kl180_duong_luong_sang")]},
    {"id": "cu_dong_ham", "stars": ["Cự Môn", "Thiên Đồng"], "when": {"dignity": ["hãm"]}, "meaning": "lẻ loi, bất đắc chí", "rescue": "che_hoa: khoa_khoc_hu.cu_dong",
     "sources": [src("kl180_cu_dong_le_loi"), src("kl180_cu_dong_khoa_khoc_hu")]},
    {"id": "tu_pha", "stars": ["Tử Vi", "Phá Quân"], "when": {"branch": ["Sửu", "Mùi"]}, "meaning": "hai phe cân bằng: con người bình thường, có cao thượng có thấp hèn",
     "sources": [src("kl179_tu_pha_suu")]},
    {"id": "tu_tham", "stars": ["Tử Vi", "Tham Lang"], "when": {"same_palace": True}, "meaning": "Tử Vi coi như hãm, mất sức cứu giải",
     "sources": [src("kl186_tu_tham_ham")]},
    {"id": "tu_phu", "stars": ["Tử Vi", "Thiên Phủ"], "when": {"branch": ["Dần", "Thân"]}, "meaning": "vua tôi cùng ngồi bàn việc nước", "sources": [src("kl186_tu_phu_dan_than")]},
    {"id": "tu_ta_huu", "stars": ["Tử Vi", "Tả Phụ", "Hữu Bật"], "meaning": "Tả Hữu là hai tay chân đắc lực nhất của Tử Vi", "sources": [src("kl186_tu_ta_huu")]},
]
modifiers = [
    {"id": "nhi_hop_vcd", "applies_to": ["Thiên Tướng", "Thất Sát"], "when": "cung nhị hợp của sao là vô chính diệu", "effect": "cô đơn, không có hậu thuẫn",
     "sources": [src("kl181_tuong_nhi_hop_vcd"), src("kl180_sat_co_don")]},
    {"id": "giap_goc", "applies_to": ["giáp"], "when": "cung bị giáp ở Dần, Thân, Tỵ, Hợi (giáp góc)", "effect": "giáp góc kém hiệu lực hơn giáp cung",
     "sources": [src("kl205_giap_goc")]},
    {"id": "tu_vi_huong", "applies_to": ["Tử Vi"], "when": "vị trí Tử Vi trên địa bàn", "effect": "Tử Vi từ Ngọ đến Dần đang đi xuống, Phá Quân từ Thân đến Mùi đang đi lên",
     "sources": [src("kl179_tu_ngo_dan_di_xuong")]},
]
# per palace: the verified rules that read a named chính tinh pair standing together in a palace (the pair's per-palace meaning, with its pages)
PAIRS = [("Tử Vi", x) for x in ("Thiên Phủ", "Thiên Tướng", "Thất Sát", "Phá Quân", "Tham Lang")] + \
        [("Vũ Khúc", x) for x in ("Thiên Phủ", "Thiên Tướng", "Thất Sát", "Phá Quân", "Tham Lang")] + \
        [("Liêm Trinh", x) for x in ("Thiên Phủ", "Thiên Tướng", "Thất Sát", "Phá Quân", "Tham Lang")] + \
        [("Thiên Cơ", "Thái Âm"), ("Thiên Cơ", "Cự Môn"), ("Thiên Cơ", "Thiên Lương"), ("Thiên Đồng", "Thái Âm"), ("Thiên Đồng", "Cự Môn"),
         ("Thiên Đồng", "Thiên Lương"), ("Thái Dương", "Thái Âm"), ("Thái Dương", "Cự Môn"), ("Thái Dương", "Thiên Lương")]
LOADER = (ROOT / "engine" / "tvbt" / "knowledge" / "loader.py").read_text("utf-8")
PACKS = json.loads(next(l for l in LOADER.splitlines() if l.startswith("PACKS = ")).split("=", 1)[1].strip())
import re  # noqa: E402

CITE = re.compile(r"\[((?:TH|KL|TT|TL|NL)[^\]]*?)\]")


def need_majors(cond):
    """the chính tinh a rule's conditions require in the palace itself (only plain top-level 'all' leaves)"""
    out = set()
    for c in cond.get("all", []):
        if c.get("fact") == "palace.own_major_stars" and c.get("operator") == "contains":
            out.add(c["value"])
    return out


per_palace = {f"{a}|{b}": {} for a, b in PAIRS}
for name in PACKS:
    for r in json.loads((D / name).read_text("utf-8"))["rules"]:
        if r.get("system") != "tu_vi" or r.get("reviewStatus") != "verified":
            continue
        pal = next((c["value"] for c in r["conditions"].get("all", []) if c.get("fact") == "palace.name"), None)
        if not pal:
            continue
        maj = need_majors(r["conditions"])
        for a, b in PAIRS:
            if a in maj and b in maj:
                per_palace[f"{a}|{b}"].setdefault(pal, []).append({"rule": r["id"], "cites": CITE.findall(r["description"])})
COMBOS = {"version": "combos-1", "date": "2026-10-24", "generated_by": "tools/build_deep3_kg.py",
          "note": "Nhóm chính tinh và cặp sao theo Khảo Luận (pp.166-167 nhóm, pp.179-186 thế đứng 12 vòng Tử Vi): 'groups' (nhóm, tính chất), 'kinds' "
                  "(nhóm hành động / lý luận), 'layouts' (thế của lá số theo vị trí Tử Vi: chart.tu_vi_branch), 'pairs' (cặp sao có nghĩa riêng trên trang), "
                  "'modifiers' (điều kiện làm đổi nghĩa), 'per_palace' (theo từng cặp chính tinh đồng cung: các rule verified đọc cặp đó ở từng cung, với trang). "
                  "Ô chữ của 12 sơ đồ vòng (KL pp.167-178) chưa khai thác: text layer xáo thứ tự ô.",
          "groups": groups, "kinds": kinds, "layouts": layouts, "pairs": pairs, "modifiers": modifiers,
          "per_palace": {k: v for k, v in per_palace.items() if v}}

# ================================================================ schools.json
SIDES = {"KL": "Tử Vi Khảo Luận", "TH": "Tử Vi Thực Hành", "TT": "Toàn Thư (bản dịch Vũ Tài Lục)", "TTH": "紫微斗數全書 (Hán văn)", "TL": "Thiên Lương (Nghiệm Lý)"}
TOPICS = []


def side(school, mid, statement=None):
    e = MINED[mid]
    return {"school": school, "statement": statement or e["reading_vi"] or e["condition_text"], **src(mid, skipped_ok=True), "cite": cite(mid)}


def topic(id, name, kind, sides, note, engine=None):
    TOPICS.append({"id": id, "topic": name, "kind": kind, "sides": sides, "note": note, **({"engine": engine} if engine else {})})


topic("kim_du_phu_gia", "Kim dư phù giá: ai giáp Tử Vi", "dinh_nghia_cach", [
    side("KL", "kl43_kim_du_phu_gia", "Tử Vi đắc địa, Tả Hữu tam hợp chiếu, Thiếu Dương, Thiếu Âm giáp Mệnh"),
    side("TH", "th73_kim_du", "Tử Vi ở Mệnh hay Quan Lộc, giáp Tả Hữu hoặc Thiếu Dương, Thiếu Âm"),
    side("TT", "tt142_kim_du_pho_gia", "Tử Vi thủ Mệnh, Nhật Nguyệt giáp; người dịch nói lời giảng sai vì Tử Vi không thể giáp Nhật Nguyệt"),
    side("TTH", "w1_kim_du_phu_gia")],
    "紫微斗數全書 nói 日月來夾 (Nhật Nguyệt giáp); KL và TH đọc thành Thiếu Dương, Thiếu Âm (cặp sao luôn kẹp cung Thái Tuế), TH thêm Tả Hữu.",
    engine="TV_TH_CACH_MENH_KIM_DU dùng định nghĩa TH")
topic("that_sat_trieu_dau", "Thất Sát triều đẩu: vị trí", "dinh_nghia_cach", [
    side("KL", "kl43_that_sat_trieu_dau", "Mệnh có Phá Quân ở Tý Ngọ, Thất Sát ở Dần Thân"),
    side("TH", "th73_that_sat_trieu_dau"), side("TT", "tt142_that_sat_trieu_dau"), side("TTH", "w1_that_sat_trieu_dau")],
    "TH chỉ Dần Thân (Ngọ là 'ngưỡng đẩu'); TT thêm Tý Ngọ; KL định nghĩa qua Phá Quân; 紫微斗數全書 không ghi vị trí ở câu phú.",
    engine="TV_TH_CACH_MENH_SAT_TRIEU_DAU (Dần, Thân)")
topic("nhat_o_mao", "Thái Dương ở Mão: tên cách và cung", "ten_cach", [
    side("KL", "kl44_nhat_xuat_phu_tang", "Nhật xuất phù tang: Mệnh ở Mão có Thái Dương, Thiên Lương"),
    side("TH", "th72_nhat_chieu_loi_mon", "Nhật chiếu lôi môn: Thái Dương ở Mão có Mệnh"),
    side("TT", "tt142_nhat_xuat_phu_tang_quan", "Nhật xuất phù tang: Thái Dương ở Mão thủ Mệnh hoặc Quan Lộc"), side("TTH", "w1_nhat_xuat_phu_tang")],
    "Cùng một lõi, hai tên; TT và 紫微斗數全書 nhận cả cung Quan Lộc.", engine="TV_TH_CACH_MENH_NHAT_MAO (Mệnh) và TV_D3_TT142_NHAT_XUAT_PHU_TANG_QUAN (Quan Lộc)")
topic("nguyet_o_ty", "Thái Âm ở Tý: Mệnh hay Điền Trạch, tên cách", "dinh_nghia_cach", [
    side("KL", "kl44_minh_chau_xuat_hai", "Minh châu xuất hải: Mệnh ở Tý có Thái Âm đồng cung Thiên Đồng"),
    side("TH", "th73_nguyet_sinh_thuong_hai", "Nguyệt sinh thương hải (Thái Âm tại Tý), cũng gọi Minh châu xuất hải"),
    side("TT", "tt142_nguyet_sinh_suong_hai", "Nguyệt sinh thương hải: Thái Âm ở Tý thủ Điền Trạch"), side("TTH", "w1_nguyet_sinh_thuong_hai")],
    "紫微斗數全書 và TT đặt cách ở Điền Trạch; TH và KL đọc ở Mệnh. 紫微斗數全書 còn có 明珠出海 là một cách riêng ('見前批注').",
    engine="TV_TH_CACH_MENH_NGUYET_TY (Mệnh) và TV_D3_TT142_NGUYET_SINH_SUONG_HAI (Điền Trạch)")
topic("nhat_nguyet_chieu_bich", "Nhật Nguyệt chiếu bích: Mệnh hay Điền Trạch", "dinh_nghia_cach", [
    side("KL", "kl44_nn_chieu_bien", "Nhật Nguyệt chiếu biến: Mệnh vô chính diệu ở Mùi có Nhật Nguyệt ở Sửu chiếu, hoặc ngược lại"),
    side("TH", "th73_nn_chieu_bich"), side("TT", "tt142_nn_chieu_bich", "Nhật Nguyệt ở Điền Trạch, ở Tứ mộ mới thật tốt"), side("TTH", "w1_nn_chieu_bich")],
    "KL, TH đọc ở Mệnh (đối chiếu); TT, 紫微斗數全書 đọc ở Điền Trạch.", engine="TV_TH_CACH_MENH_NN_CHIEU_BICH (Mệnh) và TV_D3_TT142_NN_CHIEU_BICH (Điền Trạch)")
topic("toa_quy_huong_quy", "Tọa quý hướng quý: Khôi Việt ở đâu", "dinh_nghia_cach", [
    side("KL", "kl44_toa_quy_huong_quy", "Mệnh có Khôi, Thiên Di có Việt, hoặc ngược lại"), side("TH", "th73_toa_quy"), side("TT", "tt142_toa_quy"),
    side("TTH", "w1_toa_quy_huong_quy")],
    "KL hẹp nhất (Mệnh và Thiên Di); TH, TT nhận cả Khôi Việt chiếu Mệnh.", engine="CACH_X_TOA_QUY_HUONG_QUY dùng định nghĩa KL")
topic("tai_loc_giap_ma", "Tài Lộc giáp Mã: Lộc Tồn hay Hóa Lộc", "dinh_nghia_cach", [
    side("KL", "kl45_tai_loc_giap_ma", "Thiên Mã ở Mệnh, Vũ Khúc và Lộc Tồn giáp"), side("TH", "th73_vu_loc_giap_ma"),
    side("TT", "tt142_tai_loc_hiep_ma", "Thiên Mã thủ Mệnh, giáp Vũ Khúc và Hóa Lộc"), side("TTH", "w1_tai_loc_giap_ma")],
    "KL nói Lộc Tồn, TT nói Hóa Lộc, TH nhận cả hai; 紫微斗數全書 chỉ nói 祿.", engine="CACH_X_TAI_LOC_GIAP_MA nhận cả hai")
topic("tham_hoa", "Tham Hỏa tương phùng: vị trí và sao", "dinh_nghia_cach", [
    side("KL", "kl45_tham_hoa", "Mệnh ở Tứ mộ có Tham Lang đồng cung Hỏa hoặc Linh"), side("TH", "th73_tham_hoa"),
    side("TT", "tt142_tham_hoa_mao", "Tham Lang miếu địa thủ Mệnh tại cung Mão (bản dịch)"), side("TTH", "w1_tham_hoa")],
    "Bản dịch TT thêm 'cung Mão', 紫微斗數全書 không có (chỉ nói hai sao cùng thủ Mệnh, miếu vượng); KL nhận cả Linh Tinh.", engine="TV_TH_CACH_MENH_THAM_HOA (TH)")
topic("loc_phung_luong_sat", "Lộc phùng lưỡng sát: có cần Không Vong", "dinh_nghia_cach", [
    side("KL", "kl46_loc_phung_luong_sat", "Lộc Tồn, Hóa Lộc gặp Không Kiếp đồng cung"), side("TH", "th73_loc_phung_luong_sat"),
    side("TT", "tt143_loc_phung_luong_sat", "Lộc tọa Không Vong (Tuần Triệt) gặp thêm Không Kiếp"), side("TTH", "w1_loc_phung_luong_sat")],
    "TT và 紫微斗數全書 cần Lộc ở Không Vong; KL, TH chỉ cần Không Kiếp đồng cung.", engine="TV_TH_CACH_MENH_BT_LOC_LUONG_SAT (TH)")
topic("nhat_nguyet_tang", "Nhật Nguyệt tàng huy / tàng hung: có cần Cự Môn", "dinh_nghia_cach", [
    side("KL", "kl46_nn_tang_hung"), side("TH", "th74_nn_tan_hung"), side("TT", "tt143_nn_tang_huy", "Thái Âm, Thái Dương hãm gặp Cự Môn"),
    side("TTH", "w1_nn_tang_huy")],
    "TT, 紫微斗數全書 cần thêm Cự Môn (日月反背又逢巨暗); KL chỉ cần Nhật Nguyệt hãm thủ hoặc chiếu; TH: hãm mà không có cứu tinh hoặc gặp sát.",
    engine="TV_D3_KL46_NN_TANG_HUNG (KL)")
topic("giap_hay_hoi", "Tài ấm giáp ấn, Tài ấn giáp lộc: 'giáp' hay 'hội'", "ban_dich", [
    side("TT", "tt141_tai_am_hiep_an", "Thiên Tướng thủ Mệnh, Vũ Khúc Thiên Lương hội hiệp"), side("TTH", "w1_tai_am_giap_an"),
    side("TT", "tt142_tai_an_hiep_loc", "Lộc thủ Mệnh, Thiên Lương Thiên Tướng hội hiệp"), side("TTH", "w1_tai_an_giap_loc"), side("TH", "th73_tai_an_giap_loc")],
    "Bản dịch TT viết 'hội hiệp' cho chữ 夾 (giáp) của 紫微斗數全書; TH nói Tài ấn giáp lộc là Vũ Khúc, Thiên Tướng giáp (không phải Lương Tướng). Chưa thành rule.")
topic("quan_than_khanh_hoi", "Quân thần khánh hội", "dinh_nghia_cach", [
    side("TT", "tt142_quan_than_khanh_hoi"), side("TH", "th73_quan_than")],
    "TT: Tử Vi, Tả Hữu cùng ở Mệnh, Vũ Tướng chiếu; TH: Tử Vi gặp toàn cát tinh hội.", engine="TV_D3_TT142_QUAN_THAN_KHANH_HOI (TT)")
topic("co_luong_thin_tuat", "Cơ Lương ở Thìn Tuất: tốt hay xấu", "trai_nghich", [
    side("TT", "tt70_co_luong_thin_tuat", "Cơ Lương đóng tại Thìn, Tuất và Phá Quân ở Mão Dậu đều xấu"),
    side("TH", "th73_co_luong", "Cơ Lương Thìn Tuất là một quý cách"), side("TH", "th80_co_luong_dac_dia"),
    side("TTH", "w1_co_luong_thin_tuat", "辰戍機梁非小補: nằm trong bài 'đắc địa phú quý'")],
    "Câu 'phi tiểu bổ' (非小補 = không phải lợi nhỏ) nằm trong bài đắc địa phú quý của 紫微斗數全書 và TH xếp Cơ Lương Thìn Tuất là quý cách; bản dịch TT (pp.70, 113) đọc là xấu. Không làm rule.")
topic("pha_quan_mao_dau", "Phá Quân ở Mão Dậu", "trai_nghich", [
    side("TH", "th72_pha_liem_mao_dau", "Phá Quân đóng Mệnh ở Mão, Dậu mới hợp cách tốt"),
    side("TT", "tt70_co_luong_thin_tuat", "Phá Quân ở Mão Dậu xấu"), side("TH", "th81_pha_mao_dau_ham", "Phá Quân Mão Dậu không thanh (bài lục hãm, cùng sách)"),
    side("TTH", "w1_pha_mao_dau")],
    "TH p.72 coi là cách tốt, nhưng TH p.81, TT p.70 và 紫微斗數全書 (失陷貧賤論) coi là không thanh.", engine="TV_TH_CACH_MENH_PHA_MAO_DAU (TH p.72); không thêm rule ngược")
topic("nhat_nguyet_suu_mui", "Nhật Nguyệt đồng cung Sửu Mùi", "trai_nghich", [
    side("TH", "th72_nn_dong_cung", "Nhật Nguyệt đồng cung là một quý cách"), side("TT", "tt76_nhat_nguyet_suu_mui", "phú nôm: bất hiển công danh"),
    side("TT", "tt145_nn_suu_mui_lan_dan"), side("TTH", "w1_hop_suu", "chính tọa chỉ là trung cục; Nhật Nguyệt chiếu (triều) mới tốt")],
    "TH xếp là quý cách; phú nôm và lời bình TT nói công danh lận đận; 紫微斗數全書 nói chính tọa chỉ trung cục.",
    engine="TV_TH_CACH_MENH_NHAT_NGUYET (TH); không thêm rule ngược")
topic("liem_pha_mao_dau", "Liêm Phá Mão Dậu: hãm hay đắc", "dac_ham", [
    side("KL", "kl181_liem_pha_khien_cuong", "coi Liêm Phá Mão Dậu là hãm thì quá khắt khe, nên coi là đắc địa"), side("TH", "th81_liem_pha_mao_dau")],
    "Tác giả KL (pp.181, 185) không đồng ý với bảng truyền thống.")
topic("dac_ham_can_cu", "Đắc hãm căn cứ vào đâu", "nguyen_ly", [
    side("KL", "kl180_dac_ham_the_dung"), side("KL", "kl185_khong_cong_thuc"), side("TH", "th79_lac_ham_ngu_hanh", "lạc hãm khi hành của cung khắc hành của sao")],
    "KL: theo thế đứng của hai nhóm Tử Vi, Phá Quân, không do ngũ hành sao với cung; TH p.79 định nghĩa lạc hãm bằng ngũ hành.")
topic("that_sat_thien_hinh", "Thất Sát gặp Thiên Hình", "trai_nghich", [
    side("KL", "kl47_that_sat_ngo_hinh", "Thất Sát, Thiên Hình đồng cung: kỳ cách, thành công lạ lùng"), side("KL", "kl64_kiem_ke_co_ngua")],
    "Cùng sách: p.47 kể là kỳ cách tốt; p.64 (Mệnh Ngọ có Kình) gọi Thất Sát, Thiên Hình đồng cung là 'kiếm kề cổ ngựa'. Không làm rule.")
topic("thien_dong_sat_tinh", "Thiên Đồng gặp sát tinh", "trai_nghich", [side("KL", "kl91_dong_khong_nen_sat"), side("KL", "kl188_dong_khong_so_sat")],
      "Cùng sách: p.91 nói không nên gặp sát tinh, p.188 (tóm tắt) nói không sợ sát tinh.")
topic("thien_dong_tuan_triet", "Thiên Đồng với Tuần Triệt", "y_kien", [side("KL", "kl91_dong_khong_so_tuan_triet")],
      "KL ghi hai ý kiến trên cùng một dòng: không sợ Tuần Triệt; có người cho là cần Tuần Triệt để bớt thay đổi.")
topic("hanh_thien_luong", "Hành của Thiên Lương", "ngu_hanh", [side("TH", "th80_hanh_tho_2", "Thiên Phủ, Thiên Lương thuộc Thổ"), side("TT", "tt113_luong_moc")],
      "TH p.80 xếp Thiên Lương vào Thổ, phú nôm TT p.113 gọi là Mộc.")
topic("hanh_that_sat", "Hành của Thất Sát", "ngu_hanh", [side("TH", "th80_hanh_kim_2", "Văn Xương, Thất Sát thuộc Kim"),
                                                       side("TH", "th80_hanh_hoa_thai_duong", "bài 'Ngũ hành sở thuộc': Thất Sát thuộc Hỏa")],
      "Cùng một trang TH: bảng Nam Bắc tinh nói Kim, bài thơ ngũ hành sở thuộc nói Hỏa.")
topic("phu_pha_quan_thin_tuat", "Câu phú 'Trai bất nhân Phá Quân Thìn Tuất'", "dung_phu", [
    side("TT", "tt123_phu_khong_sai"), side("KL", "kl49_phu_so_toet"), side("KL", "kl49_phu_ban_khac"), side("TL", "tl13_phu_than_trong"), side("TL", "tl14_phu_theo_tuoi")],
    "TT tin câu phú 'hầu như chẳng bao giờ sai'; KL cho là khiên cưỡng và chép nhiều bản khác nhau; Thiên Lương đọc theo tuổi và vị trí trong vòng Thái Tuế (Giáp Dần ở tam hợp Thái Tuế thì không thể bất nhân).")
topic("dich_phá_cach_ty_suu", "Phá cách Thiên Cơ: Tý Ngọ hay Tỵ", "ban_dich", [side("TT", "tt147_dich_ty_cung"), side("TT", "tt147_pha_co_ty_ngo_cu_linh", "câu thơ: Tí Ngọ Thiên Cơ"),
                                                                       side("TTH", "w1_pha_cach_ty_suu")],
      "Bản dịch ghi 'Tị cung', câu thơ và 紫微斗數全書 ghi 子午: hệ thống theo câu thơ.", engine="TV_D3_TT147_PHA_CO_TY_NGO_CU_LINH")
topic("dich_tuat_cung", "Hợp cách Mệnh Tuất: Tử Vi hay Thiên Phủ", "ban_dich", [side("TT", "tt145_hop_tuat"), side("TTH", "w1_hop_tuat")],
      "Bản dịch ghi Thiên Phủ, câu gốc 戍宮紫微對冲辰 ghi Tử Vi. Không làm rule.")
topic("dich_tuoi_suu", "Hợp cách Mệnh Sửu: tuổi nào", "ban_dich", [side("TT", "tt143_hop_suu"), side("TTH", "w1_hop_suu")],
      "TT 'Bính Tuất', bản Hán văn '丙戍' (có lẽ 丙戊: Bính, Mậu). Không làm rule.")
topic("tham_hoa_loc_tu_mo", "Tham Lang hóa Lộc ở Tứ mộ", "ban_dich", [side("TT", "tt149_tham_hoa_loc_tu_mo", "bản in: 'Tham Lang, Hỏa Lộc cư tứ mộ'"),
                                                                  side("TH", "th81_tham_hoa_loc"), side("TTH", "w1_tham_hoa_loc_tu_mo")],
      "Bản in TT 'Hỏa Lộc', TH và 紫微斗數全書 'Hóa Lộc' (化祿): hệ thống đọc Hóa Lộc.", engine="TV_D3_TT149_THAM_HOA_LOC_TU_MO")
topic("thien_la_dia_vong", "Thiên La Địa Võng", "y_kien", [side("KL", "kl203_la_vong_menh"), side("KL", "kl203_la_vong")],
      "KL nêu hai ý: Mệnh ở Thìn Tuất là bị lưới bó; có sách nói chỉ khi Đà La cũng ở đó.")
SCHOOLS = {"version": "schools-1", "date": "2026-10-24", "generated_by": "tools/build_deep3_kg.py", "schools": SIDES,
           "note": "Chỗ các sách / trường phái nói khác nhau về cùng một điều (định nghĩa cách, tên cách, bản dịch, đắc hãm, ngũ hành, cách dùng phú). Mỗi 'side' là lời "
                   "của một sách với trích dẫn và trang (hoặc quyển · mục cho 紫微斗數全書, trang scan cho Thiên Lương). 'engine' ghi hệ thống đang dùng bên nào. "
                   "Tầng Đọc sâu ('Khác biệt trường phái', plan Workstream E) sẽ đọc tệp này.",
           "topics": TOPICS}


def main():
    for name, data in (("che_hoa.json", CHE_HOA), ("combos.json", COMBOS), ("schools.json", SCHOOLS)):
        (KG / name).write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", "utf-8")
    # star_nature.json: Thực Hành p.80 elements (book TH), replacing this builder's earlier entries
    sn = json.loads((KG / "star_nature.json").read_text("utf-8"))
    sn["entries"] = [e for e in sn["entries"] if not e.get("deep3")]
    for e in (x for x in MINED.values() if x.get("target") == "star_nature" and not x.get("skip")):
        for star in e["stars"]:
            sid = f"{star.lower().replace(' ', '_')}.hanh_th"
            sid = "".join(c for c in __import__("unicodedata").normalize("NFD", sid.replace("đ", "d")) if not __import__("unicodedata").combining(c))
            sn["entries"].append({"id": sid, "star": star, "book": "TH", "page": e["page"], "quote": e["quote"], "text": f"thuộc hành {e['hanh']} (Thực Hành)",
                                  "use": ["self"], "explains": [], "kind": "hanh", "deep3": e["id"]})
    (KG / "star_nature.json").write_text(json.dumps(sn, ensure_ascii=False, indent=1) + "\n", "utf-8")
    # van_han_books.json: Thực Hành pp.130-133 (kind 'th'), replacing this builder's earlier entries
    vb = json.loads((KG / "van_han_books.json").read_text("utf-8"))
    vb["entries"] = [e for e in vb["entries"] if e.get("kind") != "th"]
    for e in (x for x in MINED.values() if x.get("target") == "van_han" and not x.get("skip")):
        vb["entries"].append({"id": e["id"], "kind": "th", "cond": e["cond"], "text": e["reading_vi"], "tone": e["tone"], "book": "TH", "page": e["page"],
                              "quote": e["quote"]})
    vb["skipped"] = {k: v for k, v in vb["skipped"].items() if not k.startswith("th13")}
    vb["skipped"].update({x["id"]: x["skip"] for x in MINED.values() if x.get("target") == "van_han" and x.get("skip")})
    (KG / "van_han_books.json").write_text(json.dumps(vb, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(f"che_hoa {len(CH)}, combos: groups {len(groups)} layouts {len(layouts)} pairs {len(pairs)} per_palace {len(COMBOS['per_palace'])}, "
          f"schools {len(TOPICS)}, star_nature +{sum(len(x['stars']) for x in MINED.values() if x.get('target') == 'star_nature')}, "
          f"van_han th {sum(1 for x in MINED.values() if x.get('target') == 'van_han' and not x.get('skip'))}")


if __name__ == "__main__":
    main()
