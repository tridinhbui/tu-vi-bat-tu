family("tt")
# ---------------------------------------------------------------- TT pp.91-93 phú nôm (image of p.93 compared with the text layer: same order)
page("TT", 91, "Phú nôm cung Tật Ách (12 lines) + the author's note that TT's Huynh Đệ / Tử Tức sections are only counts; phú nôm Huynh Đệ begins.")
page("TT", 92, "Phú nôm Huynh Đệ (cont.) + phú nôm Tử Tức begins.")
page("TT", 93, "Phú nôm Tử Tức (cont.); 'Vấn đề vận hạn' heading. Page image read: line order as in the text layer.")
TA, HD, TU = "Tật Ách", "Huynh Đệ", "Tử Tức"
E("tt91_tat_tuan_triet", "TT", 91, TA, "Phú nôm cung Tật Ách", "Triệt Tuần đóng tại Aùch cung",
  "Tuần hoặc Triệt ở Tật Ách", "tai nào cũng khỏi, nạn nào cũng qua (Tuần Triệt giải ở cung này)", "support", ["health.shielded"],
  notes="next line 'Tai nào cũng khỏi nạn nào cũng qua'; TV_TL_TAT_ACH_GIAM (TL p.128) reads only Triệt at Tật Ách")
for _id, _q, _why in [
    ("tt91_tat_hinh_duong_cai_da", "Hình Dương Hoa Cái ngộ Đà", "a hạn event (đậu hoa) and illness"),
    ("tt91_tat_hoa_linh_tri_moc", "Hoả Linh Trì Mộc chiếu soi", "fire and water accidents (events)"),
    ("tt91_tat_benh_kiep_co", "Bởi vì Tật Aùch Bệnh phùng Kiếp Cơ", "illness"),
    ("tt91_tat_bach_ho", "Aùch cung Bạch Hổ huyết hư", "illness"),
    ("tt91_tat_duong_da_hinh", "Dương Đà Hình hội mục tì", "illness"),
    ("tt91_tat_hoa_ky", "Aùch cung Hoá Kị cho minh", "illness and children"),
    ("tt91_tat_khoi_hinh", "Cung Giải Aùch ngộ Khôi Hình", "lawsuit / prison"),
    ("tt91_tat_hinh_kinh_ngo", "Thiên Hình, Dương Nhẫn (Kình Dương) Ngọ cung", "prison"),
    ("tt91_tat_cu_ky", "Cự kị nên tránh đò sông", "accidents"),
    ("tt91_tat_hoa_linh_hinh_viet", "Hỏa Linh Hình Việt khác nào", "accidents"),
    ("tt91_tat_loc_ton", "Lộc Tồn ám tật miên trường", "illness; the second line ('Tả Hữu Xương Khúc tai ương nên phòng') may continue it: not settled"),
]:
    E(_id, "TT", 91, TA, "Phú nôm cung Tật Ách", _q, "", "", "limit", [], skip=_why)
E("tt91_bao_tuan_triet", "TT", 91, HD, "Phú nôm Huynh Đệ", "Cung Huynh Đệ Triệt Tuần làm thủ",
  "Tuần hoặc Triệt ở Huynh Đệ", "'chim đầu đàn vỗ cánh bay cao'", "support", [], skip="'Chim đầu đàn vỗ cánh bay cao' is read either as the eldest rising high or as the eldest leaving / dying: not settled")
E("tt91_bao_kk_don_so", "TT", 91, HD, "Phú nôm Huynh Đệ", "Lâm vào Huynh Đệ đơn sơ một mình",
  "Địa Không hoặc Địa Kiếp ở Huynh Đệ", "anh em ít, lẻ loi một mình", "limit", ["kin.few"], notes="'Kiếp Không hai gã nên ngừa / Lâm vào Huynh Đệ đơn sơ một mình'")
E("tt92_bao_pha_hinh_ky", "TT", 92, HD, "Phú nôm Huynh Đệ", "Phá phùng Hình kị Huynh hương",
  "Huynh Đệ có Phá Quân, Thiên Hình và Hóa Kỵ", "anh em bất thuận, nhiều đường tranh nhau", "limit", ["kin.strain"],
  notes="next line 'Anh em bất thuận nhiều đường tương tranh'")
E("tt92_bao_tuong_quan_loc_ma", "TT", 92, HD, "Phú nôm Huynh Đệ", "Tướng Quân Lộc Mã đồng cung",
  "Huynh Đệ có Tướng Quân, Thiên Mã và Lộc Tồn hoặc Hóa Lộc đồng cung", "anh em có người quyền quý", "support", ["kin.talented"],
  notes="next line 'Anh em có kẻ triều trung quí quyền'; TH p.99 has the chiếu variant (TV_TH7_HUYNH_DE_TUONG_LOC_MA)")
E("tt92_bao_tu_tang_ta_huu", "TT", 92, HD, "Phú nôm Huynh Đệ", "Tử Tang Tả Hữu cùng ngôi", "", "", "limit", [], skip="a sister's marriage (an event about another person)")
E("tt92_bao_tang_ma", "TT", 92, HD, "Phú nôm Huynh Đệ", "Tang Môn ngộ Mã đinh ninh", "Tang Môn gặp Thiên Mã ở Huynh Đệ", "anh em mỗi người một xứ", "limit", ["kin.apart"],
  dup="TV_TH7_HUYNH_DE_TANG_MA", notes="the same verse as TH p.100")
E("tt92_bao_dao_thai_hy", "TT", 92, HD, "Phú nôm Huynh Đệ", "Đào Hoa, Thai, Hỉ trong cung", "", "", "limit", [], skip="sexual reputation and pregnancy of a sister")
E("tt92_bao_tuong_phu_phuc", "TT", 92, HD, "Phú nôm Huynh Đệ", "Trong thời Tướng Phủ, Phục Binh", "", "", "limit", [], skip="sexual reputation")
E("tt92_bao_hoa_ky_hinh", "TT", 92, HD, "Phú nôm Huynh Đệ", "Gặp sao Hoá Kị khiếm hoà", "Hóa Kỵ, Thiên Hình ở Huynh Đệ", "anh em xung khắc", "limit", ["kin.strain"],
  dup="TV_KL7_HUYNH_DE_HOA_KY", notes="KL p.156 (Hóa Kỵ) and TH p.100 (Thiên Hình) already read it")
E("tt92_bao_tu_ta_huu", "TT", 92, HD, "Phú nôm Huynh Đệ", "Tử Vi, Tả Hữu lâm vào", "", "", "limit", [], skip="sexual reputation of a sister")
E("tt92_bao_tu_phu_thin", "TT", 92, HD, "Phú nôm Huynh Đệ", "Bào cung Tử Phủ ở Thìn", "", "", "limit", [],
  skip="Tử Vi and Thiên Phủ stand together only at Dần/Thân: 'Tử Phủ ở Thìn' cannot occur; and remarriage of a relative")
E("tt92_tu_kk", "TT", 92, TU, "Phú nôm Tử Tức", "Tử Cung ngộ Kiếp Không gia", "", "", "limit", [], skip="count and death of children")
E("tt92_tu_khoc_hu_duong", "TT", 92, TU, "Phú nôm Tử Tức", "Khốc Hư đồng ngộ Dưỡng tinh", "", "", "limit", [], skip="death of children")
E("tt92_tu_hinh_hao", "TT", 92, TU, "Phú nôm Tử Tức", "Hiếm hoi bởi tại Hình Hao",
  "Tử Tức có Thiên Hình và Đại Hao hoặc Tiểu Hao", "hiếm con", "limit", ["kin.few"],
  notes="the second half 'Qúi tinh trước cửa một hào đông con' does not say which quý tinh nor where 'trước cửa' is: not used")
E("tt92_tu_hinh_sat_ho", "TT", 92, TU, "Phú nôm Tử Tức", "Thiên Hình Sát Hổ Tử cung", "", "", "limit", [], skip="childlessness to old age (count); 'Sát' not named")
E("tt92_tu_sat_da_kk_xung", "TT", 92, TU, "Phú nôm Tử Tức", "Tử Cung xung chiếu Sát Đà Kiếp Không", "", "", "limit", [], skip="a child's mental disability (health)")
E("tt92_tu_kk_trung_giao", "TT", 92, TU, "Phú nôm Tử Tức", "Tử Cung Không Kiếp trùng giao", "", "", "limit", [], skip="illness at birth")
E("tt92_tu_qui_tinh_than_dau", "TT", 92, TU, "Phú nôm Tử Tức", "Qui tinh hội họp cung Thân Dậu", "", "", "limit", [], skip="'quý tinh' not listed; a birth event")
E("tt92_tu_truong_sinh_de_vuong", "TT", 92, TU, "Phú nôm Tử Tức", "Tràng sinh đế vượng đa nhân",
  "Tử Tức có Trường Sinh hoặc Đế Vượng", "đông con", "support", ["kin.many"], notes="the next line (twins, giáp Nhật Nguyệt) is left out")
E("tt92_tu_de_vuong_thai_khoi", "TT", 92, TU, "Phú nôm Tử Tức", "Đế vương ngộ Thai Khôi cùng Tướng", "", "", "limit", [], skip="half-siblings (an event)")
E("tt93_tu_da_ky", "TT", 93, TU, "Phú nôm Tử Tức", "Bởi sao Đà Kị làm hàng Tử cung",
  "Tử Tức có Đà La và Hóa Kỵ", "hiếm con", "limit", ["kin.few"], notes="'Sinh con số hiếm rõ ràng / Bởi sao Đà Kị làm hàng Tử cung'")
E("tt93_tu_ho_lang_kk", "TT", 93, TU, "Phú nôm Tử Tức", "Hổ Lang Không Kiếp Tang Giao", "", "", "limit", [], skip="death of children")
E("tt93_tu_quyen_loc", "TT", 93, TU, "Phú nôm Tử Tức", "Sinh con Quyền Lộc hiển vinh",
  "Tử Tức có Hóa Quyền và Hóa Lộc", "con cái hiển vinh", "support", ["kin.talented"],
  notes="'Quyền Lộc' read as Hóa Quyền and Hóa Lộc both in the palace (the narrower reading)")
E("tt93_tu_khoi_viet_van", "TT", 93, TU, "Phú nôm Tử Tức", "Sinh con Khôi Việt Văn tinh đỗ đầu",
  "Tử Tức có Thiên Khôi hoặc Thiên Việt, và Văn Xương hoặc Văn Khúc", "con cái học hành đỗ đạt cao", "support", ["kin.talented"],
  notes="Khôi and Việt never share a palace, nor Xương Khúc outside Sửu/Mùi: one of each pair")
E("tt93_tu_long_phuong", "TT", 93, TU, "Phú nôm Tử Tức", "Sinh con Long Phượng sang giàu",
  "Tử Tức có Long Trì và Phượng Các", "con cái sang giàu", "support", ["kin.prosper"],
  notes="KL p.149 (TV_KL7_TU_TUC_LONG_PHUONG) reads the same pair as 'rất tốt cho đường con cái'; this line names wealth and rank")
E("tt93_tu_xuong_khuc_chieu_giap", "TT", 93, TU, "Phú nôm Tử Tức", "Khúc Xương chiếu giáp thập hầu tặng phong", "", "", "support", [],
  skip="'chiếu giáp' does not settle whether Xương Khúc aim at or flank the palace")
E("tt93_tu_hy_than_phuc_tinh", "TT", 93, TU, "Phú nôm Tử Tức", "Hỉ Thần hội với Phúc Tinh", "", "", "support", [],
  skip="'Phúc Tinh' is not one named star (Thiên Phúc? Phúc Đức?)")
E("tt93_tu_thai_tuong_phuc", "TT", 93, TU, "Phú nôm Tử Tức", "Tử cung Thai, Tướng Phục Binh", "", "", "limit", [], skip="infidelity")
E("tt93_tu_co_qua", "TT", 93, TU, "Phú nôm Tử Tức", "Gian chuân vất vả về hài nhi sinh",
  "Cô Thần, Quả Tú ở Tử Tức", "vất vả về đường sinh con", "limit", ["kin.few"], dup="TV_KL7_TU_TUC_CO_QUA", notes="KL p.153 already reads Cô Quả at Tử Tức")
E("tt93_tu_thai_ta_huu", "TT", 93, TU, "Phú nôm Tử Tức", "Thai cùng Tả Hữu hội trung", "", "", "limit", [], skip="children of a concubine (an event)")
E("tt93_tu_vu_xuong_khuc", "TT", 93, TU, "Phú nôm Tử Tức", "Vũ Xương hoặc Khúc cùng ngồi", "", "", "support", [], skip="the children's appearance")
E("tt93_tu_khoc_hu_tuong_binh", "TT", 93, TU, "Phú nôm Tử Tức", "Tướng, Binh, xung phá hẳn đành hoang thai.", "", "", "limit", [], skip="pregnancy out of wedlock")
E("tt93_tu_xuong_khuc", "TT", 93, TU, "Phú nôm Tử Tức", "Cung Tử mà có Khúc Xương",
  "Tử Tức có Văn Xương hoặc Văn Khúc", "con cái dễ thành người ham ăn chơi", "limit", ["kin.wayward"],
  notes="next line 'Tuồng gì con cái những phường ăn chơi'")
E("tt93_tu_kinh_hu", "TT", 93, TU, "Phú nôm Tử Tức", "Kình Dương mà gặp Thiên Hư", "", "", "limit", [], skip="death of children ('hữu sinh vô dưỡng')")
E("tt93_tu_dau_quan", "TT", 93, TU, "Phú nôm Tử Tức", "Đẩu Quân cung Tử hiếm con", "Đẩu Quân ở Tử Tức", "hiếm con", "limit", ["kin.few"],
  dup="TV_KL7_TU_TUC_DAU_QUAN", notes="KL p.193 already reads it; the rescue line 'Cát tinh giao hội may còn ước mong' goes to che_hoa.json")
E("tt93_tu_duong_da_tuyet", "TT", 93, TU, "Phú nôm Tử Tức", "Dương Đà ngộ Tuyệt phùng xung", "", "", "limit", [], skip="'uổng công sinh thành' (a child lost or failing): not settled, sensitive")
E("tt93_tu_hoa_linh_kinh", "TT", 93, TU, "Phú nôm Tử Tức", "Có sinh con cũng liệt vào tật thương", "", "", "limit", [], skip="children's injury (health)")
E("tt93_tu_sat_ham_hinh", "TT", 93, TU, "Phú nôm Tử Tức", "Thất Sát hãm gặp Thiên Hình",
  "Tử Tức có Thất Sát hãm (bảng Toàn Thư) và Thiên Hình", "con cái dễ thành người ngang tàng, phóng đãng", "limit", ["kin.wayward"],
  notes="next line 'Sinh con những giống lưu manh hoang tàng'")
E("tt93_tu_pha_ba_tre", "TT", 93, TU, "Phú nôm Tử Tức", "Phá Quân ba trẻ bất tài", "", "", "limit", [], skip="a count of children")
E("tt93_tu_loc_ton_gia_sat", "TT", 93, TU, "Phú nôm Tử Tức", "Lộc Tồn gia Sát hiếm hoi vô cùng", "", "", "limit", [],
  skip="'Sát' (Thất Sát or the sát tinh?) not settled; Lộc Tồn never shares a palace with Kình or Đà")

# ---------------------------------------------------------------- TT pp.141-149 cách cục (TT's own translation of 紫微斗數全書 卷一 定富局 /
# 定貴局 / 定貧賤局 and the 十二宮 hợp cách / phá cách verses; the original is in engine/data/sources_web/zwds_quanshu_1.txt)
page("TT", 141, "Tính tình phú (from TH, cited by TT) + 'Cách Cục' + PHÚ CÁCH begins.")
page("TT", 142, "Phú cách (cont.), QUÍ CÁCH, BẦN TIỆN CÁCH begins.")
page("TT", 143, "Bần tiện cách (cont.); Thập nhị cung chư tinh đắc địa hợp cách quyết: Tí, Sửu, Dần (verse).")
page("TT", 144, "Hợp cách: Dần..Mùi.")
page("TT", 145, "Hợp cách: Mùi..Hợi.")
page("TT", 146, "Author's doubts on the tuổi; 'Thập nhị cung đắc địa phú quí luận' (verse only).")
page("TT", 147, "Thập nhị cung chư tinh thất hãm phá cách quyết: Tí Sửu, Dần, Mão Thìn, Tị, Ngọ (verse).")
page("TT", 148, "Phá cách: Ngọ 'Nghĩa là' .. Hợi.")
page("TT", 149, "'Thất hãm bần tiện luận' verse; Thập đẳng luận.")
C = "Cách cục"
E("tt141_tai_am_hiep_an", "TT", 141, M, C, "Thiên Tướng thủ Mệnh, Vũ Khúc Thiên Lương hội hiệp, ở điền trạch cung cũng vậy", "Tài ấm hiệp ấn", "", "support", [],
  skip="the translation says 'hội hiệp' (meet) where 紫微斗數全書 卷一 定富局 says 夾 (flank): two different conditions; recorded in schools.json")
E("tt142_nhat_nguyet_hiep_tai", "TT", 142, M, C, "Vũ Khúc thủ Mệnh, Nhật Nguyệt giáp mệnh",
  "Mệnh có Vũ Khúc, hai cung kề có Thái Dương và Thái Âm", "cách Nhật Nguyệt hiệp tài (phú cách)", "support", ["fin.abundance"], kind="formation")
E("tt142_tai_loc_hiep_ma", "TT", 142, M, C, "Thiên Mã thủ Mệnh, giáp Vũ Khúc, Hóa Lộc",
  "Mệnh có Thiên Mã, hai cung kề có Vũ Khúc và Hóa Lộc", "cách Tài Lộc hiệp Mã (phú cách)", "support", ["fin.abundance"],
  dup="CACH_X_TAI_LOC_GIAP_MA", notes="made one formation with KL p.45 (Lộc Tồn) in formations_verified.json; the readings differ on which Lộc")
E("tt142_nn_chieu_bich", "TT", 142, "Điền Trạch", C, "Nhật Nguyệt ở điền trạch cung, tại Thìn tuất Sửu Mùi mới thật tốt",
  "Điền Trạch có Thái Dương và Thái Âm (đồng cung ở Sửu/Mùi)", "cách Nhật Nguyệt chiếu bích ở Điền Trạch (phú cách)", "support", ["prop.rich"], kind="formation",
  notes="TH p.73 names a Mệnh cách Nhật Nguyệt chiếu bích (Nhật Nguyệt ở Sửu chiếu Mùi); 紫微斗數全書 日月照璧: 日月臨田宅宮. Both readings recorded in schools.json")
E("tt142_kim_san_quang_huy", "TT", 142, M, C, "Kim sán quang huy (Thái Dương đơn thủ mệnh cung ở Ngọ)", "Thái Dương đơn thủ Mệnh ở Ngọ", "", "support", [],
  dup="CACH_X_NHAT_LE_TRUNG_THIEN", notes="the same core as the verified cách Nhật lệ trung thiên")
E("tt142_nhat_xuat_phu_tang_quan", "TT", 142, "Quan Lộc", C, "Thái Dương tại cung Mão thủ mệnh hoặc quan lộc cung",
  "Quan Lộc ở Mão có Thái Dương", "cách Nhật xuất phù tang ở Quan Lộc (quý cách)", "support", ["career.status"], kind="formation",
  notes="the Mệnh half is TH p.73 Nhật chiếu lôi môn (TV_TH_CACH_MENH_NHAT_MAO); only the Quan Lộc half is new")
E("tt142_nguyet_sinh_suong_hai", "TT", 142, "Điền Trạch", C, "Nguyệt sinh sương hải (Thái âm ở cung Tí, thủ điền trạch)",
  "Điền Trạch ở Tý có Thái Âm", "cách Nguyệt sinh thương hải ở Điền Trạch (quý cách)", "support", ["prop.rich"], kind="formation",
  notes="TH p.73 reads the name at Mệnh (TV_TH_CACH_MENH_NGUYET_TY); TT and 紫微斗數全書 (月在子宮守田宅) put it at Điền Trạch: schools.json")
E("tt142_quan_than_khanh_hoi", "TT", 142, M, C, "Tử Vi, Tả Hữu cùng ở cung mệnh, lại gặp Vũ Khúc, Thiên Tướng chiếu",
  "Mệnh có Tử Vi, Tả Phụ, Hữu Bật; Vũ Khúc và Thiên Tướng trong tam phương", "cách Quân thần khánh hội (quý cách)", "support", ["career.status", "social.support"],
  kind="formation")
E("tt142_tai_an_hiep_loc", "TT", 142, M, C, "Lộc thủ Mệnh Thiên Lương Thiên Tướng hội hiệp", "Tài ấn hiệp lộc", "", "support", [],
  skip="'hội hiệp' in the translation vs 夾 in 紫微斗數全書 定貴局 (財印夾祿): two conditions; and 'Lộc' (Tồn or Hóa) not named. schools.json")
E("tt142_hinh_tu_hiep_an", "TT", 142, M, C, "Thiên Tướng thủ Mệnh Thân, có Thiên Hình Liêm Trinh hội hiệp quí về võ cách",
  "Mệnh có Thiên Tướng, Liêm Trinh và Thiên Hình đồng cung", "cách Hình tù hiệp ấn: quý về võ nghiệp", "support", ["exp.martial", "career.status"], kind="formation",
  notes="紫微斗數全書: 天刑廉貞同臨身命; Liêm Tướng share a palace at Tý/Ngọ")
E("tt142_khoa_quyen_loc_cung", "TT", 142, M, C, "Khoa, Quyền lộc củng (Chiếu thủ có cả ba Khoa, Quyền, Lộc)",
  "tam phương Mệnh có đủ Hóa Khoa, Hóa Quyền, Hóa Lộc", "cách Khoa Quyền Lộc củng (quý cách)", "support", ["career.status"], kind="formation")
E("tt142_tham_hoa_mao", "TT", 142, M, C, "Tham Lang cư miếu địa, thủ Mệnh tại cung Mão", "Tham Hỏa tương phùng", "", "support", [],
  skip="the translation adds 'cung Mão', which 紫微斗數全書 (二星守命同居廟旺) does not have; TH p.73 has the cách: schools.json")
E("tt142_kim_du_pho_gia", "TT", 142, M, C, "Tử Vi thủ Mệnh, có Nhật Nguyệt giáp mệnh", "Kim du phò giá", "", "support", [],
  skip="the author himself says the gloss cannot occur (Tử Vi is never flanked by Nhật Nguyệt); TH p.73 has its own cách: schools.json")
E("tt142_sinh_bat_phung_thoi", "TT", 142, M, C, "Mệnh tọa Không Vong lại gặp sao Liêm Trinh", "Sinh bất phùng thời", "", "limit", [],
  dup="TV_TH_CACH_MENH_BT_SINH_BAT_PHUNG", notes="TH p.74 has the cách")
E("tt143_quan_tu_tai_da", "TT", 143, M, C, "Mệnh có Tứ Sát, chính diệu lại ở hãm địa ví như người quân tử lang thang",
  "Mệnh có từ hai trong Kình Dương, Đà La, Hỏa Tinh, Linh Tinh và một chính tinh hãm (bảng Toàn Thư)", "cách Quân tử tại dã (bần tiện cách)", "limit",
  ["life.hardship"], kind="formation", notes="'Tứ Sát' as a group: two of the four (Kình and Đà never share a palace)")
E("tt143_loc_phung_luong_sat", "TT", 143, M, C, "Lộc tọa Không Vong, Tuần Triệt gặp thêm Không Kiếp", "Lộc phùng lưỡng sát", "", "limit", [],
  dup="TV_TH_CACH_MENH_BT_LOC_LUONG_SAT", notes="TH p.74 has the cách; TT adds Tuần Triệt: schools.json")
E("tt143_ma_lac_khong_vong", "TT", 143, M, C, "Thiên Mã ngộ Triệt Tuần, dù có Lộc Tồn, Hóa Lộc xung chiếu cũng vô ích", "Mã lạc Không vong", "", "limit", [],
  dup="TV_TH_CACH_MENH_BT_MA_LAC", notes="TH p.74 has the cách")
E("tt143_tai_du_tu_cuu", "TT", 143, M, C, "Vũ Khúc, Liêm Trinh cũng ở thân hay mệnh", "Tài dữ tù cừu", "", "limit", [],
  skip="Vũ Khúc and Liêm Trinh never share a palace: which of Thân / Mệnh holds which is not stated")
E("tt143_nhat_sinh_co_ban", "TT", 143, M, C, "Nhất sinh cô bần", "Mệnh có Phá Quân hãm (bảng Toàn Thư)", "cách Nhất sinh cô bần (bần tiện cách)", "limit",
  ["fin.scarcity", "social.isolated"], kind="formation", notes="'(Phá Quân thủ mệnh hãm địa)' on the next line")
E("tt143_luong_trung_hoa_cai", "TT", 143, M, C, "Lưỡng trùng Hoa Cái (Lộc Tồn, Hóa Lộc gặp Không Kiếp)",
  "Mệnh có Lộc Tồn và Hóa Lộc, thêm Địa Không hoặc Địa Kiếp đồng cung", "cách Lưỡng trùng Hoa Cái (bần tiện cách)", "limit", ["fin.volatile"], kind="formation")
E("tt143_nn_tang_huy", "TT", 143, M, C, "Thái Aâm, Thái Dương hãm địa gặp Cự Môn", "Nhật Nguyệt tàng huy", "", "limit", [],
  skip="'日月反背' needs both luminaries hãm wherever they stand; made from KL p.46's own reading (Nhật Nguyệt tàng hung) instead, and the definitions compared in schools.json")
E("tt143_hop_ty", "TT", 143, M, "Hợp cách: Mệnh tại Tí", "Khi mệnh đóng cung Tí có Tham Lang, Thất Sát, Thái Aâm thủ mệnh Cơ Lương củng",
  "Mệnh ở Tý có Tham Lang, Thất Sát hoặc Thái Âm; Thiên Cơ, Thiên Lương trong tam phương; tuổi Canh, Tân, Ất, Quý", "suốt đời phú quý, hạnh phúc", "support",
  ["fin.abundance", "life.blessed"])
E("tt143_hop_suu", "TT", 143, M, "Hợp cách: Mệnh tại Sửu", "người tuổi Bính Tuất cực hay", "Mệnh Sửu, Nhật Nguyệt chiếu", "", "support", [],
  skip="the tuổi: TT 'Bính Tuất', 紫微斗數全書 '丙戍' (probably 丙戊, Bính / Mậu): not settled; the 'chính tọa = trung cách' half goes to schools.json")
E("tt144_hop_dan", "TT", 144, M, "Hợp cách: Mệnh tại Dần", "Khi Mệnh đóng ở Dần, có Cự Môn, Thái Dương thủ hay Thất Sát, Thiên Lương việc",
  "Mệnh ở Dần có Cự Môn và Thái Dương, hoặc Thất Sát, hoặc Thiên Lương; tuổi Thân, Tỵ hoặc Canh", "việc gì cũng thông suốt", "support", ["career.success"],
  notes="'hợp với người tuổi Thân, Tị và Canh' (申巳庚人)")
E("tt144_hop_mao", "TT", 144, M, "Hợp cách: Mệnh tại Mão", "Khi Mệnh đóng ở cung Mão có Cự Cơ hoặc Vũ Khúc thủ rất hợp cho người tuổi",
  "Mệnh ở Mão có Cự Môn, Thiên Cơ hoặc có Vũ Khúc; tuổi Tân, Ất", "đàn ông nhiều phúc lộc, đàn bà giàu sang", "support", ["life.blessed", "fin.abundance"])
E("tt144_hop_thin", "TT", 144, M, "Hợp cách: Mệnh tại Thìn", "câu thứ hai tối nghĩa không giải", "Cơ Lương Thìn", "", "support", [],
  skip="the author says the second line cannot be read; 'Thìn Tuất Cơ Lương' is disputed between TT p.70 and 紫微斗數全書: schools.json")
E("tt144_hop_ty", "TT", 144, M, "Hợp cách: Mệnh tại Tị", "Khi Mệnh đóng ở cung Tị, có Thiên Cơ Thiên Tướng thủ, hoặc Tử Vi đóng đấy",
  "Mệnh ở Tỵ có Thiên Cơ, Thiên Tướng hoặc Tử Vi; tuổi Mậu, Tân, Nhâm, Bính", "tốt phúc, dễ toại ý, ít tai họa", "support", ["life.blessed"])
E("tt144_hop_ngo", "TT", 144, M, "Hợp cách: Mệnh tại Ngọ", "Khi Mệnh đóng cung Ngọ, có Tử Vi, hoặc Thái Dương hay Thất Sát hoặc Phá Quân",
  "Mệnh ở Ngọ có Tử Vi, Thái Dương, Thất Sát hoặc Phá Quân; tuổi Giáp, Đinh, Kỷ, Quý", "làm lớn, bổng lộc dồi dào", "support", ["career.status"])
E("tt145_hop_mui", "TT", 145, M, "Hợp cách: Mệnh tại Mùi", "Bài quyết này có chỗ bất", "Mùi Tử Vũ Liêm / Nhật Nguyệt Cự Môn", "", "support", [],
  skip="the author disputes the verse (Cự Môn hãm at Mùi; Nhật Nguyệt Sửu Mùi lận đận): schools.json")
E("tt145_hop_than", "TT", 145, M, "Hợp cách: Mệnh tại Thân", "Khi Mệnh đóng Thân cung có Tử Vi, Liêm Trinh, Thiên Lương, Vũ Khúc, Cự Môn",
  "Mệnh ở Thân có Tử Vi, Liêm Trinh, Thiên Lương, Vũ Khúc hoặc Cự Môn; tuổi Giáp, Canh, Quý", "được phú quý, thỏa chí", "support", ["fin.abundance", "career.success"])
E("tt145_hop_dau", "TT", 145, M, "Hợp cách: Mệnh tại Dậu", "Khi Mệnh đóng cung Dậu có Thái Aâm tọa thủ cực tốt",
  "Mệnh ở Dậu có Thái Âm", "cực tốt", "support", ["life.blessed"])
E("tt145_hop_tuat", "TT", 145, M, "Hợp cách: Mệnh tại Tuất", "Thiên Phủ tọa thủ thì chỉ có hư danh thôi rất giàu mà",
  "Mệnh Tuất ...", "", "limit", [], skip="the translation names Thiên Phủ where the verse (and 紫微斗數全書 戍宮紫微對冲辰) names Tử Vi: schools.json")
E("tt145_hop_hoi", "TT", 145, M, "Hợp cách: Mệnh tại Hợi", "Khi Mệnh đóng cung Hợi có Thái Aâm tọa thủ tuyệt hảo",
  "Mệnh ở Hợi có Thái Âm", "phú quý vinh hoa", "support", ["fin.abundance", "life.blessed"], dup="TV_TH_CACH_MENH_NGUYET_HOI",
  notes="TH p.73 Nguyệt lãng thiên môn has the same core")
E("tt147_pha_co_ty_ngo_cu_linh", "TT", 147, M, "Phá cách: Mệnh tại Tí Sửu", "Tí Ngọ Thiên Cơ, Sửu Cự Linh",
  "Mệnh ở Tý/Ngọ có Thiên Cơ, hoặc Mệnh ở Sửu có Cự Môn và Linh Tinh", "phá cách: dù có cát diệu mà phú quý cũng chẳng bền", "limit", ["fortune.brief_luck"],
  notes="the translation on the page says 'Mệnh đóng Tị cung có sao Thiên Cơ'; the verse and 紫微斗數全書 (子午天機) say Tý Ngọ: the verse is followed (schools.json)")
E("tt147_pha_dan_co_xuong_khuc_nguyet", "TT", 147, M, "Phá cách: Mệnh tại Dần", "Dần thương Cơ Xương Khúc Nguyệt phùng",
  "Mệnh ở Dần có Thiên Cơ, Thái Âm, Văn Xương hoặc Văn Khúc", "phá cách", "limit", ["career.obstacle"], dup="tt68_co_am_dan_xuong_khuc",
  notes="the same verse as p.68; one rule cites both pages")
E("tt147_pha_mao_am_kinh", "TT", 147, M, "Phá cách: Mệnh tại Mão Thìn", "Mão thượng Thái Aâm Kình Dương phùng",
  "Mệnh ở Mão có Thái Âm và Kình Dương", "phá cách: dù hóa cát cũng không toàn mỹ", "limit", ["life.blessed"],
  notes="the translation's last sentence inverts the verse (若非加殺到頭凶); only 'cách bất toàn mỹ' is used")
E("tt147_pha_thin_cu_tu", "TT", 147, M, "Phá cách: Mệnh tại Mão Thìn", "Thìn cung Cự tú Tử Vi đồng",
  "Mệnh ở Thìn có Cự Môn hoặc Tử Vi", "phá cách: dù hóa cát cũng không toàn mỹ", "limit", ["life.blessed"])
E("tt147_pha_ty", "TT", 147, M, "Phá cách: Mệnh tại Tị", "Tị cung Vũ Nguyệt Thiên Lương Cự",
  "Mệnh ở Tỵ có Vũ Khúc, Thái Âm, Thiên Lương, Cự Môn, Tham Lang hoặc Liêm Trinh", "phá cách: dù có cát diệu chiếu cũng vô ích, đời vất vả thiếu thốn", "limit",
  ["fin.scarcity", "life.hardship"])
E("tt147_pha_ngo_kinh", "TT", 147, M, "Phá cách: Mệnh tại Ngọ", "Dương Nhẫn tam hợp tối hiềm xung",
  "Mệnh ở Ngọ có Tham Lang, Cự Môn, Thái Âm hoặc Văn Xương; Kình Dương trong tam phương", "phá cách: hoạnh thành hoạnh phá, khó lâu bền", "limit", ["fin.volatile"],
  notes="'Ngọ cung Tham Cự Nguyệt Xương tòng / Dương Nhẫn tam hợp tối hiềm xung'")
E("tt148_pha_mui", "TT", 148, M, "Phá cách: Mệnh tại Mùi", "Khi Mệnh đóng cung Mùi có Cự Môn, Thái Dương tọa thủ rất xấu",
  "Mệnh ở Mùi có Cự Môn hoặc Thái Dương", "phá cách: vất vả bôn ba, chìm nổi, hay rắc rối quan tụng", "limit", ["life.hardship", "life.legal"],
  notes="the khắc thương clause is left out")
E("tt148_pha_than_nam", "TT", 148, M, "Phá cách: Mệnh tại Thân Dậu", "Khi Mệnh đóng cung Thân có Cự Cơ tọa thủ là phá cách, trai phiêu bạt",
  "nam, Mệnh ở Thân có Cự Môn hoặc Thiên Cơ", "phá cách: dễ phiêu bạt", "limit", ["life.transient"], notes="Cự Cơ share a palace only at Mão/Dậu: one of them at Thân")
E("tt148_pha_than_nu", "TT", 148, M, "Phá cách: Mệnh tại Thân Dậu", "trai phiêu bạt gái bần",
  "nữ, Mệnh ở Thân có Cự Môn hoặc Thiên Cơ", "phá cách: dễ túng thiếu", "limit", ["fin.scarcity"])
E("tt148_pha_tuat", "TT", 148, M, "Phá cách: Mệnh tại Tuất", "Khi Mệnh đóng cung Tuất có Tử Vi, Phá Quân, Thiên Đồng, Thái Dương tọa thủ",
  "Mệnh ở Tuất có Tử Vi, Phá Quân, Thiên Đồng hoặc Thái Dương", "phá cách: đều chủ hung, vất vả thiếu thốn", "limit", ["life.hardship"],
  notes="the yểu chiết clause is left out")
E("tt148_pha_hoi", "TT", 148, M, "Phá cách: Mệnh tại Hợi", "có Tham Lang, Hỏa Tinh, Thiên Lương tọa thủ tất phiêu",
  "Hợi Tham Hỏa Lương", "", "limit", [], skip="Tham Lang and Thiên Lương never share a palace: which of the three must stand at Hợi is not settled; and longevity")
E("tt149_tham_hoa_loc_tu_mo", "TT", 149, M, "Thất hãm bần tiện luận", "Tham Lang, Hỏa Lộc cư tứ mộ",
  "Mệnh ở tứ mộ có Tham Lang hóa Lộc (tuổi Mậu)", "dù gặp cát tinh cũng chỉ trung bình", "limit", ["life.blessed"],
  notes="TT prints 'Hỏa Lộc'; 紫微斗數全書 卷一 十二宮諸星失陷貧賤論: 貪狼化祿居四墓, 縱然遇吉亦中平 — read as Hóa Lộc (TH p.81 prints 'Hoá lộc')")
