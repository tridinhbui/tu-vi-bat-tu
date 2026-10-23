page("KL", 84, "Thái dương ở các cung: Tử, Tật headings (no Bào). Text layer in order.")
E("kl84_tu_nhat_nguyet_thai", "KL", 84, "Tử Tức", "Thái dương ở các cung — Tử",
  "- Nhật Nguyệt Thai có con sinh đôi.", "Nhật Nguyệt Thai có con sinh đôi",
  "Tử Tức có Thái Dương, Thái Âm và sao Thai",
  C(own_stars=["Thái Dương", "Thái Âm", "Thai"], other="the three named together; book does not say đồng cung vs hội"),
  "Tử Tức có Nhật, Nguyệt cùng sao Thai thì có con sinh đôi", "neutral", ["NEW:kin.twins"], timing=True,
  notes="Event claim (twins); palace characteristic only. Same claim repeated at KL p.99 (Thái âm section).")
E("kl84_tat_nhat_nguyet_ham_ky_da", "KL", 84, "Tật Ách", "Thái dương ở các cung — Tật",
  "- Nhật Nguyệt hãm địa gặp Hóa kỵ, Đà la mù mắt, què chân.", "Nhật Nguyệt hãm địa gặp Hóa kỵ, Đà la mù mắt, què chân",
  "Tật Ách có Nhật Nguyệt hãm địa gặp Hóa Kỵ, Đà La",
  C(own_major=["Thái Dương", "Thái Âm"], with_any=["Hóa Kỵ", "Đà La"], other="Nhật Nguyệt hãm địa"),
  "(bệnh tật cụ thể ở mắt, chân)", "limit", ["health.severe"], skip="named disability (blind, lame)")
