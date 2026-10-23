page("KL", 140, "Thiên quan–Thiên phúc: nature (giảm bệnh tật) + 'Quan Phúc ở các cung' line about Thiên sứ in Tật ách. Text layer in order.")
page("KL", 141, "Tuần Triệt ở các cung: 'Tật :' heading at the foot of the page; its line is the first line of p.142.")
page("KL", 142, "Tuần Triệt Tật line (first line, continuing the p.141 heading); rest is Điền/Phối/Quan/Mệnh + Bài đọc thêm sao Can.")
N("kl140_quan_phuc_giam_benh", "star_nature", "Thiên Quan, Thiên Phúc", "", "KL", 140,
  "Có số tu hành, có tính cách làm giảm bệnh tật",
  "Quan Phúc tượng trưng cho - Cứu giải, đức độ, tin tưởng trời phật, - Có số tu hành, có tính cách làm giảm bệnh tật, - Tăng phúc thọ do tu nhân tích đức giúp đỡ Thất sát nhân.",
  "Thiên Quan, Thiên Phúc tượng trưng cho cứu giải, đức độ, làm giảm bệnh tật, tăng phúc thọ", ["health"], "+",
  ["NEW:health.shielded", "well.longevity"])
E("kl140_tat_quan_phuc_thien_su", "KL", 140, "Tật Ách", "Quan Phúc ở các cung",
  "Nằm cùng Thiên sứ, Quan phúc giải được ác tính của Thiên sứ, làm tăng tuổi thọ vì Thiên sứ nằm trong cung Tật ách chỉ chờ mang ta đi cùng Diêm chúa.",
  "Nằm cùng Thiên sứ, Quan phúc giải được ác tính của Thiên sứ, làm tăng tuổi thọ",
  "Thiên Quan, Thiên Phúc nằm cùng Thiên Sứ (Thiên Sứ luôn ở cung Tật Ách)",
  C(own_stars=["Thiên Quan", "Thiên Phúc", "Thiên Sứ"], other="'Quan phúc' = Thiên Quan, Thiên Phúc (pair; one alone not stated) in the same palace as Thiên Sứ, which the book places in Tật Ách"),
  "Thiên Quan, Thiên Phúc ở Tật Ách cùng Thiên Sứ thì giải được tính xấu của Thiên Sứ, làm tăng tuổi thọ", "support",
  ["well.longevity", "NEW:health.shielded"],
  notes="The reason clause is death imagery ('mang ta đi cùng Diêm chúa'): do not render it; keep only the longevity/giải claim.")
E("kl142_tat_tuan_triet_vcd", "KL", 142, "Tật Ách", "Tuần Triệt ở các cung — Tật",
  "Vô chính diệu Tuần Triệt đóng ở cung Vô chính diệu thì lại tốt nhưng phải xét tùy từng hoàn cảnh.",
  "Tuần Triệt đóng ở cung Vô chính diệu thì lại tốt nhưng phải xét tùy từng hoàn",
  "Tật Ách vô chính diệu có Tuần hoặc Triệt",
  C(only=False, tt="Tuần or Triệt", other="Tật Ách has no chính tinh (vô chính diệu); book hedges 'phải xét tùy từng hoàn cảnh'"),
  "Tuần Triệt đóng ở Tật Ách vô chính diệu thì lại tốt, nhưng phải xét tùy hoàn cảnh", "support", ["life.mitigated"],
  notes="Heading 'Tật :' is the last line of p.141; this sentence (starting with an extra 'Vô chính diệu', possibly a stray sub-heading) is the first line of p.142 and the only content before 'Điền :'. Attribution to Tật is by layout; the sentence itself does not name Tật. Close to TL rule TV_TL_TAT_ACH_GIAM.")
