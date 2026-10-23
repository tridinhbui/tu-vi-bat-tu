page("KL", 110, "Thiên lương ở các cung: Tử heading (no Bào, no Tật; p.111 Di/Quan/Điền-Phúc-Phụ + Bài đọc thêm has nothing for these palaces). Text layer in order.")
page("KL", 111, "Thiên lương tail: nothing for Tử/Bào/Tật.", img=False)
E("kl110_tu_luong_dong_ti_ngo", "KL", 110, "Tử Tức", "Thiên lương ở các cung — Tử",
  "- Lương đồng Dần Thân hay Lương Tí Ngọ: đông con.", "đồng Dần Thân hay Lương Tí Ngọ: đông con",
  "Thiên Lương ở Tử Tức: đồng cung Thiên Đồng tại Dần/Thân, hoặc Thiên Lương tại Tí/Ngọ",
  C(own_major=["Thiên Lương"], branch=["Dần", "Thân", "Tí", "Ngọ"],
    other="either (Lương + Thiên Đồng đồng cung at Dần/Thân) or (Lương at Tí/Ngọ)"),
  "Tử Tức có Lương Đồng ở Dần, Thân hoặc Lương ở Tí, Ngọ thì đông con", "support", ["kin.many"], timing=True)
E("kl110_tu_luong_nhat_co", "KL", 110, "Tử Tức", "Thiên lương ở các cung — Tử",
  "- Lương Nhật ở Mão hay Lương Cơ: đông con, con khá giả.", "Cơ: đông con, con khá giả",
  "Thiên Lương ở Tử Tức: đồng cung Thái Dương tại Mão, hoặc đi với Thiên Cơ",
  C(own_major=["Thiên Lương"], other="either (Lương + Thái Dương at Mão) or (Lương + Thiên Cơ, đồng cung at Thìn/Tuất)"),
  "Tử Tức có Lương Nhật ở Mão hoặc Lương Cơ thì đông con, con cái khá giả", "support", ["kin.many", "NEW:kin.prosper"],
  timing=True, notes="'con khá giả' part is a non-timing characteristic; 'đông con' is a count.")
E("kl110_tu_luong_ty_hoi", "KL", 110, "Tử Tức", "Thiên lương ở các cung — Tử",
  "- Lương Tỵ Hợi: ít con.", "Tỵ Hợi: ít con",
  "Thiên Lương ở Tử Tức tại Tỵ hoặc Hợi", C(own_major=["Thiên Lương"], branch=["Tỵ", "Hợi"]),
  "Thiên Lương ở Tử Tức tại Tỵ, Hợi thì ít con", "limit", ["kin.few"], timing=True,
  notes="Quote fragment 'Tỵ Hợi: ít con' also matches only this line on the page (checked on image).")
