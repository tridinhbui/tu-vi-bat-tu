# ---------------------------------------------------------------- sources of school differences (schools.json) not already mined above. TH pp.72-74 and
# p.81 are read on the page images; their quotes are contiguous fragments of the scrambled text layer.
family("th")
page("TH", 72, "II. Cách cuộc lập thành ở 12 cung, A. Quý cách 1-25 (two columns cut into fragments).")
page("TH", 73, "Quý cách 26-51, B. Bần tiện cách 1-4.")
page("TH", 74, "Bần tiện cách 5-9; III. Sinh, vượng, bại, tuyệt địa.")
page("TH", 81, "Đắc địa (end), 12 cung các sao lục hãm.")
SC = "Cách cuộc (TH pp.72-74, 80-81)"


def TS(id, p, quote, topic, statement):
    E(id, "TH", p, "Mệnh", SC, quote, topic, statement, "neutral", [], target="schools")


TS("th72_pha_liem_mao_dau", 72, "9 Phá, Liêm, Mão, Dậu cách (Phá, đóng Mệnh ở Mão, Dậu mới hợp cách tốt, ở các cung", "Phá Quân Mão Dậu",
   "Phá Quân đóng Mệnh ở Mão, Dậu mới hợp cách tốt")
TS("th72_nn_dong_cung", 72, "ật, Nguyệt đo g cung cách", "Nhật Nguyệt đồng cung", "image: '8. Nhật, Nguyệt đồng cung cách' — một quý cách")
TS("th72_nhat_chieu_loi_mon", 72, "23. Nhật chiếu lôi môn cách (Nhật ở Mão có Mệnh)", "Nhật ở Mão", "tên cách: Nhật chiếu lôi môn")
TS("th73_kim_du", 73, "30. Kim dư phù giá cách (Tử vi tại mệnh hay Quan lộc mà giáp Tả Hữu, Thiếu dương, Thiếu", "Kim dư phù giá",
   "Tử Vi ở Mệnh hay Quan Lộc, giáp Tả Hữu hoặc Thiếu Dương, Thiếu Âm")
TS("th73_that_sat_trieu_dau", 73, "34. Thất sát triều đầu cách ( ở Dần, Thân có M", "Thất Sát triều đẩu", "Thất Sát ở Dần, Thân có Mệnh (ở Ngọ là 'ngưỡng đẩu')")
TS("th73_nguyet_sinh_thuong_hai", 73, "ong hải cách (Tức Nguyệt tại Tí) cách này ucngx gọi Mẹnh châu xuất hải", "Nguyệt ở Tý",
   "Nguyệt sinh thương hải (Thái Âm tại Tý), cũng gọi Minh châu xuất hải")
TS("th73_nn_chieu_bich", 73, "28. Nhật, Nguyệt chiếu bích cách (Tức ở Sửu chiếu lên Mùi có Mệnh, hoặc ở Mùi chiếu", "Nhật Nguyệt chiếu bích",
   "Nhật Nguyệt ở Sửu chiếu Mệnh ở Mùi, hoặc ngược lại")
TS("th73_toa_quy", 73, "ïa quí, hướng quí (Mệnh có Khôi đóng, gặp Việt chiếu, hoặc có Việt gặp Khôi chiếu)", "Tọa quý hướng quý",
   "Mệnh có Khôi gặp Việt chiếu, hoặc ngược lại")
TS("th73_vu_loc_giap_ma", 73, "29. Vũ, Lộc giáp Mã cách (Cung Mệnh có Mã giúp lại có Vũ khúc và Hóa lộc hay", "Tài Lộc giáp Mã",
   "Mệnh có Mã, giáp Vũ Khúc và Hóa Lộc hay Lộc Tồn")
TS("th73_tham_hoa", 73, "36. Tham, Hỏa tương hội Tứ mộ cách ( Mệnh hay Quan đóng ở Tứ mộ có Tham, Hỏa hội phát", "Tham Hỏa",
   "Mệnh hay Quan ở Tứ mộ có Tham Lang, Hỏa Tinh hội")
TS("th73_loc_phung_luong_sat", 73, "ùt (Lộc tồn hay Hóa lộc ở Mệnh gặp Không Kiếp đồng", "Lộc phùng lưỡng sát", "Lộc Tồn hay Hóa Lộc ở Mệnh gặp Không Kiếp đồng cung")
TS("th73_tai_an_giap_loc", 73, "Tài Aán giáp lộc (Cung Mệnh có Lộc, lại giáp cung có Vũ, Tướng)", "Tài ấn giáp lộc", "Mệnh có Lộc, giáp Vũ Khúc và Thiên Tướng")
TS("th73_quan_than", 73, "32. Quần Thần khách hội cách (Tử vi gặp toàn cát tinh hội)", "Quân thần khánh hội", "Tử Vi gặp toàn cát tinh hội")
TS("th73_co_luong", 73, "51. Cơ Lương Thìn, Tuất.", "Cơ Lương Thìn Tuất", "một quý cách")
TS("th74_nn_tan_hung", 74, "àn hung (Nhật Nguyệt hãm tại Mệnh mà không có cứu tinh,", "Nhật Nguyệt tàn hung", "Nhật Nguyệt hãm tại Mệnh mà không có cứu tinh, hoặc hãm mà gặp sát tinh")
TS("th80_co_luong_dac_dia", 80, "Thìn Tuất : Cơ, Lương phi tiểu bồ", "Cơ Lương Thìn Tuất", "trong 'Cung các sao đắc địa'")
TS("th81_pha_mao_dau_ham", 81, "Phá Quân : Mão, Dậu bất vi th", "Phá Quân Mão Dậu", "trong '12 cung các sao lục hãm': Phá Quân ở Mão, Dậu không thanh")
TS("th81_liem_pha_mao_dau", 81, "Mão Dậu : Liêm, Phá giữ Dư", "Liêm Phá Mão Dậu", "lục hãm: Liêm, Phá ở Mão Dậu (giữ Dương nhận)")
TS("th81_tham_hoa_loc", 81, "Tham lang, Hoá lộc cư từ mộ", "Tham Lang hóa Lộc ở Tứ mộ", "lục hãm: dù gặp cát cũng chỉ trung bình")

family("kl")


def KS(id, p, quote, topic, statement):
    E(id, "KL", p, "Mệnh", "Khảo Luận (đối chiếu)", quote, topic, statement, "neutral", [], target="schools")


KS("kl48_phu_trai_bat_nhan", 48, "Trai bất nhân, Pha quân Thìn Tuất,", "Phá Quân Thìn Tuất", "dẫn câu phú làm ví dụ")
KS("kl49_phu_so_toet", 49, "Còn giải đoán cứ thấy Phá quân Thìn Tuất là sổ toẹt thì cũng tội cho đương số quá", "Phá Quân Thìn Tuất",
   "cứ thấy Phá Quân Thìn Tuất là phán xấu thì oan cho người có lá số; câu phú có nhiều bản khác nhau")
KS("kl49_phu_ban_khac", 49, "Giái bạc tình Tham Sát Dần cung", "Tham Sát Dần Thân", "các sách chép câu phú khác nhau (Dần Thân / nhàn cung / Dần cung)")
KS("kl64_kiem_ke_co_ngua", 64, "Mệnh ở Ngọ, có Kình dương, gặp Thất sát, Thiên hình đồng cung là cách kiếm kể cổ ngựa",
   "Thất Sát gặp Thiên Hình", "Kình ở Ngọ gặp Thất Sát, Thiên Hình đồng cung là cách kiếm kề cổ ngựa (xấu)")
KS("kl91_dong_khong_nen_sat", 91, "Thiên đồng là sao hiền lành, không nên gặp sát tinh", "Thiên Đồng với sát tinh", "Thiên Đồng không nên gặp sát tinh")
KS("kl203_la_vong_menh", 203, "Mệnh tới đây như bị lưới bó chặt lại", "Thiên La Địa Võng", "Mệnh ở Thìn, Tuất như bị lưới bó chặt")

family("tt")


def TTS(id, p, quote, topic, statement):
    E(id, "TT", p, "Mệnh", "Toàn Thư (đối chiếu)", quote, topic, statement, "neutral", [], target="schools")


TTS("tt123_phu_khong_sai", 123, "hầu như chẳng bao giờ sai", "Phá Quân Thìn Tuất", "câu 'Trai bất nhân Phá Quân Thìn Tuất / Gái bạc tình Tham Sát nhàn cung' hầu như chẳng bao giờ sai")
TTS("tt113_luong_moc", 113, "Thiên Lương Mộc chủ thọ tinh", "hành của Thiên Lương", "phú nôm: Thiên Lương thuộc Mộc")
TTS("tt145_nn_suu_mui_lan_dan", 145, "Nhật Nguyệt đồng cung Sửu Mùi công danh", "Nhật Nguyệt đồng cung Sửu Mùi", "lời bình: Nhật Nguyệt đồng cung Sửu Mùi công danh thường lận đận")
TTS("tt147_dich_ty_cung", 147, "Khi Mệnh đóng Tị cung có sao Thiên Cơ tọa thủ", "phá cách Thiên Cơ", "bản dịch ghi 'Tị cung'")
TTS("tt142_toa_quy", 142, "(Khôi Việt chiếu mệnh, hoặc Khôi ở mệnh Việt hướng vào và ngược lại)", "Tọa quý hướng quý", "Khôi Việt chiếu Mệnh, hoặc Khôi ở Mệnh, Việt hướng vào")
TTS("tt142_that_sat_trieu_dau", 142, "Thất Sát triều đẩu (Thất Sát thủ mệnh ở Dần Thân Tí Ngọ)", "Thất Sát triều đẩu", "Thất Sát thủ Mệnh ở Dần, Thân, Tý, Ngọ")


def TC(id, p, quote, cond, text, pol):
    E(id, "TT", p, "", "chế hóa (Toàn Thư)", quote, cond, text, pol, [], target="che_hoa")


TC("tt66_hoa_loc_do_hai", 66, "vững vàng lại có Hoà Lộc thì đỡ", "Thái Dương hãm hội Hóa Kỵ, Mệnh vững vàng có Hóa Lộc", "Hóa Lộc làm đỡ hại", "support")
TC("tt69_cu_mieu_do_hai", 69, "bị hung tinh phá phách mà Cự Môn miếu địa đỡ", "Cự Môn miếu địa bị hung tinh phá", "Cự Môn miếu thì đỡ hại hơn Cự hãm", "support")
TC("tt93_dau_quan_cat", 93, "Cát tinh giao hội may còn ước mong", "Đẩu Quân ở Tử Tức có cát tinh giao hội", "cát tinh làm nhẹ cái hiếm con của Đẩu Quân", "support")
TC("tt117_hoa_ky_cat_giam", 117, "Nếu có cát tinh phù trợ sẽ giảm nhiều tai nguy", "nữ Mệnh có Hóa Kỵ, có cát tinh phù trợ", "cát tinh giảm nhiều tai nguy của Hóa Kỵ", "support")
