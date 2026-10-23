"""Generates engine/data/kg/van_han_books.json: the đại hạn and year readings the vận hạn chapter tells from the books, page-checked (plan
2026-10-23 Đại hạn): Toàn Thư's 'nhập hạn' verses pp.96-106 (TT p.105 the hạn's Hóa Lộc / Quyền / Khoa, read on the Tứ Hóa of the hạn's own stem,
not the natal one), Khảo Luận pp.233-236 (the chính tinh and hung tinh of the hạn đắc / hãm, Tuần / Triệt giải, the 'quan thầy' of each hung tinh,
the opening sentences for a hạn of Thất Sát / Phá Quân / Tham Lang, the stage of life a palace stands for by the chart's direction) and Thực
Hành p.119 (đại hạn and tiểu hạn on one palace; the years a tuổi 'kỵ'). Quotes and pages come from engine/data/kg/mined/van_han_sources.json
(each image-checked); the condition is the book's, never wider (a verse's 'gặp' with no position is read in the hạn palace itself). Left out:
death, illness and longevity, prison, sons/daughters, marriage and birth events, and the verses whose conditions the page leaves open
(SKIPPED, with the reason). The reader words drop the verses' event clauses; nothing is added."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MINED = {e["id"]: e for e in json.loads((ROOT / "engine" / "data" / "kg" / "mined" / "van_han_sources.json").read_text("utf-8"))["entries"]}
SAT = ["Kình Dương", "Đà La", "Địa Không", "Địa Kiếp", "Hỏa Tinh", "Linh Tinh"]
CAT = ["Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"]
GOOD = ["miếu", "vượng", "đắc"]
TU_MO = ["Thìn", "Tuất", "Sửu", "Mùi"]
E = []


def tt(mid, text, tone, **cond):
    E.append({"id": mid, "kind": "tt", "cond": cond, "text": text, "tone": tone})


# ---- Toàn Thư, nhập hạn ca (cond keys: major / star (in the hạn palace), dig (its brightness), with_any (in the palace), tp_sat / tp_cat /
# no_cat (sát / cát tinh in the tam phương tứ chính), tp_all (stars that must all stand in the tam phương), hoa (the hạn's own Hóa in the
# palace), hoa3 (the hạn's Lộc, Quyền and Khoa all in the tam phương), opp_major, branch (the hạn palace), tuoi (the birth-year branch)) ----
tt("tt97_tu_vi_mieu_cat", "hạn đến Tử Vi miếu vượng có nhiều sao tốt thì nhiều phúc lộc, người thường kiếm thêm tiền, người có chức được thăng", "pos", major="Tử Vi", dig=["miếu", "vượng"], tp_cat=True)
tt("tt97_tu_vi_spt", "Tử Vi nhập hạn vốn hay, chỉ sợ tam phương có Thất Sát, Phá Quân, Tham Lang: khi ấy người thường kém thuận, người có chức dễ bị giáng", "neg", major="Tử Vi", tp_any=["Thất Sát", "Phá Quân", "Tham Lang"])
tt("tt97_thien_co_hoa", "hạn Thiên Cơ có Khoa, Quyền, Lộc thì ra vào làm ăn thường được quý nhân giúp", "pos", major="Thiên Cơ", hoa_any=["Hóa Khoa", "Hóa Quyền", "Hóa Lộc"])
tt("tt97_thien_co_duong_da_cu", "hạn Thiên Cơ lại thêm Kình Dương, Đà La cùng Cự Môn hãm thì dễ đổ vỡ", "neg", major="Thiên Cơ", tp_any=["Kình Dương", "Đà La"], tp_major_dig={"Cự Môn": ["hãm"]})
tt("tt97_thai_duong_dac", "đại tiểu hạn gặp Thái Dương đắc địa thì nhiều tiền, tấn nghiệp, vợ chồng hòa thuận, người theo học hay làm việc công dễ hiển đạt", "pos", major="Thái Dương", dig=GOOD)
tt("tt97_thai_duong_ham_ky", "Thái Dương hãm địa nhập hạn bị ác tinh xung phá lại có Hóa Kỵ thì việc dễ hỏng, hao tài", "neg", major="Thái Dương", dig=["hãm"], tp_sat=True, hoa=["Hóa Kỵ"])
tt("tt98_vu_khuc_mieu", "đại tiểu hạn gặp Vũ Khúc nhập miếu thì tiền tài hưng vượng", "pos", major="Vũ Khúc", dig=["miếu"])
tt("tt98_vu_khuc_quyen", "Vũ Khúc nhập hạn có Hóa Quyền thì cầu mưu gì cũng dễ thành", "pos", major="Vũ Khúc", hoa=["Hóa Quyền"])
tt("tt98_vu_khuc_ham", "Vũ Khúc hãm địa nhập hạn thì dễ gặp rắc rối giấy tờ, dân thường hay mắc nợ, người có quyền thêm lo âu", "neg", major="Vũ Khúc", dig=["hãm"])
tt("tt98_thien_dong", "nhị hạn gặp Thiên Đồng thì hỷ khí đầy cửa, mọi sự hanh thông, nên gây dựng việc mới", "pos", major="Thiên Đồng", not_dig=["hãm"])
tt("tt98_thien_dong_ham", "Thiên Đồng hãm địa vào hạn gặp ác sát xung thì làm việc đầu tốt cuối hỏng, dễ mất chức, vướng nợ", "neg", major="Thiên Đồng", dig=["hãm"], tp_sat=True)
tt("tt98_liem_trinh_vuong", "Liêm Trinh nhập hạn ở vượng cung có cát tinh phò trợ thì tiền của tự tích tụ, mưu cầu lên chức dễ thành", "pos", major="Liêm Trinh", dig=["miếu", "vượng"], tp_cat=True)
tt("tt99_thien_phu", "hạn đến Thiên Phủ chủ về tài lộc: thêm tiền thêm vui, thuận cho việc xây cất nhà cửa", "pos", major="Thiên Phủ")
tt("tt99_thien_phu_tam_hoa", "hạn Thiên Phủ có đủ Khoa, Quyền, Lộc thì có thể định ngày phát triển tài năng sẵn có", "pos", major="Thiên Phủ", hoa3=True)
tt("tt99_thai_am", "hạn đến Thái Âm thì tài lộc nhiều, mưu việc tốt, nhà cửa hưng vượng", "pos", major="Thái Âm", not_dig=["hãm"])
tt("tt99_thai_am_ham", "hạn gặp Thái Âm hãm địa lại thêm Kình Dương, Đà La, Linh Tinh, Hỏa Tinh thì nhiều phá hại", "neg", major="Thái Âm", dig=["hãm"], tp_any=["Kình Dương", "Đà La"], tp_any2=["Linh Tinh", "Hỏa Tinh"])
tt("tt100_tham_lang_mieu", "hạn đến Tham Lang miếu địa rất hay: mưu cầu dễ, thường phát hoạnh tài, việc suôn sẻ", "pos", major="Tham Lang", dig=["miếu"])
tt("tt100_tham_lang_tu_mo_hoa", "Tham Lang ở tứ mộ, người tuổi Thìn, Tuất, Sửu, Mùi gặp Hỏa Tinh thì làm giàu rất nhanh", "pos", major="Tham Lang", branch=TU_MO, tuoi=TU_MO, with_any=["Hỏa Tinh"])
tt("tt100_tham_lang_ham", "Tham Lang hãm địa đến hạn thì nên tiết chế ham muốn, chớ cờ bạc mà mất nghiệp", "neg", major="Tham Lang", dig=["hãm"])
tt("tt100_tham_lang_cat_tam_phuong", "Tham Lang hãm mà tam phương có cát tinh thì có thể tránh được tai họa", "pos", major="Tham Lang", dig=["hãm"], tp_cat=True)
tt("tt100_cu_mon_quyen", "hạn Cự Môn đắc địa hóa Quyền thì mưu việc lớn dễ thành; dù lúc đầu có khẩu thiệt, mất chỗ cũ lại là để lên cao hơn", "pos", major="Cự Môn", dig=GOOD, hoa=["Hóa Quyền"])
tt("tt100_cu_mon_buon", "Cự Môn nhập hạn dễ làm người buồn", "neg", major="Cự Môn", not_dig=["hãm"])
tt("tt100_cu_mon_ham", "Cự Môn hãm địa đến hạn rất tai hại: vạ từ đâu bay tới, dễ phá cơ nghiệp", "neg", major="Cự Môn", dig=["hãm"])
tt("tt101_thien_tuong_dac", "Thiên Tướng đắc địa vào nhị hạn thì không sợ tai họa, mưu sự toại ý", "pos", major="Thiên Tướng", dig=GOOD)
tt("tt101_thien_tuong_ac_tinh", "hạn Thiên Tướng có Kình Dương, Đà La, Địa Không, Địa Kiếp hội tụ thì vướng khẩu thiệt, kiện tụng", "neg", major="Thiên Tướng", tp_any=["Kình Dương", "Đà La"], tp_any2=["Địa Không", "Địa Kiếp"])
tt("tt101_thien_tuong_kinh", "hạn Thiên Tướng gặp Kình Dương thì nhiều tai họa", "neg", major="Thiên Tướng", with_any=["Kình Dương"])
tt("tt101_thien_luong_tot", "hạn đến Thiên Lương rất tốt, như hoa cúc mùa thu ngát hương: mưu cầu chức vị đều thành", "pos", major="Thiên Lương", not_dig=["hãm"])
tt("tt101_thien_luong_hoa_linh", "hạn Thiên Lương gặp Hỏa Tinh, Linh Tinh thì nguy hại, dễ tan cửa nát nhà", "neg", major="Thiên Lương", with_any=["Hỏa Tinh", "Linh Tinh"])
tt("tt101_that_sat_dac", "đại tiểu hạn gặp Thất Sát đắc địa thì gia đạo, thân thế vẫn ung dung phấn phát", "pos", major="Thất Sát", dig=GOOD)
tt("tt101_that_sat_phu_trieu", "hạn Thất Sát có Thiên Phủ ở cung đối triều về thì kẻ sĩ danh tiếng hiển đạt", "pos", major="Thất Sát", opp_major=["Thiên Phủ"])
tt("tt102_that_sat_ham", "hạn Thất Sát hãm địa thì thế nào cũng vất vả gian nan", "neg", major="Thất Sát", dig=["hãm"])
tt("tt102_pha_quan_mieu", "hạn Phá Quân ở miếu địa thì phúc lộc dồi dào; thêm Văn Xương, Khôi Việt thì cuộc sống phong quang", "pos", major="Phá Quân", dig=["miếu"], no_sat_tp=True)
tt("tt102_pha_quan_sat", "hạn Phá Quân bị sát tinh tụ thì phải đề phòng hao phá nặng", "neg", major="Phá Quân", tp_sat2=True)
tt("tt102_loc_ton", "hạn Lộc Tồn rất tốt: mưu sự hay, người có chức được chuyển chức, người thường phát tài", "pos", star="Lộc Tồn")
tt("tt103_kinh_duong_tu_mo_tuoi", "hạn có Kình Dương mà người tuổi Thìn, Tuất, Sửu, Mùi thì không sợ họa; lại được Tử Vi, Văn Xương, Thiên Phủ thì quan lộc hiển đạt", "pos", star="Kình Dương", tuoi=TU_MO)
tt("tt103_hoa_tinh_dac", "hạn Hỏa Tinh đắc địa rất tốt: làm việc công dễ thăng, buôn bán phát tài", "pos", star="Hỏa Tinh", dig=GOOD)
tt("tt103_hoa_tinh_ham", "hạn Hỏa Tinh hãm địa thì họa như từ trên trời rơi xuống, phá tài, gian khổ", "neg", star="Hỏa Tinh", dig=["hãm"])
tt("tt103_da_la", "hạn gặp Đà La thì việc lôi thôi rất nhiều; không có cát tinh phù trợ thì mọi sự dễ sụp đổ", "neg", star="Đà La", no_cat=True)
tt("tt103_da_la_nhan_nai", "hạn gặp Đà La nhiều việc, cần nhẫn nại, khiêm hòa", "neg", star="Đà La", tp_cat=True)
tt("tt104_linh_tinh_tham", "hạn đến Linh Tinh gặp Tham Lang thì phú quý, nổi danh", "pos", star="Linh Tinh", with_any=["Tham Lang"])
tt("tt104_linh_tinh_vo_cat", "Linh Tinh vào hạn mà không có cát tinh phù trợ thì gây đảo lộn, khó khăn liên tiếp", "neg", star="Linh Tinh", no_cat=True)
tt("tt104_thien_khong_pha_cua", "Địa Không nhập hạn thì dễ phá của cải, điền sản, tiền bạc thất bại", "neg", star="Địa Không")
tt("tt104_dia_kiep", "Địa Kiếp vào đại tiểu hạn thì năm ấy khó tránh nguy; thêm Thái Tuế thì nhiều chuyện lôi thôi", "neg", star="Địa Kiếp")
tt("tt104_dia_kiep_quan_phu", "hạn Địa Kiếp gặp Quan Phù thì dễ dính đến kiện tụng", "neg", star="Địa Kiếp", with_any=["Quan Phù"])
tt("tt104_thien_thuong", "Thiên Thương vào hạn thì thiếu thốn, khốn đốn", "neg", star="Thiên Thương")
tt("tt105_thien_ma_tu_phu_loc", "hạn đến Thiên Mã gặp Tử Vi, Thiên Phủ và Lộc Tồn rất tốt: người có chức càng hiển đạt, học trò đỗ đạt", "pos", star="Thiên Mã", tp_any=["Tử Vi", "Thiên Phủ"], tp_all=["Lộc Tồn"])
tt("tt105_hoa_loc", "hạn đến Hóa Lộc thì dễ có địa vị, tiền bạc tự tích tụ, làm ăn phát đạt", "pos", hoa=["Hóa Lộc"])
tt("tt105_hoa_quyen", "Hóa Quyền thủ hạn là điều đáng mừng: quan lộc cao sang, có thể dựng nghiệp mới, gia đạo an khang", "pos", hoa=["Hóa Quyền"])
tt("tt105_hoa_quyen_vu_tham", "Hóa Quyền gặp Vũ Khúc, Tham Lang đến hạn thì việc gì cũng trót lọt", "pos", hoa=["Hóa Quyền"], with_any=["Vũ Khúc", "Tham Lang"])
tt("tt105_hoa_khoa_xuong", "hạn đến Hóa Khoa gặp Văn Xương thì kẻ sĩ đỗ đạt nổi danh, thứ dân phú quý, trăm việc đều thành", "pos", hoa=["Hóa Khoa"], with_any=["Văn Xương"])
tt("tt106_hoa_ky_mieu", "Hóa Kỵ nhập miếu lại thành hay, chỉ hiềm việc tiến thoái thất thường", "pos", hoa=["Hóa Kỵ"], hoa_star_dig=["miếu"])

# ---- Khảo Luận pp.233-236 ----
K = {
 "kl233_chinh_tinh_dac": {"src": "kl233_chinh_tinh_dac_ham", "text": "Chính tinh của cung hạn đắc địa thì tốt", "tone": "pos"},
 "kl233_chinh_tinh_ham": {"src": "kl233_chinh_tinh_dac_ham", "text": "Chính tinh của cung hạn hãm địa thì xấu, trừ khi có Tuần hay Triệt giải", "tone": "neg"},
 "kl233_chinh_tinh_ham_giai": {"src": "kl233_chinh_tinh_dac_ham", "text": "Chính tinh của cung hạn hãm địa, nhưng có {tt} ở đó giải nên lại thành tốt", "tone": "pos"},
 "kl233_hung_tinh_dac": {"src": "kl233_hung_tinh_dac", "text": "{stars} đắc địa trong cung hạn thì tốt", "tone": "pos"},
 "kl233_quan_thay": {"src": "kl233_quan_thay_pairs", "text": "{stars} đắc địa gặp đúng sao quan thầy của mình là {master} nên càng tốt", "tone": "pos"},
 "kl233_hung_tinh_ham": {"src": "kl233_hung_tinh_ham", "text": "{stars} hãm địa trong cung hạn thì rất xấu", "tone": "neg"},
 "kl235_that_sat_open": {"src": "kl235_that_sat_open", "text": "Đây là một vận Thất Sát, mà chưa qua vận Thất Sát thì chưa thật sự nổi danh, chưa nếm đủ thăng trầm", "tone": ""},
 "kl236_pha_quan_open": {"src": "kl236_pha_quan_open", "text": "Đây là một vận Phá Quân, mà chưa qua vận Phá Quân thì chưa có dịp trổ tài quyền biến, gây dựng nơi xa quê nhà", "tone": ""},
 "kl236_tham_lang_open": {"src": "kl236_tham_lang_open", "text": "Đây là một vận Tham Lang, mà chưa qua vận Tham Lang thì chưa có dịp kinh doanh lớn, giàu sang to", "tone": ""},
 "kl234_stage": {"src": "kl234_stage_thuan", "text": "", "tone": ""},
 "kl234_stage_n": {"src": "kl234_stage_nghich", "text": "", "tone": ""},
 "th119_trung_phung": {"src": "th119_dai_tieu_trung_phung", "text": "Năm nay tiểu hạn trùng đúng cung đại hạn: khi đại tiểu hạn trùng phùng, tốt hay xấu đều tăng lên rất mạnh", "tone": ""},
}
STAGES = {"thuan": {"Mệnh": "tuổi thơ", "Phụ Mẫu": "tuổi thanh thiếu niên", "Phúc Đức": "tuổi thành niên", "Điền Trạch": "tuổi thành danh", "Quan Lộc": "tuổi nổi danh", "Nô Bộc": "tuổi già", "Thiên Di": "tuổi nghỉ ngơi"},
          "nghich": {"Mệnh": "tuổi thơ", "Huynh Đệ": "tuổi thiếu niên", "Phu Thê": "tuổi thành niên", "Tử Tức": "tuổi thành danh", "Tài Bạch": "tuổi nổi danh", "Thiên Di": "tuổi nghỉ ngơi"}}
STAGE_SRC = {("thuan", p): "kl234_stage_" + {"Mệnh": "menh_thuan", "Phúc Đức": "phuc_thuan", "Điền Trạch": "dien_thuan", "Quan Lộc": "quan_thuan", "Nô Bộc": "no_thuan", "Thiên Di": "di_thuan"}.get(p, "thuan") for p in STAGES["thuan"]}
STAGE_SRC.update({("nghich", p): {"Huynh Đệ": "kl235_stage_huynh_nghich", "Phu Thê": "kl235_stage_phu_the_nghich", "Tử Tức": "kl235_stage_tu_tuc_nghich", "Tài Bạch": "kl235_stage_tai_nghich", "Thiên Di": "kl235_stage_di_nghich"}.get(p, "kl234_stage_nghich") for p in STAGES["nghich"]})
QUAN_THAY = {"Địa Không": "Phá Quân", "Địa Kiếp": "Phá Quân", "Hỏa Tinh": "Tham Lang", "Linh Tinh": "Tham Lang", "Kình Dương": "Thất Sát", "Đà La": "Thất Sát"}
SKIPPED = {
 "tt97_thien_co_chieu": "'Thiên Cơ chiếu hạn' (chiếu, not in) and the other Thiên Cơ verse need the same palace: not settled on the page",
 "tt101_thien_luong_cat": "'cát tinh' without a list", "tt101_thien_luong_tho": "health and longevity", "tt102_pha_quan_that_thoat": "accidents (an unconditional verse of blood)",
 "tt102_pha_quan_mieu_vo_hung": "said by tt102_pha_quan_mieu", "tt102_loc_ton_khoa_quyen": "longevity; the Khoa / Quyền clause differs between verse and translation",
 "tt102_loc_ton_hon_nhan": "marriage and birth events", "tt104_thien_su": "a death story", "tt105_thien_ma_ham_kiep_khong": "the book's own brightness note for Thiên Mã differs from the chart table",
 "tt106_hoa_ky_thien_khong": "punishment and office loss on a 'Không' the verse does not settle",
 "tt99_thai_am_nen_gap": "said by tt99_thai_am", "tt100_tham_lang_tu_mo_hoa": "kept",
}
out = {"version": "van-han-books-1.0.0", "note": __doc__.split("\n\n")[0], "entries": [], "kl": {}, "stages": STAGES, "quan_thay": QUAN_THAY, "skipped": SKIPPED}
for e in E:
    m = MINED[e["id"]]
    assert not m.get("skip"), e["id"]
    out["entries"].append({**e, "book": m["book"], "page": m["page"], "quote": m["quote"]})
for k, v in K.items():
    m = MINED[v["src"]]
    out["kl"][k] = {**v, "book": m["book"], "page": m["page"], "quote": m["quote"]}
for (d, p), mid in STAGE_SRC.items():
    m = MINED[mid]
    out["kl"][f"stage:{d}:{p}"] = {"src": mid, "text": STAGES[d][p], "book": m["book"], "page": m["page"], "quote": m["quote"], "tone": ""}
del SKIPPED["tt100_tham_lang_tu_mo_hoa"]
for k in SKIPPED:
    assert k in MINED, k
(ROOT / "engine" / "data" / "kg" / "van_han_books.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", "utf-8")
print(len(out["entries"]), "verses,", len(out["kl"]), "KL/TH lines")
