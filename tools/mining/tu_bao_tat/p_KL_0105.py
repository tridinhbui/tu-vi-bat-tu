page("KL", 105, "Cự môn ở các cung: Tật and Tử headings (no Bào; p.104 has only Mệnh; p.106 Bài đọc thêm has nothing for these palaces). Text layer in order.")
E("kl105_tat_cu_ky_luu_ha", "KL", 105, "Tật Ách", "Cự môn ở các cung — Tật",
  "- Cự Kỵ, Lưu hà chết đuối", "Cự Kỵ, Lưu hà chết đuối",
  "Tật Ách có Cự Môn, Hóa Kỵ, Lưu Hà", C(own_stars=["Cự Môn", "Hóa Kỵ", "Lưu Hà"]),
  "(tai nạn chết đuối)", "limit", ["health.severe"], skip="death (drowning)")
E("kl105_tat_cu_kinh_da_hoa_linh", "KL", 105, "Tật Ách", "Cự môn ở các cung — Tật",
  "- Cự môn, Kình Đà, Hỏa Linh đồng cung bệnh do tửu sắc.", "Cự môn, Kình Đà, Hỏa Linh đồng cung bệnh do tửu sắc",
  "Tật Ách có Cự Môn đồng cung Kình Dương/Đà La, Hỏa/Linh",
  C(own_major=["Cự Môn"], own_stars=["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh"], other="đồng cung"),
  "(bệnh do rượu chè, sắc dục)", "limit", ["health.severe"], skip="illness attributed to drink and sex (disease + sexual reputation)")
E("kl105_tu_cu_co", "KL", 105, "Tử Tức", "Cự môn ở các cung — Tử",
  "- Cự môn, Thiên cơ: có con bị bào.", "Cự môn, Thiên cơ: có con bị bào",
  "Tử Tức có Cự Môn và Thiên Cơ", C(own_major=["Cự Môn", "Thiên Cơ"], other="Cự Cơ (đồng cung at Mão/Dậu)"),
  "Tử Tức có Cự Cơ thì có con khác mẹ hoặc khác cha (nếu 'bị bào' là 'dị bào')", "neutral", ["NEW:kin.half"], timing=True,
  notes="Wording 'có con bị bào' is unclear — most likely a misprint of 'dị bào' (cf. KL p.80 'Cự cơ đồng cung có anh em dị bào'). Family-composition event; treat as uncertain, caller may skip.")
