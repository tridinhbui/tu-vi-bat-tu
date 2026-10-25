family("th")
# ---------------------------------------------------------------- TH pp.79-81 (images read: the text layer cuts the two-column verse into fragments)
page("TH", 79, "VI. Luận về sao cung Mệnh (7 rules of ngũ hành sinh khắc between palace, star and Mệnh); Ngũ hành sở thuộc tính tinh (verse: Kim, Mộc, Thủy, Thổ).")
page("TH", 80, "Ngũ hành sở thuộc (Thổ end, Hỏa); HÀNH CỦA NAM BẮC TINH (8 lines); Cung các sao đắc địa (= 紫微斗數全書 得地富貴論).")
page("TH", 81, "Đắc địa (end); 12 cung các sao lục hãm (= 失陷貧賤論); Hạn hành đắc số lệ (heading).")
NB = "Hành của Nam Bắc tinh"


def H(id, quote, stars, hanh, notes=""):
    E(id, "TH", 80, "", NB, quote, ", ".join(stars), f"thuộc hành {hanh}", "neutral", [], stars=stars, hanh=hanh, target="star_nature", notes=notes)


H("th80_hanh_tho_1", "Tử vi, Tả phụ, Lộc Tồn : Thổ", ["Tử Vi", "Tả Phụ", "Lộc Tồn"], "Thổ")
H("th80_hanh_kim_1", "ũ Khúc, Đà La, Dương nhận : Kim", ["Vũ Khúc", "Đà La", "Kình Dương"], "Kim", notes="the text layer drops the 'V' of 'Vũ' onto its own line")
H("th80_hanh_thuy_1", "Phá, Bật, Cự, Tham, Văn Khúc: T", ["Phá Quân", "Hữu Bật", "Cự Môn", "Tham Lang", "Văn Khúc"], "Thủy", notes="image: '... Văn Khúc: Thủy'")
H("th80_hanh_hoa_liem", "Hỏa thuộc Liêm Trinh, Bắc đẩu tinh", ["Liêm Trinh"], "Hỏa")
H("th80_hanh_tho_2", "Thiên phủ, Thiên Lương: Thổ hữu t", ["Thiên Phủ", "Thiên Lương"], "Thổ", notes="image: 'Thổ hữu tình'; TT p.119 phú nôm calls Thiên Lương 'Mộc chủ thọ tinh': schools.json")
H("th80_hanh_thuy_2", "Thiên Đồng, Thiên Tướng: Thủy tuy", ["Thiên Đồng", "Thiên Tướng"], "Thủy")
H("th80_hanh_kim_2", "Xương, Sát thuộc Kim, Thiên Cơ: M", ["Văn Xương", "Thất Sát"], "Kim",
  notes="the verse on p.80 (Ngũ hành sở thuộc) puts Thất Sát under HỎA ('Thái Dương cung lò Thất Sát'): TH is at odds with itself; schools.json")
H("th80_hanh_moc_co", "Xương, Sát thuộc Kim, Thiên Cơ: M", ["Thiên Cơ"], "Mộc", notes="image: 'Thiên Cơ: Mộc'")
H("th80_hanh_hoa_2", "Hỏa Linh, Khôi Việt: Hỏa nam tính", ["Hỏa Tinh", "Linh Tinh", "Thiên Khôi", "Thiên Việt"], "Hỏa")
E("th80_hanh_hoa_thai_duong", "TH", 80, "", "Ngũ hành sở thuộc tính tinh", "Thái Dương cung lò Thất Sa", "Thái Dương", "thuộc hành Hỏa", "neutral", [],
  stars=["Thái Dương"], hanh="Hỏa", target="star_nature", notes="image: 'HỎA: Thái Dương cung lò Thất Sát'")
E("th79_lac_ham_ngu_hanh", "TH", 79, "", "VI. Luận về sao cung Mệnh", "hành của sung khắc hành của Sao là lạc hãm",
  "hành của cung khắc hành của sao", "là lạc hãm", "limit", [], target="schools",
  notes="'2. Lạc hãm: Khi nào xem hành của sung (cung) khắc hành của Sao là lạc hãm' — TH defines lạc hãm by ngũ hành; KL pp.180, 185 reject that basis")
E("th79_lac_ham_tuan_triet", "TH", 79, "", "VI. Luận về sao cung Mệnh", "gặp Tuần Triệt nữa thì càng thêm xấu",
  "sao lạc hãm gặp Tuần, Triệt", "càng thêm xấu", "limit", [], target="che_hoa")
E("th79_lac_ham_chinh_tinh_sinh_cung", "TH", 79, "", "VI. Luận về sao cung Mệnh", "Trái lại nếu ở đó có một chính tinh nữa mà sanh",
  "sao lạc hãm, có chính tinh sinh được hành của cung", "trở thành đẹp", "support", [], target="che_hoa",
  notes="'... mà sanh được cung thì trở thành đẹp. Ví dụ sao Văn xương là Kim mà đóng ở cung Ngọ và Hỏa là lạc hãm, song nếu gặp chính tinh là Thiên cơ thuộc mộc đóng ở đó thì hóa tốt'")
E("th79_ham_hop_hanh_menh", "TH", 79, "", "VI. Luận về sao cung Mệnh", "Mệnh có sao hãm địa mà hợp được cới hành của Mệnh cũng trở thành khá hơn",
  "Mệnh có sao hãm mà hợp hành bản mệnh", "khá hơn; sao đắc địa mà không hợp hành Mệnh thì kém đi", "neutral", [], target="che_hoa")

# ---------------------------------------------------------------- TH pp.130-133 XIII. Ảnh hưởng sao nhập hạn (images read; the text layer is cut into
# fragments: each quote is the longest contiguous fragment of the line). Read on the đại hạn palace; 'sáng sủa' = miếu / vượng / đắc, 'mờ ám' = hãm;
# a 'gặp X' with no position is read in the hạn palace itself; a list of four stars that cannot share a palace is read in the tam phương.
page("TH", 130, "XIII. Ảnh hưởng sao nhập hạn: Tử Vi 1-6, Thiên Cơ 1-16, Thiên Phủ 1-2, Thái Âm 1-7.")
page("TH", 131, "Tham Lang, Thái Dương 1-6, Vũ Khúc 1-4, Thiên Đồng, Liêm Trinh 1-9, Cự Môn 1-2.")
page("TH", 132, "Cự Môn 3-7, Thiên Tướng 1-6, Thiên Lương 1-2, Thất Sát 1-8, Phá Quân 1-4.")
page("TH", 133, "Phá Quân 5-10; XIV. Luận đoán về hạn chết (not used: death).")
page("TH", 126, "XI. Liên hệ giữa Mệnh Thân và hạn (table): not mined in this batch, the cells are scrambled in the text layer.", img=True)
HN = "XIII. Ảnh hưởng sao nhập hạn"
B3 = ["miếu", "vượng", "đắc"]


def V(id, p, quote, cond, text, tone, **k):
    pol = {"pos": "support", "neg": "limit", "": "neutral"}[tone]
    E(id, "TH", p, "Đại hạn", HN, quote, json.dumps(cond, ensure_ascii=False), text, pol, [], cond=cond, tone=tone, target="van_han", **k)


V("th130_tu_vi_ty_hoi_mao_dau", 130, "Nhập hạn tai Tỵ Hợi Mão Dậu suy", {"major": "Tử Vi", "branch": ["Tỵ", "Hợi", "Mão", "Dậu"]},
  "hạn có Tử Vi ở Tỵ, Hợi, Mão, Dậu thì cái tốt giảm, có tai họa cũng khó giải", "neg")
V("th130_tu_vi_khoi_viet", 130, "Có Khôi Việt thêm danh giá, tranh chấp với ai cũng thắng lợi", {"major": "Tử Vi", "with_any": ["Thiên Khôi", "Thiên Việt"]},
  "hạn có Tử Vi gặp Khôi Việt thì thêm danh giá, tranh chấp với ai cũng thắng", "pos")
V("th130_tu_vi_phu_tuong_ta_huu_tam_hoa", 130, "6. Phủ Tướng Tả Hữu Tam Hóa: hoạnh phát danh tài",
  {"major": "Tử Vi", "tp_any": ["Thiên Phủ", "Thiên Tướng"], "tp_all": ["Tả Phụ", "Hữu Bật"], "hoa3": True},
  "hạn có Tử Vi gặp Phủ Tướng, Tả Hữu và Tam Hóa thì hoạnh phát về danh và tiền", "pos",
  notes="read in the tam phương: Tả Hữu and the three Hóa cannot all stand in one palace with Tử Vi; Hóa read on the hạn's own stem (as TT p.105)")
V("th130_co_sang", 130, "1. Sáng sảu hoạch phát", {"major": "Thiên Cơ", "dig": B3}, "hạn có Thiên Cơ sáng sủa thì hoạnh phát", "pos")
V("th130_co_loc", 130, "Gặp lộc cùng phát", {"major": "Thiên Cơ", "with_any": ["Lộc Tồn"]}, "hạn có Thiên Cơ gặp Lộc thì cùng phát", "pos",
  notes="'Lộc' read as Lộc Tồn (the narrower reading; Hóa Lộc of the hạn stem is a second reading left out)")
V("th130_co_mo", 130, "Mờ ám bị phiền toái thị ph", {"major": "Thiên Cơ", "dig": ["hãm"]}, "hạn có Thiên Cơ mờ ám thì bị phiền toái, thị phi", "neg",
  notes="the death clause of the same item is left out")
V("th130_co_qua_tu", 130, "Quả Tú: túng thiếu", {"major": "Thiên Cơ", "with_any": ["Quả Tú"]}, "hạn có Thiên Cơ gặp Quả Tú thì túng thiếu", "neg",
  notes="the starvation clause is left out")
V("th130_co_kinh_da", 130, "ặp rủi ro, đầy lo lắng", {"major": "Thiên Cơ", "with_any": ["Kình Dương", "Đà La"]}, "hạn có Thiên Cơ gặp Kình hoặc Đà thì hay gặp rủi ro, lo lắng",
  "neg", notes="image: '15. Gặp Kình Đà hay gặp rủi ro, đầy lo lắng'")
V("th130_am_sang", 130, "tài lộc phong túc, thường tậu được nhà, có nhiều hỷ sự trong gia đình", {"major": "Thái Âm", "dig": B3},
  "hạn có Thái Âm sáng sủa thì tài lộc dồi dào, thường tậu được nhà, nhà có nhiều việc vui", "pos")
V("th130_am_mo", 130, "Mờ ám: hao tán", {"major": "Thái Âm", "dig": ["hãm"]}, "hạn có Thái Âm mờ ám thì hao tán", "neg", notes="the health clauses are left out")
V("th131_tham_sang", 131, "1. Sáng sủa tốt đẹp hanh thông. Nếu ở Tứ Mộ hợp với tuổi Tứ Mộ càng hiển hách phát đạt", {"major": "Tham Lang", "dig": B3},
  "hạn có Tham Lang sáng sủa thì tốt đẹp hanh thông (ở Tứ mộ hợp tuổi Tứ mộ càng hiển hách)", "pos")
V("th131_nhat_sang", 131, "Sáng sủa: phát danh tài", {"major": "Thái Dương", "dig": B3}, "hạn có Thái Dương sáng sủa thì phát danh tài", "pos")
V("th131_vu_sang", 131, "Sáng sủa tốt đẹp, tài lộc hư", {"major": "Vũ Khúc", "dig": B3}, "hạn có Vũ Khúc sáng sủa thì tài lộc hưng vượng", "pos")
V("th131_vu_xuong_khuc_ta_huu", 131, "2. Gặp Tả Hữu Xương Khúc: tài quan song mỹ", {"major": "Vũ Khúc", "tp_all": ["Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc"]},
  "hạn có Vũ Khúc gặp Tả Hữu Xương Khúc thì tiền và chức đều tốt", "pos", notes="four stars: read in the tam phương")
V("th131_vu_mo", 131, "4. Mờ ám thì hao tán tiền tài, giáng quan chức", {"major": "Vũ Khúc", "dig": ["hãm"]}, "hạn có Vũ Khúc mờ ám thì hao tán tiền tài, dễ bị giáng chức",
  "neg")
V("th131_dong_thay_doi", 131, "Sáng sủa hay mờ ám đều thay đổi chổ ở hoặc công việc làm", {"major": "Thiên Đồng"}, "hạn có Thiên Đồng thì thay đổi chỗ ở hoặc công việc", "")
V("th131_dong_sang", 131, "Sáng sủa: Hưng vượng, trong nhà có việc vui", {"major": "Thiên Đồng", "dig": B3}, "hạn có Thiên Đồng sáng sủa thì hưng vượng, nhà có việc vui",
  "pos")
V("th131_dong_mo", 131, "Mờ am: mọi việc trước hanh thông, xau bế tắc, hao tán bị bãi quan chức", {"major": "Thiên Đồng", "dig": ["hãm"]},
  "hạn có Thiên Đồng mờ ám thì việc trước thông sau tắc, hao tán, dễ mất chức", "neg")
V("th131_liem_sang_cat", 131, "1. Sáng sủa gặp được sao tốt, danh tại toại mỹ", {"major": "Liêm Trinh", "dig": B3, "tp_cat": True},
  "hạn có Liêm Trinh sáng sủa gặp sao tốt thì danh và tiền toại ý", "pos")
V("th131_liem_ty_hoi", 131, "2. Ơû Tỵ Hợi giao dịch với người lạ bất lợi", {"major": "Liêm Trinh", "branch": ["Tỵ", "Hợi"]},
  "hạn có Liêm Trinh ở Tỵ, Hợi thì giao dịch với người lạ bất lợi, dễ sinh hiềm thù", "neg", notes="the prison clause is left out")
V("th131_liem_mo", 131, "3. Mờ ám: chơi bời đến mang họa. Nếu có công danh dễ bị trất giáng", {"major": "Liêm Trinh", "dig": ["hãm"]},
  "hạn có Liêm Trinh mờ ám thì chơi bời mang họa, có chức dễ bị giáng", "neg")
V("th131_liem_vu_loc_ma", 131, "4. Gặp Vũ Lộc Mã có danh tài", {"major": "Liêm Trinh", "tp_all": ["Vũ Khúc", "Lộc Tồn", "Thiên Mã"]},
  "hạn có Liêm Trinh gặp Vũ Khúc, Lộc, Mã thì có danh tài", "pos", notes="Vũ Khúc never shares a palace with Liêm Trinh: read in the tam phương; 'Lộc' as Lộc Tồn")
V("th131_liem_khong_kiep", 131, "8. Gặp Không Kiếp mọi sự bế t", {"major": "Liêm Trinh", "with_any": ["Địa Không", "Địa Kiếp"]},
  "hạn có Liêm Trinh gặp Không, Kiếp thì mọi sự bế tắc, hao tài", "neg", notes="image: Liêm Trinh item 8 (the fragment sits among the Thiên Đồng lines in the text layer)")
V("th132_tuong_sang", 132, "hoạnh phát bất ng", {"major": "Thiên Tướng", "dig": B3}, "hạn có Thiên Tướng sáng sủa thì mưu sự dễ thành, hoạnh phát bất ngờ", "pos",
  notes="image: '1. Sáng sủa: mưu sự dễ thành, hoạnh phát bất ngờ'")
V("th132_tuong_kk", 132, "iếp: bị tiểu nhân lừa lọc nhưng không đáng ng", {"major": "Thiên Tướng", "with_any": ["Địa Không", "Địa Kiếp"]},
  "hạn có Thiên Tướng gặp Không, Kiếp thì bị tiểu nhân lừa lọc nhưng không đáng ngại", "neg")
V("th132_luong_mo", 132, "2. Mờ ám: hao tán sức khoẻ và tiền tài", {"major": "Thiên Lương", "dig": ["hãm"]}, "hạn có Thiên Lương mờ ám thì hao tán tiền tài", "neg",
  notes="the health half is left out")
V("th132_luong_ty_hoi", 132, "nếu gặp Lương nhập hạn ở Tí Hợi chắc c", {"major": "Thiên Lương", "branch": ["Tý", "Hợi"]},
  "hạn có Thiên Lương ở Tý, Hợi thì chắc chắn đi xa hoặc thay đổi công việc", "", notes="image: '... chắc chắn đi xa hay thay đổi công việc'")
V("th132_sat_dan_than", 132, "Nếu Sát nhập hạn ở Dần", {"major": "Thất Sát", "branch": ["Dần", "Thân"]}, "hạn có Thất Sát ở Dần, Thân thì tiền và chức đều tốt, mưu sự thành nhanh",
  "pos", notes="image: 'Nếu Sát nhập hạn ở Dần Thân thật là tài quan song mỹ, mưu sự thành nhanh chóng'")
V("th132_sat_mo", 132, "Gặp nhiều chuyện buồn", {"major": "Thất Sát", "dig": ["hãm"]}, "hạn có Thất Sát mờ ám thì gặp nhiều chuyện buồn", "neg",
  notes="the accident clause is left out")
V("th132_pha_sang_xk_kv", 132, "1. Sáng sủa mà gặp được thêm Xương Khúc K ôi Việt tài quan song mỹ, phú quí cực độ",
  {"major": "Phá Quân", "dig": B3, "tp_all": ["Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"]},
  "hạn có Phá Quân sáng sủa gặp Xương Khúc Khôi Việt thì tiền và chức đều tốt, rất phú quý", "pos", notes="four stars: read in the tam phương")
V("th133_pha_phuong", 133, "7. Gặp Phượng Các bị trách oán", {"major": "Phá Quân", "with_any": ["Phượng Các"]}, "hạn có Phá Quân gặp Phượng Các thì bị trách oán", "neg")
for _id, _p, _q, _why in [
    ("th130_tu_vi_tuan_triet", 130, "2. Đại Tiểu Hạn trùng phùng gặp Tuần Triệt tính mạng đáng lo ngại", "death"),
    ("th130_tu_vi_kinh_da_kiep_ky", 130, "5. Kình Đà Kiếp Kỵ : đau ốm, bị lừa", "illness (the 'bị lừa' half joined to it)"),
    ("th130_co_nguyet_dong_luong", 130, "3. Hội Nguyệt Đồng Lương Tả Hữu, sát tinh gặp thời làm quyền gian", "'gặp thời làm quyền gian' could be read for or against: not settled"),
    ("th130_co_khoc_hoa_kinh", 130, "8. Khốc Hỏa Kình : trong nhà có sự tranh chấp", "three stars in one palace, a condition the van_han_books vocabulary cannot state yet (with_all)"),
    ("th130_phu_tam_khong", 130, "1. Gặp Tam Không: phá sản", "'Tam Không' (which three Không) is not named"),
    ("th131_nhat_sat", 131, "mọi việc trắc trở", "'Hỏa Linh Kình Đà' as a group in one palace: the vocabulary has no 'two of these in the palace'"),
    ("th131_vu_quyen", 131, "3. Gặp thêm Quyền sẽ trọng trấn biên thuỳ", "TT p.98 (tt98_vu_khuc_quyen) already reads Vũ Khúc hóa Quyền in the hạn"),
    ("th131_liem_hong_dao", 131, "5. Gặp Hồng Đào thanh gia thất", "a marriage event"),
    ("th132_tuong_di_tuan_triet", 132, "6. Nếu nhập ha ở cung Thiên Di mà gặp Tuần Triệt dễ bị gi", "the hạn palace's name is not in the vocabulary; and the death clause"),
    ("th132_sat_liem_tham_phuong", 132, "4. Gặp Liêm Tham Phượng: dễ bị oán ách", "which of Liêm, Tham must meet Thất Sát is not settled"),
]:
    E(_id, "TH", _p, "Đại hạn", HN, _q, "", "", "limit", [], skip=_why, target="van_han")

family("scan")
# ---------------------------------------------------------------- Thiên Lương, Tử Vi Nghiệm Lý Toàn Thư, 21-page scan (no text layer): pp.13-15 transcribed
page("SCAN:tvnl_scan", 13, "Những câu phú nên thận trọng áp dụng (Phá Quân Thìn Tuất / Tham Sát Dần Thân).")
page("SCAN:tvnl_scan", 14, "Four tuổi with Mệnh at Tuất and Phá Quân: the phú read by tuổi and vòng Thái Tuế.")
page("SCAN:tvnl_scan", 15, "Hóa Khoa and Tuần Triệt on Sát Phá Tham.")
page("SCAN:tvnl_scan", 11, "Can chi gốc / ngọn (Canh Thân vs Canh Dần, Giáp Ngọ vs Giáp Tí): the same examples as KL p.209; not transcribed (schools.json cites KL).", img=True)
S = "SCAN:tvnl_scan"
E("tl13_phu_than_trong", S, 13, "Mệnh", "Những câu phú nên thận trọng áp dụng",
  "có phải bất cứ mệnh nào nằm ở Thìn Tuất mà có Phá Quân là trai bất nhân", "Phá Quân Thìn Tuất / Tham Sát Dần Thân",
  "câu phú không quyết định cho mọi trường hợp", "neutral", [], target="schools")
E("tl14_phu_theo_tuoi", S, 14, "Mệnh", "Những câu phú nên thận trọng áp dụng", "Bất nhân không thể là người Thái Tuế",
  "Mệnh Tuất có Phá Quân, tuổi Giáp Dần (Mệnh trong tam hợp Thái Tuế)", "không thể coi là bất nhân", "neutral", [], target="schools")
E("tl15_khoa_spt", S, 15, "", "Hóa Khoa và Sát Phá Tham", "Bộ Sát Phá Tham nói chung, hãm địa nói riêng, gặp Hóa Khoa như phe Triệt giáo",
  "Sát Phá Tham (nhất là hãm địa) gặp Hóa Khoa", "hung tinh ngộ chế, thành người hiền, hiệp khách", "support", [], target="che_hoa",
  notes="'... được đắc đạo. Hóa Khoa có một khả năng lột xác phàm phu hoán cải tư cách tức là trường hợp hung tinh ngộ chế'")
E("tl15_tuan_triet_spt", S, 15, "", "Hóa Khoa và Sát Phá Tham", "Sát Phá Tham gặp Tuần Triệt cũng mất tính cách hung hãn",
  "Sát Phá Tham gặp Tuần, Triệt", "mất tính hung hãn, nhưng mất hết (Triệt) hay giảm hẳn tốc lực (Tuần)", "neutral", [], target="che_hoa")
