page("KL", 135, "Đà la ở các cung: Tử heading. TEXT LAYER SCRAMBLED: it glues 'Đà, Tả Hữu, Lộc Quyền ở Dần Thân Tỵ Hợi: võ hiển' under 'Tử:' and puts the real Tử line after the Thanh long paragraph; the image shows the Tử line is 'Đà Không Kiếp Hỏa (Linh): con ngỗ ngược' and 'võ hiển' belongs to Quan. Thanh long nature (giải trừ bệnh tật).")
page("KL", 136, "Song Hao ở các cung: Tài/Điền, Phúc/Nô, Quan/Di, Vận — no Tử/Bào/Tật heading; the 'Nếu ốm đau, mau lành' line is under Vận (not recorded as a Tật entry).")
page("KL", 137, "Phi liêm nature (hiếm muộn); Hỉ thần ở các cung: Bào heading starts at page foot (lines on p.138).")
page("KL", 138, "Hỉ thần Bào lines (both sexual → skipped); Bệnh phù 'Bệnh phá: ít con' (no palace named → nature).")
E("kl135_tu_da_kk_hoa", "KL", 135, "Tử Tức", "Đà la ở các cung — Tử",
  "- Đà Không Kiếp Hỏa (Linh): con ngỗ ngược.", "Đà Không Kiếp Hỏa (Linh): con ngỗ ngược",
  "Tử Tức có Đà La, Địa Không/Địa Kiếp, Hỏa Tinh (hoặc Linh Tinh)",
  C(own_stars=["Đà La", "Địa Không", "Địa Kiếp", "Hỏa Tinh"], other="'(Linh)' = Linh Tinh may stand for Hỏa Tinh; book does not say đồng cung vs hội"),
  "Tử Tức có Đà La, Không Kiếp, Hỏa (hoặc Linh) thì con cái ngỗ ngược", "limit", ["NEW:kin.wayward", "kin.strain"],
  notes="Text layer misplaces this line (see page note); quote is the line's own text, which IS on the page.")
N("kl135_thanh_long_giai_benh", "star_nature", "Thanh Long", "", "KL", 135,
  "giải trừ cho",
  "Tượng trưng cho thành công trong giao tế, may mắn cho hóa phối, lợi ích cho thi cử, giải trừ cho bệnh tật.",
  "Thanh Long tượng trưng cho may mắn trong giao tế, hôn phối, thi cử và giải trừ bệnh tật", ["health"], "+",
  ["NEW:health.shielded"], notes="Quote is short because the text layer breaks the line before 'bệnh tật'.")
N("kl137_phi_liem_hiem_muon", "star_nature", "Phi Liêm", "Tử Tức", "KL", 137,
  "Tượng trưng cho mau mắn, lanh lợi, hiếm muộn",
  "Phi liêm là tóc. - Tượng trưng cho mau mắn, lanh lợi, hiếm muộn.",
  "Phi Liêm tượng trưng cho mau mắn, lanh lợi, và hiếm muộn", ["children"], "-", ["kin.few", "kin.late"],
  notes="WHY for the existing TH p.60 rules (Phi Liêm in Tử Tức/Huynh Đệ: số con/anh em ít đi). The next lines (sản phụ, băng huyết) are skip-class.")
E("kl138_bao_hi_rieu", "KL", 138, "Huynh Đệ", "Hỉ thần ở các cung — Bào",
  "- Hỉ, Riêu : anh em chơi bời.", "Hỉ, Riêu : anh em chơi bời",
  "Hỉ Thần, Thiên Riêu ở Huynh Đệ", C(own_stars=["Hỉ Thần", "Thiên Riêu"]),
  "(anh em chơi bời)", "limit", ["NEW:kin.wayward"], skip="sexual-reputation connotation (Riêu; next line 'anh em dâm đãng')")
E("kl138_bao_hi_dao_thai_phuc", "KL", 138, "Huynh Đệ", "Hỉ thần ở các cung — Bào",
  "- Hỉ, Đào, Thai, Phục : anh em dâm đãng.", "anh em dâm đãng",
  "Hỉ Thần, Đào Hoa, Thai, Phục Binh ở Huynh Đệ", C(own_stars=["Hỉ Thần", "Đào Hoa", "Thai", "Phục Binh"]),
  "(anh em dâm đãng)", "limit", [], skip="sexual reputation")
N("kl138_benh_pha_it_con", "star_nature", "Bệnh Phù / Bệnh, Phá Quân", "Tử Tức", "KL", 138,
  "Bệnh phá : ít con",
  "- Bệnh phá : ít con.",
  "Bệnh (Bệnh Phù) đi với Phá Quân: ít con", ["children"], "-", ["kin.few"],
  notes="Listed under '11. Bệnh phù và Bệnh' with no palace named, so kept as a nature, not a Tử Tức rule. KL p.162 repeats 'Bệnh Phá : ít con' under the Mệnh heading of 'Bệnh ở các cung', so the book's condition is Bệnh + Phá at MỆNH, not at Tử Tức. 'Bệnh phá' read as Bệnh + Phá Quân (could also be Phá Toái).")
