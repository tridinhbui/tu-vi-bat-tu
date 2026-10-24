family("kl")
# ---------------------------------------------------------------- KL pp.43-48 named cách (text layer in order; one cách per numbered item)
page("KL", 43, "CÁCH VÀ PHÚ: A. Quí cách 1-5.")
page("KL", 44, "Quí cách 6-14, B. Phú cách 1.")
page("KL", 45, "Phú cách 2-5, C. Nhàn cách 1-5.")
page("KL", 46, "Nhàn cách 5-9, D. Hạ cách 1-4 (no item 5 printed), 6.")
page("KL", 47, "Hạ cách 6, E. Kỳ cách 1-10.")
page("KL", 48, "Kỳ cách 10-11; Khái niệm về phú đoán.")
M = "Mệnh"
CK = "Cách (KL pp.43-48)"


def K(id, p, quote, cond, reading, pol, concepts, target, **k):
    E(id, "KL", p, k.pop("palace", M), k.pop("heading", CK), quote, cond, reading, pol, concepts, target=target, **k)


K("kl43_kim_du_phu_gia", 43, "Mệnh có Tử vi đắc địa, Tả Hữu tam hợp chiếu, Thiếu dương, Thiếu âm giáp", "Kim dư phù giá", "", "support", [], None,
  dup="TV_TH_CACH_MENH_KIM_DU", notes="TH p.73 has the cách (Tả Hữu or Thiếu Dương / Thiếu Âm giáp); the definitions of KL, TH, TT and 紫微斗數全書 differ: schools.json")
K("kl43_tu_phu_trieu_vien", 43, "Mệnh có Tử vi đắc địa, có Thiên phủ chính chiếu",
  "Mệnh có Tử Vi đắc địa, Thiên Phủ xung chiếu (Tử Sát Tỵ Hợi) hoặc tam hợp chiếu (Tử Vi Tý Ngọ, Tử Tướng Thìn Tuất)", "cách Tử Phủ triều viên: vua quan hội họp",
  "support", ["career.status"], "formation")
K("kl43_phu_tuong_trieu_vien", 43, "Mệnh Thiên phủ, có Thiên tướng đứng hầu", "Mệnh có Thiên Phủ (Thiên Tướng luôn ở tam hợp)",
  "cách Phủ Tướng triều viên", "support", ["career.status"], "formation")
K("kl43_that_sat_trieu_dau", 43, "Thất sát ở Dần Thân ngưỡng phục Phá quân", "Thất sát triều đẩu", "", "support", [], None, dup="TV_TH_CACH_MENH_SAT_TRIEU_DAU",
  notes="KL defines it by Phá Quân at Tý Ngọ; TH p.73 and TT p.142 by Thất Sát at Dần Thân (TT adds Tý Ngọ): schools.json")
K("kl43_than_dong", 43, "Mệnh có Tử vi đồng cung Tấu thư", "Mệnh có Tử Vi và Tấu Thư đồng cung", "cách Thần đồng: thông minh tuyệt vời", "support", ["cog.sharp"], "formation")
K("kl44_thach_trung_an_ngoc", 44, "Mệnh có Cự môn, Di có Thiên cơ  ở Tí Ngọ", "Thạch trung ẩn ngọc", "", "support", [], None, dup="CACH_X_THACH_TRUNG_AN_NGOC",
  notes="KL p.44 adds 'Di có Thiên cơ' (Cự Môn at Tý/Ngọ always faces Thiên Cơ)")
K("kl44_tam_hoa_lien_chau", 44, "Mệnh có Cự môn, Di có Thiên cơ ở Tí Ngọ", "Tam hoá liên châu", "", "support", [], None,
  skip="printing error: the definition repeats item 6 (Thạch trung ẩn ngọc) word for word")
K("kl44_toa_quy_huong_quy", 44, "Mệnh có Khôi, Di có Việt hoặc ngược lại", "Mệnh có Thiên Khôi và Thiên Di có Thiên Việt, hoặc ngược lại",
  "cách Tọa quý hướng quý: người sang quý", "support", ["career.status", "social.support"], "formation")
K("kl44_khoi_viet_giap", 44, "Mệnh ở giữa, Khôi một bên, Việt một bên", "Khôi Việt giáp Mệnh", "", "support", [], None, dup="CACH_X_KHOI_VIET_GIAP_MENH")
K("kl44_nhat_nguyet_giap", 44, "Mệnh ở giữa, Nhật Nguyệt chần hai bên", "Nhật Nguyệt giáp Mệnh", "", "support", [], None, dup="TV_KL_CUNG_MENH_GIAP_NHAT_NGUYET",
  notes="KL p.215 already reads Nhật Nguyệt giáp Mệnh")
K("kl44_nn_chieu_hu_khong", 44, "Mệnh ở Mùi, vô chính diệu, Nhật ở Dần, Nguyệt ở Hợi chiếu lên", "Nhật Nguyệt chiếu hư không", "", "support", [], None,
  skip="Dần is not in the tam phương of Mùi (Hợi, Mão, Sửu): the printed position cannot 'chiếu'")
K("kl44_nhat_xuat_phu_tang", 44, "Mệnh ở Mão có Thái dương, Thiên lương đồng cung", "Nhật xuất phù tang", "", "support", [], None, dup="TV_TH_CACH_MENH_NHAT_MAO",
  notes="the same core as TH p.73 'Nhật chiếu lôi môn' (another name): schools.json")
K("kl44_minh_chau_xuat_hai", 44, "Mệnh đóng ở Tí có Thái âm đồng cung với Thiên đồng", "Minh châu xuất hải", "", "support", [], None, dup="TV_TH_CACH_MENH_NGUYET_TY",
  notes="the same core as TH p.73 'Nguyệt sinh thương hải'; 紫微斗數全書 has 明珠出海 as a separate cách: schools.json")
K("kl44_khoc_hu_ty_ngo_def", 44, "Mệnh có Thiên Hình, Phục binh tam hợp chiếu Tướng quân, Quốc ấn", "Khốc Hư Tí Ngọ", "", "support", [], None,
  skip="the definition does not name Khốc Hư (it is another cách's definition); KL p.202 states Khốc Hư Tí Ngọ itself (kl202_khoc_hu_ty_ngo)")
K("kl44_nn_chieu_bien", 44, "Mệnh vô chính diệu ở Mùi có Nhật Nguyệt đồng cung ở Sửu chiếu lên", "Nhật Nguyệt chiếu biến", "", "support", [], None,
  dup="TV_TH_CACH_MENH_NN_CHIEU_BICH", notes="TH p.73's Nhật Nguyệt chiếu bích has the same core; TT/紫微斗數全書 put 日月照璧 at Điền Trạch: schools.json")
K("kl45_tai_loc_giap_ma", 45, "Mệnh có Thiên mã, Tài (tên gọi của Vũ khúc), Lộc tồn đứng ở cung hai bên",
  "Mệnh có Thiên Mã, hai cung kề có Vũ Khúc và Lộc Tồn", "cách Tài Lộc giáp Mã: thương gia giàu có", "support", ["fin.abundance", "path.business"], "formation")
K("kl45_tham_hoa", 45, "Mệnh ở tứ mộ, có Tham lang đồng cung với Hỏa Linh", "Tham Hỏa tương phùng", "", "support", [], None, dup="TV_TH_CACH_MENH_THAM_HOA")
K("kl45_doi_kim_tich_ngoc", 45, "Mệnh có Thiên phủ – Vũ khúc đồng cung với Lộc tồn ở Tí Ngọ", "Mệnh ở Tý/Ngọ có Thiên Phủ, Vũ Khúc và Lộc Tồn",
  "cách Đôi kim tích ngọc: tiền của đầy nhà", "support", ["fin.abundance"], "formation")
K("kl45_phu_huu_lau_dai", 45, "Mệnh có Cự – Cơ, Song Hao ở Mão Dậu", "Mệnh ở Mão/Dậu có Cự Môn, Thiên Cơ, Song Hao (Đại Hao, Tiểu Hao luôn xung chiếu nhau: một sao ở cung này)",
  "cách Phú hữu lâu đài: nhà cao cửa rộng, tiền dư của để", "support", ["prop.rich", "fin.abundance"], "formation")
K("kl45_tien_cai_hau_ma", 45, "Mệnh ở giữa, Hoa cái ở  cung đằng trước, Thiên Mã ở cung đằng sau",
  "Hoa Cái và Thiên Mã ở hai cung kề Mệnh", "cách Tiền Cái hậu Mã: danh giá, hưởng lộc", "support", ["career.fame"], "formation",
  notes="Hoa Cái (mộ of the year's tam hợp) and Thiên Mã always flank a palace in this order, so 'trước / sau' adds no condition")
K("kl45_long_ho_giap", 45, "Mệnh ở cung giữa, Long trì, Bạch Hổ chầu hai bên", "Long Trì và Bạch Hổ ở hai cung kề Mệnh",
  "cách Long Hổ giáp Mệnh: giàu có, địa vị", "support", ["fin.abundance", "career.status"], "formation",
  skip="Long Trì (Thìn + năm) and Bạch Hổ (Thái Tuế + 8) always stand four palaces apart: they never flank one palace, the cách cannot occur")
K("kl45_van_long_te_hoi", 45, "Mệnh có Thanh long gặp Hóa kỵ, Lưu hà đồng cung", "Mệnh có Thanh Long, Hóa Kỵ và Lưu Hà đồng cung",
  "cách Vân long tế hội: được dịp làm giàu", "support", ["fin.windfall"], "formation")
K("kl45_tien_hinh_hau_an", 45, "Mệnh ở giữa Thiên hình đóng ở cung ở cung đằng trước, Quốc ấn theo sau",
  "Thiên Hình ở cung kề phía trước (chiều thuận) và Quốc Ấn ở cung kề phía sau", "cách Tiền Hình hậu Ấn: có chức có tiền", "support", ["career.status"], "formation",
  notes="'trước' read as the next palace clockwise, as KL p.42 places Lưu Kình 'trước' Lưu Lộc Tồn (Lộc Tồn Tỵ, Kình Ngọ)")
K("kl46_tuong_phuc_hong_dao", 46, "Mệnh có Thiên tướng Phục binh Hồng loan, Đào hoa", "Mệnh có Thiên Tướng, Phục Binh, Hồng Loan, Đào Hoa",
  "cách Tướng Phục Hồng Đào: tuổi trẻ gặp may, sớm làm giàu", "support", ["career.early", "fin.windfall"], "formation")
K("kl46_thai_toa_giap", 46, "Mệnh ở giữa, hai bên có Thai Tọa đứng chầu", "Tam Thai và Bát Tọa ở hai cung kề Mệnh",
  "cách Thai Tọa giáp Mệnh: tuổi trẻ sớm hiển đạt", "support", ["career.early"], "formation")
K("kl46_xuat_tuong_nhap_tuong", 46, "Mệnh có Thiên tướng, Di có Tướng quân hoặc người ngược lại",
  "Mệnh có Thiên Tướng và Thiên Di có Tướng Quân, hoặc ngược lại", "cách Xuất Tướng nhập Tướng: giàu có từ trong ra ngoài", "support", ["fin.abundance"], "formation")
K("kl46_song_long", 46, "Mệnh có Thanh long, Long đức đồng cung", "Mệnh có Thanh Long và Long Đức đồng cung",
  "cách Song Long vượt uyên: gặp thời làm ăn lớn", "support", ["fin.windfall", "career.success"], "formation")
K("kl46_long_phuong_ho_cai", 46, "Mệnh có một hoặc 2 sao trong 4 sao kể trên, còn lại làm tam hợp chiếu",
  "Long Trì, Phượng Các, Bạch Hổ, Hoa Cái đủ cả bốn trong Mệnh và tam hợp, ít nhất một sao ở Mệnh", "cách Long Phượng Hổ Cái: sự nghiệp sẵn sàng, có quý nhân nâng đỡ",
  "support", ["career.success", "social.support"], "formation", notes="booster: 'thường thì Mệnh nên có Bạch Hổ thì hay hơn' (same item)")
K("kl46_ma_lac_khong_vong", 46, "Mệnh có Thiên mã gặp Tuần Triệt án ngữ", "Mã lạc không vong", "", "limit", [], None, dup="TV_TH_CACH_MENH_BT_MA_LAC")
K("kl46_loc_phung_luong_sat", 46, "Mệnh có Lộc tồn, Hóa lộc gặp Không Kiếp đồng cung", "Lộc phùng lưỡng sát", "", "limit", [], None, dup="TV_TH_CACH_MENH_BT_LOC_LUONG_SAT",
  notes="three readings (KL đồng cung, TH, TT/紫微斗數全書 'Lộc tọa Không Vong'): schools.json")
K("kl46_nn_tang_hung", 46, "Mệnh có Thái dương Thái âm hãm địa, thủ mệnh hoặc chiếu mệnh",
  "Thái Dương và Thái Âm đều hãm và đều ở Mệnh hoặc tam phương Mệnh", "cách Nhật Nguyệt tàng hung (hạ cách): trời đất tối tăm", "limit", ["life.hardship"], "rule")
K("kl46_phu_ngo_tuan", 46, "Mệnh có Thiên phủ gặp Tuần an ngữ", "Mệnh có Thiên Phủ, Tuần ở Mệnh", "cách Thiên phủ ngộ Tuần (hạ cách): kho tàng trống rỗng", "limit",
  ["fin.scarcity"], "rule")
K("kl47_de_ngo_hung_do", 47, "Mệnh có Tử Phủ gặp Không Kiếp đồng cung", "Mệnh có Tử Vi, Thiên Phủ, thêm Địa Không hoặc Địa Kiếp đồng cung",
  "cách Đế ngộ hung đồ (hạ cách): dễ táng gia bại sản", "limit", ["fin.volatile"], "rule",
  notes="Không and Kiếp share a palace only at Tỵ/Hợi and Tử Phủ only at Dần/Thân: one of them")
K("kl47_khong_kiep_ty_hoi", 47, "Mệnh đóng ở Tỵ Hợi có Không Kiếp  thủ mệnh", "Mệnh ở Tỵ/Hợi có Địa Không và Địa Kiếp",
  "cách Không Kiếp Tỵ Hợi (kỳ cách): bạo phát bạo tàn", "limit", ["fin.volatile"], "rule")
K("kl47_dao_hoa_thien_khong", 47, "Mệnh có Thiên không, Đào hoa, hoặc có Thiên không, Đào hoa tam hợp chiếu",
  "Thiên Không và Đào Hoa ở Mệnh hoặc tam hợp chiếu Mệnh", "cách Đào hoa Thiên không (kỳ cách): có danh thì nghèo, lên voi xuống chó", "limit", ["fin.volatile"], "rule")
K("kl47_kinh_nhap_mieu", 47, "Mệnh ở tứ mộ có Kình dương tọa thủ", "Kình dương nhập miếu", "", "support", [], None, dup="TV_TH_CACH_MENH_KINH_NHAP_MIEU")
K("kl47_tham_linh", 47, "Mệnh có Tham lang gặp hạn Không Kiếp", "Tham Linh tịch thủ", "", "support", [], None,
  skip="items 4 and 5 swap their definitions (Tham Linh is defined by Không Kiếp, Tham Lang Không Kiếp by Linh Tinh): printing error")
K("kl47_tham_kk", 47, "Mệnh có Tham lang gặp Linh tinh đồng cung", "Tham lang Không Kiếp", "", "support", [], None, skip="see kl47_tham_linh")
K("kl47_cu_ngo_triet", 47, "Mệnh ở Tí Ngọ có Cự môn gặp Triệt án ngữ", "Cự môn ngộ Triệt", "", "support", [], None, dup="CACH_X_THACH_TRUNG_AN_NGOC",
  notes="the booster tuan_triet of the verified cách Thạch trung ẩn ngọc")
K("kl47_hoa_ky_suu_mui", 47, "Mệnh có Cự môn gặp Hóa kỵ đồng cung ở Sửu Mùi", "Mệnh ở Sửu/Mùi có Cự Môn và Hóa Kỵ đồng cung",
  "cách Hóa kỵ Sửu Mùi (kỳ cách): giàu sang phú quý", "support", ["fin.abundance", "career.status"], "formation")
K("kl47_that_sat_ngo_hinh", 47, "Mệnh có Thất sát – Thiên hình đồng cung", "Thất sát ngộ Hình", "", "support", [], None,
  skip="KL p.64 reads the same pair as breaking the cách (formations_verified KL64_PHA): the book is at odds with itself; schools.json")
K("kl47_dong_dinh_mao", 47, "Mệnh người Đinh Mão có Thiên đồng thủ mệnh", "tuổi Đinh Mão, Mệnh có Thiên Đồng",
  "cách Thiên đồng Đinh Mão (kỳ cách): phát phúc, phát lộc", "support", ["life.blessed", "fin.abundance"], "formation")
K("kl48_dong_ngo_viet", 48, "Mệnh có Thiên đồng – Thiên việt đồng cung", "Mệnh có Thiên Đồng và Thiên Việt đồng cung",
  "cách Thiên đồng ngộ Việt (kỳ cách): sang quý", "support", ["career.status"], "formation")
K("kl48_luong_ngo_khoi", 48, "Mệnh có Thiên lương, Thiên khôi đồng cung", "Mệnh có Thiên Lương và Thiên Khôi đồng cung",
  "cách Thiên lương ngộ Khôi (kỳ cách): được hưởng phước lớn", "support", ["life.blessed"], "formation")
K("kl46_effect_thai_toa", 46, "Tuổi trẻ sớm hiển đạt", "effect line of item 6", "", "support", [], None, skip="effect line, read with kl46_thai_toa_giap")

# ---------------------------------------------------------------- KL pp.202-206: Khốc Hư, Song Hao, Tuần Triệt, Cô Quả, Mệnh vô chính diệu, Giáp
page("KL", 202, "33. Thiên hình (end), 34. Phá toái, 35. Khốc Hư (Khốc Hư Tí Ngọ).")
page("KL", 203, "36. Tang Điếu (end), 37. Song Hao, 38. Thương Sứ, 39. Thiên la Địa võng, 40. Tuần Triệt.")
page("KL", 204, "Tuần Triệt (cont.), 41. Cô Quả, 42. Mệnh vô chính diệu, 43. Giáp.")
page("KL", 205, "Giáp cung / giáp góc, Bài thơ Liên Giáp, Bàn về Mệnh vô chính diệu.")
page("KL", 206, "Vô chính diệu (cont.): đắc / ngộ / kiến tam không, the five particular cases.")
K("kl202_khoc_hu_ty_ngo", 202, "Khốc Hư Tí Ngọ tiền bần nhi hậu phú, tiên trở hậu thành", "Mệnh ở Tý/Ngọ có Thiên Khốc và Thiên Hư",
  "trước nghèo sau giàu, trước trở ngại sau mới thành", "support", ["life.late_bloom"], "rule", heading="35. Khốc Hư")
K("kl203_song_hao_menh", 203, "Gặp Song Hao ở Mệnh thì hao tán, thay đổi công việc", "Mệnh có Song Hao (Đại Hao, Tiểu Hao luôn xung chiếu nhau: một sao ở cung này), ngoài Dần Thân Mão Dậu",
  "hao tán, hay thay đổi công việc", "limit", ["fin.volatile"], "rule", heading="37. Song Hao",
  notes="the next sentence makes Dần Thân Mão Dậu the exception (kl203_song_hao_dan_than_mao_dau)")
K("kl203_song_hao_dan_than_mao_dau", 203, "Nhưng Mệnh có Song Hao ở các cung Dần", "Mệnh ở Dần/Thân/Mão/Dậu có Song Hao (Đại Hao, Tiểu Hao luôn xung chiếu nhau: một sao ở cung này)",
  "hoạnh phá nhưng cũng hoạnh phát", "support", ["fin.volatile", "fin.windfall"], "rule", heading="37. Song Hao",
  notes="'Nhưng Mệnh có Song Hao ở các cung Dần Thân Mão Dậu lại tốt vì thay đổi hoạnh phá nhưng cũng hoạnh phát' (line break after 'Dần')")
K("kl203_song_hao_tai_mieu", 203, "Ở cung Tài miếu địa Song Hao cũng hoạnh phá, hoạnh phát", "Tài Bạch có Song Hao (Đại Hao, Tiểu Hao luôn xung chiếu nhau: một sao ở cung này) miếu địa",
  "tiền bạc hoạnh phá, hoạnh phát", "support", ["fin.volatile", "fin.windfall"], "rule", heading="37. Song Hao", palace="Tài Bạch")
K("kl203_song_hao_tai_khong_cu", 203, "Nếu không có Cự môn đồng cung thì Song Hao ở Tài chỉ có hao tán",
  "Tài Bạch có Song Hao (Đại Hao, Tiểu Hao luôn xung chiếu nhau: một sao ở cung này), không có Cự Môn đồng cung", "tiền bạc chỉ có hao tán", "limit", ["fin.volatile"], "rule", heading="37. Song Hao", palace="Tài Bạch",
  notes="'... vì \"Song Hao bất nghi Tài bạch\"'")
K("kl203_song_hao_cu", 203, "Song Hao cần cho Cự môn ở các cung Tài, Mệnh", "Song Hao với Cự Môn ở Tài, Mệnh", "Song Hao rửa đất đá cho ngọc (Cự Môn) lộ ra", "support", [],
  "che_hoa", heading="37. Song Hao")
K("kl203_la_vong", 203, "có sách nói chỉ khi nào có Đà la ở hai cung Thìn Tuất", "Thiên La Địa Võng", "", "limit", [], "schools", heading="39. Thiên la - Địa võng",
  notes="two readings on one page: Mệnh at Thìn/Tuất is caught in the net, or only when Đà La is there too")
K("kl203_tuan_triet_giam", 203, "Tuần Triệt là hai sao cản phá có tác dụng làm giảm cái tốt cũng như giảm cái xấu của các sao",
  "Tuần, Triệt", "giảm cả cái tốt lẫn cái xấu của các sao", "neutral", [], "che_hoa", heading="40. Tuần Triệt")
K("kl203_tuan_triet_dac_thanh_ham", 203, "Chính tinh  đắc địa gặp Tuần Triệt thì trở thành chính tinh hãm địa",
  "chính tinh đắc địa gặp Tuần, Triệt", "chính tinh đắc địa thành như hãm địa", "limit", [], "che_hoa", heading="40. Tuần Triệt")
K("kl203_phu_tuan", 203, "Thiên phủ gặp Tuần thành rỗng", "Thiên Phủ gặp Tuần", "kho rỗng", "limit", [], "che_hoa", heading="40. Tuần Triệt")
K("kl203_ma_triet", 203, "Thiên mã ngộ Triệt thành ngựa què", "Thiên Mã gặp Triệt", "ngựa què", "limit", [], "che_hoa", heading="40. Tuần Triệt")
K("kl203_tuong_triet", 203, "Thiên tướng ngộ Triệt thành tướng mất đầu", "Thiên Tướng gặp Triệt", "tướng mất đầu", "limit", [], "che_hoa", heading="40. Tuần Triệt")
K("kl203_tuan_triet_mieu", 203, "Mệnh đóng tại Dần, Mão, Thân, Dậu thì lại khá",
  "Mệnh ở Dần/Mão/Thân/Dậu có Tuần hoặc Triệt", "Tuần Triệt ở miếu địa của chúng, Mệnh lại khá", "support", ["life.mitigated"], "rule", heading="40. Tuần Triệt",
  notes="'Dần, Mão, Thân, Dậu là miếu địa của Tuần Triệt nên khi Triệt đáo Kim cung (Thân Dậu), Tuần du Mộc vị (Dần Mão), Mệnh đóng tại Dần, Mão, Thân, Dậu thì lại khá' — read as: Triệt at Thân/Dậu or Tuần at Dần/Mão on Mệnh")
K("kl204_menh_triet", 204, "Nếu Mệnh gặp Triệt, đời phải chịu nhiều khó khăn lúc niên thiếu", "Mệnh có Triệt", "thuở nhỏ chịu nhiều khó khăn", "limit",
  ["life.early_hardship"], "rule", heading="40. Tuần Triệt")
K("kl204_menh_tuan", 204, "Nếu Mệnh gặp Tuần, thì luôn luôn bị kìm hãm, trục trặc từ lúc bắt tay vào việc", "Mệnh có Tuần",
  "luôn bị kìm hãm, trục trặc ngay từ khi bắt tay vào việc", "limit", ["career.obstacle"], "rule", heading="40. Tuần Triệt")
K("kl204_tuan_triet_cung_cho", 204, "Nếu Tuần và Triệt cùng đóng chung một chỗ, ảnh hưởng của hai sao được cộng chung",
  "Tuần và Triệt cùng một cung", "sức cản mạnh hơn, sức giúp cũng mạnh hơn", "neutral", [], "che_hoa", heading="40. Tuần Triệt")
K("kl204_chinh_tinh_ham_can_tt", 204, "Chính tinh thủ Mệnh hãm địa thì cần Tuần Triệt để phá hãm",
  "chính tinh hãm ở Mệnh gặp Tuần, Triệt", "Tuần Triệt phá hãm", "support", [], "che_hoa", heading="40. Tuần Triệt",
  notes="the next clause: 'nhưng chính tinh đắc địa gặp Tuần Triệt thì lại bị phá hư'")
K("kl204_co_than_thieu_duong_hong", 204, "gặp được hai sao Thiếu dương sáng",
  "tuổi Thìn/Tuất/Sửu/Mùi, Cô Thần ở Dần/Thân/Tỵ/Hợi gặp Thiếu Dương và Hồng Loan", "đỡ cô đơn", "support", [], "che_hoa", heading="41. Cô thần - Quả tú",
  notes="'Các tuổi Thìn, Tuất, Sửu, Mùi, Cô thần ở Dần, Thân, Tỵ, Hợi gặp được hai sao Thiếu dương sáng suốt, và Hồng loan từ thiện, đạo đức nên cũng đỡ cô đơn'")
K("kl204_vcd_khong_kiep", 204, "có Không Kiếp đồng cung hay xung chiếu nên là những người làm việc rất liều mạng",
  "Mệnh vô chính diệu ở Dần/Thân/Tỵ/Hợi có Địa Không và Địa Kiếp đồng cung hoặc xung chiếu", "làm việc liều mạng, bất chấp hiểm nguy, tìm đường sống trong chỗ chết",
  "limit", ["temper.reckless"], "rule", heading="42. Mệnh vô chính diệu")
K("kl205_giap_goc", 205, "Giáp góc ít hiệu quả hơn giáp cung", "cung ở Dần/Thân/Tỵ/Hợi bị giáp", "giáp góc kém hiệu lực hơn giáp cung", "neutral", [], "combos",
  heading="43. Giáp", notes="'Giáp góc là giáp ở góc thí dụ các cung Dần Thân Tỵ Hợi'")
K("kl205_giap_long_phuong", 205, "Giáp Long, Đà Phượng các đài vinh quang", "Long Trì và Phượng Các ở hai cung kề Mệnh", "vinh quang", "support", ["career.fame"], "rule",
  heading="Bài thơ Liên Giáp", notes="'Đà' in the text layer is a misprint for 'giáp' (giáp Long, giáp Phượng các)")
K("kl205_giap_kinh_da", 205, "Giáp Kình, Đà gian nan vất vả", "Kình Dương và Đà La ở hai cung kề Mệnh (Mệnh có Lộc Tồn)", "gian nan vất vả", "limit", ["life.hardship"],
  "rule", heading="Bài thơ Liên Giáp", notes="Kình and Đà always flank Lộc Tồn: the cách holds exactly when Mệnh has Lộc Tồn")
K("kl205_giap_kiep_khong", 205, "Giáp Kiếp, Không tàn tạ cuộc đời", "Địa Không và Địa Kiếp ở hai cung kề Mệnh", "cuộc đời dễ tàn tạ", "limit", ["life.hardship"], "rule",
  heading="Bài thơ Liên Giáp", notes="KL p.65 (TV_KL_STAR_MENH_KK_GIAP_TY_HOI) reads it only at Tỵ/Hợi; this line has no position")
K("kl205_giap_hoa_linh", 205, "Giáp Hỏa, Linh mệt đứt hơi", "Hỏa Linh giáp Mệnh", "vất vả", "limit", [], None, heading="Bài thơ Liên Giáp", dup="TV_KL_STAR_MENH_HOA_LINH_GIAP")
K("kl205_giap_nhat_nguyet", 205, "Giáp Nhật, giáp Nguyệt gặp thời lên hương", "Nhật Nguyệt giáp Mệnh", "gặp thời", "support", [], None, heading="Bài thơ Liên Giáp",
  dup="TV_KL_CUNG_MENH_GIAP_NHAT_NGUYET")
K("kl205_giap_xuong_khuc", 205, "Giáp Khúc, Xương giỏi văn chương", "Văn Xương và Văn Khúc ở hai cung kề Mệnh", "giỏi văn chương", "support", ["exp.letters"], "rule",
  heading="Bài thơ Liên Giáp", notes="KL p.215 (TV_KL_CUNG_MENH_GIAP_XUONG_KHUC) reads the same giáp as help from superiors; this line names the gift")
K("kl205_giap_thai_toa", 205, "Giáp Thai giáp Tọa nhẹ đường công danh", "Thai Tọa giáp Mệnh", "đường công danh nhẹ nhàng", "support", [], None, heading="Bài thơ Liên Giáp",
  dup="kl46_thai_toa_giap", notes="a second effect source of the cách Thai Tọa giáp Mệnh")
K("kl205_giap_khoi_viet", 205, "Giáp Khôi Việt tên dành bảng hổ", "Thiên Khôi và Thiên Việt ở hai cung kề Mệnh", "thi cử đỗ đạt", "support", ["exp.letters"], "rule",
  heading="Bài thơ Liên Giáp", notes="KL p.215 reads the same giáp as being held in esteem; this line names exams. The verified cách Khôi Việt giáp Mệnh also exists")
K("kl205_giap_sat_liem", 205, "Giáp Sát, Liêm chậm trễ, lỗi thời", "Sát Liêm giáp Mệnh", "chậm trễ", "limit", [], None, heading="Bài thơ Liên Giáp", dup="TV_KL_PHU2_LIEM_SAT_GIAP")
K("kl205_giap_loc_khoa", 205, "Giáp Lộc Khoa sướng tuyệt vời", "Lộc Khoa giáp Mệnh", "sướng", "support", [], None, heading="Bài thơ Liên Giáp",
  skip="'Lộc' (Lộc Tồn or Hóa Lộc) is not settled; KL's own Khoa Lộc giáp rule (TV_KL_STAR_MENH_KHOA_LOC_GIAP) is draft for the same reason")
K("kl206_vcd_ta_huu_nhat_nguyet", 206, "Mệnh vô chính diệu có Tả Hữu đồng cung và Nhật Nguyệt  đắc địa hợp chiếu thì thông minh",
  "Mệnh vô chính diệu có Tả Phụ, Hữu Bật đồng cung; Thái Dương và Thái Âm đắc địa chiếu Mệnh", "thông minh tài giỏi, được mọi người kính phục", "support",
  ["cog.sharp", "social.support"], "rule", heading="Bàn về Mệnh vô chính diệu")
K("kl206_vcd_sat_dac_tam_hoa", 206, "Mệnh vô chính diệu có sát tinh  đắc địa, được Khoa Quyền Lộc tam hợp chiếu thì mở mày",
  "Mệnh vô chính diệu có sát tinh đắc địa; Khoa, Quyền, Lộc tam hợp chiếu", "mở mày mở mặt với đời", "support", ["career.success"], "rule",
  heading="Bàn về Mệnh vô chính diệu")
K("kl206_vcd_han", 206, "đại tiểu vận có Phá quân thì", "VCD + hạn Phá Quân / Tham / Sát", "", "support", [], None, heading="Bàn về Mệnh vô chính diệu",
  skip="readings of the hạn (đại / tiểu vận); van_han_rules.json VH_VCD_SPT already reads VCD meeting Sát Phá Tham in a hạn")
K("kl206_tam_khong", 206, "Đắc tam không là được hưởng thụ một món quà thật lạ thường", "đắc / ngộ / kiến tam không", "", "support", [], None,
  heading="Bàn về Mệnh vô chính diệu", skip="the author calls it 'một trò chơi trí não'; the three 'không' are not named")

# ---------------------------------------------------------------- chế hóa lines from the star sections (KL pp.55-200) for che_hoa.json
page("KL", 55, "Phú Tử Phủ: Tuần Triệt.")
page("KL", 75, "Tử Vi: cứu giải, sợ Kình Đà Không Kiếp Tuần Triệt, không sợ Hỏa Linh.")
page("KL", 81, "Thiên Cơ: sợ Hỏa Linh, thích Song Hao.")
page("KL", 85, "Thái Dương: sợ Kình Đà Không Kiếp, cần Tuần Triệt cứu giải.")
page("KL", 91, "Thiên Đồng: không sợ Tuần Triệt.")
page("KL", 96, "Thiên Phủ: sợ Tuần không sợ Triệt; Tử Vi sợ Triệt; sợ Hóa Kỵ Không Kiếp.")
page("KL", 97, "Thiên Phủ: giảm tính hung hăng của sát tinh.")
page("KL", 101, "Tham Liêm Tỵ Hợi cần Hóa Kỵ hóa giải.")
page("KL", 106, "Cự Môn hãm cần Hóa Khoa.")
page("KL", 108, "Thiên Tướng chế ngự sát tinh, sợ Tuần Triệt Thiên Hình.")
page("KL", 111, "Thiên Lương sợ Tuần Triệt, Hỏa Linh.")
page("KL", 113, "Thất Sát: Tử Vi, Lộc Tồn cứu giải.")
page("KL", 114, "Thất Sát không sợ Tuần Triệt, sai bảo được Kình Đà.")
page("KL", 116, "Phá Quân chế ngự Kình Dương.")
page("KL", 117, "Phá Quân không sợ Tuần Triệt.")
page("KL", 120, "Hóa Khoa đệ nhất giải thần; Thiên Giải, Địa Giải cứu giải nhỏ.")
page("KL", 125, "Không Kiếp hóa giải hiệu lực Tử Vi.")
page("KL", 128, "Xương Khúc không sợ sát tinh, sợ Hóa Kỵ; đối trọng Không Kiếp.")
page("KL", 133, "Lộc Tồn chế ngự tính lả lơi của Đào Hồng.")
page("KL", 145, "Khôi Việt sợ Tuần Triệt, Hình Kỵ, sát tinh.")
page("KL", 146, "Cát tinh sợ Triệt.")
page("KL", 180, "Cự Đồng hãm: Hóa Khoa hoặc Khốc Hư chiếu cứu giải.")
page("KL", 186, "Tử Vi với Tham Lang như hãm; sợ Tuần Triệt Kình Đà Không Kiếp.")
page("KL", 187, "Vũ Khúc đắc địa khắc sát tinh.")
page("KL", 188, "Thiên Đồng không sợ sát tinh; Liêm Trinh sợ Hóa Kỵ; Thiên Phủ sợ Tuần không, Thiên không.")
page("KL", 189, "Thiên Lương không sợ Kình; Thiên Tướng không sợ Không Kiếp, sợ Tuần Triệt; Thiên Tướng chế ngự Liêm Trinh.")
page("KL", 190, "Phá Quân giải Không Kiếp, Thất Sát giải Kình Đà, Tham Lang giải Hỏa Linh.")
page("KL", 194, "Quan Phúc cứu giải; Khôi Việt.")
page("KL", 200, "Hỏa Linh không đánh được Tử Vi, Thiên Phủ, Thái Dương; ngộ chế.")
page("KL", 202, "Thiên Hình ngộ Tuần Triệt; Phá Toái.")
CH = "chế hóa"
K("kl55_tu_phu_tuan_triet", 55, "Mệnh có Tử Phủ thì được hưởng phúc lộc tốt rất nhiều, chỉ sợ Triệt Tuần án ngữ thì kém đi thôi", "Tử Phủ ở Mệnh gặp Tuần, Triệt",
  "phúc lộc kém đi", "limit", [], "che_hoa", heading=CH)
K("kl75_tu_vi_so", 75, "Tử vi rất sợ gặp Kình, Đà, Không, Kiếp, Tuần, Triệt vì chúng biến Tử vi thành một kẻ côi cút", "Tử Vi gặp Kình, Đà, Không, Kiếp, Tuần, Triệt",
  "Tử Vi thành kẻ côi cút, mất sức cứu giải", "limit", [], "che_hoa", heading=CH)
K("kl75_tu_vi_khong_so_hoa_linh", 75, "Tử vi không sợ Hỏa, Linh", "Tử Vi với Hỏa Tinh, Linh Tinh", "Tử Vi không bị Hỏa Linh làm hại", "support", [], "che_hoa", heading=CH)
K("kl81_co_so_hoa_linh_thich_hao", 81, "Thiên cơ rất sợ Hỏa linh nhưng rất thích Song Hao", "Thiên Cơ với Hỏa Linh; với Song Hao", "Hỏa Linh hại Thiên Cơ; Song Hao giúp",
  "neutral", [], "che_hoa", heading=CH, notes="next: 'Cự Cơ ở Mão Dậu gặp Song Hao thì được hưởng phú quí' (the cách of kl45_phu_huu_lau_dai)")
K("kl85_nhat_tuan_triet_cuu", 85, "lúc đó cần Tuần Triệt cứu giải để giảm bớt đau thương", "Thái Dương gặp Kình, Đà, Không, Kiếp, có Tuần hoặc Triệt",
  "Tuần Triệt giảm bớt cái hại của sát tinh cho Thái Dương", "support", [], "che_hoa", heading=CH,
  notes="'Thái dương sợ: Kình, Đà, Không, Kiếp, gặp đám sát tinh này thì công danh trắc trở, đổ vỡ, lúc đó cần Tuần Triệt cứu giải ...'")
K("kl91_dong_khong_so_tuan_triet", 91, "Thiên đồng không sợ Tuần Triệt", "Thiên Đồng gặp Tuần, Triệt", "Thiên Đồng không bị Tuần Triệt hại (có ý kiến cho là cần, để bớt thay đổi)",
  "support", [], "che_hoa", heading=CH)
K("kl96_phu_tuan_khong_triet", 96, "Thiên phủ rất sợ Tuần mà lại không sợ Triệt, Tử vi lại rất sợ Triệt", "Thiên Phủ với Tuần, Triệt; Tử Vi với Triệt",
  "Tuần hại Thiên Phủ, Triệt thì không; Triệt hại Tử Vi", "limit", [], "che_hoa", heading=CH)
K("kl96_phu_so_ky_kk", 96, "Thiên phủ sợ gặp Hóa kỵ và Không Kiếp", "Thiên Phủ gặp Hóa Kỵ, Không, Kiếp", "Thiên Phủ bị hại, Mệnh dễ nghèo", "limit", [], "che_hoa", heading=CH)
K("kl97_phu_giam_sat", 97, "giảm bớt tính hung hăng của lũ sát tinh", "Thiên Phủ với sát tinh", "Thiên Phủ giảm bớt tính hung hăng của sát tinh", "support", [], "che_hoa",
  heading=CH)
K("kl101_tham_liem_can_ky", 101, "Tham Liêm đồng cung ở Tỵ, Hợi : trai đàng điếm, gái giang hồ, cần có Hóa kỵ mới hóa giải", "Tham Liêm Tỵ Hợi gặp Hóa Kỵ",
  "Hóa Kỵ hóa giải cái xấu của Tham Liêm Tỵ Hợi", "support", [], "che_hoa", heading=CH)
K("kl106_cu_ham_khoa", 106, "Cự môn hãm địa cần có Hóa khoa cứu giải", "Cự Môn hãm gặp Hóa Khoa", "Hóa Khoa cứu giải Cự Môn hãm", "support", [], "che_hoa", heading=CH)
K("kl108_tuong_che_sat", 108, "Thiên tướng không sợ Sát tinh mà còn chế ngự được chúng", "Thiên Tướng với sát tinh", "Thiên Tướng chế ngự sát tinh", "support", [], "che_hoa",
  heading=CH)
K("kl108_tuong_so_tt_hinh", 108, "Thiên tướng sợ Tuần Triệt, Thiên hình", "Thiên Tướng gặp Tuần, Triệt, Thiên Hình", "công danh trắc trở", "limit", [], "che_hoa", heading=CH)
K("kl111_luong_so", 111, "Thiên lương sợ Tuần Triệt, Hỏa Linh", "Thiên Lương gặp Tuần, Triệt, Hỏa, Linh", "cuộc sống lao đao", "limit", [], "che_hoa", heading=CH)
K("kl113_sat_tu_loc_cuu", 113, "nhờ Tử vi, Lộc tồn cứu giải được", "Thất Sát ở Mệnh với Tử Vi, Lộc Tồn", "Tử Vi, Lộc Tồn cứu giải tai nạn của Thất Sát", "support", [],
  "che_hoa", heading=CH, notes="'Cung Mệnh có Thất sát thường bị tai nạn, nhờ Tử vi, Lộc tồn cứu giải được'")
K("kl114_sat_khong_so", 114, "Thất sát không sợ Tuần Triệt, không ngán Kình Đà", "Thất Sát với Tuần, Triệt, Kình, Đà", "Thất Sát không bị hại, còn sai khiến được Kình Đà",
  "support", [], "che_hoa", heading=CH)
K("kl116_pha_che_kinh", 116, "Phá quân chế ngự", "Phá Quân với Kình Dương", "Phá Quân chế ngự Kình Dương", "support", [], "che_hoa", heading=CH,
  notes="'Phá quân chế ngự / được Kình dương.' (line break)")
K("kl117_pha_khong_so_tt", 117, "Phá quân không sợ Tuần Triệt", "Phá Quân gặp Tuần, Triệt", "Phá Quân không bị Tuần Triệt hại", "support", [], "che_hoa", heading=CH)
K("kl120_khoa_de_nhat_giai_than", 120, "Hóa khoa được coi là sao cứu giải mạnh nhất", "Hóa Khoa", "sao cứu giải mạnh nhất", "support", [], "che_hoa", heading=CH)
K("kl120_thien_dia_giai", 120, "Các sao Thiên giải và Địa giải là những sao cứu giải nhỏ", "Thiên Giải, Địa Giải", "cứu giải nhỏ", "support", [], "che_hoa", heading=CH)
K("kl125_kk_hoa_giai_tu", 125, "Một trong hai sao cũng đủ hóa giải hết hiệu lực của Tử vi", "Tử Vi gặp Địa Không hoặc Địa Kiếp", "mất hết hiệu lực của Tử Vi", "limit", [],
  "che_hoa", heading=CH)
K("kl128_xuong_khuc_so_ky", 128, "Xương Khúc không sợ Sát Tinh, chỉ sợ Hóa Kỵ", "Xương Khúc với sát tinh; với Hóa Kỵ", "sát tinh không hại Xương Khúc, Hóa Kỵ thì hại",
  "neutral", [], "che_hoa", heading=CH)
K("kl133_loc_ton_che_dao_hong", 133, "Đoan chính, chế ngự được tính lả lơi của Đào Hồng", "Lộc Tồn với Đào Hoa, Hồng Loan", "Lộc Tồn chế ngự tính lả lơi của Đào Hồng",
  "support", [], "che_hoa", heading=CH)
K("kl145_khoi_viet_so", 145, "Khôi Việt sợ Tuần Triệt, Hình Kỵ, Kình Đà, Không Kiếp, Hỏa Linh", "Khôi Việt gặp Tuần, Triệt, Thiên Hình, Hóa Kỵ, sát tinh",
  "công danh trắc trở", "limit", [], "che_hoa", heading=CH)
K("kl146_cat_tinh_so_triet", 146, "Các cát tinh sợ Triệt vì không có dịp phát triển thành công", "cát tinh gặp Triệt", "cát tinh khó phát triển", "limit", [], "che_hoa",
  heading=CH)
K("kl180_cu_dong_khoa_khoc_hu", 180, "có sao cứu giải như Hóa khoa hoặc khốc Hư chiếu", "Cự Đồng hãm có Hóa Khoa hoặc Khốc Hư chiếu", "Cự Đồng hãm mới khá được", "support", [],
  "che_hoa", heading=CH, notes="'Cự Đồng lẻ loi, hãm địa thành ra bất đắc chí, có sao cứu giải như Hóa khoa hoặc khốc Hư chiếu mới khá được' (Tử Vi ở Ngọ)")
K("kl186_tu_tham_ham", 186, "Tử vi là sao cứu giải trong mọi hoàn cảnh nhưng khi đi với Tham lang thì coi như bị vào hãm địa", "Tử Vi đồng cung Tham Lang",
  "Tử Vi coi như hãm, mất sức cứu giải", "limit", [], "che_hoa", heading=CH)
K("kl186_tu_so", 186, "Tử vi sợ Tuần Triệt, Kình Đà, Không Kiếp", "Tử Vi gặp Tuần, Triệt, Kình, Đà, Không, Kiếp", "đế ngộ hung đồ, thất bại chua cay", "limit", [], "che_hoa",
  heading=CH)
K("kl187_vu_khac_sat", 187, "chẳng sợ sát tinh nào mà còn là khắc của các sát tinh", "Vũ Khúc đắc địa với sát tinh", "Vũ Khúc đắc địa khắc chế sát tinh", "support", [], "che_hoa",
  heading=CH)
K("kl188_dong_khong_so_sat", 188, "Thiên đồng không sợ sát tinh", "Thiên Đồng với sát tinh", "Thiên Đồng không bị sát tinh hại", "support", [], "che_hoa", heading=CH,
  notes="KL p.91 says the opposite for Hỏa Tinh, Hình Kỵ ('Thiên đồng là sao hiền lành, không nên gặp sát tinh'): schools.json")
K("kl188_liem_so_ky", 188, "Liêm trinh rất sợ Hóa kỵ", "Liêm Trinh gặp Hóa Kỵ", "Liêm Trinh bị Hóa Kỵ hại", "limit", [], "che_hoa", heading=CH)
K("kl188_phu_so_khong", 188, "Thiên phủ sợ Tuần không, Thiên không", "Thiên Phủ gặp Tuần, Thiên Không", "kho rỗng", "limit", [], "che_hoa", heading=CH)
K("kl189_luong_khong_so_kinh", 189, "Thiên lương không sợ Kình dương, nhưng gặp Song Hao, Không Kiếp, Tuần Triệt thì bị tai họa",
  "Thiên Lương với Kình Dương; với Song Hao, Không Kiếp, Tuần Triệt", "Kình không hại Thiên Lương; Song Hao, Không Kiếp, Tuần Triệt thì hại", "neutral", [], "che_hoa",
  heading=CH)
K("kl189_tuong_khong_so_kk", 189, "Thiên tướng không sợ Không Kiếp, nhưng sợ Tuần Triệt", "Thiên Tướng với Không Kiếp; với Tuần Triệt",
  "Không Kiếp không hại Thiên Tướng; Tuần Triệt thì hại", "neutral", [], "che_hoa", heading=CH)
K("kl189_tuong_che_liem", 189, "Thiên tướng canh chừng Phá quân, chế ngự Liêm trinh", "Thiên Tướng với Phá Quân, Liêm Trinh", "Thiên Tướng chế ngự Liêm Trinh, canh chừng Phá Quân",
  "support", [], "che_hoa", heading=CH)
K("kl190_tham_giai_hoa_linh", 190, "và Tham lang", "Tham Lang với Hỏa Tinh, Linh Tinh", "Tham Lang giải trừ ác tính của Hỏa Linh", "support", [], "che_hoa", heading=CH,
  notes="'Phá quân giải trừ được ác tính của Không Kiếp, cũng như Thất sát giải trừ Kình Đà, và Tham lang / giải trừ Hỏa Linh.' (line break); the Phá Quân and Thất Sát halves are already star_nature entries")
K("kl194_quan_phuc", 194, "Quan Phúc không phải sao cản hãm như Tuần Triệt mà là những sao cứu giải thuần túy", "Thiên Quan, Thiên Phúc", "cứu giải thuần túy", "support", [],
  "che_hoa", heading=CH)
K("kl194_quan_phuc_nang", 194, "Gặp trường hợp nặng, phải đủ cả hai Phúc và Quan mới cứu giải được", "Thiên Quan và Thiên Phúc (và Khôi Việt)",
  "trường hợp nặng cần đủ cả Quan, Phúc, có khi cần thêm Khôi Việt", "support", [], "che_hoa", heading=CH)
K("kl200_hoa_linh_khong_danh", 200, "Hỏa Linh không đánh được các sao Tử vi, Thiên phủ, Thái dương", "Hỏa Linh với Tử Vi, Thiên Phủ, Thái Dương",
  "Hỏa Linh không hại được ba sao này", "support", [], "che_hoa", heading=CH)
K("kl200_ngo_che", 200, "Khí bị hóa giải, các hung sát tinh thành ra ngộ chế", "hung sát tinh gặp sao giải mạnh", "hung sát tinh bị vô hiệu hóa (ngộ chế)", "support", [],
  "che_hoa", heading=CH)
K("kl202_hinh_tuan_triet", 202, "Thiên hình ngọ Tuần  Triệt thì thành kiếm gẫy", "Thiên Hình gặp Tuần, Triệt", "kiếm gãy: dễ mất việc, bị buộc từ chức", "limit", [], "che_hoa",
  heading=CH)
K("kl202_pha_toai_hao_hien", 202, "Phá toái không phò trợ mà chỉ làm hao tán chính diệu nhất là các sao Tử vi, Thiên",
  "Phá Toái với Tử Vi, Thiên Phủ, Thiên Lương, Thiên Cơ", "Phá Toái làm hao tán các sao hiền", "limit", [], "che_hoa", heading=CH,
  notes="'... Tử vi, Thiên phủ, Thiên lương, Thiên cơ là những sao hiền lành. Trái lại, Phá toái làm tăng sức mạnh của bộ hung tinh Sát Phá Tham'")
K("kl202_pha_toai_tang_spt", 202, "Phá toái làm tăng sức mạnh của bộ hung tinh Sát", "Phá Toái với Sát Phá Tham", "Phá Toái làm Sát Phá Tham mạnh thêm", "neutral", [], "che_hoa",
  heading=CH)

# ---------------------------------------------------------------- KL pp.166-186 chính tinh groups, the twelve vòng and 'thế đứng' (combos.json)
page("KL", 166, "Nhóm hành động: Tử Phủ Vũ Tướng (hành động có lý luận).")
page("KL", 167, "Sát Phá Liêm Tham; nhóm lý luận: Cơ Nguyệt Đồng Lương, Cự Nhật / Nhật Nguyệt; Vòng Một (Tử Vi Ngọ) begins. The vòng diagrams (pp.167-178) "
                "scramble cell order in the text layer: their per-palace keywords are not mined in this batch.")
page("KL", 172, "Vòng Sáu headline (Tử Phá Sửu).")
page("KL", 179, "Nhận xét 12 vòng; Tử Phá Sửu Mùi; THẾ ĐỨNG CỦA HAI NHÓM CHÍNH TINH begins.")
page("KL", 180, "Thế đứng 1 (Tử Ngọ), 2 (Tử Tí).")
page("KL", 181, "Thế đứng 3 (Tử Sát Tỵ), 4 (Tử Sát Hợi).")
page("KL", 182, "Thế đứng 5, 6 (Tử Tướng Thìn Tuất), 7 (Tử Tham Mão).")
page("KL", 183, "Thế đứng 7 (cont.), 8 (Tử Tham Dậu), 9 (Tử Phủ Dần).")
page("KL", 184, "Thế đứng 9 (cont.), 10 (Tử Phủ Thân), 11 (Tử Phá Sửu).")
page("KL", 185, "Thế đứng 12 (Tử Phá Mùi); nhận xét chung.")
page("KL", 186, "Tóm tắt các sao: Tử Vi.")
G = "Mười hai vòng chính tinh / thế đứng"


def KC(id, p, quote, cond, reading, pol="neutral", **k):
    E(id, "KL", p, "", G, quote, cond, reading, pol, [], **{"target": "combos", **k})


KC("kl166_tpvt", 166, "Tử Phủ Vũ Tướng (Hành động có lý luận)", "nhóm Tử Phủ Vũ Tướng", "nhóm hành động có lý luận")
KC("kl167_splt", 167, "Sát Phá Liêm Tham (Hành động mạch mẽ)", "nhóm Sát Phá Liêm Tham", "nhóm hành động mạnh mẽ")
KC("kl167_cndl", 167, "Cơ Nguyệt Đồng Lương (Lý luận thuần túy)", "nhóm Cơ Nguyệt Đồng Lương", "nhóm lý luận thuần túy")
KC("kl167_cu_nhat", 167, "Cự - Nhật, Nhật - Nguyệt (Lý luận thực hành)", "nhóm Cự Nhật, Nhật Nguyệt", "nhóm lý luận thực hành")
KC("kl167_hanh_dong", 167, "Khi gặp nhóm hành động là lúc ta đang bận rộn, vất vả", "nhóm hành động (Tử Phủ Vũ Tướng, Sát Phá Liêm Tham)", "lúc gặp là lúc bận rộn, vất vả")
KC("kl167_ly_luan", 167, "Khi gặp nhóm lý luận là lúc ta đang tính toán suy", "nhóm lý luận (Cơ Nguyệt Đồng Lương, Cự Nhật)", "lúc gặp là lúc tính toán, suy nghĩ")
KC("kl179_tu_pha_suu", 179, "Tử vi Phá quân gặp nhau ở Sửu là thế Tử Phá", "Tử Vi, Phá Quân đồng cung ở Sửu/Mùi",
   "hai phe cân bằng, hiện nguyên hình con người bình thường, có cao thượng có thấp hèn")
KC("kl179_tu_ngo_dan_di_xuong", 179, "Tử vi từ Ngọ đến Dần là đang đi xuống, Phá quân đi", "vị trí Tử Vi trên địa bàn", "Tử Vi từ Ngọ đến Dần đang đi xuống, Phá Quân từ Thân đến Mùi đang đi lên")
KC("kl180_tu_ngo", 180, "Khi Tử vi  đắc địa ở Ngọ thì kéo Vũ Tướng, Liêm Phủ  đắc địa theo, nhóm Tử Vũ Liêm ở thế", "thế Tử Vi ở Ngọ",
   "nhóm Tử Vũ Liêm ở thế thượng phong, giàu sang phú quý; Sát Phá Tham bị dồn vào thế hãm", "support")
KC("kl180_co_am_giau", 180, "Cơ Âm  đắc địa thì giầu", "Thiên Cơ, Thái Âm đắc địa (thế Tử Vi ở Ngọ)", "giàu", "support")
KC("kl180_duong_luong_sang", 180, "Dương Lương  đắc địa thì sang", "Thái Dương, Thiên Lương đắc địa (thế Tử Vi ở Ngọ)", "sang", "support")
KC("kl180_cu_dong_le_loi", 180, "Cự Đồng lẻ loi, hãm địa thành ra bất đắc chí", "Cự Môn, Thiên Đồng hãm (thế Tử Vi ở Ngọ)", "bất đắc chí", "limit")
KC("kl180_sat_co_don", 180, "Thất Sát cô đơn không có hậu thuẫn", "Thất Sát ở Thìn, nhị hợp vô chính diệu (thế Tử Vi ở Ngọ)", "cô đơn, không có hậu thuẫn", "limit")
KC("kl180_tu_ty", 180, "Người có cách Tử vi ở Tí thua thiệt hơn cách Tử vi ở Ngọ rõ ràng", "thế Tử Vi ở Tý", "thua thiệt hơn thế Tử Vi ở Ngọ: Tử Vi, Cơ Âm, Dương Lương hãm", "limit")
KC("kl180_dac_ham_the_dung", 180, "khái niệm về  đắc địa, hãm địa của các chính tinh người xưa đặt ra là để căn cứ vào thế đứng",
   "đắc / hãm của chính tinh", "đắc hãm căn cứ vào thế đứng của hai nhóm Tử Vi và Phá Quân, không do ngũ hành sao với cung", target="schools")
KC("kl181_tu_sat_ty", 181, "Cơ Âm, Dương Cự, Vũ Tham, Đồng Âm đều  đắc địa", "thế Tử Sát ở Tỵ", "Cơ Âm, Dương Cự, Vũ Tham, Đồng Âm đều đắc địa; Thiên Tướng cô đơn; Liêm Phá bị coi là hãm",
   "support")
KC("kl181_tuong_nhi_hop_vcd", 181, "Thiên tướng lâm vào thế hãm, cô đơn không có hậu thuẫn (nhị hợp vô chính diệu)", "Thiên Tướng có cung nhị hợp vô chính diệu",
   "Thiên Tướng cô đơn, không có hậu thuẫn", "limit")
KC("kl181_liem_pha_khien_cuong", 181, "Duy chỉ có Liêm Phá lại bị hãm địa, theo quan niệm xưa, e là khiên cưỡng", "Liêm Phá ở Mão Dậu (thế Tử Sát)",
   "tác giả cho rằng coi là đắc địa thì hợp lý hơn", target="schools")
KC("kl181_tu_sat_hoi", 181, "Vậy thì người có cách Tử Sát ở Hợi có phần thiệt thòi hơn cách Tử Sát ở Tỵ", "thế Tử Sát ở Hợi", "thiệt thòi hơn thế Tử Sát ở Tỵ (Đồng Âm Ngọ, Thái Dương Thân hãm)",
   "limit")
KC("kl182_tu_tuong_thin", 182, "Lần này thì phe Sát Phá Tham vùng lên ngang ngửa,  đắc địa như ai", "thế Tử Tướng ở Thìn, Tuất",
   "Tử Tướng, Phủ Vũ, Liêm Trinh đắc địa; Sát Phá Tham cũng đắc địa; Đồng Lương chia cách, Thiên Lương hãm", "support")
KC("kl182_tu_tham_mao", 182, "Tham lang hãm địa, Cơ Âm hãm địa", "thế Tử Tham ở Mão", "Tham Lang, Cơ Âm, Thái Dương, Cự Môn, Vũ Phá hãm; chỉ Liêm Sát đắc địa", "limit")
KC("kl183_tu_tham_dau", 183, "So sách 2 thế Tử Tham ở Mão và Tử Tham ở Dậu, thì Tử Tham ở Dậu khá hơn Tử Tham ở", "thế Tử Tham ở Dậu",
   "khá hơn Tử Tham ở Mão nhiều (Cơ Âm, Thái Dương đắc địa)", "support")
KC("kl183_tu_phu_dan", 183, "Hai phe Tử vị - Phá quân chia đều thế đắc địa của mình", "thế Tử Phủ ở Dần", "hình ảnh sung túc thịnh vượng; chỉ Thái Âm, Thái Dương hãm", "support")
KC("kl184_tu_phu_than", 184, "Người có thế Tử vi ở Thân, thì dù Mệnh đóng ở cung nào cũng được hưởng phú quí cả", "thế Tử Phủ ở Thân",
   "trường hợp toàn mỹ nhất trong 12 vòng: dù Mệnh ở cung nào cũng được hưởng phú quý", "support")
KC("kl184_tu_pha_suu_ben", 184, "có giầu sang một thời rồi cũng chẳng bền", "thế Tử Phá ở Sửu", "chỉ Tử Phá tung hoành, giàu sang một thời rồi cũng chẳng bền", "limit")
KC("kl185_tu_pha_mui", 185, "Người có cách Tử Phá ở Mùi khá hơn ở Sửu rất nhiều", "thế Tử Phá ở Mùi", "khá hơn ở Sửu rất nhiều; Liêm Tham, Thất Sát hãm", "support")
KC("kl185_khong_cong_thuc", 185, "Tựu trung thì căn cứ vào thế đứng của hai nhóm Tử vi, Phá quân trong 12 vòng, có vẻ hợp lý hơn",
   "đắc / hãm", "đắc hãm theo thế đứng hợp lý hơn theo ngũ hành sao với cung", target="schools")
KC("kl186_tu_ta_huu", 186, "Tử vi cần nhất  Tả Hữu, hai tay chân đắc lực nhất", "Tử Vi với Tả Phụ, Hữu Bật", "Tả Hữu là hai tay chân đắc lực nhất của Tử Vi", "support")
KC("kl186_tu_phu_dan_than", 186, "hai Vua tôi Tử vi và Thiên phủ cùng ngồi", "Tử Phủ đồng cung Dần, Thân", "vua tôi cùng ngồi bàn việc nước", "support")
