page("KL", 193, "Bài đọc thêm: '19. Đẩu quân … Đẩu quân đóng tại Tử tức là dấu hiệu hiếm con'. Text layer scrambled (Ân quang paragraph and Thiếu dương line interleaved into the Đẩu quân paragraph); image read.")
page("KL", 200, "Hỏa Linh nature 'xa lánh anh em'; list of strong cứu giải stars (Tuần Triệt, Thiên tài, Hóa khoa, Quan Phúc). Text layer partly scrambled (the 'ngộ chế' sentence split).")
page("KL", 215, "Mệnh/Thân section of the palace chapter: two sentences relating Tật (with Di, Vận) to Mệnh/Phúc; one rhetorical sentence on Phúc, Ách, Thê, Tử. Text layer scrambled (line fragments reordered).")
page("KL", 220, "Cung Phụ mẫu: relation 'Phụ mẫu quá đẹp thì Tật ách heo hút nghèo nàn'.")
page("KL", 234, "Đại vận sequence by palace (nghịch: Huynh đệ = tuổi thiếu niên, Tử Tức = tuổi thành danh, continued on p.235) — vận/timing, not recorded.", img=False)
E("kl193_tu_dau_quan", "KL", 193, "Tử Tức", "19. Đẩu quân (Bài đọc thêm)",
  "Đẩu quân đóng tại Tử tức là dấu hiệu hiếm con.", "Đẩu quân đóng tại Tử tức là dấu hiệu hiếm con",
  "Đẩu Quân ở Tử Tức", C(own_stars=["Đẩu Quân"]),
  "Đẩu Quân ở Tử Tức là dấu hiệu hiếm con", "limit", ["kin.few"], timing=True,
  notes="Agrees with KL p.218 listing Đẩu among Tử Tức 'không có con' stars (that line skipped).")
N("kl200_hoa_linh_xa_anh_em", "star_nature", "Hỏa Tinh, Linh Tinh", "Huynh Đệ", "KL", 200,
  "Hỏa Linh thích cô độc, xa lánh anh em, nóng nẩy nên gây họa",
  "Hỏa Linh thích cô độc, xa lánh anh em, nóng nẩy nên gây họa.",
  "Hỏa Linh thích cô độc, xa lánh anh em, nóng nảy nên gây họa", ["siblings"], "-", ["kin.apart", "kin.strain"],
  notes="Star temperament (said generally, not of the Huynh Đệ palace).")
N("kl200_sao_giai_manh", "star_nature", "Tuần, Triệt, Thiên Tài, Hóa Khoa, Thiên Quan, Thiên Phúc", "", "KL", 200,
  "Những sao giải mạnh gồm Tuần Triệt, Thiên tài, Hóa khoa, Quan Phúc",
  "Gặp các hung sát tinh không có sao giải thì nguy hiểm. Nếu có sao giải mạnh thì có thể vô hiệu hóa ác tính của chúng. … Những sao giải mạnh gồm Tuần Triệt, Thiên tài, Hóa khoa, Quan Phúc.",
  "gặp hung sát tinh mà có sao giải mạnh (Tuần Triệt, Thiên Tài, Hóa Khoa, Quan Phúc) thì có thể vô hiệu hóa ác tính của chúng",
  ["health"], "+", ["life.mitigated", "NEW:health.shielded"],
  notes="Differs from KL p.120's strong list (which has Vũ khúc, Tử vi, Thiên phủ, Thiên lương, Thiên đồng and not Thiên tài, Quan Phúc).")
N("kl215_menh_phuc_tot_tat_do_xau", "palace_relation", "", "Tật Ách", "KL", 215,
  "Mệnh Phúc tốt mà Di, Tật, Vận ngộ hung sát cũng đỡ xấu",
  "Mệnh Phúc tốt mà Di, Tật, Vận ngộ hung sát cũng đỡ xấu.",
  "Mệnh và Phúc Đức tốt thì Thiên Di, Tật Ách, vận có gặp hung sát tinh cũng đỡ xấu", ["health", "fortune"], "±",
  ["life.mitigated"], notes="Relation: Mệnh + Phúc Đức buffer the Tật Ách palace.")
N("kl215_menh_phuc_xau_tat_nguy", "palace_relation", "", "Tật Ách", "KL", 215,
  "Mệnh Phúc xấu và Di, Tật, Vận có hung tinh thì nguy vô cùng",
  "Mệnh Phúc xấu và Di, Tật, Vận có hung tinh thì nguy vô cùng.",
  "Mệnh và Phúc Đức xấu mà Thiên Di, Tật Ách, vận lại có hung tinh thì rất nguy", ["health", "fortune"], "-",
  ["NEW:health.exposed"])
N("kl215_phuc_ach_the_tu", "palace_relation", "", "Tử Tức, Tật Ách", "KL", 215,
  "Giàu sang phú quí mà đầy tai họa ở các cung Phúc, Ách, Thê, Tử thì có hạnh phúc không",
  "Giàu sang phú quí mà đầy tai họa ở các cung Phúc, Ách, Thê, Tử thì có hạnh phúc không? Thanh bạch, bình dị, thư thái tuy chẳng giàu mà gia đình cha mẹ vợ con được êm ấm, thương yêu, đùm bọc nhau thì có phải là bất hạnh chăng?",
  "giàu sang mà các cung Phúc Đức, Tật Ách, Phu Thê, Tử Tức đầy tai họa thì chưa chắc hạnh phúc; thanh bạch mà gia đình êm ấm thì chưa hẳn bất hạnh",
  ["children", "health", "fortune", "money"], "±", [],
  notes="Rhetorical framing sentence: Tử Tức and Tật Ách weigh on happiness independently of wealth (Mệnh/Tài/Quan).")
N("kl220_phu_mau_dep_tat_ngheo", "palace_relation", "", "Tật Ách", "KL", 220,
  "Có điều là cung Phụ mẫu mà quá đẹp thì cung Tật ách của đương số lại heo hút nghèo nàn",
  "Có điều là cung Phụ mẫu mà quá đẹp thì cung Tật ách của đương số lại heo hút nghèo nàn. Không biết đây có phải là sự sắp xếp cố ý của người xưa để ranh đe hậu thế đừng quá ỷ lại bào bậc sinh thành hay không !",
  "cung Phụ Mẫu quá đẹp thì cung Tật Ách của đương số lại heo hút, nghèo nàn", ["health", "parents"], "±", [],
  notes="Relation Phụ Mẫu ↔ Tật Ách (the two palaces are always opposite, xung chiếu). Book itself wonders whether it is a moral device.")
