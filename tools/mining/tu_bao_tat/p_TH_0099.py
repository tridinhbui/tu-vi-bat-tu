page("TH", 99, "Verse; 'CUNG BÀO' heading starts at the bottom of p.99 and runs to p.101 (before 'CUNG PHỐI'). TEXT LAYER SCRAMBLED (right-hand halves of lines cut and moved to the top of the page). Existing verified rules TV_TH_P2_HUYNH_DE_TT ('Triệt Tuần xung củng, đấu đàng ly tông'), _KHONG_KIEP ('Hễ là Địa Kiếp Thiên Không chẳng nhiều') and _TUONG_LOC_MA ('Tướng quân Lộc Mã đồng cung / Anh em có kẻ triều trung qui quyền') are on the image under CUNG BÀO.")
page("TH", 100, "Cung Bào verse continues for the whole page. Text layer scrambled (line ends cut). Existing verified rules _TS_DV ('Trường sinh Đế vượng đa nhân') and _LOC_MA ('Lộc Mã buôn bán nên giàu') confirmed on the image. Draft checks: see entries th100_bao_pha_hinh_ky and th100_bao_that_sat_loc_ton_co_qua.")
page("TH", 101, "Cung Bào verse ends after 'Đẩu quân Kỵ Huynh đệ cùng / Cát hội hoà thuận, còn hưng vẫn thù'; then CUNG PHỐI. Draft check: th101_bao_khoi_viet_tam_hoa.")

# ---- draft checks ----
E("th100_bao_pha_hinh_ky", "TH", 100, "Huynh Đệ", "CUNG BÀO (verse)",
  "Phá phùng Hình Kỵ đồng xung / Anh em bất thuận những đường trở tranh",
  "Anh em bất thuận những đường trở tranh",
  "Huynh Đệ có Phá Quân gặp Thiên Hình, Hóa Kỵ ('đồng xung')",
  C(own_major=["Phá Quân"], with_any=[], other="Phá Quân meets BOTH Thiên Hình and Hóa Kỵ ('phùng Hình Kỵ'); 'đồng xung' = together, in the palace or opposite (đồng cung hay xung chiếu) — reader's reading"),
  "Huynh Đệ có Phá Quân gặp Hình, Kỵ thì anh em bất thuận, hay tranh chấp", "limit", ["kin.strain"],
  dup="TV_TH_P2_HUYNH_DE_PHA_KY",
  notes="DRAFT CHECK: line IS on TH p.100 under CUNG BÀO. The book's condition is Phá + Hình + Kỵ (Hình is part of the condition, not an extra); the draft reading 'Phá Quân, Hóa Kỵ; sách còn kể Thiên Hình' under-specifies it. Separate one-star lines exist two couplets earlier: 'Gặp sao Hóa Kỵ khiếm hoà' and 'Thiên Hình xung khắc trong nhà ghét nhau' (entries th100_bao_hoa_ky, th100_bao_thien_hinh).")
E("th100_bao_that_sat_loc_ton_co_qua", "TH", 100, "Huynh Đệ", "CUNG BÀO (verse)",
  "Thìn Tuất Thất Sát một mình / Lộc Tồn Cô quả, anh em có nào",
  "Lộc Tồn Cô quả, anh em có nào",
  "Huynh Đệ: Thất Sát một mình ở Thìn/Tuất; Lộc Tồn, Cô Thần/Quả Tú",
  C(other="couplet: 'Thìn Tuất Thất Sát một mình' (Thất Sát độc thủ at Thìn/Tuất) + 'Lộc Tồn Cô quả'; unclear whether these are alternatives or one combined condition"),
  "Huynh Đệ có Thất Sát độc thủ ở Thìn Tuất, (cùng) Lộc Tồn, Cô Quả thì hầu như không có anh em", "limit", ["kin.few"], timing=True,
  dup="TV_TH_P2_HUYNH_DE_LOC_TON_IT",
  notes="DRAFT CHECK: line IS on TH p.100 under CUNG BÀO, but the draft condition 'Lộc Tồn' alone is a WIDENING: the couplet also names Thất Sát một mình at Thìn/Tuất and Cô Quả. 'anh em có nào' = (hầu như) chẳng có anh em — stronger than 'ít'. Recommend: keep draft only if condition = Lộc Tồn + Cô/Quả (and possibly Thất Sát Thìn/Tuất), or drop.")
E("th101_bao_khoi_viet_tam_hoa", "TH", 101, "Huynh Đệ", "CUNG BÀO (verse, last lines before CUNG PHỐI)",
  "Khôi Việt Tam Hóa được ngôi anh hung", "Khôi Việt Tam Hóa được ngôi anh h",
  "Huynh Đệ có Khôi, Việt, Tam Hóa (Khoa, Quyền, Lộc)",
  C(own_stars=["Thiên Khôi", "Thiên Việt", "Hóa Khoa", "Hóa Quyền", "Hóa Lộc"], other="verse gives no đồng cung/hội; 'anh hung' on the page (likely 'anh hùng' = a sibling of high standing)"),
  "Huynh Đệ có Khôi Việt, Tam Hóa thì anh em có người được ngôi cao", "support", ["NEW:kin.talented", "NEW:kin.prosper"],
  dup="TV_TH_P2_HUYNH_DE_KHOI_VIET_HOA",
  notes="DRAFT CHECK: line IS on TH p.101 under CUNG BÀO (CUNG BÀO continues from p.99 to here). Wording on the page is 'anh hung' (sic). The verse does not say 'hội': the draft's 'đọc là hội' is a system reading.")

# ---- other Cung Bào lines (new) ----
E("th99_bao_tuong_loc_ma_trieu", "TH", 99, "Huynh Đệ", "CUNG BÀO (verse)",
  "Tướng quân Lộc Mã cung triều. / Anh em có kẻ thuận chiều danh công",
  "Anh em có kẻ thuận chi",
  "Huynh Đệ được Tướng Quân, Lộc Tồn (Lộc), Thiên Mã chiếu ('cung triều')",
  C(tam=["Tướng Quân", "Lộc Tồn", "Thiên Mã"], other="'cung triều' = chiếu về (tam phương/xung chiếu), contrasted with the next couplet 'đồng cung'; 'Lộc' may be Lộc Tồn or Hóa Lộc"),
  "Huynh Đệ được Tướng Quân, Lộc, Mã chiếu thì anh em có người thuận đường công danh", "support", ["NEW:kin.talented"],
  notes="Companion of the đồng-cung couplet already in rule TV_TH_P2_HUYNH_DE_TUONG_LOC_MA (stronger: 'triều trung qui quyền').")
E("th100_bao_thai_nhat_nguyet", "TH", 100, "Huynh Đệ", "CUNG BÀO (verse)",
  "Thai giữ Nhật Nguyệt có lần song sinh", "Thai giữ Nhật Nguyệt có lần song sinh",
  "Huynh Đệ có sao Thai cùng Nhật, Nguyệt", C(own_stars=["Thai"], with_any=["Thái Dương", "Thái Âm"], other="'Thai giữ Nhật Nguyệt' — Thai with Nhật and Nguyệt; placement not stated"),
  "Huynh Đệ có Thai với Nhật Nguyệt thì anh em có lần sinh đôi", "neutral", ["NEW:kin.twins"], timing=True,
  notes="Agrees with KL p.99 'Nhật, Nguyệt giáp thai có anh em song sinh' (kl99_bao_nhat_nguyet_giap_thai).")
E("th100_bao_tang_ma", "TH", 100, "Huynh Đệ", "CUNG BÀO (verse)",
  "Tang môn ngộ Mã đinh ninh / Mỗi người mỗi xứ gia đình quạnh hiu", "Mõi người mỗi xứ gia đình quạnh hi",
  "Huynh Đệ có Tang Môn gặp Thiên Mã", C(own_stars=["Tang Môn"], with_any=["Thiên Mã"]),
  "Huynh Đệ có Tang Môn gặp Thiên Mã thì anh em mỗi người một xứ, gia đình quạnh hiu", "limit", ["kin.apart"])
E("th100_bao_hoa_ky", "TH", 100, "Huynh Đệ", "CUNG BÀO (verse)",
  "Gặp sao Hóa Kỵ khiếm hoà", "Gặp sao Hóa Kỵ khiếm hoà",
  "Huynh Đệ gặp Hóa Kỵ", C(with_any=["Hóa Kỵ"], other="'gặp' — not said đồng cung"),
  "Huynh Đệ gặp Hóa Kỵ thì anh em kém hòa thuận", "limit", ["kin.strain"],
  notes="Agrees with KL p.156 'Hóa kỵ … Bào: Anh em xung khắc' (kl156_bao_hoa_ky).")
E("th100_bao_thien_hinh", "TH", 100, "Huynh Đệ", "CUNG BÀO (verse)",
  "Thiên Hình xung khắc trong nhà ghét nhau", "Thiên Hình xung khắc trong nhà ghét nha",
  "Huynh Đệ có Thiên Hình", C(own_stars=["Thiên Hình"], other="the verse names only Thiên Hình"),
  "Huynh Đệ có Thiên Hình thì anh em xung khắc, trong nhà ghét nhau", "limit", ["kin.strain"],
  notes="'xung khắc' = clash, not the fatal 'khắc'.")
E("th100_bao_duong_thai_triet_vuong", "TH", 100, "Huynh Đệ", "CUNG BÀO (verse)",
  "Dương Thai Triệt Vượng thấu vào / Trong anh em có dị bào chẳng không", "Trong anh em có dị bào chẳng không",
  "Huynh Đệ có Kình Dương, Thai, Triệt, Đế Vượng", C(own_stars=["Kình Dương", "Thai", "Đế Vượng"], tt="Triệt", other="'Dương' read as Kình Dương; 'thấu vào' = all present"),
  "Huynh Đệ có Dương, Thai, Triệt, Vượng thì trong anh em có người khác cha hoặc khác mẹ", "neutral", ["NEW:kin.half"], timing=True,
  notes="Family-composition claim; see also KL p.80 Cự Cơ dị bào.")
E("th100_bao_am_phuc_di_bao", "TH", 100, "Huynh Đệ", "CUNG BÀO (verse)",
  "Âm dương chiếu với Hỉ tinh / Âm cùng Thiên Phúc cũng sinh dị bào (Thái âm và Thiên phúc)",
  "cùng Thiên Phúc cũng sinh dị",
  "Huynh Đệ: Nhật Nguyệt chiếu cùng Hỉ (Thiên Hỷ/Hỉ Thần); hoặc Thái Âm cùng Thiên Phúc",
  C(other="couplet: (Âm Dương chiếu + Hỉ tinh) and/or (Thái Âm + Thiên Phúc, gloss in parentheses on the page)"),
  "Huynh Đệ có Âm Dương chiếu với Hỉ, hoặc Thái Âm cùng Thiên Phúc, thì có anh em khác cha/mẹ", "neutral", ["NEW:kin.half"], timing=True)
E("th100_bao_tuong_thai_vuong_di_bao", "TH", 100, "Huynh Đệ", "CUNG BÀO (verse)",
  "Tương Thai, Đế vượng hợp cùng / Dị bào có kẻ trong vòng Đệ huynh", "Dị bào có kẻ trong vòng Đệ huynh",
  "Huynh Đệ có Tướng (Tướng Quân hoặc Thiên Tướng), Thai, Đế Vượng", C(own_stars=["Thai", "Đế Vượng"], with_any=["Tướng Quân", "Thiên Tướng"], other="'Tương' (sic) = Tướng"),
  "Huynh Đệ có Tướng, Thai, Đế Vượng thì trong anh em có người khác cha hoặc khác mẹ", "neutral", ["NEW:kin.half"], timing=True)
E("th100_bao_xuong_khuc_thai_tue", "TH", 100, "Huynh Đệ", "CUNG BÀO (verse)",
  "Khúc Xương, Thai Tuế cung Bào / Có người anh trưởng thấp cao tung hoành", "Có người anh trưởng thấp cao tung hoa",
  "Huynh Đệ có Văn Khúc, Văn Xương, Thai, Thái Tuế", C(own_stars=["Văn Khúc", "Văn Xương", "Thai", "Thái Tuế"]),
  "Huynh Đệ có Xương Khúc, Thai, Thái Tuế thì có người anh cả tung hoành", "support", ["NEW:kin.talented"],
  notes="'thấp cao tung hoành' = active at every level; refers to the eldest brother.")
E("th100_bao_tuong_phuc_y_cong", "TH", 100, "Huynh Đệ", "CUNG BÀO (verse)",
  "Lộc Mã buôn bán nên giàu / Nhược bằng Tướng phục là màu Y công", "Tướng phục là màu Y c",
  "Huynh Đệ có Tướng (Quân) và Phục Binh", C(with_any=["Tướng Quân", "Phục Binh"], other="'Tướng phục' = Tướng Quân + Phục Binh (reader's reading)"),
  "Huynh Đệ có Tướng, Phục thì anh em làm nghề y hoặc thợ ('y công')", "neutral", ["NEW:kin.trade"],
  notes="Meaning of 'màu Y công' uncertain (y = medicine, công = craft/work).")
E("th101_bao_duong_da", "TH", 101, "Huynh Đệ", "CUNG BÀO (verse)",
  "Dươnng Đà xung khắc chẳng sai", "Dươnng Đà xung khắc chẳng sai",
  "Huynh Đệ có Kình Dương, Đà La", C(own_stars=["Kình Dương", "Đà La"], other="'Dương Đà' — either or both (book unclear)"),
  "Huynh Đệ có Kình Dương, Đà La thì anh em xung khắc", "limit", ["kin.strain"],
  notes="Page misprint 'Dươnng'. 'xung khắc' = clash.")
E("th101_bao_dau_quan_ky", "TH", 101, "Huynh Đệ", "CUNG BÀO (verse)",
  "Đẩu quân Kỵ Huynh đệ cùng / Cát hội hoà thuận, còn hưng vẫn thù", "Cát hội hoà thuận, còn hưng vẫn",
  "Huynh Đệ có Đẩu Quân và Hóa Kỵ; có cát tinh hội thì hòa thuận, (có hung tinh) thì vẫn thù",
  C(own_stars=["Đẩu Quân", "Hóa Kỵ"], other="split: with cát tinh hội → hòa thuận; otherwise ('còn hưng' read as 'còn hung' = with hung tinh) → vẫn thù"),
  "Huynh Đệ có Đẩu Quân, Hóa Kỵ: gặp cát tinh thì anh em hòa thuận, gặp hung tinh thì vẫn thù hằn", "neutral", ["kin.strain", "kin.harmony"],
  notes="'hưng' on the page is read as 'hung' (bad stars) by context.")
E("th100_bao_tu_tang_ta_huu", "TH", 100, "Huynh Đệ", "CUNG BÀO (verse)",
  "Tử Tang Tả Hữu cùng ngôi / Có chị em gái duyên ôi chẳng lành", "Có chị em gái duyên ôi chẳng lành",
  "Huynh Đệ có sao Tử (vòng Trường sinh), Tang Môn, Tả Phù, Hữu Bật", C(own_stars=["Tử", "Tang Môn", "Tả Phù", "Hữu Bật"]),
  "Huynh Đệ có Tử, Tang, Tả Hữu thì có chị em gái duyên phận không lành", "limit", ["kin.strain"],
  notes="About a sister's marriage luck; not sexual conduct.")
E("th100_bao_tam_khong_duong", "TH", 100, "Huynh Đệ", "CUNG BÀO (verse)",
  "Tam Không ngộ Dương đinh ninh / Nuôi con nghĩa tử giúp mình yên vui", "Nuôi con nghĩa tử giúp minh yên vui",
  "Huynh Đệ có Tam Không gặp Kình Dương", C(with_any=["Kình Dương"], other="'Tam Không' (Địa Không, Thiên Không, Tuần Không) + Dương"),
  "Huynh Đệ có Tam Không gặp Kình Dương thì (có) nuôi nghĩa tử, được yên vui", "neutral", ["NEW:kin.adopted"], timing=True,
  notes="Meaning in a Huynh Đệ context is unclear (adopted sibling? adopted child?).")
# skipped Cung Bào lines
E("th100_bao_gian_dao", "TH", 100, "Huynh Đệ", "CUNG BÀO (verse, couplet spans p.99→p.100)",
  "Triệt Tuần Không Kiếp giao liên / Có người gian đạo để phiền luỵ thân", "Có người gian đạo để phiền luỵ thân",
  "Huynh Đệ có Triệt, Tuần, Không, Kiếp", C(own_stars=["Địa Không", "Địa Kiếp"], tt="Tuần and Triệt"),
  "(anh em có người gian đạo làm phiền lụy)", "limit", ["kin.burden"], skip="theft/dishonesty ('gian đạo')")
E("th100_bao_chi_em_theo_trai", "TH", 100, "Huynh Đệ", "CUNG BÀO (verse)",
  "Đào hoa, Thai Hỉ trong cung, / Phá quản, Tương, Phục chiếm xung ở ngoài / Có chị em gái theo trai / Say mê đến nõi hoang thai bỏ mình",
  "Có chị em gái theo trai", "Huynh Đệ có Đào Hoa, Thai, Hỉ; Phá Quân, Tướng, Phục xung chiếu", C(own_stars=["Đào Hoa", "Thai"]),
  "(chuyện tình dục)", "limit", [], skip="sexual reputation + death")
E("th100_bao_tu_thong", "TH", 100, "Huynh Đệ", "CUNG BÀO (verse)",
  "Trong thời Tướng Phổ, Phục binh, / Ngoài thì Hoa Cái liên minh Đào Hồng / Bần cung đối chiếu tinh tườn / Anh em có kẻ tư thông hẳn là",
  "Anh em có kẻ tư thông hẳn là", "Huynh Đệ có Tướng, Phục Binh; Hoa Cái, Đào Hồng chiếu", C(),
  "(chuyện tình dục)", "limit", [], skip="sexual reputation")
E("th100_bao_phan_son", "TH", 100, "Huynh Đệ", "CUNG BÀO (verse)",
  "Tử vi Tả Hữu lâm vào / Có chị em gái say màu phấn son (làm dáng)", "Có chị em gái say màu phấn son",
  "Huynh Đệ có Tử Vi, Tả Hữu", C(own_major=["Tử Vi"], own_stars=["Tả Phù", "Hữu Bật"]),
  "(chị em gái thích làm dáng)", "neutral", [], skip="appearance / vanity")
E("th100_bao_tu_phu_thin", "TH", 100, "Huynh Đệ", "CUNG BÀO (verse)",
  "Bào cung Tử Phú ở Thìn / Họ hàng có kẻ tìm phương lộn chồng", "Họ hàng có kẻ tìm phương lộn chồng",
  "Huynh Đệ có Tử Phủ (?) ở Thìn", C(branch=["Thìn"]),
  "(chuyện ngoại tình trong họ hàng)", "limit", [], skip="sexual reputation; also 'Tử Phú ở Thìn' is not a possible Tử Phủ placement")
# count lines (timing)
E("th100_bao_khoi_viet_counts", "TH", 100, "Huynh Đệ", "CUNG BÀO (verse)",
  "Thiên Khôi có kẻ đàn anh / Thiên Việt ba kẻ lại dành đàn em", "Thiên Việt ba kẻ lại dành đàn em",
  "Huynh Đệ có Thiên Khôi / Thiên Việt", C(with_any=["Thiên Khôi", "Thiên Việt"]),
  "Khôi ở Huynh Đệ thì có anh; Việt thì có (ba) em", "neutral", ["kin.many"], timing=True,
  notes="Birth-order / count verse.")
E("th100_bao_counts_chinh_tinh", "TH", 100, "Huynh Đệ", "CUNG BÀO (verse)",
  "Tử vi răm kẻ trọn miền. / Đồng Lương trai gái kết liền được ba / Thái Dương trai hợp một nhà / Âm Đồng Tướng Toạ sinh ra năm chàng",
  "Đồng Lương trai gái kết liền được b",
  "Huynh Đệ có Tử Vi / Đồng Lương / Thái Dương / Âm Đồng (Tướng, Tọa)", C(other="one count per star group"),
  "số anh em theo chính tinh ở Huynh Đệ (Tử Vi 'răm' kẻ, Đồng Lương ba, Âm Đồng năm …)", "neutral", ["kin.many"], timing=True,
  notes="Count verse; 'răm' unclear (năm? rằm?). Continues on p.101 ('Sát Liêm ngộ Cát … 3 chàng', 'Khúc Xương Tả Hữu năm lân', 'Linh Hỏa … được hai'). Palace-characteristic use only, if at all.")
E("th101_bao_counts", "TH", 101, "Huynh Đệ", "CUNG BÀO (verse)",
  "Sát Liêm ngộ Cát kể tường / Ắt là cùn được 3 chàng nên thân / Khúc Xương Tả Hữu năm lân / Kìa ngoài Linh Hỏa vương thần được hai",
  "Sát Liêm ngộ Cát kể tường",
  "Huynh Đệ có Sát Liêm gặp cát tinh / Xương Khúc Tả Hữu / Linh Hỏa", C(other="one count per star group"),
  "số anh em: Sát Liêm gặp cát còn được ba người nên thân; Xương Khúc Tả Hữu năm; Linh Hỏa hai", "neutral", ["kin.many"], timing=True,
  notes="Count verse continuing from p.100.")
