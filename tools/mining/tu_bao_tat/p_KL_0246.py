page("KL", 246, "Case study 'Lá số phá sản' (Giải đoán #11 Cung Tật ách vô chính diệu). Text layer in order. #3 Tử Phá ở Tử tức ngộ Triệt is already rule TV_KL_CASE_TU_TUC_TU_PHA_TRIET.")
page("KL", 244, "Case study 'Lá số thành đạt' #14 Tật ách (Thiên phủ + Hỏa, Tang Hổ, Thiên thọ → bệnh hiểm nghèo, cont. p.245): disease/event of one chart — not recorded.", img=False)
page("KL", 281, "Appendix 'Xem gì ở cung Phúc': Phúc as counterweight for Mệnh, Thân, Tài, Quan, Di, Phối, Tử.")
page("KL", 282, "Appendix '3. Số sống lâu': Cung Tật ách có nhiều phúc tinh, quí tinh thì ít bệnh tật. TEXT LAYER HEAVILY SCRAMBLED (left-column fragments cut mid-word); image read.")
E("kl246_tat_vcd_trong_khong", "KL", 246, "Tật Ách", "Lá số phá sản — Giải đoán 11. Cung Tật ách",
  "11. Cung Tật ách: vô chính diệu, không có một chính tinh, trung tinh nào, không có nghĩa là không có bệnh tật, tai họa mà có nghĩa là cuối đời trắng tay.",
  "không có nghĩa là không có bệnh tật, tai họa mà có nghĩa là cuối đời trắng tay",
  "Tật Ách vô chính diệu và không có trung tinh nào",
  C(other="Tật Ách has no chính tinh AND no trung tinh (book: 'không có một chính tinh, trung tinh nào'); said in a worked case (Mậu Tí chart)"),
  "Tật Ách vô chính diệu, không có cả trung tinh, không phải là không bệnh tật mà là cuối đời trắng tay", "limit",
  ["NEW:fortune.late_poor"],
  notes="Case-study judgement, consistent with KL p.218 (Tật = hình ảnh lúc về già). Contrasts with KL p.142 (Tuần Triệt ở Tật vô chính diệu thì lại tốt) — different condition (that one needs Tuần/Triệt).")
E("kl282_tat_phuc_qui_tinh", "KL", 282, "Tật Ách", "3. Số sống lâu",
  "Do vậy, Cung Tật ách cũng không thể bỏ qua. Cung Tật ách có nhiều phúc tinh, quí tinh thì đương số ít bệnh tật, tai qua nạn khỏi.",
  "Tật ách có nhiều phúc tinh, quí tinh thì đương",
  "Tật Ách có nhiều phúc tinh, quí tinh (theo danh sách của sách, pp.280-282)",
  C(other="'nhiều phúc tinh, quí tinh' — the book's own lists: phúc tinh (p.280-281, e.g. Thiên cơ, Thiên tướng, Đào Hồng Hỷ, Phi liêm, Thanh long, Khôi Việt, Thiên giải, Địa giải, Long Phượng, Quan đới, Lâm quan, Đế vượng) and quí tinh (p.282: Thái dương, Tham lang, Thiên tướng, Xương Khúc, Khôi Việt, Tả Hữu, Thai Tọa); 'nhiều' is not quantified"),
  "Tật Ách có nhiều phúc tinh, quí tinh thì ít bệnh tật, tai qua nạn khỏi", "support",
  ["well.health", "NEW:health.few_ills", "life.mitigated"],
  notes="Quote is the fragment the scrambled text layer keeps contiguous; full sentence read on the image.")
N("kl282_song_lau_menh_phuc_tat", "palace_relation", "", "Tật Ách", "KL", 282,
  "Do vậy, Cung Tật ách cũng không thể bỏ qua",
  "Muốn được sống lâu thứ nhất là phải khỏe mạnh (Mệnh), thứ đến là phải may mắn (Phúc), ít gặp tai họa, nếu có gặp cũng được cứu giải. Do vậy, Cung Tật ách cũng không thể bỏ qua.",
  "muốn sống lâu, trước hết phải khỏe mạnh (Mệnh), rồi may mắn (Phúc), ít gặp tai họa hoặc gặp thì được cứu giải, nên cung Tật Ách cũng không thể bỏ qua",
  ["health", "fortune"], "±", ["well.longevity"])
N("kl281_phuc_doi_trong_tu", "palace_relation", "", "Tử Tức", "KL", 281,
  "thường lấy cung Phúc làm đối trọng cho các cung Mệnh",
  "Môn phái Tử vi coi trọng cung Phúc lắm, thường lấy cung Phúc làm đối trọng cho các cung Mệnh, Thân, Tài, Quan, Di, Phối, Tử để thêm bớt cái may cái rủi ở các cung nêu trên, ví như gia giảm một vài men dẫn (enzyme) trong một thang thuốc vậy.",
  "cung Phúc Đức là đối trọng cho các cung Mệnh, Thân, Tài, Quan, Di, Phối, Tử: thêm bớt cái may cái rủi của các cung ấy",
  ["children", "fortune"], "±", [],
  notes="Relation Phúc Đức → Tử Tức (Phúc tempers Tử Tức's good and bad).")
