page("KL", 120, "Thiên giải/Địa giải + 'Bàn về các sao giải' (strong/small cứu giải lists): natures only. Text layer in order.")
page("KL", 121, "Tả Hữu (Bào, Tử, Tật lines) + Thiên riêu ở các cung (Tử, Bào). Text layer in order.")
page("KL", 122, "Thiên y: one star nature (cứu giải bệnh tật); Mệnh/Vận lines out of scope.")
N("kl120_giai_nho", "star_nature", "Thiên Giải, Địa Giải", "", "KL", 120,
  "Khi gặp tai nạn, có các sao này có phần nào hy vọng thoát nạn",
  "- Các sao Thiên giải và Địa giải là những sao cứu giải nhỏ. - Khi gặp tai nạn, có các sao này có phần nào hy vọng thoát nạn. Tính nết: Nhân hậu, từ thiện, giải ách, giảm bệnh tật, tăng thọ.",
  "Thiên Giải, Địa Giải là sao cứu giải nhỏ: gặp tai nạn có phần nào hy vọng thoát, giảm bệnh tật", ["health"], "+",
  ["life.mitigated", "NEW:health.shielded"])
N("kl120_cuu_giai_manh", "star_nature", "Vũ Khúc, Hóa Khoa, Tử Vi, Thiên Phủ, Thiên Lương, Thiên Đồng, Tuần, Triệt", "", "KL", 120,
  "Vũ khúc, Hóa khoa, Tử vi, Thiên phủ, Thiên lương, Thiên đồng, Tuần Triệt",
  "- Cứu giải mạnh: Vũ khúc, Hóa khoa, Tử vi, Thiên phủ, Thiên lương, Thiên đồng, Tuần Triệt.",
  "các sao cứu giải mạnh: Vũ Khúc, Hóa Khoa, Tử Vi, Thiên Phủ, Thiên Lương, Thiên Đồng, Tuần, Triệt", ["health"], "+",
  ["life.mitigated", "NEW:health.shielded"],
  notes="Classification list (strong rescuers). Small rescuers listed next: Địa giải, Giải thần, Thiên/Nguyệt/Phúc/Long đức, Thanh long, Thiếu dương, Thiếu âm, Thiên quan, Thiên phúc, Hóa lộc, Lộc tồn, Trường sinh, Đế vượng.")
N("kl120_cuu_giai_nho_list", "star_nature", "Địa Giải, Giải Thần, Thiên Đức, Nguyệt Đức, Phúc Đức, Long Đức, Thanh Long, Thiếu Dương, Thiếu Âm, Thiên Quan, Thiên Phúc, Hóa Lộc, Lộc Tồn, Trường Sinh, Đế Vượng", "", "KL", 120,
  "Địa giải, Giải thần, Thiên đức, Nguyệt đức, Phúc đức, Long đức, Thanh long",
  "- Cứu giải nhỏ: Địa giải, Giải thần, Thiên đức, Nguyệt đức, Phúc đức, Long đức, Thanh long, Thiếu dương, Thiếu âm, Thiên quan, Thiên phúc, Hóa lộc, Lộc tồn, Trường sinh, Đế vương.",
  "các sao cứu giải nhỏ: Địa Giải, Giải Thần, Thiên/Nguyệt/Phúc/Long Đức, Thanh Long, Thiếu Dương, Thiếu Âm, Thiên Quan, Thiên Phúc, Hóa Lộc, Lộc Tồn, Trường Sinh, Đế Vượng",
  ["health"], "+", ["life.mitigated"])
E("kl121_bao_ta_huu", "KL", 121, "Huynh Đệ", "Thế đứng của Tả Hữu",
  "- Tả Hữu tại cung Bào, Tử: đông anh em, nhiều con.", "Tả Hữu tại cung Bào, Tử: đông anh em, nhiều con",
  "Tả Phù, Hữu Bật ở Huynh Đệ", C(own_stars=["Tả Phù", "Hữu Bật"], other="'Tả Hữu' — book names the pair; whether one alone suffices is not stated"),
  "Tả Hữu ở Huynh Đệ thì đông anh em", "support", ["kin.many"], timing=True)
E("kl121_tu_ta_huu", "KL", 121, "Tử Tức", "Thế đứng của Tả Hữu",
  "- Tả Hữu tại cung Bào, Tử: đông anh em, nhiều con.", "Tả Hữu tại cung Bào, Tử: đông anh em, nhiều con",
  "Tả Phù, Hữu Bật ở Tử Tức", C(own_stars=["Tả Phù", "Hữu Bật"], other="'Tả Hữu' — the pair"),
  "Tả Hữu ở Tử Tức thì nhiều con", "support", ["kin.many"], timing=True,
  notes="Consistent with KL p.218 list (Tả, Hữu among 'dễ sinh con' stars, existing rule TV_KL_CUNG_TU_TUC_PHU_TINH) but a different page and claim (count).")
E("kl121_tat_ta_huu", "KL", 121, "Tật Ách", "Thế đứng của Tả Hữu",
  "- Tả Hữu cung Tật đau ốm mau mạnh.", "Tả Hữu cung Tật  đau ốm mau mạnh",
  "Tả Phù, Hữu Bật ở Tật Ách", C(own_stars=["Tả Phù", "Hữu Bật"], other="'Tả Hữu' — the pair"),
  "Tả Hữu ở Tật Ách thì đau ốm mau khỏi", "support", ["NEW:health.recover", "life.mitigated"],
  notes="Not a disease name: says illness passes quickly.")
E("kl121_tu_rieu_con_choi_boi", "KL", 121, "Tử Tức", "Thiên riêu ở các cung — Tử, Bào",
  "- Con chơi bời.", "Con chơi bời",
  "Thiên Riêu ở Tử Tức", C(own_stars=["Thiên Riêu"]),
  "(con cái ham chơi bời)", "limit", ["NEW:kin.wayward"],
  skip="sexual-reputation connotation (Riêu is the book's dâm tinh; next line is about sisters' sexual conduct)")
E("kl121_bao_rieu_chi_em", "KL", 121, "Huynh Đệ", "Thiên riêu ở các cung — Tử, Bào",
  "- Chị em theo trai, chửa hoang.", "Chị em theo trai, chửa hoang",
  "Thiên Riêu ở Huynh Đệ", C(own_stars=["Thiên Riêu"]),
  "(chuyện tình dục của chị em)", "limit", ["kin.strain"], skip="sexual reputation")
N("kl122_thien_y_cuu_giai", "star_nature", "Thiên Y", "", "KL", 122,
  "Thiên y là sao cứu giải bệnh tất, chủ việc thuốc men, nghề y dược",
  "Thiên y là sao cứu giải bệnh tất, chủ việc thuốc men, nghề y dược.",
  "Thiên Y là sao cứu giải bệnh tật, chủ việc thuốc men, nghề y dược", ["health"], "+",
  ["NEW:health.shielded", "NEW:health.recover"], notes="'bệnh tất' is the page's misprint for 'bệnh tật'.")
