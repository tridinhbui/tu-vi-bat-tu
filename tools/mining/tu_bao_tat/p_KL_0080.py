page("KL", 80, "Thiên cơ ở các cung: Bào and Tử headings (no Tật heading). Text layer in order.")
E("kl80_bao_co_cu_di_bao", "KL", 80, "Huynh Đệ", "Thiên cơ ở các cung — Bào",
  "- Cự cơ đồng cung có anh em dị bào", "Cự cơ đồng cung có anh em dị bào",
  "Huynh Đệ có Thiên Cơ đồng cung Cự Môn",
  C(own_major=["Thiên Cơ", "Cự Môn"], other="Cự Môn and Thiên Cơ in the same palace (Mão/Dậu)"),
  "Huynh Đệ có Cự Cơ đồng cung thì có anh em khác cha hoặc khác mẹ", "neutral", ["NEW:kin.half"], timing=True,
  notes="Family-composition fact (half-siblings), implies a parent's other marriage; event-type claim, marked timing. Caller may prefer to skip as too specific.")
E("kl80_tu_co_luong_nguyet", "KL", 80, "Tử Tức", "Thiên cơ ở các cung — Tử",
  "- Cơ Lương hay Nguyệt: 3-5 con.", "Cơ Lương hay Nguyệt: 3-5 con",
  "Tử Tức có Thiên Cơ đi với Thiên Lương hoặc Thái Âm",
  C(own_major=["Thiên Cơ"], with_any=["Thiên Lương", "Thái Âm"],
    other="'Cơ Lương hay Nguyệt' — Thiên Cơ paired with Thiên Lương or Thái Âm; book does not say đồng cung explicitly (these pairs are normally đồng cung)"),
  "Tử Tức có Cơ Lương hoặc Cơ Nguyệt thì có khoảng 3-5 con", "neutral", ["kin.many"], timing=True,
  notes="Number-of-children line: palace characteristic only.")
