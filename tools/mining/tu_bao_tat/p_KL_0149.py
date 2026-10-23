page("KL", 149, "Tứ đức nature (giải bệnh nhỏ) and Long trì–Phượng các line 'rất tốt cho các cung Phối, Tử, và Phúc, Điền'. Text layer in order.")
page("KL", 150, "Đào Hồng: Mệnh-level remark that monk-destiny charts have bad Tử tức/Phu thê — not recorded (Mệnh condition).", img=False)
page("KL", 153, "Cô quả ở các cung: 'Phúc. Tử, Bào' heading. TEXT LAYER SCRAMBLED (Khốc Hư sentence and 'Quả, Đào, Mã' line pushed into the Phối list); image read.")
N("kl149_tu_duc_giai_benh_nho", "star_nature", "Thiên Đức, Nguyệt Đức, Long Đức, Phúc Đức (Tứ Đức)", "", "KL", 149,
  "Tứ đức giải trừ các bệnh nhỏ và tai họa nhỏ, mang lại may mắn và hỉ sự",
  "Tứ đức giải trừ các bệnh nhỏ và tai họa nhỏ, mang lại may mắn và hỉ sự.",
  "Tứ Đức giải trừ các bệnh nhỏ và tai họa nhỏ, mang lại may mắn và hỉ sự", ["health"], "+",
  ["health.mild", "life.mitigated"])
N("kl149_long_phuong_sinh_no", "star_nature", "Long Trì, Phượng Các", "Tử Tức", "KL", 149,
  "may mắn trong hôn nhân",
  "Long Phượng có nghĩa là thì đỗ cao nhất là khi ở Mão Dậu, tăng tài lộc, may mắn trong hôn nhân, sinh nở.",
  "Long Phượng chủ thi đỗ, tăng tài lộc, may mắn trong hôn nhân và sinh nở", ["children", "marriage"], "+",
  ["NEW:kin.easy_children"], notes="WHY for the next entry and for KL p.218 listing Long trì, Phượng các among 'dễ sinh con' stars.")
E("kl149_tu_long_phuong", "KL", 149, "Tử Tức", "10. Long trì - Phượng các",
  "Long Phượng rất tốt cho các cung Phối, Tử, và Phúc, Điền.",
  "Long Phượng rất tốt cho các cung Phối, Tử, và Phúc, Điền",
  "Long Trì, Phượng Các ở Tử Tức", C(own_stars=["Long Trì", "Phượng Các"], other="'Long Phượng' — the pair; one alone not stated"),
  "Long Phượng ở cung Tử Tức là rất tốt", "support", ["NEW:kin.easy_children"],
  notes="Unspecific 'rất tốt'; the preceding line ties Long Phượng to 'sinh nở'. Same line also covers Phu Thê, Phúc Đức, Điền Trạch (other miners).")
E("kl153_bao_co_qua", "KL", 153, "Huynh Đệ", "Cô quả ở các cung — Phúc. Tử, Bào",
  "- Ít anh em hiếm muộn.", "Ít anh em hiếm muộn",
  "Cô Thần, Quả Tú ở Huynh Đệ", C(own_stars=["Cô Thần", "Quả Tú"], other="heading 'Cô quả': either star (pair heading)"),
  "Cô Quả ở Huynh Đệ thì ít anh em", "limit", ["kin.few"], timing=True,
  notes="One bullet serves three headings (Phúc, Tử, Bào): 'ít anh em' read for Bào, 'hiếm muộn' for Tử; how it applies to Phúc is unclear.")
E("kl153_tu_co_qua", "KL", 153, "Tử Tức", "Cô quả ở các cung — Phúc. Tử, Bào",
  "- Ít anh em hiếm muộn.", "Ít anh em hiếm muộn",
  "Cô Thần, Quả Tú ở Tử Tức", C(own_stars=["Cô Thần", "Quả Tú"], other="either star (pair heading)"),
  "Cô Quả ở Tử Tức thì hiếm muộn con", "limit", ["kin.few", "kin.late"], timing=True,
  notes="See kl153_bao_co_qua. Agrees with KL p.218 listing Cô, Quả among Tử Tức stars of childlessness (that line skipped).")
