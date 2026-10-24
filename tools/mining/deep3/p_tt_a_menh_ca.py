family("tt")
# ---------------------------------------------------------------- TT pp.64-76 Nam Mệnh ... ca (text layer in reading order; image of
# p.93 compared, TT is a typed edition). The verses are for NAM mệnh (p.64: 'Dành cho nam mệnh'; p.73 says only Khôi Việt is not split by sex).
page("TT", 64, "Mệnh/Thân thể dụng; ca split in three (nam, nữ, vận hạn); Nam Mệnh Tử Vi ca begins.")
page("TT", 65, "Tử Vi ca 'Nghĩa là' + Thiên Cơ ca + Thái Dương ca (verse).")
page("TT", 66, "Thái Dương 'Nghĩa là', Vũ Khúc ca, Thiên Đồng ca (verse).")
page("TT", 67, "Thiên Đồng / Liêm Trinh / Thiên Phủ 'Nghĩa là'.")
page("TT", 68, "Thái Âm ca, Tham Lang ca.")
page("TT", 69, "Tham Lang end, Cự Môn ca, Thiên Tướng ca.")
page("TT", 70, "Thiên Lương ca, Thất Sát ca (verse).")
page("TT", 71, "Thất Sát 'Nghĩa là', Phá Quân ca, Văn Xương ca (verse).")
page("TT", 72, "Văn Xương 'Nghĩa là', Văn Khúc ca, Tả Phụ ca, Hữu Bật ca (verse).")
page("TT", 73, "Hữu Bật 'Nghĩa là', Lộc Tồn ca, Khôi Việt ca, Kình Dương ca (verse).")
page("TT", 74, "Kình Dương 'Nghĩa là', Đà La ca, Hỏa Linh ca, Thiên Không Địa Kiếp ca (verse).")
page("TT", 75, "Không Kiếp 'Nghĩa là', Hóa Lộc ca, Hóa Quyền ca, Hóa Khoa ca (verse).")
page("TT", 76, "Hóa Khoa 'Nghĩa là', Hóa Kỵ ca, Thái Tuế ca, phú đoán Thân Mệnh a)-g).")

M = "Mệnh"
E("tt65_tu_vi_menh", "TT", 65, M, "Nam Mệnh Tử Vi ca", "Cung mệnh có Tử Vi, Phúc Lộc tiền tài hưng vượng",
  "nam, Mệnh có Tử Vi", "phúc lộc, tiền tài hưng vượng", "support", ["fin.abundance", "life.blessed"])
E("tt65_tu_vi_tuong_ta", "TT", 65, M, "Nam Mệnh Tử Vi ca", "Nếu thêm Tướng Tá hội tụ tất phú quí song toàn",
  "Tử Vi + 'Tướng Tá' hội", "phú quý song toàn", "support", ["fin.abundance", "career.status"],
  skip="'Tướng Tá' (將佐) does not name stars the chart can be checked for (Thiên Tướng and Tả Phụ? the ministers Tả Hữu?)")
E("tt65_tu_vi_kk", "TT", 65, M, "Nam Mệnh Tử Vi ca", "nếu gặp Kiếp Không (nhị sát) thì không thọ",
  "Tử Vi gặp Không Kiếp", "không thọ", "limit", [], skip="longevity (health policy)")
E("tt65_tu_vi_sat_tinh_chua", "TT", 65, M, "Nam Mệnh Tử Vi ca", "nếu gặp Dương Đà, Hoả Linh chỉ nên vào", "Tử Vi + Kình, Đà, Hỏa, Linh hội (two of them)",
  "chỉ nên theo đường tu hành", "limit", ["spirit.unworldly"], notes="verse 'Dương Đà Hoả Linh lai tương hội': a named group needs two of its stars in the tam phương")
E("tt65_tu_vi_thin_tuat_pha", "TT", 65, M, "Nam Mệnh Tử Vi ca", "Tử Vi đóng cung Thìn, Tuất hội cùng Phá Quân có thể giàu mà chẳng sang loại hư danh",
  "Mệnh ở Thìn/Tuất có Tử Vi (Phá Quân xung chiếu)", "có thể giàu mà chẳng sang, chỉ được hư danh", "limit", ["career.status"],
  notes="Tử Vi at Thìn/Tuất always faces Phá Quân in the opposite palace")
E("tt65_tu_tham_mao_dau", "TT", 65, M, "Nam Mệnh Tử Vi ca", "Tử Vi gặp Tham Lang tại cung Mão, Dậu là người ưa làm tôi bất trung",
  "Mệnh Mão/Dậu có Tử Vi, Tham Lang", "là người làm tôi mà dễ bất trung", "limit", ["values.integrity"])
E("tt65_tu_sat_bon_sat", "TT", 65, M, "Nam Mệnh Tử Vi ca", "Bị Hoả Linh Dương Đà vây bọc thêm Thất Sát, người du thủ du thực bất quí, hay lừa",
  "Mệnh có Tử Vi, Thất Sát, hai trong Hỏa Linh Kình Đà trong tam phương", "du thủ du thực, không quý hiển, hay lừa dối, cô độc", "limit",
  ["values.integrity", "social.isolated"], notes="the sentence goes on 'dối, cô độc nên đi tu cho bớt nghiệp chướng' (line break after 'lừa')")
E("tt65_co_nguyet_luong_nhat", "TT", 65, M, "Nam Mệnh Thiên Cơ ca", "Thiên Cơ, thái âm, thiên lương hợp cùng với Thái Dương đắc địa thì kẻ tầm thường rồi",
  "Mệnh có Thiên Cơ; Thái Âm, Thiên Lương, Thái Dương (đắc địa) trong tam phương", "người bình thường cũng nên giàu, có nhà cửa", "support",
  ["fin.abundance", "prop.rich"], notes="sentence ends on the next line 'cũng sẽ giàu sang nhà cửa'")
E("tt65_co_nguyet_luong_tam_hoa", "TT", 65, M, "Nam Mệnh Thiên Cơ ca", "Nếu là người chức tước được thêm Khoa Quyền Lộc tất chức vị lên",
  "như trên, thêm Khoa, Quyền, Lộc trong tam phương", "người có chức tước thì chức vị lên cao", "support", ["career.status"])
E("tt65_co_hoa_ky_ty", "TT", 65, M, "Nam Mệnh Thiên Cơ ca", "Thiên Cơ ngộ Hoá Kị lại ở nhàn cung (tức cung Tị) dù có chức vị tiền tài",
  "Mệnh ở Tỵ có Thiên Cơ hóa Kỵ (tuổi Mậu)", "dù có chức vị, tiền tài rồi cũng mất hết, dễ thành người phiêu bạt, tu hành", "limit",
  ["fin.volatile", "spirit.unworldly"], notes="Hóa Kỵ falls on Thiên Cơ only in Mậu years (Tứ Hóa); the book itself glosses nhàn cung as Tị here")
E("tt66_nhat_tho", "TT", 66, M, "Nam Mệnh Thái Dương ca", "Trong cung Mệnh có sao, Thái Dương thì phúc thọ nông hậu",
  "Mệnh có Thái Dương", "phúc thọ nồng hậu", "support", [], skip="longevity (health policy); the phúc half alone is not the page's sentence")
E("tt66_nhat_quyen_loc_cat", "TT", 66, M, "Nam Mệnh Thái Dương ca", "Lại được thêm Quyền Lộc và Thiên Khôi, Văn Xương rồi Tả Hữu tất nhiên phú quí ngang với Thạch Sùng",
  "Mệnh có Thái Dương; Hóa Quyền, Hóa Lộc, Thiên Khôi, Văn Xương, Tả Phụ, Hữu Bật trong tam phương", "phú quý lớn", "support", ["fin.abundance", "career.status"])
E("tt66_nhat_suu_mui_vo_hoa", "TT", 66, M, "Nam Mệnh Thái Dương ca", "nếu tam hợp và cung chiếu không thấy Khoa Quyền Lộc là phúc bạc",
  "Mệnh Sửu/Mùi có Thái Dương (Nhật Nguyệt đồng cung), tam phương không có Khoa, Quyền, Lộc", "phúc bạc", "limit", ["life.blessed"])
E("tt66_nhat_suu_mui_sat", "TT", 66, M, "Nam Mệnh Thái Dương ca", "lại bị thêm Sát tinh xung phá xuất đời bần cùng",
  "như trên, thêm sát tinh trong tam phương", "dễ túng thiếu cả đời", "limit", ["fin.scarcity"])
E("tt66_nhat_ham_ky", "TT", 66, M, "Nam Mệnh Thái Dương ca", "Thái Dương rơi vào hãm địa hội Hoá Kị việc gì cũng mờ ám trục trặc",
  "Mệnh có Thái Dương hãm (bảng Toàn Thư), Hóa Kỵ trong tam phương", "việc gì cũng mờ ám, trục trặc, dễ gặp việc bất ngờ hao tổn sản nghiệp", "limit",
  ["life.hardship", "fin.volatile"])
E("tt66_vu_quyen_cat", "TT", 66, M, "Nam Mệnh Vũ Khúc ca", "khí hơn người tinh thần cũng hơn người",
  "Mệnh có Vũ Khúc hóa Quyền, có cát tinh trong tam phương", "chí khí và tinh thần hơn người", "support", ["amb.drive"],
  notes="the 'Nghĩa là' line: 'Vũ Khúc thủ Mệnh hoà thành Quyền. Chung quanh có sao tốt thì hoàn toàn phúc thọ. Chí khí hơn người...' (line break inside 'Chí'); phúc thọ left out (health)")
E("tt66_vu_nhieu_sat", "TT", 66, M, "Nam Mệnh Vũ Khúc ca", "Nếu bị nhiều sát tinh xung phá dù cho giàu có cũng sẽ lụn bại",
  "Mệnh có Vũ Khúc, từ hai sát tinh trong tam phương", "dù giàu có rồi cũng lụn bại", "limit", ["fin.volatile"])
E("tt67_dong_on_hoa", "TT", 67, M, "Nam Mệnh Thiên Đồng ca", "Thiên Đồng toạ mệnh cung, tính tình ôn hoà tử tế có phúc lộc",
  "Mệnh có Thiên Đồng", "tính tình ôn hòa, tử tế, có phúc lộc", "support", ["values.kind"], notes="the sentence goes on 'và đa thọ' (left out: longevity)")
E("tt67_dong_mieu_vuong", "TT", 67, M, "Nam Mệnh Thiên Đồng ca", "Nếu đóng tại miếu vượng chẳng những ăn lộc còn danh tiếng nữa",
  "Mệnh có Thiên Đồng miếu, vượng (bảng Toàn Thư)", "không những có lộc mà còn có danh tiếng", "support", ["career.fame"])
E("tt67_dong_cat", "TT", 67, M, "Nam Mệnh Thiên Đồng ca", "Gặp cát tinh phò trợ, thông minh, lanh lợi",
  "Mệnh có Thiên Đồng, có cát tinh trong tam phương", "thông minh, lanh lợi, làm việc gì cũng dễ lọt", "support", ["cog.sharp"])
E("tt67_dong_ham_hoa_da", "TT", 67, M, "Nam Mệnh Thiên Đồng ca", "thêm Hoả Tinh, Đà La xung phá là rất", "Mệnh có Thiên Đồng hãm (bảng Toàn Thư), Hỏa Tinh và Đà La trong tam phương",
  "rất hung, dù có Nguyệt Lương tiếp ứng cũng chỉ nên an phận", "limit", ["life.hardship"],
  notes="the verse says 'nhàn cung'; the author: nhàn cung of Thiên Đồng is not recorded 'cho nên phải lấy hãm địa mà đoán' (same page) — read as hãm")
E("tt67_liem_ngang", "TT", 67, M, "Nam Mệnh Liêm Trinh ca", "Liêm Trinh thủ Mệnh vốn con người phi thường chí khí ưa ngang ngược",
  "nam, Mệnh có Liêm Trinh", "con người khác thường, chí khí mạnh, ưa ngang ngược", "limit", ["temper.headstrong"])
E("tt67_liem_cach_co_dinh_tan", "TT", 67, M, "Nam Mệnh Liêm Trinh ca", "nếu lên bằng con đường cách cố đỉnh tân",
  "Liêm Trinh, theo đường đấu tranh", "có thể ở bậc đại quý", "support", [], skip="the condition is the path the person takes, not a chart fact")
E("tt67_liem_nhan_cung", "TT", 67, M, "Nam Mệnh Liêm Trinh ca", "gặp Tham Lang, Phá Quân, Kình Dương dù có giàu sang nhưng rất",
  "Liêm Trinh ở nhàn cung", "giàu sang bấp bênh", "limit", [], skip="nhàn cung of Liêm Trinh: the author says it is not recorded (p.67); no position to test")
E("tt67_liem_ham_tat", "TT", 67, M, "Nam Mệnh Liêm Trinh ca", "Liêm Trinh hãm địa (Tị Hợi) có sao tốt vây quanh vẫn hung",
  "Liêm Trinh hãm Tị Hợi", "tàn tật, thương tích", "limit", [], skip="injury and death (health policy)")
E("tt67_phu_quyen_loc_cat", "TT", 67, M, "Nam Mệnh Thiên Phủ ca", "Thiên Phủ thủ Mệnh hội cùng Quyền Lộc và Xương, Khôi, Tả Hữu sẽ được dựa kẻ quyền",
  "Mệnh có Thiên Phủ; Hóa Quyền, Hóa Lộc, Văn Xương, Thiên Khôi, Tả Phụ, Hữu Bật trong tam phương", "được dựa vào người quyền quý mà có chức tước", "support",
  ["career.status", "social.support"])
E("tt67_phu_bon_sat", "TT", 67, M, "Nam Mệnh Thiên Phủ ca", "Nếu Thiên Phủ bị Hỏa Linh Dương Đà vây hãm là người gian trá cuộc đời lận đận",
  "Mệnh có Thiên Phủ, hai trong Hỏa Linh Kình Đà trong tam phương", "dễ gian trá, cuộc đời lận đận", "limit", ["values.integrity", "life.hardship"])
E("tt67_phu_khong_kiep", "TT", 67, M, "Nam Mệnh Thiên Phủ ca", "Phủ bị Kiếp Không phá cũng không hay chỉ có thể hưởng phúc ở chốn thiền môn",
  "Mệnh có Thiên Phủ, Địa Không và Địa Kiếp đồng cung (verse 'Không Kiếp đồng viên')", "không hay, chỉ hưởng phúc nơi cửa thiền", "limit", ["spirit.unworldly"])
E("tt68_am_dau_tuat_hoi", "TT", 68, M, "Nam Mệnh Thái Âm ca", "ở Dậu Tuất Hợi là đắc địa sáng rực rỡ và tiếng tăm",
  "Mệnh ở Dậu/Tuất/Hợi có Thái Âm", "sáng rực rỡ, có tiếng tăm", "support", ["career.fame"])
E("tt68_am_mieu_quyen", "TT", 68, M, "Nam Mệnh Thái Âm ca", "bẩm tính ôn lương cung kiệm khiêm nhường",
  "Mệnh có Thái Âm miếu (bảng Toàn Thư) hóa Quyền (tuổi Mậu)", "bẩm tính ôn lương, cung kiệm, khiêm nhường; làm quan thanh hiển", "support", ["comm.gentle", "career.status"],
  notes="verse 'Thái Âm nhập miếu Hoá Quyền tinh': both conditions kept (the narrower reading)")
E("tt68_co_am_dan_xuong_khuc", "TT", 68, M, "Nam Mệnh Thái Âm ca", "dù có các sao tốt phù trợ cũng khó lòng",
  "Mệnh ở Dần có Thiên Cơ, Thái Âm và Văn Xương hoặc Văn Khúc", "dù có sao tốt phù trợ cũng khó làm nên cơ nghiệp", "limit", ["career.obstacle"],
  notes="'Thái Aâm tại Dần hội cùng Thiên Cơ, Xương Khúc dù có ...'; Xương and Khúc are together only at Sửu/Mùi, so at Dần one of them; the servant/prostitute clause is left out")
E("tt68_tham_tu_mo_hoa", "TT", 68, M, "Nam Mệnh Tham Lang ca", "nên hội với Hỏa Tinh tất oai",
  "Mệnh ở Thìn/Tuất/Sửu/Mùi có Tham Lang, Hỏa Tinh trong tam phương", "có oai quyền, danh tiếng lớn", "support", ["career.authority", "career.fame"],
  dup="TV_TH_CACH_MENH_THAM_HOA", notes="same cách as TH p.73 Tham Hỏa tương hội (formation rule); not made twice")
E("tt68_tham_kinh_da", "TT", 68, M, "Nam Mệnh Tham Lang ca", "Tham Lang thủ Mệnh đồng cung với Kình Dương thêm Đà Sát xâm lấn",
  "Tham Lang đồng cung Kình Dương, thêm Đà và sát", "khốn cùng", "limit", [], skip="Đà La never stands in the tam phương of a Kình palace (they flank Lộc Tồn): 'Đà Sát' cannot be read as printed")
E("tt68_vu_tham_liem_pha_kk", "TT", 68, M, "Nam Mệnh Tham Lang ca", "lại ngộ Liêm Trinh Phá Quân, Không Kiếp làm",
  "Mệnh có Vũ Khúc, Tham Lang; Liêm Trinh, Phá Quân và Không hoặc Kiếp trong tam phương", "nghề nào ra nghề nấy mà suốt đời vất vả", "limit", ["life.hardship"])
E("tt69_tham_tu_mo_ta_huu", "TT", 69, M, "Nam Mệnh Tham Lang ca", "Tham Lang cư tứ mộ địa gặp Tả Hữu sẽ thành phú ông",
  "Mệnh ở tứ mộ có Tham Lang, Tả Phụ và Hữu Bật đồng cung (verse 'Gia lâm Tả Hữu')", "thành phú ông", "support", ["fin.abundance"])
E("tt69_tham_tu_mo_tam_hoa", "TT", 69, M, "Nam Mệnh Tham Lang ca", "có được Khoa Quyền Lộc nữa thì tài năng văn võ đều đủ",
  "Mệnh ở tứ mộ có Tham Lang, Tả Hữu đồng cung, Khoa Quyền Lộc trong tam phương", "tài năng văn võ đều đủ", "support", ["exp.talent"])
E("tt69_cu_ty_ngo", "TT", 69, M, "Nam Mệnh Cự Môn ca", "Cự Môn ở Tí Ngọ hợp với mệnh cục thế nào cũng vinh hiển",
  "Mệnh Tý/Ngọ có Cự Môn", "vinh hiển", "support", [], dup="CACH_X_THACH_TRUNG_AN_NGOC", notes="the cách Thạch trung ẩn ngọc (formations_verified)")
E("tt69_cu_ham_hung", "TT", 69, M, "Nam Mệnh Cự Môn ca", "nếu ở hãm địa còn bị hung tinh phá phách càng thêm tai họa, tính tình thô lỗ",
  "Mệnh có Cự Môn hãm (bảng Toàn Thư), sát tinh trong tam phương", "càng thêm tai họa, tính tình thô lỗ", "limit", ["comm.friction"],
  notes="the injury clause that follows is left out")
E("tt69_cu_kinh_hoa_linh", "TT", 69, M, "Nam Mệnh Cự Môn ca", "Con người tính nóng nẩy điên đảo",
  "Mệnh có Cự Môn, Kình Dương và Hỏa Tinh hoặc Linh Tinh đồng cung", "mọi việc dễ thành bất tường, tính nóng nảy, điên đảo", "limit", ["temper.hot"])
E("tt69_tuong_ca_quyet", "TT", 69, M, "Nam Mệnh Thiên Tướng ca", "Thiên Tướng làm chủ Mệnh cung là người cả quyết tự chủ",
  "nam, Mệnh có Thiên Tướng", "là người quả quyết, tự chủ", "support", ["temper.assertive"])
E("tt69_tuong_vu_pha_sat", "TT", 69, M, "Nam Mệnh Thiên Tướng ca", "Thiên Tướng gặp Vũ Khúc, Phá Quân và Dương Đà, Linh Hỏa nếu không làm thợ, làm lái",
  "Mệnh có Thiên Tướng; Vũ Khúc, Phá Quân và hai trong Kình Đà Hỏa Linh trong tam phương", "nếu không làm thợ, làm lái buôn thì đi tu", "limit",
  ["exp.craft", "path.business"])
E("tt70_luong_ta_huu_xuong_khuc", "TT", 70, M, "Nam Mệnh Thiên Lương ca", "gặp thêm Tả Hữu, Xương Khúc làm quan, phú quí",
  "Mệnh có Thiên Lương; Tả Phụ, Hữu Bật, Văn Xương, Văn Khúc trong tam phương", "làm quan, phú quý", "support", ["career.status"])
E("tt70_luong_co_nhat_mieu", "TT", 70, M, "Nam Mệnh Thiên Lương ca", "Thái Dương, Văn Xương, Tả Hữu ở miếu địa Tí Ngọ Dần",
  "Mệnh ở Tý/Ngọ/Dần/Thân có Thiên Lương; Thiên Cơ, Thái Dương, Văn Xương, Tả Phụ, Hữu Bật trong tam phương", "quan tư thanh hiển", "support", ["career.status"],
  notes="'Thiên Lương ngộ Thiên Cơ, Thái Dương, Văn Xương, Tả Hữu ở miếu địa Tí Ngọ Dần Thân quan tư thanh hiển tới bậc tam công'")
E("tt70_luong_nhan_cung", "TT", 70, M, "Nam Mệnh Thiên Lương ca", "Thiên Lương ngộ Hỏa Tinh nơi nhàn cư",
  "Thiên Lương ở nhàn cung gặp Hỏa, Đà", "tật bệnh, phá nghiệp", "limit", [], skip="nhàn cung not defined on the page; illness")
E("tt70_co_luong_thin_tuat", "TT", 70, M, "Nam Mệnh Thiên Lương ca", "Hai sao Cơ Lương, đóng tại Thìn, Tuất và sao Phá Quân ở Mão Dậu đều xấu",
  "Cơ Lương Thìn Tuất; Phá Quân Mão Dậu", "đều xấu", "limit", [],
  skip="disputed: the verse 'Thìn Tuất Cơ Lương phi tiểu bổ' (非小補) is a good line in 紫微斗數全書 卷一 十二宮諸星得地富貴論, and TH p.72 lists Phá Quân Mão Dậu as a cách; recorded in schools.json instead of a rule")
E("tt71_sat_dan_than_ty_ngo_cat", "TT", 71, M, "Nam Mệnh Thất Sát ca", "thêm Khôi Việt, Tả Hữu tụ hội thì khoa lộc danh cao giàu sang phú quí",
  "Mệnh ở Dần/Thân/Tý/Ngọ có Thất Sát; Thiên Khôi, Thiên Việt, Tả Phụ, Hữu Bật trong tam phương", "danh cao, giàu sang phú quý", "support", ["career.fame", "fin.abundance"])
E("tt71_sat_ham", "TT", 71, M, "Nam Mệnh Thất Sát ca", "Thất Sát ở hãm địa hại vô tả, hung họa ví như ôm hổ dữ mà ngủ",
  "Mệnh có Thất Sát hãm (bảng Toàn Thư)", "hung họa nhiều, như ôm hổ mà ngủ", "limit", ["life.hardship"], notes="the death clause that follows is left out")
E("tt71_spt_mieu", "TT", 71, M, "Nam Mệnh Phá Quân ca", "Cả ba sao Phá Quân, Thất Sát, Tham Lang cư miếu địa hội tụ vào Mệnh cung tất là con",
  "Sát Phá Tham miếu hội Mệnh", "con người anh hùng", "support", [], dup="CACH_X_SAT_PHA_LIEM_THAM", notes="the cách Sát Phá Liêm Tham (formations_verified, TH p.76 thượng cách)")
E("tt71_pha_ty_ngo_xuong_ta_huu", "TT", 71, M, "Nam Mệnh Phá Quân ca", "Phá Quân đóng Tí Ngọ gặp Văn Xương có Tả Hữu thì tính tình khảng khái, tiền bạc đầy",
  "Mệnh Tý/Ngọ có Phá Quân; Văn Xương, Tả Phụ, Hữu Bật trong tam phương", "tính khảng khái, tiền bạc đầy kho", "support", ["fin.abundance"])
E("tt71_pha_doc_tam_hoa", "TT", 71, M, "Nam Mệnh Phá Quân ca", "Phá Quân đóng đơn độc không hay nhưng nếu có Khoa Quyền Lộc hội thì lại tốt dị thường",
  "Mệnh có Phá Quân đơn thủ (không chính tinh khác), Khoa Quyền Lộc trong tam phương", "lại tốt dị thường", "support", ["life.blessed", "career.success"])
E("tt71_pha_ham_sat", "TT", 71, M, "Nam Mệnh Phá Quân ca", "bị rơi vào hãm địa sẽ bỏ tổ nghiệp mà đi tha hương cầu thực",
  "Mệnh có Phá Quân hãm (bảng Toàn Thư), sát tinh trong tam phương (verse 'nhưng gia sát')", "bỏ tổ nghiệp mà đi tha hương lập thân", "limit", ["fortune.away"])
E("tt72_xuong_vuong", "TT", 72, M, "Nam Mệnh Văn Xương ca", "chí lớn tài cao, văn học tinh thông",
  "Mệnh có Văn Xương ở miếu, vượng (bảng Toàn Thư)", "chí lớn, tài cao, văn học tinh thông", "support", ["exp.letters", "amb.drive"])
E("tt72_xuong_ky", "TT", 72, M, "Nam Mệnh Văn Xương ca", "Văn Xương ngộ Hoá Kị có thể bị thương hoặc chết non yểu",
  "Văn Xương gặp Hóa Kỵ", "thương tích, yểu", "limit", [], skip="injury and death")
E("tt72_khuc_ky_hoa", "TT", 72, M, "Nam Mệnh Văn Khúc ca", "Văn Khúc thủ Mệnh ngộ Hoá Kị, Hỏa Tinh là người biện thuyết tài giỏi",
  "Mệnh có Văn Khúc, Hóa Kỵ và Hỏa Tinh đồng cung", "là người biện thuyết tài giỏi", "support", ["comm.persuasive"])
E("tt72_khuc_ac_tinh", "TT", 72, M, "Nam Mệnh Văn Khúc ca", "nên có ác tinh xung phá nữa mới hay",
  "Văn Khúc + ác tinh tam phương", "?", "limit", [], skip="the translation contradicts itself and the verse ('bất hỉ tam phương ác sát tụ'): not settled")
E("tt72_ta_phu_don_hau", "TT", 72, M, "Nam Mệnh Tả Phụ ca", "Sao Tả Phụ có thể giáng phúc là người đôn hậu thông kim cổ",
  "nam, Mệnh có Tả Phụ", "là người đôn hậu, hiểu biết rộng", "support", ["values.kind"])
E("tt72_ta_phu_bon_sat", "TT", 72, M, "Nam Mệnh Tả Phụ ca", "Tam phương Dương Đà Hỏa Linh chiếu, dù tiền nhiều chức trọng cũng không bền",
  "Mệnh có Tả Phụ, hai trong Kình Đà Hỏa Linh trong tam phương", "dù tiền nhiều, chức trọng cũng không bền", "limit", ["fortune.brief_luck"])
E("tt72_ta_phu_tu_phu_tham_vu", "TT", 72, M, "Nam Mệnh Tả Phụ ca", "nếu hội cùng Tử Vi, Thiên",
  "Tả Phụ hội Tử, Phủ, Lộc Quyền, Tham Vũ", "văn võ đều hiển quý", "support", [], skip="Tử Phủ and Tham Vũ do not stand in one tam phương together on any chart; which of them must meet is not stated")
E("tt73_huu_bat_co_muu", "TT", 73, M, "Nam Mệnh Hữu Bật ca", "Hữu Bật là người có cơ mưu, thông minh, bệ vệ",
  "nam, Mệnh có Hữu Bật", "người có cơ mưu, thông minh", "support", ["cog.sharp"])
E("tt73_huu_bat_cat_khong_sat", "TT", 73, M, "Nam Mệnh Hữu Bật ca", "lại được cát tinh phù trợ thì tiền tài, danh vọng dễ tìm",
  "Mệnh có Hữu Bật, tam phương không có Hỏa Tinh, Hóa Kỵ, Kình Dương, Đà La mà có cát tinh", "tiền tài, danh vọng dễ tìm", "support", ["fin.abundance", "career.success"],
  notes="'Nếu không bị Hỏa Kị, Dương Đà xung phá lại được cát tinh phù trợ thì tiền tài, danh vọng dễ tìm'")
E("tt73_loc_ton_qua_quyet", "TT", 73, M, "Nam Mệnh Lộc Tồn ca", "tính tình quả quyết làm việc gì cũng thành",
  "nam, Mệnh có Lộc Tồn", "tính quả quyết, làm việc gì cũng thành", "support", ["temper.assertive", "career.success"])
E("tt73_loc_ton_xuong_khuc", "TT", 73, M, "Nam Mệnh Lộc Tồn ca", "có thêm Xương Khúc hội tụ thì y lộc, nhà cao cửa rộng mãi mãi",
  "Mệnh có Lộc Tồn; Văn Xương, Văn Khúc trong tam phương", "y lộc đầy đủ, nhà cao cửa rộng", "support", ["prop.rich", "fin.abundance"])
E("tt73_loc_ton_co_kk_ky", "TT", 73, M, "Nam Mệnh Lộc Tồn ca", "Lộc Tồn rất sợ sao Thiên Cơ với Kiếp Không",
  "Mệnh có Lộc Tồn; Thiên Cơ, Hóa Kỵ và Không hoặc Kiếp trong tam phương (verse 'Thiên Cơ Kiếp Không Kị tương hội')", "chỉ nên tìm sự thanh nhàn nơi cửa chùa",
  "limit", ["spirit.unworldly"])
E("tt73_khoi_viet_han", "TT", 73, M, "Khôi Việt nhập Mệnh ca", "Khôi Việt ở Mệnh Thân đáo hạn gặp Văn Xương",
  "Khôi Việt Mệnh, hạn gặp Văn Xương", "năm ấy lên chức", "support", [], skip="a reading of a hạn year (vận hạn), not of the natal Mệnh")
E("tt74_kinh_cung_ran", "TT", 74, M, "Nam Mệnh Kình Dương ca", "Sao Kinh Dương thủ mệnh tính nết cứng rắn",
  "nam, Mệnh có Kình Dương", "tính nết cứng rắn", "limit", ["temper.headstrong"])
E("tt74_kinh_tu_mo_tu_phu", "TT", 74, M, "Nam Mệnh Kình Dương ca", "lại có tử phụ hội hợp tiền tài thóc gạo đầy kho",
  "Mệnh ở Thìn/Tuất/Sửu/Mùi có Kình Dương; Tử Vi, Thiên Phủ trong tam phương", "tiền tài, thóc gạo đầy kho", "support", ["fin.abundance"],
  notes="the clause before ('số mới thọ') is left out (longevity)")
E("tt74_da_tu_mo_tu_phu", "TT", 74, M, "Nam Mệnh Đà La ca", "Đà La thủ Mệnh tối hỉ tứ mộ địa, có Tử Vi thiên phủ hội hợp, tiền tài danh vọng đều hay",
  "Mệnh ở Thìn/Tuất/Sửu/Mùi có Đà La; Tử Vi, Thiên Phủ trong tam phương", "tiền tài, danh vọng đều hay", "support", ["fin.abundance", "career.fame"])
E("tt74_da_ham", "TT", 74, M, "Nam Mệnh Đà La ca", "Đà La ở hãm địa dễ bị vướng vào thị phi khẩu thiệt",
  "Mệnh có Đà La hãm (bảng Toàn Thư)", "dễ vướng thị phi khẩu thiệt, tiền mất người xa, làm gì cũng khó toại ý", "limit", ["comm.friction", "life.hardship"])
E("tt74_hoa_linh_mieu", "TT", 74, M, "Nam Mệnh Hỏa Linh ca", "rất cần có Tham Lang, Tử Vi, Thiên Phủ hội tụ",
  "Hỏa Linh miếu + Tham, Tử, Phủ", "uy quyền", "support", [], skip="which of Tham Lang, Tử Vi, Thiên Phủ must meet is not settled (all three is rare in one tam phương)")
E("tt74_thien_khong", "TT", 74, M, "Thiên Không Địa Kiếp nhập Mệnh ca", "Mệnh toạ Thiên Không định xuất gia",
  "Mệnh có 'Thiên Không' (天空)", "số xuất gia", "limit", [], skip="天空 of the Chinese verse is the Địa Không of Vietnamese charts, while the engine's Thiên Không is the Thái Tuế-circle star: which star is meant is not settled")
E("tt75_hoa_loc_menh", "TT", 75, M, "Hoá Lộc nhập Mệnh ca", "đàn ông có Hoá Lộc ở Mệnh tự nhiên phúc tới",
  "nam, Mệnh có Hóa Lộc", "tự nhiên có phúc; theo võ nổi danh, theo văn có tiếng", "support", ["life.blessed", "career.fame"])
E("tt75_loc_dong_nhat", "TT", 75, M, "Hoá Lộc nhập Mệnh ca", "Thiên Đồng gặp Thái Dương, dân giả cũng trở thành đại phú",
  "Mệnh có Thiên Đồng hóa Lộc (tuổi Bính), Thái Dương trong tam phương", "người bình thường cũng thành đại phú, nhà cửa ruộng vườn hưng vượng", "support", ["fin.abundance", "prop.rich"],
  notes="verse 'Lộc chủ Thiên Đồng ngộ Thái Dương': Hóa Lộc is on Thiên Đồng only in Bính years")
E("tt75_hoa_quyen_cat", "TT", 75, M, "Nam Mệnh Hoá Quyền ca", "Sao Hoá Quyền cần được các sao tốt phù trợ thì sự nghiệp hiên ngang",
  "Mệnh có Hóa Quyền, cát tinh trong tam phương", "sự nghiệp hiên ngang, đảm lượng hơn người", "support", ["career.success", "temper.assertive"])
E("tt75_hoa_quyen_cu_vu", "TT", 75, M, "Nam Mệnh Hoá Quyền ca", "Hội với Cự Môn, Vũ Khúc thì trấn thủ biên cương, nắm quyền vạn binh",
  "Mệnh có Hóa Quyền; Cự Môn, Vũ Khúc trong tam phương", "nắm quyền lớn, có thể theo võ nghiệp", "support", ["career.authority", "exp.martial"])
E("tt76_hoa_khoa_van", "TT", 76, M, "Nam Mệnh Hoá Khoa ca", "thủ Mệnh cung là người văn chương cẩm tú",
  "Mệnh có Hóa Khoa", "văn chương giỏi, thi cử hanh thông", "support", ["exp.letters"], notes="'Sao Hoá Khoa là văn tinh, thủ Mệnh cung là người văn chương cẩm tú'")
E("tt76_hoa_khoa_xk_kv", "TT", 76, M, "Nam Mệnh Hoá Khoa ca", "hội với Xương Khúc, Khôi Việt công danh sáng lạng",
  "Mệnh có Hóa Khoa; Văn Xương, Văn Khúc, Thiên Khôi, Thiên Việt trong tam phương", "công danh sáng lạng", "support", ["career.fame"])
E("tt76_hoa_ky_hung", "TT", 76, M, "Nam Mệnh Hoá Kị ca", "Gặp nó rồi lại bị thêm các hung tinh thì càng hung",
  "Mệnh có Hóa Kỵ, sát tinh trong tam phương", "càng thêm hung", "limit", ["life.hardship"])
E("tt76_hoa_ky_cat_lo", "TT", 76, M, "Nam Mệnh Hoá Kị ca", "cái giàu sang đó thường đi kèm với nhiều lo lắng",
  "Mệnh có Hóa Kỵ, cát tinh trong tam phương", "dù có cát tinh trợ cứu mà giàu sang thì giàu sang ấy đi kèm nhiều lo lắng", "limit", ["inner.unrest"])
E("tt76_tham_pha_ham_ky", "TT", 76, M, "Nam Mệnh Hoá Kị ca", "Hai sao Tham Lang, Phá Quân cư hãm địa dù có Hoá Kị đắc địa cũng bất lợi",
  "Mệnh có Tham Lang hoặc Phá Quân hãm (bảng Toàn Thư), Hóa Kỵ đồng cung", "bất lợi", "limit", ["life.hardship"], notes="the theft / prostitution clause after it is left out")
E("tt76_thai_tue", "TT", 76, M, "Thái Tuế nhập Mệnh ca", "người chức vị thường gặp lắm chuyện phù trầm",
  "Thái Tuế ...", "phù trầm", "limit", [], skip="the translation ('có nhật hạn hoặc đóng cung Quan hãm địa') does not give a natal condition")
E("tt76_hong_loan_bat_toa", "TT", 76, M, "Phú đoán Thân Mệnh a)", "Hồng Loan Bát Toạ ở minh không sai",
  "Mệnh có Hồng Loan và Bát Tọa", "công danh từ khi còn trẻ", "support", ["career.early"], notes="'Những người niên thiếu công danh / Hồng Loan Bát Toạ ở minh không sai'")
E("tt76_phu_khong_xu", "TT", 76, M, "Phú đoán Thân Mệnh b)", "Phủ phùng Không xứ tài suy",
  "Thiên Phủ gặp 'Không'", "tài suy", "limit", [], skip="'Không' (Tuần, Triệt or Địa Không) is not named")
E("tt76_nhat_nguyet_suu_mui", "TT", 76, M, "Phú đoán Thân Mệnh c)", "Chỉ vì Nhật Nguyệt đồng cung Sửu Mùi",
  "Mệnh Sửu/Mùi có Nhật Nguyệt đồng cung", "công danh không hiển", "limit", [],
  skip="contradicts TH p.72 (cách Nhật Nguyệt đồng cung); recorded in schools.json instead of a rule")
E("tt76_long_phuong_mao_dau", "TT", 76, M, "Phú đoán Thân Mệnh d)", "Phượng Long Mão Dậu đôi miền",
  "Mệnh ở Mão/Dậu có Long Trì, Phượng Các", "thi cử đỗ cao, danh đứng đầu", "support", ["exp.letters", "career.fame"],
  notes="next line 'Vượng thì kim bảng ghi tên hàng đầu'; Long Trì and Phượng Các stand together only at Mão/Dậu")
E("tt76_giap_liem_sat", "TT", 76, M, "Phú đoán Thân Mệnh e)", "Giáp Liêm giáp Sát một hào không sai",
  "Mệnh giáp Liêm Trinh và Thất Sát (hai cung kề)", "công danh phải đợi tuổi cao", "limit", ["career.late"], notes="'Công danh đợi tuổi tác cao / Giáp Liêm giáp Sát một hào không sai'")
E("tt76_kinh_da_menh", "TT", 76, M, "Phú đoán Thân Mệnh f)", "Nói năng loạn thuyết những phường điêu ngoa",
  "Mệnh có Kình Dương hoặc Đà La", "nói năng hay loạn thuyết, điêu ngoa", "limit", ["comm.friction"], notes="'Dương Đà xâm chiếm Mệnh viên': the two are never in one palace, so either one")
E("tt76_tham_liem_ty_hoi", "TT", 76, M, "Phú đoán Thân Mệnh g)", "Tham Liêm Tị Hợi không bàn",
  "Tham Liêm Tỵ Hợi", "ngục hình", "limit", [], skip="prison")
