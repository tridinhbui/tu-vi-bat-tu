page("KL", 155, "Hóa lộc/Hóa khoa/Hóa quyền: no Tử/Bào/Tật lines. 'Hóa khoa cứu giải bệnh tất' is the same sentence as existing star_nature hoa_khoa.che_sat (p.155) — not re-recorded.")
page("KL", 156, "Hóa kỵ ở các cung: Bào heading (Phối continues on p.157). Text layer in order.")
page("KL", 157, "Hóa kỵ ở các cung: Tử heading (no Tật). Text layer in order.")
E("kl156_bao_hoa_ky", "KL", 156, "Huynh Đệ", "Hóa kỵ ở các cung — Bào",
  "Anh em xung khắc.", "Anh em xung khắc",
  "Hóa Kỵ ở Huynh Đệ", C(own_stars=["Hóa Kỵ"]),
  "Hóa Kỵ ở Huynh Đệ thì anh em xung khắc, không hợp nhau", "limit", ["kin.strain"],
  notes="'xung khắc' = clash/không hợp, not the fatal 'khắc' of the skip list. Close to TH p.100 draft TV_TH_P2_HUYNH_DE_PHA_KY (Phá Quân, Hóa Kỵ: anh em bất thuận); KL needs Hóa Kỵ only.")
E("kl157_tu_hoa_ky", "KL", 157, "Tử Tức", "Hóa kỵ ở các cung — Tử",
  "- Cha mẹ xung khắc con cái.", "Cha mẹ xung khắc con cái",
  "Hóa Kỵ ở Tử Tức", C(own_stars=["Hóa Kỵ"]),
  "Hóa Kỵ ở Tử Tức thì cha mẹ và con cái xung khắc, không hợp nhau", "limit", ["kin.strain", "NEW:kin.children_strain"],
  notes="'xung khắc' = clash, not the fatal 'khắc'.")
N("kl156_hoa_ky_do_ky", "star_nature", "Hóa Kỵ", "", "KL", 156,
  "Hóa kỵ là sao Thủy, chủ đố kỵ, ghen ghét, dèm pha",
  "Hóa kỵ là sao Thủy, chủ đố kỵ, ghen ghét, dèm pha. Tính nết: hay gây phiền nhiễu, ích kỷ, ghen tuông.",
  "Hóa Kỵ chủ đố kỵ, ghen ghét, dèm pha", ["siblings", "children", "health"], "-",
  ["kin.strain", "NEW:health.exposed"],
  notes="WHY for Hóa Kỵ lines in Bào/Tử (xung khắc) and for KL p.218 'Tối kỵ cho cung Tật khi có … Hóa kỵ'.")
