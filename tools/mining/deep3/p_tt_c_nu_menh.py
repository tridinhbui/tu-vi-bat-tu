family("tt")
# ---------------------------------------------------------------- TT pp.112-120 nữ mệnh ca (pp.108-112 are pack_toan_thu_nu.json). Most lines are
# about marriage, chastity, the husband's death and childbirth (left out by policy); kept: the woman's own gifts and fortune.
page("TT", 112, "Bạc tình / dâm lines; Cự Môn nữ mệnh ca; Thiên Tướng nữ mệnh ca (verse).")
page("TT", 113, "Thiên Tướng 'Nghĩa là' + phú nôm; Thiên Lương nữ ca; Thất Sát nữ ca (verse).")
page("TT", 114, "Thất Sát 'Nghĩa là', Phá Quân nữ ca, Văn Xương nữ ca (verse).")
page("TT", 115, "Văn Xương 'Nghĩa là' + phú nôm, Văn Khúc nữ ca, Tả Hữu nữ ca.")
page("TT", 116, "Tả Hữu phú nôm, Lộc Tồn nữ ca + phú nôm, Kình Dương nữ ca, Đà La nữ ca.")
page("TT", 117, "Hỏa Linh, Hóa Quyền, Hóa Khoa, Hóa Kỵ nữ ca; Nữ mệnh cốt tủy phú begins.")
page("TT", 118, "Nữ mệnh cốt tủy phú (cont.).")
page("TT", 119, "Phú nôm nữ mệnh (mostly marriage / chastity).")
page("TT", 120, "Phú nôm cung Phu (marriage events).")
M = "Mệnh"
E("tt112_cu_nu_vuong_ta_huu", "TT", 112, M, "Cự Môn nữ mệnh ca", "được Tả Hữu tuổi thọ thêm lên", "", "", "support", [], skip="longevity")
E("tt112_bac_tinh_dan_than", "TT", 112, M, "Phú nôm nữ", "Dần Thân, Tham Sát giữ tày nhân cung", "", "", "limit", [], skip="a woman's fidelity (sexual reputation)")
E("tt113_tuong_nu_thong_minh", "TT", 113, M, "Thiên Tướng nữ mệnh ca", "Nữ mệnh có sao Thiên Tướng, người thông minh giỏi giang, y lộc tài bạch phong túc",
  "nữ, Mệnh có Thiên Tướng", "thông minh, giỏi giang, y lộc tiền bạc đầy đủ", "support", ["cog.sharp", "fin.abundance"],
  notes="the sentence ends 'vượng phu ích tử' (husband and children: left out)",
  skip="a one-star trait at Mệnh that the KL / TH star rules already give; not added as a third generic line (readable.test Barnum gate: the Mệnh chapter must not drift to what every chart gets)")
E("tt113_tuong_nu_sat_pha", "TT", 113, M, "Thiên Tướng nữ mệnh ca", "Nếu Thiên Tướng hội cùng Thất Sát Phá Quân và Dương Đà Hỏa Linh thì sát chồng",
  "", "", "limit", [], skip="the husband's death and children")
E("tt114_sat_nu_thong_minh", "TT", 114, M, "Thất Sát nữ mệnh ca", "người rất lanh lợi thông minh",
  "nữ, Mệnh có Thất Sát", "rất lanh lợi, thông minh (sách nói thêm là phải gian lao vất vả)", "support", ["cog.sharp"],
  notes="'Nữ Mệnh Thất Sát tọa thủ là điều đáng buồn, người rất lanh lợi thông minh, khi cao lớn như con trai, tuy nhiên, thế nào cũng hình phu và gian lao vất vả' — the hình phu clause is left out",
  skip="a one-star trait at Mệnh that the KL / TH star rules already give; not added as a third generic line (readable.test Barnum gate: the Mệnh chapter must not drift to what every chart gets)")
E("tt114_pha_nu_ty_ngo", "TT", 114, M, "Phá Quân nữ mệnh ca", "nữ mệnh tính cách mạnh bạo hơn người lại",
  "nữ, Mệnh ở Tý/Ngọ có Phá Quân (verse 'Phá Quân Tí Ngọ vi nhập miếu')", "tính mạnh bạo hơn người, có tài năng, nổi tiếng", "support", ["temper.assertive", "exp.talent"],
  notes="the translation prints 'Phá Quân đóng Tị Ngọ là nhập miếu'; the verse says Tí Ngọ, followed here; 'vượng phu ích tử' left out")
E("tt115_xuong_nu_tu_phu", "TT", 115, M, "Văn Xương nữ mệnh ca", "nếu có hai sao Tử Vi Thiên Phủ",
  "nữ, Mệnh có Văn Xương; Tử Vi và Thiên Phủ trong tam phương", "phú quý", "support", ["fin.abundance"],
  notes="'Văn Xương vào mệnh đàn bà, người đẹp thanh kỳ nếu có hai sao Tử Vi Thiên Phủ tam hợp chiếu phú quí được mặc áo gấm đẹp' (appearance clause left out)")
E("tt115_khuc_nu_thong_minh", "TT", 115, M, "Văn Khúc nữ mệnh ca", "thông minh lanh lợi",
  "nữ, Mệnh có Văn Khúc", "thông minh lanh lợi khác người", "support", ["cog.sharp"],
  notes="'Nữ mệnh có sao Văn Khúc, tướng mạo đẹp đẽ dễ hưởng phúc, thông minh lanh lợi khác người chỉ sợ gặp sát tinh ...' (appearance and the sát clause left out)",
  skip="a one-star trait at Mệnh that the KL / TH star rules already give; not added as a third generic line (readable.test Barnum gate: the Mệnh chapter must not drift to what every chart gets)")
E("tt115_ta_huu_nu", "TT", 115, M, "Tả Hữu nữ mệnh ca", "Nữ mệnh có Tả Hữu là người hiền lương, giỏi giang quán xuyến",
  "nữ, Mệnh có Tả Phụ hoặc Hữu Bật", "hiền lương, giỏi giang, quán xuyến", "support", ["values.kind", "exp.talent"],
  skip="a one-star trait at Mệnh that the KL / TH star rules already give; not added as a third generic line (readable.test Barnum gate: the Mệnh chapter must not drift to what every chart gets)")
E("tt115_ta_huu_nu_tu_phu", "TT", 115, M, "Tả Hữu nữ mệnh ca", "nếu được Tử Vi, Thiên Phủ hợp thì phúc lộc vô tả",
  "nữ, Mệnh có Tả Phụ hoặc Hữu Bật; Tử Vi và Thiên Phủ trong tam phương", "phúc lộc dồi dào", "support", ["life.blessed"])
E("tt116_loc_ton_nu_tu_phu", "TT", 116, M, "Lộc Tồn nữ mệnh ca", "được hội với Tử Vi, Thiên Phủ lại thêm Thiên Đồng", "", "", "support", [],
  skip="'số phu nhân' (a husband's rank) is the reading; the condition list (Tử Phủ + Đồng Liêm) cannot all meet")
E("tt116_ma_menh_ton_di", "TT", 116, M, "Lộc Tồn nữ mệnh ca", "Mã mệnh cung, Tồn hẳn Thiên Di",
  "nữ, Mệnh có Thiên Mã, Thiên Di có Lộc Tồn", "có tài buôn bán, nhiều bề giỏi giắn", "support", ["path.business"],
  notes="'Tài buôn bán nhiều bề giỏi dắn / Mã mệnh cung, Tồn hẳn Thiên Di'")
E("tt116_kinh_nu_hoa_co_cu", "TT", 116, M, "Kình Dương nữ mệnh ca", "nếu gặp Hỏa Tinh, Thiên Cơ, Cự",
  "nữ, Mệnh có Kình Dương; Hỏa Tinh, Thiên Cơ, Cự Môn trong tam phương", "đời tầm thường", "limit", ["life.blessed"],
  notes="'Kình Dương là bắc đẩu phù tinh đóng nữ mệnh nếu gặp Hỏa Tinh, Thiên Cơ, Cự Môn là hạng gái tầm thường'; the yểu clause after it is left out")
E("tt117_hoa_linh_nu_tham", "TT", 117, M, "Hỏa Linh nữ mệnh ca", "phương không bị sát xung phá số gái hạnh phúc giàu sang",
  "nữ, Mệnh có Hỏa Tinh hoặc Linh Tinh; Tham Lang đắc địa trong tam phương; tam phương không có sát tinh khác", "hạnh phúc, giàu sang", "support",
  ["life.blessed", "fin.abundance"], notes="'Hai sao Hỏa Linh đóng nữ mệnh cần hội ngộ với sao Tham Lang đắc địa tam phương không bị sát xung phá ...'")
E("tt117_hoa_quyen_nu_cat", "TT", 117, M, "Hóa Quyền nữ mệnh ca", "thêm cát tinh khác phù trợ tất phú quí song toàn",
  "nữ, Mệnh có Hóa Quyền, cát tinh trong tam phương", "phú quý song toàn", "support", ["fin.abundance", "career.status"],
  notes="the clause 'ưa đoạt quyền chồng' (about the husband) is left out",
  skip="its only condition beyond the star is 'có cát / sát tinh trong tam phương' (one of six stars in four palaces: true on most charts), so it is a one-star trait at Mệnh in practice; kept out as the other one-star traits (readable.test Barnum gate). The che_hoa entry keeps the book's turn where there is one")
E("tt117_hoa_khoa_nu", "TT", 117, M, "Hóa Khoa nữ mệnh ca", "Nữ mệnh có sao Hóa Khoa bao giờ cũng tốt, người đức độ, tính tình thanh cao",
  "nữ, Mệnh có Hóa Khoa", "đức độ, tính tình thanh cao", "support", ["values.integrity"],
  skip="a one-star trait at Mệnh that the KL / TH star rules already give; not added as a third generic line (readable.test Barnum gate: the Mệnh chapter must not drift to what every chart gets)")
E("tt117_hoa_ky_nu_hung", "TT", 117, M, "Hóa Kỵ nữ mệnh ca", "lại thêm hung tinh xung phá thì cuộc",
  "nữ, Mệnh có Hóa Kỵ, sát tinh trong tam phương", "cuộc sống cơ cực, túng thiếu", "limit", ["fin.scarcity", "life.hardship"],
  notes="'Hóa Kị dòng nữ mệnh vốn đã tầm thường, lại thêm hung tinh xung phá thì cuộc sống sẽ cơ cực bần tiện'; the rescue 'Nếu có cát tinh phù trợ sẽ giảm nhiều tai nguy' goes to che_hoa.json",
  skip="its only condition beyond the star is 'có cát / sát tinh trong tam phương' (one of six stars in four palaces: true on most charts), so it is a one-star trait at Mệnh in practice; kept out as the other one-star traits (readable.test Barnum gate). The che_hoa entry keeps the book's turn where there is one")
E("tt118_liem_nu_thanh_bach", "TT", 118, M, "Nữ mệnh cốt tủy phú", "Sao Liêm Trinh bản chất thanh bạch có thể",
  "nữ, Mệnh có Liêm Trinh không hãm (bảng Toàn Thư)", "bản chất thanh bạch", "support", ["values.integrity"],
  notes="'(Sao Liêm Trinh bản chất thanh bạch có thể tọa thủ nữ mệnh, miễn là đừng rơi vào hãm địa)'",
  skip="its only condition beyond the star is 'có cát / sát tinh trong tam phương' (one of six stars in four palaces: true on most charts), so it is a one-star trait at Mệnh in practice; kept out as the other one-star traits (readable.test Barnum gate). The che_hoa entry keeps the book's turn where there is one")
E("tt118_tu_nhat_nu_trung_thuc", "TT", 118, M, "Nữ mệnh cốt tủy phú", "tính nết trung thực",
  "nữ, Mệnh có Tử Vi hoặc Thái Dương", "tính nết trung thực", "support", ["values.integrity"],
  notes="'(Tử Vi hay Thái Dương tọa thủ nữ mệnh sớm lấy chồng hiền năng, tính nết trung thực)': the marriage clause is left out",
  skip="a one-star trait at Mệnh that the KL / TH star rules already give; not added as a third generic line (readable.test Barnum gate: the Mệnh chapter must not drift to what every chart gets)")
E("tt118_nhat_dan_ngo_cat", "TT", 118, M, "Nữ mệnh cốt tủy phú", "nữ mệnh gặp Thái Dương thế nào cũng hưởng phúc nếu thêm cát tinh",
  "nữ, Mệnh ở Dần, Mão, Thìn, Tỵ, Ngọ có Thái Dương; cát tinh trong tam phương", "hưởng phúc", "support", ["life.blessed"],
  notes="'Sao Thái Dương chỉ đắc địa từ Dần cung đến Ngọ cung nữ mệnh gặp Thái Dương thế nào cũng hưởng phúc nếu thêm cát tinh phù trợ'")
E("tt118_huu_tuong_nu", "TT", 118, M, "Nữ mệnh cốt tủy phú", "có sao Hữu Bật, Thiên Tướng phúc thường đến",
  "nữ, Mệnh có Hữu Bật và Thiên Tướng", "phúc thường đến", "support", ["life.blessed"],
  notes="the first half of the translation (Thiên Khôi, Thiên Tướng) differs from the verse (Tả Phụ, Thiên Khôi) and is not used")
E("tt118_loc_ton_nu", "TT", 118, M, "Nữ mệnh cốt tủy phú", "Lộc Tồn hậu trọng đa y thực",
  "nữ, Mệnh có Lộc Tồn", "đầy đủ cơm áo", "support", ["fin.abundance"],
  skip="a one-star trait at Mệnh that the KL / TH star rules already give; not added as a third generic line (readable.test Barnum gate: the Mệnh chapter must not drift to what every chart gets)")
E("tt118_co_cu_nu", "TT", 118, M, "Nữ mệnh cốt tủy phú", "Nữ mệnh có hai sao Cơ, Cự mặc dù đắc địa nhưng",
  "nữ, Mệnh có Thiên Cơ và Cự Môn", "dù đắc địa cuối cùng cũng dễ phá tán", "limit", ["fin.volatile"],
  notes="'không phải là đẹp vì cuối cùng tất nhiên phá đãng'")
E("tt118_xuong_khuc_nu", "TT", 118, M, "Nữ mệnh cốt tủy phú", "Văn Xương Văn Khúc phúc bất toàn",
  "nữ, Mệnh có Văn Xương hoặc Văn Khúc", "phúc không trọn", "limit", ["life.blessed"], notes="'(Xương Khúc chỉ nên vào nam mệnh bất nghi nữ mệnh)'",
  skip="a one-star trait at Mệnh that the KL / TH star rules already give; not added as a third generic line (readable.test Barnum gate: the Mệnh chapter must not drift to what every chart gets)")
E("tt118_vu_nu_co_doc", "TT", 118, M, "Nữ mệnh cốt tủy phú", "Sao Vũ Khúc là sao cô độc đối với nữ mệnh",
  "nữ, Mệnh có Vũ Khúc", "là sao cô độc", "limit", ["social.isolated"],
  skip="a one-star trait at Mệnh that the KL / TH star rules already give; not added as a third generic line (readable.test Barnum gate: the Mệnh chapter must not drift to what every chart gets)")
E("tt118_sat_nu_don", "TT", 118, M, "Nữ mệnh cốt tủy phú", "Nữ mệnh Thất Sát đơn thủ không phải là phúc",
  "nữ, Mệnh có Thất Sát đơn thủ", "không phải là phúc", "limit", ["life.blessed"])
E("tt118_song_loc_nu", "TT", 118, M, "Nữ mệnh cốt tủy phú", "Số đàn bà song lộc thủ chiếu mệnh giàu sang chức tước",
  "nữ, Lộc Tồn và Hóa Lộc trong tam phương Mệnh", "giàu sang, có chức tước", "support", ["fin.abundance", "career.status"],
  skip="its only condition beyond the star is 'có cát / sát tinh trong tam phương' (one of six stars in four palaces: true on most charts), so it is a one-star trait at Mệnh in practice; kept out as the other one-star traits (readable.test Barnum gate). The che_hoa entry keeps the book's turn where there is one")
E("tt118_pha_nu_don", "TT", 118, M, "Nữ mệnh cốt tủy phú", "Sao Phá Quân đơn thủ nữ mệnh tính cô độc đa", "", "", "limit", [], skip="sexual reputation")
E("tt118_tham_nu", "TT", 118, M, "Nữ mệnh cốt tủy phú", "Nữ mệnh Tham Lang đơn thủ rất dâm dật", "", "", "limit", [], skip="sexual reputation")
E("tt118_nu_tam_phuong_sat", "TT", 118, M, "Nữ mệnh cốt tủy phú", "Nữ mệnh sợ sát tọa thủ, sát xung chiếu", "", "", "limit", [], skip="ly khắc (marriage)")
E("tt119_nu_phu_nom", "TT", 119, M, "Phú nôm nữ mệnh", "Hình Diệu số gái long đong", "", "", "limit", [], skip="the page's lines are about remarriage, chastity and seduction")
E("tt120_phu_cung", "TT", 120, "Phu Thê", "Phú nôm cung Phu", "Song Lộc hội Phu Thê cung", "Phu Thê có Lộc Tồn và Hóa Lộc", "vợ chồng giàu sang", "support", [],
  skip="the Phu Thê lines of pp.119-120 are marriage events and the spouse's looks; 'Song Lộc' is kept out with them (no spouse-wealth concept in the KG yet)")
