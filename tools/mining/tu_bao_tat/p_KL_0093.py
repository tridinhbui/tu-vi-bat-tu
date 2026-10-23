page("KL", 93, "Liêm trinh ở các cung: Tử tức heading (no Bào, no Tật; p.94 continues Quan/Điền/Phụ only). Text layer in order.")
E("kl93_tu_liem_cham_it", "KL", 93, "Tử Tức", "Liêm trinh ở các cung — Tử tức",
  "- Chậm con, ít con trừ khi đồng cung với Thiên phủ.", "Chậm con, ít con trừ khi đồng cung với Thiên phủ",
  "Liêm Trinh ở Tử Tức, không đồng cung Thiên Phủ",
  C(own_major=["Liêm Trinh"], not_=["Thiên Phủ"], other="exception: Liêm Trinh đồng cung Thiên Phủ (Thìn/Tuất) is excluded"),
  "Liêm Trinh ở Tử Tức thì chậm con, ít con, trừ khi đồng cung Thiên Phủ", "limit", ["kin.few", "kin.late"], timing=True)
E("kl93_tu_liem_tuong_spt", "KL", 93, "Tử Tức", "Liêm trinh ở các cung — Tử tức",
  "- Khó nuôi con nếu gặp Thiên tướng, Sát Phá Tham.", "Khó nuôi con nếu gặp Thiên tướng, Sát Phá Tham",
  "Liêm Trinh ở Tử Tức gặp Thiên Tướng hoặc Thất Sát, Phá Quân, Tham Lang",
  C(own_major=["Liêm Trinh"], with_any=["Thiên Tướng", "Thất Sát", "Phá Quân", "Tham Lang"],
    other="'gặp' — book does not say đồng cung (Liêm is đồng cung with each of these in some branch)"),
  "Liêm Trinh ở Tử Tức gặp Tướng hoặc Sát Phá Tham thì khó nuôi con", "limit", ["NEW:kin.hard_raise"],
  skip="'khó nuôi con' is the traditional euphemism for children's illness / early loss",
  notes="If the caller judges 'khó nuôi' acceptable, reading would be 'việc nuôi dạy con vất vả'.")
N("kl95_tu_vi_cuu_giai_benh", "star_nature", "Tử Vi", "", "KL", 95,
  "Tử vi có thêm tính cách cứu giải các tai họa",
  "So Thiên phủ với Tử vi thì cả hai đều từ thiện nhưng Tử vi có thêm tính cách cứu giải các tai họa và bệnh tật, Thiên phủ thêm tính cách bao dung, phát lộc và sự bình an.",
  "Tử Vi có thêm tính cứu giải tai họa và bệnh tật; Thiên Phủ thêm tính bao dung, phát lộc và bình an",
  ["health"], "+", ["NEW:health.shielded", "life.mitigated"],
  notes="Same idea as existing tu_vi.cuu_giai (p.186) but a different page/quote.")
page("KL", 95, "Thiên phủ intro: one star-nature sentence comparing Tử Vi (cứu giải bệnh tật) and Thiên Phủ.")
