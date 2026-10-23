page("KL", 160, "Vòng Trường sinh: Trường sinh nature 'tốt cho sinh đẻ'. (Beyond the pp.63-155 star range, found by keyword scan.)")
page("KL", 161, "Trường sinh ở các cung (Tật exception) + Mộc dục ở các cung (Tử). Text layer in order.")
page("KL", 162, "Đế vượng nature (giải bệnh, lợi sinh nở); Suy 'Ở Tử thì hiếm con'; Bệnh ở các cung — 'Bệnh Phá: ít con' is under the MỆNH heading (so the p.138 nature kl138_benh_pha_it_con is a Mệnh condition, not Tử Tức).")
p160n = None
N("kl160_truong_sinh_sinh_de", "star_nature", "Trường Sinh", "Tử Tức", "KL", 160,
  "tốt cho sinh đẻ",
  "Tượng trưng cho: bền vững, nhân từ, bác ái, sống lây, tuổi trẻ, tốt cho sinh đẻ.",
  "Trường Sinh tượng trưng cho bền vững, nhân từ, sống lâu, tuổi trẻ, tốt cho sinh đẻ", ["children", "health"], "+",
  ["NEW:kin.easy_children", "well.longevity"],
  notes="WHY for KL p.218 listing Tràng sinh among 'dễ sinh con' stars. 'sống lây' = page misprint for 'sống lâu'.")
E("kl161_tat_truong_sinh_sao_xau", "KL", 161, "Tật Ách", "Trường sinh ở các cung",
  "- Chỉ trừ cung Tật khi gặp sao xấu thì bệnh lâu khỏi, còn ở các cung khác, Trường sinh mang lại phúc thọ tài lộc.",
  "Chỉ trừ cung Tật khi gặp sao xấu thì bệnh lâu khỏi",
  "Trường Sinh ở Tật Ách gặp sao xấu", C(own_stars=["Trường Sinh"], other="'gặp sao xấu' — unspecified bad stars (sát tinh/hung tinh)"),
  "Trường Sinh ở Tật Ách mà gặp sao xấu thì có bệnh lâu khỏi", "limit", ["health.mild", "NEW:health.lingering"],
  notes="Not a disease name. Rest of the sentence: in other palaces Trường sinh brings phúc thọ tài lộc.")
E("kl161_tu_moc_duc", "KL", 161, "Tử Tức", "Mộc dục ở các cung — Tử",
  "Tử: hiếm muộn.", "hiếm muộn",
  "Mộc Dục ở Tử Tức", C(own_stars=["Mộc Dục"]),
  "Mộc Dục ở Tử Tức thì hiếm muộn con", "limit", ["kin.few", "kin.late"], timing=True,
  notes="Quote 'hiếm muộn' occurs once on p.161 (image: 'Tử: hiếm muộn.'). Contrasts with KL p.218 which lists 'Mộc' among 'dễ sinh con' stars (if 'Mộc' there = Mộc Dục) — book-internal conflict.")
N("kl162_de_vuong_giai_benh", "star_nature", "Đế Vượng", "", "KL", 162,
  "Đế vượng gia tăng phúc thọ, giải trừ bệnh tật, tai họa, tăng tiến công danh, lợi ích cho",
  "Đế vượng gia tăng phúc thọ, giải trừ bệnh tật, tai họa, tăng tiến công danh, lợi ích cho sinh nở.",
  "Đế Vượng gia tăng phúc thọ, giải trừ bệnh tật, tai họa, lợi cho sinh nở", ["health", "children"], "+",
  ["NEW:health.shielded", "NEW:kin.easy_children", "well.longevity"],
  notes="WHY for KL p.218 (Đế vượng among 'dễ sinh con' stars).")
E("kl162_tu_suy", "KL", 162, "Tử Tức", "6. Suy",
  "Ở Tử thì hiếm con, ở Quan công danh thấp, ở Di làm tôi tớ.", "Ở Tử thì hiếm con",
  "Suy ở Tử Tức", C(own_stars=["Suy"]),
  "sao Suy ở Tử Tức thì hiếm con", "limit", ["kin.few"], timing=True)
N("kl162_suy_sa_sut", "star_nature", "Suy", "", "KL", 162,
  "Tượng trưng cho sa sút suy bại dù ở cung nào cũng vậy",
  "Sao Thủy, chủ sự yếu đuối và suy thoái. Tượng trưng cho sa sút suy bại dù ở cung nào cũng vậy.",
  "sao Suy chủ yếu đuối, suy thoái; ở cung nào cũng tượng trưng sa sút", ["children"], "-", ["kin.few"],
  notes="WHY for 'Ở Tử thì hiếm con'.")
