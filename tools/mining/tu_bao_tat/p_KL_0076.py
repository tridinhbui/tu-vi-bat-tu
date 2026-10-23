page("KL", 76, "Tử Vi ở các cung: Tật and Tử headings. Text layer in order.")
E("kl76_tat_tu_vi", "KL", 76, "Tật Ách", "Tử vi ở các cung — Tật",
  "- Tử vi rất tốt cho cung này vì tính cách cứu giải, dù có đồng cung với Thất sát.",
  "Tử vi rất tốt cho cung này vì tính cách cứu giải, dù có đồng cung với Thất sát",
  "Tật Ách có Tử Vi (kể cả khi đồng cung Thất Sát)",
  C(own_major=["Tử Vi"], other="holds even when Thất Sát is in the same palace"),
  "Tử Vi rất tốt cho cung Tật Ách vì có tính cứu giải, dù đồng cung Thất Sát", "support",
  ["life.mitigated", "NEW:health.shielded"])
E("kl76_tu_tu_vi_phu_tuong", "KL", 76, "Tử Tức", "Tử vi ở các cung — Tử",
  "- Đồng cung với Phủ Tướng thì đông con.", "Đồng cung với Phủ Tướng thì đông con",
  "Tử Tức có Tử Vi đồng cung với Thiên Phủ hoặc Thiên Tướng",
  C(own_major=["Tử Vi"], with_any=[], other="Tử Vi in the same palace as Thiên Phủ or Thiên Tướng ('Phủ Tướng')"),
  "Tử Vi đồng cung Phủ hoặc Tướng ở Tử Tức thì đông con", "support", ["kin.many"], timing=True,
  dup="TV_KL_STAR_TU_TUC_TV_PHU_TUONG")
