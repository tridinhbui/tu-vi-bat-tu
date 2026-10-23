page("KL", 55, "Phú đoán về sao Thiên phủ #2: 'Thiên phủ lâm giải ách nhi vô bệnh'. Text layer in order. (Phú section found by keyword scan of pp.30-74.)")
page("KL", 72, "Phú #37 'Hỏa Linh hãm ư Tử tức, đáo lão vô nhi khốc' → skip (childlessness / funeral).")
page("KL", 73, "Phú #46 Thiên hỷ ở Tử tức (women); #48 Ách địa Thai phùng Bạch hổ → skip (named condition).")
E("kl55_tat_thien_phu", "KL", 55, "Tật Ách", "Phú đoán về sao Thiên phủ — 2. Thiên phủ lâm giải ách nhi vô bệnh",
  "2 . Thiên phủ lâm giải ách nhi vô bệnh, Địa kiếp lâm Phúc đức nhi hữu tai — Thiên phủ ở cung Ách thì không đau bệnh gì.",
  "Thiên phủ ở cung Ách thì không đau bệnh gì",
  "Thiên Phủ ở Tật Ách", C(own_major=["Thiên Phủ"]),
  "Thiên Phủ ở Tật Ách thì không đau bệnh gì đáng kể", "support", ["well.health", "NEW:health.few_ills"],
  notes="Phú verse + KL gloss. Consistent with KL p.96 'Thiên phủ là giải tai ách chi tinh'. Paraphrase softened from 'không đau bệnh gì' to avoid an absolute health promise.")
E("kl72_tu_hoa_linh_ham", "KL", 72, "Tử Tức", "Phú — 37. Hỏa Linh hãm ư Tử tức, đáo lão vô nhi khốc",
  "Hỏa Kinh đóng ở cung Tử tức thì về già cũng không có con khóc đưa đám.",
  "đóng ở cung Tử tức thì về già cũng không có con khóc đưa đám",
  "Hỏa Tinh, Linh Tinh hãm địa ở Tử Tức", C(own_stars=["Hỏa Tinh", "Linh Tinh"], other="hãm (verse: 'Hỏa Linh hãm'); gloss misprints 'Hỏa Kinh'"),
  "(về già không có con)", "limit", ["kin.few"], skip="childlessness + funeral imagery")
E("kl73_tu_thien_hy_nhat_nguyet", "KL", 73, "Tử Tức", "Phú — 46. Sở hỷ giả Thiên hỷ nhị minh phù tử tức chi cung",
  "Sở hỷ giả Thiên hỷ nhị minh phù tử tức chi cung: Cung tử tức có Thiên hỷ gặp Nhật Nguyệt hội chiếu, đàn bà có con quí tử.",
  "Cung tử tức có Thiên hỷ gặp Nhật Nguyệt hội chiếu, đàn bà có con quí tử",
  "Tử Tức có Thiên Hỷ, được Thái Dương, Thái Âm hội chiếu; đương số là nữ",
  C(own_stars=["Thiên Hỷ"], tam=["Thái Dương", "Thái Âm"], other="female chart only ('đàn bà'); 'hội chiếu' = Nhật and Nguyệt in tam phương/xung chiếu of Tử Tức; verse 'nhị minh' = the two luminaries (brightness not stated)"),
  "nữ mệnh có Thiên Hỷ ở Tử Tức, được Nhật Nguyệt hội chiếu thì có con quý", "support", ["NEW:kin.prosper", "NEW:kin.talented"],
  notes="Gender-conditioned line.")
