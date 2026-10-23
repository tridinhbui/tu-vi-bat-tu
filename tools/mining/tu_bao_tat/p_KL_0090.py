page("KL", 90, "Thiên đồng ở các cung: Tử tức heading (no Bào, no Tật). Text layer in order.")
page("KL", 91, "Thiên đồng 'Thế đứng' (b) 'sinh nhiều con' and (e) 'con cái hiển đạt' are Mệnh-position lines, not Tử Tức: not recorded (Mệnh is out of scope).")
E("kl90_tu_dong_mao", "KL", 90, "Tử Tức", "Thiên đồng ở các cung — Tử tức",
  "- Ở Mão: đông con.", "Ở Mão: đông con",
  "Thiên Đồng ở Tử Tức tại Mão", C(own_major=["Thiên Đồng"], branch=["Mão"]),
  "Thiên Đồng ở Tử Tức tại Mão thì đông con", "support", ["kin.many"], timing=True)
E("kl90_tu_dong_ty_hoi", "KL", 90, "Tử Tức", "Thiên đồng ở các cung — Tử tức",
  "- Ở Tỵ Hợi ít con.", "Ở Tỵ Hợi ít con",
  "Thiên Đồng ở Tử Tức tại Tỵ hoặc Hợi", C(own_major=["Thiên Đồng"], branch=["Tỵ", "Hợi"]),
  "Thiên Đồng ở Tử Tức tại Tỵ, Hợi thì ít con", "limit", ["kin.few"], timing=True)
E("kl90_tu_dong_thin_tuat_cu", "KL", 90, "Tử Tức", "Thiên đồng ở các cung — Tử tức",
  "- Ở Thìn Tuất nhất là đồng cung với Cự thì hiếm con.", "Ở Thìn Tuất nhất là đồng cung với Cự thì hiếm con",
  "Thiên Đồng ở Tử Tức tại Thìn hoặc Tuất; nhất là khi đồng cung Cự Môn",
  C(own_major=["Thiên Đồng"], branch=["Thìn", "Tuất"],
    other="'nhất là đồng cung với Cự' = stronger when Cự Môn is in the same palace (Đồng–Cự share a palace only in Sửu/Mùi, so at Thìn/Tuất this is not possible; the book's wording is kept as is)"),
  "Thiên Đồng ở Tử Tức tại Thìn, Tuất thì hiếm con, nhất là khi đồng cung Cự Môn", "limit", ["kin.few"], timing=True,
  notes="Chart-structure caveat: Thiên Đồng at Thìn/Tuất is always alone (đơn thủ, Cự Môn opposite); Đồng+Cự đồng cung occurs at Sửu/Mùi. Safest reading: Đồng at Thìn/Tuất → hiếm con.")
