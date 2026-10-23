page("KL", 126, "Không Kiếp ở các cung: Bào and Tử headings (no Tật heading; p.127 continues Tài..Vận). Text layer in order.")
page("KL", 127, "Không Kiếp tail (no Tử/Bào/Tật) + Hỏa Linh intro: one star nature (chủ bệnh tật).")
E("kl126_bao_kk_ly_tan", "KL", 126, "Huynh Đệ", "Không Kiếp ở các cung — Bào",
  "- Anh em ly tán.", "Anh em ly tán",
  "Địa Không, Địa Kiếp ở Huynh Đệ", C(own_stars=["Địa Không", "Địa Kiếp"], other="'Không Kiếp' heading: either star (book treats the pair together)"),
  "Không Kiếp ở Huynh Đệ thì anh em ly tán", "limit", ["kin.apart"])
E("kl126_bao_kk_con_do", "KL", 126, "Huynh Đệ", "Không Kiếp ở các cung — Bào",
  "- Anh em côn đồ.", "Anh em côn đồ",
  "Địa Không, Địa Kiếp ở Huynh Đệ", C(own_stars=["Địa Không", "Địa Kiếp"], other="either star (pair heading)"),
  "Không Kiếp ở Huynh Đệ thì anh em có tính côn đồ, ngang ngược", "limit", ["NEW:kin.unruly"],
  notes="Harsh wording ('côn đồ' = thug); the engine may want a softer render ('anh em tính khí ngang tàng') — caller's call.")
E("kl126_bao_kk_lien_luy", "KL", 126, "Huynh Đệ", "Không Kiếp ở các cung — Bào",
  "- Liên lụy vì anh em.", "Liên lụy vì anh em",
  "Địa Không, Địa Kiếp ở Huynh Đệ", C(own_stars=["Địa Không", "Địa Kiếp"], other="either star (pair heading)"),
  "Không Kiếp ở Huynh Đệ thì bị liên lụy vì anh em", "limit", ["kin.burden"])
E("kl126_tu_kk_khong_con", "KL", 126, "Tử Tức", "Không Kiếp ở các cung — Tử",
  "- Không con, sát con.", "Không con, sát con",
  "Địa Không, Địa Kiếp ở Tử Tức", C(own_stars=["Địa Không", "Địa Kiếp"]),
  "(không con, sát con)", "limit", ["kin.few"], skip="childlessness + 'sát con' (khắc/loss of children)")
E("kl126_tu_kk_du_dang", "KL", 126, "Tử Tức", "Không Kiếp ở các cung — Tử",
  "- Con du đãng, phá sản.", "Con du đãng, phá sản",
  "Địa Không, Địa Kiếp ở Tử Tức", C(own_stars=["Địa Không", "Địa Kiếp"], other="either star (pair heading)"),
  "Không Kiếp ở Tử Tức thì con cái du đãng, phá tán của cải", "limit", ["NEW:kin.wayward"])
N("kl126_khong_kiep_nghiep_chuong", "star_nature", "Địa Không, Địa Kiếp", "", "KL", 126,
  "Không Kiếp ví như một nghiệp chướng bám vào con người",
  "Không Kiếp tượng trưng cho những trường hợp bất khả kháng khó chế ngự. Không Kiếp ví như một nghiệp chướng bám vào con người ảnh hưởng cụ thể như: - Tật nguyền, hung họa, yểu mệnh. ...",
  "Không Kiếp tượng trưng cho những trường hợp bất khả kháng, khó chế ngự, như một nghiệp chướng bám vào người", ["health", "siblings", "children"], "-",
  ["NEW:health.exposed", "kin.apart", "NEW:kin.wayward"],
  notes="WHY for KL p.218 'Tối kỵ cho cung Tật khi có … Không Kiếp'. The listed effects (tật nguyền, yểu mệnh) must not be rendered.")
N("kl127_hoa_linh_benh", "star_nature", "Hỏa Tinh, Linh Tinh", "", "KL", 127,
  "chủ bệnh tật hơn là thương tích",
  "Hỏa Linh: - nóng nẩy, phá hoại, bệnh hoạn, kiêu hãnh. - chủ bệnh tật hơn là thương tích.",
  "Hỏa Linh chủ về bệnh tật hơn là thương tích", ["health"], "-", ["health.mild"],
  notes="WHY Hỏa/Linh weigh on Tật Ách; KL p.218 lists Hỏa, Linh among 'không có con' stars too.")
