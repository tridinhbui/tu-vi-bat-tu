page("KL", 131, "Quang Quí ở các cung: Tử, Tật headings (Tật continues on p.132). Text layer in order.")
page("KL", 132, "Quang Quí Tật (2nd line) + Bài đọc thêm: Quang Quí = cứu giải tầm trung.")
page("KL", 133, "Lộc tồn ở các cung: Tử line + 'chận trễ' nature; Bác sĩ nature (giải trừ bệnh tật). Text layer in order.")
E("kl131_tu_quang_qui_hieu", "KL", 131, "Tử Tức", "Quan Quí ở các cung — Tử",
  "- Con hiếu đễ.", "Con hiếu đễ",
  "Ân Quang, Thiên Quí ở Tử Tức", C(own_stars=["Ân Quang", "Thiên Quí"], other="heading 'Quan Quí' (misprint for Quang Quí): the pair; one alone not stated"),
  "Quang Quí ở Tử Tức thì con cái hiếu thảo", "support", ["NEW:kin.filial", "kin.harmony"])
E("kl131_tu_quang_qui_con_nuoi", "KL", 131, "Tử Tức", "Quan Quí ở các cung — Tử",
  "- Có con nuôi.", "Có con nuôi",
  "Ân Quang, Thiên Quí ở Tử Tức", C(own_stars=["Ân Quang", "Thiên Quí"], other="the pair"),
  "Quang Quí ở Tử Tức thì có con nuôi", "neutral", ["NEW:kin.adopted"], timing=True,
  notes="Event/family-composition claim.")
E("kl131_tu_quang_qui_thanh_than", "KL", 131, "Tử Tức", "Quan Quí ở các cung — Tử",
  "- Có con thánh thần.", "Có con thánh thần",
  "Ân Quang, Thiên Quí ở Tử Tức", C(own_stars=["Ân Quang", "Thiên Quí"], other="the pair"),
  "Quang Quí ở Tử Tức thì có 'con thánh thần'", "neutral", [],
  skip="meaning unclear ('con thánh thần' — child consecrated to/under a deity? a gifted child?); not usable without a gloss",
  notes="Image confirms the wording.")
E("kl131_tat_quang_qui_it_benh", "KL", 131, "Tật Ách", "Quan Quí ở các cung — Tật",
  "- Ít bệnh tật.", "Ít bệnh tật",
  "Ân Quang, Thiên Quí ở Tật Ách", C(own_stars=["Ân Quang", "Thiên Quí"], other="the pair"),
  "Quang Quí ở Tật Ách thì ít bệnh tật", "support", ["well.health", "NEW:health.few_ills"])
E("kl132_tat_quang_qui_chong_khoi", "KL", 132, "Tật Ách", "Quan Quí ở các cung — Tật (cont. from p.131)",
  "- Bệnh chóng khỏi.", "Bệnh chóng khỏi",
  "Ân Quang, Thiên Quí ở Tật Ách", C(own_stars=["Ân Quang", "Thiên Quí"], other="the pair"),
  "Quang Quí ở Tật Ách thì có bệnh cũng chóng khỏi", "support", ["NEW:health.recover", "life.mitigated"],
  notes="Second bullet of the Tật list that starts on p.131; on p.132 it is the first line, before 'Quan:'.")
N("kl131_quang_qui_troi_giup", "star_nature", "Ân Quang, Thiên Quí", "", "KL", 131,
  "Quang Quí biểu hiện sự giúp đỡ của Trời",
  "Quang Quí biểu hiện sự giúp đỡ của Trời, Tả Hữu, nói lên sự giúp đỡ của người.",
  "Quang Quí biểu hiện sự giúp đỡ của Trời (còn Tả Hữu là sự giúp đỡ của người)", ["health", "children"], "+",
  ["NEW:health.shielded", "NEW:kin.filial"])
N("kl132_quang_qui_cuu_giai", "star_nature", "Ân Quang, Thiên Quí", "", "KL", 132,
  "sao cứu giải tầm cỡ trung bình",
  "Có hai đức tính này thì tránh được phần nào đố kỵ ở đời, cho nên cũng được coi là hai sao là hai sao cứu giải tầm cỡ trung bình.",
  "Ân Quang, Thiên Quí được coi là hai sao cứu giải tầm trung", ["health"], "+", ["life.mitigated", "NEW:health.shielded"])
E("kl133_tu_loc_ton", "KL", 133, "Tử Tức", "Lộc tồn ở các cung",
  "- Ở Tử thì chận và hiếm con.", "Ở Tử thì chận và hiếm con",
  "Lộc Tồn ở Tử Tức", C(own_stars=["Lộc Tồn"]),
  "Lộc Tồn ở Tử Tức thì chậm và hiếm con", "limit", ["kin.late", "kin.few"], timing=True,
  notes="'chận' = 'chậm' (page spelling). Agrees with KL p.218 (Lộc tồn among 'hiếm con' stars).")
N("kl133_loc_ton_cham_tre", "star_nature", "Lộc Tồn", "Tử Tức", "KL", 133,
  "Lộc tồn cũng có nghĩa là chận trễ",
  "Lộc tồn cũng có nghĩa là chận trễ, - Ở Phối thì chận vợ chồng. - Ở Tử thì chận và hiếm con.",
  "Lộc Tồn cũng có nghĩa là chậm trễ", ["children", "marriage"], "-", ["kin.late"],
  notes="WHY for Lộc Tồn in Tử Tức (chậm, hiếm con). Existing loc_ton.cham is p.142 'cô đơn, chậm trễ'.")
N("kl133_bac_si_giai_benh", "star_nature", "Bác Sĩ", "", "KL", 133,
  "Tượng trưng cho: thông minh, từ thiện, giải trừ bệnh tật",
  "Tượng trưng cho: thông minh, từ thiện, giải trừ bệnh tật.",
  "Bác Sĩ tượng trưng cho thông minh, từ thiện, giải trừ bệnh tật", ["health"], "+", ["NEW:health.shielded"])
