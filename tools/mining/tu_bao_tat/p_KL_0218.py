page("KL", 218, "Palace chapter: '6. Cung Tử' and '7. Cung Tật'. Text layer scrambled (line fragments reordered, bullet starts cut off); every line read on the image.")

# ---- 6. Cung Tử ----
E("kl218_tu_chinh_tinh_dac_dia", "KL", 218, "Tử Tức", "6. Cung Tử",
  "* Cung Tử tức dễ có con đều cần có chính tinh đắc địa như: Tử Phủ Vũ Tướng, Cơ Nguyệt Đồng Lương.",
  "Cung Tử tức dễ có con đều cần có chính tinh đắc địa n",
  "cung Tử Tức có chính tinh đắc địa, ví dụ Tử Vi, Thiên Phủ, Vũ Khúc, Thiên Tướng, Thiên Cơ, Thái Âm, Thiên Đồng, Thiên Lương",
  C(own_major=["Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng", "Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"],
    other="any one of the listed chính tinh in Tử Tức, and it must be đắc địa (book: 'chính tinh đắc địa như ...'); the list is given as examples ('như')"),
  "Tử Tức có chính tinh đắc địa (như Tử Phủ Vũ Tướng, Cơ Nguyệt Đồng Lương) thì dễ có con", "support", ["NEW:kin.easy_children"],
  notes="Confirms the draft rule's open question: the book DOES require đắc địa ('chính tinh đắc địa như'). 'như' = examples, so the list may not be closed.",
  dup="TV_KL_CUNG_TU_TUC_CHINH_TINH_DAC")

E("kl218_tu_phu_tinh_de_con", "KL", 218, "Tử Tức", "6. Cung Tử",
  "* Các phụ tinh như: Thai, Mộc, Dưỡng, Long trì, Phượng các, Tràng sinh, Đế vượng, Thiên đức, Nguyệt đức, Phúc đức, Long đức, Quan, Phúc, Tả, Hữu, Thanh long, Thiên hỷ, Hỷ thần đều là những sao nói lên dễ sinh con, con cái khá giả, xinh đẹp.",
  "những sao nói lên dễ sinh con, con cái khá giả, xinh đẹp",
  "Tử Tức có một trong các phụ tinh: Thai, Mộc Dục, Dưỡng, Long Trì, Phượng Các, Tràng Sinh, Đế Vượng, Thiên Đức, Nguyệt Đức, Phúc Đức, Long Đức, Thiên Quan, Thiên Phúc, Tả Phù, Hữu Bật, Thanh Long, Thiên Hỷ, Hỷ Thần",
  C(own_stars=["Thai", "Mộc Dục", "Dưỡng", "Long Trì", "Phượng Các", "Tràng Sinh", "Đế Vượng", "Thiên Đức", "Nguyệt Đức",
               "Phúc Đức", "Long Đức", "Thiên Quan", "Thiên Phúc", "Tả Phù", "Hữu Bật", "Thanh Long", "Thiên Hỷ", "Hỷ Thần"],
    other="any one of the listed stars in Tử Tức; 'Mộc' read as Mộc Dục, 'Quan, Phúc' as Thiên Quan, Thiên Phúc (quý nhân pair) — reader's reading"),
  "các phụ tinh này ở Tử Tức chỉ việc dễ sinh con, con cái khá giả", "support", ["NEW:kin.easy_children", "NEW:kin.prosper"],
  notes="Existing rule's star list is shorter (omits Mộc, Long Trì, Phượng Các, Thiên/Nguyệt/Phúc/Long Đức, Quan, Phúc). 'xinh đẹp' is appearance: do not render.",
  dup="TV_KL_CUNG_TU_TUC_PHU_TINH")

E("kl218_tu_hiem_con_sat_pha_tham", "KL", 218, "Tử Tức", "6. Cung Tử",
  "* Hiếm con có thể rơi vào các sao trong bộ Sát, Phá, Tham, Vũ khúc, Lộc tồn.",
  "Hiếm con có thể rơi vào các sao trong bộ Sát, Phá, Tham, Vũ khúc, Lộc tồn",
  "Tử Tức có một trong các sao Thất Sát, Phá Quân, Tham Lang, Vũ Khúc, Lộc Tồn",
  C(own_stars=["Thất Sát", "Phá Quân", "Tham Lang", "Vũ Khúc", "Lộc Tồn"],
    other="any one of the listed stars in Tử Tức; book hedges: 'có thể' (may)"),
  "Tử Tức có Sát, Phá, Tham, Vũ Khúc hoặc Lộc Tồn thì có thể hiếm con", "limit", ["kin.few"], timing=True,
  notes="Count-type statement (number of children), marked timing per brief; book hedges with 'có thể'.")

E("kl218_tu_khong_con", "KL", 218, "Tử Tức", "6. Cung Tử",
  "* Không có con có thể là lũ: Hình, Kỵ, Đẩu, Kiếp, Cô, Quả, Hỏa, Linh, Tuần, Triệt.",
  "n có thể là lũ: Hình, Kỵ, Đẩu, Kiếp, Cô, Quả, Hỏa, Linh, Tuần, Triệt",
  "Tử Tức có Thiên Hình, Hóa Kỵ, Đẩu Quân, Địa Kiếp, Cô Thần, Quả Tú, Hỏa Tinh, Linh Tinh, Tuần, Triệt",
  C(own_stars=["Thiên Hình", "Hóa Kỵ", "Đẩu Quân", "Địa Kiếp", "Cô Thần", "Quả Tú", "Hỏa Tinh", "Linh Tinh"],
    tt="Tuần or Triệt", other="'lũ' = the group; book hedges 'có thể'"),
  "Tử Tức có Hình, Kỵ, Đẩu, Kiếp, Cô, Quả, Hỏa, Linh, Tuần, Triệt thì có thể không có con", "limit", ["kin.few"], timing=True,
  skip="predicts childlessness: fatalistic like 'khắc con'; recorded for reference only",
  notes="If the caller wants a softer use, only 'kin.few' as a palace characteristic would be faithful-ish; left skipped.")

N("kl218_tu_nghia", "palace_relation", "", "Tử Tức", "KL", 218, "Cung Tử nói về con cái",
  "Cung Tử nói về con cái.", "cung Tử Tức nói về con cái", ["children"], "±", [])
N("kl218_tu_soi_day", "palace_relation", "", "Tử Tức", "KL", 218, "Con cái là sợi dây nối liền quá khứ với tương la",
  "Con cái là sợi dây nối liền quá khứ với tương lai của đương số.",
  "con cái là sợi dây nối quá khứ với tương lai của đương số", ["children"], "±", [])
N("kl218_tu_ve_gia", "palace_relation", "", "Tử Tức", "KL", 218, "Cung tử tức cũng là hình ảnh đời mình về già",
  "Cung tử tức cũng là hình ảnh đời mình về già.", "cung Tử Tức cũng là hình ảnh đời mình lúc về già",
  ["children", "fortune"], "±", ["NEW:kin.prosper", "NEW:kin.easy_children"],
  notes="Tử Tức = tuổi già statement asked for in the assignment.")
N("kl218_tu_khong_doan_trai_gai", "palace_relation", "", "Tử Tức", "KL", 218,
  "Quan niệm trọng nam khinh nữ, thích trai chê gái đã quá lỗi thời, chẳng nên tìm kiếm ở cung Tử",
  "* Quan niệm trọng nam khinh nữ, thích trai chê gái đã quá lỗi thời, chẳng nên tìm kiếm ở cung Tử tức nữa, mà nhiều khi xác xuất về trai gái cũng chẳng đáng tin.",
  "không nên tìm đoán con trai hay con gái ở cung Tử Tức, xác suất trai gái ở đây nhiều khi không đáng tin",
  ["children"], "±", [],
  notes="Guard: KL itself says the Tử Tức palace is unreliable for son/daughter; relevant to TH p.103/104 rules TV_TH_P2_TU_TUC_DONG_AM, _NHAT_DUONG, _AM_AM.")

# ---- 7. Cung Tật ----
N("kl218_tat_tho_au_ve_gia", "palace_relation", "", "Tật Ách", "KL", 218,
  "Cung Tật ách cũng thật đặc biệt, Đây là hình ảnh của thuở thơ ấu đầu đời",
  "Cung Tật ách cũng thật đặc biệt, Đây là hình ảnh của thuở thơ ấu đầu đời và cũng là hình ảnh đám tang lúc về già.",
  "cung Tật Ách là hình ảnh thuở thơ ấu đầu đời và cũng là hình ảnh lúc cuối đời", ["health", "fortune"], "±", [],
  notes="Book's own words for the second half are 'đám tang lúc về già' (funeral); paraphrased as 'lúc cuối đời', do not render the funeral image.")
N("kl218_tat_dep", "palace_relation", "", "Tật Ách", "KL", 218,
  "Cung Tật có đẹp thì tuổi thơ sung sướng, tuổi già an nhàn sung túc",
  "Cung Tật có đẹp thì tuổi thơ sung sướng, tuổi già an nhàn sung túc.",
  "cung Tật Ách đẹp thì tuổi thơ sung sướng, tuổi già an nhàn sung túc", ["health", "fortune"], "+", ["well.longevity"])
N("kl218_tat_can_cho_ve_gia", "palace_relation", "", "Tật Ách", "KL", 218,
  "cung Tài, cung Quan đẹp chưa đủ, phải có cung Tật",
  "Một cung Mệnh đẹp, một cung Thân đẹp, cung Tài, cung Quan đẹp chưa đủ, phải có cung Tật đẹp thì mới hưởng phúc lúc về già, nếu không thì có thể tuổi trung niên giầu sang, về già chết có bó chiếu.",
  "Mệnh, Thân, Tài Bạch, Quan Lộc đẹp vẫn chưa đủ, phải có cung Tật Ách đẹp mới hưởng phúc lúc về già; nếu không thì có thể trung niên giàu sang mà về già sa sút",
  ["health", "fortune", "money", "career"], "±", [],
  notes="Relation Tật Ách ↔ Mệnh/Thân/Tài/Quan for old age. Last clause literally 'về già chết có bó chiếu' (dies wrapped in a mat = destitute): death imagery, paraphrased as 'sa sút'; do not render literally.")
E("kl218_tat_cuoi_doi_sao_tot", "KL", 218, "Tật Ách", "7. Cung Tật",
  "Cung Tật cần có Tử Phủ Vũ Tướng, hoặc Sát Phá Tham, Tả Hữu, Khoa Quyền Lộc, Khôi Việt, những sao này là hình ảnh một đám tang to lớn, có nghĩa là giầu sang vào lúc cuối đời.",
  "những sao này là hình ảnh một đám tang to lớn, có nghĩa là giầu sang vào lúc cuối đời",
  "Tật Ách có Tử Phủ Vũ Tướng, hoặc Sát Phá Tham, Tả Hữu, Khoa Quyền Lộc, Khôi Việt",
  C(own_stars=["Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng", "Thất Sát", "Phá Quân", "Tham Lang", "Tả Phù", "Hữu Bật",
               "Hóa Khoa", "Hóa Quyền", "Hóa Lộc", "Thiên Khôi", "Thiên Việt"],
    other="'cần có' — any of the listed groups in Tật Ách; no brightness stated"),
  "Tật Ách có Tử Phủ Vũ Tướng, Sát Phá Tham, Tả Hữu, Khoa Quyền Lộc, Khôi Việt thì giàu sang lúc cuối đời", "support",
  ["well.longevity", "NEW:fortune.late_ease"],
  notes="Existing rule's reading omits 'Sát Phá Tham' which IS in the book's list; the book then calls Tham Lang 'tối kỵ' for Tật two lines later (internal tension — the existing rule resolves it by excluding Tham Lang). Book's image is 'a big funeral': paraphrase as late-life prosperity only.",
  dup="TV_KL_CUNG_TAT_ACH_CUOI_DOI")
E("kl218_tat_pha_sat_doc_tri_doc", "KL", 218, "Tật Ách", "7. Cung Tật",
  "Tốt: nếu có những sao: Phá quân, Phá toái, Thất sát sẽ phá hết hạn xấu, là cách dĩ độc trị độc.",
  "Tốt: nếu có những sao: Phá quân, Phá toái, Thất sát sẽ phá hết hạn xấu",
  "Tật Ách có Phá Quân, Phá Toái hoặc Thất Sát",
  C(own_stars=["Phá Quân", "Phá Toái", "Thất Sát"], other="any one of the three in Tật Ách ('nếu có')"),
  "Tật Ách có Phá Quân, Phá Toái, Thất Sát là tốt: phá hết hạn xấu, lấy độc trị độc", "support",
  ["life.mitigated", "NEW:health.shielded"])
E("kl218_tat_thien_khong", "KL", 218, "Tật Ách", "7. Cung Tật",
  "Thiên không thì lại cứu giải bất ngờ.", "Thiên không thì lại cứu giải bất ngờ",
  "Tật Ách có Thiên Không", C(own_stars=["Thiên Không"]),
  "Thiên Không ở Tật Ách lại cứu giải bất ngờ", "support", ["life.mitigated", "NEW:health.shielded"],
  notes="Indented under the 'Tốt:' line, so it belongs to the good (cứu giải) list for Cung Tật.")
E("kl218_tat_song_hao", "KL", 218, "Tật Ách", "7. Cung Tật",
  "Song Hao giải trừ nạn xấu.", "Hao giải trừ nạn xấu",
  "Tật Ách có Song Hao (Đại Hao, Tiểu Hao)", C(own_stars=["Đại Hao", "Tiểu Hao"], other="'Song Hao' = the pair; whether one Hao suffices is not stated"),
  "Song Hao ở Tật Ách giải trừ nạn xấu", "support", ["life.mitigated", "NEW:health.shielded"],
  notes="Text layer splits 'Song' from 'Hao giải trừ nạn xấu'; image shows 'Song Hao giải trừ nạn xấu.'")
E("kl218_tat_triet", "KL", 218, "Tật Ách", "7. Cung Tật",
  "Triệt thì cản phá hung tai.", "Triệt thì cản phá hung tai",
  "Tật Ách có Triệt", C(tt="Triệt"),
  "Triệt ở Tật Ách cản phá hung tai", "support", ["life.mitigated", "NEW:health.shielded"],
  notes="Only Triệt is named here (not Tuần). Close to TL rule TV_TL_TAT_ACH_GIAM (Tuần, Triệt or vô chính diệu reduce tật ách) but a different book/page.")
E("kl218_tat_toi_ky", "KL", 218, "Tật Ách", "7. Cung Tật",
  "Tối kỵ cho cung Tật khi có Tham lang, Hóa kỵ, Không Kiếp dự vào.",
  "Tối kỵ cho cung Tật khi có Tham lang, Hóa kỵ, Không Kiếp dự vào",
  "Tật Ách có Tham Lang, Hóa Kỵ, Địa Không, Địa Kiếp 'dự vào'",
  C(with_any=["Tham Lang", "Hóa Kỵ", "Địa Không", "Địa Kiếp"],
    other="'dự vào' (take part in) — book does not say tọa thủ vs hội; any one of them"),
  "Tật Ách có Tham Lang, Hóa Kỵ, Không Kiếp dự vào là điều tối kỵ", "limit", ["NEW:health.exposed"],
  notes="Used as the 'không có' clause of existing rule TV_KL_CUNG_TAT_ACH_CUOI_DOI, but not yet a rule of its own.")
