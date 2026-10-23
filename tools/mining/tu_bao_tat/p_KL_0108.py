page("KL", 108, "Thiên tướng ở các cung: Tử heading (no Bào, no Tật; p.107 has only intro + Mệnh start). Text layer in order.")
page("KL", 109, "Thiên lương intro: one star-nature line (cứu giải bệnh tật).")
E("kl108_tu_tuong_tu_vi", "KL", 108, "Tử Tức", "Thiên tướng ở các cung — Tử",
  "- Đi với Tử vi ở Tỵ, Hợi Sửu Mùi thì có ba con trở lên.", "Đi với Tử vi ở Tỵ, Hợi Sửu Mùi thì có ba con trở lên",
  "Thiên Tướng ở Tử Tức 'đi với' Tử Vi, ở Tỵ, Hợi, Sửu, Mùi",
  C(own_major=["Thiên Tướng"], with_any=["Tử Vi"], branch=["Tỵ", "Hợi", "Sửu", "Mùi"],
    other="'đi với' is not đồng cung here: Tử Vi and Thiên Tướng share a palace only at Thìn/Tuất. The same wording in the Phúc line ('Kết hợp với Tử, Liêm, Vũ ở Tỵ Hợi Sửu Mùi') suggests a looser link; on a chart Tử Vi is not even in Tướng's tam phương at Tỵ/Hợi/Sửu/Mùi — condition is ambiguous"),
  "Thiên Tướng ở Tử Tức đi với Tử Vi ở Tỵ, Hợi, Sửu, Mùi thì có từ ba con trở lên", "support", ["kin.many"], timing=True,
  notes="Number-of-children line. Condition cannot be mapped cleanly onto a chart (see condition.other); caller should decide or drop.")
E("kl108_tu_tuong_liem_vu", "KL", 108, "Tử Tức", "Thiên tướng ở các cung — Tử",
  "- Đi vợi Liêm, Vũ ít con, muộn con.", "Liêm, Vũ ít con, muộn con",
  "Thiên Tướng ở Tử Tức đi với Liêm Trinh hoặc Vũ Khúc",
  C(own_major=["Thiên Tướng"], with_any=["Liêm Trinh", "Vũ Khúc"],
    other="'đi với' — Tướng is đồng cung with Liêm at Tí/Ngọ and with Vũ at Dần/Thân"),
  "Thiên Tướng ở Tử Tức đi với Liêm hoặc Vũ thì ít con, muộn con", "limit", ["kin.few", "kin.late"], timing=True,
  notes="Page misprint 'vợi' for 'với'. Agrees with KL p.93 (Liêm in Tử: chậm con, ít con).")
N("kl109_thien_luong_cuu_giai", "star_nature", "Thiên Lương", "", "KL", 109,
  "Cứu giải tai họa, bệnh tật, từ thiện",
  "Tính nết: Cứu giải tai họa, bệnh tật, từ thiện, Có mưu lược.",
  "Thiên Lương có tính cứu giải tai họa, bệnh tật, từ thiện", ["health"], "+",
  ["NEW:health.shielded", "life.mitigated"],
  notes="Close in meaning to existing thien_luong.phuc (p.189) but a different page/quote.")
